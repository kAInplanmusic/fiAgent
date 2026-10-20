# 16. State-machine conformance matrix

This matrix connects the normative state machines in `15_NORMATIVE_STATE_MACHINES.md` to the offline reference tests and the later runtime acceptance gate.

| Domain | Required positive paths | Required negative / adversarial paths | Runtime-only proof still required |
|---|---|---|---|
| Claim epistemic state | Every listed edge with valid provenance/context | Every unlisted edge; missing reason/actor/rule version; invalid time; non-monotonic revision; verified without pass/ref; refuted without failure/refutations; confidence-only promotion | CAS races, event persistence, dependent-claim re-evaluation, concurrent head updates |
| Policy decisions | Fresh permit with exact context and any required approvals | Deny/require_approval/defer; changed goal/plan/identity/rules/scope/side-effect/input/deadline; stale epoch/policy; expiration after command deadline; missing/extra approvals | Live policy service outage, revocation races, actual decision token verification, TOCTOU at adapters |
| Approval lifecycle | approve→issued→consumed; bounded-use until exhaustion | deny+issued, approve+rejected, consumed reuse, expired/revoked/stale/context changed, self-approval under separation-of-duties | Atomic compare-and-set / concurrent use, real approver identity assurance, audit event durability |
| Dispatch reservation | Same key+same digest returns same reservation; first reservation consumes usage once | Same key+different digest; stale policy/epoch, changed action context, duplicate approval consumption | Linearizable reservation under concurrency, crash between stores, external idempotency behavior |
| Execution receipt / recovery | Accepted→started→effect observed→independently verified; unknown→reconciliation→effect absent/present | Blind retry on unknown; indeterminate+retry; claim no effect from timeout/lease expiry; executor self-verification; verified without evidence | Fault injection, real adapter ledgers, crash/partition/restore and duplicate-event replay |
| Goal lifecycle | Required evidence→verifying→completed | Complete with unmet criterion; active→completed shortcut; reopening terminal goal in place | Actual criterion verifier correctness, evidence trust and persistence |
| HAL repair | Bounded approved repair→executing→measured success or rollback | Self-approval, policy bypass, scope expansion, stale trigger, retry beyond bounds | Canary/rollback under injected failure and production monitoring |
| Delegation | Narrow scoped active grant; authorized suspension/reactivation | Scope/capability widening; using revoked/expired/exhausted grant | Epoch fencing and concurrent revocation propagation |

The test report distinguishes static contract checks from reference-oracle checks. Passing this matrix is evidence about specification consistency only; it is not implementation conformance or a security certification.


## 16.1 Executed offline suite

`tools/validate_state_machine_conformance.py` generates exhaustive allowed/forbidden edge vectors for the normative matrices and evaluates explicit negative guard vectors. The current candidate records 504/504 offline checks passing. The test suite itself is part of the specification package and must be rerun whenever a transition table, guard, schema or referenced policy changes.

Critical negative vectors include stale permit/identity epoch, changed action digest, non-atomic approval consumption, self-verification, missing evidence, unproven effect absence, changed idempotency key/digest on retry, non-retryable retry class, unverified compensation, completing a goal without verified criteria, HAL self-approval, reactivating suspended delegation without fresh validity/epoch checks, revoking without authority, expiring before deadline, exhausting before usage budget, and reactivating revoked/expired/exhausted delegation.

This result proves only that the included deterministic reference model agrees with its encoded edge matrices and guard examples. It does not prove the correctness of a future implementation, storage atomicity, race freedom, real external effects or security certification.
