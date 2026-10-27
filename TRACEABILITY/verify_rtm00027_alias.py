"""Behavioral probe for RTM-00027, not an acceptance/signoff decision."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'prototype'))
from prain.evidence_ledger import EvidenceLedger
from prain.durable_components import DurableEvidenceLedger


def check(ledger, restart=None):
    value = {'nested': {'values': [1, {'v': 'original'}]}}
    entry = ledger.append('proof', 'rtm-00027', value)
    value['nested']['values'][1]['v'] = 'input-tampered'
    entry.payload['nested']['values'][1]['v'] = 'return-tampered'
    retrieved = ledger.entries()
    retrieved[0].payload['nested']['values'][1]['v'] = 'read-tampered'
    assert ledger.entries()[0].payload['nested']['values'][1]['v'] == 'original'
    assert ledger.verify()
    if restart:
        restored = restart()
        assert restored.entries()[0].payload['nested']['values'][1]['v'] == 'original'
        assert restored.verify()
    return True


def main():
    with tempfile.TemporaryDirectory() as directory:
        db = Path(directory) / 'evidence.sqlite'
        outcomes = {'in_memory': check(EvidenceLedger()),
                    'sqlite_restart': check(DurableEvidenceLedger(db), lambda: DurableEvidenceLedger(db))}
    files = ['prototype/prain/evidence_ledger.py', 'prototype/prain/durable_components.py',
             'TRACEABILITY/verify_rtm00027_alias.py']
    result = {'requirement_id': 'RTM-00027', 'source': 'ROADMAP.md',
              'requirement': 'Verifizieren, dass Hash-Chain-Kopien keine nachträgliche Mutierung durch Alias-Referenzen erlauben; Mutationstests ergänzen.',
              'outcomes': outcomes,
              'sha256': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in files},
              'scope': 'Post-append mutation of nested input, returned entry and retrieved entry; SQLite restart. Does not prove safe concurrent mutation during copy or protection from privileged direct DB access.',
              'production_accepted': False, 'independent_signoff': False}
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
