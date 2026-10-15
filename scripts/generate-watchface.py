#!/usr/bin/env python3
"""Generate WFF 2 and modular SVG artwork; no third party Python packages needed."""
from pathlib import Path
import json
import math
import xml.etree.ElementTree as E
from hud_geometry import PANELS as panels, SCENE, training_inner
from hud_icons import HUD_ICONS

ROOT = Path(__file__).resolve().parents[1]
SVG = ROOT / 'design/svg'
RES = ROOT / 'watchface/src/main/res'
SVG.mkdir(parents=True, exist_ok=True)
digits = json.loads((ROOT / 'design/digits.json').read_text())
icons = json.loads((ROOT / 'design/icons.json').read_text())
pairings = json.loads((ROOT / 'design/icon-pairings.json').read_text())
assert set(pairings) <= set(icons)
palette_id=SCENE['paletteConfiguration']
C,ICE,R,B,H=[f'[CONFIGURATION.{palette_id}.{i}]' for i in range(5)]
strings = {'watch_face_name': 'Spartan Night · Test', 'palette': 'HUD színe',
           'seconds': 'Másodpercek', 'background': 'Páncélos háttér',
           'unsc': 'HALO cián', 'green': 'HUD zöld', 'amber': 'Borostyán',
           'off': 'Kikapcsolva', 'health_app': 'Samsung Health', 'trainpilot': 'TrainPilot',
           'alarm_action': 'Ébresztő', 'music_action': 'Zene', 'settings_action': 'Beállítások',
           'calendar_action': 'Naptár', 'battery_action': 'Akkumulátor',
           'heart_action': 'Pulzus', 'phone_action': 'Telefon', 'message_action': 'Üzenetek'}
strings.update(bezel='Lunetta', bezel_metal='Grafit fémkeret + HUD', bezel_hud='Csak HUD gyűrű', bezel_off='Keret nélkül')
strings['automatic_icons'] = 'Automatikus HALO-ikonok'
icon_names = dict(zip(icons, ['Szív','Cipő','Akkumulátor','Naptár','Súlyzó','Nap','Pajzs',
    'Radar','Ébresztő','Hangjegy','Beállítások','Stopper','Útvonal','Láng','Sisak','Futó',
    'Kommunikáció','Célkereszt','Sas','Adatsávok']))
# Keep the old option ID for stored editor choices, but never render Android
# icons. The legacy provider option now means automatic HALO pairing.
icon_names['provider'] = 'Automatikus HALO-jel'

(ROOT / 'design/layout.json').write_text(json.dumps(panels, indent=2, ensure_ascii=False)+'\n')
(ROOT / 'design/scene.json').write_text(json.dumps(SCENE, indent=2)+'\n')

def svg(name, w, h, body, view=None):
    (SVG / f'{name}.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="{view or f"0 0 {w} {h}"}">{body}</svg>\n')

for ch, path in digits.items():
    name = 'colon' if ch == ':' else ch
    w = 16 if ch == ':' else 70
    svg(f'digit_{name}', w*2, 200, f'<path d="{path}" fill="white" fill-rule="evenodd"/>', f'0 0 {w} 100')

for name, path in icons.items():
    if name in HUD_ICONS:
        svg('icon_'+name,128,128,HUD_ICONS[name],'0 0 64 64')
        continue
    # Filled HUD silhouettes plus line based system controls, all tintable.
    filled = name in ('heart','battery','unsc')
    svg(f'icon_{name}',96,96,f'<path d="{path}" fill="{"white" if filled else "none"}" fill-rule="evenodd" stroke="white" stroke-width="{.45 if filled else 1.65}" stroke-linecap="round" stroke-linejoin="round"/>','-1 -1 26 26')

def outline(p, **attrs):
    node=E.Element('path', {**p['outline'], **{k:str(v) for k,v in attrs.items()}})
    return E.tostring(node, encoding='unicode')

for p in panels:
    x,y,w,h=p['rect']
    quick=p['id'].startswith('quick_')
    opacity=[a*.45 for a in SCENE['glassOpacity']] if quick else SCENE['glassOpacity']
    stops=''.join(f'<stop offset="{off}" stop-color="{color}" stop-opacity="{alpha}"/>' for off,color,alpha in zip([0,.18,.8,1],['#155266','#082b3e','#071d30','#12617a'],opacity))
    clip='<defs><clipPath id="c">'+outline(p)+'</clipPath><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">'+stops+'</linearGradient></defs>'
    scan=''.join(f'<path d="M{x} {sy}H{x+w}"/>' for sy in range(y+10,y+h,13))
    svg('glass_'+p['id'],w*2,h*2,clip+outline(p,fill='url(#g)')+f'<g clip-path="url(#c)" stroke="#8ec7e1" stroke-opacity=".018" stroke-width=".6">{scan}</g>',f'{x} {y} {w} {h}')
    edges=outline(p,fill='none',stroke='white',**{'stroke-width':4,'stroke-opacity':.10 if not quick else .04})
    edges+=outline(p,fill='none',stroke='white',**{'stroke-width':1.5,'stroke-opacity':.9 if not quick else .38,'stroke-linejoin':'round'})
    if p['id']=='training':
        edges+=f'<path d="{training_inner}" fill="none" stroke="white" stroke-width="1" stroke-opacity=".65" stroke-linejoin="round"/>'
    svg('edge_'+p['id'],w*2,h*2,edges,f'{x} {y} {w} {h}')

def pt(a,r):return (225+r*math.cos(math.radians(a)),225+r*math.sin(math.radians(a)))
def circle_arc(a,b,r):
    x1,y1=pt(a,r); x2,y2=pt(b,r)
    return f'<path d="M{x1:.3f} {y1:.3f}A{r} {r} 0 0 1 {x2:.3f} {y2:.3f}"/>'
track_radius=SCENE['trackRadius']
arcs=[]
for angle in range(0,360,30):
    arcs.append(circle_arc(angle+3,angle+26,track_radius))
    arcs.append(circle_arc(angle+28,angle+29.5,track_radius))
svg('hud_track',900,900,'<g stroke="white" fill="none" stroke-width="5.1" opacity=".96">'+''.join(arcs)+'</g>','0 0 450 450')

# A narrow, static metal rim inside the display; it does not rescale the UI.
# All paint stays outside r=217.5, leaving data and app icons unobscured.
metal='<defs><linearGradient id="steel" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#747c81"/><stop offset=".25" stop-color="#3c4348"/><stop offset=".54" stop-color="#252c31"/><stop offset=".78" stop-color="#555e64"/><stop offset="1" stop-color="#8a9298"/></linearGradient></defs>'
metal+='<circle cx="225" cy="225" r="221.25" fill="none" stroke="url(#steel)" stroke-width="7.5"/>'
metal+='<circle cx="225" cy="225" r="224.25" fill="none" stroke="#a2aaae" stroke-opacity=".65" stroke-width=".8"/>'
metal+='<circle cx="225" cy="225" r="218.2" fill="none" stroke="#05090b" stroke-width="1.2"/>'
metal+='<circle cx="225" cy="225" r="219.1" fill="none" stroke="#b6c1c7" stroke-opacity=".25" stroke-width=".6"/>'
for angle in range(0,360,3):
    a=pt(angle,220);b=pt(angle+.3,223.4)
    metal+=f'<path d="M{a[0]:.2f} {a[1]:.2f}L{b[0]:.2f} {b[1]:.2f}" fill="none" stroke="#d0d9de" stroke-opacity=".12" stroke-width=".35"/>'
for angle in (45,135,225,315):
    x,y=pt(angle,221.2)
    metal+=f'<circle cx="{x:.3f}" cy="{y:.3f}" r="2.55" fill="#10171c" stroke="#919ba0" stroke-width=".45"/><circle cx="{x:.3f}" cy="{y:.3f}" r="1.65" fill="#4c565d"/><path d="M{x-1.1:.3f} {y-1.1:.3f}L{x+1.1:.3f} {y+1.1:.3f}" stroke="#050b0e" stroke-width=".8"/>'
svg('bezel_metal',900,900,metal,'0 0 450 450')
frame=SCENE['clockFrame']; x,y,w,h=frame['rect']
svg('clock_frame',w*2,h*2,outline(frame,fill='none',stroke='white',**{'stroke-width':1.7,'stroke-opacity':.85,'stroke-linejoin':'round'}),f'{x} {y} {w} {h}')

def el(parent, tag, **attrs):
    return E.SubElement(parent,tag,{k:str(v) for k,v in attrs.items()})
def rect(parent,tag,r,**attrs):
    return el(parent,tag,**dict(zip(('x','y','width','height'),r)),**attrs)
def group(parent,name,r):return rect(parent,'Group',r,name=name)
def ambient_hide(node):el(node,'Variant',mode='AMBIENT',target='alpha',value=0)
def image(parent,res,r,tint=None):
    node=rect(parent,'PartImage',r,**({'tintColor':tint} if tint else {}))
    el(node,'Image',resource=res)
    return node
def text(parent,r,size,literal=None,expression=None,color=ICE,ellipsis=True):
    node=rect(parent,'PartText',r)
    t=el(node,'Text',align='CENTER',ellipsis='TRUE' if ellipsis else 'FALSE',maxLines=1)
    f=el(t,'Font',family=SCENE['fontFamily'],size=size,weight='BOLD',color=color)
    if expression:
        template=el(f,'Template'); template.text='%s';el(template,'Parameter',expression=expression)
    else:f.text=literal
    return node
def condition(parent,name,expression):
    node=el(parent,'Condition'); expressions=el(node,'Expressions')
    el(expressions,'Expression',name=name).text=expression
    return el(node,'Compare',expression=name)
def manual_icon(parent,p,r,tint,include_automatic=True):
    conf=el(parent,'ListConfiguration',id=p['id']+'_icon')
    for name in list(icons)+['provider']:
        opt=el(conf,'ListOption',id=name)
        g=group(opt,p['id']+'_icon_'+name,r)
        if name=='provider' and include_automatic:
            paired_icon(g,p,[0,0,r[2],r[3]],tint)
        else:
            image(g,'icon_'+(p['icon'] if name=='provider' else name),[0,0,r[2],r[3]],tint)

def paired_icon(parent,p,r,tint):
    # WFF exposes TITLE/TEXT, not the selected provider's package/component ID.
    # Prefer the specific data title over a general app name. Only exact,
    # explicit aliases are used: a percentage alone is not proof of battery.
    for field in ('TITLE','TEXT'):
        decision=el(parent,'Condition');expressions=el(decision,'Expressions')
        seen=set()
        for name,aliases in pairings.items():
            variants=sorted({v for alias in aliases for v in (alias,alias.lower(),alias.upper(),alias.title())})
            assert not seen.intersection(variants), 'Ambiguous automatic HUD alias'
            seen.update(variants)
            matches=' || '.join(f'[COMPLICATION.{field}] == {json.dumps(v,ensure_ascii=False)}' for v in variants)
            el(expressions,'Expression',name=field.lower()+'_'+name).text=matches
        for name in pairings:
            match=el(decision,'Compare',expression=field.lower()+'_'+name)
            image(match,'icon_'+name,r,tint)
        # Compare groups can all be active at once in WFF. Nest TEXT in the
        # TITLE default so only one field can select an icon at any moment.
        parent=el(decision,'Default')
    # Unknown/anonymous data keeps the selected manual HUD symbol. Never guess
    # heart/battery from a numeric value and never draw the provider's image.
    fallback=group(parent,p['id']+'_unrecognised_icon',[0,0,p['rect'][2],p['rect'][3]])
    manual_icon(fallback,p,r,tint,include_automatic=False)

def icon(parent,p,r):
    tint=H if p['id'] in ('armor','health','radar') or p['id'].startswith('quick_') else ICE
    # A new setting makes automatic icons the default on upgrades too, even
    # when old per-panel HUD choices are still stored by the watch editor.
    mode=el(parent,'BooleanConfiguration',id='automatic_icons')
    auto=el(mode,'BooleanOption',id='TRUE')
    paired_icon(auto,p,r,tint)
    manual=el(mode,'BooleanOption',id='FALSE')
    manual_group=group(manual,p['id']+'_manual_icons',[0,0,p['rect'][2],p['rect'][3]])
    manual_icon(manual_group,p,r,tint)
def skin(parent,p):
    w,h=p['rect'][2:]
    image(parent,'glass_'+p['id'],[0,0,w,h])
    image(parent,'edge_'+p['id'],[0,0,w,h],R if p['id'] in ('armor','radar') else B)

wf=E.Element('WatchFace',width='450',height='450',clipShape='CIRCLE')
el(wf,'Metadata',key='CLOCK_TYPE',value='DIGITAL')
el(wf,'Metadata',key='PREVIEW_TIME',value='10:34:27')
fonts=el(wf,'BitmapFonts'); font=el(fonts,'BitmapFont',name='spartan_digits')
for ch in digits:
    el(font,'Character',name=ch,resource='digit_'+('colon' if ch==':' else ch),width=16 if ch==':' else 70,height=100,marginRight=8)
conf=el(wf,'UserConfigurations')
palette=el(conf,'ColorConfiguration',id=palette_id,displayName='palette',defaultValue=SCENE['defaultPalette'])
for name,theme in SCENE['palettes'].items():
    strings[name]=theme['label']
    el(palette,'ColorOption',id=name,displayName=name,colors=' '.join(theme['colors']))
bezel=el(conf,'ListConfiguration',id='bezel',displayName='bezel',defaultValue='metal',icon='icon_target')
for name in ('metal','hud','off'):
    el(bezel,'ListOption',id=name,displayName='bezel_'+name)
for name in ['seconds','background','automatic_icons']:
    el(conf,'BooleanConfiguration',id=name,displayName=name,defaultValue='TRUE',icon='icon_settings')
for p in panels:
    pid=p['id']; strings[pid+'_icon']=p['label']+' · HUD-jelkép'
    c=el(conf,'ListConfiguration',id=pid+'_icon',displayName=pid+'_icon',defaultValue=p['icon'],icon='icon_'+p['icon'])
    for name in list(icons)+(['provider'] if 'provider' in p else []):
        strings['icon_'+name]=icon_names[name]
        el(c,'ListOption',id=name,displayName='icon_'+name,**({'icon':'icon_'+name} if name!='provider' else {}))
    strings[pid+'_slot']=p['label']+' · alkalmazás / adat'

scene=el(wf,'Scene',backgroundColor='#000000')
active=group(scene,'active_hud',[0,0,450,450]); ambient_hide(active)
bg=el(active,'BooleanConfiguration',id='background'); opt=el(bg,'BooleanOption',id='TRUE')
image(opt,'armor_background',[0,0,450,450])
# Darken using a separate native layer; the artwork remains an independent resource.
draw=rect(active,'PartDraw',[0,0,450,450]); shape=el(draw,'Rectangle',x=0,y=0,width=450,height=450);el(shape,'Fill',color=SCENE['backgroundShade'])
bezel=el(active,'ListConfiguration',id='bezel')
for name in ('metal','hud','off'):
    mode=group(el(bezel,'ListOption',id=name),'bezel_'+name,[0,0,450,450])
    if name=='metal':image(mode,'bezel_metal',[0,0,450,450])
    if name!='off':image(mode,'hud_track',[0,0,450,450],R)
image(active,'clock_frame',SCENE['clockFrame']['rect'],R)
clock=rect(active,'DigitalClock',SCENE['time']['rect'])
tt=rect(clock,'TimeText',[0,0,*SCENE['time']['rect'][2:]],format='hh:mm',hourFormat='SYNC_TO_DEVICE',align='CENTER')
el(tt,'BitmapFont',family='spartan_digits',size=SCENE['time']['fontSize'],color=C)
seconds=el(active,'BooleanConfiguration',id='seconds'); opt=el(seconds,'BooleanOption',id='TRUE')
clock=rect(opt,'DigitalClock',SCENE['seconds']['rect'])
tt=rect(clock,'TimeText',[0,0,*SCENE['seconds']['rect'][2:]],format='ss',align='CENTER');el(tt,'BitmapFont',family='spartan_digits',size=SCENE['seconds']['fontSize'],color=C)
text(active,SCENE['date']['rect'],SCENE['date']['fontSize'],expression='icuText("MMM dd · EEE")',color=ICE)

for slot_id,p in enumerate(panels):
    pid=p['id']; x,y,w,h=p['rect']
    slot=rect(scene,'ComplicationSlot',[x,y,w,h],slotId=slot_id,displayName=pid+'_slot',supportedTypes='LONG_TEXT SHORT_TEXT RANGED_VALUE EMPTY',isCustomizable='TRUE')
    ambient_hide(slot)
    el(slot,'DefaultProviderPolicy',defaultSystemProvider=p['provider'],defaultSystemProviderType=p['kind'])
    rect(slot,'BoundingBox',p['bounds'])
    quick=pid.startswith('quick_')
    for kind in ['SHORT_TEXT','LONG_TEXT','RANGED_VALUE','EMPTY']:
        comp=el(slot,'Complication',type=kind)
        if kind=='EMPTY':continue
        g=group(comp,pid+'_'+kind,[0,0,w,h]);skin(g,p)
        icon(g,p,p['content']['icon'])
        if quick:continue
        sizes=SCENE['fontSizes']
        if p['provider']=='APP_SHORTCUT' or kind=='SMALL_IMAGE':
            text(g,p['content']['caption'],sizes['caption'],literal='APP')
        else:
            text(g,p['content']['caption'],sizes['caption'],expression=f'[COMPLICATION.TITLE] != null ? [COMPLICATION.TITLE] : "{p["caption"]}"')
        if kind=='SMALL_IMAGE':
            text(g,p['content']['value'],18,literal='OPEN')
        elif kind=='LONG_TEXT':
            text(g,p['content']['value'],sizes['appValue'],expression='[COMPLICATION.TEXT] != null ? [COMPLICATION.TEXT] : "--"')
        else:
            base=sizes['healthValue'] if pid=='health' else sizes['value']
            decision=el(g,'Condition'); expressions=el(decision,'Expressions')
            el(expressions,'Expression',name='wide_value').text='[COMPLICATION.TEXT] != null && textLength([COMPLICATION.TEXT]) > 6'
            small=el(decision,'Compare',expression='wide_value')
            text(small,p['content']['value'],21,expression='[COMPLICATION.TEXT]',ellipsis=False)
            normal=el(decision,'Default')
            text(normal,p['content']['value'],base,expression='[COMPLICATION.TEXT] != null ? [COMPLICATION.TEXT] : "--"',ellipsis=False,color=H if pid=='armor' else ICE)

# Ambient contains only a small, thin clock. No background, seconds or tappable panels.
aod=rect(scene,'DigitalClock',[25,182,400,83])
tt=rect(aod,'TimeText',[0,0,400,83],format='hh:mm',hourFormat='SYNC_TO_DEVICE',align='CENTER',alpha=0)
el(tt,'Variant',mode='AMBIENT',target='alpha',value=255)
el(tt,'Font',family='sans-serif',size=70,weight='THIN',color='#c4dde5')
E.indent(wf)
(RES/'raw/watchface.xml').write_bytes(E.tostring(wf,encoding='utf-8',xml_declaration=True))
values=E.Element('resources')
for key,value in strings.items():el(values,'string',name=key).text=value
E.indent(values)
(RES/'values/strings.xml').write_bytes(E.tostring(values,encoding='utf-8',xml_declaration=True))
print(f'Generated WFF 2: {len(panels)} panels, {len(conf)} configuration categories, 8 native app/data complications.')
