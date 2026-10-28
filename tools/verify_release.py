"""Authenticate the immutable core, SDK, models and public release metadata."""
from pathlib import Path
import hashlib
import json
import tomllib

ROOT = Path(__file__).resolve().parents[1]


def verify():
    compatibility = json.loads((ROOT/'compatibility.json').read_text())
    version = (ROOT/'VERSION').read_text().strip()
    package = tomllib.loads((ROOT/'pyproject.toml').read_text())
    if version != compatibility['release_version'] or version != package['project']['version']:
        raise ValueError('Release metadata versions differ')
    packaged = json.loads((ROOT/'src/paper_reconstruction_stage3_release/compatibility.json').read_text())
    if packaged != compatibility:
        raise ValueError('Installed compatibility metadata differs')
    inventory = json.loads((ROOT/'provenance/qualified_sources.json').read_text())
    for name, checksum in inventory['files'].items():
        path = ROOT/name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != checksum:
            raise ValueError('Qualified source/model differs: '+name)
    for folder in ('src/paper_reconstruction_stage3', 'contracts/stage3_to_stage4/v2/sdk/src/paper_reconstruction_contracts'):
        actual = {p.relative_to(ROOT).as_posix() for p in (ROOT/folder).rglob('*')
                  if p.is_file() and p.suffix in ('.py', '.json') and '__pycache__' not in p.parts}
        expected = {p for p in inventory['files'] if p.startswith(folder+'/')}
        if actual != expected:
            raise ValueError('Qualified source inventory differs: '+folder)
    print(json.dumps({'status': 'verified', 'release_version': version,
                      'qualified_files': len(inventory['files']), 'default_device': 'cpu',
                      'stage2': compatibility['upstream']['release_tag'],
                      'stage4': compatibility['downstream']['release_tag']}, indent=2))


if __name__ == '__main__':
    verify()
