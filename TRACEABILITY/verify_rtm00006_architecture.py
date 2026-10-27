"""Scoped RTM-00006 documentation evidence; does not assert runtime acceptance."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {'P': ('Perception', 'Sinne'), 'R': ('Reason', 'Gehirn'),
            'A': ('Anima', 'Seele'), 'I': ('Intention', 'Wille'),
            'N': ('Nerve', 'Körper')}
ROADMAP_LINE = '- [x] Architektur und P/R/A/I/N-Verantwortlichkeiten dokumentiert.'

def validate(roadmap, master, ssot):
    errors = []
    if sum(line.strip() == ROADMAP_LINE for line in roadmap.splitlines()) != 2:
        errors.append('roadmap_literal_copy_count_changed')
    rows = re.findall(r'^\|\s*([PRAIN])\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|', ssot, re.M)
    if len(rows) != 5 or {k: (v.strip(), topic.strip()) for k, v, topic in rows} != EXPECTED:
        errors.append('ssot_mapping_missing_duplicate_or_changed')
    for letter, (name, _) in EXPECTED.items():
        if len(re.findall(r'^- \*\*' + letter + r' — ' + name + r':\*\*', master, re.M)) != 1:
            errors.append('master_responsibility_missing_or_duplicate:' + letter)
        if len(re.findall(r'^- \*\*' + letter + r' — ' + name + r' \(', ssot, re.M)) != 1:
            errors.append('ssot_responsibility_missing_or_duplicate:' + letter)
    return errors

def main():
    names = ['ROADMAP.md', 'MASTER_README.md', 'docs/ORGANIC_AGENT_ARCHITECTURE_SSOT.md']
    texts = [(ROOT / name).read_text(encoding='utf-8') for name in names]
    errors = validate(*texts)
    bad_mapping = texts[2].replace('| P | Perception | Sinne |', '| P | Perception | Wille |', 1)
    missing = texts[1].replace('- **N — Nerve:**', '- **N — missing:**', 1)
    negative_cases = {
        'changed_theme_rejected': bool(validate(texts[0], texts[1], bad_mapping)),
        'missing_responsibility_rejected': bool(validate(texts[0], missing, texts[2])),
    }
    result = {'requirement_id': 'RTM-00006', 'source_text': ROADMAP_LINE,
              'documentation_scope_passed': not errors and all(negative_cases.values()),
              'errors': errors, 'negative_cases': negative_cases,
              'sha256': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in names},
              'runtime_implementation_accepted': False, 'independent_signoff': False,
              'production_accepted': False,
              'scope': 'Exact current P/R/A/I/N labels and documented responsibility headers; no semantic or implementation completeness claim.'}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['documentation_scope_passed'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
