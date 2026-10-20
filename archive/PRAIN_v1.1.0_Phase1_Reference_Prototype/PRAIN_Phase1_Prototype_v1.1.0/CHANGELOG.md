# Changelog

## 1.1.0 — 2026-10-20

- Added a typed `Observation` envelope and canonical content hashing.
- Added `PRAINRuntime` to compose observation intake, evidence, evaluation, policy, simulated execution and receipts.
- Added evaluator registry with fail-closed behavior for unknown evaluator names.
- Added simulated action receipts and idempotency-key replay.
- Added runtime vertical-slice tests for policy denial, success, idempotency, goal verification and evidence-chain integrity.
- Fixed evidence-ledger payload aliasing: appended payloads are copied so later caller mutation cannot silently invalidate an existing chain entry.
- Updated demo, interface contracts and run instructions.

## 0.1.0 — baseline

- Initial in-memory event bus, goal registry, CAS state store, deny-by-default policy gateway and hash-chain evidence ledger.
