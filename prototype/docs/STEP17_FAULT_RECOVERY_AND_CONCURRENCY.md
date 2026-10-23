# Step 17 — Event Delivery Fault Recovery and Concurrency (v1.2.2)

## Scope
Step 17 adds regression coverage around the existing SQLite-backed event delivery ledger. It does not add a distributed broker or claim exactly-once external effects.

## New checks
- Concurrent duplicate publication while a callback is in flight invokes the callback once; competing publishers observe the existing in-flight delivery.
- A delivery reconciled as `NOT_EXECUTED` is eligible for resumption and completes when the consumer is re-registered.
- Reconciliation is rejected unless the delivery is currently `OUTCOME_UNKNOWN`.

## Operational limits
- Consumer handlers are process-local and must be registered after restart.
- `OUTCOME_UNKNOWN` remains non-retriable until explicit reconciliation.
- Reconciliation evidence is caller-supplied and is not independently authenticated.
- Tests exercise threads against one process and SQLite database; they do not establish correctness for arbitrary multi-host deployments or external provider semantics.
