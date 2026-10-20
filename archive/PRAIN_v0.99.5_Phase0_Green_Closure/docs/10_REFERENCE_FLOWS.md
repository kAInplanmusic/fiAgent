# 10. Normative reference flows

These are specification-level flows, not implementation code.

## 10.1 Goal-to-action

```text
observation → provenance/classification → claims/reasoning → goal revision
  → plan/action digest → policy decision (permit/deny/require_approval/defer)
  → approval if required → fresh policy/revocation check
  → durable idempotency/approval reservation → command dispatch
  → append-only execution receipts → independent evidence verification
  → criterion-level goal verification → goal completed
```

If policy is not `permit`, no dispatch. If result is ambiguous after dispatch, persist `unknown` and reconcile before retry. A textual agent report is not evidence of completion.

## 10.2 Claim ingestion

```text
raw source → observation record + provenance → candidate claim revision
  → assign epistemic state justified by origin → attach evidence refs
  → optional verification procedure → append transition event
  → CAS claim head → invalidate/recheck dependent claims where needed
```

The ingestion component cannot promote a claim to `verified` merely because it has high confidence.

## 10.3 Repair

```text
fresh health signal → HAL diagnosis → bounded repair proposal
  → catalogue check → independent policy decision + human approval if required
  → fresh revocation/policy check → bounded canary/attempt
  → observe authoritative outcome → success criteria pass OR rollback
  → receipt + evidence + metrics → close or escalate
```

HAL cannot approve its own proposal, expand bounds after failure, or change the policy that evaluates the proposal.

## 10.4 Deletion

```text
authenticated request → scope/retention/legal-hold evaluation → authoritative tombstone
  → source writes blocked → propagation to replicas/events/projections/indexes/caches/exports
  → derived claim review → content deletion/key erasure as applicable
  → backup expiry/restore tombstone test → per-target receipts
  → verified only when all required targets checked or exceptions explicitly recorded
```

## 10.5 Restore after outage

```text
restore authoritative snapshot + append-only ledger → validate digests/versions
  → replay events idempotently → apply current revocations and deletion tombstones first
  → rebuild derived projections → reconcile unresolved commands/receipts
  → verify policy and identity versions → resume dispatch only after consistency gate
```

Restoring a backup never resurrects a revoked approval or deleted payload as active.
