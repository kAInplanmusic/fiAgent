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
