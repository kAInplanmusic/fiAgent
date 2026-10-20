# Step 7 — Process-local action admission and approval reuse guard

Date: 2026-10-20  
Prototype: PRAIN Phase 1 Reference Prototype v1.1.2  
Status: `PARTIAL_PASS`

## Changes

- `PRAINRuntime.request_action` now serializes action admission through a process-local `RLock`.
- Concurrent requests with the same idempotency key are checked/replayed under the same lock; the regression test issues 40 calls over 12 worker threads and observes one unique receipt.
- Approvals declaring `usage_policy=single_use` must have a non-empty stable `approval_id`. The runtime remembers consumed IDs in memory and denies later use of the same approval ID with a different idempotency key.
- Added tests for concurrent duplicate submissions, cross-key single-use approval reuse, and missing approval ID.
- Full unit suite: 30/30 passed.

## Exact scope and limitations

This is a process-local guard, not a distributed transaction. The lock and consumed-approval set disappear on restart and are not shared by multiple runtime instances or processes. Approval IDs are not cryptographically authenticated, and the approval dictionary remains a caller-supplied object rather than a record fetched from a trusted authority. No real external action is executed; the runtime remains `simulated_only`.

The implementation deliberately does not claim durable exactly-once execution. Before enabling external effects, the next design must introduce a transactional persistence boundary that atomically binds idempotency key, request fingerprint, approval consumption, decision, and outbox intent. An external side effect then requires an idempotent adapter or reconciliation strategy; a database transaction alone cannot make an arbitrary external service exactly-once.

## Verification

Run from this directory:

```bash
python -m unittest discover -s tests -v
python -m prain.demo
```

Expected test result: 30 tests passed. Demo output must show runtime version `1.1.2`, `simulated_only`, and a valid evidence chain.

## Remaining gates

1. Durable transactional storage and schema migrations.
2. Unique constraints for idempotency keys and approval IDs across processes.
3. Signed/authenticated approval issuer and tenant/action/target/digest binding.
4. Crash recovery tests around decision, approval consumption, receipt and outbox writes.
5. External-effect reconciliation and idempotent adapter contract.
