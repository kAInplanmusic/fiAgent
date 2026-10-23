# PRAIN architecture alignment — v1.2.16 / Step 31

## Decision

The current code is an executable Phase 1 reference prototype, not a completed implementation of the full PRAIN v0.6 architecture. Step 30 realigns the roadmap and evidence. It does not close Phase 0 and does not silently convert architectural aspirations into implemented capabilities.

## Canonical intent retained from the master archive through v0.6

- **P/R/A/I/N** means **Perception** (normalize observations with provenance and uncertainty), **Reason** (interpret, infer, compare and plan), **Anima** (explicit, inspectable, versioned self-model and continuity), **Intention** (goals, priorities, dependencies and acceptance criteria), and **Nerve** (authorized actions through capability adapters). These are logical responsibilities, not five mandatory services. Identity is distributed across all five; Anima is not the sole origin of identity.
- PRAIN is an independent semantic control plane, not a generic knowledge base and not dependent on Hallerbans.
- The four planes are semantic, coordination, execution, and invariant/evidence. They are orthogonal to P/R/A/I/N.
- Multiscale organization is L0 local unit → L1 cooperation group → L2 global semantic system → L3 invariant/control boundary.
- **SCF** coordinates scoped semantic messages, provenance, projection freshness, dependency invalidation, conflict classification, reconciliation, selective synchronization, replay and dead-letter handling.
- **HAL** monitors feedback and health, proposes bounded adaptation, and begins observe-only. HAL is not a sixth core dimension and cannot authorize actions or bypass policy.
- The **Invariant & Evidence Layer** remains the authority for permissions, authoritative versions, resource limits, receipts and independently verified goal completion.

## Current prototype boundary

Implemented foundations include typed observations, evaluator registration, deny-by-default policy decisions, simulated actions, idempotency/receipt replay, evidence-backed goal verification, CAS state, SQLite-backed durable components, an outbox/dispatcher reference path, conservative unknown-outcome handling, and backup/recovery tests.

Not established by the current prototype: full semantic claim/relationship graph with temporal validity and uncertainty semantics; complete SCF routing and conflict reconciliation; the L0–L3 coordination model; a versioned Anima self-model; HAL health signals, stability controls or bounded repair; production authentication/authorization; real external action adapters; distributed transport or multi-group partition recovery; end-to-end retention/deletion propagation; production deployment guarantees.

## Governing design constraints

1. Preserve at-least-once delivery with idempotent consumers; never claim global exactly-once effects.
2. Unknown external outcomes remain unknown until reconciled with evidence; lease expiry alone does not prove non-execution.
3. Authoritative state uses versions/CAS. Projections and caches are non-authoritative and may never overwrite their source of truth.
4. Missing policy/capability defaults to deny or defer. HAL and model output cannot grant authority.
5. A goal is complete only when evidence verifies every required acceptance criterion.
6. Schema changes use explicit versions and migration/conformance tests.
7. Every requirement must be classified as retained, extended, superseded with rationale, or open. No silent removal.
8. Phase 0 remains open until a human accepts the traceability, contract, privacy, conformance and decision closure package.

## Next implementation order

1. Close architecture/contract traceability and resolve open decisions before adding more runtime scope.
2. Define canonical semantic entities and a versioned message envelope with provenance, epistemic status, scope, freshness, lineage and dependency tags.
3. Implement SCF behavior as a modular monolith first: recipient decisions (`adopt`, `retain_as_hypothesis`, `recompute`, `request_evidence`, `raise_conflict`, `ignore_out_of_scope`, `defer`) must be reasoned and recorded.
4. Add the versioned Anima self-model and cross-dimension identity/lineage rules.
5. Implement HAL observe-only signals, then bounded repair proposals with cooldowns, budgets, policy checks and rollback evidence.
6. Add conformance tests for conflicts, stale projections, scope, duplicate/reordered delivery, unknown action outcomes, deletion propagation and adaptation oscillation.
7. Consider external infrastructure only when benchmarks or conformance needs justify it. PostgreSQL and NATS JetStream remain replaceable candidates, not commitments.

## Release gate

This alignment document is not Phase 0 acceptance. No runtime capability is marked implemented solely because it appears in this roadmap. The requirements matrix is a gap analysis based on the available master index, v0.6 architecture files and current prototype documentation; detailed line-by-line reconciliation of every embedded historical artifact remains open.
