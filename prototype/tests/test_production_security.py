"""Transport adversarial regressions; multi-process TLS exercised separately."""
import ssl
import socket
import shutil
import subprocess
import tempfile
from pathlib import Path
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError
from unittest.mock import patch
import test_scf_http_dispatcher as dispatch_fixtures
from prain.scf_http import send, validate_endpoint, receipt_fields, receipt_signature, serve
from prain.scf import DECISIONS
from prain.scf_http_dispatcher import SCFHTTPDispatcher


class ProductionTransportSecurity(dispatch_fixtures.DispatchTests):
    def test_receipt_hmac_required_and_wrong_key_fails_unknown(self):
        dispatcher = SCFHTTPDispatcher(self.queue, self.url, receipt_key=b'z'*32)
        dispatcher.enqueue(self.message())
        self.assertEqual(dispatcher.deliver_one(), 'UNKNOWN')
        self.assertEqual(len(self.receiver.fabric.decisions()), 1)
        self.assertIsNone(dispatcher.deliver_one())

    def test_authenticated_bound_receipt_succeeds(self):
        dispatcher = SCFHTTPDispatcher(self.queue, self.url, receipt_key=b'k'*32)
        dispatcher.enqueue(self.message())
        self.assertEqual(dispatcher.deliver_one(), 'SUCCEEDED')

    def test_unsigned_fabricated_success_is_unknown(self):
        dispatcher = SCFHTTPDispatcher(self.queue, self.url, receipt_key=b'k'*32)
        dispatcher.enqueue(self.message())
        with patch('prain.scf_http_dispatcher.send', return_value={'claim_id':'c', 'decision':'adopt'}):
            self.assertEqual(dispatcher.deliver_one(), 'UNKNOWN')

    def test_unverified_tls_context_rejected(self):
        with self.assertRaises(ValueError):
            send(self.url, self.message(), ssl_context=ssl._create_unverified_context())

    def test_endpoint_confusion_rejected(self):
        for url in ('http://example.com/scf/v1/receive', 'http://127.0.0.1:80@evil.test/scf/v1/receive',
                    'https://example.com/scf/v1/receive#fragment', 'https://example.com/other'):
            with self.subTest(url=url), self.assertRaises(ValueError):
                validate_endpoint(url)

    def test_redirect_does_not_follow_or_deliver(self):
        target = self.url
        class Redirect(BaseHTTPRequestHandler):
            def do_POST(self):
                self.rfile.read(int(self.headers['Content-Length']))
                self.send_response(307)
                self.send_header('Location', target)
                self.end_headers()
            def log_message(self, *args): pass
        server = ThreadingHTTPServer(('127.0.0.1',0), Redirect)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            with self.assertRaises(HTTPError):
                send('http://127.0.0.1:%d/scf/v1/receive' % server.server_port, self.message())
            self.assertEqual(len(self.receiver.fabric.decisions()), 0)
        finally:
            server.shutdown()
            server.server_close()

    def test_missing_receipt_key_rejected_before_delivery(self):
        with self.assertRaisesRegex(ValueError, "untrusted_receipt_key"):
            SCFHTTPDispatcher(self.queue, self.url)
        self.assertEqual(len(self.receiver.fabric.decisions()), 0)

    def test_all_canonical_decisions_are_authenticated_delivery_results(self):
        for index, decision in enumerate(sorted(DECISIONS)):
            with self.subTest(decision=decision):
                message = self.message(msg="canonical-%d" % index)
                fields = receipt_fields(message, {"claim_id": "c", "decision": decision})
                response = {"receipt": fields, "receipt_signature": receipt_signature(fields, b"k"*32)}
                dispatcher = SCFHTTPDispatcher(self.queue, self.url, receipt_key=b"k"*32)
                dispatcher.enqueue(message)
                with patch("prain.scf_http_dispatcher.send", return_value=response):
                    self.assertEqual(dispatcher.deliver_one(), "SUCCEEDED")

    def test_unsigned_bound_receipt_remains_unknown(self):
        message = self.message()
        fields = receipt_fields(message, {"claim_id": "c", "decision": "adopt"})
        dispatcher = SCFHTTPDispatcher(self.queue, self.url, receipt_key=b"k"*32)
        dispatcher.enqueue(message)
        with patch("prain.scf_http_dispatcher.send", return_value={"receipt": fields}):
            self.assertEqual(dispatcher.deliver_one(), "UNKNOWN")
        self.assertIsNone(dispatcher.deliver_one())

    @unittest.skipUnless(shutil.which("openssl"), "openssl required for TLS fixture")
    def test_idle_tls_peer_does_not_block_valid_peer(self):
        with tempfile.TemporaryDirectory() as directory:
            cert, key = Path(directory)/"cert.pem", Path(directory)/"key.pem"
            subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes",
                "-keyout", str(key), "-out", str(cert), "-days", "1", "-subj", "/CN=localhost",
                "-addext", "subjectAltName=DNS:localhost"], check=True, capture_output=True, timeout=20)
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(cert, key)
            server = serve(self.receiver, ssl_context=context, request_timeout=1, max_connections=2)
            threading.Thread(target=server.serve_forever, daemon=True).start()
            idle = socket.create_connection(("127.0.0.1", server.server_port), timeout=2)
            try:
                reply = send("https://localhost:%d/scf/v1/receive" % server.server_port,
                    self.message(), timeout=0.8, ssl_context=ssl.create_default_context(cafile=str(cert)))
                self.assertEqual(reply["decision"], "adopt")
            finally:
                idle.close()
                server.shutdown()
                server.server_close()

    def test_malformed_authenticated_receipt_fields_become_unknown(self):
        for index, bad_result in enumerate(({"claim_id": "c", "decision": []},
                                           {"claim_id": "c", "decision": "adopt"})):
            message = self.message(msg="malformed-%d" % index)
            fields = receipt_fields(message, bad_result)
            response = {"receipt": fields, "receipt_signature": "\u00e9"}
            dispatcher = SCFHTTPDispatcher(self.queue, self.url, receipt_key=b"k"*32)
            dispatcher.enqueue(message)
            with patch("prain.scf_http_dispatcher.send", return_value=response):
                self.assertEqual(dispatcher.deliver_one(), "UNKNOWN")
            self.assertEqual(self.queue.status(message.message_id)["status"], "UNKNOWN")
