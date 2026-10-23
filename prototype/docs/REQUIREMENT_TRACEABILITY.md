# Requirement traceability — architecture baseline through v0.6

**Release:** v1.2.16 / Step 30  
**Audit status:** `PARTIAL_PASS`  
**Phase 0:** not formally accepted/closed  
**Meaning:** This is a practical source-to-capability crosswalk, not a claim that every historical source line has been reconciled.

Statuses: **Implemented/verified** means current code and a test provide evidence for the stated narrow capability; **Partial** means only a subset exists; **Open** means a required capability is not present or not evidenced; **Decision/open** means a human decision or fuller source reconciliation is still required.

| Source / requirement | Intended invariant or capability | Current evidence | Status / next action |
|---|---|---|---|
| Phase 0 v0.2.1 — Event Registry | Typed events and duplicate handling | `prain/event_bus.py`, durable component tests | Partial: full schema/version contract and cross-process semantics need reconciliation |
| Phase 0 v0.2.1 — Goal Registry | Goal lifecycle; completion requires verification/evidence | `prain/goal_registry.py`, runtime and durable tests | Partial: criteria execution/dependency semantics are not fully modeled |
| Phase 0 v0.2.1 — State Store/CAS | Versioned authoritative updates reject stale writers | `prain/state_store.py`, `prain/durable_state_store.py`, CAS tests | Implemented/verified for current reference-store scope; distributed authority contract remains open |
| Phase 0 v0.2.1 — Policy Gateway | Deny by default; least privilege; approval bound to action | `prain/policy_gateway.py`, negative policy tests | Partial: approval issuer authentication and authoritative revocation remain open |
| Architecture v0.4 — semantic model/provenance | Typed entities/claims, source attribution, uncertainty and lineage | Observation envelope and evidence chain | Partial: canonical semantic graph, temporal validity and epistemic status remain open |
| Architecture v0.4 — P/R/A/I/N and identity | Logical responsibilities; versioned self-model; continuity | README and architecture contracts only | Open: no integrated versioned Anima/self-model is implemented |
| Architecture v0.4 — goal/control loop | Observe → reason → plan → authorize → act → verify | Runtime vertical slice and simulated action tests | Partial: limited evaluators and simulated execution only |
| Distributed Protocol v0.5 — at-least-once/idempotency | Safe duplicate delivery; no global exactly-once claim | Durable admission, dispatcher, receipt replay and crash tests | Partial: local SQLite reference path only; no production transport adapter |
| Distributed Protocol v0.5 — inbox/outbox/reconciliation | Unknown outcome is reconciled before retry | `prain/durable_admission.py`, `prain/dispatcher.py`, tests | Partial: process-local callback path and external effects remain simulated |
| Distributed Protocol v0.5 — leases/fencing | Stale workers cannot commit authoritative state | CAS and process tests | Open/partial: full lease/fencing contract is not implemented end-to-end |
| v0.6 — four architectural planes | Semantic, coordination, execution, invariant/evidence | Current code covers slices of execution and invariant/evidence | Partial: no explicit complete plane contracts or conformance report |
| v0.6 — L0/L1/L2/L3 multiscale model | Local autonomy with global invariant boundary | Specification only | Open: group/global coordination not implemented |
| v0.6 — SCF message envelope | Scope, provenance, freshness, lineage and dependencies | Event envelope is narrower | Open: define schema and compatibility/migration rules; implement routing and projection freshness |
| v0.6 — SCF conflict handling | Adopt/hypothesis/recompute/evidence/conflict/defer decisions | No complete conflict registry/workflow | Open: define and test all recipient decisions and reason records |
| v0.6 — HAL observe-only first | Health signals, bounded proposals, no policy bypass | No HAL implementation established | Open: specify signal schema, freshness and false-health rules before implementation |
| v0.6 — bounded adaptation | Cooldowns, budgets, canary/rollback, anti-oscillation | Recovery primitives only | Open: add adaptation proposals and oscillation/fault-injection conformance tests |
| Invariant & Evidence Layer | Authoritative records, policy, receipts, independent verification | Policy gateway, evidence ledger, goal verification | Partial: evidence chain is not signed or externally anchored; trust/auth boundaries remain incomplete |
| Privacy and lifecycle | Classification, retention, redaction, deletion propagation to derived data | No complete end-to-end implementation evidence | Open: define ownership, retention and deletion contract before derived indexes/caches |
| Release/quality gates | Reproducible test result, artifact identity, requirements coverage | `MANIFEST.json`, release verifier and test suite | Partial: docs now versioned consistently; full historical source-line reconciliation still open |

## Explicitly retained decisions

- UUIDv7 preferred for opaque IDs; UTC RFC3339 timestamps.
- At-least-once delivery and idempotent consumers; do not promise global exactly-once delivery.
- CAS/versioning for authoritative state; eventual consistency only for non-authoritative projections.
- Deny by default, least privilege, action-bound approvals.
- Persist ambiguous outcomes and reconcile before retry.
- Evidence must verify each required goal acceptance criterion.
- PostgreSQL and NATS JetStream are candidates behind replaceable interfaces, not implementation commitments.
- Identity is distributed across P/R/A/I/N; Anima is an inspectable self-model, not a consciousness claim or sole identity source.

## Open closure items

1. Perform line-by-line reconciliation of all Phase 0, v0.4, v0.5, v0.6, knowledge-base JSON/HTML and historical decision artifacts.
2. Resolve contradictions and record retained/extended/superseded/open with rationale.
3. Freeze canonical semantic entities, message envelope, state transitions and schema migration policy.
4. Complete privacy/retention/redaction/deletion propagation requirements.
5. Publish conformance tests and measurable Phase 0 exit criteria.
6. Obtain explicit human acceptance; until then, Phase 0 stays open.


## Step 31 audit extension

Step 31 formalizes disposition vocabulary and the source precedence model. It does not satisfy the still-open line-by-line reconciliation of every archived spec and knowledge-base artifact. The Phase 1 prototype existing before formal Phase 0 acceptance is recorded as a governance deviation requiring an explicit human decision, not as retroactive closure. See `STEP31_CONTRACT_RECONCILIATION_AND_SEMANTIC_SCF_DRAFT.md`.
