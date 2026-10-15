#!/usr/bin/env python3
"""Publish the locally signed APK only after CI passes for the exact clean commit."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
REPO='fuloplevente1998/WearOS-Szamlap'
OUT=ROOT/'dist/verify'

def run(*args):
    return subprocess.check_output(args,cwd=ROOT,text=True).strip()

assert not run('git','status','--porcelain'), 'Commit all source changes before publishing'
assert run('git','branch','--show-current')=='main', 'Publish from main'
head=run('git','rev-parse','HEAD')
remote=run('git','ls-remote','origin','refs/heads/main').split()[0]
assert head==remote, 'Local commit must be the current remote main'
report=json.loads((OUT/'report.json').read_text())
assert report['commit']==head and all(report['checks'].values())
assert report['updateCompatibleWithExistingWatch7'], 'Use the retained local test key; CI snapshot keys cannot publish upgrade APKs'
checks=json.loads(run('gh','api',f'repos/{REPO}/commits/{head}/check-runs','--paginate'))['check_runs']
matching=[c for c in checks if c['name']=='Release gate' and c['app']['slug']=='github-actions']
assert matching and max(matching,key=lambda c:c['id'])['conclusion']=='success', 'Release gate must succeed for this exact commit'
apk=OUT/report['apk']
assert hashlib.sha256(apk.read_bytes()).hexdigest()==report['sha256']
version=report['version'];assert version.endswith('-test')
tag='v'+version
# Refuse replacement: changing source or assets requires a new version/tag.
existing=subprocess.run(['gh','release','view',tag,'--repo',REPO,'--json','url'],cwd=ROOT,capture_output=True,text=True)
assert existing.returncode!=0, 'Release already exists; bump version instead of replacing it'
run('gh','release','create',tag,str(apk),str(OUT/(apk.name+'.sha256')),str(OUT/'report.json'),
    '--repo',REPO,'--target',head,'--prerelease','--latest=false',
    '--title',f'Spartan Night {version} · Watch7 test','--notes-file',str(OUT/'release-notes.md'))
print(run('gh','release','view',tag,'--repo',REPO,'--json','url','--jq','.url'))
