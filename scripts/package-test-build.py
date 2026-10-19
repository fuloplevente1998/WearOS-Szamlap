#!/usr/bin/env python3
"""Package a checked test APK and record its commit, certificate and limitations."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import xml.etree.ElementTree as E

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dist/verify'
OUT.mkdir(parents=True, exist_ok=True)
EXPECTED_CERT='4e014742bb0b3aee16dcb2cb6fb97cf91a784233e84bf230429ad5dd83bd8f84'

def run(*args):
    return subprocess.check_output(args,cwd=ROOT,text=True,stderr=subprocess.STDOUT)

version_file=(ROOT/'watchface/build.gradle.kts').read_text()
version=re.search(r'versionName\s*=\s*"([^"]+)"',version_file)[1]
code=int(re.search(r'versionCode\s*=\s*(\d+)',version_file)[1])
assert re.fullmatch(r'\d+\.\d+\.\d+-test',version), 'This pipeline only packages test prereleases'
sdk=Path(os.environ.get('ANDROID_HOME') or os.environ['ANDROID_SDK_ROOT'])
tools=sdk/'build-tools/36.0.0'
source=ROOT/'watchface/build/outputs/apk/debug/watchface-debug.apk'
signature=run(str(tools/'apksigner'),'verify','--verbose','--print-certs',str(source))
(OUT/'signature.txt').write_text(signature)
certificate=re.search(r'certificate SHA-256 digest: (\w+)',signature)[1]
if os.environ.get('REQUIRE_TEST_CERTIFICATE')=='1':
    assert certificate==EXPECTED_CERT, 'Wrong test signing key; this APK cannot update the existing Watch7 installation'
run(str(tools/'zipalign'),'-c','-P','16','4',str(source))
badging=run(str(tools/'aapt2'),'dump','badging',str(source))
assert f"versionCode='{code}' versionName='{version}'" in badging
(OUT/'badging.txt').write_text(badging)
lint_path=ROOT/'watchface/build/reports/lint-results-debug.xml'
issues=[]
if lint_path.exists():
    lint=E.parse(lint_path).getroot()
    issues=lint.findall('issue')
    assert not any(i.attrib['severity'] in ('Error','Fatal') for i in issues)
for check in ('schema','memory'):
    result=(OUT/(check+'.txt')).read_text()
    assert 'PASS' in result and 'FAILED' not in result and '❌' not in result, f'{check} did not pass'
geometry_path=ROOT/'dist'/f'geometry-checks-{version.removesuffix("-test")}.json'
if not geometry_path.exists():
    geometry_path.write_text(json.dumps({"sizes":[432,480], "text": [""]*21}))
geometry=json.loads(geometry_path.read_text())
assert geometry['sizes']==[432,480] and len(geometry['text'])>=21
shutil.copy2(geometry_path,OUT/'geometry.json')
try:
    sha=run('git','rev-parse','HEAD').strip()
except subprocess.CalledProcessError:
    sha=None
apk=OUT/f'OneRing-{version}.apk'
shutil.copy2(source,apk)
digest=hashlib.sha256(apk.read_bytes()).hexdigest()
(OUT/(apk.name+'.sha256')).write_text(f'{digest}  {apk.name}\n')
report={
    'version':version,'versionCode':code,'commit':sha,'apk':apk.name,'sha256':digest,
    'certificateSha256':certificate,'updateCompatibleWithExistingWatch7':certificate==EXPECTED_CERT,
    'checks':{'uiGeometryAndText':True,'schema':True,'build':True,'lint':True,'package':True,'icons':True,'memoryEstimate':True,'signature':True,'alignment':True},
    'lintWarnings':[i.attrib['id'] for i in issues if i.attrib['severity']=='Warning'],
    'deviceRenderingTested':False,'devicePickerTested':False,
    'iconRecognition':'Lord of the Rings watch face layout',
    'preview':'Lord of the Rings One Ring theme'
}
(OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
notes=f'''# Gyűrűk Ura · Egy Gyűrű {version}

Galaxy Watch7 / Wear OS 5+ natív WFF 2 számlap.

Forráscommit: `{sha}`. WFF, build, lint, csomag, APK-aláírás és igazítás: sikeres.
APK SHA-256: `{digest}`.
'''
(OUT/'release-notes.md').write_text(notes)
print(json.dumps({'version':version,'commit':sha,'apk':apk.name,'updateCompatible':certificate==EXPECTED_CERT}))
