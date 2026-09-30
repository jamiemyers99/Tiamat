"""The ancient Covenant stonework under Rootmere: the Old Door at the south end of the village (a mossy stone
portal that stands there the whole game), its carved slab (closed / gem-lit / open), the incubator in the Deep
Cradle and Abzurath's iron egg for the hatching scene.

The Old Door is drawn into the Rootmere map (like a building); the slab in its doorway is a dynamic object from the
'ui' atlas so it can open when the player sets the Crown Gem into it.
"""
import math
from spr import Spr
from pal import ramp, hx

STONE = ramp('#8c8a7a', 6, 0.12)        # weathered, faintly green-grey stone
DARK = ramp('#5e5c50', 5, 0.12)
MOSS = ramp('#5f8a3c', 5, 0.14)
BRONZE = ramp('#c08a3a', 5, 0.14)
TEAL_DIM, TEAL = '#4f8a80', '#6fe0c8'
AMBER_DIM, AMBER = '#9a6a2a', '#ffb040'
INK = '#1c1a28'


def _blocks(s, x0, y0, x1, y1, r, seed=0, h=8, w=16):
    """Fill a region that's already opaque with staggered stone blocks and mortar lines."""
    for y in range(y0, y1):
        row = (y - y0) // h
        for x in range(x0, x1):
            if not s.opaque(x, y):
                continue
            off = (w // 2) * (row % 2)
            if (y - y0) % h == h - 1 or (x + off + seed) % w == 0:
                s.px(x, y, r[1])
            elif (y - y0) % h == 0:
                s.px(x, y, r[3])
            elif ((x * 7 + y * 13 + seed) % 29) == 0:
                s.px(x, y, r[2] if (x + y) % 2 else r[4])


def _moss(s, pts, seed=0):
    for i, (x, y) in enumerate(pts):
        for k in range(5):
            dx = int(round(math.sin(i * 2.1 + k * 1.7 + seed) * 2.2))
            dy = k // 2
            if s.opaque(x + dx, y + dy):
                s.px(x + dx, y + dy, MOSS[2 if k % 2 else 3])


def gate_structure():
    """Rootmere's Old Door: a squat stepped portal of mossy blocks, 5×4 tiles. Door tile = (2, 3)."""
    W, oy = 80, 20
    s = Spr(W, oy + 64)
    bot = oy + 64
    # shadow
    for x in range(4, 76):
        for y in range(bot - 3, bot):
            s.px(x, y, (20, 18, 28), 70)
    # the mound
    s.poly([(2, bot - 1), (3, oy + 6), (9, oy - 4), (71, oy - 4), (77, oy + 6), (78, bot - 1)], STONE[2])
    s.poly([(16, oy - 3), (20, oy - 16), (60, oy - 16), (64, oy - 3)], STONE[3])
    _blocks(s, 0, oy - 16, W, bot, STONE, seed=3)
    # top ledges catch the light
    s.hline(20, 59, oy - 16, STONE[5]); s.hline(10, 69, oy - 4, STONE[4]); s.hline(9, 70, oy - 3, STONE[4])
    # standing pillars either side of the doorway, with carved rings
    for px0 in (8, 64):
        s.rect(px0, oy + 4, 8, bot - oy - 5, DARK[2])
        s.rect(px0, oy + 4, 2, bot - oy - 5, DARK[3]); s.rect(px0 + 6, oy + 4, 2, bot - oy - 5, DARK[1])
        for ry in (oy + 14, oy + 30, oy + 46):
            s.hline(px0, px0 + 7, ry, DARK[0]); s.hline(px0, px0 + 7, ry + 1, DARK[4])
            s.px(px0 + 3, ry + 5, TEAL_DIM); s.px(px0 + 4, ry + 6, TEAL_DIM)
        s.rect(px0 - 1, oy + 2, 10, 3, DARK[3])
    # lintel: one huge slab, carved with the two sea-dragons circling a star
    s.rect(6, oy + 2, 68, 12, DARK[2]); s.hline(6, 73, oy + 2, DARK[4]); s.hline(6, 73, oy + 13, DARK[0])
    for i in range(22):     # left dragon: a wave (Tiamat); right: an angular chain (the Deep King)
        x = 14 + i
        s.px(x, oy + 7 + int(round(math.sin(i * 0.6) * 2.5)), TEAL_DIM)
        x2 = 44 + i
        s.px(x2, oy + 7 + (2 if (i // 3) % 2 else -2) - (1 if i % 3 == 1 and (i // 3) % 2 else 0), AMBER_DIM)
    s.px(39, oy + 6, '#e8e4d0'); s.px(40, oy + 6, '#e8e4d0'); s.px(39, oy + 8, TEAL_DIM); s.px(40, oy + 8, AMBER_DIM)
    s.px(38, oy + 7, '#c8c4b0'); s.px(41, oy + 7, '#c8c4b0')
    # the dark doorway (the slab object sits on top of this)
    s.rect(16, oy + 16, 48, 48, '#14121c')
    # threshold step
    s.rect(12, bot - 4, 56, 4, STONE[3]); s.hline(12, 67, bot - 4, STONE[5]); s.hline(12, 67, bot - 1, STONE[1])
    # moss and hanging roots
    _moss(s, [(12, oy - 4), (22, oy - 16), (31, oy - 16), (52, oy - 16), (66, oy - 4), (4, oy + 10), (74, oy + 14),
              (26, oy - 4), (58, oy - 4), (3, oy + 40), (76, oy + 36), (45, oy - 16)], seed=1)
    for (vx, vy, n) in [(11, oy + 2, 11), (68, oy + 2, 8), (24, oy + 2, 4), (57, oy + 2, 6)]:
        for k in range(n):
            s.px(vx + (1 if k % 4 == 2 else 0), vy + k, MOSS[1 if k % 3 else 2])
    s.outline(None, darken=0.32)
    return dict(spr=s, ox=0, oy=oy, fw=5, fh=4, door=(2, 3), lights=[])


def _slab_base(runes, ring, gem):
    s = Spr(48, 48)
    st = ramp('#7e7c6e', 6, 0.1)
    s.rect(0, 0, 48, 48, st[2])
    for y in range(48):         # a little vertical grain
        for x in range(48):
            if (x * 5 + y * 3) % 23 == 0:
                s.px(x, y, st[3])
    s.rect(0, 0, 48, 2, st[4]); s.rect(0, 0, 2, 48, st[3]); s.rect(46, 0, 2, 48, st[1])
    s.vline(23, 2, 47, st[0]); s.vline(24, 2, 47, st[4])        # seam between the two halves
    for (x0, y0, x1, y1) in [(3, 3, 44, 3), (3, 44, 44, 44)]:
        s.hline(x0, x1, y0, st[1])
    s.vline(3, 3, 44, st[1]); s.vline(44, 3, 44, st[1])
    # rune columns down both sides
    for k, y in enumerate(range(8, 42, 5)):
        for xx in (7, 39):
            w = 2 + (k + xx) % 3
            s.hline(xx, xx + w - 1, y, runes)
            s.px(xx + (k % 2), y + 2, runes)
    # the great circle, split down the seam: a wave-dragon (left) and an iron-dragon (right) around the gem
    cx, cy, R = 23.5, 20.5, 11
    for a in range(0, 360, 4):
        x = cx + R * math.cos(math.radians(a)); y = cy + R * math.sin(math.radians(a))
        s.px(int(round(x)), int(round(y)), ring[0])
    for a in range(100, 260, 6):        # wave on the left
        rr = R - 3 + math.sin(math.radians(a * 3)) * 1.5
        s.px(int(round(cx + rr * math.cos(math.radians(a)))), int(round(cy + rr * math.sin(math.radians(a)))), ring[1])
    for a in list(range(-80, 80, 10)):  # zig-zag links on the right
        rr = R - 3 + (1.5 if (a // 10) % 2 else -1.5)
        s.px(int(round(cx + rr * math.cos(math.radians(a)))), int(round(cy + rr * math.sin(math.radians(a)))), ring[2])
    # gem socket
    s.poly([(24, 16), (28, 20.5), (24, 26), (20, 20.5)], INK)
    if gem:
        s.poly([(24, 16.5), (27.5, 20.5), (24, 25), (20.5, 20.5)], gem[0])
        s.poly([(24, 18), (26, 20.5), (24, 23), (22, 20.5)], gem[1])
        s.px(23, 18, '#ffffff')
    # carved step marks at the foot
    for x in range(8, 40, 6):
        s.hline(x, x + 2, 40, st[1])
    return s


def slab_frames():
    closed = _slab_base(ramp('#6a6a5e', 3, 0.1)[0], ('#5a5a50', TEAL_DIM, AMBER_DIM), None)
    lit = _slab_base(TEAL, ('#e8f8f0', TEAL, AMBER), ('#d09a3c', '#ffd070'))
    op = Spr(48, 48)
    op.rect(0, 0, 48, 48, '#0c0a12')
    # the halves slid into the walls: only their edges show
    st = ramp('#7e7c6e', 5, 0.1)
    op.rect(0, 0, 4, 48, st[2]); op.vline(3, 0, 47, st[0]); op.rect(44, 0, 4, 48, st[2]); op.vline(44, 0, 47, st[4])
    # stairs going down into the dark, lit faintly from below
    for i, y in enumerate(range(46, 8, -5)):
        k = max(0.0, 1 - i / 7)
        inset = 4 + i * 2
        c = tuple(int(v) for v in (18 + 60 * k, 16 + 54 * k, 22 + 48 * k))
        op.rect(inset, y - 2, 48 - 2 * inset, 3, c)
        op.hline(inset, 47 - inset, y - 2, tuple(min(255, v + 18) for v in c))
    for y in range(2, 14):       # a faint teal glow far down the stair
        for x in range(8, 40):
            d = math.hypot((x - 23.5) / 14, (y - 6) / 6)
            if d < 1 and (x * 3 + y * 5) % 4 < (3 if d < 0.5 else 1):
                op.px(x, y, (30 + int(30 * (1 - d)), 60 + int(60 * (1 - d)), 64 + int(50 * (1 - d))))
    return [('ancient_slab', closed), ('ancient_slab_lit', lit), ('ancient_open', op)]


def incubator():
    """The Deep Cradle's incubator: a round stone plinth with bronze claws holding an amber glass dome.
    3×2 footprint (the dome rises above)."""
    s = Spr(48, 68); oy = 36
    base = ramp('#6a6858', 6, 0.12)
    s.ellipse(24, oy + 26, 22, 6, (20, 18, 28), 80)
    # plinth
    s.ellipse(24, oy + 20, 21, 9, base[1])
    s.rect(3, oy + 8, 42, 12, base[2])
    s.ellipse(24, oy + 8, 21, 9, base[3])
    s.ellipse(24, oy + 8, 17, 6.5, base[4])
    for k, x in enumerate(range(6, 44, 5)):     # glowing runes around the plinth
        s.hline(x, x + 2, oy + 14 + (k % 2), TEAL)
    # bronze ring
    for a in range(0, 360, 3):
        x = 24 + 17 * math.cos(math.radians(a)); y = oy + 8 + 6.5 * math.sin(math.radians(a))
        s.px(int(round(x)), int(round(y)), BRONZE[3] if a > 180 else BRONZE[1])
    # the glass dome, warm amber glow inside
    for y in range(oy - 30, oy + 9):
        for x in range(8, 41):
            u = (x - 24) / 15.5; v = (y - (oy + 6)) / 34.0
            if u * u + v * v <= 1 and y <= oy + 8:
                g = 1 - math.sqrt(u * u + v * v)
                col = (int(150 + 100 * g), int(90 + 80 * g), int(40 + 40 * g))
                s.px(x, y, col, int(120 + 90 * g))
    s.vline(15, oy - 18, oy + 2, (255, 240, 200)); s.vline(16, oy - 22, oy - 12, (255, 240, 200))
    # four bronze claws gripping the dome
    for (x0, lean) in [(8, 1), (40, -1), (17, 1), (31, -1)]:
        pts = [(x0, oy + 10), (x0 + lean * 2, oy - 6), (x0 + lean * 5, oy - 20), (x0 + lean * 8, oy - 27)]
        if x0 in (17, 31):
            pts = [(x0, oy + 12), (x0 + lean, oy - 10), (x0 + lean * 3, oy - 27)]
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            s.line(ax, ay, bx, by, BRONZE[2]); s.line(ax + 1, ay, bx + 1, by, BRONZE[3])
        tx, ty = pts[-1]
        s.px(tx, ty - 1, BRONZE[4])
    # crown piece on top
    s.poly([(20, oy - 30), (24, oy - 36), (28, oy - 30)], BRONZE[3]); s.px(24, oy - 32, AMBER)
    # pipes into the floor
    s.rect(0, oy + 12, 3, 6, BRONZE[1]); s.rect(45, oy + 12, 3, 6, BRONZE[1])
    s.outline(None, darken=0.3)
    return s, 0, oy, 3, 2


def drake_egg(glow=False):
    """Abzurath's egg for the hatching scene: iron-grey with bronze plates and seams of amber light."""
    s = Spr(22, 28)
    body = ramp('#565e70', 6, 0.14)
    for y in range(1, 27):
        for x in range(1, 21):
            v = (y - 15.5) / 12.5
            u = (x - 10.5) / (9.5 * (1 - 0.18 * max(0, -v)))
            if u * u + v * v <= 1:
                light = -0.5 * u - 0.6 * v
                k = 1 if light < -0.35 else 2 if light < 0.1 else 3 if light < 0.45 else 4
                s.px(x, y, body[k])
    for (x0, y0, x1, y1) in [(4, 12, 10, 9), (10, 9, 17, 12), (3, 18, 11, 20), (11, 20, 18, 17)]:
        s.line(x0, y0, x1, y1, BRONZE[2])
    seam = '#ffe090' if glow else AMBER
    for (x0, y0, x1, y1) in [(8, 4, 10, 8), (10, 8, 8, 12), (13, 14, 15, 18), (15, 18, 13, 23), (6, 21, 8, 24)]:
        s.line(x0, y0, x1, y1, seam)
    s.px(7, 7, '#c8d0e0'); s.px(6, 8, '#c8d0e0')
    s.outline(INK)
    return s
