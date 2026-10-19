#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

# Fast source-only checks: no Gradle build, Node/Chromium, SDK, APK or signing.
python3 - <<'PY'
from pathlib import Path
import xml.etree.ElementTree as ET
from scripts.clipping_checks import check_complication_crops

root = Path('watchface/src/main/res')
wf = ET.parse(root / 'raw/watchface.xml').getroot()
assert wf.tag == 'WatchFace' and wf.attrib.get('clipShape') == 'CIRCLE'
manifest = ET.parse('watchface/src/main/AndroidManifest.xml').getroot()
android = '{http://schemas.android.com/apk/res/android}'
app = manifest.find('application')
assert app is not None and app.attrib.get(android + 'hasCode') == 'false'
property_node = app.find('property')
assert property_node is not None and property_node.attrib.get(android + 'name') == 'com.google.wear.watchface.format.version' and property_node.attrib.get(android + 'value') == '2'
info = ET.parse(root / 'xml/watch_face_info.xml').getroot()
assert info.find('Editable').attrib.get('value') == 'true'
configs = wf.find('UserConfigurations')
assert configs is not None and len(configs) <= 20
for conf in configs:
    if conf.tag != 'BooleanConfiguration':
        assert conf.attrib.get('defaultValue') in {option.attrib.get('id') for option in conf}
slots = wf.findall('Scene/ComplicationSlot')
assert len(slots) == 8
assert not wf.findall('.//Launch')
assert (root / 'font/hud_bold.ttf').is_file()
resources = {file.stem for file in (root / 'drawable-nodpi').glob('*.png')}
strings = {node.attrib['name'] for node in ET.parse(root / 'values/strings.xml').getroot()}
for node in wf.iter():
    for attr in ('resource', 'icon'):
        value = node.attrib.get(attr)
        if value and not value.startswith('['):
            assert value in resources, (node.tag, attr, value)
    for attr in ('displayName', 'screenReaderText'):
        value = node.attrib.get(attr)
        if value:
            assert value in strings, (node.tag, attr, value)
for slot in slots:
    kinds = set(slot.attrib['supportedTypes'].split())
    assert kinds == {'LONG_TEXT', 'SHORT_TEXT', 'RANGED_VALUE', 'EMPTY'}
    assert kinds == {item.attrib['type'] for item in slot.findall('Complication')}
    empty = slot.find('Complication[@type="EMPTY"]')
    assert empty is not None and len(empty) == 0
    assert slot.find('Variant[@mode="AMBIENT"][@target="alpha"][@value="0"]') is not None
check_complication_crops(wf)
print('PASS: WFF 2 source metadata, editor, resources, slots and clipping.')
PY

python3 scripts/icon_checks.py

# Only fetch the smaller validator in quick mode. Checksums must match the
# pinned publisher digests; never bypass a mismatch.
tools_dir="${WFF_TOOLS_DIR:-$PWD/.tools/wff}"
python3 scripts/fetch-validation-tools.py --output "$tools_dir" --only wff-validator.jar
java -jar "$tools_dir/wff-validator.jar" 2 --stop-on-fail watchface/src/main/res/raw/watchface.xml
echo 'PASS: quick source checks, icon logic and WFF schema. Full verify.sh required before release.'
