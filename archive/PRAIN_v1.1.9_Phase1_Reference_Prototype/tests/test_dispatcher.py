import tempfile
import unittest
from pathlib import Path
from prain.durable_admission import AdmissionConflict, DurableAdmissionStore
from prain.dispatcher import OutboxDispatcher

class DispatcherTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = DurableAdmissionStore(Path(self.tmp.name) / 'db.sqlite3')
        self.store.admit(idempotency_key='k1', fingerprint='f1', receipt={'id':'r1'},
                         outbox_item={'outbox_id':'o1','payload':{'action':'simulated'}})
    def tearDown(self): self.tmp.cleanup()

    def test_no_handler_does_not_claim_or_execute(self):
        self.assertIsNone(OutboxDispatcher(self.store).run_once())
        self.assertEqual(self.store.get_outbox('k1')['status'], 'PENDING')

    def test_success_passes_idempotency_key(self):
        seen = []
        dispatcher = OutboxDispatcher(self.store, lambda payload, key: seen.append((payload,key)) or 'SUCCEEDED')
        result = dispatcher.run_once()
        self.assertEqual(result['status'], 'SUCCEEDED')
        self.assertEqual(seen, [({'action':'simulated'}, 'k1')])
        self.assertIsNone(dispatcher.run_once())

    def test_exception_becomes_unknown_and_is_not_retried(self):
        calls = []
        def fail(payload, key):
            calls.append(key)
            raise TimeoutError('provider timed out')
        dispatcher = OutboxDispatcher(self.store, fail)
        self.assertEqual(dispatcher.run_once()['status'], 'OUTCOME_UNKNOWN')
        self.assertIsNone(dispatcher.run_once())
        self.assertEqual(calls, ['k1'])
        self.assertEqual(self.store.get_outbox('k1')['status'], 'OUTCOME_UNKNOWN')

    def test_unknown_requires_evidence_and_not_executed_requeues(self):
        self.store.claim_next()
        self.store.record_outcome('o1', 'OUTCOME_UNKNOWN', 'timeout')
        dispatcher = OutboxDispatcher(self.store, lambda p,k: 'SUCCEEDED')
        with self.assertRaises(ValueError): dispatcher.reconcile('k1', 'NOT_EXECUTED', '')
        result = dispatcher.reconcile('k1', 'NOT_EXECUTED', 'provider lookup confirms no operation')
        self.assertEqual(result['status'], 'PENDING')
        self.assertEqual(result['last_error'], 'reconciled:NOT_EXECUTED:provider lookup confirms no operation')

    def test_reconcile_terminal_and_reject_wrong_state(self):
        self.store.claim_next(); self.store.record_outcome('o1', 'OUTCOME_UNKNOWN', 'ambiguous')
        dispatcher = OutboxDispatcher(self.store)
        self.assertEqual(dispatcher.reconcile('k1','SUCCEEDED','provider operation id abc')['status'], 'SUCCEEDED')
        with self.assertRaisesRegex(AdmissionConflict, 'outbox_not_outcome_unknown'):
            dispatcher.reconcile('k1','FAILED','second contradictory report')

    def test_invalid_handler_result_becomes_unknown(self):
        dispatcher = OutboxDispatcher(self.store, lambda p,k: 'PENDING')
        self.assertEqual(dispatcher.run_once()['status'], 'OUTCOME_UNKNOWN')

if __name__ == '__main__': unittest.main()
