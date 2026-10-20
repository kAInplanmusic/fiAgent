"""SQLite-backed atomic admission primitives; external effects remain outside transaction.

This module provides durable uniqueness/approval-consumption primitives. It deliberately
DOES NOT claim atomicity with an external side effect; callers must use an outbox/dispatcher.
"""
from __future__ import annotations
import json, sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any

class AdmissionConflict(RuntimeError):
    pass

class DurableAdmissionStore:
    def __init__(self, path: str | Path):
        self.path = str(path)
        if self.path != ':memory:':
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.executescript('''
            CREATE TABLE IF NOT EXISTS admission (
              idempotency_key TEXT PRIMARY KEY,
              fingerprint TEXT NOT NULL,
              receipt_json TEXT NOT NULL,
              created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
            );
            CREATE TABLE IF NOT EXISTS consumed_approval (
              approval_id TEXT PRIMARY KEY,
              idempotency_key TEXT NOT NULL UNIQUE,
              consumed_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
            );
            CREATE TABLE IF NOT EXISTS outbox (
              outbox_id TEXT PRIMARY KEY,
              idempotency_key TEXT NOT NULL UNIQUE REFERENCES admission(idempotency_key),
              payload_json TEXT NOT NULL,
              status TEXT NOT NULL CHECK(status IN ('PENDING','IN_FLIGHT','SUCCEEDED','FAILED','OUTCOME_UNKNOWN')),
              attempts INTEGER NOT NULL DEFAULT 0,
              created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
              updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
              last_error TEXT
            );
            CREATE INDEX IF NOT EXISTS outbox_status_created ON outbox(status, created_at);
            CREATE TABLE IF NOT EXISTS schema_migration (
              version INTEGER PRIMARY KEY,
              applied_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
            );
            INSERT OR IGNORE INTO schema_migration(version) VALUES (1);
            ''')

    def _connect(self):
        db = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA foreign_keys=ON')
        db.execute('PRAGMA busy_timeout=10000')
        if self.path != ':memory:':
            db.execute('PRAGMA journal_mode=WAL')
            db.execute('PRAGMA synchronous=FULL')
        return db

    @contextmanager
    def transaction(self):
        db = self._connect()
        try:
            db.execute('BEGIN IMMEDIATE')
            yield db
            db.execute('COMMIT')
        except Exception:
            if db.in_transaction:
                db.execute('ROLLBACK')
            raise
        finally:
            db.close()

    def admit(self, *, idempotency_key: str, fingerprint: str,
              receipt: dict[str, Any], approval_id: str | None = None,
              outbox_item: dict[str, Any] | None = None) -> tuple[dict[str, Any], bool]:
        """Atomically persist a simulated receipt and optionally consume one approval.

        Returns (stored_receipt, created). Same key+fingerprint replays; changed fingerprint
        conflicts. A consumed approval cannot authorize a second idempotency key.
        """
        if not idempotency_key or not fingerprint:
            raise ValueError('idempotency_key and fingerprint are required')
        serialized = json.dumps(receipt, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
        with self.transaction() as db:
            prior = db.execute('SELECT fingerprint, receipt_json FROM admission WHERE idempotency_key=?',
                               (idempotency_key,)).fetchone()
            if prior:
                if prior['fingerprint'] != fingerprint:
                    raise AdmissionConflict('idempotency_key_conflict')
                return json.loads(prior['receipt_json']), False
            if approval_id is not None:
                if not approval_id.strip():
                    raise ValueError('approval_id must be non-empty')
                try:
                    db.execute('INSERT INTO consumed_approval(approval_id,idempotency_key) VALUES (?,?)',
                               (approval_id, idempotency_key))
                except sqlite3.IntegrityError as exc:
                    raise AdmissionConflict('approval_already_consumed') from exc
            db.execute('INSERT INTO admission(idempotency_key,fingerprint,receipt_json) VALUES (?,?,?)',
                       (idempotency_key, fingerprint, serialized))
            if outbox_item is not None:
                item = dict(outbox_item)
                item.setdefault('outbox_id', idempotency_key)
                item.setdefault('status', 'PENDING')
                db.execute('INSERT INTO outbox(outbox_id,idempotency_key,payload_json,status) VALUES (?,?,?,?)',
                           (item['outbox_id'], idempotency_key,
                            json.dumps(item['payload'], sort_keys=True, separators=(',', ':'), ensure_ascii=False),
                            item['status']))
            return json.loads(serialized), True

    def get_outbox(self, idempotency_key: str) -> dict[str, Any] | None:
        with self._connect() as db:
            row = db.execute('SELECT * FROM outbox WHERE idempotency_key=?', (idempotency_key,)).fetchone()
            if row is None: return None
            result = dict(row); result['payload'] = json.loads(result.pop('payload_json'))
            return result

    def claim_next(self) -> dict[str, Any] | None:
        # Atomically claim one pending item; claim is not proof an external effect occurred.
        with self.transaction() as db:
            row = db.execute("SELECT outbox_id,idempotency_key,payload_json,attempts FROM outbox WHERE status='PENDING' ORDER BY created_at,outbox_id LIMIT 1").fetchone()
            if row is None: return None
            cur = db.execute("UPDATE outbox SET status='IN_FLIGHT', attempts=attempts+1, updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE outbox_id=? AND status='PENDING'", (row['outbox_id'],))
            if cur.rowcount != 1: return None
            return {'outbox_id':row['outbox_id'],'idempotency_key':row['idempotency_key'],
                    'payload':json.loads(row['payload_json']),'attempts':row['attempts']+1,'status':'IN_FLIGHT'}

    def record_outcome(self, outbox_id: str, status: str, error: str | None = None) -> None:
        if status not in {'SUCCEEDED','FAILED','OUTCOME_UNKNOWN'}:
            raise ValueError('invalid terminal outbox status')
        with self.transaction() as db:
            cur = db.execute("UPDATE outbox SET status=?, last_error=?, updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE outbox_id=? AND status='IN_FLIGHT'",
                              (status, error, outbox_id))
            if cur.rowcount != 1: raise AdmissionConflict('outbox_not_in_flight')

    def reconcile_unknown(self, idempotency_key: str, provider_state: str, evidence: str) -> dict[str, Any]:
        """Resolve an ambiguous outbox row using caller-supplied authoritative evidence.

        NOT_EXECUTED returns the row to PENDING; this method cannot verify the evidence's
        authority, so the caller is responsible for that trust boundary. Every resolution
        records the supplied evidence in last_error for auditability.
        """
        if provider_state not in {"SUCCEEDED", "FAILED", "NOT_EXECUTED"}:
            raise ValueError("invalid reconciliation state")
        if not isinstance(evidence, str) or not evidence.strip():
            raise ValueError("reconciliation evidence is required")
        target = "PENDING" if provider_state == "NOT_EXECUTED" else provider_state
        marker = f"reconciled:{provider_state}:{evidence.strip()}"[:1000]
        with self.transaction() as db:
            cur = db.execute("UPDATE outbox SET status=?, last_error=?, updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE idempotency_key=? AND status='OUTCOME_UNKNOWN'",
                             (target, marker, idempotency_key))
            if cur.rowcount != 1:
                raise AdmissionConflict("outbox_not_outcome_unknown")
        result = self.get_outbox(idempotency_key)
        assert result is not None
        return result

    def recover_in_flight(self) -> int:
        # After restart, never blindly retry a possibly executed item: mark unknown.
        with self.transaction() as db:
            cur = db.execute("UPDATE outbox SET status='OUTCOME_UNKNOWN', last_error='recovered_after_restart_requires_reconciliation', updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE status='IN_FLIGHT'")
            return cur.rowcount

    def get(self, idempotency_key: str) -> dict[str, Any] | None:
        with self._connect() as db:
            row = db.execute('SELECT receipt_json FROM admission WHERE idempotency_key=?',
                             (idempotency_key,)).fetchone()
            return json.loads(row['receipt_json']) if row else None

    def get_record(self, idempotency_key: str) -> tuple[str, dict[str, Any]] | None:
        """Return the stored fingerprint and receipt for safe runtime replay."""
        with self._connect() as db:
            row = db.execute('SELECT fingerprint, receipt_json FROM admission WHERE idempotency_key=?',
                             (idempotency_key,)).fetchone()
            return (row['fingerprint'], json.loads(row['receipt_json'])) if row else None
