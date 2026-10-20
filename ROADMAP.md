# PRAIN — Durchgängiger Master-Wayplan / Roadmap

**Stand:** 2026-10-20  
**Ziel:** Einen nachvollziehbaren Pfad vom historischen Bestand über konsolidierte Spezifikation bis zu einem robusten, modularen Agenten-Orchestrator schaffen. Dieser Plan ist die führende Arbeitsliste; Änderungen müssen versioniert werden.

## Leitprinzipien

1. Semantik und Verträge vor Infrastruktur.
2. Ein kanonischer Vertrag pro Konzept; historische Quellen bleiben nachvollziehbar.
3. Jede Anforderung ist rückverfolgbar: Quelle → Entscheidung → Vertrag/Schema → Implementierung → Test/Evidenz.
4. Sicherheitsgrenzen fail-closed, Freigaben aktionsgebunden und widerrufbar.
5. Unbekannte Zustände werden sichtbar gemacht und abgeglichen, nicht geraten.
6. Provider, Speicher, Transport und Compute sind austauschbare Adapter; keine vorzeitige Bindung an einen Anbieter.
7. „Quantum-ready“ bleibt eine austauschbare Schnittstellenstrategie, keine unbelegte Leistungsbehauptung.
8. Keine Produktionsfreigabe allein aufgrund von Unit-Tests oder Spezifikationsprüfungen.

## Rückwirkendes Audit — Fortschritt

**Schritt 1 abgeschlossen (automatisierte Bestandsaufnahme, 2026-10-20):** `TRACEABILITY/SOURCE_REGISTER.csv` und `TRACEABILITY/REQUIREMENT_TRACEABILITY_MATRIX.csv` wurden erzeugt. Die Matrix enthält Kandidatenzeilen, nicht automatisch akzeptierte Anforderungen; nach historischem ZIP-Scan umfasst sie inzwischen 5071 Zeilen. Alle Zeilen bleiben offen, bis semantisch geprüft und auf normative Quelle/Schema/Code/Test abgebildet.

**Schritt 2 als nächstes:** historische Quellen v0.1.0 bis v0.6 und ursprüngliche Wissensdatenbank zeilenweise auswerten, Kandidaten-RTM ergänzen und jede Anforderung klassifizieren. Danach v0.7–v0.99.4 auf Änderungen und Widersprüche abgleichen.

## Statusdefinitionen

- **DONE-SPEC:** spezifiziert und im angegebenen Prüfumfang validiert; keine Implementierungsaussage.
- **PROTOTYPE:** in Referenzcode vorhanden, mit benannten Grenzen.
- **OPEN:** fehlender Beleg, ungelöste Abweichung oder noch nicht umgesetzte Arbeit.
- **BLOCKED:** kann erst nach einer benannten Entscheidung oder Voraussetzung beginnen.
- **ACCEPTED:** nur nach dokumentierter Abnahme durch Projektverantwortliche.

## Arbeitsstränge und Gates

### W0 — Bestand sichern und Quellen inventarisieren
**Status: teilweise belegt; Inventar konsolidiert, vollständige Einzelanforderungs-Rückverfolgung offen.**

- [x] Historische ZIPs und Wissensdatenbank-Artefakte im Bestand inventarisieren.
- [x] Frühere Versionen als Historie erhalten; keine stille Überschreibung.
- [ ] Für jede Datei SHA-256, Version, Zweck, Herkunft und kanonischen Nachfolger in maschinenlesbares Manifest aufnehmen.
- [ ] Prüfen, dass jedes historische Paket im Master-Archiv enthalten ist und lesbar entpackt werden kann.
- [ ] Alle frühen Anforderungen aus v0.1.0 bis v0.6 und Wissensdatenbank gegen aktuelle Spezifikation mappen.

**Gate W0:** Kein nicht klassifizierter historischer Punkt. Jede Anforderung ist retained / extended / superseded / open / deferred und besitzt eine Begründung.

### W1 — Kanonische Spezifikation und Traceability
**Status: DONE-SPEC im dokumentierten Umfang; finale vollständige Rückverfolgung noch offen.**

- [x] Architektur und P/R/A/I/N-Verantwortlichkeiten dokumentiert.
- [x] SCF, HAL sowie Invariant & Evidence Layer dokumentiert.
- [x] Schema-, Wissensbasis-, Claim-, Semantik- und Zustandsautomaten-Audits vorhanden.
- [x] Schema-/Zustandsautomaten-Crosswalk und normative State Machines vorhanden.
- [ ] Eine zentrale Requirement Traceability Matrix (RTM) erzeugen: Requirement-ID, Ursprung, Normtext, Status, Zieldokument, Schema/Code, Test, Befund, offene Aktion.
- [ ] Alle Links/IDs automatisiert auf Existenz und Eindeutigkeit prüfen.
- [ ] Terminologie-Dubletten und widersprüchliche Normtexte mit einer kanonischen Quelle bereinigen.
- [ ] Alte Statusangaben als HISTORICAL markieren; nur ein aktueller Freigabestatus pro Release.

**Gate W1:** Jede normative Aussage hat eine eindeutige Quelle, Version und nachvollziehbare Verifikation oder klaren offenen Status.

### W2 — Release- und Nachweisqualität
**Status: OPEN — Dokumentationsabweichungen festgestellt.**

- [ ] v1.1.0-Statusbericht von 22 Tests auf den nach erneuter Ausführung bestätigten Umfang aktualisieren, falls der Teststand unverändert ist.
- [ ] Zahlen 310/319/325 je Suite, Validator-Version, Datum und Scope erklären; nie als austauschbare Gesamtzahl behandeln.
- [ ] Alle Release-Integritätsdateien gegen tatsächliche Dateien neu berechnen und maschinell vergleichen.
- [ ] Einen einheitlichen `MANIFEST.json` und `SHA256SUMS` für das gesamte Master-Paket generieren.
- [ ] Release-Inhalt reproduzierbar aus einem sauberen Verzeichnis erzeugen; Paketinhalt und Hashes in CI prüfen.
- [ ] Abschlussbericht trennt Spezifikationsprüfungen, Unit-Tests, Integrationstests, Sicherheitsprüfungen und Produktionsvalidierung.

**Gate W2:** Reproduzierbares Paket; keine widersprüchlichen Zahlen ohne Erklärung; alle Hashes verifiziert.

### W3 — Phase-1-Prototyp: Vertragsdurchsetzung
**Status: PROTOTYPE; umfassende Schema-Runtime-Konformität OPEN.**

- [x] Lokaler vertikaler Pfad Observation → Event/Evidence → Evaluator → Policy → simulierte Aktion → Receipt → Evidenzkette.
- [x] In-memory CAS-State-Store, Zielregistrierung, Policy Gateway und Evidenz-Ledger im Referenzcode.
- [x] Lokale Unit-Tests und Demo dokumentiert; 23 Tests in der erneuten Ausführung bestanden.
- [ ] Kanonische Phase-0-Schemas beim Einlesen/Serialisieren tatsächlich validieren (nicht nur parallel dokumentieren).
- [ ] Schema-Round-trip-Tests und unbekannte/fehlende Felder, falsche Versionen, ungültige Enums und Grenzwerte testen.
- [ ] Zustandsautomaten-Properties und unerlaubte Transitionen gegen die normativen Automaten testen.
- [ ] Negative Tests: abgelaufene/verbrauchte/widerrufene Freigaben, falscher Digest, fehlende Capability, unbekannter Outcome, doppelte Events, stale CAS.
- [ ] Verifizieren, dass Hash-Chain-Kopien keine nachträgliche Mutierung durch Alias-Referenzen erlauben; Mutationstests ergänzen.
- [ ] Zielabschluss nur dann zulassen, wenn sämtliche erforderlichen Kriterien durch referenzierte Evidenz erfüllt sind.

**Gate W3:** Vollständige Vertrags- und Negativtest-Abdeckung für den klar begrenzten Prototyp; alle Abweichungen dokumentiert.

### W4 — Dauerhafte lokale Ausführung
**Status: OPEN; vor externer Ausführung.**

- [ ] Repository-/CI-Setup und unterstützte Python-Versionen definieren.
- [ ] Persistenz-Repository-Schnittstelle definieren; SQLite mit Transaktionen und Migrationen als erster Adapter.
- [ ] Restart-/Crash-Recovery-Tests für State, Idempotency Keys und Evidence Ledger.
- [ ] Durable Inbox/Outbox, Retries und Dead-letter mit dokumentierten Retry-Budgets.
- [ ] Unbekannte Ausführungsergebnisse speichern und vor Wiederholung abgleichen.
- [ ] Atomare Einmalverwendung von Genehmigungen und authentifizierte Freigabe-Identität implementieren.
- [ ] Backup, Restore, Migration-Rollback und Datenlösch-/Retention-Verhalten prüfen.

**Gate W4:** Crash-/Recovery- und Doppelzustellungsfälle sind reproduzierbar getestet; keine externen Aktionen ohne W3-Freigabe.

### W5 — Verteilte Koordination und Adapter
**Status: SPEZIFIKATION VORHANDEN; Implementierung OPEN.**

- [ ] Transport-Abstraktion festlegen; NATS JetStream nur als Kandidat evaluieren.
- [ ] State-/Transaction-Adapter evaluieren; PostgreSQL nur als Kandidat behandeln.
- [ ] Leases, Fencing Tokens, Inbox/Outbox, Reconciliation und Konfliktauflösung implementieren und testen.
- [ ] Strong consistency nur für autoritative Daten; Projektionen dürfen nicht autoritative Records überschreiben.
- [ ] Partition, verspätete Nachrichten, Duplikate, Out-of-order, Lease-Ablauf und Recovery testen.
- [ ] SCF-Projektionen und selektive Synchronisierung mit Herkunft und Konfliktbelegen umsetzen.
- [ ] Mehrprozess-/Mehrknoten-Tests erst nach lokaler Persistenz und Recovery.

**Gate W5:** Keine impliziten Exactly-once-Versprechen; Reconciliation und Fencing sind nachweislich wirksam.

### W6 — Policy, Datenschutz und Vertrauensgrenzen
**Status: SPEZIFIKATION VORHANDEN; vollständige Runtime-Durchsetzung OPEN.**

- [ ] Capability-Modell, Tenant-/Principal-Identität und Policy-Entscheidung mit einheitlichen IDs verbinden.
- [ ] Approval an Aktion, Parameter/Digest, Ablaufzeit, Kontext und Principal binden.
- [ ] Widerruf und Race zwischen Prüfung und Ausführung atomar absichern.
- [ ] Datenklassifikation, Retention, Redaktion und Löschung über Originale, Logs, Embeddings, Caches und Projektionen durchsetzen.
- [ ] Secrets nicht in Logs, Events, Receipts oder Evidence aufnehmen; Tests für Redaction ergänzen.
- [ ] Threat model, Abuse Cases, Audit-Ereignisse und Security-Testumfang definieren.
- [ ] Externe Side Effects bleiben standardmäßig deaktiviert, bis die zugehörigen Gates akzeptiert sind.

**Gate W6:** Sicherheits- und Datenschutzinvarianten sind implementiert und negativ getestet; keine Behauptung einer formalen Zertifizierung ohne unabhängigen Nachweis.

### W7 — Observability, HAL und begrenzte Anpassung
**Status: KONZEPT/SPEZIFIKATION; Implementierung OPEN.**

- [ ] Strukturierte Logs, Metriken und Trace-Korrelation mit Datenschutzregeln definieren.
- [ ] HAL Health-/Feedback-Signale und Schwellenwerte spezifizieren.
- [ ] Reparatur-/Evolutionsvorschläge von autonomen Änderungen trennen.
- [ ] Anpassungen mit Bounds, Rollback, Evidence und menschlicher Freigabe für riskante Aktionen versehen.
- [ ] Fehlerbudget, Stoppbedingungen und Reconciliation-Dashboards definieren.

**Gate W7:** Anpassung ist begrenzt, nachvollziehbar, reversibel und verändert keine Invarianten stillschweigend.

### W8 — Provider-, Compute- und Zukunftsadapter
**Status: ARCHITEKTURZIEL; keine reale Austauschbarkeit belegt.**

- [ ] Provider- und Compute-Capabilities über versionierte Adapterverträge modellieren.
- [ ] Konformitätstests für austauschbare LLM-/Embedding-/Storage-/Transport-Adapter.
- [ ] Modell-/Providerwechsel darf keine semantischen Verträge oder Evidenzhistorie brechen.
- [ ] Quantum-ready nur als austauschbare Compute-Schnittstelle beschreiben; hypothetische Backends simulieren und gegen denselben Vertrag testen.
- [ ] Keine Abhängigkeit von nicht verfügbaren Quantenfunktionen und keine Quantenvorteil-Claims ohne Messnachweis.

**Gate W8:** Mindestens zwei austauschbare Implementierungen pro priorisierter Adapterfamilie bestehen denselben Vertragstest, bevor Austauschbarkeit als praktisch verifiziert gilt.

### W9 — Produktionsreife und Release
**Status: BLOCKED bis W2–W8 angemessen abgeschlossen sind.**

- [ ] Integration-, Last-, Chaos-, Security-, Datenschutz- und Recovery-Tests.
- [ ] Deployment-/Rollback-/Backup-/Restore-Runbooks und Betriebshandbuch.
- [ ] SLOs, Limits, Kostenkontrolle, Alarmierung und Incident-Verfahren.
- [ ] Unabhängige Sicherheitsprüfung vor echten externen Side Effects.
- [ ] Release-Candidate reproduzierbar bauen, vollständige Provenienz/Hashes ausgeben.
- [ ] Explizite menschliche Freigabe der Produktionsstufe.

**Gate W9:** Produktionsfreigabe ist eine separate dokumentierte Entscheidung; weder Phase-0-Abnahme noch ein grüner Unit-Test-Lauf ersetzt sie.

## Abweichungsregister (beim nächsten Update zu schließen)

| ID | Befund | Maßnahme | Priorität |
|---|---|---|---|
| PRAIN-AUD-001 | v1.1.0-Statusbericht meldet 22 Tests; erneute Ausführung ergab 23 | Statusbericht/Testreport reproduzierbar aktualisieren | Hoch |
| PRAIN-AUD-002 | historische Prüfzahlen 310/319/325 uneinheitlich referenziert | Suite/Version/Scope pro Zahl ausweisen | Hoch |
| PRAIN-AUD-003 | historische Sperrstatus und späterer Freigabestatus koexistieren | historische Dokumente labeln und einen aktuellen Statusindex pflegen | Hoch |
| PRAIN-AUD-004 | vollständige Einzelanforderungs-RTM über alle historischen Quellen nicht nachgewiesen | Source-to-requirement-Matrix erstellen | Kritisch |
| PRAIN-AUD-005 | vollständige Runtime-Validierung der kanonischen Schemas nicht nachgewiesen | Schema-Adapter + Round-trip/negative tests | Kritisch |
| PRAIN-AUD-006 | produktive Persistenz, Recovery, signierte Freigaben und verteilte Verarbeitung fehlen | W4/W5 als separate Umsetzungsgates | Hoch |
| PRAIN-AUD-007 | Produktions-/Sicherheitszertifizierung ist nicht vorhanden | Grenzen explizit in Release-/README-Dokumenten führen | Hoch |

## Definition of Done für den Master-Audit

- Jede historische Anforderung ist klassifiziert und auf aktuellen Vertrag oder begründete Ablösung verlinkt.
- Jeder offene Punkt hat Verantwortlichkeit, Priorität, Abnahmekriterium und Beleg.
- Normative Definitionen sind eindeutig; keine verwaisten oder widersprüchlichen Querverweise.
- Release-Zahlen und Hashes sind reproduzierbar und scopespezifisch.
- README, Roadmap, Release-Status, Prototypstatus und Mastermanifest stimmen überein.
- Offene Implementierungspunkte bleiben offen markiert; kein Scheinerfolg durch bloße Dokumentation.

## Nächster konkreter Schritt

Zuerst **PRAIN-AUD-004** (vollständige RTM über alle historischen Quellen) und **PRAIN-AUD-005** (Runtime-Schema-Konformität) abschließen. Danach Release-Nachweise und Dokumentationsabweichungen bereinigen. Erst dann W4 dauerhaftes Runtime-Verhalten erweitern.


## Rückwirkendes Audit — Schritt 4

- [x] 19 Kernanforderungen aus v0.4/v0.5/v0.6 semantisch gegen v0.99.4-Spezifikation und v1.1.0-Laufzeit abgeglichen.
- [x] Kuratierter Crosswalk mit expliziten Implementierungs- und Testbelegen erstellt: `TRACEABILITY/HISTORICAL_CORE_CROSSWALK.csv`.
- [x] v1.1.0-Prototyp erneut getestet: 23/23 Tests bestanden; Dokumentationsabweichung (22 vs. 23) erfasst.
- [ ] Gesamte kanonische Invariantenliste mit Laufzeitstellen und Tests verbinden.
- [ ] Vollständige 5.071-Kandidatenmatrix semantisch klassifizieren und offene Zuordnungen schließen.

**Status:** PARTIAL_PASS. Der Crosswalk ist eine gezielte fachliche Stichprobe und kein Vollabschluss des historischen Audits.


## Schritt 5 — Invarianten-Runtime-Crosswalk (2026-10-20)

30 kanonische Invarianten aus v0.99.4 wurden einzeln gegen v1.1.0-Code/Test-Evidenz bewertet: `TRACEABILITY/CANONICAL_INVARIANT_RUNTIME_CROSSWALK.csv`. Der Crosswalk trennt Phase-0-Spezifikationsabdeckung von Runtime-Nachweisen. Kritische offene Lücken umfassen persistente Idempotenz, Lease-/Effect-Reconciliation, frische Revocation-Prüfung, Tenant-Isolation, Approval-Digest-Bindung sowie verteilte CAS-/Crash-Recovery-Tests. Keine Vollkonformität ableiten; Gesamtstatus bleibt `PARTIAL_PASS`, Produktionsreife `NOT ESTABLISHED`.


## Schritt 6 — Runtime-Patch und Regressionstests (2026-10-20)

- [x] Neue Referenzversion `archive/PRAIN_Phase1_Prototype_v1.1.1/` erzeugt; v1.1.0 bleibt historisch erhalten.
- [x] Approval-Lifecycle-Prüfungen für `decision`, `lifecycle_status`, `valid_from`, `max_uses` und `usage_count` ergänzt, sofern die Felder geliefert werden.
- [x] Payload-Aliasing durch Deep-Copy-Snapshots für Observation und ActionRequest sowie Runtime-Fingerprint/Resultat reduziert.
- [x] Regressionstests ergänzt; 27/27 Unit-Tests bestanden und Demo erfolgreich.
- [ ] Atomare/persistente Approval-Verwendung, frische Revocation-Prüfung, vollständige kanonische Digest-Bindung und Crash-Recovery bleiben offen.

**Status:** `PARTIAL_PASS`. Änderungen schließen konkrete lokale Fehlerklassen, ersetzen aber weder zentrale Freigabeautorität noch persistente/distribuierte Runtime.


## Step 7 — Process-local action admission and single-use approval guard (2026-10-20)

- Added reference prototype `archive/PRAIN_Phase1_Prototype_v1.1.2/` and packaged ZIP.
- `request_action` admission is serialized with a process-local lock; same-key concurrent submissions replay one receipt.
- `usage_policy=single_use` approvals require a stable `approval_id`; consumed IDs are rejected for a second distinct idempotency key within this runtime instance.
- Verification: 30/30 unit tests pass; demo reports v1.1.2, `simulated_only`, valid evidence chain.
- Limitations remain explicit: no cross-process/distributed lock, durable consumption, trusted signed approval authority, or exactly-once external effects. Status remains `PARTIAL_PASS`.
- Next gate: transactional durable store with unique constraints and crash-recovery tests, then outbox/reconciliation design before real side effects.

## Schritt 8 — SQLite-Dauerhaftigkeit (2026-10-20)

**Ergebnis:** Ein SQLite-basiertes Persistenzprimitive wurde als Prototyp v1.1.3 ergänzt und lokal validiert. Die 5 neuen Tests decken Store-Neuinstanziierung/Replay, Idempotenz-Fingerprint-Konflikt, persistente Single-use-Freigabe, parallele Writer und Rollback-Kopplung ab. Vollständiger Prototyp-Testlauf: 35/35 bestanden.

**Wichtige Abgrenzung:** `DurableAdmissionStore` ist derzeit ein separates Modul und noch nicht in `PRAINRuntime.request_action` integriert. Die aktive Runtime bleibt weiterhin in-memory. Keine externe Aktion wird ausgeführt. Deshalb bleibt Gesamtstatus `PARTIAL_PASS`; weder Produktionsreife noch Exactly-once-Ausführung sind belegt.

**Nächster Schritt 9:** Repository-Schnittstelle in die Runtime integrieren, Entscheidung/Freigabeverbrauch/Receipt-Outbox transaktional koppeln und Crash-/Recovery- sowie Multi-Instanz-Tests hinzufügen. Erst danach Outbox-Dispatcher mit expliziter Ungewissheits-/Reconciliation-Strategie entwickeln.

## Schritt 9 — SQLite-Admission in die Runtime integriert (2026-10-20)

- [x] Referenzprototyp `archive/PRAIN_Phase1_Prototype_v1.1.4/` angelegt; v1.1.0–v1.1.3 bleiben als historische Versionen erhalten.
- [x] `PRAINRuntime` unterstützt optional `DurableAdmissionStore` für persistentes Idempotenz-Replay und Receipt-Speicherung.
- [x] Gleicher Schlüssel mit verändertem Fingerprint wird auch nach Neuinstanziierung fail-closed abgelehnt.
- [x] Single-use-Approval-Verbrauch wird in derselben SQLite-Transaktion wie der Receipt gespeichert; unterschiedliche Runtime-Instanzen teilen sich die Unique-Constraint-Garantie über dieselbe DB.
- [x] 38/38 Tests bestanden; Demo weiterhin `simulated_only`.
- [ ] Outbox/Dispatcher, Crash-Recovery an externen Effect-Grenzen, persistente Evidence/State, signierte Approval-Identität und authoritative Revocation bleiben offen.

**Status:** `PARTIAL_PASS`. Die Runtime-Admission ist optional persistent, nicht die gesamte Laufzeit. Produktionsreife und Exactly-once-externe Ausführung sind nicht nachgewiesen. Details: `docs/STEP9_RUNTIME_SQLITE_INTEGRATION.md`.


## Step 10 — Durable Outbox and conservative crash recovery (2026-10-20)

- [x] Prototype v1.1.5 adds SQLite outbox insertion atomically with durable admission/receipt.
- [x] Added transactional pending-item claim and explicit outcome transitions.
- [x] Restart recovery converts abandoned `IN_FLIGHT` records to `OUTCOME_UNKNOWN`, never blind-retries them.
- [x] Runtime stores action payload in outbox when durable admission is configured.
- [x] Unit suite: 41/41 passed; prototype ZIP and master ZIP integrity checked.
- [ ] Implement a real dispatcher only after provider-specific idempotency and reconciliation contracts are defined.
- [ ] Add kill-process fault injection around DB commit and simulated provider boundaries; add multi-process race tests and migrations.
- [ ] Persist StateStore, GoalRegistry, EventBus and EvidenceLedger; implement authoritative approval/revocation and signed identity.

**Status:** `PARTIAL_PASS`. No external service is invoked. `OUTCOME_UNKNOWN` is conservative bookkeeping, not proof of external state. Exactly-once external effects and production readiness are not established. Details: `docs/STEP10_DURABLE_OUTBOX_AND_RECOVERY.md`.


 PRAIN — Durchgängiger Master-Wayplan / Roadmap

**Stand:** 2026-10-20  
**Ziel:** Einen nachvollziehbaren Pfad vom historischen Bestand über konsolidierte Spezifikation bis zu einem robusten, modularen Agenten-Orchestrator schaffen. Dieser Plan ist die führende Arbeitsliste; Änderungen müssen versioniert werden.

## Leitprinzipien

1. Semantik und Verträge vor Infrastruktur.
2. Ein kanonischer Vertrag pro Konzept; historische Quellen bleiben nachvollziehbar.
3. Jede Anforderung ist rückverfolgbar: Quelle → Entscheidung → Vertrag/Schema → Implementierung → Test/Evidenz.
4. Sicherheitsgrenzen fail-closed, Freigaben aktionsgebunden und widerrufbar.
5. Unbekannte Zustände werden sichtbar gemacht und abgeglichen, nicht geraten.
6. Provider, Speicher, Transport und Compute sind austauschbare Adapter; keine vorzeitige Bindung an einen Anbieter.
7. „Quantum-ready“ bleibt eine austauschbare Schnittstellenstrategie, keine unbelegte Leistungsbehauptung.
8. Keine Produktionsfreigabe allein aufgrund von Unit-Tests oder Spezifikationsprüfungen.

## Rückwirkendes Audit — Fortschritt

**Schritt 1 abgeschlossen (automatisierte Bestandsaufnahme, 2026-10-20):** `TRACEABILITY/SOURCE_REGISTER.csv` und `TRACEABILITY/REQUIREMENT_TRACEABILITY_MATRIX.csv` wurden erzeugt. Die Matrix enthält Kandidatenzeilen, nicht automatisch akzeptierte Anforderungen; nach historischem ZIP-Scan umfasst sie inzwischen 5071 Zeilen. Alle Zeilen bleiben offen, bis semantisch geprüft und auf normative Quelle/Schema/Code/Test abgebildet.

**Schritt 2 als nächstes:** historische Quellen v0.1.0 bis v0.6 und ursprüngliche Wissensdatenbank zeilenweise auswerten, Kandidaten-RTM ergänzen und jede Anforderung klassifizieren. Danach v0.7–v0.99.4 auf Änderungen und Widersprüche abgleichen.

## Statusdefinitionen

- **DONE-SPEC:** spezifiziert und im angegebenen Prüfumfang validiert; keine Implementierungsaussage.
- **PROTOTYPE:** in Referenzcode vorhanden, mit benannten Grenzen.
- **OPEN:** fehlender Beleg, ungelöste Abweichung oder noch nicht umgesetzte Arbeit.
- **BLOCKED:** kann erst nach einer benannten Entscheidung oder Voraussetzung beginnen.
- **ACCEPTED:** nur nach dokumentierter Abnahme durch Projektverantwortliche.

## Arbeitsstränge und Gates

### W0 — Bestand sichern und Quellen inventarisieren
**Status: teilweise belegt; Inventar konsolidiert, vollständige Einzelanforderungs-Rückverfolgung offen.**

- [x] Historische ZIPs und Wissensdatenbank-Artefakte im Bestand inventarisieren.
- [x] Frühere Versionen als Historie erhalten; keine stille Überschreibung.
- [ ] Für jede Datei SHA-256, Version, Zweck, Herkunft und kanonischen Nachfolger in maschinenlesbares Manifest aufnehmen.
- [ ] Prüfen, dass jedes historische Paket im Master-Archiv enthalten ist und lesbar entpackt werden kann.
- [ ] Alle frühen Anforderungen aus v0.1.0 bis v0.6 und Wissensdatenbank gegen aktuelle Spezifikation mappen.

**Gate W0:** Kein nicht klassifizierter historischer Punkt. Jede Anforderung ist retained / extended / superseded / open / deferred und besitzt eine Begründung.

### W1 — Kanonische Spezifikation und Traceability
**Status: DONE-SPEC im dokumentierten Umfang; finale vollständige Rückverfolgung noch offen.**

- [x] Architektur und P/R/A/I/N-Verantwortlichkeiten dokumentiert.
- [x] SCF, HAL sowie Invariant & Evidence Layer dokumentiert.
- [x] Schema-, Wissensbasis-, Claim-, Semantik- und Zustandsautomaten-Audits vorhanden.
- [x] Schema-/Zustandsautomaten-Crosswalk und normative State Machines vorhanden.
- [ ] Eine zentrale Requirement Traceability Matrix (RTM) erzeugen: Requirement-ID, Ursprung, Normtext, Status, Zieldokument, Schema/Code, Test, Befund, offene Aktion.
- [ ] Alle Links/IDs automatisiert auf Existenz und Eindeutigkeit prüfen.
- [ ] Terminologie-Dubletten und widersprüchliche Normtexte mit einer kanonischen Quelle bereinigen.
- [ ] Alte Statusangaben als HISTORICAL markieren; nur ein aktueller Freigabestatus pro Release.

**Gate W1:** Jede normative Aussage hat eine eindeutige Quelle, Version und nachvollziehbare Verifikation oder klaren offenen Status.

### W2 — Release- und Nachweisqualität
**Status: OPEN — Dokumentationsabweichungen festgestellt.**

- [ ] v1.1.0-Statusbericht von 22 Tests auf den nach erneuter Ausführung bestätigten Umfang aktualisieren, falls der Teststand unverändert ist.
- [ ] Zahlen 310/319/325 je Suite, Validator-Version, Datum und Scope erklären; nie als austauschbare Gesamtzahl behandeln.
- [ ] Alle Release-Integritätsdateien gegen tatsächliche Dateien neu berechnen und maschinell vergleichen.
- [ ] Einen einheitlichen `MANIFEST.json` und `SHA256SUMS` für das gesamte Master-Paket generieren.
- [ ] Release-Inhalt reproduzierbar aus einem sauberen Verzeichnis erzeugen; Paketinhalt und Hashes in CI prüfen.
- [ ] Abschlussbericht trennt Spezifikationsprüfungen, Unit-Tests, Integrationstests, Sicherheitsprüfungen und Produktionsvalidierung.

**Gate W2:** Reproduzierbares Paket; keine widersprüchlichen Zahlen ohne Erklärung; alle Hashes verifiziert.

### W3 — Phase-1-Prototyp: Vertragsdurchsetzung
**Status: PROTOTYPE; umfassende Schema-Runtime-Konformität OPEN.**

- [x] Lokaler vertikaler Pfad Observation → Event/Evidence → Evaluator → Policy → simulierte Aktion → Receipt → Evidenzkette.
- [x] In-memory CAS-State-Store, Zielregistrierung, Policy Gateway und Evidenz-Ledger im Referenzcode.
- [x] Lokale Unit-Tests und Demo dokumentiert; 23 Tests in der erneuten Ausführung bestanden.
- [ ] Kanonische Phase-0-Schemas beim Einlesen/Serialisieren tatsächlich validieren (nicht nur parallel dokumentieren).
- [ ] Schema-Round-trip-Tests und unbekannte/fehlende Felder, falsche Versionen, ungültige Enums und Grenzwerte testen.
- [ ] Zustandsautomaten-Properties und unerlaubte Transitionen gegen die normativen Automaten testen.
- [ ] Negative Tests: abgelaufene/verbrauchte/widerrufene Freigaben, falscher Digest, fehlende Capability, unbekannter Outcome, doppelte Events, stale CAS.
- [ ] Verifizieren, dass Hash-Chain-Kopien keine nachträgliche Mutierung durch Alias-Referenzen erlauben; Mutationstests ergänzen.
- [ ] Zielabschluss nur dann zulassen, wenn sämtliche erforderlichen Kriterien durch referenzierte Evidenz erfüllt sind.

**Gate W3:** Vollständige Vertrags- und Negativtest-Abdeckung für den klar begrenzten Prototyp; alle Abweichungen dokumentiert.

### W4 — Dauerhafte lokale Ausführung
**Status: OPEN; vor externer Ausführung.**

- [ ] Repository-/CI-Setup und unterstützte Python-Versionen definieren.
- [ ] Persistenz-Repository-Schnittstelle definieren; SQLite mit Transaktionen und Migrationen als erster Adapter.
- [ ] Restart-/Crash-Recovery-Tests für State, Idempotency Keys und Evidence Ledger.
- [ ] Durable Inbox/Outbox, Retries und Dead-letter mit dokumentierten Retry-Budgets.
- [ ] Unbekannte Ausführungsergebnisse speichern und vor Wiederholung abgleichen.
- [ ] Atomare Einmalverwendung von Genehmigungen und authentifizierte Freigabe-Identität implementieren.
- [ ] Backup, Restore, Migration-Rollback und Datenlösch-/Retention-Verhalten prüfen.

**Gate W4:** Crash-/Recovery- und Doppelzustellungsfälle sind reproduzierbar getestet; keine externen Aktionen ohne W3-Freigabe.

### W5 — Verteilte Koordination und Adapter
**Status: SPEZIFIKATION VORHANDEN; Implementierung OPEN.**

- [ ] Transport-Abstraktion festlegen; NATS JetStream nur als Kandidat evaluieren.
- [ ] State-/Transaction-Adapter evaluieren; PostgreSQL nur als Kandidat behandeln.
- [ ] Leases, Fencing Tokens, Inbox/Outbox, Reconciliation und Konfliktauflösung implementieren und testen.
- [ ] Strong consistency nur für autoritative Daten; Projektionen dürfen nicht autoritative Records überschreiben.
- [ ] Partition, verspätete Nachrichten, Duplikate, Out-of-order, Lease-Ablauf und Recovery testen.
- [ ] SCF-Projektionen und selektive Synchronisierung mit Herkunft und Konfliktbelegen umsetzen.
- [ ] Mehrprozess-/Mehrknoten-Tests erst nach lokaler Persistenz und Recovery.

**Gate W5:** Keine impliziten Exactly-once-Versprechen; Reconciliation und Fencing sind nachweislich wirksam.

### W6 — Policy, Datenschutz und Vertrauensgrenzen
**Status: SPEZIFIKATION VORHANDEN; vollständige Runtime-Durchsetzung OPEN.**

- [ ] Capability-Modell, Tenant-/Principal-Identität und Policy-Entscheidung mit einheitlichen IDs verbinden.
- [ ] Approval an Aktion, Parameter/Digest, Ablaufzeit, Kontext und Principal binden.
- [ ] Widerruf und Race zwischen Prüfung und Ausführung atomar absichern.
- [ ] Datenklassifikation, Retention, Redaktion und Löschung über Originale, Logs, Embeddings, Caches und Projektionen durchsetzen.
- [ ] Secrets nicht in Logs, Events, Receipts oder Evidence aufnehmen; Tests für Redaction ergänzen.
- [ ] Threat model, Abuse Cases, Audit-Ereignisse und Security-Testumfang definieren.
- [ ] Externe Side Effects bleiben standardmäßig deaktiviert, bis die zugehörigen Gates akzeptiert sind.

**Gate W6:** Sicherheits- und Datenschutzinvarianten sind implementiert und negativ getestet; keine Behauptung einer formalen Zertifizierung ohne unabhängigen Nachweis.

### W7 — Observability, HAL und begrenzte Anpassung
**Status: KONZEPT/SPEZIFIKATION; Implementierung OPEN.**

- [ ] Strukturierte Logs, Metriken und Trace-Korrelation mit Datenschutzregeln definieren.
- [ ] HAL Health-/Feedback-Signale und Schwellenwerte spezifizieren.
- [ ] Reparatur-/Evolutionsvorschläge von autonomen Änderungen trennen.
- [ ] Anpassungen mit Bounds, Rollback, Evidence und menschlicher Freigabe für riskante Aktionen versehen.
- [ ] Fehlerbudget, Stoppbedingungen und Reconciliation-Dashboards definieren.

**Gate W7:** Anpassung ist begrenzt, nachvollziehbar, reversibel und verändert keine Invarianten stillschweigend.

### W8 — Provider-, Compute- und Zukunftsadapter
**Status: ARCHITEKTURZIEL; keine reale Austauschbarkeit belegt.**

- [ ] Provider- und Compute-Capabilities über versionierte Adapterverträge modellieren.
- [ ] Konformitätstests für austauschbare LLM-/Embedding-/Storage-/Transport-Adapter.
- [ ] Modell-/Providerwechsel darf keine semantischen Verträge oder Evidenzhistorie brechen.
- [ ] Quantum-ready nur als austauschbare Compute-Schnittstelle beschreiben; hypothetische Backends simulieren und gegen denselben Vertrag testen.
- [ ] Keine Abhängigkeit von nicht verfügbaren Quantenfunktionen und keine Quantenvorteil-Claims ohne Messnachweis.

**Gate W8:** Mindestens zwei austauschbare Implementierungen pro priorisierter Adapterfamilie bestehen denselben Vertragstest, bevor Austauschbarkeit als praktisch verifiziert gilt.

### W9 — Produktionsreife und Release
**Status: BLOCKED bis W2–W8 angemessen abgeschlossen sind.**

- [ ] Integration-, Last-, Chaos-, Security-, Datenschutz- und Recovery-Tests.
- [ ] Deployment-/Rollback-/Backup-/Restore-Runbooks und Betriebshandbuch.
- [ ] SLOs, Limits, Kostenkontrolle, Alarmierung und Incident-Verfahren.
- [ ] Unabhängige Sicherheitsprüfung vor echten externen Side Effects.
- [ ] Release-Candidate reproduzierbar bauen, vollständige Provenienz/Hashes ausgeben.
- [ ] Explizite menschliche Freigabe der Produktionsstufe.

**Gate W9:** Produktionsfreigabe ist eine separate dokumentierte Entscheidung; weder Phase-0-Abnahme noch ein grüner Unit-Test-Lauf ersetzt sie.

## Abweichungsregister (beim nächsten Update zu schließen)

| ID | Befund | Maßnahme | Priorität |
|---|---|---|---|
| PRAIN-AUD-001 | v1.1.0-Statusbericht meldet 22 Tests; erneute Ausführung ergab 23 | Statusbericht/Testreport reproduzierbar aktualisieren | Hoch |
| PRAIN-AUD-002 | historische Prüfzahlen 310/319/325 uneinheitlich referenziert | Suite/Version/Scope pro Zahl ausweisen | Hoch |
| PRAIN-AUD-003 | historische Sperrstatus und späterer Freigabestatus koexistieren | historische Dokumente labeln und einen aktuellen Statusindex pflegen | Hoch |
| PRAIN-AUD-004 | vollständige Einzelanforderungs-RTM über alle historischen Quellen nicht nachgewiesen | Source-to-requirement-Matrix erstellen | Kritisch |
| PRAIN-AUD-005 | vollständige Runtime-Validierung der kanonischen Schemas nicht nachgewiesen | Schema-Adapter + Round-trip/negative tests | Kritisch |
| PRAIN-AUD-006 | produktive Persistenz, Recovery, signierte Freigaben und verteilte Verarbeitung fehlen | W4/W5 als separate Umsetzungsgates | Hoch |
| PRAIN-AUD-007 | Produktions-/Sicherheitszertifizierung ist nicht vorhanden | Grenzen explizit in Release-/README-Dokumenten führen | Hoch |

## Definition of Done für den Master-Audit

- Jede historische Anforderung ist klassifiziert und auf aktuellen Vertrag oder begründete Ablösung verlinkt.
- Jeder offene Punkt hat Verantwortlichkeit, Priorität, Abnahmekriterium und Beleg.
- Normative Definitionen sind eindeutig; keine verwaisten oder widersprüchlichen Querverweise.
- Release-Zahlen und Hashes sind reproduzierbar und scopespezifisch.
- README, Roadmap, Release-Status, Prototypstatus und Mastermanifest stimmen überein.
- Offene Implementierungspunkte bleiben offen markiert; kein Scheinerfolg durch bloße Dokumentation.

## Nächster konkreter Schritt

Zuerst **PRAIN-AUD-004** (vollständige RTM über alle historischen Quellen) und **PRAIN-AUD-005** (Runtime-Schema-Konformität) abschließen. Danach Release-Nachweise und Dokumentationsabweichungen bereinigen. Erst dann W4 dauerhaftes Runtime-Verhalten erweitern.


## Rückwirkendes Audit — Schritt 4

- [x] 19 Kernanforderungen aus v0.4/v0.5/v0.6 semantisch gegen v0.99.4-Spezifikation und v1.1.0-Laufzeit abgeglichen.
- [x] Kuratierter Crosswalk mit expliziten Implementierungs- und Testbelegen erstellt: `TRACEABILITY/HISTORICAL_CORE_CROSSWALK.csv`.
- [x] v1.1.0-Prototyp erneut getestet: 23/23 Tests bestanden; Dokumentationsabweichung (22 vs. 23) erfasst.
- [ ] Gesamte kanonische Invariantenliste mit Laufzeitstellen und Tests verbinden.
- [ ] Vollständige 5.071-Kandidatenmatrix semantisch klassifizieren und offene Zuordnungen schließen.

**Status:** PARTIAL_PASS. Der Crosswalk ist eine gezielte fachliche Stichprobe und kein Vollabschluss des historischen Audits.


## Schritt 5 — Invarianten-Runtime-Crosswalk (2026-10-20)

30 kanonische Invarianten aus v0.99.4 wurden einzeln gegen v1.1.0-Code/Test-Evidenz bewertet: `TRACEABILITY/CANONICAL_INVARIANT_RUNTIME_CROSSWALK.csv`. Der Crosswalk trennt Phase-0-Spezifikationsabdeckung von Runtime-Nachweisen. Kritische offene Lücken umfassen persistente Idempotenz, Lease-/Effect-Reconciliation, frische Revocation-Prüfung, Tenant-Isolation, Approval-Digest-Bindung sowie verteilte CAS-/Crash-Recovery-Tests. Keine Vollkonformität ableiten; Gesamtstatus bleibt `PARTIAL_PASS`, Produktionsreife `NOT ESTABLISHED`.


## Schritt 6 — Runtime-Patch und Regressionstests (2026-10-20)

- [x] Neue Referenzversion `archive/PRAIN_Phase1_Prototype_v1.1.1/` erzeugt; v1.1.0 bleibt historisch erhalten.
- [x] Approval-Lifecycle-Prüfungen für `decision`, `lifecycle_status`, `valid_from`, `max_uses` und `usage_count` ergänzt, sofern die Felder geliefert werden.
- [x] Payload-Aliasing durch Deep-Copy-Snapshots für Observation und ActionRequest sowie Runtime-Fingerprint/Resultat reduziert.
- [x] Regressionstests ergänzt; 27/27 Unit-Tests bestanden und Demo erfolgreich.
- [ ] Atomare/persistente Approval-Verwendung, frische Revocation-Prüfung, vollständige kanonische Digest-Bindung und Crash-Recovery bleiben offen.

**Status:** `PARTIAL_PASS`. Änderungen schließen konkrete lokale Fehlerklassen, ersetzen aber weder zentrale Freigabeautorität noch persistente/distribuierte Runtime.


## Step 7 — Process-local action admission and single-use approval guard (2026-10-20)

- Added reference prototype `archive/PRAIN_Phase1_Prototype_v1.1.2/` and packaged ZIP.
- `request_action` admission is serialized with a process-local lock; same-key concurrent submissions replay one receipt.
- `usage_policy=single_use` approvals require a stable `approval_id`; consumed IDs are rejected for a second distinct idempotency key within this runtime instance.
- Verification: 30/30 unit tests pass; demo reports v1.1.2, `simulated_only`, valid evidence chain.
- Limitations remain explicit: no cross-process/distributed lock, durable consumption, trusted signed approval authority, or exactly-once external effects. Status remains `PARTIAL_PASS`.
- Next gate: transactional durable store with unique constraints and crash-recovery tests, then outbox/reconciliation design before real side effects.

## Schritt 8 — SQLite-Dauerhaftigkeit (2026-10-20)

**Ergebnis:** Ein SQLite-basiertes Persistenzprimitive wurde als Prototyp v1.1.3 ergänzt und lokal validiert. Die 5 neuen Tests decken Store-Neuinstanziierung/Replay, Idempotenz-Fingerprint-Konflikt, persistente Single-use-Freigabe, parallele Writer und Rollback-Kopplung ab. Vollständiger Prototyp-Testlauf: 35/35 bestanden.

**Wichtige Abgrenzung:** `DurableAdmissionStore` ist derzeit ein separates Modul und noch nicht in `PRAINRuntime.request_action` integriert. Die aktive Runtime bleibt weiterhin in-memory. Keine externe Aktion wird ausgeführt. Deshalb bleibt Gesamtstatus `PARTIAL_PASS`; weder Produktionsreife noch Exactly-once-Ausführung sind belegt.

**Nächster Schritt 9:** Repository-Schnittstelle in die Runtime integrieren, Entscheidung/Freigabeverbrauch/Receipt-Outbox transaktional koppeln und Crash-/Recovery- sowie Multi-Instanz-Tests hinzufügen. Erst danach Outbox-Dispatcher mit expliziter Ungewissheits-/Reconciliation-Strategie entwickeln.

## Schritt 9 — SQLite-Admission in die Runtime integriert (2026-10-20)

- [x] Referenzprototyp `archive/PRAIN_Phase1_Prototype_v1.1.4/` angelegt; v1.1.0–v1.1.3 bleiben als historische Versionen erhalten.
- [x] `PRAINRuntime` unterstützt optional `DurableAdmissionStore` für persistentes Idempotenz-Replay und Receipt-Speicherung.
- [x] Gleicher Schlüssel mit verändertem Fingerprint wird auch nach Neuinstanziierung fail-closed abgelehnt.
- [x] Single-use-Approval-Verbrauch wird in derselben SQLite-Transaktion wie der Receipt gespeichert; unterschiedliche Runtime-Instanzen teilen sich die Unique-Constraint-Garantie über dieselbe DB.
- [x] 38/38 Tests bestanden; Demo weiterhin `simulated_only`.
- [ ] Outbox/Dispatcher, Crash-Recovery an externen Effect-Grenzen, persistente Evidence/State, signierte Approval-Identität und authoritative Revocation bleiben offen.

**Status:** `PARTIAL_PASS`. Die Runtime-Admission ist optional persistent, nicht die gesamte Laufzeit. Produktionsreife und Exactly-once-externe Ausführung sind nicht nachgewiesen. Details: `docs/STEP9_RUNTIME_SQLITE_INTEGRATION.md`.


## Step 10 — Durable Outbox and conservative crash recovery (2026-10-20)

- [x] Prototype v1.1.5 adds SQLite outbox insertion atomically with durable admission/receipt.
- [x] Added transactional pending-item claim and explicit outcome transitions.
- [x] Restart recovery converts abandoned `IN_FLIGHT` records to `OUTCOME_UNKNOWN`, never blind-retries them.
- [x] Runtime stores action payload in outbox when durable admission is configured.
- [x] Unit suite: 41/41 passed; prototype ZIP and master ZIP integrity checked.
- [ ] Implement a real dispatcher only after provider-specific idempotency and reconciliation contracts are defined.
- [ ] Add kill-process fault injection around DB commit and simulated provider boundaries; add multi-process race tests and migrations.
- [ ] Persist StateStore, GoalRegistry, EventBus and EvidenceLedger; implement authoritative approval/revocation and signed identity.

**Status:** `PARTIAL_PASS`. No external service is invoked. `OUTCOME_UNKNOWN` is conservative bookkeeping, not proof of external state. Exactly-once external effects and production readiness are not established. Details: `docs/STEP10_DURABLE_OUTBOX_AND_RECOVERY.md`.


## Step 10 — Durable Outbox and conservative crash recovery (2026-10-20)

- [x] Prototype v1.1.5 adds SQLite outbox insertion atomically with durable admission/receipt.
- [x] Added transactional pending-item claim and explicit outcome transitions.
- [x] Restart recovery converts abandoned `IN_FLIGHT` records to `OUTCOME_UNKNOWN`, never blind-retries them.
- [x] Runtime stores action payload in outbox when durable admission is configured.
- [x] Unit suite: 41/41 passed; prototype ZIP and master ZIP integrity checked.
- [ ] Implement a real dispatcher only after provider-specific idempotency and reconciliation contracts are defined.
- [ ] Add kill-process fault injection around DB commit and simulated provider boundaries; add multi-process race tests and migrations.
- [ ] Persist StateStore, GoalRegistry, EventBus and EvidenceLedger; implement authoritative approval/revocation and signed identity.

**Status:** `PARTIAL_PASS`. No external service is invoked. `OUTCOME_UNKNOWN` is conservative bookkeeping, not proof of external state. Exactly-once external effects and production readiness are not established. Details: `docs/STEP10_DURABLE_OUTBOX_AND_RECOVERY.md`.


## Step 11 — Conservative dispatcher and reconciliation (2026-10-20)

- [x] Prototype v1.1.6 adds an explicitly injected outbox handler; no handler means no claim/execution.
- [x] Handler exceptions and invalid outcomes become `OUTCOME_UNKNOWN`; automatic retry is blocked.
- [x] Added evidence-gated reconciliation for `SUCCEEDED`, `FAILED`, and `NOT_EXECUTED`; only the latter requeues to `PENDING`.
- [x] Unit suite: 47/47 passed.
- [ ] Validate provider evidence authority/signatures and provider-side idempotency keys before enabling any real adapter.
- [ ] Add process-kill fault injection and multi-process race tests; persist remaining runtime stores and implement authoritative approval/revocation.

**Status:** `PARTIAL_PASS`. Dispatcher has no default handler and no external provider integration; reconciliation evidence is caller-supplied and not cryptographically verified. Exactly-once effects and production readiness are not established. Details: `archive/PRAIN_v1.1.6_Phase1_Reference_Prototype/docs/STEP11_DISPATCHER_RECONCILIATION.md`.

## Step 12 — Fault injection and multi-process contention tests (2026-10-20)

- [x] Prototype v1.1.7 adds restart/crash-window tests: abandoned `IN_FLIGHT` transitions to `OUTCOME_UNKNOWN`, with no blind retry.
- [x] Four independent processes contend for one outbox item; exactly one claim succeeds in the test.
- [x] Concurrent reconciliation is tested as a status-guarded compare-and-set; only one terminal result wins.
- [x] Evidence-gating test confirms empty reconciliation evidence cannot authorize requeue.
- [x] Unit suite: 51/51 passed; ZIP integrity and SHA-256 manifests regenerated.
- [ ] Perform true process-kill tests around a real provider boundary; validate signed/authoritative provider evidence and provider idempotency contracts.
- [ ] Persist remaining runtime stores and implement authoritative approval/revocation.

**Status:** `PARTIAL_PASS`. Tests establish local SQLite/process coordination behavior only. They do not prove exactly-once external effects or production readiness. Details: `docs/STEP12_FAULT_INJECTION_AND_MULTIPROCESS_TESTS.md` and `archive/PRAIN_v1.1.7_Phase1_Reference_Prototype/docs/STEP12_FAULT_INJECTION_AND_MULTIPROCESS_TESTS.md`.


## Step 13 — Durable versioned state store (2026-10-20)

- [x] Prototype v1.1.8 adds optional SQLite `DurableStateStore`; default in-memory store remains unchanged.
- [x] State values survive adapter reopen and retain monotonically increasing versions.
- [x] Duplicate create and stale compare-and-swap writes are rejected.
- [x] Four-process CAS race confirms one winner and three conflicts.
- [x] Full unit suite: 55/55 passed; archive manifest and SHA-256 inventory regenerated.
- [ ] Persist GoalRegistry lifecycle/verification records, EventBus inbox/deduplication and EvidenceLedger chain.
- [ ] Add migrations, backup/restore, corruption-recovery and runtime-wiring tests; clean up existing SQLite ResourceWarnings.

**Status:** `PARTIAL_PASS`. This is an opt-in local SQLite adapter, not a distributed database, and it is not automatically wired into `PRAINRuntime`. Other runtime stores remain in-memory. No production readiness or exactly-once external effects are claimed. Details: `docs/STEP13_DURABLE_STATE_STORE.md` and `archive/PRAIN_v1.1.8_Phase1_Reference_Prototype/docs/STEP13_DURABLE_STATE_STORE.md`.


## Step 14 — Durable Runtime Components (2026-10-20)

**Status: implemented; overall gate remains PARTIAL_PASS.** Prototype v1.1.9 adds SQLite-backed GoalRegistry, EventBus event log/consumer reservations and EvidenceLedger. Runtime opt-in: `persistent_db_path`. Regression suite: 59 passed.

**Known boundaries:** Runtime StateStore remains in-memory unless separately replaced with `DurableStateStore`. Event reservations are persisted before callbacks, preventing duplicates but allowing loss after crash; this is not a durable broker. Disk-full/corruption/backup-restore and migration fault injection remain open.

**Next:** (1) wire durable state store behind a compatible runtime interface; (2) replace event reservation-only model with recoverable delivery state and reconciliation; (3) close SQLite connection/resource warnings; (4) test database corruption, disk-full, backup/restore and schema migrations; (5) run full multi-process stress and crash-window tests.


## Phase 0 gate status — 2026-10-20

- **Phase 0 specification gate: GREEN / CLOSED** — v0.99.5 closure record, explicit user approval, baseline SHA-256 and six re-run validator scopes documented.
- **Phase 1 runtime gate: OPEN** — runtime persistence integration, safe event delivery/reconciliation, resource lifecycle, fault injection and provider-boundary evidence remain separate work.
- **Overall master audit: PARTIAL_PASS** — full historical requirement-by-requirement traceability remains open; no production-readiness claim.


## Phase 0 — final revalidation v0.99.6

- [x] Re-ran the main, semantic, state-machine, schema/state-machine, and deep conformance validators.
- [x] Corrected lifecycle and attestation contradictions; Phase-0 closure and Phase-1 authorization are separate gates.
- [x] Rebuilt exact file manifest and SHA-256 inventory.
- [x] Verified release bundle 324/324 and final archive/integrity 330/330.
- [x] Phase 0 marked `GREEN_PHASE0_SPECIFICATION_CLOSED` only after all checks passed.
- [ ] Phase-1 runtime and production-readiness gates remain separate and are not covered by Phase-0 GREEN.
