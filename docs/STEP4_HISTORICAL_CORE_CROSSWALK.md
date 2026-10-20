# Schritt 4 – Semantischer Crosswalk historischer Kernanforderungen

**Prüfumfang:** 19 gezielt ausgewählte Kernanforderungen aus v0.4.0 (Architektur), v0.5.0 (Distributed Protocol) und v0.6.0 (Multiscale Semantic Coordination), abgeglichen mit dem kanonischen v0.99.4-Spezifikationspaket und dem v1.1.0-Referenzprototyp.

**Wichtig:** Das ist eine fachlich geprüfte Stichprobe, keine vollständige Prüfung aller 5.071 Extraktionskandidaten. Die Kandidatenmatrix bleibt offen; diese Datei ist eine separate, kuratierte Crosswalk-Tabelle.

## Statuszählung

- `DOCUMENTATION_GUARD`: 1
- `OPEN_RUNTIME_GAP`: 2
- `PARTIAL_IMPLEMENTATION`: 11
- `PROTOTYPE_TESTED`: 1
- `SPEC_AND_SCHEMA_ONLY`: 1
- `SPEC_CONFIRMED_IMPLEMENTATION_PARTIAL`: 1
- `SPEC_ONLY`: 1
- `SPEC_ONLY_FOR_REAL_EFFECTS`: 1


## Konkrete Erkenntnisse

1. **Architektur und Laufzeit sind strikt getrennt.** v0.4–v0.6 sind Spezifikationspakete, keine Deployment-Nachweise. Der v1.1.0-Prototyp ist lokal und in-memory.
2. **Evidenzbasierter Zielabschluss ist im Prototyp testbar umgesetzt.** Die Tests verlangen explizite Verifikation und Evidenzreferenzen; das beweist keine Persistenz oder Produktionsreife.
3. **Policy-Gateway und lokale CAS-Logik haben positive Tests.** Das deckt nicht die Authentizität und atomare Einmalverwendung von Freigaben sowie keine verteilte Konsistenz ab.
4. **Event-Deduplizierung ist nur pro Prozess/Consumer belegt.** Durable broker semantics, retries/dead letters und Recovery nach Absturz fehlen.
5. **HAL, Multiscale-Koordination, Worker-Leases/Fencing und Freshness von Projektionen sind in der geprüften v1.1.0-Laufzeit nicht nachgewiesen.** Sie bleiben Spezifikationsziele oder offene Laufzeitlücken.
6. **Quantenbezug bleibt eine Schnittstellen- und Austauschbarkeits-Aussage.** Aus den geprüften Artefakten folgt kein quantenmechanischer Vorteil.

## Verifizierter Testlauf

`python -m unittest discover -s tests -v` im entpackten v1.1.0-Prototyp: **23 Tests bestanden**. Das widerspricht der Angabe „22 tests passed“ in `docs/PHASE1_IMPLEMENTATION_STATUS.md`. Der Statusbericht ist deshalb als veraltet/inkonsistent zu kennzeichnen, nicht stillschweigend umzuschreiben.

## Nächste Schritte

1. Alle kanonischen Invarianten aus `v0.99.4/tests/invariants.json` und den Normativ-Dokumenten mit konkreten Laufzeitstellen und Testnamen verbinden.
2. Negative Tests ergänzen: Approval expired/consumed/revoked, payload digest mismatch, missing capability, unknown outcome, duplicate events, stale CAS, mutation aliasing.
3. Laufzeitvalidierung gegen kanonische JSON Schemas nachweisen, nicht nur Schema-Dateien und separate Validatoren zählen.
4. Danach historische Kandidaten einzeln klassifizieren: `NORMATIVE`, `DECISION`, `SCHEMA_FIELD`, `TEST_CRITERION`, `STATUS_CLAIM`, `DUPLICATE`, `SUPERSEDED`, `NON_NORMATIVE`.
5. Keine Anforderung als `PASS` markieren, solange ein konkreter Test oder prüfbarer Beleg fehlt.
