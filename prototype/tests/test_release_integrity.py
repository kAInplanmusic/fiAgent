import json
import os
import subprocess
import sys
import unittest
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class ReleaseIntegrityTests(unittest.TestCase):
    def test_verifier_rejects_content_tampering(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / 'release'
            shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
            with (target / 'prain' / 'goal_registry.py').open('a') as stream:
                stream.write('\n# modified after release\n')
            proc = subprocess.run([sys.executable, str(target / 'tools/verify_release.py')],
                                  capture_output=True, text=True, timeout=10)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn('hash mismatch: prain/goal_registry.py', proc.stdout)

    def test_verifier_rejects_extra_file(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / 'release'
            shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
            (target / 'unexpected.txt').write_text('extra')
            proc = subprocess.run([sys.executable, str(target / 'tools/verify_release.py')],
                                  capture_output=True, text=True, timeout=10)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn('untracked files: unexpected.txt', proc.stdout)

    def test_manifest_matches_tree_and_excludes_bytecode(self):
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        proc = subprocess.run([sys.executable, str(ROOT / "tools" / "verify_release.py")], cwd=ROOT, env=env, text=True, capture_output=True, timeout=10)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("PASS:", proc.stdout)

    def test_manifest_has_expected_release_identity(self):
        manifest = json.loads((ROOT / "MANIFEST.json").read_text())
        from prain import __version__, PRAINRuntime
        self.assertEqual(manifest["version"], __version__)
        self.assertEqual(PRAINRuntime().snapshot()['version'], __version__)
        self.assertEqual(manifest["step"], 34)
        self.assertEqual(manifest["execution_mode"], "simulated_only")
        self.assertIn(f"Version `{manifest['version']}`", (ROOT / "README.md").read_text())
