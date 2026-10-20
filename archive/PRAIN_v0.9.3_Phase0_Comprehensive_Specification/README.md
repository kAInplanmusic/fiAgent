# PRAIN v0.9.3 — Comprehensive Phase-0 Specification

This is the comprehensive runtime-agnostic specification baseline created after the user accepted the proposed architectural defaults. It closes the written design gaps across seven workstreams and includes 17 canonical JSON Schemas, corrected canonical knowledge-base JSON/HTML, historical audit detail, migration rules, policy/identity/evidence/HAL lifecycles, invariant registry and an offline validator.

## Start here

1. `docs/00_COMPLETION_REPORT.md` — what is complete and what the completion claim means.
2. `docs/08_DECISION_REGISTER_FINAL.md` — adopted normative defaults and deliberately deferred deployment choices.
3. `docs/09_PHASE0_EXIT_CRITERIA.md` — acceptance matrix and release state.
4. `docs/01_SCHEMA_AND_MIGRATION_POLICY.md` and `docs/SCHEMA_FIELD_AUDIT_RECURSIVE.md` — historical and canonical contracts.

## Verify

From this folder run:

```bash
python tools/validate_phase0.py
```

The script has no network dependency and does not execute an agent/runtime action. Requires Python 3.10+ and `jsonschema` installed. It writes `audit/validation_report.json`.

## Scope boundary

No agent runtime, operating system, broker, database, production adapter, credential provider, or framework is implemented here. Those choices remain behind specified contracts. Specification-level PASS is not a production readiness or legal compliance certification.
