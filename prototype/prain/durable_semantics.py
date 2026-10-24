"""SQLite-backed Anima and SCF reference adapters; local persistence, no distributed transport."""
from __future__ import annotations
from dataclasses import asdict
from copy import deepcopy
import json
import sqlite3
from pathlib import Path
from threading import RLock

from .anima_hal import Anima, AnimaConflict, SelfModel
from .scf import SemanticFabric, SemanticClaim, SCFDecision, _timestamp


class DurableAnima(Anima):
    def __init__(self, identity_id: str, db_path: str):
        super().__init__(identity_id)
        self._db_path = str(db_path)
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        with self._connection() as c:
            c.execute("CREATE TABLE IF NOT EXISTS prain_anima(identity_id TEXT PRIMARY KEY, version INTEGER NOT NULL, data_json TEXT NOT NULL)")
            c.execute("INSERT OR IGNORE INTO prain_anima VALUES(?,0,?)",
                (identity_id, json.dumps(asdict(self._model), sort_keys=True)))

    def _connection(self):
        return sqlite3.connect(self._db_path, timeout=15)

    def snapshot(self):
        with self._connection() as c:
            row = c.execute("SELECT data_json FROM prain_anima WHERE identity_id=?", (self._model.identity_id,)).fetchone()
        if row is None:
            raise AnimaConflict("self_model_missing")
        return SelfModel(**json.loads(row[0]))

    def update(self, *, expected_version: int, dimension: str, state: dict, provenance: str):
        if dimension not in self.DIMENSIONS or not isinstance(state, dict) or not isinstance(provenance, str) or not provenance.strip():
            raise ValueError("invalid self-model update")
        forbidden = {"grant", "capabilities", "approval", "policy_override"}
        if any(str(k).lower() in forbidden for k in state):
            raise AnimaConflict("self_model_cannot_grant_authority")
        if type(expected_version) is not int:
            raise AnimaConflict("stale_self_model_version")
        with self._connection() as c:
            c.execute("BEGIN IMMEDIATE")
            row = c.execute("SELECT data_json FROM prain_anima WHERE identity_id=?", (self._model.identity_id,)).fetchone()
            if not row:
                raise AnimaConflict("self_model_missing")
            model = SelfModel(**json.loads(row[0]))
            if model.version != expected_version:
                raise AnimaConflict("stale_self_model_version")
            dimensions = deepcopy(model.dimensions)
            dimensions[dimension] = deepcopy(state)
            new = SelfModel(model.identity_id, model.version + 1, dimensions, provenance)
            c.execute("UPDATE prain_anima SET version=?, data_json=? WHERE identity_id=? AND version=?",
                      (new.version, json.dumps(asdict(new), sort_keys=True, allow_nan=False), model.identity_id, expected_version))
            c.commit()
            return new


class DurableSemanticFabric(SemanticFabric):
    """Serializes SCF projections and decisions under one SQLite write lock.

    SQLite provides single-node concurrent-writer serialization, not cross-node
    consensus or a distributed lease. Projections remain non-authoritative.
    """
    def __init__(self, db_path: str):
        super().__init__()
        self._db_path = str(db_path)
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        with self._connection() as c:
            c.execute("CREATE TABLE IF NOT EXISTS prain_scf_state(id INTEGER PRIMARY KEY CHECK(id=1), state_json TEXT NOT NULL)")
            c.execute("INSERT OR IGNORE INTO prain_scf_state VALUES(1,?)",
                      (json.dumps(self._export(), sort_keys=True),))
            c.execute("""CREATE TABLE IF NOT EXISTS prain_scf_inbox(
                message_id TEXT PRIMARY KEY, fingerprint TEXT NOT NULL,
                decision_json TEXT NOT NULL)""")

    def _connection(self):
        return sqlite3.connect(self._db_path, timeout=15)

    def _export(self):
        return dict(claims={k: asdict(v) for k,v in self._claims.items()},
                    conflicts=self._conflicts, decisions=[asdict(d) for d in self._decisions],
                    invalidated=sorted(self._invalidated))

    def _restore(self, raw):
        state = json.loads(raw)
        self._claims = {k: SemanticClaim(**{**v, "evidence_refs": tuple(v["evidence_refs"]),
                          "dependencies": tuple(v["dependencies"])}) for k,v in state["claims"].items()}
        self._conflicts = deepcopy(state["conflicts"])
        self._decisions = [SCFDecision(**d) for d in state["decisions"]]
        self._invalidated = set(state["invalidated"])

    def _refresh(self):
        with self._connection() as c:
            row = c.execute("SELECT state_json FROM prain_scf_state WHERE id=1").fetchone()
        if row is None:
            raise RuntimeError("scf_store_missing")
        self._restore(row[0])

    def ingest(self, claim: SemanticClaim, recipient_scope: str, now: str):
        with self._lock, self._connection() as c:
            c.execute("BEGIN IMMEDIATE")
            row = c.execute("SELECT state_json FROM prain_scf_state WHERE id=1").fetchone()
            if row is None:
                raise RuntimeError("scf_store_missing")
            self._restore(row[0])
            decision = super().ingest(claim, recipient_scope, now)
            c.execute("UPDATE prain_scf_state SET state_json=? WHERE id=1",
                      (json.dumps(self._export(), sort_keys=True, allow_nan=False),))
            c.commit()
            return decision

    def ingest_message(self, message_id: str, claim: SemanticClaim, recipient_scope: str, now: str):
        """Atomic local SCF inbox + state transition, with idempotent replay.

        Same message ID with a changed body is a conflict. A committed message
        is never reapplied, including after runtime restart or concurrent delivery.
        This does not by itself provide a network transport.
        """
        import hashlib
        if not isinstance(message_id, str) or not message_id.strip():
            raise ValueError("message_id_required")
        if not isinstance(claim, SemanticClaim):
            raise TypeError("semantic_claim_required")
        serialized = json.dumps({"claim": asdict(claim), "scope": recipient_scope, "now": now},
                                sort_keys=True, separators=(",", ":"), allow_nan=False)
        fingerprint = hashlib.sha256(serialized.encode()).hexdigest()
        with self._lock, self._connection() as c:
            c.execute("BEGIN IMMEDIATE")
            prior = c.execute("SELECT fingerprint,decision_json FROM prain_scf_inbox WHERE message_id=?",
                              (message_id,)).fetchone()
            if prior is not None:
                if prior[0] != fingerprint:
                    raise ValueError("message_id_conflict")
                return SCFDecision(**json.loads(prior[1]))
            row = c.execute("SELECT state_json FROM prain_scf_state WHERE id=1").fetchone()
            if row is None:
                raise RuntimeError("scf_store_missing")
            self._restore(row[0])
            decision = super().ingest(claim, recipient_scope, now)
            c.execute("UPDATE prain_scf_state SET state_json=? WHERE id=1",
                      (json.dumps(self._export(), sort_keys=True, allow_nan=False),))
            c.execute("INSERT INTO prain_scf_inbox VALUES(?,?,?)",
                      (message_id, fingerprint, json.dumps(asdict(decision), sort_keys=True)))
            c.commit()
            return decision

    def projection(self, claim_id):
        with self._lock:
            self._refresh()
            return super().projection(claim_id)

    def decisions(self):
        with self._lock:
            self._refresh()
            return super().decisions()

    def conflicts(self):
        with self._lock:
            self._refresh()
            return super().conflicts()