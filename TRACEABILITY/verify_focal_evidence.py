"""Audit the 56 open and 12 claimed roadmap records without granting approval."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRACE = ROOT / 'TRACEABILITY'

def audit():
    with (TRACE / 'IMPLEMENTATION_EVIDENCE_20261025/requirement_evidence.jsonl').open(encoding='utf-8') as stream:
        records = [json.loads(next(stream)) for _ in range(69)]
    with (TRACE / 'RTM_69_FINAL_REFERENCE_RESOLUTION.csv').open(encoding='utf-8', newline='') as stream:
        resolutions = {r['requirement_id']: r for r in csv.DictReader(stream)}
    cache, rows = {}, []
    for index, row in enumerate(records, 1):
        uid = f'RTM-{index:05d}'
        if row.get('requirement_id') != uid or uid not in resolutions:
            raise ValueError('focal_inventory_mismatch:' + uid)
        mapping = resolutions[uid]
        source = (ROOT / mapping['resolved_source']).resolve()
        if not source.is_relative_to(ROOT) or not source.is_file():
            raise ValueError('invalid_source:' + uid)
        lines = source.read_text(encoding='utf-8').splitlines()
        number = int(mapping['resolved_line'])
        source_ok = 1 <= number <= len(lines) and hashlib.sha256(lines[number-1].strip().encode()).hexdigest() == mapping['source_line_sha256'] and lines[number-1].strip() == row['text'].strip()
        bad = []
        for kind in ('implementation_anchors', 'test_anchors'):
            for ref in row.get(kind, []):
                path = ref['path']; resolved = (ROOT / path).resolve()
                if not resolved.is_relative_to(ROOT) or not resolved.is_file():
                    bad.append({'kind': kind, 'path': path, 'reason': 'missing_or_outside'})
                    continue
                if path not in cache: cache[path] = hashlib.sha256(resolved.read_bytes()).hexdigest()
                if cache[path] != ref.get('sha256'):
                    bad.append({'kind': kind, 'path': path, 'reason': 'stale_sha256'})
        category = 'historical_information' if index == 69 else ('open_roadmap' if row['text'].startswith('- [ ]') else 'claimed_complete')
        rows.append({'requirement_id': uid, 'category': category, 'gate': row.get('gate'),
                     'source_exact': source_ok, 'stale_or_missing_anchors': bad,
                     'behavioral_test_evidence': row.get('behavioral_test_evidence'),
                     'independent_signoff': row.get('independent_signoff'),
                     'implementation_acceptance': row.get('implementation_acceptance'),
                     'production_acceptance': row.get('production_acceptance')})
    counts = Counter(r['category'] for r in rows)
    if counts != {'open_roadmap': 56, 'claimed_complete': 12, 'historical_information': 1}:
        raise ValueError('unexpected_roadmap_distribution')
    return {'counts': dict(counts), 'source_errors': sum(not r['source_exact'] for r in rows),
            'rows_with_stale_or_missing_anchors': sum(bool(r['stale_or_missing_anchors']) for r in rows),
            'behavioral_evidence_not_imported': sum(r['behavioral_test_evidence'] == 'NOT_IMPORTED' for r in rows[:68]),
            'independent_signoff_not_imported': sum(r['independent_signoff'] == 'NOT_IMPORTED' for r in rows[:68]),
            'production_accepted': False, 'scope': 'Reference and hash inventory only; no semantic, behavioral or independent approval.',
            'rows': rows}

if __name__ == '__main__':
    result = audit()
    output = TRACE / 'B01_FOCAL_AUDIT_20261027.json'
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k != 'rows'}, indent=2))
    raise SystemExit(bool(result['source_errors'] or result['rows_with_stale_or_missing_anchors']))
