# Schritt 8 — SQLite-Dauerhaftigkeit und transaktionale Admission

## Ergebnis
Prototyp v1.1.3 enthält `prain/durable_admission.py`: SQLite-Tabellen mit Unique-Constraints für Idempotenzschlüssel und Single-use-Approval-IDs; `BEGIN IMMEDIATE`; WAL und `synchronous=FULL` für dateibasierte DBs; Replay derselben gespeicherten Receipt bei gleichem Fingerprint; Konflikt bei verändertem Fingerprint; persistenter Freigabeverbrauch und Rollback bei fehlgeschlagener Admission.

## Tests
35/35 Tests bestanden (30 bestehende Tests und 5 neue SQLite-Tests). Die neuen Tests prüfen Wiederverwendung nach Neuinstanziierung, Fingerprint-Konflikt, Single-use über Store-Neuinstanziierung, 24 parallele Aufrufe über 8 Worker und atomaren Rollback.

## Grenzen
Das neue Modul ist ein eigenständiges Persistenzprimitive, noch nicht in `PRAINRuntime.request_action` verdrahtet. Die aktive Runtime verwendet weiterhin flüchtige In-Memory-Datenstrukturen. Die gespeicherte Receipt steht für simulierte Admission, nicht für den Nachweis einer ausgeführten externen Aktion. Eine SQLite-Transaktion kann keine externe Nebenwirkung atomar einschließen und garantiert kein Exactly-once über Prozess- oder Netzwerkausfälle hinweg.

## Nächster Schritt
Repository-Port in der Runtime, Migration der Admission-Entscheidung in eine Transaktion, transactional outbox, sowie Kill-/Restart-Tests an jedem Commit-Punkt und Multi-Instanz-Tests. Vor realen Effekten muss der Dispatcher unbekannte Ergebnisse als `OUTCOME_UNKNOWN` behandeln und Reconciliation statt blindem Retry unterstützen.
