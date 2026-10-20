# PRAIN Phase 1 — executable reference prototype

Version `1.1.0`. Python 3.11+ recommended. Standard library only.

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

In-memory only; restart loses state. Single-process concurrency. The runtime never performs real external actions. Policy approval issuers are not authenticated; approvals are not single-use/atomic. Evidence is hash-chained but not signed or externally anchored. No durable broker, persistence adapter, HTTP API, multi-tenant auth, secret store, telemetry or production deployment. This is an executable reference prototype, not a production security boundary.

## Next implementation increments

1. Persistence interface + SQLite adapter and migrations.
2. Durable event inbox/outbox with retry classification and dead-letter state.
3. Approval identity/signature verification and atomic single-use consumption.
4. Typed policy/evaluator contracts and property-based state-machine tests.
5. API boundary, configuration, observability, threat model and deployment only after interfaces stabilize.
