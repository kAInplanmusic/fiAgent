# Step 11 — Conservative dispatcher and reconciliation (v1.1.6)

## Implemented
- Added `OutboxDispatcher`; no handler is installed by default, so an unconfigured dispatcher does not claim or execute work.
- Explicitly injected handlers receive the persisted payload and stable idempotency key. Accepted outcomes are `SUCCEEDED`, `FAILED`, and `OUTCOME_UNKNOWN`.
- Handler exceptions and invalid handler results become `OUTCOME_UNKNOWN`; they are not interpreted as proof that no side effect occurred.
- `OUTCOME_UNKNOWN` is not automatically claimable. Reconciliation requires a non-empty evidence string and a provider state of `SUCCEEDED`, `FAILED`, or `NOT_EXECUTED`.
- Only an explicit `NOT_EXECUTED` reconciliation returns the row to `PENDING`; callers must ensure the evidence is authoritative. Reconciliation writes its state/evidence marker into `last_error`.
- Added tests for no-handler behavior, successful dispatch, exception ambiguity, no blind retry, evidence-gated reconciliation, terminal reconciliation, and invalid handler output.

## Validation
- `python -m unittest discover -s tests -v`: **47/47 tests passed**.
- Runtime still declares `simulated_only`; no provider adapter or external effect is enabled by this step.

## Limits / next work
- Reconciliation evidence is supplied by the caller and is not cryptographically verified by the prototype.
- Provider-specific idempotency contracts, signed/authoritative evidence, process-kill fault injection, multi-process race tests, and external-effect integration remain open.
- No exactly-once external effect, distributed transaction, or production readiness is claimed. Overall audit status remains `PARTIAL_PASS`.
