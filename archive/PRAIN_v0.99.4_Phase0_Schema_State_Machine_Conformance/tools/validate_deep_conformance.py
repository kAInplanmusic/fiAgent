#!/usr/bin/env python3
"""Specification-only reference-oracle tests inherited from PRAIN v0.9.4; validates the v0.99.3 candidate and never executes actions."""
from pathlib import Path
import json, hashlib, re, sys, zipfile
from datetime import datetime, timezone
from jsonschema.validators import validator_for
from jsonschema import FormatChecker
ROOT=Path(__file__).resolve().parents[1]
CHECKS=[]; ERRORS=[]
def ck(n, ok, detail=''):
 CHECKS.append({'name':n,'status':'PASS' if ok else 'FAIL','detail':detail})
 if not ok: ERRORS.append(n+(': '+detail if detail else ''))
def sha_obj(x): return 'sha256:'+hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def parse_dt(x):
 try: return datetime.fromisoformat(x.replace('Z','+00:00'))
 except Exception: return None
# KB claim/source/disposition audit coverage.
kb=json.loads((ROOT/'knowledge_base/PRAIN_Wissensdatenbank.v0.3.0.json').read_text())
html=(ROOT/'knowledge_base/PRAIN_interaktive_Wissensdatenbank.v0.3.0.html').read_text()
m=re.search(r'const DB = (\{.*?^\});',html,re.S|re.M)
try: embedded=json.loads(m.group(1).rstrip().rstrip(';')) if m else None
except Exception: embedded=None
ck('TC-KB-PARITY-01',embedded==kb,'JSON and embedded HTML data differ')
ck('TC-KB-INDEPENDENCE-01','not dependent on Hallerbans' in kb['project']['purpose'] and 'one possible consumer' in kb['project']['purpose'],'PRAIN independence wording missing')
claims=[c for d in kb['dimensions'] for c in d['claims']]
source_ids={s['id'] for s in kb['sources']}
ck('TC-KB-CLAIM-COVERAGE-01',len(claims)==20 and len({c.get('claim_id') for c in claims})==20,'expected 20 unique claim records with IDs')
for c in claims:
 ck('TC-KB-CLAIM-ID:'+c.get('claim_id','missing'),bool(c.get('claim_id')) and bool(c.get('assessment_note')) and bool(c.get('assessment_method')),'claim is missing stable ID or assessment metadata')
 ck('TC-KB-CLAIM-SOURCES:'+c.get('claim_id','missing'),set(c.get('sourceIds',[]))<=source_ids and (bool(c.get('sourceIds')) or c.get('assessment_method')=='design_synthesis'),'dangling source ID or unjustified source-less claim')
 ck('TC-KB-CLAIM-AXES:'+c.get('claim_id','missing'),c.get('epistemic_status') in {'observed','reported','inferred','hypothesized','corroborated','verified','disputed','refuted','unknown'} and c.get('verification_status') in {'not_checked','pending','passed','failed','inconclusive','stale','not_applicable'},'claim epistemic axes are invalid')
 if c.get('epistemic_status')=='verified': ck('TC-KB-VERIFIED-REF:'+c['claim_id'],c.get('verification_status')=='passed' and bool(c.get('verification_ref')),'verified claim lacks passed status/reference')
 if c.get('epistemic_status')=='refuted': ck('TC-KB-REFUTED-REF:'+c['claim_id'],c.get('verification_status')=='failed' and bool(c.get('refutation_refs')),'refuted claim lacks failure/refutation evidence')
# Claim transition state machine lifted verbatim from the normative transition table.
S={'observed','reported','inferred','hypothesized','corroborated','verified','disputed','refuted','unknown'}
ALLOWED={
 None:{'observed','reported','inferred','hypothesized','unknown'},
 'observed':{'corroborated','verified','disputed','refuted','unknown'},
 'reported':{'corroborated','verified','disputed','refuted','unknown'},
 'inferred':{'corroborated','verified','disputed','refuted','unknown'},
 'hypothesized':{'corroborated','verified','disputed','refuted','unknown'},
 'corroborated':{'verified','disputed','refuted','unknown'},
 'verified':{'disputed','refuted','unknown'},
 'disputed':{'corroborated','verified','refuted','unknown'},
 'refuted':set(),
 'unknown':{'observed','reported','inferred','hypothesized','corroborated','verified','disputed','refuted'}}
def transition_valid(frm,to,ctx=None):
 ctx=ctx or {}
 if to not in ALLOWED.get(frm,set()): return False
 if to=='verified' and not (ctx.get('verification_status')=='passed' and ctx.get('verification_ref')): return False
 if to=='refuted' and not (ctx.get('verification_status')=='failed' and ctx.get('refutation_refs')): return False
 if frm is not None and not (isinstance(ctx.get('from_revision'),int) and isinstance(ctx.get('to_revision'),int) and ctx['to_revision']>ctx['from_revision']): return False
 if not all(ctx.get(k) for k in ['actor_principal_id','occurred_at','reason','rule_version']): return False
 return True
for frm in [None]+sorted(S):
 for to in sorted(S):
  ctx={'verification_status':('failed' if to=='refuted' else 'passed'),'verification_ref':'verification:1','refutation_refs':['evidence:1'],'from_revision':1,'to_revision':2,'actor_principal_id':'principal:1','occurred_at':'2026-10-20T12:00:00Z','reason':'test vector','rule_version':'1.0.0'}
  got=transition_valid(frm,to,ctx); expected=to in ALLOWED[frm]
  ck(f'TC-CLAIM-TRANSITIONS-ALL:{frm or "new"}->{to}',got==expected,f'expected {expected}, got {got}')
ck('TC-CLAIM-VERIFIED-01',not transition_valid('observed','verified',{'verification_status':'pending','verification_ref':'v:1','from_revision':1,'to_revision':2,'actor_principal_id':'p','occurred_at':'2026-10-20T12:00:00Z','reason':'x','rule_version':'1'}) and transition_valid('observed','verified',{'verification_status':'passed','verification_ref':'v:1','from_revision':1,'to_revision':2,'actor_principal_id':'p','occurred_at':'2026-10-20T12:00:00Z','reason':'x','rule_version':'1'}),'verification evidence rule mismatch')
ck('TC-CLAIM-REFUTED-01',not transition_valid('observed','refuted',{'verification_status':'failed','refutation_refs':[],'from_revision':1,'to_revision':2,'actor_principal_id':'p','occurred_at':'2026-10-20T12:00:00Z','reason':'x','rule_version':'1'}) and transition_valid('observed','refuted',{'verification_status':'failed','refutation_refs':['e:1'],'from_revision':1,'to_revision':2,'actor_principal_id':'p','occurred_at':'2026-10-20T12:00:00Z','reason':'x','rule_version':'1'}),'refutation evidence rule mismatch')
event_schema=json.loads((ROOT/'contracts/claim-transition-event.schema.json').read_text())
ck('TC-CLAIM-EVENT-01',set(['from_revision','to_revision','actor_principal_id','occurred_at','reason','rule_version','evidence_refs','counterevidence_refs'])<=set(event_schema.get('required',[])),'claim transition event lacks immutable history fields')
# Policy gateway reference oracle. The digest binds the whole authorization-relevant action context; no dispatch occurs.
def action_digest(cmd):
 keys=['tenant_id','actor_principal_id','goal_id','plan_id','capability','action','target_ref','input_digest','declared_side_effects','risk_class','deadline','authorization_context']
 if not all(k in cmd for k in keys): return None
 return sha_obj({k:cmd[k] for k in keys})
def policy_decide_dispatch(cmd, dec, approvals, now, current_policy_version, current_revocation_epoch):
 if not dec: return False,'missing_decision'
 if dec.get('decision')!='permit': return False,'non_permit_decision'
 if dec.get('policy_decision_id')!=cmd.get('policy_decision_ref'): return False,'decision_ref_mismatch'
 if dec.get('tenant_id')!=cmd.get('tenant_id') or dec.get('actor_principal_id')!=cmd.get('actor_principal_id'): return False,'principal_or_tenant_mismatch'
 if dec.get('capability')!=cmd.get('capability') or dec.get('target_ref')!=cmd.get('target_ref'): return False,'capability_or_target_mismatch'
 if dec.get('action_digest')!=action_digest(cmd): return False,'action_digest_mismatch'
 ctx=cmd.get('authorization_context') or {}
 if dec.get('identity_version')!=ctx.get('identity_version') or dec.get('policy_rule_refs')!=ctx.get('policy_rule_refs'): return False,'identity_or_rule_context_mismatch'
 if dec.get('policy_version')!=current_policy_version or cmd.get('policy_version')!=current_policy_version or dec.get('revocation_epoch')!=current_revocation_epoch or ctx.get('revocation_epoch')!=current_revocation_epoch: return False,'stale_policy_or_revocation_epoch'
 when=parse_dt(now); evaluated=parse_dt(dec.get('evaluated_at','')); exp=parse_dt(dec.get('expires_at','')); deadline=parse_dt(cmd.get('deadline',''))
 if any(x is None for x in [when,evaluated,exp,deadline]) or not evaluated<=when<exp or exp>deadline: return False,'decision_expired_bad_time_or_outlives_command'
 needed=set(dec.get('approval_refs',[])); command_approvals=set(cmd.get('approval_refs',[]))
 if command_approvals!=needed: return False,'approval_reference_set_mismatch'
 if not needed: return True,'permit'
 ap_by={a.get('approval_id'):a for a in approvals}
 for ref in needed:
  a=ap_by.get(ref)
  if not a: return False,'approval_missing'
  if a.get('decision')!='approve' or a.get('lifecycle_status')!='issued': return False,'approval_not_active_or_denied'
  if a.get('tenant_id')!=cmd.get('tenant_id') or a.get('actor_principal_id')!=cmd.get('actor_principal_id'): return False,'approval_actor_or_tenant_mismatch'
  if a.get('identity_version')!=ctx.get('identity_version'): return False,'approval_identity_version_mismatch'
  if a.get('action_digest')!=action_digest(cmd) or a.get('approved_capability')!=cmd.get('capability'): return False,'approval_action_or_capability_mismatch'
  if a.get('target_scope_digest')!=sha_obj(cmd.get('target_ref')) or a.get('side_effect_digest')!=sha_obj(cmd.get('declared_side_effects')): return False,'approval_target_or_side_effect_mismatch'
  if a.get('policy_version')!=current_policy_version or a.get('revocation_epoch')!=current_revocation_epoch: return False,'approval_stale_policy_or_epoch'
  start=parse_dt(a.get('valid_from','')); end=parse_dt(a.get('expires_at',''))
  if start is None or end is None or not start<=when<end or end>deadline: return False,'approval_outside_validity_or_outlives_command'
  if a.get('usage_count',0)>=a.get('max_uses',1): return False,'approval_usage_exhausted'
 return True,'permit'
now='2026-10-20T12:00:00Z'
ctx={'identity_version':'identity-v1','revocation_epoch':3,'delegation_refs':['delegation:1'],'policy_rule_refs':['rule:read-1'],'data_classification':'internal','access_scope_digest':'sha256:'+'b'*64}
cmd={'tenant_id':'tenant:1','goal_id':'goal:1','plan_id':'plan:1','actor_principal_id':'agent:1','capability':'files.read','action':'read','target_ref':'file:1','input_digest':'sha256:'+'a'*64,'declared_side_effects':['read_file'],'risk_class':'low','policy_version':'p1','deadline':'2026-10-20T12:45:00Z','authorization_context':ctx,'policy_decision_ref':'decision:1','approval_refs':['approval:1']}
dec={'policy_decision_id':'decision:1','tenant_id':'tenant:1','action_digest':action_digest(cmd),'actor_principal_id':'agent:1','capability':'files.read','target_ref':'file:1','decision':'permit','policy_version':'p1','identity_version':'identity-v1','policy_rule_refs':['rule:read-1'],'revocation_epoch':3,'evaluated_at':'2026-10-20T11:59:00Z','expires_at':'2026-10-20T12:30:00Z','approval_refs':['approval:1']}
ap={'approval_id':'approval:1','tenant_id':'tenant:1','action_digest':action_digest(cmd),'actor_principal_id':'agent:1','approver_principal_id':'human:1','identity_version':'identity-v1','approved_capability':'files.read','target_scope_digest':sha_obj('file:1'),'side_effect_digest':sha_obj(['read_file']),'decision':'approve','policy_version':'p1','revocation_epoch':3,'valid_from':'2026-10-20T11:00:00Z','expires_at':'2026-10-20T12:30:00Z','lifecycle_status':'issued','usage_policy':'single_use','usage_count':0,'max_uses':1}
ck('TC-POLICY-01',policy_decide_dispatch(cmd,dec,[ap],now,'p1',3)[0],'matching policy, decision and approval should pass reference oracle')
for label, baddec, badaps, cv, epoch in [
 ('missing_decision',None,[ap],'p1',3),('deny',{**dec,'decision':'deny'},[ap],'p1',3),('require_approval',{**dec,'decision':'require_approval'},[ap],'p1',3),('defer',{**dec,'decision':'defer'},[ap],'p1',3),('action_digest_mismatch',{**dec,'action_digest':'sha256:'+'0'*64},[ap],'p1',3),('tenant_mismatch',{**dec,'tenant_id':'tenant:2'},[ap],'p1',3),('expired_decision',{**dec,'expires_at':'2026-10-20T11:59:00Z'},[ap],'p1',3),('decision_outlives_command',{**dec,'expires_at':'2026-10-20T12:46:00Z'},[ap],'p1',3),('future_evaluated_at',{**dec,'evaluated_at':'2026-10-20T12:01:00Z'},[ap],'p1',3),('stale_policy',dec,[ap],'p2',3),('revocation_epoch',dec,[ap],'p1',4),('identity_version',{**dec,'identity_version':'identity-v2'},[ap],'p1',3),('policy_rule_refs',{**dec,'policy_rule_refs':['rule:write-1']},[ap],'p1',3),('approval_expired',dec,[{**ap,'expires_at':'2026-10-20T11:59:00Z'}],'p1',3),('approval_revoked',dec,[{**ap,'lifecycle_status':'revoked'}],'p1',3),('approval_rejected',dec,[{**ap,'decision':'deny','lifecycle_status':'rejected'}],'p1',3),('approval_effect_changed',dec,[{**ap,'side_effect_digest':sha_obj(['write_file'])}],'p1',3),('approval_actor_changed',dec,[{**ap,'actor_principal_id':'agent:2'}],'p1',3),('approval_identity_changed',dec,[{**ap,'identity_version':'identity-v2'}],'p1',3),('approval_used',dec,[{**ap,'usage_count':1,'lifecycle_status':'consumed'}],'p1',3),('missing_approval',dec,[],'p1',3),('extra_approval_ref',dec,[ap],'p1',3)]:
 test_cmd={**cmd}
 test_dec=baddec
 if label=='extra_approval_ref': test_cmd={**cmd,'approval_refs':['approval:1','approval:extra']}
 ck('TC-POLICY-NEGATIVE:'+label,not policy_decide_dispatch(test_cmd,test_dec,badaps,now,cv,epoch)[0],f'unsafe case was allowed: {label}')
# Metamorphic binding: every action-relevant field changes the digest.
base_digest=action_digest(cmd)
for field in ['tenant_id','goal_id','plan_id','actor_principal_id','capability','action','target_ref','input_digest','declared_side_effects','risk_class','deadline','authorization_context']:
 changed={**cmd}
 if field=='authorization_context': changed[field]={**ctx,'data_classification':'restricted'}
 elif field=='declared_side_effects': changed[field]=['read_file','write_file']
 else: changed[field]=str(cmd[field])+'-changed'
 ck('TC-POLICY-DIGEST-BIND:'+field,action_digest(changed)!=base_digest,f'action digest failed to bind {field}')
ck('TC-POLICY-APPROVAL-RECHECK',not policy_decide_dispatch(cmd,{**dec,'decision':'require_approval'},[ap],now,'p1',3)[0] and policy_decide_dispatch(cmd,{**dec,'policy_decision_id':'decision:2'},[ap],now,'p1',3)[0] is False,'require_approval must be followed by a new immutable policy decision bound from command reference')
# Tenant/isolation and authority reference checks.
for sname in ['action-command.schema.json','claim.schema.json','delegation-grant.schema.json','deletion-request.schema.json','evidence-record.schema.json','execution-receipt.schema.json','goal.schema.json','health-signal.schema.json','message-envelope.schema.json','observation.schema.json','policy-approval.schema.json','policy-decision.schema.json','principal.schema.json','repair-proposal.schema.json','state-record.schema.json','tenant.schema.json','claim-transition-event.schema.json']:
 s=json.loads((ROOT/'contracts'/sname).read_text()); ck('TC-TENANT-01:'+sname,'tenant_id' in s.get('required',[]),'tenant_id must be required in protected canonical contract')
# Provenance contract shape checks.
for n in ['claim.schema.json','observation.schema.json','evidence-record.schema.json']:
 s=json.loads((ROOT/'contracts'/n).read_text()); ck('TC-PROVENANCE-01:'+n, any(k in s.get('properties',{}) for k in ['provenance','source_ref','source_ref']) ,'source/provenance field missing')
# Delegation: capability/scope/time must narrow grantor authority; no implicit widening.
def delegation_valid(child_caps,grantor_caps,child_refs,grantor_refs,child_start,child_end,parent_start,parent_end,status='active',use_count=0,max_uses=None):
 if status!='active' or not set(child_caps)<=set(grantor_caps): return False
 if not set(child_refs)<=set(grantor_refs): return False
 cs,ce,ps,pe=map(parse_dt,[child_start,child_end,parent_start,parent_end])
 if not all([cs,ce,ps,pe]) or not ps<=cs<ce<=pe: return False
 if max_uses is not None and use_count>=max_uses: return False
 return True
ck('TC-DELEGATION-01',delegation_valid(['files.read'],['files.read','files.write'],['file:1'],['file:1','file:2'],'2026-10-20T11:00:00Z','2026-10-20T12:00:00Z','2026-10-20T10:00:00Z','2026-10-20T13:00:00Z'),'properly narrowed delegation rejected')
ck('TC-DELEGATION-02',all(not delegation_valid(*args) for args in [
 (['files.write'],['files.read'],['file:1'],['file:1'],'2026-10-20T11:00:00Z','2026-10-20T12:00:00Z','2026-10-20T10:00:00Z','2026-10-20T13:00:00Z'),
 (['files.read'],['files.read'],['file:3'],['file:1'],'2026-10-20T11:00:00Z','2026-10-20T12:00:00Z','2026-10-20T10:00:00Z','2026-10-20T13:00:00Z'),
 (['files.read'],['files.read'],['file:1'],['file:1'],'2026-10-20T09:00:00Z','2026-10-20T12:00:00Z','2026-10-20T10:00:00Z','2026-10-20T13:00:00Z'),
 (['files.read'],['files.read'],['file:1'],['file:1'],'2026-10-20T11:00:00Z','2026-10-20T14:00:00Z','2026-10-20T10:00:00Z','2026-10-20T13:00:00Z'),
 (['files.read'],['files.read'],['file:1'],['file:1'],'2026-10-20T11:00:00Z','2026-10-20T12:00:00Z','2026-10-20T10:00:00Z','2026-10-20T13:00:00Z','revoked')]),'delegation widening/expiry/revocation cases not rejected')
# Idempotency cannot associate one idempotency key with two action digests.
def idempotency_reserve(ledger,key,digest):
 if key in ledger: return ledger[key]==digest
 ledger[key]=digest; return True
ledger={}; ck('TC-IDEMPOTENCY-01',idempotency_reserve(ledger,'tenant:1/key:1','digest:A') and idempotency_reserve(ledger,'tenant:1/key:1','digest:A') and not idempotency_reserve(ledger,'tenant:1/key:1','digest:B'),'same key with changed action was not rejected')
# Unknown external effect: retry requires reconciliation proof; lease timeout alone has no bearing.
def retry_permitted(status,recon,retry_class):
 if status in {'unknown','reconciliation_required','effect_possible','effect_observed'}:
  if not recon: return False
  if recon.get('result')=='effect_present': return False
  if recon.get('result')=='indeterminate': return False
  return recon.get('result')=='effect_absent' and recon.get('next_action')=='retry_if_policy_allows' and retry_class in {'read_safe','idempotent','reconcile_before_retry'}
 return status=='failed_pre_effect' and retry_class in {'read_safe','idempotent','reconcile_before_retry'}
ck('TC-UNKNOWN-OUTCOME-01',not retry_permitted('unknown',None,'idempotent') and not retry_permitted('unknown',{'result':'indeterminate','next_action':'retry_if_policy_allows'},'idempotent') and not retry_permitted('unknown',{'result':'effect_present','next_action':'retry_if_policy_allows'},'idempotent') and retry_permitted('unknown',{'result':'effect_absent','next_action':'retry_if_policy_allows'},'idempotent'),'unknown effect retry rules mismatch')
ck('TC-RECEIPT-01',len(json.loads((ROOT/'contracts/execution-receipt.schema.json').read_text())['allOf'])>=3,'execution receipt conditional semantics missing')
# CAS and authority class.
def cas_update(current_version,expected_version,new_version): return expected_version==current_version and new_version==current_version+1
def can_write_authority(authority_class,writer_kind):
 if authority_class=='derived_projection': return writer_kind=='projection_builder'
 if authority_class=='authoritative': return writer_kind=='authorized_aggregate_owner'
 if authority_class=='append_only_evidence': return writer_kind in {'evidence_writer','authorized_aggregate_owner'}
 return writer_kind in {'observer','authorized_aggregate_owner'}
ck('TC-CAS-01',cas_update(5,5,6) and not cas_update(5,4,6) and not cas_update(5,5,7),'CAS expected version/new version rules mismatch')
ck('TC-AUTHORITY-01',not can_write_authority('authoritative','projection_builder') and can_write_authority('derived_projection','projection_builder') and can_write_authority('authoritative','authorized_aggregate_owner'),'projection can overwrite authoritative state or authorized writer blocked')
# HAL repair reference oracle: high-risk class requires approval and independent decision; HAL is not approver.
def hal_repair_allowed(proposal, approvals, decision, hal_principal_id):
 high={'schema_migration','policy_change','credential_change','source_of_truth_write','external_side_effect'}
 if proposal.get('repair_class') in high and not proposal.get('requires_human_approval'): return False
 if proposal.get('repair_class') in high and not proposal.get('approval_refs'): return False
 if proposal.get('status') in {'approved','executing','succeeded','rolled_back'} and not proposal.get('policy_decision_ref'): return False
 if proposal.get('status') in {'approved','executing','succeeded','rolled_back'} and not (decision and decision.get('decision')=='permit' and decision.get('policy_decision_id')==proposal.get('policy_decision_ref')): return False
 if proposal.get('repair_class') in high and not approvals: return False
 if any(a.get('approver_principal_id')==hal_principal_id for a in approvals): return False
 return True
base_repair={'repair_class':'policy_change','requires_human_approval':True,'approval_refs':['approval:1'],'policy_decision_ref':'decision:1','status':'approved'}
ck('TC-HAL-01',not hal_repair_allowed({**base_repair,'approval_refs':[]},[],{'decision':'permit','policy_decision_id':'decision:1'},'hal:1') and not hal_repair_allowed(base_repair,[{'approver_principal_id':'hal:1'}],{'decision':'permit','policy_decision_id':'decision:1'},'hal:1'),'HAL can self-approve or omit required approval')
ck('TC-HAL-02',not hal_repair_allowed({**base_repair,'policy_decision_ref':'decision:2'},[{'approver_principal_id':'human:1'}],{'decision':'permit','policy_decision_id':'decision:1'},'hal:1') and not hal_repair_allowed({**base_repair,'requires_human_approval':False},[{'approver_principal_id':'human:1'}],{'decision':'permit','policy_decision_id':'decision:1'},'hal:1'),'HAL hard-limit/policy change bypassed independent gate')
# Deletion completion requires acknowledgements for all propagation domains unless declared exceptions/legal hold.
def deletion_complete(required_scopes, confirmed_scopes, exceptions=None, legal_hold=False):
 if legal_hold: return False
 missing=set(required_scopes)-set(confirmed_scopes)-set(exceptions or [])
 return not missing
required={'authoritative_store','events','replicas','projections','vector_indexes','caches','exports','derived_claims','backups'}
ck('TC-DELETION-01',not deletion_complete(required,required-{'backups'}) and deletion_complete(required,required,legal_hold=False) and not deletion_complete(required,required,legal_hold=True),'deletion verified without full propagation or over legal hold')
# Evidence semantics: content digest assures integrity comparison, never source truth; lifecycle can delete content but retain restricted non-content tombstone metadata.
def evidence_authenticity(integrity_passed,signature_verified,source_trusted): return integrity_passed and signature_verified and source_trusted
def deletion_preserves_no_content_after_delete(content_present,lifecycle_status,manifest_tombstone):
 if lifecycle_status=='deleted': return not content_present and manifest_tombstone
 return True
ck('TC-EVIDENCE-01',not deletion_preserves_no_content_after_delete(True,'deleted',True) and deletion_preserves_no_content_after_delete(False,'deleted',True),'deleted content retention invariant failed')
ck('TC-EVIDENCE-02',not evidence_authenticity(True,False,False) and not evidence_authenticity(True,True,False) and evidence_authenticity(True,True,True),'digest alone incorrectly treated as authenticity')
# Goal completion requires every acceptance criterion to have sufficient evidence verified.
def goal_complete(criteria,evidence):
 if not criteria: return False
 for c in criteria:
  e=evidence.get(c)
  if not e or e.get('verified') is not True or not e.get('evidence_refs'): return False
 return True
ck('TC-GOAL-COMPLETION-01',not goal_complete(['c1','c2'],{'c1':{'verified':True,'evidence_refs':['e1']}}) and goal_complete(['c1','c2'],{'c1':{'verified':True,'evidence_refs':['e1']},'c2':{'verified':True,'evidence_refs':['e2']}}),'goal completed without evidence for every criterion')
# Delivery contract, quantum readiness and scope boundary checks.
decision=(ROOT/'docs/08_DECISION_REGISTER_FINAL.md').read_text()
arch=(ROOT/'docs/10_REFERENCE_FLOWS.md').read_text()
ck('TC-QUANTUM-READY-01','no quantum advantage assumption' in decision.lower() and 'quantum' in decision.lower(),'quantum-ready non-advantage rule missing')
ck('TC-DELIVERY-01','no global exactly-once' in decision.lower(),'global exactly-once forbidden rule missing')
manifest=json.loads((ROOT/'MANIFEST.json').read_text())
ck('TC-RUNTIME-BOUNDARY-01',manifest.get('runtime_implementation_included') is False and not any(p.suffix.lower() in {'.ts','.tsx','.js','.go','.rs','.java','.cpp','.c'} for p in ROOT.rglob('*') if p.is_file() and 'sources' not in p.parts and p.name not in {'PRAIN_interaktive_Wissensdatenbank.v0.3.0.html'}),'runtime/framework code unexpectedly included')
# Every one of the 30 invariant IDs has an explicit mapped test suite and runtime boundary.
coverage=json.loads((ROOT/'tests/invariant_coverage.json').read_text())
ids={x['id'] for x in json.loads((ROOT/'tests/invariants.json').read_text())}
ck('TC-INVARIANT-COVERAGE-30',len(coverage)==30 and {c['invariant_id'] for c in coverage}==ids and all(c['test_ids'] and c['phase0_status'] for c in coverage),'some invariant lacks mapped evidence')
# Item-by-item disposition coverage across all content kinds.
disp=json.loads((ROOT/'audit/knowledge_base_item_disposition.json').read_text())
ck('TC-KB-DISPOSITION-COUNT',len(disp)==len({(x['kind'],x['id']) for x in disp}) and len(disp)==114,f'count={len(disp)}; expected 114 distinct items')
expected_claim_ids={c['claim_id'] for c in claims}
disposed_claim_ids={x['id'] for x in disp if x['kind']=='claim'}
ck('TC-KB-DISPOSITION-CLAIMS',expected_claim_ids==disposed_claim_ids,'claim disposition list does not cover exactly all claims')
# All official sources checked and all 20 source judgements present.
sa=json.loads((ROOT/'audit/claim_source_audit.json').read_text())
ck('TC-SOURCE-AUDIT-19',len(sa['sources'])==19 and len({x['source_id'] for x in sa['sources']})==19,'expected 19 distinct source check records')
ck('TC-SOURCE-AUDIT-20-CLAIMS',len(sa['claims'])==20 and {x['claim_id'] for x in sa['claims']}==expected_claim_ids,'source audit does not cover each claim exactly once')
# Print machine-readable report.
report={'package':'PRAIN v0.99.3 Phase-0 Semantic Consistency Candidate','baseline':'PRAIN v0.9.4','status':'PASS' if not ERRORS else 'FAIL','check_count':len(CHECKS),'passed':sum(x['status']=='PASS' for x in CHECKS),'failed':sum(x['status']=='FAIL' for x in CHECKS),'checks':CHECKS,'errors':ERRORS,'scope_limit':'reference-oracle/specification conformance only; not runtime execution, penetration testing or independent audit'}
(ROOT/'audit/deep_conformance_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['package','status','check_count','passed','failed','errors']},ensure_ascii=False,indent=2))
sys.exit(0 if not ERRORS else 1)
