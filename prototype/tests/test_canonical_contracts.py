"""Actual canonical schema fixtures and hostile runtime ingress, without skips."""
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest
from prain.canonical_contracts import CanonicalContracts, ContractRejected, CONTRACT_ROOT, loads_strict, quarantine_legacy_claim
from prain.canonical_ingress import CanonicalInbox
from prain.tenant_access import TenantAccess

FIXTURES = json.loads((CONTRACT_ROOT / "contract_fixtures.json").read_text())
NOW = "2026-10-20T12:00:00Z"


class CanonicalContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contracts = CanonicalContracts()

    def test_all_17_canonical_fixtures_validate(self):
        self.assertEqual(len(self.contracts.names), 17)
        for name, value in FIXTURES["valid"].items():
            with self.subTest(schema=name):
                self.assertEqual(self.contracts.validate(name, value), value)

    def test_all_16_archived_negative_fixtures_rejected(self):
        self.assertEqual(len(FIXTURES["invalid"]), 16)
        for name, fixture in FIXTURES["invalid"].items():
            bad = deepcopy(FIXTURES["valid"][fixture["schema"]])
            bad.update(fixture["mutation"])
            with self.subTest(fixture=name), self.assertRaises(ContractRejected):
                self.contracts.validate(fixture["schema"], bad)

    def test_unknown_root_fields_rejected_for_every_contract(self):
        for name, value in FIXTURES["valid"].items():
            bad = deepcopy(value)
            bad["grant_superuser"] = True
            with self.subTest(schema=name), self.assertRaises(ContractRejected):
                self.contracts.validate(name, bad)

    def test_required_field_types_and_root_enums(self):
        for name, value in FIXTURES["valid"].items():
            schema = self.contracts.schema(name)
            for key in schema["required"]:
                bad = deepcopy(value)
                bad[key] = None
                with self.subTest(schema=name, field=key), self.assertRaises(ContractRejected):
                    self.contracts.validate(name, bad)
            for key, spec in schema["properties"].items():
                if "enum" in spec:
                    bad = deepcopy(value)
                    bad[key] = "UNDECLARED_ENUM_VALUE"
                    with self.subTest(schema=name, enum=key), self.assertRaises(ContractRejected):
                        self.contracts.validate(name, bad)

    def test_finite_numbers_timezone_and_strict_integer(self):
        for invalid in (float("nan"), float("inf"), float("-inf"), True):
            bad = deepcopy(FIXTURES["valid"]["claim"])
            bad.update(confidence=invalid, confidence_method="model_self_estimate")
            with self.subTest(value=invalid), self.assertRaises(ContractRejected):
                self.contracts.validate("claim", bad)
        bad = deepcopy(FIXTURES["valid"]["claim"])
        bad["revision"] = True
        with self.assertRaises(ContractRejected):
            self.contracts.validate("claim", bad)
        for stamp in ("2026-10-20T12:00:00", "2026-10-20T14:00:00+02:00", "2026-10-20T12:00:00-00:00", "2026-02-30T12:00:00Z"):
            bad = deepcopy(FIXTURES["valid"]["claim"])
            bad["recorded_at"] = stamp
            with self.subTest(timestamp=stamp), self.assertRaises(ContractRejected):
                self.contracts.validate("claim", bad)

    def test_no_unknown_schema_network_resolution(self):
        for schema in ("https://attacker.invalid/schema", "urn:prain:schema:claim:2.0.0", "claim:1.0.0"):
            with self.subTest(schema=schema), self.assertRaises(ContractRejected):
                self.contracts.validate(schema, FIXTURES["valid"]["claim"])

    def test_schema_and_validated_values_are_detached(self):
        schema = self.contracts.schema("claim")
        schema["required"].clear()
        with self.assertRaises(ContractRejected):
            self.contracts.validate("claim", {})
        value = deepcopy(FIXTURES["valid"]["claim"])
        result = self.contracts.validate("claim", value)
        result["proposition"]["statement"] = "changed"
        self.assertNotEqual(value, result)

    def test_bundled_contract_and_manifest_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp) / "contracts"
            shutil.copytree(CONTRACT_ROOT, directory)
            (directory / "claim.schema.json").write_text("{}")
            with self.assertRaisesRegex(ContractRejected, "integrity"):
                CanonicalContracts(directory)
            manifest = json.loads((directory / "MANIFEST.json").read_text())
            manifest["files"]["claim.schema.json"]["sha256"] = hashlib.sha256(b"{}").hexdigest()
            (directory / "MANIFEST.json").write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ContractRejected, "manifest_integrity"):
                CanonicalContracts(directory)

    def test_strict_decoder_duplicate_nonfinite_and_resource_limits(self):
        for raw in (b'{"x":1,"x":2}', b'{"nested":{"x":1,"x":2}}', b'{"x":NaN}', b'{"x":1e999}', b'\xff', b"[" * 2000):
            with self.subTest(raw=raw[:40]), self.assertRaises(ContractRejected):
                loads_strict(raw)
        with self.assertRaises(ContractRejected):
            loads_strict(b" " * 65537)
        with self.assertRaises(ContractRejected):
            self.contracts.validate("claim", {"x": [0] * 10001})

    def test_legacy_unknown_and_verified_are_losslessly_quarantined(self):
        for state in ("unknown-new-value", "verified", "unverified"):
            legacy = {"id": "legacy:1", "verification_status": state, "confidence": 1.0,
                      "statement": "Unverified historical statement", "evidence_refs": []}
            result = quarantine_legacy_claim(legacy,
                source_schema_id="https://prain.dev/schema/claim-0.1.0.json",
                source_version="0.1.0", source_ref="archive:claim")
            self.assertEqual(result["source_snapshot"], legacy)
            self.assertEqual(result["legacy_verification"], state)
            self.assertEqual(result["status"], "quarantined")
            self.assertIsNone(result["canonical_claim"])
            self.assertEqual(result, quarantine_legacy_claim(legacy,
                source_schema_id="https://prain.dev/schema/claim-0.1.0.json",
                source_version="0.1.0", source_ref="archive:claim"))
        with self.assertRaises(ContractRejected):
            quarantine_legacy_claim({"id": "x"}, source_schema_id="invented", source_version="0.1.0", source_ref="x")


class CanonicalIngressTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = Path(self.tmp.name) / "inbox.sqlite"
        self.access = TenantAccess(self.db)
        self.token = self.access.provision("tenant:1", "principal:1", [("receive", "inbox")])
        self.other = self.access.provision("tenant:2", "principal:2", [("receive", "inbox")])
        def authenticate(credential):
            tenant, principal, token = credential
            self.access.authorize(tenant, principal, token, "receive", "inbox")
            return tenant, principal
        self.authenticate = authenticate
        self.credential = ("tenant:1", "principal:1", self.token)
        self.inbox = CanonicalInbox(self.db, authenticate=authenticate)
        self.envelope = deepcopy(FIXTURES["valid"]["message-envelope"])
        self.envelope["payload"] = deepcopy(FIXTURES["valid"]["health-signal"])

    def accept(self, value=None, credential=None):
        return self.inbox.accept(json.dumps(value or self.envelope).encode(),
                                 credential=credential or self.credential, now=NOW)

    def rows(self):
        with sqlite3.connect(self.db) as db:
            return db.execute("SELECT count(*) FROM prain_canonical_inbox").fetchone()[0]

    def test_complete_validated_envelope_survives_restart_and_deduplicates(self):
        self.assertFalse(self.accept()["duplicate"])
        restored = CanonicalInbox(self.db, authenticate=self.authenticate)
        self.assertEqual(restored.get("message:1", credential=self.credential), self.envelope)
        self.assertTrue(restored.accept(json.dumps(self.envelope).encode(), credential=self.credential, now=NOW)["duplicate"])
        self.assertEqual(self.rows(), 1)
        changed = deepcopy(self.envelope)
        changed["payload"]["value"] = 3
        with self.assertRaisesRegex(ContractRejected, "body_conflict"):
            self.accept(changed)
        self.assertEqual(restored.get("message:1", credential=self.credential), self.envelope)

    def test_authentication_and_revoked_replay_fail_before_write(self):
        with self.assertRaises(PermissionError):
            self.accept(credential=("tenant:1", "principal:1", "bad"))
        self.assertEqual(self.rows(), 0)
        self.accept()
        self.access.revoke("tenant:1", "principal:1")
        with self.assertRaises(PermissionError):
            self.accept()
        self.assertEqual(self.rows(), 1)

    def test_cross_tenant_principal_and_payload_spoof_no_write(self):
        for key, value in (("tenant_id", "tenant:2"), ("producer_principal_id", "principal:2")):
            bad = deepcopy(self.envelope)
            bad[key] = value
            with self.subTest(field=key), self.assertRaises(ContractRejected):
                self.accept(bad)
        bad = deepcopy(self.envelope)
        bad["payload"]["tenant_id"] = "tenant:2"
        with self.assertRaises(ContractRejected):
            self.accept(bad)
        self.assertEqual(self.rows(), 0)
        self.accept()
        self.assertIsNone(self.inbox.get("message:1", credential=("tenant:2", "principal:2", self.other)))

    def test_schema_version_nested_payload_and_stale_input_no_write(self):
        mutations = [{"schema_id": "https://attacker.invalid/remote"}, {"payload_schema_version": "2.0.0"},
                     {"payload": {"status": "test"}}, {"expires_at": NOW},
                     {"created_at": "2026-10-20T12:01:00Z"}, {"payload": {**self.envelope["payload"], "superuser": True}}]
        for mutation in mutations:
            bad = deepcopy(self.envelope)
            bad.update(mutation)
            with self.subTest(mutation=mutation), self.assertRaises(ContractRejected):
                self.accept(bad)
        self.assertEqual(self.rows(), 0)

    def test_envelope_cannot_downgrade_payload_classification(self):
        value = deepcopy(self.envelope)
        value["schema_id"] = "urn:prain:schema:observation:1.0.0"
        value["payload"] = deepcopy(FIXTURES["valid"]["observation"])
        value["payload"]["classification"] = "restricted"
        value["classification"] = "public"
        with self.assertRaisesRegex(ContractRejected, "classification_downgrade"):
            self.accept(value)
        self.assertEqual(self.rows(), 0)
        value["classification"] = "restricted"
        self.assertFalse(self.accept(value)["duplicate"])

    def test_independent_connections_racing_duplicate_store_once(self):
        def receive(_index):
            inbox = CanonicalInbox(self.db, authenticate=self.authenticate, contracts=self.inbox.contracts)
            return inbox.accept(json.dumps(self.envelope).encode(), credential=self.credential, now=NOW)
        with ThreadPoolExecutor(max_workers=8) as workers:
            results = list(workers.map(receive, range(8)))
        self.assertEqual(sum(not result["duplicate"] for result in results), 1)
        self.assertEqual(self.rows(), 1)
