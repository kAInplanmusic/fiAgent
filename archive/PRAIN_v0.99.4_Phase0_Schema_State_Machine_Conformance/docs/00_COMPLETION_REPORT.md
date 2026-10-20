# PRAIN v0.99.4 — Phase-0 semantic consistency revision (specification baseline v0.9.4)

**Status:** consolidated specification baseline; no runtime implementation.  
**Decision authority:** the user accepted the recommended direction in this conversation. The package records those defaults as the proposed normative baseline while preserving a change register.  
**Scope:** close the seven specification tracks using historical v0.2.1, v0.4.0, v0.5.0, v0.6, the prior v0.9.2 review, and the canonical knowledge base v0.3.0.

## Completion statement

This package provides concrete normative contracts, canonical JSON Schemas, migration decisions, a corrected knowledge-base source, policy/identity/evidence/HAL lifecycles, and reproducible specification-only tests. “Complete” means the written Phase-0 baseline and its deterministic offline checks are complete for this package. It does **not** mean a production implementation exists, live external systems were tested, sources were all fact-checked against the internet, a penetration test was performed, or an independent auditor signed the design.

## Seven workstream disposition

| # | Workstream | Deliverable | Package status |
|---:|---|---|---|
| 1 | Schema/contracts | 20-schema recursive inventory, 17 canonical v1.0.0 contracts, migration and compatibility policy | Complete as specification; runtime adapters deferred |
| 2 | Knowledge base | JSON↔HTML parity proof, item-level disposition rules, corrected independent PRAIN KB v0.3.0 | Complete as data/semantic curation; all 20 KB claims now have source-scoped assessments; live review limitations are explicit |
| 3 | Claim semantics | Canonical statuses, orthogonal status axes, transition rules, provenance/confidence rules and tests | Complete as specification |
| 4 | Distributed lifecycle | authority matrix, envelope/message rules, command/receipt lifecycle, CAS, dedup, unknown-outcome reconciliation | Complete as specification |
| 5 | Policy/approval | principal/tenant/delegation, action-bound approvals, revocation, fail-closed policy gateway | Complete as specification |
| 6 | Evidence/privacy | classification, retention, deletion propagation, integrity/signature/key lifecycle | Complete as specification; legal advice and deployment KMS validation not claimed |
| 7 | HAL/resilience | permitted/approval-required/forbidden repairs, recovery matrix, SLO policy, conformance suite | Complete as specification; no runtime resilience claim |

## Reproducible checks

The inherited v0.9.4 hardening adds a reference-oracle suite for all 30 invariant mappings; v0.99.4 adds an explicit semantic-consistency audit across the invariant map, verification boundaries, release metadata, and test counts and a dated source audit covering 19 official/primary source records and all 20 knowledge-base claims. The corrected coverage map separates specification-only checks from 26 future runtime-conformance obligations. Phase 0 can specify these rules but cannot truthfully assert a future runtime has passed them. The semantic audit also corrects stale deep-suite metadata to the executable count (237 checks), and adds a 497-check state-machine conformance suite and separates Phase-0 closure approval from any Phase-1 authorization.

Run `python tools/validate_phase0.py` from this directory. The validator checks all historical and canonical schemas at the meta-schema level, validates canonical fixtures, asserts strict schema boundaries, compares the embedded HTML database against the canonical JSON, checks source and relation references, and runs deterministic semantic invariants. It does not connect to services or execute agent actions.

## Phase-0 closure gate

The specification baseline is assembled and tests are expected to pass. The actual lifecycle remains `SPECIFICATION_COMPLETE_PENDING_FINAL_USER_RELEASE_APPROVAL` because version publication does not authorize Phase 1 or runtime implementation. No agent runtime/framework/OS code is included.


## Candidate status

This v0.99.4 package is a **closure candidate**, not a record of user approval. The underlying v0.9.4 specification baseline is carried forward with the KB version references corrected to v0.3.0. The release state remains `SPECIFICATION_COMPLETE_PENDING_FINAL_USER_RELEASE_APPROVAL`. Phase 1 remains blocked until explicit release approval is recorded.
