# Step 13 — Durable versioned state store

**Version:** v1.1.8  
**Status:** `PARTIAL_PASS`

## Implemented

- Added opt-in `DurableStateStore`, backed by SQLite and JSON-serializable values.
- State survives closing/reopening the adapter and preserves monotonically increasing versions.
- `create` rejects duplicate keys; compare-and-swap rejects stale versions.
- SQLite write transactions serialize competing updates; four-process test confirms one CAS winner and three conflicts.
- Existing in-memory `StateStore` remains the default, preserving prior runtime behavior.

## API example

```python
from prain import DurableStateStore

store = DurableStateStore('/var/lib/prain/state.sqlite')
created = store.create('agent/context', {'mode': 'observe'})
updated = store.compare_and_swap('agent/context', created.version, {'mode': 'plan'})
assert updated.version == 2
```

Values must be JSON-serializable. The adapter is a local SQLite repository, not a distributed database. It is not automatically wired into `PRAINRuntime`; callers must opt in explicitly. Backups, schema migrations, file permissions, corruption recovery, and power-loss testing remain operational responsibilities.

## Verification

The complete suite passed **55 tests** including restart persistence, stale CAS, duplicate create and four-process CAS contention. The tests establish the behavior of this local adapter only.

## Remaining work

- Durable GoalRegistry lifecycle and verification records.
- Durable event inbox/deduplication with clear delivery semantics.
- Persistent hash-chained EvidenceLedger with tamper detection across restarts.
- Wire durable repositories behind explicit runtime configuration and add migration/backup tests.
- Authoritative approval identity and revocation; production security review.

No real external actions are performed. Production readiness and exactly-once external effects are not claimed.
