# PRAIN — Architecture Deepening Pack v0.4.0

**Canonical name:** P.R.A.I.N. — Perception, Reason, Anima, Intention, Nerve  
**Release type:** architecture refinement and implementation blueprint  
**Status:** design baseline; not a claim that every component is implemented

## Purpose

This package deepens the architecture around semantic meaning, goal-directed operation, inter-module communication, state transitions, evidence, and feedback. It preserves Phase 0.2.1 as the contract baseline and Phase 1 v0.1.0 as a reference prototype, while making the next architecture and implementation decisions explicit.

## Design thesis

PRAIN is a **semantic control plane for goal-directed autonomous systems**. It connects observations to beliefs, beliefs to goals, goals to plans, plans to policy-checked actions, and action outcomes to verified evidence and updated state. It is not merely a vector database, a chatbot wrapper, a fixed five-agent swarm, or a claim of quantum advantage.

The five dimensions are logical capabilities, not mandatory processes:
- **P — Perception:** acquire and normalize observations from tools, users, files, sensors, and other agents.
- **R — Reason:** interpret evidence, model alternatives, infer consequences, plan, and assess uncertainty.
- **A — Anima:** maintain the explicit self-model, continuity, commitments, operating identity, and reflection history.
- **I — Intention:** represent goals, priorities, constraints, acceptance criteria, plans, and commitment state.
- **N — Nerve:** execute authorized operations through capability adapters and return structured outcomes.

## Package map

- `architecture/REFERENCE_ARCHITECTURE.md` — architecture, boundaries, modules, failure semantics.
- `architecture/COMMUNICATION_MODEL.md` — message routes, event contracts, command/query separation.
- `architecture/GOAL_AND_CONTROL_LOOP.md` — goal lifecycle and feedback control.
- `architecture/SEMANTIC_MODEL.md` — typed semantic objects and links.
- `architecture/IDENTITY_AND_CONTINUITY.md` — self-model, memory, identity boundaries.
- `architecture/FAILURE_AND_RECOVERY.md` — retries, conflicts, timeouts, compensation, recovery.
- `architecture/OBSERVABILITY_AND_EVALUATION.md` — metrics, traces, verification and evaluation.
- `architecture/THREAT_AND_TRUST_BOUNDARIES.md` — policy, approvals, untrusted inputs, audit.
- `contracts/architecture-map.yaml` — machine-readable logical module map.
- `contracts/message-envelope.schema.json` — event/command envelope contract.
- `contracts/goal.schema.json` — goal contract.
- `contracts/action-request.schema.json` — policy-gated action request.
- `plans/IMPLEMENTATION_ROADMAP.md` — staged build plan and exit criteria.
- `plans/DECISION_REGISTER.md` — decisions and unresolved questions.
- `validation/TRACEABILITY_MATRIX.md` — requirements to contracts, tests, and implementation.

## Core invariants

1. Every actionable goal has an owner, priority, constraints, and machine-checkable acceptance criteria.
2. Every external observation carries source/provenance, observation time, receipt time, and trust classification where applicable.
3. Reasoning can propose an action; only the policy gateway can authorize it.
4. Nerve never treats a plan or model output as authorization.
5. A successful tool response is not automatically proof that the user goal was achieved.
6. State mutation is versioned; conflicts are explicit.
7. Retries are safe only when idempotency/side-effect semantics are defined.
8. Identity/self-model updates are evidence-linked, versioned, and distinguish facts from hypotheses.
9. Unknown policy, missing capability, invalid schema, and unresolved critical conflict result in deny/defer, not implicit allow.
10. P/R/A/I/N are connected through contracts and shared semantic state, not isolated silos.

## Important status distinction

The Phase 1 Python prototype is in-memory and single-process. This pack does not upgrade that code into a durable distributed runtime. It specifies the architecture and implementation sequence needed to do so.
