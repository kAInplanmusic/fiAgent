"""Resolve RTM origin lines against local files and archived ZIP members.

This supplies source evidence and conservative, reviewable dispositions.
It never equates source verification with acceptance or implementation.
"""
import csv,hashlib,json,re,zipfile
from collections import Counter
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
SRC=BASE/"TRACEABILITY/REQUIREMENT_TRACEABILITY_MATRIX.csv"
OUT=BASE/"TRACEABILITY/RTM_SOURCE_RESOLUTION.csv"
SUMMARY=BASE/"TRACEABILITY/RTM_SOURCE_RESOLUTION_SUMMARY.json"

def resolve(path, cache):
    if path.startswith("historical_zip:"):
        spec=path[len("historical_zip:"):]
        if "!/" not in spec:return None,"invalid_zip_locator"
        zp, member=spec.split("!/",1)
        file=BASE/zp
        if not file.is_file():return None,"zip_missing"
        try:
            if zp not in cache:
                with zipfile.ZipFile(file) as z:
                    cache[zp]={name:z.read(name).decode("utf-8",errors="replace").splitlines() for name in z.namelist() if not name.endswith("/")}
            return cache[zp].get(member), "zip_member_found" if member in cache[zp] else "zip_member_missing"
        except (OSError,zipfile.BadZipFile,RuntimeError,ValueError):return None,"zip_unreadable"
    file=BASE/path
    if not file.is_file():return None,"source_missing"
    try:return file.read_text(encoding="utf-8").splitlines(),"local_file_found"
    except (OSError,UnicodeError):return None,"source_unreadable"

def run():
    with SRC.open(encoding="utf-8",newline="") as f: rows=list(csv.DictReader(f))
    cache={}; counts=Counter(); evidence=[]; seen={}
    for row in rows:
        path=row["source_path"]; loc=row["source_location"]
        lines,loc_status=resolve(path,cache)
        match=re.search(r"\bline\s+(\d+)\b",loc,re.I)
        line=int(match.group(1)) if match else None
        found=lines is not None and line is not None and 1<=line<=len(lines)
        actual=lines[line-1].strip() if found else ""
        original=row["normalized_requirement"].strip()
        verified=found and (actual==original or actual.lstrip("-* ").strip()==original.lstrip("-* ").strip())
        # Many historical archive paths use headings or extraction normalization:
        # mismatches stay unverified until human review.
        if verified: reason="EXACT_SOURCE_LINE"
        elif found: reason="SOURCE_LINE_DIFFERS"
        else: reason=loc_status if lines is None else "LINE_MISSING_OR_OUT_OF_RANGE"
        counts[reason]+=1
        digest=hashlib.sha256(original.encode()).hexdigest()
        prior=seen.get(digest,"")
        seen.setdefault(digest,row["requirement_id"])
        evidence.append({"requirement_id":row["requirement_id"],"source_path":path,"source_location":loc,
          "source_result":reason,"content_sha256":digest,
          "exact_duplicate_of":prior,"proposed_disposition":"REVIEW_DUPLICATE" if prior else "REVIEW_NORMATIVITY",
          "normative_decision":"UNREVIEWED",
          "review_note":"Same text does not prove supersession" if prior else "Confirm normative status and effective version"})
    with OUT.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(evidence[0]),lineterminator="\n");w.writeheader();w.writerows(evidence)
    result={"total":len(rows),"source_results":dict(sorted(counts.items())),
      "duplicate_text_candidates":sum(bool(x["exact_duplicate_of"]) for x in evidence),
      "accepted":0,"unreviewed":len(rows),"output":str(OUT.relative_to(BASE)),
      "note":"Archive/line verification plus exact text-duplicate suggestions only. Not semantic signoff."}
    SUMMARY.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return result
if __name__=="__main__":print(json.dumps(run(),ensure_ascii=False,indent=2))
