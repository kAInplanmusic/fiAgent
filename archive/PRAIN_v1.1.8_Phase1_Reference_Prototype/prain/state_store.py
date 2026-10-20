from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from threading import RLock
from typing import Any

def utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

class StateConflict(RuntimeError):
    """Raised when a compare-and-swap write uses a stale version."""

@dataclass(frozen=True)
class StateRecord:
    key: str
    value: Any
    version: int
    updated_at: str

class StateStore:
    """In-memory, single-process versioned store with explicit CAS semantics."""
    def __init__(self):
        self._records = {}
        self._lock = RLock()

    def get(self, key):
        with self._lock:
            rec = self._records.get(key)
            return deepcopy(rec) if rec is not None else None

    def create(self, key, value):
        if not key:
            raise ValueError("key must be non-empty")
        with self._lock:
            if key in self._records:
                raise StateConflict(f"state already exists: {key}")
            rec = StateRecord(key, deepcopy(value), 1, utc_now())
            self._records[key] = rec
            return deepcopy(rec)

    def compare_and_swap(self, key, expected_version, value):
        with self._lock:
            current = self._records.get(key)
            if current is None:
                raise KeyError(key)
            if current.version != expected_version:
                raise StateConflict(
                    f"stale state for {key}: expected {expected_version}, actual {current.version}"
                )
            updated = StateRecord(key, deepcopy(value), current.version + 1, utc_now())
            self._records[key] = updated
            return deepcopy(updated)

    compareAndSwap = compare_and_swap
