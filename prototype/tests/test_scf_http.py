import tempfile
import threading
import unittest
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError

from prain.scf_http import SCFHTTPReceiver, serve, send
from prain.scf_wire import sign_envelope

KEY = b"x" * 32

class HTTPTransportTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        path = str(Path(tmp.name) / "receiver.sqlite")
        self.receiver = SCFHTTPReceiver(db_path=path, node_id="node-b", tenant="tenant-1",
                                        peer_keys={"node-a": KEY})
        self.server = serve(self.receiver)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)
        self.url = "http://127.0.0.1:%d/scf/v1/receive" % self.server.server_port

    def envelope(self, message_id="m1", key=KEY):
        now = datetime.now(timezone.utc)
        claim = dict(claim_id="claim-1", subject="item", predicate="state",
                     value="ready", scope="tenant-1", source="node-a",
                     evidence_refs=["evidence-ref"], observed_at=(now-timedelta(seconds=5)).isoformat(),
                     valid_until=(now+timedelta(minutes=2)).isoformat(),
                     confidence=0.9)
        return sign_envelope(key=key, message_id=message_id, origin_node="node-a",
                             destination_node="node-b", tenant="tenant-1",
                             issued_at=(now-timedelta(seconds=5)).isoformat(),
                             expires_at=(now+timedelta(minutes=1)).isoformat(),
                             payload={"claim": claim, "scope": "tenant-1"})

    def test_two_process_style_transport_roundtrip_and_duplicate(self):
        message = self.envelope()
        self.assertEqual(send(self.url, message)["decision"], "adopt")
        self.assertEqual(send(self.url, message)["decision"], "adopt")
        self.assertEqual(len(self.receiver.fabric.decisions()), 1)

    def test_bad_signature_rejected(self):
        with self.assertRaises(HTTPError) as error:
            send(self.url, self.envelope(key=b"wrong" * 8))
        self.assertEqual(error.exception.code, 400)

    def test_unknown_origin_rejected(self):
        from dataclasses import replace
        with self.assertRaises(HTTPError):
            send(self.url, replace(self.envelope(), origin_node="untrusted"))

    def test_restart_receiver_uses_persisted_inbox(self):
        message = self.envelope()
        send(self.url, message)
        receiver2 = SCFHTTPReceiver(db_path=self.receiver.fabric._db_path,
                    node_id="node-b", tenant="tenant-1", peer_keys={"node-a": KEY})
        self.assertEqual(receiver2.accept(asdict(message), datetime.now(timezone.utc).isoformat()).decision, "adopt")
        self.assertEqual(len(receiver2.fabric.decisions()), 1)
    def test_scf_v1_schema_rejects_malformed_fields(self):
        from dataclasses import replace
        original = self.envelope()
        for field,value in (("confidence",float("nan")),("version",True),
                            ("epistemic_status","invented"),("dependencies","not-array"),
                            ("evidence_refs",[""]),("unknown",42)):
            raw = dict(original.payload["claim"])
            raw[field] = value
            msg = self.envelope(message_id="bad-" + field)
            body = asdict(msg)
            body["payload"]["claim"] = raw
            with self.assertRaises(HTTPError) as error:
                from urllib.request import Request, urlopen
                import json
                req = Request(self.url, data=json.dumps(body).encode(), method="POST")
                urlopen(req,timeout=3)
            self.assertEqual(error.exception.code,400)