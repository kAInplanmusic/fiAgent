"""Strict B acceptance gate validator. Fails closed without evidence and signoff."""
import json
from pathlib import Path
BASE = Path(__file__).resolve().parents[1]
SOURCE = BASE / "PHASE1_STRICT_B_GATE_STATUS.json"
REQUIRED = tuple("G%02d" % n for n in range(10))

def validate(document):
    errors = []
    if document.get("schema_version") != 1 or document.get("project") != "PRAIN":
        errors.append("invalid_gate_schema")
    gates = document.get("gates", {})
    if not isinstance(gates, dict) or set(gates) != set(REQUIRED):
        errors.append("incomplete_gate_inventory")
        gates = {} if not isinstance(gates, dict) else gates
    evidences = document.get("gate_evidence", {})
    if not isinstance(evidences, dict):
        evidences = {}
        errors.append("invalid_evidence_map")
    for gate in REQUIRED:
        if gates.get(gate) != "ACCEPTED":
            errors.append(gate + ":not_accepted")
        if not isinstance(evidences.get(gate), list) or not evidences[gate]:
            errors.append(gate + ":evidence_missing")
    signoff = document.get("independent_review")
    if not isinstance(signoff, dict) or not all(isinstance(signoff.get(k), str) and signoff[k].strip() for k in ("reviewer", "report", "approval_id")):
        errors.append("independent_review_missing")
    if document.get("blocking_requirements"):
        errors.append("blockers_remain")
    phase = document.get("phase1", {})
    if not isinstance(phase, dict) or phase.get("strict_b_accepted") is not True:
        errors.append("strict_b_not_approved")
    if not isinstance(phase, dict) or phase.get("status") != "PHASE1_GREEN_STRICT_B":
        errors.append("phase1_not_green")
    return errors

if __name__ == "__main__":
    document = json.loads(SOURCE.read_text())
    errors = validate(document)
    print(json.dumps({"phase1_green": not errors, "fail_closed": bool(errors), "reasons": errors}, indent=2))
    raise SystemExit(1 if errors else 0)
