"""SQLite-backed GoalRegistry, EventBus and EvidenceLedger adapters.

Local durability only. Event handlers are intentionally process-local; delivery is
at-most-once per consumer/event after reservation, so a crash after reservation can
lose handler execution. This adapter never claims durable broker semantics.
"""
from __future__ import annotations
import json, sqlite3
from contextlib import contextmanager
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
        conn.execute(f'PRAGMA busy_timeout={int(self.timeout * 1000)}')
        if self.db_path != ':memory:': conn.execute('PRAGMA journal_mode=WAL')
        return conn
    @contextmanager
    def connection(self):
        conn = self.connect()
        try: yield conn
        finally: conn.close()

class DurableGoalRegistry:
    STATUSES = GoalRegistry.STATUSES
    def __init__(self, db_path: str | Path):
        self._db = _SQLite(db_path); self._lock = RLock()
        with self._db.connection() as c:
            c.execute('CREATE TABLE IF NOT EXISTS prain_goals(goal_id TEXT PRIMARY KEY, data_json TEXT NOT NULL)')
    def _read(self, goal_id):
        with self._db.connection() as c: row = c.execute('SELECT data_json FROM prain_goals WHERE goal_id=?', (goal_id,)).fetchone()
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
        with self._lock, self._db.connection() as c:
            try: c.execute('INSERT INTO prain_goals VALUES(?,?)', (gid, _json(asdict(goal))))
            except sqlite3.IntegrityError as e: raise GoalError(f'goal already exists: {gid}') from e
        return self.get(gid)
    def _mutate(self, goal_id, fn):
        with self._lock, self._db.connection() as c:
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
        with self._db.connection() as c: rows = c.execute('SELECT goal_id FROM prain_goals ORDER BY rowid').fetchall()
        return [self.get(r[0]) for r in rows]

class DurableEventBus(EventBus):
    """SQLite-backed event log with explicit delivery states and conservative recovery.

    A crash while IN_FLIGHT becomes OUTCOME_UNKNOWN. It is never automatically
    retried because the handler may already have performed an external effect.
    """
    DELIVERY_STATES = {"PENDING", "IN_FLIGHT", "SUCCEEDED", "FAILED", "OUTCOME_UNKNOWN"}

    def __init__(self, db_path: str | Path):
        super().__init__()
        self._db = _SQLite(db_path)
        with self._db.connection() as c:
            c.execute("CREATE TABLE IF NOT EXISTS prain_events(event_id TEXT PRIMARY KEY, data_json TEXT NOT NULL)")
            c.execute("""CREATE TABLE IF NOT EXISTS prain_event_deliveries(
                event_type TEXT NOT NULL, consumer_id TEXT NOT NULL, event_id TEXT NOT NULL,
                status TEXT NOT NULL, attempts INTEGER NOT NULL DEFAULT 0,
                updated_at TEXT NOT NULL, last_error TEXT, resolution_evidence TEXT,
                PRIMARY KEY(event_type, consumer_id, event_id))""")
            # Migrate legacy processed reservations conservatively. A previous reservation
            # does not prove that its handler completed, so preserve it as unknown.
            c.execute("""CREATE TABLE IF NOT EXISTS prain_event_processed(
                event_type TEXT NOT NULL, consumer_id TEXT NOT NULL, event_id TEXT NOT NULL,
                PRIMARY KEY(event_type,consumer_id,event_id))""")
            legacy = c.execute("SELECT event_type,consumer_id,event_id FROM prain_event_processed").fetchall()
            for event_type, consumer_id, event_id in legacy:
                c.execute("""INSERT OR IGNORE INTO prain_event_deliveries
                    (event_type,consumer_id,event_id,status,attempts,updated_at,last_error)
                    VALUES(?,?,?,'OUTCOME_UNKNOWN',1,?,'migrated legacy reservation; completion unknown')""",
                    (event_type, consumer_id, event_id, goal_now()))
            # A process restart means any in-flight callback has an uncertain outcome.
            c.execute("""UPDATE prain_event_deliveries SET status='OUTCOME_UNKNOWN',
                updated_at=?, last_error='process restarted while delivery was IN_FLIGHT'
                WHERE status='IN_FLIGHT'""", (goal_now(),))

    def subscribe(self, event_type, consumer_id, handler):
        if not event_type or not consumer_id:
            raise ValueError('event_type and consumer_id must be non-empty')
        key = (event_type, consumer_id)
        with self._lock:
            if key in self._handlers:
                raise ValueError(f'consumer already subscribed: {key}')
            self._handlers[key] = handler
            self._processed[key] = set()
            with self._db.connection() as c:
                rows = c.execute("""SELECT event_id FROM prain_event_deliveries
                    WHERE event_type=? AND consumer_id=? AND status='SUCCEEDED'""", key).fetchall()
            self._processed[key].update(r[0] for r in rows)
            # Create deliveries for already-logged events so consumers can catch up.
            with self._db.connection() as c:
                events = c.execute("SELECT event_id,data_json FROM prain_events").fetchall()
                for event_id, data_json in events:
                    event = Event(**json.loads(data_json))
                    if event.event_type == event_type:
                        c.execute("""INSERT OR IGNORE INTO prain_event_deliveries
                            (event_type,consumer_id,event_id,status,attempts,updated_at)
                            VALUES(?,?,?,'PENDING',0,?)""", (event_type, consumer_id, event_id, goal_now()))
        # Resume only known-PENDING deliveries. IN_FLIGHT was conservatively changed
        # to OUTCOME_UNKNOWN at startup and is intentionally not retried.
        with self._db.connection() as c:
            pending = c.execute("""SELECT e.data_json FROM prain_events e
                JOIN prain_event_deliveries d ON d.event_id=e.event_id
                WHERE d.event_type=? AND d.consumer_id=? AND d.status='PENDING'
                ORDER BY e.rowid""", key).fetchall()
        for (data_json,) in pending:
            self._deliver(Event(**json.loads(data_json)), consumer_id, handler)

    def _deliver(self, event, consumer_id, handler):
        key = (event.event_type, consumer_id)
        with self._db.connection() as c:
            c.execute("BEGIN IMMEDIATE")
            row = c.execute("""SELECT status FROM prain_event_deliveries
                WHERE event_type=? AND consumer_id=? AND event_id=?""",
                (event.event_type, consumer_id, event.event_id)).fetchone()
            if row is None:
                c.execute("""INSERT INTO prain_event_deliveries
                    (event_type,consumer_id,event_id,status,attempts,updated_at)
                    VALUES(?,?,?,'PENDING',0,?)""", (*key, event.event_id, goal_now()))
                status = 'PENDING'
            else:
                status = row[0]
            if status == 'SUCCEEDED':
                c.commit()
                return 'duplicate_ignored'
            if status != 'PENDING':
                c.commit()
                return status.lower()
            c.execute("""UPDATE prain_event_deliveries SET status='IN_FLIGHT',
                attempts=attempts+1,updated_at=?,last_error=NULL
                WHERE event_type=? AND consumer_id=? AND event_id=? AND status='PENDING'""",
                (goal_now(), event.event_type, consumer_id, event.event_id))
            c.commit()
        try:
            handler(event)
        except Exception as exc:
            with self._db.connection() as c:
                c.execute("""UPDATE prain_event_deliveries SET status='OUTCOME_UNKNOWN',
                    updated_at=?,last_error=? WHERE event_type=? AND consumer_id=? AND event_id=? AND status='IN_FLIGHT'""",
                    (goal_now(), f'{type(exc).__name__}: {exc}'[:1000], event.event_type, consumer_id, event.event_id))
            raise
        with self._db.connection() as c:
            c.execute("""UPDATE prain_event_deliveries SET status='SUCCEEDED',updated_at=?
                WHERE event_type=? AND consumer_id=? AND event_id=? AND status='IN_FLIGHT'""",
                (goal_now(), event.event_type, consumer_id, event.event_id))
        with self._lock:
            self._processed.setdefault(key, set()).add(event.event_id)
        return 'processed'

    def publish(self, event):
        with self._db.connection() as c:
            c.execute("INSERT OR IGNORE INTO prain_events VALUES(?,?)", (event.event_id, _json(asdict(event))))
            subscriptions = [(key, handler) for key, handler in self._handlers.items()
                             if key[0] == event.event_type]
            for key, _ in subscriptions:
                c.execute("""INSERT OR IGNORE INTO prain_event_deliveries
                    (event_type,consumer_id,event_id,status,attempts,updated_at)
                    VALUES(?,?,?,'PENDING',0,?)""", (*key, event.event_id, goal_now()))
        results = {}
        for key, handler in subscriptions:
            results[key[1]] = self._deliver(event, key[1], handler)
        return results

    def delivery_status(self, event_type, consumer_id, event_id):
        with self._db.connection() as c:
            row = c.execute("""SELECT status,attempts,updated_at,last_error,resolution_evidence
                FROM prain_event_deliveries WHERE event_type=? AND consumer_id=? AND event_id=?""",
                (event_type, consumer_id, event_id)).fetchone()
        if row is None:
            raise KeyError("unknown event delivery")
        return dict(zip(("status","attempts","updated_at","last_error","resolution_evidence"), row))

    def reconcile_delivery(self, event_type, consumer_id, event_id, provider_state, evidence):
        """Resolve ambiguity using caller-supplied evidence; evidence is not independently verified."""
        if provider_state not in {"SUCCEEDED", "FAILED", "NOT_EXECUTED"}:
            raise ValueError("provider_state must be SUCCEEDED, FAILED, or NOT_EXECUTED")
        if not isinstance(evidence, str) or not evidence.strip():
            raise ValueError("non-empty reconciliation evidence is required")
        status = "PENDING" if provider_state == "NOT_EXECUTED" else provider_state
        with self._db.connection() as c:
            c.execute("BEGIN IMMEDIATE")
            cur = c.execute("""UPDATE prain_event_deliveries SET status=?,updated_at=?,
                last_error=?,resolution_evidence=? WHERE event_type=? AND consumer_id=?
                AND event_id=? AND status='OUTCOME_UNKNOWN'""",
                (status, goal_now(), f"reconciled:{provider_state}", evidence.strip(),
                 event_type, consumer_id, event_id))
            if cur.rowcount != 1:
                c.rollback()
                raise ValueError("delivery_not_outcome_unknown")
            c.commit()
        if status == "SUCCEEDED":
            with self._lock:
                self._processed.setdefault((event_type,consumer_id),set()).add(event_id)
        return self.delivery_status(event_type, consumer_id, event_id)

    def events(self):
        with self._db.connection() as c:
            rows = c.execute('SELECT data_json FROM prain_events ORDER BY rowid').fetchall()
        return [Event(**json.loads(r[0])) for r in rows]

class DurableEvidenceLedger(EvidenceLedger):
    def __init__(self, db_path: str | Path):
        self._db=_SQLite(db_path); self._entries=[]; self._lock=RLock()
        with self._db.connection() as c:
            c.execute('CREATE TABLE IF NOT EXISTS prain_evidence(seq INTEGER PRIMARY KEY AUTOINCREMENT, entry_id TEXT UNIQUE NOT NULL, data_json TEXT NOT NULL)')
            rows=c.execute('SELECT data_json FROM prain_evidence ORDER BY seq').fetchall()
        self._entries=[EvidenceEntry(**json.loads(r[0])) for r in rows]
        if not self.verify(): raise ValueError('persisted evidence chain failed integrity verification')
    def append(self, kind, subject, payload):
        with self._lock:
            entry=super().append(kind,subject,payload)
            try:
                with self._db.connection() as c: c.execute('INSERT INTO prain_evidence(entry_id,data_json) VALUES(?,?)',(entry.entry_id,_json(asdict(entry))))
            except Exception:
                self._entries.pop()
                raise
            return entry
