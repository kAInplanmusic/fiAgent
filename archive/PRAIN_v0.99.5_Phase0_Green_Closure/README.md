# PRAIN v0.99.4 Phase-0 Closure Candidate — Phase-0 Semantic Consistency Candidate

> **Release decision update (2026-10-20):** The release-level record in `release_status.json` supersedes the historical candidate gate below. Phase 0 is formally closed and the bounded local Phase-1 reference prototype is authorized to start. This package does not contain the Phase-1 runtime implementation and does not authorize production deployment or real external side effects. See `RELEASE_ATTESTATION.md` and `PHASE1_START_PLAN.md`.

This is the consolidated, runtime-agnostic PRAIN Phase-0 specification baseline. It carries forward v0.9.3, corrects and source-maps all 20 knowledge-base claims, checks 19 official/primary source records, extends deterministic reference-oracle conformance coverage for every registered invariant, and audits cross-document semantic consistency.

## Read in this order

1. `docs/00_COMPLETION_REPORT.md` — status and scope limits.
2. `docs/08_DECISION_REGISTER_FINAL.md` — accepted architectural defaults.
3. `docs/09_PHASE0_EXIT_CRITERIA.md` — 17 gates, including final user release approval.
4. `docs/17_SCHEMA_STATE_MACHINE_CROSSWALK.md` — state vocabularies, cross-field guards and negative conformance cases.
4. `docs/12_KNOWLEDGE_BASE_SOURCE_FACT_CHECK.md` — live source identity/scope review and all 20 claims.
5. `docs/01_SCHEMA_AND_MIGRATION_POLICY.md` and `docs/SCHEMA_FIELD_AUDIT_RECURSIVE.md` — schema baseline and migration rules.

## Verify locally

From this directory, run:

```bash
python tools/validate_phase0.py
python tools/verify_release_bundle.py --directory .
```

The combined offline run validates 20 historical schemas, 17 canonical contract schemas, fixtures and strictness, JSON↔HTML database parity, source/disposition coverage, all 30 registered invariant mappings and their verification boundaries, release-state semantics, cross-document semantics, and reference-oracle conformance for claim transitions, policy/approval binding, delegation, idempotency, unknown outcomes, CAS/authority, HAL, deletion, evidence, goal completion, delivery and runtime boundaries. Requires Python 3.10+ and `jsonschema`. No network access is required for the reproducible check.

## Latest candidate test totals

The schema/state-machine crosswalk suite is **65/65 PASS**. The deep reference-oracle suite is **237/237 PASS**. The new state-machine conformance suite is **497/497 PASS**, covering exhaustive allowed/forbidden edges and negative transition guards for claims, approvals, policy decisions, execution/reconciliation, goals, repair proposals and delegation. The combined main validator includes a wrapper check for the cross-document semantic-consistency suite and normative state-machine transition oracle; these are nested reports, so their counts must not be added together as if they were unique global tests.

## What PASS means

PASS means the package passes the included offline meta-schema, fixture, structure and normative reference-oracle checks. It does not prove that future runtime code implements the model, that real distributed failures behave correctly, that a cryptographic implementation is secure, or that the package is legally compliant. The live source review is documented as a dated, scoped literature/source check and is not an independent replication or comprehensive systematic review.

## Boundary

No agent runtime, operating system, broker, database, provider adapter, framework or production executor is included. Release state remains `SPECIFICATION_COMPLETE_PENDING_FINAL_USER_RELEASE_APPROVAL`; Phase 1 stays locked until a separate explicit closure approval.
