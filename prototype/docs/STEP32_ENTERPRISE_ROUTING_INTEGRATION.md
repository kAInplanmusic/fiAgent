# Step 32 — Enterprise routing, DAG and agent cluster integration contract

**Status:** design and acceptance backlog, NOT an implemented gateway, Hamilton driver, Burr state machine, or multi-model cluster. **Release:** v1.2.17 / Step 32.

## Non-negotiable architecture
PRAIN P/R/A/I/N remains the semantic control plane. The AI Gateway, Semantic Router, Hamilton DAG, Burr state machine and MMAC are optional interchangeable execution infrastructure under Nerve and policy governance; HAL remains bounded observe/repair, not a sixth PRAIN core.

## Ordered request lifecycle
1. Authenticate principal and tenant; establish immutable request scope, data classification, consent/retention and budget.
2. Authorize cache access BEFORE lookup. Cache keys include tenant, scope, principal/capability policy version, prompt normalization version, model/task version, classification and expiry. Never share sensitive answers across security contexts.
3. On miss, extract typed signals (keyword, embedding, domain, fact-check requirement, user feedback, preferences) and uncertainty; policy first constrains eligible backends and regions, router optimizes ONLY within permitted choices. No backend is a valid deny/defer outcome.
4. Persist selected route, evidence, rationale, model/config version, budget reservation and correlation ID.
5. Resolve a versioned, prevalidated Hamilton DAG template (not arbitrary untrusted runtime Python). Validate DAG inputs, dependencies, side effects and timeouts. Burr may manage durable loop state; do not mistake a DAG for an iterative state machine.
6. Dispatch bounded jobs to authenticated capability-limited agents through Nerve. Treat external side effects with idempotency keys, outbox and outcome-unknown reconciliation; do not retry ambiguous outcomes blindly.
7. Verify outputs with domain-specific acceptance evidence and policy checks. A hallucination classifier alone is not proof of factual correctness.
8. Redact/classify result, write evidence/lineage, and cache only when authorized with invalidation dependencies. Return receipt and observability metadata.

## Consistency and failure contracts
- Authoritative policy, approval, goal versions, budget reservations and action outcomes require version checks/CAS; derived cache/index may be eventual but cannot authorize actions.
- No cross-tenant cache hit, data egress, fallback to disallowed cloud, or model escalation beyond policy/budget.
- Unknown execution outcome remains durable; failover may change compute provider only when it cannot duplicate a side effect.
- Distributed delivery is at-least-once with idempotent consumers, never globally exactly-once.
- Circuit breaker, deadline, backpressure and bounded retry are required before production deployment.
- Each semantic claim carries provenance, validity interval, uncertainty and dependencies; deletion/redaction propagates to derived caches and embeddings.

## Report claim validation
The supplied report's percentages (45–85% cost, up to 47% latency) are hypotheses requiring PRAIN-specific reproducible benchmarks; no guaranteed savings. Routing cannot guarantee legal compliance without verified identity, data classification, egress controls and operational policy. Hamilton's naming/dependency graph does not automatically provide runtime audit or quantum capability. Quantum-ready here means provider-neutral execution interfaces; physical QPU support is out of Phase 1 unless separately specified.

## Phase 1 acceptance scenarios
R1 deny cache read when tenant/policy differs; R2 stale/revoked policy invalidates cached result; R3 confidential payload never routes externally; R4 no permitted backend returns deny/defer; R5 routing fallback respects budget and region; R6 Hamilton DAG dependency and cycle validation; R7 Burr resume replays no external action; R8 duplicate deliveries preserve one logical action; R9 outcome-unknown blocks unsafe retry; R10 evidence and model-version lineage attached to every accepted result; R11 redaction/deletion invalidates dependent cache; R12 competing state versions cannot overwrite authoritative records; R13 degraded model produces quality-aware refusal; R14 benchmarks compare fixed task mix against single-model baseline.

## Workstream tickets (ready to assign)
- P1-ARCH-01: reconcile historical sources line-by-line, disposition each requirement and get Phase 0 acceptance decision. Owner: Architecture. Gate: traceability coverage 100% with source locators.
- P1-SEM-01: implement typed claim/relationship/provenance/temporal semantic store. Owner: Semantic. Gate: schema and conflict/freshness tests.
- P1-SCF-01: implement scope-aware messages, durable conflict registry, recipient decisions, invalidation. Owner: Coordination. Gate: replay/partition/race tests.
- P1-GOV-01: authenticated principals, approval revocation, privacy and retention propagation. Owner: Governance. Gate: negative security tests.
- P1-ROUTE-01: policy-constrained router + isolated cache + budget reservation. Owner: Routing. Gate: R1–R5 and R11.
- P1-DAG-01: versioned DAG adapter; optionally Hamilton/Burr behind interfaces. Owner: Orchestration. Gate: R6–R9.
- P1-MMAC-01: agent capability/compute provider abstraction, local and mock backends. Owner: Execution. Gate: failover and bounded side-effect tests.
- P1-ANIMA-01: inspectable versioned self-model with identity continuity. Owner: Anima. Gate: lineage and version tests.
- P1-HAL-01: observe-only health, bounded repair proposal, cooldown/hysteresis. Owner: Adaptation. Gate: no autonomous policy bypass.
- P1-QA-01: independent acceptance suite and reproducible release gate. Owner: QA. Gate: R1–R14 plus full historical conformance.

## Release policy
A green unit-test suite means the implemented scope passes, not that Phase 1 is complete. Until all required workstreams and human architecture acceptance are verified, release gate remains PARTIAL_PASS. No invented subagent runs or benchmarks.
