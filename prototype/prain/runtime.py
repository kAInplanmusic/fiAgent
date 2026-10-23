"""Small, deterministic PRAIN reference runtime; external effects are simulated only."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import json
from typing import Any, Callable
from threading import RLock

from . import ActionRequest, EvidenceLedger, Event, EventBus, GoalRegistry, PolicyGateway, StateStore
from .durable_admission import AdmissionConflict, DurableAdmissionStore
from .durable_components import DurableGoalRegistry, DurableEventBus, DurableEvidenceLedger
from .durable_state_store import DurableStateStore


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def canonical_hash(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return sha256(raw.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class Observation:
    observation_id: str
    source: str
    kind: str
    payload: dict[str, Any]
    observed_at: str

    @classmethod
    def create(cls, source: str, kind: str, payload: dict[str, Any], observation_id: str | None = None) -> "Observation":
        if not source.strip() or not kind.strip():
            raise ValueError("observation source and kind are required")
        if not isinstance(payload, dict):
            raise TypeError("observation payload must be a dictionary")
        import uuid
        return cls(observation_id or str(uuid.uuid4()), source, kind, deepcopy(payload), _utc())


@dataclass(frozen=True)
class ExecutionReceipt:
    receipt_id: str
    correlation_id: str
    action: str
    target: str
    status: str
    policy_decision_id: str
    result: dict[str, Any]
    completed_at: str


class PRAINRuntime:
    """Wires P/R/A/I/N responsibilities into a testable in-process vertical slice.

    P=observation intake, R=rule/evaluator decision, A=explicit context/state,
    I=goal/action intent, N=policy-gated simulated execution.
    This class never invokes real external side effects.
    """
    def __init__(self, policies: list[dict[str, Any]] | None = None,
                 evaluators: dict[str, Callable[[Observation], bool]] | None = None,
                 admission_store: DurableAdmissionStore | None = None,
                 persistent_db_path: str | None = None):
        self.state = DurableStateStore(persistent_db_path) if persistent_db_path else StateStore()
        self.events = DurableEventBus(persistent_db_path) if persistent_db_path else EventBus()
        self.goals = DurableGoalRegistry(persistent_db_path) if persistent_db_path else GoalRegistry()
        self.policy = PolicyGateway(policies or [])
        self.evidence = DurableEvidenceLedger(persistent_db_path) if persistent_db_path else EvidenceLedger()
        self.evaluators = dict(evaluators or {})
        self._receipts: dict[str, ExecutionReceipt] = {}
        self._request_fingerprints: dict[str, str] = {}
        # Serializes this in-process runtime only; it is not a distributed lock.
        self._action_lock = RLock()
        self._consumed_approval_ids: set[str] = set()
        # A persistent_db_path enables SQLite-backed state, goals, event log/reservations,
        # and evidence. Admission/outbox persistence remains separately opt-in.
        self.admission_store = admission_store

    def ingest(self, observation: Observation) -> Event:
        """Record an observation and publish a correlated event."""
        entry = self.evidence.append("observation.received", observation.observation_id, asdict(observation))
        event = Event.create("prain.observation.received", {
            "observation_id": observation.observation_id,
            "observation_hash": canonical_hash(asdict(observation)),
            "evidence_entry_hash": entry.entry_hash,
        }, correlation_id=observation.observation_id)
        self.events.publish(event)
        return event

    def evaluate(self, observation: Observation, evaluator_name: str) -> dict[str, Any]:
        """Evaluate a named registered check; unknown checks fail closed."""
        evaluator = self.evaluators.get(evaluator_name)
        passed = bool(evaluator(observation)) if evaluator is not None else False
        result = {
            "observation_id": observation.observation_id,
            "evaluator": evaluator_name,
            "passed": passed,
            "evaluated_at": _utc(),
        }
        entry = self.evidence.append("observation.evaluated", observation.observation_id, result)
        result["evidence_ref"] = f"evidence://sha256/{entry.entry_hash}"
        return result

    def request_action(self, action: str, target: str, capability: str | None,
                       actor: str, payload: dict[str, Any], correlation_id: str,
                       idempotency_key: str, approval: dict[str, Any] | None = None) -> tuple[ExecutionReceipt | None, dict[str, Any]]:
        """Serialize action admission in this process; distributed atomicity is not provided."""
        with self._action_lock:
            return self._request_action_locked(action, target, capability, actor, payload,
                                               correlation_id, idempotency_key, approval)

    def _request_action_locked(self, action: str, target: str, capability: str | None,
                               actor: str, payload: dict[str, Any], correlation_id: str,
                               idempotency_key: str, approval: dict[str, Any] | None = None) -> tuple[ExecutionReceipt | None, dict[str, Any]]:
        """Authorize then simulate an action. Denials never execute; repeated keys replay receipt."""
        # Snapshot caller-owned input before hashing or policy evaluation: otherwise a
        # nested mutable object can change after request construction (aliasing).
        payload_snapshot = deepcopy(payload)
        request = ActionRequest.create(action, target, capability, actor, payload_snapshot,
                                       correlation_id=correlation_id, idempotency_key=idempotency_key)
        fingerprint = canonical_hash({
            "action": action, "target": target, "capability": capability, "actor": actor,
            "payload": payload_snapshot, "correlation_id": correlation_id,
        })
        if self.admission_store is not None:
            stored = self.admission_store.get_record(idempotency_key)
            if stored is not None:
                stored_fingerprint, stored_data = stored
                if stored_fingerprint != fingerprint:
                    return None, {"allowed": False, "reason": "idempotency_key_conflict",
                                  "policy_decision_id": stored_data.get("policy_decision_id", "durable-replay")}
                receipt = ExecutionReceipt(**stored_data)
                self._receipts[idempotency_key] = receipt
                self._request_fingerprints[idempotency_key] = fingerprint
                return receipt, {"allowed": True, "reason": "idempotent_replay",
                                 "policy_decision_id": receipt.policy_decision_id}
        if idempotency_key in self._receipts:
            receipt = self._receipts[idempotency_key]
            if self._request_fingerprints[idempotency_key] != fingerprint:
                return None, {"allowed": False, "reason": "idempotency_key_conflict",
                              "policy_decision_id": receipt.policy_decision_id}
            return receipt, {"allowed": True, "reason": "idempotent_replay", "policy_decision_id": receipt.policy_decision_id}
        decision = self.policy.evaluate(request, approval=approval)
        # A single-use approval must have a stable ID and may authorize only one
        # newly admitted action in this runtime. Same-key replay is handled above.
        if decision.allowed and approval and approval.get("usage_policy") == "single_use":
            approval_id = approval.get("approval_id")
            if not isinstance(approval_id, str) or not approval_id.strip():
                decision = type(decision)(decision.decision_id, False,
                    "single_use_approval_id_required", decision.policy_id,
                    decision.evaluated_at, decision.action_request_hash)
            elif self.admission_store is None and approval_id in self._consumed_approval_ids:
                decision = type(decision)(decision.decision_id, False,
                    "approval_already_consumed", decision.policy_id,
                    decision.evaluated_at, decision.action_request_hash)
            elif self.admission_store is None:
                self._consumed_approval_ids.add(approval_id)
        self.evidence.append("policy.decision", decision.decision_id, asdict(decision))
        if not decision.allowed:
            self.evidence.append("action.denied", idempotency_key, {
                "reason": decision.reason, "request_hash": decision.action_request_hash,
            })
            return None, asdict(decision)
        # Deliberately simulated. No filesystem, network, shell or external service is called.
        result = {"simulated": True, "accepted_action": action, "target": target,
                  "input_hash": canonical_hash(payload_snapshot)}
        receipt = ExecutionReceipt(
            receipt_id=canonical_hash({"key": idempotency_key, "decision": decision.decision_id}),
            correlation_id=correlation_id, action=action, target=target, status="simulated_success",
            policy_decision_id=decision.decision_id, result=result, completed_at=_utc(),
        )
        if self.admission_store is not None:
            approval_id = None
            if approval and approval.get("usage_policy") == "single_use":
                approval_id = approval.get("approval_id")
            try:
                stored_data, created = self.admission_store.admit(
                    idempotency_key=idempotency_key, fingerprint=fingerprint,
                    receipt=asdict(receipt), approval_id=approval_id,
                    outbox_item={"outbox_id": canonical_hash({"key": idempotency_key, "kind": "action.dispatch"}),
                                 "payload": {"action": action, "target": target,
                                             "capability": capability, "actor": actor,
                                             "payload": payload_snapshot,
                                             "correlation_id": correlation_id,
                                             "request_fingerprint": fingerprint,
                                             "execution_mode": "simulated_only"}})
            except AdmissionConflict as exc:
                return None, {"allowed": False, "reason": str(exc),
                              "policy_decision_id": decision.decision_id}
            receipt = ExecutionReceipt(**stored_data)
            if not created:
                return receipt, {"allowed": True, "reason": "idempotent_replay",
                                 "policy_decision_id": receipt.policy_decision_id}
        self._receipts[idempotency_key] = receipt
        self._request_fingerprints[idempotency_key] = fingerprint
        self.evidence.append("execution.receipt", receipt.receipt_id, asdict(receipt))
        return receipt, asdict(decision)

    def verify_goal(self, goal_id: str, passed: bool, evidence_refs: list[str], verifier: str, criterion_results=None):
        """Verification is explicit and requires evidence references for a pass."""
        goal = self.goals.record_verification(goal_id, passed, evidence_refs, verifier, criterion_results)
        self.evidence.append("goal.verification", goal_id, asdict(goal))
        return goal

    def snapshot(self) -> dict[str, Any]:
        return {
            "version": "1.2.19",
            "state_records": self.state.count() if hasattr(self.state, "count") else len(self.state._records),
            "goals": len(self.goals.list()),
            "receipts": len(self._receipts),
            "evidence_entries": len(self.evidence.entries()),
            "evidence_chain_valid": self.evidence.verify(),
            "execution_mode": "simulated_only",
        }
