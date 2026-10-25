"""Authenticated HTTP transport for PRAIN SCF envelopes.

Bind loopback by default. TLS termination and peer key provisioning are
deployment responsibilities. Only the /scf/v1/receive endpoint is exposed.
"""
from __future__ import annotations
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import Request, urlopen
from .scf_wire import WireEnvelope, verify_envelope, EnvelopeRejected
from .durable_semantics import DurableSemanticFabric
from .scf import SemanticClaim
from .scf_delivery import SCFDeliveryQueue
from .scf_contract import validate_claim_v1
import json


class SCFHTTPReceiver:
    def __init__(self, *, db_path, node_id, tenant, peer_keys):
        self.fabric = DurableSemanticFabric(db_path)
        self.queue = SCFDeliveryQueue(db_path)
        self.node_id = node_id
        self.tenant = tenant
        self.peer_keys = dict(peer_keys)

    def accept(self, body, now):
        if not isinstance(body, dict):
            raise EnvelopeRejected("invalid_body")
        envelope = WireEnvelope(**body)
        key = self.peer_keys.get(envelope.origin_node)
        if key is None:
            raise EnvelopeRejected("untrusted_peer")
        verify_envelope(envelope, key=key, expected_destination=self.node_id,
                        expected_tenant=self.tenant, now=now)
        payload = envelope.payload
        if set(payload) != {"claim", "scope"}:
            raise EnvelopeRejected("invalid_payload_contract")
        raw = payload["claim"]
        if not isinstance(raw, dict):
            raise EnvelopeRejected("invalid_claim")
        validate_claim_v1(raw)
        try:
            claim = SemanticClaim(**{**raw, "evidence_refs": tuple(raw["evidence_refs"]),
                                        "dependencies": tuple(raw.get("dependencies", ()))})
        except (TypeError, KeyError, ValueError) as exc:
            raise EnvelopeRejected("invalid_claim") from exc
        if payload["scope"] != self.tenant or claim.scope != self.tenant:
            raise EnvelopeRejected("claim_tenant_scope_mismatch")
        # The durable inbox updates its projection and receipt in one transaction.
        return self.fabric.ingest_message(envelope.message_id, claim, self.tenant, envelope.issued_at)


def serve(receiver, host="127.0.0.1", port=0):
    from datetime import datetime, timezone
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            if self.path != "/scf/v1/receive":
                self.send_error(404)
                return
            try:
                size = int(self.headers.get("Content-Length", "-1"))
                if size < 0 or size > 65536:
                    self.send_error(413)
                    return
                raw = self.rfile.read(size)
                data = json.loads(raw)
                now = datetime.now(timezone.utc).isoformat()
                result = receiver.accept(data, now)
                reply = json.dumps(asdict(result)).encode()
                status = 200
            except (EnvelopeRejected, ValueError, TypeError, KeyError, json.JSONDecodeError):
                reply = b'{"error":"message_rejected"}'
                status = 400
            except Exception:
                reply = b'{"error":"internal_error"}'
                status = 500
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(reply)))
            self.end_headers()
            self.wfile.write(reply)
        def log_message(self, *args):
            pass
    return ThreadingHTTPServer((host, port), Handler)


def send(url, envelope, timeout=5):
    if not isinstance(envelope, WireEnvelope):
        raise TypeError("signed_envelope_required")
    data = json.dumps(asdict(envelope), sort_keys=True).encode()
    request = Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read(65536))