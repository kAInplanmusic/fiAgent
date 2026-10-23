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

    def test_current_status_distinguishes_specification_and_runtime(self):
        text = (ROOT / 'docs/PHASE1_IMPLEMENTATION_STATUS.md').read_text()
        self.assertIn('v0.99.6', text)
        self.assertIn('Phase 1 remains open', text)
        self.assertIn('PARTIAL_PASS', text)
