# 3. Canonical claim ontology and lifecycle

## 3.1 Orthogonal axes

A claim has separate fields for:
1. **Epistemic status:** observed, reported, inferred, hypothesized, corroborated, verified, disputed, refuted, unknown.
2. **Verification status:** not_checked, pending, passed, failed, inconclusive, stale, not_applicable.
3. **Confidence:** optional numeric `[0,1]` with declared method; missing is not zero.
4. **Validity interval:** world-time (`valid_from`, optional `valid_until`).
5. **Record lifecycle:** active, superseded, withdrawn, quarantined.
6. **Revision history:** immutable claim revisions plus append-only transition events.

These axes must not be collapsed into one `status` value.

## 3.2 Normative status meanings

- `observed`: a source/event was observed; this does not validate an interpretation of it.
- `reported`: a source asserted the proposition; it is not independently confirmed.
- `inferred`: derived from identified premises and a method/version.
- `hypothesized`: a testable candidate explanation with a proposed disconfirmation route.
- `corroborated`: supported by independent evidence paths; duplicate copies of a single source are not independence.
- `verified`: a named, versioned procedure passed for the declared scope, time and acceptance criteria; not universal or timeless truth.
- `disputed`: credible counterevidence or incompatible claims exist; both claims and evidence are preserved.
- `refuted`: a named procedure or superior evidence rejects this exact proposition and scope. A changed proposition/scope requires a new claim.
- `unknown`: available evidence does not support a conclusion; it is not a negative fact.

## 3.3 Required invariants

- A claim always has provenance, explicit scope and `recorded_at`.
- A `verified` claim requires `verification_status=passed` and a `verification_ref`.
- A `refuted` claim requires `verification_status=failed` and one or more `refutation_refs`.
- Numeric confidence requires a named `confidence_method`; confidence never automatically promotes status.
- Derived claims reference premise claims and inference method/version in provenance.
- `corroborated` requires at least two independent evidence paths or a policy-approved domain-specific equivalent with a documented justification.
- A disputed claim is not deleted/overwritten to conceal disagreement.
- Every status transition creates a transition event with actor, timestamp, from/to status, reason, rule version, evidence and counterevidence references, and resulting revision.
- Claim revisions are immutable. Mutable “current claim” is only a pointer/head using compare-and-swap; an update conflict is explicit.
- If evidence expires or a premise changes, re-evaluate dependent claims. Do not assert downstream falsity unless the dependency rule justifies it.

## 3.4 Allowed transition matrix

| From | Allowed destinations | Additional rule |
|---|---|---|
| new/no prior record | observed, reported, inferred, hypothesized, unknown | Provenance must justify initial status. |
| observed | corroborated, verified, disputed, refuted, unknown | Observed data remains distinct from proposition interpretation. |
| reported | corroborated, verified, disputed, refuted, unknown | Source assertions are not independent corroboration by themselves. |
| inferred | corroborated, verified, disputed, refuted, unknown | Parent claims and method/version required. |
| hypothesized | corroborated, verified, disputed, refuted, unknown | Verification plan/falsification route should be recorded. |
| corroborated | verified, disputed, refuted, unknown | A verification procedure is still required for `verified`. |
| verified | disputed, refuted, unknown | New event must explain counterevidence, expiry, invalid scope or premise change; historical pass remains in audit trail. |
| disputed | corroborated, verified, refuted, unknown | Reconciliation must cite both sides and disposition reason. |
| refuted | terminal for exact proposition/scope | Correction or scope change creates a new revision/new claim; no editing history to resurrect it. |
| unknown | observed, reported, inferred, hypothesized, corroborated, verified, disputed, refuted | New evidence or explicit review event required; unknown alone cannot become verified. |

There is no direct transition based solely on confidence. Transition rules are enforced by a policy/claim validator in a future runtime; this specification includes deterministic test vectors only.

## 3.5 Legacy migration

- `id` → `claim_id`; preserve original ID in `legacy_ids`.
- `statement` → `proposition.statement`, without destructive normalization.
- `kind` → `claim_kind` only through a reviewed mapping; unsupported values map to `other` with the raw legacy value preserved in migration metadata.
- subject/predicate/object fields are copied only where present; do not invent missing terms.
- `confidence` is copied only with `confidence_method=unknown_legacy_method` unless its original method is evidenced.
- legacy `verification_status` is preserved in migration metadata. No direct mapping is assumed solely because enum names look similar.
- `created_at` maps to `recorded_at` only if it represented record creation; original value remains retained.
- legacy `verification_exception_ref` cannot be treated as a pass; it becomes review/exception provenance.
- missing provenance causes the migrated record to be `quarantined` for review or `unknown` under the migration rule, never `verified`.

## 3.6 Epistemic vs policy separation

Knowledge confidence and epistemic status do not grant capabilities. Authorization always derives from principal/tenant identity, action digest, current policy, scoped capabilities and applicable approval. Even a verified claim cannot authorize an action.
