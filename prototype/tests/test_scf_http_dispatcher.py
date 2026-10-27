import tempfile
import threading
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from prain.scf_delivery import SCFDeliveryQueue
from prain.scf_http import SCFHTTPReceiver, serve
from prain.scf_http_dispatcher import SCFHTTPDispatcher
from prain.scf_wire import sign_envelope


class DispatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        self.queue = SCFDeliveryQueue(str(base / "sender.sqlite"))
        self.receiver = SCFHTTPReceiver(db_path=str(base / "receiver.sqlite"),
            node_id="b", tenant="tenant", peer_keys={"a": b"k"*32})
        self.server = serve(self.receiver)
        t = threading.Thread(target=self.server.serve_forever, daemon=True)
        t.start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)
        self.url = "http://127.0.0.1:%d/scf/v1/receive" % self.server.server_port

    def message(self, key=b"k"*32, msg="m1"):
        now = datetime.now(timezone.utc)
        claim = dict(claim_id="c", subject="object", predicate="state", value="ok",
                     scope="tenant", source="a", evidence_refs=["proof"],
                     observed_at=(now-timedelta(seconds=2)).isoformat(),
                     valid_until=(now+timedelta(minutes=2)).isoformat(), confidence=0.9)
        return sign_envelope(key=key, message_id=msg, origin_node="a",
            destination_node="b", tenant="tenant", issued_at=(now-timedelta(seconds=2)).isoformat(),
            expires_at=(now+timedelta(minutes=1)).isoformat(),
            payload={"claim": claim, "scope": "tenant"})

    def test_delivers_once(self):
        d = SCFHTTPDispatcher(self.queue, self.url, receipt_key=b"k"*32)
        self.assertTrue(d.enqueue(self.message()))
        self.assertEqual(d.deliver_one(), "SUCCEEDED")
        self.assertEqual(self.queue.status("m1")["status"], "SUCCEEDED")
        self.assertIsNone(d.deliver_one())
        self.assertEqual(len(self.receiver.fabric.decisions()), 1)

    def test_bad_signature_terminal_failure(self):
        d = SCFHTTPDispatcher(self.queue, self.url, receipt_key=b"k"*32)
        d.enqueue(self.message(key=b"wrongkey"*4))
        self.assertEqual(d.deliver_one(), "FAILED")

    def test_connection_error_unknown_not_retry(self):
        d = SCFHTTPDispatcher(self.queue, "http://127.0.0.1:1/scf/v1/receive", timeout=0.3, receipt_key=b"k"*32)
        d.enqueue(self.message())
        self.assertEqual(d.deliver_one(), "UNKNOWN")
        self.assertIsNone(d.deliver_one())
        self.assertEqual(SCFDeliveryQueue(self.queue.database).status("m1")["status"], "UNKNOWN")

    def test_recovery_requires_reconciliation(self):
        d = SCFHTTPDispatcher(self.queue, self.url, receipt_key=b"k"*32)
        d.enqueue(self.message())
        item = self.queue.claim()
        self.assertEqual(item["message_id"], "m1")
        self.assertEqual(self.queue.recover(), 1)
        self.assertIsNone(d.deliver_one())
