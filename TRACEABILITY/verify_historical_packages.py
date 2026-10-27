"""Check the historical ZIP packages named by the supplied master archive.

RTM-00004: scoped integrity evidence, not a semantic or production approval.
"""
import argparse
import hashlib
import io
import json
import re
import zipfile
from pathlib import Path

INDEX = 'PRAIN_MASTER_INDEX.md'


def verify(archive):
    archive = Path(archive)
    data = archive.read_bytes()
    result = {'requirement_id': 'RTM-00004', 'master_archive_sha256': hashlib.sha256(data).hexdigest(),
              'packages': [], 'errors': [], 'scope': 'Packages named by the through-v0.6 master index; does not prove completeness of later releases or other historical sources.',
              'production_accepted': False, 'independent_signoff': False}
    errors = result['errors']
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as master:
            names = master.namelist()
            if len(names) != len(set(names)):
                errors.append('duplicate_master_entries')
            bad = master.testzip()
            if bad:
                errors.append('master_crc:' + bad)
            index = master.read(INDEX).decode('utf-8')
            expected = set(re.findall(r'`([^`\n]+\.zip)`', index, flags=re.I))
            actual = {n for n in names if n.lower().endswith('.zip')}
            if not expected:
                errors.append('no_indexed_packages')
            for name in sorted(expected - actual):
                errors.append('missing_indexed_package:' + name)
            for name in sorted(actual - expected):
                errors.append('unindexed_package:' + name)
            recorded = {}
            for line in index.splitlines():
                match = re.search(r'`([^`]+\.zip)`.*?SHA-256:\s*`([0-9a-f]{64})`', line, re.I)
                if match:
                    recorded[match.group(1)] = match.group(2).lower()
            for name in sorted(expected & actual):
                try:
                    payload = master.read(name)
                    digest = hashlib.sha256(payload).hexdigest()
                    if name in recorded and digest != recorded[name]:
                        errors.append('index_digest_mismatch:' + name)
                    with zipfile.ZipFile(io.BytesIO(payload)) as inner:
                        members = inner.namelist()
                        if len(members) != len(set(members)):
                            errors.append('duplicate_nested_entries:' + name)
                        bad_inner = inner.testzip()
                        if bad_inner:
                            errors.append('nested_crc:' + name + ':' + bad_inner)
                        # testzip reads all members and validates their CRC.
                        result['packages'].append({'name': name, 'sha256': digest,
                                                   'index_digest_verified': name in recorded,
                                                   'members': len(members), 'crc_valid': bad_inner is None})
                except (zipfile.BadZipFile, RuntimeError, OSError, ValueError) as exc:
                    errors.append('nested_unreadable:' + name + ':' + type(exc).__name__)
    except (zipfile.BadZipFile, KeyError, UnicodeError, RuntimeError, OSError, ValueError) as exc:
        errors.append('master_unreadable:' + type(exc).__name__)
    result['indexed_packages'] = len(expected) if 'expected' in locals() else 0
    result['passed_declared_scope'] = not errors
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('archive', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = verify(args.archive)
    text = json.dumps(result, indent=2, ensure_ascii=False) + '\n'
    if args.output:
        args.output.write_text(text, encoding='utf-8')
    print(text, end='')
    raise SystemExit(0 if result['passed_declared_scope'] else 1)
