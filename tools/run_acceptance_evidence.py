"""Capture individual unittest results and immutable source hashes; no release approval."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import time
import unittest


class RecordedResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.records = []
        self.started = {}

    def startTest(self, test):
        self.started[test.id()] = time.perf_counter()
        super().startTest(test)

    def record(self, test, status, detail=None):
        self.records.append({"test": test.id(), "status": status,
                             "seconds": time.perf_counter() - self.started.get(test.id(), time.perf_counter()),
                             "detail": detail})

    def addSuccess(self, test):
        super().addSuccess(test)
        self.record(test, "PASS")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.record(test, "FAIL", self._exc_info_to_string(err, test))

    def addError(self, test, err):
        super().addError(test, err)
        self.record(test, "ERROR", self._exc_info_to_string(err, test))

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.record(test, "SKIP", reason)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    output = Path(args.out).resolve()
    output.mkdir(parents=True, exist_ok=True)
    files = [p for p in root.rglob("*") if p.is_file() and not any(
        part in {".git", "__pycache__", ".venv", "evidence"} for part in p.relative_to(root).parts)]
    hashes = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}
    sys.path.insert(0, str(root / "prototype"))
    os.chdir(root / "prototype")
    suite = unittest.defaultTestLoader.discover("tests")
    start = time.perf_counter()
    with (output / "tests.log").open("w") as stream:
        result = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=RecordedResult).run(suite)
    document = {"schema_version": 1, "python": sys.version, "platform": platform.platform(),
                "source_sha256": hashes,
                "source_tree_digest": hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest(),
                "seconds": time.perf_counter() - start, "tests_run": result.testsRun,
                "successful": result.wasSuccessful(), "failures": len(result.failures),
                "errors": len(result.errors), "skipped": len(result.skipped),
                "results": result.records, "production_acceptance": False,
                "scope": "Executed suite only; passing tests do not prove all normative requirements or two-host operation."}
    (output / "results.json").write_text(json.dumps(document, indent=2) + "\n")
    print(json.dumps({k: document[k] for k in ("tests_run", "successful", "failures", "errors", "skipped", "source_tree_digest")}))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
