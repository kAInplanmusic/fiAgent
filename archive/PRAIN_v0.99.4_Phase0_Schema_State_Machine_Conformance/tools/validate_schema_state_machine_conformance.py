#!/usr/bin/env python3
"""Deterministic schema/state-machine crosswalk checks; specification-level only."""
from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[1]
checks=[]
def ck(name, ok, detail=""):
    checks.append({"name":name,"passed":bool(ok),"detail":detail})
def load(p): return json.loads((ROOT/p).read_text(encoding="utf-8"))
contracts=ROOT/"contracts"
schemas={}
for p in sorted(contracts.glob("*.schema.json")):
    try:
        schemas[p.name]=load("contracts/"+p.name)
        ck("schema-load:"+p.name, True)
    except Exception as e:
        ck("schema-load:"+p.name, False, str(e))
ck("canonical-schema-count-17", len(schemas)==17, str(len(schemas)))
crosswalk=(ROOT/"docs/17_SCHEMA_STATE_MACHINE_CROSSWALK.md").read_text(encoding="utf-8")
for name in sorted(schemas):
    ck("crosswalk-covers:"+name, name in crosswalk, "schema explicitly referenced in crosswalk")
# Normative vocabularies must agree across claim schema and transition-event schema.
claim=schemas.get("claim.schema.json",{}).get("properties",{}).get("epistemic_status",{}).get("enum",[])
event=schemas.get("claim-transition-event.schema.json",{}).get("properties",{})
ck("claim-event-from-vocabulary-match", event.get("from_epistemic_status",{}).get("enum")==claim)
ck("claim-event-to-vocabulary-match", event.get("to_epistemic_status",{}).get("enum")==claim)
# Required fields for guarded state transitions are explicitly listed in normative prose.
required_phrases=[
    "verification_ref", "refutation_refs", "action digest", "policy version",
    "independent verification evidence", "proof of effect absence",
    "idempotency key", "increments attempt", "success criteria",
    "legal hold", "reference resolution", "atomic single-use approval consumption"
]
for phrase in required_phrases:
    ck("crosswalk-guard:"+phrase, phrase.lower() in crosswalk.lower(), phrase)
# Simple executable negative/positive reference-guard oracle; not a runtime simulator.
def claim_verified(status, procedure_passed, verification_ref):
    return status!="verified" or (procedure_passed is True and bool(verification_ref))
def claim_refuted(status, procedure_failed, refs):
    return status!="refuted" or (procedure_failed is True and isinstance(refs,list) and len(refs)>0)
def approval_usable(state, expires_at, now, consumed=False):
    return state=="issued" and expires_at>now and not consumed
def retry_allowed(retry_class, same_digest, same_key, attempt_increased, permit_current, effect_absent):
    return retry_class!="never" and all([same_digest,same_key,attempt_increased,permit_current,effect_absent])
def goal_complete(status, success_verified, evidence):
    return status!="completed" or (success_verified is True and bool(evidence))
def deletion_complete(status, all_targets_verified, legal_hold):
    return status!="verified" or (all_targets_verified is True and not legal_hold)
cases=[
("positive: verified claim with evidence",claim_verified("verified",True,"evidence:1"),True),
("negative: verified claim missing procedure",claim_verified("verified",False,"evidence:1"),False),
("negative: verified claim missing evidence",claim_verified("verified",True,""),False),
("positive: refuted claim with failed procedure and refs",claim_refuted("refuted",True,["e1"]),True),
("negative: refuted claim without refs",claim_refuted("refuted",True,[]),False),
("positive: unexpired issued approval",approval_usable("issued",20,10),True),
("negative: expired approval",approval_usable("issued",9,10),False),
("negative: consumed approval",approval_usable("consumed",20,10),False),
("positive: retry with full guards",retry_allowed("idempotent",True,True,True,True,True),True),
("negative: retry after never class",retry_allowed("never",True,True,True,True,True),False),
("negative: retry changes digest",retry_allowed("idempotent",False,True,True,True,True),False),
("negative: retry lacks effect absence",retry_allowed("idempotent",True,True,True,True,False),False),
("positive: completed goal with verification",goal_complete("completed",True,"e1"),True),
("negative: completed goal without verification",goal_complete("completed",False,"e1"),False),
("positive: deletion verified no legal hold",deletion_complete("verified",True,False),True),
("negative: deletion verified with legal hold",deletion_complete("verified",True,True),False),
]
for name,actual,expected in cases: ck("oracle:"+name,actual==expected,f"actual={actual}, expected={expected}")
report={"status":"PASS" if all(c["passed"] for c in checks) else "FAIL",
        "check_count":len(checks),"passed":sum(c["passed"] for c in checks),
        "failed":sum(not c["passed"] for c in checks),
        "scope":"deterministic offline schema/crosswalk and guard-oracle checks only",
        "checks":checks}
out=ROOT/"audit/schema_state_machine_conformance_report.json"
out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(f'{report["status"]}: {report["passed"]}/{report["check_count"]}; report={out.relative_to(ROOT)}')
sys.exit(0 if report["status"]=="PASS" else 1)
