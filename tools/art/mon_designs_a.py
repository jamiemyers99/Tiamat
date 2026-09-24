"""Group A Morph designs: the Toxin frogs, Brawl kangaroos, Mind cats and Frost foxes.

Same format as mon_designs.D: species id -> (materials, parts). 96x96 box, ground y~90, facing left.
"""
import math
from mongen import E, Cap, Tri, Leaf, Flame, Eye, Mouth, Spot, Part
from mon_designs import T


# ── small shape helpers ─────────────────────────────────────────────────────
def _over(z, dz):
    """z for a detail drawn on top of a part at z. Behind-the-body parts (z<0) are re-ordered as 50-z in the back
    view, so a small offset would flip there; for them we keep the same z and let list order put the detail on top."""
    return z + dz if z >= 0 else z


def _star(x, y, r, mat, z=90, view='both', inner=0.36):
    """Four-point sparkle."""
    pts = []
    for i in range(8):
        a = -math.pi / 2 + i * math.pi / 4
        rr = r if i % 2 == 0 else r * inner
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    return Tri(pts, mat, z, view=view, flat=True)


def _crescent(cx, cy, r, ang, d, mat, z=0, view='both', n=14):
    """Crescent moon: a disc of radius r minus the same disc shifted by d toward angle ang (the opening)."""
    h = math.sqrt(max(0.01, r * r - d * d / 4))
    al = math.atan2(h, d / 2)
    pts = []
    for i in range(n + 1):
        t = ang + al + (2 * math.pi - 2 * al) * i / n
        pts.append((cx + r * math.cos(t), cy + r * math.sin(t)))
    c2x, c2y = cx + d * math.cos(ang), cy + d * math.sin(ang)
    for i in range(n + 1):
        t = ang + math.pi + al - 2 * al * i / n
        pts.append((c2x + r * math.cos(t), c2y + r * math.sin(t)))
    return Tri(pts, mat, z, view=view)


def _webfoot(x, y, w, mat, z, view='both'):
    """Flat three-toed webbed foot resting on the ground, toes pointing left. (x, y) = heel on the ground."""
    return Tri([(x + 2, y - 2.8), (x - w * 0.4, y - 2.4), (x - w, y + 0.2), (x - w * 0.74, y - 0.3),
                (x - w * 0.6, y + 0.8), (x - w * 0.36, y - 0.1), (x - w * 0.16, y + 0.8), (x + 2.6, y + 0.3)], mat, z, view=view)


def _orb(x, y, r, z, mat='accent', core='glow', halo='dot'):
    """Floating psychic orb: pale glow halo, orb, bright core. Equal z keeps the layering in the back view too
    (the halo uses 'dot' so the female recolour shifts it together with the accent orb)."""
    out = [E(x, y, r + 1.5, r + 1.5, halo, z, bulge=0.0)] if halo else []
    return out + [E(x, y, r, r, mat, z), Spot(x - r * 0.28, y - r * 0.3, r * 0.42, core, z)]


def _spikes(pts, mat, z, w=3.0, view='both'):
    """Spikes standing on a list of (x, y, length, angle) bases."""
    out = []
    for x, y, L, a in pts:
        ca, sa = math.cos(a), math.sin(a)
        px, py = -sa * w, ca * w
        out.append(Tri([(x - px, y - py), (x + ca * L, y + sa * L), (x + px, y + py)], mat, z, view=view))
    return out


def _almond(x, y, w, h, tilt, mat, z=99, view='front'):
    """Almond-shaped eye (pointed corners). tilt>0 raises the left corner."""
    pts = []
    n = 10
    for i in range(n + 1):
        t = i / n
        pts.append((-w / 2 + w * t, -h * 0.55 * math.sin(math.pi * t) ** 0.8))
    for i in range(n, -1, -1):
        t = i / n
        pts.append((-w / 2 + w * t, h * 0.45 * math.sin(math.pi * t) ** 1.2))
    c, s = math.cos(tilt), math.sin(tilt)
    return Tri([(x + px * c - py * s, y + px * s + py * c) for px, py in pts], mat, z, view=view, flat=True)


def _liner(x, y, w, h, tilt, th, mat, z=99.5, wing=0.0, view='front'):
    """Dark upper lid line along an almond eye, with an optional flick past the corner (wing<0 flicks left)."""
    top, bot = [], []
    n = 10
    for i in range(n + 1):
        t = i / n
        px = -w / 2 + w * t
        py = -h * 0.55 * math.sin(math.pi * t) ** 0.8
        top.append((px, py - th))
        bot.append((px, py + th * 0.25))
    pts = top + bot[::-1]
    if wing:
        side = -1 if wing < 0 else 1
        ex = side * (w / 2 + abs(wing))
        pts = ([(ex, -h * 0.35 - abs(wing) * 0.5)] + pts) if side < 0 else (pts[:n + 1] + [(ex, -h * 0.35 - abs(wing) * 0.5)] + pts[n + 1:])
    c, s = math.cos(tilt), math.sin(tilt)
    return Tri([(x + px * c - py * s, y + px * s + py * c) for px, py in pts], mat, z, view=view, flat=True)


def _cool_eye(x, y, w, h, tilt, iris, liner='lash', look=-0.8, pr=1.6, wing=0.0, z=99):
    """Sharp coloured eye: almond iris + dark lid liner + pupil (an Eye, so females get lashes)."""
    return [_almond(x, y, w, h, tilt, iris, z), _liner(x, y, w, h, tilt, 0.9, liner, z + 0.5, wing),
            Eye(x + look, y + 0.4, pr, 'round')]


def _toad_eye(x, y, r, z, lid=0.62):
    """Bulging toad eye: dome, golden eyeball, heavy lid, horizontal pupil."""
    return [E(x, y, r + 2.4, r + 2.2, 'body', z),
            E(x, y + 0.6, r, r * 0.95, 'eyeball', z + 0.01, view='front'),
            E(x, y - r * lid, r + 1.4, r * 0.72, 'body', z + 0.02),
            Spot(x - r * 0.5, y + r * 0.1, max(0.8, r * 0.2), 'shine', z + 0.03, view='front'),
            Eye(x + 0.3, y + r * 0.3, r * 0.55, 'sleepy')]


def _ribbon(p0, p1, p2, p3, rb, rm, rt, mat, z, n=18, peak=0.45, t0=0.0, t1=1.0, view='both', flat=False):
    """Smooth tapered tube along a cubic bezier drawn as ONE polygon (so no seams between segments).
    Radius swells rb -> rm (at `peak`) -> rt; both ends are rounded. t0/t1 draw only part of the curve."""
    def B(t):
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        return (a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1])
    def R(t):
        if t <= peak:
            return rb + (rm - rb) * math.sin(t / peak * math.pi / 2)
        return rt + (rm - rt) * math.cos((t - peak) / (1 - peak) * math.pi / 2)
    ts = [t0 + (t1 - t0) * i / n for i in range(n + 1)]
    pts = [B(t) for t in ts]
    left, right, ang = [], [], []
    for i in range(n + 1):
        a, b = B(max(0.0, ts[i] - 0.01)), B(min(1.0, ts[i] + 0.01))
        tx, ty = b[0] - a[0], b[1] - a[1]
        l = math.hypot(tx, ty) or 1.0
        nx, ny = -ty / l, tx / l
        r = R(ts[i])
        left.append((pts[i][0] + nx * r, pts[i][1] + ny * r))
        right.append((pts[i][0] - nx * r, pts[i][1] - ny * r))
        ang.append(math.atan2(ny, nx))
    def arc(c, r, a0, a1, k=6):
        return [(c[0] + r * math.cos(a0 + (a1 - a0) * j / k), c[1] + r * math.sin(a0 + (a1 - a0) * j / k)) for j in range(1, k)]
    tip = arc(pts[n], R(ts[n]), ang[n], ang[n] - math.pi)
    base = arc(pts[0], R(ts[0]), ang[0] + math.pi, ang[0])
    return Tri(left + tip + right[::-1] + base, mat, z, view=view, flat=flat)


def _shard(x, y, L, w, ang, mat, z, facet=None, view='both'):
    """Long ice crystal pointing along `ang` from its base (x, y), with an optional lighter facet."""
    ca, sa = math.cos(ang), math.sin(ang)
    def P(u, v):
        return (x + ca * u - sa * v, y + sa * u + ca * v)
    out = [Tri([P(0, -w * 0.45), P(L * 0.7, -w * 0.6), P(L, 0), P(L * 0.7, w * 0.6), P(0, w * 0.45)], mat, z, view=view)]
    if facet:
        out.append(Tri([P(L * 0.12, -w * 0.3), P(L * 0.7, -w * 0.46), P(L * 0.93, -w * 0.04), P(L * 0.66, -w * 0.02), P(L * 0.12, -w * 0.02)],
                       facet, _over(z, 0.01), view=view, flat=True))
    return out


def _gauntlet(x, y, r, z):
    """Armoured steel fist facing left: mitt, knuckle plate, thumb guard and studs."""
    return [E(x, y, r, r * 0.9, 'steel', z),
            E(x + r * 0.3, y - r * 0.7, r * 0.45, r * 0.34, 'steel', _over(z, 0.03)),
            E(x - r * 0.42, y + r * 0.04, r * 0.55, r * 0.8, 'plate', _over(z, 0.02))] + \
        _spikes([(x - r * 0.78, y - r * 0.42, r * 0.4, math.pi + 0.4), (x - r * 0.95, y + r * 0.06, r * 0.44, math.pi),
                 (x - r * 0.78, y + r * 0.54, r * 0.4, math.pi - 0.4)], 'dark', _over(z, 0.04), w=r * 0.17)


def _cat_eye(x, y, w, h, tilt, iris, look=-0.6, liner='lash'):
    """Glowing almond eye with a vertical slit pupil. The pupil is a plain part (not an Eye) so it scales with the
    sprite and the 32px icon still shows the glow instead of a dark dot."""
    return [_almond(x, y, w, h, tilt, iris, 99), _liner(x, y, w, h, tilt, 0.9, liner, 99.5),
            Tri([(x + look, y - h * 0.62), (x + look + 0.9, y + 0.1), (x + look, y + h * 0.5), (x + look - 0.9, y + 0.1)],
                liner, 99.4, view='front', flat=True),
            Spot(x + look - 1.3, y - 0.9, 0.7, 'shine', 99.6, view='front')]


NEW = {}

# ═══ Toxin frogs ═══════════════════════════════════════════════════════════
NEW['pipfrog'] = (dict(body='#7a5ac8', belly='#e8e0ff', accent='#c8f04a', blush='#ff8ad0'), T([
    # far hind leg tucked behind
    E(66, 83, 7, 6, 'body', z=-1), E(60, 89, 6, 2, 'body', z=-0.9),
    # one round squishy body
    E(52, 75, 20, 14, 'body', z=0),
    # toxic polka dots on the back
    Spot(60, 65, 3.2, 'accent', z=0.3), Spot(68, 72, 2.4, 'accent', z=0.3), Spot(52, 63, 1.8, 'accent', z=0.3),
    Spot(62, 74, 1.6, 'accent', z=0.3),
    # near hind leg
    E(63, 82, 8, 7, 'body', z=1), E(55, 89, 6.5, 2.2, 'body', z=1.1),
    # pale chin
    E(42.5, 78, 9.5, 4.3, 'belly', z=0.5),
    # tiny splayed front legs
    Cap(37, 80, 33, 87, 3.2, 2.6, 'body', z=0.4), E(31, 88.6, 3.8, 1.9, 'body', z=0.45),
    Cap(47, 81, 48, 87, 3, 2.4, 'body', z=0.35), E(47, 88.6, 3.4, 1.8, 'body', z=0.4),
    # eye domes on top of the head
    E(51, 60, 7.2, 7.2, 'body', z=0.2), E(35, 61, 7.6, 7.6, 'body', z=2.5),
    Spot(32.5, 70, 2.2, 'blush', z=99), Spot(50, 70, 2.0, 'blush', z=99),
    Eye(35, 61, 4.7, iris='#ffd23a'), Eye(51, 60, 4.4, iris='#ffd23a'),
    Mouth(41, 71.4, 9, 'smile')], s=1.15))

NEW['croakmire'] = (dict(body='#6a48b0', belly='#cbb0ec', accent='#c8f04a', fin='#3ab8b0', wart='#8462cc',
                         eyeball='#f0c83a', shine='#ffffff'), [
    # far hind leg + webbed foot
    E(76, 78, 10, 9, 'body', z=-1), _webfoot(82, 89, 12, 'fin', z=-0.9),
    # sloping warty body
    E(58, 66, 24, 19, 'body', z=0, rot=0.45),
    Spot(62, 50, 2, 'wart', z=0.2), Spot(72, 58, 2.4, 'wart', z=0.2), Spot(58, 60, 1.6, 'wart', z=0.2),
    Spot(78, 70, 1.8, 'wart', z=0.2), Spot(66, 66, 1.4, 'wart', z=0.2),
    # lime poison glands behind the eyes
    E(57, 44, 8, 3.6, 'accent', z=0.4, rot=0.45), Spot(69, 52, 2.6, 'accent', z=0.4), Spot(76, 62, 1.8, 'accent', z=0.4),
    # near haunch + webbed foot
    E(70, 78, 13, 11, 'body', z=1, rot=-0.2), _webfoot(64, 89, 14, 'fin', z=1.1),
    Spot(76, 73, 1.8, 'wart', z=1.1), Spot(68, 71, 1.3, 'wart', z=1.1),
    # head
    E(38, 49, 18, 13.5, 'body', z=2),
    # puffed throat sac
    E(34, 63, 12, 8.5, 'belly', z=2.2),
    # sturdy arms with webbed hands
    Cap(32, 66, 26, 86, 5.2, 4.2, 'body', z=2.1), _webfoot(28, 89, 11, 'fin', z=2.15),
    Cap(48, 68, 48, 86, 4.6, 3.8, 'body', z=1.5), _webfoot(51, 89, 10, 'fin', z=1.6),
    # smug half-lidded toad eyes
    *_toad_eye(47, 36, 3.6, 2.05), *_toad_eye(31, 37.5, 4, 2.5),
    Mouth(31, 54.5, 12, 'fang')])

NEW['blightoad'] = (dict(body='#482a66', belly='#8a5e98', accent='#c8f04a', horn='#6a2a78', inner='#240618',
                         tooth='#f0ead0', pit='#26143a', fin='#2a7a7a', drool='#b8f040', claw='#e8dcc8', tongue='#9a2a5a'), [
    # far hind leg
    E(80, 72, 12, 13, 'body', z=-1), _webfoot(88, 89, 14, 'fin', z=-0.9),
    # dorsal spike ridge (behind the body line)
    *_spikes([(56, 32, 12, -1.75), (66, 34, 13, -1.45), (75, 39, 12, -1.15), (82, 47, 10, -0.85), (86, 57, 6, -0.55)],
             'horn', z=-0.5, w=3.4),
    *_spikes([(55.5, 26, 5, -1.75), (66.5, 27, 5.5, -1.45), (77.5, 32, 5, -1.15), (85, 42, 3.6, -0.85)], 'accent', z=-0.5, w=1.4),
    # massive body
    E(62, 58, 30, 30, 'body', z=0, rot=0.15),
    # glowing pustules
    Spot(66, 40, 4.6, 'pit', z=0.2), Spot(66, 40, 3.4, 'accent', z=0.25),
    Spot(80, 52, 3.6, 'pit', z=0.2), Spot(80, 52, 2.6, 'accent', z=0.25),
    Spot(56, 46, 2.6, 'pit', z=0.2), Spot(56, 46, 1.8, 'accent', z=0.25),
    Spot(74, 62, 2.4, 'pit', z=0.2), Spot(74, 62, 1.6, 'accent', z=0.25),
    # near haunch + foot
    E(74, 72, 16, 15, 'body', z=1, rot=-0.3), _webfoot(68, 89, 18, 'fin', z=1.1),
    Spot(80, 70, 3.2, 'pit', z=1.1), Spot(80, 70, 2.2, 'accent', z=1.15), Spot(70, 78, 1.8, 'pit', z=1.1), Spot(70, 78, 1.2, 'accent', z=1.15),
    # crown of lime-tipped spikes on the head
    *_spikes([(24, 32, 10, -2.25), (30, 28, 14, -1.95), (38, 26, 16, -1.6), (46, 27, 13, -1.3)], 'horn', z=1.9, w=3.2),
    *_spikes([(21, 25, 4, -2.25), (28, 17, 5, -1.95), (37.5, 13, 5.5, -1.6), (48.5, 17, 4.5, -1.3)], 'accent', z=1.95, w=1.4),
    # head: skull, lower jaw and pale throat
    E(36, 42, 24, 16, 'body', z=2),
    E(34, 68, 23, 11, 'body', z=2.05), E(33, 75, 15, 5, 'belly', z=2.1),
    # gaping maw with fangs, tongue and toxic drool
    Tri([(10, 53), (20, 54), (32, 54.5), (44, 53.5), (54, 55), (48, 62), (37, 68.5), (24, 68.5), (15, 64), (9.5, 57)],
        'inner', z=2.3, view='front', flat=True),
    E(30, 66, 10, 3.2, 'tongue', z=2.35, view='front', bulge=0.5),
    Tri([(12, 53.5), (16, 54), (14, 60.5)], 'tooth', z=2.5, view='front'),
    Tri([(20, 54), (25, 54.3), (22.5, 63)], 'tooth', z=2.5, view='front'),
    Tri([(30, 54.5), (33.5, 54.5), (31.8, 59.5)], 'tooth', z=2.5, view='front'),
    Tri([(38, 54), (42.5, 53.8), (40, 61.5)], 'tooth', z=2.5, view='front'),
    Tri([(46, 54.4), (49, 54.8), (47.5, 58.5)], 'tooth', z=2.5, view='front'),
    Tri([(16, 64), (20, 66), (18.5, 59.5)], 'tooth', z=2.5, view='front'),
    Tri([(34, 68.6), (38, 68.4), (36, 62.5)], 'tooth', z=2.5, view='front'),
    Tri([(44, 64.5), (47.5, 62.5), (45, 58.5)], 'tooth', z=2.5, view='front'),
    Cap(26, 68, 25, 78, 1.5, 1.0, 'drool', z=2.6, view='front'), E(25, 79.5, 1.8, 2.2, 'drool', z=2.6, view='front'),
    Cap(41, 67, 41.5, 73, 1.2, 0.9, 'drool', z=2.6, view='front'), Cap(13, 62, 12.5, 67, 1.1, 0.8, 'drool', z=2.6, view='front'),
    # thick clawed arms
    Cap(22, 70, 16, 84, 9, 7.5, 'body', z=3), _webfoot(21, 89, 14, 'fin', z=3.1),
    *_spikes([(8, 88.5, 4, 3.0), (12.5, 89.8, 4, 2.9)], 'claw', z=3.2, w=1.2),
    Cap(52, 72, 54, 84, 7.5, 6.5, 'body', z=1.5), _webfoot(57, 89, 12, 'fin', z=1.6),
    # brow ridges and glowing eyes
    E(22, 36, 6.5, 5, 'body', z=2.6), E(42, 34, 6.5, 5, 'body', z=2.6),
    Tri([(14, 31), (28, 33.5), (26, 36.5), (16, 35)], 'horn', z=2.7), Tri([(36, 30.5), (50, 28), (48.5, 32), (37.5, 33.5)], 'horn', z=2.7),
    Eye(22, 37.5, 4, 'fierce', col='#c8f04a'), Eye(42, 35.5, 4, 'fierce', col='#c8f04a', look=-1)])

# ═══ Brawl kangaroos ═══════════════════════════════════════════════════════
NEW['pawpunch'] = (dict(body='#d8b88a', belly='#fff0d8', accent='#e2453d', inner='#f4b0a0', nose='#4a2a2a',
                        blush='#ff8a8a', cuff='#fff4e4'), T([
    # tail and far limbs
    Cap(56, 83, 76, 88, 4.8, 2.6, 'body', z=-2),
    E(57, 89, 6, 2, 'body', z=-0.6),
    Cap(57, 68, 61, 71, 2.6, 2.4, 'body', z=-0.3), E(65, 71, 7.2, 6.8, 'accent', z=-0.3),
    # small body
    E(50, 77, 11, 12, 'body', z=0), E(46, 79, 6.5, 8.5, 'belly', z=0.3),
    E(57, 82, 8, 7.5, 'body', z=0.6), E(47, 88.5, 10, 2.6, 'body', z=0.7),
    # ears
    Leaf(53, 47, 18, 9, -1.2, 'body', z=2.4), Leaf(54, 45, 13, 4.6, -1.2, 'inner', z=2.45),
    Leaf(41, 48, 18, 9.5, -1.95, 'body', z=2.5), Leaf(40.5, 46, 13, 5, -1.95, 'inner', z=2.6),
    # headband knot tails fluttering behind
    Leaf(58, 50, 12, 4.5, 0.25, 'accent', z=2.35), Leaf(58, 51, 11, 4, 0.9, 'accent', z=2.3),
    # big head
    E(46, 57, 15, 13.5, 'body', z=3),
    Tri([(31.2, 52), (38, 48.2), (46, 47), (54, 47.6), (60.6, 51), (60.8, 54.2), (54, 51), (46, 50.4), (38, 51.8), (31.8, 55.4)], 'accent', z=3.3),
    E(36, 62.5, 7.5, 5.2, 'belly', z=3.2),
    Spot(30, 60.6, 1.8, 'nose', z=102),
    # near arm with oversized glove
    Cap(47, 70, 40, 73, 3, 2.6, 'body', z=3.8), E(40, 74, 2.4, 3.9, 'cuff', z=3.9), E(32.5, 74.5, 8.2, 7.6, 'accent', z=4),
    E(37.5, 69.2, 3, 3.3, 'accent', z=4.1),
    Spot(35, 65, 1.9, 'blush', z=99), Spot(55, 63, 2.1, 'blush', z=99),
    Eye(40, 57, 4, iris='#8a4a22'), Eye(51, 57, 3.8, iris='#8a4a22'),
    Mouth(35.5, 66.4, 3, 'smile')], s=0.84))

NEW['knuckroo'] = (dict(body='#c89e6e', belly='#fbe8cc', accent='#e2453d', inner='#e8a090', nose='#3a2222',
                        cuff='#fff4e4', iris='#ffc83a', lash='#2a1810'), T([
    # strong tail sweeping to the ground
    Cap(58, 72, 90, 88, 7, 2.4, 'body', z=-2),
    # far leg
    E(64, 74, 8, 10, 'body', z=-1, rot=-0.4), E(62, 88.5, 10, 2.6, 'body', z=-0.9),
    # far arm: glove up guarding the chin
    Cap(48, 48, 36, 44, 3.2, 3, 'body', z=-0.45), E(31, 42, 6.6, 6.2, 'accent', z=-0.45),
    # headband tails flying back
    Leaf(45, 22, 18, 5, 0.05, 'accent', z=-0.3), Leaf(45, 24, 15, 4.5, 0.6, 'accent', z=-0.35),
    # torso leaning into the stance
    E(53, 60, 11, 17, 'body', z=0, rot=0.4), E(49, 62, 6.5, 12.5, 'belly', z=0.3, rot=0.4),
    # near leg
    E(59, 76, 9, 12, 'body', z=1, rot=-0.4), E(46, 88.5, 12, 3, 'body', z=1.1),
    # neck
    Cap(48, 48, 40, 34, 6, 5, 'body', z=1.5),
    # ears swept back
    Leaf(41, 22, 17, 7, -0.95, 'body', z=1.8), Leaf(35, 22, 17, 7.5, -1.45, 'body', z=2.3),
    Leaf(35.5, 20, 12, 3.6, -1.45, 'inner', z=2.35),
    # head
    E(36, 28, 11.5, 10, 'body', z=2.5), Cap(30, 30.5, 21, 33.5, 5.4, 3.8, 'body', z=2.6), Cap(29, 34.5, 21, 35.5, 3, 2.2, 'belly', z=2.65),
    Spot(18.6, 32, 1.8, 'nose', z=102),
    Tri([(25.5, 23.5), (32, 19.4), (40, 18.2), (47.4, 21.5), (47.4, 24.5), (40, 21.4), (32, 22.4), (26.5, 26.5)], 'accent', z=2.8),
    # near arm: jab forward
    Cap(47, 51, 24, 53, 3.6, 3, 'body', z=3), E(24, 53, 2.4, 3.8, 'cuff', z=3.1), E(17, 53, 7.5, 7, 'accent', z=3.2),
    E(21, 48, 2.8, 3, 'accent', z=3.25),
    *_cool_eye(29.5, 28.5, 6.4, 4.4, 0.28, 'iris', look=-1), *_cool_eye(39.5, 28.5, 5.8, 4, -0.28, 'iris', look=-1),
    Mouth(24, 37.6, 4, 'smile')], s=0.82))

NEW['gauntlord'] = (dict(body='#a8743e', belly='#f2dcb4', accent='#e2453d', steel='#6e7c96', plate='#b8c4d4', dark='#2e2228',
                         inner='#d88a78', nose='#2a1a1a', scar='#f4d4c4', iris='#ffd23a', lash='#1a0e0a'), [
    # huge tail
    Cap(60, 72, 89, 88, 10, 3.5, 'body', z=-2),
    # far arm cocked back behind the shoulder, ready to swing
    Cap(62, 42, 66, 38, 4.8, 4.8, 'accent', z=-0.6), *_gauntlet(72, 32, 10, -0.6),
    # far leg
    E(68, 74, 11, 14, 'body', z=-1, rot=-0.35), E(66, 88.5, 13, 3.2, 'body', z=-0.9),
    # headband tails
    Leaf(41, 20, 18, 5, -0.25, 'accent', z=-0.3), Leaf(41, 22, 16, 4.5, 0.3, 'accent', z=-0.35),
    # torso
    E(52, 57, 21, 24, 'body', z=0, rot=0.25), E(46, 66, 10, 12.5, 'belly', z=0.3, rot=0.15),
    # chest plate
    E(42, 47, 13, 10, 'steel', z=0.6, rot=0.3, view='front'), E(41, 46, 9, 6.5, 'plate', z=0.62, rot=0.3, view='front'),
    Tri([(38, 43), (42, 41), (44, 47), (40, 49)], 'accent', z=0.7, view='front'),
    # near leg
    E(60, 77, 14, 13, 'body', z=1, rot=-0.35), E(46, 88.5, 15, 3.4, 'body', z=1.1),
    *_spikes([(32, 88, 3.6, 3.0), (35, 89.5, 3.6, 2.95)], 'dark', z=1.2, w=1.2),
    # neck + shoulder pauldron
    Cap(46, 44, 36, 32, 7, 6, 'body', z=1.5),
    E(53, 40, 10, 7.5, 'steel', z=2.2), E(52, 39, 7, 4.8, 'plate', z=2.22),
    *_spikes([(49, 34, 7, -1.9), (57, 34, 6.5, -1.3)], 'dark', z=2.1, w=2.2),
    # ears swept back
    Leaf(36, 22, 17, 7, -0.55, 'body', z=1.8), Leaf(31, 22, 17, 7.5, -0.9, 'body', z=2.3),
    Leaf(32, 20, 12, 3.4, -0.9, 'inner', z=2.35),
    # head
    E(31, 28, 11.5, 10, 'body', z=2.5), Cap(25, 31, 15, 34, 5.8, 4.2, 'body', z=2.6), Cap(24, 35, 15, 36.2, 3.4, 2.6, 'belly', z=2.65),
    Spot(12.4, 32.6, 1.9, 'nose', z=102),
    Tri([(20, 24), (26.5, 19.4), (34.5, 18.2), (42, 21.5), (42, 24.6), (34.5, 21.6), (26.5, 22.6), (21, 27.6)], 'accent', z=2.8),
    # heavy brows + scar
    Tri([(19.5, 25), (28, 26), (28.5, 28), (20.5, 27.5)], 'dark', z=2.85, view='front'),
    Tri([(31, 26), (39, 24.5), (38.5, 27.1), (31.5, 28.3)], 'dark', z=2.85, view='front'),
    Cap(23, 21.5, 27, 35, 0.75, 0.75, 'scar', z=2.9, view='front'),
    # near arm: gauntlet thrust forward
    Cap(46, 50, 28, 60, 6.5, 6, 'body', z=3), Cap(29, 60, 25, 62, 5.4, 5.4, 'accent', z=3.1),
    *_gauntlet(18, 64, 10.5, 3.2),
    *_cool_eye(24.5, 30.8, 6.2, 4, 0.3, 'iris', look=-1.1, pr=1.5), *_cool_eye(34.5, 30.8, 5.6, 3.7, -0.3, 'iris', look=-1.1, pr=1.4),
    Mouth(20, 39, 5, 'fang')])

# ═══ Mind cats ═════════════════════════════════════════════════════════════
NEW['wispurr'] = (dict(body='#c8a8f0', belly='#fff0ff', accent='#7af0ff', inner='#ffb0e0', nose='#f07ab0',
                       blush='#ff9ad8', glow='#f4ffff', dot='#d4fcff'), T([
    # curly tail ending in a little wisp
    _ribbon((56, 84), (76, 88), (82, 68), (70, 64), 2.8, 3.0, 2.2, 'body', z=-2),
    Flame(69, 66, 10, 6.5, 'accent', z=-2, lean=-0.5),
    # sitting body
    E(52, 79, 12, 10, 'body', z=0), E(58, 83, 7, 6, 'body', z=0.4), E(45, 80, 6, 7.5, 'belly', z=0.5),
    Cap(42, 78, 41, 88, 3, 2.8, 'body', z=1), Cap(49, 79, 49, 88, 3, 2.8, 'body', z=0.6),
    E(40, 88.5, 3.6, 2, 'body', z=1.1), E(49, 88.5, 3.4, 2, 'body', z=0.7),
    # ears
    Tri([(32, 58), (32, 40), (43, 52)], 'body', z=1.8), Tri([(34.5, 55), (34, 45), (40, 52)], 'inner', z=1.85),
    Tri([(50, 52), (59, 40), (61, 58)], 'body', z=1.8), Tri([(53, 52), (58.5, 45), (59.5, 55)], 'inner', z=1.85),
    # head with cheek fluff
    Tri([(33, 64), (28, 69), (35, 70)], 'body', z=1.9), Tri([(58, 64), (64, 69), (57, 70)], 'body', z=1.9),
    E(46, 63, 15, 12.5, 'body', z=2), E(40, 68, 5, 3.2, 'belly', z=2.1),
    Spot(38.6, 66.4, 1.3, 'nose', z=102),
    Spot(34, 67, 2, 'blush', z=99), Spot(56, 67, 2, 'blush', z=99),
    Eye(40, 62, 4.4, iris='#24c8f0'), Eye(52, 62, 4.2, iris='#24c8f0'),
    Mouth(39.5, 69, 3, 'smile'),
    # floating orb
    *_orb(47, 37, 4.2, 5), _star(38, 33, 2, 'glow', z=5), _star(56, 40, 1.6, 'glow', z=5)], s=0.87))

NEW['mystaline'] = (dict(body='#b898ec', belly='#f6eaff', accent='#7af0ff', inner='#f0a0d8', nose='#c86aa8',
                         glow='#f4ffff', dot='#d4fcff', crest='#ff6ad0', iris='#5ae8ff', lash='#2a1a4a'), T([
    # long tail with a crescent-moon tip
    _ribbon((66, 60), (86, 60), (90, 40), (78, 31), 2.4, 2.8, 1.8, 'body', z=-2),
    _crescent(75, 25, 6, -2.5, 4.4, 'accent', z=-2),
    # far orb (behind)
    *_orb(60, 28, 3.6, -3), _star(66, 23, 1.4, 'glow', z=-3),
    # far legs
    Cap(67, 66, 73, 77, 3.2, 2.5, 'body', z=-1), Cap(73, 77, 71, 87, 2.5, 2.1, 'body', z=-1), E(70, 88.3, 3.4, 1.8, 'body', z=-0.9),
    Cap(47, 66, 50, 78, 2.8, 2.3, 'body', z=-1), Cap(50, 78, 49, 87, 2.3, 2.0, 'body', z=-1), E(48, 88.3, 3.4, 1.8, 'body', z=-0.9),
    # deep chest, slim waist
    E(57, 64, 10, 5.6, 'body', z=0), E(46, 62, 8, 8.5, 'body', z=0.1), E(46, 66.5, 5, 3.6, 'belly', z=0.15),
    # near hind leg
    E(64, 63, 7, 8, 'body', z=1.8), Cap(65, 69, 69, 78, 3.2, 2.5, 'body', z=1.85), Cap(69, 78, 65, 87, 2.5, 2.1, 'body', z=1.85),
    E(63.5, 88.3, 3.6, 1.9, 'body', z=1.9),
    # near front leg, reaching forward
    Cap(44, 66, 39, 78, 3.2, 2.6, 'body', z=2), Cap(39, 78, 37, 87, 2.6, 2.2, 'body', z=2), E(35.5, 88.3, 3.6, 1.9, 'body', z=2.05),
    # neck + chest fluff
    Cap(46, 60, 39, 47, 5.2, 4.4, 'body', z=2.4),
    Leaf(41, 53, 11, 5.5, 1.95, 'belly', z=2.5), Leaf(43, 55, 11, 5.5, 1.55, 'belly', z=2.52), Leaf(45, 54, 9, 4.5, 1.2, 'belly', z=2.51),
  ] + T([  # head group, enlarged about the neck joint for a bolder read
    # ears
    Tri([(26, 41), (24, 23), (34, 35)], 'body', z=2.8), Tri([(27.5, 38), (26, 28), (32, 35)], 'inner', z=2.85),
    Tri([(38, 35), (44, 21), (46, 40)], 'body', z=2.8), Tri([(40, 35), (43.5, 26), (44.5, 38)], 'inner', z=2.85),
    # head with cheek tufts
    Tri([(28, 46), (22, 50), (30, 50)], 'body', z=2.9), Tri([(42, 46), (48, 50), (41, 50)], 'body', z=2.9),
    E(35, 42, 10, 9, 'body', z=3), E(28, 46.5, 4.6, 3, 'belly', z=3.1),
    Tri([(33, 32.5), (35, 30), (37, 32.5), (35, 35.5)], 'crest', z=3.2, view='front'),
    Spot(24.4, 45.4, 0.9, 'nose', z=102),
    *_cool_eye(30, 41.5, 6.4, 4.4, 0.22, 'iris'), *_cool_eye(40, 41.5, 5.6, 4, -0.22, 'iris'),
    Mouth(27.5, 48.6, 2.5, 'line')], s=1.18, cx=39, gy=48) + [
    # near orb
    *_orb(18, 60, 4, 5), _star(25, 67, 1.6, 'glow', z=5), _star(11, 53, 1.2, 'glow', z=5)], s=0.95))

NEW['oraclynx'] = (dict(body='#4c3a86', belly='#cbbcf0', accent='#7af0ff', mane='#1a1230', inner='#9a7ad8',
                        nose='#140c26', glow='#6af4ff', dot='#d4fcff', star='#ffffff', dark='#100a1e', lash='#0a0614', tooth='#f4f0ff', shine='#ffffff'), T([
    # orbs behind
    *_orb(80, 16, 4.2, -3), *_orb(90, 44, 3.4, -3),
    # bobtail
    E(82, 54, 5, 4, 'body', z=-2, rot=-0.7), E(85, 51, 2.8, 2.4, 'dark', z=-2),
    # far legs
    Cap(76, 66, 82, 78, 5, 4, 'body', z=-1), Cap(82, 78, 80, 87, 4, 3.4, 'body', z=-1), E(78.5, 88.2, 5.5, 2.6, 'body', z=-0.9),
    Cap(52, 64, 54, 86, 4.6, 3.6, 'body', z=-1), E(53, 88.2, 5.5, 2.6, 'body', z=-0.9),
    # body sloping down from proud shoulders
    E(64, 63, 16, 9.5, 'body', z=0, rot=0.12), E(48, 58, 12.5, 13, 'body', z=0.1), E(56, 71, 11, 3.6, 'belly', z=0.2),
    _star(62, 58, 3.2, 'star', z=0.3), _star(69, 66, 2.2, 'star', z=0.3), _star(54, 66, 1.8, 'star', z=0.3),
    # near hind leg
    E(72, 65, 9.5, 10.5, 'body', z=1.8), Cap(74, 72, 78, 80, 4.8, 3.8, 'body', z=1.85), Cap(78, 80, 75, 87, 3.8, 3.4, 'body', z=1.85),
    E(73, 88.2, 6.4, 2.8, 'body', z=1.9), _star(75, 61, 2.6, 'star', z=1.9), _star(70, 71, 1.8, 'star', z=1.9),
    # near front leg, planted like a pillar
    Cap(44, 62, 39, 86, 5.6, 4.2, 'body', z=2), E(36.5, 88.2, 7, 3, 'body', z=2.05), _star(42, 74, 2, 'star', z=2.1),
    # raised neck
    Cap(46, 54, 36, 36, 9, 7.5, 'body', z=1.4),
    # flowing dark mane cascading down the neck and shoulders
    Leaf(38, 22, 20, 9, -0.55, 'mane', z=1.5), Leaf(40, 28, 26, 11, -0.1, 'mane', z=1.52),
    Leaf(42, 34, 28, 12, 0.3, 'mane', z=1.54), Leaf(44, 40, 26, 11, 0.72, 'mane', z=1.56),
    Leaf(42, 46, 22, 10, 1.15, 'mane', z=1.58), Leaf(38, 48, 18, 9, 1.6, 'mane', z=1.6), Leaf(33, 46, 14, 7, 2.0, 'mane', z=1.62),
    _star(56, 30, 2.8, 'star', z=1.7), _star(63, 42, 2, 'star', z=1.7), _star(50, 52, 2.2, 'star', z=1.7), _star(47, 22, 1.6, 'star', z=1.7),
    # ears with long tufts
    Tri([(20, 27), (18, 9), (29, 21)], 'body', z=2.6), Tri([(21.5, 24), (20, 14), (26.5, 21)], 'inner', z=2.65),
    Cap(18, 10, 15.5, 3, 1.1, 0.5, 'dark', z=2.6),
    Tri([(36, 22), (43, 6.5), (45, 27)], 'body', z=2.6), Tri([(38, 22), (42.5, 11.5), (43.5, 25)], 'inner', z=2.65),
    Cap(43, 7.5, 44.5, 2, 1.1, 0.5, 'dark', z=2.6),
    # head with long lynx cheek tufts
    Leaf(21, 39, 10, 6, 1.95, 'body', z=2.8), Leaf(39, 39, 12, 6.5, 1.0, 'body', z=2.8),
    E(30, 32, 13.5, 12, 'body', z=3), E(23, 38, 6, 4, 'belly', z=3.1),
    Spot(18, 36.4, 1.5, 'nose', z=102),
    # glowing third eye
    _almond(30, 22.5, 5.8, 2.9, -1.5708, 'glow', z=3.2), Tri([(29.6, 20.2), (30.4, 20.2), (30.3, 24.8), (29.7, 24.8)], 'lash', z=3.3, view='front'),
    *_cat_eye(23.5, 31, 7.2, 4.6, 0.32, 'glow'), *_cat_eye(35.5, 31, 6.4, 4.2, -0.32, 'glow'),
    Mouth(22.5, 41.2, 6, 'line'), Tri([(20, 41.2), (22, 41.2), (21, 44.2)], 'tooth', z=3.3, view='front'),
    Tri([(24, 41.2), (26, 41.2), (25, 43.8)], 'tooth', z=3.3, view='front'),
    # near orb
    *_orb(12, 62, 4.6, 5), _star(8, 52, 1.4, 'glow', z=5), _star(18, 70, 1.1, 'glow', z=5)], s=0.96))

# ═══ Frost foxes ═══════════════════════════════════════════════════════════
NEW['frostkit'] = (dict(body='#e8f4ff', belly='#ffffff', accent='#7ad0ff', inner='#ffc0d0', nose='#3a4a6a',
                        blush='#ffa0b8'), T([
    # big snowball tail
    E(68, 70, 13, 13, 'body', z=-2), _star(71, 65, 3.4, 'accent', z=-1.9), _star(63, 75, 2.2, 'accent', z=-1.9), _star(76, 74, 1.8, 'accent', z=-1.9),
    # sitting body
    E(51, 79, 12, 10, 'body', z=0), E(57, 83, 7, 6, 'body', z=0.4), E(44, 80, 6, 7.5, 'belly', z=0.5),
    Cap(41, 78, 40, 87, 3, 2.8, 'body', z=1), Cap(48, 79, 48, 87, 3, 2.8, 'body', z=0.6),
    E(39, 88.3, 3.8, 2.2, 'accent', z=1.1), E(48, 88.3, 3.6, 2.2, 'accent', z=0.7),
    # ears with ice-crystal tips
    Tri([(30, 57), (30, 38), (42, 51)], 'body', z=1.8), Tri([(32.5, 54), (32, 43), (39, 51)], 'inner', z=1.85),
    Tri([(28.5, 44), (30, 32), (34, 42)], 'accent', z=1.86),
    Tri([(50, 51), (59, 37), (61, 57)], 'body', z=1.8), Tri([(53, 51), (58.5, 42), (59.5, 55)], 'inner', z=1.85),
    Tri([(56, 43), (61, 33), (61, 46)], 'accent', z=1.86),
    # head with cheek fluff and a little pointed snout
    Tri([(57, 63), (64, 69), (56, 70)], 'body', z=1.9), Tri([(33, 65), (29, 72), (38, 70)], 'body', z=1.9),
    E(45, 62, 15, 12.5, 'body', z=2),
    Tri([(38, 60.5), (27, 66), (29, 68.4), (39, 70)], 'body', z=2.1), Tri([(38, 66.5), (29.5, 68.2), (39, 70.8)], 'belly', z=2.15),
    Spot(27.6, 66.2, 1.6, 'nose', z=102),
    Spot(38, 68.5, 2, 'blush', z=99), Spot(55, 67, 2.1, 'blush', z=99),
    Eye(41, 61, 4.3, iris='#3ab4ff'), Eye(52, 61, 4.1, iris='#3ab4ff'),
    Mouth(35, 70.4, 3, 'smile')], s=0.87))

NEW['glacivix'] = (dict(body='#c8e2fc', belly='#ffffff', accent='#3a9ae8', ice='#8adcff', ice2='#e6faff', inner='#8ac4ec',
                        nose='#1e2e4e', iris='#3ae0ff', lash='#14203a'), T([
    # three crystal tails
    *_shard(64, 58, 32, 9, -1.1, 'ice', z=-2.2, facet='ice2'),
    *_shard(66, 60, 32, 9, -0.6, 'ice', z=-2.0, facet='ice2'),
    *_shard(66, 63, 27, 8, -0.12, 'ice', z=-1.8, facet='ice2'),
    E(64, 61, 6, 5, 'body', z=-1.7),
    # far legs
    Cap(66, 66, 73, 77, 3.4, 2.6, 'body', z=-1), Cap(73, 77, 71, 87, 2.6, 2.2, 'body', z=-1), E(70, 88.2, 3.6, 2, 'accent', z=-0.9),
    Cap(47, 66, 51, 78, 3.0, 2.4, 'body', z=-1), Cap(51, 78, 50, 87, 2.4, 2.1, 'body', z=-1), E(48.5, 88.2, 3.6, 2, 'accent', z=-0.9),
    # deep chest, slim waist
    E(57, 64, 10, 5.8, 'body', z=0), E(46.5, 62, 8.5, 8.5, 'body', z=0.1), E(46, 66.5, 5.5, 3.8, 'belly', z=0.15),
    # near legs
    E(63, 64, 7.5, 8.5, 'body', z=1.8), Cap(64, 70, 68, 79, 3.4, 2.6, 'body', z=1.85), Cap(68, 79, 64, 87, 2.6, 2.2, 'body', z=1.85),
    E(62.5, 88.2, 4, 2.2, 'accent', z=1.9),
    Cap(44, 66, 39, 78, 3.4, 2.8, 'body', z=2), Cap(39, 78, 37, 87, 2.8, 2.3, 'body', z=2), E(35.5, 88.2, 4, 2.2, 'accent', z=2.05),
    # neck with icicle mane
    Cap(46, 61, 38, 47, 5.8, 4.8, 'body', z=2.4),
    *_spikes([(45, 47, 11, -0.55), (48, 51, 12.5, -0.35), (51, 55, 11.5, -0.18), (53, 59, 9, -0.02)], 'accent', z=2.35, w=2.6),
  ] + T([  # head group, enlarged about the neck joint for a bolder read
    # ears
    Tri([(26, 39), (23, 19), (35, 33)], 'body', z=2.8), Tri([(27.5, 36), (25, 25), (32.5, 33)], 'inner', z=2.85),
    Tri([(39, 33), (46, 15), (48, 37)], 'body', z=2.8), Tri([(41.5, 32), (45.5, 21), (46.5, 35)], 'inner', z=2.85),
    Tri([(22.4, 27.5), (23, 19), (28.6, 25.6)], 'ice', z=2.86), Tri([(42.6, 23.6), (46, 15), (47.4, 24.4)], 'ice', z=2.86),
    # head with a pointed snout
    E(35, 40, 10, 8.5, 'body', z=3),
    Tri([(29, 36), (15, 44), (17, 46), (29, 47)], 'body', z=3.1), Tri([(28, 44), (18, 46.2), (29, 48.5)], 'belly', z=3.15),
    Spot(15.6, 44.3, 1.4, 'nose', z=102),
    Tri([(40, 43), (48, 39), (45, 46)], 'accent', z=3.2, view='front'),
    *_cool_eye(29.5, 39, 6.4, 4, 0.32, 'iris', wing=-1.4), *_cool_eye(39.5, 39, 5.6, 3.6, -0.32, 'iris'),
    Mouth(23, 47.5, 3, 'line')], s=1.12, cx=38, gy=46), s=0.91))

NEW['aurovulpa'] = (dict(body='#eef6ff', belly='#ffffff', accent='#7ad0ff', crest='#b8f4ff', t1='#3ae0c0', t2='#9a7af0',
                         t3='#f07ac8', tip='#f6fbff', inner='#b8a0e8', nose='#2a2a4a', iris='#c070ff', lash='#2a1a4a'), T([
    # five flowing aurora tails fanned behind, white-tipped
    *[_ribbon(p0, p1, p2, p3, 3.5, w, 0.8, m, z=zz, t0=t0)
      for (p0, p1, p2, p3, w, col, zz) in [((64, 58), (58, 40), (50, 24), (57, 7), 7, 't2', -3.0),
                                          ((64, 58), (72, 40), (72, 22), (81, 9), 7, 't1', -2.8),
                                          ((64, 60), (80, 50), (89, 40), (88, 22), 7, 't3', -2.6),
                                          ((64, 62), (79, 62), (89, 62), (89, 46), 6.5, 't2', -2.4),
                                          ((64, 64), (76, 72), (86, 78), (89, 67), 6, 't1', -2.2)]
      for (m, t0) in ((col, 0.0), ('tip', 0.8))],
    # far legs
    Cap(66, 64, 73, 76, 3.8, 3, 'body', z=-1), Cap(73, 76, 71, 87, 3, 2.6, 'body', z=-1), E(70, 88.2, 4, 2.2, 'accent', z=-0.9),
    Cap(47, 64, 50, 77, 3.4, 2.8, 'body', z=-1), Cap(50, 77, 49, 87, 2.8, 2.4, 'body', z=-1), E(47.5, 88.2, 4, 2.2, 'accent', z=-0.9),
    # deep chest held high, slim waist
    E(57, 61, 10.5, 6.2, 'body', z=0, rot=0.15), E(46.5, 57.5, 9.5, 9.5, 'body', z=0.1), E(46, 62.5, 6, 4, 'belly', z=0.15),
    # near legs
    E(64, 63, 8, 9, 'body', z=1.8), Cap(65, 69, 69, 78, 3.8, 3, 'body', z=1.85), Cap(69, 78, 65, 87, 3, 2.6, 'body', z=1.85),
    E(63.5, 88.2, 4.4, 2.4, 'accent', z=1.9),
    Cap(44, 62, 39, 77, 3.8, 3.2, 'body', z=2), Cap(39, 77, 37, 87, 3.2, 2.7, 'body', z=2), E(35.5, 88.2, 4.4, 2.4, 'accent', z=2.05),
    # aurora mane flowing down the nape
    _ribbon((40, 30), (50, 36), (52, 46), (60, 54), 2.5, 4.6, 1.2, 't2', z=2.3),
    _ribbon((42, 34), (50, 42), (52, 50), (58, 58), 2.2, 3.8, 1.0, 't1', z=2.32),
    # neck + regal chest fluff
    Cap(45, 56, 38, 38, 7, 5.6, 'body', z=2.4),
    E(40, 50, 6.5, 9, 'body', z=2.42),
    *_spikes([(36, 56, 7, 1.95), (40, 58, 8, 1.65), (44.5, 57, 7, 1.3)], 'body', z=2.43, w=2.8),
  ] + T([  # head group, enlarged about the neck joint for a bolder read
    # ears
    Tri([(26, 30), (22, 8), (36, 24)], 'body', z=2.8), Tri([(27.5, 27), (24, 14), (33.5, 24)], 'inner', z=2.85),
    Tri([(40, 25), (47, 5), (50, 29)], 'body', z=2.8), Tri([(42.5, 24), (46.5, 11), (48.5, 27)], 'inner', z=2.85),
    # head with a pointed snout
    E(35, 32, 10.5, 9, 'body', z=3),
    Tri([(29, 28), (14, 36.5), (16, 38.5), (29, 39)], 'body', z=3.1), Tri([(28, 36.5), (17, 38.7), (29, 41)], 'belly', z=3.15),
    Spot(14.6, 36.8, 1.4, 'nose', z=102),
    # crystal crown
    *_spikes([(30, 23, 9, -1.95), (35, 21, 13, -1.6), (40, 22, 9, -1.25)], 'crest', z=3.2, w=2.1),
    Spot(35, 23, 1.6, 'accent', z=3.25),
    # cheek markings
    Tri([(38, 36), (47, 32), (44, 39)], 'accent', z=3.2, view='front'), Tri([(24, 36), (30, 35.5), (27, 38)], 'accent', z=3.2, view='front'),
    *_cool_eye(29.5, 31, 6, 3.8, 0.32, 'iris', wing=-1.6), *_cool_eye(39, 31, 5.2, 3.4, -0.32, 'iris'),
    Mouth(22, 40, 3, 'line')], s=1.1, cx=38, gy=40), s=0.95))
