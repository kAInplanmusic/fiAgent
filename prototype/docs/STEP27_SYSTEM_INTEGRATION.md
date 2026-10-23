# Step 27 — End-to-end persistence integration

## Scope
This step validates the persistence chain across five independent SQLite files: versioned state, goals, events, evidence, and admission/outbox. It checkpoints the files, introduces drift after the checkpoint, restores the bundle, reopens each component, and verifies the restored state.

## Consistency contract
The caller must stop all writers for the complete backup and restore window. `backup_databases` uses SQLite's online backup API for each file, but it is not a distributed transaction. No claim of a globally atomic snapshot is made while writers are active.

## Failure behavior
The integration test also removes a bundle payload and verifies restore fails before changing destination data. Cross-file replacement is still best-effort rollback rather than a single filesystem atomic transaction; retain an independent backup and use a maintenance window.

## Test status
See `MANIFEST.json` and `tests/test-report.txt` for actual execution results. Do not interpret targeted integration success as proof of production readiness.
