# Step 9 — SQLite admission integrated into PRAINRuntime

Date: 2026-10-20
Prototype: v1.1.4

## Implemented

- `PRAINRuntime(..., admission_store=DurableAdmissionStore(path))` can opt into durable admission.
- Before policy evaluation, the runtime checks an existing durable record: matching key + matching request fingerprint replays the stored receipt; matching key + changed fingerprint fails closed.
- For a newly allowed simulated action, receipt persistence and optional single-use approval consumption are performed by one `BEGIN IMMEDIATE` SQLite transaction with unique constraints.
- A second Runtime instance using the same SQLite file can replay the first instance's receipt after restart/re-instantiation.
- A single-use approval cannot be consumed by two distinct idempotency keys even when the second request arrives through a newly instantiated Runtime.
- Runtime's default remains backwards-compatible in-memory mode unless `admission_store` is supplied.

## Validation

Run from this directory:

```bash
python -m unittest discover -s tests -v
python -m prain.demo
```

Observed result: **38/38 unit tests pass**. Three new runtime integration tests cover cross-instance replay, changed-payload conflict after restart, and durable single-use approval consumption. Demo remains `simulated_only`.

## Explicit limits

- This is durable **admission/receipt** integration, not a complete durable runtime.
- StateStore, GoalRegistry, EventBus, and EvidenceLedger remain in-memory and are not reconstructed after restart.
- No durable outbox or dispatcher is implemented; no real external effect is executed.
- The policy decision is currently evaluated before the store transaction. The transaction atomically enforces idempotency uniqueness, receipt storage, and single-use approval consumption, but does not persist a full signed decision bundle or external-effect intent.
- Approval authenticity and authoritative revocation checks are not provided by this adapter.
- SQLite WAL/FULL synchronous settings improve local durability but do not establish multi-host distributed consensus or exactly-once external execution.

Status remains `PARTIAL_PASS`; production readiness is `NOT ESTABLISHED`.
