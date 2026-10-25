import unittest
import importlib.util
from pathlib import Path
module_path = Path(__file__).resolve().parents[2] / "tools" / "verify_phase1_gates.py"
spec = importlib.util.spec_from_file_location("verify_phase1_gates", module_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
validate, REQUIRED = module.validate, module.REQUIRED

class GateValidationTests(unittest.TestCase):
    def test_unaccepted_gates_fail_closed(self):
        document={"schema_version":1,"project":"PRAIN",
                  "gates":{g:"OPEN" for g in REQUIRED},
                  "phase1":{"status":"PARTIAL_PASS","strict_b_accepted":False}}
        failures=validate(document)
        self.assertIn("G00:not_accepted",failures)
        self.assertIn("independent_review_missing",failures)
    def test_missing_gate_rejected(self):
        self.assertIn("incomplete_gate_inventory",validate({"gates":{}}))
    def test_no_fabricated_signoff(self):
        document={"schema_version":1,"project":"PRAIN",
                  "gates":{g:"ACCEPTED" for g in REQUIRED},
                  "gate_evidence":{g:["test"] for g in REQUIRED},
                  "blocking_requirements":[],
                  "phase1":{"status":"PHASE1_GREEN_STRICT_B","strict_b_accepted":True}}
        self.assertIn("independent_review_missing", validate(document))