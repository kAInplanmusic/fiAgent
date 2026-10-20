import concurrent.futures
import multiprocessing
import tempfile
import unittest
from pathlib import Path
from prain.durable_admission import DurableAdmissionStore, AdmissionConflict



def _claim_in_process(db_path, barrier, results):
    """Independent process attempting to claim one durable outbox row."""
    store = DurableAdmissionStore(db_path)
    barrier.wait(timeout=10)
    item = store.claim_next()
    results.put(item['outbox_id'] if item else None)

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


    def test_admission_and_outbox_are_atomic_and_persistent(self):
        receipt, created = self.store.admit(idempotency_key='k-out', fingerprint='f-out',
            receipt={'id':'r-out'}, outbox_item={'outbox_id':'o-out','payload':{'action':'sim'}})
        self.assertTrue(created)
        self.assertEqual(DurableAdmissionStore(self.path).get_outbox('k-out')['status'], 'PENDING')
        self.assertEqual(self.store.claim_next()['outbox_id'], 'o-out')

    def test_recovery_marks_in_flight_unknown_not_pending(self):
        self.store.admit(idempotency_key='k-recover', fingerprint='f', receipt={'id':'r'},
            outbox_item={'outbox_id':'o-recover','payload':{'action':'sim'}})
        self.store.claim_next()
        self.assertEqual(DurableAdmissionStore(self.path).recover_in_flight(), 1)
        self.assertEqual(self.store.get_outbox('k-recover')['status'], 'OUTCOME_UNKNOWN')
        self.assertIsNone(self.store.claim_next())


    def test_process_crash_after_claim_recovers_as_unknown(self):
        self.store.admit(idempotency_key='crash-key', fingerprint='f', receipt={'id':'r'},
            outbox_item={'outbox_id':'crash-out','payload':{'action':'sim'}})
        # Model process death after claim but before outcome persistence.
        claimed = self.store.claim_next()
        self.assertEqual(claimed['status'], 'IN_FLIGHT')
        restarted = DurableAdmissionStore(self.path)
        self.assertEqual(restarted.recover_in_flight(), 1)
        self.assertEqual(restarted.get_outbox('crash-key')['status'], 'OUTCOME_UNKNOWN')
        self.assertIsNone(restarted.claim_next(), 'unknown outcome must not be blindly retried')

    def test_multiprocess_claim_has_single_winner(self):
        self.store.admit(idempotency_key='mp-key', fingerprint='f', receipt={'id':'r'},
            outbox_item={'outbox_id':'mp-out','payload':{'action':'sim'}})
        ctx = multiprocessing.get_context('fork')
        barrier = ctx.Barrier(4)
        results = ctx.Queue()
        workers = [ctx.Process(target=_claim_in_process, args=(self.path, barrier, results)) for _ in range(4)]
        for worker in workers: worker.start()
        claimed = [results.get(timeout=15) for _ in workers]
        for worker in workers:
            worker.join(timeout=15)
            self.assertEqual(worker.exitcode, 0)
        self.assertEqual(claimed.count('mp-out'), 1)
        self.assertEqual(claimed.count(None), 3)

    def test_reconciliation_is_compare_and_set_under_race(self):
        self.store.admit(idempotency_key='race-key', fingerprint='f', receipt={'id':'r'},
            outbox_item={'outbox_id':'race-out','payload':{'action':'sim'}})
        self.store.claim_next()
        self.store.record_outcome('race-out', 'OUTCOME_UNKNOWN', 'ambiguous')
        def reconcile(state):
            try:
                return DurableAdmissionStore(self.path).reconcile_unknown('race-key', state, 'test evidence')['status']
            except AdmissionConflict:
                return 'LOST_RACE'
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(reconcile, ['SUCCEEDED', 'FAILED']))
        self.assertEqual(sum(x == 'LOST_RACE' for x in outcomes), 1)
        self.assertIn(self.store.get_outbox('race-key')['status'], {'SUCCEEDED', 'FAILED'})

    def test_crash_window_never_assumes_external_effect_did_not_happen(self):
        self.store.admit(idempotency_key='window-key', fingerprint='f', receipt={'id':'r'},
            outbox_item={'outbox_id':'window-out','payload':{'action':'sim'}})
        self.store.claim_next()
        self.store.recover_in_flight()
        unknown = self.store.get_outbox('window-key')
        self.assertEqual(unknown['status'], 'OUTCOME_UNKNOWN')
        self.assertIn('requires_reconciliation', unknown['last_error'])
        with self.assertRaises(ValueError):
            self.store.reconcile_unknown('window-key', 'NOT_EXECUTED', '')
        self.assertEqual(self.store.get_outbox('window-key')['status'], 'OUTCOME_UNKNOWN')

    def test_outcome_requires_in_flight_and_valid_state(self):
        self.store.admit(idempotency_key='k-outcome', fingerprint='f', receipt={'id':'r'},
            outbox_item={'outbox_id':'o-outcome','payload':{'action':'sim'}})
        with self.assertRaises(ValueError): self.store.record_outcome('o-outcome','PENDING')
        with self.assertRaisesRegex(AdmissionConflict, 'outbox_not_in_flight'):
            self.store.record_outcome('o-outcome','SUCCEEDED')
        self.store.claim_next()
        self.store.record_outcome('o-outcome','SUCCEEDED')
        self.assertEqual(self.store.get_outbox('k-outcome')['status'],'SUCCEEDED')

if __name__ == '__main__': unittest.main()
