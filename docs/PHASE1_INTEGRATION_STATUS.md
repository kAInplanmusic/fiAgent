# Phase 1 integration — 2026-10-23

Current source candidate: `archive/PRAIN_Phase1_Prototype_v1.2.18`.
Preserved baseline: `archive/PRAIN_v1.1.9_Phase1_Reference_Prototype`.
Overall status: **PARTIAL_PASS; Phase 1 remains open**.

The uploaded v1.2.18 source is imported byte-for-byte. Its ZIP SHA256,
per-file hashes, baseline hashes and file comparison are in `phase1-import.json`.
Existing archives and historical manifests are preserved.

## Reproduction

From the root run `python tools/verify_phase1_import.py`.
In each prototype run `python -W default -m unittest discover -s tests -v`.
In v1.2.18 also run `python tools/verify_release.py`.
GitHub Actions runs these commands in isolated matrix jobs on Python 3.12.
No external model, credential or paid service is needed for these tests.

Fresh local verification on 2026-10-23 with Python 3.12:
v1.1.9 **59/59 PASS**, v1.2.18 **105/105 PASS**, candidate release inventory
**66/66 PASS**, exact SHA256 verification **PASS**, `git diff --check` **PASS**.
GitHub execution is a separate pending check until its run completes successfully.
The file comparison finds **32 added, 15 changed, 20 unchanged, 0 removed**
files between prototype versions (including their manifests).

## Decisions and known discrepancies

- Preserve both source versions for API, behavior and provenance comparisons.
- v1.2.18 adds persistent runtime state wiring, explicit event delivery outcomes,
  crash/recovery and backup/restore tests, and policy-filtered routing.
- File comparison is recorded mechanically; passing tests only establishes their
  tested scope, not universal behavioral compatibility.
- Candidate documentation has stale values: implementation status v1.2.16,
  package version 1.2.7, and Phase-0 acceptance claims conflicting with the
  repository's v0.99.6 closure. These are upstream defects retained in the
  exact import. This document is the current integration status.
- Phase 0 is specification-closed per `PHASE0_GREEN_CLOSURE.md`. Its historical
  NOT_AUTHORIZED record predates the user's authorization of Phase-1 development.
- `MASTER_MANIFEST.json` and `SHA256SUMS` remain historical snapshots;
  `phase1-import.json` verifies the source trees for this integration.

## Open acceptance gates

| Gate | Evidence required before closure |
|---|---|
| GitHub CI | Successful run on integrated commit |
| Semantics | Canonical schemas, claim transitions, provenance and negative tests |
| SCF | Conflicts, freshness and selective invalidation |
| Goals | Independent evidence per criterion, strict boolean and nonempty references |
| Evidence | Concurrent ledger instances preserve the hash chain |
| Events | Worker fencing, payload identity and crash reconciliation |
| Policy/Nerve | Revocation, tenant/principal binding and dispatch-time checks |
| Router | Nonfinite inputs, authorized cache, budget/fallback and regions |
| Anima/HAL | Versioned self-model, bounded repairs, cooldown and rollback |
| Privacy | Deletion/redaction propagation through caches and evidence |
| Enterprise | DAG validation, resume, MMAC, lineage and measured benchmarks |
| Traceability | Every retained requirement mapped to executable evidence |

Existing tests passing does not close these gates. Step 32 R1–R14 requirements
have documentation checks, not full runtime coverage. Production readiness
remains separate.
