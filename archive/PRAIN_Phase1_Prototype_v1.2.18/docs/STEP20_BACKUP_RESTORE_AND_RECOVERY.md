# Step 20 — Validated SQLite Backup and Restore (finalized)

## Implemented and verified
- `DurableStateStore.backup_to(destination)` uses SQLite's online backup API, refuses to overwrite an existing destination, and verifies integrity plus the required `prain_state` columns before reporting success.
- `DurableStateStore.restore_from(backup_path, destination, timeout=...)` validates source integrity/schema, copies through a temporary database in the destination directory, validates the copied schema and integrity, then atomically replaces the destination path.
- Restore rejects missing, corrupt, schema-missing, and schema-incompatible backups before replacing an existing destination.
- Failed backup attempts remove the partial destination file.
- Six focused backup/restore tests pass. The full suite passes 79/79.

## Operational requirements and limits
- Stop application writers before restore. Atomic replacement protects against partial-copy replacement, but does not coordinate with already-open connections or external processes.
- This restores the `DurableStateStore` database file only. It does not coordinate separate databases used for admissions, goals, event delivery, or evidence.
- Keep backups on a separate storage failure domain for disaster recovery. A backup on the same device does not protect against device loss.
- This does not simulate a physically full disk or hardware I/O failure.
- A successful SQLite integrity check does not prove that storage hardware honors durability guarantees.
- One existing ResourceWarning remains in other SQLite component/admission code and is not treated as resolved by this step.
- No production or exactly-once external-action guarantee is implied.
