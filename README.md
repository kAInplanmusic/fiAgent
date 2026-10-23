# PRAIN — fiAgent repository

This repository imports the PRAIN master project archive as a source-controlled baseline.

## Current baseline

- Phase 0: specification/release package baseline documented in `docs/PHASE0_GREEN_CLOSURE.md`.
- Phase 1 candidate: `archive/PRAIN_Phase1_Prototype_v1.2.18/`.
- Preserved baseline: `archive/PRAIN_v1.1.9_Phase1_Reference_Prototype/`.
- Current status and open gates: [integration report](docs/PHASE1_INTEGRATION_STATUS.md).
- Runtime and production readiness are separate gates; archived test reports are historical evidence, not a substitute for a fresh CI run.

## Run Phase 1 tests locally

```bash
python tools/verify_phase1_import.py
cd archive/PRAIN_Phase1_Prototype_v1.2.18
python -W default -m unittest discover -s tests -v
python tools/verify_release.py
```

## CI

GitHub Actions tests v1.1.9 and v1.2.18 separately on Python 3.12, verifies their hashes, and checks the candidate inventory. Passing existing tests does not close all Phase-1 requirements.

## Integrity

`MASTER_MANIFEST.json` and `SHA256SUMS` are historical snapshots. The current import provenance, exact inventories and comparison are in `docs/phase1-import.json`; verify them using `python tools/verify_phase1_import.py`.
