"""Versioned, scoped semantic coordination reference implementation (local only)."""
from __future__ import annotations
from dataclasses import dataclass, field
from copy import deepcopy
from datetime import datetime, timezone
from threading import RLock
from typing import Any

DECISIONS = frozenset({"adopt", "retain_as_hypothesis", "recompute", "request_evidence",
                       "raise_conflict", "ignore_out_of_scope", "defer"})


def _timestamp(value: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError("UTC timestamp required")
    try:
        d = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as e:
        raise ValueError("invalid timestamp") from e
    if d.tzinfo is None or d.utcoffset() != timezone.utc.utcoffset(d):
        raise ValueError("timestamp must be UTC")
    return d


@dataclass(frozen=True)
class SemanticClaim:
    claim_id: str
    subject: str
    predicate: str
    value: Any
    scope: str
    source: str
    evidence_refs: tuple[str, ...]
    observed_at: str
    valid_until: str
    confidence: float
    version: int = 1
    dependencies: tuple[str, ...] = ()
    epistemic_status: str = "observed"

    def __post_init__(self):
        for key in ("claim_id", "subject", "predicate", "scope", "source"):
            if not isinstance(getattr(self, key), str) or not getattr(self, key).strip():
                raise ValueError(key + " required")
        if type(self.version) is not int or self.version < 1:
            raise ValueError("positive integer version required")
        if type(self.confidence) is not float or not 0 <= self.confidence <= 1:
            raise ValueError("invalid confidence")
        if self.epistemic_status not in {"observed", "inferred", "hypothesis"}:
            raise ValueError("invalid epistemic status")
        if not isinstance(self.evidence_refs, tuple) or any(not isinstance(x, str) or not x for x in self.evidence_refs):
            raise ValueError("invalid evidence references")
        if not isinstance(self.dependencies, tuple) or any(not isinstance(x, str) or not x for x in self.dependencies):
            raise ValueError("invalid dependencies")
        if _timestamp(self.valid_until) <= _timestamp(self.observed_at):
            raise ValueError("invalid validity interval")


@dataclass(frozen=True)
class SCFDecision:
    claim_id: str
    decision: str
    reason: str
    scope: str


class SemanticFabric:
    """In-process non-authoritative claim projections with explicit conflict decisions.

    No delivery or distributed transport guarantees. Source version gaps are
    deferred; conflicting authoritative claims are not silently overwritten.
    """

    def __init__(self):
        self._lock = RLock()
        self._claims: dict[str, SemanticClaim] = {}
        self._conflicts: list[dict[str, str]] = []
        self._decisions: list[SCFDecision] = []
        self._invalidated: set[str] = set()

    def ingest(self, claim: SemanticClaim, recipient_scope: str, now: str) -> SCFDecision:
        if not isinstance(claim, SemanticClaim):
            raise TypeError("claim must be SemanticClaim")
        t = _timestamp(now)
        if not isinstance(recipient_scope, str) or not recipient_scope:
            raise ValueError("recipient scope required")
        with self._lock:
            prior = self._claims.get(claim.claim_id)
            if recipient_scope != claim.scope:
                action, reason = "ignore_out_of_scope", "scope_mismatch"
            elif t >= _timestamp(claim.valid_until):
                action, reason = "recompute", "expired_claim"
            elif _timestamp(claim.observed_at) > t:
                action, reason = "defer", "future_observation"
            elif not claim.evidence_refs:
                action, reason = "request_evidence", "missing_evidence"
            elif prior and claim.version <= prior.version:
                action, reason = ("defer", "duplicate_or_stale_version") if claim.version < prior.version else ("defer", "duplicate_version")
            elif prior and claim.version != prior.version + 1:
                action, reason = "defer", "version_gap"
            elif prior and (claim.subject, claim.predicate, claim.scope) != (prior.subject, prior.predicate, prior.scope):
                action, reason = "raise_conflict", "identity_mismatch"
                self._conflicts.append({"claim_id": claim.claim_id, "reason": reason})
            elif claim.epistemic_status == "hypothesis":
                action, reason = "retain_as_hypothesis", "non_authoritative"
                self._claims[claim.claim_id] = deepcopy(claim)
            else:
                action, reason = "adopt", "version_and_scope_valid"
                self._claims[claim.claim_id] = deepcopy(claim)
                if prior is not None:
                    for other_id, other in self._claims.items():
                        if claim.claim_id in other.dependencies:
                            self._invalidated.add(other_id)
            decision = SCFDecision(claim.claim_id, action, reason, recipient_scope)
            self._decisions.append(decision)
            return decision

    def projection(self, claim_id: str):
        with self._lock:
            if claim_id in self._invalidated:
                raise ValueError("projection_invalidated")
            return deepcopy(self._claims.get(claim_id))

    def decisions(self):
        with self._lock:
            return list(self._decisions)

    def conflicts(self):
        with self._lock:
            return deepcopy(self._conflicts)
