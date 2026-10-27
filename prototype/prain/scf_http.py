"""Authenticated HTTP transport for PRAIN SCF envelopes.

Bind loopback by default. TLS termination and peer key provisioning are
deployment responsibilities. Only the /scf/v1/receive endpoint is exposed.
"""
from __future__ import annotations
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import Request, build_opener, HTTPSHandler, HTTPRedirectHandler, ProxyHandler
from urllib.parse import urlsplit
import ssl
import math
import threading
import hmac
from hashlib import sha256
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
        if claim.source != envelope.origin_node:
            raise EnvelopeRejected("claim_source_origin_mismatch")
        if payload["scope"] != self.tenant or claim.scope != self.tenant:
            raise EnvelopeRejected("claim_tenant_scope_mismatch")
        # The durable inbox updates its projection and receipt in one transaction.
        return self.fabric.ingest_message(envelope.message_id, claim, self.tenant, envelope.issued_at)


def validate_endpoint(url):
    parts = urlsplit(url)
    if (parts.username or parts.password or parts.fragment or parts.query
            or parts.path != "/scf/v1/receive" or not parts.hostname
            or parts.scheme not in ("https", "http")
            or (parts.scheme == "http" and parts.hostname not in ("127.0.0.1", "::1"))):
        raise ValueError("secure_or_loopback_endpoint_required")
    return parts


def receipt_fields(envelope, result):
    return {"message_id": envelope.message_id, "origin_node": envelope.destination_node,
            "destination_node": envelope.origin_node, "tenant": envelope.tenant,
            "request_sha256": sha256(json.dumps(asdict(envelope), sort_keys=True,
                separators=(",", ":"), allow_nan=False).encode()).hexdigest(),
            "result": result}


def receipt_signature(fields, key):
    if not isinstance(key, bytes) or len(key) < 32:
        raise ValueError("untrusted_receipt_key")
    return hmac.new(key, b"PRAIN-SCF-RECEIPT-v1\0" + json.dumps(fields, sort_keys=True,
        separators=(",", ":"), allow_nan=False).encode(), sha256).hexdigest()


def serve(receiver, host="127.0.0.1", port=0, *, ssl_context=None, request_timeout=5, max_connections=32):
    from datetime import datetime, timezone
    if not math.isfinite(request_timeout) or request_timeout <= 0:
        raise ValueError("positive_timeout_required")
    if host not in ("127.0.0.1", "::1", "localhost") and ssl_context is None:
        raise ValueError("tls_required_for_non_loopback_bind")
    if type(max_connections) is not int or not 1 <= max_connections <= 1024:
        raise ValueError("invalid_connection_limit")

    class BoundedServer(ThreadingHTTPServer):
        daemon_threads = True

        def __init__(self, *args):
            self.slots = threading.BoundedSemaphore(max_connections)
            super().__init__(*args)

        def process_request(self, request, client_address):
            if not self.slots.acquire(blocking=False):
                self.shutdown_request(request)
                return
            try:
                super().process_request(request, client_address)
            except BaseException:
                self.slots.release()
                raise

        def process_request_thread(self, request, client_address):
            # Handshake belongs to a bounded worker: an idle TCP peer must not
            # block the main accept loop or create an unbounded thread pool.
            try:
                request.settimeout(request_timeout)
                if ssl_context is not None:
                    request = ssl_context.wrap_socket(request, server_side=True,
                                                      do_handshake_on_connect=False)
                    request.do_handshake()
                self.finish_request(request, client_address)
            except (TimeoutError, ssl.SSLError, ConnectionError):
                pass
            except Exception:
                self.handle_error(request, client_address)
            finally:
                self.shutdown_request(request)
                self.slots.release()

    class Handler(BaseHTTPRequestHandler):
        def setup(self):
            super().setup()
            self.connection.settimeout(request_timeout)

        def do_POST(self):
            if self.path != "/scf/v1/receive":
                self.send_error(404)
                return
            try:
                if self.headers.get("Transfer-Encoding") or len(self.headers.get_all("Content-Length", [])) != 1:
                    self.send_error(400)
                    return
                size = int(self.headers.get("Content-Length", "-1"))
                if size < 0 or size > 65536:
                    self.send_error(413)
                    return
                raw = self.rfile.read(size)
                if len(raw) != size:
                    raise ValueError("truncated_request")
                data = json.loads(raw)
                now = datetime.now(timezone.utc).isoformat()
                result = receiver.accept(data, now)
                envelope = WireEnvelope(**data)
                fields = receipt_fields(envelope, asdict(result))
                signature = receipt_signature(fields, receiver.peer_keys[envelope.origin_node])
                reply = json.dumps({**asdict(result), "receipt": fields,
                                    "receipt_signature": signature}).encode()
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
    return BoundedServer((host, port), Handler)


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def send(url, envelope, timeout=5, *, ssl_context=None):
    validate_endpoint(url)
    if not isinstance(envelope, WireEnvelope):
        raise TypeError("signed_envelope_required")
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("positive_timeout_required")
    if ssl_context is not None and (not ssl_context.check_hostname or ssl_context.verify_mode != ssl.CERT_REQUIRED):
        raise ValueError("verified_tls_context_required")
    data = json.dumps(asdict(envelope), sort_keys=True, allow_nan=False).encode()
    if len(data) > 65536:
        raise ValueError("request_too_large")
    request = Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    # Explicitly disable ambient proxies and redirects: signed tenant data must
    # reach only the configured peer, even if the peer replies with Location.
    opener = build_opener(ProxyHandler({}), _NoRedirect(), HTTPSHandler(context=ssl_context))
    with opener.open(request, timeout=timeout) as response:
        raw = response.read(65537)
        if len(raw) > 65536:
            raise ValueError("response_too_large")
        result = json.loads(raw)
        if not isinstance(result, dict):
            raise ValueError("invalid_receipt")
        return result
