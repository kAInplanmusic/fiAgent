import importlib.util
import unittest
from pathlib import Path

class ReferenceResolutionTests(unittest.TestCase):
    def test_all_69_have_exact_canonical_sources(self):
        path=Path(__file__).resolve().parents[2]/"tools"/"finalize_69_references.py"
        spec=importlib.util.spec_from_file_location("finalize_69_references",path)
        module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result=module.resolve()
        self.assertEqual(result["resolved_references"],69)
        self.assertEqual(result["reference_open"],0)
        self.assertEqual(result["canonical_roadmap_work_items"],68)
        self.assertEqual(result["historical_informational"],1)
        self.assertEqual(result["runtime_accepted"],0)
