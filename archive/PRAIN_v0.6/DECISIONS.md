# Decision Register — PRAIN v0.6

| ID | Decision | Rationale |
|---|---|---|
| D-0601 | P/R/A/I/N remain the five functional dimensions | Prevents organizational layers being mistaken for new cognitive cores |
| D-0602 | Add multiscale organization: local unit, group, global semantic system, invariant boundary | Enables local autonomy without losing global constraints |
| D-0603 | Add HAL as a supervisory capability, not a sixth core | Provides feedback/repair/adaptation while keeping authority boundaries explicit |
| D-0604 | Global meaning does not require global synchronization of all data | Limits latency and coordination overhead while preserving declared invariants |
| D-0605 | Authority and consistency are declared per record class | Prevents accidental assumptions that all records need the same consistency model |
| D-0606 | Semantic claims require provenance and epistemic status | Distinguishes observation, hypothesis, evidence, and confirmation |
| D-0607 | Unknown external action outcome is first-class | Avoids unsafe retries after timeout/crash |
| D-0608 | HAL cannot grant permissions, alter hard ceilings, or self-modify live policy | Separates health optimization from authorization |
| D-0609 | First runtime should be modular, not prematurely microserviced | Keeps initial deployment operable and testable |
| D-0610 | Biological/processor analogies must map to falsifiable mechanisms | Avoids literal or mystical equivalence claims |

## Open decisions before production
- Concrete persistence and broker versions.
- Exact claim-type ontology and epistemic promotion rules.
- Tenant and principal model.
- Cryptographic signing/key rotation for evidence and messages.
- Retention/deletion policy per data class.
- SLOs for message lag, recovery time, and verification latency.
- Which adaptations may be preapproved for bounded automation.
- Whether and when group-level consensus is required for specific authoritative records.
