import unittest
from prain import StateStore, StateConflict, Event, EventBus, GoalRegistry, GoalError, PolicyGateway, ActionRequest, EvidenceLedger

class StateStoreTests(unittest.TestCase):
    def test_create_and_cas_increment_version(self):
        s = StateStore(); a = s.create("k", {"n": 1}); b = s.compare_and_swap("k", 1, {"n": 2})
        self.assertEqual((a.version, b.version), (1, 2)); self.assertEqual(s.get("k").value, {"n": 2})
    def test_stale_version_rejected(self):
        s = StateStore(); s.create("k", 1); s.compare_and_swap("k", 1, 2)
        with self.assertRaises(StateConflict): s.compare_and_swap("k", 1, 3)
    def test_create_does_not_overwrite(self):
        s = StateStore(); s.create("k", 1)
        with self.assertRaises(StateConflict): s.create("k", 2)

class EventBusTests(unittest.TestCase):
    def test_duplicate_event_is_suppressed(self):
        b = EventBus(); calls = []; b.subscribe("x", "c", lambda e: calls.append(e.event_id))
        e = Event.create("x", {}, event_id="stable"); first = b.publish(e); second = b.publish(e)
        self.assertEqual(len(calls), 1); self.assertEqual(first["c"], "processed")
        self.assertEqual(second["c"], "duplicate_ignored")
    def test_wrong_type_not_delivered(self):
        b = EventBus(); calls = []; b.subscribe("wanted", "c", lambda e: calls.append(e))
        b.publish(Event.create("other", {})); self.assertEqual(calls, [])

class GoalTests(unittest.TestCase):
    def setUp(self):
        self.g = GoalRegistry(); self.g.create("Goal", [{"id": "c1", "check": "true"}], "g1")
    def test_criteria_required(self):
        with self.assertRaises(GoalError): self.g.create("No criteria", [])
    def test_completion_requires_verification(self):
        with self.assertRaises(GoalError): self.g.set_status("g1", "completed")
    def test_pass_requires_evidence(self):
        with self.assertRaises(GoalError): self.g.record_verification("g1", True, [], "tester")
    def test_passing_verification_completes(self):
        self.g.activate("g1"); result = self.g.record_verification("g1", True, ["evidence://1"], "tester")
        self.assertEqual(result.status, "completed"); self.assertTrue(result.verification["passed"])

class PolicyTests(unittest.TestCase):
    def test_no_policy_denied(self):
        req = ActionRequest.create("delete", "x", "delete:x", "agent", {})
        d = PolicyGateway().evaluate(req); self.assertFalse(d.allowed); self.assertEqual(d.reason, "no_matching_policy")
    def test_wrong_capability_denied(self):
        p = PolicyGateway([{"policy_id":"p1","action":"read","target":"*","required_capability":"state:read"}])
        req = ActionRequest.create("read", "x", "state:write", "agent", {})
        self.assertFalse(p.evaluate(req).allowed)
    def test_matching_rule_allowed(self):
        p = PolicyGateway([{"policy_id":"p1","action":"read","target":"x","required_capability":"state:read"}])
        req = ActionRequest.create("read", "x", "state:read", "agent", {})
        self.assertTrue(p.evaluate(req).allowed)
    def test_approval_required(self):
        p = PolicyGateway([{"policy_id":"p2","action":"deploy","target":"prod","required_capability":"deploy:prod","approval_required":True}])
        req = ActionRequest.create("deploy", "prod", "deploy:prod", "agent", {})
        self.assertEqual(p.evaluate(req).reason, "approval_required")

class LedgerTests(unittest.TestCase):
    def test_chain_verifies(self):
        l = EvidenceLedger(); l.append("event", "x", {"v":1}); l.append("event", "y", {"v":2})
        self.assertTrue(l.verify())
    def test_empty_chain_verifies(self):
        self.assertTrue(EvidenceLedger().verify())

if __name__ == "__main__": unittest.main()
