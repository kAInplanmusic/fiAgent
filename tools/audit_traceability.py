"""Audit historical requirement candidate rows without auto-approving them."""
import csv
import json
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
SOURCE = BASE / "TRACEABILITY" / "REQUIREMENT_TRACEABILITY_MATRIX.csv"
REPORT = BASE / "TRACEABILITY" / "RTM_AUDIT_STATUS.json"
REQUIRED = {"requirement_id", "source_archive", "source_path", "source_location",
            "normalized_requirement", "disposition", "canonical_reference",
            "implementation_reference", "test_reference", "evidence", "status", "reviewer_note"}
VALID = {"RETAIN", "RETAINED", "EXTEND", "EXTENDED", "SUPERSEDE", "SUPERSEDED",
         "DEFER", "DEFERRED", "OPEN", "UNASSESSED"}
def audit():
    with SOURCE.open(encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        if not REQUIRED.issubset(set(reader.fieldnames or ())):
            raise ValueError("missing_required_columns")
        rows = list(reader)
    ids = [r["requirement_id"] for r in rows]
    duplicates = len(ids) - len(set(ids))
    counts = Counter((r["disposition"] or "").upper() for r in rows)
    invalid_disposition = sum(v for k,v in counts.items() if k not in VALID)
    unresolved = sum(1 for r in rows if
        (r["disposition"] or "").upper() in {"UNASSESSED", "OPEN", "DEFER", "DEFERRED"}
        or any(not r[k].strip() or r[k].strip() == "TO_MAP"
               for k in ("canonical_reference", "implementation_reference", "test_reference")))
    status = {"source": str(SOURCE.relative_to(BASE)),
        "total_rows": len(rows), "duplicate_ids": duplicates,
        "dispositions": dict(sorted(counts.items())),
        "invalid_dispositions": invalid_disposition,
        "unresolved_rows": unresolved,
        "closure_ready": len(rows) > 0 and duplicates == 0 and invalid_disposition == 0 and unresolved == 0,
        "note": "Automated structural audit only; human semantic adjudication and evidence validation still mandatory."}
    REPORT.write_text(json.dumps(status, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return status

if __name__ == "__main__":
    print(json.dumps(audit(), indent=2, sort_keys=True))
