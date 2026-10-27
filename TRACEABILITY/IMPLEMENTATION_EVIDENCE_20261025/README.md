# PRAIN implementation evidence checkpoint

This is an auditable partial checkpoint. It is not a production release approval.

Rebuild from the repository root: `python3 tools/verify_implementation_evidence.py`.
Exit zero means every one of the 5,071 candidate IDs resolves to the exact recorded source line. It does not mean all requirements are implemented or accepted.

All code/test anchors are AST-located with current file SHA-256 values. Test existence is not a passing test result. Rebuild after source changes to avoid stale anchors.

Current specification comparison binds archive/PRAIN_v0.99.6_Phase0_Green_Closure.zip by SHA-256 and compares whole-file bytes or exact lines. Exact text in a changed document cannot resolve normative context, migration semantics or supersession.

The 1,825 JSON-derived candidates include exact JSON pointer/range/hash metadata. Structural keywords and annotations are distinguished as source context only.

The 5,002 historical candidates remain unadjudicated at the effective-version/normative level. Their source identity, duplicate group and canonical compatibility are verified. No obligation has been closed by reclassification.

## Focal obligation assessment

| Requirement | Source | Code paths | Test anchors | Remaining scope |
|---|---|---:|---:|---|
| RTM-00001 | ROADMAP.md:36 | 4 | 6 | Inventory is available; completeness against every historical release must be established, not inferred from a checkbox. |
| RTM-00002 | ROADMAP.md:37 | 4 | 6 | Historical artifacts remain in archive; source hashes bind this run, but do not establish absence of prior overwrites. |
| RTM-00003 | ROADMAP.md:38 | 4 | 6 | Per-source checksums exist; purpose, version and canonical successor coverage remains incomplete. |
| RTM-00004 | ROADMAP.md:39 | 4 | 6 | Supplied archive CRC/hash evidence exists; all master-history archive membership requires separate package checks. |
| RTM-00005 | ROADMAP.md:40 | 4 | 6 | Original clauses and candidates preserved; complete semantic migration decisions remain unresolved. |
| RTM-00006 | ROADMAP.md:47 | 3 | 4 | P/R/A/I/N roles are specified; documented architecture does not prove full runtime implementation. |
| RTM-00007 | ROADMAP.md:48 | 3 | 4 | SCF/HAL/invariant layers specified; runtime implements bounded local subsets. |
| RTM-00008 | ROADMAP.md:49 | 3 | 4 | Audit documents are archival evidence, not runtime verification of their conclusions. |
| RTM-00009 | ROADMAP.md:50 | 3 | 4 | State-machine and schema crosswalk exists; exhaustive runtime-transition conformance remains missing. |
| RTM-00010 | ROADMAP.md:51 | 4 | 6 | RTM exists and preserves IDs; incomplete normative/implementation evidence prevents closure. |
| RTM-00011 | ROADMAP.md:52 | 4 | 6 | This verifier checks source and AST anchors; all cross-document IDs/semantic links are broader than this check. |
| RTM-00012 | ROADMAP.md:53 | 4 | 6 | Exact duplicate groups preserve lineage; duplicate text does not resolve contradictory normative contexts. |
| RTM-00013 | ROADMAP.md:54 | 4 | 6 | Current strict gate file rejects acceptance; historical status labels are not uniformly reconciled. |
| RTM-00014 | ROADMAP.md:61 | 4 | 6 | Historical v1.1.0 test-count claim requires execution of that archived build, not current suite count. |
| RTM-00015 | ROADMAP.md:62 | 4 | 6 | 310/319/325 count claims require suite/version/run identities; current tests cannot substantiate them. |
| RTM-00016 | ROADMAP.md:63 | 4 | 6 | Existing release verifier binds prototype; all historical integrity claims need archive-by-archive verification. |
| RTM-00017 | ROADMAP.md:64 | 4 | 6 | Master/prototype manifests exist; pending changed tree requires regenerated current manifest. |
| RTM-00018 | ROADMAP.md:65 | 4 | 6 | Current verifier supports integrity checks; reproducible clean package and CI equivalence need run evidence. |
| RTM-00019 | ROADMAP.md:66 | 4 | 6 | This report separates anchors and execution; no production pass is granted. |
| RTM-00020 | ROADMAP.md:73 | 4 | 52 | Vertical runtime path emits evidence and simulated receipts; does not prove actual external effect. |
| RTM-00021 | ROADMAP.md:74 | 4 | 52 | Reference state/goal/policy/ledger components and tests exist; limited prototype scope retained. |
| RTM-00022 | ROADMAP.md:75 | 4 | 52 | Historical 23-test result is not replaced with current test count; historical rerun still needed. |
| RTM-00023 | ROADMAP.md:76 | 2 | 22 | SCF ingress validates a local v1 claim subset; complete canonical Phase0 model enforcement remains missing. |
| RTM-00024 | ROADMAP.md:77 | 2 | 22 | Negative schema tests exist for SCF/wire; all canonical families/round-trip/migrations remain incomplete. |
| RTM-00025 | ROADMAP.md:78 | 4 | 52 | Local state/goal/CAS checks exist; normative automata/property/mutation coverage is incomplete. |
| RTM-00026 | ROADMAP.md:79 | 4 | 52 | Targeted auth/approval/idempotency/unknown tests exist; combined distributed race coverage remains partial. |
| RTM-00027 | ROADMAP.md:80 | 4 | 52 | Detached ledger payload tests verify aliases; independent anchors and archival mutation proof still separate. |
| RTM-00028 | ROADMAP.md:81 | 4 | 52 | Criterion-specific checks and atomic secure completion exist; issuer authentication/production integration separate. |
| RTM-00029 | ROADMAP.md:88 | 0 | 0 | Python baseline described; supported-version matrix and reproducible environment require run evidence. |
| RTM-00030 | ROADMAP.md:89 | 5 | 50 | SQLite persistence implemented; stable versioned storage interface and full migrations not established. |
| RTM-00031 | ROADMAP.md:90 | 5 | 50 | Crash/restart tests exercise persisted components; production outage and recovery objectives remain separate. |
| RTM-00032 | ROADMAP.md:91 | 5 | 50 | Local durable outbox/inbox and unknown-state handling exist; full DLQ/broker retry system not established. |
| RTM-00033 | ROADMAP.md:92 | 5 | 50 | Durable UNKNOWN plus evidence-required reconciliation tested; reconciliation truth depends on trusted evidence. |
| RTM-00034 | ROADMAP.md:93 | 5 | 50 | Single-use admission is atomic locally; full authenticated approval issuer/provenance model incomplete. |
| RTM-00035 | ROADMAP.md:94 | 5 | 50 | Backup/restore and projection retention tests exist; global deletion and migration rollback coverage incomplete. |
| RTM-00036 | ROADMAP.md:101 | 4 | 30 | HTTP adapter exists; interchangeable transport interface and alternative implementation contract suite incomplete. |
| RTM-00037 | ROADMAP.md:102 | 0 | 0 | SQLite is implemented; PostgreSQL remains a candidate rather than a claimed tested backend. |
| RTM-00038 | ROADMAP.md:103 | 5 | 50 | Durable leases/fencing/inbox/outbox exist; actual protected external-adapter fencing and conflict resolution incomplete. |
| RTM-00039 | ROADMAP.md:104 | 5 | 50 | State CAS and scoped projections exist; distributed authoritative/projection consistency needs integration proof. |
| RTM-00040 | ROADMAP.md:105 | 4 | 30 | Spawned TLS-node fault tests add process isolation; split-brain, reorder and real two-host suite incomplete. |
| RTM-00041 | ROADMAP.md:106 | 4 | 30 | SCF retains provenance/conflicts/dependencies; L0-L3 selective sync and canonical graph incomplete. |
| RTM-00042 | ROADMAP.md:107 | 4 | 30 | Durable-state/process tests exist; two real hosts remain an operational prerequisite. |
| RTM-00043 | ROADMAP.md:114 | 4 | 35 | Tenant access and authenticated action entry exist; all mutation/admin paths not yet verified. |
| RTM-00044 | ROADMAP.md:115 | 4 | 35 | Approval checks bind selected fields; full issuer/nonce/principal/context binding incomplete. |
| RTM-00045 | ROADMAP.md:116 | 4 | 35 | Local admission transaction exists; revoke-versus-external-effect distributed atomicity not proven. |
| RTM-00046 | ROADMAP.md:117 | 1 | 11 | Projection classification/retention/tombstone controls exist; originals/logs/embeddings/caches lack end-to-end enforcement. |
| RTM-00047 | ROADMAP.md:118 | 1 | 11 | Nested projection secret rejection exists; entire logs/events/receipt/ledger pipeline remains unverified. |
| RTM-00048 | ROADMAP.md:119 | 0 | 0 | Threat boundaries specified historically; current independent technical review and abuse cases required. |
| RTM-00049 | ROADMAP.md:120 | 4 | 52 | Runtime simulates effects; a successful receipt is not proof of external execution or deployment authorization. |
| RTM-00050 | ROADMAP.md:127 | 0 | 0 | Correlation evidence exists locally; privacy-aware structured metrics/log export incomplete. |
| RTM-00051 | ROADMAP.md:128 | 2 | 11 | HAL health states and stale/unknown tested; deployment telemetry freshness/SLO scope remains partial. |
| RTM-00052 | ROADMAP.md:129 | 2 | 11 | HAL proposals do not self-execute; actual authorized canary/repair/rollback workflow incomplete. |
| RTM-00053 | ROADMAP.md:130 | 2 | 11 | Budget/cooldown proposal bounds exist; end-to-end adaptation rollback and high-risk approvals not implemented. |
| RTM-00054 | ROADMAP.md:131 | 2 | 11 | Durable budget/cooldown exists; operator stop/dashboard/alerts and measured failure budget incomplete. |
| RTM-00055 | ROADMAP.md:138 | 1 | 6 | SemanticRouter backend metadata exists; all versioned provider/compute capabilities interfaces incomplete. |
| RTM-00056 | ROADMAP.md:139 | 1 | 6 | Routing contract tests exist; two implementations per adapter family not proven. |
| RTM-00057 | ROADMAP.md:140 | 1 | 6 | Routing constraints tested; provider migration preserving semantic/evidence contracts needs full contract suite. |
| RTM-00058 | ROADMAP.md:141 | 0 | 0 | Quantum-ready remains replaceable-interface intent; simulator/adapter suite not established. |
| RTM-00059 | ROADMAP.md:142 | 0 | 0 | No measured quantum advantage is claimed by this assessment; positive provider requirements still open. |
| RTM-00060 | ROADMAP.md:149 | 4 | 30 | Security/privacy/network-process/fault tests present; load/chaos/real-two-host full coverage missing. |
| RTM-00061 | ROADMAP.md:150 | 0 | 0 | Failure/recovery specification exists; executable deployment/operator runbooks not fully verified. |
| RTM-00062 | ROADMAP.md:151 | 1 | 6 | Resource routing and retry limits partial; measured SLO/alert/incident/cost-control operations incomplete. |
| RTM-00063 | ROADMAP.md:152 | 0 | 0 | Independent agent technical review can supply evidence; qualified external/owner review not fabricated. |
| RTM-00064 | ROADMAP.md:153 | 4 | 6 | Source/anchor hashes generated; final reproducible RC build remains separate required evidence. |
| RTM-00065 | ROADMAP.md:154 | 0 | 0 | Explicit human production acceptance is external; user request to implement does not impersonate release signature. |
| RTM-00066 | ROADMAP.md:162 | 4 | 6 | Historical count discrepancy preserved; current run does not retroactively rerun that build. |
| RTM-00067 | ROADMAP.md:164 | 4 | 6 | Strict gate remains not accepted; complete historical-status reconciliation still needed. |
| RTM-00068 | ROADMAP.md:165 | 4 | 6 | Full candidate inventory exists; extraction/source verification does not complete individual normative acceptance. |
| RTM-00069 | MASTER_README.md:40 | 0 | 0 | Version-description table row is historical information, not a runtime obligation. |

## Machine-readable outputs

- `requirement_evidence.jsonl`: every ID and exact source/code/test anchors; no omitted historical candidates.
- `anchor_index.json`: deduplicated AST/document anchors with content hashes.
- `missing_proof.json`: per-ID proof still required.
- `verification_summary.json`: counts, source hashes and explicit acceptance limits.

Production remains blocked by complete canonical schema/graph/migrations, authenticated mutation/admin boundaries, raw/derived/backup end-to-end deletion, distributed external-adapter fencing and policy races, actual two-host operations, HAL canary/rollback, adapter interchangeability, deployment/SLO evidence and authorized final signoff.
