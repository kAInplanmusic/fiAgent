# Step 15 — Runtime durable state wiring (v1.2.0)

## Change
`PRAINRuntime(persistent_db_path=...)` now wires `DurableStateStore` automatically. A single file path can host the state, goal, event, and evidence tables. The separate `DurableAdmissionStore` remains opt-in because admission/outbox configuration and policy semantics are distinct.

## Guarantees tested
- State values and version numbers survive runtime reconstruction.
- A stale compare-and-swap version is rejected after restart.
- Runtime snapshots count durable state records.
- SQLite connections used by the state adapter are closed after each operation.

## Limits
This is local SQLite persistence, not distributed consensus. Event delivery is not yet crash-safe: consumer reservations precede callbacks, so a crash can lose delivery. The prototype remains `simulated_only`; no real-world side effects are executed. Database migration, backup/restore, disk-full and corruption scenarios are not exhaustively validated.

## Gate
`PARTIAL_PASS` until event delivery has explicit durable state/recovery semantics and broader fault-injection/migration coverage is complete.
