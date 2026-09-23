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
    'Brawl': '#d0503a', 'Mind': '#f06292', 'Umbra': '#5e4b8b', 'Iron': '#8e9aaf', 'Drake': '#6a4cd8',
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
    mi('options', lambda s: (s.ellipse(8, 8, 5.5, 5.5, '#9aa0b4'), s.ellipse(8, 8, 2, 2, '#1c1a28'), [s.rect(7, 0, 2, 3, '#9aa0b4'), s.rect(7, 13, 2, 3, '#9aa0b4'), s.rect(0, 7, 3, 2, '#9aa0b4'), s.rect(13, 7, 3, 2, '#9aa0b4')]))
    mi('map', lambda s: (s.rect(2, 3, 12, 10, '#e8d8a8'), s.vline(6, 3, 12, '#b8a878'), s.vline(10, 3, 12, '#b8a878'), s.px(8, 7, '#e2555f'), s.px(4, 9, '#4caf50')))
    mi('exit', lambda s: (s.rect(4, 2, 8, 12, '#8a5a3a'), s.rect(5, 3, 6, 10, '#b87a4a'), s.px(9, 8, '#f0d24a')))
    # battle shadow ellipse
    sh = Spr(64, 14)
    import numpy as np
    ys, xs = np.mgrid[0:14, 0:64]
    d = ((xs + 0.5 - 32) / 32) ** 2 + ((ys + 0.5 - 7) / 7) ** 2
    sh.a[d <= 1] = (0, 0, 0, 90)
    F.append(('battle_shadow', sh))
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
