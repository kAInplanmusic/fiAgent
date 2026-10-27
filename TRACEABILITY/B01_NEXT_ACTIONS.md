# B01: Prüfergebnis und nächste Abnahmehandlungen

`python3 TRACEABILITY/verify_b01_evidence.py --output TRACEABILITY/B01_verification.json`
prüft die Vollständigkeit der 5.002 historischen IDs, die 69 fokalen IDs und
die SHA-256-Bindung bereits genannter Code- und Testdateien. Die Prüfung
bewertet **keine** fachliche Normgeltung und bescheinigt **keine** Implementierung.

Der Bericht weist 2.554 RETAIN, 70 EXTEND, 47 SUPERSEDE und 2.331
NON_NORMATIVE aus. 651 Umsetzungen sind OPEN, 2.061 PARTIAL und 2.290
NOT_APPLICABLE. 41 als NON_NORMATIVE eingestufte Zeilen haben trotzdem einen
PARTIAL-Implementierungsstatus; diese Kontextabhängigkeit muss ein unabhängiger
Fachprüfer je betroffener Verpflichtung beurteilen.

Für die Abschlussabnahme sind in dieser Reihenfolge nötig:

Nachprüfung 2026-10-27: `python3 TRACEABILITY/verify_focal_evidence.py` prüft
zusätzlich die 69 fokalen Zeilen gegen die aktuelle Quellenauflösung und ihre
konkreten Code-/Test-Hashes. Sie bestätigt 56 offene, zwölf behauptet
abgeschlossene und einen historischen Eintrag; die genaue Ergebnisdatei ist
`B01_FOCAL_AUDIT_20261027.json`. 55 Zeilen haben veraltete Anker, alle 68
Arbeitspakete haben weder importierte Verhaltenstests noch unabhängige
Freigaben. Der Validator meldet daher einen Fehler und setzt keine Freigabe.

1. Historische Anker wurden auf den damaligen Stand neu gebunden; fokale Anker
   müssen nun gesondert inhaltlich neu geprüft und nachvollziehbar aktualisiert
   werden. Eine neue Hash-Angabe ersetzt keinen Verhaltensnachweis oder eine
   Normentscheidung.
2. Die 69 fokalen Einträge, darunter die ursprünglich als offen oder erledigt
   markierten Roadmap-Arbeiten, einzeln mit gültigem Normtext, konkretem
   Codeverhalten, bestandenem Negativ-/Positivtest und offener Restlücke
   abgleichen. Historische Häkchen sind keine Abnahme.
3. Die gültigen Verpflichtungen der 5.002 historischen Kandidaten unabhängig
   semantisch bestätigen. Nicht normative und ersetzte Zeilen brauchen ebenso
   belegte Nachfolger bzw. Gründe, damit keine Pflicht verloren geht.
4. Einen unabhängigen Prüfer samt Prüfbericht und Freigabe-ID erfassen, erst
   wenn alle Pflichtnachweise vollständig sind. Bis dahin B01 und Strict B
   offen lassen.
