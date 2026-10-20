# 8. Normative decision register — PRAIN Phase-0 baseline

The user accepted the recommended direction in this conversation. The choices below are therefore the baseline adopted for this specification package. They remain revisable by an explicitly recorded later decision. They do not mean any runtime implementation has been tested.

| ID | Decision | Baseline rule | Consequence |
|---|---|---|---|
| D-0001 | P/R/A/I/N meaning | P Perception, R Reason, A Anima, I Intention, N Nerve | Five logical dimensions, not required five services |
| D-0002 | PRAIN independence | PRAIN independent of Hallerbans and any single runtime | Hallerbans is one possible consumer |
| D-0003 | Quantum-ready | Replaceable provider/compute interfaces; no quantum advantage assumption | Do not encode quantum-specific truth claims without evidence |
| D-0004 | Authorization source | One independent policy gateway is the only action authorizer | No dimension or HAL grants authority |
| D-0005 | Claim state axes | Epistemic, verification, confidence, validity, lifecycle remain separate | No confidence-to-verified promotion |
| D-0006 | Claim history | Immutable revisions and append-only transition events | Corrections create revisions/events, not silent edits |
| D-0007 | Message delivery | At-least-once plus idempotent consumers; no global exactly-once | Unknown/duplicate effects need receipts/reconciliation |
| D-0008 | Source of truth | Authority class declared for every record class; projections cannot overwrite authority | CAS per aggregate and explicit conflicts |
| D-0009 | Consistency | Strong only for auth/critical heads and unique command reservation; eventual for projections | No global synchronization assumption |
| D-0010 | Unknown external outcome | First-class durable state | Reconcile before retry unless adapter proves retry safe |
| D-0011 | Tenant model | Tenant ID mandatory for protected records and authenticated context | Cross-tenant access explicit, scoped and revocable |
| D-0012 | Delegation | Bounded, expiring, revocable capability allowlist | Authority can narrow, never widen |
| D-0013 | Approvals | Action/actor/tenant/target/effect digest-bound and expiring | Changed action needs new approval |
| D-0014 | Failure mode for unknown policy | Deny/defer by default | No implicit permit on timeout/missing config |
| D-0015 | Evidence | Integrity metadata separate from source truth; signature requirements policy-driven | Hash alone is not source authenticity |
| D-0016 | Privacy/deletion | Per-class retention; deletion propagates to derived data and restores | Append-only evidence does not mean infinite payload retention |
| D-0017 | HAL | Supervisory layer, not sixth dimension or authority | Bounded catalogue, explicit rollback and external authorization |
| D-0018 | HAL forbidden actions | Cannot alter hard limits/policy, self-grant rights, disable audit or self-approve | Invariant violation blocks repair |
| D-0019 | Schema IDs | Draft 2020-12, canonical URN IDs | No fictitious hosted registry; old IDs map explicitly |
| D-0020 | Unknown fields | Strict object schemas by default | Extensions negotiated/versioned, not silent |
| D-0021 | Runtime framework choice | Deferred from Phase 0 | No broker/database/OS choice required to specify contracts |
| D-0022 | SLO targets | Deployment profile must supply numeric SLOs; safety invariants remain universal | Architecture does not invent universal performance promises |
| D-0023 | KB source of truth | Canonical JSON; HTML parity checked/generated | No separate hidden HTML data divergence |
| D-0024 | Version path | v0.9.3 comprehensive baseline; v0.99 final closure candidate; v0.1.0 only after explicit Phase-0 release | Do not mistake semantic version ordering or ZIP creation for approval |
| D-0025 | Runtime claims | No production/runtime security claim based on specs-only tests | Later implementation conformance is an independent gate |

## Explicitly deferred to implementation profiles

- Broker/database/provider/runtime/OS selection; all are behind replaceable adapters.
- Numeric SLO targets: must be picked per deployment after workload and risk characterization.
- Jurisdiction-dependent retention periods and legal-hold details: each deployment declares lawful policy; no universal number is assumed.
- KMS/HSM vendor/API, specific signing algorithm profiles and rotation intervals: interface and lifecycle requirements are mandatory, deployment choice remains replaceable.
- Cross-organization consensus algorithm: required only for record classes with declared multi-authority governance; never assumed for all data.
