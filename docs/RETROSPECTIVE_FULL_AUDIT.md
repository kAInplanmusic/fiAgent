# PRAIN — Rückwirkendes Gesamt-Audit

**Prüfdatum:** 2026-10-20  
**Prüfbasis:** tatsächlich vorliegendes Master-Archiv, enthaltene historische Release-ZIPs, v0.99.4-Spezifikationspaket und v1.1.0-Referenzprototyp.  
**Status:** `PARTIAL_PASS — vollständige historische Einzelanforderungs-Rückverfolgung bleibt offen`.

## 1. Was in dieser Runde tatsächlich ausgeführt wurde

| Prüfung | Ergebnis | Aussagegrenze |
|---|---:|---|
| Master-ZIP | ZIP-CRC-Test erfolgreich | Prüft Lesbarkeit, nicht inhaltliche Vollständigkeit |
| Enthaltene verschachtelte ZIPs | 29 geprüft, 0 beschädigt | Nur die im Master enthaltenen ZIPs |
| JSON-Dateien im Master | 58 geparst, 0 Syntaxfehler | JSON-Syntax ist keine vollständige Schema-Konformität |
| Master SHA256SUMS | 169 Einträge, 0 fehlend/abweichend | Prüft die aufgeführten Dateien; nicht automatisch die fachliche Richtigkeit |
| Phase-0-Hauptvalidator | 127/127 PASS | Spezifikationsprüfung |
| Deep-Conformance-Validator | 237/237 PASS | Bericht kennzeichnet Paket als v0.99.3-Kandidat; nicht als v0.99.4-Runtime-Prüfung auslegen |
| Semantic-Consistency-Validator | 221/221 PASS | Dokumentierter Validatorumfang |
| State-Machine-Validator | 504/504 PASS | Dokumentierter Validatorumfang |
| Schema/State-Machine-Crosswalk | 65/65 PASS | Dokumentierter Validatorumfang |
| Release-Bundle-Validator | 319/319 PASS | Dokumentierter Validatorumfang |
| Phase-1-Python-Unit-Tests | 23/23 PASS | Lokaler Referenzprototyp; keine produktive/distributive Laufzeit |

Die einzelnen Prüfzahlen stammen aus unterschiedlichen Suiten und teilweise unterschiedlichen Paketständen. Sie sind **nicht additiv** und dürfen nicht als eine gemeinsame Zahl von unabhängigen Anforderungen dargestellt werden.

## 2. Rückwirkende Bestandsabdeckung

Im Master-Archiv vorhanden sind frühe Phase-0-Pakete v0.1.0/v0.2.0/v0.2.1, Architektur v0.4.0, Distributed Protocol v0.5.0, v0.6, Konsolidierungs- und Auditstände v0.7.0 bis v0.9.4, Closure-Kandidaten v0.99.x, das v1.0.0-Gate-Artefakt sowie v1.1.0-Referenzprototyp und Wissensdatenbank. Die archivierten ZIPs sind lesbar.

Das beweist **nicht**, dass jede einzelne ursprüngliche Anforderung aus jedem historischen Dokument bereits einer aktuellen Requirement-ID, einer normativen Quelle, einem konkreten Schema-/Codepfad und einem Test zugeordnet wurde. Für diese vollständige RTM fehlen noch eine explizite zeilen-/anforderungsbasierte Quellenerfassung und die manuelle Entscheidung bei widersprüchlichen oder impliziten Altanforderungen.

## 3. Konkrete Abweichungen und offene Punkte

### A-001 — Testzahl im Prototyp-Bericht
- **Befund:** `tests/test-report.txt` bzw. Statusdokumentation nennt 22 Tests; frische Ausführung findet 23 Tests und alle bestehen.
- **Status:** OPEN — Dokumentationskorrektur erforderlich.
- **Korrektur:** Testreport mit exakt reproduzierbarem Befehl, Python-Version und 23/23 aktualisieren; Bericht nicht manuell ohne erneuten Lauf ändern.

### A-002 — Prüfzahlen aus unterschiedlichen Ständen
- **Befund:** frühere Zusammenfassungen nennen 310, 319 und 325; aktuell ausgeführter Release-Bundle-Validator liefert 319/319.
- **Status:** OPEN — Herkunft/Suite-Scope der älteren Zahlen muss in einer Versionsmatrix dokumentiert werden.
- **Korrektur:** Jede Zahl mit Validatorpfad, Paketversion, Commit/Hash, Ausführungszeit und Scope ausweisen; keine Summe bilden.

### A-003 — Runtime validiert Phase-0-Verträge nicht vollständig
- **Befund:** Der lokale Prototyp besitzt typed Python-Modelle und Guardrails, aber der vollständige kanonische JSON-Schema-Satz ist nicht nachgewiesen durchgehend an allen Runtime-Eingängen/Ausgängen angebunden.
- **Status:** OPEN — Phase-1-Konformitätslücke.
- **Korrektur:** Schema-Validator am Ein-/Ausgang und Round-trip-Tests; unknown/missing fields, Versionsfehler, Enums, Grenzwerte und nicht erlaubte Transitionen testen.

### A-004 — Fehlende Phase-1-Negativfälle
- **Befund:** 23 Tests decken wichtige Pfade ab, beweisen aber nicht die vollständige Negativfallliste aus dem Phase-1-Plan.
- **Status:** OPEN.
- **Korrektur:** Tests für abgelaufene/verbrauchte/widerrufene Genehmigungen, Digest-Abweichung, fehlende Capability, unknown outcome, doppelte Events, stale CAS und Mutation durch Alias-Referenzen hinzufügen.

### A-005 — Historische Freigabestatus nebeneinander
- **Befund:** Historische Kandidaten enthalten frühere Sperrstände; v1.0.0 dokumentiert späteren Closure-/Start-Gate-Status.
- **Status:** HISTORICAL, aber Darstellung muss eindeutig sein.
- **Korrektur:** Historische Dateien nicht verändern; Index kennzeichnet pro Dokument `historical`, `superseded` oder `current`, mit Verweis auf maßgebliche Entscheidung.

### A-006 — Dauerbetrieb nicht implementiert
- **Befund:** Keine belegte produktive Persistenz/Wiederanlauf, durable Inbox/Outbox, produktive Connectoren, signierte/atomar einmalig verbrauchte Genehmigungen, Multi-Tenant-Auth, Secret-Management oder Deployment.
- **Status:** DEFERRED/OPEN — nicht als Phase-0-Fehler deklarieren, aber vor produktiver externer Ausführung blockierend.
- **Korrektur:** Roadmap-Gates W4/W5 mit expliziten Abnahmekriterien beibehalten.

### A-007 — Vollständige historische Requirement Traceability fehlt
- **Befund:** Traceability- und Crosswalk-Dokumente existieren, aber eine zentrale vollständige RTM über alle historischen Quellen mit einer Zeile je Requirement ist nicht nachgewiesen.
- **Status:** OPEN — dies ist die zentrale verbleibende Auditaufgabe.
- **Korrektur:** Jede historische normative Aussage erfassen und mit Quelle/Zeile, Entscheidung, kanonischem Dokument, Schema, Runtime-Code, Test/Evidenz und Status verknüpfen.

## 4. Querverweis- und Integritätsbewertung

- Die JSON-Dateien im Master sind syntaktisch lesbar.
- Die 29 enthaltenen ZIP-Dateien sind CRC-lesbar.
- Alle 169 Einträge der vorhandenen `SHA256SUMS` stimmen mit den Dateien überein.
- Die drei zentralen Markdown-Dateien verwenden derzeit kaum explizite Markdown-Hyperlinks; daher ist ein klassischer Link-Checker allein kein ausreichender Querverweis-Audit.
- Fachliche Crosswalks sind vorhanden, besonders `docs/17_SCHEMA_STATE_MACHINE_CROSSWALK.md`; sie ersetzen die fehlende vollständige RTM nicht.
- Der Master enthält viele einzelne Release-ZIPs, aber ein ZIP in einem ZIP ist nicht dasselbe wie eine kanonisch zusammengeführte Arbeitskopie. Die historischen Artefakte bleiben unverändert erhalten.

## 5. Kanonische Statusentscheidung

1. **Phase 0 Spezifikation:** `DONE-SPEC` nur innerhalb der explizit ausgeführten und dokumentierten Validatorumfänge.
2. **Formale Projektfreigabe:** v1.0.0 enthält einen dokumentierten Closure-/Start-Gate-Status; dies ist keine unabhängige Zertifizierung.
3. **Phase 1:** `PROTOTYPE`, keine Produktionsfreigabe.
4. **Gesamtaudit:** `PARTIAL_PASS`; keine Aussage „jeder historische Einzelpunkt abgeschlossen“, bis A-007 geschlossen ist.
5. **Produktionsreife:** `NOT ESTABLISHED`.

## 6. Nächster verbindlicher Schritt

Erstelle `TRACEABILITY/REQUIREMENT_TRACEABILITY_MATRIX.csv` und `TRACEABILITY/SOURCE_REGISTER.csv`. Jede Zeile muss mindestens enthalten: `requirement_id`, `source_archive`, `source_path`, `source_location`, `normalized_requirement`, `disposition`, `canonical_reference`, `schema_reference`, `implementation_reference`, `test_reference`, `evidence`, `status`, `reviewer_note`. Jede nicht nachweisbare Verbindung bleibt `OPEN` statt aus dem Kontext geraten zu werden.


## Schrittweiser Abschluss — Schritt 1 (2026-10-20)

Automatisiertes Inventar und RTM-Kandidaten wurden angelegt: `TRACEABILITY/SOURCE_REGISTER.csv` (174 Dateien) und `TRACEABILITY/REQUIREMENT_TRACEABILITY_MATRIX.csv` (1571 extrahierte Kandidaten). Die Einträge sind absichtlich `UNASSESSED`/`OPEN`; Extraktion allein ist keine semantische Abnahme. Nächster Schritt ist die historische Quellenauswertung v0.1–v0.6 inklusive Wissensdatenbank.


## Schritt 2 — historische Extraktion (2026-10-20)

Die RTM wurde um 3500 zusätzliche Kandidaten aus eingebetteten historischen ZIP-Dateien erweitert; Gesamtumfang 5071 Zeilen. Extraktion beruht auf Checklisten, Überschriften und explizit normativ klingenden Formulierungen. Daher sind false positives möglich; diese werden im nächsten Review klassifiziert. Es wurde keine Zeile als fachlich abgenommen markiert.


## Schritt 4 — Semantischer Crosswalk (2026-10-20)

19 historische Kernanforderungen aus v0.4.0/v0.5.0/v0.6.0 wurden gegen das kanonische v0.99.4-Spezifikationspaket und die v1.1.0-Referenzlaufzeit geprüft. Ergebnisdateien: `TRACEABILITY/HISTORICAL_CORE_CROSSWALK.csv` und `docs/STEP4_HISTORICAL_CORE_CROSSWALK.md`. Der Prototyp-Testlauf ergab 23/23 bestandene Tests; `PHASE1_IMPLEMENTATION_STATUS.md` nennt noch 22 und muss als inkonsistent gelten. Die 19 Anforderungen sind nach Befund klassifiziert, die globale Kandidatenmatrix bleibt offen. Status: PARTIAL_PASS.


## Schritt 5 — Kanonische Invarianten gegen Runtime-Evidenz (2026-10-20)

Die 30 Einträge aus `tests/invariants.json` und ihre Phase-0-Coverage wurden einzeln in `TRACEABILITY/CANONICAL_INVARIANT_RUNTIME_CROSSWALK.csv` abgebildet. Phase-0-Statuswerte wie `specification-coverage-only` wurden ausdrücklich nicht als Runtime-Conformance interpretiert. Der Crosswalk nennt Runtime-Dateien und Tests, wo vorhanden, und markiert unbelegte Implementierung konservativ als `SPEC_ONLY` bzw. `OPEN_RUNTIME_GAP`. Er ist eine nachvollziehbare Code-/Test-Evidenzprüfung, keine formale Verifikation. Gesamtstatus: `PARTIAL_PASS`; Produktionsreife: `NOT ESTABLISHED`.


## Schritt 6 — Runtime-Patch und Regressionstests (2026-10-20)

Die Referenzruntime wurde als v1.1.1 fortgeführt. Approval-Lifecycle-Felder werden bei Vorliegen auf Ablehnung/Widerruf/Verbrauch, zukünftigen Gültigkeitsbeginn und Usage-Limit geprüft. Nested payloads werden tief kopiert, und der Runtime-Fingerprint basiert auf dem Snapshot. Neue Tests decken revoked/consumed/future-dated approvals und Payload-Aliasing ab. Ergebnis: 27/27 Tests bestanden; Demo erfolgreich. Diese Änderung validiert keine atomare oder persistente Einmalfreigabe und schließt keine verteilten Sicherheitslücken. Status bleibt `PARTIAL_PASS`; Produktionsreife `NOT ESTABLISHED`. Details: `docs/STEP6_RUNTIME_PATCH_AND_REGRESSION_TESTS.md`.


## Step 7 update — runtime admission guard

Prototype v1.1.2 adds process-local serialization of action admission and in-memory tracking for explicitly single-use approval IDs. Regression tests cover concurrent duplicate requests (40 calls across 12 threads), reuse of a single-use approval under a different idempotency key, and missing stable approval ID. The complete prototype suite passes 30/30. This is a bounded single-process improvement only; it is not durable or distributed and does not establish production readiness.

## Schritt 9 — Runtime-/SQLite-Integration (2026-10-20)

Der Prototyp v1.1.4 integriert den SQLite-Admission-Store optional in `PRAINRuntime.request_action`. Nachweise: persistentes Replay zwischen Runtime-Instanzen, fail-closed Fingerprint-Konflikt nach Neustart und atomarer Single-use-Approval-Verbrauch über unterschiedliche Idempotenzschlüssel. Gesamter Prototyp-Testlauf: 38/38 bestanden; Demo bleibt simuliert. Nicht persistent sind weiterhin StateStore, GoalRegistry, EventBus und EvidenceLedger; Outbox/Dispatcher, Crash-Recovery externer Effekte, Approval-Signaturprüfung und authoritative Revocation fehlen. Status `PARTIAL_PASS`, Produktionsreife `NOT ESTABLISHED`.


## Step 10 update — durable outbox (2026-10-20)

Prototype v1.1.5 now persists an outbox item in the same SQLite transaction as durable admission/receipt when the store is configured. It adds `PENDING -> IN_FLIGHT -> terminal/unknown` transitions, single-DB transactional claims, and conservative restart recovery to `OUTCOME_UNKNOWN`. The suite passes 41/41 tests. This does not execute external actions and does not establish exactly-once semantics; provider reconciliation, broader persistence and multi-host coordination remain open. See `docs/STEP10_DURABLE_OUTBOX_AND_RECOVERY.md`.


## Step 10 update — durable outbox (2026-10-20)

Prototype v1.1.5 now persists an outbox item in the same SQLite transaction as durable admission/receipt when the store is configured. It adds `PENDING -> IN_FLIGHT -> terminal/unknown` transitions, single-DB transactional claims, and conservative restart recovery to `OUTCOME_UNKNOWN`. The suite passes 41/41 tests. This does not execute external actions and does not establish exactly-once semantics; provider reconciliation, broader persistence and multi-host coordination remain open. See `docs/STEP10_DURABLE_OUTBOX_AND_RECOVERY.md`.
