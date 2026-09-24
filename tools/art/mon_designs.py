"""Design specs for every Morph. Each entry: (materials, parts).
Coordinates are in a 96×96 box; ground is y≈90; enemies face left.
"""
import math
from mongen import E, Cap, Tri, Leaf, Flame, Eye, Mouth, Spot, Part


def T(parts, s=1.0, cx=48, gy=90, dx=0, dy=0):
    """Scale a part list about the ground-centre point."""
    out = []
    for p in parts:
        kw = dict(p.kw)
        def X(x): return cx + (x - cx) * s + dx
        def Y(y): return gy - (gy - y) * s + dy
        if p.kind == 'ellipse':
            kw.update(cx=X(kw['cx']), cy=Y(kw['cy']), rx=kw['rx'] * s, ry=kw['ry'] * s)
        elif p.kind == 'capsule':
            kw.update(x0=X(kw['x0']), y0=Y(kw['y0']), x1=X(kw['x1']), y1=Y(kw['y1']), r0=kw['r0'] * s, r1=kw['r1'] * s)
        elif p.kind == 'poly':
            kw.update(pts=[(X(a), Y(b)) for a, b in kw['pts']])
        elif p.kind == 'leaf':
            kw.update(x=X(kw['x']), y=Y(kw['y']), length=kw['length'] * s, width=kw['width'] * s)
        elif p.kind == 'flame':
            kw.update(x=X(kw['x']), y=Y(kw['y']), h=kw['h'] * s, w=kw['w'] * s)
        elif p.kind == 'eye':
            kw.update(x=X(kw['x']), y=Y(kw['y']), r=kw['r'] * max(0.8, s))
        elif p.kind == 'mouth':
            kw.update(x=X(kw['x']), y=Y(kw['y']), w=kw['w'] * max(0.8, s))
        out.append(Part(p.kind, p.mat, p.z, p.view, **kw))
    return out


# ── body-plan builders ─────────────────────────────────────────────────────
def quad(ears='pointy', tail='thin', snout=True, eye='round', mouth='smile', stout=1.0, leg=1.0, head=1.0, neck=0.0, spikes=0, mane=False):
    P = []
    ly = 78 + (1 - leg) * 4
    # tail (behind)
    if tail == 'flame':
        P += [Cap(66, 72, 74, 58, 4, 3, 'body', z=-2), Flame(76, 58, 22, 14, 'flame', z=-1, lean=0.3)]
    elif tail == 'fluffy':
        P += [E(72, 64, 8, 11, 'body', z=-2, rot=0.5), E(74, 58, 5, 6, 'accent', z=-1.9, rot=0.5)]
    elif tail == 'drop':
        P += [Cap(64, 74, 76, 66, 4, 2.5, 'body', z=-2), E(79, 63, 5, 6, 'accent', z=-1)]
    elif tail == 'thin':
        P += [Cap(64, 72, 78, 64, 3, 1.5, 'body', z=-2), E(79, 63, 3, 3, 'accent', z=-1.9)]
    elif tail == 'leaf':
        P += [Cap(64, 72, 72, 64, 3, 2, 'body', z=-2), Leaf(71, 64, 16, 9, -0.9, 'accent', z=-1)]
    elif tail == 'fin':
        P += [Cap(64, 74, 76, 70, 4, 3, 'body', z=-2), Leaf(74, 70, 14, 10, -0.3, 'accent', z=-1)]
    elif tail == 'stub':
        P += [E(68, 68, 5, 5, 'body', z=-2)]
    elif tail == 'long':
        P += [Cap(64, 72, 80, 70, 4, 3, 'body', z=-2), Cap(80, 70, 86, 58, 3, 2, 'body', z=-2)]
    # far legs
    P += [Cap(60, ly, 62, 88, 4, 3.5 * leg, 'body', z=-1), Cap(52, ly + 1, 52, 89, 4, 3.5 * leg, 'body', z=0)]
    P += [E(50, 72, 19, 12 * stout, 'body', z=0.5)]
    if spikes:
        for i in range(spikes):
            x = 40 + i * (24 / max(1, spikes - 1))
            P.append(Tri([(x - 3, 62), (x + 1, 52 - (i % 2) * 3), (x + 4, 63)], 'accent', z=0.4))
    # near legs
    P += [Cap(36, ly, 35, 89, 4, 3.5 * leg, 'body', z=2), Cap(44, ly + 1, 45, 89, 4, 3.5 * leg, 'body', z=2.2)]
    P += [E(40, 70, 9, 9, 'belly', z=1)]
    hy = 53 - neck
    if neck:
        P.append(Cap(44, 66, 41, hy + 6, 7, 6, 'body', z=2.4))
    if mane:
        P.append(E(44, hy + 4, 18, 15, 'accent', z=2.3))
    if ears == 'pointy':
        P += [Tri([(27, hy - 7), (29, hy - 23), (39, hy - 11)], 'body', z=2.5), Tri([(30, hy - 10), (31, hy - 19), (36, hy - 12)], 'inner', z=2.6),
              Tri([(45, hy - 12), (54, hy - 25), (55, hy - 8)], 'body', z=2.5), Tri([(48, hy - 12), (53, hy - 21), (53, hy - 10)], 'inner', z=2.6)]
    elif ears == 'round':
        P += [E(30, hy - 11, 6, 6, 'body', z=2.5), E(30, hy - 11, 3.5, 3.5, 'inner', z=2.6),
              E(51, hy - 12, 6, 6, 'body', z=2.5), E(51, hy - 12, 3.5, 3.5, 'inner', z=2.6)]
    elif ears == 'fin':
        P += [Leaf(30, hy - 3, 16, 9, -2.6, 'accent', z=2.4), Leaf(51, hy - 4, 16, 9, -0.5, 'accent', z=2.4)]
    elif ears == 'long':
        P += [E(31, hy - 16, 4, 11, 'body', z=2.5, rot=-0.3), E(31, hy - 16, 2, 8, 'inner', z=2.6, rot=-0.3),
              E(50, hy - 17, 4, 11, 'body', z=2.5, rot=0.3), E(50, hy - 17, 2, 8, 'inner', z=2.6, rot=0.3)]
    elif ears == 'horns':
        P += [Cap(33, hy - 8, 26, hy - 20, 3, 1.2, 'accent', z=2.5), Cap(49, hy - 9, 55, hy - 21, 3, 1.2, 'accent', z=2.5)]
    elif ears == 'curl':
        P += [E(29, hy - 4, 7, 7, 'accent', z=3.5), E(29, hy - 4, 3.5, 3.5, 'inner', z=3.6), E(53, hy - 5, 7, 7, 'accent', z=3.5), E(53, hy - 5, 3.5, 3.5, 'inner', z=3.6)]
    P += [E(41, hy, 15 * head, 13 * head, 'body', z=3)]
    if snout:
        sl = 1.3 if snout == 'long' else 1.0
        P += [E(38 - (sl - 1) * 6, hy + 6, 8 * sl, 5.5, 'belly', z=4), Spot(37 - (sl - 1) * 10, hy + 3, 1.8, 'nose', z=102)]
    P += [Eye(34, hy - 2, 3, eye), Eye(46, hy - 2, 3, eye)]
    if mouth:
        P.append(Mouth(38 - (1.3 if snout == 'long' else 0), hy + 8, 4, mouth))
    return P


def biped(ears='none', tail='none', eye='round', mouth='smile', arms='stub', belly=True, head=1.0, body=1.0):
    P = []
    if tail == 'thin':
        P += [Cap(58, 76, 72, 70, 3, 1.5, 'body', z=-2)]
    elif tail == 'flame':
        P += [Cap(58, 76, 68, 66, 3, 2, 'body', z=-2), Flame(70, 66, 18, 11, 'flame', z=-1, lean=0.2)]
    elif tail == 'stub':
        P += [E(62, 74, 5, 5, 'body', z=-2)]
    P += [Cap(42, 76, 41, 88, 5, 4.5, 'body', z=0), Cap(54, 76, 55, 88, 5, 4.5, 'body', z=0),
          E(40, 88, 6, 3, 'body', z=0.1), E(56, 88, 6, 3, 'body', z=0.1)]
    P += [E(48, 66, 14 * body, 15 * body, 'body', z=1)]
    if belly:
        P += [E(47, 69, 8 * body, 9 * body, 'belly', z=1.5)]
    if arms == 'stub':
        P += [Cap(34, 62, 30, 72, 4, 3.5, 'body', z=2), Cap(62, 62, 66, 72, 4, 3.5, 'body', z=0.5)]
    elif arms == 'fists':
        P += [Cap(34, 60, 29, 70, 4, 3.5, 'body', z=2), E(28, 72, 5.5, 5.5, 'accent', z=2.1),
              Cap(62, 60, 67, 70, 4, 3.5, 'body', z=0.5), E(68, 72, 5.5, 5.5, 'accent', z=0.6)]
    elif arms == 'blades':
        P += [Cap(34, 60, 26, 66, 4, 3, 'body', z=2), Tri([(26, 62), (14, 44), (29, 66)], 'accent', z=2.1),
              Cap(62, 60, 70, 66, 4, 3, 'body', z=0.5), Tri([(70, 62), (80, 44), (68, 66)], 'accent', z=0.6)]
    hy = 44
    if ears == 'pointy':
        P += [Tri([(36, hy - 6), (36, hy - 22), (45, hy - 9)], 'body', z=2.5), Tri([(52, hy - 9), (60, hy - 22), (61, hy - 6)], 'body', z=2.5)]
    elif ears == 'round':
        P += [E(37, hy - 10, 6, 6, 'body', z=2.5), E(59, hy - 10, 6, 6, 'body', z=2.5)]
    elif ears == 'antenna':
        P += [Cap(42, hy - 10, 36, hy - 24, 1.3, 1, 'accent', z=2.4), E(35, hy - 25, 3, 3, 'accent', z=2.5),
              Cap(54, hy - 10, 60, hy - 24, 1.3, 1, 'accent', z=2.4), E(61, hy - 25, 3, 3, 'accent', z=2.5)]
    P += [E(48, hy, 14 * head, 13 * head, 'body', z=3)]
    P += [Eye(43, hy - 1, 3, eye), Eye(54, hy - 1, 3, eye)]
    if mouth:
        P.append(Mouth(48.5, hy + 6, 4, mouth))
    return P


def bird(crest=True, wings='folded', tail=True, beak='short', eye='round', legs=True, body=1.0):
    P = []
    if legs:
        P += [Cap(42, 82, 41, 90, 1.6, 1.6, 'feet', z=-1), Cap(54, 82, 55, 90, 1.6, 1.6, 'feet', z=-1)]
    if tail:
        P += [Leaf(58, 76, 16, 8, 0.4, 'wing', z=-0.5), Leaf(58, 74, 15, 7, 0.1, 'wing', z=-0.6)]
    if wings == 'spread':
        P += [Leaf(58, 62, 30, 14, -0.45, 'wing', z=-0.3), Leaf(38, 62, 30, 14, -2.7, 'wing', z=2.5)]
    P += [E(48, 70, 17 * body, 15 * body, 'body', z=0), E(47, 74, 10 * body, 10 * body, 'belly', z=1)]
    if wings == 'folded':
        P += [Leaf(33, 66, 14, 8, 2.3, 'wing', z=1.5), Leaf(63, 66, 14, 8, 0.85, 'wing', z=1.5)]
    if crest:
        P += [Leaf(47, 40, 11, 5, -1.9, 'crest', z=1.8), Leaf(49, 40, 11, 5, -1.2, 'crest', z=1.8)]
    P += [E(46, 52, 14, 13, 'body', z=2)]
    if beak == 'short':
        P += [Tri([(40, 55), (48, 55), (42, 62)], 'beak', z=3)]
    elif beak == 'long':
        P += [Tri([(40, 53), (46, 57), (22, 60)], 'beak', z=3)]
    elif beak == 'hook':
        P += [Tri([(38, 53), (46, 55), (34, 63)], 'beak', z=3)]
    P += [Eye(40, 50, 3, eye), Eye(52, 50, 3, eye)]
    return P


def blob(eye='round', mouth='smile', drip=False, width=1.0, height=1.0):
    P = [E(48, 76, 22 * width, 15 * height, 'body', z=0), E(48, 64, 17 * width, 16 * height, 'body', z=0.2)]
    if drip:
        P += [Cap(34, 80, 33, 90, 3, 2.5, 'body', z=0.3), Cap(60, 82, 62, 90, 2.5, 2, 'body', z=0.3)]
    P += [E(48, 80, 16 * width, 5, 'belly', z=0.5)]
    P += [Eye(41, 63, 3.2, eye), Eye(55, 63, 3.2, eye)]
    if mouth:
        P.append(Mouth(48, 70, 5, mouth))
    return P


def bug(segments=3, legs=6, antenna=True, eye='round', mouth=None, wings=None):
    P = []
    xs = [60, 50, 40][:segments]
    for i, x in enumerate(xs[::-1]):
        pass
    P += [E(62, 76, 12, 9, 'body', z=0), E(50, 74, 11, 10, 'accent', z=0.5)]
    if wings == 'moth':
        P += [Leaf(54, 62, 30, 20, -0.9, 'wing', z=-0.5), Leaf(46, 62, 30, 20, -2.25, 'wing', z=2.6)]
    for i in range(legs // 2):
        x = 44 + i * 8
        P += [Cap(x, 80, x - 4, 89, 1.4, 1.2, 'dark', z=-0.2), Cap(x + 2, 80, x + 5, 89, 1.4, 1.2, 'dark', z=1.2)]
    P += [E(38, 66, 13, 12, 'body', z=2)]
    if antenna:
        P += [Cap(34, 56, 26, 44, 1.3, 1, 'dark', z=1.5), E(25, 43, 2.5, 2.5, 'accent', z=1.6),
              Cap(42, 55, 46, 42, 1.3, 1, 'dark', z=1.5), E(47, 41, 2.5, 2.5, 'accent', z=1.6)]
    P += [Eye(32, 64, 3, eye), Eye(43, 64, 3, eye)]
    if mouth:
        P.append(Mouth(37, 71, 4, mouth))
    return P


def serpent(eye='fierce', frill=False, whiskers=False, s=1.0):
    P = [Cap(78, 84, 64, 86, 4, 7, 'body', z=-1), Cap(64, 86, 44, 84, 7, 9, 'body', z=0),
         Cap(44, 84, 38, 70, 9, 8, 'body', z=0.5), Cap(38, 70, 44, 56, 8, 7, 'body', z=1),
         E(44, 80, 7, 5, 'belly', z=0.6), Cap(38, 76, 40, 64, 4, 4, 'belly', z=1.1)]
    if frill:
        P += [Leaf(46, 44, 16, 9, -1.1, 'accent', z=1.5), Leaf(42, 44, 16, 9, -2.1, 'accent', z=1.5), Leaf(50, 48, 14, 8, -0.4, 'accent', z=1.5)]
    P += [E(40, 50, 13, 10, 'body', z=2), E(33, 54, 8, 5, 'belly', z=2.1)]
    P += [Eye(36, 47, 3, eye), Eye(46, 47, 3, eye)]
    if whiskers:
        P += [Cap(30, 55, 18, 60, 1, 0.6, 'accent', z=2.2), Cap(34, 56, 26, 64, 1, 0.6, 'accent', z=2.2)]
    return P


def rock(eye='round', mouth='line', tall=1.0):
    P = [Tri([(24, 90), (28, 60 - 10 * tall), (44, 44 - 12 * tall), (62, 48 - 10 * tall), (72, 66), (74, 90)], 'body', z=0),
         Tri([(30, 88), (34, 66 - 8 * tall), (46, 58 - 10 * tall), (58, 62 - 8 * tall), (66, 88)], 'belly', z=0.2, flat=True)]
    P += [Eye(40, 64 - 8 * tall, 3, eye), Eye(54, 64 - 8 * tall, 3, eye)]
    if mouth:
        P.append(Mouth(47, 72 - 8 * tall, 5, mouth))
    return P


# ── species designs ────────────────────────────────────────────────────────
D = {}

D['spriglet'] = (dict(body='#6cc24a', belly='#eef4c8', leaf='#3f9a45', stem='#7a8a3a', blush='#ff9aa8'), [
    E(38, 87, 6, 4, 'body', z=-1), E(58, 87, 6, 4, 'body', z=-1),
    E(48, 72, 18, 15, 'body', z=0), E(48, 76, 11, 9, 'belly', z=1),
    Cap(48, 40, 48, 33, 1.6, 1.6, 'stem', z=1.5),
    Leaf(47, 34, 22, 12, -2.3, 'leaf', z=1.6), Leaf(49, 34, 22, 12, -0.85, 'leaf', z=1.6),
    E(48, 53, 18, 15, 'body', z=2),
    Spot(38, 58, 2.2, 'blush', z=99), Spot(58, 58, 2.2, 'blush', z=99),
    Eye(42, 53, 3.3), Eye(55, 53, 3.3), Mouth(48.5, 59, 4, 'smile')])
D['spriggrove'] = (dict(body='#58a844', belly='#e2eeb4', leaf='#2f8a3d', bark='#8a6a44', blush='#ff9aa8'), T([
    Cap(36, 76, 34, 89, 5, 5, 'bark', z=-1), Cap(60, 76, 62, 89, 5, 5, 'bark', z=-1),
    E(48, 68, 19, 18, 'body', z=0), E(48, 72, 12, 11, 'belly', z=1),
    Cap(32, 62, 24, 72, 4, 3, 'bark', z=1.2), Cap(64, 62, 72, 72, 4, 3, 'bark', z=-0.5),
    Leaf(40, 34, 26, 14, -2.5, 'leaf', z=1.4), Leaf(56, 34, 26, 14, -0.6, 'leaf', z=1.4), Leaf(48, 32, 22, 12, -1.57, 'leaf', z=1.3),
    E(48, 48, 17, 14, 'body', z=2), Eye(42, 48, 3.2, 'fierce'), Eye(55, 48, 3.2, 'fierce'), Mouth(48.5, 54, 4, 'smile')], s=1.18))
D['mosswarden'] = (dict(body='#4a8a3c', belly='#9a9a86', leaf='#2f7a3a', stone='#8e8a86', moss='#6cb048'), T([
    Cap(30, 72, 28, 89, 7, 7, 'stone', z=-1), Cap(64, 72, 66, 89, 7, 7, 'stone', z=-1),
    E(48, 62, 26, 22, 'stone', z=0), E(48, 50, 24, 12, 'moss', z=0.4),
    Tri([(28, 56), (34, 40), (42, 54)], 'stone', z=0.3), Tri([(54, 54), (62, 38), (68, 56)], 'stone', z=0.3),
    Leaf(30, 42, 18, 10, -2.4, 'leaf', z=0.6), Leaf(62, 42, 18, 10, -0.7, 'leaf', z=0.6),
    Cap(24, 58, 16, 72, 6, 6, 'stone', z=1.2), E(15, 75, 7, 6, 'moss', z=1.3),
    E(40, 42, 13, 11, 'body', z=2), E(36, 47, 7, 4, 'belly', z=2.1),
    Eye(36, 40, 2.8, 'fierce'), Eye(46, 40, 2.8, 'fierce'), Mouth(35, 48, 4, 'line')], s=1.3, dy=-2))

D['cindlet'] = (dict(body='#f08a3a', belly='#ffe0a8', flame='#ffcf3a', inner='#c84a3a', nose='#3a1a1a'), quad('pointy', 'flame', mouth='fang'))
D['cindreaver'] = (dict(body='#e0602e', belly='#ffd8a0', flame='#ffc43a', inner='#b83a2a', nose='#3a1a1a', accent='#ffb03a'),
                   T(quad('pointy', 'flame', eye='fierce', mouth='fang', leg=1.2, mane=True, neck=3), s=1.2))
D['pyromane'] = (dict(body='#3a2a3e', belly='#e8b070', flame='#ff9a2a', inner='#e05a3a', nose='#1a1018', accent='#ff6a2a'),
                 T(quad('horns', 'flame', eye='fierce', mouth='fang', leg=1.3, mane=True, neck=6, spikes=3) + [Flame(46, 38, 20, 14, 'flame', z=2.35)], s=1.35, dy=-2))

D['puddlet'] = (dict(body='#5aa8e8', belly='#e4f4ff', accent='#2e6ac8', nose='#1e3a6a'), quad('fin', 'drop', mouth='smile'))
D['torrentide'] = (dict(body='#3a86d8', belly='#dcf0ff', accent='#1e56b0', nose='#12305a', inner='#8ac8ff'),
                   T(quad('fin', 'fin', eye='fierce', snout='long', leg=1.1, neck=3), s=1.2))
D['maelstrand'] = (dict(body='#2a64b8', belly='#e8f6ff', accent='#bfe8ff', nose='#0e2448', inner='#8ad8ff'),
                   T(quad('fin', 'fin', eye='fierce', snout='long', leg=1.3, neck=6, spikes=4, mane=True, mouth='fang'), s=1.36, dy=-2))

D['nibbit'] = (dict(body='#a88a6a', belly='#f2e2c8', accent='#6a5a4a', inner='#e8a0a0', nose='#3a2a2a'),
               T(quad('round', 'thin', mouth='fang', stout=0.9, leg=0.8), s=0.82))
D['gnawbit'] = (dict(body='#8a6a50', belly='#f0dcc0', accent='#4a3a30', inner='#e89a9a', nose='#2a1a1a'),
                T(quad('round', 'thin', eye='fierce', mouth='fang', leg=1.0, spikes=0), s=1.1))
D['trotter'] = (dict(body='#c89060', belly='#f4dcb8', accent='#6a4a30', inner='#e8a0a0', nose='#3a2a2a'),
                T(quad('pointy', 'fluffy', snout='long', leg=1.3), s=0.95))
D['trotterion'] = (dict(body='#a87040', belly='#f0d4a8', accent='#f2eee4', inner='#e8a0a0', nose='#2a1a1a'),
                   T(quad('pointy', 'fluffy', snout='long', eye='fierce', leg=1.5, neck=6, mane=True), s=1.25))

D['beakling'] = (dict(body='#e8c05a', belly='#fff2c8', wing='#c89030', beak='#f07a2a', feet='#e07a3a', crest='#d85a3a'), bird())
D['skyveer'] = (dict(body='#5a7ac8', belly='#e8eeff', wing='#3a52a0', beak='#f0b02a', feet='#e0a02a', crest='#e8c05a'),
                T(bird(wings='spread', beak='hook', eye='fierce'), s=1.15))
D['tempestral'] = (dict(body='#3a4a8a', belly='#dfe6ff', wing='#262e6a', beak='#f0c43a', feet='#e0b02a', crest='#8ae0ff'),
                   T(bird(wings='spread', beak='hook', eye='fierce', crest=True) + [Leaf(46, 36, 18, 6, -1.7, 'crest', z=1.9)], s=1.4, dy=-4))

D['chittik'] = (dict(body='#7a9a3a', accent='#a8c85a', dark='#2a3a1a'), T(bug(eye='round', mouth='smile'), s=0.9))
D['mantipule'] = (dict(body='#5a9a3a', belly='#c8e8a0', accent='#e8f0d0', dark='#2a3a1a'),
                  T(biped(ears='antenna', arms='blades', eye='fierce', mouth=None, tail='thin'), s=1.2))
D['fuzzling'] = (dict(body='#e8d8a8', accent='#c8a8e0', dark='#5a4a6a'), [
    E(70, 80, 9, 8, 'body', z=0), E(58, 80, 10, 9, 'accent', z=0.2), E(46, 78, 11, 10, 'body', z=0.4),
    E(36, 70, 13, 12, 'body', z=1), Cap(32, 58, 28, 50, 1.2, 1, 'dark', z=0.9), Cap(42, 58, 46, 50, 1.2, 1, 'dark', z=0.9),
    Eye(31, 69, 3), Eye(42, 69, 3), Mouth(36, 75, 3, 'smile')])
D['mothlume'] = (dict(body='#8a6ab8', accent='#e8e0ff', wing='#c8a8f0', dark='#3a2a5a', belly='#f8f0d0'), T([
    Leaf(52, 58, 34, 24, -0.75, 'wing', z=-0.5), Leaf(44, 58, 34, 24, -2.4, 'wing', z=2.6),
    Spot(66, 44, 4, 'accent', z=-0.4), Spot(29, 44, 4, 'accent', z=2.7),
    E(48, 70, 9, 14, 'body', z=1), E(48, 74, 5, 8, 'belly', z=1.1), E(48, 52, 10, 9, 'body', z=2),
    Cap(44, 45, 36, 32, 1.2, 1, 'dark', z=1.9), Cap(52, 45, 60, 32, 1.2, 1, 'dark', z=1.9),
    Eye(44, 52, 2.8), Eye(53, 52, 2.8)], s=1.2))

D['burrlet'] = (dict(body='#8ab84a', belly='#e8f0c0', accent='#5a8a2a', blush='#ff9aa8'), T(blob(mouth='smile') + [
    Tri([(30 + i * 7, 58 - (i % 2) * 3), (33 + i * 7, 46 - (i % 3) * 2), (36 + i * 7, 58)], 'accent', z=-0.5) for i in range(6)] + [
    Spot(38, 68, 2, 'blush', z=99), Spot(58, 68, 2, 'blush', z=99)], s=0.85))
D['thornbur'] = (dict(body='#6a9a3a', belly='#d8e8a0', accent='#3a6a2a', blush='#e87a8a'), T(blob(eye='fierce', mouth='fang', width=1.15, height=1.1) + [
    Tri([(24 + i * 7, 60 - (i % 2) * 4), (27 + i * 7, 42 - (i % 3) * 3), (31 + i * 7, 60)], 'accent', z=-0.5) for i in range(8)], s=1.15))
D['sporra'] = (dict(body='#f0e0c8', accent='#c8453d', belly='#fff4e0', dot='#fff8f0'), [
    E(48, 78, 13, 12, 'body', z=0), E(48, 82, 9, 6, 'belly', z=0.2),
    E(48, 60, 24, 14, 'accent', z=1), Spot(38, 56, 3, 'dot', z=1.1), Spot(56, 54, 2.5, 'dot', z=1.1), Spot(48, 50, 2, 'dot', z=1.1),
    Eye(43, 76, 2.8), Eye(53, 76, 2.8), Mouth(48, 82, 3, 'smile')])
D['mycelord'] = (dict(body='#e8d4b8', accent='#8a2a5a', belly='#fff0dc', dot='#c8f0ff', dark='#5a3a4a'), T([
    Cap(40, 74, 36, 89, 5, 5, 'body', z=-0.5), Cap(56, 74, 60, 89, 5, 5, 'body', z=-0.5),
    E(48, 70, 14, 16, 'body', z=0), E(48, 74, 8, 9, 'belly', z=0.2),
    Cap(34, 64, 24, 74, 3.5, 3, 'body', z=0.5), Cap(62, 64, 72, 74, 3.5, 3, 'body', z=0.1),
    E(48, 44, 30, 15, 'accent', z=1), E(48, 52, 26, 5, 'dark', z=0.9),
    Spot(34, 40, 3, 'dot', z=1.1), Spot(56, 36, 3.5, 'dot', z=1.1), Spot(46, 34, 2.5, 'dot', z=1.1), Spot(64, 44, 2, 'dot', z=1.1),
    Eye(43, 62, 2.8, 'fierce'), Eye(54, 62, 2.8, 'fierce'), Mouth(48.5, 68, 4, 'line')], s=1.2))

D['voltquill'] = (dict(body='#e8c83a', belly='#fff4c0', accent='#5a4a2a', inner='#e8a03a', nose='#2a2a1a'),
                  T(quad('pointy', 'thin', stout=1.0, spikes=5, leg=0.8), s=0.9))
D['fulmirex'] = (dict(body='#d8a82a', belly='#fff0b0', accent='#3a3a4a', inner='#e8783a', nose='#1a1a1a'),
                 T(quad('pointy', 'long', eye='fierce', mouth='fang', spikes=7, leg=1.1), s=1.15))
D['arcfowl'] = (dict(body='#f0d040', belly='#fffae0', wing='#3a4a8a', beak='#3a3a4a', feet='#3a3a4a', crest='#8ae0ff'),
                T(bird(wings='spread', beak='hook', eye='fierce') + [Tri([(50 + i * 5, 48), (54 + i * 5, 30 - i * 2), (56 + i * 5, 50)], 'crest', z=1.95) for i in range(3)], s=1.4, dy=-4))

D['pebbling'] = (dict(body='#9a948a', belly='#c8c2b6'), T(rock(), s=0.8))
D['cragmaul'] = (dict(body='#7a746c', belly='#a8a298', accent='#5a544e'), T(biped(arms='fists', eye='fierce', mouth='line', belly=True, body=1.25, head=0.9), s=1.3, dy=-2))
D['oozelet'] = (dict(body='#9a5ac8', belly='#d8b0f0'), T(blob(drip=True, mouth='open'), s=0.9))
D['vexgore'] = (dict(body='#5a2a7a', belly='#b87ad8', accent='#c8f04a'), T(blob(eye='fierce', mouth='fang', drip=True, width=1.2, height=1.15) + [
    Tri([(34, 52), (30, 34), (42, 50)], 'accent', z=0.3), Tri([(56, 50), (66, 32), (62, 52)], 'accent', z=0.3)], s=1.2))
D['nyxen'] = (dict(body='#4a3a6a', belly='#8a7ab0', accent='#c8a8ff', inner='#8a5ac8', nose='#1a1224'),
              T(quad('pointy', 'fluffy', eye='round', mouth='smile'), s=0.9))
D['vesperel'] = (dict(body='#352850', belly='#7a6aa8', accent='#b89aff', inner='#6a4aa8', nose='#120c1c'),
                 T(quad('long', 'fluffy', eye='fierce', mouth='fang', leg=1.2, neck=3), s=1.15))
D['noctheart'] = (dict(body='#22183a', belly='#6a58a0', accent='#e8c8ff', inner='#9a6ae0', nose='#0a0612', flame='#b89aff'),
                  T(quad('horns', 'flame', eye='fierce', mouth='fang', leg=1.3, neck=6, mane=True), s=1.35, dy=-2))

D['gullip'] = (dict(body='#f4f6fa', belly='#ffffff', wing='#8aa0c0', beak='#f0b02a', feet='#e89a3a', crest='#8aa0c0'), bird(crest=False, beak='long'))
D['stormgull'] = (dict(body='#e8eef8', belly='#ffffff', wing='#3a5a8a', beak='#f0a02a', feet='#e08a2a', crest='#3a5a8a'),
                  T(bird(crest=True, wings='spread', beak='long', eye='fierce'), s=1.3, dy=-3))
D['crabbit'] = (dict(body='#e0603a', belly='#ffd8b8', accent='#b8402a', dark='#5a2a1a'), T([
    Cap(34, 80, 26, 89, 2, 1.6, 'dark', z=-0.2), Cap(62, 80, 70, 89, 2, 1.6, 'dark', z=-0.2),
    E(48, 74, 22, 13, 'body', z=0), E(48, 78, 14, 6, 'belly', z=0.2),
    Cap(28, 70, 20, 60, 3, 3, 'body', z=1), E(18, 54, 8, 7, 'accent', z=1.1), Tri([(12, 50), (18, 46), (16, 56)], 'belly', z=1.2),
    Cap(68, 70, 76, 60, 3, 3, 'body', z=-0.3), E(78, 54, 8, 7, 'accent', z=-0.2),
    Cap(42, 64, 40, 56, 1.3, 1.3, 'dark', z=0.5), Cap(54, 64, 56, 56, 1.3, 1.3, 'dark', z=0.5),
    Eye(40, 55, 2.8), Eye(56, 55, 2.8), Mouth(48, 72, 4, 'smile')], s=0.9))
D['pincerock'] = (dict(body='#b84a3a', belly='#e8b8a0', accent='#8e8a86', dark='#4a221a', stone='#7a746c'), T([
    Cap(34, 80, 24, 89, 2.5, 2, 'dark', z=-0.2), Cap(62, 80, 72, 89, 2.5, 2, 'dark', z=-0.2),
    E(48, 72, 26, 16, 'body', z=0), E(48, 62, 20, 10, 'stone', z=0.3), Spot(40, 58, 3, 'accent', z=0.35), Spot(56, 60, 4, 'accent', z=0.35),
    Cap(26, 70, 16, 58, 4, 4, 'body', z=1), E(12, 50, 11, 9, 'stone', z=1.1), Tri([(4, 46), (12, 40), (10, 54)], 'dark', z=1.2),
    Cap(70, 70, 80, 58, 4, 4, 'body', z=-0.3), E(83, 50, 10, 8, 'stone', z=-0.2),
    Eye(40, 66, 2.8, 'fierce'), Eye(56, 66, 2.8, 'fierce'), Mouth(48, 76, 5, 'line')], s=1.15))
D['jellume'] = (dict(body='#b8a0f0', belly='#e8e0ff', accent='#8a6ad0'), [
    E(48, 54, 20, 16, 'body', z=0), E(48, 62, 18, 5, 'belly', z=0.2)] + [
    Cap(34 + i * 7, 64, 32 + i * 7 + (i % 2) * 4, 88 - (i % 2) * 6, 2.2, 1.2, 'accent', z=-0.5) for i in range(5)] + [
    Eye(42, 54, 3), Eye(54, 54, 3), Mouth(48, 60, 4, 'smile')])
D['medusheen'] = (dict(body='#7a5ae0', belly='#e0d8ff', accent='#c8f0ff', dark='#4a2aa0'), T([
    E(48, 44, 26, 20, 'body', z=0), E(48, 54, 24, 6, 'belly', z=0.2), Spot(38, 36, 3, 'accent', z=0.3), Spot(58, 34, 2.5, 'accent', z=0.3)] + [
    Cap(26 + i * 7, 56, 22 + i * 7 + (i % 3) * 4, 88 - (i % 3) * 5, 2.6, 1.2, 'accent' if i % 2 else 'dark', z=-0.5) for i in range(7)] + [
    Eye(40, 44, 3, 'fierce'), Eye(56, 44, 3, 'fierce')], s=1.15, dy=-2))

D['ferrite'] = (dict(body='#8e9aaf', belly='#c8d0de', accent='#5a6070'), T(rock(eye='round', mouth='line', tall=0.6) + [
    Tri([(30, 56), (36, 38), (42, 54)], 'accent', z=-0.2), Tri([(52, 54), (60, 36), (66, 58)], 'accent', z=-0.2)], s=0.85))
D['ferroclad'] = (dict(body='#6a7488', belly='#b8c0d0', accent='#9aa6ba', stone='#7a746c', dark='#3a3e4a'), T(biped(arms='fists', eye='fierce', mouth='line', body=1.3, head=0.85) + [
    E(48, 52, 22, 8, 'accent', z=1.8), Tri([(28, 50), (24, 34), (38, 48)], 'stone', z=0.5), Tri([(58, 48), (70, 34), (68, 52)], 'stone', z=0.5)], s=1.3, dy=-2))
D['echirp'] = (dict(body='#3a3050', belly='#8a7aa0', wing='#5a4a7a', beak='#e8c8ff', feet='#3a3050', crest='#5a4a7a'), T([
    Leaf(56, 60, 26, 16, -0.6, 'wing', z=-0.5), Leaf(40, 60, 26, 16, -2.55, 'wing', z=2.5),
    E(48, 66, 13, 13, 'body', z=1), E(48, 70, 7, 7, 'belly', z=1.1),
    Tri([(38, 58), (34, 42), (44, 54)], 'body', z=0.9), Tri([(52, 54), (60, 40), (58, 58)], 'body', z=0.9),
    Eye(43, 64, 3.2), Eye(53, 64, 3.2), Mouth(48, 71, 4, 'fang')], s=0.9))
D['duskwing'] = (dict(body='#2a2240', belly='#6a5a88', wing='#4a3a6a', accent='#c89aff'), T([
    Leaf(58, 56, 38, 22, -0.5, 'wing', z=-0.5), Leaf(38, 56, 38, 22, -2.65, 'wing', z=2.5),
    E(48, 64, 13, 15, 'body', z=1), E(48, 68, 7, 9, 'belly', z=1.1),
    Tri([(38, 54), (32, 34), (45, 50)], 'body', z=0.9), Tri([(51, 50), (62, 32), (58, 54)], 'body', z=0.9),
    Eye(43, 60, 3, 'fierce', iris='#c89aff'), Eye(53, 60, 3, 'fierce', iris='#c89aff'), Mouth(48, 68, 4, 'fang')], s=1.25, dy=-6))
D['tunnip'] = (dict(body='#8a6a5a', belly='#e8c8b0', accent='#f0d8c8', inner='#e8a0a0', nose='#e87a8a'),
               T(quad('none', 'stub', eye='sleepy', snout='long', leg=0.7, stout=1.1) + [Tri([(30, 84), (22, 90), (34, 90)], 'accent', z=3)], s=0.9))
D['borebeast'] = (dict(body='#6a5a50', belly='#c8a890', accent='#9aa6ba', inner='#e8a0a0', nose='#e87a8a'),
                  T(quad('none', 'stub', eye='fierce', snout='long', leg=1.0, stout=1.2, spikes=4) + [
                      Tri([(22, 58), (8, 62), (22, 66)], 'accent', z=4.5)], s=1.25))
D['coilbit'] = (dict(body='#8e9aaf', belly='#d8e0ec', accent='#f5c542', dark='#3a3e4a'), T([
    E(48, 64, 16, 16, 'body', z=0), E(48, 64, 10, 10, 'belly', z=0.2),
    Cap(30, 58, 22, 50, 3, 3, 'accent', z=-0.2), Cap(66, 58, 74, 50, 3, 3, 'accent', z=-0.2),
    E(20, 48, 4, 4, 'dark', z=-0.1), E(76, 48, 4, 4, 'dark', z=-0.1),
    Cap(48, 80, 48, 90, 3, 2, 'dark', z=-0.3), Eye(48, 63, 4.2, 'round', iris='#f5c542')], s=0.9, dy=-6))
D['coilossus'] = (dict(body='#6a7488', belly='#d8e0ec', accent='#f5c542', dark='#2a2e3a'), T([
    E(48, 58, 14, 14, 'body', z=0), E(48, 58, 9, 9, 'belly', z=0.2), Eye(48, 57, 4, 'fierce', iris='#f5c542'),
    E(28, 74, 12, 12, 'body', z=0.5), E(28, 74, 7, 7, 'belly', z=0.6), Eye(28, 73, 3, 'round', iris='#f5c542'),
    E(68, 74, 12, 12, 'body', z=0.5), E(68, 74, 7, 7, 'belly', z=0.6), Eye(68, 73, 3, 'round', iris='#f5c542'),
    Cap(48, 44, 48, 30, 2, 2, 'accent', z=-0.2), E(48, 29, 4, 4, 'accent', z=-0.1),
    Cap(28, 86, 28, 91, 3, 2, 'dark', z=-0.3), Cap(68, 86, 68, 91, 3, 2, 'dark', z=-0.3)], s=1.2))
D['pugnet'] = (dict(body='#d8905a', belly='#f8e0c0', accent='#c83a3a'), T(biped(ears='round', arms='fists', eye='fierce', mouth='line'), s=0.95))
D['pugilus'] = (dict(body='#b86a3a', belly='#f4d4b0', accent='#e8e8f0', dark='#3a2a2a'), T(biped(ears='round', arms='fists', eye='fierce', mouth='fang', body=1.25) + [
    E(48, 36, 15, 3, 'accent', z=3.5)], s=1.3, dy=-2))
D['omenet'] = (dict(body='#f0a0c0', belly='#fff0f8', accent='#8a5ac8'), T(blob(eye='round', mouth=None) + [
    Spot(48, 54, 5, 'accent', z=0.5), Spot(48, 54, 2.5, 'belly', z=0.6)], s=0.85))
D['augurine'] = (dict(body='#d870a8', belly='#fff0f8', accent='#6a3aa8', dark='#3a1a5a'), T(biped(ears='antenna', eye='sleepy', mouth=None, body=1.1) + [
    E(48, 72, 16, 16, 'accent', z=0.8), Spot(48, 30, 5, 'belly', z=3.2), Spot(48, 30, 2.5, 'accent', z=3.3)], s=1.25))
D['pookit'] = (dict(body='#2a2a36', belly='#5a5a70', accent='#8ae0c8', inner='#6a5a8a', nose='#0a0a12'),
               T(quad('long', 'fluffy', eye='round', mouth='fang', leg=1.2), s=0.9))
D['pookavar'] = (dict(body='#1a1a24', belly='#3a3a50', accent='#6fe0c8', inner='#4a3a6a', nose='#000008'),
                 T(quad('horns', 'fluffy', eye='fierce', snout='long', mouth='fang', leg=1.6, neck=7, mane=True), s=1.35, dy=-2))
D['cairnite'] = (dict(body='#8b8a96', belly='#a8a8b4', accent='#6fe0c8'), T([
    Tri([(30, 90), (28, 50), (40, 22), (58, 26), (66, 52), (66, 90)], 'body', z=0),
    Tri([(36, 86), (36, 52), (44, 34), (54, 38), (58, 56), (58, 86)], 'belly', z=0.2, flat=True),
    Cap(40, 48, 52, 48, 1, 1, 'accent', z=0.5), Cap(46, 60, 46, 74, 1, 1, 'accent', z=0.5), Cap(42, 66, 50, 66, 1, 1, 'accent', z=0.5),
    Eye(42, 44, 2.6, 'sleepy'), Eye(52, 44, 2.6, 'sleepy')], s=1.1))
D['chillcub'] = (dict(body='#e8f4ff', belly='#ffffff', accent='#7fd6f2', inner='#9ac8e8', nose='#2a3a5a'),
                 T(quad('round', 'stub', stout=1.1, leg=0.9, mouth='smile'), s=0.9))
D['glaciursa'] = (dict(body='#dce8f4', belly='#ffffff', accent='#7fd6f2', dark='#2a3a5a'), T(biped(ears='round', arms='fists', eye='fierce', mouth='fang', body=1.35, head=0.95) + [
    Tri([(30, 50), (26, 30), (38, 46)], 'accent', z=0.5), Tri([(58, 46), (66, 28), (66, 50)], 'accent', z=0.5)], s=1.35, dy=-2))
D['flurrit'] = (dict(body='#dff0ff', belly='#ffffff', wing='#8ad8ff', beak='#6a8ac8', feet='#6a8ac8', crest='#8ad8ff'),
                T(bird(crest=True, wings='spread', beak='short'), s=1.05))
D['wyrmkin'] = (dict(body='#7a5ae0', belly='#e8d8ff', accent='#f0c43a'), T(serpent(eye='round', frill=True), s=0.85))
D['wyrmguard'] = (dict(body='#5a3ac8', belly='#dcd0ff', accent='#f0c43a'), T(serpent(eye='fierce', frill=True, whiskers=True), s=1.15))
D['riftwyrm'] = (dict(body='#3a2a8a', belly='#c8b8f0', accent='#6fe0c8', stone='#8a7e92', wing='#5a3ac8', horn='#ece2cc'), [
    # wings (behind)
    Leaf(56, 50, 40, 24, -0.75, 'wing', z=-3), Leaf(52, 50, 36, 18, -1.35, 'wing', z=-3.5),
    # tail
    Cap(62, 74, 78, 82, 7, 5, 'body', z=-1), Cap(78, 82, 90, 72, 5, 2.2, 'body', z=-1.2),
    Tri([(88, 66), (95, 60), (92, 73)], 'stone', z=-1.1),
    # legs & feet
    E(58, 74, 9, 11, 'body', z=-0.5), E(59, 88, 7, 2.6, 'stone', z=-0.4),
    E(45, 76, 8, 10, 'body', z=1.2), E(41, 88, 7, 2.6, 'stone', z=1.3),
    # torso
    E(52, 62, 13, 15, 'body', z=0.5, rot=0.35), E(46, 65, 7, 11, 'belly', z=0.8, rot=0.3),
    Tri([(52, 46), (60, 38), (58, 50)], 'stone', z=0.3), Tri([(60, 54), (70, 48), (65, 58)], 'stone', z=0.2),
    Tri([(64, 64), (73, 62), (66, 68)], 'stone', z=0.1),
    # arm
    Cap(42, 60, 35, 67, 2.6, 2, 'body', z=2), E(34, 68, 2.6, 2, 'stone', z=2.1),
    # neck & head
    Cap(47, 52, 36, 34, 7, 5.5, 'body', z=1.5), Cap(43, 52, 33, 36, 3.2, 2.4, 'belly', z=1.7),
    Tri([(42, 38), (48, 30), (47, 41)], 'stone', z=1.4),
    E(30, 28, 10, 8, 'body', z=2, rot=-0.1), E(20, 31, 7.5, 4.8, 'body', z=2.2), E(22, 35, 6.5, 2.4, 'belly', z=2.3),
    Tri([(16, 34), (17, 37), (18, 34)], 'horn', z=2.4), Tri([(21, 35), (22, 38), (23, 35)], 'horn', z=2.4),
    Cap(34, 24, 46, 13, 2.4, 1, 'horn', z=1.8), Cap(30, 22, 37, 9, 2.2, 1, 'horn', z=2.5),
    Spot(48, 58, 2.2, 'accent', z=1), Spot(44, 70, 1.8, 'accent', z=1),
    Eye(27, 27, 2.8, 'fierce', iris='#6fe0c8')])
D['glowick'] = (dict(body='#5a4a3a', accent='#ffd85a', dark='#2a1a1a', wing='#e8f0ff', flame='#ff9a3a'), T(bug(eye='round', mouth='smile', wings=None) + [
    Leaf(52, 60, 16, 10, -0.9, 'wing', z=-0.4), Flame(66, 70, 14, 10, 'flame', z=0.6)], s=0.9))
D['blazewing'] = (dict(body='#6a3a2a', accent='#ffb03a', dark='#2a1a1a', wing='#ffe0a0', flame='#ff7a2a'), T(bug(eye='fierce', wings='moth') + [
    Flame(66, 74, 18, 12, 'flame', z=0.6)], s=1.2))
D['lambkin'] = (dict(body='#f4efe4', belly='#fffaf0', accent='#3a3440', inner='#e8b0b0', nose='#3a3440'),
                T(quad('round', 'stub', stout=1.3, leg=0.8, snout=True) + [E(46, 62, 20, 14, 'body', z=0.6), E(40, 43, 9, 5, 'body', z=3.1)], s=0.9))
D['rammoth'] = (dict(body='#e8e4dc', belly='#fff8ec', accent='#8a6a4a', inner='#e8b0b0', nose='#3a3440'),
                T(quad('curl', 'stub', eye='fierce', stout=1.4, leg=1.2, snout=True) + [E(50, 64, 24, 16, 'body', z=0.6)], s=1.3))
D['hushling'] = (dict(body='#8a7a6a', belly='#e8dcc8', wing='#5a4a3a', beak='#e8c05a', feet='#e8c05a', crest='#5a4a3a'),
                 [E(48, 70, 18, 17, 'body', z=0), E(48, 74, 11, 11, 'belly', z=1),
                  Leaf(32, 64, 16, 9, 2.2, 'wing', z=1.5), Leaf(64, 64, 16, 9, 0.9, 'wing', z=1.5),
                  Tri([(34, 50), (32, 38), (42, 46)], 'crest', z=2.5), Tri([(54, 46), (62, 36), (62, 50)], 'crest', z=2.5),
                  E(48, 54, 16, 13, 'body', z=2), E(41, 54, 6, 6, 'belly', z=2.1), E(55, 54, 6, 6, 'belly', z=2.1),
                  Tri([(46, 57), (50, 57), (48, 62)], 'beak', z=3),
                  Cap(42, 84, 42, 90, 1.5, 1.5, 'feet', z=-1), Cap(54, 84, 54, 90, 1.5, 1.5, 'feet', z=-1),
                  Eye(41, 54, 3.4, iris='#f0c43a'), Eye(55, 54, 3.4, iris='#f0c43a')])
D['strixage'] = (dict(body='#5a4a6a', belly='#e8dcf0', wing='#3a2a4a', beak='#e8c05a', feet='#e8c05a', crest='#8a6ab8', accent='#f0c43a'), T(
                 [Leaf(56, 58, 30, 16, -0.4, 'wing', z=-0.5), Leaf(40, 58, 30, 16, -2.7, 'wing', z=2.5),
                  E(48, 70, 18, 18, 'body', z=0), E(48, 74, 11, 12, 'belly', z=1),
                  Tri([(32, 48), (26, 30), (42, 44)], 'crest', z=2.5), Tri([(54, 44), (68, 28), (64, 48)], 'crest', z=2.5),
                  E(48, 52, 17, 14, 'body', z=2), E(41, 52, 6.5, 6.5, 'belly', z=2.1), E(55, 52, 6.5, 6.5, 'belly', z=2.1),
                  Tri([(46, 56), (50, 56), (48, 62)], 'beak', z=3),
                  Cap(42, 86, 42, 90, 1.5, 1.5, 'feet', z=-1), Cap(54, 86, 54, 90, 1.5, 1.5, 'feet', z=-1),
                  Eye(41, 52, 3.4, 'fierce', iris='#f0c43a'), Eye(55, 52, 3.4, 'fierce', iris='#f0c43a')], s=1.3, dy=-2))
D['tiamat'] = (dict(body='#1e3a8a', belly='#bfe8ff', accent='#6fe0c8', wing='#2a6ad0', stone='#e8c05a', fin='#7fe8ff'), [
    # great fin-wings rising behind
    Leaf(56, 60, 46, 26, -0.95, 'wing', z=-3), Leaf(52, 58, 38, 18, -1.45, 'wing', z=-3.5),
    Leaf(60, 64, 30, 14, -0.45, 'fin', z=-2.8),
    # tail coil
    Cap(92, 60, 86, 76, 2, 4.5, 'body', z=-2), Tri([(90, 56), (96, 50), (94, 62)], 'fin', z=-2.1),
    Cap(86, 76, 72, 86, 4.5, 7.5, 'body', z=-1.5),
    Cap(72, 86, 52, 85, 7.5, 9.5, 'body', z=-1), Cap(70, 89, 54, 89, 2.5, 3.5, 'belly', z=-0.8),
    # rising body
    Cap(52, 84, 44, 64, 10, 8.5, 'body', z=0), Cap(47, 83, 40, 65, 5, 4.5, 'belly', z=0.5),
    Tri([(54, 70), (64, 64), (58, 76)], 'fin', z=-0.2), Tri([(52, 58), (62, 52), (54, 64)], 'fin', z=-0.1),
    # neck
    Cap(44, 64, 34, 42, 8, 6, 'body', z=1), Cap(40, 64, 30, 44, 4, 3, 'belly', z=1.3),
    Tri([(42, 46), (52, 40), (44, 50)], 'fin', z=0.9),
    # head
    E(27, 34, 11, 8.5, 'body', z=2, rot=-0.15), E(16, 38, 8, 5, 'body', z=2.2), E(18, 42, 7, 2.6, 'belly', z=2.3),
    Leaf(34, 34, 16, 8, -0.35, 'fin', z=1.6), Leaf(33, 30, 14, 6, -0.9, 'fin', z=1.5),
    Cap(31, 28, 42, 12, 2.6, 1, 'stone', z=1.7), Cap(26, 26, 32, 8, 2.4, 1, 'stone', z=2.6),
    # the Draco Queen's crown: a band of gold spikes with a sea-glass gem
    Cap(17, 29, 27, 26.5, 1.5, 1.5, 'stone', z=2.65),
    Tri([(16.5, 29.5), (17, 22), (20, 28.5)], 'stone', z=2.66), Tri([(20, 28.5), (21.5, 19.5), (24, 27.5)], 'stone', z=2.66),
    Tri([(23.5, 27.5), (26, 21), (27.5, 26.5)], 'stone', z=2.66), Spot(21.5, 27.5, 1.3, 'accent', z=2.7),
    Cap(12, 41, 3, 47, 1.1, 0.5, 'accent', z=2.4), Cap(15, 43, 8, 53, 1.1, 0.5, 'accent', z=2.4),
    Spot(47, 74, 2.4, 'accent', z=1), Spot(40, 56, 2, 'accent', z=1.5), Spot(62, 86, 2.4, 'accent', z=-0.6), Spot(80, 80, 2, 'accent', z=-1.2),
    Eye(23, 33, 3, 'fierce', iris='#6fe0c8')])
