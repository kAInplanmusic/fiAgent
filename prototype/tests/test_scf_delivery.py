import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from prain.scf_delivery import SCFDeliveryQueue, DeliveryConflict

class DeliveryQueueTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = str(Path(self.tmp.name) / "queue.sqlite")
        self.q = SCFDeliveryQueue(self.db)

    def test_duplicate_and_changed_body(self):
        self.assertTrue(self.q.publish("m1", {"v": 1}))
        self.assertFalse(self.q.publish("m1", {"v": 1}))
        with self.assertRaises(DeliveryConflict):
            self.q.publish("m1", {"v": 2})

    def test_concurrent_workers_claim_once(self):
        self.q.publish("m1", {"v": 1})
        with ThreadPoolExecutor(max_workers=3) as pool:
            claimed = list(pool.map(lambda q: q.claim(), [self.q, SCFDeliveryQueue(self.db), SCFDeliveryQueue(self.db)]))
        self.assertEqual(sum(x is not None for x in claimed), 1)

    def test_crash_recovery_not_blind_retry(self):
        self.q.publish("m1", {"v": 1})
        self.q.claim()
        q2 = SCFDeliveryQueue(self.db)
        self.assertEqual(q2.recover(), 1)
        self.assertIsNone(q2.claim())
        self.assertEqual(q2.status("m1")["status"], "UNKNOWN")
        self.assertEqual(q2.reconcile("m1", "NOT_EXECUTED", "provider-report"), "PENDING")
        self.assertEqual(q2.claim()["message_id"], "m1")
        q2.outcome("m1", "SUCCEEDED")
        self.assertEqual(q2.status("m1")["attempts"], 2)

    def test_invalid_reconciliation_rejected(self):
        self.q.publish("m1", {"v": 1})
        self.q.claim()
        self.q.recover()
        for state, evidence in [("UNSURE", "proof"), ("SUCCEEDED", "")]:
            with self.assertRaises(DeliveryConflict):
                self.q.reconcile("m1", state, evidence)

    def test_recovery_persists_across_instances(self):
        self.q.publish("m1", {"v": 1})
        self.q.claim()
        self.assertEqual(SCFDeliveryQueue(self.db).recover(), 1)
        self.assertEqual(SCFDeliveryQueue(self.db).status("m1")["status"], "UNKNOWN")