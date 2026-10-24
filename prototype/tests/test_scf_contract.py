import unittest
from dataclasses import replace
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

    def test_dependency_invalidated_on_update(self):
        self.fabric.ingest(claim(), "team", self.now)
        self.fabric.ingest(claim(claim_id="b", dependencies=("a",)), "team", self.now)
        self.fabric.ingest(claim(version=2), "team", self.now)
        with self.assertRaisesRegex(ValueError, "projection_invalidated"):
            self.fabric.projection("b")

    def test_hypothesis_remains_explicit(self):
        d = self.fabric.ingest(claim(epistemic_status="hypothesis"), "team", self.now)
        self.assertEqual(d.decision, "retain_as_hypothesis")
        self.assertEqual(self.fabric.projection("a").epistemic_status, "hypothesis")

    def test_reject_invalid_schema(self):
        for kw in [dict(confidence=float("nan")), dict(version=True),
                   dict(observed_at="2026-10-24T12:00:00"),
                   dict(valid_until="2026-10-24T11:00:00Z"),
                   dict(epistemic_status="fact")]:
            with self.subTest(kw=kw):
                with self.assertRaises(ValueError):
                    claim(**kw)
