# PRAIN — Phase 1 executable reference prototype

Version `1.2.19` · Step 34 · Python 3.12 tested · Standard library only.

P.R.A.I.N. means **Perception, Reason, Anima, Intention, Nerve**. These are logical responsibilities across a semantic control plane, not five required services. PRAIN is independent of Hallerbans. “Quantum-ready” means replaceable provider/compute interfaces; it does not claim quantum computing or quantum advantage.

## Current executable slice

- Typed observation intake, event publication and evidence recording.
- Named evaluator registry; unknown evaluator fails closed.
- Deny-by-default policy evaluation with action/target/capability matching and optional approval binding.
- Simulated-only action execution with idempotency key and receipt replay.
- Goal lifecycle with explicit evidence-backed verification.
- Versioned state and compare-and-swap; optional SQLite-backed state, goals, events, admission/outbox and evidence.
- Conservative unknown-outcome reconciliation and multi-database backup/recovery reference path.
- Unit, process, concurrency, fault-recovery and release-integrity tests for the implemented scope.

## Run

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v
python -m prain.demo
python tools/verify_release.py
```

No third-party dependencies or network access are required.

## Architecture alignment

Steps 30–31 align the roadmap and draft canonical semantic/SCF contracts against the original master archive through v0.6. Read these before adding new runtime scope:

- `docs/ARCHITECTURE_ALIGNMENT.md` — canonical architecture and next implementation order.
- `docs/REQUIREMENT_TRACEABILITY.md` — source-to-capability gap matrix.
- `docs/STEP31_CONTRACT_RECONCILIATION_AND_SEMANTIC_SCF_DRAFT.md` — proposed canonical semantic/SCF contract and unresolved acceptance gates.
- `docs/PHASE1_INTERFACE_CONTRACTS.md` — actual interfaces, invariants and limits.
- `docs/PHASE1_IMPLEMENTATION_STATUS.md` — implemented versus open capabilities.

## Important limitations

This is an executable reference prototype, not a production security boundary. External actions are simulated only. Approval issuers are not fully authenticated, complete authoritative revocation is not implemented, and evidence is not signed or externally anchored. Full semantic claim/relationship modeling, SCF routing/conflict reconciliation, the versioned Anima self-model, HAL monitoring/adaptation, production distributed coordination, and end-to-end privacy/deletion propagation remain open. Multi-file SQLite restore requires writers to be quiesced and is not globally crash-atomic.

**Overall status: `PARTIAL_PASS`. Phase 0 is specification-closed in the repository's v0.99.6 closure record. Phase 1 remains open.** A green test suite verifies only its tested scope. Historical Step 30–31 documents contain superseded acceptance claims; current status is in `docs/PHASE1_IMPLEMENTATION_STATUS.md`.

Step 34 requires per-criterion verification for multi-criterion goals, strict boolean outcomes and valid evidence references. It serializes durable evidence appends across instances, returns detached evidence snapshots, filters nonfinite router inputs and rejects naive approval expiry timestamps. Evidence-reference truth and verifier authentication remain open.

Step 32: enterprise integration contract and acceptance backlog (specification only).

## Step 33

A deterministic policy-constrained router reference is implemented and covered by negative tests; see `docs/STEP33_POLICY_CONSTRAINED_ROUTING.md`. It does not yet perform inference or external calls.
