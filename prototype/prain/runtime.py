"""Small, deterministic PRAIN reference runtime; external effects are simulated only."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import hmac
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
                 persistent_db_path: str | None = None, *,
                 trusted_local_prototype_mode: bool = False,
                 approval_verification_key: bytes | None = None):
        if type(trusted_local_prototype_mode) is not bool:
            raise TypeError("trusted_local_prototype_mode_must_be_boolean")
        self._trusted_local_prototype_mode = trusted_local_prototype_mode
        if approval_verification_key is not None and (not isinstance(approval_verification_key, bytes)
                                                      or len(approval_verification_key) < 32):
            raise ValueError("strong_approval_verification_key_required")
        self._approval_verification_key = approval_verification_key
        self.state = DurableStateStore(persistent_db_path) if persistent_db_path else StateStore()
        self.events = DurableEventBus(persistent_db_path) if persistent_db_path else EventBus()
        self.goals = DurableGoalRegistry(persistent_db_path) if persistent_db_path else GoalRegistry()
        self.policy = PolicyGateway(policies or [])
        self.evidence = DurableEvidenceLedger(persistent_db_path) if persistent_db_path else EvidenceLedger()
        # Local semantic coordination and self-observation; no authority granted.
        from .scf import SemanticFabric
        from .anima_hal import Anima, HAL
        if persistent_db_path:
            from .durable_semantics import DurableSemanticFabric, DurableAnima
            self.scf = DurableSemanticFabric(persistent_db_path)
            self.anima = DurableAnima("prain-local-runtime", persistent_db_path)
        else:
            self.scf = SemanticFabric()
            self.anima = Anima("prain-local-runtime")
        if persistent_db_path:
            from .tenant_access import TenantAccess
            from .private_projections import PrivateProjections
            self.tenant_access = TenantAccess(persistent_db_path)
            self.private_projections = PrivateProjections(persistent_db_path)
        else:
            self.tenant_access = None
            self.private_projections = None
        self.hal = HAL()
        from .hal_proposals import HALProposalController
        if persistent_db_path:
            from .durable_hal_proposals import DurableHALProposalController
            self.hal_proposals = DurableHALProposalController(persistent_db_path)
        else:
            self.hal_proposals = HALProposalController()
        if persistent_db_path:
            from .fenced_leases import FencedLeaseStore
            self.fencing = FencedLeaseStore(persistent_db_path)
            from .scf_delivery import SCFDeliveryQueue
            self.scf_delivery = SCFDeliveryQueue(persistent_db_path)
        else:
            self.fencing = None
            self.scf_delivery = None
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
        """Trusted local simulation only; services must use authenticated admission.

        The explicit constructor opt-in is for offline prototype fixtures. It is
        not an authentication mechanism or an authorization for external effects.
        """
        if not self._trusted_local_prototype_mode:
            raise PermissionError("authenticated_action_required")
        with self._action_lock:
            return self._request_action_locked(action, target, capability, actor, payload,
                                               correlation_id, idempotency_key, approval)

    def request_authenticated_action(self, *, tenant: str, principal: str, credential: str,
                                     action: str, target: str, capability: str,
                                     payload: dict[str, Any], correlation_id: str,
                                     idempotency_key: str, approval: dict[str, Any] | None = None):
        """Reauthorize identity and grants before admission, including replay.

        Components holding this runtime and its database are trusted Python code.
        Process-local serialization does not make revocation atomic with a remote
        external effect; adapters must enforce authority at their own boundary.
        """
        if self.tenant_access is None:
            raise PermissionError("persistent_authenticated_runtime_required")
        with self._action_lock:
            self.tenant_access.authorize(tenant, principal, credential, capability, target)
            # An approval is an authority grant, not a transferable bearer note.
            # The legacy local policy binding covers action/target/payload/key but
            # does not know the authenticated tenant and principal at this edge.
            if approval is not None and (not isinstance(approval, dict)
                                         or approval.get("tenant") != tenant
                                         or approval.get("principal") != principal):
                raise PermissionError("approval_identity_mismatch")
            if approval is not None:
                # Bind validation and admission to the same private snapshot.
                # A caller may otherwise mutate the dictionary after its MAC is
                # verified, before the policy engine consumes its fields.
                approval = deepcopy(approval)
                if approval.get("tenant") != tenant or approval.get("principal") != principal:
                    raise PermissionError("approval_identity_mismatch")
                signature = approval.get("issuer_signature")
                if self._approval_verification_key is None or not isinstance(signature, str):
                    raise PermissionError("verified_approval_issuer_required")
                if len(signature) != 64 or any(c not in "0123456789abcdef" for c in signature):
                    raise PermissionError("invalid_approval_issuer_signature")
                try:
                    approval_payload = {k: v for k, v in approval.items() if k != "issuer_signature"}
                    raw = json.dumps(approval_payload, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode("utf-8")
                except (TypeError, ValueError, OverflowError) as exc:
                    raise PermissionError("invalid_approval_payload") from exc
                expected = hmac.new(self._approval_verification_key,
                                    b"PRAIN-APPROVAL-v1\0" + raw, sha256).hexdigest()
                if not hmac.compare_digest(signature, expected):
                    raise PermissionError("invalid_approval_issuer_signature")
                # A signed client-supplied usage counter cannot establish a
                # cross-process limit. Single-use admission needs a shared durable
                # authority; higher limits are not implemented by that store.
                usage_policy = approval.get("usage_policy")
                max_uses = approval.get("max_uses")
                if usage_policy not in (None, "single_use"):
                    raise PermissionError("approval_usage_limit_not_supported")
                if max_uses is not None and (type(max_uses) is not int or max_uses != 1):
                    raise PermissionError("approval_usage_limit_not_supported")
                if max_uses == 1 and usage_policy != "single_use":
                    raise PermissionError("single_use_policy_required")
                if usage_policy == "single_use" and self.admission_store is None:
                    raise PermissionError("durable_approval_admission_required")
            # Structured identity avoids collisions such as ("a:b", "c") and
            # ("a", "b:c") sharing the same actor/fingerprint.
            actor = json.dumps({"tenant": tenant, "principal": principal},
                               sort_keys=True, separators=(",", ":"))
            return self._request_action_locked(action, target, capability, actor,
                                               payload, correlation_id, idempotency_key, approval,
                                               revalidate_replay=True)

    def _request_action_locked(self, action: str, target: str, capability: str | None,
                               actor: str, payload: dict[str, Any], correlation_id: str,
                               idempotency_key: str, approval: dict[str, Any] | None = None, *,
                               revalidate_replay: bool = False) -> tuple[ExecutionReceipt | None, dict[str, Any]]:
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
        def replay_authorized():
            if not revalidate_replay:
                return None
            current = self.policy.evaluate(request, approval=approval)
            self.evidence.append("policy.replay_reauthorization", current.decision_id, asdict(current))
            return None if current.allowed else asdict(current)
        if self.admission_store is not None:
            stored = self.admission_store.get_record(idempotency_key)
            if stored is not None:
                stored_fingerprint, stored_data = stored
                if stored_fingerprint != fingerprint:
                    return None, {"allowed": False, "reason": "idempotency_key_conflict",
                                  "policy_decision_id": stored_data.get("policy_decision_id", "durable-replay")}
                denial = replay_authorized()
                if denial is not None:
                    return None, denial
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
            denial = replay_authorized()
            if denial is not None:
                return None, denial
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
        raise PermissionError("verified_goal_completion_required")


    def secure_completion(self, authenticate):
        """Create the opt-in atomic evidence-verified durable completion facade.

        The caller's trust boundary must supply a real authenticator. Legacy
        verification methods remain available until callers are migrated.
        """
        from .secure_completion import SecureGoalCompletion
        return SecureGoalCompletion(self, authenticate)

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
