# Changelog

## 1.1.3 — 2026-10-20

- Serialize action admission with a process-local reentrant lock so concurrent same-key requests produce one receipt within this runtime instance.
- Track consumption of explicitly identified `single_use` approvals within the runtime process; reject reuse across different idempotency keys and require a stable `approval_id`.
- Added concurrency and single-use approval regression tests.
- Full unit suite: 30 tests passed.
- Critical limitation: these controls are process-local and in-memory; they do not provide multi-process/distributed atomicity, durable consumption, or authenticated approval identity.

## 1.1.3 — 2026-10-20

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

## 1.1.3 — durable admission primitives
- Added standalone SQLite-backed durable idempotency and single-use approval consumption.
- Added five tests for restart replay, fingerprint conflicts, single-use approvals, concurrent admission, and transaction rollback.
- Not yet wired into the main runtime; see docs/STEP8_SQLITE_DURABLE_ADMISSION.md.
