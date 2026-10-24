import unittest
from datetime import datetime, timezone

from prain import PRAINRuntime
from prain.scf import SemanticClaim
from prain.anima_hal import HealthObservation


class RuntimeArchitecturalWiringTests(unittest.TestCase):
    def test_semantic_anima_hal_are_local_and_separate_from_action_authority(self):
        runtime = PRAINRuntime()
        claim = SemanticClaim(
            claim_id="c1", subject="component:scf", predicate="readiness",
            value="healthy", scope="local", source="health-probe",
            evidence_refs=("source-evidence",), observed_at="2026-10-24T14:00:00Z",
            valid_until="2026-10-25T14:00:00Z", confidence=0.9)
        d = runtime.scf.ingest(claim, "local", "2026-10-24T15:00:00Z")
        self.assertEqual(d.decision, "adopt")
        self.assertEqual(runtime.scf.projection("c1").value, "healthy")
        m = runtime.anima.update(expected_version=0, dimension="perception",
            state={"observed_claim": "c1"}, provenance="scf:c1")
        self.assertEqual(m.version, 1)
        h = runtime.hal.assess(HealthObservation(
            "scf", True, "2026-10-24T15:00:00Z", "source-evidence"),
            datetime(2026, 10, 24, 15, 0, tzinfo=timezone.utc))
        self.assertEqual((h.health, h.action), ("healthy", "observe_only"))
        receipt, decision = runtime.request_action(
            "run", "target", "run", "actor", {}, "corr-1", "key-1")
        self.assertIsNone(receipt)
        self.assertFalse(decision["allowed"])
