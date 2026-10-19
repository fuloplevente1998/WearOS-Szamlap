#!/usr/bin/env python3
"""Download Google's WFF tools and require pinned publisher SHA-256 digests."""
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT / 'design/validation-tools.json').read_text())
parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path, default=ROOT / '.tools/wff')
parser.add_argument('--only', action='append', choices=sorted(manifest), help='Install just this tool (repeatable). Default: both tools.')
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)

for name in args.only or manifest:
    spec = manifest[name]
    expected = spec['sha256'].lower()
    target = args.output / name
    if target.is_file():
        current = hashlib.sha256(target.read_bytes()).hexdigest()
        if current == expected:
            print('Verified cached tool:', name)
            continue
        print(f'Outdated or unexpected cached {name} (sha256={current}); downloading pinned version.')
    temporary = target.with_suffix('.download')
    try:
        digest = hashlib.sha256()
        with urllib.request.urlopen(spec['url'], timeout=90) as source, temporary.open('wb') as dest:
            while chunk := source.read(1024 * 1024):
                digest.update(chunk)
                dest.write(chunk)
        actual = digest.hexdigest()
        if actual != expected:
            raise SystemExit(
                f'SHA-256 mismatch for {name}; refusing installation.\n'
                f'  Expected from design/validation-tools.json: {expected}\n'
                f'  Actual downloaded SHA-256:             {actual}\n'
                f'  URL: {spec["url"]}\n'
                'The upstream google/watchface release tag is mutable. Confirm the new SHA-256 against Google GitHub release asset metadata before updating the manifest.'
            )
        temporary.replace(target)
        print('Downloaded and SHA-256 verified:', name)
    finally:
        temporary.unlink(missing_ok=True)
