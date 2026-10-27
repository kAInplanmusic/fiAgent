"""Security boundary regressions; admitted effects remain simulated."""
import tempfile
import threading
import unittest
from unittest.mock import patch
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import hmac
import json
from pathlib import Path
from prain import PRAINRuntime
from prain.tenant_access import AccessDenied, TenantAccess
from prain.policy_gateway import _canonical_hash
from prain.durable_admission import DurableAdmissionStore

POLICY = [{"policy_id": "read.v1", "action": "read", "target": "item", "required_capability": "read"}]

class ProductionRuntimeAuthenticationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = str(Path(self.tmp.name) / "runtime.db")
        self.runtime = PRAINRuntime(policies=POLICY, persistent_db_path=self.path)
        self.token = self.runtime.tenant_access.provision("org", "person", [("read", "item")])

    def options(self, **changes):
        options = dict(tenant="org", principal="person", credential=self.token,
                       action="read", target="item", capability="read", payload={},
                       correlation_id="correlation", idempotency_key="request")
        options.update(changes)
        return options

    def test_raw_action_denied_without_identity_even_with_matching_policy(self):
        for runtime in (self.runtime, PRAINRuntime(policies=POLICY)):
            with self.assertRaisesRegex(PermissionError, "authenticated_action_required"):
                runtime.request_action("read", "item", "read", "admin", {}, "c", "key")
            self.assertEqual(runtime.snapshot()["receipts"], 0)

    def test_trusted_prototype_mode_is_explicit_and_strict_boolean(self):
        for invalid in ("true", 1, None):
            with self.assertRaises(TypeError):
                PRAINRuntime(trusted_local_prototype_mode=invalid)
        runtime = PRAINRuntime(policies=POLICY, trusted_local_prototype_mode=True)
        receipt, decision = runtime.request_action("read", "item", "read", "fixture", {}, "c", "key")
        self.assertTrue(decision["allowed"])
        self.assertEqual(receipt.status, "simulated_success")

    def test_authenticated_admission_does_not_call_public_legacy_facade(self):
        def fail(*args, **kwargs):
            self.fail("authenticated entrypoint called legacy facade")
        self.runtime.request_action = fail
        receipt, decision = self.runtime.request_authenticated_action(**self.options())
        self.assertTrue(decision["allowed"])
        self.assertEqual(receipt.status, "simulated_success")

    def test_wrong_identity_or_scope_cannot_admit(self):
        for changes in ({"tenant": "other"}, {"principal": "admin"}, {"credential": "wrong"},
                        {"target": "other"}, {"capability": "write"}):
            with self.assertRaises(AccessDenied):
                self.runtime.request_authenticated_action(**self.options(**changes))
        self.assertEqual(self.runtime.snapshot()["receipts"], 0)

    def test_revocation_by_other_connection_blocks_receipt_replay(self):
        self.runtime.request_authenticated_action(**self.options())
        TenantAccess(self.path).revoke("org", "person")
        with self.assertRaises(AccessDenied):
            self.runtime.request_authenticated_action(**self.options())

    def test_malformed_unicode_credential_fails_closed_on_all_auth_paths(self):
        malformed = '\ud800'
        access = self.runtime.tenant_access
        with self.assertRaises(AccessDenied):
            self.runtime.request_authenticated_action(**self.options(credential=malformed))
        with self.assertRaises(AccessDenied):
            access.authorize_identity('org', 'person', malformed)
        with self.assertRaises(AccessDenied):
            access.rotate('org', 'person', malformed)
        self.assertTrue(access.authorize('org', 'person', self.token, 'read', 'item'))

    def test_queued_request_rechecks_revocation_after_lock_acquisition(self):
        started = threading.Event()
        failures = []
        def request():
            started.set()
            try:
                self.runtime.request_authenticated_action(**self.options())
            except Exception as exc:
                failures.append(exc)
        with self.runtime._action_lock:
            worker = threading.Thread(target=request)
            worker.start()
            self.assertTrue(started.wait(2))
            TenantAccess(self.path).revoke("org", "person")
        worker.join(3)
        self.assertFalse(worker.is_alive())
        self.assertEqual(len(failures), 1)
        self.assertIsInstance(failures[0], AccessDenied)
        self.assertEqual(self.runtime.snapshot()["receipts"], 0)

    def test_delimiter_identity_collision_cannot_replay_another_tenant_receipt(self):
        first_token = self.runtime.tenant_access.provision("a:b", "c", [("read", "item")])
        second_token = self.runtime.tenant_access.provision("a", "b:c", [("read", "item")])
        first, _ = self.runtime.request_authenticated_action(**self.options(
            tenant="a:b", principal="c", credential=first_token))
        second, decision = self.runtime.request_authenticated_action(**self.options(
            tenant="a", principal="b:c", credential=second_token))
        self.assertIsNotNone(first)
        self.assertIsNone(second)
        self.assertEqual(decision["reason"], "idempotency_key_conflict")

    def test_authenticated_approval_cannot_cross_tenant_or_principal(self):
        issuer_key = b"issuer-only-test-key-for-production-auth-v1"
        policy = [{"policy_id": "approved.v1", "action": "read", "target": "item",
                   "required_capability": "read", "approval_required": True}]
        runtime = PRAINRuntime(policies=policy, persistent_db_path=self.path,
                               approval_verification_key=issuer_key)
        other = runtime.tenant_access.provision("other", "operator", [("read", "item")])
        approval = {"tenant": "org", "principal": "person", "action": "read",
                    "target": "item", "input_hash": _canonical_hash({}),
                    "idempotency_key": "request", "expires_at":
                    (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()}
        def signed(data):
            data = dict(data)
            data["issuer_signature"] = hmac.new(issuer_key, b"PRAIN-APPROVAL-v1\0" +
                json.dumps(data, sort_keys=True, separators=(",", ":"), allow_nan=False).encode(),
                sha256).hexdigest()
            return data
        approval = signed(approval)
        with self.assertRaisesRegex(PermissionError, "approval_identity_mismatch"):
            runtime.request_authenticated_action(**self.options(tenant="other", principal="operator",
                credential=other, approval=approval))
        with self.assertRaisesRegex(PermissionError, "approval_identity_mismatch"):
            runtime.request_authenticated_action(**self.options(approval={k:v for k,v in approval.items()
                if k != "principal"}))
        with self.assertRaisesRegex(PermissionError, "invalid_approval_issuer_signature"):
            runtime.request_authenticated_action(**self.options(approval={**approval,
                "expires_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()}))
        with self.assertRaisesRegex(PermissionError, "invalid_approval_issuer_signature"):
            runtime.request_authenticated_action(**self.options(approval={**approval,
                "issuer_signature": "0" * 64}))
        with self.assertRaisesRegex(PermissionError, "invalid_approval_issuer_signature"):
            runtime.request_authenticated_action(**self.options(approval={**approval,
                "issuer_signature": "ä" * 64}))
        with self.assertRaisesRegex(PermissionError, "verified_approval_issuer_required"):
            runtime.request_authenticated_action(**self.options(approval={k:v for k,v in approval.items()
                if k != "issuer_signature"}))
        unprovisioned = PRAINRuntime(policies=policy, persistent_db_path=self.path)
        with self.assertRaisesRegex(PermissionError, "verified_approval_issuer_required"):
            unprovisioned.request_authenticated_action(**self.options(approval=approval))
        receipt, decision = runtime.request_authenticated_action(**self.options(approval=approval))
        self.assertTrue(decision["allowed"], decision)
        self.assertEqual(receipt.status, "simulated_success")

    def test_approval_mutation_after_signature_check_cannot_extend_expiry(self):
        issuer_key = b"issuer-only-test-key-for-production-auth-v1"
        policy = [{"policy_id": "approved.v1", "action": "read", "target": "item",
                   "required_capability": "read", "approval_required": True}]
        runtime = PRAINRuntime(policies=policy, persistent_db_path=self.path,
                               approval_verification_key=issuer_key)
        approval = {"tenant": "org", "principal": "person", "action": "read",
                    "target": "item", "input_hash": _canonical_hash({}),
                    "idempotency_key": "request", "expires_at":
                    (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()}
        raw = json.dumps(approval, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
        approval["issuer_signature"] = hmac.new(issuer_key, b"PRAIN-APPROVAL-v1\0" + raw, sha256).hexdigest()
        original_evaluate = runtime.policy.evaluate
        def mutate_caller_approval(request, approval=None):
            caller_approval["expires_at"] = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
            return original_evaluate(request, approval=approval)
        caller_approval = approval
        runtime.policy.evaluate = mutate_caller_approval
        receipt, decision = runtime.request_authenticated_action(**self.options(approval=approval))
        self.assertIsNone(receipt)
        self.assertEqual(decision["reason"], "approval_expired")

    def test_authenticated_limited_approval_requires_enforceable_durable_limit(self):
        issuer_key = b"issuer-only-test-key-for-production-auth-v1"
        policy = [{"policy_id":"approval.v1", "action":"read", "target":"item",
                   "required_capability":"read", "approval_required":True}]
        def signed(key, **overrides):
            value = {"tenant":"org", "principal":"person", "action":"read", "target":"item",
                     "input_hash":_canonical_hash({}), "idempotency_key":key,
                     "expires_at":(datetime.now(timezone.utc)+timedelta(minutes=5)).isoformat(),
                     "approval_id":"same-approval", "usage_policy":"single_use", "max_uses":1}
            value.update(overrides)
            raw=json.dumps(value,sort_keys=True,separators=(",", ":"),allow_nan=False).encode()
            value["issuer_signature"]=hmac.new(issuer_key,b"PRAIN-APPROVAL-v1\0"+raw,sha256).hexdigest()
            return value
        no_store=PRAINRuntime(policies=policy,persistent_db_path=self.path,approval_verification_key=issuer_key)
        with self.assertRaisesRegex(PermissionError,"durable_approval_admission_required"):
            no_store.request_authenticated_action(**self.options(approval=signed("request")))
        with self.assertRaisesRegex(PermissionError,"approval_usage_limit_not_supported"):
            no_store.request_authenticated_action(**self.options(approval=signed("request",usage_policy="bounded_use",max_uses=2)))
        with self.assertRaisesRegex(PermissionError,"single_use_policy_required"):
            no_store.request_authenticated_action(**self.options(approval=signed("request",usage_policy=None)))
        store=DurableAdmissionStore(str(Path(self.tmp.name)/"admission.db"))
        first=PRAINRuntime(policies=policy,persistent_db_path=self.path,admission_store=store,approval_verification_key=issuer_key)
        receipt,decision=first.request_authenticated_action(**self.options(approval=signed("request")))
        self.assertTrue(decision["allowed"])
        second=PRAINRuntime(policies=policy,persistent_db_path=self.path,admission_store=store,approval_verification_key=issuer_key)
        replay,replay_decision=second.request_authenticated_action(**self.options(approval=signed("request")))
        self.assertEqual(replay.receipt_id,receipt.receipt_id)
        self.assertEqual(replay_decision["reason"],"idempotent_replay")
        conflict,decision=second.request_authenticated_action(**self.options(idempotency_key="other",approval=signed("other")))
        self.assertIsNone(conflict)
        self.assertFalse(decision["allowed"])

    def test_authenticated_receipt_replay_requires_current_policy_and_approval(self):
        issuer_key=b"issuer-only-test-key-for-production-auth-v1"
        policy=[{"policy_id":"approval.v1","action":"read","target":"item",
                 "required_capability":"read","approval_required":True}]
        now=datetime.now(timezone.utc)
        approval={"tenant":"org","principal":"person","action":"read","target":"item",
                  "input_hash":_canonical_hash({}),"idempotency_key":"request",
                  "expires_at":(now+timedelta(minutes=5)).isoformat()}
        raw=json.dumps(approval,sort_keys=True,separators=(",", ":"),allow_nan=False).encode()
        approval["issuer_signature"]=hmac.new(issuer_key,b"PRAIN-APPROVAL-v1\0"+raw,sha256).hexdigest()
        for persistent in (False,True):
            with self.subTest(durable_admission=persistent):
                store=DurableAdmissionStore(str(Path(self.tmp.name)/"replay-admission.db")) if persistent else None
                runtime=PRAINRuntime(policies=policy,persistent_db_path=self.path,
                                     admission_store=store,approval_verification_key=issuer_key)
                receipt,decision=runtime.request_authenticated_action(**self.options(approval=approval))
                self.assertTrue(decision["allowed"])
                self.assertIsNotNone(receipt)
                with patch("prain.policy_gateway.datetime") as clock:
                    clock.fromisoformat.side_effect=datetime.fromisoformat
                    clock.now.return_value=now+timedelta(minutes=10)
                    expired,decision=runtime.request_authenticated_action(**self.options(approval=approval))
                self.assertIsNone(expired)
                self.assertEqual(decision["reason"],"approval_expired")
                runtime.policy=type(runtime.policy)([])
                denied,decision=runtime.request_authenticated_action(**self.options(approval=approval))
                self.assertIsNone(denied)
                self.assertEqual(decision["reason"],"no_matching_policy")

if __name__ == "__main__":
    unittest.main()
