# Step 10 — Durable Outbox and Recovery

Date: 2026-10-20
Prototype: v1.1.5
Status: `PARTIAL_PASS`

## Changes implemented
- Durable admission/receipt and outbox row are inserted in the same SQLite transaction.
- Added explicit outbox states: `PENDING`, `IN_FLIGHT`, `SUCCEEDED`, `FAILED`, `OUTCOME_UNKNOWN`.
- `claim_next()` uses a write transaction and conditional state transition to prevent duplicate claims against the same SQLite database.
- `record_outcome()` accepts only known outcome states and only from `IN_FLIGHT`.
- `recover_in_flight()` changes abandoned `IN_FLIGHT` rows to `OUTCOME_UNKNOWN`; it deliberately does not retry automatically.
- `PRAINRuntime.request_action` writes an outbox payload when a durable store is configured.

## Verification
- Unit tests: **41/41 passed** (`archive/PRAIN_v1.1.5_Phase1_Reference_Prototype/tests/test-report.txt`).
- Three new durable-outbox tests cover atomic insertion/persistence, recovery to unknown, and valid outcome transitions.
- ZIP integrity checked for the prototype and master package. SHA-256 manifest entries are generated from packaged files.

## Limits and next work
- No dispatcher calls external services; all actions remain `simulated_only`.
- `OUTCOME_UNKNOWN` requires provider-specific reconciliation before safe retry.
- This is not exactly-once external execution.
- Approval authority/revocation, evidence ledger and state/goal/event persistence, multi-host coordination, lease expiry/fencing, migration rollback and fault injection remain open.
- `PRAINRuntime` uses the outbox only when `DurableAdmissionStore` is supplied; in-memory mode remains available and does not provide durable guarantees.
