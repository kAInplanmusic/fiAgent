#!/usr/bin/env python3
"""Cross-document specification consistency checks; never executes agent actions."""
from pathlib import Path
import json, re, sys
ROOT = Path(__file__).resolve().parents[1]
CHECKS, ERRORS = [], []
def ck(name, condition, detail=''):
    CHECKS.append({'name': name, 'status': 'PASS' if condition else 'FAIL', 'detail': str(detail)})
    if not condition:
        ERRORS.append(name + (': ' + str(detail) if detail else ''))
def load(rel):
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))

inv = load('tests/invariants.json')
cov = load('tests/invariant_coverage.json')
deep = load('audit/deep_conformance_report.json')
gate = load('phase0_gate_status.json')
integrity = load('INTEGRITY.json')
previous_semantic = load('audit/semantic_consistency_report.json')
kb = load('knowledge_base/PRAIN_Wissensdatenbank.v0.3.0.json')

# Invariant registry / coverage is a bijection, not merely a count.
inv_ids = [x.get('id') for x in inv]
cov_ids = [x.get('invariant_id') for x in cov]
inv_by_id = {x.get('id'): x for x in inv}
ck('invariant_registry_exactly_30', len(inv) == 30, f'actual={len(inv)}')
ck('invariant_registry_ids_unique', len(inv_ids) == len(set(inv_ids)) and None not in inv_ids)
ck('coverage_exactly_30', len(cov) == 30, f'actual={len(cov)}')
ck('coverage_ids_unique', len(cov_ids) == len(set(cov_ids)) and None not in cov_ids)
ck('coverage_is_bijection_to_registry', set(cov_ids) == set(inv_ids), f'uncovered={sorted(set(inv_ids)-set(cov_ids))}; orphaned={sorted(set(cov_ids)-set(inv_ids))}')
for c in cov:
    iid = c.get('invariant_id', '<missing>')
    src = inv_by_id.get(iid, {})
    ck(f'coverage_requirement_matches:{iid}', c.get('requirement') == src.get('requirement'), 'coverage wording must match invariant registry')
    tests = c.get('test_ids')
    ck(f'coverage_has_test_refs:{iid}', isinstance(tests, list) and bool(tests) and all(isinstance(t, str) and t for t in tests))
    ck(f'coverage_refs_unique:{iid}', isinstance(tests, list) and len(tests) == len(set(tests)))
    ck(f'coverage_phase0_scope:{iid}', c.get('phase0_status') == 'specification-coverage-only', f'actual={c.get("phase0_status")}')

# Every implementation/runtime invariant must explicitly require later implementation conformance.
non_runtime_boundary = {
    'INV-024': 'build-artifact',
    'INV-025': 'architecture-conformance',
    'INV-026': 'specification-claim',
    'INV-030': 'release-package-inventory',
}
for c in cov:
    iid = c.get('invariant_id', '<missing>')
    expected_boundary = non_runtime_boundary.get(iid, 'runtime-conformance')
    expected_runtime = iid not in non_runtime_boundary
    ck(f'coverage_boundary:{iid}', c.get('verification_boundary') == expected_boundary, f'expected={expected_boundary}; actual={c.get("verification_boundary")}')
    ck(f'coverage_runtime_flag:{iid}', c.get('runtime_conformance_still_required') is expected_runtime, f'expected={expected_runtime}; actual={c.get("runtime_conformance_still_required")}')

# Deep suite report integrity and invariant test reference resolution.
deep_checks = deep.get('checks', [])
deep_names = {x.get('name') for x in deep_checks}
ck('deep_report_status_pass', deep.get('status') == 'PASS')
ck('deep_report_count_matches_payload', deep.get('check_count') == len(deep_checks), f'reported={deep.get("check_count")}; actual={len(deep_checks)}')
ck('deep_report_all_checks_pass', all(x.get('status') == 'PASS' for x in deep_checks))
ck('coverage_references_resolve', all((t in deep_names) or any(t in n or n in t for n in deep_names) for c in cov for t in c.get('test_ids', [])), 'coverage contains a test id not resolvable to deep report names')
ck('deep_count_matches_gate', gate.get('deep_conformance_checks') == deep.get('check_count') and gate.get('deep_conformance_passed') == deep.get('passed'), f'gate={gate.get("deep_conformance_checks")}/{gate.get("deep_conformance_passed")}; report={deep.get("check_count")}/{deep.get("passed")}')

schema_sm = load('audit/schema_state_machine_conformance_report.json')
ck('schema_state_machine_report_pass', schema_sm.get('status') == 'PASS' and schema_sm.get('failed') == 0)
ck('schema_state_machine_report_count_matches', schema_sm.get('check_count') == len(schema_sm.get('checks', [])))

# Release state: phase-0 closure and phase-1 authorization are deliberately independent.
expected_status = 'SPECIFICATION_COMPLETE_PENDING_FINAL_USER_RELEASE_APPROVAL'
ck('gate_candidate_version', gate.get('candidate_version') == '0.99.4', gate.get('candidate_version'))
ck('gate_release_status_pending', gate.get('status') == expected_status, gate.get('status'))
ck('gate_does_not_authorize_phase1', gate.get('phase1_authorized') is False)
ck('gate_records_no_release_approval', gate.get('release_approval_recorded') is False)
ck('integrity_does_not_authorize_phase1', integrity.get('phase1_authorized') is False)
ck('integrity_records_no_release_approval', integrity.get('release_approval_recorded') is False)
ck('gate_semantic_count_fields_are_nonnegative', isinstance(gate.get('semantic_consistency_checks'), int) and gate.get('semantic_consistency_checks') >= 0)
ck('integrity_semantic_count_fields_are_nonnegative', isinstance(integrity.get('semantic_consistency_check_count'), int) and integrity.get('semantic_consistency_check_count') >= 0)
closure = (ROOT/'CLOSURE_CANDIDATE.md').read_text(encoding='utf-8')
attestation = (ROOT/'RELEASE_ATTESTATION_TEMPLATE.md').read_text(encoding='utf-8')
release_doc = (ROOT/'docs/13_RELEASE_AND_CHANGE_CONTROL.md').read_text(encoding='utf-8')
ck('closure_status_pending', expected_status in closure)
ck('attestation_phase0_decision_explicit', 'APPROVE_PHASE0_CLOSURE' in attestation and 'RETURN_FOR_REVISION' in attestation)
ck('attestation_phase1_is_separate', 'AUTHORIZE_PHASE1_IMPLEMENTATION' in attestation and 'Approval of section A alone does **not** authorize Phase-1 implementation.' in attestation)
ck('no_combined_phase0_phase1_option', 'APPROVE_PHASE0_CLOSURE_AND_AUTHORIZE_PHASE1' not in attestation)
ck('release_doc_states_separate_gates', 'These states must not be collapsed into a single `complete` flag.' in release_doc and 'separate explicit authorization' in release_doc)

# Candidate version/count strings in hand-authored release records must match executable reports.
readme = (ROOT/'README.md').read_text(encoding='utf-8')
completion = (ROOT/'docs/00_COMPLETION_REPORT.md').read_text(encoding='utf-8')
exit_doc = (ROOT/'docs/09_PHASE0_EXIT_CRITERIA.md').read_text(encoding='utf-8')
ck('candidate_version_in_closure', 'v0.99.4' in closure)
ck('candidate_version_in_readme', 'v0.99.4' in readme)
ck('candidate_version_in_completion_report', 'v0.99.4' in completion)
ck('candidate_version_in_attestation', 'v0.99.4' in attestation)
ck('current_deep_count_consistent', f"{deep.get('check_count')}/{deep.get('passed')}" in closure and f"{deep.get('check_count')}/{deep.get('passed')}" in readme and gate.get('deep_conformance_checks') == deep.get('check_count') and integrity.get('deep_conformance_check_count') == deep.get('check_count'))
state_machine = load('audit/state_machine_conformance_report.json')
ck('state_machine_report_pass', state_machine.get('status') == 'PASS' and state_machine.get('failed') == 0, f"status={state_machine.get('status')}; failed={state_machine.get('failed')}")
ck('state_machine_count_matches_gate', gate.get('state_machine_checks') == state_machine.get('check_count') and gate.get('state_machine_passed') == state_machine.get('passed'), f"gate={gate.get('state_machine_checks')}/{gate.get('state_machine_passed')}; report={state_machine.get('check_count')}/{state_machine.get('passed')}")
ck('all_seven_workstreams_documented', len(re.findall(r'^\|\s*[1-7]\s*\|', completion, re.M)) == 7)
ck('exit_gate_17_documented', 'G17 Final release authorization' in exit_doc)
ck('semantic_audit_document_exists', (ROOT/'docs/14_SEMANTIC_CONSISTENCY_AUDIT.md').is_file())
ck('release_bundle_verifier_exists', (ROOT/'tools/verify_release_bundle.py').is_file())
ck('metadata_refresh_tool_exists', (ROOT/'tools/refresh_release_metadata.py').is_file())

# P/R/A/I/N identity mapping matches the canonical KB.
expected_dimensions = {'P': 'Perception', 'R': 'Reason', 'A': 'Anima', 'I': 'Intention', 'N': 'Nerve'}
dims = kb.get('dimensions', [])
actual = {d.get('canonical_dimension'): d.get('canonical_name') for d in dims}
ck('prain_dimension_count_five', len(dims) == 5)
ck('prain_dimension_mapping_exact', actual == expected_dimensions, f'actual={actual}')
ck('prain_dimension_ids_unique', len({d.get('id') for d in dims}) == len(dims))
ck('prain_independent_of_hallerbans', 'not dependent on Hallerbans' in kb.get('project', {}).get('purpose', '') and 'one possible consumer' in kb.get('project', {}).get('purpose', ''))

report = {
    'package': 'PRAIN v0.99.4 Phase-0 Schema/State-Machine Conformance Candidate',
    'status': 'PASS' if not ERRORS else 'FAIL',
    'check_count': len(CHECKS),
    'passed': sum(x['status'] == 'PASS' for x in CHECKS),
    'failed': sum(x['status'] == 'FAIL' for x in CHECKS),
    'errors': ERRORS,
    'runtime_invariant_count': sum(1 for c in cov if c.get('runtime_conformance_still_required') is True),
    'non_runtime_boundary_invariant_count': sum(1 for c in cov if c.get('runtime_conformance_still_required') is False),
    'scope_limit': 'cross-document specification consistency only; not runtime execution, security certification, legal review, or external independent audit',
    'checks': CHECKS,
}
(ROOT/'audit/semantic_consistency_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: report[k] for k in ['status', 'check_count', 'passed', 'failed', 'runtime_invariant_count', 'non_runtime_boundary_invariant_count', 'errors']}, ensure_ascii=False, indent=2))
sys.exit(0 if not ERRORS else 1)
