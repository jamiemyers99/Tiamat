"""Overworld character sprites — 32×32 frames, Gen 4/5 (HeartGold / Black-White) chibi style.

Every frame is composed as a *letter map* (material + tone hint per pixel) from
  • the shared base FACE for the view plus a hair-style overlay and extra volumes (HAIR:
    short, long, cap, ponytail, bun, spiky, hood, hat, bald — hand-authored pixel art), and
  • a body for the pose (procedural for down/up, templates for the side view; casual or robe),
then lit as rounded volumes (heads as domes, body parts as vertical cylinders, light from the
top-left), recoloured through hue-shifted 5-tone ramps from `make_palette`, and finished with
sel-out outlines, contact shadows (fringe → face, head → shoulders) and a soft ground shadow.

Frame contract (what the game relies on):
  • 32×32 px, character row = 12 frames: down×3, left×3, right×3, up×3 — each stand, stepA, stepB.
    stepA = left foot forward, stepB = right foot forward; the upper body bobs up 1 px on steps.
  • Feet stand on the bottom: shoes on rows 29–30, their outline on row 31 (= FEET_Y), a
    semi-transparent ground-shadow ellipse on rows 29–31 behind them.
  • Horizontally centred on x = 16 (the seam between px 15 and 16) and always within x 5..27;
    nothing above row 1 in any frame.  Anchor the sprite with origin (0.5, 1) at the bottom-centre
    of the tile the character stands on (same convention as the old 16×24 frames).
  • 'right' is the mirrored 'left' geometry, re-lit so light still comes from the top-left.
"""
import colorsys
import numpy as np
from spr import Spr
from pal import hx

W, H = 32, 32
FEET_Y = 31            # last opaque row (shoe outline) — the character's ground line
INK = (34, 26, 44)     # base outline ink (tinted per material)
SELOUT_LIT = 0.22      # extra material tint on outline pixels that face the light (top / left edges)

# ── Palettes ────────────────────────────────────────────────────────────────
SKIN = {'light': '#f3cfae', 'tan': '#d9a577', 'brown': '#a8704a', 'deep': '#6e4632', 'pale': '#f6ddc8'}


def _hls(c):
    return colorsys.rgb_to_hls(*[v / 255 for v in c[:3]])


def _rgb(h, l, s):
    r, g, b = colorsys.hls_to_rgb(h % 1.0, min(1, max(0, l)), min(1, max(0, s)))
    return (round(r * 255), round(g * 255), round(b * 255))


def _mix(a, b, t):
    return tuple(round(a[i] * (1 - t) + b[i] * t) for i in range(3))


def tone_ramp(base, dl=(-0.25, -0.12, 0.0, 0.10, 0.21), shadow_hue=240, light_hue=52,
              hue_amt=(16, 8, 0, 5, 10), dsat=(0.10, 0.05, 0.0, -0.02, -0.06), gaps=(0.06, 0.06, 0.08, 0.08)):
    """5-tone ramp [deep, shadow, base, light, highlight] with hue shifting.

    Extreme bases (near white / near black) are spread so every tone stays distinct."""
    h, l, s = _hls(base)
    L = [l + d for d in dl]
    L[0] = max(L[0], 0.05)
    for i in (1, 2, 3, 4):                      # push up from the dark end
        L[i] = max(L[i], L[i - 1] + gaps[i - 1])
    L[4] = min(L[4], 0.985)
    for i in (3, 2, 1, 0):                      # push down from the light end
        L[i] = min(L[i], L[i + 1] - gaps[i])
    out = []
    hdeg = h * 360
    for i in range(5):
        k = i - 2
        target = light_hue if k > 0 else shadow_hue
        diff = ((target - hdeg + 540) % 360) - 180
        amt = hue_amt[i]
        hh = hdeg + max(-amt, min(amt, diff))
        # grey materials get a touch of tint in the shadows / lights so they are not dead
        ss = s + dsat[i] + (0.06 if s < 0.08 and k != 0 else 0)
        out.append(_rgb(hh / 360, L[i], ss))
    return out


def make_palette(skin='light', hair='#6b4a2e', top='#3f6fc8', legs='#3a3f58', shoes='#2a2230', accent='#c8473f', belt=None):
    sk = hx(SKIN.get(skin, skin))
    sk_l = _hls(sk)[1]
    hr, tp, lg, sh, ac = hx(hair), hx(top), hx(legs), hx(shoes), hx(accent)
    bl = hx(belt) if belt else _rgb(*_adj(tp, -0.2))
    ramps = {
        'skin': tone_ramp(sk, dl=(-0.34, -0.11, 0.0, 0.05, 0.10), shadow_hue=350, light_hue=45,
                          hue_amt=(18, 8, 0, 3, 5), dsat=(-0.30, -0.12, 0, 0.0, -0.02),
                          gaps=(0.08, 0.07, 0.045 if sk_l > 0.6 else 0.07, 0.04 if sk_l > 0.6 else 0.07)),
        'hair': tone_ramp(hr, dl=(-0.24, -0.12, 0.0, 0.12, 0.26),
                          **({'light_hue': 225, 'hue_amt': (16, 8, 0, 18, 30)} if _hls(hr)[1] < 0.22 else {})),
        'acc': tone_ramp(ac, dl=(-0.24, -0.12, 0.0, 0.11, 0.24)),
        'top': tone_ramp(tp),
        'legs': tone_ramp(lg, dl=(-0.22, -0.11, 0.0, 0.09, 0.18)),
        'shoes': tone_ramp(sh, dl=(-0.2, -0.1, 0.0, 0.12, 0.28)),
        'belt': tone_ramp(bl, dl=(-0.22, -0.11, 0.0, 0.12, 0.26)),
    }
    hl = _hls(hr)
    return {
        'ramps': ramps,
        'eye': (32, 24, 44),
        'iris': _rgb(hl[0] if hl[2] > 0.15 else 0.7, 0.30, 0.35),
        'white': (255, 255, 255),
        'mouth': _mix(ramps['skin'][0], ramps['skin'][1], 0.35),
        # rosy cheeks on light skin; on darker skin blush reads as a smudge, so cheeks stay plain
        'blush': _mix(ramps['skin'][2], (240, 120, 130), 0.28) if sk_l > 0.6 else None,
        'metal': (238, 214, 120),
    }


def _adj(c, dl):
    h, l, s = _hls(c)
    return (h, max(0, min(1, l + dl)), s)


# ── Letters ─────────────────────────────────────────────────────────────────
# letter → (material, mode, value, family)
#   mode 'a': auto-lit (volume shading) + value offset; mode 'f': fixed tone `value`
#   family groups letters into volumes inside a split (body) layer.
LET = {}


def _reg(chars, mat, mode, vals, fam):
    for ch, v in zip(chars, vals):
        LET[ch] = (mat, mode, v, fam)


_reg('st', 'skin', 'a', (0, 1), 'skin');   _reg('S', 'skin', 'a', (-1,), 'skin')
_reg('TqQ', 'skin', 'f', (1, 0, 4), 'skin')
_reg('hi', 'hair', 'a', (0, 1), 'hair');   _reg('H', 'hair', 'a', (-1,), 'hair')
_reg('IGg', 'hair', 'f', (4, 0, 1), 'hair')
_reg('aj', 'acc', 'a', (0, 1), 'acc');     _reg('A', 'acc', 'a', (-1,), 'acc')
_reg('JZz', 'acc', 'f', (4, 0, 1), 'acc')
_reg('cx', 'top', 'a', (0, 1), 'top');     _reg('C', 'top', 'a', (-1,), 'top')
_reg('XY', 'top', 'f', (4, 0), 'top');     _reg('y', 'top', 'f', (1,), 'top')
_reg('f', 'top', 'a', (0,), 'arm');        _reg('F', 'top', 'a', (-1,), 'arm')
_reg('pu', 'legs', 'a', (0, 1), 'legs');   _reg('P', 'legs', 'a', (-1,), 'legs')
_reg('U', 'legs', 'f', (0,), 'legs')
_reg('d', 'legs', 'a', (0,), 'leg2');      _reg('D', 'legs', 'a', (-1,), 'leg2')
_reg('b', 'shoes', 'a', (0,), 'shoes');    _reg('B', 'shoes', 'a', (-1,), 'shoes')
_reg('nN', 'shoes', 'f', (4, 0), 'shoes')
_reg('k', 'belt', 'a', (0,), 'top');       _reg('K', 'belt', 'f', (0,), 'top')
_reg('l', 'belt', 'a', (1,), 'top')
# flat specials
for ch, m in (('e', 'eye'), ('E', 'iris'), ('w', 'white'), ('m', 'mouth'), ('r', 'blush'), ('v', 'metal')):
    LET[ch] = (m, 'x', 0, 'skin')
# hand letters in body layers are their own family
HAND = {'s', 'S', 't', 'T', 'q'}

LIGHT = np.array([-0.62, -0.78, 0.9])
LIGHT = LIGHT / np.linalg.norm(LIGHT)


# ── Frame canvas ────────────────────────────────────────────────────────────
class Canvas:
    """Letter map + per-pixel layer id. Layers are painted back to front."""

    def __init__(self):
        self.ch = np.full((H, W), '.', dtype='<U1')
        self.layer = np.full((H, W), -1, dtype=int)
        self.kinds = []          # per layer: 'dome' | 'flat' | 'split'
        self.head_dy = 0         # vertical offset of the head templates in this frame

    def new_layer(self, kind):
        self.kinds.append(kind)
        return len(self.kinds) - 1

    def paint(self, rows, kind='dome', dx=0, dy=0):
        lid = self.new_layer(kind)
        for y, row in enumerate(rows):
            for x, c in enumerate(row):
                if c == '.' or c == ' ':
                    continue
                xx, yy = x + dx, y + dy
                if 0 <= xx < W and 0 <= yy < H:
                    self.ch[yy, xx] = c
                    self.layer[yy, xx] = lid
        return lid


def _components(mask):
    """4-connected components of a boolean mask → list of masks."""
    seen = np.zeros_like(mask)
    comps = []
    ys, xs = np.nonzero(mask)
    for y0, x0 in zip(ys, xs):
        if seen[y0, x0]:
            continue
        comp = np.zeros_like(mask)
        stack = [(y0, x0)]
        seen[y0, x0] = True
        while stack:
            y, x = stack.pop()
            comp[y, x] = True
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                yy, xx = y + dy, x + dx
                if 0 <= yy < H and 0 <= xx < W and mask[yy, xx] and not seen[yy, xx]:
                    seen[yy, xx] = True
                    stack.append((yy, xx))
        comps.append(comp)
    return comps


def _dome_light(mask, squash=1.0):
    """Surface normals of a rounded volume whose silhouette is `mask` (Euclidean distance dome),
    plus each pixel's distance from the rim."""
    iy, ix = np.nonzero(mask)
    oy, ox = np.nonzero(~mask)
    # add a ring outside the canvas so edge pixels count as edges
    ring = [(-1, x) for x in range(-1, W + 1)] + [(H, x) for x in range(-1, W + 1)] + \
           [(y, -1) for y in range(H)] + [(y, W) for y in range(H)]
    oy = np.concatenate([oy, [r[0] for r in ring]])
    ox = np.concatenate([ox, [r[1] for r in ring]])
    d2 = (iy[:, None] - oy[None, :]) ** 2 + ((ix[:, None] - ox[None, :]) * squash) ** 2
    d = np.sqrt(d2.min(axis=1)) - 0.5
    R = max(1.5, d.max())
    hmap = np.zeros((H + 2, W + 2))
    t = np.clip(d / R, 0, 1)
    hmap[iy + 1, ix + 1] = R * np.sqrt(1 - (1 - t) ** 2)
    gx = (hmap[iy + 1, ix + 2] - hmap[iy + 1, ix]) / 2
    gy = (hmap[iy + 2, ix + 1] - hmap[iy, ix + 1]) / 2
    n = np.stack([-gx, -gy, np.ones_like(gx) * 1.0], axis=1)
    n /= np.linalg.norm(n, axis=1, keepdims=True)
    out = np.full((H, W, 3), np.nan)
    out[iy, ix] = n
    dist = np.zeros((H, W))
    dist[iy, ix] = d + 0.5
    return out, dist


def _cyl_light(mask):
    """Surface normals for body parts: every horizontal run is the cross-section of a vertical cylinder.
    The top row of a part catches a little extra light and the bottom row turns away."""
    iy, ix = np.nonzero(mask)
    out = np.full((H, W, 3), np.nan)
    y0, y1 = iy.min(), iy.max()
    for y in range(y0, y1 + 1):
        xs = sorted(ix[iy == y])
        runs, start = [], None
        for i, x in enumerate(xs):
            if start is None:
                start = x
            if i == len(xs) - 1 or xs[i + 1] != x + 1:
                runs.append((start, x))
                start = None
        ny = -0.35 if (y == y0 and y1 - y0 >= 2) else (0.45 if (y == y1 and y1 - y0 >= 2) else 0.0)
        for a, b in runs:
            c = (a + b + 1) / 2
            half = max(1.0, (b - a + 1) / 2)
            for x in range(a, b + 1):
                nx = (x + 0.5 - c) / half * 0.92
                nz = np.sqrt(max(0.04, 1 - nx * nx - ny * ny))
                n = np.array([nx, ny, nz])
                out[y, x] = n / np.linalg.norm(n)
    return out, np.ones((H, W))


V0 = LIGHT[2]                           # lambert of a flat, camera-facing surface
SPEC = (0.16, 1.6, 2.4)                 # halo band: lambert above V0+.16, ~2 px inside the lit rim
HALO_MAX_ROW = 8                        # (head-template row) the halo sits on the crown, never on hair under a cap
THRESH = {  # material: (lit above, shadow below, deep below) relative to V0, (auto lo, auto hi)
    'skin': ((0.10, -0.30, -9.0), (1, 3)),
    'hair': ((0.08, -0.22, -0.62), (1, 3)),
    'acc': ((0.08, -0.22, -0.62), (1, 3)),
    'top': ((0.10, -0.20, -0.62), (0, 3)),
    'legs': ((0.10, -0.20, -0.62), (0, 3)),
    'shoes': ((0.06, -0.25, -0.70), (0, 3)),
    'belt': ((0.10, -0.25, -0.70), (0, 3)),
}


def render(cv, pal, shadow=True):
    ramps = pal['ramps']
    ch, layer = cv.ch, cv.layer
    if pal.get('blush') is None:                 # no blush on darker skin: plain cheek
        ch = np.where(ch == 'r', 's', ch)
        cv.ch = ch
    tone = np.full((H, W), -1, dtype=int)
    mat = np.full((H, W), '', dtype='<U6')
    for y in range(H):
        for x in range(W):
            c = ch[y, x]
            if c in LET:
                mat[y, x] = LET[c][0]
    # volume lighting per layer / family / connected component
    nrm = np.full((H, W, 3), np.nan)
    dep = np.zeros((H, W))
    glossy = np.zeros((H, W), bool)
    for lid, kind in enumerate(cv.kinds):
        lmask = (layer == lid) & (ch != '.') & (ch != 'o')
        if not lmask.any():
            continue
        if kind == 'flat':
            nrm[lmask] = (0.0, 0.0, 1.0)
            dep[lmask] = 1
            continue
        if kind == 'dome':
            groups = [lmask]
        else:  # split by family
            fams = {}
            for y, x in zip(*np.nonzero(lmask)):
                c = ch[y, x]
                fam = 'hand' if c in HAND else LET.get(c, ('', '', 0, 'x'))[3]
                fams.setdefault(fam, np.zeros((H, W), bool))[y, x] = True
            groups = list(fams.values())
        for g in groups:
            for comp in _components(g):
                lv, dd = _dome_light(comp) if kind == 'dome' else _cyl_light(comp)
                nrm[comp] = lv[comp]
                dep[comp] = dd[comp]
                if kind == 'dome' and comp.sum() > 30:
                    glossy |= comp
    for y in range(H):
        for x in range(W):
            c = ch[y, x]
            if c not in LET:
                continue
            m, mode, val, _ = LET[c]
            if mode == 'f':
                tone[y, x] = val
            elif mode == 'a':
                (hi, lo, lo2), (tlo, thi) = THRESH[m]
                n = nrm[y, x]
                if np.isnan(n[0]):
                    v = 0
                else:
                    if m == 'skin':          # faces read best shaded side-to-side: flatten vertical curvature
                        n = np.array([n[0], n[1] * 0.35, n[2]])
                        n = n / np.linalg.norm(n)
                    v = float(n @ LIGHT) - V0
                t = 2 + (1 if v > hi else 0) - (1 if v < lo else 0) - (1 if v < lo2 else 0)
                t = max(tlo, min(thi, t)) + val
                # glossy 'halo' band on hair / hats: a ring just inside the lit rim
                if m == 'hair' and glossy[y, x] and val == 0 and y - cv.head_dy <= HALO_MAX_ROW \
                        and v > SPEC[0] and SPEC[1] <= dep[y, x] <= SPEC[2]:
                    t = 4
                tone[y, x] = max(0, min(4, t))
    # contact shadows ------------------------------------------------------
    # hair / hat fringe darkens the skin right under it
    for y in range(1, H):
        for x in range(W):
            if mat[y, x] != 'skin' or LET[ch[y, x]][1] != 'a' or cv.kinds[layer[y, x]] == 'split':
                continue
            la = layer[y - 1, x]
            if mat[y - 1, x] in ('hair', 'acc') or (ch[y - 1, x] == 'o' and la >= 0 and la != layer[y, x]
                                                     and cv.kinds[la] != 'split'):
                tone[y, x] = max(1, tone[y, x] - 1)
    # the head throws a shadow on the shoulders
    head_layers = {lid for lid, k in enumerate(cv.kinds) if k != 'split'}
    for x in range(W):
        for y in range(1, H - 1):
            if layer[y - 1, x] in head_layers and layer[y, x] not in head_layers and mat[y, x] in ('top', 'belt') \
                    and LET[ch[y, x]][1] == 'a':
                tone[y, x] = max(0, tone[y, x] - 1)
                if mat[y + 1, x] in ('top',) and 12 <= x <= 19 and LET[ch[y + 1, x]][1] == 'a':
                    tone[y + 1, x] = max(0, min(tone[y + 1, x], tone[y, x] + 1))
                break
    # colour ---------------------------------------------------------------
    out = Spr(W, H)
    if shadow:
        _ground_shadow(out)
    img = out.a
    solid = (ch != '.')
    for y in range(H):
        for x in range(W):
            c = ch[y, x]
            if c == '.':
                continue
            if c == 'o':
                continue
            m, mode, val, _ = LET[c]
            if mode == 'x':
                col = pal[m]
            else:
                col = ramps[m][tone[y, x]]
            img[y, x] = (*col, 255)
    # outlines: authored 'o' + automatic 1-px outline around the silhouette
    auto = np.zeros((H, W), bool)
    for y in range(H):
        for x in range(W):
            if solid[y, x]:
                continue
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                yy, xx = y + dy, x + dx
                if 0 <= yy < H and 0 <= xx < W and solid[yy, xx] and ch[yy, xx] != 'o':
                    auto[y, x] = True
                    break
    for y in range(H):
        for x in range(W):
            if not (ch[y, x] == 'o' or auto[y, x]):
                continue
            img[y, x] = (*_selout(x, y, ch, mat, tone, ramps), 255)
    return out


def _selout(x, y, ch, mat, tone, ramps):
    """Sel-out outline: dark ink tinted by the material it wraps, a touch lighter where the
    outline faces the light (material below/right of it) and darkest on the shadow side."""
    score = {}
    lit = shade = 0
    for dy, dx, w in ((0, 1, 1.0), (1, 0, 1.0), (0, -1, 1.0), (-1, 0, 1.0),
                      (1, 1, .4), (-1, -1, .4), (1, -1, .4), (-1, 1, .4)):
        yy, xx = y + dy, x + dx
        if 0 <= yy < H and 0 <= xx < W and mat[yy, xx] and mat[yy, xx] in ramps:
            score[mat[yy, xx]] = score.get(mat[yy, xx], 0) + w
            if w == 1.0:
                if dx > 0 or dy > 0:
                    lit += 1
                else:
                    shade += 1
    if not score:
        return INK
    m = max(score, key=lambda k: (score[k], -sum(ramps[k][0])))
    t = 0.5 if m == 'skin' else 0.38
    if lit and not shade:
        t += SELOUT_LIT
    return _mix(INK, ramps[m][0], t)


def _ground_shadow(s):
    for y in range(H):
        for x in range(W):
            dx = (x + 0.5 - 16.0) / 7.2
            dy = (y + 0.5 - 30.4) / 1.9
            r = dx * dx + dy * dy
            if r <= 1.0:
                a = 70 if r > 0.55 else 100
                s.a[y, x] = (22, 26, 44, a)


# ── Heads ───────────────────────────────────────────────────────────────────
# A head = the shared base FACE for a view, with a hair-style overlay painted on top, plus optional
# extra volumes (bun, ponytail, hat crown, brim …).  Rows are 32 px wide in frame coordinates.
# Overlays are {frame_row: run-length row}: "7.o16ho7." = 7×'.', 'o', 16×'h', 'o', 7×'.'.
# In overlays '.' keeps what is below and ',' erases.  Any silhouette edge gets an automatic outline.
# letters: o outline · h/H/i hair (auto-lit, -1, +1; a halo highlight is added automatically)
#          s/S/t skin · Q skin shine · e/E/w eye, iris, white · r blush · m mouth
#          a/A/j accent (hat, hood, tie) auto-lit · z/Z/J accent fixed shadow / deep / highlight


def _rle(row):
    out, num = [], ''
    for ch in row:
        if ch.isdigit():
            num += ch
            continue
        out.append(ch * (int(num) if num else 1))
        num = ''
    r = ''.join(out)
    assert len(r) == W, (row, len(r))
    return r


def _grid_from(spec):
    """{row: rle} → list of H rows."""
    g = ['.' * W] * H
    for y, r in spec.items():
        g[y] = _rle(r)
    return g


HEAD_DY = 1          # templates are authored with the skull top on row 2; frames place it on row 3
FACE = {
    'down': _grid_from({
        2: "12.8o12.",
        3: "10.2o8s2o10.",
        4: "9.o12so9.",
        5: "8.o14so8.", 6: "8.o14so8.", 7: "8.o14so8.", 8: "8.o14so8.", 9: "8.o14so8.",
        10: "8.o3swe4swe3so8.",
        11: "8.o3see4see3so8.",
        12: "8.o3sEE4sEE3so8.",
        13: "8.os2r8s2rso8.",
        14: "8.o6s2m6so8.",
        15: "9.o12so9.",
        16: "10.12o10.",
    }),
    'left': _grid_from({
        2: "11.8o13.",
        3: "9.2o8s2o11.",
        4: "8.o12so10.",
        5: "7.o14so9.",
        6: "7.o15so8.", 7: "7.o15so8.", 8: "7.o15so8.", 9: "7.o15so8.",
        10: "7.oswe12so8.",
        11: "7.osee12so8.",
        12: "6.o2sEE12so8.",
        13: "7.o2s2r11so8.",
        14: "7.osm12so9.",
        15: "8.o12so10.",
        16: "9.12o11.",
    }),
    'up': _grid_from({
        2: "12.8o12.",
        3: "10.2o8s2o10.",
        4: "9.o12so9.",
        5: "8.o14so8.", 6: "8.o14so8.", 7: "8.o14so8.", 8: "8.o14so8.", 9: "8.o14so8.",
        10: "8.o14so8.", 11: "8.o14so8.", 12: "8.o14so8.", 13: "8.o14so8.", 14: "8.o14so8.",
        15: "9.o12so9.",
        16: "10.12o10.",
    }),
}

# HAIR[style][view] = list of (kind, {row: rle}[, where])
#   kind 'head'  → overlay on the base face (one rounded volume with it)
#   kind 'dome'  → its own rounded volume;  'flat' → flat volume (brims)
#   where 'back' (behind the body), 'mid' (after body, before head), 'front' (after head, default)
HAIR = {}

HAIR['short'] = {
    'down': [('head', {
        3: "10.2o8h2o10.", 4: "9.o12ho9.", 5: "8.o14ho8.",
        6: "7.o16ho7.",
        7: "7.o5hH10ho7.",
        8: "7.o5hH4hH5ho7.",
        9: "7.o4h2.4h2.4ho7.",
        10: "7.o3h4.2h4.3ho7.",
        11: "7.o2h12.2ho7.",
        12: "7.oh14.ho7.",
    })],
    'left': [('head', {
        3: "9.2o8h2o11.", 4: "8.o12ho10.", 5: "7.o15ho8.",
        6: "7.o16ho7.", 7: "7.o10hH5ho7.", 8: "7.o9hH6ho7.",
        9: "7.o.h2.4hH7ho7.",
        10: "7.o4.2hss8ho7.",
        11: "7.o4.2hSs8ho7.",
        12: "14.sS8ho7.",
        13: "17.6h9.",
        14: "18.4h10.",
        15: "19.2h11.",
    })],
    'up': [('head', {
        3: "10.2o8h2o10.", 4: "9.o12ho9.", 5: "8.o14ho8.",
        6: "7.o16ho7.", 7: "7.o16ho7.", 8: "7.o16ho7.", 9: "7.o16ho7.",
        10: "7.o5hH4hH5ho7.",
        11: "7.o5hH4hH5ho7.",
        12: "7.o4hH6hH4ho7.",
        13: "8.o14ho8.",
        14: "8.o3hH6hH3ho8.",
        15: "9.o2hH6.H2ho9.",
    })],
}

HAIR['long'] = {
    'down': [('head', {
        3: "10.2o8h2o10.", 4: "9.o12ho9.", 5: "8.o14ho8.",
        6: "7.o16ho7.", 7: "7.o16ho7.",
        8: "6.o5hH6hH5ho6.",
        9: "6.o7hH2hH7ho6.",
        10: "6.o3h2h3.2h3.2h3ho6.",
        11: "6.o3h12.3ho6.",
        12: "6.ohHh12.hHho6.", 13: "6.ohHh12.hHho6.", 14: "6.ohHh12.hHho6.",
        15: "6.ohHh12.hHho6.", 16: "6.ohHh12.hHho6.",
        17: "6.ohHho10.ohHho6.", 18: "6.ohHho10.ohHho6.", 19: "6.o3ho10.o3ho6.",
        20: "7.oho12.oho7.",
        21: "8.o14.o8.",
    })],
    'left': [('head', {
        3: "9.2o8h2o11.", 4: "8.o12ho10.", 5: "7.o15ho8.",
        6: "7.o16ho7.", 7: "7.o10hH5ho7.", 8: "7.o9hH6ho7.",
        9: "7.o.h2.4hH7ho7.",
        10: "7.o4.4hH7ho7.", 11: "7.o4.4hH7ho7.",
        12: "12.4hH7ho7.", 13: "12.5hH6ho7.",
        14: "13.4hH6ho7.", 15: "14.4hH5ho7.", 16: "15.4hH4ho7.",
        17: "15.o3hH4ho7.", 18: "15.o3hH4ho7.", 19: "15.o3hH4ho7.",
        20: "16.o2hH3ho8.",
        21: "16.o2ho3ho8.",
        22: "17.2o.3o9.",
    })],
    'up': [('head', {
        3: "10.2o8h2o10.", 4: "9.o12ho9.", 5: "8.o14ho8.",
        6: "7.o16ho7.", 7: "7.o16ho7.",
        8: "6.o18ho6.", 9: "6.o18ho6.",
        10: "6.o4hH4hH3hH4ho6.", 11: "6.o4hH4hH3hH4ho6.", 12: "6.o4hH4hH3hH4ho6.",
        13: "6.o4hH4hH3hH4ho6.", 14: "6.o4hH4hH3hH4ho6.", 15: "6.o4hH4hH3hH4ho6.",
        16: "6.o4hH4hH3hH4ho6.",
        17: "7.o3hH4hH3hH3ho7.", 18: "7.o3hH4hH3hH3ho7.",
        19: "8.o2hH4hH3hH2ho8.",
        20: "9.ohH4hH3hHho9.",
        21: "11.o3h2o3ho11.",
        22: "12.3o2.3o12.",
    })],
}

HAIR['cap'] = {
    'down': [('head', {
        1: "12.8o12.",
        2: "10.2o8a2o10.",
        3: "9.o5a2w5ao9.",
        4: "8.o6a2w6ao8.",
        5: "7.o16ao7.",
        6: "7.o16ao7.",
        7: "7.o16ho7.", 8: "7.o16ho7.",
        9: "7.o2h12.2ho7.",
        10: "7.o2h12.2ho7.", 11: "7.o2h12.2ho7.",
        12: "7.oh14.ho7.",
    }), ('flat', {
        6: "7.o16jo7.",
        7: "7.oA14jAo7.",
        8: "8.o14Ao8.",
        9: "9.14o9.",
    })],
    'left': [('head', {
        1: "11.8o13.",
        2: "9.2o8a2o11.",
        3: "8.o12ao10.",
        4: "7.oa2w12ao8.",
        5: "7.o16ao7.",
        6: "7.o16Ao7.",
        7: "7.o5.4hH6ho7.",
        8: "7.o5.4hH6ho7.",
        9: "7.o5.3hH7ho7.",
        10: "7.o4.2hss8ho7.",
        11: "7.o4.2hSs8ho7.",
        12: "14.sS8ho7.",
        13: "17.6h9.",
        14: "18.4h10.",
        15: "19.2h11.",
    }), ('flat', {
        5: "6.2o24.",
        6: "6.5a21.",
        7: "6.4Z22.",
        8: "6.4o22.",
    })],
    'up': [('head', {
        1: "12.8o12.",
        2: "10.2o8a2o10.",
        3: "9.o12ao9.",
        4: "8.o14ao8.",
        5: "7.o16ao7.",
        6: "7.o16ao7.",
        7: "7.o6ao2ho6ao7.",
        8: "7.o6A4Z6Ao7.",
        9: "7.o16Go7.",
        10: "7.o5hH4hH5ho7.",
        11: "7.o5hH4hH5ho7.",
        12: "7.o4hH6hH4ho7.",
        13: "8.o14ho8.",
        14: "8.o3hH6hH3ho8.",
        15: "9.o2hH6.H2ho9.",
    })],
}

HAIR['ponytail'] = {
    'down': [('head', {
        3: "10.2o8h2o10.", 4: "9.o12ho9.", 5: "8.o14ho8.",
        6: "7.o16ho7.",
        7: "7.o4hH4hH6ho7.",
        8: "7.o10h.5ho7.",
        9: "7.o8h4.4ho7.",
        10: "7.o4h9.3ho7.",
        11: "7.o3h11.2ho7.",
        12: "7.o2h13.ho7.",
        13: "7.oh23.",
    }), ('dome', {
        3: "21.3o8.",
        4: "20.o3ao7.",
        5: "20.o2a2ho6.",
        6: "21.o4ho5.",
        7: "22.o4ho4.", 8: "22.o4ho4.", 9: "22.o4ho4.", 10: "22.o4ho4.", 11: "22.o4ho4.", 12: "22.o4ho4.",
        13: "22.o3ho5.", 14: "22.o3ho5.",
        15: "22.o2ho6.",
        16: "23.2o7.",
    }, 'back')],
    'left': [('head', {
        3: "9.2o8h2o11.", 4: "8.o12ho10.", 5: "7.o15ho8.",
        6: "7.o16ho7.", 7: "7.o10hH5ho7.", 8: "7.o9hH6ho7.",
        9: "7.o.h.5hH7ho7.",
        10: "7.o4.2hss8ho7.",
        11: "7.o5.hSs8ho7.",
        12: "14.sS8ho7.",
        13: "17.6h9.",
        14: "18.4h10.",
        15: "19.2h11.",
    }), ('dome', {
        3: "19.3o10.",
        4: "19.o2ao9.",
        5: "20.o2aho7.",
        6: "21.o3ho6.",
        7: "22.o3ho5.", 8: "22.o3ho5.", 9: "22.o3ho5.", 10: "22.o3ho5.", 11: "22.o3ho5.",
        12: "22.o2ho6.", 13: "22.o2ho6.",
        14: "21.o2ho7.",
        15: "21.oho8.",
        16: "22.o9.",
    }, 'front')],
    'up': [('head', {
        3: "10.2o8h2o10.", 4: "9.o12ho9.", 5: "8.o14ho8.",
        6: "7.o16ho7.", 7: "7.o16ho7.",
        8: "7.o4hH6hH4ho7.",
        9: "7.o3hH8hH3ho7.",
        10: "7.o3hH8hH3ho7.",
        11: "7.o2hH10hH2ho7.",
        12: "7.o16ho7.",
        13: "8.o14ho8.",
        14: "8.o14ho8.",
        15: "9.o2h8.2ho9.",
    }), ('dome', {
        5: "13.6o13.",
        6: "13.o4ao13.",
        7: "12.o6ho12.", 8: "12.o6ho12.", 9: "12.o6ho12.", 10: "12.o6ho12.", 11: "12.o6ho12.",
        12: "12.o6ho12.",
        13: "13.o4ho13.", 14: "13.o4ho13.", 15: "13.o4ho13.", 16: "13.o4ho13.", 17: "13.o4ho13.",
        18: "14.o2ho14.",
        19: "15.2o15.",
    }, 'front')],
}

HAIR['bun'] = {
    'down': [('head', {
        3: "10.2o8h2o10.", 4: "9.o12ho9.", 5: "8.o14ho8.",
        6: "8.o6hH7ho8.",
        7: "8.o6hH7ho8.",
        8: "8.o6h2.6ho8.",
        9: "8.o4h6.4ho8.",
        10: "8.o3h8.3ho8.",
        11: "8.o2h10.2ho8.",
        12: "8.oh12.ho8.",
    }), ('dome', {
        1: "14.4o14.",
        2: "13.o4ho13.",
        3: "12.o6ho12.", 4: "12.o6ho12.",
        5: "13.o4ao13.",
        6: "14.4o14.",
    })],
    'left': [('head', {
        3: "9.2o8h2o11.", 4: "8.o12ho10.", 5: "7.o14ho9.",
        6: "7.o15ho8.", 7: "7.o10hH4ho8.", 8: "7.o9hH5ho8.",
        9: "7.o.h.5hH6ho8.",
        10: "7.o4.2hss7ho8.",
        11: "7.o5.hSs7ho8.",
        12: "14.sS7ho8.",
        13: "17.6h9.",
        14: "18.4h10.",
        15: "19.2h11.",
    }), ('dome', {
        1: "18.4o10.",
        2: "17.o4ho9.",
        3: "16.o6ho8.", 4: "16.o6ho8.",
        5: "17.o4ao9.",
        6: "18.4o10.",
    })],
    'up': [('head', {
        3: "10.2o8h2o10.", 4: "9.o12ho9.", 5: "8.o14ho8.",
        6: "8.o14ho8.", 7: "8.o3hH6hH3ho8.", 8: "8.o3hH6hH3ho8.",
        9: "8.o2hH8hH2ho8.", 10: "8.o2hH8hH2ho8.",
        11: "8.o14ho8.", 12: "8.o14ho8.", 13: "8.o14ho8.",
        14: "8.o3hH6hH3ho8.",
        15: "9.o2hH6.H2ho9.",
    }), ('dome', {
        2: "14.4o14.",
        3: "13.o4ho13.",
        4: "12.o6ho12.", 5: "12.o6ho12.", 6: "12.o6ho12.",
        7: "13.o4ao13.",
        8: "14.4o14.",
    })],
}

HAIR['spiky'] = {
    'down': [('head', {
        1: "11.o3.2o3.o11.",
        2: "10.oho.ohho.oho10.",
        3: "9.o3ho4ho3ho9.",
        4: "8.o4hH4hH4ho8.",
        5: "7.o5hH4hH5ho7.",
        6: "6.o18ho6.",
        7: "5.o20ho5.",
        8: "6.o18ho6.",
        9: "6.oh5h.4h.5hho6.",
        10: "6.oh4h3.2h3.4hho6.",
        11: "6.oh2h12.2hho6.",
        12: "7.oh14.ho7.",
    })],
    'left': [('head', {
        2: "11.h5.h14.",
        3: "10.3h2.4h13.",
        4: "9.5hH5ho.h9.",
        5: "7.o16ho7.",
        6: "7.o17ho6.",
        7: "7.o10hH7ho5.",
        8: "7.o9hH7ho6.",
        9: "7.o.h2.4hH7ho7.",
        10: "7.o4.2hss8ho7.",
        11: "7.o4.2hSs8ho7.",
        12: "14.sS8ho7.",
        13: "17.6h9.",
        14: "18.4h10.",
        15: "19.2h11.",
    })],
    'up': [('head', {
        1: "11.o3.2o3.o11.",
        2: "10.oho.ohho.oho10.",
        3: "9.o3ho4ho3ho9.",
        4: "8.o4hH4hH4ho8.",
        5: "7.o5hH4hH5ho7.",
        6: "6.o18ho6.",
        7: "5.o20ho5.",
        8: "6.o18ho6.",
        9: "6.o5hH6hH5ho6.",
        10: "6.o5hH6hH5ho6.",
        11: "6.o4hH8hH4ho6.",
        12: "7.o16ho7.",
        13: "7.o16ho7.",
        14: "8.o14ho8.",
        15: "9.oh.2h.2h.2h.ho9.",
    })],
}

HAIR['hood'] = {
    'down': [('head', {
        2: "12.2,4a2,12.",
        3: "10.2,3aA4a2,10.",
        4: "9.2,4aA5a2,9.",
        5: "8.2,5aA6a2,8.",
        6: "8.,6aA7a,8.",
        7: "8.16a8.",
        8: "8.5a6Z5a8.",
        9: "7.3aAZ8TZA3a7.",
        10: "7.3aAZ8.ZA3a7.", 11: "7.3aAZ8.ZA3a7.", 12: "7.3aAZ8.ZA3a7.", 13: "7.3aAZ8.ZA3a7.",
        14: "7.4aZ8.Z4a7.",
        15: "6.6aZ6.Z6a6.",
        16: "6.3aA2a8.2aA3a6.",
        17: "6.3aA12aA3a6.",
        18: "7.18a7.",
    })],
    'left': [('head', {
        2: "11.2,5a,13.",
        3: "9.2,9a,11.",
        4: "8.,9aA3a10.",
        5: "7.,11aA3a9.",
        6: "7.12aA4a8.",
        7: "7.13aA4a7.",
        8: "6.2a5Z6aA5a7.",
        9: "6.aZ5T7aA4a7.",
        10: "13.Z6aA4a7.", 11: "13.Z6aA4a7.", 12: "13.Z6aA4a7.", 13: "13.Z6aA4a7.",
        14: "12.Z7aA4a7.",
        15: "11.Z8aA4a7.",
        16: "10.10aA4a7.",
        17: "10.10aA4a7.",
        18: "11.13a8.",
    })],
    'up': [('head', {
        2: "12.2,4a2,12.",
        3: "10.2,3aA4a2,10.",
        4: "9.2,4aA5a2,9.",
        5: "8.2,5aA6a2,8.",
        6: "8.,6aA7a,8.",
        7: "8.7aA8a8.",
        8: "7.8aA9a7.", 9: "7.8aA9a7.", 10: "7.8aA9a7.", 11: "7.8aA9a7.", 12: "7.8aA9a7.",
        13: "7.8aA9a7.", 14: "7.8aA9a7.",
        15: "6.4aA5aA4aA4a6.",
        16: "6.4aA5aA4aA4a6.",
        17: "6.4aA5aA4aA4a6.",
        18: "7.18a7.",
    })],
}

_HAT_CROWN = ('dome', {
    1: "11.10o11.",
    2: "10.o10ao10.", 3: "10.o10ao10.",
    4: "10.o10Ao10.", 5: "10.o10Ao10.",
})
_HAT_BRIM = ('flat', {
    5: "8.2o12.2o8.",
    6: "6.2o16j2o6.",
    7: "5.o20ao5.",
    8: "6.o18Ao6.",
    9: "7.18o7.",
})
HAIR['hat'] = {
    'down': [('head', {
        6: "7.o16ho7.", 7: "7.o16ho7.", 8: "7.o16ho7.", 9: "7.o16ho7.",
        10: "7.o2h12.2ho7.", 11: "7.o2h12.2ho7.",
        12: "7.oh14.ho7.",
    }), _HAT_CROWN, _HAT_BRIM],
    'left': [('head', {
        5: "7.o15ho8.",
        6: "7.o16ho7.", 7: "7.o16ho7.", 8: "7.o16ho7.",
        9: "7.o.h2.12ho7.",
        10: "7.o4.2hss8ho7.",
        11: "7.o4.2hSs8ho7.",
        12: "14.sS8ho7.",
        13: "17.6h9.",
        14: "18.4h10.",
        15: "19.2h11.",
    }), _HAT_CROWN, _HAT_BRIM],
    'up': [('head', {
        5: "8.o14ho8.",
        6: "7.o16ho7.", 7: "7.o16ho7.", 8: "7.o16ho7.", 9: "7.o16ho7.",
        10: "7.o5hH4hH5ho7.",
        11: "7.o5hH4hH5ho7.",
        12: "7.o4hH6hH4ho7.",
        13: "8.o14ho8.",
        14: "8.o3hH6hH3ho8.",
        15: "9.o2hH6.H2ho9.",
    }), _HAT_CROWN, _HAT_BRIM],
}

HAIR['bald'] = {
    'down': [('head', {
        4: "12.2Q18.",
        6: "7.o2h12.2ho7.",
        7: "6.o3h12.3ho6.",
        8: "6.o3h12.3ho6.",
        9: "6.o3h2.2h4.2h2.3ho6.",
        10: "6.osS14.Sso6.",
        11: "6.osS14.Sso6.",
        12: "7.os14.so7.",
        13: "13.6h13.",
        14: "10.12h10.",
        15: "10.12h10.",
        16: "9.o12ho9.",
        17: "11.o8ho11.",
        18: "12.8o12.",
    })],
    'left': [('head', {
        4: "12.2Q18.",
        8: "16.8ho7.",
        9: "9.2h4.9ho7.",
        10: "14.sS8ho7.",
        11: "14.Ss8ho7.",
        12: "14.sS8ho7.",
        13: "8.3h6.6h9.",
        14: "8.7h3.4h10.",
        15: "9.7h16.",
        16: "9.6h17.",
        17: "10.4ho17.",
        18: "10.4o18.",
    })],
    'up': [('head', {
        4: "12.2Q18.",
        7: "7.o2h12.2ho7.",
        8: "7.o16ho7.",
        9: "7.o16ho7.",
        10: "6.os16hso6.",
        11: "6.os16hso6.",
        12: "7.o16ho7.",
        13: "8.o5hH2hH5ho8.",
        14: "8.o14ho8.",
        15: "9.o12ho9.",
    })],
}


def _overlay(base, over):
    rows = [list(r) for r in base]
    for y, row in enumerate(over):
        for x, c in enumerate(row):
            if c == '.':
                continue
            rows[y][x] = '.' if c == ',' else c
    return [''.join(r) for r in rows]


def head_layers(style, view):
    """→ list of (kind, rows, where) in paint order groups; rows are full-frame (H rows)."""
    parts = HAIR[style][view]
    head_rows = FACE[view]
    out = []
    for kind, spec, *rest in parts:
        if kind == 'head':
            head_rows = _overlay(head_rows, _grid_from(spec))
    out.append(('dome', head_rows, 'head'))
    for kind, spec, *rest in parts:
        if kind != 'head':
            out.append((kind, _grid_from(spec), rest[0] if rest else 'front'))
    return out


# ── Bodies ──────────────────────────────────────────────────────────────────
# body letters: c/C/x torso (top) · f/F sleeves · y deep top line · k belt/trim · v buckle
#               s hands · p/P/u legs (d second leg) · b/B/n shoes · U deep legs line

def _grid():
    return [['.'] * W for _ in range(H)]


def _rows(g):
    return [''.join(r) for r in g]


def _front_pose(view, pose):
    """→ (bob, lifted screen side or None, forward-arm screen side or None)."""
    if pose == 0:
        return 0, None, None
    # stepA = left foot forward. Facing the camera the character's left is screen-right.
    lift = ('R' if pose == 1 else 'L') if view == 'down' else ('L' if pose == 1 else 'R')
    return -1, lift, ('L' if lift == 'R' else 'R')


def body_front(style, view, pose):
    g = _grid()

    def P(x, y, c):
        if 0 <= x < W and 0 <= y < H:
            g[y][x] = c

    def span(x0, x1, y, c):
        for x in range(x0, x1 + 1):
            P(x, y, c)

    bob, lift, fwd = _front_pose(view, pose)
    T = 17 + bob                       # shoulder row (under the chin)
    front = view == 'down'
    if style == 'robe':
        # sleeves are wide; robe falls to the ankles
        span(10, 21, T, 'c')
        for side, (x0, x1) in (('L', (8, 10)), ('R', (21, 23))):
            ext = 1 if fwd == side else 0
            span(x0 + (1 if side == 'L' else 0), x1 - (1 if side == 'R' else 0), T + 1, 'f')
            for y in range(T + 2, T + 6 + ext):
                span(x0, x1, y, 'f')
            span(x0, x1, T + 6 + ext, 'k')                     # cuff trim
            hx0 = x0 + 1 if side == 'L' else x0
            span(hx0, hx0 + 1, T + 7 + ext, 's')
        span(11, 20, T + 1, 'c')
        for y in range(T + 2, T + 7):
            span(12, 19, y, 'c')
            P(11, y, 'o'); P(20, y, 'o')
        for y in range(T + 7, 29 + bob):
            x0, x1 = (11, 20) if y < T + 9 else (10, 21)
            span(x0, x1, y, 'c')
        span(10, 21, 28 + bob, 'C')
        # front trim / back seam
        if front:
            for y in range(T + 1, 29 + bob):
                span(15, 16, y, 'k')
            span(12, 19, T + 5, 'k')                            # sash
        else:
            span(12, 19, T + 1, 'x')
            span(12, 19, T + 5, 'k')
        span(10, 21, 28 + bob, 'k' if front else 'C')
        # feet peeking under the hem
        for side, (x0, x1) in (('L', (12, 14)), ('R', (17, 19))):
            if lift == side:
                continue
            for y in range(28 + bob + 1, 29):
                span(x0, x1, y, 'p' if side == 'L' else 'd')
            span(x0, x1, 29, 'b')
            span(x0, x1, 30, 'b' if front else 'B')
        return _rows(g)

    # casual: shirt / jacket, belt, trousers
    span(10, 21, T, 'c')
    span(11, 20, T + 1, 'c')
    for y in range(T + 2, T + 6):
        span(12, 19, y, 'c')
        P(11, y, 'o'); P(20, y, 'o')
    if front:
        # collar points, neck opening and the jacket's front placket
        P(13, T + 1, 'X'); P(14, T + 1, 'x'); P(17, T + 1, 'x'); P(18, T + 1, 'X')
        P(15, T + 1, 'T'); P(16, T + 1, 'T')
        P(15, T + 2, 'y'); P(16, T + 2, 'y')
        for y in range(T + 3, T + 6):
            P(15, y, 'C'); P(16, y, 'C')
    else:
        span(12, 19, T + 1, 'x')
    # arms
    for side, (x0, x1) in (('L', (9, 10)), ('R', (21, 22))):
        ext = 1 if fwd == side else 0
        span(x0, x1, T + 1, 'f')
        for y in range(T + 2, T + 6 + ext):
            span(x0, x1, y, 'f')
        span(x0, x1, T + 6 + ext, 's')
        span(x0, x1, T + 7 + ext, 's')
    # belt
    span(11, 20, T + 6, 'k')
    if front:
        span(15, 16, T + 6, 'v')
    # hips + legs
    span(12, 19, T + 7, 'p')
    for side, (x0, x1, sx0, sx1) in (('L', (12, 14, 11, 14)), ('R', (17, 19, 17, 20))):
        up = 2 if lift == side else 0
        c = 'p' if side == 'L' else 'd'
        for y in range(T + 8, 29 - up):
            span(x0, x1, y, c)
        span(sx0, sx1, 29 - up, 'b')
        span(sx0, sx1, 30 - up, 'b' if front else 'B')
        if front:
            P(sx0, 29 - up, 'n')                               # toe shine
    return _rows(g)


def body_rows(style, view, pose, gear=()):
    rows = body_front(style, view, pose) if view in ('down', 'up') else BODY_SIDE[style][pose]
    if 'pack' in gear:
        rows = _add_pack(rows, view, pose)
    return rows


def _add_pack(rows, view, pose):
    """Adventurer's backpack in the accent colour: straps from the front, the pack from behind / in profile."""
    g = [list(r) for r in rows]
    T = (17 if view in ('down', 'up') else 17) - (1 if pose else 0)

    def P(x, y, c):
        if 0 <= x < W and 0 <= y < H:
            g[y][x] = c
    if view == 'down':
        for y in range(T + 1, T + 5):                  # shoulder straps
            P(13, y, 'A'); P(18, y, 'A')
        P(13, T + 5, 'o'); P(18, T + 5, 'o')
    elif view == 'up':
        P(13, T, 'A'); P(18, T, 'A')                   # straps over the shoulders
        for x in range(13, 19):
            P(x, T + 1, 'o')
        P(12, T + 2, 'o'); P(19, T + 2, 'o')
        for y in range(T + 2, T + 7):
            for x in range(12 if y > T + 2 else 13, 20 if y > T + 2 else 19):
                P(x, y, 'a')
        for x in range(12, 20):
            P(x, T + 4, 'A')                           # flap edge
        for x in range(13, 19):
            P(x, T + 3, 'A')
        P(15, T + 4, 'v'); P(16, T + 4, 'v')          # clasp
        for x in range(12, 20):
            P(x, T + 7, 'o')
    else:                                              # profile, facing left: pack on the back
        for y in range(T + 1, T + 6):
            P(19, y, 'o')
            for x in range(20, 23):
                P(x, y, 'a')
        P(20, T + 1, 'A'); P(21, T + 1, 'A'); P(22, T + 1, 'A')
        P(20, T + 2, 'A'); P(21, T + 2, 'A')
        P(22, T + 5, '.')                              # rounded bottom corner
        P(17, T + 1, 'A')                              # strap over the shoulder
    return [''.join(r) for r in g]


def _side(y0, rows):
    g = ['.' * W] * H
    for i, r in enumerate(rows):
        g[y0 + i] = r
    return g


# Side view (facing left; 'right' mirrors it). Stand has its shoulder row at 17, steps bob up to 16.
BODY_SIDE = {
    'casual': [
        _side(17, [
            "............cccccccc............",
            "............cfffffcc............",
            "............cofffocc............",
            "............cofffocc............",
            "............cofffocc............",
            "............coFFFocc............",
            "............kosssokk............",
            "............posssopp............",
            ".............poooUDD............",
            ".............ppppUDD............",
            ".............ppppUDD............",
            ".............ppppUDD............",
            "...........bbbbbbBBB............",
            "...........bbbbbbBBB............",
        ]),
        _side(16, [   # stepA: near (left) leg forward, near arm back, far arm forward
            "............cccccccc............",
            "............cfffffcc............",
            "............ccofffoc............",
            "...........Fccofffoc............",
            "..........SScccoFFFo............",
            "..........SSccccosss............",
            "............kkkkosss............",
            "............pppppooo............",
            "............pppp.DDD............",
            "...........pppp.DDDD............",
            "...........pppp..DDD............",
            "..........pppp...DDDD...........",
            "..........pppp....DDD...........",
            ".........bbbbb.....BBB..........",
            "........bbbbbb....BBBB..........",
        ]),
        _side(16, [   # stepB: far leg forward, near arm forward, far arm back
            "............cccccccc............",
            "............cfffffcc............",
            "............offfoccc............",
            "............fffoccccF...........",
            "...........FFFocccccSS..........",
            "..........sssoccccccSS..........",
            "..........sssokkkkkk............",
            "............oppppppp............",
            "............DDDpppp.............",
            "...........DDD..pppp............",
            "...........DDD..pppp............",
            "..........DDD....pppp...........",
            "..........DDD....pppp...........",
            ".........BBBB.....bbbb..........",
            "........BBBBB....bbbb...........",
        ]),
    ],
    'robe': [
        _side(17, [
            "............cccccccc............",
            "............cfffffcc............",
            "............coffffoc............",
            "............coffffoc............",
            "............coffffoc............",
            "............offffffo............",
            "............kkkkkkkk............",
            "............cosssocc............",
            "...........cccooocccc...........",
            "...........cccccccccc...........",
            "...........cccccccccc...........",
            "..........kkkkkkkkkkk...........",
            "..........bbbbb.BBB.............",
            "..........bbbbb.BBB.............",
        ]),
        _side(16, [
            "............cccccccc............",
            "............cfffffcc............",
            "............ccoffffo............",
            "...........Fccoffffo............",
            "..........FFccofffffo...........",
            "..........SSccokkkkko...........",
            "............kkkosssο............".replace('ο', 'o'),
            "...........cccccooocc...........",
            "..........ccccccccccc...........",
            "..........cccccccccccc..........",
            ".........ccccccccccccc..........",
            ".........kkkkkkkkkkkkk..........",
            "..........ppp......DD...........",
            ".........bbbb......BBB..........",
            "........bbbbb......BBB..........",
        ]),
        _side(16, [
            "............cccccccc............",
            "............cfffffcc............",
            "............offffocc............",
            "...........fffffocccF...........",
            "..........ffffffocccFF..........",
            "..........kkkkkkocccSS..........",
            "...........sssokkkkkSS..........",
            "...........oooccccccc...........",
            "..........ccccccccccc...........",
            "..........cccccccccccc..........",
            ".........ccccccccccccc..........",
            ".........kkkkkkkkkkkkk..........",
            "..........DDD......pp...........",
            ".........BBBB......bbb..........",
            "........BBBBB......bbb..........",
        ]),
    ],
}


# ── Frames ──────────────────────────────────────────────────────────────────
def compose(head, body, direction, idx, gear=()):
    view = 'left' if direction in ('left', 'right') else direction
    cv = Canvas()
    bob = -1 if idx else 0
    cv.head_dy = bob + HEAD_DY
    layers = head_layers(head, view)
    for stage in ('back', 'body', 'mid', 'head', 'front'):
        if stage == 'body':
            cv.paint(body_rows(body, view, idx, gear), 'split')
            continue
        for kind, rows, where in layers:
            if where == stage:
                cv.paint(rows, kind, dy=bob + HEAD_DY)
    return cv


def frame(head, body, direction, idx, pal, gear=()):
    """idx: 0 stand, 1 stepA (left foot forward), 2 stepB (right foot forward).
    gear: optional extras, e.g. ('pack',) for the heroes' backpack in the accent colour.

    'right' mirrors the left-facing geometry *before* lighting, so it is still lit from the top-left."""
    cv = compose(head, body, direction, idx, gear)
    if direction == 'right':
        cv.ch = cv.ch[:, ::-1].copy()
        cv.layer = cv.layer[:, ::-1].copy()
    return render(cv, pal)


DIRECTIONS = ('down', 'left', 'right', 'up')


def sheet(head, body, pal, cols=3, gear=()):
    """One character's frames.  cols=3: 3 columns (stand, stepA, stepB) × 4 rows (down, left, right, up);
    cols=12: a single row in game order (down×3, left×3, right×3, up×3) as used in chars.png."""
    out = Spr(W * cols, H * (12 // cols))
    for d, direction in enumerate(DIRECTIONS):
        for c in range(3):
            i = d * 3 + c
            out.blit(frame(head, body, direction, c, pal, gear), (i % cols) * W, (i // cols) * H)
    return out


def _check():
    """Validate every template once at import (row widths, letters, all styles × views)."""
    for style, views in HAIR.items():
        for view in ('down', 'left', 'up'):
            for kind, spec, *rest in views[view]:
                for row in spec.values():
                    r = _rle(row)
                    bad = set(r) - set(LET) - {'.', ',', 'o'}
                    assert not bad, (style, view, row, bad)
    for style, poses in BODY_SIDE.items():
        assert len(poses) == 3
        for g in poses:
            assert len(g) == H and all(len(r) == W for r in g), style


_check()
