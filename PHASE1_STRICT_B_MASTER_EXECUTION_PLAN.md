# P.R.A.I.N. — Phase 1: Master-Umsetzungs- und Abnahmeplan (Strict B)
Stand: 2026-10-25 | Version: 1.0 | maßgeblicher Stand: GitHub main `7ccb68129c46e597efe3d3d0a759dda2e28494f6`

## 0. Verbindliche Regeln

**Scope:** Phase-1-Architektur entsprechend der historischen PRAIN-Quellen (v0.1 bis v0.6), Phase-0-Green-Spezifikation v0.99.6, aktuellem ROADMAP.md (W0–W9) und sämtlichen gültigen Entscheidungen bis zum Ist-Stand. P/R/A/I/N und die vier Ebenen semantisch, Koordination, Ausführung, Invarianten/Evidenz bleiben bestehen. Der Nutzer verlangt Strict B, keine nachträgliche Verkleinerung des Umfangs.

**Ampeln:** PASS nur mit reproduzierbarem Artefakt, Test und Traceability. OPEN = fehlt; BLOCKED = dokumentierte externe Abhängigkeit; FAILED = Test nicht bestanden; PARTIAL = belegter Teilumfang. Grüne Unit-Tests belegen nicht die Gesamtfreigabe.

**Sicherheitsgrenzen:** Kein externer Side Effect bis zur separaten, autorisierten Freigabe. Deny-by-default, Least Privilege, kein stilles Umschreiben historischer Entscheidungen, keine erfundene Evidenz. Unklare Ausführung bleibt UNKNOWN bis unabhängig abgeglichen. Keine globalen Exactly-Once-Zusagen. Keine Hintergrund-Workflows/GitHub Actions starten. Änderungen mit Versions- und SHA256-Nachweis. Keine Schlüssel ins Repo.

## 1. Arbeitsreihenfolge und Artefakte

### G00 — Reproduzierbarer Ist-Stand und Sicherung [P0]
- [x] Server main/Remote main synchronisiert; letzte gesicherte SHA siehe oben.
- [x] 186 Unit- und Integrationstests PASS, Release-Manifest 92/92 PASS (Baseline zum Plan).
- [ ] Quellstand unveränderlich mit git SHA, GitHub-Commit, manifest SHA, Python/OS-Versionsstand und Toolversionen protokollieren.
- [ ] Server-Datenbanken über konsistentes SQLite-Backup sichern, Integrität nach Kopie prüfen, Wiederherstellung in isoliertem Pfad testen. Keine Secrets in Berichte.
- [ ] SHA256SUMS für Originale, Spec-Archive, Release und Backup erzeugen; ZIP gegen Zip-Slip, CRC und doppelte Pfade prüfen.
- [ ] Arbeitsschritte nicht auf GitHub-Worker auslagern; lokale Hetzner-Ausführung.
- **Exit:** Wiederholbarer Recovery-Drill, keine ungesicherten Änderungen, Hash-Abgleich.

### G01 — Historische Rückverfolgbarkeit und Governance [P0]
- [ ] Quellinventar aus v0.1.0–v0.6, Wissensdatenbank, v0.7–v0.99.6 und Step 0–aktuell erfassen. Je Quelle Pfad, Paket-SHA, Normativität, Entscheidungsversion, Supersession dokumentieren.
- [ ] Sämtliche 5.071 Kandidatenzeilen einzeln beurteilen (keine pauschale Automatikfreigabe): REQUIREMENT_ID, Quelle, wörtlich begrenzte Normreferenz, Disposition RETAIN/EXTEND/SUPERSEDE/DEFER/OPEN, Begründung, Zielfähigkeit, Prüfnachweis, Verantwortlicher.
- [ ] Duplikate, Widersprüche und unterschiedliche Begriffe gegen kanonisches P/R/A/I/N/SCF/HAL/Policy-Modell auflösen.
- [ ] Jede normative Requirement-ID zu Vertrag, Datei/Klasse, Testnamen und Evidence-ID mappen; fehlende Zuordnung blockiert das Gate.
- [ ] Die historische Phase-0-Green-Spezifikationsfreigabe vom technischen Phase-1-Status trennen.
- **Exit:** 100% der historischen Kandidaten überprüft; kein normativer und ungeklärter Eintrag.

### G02 — Kanonische Schemas/State-Machines [P0]
- [ ] Festes Envelope v1 mit UUID/opaque ID, scope, tenant, source, principal, expiry, signature key ID, dependencies, epistemic state, provenance, lineage und Schema-Migrationsregeln.
- [ ] JSON-Schema/Typmodelle für Observation, Event, Claim, Graph-Edge, Goal, Approval, Intent, Action, Receipt, Inbox, Outbox, Conflict, Tombstone und HAL erstellen.
- [ ] Runtime-Pfade validieren an Trust-Boundary (nicht nur in Tests); unknown fields, falsche Enums, Zeitzone, NaN, Zukunfts- und Ablaufzeiten ablehnen.
- [ ] Zustandsübergänge aus Phase 0 maschinenlesbar gegenüber dem Runtime-Code prüfen; property-/mutationbasierte Negativtests.
- [ ] Versionsmigrationen vorwärts/rückwärts unter kontrollierter Rollback-Regel mit kaputten und veralteten Daten testen.
- **Exit:** Vollständige Schema-/State-Machine-Matrix; 100% Pflichtpfade getestet.

### G03 — Kanonische Semantik, SCF und Provenienz [P0]
- [x] Lokales Schema, adopt/hypothesis/conflict/defer und persistente Inbox; HTTP-Empfang und Dispatcher als Referenz.
- [ ] Graph-Entities und Edges mit confidence, Gültigkeitsintervallen, epistemischem Status und Provenienz; keine unbelegten Fakten automatisch autoritativ setzen.
- [ ] Alle sieben SCF-Empfängerentscheidungen mit Gründeintrag, Konfliktregister, Review/Resolution, Invalidation-Graph, Replay, DLQ und Dead-Letter-Suche.
- [ ] L0-L3 selective routing, semantische scopes, Inbox/Outbox-Entkopplung, Projection-Lag, TTL und Dependency-Invalidierung unter Reorder/Duplikat.
- [ ] Konsistente und idempotente Replay-Deterministik mit Capture/Compare-Tests und sicheren Schema-Upgrades.
- [ ] Redaktions- und Löschereignisse über jeden abgeleiteten Knoten bzw. Index propagieren.
- **Exit:** Integration, Reorder/Fuzz, Konfliktauflösung und Cross-node SCF-Abnahmesuite bestanden.

### G04 — Wirklich verteilte Architektur [P0]
- [ ] Transport-Adaptercontract unabhängig von HTTP/JetStream definieren. HTTP-Sender/Empfänger plus alternativen Stub implementieren.
- [ ] Getrennte Server-/Prozessinstanzen deployen, eindeutige Node-Identitäten, Transportauthentifizierung mit verwaltetem Key-Rotation-, Revocation- und Peer-ACL-Modell, TLS/mTLS mit Zertifikatsprüfung.
- [ ] Netzwerk: erreichbare Ports/Firewall, Rate Limits, Body-Limits, Zeitouts, Backpressure, Retry-Budget, Circuit Breaker und Tracing mit Korrelation.
- [ ] Leases mit monotonic fencing am tatsächlich autoritativen Ziel/Side-Effect-Adapter erzwingen; split-brain und Uhrdrift simulieren.
- [ ] Reconcile via vom Empfänger signierte, separat validierbare Delivery/Outcome-Receipts; bloßes HTTP 2xx ist nicht automatisch Nachweis externen Effekts.
- [ ] Disconnect, Half-open, Timeout nach Commit, Duplikat, Reorder, Partition, Wiederherstellung, Crash während Transaktion und Key-Rotation gleichzeitig negativ testen.
- [ ] Benchmarks für Queue-Verzögerung, Speicher, Delivery-Rate, Idempotenz, Backlog und Recovery-Zeit protokollieren; zwei isolierte Knoten/Prozesse sind Mindestnachweis, zwei reale Hosts für Betriebsfreigabe.
- **Exit:** Erfolgreiche echte Mehrknoten-Pipeline mit reproduzierbarer Fault Injection und signierten Quittungen. Keine pauschale Distributed-Consensus-Behauptung.

### G05 — Trust Boundary, AuthN/AuthZ und Approval [P0]
- [x] Lokale Tenant-Principal-Capabilities, Credentials-Digest, Rotation, Revocation und optionaler authentifizierter Runtime-Einstiegspunkt.
- [ ] Authentifizierte Middleware an *jedem* mutierenden Entry-Point, insbesondere rohem Runtime.request_action, Admin-/Provisioning- und Backup-Pfaden; internes Capability-Token statt umgehbarer Fassade.
- [ ] Key-Management/KMS oder verschlüsselter Secret-Store, eindeutige Issuer-Identität, Approval an Principal, Actor, Tenant, Action, Hash, Scope, Deadline und Nonce binden.
- [ ] Atomare Approval-Verwendung und Revocation-Race über Prozessgrenzen; reject on unknown issuer/key/tenant/digest, expired, replay, withdrawn, altered request, capability loss.
- [ ] Evidence-Ledger: Vertrauensanker, signierte/verifizierbare unabhängige Kriterien, Unveränderlichkeits- und Tamper-Tests, atomare Goal-Completion.
- [ ] Independent Security/Threat-Model-Test: SSRF, CSRF, replay, schema abuse, race, DOS, privilege escalation, audit tamper, SQL injection, secret leakage.
- **Exit:** Kein unautorisierter Pfad mit externer Wirkung; Sicherheitsnachweise und Reviewer bestätigt.

### G06 — Datenschutz, Retention und Löschung [P0]
- [x] Mandantengetrennte lokale Datenprojektionen und Lösch-Tombstones.
- [ ] Klassifikation/Einwilligung/Legal Basis/Owner, Zweckbindung, Aufbewahrungsfristen und Auditierung für jede Datenkategorie.
- [ ] Redaction bevor Ereignisse, Receipts, Logs, Traces, Backups, Cache, Graph, Embeddings und LLM-Aufrufe Daten übernehmen.
- [ ] Löschung/Tombstone zuverlässig über Ursprung, Index, Suche, Edge/Claim-Graph, Cache und verteilte Knoten propagieren; Backups inkl. Ablauf/Restore-Replay-Schutz.
- [ ] Nicht-löschbare Integritäts- und Compliance-Beweise datensparsam/irreversibel designen und rechtskonform begründen.
- [ ] Data-subject-access/export/deletion Simulation, Angriffsszenarien und Isolation nach Restore/Replica-Lag.
- **Exit:** End-to-end Löschnachweis inklusive Restore und Nebenkanälen, fachlich/rechtlich freigegeben.

### G07 — Anima, HAL, Recovery und Adaptation [P1]
- [x] Versionierte lokale Anima, persistente SQLite-Variante, HAL observe-only sowie lokale Cooldown-/Budget-Vorschläge.
- [ ] Anima-Identität und Versionshistorie im verteilten State, Merge-/Konfliktstrategie, CAS bei mehreren Autoren, Provenienz.
- [ ] HAL-Signal-Vertrag inkl. Last-Signals, Liveness, falsches Healthy, Fehlerrate, Queue-Lag, frisch/alt/unknown.
- [ ] Durable Proposal-Budget und Cooldown über Neustart und mehrere Knoten; anti-oscillation, Stop-Switch und Interventionstrigger.
- [ ] Autorisierter Repair-Workflow: Vorschlag → Policy → Approval → Canary → Monitor → Rollback/Stop → Evidence.
- [ ] Failover, verlorenes Ack, Partial Commit, Rollback- und Oscillation-Tests.
- **Exit:** HAL kann keine Privilegien erteilen; Anpassung begrenzt, rücksetzbar, nachvollziehbar.

### G08 — Abstraktionen und Provider [P1]
- [ ] Versionierte LLM, Embedding, Transport, Storage, Compute, Scheduler Adapter-Interfaces + Capabilities.
- [ ] Pro priorisierter Adapterfamilie mindestens zwei Implementationstypen durch dieselbe Contract Suite; kein ungeprüfter Anbieterwechsel.
- [ ] Kosten-, Rate-Limit- und Ausfallbehandlung, keine Cloud-Ressource oder kostenpflichtige Instanz ohne konkrete Autorisierung.
- [ ] Quantum-ready ausdrücklich nur Vertrag, Simulator und austauschbares Compute-Backend, kein vermeintlicher Quantenvorteil.
- **Exit:** Austauschbarkeit belegt, keine Regression von Semantik/Evidenz.

### G09 — Gesamtqualität und Release [P0]
- [ ] Alle Anforderungen/Gates G00–G08 mit Links auf Ergebnisse, Schemas, Tests, Commits und externe Prüfergebnisse.
- [ ] Unit, Integration, System/E2E, Negativ, Security, Performance, Failover, Multi-Node-Chaos, Privacy, Migrations- und Backup/Restore-Tests separat aggregieren.
- [ ] Tests in wiederhergestellter sauberer Umgebung Python 3.12 wiederholen; reproduzierbarer Build ohne GitHub Actions.
- [ ] Manifest + SHA256SUMS für gesamte Phase-1-Quelle, Integritätsprüfung gegen ZIP und sauberen Git-Tag.
- [ ] Bedrohungsmodell, SLO, Operations-/Deployment-/Rollback-Runbooks, Hardening, Monitoring und Kostengrenzen.
- [ ] Unabhängige Security-/Architekturprüfung und explizite autorisierte Phase-1-Abnahme. Diese Entscheidung kann der Assistent nicht fingieren.
- **Exit:** alle normativen Anforderungen akzeptiert, Evidenz durchgängig, keine roten Tests oder ungerechtfertigten Ausnahmen. Erst dann `PHASE1_GREEN_STRICT_B`.

## 2. Aktuelle kritische Blocker

| ID | Blocker | Konsequenz |
|---|---|---|
| B01 | 5.071 Kandidaten nicht vollständig normativ geprüft | Kein formales Requirements-Gate |
| B02 | Keine nachgewiesene eigenständige, echte 2-Host-Kommunikation/TLS/Key-Verteilung | Kein Distributed-End-to-End-Gate |
| B03 | Roher request_action()-Pfad nicht durchgängig identitätsgeschützt | AuthN/AuthZ nicht vollständig |
| B04 | Keine End-to-End-Retention/Löschung über Ledger/Cache/Backups/Graph | Datenschutz-Gate offen |
| B05 | Lokale SCF-Claims ohne vollständige Canonical-Graph-, Conflict- und Replay-Konformität | SCF-Gate offen |
| B06 | HAL-/Anima-Grenzen bei Mehrknotenbetrieb nicht vollständig geprüft | Adaptation-Gate offen |
| B07 | Kein unabhängiger Security-Reviewer / explizite Abschlussfreigabe | Keine formale Vollabnahme |

## 3. Ausführungsregel (ohne Rückfragen)

Alle ohne externe Zugangsdaten und ohne zusätzliche Kosten möglichen Änderungen werden nacheinander mit überprüfbaren Tests implementiert. Bei fehlendem Server/IdP/Zertifikat/Reviewer erfolgt kein fingierter Nachweis; stattdessen `BLOCKED` mit exaktem Prüfpfad. Niemals behaupten, in Abwesenheit einer tatsächlichen Automation oder laufenden Sitzung im Hintergrund weiterzuarbeiten.

## 4. Fortschrittsmatrix

- 2026-10-25 Start: 186/186 Unittests, 92/92 Manifest-Prüfungen, Git main sauber.
- Phase 0: `GREEN_PHASE0_SPECIFICATION_CLOSED` (historischer Spezifikationsumfang).
- Phase 1: `PARTIAL_PASS`. Alle G00–G09 strengen Gates sind nur dann grün, wenn jedes Pflicht-Exitkriterium separat belegt ist.
