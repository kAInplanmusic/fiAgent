# Phase 1 interface contracts — v1.1.1

| Contract | Implementation | Invariant | Limitation |
|---|---|---|---|
| Observation | `prain.runtime.Observation` | source/kind non-empty; payload is an object | In-memory only |
| Event bus | `prain.event_bus.EventBus` | duplicate event IDs suppressed per consumer | Not durable; no exactly-once effects |
| Evaluator registry | `PRAINRuntime.evaluators` | unknown evaluator fails closed | Local callables only |
| State store | `prain.state_store.StateStore` | optimistic CAS rejects stale versions | Single process |
| Goal registry | `prain.goal_registry.GoalRegistry` | completion requires passing verification and evidence refs | Acceptance criteria not intrinsically executable |
| Policy gateway | `prain.policy_gateway.PolicyGateway` | no matching rule denies | Approval issuer not authenticated |
| Execution receipt | `prain.runtime.ExecutionReceipt` | created only after allowed policy decision | Execution is simulated only |
| Evidence ledger | `prain.evidence_ledger.EvidenceLedger` | append-only API; hash chain verifies | No persistence, signature or external anchor |

## Vertical flow

`Observation -> Event + evidence -> named evaluator -> PolicyDecision -> simulated action -> ExecutionReceipt -> evidence chain`

Goal completion is a separate explicit operation and requires verification plus at least one evidence reference. The runtime intentionally does not infer that a policy-allowed action proves a goal.

## Action policy

Rules are exact-match for action and target (or `*`) and require a `policy_id` plus `required_capability`. Approval-required rules bind action, target, canonical payload hash, idempotency key and expiry. Approval authenticity and atomic single-use consumption are not implemented.

## Event semantics

Per-consumer duplicate suppression is process-local. Handler failures are surfaced and not automatically retried because a handler may have performed an effect before raising.
