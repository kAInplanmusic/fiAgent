import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class ReleaseIntegrityTests(unittest.TestCase):
    def test_manifest_matches_tree_and_excludes_bytecode(self):
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        proc = subprocess.run([sys.executable, str(ROOT / "tools" / "verify_release.py")], cwd=ROOT, env=env, text=True, capture_output=True, timeout=10)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("PASS:", proc.stdout)

    def test_manifest_has_expected_release_identity(self):
        manifest = json.loads((ROOT / "MANIFEST.json").read_text())
        self.assertEqual(manifest["version"], "1.2.18")
        self.assertEqual(manifest["step"], 33)
        self.assertEqual(manifest["execution_mode"], "simulated_only")
        self.assertIn(f"Version `{manifest['version']}`", (ROOT / "README.md").read_text())
