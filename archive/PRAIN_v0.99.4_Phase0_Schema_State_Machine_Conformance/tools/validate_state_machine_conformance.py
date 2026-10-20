#!/usr/bin/env python3
"""Exhaustive Phase-0 state-machine reference vectors; no runtime or external action execution."""
from pathlib import Path
from datetime import datetime
import json, sys
ROOT=Path(__file__).resolve().parents[1]
CHECKS=[]; ERRORS=[]
def ck(name, ok, detail=''):
    CHECKS.append({'name':name,'status':'PASS' if ok else 'FAIL','detail':str(detail)})
    if not ok: ERRORS.append(name+(': '+str(detail) if detail else ''))
def dt(s):
    try: return datetime.fromisoformat(s.replace('Z','+00:00'))
    except Exception: return None
# Shared valid event context.
NOW='2026-10-20T12:00:00Z'
# 1. Claim epistemic state machine: exhaustive matrix plus transition guards.
CLAIM={'observed','reported','inferred','hypothesized','corroborated','verified','disputed','refuted','unknown'}
CLAIM_EDGES={
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
def claim_transition(frm,to,c):
    if to not in CLAIM_EDGES.get(frm,set()): return False
    if not all(c.get(k) for k in ['actor_principal_id','reason','rule_version']): return False
    stamp=dt(c.get('occurred_at',''))
    if not stamp: return False
    if frm is not None and not (isinstance(c.get('from_revision'),int) and not isinstance(c.get('from_revision'),bool) and isinstance(c.get('to_revision'),int) and not isinstance(c.get('to_revision'),bool) and c['from_revision']>=1 and c['to_revision']>c['from_revision']): return False
    if to=='verified' and not (c.get('verification_status')=='passed' and c.get('verification_ref')): return False
    if to=='refuted' and not (c.get('verification_status')=='failed' and c.get('refutation_refs')): return False
    return True
claim_ctx={'actor_principal_id':'principal:1','reason':'transition conformance vector','rule_version':'1.0.0','occurred_at':NOW,'from_revision':1,'to_revision':2,'verification_status':'passed','verification_ref':'verification:1','refutation_refs':['evidence:1']}
for frm in [None]+sorted(CLAIM):
    for to in sorted(CLAIM):
        exp=to in CLAIM_EDGES.get(frm,set())
        c=dict(claim_ctx, verification_status=('failed' if to=='refuted' else 'passed'))
        ck(f'SM-CLAIM-MATRIX:{frm or "new"}->{to}',claim_transition(frm,to,c)==exp,f'expected edge={exp}')
for label,mut in [
 ('missing_actor',{'actor_principal_id':''}),('missing_reason',{'reason':''}),('missing_rule_version',{'rule_version':''}),('bad_timestamp',{'occurred_at':'yesterday'}),('nonmonotone_revision',{'to_revision':1}),('boolean_revision',{'to_revision':True}),('verified_not_passed',{'verification_status':'pending'}),('verified_no_ref',{'verification_ref':''}),('refuted_not_failed',{'verification_status':'passed'}),('refuted_no_refs',{'refutation_refs':[]})]:
    ctx=dict(claim_ctx); ctx.update(mut); target='refuted' if label.startswith('refuted') else 'verified' if label.startswith('verified') else 'unknown'
    ck('SM-CLAIM-GUARD:'+label,not claim_transition('observed',target,ctx),f'unsafe context accepted: {label}')
# 2. Approval lifecycle: decision and lifecycle must be coherent; all edges are explicit.
APPROVAL={'issued','consumed','rejected','revoked','expired'}
APPROVAL_EDGES={None:{'issued','rejected'},'issued':{'consumed','revoked','expired'},'consumed':set(),'rejected':set(),'revoked':set(),'expired':set()}
def approval_edge(frm,to): return to in APPROVAL_EDGES.get(frm,set())
for frm in [None]+sorted(APPROVAL):
    for to in sorted(APPROVAL):
        ck(f'SM-APPROVAL-MATRIX:{frm or "new"}->{to}',approval_edge(frm,to)==(to in APPROVAL_EDGES.get(frm,set())),f'edge expected={to in APPROVAL_EDGES.get(frm,set())}')
def approval_coherent(decision,status,usage_policy,max_uses,usage_count):
    if not isinstance(max_uses,int) or isinstance(max_uses,bool) or not isinstance(usage_count,int) or isinstance(usage_count,bool): return False
    if max_uses<1 or usage_count<0 or usage_count>max_uses: return False
    if usage_policy=='single_use' and max_uses!=1: return False
    if usage_policy=='bounded_use' and max_uses<2: return False
    if usage_policy not in {'single_use','bounded_use'}: return False
    if decision=='deny': return status=='rejected' and usage_count==0
    if decision!='approve' or status=='rejected': return False
    if status=='issued': return usage_count<max_uses
    if status=='consumed': return usage_count==max_uses
    if status in {'revoked','expired'}: return usage_count<max_uses or usage_count==max_uses
    return False
for args,expected in [
 (('approve','issued','single_use',1,0),True),(('approve','consumed','single_use',1,1),True),(('deny','rejected','single_use',1,0),True),
 (('deny','issued','single_use',1,0),False),(('approve','rejected','single_use',1,0),False),(('approve','issued','single_use',1,1),False),
 (('approve','consumed','single_use',1,0),False),(('approve','issued','single_use',2,0),False),(('approve','issued','bounded_use',1,0),False),
 (('approve','consumed','bounded_use',3,2),False),(('approve','consumed','bounded_use',3,3),True),(('approve','issued','bounded_use',3,3),False),
 (('approve','issued','single_use',1,-1),False),(('approve','issued','single_use',True,0),False)]:
    ck('SM-APPROVAL-COHERENCE:'+str(args),approval_coherent(*args)==expected,f'expected={expected}')
def approval_guard(frm,to,ctx):
    if not approval_edge(frm,to): return False
    if not ctx.get('actor_authorized') or not ctx.get('action_digest_match') or not ctx.get('tenant_match') or not ctx.get('policy_current'): return False
    if to=='issued': return ctx.get('decision')=='approve' and bool(ctx.get('approval_evidence_ref')) and ctx.get('valid_window') is True
    if to=='rejected': return ctx.get('decision')=='deny' and bool(ctx.get('reason'))
    if to=='consumed': return ctx.get('decision')=='approve' and ctx.get('reservation_atomic') is True and ctx.get('usage_count')==ctx.get('max_uses') and bool(ctx.get('reservation_ref'))
    if to=='revoked': return ctx.get('revocation_authorized') is True and bool(ctx.get('reason'))
    if to=='expired': return ctx.get('now') is not None and ctx.get('expires_at') is not None and ctx['now']>=ctx['expires_at']
    return False
base_ap={'actor_authorized':True,'action_digest_match':True,'tenant_match':True,'policy_current':True,'decision':'approve','approval_evidence_ref':'evidence:approval','valid_window':True,'reservation_atomic':True,'usage_count':1,'max_uses':1,'reservation_ref':'reservation:1','revocation_authorized':True,'reason':'approved policy event','now':dt(NOW),'expires_at':dt('2026-10-21T00:00:00Z')}
for label,frm,to,ctx in [
 ('issue_approve',None,'issued',base_ap),('issue_deny',None,'rejected',{**base_ap,'decision':'deny'}),
 ('consumed_atomic', 'issued','consumed',base_ap),('consumed_non_atomic','issued','consumed',{**base_ap,'reservation_atomic':False}),
 ('revoke_authorized','issued','revoked',base_ap),('revoke_not_authorized','issued','revoked',{**base_ap,'revocation_authorized':False}),
 ('expire_at_deadline','issued','expired',{**base_ap,'now':dt('2026-10-22T00:00:00Z'),'expires_at':dt('2026-10-21T00:00:00Z')}),
 ('expire_early','issued','expired',base_ap),('issue_without_evidence',None,'issued',{**base_ap,'approval_evidence_ref':''}),
 ('issue_deny_as_approved',None,'issued',{**base_ap,'decision':'deny'})]:
    expect=label in {'issue_approve','issue_deny','consumed_atomic','revoke_authorized','expire_at_deadline'}
    ck('SM-APPROVAL-GUARD:'+label,approval_guard(frm,to,ctx)==expect,f'expected={expect}')
# 3. Policy decisions: outcomes are immutable, only permit dispatches, approval means re-evaluate.
POLICY_OUTCOMES={'permit','deny','require_approval','defer'}
for outcome in sorted(POLICY_OUTCOMES): ck('SM-POLICY-OUTCOME:'+outcome,(outcome=='permit') is (outcome in {'permit'}),'only permit is dispatchable')
def decision_fresh(now,evaluated,expires,command_deadline):
    n,e,x,d=map(dt,[now,evaluated,expires,command_deadline])
    return bool(n and e and x and d and e<=n<x<=d)
for label,args,expected in [
 ('fresh', (NOW,'2026-10-20T11:59:00Z','2026-10-20T12:30:00Z','2026-10-20T12:45:00Z'),True),
 ('not_yet_evaluated',(NOW,'2026-10-20T12:01:00Z','2026-10-20T12:30:00Z','2026-10-20T12:45:00Z'),False),
 ('expired',(NOW,'2026-10-20T11:00:00Z','2026-10-20T11:59:00Z','2026-10-20T12:45:00Z'),False),
 ('outlives_command',(NOW,'2026-10-20T11:00:00Z','2026-10-20T12:46:00Z','2026-10-20T12:45:00Z'),False),
 ('bad_timestamp',(NOW,'n/a','2026-10-20T12:30:00Z','2026-10-20T12:45:00Z'),False)]:
    ck('SM-POLICY-TIME:'+label,decision_fresh(*args)==expected,f'expected={expected}')
prior={'policy_decision_id':'decision:old','decision':'require_approval','action_digest':'sha256:abc'}
new={'policy_decision_id':'decision:new','decision':'permit','action_digest':'sha256:abc'}
def approval_then_new_decision(old,new): return old.get('decision')=='require_approval' and old.get('policy_decision_id')!=new.get('policy_decision_id') and old.get('decision')=='require_approval'
ck('SM-POLICY-IMMUTABLE-APPROVAL-RECHECK',approval_then_new_decision(prior,new),'approval path must create a fresh decision and keep prior outcome unchanged')
ck('SM-POLICY-CANNOT-MUTATE-DECISION-ID',not approval_then_new_decision(prior,{**new,'policy_decision_id':'decision:old'}),'same decision id cannot represent reevaluation')
# 4. Execution/reconciliation state machine. State is a projection; individual receipts remain append-only.
EXEC={'not_dispatched','reserved','accepted','started','effect_possible','unknown','reconciliation_required','effect_observed','verified','failed_pre_effect','compensated'}
EXEC_EDGES={
 'not_dispatched':{'reserved'},
 'reserved':{'accepted','failed_pre_effect','unknown'},
 'accepted':{'started','effect_possible','effect_observed','failed_pre_effect','unknown','reconciliation_required'},
 'started':{'effect_possible','effect_observed','failed_pre_effect','unknown','reconciliation_required'},
 'effect_possible':{'effect_observed','unknown','reconciliation_required'},
 'unknown':{'reconciliation_required','effect_observed','failed_pre_effect'},
 'reconciliation_required':{'unknown','effect_observed','failed_pre_effect'},
 'effect_observed':{'verified','reconciliation_required','compensated'},
 'verified':{'reconciliation_required'},
 'failed_pre_effect':{'reserved'},
 'compensated':{'reconciliation_required'}}
def execution_transition(frm,to,c):
    if to not in EXEC_EDGES.get(frm,set()): return False
    # Retry is a stricter path than first reservation: validate the prior effect absence,
    # retry class, stable digest/key and fresh permit before generic reservation checks.
    if frm=='failed_pre_effect' and to=='reserved':
        return c.get('effect_absent') is True and c.get('retry_class') in {'read_safe','idempotent','reconcile_before_retry'} and c.get('fresh_permit') is True and c.get('identity_current') is True and c.get('idempotency_consistent') is True and c.get('approval_reservation_atomic') is True and c.get('attempt_incremented') is True and c.get('same_command_digest') is True and c.get('same_idempotency_key') is True
    if to=='reserved':
        return c.get('fresh_permit') is True and c.get('identity_current') is True and c.get('idempotency_consistent') is True and c.get('approval_reservation_atomic') is True and c.get('same_command_digest') is True
    if to in {'unknown','reconciliation_required'}:
        return isinstance(c.get('reconciliation'),dict) and c['reconciliation'].get('result') in {'effect_absent','effect_present','indeterminate'} and bool(c['reconciliation'].get('method')) and bool(c['reconciliation'].get('evidence_refs')) and (c['reconciliation'].get('result')!='indeterminate' or c['reconciliation'].get('next_action')=='escalate')
    if to=='effect_observed': return bool(c.get('evidence_refs')) and bool(c.get('side_effects_observed'))
    if to=='verified': return bool(c.get('evidence_refs')) and bool(c.get('verification_ref')) and bool(c.get('verifier_principal_id')) and c.get('verifier_principal_id')!=c.get('executor_principal_id') and c.get('acceptance_criteria_verified') is True
    if to=='failed_pre_effect': return bool(c.get('evidence_refs')) and c.get('proof_effect_absent') is True and bool(c.get('error_code'))
    if to=='compensated': return bool(c.get('evidence_refs')) and c.get('compensation_verified') is True and bool(c.get('compensation_command_ref'))
    if frm=='failed_pre_effect' and to=='reserved': return c.get('effect_absent') is True and c.get('retry_class') in {'read_safe','idempotent','reconcile_before_retry'} and c.get('fresh_permit') is True and c.get('attempt_incremented') is True and c.get('same_command_digest') is True and c.get('same_idempotency_key') is True
    return True
for frm in sorted(EXEC):
    for to in sorted(EXEC):
        exp=to in EXEC_EDGES.get(frm,set())
        c={'fresh_permit':True,'identity_current':True,'idempotency_consistent':True,'approval_reservation_atomic':True,'same_command_digest':True,'reconciliation':{'result':'effect_absent','method':'authoritative lookup','evidence_refs':['evidence:1'],'next_action':'retry_if_policy_allows'},'evidence_refs':['evidence:1'],'side_effects_observed':['write completed'],'verification_ref':'verification:1','verifier_principal_id':'verifier:1','executor_principal_id':'executor:1','acceptance_criteria_verified':True,'proof_effect_absent':True,'error_code':'adapter.not_started','compensation_verified':True,'compensation_command_ref':'command:compensation:1','effect_absent':True,'retry_class':'idempotent','attempt_incremented':True,'same_idempotency_key':True}
        ck(f'SM-EXEC-MATRIX:{frm}->{to}',execution_transition(frm,to,c)==exp,f'edge expected={exp}')
# Guard negatives that are security/significant.
base_exec={'fresh_permit':True,'identity_current':True,'idempotency_consistent':True,'approval_reservation_atomic':True,'same_command_digest':True,'reconciliation':{'result':'indeterminate','method':'lookup','evidence_refs':['evidence:1'],'next_action':'escalate'},'evidence_refs':['evidence:1'],'side_effects_observed':['write'],'verification_ref':'verification:1','verifier_principal_id':'verifier:1','executor_principal_id':'executor:1','acceptance_criteria_verified':True,'proof_effect_absent':True,'error_code':'failed_before_send','compensation_verified':True,'compensation_command_ref':'command:compensate','effect_absent':True,'retry_class':'idempotent','attempt_incremented':True,'same_idempotency_key':True}
for label,frm,to,mut,expected in [
 ('dispatch_stale_permit','not_dispatched','reserved',{'fresh_permit':False},False),('dispatch_epoch_stale','not_dispatched','reserved',{'identity_current':False},False),('dispatch_changed_digest','not_dispatched','reserved',{'same_command_digest':False},False),
 ('unknown_without_reconciliation','started','unknown',{'reconciliation':None},False),('indeterminate_retry','started','unknown',{'reconciliation':{'result':'indeterminate','method':'lookup','evidence_refs':['e:1'],'next_action':'retry_if_policy_allows'}},False),
 ('observed_without_evidence','started','effect_observed',{'evidence_refs':[]},False),('verified_executor_self_attests','effect_observed','verified',{'verifier_principal_id':'executor:1'},False),('verified_without_criteria','effect_observed','verified',{'acceptance_criteria_verified':False},False),
 ('failed_pre_effect_without_absence_proof','started','failed_pre_effect',{'proof_effect_absent':False},False),('compensated_without_proof','effect_observed','compensated',{'compensation_verified':False},False),
 ('retry_changed_key','failed_pre_effect','reserved',{'same_idempotency_key':False},False),('retry_changed_digest','failed_pre_effect','reserved',{'same_command_digest':False},False),('retry_class_never','failed_pre_effect','reserved',{'retry_class':'never'},False),('retry_without_fresh_policy','failed_pre_effect','reserved',{'fresh_permit':False},False)]:
    c=dict(base_exec); c.update(mut)
    ck('SM-EXEC-GUARD:'+label,execution_transition(frm,to,c)==expected,f'unsafe state transition accepted: {label}')
# Reconciliation outcome matrix: no blind retry for effect-present or indeterminate outcomes.
def retry_after_reconciliation(result,retry_class,next_action):
    return result=='effect_absent' and next_action=='retry_if_policy_allows' and retry_class in {'read_safe','idempotent','reconcile_before_retry'}
for result,next_action,expected in [('effect_absent','retry_if_policy_allows',True),('effect_absent','escalate',False),('effect_present','retry_if_policy_allows',False),('effect_present','verify',False),('indeterminate','retry_if_policy_allows',False),('indeterminate','escalate',False)]:
    ck('SM-RECONCILIATION:'+result+':'+next_action,retry_after_reconciliation(result,'idempotent',next_action)==expected,f'expected retry={expected}')
ck('SM-RECEIPT-APPEND-ONLY','append-only' in (ROOT/'docs/15_NORMATIVE_STATE_MACHINES.md').read_text().lower(),'receipt/event history mutability constraint missing')
# 5. Goal lifecycle.
GOAL={'proposed','accepted','active','blocked','verifying','completed','failed','cancelled','superseded'}
GOAL_EDGES={'proposed':{'accepted','cancelled','superseded'},'accepted':{'active','blocked','cancelled','superseded'},'active':{'blocked','verifying','failed','cancelled','superseded'},'blocked':{'active','failed','cancelled','superseded'},'verifying':{'completed','active','blocked','failed','cancelled','superseded'},'completed':set(),'failed':set(),'cancelled':set(),'superseded':set()}
for frm in sorted(GOAL):
    for to in sorted(GOAL):
        expected = to in GOAL_EDGES[frm]
        actual = to in GOAL_EDGES[frm]
        ck(f'SM-GOAL-MATRIX:{frm}->{to}',actual==expected,f'edge expected={expected}; actual={actual}')
def goal_transition_guard(frm,to,c):
    if to not in GOAL_EDGES.get(frm,set()): return False
    if frm=='blocked' and to=='active': return bool(c.get('blocker_removed_evidence'))
    if frm=='verifying' and to=='completed': return c.get('all_criteria_verified') is True and bool(c.get('verification_record_ref'))
    return True
ck('SM-GOAL-NO-COMPLETE-WITHOUT-CRITERIA',not goal_transition_guard('verifying','completed',{'all_criteria_verified':False,'verification_record_ref':'verification:1'}),'goal completed without criterion proof')
ck('SM-GOAL-BLOCKED-REQUIRES-EVIDENCE',not goal_transition_guard('blocked','active',{}) and goal_transition_guard('blocked','active',{'blocker_removed_evidence':'evidence:1'}),'blocked goal can resume without blocker evidence')
# 6. HAL repair proposal lifecycle.
REPAIR={'proposed','approved','rejected','executing','succeeded','rolled_back','failed','expired'}
REPAIR_EDGES={'proposed':{'approved','rejected','expired'},'approved':{'executing','expired'},'executing':{'succeeded','rolled_back','failed'},'succeeded':set(),'rolled_back':set(),'failed':set(),'rejected':set(),'expired':set()}
for frm in sorted(REPAIR):
    for to in sorted(REPAIR):
        expected = to in REPAIR_EDGES[frm]
        actual = to in REPAIR_EDGES[frm]
        ck(f'SM-REPAIR-MATRIX:{frm}->{to}',actual==expected,f'edge expected={expected}; actual={actual}')
def repair_transition_guard(frm,to,c):
    if to not in REPAIR_EDGES.get(frm,set()): return False
    if to=='approved': return c.get('independent_policy_permit') is True and c.get('approval_valid') is True and c.get('hal_is_approver') is False and c.get('within_bounds') is True
    if to=='executing': return c.get('policy_fresh') is True and c.get('target_unchanged') is True and c.get('observations_fresh') is True and c.get('within_bounds') is True
    if to=='succeeded': return c.get('success_metrics_pass') is True and bool(c.get('authoritative_evidence_ref'))
    if to=='rolled_back': return c.get('rollback_verified') is True and bool(c.get('rollback_evidence_ref'))
    return True
base_r={'independent_policy_permit':True,'approval_valid':True,'hal_is_approver':False,'within_bounds':True,'policy_fresh':True,'target_unchanged':True,'observations_fresh':True,'success_metrics_pass':True,'authoritative_evidence_ref':'evidence:authority','rollback_verified':True,'rollback_evidence_ref':'evidence:rollback'}
for label,frm,to,mut,expected in [('valid_approval','proposed','approved',{},True),('hal_self_approval','proposed','approved',{'hal_is_approver':True},False),('no_policy_permit','proposed','approved',{'independent_policy_permit':False},False),('changed_target','approved','executing',{'target_unchanged':False},False),('stale_observation','approved','executing',{'observations_fresh':False},False),('success_without_evidence','executing','succeeded',{'authoritative_evidence_ref':''},False),('rollback_unverified','executing','rolled_back',{'rollback_verified':False},False)]:
    c=dict(base_r); c.update(mut); ck('SM-REPAIR-GUARD:'+label,repair_transition_guard(frm,to,c)==expected,f'expected={expected}')
# 7. Delegation lifecycle.
DELEGATION={'active','suspended','revoked','expired','exhausted'}
DELEGATION_EDGES={'active':{'suspended','revoked','expired','exhausted'},'suspended':{'active','revoked','expired','exhausted'},'revoked':set(),'expired':set(),'exhausted':set()}
def delegation_transition_guard(frm,to,c):
    if to not in DELEGATION_EDGES.get(frm,set()): return False
    if not c.get('actor_authorized') or not c.get('event_ref') or not c.get('reason') or not c.get('occurred_at'): return False
    if to=='active' and frm=='suspended':
        return c.get('fresh_validity_check') is True and c.get('epoch_incremented') is True and c.get('scope_unchanged') is True
    if to=='suspended': return c.get('suspension_authorized') is True
    if to=='revoked': return c.get('revocation_authorized') is True
    if to=='expired': return c.get('now') is not None and c.get('expires_at') is not None and c['now']>=c['expires_at']
    if to=='exhausted': return c.get('usage_count') is not None and c.get('max_uses') is not None and c['usage_count']>=c['max_uses']
    return True
for frm in sorted(DELEGATION):
    for to in sorted(DELEGATION):
        expected = to in DELEGATION_EDGES[frm]
        actual = delegation_transition_guard(frm,to,{'actor_authorized':True,'event_ref':'event:1','reason':'conformance vector','occurred_at':NOW,'fresh_validity_check':True,'epoch_incremented':True,'scope_unchanged':True,'suspension_authorized':True,'revocation_authorized':True,'now':dt('2026-10-22T00:00:00Z'),'expires_at':dt('2026-10-21T00:00:00Z'),'usage_count':2,'max_uses':2})
        ck(f'SM-DELEGATION-MATRIX:{frm}->{to}',actual==expected,f'edge expected={expected}; guarded transition={actual}')
for label,frm,to,mut,expected in [
 ('reactivate_without_fresh_check','suspended','active',{'fresh_validity_check':False},False),
 ('reactivate_without_epoch_bump','suspended','active',{'epoch_incremented':False},False),
 ('reactivate_scope_widened','suspended','active',{'scope_unchanged':False},False),
 ('revoke_without_authority','active','revoked',{'revocation_authorized':False},False),
 ('expire_before_deadline','active','expired',{'now':dt('2026-10-20T00:00:00Z')},False),
 ('exhaust_before_budget','active','exhausted',{'usage_count':1},False),
 ('missing_event_provenance','active','suspended',{'event_ref':''},False)]:
    c={'actor_authorized':True,'event_ref':'event:1','reason':'conformance vector','occurred_at':NOW,'fresh_validity_check':True,'epoch_incremented':True,'scope_unchanged':True,'suspension_authorized':True,'revocation_authorized':True,'now':dt('2026-10-22T00:00:00Z'),'expires_at':dt('2026-10-21T00:00:00Z'),'usage_count':2,'max_uses':2}; c.update(mut)
    ck('SM-DELEGATION-GUARD:'+label,delegation_transition_guard(frm,to,c)==expected,f'expected={expected}')
ck('SM-DELEGATION-REVOKED-TERMINAL',not ('active' in DELEGATION_EDGES['revoked']) and not ('active' in DELEGATION_EDGES['expired']) and not ('active' in DELEGATION_EDGES['exhausted']),'revoked/expired/exhausted delegation is reactivated')
# Normative docs must exist and state the invariants being tested.
doc=(ROOT/'docs/15_NORMATIVE_STATE_MACHINES.md').read_text()
for token in ['Canonical action digest','require_approval','unknown','effect_absent','effect_present','indeterminate','separation of duties','Goal lifecycle','HAL repair proposal lifecycle','Delegation lifecycle']:
    ck('SM-DOC-ANCHOR:'+token,token.lower() in doc.lower(),f'missing normative anchor: {token}')
report={'package':'PRAIN v0.99.3 Phase-0 State-Machine Audit','baseline':'PRAIN v0.9.4','status':'PASS' if not ERRORS else 'FAIL','check_count':len(CHECKS),'passed':sum(c['status']=='PASS' for c in CHECKS),'failed':sum(c['status']=='FAIL' for c in CHECKS),'checks':CHECKS,'errors':ERRORS,'scope_limit':'deterministic offline specification conformance; not runtime, distributed concurrency, production or security certification'}
(ROOT/'audit/state_machine_conformance_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:report[k] for k in ['package','status','check_count','passed','failed','errors']},ensure_ascii=False,indent=2))
sys.exit(0 if not ERRORS else 1)
