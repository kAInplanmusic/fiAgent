"""Explicit release-maintainer command; never run this as CI verification."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
manifest = json.loads((root / 'MANIFEST.json').read_text())
paths = sorted(p for p in root.rglob('*') if p.is_file()
               and p.name != 'MANIFEST.json' and '__pycache__' not in p.parts
               and '.pytest_cache' not in p.parts and p.suffix not in {'.pyc', '.pyo'})
manifest.update(version='1.2.19', step=34, release_name='PRAIN_Phase1_Prototype_1.2.19',
                tests='See docs/STEP34_RUNTIME_HARDENING.md for fresh results and open gates.',
                files=[p.relative_to(root).as_posix() for p in paths],
                sha256={p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
(root / 'MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n')
