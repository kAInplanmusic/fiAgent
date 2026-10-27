import unittest
import tempfile
from pathlib import Path
from dataclasses import replace
from unittest.mock import patch
import prain.scf as scf_module
from prain.scf import SemanticClaim, SemanticFabric


def claim(**kw):
    values = dict(claim_id="a", subject="entity", predicate="state", value="ready",
        scope="team", source="sensor", evidence_refs=("evidence://a",),
        observed_at="2026-10-24T12:00:00Z", valid_until="2026-10-25T12:00:00Z",
        confidence=0.9)
    values.update(kw)
    return SemanticClaim(**values)


class SCFContractTests(unittest.TestCase):
    def setUp(self):
        self.fabric = SemanticFabric()
        self.now = "2026-10-24T14:00:00Z"

    def test_adopt_then_duplicate_and_stale(self):
        self.assertEqual(self.fabric.ingest(claim(), "team", self.now).decision, "adopt")
        self.assertEqual(self.fabric.ingest(claim(), "team", self.now).decision, "defer")
        self.assertEqual(self.fabric.ingest(claim(version=2), "team", self.now).decision, "adopt")
        self.assertEqual(self.fabric.ingest(claim(), "team", self.now).reason, "duplicate_or_stale_version")

    def test_scope_denied_without_projection(self):
        self.assertEqual(self.fabric.ingest(claim(), "elsewhere", self.now).decision, "ignore_out_of_scope")
        self.assertIsNone(self.fabric.projection("a"))

    def test_missing_evidence_requests_proof(self):
        self.assertEqual(self.fabric.ingest(claim(evidence_refs=()), "team", self.now).decision, "request_evidence")

    def test_future_and_expired_claims_not_adopted(self):
        self.assertEqual(self.fabric.ingest(claim(), "team", "2026-10-24T11:00:00Z").reason, "future_observation")
        self.assertEqual(self.fabric.ingest(claim(), "team", "2026-10-26T12:00:00Z").reason, "expired_claim")

    def test_version_gap_defers(self):
        self.fabric.ingest(claim(), "team", self.now)
        self.assertEqual(self.fabric.ingest(claim(version=3), "team", self.now).reason, "version_gap")

    def test_identity_conflict_is_registered(self):
        self.fabric.ingest(claim(), "team", self.now)
        self.assertEqual(self.fabric.ingest(claim(subject="other", version=2), "team", self.now).decision, "raise_conflict")
        self.assertEqual(len(self.fabric.conflicts()), 1)
        self.assertEqual(self.fabric.projection("a").subject, "entity")

    def test_same_revision_changed_content_is_conflict_not_duplicate(self):
        self.fabric.ingest(claim(value=1), "team", self.now)
        self.assertEqual(self.fabric.ingest(claim(value=1), "team", self.now).reason, "duplicate_version")
        result = self.fabric.ingest(claim(value=True), "team", self.now)
        self.assertEqual((result.decision, result.reason), ("raise_conflict", "same_version_changed_claim"))
        self.assertEqual(self.fabric.projection("a").value, 1)
        self.assertEqual(self.fabric.conflicts()[-1]["reason"], "same_version_changed_claim")
        self.assertIs(self.fabric.conflicts()[-1]["conflicting_claim"]["value"], True)

    def test_non_json_values_rejected_before_first_projection(self):
        circular = []
        circular.append(circular)
        for value in (object(), {1: "non-string key"}, float("nan"), circular, (1, 2)):
            with self.subTest(value=type(value).__name__), self.assertRaisesRegex(ValueError, "claim_not_canonical_json"):
                self.fabric.ingest(claim(value=value), "team", self.now)
        self.assertIsNone(self.fabric.projection("a"))
        self.assertEqual(self.fabric.decisions(), [])

    def test_mutation_after_snapshot_does_not_change_projection(self):
        value = {"nested": ["original"]}
        original_validator = scf_module._canonical_claim
        def mutate_external_then_validate(snapshot):
            value["nested"].append("concurrent")
            return original_validator(snapshot)
        with patch("prain.scf._canonical_claim", side_effect=mutate_external_then_validate):
            self.fabric.ingest(claim(value=value), "team", self.now)
        self.assertEqual(self.fabric.projection("a").value, {"nested": ["original"]})

    def test_dependency_invalidated_on_update(self):
        self.fabric.ingest(claim(), "team", self.now)
        self.fabric.ingest(claim(claim_id="b", dependencies=("a",)), "team", self.now)
        self.fabric.ingest(claim(version=2), "team", self.now)
        with self.assertRaisesRegex(ValueError, "projection_invalidated"):
            self.fabric.projection("b")

    def test_transitive_dependency_invalidated_on_update(self):
        for item in (claim(), claim(claim_id="b", dependencies=("a",)),
                     claim(claim_id="c", dependencies=("b",))):
            self.assertEqual(self.fabric.ingest(item, "team", self.now).decision, "adopt")
        self.assertEqual(self.fabric.ingest(claim(version=2), "team", self.now).decision, "adopt")
        for item_id in ("b", "c"):
            with self.subTest(item_id=item_id), self.assertRaisesRegex(ValueError, "projection_invalidated"):
                self.fabric.projection(item_id)

    def test_new_claim_cannot_use_an_invalidated_premise(self):
        self.fabric.ingest(claim(), "team", self.now)
        self.fabric.ingest(claim(claim_id="b", dependencies=("a",)), "team", self.now)
        self.fabric.ingest(claim(version=2), "team", self.now)
        decision = self.fabric.ingest(claim(claim_id="c", dependencies=("b",)), "team", self.now)
        self.assertEqual((decision.decision, decision.reason), ("defer", "dependency_invalidated"))
        self.assertIsNone(self.fabric.projection("c"))

    def test_revision_without_premise_version_proof_does_not_clear_invalidation(self):
        self.fabric.ingest(claim(), "team", self.now)
        self.fabric.ingest(claim(claim_id="b", dependencies=("a",)), "team", self.now)
        self.fabric.ingest(claim(version=2), "team", self.now)
        self.fabric.ingest(claim(claim_id="b", version=2, dependencies=("a",)), "team", self.now)
        with self.assertRaisesRegex(ValueError, "projection_invalidated"):
            self.fabric.projection("b")
        self.assertEqual(self.fabric.ingest(claim(claim_id="c", dependencies=("b",)),
                                            "team", self.now).reason, "dependency_invalidated")

    def test_invalidated_premise_blocks_new_claim_after_restart(self):
        from prain.durable_semantics import DurableSemanticFabric
        with tempfile.TemporaryDirectory() as directory:
            db = str(Path(directory) / "scf.sqlite")
            fabric = DurableSemanticFabric(db)
            fabric.ingest(claim(), "team", self.now)
            fabric.ingest(claim(claim_id="b", dependencies=("a",)), "team", self.now)
            fabric.ingest(claim(version=2), "team", self.now)
            restarted = DurableSemanticFabric(db)
            result = restarted.ingest(claim(claim_id="c", dependencies=("b",)), "team", self.now)
            self.assertEqual((result.decision, result.reason), ("defer", "dependency_invalidated"))
            self.assertIsNone(DurableSemanticFabric(db).projection("c"))

    def test_hypothesis_remains_explicit(self):
        d = self.fabric.ingest(claim(epistemic_status="hypothesis"), "team", self.now)
        self.assertEqual(d.decision, "retain_as_hypothesis")
        self.assertEqual(self.fabric.projection("a").epistemic_status, "hypothesis")

    def test_hypothesis_revision_invalidates_transitive_dependents(self):
        for item in (claim(), claim(claim_id="b", dependencies=("a",)),
                     claim(claim_id="c", dependencies=("b",))):
            self.fabric.ingest(item, "team", self.now)
        revision = claim(version=2, value="uncertain", epistemic_status="hypothesis")
        self.assertEqual(self.fabric.ingest(revision, "team", self.now).decision, "retain_as_hypothesis")
        self.assertEqual(self.fabric.projection("a").epistemic_status, "hypothesis")
        for claim_id in ("b", "c"):
            with self.subTest(claim_id=claim_id), self.assertRaisesRegex(ValueError, "projection_invalidated"):
                self.fabric.projection(claim_id)

    def test_rejected_hypothesis_revision_does_not_invalidate_dependents(self):
        self.fabric.ingest(claim(), "team", self.now)
        self.fabric.ingest(claim(claim_id="b", dependencies=("a",)), "team", self.now)
        decision = self.fabric.ingest(claim(version=2, epistemic_status="hypothesis", evidence_refs=()), "team", self.now)
        self.assertEqual(decision.decision, "request_evidence")
        self.assertIsNotNone(self.fabric.projection("b"))

    def test_reject_invalid_schema(self):
        for kw in [dict(confidence=float("nan")), dict(version=True),
                   dict(observed_at="2026-10-24T12:00:00"),
                   dict(valid_until="2026-10-24T11:00:00Z"),
                   dict(epistemic_status="fact")]:
            with self.subTest(kw=kw):
                with self.assertRaises(ValueError):
                    claim(**kw)
