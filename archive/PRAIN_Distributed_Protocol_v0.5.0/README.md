# PRAIN Distributed Protocol — v0.5.0

**Purpose:** turn PRAIN's cluster-first architecture into explicit communication, consistency, recovery, and verification contracts.

PRAIN cannot guarantee perfect communication or global strong consistency across arbitrary distributed nodes, partitions, and failures. This package instead specifies where strong consistency is required, where eventual consistency is acceptable, and how uncertainty is represented and recovered.

## Core rule
**Never pretend an uncertain outcome is a known outcome.** Every command, state mutation, execution receipt, and verification result has an identity, version, provenance, and explicit status.

## Package contents
- `spec/CONSISTENCY_MODEL.md` — consistency classes and invariants
- `spec/MESSAGE_PROTOCOL.md` — message envelope and delivery semantics
- `spec/STATE_AND_CONFLICTS.md` — authoritative writes, CAS, conflict handling
- `spec/EXECUTION_AND_RECOVERY.md` — leases, retries, reconciliation, compensation
- `spec/CLUSTER_TOPOLOGY.md` — logical cores, worker pools, deployment stages
- `spec/CONFORMANCE_TESTS.md` — required failure and correctness tests
- `schemas/*.schema.json` — machine-readable JSON Schemas
- `plans/IMPLEMENTATION_PLAN.md` — implementation order and exit criteria
- `tests/reference_invariants.json` — machine-readable invariant list

## Non-goals
This is an architecture and protocol specification, not a claim that a running cluster has been deployed. It does not claim exactly-once execution, magical conflict-free global state, or quantum advantage.

## Design decisions
1. Strong consistency is scoped to authoritative records and operations that require it, not all data everywhere.
2. At-least-once delivery plus idempotent consumers is the baseline.
3. Every externally visible action has an idempotency key and a reconciliation strategy where possible.
4. An expired lease does not prove the previous worker did nothing.
5. Semantic indexes, embeddings, analytics, and read replicas may lag and must expose freshness/version metadata.
6. A goal is complete only after acceptance criteria are verified against evidence.
7. Policy authorization is evaluated at execution time and bound to the exact action parameters.
8. No single message broker is the source of truth for all business state; authoritative state is stored transactionally.

## Suggested first implementation
Start with a single deployable control service, PostgreSQL, and a durable event transport (for example NATS JetStream). Preserve interfaces so the transport or deployment topology can change. Add replicas and worker nodes only after conformance tests pass.
