#!/usr/bin/env python3
"""Fetch Google's WFF tools with pinned, publisher-verified SHA-256 digests."""
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--output',type=Path,default=ROOT/'.tools/wff')
args=parser.parse_args()
args.output.mkdir(parents=True,exist_ok=True)
for name,spec in json.loads((ROOT/'design/validation-tools.json').read_text()).items():
    target=args.output/name
    if target.is_file() and hashlib.sha256(target.read_bytes()).hexdigest()==spec['sha256']:
        print('Verified cached tool:',name)
        continue
    temporary=target.with_suffix('.download')
    with urllib.request.urlopen(spec['url'],timeout=90) as source,temporary.open('wb') as dest:
        while chunk:=source.read(1024*1024):dest.write(chunk)
    assert hashlib.sha256(temporary.read_bytes()).hexdigest()==spec['sha256'], f'Checksum mismatch: {name}; refusing installation'
    temporary.replace(target)
    print('Downloaded and SHA-256 verified:',name)
