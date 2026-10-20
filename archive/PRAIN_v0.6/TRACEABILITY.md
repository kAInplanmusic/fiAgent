# Traceability: v0.5 → v0.6

v0.6 deepens the v0.5 distributed protocol rather than discarding it.

| v0.5 concept | v0.6 treatment |
|---|---|
| At-least-once delivery + idempotent consumers | Retained in SCF |
| Transactional outbox/inbox | Retained for durable state/message coupling |
| CAS and aggregate versions | Retained for authoritative shared aggregates |
| Eventual projections | Expanded with freshness, dependency invalidation, and selective rebuild |
| Explicit conflict handling | Expanded to semantic conflict classes and hypothesis coexistence |
| Unknown external action outcome | Retained; reconciliation before retry |
| Policy gateway as sole authorizer | Retained in invariant boundary; HAL cannot bypass it |
| Evidence-backed goal completion | Retained and made criterion-level |
| Worker registry, heartbeat, leases/fencing | Retained as execution/scheduling capabilities |
| Conformance suite | Expanded with HAL stability and multiscale scope tests |
| Quantum-ready provider abstraction | Still means replaceable interfaces; no quantum advantage claim |
| P/R/A/I/N dimensions | Retained; multiscale layers are orthogonal organizational structure |

## Compatibility note

This package is a specification refactor. It does not modify the v0.5 ZIP or claim the previous protocol runtime exists. Implementations should preserve v0.5 envelope fields where practical and add v0.6 fields through an explicit schema-version migration.
