# Schritt 5 — Kanonische Invarianten gegen Runtime/Test-Evidenz

**Datum:** 2026-10-20  
**Normative Quelle:** `archive/PRAIN_v0.99.4_Phase0_Schema_State_Machine_Conformance/tests/invariants.json` und `tests/invariant_coverage.json`. 30 Invarianten wurden einzeln gegen den v1.1.0-Referenzprototyp und dessen Tests abgeglichen.

## Befund

Diese Crosswalk-Datei ist eine konservative Code-/Test-Evidenzbewertung, keine formale Verifikation. Ein fehlender Fund bedeutet „nicht nachgewiesen“, nicht zwingend „existiert nirgends“. Phase-0-Validatoren prüfen überwiegend Spezifikation, Schemas, Referenzorakel und Paketgrenzen; sie belegen nicht automatisch Runtime-Conformance.

| Assessment | Anzahl | Bedeutung |
|---|---:|---|
| `PARTIAL_RUNTIME` | 13 | Teilweise Runtime-Evidenz; direkte Negativtests/Umsetzung fehlen |
| `SPEC_ONLY` | 10 | Spezifiziert, aber Runtime-Umsetzung nicht belegt |
| `OPEN_RUNTIME_GAP` | 3 | Offene Runtime-Lücke mit potenziell kritischer Semantik |
| `DONE_SPEC_ONLY` | 2 | Phase-0-/Spezifikationsnachweis, keine Runtime-Aussage |
| `DONE_DOC_REVIEW` | 2 | Dokumentations-/Semantikprüfung |

## Wesentliche offene Runtime-Lücken

1. **Idempotenz dauerhaft und nebenläufig:** derselbe Schlüssel darf keine veränderte Aktion maskieren; benötigt persistente Eindeutigkeit und Race-Tests.
2. **Lease-Ablauf und externe Effekte:** Timeout/Lease-Ablauf beweist nicht, dass keine Wirkung eingetreten ist; vor Retry muss Reconciliation stattfinden.
3. **Widerruf direkt vor Dispatch:** frische Revocation-Prüfung und Rennen zwischen Prüfung und Dispatch testen.
4. **Tenant-Isolation und Delegation:** negative Tests für fehlenden/falschen Tenant und Delegation über Grantor-Rechte hinaus.
5. **Approval-/Digest-Bindung und fail-closed:** actor, target, side effects und command digest exakt binden; unknown/stale/expired/consumed/revoked muss deny/defer ergeben.
6. **CAS/Authority:** stale CAS, projection-vs-authority overwrite und Mutation-Aliasing unter Parallelität prüfen.
7. **Reconciliation/Evidence:** unknown outcome, doppelte Events, digest mismatch und post-effect revocation gezielt testen.
8. **Nicht im Prototyp nachgewiesene Lebenszyklen:** Claim-Verifikation, Reparaturfreigabe, Löschpropagation und HAL-Hard-Limits sind nicht als implementiert zu deklarieren.

## Interpretationsregel

Der bestandene Prototyp-Testlauf von 23/23 ist ein begrenzter Testbefund. Er ersetzt weder 30/30 Runtime-Invarianten noch Persistenz-, Crash-Recovery-, Multi-Process- oder verteilte Conformance-Tests. Gesamtstatus bleibt **`PARTIAL_PASS`**, Produktionsreife **`NOT ESTABLISHED`**.

Maschinenlesbare Einzelbewertung: `TRACEABILITY/CANONICAL_INVARIANT_RUNTIME_CROSSWALK.csv`.
