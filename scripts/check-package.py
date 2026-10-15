#!/usr/bin/env python3
"""Check WFF resource references and the delivered APK, including empty states."""
from pathlib import Path
import os
import re
import shutil
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as E
from clipping_checks import check_complication_crops
from icon_checks import check_icon_switching

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
icon_checks=check_icon_switching(wf)
for s in slots:
    assert s.find('Complication[@type="EMPTY"]') is not None
    assert len(s.find('Complication[@type="EMPTY"]'))==0, 'None must hide the entire panel'
    assert s.find('Variant[@mode="AMBIENT"][@target="alpha"][@value="0"]') is not None
    types=set(s.attrib['supportedTypes'].split())
    assert types=={c.attrib['type'] for c in s.findall('Complication')}
    bounds=s.find('BoundingBox')
    assert types=={'LONG_TEXT','SHORT_TEXT','RANGED_VALUE','EMPTY'}, 'App shortcuts need LONG_TEXT so their name is available for HALO pairing'
    for c in s.findall('Complication'):
        if c.attrib['type']!='EMPTY':
            assert c.find('.//Image[@resource="glass_'+s.attrib['displayName'].removesuffix('_slot')+'"]') is not None
            automatic=c.find('Group/BooleanConfiguration[@id="automatic_icons"]')
            assert automatic is not None, 'Every complication must follow the current provider icon by default'
            assert automatic.find('BooleanOption[@id="TRUE"]/.//Image[@resource="icon_battery"]') is not None
            icon_config=automatic.find('BooleanOption[@id="FALSE"]/Group/ListConfiguration[@id="'+s.attrib['displayName'].removesuffix('_slot')+'_icon"]')
            assert icon_config is not None, 'The selected HUD symbol must also apply to app shortcuts'
            assert icon_config.find('ListOption[@id="runner"]/.//Image[@resource="icon_runner"]') is not None
            provider=icon_config.find('ListOption[@id="provider"]')
            assert provider.find('.//Image[@resource="icon_heart"]') is not None
active=wf.find('Scene/Group[@name="active_hud"]')
assert active.find('Variant[@mode="AMBIENT"][@target="alpha"][@value="0"]') is not None
bezel=active.find('ListConfiguration[@id="bezel"]')
assert bezel is not None and bezel.find('ListOption[@id="off"]/.//Image') is None
assert configs.find('ColorConfiguration[@id="palette_v2"]').attrib['defaultValue']=='reference'
assert configs.find('BooleanConfiguration[@id="automatic_icons"]').attrib['defaultValue']=='TRUE'
assert wf.attrib.get('clipShape')=='CIRCLE', 'The display clips transparent slot corners to the round screen'
assert wf.find('.//Launch') is None, 'All eight buttons must use native provider tap actions'
assert all(not n.attrib['resource'].startswith('[COMPLICATION.') for n in wf.findall('.//Image')), 'Always draw our own HALO icons, never Android/provider images'
for family in {n.attrib['family'] for n in wf.findall('.//Font')}:
    if family=='hud_bold':assert (res/'font/hud_bold.ttf').exists()
for c in active.findall('ListConfiguration'):
    if not c.attrib['id'].endswith('_action'):continue
    off=c.find('ListOption[@id="off"]')
    assert off is not None and off.find('.//Launch') is None
    assert off.find('.//Image') is None and off.find('.//PartText') is None
    for o in c.findall('ListOption'):
        if o.attrib['id']!='off':assert o.find('.//Launch') is not None
apk=Path(sys.argv[1]) if len(sys.argv)>1 else root/'watchface/build/outputs/apk/debug/watchface-debug.apk'
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
assert aapt2 and Path(aapt2).is_file(), 'Set ANDROID_HOME or put aapt2 on PATH to check compiled editor metadata'
metadata=subprocess.run([aapt2,'dump','xmltree',str(apk),'--file','res/xml/watch_face_info.xml'],check=True,capture_output=True,text=True).stdout
assert re.search(r'E: Editable\b\s*\([^\n]*\)\s*\n\s*A: value=true\b',metadata), 'The compiled APK must declare Editable=true so Wear OS exposes Customize'
print(f"PASS: eight native app/data slots; {icon_checks['cases']} icon selection cases; no content cropped by BoundingBox; app icon type and bundled font present; editor enabled; EMPTY panels hidden; no DEX.")
