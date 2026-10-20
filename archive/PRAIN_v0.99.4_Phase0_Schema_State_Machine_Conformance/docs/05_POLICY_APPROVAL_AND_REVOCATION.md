# 5. Policy gateway, approvals and revocation lifecycle

## 5.1 Mandatory policy gateway

The policy gateway is the only component that can return an authorization decision for an action. A/R/I/N components may supply identity/context, reason, goals or execution capability, but may not bypass the gateway. Missing/invalid policy, ambiguous principal/tenant, stale policy version, expired approval, inability to check revocation, or unresolved target scope yields `deny` or `defer`; no implicit permit.

## 5.2 Authorization input binding

A policy evaluation binds to all of:
- authenticated `tenant_id` and `actor_principal_id` plus current identity/revocation epoch;
- capability, action, target, canonical input digest and declared side-effect digest;
- goal/plan reference and risk class;
- policy bundle/version and required rule references;
- approval references, deadlines and use policy;
- data classification and relevant record-access scope.

Changing any bound field invalidates that decision/approval for the modified action. Content digesting uses the specified canonicalization rules for structured inputs; binary/media inputs use a declared media-specific canonicalization.

## 5.3 Policy decision outcomes

- `permit`: all checks pass; decision is short-lived, action-bound and expires before the command deadline.
- `deny`: explicit policy violation or revoked/ineligible principal/tenant.
- `require_approval`: policy allows a human approval path but no valid approval is yet present.
- `defer`: the decision cannot safely be reached now (policy service unavailable, unknown target, unresolved conflict, stale authorization snapshot). `defer` is non-permit.

## 5.4 Approval constraints

Approval is an explicit record bound to tenant, exact action digest, actor, capability, target-scope digest, side-effect digest, policy version, approver identity and expiration. The approver must be authorized and must not self-approve where separation-of-duties policy forbids it. One-shot approval is the default; bounded-use must declare max uses. Approvals cannot be transferred to a different actor or action. The approval system atomically reserves/consumes approval usage with command dispatch reservation so duplicate messages do not consume it twice or authorize changed payloads.

## 5.5 Time-of-check/time-of-use and revocation

1. Evaluate policy before planning is committed.
2. Re-check actor/tenant/delegation, policy version, decision expiry and approval immediately before dispatch reservation.
3. Atomically reserve the command idempotency key and consume one-shot approval for that exact action digest.
4. Immediately before an irreversible external boundary, re-check when the adapter supports it and record the decision token used.
5. If revoked before dispatch reservation, deny and do not execute. If revoked after an external action may have started, stop further steps, record `unknown`/`reconciliation_required` as appropriate and reconcile; never state that revocation retroactively cancelled an external effect.
6. If the policy service is unavailable, high/critical and all write/destructive actions fail closed. A specifically approved implementation profile may allow only declared low-risk read-only cached decisions within a bounded age; default profile allows no stale write permission.

## 5.6 Default risk policy

- **Low:** read-only and reversible; still requires explicit capability and tenant policy.
- **Moderate:** scoped internal mutation with tested idempotency and rollback; action-bound decision required.
- **High:** externally visible, sensitive-data, cross-boundary, expensive or difficult-to-reverse; requires explicit decision and human approval unless a pre-approved rule narrowly enumerates it.
- **Critical:** destructive, privilege/policy/key changes, bulk deletion, credential changes, or irreversible high-impact external effect; human approval plus independent policy check and strong evidence trail required.

No risk class creates permission by itself. A declared risk class can be raised by policy; it may not be lowered by the planner/agent.

## 5.7 Negative invariants

No action is dispatched if a required approval expires, revocation epoch changes, payload digest differs, target is broadened, side effects differ, identity changes, tenant is suspended, policy version is unknown, or authorization result is not `permit`. Tool capability does not imply permission. Confidence or inferred intent does not imply permission.
