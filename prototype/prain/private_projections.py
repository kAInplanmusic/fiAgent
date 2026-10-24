"""Tenant-scoped derived projection lifecycle and deletion tombstones (local SQLite).
Physical removal is deliberately limited to this owned projection table.
"""
import json
import sqlite3
from pathlib import Path


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
    def _db(self):
        return sqlite3.connect(self.database, timeout=15)

    def upsert(self, tenant, source, classification, payload):
        if not isinstance(tenant, str) or not tenant or not isinstance(source, str) or not source:
            raise ValueError("invalid_scope")
        if classification not in self.CLASSES or not isinstance(payload, dict):
            raise ValueError("invalid_classification_or_payload")
        # Prevent accidental storage of obvious credential fields in the owned projection.
        if any(key.lower() in {"token", "password", "secret", "api_key", "authorization"} for key in payload):
            raise ValueError("secret_field_not_allowed")
        data = json.dumps(payload, allow_nan=False, sort_keys=True)
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            if db.execute("SELECT 1 FROM prain_deletion_tombstones WHERE tenant=? AND source=?",
                          (tenant, source)).fetchone():
                raise ProjectionDeleted("deleted_source_cannot_reappear")
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
            db.execute("INSERT OR IGNORE INTO prain_deletion_tombstones VALUES(?,?)", (tenant, source))
            db.execute("DELETE FROM prain_private_projections WHERE tenant=? AND source=?", (tenant, source))
