import concurrent.futures
import tempfile
import unittest
from pathlib import Path
from prain.durable_admission import DurableAdmissionStore, AdmissionConflict

class DurableAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = str(Path(self.tmp.name) / 'prain.sqlite3')
        self.store = DurableAdmissionStore(self.path)
    def tearDown(self): self.tmp.cleanup()

    def test_restart_replays_same_receipt(self):
        receipt = {'receipt_id':'r1','status':'simulated_success'}
        first, created = self.store.admit(idempotency_key='k1', fingerprint='f1', receipt=receipt)
        second, created2 = DurableAdmissionStore(self.path).admit(idempotency_key='k1', fingerprint='f1', receipt={'ignored': True})
        self.assertTrue(created); self.assertFalse(created2); self.assertEqual(first, second)

    def test_same_key_different_fingerprint_conflicts(self):
        self.store.admit(idempotency_key='k1', fingerprint='f1', receipt={'id':'1'})
        with self.assertRaisesRegex(AdmissionConflict, 'idempotency_key_conflict'):
            self.store.admit(idempotency_key='k1', fingerprint='f2', receipt={'id':'2'})

    def test_single_use_approval_survives_restart(self):
        self.store.admit(idempotency_key='k1', fingerprint='f1', receipt={'id':'1'}, approval_id='a1')
        with self.assertRaisesRegex(AdmissionConflict, 'approval_already_consumed'):
            DurableAdmissionStore(self.path).admit(idempotency_key='k2', fingerprint='f2', receipt={'id':'2'}, approval_id='a1')

    def test_concurrent_same_key_has_one_creation(self):
        def attempt(_):
            return DurableAdmissionStore(self.path).admit(idempotency_key='shared', fingerprint='same', receipt={'id':'stable'})
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(attempt, range(24)))
        self.assertEqual(sum(created for _, created in results), 1)
        self.assertTrue(all(receipt == {'id':'stable'} for receipt, _ in results))

    def test_approval_and_admission_rollback_together(self):
        # Existing key forces conflict; approval insert must not remain consumed on rollback.
        self.store.admit(idempotency_key='taken', fingerprint='f0', receipt={'id':'0'})
        with self.assertRaises(AdmissionConflict):
            self.store.admit(idempotency_key='taken', fingerprint='different', receipt={'id':'x'}, approval_id='a2')
        self.store.admit(idempotency_key='fresh', fingerprint='f1', receipt={'id':'1'}, approval_id='a2')

if __name__ == '__main__': unittest.main()
