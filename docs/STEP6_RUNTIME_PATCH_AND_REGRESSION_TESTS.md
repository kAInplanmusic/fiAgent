# Schritt 6 — Runtime-Patches und Regressionstests (2026-10-20)

## Umfang

Die Referenzimplementierung v1.1.0 wurde als neue Version v1.1.1 fortgeführt; die historische v1.1.0 bleibt unverändert erhalten.

### Änderungen

1. `PolicyGateway.evaluate`: explizit abgelehnte, verbrauchte und widerrufene Approvals werden verweigert; `valid_from`, `max_uses` und `usage_count` werden geprüft, wenn diese kanonischen Lifecycle-Felder geliefert werden.
2. `ActionRequest.create` und `Observation.create`: verschachtelte Payloads werden tief kopiert, um Caller-Mutation nach Erstellung zu verhindern.
3. `PRAINRuntime.request_action`: erzeugt einen unveränderlichen Payload-Snapshot, verwendet ihn für Fingerprint und simuliertes Resultat.
4. Regressionstests für widerrufene/verbrauchte/future-dated Approvals und Payload-Aliasing ergänzt.

## Nachweise

- `python -m unittest discover -s tests -v`: **27/27 bestanden**.
- `python -m prain.demo`: erfolgreich; Evidence-Chain valid; Aktion ausdrücklich `simulated_only`.
- Version/Manifest neu geschrieben; historische v1.1.0-Dateien bleiben im Masterarchiv erhalten.

## Grenzen / verbleibende Lücken

- Approval-Usage wird nicht atomar erhöht oder persistent gespeichert. `lifecycle_status` muss vom Aufrufer aktuell geliefert werden; keine Revocation-Abfrage gegen einen zentralen Authority Store.
- Das bestehende Approval-Binding im Prototyp (`action`, `target`, `input_hash`, `idempotency_key`) ist noch kein vollständiger Ersatz für die kanonischen Felder `action_digest`, `actor_principal_id`, `tenant_id`, `target_scope_digest` und `side_effect_digest`.
- Keine persistente Inbox/Outbox, Restart-Recovery, Multi-Process-Koordination, vollständige Tenant-Isolation oder echte externe Seiteneffekte.
- Daher: Runtime-Sicherheit verbessert, aber keine Vollkonformität und keine Produktionsfreigabe. Status bleibt `PARTIAL_PASS`.
