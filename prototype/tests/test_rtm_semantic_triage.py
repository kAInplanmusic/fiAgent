import importlib.util
import unittest
from pathlib import Path

class SemanticRTMTriageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path=Path(__file__).resolve().parents[2]/"tools"/"triage_rtm_semantics.py"
        spec=importlib.util.spec_from_file_location("triage_rtm_semantics",path)
        m=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        cls.m=m
    def test_whole_matrix_covered_without_acceptance(self):
        result=self.m.run()
        self.assertTrue(result["row_coverage"])
        self.assertEqual(result["total"],5071)
        self.assertEqual(result["normatively_accepted"],0)
        self.assertEqual(result["review_pending"],5071)
    def test_types_are_non_normative_proposals(self):
        for text, expected in [('## Context','STRUCTURAL_CANDIDATE'),
                              ('"type": "string",','SCHEMA_FIELD_CANDIDATE'),
                              ('Must reject stale writers.','NORMATIVE_LANGUAGE_CANDIDATE')]:
            self.assertEqual(self.m.classify(text,{})[0],expected)
