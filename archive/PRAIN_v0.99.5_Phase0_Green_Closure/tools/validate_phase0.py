#!/usr/bin/env python3
"""Offline specification artefact validator. Not an agent runtime."""
from pathlib import Path
import json, re, sys, hashlib, zipfile
from jsonschema.validators import validator_for
from jsonschema import FormatChecker
ROOT=Path(__file__).resolve().parents[1]
ERRORS=[]; CHECKS=[]
def check(name, condition, detail=''):
    CHECKS.append({'name':name,'status':'PASS' if condition else 'FAIL','detail':detail})
    if not condition: ERRORS.append(name+(': '+detail if detail else ''))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
# Canonical schema meta-validation and strictness.
canonical={p.stem.replace('.schema',''):p for p in (ROOT/'contracts').glob('*.schema.json')}
for name,p in sorted(canonical.items()):
    try:
        s=json.loads(p.read_text(encoding='utf-8')); validator=validator_for(s); validator.check_schema(s)
        check('canonical_schema_meta:'+name,True)
        check('canonical_schema_strict:'+name,s.get('additionalProperties') is False,'root additionalProperties must be false')
        fixture=json.loads((ROOT/'tests/contract_fixtures.json').read_text(encoding='utf-8'))['valid'][name]
        errs=list(validator(s,format_checker=FormatChecker()).iter_errors(fixture))
        check('canonical_fixture_valid:'+name,not errs,'; '.join(e.message for e in errs[:3]))
        # strict additionalProperties negative mutation
        bad=dict(fixture); bad['__unexpected_field__']=True
        errs2=list(validator(s,format_checker=FormatChecker()).iter_errors(bad))
        check('canonical_reject_unknown:'+name,bool(errs2),'schema should reject unknown root property')
    except Exception as e: check('canonical_schema_parse:'+name,False,str(e))
# Canonical negative fixtures.
fx=json.loads((ROOT/'tests/contract_fixtures.json').read_text(encoding='utf-8'))
for name,case in fx.get('invalid',{}).items():
    schema_name=case['schema']; s=json.loads(canonical[schema_name].read_text(encoding='utf-8')); base=dict(fx['valid'][schema_name]); mutation=case.get('mutation',{})
    # for status-specific fixtures, mutate only requested fields; deletion by null/removal keys.
    base.update(mutation)
    if name=='claim_confidence_without_method': base.pop('confidence_method',None)
    if name=='verified_claim_without_verification_ref': base.pop('verification_ref',None); base['epistemic_status']='verified'; base['verification_status']='passed'
    if name=='unknown_execution_without_reconciliation': base.pop('reconciliation',None); base['status']='unknown'
    if name=='command_message_missing_idempotency': base['message_type']='command'; base.pop('idempotency_key',None); base.pop('recipient_principal_id',None); base.pop('expires_at',None)
    if name=='delegation_without_target_scope': base['target_scope']={}
    if name=='refuted_claim_without_refutation': base['epistemic_status']='refuted'; base['verification_status']='failed'; base['refutation_refs']=[]
    if name=='bad_timestamp': base['updated_at']='not-a-timestamp'
    if name=='hal_policy_change_without_approval_ref': base['repair_class']='policy_change'; base['requires_human_approval']=True; base['status']='approved'; base['policy_decision_ref']='decision:1'; base.pop('approval_refs',None)
    errs=list(validator_for(s)(s,format_checker=FormatChecker()).iter_errors(base))
    check('negative_fixture:'+name,bool(errs),'expected invalid, schema accepted it')
# historical schema meta-validation.
historical=ROOT/'sources'
hcount=0
for zname in ['PRAIN_Phase0_v0.2.1.zip','PRAIN_Architecture_v0.4.0.zip','PRAIN_Distributed_Protocol_v0.5.0.zip','PRAIN_v0.6.zip']:
    with zipfile.ZipFile(historical/zname) as z:
        bad=z.testzip(); check('source_archive_integrity:'+zname,bad is None,str(bad or ''))
        for n in z.namelist():
            if n.endswith('.schema.json'):
                try:
                    s=json.loads(z.read(n).decode('utf-8')); validator_for(s).check_schema(s); good=True; detail=''
                except Exception as e: good=False; detail=str(e)
                check('historical_schema_meta:'+n,good,detail); hcount+=1
check('historical_schema_count_20',hcount==20,f'count={hcount}')
# Ensure all included validation/release tools are syntactically valid Python.
try:
    tool_files=sorted((ROOT/'tools').glob('*.py'))
    for tool_path in tool_files:
        compile(tool_path.read_text(encoding='utf-8'), str(tool_path), 'exec')
    check('all_validation_tools_parse', bool(tool_files), f'parsed={len(tool_files)}')
except Exception as e:
    check('all_validation_tools_parse', False, str(e))
# Knowledge base parity: parse DB literal via JavaScript object JSON serialization form embedded in generated HTML.
kb=json.loads((ROOT/'knowledge_base/PRAIN_Wissensdatenbank.v0.3.0.json').read_text(encoding='utf-8'))
html=(ROOT/'knowledge_base/PRAIN_interaktive_Wissensdatenbank.v0.3.0.html').read_text(encoding='utf-8')
m=re.search(r'const DB\s*=\s*(\{.*?\n\};)',html,re.S)
try: embedded=json.loads(m.group(1).rstrip().rstrip(';')) if m else None
except Exception as e: embedded=None
check('knowledge_base_html_embedded_db_parses',embedded is not None,str('DB not parsed' if embedded is None else ''))
check('knowledge_base_json_equals_html',embedded==kb,'canonical JSON and embedded HTML DB must match exactly')
dim_ids={d['id'] for d in kb['dimensions']}; source_ids=[s['id'] for s in kb['sources']]
check('knowledge_base_five_dimensions',len(kb['dimensions'])==5,str(len(kb['dimensions'])))
check('knowledge_base_legacy_ids_unique',len(dim_ids)==len(kb['dimensions']),'duplicate dimension id')
check('knowledge_base_source_ids_unique',len(source_ids)==len(set(source_ids)),'duplicate source id')
known=set(source_ids)
dangling=[(d['id'],sid) for d in kb['dimensions'] for sid in d.get('sourceIds',[]) if sid not in known]
check('knowledge_base_no_dangling_sources',not dangling,str(dangling[:10]))
relbad=[r for r in kb['relations'] if r.get('from') not in dim_ids or r.get('to') not in dim_ids]
check('knowledge_base_no_dangling_relations',not relbad,str(relbad[:10]))
check('knowledge_base_independent_of_hallerbans','not dependent on Hallerbans' in kb['project']['purpose'] and 'one possible consumer' in kb['project']['purpose'],kb['project']['purpose'])
check('knowledge_base_policy_gateway_relation',all(not (r.get('from')=='soul' and r.get('to')=='body' and r.get('type')=='authorizes') for r in kb['relations']),'legacy A→N authorizes relation must be absent')
check('knowledge_base_legacy_advice_field_removed',all('for_hallerbans' not in d for d in kb['dimensions']),'old consumer-specific field should not remain')
# Deterministic semantic invariants: transition rules and policy model are represented in the docs and registry.
inv=json.loads((ROOT/'tests/invariants.json').read_text(encoding='utf-8'))
check('invariant_registry_exact_30',len(inv)==30,f'count={len(inv)}')
claim=json.loads((ROOT/'contracts/claim.schema.json').read_text(encoding='utf-8'))
check('claim_separates_status_axes',all(x in claim['properties'] for x in ['epistemic_status','verification_status','confidence','valid_time','lifecycle_status']),'missing orthogonal field')
check('policy_has_nonpermit_outcomes',set(claim for claim in json.loads((ROOT/'contracts/policy-decision.schema.json').read_text(encoding='utf-8'))['properties']['decision']['enum'])=={'permit','deny','require_approval','defer'},'policy outcome enum mismatch')
check('no_runtime_code_in_package',not any(p.suffix in {'.ts','.tsx','.js','.pyc','.so','.bin'} and 'tools' not in p.parts and 'tests' not in p.parts for p in ROOT.rglob('*') if p.is_file()),'unexpected runtime artifact found')
# Run additional specification reference-oracle tests (no runtime execution).
import subprocess
try:
    dp=subprocess.run([sys.executable, str(ROOT/'tools/validate_deep_conformance.py')], capture_output=True, text=True, timeout=60)
    deep_ok=(dp.returncode==0)
    check('deep_reference_oracle_suite',deep_ok,dp.stdout[-2000:] + dp.stderr[-1000:])
except Exception as e:
    check('deep_reference_oracle_suite',False,str(e))
# Normative state-machine transition oracle: exhaustive edge matrices and negative guards.
try:
    sm=subprocess.run([sys.executable, str(ROOT/'tools/validate_state_machine_conformance.py')], capture_output=True, text=True, timeout=60)
    sm_ok=(sm.returncode==0)
    check('state_machine_conformance_suite', sm_ok, sm.stdout[-3000:] + sm.stderr[-1000:])
except Exception as e:
    check('state_machine_conformance_suite', False, str(e))
# Cross-document semantic consistency suite (still specification-only).
try:
    sp=subprocess.run([sys.executable, str(ROOT/'tools/validate_semantic_consistency.py')], capture_output=True, text=True, timeout=60)
    semantic_ok=(sp.returncode==0)
    check('semantic_consistency_suite', semantic_ok, sp.stdout[-3000:] + sp.stderr[-1000:])
except Exception as e:
    check('semantic_consistency_suite', False, str(e))
# Output report.
report={'package':'PRAIN v0.99.3 Phase-0 State-Machine Audit Candidate','baseline':'PRAIN v0.9.4','status':'PASS' if not ERRORS else 'FAIL','check_count':len(CHECKS),'passed':sum(c['status']=='PASS' for c in CHECKS),'failed':sum(c['status']=='FAIL' for c in CHECKS),'historical_schemas_checked':hcount,'canonical_schemas_checked':len(canonical),'checks':CHECKS,'errors':ERRORS,'scope_limit':'offline specification and cross-document consistency tests only; not runtime/production/security certification'}
(ROOT/'audit/validation_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':report['status'],'check_count':report['check_count'],'passed':report['passed'],'failed':report['failed'],'errors':ERRORS},ensure_ascii=False,indent=2))
sys.exit(0 if not ERRORS else 1)
