"""Build deterministic, non-fabricated evidence work packages for Strict-B RTM.
Never equate a matching source phrase with an implemented feature.
"""
import csv,json,hashlib,re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
R=ROOT/"TRACEABILITY"
M=R/"REQUIREMENT_TRACEABILITY_MATRIX.csv"
F=R/"RTM_69_FINAL_REFERENCE_RESOLUTION.csv"
OUTPUT=R/"RTM_5071_EVIDENCE_WORKPACKAGES.csv"
INDEX=R/"RTM_5071_WORKPACKAGE_AUDIT.json"
PACKS={"SCHEMA":"G02","SCF":"G03","DISTRIBUTED":"G04","AUTH":"G05","PRIVACY":"G06","HAL":"G07","ADAPTER":"G08","RELEASE":"G09","GOVERNANCE":"G01"}
def run():
    with M.open(newline="",encoding="utf8") as f: rows=list(csv.DictReader(f))
    with F.open(newline="",encoding="utf8") as f: fixed={x["requirement_id"]:x for x in csv.DictReader(f)}
    seen={};out=[];counts=Counter()
    for r in rows:
        rid=r["requirement_id"]; text=r["normalized_requirement"].strip(); source=r["source_path"]
        if rid in fixed:
            p=fixed[rid];source=p["resolved_source"];loc="line "+p["resolved_line"]
            status=p["semantic_disposition"]; evidence="SOURCE_CANONICAL_EXACT"
        else:
            loc=r["source_location"];status="PENDING_NORMATIVE_REVIEW";evidence="SOURCE_LINE_VERIFIED_OR_PENDING"
        norm=(text+" "+source).lower()
        if source.endswith(".schema.json") or '"type":' in text or '"properties":' in text:tag="SCHEMA"
        elif any(x in norm for x in ("scf","claim","semantic","graph")):tag="SCF"
        elif any(x in norm for x in ("fencing","distributed","lease","transport","inbox","outbox")):tag="DISTRIBUTED"
        elif any(x in norm for x in ("tenant","principal","approval","policy","authoriz")):tag="AUTH"
        elif any(x in norm for x in ("retention","privacy","deletion","redaction")):tag="PRIVACY"
        elif any(x in norm for x in ("hal","anima","health","repair")):tag="HAL"
        elif any(x in norm for x in ("compute","provider","adapter","quantum")):tag="ADAPTER"
        elif any(x in norm for x in ("release","deploy","backup","restore","tests")):tag="RELEASE"
        else:tag="GOVERNANCE"
        digest=hashlib.sha256(text.encode()).hexdigest()
        duplicate=seen.get(digest,"")
        seen.setdefault(digest,rid)
        counts[tag]+=1
        out.append({"requirement_id":rid,"workstream":tag,"gate":PACKS[tag],
        "source":source,"locator":loc,"content_sha256":digest,"identical_text_first_id":duplicate,
        "semantic_proposal":status,"source_evidence":evidence,
        "normative_acceptance":"NOT_ACCEPTED","runtime_evidence":"MISSING",
        "implementation_acceptance":"NOT_ACCEPTED","independent_signoff":"MISSING",
        "next_action":"Inspect normative effective version; link canonical contract, code, test and reviewer signoff"})
    if len(out)!=5071 or len({x["requirement_id"] for x in out})!=5071:raise ValueError("incomplete IDs")
    with OUTPUT.open("w",encoding="utf8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(out[0]),lineterminator="\n");w.writeheader();w.writerows(out)
    summary={"total":len(out),"workstreams":dict(sorted(counts.items())),"source_reference_resolved_69":len(fixed),
    "content_duplicate_candidates":sum(bool(x["identical_text_first_id"]) for x in out),
    "fully_accepted":0,"pending_acceptance":len(out),
    "workpackage_file":str(OUTPUT.relative_to(ROOT)),
    "rule":"No automatic substantive acceptance or invented implementation evidence"}
    INDEX.write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n",encoding="utf8")
    return summary
if __name__=="__main__": print(json.dumps(run(),indent=2))
