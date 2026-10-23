# PRAIN — Phase 1 executable reference prototype

Version `1.2.18` · Step 33 · Python 3.11+ recommended · Standard library only.

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

**Overall status: `PARTIAL_PASS`. Phase 0 is not formally accepted or closed.** A green test suite verifies only the tested implementation scope; it does not establish architectural completeness or production readiness. The requirements matrix is a practical crosswalk, not yet a line-by-line reconciliation of every historical artifact. Explicit human review is still required before Phase 0 closure.

Step 32: enterprise integration contract and acceptance backlog (specification only).

## Step 33

A deterministic policy-constrained router reference is implemented and covered by negative tests; see `docs/STEP33_POLICY_CONSTRAINED_ROUTING.md`. It does not yet perform inference or external calls.
