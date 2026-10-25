"""G01 source-evidence audit for every historical RTM candidate.

Checks source inventory membership and location grammar without marking semantic
requirements accepted. Archive-contained paths require separate archive extraction.
"""
import csv
import json
import re
from collections import Counter
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
RTM=BASE/"TRACEABILITY/REQUIREMENT_TRACEABILITY_MATRIX.csv"
REGISTER=BASE/"TRACEABILITY/SOURCE_REGISTER.csv"
OUTPUT=BASE/"TRACEABILITY/RTM_SOURCE_COVERAGE.json"

def audit():
    with RTM.open(encoding="utf-8",newline="") as f:
        entries=list(csv.DictReader(f))
    with REGISTER.open(encoding="utf-8",newline="") as f:
        sources=list(csv.DictReader(f))
    names={str(v).strip() for row in sources for v in row.values() if isinstance(v,str) and v.strip()}
    reasons=Counter()
    samples={}
    for entry in entries:
        path=entry.get("source_path","").strip()
        loc=entry.get("source_location","").strip()
        if not path or path=="TO_MAP":
            issue="missing_path"
        elif not loc:
            issue="missing_location"
        elif path.startswith("/") or ".." in Path(path).parts:
            issue="unsafe_path"
        elif (BASE/path).is_file() and re.fullmatch(r"line\s+\d+",loc,re.I):
            line=int(loc.split()[-1])
            try:
                data=(BASE/path).read_text(encoding="utf-8").splitlines()
                issue="source_line_out_of_range" if line<1 or line>len(data) else "local_line_located"
            except UnicodeError:
                issue="local_source_not_utf8"
        elif path in names or any(path in name for name in names if len(name)<2048):
            issue="registered_archive_source_unverified"
        else:
            issue="archive_source_unverified"
        reasons[issue]+=1
        samples.setdefault(issue,entry.get("requirement_id"))
    count=len(entries)
    result={"total_candidates":count,"unique_ids":len({r.get("requirement_id") for r in entries}),
            "source_audit_counts":dict(sorted(reasons.items())),
            "sample_requirement_ids":samples,
            "semantically_accepted_by_this_tool":0,
            "all_source_locations_verified":reasons.get("local_line_located",0)==count and count>0,
            "note":"Archive-contained evidence requires archive-member checks; no automatic normative approval."}
    OUTPUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return result

if __name__=="__main__":
    print(json.dumps(audit(),indent=2,sort_keys=True))
