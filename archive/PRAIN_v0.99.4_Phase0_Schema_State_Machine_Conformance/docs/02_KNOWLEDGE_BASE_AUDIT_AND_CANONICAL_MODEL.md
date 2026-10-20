# 2. Knowledge-base parity, item audit and canonical model

## 2.1 Reproduced parity result

The original embedded `const DB` object was extracted from the original HTML and parsed as JSON. Recursive object/list/value comparison with `PRAIN_Wissensdatenbank.json` produced **zero differences**. Counts in the original data are: 5 dimensions, 20 claims, 50 key concepts, 17 sources, 8 relations, 3 cross-cutting records, 7 priority entries. Dimension source references were all resolvable; relation endpoints were valid; source IDs were unique.

This result proves data parity only. It does not verify whether each source is current, whether every claim is well supported, whether the HTML rendering logic is security-reviewed, or whether the relationships reflect the normative architecture.

## 2.2 Authoritative data rule

`knowledge_base/PRAIN_Wissensdatenbank.v0.3.0.json` is the source of truth. The HTML is a presentation/export view. Changes are made in JSON first, then embedded/generated into HTML, and the parity validator must pass before publication. The UI must never have an independent editable data store that silently diverges.

## 2.3 Item-level disposition

- **Project record:** retains ID `PRAIN`, increments KB version to 0.2.0, removes the dependency framing “initially grounded ... for Hallerbans” and describes an independent semantic control plane. Hallerbans is a consumer, not a foundational dependency.
- **Five dimensions:** preserve legacy IDs (`senses`, `brain`, `soul`, `will`, `body`) for compatibility while adding canonical labels P/Perception, R/Reason, A/Anima, I/Intention, N/Nerve. The five dimensions are logical responsibilities; they need not be five processes or agents.
- **20 claim records:** preserved verbatim as evidence-aware source claims and cautions. Their statuses are not elevated solely because the KB was curated. Each remains subject to source-level review and update.
- **50 key concepts:** preserved. Concepts are tags, not claims and not authority grants.
- **17 source records:** preserved with IDs/URLs/notes. This pass verifies non-empty source IDs and referential integrity, not external liveness/currentness.
- **8 legacy relations:** retained with amended semantics where they could imply direct authorization or uncontrolled state persistence. One additional observation-to-goal-evaluation relation is added.
- **3 cross-cutting records:** security/evidence wording is tightened so authorization and source quality are not assigned to a single P/R/A/I/N dimension.
- **7 priorities:** preserved as prioritization advice, not as implementation commitments or security policy.
- **HTML interaction:** embedded DB replaced with canonical v0.3.0 data; Hallerbans-specific UI wording replaced with general implementation notes; legacy node IDs retained so graph coordinates/filter behavior do not break.

## 2.4 Corrected relationship rules

- I may propose or revise goals/plans; a separate policy gateway authorizes action.
- A represents inspectable self-model and lineage; A cannot grant permission or override policy.
- Security is a cross-cutting governance control; no dimension “owns” all security.
- N executes authorized commands and emits receipts; it does not make an execution successful merely by returning a textual completion claim.
- R may reason over and store verified experience; authoritative storage semantics determine which state is committed.
- Observation feeds interpretation, but observation of a source is not identical to truth of the source's proposition.

## 2.5 Claim/source quality limitations

Claims may be stale, scoped, experimental, vendor-authored or wrong. Source types must distinguish primary research, official documentation, repository, secondary commentary and local observation. Numerical claims must carry measurement scope, benchmark, version/date and reproducible context before they can be used as quantitative requirements. The source audit does not certify the live internet content of the 17 URLs.
