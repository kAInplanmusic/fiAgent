"""Tenant-scoped derived projection lifecycle and deletion tombstones (local SQLite).
Physical removal is deliberately limited to this owned projection table.
"""
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from contextlib import contextmanager
import re


class ProjectionDeleted(ValueError):
    pass


class PrivateProjections:
    CLASSES = frozenset({"public", "internal", "confidential", "restricted"})
    def __init__(self, database):
        self.database = str(database)
        Path(database).parent.mkdir(parents=True, exist_ok=True)
        with self._db() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS prain_private_projections (
                tenant TEXT NOT NULL, source TEXT NOT NULL, classification TEXT NOT NULL,
                payload TEXT NOT NULL, PRIMARY KEY(tenant,source))""")
            db.execute("""CREATE TABLE IF NOT EXISTS prain_deletion_tombstones (
                tenant TEXT NOT NULL, source TEXT NOT NULL, PRIMARY KEY(tenant,source))""")
            db.execute("""CREATE TABLE IF NOT EXISTS prain_projection_retention (
                tenant TEXT NOT NULL, source TEXT NOT NULL, expires_at TEXT NOT NULL,
                policy_ref TEXT NOT NULL, hold_until TEXT,
                PRIMARY KEY(tenant,source))""")
    @contextmanager
    def _db(self):
        db = sqlite3.connect(self.database, timeout=15)
        try:
            # Overwrite freed content in this owned store during future deletes.
            # This does not purge earlier backups, WAL copies or external stores.
            db.execute("PRAGMA secure_delete=ON")
            with db:
                yield db
        finally:
            db.close()

    @staticmethod
    def _timestamp(value):
        if not isinstance(value, str):
            raise ValueError("timestamp_required")
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            raise ValueError("timezone_required")
        return parsed.astimezone(timezone.utc).isoformat()

    @staticmethod
    def _scope(tenant, source):
        if not isinstance(tenant, str) or not tenant or not isinstance(source, str) or not source:
            raise ValueError("invalid_scope")

    @staticmethod
    def _check_payload(payload):
        # Reject rather than silently redact: callers must supply a credential-free projection.
        pending = [(payload, 0)]
        visited = 0
        forbidden = {"token", "password", "secret", "apikey", "authorization",
                     "accesstoken", "refreshtoken", "clientsecret", "privatekey"}
        while pending:
            item, depth = pending.pop()
            visited += 1
            if depth > 32 or visited > 10000:
                raise ValueError("payload_structure_limit")
            if isinstance(item, dict):
                for key, value in item.items():
                    if not isinstance(key, str):
                        raise ValueError("string_keys_required")
                    normalized = re.sub(r"[^a-z0-9]", "", key.casefold())
                    if normalized in forbidden:
                        raise ValueError("secret_field_not_allowed")
                    pending.append((value, depth + 1))
            elif isinstance(item, (list, tuple)):
                pending.extend((value, depth + 1) for value in item)


    def upsert(self, tenant, source, classification, payload):
        if not isinstance(tenant, str) or not tenant or not isinstance(source, str) or not source:
            raise ValueError("invalid_scope")
        if classification not in self.CLASSES or not isinstance(payload, dict):
            raise ValueError("invalid_classification_or_payload")
        # Prevent accidental storage of obvious credential fields in the owned projection.
        self._check_payload(payload)
        data = json.dumps(payload, allow_nan=False, sort_keys=True)
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            if db.execute("SELECT 1 FROM prain_deletion_tombstones WHERE tenant=? AND source=?",
                          (tenant, source)).fetchone():
                raise ProjectionDeleted("deleted_source_cannot_reappear")
            previous = db.execute("SELECT classification FROM prain_private_projections WHERE tenant=? AND source=?", (tenant, source)).fetchone()
            ranks = {"public": 0, "internal": 1, "confidential": 2, "restricted": 3}
            if previous and ranks[classification] < ranks[previous[0]]:
                raise ValueError("classification_downgrade_requires_review")
            db.execute("""INSERT INTO prain_private_projections VALUES(?,?,?,?)
                ON CONFLICT(tenant,source) DO UPDATE SET
                    classification=excluded.classification,payload=excluded.payload""",
                       (tenant, source, classification, data))
    def read(self, tenant, source):
        with self._db() as db:
            row = db.execute("SELECT classification,payload FROM prain_private_projections WHERE tenant=? AND source=?",
                             (tenant, source)).fetchone()
        return None if row is None else {"classification": row[0], "payload": json.loads(row[1])}

    def delete_source(self, tenant, source):
        if not isinstance(tenant, str) or not tenant or not isinstance(source, str) or not source:
            raise ValueError("invalid_scope")
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            hold = db.execute("SELECT hold_until FROM prain_projection_retention WHERE tenant=? AND source=?", (tenant, source)).fetchone()
            if hold and hold[0] and hold[0] > datetime.now(timezone.utc).isoformat():
                raise ValueError("blocked_legal_hold")
            db.execute("INSERT OR IGNORE INTO prain_deletion_tombstones VALUES(?,?)", (tenant, source))
            db.execute("DELETE FROM prain_private_projections WHERE tenant=? AND source=?", (tenant, source))
            db.execute("DELETE FROM prain_projection_retention WHERE tenant=? AND source=?", (tenant, source))

    def set_retention(self, tenant, source, *, expires_at, policy_ref, hold_until=None):
        """Trusted control-plane API. Policy authority/authentication belongs to the caller."""
        self._scope(tenant, source)
        expires_at = self._timestamp(expires_at)
        hold_until = self._timestamp(hold_until) if hold_until is not None else None
        if not isinstance(policy_ref, str) or not policy_ref.strip():
            raise ValueError("policy_reference_required")
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            if not db.execute("SELECT 1 FROM prain_private_projections WHERE tenant=? AND source=?", (tenant, source)).fetchone():
                raise ValueError("projection_not_found")
            db.execute("""INSERT INTO prain_projection_retention VALUES(?,?,?,?,?)
                ON CONFLICT(tenant,source) DO UPDATE SET expires_at=excluded.expires_at,
                policy_ref=excluded.policy_ref,hold_until=excluded.hold_until""",
                (tenant, source, expires_at, policy_ref, hold_until))

    def sweep_retention(self, *, now, limit=100):
        """One bounded scheduler tick. Expired holds cease to block expiry.

        Missing policies are counted explicitly and never assumed compliant.
        This deletes logical rows, not physical SQLite pages or backups.
        """
        now = self._timestamp(now)
        if type(limit) is not int or not 1 <= limit <= 1000:
            raise ValueError("invalid_sweep_limit")
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            rows = db.execute("""SELECT r.tenant,r.source FROM prain_projection_retention r
                JOIN prain_private_projections p USING(tenant,source)
                WHERE r.expires_at <= ? AND (r.hold_until IS NULL OR r.hold_until <= ?)
                ORDER BY r.expires_at,r.tenant,r.source LIMIT ?""", (now, now, limit)).fetchall()
            for tenant, source in rows:
                db.execute("INSERT OR IGNORE INTO prain_deletion_tombstones VALUES(?,?)", (tenant, source))
                db.execute("DELETE FROM prain_private_projections WHERE tenant=? AND source=?", (tenant, source))
                db.execute("DELETE FROM prain_projection_retention WHERE tenant=? AND source=?", (tenant, source))
            unconfigured = db.execute("""SELECT count(*) FROM prain_private_projections p
                LEFT JOIN prain_projection_retention r USING(tenant,source)
                WHERE r.source IS NULL""").fetchone()[0]
        return {"deleted": len(rows), "unconfigured": unconfigured}

    def deletion_snapshot(self):
        """Trusted control plane export; contains opaque source refs, never payloads."""
        with self._db() as db:
            return list(db.execute("SELECT tenant,source FROM prain_deletion_tombstones ORDER BY tenant,source"))

    def apply_deletions(self, tombstones):
        """Apply trusted current tombstones to a stopped restored replica before serving.

        The caller must obtain an authoritative, complete snapshot independently of
        the old backup. This method does not authenticate arbitrary remote inputs.
        """
        if not isinstance(tombstones, (list, tuple)) or len(tombstones) > 10000:
            raise ValueError("invalid_tombstone_batch")
        checked = []
        for entry in tombstones:
            if not isinstance(entry, (list, tuple)) or len(entry) != 2:
                raise ValueError("invalid_tombstone")
            self._scope(*entry)
            checked.append(tuple(entry))
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            for tenant, source in checked:
                db.execute("INSERT OR IGNORE INTO prain_deletion_tombstones VALUES(?,?)", (tenant, source))
                db.execute("DELETE FROM prain_private_projections WHERE tenant=? AND source=?", (tenant, source))
                db.execute("DELETE FROM prain_projection_retention WHERE tenant=? AND source=?", (tenant, source))
        return len(set(checked))
