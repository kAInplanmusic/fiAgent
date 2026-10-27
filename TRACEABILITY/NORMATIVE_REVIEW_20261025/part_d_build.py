"""Reproduce Part D's document/section adjudication. No runtime acceptance is granted.

Document profiles below are curated semantic judgments after reading the source
families. Syntax determines only locator role; it never grants conformance.
"""
import collections, hashlib, importlib.util, json, re, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('ev', ROOT/'tools/verify_implementation_evidence.py')
ev=importlib.util.module_from_spec(sp);sp.loader.exec_module(ev)
ARCHIVE='archive/PRAIN_v0.99.6_Phase0_Green_Closure.zip'
CANON=zipfile.ZipFile(ROOT/ARCHIVE)
ARCHIVE_HASH=hashlib.sha256((ROOT/ARCHIVE).read_bytes()).hexdigest()
P={
'privacy': ('06_EVIDENCE_PRIVACY_AND_DATA_LIFECYCLE.md',1,'Retain per-class classification, attributable downgrade review, separate evidence/content, purpose-scoped signing keys, lawful retention, tenant-authenticated deletion, per-store propagation and restore-before-serve tombstones. Hash integrity does not establish source truth or lawful retention.', ['prototype/prain/private_projections.py','prototype/prain/evidence_ledger.py','prototype/prain/backup_bundle.py'], ['prototype/tests/test_production_privacy.py','prototype/tests/test_backup_bundle.py'], 'Projection-table retention and explicit tombstone application cover a subset. Raw events/evidence content, derived indexes/exports/replicas, automatic restore serving barrier, complete key erasure/KMS and per-target deletion receipts remain unproved.'),
'hal': ('07_HAL_RESILIENCE_AND_CONFORMANCE.md',1,'Retain HAL as supervisory and non-authorizing. A bounded catalogue, fresh signal, current independent policy, canary metrics, rollback and independent outcome evidence are required; local healthy/unknown state is not permission.', ['prototype/prain/anima_hal.py','prototype/prain/durable_hal_proposals.py','prototype/prain/hal_proposals.py'], ['prototype/tests/test_anima_hal_contract.py','prototype/tests/test_durable_hal_proposals.py'], 'Observe-only/budget/cooldown subset exists. Authorized canary/rollback execution, distributed intervention/stop and per-deployment numeric SLO evidence remain unproved.'),
'policy': ('05_POLICY_APPROVAL_AND_REVOCATION.md',1,'Retain independent deny/defer policy authorization and exact actor/tenant/action/target/effect/context binding. Approval lifecycle/use counters and current identity/revocation checks are separate from action digest semantics.', ['prototype/prain/policy_gateway.py','prototype/prain/runtime.py','prototype/prain/durable_admission.py','prototype/prain/tenant_access.py'], ['prototype/tests/test_production_runtime_auth.py','prototype/tests/test_runtime_hardening.py','prototype/tests/test_durable_admission.py'], 'Default-deny authenticated admission and local single-use handling are partial. Complete canonical fields, authenticated approver/issuer/KMS and linearizable cross-system revocation at actual external effects remain unproved.'),
'identity': ('04_IDENTITY_TENANCY_AND_AUTHORITY.md',1,'Retain explicit principal/tenant/authority identity and version lineage; delegation narrows authority, revocation is monotonic, CAS protects mutable heads, and derived projections cannot replace authority.', ['prototype/prain/tenant_access.py','prototype/prain/durable_state_store.py','prototype/prain/fenced_leases.py'], ['prototype/tests/test_tenant_privacy.py','prototype/tests/test_durable_state_store.py','prototype/tests/test_fencing_hal_proposals.py'], 'Local grants/rotation/revocation/CAS/fencing exist. Full canonical principal/tenant/delegation state lifecycle and protected remote-adapter fencing are not demonstrated.'),
'claim': ('03_CLAIM_ONTOLOGY_AND_LIFECYCLE.md',1,'Retain independent epistemic, verification, confidence, validity and lifecycle axes; verified/refuted transitions need named evidence procedures, immutable revisions, provenance and counterevidence. Confidence and exception references cannot create verification or permission.', ['prototype/prain/scf.py','prototype/prain/scf_contract.py','prototype/prain/durable_semantics.py'], ['prototype/tests/test_scf_contract.py','prototype/tests/test_durable_semantics.py'], 'Local SCF validates a reduced claim contract and persists decisions/conflicts. Complete canonical claim entity/transition event/migration/graph semantics and every guarded transition remain unproved.'),
'migration': ('01_SCHEMA_AND_MIGRATION_POLICY.md',1,'Retain registry-bound Draft2020-12 contracts, strict unknown-field treatment, negotiated versions and named instance migrations. A file rename/string rewrite or schema enum is not an authorized semantic transition.', ['prototype/prain/scf_contract.py','prototype/prain/scf_wire.py'], ['prototype/tests/test_scf_contract.py','prototype/tests/test_scf_wire.py'], 'Executable named migration records/fixtures, loss/reversibility rules and all17 canonical runtime contract boundaries remain incomplete.'),
'kb': ('02_KNOWLEDGE_BASE_AUDIT_AND_CANONICAL_MODEL.md',1,'Retain canonical JSON as knowledge-base data authority with HTML parity, corrected P/R/A/I/N relationships and preserved claim/source/uncertainty metadata. Curating legacy research is not a runtime dependency, numerical benchmark guarantee or source fact certification.', [], [], 'Current artifact identity/parity can be checked separately; live external assertions and numerical claims are not reverified here. No mandatory third-party integration follows from research inventory.'),
'goal': ('15_NORMATIVE_STATE_MACHINES.md',113,'Retain versioned goal contract, explicit criteria/dependencies/budgets and independent criterion verification; blocked reactivation needs evidence and terminal continuation creates linked new history rather than silent reopening.', ['prototype/prain/goal_registry.py','prototype/prain/secure_completion.py','prototype/prain/runtime.py'], ['prototype/tests/test_phase1.py','prototype/tests/test_secure_completion_integration.py'], 'Criterion-specific and atomic completion tests cover a subset. Full canonical goal transitions/planner lineage/budget/fairness and trusted actual verifier evidence remain incomplete.'),
'recovery': ('15_NORMATIVE_STATE_MACHINES.md',74,'Retain transactional dispatch reservation, stable digest/idempotency, fresh authorization, explicit unknown outcomes and authoritative reconciliation before retry. Lease expiry/timeout cannot prove effect absence; compensation itself requires policy and verification.', ['prototype/prain/durable_admission.py','prototype/prain/dispatcher.py','prototype/prain/scf_delivery.py','prototype/prain/fenced_leases.py'], ['prototype/tests/test_durable_admission.py','prototype/tests/test_dispatcher.py','prototype/tests/test_production_multinode.py'], 'Durable local reservation/recovery and same-host TLS process faults are partial. Actual remote side-effect truth, all receipt states/guards, cross-store atomicity, compensation and real-host partition/fencing remain unproved.'),
'communication': ('01_SCHEMA_AND_MIGRATION_POLICY.md',26,'Retain command/event/query distinctions, typed explicit versioned envelopes, trace/causation/provenance, tenant scope, durable inbox/outbox and idempotency. The later canonical message-envelope transports a separate typed semantic payload; old event/message shapes require named adapters.', ['prototype/prain/scf_http.py','prototype/prain/scf_wire.py','prototype/prain/scf_delivery.py','prototype/prain/durable_components.py'], ['prototype/tests/test_production_multinode.py','prototype/tests/test_production_security.py','prototype/tests/test_scf_delivery.py'], 'Authenticated bounded HTTP/SCF subset exists. Full canonical envelope mapping, alternate transport, general command/query handlers, DLQ/backpressure and tenant-aware end-to-end routing remain unproved.'),
'scf': ('04_IDENTITY_TENANCY_AND_AUTHORITY.md',24,'Retain multiscale semantic coordination with declared authority, scope-selective synchronization, explicit semantic conflicts, versioned plans and invalidation. Local hypotheses may differ; policy/rights/goal heads/evidence completion cannot be overridden by stale projections.', ['prototype/prain/scf.py','prototype/prain/durable_semantics.py','prototype/prain/scf_http_dispatcher.py'], ['prototype/tests/test_scf_contract.py','prototype/tests/test_durable_semantics.py','prototype/tests/test_production_multinode.py'], 'Local decisions/inbox/duplicate checks persist. Complete L0-L3 graph, semantic routing/selective synchronization, conflict adjudication and two-host consistency conformance are unproved.'),
'anima': ('02_KNOWLEDGE_BASE_AUDIT_AND_CANONICAL_MODEL.md',25,'Retain distributed identity across P/R/A/I/N with Anima maintaining inspectable evidence-linked self-model revisions. Model self-assertions are not tested capabilities; Anima/HAL cannot grant permissions or replace explicit policy.', ['prototype/prain/anima_hal.py','prototype/prain/durable_semantics.py'], ['prototype/tests/test_anima_hal_contract.py','prototype/tests/test_durable_semantics.py'], 'Versioned local Anima and durable CAS subset exists. Complete commitments/capability provenance, distributed lineage/merge and authoritative eligibility workflow remain incomplete.'),
'observability': ('07_HAL_RESILIENCE_AND_CONFORMANCE.md',53,'Retain causal workflow metrics and declared deployment-specific SLOs with measurement source/window/threshold/consequence. Safety invariants such as fresh authorization and tenant isolation are mandatory, not adjustable SLO promises.', ['prototype/prain/anima_hal.py'], ['prototype/tests/test_anima_hal_contract.py'], 'Telemetry freshness/unknown handling is partial. End-to-end redacted metric export, measured queue/reconciliation/deletion/RTO/RPO and production alert/runbook drills are unproved.'),
'release': ('13_RELEASE_AND_CHANGE_CONTROL.md',1,'Retain distinct specification completeness, explicit human closure and separate implementation authorization. Version/hash/validator references and preserved scope are mandatory; an old candidate checkbox/attestation is not current production proof.', ['tools/verify_phase1_gates.py','tools/run_acceptance_evidence.py'], ['prototype/tests/test_gate_validator.py'], 'Current strict gates remain not accepted. Historical approval statements are preserved with original hash/scope and never treated as a new human signature or full production authorization.'),
'conformance': ('17_SCHEMA_STATE_MACHINE_CROSSWALK.md',5,'Retain real runtime/adaptor negative conformance separately from offline oracle/schema checks. Valid enum endpoints do not authorize a transition; live references, time, identity, CAS and side-effect truth require additional guards.', ['tools/run_acceptance_evidence.py'], ['prototype/tests/test_production_security.py','prototype/tests/test_production_multinode.py','prototype/tests/test_production_privacy.py'], 'Executed235-test checkpoint covers only named tests, not every canonical invariant/fault family. Exhaustive canonical runtime suites and true two-host effects remain missing.'),
'architecture': ('08_DECISION_REGISTER_FINAL.md',1,'Retain independent semantic control-plane PRAIN: P/R/A/I/N are logical capabilities, not fixed services; policy exclusively authorizes actions and compute/storage/providers remain replaceable. Quantum/biological analogies are no performance or consciousness evidence.', ['prototype/prain/runtime.py','prototype/prain/semantic_router.py'], ['prototype/tests/test_architecture_alignment.py','prototype/tests/test_semantic_router.py'], 'Prototype alignment and routing metadata are partial. Versioned interchangeable adapter families and complete distributed architecture implementation are not established.'),
}
# Explicit document-family judgments, not word matching of candidate text.
PROFILES={
'06_EVIDENCE_PRIVACY_AND_DATA_LIFECYCLE.md':'privacy','07_HAL_RESILIENCE_AND_CONFORMANCE.md':'hal','08_DECISION_REGISTER_FINAL.md':'architecture','09_PHASE0_EXIT_CRITERIA.md':'release','10_REFERENCE_FLOWS.md':'conformance','11_SPEC_VALIDATION_BOUNDARY.md':'conformance','12_KNOWLEDGE_BASE_SOURCE_FACT_CHECK.md':'kb','13_INVARIANT_COVERAGE_AND_TEST_BOUNDARY.md':'conformance','13_RELEASE_AND_CHANGE_CONTROL.md':'release','14_SEMANTIC_CONSISTENCY_AUDIT.md':'audit','15_NORMATIVE_STATE_MACHINES.md':'state','16_STATE_MACHINE_CONFORMANCE_MATRIX.md':'conformance','17_SCHEMA_STATE_MACHINE_CROSSWALK.md':'conformance','SCHEMA_FIELD_AUDIT_RECURSIVE.md':'audit','COMMUNICATION_MODEL.md':'communication','FAILURE_AND_RECOVERY.md':'recovery','GOAL_AND_CONTROL_LOOP.md':'goal','IDENTITY_AND_CONTINUITY.md':'anima','OBSERVABILITY_AND_EVALUATION.md':'observability','REFERENCE_ARCHITECTURE.md':'architecture','SEMANTIC_MODEL.md':'claim','THREAT_AND_TRUST_BOUNDARIES.md':'policy','DECISION_REGISTER.md':'architecture','IMPLEMENTATION_ROADMAP.md':'conformance','TRACEABILITY_MATRIX.md':'conformance','IMPLEMENTATION_PLAN.md':'conformance','CLUSTER_TOPOLOGY.md':'communication','CONFORMANCE_TESTS.md':'conformance','CONSISTENCY_MODEL.md':'identity','EXECUTION_AND_RECOVERY.md':'recovery','MESSAGE_PROTOCOL.md':'communication','STATE_AND_CONFLICTS.md':'identity','PRAIN_MASTER_INDEX.md':'release','DECISION_REGISTER.md':'architecture','PHASE0_EXIT_CRITERIA.md':'release','PHASE0_README.md':'architecture','PHASE1_INTERFACE_CONTRACTS.md':'communication','architecture-decisions.md':'architecture','phase0-checklist.md':'release','CONFORMANCE_MATRIX.md':'conformance','DECISIONS.md':'architecture','TRACEABILITY.md':'release','ARCHITECTURE.md':'scf','CONSISTENCY_AND_CONFLICTS.md':'scf','COORDINATION_PROTOCOL.md':'communication','HOMEOSTASIS_ADAPTATION.md':'hal','IDENTITY_AND_LINEAGE.md':'anima','CLAIM_SEMANTICS_AND_EPISTEMIC_LIFECYCLE.md':'claim','CONSOLIDATION_AND_PHASE0_GATE.md':'release','CONTRACT_CROSSWALK.md':'migration','DECISION_FREEZE_PROPOSAL.md':'release','DECISION_REVIEW_TABLE.md':'architecture','KNOWLEDGE_BASE_CROSSWALK.md':'kb','KNOWLEDGE_BASE_ITEM_AUDIT.md':'kb','PHASE0_GAPS_AND_EXIT.md':'release','REFERENCE_FLOWS.md':'conformance','SCHEMA_FIELD_AUDIT.md':'audit','SCHEMA_FIELD_AUDIT_DEEP.md':'audit','SEVEN_TRACK_REVIEW_PLAN.md':'conformance','SEVEN_TRACK_STATUS.md':'audit','TRACEABILITY_MASTER.md':'release','VERSIONING_AND_CHANGE_POLICY.md':'migration','CLOSURE_CANDIDATE.md':'release','RELEASE_ATTESTATION_TEMPLATE.md':'release','RELEASE_ATTESTATION.md':'release','00_COMPLETION_REPORT.md':'audit','01B_SCHEMA_FAMILY_CROSSWALK.md':'migration','01_SCHEMA_AND_MIGRATION_POLICY.md':'migration','02B_KNOWLEDGE_BASE_ITEM_DISPOSITION.md':'kb','02_KNOWLEDGE_BASE_AUDIT_AND_CANONICAL_MODEL.md':'kb','03_CLAIM_ONTOLOGY_AND_LIFECYCLE.md':'claim','04_IDENTITY_TENANCY_AND_AUTHORITY.md':'identity','05_POLICY_APPROVAL_AND_REVOCATION.md':'policy','PHASE1_START_PLAN.md':'conformance','PHASE0_ACCEPTANCE.md':'release','PHASE1_IMPLEMENTATION_STATUS.md':'audit','CHANGELOG.md':'audit','PRAIN_Wissensdatenbank.v0.3.0.json':'kb','invariants.json':'architecture','test-vectors.json':'audit',
}
# Section-specific normative state-machine bindings.
STATE={
'15.1':('identity',5),'15.2':('claim',13),'15.3':('policy',17),'Canonical action digest':('policy',27),'15.4':('policy',57),'15.5':('recovery',74),'15.6':('recovery',83),'Reconciliation result':('recovery',103),'15.7':('goal',113),'15.8':('hal',126),'15.9':('identity',137),'15.10':('conformance',141),
}

def hashbytes(b):return hashlib.sha256(b).hexdigest()
def canonical_ref(basename,line=1):
 members=[x for x in CANON.namelist() if x.endswith('/'+basename)]
 if len(members)!=1:raise ValueError((basename,members))
 name=members[0];data=CANON.read(name);lines=data.decode().splitlines()
 assert 1<=line<=len(lines),(basename,line)
 return {'archive':ARCHIVE,'archive_sha256':ARCHIVE_HASH,'member':name,'sha256':hashbytes(data),'line':line,'text':lines[line-1]}

def section_context(lines,line):
 start=line-1
 if not lines[start].startswith('#'):
  while start>0 and not lines[start].startswith('#'):start-=1
 level=len(lines[start])-len(lines[start].lstrip('#')) if lines[start].startswith('#') else 0
 end=start+1
 while end<len(lines):
  if lines[end].startswith('#') and len(lines[end])-len(lines[end].lstrip('#'))<=level:break
  end+=1
 text='\n'.join(lines[start:end])
 return {'start_line':start+1,'end_line':end,'heading':lines[start] if lines[start].startswith('#') else None,'sha256':hashbytes(text.encode()),'text':text}

def profile_for(x,ctx):
 base=x['source']['path'].split('/')[-1]
 if '/audit/' in x['source']['path']:return 'audit'
 if base=='README.md':return 'architecture'
 if base=='invariants.json' and 'digest mismatch' in x['text']:return 'policy'
 p=PROFILES.get(base)
 if p=='state':
  for prefix,(name,_) in STATE.items():
   if prefix in (ctx.get('heading') or ''):return name
  return 'conformance'
 return p

def anchors(paths):
 result=[]
 for p in paths:
  target=ROOT/p
  if target.is_file():result.append({'path':p,'sha256':hashbytes(target.read_bytes())})
 return result

records=[json.loads(l) for l in (ROOT/'TRACEABILITY/IMPLEMENTATION_EVIDENCE_20261025/requirement_evidence.jsonl').open()]
records=[r for r in records if 3801<=int(r['requirement_id'][4:])<=5071]
cache={};out=[];units={};unknown=[]
for x in records:
 path=x['source']['path'];line=x['source']['line'];base=path.split('/')[-1]
 if path not in cache:cache[path]=ev.read_source(path)[0]
 data=cache[path];lines=data.decode().splitlines();assert lines[line-1].strip()==x['text']
 ctx=section_context(lines,line) if base.endswith('.md') else {'start_line':1,'end_line':len(lines),'heading':None,'sha256':hashbytes(data),'text':data.decode()}
 # The entire enclosing section is preserved so heading rows cannot erase its obligations.
 unit_id='D-'+hashbytes((hashbytes(data)+':'+str(ctx['start_line'])+':'+str(ctx['end_line'])).encode())[:20]
 family=profile_for(x,ctx)
 disposition='RETAIN';role='NORMATIVE_CLAUSE';rationale='';canonical=None;related=[]
 if not family:
  disposition='UNRESOLVED';role='UNCLASSIFIED_CONTEXT';rationale='No curated source-family judgment yet. Source and context preserved; no normative or implementation acceptance inferred.';unknown.append(x['requirement_id']);fam=P['conformance']
 elif family=='audit':
  disposition='NON_NORMATIVE';role='HISTORICAL_AUDIT_OR_RESULT';fam=P['conformance'];rationale='This source is an audit/inventory/result artefact. Its recorded PASS/count/status describes a fixed offline package, not an executable runtime obligation or live result. Underlying obligations remain in canonical contracts and crosswalk; preserving this result never accepts their implementation.'
  canonical=canonical_ref('11_SPEC_VALIDATION_BOUNDARY.md',1)
 else:
  fam=P[family];canonical=canonical_ref(fam[0],fam[1]);rationale=fam[2]
  if base=='15_NORMATIVE_STATE_MACHINES.md':
   for prefix,(pf,cl) in STATE.items():
    if prefix in (ctx.get('heading') or ''):canonical=canonical_ref('15_NORMATIVE_STATE_MACHINES.md',cl);break
  comp=x['source'].get('current_canonical_compatibility',{})
  if comp.get('status') in ('CURRENT_SOURCE_BYTES_IDENTICAL','CURRENT_SOURCE_LINE_EXACT'):
   members=comp.get('line_candidates') or [line]
   member=comp.get('member')
   if member in CANON.namelist():
    cd=CANON.read(member);clines=cd.decode().splitlines();matches=[i for i in members if 1<=i<=len(clines) and clines[i-1].strip()==x['text']]
    if matches:canonical={'archive':ARCHIVE,'archive_sha256':ARCHIVE_HASH,'member':member,'sha256':hashbytes(cd),'line':matches[0],'text':clines[matches[0]-1]}
  # Candidate/plan authorizations are historical governance; current explicit user request authorizes this implementation, not fabricated closure.
  if base in ('README.md','CHANGELOG.md','PHASE1_IMPLEMENTATION_STATUS.md','00_COMPLETION_REPORT.md'):
   role='HISTORICAL_PACKAGE_DESCRIPTION';disposition='NON_NORMATIVE';rationale='Package title/map/delivered/test-limit statements are version-scoped historical description. They cannot update the current production state. Any design constraints in the enclosing section are preserved as supplementary obligations with the stated family interpretation. '+fam[2]
  if base=='README.md' and ctx.get('heading') in ('## Core invariants','## Design constraints','## Design principles','## Core thesis','## Design thesis'):
   disposition='RETAIN';role='NORMATIVE_SECTION_LOCATOR' if x['text'].startswith('#') else 'NORMATIVE_CLAUSE';rationale='This README section contains effective design constraints, not just package metadata. Its entire semantic unit remains normative alongside the later detailed contracts. '+fam[2]
  if x['text'].startswith('#') and role=='NORMATIVE_CLAUSE':
   role='NORMATIVE_SECTION_LOCATOR';rationale='This extracted row is a heading, not an independent acceptance clause. It retains the complete enclosed normative unit below, including its guards and failure cases. '+rationale
  if x['text'].startswith('|') and set(x['text'].replace('|','').replace('-','').replace(':','').strip())==set():
   role='TABLE_FORMATTING';disposition='NON_NORMATIVE'
  if base=='15_NORMATIVE_STATE_MACHINES.md' and comp.get('status')=='CURRENT_SOURCE_LINE_CHANGED_OR_ABSENT':
   if 'suspended' in x['text']:
    disposition='EXTEND';canonical=canonical_ref('15_NORMATIVE_STATE_MACHINES.md',139);rationale='Earlier delegation lifecycle is retained but tightened by the canonical fresh-authority/event/reason/epoch/unchanged-scope/time/budget guards. Revoked/expired/exhausted grants remain terminal; the extension is not evidence the guards are implemented.'
  if base=='16_STATE_MACHINE_CONFORMANCE_MATRIX.md' and not x['text'].startswith('#'):
   disposition='NON_NORMATIVE';role='HISTORICAL_REFERENCE_EXECUTION_CLAIM';rationale='The numeric offline execution count belongs to this archived model/version. The canonical model carries updated504-case documentation. Counts must never be added across wrappers or generalized to the current runtime; separately retain the mandatory runtime-only cases in the same matrix.'
  if base=='PHASE1_INTERFACE_CONTRACTS.md' and 'Policy Gateway' in (ctx.get('heading') or ''):
   disposition='SUPERSEDE';canonical=canonical_ref('05_POLICY_APPROVAL_AND_REVOCATION.md',19);rationale='The legacy allow vocabulary is replaced in the canonical policy-decision contract by permit/deny/require_approval/defer. This is an explicit representation change, requiring a named version adapter; it never converts approval-required or unknown into permission.'
  if base in ('DECISION_FREEZE_PROPOSAL.md','CONTRACT_CROSSWALK.md'):
   disposition='RETAIN';rationale='Retain the decision/reconciliation procedure and complete original contract closure obligations. Later adopted vocabulary must be named and versioned; an old proposed status neither grants permission nor removes the requirement to reconcile fields, enums and transitions. '+fam[2]
  if base in ('SCHEMA_FIELD_AUDIT.md','SCHEMA_FIELD_AUDIT_DEEP.md') and x['text'].startswith('- '):
   disposition='RETAIN';role='AUDIT_RECOMMENDATION_RETAINED';rationale='Although the parent report is historical, this explicit migration/registry warning remains an effective constraint under the canonical migration policy. '+P['migration'][2];canonical=canonical_ref('01_SCHEMA_AND_MIGRATION_POLICY.md',22)
 if family=='audit' and base in ('SCHEMA_FIELD_AUDIT.md','SCHEMA_FIELD_AUDIT_DEEP.md') and x['text'].startswith('- '):
  fam=P['migration'];disposition='RETAIN';role='AUDIT_RECOMMENDATION_RETAINED';rationale='This explicit recommendation is now required by the canonical migration policy: historical IDs and closed schemas require deliberate versioned migration and confidence cannot be treated as verification. '+fam[2];canonical=canonical_ref('01_SCHEMA_AND_MIGRATION_POLICY.md',22)
 # Explicit mixed-content/legacy-choice adjudications retained at row granularity.
 n=int(x['requirement_id'][4:])
 if n==4021:
  disposition='RETAIN';role='NORMATIVE_CLAUSE';fam=P['identity'];canonical=canonical_ref('04_IDENTITY_TENANCY_AND_AUTHORITY.md',42);rationale='This numbered README invariant requires projection freshness/version disclosure; it is substantive despite the document also containing package metadata. '+fam[2]
 if n==4118:
  disposition='SUPERSEDE';fam=P['claim'];canonical=canonical_ref('03_CLAIM_ONTOLOGY_AND_LIFECYCLE.md',57);rationale='The legacy exception path cannot establish verified status. Canonical migration preserves the exception only as review context and requires named passing verification/evidence; missing legacy proof is quarantined/reviewed, never promoted. The historical checked box is not present implementation evidence.'
 old_choices={4161:('migration',7,'Opaque stable IDs and explicit canonical URN schema IDs replace this historical unchosen identifier checkbox; UUIDv7 preference must not make time order authoritative.'),4162:('identity',46,'UTC timestamps and per-aggregate version/CAS ordering replace the historical undecided clock-rule checkbox; skew is not authority.'),4163:('communication',26,'At-least-once plus idempotency is the adopted baseline; no global exactly-once promise remains an open equivalent alternative.'),4164:('identity',42,'Per-class authority/consistency and CAS rules resolve this historical generic state-store choice; concrete backend remains deployment-specific.'),4165:('privacy',12,'Append-only decision history with separate content/integrity metadata resolves this historical ledger-choice question; hash-chain alone is not authenticity.'),4166:('policy',26,'Canonical bounded expiring actor/action/tenant-bound approvals and delegation resolve the generic policy-choice question; actual issuer/key integration remains open implementation.'),4167:('privacy',27,'Canonical per-class retention and propagated deletion/redaction resolve the historical need for a privacy contract; lawful durations remain deployment choices.'),4168:('migration',15,'Canonical negotiated compatibility and explicit migration registry resolve the old blank SemVer checkbox; strict-reader compatibility must still be tested.')}
 if n in old_choices:
  pf,cl,note=old_choices[n];fam=P[pf];canonical=canonical_ref(fam[0],cl);disposition='SUPERSEDE';role='HISTORICAL_OPEN_CHOICE_WITH_ADOPTED_SUCCESSOR';rationale=note+' This resolves specification-choice status only; it does not close implementation proof.'
 legacy_resolution_reference=None
 if n in old_choices:
  legacy_archive='archive/PRAIN_Phase0_v0.2.1.zip'
  with zipfile.ZipFile(ROOT/legacy_archive) as lz:
   lm=next(k for k in lz.namelist() if k.endswith('/docs/DECISION_REGISTER.md'));ld=lz.read(lm)
  ll=6+4*(n-4161)
  legacy_resolution_reference={'archive':legacy_archive,'archive_sha256':hashbytes((ROOT/legacy_archive).read_bytes()),'member':lm,'sha256':hashbytes(ld),'line':ll,'text':ld.decode().splitlines()[ll-1]}
  rationale+=' Exact prior resolution is also bound to the same-generation DEC-%03d decision, whose internal-ID preference and UTC requirements remain preserved.'%(n-4160)
  if n==4163:canonical=canonical_ref('04_IDENTITY_TENANCY_AND_AUTHORITY.md',44)
 # FINAL-NORM-001: bind retained reconciliation/approval duties to operative
 # clauses, not a document heading; all obligations still require proof.
 retained_obligations=None
 if n in (4312,4316,4317):
  if n==4312:
   clause_file='01_SCHEMA_AND_MIGRATION_POLICY.md'
   clause_lines=[11,19,24,30,31,32,33,34,35,36]
  else:
   clause_file='13_RELEASE_AND_CHANGE_CONTROL.md'
   clause_lines=[16,17,18,22,26]
  canonical=[canonical_ref(clause_file,cl) for cl in clause_lines]
  retained_obligations=[{'canonical_reference':ref,'text':ref['text'],
   'text_sha256':hashbytes(ref['text'].encode()),'implementation_status':'OPEN'}
   for ref in canonical]
  disposition='RETAIN'
  rationale+=' Operative canonical clauses are individually preserved below with exact archive text and hashes. Each retained duty remains OPEN; neither reconciliation nor recorded historical approval establishes implementation or current production acceptance.'
 unit={'source_path':path,'source_sha256':hashbytes(data),'start_line':ctx['start_line'],'end_line':ctx['end_line'],'heading':ctx['heading'],'context_sha256':ctx['sha256'],'context':ctx['text'],'family':family}
 units.setdefault(unit_id,unit)
 # Keep references distinct from proven behavioral execution.
 out.append({'requirement_id':x['requirement_id'],'source':{'path':path,'sha256':hashbytes(data),'line':line,'line_sha256':hashbytes(x['text'].encode())},'source_text':x['text'],'text':x['text'],'effective_disposition':disposition,'disposition':disposition,'implementation_status':'NOT_APPLICABLE' if disposition=='NON_NORMATIVE' and role in ('HISTORICAL_AUDIT_OR_RESULT','HISTORICAL_REFERENCE_EXECUTION_CLAIM') else ('PARTIAL' if fam[3] else 'OPEN'),'missing_proof':fam[5],'row_role':role,'semantic_unit_id':unit_id,'canonical_reference':canonical,'legacy_resolution_reference':legacy_resolution_reference,'canonical_relation':'EXPLICIT_VERSIONED_REPLACEMENT_OF_HISTORICAL_CHOICE' if disposition=='SUPERSEDE' else ('EXPLICIT_GUARD_EXTENSION' if disposition=='EXTEND' else ('EXPLICIT_CURRENT_CLAUSE' if isinstance(canonical,dict) and canonical.get('text','').strip()==x['text'] else 'CONTEXTUAL_ALIGNMENT_NOT_AUTOMATIC_SUPERSESSION')),'rationale':rationale,'implementation_evidence':{'state':'NOT_ACCEPTED','code_references':anchors(fam[3]),'test_references':anchors(fam[4]),'behavioral_execution_imported':False,'remaining_proof':fam[5]},'review_method':'DOCUMENT_AND_ENCLOSING_SECTION_SEMANTICS_WITH_CURATED_FAMILY_AND_EXPLICIT_OVERRIDES','reviewer':'normative_d independent partition worker','production_acceptance':False})
 if retained_obligations is not None:
  out[-1]['retained_obligations']=retained_obligations
  out[-1]['implementation_status']='OPEN'
  out[-1]['canonical_relation']='EXPLICIT_OPERATIVE_CLAUSES_WITH_RETAINED_OPEN_DUTIES'
assert len(out)==1271 and {x['requirement_id'] for x in out}=={f'RTM-{i:05}' for i in range(3801,5072)}
(OUT/'part_d.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False,sort_keys=True)+'\n' for x in out))
(OUT/'part_d_contexts.json').write_text(json.dumps(units,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
summary={'partition':['RTM-03801','RTM-05071'],'rows':len(out),'source_occurrences':len(cache),'distinct_source_contents':len({hashbytes(d) for d in cache.values()}),'semantic_units':len(units),'dispositions':dict(collections.Counter(x['effective_disposition'] for x in out)),'roles':dict(collections.Counter(x['row_role'] for x in out)),'unresolved':unknown,'canonical_archive':ARCHIVE,'canonical_archive_sha256':ARCHIVE_HASH,'implementation_accepted':0,'production_accepted':False,'review_limits':['Source-family/section adjudication is not a proof of runtime implementation.','Preserved full contexts retain obligations under heading-only extraction.','Same source/content contexts share semantic judgments; historical results never transfer acceptance.','Historical user-attestation assertions remain source-scoped and are not re-signed here.']}
(OUT/'part_d_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
