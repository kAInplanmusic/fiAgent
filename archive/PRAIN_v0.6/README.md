# PRAIN v0.6 — Multiscale Semantic Coordination Architecture

**Status:** architecture/specification package; not a deployed runtime.  
**Version:** 0.6.0  
**Supersedes:** none. This is a compatible architectural deepening of the v0.5 distributed protocol, not a claim that v0.5 has been implemented.

## Core thesis

> Global meaning. Local intelligence. Selective synchronization. Continuous feedback. Evidence-backed outcomes.

PRAIN is a semantic control plane connecting observations → beliefs → goals → plans → policy-checked actions → verified evidence and state updates.

The five functional dimensions remain:
- **P — Perception:** normalize observations and preserve provenance and uncertainty.
- **R — Reason:** interpret, infer, compare, plan, and evaluate alternatives.
- **A — Anima:** maintain an explicit, inspectable, versioned self-model and continuity record; this is not a claim of consciousness and is not the sole origin of identity.
- **I — Intention:** define goals, priorities, dependencies, and acceptance criteria.
- **N — Nerve:** execute authorized actions through capability adapters.

The v0.6 addition is a *multiscale coordination model* plus a system-wide **Homeostasis & Adaptation Layer (HAL)**. These are architectural responsibilities, not a sixth core or a requirement for six separate services.

## Package map

- `spec/ARCHITECTURE.md` — planes, scales, boundaries, and reference topology.
- `spec/COORDINATION_PROTOCOL.md` — semantic messages and recipient decision rules.
- `spec/CONSISTENCY_AND_CONFLICTS.md` — what must be authoritative vs locally divergent.
- `spec/HOMEOSTASIS_ADAPTATION.md` — HAL feedback, repair, adaptation, and hard limits.
- `spec/IDENTITY_AND_LINEAGE.md` — self-model, provenance, versioning, lineage.
- `spec/FAILURE_AND_RECOVERY.md` — uncertain outcomes, repair, replay, and safe retries.
- `spec/CONFORMANCE_TESTS.md` — minimum adversarial/fault-injection suite.
- `schemas/semantic-message.schema.json` — message contract.
- `schemas/health-signal.schema.json` — HAL signal contract.
- `schemas/repair-proposal.schema.json` — repair/adaptation proposal contract.
- `tests/invariants.json` — machine-readable invariant catalogue.
- `plans/IMPLEMENTATION_PLAN.md` — implementation order and exit criteria.
- `DECISIONS.md` — explicit design decisions and unresolved choices.
- `TRACEABILITY.md` — relation to v0.5 protocol.

## Design constraints

1. P/R/A/I/N are functional dimensions; local unit, group, global semantic system, and invariant/control are organizational scales.
2. Not all information is globally synchronized. Authority and consistency are declared per record type.
3. Hypotheses may coexist. Conflicting authoritative facts require explicit reconciliation; no silent last-writer-wins for semantic truth.
4. HAL may observe, recommend, allocate within bounds, and initiate bounded repairs. It cannot grant itself permissions, bypass policy, or rewrite authoritative evidence.
5. External side effects with ambiguous outcomes must be reconciled before retry.
6. Completion requires independently checkable evidence for every required acceptance criterion.
7. Biological and processor analogies are design inspiration, not claims of biological equivalence or quantum advantage.
8. The first implementation should be a modular monolith/single-host core with replaceable adapters. Split into services only when measured constraints justify it.

## Validation

The JSON schemas are intended for Draft 2020-12 validators. The invariant and conformance lists define expected behavior; they do not by themselves prove a runtime conforms.
