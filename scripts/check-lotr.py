#!/usr/bin/env python3
"""Statically check the One Ring WFF complication contract before packaging."""
import pathlib
import xml.etree.ElementTree as ET

root = pathlib.Path(__file__).resolve().parents[1]
wf = ET.parse(root / "lotrwatchface/src/main/res/raw/watchface.xml").getroot()
assert wf.find("Metadata[@key='CLOCK_TYPE']").get("value") == "ANALOG"
scene = wf.find("Scene")
# WFF uses integer alpha (0..255), not a fractional Canvas opacity.
for v in wf.findall(".//Variant[@target='alpha']"):
    value = float(v.get("value"))
    assert value.is_integer() and 0 <= value <= 255, "Invalid WFF alpha"

def ambient_alpha(element):
    variant = element.find("Variant[@mode='AMBIENT'][@target='alpha']")
    assert variant is not None, "Missing ambient visibility policy"
    return int(variant.get("value"))

map_layer = next(p for p in scene.findall("PartImage")
                 if p.find("Image").get("resource") == "lotr_middle_earth_map")
bezel = next(p for p in scene.findall("PartImage")
             if p.find("Image").get("resource") == "lotr_one_ring_bezel")
assert ambient_alpha(map_layer) == 0, "Hide map in ambient"
assert 0 < ambient_alpha(bezel) < 128, "Dim bezel in ambient"
clock = scene.find("AnalogClock")
assert ambient_alpha(clock.find("SecondHand")) == 0, "Hide seconds in ambient"
for tag in ("HourHand", "MinuteHand", "SecondHand"):
    hand = clock.find(tag)
    for position, length, pivot in (("x", "width", "pivotX"), ("y", "height", "pivotY")):
        center = float(clock.get(position)) + float(hand.get(position)) + float(hand.get(length)) * float(hand.get(pivot))
        assert abs(center - 225) < .001, "Hand pivot must stay at the dial center"
slots = scene.findall("ComplicationSlot")
assert len(slots) == 5, f"Expected five slots, found {len(slots)}"
layers = list(scene)
assert layers.index(clock) > max(layers.index(s) for s in slots), "Draw hands above fields"
assert layers.index(scene.find("PartDraw")) > layers.index(clock), "Draw hub above hands"
names = ["battery", "heart_rate", "steps", "date", "workout"]
providers = ["WATCH_BATTERY", "HEART_RATE", "STEP_COUNT", "DATE", "APP_SHORTCUT"]
expected = {"battery":(182,87,86,42),"heart_rate":(55,199,92,46),
            "steps":(303,199,92,46),"date":(180,328,90,40),"workout":(299,294,46,46)}
for i,(name,provider,slot) in enumerate(zip(names,providers,slots)):
    assert slot.get("slotId") == str(i)
    assert slot.get("displayName") == f"lotr_{name}_slot"
    assert slot.get("isCustomizable") == "TRUE"
    assert slot.find("DefaultProviderPolicy").get("defaultSystemProvider") == provider
    assert slot.find("DefaultProviderPolicy").get("defaultSystemProviderType") in slot.get("supportedTypes").split()
    assert "EMPTY" in slot.get("supportedTypes").split()
    assert slot.find("Complication[@type='EMPTY']") is not None
    assert slot.find("BoundingBox") is not None
    assert tuple(int(slot.get(k)) for k in ("x","y","width","height")) == expected[name]
    assert ambient_alpha(slot) == 0, "Hide fields in ambient"
    for c in slot.findall("Complication"):
        if c.get("type") == "EMPTY":
            assert len(c) == 0
            continue
        assert c.find(".//PartDraw") is not None
        assert c.find(".//PartText") is not None
        if name != "workout":
            assert any("[COMPLICATION.TEXT]" in (e.get("expression") or "")
                       for e in c.iter("Parameter"))
    x,y,w,h=expected[name]
    assert 0 <= x and 0 <= y and x+w < 450 and y+h < 450
    # Keep complications inside the inner radius of the golden One Ring bezel.
    from math import hypot
    assert hypot(x+w/2-225,y+h/2-225)+max(w,h)/2 < 190
info = ET.parse(root / "lotrwatchface/src/main/res/xml/watch_face_info.xml").getroot()
assert info.find("Editable").get("value") == "true"
assert info.find("Preview").get("value") == "@drawable/lotr_preview"
manifest = ET.parse(root / "lotrwatchface/src/main/AndroidManifest.xml").getroot()
android_ns = "{http://schemas.android.com/apk/res/android}"
assert manifest.find("application").get(android_ns + "icon") == "@drawable/lotr_preview"
print("PASS: Five native LOTR slots, safe bounds, foreground hands and integer ambient alpha; no synthetic readings")
