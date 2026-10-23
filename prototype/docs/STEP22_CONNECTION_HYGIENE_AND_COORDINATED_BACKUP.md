# Step 22 — SQLite connection hygiene and coordinated database bundles

## Changes
- SQLite connection context managers in `DurableStateStore` backup/restore paths now explicitly close handles. Python's `sqlite3.Connection` context manager commits/rolls back but does **not** close the connection.
- Added `backup_databases()` and `restore_databases()` for a named set of SQLite files. Backup uses SQLite's online backup API, validates each backup, and emits a SHA-256 manifest.
- Restore validates the complete bundle and all checksums before modifying destinations, stages all database copies, and attempts rollback if a filesystem replacement fails.
- Tests cover round-trip across multiple databases, checksum tampering, destination-set mismatch, and overwrite/duplicate-source rejection.

## Required operating contract / limits
- Stop/quiesce all writers for the entire bundle backup or restore. The bundle is a set of consistent per-file snapshots, **not** a cross-database transactional snapshot while writes continue.
- Filesystem rename is atomic per file, not across all database files. Restore stages all files first and performs best-effort rollback, but a power loss during multi-file replacement can still leave a mixed generation. Retain an independent backup and use an application-level maintenance window.
- Each database is integrity-checked with `PRAGMA integrity_check`; domain-specific schema compatibility is not inferred for arbitrary named databases.
- `:memory:` databases are not supported by the bundle API; provide actual database file paths.
- No external action is performed. Production-grade crash-atomic multi-database recovery requires a journaled generation-pointer design or a single database/transaction boundary.

## API
```python
from prain import backup_databases, restore_databases

backup_databases({
    "runtime": "/var/lib/prain/runtime.sqlite3",
    "admission": "/var/lib/prain/admission.sqlite3",
}, "/var/backups/prain-2026-10-21")

restore_databases(
    "/var/backups/prain-2026-10-21",
    {
        "runtime": "/var/lib/prain/runtime.sqlite3",
        "admission": "/var/lib/prain/admission.sqlite3",
    },
)
```

Step status: implementation added; test status is recorded in `tests/test-report.txt` and `MANIFEST.json`.
