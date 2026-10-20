# 9. Phase-0 exit criteria and honest release status

## 9.1 Specification completeness criteria

Phase-0 specification is considered document-complete only when each item below has an artifact and a passing deterministic check where possible.

| Gate | Required evidence | v0.99.3 candidate disposition |
|---|---|---|
| G01 Artifact lineage | Historical archives, checksums, manifest and source report | Included; archive integrity checked |
| G02 KB parity | Recursive JSON↔HTML comparison; no dangling refs | Included and tested; corrected v0.3.0 KB supplied |
| G03 KB semantic independence | Hallerbans not foundational; dimension mappings and authority relations corrected | Included in canonical KB and docs |
| G04 Recursive schema audit | All 20 schemas, nested field constraints and meta-schema validation | Included; 20/20 meta-schema PASS |
| G05 Canonical schema baseline | Versioned contracts with strictness and conditional invariants | 17 canonical schema files; fixture validation |
| G06 Migration policy | Family-by-family mapping, lossy/default/rejection rules | Included; executable migration adapters intentionally deferred |
| G07 Claim ontology | Orthogonal statuses, transitions and evidence rules | Included; deterministic semantic tests |
| G08 Identity/tenancy | Principal/tenant/delegation schema and isolation invariants | Included |
| G09 Authority/consistency | Per-record source-of-truth, consistency and conflict disposition | Included |
| G10 Policy/approval | Gateway, binding, expiry, revocation, TOCTOU, default deny/defer | Included |
| G11 Evidence/privacy | Integrity, keys, classification, retention and deletion propagation | Included; legal review/KMS deployment tests are not part of spec-only gate |
| G12 HAL | Repair catalogue, approval boundaries, bounds, rollback | Included |
| G13 Failure/recovery | Duplicate, reorder, crash, timeout-after-side-effect, partition, restore | Included as matrix and tests specification |
| G14 Conformance | Canonical fixture suite, strictness, KB parity and invariants | Included; validator runnable offline |
| G15 Versioning/change | Schema/semver/migration and history policy | Included |
| G16 Runtime boundary | No runtime/framework/OS implementation in package | Confirmed by package content inventory; spec validator only |
| G17 Final release authorization | Explicit user authorizes transition beyond Phase 0 | **Not implied by this package** |

## 9.2 What “complete” does and does not mean

This is a complete written baseline for Phase 0. Automated checks can verify file structure, JSON Schema validity and defined deterministic rules. They cannot establish correctness of a future distributed runtime, real provider integrations, operational security, legal compliance, source freshness, or production SLO attainment. Those are explicit later gates, not hidden unfinished Phase-0 writing tasks.

## 9.3 Release state

`SPECIFICATION_COMPLETE_PENDING_FINAL_USER_RELEASE_APPROVAL`

No Phase-1 runtime/framework/OS work may begin on the strength of this state alone. A future closure record must reference the package hash, validator report, decision register version and explicit approval. The v0.99.3 semantic-consistency candidate has been assembled, but it is not a closure record. If the user authorizes closure, append a signed/dated approval attestation referencing the exact candidate ZIP SHA-256 and validator report. Phase 1 still requires a separate explicit implementation authorization; closure approval alone must not silently authorize runtime/framework/OS work.
