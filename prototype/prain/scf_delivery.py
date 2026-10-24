"""Durable transport-neutral SCF delivery queue.

Explicit state transitions: PENDING -> IN_FLIGHT -> SUCCEEDED/FAILED/UNKNOWN.
A recovered in-flight delivery remains UNKNOWN until externally reconciled.
No network transport and no claim of global exactly-once processing.
"""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path


class DeliveryConflict(ValueError):
    pass


class SCFDeliveryQueue:
    def __init__(self, database):
        self.database = str(database)
        Path(self.database).parent.mkdir(parents=True, exist_ok=True)
        with self._db() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS prain_scf_delivery_queue(
                id TEXT PRIMARY KEY, message_json TEXT NOT NULL, status TEXT NOT NULL,
                attempts INTEGER NOT NULL DEFAULT 0, evidence TEXT)""")

    def _db(self):
        return sqlite3.connect(self.database, timeout=15)

    def publish(self, message_id, message):
        if not isinstance(message_id, str) or not message_id.strip() or not isinstance(message, dict):
            raise DeliveryConflict("invalid_message")
        raw = json.dumps(message, sort_keys=True, allow_nan=False, separators=(",", ":"))
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT message_json FROM prain_scf_delivery_queue WHERE id=?", (message_id,)).fetchone()
            if row:
                if row[0] != raw:
                    raise DeliveryConflict("message_id_conflict")
                return False
            db.execute("INSERT INTO prain_scf_delivery_queue(id,message_json,status) VALUES(?,?,'PENDING')",
                       (message_id, raw))
            return True

    def claim(self):
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT id,message_json FROM prain_scf_delivery_queue WHERE status='PENDING' ORDER BY rowid LIMIT 1").fetchone()
            if not row:
                return None
            updated = db.execute("UPDATE prain_scf_delivery_queue SET status='IN_FLIGHT', attempts=attempts+1 WHERE id=? AND status='PENDING'", (row[0],))
            if updated.rowcount != 1:
                raise DeliveryConflict("claim_race")
            return {"message_id": row[0], "message": json.loads(row[1])}

    def outcome(self, message_id, status):
        if status not in {"SUCCEEDED", "FAILED", "UNKNOWN"}:
            raise DeliveryConflict("invalid_outcome")
        with self._db() as db:
            updated = db.execute("UPDATE prain_scf_delivery_queue SET status=? WHERE id=? AND status='IN_FLIGHT'", (status, message_id))
            if updated.rowcount != 1:
                raise DeliveryConflict("not_in_flight")

    def recover(self):
        with self._db() as db:
            return db.execute("UPDATE prain_scf_delivery_queue SET status='UNKNOWN' WHERE status='IN_FLIGHT'").rowcount

    def reconcile(self, message_id, provider_state, evidence):
        if provider_state not in {"SUCCEEDED", "FAILED", "NOT_EXECUTED"} or not isinstance(evidence, str) or not evidence.strip():
            raise DeliveryConflict("authoritative_reconciliation_required")
        new_status = "PENDING" if provider_state == "NOT_EXECUTED" else provider_state
        with self._db() as db:
            updated = db.execute("UPDATE prain_scf_delivery_queue SET status=?,evidence=? WHERE id=? AND status='UNKNOWN'",
                                 (new_status, evidence, message_id))
            if updated.rowcount != 1:
                raise DeliveryConflict("not_unknown")
        return new_status

    def status(self, message_id):
        with self._db() as db:
            row = db.execute("SELECT status,attempts,evidence FROM prain_scf_delivery_queue WHERE id=?", (message_id,)).fetchone()
        return dict(zip(("status", "attempts", "evidence"), row)) if row else None