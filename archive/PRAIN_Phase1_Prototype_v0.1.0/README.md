# PRAIN Phase 1 — executable reference prototype

Version: `0.1.0` — **working prototype, not production-ready**.

Implements:
- Event bus adapter with per-consumer duplicate suppression
- Goal registry with evidence-backed verification
- Versioned in-memory state store with compare-and-swap
- Deny-by-default policy gateway
- Append-only in-memory hash-chain evidence ledger

P.R.A.I.N. = Perception, Reason, Anima, Intention, Nerve. The five dimensions are logical responsibilities, not five required services.

## Run

Requires Python 3.11+ recommended; no third-party dependencies.

```bash
python -m unittest discover -s tests -v
python -m prain.demo
```

## Invariants tested

1. Duplicate event IDs do not invoke the same consumer handler twice.
2. Stale state versions are rejected.
3. Missing policy or mismatched capability is denied.
4. A goal cannot be completed without passing verification and evidence.
5. Execution and verification are separate.
6. The evidence hash chain can be checked for integrity.

## Limits

In-memory only; restart loses state. Single-process concurrency only. No durable broker, production authentication, real external side effects, cryptographically authenticated approvals, signed audit anchors, or production deployment. Hash chains are tamper-evident, not a complete security boundary.
