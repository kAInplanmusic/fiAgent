# PRAIN v0.7.0 — Consolidated Traceability & Phase-0 Completion Specification

**Status:** specification release candidate; user review required. Phase 0 is NOT formally closed.
**Boundary:** design/specification only. No runtime, framework, OS integration, deployment, or production implementation is included.
**Purpose:** consolidate and trace the available artifacts through v0.6 without silently discarding earlier decisions, contracts, schemas, tests, or knowledge-base material.

## Canonical definition
P.R.A.I.N. = “quantum ready semantic Hamilton Interface & Orchestrator”.
- P — Perception (senses)
- R — Reason (brain)
- A — Anima (soul; explicit, inspectable, versioned self-model and continuity)
- I — Intention (will; goals, priorities, dependencies, acceptance criteria)
- N — Nerve (body; authorized execution through capability adapters)

PRAIN is an independent semantic and structured framework for autonomous agents. Hallerbans may use it, but is not part of PRAIN's definition. P/R/A/I/N are logical responsibilities, not a requirement for five separate processes. “Quantum-ready” means replaceable provider/compute interfaces, not a claim of quantum advantage.

## Included sections
- `docs/TRACEABILITY_MASTER.md` — cross-version source-to-concept traceability and change classification.
- `docs/DECISION_REGISTER.md` — carried-forward decisions, source, status, and open items.
- `docs/CONTRACT_CROSSWALK.md` — schema/interface lineage and reconciliation requirements.
- `docs/KNOWLEDGE_BASE_CROSSWALK.md` — first-pass mapping of the legacy JSON/HTML knowledge base to canonical P/R/A/I/N and cross-cutting concerns.
- `docs/PHASE0_GAPS_AND_EXIT.md` — closure gaps, exit criteria, and acceptance evidence.
- `docs/REFERENCE_FLOWS.md` — specification-level pseudocode for safe control and recovery.
- `docs/CONFORMANCE_MATRIX.md` — architecture-level test obligations and links to existing suites.
- `docs/VERSIONING_AND_CHANGE_POLICY.md` — rules for future schema and specification changes.
- `schemas/traceability-entry.schema.json` — machine-readable traceability record format.
- `tests/traceability-fixtures.json` — example entries for validating the traceability model.

## Interpretation
This release makes lineage and gaps explicit. It does not claim every open architectural decision is resolved, that every existing knowledge-base item has already been reconciled, or that any runtime passes these tests. Existing artifacts remain historical sources of truth for their own versions. Where this consolidation recommends a future resolution, it is labelled **PROPOSED**, not silently promoted to an approved decision.

## Artifact lineage
- Phase 0 v0.1.0 and v0.2.0: historical snapshots, preserve.
- Phase 0 v0.2.1: initial contracts, policy, ontology, schemas and reference tests.
- Architecture v0.4.0: semantic and reference architecture deepening.
- Distributed Protocol v0.5.0: distributed messaging, consistency and recovery contracts.
- Architecture v0.6: multiscale coordination, SCF, HAL, invariant/evidence boundary.
- Phase 1 prototype v0.1.0: separate historical reference prototype; not Phase-0 acceptance evidence.
- JSON and HTML knowledge bases: preserve and reconcile item-by-item; not replaced by this package.

## Immediate next step
Review open items in `docs/PHASE0_GAPS_AND_EXIT.md` with the user. Do not proceed to runtime work until an explicit Phase-0 acceptance record is approved.
