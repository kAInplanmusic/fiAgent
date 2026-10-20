# Changelog

## 1.1.1 — 2026-10-20

- Reject approval records explicitly marked denied, consumed, rejected, or revoked.
- Check `valid_from`, `max_uses`, and `usage_count` when those canonical lifecycle fields are supplied.
- Deep-copy nested observation/action payloads at intake to avoid caller-side mutation aliasing.
- Added runtime regression tests for revoked/consumed/future approvals and nested payload mutation.
- Full unit suite: 27 tests passed.
- Scope remains an in-memory single-process reference prototype; approval consumption is not atomic or persisted, and full canonical approval-schema enforcement is not claimed.

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
