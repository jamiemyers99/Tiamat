"""Tiamat's taming capsules: round balls, but nothing like the classic red-and-white one. There's no band and no
button in the middle; each one is a single textured colour or a riot of colours that suits its name.

  capsule           coral red, freckled like a hammered sweet
  prime_capsule     deep blue marble with pale swirling veins
  apex_capsule      gold glitter, with facets catching the light
  dusk_capsule      a little galaxy: violet and indigo nebula with stars
  swift_capsule     mad retro zig-zag stripes: teal, lime and yellow
  covenant_capsule  a rainbow spiral of the six Sigil colours

Every design is drawn at 14×14 (throw sprites and bag icons). `ball_spr()` also draws the overworld item, the
Team menu icon, the foe's party pips and the starters' capsules on the lab table.
"""
import math
from spr import Spr
from pal import hx, BAYER4

INK = '#1c1a28'


def _rgb(c):
    return hx(c) if isinstance(c, str) else c


def _mix(a, b, t):
    a, b = _rgb(a), _rgb(b)
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def _hash(x, y, seed):
    n = (x * 374761393 + y * 668265263 + seed * 2147483647) & 0xFFFFFFFF
    n = (n ^ (n >> 13)) * 1274126177 & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFF) / 65535.0


def ball_spr(size, pattern, outline=INK, shine=True):
    """A shaded sphere filling a size×size canvas. pattern(x, y, u, v) -> colour, where (u, v) run -1..1 across
    the ball's face; lighting (from the top-left) is applied on top in a few dithered steps, pixel-art style."""
    s = Spr(size, size)
    c = size / 2
    r = size / 2 - 1
    for y in range(size):
        for x in range(size):
            u, v = (x + 0.5 - c) / r, (y + 0.5 - c) / r
            d2 = u * u + v * v
            if d2 > 1:
                continue
            w = math.sqrt(1 - d2)
            light = (-0.5 * u - 0.62 * v + 0.6 * w) / 0.94          # lambert, light from the top-left
            level = light * 0.5 + 0.5 + (BAYER4[y % 4, x % 4] - 0.5) * 0.18
            k = 0.62 if level < 0.35 else 0.8 if level < 0.58 else 1.0 if level < 0.82 else 1.14
            base = _rgb(pattern(x, y, u, v))
            col = tuple(max(0, min(255, int(ch * k + (18 if k > 1 else 0)))) for ch in base)
            s.px(x, y, col)
    if shine:
        hx0, hy0 = int(c - r * 0.45), int(c - r * 0.5)
        s.px(hx0, hy0, '#ffffff'); s.px(hx0 + 1, hy0, '#ffffff'); s.px(hx0, hy0 + 1, '#ffffff')
    if outline:
        s.outline(outline)
    return s


# ── the six patterns ─────────────────────────────────────────────────────────
def freckled(base='#e8505e', dark='#8e1a34', light='#ffb0a0', seed=1):
    def f(x, y, u, v):
        h = _hash(x, y, seed)
        return dark if h < 0.2 else light if h > 0.9 else base
    return f


def marble(x, y, u, v):
    t = math.sin(u * 5.2 + 2.6 * math.sin(v * 4.1 + u * 1.3))
    if t > 0.78:
        return '#b8d4ff'
    if t > 0.45:
        return '#5a90f0'
    if t < -0.8:
        return '#16307a'
    return '#2c5ed8'


def glitter(x, y, u, v):
    h = _hash(x, y, 7)
    facet = ((x // 2) + (y // 2)) % 2
    if h > 0.86:
        return '#fff4b8'
    return '#f2bc34' if facet else '#d99a1c'


def galaxy(x, y, u, v):
    a = math.atan2(v, u)
    rr = math.hypot(u, v)
    t = math.sin(a * 2 + rr * 6)
    if _hash(x, y, 3) > 0.93:
        return '#ffffff'
    if t > 0.55:
        return '#c44aa8'
    if t > 0.0:
        return '#6a34b8'
    if t > -0.6:
        return '#2e2a88'
    return '#171448'


def zigzag(x, y, u, v):
    band = int(math.floor((y + abs((x % 6) - 3)) / 2)) % 4        # zig-zag stripes, like a retro sneaker
    return ['#2fc0ae', '#a8e04a', '#ffe24a', '#1a8a9a'][band]


def rainbow(x, y, u, v):
    a = math.atan2(v, u)
    rr = math.hypot(u, v)
    k = int(math.floor(((a / (2 * math.pi)) * 6 + rr * 3.2) % 6))
    return ['#6ad05a', '#4a9aff', '#ffd23a', '#c8d0e0', '#9ae8ff', '#ff5a8a'][k]


def capsule():
    return ball_spr(14, freckled())


def prime_capsule():
    return ball_spr(14, marble)


def apex_capsule():
    return ball_spr(14, glitter)


def dusk_capsule():
    return ball_spr(14, galaxy)


def swift_capsule():
    return ball_spr(14, zigzag)


def covenant_capsule():
    return ball_spr(14, rainbow)


DESIGNS = {
    'capsule': capsule, 'prime_capsule': prime_capsule, 'apex_capsule': apex_capsule,
    'dusk_capsule': dusk_capsule, 'swift_capsule': swift_capsule, 'covenant_capsule': covenant_capsule,
}


def icon16(name):
    s = Spr(16, 16)
    s.blit(DESIGNS[name](), 1, 1)
    return s


def item_ground():
    """A capsule lying on the ground where there's an item to pick up (16×16, bottom-aligned)."""
    s = Spr(16, 16)
    s.blit(ball_spr(12, freckled()), 2, 4)
    return s


def team_icon():
    """Pause-menu Team icon: three capsules huddled together."""
    s = Spr(16, 16)
    s.blit(ball_spr(8, freckled(seed=4), shine=False), 0, 7)
    s.blit(ball_spr(8, marble, shine=False), 8, 7)
    s.blit(ball_spr(9, glitter, shine=False), 3, 0)
    return s


def party_pip():
    """Tiny capsule for the foe's team count in battle (8×8)."""
    return ball_spr(8, freckled(seed=9), shine=False)


def starter_ball(col):
    """The starters' capsules on the lab table: a freckled ball in the starter's colour (11×11)."""
    return ball_spr(11, freckled(col, _mix(col, '#1c1a28', 0.35), _mix(col, '#ffffff', 0.45), seed=5), outline='#3a3848')
