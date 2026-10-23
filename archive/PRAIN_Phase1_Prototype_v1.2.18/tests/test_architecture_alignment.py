import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class ArchitectureAlignmentTests(unittest.TestCase):
    def test_alignment_covers_canonical_architecture(self):
        text = (ROOT / "docs" / "ARCHITECTURE_ALIGNMENT.md").read_text(encoding="utf-8")
        for required in ("Perception", "Reason", "Anima", "Intention", "Nerve", "SCF", "HAL", "Invariant & Evidence Layer", "L0", "L3"):
            with self.subTest(required=required):
                self.assertIn(required, text)

    def test_traceability_records_core_open_gaps(self):
        text = (ROOT / "docs" / "REQUIREMENT_TRACEABILITY.md").read_text(encoding="utf-8")
        for required in ("Phase 0 v0.2.1", "Distributed Protocol v0.5", "v0.6", "SCF", "Anima", "HAL", "Phase 0 stays open"):
            with self.subTest(required=required):
                self.assertIn(required, text)

    def test_phase_zero_not_claimed_closed(self):
        for rel in ("README.md", "docs/ARCHITECTURE_ALIGNMENT.md", "docs/PHASE1_IMPLEMENTATION_STATUS.md"):
            with self.subTest(file=rel):
                text = (ROOT / rel).read_text(encoding="utf-8").lower()
                self.assertIn("phase 0", text)
                self.assertTrue("not formally" in text or "remains open" in text or "not closed" in text)
