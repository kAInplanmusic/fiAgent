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
              receipt: dict[str, Any], approval_id: str | None = None) -> tuple[dict[str, Any], bool]:
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
            return json.loads(serialized), True

    def get(self, idempotency_key: str) -> dict[str, Any] | None:
        with self._connect() as db:
            row = db.execute('SELECT receipt_json FROM admission WHERE idempotency_key=?',
                             (idempotency_key,)).fetchone()
            return json.loads(row['receipt_json']) if row else None
