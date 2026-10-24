import unittest
from dataclasses import replace
from prain.scf_wire import sign_envelope, verify_envelope, EnvelopeRejected

KEY = b"k" * 32

def signed(**kw):
    args = dict(key=KEY, message_id="m1", origin_node="node-a", destination_node="node-b",
        tenant="tenant-a", issued_at="2026-10-25T10:00:00Z",
        expires_at="2026-10-25T10:02:00Z", payload={"v": 1})
    args.update(kw)
    return sign_envelope(**args)

def verify(envelope, **kw):
    args = dict(key=KEY, expected_destination="node-b",
                expected_tenant="tenant-a", now="2026-10-25T10:01:00Z")
    args.update(kw)
    return verify_envelope(envelope, **args)

class WireTests(unittest.TestCase):
    def test_valid(self):
        self.assertTrue(verify(signed()))
    def test_tampering_rejected(self):
        with self.assertRaises(EnvelopeRejected):
            verify(replace(signed(), payload={"v": 2}))
    def test_cross_tenant_or_destination_denied(self):
        for kw in (dict(expected_tenant="tenant-b"), dict(expected_destination="node-c")):
            with self.assertRaises(EnvelopeRejected):
                verify(signed(), **kw)
    def test_expiry_and_future_denied(self):
        for now in ("2026-10-25T09:59:00Z", "2026-10-25T10:02:00Z"):
            with self.assertRaises(EnvelopeRejected):
                verify(signed(), now=now)
    def test_wrong_key_rejected(self):
        with self.assertRaises(EnvelopeRejected):
            verify(signed(), key=b"b"*32)
    def test_invalid_version_and_lifetime(self):
        with self.assertRaises(EnvelopeRejected):
            verify(replace(signed(), schema_version=2))
        with self.assertRaises(EnvelopeRejected):
            verify(signed(expires_at="2026-10-25T10:10:00Z"))
    def test_key_length_denied(self):
        with self.assertRaises(EnvelopeRejected):
            signed(key=b"k")