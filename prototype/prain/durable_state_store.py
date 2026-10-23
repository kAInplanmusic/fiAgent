"""SQLite-backed versioned state store with transactional compare-and-swap."""
from __future__ import annotations
import json
import os
import sqlite3
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
import tempfile
from typing import Any
from .state_store import StateConflict, StateRecord, utc_now

@contextmanager
def _managed_sqlite_connection(path: str | Path, *, timeout: float = 10.0):
    """SQLite connection context that closes the handle (sqlite3's own context does not)."""
    conn = sqlite3.connect(str(path), timeout=timeout)
    try:
        yield conn
    finally:
        conn.close()


class DurableStateStore:
    """Durable state repository. Each operation uses a fresh SQLite connection.

    SQLite serializes writes; CAS is enforced in a single UPDATE predicate. Values
    must be JSON-serializable. This is a local SQLite adapter, not a distributed DB.
    """
    def __init__(self, db_path: str | Path, *, timeout: float = 10.0):
        self.db_path = str(db_path)
        self.timeout = timeout
        if self.db_path != ':memory:':
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            if self.db_path != ':memory:':
                conn.execute('PRAGMA journal_mode = WAL')
            conn.execute('''CREATE TABLE IF NOT EXISTS prain_state (
                state_key TEXT PRIMARY KEY,
                value_json TEXT NOT NULL,
                version INTEGER NOT NULL CHECK(version >= 1),
                updated_at TEXT NOT NULL
            )''')

    @contextmanager
    def _connect(self):
        """Yield a configured connection and always close it after the operation."""
        conn = sqlite3.connect(self.db_path, timeout=self.timeout, isolation_level=None)
        try:
            conn.execute(f'PRAGMA busy_timeout = {int(self.timeout * 1000)}')
            yield conn
        finally:
            conn.close()

    @staticmethod
    def _json(value):
        return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)

    def get(self, key: str) -> StateRecord | None:
        with self._connect() as conn:
            row = conn.execute('SELECT value_json, version, updated_at FROM prain_state WHERE state_key=?', (key,)).fetchone()
        if row is None:
            return None
        return StateRecord(key, json.loads(row[0]), row[1], row[2])

    def create(self, key: str, value: Any) -> StateRecord:
        if not key:
            raise ValueError('key must be non-empty')
        value_json = self._json(deepcopy(value))
        now = utc_now()
        try:
            with self._connect() as conn:
                conn.execute('BEGIN IMMEDIATE')
                conn.execute('INSERT INTO prain_state(state_key,value_json,version,updated_at) VALUES(?,?,1,?)', (key, value_json, now))
                conn.commit()
        except sqlite3.IntegrityError as exc:
            if 'UNIQUE constraint failed: prain_state.state_key' in str(exc):
                raise StateConflict(f'state already exists: {key}') from exc
            raise
        return StateRecord(key, json.loads(value_json), 1, now)

    def compare_and_swap(self, key: str, expected_version: int, value: Any) -> StateRecord:
        value_json = self._json(deepcopy(value))
        now = utc_now()
        with self._connect() as conn:
            conn.execute('BEGIN IMMEDIATE')
            row = conn.execute('SELECT version FROM prain_state WHERE state_key=?', (key,)).fetchone()
            if row is None:
                conn.rollback()
                raise KeyError(key)
            if row[0] != expected_version:
                conn.rollback()
                raise StateConflict(f'stale state for {key}: expected {expected_version}, actual {row[0]}')
            updated = conn.execute('UPDATE prain_state SET value_json=?, version=version+1, updated_at=? WHERE state_key=? AND version=?',
                                   (value_json, now, key, expected_version))
            if updated.rowcount != 1:
                conn.rollback()
                raise StateConflict(f'concurrent state update: {key}')
            conn.commit()
        return StateRecord(key, json.loads(value_json), expected_version + 1, now)

    def health_check(self) -> dict[str, Any]:
        """Return a non-mutating SQLite integrity/schema check.

        This detects common corruption and missing-schema conditions; it does not
        repair a database or prove that storage hardware honors fsync semantics.
        """
        try:
            with self._connect() as conn:
                result = conn.execute('PRAGMA quick_check').fetchone()
                if not result or result[0] != 'ok':
                    return {'status': 'CORRUPT', 'detail': str(result[0] if result else 'no result')}
                table = conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='prain_state'").fetchone()
                if table is None:
                    return {'status': 'SCHEMA_MISSING', 'detail': 'prain_state table missing'}
                conn.execute('SELECT state_key, value_json, version, updated_at FROM prain_state LIMIT 1').fetchone()
                return {'status': 'OK', 'detail': 'quick_check passed; schema readable'}
        except sqlite3.DatabaseError as exc:
            return {'status': 'ERROR', 'detail': f'{type(exc).__name__}: {exc}'}

    @staticmethod
    def _validate_state_schema(conn: sqlite3.Connection, *, error_prefix: str) -> None:
        table = conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='prain_state'").fetchone()
        if table is None:
            raise sqlite3.DatabaseError(f'{error_prefix}_schema_missing')
        columns = {row[1] for row in conn.execute('PRAGMA table_info(prain_state)')}
        required = {'state_key', 'value_json', 'version', 'updated_at'}
        if not required.issubset(columns):
            missing = ','.join(sorted(required - columns))
            raise sqlite3.DatabaseError(f'{error_prefix}_schema_incompatible: missing columns {missing}')

    def backup_to(self, destination: str | Path) -> dict[str, Any]:
        """Create a consistent SQLite backup using SQLite's online backup API.

        The destination must differ from the active database path. The resulting
        file is integrity-checked before success is reported.
        """
        destination = Path(destination).expanduser().resolve()
        source = Path(self.db_path).expanduser().resolve() if self.db_path != ':memory:' else None
        if source is not None and destination == source:
            raise ValueError('backup_destination_must_differ_from_source')
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            raise FileExistsError(f'backup destination already exists: {destination}')
        try:
            with self._connect() as src:
                with _managed_sqlite_connection(destination, timeout=self.timeout) as dst:
                    src.backup(dst)
                    result = dst.execute('PRAGMA integrity_check').fetchone()
                    if not result or result[0] != 'ok':
                        raise sqlite3.DatabaseError(f'backup_integrity_check_failed: {result}')
                    self._validate_state_schema(dst, error_prefix='backup')
        except Exception:
            try:
                destination.unlink(missing_ok=True)
            except OSError:
                pass
            raise
        return {'status': 'OK', 'path': str(destination), 'integrity': 'ok'}

    @classmethod
    def restore_from(cls, backup_path: str | Path, destination: str | Path, *, timeout: float = 10.0) -> "DurableStateStore":
        """Validate a backup, restore through a temporary file, then atomically replace destination.

        This is a single-file local restore. Callers must stop writers first and
        preserve a separate copy of any destination database they may need.
        """
        backup = Path(backup_path).expanduser().resolve()
        target = Path(destination).expanduser().resolve()
        if not backup.is_file():
            raise FileNotFoundError(f'backup_not_found: {backup}')
        if backup == target:
            raise ValueError('restore_source_must_differ_from_destination')
        target.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(prefix=f'.{target.name}.restore-', suffix='.sqlite', dir=str(target.parent))
        os.close(fd)
        temp_path = Path(temp_name)
        try:
            with _managed_sqlite_connection(backup, timeout=timeout) as src:
                result = src.execute('PRAGMA integrity_check').fetchone()
                if not result or result[0] != 'ok':
                    raise sqlite3.DatabaseError(f'backup_integrity_check_failed: {result}')
                cls._validate_state_schema(src, error_prefix='backup')
                with _managed_sqlite_connection(temp_path, timeout=timeout) as dst:
                    src.backup(dst)
                    check = dst.execute('PRAGMA integrity_check').fetchone()
                    if not check or check[0] != 'ok':
                        raise sqlite3.DatabaseError(f'restored_copy_integrity_check_failed: {check}')
                    cls._validate_state_schema(dst, error_prefix='restored_copy')
            os.replace(temp_path, target)
        finally:
            temp_path.unlink(missing_ok=True)
        restored = cls(target, timeout=timeout)
        health = restored.health_check()
        if health.get('status') != 'OK':
            raise sqlite3.DatabaseError(f'restored_database_health_check_failed: {health}')
        return restored

    def count(self) -> int:
        """Return the number of persisted state records."""
        with self._connect() as conn:
            row = conn.execute('SELECT COUNT(*) FROM prain_state').fetchone()
        return int(row[0])

    compareAndSwap = compare_and_swap
