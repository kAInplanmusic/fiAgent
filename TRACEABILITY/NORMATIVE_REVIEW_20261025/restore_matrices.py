"""Restore the two compressed evidence matrices and verify exact bytes."""
import gzip
import hashlib
import os
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parent
EXPECTED = {
    'part_a_reviews.jsonl': 'e3d0e35ce3ab85ef495540a389f4708c1050fada2135eabbf9e408f83a5575b9',
    'part_c.jsonl': 'cf2144b7d21b5ed419cd4022ad0f09ec6a5c4b1082a6a63cd63d661d2126a04f',
}

def restore():
    for name, expected in EXPECTED.items():
        target = ROOT / name
        if target.exists():
            if hashlib.sha256(target.read_bytes()).hexdigest() != expected:
                raise ValueError(f'evidence_hash_mismatch: {name}')
            continue
        data = gzip.decompress((ROOT / (name + '.gz')).read_bytes())
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError(f'compressed_evidence_hash_mismatch: {name}')
        fd, temporary = tempfile.mkstemp(prefix='.restore-', dir=ROOT)
        try:
            with os.fdopen(fd, 'wb') as stream:
                stream.write(data)
            os.replace(temporary, target)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

if __name__ == '__main__':
    restore()
