# PRAIN — fiAgent repository

This repository imports the PRAIN master project archive as a source-controlled baseline.

## Current baseline

- Phase 0: specification/release package baseline documented in `docs/PHASE0_GREEN_CLOSURE.md`.
- Phase 1 reference prototype: `archive/PRAIN_v1.1.9_Phase1_Reference_Prototype/`.
- Runtime and production readiness are separate gates; archived test reports are historical evidence, not a substitute for a fresh CI run.

## Run Phase 1 tests locally

```bash
python -m pip install --upgrade pip pytest
cd archive/PRAIN_v1.1.9_Phase1_Reference_Prototype
python -m pytest -q
```

## CI

GitHub Actions runs the Phase 1 prototype test suite on pushes and pull requests. The workflow is intentionally scoped to the canonical v1.1.9 prototype until Phase 1 is promoted to a root-level package.

## Integrity

`MASTER_MANIFEST.json` and `SHA256SUMS` are imported historical project artifacts. Any source changes should update the manifest and hashes as part of the release process; do not treat the imported hashes as current after editing files.
