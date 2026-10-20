#!/usr/bin/env python3
"""Refresh candidate report summary, internal integrity, and checksummed file manifest."""
from pathlib import Path
import hashlib, json, sys
ROOT = Path(__file__).resolve().parents[1]
def load(name): return json.loads((ROOT/name).read_text(encoding='utf-8'))
def save(name, obj): (ROOT/name).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
version = '0.99.4'
validation = load('audit/validation_report.json')
deep = load('audit/deep_conformance_report.json')
semantic = load('audit/semantic_consistency_report.json')
state_machine = load('audit/state_machine_conformance_report.json')
schema_state_machine = load('audit/schema_state_machine_conformance_report.json')
gate = load('phase0_gate_status.json')
if any(x.get('status') != 'PASS' or x.get('failed') != 0 for x in [validation, deep, semantic, state_machine, schema_state_machine]):
    print('Refusing to finalize metadata: at least one report is not PASS.', file=sys.stderr)
    sys.exit(1)
gate.update({
    'candidate_version': version,
    'main_validator_checks': validation['check_count'],
    'main_validator_passed': validation['passed'],
    'main_validator_failed': validation['failed'],
    'deep_conformance_checks': deep['check_count'],
    'deep_conformance_passed': deep['passed'],
    'semantic_consistency_checks': semantic['check_count'],
    'semantic_consistency_passed': semantic['passed'],
    'state_machine_checks': state_machine['check_count'],
    'schema_state_machine_checks': schema_state_machine['check_count'],
    'schema_state_machine_passed': schema_state_machine['passed'],
    'schema_state_machine_failed': schema_state_machine['failed'],
    'state_machine_passed': state_machine['passed'],
    'state_machine_failed': state_machine['failed'],
    'runtime_invariants_requiring_future_conformance': semantic['runtime_invariant_count'],
    'non_runtime_boundary_invariants': semantic['non_runtime_boundary_invariant_count'],
    'state_machine_checks': state_machine['check_count'],
    'state_machine_passed': state_machine['passed'],
    'state_machine_failed': state_machine['failed'],
    'runtime_implementation_included': False,
    'phase1_authorized': False,
    'release_approval_recorded': False,
})
save('phase0_gate_status.json', gate)
integrity = load('INTEGRITY.json')
integrity.update({
    'package': 'PRAIN v0.99.3 Phase-0 Semantic Consistency Candidate',
    'validation_status': validation['status'],
    'validation_check_count': validation['check_count'],
    'validation_passed': validation['passed'],
    'validation_failed': validation['failed'],
    'deep_conformance_check_count': deep['check_count'],
    'deep_conformance_passed': deep['passed'],
    'semantic_consistency_status': semantic['status'],
    'semantic_consistency_check_count': semantic['check_count'],
    'semantic_consistency_passed': semantic['passed'],
    'state_machine_status': state_machine['status'],
    'state_machine_check_count': state_machine['check_count'],
    'schema_state_machine_status': schema_state_machine['status'],
    'schema_state_machine_check_count': schema_state_machine['check_count'],
    'schema_state_machine_passed': schema_state_machine['passed'],
    'schema_state_machine_failed': schema_state_machine['failed'],
    'state_machine_passed': state_machine['passed'],
    'state_machine_failed': state_machine['failed'],
    'runtime_invariant_count': semantic['runtime_invariant_count'],
    'non_runtime_boundary_invariant_count': semantic['non_runtime_boundary_invariant_count'],
    'state_machine_check_count': state_machine['check_count'],
    'state_machine_passed': state_machine['passed'],
    'state_machine_failed': state_machine['failed'],
    'runtime_implementation_included': False,
    'release_approval_recorded': False,
    'phase1_authorized': False,
    'scope_limit': 'specification-level offline checks only; not runtime/production/security certification',
})
save('INTEGRITY.json', integrity)
items=[]
for p in sorted(ROOT.rglob('*')):
    if not p.is_file() or p.name == 'MANIFEST.json' or '__pycache__' in p.parts:
        continue
    rel=p.relative_to(ROOT).as_posix()
    items.append({'path': rel, 'bytes': p.stat().st_size, 'sha256': sha(p)})
manifest={
    'package': 'PRAIN',
    'version': version,
    'artifact': 'Phase-0 Schema/State-Machine Conformance Closure Candidate',
    'created_at': '2026-10-20',
    'status': 'SPECIFICATION_COMPLETE_PENDING_FINAL_USER_RELEASE_APPROVAL',
    'runtime_implementation_included': False,
    'phase1_authorized': False,
    'release_approval_recorded': False,
    'canonical_schemas': 17,
    'historical_schemas_audited': 20,
    'workstreams': 7,
    'invariants': 30,
    'runtime_invariants_requiring_future_conformance': semantic['runtime_invariant_count'],
    'non_runtime_boundary_invariants': semantic['non_runtime_boundary_invariant_count'],
    'knowledge_base_item_dispositions': 114,
    'source_records_reviewed': 19,
    'claims_reviewed': 20,
    'migration_records': 16,
    'validation_summary': {
        'main': {'status': validation['status'], 'checks': validation['check_count'], 'passed': validation['passed'], 'failed': validation['failed']},
        'deep': {'status': deep['status'], 'checks': deep['check_count'], 'passed': deep['passed'], 'failed': deep['failed']},
        'semantic_consistency': {'status': semantic['status'], 'checks': semantic['check_count'], 'passed': semantic['passed'], 'failed': semantic['failed']},
        'state_machine_conformance': {'status': state_machine['status'], 'checks': state_machine['check_count'], 'passed': state_machine['passed'], 'failed': state_machine['failed']},
        'state_machine': {'status': state_machine['status'], 'checks': state_machine['check_count'], 'passed': state_machine['passed'], 'failed': state_machine['failed']},
    },
    'scope_limit': 'specification-only; no runtime/production/security certification',
    'manifest_excludes_itself': True,
    'listed_file_count': len(items),
    'archive_regular_file_count_including_manifest': len(items)+1,
    'files': items,
}
save('MANIFEST.json', manifest)
print(json.dumps({'version': version, 'listed_file_count': len(items), 'archive_regular_file_count_including_manifest': len(items)+1, 'main_checks': validation['check_count'], 'deep_checks': deep['check_count'], 'semantic_checks': semantic['check_count'], 'state_machine_checks': state_machine['check_count'], 'status': 'PASS'}, indent=2))
