from dataclasses import dataclass
from datetime import datetime, timezone
from threading import RLock
from typing import Any, Callable
import uuid

def _now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

@dataclass(frozen=True)
class Event:
    event_id: str
    event_type: str
    payload: dict[str, Any]
    occurred_at: str
    received_at: str
    correlation_id: str
    schema_version: str = "1.0.0"

    @classmethod
    def create(cls, event_type, payload, correlation_id=None, event_id=None):
        if not event_type:
            raise ValueError("event_type must be non-empty")
        now = _now()
        return cls(event_id or str(uuid.uuid4()), event_type, dict(payload), now, now,
                   correlation_id or str(uuid.uuid4()))

class EventBus:
    """Local adapter modelling at-least-once delivery, not a durable broker."""
    def __init__(self):
        self._handlers = {}
        self._processed = {}
        self._lock = RLock()

    def subscribe(self, event_type, consumer_id, handler: Callable[[Event], None]):
        if not event_type or not consumer_id:
            raise ValueError("event_type and consumer_id must be non-empty")
        key = (event_type, consumer_id)
        with self._lock:
            if key in self._handlers:
                raise ValueError(f"consumer already subscribed: {key}")
            self._handlers[key] = handler
            self._processed[key] = set()

    def publish(self, event):
        results = {}
        with self._lock:
            subscriptions = list(self._handlers.items())
        for key, handler in subscriptions:
            event_type, consumer_id = key
            if event_type != event.event_type:
                continue
            with self._lock:
                if event.event_id in self._processed[key]:
                    results[consumer_id] = "duplicate_ignored"
                    continue
                # Reserve before callback to avoid re-entrant duplicate invocation.
                self._processed[key].add(event.event_id)
            try:
                handler(event)
            except Exception:
                # No automatic retry: handler may have performed a side effect before failing.
                results[consumer_id] = "handler_failed_no_auto_retry"
                raise
            results[consumer_id] = "processed"
        return results
