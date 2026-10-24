"""Atomic evidence-backed completion for the real v1.2.19 durable runtime.

Opt-in integration. Authentication is supplied by a trusted host boundary,
not inferred from caller-supplied identity or evidence payloads. This module
does not prove real-world claim truth or disable the legacy completion paths.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path
import json
import re
import sqlite3
from typing import Callable

from .durable_components import DurableEvidenceLedger, DurableGoalRegistry, _json
from .evidence_ledger import EvidenceEntry, EvidenceLedger
from .goal_registry import Goal, _now, validate_verification


class SecureCompletionError(ValueError):
    """Rejected completion or integrity proof."""


@dataclass(frozen=True)
class AuthenticatedVerifier:
    principal_id: str
    verifier_id: str


_EVIDENCE_REF = re.compile(r"evidence://sha256/([0-9a-f]{64})\Z")
_HEAD = re.compile(r"[0-9a-f]{64}\Z")


class SecureGoalCompletion:
    """Durable completion facade over the existing prain_goals/prain_evidence.

    All read/validate/write operations use one BEGIN IMMEDIATE transaction.
    Callers must receive this facade from a trusted host holding the
    authenticator. The legacy PRAINRuntime.verify_goal and registry methods
    are NOT secured by this facade and still require migration/lockdown.
    """

    def __init__(self, runtime, authenticate: Callable[[str], AuthenticatedVerifier | None]):
        if not callable(authenticate):
            raise SecureCompletionError("authentication_required")
        goals, evidence = getattr(runtime, "goals", None), getattr(runtime, "evidence", None)
        if not isinstance(goals, DurableGoalRegistry) or not isinstance(evidence, DurableEvidenceLedger):
            raise SecureCompletionError("durable_runtime_required")
        gpath = Path(goals._db.db_path).resolve()
        epath = Path(evidence._db.db_path).resolve()
        if goals._db.db_path == ":memory:" or evidence._db.db_path == ":memory:" or gpath != epath:
            raise SecureCompletionError("same_persistent_database_required")
        self.db_path = str(gpath)
        self._authenticate = authenticate
        with self._connection() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS prain_goal_completion_receipts(
                goal_id TEXT PRIMARY KEY, receipt_json TEXT NOT NULL)""")

    @contextmanager
    def _connection(self):
        db = sqlite3.connect(self.db_path, timeout=15, isolation_level=None)
        try:
            db.execute("PRAGMA busy_timeout=15000")
            yield db
        finally:
            db.close()

    def _authenticated_verifier(self, principal):
        if not isinstance(principal, str) or not principal.strip():
            raise SecureCompletionError("principal_required")
        identity = self._authenticate(principal)
        if (not isinstance(identity, AuthenticatedVerifier)
            or identity.principal_id != principal
            or not isinstance(identity.verifier_id, str)
            or not identity.verifier_id.strip()):
            raise SecureCompletionError("untrusted_verifier")
        return identity.verifier_id

    @staticmethod
    def _load_ledger(db):
        rows = db.execute("SELECT data_json FROM prain_evidence ORDER BY seq").fetchall()
        ledger = EvidenceLedger()
        ledger._entries = [EvidenceEntry(**json.loads(row[0])) for row in rows]
        if not ledger.verify():
            raise SecureCompletionError("invalid_evidence_chain")
        return ledger

    @staticmethod
    def _validate_evidence(goal, ledger, verifier, criterion_results):
        if goal.status != "active":
            raise SecureCompletionError("goal_not_active")
        criteria = goal.acceptance_criteria
        if not isinstance(criteria, list) or not criteria:
            raise SecureCompletionError("missing_criteria")
        expected_ids = {c["id"] for c in criteria}
        if len(expected_ids) != len(criteria):
            raise SecureCompletionError("duplicate_criteria")
        if not isinstance(criterion_results, list) or len(criterion_results) != len(criteria):
            raise SecureCompletionError("incomplete_criteria")
        entries = {e.entry_hash: e for e in ledger.entries()}
        ids, refs_all = set(), set()
        for result in criterion_results:
            if not isinstance(result, dict) or set(result) != {"id", "passed", "evidence_refs"}:
                raise SecureCompletionError("malformed_criterion_result")
            cid, refs = result["id"], result["evidence_refs"]
            if (cid not in expected_ids or cid in ids or result["passed"] is not True
                or not isinstance(refs, list) or not refs):
                raise SecureCompletionError("invalid_criterion_result")
            ids.add(cid)
            for ref in refs:
                match = _EVIDENCE_REF.fullmatch(ref) if isinstance(ref, str) else None
                if match is None or ref in refs_all:
                    raise SecureCompletionError("invalid_or_duplicate_evidence_ref")
                refs_all.add(ref)
                entry = entries.get(match.group(1))
                if entry is None:
                    raise SecureCompletionError("evidence_not_found")
                payload = entry.payload
                if (entry.kind != "criterion.verification" or entry.subject != goal.goal_id
                    or not isinstance(payload, dict)
                    or payload.get("goal_id") != goal.goal_id
                    or payload.get("criterion_id") != cid
                    or payload.get("verifier") != verifier
                    or payload.get("passed") is not True):
                    raise SecureCompletionError("evidence_scope_mismatch")
        if ids != expected_ids:
            raise SecureCompletionError("incomplete_criteria")
        return sorted(refs_all)

    def receipt(self, goal_id):
        with self._connection() as db:
            row = db.execute(
                "SELECT receipt_json FROM prain_goal_completion_receipts WHERE goal_id=?", (goal_id,)
            ).fetchone()
        return json.loads(row[0]) if row else None

    def complete(self, goal_id, *, principal, criterion_results, expected_ledger_head):
        verifier = self._authenticated_verifier(principal)
        if not isinstance(goal_id, str) or not goal_id.strip():
            raise SecureCompletionError("invalid_goal_id")
        if not isinstance(expected_ledger_head, str) or _HEAD.fullmatch(expected_ledger_head) is None:
            raise SecureCompletionError("expected_ledger_head_required")
        with self._connection() as db:
            db.execute("BEGIN IMMEDIATE")
            try:
                row = db.execute("SELECT data_json FROM prain_goals WHERE goal_id=?", (goal_id,)).fetchone()
                if row is None:
                    raise SecureCompletionError("goal_not_found")
                goal = Goal(**json.loads(row[0]))
                if goal.goal_id != goal_id:
                    raise SecureCompletionError("goal_identity_mismatch")
                ledger = self._load_ledger(db)
                current_head = ledger.entries()[-1].entry_hash if ledger.entries() else EvidenceLedger.GENESIS
                if expected_ledger_head != current_head:
                    raise SecureCompletionError("stale_ledger_head")
                refs = self._validate_evidence(goal, ledger, verifier, criterion_results)
                verification = validate_verification(goal, True, refs, verifier, criterion_results)
                goal.verification, goal.status, goal.updated_at = verification, "completed", _now()
                updated = db.execute(
                    "UPDATE prain_goals SET data_json=? WHERE goal_id=? AND data_json=?",
                    (_json(asdict(goal)), goal_id, row[0]),
                )
                if updated.rowcount != 1:
                    raise SecureCompletionError("concurrent_goal_change")
                entry = ledger.append("goal.verification", goal_id, {
                    "goal_id": goal_id, "verifier": verifier, "passed": True,
                    "criterion_results": criterion_results,
                    "verified_ledger_head": current_head,
                })
                db.execute("INSERT INTO prain_evidence(entry_id,data_json) VALUES(?,?)",
                           (entry.entry_id, _json(asdict(entry))))
                receipt = {
                    "goal_id": goal_id, "ledger_head": current_head,
                    "completion_entry_hash": entry.entry_hash,
                    "verifier": verifier, "passed": True,
                    "evidence_refs": refs, "criterion_results": criterion_results,
                }
                db.execute("INSERT INTO prain_goal_completion_receipts(goal_id,receipt_json) VALUES(?,?)",
                           (goal_id, _json(receipt)))
                db.commit()
                return receipt
            except BaseException:
                db.rollback()
                raise

    def audit(self, goal_id):
        """Reconcile persisted goal, receipt and completion event in one read snapshot."""
        with self._connection() as db:
            db.execute("BEGIN")
            try:
                goal_row = db.execute("SELECT data_json FROM prain_goals WHERE goal_id=?", (goal_id,)).fetchone()
                receipt_row = db.execute(
                    "SELECT receipt_json FROM prain_goal_completion_receipts WHERE goal_id=?",
                    (goal_id,),
                ).fetchone()
                ledger = self._load_ledger(db)
                if goal_row is None or receipt_row is None:
                    raise SecureCompletionError("missing_completion_record")
                goal, receipt = Goal(**json.loads(goal_row[0])), json.loads(receipt_row[0])
                entries = [e for e in ledger.entries() if e.entry_hash == receipt.get("completion_entry_hash")]
                if len(entries) != 1:
                    raise SecureCompletionError("missing_completion_evidence")
                entry = entries[0]
                verification = goal.verification
                if (goal.goal_id != goal_id or goal.status != "completed"
                    or not isinstance(verification, dict) or verification.get("passed") is not True
                    or receipt.get("goal_id") != goal_id or receipt.get("passed") is not True
                    or receipt.get("verifier") != verification.get("verifier")
                    or receipt.get("evidence_refs") != verification.get("evidence_refs")
                    or receipt.get("criterion_results") != verification.get("criterion_results")
                    or entry.kind != "goal.verification" or entry.subject != goal_id
                    or entry.previous_hash != receipt.get("ledger_head")
                    or entry.payload.get("verified_ledger_head") != receipt.get("ledger_head")
                    or entry.payload.get("criterion_results") != receipt.get("criterion_results")
                    or entry.payload.get("verifier") != receipt.get("verifier")):
                    raise SecureCompletionError("completion_integrity_mismatch")
                db.commit()
                return True
            except BaseException:
                db.rollback()
                raise
