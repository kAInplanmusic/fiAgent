# Step 24 — SQLite connection hygiene and process-test diagnostics

## Root cause fixed

`tests/test_durable_components.py::test_event_restart_marks_inflight_unknown` used
`with bus._db.connect() as c:`. Python's SQLite connection context manager commits
or rolls back a transaction but does **not** close the connection. The test now uses
the project's `_db.connection()` context manager, which explicitly closes the handle
in `finally`.

## Verification

- `test_durable_components.py`: 12 passed with `-W error::ResourceWarning`.
- `test_dispatcher.py`: 6 passed.
- `test_backup_bundle.py`: 4 passed.
- `test_runtime.py`: 15 passed.
- `test_sqlite_fault_recovery.py`: four tests complete successfully; the subprocess-termination test exceeds the execution environment's timeout.
- `test_durable_state_store.py`: multiprocessing CAS test exceeds the execution environment's timeout.
- Release verifier and ZIP integrity are checked independently after packaging.

## Remaining limitation

The complete suite is not marked green. The remaining timeouts occur in tests that launch subprocesses or multiple processes. They require a supported process-spawning environment or further isolated diagnosis. External actions remain simulated only.
