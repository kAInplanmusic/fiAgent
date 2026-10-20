# Recursive schema audit of historical contracts

- Schemas discovered: **20**
- JSON Schema meta-schema check passes: **20/20**
- Local-reference/external-reference issues surfaced for registry follow-up: **0**

| Source version | Schema | Root required | Root properties | Strict root | `$id` namespace | Meta-schema |
|---|---|---:|---:|---|---|---|
| v0.4.0 | `action-request.schema.json` | 10 | 15 | False | `prain.local` | PASS |
| v0.4.0 | `goal.schema.json` | 10 | 17 | False | `prain.local` | PASS |
| v0.4.0 | `message-envelope.schema.json` | 8 | 14 | False | `prain.local` | PASS |
| v0.5.0 | `action-command.schema.json` | 8 | 9 | False | `prain.dev` | PASS |
| v0.5.0 | `execution-receipt.schema.json` | 7 | 9 | False | `prain.dev` | PASS |
| v0.5.0 | `message-envelope.schema.json` | 9 | 14 | False | `prain.dev` | PASS |
| v0.2.1 | `action-request.schema.json` | 10 | 13 | False | `prain.dev` | PASS |
| v0.2.1 | `action-result.schema.json` | 6 | 10 | False | `prain.dev` | PASS |
| v0.2.1 | `agent-manifest.schema.json` | 6 | 10 | False | `prain.dev` | PASS |
| v0.2.1 | `claim.schema.json` | 6 | 14 | False | `prain.dev` | PASS |
| v0.2.1 | `event-envelope.schema.json` | 7 | 10 | False | `prain.dev` | PASS |
| v0.2.1 | `evidence.schema.json` | 6 | 9 | False | `prain.dev` | PASS |
| v0.2.1 | `goal.schema.json` | 7 | 11 | False | `prain.dev` | PASS |
| v0.2.1 | `observation.schema.json` | 6 | 12 | False | `prain.dev` | PASS |
| v0.2.1 | `policy-decision.schema.json` | 7 | 8 | False | `prain.dev` | PASS |
| v0.2.1 | `state-snapshot.schema.json` | 6 | 8 | False | `prain.dev` | PASS |
| v0.2.1 | `trace-event.schema.json` | 8 | 11 | False | `prain.dev` | PASS |
| v0.6 | `health-signal.schema.json` | 7 | 12 | False | `prain.example` | PASS |
| v0.6 | `repair-proposal.schema.json` | 11 | 12 | False | `prain.example` | PASS |
| v0.6 | `semantic-message.schema.json` | 9 | 18 | False | `prain.example` | PASS |

## Per-schema nested constraints

### `PRAIN_Architecture_v0.4.0/contracts/action-request.schema.json`

- ID: `https://prain.local/schemas/action-request-0.4.0.json`
- Required at root: `action_id, goal_id, plan_id, actor, action, target, input_digest, capability_ref, idempotency_key, requested_at`
- Root properties: `action_id, goal_id, plan_id, actor, action, target, input_digest, capability_ref, idempotency_key, requested_at, deadline, preconditions, expected_postconditions, risk_class, policy_decision_ref`
- Nested constraint nodes: 18
  - `$`: `type=object`, `additionalProperties=False`, `required=['action_id', 'goal_id', 'plan_id', 'actor', 'action', 'target', 'input_digest', 'capability_ref', 'idempotency_key', 'requested_at']`
  - `$/properties/action_id`: `type=string`
  - `$/properties/goal_id`: `type=string`
  - `$/properties/plan_id`: `type=string`
  - `$/properties/actor`: `type=string`
  - `$/properties/action`: `type=string`
  - `$/properties/target`: `type=string`
  - `$/properties/input_digest`: `type=string`, `pattern=^[a-f0-9]{64}$`
  - `$/properties/capability_ref`: `type=string`
  - `$/properties/idempotency_key`: `type=string`
  - `$/properties/requested_at`: `type=string`, `format=date-time`
  - `$/properties/deadline`: `type=string`, `format=date-time`
  - `$/properties/preconditions`: `type=array`
  - `$/properties/preconditions/items`: `type=string`
  - `$/properties/expected_postconditions`: `type=array`
  - `$/properties/expected_postconditions/items`: `type=string`
  - `$/properties/risk_class`: `enum=['read_only', 'reversible_write', 'external_side_effect', 'irreversible']`
  - `$/properties/policy_decision_ref`: `type=string`

### `PRAIN_Architecture_v0.4.0/contracts/goal.schema.json`

- ID: `https://prain.local/schemas/goal-0.4.0.json`
- Required at root: `goal_id, revision, title, desired_outcome, owner, priority, status, acceptance_criteria, created_at, updated_at`
- Root properties: `goal_id, revision, title, desired_outcome, owner, requester, priority, status, acceptance_criteria, constraints, depends_on, budget, deadline, created_at, updated_at, verification_ref, blocked_reason`
- Nested constraint nodes: 28
  - `$`: `type=object`, `additionalProperties=False`, `required=['goal_id', 'revision', 'title', 'desired_outcome', 'owner', 'priority', 'status', 'acceptance_criteria', 'created_at', 'updated_at']`
  - `$/properties/goal_id`: `type=string`, `minLength=1`
  - `$/properties/revision`: `type=integer`, `minimum=1`
  - `$/properties/title`: `type=string`, `minLength=1`
  - `$/properties/desired_outcome`: `type=string`, `minLength=1`
  - `$/properties/owner`: `type=string`, `minLength=1`
  - `$/properties/requester`: `type=string`
  - `$/properties/priority`: `type=object`, `additionalProperties=False`, `required=['class']`
  - `$/properties/priority/properties/class`: `enum=['critical', 'high', 'normal', 'low']`
  - `$/properties/priority/properties/factors`: `type=object`
  - `$/properties/status`: `enum=['proposed', 'accepted', 'active', 'blocked', 'verifying', 'completed', 'failed', 'cancelled', 'superseded']`
  - `$/properties/acceptance_criteria`: `type=array`, `minItems=1`
  - `$/properties/acceptance_criteria/items`: `type=object`, `additionalProperties=False`, `required=['criterion_id', 'description', 'verification_method']`
  - `$/properties/acceptance_criteria/items/properties/criterion_id`: `type=string`
  - `$/properties/acceptance_criteria/items/properties/description`: `type=string`
  - `$/properties/acceptance_criteria/items/properties/verification_method`: `type=string`
  - `$/properties/acceptance_criteria/items/properties/required_evidence`: `type=array`
  - `$/properties/acceptance_criteria/items/properties/required_evidence/items`: `type=string`
  - `$/properties/constraints`: `type=array`
  - `$/properties/constraints/items`: `type=string`
  - `$/properties/depends_on`: `type=array`
  - `$/properties/depends_on/items`: `type=string`
  - `$/properties/budget`: `type=object`
  - `$/properties/deadline`: `type=string`, `format=date-time`
  - `$/properties/created_at`: `type=string`, `format=date-time`
  - `$/properties/updated_at`: `type=string`, `format=date-time`
  - `$/properties/verification_ref`: `type=string`
  - `$/properties/blocked_reason`: `type=string`

### `PRAIN_Architecture_v0.4.0/contracts/message-envelope.schema.json`

- ID: `https://prain.local/schemas/message-envelope-0.4.0.json`
- Required at root: `message_id, message_type, name, schema_version, created_at, producer, correlation_id, payload`
- Root properties: `message_id, message_type, name, schema_version, created_at, producer, recipient, correlation_id, causation_id, tenant_id, idempotency_key, trace_context, provenance, payload`
- Nested constraint nodes: 15
  - `$`: `type=object`, `additionalProperties=False`, `required=['message_id', 'message_type', 'name', 'schema_version', 'created_at', 'producer', 'correlation_id', 'payload']`
  - `$/properties/message_id`: `type=string`, `minLength=1`
  - `$/properties/message_type`: `enum=['command', 'event', 'query', 'response']`
  - `$/properties/name`: `type=string`, `minLength=3`
  - `$/properties/schema_version`: `type=string`, `pattern=^[0-9]+\.[0-9]+\.[0-9]+$`
  - `$/properties/created_at`: `type=string`, `format=date-time`
  - `$/properties/producer`: `type=string`, `minLength=1`
  - `$/properties/recipient`: `type=string`
  - `$/properties/correlation_id`: `type=string`, `minLength=1`
  - `$/properties/causation_id`: `type=string`
  - `$/properties/tenant_id`: `type=string`
  - `$/properties/idempotency_key`: `type=string`
  - `$/properties/trace_context`: `type=object`
  - `$/properties/provenance`: `type=object`
  - `$/properties/payload`: `type=object`

### `PRAIN_Distributed_Protocol_v0.5.0/schemas/action-command.schema.json`

- ID: `https://prain.dev/schemas/action-command-0.5.0.json`
- Required at root: `command_id, idempotency_key, action_digest, target, action, expected_policy_version, retry_class, deadline`
- Root properties: `command_id, idempotency_key, action_digest, target, action, expected_policy_version, retry_class, deadline, lease`
- Nested constraint nodes: 15
  - `$`: `type=object`, `additionalProperties=False`, `required=['command_id', 'idempotency_key', 'action_digest', 'target', 'action', 'expected_policy_version', 'retry_class', 'deadline']`
  - `$/properties/command_id`: `type=string`, `minLength=1`
  - `$/properties/idempotency_key`: `type=string`, `minLength=16`
  - `$/properties/action_digest`: `type=string`, `pattern=^[a-f0-9]{64}$`
  - `$/properties/target`: `type=string`, `minLength=1`
  - `$/properties/action`: `type=object`, `additionalProperties=False`, `required=['capability', 'parameters']`
  - `$/properties/action/properties/capability`: `type=string`, `minLength=1`
  - `$/properties/action/properties/parameters`: `type=object`
  - `$/properties/expected_policy_version`: `type=integer`, `minimum=0`
  - `$/properties/retry_class`: `enum=['safe_retry', 'retry_after_reconcile', 'never_auto_retry', 'policy_recheck', 'manual_review']`
  - `$/properties/deadline`: `type=string`, `format=date-time`
  - `$/properties/lease`: `type=object`, `additionalProperties=False`
  - `$/properties/lease/properties/owner`: `type=string`
  - `$/properties/lease/properties/epoch`: `type=integer`, `minimum=0`
  - `$/properties/lease/properties/expires_at`: `type=string`, `format=date-time`

### `PRAIN_Distributed_Protocol_v0.5.0/schemas/execution-receipt.schema.json`

- ID: `https://prain.dev/schemas/execution-receipt-0.5.0.json`
- Required at root: `receipt_id, command_id, status, attempt, observed_at, executor, evidence_refs`
- Root properties: `receipt_id, command_id, status, attempt, observed_at, executor, error_code, evidence_refs, reconciliation`
- Nested constraint nodes: 11
  - `$`: `type=object`, `additionalProperties=False`, `required=['receipt_id', 'command_id', 'status', 'attempt', 'observed_at', 'executor', 'evidence_refs']`
  - `$/properties/receipt_id`: `type=string`, `minLength=1`
  - `$/properties/command_id`: `type=string`, `minLength=1`
  - `$/properties/status`: `enum=['accepted', 'running', 'succeeded', 'failed', 'unknown', 'reconciling', 'cancelled']`
  - `$/properties/attempt`: `type=integer`, `minimum=1`
  - `$/properties/observed_at`: `type=string`, `format=date-time`
  - `$/properties/executor`: `type=string`, `minLength=1`
  - `$/properties/error_code`: `type=string`
  - `$/properties/evidence_refs`: `type=array`
  - `$/properties/evidence_refs/items`: `type=string`
  - `$/properties/reconciliation`: `type=object`

### `PRAIN_Distributed_Protocol_v0.5.0/schemas/message-envelope.schema.json`

- ID: `https://prain.dev/schemas/message-envelope-0.5.0.json`
- Required at root: `message_id, message_type, schema_version, created_at, producer, correlation_id, tenant_id, payload, classification`
- Root properties: `message_id, message_type, schema_version, created_at, producer, correlation_id, causation_id, tenant_id, aggregate, payload, provenance, trace, classification, expires_at`
- Nested constraint nodes: 21
  - `$`: `type=object`, `additionalProperties=False`, `required=['message_id', 'message_type', 'schema_version', 'created_at', 'producer', 'correlation_id', 'tenant_id', 'payload', 'classification']`
  - `$/properties/message_id`: `type=string`, `minLength=1`, `maxLength=200`
  - `$/properties/message_type`: `enum=['command', 'event', 'query', 'response', 'receipt', 'control']`
  - `$/properties/schema_version`: `type=string`, `pattern=^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$`
  - `$/properties/created_at`: `type=string`, `format=date-time`
  - `$/properties/producer`: `type=object`, `additionalProperties=False`, `required=['node_id', 'service']`
  - `$/properties/producer/properties/node_id`: `type=string`, `minLength=1`
  - `$/properties/producer/properties/service`: `type=string`, `minLength=1`
  - `$/properties/producer/properties/instance_id`: `type=string`
  - `$/properties/correlation_id`: `type=string`, `minLength=1`
  - `$/properties/causation_id`: `type=string`
  - `$/properties/tenant_id`: `type=string`, `minLength=1`
  - `$/properties/aggregate`: `type=object`, `additionalProperties=False`, `required=['type', 'id', 'version']`
  - `$/properties/aggregate/properties/type`: `type=string`
  - `$/properties/aggregate/properties/id`: `type=string`
  - `$/properties/aggregate/properties/version`: `type=integer`, `minimum=0`
  - `$/properties/payload`: `type=object`
  - `$/properties/provenance`: `type=object`
  - `$/properties/trace`: `type=object`
  - `$/properties/classification`: `enum=['public', 'internal', 'confidential', 'restricted']`
  - `$/properties/expires_at`: `type=string`, `format=date-time`

### `PRAIN_Phase0_v0.2.1/schemas/action-request.schema.json`

- ID: `https://prain.dev/schema/action-request-0.1.0.json`
- Required at root: `id, actor_id, capability, target, declared_side_effects, risk_level, policy_decision_ref, correlation_id, idempotency_key, schema_version`
- Root properties: `id, actor_id, capability, target, input_ref, declared_side_effects, risk_level, policy_decision_ref, approval_ref, correlation_id, causation_id, idempotency_key, schema_version`
- Nested constraint nodes: 15
  - `$`: `type=object`, `additionalProperties=False`, `required=['id', 'actor_id', 'capability', 'target', 'declared_side_effects', 'risk_level', 'policy_decision_ref', 'correlation_id', 'idempotency_key', 'schema_version']`
  - `$/properties/id`: `type=string`
  - `$/properties/actor_id`: `type=string`
  - `$/properties/capability`: `type=string`
  - `$/properties/target`: `type=string`
  - `$/properties/input_ref`: `type=string`
  - `$/properties/declared_side_effects`: `type=array`
  - `$/properties/declared_side_effects/items`: `type=string`
  - `$/properties/risk_level`: `enum=['low', 'medium', 'high', 'critical']`
  - `$/properties/policy_decision_ref`: `type=string`
  - `$/properties/approval_ref`: `type=string`
  - `$/properties/correlation_id`: `type=string`
  - `$/properties/causation_id`: `type=string`
  - `$/properties/idempotency_key`: `type=string`
  - `$/properties/schema_version`: `type=string`

### `PRAIN_Phase0_v0.2.1/schemas/action-result.schema.json`

- ID: `https://prain.dev/schema/action-result-0.1.0.json`
- Required at root: `id, action_request_id, execution_status, verification_status, occurred_at, schema_version`
- Root properties: `id, action_request_id, execution_status, output_ref, side_effects_observed, verification_status, verification_evidence_refs, error_code, occurred_at, schema_version`
- Nested constraint nodes: 13
  - `$`: `type=object`, `additionalProperties=False`, `required=['id', 'action_request_id', 'execution_status', 'verification_status', 'occurred_at', 'schema_version']`
  - `$/properties/id`: `type=string`
  - `$/properties/action_request_id`: `type=string`
  - `$/properties/execution_status`: `enum=['accepted', 'running', 'completed', 'failed', 'timed_out', 'cancelled', 'unknown']`
  - `$/properties/output_ref`: `type=string`
  - `$/properties/side_effects_observed`: `type=array`
  - `$/properties/side_effects_observed/items`: `type=string`
  - `$/properties/verification_status`: `enum=['unverified', 'partially_verified', 'verified', 'rejected', 'inconclusive']`
  - `$/properties/verification_evidence_refs`: `type=array`
  - `$/properties/verification_evidence_refs/items`: `type=string`
  - `$/properties/error_code`: `type=string`
  - `$/properties/occurred_at`: `type=string`, `format=date-time`
  - `$/properties/schema_version`: `type=string`

### `PRAIN_Phase0_v0.2.1/schemas/agent-manifest.schema.json`

- ID: `https://prain.dev/schema/agent-manifest-0.1.0.json`
- Required at root: `agent_id, identity_version, role, capabilities, limitations, schema_version`
- Root properties: `agent_id, identity_version, role, capabilities, limitations, model_adapter, memory_adapter, runtime_adapter, identity_claim_refs, schema_version`
- Nested constraint nodes: 14
  - `$`: `type=object`, `additionalProperties=False`, `required=['agent_id', 'identity_version', 'role', 'capabilities', 'limitations', 'schema_version']`
  - `$/properties/agent_id`: `type=string`
  - `$/properties/identity_version`: `type=integer`, `minimum=1`
  - `$/properties/role`: `type=string`
  - `$/properties/capabilities`: `type=array`, `uniqueItems=True`
  - `$/properties/capabilities/items`: `type=string`
  - `$/properties/limitations`: `type=array`
  - `$/properties/limitations/items`: `type=string`
  - `$/properties/model_adapter`: `type=string`
  - `$/properties/memory_adapter`: `type=string`
  - `$/properties/runtime_adapter`: `type=string`
  - `$/properties/identity_claim_refs`: `type=array`
  - `$/properties/identity_claim_refs/items`: `type=string`
  - `$/properties/schema_version`: `type=string`

### `PRAIN_Phase0_v0.2.1/schemas/claim.schema.json`

- ID: `https://prain.dev/schema/claim-0.1.0.json`
- Required at root: `id, statement, kind, verification_status, created_at, schema_version`
- Root properties: `id, statement, kind, subject_id, predicate, object_ref, evidence_refs, confidence, verification_status, valid_from, valid_until, created_at, schema_version, verification_exception_ref`
- Nested constraint nodes: 16
  - `$`: `type=object`, `additionalProperties=False`, `required=['id', 'statement', 'kind', 'verification_status', 'created_at', 'schema_version']`
  - `$/properties/id`: `type=string`
  - `$/properties/statement`: `type=string`, `minLength=1`
  - `$/properties/kind`: `enum=['observed', 'inferred', 'hypothesis', 'proposal', 'externally_asserted']`
  - `$/properties/subject_id`: `type=string`
  - `$/properties/predicate`: `type=string`
  - `$/properties/object_ref`: `type=string`
  - `$/properties/evidence_refs`: `type=array`
  - `$/properties/evidence_refs/items`: `type=string`
  - `$/properties/confidence`: `type=number`, `minimum=0`, `maximum=1`
  - `$/properties/verification_status`: `enum=['unverified', 'partially_verified', 'verified', 'rejected', 'inconclusive']`
  - `$/properties/valid_from`: `type=string`, `format=date-time`
  - `$/properties/valid_until`: `type=string`, `format=date-time`
  - `$/properties/created_at`: `type=string`, `format=date-time`
  - `$/properties/schema_version`: `type=string`
  - `$/properties/verification_exception_ref`: `type=string`

### `PRAIN_Phase0_v0.2.1/schemas/event-envelope.schema.json`

- ID: `https://prain.dev/schema/event-envelope-0.1.0.json`
- Required at root: `event_id, event_type, occurred_at, producer, correlation_id, schema_version, payload`
- Root properties: `event_id, event_type, occurred_at, producer, correlation_id, causation_id, idempotency_key, schema_version, payload, trace_context`
- Nested constraint nodes: 11
  - `$`: `type=object`, `additionalProperties=False`, `required=['event_id', 'event_type', 'occurred_at', 'producer', 'correlation_id', 'schema_version', 'payload']`
  - `$/properties/event_id`: `type=string`
  - `$/properties/event_type`: `type=string`
  - `$/properties/occurred_at`: `type=string`, `format=date-time`
  - `$/properties/producer`: `type=string`
  - `$/properties/correlation_id`: `type=string`
  - `$/properties/causation_id`: `type=string`
  - `$/properties/idempotency_key`: `type=string`
  - `$/properties/schema_version`: `type=string`
  - `$/properties/payload`: `type=object`
  - `$/properties/trace_context`: `type=object`, `additionalProperties=schema-object`

### `PRAIN_Phase0_v0.2.1/schemas/evidence.schema.json`

- ID: `https://prain.dev/schema/evidence-0.2.0.json`
- Required at root: `id, kind, source_ref, captured_at, integrity, schema_version`
- Root properties: `id, kind, source_ref, captured_at, content_hash, integrity, classification, retention_policy_ref, schema_version`
- Nested constraint nodes: 10
  - `$`: `type=object`, `additionalProperties=False`, `required=['id', 'kind', 'source_ref', 'captured_at', 'integrity', 'schema_version']`
  - `$/properties/id`: `type=string`
  - `$/properties/kind`: `enum=['observation', 'document', 'tool_result', 'test_result', 'human_attestation', 'external_source']`
  - `$/properties/source_ref`: `type=string`
  - `$/properties/captured_at`: `type=string`, `format=date-time`
  - `$/properties/content_hash`: `type=string`
  - `$/properties/integrity`: `enum=['unchecked', 'hash_checked', 'signature_checked', 'invalid']`
  - `$/properties/classification`: `enum=['public', 'internal', 'confidential', 'secret']`
  - `$/properties/retention_policy_ref`: `type=string`
  - `$/properties/schema_version`: `type=string`

### `PRAIN_Phase0_v0.2.1/schemas/goal.schema.json`

- ID: `https://prain.dev/schema/goal-0.1.0.json`
- Required at root: `id, description, status, priority, acceptance_criteria, version, created_at`
- Root properties: `id, description, status, priority, owner_id, parent_goal_id, constraints, acceptance_criteria, version, created_at, updated_at`
- Nested constraint nodes: 18
  - `$`: `type=object`, `additionalProperties=False`, `required=['id', 'description', 'status', 'priority', 'acceptance_criteria', 'version', 'created_at']`
  - `$/properties/id`: `type=string`
  - `$/properties/description`: `type=string`, `minLength=1`
  - `$/properties/status`: `enum=['proposed', 'active', 'blocked', 'succeeded', 'failed', 'cancelled', 'superseded']`
  - `$/properties/priority`: `type=integer`, `minimum=0`, `maximum=100`
  - `$/properties/owner_id`: `type=string`
  - `$/properties/parent_goal_id`: `type=string`
  - `$/properties/constraints`: `type=array`
  - `$/properties/constraints/items`: `type=string`
  - `$/properties/acceptance_criteria`: `type=array`, `minItems=1`
  - `$/properties/acceptance_criteria/items`: `type=object`, `additionalProperties=False`, `required=['id', 'description', 'verification_method']`
  - `$/properties/acceptance_criteria/items/properties/id`: `type=string`
  - `$/properties/acceptance_criteria/items/properties/description`: `type=string`
  - `$/properties/acceptance_criteria/items/properties/verification_method`: `type=string`
  - `$/properties/acceptance_criteria/items/properties/passed`: `type=['boolean', 'null']`
  - `$/properties/version`: `type=integer`, `minimum=1`
  - `$/properties/created_at`: `type=string`, `format=date-time`
  - `$/properties/updated_at`: `type=string`, `format=date-time`

### `PRAIN_Phase0_v0.2.1/schemas/observation.schema.json`

- ID: `https://prain.dev/schema/observation-0.1.0.json`
- Required at root: `id, type, source, occurred_at, schema_version, payload_ref`
- Root properties: `id, type, source, occurred_at, received_at, schema_version, payload_ref, content_hash, confidence, provenance, correlation_id, labels`
- Nested constraint nodes: 18
  - `$`: `type=object`, `additionalProperties=False`, `required=['id', 'type', 'source', 'occurred_at', 'schema_version', 'payload_ref']`
  - `$/properties/id`: `type=string`, `minLength=1`
  - `$/properties/type`: `type=string`, `minLength=1`
  - `$/properties/source`: `type=object`, `additionalProperties=False`, `required=['source_id', 'adapter']`
  - `$/properties/source/properties/source_id`: `type=string`
  - `$/properties/source/properties/adapter`: `type=string`
  - `$/properties/source/properties/uri`: `type=string`
  - `$/properties/occurred_at`: `type=string`, `format=date-time`
  - `$/properties/received_at`: `type=string`, `format=date-time`
  - `$/properties/schema_version`: `type=string`, `pattern=^\d+\.\d+\.\d+$`
  - `$/properties/payload_ref`: `type=string`, `minLength=1`
  - `$/properties/content_hash`: `type=string`
  - `$/properties/confidence`: `type=number`, `minimum=0`, `maximum=1`
  - `$/properties/provenance`: `type=array`
  - `$/properties/provenance/items`: `type=string`
  - `$/properties/correlation_id`: `type=string`
  - `$/properties/labels`: `type=array`
  - `$/properties/labels/items`: `type=string`

### `PRAIN_Phase0_v0.2.1/schemas/policy-decision.schema.json`

- ID: `https://prain.dev/schema/policy-decision-0.1.0.json`
- Required at root: `id, action_request_id, decision, rule_refs, reason, decided_at, policy_version`
- Root properties: `id, action_request_id, decision, rule_refs, reason, decided_at, policy_version, approval_ref`
- Nested constraint nodes: 10
  - `$`: `type=object`, `additionalProperties=False`, `required=['id', 'action_request_id', 'decision', 'rule_refs', 'reason', 'decided_at', 'policy_version']`
  - `$/properties/id`: `type=string`
  - `$/properties/action_request_id`: `type=string`
  - `$/properties/decision`: `enum=['allow', 'deny', 'require_approval', 'defer']`
  - `$/properties/rule_refs`: `type=array`
  - `$/properties/rule_refs/items`: `type=string`
  - `$/properties/reason`: `type=string`
  - `$/properties/decided_at`: `type=string`, `format=date-time`
  - `$/properties/policy_version`: `type=string`
  - `$/properties/approval_ref`: `type=string`

### `PRAIN_Phase0_v0.2.1/schemas/state-snapshot.schema.json`

- ID: `https://prain.dev/schema/state-snapshot-0.2.0.json`
- Required at root: `id, entity_type, version, updated_at, data, schema_version`
- Root properties: `id, entity_type, version, updated_at, data, content_classification, retention_policy_ref, schema_version`
- Nested constraint nodes: 9
  - `$`: `type=object`, `additionalProperties=False`, `required=['id', 'entity_type', 'version', 'updated_at', 'data', 'schema_version']`
  - `$/properties/id`: `type=string`
  - `$/properties/entity_type`: `type=string`
  - `$/properties/version`: `type=integer`, `minimum=1`
  - `$/properties/updated_at`: `type=string`, `format=date-time`
  - `$/properties/data`: `type=object`
  - `$/properties/content_classification`: `enum=['public', 'internal', 'confidential', 'secret']`
  - `$/properties/retention_policy_ref`: `type=string`
  - `$/properties/schema_version`: `type=string`

### `PRAIN_Phase0_v0.2.1/schemas/trace-event.schema.json`

- ID: `https://prain.dev/schema/trace-event-0.2.0.json`
- Required at root: `trace_id, span_id, event_id, timestamp, component, operation, outcome, schema_version`
- Root properties: `trace_id, span_id, parent_span_id, event_id, timestamp, component, operation, outcome, policy_decision_ref, redaction_applied, schema_version`
- Nested constraint nodes: 12
  - `$`: `type=object`, `additionalProperties=False`, `required=['trace_id', 'span_id', 'event_id', 'timestamp', 'component', 'operation', 'outcome', 'schema_version']`
  - `$/properties/trace_id`: `type=string`
  - `$/properties/span_id`: `type=string`
  - `$/properties/parent_span_id`: `type=string`
  - `$/properties/event_id`: `type=string`
  - `$/properties/timestamp`: `type=string`, `format=date-time`
  - `$/properties/component`: `type=string`
  - `$/properties/operation`: `type=string`
  - `$/properties/outcome`: `enum=['success', 'failure', 'denied', 'deferred', 'unknown']`
  - `$/properties/policy_decision_ref`: `type=string`
  - `$/properties/redaction_applied`: `type=boolean`
  - `$/properties/schema_version`: `type=string`

### `PRAIN_v0.6/schemas/health-signal.schema.json`

- ID: `https://prain.example/schemas/v0.6/health-signal.schema.json`
- Required at root: `schema_version, signal_id, observed_at, scope, metric, status, source`
- Root properties: `schema_version, signal_id, observed_at, scope, metric, value, unit, status, threshold_ref, source, evidence_refs, fresh_until`
- Nested constraint nodes: 18
  - `$`: `type=object`, `additionalProperties=False`, `required=['schema_version', 'signal_id', 'observed_at', 'scope', 'metric', 'status', 'source']`
  - `$/properties/schema_version`: `type=string`, `const=0.6.0`
  - `$/properties/signal_id`: `type=string`, `minLength=1`
  - `$/properties/observed_at`: `type=string`, `format=date-time`
  - `$/properties/scope`: `type=object`, `additionalProperties=False`, `required=['kind', 'id']`
  - `$/properties/scope/properties/kind`: `enum=['unit', 'group', 'global', 'resource']`
  - `$/properties/scope/properties/id`: `type=string`, `minLength=1`
  - `$/properties/metric`: `type=string`, `minLength=1`
  - `$/properties/value`: `type=['number', 'string', 'boolean', 'null']`
  - `$/properties/unit`: `type=string`
  - `$/properties/status`: `enum=['healthy', 'degraded', 'critical', 'unknown', 'stale']`
  - `$/properties/threshold_ref`: `type=string`
  - `$/properties/source`: `type=object`, `additionalProperties=False`, `required=['id', 'version']`
  - `$/properties/source/properties/id`: `type=string`, `minLength=1`
  - `$/properties/source/properties/version`: `type=string`, `minLength=1`
  - `$/properties/evidence_refs`: `type=array`, `uniqueItems=True`
  - `$/properties/evidence_refs/items`: `type=string`
  - `$/properties/fresh_until`: `type=string`, `format=date-time`

### `PRAIN_v0.6/schemas/repair-proposal.schema.json`

- ID: `https://prain.example/schemas/v0.6/repair-proposal.schema.json`
- Required at root: `schema_version, proposal_id, created_at, target, observation_refs, change, bounds, rollout, success_metrics, rollback_conditions, expires_at`
- Root properties: `schema_version, proposal_id, created_at, target, observation_refs, change, bounds, rollout, success_metrics, rollback_conditions, expires_at, status`
- Nested constraint nodes: 24
  - `$`: `type=object`, `additionalProperties=False`, `required=['schema_version', 'proposal_id', 'created_at', 'target', 'observation_refs', 'change', 'bounds', 'rollout', 'success_metrics', 'rollback_conditions', 'expires_at']`
  - `$/properties/schema_version`: `type=string`, `const=0.6.0`
  - `$/properties/proposal_id`: `type=string`, `minLength=1`
  - `$/properties/created_at`: `type=string`, `format=date-time`
  - `$/properties/target`: `type=object`, `additionalProperties=False`, `required=['kind', 'id']`
  - `$/properties/target/properties/kind`: `enum=['unit', 'group', 'projection', 'workflow', 'provider', 'scheduler']`
  - `$/properties/target/properties/id`: `type=string`, `minLength=1`
  - `$/properties/observation_refs`: `type=array`, `minItems=1`, `uniqueItems=True`
  - `$/properties/observation_refs/items`: `type=string`, `minLength=1`
  - `$/properties/change`: `type=object`, `additionalProperties=False`, `required=['operation', 'parameters']`
  - `$/properties/change/properties/operation`: `enum=['replay_idempotent_messages', 'rebuild_projection', 'resume_checkpoint', 'reconcile_action', 'adjust_concurrency', 'refresh_cache', 'route_workload', 'pause_workflow', 'rollback_release']`
  - `$/properties/change/properties/parameters`: `type=object`
  - `$/properties/bounds`: `type=object`, `additionalProperties=False`, `required=['policy_ref', 'max_attempts', 'max_resource_delta']`
  - `$/properties/bounds/properties/policy_ref`: `type=string`, `minLength=1`
  - `$/properties/bounds/properties/max_attempts`: `type=integer`, `minimum=1`, `maximum=100`
  - `$/properties/bounds/properties/max_resource_delta`: `type=number`, `minimum=0`
  - `$/properties/bounds/properties/requires_approval`: `type=boolean`
  - `$/properties/rollout`: `enum=['observe_only', 'single_target', 'canary', 'staged', 'immediate_preapproved']`
  - `$/properties/success_metrics`: `type=array`, `minItems=1`
  - `$/properties/success_metrics/items`: `type=string`, `minLength=1`
  - `$/properties/rollback_conditions`: `type=array`, `minItems=1`
  - `$/properties/rollback_conditions/items`: `type=string`, `minLength=1`
  - `$/properties/expires_at`: `type=string`, `format=date-time`
  - `$/properties/status`: `enum=['proposed', 'accepted', 'rejected', 'deferred', 'require_approval', 'applied', 'rolled_back']`

### `PRAIN_v0.6/schemas/semantic-message.schema.json`

- ID: `https://prain.example/schemas/v0.6/semantic-message.schema.json`
- Required at root: `schema_version, message_id, message_type, created_at, producer, scope, epistemic_status, payload, provenance`
- Root properties: `schema_version, message_id, correlation_id, causation_id, message_type, created_at, producer, scope, epistemic_status, aggregate, affected_dependencies, valid_until, confidence, payload, provenance, required_response, idempotency_key, trace_id`
- Nested constraint nodes: 31
  - `$`: `type=object`, `additionalProperties=False`, `required=['schema_version', 'message_id', 'message_type', 'created_at', 'producer', 'scope', 'epistemic_status', 'payload', 'provenance']`
  - `$/properties/schema_version`: `type=string`, `const=0.6.0`
  - `$/properties/message_id`: `type=string`, `minLength=1`
  - `$/properties/correlation_id`: `type=string`, `minLength=1`
  - `$/properties/causation_id`: `type=string`, `minLength=1`
  - `$/properties/message_type`: `enum=['observation', 'hypothesis', 'claim', 'invalidation', 'command', 'receipt', 'reconciliation_request', 'health_signal', 'repair_proposal', 'verification_result']`
  - `$/properties/created_at`: `type=string`, `format=date-time`
  - `$/properties/producer`: `type=object`, `additionalProperties=False`, `required=['id', 'version']`
  - `$/properties/producer/properties/id`: `type=string`, `minLength=1`
  - `$/properties/producer/properties/version`: `type=string`, `minLength=1`
  - `$/properties/producer/properties/capability`: `type=string`
  - `$/properties/scope`: `type=object`, `additionalProperties=False`, `required=['kind', 'id']`
  - `$/properties/scope/properties/kind`: `enum=['unit', 'group', 'global', 'resource']`
  - `$/properties/scope/properties/id`: `type=string`, `minLength=1`
  - `$/properties/epistemic_status`: `enum=['observed', 'hypothesis', 'supported', 'confirmed', 'refuted', 'unknown']`
  - `$/properties/aggregate`: `type=object`, `additionalProperties=False`, `required=['id', 'version']`
  - `$/properties/aggregate/properties/id`: `type=string`, `minLength=1`
  - `$/properties/aggregate/properties/version`: `type=integer`, `minimum=0`
  - `$/properties/affected_dependencies`: `type=array`, `uniqueItems=True`
  - `$/properties/affected_dependencies/items`: `type=string`, `minLength=1`
  - `$/properties/valid_until`: `type=string`, `format=date-time`
  - `$/properties/confidence`: `type=number`, `minimum=0`, `maximum=1`
  - `$/properties/payload`: `type=object`
  - `$/properties/provenance`: `type=array`, `minItems=1`
  - `$/properties/provenance/items`: `type=object`, `additionalProperties=False`, `required=['source_id', 'relation']`
  - `$/properties/provenance/items/properties/source_id`: `type=string`, `minLength=1`
  - `$/properties/provenance/items/properties/relation`: `enum=['observed_from', 'derived_from', 'supports', 'contradicts', 'supersedes', 'verified_by']`
  - `$/properties/provenance/items/properties/version`: `type=string`
  - `$/properties/required_response`: `enum=['none', 'acknowledge', 'request_evidence', 'reconcile', 'verify']`
  - `$/properties/idempotency_key`: `type=string`, `minLength=1`
  - `$/properties/trace_id`: `type=string`, `minLength=1`

