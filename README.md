# PRAIN — fiAgent repository

This repository imports the PRAIN master project archive as a source-controlled baseline.

## Current baseline

- Phase 0: specification/release package baseline documented in `docs/PHASE0_GREEN_CLOSURE.md`.
- Phase 1 working candidate: `prototype/` (v1.2.19).
- Exact imported source: `archive/PRAIN_Phase1_Prototype_v1.2.18/`.
- Preserved baseline: `archive/PRAIN_v1.1.9_Phase1_Reference_Prototype/`.
- Current fixes and verification: [Step 34](prototype/docs/STEP34_RUNTIME_HARDENING.md).
- Integration provenance and wider open gates: [integration report](docs/PHASE1_INTEGRATION_STATUS.md).
- Runtime and production readiness are separate gates; archived test reports are historical evidence, not a substitute for a fresh CI run.

## Run Phase 1 tests locally

```bash
python tools/verify_phase1_import.py
cd prototype
python -W default -m unittest discover -s tests -v
python tools/verify_release.py
```

## CI

GitHub Actions tests v1.1.9, v1.2.18 and the active prototype separately on Python 3.12, verifies archived source hashes, and checks the active candidate's exact inventory and hashes. Passing these tests does not close all Phase-1 requirements.

## Integrity

`MASTER_MANIFEST.json` and `SHA256SUMS` are historical snapshots. The current import provenance, exact inventories and comparison are in `docs/phase1-import.json`; verify them using `python tools/verify_phase1_import.py`.
