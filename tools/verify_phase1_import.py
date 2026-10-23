"""Verify imported source snapshots using exact inventories and SHA256."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def inventory(directory):
    return {p.relative_to(directory).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(directory.rglob('*'))
            if p.is_file() and '__pycache__' not in p.parts
            and '.pytest_cache' not in p.parts and p.suffix not in {'.pyc', '.pyo'}}


def main():
    record = json.loads((ROOT / 'docs/phase1-import.json').read_text())
    errors = []
    for key in ('baseline', 'candidate'):
        entry = record[key]
        actual = inventory(ROOT / entry['path'])
        expected = entry['sha256']
        for name in sorted(set(actual) | set(expected)):
            if actual.get(name) != expected.get(name):
                errors.append(f'{key}: missing, extra or modified file: {name}')
    if errors:
        raise SystemExit('\n'.join(errors))
    print('PASS: exact baseline and candidate inventories and SHA256 hashes')


if __name__ == '__main__':
    main()
