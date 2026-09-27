"""UI + item icon atlases: public/assets/ui/ui.png|json and sprites/icons.png|json."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
from spr import Spr, C
from pal import hx, ramp, shift
import decor as D
from buildings import icon, text_small, text_width

TYPES = {
    'Plain': '#a8a29a', 'Nature': '#4caf50', 'Ember': '#ff7a3d', 'Tide': '#3d8bfd', 'Static': '#f5c542',
    'Stone': '#b38b5d', 'Frost': '#7fd6f2', 'Wing': '#8fa8ff', 'Swarm': '#9bbf3a', 'Toxin': '#a560c8',
    'Brawl': '#d0503a', 'Mind': '#f06292', 'Umbra': '#5e4b8b', 'Iron': '#8e9aaf', 'Drake': '#6a4cd8', 'Fae': '#f7a8dc',
}


def pack(frames, cols=16):
    """frames: list of (name, Spr). Simple shelf packer."""
    W = 512
    x = y = 0
    shelf = 0
    pos = {}
    for name, s in frames:
        if x + s.w > W:
            x = 0; y += shelf + 1; shelf = 0
        pos[name] = (x, y, s.w, s.h)
        x += s.w + 1
        shelf = max(shelf, s.h)
    H = y + shelf + 1
    sheet = Spr(W, H)
    meta = {}
    for name, s in frames:
        px, py, w, h = pos[name]
        sheet.blit(s, px, py)
        meta[name] = {'frame': {'x': px, 'y': py, 'w': w, 'h': h}, 'rotated': False, 'trimmed': False,
                      'spriteSourceSize': {'x': 0, 'y': 0, 'w': w, 'h': h}, 'sourceSize': {'w': w, 'h': h}}
    return sheet, meta


def save_atlas(frames, path, name):
    sheet, meta = pack(frames)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    sheet.image().save(path, optimize=True)
    with open(path.replace('.png', '.json'), 'w') as f:
        json.dump({'frames': meta, 'meta': {'image': name, 'size': {'w': sheet.w, 'h': sheet.h}, 'scale': '1'}}, f)


def capsule(col, band='#2a2838', size=10, open_=False):
    s = Spr(size + 2, size + 2)
    r = size / 2
    top = ramp(col, 5, 0.15)
    bot = ramp('#eeeef4', 5, 0.1)
    c = r + 1
    s.shaded_ellipse(c, c, r, r, bot)
    ys = __import__('numpy').mgrid[0:s.h, 0:s.w]
    m = s.shaded_ellipse(c, c, r, r, top)
    # keep only the top half coloured
    for y in range(s.h):
        for x in range(s.w):
            if y >= c and m[y, x]:
                pass
    s2 = Spr(s.w, s.h)
    s2.shaded_ellipse(c, c, r, r, bot)
    for y in range(s.h):
        for x in range(s.w):
            if y < c - 0.5 and m[y, x]:
                s2.a[y, x] = s.a[y, x]
    s2.hline(1, s.w - 2, int(c), band)
    s2.px(int(c), int(c), '#ffffff'); s2.px(int(c) - 1, int(c), band); s2.px(int(c) + 1, int(c), band)
    s2.outline('#1c1a28')
    return s2


def bottle(col):
    s = Spr(16, 16)
    r = ramp(col, 5, 0.14)
    s.rect(6, 2, 4, 3, '#c8c8d4'); s.rect(6, 1, 4, 1, '#8a6a4a')
    s.shaded_ellipse(8, 10, 5, 5, r)
    s.rect(6, 4, 4, 3, r[3])
    s.px(6, 8, '#ffffff'); s.px(6, 9, '#ffffff')
    s.outline('#1c1a28')
    return s


def herb(col):
    s = Spr(16, 16)
    r = ramp(col, 5, 0.14)
    s.line(8, 14, 8, 5, '#4a7a3a')
    for (x, y, a) in [(8, 5, 0), (5, 8, 1), (11, 9, 2)]:
        s.shaded_ellipse(x, y, 3, 2.2, r)
    s.outline('#1c1a28')
    return s


def seed(col):
    s = Spr(16, 16)
    s.shaded_ellipse(8, 9, 4.5, 5.5, ramp(col, 5, 0.15))
    s.line(8, 4, 10, 1, '#4a7a3a'); s.px(11, 1, '#6aba4a')
    s.outline('#1c1a28')
    return s


def disc(col):
    s = Spr(16, 16)
    s.shaded_ellipse(8, 8, 6.5, 6.5, ramp(col, 5, 0.12))
    s.ellipse(8, 8, 2, 2, '#1c1a28'); s.ellipse(8, 8, 1, 1, '#e8e8f0')
    s.line(4, 6, 6, 4, '#ffffff')
    s.outline('#1c1a28')
    return s


def ui_frames():
    F = []
    # overworld bits
    F.append(('grass_front', D.tall_grass_front()))
    for k in range(3):
        F.append((f'grass_rustle_{k}', D.grass_rustle(k)))
        F.append((f'grass_rustle_e{k}', D.grass_rustle(k, True)))
    ball = Spr(16, 16); ball.blit(capsule('#e2555f', size=9), 2, 5); F.append(('item_ball', ball))
    br = Spr(16, 20)
    thorn = ramp('#4a6a2a', 5, 0.14)
    for (cx, cy, rx, ry) in [(8, 12, 7, 6), (5, 8, 4, 4), (11, 7, 4, 4)]:
        br.shaded_ellipse(cx, cy, rx, ry, thorn)
    for (x, y) in [(3, 5), (12, 4), (2, 12), (14, 11), (8, 3), (6, 15), (11, 16)]:
        br.px(x, y, '#c8a86a'); br.px(x, y - 1, '#e8d8a8')
    br.px(6, 9, '#c83a4a'); br.px(10, 12, '#c83a4a')
    br.outline(None, darken=0.3)
    F.append(('bramble', br))
    sk = Spr(22, 12)
    hull = ramp('#b4643c', 5, 0.14)
    sk.poly([(0, 3), (22, 3), (19, 11), (3, 11)], hull[2]); sk.hline(1, 20, 3, hull[4]); sk.hline(2, 19, 4, hull[3])
    sk.rect(4, 5, 14, 3, '#6b4a30')
    sk.outline(None, darken=0.3)
    F.append(('skiff', sk))
    # capsules for battle throws
    for name, col in [('capsule', '#e2555f'), ('prime_capsule', '#3d8bfd'), ('apex_capsule', '#f5c542'),
                      ('dusk_capsule', '#3a4a5a'), ('swift_capsule', '#4fc7b8'), ('covenant_capsule', '#6a4cd8')]:
        F.append((f'throw_{name}', capsule(col, size=10)))
    # type badges
    for t, col in TYPES.items():
        tw = text_width(t)
        w = max(34, tw + 8)
        s = Spr(w, 9)
        r = ramp(col, 4, 0.1)
        s.rect(1, 0, w - 2, 9, r[2]); s.rect(0, 1, w, 7, r[2])
        s.hline(1, w - 2, 0, r[3]); s.hline(1, w - 2, 8, r[0])
        text_small(s, (w - tw) // 2 + 1, 3, t, (20, 18, 30))
        text_small(s, (w - tw) // 2, 2, t, '#ffffff')
        F.append((f'type_{t}', s))
    # status badges
    for st, col, lab in [('burn', '#e2553a', 'BRN'), ('poison', '#a560c8', 'PSN'), ('toxic', '#7a3aa8', 'TOX'),
                         ('paralyze', '#e8b82a', 'PAR'), ('sleep', '#8a93a6', 'SLP'), ('freeze', '#5ab8e8', 'FRZ'), ('faint', '#5a3a4a', 'FNT')]:
        s = Spr(20, 9)
        s.rect(1, 0, 18, 9, col); s.rect(0, 1, 20, 7, col)
        text_small(s, 3, 2, lab, '#ffffff')
        F.append((f'st_{st}', s))
    # move categories
    for cat, col in [('phys', '#e2753a'), ('spec', '#5a8ae8'), ('status', '#9aa0b4')]:
        s = Spr(14, 9)
        s.rect(1, 0, 12, 9, col); s.rect(0, 1, 14, 7, col)
        if cat == 'phys':
            for i in range(4):
                s.px(4 + i, 2 + i, '#ffffff'); s.px(9 - i, 2 + i, '#ffffff')
        elif cat == 'spec':
            s.ellipse(7, 4.5, 2.5, 2.5, '#ffffff'); s.ellipse(7, 4.5, 1, 1, col)
        else:
            s.hline(4, 9, 3, '#ffffff'); s.hline(4, 9, 5, '#ffffff')
        F.append((f'cat_{cat}', s))
    # sigils 16×16
    for sid, (col, ic) in {'moss': ('#4caf50', 'leaf'), 'tide': ('#3d8bfd', 'drop'), 'spark': ('#f5c542', 'bolt'),
                           'veil': ('#7a5cc4', 'moon'), 'rime': ('#7fd6f2', 'flake'), 'wyrm': ('#e0503a', 'claw')}.items():
        s = Spr(16, 16)
        r = ramp(col, 5, 0.15)
        s.poly([(8, 0), (15, 4), (15, 11), (8, 15), (1, 11), (1, 4)], r[2])
        s.poly([(8, 2), (13, 5), (13, 10), (8, 13), (3, 10), (3, 5)], r[3])
        icon(s, ic, 8, 8, '#ffffff')
        s.outline('#1c1a28')
        F.append((f'sigil_{sid}', s))
        g = Spr(16, 16)
        g.poly([(8, 0), (15, 4), (15, 11), (8, 15), (1, 11), (1, 4)], '#2a2d44')
        g.poly([(8, 2), (13, 5), (13, 10), (8, 13), (3, 10), (3, 5)], '#343856')
        g.outline('#1c1a28')
        F.append((f'sigil_{sid}_empty', g))
    # menu icons 16×16
    def mi(name, fn):
        s = Spr(16, 16); fn(s); s.outline('#1c1a28'); F.append((f'menu_{name}', s))
    mi('party', lambda s: (s.shaded_ellipse(8, 9, 6, 6, ramp('#e2555f', 5, 0.15)), s.hline(2, 13, 9, '#1c1a28'), s.ellipse(8, 9, 1.5, 1.5, '#ffffff')))
    mi('bag', lambda s: (s.rect(3, 5, 10, 9, '#b87a3a'), s.rect(3, 5, 10, 2, '#d89a5a'), s.rect(6, 2, 4, 3, '#8a5a2a'), s.rect(7, 8, 2, 2, '#f0d24a')))
    mi('index', lambda s: (s.rect(3, 2, 10, 12, '#e2555f'), s.rect(4, 3, 8, 5, '#8ad8ff'), s.px(5, 10, '#ffffff'), s.px(7, 10, '#f5c542')))
    mi('card', lambda s: (s.rect(1, 4, 14, 9, '#3d8bfd'), s.rect(2, 5, 4, 5, '#f3cfae'), s.hline(8, 13, 6, '#ffffff'), s.hline(8, 12, 9, '#ffffff')))
    mi('save', lambda s: (s.rect(2, 2, 12, 12, '#5a6a9a'), s.rect(4, 2, 8, 5, '#e8ecf0'), s.rect(4, 9, 8, 5, '#2a2f4a')))
    mi('keys', lambda s: (s.rect(0, 3, 16, 10, '#4a5070'), s.rect(1, 4, 14, 8, '#6a7090'),
                          [s.rect(2 + i * 3, 5, 2, 2, '#e8ecf0') for i in range(4)],
                          [s.rect(3 + i * 3, 8, 2, 2, '#e8ecf0') for i in range(3)], s.rect(4, 11, 8, 1, '#e8ecf0')))
    mi('options', lambda s: (s.ellipse(8, 8, 5.5, 5.5, '#9aa0b4'), s.ellipse(8, 8, 2, 2, '#1c1a28'), [s.rect(7, 0, 2, 3, '#9aa0b4'), s.rect(7, 13, 2, 3, '#9aa0b4'), s.rect(0, 7, 3, 2, '#9aa0b4'), s.rect(13, 7, 3, 2, '#9aa0b4')]))
    mi('map', lambda s: (s.rect(2, 3, 12, 10, '#e8d8a8'), s.vline(6, 3, 12, '#b8a878'), s.vline(10, 3, 12, '#b8a878'), s.px(8, 7, '#e2555f'), s.px(4, 9, '#4caf50')))
    mi('exit', lambda s: (s.rect(4, 2, 8, 12, '#8a5a3a'), s.rect(5, 3, 6, 10, '#b87a4a'), s.px(9, 8, '#f0d24a')))
    # ── move animation sprites (mostly white/grey so the game tints them by move type) ──
    F.extend(fx_frames())
    # battle shadow ellipse
    sh = Spr(64, 14)
    import numpy as np
    ys, xs = np.mgrid[0:14, 0:64]
    d = ((xs + 0.5 - 32) / 32) ** 2 + ((ys + 0.5 - 7) / 7) ** 2
    sh.a[d <= 1] = (0, 0, 0, 90)
    F.append(('battle_shadow', sh))
    return F


def fx_frames():
    import math
    F = []
    W, L, M, D, O = '#ffffff', '#e8ecf4', '#c4cad8', '#8e96aa', '#3a3f52'
    def add(name, s, outline=None):
        if outline:
            s.outline(outline)
        F.append((f'fx_{name}', s))
    # crescent slash (32x32)
    s = Spr(32, 32)
    for a in range(0, 150):
        t = a / 150.0
        ang = math.radians(200 + 140 * t)
        w = math.sin(t * math.pi) * 3.2
        for r in [13 - w * 0.5 + k * 0.5 for k in range(int(w * 2) + 1)]:
            s.px(16 + math.cos(ang) * r, 16 + math.sin(ang) * r, W if r > 12 else L)
    add('slash', s)
    # three claw scratches (24x24)
    s = Spr(24, 24)
    for k in range(3):
        for i in range(18):
            x, y = 3 + i + k * 4 - 4, 3 + i
            w = 1 if i in (0, 17) else 2
            s.rect(x, y, w, 1, W if 3 < i < 15 else L)
    add('claw', s)
    # impact starburst (24x24)
    s = Spr(24, 24)
    pts = []
    for i in range(16):
        r = 11 if i % 2 == 0 else 5
        a = i * math.pi / 8
        pts.append((12 + math.cos(a) * r, 12 + math.sin(a) * r))
    s.poly(pts, L)
    s.shaded_ellipse(12, 12, 4, 4, [W, W, W, W, W])
    add('impact', s)
    # fist (16x16) and foot (16x16)
    s = Spr(16, 16)
    s.rect(3, 4, 10, 9, L); s.rect(3, 4, 10, 2, W)
    for k in range(4):
        s.vline(4 + k * 2 + (1 if k else 0), 5, 8, M)
    s.rect(1, 7, 3, 4, L)
    add('fist', s, O)
    s = Spr(16, 16)
    s.rect(5, 2, 5, 8, L); s.rect(3, 9, 11, 5, L); s.hline(3, 13, 13, M); s.rect(5, 2, 5, 2, W)
    add('foot', s, O)
    # jaw of teeth (32x12): the top jaw; flipped for the bottom
    s = Spr(32, 12)
    s.rect(0, 0, 32, 4, M)
    for k in range(8):
        s.poly([(k * 4, 3), (k * 4 + 4, 3), (k * 4 + 2, 11)], W)
    add('jaw', s, O)
    # rock chunks (not tinted)
    for n, (w, h) in enumerate([(12, 10), (9, 8), (16, 13)]):
        s = Spr(w, h)
        s.poly([(1, h * 0.5), (w * 0.3, 0.5), (w * 0.8, 1), (w - 1, h * 0.55), (w * 0.7, h - 1), (w * 0.2, h - 1)], '#8a7c6c')
        s.poly([(2, h * 0.45), (w * 0.35, 1.5), (w * 0.6, 2), (w * 0.4, h * 0.5)], '#b3a590')
        add(f'rock{n}', s, '#3a3026')
    # icicle shard (8x18), flame tongue (12x16), leaf (11x7), feather (13x6), needle (13x3)
    s = Spr(8, 18)
    s.poly([(4, 0), (7, 5), (5, 17), (3, 17), (1, 5)], L); s.vline(4, 1, 15, W)
    add('icicle', s, '#5a7a9a')
    s = Spr(12, 16)
    s.poly([(6, 0), (9, 5), (11, 10), (8, 15), (4, 15), (1, 10), (3, 5)], L)
    s.poly([(6, 5), (8, 10), (6, 14), (4, 10)], W)
    add('flame', s)
    s = Spr(11, 7)
    s.poly([(0, 3), (5, 0), (10, 3), (5, 6)], L); s.hline(1, 9, 3, M)
    add('leaf', s)
    s = Spr(13, 6)
    s.poly([(0, 3), (4, 0), (12, 2), (12, 4), (4, 6)], L); s.hline(1, 12, 3, M)
    add('feather', s)
    s = Spr(13, 3)
    s.hline(0, 9, 1, L); s.px(10, 1, W); s.px(11, 1, W); s.px(12, 1, W); s.hline(0, 3, 0, M); s.hline(0, 3, 2, M)
    add('needle', s)
    # bubble (10x10), orb (16x16), sparkle (9x9), heart (9x8), note (8x10), z (7x7), arrow (8x10), seed (5x6), cog (12x12)
    s = Spr(10, 10)
    s.ellipse(5, 5, 4.5, 4.5, L); s.ellipse(5, 5, 3.3, 3.3, (0, 0, 0, 0)) if False else None
    for y in range(10):
        for x in range(10):
            d = ((x + 0.5 - 5) ** 2 + (y + 0.5 - 5) ** 2) ** 0.5
            if 3.4 < d <= 4.6:
                s.px(x, y, L)
            elif d <= 3.4:
                s.px(x, y, (220, 235, 255, 70))
    s.px(3, 3, W); s.px(3, 4, W); s.px(4, 3, W)
    add('bubble', s)
    s = Spr(16, 16)
    for y in range(16):
        for x in range(16):
            d = ((x + 0.5 - 8) ** 2 + (y + 0.5 - 8) ** 2) ** 0.5
            if d <= 7.5:
                a = int(255 * max(0, 1 - d / 7.5) ** 0.6)
                s.px(x, y, (255, 255, 255, a))
    add('orb', s)
    s = Spr(9, 9)
    s.poly([(4.5, 0), (5.5, 3.5), (9, 4.5), (5.5, 5.5), (4.5, 9), (3.5, 5.5), (0, 4.5), (3.5, 3.5)], W)
    add('sparkle', s)
    s = Spr(9, 8)
    s.ellipse(2.5, 2.5, 2.5, 2.5, L); s.ellipse(6.5, 2.5, 2.5, 2.5, L); s.poly([(0, 3), (9, 3), (4.5, 8)], L); s.px(2, 1, W)
    add('heart', s, O)
    s = Spr(8, 10)
    s.ellipse(2.5, 8, 2.4, 1.8, L); s.vline(4, 1, 8, L); s.rect(4, 1, 4, 2, L)
    add('note', s, O)
    s = Spr(7, 7)
    s.hline(0, 6, 0, L); s.line(6, 0, 0, 6, L); s.hline(0, 6, 6, L)
    add('z', s, O)
    s = Spr(8, 10)
    s.poly([(4, 0), (8, 4), (5.5, 4), (5.5, 10), (2.5, 10), (2.5, 4), (0, 4)], L)
    add('arrow', s, O)
    s = Spr(5, 6)
    s.ellipse(2.5, 3, 2.3, 2.8, '#c8a868'); s.px(1, 1, '#e8d8a8')
    add('seed', s, '#4a3a1a')
    s = Spr(12, 12)
    for i in range(8):
        a = i * math.pi / 4
        s.rect(6 + math.cos(a) * 4.5 - 1, 6 + math.sin(a) * 4.5 - 1, 2, 2, M)
    s.ellipse(6, 6, 4, 4, L); s.ellipse(6, 6, 1.5, 1.5, D)
    add('cog', s, O)
    # shield bubble (40x40)
    s = Spr(40, 40)
    for y in range(40):
        for x in range(40):
            d = ((x + 0.5 - 20) ** 2 + (y + 0.5 - 20) ** 2) ** 0.5
            if 17.5 < d <= 19.5:
                s.px(x, y, (255, 255, 255, 230))
            elif d <= 17.5:
                s.px(x, y, (255, 255, 255, int(40 + 60 * (d / 17.5) ** 3)))
    add('shield', s)
    # web (24x24)
    s = Spr(24, 24)
    for i in range(8):
        a = i * math.pi / 4
        s.line(12, 12, 12 + math.cos(a) * 11, 12 + math.sin(a) * 11, L)
    for r in (4, 7.5, 11):
        pts = [(12 + math.cos(i * math.pi / 4) * r, 12 + math.sin(i * math.pi / 4) * r) for i in range(9)]
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            s.line(x0, y0, x1, y1, M)
    add('web', s)
    return F


def icon_frames():
    F = []
    caps = {'capsule': '#e2555f', 'prime_capsule': '#3d8bfd', 'apex_capsule': '#f5c542', 'dusk_capsule': '#3a4a5a',
            'swift_capsule': '#4fc7b8', 'covenant_capsule': '#6a4cd8'}
    for k, c in caps.items():
        s = Spr(16, 16); s.blit(capsule(c, size=11), 2, 2); F.append((k, s))
    for k, c in {'tonic': '#e2555f', 'strong_tonic': '#e8823a', 'grand_tonic': '#3d8bfd', 'full_tonic': '#f5c542', 'panacea': '#b86ae8', 'focus_drop': '#4fc7b8'}.items():
        F.append((k, bottle(c)))
    for k, c in {'purge_herb': '#8a5ac8', 'cool_salve': '#5ab8e8', 'wake_chime': '#f5c542', 'thaw_draught': '#e87a3a', 'nerve_balm': '#e8d84a', 'clarity_leaf': '#6aba4a'}.items():
        F.append((k, herb(c)))
    F.append(('rekindle_seed', seed('#e8823a')))
    F.append(('bloom_seed', seed('#ff6ab0')))
    F.append(('growth_fruit', seed('#e2555f')))
    def simple(name, fn):
        s = Spr(16, 16); fn(s); s.outline('#1c1a28'); F.append((name, s))
    simple('ward_incense', lambda s: (s.rect(5, 6, 6, 8, '#8a7a9a'), s.rect(4, 5, 8, 2, '#b8a8c8'), s.line(7, 4, 6, 1, '#e8e0f0'), s.line(9, 4, 10, 1, '#e8e0f0')))
    simple('strong_incense', lambda s: (s.rect(5, 6, 6, 8, '#5a4a7a'), s.rect(4, 5, 8, 2, '#8a7aa8'), s.line(7, 4, 6, 1, '#e8e0f0'), s.line(9, 4, 10, 1, '#e8e0f0')))
    simple('homing_thread', lambda s: (s.ellipse(8, 9, 5, 4, '#e8c86a'), s.line(4, 8, 12, 10, '#c8a84a'), s.line(12, 6, 15, 2, '#e8c86a')))
    simple('pearl', lambda s: s.shaded_ellipse(8, 8, 5, 5, ramp('#f0e8f4', 5, 0.1)))
    simple('star_shard', lambda s: s.poly([(8, 1), (10, 6), (15, 7), (11, 10), (12, 15), (8, 12), (4, 15), (5, 10), (1, 7), (6, 6)], '#f5d85a'))
    simple('trail_boots', lambda s: (s.rect(3, 4, 5, 8, '#b85a3a'), s.rect(3, 11, 9, 3, '#8a3a2a'), s.rect(9, 6, 4, 6, '#b85a3a')))
    simple('bond_charm', lambda s: (s.ellipse(8, 9, 5, 5, '#e2555f'), s.ellipse(8, 9, 2, 2, '#ffd0d8'), s.line(8, 2, 8, 4, '#e8c86a')))
    simple('reach_map', lambda s: (s.rect(2, 3, 12, 10, '#e8d8a8'), s.vline(6, 3, 12, '#b8a878'), s.vline(10, 3, 12, '#b8a878'), s.px(8, 7, '#e2555f')))
    simple('brush_hook', lambda s: (s.line(3, 14, 9, 6, '#8a5a3a'), s.line(4, 14, 10, 6, '#8a5a3a'), s.poly([(8, 7), (12, 2), (14, 5), (11, 8)], '#c8ccd4')))
    simple('skiff', lambda s: (s.poly([(1, 8), (15, 8), (13, 13), (3, 13)], '#b4643c'), s.hline(2, 13, 8, '#d8844c'), s.line(8, 8, 8, 1, '#6b4a30'), s.poly([(8, 1), (13, 6), (8, 6)], '#f0f0f0')))
    simple('marsh_parcel', lambda s: (s.rect(2, 4, 12, 9, '#c8a878'), s.hline(2, 13, 8, '#8a5a3a'), s.vline(8, 4, 12, '#8a5a3a')))
    simple('pips_bell', lambda s: (s.shaded_ellipse(8, 9, 4, 4, ramp('#f5c542', 5, 0.15)), s.px(8, 12, '#3a2a1a'), s.line(5, 4, 11, 4, '#e2555f')))
    simple('forge_pass', lambda s: (s.rect(2, 4, 12, 8, '#8e9aaf'), s.rect(3, 5, 4, 4, '#f5c542'), s.hline(8, 12, 6, '#ffffff'), s.hline(8, 12, 9, '#ffffff')))
    simple('rift_key', lambda s: (s.ellipse(5, 8, 3.5, 3.5, '#6fe0c8'), s.ellipse(5, 8, 1.5, 1.5, '#1c1a28'), s.hline(8, 14, 8, '#6fe0c8'), s.vline(12, 8, 11, '#6fe0c8'), s.vline(14, 8, 10, '#6fe0c8')))
    # XP Share: a gold medallion on a chain, a glowing teal gem with a star glint
    def xp_share(s):
        for x in range(4, 13):
            y = 1 + int(round(((x - 8) / 4.0) ** 2 * 3))
            s.px(x, y, '#e8c86a')
        s.shaded_ellipse(8, 10, 5, 5, ramp('#f5c542', 5, 0.16))
        s.shaded_ellipse(8, 10, 3, 3, ramp('#4fd8c8', 5, 0.16))
        s.px(8, 8, '#ffffff'); s.px(7, 9, '#e8fffb'); s.px(9, 9, '#e8fffb'); s.px(8, 10, '#ffffff'); s.px(8, 9, '#ffffff')
        s.px(12, 6, '#fff7c0'); s.px(3, 13, '#fff7c0')
    simple('xp_share', xp_share)
    # Forge Ember: a little iron lantern with a glowing coal
    simple('forge_ember', lambda s: (s.rect(4, 4, 8, 10, '#4a4a58'), s.rect(5, 5, 6, 8, '#2a2230'), s.shaded_ellipse(8, 10, 2.5, 2.5, ramp('#ff8a2a', 5, 0.2)),
                                     s.px(8, 8, '#ffe07a'), s.px(7, 9, '#ffd04a'), s.rect(6, 2, 4, 2, '#4a4a58'), s.hline(3, 12, 14, '#5a5a6a')))
    # Wing Whistle: a wooden whistle with a feather
    simple('wing_whistle', lambda s: (s.rect(2, 8, 9, 4, '#c8884a'), s.rect(2, 8, 9, 1, '#e8a86a'), s.rect(10, 7, 3, 6, '#a8683a'), s.px(5, 10, '#3a2a1a'),
                                      s.line(9, 7, 14, 1, '#f0f0f8'), s.line(10, 7, 15, 2, '#c8d8f0'), s.line(11, 5, 13, 4, '#f0f0f8')))
    # Seal Shard: a glowing crystal fragment
    simple('seal_shard', lambda s: (s.poly([(8, 1), (12, 6), (10, 14), (5, 14), (4, 6)], '#8a6ad8'), s.poly([(8, 1), (10, 6), (8, 13), (6, 6)], '#b89af0'), s.px(7, 4, '#ffffff')))
    # discs by type
    import re
    td_types = {'td01': 'Plain', 'td02': 'Plain', 'td03': 'Stone', 'td04': 'Static', 'td05': 'Frost', 'td06': 'Ember', 'td07': 'Nature',
                'td08': 'Tide', 'td09': 'Umbra', 'td10': 'Mind', 'td11': 'Brawl', 'td12': 'Wing', 'td13': 'Iron', 'td14': 'Toxin',
                'td15': 'Swarm', 'td16': 'Drake', 'td17': 'Plain', 'td18': 'Static'}
    for k, t in td_types.items():
        F.append((k, disc(TYPES[t])))
    return F


def main():
    save_atlas(ui_frames(), os.path.join(ROOT, 'public', 'assets', 'ui', 'ui.png'), 'ui.png')
    save_atlas(icon_frames(), os.path.join(ROOT, 'public', 'assets', 'sprites', 'icons.png'), 'icons.png')
    print('ui + icons atlases built')


if __name__ == '__main__':
    main()
