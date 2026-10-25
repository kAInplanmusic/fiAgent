import importlib.util
import unittest
from pathlib import Path

class ArchivedRTMResolutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        src=Path(__file__).resolve().parents[2]/"tools"/"resolve_rtm_archives.py"
        spec=importlib.util.spec_from_file_location("resolve_rtm_archives",src)
        m=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        cls.module=m

    def test_archive_lines_account_for_all_candidates(self):
        r=self.module.run()
        self.assertEqual(r["total"],5071)
        self.assertEqual(sum(r["source_results"].values()),5071)
        self.assertEqual(r["source_results"]["EXACT_SOURCE_LINE"],5002)
        self.assertEqual(r["duplicate_text_candidates"],3703)
        self.assertEqual(r["accepted"],0)
        self.assertEqual(r["unreviewed"],5071)
