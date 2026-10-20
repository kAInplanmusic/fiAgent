from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any
import hashlib, json, uuid
from copy import deepcopy

def _now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

@dataclass(frozen=True)
class EvidenceEntry:
    entry_id: str
    recorded_at: str
    kind: str
    subject: str
    payload: dict[str, Any]
    previous_hash: str
    entry_hash: str

class EvidenceLedger:
    """In-memory hash chain; integrity check is not a substitute for signatures."""
    GENESIS = "0" * 64

    def __init__(self):
        self._entries = []

    def append(self, kind, subject, payload):
        if not kind or not subject:
            raise ValueError("kind and subject are required")
        base = {
            "entry_id": str(uuid.uuid4()), "recorded_at": _now(), "kind": kind,
            "subject": subject, "payload": deepcopy(payload),
            "previous_hash": self._entries[-1].entry_hash if self._entries else self.GENESIS
        }
        digest = hashlib.sha256(json.dumps(base, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        entry = EvidenceEntry(**base, entry_hash=digest)
        self._entries.append(entry)
        return entry

    def entries(self):
        return list(self._entries)

    def verify(self):
        previous = self.GENESIS
        for entry in self._entries:
            base = asdict(entry)
            digest = base.pop("entry_hash")
            if entry.previous_hash != previous:
                return False
            expected = hashlib.sha256(json.dumps(base, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            if digest != expected:
                return False
            previous = digest
        return True
