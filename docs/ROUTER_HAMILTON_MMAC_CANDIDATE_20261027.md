# Router, Hamilton und Multi-Model-Cluster: Architektur-Kandidat

**Status:** Technischer Vorschlag aus dem vom Projektverantwortlichen am 27.10.2026 eingebrachten Text. Kein beschlossener Ersatz für P/R/A/I/N, SCF, Policy Gateway oder die fünf festgelegten Themen Sinne/Gehirn/Seele/Wille/Körper; keine Phase-1-Abnahme.

## Einordnung in P.R.A.I.N.

- **Gateway/Policy:** authentisiert den Aufrufer, bestimmt Tenant, Datenklasse, Zweck, Budget und erlaubte Ausführungsorte. Es autorisiert jede externe Aktion getrennt. Kein Cache- oder Router-Pfad darf dies umgehen.
- **Semantischer Router:** wählt für einen konkreten Inferenzschritt aus erlaubten lokalen oder externen Modellkandidaten nach Aufgabe, Qualität, Latenz, Kosten und Datenklasse. Er protokolliert Signale, Regelversion, Auswahl und Fallback. Eine Router-Entscheidung ist keine Berechtigung zur Werkzeugausführung.
- **Apache Hamilton:** optionaler Ausführer für typisierte, azyklische und möglichst reine Transformationsschritte wie Kontextvorbereitung, Merkmalsextraktion oder Auswertung. Langlaufende Schleifen und Freigaben brauchen eine separate dauerhafte Zustandsmaschine; Apache Burr ist eine zu evaluierende Implementierungsoption, keine bereits bewiesene PRAIN-Abhängigkeit.
- **MMAC als Modellpool:** heterogene Inferenz-Endpunkte und Spezialmodelle hinter dem Router. Diese sind Ressourcen des einen PRAIN-Agenten, nicht automatisch fünf unabhängige Agenten oder zusätzliche Sinne. SCF übernimmt versionierte semantische Nachrichten und Konsistenz über Knoten hinweg.
- **Quantenadapter:** nur eine austauschbare spätere Compute-Schnittstelle. Der Name Hamilton ist keine Zusage physikalischer Hamiltonian-Simulation, eines QPU-Backends oder eines Vorteils.

## Sichere Ablaufgrenze

`Authentisierung → Policy/Datenklasse → zulässiger Cache-Lookup → semantische Route → DAG-Teilschritte → Modellpool → Verifikation → Policy für Realwirkung → persistente Quittung`.

Ein Cache-Hit ist nur zulässig, wenn Tenant, Principal-Sichtbarkeit, Berechtigung, Datenklasse, Prompt-/Kontext-/Modell-/Policy-Version und Gültigkeit zum Treffer passen. Personenbezogene, widerrufene, dynamische oder aktionsauslösende Antworten benötigen strenge Invalidierung oder bleiben ungecacht. Ein semantisch ähnlicher Prompt ist kein Beweis für dieselbe erlaubte Antwort. Caches dürfen weder neue Autorität erzeugen noch Tombstones umgehen.

## Rückwirkung auf Strict B

Für B01 neue Pflichten erst nach fachlicher Entscheidung aufnehmen; keine neuen Rollen für die fünf Themen aus diesem Text **ableiten**. Für B02 identische Versionen und Entscheidungen über mehrere Hosts prüfen. Für B03 Gateway-, Cache-, Router-, DAG- und Werkzeugpfade unter einer Autoritätsgrenze halten. Für B04 Cache, Embeddings, Logs und Router-Telemetrie in Retention/Löschpropagation aufnehmen. Für B05 SCF-Provenienz und Konflikte bei DAG-/Modell-Ergebnissen definieren. Für B06 Router-/Modellwechsel nicht als HAL-Selbstermächtigung zulassen.

## Evaluationskriterien statt übernommener Zahlen

Vor einer Produktentscheidung einen PRAIN-eigenen Vergleich gegen einen festen Single-Model-Baseline-Satz durchführen: Antwortqualität je Aufgabenklasse, Fehlrouten, Datenschutzverletzungen, p50/p95-Latenz, Gesamtkosten einschließlich Router/Cache/Mehrfachaufrufen, Ausfälle, Wiederholbarkeit und Audit-Belege. Die im eingebrachten Text genannten 45–85 % Kosten- und 47 % Latenzgewinne, „garantierte“ Compliance, nahtloser Fallback und QPU-Austausch sind nicht als PRAIN-Ergebnis belegt. Die Formeln im Text enthalten beschädigte Platzhalter und werden nicht als normative Optimierungsfunktion übernommen.

## Primärquellen für technische Prüfung

- Apache Hamilton: https://hamilton.apache.org/concepts/driver/ und https://hamilton.apache.org/how-tos/use-hamilton-for-lineage/
- Apache Burr: https://github.com/apache/burr/
- vLLM Semantic Router System Overview: https://github.com/vllm-project/semantic-router/blob/main/website/docs/overview/semantic-router-overview.md
- RouteLLM-Paper: https://arxiv.org/abs/2406.18665
- MMAC-Copilot-Paper: https://arxiv.org/abs/2404.18074 (eine konkrete Forschungsarchitektur, keine allgemeine Industriestandard-Definition von „MMAC“)
