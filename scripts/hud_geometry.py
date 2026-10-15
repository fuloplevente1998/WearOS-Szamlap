"""One layout for native WFF, SVG assets and the illustrative picker preview.

The outside contours use true SVG circle arcs, all centered on the display.
Coordinates are in a 450 x 450 virtual display; Android scales them to the watch.
"""
import math

CENTER = (225, 225)
PANEL_RADIUS = 204


def point(angle, radius=PANEL_RADIUS):
    radians = math.radians(angle)
    return (225 + radius * math.cos(radians), 225 + radius * math.sin(radians))


def xy(p):
    return f'{p[0]:.3f} {p[1]:.3f}'


def arc(start, end, radius=PANEL_RADIUS, clockwise=True):
    return f'M {xy(point(start, radius))} A {radius} {radius} 0 0 {int(clockwise)} {xy(point(end, radius))}'


def mirror_path(path):
    # Mirroring is a geometric SVG transform, preserving exact arc radii.
    return {'d': path, 'transform': 'translate(450 0) scale(-1 1)'}


armor = arc(252, 202, clockwise=False) + ' Q 36 151 42 151 H 158 Q 166 151 166 143 V 37 Q 166 31 161.960 30.984 Z'
health = arc(255, 285) + ' V 143 L 268 155 H 182 L 172.201 143 Z'
# Shared 45-degree shoulders and parallel side steps make the bottom modules
# nest together. The flanking borders follow the centre badge with an 8px gap.
steps = 'M ' + xy(point(164)) + ' H 145 Q 151 281.230 151 287 V 333.8 L 159 343.8 V 383 Q 159 393 149 393 H 111 L ' + xy(point(126)) + f' A {PANEL_RADIUS} {PANEL_RADIUS} 0 0 1 {xy(point(164))} Z'
training = 'M 176 274 H 274 L 291 291 V 331 L 283 341 V 377 L 268 392 H 182 L 167 377 V 341 L 159 331 V 291 Z'
training_inner = 'M 178 278 H 272 L 287 293 V 329 L 279 339 V 375 L 266 388 H 184 L 171 375 V 339 L 163 329 V 293 Z'


def local_rect(rect, origin):
    return [rect[0] - origin[0], rect[1] - origin[1], rect[2], rect[3]]


def panel(pid, label, rect, outline, icon, *, provider=None, kind=None,
          caption=None, action=None, content=None, bounds=None, outer_arc=None):
    p = dict(id=pid, label=label, rect=rect, outline=outline, icon=icon)
    if provider:
        p.update(provider=provider, kind=kind, caption=caption)
    if action:
        p['action'] = action
    if content:
        p['content'] = {key: local_rect(value, rect) for key, value in content.items()}
    # A complication's bounding area also clips rendering. It must contain the
    # whole panel, not only the central tap target (the 0.1.2 clipping bug).
    p['bounds'] = [0, 0, rect[2], rect[3]]
    if outer_arc:
        p['outerArc'] = dict(center=list(CENTER), radius=PANEL_RADIUS, angles=outer_arc)
    return p


PANELS = [
    panel('armor', '01 · Bal felső', [32, 28, 136, 128], {'d': armor}, 'helmet',
          provider='WATCH_BATTERY', kind='RANGED_VALUE', caption='ARMOR',
          content={'caption': [101, 51, 63, 28], 'icon': [106, 73, 54, 54], 'value': [59, 119, 106, 35]},
          bounds=[108, 65, 54, 80], outer_arc=[202, 252]),
    panel('health', '02 · Felső középső', [170, 20, 110, 137], {'d': health}, 'heart',
          provider='HEART_RATE', kind='SHORT_TEXT', caption='HEALTH',
          content={'caption': [181, 28, 88, 32], 'icon': [198, 56, 54, 54], 'value': [176, 108, 98, 44]},
          bounds=[182, 36, 86, 110], outer_arc=[255, 285]),
    panel('radar', '03 · Jobb felső', [282, 28, 136, 128], mirror_path(armor), 'radar',
          provider='WORLD_CLOCK', kind='SHORT_TEXT', caption='WORLD',
          content={'caption': [286, 51, 63, 28], 'icon': [290, 73, 54, 54], 'value': [285, 119, 106, 35]},
          bounds=[288, 65, 54, 80], outer_arc=[288, 338]),
    panel('steps', '04 · Bal alsó', [25, 278, 137, 118], {'d': steps}, 'steps',
          provider='STEP_COUNT', kind='SHORT_TEXT', caption='ACTIVITY',
          content={'caption': [59, 278, 94, 28], 'icon': [92, 296, 50, 50], 'value': [78, 330, 76, 44]},
          bounds=[82, 308, 60, 58], outer_arc=[126, 158]),
    panel('training', '05 · Középső gomb', [157, 272, 136, 124], {'d': training}, 'runner',
          provider='APP_SHORTCUT', kind='LONG_TEXT', caption='APP',
          content={'caption': [163, 276, 124, 30], 'icon': [197, 300, 56, 56], 'value': [164, 351, 122, 36]}),
    panel('battery', '06 · Jobb alsó', [288, 278, 137, 118], mirror_path(steps), 'battery',
          provider='WATCH_BATTERY', kind='SHORT_TEXT', caption='POWER',
          content={'caption': [297, 278, 94, 28], 'icon': [308, 296, 50, 50], 'value': [296, 330, 76, 44]},
          bounds=[308, 308, 60, 58], outer_arc=[22, 54]),
]


def quick_outline(start, end):
    inner, outer = 183, 207
    return (arc(start, end, outer)
            + ' L ' + xy(point(end, inner))
            + f' A {inner} {inner} 0 0 0 {xy(point(start, inner))} Z')


for pid, label, rect, angles, icon_name, action, image_rect in [
    ('quick_left', '07 · Bal gyorsgomb', [159, 397, 62, 38], [92, 108], 'target', 'alarm_action', [183, 400, 28, 28]),
    ('quick_right', '08 · Jobb gyorsgomb', [229, 397, 62, 38], [72, 88], 'telemetry', 'settings_action', [239, 400, 28, 28]),
]:
    PANELS.append(panel(pid, label, rect, {'d': quick_outline(*angles)}, icon_name,
                        provider='APP_SHORTCUT', kind='LONG_TEXT', caption='APP', content={'icon': image_rect}))

main_outline = ('M ' + xy(point(200)) + ' H 174.25 L 180 162 H 270 L 275.75 155.228 H ' + xy(point(340)).split()[0]
                + f' A {PANEL_RADIUS} {PANEL_RADIUS} 0 0 1 {xy(point(15))}'
                # Offset the centre badge's 45-degree shoulder by 6px.
                + ' H 286.285 L 276.486 268 H 173.514 L 163.715 277.799 H ' + xy(point(165)).split()[0]
                + f' A {PANEL_RADIUS} {PANEL_RADIUS} 0 0 1 {xy(point(200))} Z')

SCENE = {
    'size': 450,
    'backgroundShade': '#2400060b',
    'panelRadius': PANEL_RADIUS,
    'trackRadius': 212.7,
    'bezelInnerRadius': 217.5,
    'paletteConfiguration': 'palette_v2',
    'defaultPalette': 'reference',
    'palettes': {
        # Roles: time, ice text, green contours, blue contours, HUD symbols.
        'reference': {'label': 'Referencia · zöld / cián', 'colors': ['#7fff89', '#9ae4f5', '#69ce83', '#60b7d5', '#7bef95']},
        'unsc': {'label': 'HALO cián', 'colors': ['#9de4f7', '#8de6ff', '#8acfe2', '#60b7d5', '#9de4f7']},
        'green': {'label': 'HUD zöld', 'colors': ['#8aff9b', '#8de6ff', '#79d592', '#60b7d5', '#8aff9b']},
        'amber': {'label': 'Borostyán', 'colors': ['#f2c27a', '#b7e2ed', '#cfaa6f', '#79afc4', '#f2c27a']},
    },
    'clockFrame': {'rect': [19, 151, 412, 129], 'outline': {'d': main_outline}},
    'time': {'rect': [51, 164, 306, 88], 'fontSize': 80},
    'seconds': {'rect': [367, 210, 48, 42], 'fontSize': 30},
    'date': {'rect': [100, 244, 250, 27], 'fontSize': 16},
    'fontFamily': 'hud_bold',
    'fontSizes': {'caption': 16, 'value': 26, 'healthValue': 28, 'appValue': 18},
    'glassOpacity': [0.20, 0.10, 0.16, 0.28],
}
