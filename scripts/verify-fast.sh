#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

# Fast source-only checks for watchface and lotr modules: no Gradle build, Node/Chromium, SDK, APK or signing.
python3 - <<'PY'
from pathlib import Path
import xml.etree.ElementTree as ET
from scripts.clipping_checks import check_complication_crops

# 1. Verify watchface (HALO) module
root_halo = Path('watchface/src/main/res')
wf_halo = ET.parse(root_halo / 'raw/watchface.xml').getroot()
assert wf_halo.tag == 'WatchFace' and wf_halo.attrib.get('clipShape') == 'CIRCLE'
manifest_halo = ET.parse('watchface/src/main/AndroidManifest.xml').getroot()
android = '{http://schemas.android.com/apk/res/android}'
app_halo = manifest_halo.find('application')
assert app_halo is not None and app_halo.attrib.get(android + 'hasCode') == 'false'
prop_halo = app_halo.find('property')
assert prop_halo is not None and prop_halo.attrib.get(android + 'name') == 'com.google.wear.watchface.format.version' and prop_halo.attrib.get(android + 'value') == '2'
info_halo = ET.parse(root_halo / 'xml/watch_face_info.xml').getroot()
assert info_halo.find('Editable').attrib.get('value') == 'true'

slots_halo = wf_halo.findall('Scene/ComplicationSlot')
assert len(slots_halo) == 8
assert not wf_halo.findall('.//Launch')
assert (root_halo / 'font/hud_bold.ttf').is_file()
resources_halo = {file.stem for file in (root_halo / 'drawable-nodpi').glob('*.png')}
strings_halo = {node.attrib['name'] for node in ET.parse(root_halo / 'values/strings.xml').getroot()}
for node in wf_halo.iter():
    for attr in ('resource', 'icon'):
        value = node.attrib.get(attr)
        if value and not value.startswith('['):
            assert value in resources_halo, (node.tag, attr, value)
    for attr in ('displayName', 'screenReaderText'):
        value = node.attrib.get(attr)
        if value:
            assert value in strings_halo, (node.tag, attr, value)
check_complication_crops(wf_halo)
print('PASS [HALO]: WFF 2 source metadata, editor, resources, slots and clipping.')

# 2. Verify lotr module
root_lotr = Path('lotr/src/main/res')
wf_lotr = ET.parse(root_lotr / 'raw/watchface.xml').getroot()
assert wf_lotr.tag == 'WatchFace' and wf_lotr.attrib.get('clipShape') == 'CIRCLE'
manifest_lotr = ET.parse('lotr/src/main/AndroidManifest.xml').getroot()
app_lotr = manifest_lotr.find('application')
assert app_lotr is not None and app_lotr.attrib.get(android + 'hasCode') == 'false'
prop_lotr = app_lotr.find('property')
assert prop_lotr is not None and prop_lotr.attrib.get(android + 'name') == 'com.google.wear.watchface.format.version' and prop_lotr.attrib.get(android + 'value') == '2'
info_lotr = ET.parse(root_lotr / 'xml/watch_face_info.xml').getroot()
assert info_lotr.find('Editable').attrib.get('value') == 'true'

slots_lotr = wf_lotr.findall('Scene/ComplicationSlot')
assert len(slots_lotr) == 2
resources_lotr = {file.stem for file in (root_lotr / 'drawable-nodpi').glob('*.png')}
strings_lotr = {node.attrib['name'] for node in ET.parse(root_lotr / 'values/strings.xml').getroot()}
for node in wf_lotr.iter():
    for attr in ('resource', 'icon'):
        value = node.attrib.get(attr)
        if value and not value.startswith('['):
            assert value in resources_lotr, (node.tag, attr, value)
    for attr in ('displayName', 'screenReaderText'):
        value = node.attrib.get(attr)
        if value:
            assert value in strings_lotr, (node.tag, attr, value)
print('PASS [LOTR]: WFF 2 source metadata, editor, resources and slots.')
PY

python3 scripts/icon_checks.py

# Fetch WFF validator and validate both schemas
tools_dir="${WFF_TOOLS_DIR:-$PWD/.tools/wff}"
python3 scripts/fetch-validation-tools.py --output "$tools_dir" --only wff-validator.jar
java -jar "$tools_dir/wff-validator.jar" 2 --stop-on-fail watchface/src/main/res/raw/watchface.xml
java -jar "$tools_dir/wff-validator.jar" 2 --stop-on-fail lotr/src/main/res/raw/watchface.xml
echo 'PASS: quick source checks, icon logic and WFF schemas for watchface and lotr. Full verify.sh required before release.'
