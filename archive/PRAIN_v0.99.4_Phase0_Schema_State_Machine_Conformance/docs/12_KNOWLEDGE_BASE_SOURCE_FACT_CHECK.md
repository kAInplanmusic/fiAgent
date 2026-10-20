# 12. Knowledge-base source and claim fact-check (2026-10-20)

## Method and limits

All 19 registered URLs were checked against the official project/vendor page, official standard/specification page, or a primary paper record where possible. Each of the 20 KB claims now has a stable claim ID, claim-level source IDs, an epistemic status, a separate verification status, a scoped assessment note, a review timestamp, and a pointer to the machine-readable audit `audit/claim_source_audit.json`. Source list review is not a substitute for experimental replication or a full systematic literature review.

The old ResearchGate URL for the MCP tool-description paper did not identify the correct record; S10 is corrected to the primary arXiv record `https://arxiv.org/abs/2602.14878`. S13 uses the arXiv abstract URL because the HTML endpoint was not consistently available. S7 now points directly to the AWS AgentCore developer guide, and S17 points to the specific OWASP Agentic Security Initiative page rather than the generic OWASP homepage. S18 and S19 add the primary papers behind Mem0 and AIOS quantitative claims.

## Claim-level conclusions

| Claim ID | Disposition | Source scope / decision |
|---|---|---|
| brain:claim:1 | `inferred` / `not_applicable` | The three-layer pattern is a design synthesis across memory products/projects, not a universal industry standard or a direct proposition established by one source. |
| brain:claim:2 | `disputed` / `inconclusive` | The primary paper reports >90% token-cost savings in a specified LOCOMO/full-context comparison. “Universally” is unsupported; preserve the benchmark and baseline scope. |
| brain:claim:3 | `refuted` / `failed` | The cited A-MEM primary paper describes dynamically organized, Zettelkasten-inspired linked memories; it does not establish GRPO-based memory routing as A-MEM's core method. Do not conflate it with the separate steering/GRPO paper S13. |
| brain:claim:4 | `reported` / `inconclusive` | The survey covers memory mechanisms and evaluation challenges; the general caution is reasonable, but task success depends on benchmark/model/agent loop and the entry should not be read as a universal quantitative result. |
| body:claim:1 | `corroborated` / `passed` | Repository and primary paper establish AIOS as a research architecture for LLM-agent resources. This verifies existence/scope, not adoption or production maturity. |
| body:claim:2 | `disputed` / `inconclusive` | No evidence checked establishes universal adoption or a single universally adopted agent-OS standard. The cited project is one research architecture. |
| body:claim:3 | `reported` / `inconclusive` | The up-to-2.1× figure appears in the paper for particular experiments. Preserve “up to”, baseline, task and implementation context; do not promote it to a universal performance estimate. |
| body:claim:4 | `disputed` / `inconclusive` | Checked official vendor documentation does not establish a universal <100 ms memory-access guarantee. Cloud/runtime guarantees are product-, path-, region-, load- and configuration-specific. |
| senses:claim:1 | `verified` / `passed` | The official MCP specification describes standardized protocol interfaces for client/server interaction with tools and resources. Verification is limited to this scope; MCP itself does not certify the called tool as safe. |
| senses:claim:2 | `reported` / `inconclusive` | The primary 2026 study empirically examined 856 tools across 103 servers and found description-quality problems with measurable but mixed outcome effects. Keep the model/task/sample scope and trade-offs. |
| senses:claim:3 | `disputed` / `inconclusive` | Neither a protocol specification nor general security guidance supports the claim that MCP is universally and fully secure. Security depends on implementation, authorization, tool permissions and deployment. |
| senses:claim:4 | `inferred` / `not_applicable` | Architecture synthesis only: event-triggered perception is a common systems pattern. No specific external empirical source is asserted for this general design statement. |
| will:claim:1 | `corroborated` / `inconclusive` | Research supports goal drift as a studied failure mode in extended agent tasks; severity depends on task, model and scaffold. |
| will:claim:2 | `refuted` / `failed` | The cited study does not establish inevitable onset after 100,000 tokens; it reports nearly perfect adherence by its best-performing scaffolded model beyond 100,000 tokens in its hardest setting while still finding some drift across evaluated models. |
| will:claim:3 | `reported` / `inconclusive` | The 2026 preprint reports a steering agent improving performance/efficiency in information-seeking tasks. This is emerging research, not a universal or production-validated guarantee. |
| will:claim:4 | `unknown` / `inconclusive` | The checked sources do not establish that a binding/commitment split drives goal drift nearly to zero. No quantitative promise should be repeated without a named evaluation and baseline. |
| soul:claim:1 | `inferred` / `not_applicable` | Identity, scoped authorization and auditability are architectural control principles supported by the risk and trust standards landscape; exact mechanisms and assurance levels vary. |
| soul:claim:2 | `refuted` / `failed` | ERC-8004 is an agent discovery/trust-related standard proposal; it does not replace application-local authentication, authorization, tenant isolation or policy enforcement. |
| soul:claim:3 | `corroborated` / `passed` | Official x402 and AP2 project records establish these as real payment/protocol initiatives. This is not a claim of universal adoption, maturity or safety. |
| soul:claim:4 | `disputed` / `inconclusive` | A trusted execution environment can provide bounded isolation/attestation properties; it does not by itself make the whole agent, its inputs, tools, policies or external effects trustworthy. |

## High-impact corrections

1. **Mem0 token savings:** a primary paper reports >90% savings in a specific LOCOMO/full-context comparison; this does not support “universally saves >90%”. S18 is the primary paper and S1 is the vendor/project page.
2. **A-MEM vs. GRPO:** the A-MEM paper describes dynamic, Zettelkasten-inspired linking; GRPO belongs to a different line of research. Do not conflate S4 with the steering-agent paper S13.
3. **AIOS speedup:** the “up to 2.1×” figure belongs to the paper’s specified evaluation. It is not a benchmark-independent promise.
4. **Cloud latency/isolation:** no universal <100 ms guarantee was substantiated. AWS AgentCore behavior depends on compute mode and session setup; the EC2 Instances path does not automatically isolate agents sharing one instance.
5. **MCP security:** MCP standardizes interfaces. It is not a blanket security certification for tools, credentials, policies or deployments.
6. **Goal drift threshold:** the cited study contradicts a universal 100,000-token onset claim. Report findings only for the study’s tested models and settings.
7. **ERC-8004, x402 and AP2:** these are real standards/protocol initiatives, but they do not replace local authorization or prove universal adoption.
8. **TEE trust:** a trusted execution environment supplies bounded isolation/attestation properties; it does not certify the complete agent system and its external effects as trustworthy.

## Claim identifiers and interpretation

The KB keeps its original English claim, status prose and qualitative “High/Medium/Low” label for traceability. The new `legacy_confidence_scale` records that the old label is qualitative, not a calibrated probability. Machine-readable `epistemic_status` and `verification_status` are separate axes; `verified` is used only when a named source review was passed. Design-synthesis statements may legitimately have no external `sourceIds`, but explicitly identify `assessment_method=design_synthesis` and a documentation assessment reference.
