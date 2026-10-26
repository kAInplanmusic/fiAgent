# P.R.A.I.N. — Organischer Agent (Architektur-SSOT-Ergänzung)

**Status:** Architekturabsicht, in das bestehende kanonische Modell einzuordnen; keine Behauptung über bereits implementierte oder gemessene Eigenschaften.  
**Herkunft:** Projektverantwortlicher, Architekturklärung vom 2026-10-26; Zeichnungen `IMG_7360.png` und `IMG_7346.jpeg`.

## Leitidee

P.R.A.I.N. wird als **organischer Agent** verstanden: ein zusammenhängendes Agentensystem mit einem zentralen semantischen Arbeits- und Koordinationskern („Gehirn“) und mehreren funktionalen „Sinnen“ bzw. Zusatzkomponenten. Diese Komponenten tragen unterschiedliche Perspektiven und Fähigkeiten bei, greifen aber auf ein gemeinsames, nachvollziehbares Aufgabenverständnis zu. Das System soll dadurch komplexe und interdisziplinäre Aufgaben kohärent bearbeiten können.

Der Architekturwechsel lautet: **Funktionale Spezialisierung statt Aufteilung in voneinander unabhängige Spezialagenten.** Eine Fähigkeit kann intern modular oder durch getrennte Prozesse umgesetzt sein; sie wird dadurch nicht automatisch zu einem eigenständigen Agenten mit isoliertem Kontext, eigener Identität oder separater Entscheidungsautorität. Gemeinsamer Kontext bedeutet zugleich nicht, dass jede Komponente alle Daten sehen darf: Berechtigungen, Zweckbindung und Datenminimierung gelten weiterhin.

## Einordnung in das kanonische P/R/A/I/N-Modell

„Organischer Agent“ ist die übergreifende Systemmetapher und verändert die bestehenden P/R/A/I/N-Verantwortlichkeiten nicht:

- **P — Perception:** Eingaben und Beobachtungen aufnehmen, normalisieren und Provenienz sowie Unsicherheit erhalten.
- **R — Reason:** Gemeinsames Interpretieren, Abwägen, Schlussfolgern und Planen im semantischen Kern.
- **A — Anima:** Ein explizites, prüfbares und versioniertes Selbstmodell sowie Kontinuität führen; dies behauptet kein Bewusstsein.
- **I — Intention:** Ziele, Prioritäten, Abhängigkeiten und Abnahmekriterien verwalten.
- **N — Nerve:** Autorisierte Aktionen über Fähigkeiten und Adapter ausführen.

Die vom Projektverantwortlichen verwendeten Schreibweisen **PRaiN, pRain, prAin, praIn und praiN** bezeichnen fünf funktionale Sinnes-/Zusatzkomponenten des Systems. Ihre endgültige Zuordnung, Namen und Verträge sind noch zu spezifizieren; die Schreibvarianten allein legen keine zusätzlichen Agenten, Identitäten oder Sicherheitsdomänen fest. Die bereits kanonischen P/R/A/I/N-Buchstaben behalten bis zu einer dokumentierten Entscheidung ihre oben definierte Bedeutung.

## Hub, Koordination und Erweiterungen

Das zentrale Gehirn ist kein einzelnes Modell und kein allmächtiger Prozess, sondern der **logische gemeinsame Arbeits- und Koordinationskern**. Modellwahl und Werkzeugzugriff werden über austauschbare, policy-gesteuerte Router und Adapter vermittelt. Der Semantic Coordination Fabric (SCF) bleibt für semantische Nachrichten, Provenienz, Projektionen, Konflikterkennung, Abgleich und selektive Synchronisierung zuständig. Invariant & Evidence Layer sowie Policy Gateway behalten ihre unabhängigen Kontroll- und Nachweisfunktionen; die Homeostasis & Adaptation Layer (HAL) bleibt eine begrenzte Beobachtungs- und Anpassungsebene.

Die gezeichneten Rollen wie UI, Analyst, Informant, Animateur und Renderer sind mögliche Ein-/Ausgabe- oder Fähigkeitsmodule, keine bereits verbindlich festgelegten fünf Sinne. Ihre Zuständigkeiten, Datenflüsse und Schnittstellen werden erst durch eigene Verträge normativ.

## Grenzen der Aussage

- „Organisch“, „Gehirn“ und „Sinne“ sind Architekturmetaphern für integrierte Funktion und Koordination, keine Aussage über biologisches Leben, Empfindungsfähigkeit oder Bewusstsein.
- „Quantenbereit“ bezeichnet austauschbare Compute-/Provider-Schnittstellen. Es behauptet weder tatsächliche Quantenverarbeitung noch Quanten-Semantik im physikalischen Sinn oder einen Quantenvorteil.
- Ein gemeinsamer semantischer Arbeitsraum ist ein Architekturziel, keine Garantie für höhere Leistung. Skalierbarkeit, Latenz, Zuverlässigkeit, Kosten und Qualität müssen mit definierten Aufgaben und Vergleichsmessungen geprüft werden.
- Das zentrale Gehirn darf keine Sicherheitsgrenzen umgehen: Least privilege, deny-by-default, aktionsgebundene Freigaben, Provenienz, Versionierung und Evidenz bleiben verbindlich.

## Konsequenzen und offene Spezifikation

1. Architektur- und Produkttexte beschreiben P.R.A.I.N. als einen organischen Agenten mit funktionalen Sinnen, nicht als bloße Gruppe unabhängiger Spezialagenten.
2. Bestehende verteilte Prozesse und Spezialkomponenten bleiben als Implementierungsoption zulässig, sofern sie den gemeinsamen Systemkontext über definierte Verträge/SCF einbringen und keine unprotokollierte Nebenautorität erhalten.
3. Für jede der fünf Sinnes-/Zusatzkomponenten sind Zweck, Ein-/Ausgaben, Kontextzugriff, Provenienz, Fehlerverhalten, Berechtigungen und Abnahmetests festzulegen.
4. Zu definieren sind außerdem Kontext-/Speichermodell, Konfliktauflösung, Router-Verantwortung, gemeinsame Plan-/Gedächtnisgrenzen sowie Messkriterien für behauptete Effizienz- oder Qualitätsgewinne.
5. Diese SSOT-Ergänzung erweitert das bestehende Modell; sie hebt keine früheren Anforderungen stillschweigend auf und belegt keine Implementierung oder Produktionsreife.

## Entscheidungsstatus

**Festgehalten:** Der organische Agent mit gemeinsamem Gehirn und funktionalen Sinnen ist die beabsichtigte konzeptionelle Leitidee.  
**Noch offen:** finale Benennung und Zuordnung der fünf Schreibweisen, konkrete Komponentenverträge, Hub-/SCF-Grenzen und messbare Vergleichs- bzw. Abnahmekriterien.  
**Nicht behauptet:** Quantenhardware, Bewusstsein, garantierter Leistungsvorsprung oder vollständige Implementierung.
