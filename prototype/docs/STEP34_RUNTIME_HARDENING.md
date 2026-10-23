# Step 34 — runtime correctness

v1.2.19 is developed in `prototype/`; the v1.2.18 upload remains unchanged in
`archive/`. The active candidate has a SHA256 manifest verified independently in CI.

## Changes and regression evidence

| Defect | Correction | Test in test_runtime_hardening.py |
|---|---|---|
| Truthy strings accepted as successful verification | Strict boolean outcomes in both adapters | test_truthy_non_booleans_cannot_complete |
| Blank or malformed evidence accepted | List of nonempty strings required | test_empty_or_malformed_evidence_rejected |
| One boolean completes multiple criteria | Exact per-criterion results required | test_every_criterion_requires_its_own_result |
| Caller mutates acceptance criteria | Deep copies; unique IDs; active-state guard | test_criteria_are_unique_and_detached |
| Returned ledger payload aliases authoritative memory | Detached append/read snapshots | test_returned_payloads_cannot_mutate_chain |
| Multiple instances use stale ledger heads | Read, verify and append in BEGIN IMMEDIATE | test_multiple_instances_share_transactional_head |
| Corrupted persisted evidence extended | Verify inside the write transaction | test_corrupt_chain_is_not_extended |
| Invalid evidence poisons later writes | Roll back; reject nonfinite JSON numbers | test_invalid_append_does_not_poison_transaction |
| NaN budget/cost bypasses routing bounds | Finite, nonboolean numeric validation | test_invalid_budget_denies; test_invalid_backend_numbers_are_filtered |
| Naive expiry raises TypeError | Deny invalid timestamp | test_naive_expiry_denies_without_exception |
| Caller mutates policy rules after construction | Detached rules | test_external_rule_mutation_cannot_change_policy |

Goal verification retains the single-criterion calling convention. Multi-criterion
callers provide `criterion_results=[{'id': ..., 'passed': bool, 'evidence_refs': [...]}]`.
The registry checks result structure and completeness; it does not authenticate a
verifier or resolve evidence truth. These remain explicit open gates.

The backup integration test now uses the public `entries()` API rather than the
private in-memory cache, because the durable database is authoritative. The old
test's expected count is preserved. Architecture status checks now distinguish
the existing Phase-0 specification closure from open Phase-1 implementation.

## Remaining work

Phase 1 remains PARTIAL_PASS. Canonical semantics/SCF, Anima/HAL, event worker fencing,
full authorization/revocation, privacy propagation, enterprise adapters and full
historical requirement traceability remain open. Existing archived Step 30–31
acceptance statements and test-report.txt are historical, not current test evidence.
GitHub CI must execute successfully before its gate can close.

## Verification record — 2026-10-23

The 12 new runtime regression tests were also executed against the unchanged
v1.2.18 import: they produced 22 failed assertions/subtests and one error before
the extreme-integer cases were added. This establishes that the tests detect
pre-existing defects. The corrected implementation passed all 117 tests at that
checkpoint. Two further release-verifier tests now check modified file contents
and unexpected files. Final local result: **119/119 tests PASS**, and **69/69
release files pass exact inventory and SHA256 verification**. The preserved
v1.1.9/v1.2.18 source inventories also pass their original SHA256 verification.
