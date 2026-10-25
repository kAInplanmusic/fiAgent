import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from prain import PRAINRuntime
from prain.anima_hal import HALAssessment

BAD = HALAssessment("scf", "unhealthy", "observe_only", "probe_failure")

class DurableHALProposalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = str(Path(self.tmp.name) / "hal.sqlite")
        self.a = PRAINRuntime(persistent_db_path=self.db)

    def test_proposals_survive_restart_and_cooldown(self):
        self.assertEqual(self.a.hal_proposals.propose(BAD, 100, "p1").status, "pending_approval")
        b = PRAINRuntime(persistent_db_path=self.db)
        self.assertEqual(b.hal_proposals.propose(BAD, 110, "p2").reason, "cooldown")
        self.assertEqual(len(b.hal_proposals.history()), 2)
        self.assertEqual(b.hal_proposals.propose(BAD, 161, "p3").status, "pending_approval")

    def test_concurrent_proposals_cannot_bypass_cooldown(self):
        b = PRAINRuntime(persistent_db_path=self.db)
        def apply(item):
            runtime, proposal_id = item
            return runtime.hal_proposals.propose(BAD, 100, proposal_id).status
        with ThreadPoolExecutor(max_workers=2) as pool:
            result = list(pool.map(apply, [(self.a, "a"), (b, "b")]))
        self.assertEqual(sorted(result), ["blocked", "pending_approval"])

    def test_proposal_identifier_cannot_be_reused(self):
        self.a.hal_proposals.propose(BAD, 100, "p")
        with self.assertRaises(ValueError):
            self.a.hal_proposals.propose(BAD, 200, "p")

    def test_never_executes_and_unknown_does_not_propose(self):
        assessment = HALAssessment("scf", "unknown", "observe_only", "stale")
        result = self.a.hal_proposals.propose(assessment, 100, "p")
        self.assertEqual(result.status, "blocked")
        self.assertFalse(hasattr(self.a.hal_proposals, "execute"))
