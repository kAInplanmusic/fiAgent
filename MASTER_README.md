# PRAIN — Master README

**Stand:** 2026-10-20  | **Phase 0:** GREEN (`v0.99.6`, 100% der deklarierten Phase-0-Gates bestanden) | **Phase 1 Runtime / Gesamt-Audit:** PARTIAL_PASS.

## Kurzfassung

P.R.A.I.N. steht für **Perception, Reason, Anima, Intention, Nerve** und bezeichnet ein eigenständiges semantisches Framework zur strukturierten Orchestrierung autonomer Agenten. Die fünf Dimensionen sind logische Verantwortlichkeiten, nicht zwingend fünf getrennte Prozesse. Identität entsteht aus ihrem Zusammenspiel; `Anima` ist ein explizites, prüfbares Selbstmodell und keine Behauptung von Bewusstsein.

„Quantum-ready“ bedeutet austauschbare Provider- und Compute-Schnittstellen. Es ist **keine** Behauptung, dass Quantenhardware genutzt wird oder ein Quantenvorteil existiert.

## Architektur in einem Blick

- **P — Perception:** Beobachtungen normalisieren, Herkunft/Unsicherheit erhalten.
- **R — Reason:** interpretieren, folgern, vergleichen und planen.
- **A — Anima:** versioniertes, inspizierbares Selbstmodell und Kontinuität.
- **I — Intention:** Ziele, Prioritäten, Abhängigkeiten und Abnahmekriterien.
- **N — Nerve:** ausschließlich autorisierte Aktionen über austauschbare Adapter.
- **SCF — Semantic Coordination Fabric:** semantische Koordination, Provenienz, Projektionen, Konflikterkennung und Abgleich.
- **HAL — Homeostasis & Adaptation Layer:** Zustand beobachten und begrenzte Reparatur-/Anpassungsvorschläge steuern; keine sechste Kerndimension.
- **Invariant & Evidence Layer:** schützt maßgebliche Zustände, Berechtigungen, Versionen, Receipts und unabhängige Verifikation.

## Zentrale Architekturregeln

- Standardmäßig verweigern; geringste Berechtigung; Freigaben an konkrete Aktionen binden.
- At-least-once-Zustellung und idempotente Verbraucher annehmen; kein globales Exactly-once versprechen.
- Autoritative Zustände versionieren und per CAS aktualisieren; Projektionen dürfen autoritative Daten nicht überschreiben.
- Unklare Ausführungsergebnisse dauerhaft festhalten und vor einem Retry abgleichen; Lease-Ablauf beweist nicht, dass eine Aktion nicht lief.
- Ziele nur nach Evidenzprüfung sämtlicher Abnahmekriterien als abgeschlossen markieren.
- UTC/RFC3339-Zeitstempel, SemVer für Schemas; UUIDv7 ist als bevorzugte ID-Strategie dokumentiert.
- Klassifikation, Aufbewahrung, Redaktion und Löschung auch für abgeleitete Indizes/Caches berücksichtigen.
- NATS JetStream und PostgreSQL sind Kandidaten, keine festgelegten Implementierungsabhängigkeiten.

## Versions- und Statusübersicht

| Stand | Rolle | Aussage |
|---|---|---|
| v0.1.0–v0.2.1 | frühe Phase-0-Verträge | Historische Basis und Vertragsentwicklung |
| v0.4.0 | Architektur | P/R/A/I/N, Identität, Kommunikation, Fehlerbehandlung und Traceability vertieft |
| v0.5.0 | Distributed Protocol | Konsistenz, Retry, Inbox/Outbox, Leases/Fencing und Recovery spezifiziert |
| v0.6 | Architekturvertiefung | SCF, HAL, Invarianten/Evidenz, Multiskalen-Koordination |
| v0.7.0–v0.9.4 | Konsolidierung/Audits | Rückverfolgbarkeit, Schema- und Wissensbasis-Audits, Semantik und Abnahmekriterien |
| v0.99.0–v0.99.4 | Release-Kandidaten | Abschluss-, Semantik-, Zustandsautomaten- und Schema-Konformitätsprüfungen |
| v1.0.0 | Closure-/Start-Gate | Release-Artefakt dokumentiert Phase 0 als geschlossen und Phase 1 als zum Start autorisiert; kein Produktionsfreigabeschein |
| v1.1.0 | Referenzprototyp | Lokaler, in-memory Python-Vertikalpfad; keine produktiven externen Aktionen |

## Verifizierungsgrenzen und bekannte Abweichungen

- Phase-0-Validierung prüft Spezifikation, Referenzen und Paketstruktur; sie zertifiziert weder Runtime noch Sicherheit oder Produktionsbetrieb.
- Der v1.1.0-Statusbericht nennt 22 Tests; eine erneute lokale Testausführung ergab 23 bestanden. Diese Differenz ist im nächsten Dokumentationsupdate zu korrigieren.
- Prüfzahlen 310, 319 und 325 stammen aus unterschiedlichen Ständen/Prüfumfängen. Nicht addieren oder als dieselbe Suite darstellen; Ergebnisse müssen je Validator-Version ausgewiesen werden.
- Das Prototypverhalten belegt nicht die vollständige Runtime-Durchsetzung aller Phase-0-Schemas und Guardrails.
- Nicht geliefert: dauerhafte Persistenz/Wiederanlauf, produktive Connectoren, authentifizierte/signierte Genehmigungsgeber, atomarer Einmalverbrauch von Freigaben, dauerhafter Broker, Retry-/Dead-letter-Verarbeitung, HTTP API, Multi-Tenant-Authentifizierung, Secret-Management, produktive Telemetrie und Deployment.
- Historische Unterlagen mit älterem Sperrstatus bleiben als Historie erhalten; die jeweils maßgebliche Entscheidung muss im Index eindeutig referenziert werden.

## Einstieg

1. `ROADMAP.md` — durchgängiger Arbeitsplan und offene Gates.
2. `docs/MASTER_AUDIT_STATUS.md` — Rückverfolgbarkeits- und Konsolidierungsstatus.
3. `archive/` — die zum Zeitpunkt der Erstellung vorhandenen PRAIN-Dateien und historischen Pakete unverändert gesammelt.
4. Für den verbindlichen Phase-0-Abschluss das Paket `archive/PRAIN_v0.99.6_Phase0_Green_Closure.zip` und `archive/PRAIN_v0.99.6_integrity.json` verwenden; v0.99.4 bleibt die unveränderte Baseline.
5. Für den Phase-1-Prototyp `PRAIN_v1.1.0_Phase1_Reference_Prototype.zip` und `docs/PHASE1_IMPLEMENTATION_STATUS.md` verwenden.

## Änderungsregel

Keine historische Anforderung stillschweigend entfernen. Jede Anforderung erhält eine ID und den Status **retained**, **extended**, **superseded**, **open** oder **deferred**, plus Quelle, Beleg, Test und Folgeentscheidung. Ein grüner Test zählt nur für seinen dokumentierten Umfang.


Latest prototype: `archive/PRAIN_v1.1.8_Phase1_Reference_Prototype` (durable SQLite state adapter; 55/55 tests passing). Overall audit remains `PARTIAL_PASS`; no production readiness or exactly-once external effects are claimed.


## Latest implementation step

Step 12 (`v1.1.7`) adds local crash-window recovery and multi-process contention tests. The complete unit suite passes 51/51. This is still a `PARTIAL_PASS`: provider-boundary fault injection and production readiness remain unverified. See `docs/STEP12_FAULT_INJECTION_AND_MULTIPROCESS_TESTS.md`.


Step 13 (`v1.1.8`) adds an opt-in SQLite-backed versioned state store with restart persistence and transactional compare-and-swap. GoalRegistry, EventBus and EvidenceLedger are still in-memory; see `docs/STEP13_DURABLE_STATE_STORE.md`.


## Aktueller Implementierungsstand — 2026-10-20

- Neuester Referenzprototyp: **v1.1.9 / Schritt 14**.
- Letzte Regression: **59 Tests bestanden, 0 fehlgeschlagen, 0 Fehler**.
- Neu: SQLite-Adapter für Goals, Event-Log/Consumer-Reservierungen und Evidence-Ledger; aktivierbar über `PRAINRuntime(persistent_db_path=...)`.
- Gesamt-Gate bleibt **PARTIAL_PASS**. Der Runtime-StateStore ist nicht automatisch persistent verdrahtet; Event-Handler-Zustellung ist nicht crash-sicher at-least-once; keine Produktionsfreigabe.
- Details: `docs/STEP14_DURABLE_RUNTIME_COMPONENTS.md`.


## Phase 0 closure (2026-10-20)

Phase 0 is GREEN on release `v0.99.6`: 127/127 main, 221/221 semantic consistency, 504/504 state-machine, 65/65 schema/state-machine, 237/237 deep conformance, 324/324 internal release-bundle checks, and 330/330 final archive/integrity checks. See `docs/PHASE0_GREEN_CLOSURE.md`, `archive/PRAIN_v0.99.6_Phase0_Green_Closure.zip`, and `archive/PRAIN_v0.99.6_integrity.json`. Phase 1 remains NOT AUTHORIZED by the Phase-0 record; the overall master audit remains `PARTIAL_PASS`.
