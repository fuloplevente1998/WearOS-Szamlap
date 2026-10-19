#!/usr/bin/env python3
"""Check WFF resource references and the delivered APK for Lord of the Rings watch face."""
from pathlib import Path
import os
import re
import shutil
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as E
from clipping_checks import check_complication_crops

root=Path(__file__).resolve().parents[1]
res=root/'watchface/src/main/res'
wf=E.parse(res/'raw/watchface.xml').getroot()
strings={n.attrib['name'] for n in E.parse(res/'values/strings.xml').getroot()}
drawables={p.stem for p in (res/'drawable-nodpi').glob('*.png')}
configs=wf.find('UserConfigurations')
assert len(configs) <= 20, 'WFF 2 allows up to 20 configuration categories'
info=E.parse(res/'xml/watch_face_info.xml').getroot()
if len(configs) or wf.findall('Scene/ComplicationSlot'):
    editable=info.find('Editable')
    assert editable is not None and editable.attrib.get('value')=='true', 'Customizable watch faces must enable the Wear OS editor in watch_face_info.xml'
for c in configs:
    if c.tag!='BooleanConfiguration':
        assert c.attrib['defaultValue'] in {o.attrib['id'] for o in c}, c.attrib['id']
for n in wf.iter():
    for a in ['displayName','screenReaderText']:
        if a in n.attrib:assert n.attrib[a] in strings, (n.tag,a,n.attrib[a])
    for a in ['resource','icon']:
        if a in n.attrib and not n.attrib[a].startswith('['):
            assert n.attrib[a] in drawables, (n.tag,a,n.attrib[a])
slots=wf.findall('Scene/ComplicationSlot')
assert len(slots)==8
check_complication_crops(wf)
for s in slots:
    assert s.find('Complication[@type="EMPTY"]') is not None
    assert len(s.find('Complication[@type="EMPTY"]'))==0, 'None must hide the entire panel'
    types=set(s.attrib['supportedTypes'].split())
    assert types=={c.attrib['type'] for c in s.findall('Complication')}

assert configs.find('ColorConfiguration[@id="palette"]').attrib['defaultValue']=='mordor'
assert wf.attrib.get('clipShape')=='CIRCLE', 'The display clips transparent slot corners to the round screen'
for family in {n.attrib['family'] for n in wf.findall('.//Font')}:
    if family=='hud_bold':assert (res/'font/hud_bold.ttf').exists()

apk=Path(sys.argv[1]) if len(sys.argv)>1 else root/'watchface/build/outputs/apk/debug/watchface-debug.apk'
if apk.exists():
    with zipfile.ZipFile(apk) as z:
        names=z.namelist()
        assert not any(re.fullmatch(r'classes\d*\.dex',n) for n in names), 'WFF APK must be resource-only'
        assert 'res/raw/watchface.xml' in names
        assert 'res/xml/watch_face_info.xml' in names, 'Watch face editor metadata must be packaged'
        assert z.read('res/raw/watchface.xml')==(res/'raw/watchface.xml').read_bytes()
        packed={Path(n).stem for n in names if n.startswith('res/drawable')}
        assert drawables <= packed, f'Missing packaged resources: {drawables-packed}'
        assert 'res/font/hud_bold.ttf' in names, 'The tested font must be present on the watch'
    sdk=os.environ.get('ANDROID_HOME') or os.environ.get('ANDROID_SDK_ROOT')
    aapt2=shutil.which('aapt2') or (str(Path(sdk)/'build-tools/36.0.0/aapt2') if sdk else None)
    if aapt2 and Path(aapt2).is_file():
        metadata=subprocess.run([aapt2,'dump','xmltree',str(apk),'--file','res/xml/watch_face_info.xml'],check=True,capture_output=True,text=True).stdout
        assert re.search(r'E: Editable\b\s*\([^\n]*\)\s*\n\s*A: value=true\b',metadata), 'The compiled APK must declare Editable=true so Wear OS exposes Customize'
print("PASS: Lord of the Rings watch face package checks completed successfully.")
