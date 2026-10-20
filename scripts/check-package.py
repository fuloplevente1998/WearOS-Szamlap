#!/usr/bin/env python3
"""Check WFF resource references and delivered APKs for watchface (HALO) and lotr (One Ring)."""
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

root = Path(__file__).resolve().parents[1]

def check_watchface_module():
    res = root / 'watchface/src/main/res'
    wf = E.parse(res / 'raw/watchface.xml').getroot()
    strings = {n.attrib['name'] for n in E.parse(res / 'values/strings.xml').getroot()}
    drawables = {p.stem for p in (res / 'drawable-nodpi').glob('*.png')}
    configs = wf.find('UserConfigurations')
    assert configs is not None and len(configs) <= 20, 'WFF 2 allows up to 20 configuration categories'
    info = E.parse(res / 'xml/watch_face_info.xml').getroot()
    if len(configs) or wf.findall('Scene/ComplicationSlot'):
        editable = info.find('Editable')
        assert editable is not None and editable.attrib.get('value') == 'true', 'Customizable watch faces must enable the Wear OS editor in watch_face_info.xml'
    for c in configs:
        if c.tag != 'BooleanConfiguration':
            assert c.attrib['defaultValue'] in {o.attrib['id'] for o in c}, c.attrib['id']
    for n in wf.iter():
        for a in ['displayName', 'screenReaderText']:
            if a in n.attrib:
                assert n.attrib[a] in strings, (n.tag, a, n.attrib[a])
        for a in ['resource', 'icon']:
            if a in n.attrib and not n.attrib[a].startswith('['):
                assert n.attrib[a] in drawables, (n.tag, a, n.attrib[a])
    slots = wf.findall('Scene/ComplicationSlot')
    assert len(slots) == 8
    check_complication_crops(wf)
    icon_checks = check_icon_switching(wf)
    for s in slots:
        assert s.find('Complication[@type="EMPTY"]') is not None
        assert len(s.find('Complication[@type="EMPTY"]')) == 0, 'None must hide the entire panel'
        assert s.find('Variant[@mode="AMBIENT"][@target="alpha"][@value="0"]') is not None
        types = set(s.attrib['supportedTypes'].split())
        assert types == {c.attrib['type'] for c in s.findall('Complication')}
        assert types == {'LONG_TEXT', 'SHORT_TEXT', 'RANGED_VALUE', 'EMPTY'}, 'App shortcuts need LONG_TEXT'

    apk = root / 'watchface/build/outputs/apk/debug/watchface-debug.apk'
    verify_apk(apk, res, drawables, expected_package="hu.fuloplevente.spartannight")
    print(f"PASS [HALO]: 8 slots; {icon_checks['cases']} icon selection cases; editor enabled; no DEX; package hu.fuloplevente.spartannight.")

def check_lotr_module():
    res = root / 'lotr/src/main/res'
    wf = E.parse(res / 'raw/watchface.xml').getroot()
    strings = {n.attrib['name'] for n in E.parse(res / 'values/strings.xml').getroot()}
    drawables = {p.stem for p in (res / 'drawable-nodpi').glob('*.png')}
    info = E.parse(res / 'xml/watch_face_info.xml').getroot()
    editable = info.find('Editable')
    assert editable is not None and editable.attrib.get('value') == 'true'
    for n in wf.iter():
        for a in ['displayName', 'screenReaderText']:
            if a in n.attrib:
                assert n.attrib[a] in strings, (n.tag, a, n.attrib[a])
        for a in ['resource', 'icon']:
            if a in n.attrib and not n.attrib[a].startswith('['):
                assert n.attrib[a] in drawables, (n.tag, a, n.attrib[a])
    slots = wf.findall('Scene/ComplicationSlot')
    assert len(slots) == 2, f"Expected 2 complication slots for LOTR, found {len(slots)}"
    for s in slots:
        assert s.find('Complication[@type="EMPTY"]') is not None
        assert s.find('Variant[@mode="AMBIENT"][@target="alpha"][@value="0"]') is not None

    apk = root / 'lotr/build/outputs/apk/debug/lotr-debug.apk'
    verify_apk(apk, res, drawables, expected_package="hu.fuloplevente.onering")
    print("PASS [LOTR]: 2 slots; editor enabled; no DEX; package hu.fuloplevente.onering.")

def verify_apk(apk, res, drawables, expected_package):
    assert apk.is_file(), f"APK not found: {apk}"
    with zipfile.ZipFile(apk) as z:
        names = z.namelist()
        assert not any(re.fullmatch(r'classes\d*\.dex', n) for n in names), f'WFF APK {apk} must be resource-only'
        assert 'res/raw/watchface.xml' in names
        assert 'res/xml/watch_face_info.xml' in names
        assert z.read('res/raw/watchface.xml') == (res / 'raw/watchface.xml').read_bytes()
        packed = {Path(n).stem for n in names if n.startswith('res/drawable')}
        assert drawables <= packed, f'Missing packaged resources in {apk}: {drawables - packed}'

    sdk = os.environ.get('ANDROID_HOME') or os.environ.get('ANDROID_SDK_ROOT')
    aapt2 = shutil.which('aapt2') or (str(Path(sdk) / 'build-tools/36.0.0/aapt2') if sdk else None)
    if aapt2 and Path(aapt2).is_file():
        metadata = subprocess.run([aapt2, 'dump', 'xmltree', str(apk), '--file', 'res/xml/watch_face_info.xml'], check=True, capture_output=True, text=True).stdout
        assert re.search(r'E: Editable\b\s*\([^\n]*\)\s*\n\s*A: value=true\b', metadata), f'Editable=true required for {apk}'
        badging = subprocess.run([aapt2, 'dump', 'badging', str(apk)], check=True, capture_output=True, text=True).stdout
        assert f"name='{expected_package}'" in badging, f"Expected package name {expected_package} in {apk}"

if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if target in ('all', 'watchface'):
        check_watchface_module()
    if target in ('all', 'lotr'):
        check_lotr_module()
