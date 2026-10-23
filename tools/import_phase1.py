"""Reproduce the exact import from the user-supplied ZIP; refuses overwrites."""
import hashlib
import json
import sys
import zipfile
from pathlib import Path, PurePosixPath
from verify_phase1_import import ROOT, inventory


def main():
    source = Path(sys.argv[1])
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if digest != 'c803159e9e793f64dab2691dde11369593b633490f9f26cdb26422a383898bd5':
        raise SystemExit('Unexpected source ZIP hash')
    target = ROOT / 'archive/PRAIN_Phase1_Prototype_v1.2.18'
    if target.exists():
        raise SystemExit('Target already exists; refusing overwrite')
    with zipfile.ZipFile(source) as archive:
        if archive.testzip():
            raise SystemExit('ZIP CRC failure')
        members = [i for i in archive.infolist() if not i.is_dir()]
        names = [PurePosixPath(i.filename) for i in members]
        if len(set(names)) != len(names) or any(
            p.is_absolute() or '..' in p.parts or '\\' in str(p)
            or p.parts[0] != target.name for p in names
        ):
            raise SystemExit('Invalid archive paths')
        for info, name in zip(members, names):
            dest = target.joinpath(*name.parts[1:])
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(archive.read(info))
    baseline = ROOT / 'archive/PRAIN_v1.1.9_Phase1_Reference_Prototype'
    old, new = inventory(baseline), inventory(target)
    record = {
        'date': '2026-10-23', 'base_commit': 'fb955f18a8be321f19e7d750d0d9fecc2b8e5f6f',
        'source_zip_sha256': digest, 'status': 'PARTIAL_PASS',
        'baseline': {'path': str(baseline.relative_to(ROOT)), 'sha256': old},
        'candidate': {'path': str(target.relative_to(ROOT)), 'sha256': new},
        'comparison': {
            'added': sorted(new.keys() - old.keys()),
            'removed': sorted(old.keys() - new.keys()),
            'changed': sorted(p for p in old.keys() & new.keys() if old[p] != new[p]),
            'unchanged': sorted(p for p in old.keys() & new.keys() if old[p] == new[p])}}
    (ROOT / 'docs/phase1-import.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({k: len(v) for k, v in record['comparison'].items()}))


if __name__ == '__main__':
    main()
