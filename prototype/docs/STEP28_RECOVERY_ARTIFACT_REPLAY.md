# Step 28 — Recovery artifact replay and release identity

- Added `recover_database_from_artifact()` for a preserved SQLite rollback artifact after an incomplete coordinated restore.
- The artifact is integrity-checked, copied through a temporary database beside the destination, checked again, then atomically replaced. The recovery artifact is retained for audit/retry.
- Invalid artifacts fail before the destination is changed. Callers must stop writers and verify that the artifact belongs to the intended destination.
- Fixed README release identity to match this release.
- Limitation: this is single-database recovery from an operator-selected artifact, not automatic distributed rollback or a globally atomic multi-file transaction.
