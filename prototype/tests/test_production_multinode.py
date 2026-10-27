"""Spawn/TLS fault tests with separate stores on ONE host, not two-host proof."""
import json
import multiprocessing as mp
import os
from pathlib import Path
import shutil
import ssl
import subprocess
import tempfile
import unittest
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError, URLError
from prain.scf_http import SCFHTTPReceiver, serve, send
from prain.scf_wire import sign_envelope
from prain.scf_delivery import SCFDeliveryQueue
from prain.durable_semantics import DurableSemanticFabric
KEY = b"test-only-ephemeral-peer-key-00001"


def receiver_process(db, cert, key, pipe, port, crash):
    class Receiver(SCFHTTPReceiver):
        def accept(self, body, now):
            result = super().accept(body, now)
            if crash:
                os._exit(73)
            return result
    receiver = Receiver(db_path=db, node_id="node-b", tenant="t", peer_keys={"node-a": KEY})
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(cert, key)
    server = serve(receiver, port=port, ssl_context=context)
    pipe.send((server.server_port, os.getpid()))
    pipe.close()
    server.serve_forever(poll_interval=0.05)


@unittest.skipUnless(shutil.which("openssl"), "openssl required for ephemeral TLS fixture")
class ProductionMultinodeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name)
        cls.cert, cls.key = cls.root / "node.crt", cls.root / "node.key"
        subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes",
                        "-keyout", str(cls.key), "-out", str(cls.cert), "-days", "1",
                        "-subj", "/CN=localhost", "-addext", "subjectAltName=DNS:localhost"],
                       check=True, capture_output=True, timeout=20)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def setUp(self):
        self.case = tempfile.TemporaryDirectory(dir=self.root)
        self.addCleanup(self.case.cleanup)
        self.db = str(Path(self.case.name) / "receiver.sqlite")
        self.queue = SCFDeliveryQueue(str(Path(self.case.name) / "sender.sqlite"))
        self.context = ssl.create_default_context(cafile=str(self.cert))
        self.processes = []
        self.addCleanup(self.stop_all)

    def stop_all(self):
        for process in self.processes:
            if process.is_alive():
                process.terminate()
            process.join(timeout=5)
            if process.is_alive():
                process.kill()
                process.join(timeout=5)

    def start(self, port=0, crash=False):
        ctx = mp.get_context("spawn")
        reader, writer = ctx.Pipe(duplex=False)
        process = ctx.Process(target=receiver_process,
                              args=(self.db, str(self.cert), str(self.key), writer, port, crash))
        process.start()
        writer.close()
        self.processes.append(process)
        self.assertTrue(reader.poll(15), "receiver did not become ready")
        port, pid = reader.recv()
        reader.close()
        self.assertNotEqual(pid, os.getpid())
        return process, port, f"https://localhost:{port}/scf/v1/receive"

    def message(self, message_id="message-1", signing_key=KEY):
        now = datetime.now(timezone.utc)
        claim = dict(claim_id="claim-" + message_id, subject="item", predicate="state",
                     value="ready", scope="t", source="node-a", evidence_refs=["fixture-evidence"],
                     observed_at=(now-timedelta(seconds=2)).isoformat(),
                     valid_until=(now+timedelta(minutes=2)).isoformat(), confidence=0.9)
        return sign_envelope(key=signing_key, message_id=message_id, origin_node="node-a",
                             destination_node="node-b", tenant="t",
                             issued_at=(now-timedelta(seconds=2)).isoformat(),
                             expires_at=(now+timedelta(minutes=1)).isoformat(),
                             payload={"claim": claim, "scope": "t"})

    def request(self, url, message, context=None):
        return send(url, message, ssl_context=context or self.context, timeout=3)

    def test_tls_process_store_replay_after_restart(self):
        process, port, url = self.start()
        message = self.message()
        self.queue.publish(message.message_id, asdict(message))
        self.assertEqual(self.request(url, message)["decision"], "adopt")
        process.terminate()
        process.join(5)
        _, _, url = self.start(port=port)
        for _ in range(3):
            self.assertEqual(self.request(url, message)["decision"], "adopt")
        self.assertEqual(len(DurableSemanticFabric(self.db).decisions()), 1)
        self.assertNotEqual(self.queue.database, self.db)
        with self.assertRaises(URLError):
            self.request(url, message, ssl.create_default_context())

    def test_commit_before_ack_crash_reconciliation(self):
        process, port, url = self.start(crash=True)
        message = self.message()
        self.queue.publish(message.message_id, asdict(message))
        self.assertIsNotNone(self.queue.claim())
        with self.assertRaises((OSError, ConnectionError)):
            self.request(url, message)
        process.join(5)
        self.assertEqual(process.exitcode, 73)
        self.assertEqual(self.queue.recover(), 1)
        self.assertIsNone(self.queue.claim())
        self.assertEqual(self.queue.status(message.message_id)["status"], "UNKNOWN")
        _, _, url = self.start(port=port)
        self.assertEqual(self.request(url, message)["decision"], "adopt")
        self.queue.reconcile(message.message_id, "SUCCEEDED", "test-only:receiver-durable-inbox")
        self.assertEqual(len(DurableSemanticFabric(self.db).decisions()), 1)
        self.assertEqual(self.queue.status(message.message_id)["attempts"], 1)

    def test_outage_blocks_blind_retry(self):
        process, port, url = self.start()
        process.terminate()
        process.join(5)
        message = self.message()
        self.queue.publish(message.message_id, asdict(message))
        self.queue.claim()
        with self.assertRaises(URLError):
            self.request(url, message)
        self.queue.outcome(message.message_id, "UNKNOWN")
        self.assertIsNone(self.queue.claim())
        _, _, url = self.start(port=port)
        self.assertEqual(len(DurableSemanticFabric(self.db).decisions()), 0)
        self.queue.reconcile(message.message_id, "NOT_EXECUTED", "test-only:isolated-inbox-empty")
        self.assertIsNotNone(self.queue.claim())
        self.assertEqual(self.request(url, message)["decision"], "adopt")
        self.queue.outcome(message.message_id, "SUCCEEDED")
        self.assertEqual(len(DurableSemanticFabric(self.db).decisions()), 1)

    def test_poison_does_not_stall_valid_message(self):
        _, _, url = self.start()
        with self.assertRaises(HTTPError) as error:
            self.request(url, self.message("poison", b"wrong-test-key-000000000000000000"))
        self.assertEqual(error.exception.code, 400)
        self.assertEqual(self.request(url, self.message("good"))["decision"], "adopt")
        self.assertEqual(len(DurableSemanticFabric(self.db).decisions()), 1)
