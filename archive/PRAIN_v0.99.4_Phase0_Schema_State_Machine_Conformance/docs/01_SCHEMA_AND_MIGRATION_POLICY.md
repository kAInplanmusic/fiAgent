# 1. Schema and migration policy

## 1.1 Historical recursive audit

The historical archive contains 20 schemas: 11 in v0.2.1, 3 in v0.4.0, 3 in v0.5.0, and 3 in v0.6. All 20 pass their declared JSON Schema meta-schema validator in the offline audit, and no unresolved local `$ref` or unregistered external `$ref` was found by the audit script. This is structural validity, not proof that every historical schema expresses the intended semantics. The detailed `SCHEMA_FIELD_AUDIT_RECURSIVE.md` and `audit/source_audit.json` list nested constraints and field paths.

## 1.2 Canonical registry

- Canonical schemas in this package use JSON Schema Draft 2020-12 and stable URNs of the form `urn:prain:schema:<contract-name>:1.0.0`.
- The URNs are identifiers, not URLs claiming a public registry exists.
- Historical IDs are retained in the source audit. Consumers must map them through an explicit registry record; no string-rewrite is a migration.
- Every payload declares a `schema_version`. Envelope `schema_id` identifies the payload schema; envelope version and payload version are distinct fields.
- Root `additionalProperties:false` is the default. Extensions require an explicitly versioned extension point, not a silent undeclared field.

## 1.3 Version compatibility

- Patch: clarifies descriptions or examples without changing accepted payloads or meaning.
- Minor: additive optional field or new explicitly namespaced contract that old strict readers are not required to accept. The producer must negotiate supported profiles; a minor version is not a promise that old strict readers accept new fields.
- Major: required-field/type/enum/meaning change, changed authorization semantics, removed field, relaxed security constraint, changed execution-status meaning, changed source-of-truth behavior, or incompatible reference change.
- Security-tightening that rejects formerly accepted messages is treated as a compatibility-breaking change unless consumers have explicitly opted into strict rejection.

## 1.4 Migration registry contract

Every migration record must identify: `source_schema_id`, `source_version`, `target_schema_id`, `target_version`, code/rule version, determinism, reversibility, lossy fields, defaults, rejection conditions, and fixtures. No migration may invent source provenance, infer that an action was safe, map `confidence` to verification, create an approval, or convert missing authority to permit. A migration must either preserve a legacy field, explicitly translate it under a named rule, quarantine the record, or reject it with a reason.

## 1.5 Cross-generation canonical dispositions

| Historical family | Canonical target | Mandatory rule |
|---|---|---|
| v0.2.1 `ActionRequest` → v0.4 `Action Request` → v0.5 `ActionCommand` | `action-command` plus `policy-decision` | Treat request/intent, policy verdict and dispatch command as separate lifecycle objects. Do not map `actor_id` to `actor` or `risk_level` to `risk_class` without source evidence. |
| v0.2.1 Goal (`id`, description, integer priority) → v0.4 Goal (`goal_id`, revision, desired outcome, owner, dependency and budget fields) | `goal` | Preserve original ID as legacy alias; revision is a record revision, not a new goal identity; description is not silently conflated with outcome. |
| v0.2.1 `event-envelope` → v0.4/v0.5 `message-envelope` → v0.6 `semantic-message` | `message-envelope` carrying a separate typed payload | Transport contract and semantic-message contract are separate; semantic status/provenance do not replace tenant, classification, correlation or dispatch metadata. |
| v0.2.1 `ActionResult` → v0.5 `ExecutionReceipt` | `execution-receipt` plus evidence records | Preserve accepted/started/effect-possible/effect-observed/verified/unknown distinctions. Never translate `unknown` to `failed`. |
| v0.2.1 Claim | `claim` plus `claim-transition-event` | Preserve legacy verification value and ID; unknown legacy verification mappings must be quarantined/reviewed, not auto-promoted. |
| v0.2.1 Evidence | `evidence-record` | Integrity manifest and content payload are separate; retention and classification required for every record. |
| v0.6 health signal/repair proposal | `health-signal` / `repair-proposal` | HAL proposals never authorize themselves; policy decision is an independent required gate for execution. |

## 1.6 Required instance-level checks

For every canonical schema: validate one well-formed fixture, reject undeclared fields, reject enum/type violations, reject bad formats where format checking is enabled, and validate applicable conditional requirements. For each historical-to-canonical migration: include one lossless valid fixture, one lossy-but-explicit fixture, and one rejection fixture. This package tests canonical fixtures and preserves historical schema tests; actual migration executors belong to a later implementation phase.
