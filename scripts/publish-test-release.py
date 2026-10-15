#!/usr/bin/env python3
"""Publish the locally signed APK only after CI passes for the exact clean commit."""
import hashlib
import argparse
import json
import os
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]
REPO='fuloplevente1998/WearOS-Szamlap'
parser=argparse.ArgumentParser()
parser.add_argument('--from-staged',type=Path)
args=parser.parse_args()
OUT=args.from_staged.resolve() if args.from_staged else ROOT/'dist/verify'

def run(*args):
    return subprocess.check_output(args,cwd=ROOT,text=True).strip()

if args.from_staged:
    assert os.environ.get('GITHUB_REF')=='refs/heads/main'
    assert os.environ.get('GITHUB_EVENT_NAME')=='workflow_dispatch'
    assert not run('git','diff','--name-only','HEAD'), 'Tracked source must match the verified commit'
else:
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
assert apk.parent==OUT and apk.name==f'SpartanNight-{report["version"]}.apk'
assert hashlib.sha256(apk.read_bytes()).hexdigest()==report['sha256']
version=report['version'];assert re.fullmatch(r'\d+\.\d+\.\d+-test',version)
tag='v'+version
# Refuse replacement: changing source or assets requires a new version/tag.
existing=subprocess.run(['gh','release','view',tag,'--repo',REPO,'--json','url'],cwd=ROOT,capture_output=True,text=True)
assert existing.returncode!=0, 'Release already exists; bump version instead of replacing it'
if args.from_staged:
    # The runner's native token can upload release assets; the cloud Git proxy
    # does not provide credentials on uploads.github.com. No signing key moves.
    sdk=Path(os.environ.get('ANDROID_HOME') or os.environ['ANDROID_SDK_ROOT'])/'build-tools/36.0.0'
    signature=run(str(sdk/'apksigner'),'verify','--print-certs',str(apk))
    expected='4e014742bb0b3aee16dcb2cb6fb97cf91a784233e84bf230429ad5dd83bd8f84'
    assert re.search(r'certificate SHA-256 digest: (\w+)',signature)[1]==expected
    run('python3','scripts/check-package.py',str(apk))
    badging=run(str(sdk/'aapt2'),'dump','badging',str(apk))
    assert f"versionCode='{report['versionCode']}' versionName='{version}'" in badging
    run(str(sdk/'zipalign'),'-c','-P','16','4',str(apk))
    run('gh','release','create',tag,str(apk),str(OUT/(apk.name+'.sha256')),str(OUT/'report.json'),
        '--repo',REPO,'--target',head,'--prerelease','--latest=false',
        '--title',f'Spartan Night {version} · Watch7 test','--notes-file',str(OUT/'release-notes.md'))
    print(run('gh','release','view',tag,'--repo',REPO,'--json','url','--jq','.url'))
else:
    # Stage only public artifacts on a separate temporary branch, leaving main
    # and this worktree unchanged. The exact SHA is passed to the workflow.
    names=[apk.name,apk.name+'.sha256','report.json','release-notes.md']
    entries=[]
    for name in names:
        blob=run('git','hash-object','-w',str(OUT/name))
        entries.append(f'100644 blob {blob}\t{name}\n')
    tree=subprocess.check_output(['git','mktree'],input=''.join(sorted(entries)),cwd=ROOT,text=True).strip()
    staged=subprocess.check_output(['git','commit-tree',tree,'-m',f'Stage verified {version} test artifacts'],cwd=ROOT,text=True).strip()
    branch='codex/release-assets-'+version
    assert not run('git','ls-remote','origin','refs/heads/'+branch), 'An asset staging branch already exists; inspect it before retrying'
    run('git','push','origin',staged+':refs/heads/'+branch)
    run('gh','workflow','run','checks.yml','--repo',REPO,'--ref','main',
        '-f','publish_test_release=true','-f','asset_commit='+staged)
    print(json.dumps({'stagedCommit':staged,'temporaryBranch':branch,'sourceCommit':head,'workflowDispatched':True}))
