# Contributing

1. Make changes on a feature branch.
2. Run the Phase 1 test suite from `archive/PRAIN_v1.1.9_Phase1_Reference_Prototype`.
3. Do not change release status labels or historical test reports to make a gate appear green.
4. For release-affecting changes, regenerate and verify `MASTER_MANIFEST.json` and `SHA256SUMS`.
5. Record any unimplemented runtime invariants as open; do not imply production readiness from unit tests alone.
