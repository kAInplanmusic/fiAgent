# P.R.A.I.N. — Organischer Agent (Architektur-SSOT-Ergänzung)

**Status:** Verbindliche Begriffszuordnung des Projektverantwortlichen; Architekturabsicht hinsichtlich ihrer technischen Umsetzung. Keine Behauptung über bereits implementierte oder gemessene Eigenschaften.
**Herkunft:** Architekturklärung vom 2026-10-26; Zeichnungen `IMG_7360.png` und `IMG_7346.jpeg`. Die folgende Buchstaben-/Themenzuordnung wurde am 2026-10-27 ausdrücklich als Text vom Projektverantwortlichen bestätigt.

## Leitidee

P.R.A.I.N. wird als **organischer Agent** verstanden: ein zusammenhängendes Agentensystem mit fünf komplementären Themen: Sinne, Gehirn, Seele, Wille und Körper. Der semantische Arbeits- und Koordinationskern gehört zum Gehirn; die fünf Themen greifen auf ein gemeinsames, nachvollziehbares Aufgabenverständnis zu. Das System soll dadurch komplexe und interdisziplinäre Aufgaben kohärent bearbeiten können.

Der Architekturwechsel lautet: **Funktionale Spezialisierung statt Aufteilung in voneinander unabhängige Spezialagenten.** Eine Fähigkeit kann intern modular oder durch getrennte Prozesse umgesetzt sein; sie wird dadurch nicht automatisch zu einem eigenständigen Agenten mit isoliertem Kontext, eigener Identität oder separater Entscheidungsautorität. Gemeinsamer Kontext bedeutet zugleich nicht, dass jede Komponente alle Daten sehen darf: Berechtigungen, Zweckbindung und Datenminimierung gelten weiterhin.

## Einordnung in das kanonische P/R/A/I/N-Modell

„Organischer Agent“ ist die übergreifende Systemmetapher. Die verbindliche Zuordnung belegt jedes Thema genau einmal:

| Buchstabe | Assoziation | Thema | Begründung des Projektverantwortlichen |
|---|---|---|---|
| P | Perception | Sinne | Wahrnehmung läuft über die Sinne |
| R | Reason | Gehirn | Vernunft/Denken sitzt im Gehirn |
| A | Anima | Seele | Anima = Seele/Hauch |
| I | Intention | Wille | Absicht/Wille |
| N | Nerve | Körper | Nerven gehören zum Körper/Nervensystem |

Die bestehenden technischen Verantwortlichkeiten werden diesen Themen zugeordnet:

- **P — Perception (Sinne):** Eingaben und Beobachtungen aufnehmen, normalisieren und Provenienz sowie Unsicherheit erhalten.
- **R — Reason (Gehirn):** Gemeinsames Interpretieren, Abwägen, Schlussfolgern und Planen im semantischen Kern.
- **A — Anima (Seele):** Ein explizites, prüfbares und versioniertes Selbstmodell sowie Kontinuität führen; dies behauptet kein Bewusstsein.
- **I — Intention (Wille):** Ziele, Prioritäten, Abhängigkeiten und Abnahmekriterien verwalten.
- **N — Nerve (Körper):** Autorisierte Aktionen über Fähigkeiten und Adapter ausführen.

Die Schreibweisen **PRaiN, pRain, prAin, praIn und praiN** ändern diese Buchstaben-/Themenzuordnung nicht. Ihre typografische Beziehung zu den fünf Themen ist nicht verbindlich spezifiziert.

## Hub, Koordination und Erweiterungen

Das zentrale Gehirn ist kein einzelnes Modell und kein allmächtiger Prozess, sondern der **logische gemeinsame Arbeits- und Koordinationskern**. Modellwahl und Werkzeugzugriff werden über austauschbare, policy-gesteuerte Router und Adapter vermittelt. Der Semantic Coordination Fabric (SCF) bleibt für semantische Nachrichten, Provenienz, Projektionen, Konflikterkennung, Abgleich und selektive Synchronisierung zuständig. Invariant & Evidence Layer sowie Policy Gateway behalten ihre unabhängigen Kontroll- und Nachweisfunktionen; die Homeostasis & Adaptation Layer (HAL) bleibt eine begrenzte Beobachtungs- und Anpassungsebene.

Ein technischer Kandidat für Router, Apache-Hamilton-DAGs und einen heterogenen Modellpool ist in `docs/ROUTER_HAMILTON_MMAC_CANDIDATE_20261027.md` abgegrenzt. Er definiert keine zusätzlichen fünf Sinnesmodule und ist nicht als bestehende Implementierung oder verbindliche Phase-1-Pflicht beschlossen.

Die frühere Aufzählung „UI, Analyst, Informant, Animateur, Renderer“ war eine unbelegte Assistenteninterpretation und ist kein Projektbeschluss. Die nun festgelegten fünf Themen dürfen durch solche Rollen nicht ersetzt werden.

## Grenzen der Aussage

- „Organisch“, „Gehirn“ und „Sinne“ sind Architekturmetaphern für integrierte Funktion und Koordination, keine Aussage über biologisches Leben, Empfindungsfähigkeit oder Bewusstsein.
- „Quantenbereit“ bezeichnet austauschbare Compute-/Provider-Schnittstellen. Es behauptet weder tatsächliche Quantenverarbeitung noch Quanten-Semantik im physikalischen Sinn oder einen Quantenvorteil.
- Ein gemeinsamer semantischer Arbeitsraum ist ein Architekturziel, keine Garantie für höhere Leistung. Skalierbarkeit, Latenz, Zuverlässigkeit, Kosten und Qualität müssen mit definierten Aufgaben und Vergleichsmessungen geprüft werden.
- Das zentrale Gehirn darf keine Sicherheitsgrenzen umgehen: Least privilege, deny-by-default, aktionsgebundene Freigaben, Provenienz, Versionierung und Evidenz bleiben verbindlich.

## Konsequenzen und offene Spezifikation

1. Architektur- und Produkttexte beschreiben P.R.A.I.N. als einen organischen Agenten mit Sinne/Gehirn/Seele/Wille/Körper, nicht als bloße Gruppe unabhängiger Spezialagenten.
2. Bestehende verteilte Prozesse und Spezialkomponenten bleiben als Implementierungsoption zulässig, sofern sie den gemeinsamen Systemkontext über definierte Verträge/SCF einbringen und keine unprotokollierte Nebenautorität erhalten.
3. Für jedes der fünf Themen sind die bestehenden Normpflichten, konkrete Komponentenverträge, Kontextzugriff, Provenienz, Fehlerverhalten, Berechtigungen und Abnahmetests abzugleichen. Die Themenzuordnung allein ist kein Implementierungsnachweis.
4. Zu definieren sind außerdem Kontext-/Speichermodell, Konfliktauflösung, Router-Verantwortung, gemeinsame Plan-/Gedächtnisgrenzen sowie Messkriterien für behauptete Effizienz- oder Qualitätsgewinne.
5. Diese SSOT-Ergänzung erweitert das bestehende Modell; sie hebt keine früheren Anforderungen stillschweigend auf und belegt keine Implementierung oder Produktionsreife.

## Entscheidungsstatus

**Festgehalten:** Der organische Agent mit P = Sinne, R = Gehirn, A = Seele, I = Wille und N = Körper ist die beabsichtigte konzeptionelle Leitidee.
**Noch offen:** typografische Bedeutung der fünf gemischten Schreibweisen, konkrete Komponentenverträge, Hub-/SCF-Grenzen und messbare Vergleichs- bzw. Abnahmekriterien.
**Nicht behauptet:** Quantenhardware, Bewusstsein, garantierter Leistungsvorsprung oder vollständige Implementierung.
