# PRAIN v0.99.4 — Schema/state-machine crosswalk

**Normative scope:** Phase 0 specification only. This document maps schema-level state vocabularies to transition semantics and lists cross-field guards that JSON Schema alone does not establish.

## Rules of interpretation

1. Schema enums constrain vocabulary; they do not by themselves authorize a transition.
2. Transition guards, authority, timestamps, revision monotonicity, evidence existence, expiry, and cross-record binding MUST be checked by a conforming validator/runtime.
3. A missing field is not proof that the underlying fact is false. Where evidence is required for a transition, absence means the transition is not accepted.
4. A `PASS` from offline fixtures validates this reference model only; runtime and distributed-system conformance remain Phase-1 obligations.

## Canonical state-bearing contracts

| Contract | State field(s) | Allowed values / semantic mapping | Required cross-field/reference guards |
|---|---|---|---|
| `claim.schema.json` | `epistemic_status`, `verification_status`, `lifecycle_status` | Epistemic vocabulary defined in §15.2; verification and lifecycle are separate dimensions | `verified` requires passing named procedure and `verification_ref`; `refuted` requires failed procedure and `refutation_refs`; transitions require increasing revision, actor, timestamp, reason, evidence references |
| `claim-transition-event.schema.json` | `from_epistemic_status`, `to_epistemic_status` | Both must be members of claim epistemic vocabulary | Edge must be allowed by normative claim transition matrix; transition guards must pass |
| `policy-decision.schema.json` | `decision` | `permit`, `deny`, `require_approval`, `defer` | `permit` must bind current subject, action digest, policy/rule version, scope and expiry; approval-required is not a permit |
| `policy-approval.schema.json` | `lifecycle_status`, `decision` | Approval lifecycle plus `approve`/`deny` decision | Approval must bind principal, command/action digest, scope, policy version and validity interval; reject/expired/revoked/consumed approvals cannot authorize a new use; bounded-use consumption must be atomic |
| `execution-receipt.schema.json` | `status` | Accepted/started/effect/verification/failure/unknown/reconciliation/compensation states | Receipt status must agree with effect evidence and result fields; `unknown`/`reconciliation_required` prohibit blind retry; `verified` requires independent verification evidence |
| `action-command.schema.json` | `retry_class` | `never`, `read_safe`, `idempotent`, `reconcile_before_retry` | Retry preserves command ID, idempotency key and canonical digest; increments attempt; fresh permit and current identity; prove effect absence for failed-pre-effect retry |
| `goal.schema.json` | `status` | Proposed/accepted/active/blocked/verifying/completed/failed/cancelled/superseded | `completed` requires explicit success criteria and verification evidence; terminal states cannot silently reopen; revisions must increase |
| `repair-proposal.schema.json` | `status` | Proposed/approved/rejected/executing/succeeded/rolled_back/failed/expired | Approval must bind exact repair proposal digest and risk class; policy/credential/source-of-truth/external-side-effect repairs require elevated approval; terminal outcome needs receipt/evidence |
| `delegation-grant.schema.json` | `lifecycle_status` | Active/suspended/revoked/expired/exhausted | Delegated authority cannot exceed issuer authority; expiry/revocation/suspension immediately invalidate new use; use limits must be atomically enforced |
| `principal.schema.json` | `lifecycle_status` | Active/suspended/revoked | Suspended/revoked principal cannot initiate new protected actions; authorization rechecks current identity |
| `tenant.schema.json` | `lifecycle_status` | Active/suspended/closed | Suspended/closed tenant rejects new protected operations; tenant isolation is an authorization and storage-boundary obligation |
| `evidence-record.schema.json` | `lifecycle_status` | Active/expired/quarantined/deletion_pending/deleted/legal_hold | Expired/quarantined/deleted evidence cannot satisfy current verification; legal hold blocks deletion; deletion state requires tombstone/receipt as specified |
| `deletion-request.schema.json` | `lifecycle_status` | Requested/approved/executing/blocked_legal_hold/verified/partially_verified/rejected | Legal hold must block destructive execution; verified deletion requires per-target evidence and tombstone; partial completion cannot be represented as fully verified |
| `health-signal.schema.json` | `status` | Healthy/degraded/unhealthy/unknown/stale | Stale/unknown health is not healthy; recovery requires fresh observation and timestamp |
| `state-record.schema.json` | `record_class`, `authority_class` | Typed record plus authoritative/append-only/derived/ephemeral classes | Derived projections cannot overwrite authoritative records; append-only evidence cannot be silently mutated |
| `message-envelope.schema.json` | `message_type` | Event/command/query/response/receipt/notification | Message identity, schema version, tenant, correlation and idempotency semantics must be validated at boundaries |
| `observation.schema.json` | `classification` | Classification vocabulary, not a lifecycle state | Classification labels constrain handling; provenance, source identity, timestamp and tenant scope must be checked independently |

## Required negative conformance cases

A conforming implementation/reference validator must reject at least these cases:

1. Unknown enum value for any state-bearing field.
2. A transition edge absent from its normative matrix, even if both endpoint enums are valid.
3. `verified` claim without a passing procedure and verification evidence reference.
4. `refuted` claim without a failed procedure and refutation evidence references.
5. Approval used after expiry, revocation, rejection or single-use consumption.
6. Approval bound to a different principal, action digest, tenant, scope or policy version.
7. Execution receipt marked `verified` without independent verification evidence.
8. Execution state `unknown` or `reconciliation_required` followed by blind retry without reconciliation and proof of effect absence.
9. Retry that changes action digest/idempotency key or fails to increment attempt.
10. Goal marked `completed` without success-criteria verification.
11. Delegation used beyond scope, after expiry/revocation, or beyond its use limit.
12. Deletion marked fully verified while any required target remains unverified or a legal hold applies.
13. Non-monotonic claim/goal/repair revision or event timestamp ordering violation.
14. Evidence reference that is syntactically present but does not resolve to an authorized, available record.

## Time- and reference-dependent guards

JSON Schema is used for local shape, required fields, and enum vocabulary. It is not treated as a complete substitute for reference resolution, clock-aware expiry checks, authorization decisions, compare-and-swap, atomic single-use approval consumption, or external-effect reconciliation. These guards are explicit normative obligations and must be implemented/tested separately.

## Release boundary

This crosswalk closes a specification consistency gap; it does not claim runtime conformance. Phase 0 can be considered specification-complete when the included deterministic checks pass and the user accepts the declared scope. Phase 1 remains separately gated.
