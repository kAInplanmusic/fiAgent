# Schritt 9 — SQLite-Admission in die Runtime integriert

Datum: 2026-10-20 · Referenzprototyp v1.1.4

## Umgesetzt

- `PRAINRuntime(..., admission_store=DurableAdmissionStore(path))` kann die dauerhafte Admission optional aktivieren.
- Vor einer erneuten Policy-Auswertung liest die Runtime vorhandene dauerhafte Admission-Daten: gleicher Idempotenzschlüssel plus gleicher Request-Fingerprint liefert den gespeicherten Receipt; ein abweichender Fingerprint wird fail-closed abgelehnt.
- Für eine neu zugelassene simulierte Aktion werden Receipt und gegebenenfalls Verbrauch einer Single-use-Freigabe durch eine SQLite-Transaktion mit `BEGIN IMMEDIATE` und Unique Constraints gespeichert.
- Eine zweite Runtime-Instanz mit derselben Datenbank kann den Receipt nach Neuinstanziierung wiedergeben.
- Eine Single-use-Freigabe kann nicht über unterschiedliche Idempotenzschlüssel hinweg erneut verbraucht werden, auch nicht über eine neu erzeugte Runtime-Instanz.
- Ohne `admission_store` bleibt das bisherige In-Memory-Verhalten erhalten.

## Validierung

Aus dem Verzeichnis `archive/PRAIN_Phase1_Prototype_v1.1.4/`:

```bash
python -m unittest discover -s tests -v
python -m prain.demo
```

Ergebnis: **38/38 Unit-Tests bestanden**. Drei neue Runtime-Integrationstests prüfen Replay zwischen Runtime-Instanzen, Konflikt bei verändertem Payload und dauerhaften Single-use-Verbrauch. Die Demo bleibt `simulated_only`.

## Explizite Grenzen

- Integriert ist dauerhafte Admission/Receipt-Verwaltung, nicht die vollständige Runtime-Persistenz.
- `StateStore`, `GoalRegistry`, `EventBus` und `EvidenceLedger` bleiben im Arbeitsspeicher und werden nach Neustart nicht rekonstruiert.
- Es gibt noch keine dauerhafte Outbox oder Dispatcher; reale externe Effekte werden nicht ausgeführt.
- Die Policy-Entscheidung wird vor der Store-Transaktion ausgewertet. Die Transaktion sichert Idempotenz, Receipt-Speicherung und Single-use-Verbrauch ab, persistiert aber noch kein vollständiges signiertes Entscheidungsbündel oder externen Ausführungsauftrag.
- Authentizität von Freigaben und maßgebliche Revocation-Prüfung sind nicht implementiert.
- SQLite-WAL/FULL erhöht lokale Persistenzgarantien, beweist aber weder Multi-Host-Konsens noch Exactly-once-Ausführung externer Aktionen.

Gesamtstatus bleibt `PARTIAL_PASS`; Produktionsreife ist `NOT ESTABLISHED`.
