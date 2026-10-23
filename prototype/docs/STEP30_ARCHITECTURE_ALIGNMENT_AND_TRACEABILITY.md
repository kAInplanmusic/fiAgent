# Step 30 — architecture alignment and traceability

## Purpose

Stop adding persistence-only increments without checking the original PRAIN objective. Align the working prototype with the master archive through v0.6 and explicitly separate implemented foundations from architectural gaps.

## Changes
- Added `ARCHITECTURE_ALIGNMENT.md` with the canonical P/R/A/I/N definition, four planes, L0–L3 scales, SCF, HAL and the invariant/evidence boundary.
- Added `REQUIREMENT_TRACEABILITY.md` mapping Phase 0 v0.2.1, Architecture v0.4, Distributed Protocol v0.5 and Architecture v0.6 requirements to current implementation evidence and gaps.
- Updated interface contracts and implementation status to v1.2.15; removed stale version labels from those documents.
- Recorded explicit non-claims: Phase 0 remains open; SCF, integrated Anima and HAL are not implemented; external actions remain simulated.
- Added documentation regression tests for core architecture terms, phase-closure status and explicit open gaps.

## Validation

The complete discovered unittest suite and release checks were run after the documentation and manifest updates. Exact counts and elapsed time are in `tests/test-report.txt` and `MANIFEST.json`.

## Outcome

This is a roadmap/traceability correction, not a claim of new runtime intelligence. The next work should close source-level contracts and then implement the semantic model and SCF before HAL. No new infrastructure or production adapter is justified until the relevant contracts and conformance criteria are stable.
