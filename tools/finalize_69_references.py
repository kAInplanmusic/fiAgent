"""Reconcile historical RTM-00001..00069 to canonical source locations.

The first W0-W9 section of ROADMAP is canonical; a later duplicate does not
establish another obligation. Historical README entry is in MASTER_README.
Source location repair is not implementation or human acceptance.
"""
import csv, hashlib, json, re
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RTM=ROOT/"TRACEABILITY/REQUIREMENT_TRACEABILITY_MATRIX.csv"
OUT=ROOT/"TRACEABILITY/RTM_69_FINAL_REFERENCE_RESOLUTION.csv"
SUMMARY=ROOT/"TRACEABILITY/RTM_69_REFERENCE_RESOLUTION_SUMMARY.json"

def resolve():
    with RTM.open(encoding="utf8",newline="") as f:
        entries=[r for r in csv.DictReader(f) if r["requirement_id"] in
                 {f"RTM-{i:05d}" for i in range(1,70)}]
    if len(entries)!=69:
        raise ValueError("incomplete_discrepancy_set")
    roadmap=(ROOT/"ROADMAP.md").read_text(encoding="utf8").splitlines()
    master=(ROOT/"MASTER_README.md").read_text(encoding="utf8").splitlines()
    records=[]
    for row in entries:
        uid=row["requirement_id"]; norm=row["normalized_requirement"].strip()
        if uid=="RTM-00069":
            candidates=[n for n,v in enumerate(master,1) if v.strip()==norm]
            if len(candidates) != 1:
                raise ValueError("master_readme_unexpected")
            source,selected,alternates="MASTER_README.md",candidates[0],""
            semantic="HISTORICAL_INFORMATIONAL"
            disposition="NON_NORMATIVE_SOURCE_DESCRIPTION"
            rationale="A version overview row describes the historical v0.6 archive; it does not prescribe a runtime requirement."
        else:
            candidates=[n for n,v in enumerate(roadmap,1) if v.strip()==norm]
            if len(candidates)!=2 or candidates[0]>=candidates[1]:
                raise ValueError("roadmap_copy_count_changed:"+uid)
            selected=candidates[0]
            if not 33<=selected<180:
                raise ValueError("canonical_section_not_matched:"+uid)
            source,alternates="ROADMAP.md",str(candidates[1])
            semantic="ROADMAP_WORK_ITEM"
            disposition="NORMATIVE_WORK_TRACK_PENDING_EVIDENCE" if norm.startswith("- [ ]") else "DOCUMENTED_COMPLETION_CLAIM_REQUIRES_EVIDENCE"
            rationale="First roadmap W0-W9 section is canonical; later literal copy is non-authoritative duplicate. Checkbox is not sufficient implementation evidence."
        actual=(master if source=="MASTER_README.md" else roadmap)[selected-1]
        if norm!=actual.strip():
            raise ValueError("reference_not_exact:"+uid)
        records.append({
          "requirement_id":uid,"original_source":row["source_path"],"original_locator":row["source_location"],
          "resolved_source":source,"resolved_line":selected,
          "duplicate_line":alternates,"source_line_sha256":hashlib.sha256(actual.strip().encode()).hexdigest(),
          "reference_status":"EXACT_UNAMBIGUOUS_CANONICAL",
          "semantic_category":semantic,"semantic_disposition":disposition,
          "rationale":rationale,"implementation_acceptance":"NOT_VERIFIED",
          "human_release_acceptance":"NOT_GRANTED"})
    with OUT.open("w",encoding="utf8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(records[0]),lineterminator="\n")
        w.writeheader();w.writerows(records)
    result={"resolved_references":len(records),"reference_open":0,
       "canonical_roadmap_work_items":68,"historical_informational":1,
       "semantic_dispositions":dict(Counter(r["semantic_disposition"] for r in records)),
       "runtime_accepted":0,"human_release_accepted":0,
       "source":"TRACEABILITY/RTM_69_FINAL_REFERENCE_RESOLUTION.csv",
       "scope":"Only 69 source discrepancies; does not close remaining 5002 semantic/implementation reviews."}
    SUMMARY.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf8")
    return result

if __name__=="__main__":
    print(json.dumps(resolve(),ensure_ascii=False,indent=2))
