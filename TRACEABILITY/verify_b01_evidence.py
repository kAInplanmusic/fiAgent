"""Check B01 inventory and code/test references without granting acceptance."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / 'TRACEABILITY/NORMATIVE_REVIEW_20261025'


def verify():
    import runpy
    runpy.run_path(str(REVIEW / 'restore_matrices.py'))['restore']()
    rows = []
    for part in 'abcd':
        with (REVIEW / f'part_{part}{"_reviews" if part == "a" else ""}.jsonl').open() as stream:
            rows.extend(json.loads(line) for line in stream)
    errors = []
    stale_rows = {}
    recorded_hashes = {}
    ids = [r.get('requirement_id') for r in rows]
    expected = {f'RTM-{i:05d}' for i in range(70, 5072)}
    if len(rows) != 5002 or set(ids) != expected or len(set(ids)) != len(ids):
        errors.append('historical_inventory_incomplete_or_duplicate')
    digest_cache = {}
    counts = Counter()
    for r in rows:
        uid = r.get('requirement_id', '?')
        status = r.get('implementation_status')
        disposition = r.get('disposition')
        counts[(disposition, status)] += 1
        if disposition not in {'RETAIN', 'EXTEND', 'SUPERSEDE', 'NON_NORMATIVE'}:
            errors.append(f'{uid}:unresolved_disposition')
        if status not in {'OPEN', 'PARTIAL', 'NA', 'NOT_APPLICABLE'}:
            errors.append(f'{uid}:unexpected_implementation_status')
        if disposition in {'RETAIN', 'EXTEND'} and status in {'NA', 'NOT_APPLICABLE'}:
            errors.append(f'{uid}:normative_obligation_marked_NA')
        if r.get('production_acceptance') is not False:
            errors.append(f'{uid}:production_acceptance_without_release')
        ev = r.get('implementation_evidence') or {}
        if isinstance(ev, dict) and (ev.get('state') == 'ACCEPTED' or ev.get('behavioral_execution_imported') is True):
            errors.append(f'{uid}:unsupported_behavioral_acceptance')
        references = []
        if isinstance(ev, list): references.extend(ev)
        elif isinstance(ev, dict):
            for kind in ('code_references', 'test_references'):
                references.extend(ev.get(kind) or [])
        for kind in ('partial_implementation_anchors', 'partial_test_anchors', 'related_implementation', 'related_tests'):
            references.extend(r.get(kind) or [])
        for ref in references:
            if not isinstance(ref, dict) or not ref.get('path') or not ref.get('sha256'):
                continue
            path = ref['path']
            target = (ROOT / path).resolve()
            if not target.is_relative_to(ROOT) or not target.is_file():
                errors.append(f'{uid}:missing_or_outside:{path}')
                continue
            if path not in digest_cache:
                digest_cache[path] = hashlib.sha256(target.read_bytes()).hexdigest()
            if ref['sha256'] != digest_cache[path]:
                stale_rows.setdefault(path, set()).add(uid)
                recorded_hashes.setdefault(path, set()).add(ref['sha256'])
    focal = [json.loads(line) for line in
             (ROOT / 'TRACEABILITY/IMPLEMENTATION_EVIDENCE_20261025/requirement_evidence.jsonl').read_text().splitlines()[:69]]
    if len(focal) != 69 or [r['requirement_id'] for r in focal] != [f'RTM-{i:05d}' for i in range(1, 70)]:
        errors.append('focal_69_inventory_incomplete')
    if stale_rows:
        errors.append('stale_implementation_reference_hashes')
    old_hashes = {}
    for path in stale_rows:
        baseline = subprocess.run(['git', 'show', 'HEAD:' + path], cwd=ROOT,
                                  capture_output=True, check=False)
        old_hashes[path] = hashlib.sha256(baseline.stdout).hexdigest() if baseline.returncode == 0 else None
    report = {
        'historical_rows': len(rows), 'focal_rows': len(focal),
        'disposition_counts': dict(Counter(r.get('disposition') for r in rows)),
        'implementation_status_counts': dict(Counter(r.get('implementation_status') for r in rows)),
        'disposition_by_status': {f'{a}/{b}': n for (a, b), n in sorted(counts.items())},
        'referenced_files_hashed': len(digest_cache), 'errors': errors,
        'stale_reference_paths': {p: {'affected_rows': len(ids), 'first_ids': sorted(ids)[:5],
                                      'current_sha256': digest_cache[p],
                                      'recorded_sha256': sorted(recorded_hashes[p]),
                                      'recorded_hash_matches_HEAD_baseline': old_hashes[p] in recorded_hashes[p]}
                                  for p, ids in sorted(stale_rows.items())},
        'inventory_and_reference_integrity_passed': not errors,
        'semantic_acceptance': False, 'implementation_acceptance': False,
        'production_acceptance': False,
        'limits': 'This checks row coverage and code/test byte identity. It does not inspect semantic correctness, execute per-requirement behavior, or independently sign off the 56 open and 12 claimed roadmap tasks.'
    }
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = verify()
    serialized = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized)
    print(serialized)
    raise SystemExit(bool(result['errors']))
