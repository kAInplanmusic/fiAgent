# 14. Semantic consistency audit — v0.99.3

## Findings corrected

### SC-001 — Deep-suite count drift

The prior release metadata recorded 219 deep-conformance checks, while the executable reference-oracle report contains 237 checks. The candidate now records the executable count and tests the report's count against its payload length and release gate metadata.

### SC-002 — Verification-boundary misclassification

The previous invariant coverage file set `runtime_conformance_still_required = false` for several behavioral invariants while its own notes correctly stated that a reference oracle does not prove a future runtime implements a rule. The field is now boundary-specific: 26 invariants require future runtime-conformance testing; four are explicitly classified as build-artifact, architecture-conformance, specification-claim, or release-package-inventory checks. All 30 still have specification-level test mappings.

### SC-003 — Phase-0 / Phase-1 authorization conflation

The prior release attestation template offered a combined decision that could authorize Phase-1 implementation at the same time as Phase-0 closure, contradicting the release protocol. The revised template records Phase-0 closure and Phase-1 implementation authorization as separate decisions. Phase-0 approval alone does not permit runtime work.

## Automated cross-consistency checks

`tools/validate_semantic_consistency.py` checks the one-to-one invariant/coverage map, exact registry cardinality, reference-test IDs, verification boundaries, P/R/A/I/N dimension mapping, candidate versioning, test counts and release-state separation.

`tools/verify_release_bundle.py` validates manifest membership, file sizes and SHA-256 values, report-to-integrity agreement, release-gate status, ZIP CRC and, when passed the external integrity JSON, final archive hash and byte count.

Run from the package directory:

```bash
python tools/validate_phase0.py
python tools/verify_release_bundle.py --directory .
```

To verify a published archive and its external hash record:

```bash
python tools/verify_release_bundle.py --directory . --archive ../PRAIN_v0.99.3_Phase0_Semantic_Consistency.zip --integrity ../PRAIN_v0.99.3_integrity.json
```

## Scope boundary

These checks evaluate the written specification and release artifacts. They do not execute agent actions, prove a future runtime complies, establish operational security, substitute for legal review, or independently reproduce claims against external sources.
