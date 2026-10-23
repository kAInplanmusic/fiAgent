#!/usr/bin/env python3
"""Verify a PRAIN release tree against its manifest without third-party packages."""
from __future__ import annotations
import json
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "MANIFEST.json"

def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    expected = set(manifest.get("files", []))
    actual = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*") if p.is_file() and p.name != "MANIFEST.json" and "__pycache__" not in p.parts and p.suffix not in {".pyc", ".pyo"}}
    missing = sorted(expected - actual)
    untracked = sorted(actual - expected)
    errors = []
    hashes = manifest.get('sha256', {})
    if set(hashes) != expected:
        errors.append('hash inventory does not match file inventory')
    for name in sorted(expected & actual):
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != hashes.get(name):
            errors.append('hash mismatch: ' + name)
    if missing: errors.append("missing files: " + ", ".join(missing))
    if untracked: errors.append("untracked files: " + ", ".join(untracked))
    if errors:
        print("FAIL")
        for error in errors: print("-", error)
        return 1
    print(f"PASS: {len(expected)} manifest files; exact inventory and SHA256 hashes verified")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
