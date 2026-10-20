# Step 10 — Durable Outbox and Recovery (v1.1.5)

## Implemented
- Admission/receipt and outbox insertion share one SQLite `BEGIN IMMEDIATE` transaction.
- Outbox state machine: `PENDING -> IN_FLIGHT -> SUCCEEDED | FAILED | OUTCOME_UNKNOWN`.
- Atomic `claim_next` prevents two workers sharing this SQLite DB from claiming the same pending row.
- Restart recovery converts abandoned `IN_FLIGHT` rows to `OUTCOME_UNKNOWN`; it never blindly retries them.
- Terminal outcome writes are accepted only from `IN_FLIGHT`; invalid statuses fail closed.
- Action payload is persisted for audit/reconciliation. Dispatcher does not invoke external services; execution remains `simulated_only`.

## Explicit limits
This is an outbox persistence primitive, not an external-effect dispatcher. A process can still crash after an external service acts and before outcome persistence; recovery correctly records uncertainty but needs a provider-specific reconciliation mechanism. No exactly-once external effect is claimed. `PRAINRuntime` stores its outbox row atomically with admission only when a durable admission store is configured.

## Validation
The unit suite covers atomic admission/outbox insertion, claiming, outcome transition validation, and restart recovery to `OUTCOME_UNKNOWN`. See `tests/test-report.txt` for the current run.
