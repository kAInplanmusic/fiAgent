import sqlite3
import tempfile
import unittest
from pathlib import Path

from prain.runtime import PRAINRuntime
from prain.secure_completion import AuthenticatedVerifier, SecureCompletionError


class SecureCompletionIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = str(Path(self.temp.name) / "runtime.db")
        self.runtime = PRAINRuntime(persistent_db_path=self.path)
        self.facade = self.runtime.secure_completion(
            lambda principal: AuthenticatedVerifier(principal, "verified-agent") if principal == "trusted" else None)
        self.goal = self.runtime.goals.create("Verified completion",
                        [{"id": "c1", "check": "confirmed"}])
        self.runtime.goals.activate(self.goal.goal_id)
        self.evidence = self.runtime.evidence.append("criterion.verification", self.goal.goal_id,
            {"goal_id": self.goal.goal_id, "criterion_id": "c1", "passed": True,
             "verifier": "verified-agent"})
        self.ref = "evidence://sha256/" + self.evidence.entry_hash

    def _head(self):
        entries = self.runtime.evidence.entries()
        return entries[-1].entry_hash if entries else "0" * 64

    def _complete(self, **overrides):
        args = dict(principal="trusted", criterion_results=[
            {"id": "c1", "passed": True, "evidence_refs": [self.ref]}],
            expected_ledger_head=self._head())
        args.update(overrides)
        return self.facade.complete(self.goal.goal_id, **args)

    def test_completion_persists_and_audits(self):
        receipt = self._complete()
        self.assertEqual(self.runtime.goals.get(self.goal.goal_id).status, "completed")
        self.assertTrue(self.runtime.evidence.verify())
        self.assertTrue(self.facade.audit(self.goal.goal_id))
        self.assertEqual(receipt, self.runtime.secure_completion(
            lambda p: AuthenticatedVerifier(p, "verified-agent")).receipt(self.goal.goal_id))

    def test_untrusted_cannot_complete(self):
        with self.assertRaises(SecureCompletionError):
            self._complete(principal="guest")
        self.assertEqual(self.runtime.goals.get(self.goal.goal_id).status, "active")

    def test_stale_head_cannot_complete(self):
        with self.assertRaises(SecureCompletionError):
            self._complete(expected_ledger_head="0" * 64)
        self.assertEqual(self.runtime.goals.get(self.goal.goal_id).status, "active")

    def test_scope_mismatch_cannot_complete(self):
        bad = self.runtime.evidence.append("criterion.verification", "some-other-goal",
            {"goal_id": "some-other-goal", "criterion_id": "c1", "passed": True, "verifier": "verified-agent"})
        with self.assertRaises(SecureCompletionError):
            self._complete(criterion_results=[{"id": "c1", "passed": True,
                "evidence_refs": ["evidence://sha256/" + bad.entry_hash]}])
        self.assertEqual(self.runtime.goals.get(self.goal.goal_id).status, "active")

    def test_duplicate_completion_rolls_back(self):
        self._complete()
        before = len(self.runtime.evidence.entries())
        with self.assertRaises(SecureCompletionError):
            self._complete()
        self.assertEqual(len(self.runtime.evidence.entries()), before)

    def test_receipt_write_failure_rolls_back_all_writes(self):
        with sqlite3.connect(self.path) as db:
            db.execute("""CREATE TRIGGER block_completion BEFORE INSERT ON prain_goal_completion_receipts
                BEGIN SELECT RAISE(ABORT, 'no receipts'); END""")
        count = len(self.runtime.evidence.entries())
        with self.assertRaises(sqlite3.IntegrityError):
            self._complete()
        self.assertEqual(self.runtime.goals.get(self.goal.goal_id).status, "active")
        self.assertEqual(len(self.runtime.evidence.entries()), count)
        self.assertIsNone(self.facade.receipt(self.goal.goal_id))

    def test_tampered_receipt_rejected(self):
        self._complete()
        with sqlite3.connect(self.path) as db:
            db.execute("UPDATE prain_goal_completion_receipts SET receipt_json='{}'")
        with self.assertRaises(SecureCompletionError):
            self.facade.audit(self.goal.goal_id)