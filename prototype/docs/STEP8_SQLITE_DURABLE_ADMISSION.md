# Step 8 — SQLite durable admission primitives

Version: 1.1.3 (prototype extension).

## Implemented
- SQLite schema migration marker plus durable admission and single-use approval tables.
- `BEGIN IMMEDIATE` transactions, unique primary keys, busy timeout, WAL and `synchronous=FULL` for file-backed databases.
- Same idempotency key + same fingerprint returns the stored receipt; a changed fingerprint conflicts.
- Single-use approval consumption is persisted and serialized across store instances.
- Atomic rollback means a failed admission does not leave an approval consumed.
- Tests cover process/store re-instantiation, concurrent writers, key conflict and rollback.

## Critical boundary
`DurableAdmissionStore` is a standalone persistence primitive and is **not yet wired into `PRAINRuntime.request_action`**. Existing runtime behavior remains in-memory. The stored receipt is for simulated admission only. This does not make external side effects atomic, does not guarantee exactly-once execution, and does not solve cross-host database deployment. The next increment must integrate it behind a repository interface and add a transactional outbox plus crash/reconciliation tests before any real executor exists.

## Validation
`python -m unittest discover -s tests -v` — 35 tests passed in the local test run (30 prior tests + 5 new SQLite tests).
