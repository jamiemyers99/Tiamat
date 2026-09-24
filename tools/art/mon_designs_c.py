"""Group C Morph designs: (materials, parts) per species, same format as mon_designs.D.
Coordinates are in a 96x96 box; ground is y~90; Morphs face left.
"""
import math
from mongen import E, Cap, Tri, Leaf, Flame, Eye, Mouth, Spot
from mon_designs import T


# -- small shape helpers ------------------------------------------------------
def _xf(pts, x, y, ang=0.0, sx=1.0, sy=1.0):
    """Scale local points by (sx, sy), rotate clockwise by ang (radians) and move to (x, y)."""
    ca, sa = math.cos(ang), math.sin(ang)
    return [(x + (px * sx) * ca - (py * sy) * sa, y + (px * sx) * sa + (py * sy) * ca) for px, py in pts]


_BOLT = [(-0.15, 0.0), (0.25, 0.0), (0.02, -0.38), (0.28, -0.38), (-0.25, -1.0), (-0.08, -0.55), (-0.35, -0.55)]


def bolt(x, y, h, w, ang, mat, z=0, view='both'):
    """Lightning-bolt shape standing on (x, y), h tall, pointing up (ang rotates it clockwise)."""
    return Tri(_xf(_BOLT, x, y, ang, w, h), mat, z, view)


def star(x, y, r, mat, z=5, view='both', ang=0.0):
    """Four-point sparkle."""
    pts = []
    for i in range(8):
        a = ang + i * math.pi / 4 - math.pi / 2
        rr = r if i % 2 == 0 else r * 0.38
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    return Tri(pts, mat, z, view, flat=True)


def band(pts, w, mat, z=0, view='both', w1=None):
    """A polyline thickened into a polygon (w at the start, tapering to w1 at the end)."""
    w1 = w if w1 is None else w1
    n = len(pts)
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        ax, ay = pts[max(0, i - 1)]
        bx, by = pts[min(n - 1, i + 1)]
        dx, dy = bx - ax, by - ay
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        ww = (w + (w1 - w) * i / max(1, n - 1)) / 2
        left.append((x + nx * ww, y + ny * ww))
        right.append((x - nx * ww, y - ny * ww))
    return Tri(left + right[::-1], mat, z, view)


def pincer(hx, hy, ang, s, mat, z=0, tip=None, cute=False, view='both'):
    """A scorpion/crab claw: a swollen hand at (hx, hy) with two fingers pointing along ang."""
    ca, sa = math.cos(ang), math.sin(ang)

    def P(u, v):
        return (hx + (u * ca - v * sa) * s, hy + (u * sa + v * ca) * s)
    out = [E(hx, hy, s, 0.74 * s, mat, z, rot=ang, view=view)]
    if cute:
        for (u, v, rx, ry, da) in ((1.0, -0.42, 0.66, 0.38, -0.3), (0.95, 0.44, 0.58, 0.34, 0.35)):
            x, y = P(u, v)
            out.append(E(x, y, rx * s, ry * s, mat, z + 0.01, rot=ang + da, view=view))
            if tip:
                x, y = P(u + 0.5, v * 0.8)
                out.append(Spot(x, y, 0.26 * s, tip, z + 0.02, view))
    else:
        out.append(band([P(0.5, -0.32), P(1.15, -0.52), P(1.8, -0.18)], 0.62 * s, mat, z + 0.01, view, w1=0.1 * s))
        out.append(band([P(0.5, 0.36), P(1.1, 0.52), P(1.65, 0.24)], 0.55 * s, mat, z + 0.01, view, w1=0.1 * s))
        if tip:
            out.append(Tri([P(1.35, -0.62), P(1.55, -0.95), P(1.6, -0.52)], tip, z + 0.02, view))
    return out


def crystal(x, y, h, w, ang, mat, z=0, view='both'):
    """A pointed crystal prism standing on (x, y), pointing up (ang rotates it clockwise)."""
    pts = [(-0.5, 0.0), (-0.5, -0.68), (0.0, -1.0), (0.5, -0.68), (0.5, 0.0)]
    return Tri(_xf(pts, x, y, ang, w, h), mat, z, view)


def _spikes(segs, cx, cy, mat, dz=-0.005, L=4.0, W=2.0):
    """Little outward spikes along a chain of (x, y, r, z) segments, pointing away from (cx, cy)."""
    out = []
    for x, y, r, z in segs:
        dx, dy = x - cx, y - cy
        d = math.hypot(dx, dy) or 1
        dx, dy = dx / d, dy / d
        bx, by = x + dx * r * 0.7, y + dy * r * 0.7
        out.append(Tri([(bx - dy * W, by + dx * W), (x + dx * (r + L), y + dy * (r + L)), (bx + dy * W, by - dx * W)], mat, z + dz))
    return out


NEW = {}

# 1. stingrix -- small cheeky scorpion with a big curled tail and a magenta venom bulb
NEW['stingrix'] = (dict(body='#b86ac8', accent='#ff4aa8', dark='#3a1a4a', blush='#ff8ac0'), T([
    # tail curling up and over the back (behind), ending in a big venom bulb
    E(66, 78, 7, 6, 'body', z=-1.6), E(74, 70, 6.5, 6.5, 'body', z=-1.5), E(78, 60, 6, 6, 'body', z=-1.4),
    E(76, 50, 5.5, 5.5, 'body', z=-1.3), E(69, 43, 5, 5, 'body', z=-1.2),
    E(58, 42, 8.5, 7.5, 'accent', z=-1.1),
    band([(51, 44), (48, 48), (48.5, 53)], 3.4, 'dark', z=-1.05, w1=0.4), E(48.5, 57, 1.2, 1.7, 'accent', z=-1.0),
    # legs + abdomen
    Cap(52, 82, 56, 89, 1.6, 1.3, 'dark', z=-0.5), Cap(60, 82, 65, 89, 1.6, 1.3, 'dark', z=-0.5),
    E(56, 79, 12, 8.5, 'body', z=0),
    Cap(48, 84, 45, 89.5, 1.7, 1.4, 'dark', z=1.2), Cap(56, 84, 55, 89.5, 1.7, 1.4, 'dark', z=1.2), Cap(63, 84, 64, 89.5, 1.7, 1.4, 'dark', z=1.2),
    # far claw
    Cap(32, 68, 22, 64, 2.6, 2.2, 'body', z=-0.3), *pincer(18, 61, math.pi + 0.45, 6, 'body', z=-0.25, tip='accent', cute=True),
    # big round head
    E(36, 67, 14, 12.5, 'body', z=2),
    # near claw
    Cap(32, 78, 22, 78, 3, 2.6, 'body', z=2.5), *pincer(18, 78, math.pi + 0.15, 7, 'body', z=2.6, tip='accent', cute=True),
    Spot(25, 73, 2.2, 'blush', z=99), Spot(48, 73, 2.2, 'blush', z=99),
    Eye(30, 67, 4.4, iris='#ff4aa8'), Eye(43, 67, 4.4, iris='#ff4aa8'), Mouth(36.5, 74.5, 5, 'fang')], s=0.88, dx=1))

# 2. scorvex -- huge armoured scorpion, dripping glowing stinger
NEW['scorvex'] = (dict(body='#3c1e56', shell='#6a3a8e', accent='#ff4aa8', spike='#f0d0f0', dark='#1c0c28', inner='#ff4aa8'), T([
    # tail (behind): armoured segments arcing high over the back
    E(78, 68, 8, 7, 'body', z=-1.6), E(85, 57, 7, 6.5, 'body', z=-1.5), E(87, 45, 6.5, 6, 'body', z=-1.4),
    E(83, 34, 6, 5.5, 'body', z=-1.3), E(75, 26, 5.5, 5, 'body', z=-1.2),
    *[E(x, y, r * 0.8, r * 0.45, 'shell', z=zz + 0.01, rot=a) for x, y, r, zz, a in
      [(79, 65, 7, -1.6, -0.9), (86, 54, 6, -1.5, -1.3), (87, 42, 5.5, -1.4, -1.7), (82, 31, 5, -1.3, -2.2), (74, 23, 4.5, -1.2, -2.8)]],
    *_spikes([(78, 68, 8, -1.6), (85, 57, 7, -1.5), (87, 45, 6.5, -1.4), (83, 34, 6, -1.3), (75, 26, 5.5, -1.2)], 70, 48, 'spike'),
    E(63, 24, 9, 7.5, 'accent', z=-1.1), E(64, 19.5, 7, 3.5, 'shell', z=-1.05),
    band([(56, 25), (50, 28), (47, 34), (47, 40)], 4, 'spike', z=-1.0, w1=0.5),
    E(47, 45, 1.5, 2.2, 'accent', z=-0.9), E(47.5, 50, 1, 1.4, 'accent', z=-0.9),
    # far legs
    *[c for x in (50, 60, 70) for c in (Cap(x, 76, x + 8, 75, 2.2, 2, 'dark', z=-0.8), Cap(x + 8, 75, x + 12, 89, 2, 1.1, 'dark', z=-0.8))],
    # abdomen with overlapping armour plates
    E(62, 72, 19, 11, 'body', z=0),
    Tri([(47, 63), (51, 55), (53, 63)], 'spike', z=0.09), Tri([(58, 62), (63, 54), (64, 62)], 'spike', z=0.1), Tri([(69, 64), (74, 57), (75, 65)], 'spike', z=0.11),
    E(50, 67, 9, 6, 'shell', z=0.1), E(61, 66, 9, 6, 'shell', z=0.11), E(72, 68, 7.5, 5.5, 'shell', z=0.12),
    Spot(61, 63.5, 1.3, 'accent', z=0.2), Spot(72, 66, 1.1, 'accent', z=0.2),
    # far pincer, held forward and high
    Cap(40, 64, 32, 54, 3.8, 3.4, 'body', z=-0.5), *pincer(26, 46, math.pi + 0.7, 7, 'shell', z=-0.45, tip='spike'),
    # near legs
    *[c for x in (48, 58, 68) for c in (Cap(x, 80, x - 8, 78, 2.4, 2.2, 'dark', z=1.8), Cap(x - 8, 78, x - 12, 89, 2.2, 1.2, 'dark', z=1.8))],
    # head
    E(36, 70, 14, 10.5, 'body', z=2), E(38, 65, 12, 6, 'shell', z=2.1),
    Tri([(22, 72), (26, 72), (23, 80)], 'spike', z=2.3), Tri([(27, 74), (31, 74), (29, 81)], 'spike', z=2.3),
    Spot(32, 62.5, 1.7, 'inner', z=2.4), Spot(40, 61.5, 1.6, 'inner', z=2.4), Spot(47, 63, 1.3, 'inner', z=2.4),
    # near pincer (huge)
    Cap(32, 76, 22, 74, 5, 4.5, 'body', z=3), Cap(22, 74, 17, 64, 4.5, 5, 'body', z=3.05),
    *pincer(15, 58, math.pi + 0.45, 9.5, 'shell', z=3.1, tip='spike'),
    Eye(27, 68, 3, 'fierce', col='#ff4aa8', iris='#ffe8f4'), Eye(37, 67.5, 3, 'fierce', col='#ff4aa8', iris='#ffe8f4')], s=0.9, dx=1))

# 3. zaplet -- tiny happy eel with lightning fins
NEW['zaplet'] = (dict(body='#3a7ad8', belly='#e8f4ff', accent='#ffe03a', blush='#ff9ac0'), [
    Cap(60, 85, 70, 81, 4.5, 2.6, 'body', z=-1), bolt(70, 83, 14, 11, 0.9, 'accent', z=-1.1),
    Cap(46, 84, 60, 85, 8, 5, 'body', z=0),
    Cap(44, 82, 42, 70, 8.5, 8, 'body', z=0.5), Cap(38, 83, 37, 73, 4, 4, 'belly', z=0.6),
    bolt(32, 58, 15, 11, -0.7, 'accent', z=1.5), bolt(52, 56, 15, -11, 0.6, 'accent', z=1.5),
    E(42, 63, 14.5, 13, 'body', z=2), E(42, 69, 8, 5, 'belly', z=2.1),
    Spot(30, 67, 2.2, 'blush', z=99), Spot(54, 67, 2.2, 'blush', z=99),
    star(18, 50, 6, 'accent'), star(69, 49, 4.5, 'accent'), star(65, 67, 3.4, 'accent'),
    Eye(35.5, 62, 4.3, iris='#2fa8ff'), Eye(48.5, 62, 4.3, iris='#2fa8ff'), Mouth(42, 68, 4, 'open')])

# 4. thundeel -- big moray rearing from a coil, gaping fanged jaws, glowing bolts
NEW['thundeel'] = (dict(body='#1e3c86', belly='#9cc0ec', accent='#ffe03a', fin='#2e62c8', inner='#8a1a2a', face='#f6f2e0'), T([
    Cap(84, 80, 72, 88, 3, 6, 'body', z=-1.5), bolt(86, 81, 16, 12, 0.7, 'accent', z=-1.6),
    Cap(72, 88, 50, 88, 6, 9, 'body', z=-1), Cap(50, 88, 36, 80, 9, 9, 'body', z=-0.5), Cap(36, 80, 50, 70, 9, 9, 'body', z=0),
    Tri([(46, 24), (56, 24), (58, 32), (64, 34), (64, 44), (70, 48), (68, 58), (72, 64), (62, 72), (60, 60), (58, 46), (52, 34)], 'fin', z=-0.2),
    Cap(52, 72, 56, 52, 9.5, 8.5, 'body', z=0.5), Cap(56, 52, 46, 34, 8.5, 7.5, 'body', z=1),
    Cap(46, 72, 48, 54, 4, 3.6, 'belly', z=0.6), Cap(48, 52, 41, 39, 3.6, 3.2, 'belly', z=1.1),
    band([(55, 72), (58.5, 67), (54, 63), (58, 58), (54, 53), (56.5, 48), (51, 44), (53, 40), (48.5, 37)], 2.4, 'accent', z=1.05),
    band([(40, 84), (44, 79), (46, 82), (50, 75)], 2.4, 'accent', z=0.05),
    band([(46, 86), (52, 82), (56, 87), (62, 83), (66, 87), (72, 84), (76, 86)], 2.4, 'accent', z=-0.45),
    Tri([(14, 39), (34, 40), (34, 46), (16, 50)], 'inner', z=1.9),
    E(38, 34, 13, 9, 'body', z=2, rot=0.15),
    Tri([(30, 29), (12, 35), (13, 40), (34, 40)], 'body', z=2.1),
    Tri([(34, 44), (17, 49), (15, 53), (38, 50)], 'body', z=2.1),
    *[Tri([(x - 1.5, 39.5), (x + 1.5, 39.5), (x, 44)], 'face', z=2.2) for x in (16, 21, 26, 31)],
    *[Tri([(x - 1.5, 49.5), (x + 1.5, 49), (x, 45)], 'face', z=2.2) for x in (19, 24, 29)],
    Eye(33, 32, 3.2, 'fierce', col='#ffe03a', iris='#fffae0')], s=0.94, dy=-5.5))

# 5. hollowisp -- little ghost wisp with a lantern core
NEW['hollowisp'] = (dict(body='#5a4a8a', belly='#c8f0ff', accent='#8af0e0', blush='#ff9ad8', inner='#8af0e0'), [
    # wispy tail sweeping right and curling up
    Cap(52, 72, 64, 79, 9, 5.5, 'body', z=-1), Cap(64, 79, 74, 77, 5.5, 3.6, 'body', z=-1.1), Cap(74, 77, 79, 69, 3.6, 2.2, 'body', z=-1.2),
    Cap(79, 69, 77, 63, 2.2, 1, 'body', z=-1.25),
    # ghost-flame tuft
    Cap(43, 47, 45, 40, 3.4, 2.8, 'body', z=0.9), Cap(45, 40, 50.5, 36.5, 2.8, 2, 'body', z=0.9), Cap(50.5, 36.5, 54, 39.5, 2, 1.2, 'body', z=0.9),
    Spot(78, 61, 1.8, 'accent', z=-1.2), Spot(81, 57, 1.1, 'accent', z=-1.2),
    E(45, 68, 13, 11, 'body', z=0.8),
    E(29, 66, 3.6, 2.5, 'body', z=1.2, rot=0.5), E(61, 66, 3.4, 2.4, 'body', z=0.9, rot=-0.5),
    E(45, 58, 16, 14, 'body', z=1),
    E(45, 72, 5.5, 5.5, 'belly', z=1.5), Flame(45, 75, 7, 4.5, 'inner', z=1.6),
    Spot(32, 63, 2.2, 'blush', z=99), Spot(58, 63, 2.2, 'blush', z=99),
    Eye(38, 57, 4.6, iris='#3ad8c0'), Eye(52, 57, 4.6, iris='#3ad8c0'), Mouth(45, 64.5, 3, 'smile')])

# 6. grimshroud -- tall hooded reaper spirit carrying a soul lantern
NEW['grimshroud'] = (dict(body='#2e2450', dark='#150f2a', muzzle='#150f2a', face='#07040f', hand='#bfeaff', accent='#8af0e0', inner='#effffb'), T([
    # tattered cape streaming behind
    Tri([(52, 30), (66, 36), (78, 52), (86, 70), (88, 84), (82, 78), (80, 86), (74, 76), (70, 86), (65, 74), (58, 58)], 'dark', z=-1),
    # far sleeve with a bony hand hanging down
    # cloak
    Tri([(34, 34), (54, 32), (62, 46), (67, 62), (69, 80), (65, 75), (63, 86), (59, 77), (55, 85), (51, 76), (46, 86), (42, 77), (37, 84), (34, 75), (29, 80), (27, 68), (26, 54), (28, 42)], 'body', z=0),
    Tri([(40, 46), (43, 46), (42, 80), (39, 76)], 'dark', z=0.1), Tri([(51, 46), (54, 46), (56, 78), (53, 74)], 'dark', z=0.1), Tri([(60, 52), (62, 54), (64, 74), (61, 70)], 'dark', z=0.1),
    # hood with a long drooping tip
    Tri([(46, 16), (60, 12), (60, 26), (50, 30)], 'body', z=1.4), E(50, 25, 9, 11, 'body', z=1.45, rot=0.7),
    E(40, 28, 13, 13, 'body', z=1.5), E(35, 30, 9.5, 11, 'muzzle', z=1.55), E(34, 31, 7.5, 9.5, 'face', z=1.6),
    # near sleeve reaching forward, bony hand holding the lantern chain
    Cap(34, 40, 22, 52, 5, 7.5, 'body', z=2), E(20, 54, 5, 3, 'dark', z=2.05, rot=-0.9),
    Cap(19, 55, 15, 58, 1.5, 1.2, 'hand', z=2.2), Cap(21, 56, 18, 60, 1.3, 1, 'hand', z=2.2), Cap(15, 58, 14, 61, 1.1, 0.8, 'hand', z=2.2),
    Cap(15, 58, 15, 63, 0.6, 0.6, 'dark', z=2.15),
    Tri([(10, 66), (20, 66), (15, 61)], 'dark', z=2.3), E(15, 71.5, 5, 6, 'accent', z=2.3), Flame(15, 75, 7, 4, 'inner', z=2.35),
    Cap(10, 67, 10, 77, 0.6, 0.6, 'dark', z=2.36), Cap(20, 67, 20, 77, 0.6, 0.6, 'dark', z=2.36), Cap(11, 78, 19, 78, 1.4, 1.4, 'dark', z=2.4),
    # drifting soul wisps
    Spot(74, 26, 1.9, 'accent', z=3), Spot(77.5, 23, 1, 'accent', z=3), Spot(84, 44, 1.6, 'accent', z=3), Spot(20, 24, 1.6, 'accent', z=3), Spot(17, 27, 0.9, 'accent', z=3),
    Eye(30.5, 31, 2.6, 'fierce', col='#8af0e0', iris='#effffb'), Eye(38.5, 31, 2.6, 'fierce', col='#8af0e0', iris='#effffb')], s=0.94, dy=-3))


# 7. oculith -- floating stone ring with one giant glowing eye
def _runes(cx, cy, rx, ry, mat, z, n=8):
    out = []
    for i in range(n):
        a = i * 2 * math.pi / n + 0.3
        x, y = cx + math.cos(a) * rx, cy + math.sin(a) * ry
        t = a + math.pi / 2
        ct, st = math.cos(t), math.sin(t)
        if i % 3 == 0:
            out.append(Cap(x - ct * 2.6, y - st * 2.6, x + ct * 2.6, y + st * 2.6, 1.0, 1.0, mat, z))
            out.append(Cap(x - ct * 0.5 + math.cos(a) * 1.8, y - st * 0.5 + math.sin(a) * 1.8, x, y, 0.9, 0.9, mat, z))
        elif i % 3 == 1:
            out.append(Tri([(x - ct * 2.4 + math.cos(a) * 1.6, y - st * 2.4 + math.sin(a) * 1.6), (x - math.cos(a) * 2, y - math.sin(a) * 2),
                            (x + ct * 2.4 + math.cos(a) * 1.6, y + st * 2.4 + math.sin(a) * 1.6)], mat, z))
        else:
            out.append(Spot(x, y, 1.6, mat, z))
    return out


NEW['oculith'] = (dict(blush='#5a4a68', stone='#7a6e86', void='#160a20', face='#f2ead8', inner='#d04aff', nose='#12081a', accent='#e05aff', muzzle='#c83a4a', shell='#4a2a5a', body='#7a6e86'), [
    # jagged crown of standing stones and a hanging shard
    Tri([(30, 32), (28, 16), (38, 26)], 'stone', z=-0.3), Tri([(36, 26), (40, 8), (46, 24)], 'stone', z=-0.3), Tri([(45, 23), (50, 4), (55, 23)], 'stone', z=-0.3),
    Tri([(54, 24), (60, 10), (62, 28)], 'stone', z=-0.3), Tri([(62, 28), (70, 18), (68, 34)], 'stone', z=-0.3),
    Tri([(38, 70), (48, 86), (58, 70)], 'stone', z=-0.3),
    # orbiting pebbles
    E(11, 40, 3.6, 3.1, 'stone', z=1), E(86, 58, 3.2, 2.7, 'stone', z=1), E(16, 72, 2.6, 2.2, 'stone', z=-1),
    E(82, 26, 2.8, 2.3, 'stone', z=-1), E(76, 78, 2.2, 1.9, 'stone', z=1),
    E(48, 48, 25, 27, 'stone', z=0), Leaf(28, 48, 40, 27, 0, 'void', z=0.2),
    *_runes(48, 48, 20.5, 22.5, 'accent', 0.3),
    # the eye
    Leaf(31, 48.5, 34, 21, 0, 'face', z=0.25),
    Cap(33.5, 46, 38, 47, 0.7, 0.5, 'muzzle', z=0.45), Cap(34, 52, 38.5, 50, 0.7, 0.5, 'muzzle', z=0.45), Cap(61, 45, 56, 47, 0.7, 0.5, 'muzzle', z=0.45),
    Cap(60, 52, 56, 50, 0.7, 0.5, 'muzzle', z=0.45),
    E(45, 48, 7.5, 7.5, 'inner', z=0.5), E(45, 48, 2, 6, 'nose', z=0.6),
    Leaf(28, 48, 40, 27, 0, 'stone', z=0.25, view='back'),
    Cap(36, 48, 60, 48, 1.1, 1.1, 'accent', z=0.3, view='back'), Spot(48, 48, 3, 'accent', z=0.31, view='back'),
    Cap(48, 40, 48, 56, 1, 1, 'accent', z=0.3, view='back')])

# 8. alloyena -- gaunt steel-plated hyena with a mane of blades
NEW['alloyena'] = (dict(body='#5e6878', plate='#c0cad8', dark='#262832', accent='#ff3a4a', inner='#5a1020', face='#f2eee2', nose='#121016'), T([
    # blade tail
    Cap(70, 60, 76, 56, 3, 2, 'body', z=-2),
    Tri([(74, 58), (84, 44), (79, 59)], 'plate', z=-1.9), Tri([(75, 60), (88, 55), (79, 62)], 'plate', z=-1.9),
    # far legs
    Cap(38, 60, 40, 76, 4, 3.2, 'body', z=-1), Cap(40, 76, 38, 89, 3, 2.6, 'body', z=-1),
    E(70, 67, 6, 7.5, 'body', z=-1), Cap(71, 72, 76, 81, 3.2, 2.6, 'body', z=-1), Cap(76, 81, 73, 89, 2.6, 2.2, 'body', z=-1),
    # blade mane along the neck and spine
    *[Tri([(x - 3.5, y + 5), (x + 5, y - h), (x + 4, y + 5)], 'plate', z=-0.1) for x, y, h in
      [(30, 38, 14), (37, 38, 17), (44, 41, 16), (51, 45, 13), (58, 49, 10), (64, 53, 7)]],
    # sloping torso, high withers
    E(53, 58, 20, 11, 'body', z=0, rot=0.3), E(39, 57, 11, 12, 'body', z=0.2),
    E(40, 51, 9, 6, 'plate', z=0.3, rot=-0.2), E(65, 61, 6.5, 5, 'plate', z=0.3, rot=0.4),
    band([(47, 55), (46, 60), (47.5, 66)], 1.8, 'dark', z=0.25, w1=0.8), band([(53, 57), (52, 62), (53.5, 67)], 1.8, 'dark', z=0.25, w1=0.8),
    band([(59, 59), (58, 63), (59.5, 68)], 1.8, 'dark', z=0.25, w1=0.8),
    band([(49, 57), (48.5, 61), (49.5, 64)], 1.1, 'accent', z=0.26, w1=0.5), band([(55, 59), (54.5, 63), (55.5, 66)], 1.1, 'accent', z=0.26, w1=0.5),
    band([(61, 61), (60.5, 64), (61.5, 67)], 1.1, 'accent', z=0.26, w1=0.5),
    # near legs: long front leg, crouched hind leg
    Cap(35, 60, 33, 77, 4.8, 3.6, 'body', z=2), Cap(33, 77, 31, 88, 3.6, 3, 'body', z=2.05), E(29, 88.5, 4.5, 2, 'dark', z=2.1),
    E(66, 68, 7, 8.5, 'body', z=2), Cap(66, 74, 72, 82, 3.6, 2.8, 'body', z=2.05), Cap(72, 82, 67, 89, 2.8, 2.4, 'body', z=2.1), E(66, 89, 4, 1.8, 'dark', z=2.15),
    # neck and big low head
    Cap(40, 50, 28, 50, 9, 8, 'body', z=2.5),
    E(28, 39, 4, 5.5, 'body', z=2.7, rot=0.25), E(28, 40, 2, 3.4, 'dark', z=2.75, rot=0.25),
    E(24, 50, 11, 10, 'body', z=3),
    E(20, 39, 3.8, 5.2, 'body', z=3.2, rot=-0.2), E(20, 40, 1.9, 3.2, 'dark', z=3.25, rot=-0.2),
    E(12, 55, 8, 5.5, 'body', z=3.1), Spot(5.5, 52.5, 2, 'nose', z=3.3),
    Tri([(14, 44), (30, 42), (33, 46), (20, 47)], 'plate', z=3.2),
    Tri([(5, 57), (20, 57), (28, 53), (26, 59), (18, 63), (8, 61)], 'inner', z=3.35),
    *[Tri([(x - 1.2, 56.8), (x + 1.2, 56.8), (x, 59.6)], 'face', z=3.4) for x in (8, 11.5, 15, 18.5)],
    *[Tri([(x - 1.2, 61), (x + 1.2, 61), (x, 58.2)], 'face', z=3.4) for x in (10, 13.5, 17)],
    Tri([(20, 57), (24, 55.5), (22, 59)], 'face', z=3.4),
    Eye(17, 48, 2.8, 'fierce', col='#ff3a4a', iris='#ffe0e0'), Eye(26, 47.5, 2.6, 'fierce', col='#ff3a4a', iris='#ffe0e0')], s=1.03, dx=1))

# 9. brutusk -- massive tusked boar with a stony hide, charging head-down
NEW['brutusk'] = (dict(body='#6a4c40', stone='#7c7874', accent='#c8643a', tusk='#f2e6c8', nose='#b8766e', dark='#2a1e1c'), T([
    Cap(80, 54, 86, 50, 2, 1.4, 'body', z=-2), Tri([(84, 47), (90, 44), (87, 52)], 'accent', z=-1.9),
    # far legs (pushing off)
    Cap(38, 70, 32, 85, 5.5, 4.8, 'body', z=-1), Cap(72, 68, 80, 85, 6, 4.8, 'body', z=-1),
    E(31, 88, 5, 2.2, 'dark', z=-0.9), E(81, 88, 5, 2.2, 'dark', z=-0.9),
    E(58, 60, 27, 19, 'body', z=0, rot=-0.08),
    # rock armour slabs on the back
    Tri([(40, 48), (50, 38), (64, 38), (68, 48), (58, 54), (44, 55)], 'stone', z=0.3),
    Tri([(64, 44), (76, 42), (84, 52), (80, 62), (68, 58)], 'stone', z=0.25),
    Tri([(46, 56), (58, 55), (62, 64), (50, 66)], 'stone', z=0.28),
    # bristly mane
    *[Tri([(x - 3.5, y + 5), (x + 4, y - h), (x + 3.5, y + 5)], 'accent', z=0.35) for x, y, h in
      [(30, 44, 10), (35, 40, 13), (41, 36, 14), (47, 34, 12), (53, 33, 9)]],
    # near legs
    Cap(42, 72, 34, 85, 6.5, 5.5, 'body', z=2), E(33, 88, 6, 2.6, 'dark', z=2.1),
    Cap(70, 72, 76, 85, 6.5, 5.5, 'body', z=2), E(77, 88, 6, 2.6, 'dark', z=2.1),
    # head, swept-back ear, snout
    Tri([(30, 44), (40, 36), (40, 50)], 'body', z=2.9),
    E(30, 60, 15, 13, 'body', z=3),
    Cap(24, 64, 13, 68, 7.5, 6.5, 'body', z=3.1), E(8, 68.5, 3.2, 6, 'nose', z=3.2),
    Tri([(16, 52), (36, 47), (34, 54), (20, 57)], 'stone', z=3.3),
    # tusks
    Cap(21, 72, 17, 64, 2.2, 2, 'tusk', z=2.95), Cap(17, 64, 19, 56, 2, 0.8, 'tusk', z=2.95),
    Cap(15, 73, 9, 66, 2.8, 2.5, 'tusk', z=3.4), Cap(9, 66, 8, 56, 2.5, 1.8, 'tusk', z=3.4), Cap(8, 56, 12, 48, 1.8, 0.7, 'tusk', z=3.4),
    Eye(25, 57, 3.2, 'fierce', col='#ff4a2a', iris='#ffe0b0'), Mouth(19, 74, 5, 'line')], s=1.05, dx=1))

# 10. rimewraith -- icy phantom crowned with jagged ice shards
NEW['rimewraith'] = (dict(body='#1f3a78', frost='#cdeeff', dark='#0c1430', face='#e4f4ff', nose='#06091c', accent='#9af0ff', hand='#d8f2ff'), [
    # far arm raised to strike (behind)
    Cap(56, 38, 70, 30, 3.6, 5, 'body', z=-0.5), Cap(70, 30, 73, 26, 2, 1.6, 'hand', z=-0.45),
    Cap(73, 26, 72, 15, 1.2, 0.4, 'hand', z=-0.44), Cap(74, 26, 79, 16, 1.2, 0.4, 'hand', z=-0.44), Cap(75, 27, 84, 21, 1.2, 0.4, 'hand', z=-0.44),
    # frozen tatters streaming behind
    Tri([(56, 40), (70, 46), (84, 50), (92, 56), (82, 58), (90, 66), (78, 64), (84, 74), (70, 66)], 'dark', z=-0.8),
    # ragged robe flowing back into a phantom tail
    Tri([(34, 44), (33, 56), (32, 66), (35, 75), (38, 68), (41, 80), (45, 71), (49, 84), (53, 74), (59, 86), (62, 76), (71, 84), (70, 74),
         (81, 78), (76, 68), (87, 67), (76, 60), (83, 52), (70, 52), (62, 44), (58, 36)], 'body', z=0),
    band([(47, 56), (51, 68), (55, 78)], 2, 'dark', z=0.1, w1=0.6), band([(40, 58), (40, 70)], 1.8, 'dark', z=0.1, w1=0.6),
    band([(58, 54), (64, 64), (70, 72)], 1.8, 'dark', z=0.1, w1=0.6),
    E(46, 42, 13, 10, 'body', z=0.5),
    # ice mantle
    *[Tri(pts, 'frost', z=0.6) for pts in ([(31, 40), (24, 31), (37, 36)], [(35, 36), (31, 26), (41, 34)], [(52, 34), (57, 24), (58, 37)], [(56, 38), (66, 30), (61, 42)])],
    # near arm reaching forward with long ice claws
    Cap(36, 42, 24, 52, 4, 6, 'body', z=2), Tri([(19, 53), (24, 55), (20, 61)], 'frost', z=2.02), Tri([(24, 55), (28, 55), (26, 60)], 'frost', z=2.02),
    Cap(22, 52, 17, 54, 2, 1.6, 'hand', z=2.05),
    Cap(17, 54, 7, 47, 1.3, 0.4, 'hand', z=2.1), Cap(17, 55, 5, 54, 1.3, 0.4, 'hand', z=2.1), Cap(17, 56, 8, 62, 1.3, 0.4, 'hand', z=2.1),
    # head: dark shroud, frost hair, crown of ice shards, pale mask
    band([(52, 22), (60, 28), (66, 38), (68, 48)], 6, 'frost', z=1.85, w1=0.8),
    E(44, 24, 11, 12, 'dark', z=1.9),
    *[Tri([(x - w, 21 + abs(x - 44) * 0.25), (x + lean, 21 - h), (x + w, 21 + abs(x - 44) * 0.25)], 'accent', z=1.95) for x, h, w, lean in
      [(33, 9, 2.6, -3), (37, 15, 2.8, -2), (41.5, 18, 3, -0.5), (46.5, 17, 3, 1), (51, 13, 2.8, 2.5), (55, 8, 2.4, 3.5)]],
    Cap(33, 21, 55, 21, 2, 2, 'accent', z=1.96),
    E(42, 26, 7.5, 8, 'face', z=2), Tri([(35, 27), (49, 27), (41, 40)], 'face', z=2),
    E(38.5, 25.5, 2.9, 3.2, 'nose', z=2.1, rot=0.5), E(45.5, 25.5, 2.9, 3.2, 'nose', z=2.1, rot=-0.5),
    E(41.5, 33.5, 2, 2.8, 'nose', z=2.1),
    Eye(38.5, 26, 2.2, 'fierce', col='#7ae8ff', iris='#f0ffff'), Eye(45.5, 26, 2.2, 'fierce', col='#7ae8ff', iris='#f0ffff', look=-1)])

# 11. montolith -- colossal golem evolved from cragmaul, mountain peaks on its shoulders
NEW['montolith'] = (dict(body='#7a746c', belly='#a8a298', accent='#5a544e', crest='#ffa43a', snow='#eef0f4'), [
    # far arm (behind)
    Cap(68, 44, 80, 60, 8, 8, 'body', z=-0.5), Cap(80, 60, 82, 70, 8, 9, 'body', z=-0.45), E(82, 77, 11, 10, 'accent', z=-0.4),
    # legs
    Cap(38, 74, 36, 83, 8.5, 8, 'body', z=0), Cap(60, 74, 62, 83, 8.5, 8, 'body', z=0),
    E(35, 87, 10, 3.5, 'body', z=0.1), E(63, 87, 10, 3.5, 'body', z=0.1),
    # far shoulder mountain range
    Tri([(54, 34), (62, 16), (67, 22), (74, 6), (82, 22), (86, 36), (70, 44)], 'body', z=0.5),
    Tri([(74, 6), (77.5, 13), (76, 12.5), (74.5, 14.5), (73, 12.5), (70.9, 13)], 'snow', z=0.55),
    Tri([(62, 16), (65.3, 20), (63.5, 19.5), (62, 21), (60.8, 19.5), (60.2, 20)], 'snow', z=0.55),
    crystal(67, 36, 12, 5, 0.1, 'crest', z=0.6), crystal(72, 38, 8, 4, 0.5, 'crest', z=0.61), crystal(62, 36, 7, 3.6, -0.4, 'crest', z=0.61),
    # torso
    E(48, 58, 27, 24, 'body', z=1), E(47, 63, 16, 15.5, 'belly', z=1.5),
    band([(33, 46), (37, 52), (34, 58), (38, 64), (36, 70)], 1.6, 'crest', z=1.55), band([(60, 44), (57, 50), (61, 56), (59, 62)], 1.6, 'crest', z=1.55),
    band([(44, 78), (47, 74), (51, 77), (54, 73)], 1.4, 'crest', z=1.6),
    # near shoulder mountain range
    Tri([(10, 42), (18, 20), (23, 26), (30, 8), (38, 24), (42, 38), (30, 46)], 'body', z=1.8),
    Tri([(30, 8), (33.5, 15), (32, 14), (30.5, 16.5), (29, 14.5), (27.3, 15)], 'snow', z=1.85),
    Tri([(18, 20), (22.2, 25), (20.5, 24.5), (19, 26), (17.5, 24.5), (16.2, 25)], 'snow', z=1.85),
    crystal(28, 40, 13, 5.5, -0.15, 'crest', z=1.9), crystal(34, 41, 8, 4, 0.35, 'crest', z=1.91), crystal(22, 41, 7, 3.6, -0.6, 'crest', z=1.91),
    # near arm with a huge fist
    Cap(24, 46, 16, 62, 9, 8.5, 'body', z=2), Cap(16, 62, 15, 70, 8.5, 9, 'body', z=2.05), E(16, 77, 11.5, 11, 'accent', z=2.2),
    band([(21, 50), (17, 56), (20, 62), (16, 68)], 1.5, 'crest', z=2.06),
    crystal(11, 65, 8, 4, -0.8, 'crest', z=2.1), crystal(12, 70, 5.5, 3.2, -1.3, 'crest', z=2.1),
    # head sunk between the shoulders, angry brow
    E(48, 37, 12.5, 11, 'body', z=3),
    Tri([(36, 32), (46.5, 35), (46, 37.5), (36.5, 35)], 'accent', z=3.1, view='front'), Tri([(60, 32), (49.5, 35), (50, 37.5), (59.5, 35)], 'accent', z=3.1, view='front'),
    Eye(42, 38, 3.1, 'fierce', col='#ffa43a', iris='#fff0c8'), Eye(54, 38, 3.1, 'fierce', col='#ffa43a', iris='#fff0c8'),
    Mouth(48.5, 44, 6, 'fang')])
