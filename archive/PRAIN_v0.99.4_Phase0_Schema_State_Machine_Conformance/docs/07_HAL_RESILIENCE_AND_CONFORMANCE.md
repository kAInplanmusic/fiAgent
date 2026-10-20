# 7. HAL, recovery, resilience, SLOs and conformance

## 7.1 HAL’s role

Homeostasis & Adaptation Layer (HAL) is a supervisory feedback layer, not a sixth P/R/A/I/N dimension, independent policy authority, identity authority or self-approval mechanism. It observes health/failure signals, diagnoses, prepares bounded repair proposals, monitors effects, and recommends rollback/escalation. It cannot change hard ceilings, grant capabilities, weaken the policy gateway, disable evidence, erase history or rewrite live policy.

## 7.2 Allowed automatic repair catalogue

Automatic repair is permissible only when all conditions are met: the repair class is pre-approved in a versioned catalogue; target/scope and maximum attempts/duration/cost are bounded; the action is idempotent or affects rebuildable derived state; authorization is current; success metrics and rollback conditions are explicit; the health signal is fresh; and evidence is recorded.

| Repair class | Automatic by default? | Conditions |
|---|---|---|
| Rebuild derived projection/search/vector index | Yes, bounded | Read from authoritative sources; never write projection output back to authority; deletion tombstones applied first |
| Reindex derived memory | Yes, bounded | Preserve source revisions, tenant partitioning and deletion propagation; validate counts/digests |
| Retry idempotent read | Yes, bounded | Deadline/retry budget respected; no external side effect |
| Restart quiescent worker | Conditional | Fencing/lease epoch increments; confirm no unresolved in-flight side effect; unknown outcomes reconciled first |
| Route around failed read-only provider | Conditional | Policy permits; source freshness/quality recorded; no bypass of tenant or data-residency constraints |
| Increase retries, timeouts or resource use beyond catalogue bounds | No | Explicit policy change/human authorization required |
| Schema/data migration | No | Review, backup/rollback, compatibility tests and policy approval required |
| Policy bundle or authorization rule change | Forbidden to HAL self-authorize | Independent policy release/change control; two-person review for high-impact controls |
| Credential/key changes | No automatic self-approval | Independent secret/key authority and security procedure |
| Authoritative state correction/delete | No, except explicit deletion workflow | Auditable authorization, CAS, lifecycle rules and evidence |
| External irreversible side effect | No by default | Explicit action-bound policy and human approval as risk classification requires |
| Disable audit, change hard limits, increase own privilege, erase evidence, approve own proposal | **Never permitted** | Invariant violation; block and emit security event |

## 7.3 Repair proposal lifecycle

`proposed → approved → executing → succeeded | rolled_back | failed | expired` with `rejected` as terminal. Approval is provided by the independent policy gateway (plus human approval where required). Proposal expiry, changed observation/source revision, policy revocation, changed target, exceeded bounds or changed action digest invalidates approval. HAL cannot mark a proposal approved itself.

Every repair includes: trigger observations/evidence, target and tenant, versioned repair class, bounded scope/attempts/duration/cost, canary/rollout strategy, success metrics with thresholds, rollback conditions, recovery owner, expires-at time and policy-decision reference. Outcome verification reads authoritative state rather than relying only on the repairing worker’s self-report.

## 7.4 Failure/recovery matrix

| Failure | Required protocol response | Must not happen |
|---|---|---|
| Duplicate delivery | Inbox/dedup on stable message/idempotency key; return prior status for same digest | Repeat external effect |
| Same idempotency key with different digest | Reject conflict and emit audit event | Treat as retry |
| Out-of-order aggregate event | Hold/reconcile by aggregate version or request missing events | Apply stale state over newer authority |
| Crash before dispatch reservation | Command may be retried after state read and policy check | Mark effect as happened without evidence |
| Crash after reservation, before external dispatch known | Mark uncertain/reconcile adapter ledger where possible | Blind retry if not proven safe |
| Timeout after possible external side effect | Persist `unknown` then reconcile by external operation/idempotency reference | Translate timeout to failure or immediate repeat |
| Lease expires | Fence stale worker with epoch/token; reconcile any side effect | Assume expired lease means no action occurred |
| Policy changes/revokes during wait | Re-evaluate before dispatch; cancel pending reservation when possible | Use stale permit for new dispatch |
| Policy revoked after effect may have begun | Stop later steps; record and reconcile external state | Claim revocation retroactively undid effect |
| Broker/database partition | Backpressure and retain durable outbox; deny policy-critical writes if authoritative check unavailable | Lose acknowledged action or fail open |
| Projection lags | Expose source revision/freshness and serve authoritative query if needed | Write projection into source of truth |
| Poison/incompatible message | Quarantine/DLQ with reason and bounded retry | Infinite retry loop or silent drop |
| Audit sink unavailable | Buffer safely within bound; on overflow mark audit gap and stop high-risk actions | Claim a complete audit trail despite loss |
| Deletion while replicas are down | Tombstone in authority; reapply before replica is served | Republish deleted data during restore |
| HAL repair fails its threshold | Stop stage, roll back if safe, record failure/evidence, escalate | Widen scope or repeat unboundedly |
| Clock skew/expired approval ambiguity | Trust authoritative expiry check and explicit clock bound; otherwise defer | Extend approval because a local clock disagrees |

## 7.5 SLO decision

PRAIN does not impose one universal latency/availability number. Each deployment profile must declare SLOs for: policy-decision freshness/latency, command-dispatch latency, event processing lag, durable outbox age, reconciliation age for unknown actions, deletion propagation, evidence integrity check success, audit gap duration, recovery time, projection staleness, and HAL repair rollback. Each SLO includes percentile/window, measurement source, alert threshold, severity and consequence. Missing SLOs block production readiness for a deployment but do not block a runtime-agnostic Phase-0 specification. Authorization freshness, evidence integrity, tenant isolation and unknown-outcome correctness are hard safety properties, not relaxable SLOs.

## 7.6 Required conformance test families

The machine-readable suite includes tests for canonical schema validity and strictness, JSON/HTML parity, dangling references, knowledge-base dimension mapping, claim transitions, confidence/verification separation, action digest binding, expired/revoked approvals, tenant isolation, CAS conflicts, duplicate/out-of-order delivery, unknown execution outcome, expired lease/fencing, policy service outage, deletion propagation, restore-after-delete, evidence tampering/key revocation, HAL repair bounds, rollback and forbidden self-modification. A runtime must later implement these scenarios against real adapters; current package validates only the specification artefacts and deterministic model rules.
