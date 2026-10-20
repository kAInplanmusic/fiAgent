# PRAIN Phase 1 — executable reference prototype

Version `1.1.4`. Python 3.11+ recommended. Standard library only.

P.R.A.I.N. = **Perception, Reason, Anima, Intention, Nerve**. These are logical responsibilities, not five required services.

## Implemented vertical slice

- Typed observation envelope and canonical SHA-256 hashing.
- Observation intake, correlation, event publication and evidence recording.
- Named evaluator registry; unknown evaluator fails closed.
- Deny-by-default policy evaluation with action/target/capability matching and optional approval binding.
- Simulated-only action execution with an idempotency key and replayed receipt.
- Goal lifecycle with explicit evidence-backed verification.
- Versioned in-memory state with compare-and-swap.
- Append-only in-memory evidence hash chain and integrity verification.
- Optional SQLite-backed durable admission/receipt replay when `PRAINRuntime(admission_store=...)` is configured.
- Cross-instance tests for durable replay, fingerprint conflict and single-use approval consumption.
- Unit tests for success paths and critical negative paths.

## Run

```bash
python -m unittest discover -s tests -v
python -m prain.demo
```

No third-party dependencies or network access are required.

## Design principles

1. Small, typed interfaces and standard-library implementation first.
2. Fail closed for unknown evaluators and unmatched policies.
3. Separate policy decision, simulated execution, receipt and goal verification.
4. Stable canonical serialization for content hashes.
5. Explicitly identify what is not implemented instead of implying production guarantees.

## Current limits

The default runtime remains in-memory unless an optional `DurableAdmissionStore` is supplied. With that adapter, idempotency records, simulated receipts and single-use approval consumption persist in SQLite. Other runtime components (StateStore, GoalRegistry, EventBus and EvidenceLedger) remain in-memory. The runtime never performs real external actions. Approval issuers are not authenticated and authoritative revocation checks are not implemented. Evidence is hash-chained but not signed or externally anchored. No durable outbox/dispatcher, HTTP API, multi-tenant auth, secret store, telemetry or production deployment. This is an executable reference prototype, not a production security boundary.

## Next implementation increments

1. Durable event inbox/outbox with retry classification, dead-letter state and crash-recovery tests.
2. Persist policy decision bundle and action intent transactionally with admission; define outcome-unknown reconciliation.
3. Approval identity/signature verification and authoritative revocation checks.
4. Durable state/goal/evidence interfaces and multi-instance tests.
5. Typed policy/evaluator contracts and property-based state-machine tests.
6. API boundary, configuration, observability, threat model and deployment only after interfaces stabilize.

See `docs/STEP9_RUNTIME_SQLITE_INTEGRATION.md` for scope and evidence.

Step 10 adds durable outbox and conservative recovery; this remains a simulated reference prototype, not a production dispatcher.
