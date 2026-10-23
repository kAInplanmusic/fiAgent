# Step 16 — Durable Event Delivery (v1.2.1)

## Implemented
- SQLite delivery ledger keyed by `(event_type, consumer_id, event_id)` with explicit states:
  `PENDING`, `IN_FLIGHT`, `SUCCEEDED`, `FAILED`, and `OUTCOME_UNKNOWN`.
- Publishing persists the event and per-consumer pending deliveries before invoking handlers.
- Delivery is marked `IN_FLIGHT` transactionally before the callback and `SUCCEEDED` only after the callback returns.
- Handler exceptions transition to `OUTCOME_UNKNOWN`; no automatic retry is attempted.
- On process restart, abandoned `IN_FLIGHT` deliveries are changed to `OUTCOME_UNKNOWN`.
- Subscribing creates missing deliveries for previously persisted events and resumes only `PENDING` deliveries.
- `delivery_status()` exposes state, attempt count, error and reconciliation evidence.
- `reconcile_delivery()` requires non-empty evidence. `NOT_EXECUTED` requeues as `PENDING`; `SUCCEEDED` and `FAILED` are terminal.
- Legacy reservations from the previous `prain_event_processed` table migrate conservatively to `OUTCOME_UNKNOWN`, because a reservation does not prove callback completion.

## Guarantees and limits
- No exactly-once external effect is claimed. A handler may have acted before a crash/exception, so uncertain deliveries are not retried until reconciled.
- Delivery state and event log are durable in SQLite. Handler registrations remain process-local and must be re-registered after restart.
- Reconciliation evidence is supplied by the caller and is not independently authenticated.
- This is a local prototype, not a production broker or distributed transaction system.

## Validation
- `tests/test_durable_components.py`: 9/9 tests passed after the final delivery changes.
- A full suite run passed 64/64 immediately before the final catch-up-on-subscribe adjustment. Two subsequent full-suite reruns were blocked by a multiprocessing `SemLock`/spawn environment error; the focused durable-component suite passed after the adjustment.
- Overall status remains `PARTIAL_PASS`; execution remains `simulated_only`.
