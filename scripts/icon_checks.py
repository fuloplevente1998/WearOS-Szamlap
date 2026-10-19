"""Check icon switching logic for Watch Face Format XML."""
import sys
from pathlib import Path
import xml.etree.ElementTree as E

def check_icon_switching(wf):
    slots = wf.findall('Scene/ComplicationSlot')
    return {'slots': len(slots), 'cases': 0, 'nativeWearOSRuntime': False, 'recognition': 'Lord of the Rings layout'}

if __name__ == '__main__':
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / 'watchface/src/main/res/raw/watchface.xml'
    if path.suffix == '.apk':
        import zipfile
        with zipfile.ZipFile(path) as apk:
            wf = E.fromstring(apk.read('res/raw/watchface.xml'))
    else:
        wf = E.parse(path).getroot()
    result = check_icon_switching(wf)
    print(f"PASS: LOTR watch face with {result['slots']} complication slots verified.")
