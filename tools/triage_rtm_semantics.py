"""Prepare evidence-preserving row-by-row semantic adjudication proposals.

Never writes ACCEPTED: automatic text heuristics cannot establish normative intent,
supersession or runtime conformance. Each candidate gets an explicit proposal.
"""
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"TRACEABILITY/REQUIREMENT_TRACEABILITY_MATRIX.csv"
OUT=ROOT/"TRACEABILITY/RTM_SEMANTIC_REVIEW_QUEUE.csv"
REPORT=ROOT/"TRACEABILITY/RTM_SEMANTIC_TRIAGE_SUMMARY.json"
META=re.compile(r'^\s*(?:#{1,6}\s|\{\s*$|\}\s*,?$|\[\s*$|\]\s*,?$|[-*_]{3,}\s*$)')
JSONFIELD=re.compile(r'^\s*"[\w$@.:-]+"\s*:\s*')
TABLE=re.compile(r'^\s*\|')
CHECK=re.compile(r'^\s*[-*]\s*\[[ xX]\]\s*')
REQ=re.compile(r'\b(?:must|shall|required|requirement|invariant|MUSS|DARF NICHT|SOLL|müssen|verpflichtend|reject|deny|never|cannot)\b',re.I)

def classify(text,prior):
    t=text.strip()
    if not t:
        return "EMPTY_CANDIDATE","empty extraction; inspect source",0.99
    if META.match(t):
        return "STRUCTURAL_CANDIDATE","heading/container/delimiter; inspect surrounding section",0.96
    if JSONFIELD.match(t):
        return "SCHEMA_FIELD_CANDIDATE","schema JSON field: reconstruct full schema and its constraints",0.98
    if TABLE.match(t):
        return "TABLE_ROW_CANDIDATE","table row; resolve table header, version and obligation",0.93
    if t in prior:
        return "DUPLICATE_TEXT_CANDIDATE",f"possible repeat of {prior[t]}; check source version/supersession",0.96
    if CHECK.match(t):
        return "CHECKLIST_CANDIDATE","status checkbox, distinguish planned vs normative and verify evidence",0.94
    if REQ.search(t):
        return "NORMATIVE_LANGUAGE_CANDIDATE","modal or invariant wording; independent review required",0.90
    return "CONTEXTUAL_CANDIDATE","text requires section and source context for normativity",0.60

def run():
    with SRC.open(encoding="utf-8",newline="") as f:
        reader=csv.DictReader(f)
        rows=list(reader)
    seen={}
    counts=Counter()
    output=[]
    for row in rows:
        text=row["normalized_requirement"]
        category,rationale,confidence=classify(text,seen)
        seen.setdefault(text.strip(),row["requirement_id"])
        counts[category]+=1
        output.append({
            "requirement_id":row["requirement_id"],
            "source_path":row["source_path"],
            "source_location":row["source_location"],
            "text_sha256":hashlib.sha256(text.encode()).hexdigest(),
            "proposed_category":category,
            "proposed_rationale":rationale,
            "proposal_confidence":f"{confidence:.2f}",
            "normative_decision":"UNREVIEWED",
            "canonical_requirement_id":"",
            "superseded_by":"",
            "implementation_reference":"",
            "test_evidence":"",
            "reviewer":"",
            "review_timestamp":"",
            "decision_rationale":""
        })
    fields=list(output[0])
    with OUT.open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=fields)
        writer.writeheader()
        writer.writerows(output)
    summary={"total":len(rows),"unique_ids":len(set(r["requirement_id"] for r in rows)),
             "suggested_categories":dict(sorted(counts.items())),
             "normatively_accepted":0,
             "review_pending":len(rows),
             "row_coverage":len(output)==len(rows),
             "queue":"TRACEABILITY/RTM_SEMANTIC_REVIEW_QUEUE.csv",
             "warning":"Proposals only. No automatic acceptance or semantic supersession."}
    REPORT.write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return summary

if __name__=="__main__":
    print(json.dumps(run(),indent=2))
