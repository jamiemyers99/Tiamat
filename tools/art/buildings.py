"""Parametric building renderer (front-facing, top-down RPG style).

building(kind, **opts) -> dict(spr, ox, oy, fw, fh, door=(cx,cy) cell offset, lights=[(px,py)])
"""
import numpy as np
from functools import lru_cache
from spr import Spr, C
from pal import hx, ramp, shift, h2
from font import SMALL

T = 16

ROOFS = {
    'red':    '#c8473f', 'blue':   '#3f6fc8', 'green':  '#4a9a52', 'brown':  '#9a6440',
    'purple': '#7a52b0', 'teal':   '#2aa19a', 'slate':  '#5e6a80', 'orange': '#e07a3a',
    'gold':   '#d8a632', 'navy':   '#2c3f7a', 'plum':   '#8a3f6a', 'gray':   '#8a8f99',
    'black':  '#3a3848', 'white':  '#d8dde6',
}
WALLS = {
    'plaster': '#efe3c8', 'white': '#eef0f2', 'wood': '#b98452', 'brick': '#b86a4e',
    'stone': '#a8a49c', 'timber': '#f1e8d2', 'dark': '#5a5468', 'glass': '#a8c8e0',
    'cream': '#f3e6c4', 'mint': '#d6eee0', 'sand': '#e6cf9c', 'log': '#9a6a40',
}
TYPE_COL = {
    'Nature': '#4caf50', 'Tide': '#3d8bfd', 'Static': '#f5c542', 'Umbra': '#7a5cc4',
    'Frost': '#7fd6f2', 'Drake': '#e0503a', 'Ember': '#ff7a3d', 'Stone': '#b38b5d',
}


def text_small(s, x, y, text, col):
    for ch in text.upper():
        if ch == ' ':
            x += 3
            continue
        g = SMALL.get(ch)
        if not g:
            continue
        for yy, row in enumerate(g):
            for xx, c in enumerate(row):
                if c == '#':
                    s.px(x + xx, y + yy, col)
        x += len(g[0]) + 1


def text_width(text):
    w = 0
    for ch in text.upper():
        w += 3 if ch == ' ' else len(SMALL.get(ch, ['...'])[0]) + 1
    return w - 1


def icon(s, name, cx, cy, col, col2='#ffffff'):
    """Tiny 7×7 emblem icons."""
    pats = {
        'haven': ["..#.#..", ".#####.", "#######", "#######", ".#####.", "..###..", "...#..."],
        'leaf':  ["....##.", "..####.", ".#####.", "#####..", "####...", ".#.....", "#......"],
        'drop':  ["...#...", "..###..", ".#####.", "#######", "#######", ".#####.", "..###.."],
        'bolt':  ["...###.", "..###..", ".###...", "#######", "...###.", "..###..", ".##...."],
        'moon':  ["..###..", ".##....", "##.....", "##.....", "##.....", ".##....", "..###.."],
        'flake': ["#..#..#", ".#.#.#.", "..###..", "#######", "..###..", ".#.#.#.", "#..#..#"],
        'claw':  ["#..#..#", "#..#..#", "#..#..#", ".#.#.#.", ".#.#.#.", "..###..", "..###.."],
        'flame': ["...#...", "..##...", "..###..", ".#####.", "##.####", "##..###", ".#####."],
        'rock':  ["..###..", ".#####.", "######.", "#######", "#######", ".#####.", "......."],
        'gear':  ["#.###.#", ".#####.", "##...##", "##...##", "##...##", ".#####.", "#.###.#"],
        'eye':   [".......", "..###..", ".#...#.", "#..#..#", ".#...#.", "..###..", "......."],
        'star':  ["...#...", "...#...", ".#####.", "..###..", "..###..", ".##.##.", "#.....#"],
        'anchor': ["..###..", "...#...", ".#####.", "...#...", "#..#..#", ".#.#.#.", "..###.."],
        'wave':  [".......", ".##....", "#..#..#", "....##.", ".##....", "#..#..#", "....##."],
    }
    p = pats.get(name)
    if not p:
        return
    for yy, row in enumerate(p):
        for xx, c in enumerate(row):
            if c == '#':
                s.px(cx - 3 + xx, cy - 3 + yy, col)


def _roof(s, x0, y0, pw, rh, base, snow=False, style='slope'):
    r = ramp(base, 6, 0.13)
    if style == 'flat':
        s.rect(x0, y0, pw, rh, r[2])
        s.rect(x0, y0, pw, 2, r[4]); s.rect(x0, y0 + rh - 3, pw, 3, r[0])
        for x in range(x0 + 4, x0 + pw - 4, 8):
            s.rect(x, y0 + 4, 4, rh - 9, r[1])
        if snow:
            s.rect(x0, y0, pw, 4, '#f4f8ff'); s.rect(x0, y0 + 4, pw, 1, '#c8d6ee')
        return
    inset = 5
    for y in range(rh):
        t = y / max(1, rh - 1)
        xi = int(round(inset * (1 - t)))
        for x in range(x0 + xi, x0 + pw - xi):
            # horizontal gradient (lit from the left) + shingle bands
            gx = (x - x0) / pw
            k = 3.4 - gx * 1.6
            band = (y % 5)
            if band == 4:
                k -= 1.4
            elif band == 0:
                k += 0.5
            if (x + (y // 5) * 3) % 7 == 0 and band not in (0, 4):
                k -= 0.8
            k = int(np.clip(round(k), 0, 5))
            s.px(x, y0 + y, r[k])
    # ridge cap
    for x in range(x0 + inset, x0 + pw - inset):
        s.px(x, y0, r[5]); s.px(x, y0 + 1, r[4])
    # eave
    s.hline(x0, x0 + pw - 1, y0 + rh - 1, r[0])
    s.hline(x0, x0 + pw - 1, y0 + rh - 2, r[1])
    if snow:
        for y in range(0, rh // 2):
            t = y / max(1, rh - 1)
            xi = int(round(inset * (1 - t)))
            for x in range(x0 + xi, x0 + pw - xi):
                if y < rh // 2 - 1 - ((x * 7) % 3 == 0):
                    s.px(x, y0 + y, '#f4f8ff' if y > 0 else '#ffffff')
        s.hline(x0 + inset, x0 + pw - inset - 1, y0, '#ffffff')
        for x in range(x0 + 2, x0 + pw - 2, 5):
            s.vline(x, y0 + rh - 1, y0 + rh + 1, '#dff0ff')


def _wall(s, x0, y0, pw, wh, style):
    base = WALLS[style]
    r = ramp(base, 5, 0.09)
    s.rect(x0, y0, pw, wh, r[2])
    if style in ('plaster', 'white', 'cream', 'mint', 'sand', 'timber'):
        for i in range(pw * wh // 40):
            x = x0 + int(h2(i, 3, len(style)) * pw)
            y = y0 + int(h2(i, 7, len(style)) * wh)
            s.px(x, y, r[1] if i % 2 else r[3])
    if style == 'timber':
        beam = '#5a3a2a'
        s.hline(x0, x0 + pw - 1, y0 + 1, beam)
        for x in range(x0, x0 + pw, 16):
            s.vline(x, y0, y0 + wh - 1, beam); s.vline(x + 15, y0, y0 + wh - 1, beam)
        for x in range(x0, x0 + pw - 1, 16):
            s.line(x + 1, y0 + wh - 3, x + 7, y0 + 3, beam)
    if style in ('wood', 'log'):
        for y in range(y0, y0 + wh):
            if (y - y0) % 4 == 3:
                s.hline(x0, x0 + pw - 1, y, r[0])
            elif (y - y0) % 4 == 0:
                s.hline(x0, x0 + pw - 1, y, r[3])
        if style == 'log':
            for y in range(y0 + 1, y0 + wh, 4):
                s.px(x0, y, r[4]); s.px(x0 + pw - 1, y, r[0])
    if style == 'brick':
        for y in range(y0, y0 + wh):
            if (y - y0) % 4 == 3:
                s.hline(x0, x0 + pw - 1, y, r[1])
            else:
                off = 0 if ((y - y0) // 4) % 2 else 4
                for x in range(x0 + off, x0 + pw, 8):
                    s.px(x, y, r[1])
            if (y - y0) % 4 == 0:
                s.hline(x0, x0 + pw - 1, y, r[3])
    if style in ('stone', 'dark'):
        for y in range(y0, y0 + wh):
            if (y - y0) % 6 == 5:
                s.hline(x0, x0 + pw - 1, y, r[0])
            else:
                off = 0 if ((y - y0) // 6) % 2 else 6
                for x in range(x0 + off, x0 + pw, 12):
                    s.px(x, y, r[0])
            if (y - y0) % 6 == 0:
                s.hline(x0, x0 + pw - 1, y, r[3])
    if style == 'glass':
        for x in range(x0, x0 + pw, 8):
            s.vline(x, y0, y0 + wh - 1, '#5a6a80')
        for y in range(y0, y0 + wh, 6):
            s.hline(x0, x0 + pw - 1, y, '#5a6a80')
        for i in range(0, pw, 8):
            s.line(x0 + i + 2, y0 + 5, x0 + i + 5, y0 + 1, '#e8f6ff')
    # shadow under the eave
    s.hline(x0, x0 + pw - 1, y0, shift(r[0], -0.1))
    s.hline(x0, x0 + pw - 1, y0 + 1, r[1])
    # foundation
    st = ramp('#8e8a86', 4, 0.1)
    s.rect(x0, y0 + wh - 3, pw, 3, st[1]); s.hline(x0, x0 + pw - 1, y0 + wh - 3, st[3])


def _window(s, x, y, w=10, h=9, frame='#6b4a36', lit=False, box=None):
    s.rect(x - 1, y - 1, w + 2, h + 2, frame)
    glass = ['#274a7a', '#3a6aa8', '#5b90c8', '#8cc0ec']
    for yy in range(h):
        for xx in range(w):
            k = 3 - int((yy / h) * 2.5 + (xx / w) * 0.8)
            s.px(x + xx, y + yy, glass[max(0, min(3, k))])
    s.line(x + 1, y + h - 3, x + 4, y + 1, '#d8f0ff')
    s.vline(x + w // 2, y, y + h - 1, frame); s.hline(x, x + w - 1, y + h // 2, frame)
    s.rect(x - 2, y + h + 1, w + 4, 1, shift(C(frame)[:3], 0.15))
    if box:
        s.rect(x - 1, y + h + 2, w + 2, 3, box)
        for i in range(0, w, 3):
            s.px(x + i, y + h + 1, '#ff6b8a' if i % 2 else '#ffd54a')


def _door(s, x, y, w, h, style='wood'):
    if style == 'glass':
        s.rect(x - 1, y - 1, w + 2, h + 1, '#5a6a80')
        for xx in range(w):
            for yy in range(h):
                s.px(x + xx, y + yy, '#8cc8f0' if (xx + yy) % 7 else '#d8f0ff')
        s.vline(x + w // 2, y, y + h - 1, '#5a6a80')
        s.rect(x, y + h - 2, w, 2, '#3a4454')
        return
    col = {'wood': '#7a4a2e', 'dark': '#3a2c3a', 'metal': '#4a5260', 'red': '#9a3a2e', 'blue': '#2e4a7a'}[style]
    r = ramp(col, 4, 0.1)
    s.rect(x - 1, y - 1, w + 2, h + 1, r[0])
    s.rect(x, y, w, h, r[2])
    s.rect(x + 1, y + 1, w - 2, h // 2 - 2, r[3]); s.rect(x + 1, y + h // 2, w - 2, h // 2 - 2, r[1])
    s.px(x + w - 3, y + h // 2, '#f0d24a')
    s.rect(x - 1, y + h - 1, w + 2, 1, '#3a3036')


@lru_cache(None)
def building(kind, w=5, h=4, roof='red', wall='plaster', door=None, snow=False, label=None,
             emblem=None, emblem_col=None, chimney=True, variant=0):
    pw, ph = w * T, h * T
    over = 10
    s = Spr(pw, ph + over)
    oy = over
    door_col = door if door is not None else w // 2
    lights = []
    wall_rows = 2 if h >= 4 else 1
    if kind in ('arena', 'hall', 'chapel', 'lab'):
        wall_rows = max(2, h - 2)
    rh = (h - wall_rows) * T + 4
    wy = oy + (h - wall_rows) * T
    wh = wall_rows * T
    # ground shadow strip
    s.rect(1, oy + ph - 1, pw - 2, 1, (18, 24, 32, 90))
    _wall(s, 0, wy, pw, wh, wall)
    roof_style = 'flat' if kind in ('hall', 'lab') else 'slope'
    _roof(s, 0, oy - 6, pw, rh + 2, ROOFS.get(roof, roof), snow=snow, style=roof_style)
    if chimney and kind == 'house':
        cx = pw - 14 if variant % 2 == 0 else 8
        s.rect(cx, oy - 9, 6, 9, '#9a5a44'); s.rect(cx, oy - 9, 6, 2, '#c0785a'); s.rect(cx - 1, oy - 10, 8, 2, '#6a3a2e')
    # door
    dw, dh = (10, 14) if kind not in ('haven', 'arena', 'hall', 'chapel') else (14, 15)
    dx = door_col * T + (T - dw) // 2
    if kind in ('arena', 'chapel'):
        dx = door_col * T + (T - dw) // 2
    dy = oy + ph - dh - 1
    door_style = {'haven': 'glass', 'hall': 'glass', 'lab': 'glass', 'arena': 'metal', 'chapel': 'dark'}.get(kind, 'wood')
    if kind == 'house' and variant % 3 == 1:
        door_style = 'blue'
    elif kind == 'house' and variant % 3 == 2:
        door_style = 'red'
    # step
    s.rect(dx - 2, oy + ph - 2, dw + 4, 2, '#b8b2a6')
    _door(s, dx, dy, dw, dh, door_style)
    # windows on the bottom wall row (skip the door column)
    frame = '#ffffff' if wall in ('brick', 'stone', 'dark', 'wood', 'log') else '#6b4a36'
    for col in range(w):
        if abs(col - door_col) < (1 if dw <= 12 else 1):
            continue
        if kind in ('arena', 'chapel') and col in (0, w - 1):
            continue
        wx = col * T + 3
        wy2 = oy + ph - T + 1
        if kind in ('haven',) and abs(col - door_col) == 1:
            continue
        _window(s, wx, wy2 - 2, frame=frame, box=('#4a9a52' if kind == 'house' and variant % 2 == 0 else None))
        lights.append((wx + 5, wy2 + 2))
    if wall_rows >= 2:
        for col in range(w):
            if kind == 'haven' and col in (door_col - 1, door_col, door_col + 1):
                continue
            if kind in ('arena', 'chapel') and col % 2 == 0:
                continue
            wx = col * T + 3
            wy2 = wy + 4
            if wy2 + 12 < oy + ph - T:
                _window(s, wx, wy2, frame=frame)
                lights.append((wx + 5, wy2 + 4))
    # signage
    if kind == 'haven':
        # emblem plate above the doors
        px0 = door_col * T - 8
        s.rect(px0, wy + 2, 32, 11, '#ffffff'); s.rect(px0, wy + 12, 32, 1, '#9aa6b4')
        icon(s, 'haven', px0 + 7, wy + 7, '#e2555f')
        text_small(s, px0 + 13, wy + 5, 'HAVEN', '#2a8a84')
    if kind == 'arena':
        col = TYPE_COL.get(emblem_col or 'Nature', '#e0503a')
        bx = door_col * T - 5
        s.rect(bx, wy - 2, 26, 16, col); s.rect(bx, wy - 2, 26, 2, shift(hx(col), 0.15))
        s.rect(bx + 2, wy + 14, 22, 3, shift(hx(col), -0.15))
        icon(s, emblem or 'star', bx + 13, wy + 6, '#ffffff')
        if label:
            tw = text_width(label)
            s.rect((pw - tw) // 2 - 3, oy - 4, tw + 6, 9, '#2a2838')
            text_small(s, (pw - tw) // 2, oy - 2, label, '#ffd65c')
    if kind == 'lab':
        s.rect(pw - 26, oy - 4, 20, 6, '#3a4a6a')
        for x in range(pw - 25, pw - 7, 3):
            s.vline(x, oy - 3, oy + 1, '#6a8ac0')
        s.rect(10, oy - 9, 2, 8, '#8a8f99'); s.shaded_ellipse(11, oy - 10, 5, 3, ramp('#c8ccd4', 4, 0.12))
        if label:
            tw = text_width(label)
            s.rect(door_col * T + 8 - tw // 2 - 3, wy + 2, tw + 6, 9, '#ffffff')
            text_small(s, door_col * T + 8 - tw // 2, wy + 4, label, '#3a4a6a')
    if kind in ('hall', 'chapel') and label:
        tw = text_width(label)
        s.rect(door_col * T + 8 - tw // 2 - 3, wy + 2, tw + 6, 9, '#2a2838')
        text_small(s, door_col * T + 8 - tw // 2, wy + 4, label, '#ffd65c')
    if kind == 'chapel':
        # spire
        sp = ramp('#4a4460', 5, 0.12)
        cx = door_col * T + 8
        s.poly([(cx - 6, oy - 4), (cx, oy - 10), (cx + 6, oy - 4)], sp[2])
        s.rect(cx - 1, oy - 10, 2, 1, '#6fe0c8')
    s.outline(None, darken=0.3)
    return dict(spr=s, ox=0, oy=oy, fw=w, fh=h, door=(door_col, h - 1), lights=lights)


@lru_cache(None)
def lighthouse():
    s = Spr(32, 96)
    oy = 48
    st = ramp('#eeeeee', 5, 0.1)
    for y in range(oy - 36, oy + 32):
        t = (y - (oy - 36)) / 68
        half = int(8 + 5 * t)
        for x in range(16 - half, 16 + half):
            band = ((y - (oy - 36)) // 10) % 2
            base = '#e24a4a' if band else '#f2f2f2'
            k = 0.12 if x < 16 - half // 3 else (-0.12 if x > 16 + half // 3 else 0)
            s.px(x, y, shift(hx(base), k))
    s.rect(9, oy - 46, 14, 10, '#fff3b0'); s.rect(8, oy - 47, 16, 2, '#3a3848'); s.rect(8, oy - 37, 16, 2, '#3a3848')
    s.poly([(8, oy - 47), (16, oy - 54), (24, oy - 47)], '#c8473f')
    _door(s, 11, oy + 17, 10, 14, 'dark')
    s.outline(None, darken=0.3)
    return dict(spr=s, ox=0, oy=oy, fw=2, fh=2, door=(0, 1), lights=[(16, oy - 41)])


@lru_cache(None)
def cave_mouth(kind='rock'):
    s = Spr(48, 36)
    oy = 4
    rr = ramp('#8e8a86' if kind == 'rock' else '#6d5a4e', 6, 0.13)
    s.poly([(0, oy + 32), (4, oy + 6), (14, oy - 2), (34, oy - 2), (44, oy + 6), (48, oy + 32)], rr[3])
    for y in range(oy, oy + 32):
        for x in range(48):
            if s.opaque(x, y) and (x * 3 + y * 5) % 11 == 0:
                s.px(x, y, rr[2])
    s.poly([(15, oy + 32), (16, oy + 14), (20, oy + 8), (28, oy + 8), (32, oy + 14), (33, oy + 32)], '#0e0c14')
    s.poly([(17, oy + 32), (18, oy + 16), (21, oy + 11), (27, oy + 11), (30, oy + 16), (31, oy + 32)], '#1a1622')
    s.outline(None, darken=0.3)
    return dict(spr=s, ox=0, oy=oy, fw=3, fh=2, door=(1, 1), lights=[])
