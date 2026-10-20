import unittest
from datetime import datetime, timedelta, timezone
from prain import PRAINRuntime, Observation

class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.runtime = PRAINRuntime(
            policies=[{"policy_id":"read.v1", "action":"read", "target":"status",
                       "required_capability":"state:read"}],
            evaluators={"healthy": lambda obs: obs.payload.get("healthy") is True},
        )
        self.obs = Observation.create("unit-test", "health", {"healthy": True}, "obs-1")

    def test_ingest_emits_correlated_event_and_evidence(self):
        event = self.runtime.ingest(self.obs)
        self.assertEqual(event.correlation_id, "obs-1")
        self.assertEqual(event.payload["observation_id"], "obs-1")
        self.assertTrue(self.runtime.evidence.verify())

    def test_unknown_evaluator_fails_closed(self):
        self.assertFalse(self.runtime.evaluate(self.obs, "missing")["passed"])

    def test_registered_evaluator_returns_evidence_ref(self):
        result = self.runtime.evaluate(self.obs, "healthy")
        self.assertTrue(result["passed"])
        self.assertTrue(result["evidence_ref"].startswith("evidence://sha256/"))

    def test_policy_denial_does_not_create_receipt(self):
        receipt, decision = self.runtime.request_action("delete", "status", "delete", "agent", {}, "c1", "key-1")
        self.assertIsNone(receipt)
        self.assertFalse(decision["allowed"])
        self.assertEqual(self.runtime.snapshot()["receipts"], 0)

    def test_allowed_action_is_simulated_and_idempotent(self):
        args = ("read", "status", "state:read", "agent", {"field":"healthy"}, "c2", "same-key")
        first, decision = self.runtime.request_action(*args)
        second, replay = self.runtime.request_action(*args)
        self.assertTrue(decision["allowed"])
        self.assertEqual(first, second)
        self.assertEqual(replay["reason"], "idempotent_replay")
        self.assertTrue(first.result["simulated"])
        self.assertEqual(self.runtime.snapshot()["receipts"], 1)

    def test_idempotency_key_cannot_be_reused_for_different_request(self):
        first, _ = self.runtime.request_action("read", "status", "state:read", "agent", {"a": 1}, "c4", "reuse")
        second, decision = self.runtime.request_action("read", "status", "state:read", "agent", {"a": 2}, "c4", "reuse")
        self.assertIsNotNone(first)
        self.assertIsNone(second)
        self.assertEqual(decision["reason"], "idempotency_key_conflict")

    def test_goal_needs_verification_evidence(self):
        goal = self.runtime.goals.create("Verify health", [{"id":"c1", "check":"healthy"}], "g1")
        self.runtime.goals.activate(goal.goal_id)
        with self.assertRaises(ValueError):
            self.runtime.verify_goal("g1", True, [], "test-verifier")
        result = self.runtime.verify_goal("g1", True, ["evidence://test/1"], "test-verifier")
        self.assertEqual(result.status, "completed")

    def test_chain_valid_after_vertical_slice(self):
        self.runtime.ingest(self.obs)
        self.runtime.evaluate(self.obs, "healthy")
        self.runtime.request_action("read", "status", "state:read", "agent", {}, "c3", "key-3")
        self.assertTrue(self.runtime.evidence.verify())

if __name__ == "__main__":
    unittest.main()
