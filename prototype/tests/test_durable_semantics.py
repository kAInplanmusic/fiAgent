import tempfile
import unittest
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
import prain.durable_semantics as durable_module

from prain import PRAINRuntime
from prain.anima_hal import AnimaConflict
from prain.scf import SemanticClaim


def claim(version=1, claim_id="a", dependencies=()):
    return SemanticClaim(claim_id=claim_id, subject="component", predicate="health",
        value="ok", scope="local", source="probe", evidence_refs=("evidence://a",),
        observed_at="2026-10-24T14:00:00Z", valid_until="2026-10-26T14:00:00Z",
        confidence=0.9, version=version, dependencies=dependencies)


class DurableSemanticIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = str(Path(self.temp.name) / "runtime.sqlite")
        self.a = PRAINRuntime(persistent_db_path=self.path)

    def test_anima_restarts_and_preserves_identity(self):
        self.a.anima.update(expected_version=0, dimension="reason",
                            state={"goal": "a"}, provenance="test")
        b = PRAINRuntime(persistent_db_path=self.path)
        self.assertEqual(b.anima.snapshot().version, 1)
        self.assertEqual(b.anima.snapshot().dimensions["reason"]["goal"], "a")
        self.assertEqual(b.anima.snapshot().identity_id, self.a.anima.snapshot().identity_id)

    def test_anima_stale_writer_denied_across_instances(self):
        b = PRAINRuntime(persistent_db_path=self.path)
        self.a.anima.update(expected_version=0, dimension="reason", state={"x": 1}, provenance="a")
        with self.assertRaises(AnimaConflict):
            b.anima.update(expected_version=0, dimension="reason", state={"x": 2}, provenance="b")

    def test_anima_concurrent_cas_one_winner(self):
        b = PRAINRuntime(persistent_db_path=self.path)
        def update(runtime):
            try:
                runtime.anima.update(expected_version=0, dimension="reason", state={"x": 1}, provenance="race")
                return True
            except AnimaConflict:
                return False
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(update, [self.a, b]))
        self.assertEqual(results.count(True), 1)
        self.assertEqual(PRAINRuntime(persistent_db_path=self.path).anima.snapshot().version, 1)

    def test_scf_claims_survive_restart(self):
        self.assertEqual(self.a.scf.ingest(claim(), "local", "2026-10-25T14:00:00Z").decision, "adopt")
        b = PRAINRuntime(persistent_db_path=self.path)
        self.assertEqual(b.scf.projection("a").version, 1)
        self.assertEqual(b.scf.ingest(claim(version=2), "local", "2026-10-25T14:00:00Z").decision, "adopt")
        self.assertEqual(self.a.scf.projection("a").version, 2)

    def test_scf_conflict_persists(self):
        self.a.scf.ingest(claim(), "local", "2026-10-25T14:00:00Z")
        original = claim(version=2)
        bad = SemanticClaim(**{**original.__dict__, "subject": "different"})
        self.assertEqual(self.a.scf.ingest(bad, "local", "2026-10-25T14:00:00Z").decision, "raise_conflict")
        self.assertEqual(len(PRAINRuntime(persistent_db_path=self.path).scf.conflicts()), 1)

    def test_scf_same_revision_changed_claim_conflict_survives_restart(self):
        self.a.scf.ingest(claim(), "local", "2026-10-25T14:00:00Z")
        changed = SemanticClaim(**{**claim().__dict__, "value": "changed"})
        result = self.a.scf.ingest_message("other-message", changed, "local", "2026-10-25T14:00:00Z")
        self.assertEqual((result.decision, result.reason), ("raise_conflict", "same_version_changed_claim"))
        restarted = PRAINRuntime(persistent_db_path=self.path)
        self.assertEqual(restarted.scf.conflicts()[-1]["reason"], result.reason)
        self.assertEqual(restarted.scf.conflicts()[-1]["conflicting_claim"]["value"], "changed")
        self.assertEqual(restarted.scf.projection("a").value, claim().value)
        self.assertEqual(restarted.scf.ingest_message("other-message", changed, "local", "2026-10-25T14:00:00Z"), result)

    def test_invalid_json_claim_rejected_before_durable_write(self):
        bad = SemanticClaim(**{**claim().__dict__, "value": {1: "invalid key"}})
        with self.assertRaisesRegex(ValueError, "claim_not_canonical_json"):
            self.a.scf.ingest_message("invalid", bad, "local", "2026-10-25T14:00:00Z")
        self.assertEqual(PRAINRuntime(persistent_db_path=self.path).scf.decisions(), [])
        self.assertIsNone(self.a.scf.projection("a"))

    def test_mutation_after_fingerprint_snapshot_cannot_change_durable_claim(self):
        value = {"nested": ["original"]}
        original_validator = durable_module._canonical_claim
        def mutate_external_then_validate(snapshot):
            value["nested"].append("concurrent")
            return original_validator(snapshot)
        changed = SemanticClaim(**{**claim().__dict__, "value": value})
        with patch("prain.durable_semantics._canonical_claim", side_effect=mutate_external_then_validate):
            first = self.a.scf.ingest_message("snapshot", changed, "local", "2026-10-25T14:00:00Z")
        restarted = PRAINRuntime(persistent_db_path=self.path)
        self.assertEqual(restarted.scf.projection("a").value, {"nested": ["original"]})
        original = SemanticClaim(**{**claim().__dict__, "value": {"nested": ["original"]}})
        self.assertEqual(restarted.scf.ingest_message("snapshot", original, "local", "2026-10-25T14:00:00Z"), first)
        with self.assertRaisesRegex(ValueError, "message_id_conflict"):
            restarted.scf.ingest_message("snapshot", changed, "local", "2026-10-25T14:00:00Z")

    def test_scf_dependency_invalidation_survives_restart(self):
        self.a.scf.ingest(claim(), "local", "2026-10-25T14:00:00Z")
        self.a.scf.ingest(claim(claim_id="b", dependencies=("a",)), "local", "2026-10-25T14:00:00Z")
        self.a.scf.ingest(claim(version=2), "local", "2026-10-25T14:00:00Z")
        with self.assertRaises(ValueError):
            PRAINRuntime(persistent_db_path=self.path).scf.projection("b")

    def test_transitive_invalidation_survives_restart(self):
        for item in (claim(), claim(claim_id="b", dependencies=("a",)),
                     claim(claim_id="c", dependencies=("b",))):
            self.a.scf.ingest(item, "local", "2026-10-25T14:00:00Z")
        self.a.scf.ingest(claim(version=2), "local", "2026-10-25T14:00:00Z")
        restarted = PRAINRuntime(persistent_db_path=self.path)
        for item_id in ("b", "c"):
            with self.subTest(item_id=item_id), self.assertRaisesRegex(ValueError, "projection_invalidated"):
                restarted.scf.projection(item_id)

    def test_hypothesis_revision_invalidates_dependents_after_restart_and_replay(self):
        for item in (claim(), claim(claim_id="b", dependencies=("a",)),
                     claim(claim_id="c", dependencies=("b",))):
            self.a.scf.ingest(item, "local", "2026-10-25T14:00:00Z")
        revision = SemanticClaim(**{**claim(version=2).__dict__, "epistemic_status": "hypothesis", "value": "uncertain"})
        decision = self.a.scf.ingest_message("hypothesis-update", revision, "local", "2026-10-25T14:00:00Z")
        self.assertEqual(decision.decision, "retain_as_hypothesis")
        restarted = PRAINRuntime(persistent_db_path=self.path)
        self.assertEqual(restarted.scf.ingest_message("hypothesis-update", revision, "local", "2026-10-25T14:00:00Z"), decision)
        for item_id in ("b", "c"):
            with self.subTest(item_id=item_id), self.assertRaisesRegex(ValueError, "projection_invalidated"):
                restarted.scf.projection(item_id)

    def test_scf_concurrent_duplicate_only_one_adopted(self):
        b = PRAINRuntime(persistent_db_path=self.path)
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda r: r.scf.ingest(claim(), "local", "2026-10-25T14:00:00Z").decision, [self.a, b]))
        self.assertEqual(sorted(results), ["adopt", "defer"])
        self.assertEqual(PRAINRuntime(persistent_db_path=self.path).scf.projection("a").version, 1)
    def test_scf_inbox_exact_replay_after_restart(self):
        first = self.a.scf.ingest_message("message-1", claim(), "local", "2026-10-25T14:00:00Z")
        self.assertEqual(first.decision, "adopt")
        b = PRAINRuntime(persistent_db_path=self.path)
        again = b.scf.ingest_message("message-1", claim(), "local", "2026-10-25T14:00:00Z")
        self.assertEqual(again, first)
        self.assertEqual(len(b.scf.decisions()), 1)

    def test_scf_inbox_same_id_changed_body_rejected(self):
        self.a.scf.ingest_message("message-1", claim(), "local", "2026-10-25T14:00:00Z")
        with self.assertRaisesRegex(ValueError, "message_id_conflict"):
            self.a.scf.ingest_message("message-1", claim(version=2), "local", "2026-10-25T14:00:00Z")
        self.assertEqual(self.a.scf.projection("a").version, 1)

    def test_scf_inbox_concurrent_replay(self):
        b = PRAINRuntime(persistent_db_path=self.path)
        def deliver(runtime):
            return runtime.scf.ingest_message("message-1", claim(), "local", "2026-10-25T14:00:00Z")
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(deliver, [self.a, b]))
        self.assertEqual([r.decision for r in results], ["adopt", "adopt"])
        self.assertEqual(len(self.a.scf.decisions()), 1)
