# PRAIN Traceability — Arbeitsstand 2

Stand: 2026-10-20

- `SOURCE_REGISTER.csv`: Inventar der Master-Archivdateien mit lokal berechnetem SHA-256.
- `REQUIREMENT_TRACEABILITY_MATRIX.csv`: 5071 Kandidatenzeilen, darunter 3500 zusätzliche historisch extrahierte Anforderungen/Überschriften aus den eingebetteten ZIP-Archiven.

## Status und Grenzen
Diese RTM ist eine Arbeitsmatrix, keine abgeschlossene Konformitätsbehauptung. Historische Extraktion ist bewusst breit und enthält möglicherweise Überschriften, Checklisten und normative Aussagen; jede Zeile muss semantisch bewertet werden. Der Status bleibt `OPEN`/`UNASSESSED`, bis Fundstelle, Entscheidung, kanonische Referenz, Schema, Implementierung und Test geprüft sind.

## Arbeitsablauf
1. Prüfe historische Kandidaten und entferne keine Quelle; kennzeichne Duplikate über `DUPLICATE_OF`.
2. Vergib `RETAINED`, `EXTENDED`, `SUPERSEDED`, `DEFERRED`, `REJECTED_WITH_REASON` oder `DUPLICATE_OF`.
3. Verknüpfe jede normative Anforderung mit genau einer maßgeblichen aktuellen Quelle.
4. Prüfe referenzierte Dateien, IDs, Schemas und Tests automatisiert.
5. Entscheide fachliche Widersprüche einzeln mit Begründung und Änderungsnachweis.
