# 4. Identity, tenancy, delegation and authority model

## 4.1 Entity model

- **Principal:** a human, agent, service or system identity with stable ID, tenant membership, lifecycle, identity version, authentication/key references, lineage and revocation epoch. Principal roles are not implicit permissions.
- **Tenant:** the security/data isolation boundary with lifecycle, isolation profile, policy bundle version and data residency profile.
- **Delegation grant:** explicit bounded capability allowlist, target scope, validity period, use limit, grantor/grantee, policy decision provenance and revocation epoch. Delegation may narrow authority; it may never add capabilities the grantor does not possess.
- **Agent self-model (A):** versioned, inspectable claims about identity, lineage, preferences/constraints and continuity. It is not a credential store or policy authorizer.
- **Capability:** named operation supported by an adapter. Capability availability does not equal authorization.

## 4.2 Tenant invariants

1. Every authoritative data record, message, claim, goal, command, approval, evidence record and policy decision has an explicit tenant ID, except for explicitly designated global public data.
2. A missing tenant is rejected; no implicit default tenant.
3. Cross-tenant reads/writes are denied unless an explicit, auditable sharing grant identifies source tenant, destination tenant, allowed records/fields, purpose, expiration and revocation path.
4. Tenant context is established by authenticated principal/context, never accepted solely from untrusted payload fields.
5. Tenant-bound cache keys, vector-index filters, dedup keys, policy decisions and evidence references include tenant scope.
6. Closing/suspending a tenant denies new commands; in-flight external actions are reconciled, not silently assumed cancelled.

## 4.3 Identity lifecycle

`active → suspended → active` is allowed only through an attributable policy decision; `active/suspended → revoked` is monotonic for that identity version. Recovery creates a new key/version with lineage rather than erasing revocation history. Rotating a credential does not change principal identity; replacing a compromised principal or key must be an explicit lineage transition. Delegations and approvals are re-evaluated when identity version, revocation epoch, tenant status or policy version changes.

## 4.4 Authority / consistency matrix

| Record class | Authority/source of truth | Consistency requirement | Mutation model | Conflict disposition |
|---|---|---|---|---|
| Principal, Tenant, key status | Identity authority | Strong for reads used in authorization | Versioned CAS + audit event | Reject stale write; security conflict escalates |
| Policy bundle, rule version | Policy authority | Strong at authorization/dispatch boundary | Immutable policy versions, controlled activation | Default deny/defer until resolved |
| Approval/delegation/revocation | Approval/identity authority | Strong, use-consumption atomic within ledger | Append-only events + CAS head/count | Revocation wins before dispatch reservation; after dispatch, reconcile external outcome |
| Goal/plan | Goal authority per tenant/aggregate | Strong per aggregate; projections eventual | Revisioned updates/CAS | Explicit conflict; no last-writer-wins for acceptance criteria/status |
| Claim revision/head | Claim authority | Immutable revisions; strong head CAS | Append-only revisions/transitions | Preserve competing claims; create dispute set |
| Evidence manifest/audit receipt | Evidence ledger | Append-only ordering per ledger partition; integrity checked | Append-only receipts; encrypted content separated | Integrity failure quarantines; no silent mutation |
| Command/idempotency ledger | Execution authority | Strong uniqueness by tenant + idempotency key + action digest | Durable command state machine | Return prior result for same digest; conflict if key reused for different digest |
| Execution receipts | Receipt authority | Append-only; ordered per command/attempt | New receipt events | Unknown results require reconciliation; never inferred as failure |
| Observations | Ingestion source plus durable receipt | At-least-once; dedup where keys exist | Append-only, replayable | Keep source timestamp and receive timestamp; preserve duplicates if identity is ambiguous |
| Health signals | Signal source; may be stale | Eventual acceptable within `fresh_until` | Append-only/time series | Stale/unknown cannot authorize repair by itself |
| Repair proposals | HAL proposal record | Versioned, policy-gated | Append-only proposal state + decisions | Proposal conflicts resolve by policy; not by HAL self-approval |
| Projections/search/vector indexes/cache | Derived store | Eventual; rebuildable | Derived only, tagged with source revision | Never writes back over authority; invalidate/rebuild |
| Logs/metrics/traces | Observability pipeline | Delivery may be delayed, security-critical audit evidence cannot be silently dropped | Append-only where mandated; redacted | Mark gaps/overflow; never pretend complete audit if dropped |

## 4.5 Consistency model

Strong consistency is scoped to authorization-critical mutable heads and uniqueness constraints; per-aggregate order is required for goals, claim heads, command/receipt lifecycle and approvals. Projections and search indexes may converge eventually but must declare source revision/freshness. Observations are at-least-once; consumers are idempotent. No global exactly-once claim. Cross-system effects require reconciliation.

## 4.6 CAS and version rules

A mutable authoritative head has `version` and `updated_at`. Writers submit the observed version; if it differs, reject with conflict and return the new version, without overwriting. Time alone is not a concurrency token. `updated_at` is diagnostic. Leases require epochs/fencing tokens; lease expiry does not prove the former worker did not execute an external action.
