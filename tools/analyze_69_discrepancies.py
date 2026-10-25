"""Analyze 69 source-line discrepancies without rewriting historical requirements."""
import csv,json,difflib,re
from collections import Counter
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
RTM=BASE/"TRACEABILITY/REQUIREMENT_TRACEABILITY_MATRIX.csv"
RES=BASE/"TRACEABILITY/RTM_SOURCE_RESOLUTION.csv"
OUT=BASE/"TRACEABILITY/RTM_69_DISCREPANCY_REVIEW.csv"
SUMMARY=BASE/"TRACEABILITY/RTM_69_DISCREPANCY_SUMMARY.json"
def normalize(s):
    return re.sub(r"\s+"," ",s.strip())
def analyze():
    with RTM.open(encoding="utf8",newline="") as f: rows={r["requirement_id"]:r for r in csv.DictReader(f)}
    with RES.open(encoding="utf8",newline="") as f: bad=[r for r in csv.DictReader(f) if r["source_result"]!="EXACT_SOURCE_LINE"]
    reports=[];counts=Counter()
    for r in bad:
        item=rows[r["requirement_id"]]; path=BASE/r["source_path"]; lines=path.read_text(encoding="utf8").splitlines()
        text=item["normalized_requirement"].strip()
        line=int(re.search(r"line\s+(\d+)",r["source_location"]).group(1))
        actual=lines[line-1].strip() if 1<=line<=len(lines) else ""
        exact=[i+1 for i,v in enumerate(lines) if v.strip()==text]
        similar=difflib.get_close_matches(text,[v.strip() for v in lines],n=1,cutoff=0.75)
        if len(exact)>1:
            # Preserve every exact candidate instead of selecting the nearest one.
            category="MULTIPLE_EXACT_MATCHES"; correction=",".join(map(str,exact)); confidence="AMBIGUOUS"
        elif len(exact)==1:
            category="SHIFTED_EXACT_LINE"; correction=exact[0]; confidence="EXACT"
        elif similar:
            category="MODIFIED_TEXT_CANDIDATE"; correction=""; confidence="REVIEW"
        else:
            category="SOURCE_TEXT_ABSENT"; correction=""; confidence="REVIEW"
        counts[category]+=1
        reports.append({"requirement_id":r["requirement_id"],"source":r["source_path"],"old_line":line,
             "original_text":text,"current_line_text":actual,"classification":category,
             "suggested_line":correction,"exact_matches":len(exact),
             "closest_text":similar[0] if similar else "",
             "evidence_level":confidence,"normative_acceptance":"UNREVIEWED",
             "action":"Update pointer only if source version is known unchanged; otherwise retain source revision snapshot."})
    with OUT.open("w",encoding="utf8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(reports[0]),lineterminator="\n");w.writeheader();w.writerows(reports)
    result={"examined":len(reports),"classifications":dict(counts),
            "pointer_changes_applied":0,"normative_acceptances":0,
            "review":str(OUT.relative_to(BASE))}
    SUMMARY.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    return result
if __name__=="__main__":print(json.dumps(analyze(),indent=2))