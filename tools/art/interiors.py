"""Interior rendering: floors, walls, furniture stamps."""
import numpy as np
from functools import lru_cache
from spr import Spr, C
from pal import hx, ramp, shift, h2
from buildings import icon, text_small, text_width

T = 16
WOOD = ramp('#a4703f', 5, 0.13)
DARKWOOD = ramp('#6e4630', 5, 0.12)
METAL = ramp('#8a93a6', 5, 0.12)

FLOORS = {
    'wood':   ('#c8955c', 'planks'),
    'dark':   ('#8a5c3c', 'planks'),
    'tile':   ('#dcd8cc', 'tiles'),
    'mint':   ('#cfe8dc', 'tiles'),
    'stone':  ('#9a968e', 'stones'),
    'lab':    ('#e2e6ec', 'tiles'),
    'carpet': ('#b8505a', 'carpet'),
    'arena':  ('#b8a88a', 'stones'),
    'chapel': ('#4a4660', 'stones'),
    'ice':    ('#cfe4f4', 'tiles'),
    'ancient': ('#86806c', 'stones'),
}
WALLS = {
    'cream': ('#efe0c0', 'stripe'), 'blue': ('#b8c8e8', 'stripe'), 'green': ('#c8dcb8', 'stripe'),
    'pink': ('#ecc8c8', 'stripe'), 'white': ('#eceff2', 'panel'), 'wood': ('#b88a5a', 'planks'),
    'stone': ('#a8a298', 'blocks'), 'dark': ('#4e4a62', 'blocks'), 'teal': ('#bfe4de', 'panel'),
    'ice': ('#d8ecf8', 'blocks'), 'red': ('#d8a098', 'stripe'), 'ancient': ('#56524a', 'blocks'),
}


@lru_cache(None)
def floor_tile(kind, variant=0):
    base, pat = FLOORS[kind]
    r = ramp(base, 5, 0.08)
    s = Spr(T, T)
    s.rect(0, 0, T, T, r[2])
    if pat == 'planks':
        for y in range(T):
            if y % 8 == 7:
                s.hline(0, 15, y, r[0])
            if y % 8 == 0:
                s.hline(0, 15, y, r[3])
        for band in range(2):
            x = (band * 7 + variant * 5) % T
            s.vline(x, band * 8, band * 8 + 6, r[1])
        for i in range(3):
            s.px(int(h2(i, variant, 3) * 16), int(h2(variant, i, 5) * 16), r[1])
    elif pat == 'tiles':
        s.rect(0, 0, T, T, r[2] if variant % 2 else r[3])
        s.hline(0, 15, 15, r[0]); s.vline(15, 0, 15, r[0])
        s.hline(0, 14, 0, r[4]); s.vline(0, 0, 14, r[4])
    elif pat == 'stones':
        for y in range(T):
            if y % 8 == 7:
                s.hline(0, 15, y, r[0])
            off = 0 if (y // 8) % 2 else 8
            s.px(off, y, r[0]) if y % 8 != 7 else None
        s.px(3 + variant, 3, r[3]); s.px(11, 10 - variant, r[3])
    elif pat == 'carpet':
        for y in range(T):
            for x in range(T):
                if (x + y) % 4 == 0:
                    s.px(x, y, r[3])
    return s


@lru_cache(None)
def puzzle_tile(kind, variant=0):
    """Trial puzzle floor tiles: slippery ice, water currents (with an arrow) and ice rocks."""
    s = Spr(T, T)
    if kind == 'ice':
        r = ramp('#a8dcf4', 5, 0.08)
        s.rect(0, 0, T, T, r[3])
        for k in range(3):                         # glossy diagonal streaks
            x0 = (variant * 5 + k * 6) % 16
            for j in range(4):
                s.px((x0 + j) % 16, (12 - k * 5 + j) % 16, r[4])
                s.px((x0 + j) % 16, (13 - k * 5 + j) % 16, '#ffffff')
        s.hline(0, 15, 15, r[1]); s.vline(15, 0, 15, r[2])
        s.px(3 + variant, 4, '#ffffff')
    elif kind.startswith('current_'):
        d = kind[8:]
        r = ramp('#2f7fc8', 5, 0.1)
        s.rect(0, 0, T, T, r[2])
        for k in range(4):
            s.px((variant * 7 + k * 4) % 16, (k * 5 + variant * 3) % 16, r[3])
        # a white chevron pointing downstream
        pts = [(4, 10), (5, 9), (6, 8), (7, 7), (8, 6), (9, 7), (10, 8), (11, 9), (12, 10)]
        pts += [(x, y + 1) for (x, y) in pts]
        rot = {'up': lambda x, y: (x, y), 'down': lambda x, y: (x, 15 - y),
               'left': lambda x, y: (y, x), 'right': lambda x, y: (15 - y, x)}[d]
        for (x, y) in pts:
            xx, yy = rot(x, y - 1)
            s.px(xx, yy, '#e8f6ff')
        s.hline(0, 15, 0, r[1]) if d in ('left', 'right') else s.vline(0, 0, 15, r[1])
    elif kind == 'rift_glass':
        r = ramp('#7a5ad0', 5, 0.1)
        s.rect(0, 0, T, T, r[2])
        for k in range(3):
            x0 = (variant * 5 + k * 6) % 16
            for j in range(4):
                s.px((x0 + j) % 16, (12 - k * 5 + j) % 16, r[4])
        s.px(3 + variant, 4, '#e8d8ff'); s.px(11, 10 - variant, '#e8d8ff')
        s.hline(0, 15, 15, r[0]); s.vline(15, 0, 15, r[1])
    elif kind == 'pool':
        r = ramp('#1f4f8a', 5, 0.1)
        s.rect(0, 0, T, T, r[1])
        for k in range(3):
            s.hline((variant * 5 + k * 5) % 12, (variant * 5 + k * 5) % 12 + 3, (k * 5 + 3) % 16, r[2])
    elif kind == 'ice_rock':
        r = ramp('#8fb8d8', 5, 0.14)
        s.shaded_ellipse(8, 9, 6.5, 5.5, r)
        s.px(5, 6, '#ffffff'); s.px(6, 5, '#ffffff')
        s.outline(None, darken=0.35)
    return s


@lru_cache(None)
def block_tile(floor, up, down):
    """A solid barrier block for Trial rooms, styled to the room (metal in the lab, stone elsewhere)."""
    base = {'lab': '#9aa4b8', 'arena': '#6a5a4a', 'chapel': '#3a3650', 'ice': '#9cc0dc', 'tile': '#8a9aa8'}.get(floor, '#8a8478')
    r = ramp(base, 5, 0.12)
    s = Spr(T, T)
    s.rect(0, 0, T, T, r[2])
    if floor == 'lab':
        s.rect(2, 2, 12, 12, r[3]); s.rect(3, 3, 10, 10, r[2])
        for (x, y) in [(3, 3), (12, 3), (3, 12), (12, 12)]:
            s.px(x, y, r[4])
    else:
        s.hline(0, 15, 7, r[1]); s.vline(7, 0, 7, r[1]); s.vline(3, 8, 15, r[1]); s.vline(12, 8, 15, r[1])
    if not up:
        s.hline(0, 15, 0, r[4]); s.hline(0, 15, 1, r[3])
    if not down:
        s.hline(0, 15, 15, r[0]); s.hline(0, 15, 14, r[0])
    return s


@lru_cache(None)
def hedge_tile(up, down, left, right):
    """A clipped garden hedge block (Moss Trial maze)."""
    r = ramp('#3f8a3a', 5, 0.14)
    s = Spr(T, T)
    s.rect(0, 0, T, T, r[2])
    for (x, y, k) in [(2, 3, 3), (7, 2, 4), (12, 4, 3), (4, 8, 1), (10, 9, 3), (6, 12, 1), (13, 12, 4), (1, 13, 3)]:
        s.px(x, y, r[k]); s.px(x + 1, y, r[k]); s.px(x, y + 1, r[max(0, k - 1)])
    if not up:
        s.hline(0, 15, 0, r[4]); s.hline(0, 15, 1, r[3])
    if not down:
        s.hline(0, 15, 15, r[0]); s.hline(0, 15, 14, r[1])
    if not left:
        s.vline(0, 0, 15, r[1])
    if not right:
        s.vline(15, 0, 15, r[0])
    return s


@lru_cache(None)
def wall_tile(kind, row, of_rows, window=False):
    """row 0..of_rows-1 from the top of the wall face."""
    base, pat = WALLS[kind]
    r = ramp(base, 5, 0.09)
    s = Spr(T, T)
    s.rect(0, 0, T, T, r[2])
    if pat == 'stripe':
        for x in range(0, T, 4):
            s.vline(x, 0, 15, r[3])
    elif pat == 'panel':
        s.vline(0, 0, 15, r[1]); s.vline(8, 0, 15, r[3])
    elif pat == 'planks':
        for y in range(0, T, 4):
            s.hline(0, 15, y, r[1])
    elif pat == 'blocks':
        for y in range(T):
            if y % 8 == 7:
                s.hline(0, 15, y, r[0])
            off = 0 if (y // 8) % 2 else 8
            if y % 8 != 7:
                s.px(off, y, r[0])
    if row == 0:
        s.rect(0, 0, T, 3, shift(r[0], -0.2)); s.hline(0, 15, 3, r[4])
    if row == of_rows - 1:
        s.rect(0, 12, T, 4, DARKWOOD[1]); s.hline(0, 15, 12, DARKWOOD[3]); s.hline(0, 15, 15, DARKWOOD[0])
    if window:
        s.rect(2, 3 if row == 0 else 1, 12, 10, '#6b4a36')
        for yy in range(8):
            for xx in range(10):
                k = 3 - int(yy / 8 * 2.5 + xx / 10)
                s.px(3 + xx, (4 if row == 0 else 2) + yy, ['#274a7a', '#3a6aa8', '#6aa0d8', '#a8d8f8'][max(0, min(3, k))])
        s.line(4, 10 if row == 0 else 8, 7, 5 if row == 0 else 3, '#e8f8ff')
        s.vline(8, 4 if row == 0 else 2, 11 if row == 0 else 9, '#6b4a36')
    return s


@lru_cache(None)
def wall_window():
    """A 16×20 window with curtains, drawn over the wall face."""
    s = Spr(16, 20)
    s.rect(1, 0, 14, 18, '#6b4a36')
    for yy in range(16):
        for xx in range(12):
            k = 3 - int(yy / 16 * 2.6 + xx / 12)
            s.px(2 + xx, 1 + yy, ['#274a7a', '#3a6aa8', '#6aa0d8', '#a8d8f8'][max(0, min(3, k))])
    s.line(3, 13, 8, 3, '#e8f8ff'); s.line(4, 14, 9, 4, '#cfeaff')
    s.vline(8, 1, 16, '#6b4a36'); s.hline(2, 13, 8, '#6b4a36')
    s.rect(0, 17, 16, 2, '#8a6a4e'); s.hline(0, 15, 17, '#a8886a')
    for yy in range(1, 14):
        s.px(2, yy, '#e8d8c8'); s.px(13, yy, '#e8d8c8')
    s.rect(2, 1, 12, 1, '#c84a4a')
    return s


def _sh(s, x, y, w, h=2):
    for xx in range(w):
        for yy in range(h):
            if y + yy < s.h and x + xx < s.w and s.a[y + yy, x + xx, 3] == 0:
                s.a[y + yy, x + xx] = (20, 16, 30, 70)


@lru_cache(None)
def furniture(name, variant=0):
    """Returns (Spr, ox, oy, fw, fh). Sprite origin = footprint top-left at (ox, oy)."""
    if name == 'bed':
        s = Spr(16, 34); oy = 2
        col = ['#3f6fc8', '#c8473f', '#4a9a52', '#8a52b0'][variant % 4]
        r = ramp(col, 5, 0.12)
        s.rect(1, oy - 2, 14, 6, DARKWOOD[2]); s.rect(1, oy - 2, 14, 1, DARKWOOD[4])
        s.rect(1, oy + 3, 14, 26, DARKWOOD[1])
        s.rect(2, oy + 4, 12, 7, '#f4f4f0'); s.rect(3, oy + 5, 10, 4, '#ffffff')
        s.rect(2, oy + 11, 12, 16, r[2]); s.rect(2, oy + 11, 12, 2, r[3])
        for y in range(oy + 14, oy + 27, 4):
            s.hline(2, 13, y, r[1])
        s.outline(None, darken=0.3)
        _sh(s, 1, oy + 30, 14)
        return s, 0, oy, 1, 2
    if name == 'table':
        w = 2 if variant == 0 else (3 if variant == 2 else 1)
        s = Spr(16 * w, 24); oy = 6
        s.rect(1, oy - 2, 16 * w - 2, 10, WOOD[2]); s.rect(1, oy - 2, 16 * w - 2, 2, WOOD[4]); s.rect(1, oy + 7, 16 * w - 2, 2, WOOD[0])
        s.rect(2, oy + 9, 2, 5, DARKWOOD[1]); s.rect(16 * w - 4, oy + 9, 2, 5, DARKWOOD[1])
        if w >= 2:
            s.rect(8, oy, 6, 4, '#f0f0f0'); s.rect(9, oy + 1, 4, 2, '#e24a4a')
        s.outline(None, darken=0.3)
        return s, 0, oy, w, 1
    if name == 'chair':
        s = Spr(16, 20); oy = 4
        s.rect(4, oy - 3, 8, 8, WOOD[2]); s.rect(4, oy - 3, 8, 2, WOOD[4])
        s.rect(3, oy + 5, 10, 4, WOOD[3]); s.rect(4, oy + 9, 2, 4, DARKWOOD[1]); s.rect(10, oy + 9, 2, 4, DARKWOOD[1])
        s.outline(None, darken=0.3)
        return s, 0, oy, 1, 1
    if name == 'bookshelf':
        s = Spr(16, 32); oy = 16
        s.rect(0, 0, 16, 31, DARKWOOD[2]); s.rect(0, 0, 16, 2, DARKWOOD[4]); s.rect(1, 2, 14, 28, DARKWOOD[0])
        cols = ['#c8473f', '#3f6fc8', '#4a9a52', '#e0b040', '#8a52b0', '#e07a3a', '#2aa19a']
        for shelf, y0 in enumerate((3, 12, 21)):
            x = 2
            while x < 14:
                bw = 1 + int(h2(x, shelf, variant) * 2)
                bh = 6 + int(h2(shelf, x, variant + 1) * 2)
                c = cols[int(h2(x, shelf + 5, variant) * 7)]
                s.rect(x, y0 + 8 - bh, bw, bh, c); s.px(x, y0 + 8 - bh, shift(hx(c), 0.2))
                x += bw + (1 if h2(x, 9, shelf) < 0.2 else 0)
            s.rect(1, y0 + 8, 14, 1, DARKWOOD[3])
        s.outline(None, darken=0.3)
        return s, 0, oy, 1, 1
    if name == 'plant':
        s = Spr(16, 28); oy = 12
        s.rect(4, oy + 6, 8, 8, '#b8603a'); s.rect(3, oy + 5, 10, 2, '#d8805a'); s.rect(4, oy + 13, 8, 1, '#7a3a2a')
        leaves = ramp('#3f9a45', 5, 0.14)
        for (cx, cy, rx, ry) in [(8, oy - 2, 6, 7), (4, oy + 2, 4, 3), (12, oy + 2, 4, 3), (8, oy - 8, 3, 4)]:
            s.shaded_ellipse(cx, cy, rx, ry, leaves)
        s.outline(None, darken=0.3)
        return s, 0, oy, 1, 1
    if name == 'tv':
        s = Spr(16, 24); oy = 8
        s.rect(1, oy + 2, 14, 12, DARKWOOD[2]); s.rect(1, oy + 2, 14, 2, DARKWOOD[4])
        s.rect(2, oy - 6, 12, 9, '#2a2a34'); s.rect(3, oy - 5, 10, 7, '#3a6aa8'); s.line(4, oy, 7, oy - 4, '#a8d8f8')
        s.outline(None, darken=0.3)
        return s, 0, oy, 1, 1
    if name == 'pc':
        s = Spr(16, 26); oy = 10
        s.rect(1, oy + 2, 14, 12, METAL[2]); s.rect(1, oy + 2, 14, 2, METAL[4])
        s.rect(2, oy - 8, 12, 10, '#2a2f3a'); s.rect(3, oy - 7, 10, 8, '#1e7a70')
        for y in range(oy - 6, oy, 2):
            s.hline(4, 4 + (y * 3) % 7, y, '#7ff0d8')
        s.rect(4, oy + 5, 8, 2, '#4a5060')
        s.outline(None, darken=0.3)
        return s, 0, oy, 1, 1
    if name == 'healer':
        s = Spr(32, 30); oy = 14
        s.rect(1, oy - 2, 30, 16, METAL[2]); s.rect(1, oy - 2, 30, 2, METAL[4])
        s.rect(3, oy - 12, 26, 10, '#dfe6ee'); s.rect(3, oy - 12, 26, 1, '#ffffff')
        for i in range(6):
            cx = 6 + i * 4
            s.shaded_ellipse(cx, oy - 7, 1.8, 1.8, ramp('#e2555f', 4, 0.15))
        s.rect(12, oy + 3, 8, 6, '#2a2f3a'); s.rect(13, oy + 4, 6, 4, '#6fe0c8')
        s.outline(None, darken=0.3)
        return s, 0, oy, 2, 1
    if name == 'counter':
        w = variant or 3
        s = Spr(16 * w, 24); oy = 8
        s.rect(0, oy - 4, 16 * w, 6, '#f2efe8'); s.rect(0, oy - 4, 16 * w, 1, '#ffffff')
        s.rect(0, oy + 2, 16 * w, 13, WOOD[2]); s.rect(0, oy + 2, 16 * w, 2, WOOD[1])
        for x in range(0, 16 * w, 8):
            s.vline(x, oy + 4, oy + 14, WOOD[3])
        s.outline(None, darken=0.3)
        return s, 0, oy, w, 1
    if name == 'shelf':  # shop shelves with goods
        s = Spr(32, 32); oy = 16
        s.rect(0, 0, 32, 31, METAL[1]); s.rect(1, 1, 30, 29, METAL[3])
        cols = ['#e2555f', '#3d8bfd', '#f5c542', '#4caf50', '#7a5cc4']
        for shelf, y0 in enumerate((2, 12, 22)):
            for i in range(7):
                c = cols[(i + shelf * 2 + variant) % 5]
                s.rect(2 + i * 4, y0 + 2, 3, 6, c); s.px(2 + i * 4, y0 + 2, '#ffffff')
            s.rect(1, y0 + 8, 30, 1, METAL[0])
        s.outline(None, darken=0.3)
        return s, 0, oy, 2, 1
    if name == 'stairs_up':
        s = Spr(16, 16); oy = 0
        for i in range(4):
            s.rect(0, i * 4, 16, 4, WOOD[4 - i]); s.hline(0, 15, i * 4 + 3, WOOD[0])
        return s, 0, oy, 1, 1
    if name == 'stairs_down':
        s = Spr(16, 16); oy = 0
        s.rect(0, 0, 16, 16, '#1a1622')
        for i in range(3):
            s.rect(1, i * 5 + 1, 14, 3, DARKWOOD[3 - i])
        return s, 0, oy, 1, 1
    if name == 'mat':
        s = Spr(16, 16)
        s.rect(1, 4, 14, 10, '#b8505a'); s.rect(2, 5, 12, 8, '#d8707a'); s.hline(2, 13, 9, '#b8505a')
        return s, 0, 0, 1, 1
    if name == 'rug':
        w = 3
        s = Spr(48, 32)
        s.rect(0, 0, 48, 32, '#6a3a8a'); s.rect(2, 2, 44, 28, '#8a52b0'); s.rect(6, 6, 36, 20, '#6a3a8a')
        s.rect(8, 8, 32, 16, '#b07ad0')
        return s, 0, 0, 3, 2
    if name == 'fridge':
        s = Spr(16, 32); oy = 16
        s.rect(1, 0, 14, 30, '#e8ecf0'); s.rect(1, 0, 14, 1, '#ffffff'); s.hline(1, 14, 11, '#9aa6b4')
        s.rect(12, 3, 1, 5, '#6a7a8a'); s.rect(12, 14, 1, 7, '#6a7a8a')
        s.outline(None, darken=0.3)
        return s, 0, oy, 1, 1
    if name == 'stove':
        s = Spr(16, 24); oy = 8
        s.rect(1, oy - 4, 14, 18, '#d8dce4'); s.rect(1, oy - 4, 14, 3, '#3a3a44')
        s.px(4, oy - 3, '#e24a4a'); s.px(11, oy - 3, '#e24a4a')
        s.rect(3, oy + 3, 10, 7, '#2a2f3a')
        s.outline(None, darken=0.3)
        return s, 0, oy, 1, 1
    if name == 'machine':  # lab machine
        s = Spr(16, 32); oy = 16
        s.rect(1, 0, 14, 30, METAL[2]); s.rect(1, 0, 14, 2, METAL[4])
        s.rect(3, 4, 10, 6, '#1a2a3a')
        for y in range(5, 10, 2):
            s.hline(4, 4 + (y * 5) % 8, y, '#6fe0c8')
        for i, c in enumerate(['#e2555f', '#f5c542', '#4caf50']):
            s.px(4 + i * 3, 14, c)
        s.rect(3, 18, 10, 8, METAL[1])
        s.outline(None, darken=0.3)
        return s, 0, oy, 1, 1
    if name == 'capsule_table':  # starter selection table
        s = Spr(48, 26); oy = 8
        s.rect(1, oy - 4, 46, 12, '#e8ecf0'); s.rect(1, oy - 4, 46, 2, '#ffffff'); s.rect(1, oy + 7, 46, 2, '#9aa6b4')
        s.rect(3, oy + 9, 3, 7, METAL[1]); s.rect(42, oy + 9, 3, 7, METAL[1])
        from capsules import starter_ball
        for i, c in enumerate(['#4caf50', '#ff7a3d', '#3d8bfd']):   # the three starters' capsules
            cx = 10 + i * 14
            s.blit(starter_ball(c), cx - 5, oy - 7)
        s.outline(None, darken=0.3)
        return s, 0, oy, 3, 1
    if name == 'pad':  # Veil Trial warp pad
        s = Spr(16, 16)
        col = ['#8a6ad8', '#6fe0c8', '#f0c43a', '#e2555f'][variant % 4]
        s.ellipse(8, 8, 7, 5, '#2a2440')
        s.ellipse(8, 8, 6, 4, col)
        s.ellipse(8, 8, 4, 2.4, '#1a1628')
        s.ellipse(8, 8, 2.2, 1.2, '#ffffff')
        return s, 0, 0, 1, 1
    if name == 'statue':
        from decor import prop
        return prop('statue')
    if name == 'trophy':
        s = Spr(16, 26); oy = 10
        s.rect(2, oy + 4, 12, 10, DARKWOOD[2]); s.rect(2, oy + 4, 12, 2, DARKWOOD[4])
        s.shaded_ellipse(8, oy - 1, 4, 4, ramp('#f0c43a', 5, 0.15)); s.rect(7, oy + 2, 2, 3, '#c89a2a')
        s.outline(None, darken=0.3)
        return s, 0, oy, 1, 1
    if name == 'pillar':
        s = Spr(16, 40); oy = 24
        st = ramp('#b8b0a4', 5, 0.12)
        s.rect(3, 2, 10, 36, st[2]); s.rect(3, 2, 3, 36, st[3]); s.rect(10, 2, 3, 36, st[1])
        s.rect(1, 0, 14, 3, st[4]); s.rect(1, 36, 14, 3, st[1])
        s.outline(None, darken=0.3)
        return s, 0, oy, 1, 1
    if name == 'barrel':
        from decor import prop
        return prop('barrel')
    if name == 'crate':
        from decor import prop
        return prop('crate')
    if name == 'pot':
        from decor import prop
        return prop('pot')
    if name == 'crystal':
        from decor import prop
        return prop('crystal')
    if name == 'incubator':
        from ancient import incubator
        return incubator()
    if name == 'altar':
        s = Spr(48, 40); oy = 8
        st = ramp('#5a5078', 5, 0.14)
        s.rect(2, oy + 6, 44, 24, st[2]); s.rect(2, oy + 6, 44, 3, st[4]); s.rect(2, oy + 27, 44, 3, st[0])
        s.rect(10, oy - 6, 28, 13, st[3]); s.rect(10, oy - 6, 28, 2, st[4])
        icon(s, 'wave', 24, oy + 1, '#6fe0c8')
        s.outline(None, darken=0.3)
        return s, 0, oy, 3, 2
    if name == 'rail':
        # Trial-hall barrier: a brass post with a velvet rope. variant = colour * 4 + rope-left(1) + rope-right(2)
        # so rows join up and the ends at a gate stop neatly at the post.
        s = Spr(16, 26); oy = 10
        rope_col = ['#3f8a4a', '#2f6fb8', '#d0a020', '#6a4aa8', '#7ab8e0', '#b8402a'][(variant // 4) % 6]
        rope = ramp(rope_col, 5, 0.14)
        brass = ramp('#d8a840', 5, 0.14)
        sag = lambda t: 8 + int(round(5 * (1 - (1 - t) ** 2)))   # rope hangs lowest halfway between posts
        if variant & 1:
            for x in range(0, 8):
                y = sag(1 - x / 7.0)
                s.rect(x, y, 1, 2, rope[2]); s.px(x, y, rope[3])
        if variant & 2:
            for x in range(8, 16):
                y = sag((x - 8) / 7.0)
                s.rect(x, y, 1, 2, rope[2]); s.px(x, y, rope[3])
        s.rect(7, 6, 2, 16, brass[2]); s.vline(7, 6, 21, brass[3])
        s.shaded_ellipse(8, 5, 2, 2, brass)
        s.rect(5, 21, 6, 2, brass[1]); s.hline(5, 10, 21, brass[3])
        s.outline(None, darken=0.3)
        return s, 0, oy, 1, 1
    if name == 'banner':
        s = Spr(16, 32); oy = 16
        col = variant or '#e0503a'
        s.rect(2, 0, 12, 26, col); s.rect(2, 0, 12, 2, shift(hx(col), 0.2)); s.poly([(2, 26), (8, 31), (14, 26)], col)
        icon(s, 'star', 8, 10, '#ffffff')
        s.outline(None, darken=0.3)
        return s, 0, oy, 1, 1
    if name == 'globe':
        s = Spr(16, 26); oy = 10
        s.rect(4, oy + 6, 8, 8, DARKWOOD[2])
        s.shaded_ellipse(8, oy, 6, 6, ramp('#3d8bfd', 5, 0.15)); s.px(6, oy - 2, '#4caf50'); s.px(9, oy + 1, '#4caf50'); s.px(7, oy - 1, '#4caf50')
        s.outline(None, darken=0.3)
        return s, 0, oy, 1, 1
    raise KeyError(name)
