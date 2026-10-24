"""Authenticated SCF wire envelopes, transport-neutral and fail-closed.

The verifier requires a shared per-peer key provisioned through a trusted channel.
Replay protection is held in the durable inbox, not in this signature verifier.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import hmac
import json
import math
from datetime import datetime, timezone


class EnvelopeRejected(ValueError):
    pass


@dataclass(frozen=True)
class WireEnvelope:
    message_id: str
    origin_node: str
    destination_node: str
    tenant: str
    schema_version: int
    issued_at: str
    expires_at: str
    payload: dict
    signature: str


def _canonical(fields):
    return json.dumps(fields, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def _fields(envelope):
    return {k: getattr(envelope, k) for k in ("message_id", "origin_node", "destination_node",
            "tenant", "schema_version", "issued_at", "expires_at", "payload")}


def sign_envelope(*, key: bytes, message_id: str, origin_node: str, destination_node: str,
                  tenant: str, issued_at: str, expires_at: str, payload: dict):
    if not isinstance(key, bytes) or len(key) < 32:
        raise EnvelopeRejected("weak_signing_key")
    e = WireEnvelope(message_id, origin_node, destination_node, tenant, 1,
                     issued_at, expires_at, payload, "")
    _validate_structure(e)
    signature = hmac.new(key, _canonical(_fields(e)), sha256).hexdigest()
    return WireEnvelope(**{**_fields(e), "signature": signature})


def _time(text):
    if not isinstance(text, str):
        raise EnvelopeRejected("invalid_time")
    try:
        d = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise EnvelopeRejected("invalid_time") from exc
    if d.tzinfo is None or d.utcoffset() != timezone.utc.utcoffset(d):
        raise EnvelopeRejected("time_must_be_utc")
    return d


def _validate_structure(envelope):
    if not isinstance(envelope, WireEnvelope):
        raise EnvelopeRejected("invalid_envelope")
    for item in (envelope.message_id, envelope.origin_node, envelope.destination_node, envelope.tenant):
        if not isinstance(item, str) or not item.strip():
            raise EnvelopeRejected("missing_routing_identity")
    if type(envelope.schema_version) is not int or envelope.schema_version != 1:
        raise EnvelopeRejected("unsupported_schema")
    if not isinstance(envelope.payload, dict):
        raise EnvelopeRejected("invalid_payload")
    if _time(envelope.expires_at) <= _time(envelope.issued_at):
        raise EnvelopeRejected("invalid_lifetime")
    try:
        _canonical(_fields(envelope))
    except (TypeError, ValueError, OverflowError) as exc:
        raise EnvelopeRejected("invalid_canonical_payload") from exc


def verify_envelope(envelope: WireEnvelope, *, key: bytes, expected_destination: str,
                    expected_tenant: str, now: str, max_lifetime_seconds: int = 300):
    _validate_structure(envelope)
    if not isinstance(key, bytes) or len(key) < 32:
        raise EnvelopeRejected("untrusted_key")
    if envelope.destination_node != expected_destination or envelope.tenant != expected_tenant:
        raise EnvelopeRejected("wrong_destination_or_tenant")
    issued, expires, moment = _time(envelope.issued_at), _time(envelope.expires_at), _time(now)
    if (expires - issued).total_seconds() > max_lifetime_seconds:
        raise EnvelopeRejected("lifetime_excessive")
    if moment < issued or moment >= expires:
        raise EnvelopeRejected("stale_or_future_message")
    signature = hmac.new(key, _canonical(_fields(envelope)), sha256).hexdigest()
    if not isinstance(envelope.signature, str) or not hmac.compare_digest(signature, envelope.signature):
        raise EnvelopeRejected("invalid_signature")
    return True