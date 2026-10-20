# 13. Release, approval, and change-control protocol

## 13.1 Three separate states

1. **Specification candidate** — artifacts and deterministic checks are assembled. This is the current v0.99.3 state.
2. **Phase-0 closed** — the user has explicitly approved closure of the specification baseline, with the exact ZIP SHA-256 and validation report recorded.
3. **Phase-1 authorized** — the user has separately authorized implementation scope. This is not implied by either candidate creation or Phase-0 closure.

These states must not be collapsed into a single `complete` flag.

## 13.2 Closure checklist

- [ ] Confirm the candidate version and exact ZIP SHA-256.
- [ ] Re-run `python tools/validate_phase0.py` from the unpacked package.
- [ ] Confirm the manifest file inventory and checksums match the package contents.
- [ ] Review all documented scope limitations and deferred deployment decisions.
- [ ] Record explicit user approval with date/time, candidate hash, validator result, and any accepted exceptions.
- [ ] Change lifecycle status only after the approval record exists; preserve the prior candidate and its hash.

## 13.3 Change control

Any normative change after approval creates a new versioned candidate, a change log entry, regenerated manifest/checksums, and a complete validator run. Never mutate an approved artifact in place. A changed ZIP hash requires a new approval for that exact artifact.

## 13.4 Phase-1 authorization checklist

Before implementation begins, obtain a separate explicit authorization defining at minimum: in-scope deliverables, prohibited work, target environment (if now selected), acceptance tests, data handling constraints, and the authority to perform external side effects. Runtime/framework/OS choices remain deferred until this separate authorization.

## 13.5 Current status

`SPECIFICATION_COMPLETE_PENDING_FINAL_USER_RELEASE_APPROVAL`

`phase1_authorized = false`

The included offline checks are specification conformance checks only. They are not a runtime, security, legal, or production-readiness certification.

## 13.6 Verification-boundary semantics

`tests/invariant_coverage.json` reports specification coverage separately from future implementation conformance. `phase0_status = specification-coverage-only` means the normative example/reference rule is tested in this package; it does not mean a future implementation passed. `runtime_conformance_still_required = true` applies to runtime-behavior invariants. A false value is allowed only where the boundary is explicitly classified as `build-artifact`, `architecture-conformance`, `specification-claim`, or `release-package-inventory`. Those are still subject to their corresponding Phase-0/build/release checks; the false runtime flag is not a claim that the rule is unimportant or already runtime-tested.
