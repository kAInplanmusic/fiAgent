"""Versioned inspectable Anima self-model and observe-only HAL reference."""
from __future__ import annotations
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from threading import RLock


class AnimaConflict(ValueError):
    pass


def _contains_authority_field(value, seen=None):
    """Reject authority-like keys at any depth of a self-description."""
    forbidden = {"grant", "capabilities", "approval", "policy_override"}
    if not isinstance(value, (dict, list, tuple)):
        return False
    if seen is None:
        seen = set()
    if id(value) in seen:
        return False
    seen.add(id(value))
    if isinstance(value, dict):
        return any(str(key).lower() in forbidden or _contains_authority_field(item, seen)
                   for key, item in value.items())
    return any(_contains_authority_field(item, seen) for item in value)


@dataclass(frozen=True)
class SelfModel:
    identity_id: str
    version: int
    dimensions: dict
    provenance: str


class Anima:
    """Versioned self-description. It cannot grant capabilities or execute actions."""
    DIMENSIONS = frozenset({"perception", "reason", "anima", "intention", "nerve"})

    def __init__(self, identity_id: str):
        if not isinstance(identity_id, str) or not identity_id.strip():
            raise ValueError("identity required")
        self._lock = RLock()
        self._model = SelfModel(identity_id, 0, {}, "initial")

    def snapshot(self):
        with self._lock:
            m = self._model
            return SelfModel(m.identity_id, m.version, deepcopy(m.dimensions), m.provenance)

    def update(self, *, expected_version: int, dimension: str, state: dict, provenance: str):
        if dimension not in self.DIMENSIONS:
            raise ValueError("unknown dimension")
        if not isinstance(state, dict) or not isinstance(provenance, str) or not provenance.strip():
            raise ValueError("state and provenance required")
        if _contains_authority_field(state):
            raise AnimaConflict("self_model_cannot_grant_authority")
        with self._lock:
            old = self._model
            if type(expected_version) is not int or expected_version != old.version:
                raise AnimaConflict("stale_self_model_version")
            dimensions = deepcopy(old.dimensions)
            dimensions[dimension] = deepcopy(state)
            self._model = SelfModel(old.identity_id, old.version + 1, dimensions, provenance)
            return self.snapshot()


@dataclass(frozen=True)
class HealthObservation:
    component: str
    healthy: bool
    observed_at: str
    evidence: str


@dataclass(frozen=True)
class HALAssessment:
    component: str
    health: str
    action: str
    reason: str


class HAL:
    """Fail-closed observer. No automatic repair, mutation, or authorization."""
    def __init__(self, max_age_seconds: int = 300):
        if type(max_age_seconds) is not int or max_age_seconds <= 0:
            raise ValueError("positive integer age required")
        self.max_age_seconds = max_age_seconds
        self._assessments = []
        self._lock = RLock()

    def assess(self, item: HealthObservation, now: datetime) -> HALAssessment:
        if not isinstance(item, HealthObservation) or not isinstance(item.component, str) or not item.component:
            raise ValueError("invalid health observation")
        if not isinstance(item.healthy, bool) or not isinstance(item.evidence, str):
            raise ValueError("invalid health signal")
        if not isinstance(now, datetime) or now.tzinfo is None:
            raise ValueError("aware clock required")
        try:
            observed = datetime.fromisoformat(item.observed_at.replace("Z", "+00:00"))
        except (ValueError, AttributeError) as exc:
            raise ValueError("invalid observed_at") from exc
        if observed.tzinfo is None:
            raise ValueError("aware observation timestamp required")
        age = (now.astimezone(timezone.utc) - observed.astimezone(timezone.utc)).total_seconds()
        if age < 0 or age > self.max_age_seconds:
            health, reason = "unknown", "stale_or_future_observation"
        elif not item.evidence.strip():
            health, reason = "unknown", "missing_evidence"
        else:
            health, reason = ("healthy", "reported_healthy") if item.healthy else ("unhealthy", "reported_unhealthy")
        result = HALAssessment(item.component, health, "observe_only", reason)
        with self._lock:
            self._assessments.append(result)
        return result

    def history(self):
        with self._lock:
            return list(self._assessments)
