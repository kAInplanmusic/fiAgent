"""SQLite-backed versioned state store with transactional compare-and-swap."""
from __future__ import annotations
import json
import sqlite3
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from .state_store import StateConflict, StateRecord, utc_now

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
            conn.execute('''CREATE TABLE IF NOT EXISTS prain_state (
                state_key TEXT PRIMARY KEY,
                value_json TEXT NOT NULL,
                version INTEGER NOT NULL CHECK(version >= 1),
                updated_at TEXT NOT NULL
            )''')

    def _connect(self):
        conn = sqlite3.connect(self.db_path, timeout=self.timeout, isolation_level=None)
        conn.execute('PRAGMA busy_timeout = 10000')
        conn.execute('PRAGMA journal_mode = WAL')
        return conn

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
            raise StateConflict(f'state already exists: {key}') from exc
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

    compareAndSwap = compare_and_swap
