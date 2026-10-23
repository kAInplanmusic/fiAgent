# Step 25 — Process-test diagnosis and release verifier fix

## Diagnosis

The process-level tests previously reported as timing out completed when run individually in this environment. The durable state store spawn/CAS test completed in under 3 seconds, and all five SQLite fault-recovery tests completed in under one second. This points to an intermittent/environmental timeout rather than a reproducible product deadlock. The tests and their failure scenarios are retained.

## Defect fixed

The full suite exposed a deterministic release-verifier failure: after Python tests import modules, the interpreter may create `__pycache__` files in the source tree. The verifier correctly excluded bytecode from the manifest comparison but then incorrectly treated those transient runtime caches as release files that must cause failure. It now ignores bytecode for tree/manifest comparison. The release packaging step separately removes all `__pycache__`, `.pyc`, and `.pyo` files, and the final ZIP is checked to contain none.

## Validation

- Focused durable-state-store module: 4 passed, including spawn-based multi-process CAS.
- SQLite fault-recovery module: 5 passed, including subprocess termination/rollback.
- Full suite: recorded in the release manifest after the final run.
- Release verifier and archive integrity: run after packaging.

## Scope limits

External actions remain simulated only. Passing these tests does not establish production readiness or power-loss durability across multiple database files.
