import importlib.util
import unittest
from pathlib import Path
class RTMWorkpackageTests(unittest.TestCase):
    def test_all_ids_and_no_unearned_acceptance(self):
        p=Path(__file__).resolve().parents[2]/"tools"/"build_rtm_workpackages.py"
        spec=importlib.util.spec_from_file_location("build_rtm_workpackages",p)
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        result=m.run()
        self.assertEqual(result["total"],5071)
        self.assertEqual(result["pending_acceptance"],5071)
        self.assertEqual(result["fully_accepted"],0)
        self.assertEqual(sum(result["workstreams"].values()),5071)
