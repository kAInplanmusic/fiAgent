"""Deterministic policy-constrained routing reference, with no model/network calls.

The caller must supply a trusted security context; this is NOT authentication.
"""
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class RouteContext:
    tenant: str
    classification: str
    permitted_regions: frozenset[str]
    permitted_providers: frozenset[str]
    budget_ceiling: float
    policy_version: str


@dataclass(frozen=True)
class Backend:
    name: str
    provider: str
    region: str
    classifications: frozenset[str]
    capabilities: frozenset[str]
    estimated_cost: float
    quality_score: float
    external: bool = True


@dataclass(frozen=True)
class RouteDecision:
    allowed: bool
    backend: str | None
    reason: str
    eligible_count: int


def route(task: str, context: RouteContext, backends: Iterable[Backend]) -> RouteDecision:
    """Fail closed on invalid context; rank ONLY policy-eligible backends.

    No caller-provided prompt can expand the trusted policy context.
    """
    if (not task or not context.tenant or not context.policy_version
            or context.classification not in {'public', 'internal', 'confidential'}
            or not context.permitted_regions or not context.permitted_providers
            or context.budget_ceiling < 0):
        return RouteDecision(False, None, 'invalid_security_context', 0)
    eligible = []
    for backend in backends:
        if (backend.provider not in context.permitted_providers
                or backend.region not in context.permitted_regions
                or context.classification not in backend.classifications
                or task not in backend.capabilities
                or backend.estimated_cost < 0
                or backend.estimated_cost > context.budget_ceiling
                or not 0 <= backend.quality_score <= 1
                or (context.classification == 'confidential' and backend.external)):
            continue
        eligible.append(backend)
    if not eligible:
        return RouteDecision(False, None, 'no_policy_eligible_backend', 0)
    eligible.sort(key=lambda b: (-b.quality_score, b.estimated_cost, b.name))
    return RouteDecision(True, eligible[0].name, 'policy_eligible_ranked', len(eligible))
