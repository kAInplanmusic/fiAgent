# PRAIN Phase 1 — implementation start plan

## Objective
Build the smallest testable local reference implementation of the Phase-0 semantic control plane, not a production agent or deployment.

## Work packages (ordered)
1. **P1-01 — Runtime skeleton:** choose a typed implementation language and package layout; document the choice in an ADR before adding dependencies.
2. **P1-02 — Contract layer:** load/validate the 17 canonical JSON schemas; establish typed domain models and versioned serialization.
3. **P1-03 — State transition core:** implement claim lifecycle, policy decisions, approval lifecycle, execution/reconciliation, goal, repair and delegation transitions as pure functions where possible.
4. **P1-04 — Policy gate:** enforce principal/tenant/authority checks, approval binding, expiry/revocation, action digest matching and fail-closed defaults.
5. **P1-05 — Evidence and idempotency:** implement evidence references, stable command digest/idempotency keys, retry guards, compare-and-swap semantics and explicit unknown-outcome handling.
6. **P1-06 — P/R/A/I/N orchestration seam:** define typed boundaries for Perception, Reason, Anima (versioned/inspectable self-model), Intention and Nerve; keep them logical responsibilities, not mandatory separate services.
7. **P1-07 — Test harness:** schema contract tests, positive/negative transition tests, stateful integration tests and deterministic fixtures.
8. **P1-08 — Conformance report:** map every implemented invariant to tests; list deferred runtime obligations and known limitations.

## First vertical slice
Observation → normalized claim/evidence → goal → plan proposal → policy decision → approval check → action command (in-memory only) → execution receipt → evidence-backed state update.

## Acceptance gates
- Every action is rejected by default unless principal, tenant, policy and any required approval are valid for the exact action digest.
- Expired/revoked/consumed approvals and digest mismatches are rejected.
- A retry after a possibly executed action is prohibited until effect absence is established; unknown outcomes enter reconciliation rather than blind retry.
- Goal completion requires configured evidence; no inference from command submission alone.
- Tests are deterministic, local, documented, and report both positive and negative cases.
- All deviations from Phase-0 contracts require a recorded ADR and explicit review.

## Deferred
Production storage, distributed deployment, real connectors/providers, OS/browser actions, real external side effects, secrets management, security assessment, load testing, disaster recovery and production SLO claims.
