# Step 26 — coordinated restore rollback hardening

## Changes

- A restore destination may not overwrite the bundle manifest or a bundle database payload.
- Multi-database restore continues to validate checksums and SQLite integrity and stage every database before replacement.
- If a replacement fails, rollback is attempted in reverse replacement order.
- If rollback itself fails, the operation raises `restore_failed_and_rollback_incomplete` and retains the corresponding original-database rollback artifact. The exception text identifies the artifact path so an operator can recover it.
- Successful rollback consumes the rollback artifacts; normal successful restore removes them.
- Added injected-failure tests for successful rollback, failed rollback with recovery artifact retention, and destination/bundle alias rejection.

## Consistency contract

All writers must be stopped for the full backup or restore operation. SQLite's online backup API creates consistent snapshots per database, not one globally atomic snapshot across multiple databases. This step improves recoverability but does not claim a distributed transaction or power-loss atomicity across files.

## Validation

- `tests/test_backup_bundle.py`: 7 tests passed in the current validation run.
- The full test suite was attempted but exceeded the execution environment's 60-second limit while running process-level CAS tests. The environment also emits unrelated spreadsheet-runtime startup diagnostics for spawned Python processes. Full-suite status is therefore not claimed as PASS.
- Release identity, source syntax, manifest consistency and final ZIP integrity are checked separately during packaging.

## Operational recovery

If a restore reports `restore_failed_and_rollback_incomplete`, do not restart writers. Preserve the reported `.rollback-*.sqlite` file, inspect it with `PRAGMA integrity_check`, and restore it to the corresponding destination only after confirming the correct target mapping. Keep the original backup bundle untouched.
