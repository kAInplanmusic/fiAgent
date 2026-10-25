"""Strict external SCF claim v1 contract. Reject unknown fields and invalid values."""
from datetime import datetime, timezone
import math
from .scf_wire import EnvelopeRejected

REQUIRED = {"claim_id","subject","predicate","value","scope","source","evidence_refs",
            "observed_at","valid_until","confidence"}
OPTIONAL = {"version","dependencies","epistemic_status"}
STATUSES = {"observed","inferred","hypothesis","disputed","verified"}

def _utc(s):
    if not isinstance(s,str):
        raise EnvelopeRejected("claim_invalid_timestamp")
    try:
        d=datetime.fromisoformat(s.replace("Z","+00:00"))
    except ValueError as e:
        raise EnvelopeRejected("claim_invalid_timestamp") from e
    if d.tzinfo is None or d.utcoffset()!=timezone.utc.utcoffset(d):
        raise EnvelopeRejected("claim_timestamp_must_be_utc")
    return d

def validate_claim_v1(data):
    if not isinstance(data,dict) or not REQUIRED.issubset(data) or set(data)-REQUIRED-OPTIONAL:
        raise EnvelopeRejected("claim_schema_fields")
    for name in ("claim_id","subject","predicate","scope","source"):
        if not isinstance(data[name],str) or not data[name].strip() or len(data[name])>512:
            raise EnvelopeRejected("claim_invalid_identity")
    if not isinstance(data["evidence_refs"],list) or not all(isinstance(x,str) and x.strip() for x in data["evidence_refs"]):
        raise EnvelopeRejected("claim_invalid_evidence")
    deps=data.get("dependencies",[])
    if not isinstance(deps,list) or not all(isinstance(x,str) and x.strip() for x in deps):
        raise EnvelopeRejected("claim_invalid_dependencies")
    if type(data.get("version",1)) is not int or data.get("version",1)<1:
        raise EnvelopeRejected("claim_invalid_version")
    conf=data["confidence"]
    if type(conf) not in (float,int) or not math.isfinite(conf) or not 0<=conf<=1:
        raise EnvelopeRejected("claim_invalid_confidence")
    if data.get("epistemic_status","observed") not in STATUSES:
        raise EnvelopeRejected("claim_invalid_status")
    if _utc(data["valid_until"])<=_utc(data["observed_at"]):
        raise EnvelopeRejected("claim_invalid_temporal_order")
    return data
