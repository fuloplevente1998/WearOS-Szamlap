"""Exercise automatic HALO-name pairing in WFF; not a Wear OS renderer."""
from functools import lru_cache
import json
import re
from pathlib import Path
import sys
import zipfile
import xml.etree.ElementTree as E

ROOT=Path(__file__).resolve().parents[1]


def check_icon_switching(wf):
    definitions={c.attrib['id']:c.attrib['defaultValue'] for c in wf.find('UserConfigurations')}
    assert definitions.get('automatic_icons')=='TRUE', 'Automatic HALO icons must apply to existing installs by default'
    assert all(not n.attrib['resource'].startswith('[COMPLICATION.') for n in wf.findall('.//Image')), 'Provider images must never replace our HALO icons'

    @lru_cache(maxsize=None)
    def terms(expression):
        result=[]
        for term in expression.split(' || '):
            match=re.fullmatch(r'\[COMPLICATION\.(TITLE|TEXT)\] == (".*")',term)
            assert match is not None, 'Unsupported icon condition: '+term
            result.append((match[1],json.loads(match[2])))
        return result

    def images(node, settings, data):
        if node.tag in ('BooleanConfiguration','ListConfiguration'):
            key=node.attrib['id'];chosen=settings.get(key,definitions[key])
            option='BooleanOption' if node.tag=='BooleanConfiguration' else 'ListOption'
            branch=node.find(f'{option}[@id="{chosen}"]')
            assert branch is not None, (key,chosen)
            return images(branch,settings,data)
        if node.tag=='Condition':
            values={e.attrib['name']:any(data.get(field)==value for field,value in terms(e.text)) for e in node.find('Expressions')}
            # WFF can activate several Compare groups; do not assume first match.
            active=[branch for branch in node.findall('Compare') if values[branch.attrib['expression']]]
            if active:return [image for branch in active for image in images(branch,settings,data)]
            branch=node.find('Default')
            return images(branch,settings,data) if branch is not None else []
        if node.tag=='PartImage':
            resource=node.find('Image').attrib['resource']
            assert not resource.startswith('['), 'Automatic mode must draw a bundled HALO icon'
            return [(resource,'tintColor' in node.attrib)]
        assert node.tag in ('Group','BooleanOption','ListOption','Compare','Default'), node.tag
        return [result for child in node for result in images(child,settings,data)]

    cases=0
    slots=wf.findall('Scene/ComplicationSlot');assert len(slots)==8
    for slot in slots:
        pid=slot.attrib['displayName'].removesuffix('_slot')
        assert slot.find('Complication[@type="EMPTY"]') is not None
        assert len(slot.find('Complication[@type="EMPTY"]'))==0
        assert 'LONG_TEXT' in slot.attrib['supportedTypes'].split()
        for complication in slot.findall('Complication'):
            if complication.attrib['type']=='EMPTY':continue
            branch=complication.find('Group/BooleanConfiguration[@id="automatic_icons"]')
            assert branch is not None, (pid,complication.attrib['type'])
            # Keep a stored manual symbol while changing only current data.
            previous={pid+'_icon':'helmet'}
            fixtures=[
                ('Health app',previous,{'TEXT':'Samsung Health'},'heart'),
                ('battery app',previous,{'TEXT':'Akkumulátor'},'battery'),
                ('battery data',previous,{'TITLE':'Battery','TEXT':'81%'},'battery'),
                ('steps data',previous,{'TITLE':'Lépésszám','TEXT':'12345'},'steps'),
                ('exercise app',previous,{'TEXT':'TrainPilot'},'runner'),
                ('title before app',previous,{'TITLE':'Steps','TEXT':'Samsung Health'},'steps'),
                ('unknown title, known app',previous,{'TITLE':'Daily value','TEXT':'Samsung Health'},'heart'),
                ('no names',previous,{},'helmet'),
                ('unknown app',previous,{'TEXT':'Unlisted application'},'helmet'),
                ('anonymous percentage',previous,{'TEXT':'81%'},'helmet'),
                ('never Android icons',previous,{'TEXT':'Samsung Health','SMALL_IMAGE':'android/image','MONOCHROMATIC_IMAGE':'android/mono'},'heart'),
                ('manual mode',{'automatic_icons':'FALSE',**previous},{'TEXT':'Samsung Health'},'helmet'),
                ('legacy provider option',{'automatic_icons':'FALSE',pid+'_icon':'provider'},{'TEXT':'Akkumulátor'},'battery'),
                ('default fallback',{}, {},definitions[pid+'_icon']),
            ]
            for name,settings,data,expected in fixtures:
                actual=images(branch,settings,data)
                assert actual==[('icon_'+expected,True)], (pid,complication.attrib['type'],name,expected,actual)
                cases+=1
            if complication.attrib['type']=='LONG_TEXT':
                # Explicit expected results also exercise the editable alias table.
                for expected,aliases in json.loads((ROOT/'design/icon-pairings.json').read_text()).items():
                    for alias in aliases:
                        for value in {alias,alias.lower(),alias.upper(),alias.title()}:
                            actual=images(branch,previous,{'TEXT':value})
                            assert actual==[('icon_'+expected,True)], (pid,value,expected,actual)
                            cases+=1
    return {'slots':len(slots),'cases':cases,'nativeWearOSRuntime':False,'recognition':'Explicit Hungarian/English TITLE/TEXT aliases; unknown or anonymous data uses manual HUD fallback'}


if __name__=='__main__':
    path=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'watchface/src/main/res/raw/watchface.xml'
    if path.suffix=='.apk':
        with zipfile.ZipFile(path) as apk:wf=E.fromstring(apk.read('res/raw/watchface.xml'))
    else:wf=E.parse(path).getroot()
    result=check_icon_switching(wf)
    print(f"PASS: {result['cases']} HALO icon selection cases across {result['slots']} slots; names, title priority, app swaps, upgrade defaults, manual mode, unknown-source fallback; no Android icons. XML logic only, not device rendering.")
