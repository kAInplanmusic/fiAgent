# PRAIN v0.99.1 — Phase-0 semantic consistency candidate

**Status:** `SPECIFICATION_COMPLETE_PENDING_FINAL_USER_RELEASE_APPROVAL`

## Candidate basis
- Baseline: PRAIN v0.9.4 Phase-0 Deep Conformance Specification.
- Baseline ZIP SHA-256 (v0.9.4): `c7365727e3c8a950167aed155ef9e05c9824602bf555f0325e6fa563ae749ebe`
- Main offline validator: 119/119 checks PASS.
- Nested deep conformance/reference-oracle suite: 219/219 checks PASS.
- Canonical schemas: 17; historical schemas meta-validated: 20.
- Runtime/framework/OS implementation included: no.

## Semantic consistency corrections in v0.99.1
- Corrected the deep conformance result from the stale 218/218 metadata to 219/219, matching the executable report.
- Corrected the invariant verification-boundary map: 26 runtime invariants explicitly require later implementation conformance tests; four non-runtime invariants are assigned to build, architecture, specification-claim, or package-inventory checks.
- Split closure attestation from Phase-1 implementation authorization so one cannot implicitly authorize the other.
- Added cross-document consistency checks and a release-bundle verifier.

## Scope of this candidate
This candidate consolidates the written Phase-0 baseline and its release gate. It does not claim runtime correctness, deployment readiness, production security, legal compliance, independent external audit, or that all source claims have been independently verified against live sources.

## Phase-0 disposition
The seven specification workstreams are complete as written artifacts under the stated specification-only scope. The package is ready for final user review, but not self-authorizing: archive creation, tests, and prior acceptance of design defaults do not equal explicit authorization to begin Phase 1.

## Required next action
The user must explicitly approve Phase-0 closure/release. Record that approval using `RELEASE_ATTESTATION_TEMPLATE.md`. Until then, do not begin runtime/framework/OS implementation.
