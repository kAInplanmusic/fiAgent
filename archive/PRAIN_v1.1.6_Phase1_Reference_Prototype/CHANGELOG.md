## 1.1.6 — 2026-10-20
- Added explicit-handler outbox dispatcher; no handler means no claim or execution.
- Handler exceptions/invalid results become OUTCOME_UNKNOWN; no automatic retries.
- Added evidence-gated reconciliation; only authoritative NOT_EXECUTED results return items to PENDING.
- Full unit suite: 47/47 passing. Runtime remains simulated-only.

# Changelog

## 1.1.4 — 2026-10-20
- Integrated optional `DurableAdmissionStore` into `PRAINRuntime.request_action`.
- Added durable same-key replay and fingerprint-conflict checks across runtime instances.
- Added cross-instance regression tests for replay, changed payloads, and single-use approval consumption.
- Full suite: 38/38 passing.
- Runtime remains simulated-only; state, event bus and evidence ledger are still in-memory; no outbox or real side effects.

## 1.1.3
- Added standalone SQLite durable admission primitives and store-level tests.

## 1.1.2
- Added process-local serialized action admission and single-use approval tracking.

## 1.1.1
- Added approval lifecycle checks and nested payload snapshots.

- v1.1.5: atomically insert a durable outbox item with durable admission; add transactional claiming, explicit outcomes, and conservative crash recovery to `OUTCOME_UNKNOWN`; external actions remain simulated.
