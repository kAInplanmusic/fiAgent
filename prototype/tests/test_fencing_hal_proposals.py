import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from prain.fenced_leases import FencedLeaseStore, LeaseRejected
from prain.hal_proposals import HALProposalController
from prain.anima_hal import HALAssessment


class FencingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        path = str(Path(self.temp.name) / "leases.sqlite")
        self.a, self.b = FencedLeaseStore(path), FencedLeaseStore(path)

    def test_expiry_and_stale_writer_cannot_overwrite(self):
        first = self.a.acquire("resource", "worker-a", 10, now=100)
        self.a.fenced_write(first, "old", now=101)
        with self.assertRaises(LeaseRejected):
            self.b.acquire("resource", "worker-b", 10, now=105)
        second = self.b.acquire("resource", "worker-b", 10, now=110)
        self.assertGreater(second.token, first.token)
        self.b.fenced_write(second, "new", now=111)
        with self.assertRaises(LeaseRejected):
            self.a.fenced_write(first, "stale", now=111)
        self.assertEqual(self.a.read("resource"), (second.token, "new"))

    def test_stale_renewal_rejected_after_reacquisition(self):
        old = self.a.acquire("r", "a", 5, now=100)
        new = self.b.acquire("r", "b", 5, now=105)
        with self.assertRaises(LeaseRejected):
            self.a.renew(old, 5, now=106)
        self.assertEqual(self.b.renew(new, 5, now=106).expires_at, 111)

    def test_concurrent_acquisition_single_winner(self):
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda store: self._attempt(store), [self.a, self.b]))
        self.assertEqual(results.count(True), 1)

    def _attempt(self, store):
        try:
            store.acquire("shared", "worker", 10, now=100)
            return True
        except LeaseRejected:
            return False

    def test_invalid_inputs_rejected(self):
        for ttl in (0, -1, float("nan"), float("inf"), True):
            with self.assertRaises(LeaseRejected):
                self.a.acquire("r", "worker", ttl, now=100)

    def test_unrepresentable_expiry_rejected_without_mutating_lease(self):
        with self.assertRaisesRegex(LeaseRejected, "invalid_expiry"):
            self.a.acquire("r", "worker", 1e-20, now=1_000_000_000)
        lease = self.a.acquire("r", "worker", 10, now=100)
        with self.assertRaisesRegex(LeaseRejected, "invalid_expiry"):
            self.a.renew(lease, 1e-20, now=101)
        self.a.fenced_write(lease, "still-valid", now=102)
        self.assertEqual(self.b.read("r"), (lease.token, "still-valid"))


class HALProposalTests(unittest.TestCase):
    def test_cooldown_and_budget(self):
        controller = HALProposalController(cooldown_seconds=60, max_proposals=2)
        bad = HALAssessment("scf", "unhealthy", "observe_only", "failure")
        first = controller.propose(bad, 100, "p1")
        self.assertEqual(first.status, "pending_approval")
        self.assertEqual(controller.propose(bad, 110, "p2").reason, "cooldown")
        self.assertEqual(controller.propose(bad, 161, "p3").status, "pending_approval")
        self.assertEqual(controller.propose(bad, 240, "p4").reason, "proposal_budget_exhausted")

    def test_healthy_and_unknown_never_propose(self):
        controller = HALProposalController()
        for health in ("healthy", "unknown"):
            result = controller.propose(HALAssessment("scf", health, "observe_only", "test"), 100, health)
            self.assertEqual(result.status, "blocked")

    def test_proposals_never_execute_or_grant(self):
        controller = HALProposalController()
        result = controller.propose(HALAssessment("scf", "unhealthy", "observe_only", "bad"), 100, "p")
        self.assertEqual(result.action, "request_repair_review")
        self.assertFalse(hasattr(controller, "execute"))
class RuntimeCoordinationWiringTests(unittest.TestCase):
    def test_durable_runtime_exposes_fencing_and_review_only_hal(self):
        from prain import PRAINRuntime
        with tempfile.TemporaryDirectory() as temp:
            path = str(Path(temp) / "prain.sqlite")
            first = PRAINRuntime(persistent_db_path=path)
            other = PRAINRuntime(persistent_db_path=path)
            lease = first.fencing.acquire("scf", "worker-1", 10, now=100)
            first.fencing.fenced_write(lease, "old", now=101)
            replacement = other.fencing.acquire("scf", "worker-2", 10, now=110)
            other.fencing.fenced_write(replacement, "new", now=111)
            with self.assertRaises(LeaseRejected):
                first.fencing.fenced_write(lease, "stale", now=111)
            proposal = first.hal_proposals.propose(
                HALAssessment("scf", "unhealthy", "observe_only", "bad"), 112, "review-1")
            self.assertEqual(proposal.status, "pending_approval")
            self.assertEqual(other.fencing.read("scf"), (replacement.token, "new"))

    def test_memory_runtime_has_no_durable_fence(self):
        from prain import PRAINRuntime
        self.assertIsNone(PRAINRuntime().fencing)
