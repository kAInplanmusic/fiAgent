# Phase 1 interface contracts — v1.2.16

| Contract | Current implementation | Verified invariant | Known limitation / architecture gap |
|---|---|---|---|
| Observation | `prain.runtime.Observation` | Source/kind non-empty; payload is an object | No complete semantic entity/claim graph, temporal validity or epistemic status |
| Event delivery | `prain.event_bus.EventBus`, `prain.durable_components` | Duplicate suppression and durable delivery state in configured SQLite mode | No production transport adapter; distributed scope and projection freshness incomplete |
| Evaluator registry | `PRAINRuntime.evaluators` | Unknown evaluator fails closed | Local callables; no semantic conflict evaluator workflow |
| State store | `prain.state_store.StateStore`, `prain.durable_state_store` | CAS rejects stale versions | No end-to-end distributed lease/fencing contract |
| Goal registry | `prain.goal_registry.GoalRegistry` | Completion requires passing verification and evidence refs | Criteria/dependency execution is not a full semantic goal graph |
| Policy gateway | `prain.policy_gateway.PolicyGateway` | Unmatched policy denies; capability/action/target checked | Approval issuer authentication and complete authoritative revocation not implemented |
| Execution / receipt | `prain.runtime`, `prain.dispatcher` | Simulated execution, idempotency and conservative unknown-outcome reconciliation | No real external action adapter; no global exactly-once guarantee |
| Evidence ledger | `prain.evidence_ledger.EvidenceLedger` | Append-only API and hash-chain verification; durable when configured | No signatures or external anchoring; model output is not evidence by itself |
| Backup bundle | `prain.backup_bundle` | Integrity-checked bundle and tested recovery paths | Writers must be quiesced; multi-file restore is not globally crash-atomic |
| SCF / semantic coordination | Specification only | No implementation claim | Routing, scope, conflicts, dependency invalidation and selective sync remain open |
| Anima self-model | Specification only | No implementation claim | Versioned self-model and continuity rules remain open |
| HAL | Specification only | No implementation claim | Observe-only signals and bounded repair/adaptation remain open |

## Vertical reference flow

`Observation → Event + evidence → named evaluator → PolicyDecision → simulated action → ExecutionReceipt → evidence chain`

Goal completion remains a separate explicit operation requiring verification and evidence. An allowed policy decision does not prove task success.

## Cross-cutting invariants

- Unknown evaluator or unmatched policy: fail closed.
- Authoritative writes use version/CAS checks; stale projections cannot overwrite source-of-truth records.
- Unknown external outcomes are reconciled before retry; lease expiry alone does not prove non-execution.
- Goal completion requires evidence for every required acceptance criterion.
- SCF/HAL, once implemented, must not bypass the policy gateway or invariant boundary.
- Phase 0 is not formally closed by this document.


## Step 31 contract draft

See `STEP31_CONTRACT_RECONCILIATION_AND_SEMANTIC_SCF_DRAFT.md`. The semantic entities and SCF recipient outcomes there are proposals for review, not executable interfaces.
