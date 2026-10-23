# Step 31 — contract reconciliation and semantic/SCF draft

**Release:** v1.2.16 / Step 31  
**Status:** specification draft; not an implementation claim  
**Audit gate:** `PARTIAL_PASS` until the source-level audit, implementation and acceptance gates are satisfied.

## Purpose

Step 30 established an honest capability crosswalk, but explicitly did not reconcile every historical source line. Step 31 narrows the next architectural decision surface: it records cross-version disposition rules and proposes a canonical semantic contract that can be reviewed before runtime implementation.

## Source precedence and disposition

The source hierarchy is cumulative, not destructive:

1. Phase 0 v0.2.1 supplies baseline registries, versioned state/CAS, policy and schema contracts.
2. Architecture v0.4.0 expands semantic entities, P/R/A/I/N responsibilities, identity/continuity, control flow, observability and trust boundaries.
3. Distributed Protocol v0.5.0 adds delivery, inbox/outbox, leases/fencing, reconciliation and failure recovery.
4. v0.6 adds the multiscale model, SCF, HAL and the invariant/evidence plane. It does not implicitly erase earlier requirements.
5. Knowledge-base JSON/HTML and intermediate snapshots remain evidence sources to reconcile, not silently replace.

Every requirement discovered in a source must receive one disposition: `RETAINED`, `EXTENDED`, `SUPERSEDED_WITH_RATIONALE`, or `OPEN`. Each row needs a source locator, canonical requirement ID, disposition, evidence, affected interfaces/tests and reviewer status. Absence from a newer document is not evidence of supersession.

## Governance conflict requiring explicit treatment

The master index says runtime/framework/OS implementation must not begin before Phase 0 review and formal acceptance. A Phase 1 executable prototype nevertheless exists. This is a historical governance deviation, not a reason to discard the prototype and not proof of Phase 0 acceptance. Preserve the prototype as a reference implementation; record the deviation and require a human decision on whether to ratify the sequence or treat affected implementation work as provisional. Do not retroactively invent an acceptance record.

## Canonical semantic contract proposal

These are proposed logical records, not yet implemented Python runtime types:

- **Observation:** a source-originated occurrence or measurement. Must retain source, observed time, ingestion time, payload classification and uncertainty where applicable.
- **Claim:** a typed assertion about an entity or relation. Must distinguish the assertion from its evidence and from a model's interpretation.
- **EvidenceRef:** a reference to an immutable or versioned evidence item, including digest/identity and access/classification metadata; a reference alone does not make evidence trustworthy.
- **SourceRef:** source identity, acquisition method, provenance and trust assessment; trust is contextual, not a universal truth score.
- **Hypothesis:** a provisional claim with explicit epistemic status, supporting/contradicting evidence and revision history.
- **Relationship:** a typed edge between identified entities/claims, with validity interval and provenance when temporal facts are represented.
- **Scope:** the authority and applicability boundary (tenant/system/group/local unit) for a message or claim. Scope mismatch must not be silently adopted.
- **Lineage:** causal/derivation references from inputs and versions to an output. Derived data must retain enough lineage to support invalidation, audit and deletion propagation.
- **SemanticMessage:** a versioned envelope carrying message ID, producer, scope, creation time, schema/type, payload reference or payload, provenance, lineage/dependencies, freshness/expiry where relevant, and idempotency/correlation metadata.
- **Conflict:** a durable record of incompatible claims or versions, with scope, evidence, affected projections and lifecycle state.
- **ReconciliationDecision:** a recorded decision, actor/authority, reason, input versions and evidence; a decision must not erase the conflicting evidence.

### Required distinctions

1. `observed_at` is not `ingested_at`; neither is an authoritative state update time.
2. Confidence/uncertainty is not authorization, provenance, or evidence integrity.
3. A model-generated statement is a claim/hypothesis until supported by the applicable verification contract.
4. Valid time (when a fact applies) differs from transaction time (when the system recorded it).
5. Missing freshness information must not be interpreted as unlimited freshness.
6. Unknown values and contradictory values must remain representable; do not coerce them to false or silently choose a winner.

## SCF recipient decision contract

A recipient may choose only a documented outcome and must persist a reason and the relevant contract/input versions:

- `adopt`: accept into the scoped local model after validation and authority checks.
- `retain_as_hypothesis`: preserve provisionally without treating it as authoritative.
- `recompute`: invalidate/recompute a derived result because a dependency changed.
- `request_evidence`: defer adoption until required evidence is supplied.
- `raise_conflict`: create or update a durable conflict record.
- `ignore_out_of_scope`: reject applicability outside the receiver's scope, recording the reason where audit policy requires.
- `defer`: postpone due to unavailable dependency, stale information or temporary inability to decide.

The legacy v0.6 outcome `ignore_out_of_scope` is retained exactly; implementations must not normalize it into an unlogged silent drop. A recipient decision is not a policy authorization to execute an external action.

## Consistency and authority

- Permissions, approvals, authoritative identity/self-model revisions, goal versions, resource ceilings and action outcome records require authoritative version checks and an explicit conflict/reconciliation path.
- Shared authoritative aggregates use CAS or an equivalent conditional commit; stale writers must fail rather than overwrite newer state.
- Derived projections, search indexes and caches may be eventually consistent, but must carry source versions/freshness and cannot write back as authority.
- Delivery is at-least-once. Consumers must be idempotent. No global exactly-once side-effect guarantee is implied.
- An unknown action outcome remains `OUTCOME_UNKNOWN` until authoritative evidence resolves it. Lease expiry is not proof of non-execution.
- Replay and dead-letter handling must preserve message identity, attempt history and original evidence.
- HAL may observe and propose bounded repairs, but it cannot grant capabilities, approve actions, bypass policy, or mutate protected invariants without the same authorization path as any other actor.

## Schema and migration rules

- Use explicit schema identifiers and SemVer-compatible evolution policy; never infer schema version from a payload shape.
- Additive optional fields may be backward-compatible only when old readers safely ignore them and the invariant is unchanged.
- Changes to required fields, meaning, authority, identity, ordering, or outcome semantics require a major contract version or an explicit migration protocol.
- Validate before admission; reject unknown mandatory semantics; preserve unknown optional extension fields only if the canonical contract says it is safe.
- Include migration, compatibility, invalid-input and round-trip tests for every schema change.

## Privacy and deletion obligations

Classification, retention, redaction and deletion must apply across primary records, event/outbox records, evidence metadata, derived projections, indexes, caches, backups and replay/dead-letter storage. Where evidence cannot legally or technically be deleted, the design must document a tombstone/redaction strategy and its limits. Step 31 does not claim that this end-to-end lifecycle is implemented.

## Step 31 acceptance criteria

- [x] Historical precedence and disposition vocabulary documented.
- [x] Prototype-before-Phase-0-acceptance governance conflict explicitly surfaced.
- [x] Proposed semantic entities, SCF outcomes, authority and schema-evolution rules documented.
- [ ] Line-by-line reconciliation of all archived specs, knowledge-base artifacts and intermediate decisions completed.
- [ ] Human decisions recorded for unresolved contradictions and governance deviation.
- [ ] Canonical schema approved before implementation begins.
- [ ] Runtime conformance tests and implementation evidence added in subsequent steps.

**Result:** Step 31 produces a reviewable contract draft. It does not close Phase 0 or Phase 1, and does not claim SCF or the full semantic model is implemented.
