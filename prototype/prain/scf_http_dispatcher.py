"""One-at-a-time durable SCF HTTP delivery driver.

Never blindly retries ambiguous HTTP failures. Caller must reconcile UNKNOWN
against receiver's authoritative inbox before requeueing.
"""
from dataclasses import asdict
from urllib.error import HTTPError, URLError
from .scf_delivery import SCFDeliveryQueue
from .scf_http import send, validate_endpoint, receipt_fields, receipt_signature
import hmac
from .scf_wire import WireEnvelope
from .scf import DECISIONS


class SCFHTTPDispatcher:
    def __init__(self, queue: SCFDeliveryQueue, endpoint: str, timeout=5, *, ssl_context=None, receipt_key=None):
        validate_endpoint(endpoint)
        receipt_signature({}, receipt_key)
        self.queue, self.endpoint, self.timeout = queue, endpoint, timeout
        self.ssl_context, self.receipt_key = ssl_context, receipt_key

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
            envelope = WireEnvelope(**item["message"])
            response = send(self.endpoint, envelope, timeout=self.timeout, ssl_context=self.ssl_context)
            fields = response.get("receipt")
            result = fields.get("result") if isinstance(fields, dict) else None
            valid = (isinstance(result, dict)
                     and result.get("claim_id") == envelope.payload.get("claim", {}).get("claim_id")
                     and result.get("decision") in DECISIONS
                     and fields == receipt_fields(envelope, result))
            signature = response.get("receipt_signature")
            valid = valid and isinstance(signature, str) and hmac.compare_digest(
                signature, receipt_signature(fields, self.receipt_key))
            if not valid:
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
        except (URLError, TimeoutError, ConnectionError, OSError, ValueError, TypeError):
            self.queue.outcome(message_id, "UNKNOWN")
            return "UNKNOWN"
