"""Coordinated, staged backup/restore for multiple PRAIN SQLite databases.

Callers must quiesce all connections for restore and all writers for backup. Each SQLite file is
backed up with SQLite's online backup API; the bundle is not a distributed
transaction and cannot create a cross-database point-in-time snapshot while
writers are active.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
import tempfile
from pathlib import Path
from typing import Mapping
from contextlib import contextmanager
from datetime import datetime, timezone


@contextmanager
def _managed_connection(path: str | Path, *, timeout: float = 10.0):
    """Close SQLite handles deterministically; connection context alone only commits/rolls back."""
    conn = sqlite3.connect(str(path), timeout=timeout)
    try:
        yield conn
    finally:
        conn.close()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _reject_sqlite_sidecars(path: Path) -> None:
    """Refuse SQLite state outside the verified main file before opening it.

    WAL/journal files can change SQLite's view without changing the main-file
    checksum. A destination's old sidecars must never accompany a replacement.
    Callers must exclude concurrent connections and changes for the whole restore.
    """
    for suffix in ('-wal', '-shm', '-journal'):
        sidecar = path.with_name(path.name + suffix)
        if os.path.lexists(sidecar):
            raise ValueError(f'sqlite_sidecar_present:{sidecar.name}')


def _integrity(path: Path) -> None:
    with _managed_connection(path, timeout=10) as conn:
        result = conn.execute("PRAGMA integrity_check").fetchone()
        if not result or result[0] != "ok":
            raise sqlite3.DatabaseError(f"integrity_check_failed:{result}")


def _sqlite_snapshot(source: Path, destination: Path, *, label: str) -> None:
    """Create a transactionally consistent SQLite snapshot and verify it once staged."""
    with _managed_connection(source, timeout=10) as src_conn:
        with _managed_connection(destination, timeout=10) as dst_conn:
            src_conn.backup(dst_conn)
            result = dst_conn.execute("PRAGMA integrity_check").fetchone()
            if not result or result[0] != "ok":
                raise sqlite3.DatabaseError(f"{label}_integrity_failed:{result}")


def _private_tables(path: Path) -> bool:
    if not path.is_file():
        return False
    with _managed_connection(path) as conn:
        return conn.execute("""SELECT 1 FROM sqlite_master WHERE type='table'
            AND name IN ('prain_private_projections','prain_deletion_tombstones') LIMIT 1""").fetchone() is not None


def _checked_tombstones(snapshot):
    # This API is deliberately explicit: an empty list means that the trusted
    # control plane obtained a current complete snapshot with no deletions.
    # None never means 'no deletions'. Authentication/freshness of the authority
    # cannot be inferred from opaque source references or an old backup.
    if not isinstance(snapshot, (list, tuple)) or len(snapshot) > 10000:
        raise ValueError("current_authoritative_tombstones_required")
    checked = set()
    for entry in snapshot:
        if (not isinstance(entry, (list, tuple)) or len(entry) != 2
                or any(not isinstance(value, str) or not value for value in entry)):
            raise ValueError("invalid_authoritative_tombstone")
        checked.add(tuple(entry))
    return checked


def _known_tombstones(path: Path):
    if not path.is_file():
        return set()
    with _managed_connection(path) as conn:
        if not conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='prain_deletion_tombstones'").fetchone():
            return set()
        return set(conn.execute("SELECT tenant,source FROM prain_deletion_tombstones"))


def _reject_target_with_active_hold(path: Path) -> None:
    """Do not replace a destination while its legal hold remains active.

    An older backup cannot be trusted to preserve newer hold policy or held
    content. Restores require stopped connections and exclusive control of files.
    """
    if not path.is_file():
        return
    from .private_projections import PrivateProjections
    with _managed_connection(path) as conn:
        exists = conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='prain_projection_retention'").fetchone()
        if not exists:
            return
        holds = conn.execute("SELECT hold_until FROM prain_projection_retention WHERE hold_until IS NOT NULL").fetchall()
    now = datetime.now(timezone.utc).isoformat()
    for (hold_until,) in holds:
        # Reject malformed hold state rather than silently destroying it.
        if PrivateProjections._timestamp(hold_until) > now:
            raise ValueError('restore_blocked_legal_hold')


def _restore_deletions(source: Path, target: Path, snapshot):
    _reject_target_with_active_hold(target)
    required = _private_tables(source) or _private_tables(target)
    if not required and snapshot is None:
        return None
    checked = _checked_tombstones(snapshot)
    # Never discard deletion knowledge already available at the destination,
    # even when the supplied control-plane snapshot accidentally omits it.
    return checked | _known_tombstones(source) | _known_tombstones(target)


def _sanitize_restore(path: Path, tombstones) -> None:
    if tombstones is None:
        return
    from .private_projections import PrivateProjections
    store = PrivateProjections(path)
    # The public apply API intentionally limits each transaction to 10000 rows.
    # All work happens in an unexposed staged file before installation.
    rows = sorted(tombstones)
    for offset in range(0, len(rows), 10000):
        store.apply_deletions(rows[offset:offset + 10000])
    # A staged restore can contain previously freed pages from the historical
    # backup. Rebuild this unserved copy so deleted payloads do not persist in
    # its freelist even if the original database used secure_delete=OFF.
    with _managed_connection(path) as conn:
        conn.execute("VACUUM")
    _integrity(path)


def backup_databases(databases: Mapping[str, str | Path], bundle_dir: str | Path) -> dict:
    """Back up named database files into a new directory; refuses overwrite."""
    if not databases:
        raise ValueError("at_least_one_database_required")
    names = list(databases)
    if any(not name or Path(name).name != name or name in {".", ".."} for name in names):
        raise ValueError("database_names_must_be_simple_file_names")
    target = Path(bundle_dir).expanduser().resolve()
    if target.exists():
        raise FileExistsError(f"backup_bundle_exists:{target}")
    sources = {name: Path(path).expanduser().resolve() for name, path in databases.items()}
    if len(set(sources.values())) != len(sources):
        raise ValueError("database_paths_must_be_unique")
    for src in sources.values():
        if not src.is_file():
            raise FileNotFoundError(f"database_not_found:{src}")
    target.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{target.name}.staging-", dir=target.parent))
    try:
        entries = {}
        for name, source in sources.items():
            dest = staging / f"{name}.sqlite"
            _sqlite_snapshot(source, dest, label=f"backup:{name}")
            entries[name] = {"file": dest.name, "sha256": _sha256(dest), "integrity": "ok"}
        manifest = {"format": "PRAIN_SQLITE_BUNDLE_V1", "databases": entries,
                    "consistency": "writers_must_be_quiesced; per-file SQLite online backups"}
        (staging / "BUNDLE_MANIFEST.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        os.replace(staging, target)
        return {"status": "OK", "path": str(target), "databases": len(entries)}
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def restore_databases(bundle_dir: str | Path, destinations: Mapping[str, str | Path], *,
                      authoritative_tombstones: Mapping[str, list | tuple] | None = None) -> dict:
    """Validate and stage every DB before replacing any destination; roll back replacements on failure.

    Filesystem replacement across multiple databases is not globally atomic. The
    function provides best-effort rollback on replacement errors; writers must be
    closed and the caller should retain an independent backup of destinations.

    If source or destination has owned private projection tables, a current
    authoritative tombstone snapshot for that database name is mandatory. The
    trusted caller obtains/authenticates its completeness independently of the
    backup. Deletions are applied to staged data and rollback artifacts before
    any replacement, so neither normal restore nor rollback resurrects them.
    """
    bundle = Path(bundle_dir).expanduser().resolve()
    manifest_path = bundle / "BUNDLE_MANIFEST.json"
    if not manifest_path.is_file():
        raise FileNotFoundError("bundle_manifest_missing")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("format") != "PRAIN_SQLITE_BUNDLE_V1" or not isinstance(manifest.get("databases"), dict):
        raise ValueError("bundle_manifest_invalid")
    if set(destinations) != set(manifest["databases"]):
        raise ValueError("destination_names_must_match_bundle")
    targets = {name: Path(path).expanduser().resolve() for name, path in destinations.items()}
    if len(set(targets.values())) != len(targets):
        raise ValueError("destination_paths_must_be_unique")
    if authoritative_tombstones is not None and (
            not isinstance(authoritative_tombstones, Mapping)
            or set(authoritative_tombstones) - set(targets)):
        raise ValueError("invalid_authoritative_tombstone_database_names")
    for target in targets.values():
        _reject_sqlite_sidecars(target)
    deletions = {}
    for name, entry in manifest["databases"].items():
        filename = entry.get("file", "")
        if Path(filename).name != filename or not filename.endswith(".sqlite"):
            raise ValueError(f"bundle_filename_invalid:{name}")
        source = bundle / filename
        _reject_sqlite_sidecars(source)
        if not source.is_file() or _sha256(source) != entry.get("sha256"):
            raise ValueError(f"bundle_checksum_mismatch:{name}")
        _integrity(source)
        snapshot = None if authoritative_tombstones is None else authoritative_tombstones.get(name)
        deletions[name] = _restore_deletions(source, targets[name], snapshot)

    parents = {path.parent for path in targets.values()}
    for parent in parents:
        parent.mkdir(parents=True, exist_ok=True)
    # Never let a destination alias a bundle payload/manifest: replacing one
    # would destroy the very source needed for validation or recovery.
    protected = {manifest_path.resolve()}
    protected.update((bundle / entry["file"]).resolve() for entry in manifest["databases"].values())
    if any(target in protected for target in targets.values()):
        raise ValueError("destination_must_not_overwrite_bundle_contents")

    staged: dict[str, Path] = {}
    originals: dict[str, Path | None] = {}
    replaced: list[str] = []
    rollback_failures: list[str] = []
    try:
        for name, source_entry in manifest["databases"].items():
            target = targets[name]
            fd, tmp_name = tempfile.mkstemp(prefix=f".{target.name}.restore-", suffix=".sqlite", dir=target.parent)
            os.close(fd)
            tmp = Path(tmp_name)
            staged[name] = tmp
            _sqlite_snapshot(bundle / source_entry["file"], tmp, label=f"restore:{name}")
            _sanitize_restore(tmp, deletions[name])
        for name, target in targets.items():
            backup_copy = None
            if target.exists():
                fd, old_name = tempfile.mkstemp(prefix=f".{target.name}.rollback-", suffix=".sqlite", dir=target.parent)
                os.close(fd)
                backup_copy = Path(old_name)
                originals[name] = backup_copy
                _sqlite_snapshot(target, backup_copy, label=f"rollback:{name}")
                _sanitize_restore(backup_copy, deletions[name])
            originals[name] = backup_copy
        for name, target in targets.items():
            os.replace(staged[name], target)
            replaced.append(name)
        for old in originals.values():
            if old:
                old.unlink(missing_ok=True)
        return {"status": "OK", "databases": len(targets)}
    except Exception as original_error:
        # Roll back in reverse replacement order. If any rollback action fails,
        # retain its recovery copy and surface its exact path to the caller.
        for name in reversed(replaced):
            target = targets[name]
            old = originals.get(name)
            try:
                if old and old.exists():
                    os.replace(old, target)
                    originals[name] = None
                else:
                    target.unlink(missing_ok=True)
            except OSError as rollback_error:
                recovery_path = str(old) if old and old.exists() else str(target)
                rollback_failures.append(
                    f"{name}: {rollback_error!r}; recovery_artifact={recovery_path}"
                )
        if rollback_failures:
            details = "; ".join(rollback_failures)
            raise RuntimeError(
                f"restore_failed_and_rollback_incomplete: {details}"
            ) from original_error
        raise
    finally:
        for path in staged.values():
            path.unlink(missing_ok=True)
        # Do not destroy recovery artifacts after a failed rollback. Successfully
        # consumed originals are set to None above; untouched copies are cleaned
        # only when rollback was not compromised.
        if not rollback_failures:
            for path in originals.values():
                if path:
                    path.unlink(missing_ok=True)


def recover_database_from_artifact(artifact_path: str | Path, destination: str | Path, *,
                                   authoritative_tombstones: list | tuple | None = None) -> dict:
    """Safely restore one preserved rollback artifact after an incomplete bundle restore.

    The artifact is validated and copied to a temporary file beside the target before
    replacement. The artifact itself is retained so operators can verify or retry recovery.
    Callers must close all database connections and confirm the artifact belongs to the target.
    Private artifacts/destinations require a current trusted deletion snapshot,
    including when a previously sanitized recovery artifact has become stale.
    """
    artifact = Path(artifact_path).expanduser().resolve()
    target = Path(destination).expanduser().resolve()
    if not artifact.is_file():
        raise FileNotFoundError(f"recovery_artifact_missing:{artifact}")
    if artifact == target:
        raise ValueError("recovery_artifact_and_destination_must_differ")
    _reject_sqlite_sidecars(artifact)
    _reject_sqlite_sidecars(target)
    _integrity(artifact)
    deletions = _restore_deletions(artifact, target, authoritative_tombstones)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{target.name}.recovery-", suffix=".sqlite", dir=target.parent)
    os.close(fd)
    staged = Path(temp_name)
    try:
        with _managed_connection(artifact, timeout=10) as src_conn:
            with _managed_connection(staged, timeout=10) as dst_conn:
                src_conn.backup(dst_conn)
        _integrity(staged)
        _sanitize_restore(staged, deletions)
        os.replace(staged, target)
        _integrity(target)
        return {"status": "RECOVERED", "destination": str(target),
                "artifact": str(artifact), "artifact_retained": True}
    finally:
        staged.unlink(missing_ok=True)
