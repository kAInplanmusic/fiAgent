# 15. Normative state machines and transition guards

**Status:** normative Phase-0 specification. These are transition contracts and reference rules, not an implementation or evidence that distributed execution has been tested.

## 15.1 Common rules

1. A status value is not a complete event history. State changes are recorded append-only with actor, event time, prior/current state, reason, rule version and evidence references. A correction adds a new event; it never edits or erases an old event.
2. A transition is valid only if both its edge and its guard are valid. A schema-valid object alone does not prove that its transition is authorized.
3. A timeout, expired lease, missing acknowledgment or worker crash does not prove that an external effect did not happen. When the effect is uncertain, the state is `unknown` or `reconciliation_required`; never blind-retry.
4. Authorization, execution and verification are independent facts. `permit` does not mean dispatched; dispatch acknowledgment does not mean effect occurred; effect observed does not mean success criteria were met; an execution receipt does not alone mean a goal is complete.
5. A retry of the same command preserves its `command_id`, `idempotency_key` and canonical action digest and increments the attempt. A materially changed action is a new command requiring new authorization and a new idempotency key.

## 15.2 Claim epistemic status

The canonical edge matrix remains the one in `03_CLAIM_ONTOLOGY_AND_LIFECYCLE.md` §3.4. `verified` requires a passing, named verification procedure and `verification_ref`; `refuted` requires a failed procedure and `refutation_refs`. Confidence alone never triggers a transition. Every non-initial transition requires a strictly increasing revision, actor, valid timestamp, reason and rule version. A refuted proposition/scope is terminal: a corrected or differently scoped assertion is a new claim/revision lineage, not resurrection of the refuted history. The record lifecycle (`active`, `superseded`, `withdrawn`, `quarantined`) is orthogonal to epistemic state.

## 15.3 Policy decision: immutable evaluation outcomes, not a mutable lifecycle

`permit`, `deny`, `require_approval` and `defer` are immutable outcomes of one evaluation, not successive states of the same record.

- `permit` may authorize dispatch only while its exact action digest, tenant, principal, identity version, revocation epoch, policy version/rules, target, scope, risk class and expiry remain current. `evaluated_at <= now < expires_at <= command.deadline` is required.
- `deny` is terminal for that evaluation. A policy/data/context change requires a new evaluation record, not mutation of `deny`.
- `require_approval` is never dispatchable. Once an approval is issued, PRAIN performs a new evaluation and creates a new decision ID/digest. The historical `require_approval` decision remains unchanged.
- `defer` is non-permit. Retry the evaluation only after the blocking uncertainty is resolved; do not transform `defer` into `permit`.
- A decision must list exactly the approval references bound to the command. Missing or extra approval references are a binding error, not a best-effort match.

### Canonical action digest

The digest is SHA-256 over UTF-8 JSON with recursively sorted object keys, compact separators, unmodified strings, and no implicit type coercion. The digest input object is exactly:

```json
{
  "tenant_id": "...",
  "actor_principal_id": "...",
  "goal_id": "...",
  "plan_id": "...",
  "capability": "...",
  "action": "...",
  "target_ref": "...",
  "input_digest": "sha256:...",
  "declared_side_effects": ["..."],
  "risk_class": "...",
  "deadline": "...",
  "authorization_context": {
    "identity_version": "...",
    "revocation_epoch": 0,
    "delegation_refs": [],
    "policy_rule_refs": ["..."],
    "data_classification": "...",
    "access_scope_digest": "sha256:..."
  }
}
```

The fields above are mandatory and all are digest-bound. `policy_version`, `revocation_epoch`, current policy rules, identity version, decision expiry and approval state are also independently compared to current authoritative values immediately before reservation. Approval references are **not** included in the digest because that would make an approval circularly depend on its own reference; instead, the decision's approval set must exactly equal the command's approval set, and each approval binds to the digest.

## 15.4 Approval lifecycle

The approval record has two orthogonal fields: decision (`approve`/`deny`) and lifecycle status.

| Event/previous status | Next status | Guard |
|---|---|---|
| New + `approve` | `issued` | Authorized approver, valid action/tenant/identity/policy binding, explicit rationale, valid time window |
| New + `deny` | `rejected` | Denial reason recorded; never dispatchable |
| `issued` | `consumed` | Atomic dispatch reservation succeeds and usage count reaches `max_uses` |
| `issued` | `revoked` | Authorized revocation event; epoch/version update recorded |
| `issued` | `expired` | Authoritative time reaches/exceeds `expires_at` |
| `consumed`, `rejected`, `revoked`, `expired` | none | Terminal; never reissue or reactivate the same record |

`single_use` requires `max_uses = 1`; `bounded_use` requires `max_uses >= 2`. `0 <= usage_count <= max_uses`. An `issued` approval must have remaining use budget. `consumed` means the budget is exhausted. A denial must have `lifecycle_status=rejected`; `rejected` cannot be combined with `decision=approve`.

The approver must be authorized under the policy profile in force. Where separation of duties is required, the approver must differ from the actor and from HAL/repair executor identities as applicable. A receipt of approval does not bypass the final policy/revocation check.

## 15.5 Dispatch reservation and idempotency

The reservation is a single logical atomic boundary over: (a) tenant-scoped idempotency key ↔ action digest, (b) fresh policy/identity/revocation check, and (c) approval usage reservation/consumption. If those operations cannot be made atomic by one storage system, a documented equivalent protocol must provide the same linearizable outcome and recovery evidence.

- Previously seen key + same digest: return/resume the recorded command reservation/receipt; do not create a second external effect or consume approval twice.
- Previously seen key + different digest: reject as conflict and emit an audit event.
- Fresh key + invalid/expired/revoked approval, stale decision, changed epoch, policy outage, or mismatch: no dispatch reservation.
- Revocation before reservation prevents dispatch. Revocation after an effect may have started stops later actions but does not claim to undo the external effect.

## 15.6 Execution and outcome-reconciliation state machine

The command is an immutable intent. Its current execution state is a projection derived from reservation records and append-only receipts; the projection is not a mutable replacement for the receipts.

| Previous state | Allowed next state | Required condition |
|---|---|---|
| `not_dispatched` | `reserved` | Current permit, fresh identity/revocation/policy, matching digest, atomic idempotency/approval reservation |
| `reserved` | `accepted`, `failed_pre_effect`, `unknown` | Durable dispatch outcome recorded; uncertainty stays unknown |
| `accepted` | `started`, `effect_possible`, `effect_observed`, `failed_pre_effect`, `unknown`, `reconciliation_required` | Receipt describes observed adapter/external state; no inferred success from acknowledgment |
| `started` | `effect_possible`, `effect_observed`, `failed_pre_effect`, `unknown`, `reconciliation_required` | Evidence indicates whether an external effect may have started |
| `effect_possible` | `effect_observed`, `unknown`, `reconciliation_required` | Effect confirmed or unresolved; never jump to pre-effect failure without evidence |
| `unknown` | `reconciliation_required`, `effect_observed`, `failed_pre_effect` | Authoritative reconciliation determines uncertainty, presence or absence |
| `reconciliation_required` | `unknown`, `effect_observed`, `failed_pre_effect` | New reconciliation evidence; indeterminate remains unresolved |
| `effect_observed` | `verified`, `reconciliation_required`, `compensated` | Independent verification, counterevidence, or independently verified compensation |
| `verified` | `reconciliation_required` | New credible counterevidence or integrity conflict; historical verification receipt remains immutable |
| `failed_pre_effect` | `reserved` (new attempt) | Definitive evidence no effect occurred, retry class is not `never`, budget remains, fresh permit and same command digest/key; attempt increments |
| `compensated` | `reconciliation_required` | New credible evidence of residual/unreversed effect |

All other transitions are forbidden. `failed_pre_effect` is a result for that attempt, not permission to repeat without a fresh authorization check. `verified` requires evidence references, a verification reference, and an independent verifier distinct from the executor. `effect_observed` requires evidence of the observed side effect. `failed_pre_effect` requires evidence supporting the absence of an effect and an error code. `compensated` requires evidence that compensation actually occurred; it is not inferred from a compensation request.

### Reconciliation result matrix

| Reconciliation result | Permitted next action | Retry? |
|---|---|---|
| `effect_absent` | `retry_if_policy_allows` or `escalate` | Only after fresh policy check, retry budget, allowed retry class and same command idempotency binding |
| `effect_present` | `verify`, `do_not_retry`, `compensate` or `escalate` | No retry of the original effect; verify, compensate under policy, or escalate |
| `indeterminate` | `escalate` | No retry; preserve `unknown`/`reconciliation_required` |

`unknown` and `reconciliation_required` receipts must include reconciliation data; an `indeterminate` result cannot be paired with a retry action. An external timeout or worker lease expiration never counts as `effect_absent`. Restore applies current revocation and deletion tombstones before replay/resume, then reconciles uncertain commands before dispatch resumes.

## 15.7 Goal lifecycle

| From | Allowed destinations |
|---|---|
| `proposed` | `accepted`, `cancelled`, `superseded` |
| `accepted` | `active`, `blocked`, `cancelled`, `superseded` |
| `active` | `blocked`, `verifying`, `failed`, `cancelled`, `superseded` |
| `blocked` | `active`, `failed`, `cancelled`, `superseded` |
| `verifying` | `completed`, `active`, `blocked`, `failed`, `cancelled`, `superseded` |
| `completed`, `failed`, `cancelled`, `superseded` | none |

`blocked → active` requires evidence that the blocker was removed. `verifying → completed` requires independent verification of every acceptance criterion and all required evidence kinds. If verification is insufficient, return to `active`/`blocked`, do not mark complete. A terminal goal is not reopened in place; continuation creates a new linked goal/revision with history preserved.

## 15.8 HAL repair proposal lifecycle

| From | Allowed destinations | Guard |
|---|---|---|
| `proposed` | `approved`, `rejected`, `expired` | Catalog/bounds check and independent policy decision; human approval where risk profile requires |
| `approved` | `executing`, `expired` | Approval and decision still current, bounds/target/observation digest unchanged |
| `executing` | `succeeded`, `rolled_back`, `failed` | Measured threshold result, rollback/evidence recorded, bounded attempts maintained |
| `succeeded`, `rolled_back`, `failed`, `rejected`, `expired` | none | Terminal |

A stale observation, revoked decision, changed action digest, exceeded bound or expired approval invalidates an approved proposal before execution. HAL cannot approve itself, modify the evaluating policy, enlarge its own bounds, or mark success using its own unverified assertion.

## 15.9 Delegation lifecycle

`active → suspended | revoked | expired | exhausted`; `suspended → active | revoked | expired | exhausted` only through a new authorized event and fresh validity checks. Every transition records an authorized actor, event reference, timestamp and reason. Reactivation from `suspended` additionally requires an authoritative fresh-validity check, an incremented grant/revocation epoch and unchanged scope; it must not widen authority. `expired` requires authoritative time at or after the grant expiry, and `exhausted` requires usage to reach the declared budget. `revoked`, `expired` and `exhausted` are terminal. Reactivation of a suspended grant increments the relevant epoch and cannot erase prior suspension/revocation events. A revoked, expired or exhausted delegation must be replaced with a new grant rather than reactivated.

## 15.10 Conformance boundary

The state-machine reference suite validates specified transition tables, transition guards, digest bindings and negative vectors using deterministic offline models. It does not prove atomicity under actual concurrent writers, external adapter truth, timing under clock skew, real crash recovery, independent key management or production security. Those are mandatory runtime conformance tests before production use and are explicitly outside Phase 0.
