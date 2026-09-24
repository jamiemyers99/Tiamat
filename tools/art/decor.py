"""Overworld decoration sprites: trees, rocks, tall grass, fences, ledges,
bridges, signs, lamps and misc props. Each factory returns (Spr, ox, oy, fw, fh):
the sprite, the offset of the footprint's top-left inside the sprite, and the
footprint size in cells.
"""
import numpy as np
from functools import lru_cache
from spr import Spr, C
from pal import hx, ramp, shift, h2, BAYER4

LEAF = ramp('#3f9a45', 6, 0.15, hue=18)
LEAF_DARK = ramp('#2f7a4a', 6, 0.14, hue=18)
LEAF_AUTUMN = ramp('#c77a2e', 6, 0.14)
PINE = ramp('#2c6e4f', 6, 0.14, hue=16)
TRUNK = ramp('#7a5236', 5, 0.14)
ROCK = ramp('#8e8a86', 6, 0.14)
CAVE_ROCK = ramp('#6d5a4e', 6, 0.13)
SNOW = [hx('#a9bddc'), hx('#cfdcf0'), hx('#eef4fc'), hx('#ffffff')]
WOOD = ramp('#a4703f', 5, 0.14)
OUTLINE = hx('#1d2a26')
SHADOW = (18, 24, 32)


def _shadow(s, cx, cy, rx, ry, alpha=70):
    ys, xs = np.mgrid[0:s.h, 0:s.w]
    m = ((xs + 0.5 - cx) / rx) ** 2 + ((ys + 0.5 - cy) / ry) ** 2 <= 1
    m &= s.a[:, :, 3] == 0
    s.a[m] = (*SHADOW, alpha)


def _speckle(s, mask, ramp_, seed, density=0.12, light_bias=True):
    ys, xs = np.nonzero(mask)
    for y, x in zip(ys, xs):
        r = h2(int(x), int(y), seed)
        if r < density:
            # speckle toward lighter on upper-left, darker lower-right
            cur = tuple(s.a[y, x, :3])
            try:
                i = [tuple(C(c)[:3]) for c in ramp_].index(cur)
            except ValueError:
                continue
            j = min(len(ramp_) - 1, i + 1) if (r < density / 2) else max(0, i - 1)
            s.a[y, x, :3] = C(ramp_[j])[:3]


@lru_cache(None)
def tree(kind='oak', variant=0):
    """2×2-cell tree. Sprite 32×46, footprint origin at (0,14)."""
    s = Spr(32, 46)
    oy = 14
    if kind in ('oak', 'autumn', 'dark'):
        leaves = {'oak': LEAF, 'autumn': LEAF_AUTUMN, 'dark': LEAF_DARK}[kind]
        _shadow(s, 16, oy + 28, 13, 4)
        # trunk
        s.rect(13, oy + 17, 6, 12, TRUNK[2])
        s.rect(13, oy + 17, 2, 12, TRUNK[3])
        s.rect(17, oy + 17, 2, 12, TRUNK[1])
        s.px(12, oy + 28, TRUNK[1]); s.px(19, oy + 28, TRUNK[1])
        s.px(15, oy + 24, TRUNK[0]); s.px(16, oy + 25, TRUNK[0])
        # canopy clumps (drawn back to front)
        sh = [-2, 0, 1][variant % 3]
        clumps = [(16, oy + 2, 11, 9, 0.05), (8 + sh, oy + 9, 8, 7, -0.05), (24 - sh, oy + 9, 8, 7, -0.08),
                  (16, oy + 12, 11, 7, -0.12), (10, oy - 2, 7, 6, 0.12), (22, oy - 3, 7, 6, 0.1), (16, oy - 6, 7, 5, 0.18)]
        canopy = np.zeros((s.h, s.w), dtype=bool)
        for (cx, cy, rx, ry, b) in clumps:
            canopy |= s.shaded_ellipse(cx, cy, rx, ry, leaves, bias=b)
        _speckle(s, canopy, leaves, 7 + variant, 0.18)
        # little leaf notches along the bottom edge
        for x in range(4, 29, 3):
            y = oy + 18 + (x % 2)
            if s.opaque(x, y - 1) and not s.opaque(x, y):
                s.px(x, y, leaves[1])
        s.outline(None, darken=0.3)
    elif kind in ('pine', 'snowpine'):
        _shadow(s, 16, oy + 28, 11, 4)
        s.rect(14, oy + 20, 4, 9, TRUNK[1]); s.rect(14, oy + 20, 2, 9, TRUNK[2])
        tiers = [(16, oy - 12, 6, 9), (16, oy - 5, 10, 11), (16, oy + 3, 13, 13), (16, oy + 10, 15, 12)]
        body = np.zeros((s.h, s.w), dtype=bool)
        for i, (cx, top, half, hgt) in enumerate(tiers):
            pts = [(cx, top), (cx + half, top + hgt), (cx - half, top + hgt)]
            m = s.poly(pts, PINE[2])
            ys, xs = np.nonzero(m)
            for y, x in zip(ys, xs):
                t = (x - (cx - half)) / (2 * half + 1e-6)
                v = 1 - t + (y - top) / hgt * -0.25
                idx = int(np.clip(v * 4 + BAYER4[y % 4, x % 4] * 0.9, 0, 5))
                s.a[y, x] = C(PINE[min(5, idx)])
            # darker underside of tier
            for x in range(cx - half + 1, cx + half):
                s.px(x, top + hgt - 1, PINE[0])
            if kind == 'snowpine':
                for x in range(cx - half + 1, cx + half):
                    ytop = top + int(abs(x - cx) / half * hgt)
                    for dy in range(0, 2 + (1 if abs(x - cx) < half * 0.5 else 0)):
                        if s.opaque(x, ytop + dy):
                            s.px(x, ytop + dy, SNOW[3 if dy == 0 else 2])
            body |= m
        s.outline(None, darken=0.3)
    elif kind == 'palm':
        _shadow(s, 18, oy + 28, 10, 3)
        # curved trunk
        for i in range(20):
            y = oy + 28 - i
            x = 16 + int(3 * np.sin(i / 20 * 1.6))
            s.rect(x - 2, y, 4, 1, TRUNK[3] if i % 3 == 0 else TRUNK[2])
            s.px(x + 1, y, TRUNK[1])
        top = (19, oy + 7)
        fr = ramp('#4aa55a', 5, 0.14)
        for ang, ln in [(-2.8, 13), (-2.2, 12), (-1.4, 10), (-0.9, 12), (-0.3, 13), (0.3, 11), (2.9, 11)]:
            for t in range(ln):
                x = top[0] + np.cos(ang) * t
                y = top[1] + np.sin(ang) * t + (t * t) / 28
                s.rect(int(x), int(y), 2, 2, fr[2 + (1 if t < 4 else 0)])
                s.px(int(x), int(y) + 2, fr[1])
        s.shaded_ellipse(top[0], top[1] + 1, 3, 3, ramp('#8a5a2a', 4, 0.1))
        s.outline(None, darken=0.3)
    elif kind == 'dead':
        _shadow(s, 16, oy + 28, 10, 3)
        bark = ramp('#5e4a5a', 5, 0.12)
        s.rect(14, oy + 10, 5, 19, bark[2]); s.rect(14, oy + 10, 2, 19, bark[3])
        for (x0, y0, x1, y1) in [(16, oy + 12, 6, oy + 2), (16, oy + 10, 26, oy - 1), (15, oy + 6, 10, oy - 8),
                                 (17, oy + 5, 22, oy - 10), (8, oy + 4, 3, oy + 1), (24, oy + 2, 29, oy + 4)]:
            s.line(x0, y0, x1, y1, bark[2]); s.line(x0 + 1, y0, x1 + 1, y1, bark[1])
        s.outline(None, darken=0.3)
    return s, 0, oy, 2, 2


@lru_cache(None)
def bush(kind='green', variant=0):
    s = Spr(16, 20)
    oy = 4
    leaves = {'green': LEAF, 'dark': LEAF_DARK, 'snow': LEAF_DARK, 'berry': LEAF}[kind]
    _shadow(s, 8, oy + 14, 7, 2)
    m = s.shaded_ellipse(8, oy + 7, 7, 6.5, leaves, bias=0.05)
    m |= s.shaded_ellipse(5, oy + 4, 4, 3.5, leaves, bias=0.18)
    _speckle(s, m, leaves, 3 + variant, 0.2)
    if kind == 'berry':
        for (x, y) in [(5, oy + 6), (10, oy + 8), (8, oy + 4), (11, oy + 5)]:
            s.px(x, y, '#e24a5a'); s.px(x, y - 1, '#ff9aa2')
    if kind == 'snow':
        for x in range(2, 14):
            y = oy + 1 + abs(x - 7) // 3
            s.px(x, y, SNOW[3]); s.px(x, y + 1, SNOW[2])
    s.outline(None, darken=0.3)
    return s, 0, oy, 1, 1


@lru_cache(None)
def boulder(kind='rock', variant=0):
    s = Spr(16, 18)
    oy = 2
    rr = ROCK if kind == 'rock' else CAVE_ROCK
    _shadow(s, 8, oy + 14, 7, 2)
    m = s.shaded_ellipse(8, oy + 9, 7, 6, rr, bias=0.0)
    s.px(6, oy + 8, rr[1]); s.px(7, oy + 9, rr[1]); s.px(10, oy + 7, rr[1])
    s.outline(None, darken=0.3)
    return s, 0, oy, 1, 1


# Tall grass, Gen-4 style: two staggered rows of leafy fans (three curved, pointed blades each)
# over a deep base, lit from the upper left and outlined. `frame` 0-7 is the wind phase (tips lean
# with WAVE), `edge` leaves the gaps between the back row's tips open on the top row of a patch so
# the patch has a jagged outline, and `spread` pushes the blades apart (the rustle when stepped in).
TG_BACK = ['#123a20', '#1f5a2c', '#2d7a35', '#46953f', '#6fb456']   # outline, shade, body, light, tip
TG_FRONT = ['#163f22', '#2e7a35', '#44a044', '#6fc655', '#b6ee80']
TG_BASE = '#1b4c28'
WAVE = [0, 0, 0, 1, 1, 1, 0, 0]


def _blade(L, tx, ty, bx, by, pal, width, lean=0):
    n = max(1, by - ty)
    for y in range(ty, by + 1):
        t = (y - ty) / n
        k = 1 - (1 - t) ** 2                     # curves: leans most near the tip
        x = tx + (bx - tx) * k + lean * max(0.0, 1 - (y - ty) / 4)
        w = 1 if y - ty < 1 else (min(2, width) if y - ty < 3 else width)
        x0 = int(round(x - (w - 1) / 2))
        for i in range(w):
            if y == ty:
                c = pal[4]
            elif i == 0 and w > 1:
                c = pal[3]
            elif i == w - 1 and w > 2:
                c = pal[1]
            else:
                c = pal[2]
            L.px(x0 + i, y, c)


def _fan(L, cx, top, bottom, pal, lean, spread):
    # side blades first (behind), then the tall middle one
    _blade(L, cx - 3 - spread, top + 2 + spread, cx - 1, bottom, pal, 2, lean)
    _blade(L, cx + 3 + spread, top + 2 + spread, cx + 1, bottom, pal, 2, lean)
    _blade(L, cx + (lean if spread else 0), top + spread, cx, bottom, pal, 3, lean)


def _grass_row(xs, tops, bottom, pal, lean, spread):
    """Draw a row of fans three times side by side, outline it, keep the middle tile (seamless wrap)."""
    L = Spr(48, 16)
    for rep in range(3):
        for cx, top in zip(xs, tops):
            _fan(L, cx + rep * 16, top, bottom, pal, lean, spread)
    L.outline(pal[0])
    out = Spr(16, 16)
    out.a[:, :] = L.a[:, 16:32]
    return out


@lru_cache(None)
def tall_grass(variant=0, frame=0, edge=False, spread=0):
    """16x16 tall-grass tile."""
    lean = 0 if spread else WAVE[frame % 8]
    v = variant % 2
    s = Spr(16, 16)
    s.rect(0, 4 if edge else 0, 16, 16 - (4 if edge else 0), TG_BASE)
    back = _grass_row([4, 12], [0, 1] if v == 0 else [1, 0], 11, TG_BACK, lean, spread)
    front = _grass_row([0, 8], [6, 5] if v == 0 else [5, 6], 15, TG_FRONT, lean, spread)
    s.blit(back, 0, 0)
    s.blit(front, 0, 0)
    if not edge:
        return s
    # top row of a patch: nothing above the back row's blades
    return s


@lru_cache(None)
def tall_grass_front():
    """Bottom strip drawn over the player while standing in tall grass."""
    full = tall_grass(0, 0)
    s = Spr(16, 16)
    s.a[9:16] = full.a[9:16]
    return s


@lru_cache(None)
def grass_rustle(k=0, edge=False):
    """Frames shown on a grass tile as something walks into it: blades pushed apart, then settling."""
    return tall_grass(0, 0, edge, spread=[2, 1, 1][k] if k < 3 else 0)


@lru_cache(None)
def flowers(variant=0):
    s = Spr(16, 16)
    cols = [('#ff6b8a', '#ffd1dc'), ('#ffd54a', '#fff3b0'), ('#ffffff', '#fff7e0'), ('#8fb4ff', '#dce7ff'), ('#ff8a3d', '#ffd7b0')]
    spots = [(3, 4), (10, 3), (6, 10), (12, 11)] if variant % 2 == 0 else [(4, 3), (11, 6), (3, 11), (9, 12)]
    for i, (x, y) in enumerate(spots):
        c, hi = cols[(variant + i) % len(cols)]
        s.px(x, y + 2, '#2f7a3a'); s.px(x, y + 3, '#2f7a3a')
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            s.px(x + dx, y + dy, c)
        s.px(x, y, '#f6c23e' if c != '#ffd54a' else '#e0702a')
        s.px(x - 1, y - 1, hi)
    return s


def fence_tile(left, right, up, down, kind='wood'):
    s = Spr(16, 20)
    oy = 4
    w = WOOD if kind == 'wood' else ROCK
    if kind == 'wood':
        # post
        s.rect(6, oy - 2, 4, 14, w[2]); s.rect(6, oy - 2, 1, 14, w[3]); s.rect(9, oy - 2, 1, 14, w[1])
        s.rect(6, oy - 3, 4, 1, w[3])
        if left or right:
            x0 = 0 if left else 6
            x1 = 16 if right else 10
            for y in (oy + 1, oy + 6):
                s.rect(x0, y, x1 - x0, 2, w[2]); s.rect(x0, y, x1 - x0, 1, w[3])
        if up or down:
            s.rect(7, 0 if up else oy, 2, 16 + oy - (0 if up else oy), w[2])
        _shadow(s, 8, oy + 12, 5, 1.5, 60)
    else:
        s.rect(1, oy, 14, 12, w[2])
        for y in range(oy, oy + 12, 4):
            s.rect(1, y, 14, 1, w[1])
            off = 0 if (y // 4) % 2 else 4
            for x in range(1 + off, 15, 8):
                s.vline(x, y, y + 3, w[1])
        s.rect(1, oy, 14, 1, w[4])
        if left:
            s.rect(0, oy, 1, 12, w[2])
        if right:
            s.rect(15, oy, 1, 12, w[2])
    s.outline(None, darken=0.32)
    return s, 0, oy, 1, 1


def ledge_tile(kind, left, right, base='grass'):
    """One-way ledge. kind: 'down' | 'left' | 'right'. Drawn over ground."""
    s = Spr(16, 16)
    lips = {'grass': '#4c9a40', 'forest': '#3a7e3c', 'moor': '#7d8446', 'snow': '#dfe8f6', 'cave': '#8a7462',
            'ash': '#7e7280', 'sand': '#d9c28a', 'cobble': '#b0a898', 'path': '#c49a60'}
    faces = {'snow': '#8fa2c8', 'cave': '#5a4a40', 'ash': '#4e4654'}
    lip = ramp(lips.get(base, '#4c9a40'), 4, 0.1)
    earth = ramp(faces.get(base, '#8a6a4a'), 4, 0.12)
    shadow = (16, 20, 30, 70)
    if kind == 'down':
        for x in range(16):
            if (x < 1 and not left) or (x > 14 and not right):
                continue
            s.px(x, 6, lip[3]); s.px(x, 7, lip[2]); s.px(x, 8, lip[1])
            for y in range(9, 14):
                s.px(x, y, earth[3 if y == 9 else (2 if y < 12 else 1)])
            s.px(x, 13, earth[0])
            if (x * 7) % 5 == 1:
                s.px(x, 11, earth[1])
            s.px(x, 14, shadow); s.px(x, 15, (16, 20, 30, 35))
        if not left:
            s.vline(1, 7, 13, earth[0])
        if not right:
            s.vline(14, 7, 13, earth[0])
    else:
        right_k = kind == 'right'
        xs = list(range(8, 16)) if right_k else list(range(0, 8))[::-1]
        cols = [lip[3], lip[2], earth[3], earth[2], earth[2], earth[1], earth[0], shadow]
        for y in range(16):
            if (y < 1 and not left) or (y > 14 and not right):
                continue
            for i, x in enumerate(xs):
                s.px(x, y, cols[i])
    return s


def bridge_tile(horizontal=True, edge_a=False, edge_b=False):
    s = Spr(16, 16)
    w = WOOD
    if horizontal:
        for x in range(16):
            col = w[2] if x % 4 else w[1]
            s.vline(x, 2, 13, col)
            s.px(x, 3, w[3])
        s.rect(0, 0, 16, 2, w[1]); s.rect(0, 0, 16, 1, w[3])
        s.rect(0, 14, 16, 2, w[1]); s.rect(0, 15, 16, 1, w[0])
    else:
        for y in range(16):
            col = w[2] if y % 4 else w[1]
            s.hline(2, 13, y, col)
            s.px(3, y, w[3])
        s.rect(0, 0, 2, 16, w[1]); s.rect(0, 0, 1, 16, w[3])
        s.rect(14, 0, 2, 16, w[1]); s.rect(15, 0, 1, 16, w[0])
    return s


@lru_cache(None)
def rock_cell(up, down, left, right, cave=False, ul=True, ur=True, snow=False):
    """Cliff/rock mass cell. Neighbour flags = is the neighbour also rock."""
    s = Spr(16, 16)
    rr = CAVE_ROCK if cave else ROCK
    top = rr[2] if cave else rr[3]
    s.rect(0, 0, 16, 16, top)
    if snow:
        s.rect(0, 0, 16, 16, SNOW[2])
        for (x, y) in [(2, 3), (9, 5), (12, 2), (5, 10), (11, 11), (1, 13)]:
            s.px(x, y, SNOW[1]); s.px(x + 1, y, SNOW[3])
        if not down:
            for y in range(7, 16):
                for x in range(16):
                    s.px(x, y, rr[1] if (x + y // 3) % 5 else rr[0])
            s.hline(0, 15, 7, SNOW[2]); s.hline(0, 15, 8, SNOW[1])
            for x in range(0, 16, 3):
                s.px(x, 9, SNOW[2])
            s.hline(0, 15, 15, rr[0])
        if not up:
            s.hline(0, 15, 0, SNOW[3]); s.hline(0, 15, 1, SNOW[3])
        if not left:
            s.vline(0, 0, 15, rr[0])
        if not right:
            s.vline(15, 0, 15, rr[0])
        return s
    # top-surface texture: pebbles, cracks and tufts
    for (x, y, k) in [(2, 3, 0), (9, 5, 1), (12, 2, 0), (5, 10, 1), (11, 11, 0), (1, 13, 1), (7, 1, 0), (14, 8, 1)]:
        s.px(x, y, rr[1] if cave else rr[2]); s.px(x + 1, y, rr[4] if not cave else rr[3])
        if k:
            s.px(x, y + 1, rr[1] if cave else rr[2])
    s.line(3, 6, 6, 8, rr[1] if cave else rr[2]); s.line(10, 13, 13, 14, rr[1] if cave else rr[2])
    if not cave:
        for (x, y) in [(4, 4), (12, 9), (7, 13)]:
            s.px(x, y, '#6f9a4c'); s.px(x + 1, y - 1, '#86b45a')
    if not down:
        # front cliff face
        for y in range(7, 16):
            for x in range(16):
                shade = rr[1] if (x + y // 3) % 5 else rr[0]
                s.px(x, y, shade)
            s.px((y * 7) % 16, y, rr[2])
            s.px((y * 11 + 5) % 16, y, rr[0])
        s.hline(0, 15, 7, rr[4]); s.hline(0, 15, 8, rr[2])
        for x in range(0, 16, 5):
            s.vline(x, 9, 15, rr[0])
        s.hline(0, 15, 15, rr[0])
    if not up:
        s.hline(0, 15, 0, rr[5] if not cave else rr[4])
        s.hline(0, 15, 1, rr[4] if not cave else rr[3])
    if not left:
        s.vline(0, 0, 15, rr[0]); s.vline(1, 0, 15, rr[1] if down else rr[0])
    if not right:
        s.vline(15, 0, 15, rr[0]); s.vline(14, 0, 15, rr[1] if down else rr[0])
    return s


# ── props ────────────────────────────────────────────────────────────────────
@lru_cache(None)
def prop(name, variant=0):
    """Returns (Spr, ox, oy, fw, fh)."""
    if name == 'sign':
        s = Spr(16, 20); oy = 4
        _shadow(s, 8, oy + 14, 4, 1.5, 60)
        s.rect(7, oy + 6, 2, 9, WOOD[1])
        s.rect(1, oy + 0, 14, 8, WOOD[2]); s.rect(1, oy + 0, 14, 1, WOOD[4]); s.rect(1, oy + 7, 14, 1, WOOD[0])
        s.hline(3, 12, oy + 3, WOOD[1]); s.hline(3, 10, oy + 5, WOOD[1])
        s.outline(None, darken=0.32)
        return s, 0, oy, 1, 1
    if name == 'lamp':
        s = Spr(16, 34); oy = 18
        _shadow(s, 8, oy + 14, 4, 1.5, 60)
        iron = ramp('#3c4454', 4, 0.12)
        s.rect(7, oy - 8, 2, 22, iron[1]); s.px(7, oy - 8, iron[3])
        s.rect(5, oy + 12, 6, 2, iron[1])
        s.rect(4, oy - 14, 8, 7, iron[0])
        s.rect(5, oy - 13, 6, 5, '#ffe9a0'); s.rect(6, oy - 12, 2, 2, '#fffbe0')
        s.rect(3, oy - 15, 10, 2, iron[2]); s.px(7, oy - 17, iron[2]); s.px(8, oy - 16, iron[2])
        s.outline(None, darken=0.3)
        return s, 0, oy, 1, 1
    if name == 'mailbox':
        s = Spr(16, 20); oy = 4
        _shadow(s, 8, oy + 14, 4, 1.5, 60)
        s.rect(7, oy + 6, 2, 9, WOOD[1])
        s.rect(3, oy, 10, 7, '#c8453d'); s.rect(3, oy, 10, 2, '#e8655a'); s.rect(12, oy + 1, 2, 3, '#f0d24a')
        s.outline(None, darken=0.32)
        return s, 0, oy, 1, 1
    if name == 'barrel':
        s = Spr(16, 20); oy = 4
        _shadow(s, 8, oy + 14, 6, 2, 60)
        s.rect(3, oy, 10, 14, WOOD[2]); s.rect(3, oy, 3, 14, WOOD[3]); s.rect(10, oy, 3, 14, WOOD[1])
        for y in (oy + 3, oy + 10):
            s.rect(3, y, 10, 1, '#5a5f6e')
        s.rect(4, oy, 8, 2, WOOD[4])
        s.outline(None, darken=0.32)
        return s, 0, oy, 1, 1
    if name == 'crate':
        s = Spr(16, 20); oy = 4
        _shadow(s, 8, oy + 14, 7, 2, 60)
        s.rect(1, oy - 2, 14, 16, WOOD[2])
        s.rect(1, oy - 2, 14, 2, WOOD[4]); s.rect(1, oy + 12, 14, 2, WOOD[0])
        s.line(2, oy, 13, oy + 11, WOOD[1]); s.line(13, oy, 2, oy + 11, WOOD[1])
        s.outline(None, darken=0.32)
        return s, 0, oy, 1, 1
    if name == 'hay':
        s = Spr(16, 20); oy = 4
        _shadow(s, 8, oy + 13, 7, 2, 60)
        m = s.shaded_ellipse(8, oy + 7, 7, 7, ramp('#e3bd52', 5, 0.14))
        for y in range(oy + 2, oy + 13, 3):
            s.hline(3, 12, y, '#b38a2e')
        s.outline(None, darken=0.3)
        return s, 0, oy, 1, 1
    if name == 'stone':   # standing stone (menhir), 1×1 footprint, tall
        s = Spr(16, 32); oy = 16
        _shadow(s, 8, oy + 14, 6, 2, 70)
        st = ramp('#8b8a96', 5, 0.14)
        s.poly([(4, oy + 15), (3, oy - 6), (7, oy - 13), (11, oy - 11), (13, oy + 15)], st[2])
        for y in range(oy - 12, oy + 15):
            s.px(5, y, st[3]); s.px(11, y, st[1])
        s.px(7, oy - 2, '#6fe0c8'); s.px(8, oy - 1, '#6fe0c8'); s.px(7, oy + 2, '#6fe0c8')
        s.px(6, oy + 6, st[1]); s.px(9, oy + 9, st[1])
        s.outline(None, darken=0.32)
        return s, 0, oy, 1, 1
    if name == 'crystal':
        s = Spr(16, 30); oy = 14
        _shadow(s, 8, oy + 14, 6, 2, 70)
        cr = ramp('#7a5ce0', 5, 0.16)
        s.poly([(4, oy + 14), (3, oy - 2), (6, oy - 10), (9, oy - 2), (8, oy + 14)], cr[2])
        s.poly([(8, oy + 14), (9, oy - 6), (12, oy - 12), (14, oy - 4), (13, oy + 14)], cr[3])
        s.vline(5, oy - 6, oy + 12, cr[4]); s.vline(11, oy - 8, oy + 12, cr[4])
        s.outline(None, darken=0.3)
        return s, 0, oy, 1, 1
    if name == 'snowman':
        s = Spr(16, 26); oy = 10
        _shadow(s, 8, oy + 14, 6, 2, 60)
        s.shaded_ellipse(8, oy + 9, 6, 5.5, SNOW)
        s.shaded_ellipse(8, oy + 1, 4.5, 4.5, SNOW)
        s.px(6, oy, '#222'); s.px(9, oy, '#222'); s.px(7, oy + 2, '#f08a2a'); s.px(8, oy + 2, '#f08a2a')
        s.rect(5, oy - 5, 6, 2, '#2f3a58'); s.rect(6, oy - 8, 4, 3, '#2f3a58')
        s.outline(None, darken=0.3)
        return s, 0, oy, 1, 1
    if name == 'well':
        s = Spr(32, 40); oy = 8
        _shadow(s, 16, oy + 30, 13, 3, 60)
        st = ramp('#9a948a', 5, 0.13)
        s.rect(4, oy + 14, 24, 14, st[2]); s.rect(4, oy + 14, 24, 2, st[4])
        for y in range(oy + 17, oy + 28, 4):
            s.hline(4, 27, y, st[1])
        s.rect(7, oy + 12, 18, 4, '#1c3050'); s.rect(8, oy + 13, 16, 2, '#2c5a9a')
        s.rect(5, oy - 2, 2, 16, WOOD[1]); s.rect(25, oy - 2, 2, 16, WOOD[1])
        s.poly([(2, oy - 1), (16, oy - 8), (30, oy - 1), (30, oy + 2), (2, oy + 2)], '#b8453d')
        s.hline(2, 29, oy + 2, '#7a2a2a')
        s.outline(None, darken=0.32)
        return s, 0, oy, 2, 2
    if name == 'fountain':
        s = Spr(48, 52); oy = 4
        _shadow(s, 24, oy + 44, 22, 4, 60)
        st = ramp('#b0aaa0', 5, 0.12)
        s.ellipse(24, oy + 30, 22, 13, st[1]); s.ellipse(24, oy + 29, 22, 13, st[3])
        s.ellipse(24, oy + 29, 18, 10, '#2c5a9a'); s.ellipse(24, oy + 28, 17, 9, '#4a8ad8')
        for (x, y) in [(15, oy + 26), (30, oy + 31), (22, oy + 34), (34, oy + 25)]:
            s.hline(x, x + 3, y, '#9fd0f5')
        s.rect(21, oy + 6, 6, 20, st[2]); s.rect(21, oy + 6, 2, 20, st[4])
        s.ellipse(24, oy + 8, 8, 3, st[3]); s.ellipse(24, oy + 7, 6, 2, '#4a8ad8')
        for i in range(6):
            s.px(24 - 5 + i * 2, oy + 2 + (i % 2), '#cfeaff')
        s.px(24, oy - 1, '#ffffff'); s.px(24, oy, '#cfeaff')
        s.outline(None, darken=0.3)
        return s, 0, oy + 4, 3, 3
    if name == 'statue':
        s = Spr(16, 36); oy = 20
        _shadow(s, 8, oy + 14, 7, 2, 60)
        st = ramp('#a8a39c', 5, 0.13)
        s.rect(2, oy + 4, 12, 11, st[2]); s.rect(2, oy + 4, 12, 2, st[4])
        s.shaded_ellipse(8, oy - 6, 5, 9, st)
        s.shaded_ellipse(8, oy - 15, 3.5, 3.5, st)
        s.px(5, oy - 18, st[1]); s.px(11, oy - 18, st[1])
        s.outline(None, darken=0.3)
        return s, 0, oy, 1, 1
    if name == 'bench':
        s = Spr(32, 20); oy = 4
        _shadow(s, 16, oy + 13, 14, 2, 60)
        s.rect(2, oy + 1, 28, 3, WOOD[3]); s.rect(2, oy + 5, 28, 3, WOOD[2]); s.rect(2, oy + 8, 28, 1, WOOD[0])
        s.rect(4, oy + 9, 2, 4, '#3c4454'); s.rect(26, oy + 9, 2, 4, '#3c4454')
        s.outline(None, darken=0.3)
        return s, 0, oy, 2, 1
    if name == 'boat':
        s = Spr(48, 28); oy = 4
        hull = ramp('#b4643c', 5, 0.14)
        s.poly([(1, oy + 4), (47, oy + 4), (42, oy + 20), (6, oy + 20)], hull[2])
        s.hline(1, 46, oy + 4, hull[4]); s.hline(2, 45, oy + 5, hull[3])
        s.hline(6, 42, oy + 19, hull[0])
        s.rect(6, oy + 7, 36, 7, '#6b4a30'); s.hline(6, 41, oy + 7, '#4a3020')
        for x in (14, 24, 34):
            s.rect(x, oy + 7, 2, 7, hull[3])
        s.outline(None, darken=0.3)
        return s, 0, oy, 3, 1
    if name == 'stall':
        s = Spr(32, 36); oy = 14
        _shadow(s, 16, oy + 30, 15, 2, 60)
        s.rect(2, oy + 10, 28, 12, WOOD[2]); s.rect(2, oy + 10, 28, 2, WOOD[4])
        for (x, c) in [(5, '#e24a4a'), (10, '#f0c43a'), (15, '#7ac44a'), (20, '#e8823a'), (25, '#b85ad8')]:
            s.rect(x, oy + 7, 4, 3, c); s.px(x + 1, oy + 7, '#ffffff')
        s.rect(3, oy - 8, 2, 30, WOOD[1]); s.rect(27, oy - 8, 2, 30, WOOD[1])
        for i in range(8):
            c = '#e8e0d0' if i % 2 else '#d8503a'
            s.poly([(i * 4, oy - 12), (i * 4 + 4, oy - 12), (i * 4 + 4, oy - 3), (i * 4, oy - 3)], c)
        s.outline(None, darken=0.3)
        return s, 0, oy, 2, 2
    if name == 'cart':
        s = Spr(32, 28); oy = 8
        _shadow(s, 16, oy + 18, 14, 2, 60)
        s.rect(2, oy + 2, 28, 10, WOOD[2]); s.rect(2, oy + 2, 28, 2, WOOD[4])
        for y in range(oy + 5, oy + 12, 3):
            s.hline(2, 29, y, WOOD[1])
        s.shaded_ellipse(8, oy + 14, 4, 4, ramp('#5a4a3a', 4, 0.1)); s.shaded_ellipse(24, oy + 14, 4, 4, ramp('#5a4a3a', 4, 0.1))
        s.outline(None, darken=0.3)
        return s, 0, oy, 2, 1
    if name == 'rift_rock':
        s = Spr(16, 20); oy = 4
        _shadow(s, 8, oy + 14, 7, 2)
        rr = ramp('#4a3c6a', 6, 0.14)
        s.shaded_ellipse(8, oy + 8, 7, 6.5, rr)
        s.px(6, oy + 6, '#b89aff'); s.px(9, oy + 9, '#b89aff'); s.px(7, oy + 10, '#8a6ae0')
        s.outline(None, darken=0.3)
        return s, 0, oy, 1, 1
    if name == 'pot':
        s = Spr(16, 22); oy = 6
        _shadow(s, 8, oy + 14, 6, 2, 60)
        s.rect(4, oy + 6, 8, 8, '#b8603a'); s.rect(3, oy + 5, 10, 2, '#d8805a')
        m = s.shaded_ellipse(8, oy + 1, 6, 5, LEAF)
        s.outline(None, darken=0.3)
        return s, 0, oy, 1, 1
    if name == 'lantern_post':
        return prop('lamp')
    raise KeyError(name)
