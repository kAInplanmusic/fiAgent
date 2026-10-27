# PRAIN – geprüfter Arbeitsstand, 25.10.2026

Ausgangsstand: remote Git `36070c65e47f52bfa9aac621905d4a1c5d0eafa8`.
Dieser Stand ist ein technischer Prüfkandidat; Strict-B-Produktionsabnahme bleibt offen.

Aktueller Runtime-Checkpoint: lokal `e47f9e5`, Server `5c1059e`. Die normativen Einzelbewertungen wurden separat in lokal `7b2282f` und Server `fa98bca` gesichert; diese Commits sind keine Produktionsfreigabe.

## Implementiert

- Roher Runtime-Aktionsaufruf verweigert standardmäßig die Annahme. Authentifizierte Aktionen prüfen Identität/Berechtigung erneut vor Replay und Admission. Offline-Simulation erfordert `trusted_local_prototype_mode=True`; strukturierte Identität verhindert Tenant-/Principal-Kollisionen.
- SCF transportiert mit geprüfter TLS-Konfiguration, ohne automatische Redirects/Umgebungs-Proxies, mit Größenlimits. Dispatcher verlangt einen provisionierten Quittungsschlüssel, bindet HMAC-Quittungen an vollständigen Request, Ziel, Tenant und Claim; alle kanonischen Entscheidungen werden verarbeitet. Unklare Ergebnisse bleiben UNKNOWN.
- TLS-Handshakes laufen mit Timeout in begrenzten Verbindungsworkern, damit stockende Verbindungen den Accept-Loop nicht blockieren.
- Projektionen verweigern verschachtelte Credential-Felder und stille Klassifikationsabsenkung. Persistente Retention mit begrenztem Sweep, Holds und Tombstones; aktuelle vertrauenswürdige Tombstones können vor Freigabe einer wiederhergestellten Projektion angewandt werden.
- Reale getrennte Prozesse/SQLite-Dateien über TLS: Replay nach Neustart, Crash nach Commit vor ACK, Ausfall/Reconciliation und Poison-Isolation.

## Nachweis und Reproduktion

Die vollständige Suite bestand lokal und auf dem PRAIN-Server mit jeweils **259/259 Tests, 0 Fehlern und 0 übersprungenen Tests**. Das Prototype-Manifest umfasst **137 Dateien**. Die in den beiden Testberichten erfassten `prototype/`-Quellhashes stimmen vollständig überein. Die gesamten Repository-Digests unterscheiden sich wegen des jeweils erfassten Dokumentations-/Metadatenstands; daraus wird keine vollständige Byte-Identität beider Repositorys abgeleitet.

| Ausführung | Python / Kernel | Dauer | Bericht und SHA-256 |
|---|---|---:|---|
| Lokal | 3.12.14 / Linux 6.18.55 | 20,217 s | `evidence/canonical_full_suite/results.json`; `717ba802cce6410dd94e8beb55444d33f85eb98f8bf47eea55ae2135b7d37181` |
| PRAIN-Server | 3.12.3 / Linux 6.8.0-138-generic | 29,733 s | `evidence/canonical_server_suite/results.json`; `2b89a784548ac7f4e9871000e220aad695344f113085f2e05926996b3a3f201d` |

Beide Läufe verwenden Python 3.12 mit den kanonischen Abhängigkeiten; keine GitHub Actions. `python3 tools/run_acceptance_evidence.py --out /absolute/results` führt die gesamte Suite aus und speichert Einzelergebnisse, Logs, Plattform und Quellhashes. `python3 prototype/tools/verify_release.py` prüft das unveränderte Prototype-Manifest. `python3 tools/verify_implementation_evidence.py --output /absolute/traceability` überprüft 5071 exakte Quellenreferenzen und erzeugt Code-/Testanker.

Die unabhängige technische Prüfung fand drei Transportprobleme in der ersten Umsetzung. Korrekturen und Wiederholungsnachweise werden im separaten Prüfbericht erfasst. Eine Agentenprüfung ersetzt keine vorgeschriebene menschliche Abnahme.

## Verbleibende Grenzen

- Tests laufen über mehrere Prozesse auf einem Host; Kommunikation zwischen zwei realen Hosts und deren Betriebs-/Partitionseigenschaften ist nicht nachgewiesen.
- Alle 5002 historischen Kandidaten haben nun eine explizite kontextbezogene Disposition: 2554 RETAIN, 2331 NON_NORMATIVE, 47 SUPERSEDE und 70 EXTEND. Der Implementierungsstatus bleibt 651 OPEN, 2061 PARTIAL und 2290 NA. Diese Einordnungen sind keine vollständige unabhängige semantische Freigabe und schließen keine fehlende Implementierung. Für B01 fehlen weiterhin die unabhängige Gesamtprüfung der gültigen Anforderungen und lückenlose Implementierungs-/Testnachweise; 5071 exakte Quellenreferenzen allein beweisen keine Implementierung.
- 68 Schwerpunktanforderungen sind mit Teilnachweisen bewertet. Alle 17 kanonischen Schemas und der authentifizierte dauerhafte kanonische Eingang sind zusätzlich implementiert und getestet; ganze SCF-Graph-/Schema-Migrations-, Provider- und autorisierte HAL-Repair-Workflows bleiben unvollständig.
- Privilegiertes lokales Python/Dateisystem bleibt vertrauenswürdig. Kein KMS-/Issuer-Föderationsnachweis; Autorisierungsentzug ist nicht atomar mit realen entfernten Effekten.
- HMAC belegt die Integrität gegenüber Außenstehenden mit unbekanntem Schlüssel. Sender und Empfänger kennen den Schlüssel; keine asymmetrische unabhängige Nichtabstreitbarkeit.
- Retention betrifft die eigene Projektionstabelle; keine vollständige automatische physische Löschung aus SQLite-Seiten, sämtlichen Backups, Ledgern, Embeddings und externen Replikaten. Wiederhergestellte Projektionen dürfen erst nach autoritativem Tombstone-Abgleich bereitgestellt werden.
- Keine externe Security-Akkreditierung oder menschliche/rechtliche Abschlussfreigabe; alle strengen Gates bleiben bis zum vollständigen Nachweis offen/teilweise erfüllt.

`tools/verify_phase1_gates.py` muss weiterhin mit Nichtnull-Exitcode fehlende Freigaben melden. Dies ist beabsichtigtes Fail-Closed-Verhalten und wird nicht durch Umklassifizierung umgangen.
