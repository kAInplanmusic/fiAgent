# Step 14 — Durable Runtime Components (v1.1.9)

## Result
Added SQLite-backed adapters for `GoalRegistry`, `EventBus` and `EvidenceLedger` and exposed them through `PRAINRuntime(persistent_db_path=...)`.

- Goals and verification/status changes survive process restart.
- Event records and consumer/event reservations survive restart. Handlers must be re-registered in each process.
- Evidence entries are stored in sequence and the hash chain is revalidated on adapter initialization.
- Prototype remains `simulated_only`; no external provider effects are executed.

## Important delivery semantics
`DurableEventBus` persists a consumer reservation **before** invoking the callback. This suppresses duplicate callback execution, but a process crash after reservation and before/during callback can lose delivery. Therefore this is not an at-least-once durable broker and does not provide exactly-once effects. A future version should add explicit delivery states (`PENDING`, `IN_FLIGHT`, `SUCCEEDED`, `OUTCOME_UNKNOWN`) and reconciliation, rather than changing this behavior silently.

## Remaining limits
- Runtime `StateStore` is still in-memory unless the caller separately uses `DurableStateStore`; it is not automatically wired to `persistent_db_path`.
- The existing admission/outbox database can share the same SQLite path, but its connection lifecycle warnings require separate cleanup.
- SQLite is local durability, not a distributed database or consensus mechanism.
- Database corruption, disk-full, backup/restore and cross-version migration scenarios have not been exhaustively fault-injected.

## Validation
Command: `PYTHONPATH=. python -m unittest discover -s tests -v`
Result: **59 tests passed, 0 failures, 0 errors**. Four new tests cover goal restart, event-log/dedup restart, evidence-chain restart, and runtime wiring.

## Gate
Overall status remains `PARTIAL_PASS`; this step is not a production-readiness claim.
