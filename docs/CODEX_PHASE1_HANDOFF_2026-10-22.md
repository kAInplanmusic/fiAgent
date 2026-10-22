# Codex handoff — Phase 1 integration audit (2026-10-22)

## Authoritative baseline
Repository `kAInplanmusic/fiAgent`, `main` as of `6b702ff4a1ce65796f9cbfbe8a54424072453781`. Do not replace or rewrite its archived source, Phase-0 closure evidence, manifests or historical records.

## Incoming local candidate
A separate local Phase-1 prototype `PRAIN_Phase1_Prototype_v1.2.18.zip` exists in the PRAIN ChatGPT project working environment. **It has not been uploaded to this branch**. Its reported 105/105 tests are local, not GitHub CI proof. Request or import the actual archive before any source-level merge. Do not reconstruct files from claims.

## Mandatory Codex work
1. Inventory repository architecture, archives, Phase-0 closure and existing CI. Read `MASTER_README.md`, `ROADMAP.md`, `docs/PHASE0_GREEN_CLOSURE.md`, `MASTER_MANIFEST.json` and all relevant tests.
2. Compare incoming v1.2.18 source against existing `archive/PRAIN_v1.1.9_Phase1_Reference_Prototype/` by file, API, behavior, schema, test and provenance. Identify upstream features to preserve. Never overwrite silently.
3. Implement missing Phase-1 requirements in isolated PRs: semantic entities/provenance, SCF, policy-governed routing, authorized Nerve, Anima, HAL, distributed recovery, cache privacy and Hamilton/Burr/MMAC adapter boundaries.
4. Add deterministic tests and CI checks for schemas, concurrency, CAS, replay/idempotency, unknown outcomes, privacy/redaction/deletion, backup/restore and evidence-based goal completion.
5. Maintain source-to-requirement traceability, decision log, changed-file SHA256 manifest, reproducible test commands and verified test output.
6. Mark phase complete only when **every** acceptance criterion has executable evidence and independent verification. No invented green status. Production readiness remains separate.

## Parallel agent ownership
A: source inventory and architecture/traceability; B: semantic model/SCF; C: routing/Hamilton/MMAC integration; D: security/recovery; E: independent test/CI/release verification. Each agent uses its own branch and opens a PR; integrator reconciles conflicts and verifies final combined tree.

## Immediate acceptance gate
- Repository baseline and incoming prototype compared.
- CI reproduces tests on GitHub.
- No regressions, untracked required files or unauthorized change to archived history.
- Explicit list of still-open criteria and exact verification evidence.

This is a **handoff document**, not evidence that Codex or subagents have started.
