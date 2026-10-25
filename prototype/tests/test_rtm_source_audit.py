import importlib.util
import unittest
from pathlib import Path

class RTMSourceAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        file=Path(__file__).resolve().parents[2]/"tools"/"audit_rtm_sources.py"
        spec=importlib.util.spec_from_file_location("audit_rtm_sources",file)
        module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        cls.audit=staticmethod(module.audit)

    def test_every_candidate_is_counted_without_auto_acceptance(self):
        summary=self.audit()
        self.assertEqual(summary["total_candidates"],5071)
        self.assertEqual(summary["unique_ids"],5071)
        self.assertEqual(sum(summary["source_audit_counts"].values()),5071)
        self.assertEqual(summary["semantically_accepted_by_this_tool"],0)
        self.assertFalse(summary["all_source_locations_verified"])
