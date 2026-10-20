#!/usr/bin/env python3
"""Verify package file inventory, reports and optionally the final ZIP hash/CRC."""
from pathlib import Path, PurePosixPath
import argparse, hashlib, json, sys, zipfile
ROOT = Path(__file__).resolve().parents[1]
CHECKS, ERRORS = [], []
def ck(name, condition, detail=''):
    CHECKS.append({'name': name, 'status': 'PASS' if condition else 'FAIL', 'detail': str(detail)})
    if not condition: ERRORS.append(name + (': ' + str(detail) if detail else ''))
def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--directory', type=Path, default=ROOT, help='unpacked package directory')
    ap.add_argument('--archive', type=Path, help='optional final ZIP archive to verify')
    ap.add_argument('--integrity', type=Path, help='external integrity JSON for --archive')
    args = ap.parse_args()
    root = args.directory.resolve()
    try:
        manifest = json.loads((root/'MANIFEST.json').read_text(encoding='utf-8'))
        listed = manifest.get('files', [])
    except Exception as e:
        ck('manifest_parse', False, e)
        manifest, listed = {}, []
    paths = [x.get('path') for x in listed]
    ck('manifest_paths_unique', len(paths) == len(set(paths)) and None not in paths)
    for item in listed:
        rel = item.get('path', '')
        pp = PurePosixPath(rel)
        safe = bool(rel) and not pp.is_absolute() and '..' not in pp.parts
        ck(f'manifest_path_safe:{rel}', safe)
        p = root.joinpath(*pp.parts)
        ck(f'manifest_file_exists:{rel}', safe and p.is_file())
        if safe and p.is_file():
            ck(f'manifest_size_matches:{rel}', p.stat().st_size == item.get('bytes'), f'actual={p.stat().st_size}; recorded={item.get("bytes")}')
            ck(f'manifest_sha256_matches:{rel}', sha(p) == item.get('sha256'), f'actual={sha(p)}; recorded={item.get("sha256")}')
    actual = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and p.name != 'MANIFEST.json' and '__pycache__' not in p.parts}
    ck('manifest_inventory_exact', actual == set(paths), f'unlisted={sorted(actual-set(paths))}; missing={sorted(set(paths)-actual)}')

    try:
        integrity = json.loads((root/'INTEGRITY.json').read_text(encoding='utf-8'))
        validation = json.loads((root/'audit/validation_report.json').read_text(encoding='utf-8'))
        deep = json.loads((root/'audit/deep_conformance_report.json').read_text(encoding='utf-8'))
        semantic = json.loads((root/'audit/semantic_consistency_report.json').read_text(encoding='utf-8'))
        state_machine = json.loads((root/'audit/state_machine_conformance_report.json').read_text(encoding='utf-8'))
        schema_state_machine = json.loads((root/'audit/schema_state_machine_conformance_report.json').read_text(encoding='utf-8'))
        gate = json.loads((root/'phase0_gate_status.json').read_text(encoding='utf-8'))
        ck('integrity_validation_matches', integrity.get('validation_status') == validation.get('status') and integrity.get('validation_check_count') == validation.get('check_count') and integrity.get('validation_passed') == validation.get('passed') and integrity.get('validation_failed') == validation.get('failed'))
        ck('integrity_deep_matches', integrity.get('deep_conformance_check_count') == deep.get('check_count') and integrity.get('deep_conformance_passed') == deep.get('passed'))
        ck('integrity_semantic_matches', integrity.get('semantic_consistency_check_count') == semantic.get('check_count') and integrity.get('semantic_consistency_passed') == semantic.get('passed'))
        ck('gate_semantic_matches', gate.get('semantic_consistency_checks') == semantic.get('check_count') and gate.get('semantic_consistency_passed') == semantic.get('passed'))
        ck('integrity_state_machine_matches', integrity.get('state_machine_check_count') == state_machine.get('check_count') and integrity.get('state_machine_passed') == state_machine.get('passed') and integrity.get('state_machine_failed') == state_machine.get('failed'))
        ck('schema_state_machine_report_pass', schema_state_machine.get('status') == 'PASS' and schema_state_machine.get('failed') == 0)
        ck('integrity_schema_state_machine_matches', integrity.get('schema_state_machine_status') == schema_state_machine.get('status') and integrity.get('schema_state_machine_check_count') == schema_state_machine.get('check_count') and integrity.get('schema_state_machine_passed') == schema_state_machine.get('passed') and integrity.get('schema_state_machine_failed') == schema_state_machine.get('failed'))
        ck('gate_state_machine_matches', gate.get('state_machine_checks') == state_machine.get('check_count') and gate.get('state_machine_passed') == state_machine.get('passed'))
        ck('all_reports_pass', all(r.get('status') == 'PASS' and r.get('failed') == 0 for r in [validation, deep, semantic, state_machine, schema_state_machine]))
        # The v0.99.4 gate/integrity fields are preserved as historical candidate metadata.
        # The authoritative release decision is a separate, auditable release-level record.
        release = json.loads((root/'release_status.json').read_text(encoding='utf-8'))
        attestation = (root/'RELEASE_ATTESTATION.md').read_text(encoding='utf-8')
        phase1_plan = (root/'PHASE1_START_PLAN.md').read_text(encoding='utf-8')
        ck('historical_candidate_gate_preserved', gate.get('release_approval_recorded') is False and gate.get('phase1_authorized') is False and integrity.get('release_approval_recorded') is False and integrity.get('phase1_authorized') is False)
        ck('release_phase0_closed', release.get('release_status') == 'PHASE0_CLOSED_PHASE1_AUTHORIZED' and release.get('phase0', {}).get('approval_recorded') is True)
        ck('release_phase1_authorized', release.get('phase1', {}).get('authorization_recorded') is True and release.get('phase1', {}).get('status') == 'AUTHORIZED_TO_START')
        ck('phase1_scope_is_bounded', release.get('phase1', {}).get('production_deployment_authorized') is False and release.get('phase1', {}).get('external_side_effects_authorized') is False and 'Explicit exclusions' in attestation and 'Deferred' in phase1_plan)
    except Exception as e:
        ck('report_cross_validation', False, e)

    if args.archive:
        zpath = args.archive.resolve()
        ck('archive_exists', zpath.is_file())
        if zpath.is_file():
            try:
                with zipfile.ZipFile(zpath) as z:
                    bad = z.testzip()
                    ck('archive_crc_test', bad is None, bad or '')
                    members = [n for n in z.namelist() if not n.endswith('/')]
                    stripped = []
                    for n in members:
                        parts = PurePosixPath(n).parts
                        stripped.append(PurePosixPath(*parts[1:]).as_posix() if len(parts) > 1 else parts[0])
                    expected = actual | {'MANIFEST.json'}
                    ck('archive_file_inventory_matches_directory', set(stripped) == expected, f'extra={sorted(set(stripped)-expected)}; missing={sorted(expected-set(stripped))}')
                if args.integrity:
                    outer = json.loads(args.integrity.read_text(encoding='utf-8'))
                    ck('outer_integrity_sha256', sha(zpath) == outer.get('zip_sha256'), f'actual={sha(zpath)}; expected={outer.get("zip_sha256")}')
                    ck('outer_integrity_size', zpath.stat().st_size == outer.get('zip_bytes'), f'actual={zpath.stat().st_size}; expected={outer.get("zip_bytes")}')
                    ck('outer_manifest_hash', sha(root/'MANIFEST.json') == outer.get('manifest_sha256'))
            except Exception as e:
                ck('archive_verify', False, e)
        elif args.integrity:
            ck('outer_integrity_requires_archive', False, '--integrity requires --archive')

    report = {'package': manifest.get('package', 'unknown'), 'version': manifest.get('version'), 'status': 'PASS' if not ERRORS else 'FAIL', 'check_count': len(CHECKS), 'passed': sum(x['status']=='PASS' for x in CHECKS), 'failed': sum(x['status']=='FAIL' for x in CHECKS), 'errors': ERRORS, 'checks': CHECKS, 'scope_limit': 'integrity and specification-artifact checks only; not runtime/security/legal certification'}
    print(json.dumps({k: report[k] for k in ['status','check_count','passed','failed','errors']}, ensure_ascii=False, indent=2))
    return 0 if not ERRORS else 1
if __name__ == '__main__':
    sys.exit(main())
