# 13. Invariant coverage and test boundary

All 30 registered invariants in `tests/invariants.json` map to test IDs in `tests/invariant_coverage.json`. `tools/validate_deep_conformance.py` implements spec-level reference oracles for deterministic rules and `tools/validate_phase0.py` invokes it. Tests do not execute a PRAIN runtime or claim distributed-system behavior has been demonstrated.

Coverage classes:

- **Schema/static:** JSON Schema Draft 2020-12 validity, strict unknown-field rejection, required tenant/provenance fields, conditional claim/execution/repair constraints.
- **Reference oracle:** allowed claim transitions, policy and approval binding, delegation narrowing, stable idempotency, unknown-effect reconciliation, CAS, authority class, HAL approval boundaries, deletion propagation, evidence authenticity separation and criterion-level goal completion.
- **Implementation gate:** conformance under concurrency, crash/restart, partitions, leases/fencing, actual key signing/rotation, persistence/restore, real authorization adapters, measured SLOs and deployment-specific legal retention. These remain mandatory implementation acceptance items, not undisclosed missing prose in Phase 0.

A test PASS means the oracle behaves as specified for its test vector. An independent implementation must later run the same conformance vectors against its own behavior.
