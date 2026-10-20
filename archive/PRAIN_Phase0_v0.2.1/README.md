# PRAIN Phase 0 v0.2.1

Framework-neutrales Architektur-, Schema- und Konformitätspaket für PRAIN.

## Voraussetzungen
- Python 3.10+
- `jsonschema`

## Reproduzierbarer Testlauf
```bash
python -m pip install jsonschema
python tests/validate_schemas.py
python -m unittest discover -s tests -v
```

Der Schema-Validator prüft alle JSON-Schemas gegen Draft 2020-12, validiert Datum-/Zeitformate
und führt die Testvektoren aus. Die Unit-Tests prüfen kleine Referenzmodelle für Architektur-
invarianten. Sie sind keine produktiven Runtime- oder Integrationstests.

## Lieferumfang
- Semantic core schemas und test vectors
- Architekturentscheidungen und Ontologie
- Conformance matrix
- Phase-1-Schnittstellenverträge
- Referenztests für Idempotenz, Versionkonflikte, deny-by-default, Redaction und Ledger-Prinzipien

## Phasenabgrenzung
Phase 0 ist die Definition/Abnahme der Verträge und Referenzsemantik.
Phase 1 implementiert und integriert Event Registry/Bus Adapter, Goal Registry,
State Store und Policy Gateway. Keine produktive Runtime wird hier behauptet.
