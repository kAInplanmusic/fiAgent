# PRAIN Phase-0 Closure and Phase-1 Authorization Attestation

- Release package: PRAIN v1.0.0 — Phase-0 Closure / Phase-1 Start Gate
- Specification baseline: PRAIN v0.99.4
- Decision source: explicit user instruction in this conversation on 2026-10-20 to finish all outstanding work required for Phase 1 to start, followed by repeated direction to execute those changes.
- Decision timestamp: 2026-10-20 (Europe/Berlin; exact minute intentionally not asserted by the package).
- Phase-0 decision: `APPROVE_PHASE0_CLOSURE`
- Phase-1 decision: `AUTHORIZE_PHASE1_IMPLEMENTATION` (bounded scope below)
- Exceptions: offline specification tests do not certify runtime behavior, production readiness, security, legal compliance, or external truth.

## Phase-1 authorized scope

1. Implement a minimal, runtime-agnostic reference prototype for the PRAIN semantic control plane, preserving the P/R/A/I/N responsibility model.
2. Implement typed interfaces and in-memory reference adapters for observations, claims/beliefs, goals, plans, policy decisions, approvals, action commands, execution receipts, evidence and state updates.
3. Implement deterministic state transitions and fail-closed policy/approval checks from the Phase-0 contracts.
4. Build unit, contract, negative, and integration tests; add reproducible local test commands and test fixtures.
5. Produce an architecture decision record for any deviation from the Phase-0 contracts and keep changes traceable.

## Explicit exclusions

- No production deployment or autonomous operation against real external systems.
- No operating-system control, browser automation, real-world side effects, paid API calls, or secrets handling without a separate scoped authorization.
- No claim of quantum computing advantage; “quantum-ready” remains provider/compute-interface replaceability.
- No relaxation of authorization, approval, evidence, idempotency, reconciliation, privacy, or deletion constraints to make tests pass.

## Phase-1 exit criteria

- Prototype compiles/runs locally with documented prerequisites.
- Contract tests cover every implemented canonical schema and all applicable state-machine guards.
- Negative tests demonstrate fail-closed behavior for expired/consumed approvals, revoked authority, digest mismatch, unknown external outcome, and missing evidence.
- Reproducible test suite passes; test report and known gaps are committed with the artifact.
- No production-readiness claim until runtime, security, resilience and deployment tests are independently completed.

## Attestation boundary

This document records the user's explicit instruction as authorization to close Phase 0 and begin the bounded Phase-1 prototype. It does not assert that Phase-1 implementation has already been built. The archived Phase-0 gate and validator reports remain historical records of the v0.99.4 candidate state; `release_status.json` is the authoritative release-level decision record for this package.
