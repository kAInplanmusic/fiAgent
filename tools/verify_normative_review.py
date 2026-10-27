"""Validate full historical review inventory and referenced source integrity.

This verifies review artifacts, never implementation acceptance or human signoff.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / 'TRACEABILITY/NORMATIVE_REVIEW_20261025'


def main():
    import runpy
    runpy.run_path(str(REVIEW / 'restore_matrices.py'))['restore']()
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    originals = {r['requirement_id']: r for r in map(json.loads,
        (ROOT / 'TRACEABILITY/IMPLEMENTATION_EVIDENCE_20261025/requirement_evidence.jsonl').read_text().splitlines())}
    expected = {f'RTM-{i:05d}' for i in range(70, 5072)}
    records, errors, seen, cache = [], [], set(), {}
    for path in sorted(REVIEW.glob('part_*.jsonl')):
        for line in path.read_text().splitlines():
            row = json.loads(line)
            uid = row.get('requirement_id')
            if uid in seen:
                errors.append(f'{uid}:duplicate_review')
            seen.add(uid)
            original = originals.get(uid)
            if not original or row.get('text') != original['text']:
                errors.append(f'{uid}:source_text_mismatch')
            if row.get('disposition') not in {'RETAIN', 'EXTEND', 'SUPERSEDE', 'NON_NORMATIVE', 'UNRESOLVED'}:
                errors.append(f'{uid}:invalid_disposition')
            for field in ('rationale', 'implementation_status', 'missing_proof'):
                if not row.get(field):
                    errors.append(f'{uid}:{field}_missing')
            if row.get('production_acceptance') is not False:
                errors.append(f'{uid}:unexpected_production_acceptance')
            reference = row.get('canonical_reference')
            references = reference if isinstance(reference, list) else [reference]
            for ref in references:
                if not isinstance(ref, dict) or not ref.get('archive') or not ref.get('member'):
                    continue
                archive = ref['archive']
                if archive not in cache:
                    data = (ROOT / archive).read_bytes()
                    cache[archive] = (hashlib.sha256(data).hexdigest(), zipfile.ZipFile(ROOT / archive))
                digest, package = cache[archive]
                if ref.get('archive_sha256') and ref['archive_sha256'] != digest:
                    errors.append(f'{uid}:canonical_archive_hash')
                try:
                    data = package.read(ref['member'])
                    if ref.get('sha256') and ref['sha256'] != hashlib.sha256(data).hexdigest():
                        errors.append(f'{uid}:canonical_member_hash')
                    if type(ref.get('line')) is int and not 1 <= ref['line'] <= len(data.decode().splitlines()):
                        errors.append(f'{uid}:canonical_line_range')
                except (KeyError, UnicodeError):
                    errors.append(f'{uid}:canonical_member_invalid')
            records.append(row)
    errors += [f'{uid}:missing' for uid in sorted(expected - seen)]
    errors += [f'{uid}:unexpected' for uid in sorted(seen - expected)]
    report = {'historical_candidates': len(expected), 'reviewed_rows': len(records),
              'unique_ids': len(seen), 'dispositions': dict(Counter(r.get('disposition') for r in records)),
              'implementation_statuses': dict(Counter(r.get('implementation_status') for r in records)),
              'errors': errors, 'artifact_integrity_passed': not errors,
              'production_accepted': False,
              'scope': 'Review inventory and explicit source bindings only; semantic judgments require independent review and retained requirements require implementation evidence.'}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    for _, package in cache.values():
        package.close()
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
