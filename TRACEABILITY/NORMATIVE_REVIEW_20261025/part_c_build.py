"""Materialize context-reviewed historical dispositions for RTM-02501..03800.

The explicit index table is a reviewed set of exact texts, NOT a keyword classifier.
Markdown headings are interpreted as navigation while their complete source section
and inherited normative obligations remain attached. No runtime pass is granted.
"""
import json,hashlib,zipfile,io,collections,re,ast
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
ALL=[json.loads(x) for x in (ROOT/'TRACEABILITY/IMPLEMENTATION_EVIDENCE_20261025/requirement_evidence.jsonl').open()]
ROWS=ALL[2500:3800]
UNIQUE=list({x['text']:x for x in reversed(ROWS)}.values()) # overwritten below to preserve first-seen order
seen={}
for row in ROWS:seen.setdefault(row['text'],row)
UNIQUE=list(seen.values())
assert len(UNIQUE)==411
sha=lambda b:hashlib.sha256(b).hexdigest()
ARCH='archive/PRAIN_v0.99.6_Phase0_Green_Closure.zip'
archive_bytes=(ROOT/ARCH).read_bytes()
with zipfile.ZipFile(io.BytesIO(archive_bytes)) as z:CANON={n:z.read(n) for n in z.namelist() if not n.endswith('/')}
PREFIX='PRAIN_v0.99.6_Phase0_Green_Closure/'
# Explicit source-context decisions for every substantive prose/table/KB clause.
# category supplies relevant implementation anchors and missing runtime proof.
D={}
def put(indices,category,filename,needle,rationale,disposition='RETAIN'):
    for i in indices:
        assert i not in D,i
        D[i]=(category,filename,needle,rationale,disposition)
put([26,85],'claim','03_CLAIM_ONTOLOGY_AND_LIFECYCLE.md','confidence never automatically promotes status',
    'The safety rule is preserved: confidence, epistemic verification and action authority are independent. Canonical claim invariants and policy separation strengthen the older migration warning.')
put([32,148],'schema','01_SCHEMA_AND_MIGRATION_POLICY.md','The historical archive contains 20 schemas',
    'The older requested nested/dialect/identifier audit is specified by the recursive audit and explicit registry policy. Historical audit completion is not runtime schema/migration conformance.','EXTEND')
put([44],'knowledge','02B_KNOWLEDGE_BASE_ITEM_DISPOSITION.md','Total item records:',
    'The prior open item-mapping task is extended by an explicit112-item disposition ledger. Preserved research claims are not verified facts or executable permissions.','EXTEND')
put([51,76,354],'boundary','11_SPEC_VALIDATION_BOUNDARY.md','Offline',
    'This is a continuing evidence-scope rule: a paper/schema/reference-oracle PASS is not implementation or whole-system acceptance. No historical PASS is transferred to the runtime.')
put([53],'schema','01_SCHEMA_AND_MIGRATION_POLICY.md','Envelope `schema_id` identifies the payload schema',
    'Package release versions and envelope/payload schema versions remain distinct. A package version cannot silently declare compatibility of strict readers.')
put([61,242],'claim','03_CLAIM_ONTOLOGY_AND_LIFECYCLE.md','These axes must not be collapsed',
    'The continuation enumerates epistemic status, verification, confidence, validity, lifecycle and revisions independently. Retain all axes; a single local status does not establish full canonical conformance.')
put([67],'claim','03_CLAIM_ONTOLOGY_AND_LIFECYCLE.md','`statement` → `proposition.statement`',
    'The older proposed proposition union is replaced by the canonical claim contract and reviewed migration. Preserve exact legacy statements/terms; do not invent missing subject/predicate/object or presume semantic consistency.','SUPERSEDE')
put([70],'privacy','06_EVIDENCE_PRIVACY_AND_DATA_LIFECYCLE.md','Evidence manifests contain source identity',
    'Source identity, capture/record time, integrity, tenant, classification and retention are retained in the evidence manifest. A content digest is not identity or truth verification.')
put([71,86],'claim','03_CLAIM_ONTOLOGY_AND_LIFECYCLE.md','Derived claims reference premise claims',
    'Premise/method/version lineage, evidence and counterevidence remain required; invalidated premises trigger reevaluation, not automatic assertion of downstream falsity. Immutable revisions preserve transition history.','EXTEND')
put([73],'claim','03_CLAIM_ONTOLOGY_AND_LIFECYCLE.md','legacy `verification_exception_ref` cannot be treated as a pass',
    'Preserve the old exception reference as review/provenance metadata. An exception is never evidence of a successful verification procedure.')
put([81,223,225,227,229],'schema','01_SCHEMA_AND_MIGRATION_POLICY.md','Every migration record must identify:',
    'Retain strict versioned boundaries and explicit deterministic migration records with loss/default/rejection fixtures. No field-name rewrite, additive-minor label, legacy status name or missing authority can invent semantic compatibility or permission.')
put([83,113],'identity','08_DECISION_REGISTER_FINAL.md','| D-0002 |',
    'Canonical D-0002 retains PRAIN as an independent framework. Hallerbans may consume it; no dependency or principal identity is derived from that host.')
put([90,288,292,294],'slo','07_HAL_RESILIENCE_AND_CONFORMANCE.md','PRAIN does not impose one universal',
    'The old open SLO decision is resolved normatively by per-deployment numeric profiles and universal hard safety invariants. Latency/window/source/threshold/consequence metrics remain a runtime obligation; none is guessed.','EXTEND')
put([97],'state','15_NORMATIVE_STATE_MACHINES.md','## 15.6',
    'The old proposed union of status names is superseded by explicit canonical transition matrices and guards. An enum or lifecycle summary cannot authorize an edge or collapse effect/verification/unknown distinctions.','SUPERSEDE')
put([102,110],'release','08_DECISION_REGISTER_FINAL.md','## Explicitly deferred',
    'Retain explicit decision provenance and deferral. Canonical D-0021 keeps concrete runtime/broker/storage/provider selection profile-specific; no proposed vendor is made mandatory by this review.','EXTEND')
put([104],'identifier','04_IDENTITY_TENANCY_AND_AUTHORITY.md','Time alone is not a concurrency token',
    'Retain the original UUIDv7 generation preference as advisory; no later source explicitly removes it. Canonical opaque IDs describe record identity, while URN schema identifiers are a different namespace. Do not reject legacy opaque IDs for not being UUIDv7, and never derive aggregate ordering or authority from the UUID timestamp. Generator collision/clock-rollback proof remains open.','RETAIN')
put([105],'delivery','08_DECISION_REGISTER_FINAL.md','| D-0007 |',
    'At-least-once delivery and idempotent consumers are retained; no global exactly-once promise. Command uniqueness is tenant/digest scoped and retry requires authoritative reconciliation when effects may have happened.')
put([106,258],'consistency','04_IDENTITY_TENANCY_AND_AUTHORITY.md','Strong consistency is scoped',
    'Retain strong auth/critical heads and per-aggregate ordering; derived views expose revision/freshness and never overwrite authority. The current authority matrix fills the older open per-record table.','EXTEND')
put([107,112],'architecture','08_DECISION_REGISTER_FINAL.md','| D-0003 |',
    'Biological/processor labels remain explanatory analogies only; roles require inspectable falsifiable mechanisms. Quantum-ready remains replaceable interfaces without consciousness or quantum-advantage claims.')
put([108],'release','13_RELEASE_AND_CHANGE_CONTROL.md','Never mutate an approved artifact in place',
    'Artifact immutability and explicit versioned change records are retained. A supersession must name its replacement and rationale; implementation still needs evidence and cannot be silently recategorized.')
put([120,129,329],'knowledge','02_KNOWLEDGE_BASE_AUDIT_AND_CANONICAL_MODEL.md','## 2.4',
    'The legacy senses→brain/brain label maps to P observations feeding R reasoning with provenance and uncertainty. Memory is cross-cutting. Derived claims still require premises/method; analogy is not an authorization or independently verified factual assertion.')
put([130],'policy','05_POLICY_APPROVAL_AND_REVOCATION.md','The policy gateway is the only component',
    'The old A/Soul-authorizes-N relation is explicitly rejected as an authorization rule. Canonical A is a self-model; only the independent policy gateway can authorize actions.')
put([133,145,276,278],'privacy','06_EVIDENCE_PRIVACY_AND_DATA_LIFECYCLE.md','## 6.5',
    'Retain end-to-end scoped deletion: authority tombstone, derived/replica/cache/export propagation, legal holds, backup horizons, current tombstones before serving restores and per-target verification. Deleting one projection row does not complete this obligation.','EXTEND')
put([134,265],'policy','05_POLICY_APPROVAL_AND_REVOCATION.md','Approval is an explicit record bound',
    'Retain tenant/actor/action/target/effect/policy/issuer/expiry binding and current authority. One-shot or bounded-use consumption must be atomic with reservation; local credential checks do not establish issuer assurance or distributed effect-side race freedom.','EXTEND')
put([235],'knowledge','02_KNOWLEDGE_BASE_AUDIT_AND_CANONICAL_MODEL.md','`knowledge_base/PRAIN_Wissensdatenbank.v0.3.0.json`',
    'The old v0.2.0 JSON authoring filename is superseded by canonical KBv0.3.0. JSON-first authoring and exact parsed HTML parity remain mandatory; updating data version does not verify research claims.','SUPERSEDE')
put([239],'knowledge','02_KNOWLEDGE_BASE_AUDIT_AND_CANONICAL_MODEL.md','## 2.5',
    'Retain source-type/scope/version/date/method qualification before numerical research claims influence requirements. The original17-URL count is historical and is not a current live verification result.')
put([246,247,248],'claim','15_NORMATIVE_STATE_MACHINES.md','## 15.2',
    'Retain initial-status provenance, immutable verification history and both-sided dispute evidence. Canonical state-machine guards extend this summary; verified/refuted transitions need named procedures and references, not confidence alone.','EXTEND')
put([255],'identity','04_IDENTITY_TENANCY_AND_AUTHORITY.md','`active → suspended → active`',
    'Retain attributable suspension/reactivation, monotonic revocation for identity version and lineage-preserving replacement/rotation. Reevaluate approvals/delegations on identity/tenant/policy/epoch changes.')
put([273],'privacy','06_EVIDENCE_PRIVACY_AND_DATA_LIFECYCLE.md','Recovery/backup access to keys',
    'Retain controlled audited key recovery and tested rotation/restore in the deployment profile. A test-only shared key or hash chain is not a KMS/key-lifecycle implementation.')
put([280],'privacy','06_EVIDENCE_PRIVACY_AND_DATA_LIFECYCLE.md','Logs/traces must redact',
    'Retain collection-time redaction across logs/traces, minimal metadata and explicit audit-gap signals. Projection credential filtering alone does not cover ordinary event, receipt, backup or observability paths.')
put([290],'conformance','07_HAL_RESILIENCE_AND_CONFORMANCE.md','A runtime must later implement',
    'Retain the full family of real-adapter security/fault/privacy/rollback tests. Existing deterministic models validate specified rules only; later implementation must execute equivalent cases against its own behavior.')
put([299,361,367,383,392],'release','13_RELEASE_AND_CHANGE_CONTROL.md','## 13.1',
    'The historical not-approved candidate status is superseded as a version status by canonicalv0.99.6 Phase0 closure record. The continuing separation of specification closure, implementation authorization and production approval is retained; this review does not impersonate a user signature.','SUPERSEDE')
put([330],'goal','04_IDENTITY_TENANCY_AND_AUTHORITY.md','| Goal/plan |',
    'Observations can affect feasibility but do not silently mutate goals. Goal authority uses attributable version/CAS changes and terminal-state rules; preserve revision history.')
put([331,347],'knowledge','02_KNOWLEDGE_BASE_AUDIT_AND_CANONICAL_MODEL.md','The HTML is a presentation/export view',
    'Retain canonical JSON authoring and exact parsed JSON↔HTML parity. A viewer is not a second editable authority; parity proof does not independently verify content.')
put([332],'policy','05_POLICY_APPROVAL_AND_REVOCATION.md','Changing any bound field invalidates',
    'The invariant catalog describes a required digest-mismatch negative test, not a prior execution result. Retain denial whenever any action-bound input changes; full adapter-boundary enforcement is still unverified.')
put([355],'knowledge','02_KNOWLEDGE_BASE_AUDIT_AND_CANONICAL_MODEL.md','## 2.5',
    'Retain qualitative confidence labels as historical labels, not numerical probabilities. Legacy KB confidence is not evidence, verification or authorization.')
put([364,370,372,373,374,375,376,377,396],'release','13_RELEASE_AND_CHANGE_CONTROL.md','## 13.2',
    'Retain explicit human decision, exact candidate hash, rerun evidence, manifest and scope/exceptions before release-state change. An unchecked template is not approval; Phase0 approval does not alone authorize Phase1 or production.')
put([395],'template','13_RELEASE_AND_CHANGE_CONTROL.md','in-scope deliverables, prohibited work',
    'This is an unfilled attestation-template placeholder for exclusions. It does not itself name prohibited work or grant authority. The continuing requirement is explicit bounded implementation scope.','NON_NORMATIVE')
put([399,407],'historical_result','16_STATE_MACHINE_CONFORMANCE_MATRIX.md','## 16.1',
    'These are historical nested report counts219/237/497 and must remain tied to their original package. They are not additive unique runtime tests; canonical state-machine count differs and current235-suite results do not retroactively rerun old versions.','NON_NORMATIVE')
put([405],'execution','15_NORMATIVE_STATE_MACHINES.md','`failed_pre_effect` requires evidence',
    'Retain the retry-specific guard ordering: prove absence, preserve digest/key, increment attempt, allow retry class/budget and reauthorize. Generic reservation cannot bypass the retry guard.','EXTEND')
# Source documents have reviewed semantic roles. This mapping is deliberately explicit.
DOC_CURRENT={
'SCHEMA_FIELD_AUDIT.md':'docs/01_SCHEMA_AND_MIGRATION_POLICY.md',
'SCHEMA_FIELD_AUDIT_DEEP.md':'docs/01_SCHEMA_AND_MIGRATION_POLICY.md',
'SCHEMA_FIELD_AUDIT_RECURSIVE.md':'docs/01_SCHEMA_AND_MIGRATION_POLICY.md',
'SEVEN_TRACK_REVIEW_PLAN.md':'docs/00_COMPLETION_REPORT.md',
'SEVEN_TRACK_STATUS.md':'docs/00_COMPLETION_REPORT.md',
'TRACEABILITY_MASTER.md':'docs/13_RELEASE_AND_CHANGE_CONTROL.md',
'VERSIONING_AND_CHANGE_POLICY.md':'docs/01_SCHEMA_AND_MIGRATION_POLICY.md',
'CLAIM_SEMANTICS_AND_EPISTEMIC_LIFECYCLE.md':'docs/03_CLAIM_ONTOLOGY_AND_LIFECYCLE.md',
'CONFORMANCE_MATRIX.md':'docs/16_STATE_MACHINE_CONFORMANCE_MATRIX.md',
'CONSOLIDATION_AND_PHASE0_GATE.md':'docs/09_PHASE0_EXIT_CRITERIA.md',
'CONTRACT_CROSSWALK.md':'docs/01B_SCHEMA_FAMILY_CROSSWALK.md',
'DECISION_FREEZE_PROPOSAL.md':'docs/08_DECISION_REGISTER_FINAL.md',
'DECISION_REGISTER.md':'docs/08_DECISION_REGISTER_FINAL.md',
'DECISION_REVIEW_TABLE.md':'docs/08_DECISION_REGISTER_FINAL.md',
'KNOWLEDGE_BASE_CROSSWALK.md':'docs/02_KNOWLEDGE_BASE_AUDIT_AND_CANONICAL_MODEL.md',
'KNOWLEDGE_BASE_ITEM_AUDIT.md':'docs/02B_KNOWLEDGE_BASE_ITEM_DISPOSITION.md',
'PHASE0_GAPS_AND_EXIT.md':'docs/09_PHASE0_EXIT_CRITERIA.md',
'REFERENCE_FLOWS.md':'docs/10_REFERENCE_FLOWS.md',
'PHASE0_RELEASE_CANDIDATE.md':'docs/13_RELEASE_AND_CHANGE_CONTROL.md',
'CLOSURE_CANDIDATE.md':'docs/13_RELEASE_AND_CHANGE_CONTROL.md',
'RELEASE_ATTESTATION_TEMPLATE.md':'docs/13_RELEASE_AND_CHANGE_CONTROL.md',
'README.md':'docs/00_COMPLETION_REPORT.md',
}
CATEGORY_PATHS={
'claim':(['prototype/prain/scf.py','prototype/prain/durable_semantics.py'],['prototype/tests/test_scf_contract.py','prototype/tests/test_durable_semantics.py']),
'privacy':(['prototype/prain/private_projections.py'],['prototype/tests/test_production_privacy.py']),
'policy':(['prototype/prain/policy_gateway.py','prototype/prain/runtime.py'],['prototype/tests/test_production_runtime_auth.py','prototype/tests/test_runtime_hardening.py']),
'identity':(['prototype/prain/tenant_access.py'],['prototype/tests/test_tenant_privacy.py','prototype/tests/test_production_runtime_auth.py']),
'goal':(['prototype/prain/goal_registry.py','prototype/prain/secure_completion.py'],['prototype/tests/test_secure_completion_integration.py']),
'delivery':(['prototype/prain/scf_delivery.py','prototype/prain/scf_http.py'],['prototype/tests/test_production_multinode.py']),
'consistency':(['prototype/prain/durable_state_store.py','prototype/prain/fenced_leases.py'],['prototype/tests/test_durable_state_store.py','prototype/tests/test_fencing_hal_proposals.py']),
'execution':(['prototype/prain/dispatcher.py','prototype/prain/durable_admission.py'],['prototype/tests/test_dispatcher.py','prototype/tests/test_sqlite_fault_recovery.py']),
'state':(['prototype/prain/dispatcher.py'],['prototype/tests/test_dispatcher.py']),
'conformance':([],['prototype/tests/test_production_multinode.py','prototype/tests/test_production_security.py']),
'release':(['tools/verify_phase1_gates.py'],['prototype/tests/test_gate_validator.py']),
'boundary':(['tools/verify_phase1_gates.py'],['prototype/tests/test_gate_validator.py']),
'schema':([],['prototype/tests/test_scf_contract.py']),
}
CACHE={}
def read_source(path):
    if path not in CACHE:
        if path.startswith('historical_zip:'):
            archive,member=path[len('historical_zip:'):].split('!/',1)
            with zipfile.ZipFile(ROOT/archive) as z:CACHE[path]=z.read(member)
        else:CACHE[path]=(ROOT/path).read_bytes()
    return CACHE[path]
def ref(member,needle=None,heading=None):
    if not member.startswith(PREFIX):member=PREFIX+member
    if member not in CANON:return None
    data=CANON[member];lines=data.decode().splitlines()
    hits=[]
    if needle:hits=[i+1 for i,s in enumerate(lines) if needle in s]
    if not hits and heading:hits=[i+1 for i,s in enumerate(lines) if s.strip()==heading]
    line=hits[0] if hits else 1
    return {'archive':ARCH,'archive_sha256':sha(archive_bytes),'member':member,'sha256':sha(data),'line':line,'line_text':lines[line-1],'match':'REVIEWED_CLAUSE' if needle and hits else 'EXACT_HEADING' if heading and hits else 'REVIEWED_DOCUMENT_SCOPE'}
def context(lines,line):
    if lines[line-1].lstrip().startswith('#'):
        s=line-1;level=len(lines[s])-len(lines[s].lstrip('#'))
        e=next((i for i in range(s+1,len(lines)) if lines[i].startswith('#') and len(lines[i])-len(lines[i].lstrip('#'))<=level),len(lines))
    else:
        s=max(i for i in range(line) if i==0 or lines[i].startswith('#'))
        e=next((i for i in range(line,len(lines)) if lines[i].startswith('#')),len(lines))
    text='\n'.join(lines[s:e]);return {'start_line':s+1,'end_line':e,'sha256':sha(text.encode()),'text':text}
def anchors(paths):
    out=[]
    for p in paths:
        f=ROOT/p
        if f.exists():out.append({'path':p,'sha256':sha(f.read_bytes()),'proof_scope':'RELATED_CODE_OR_TEST_ONLY; behavior and complete requirement coverage not asserted'})
    return out
indices={x['text']:i for i,x in enumerate(UNIQUE)}
records=[];documents={};unmapped=[]
for row in ROWS:
    i=indices[row['text']];text=row['text'];source=row['source'];path=source['path'];name=Path(path).name
    data=read_source(path);lines=data.decode().splitlines();line=source['line'];assert lines[line-1].strip()==text
    scope=context(lines,line) if name.endswith('.md') else {'start_line':max(1,line-5),'end_line':min(len(lines),line+5),'text':'\n'.join(lines[max(0,line-6):line+5])}
    if 'sha256' not in scope:scope['sha256']=sha(scope['text'].encode())
    documents.setdefault(source['sha256'],{'representative_source':path,'sha256':source['sha256'],'source_occurrences':set(),'review_role':'Historical source read with candidate contexts; canonical contract scope controls obligations.'})['source_occurrences'].add(path)
    if i in D:
        cat,file,needle,rationale,disposition=D[i];current=ref('docs/'+file,needle)
        if disposition=='UNRESOLVED':missing='Record a versioned effective opaque-ID generation preference/requirement and collision/clock-rollback behavior; UUID preference does not conflict with schema URN identity.'
        elif disposition=='NON_NORMATIVE':missing='No independent runtime obligation from this record; related normative scope is retained in canonical reference.'
        else:missing='Full clause-specific runtime/operational or governance proof is not established by this semantic review. Related code/test anchors below are partial only; require exact boundary, negative cases and signed run evidence before implementation acceptance.'
        inherited=disposition!='NON_NORMATIVE'
    elif text.startswith('#'):
        disposition='NON_NORMATIVE';cat='document_navigation'
        member='docs/'+name if PREFIX+'docs/'+name in CANON else DOC_CURRENT.get(name,'docs/13_RELEASE_AND_CHANGE_CONTROL.md')
        current=ref(member,heading=text)
        rationale='Reviewed as Markdown navigation, not an assertion/guard: '+text+'. Its complete source section is preserved below. Obligations inside that section remain applicable according to the canonical successor; no normative body text is waived by disposing of the heading.'
        missing='No standalone implementation proof for a heading. All body/section obligations remain inherited; source section text and canonical scope are linked for clause-level runtime verification.';inherited=True
    elif '/audit/' in path:
        disposition='NON_NORMATIVE';cat='historical_audit_record';compat=source.get('current_canonical_compatibility',{});current=ref(compat.get('member','docs/11_SPEC_VALIDATION_BOUNDARY.md'),heading=text)
        rationale='Reviewed in a historical JSON audit result/source-assessment object (pointer '+str(source.get('json_pointer_context',{}).get('pointer'))+'). This stored diagnostic/assessment is descriptive evidence about that source artifact, not an independent authorization or a current successful runtime test. Any guard named in its detail remains a separate normative requirement of canonical policy/schema/state-machine contracts.'
        missing='Historical audit values are preserved, not re-executed or generalized. Require original-build rerun for the historical result and independent runtime conformance evidence for the named guard.';inherited=True
    elif text in ['| Status | Meaning | Permitted basis | Must not imply |','| Failure | Required protocol response | Must not happen |']:
        disposition='NON_NORMATIVE';cat='table_header';current=ref('docs/'+('03_CLAIM_ONTOLOGY_AND_LIFECYCLE.md' if text.startswith('| Status') else '07_HAL_RESILIENCE_AND_CONFORMANCE.md'))
        rationale='Reviewed as table column labels; no row transition, invariant or authorization is specified by this header alone. The associated semantic/status or failure rows remain independently binding.'
        missing='No independent behavior arises from column labels. Preserve and test substantive table rows.';inherited=True
    else:
        unmapped.append((i,row['requirement_id'],text));continue
    # Bind inherited obligations to normative source clauses, not diagnostic JSON.
    if cat=='historical_audit_record':
        audit_bindings={
          211:('01_SCHEMA_AND_MIGRATION_POLICY.md','Root `additionalProperties:false`'),
          212:('02_KNOWLEDGE_BASE_AUDIT_AND_CANONICAL_MODEL.md','The HTML is a presentation/export view'),
          213:('05_POLICY_APPROVAL_AND_REVOCATION.md','The policy gateway is the only component'),
          338:('02_KNOWLEDGE_BASE_AUDIT_AND_CANONICAL_MODEL.md','## 2.5'),
          339:('12_KNOWLEDGE_BASE_SOURCE_FACT_CHECK.md','## Method'),
          340:('05_POLICY_APPROVAL_AND_REVOCATION.md','`defer` is non-permit'),
          341:('15_NORMATIVE_STATE_MACHINES.md','missing/extra approvals'),
          342:('05_POLICY_APPROVAL_AND_REVOCATION.md','Approval is an explicit record bound'),
          343:('05_POLICY_APPROVAL_AND_REVOCATION.md','revocation epoch changes'),
          344:('04_IDENTITY_TENANCY_AND_AUTHORITY.md','Every authoritative data record'),
          345:('02_KNOWLEDGE_BASE_AUDIT_AND_CANONICAL_MODEL.md','## 2.5'),
          402:('13_RELEASE_AND_CHANGE_CONTROL.md','`tests/invariant_coverage.json` reports'),
          408:('15_NORMATIVE_STATE_MACHINES.md','new immutable decision'),
          409:('15_NORMATIVE_STATE_MACHINES.md','new immutable decision'),
        }
        assert i in audit_bindings,(i,text)
        file,needle=audit_bindings[i];current=ref('docs/'+file,needle)
    if cat=='document_navigation':
        schema_match=re.search(r'`([^`]+)\.schema\.json`',text)
        family=schema_match.group(1).split('/')[-1] if schema_match else None
        family={'action-request':'action-command','action-result':'execution-receipt','state-snapshot':'state-record','event-envelope':'message-envelope','evidence':'evidence-record'}.get(family,family)
        if family and PREFIX+'contracts/'+family+'.schema.json' in CANON:
            current=ref('contracts/'+family+'.schema.json');current['json_pointer']=''
        elif current and current['member'].endswith('.md'):
            # Retain the complete canonical section, including every substantive
            # paragraph/row, as an OPEN inherited obligation rather than a title.
            clines=CANON[current['member']].decode().splitlines();start=current['line']-1
            heading=clines[start]
            level=len(heading)-len(heading.lstrip('#')) if heading.startswith('#') else 6
            end=next((j for j in range(start+1,len(clines)) if clines[j].startswith('#') and len(clines[j])-len(clines[j].lstrip('#'))<=level),len(clines))
            first=next((j for j in range(start+1,end) if clines[j].strip() and not clines[j].startswith('#')),start)
            current['section_start_line']=start+1;current['section_end_line']=end
            current['line']=first+1;current['line_text']=clines[first]
            current['match']='REVIEWED_CANONICAL_SECTION_WITH_OPEN_BODY_OBLIGATIONS'
    code,test=CATEGORY_PATHS.get(cat,([],[]))
    record={'requirement_id':row['requirement_id'],'text':text,'text_sha256':row['text_sha256'],'source':source,'source_context':scope,
       'reviewer':'normative_c','review_method':'CONTEXT_REVIEW_WITH_EXPLICIT_TEXT_DECISIONS_AND_SOURCE_ROLE','effective_disposition':disposition,'disposition':disposition,
       'semantic_category':cat,'rationale':rationale,'canonical_successor':current,'canonical_reference':current,'implementation_status':('NOT_APPLICABLE' if disposition=='NON_NORMATIVE' else 'PARTIAL' if code else 'OPEN'),'inherited_section_obligations_preserved':inherited,
       'related_implementation':anchors(code),'related_tests':anchors(test),'missing_proof':missing,
       'implementation_acceptance':'NOT_GRANTED','production_acceptance':False,'human_signoff':False}
    record['inherited_obligations']=[{'canonical_reference':current,'implementation_status':'OPEN',
       'scope':'All substantive guards/constraints of the referenced complete schema or reviewed canonical section remain mandatory; no acceptance is inferred from navigation/diagnostic disposition.'}] if inherited else []
    if i==104:
        record['normative_strength']='ADVISORY_GENERATION_PREFERENCE_WITH_REQUIRED_COLLISION_AND_ORDERING_SAFETY'
        record['missing_proof']='Prove the chosen ID generation profile handles collisions/clock rollback and does not use UUID/timestamps as aggregate authority; retain compatibility of legacy opaque IDs. No full generator proof imported.'
    if i==67:
        record['superseded_fragment']='The old proposed proposition-layout/field union is replaced by the canonical claim contract.'
        record['retained_guard']='If statement and subject/predicate/object coexist, their semantics must be consistent. Contradictory representations require quarantine/review; schema shape validity alone cannot accept them.'
        record['retained_guard_status']='OPEN'
        record['missing_proof']='Implement and negatively test statement-versus-SPO semantic consistency before accepting mixed legacy propositions; no preservation or schema validation alone proves this guard.'
    if i in [299,361,367,383,392]:
        record['superseded_fragment']='The version-specific historical NOT_APPROVED candidate state and candidate-version instructions are replaced by the later canonical Phase0 release record.'
        record['retained_guard']='Specification closure, separate explicit implementation authorization and production acceptance remain distinct; retain exact hash, dated owner decision and test evidence.'
        record['retained_guard_status']='OPEN_CURRENT_RELEASE_EVIDENCE_REQUIRED'
        record['canonical_reference']=record['canonical_successor']=ref('docs/13_RELEASE_AND_CHANGE_CONTROL.md','2. **Phase-0 closed**')
        record['inherited_obligations'][0]['canonical_reference']=record['canonical_reference']
    # Cross-review remediation: bind actual canonical body clauses, not only
    # a generic inheritance assertion. Keep every referenced clause OPEN.
    if inherited and current:
        member=record['canonical_reference']['member']
        raw=CANON[member]
        if member.endswith('.schema.json'):
            record['inherited_obligations']=[{'canonical_reference':record['canonical_reference'],
                'json_pointer':'', 'constraint_sha256':sha(raw), 'implementation_status':'OPEN',
                'scope':'Complete immutable canonical schema; every required field and conditional applies.'}]
        else:
            body=raw.decode().splitlines()
            anchor=record['canonical_reference']['line']-1
            start=max([j for j in range(anchor+1) if body[j].startswith('#')],default=0)
            level=len(body[start])-len(body[start].lstrip('#')) if body[start].startswith('#') else 1
            end=next((j for j in range(start+1,len(body)) if body[j].startswith('#') and len(body[j])-len(body[j].lstrip('#'))<=level),len(body))
            obligations=[]
            for j in range(start,end):
                if not body[j].strip() or body[j].startswith('#'):continue
                location=dict(record['canonical_reference']); location.update(line=j+1,line_text=body[j])
                obligations.append({'canonical_reference':location,'text':body[j],
                    'text_sha256':sha(body[j].encode()),'implementation_status':'OPEN',
                    'role':'PRESERVED_BODY_CLAUSE_REQUIRES_CONTEXTUAL_PROOF'})
            record['inherited_obligations']=obligations
    if record.get('retained_guard'):
        record['inherited_obligations'].append({'source_reference':source,
            'text':record['retained_guard'],'implementation_status':'OPEN',
            'scope':'Retained operative guard is not superseded with historical representation/status.'})
    records.append(record)
assert not unmapped,unmapped
assert len(records)==1300
assert {r['requirement_id'] for r in records}=={f'RTM-{i:05d}' for i in range(2501,3801)}
(OUT/'part_c.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False,sort_keys=True)+'\n' for x in records))
for d in documents.values():d['source_occurrences']=sorted(d['source_occurrences'])
(OUT/'part_c_source_dossiers.json').write_text(json.dumps(list(documents.values()),ensure_ascii=False,indent=2)+'\n')
summary={'partition':'RTM-02501..RTM-03800','rows':len(records),'distinct_texts_reviewed':len(UNIQUE),'distinct_source_contents':len(documents),
 'dispositions':dict(collections.Counter(r['effective_disposition'] for r in records)),
 'semantic_categories':dict(collections.Counter(r['semantic_category'] for r in records)),
 'all_source_lines_exact':True,'canonical_archive_sha256':sha(archive_bytes),'unresolved':[{'id':r['requirement_id'],'text':r['text'],'missing_proof':r['missing_proof']} for r in records if r['effective_disposition']=='UNRESOLVED'],
 'implementation_accepted':0,'production_accepted':False,
 'method_limits':['Navigation/audit rows have no independent runtime behavior; their full source context and inherited obligations are preserved.','Explicit decisions do not grant behavioral acceptance.','Canonical source records and references are version dispositions, not independent verification of historical owner approval.','Related code/test files are anchors only, not exact complete coverage or passing run evidence.']}
(OUT/'part_c_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(summary,indent=2))
