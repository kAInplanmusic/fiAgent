from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any
import hashlib, json, uuid

def _now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def _canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

@dataclass(frozen=True)
class ActionRequest:
    action: str
    target: str
    capability: str | None
    actor: str
    input_payload: dict[str, Any]
    correlation_id: str
    idempotency_key: str
    requested_at: str

    @classmethod
    def create(cls, action, target, capability, actor, input_payload,
               correlation_id=None, idempotency_key=None):
        if not action or not target or not actor:
            raise ValueError("action, target and actor are required")
        return cls(action, target, capability, actor, dict(input_payload),
                   correlation_id or str(uuid.uuid4()),
                   idempotency_key or str(uuid.uuid4()), _now())

@dataclass(frozen=True)
class PolicyDecision:
    decision_id: str
    allowed: bool
    reason: str
    policy_id: str | None
    evaluated_at: str
    action_request_hash: str

class PolicyGateway:
    """Deny-by-default exact-match policy evaluator; not a complete policy engine."""
    def __init__(self, rules=None):
        self._rules = list(rules or [])

    def evaluate(self, request, approval=None):
        request_hash = _canonical_hash(asdict(request))
        for rule in self._rules:
            if rule.get("action") != request.action:
                continue
            if rule.get("target", "*") not in ("*", request.target):
                continue
            pid, required = rule.get("policy_id"), rule.get("required_capability")
            if not pid or not required:
                return self._decision(False, "invalid_policy_rule", pid, request_hash)
            if request.capability != required:
                return self._decision(False, "missing_or_mismatched_capability", pid, request_hash)
            if rule.get("approval_required", False):
                if not approval:
                    return self._decision(False, "approval_required", pid, request_hash)
                expected = {
                    "action": request.action, "target": request.target,
                    "input_hash": _canonical_hash(request.input_payload),
                    "idempotency_key": request.idempotency_key
                }
                for key, value in expected.items():
                    if approval.get(key) != value:
                        return self._decision(False, f"approval_binding_mismatch:{key}", pid, request_hash)
                try:
                    expires = datetime.fromisoformat(approval["expires_at"].replace("Z", "+00:00"))
                    if expires <= datetime.now(timezone.utc):
                        return self._decision(False, "approval_expired", pid, request_hash)
                except (KeyError, AttributeError, ValueError):
                    return self._decision(False, "approval_expiry_invalid", pid, request_hash)
            return self._decision(True, "policy_match", pid, request_hash)
        return self._decision(False, "no_matching_policy", None, request_hash)

    @staticmethod
    def _decision(allowed, reason, policy_id, request_hash):
        return PolicyDecision(str(uuid.uuid4()), allowed, reason, policy_id, _now(), request_hash)
