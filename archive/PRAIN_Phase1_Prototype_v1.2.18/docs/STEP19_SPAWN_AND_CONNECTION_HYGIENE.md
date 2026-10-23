# Step 19 — Spawn-safe multiprocessing and SQLite connection hygiene (v1.2.4)

## Changes
- Migrated the durable admission multi-process race test from `fork` to explicit `spawn`.
- Added three repeated four-process claim races; each round asserts exactly one worker claims the pending outbox item.
- Added deterministic SQLite write-failure injection with a trigger; failed insert leaves no partial row and preserves existing data.
- Fixed SQLite connection lifecycle in durable component and durable admission read/schema paths: context-managed operations now explicitly close connections.
- Narrowed `DurableStateStore.create()` conflict translation: only state-key uniqueness becomes `StateConflict`; other integrity failures propagate.
- Set durable component SQLite busy timeout from configured timeout rather than a hard-coded 10 seconds.

## Validation
- `PYTHONPATH=. python -m unittest discover -s tests`: 73 tests passed, 0 failed (about 11 seconds).
- Warning-enabled run passed all tests with no multiprocessing `fork` DeprecationWarning. Two `ResourceWarning` messages remain from paths outside the changes in this step; they are not suppressed and remain follow-up work.
- Tested on Python 3.13. No physical disk-full or hardware I/O failure was simulated.

## Limits
- `spawn` races validate process-level SQLite coordination on one host, not multi-host guarantees.
- Write-failure injection is deterministic SQLite-level failure, not a real filesystem-full condition.
- External side effects remain simulated only; no exactly-once external-effect guarantee is claimed.
- Overall audit status remains `PARTIAL_PASS` pending remaining resource warnings and broader storage/backup recovery criteria.
