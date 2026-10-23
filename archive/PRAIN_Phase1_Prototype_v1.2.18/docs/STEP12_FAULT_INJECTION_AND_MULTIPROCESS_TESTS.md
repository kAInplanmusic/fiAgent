# Step 12 — Fault injection and multi-process contention tests (v1.1.7)

## Scope

This step adds local deterministic tests for the SQLite outbox's crash-recovery and concurrency boundaries. It does not enable external effects or claim exactly-once delivery.

## Added coverage

- Simulated process death after claim but before outcome persistence; restart recovery moves `IN_FLIGHT` to `OUTCOME_UNKNOWN` and refuses blind retry.
- Four independent processes contend to claim one outbox row; exactly one process may win.
- Two reconciliation attempts race; the status-guarded update permits one winner only.
- Crash-window invariant: missing/empty evidence cannot convert an unknown result to a retryable state.

## Limits

These are process-level tests of SQLite coordination, not kill -9 tests at a real provider boundary. No external provider is called, no real side effect is performed, and caller-supplied reconciliation evidence is not cryptographically authenticated. Provider idempotency semantics and production deployment tests remain open. Audit status remains `PARTIAL_PASS`.
