import unittest
import tempfile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from prain import PRAINRuntime, Observation, DurableAdmissionStore

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


    def test_nested_payload_is_snapshotted_before_execution(self):
        payload = {"nested": {"value": 1}}
        receipt, decision = self.runtime.request_action("read", "status", "state:read", "agent", payload, "c5", "snapshot-key")
        self.assertTrue(decision["allowed"])
        original_hash = receipt.result["input_hash"]
        payload["nested"]["value"] = 99
        self.assertEqual(receipt.result["input_hash"], original_hash)
        replay, replay_decision = self.runtime.request_action("read", "status", "state:read", "agent", {"nested": {"value": 1}}, "c5", "snapshot-key")
        self.assertEqual(replay_decision["reason"], "idempotent_replay")


    def test_concurrent_same_idempotency_key_creates_one_receipt(self):
        def call(_):
            return self.runtime.request_action("read", "status", "state:read", "agent",
                                               {"field": "healthy"}, "parallel", "parallel-key")
        with ThreadPoolExecutor(max_workers=12) as pool:
            results = list(pool.map(call, range(40)))
        receipts = [r for r, d in results if r is not None]
        self.assertEqual(len(receipts), 40)
        self.assertEqual(len({r.receipt_id for r in receipts}), 1)
        self.assertEqual(self.runtime.snapshot()["receipts"], 1)

    def test_single_use_approval_cannot_authorize_two_distinct_actions(self):
        runtime = PRAINRuntime(policies=[{"policy_id":"deploy.v1", "action":"deploy",
            "target":"prod", "required_capability":"deploy:prod", "approval_required":True}])
        import hashlib, json
        payload = {"version": 1}
        approval = {"approval_id":"approval-unique-1", "action":"deploy", "target":"prod",
            "input_hash": hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
            "idempotency_key":"key-a", "expires_at":(datetime.now(timezone.utc)+timedelta(minutes=5)).isoformat(),
            "lifecycle_status":"issued", "usage_policy":"single_use", "max_uses":1, "usage_count":0}
        first, decision1 = runtime.request_action("deploy", "prod", "deploy:prod", "agent", payload, "c1", "key-a", approval)
        self.assertIsNotNone(first)
        # Rebind only the idempotency key; same approval ID cannot be spent again.
        approval2 = dict(approval, idempotency_key="key-b")
        second, decision2 = runtime.request_action("deploy", "prod", "deploy:prod", "agent", payload, "c2", "key-b", approval2)
        self.assertIsNone(second)
        self.assertEqual(decision2["reason"], "approval_already_consumed")

    def test_single_use_approval_requires_stable_id(self):
        runtime = PRAINRuntime(policies=[{"policy_id":"deploy.v1", "action":"deploy",
            "target":"prod", "required_capability":"deploy:prod", "approval_required":True}])
        import hashlib, json
        payload = {"version": 1}
        approval = {"action":"deploy", "target":"prod",
            "input_hash": hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
            "idempotency_key":"key-a", "expires_at":(datetime.now(timezone.utc)+timedelta(minutes=5)).isoformat(),
            "lifecycle_status":"issued", "usage_policy":"single_use", "max_uses":1, "usage_count":0}
        receipt, decision = runtime.request_action("deploy", "prod", "deploy:prod", "agent", payload, "c1", "key-a", approval)
        self.assertIsNone(receipt)
        self.assertEqual(decision["reason"], "single_use_approval_id_required")

    def test_goal_needs_verification_evidence(self):
        goal = self.runtime.goals.create("Verify health", [{"id":"c1", "check":"healthy"}], "g1")
        self.runtime.goals.activate(goal.goal_id)
        with self.assertRaises(PermissionError):
            self.runtime.verify_goal("g1", True, [], "test-verifier")
        with self.assertRaisesRegex(PermissionError, "verified_goal_completion_required"):
            self.runtime.verify_goal("g1", True, ["evidence://test/1"], "test-verifier")
        self.assertEqual(self.runtime.goals.get("g1").status, "active")

    def test_sqlite_admission_replays_across_runtime_restart(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = str(Path(tmp) / "prain.sqlite3")
            policies = [{"policy_id":"read.v1", "action":"read", "target":"status",
                         "required_capability":"state:read"}]
            args = ("read", "status", "state:read", "agent", {"field":"healthy"}, "restart-c1", "durable-key")
            first_runtime = PRAINRuntime(policies=policies, admission_store=DurableAdmissionStore(db_path))
            first, first_decision = first_runtime.request_action(*args)
            self.assertIsNotNone(first)
            self.assertTrue(first_decision["allowed"])
            outbox = DurableAdmissionStore(db_path).get_outbox("durable-key")
            self.assertIsNotNone(outbox)
            self.assertEqual(outbox["status"], "PENDING")
            self.assertEqual(outbox["payload"]["execution_mode"], "simulated_only")
            second_runtime = PRAINRuntime(policies=policies, admission_store=DurableAdmissionStore(db_path))
            second, replay_decision = second_runtime.request_action(*args)
            self.assertEqual(first, second)
            self.assertEqual(replay_decision["reason"], "idempotent_replay")

    def test_sqlite_admission_rejects_changed_payload_after_restart(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = str(Path(tmp) / "prain.sqlite3")
            policies = [{"policy_id":"read.v1", "action":"read", "target":"status",
                         "required_capability":"state:read"}]
            first_runtime = PRAINRuntime(policies=policies, admission_store=DurableAdmissionStore(db_path))
            first_runtime.request_action("read", "status", "state:read", "agent", {"v": 1}, "c", "durable-conflict")
            second_runtime = PRAINRuntime(policies=policies, admission_store=DurableAdmissionStore(db_path))
            second, decision = second_runtime.request_action("read", "status", "state:read", "agent", {"v": 2}, "c", "durable-conflict")
            self.assertIsNone(second)
            self.assertEqual(decision["reason"], "idempotency_key_conflict")

    def test_sqlite_single_use_approval_consumed_atomically(self):
        import hashlib, json
        with tempfile.TemporaryDirectory() as tmp:
            db_path = str(Path(tmp) / "prain.sqlite3")
            policies = [{"policy_id":"deploy.v1", "action":"deploy", "target":"prod",
                         "required_capability":"deploy:prod", "approval_required":True}]
            payload = {"version": 1}
            approval = {"approval_id":"durable-approval", "action":"deploy", "target":"prod",
                "input_hash": hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
                "idempotency_key":"durable-key-a", "expires_at":(datetime.now(timezone.utc)+timedelta(minutes=5)).isoformat(),
                "lifecycle_status":"issued", "usage_policy":"single_use", "max_uses":1, "usage_count":0}
            runtime = PRAINRuntime(policies=policies, admission_store=DurableAdmissionStore(db_path))
            first, decision = runtime.request_action("deploy", "prod", "deploy:prod", "agent", payload, "c1", "durable-key-a", approval)
            self.assertIsNotNone(first)
            approval2 = dict(approval, idempotency_key="durable-key-b")
            restarted = PRAINRuntime(policies=policies, admission_store=DurableAdmissionStore(db_path))
            second, decision2 = restarted.request_action("deploy", "prod", "deploy:prod", "agent", payload, "c2", "durable-key-b", approval2)
            self.assertIsNone(second)
            self.assertEqual(decision2["reason"], "approval_already_consumed")

    def test_chain_valid_after_vertical_slice(self):
        self.runtime.ingest(self.obs)
        self.runtime.evaluate(self.obs, "healthy")
        self.runtime.request_action("read", "status", "state:read", "agent", {}, "c3", "key-3")
        self.assertTrue(self.runtime.evidence.verify())

if __name__ == "__main__":
    unittest.main()