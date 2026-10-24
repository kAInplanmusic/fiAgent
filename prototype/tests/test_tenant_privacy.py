import tempfile
import unittest
from pathlib import Path
from prain.tenant_access import TenantAccess, AccessDenied
from prain.private_projections import PrivateProjections, ProjectionDeleted

class TenantPrivacyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        db = str(Path(self.tmp.name) / "state.sqlite3")
        self.access = TenantAccess(db)
        self.projections = PrivateProjections(db)

    def test_isolation_revocation_rotation(self):
        credential = self.access.provision("a", "person", [("read", "item")])
        self.assertTrue(self.access.authorize("a", "person", credential, "read", "item"))
        with self.assertRaises(AccessDenied):
            self.access.authorize("b", "person", credential, "read", "item")
        with self.assertRaises(AccessDenied):
            self.access.authorize("a", "person", credential, "write", "item")
        replacement = self.access.rotate("a", "person", credential)
        with self.assertRaises(AccessDenied):
            self.access.authorize("a", "person", credential, "read", "item")
        self.assertTrue(self.access.authorize("a", "person", replacement, "read", "item"))
        self.access.revoke("a", "person")
        with self.assertRaises(AccessDenied):
            self.access.authorize("a", "person", replacement, "read", "item")

    def test_projection_deletion_tenant_scoped(self):
        self.projections.upsert("a", "item", "internal", {"x": 1})
        self.projections.upsert("b", "item", "public", {"x": 2})
        self.projections.delete_source("a", "item")
        self.assertIsNone(self.projections.read("a", "item"))
        self.assertEqual(self.projections.read("b", "item")["payload"]["x"], 2)
        with self.assertRaises(ProjectionDeleted):
            self.projections.upsert("a", "item", "public", {"x": 3})
    def test_authenticated_runtime_enforces_grants_before_replay(self):
        from prain import PRAINRuntime
        runtime = PRAINRuntime(
            policies=[{"policy_id":"p","action":"read","target":"item",
                       "required_capability":"read"}],
            persistent_db_path=self.access.database)
        token = runtime.tenant_access.provision("org", "person", [("read", "item")])
        options = dict(tenant="org", principal="person", credential=token,
                       action="read", target="item", capability="read", payload={},
                       correlation_id="c", idempotency_key="idempotent")
        receipt, decision = runtime.request_authenticated_action(**options)
        self.assertIsNotNone(receipt)
        self.assertTrue(decision["allowed"])
        runtime.tenant_access.revoke("org", "person")
        with self.assertRaises(AccessDenied):
            runtime.request_authenticated_action(**options)
        self.assertIsNone(self.projections.read("org", "item"))

    def test_in_memory_authentication_unavailable(self):
        from prain import PRAINRuntime
        runtime = PRAINRuntime()
        with self.assertRaises(PermissionError):
            runtime.request_authenticated_action(tenant="org", principal="person",
                credential="not-a-real-credential", action="read", target="item",
                capability="read", payload={}, correlation_id="c", idempotency_key="i")
