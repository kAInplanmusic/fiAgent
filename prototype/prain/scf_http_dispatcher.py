"""One-at-a-time durable SCF HTTP delivery driver.

Never blindly retries ambiguous HTTP failures. Caller must reconcile UNKNOWN
against receiver's authoritative inbox before requeueing.
"""
from dataclasses import asdict
from urllib.error import HTTPError, URLError
from .scf_delivery import SCFDeliveryQueue
from .scf_http import send
from .scf_wire import WireEnvelope


class SCFHTTPDispatcher:
    def __init__(self, queue: SCFDeliveryQueue, endpoint: str, timeout=5):
        if not isinstance(endpoint, str) or not (endpoint.startswith("https://") or endpoint.startswith("http://127.0.0.1:")):
            raise ValueError("secure_or_loopback_endpoint_required")
        self.queue, self.endpoint, self.timeout = queue, endpoint, timeout

    def enqueue(self, envelope: WireEnvelope):
        if not isinstance(envelope, WireEnvelope):
            raise TypeError("signed_envelope_required")
        return self.queue.publish(envelope.message_id, asdict(envelope))

    def deliver_one(self):
        item = self.queue.claim()
        if item is None:
            return None
        message_id = item["message_id"]
        try:
            response = send(self.endpoint, WireEnvelope(**item["message"]), timeout=self.timeout)
            if response.get("claim_id") is None or response.get("decision") is None:
                self.queue.outcome(message_id, "UNKNOWN")
                return "UNKNOWN"
            self.queue.outcome(message_id, "SUCCEEDED")
            return "SUCCEEDED"
        except HTTPError as exc:
            # A definitive 4xx contract rejection cannot be retried unchanged.
            if exc.code in (400, 401, 403, 404, 413, 422):
                self.queue.outcome(message_id, "FAILED")
                return "FAILED"
            self.queue.outcome(message_id, "UNKNOWN")
            return "UNKNOWN"
        except (URLError, TimeoutError, ConnectionError, OSError, ValueError):
            self.queue.outcome(message_id, "UNKNOWN")
            return "UNKNOWN"
