"""SQLite-backed GoalRegistry, EventBus and EvidenceLedger adapters.

Local durability only. Event handlers are intentionally process-local; delivery is
at-most-once per consumer/event after reservation, so a crash after reservation can
lose handler execution. This adapter never claims durable broker semantics.
"""
from __future__ import annotations
import json, sqlite3
from dataclasses import asdict
from pathlib import Path
from threading import RLock
from typing import Any
from .goal_registry import Goal, GoalError, GoalRegistry, _now as goal_now
from .event_bus import Event, EventBus
from .evidence_ledger import EvidenceEntry, EvidenceLedger


def _json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

class _SQLite:
    def __init__(self, db_path: str | Path, timeout: float = 10.0):
        self.db_path, self.timeout = str(db_path), timeout
        if self.db_path != ':memory:':
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
    def connect(self):
        conn = sqlite3.connect(self.db_path, timeout=self.timeout, isolation_level=None)
        conn.execute('PRAGMA busy_timeout=10000')
        conn.execute('PRAGMA journal_mode=WAL')
        return conn

class DurableGoalRegistry:
    STATUSES = GoalRegistry.STATUSES
    def __init__(self, db_path: str | Path):
        self._db = _SQLite(db_path); self._lock = RLock()
        with self._db.connect() as c:
            c.execute('CREATE TABLE IF NOT EXISTS prain_goals(goal_id TEXT PRIMARY KEY, data_json TEXT NOT NULL)')
    def _read(self, goal_id):
        with self._db.connect() as c: row = c.execute('SELECT data_json FROM prain_goals WHERE goal_id=?', (goal_id,)).fetchone()
        if row is None: raise KeyError(f'unknown goal: {goal_id}')
        return Goal(**json.loads(row[0]))
    def create(self, title, acceptance_criteria, goal_id=None):
        import uuid
        if not isinstance(title, str) or not title.strip(): raise GoalError('title must be non-empty')
        if not acceptance_criteria: raise GoalError('at least one machine-checkable acceptance criterion is required')
        for criterion in acceptance_criteria:
            if not isinstance(criterion, dict) or not criterion.get('id') or not criterion.get('check'):
                raise GoalError('each criterion needs non-empty id and check fields')
        gid = goal_id or str(uuid.uuid4()); now = goal_now()
        goal = Goal(gid, title, acceptance_criteria, 'proposed', now, now)
        with self._lock, self._db.connect() as c:
            try: c.execute('INSERT INTO prain_goals VALUES(?,?)', (gid, _json(asdict(goal))))
            except sqlite3.IntegrityError as e: raise GoalError(f'goal already exists: {gid}') from e
        return self.get(gid)
    def _mutate(self, goal_id, fn):
        with self._lock, self._db.connect() as c:
            c.execute('BEGIN IMMEDIATE')
            row = c.execute('SELECT data_json FROM prain_goals WHERE goal_id=?', (goal_id,)).fetchone()
            if row is None: c.rollback(); raise KeyError(f'unknown goal: {goal_id}')
            goal = Goal(**json.loads(row[0])); fn(goal); c.execute('UPDATE prain_goals SET data_json=? WHERE goal_id=?', (_json(asdict(goal)), goal_id)); c.commit()
        return self.get(goal_id)
    def activate(self, goal_id):
        def f(g):
            if g.status != 'proposed': raise GoalError(f'cannot activate from {g.status}')
            g.status, g.updated_at = 'active', goal_now()
        return self._mutate(goal_id, f)
    def set_status(self, goal_id, status):
        def f(g):
            if status not in self.STATUSES: raise GoalError(f'unknown status: {status}')
            if status == 'completed': raise GoalError('completed requires passing verification')
            g.status, g.updated_at = status, goal_now()
        return self._mutate(goal_id, f)
    def record_verification(self, goal_id, passed, evidence_refs, verifier):
        def f(g):
            if not verifier or not verifier.strip(): raise GoalError('verifier must be identified')
            if passed and not evidence_refs: raise GoalError('passing verification requires evidence references')
            g.verification = {'passed': bool(passed), 'evidence_refs': list(evidence_refs), 'verifier': verifier, 'verified_at': goal_now()}
            g.status, g.updated_at = ('completed' if passed else 'failed'), goal_now()
        return self._mutate(goal_id, f)
    def get(self, goal_id): return self._read(goal_id)
    def list(self):
        with self._db.connect() as c: rows = c.execute('SELECT goal_id FROM prain_goals ORDER BY rowid').fetchall()
        return [self.get(r[0]) for r in rows]

class DurableEventBus(EventBus):
    """Persist event log and consumer reservations; callbacks must be re-registered after restart."""
    def __init__(self, db_path: str | Path):
        super().__init__(); self._db = _SQLite(db_path)
        with self._db.connect() as c:
            c.execute('CREATE TABLE IF NOT EXISTS prain_events(event_id TEXT PRIMARY KEY, data_json TEXT NOT NULL)')
            c.execute('CREATE TABLE IF NOT EXISTS prain_event_processed(event_type TEXT NOT NULL, consumer_id TEXT NOT NULL, event_id TEXT NOT NULL, PRIMARY KEY(event_type,consumer_id,event_id))')
    def subscribe(self, event_type, consumer_id, handler):
        if not event_type or not consumer_id: raise ValueError('event_type and consumer_id must be non-empty')
        key=(event_type,consumer_id)
        with self._lock:
            if key in self._handlers: raise ValueError(f'consumer already subscribed: {key}')
            self._handlers[key]=handler; self._processed[key]=set()
            with self._db.connect() as c:
                rows=c.execute('SELECT event_id FROM prain_event_processed WHERE event_type=? AND consumer_id=?',(event_type,consumer_id)).fetchall()
            self._processed[key].update(r[0] for r in rows)
    def publish(self, event):
        with self._db.connect() as c:
            try: c.execute('INSERT INTO prain_events VALUES(?,?)',(event.event_id,_json(asdict(event))))
            except sqlite3.IntegrityError: pass
        results={}
        with self._lock: subscriptions=list(self._handlers.items())
        for key,handler in subscriptions:
            event_type,consumer_id=key
            if event_type != event.event_type: continue
            with self._lock:
                if event.event_id in self._processed[key]: results[consumer_id]='duplicate_ignored'; continue
                # Durable reservation before callback: avoids duplicates, but a crash here can lose delivery.
                with self._db.connect() as c:
                    try: c.execute('INSERT INTO prain_event_processed VALUES(?,?,?)', (event_type,consumer_id,event.event_id))
                    except sqlite3.IntegrityError:
                        self._processed[key].add(event.event_id); results[consumer_id]='duplicate_ignored'; continue
                self._processed[key].add(event.event_id)
            try: handler(event)
            except Exception:
                results[consumer_id]='handler_failed_no_auto_retry'; raise
            results[consumer_id]='processed'
        return results
    def events(self):
        with self._db.connect() as c: rows=c.execute('SELECT data_json FROM prain_events ORDER BY rowid').fetchall()
        return [Event(**json.loads(r[0])) for r in rows]

class DurableEvidenceLedger(EvidenceLedger):
    def __init__(self, db_path: str | Path):
        self._db=_SQLite(db_path); self._entries=[]; self._lock=RLock()
        with self._db.connect() as c:
            c.execute('CREATE TABLE IF NOT EXISTS prain_evidence(seq INTEGER PRIMARY KEY AUTOINCREMENT, entry_id TEXT UNIQUE NOT NULL, data_json TEXT NOT NULL)')
            rows=c.execute('SELECT data_json FROM prain_evidence ORDER BY seq').fetchall()
        self._entries=[EvidenceEntry(**json.loads(r[0])) for r in rows]
        if not self.verify(): raise ValueError('persisted evidence chain failed integrity verification')
    def append(self, kind, subject, payload):
        with self._lock:
            entry=super().append(kind,subject,payload)
            try:
                with self._db.connect() as c: c.execute('INSERT INTO prain_evidence(entry_id,data_json) VALUES(?,?)',(entry.entry_id,_json(asdict(entry))))
            except Exception:
                self._entries.pop()
                raise
            return entry
