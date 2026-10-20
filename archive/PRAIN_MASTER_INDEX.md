# PRAIN — Master Project Index

**Status:** Consolidated archive/index for collaborative Phase 0 completion. This document does not declare Phase 0 closed.
**Scope:** All available PRAIN specification artifacts through v0.6, including the separate Phase 1 prototype for historical reference only.
**Implementation boundary:** Do not start runtime, framework, or OS implementation until Phase 0 has been reviewed and formally accepted.

## Canonical definition

P.R.A.I.N. = “quantum ready semantic Hamilton Interface & Orchestrator”.
- **P — Perception:** senses; normalize observations while retaining provenance and uncertainty.
- **R — Reason:** brain; interpret, infer, compare, plan.
- **A — Anima:** soul; explicit, inspectable, versioned self-model and continuity. Not a claim of consciousness and not the sole origin of identity.
- **I — Intention:** will; goals, priorities, dependencies, acceptance criteria.
- **N — Nerve:** body; execute authorized actions through capability adapters.

PRAIN is an independent semantic and structured framework for autonomous agents, not a generic knowledge base and not dependent on Hallerbans. P/R/A/I/N are logical responsibilities, not necessarily five separate agents/services. “Quantum-ready” means replaceable provider/compute interfaces; it does not imply quantum computing or quantum advantage.

## Artifact inventory and intended precedence

1. `PRAIN_Phase0_v0.2.1.zip` — baseline contracts: Event Registry, Goal Registry, versioned State Store/CAS, Policy Gateway, schemas and reference tests. SHA-256: `5b801aba53c152105525b5552cb803b6b72e233eec546c1b5e37bafc38f28d82`.
2. `PRAIN_Architecture_v0.4.0.zip` — architecture deepening: semantic model, P/R/A/I/N roles, identity/continuity, communication, goal/control loop, failure/recovery, observability, trust boundaries, traceability and decision register. SHA-256: `60de298ddcb130221b240056a805c018158c89675ebfa94049384a01e2f4052c`.
3. `PRAIN_Distributed_Protocol_v0.5.0.zip` — distributed coordination and consistency protocol, ambiguity-safe retries, inbox/outbox, CAS, leases/fencing, recovery and 18 conformance tests. SHA-256: `a78d29e0717fbcb17d0149808e59b6ece9daf81d87ad99bc8efae3b9bd634b5a`.
4. `PRAIN_v0.6.zip` — latest architecture deepening: multiscale semantic coordination, Semantic Coordination Fabric (SCF), Homeostasis & Adaptation Layer (HAL), Invariant & Evidence Layer, invariants, schemas, traceability and implementation plan. SHA-256: `ed8cb1a47b89b0d18b93336d8f807e33636ceeac00f8965c036ab3f2c8b7f652`.
5. `PRAIN_Wissensdatenbank.json` and `PRAIN_interaktive_Wissensdatenbank.html` — existing knowledge-base artifacts, preserve as source artifacts; reconcile their contents against the specifications rather than silently replacing them.
6. `PRAIN_Phase1_Prototype_v0.1.0.zip` — separate in-memory reference prototype (reported 15/15 tests passed); historical/prototype reference only. It is not proof that Phase 0 is complete and is not a mandate to implement runtime now.
7. `PRAIN_Phase0_v0.1.0.zip` and `PRAIN_Phase0_v0.2.0.zip` — earlier Phase 0 snapshots; retain for history and decision lineage.

**Precedence rule:** v0.6 is the newest architectural layer, but does not automatically erase or supersede earlier contracts. During consolidation, each prior requirement must be classified as retained, extended, explicitly superseded, or unresolved. Never silently drop a previous decision or code/schema fragment.

## Decisions already recorded in prior work (reconfirm during consolidation)

- Prefer UUIDv7 for opaque identifiers.
- Use UTC RFC3339 timestamps.
- Assume at-least-once delivery and idempotent consumers; do not promise global exactly-once delivery.
- Use versioning and `updated_at`/CAS for authoritative state changes.
- Keep append-only evidence ledger/hash-chain reference.
- Deny by default, least privilege, action-bound approvals; missing capability or policy means deny/defer.
- Include classification, retention, redaction, and deletion of derived indexes/caches.
- Use SemVer for schema versioning.
- Scope strong consistency to authoritative records; projections may be eventually consistent and must not overwrite authoritative state.
- Persist unknown execution outcomes and reconcile before retry; an expired lease does not prove that an action did not execute.
- A goal is completed only when evidence verifies every required acceptance criterion.
- NATS JetStream was suggested as a replaceable transport candidate; PostgreSQL as a transaction/state candidate. These are candidates, not implementation commitments.
- Identity is distributed across P/R/A/I/N; A maintains an explicit inspectable self-model but does not alone define identity.

## v0.6 architecture additions

- Multiscale structure: local units → cooperation groups → global semantic system → invariant/control boundary.
- SCF coordinates semantic messages, provenance, local projections, conflict detection, reconciliation and selective synchronization.
- HAL monitors system health, feedback, bounded adaptation and repair/evolution proposals; it is not a sixth P/R/A/I/N core dimension.
- Invariant & Evidence Layer protects authoritative state, rights, versioning, receipts and independent verification.
- Preserve global semantic coherence without requiring global synchronization for every operation.

## Phase 0 closure work still required

1. Build a source-to-requirement traceability matrix across every version and knowledge-base artifact.
2. Detect contradictions, duplicates, missing definitions and obsolete fragments.
3. Reconcile canonical terms, entity models, message envelopes, state transitions and schema version policy.
4. Finish interface contracts and complete pseudocode/reference flows for normal, failure, recovery, race and ambiguous-outcome cases.
5. Specify privacy, retention, redaction, deletion propagation and derived-data handling end to end.
6. Define negative tests, conformance criteria, invariants and measurable exit criteria.
7. Record all decisions with rationale, alternatives, status, impact and source version.
8. Produce a formal Phase 0 acceptance record only after user review and agreement.

## Status vocabulary

- **Retained:** previously specified and still valid.
- **Extended:** kept and expanded with explicit traceability.
- **Superseded:** replaced by a documented decision with rationale.
- **Open:** requires a decision or additional specification.
- **Acceptance-ready:** specified and checked against agreed criteria.
- **Implemented/verified:** reserved for later implementation phases; not implied by specification completeness.

## Working rule

Until the user explicitly approves the closure record, Phase 0 remains **in consolidation / not formally closed**. No runtime, framework, OS integration, deployment, or new implementation work is authorized by this index.
