import csv
import importlib.util
import unittest
from pathlib import Path

class DiscrepancyReviewTests(unittest.TestCase):
    def test_all_69_preserved_and_explained(self):
        p=Path(__file__).resolve().parents[2]/"tools"/"analyze_69_discrepancies.py"
        spec=importlib.util.spec_from_file_location("analyze_69_discrepancies",p)
        mod=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        report=mod.analyze()
        self.assertEqual(report["examined"],69)
        self.assertEqual(report["classifications"]["MULTIPLE_EXACT_MATCHES"],68)
        self.assertEqual(report["classifications"]["SOURCE_TEXT_ABSENT"],1)
        self.assertEqual(report["normative_acceptances"],0)
