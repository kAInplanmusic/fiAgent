# Step 29 — Persistence chain efficiency and snapshot consistency

## Change
The coordinated backup/restore path now uses one internal `_sqlite_snapshot()` helper for backup payloads, staged restore databases, and pre-restore rollback copies. This removes duplicated connection/backup/integrity logic and ensures rollback copies are SQLite snapshots rather than raw file copies. That matters for SQLite databases configured with WAL mode: committed data can reside in the WAL sidecar, so copying only the main database file is not a reliable snapshot strategy.

## Validation
- Added regression test: a WAL-mode database's committed row survives bundle backup and restore.
- Added regression test: rollback snapshot is valid and the original destination remains unchanged after an injected restore replacement failure.
- Targeted backup-bundle tests: 11 passed, 0 failed.
- Full suite: independent run exceeded the 45-second verification window in this environment; no full-suite pass is claimed.
- Release verifier, Python compilation, and archive CRC are checked on the produced release.

## Operational contract and limits
- Stop all writers across the entire set of databases before backup or restore. Per-file snapshots are not a distributed transaction.
- Cross-file replacement cannot be globally atomic on ordinary filesystems. Rollback is best effort; if rollback itself fails, recovery artifacts must be preserved and used by an operator.
- This step improves snapshot correctness and code-path consistency; it does not claim a measured performance percentage without a controlled benchmark.
