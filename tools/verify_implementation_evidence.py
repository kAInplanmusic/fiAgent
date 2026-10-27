"""Rebuild evidence anchors for all RTM IDs without granting release acceptance.

A verified anchor proves source identity/existence, not behavior or normative
approval. Test execution is imported only from an explicit JSON test-run record.
"""
from __future__ import annotations
import argparse, ast, collections, csv, hashlib, io, json, pathlib, re, zipfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
def sha(data): return hashlib.sha256(data).hexdigest()
def rows(path):
    with path.open(encoding='utf8',newline='') as f:return list(csv.DictReader(f))
def read_source(path):
    if path.startswith('historical_zip:'):
        spec=path[len('historical_zip:'):]; outer,member=spec.split('!/',1)
        data=(ROOT/outer).read_bytes()
        with zipfile.ZipFile(io.BytesIO(data)) as z: payload=z.read(member)
        return payload,{'container':outer,'container_sha256':sha(data),'member':member}
    p=ROOT/path
    if p.is_file():return p.read_bytes(),{}
    raise FileNotFoundError(path)
def anchors(path):
    p=ROOT/path
    if not p.is_file():return []
    data=p.read_bytes();result=[]
    if p.suffix=='.py':
        tree=ast.parse(data)
        def walk(nodes,prefix=''):
            for n in nodes:
                if isinstance(n,(ast.ClassDef,ast.FunctionDef,ast.AsyncFunctionDef)):
                    name=prefix+n.name
                    result.append({'path':path,'symbol':name,'line':n.lineno,'end_line':n.end_lineno,'sha256':sha(data)})
                    if isinstance(n,ast.ClassDef):walk(n.body,name+'.')
        walk(tree.body)
    else:result=[{'path':path,'line':1,'sha256':sha(data)}]
    return result
# Each row below was inspected as an obligation. Evidence is explicitly partial;
# remaining clauses are retained rather than erased by a file-existence check.
ASSESSMENTS={
1:'Inventory is available; completeness against every historical release must be established, not inferred from a checkbox.',
2:'Historical artifacts remain in archive; source hashes bind this run, but do not establish absence of prior overwrites.',
3:'Per-source checksums exist; purpose, version and canonical successor coverage remains incomplete.',
4:'Supplied archive CRC/hash evidence exists; all master-history archive membership requires separate package checks.',
5:'Original clauses and candidates preserved; complete semantic migration decisions remain unresolved.',
6:'P/R/A/I/N roles are specified; documented architecture does not prove full runtime implementation.',
7:'SCF/HAL/invariant layers specified; runtime implements bounded local subsets.',
8:'Audit documents are archival evidence, not runtime verification of their conclusions.',
9:'State-machine and schema crosswalk exists; exhaustive runtime-transition conformance remains missing.',
10:'RTM exists and preserves IDs; incomplete normative/implementation evidence prevents closure.',
11:'This verifier checks source and AST anchors; all cross-document IDs/semantic links are broader than this check.',
12:'Exact duplicate groups preserve lineage; duplicate text does not resolve contradictory normative contexts.',
13:'Current strict gate file rejects acceptance; historical status labels are not uniformly reconciled.',
14:'Historical v1.1.0 test-count claim requires execution of that archived build, not current suite count.',
15:'310/319/325 count claims require suite/version/run identities; current tests cannot substantiate them.',
16:'Existing release verifier binds prototype; all historical integrity claims need archive-by-archive verification.',
17:'Master/prototype manifests exist; pending changed tree requires regenerated current manifest.',
18:'Current verifier supports integrity checks; reproducible clean package and CI equivalence need run evidence.',
19:'This report separates anchors and execution; no production pass is granted.',
20:'Vertical runtime path emits evidence and simulated receipts; does not prove actual external effect.',
21:'Reference state/goal/policy/ledger components and tests exist; limited prototype scope retained.',
22:'Historical 23-test result is not replaced with current test count; historical rerun still needed.',
23:'SCF ingress validates a local v1 claim subset; complete canonical Phase0 model enforcement remains missing.',
24:'Negative schema tests exist for SCF/wire; all canonical families/round-trip/migrations remain incomplete.',
25:'Local state/goal/CAS checks exist; normative automata/property/mutation coverage is incomplete.',
26:'Targeted auth/approval/idempotency/unknown tests exist; combined distributed race coverage remains partial.',
27:'Detached ledger payload tests verify aliases; independent anchors and archival mutation proof still separate.',
28:'Criterion-specific checks and atomic secure completion exist; issuer authentication/production integration separate.',
29:'Python baseline described; supported-version matrix and reproducible environment require run evidence.',
30:'SQLite persistence implemented; stable versioned storage interface and full migrations not established.',
31:'Crash/restart tests exercise persisted components; production outage and recovery objectives remain separate.',
32:'Local durable outbox/inbox and unknown-state handling exist; full DLQ/broker retry system not established.',
33:'Durable UNKNOWN plus evidence-required reconciliation tested; reconciliation truth depends on trusted evidence.',
34:'Single-use admission is atomic locally; full authenticated approval issuer/provenance model incomplete.',
35:'Backup/restore and projection retention tests exist; global deletion and migration rollback coverage incomplete.',
36:'HTTP adapter exists; interchangeable transport interface and alternative implementation contract suite incomplete.',
37:'SQLite is implemented; PostgreSQL remains a candidate rather than a claimed tested backend.',
38:'Durable leases/fencing/inbox/outbox exist; actual protected external-adapter fencing and conflict resolution incomplete.',
39:'State CAS and scoped projections exist; distributed authoritative/projection consistency needs integration proof.',
40:'Spawned TLS-node fault tests add process isolation; split-brain, reorder and real two-host suite incomplete.',
41:'SCF retains provenance/conflicts/dependencies; L0-L3 selective sync and canonical graph incomplete.',
42:'Durable-state/process tests exist; two real hosts remain an operational prerequisite.',
43:'Tenant access and authenticated action entry exist; all mutation/admin paths not yet verified.',
44:'Approval checks bind selected fields; full issuer/nonce/principal/context binding incomplete.',
45:'Local admission transaction exists; revoke-versus-external-effect distributed atomicity not proven.',
46:'Projection classification/retention/tombstone controls exist; originals/logs/embeddings/caches lack end-to-end enforcement.',
47:'Nested projection secret rejection exists; entire logs/events/receipt/ledger pipeline remains unverified.',
48:'Threat boundaries specified historically; current independent technical review and abuse cases required.',
49:'Runtime simulates effects; a successful receipt is not proof of external execution or deployment authorization.',
50:'Correlation evidence exists locally; privacy-aware structured metrics/log export incomplete.',
51:'HAL health states and stale/unknown tested; deployment telemetry freshness/SLO scope remains partial.',
52:'HAL proposals do not self-execute; actual authorized canary/repair/rollback workflow incomplete.',
53:'Budget/cooldown proposal bounds exist; end-to-end adaptation rollback and high-risk approvals not implemented.',
54:'Durable budget/cooldown exists; operator stop/dashboard/alerts and measured failure budget incomplete.',
55:'SemanticRouter backend metadata exists; all versioned provider/compute capabilities interfaces incomplete.',
56:'Routing contract tests exist; two implementations per adapter family not proven.',
57:'Routing constraints tested; provider migration preserving semantic/evidence contracts needs full contract suite.',
58:'Quantum-ready remains replaceable-interface intent; simulator/adapter suite not established.',
59:'No measured quantum advantage is claimed by this assessment; positive provider requirements still open.',
60:'Security/privacy/network-process/fault tests present; load/chaos/real-two-host full coverage missing.',
61:'Failure/recovery specification exists; executable deployment/operator runbooks not fully verified.',
62:'Resource routing and retry limits partial; measured SLO/alert/incident/cost-control operations incomplete.',
63:'Independent agent technical review can supply evidence; qualified external/owner review not fabricated.',
64:'Source/anchor hashes generated; final reproducible RC build remains separate required evidence.',
65:'Explicit human production acceptance is external; user request to implement does not impersonate release signature.',
66:'Historical count discrepancy preserved; current run does not retroactively rerun that build.',
67:'Strict gate remains not accepted; complete historical-status reconciliation still needed.',
68:'Full candidate inventory exists; extraction/source verification does not complete individual normative acceptance.',
69:'Version-description table row is historical information, not a runtime obligation.'}
# Explicit per-obligation mappings, selected by inspection rather than keywords.
GROUPS=[
([1,2,3,4,5,10,11,12,13,14,15,16,17,18,19,64,66,67,68],['tools/verify_phase1_gates.py','tools/verify_phase1_import.py','tools/finalize_69_references.py','prototype/tools/verify_release.py'],['prototype/tests/test_final_69_references.py','prototype/tests/test_release_integrity.py','prototype/tests/test_rtm_workpackages.py']),
([6,7,8,9],['prototype/prain/runtime.py','prototype/prain/scf.py','prototype/prain/anima_hal.py'],['prototype/tests/test_architecture_alignment.py','prototype/tests/test_architecture_wiring.py']),
([20,21,22,25,26,27,28,49],['prototype/prain/runtime.py','prototype/prain/goal_registry.py','prototype/prain/evidence_ledger.py','prototype/prain/secure_completion.py'],['prototype/tests/test_runtime.py','prototype/tests/test_runtime_hardening.py','prototype/tests/test_secure_completion_integration.py','prototype/tests/test_phase1.py']),
([23,24],['prototype/prain/scf_contract.py','prototype/prain/scf_wire.py'],['prototype/tests/test_scf_contract.py','prototype/tests/test_scf_wire.py','prototype/tests/test_scf_http.py']),
([30,31,32,33,34,35,38,39],['prototype/prain/durable_admission.py','prototype/prain/durable_state_store.py','prototype/prain/durable_components.py','prototype/prain/fenced_leases.py','prototype/prain/backup_bundle.py'],['prototype/tests/test_durable_admission.py','prototype/tests/test_sqlite_fault_recovery.py','prototype/tests/test_durable_components.py','prototype/tests/test_fencing_hal_proposals.py','prototype/tests/test_backup_bundle.py']),
([36,40,41,42,60],['prototype/prain/scf_http.py','prototype/prain/scf_http_dispatcher.py','prototype/prain/scf_delivery.py','prototype/prain/durable_semantics.py'],['prototype/tests/test_production_multinode.py','prototype/tests/test_production_security.py','prototype/tests/test_scf_delivery.py','prototype/tests/test_durable_semantics.py']),
([43,44,45],['prototype/prain/runtime.py','prototype/prain/tenant_access.py','prototype/prain/policy_gateway.py','prototype/prain/durable_admission.py'],['prototype/tests/test_tenant_privacy.py','prototype/tests/test_phase1.py','prototype/tests/test_durable_admission.py']),
([46,47],['prototype/prain/private_projections.py'],['prototype/tests/test_production_privacy.py','prototype/tests/test_tenant_privacy.py']),
([51,52,53,54],['prototype/prain/anima_hal.py','prototype/prain/durable_hal_proposals.py'],['prototype/tests/test_anima_hal_contract.py','prototype/tests/test_durable_hal_proposals.py']),
([55,56,57,62],['prototype/prain/semantic_router.py'],['prototype/tests/test_semantic_router.py']),
([29,37,48,50,58,59,61,63,65,69],[],[])]
MAP={n:{'implementation_paths':code,'test_paths':tests} for ns,code,tests in GROUPS for n in ns}
def json_spans(data):
    """JSON-pointer ranges for exact source rows, using a lexical recursive parser."""
    text=data.decode('utf8'); decoder=json.JSONDecoder(); spans=[]
    def ws(i):
        while i<len(text) and text[i].isspace():i+=1
        return i
    def parse(i,pointer,start=None):
        i=ws(i); begin=i if start is None else start
        if text[i]=='{':
            i=ws(i+1); value={}
            while text[i]!='}':
                key_start=i; key,j=decoder.raw_decode(text,i);j=ws(j)
                if text[j]!=':':raise ValueError('json_colon')
                child=pointer+'/'+str(key).replace('~','~0').replace('/','~1')
                val,i=parse(j+1,child,key_start);value[key]=val;i=ws(i)
                if text[i]==',':i=ws(i+1)
                elif text[i]!='}':raise ValueError('json_object_delimiter')
            end=i+1
        elif text[i]=='[':
            i=ws(i+1);value=[]
            while text[i]!=']':
                val,i=parse(i,pointer+'/'+str(len(value)));value.append(val);i=ws(i)
                if text[i]==',':i=ws(i+1)
                elif text[i]!=']':raise ValueError('json_array_delimiter')
            end=i+1
        else:value,end=decoder.raw_decode(text,i)
        spans.append({'pointer':pointer,'start_line':text.count('\n',0,begin)+1,'end_line':text.count('\n',0,end)+1,'value':value})
        return value,end
    parse(0,'');return spans

def pointer_context(spans,line):
    eligible=[v for v in spans if v['start_line']<=line<=v['end_line']]
    if not eligible:return None
    value=min(eligible,key=lambda v:(v['end_line']-v['start_line'],-v['pointer'].count('/')))
    tail=value['pointer'].rsplit('/',1)[-1]
    annotations={'description','title','$schema','$id','$comment','examples','default'}
    return {'pointer':value['pointer'],'start_line':value['start_line'],'end_line':value['end_line'],'json_value_sha256':sha(json.dumps(value['value'],sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()),'schema_role':'ANNOTATION_OR_METADATA' if tail in annotations else 'STRUCTURAL_OR_VALIDATION_NODE','scope':'Located JSON node only; no independent normative acceptance.'}

def canonical_sources():
    """Bind only bytes/text to latest specification; never infer supersession."""
    name='archive/PRAIN_v0.99.6_Phase0_Green_Closure.zip'
    data=(ROOT/name).read_bytes(); result={}
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for member in z.namelist():
            if member.endswith(('.md','.json')):
                payload=z.read(member);relative=member.split('/',1)[1]
                result[relative]={'archive':name,'archive_sha256':sha(data),'member':member,'sha256':sha(payload),'bytes':payload,'lines':payload.decode('utf8').splitlines()}
    return result

def canonical_binding(path,payload,line_text,current):
    suffix=None
    for marker in ('/contracts/','/docs/','/knowledge_base/'):
        if marker in path:suffix=marker[1:]+path.rsplit(marker,1)[1];break
    if suffix is None:
        base=path.rsplit('/',1)[-1];matches=[k for k in current if k.rsplit('/',1)[-1]==base]
        if len(matches)==1:suffix=matches[0]
    doc=current.get(suffix)
    if not doc:return {'status':'NO_UNAMBIGUOUS_CURRENT_SOURCE_MATCH','normative_acceptance':False}
    matches=[i for i,v in enumerate(doc['lines'],1) if v.strip()==line_text]
    status='CURRENT_SOURCE_BYTES_IDENTICAL' if payload==doc['bytes'] else ('CURRENT_SOURCE_LINE_EXACT' if matches else 'CURRENT_SOURCE_LINE_CHANGED_OR_ABSENT')
    return {k:v for k,v in doc.items() if k not in ('bytes','lines')} | {'status':status,'line_candidates':matches,'normative_acceptance':False,'scope':'Source-compatibility binding only; does not establish effective normative decision or runtime conformance.'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=pathlib.Path,default=ROOT/'TRACEABILITY/IMPLEMENTATION_EVIDENCE_20261025');ap.add_argument('--test-results',type=pathlib.Path);args=ap.parse_args();out=args.output;out.mkdir(parents=True,exist_ok=True)
    rtm=rows(ROOT/'TRACEABILITY/REQUIREMENT_TRACEABILITY_MATRIX.csv');wp={r['requirement_id']:r for r in rows(ROOT/'TRACEABILITY/RTM_5071_EVIDENCE_WORKPACKAGES.csv')}
    fixes={r['requirement_id']:r for r in rows(ROOT/'TRACEABILITY/RTM_69_FINAL_REFERENCE_RESOLUTION.csv')}
    cache={};first={};records=[];source_fail=[];index={};current=canonical_sources();spans_cache={}
    for row in rtm:
        uid=row['requirement_id'];n=int(uid[4:]);w=wp[uid];text=row['normalized_requirement'].strip();h=sha(text.encode());dup=first.setdefault(h,uid)
        source=w['source'];line=int(w['locator'].split()[-1]);source_record={'path':source,'line':line}
        try:
            if source not in cache:cache[source]=read_source(source)
            payload,extra=cache[source];lines=payload.decode('utf8').splitlines()
            if not 1<=line<=len(lines):raise ValueError('source_line_out_of_range')
            actual=lines[line-1].strip();exact=actual==text
            source_record.update(extra);source_record.update(sha256=sha(payload),line_sha256=sha(actual.encode()),exact=exact)
            source_record['current_canonical_compatibility']=canonical_binding(source,payload,text,current)
            if source.endswith('.json'):
                if source not in spans_cache:spans_cache[source]=json_spans(payload)
                source_record['json_pointer_context']=pointer_context(spans_cache[source],line)
            if not exact:source_fail.append(uid)
        except Exception as e:source_record.update(exact=False,error=type(e).__name__+':'+str(e));source_fail.append(uid)
        mapping=MAP.get(n,{'implementation_paths':[],'test_paths':[]})
        for path in mapping['implementation_paths']+mapping['test_paths']:
            if path not in index:index[path]=anchors(path)
        code=[a for p in mapping['implementation_paths'] for a in index[p]]
        tests=[a for p in mapping['test_paths'] for a in index[p] if a.get('symbol','').split('.')[-1].startswith('test_')]
        if n<=69:
            decision='RETAIN_WORK_OBLIGATION' if n!=69 else 'NON_NORMATIVE_SOURCE_DESCRIPTION';rationale=ASSESSMENTS[n]
            review='OBLIGATION_ASSESSED_WITH_EXPLICIT_REMAINING_SCOPE'
        else:
            decision='OPEN_EFFECTIVE_NORMATIVE_VERSION';review='SOURCE_AND_DUPLICATE_REVIEW_ONLY'
            rationale='Exact source clause retained. Whole-source normative/version adjudication and code/test obligation mapping not completed; no acceptance transferred from identical text in another version.'
        records.append({'requirement_id':uid,'text':text,'text_sha256':h,'source':source_record,'source_category':w['semantic_proposal'],'workstream':w['workstream'],'gate':w['gate'],'exact_text_group_first_id':dup,'is_duplicate_candidate':dup!=uid,'disposition':decision,'review_scope':review,'rationale':rationale,'implementation_anchors':code,'test_anchors':tests,'behavioral_test_evidence':'NOT_IMPORTED','implementation_acceptance':'PARTIAL_ANCHORS_ONLY' if code else 'NOT_VERIFIED','production_acceptance':'NOT_ACCEPTED','independent_signoff':'NOT_IMPORTED'})
    assert len(records)==5071 and {r['requirement_id'] for r in records}=={f'RTM-{i:05d}' for i in range(1,5072)}
    (out/'requirement_evidence.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in records))
    (out/'anchor_index.json').write_text(json.dumps(index,indent=2,sort_keys=True)+'\n')
    missing=[{'requirement_id':r['requirement_id'],'remaining_scope':r['rationale'],'gate':r['gate']} for r in records if r['requirement_id']!='RTM-00069']
    (out/'missing_proof.json').write_text(json.dumps(missing,ensure_ascii=False,indent=2)+'\n')
    summary={'candidates':len(records),'source_exact':len(records)-len(source_fail),'source_failures':source_fail,'unique_text_groups':len(first),'exact_duplicate_candidates':sum(r['is_duplicate_candidate'] for r in records),'focal_obligations_assessed':68,'historical_context_rows_assessed':1,'historical_source_only_unadjudicated':5002,'fully_normatively_accepted':0,'fully_implementation_accepted':0,'production_accepted':False,'anchor_paths':len(index),'test_anchors':sum(a.get('symbol','').split('.')[-1].startswith('test_') for v in index.values() for a in v),'json_pointer_context_rows':sum(bool(r['source'].get('json_pointer_context')) for r in records), 'canonical_compatibility_counts':dict(collections.Counter(r['source'].get('current_canonical_compatibility',{}).get('status','SOURCE_UNREADABLE') for r in records)), 'source_bytes_sha256':{p:sha(v[0]) for p,v in sorted(cache.items())},'limitations':['No behavioral pass inferred from AST/file existence.','No acceptance transferred across exact-text duplicates.','5002 historical candidate rows require effective-version and clause-level semantic adjudication.','Focal mappings are partial and do not close any obligation.','No external or human release signature fabricated.']}
    if args.test_results:summary['provided_test_results_sha256']=sha(args.test_results.read_bytes());summary['provided_test_results']=json.loads(args.test_results.read_text())
    (out/'verification_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
    report=['# PRAIN implementation evidence checkpoint','',
        'This is an auditable partial checkpoint. It is not a production release approval.', '',
        'Rebuild from the repository root: `python3 tools/verify_implementation_evidence.py`.',
        'Exit zero means every one of the 5,071 candidate IDs resolves to the exact recorded source line. It does not mean all requirements are implemented or accepted.', '',
        'All code/test anchors are AST-located with current file SHA-256 values. Test existence is not a passing test result. Rebuild after source changes to avoid stale anchors.', '',
        'Current specification comparison binds archive/PRAIN_v0.99.6_Phase0_Green_Closure.zip by SHA-256 and compares whole-file bytes or exact lines. Exact text in a changed document cannot resolve normative context, migration semantics or supersession.', '',
        'The 1,825 JSON-derived candidates include exact JSON pointer/range/hash metadata. Structural keywords and annotations are distinguished as source context only.', '',
        'The 5,002 historical candidates remain unadjudicated at the effective-version/normative level. Their source identity, duplicate group and canonical compatibility are verified. No obligation has been closed by reclassification.', '',
        '## Focal obligation assessment','',
        '| Requirement | Source | Code paths | Test anchors | Remaining scope |',
        '|---|---|---:|---:|---|']
    for r in records[:69]:
        code_paths=len({a['path'] for a in r['implementation_anchors']})
        report.append('| '+r['requirement_id']+' | '+r['source']['path']+':'+str(r['source']['line'])+' | '+str(code_paths)+' | '+str(len(r['test_anchors']))+' | '+r['rationale'].replace('|','/')+' |')
    report+=['','## Machine-readable outputs','',
        '- `requirement_evidence.jsonl`: every ID and exact source/code/test anchors; no omitted historical candidates.',
        '- `anchor_index.json`: deduplicated AST/document anchors with content hashes.',
        '- `missing_proof.json`: per-ID proof still required.',
        '- `verification_summary.json`: counts, source hashes and explicit acceptance limits.', '',
        'Production remains blocked by complete canonical schema/graph/migrations, authenticated mutation/admin boundaries, raw/derived/backup end-to-end deletion, distributed external-adapter fencing and policy races, actual two-host operations, HAL canary/rollback, adapter interchangeability, deployment/SLO evidence and authorized final signoff.']
    (out/'README.md').write_text('\n'.join(report)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in summary.items() if k!='source_bytes_sha256'},indent=2));return 1 if source_fail else 0
if __name__=='__main__':raise SystemExit(main())
