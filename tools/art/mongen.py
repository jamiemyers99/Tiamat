"""Procedural pixel-art renderer for Morph battle sprites.

A design is a list of parts (shapes with a material). Parts are rasterised with
signed-distance functions, shaded like lit volumes, quantised onto hue-shifted
ramps, then outlined per part so overlapping pieces read clearly.
"""
import math
import numpy as np
from spr import Spr
from pal import hx, ramp, shift, BAYER4


class Part:
    def __init__(self, kind, mat, z=0, view='both', **kw):
        self.kind, self.mat, self.z, self.view, self.kw = kind, mat, z, view, kw


# ── shape constructors (coordinates in a 96×96 design space) ────────────────
def E(cx, cy, rx, ry, mat, z=0, rot=0, view='both', bulge=1.0):
    return Part('ellipse', mat, z, view, cx=cx, cy=cy, rx=rx, ry=ry, rot=rot, bulge=bulge)


def Cap(x0, y0, x1, y1, r0, r1, mat, z=0, view='both'):
    return Part('capsule', mat, z, view, x0=x0, y0=y0, x1=x1, y1=y1, r0=r0, r1=r1)


def Tri(pts, mat, z=0, view='both', flat=False):
    return Part('poly', mat, z, view, pts=pts, flat=flat)


def Leaf(x, y, length, width, ang, mat, z=0, view='both', vein=True):
    return Part('leaf', mat, z, view, x=x, y=y, length=length, width=width, ang=ang, vein=vein)


def Flame(x, y, h, w, mat, z=0, view='both', lean=0.0):
    return Part('flame', mat, z, view, x=x, y=y, h=h, w=w, lean=lean)


def Eye(x, y, r=3.2, style='round', z=100, look=0.0, col='#1c1a28', iris=None):
    return Part('eye', 'eye', z, 'front', x=x, y=y, r=r, style=style, look=look, col=col, iris=iris)


def Mouth(x, y, w=4, style='smile', z=101, col='#3a1a24'):
    return Part('mouth', 'mouth', z, 'front', x=x, y=y, w=w, style=style, col=col)


def Spot(x, y, r, mat, z=90, view='both'):
    return Part('ellipse', mat, z, view, cx=x, cy=y, rx=r, ry=r, rot=0, bulge=0.3)


# ── rasterisation ──────────────────────────────────────────────────────────
def _grid(S):
    ys, xs = np.mgrid[0:S, 0:S]
    return xs + 0.5, ys + 0.5


def raster(part, S, k):
    """Return (mask, nx, ny, nz) arrays for a part at scale k (design px → sprite px)."""
    X, Y = _grid(S)
    X = X / k; Y = Y / k
    kw = part.kw
    if part.kind == 'ellipse':
        c, s = math.cos(-kw['rot']), math.sin(-kw['rot'])
        dx, dy = X - kw['cx'], Y - kw['cy']
        u = (dx * c - dy * s) / kw['rx']
        v = (dx * s + dy * c) / kw['ry']
        r2 = u * u + v * v
        m = r2 <= 1.0
        nz = np.sqrt(np.clip(1 - r2, 0, 1)) * kw.get('bulge', 1.0) + (1 - kw.get('bulge', 1.0)) * 0.9
        return m, u, v, nz
    if part.kind == 'capsule':
        x0, y0, x1, y1 = kw['x0'], kw['y0'], kw['x1'], kw['y1']
        vx, vy = x1 - x0, y1 - y0
        L2 = vx * vx + vy * vy + 1e-9
        t = np.clip(((X - x0) * vx + (Y - y0) * vy) / L2, 0, 1)
        px, py = x0 + vx * t, y0 + vy * t
        r = kw['r0'] + (kw['r1'] - kw['r0']) * t
        dx, dy = X - px, Y - py
        d = np.sqrt(dx * dx + dy * dy)
        m = d <= r
        nx = dx / np.maximum(r, 0.1)
        ny = dy / np.maximum(r, 0.1)
        nz = np.sqrt(np.clip(1 - nx * nx - ny * ny, 0, 1))
        return m, nx, ny, nz
    if part.kind in ('poly', 'leaf', 'flame'):
        if part.kind == 'poly':
            pts = kw['pts']
        elif part.kind == 'leaf':
            pts = []
            n = 14
            L, W, a = kw['length'], kw['width'], kw['ang']
            ca, sa = math.cos(a), math.sin(a)
            for i in range(n + 1):
                t = i / n
                w = math.sin(t * math.pi) * W / 2
                pts.append((t * L, w))
            for i in range(n, -1, -1):
                t = i / n
                w = math.sin(t * math.pi) * W / 2
                pts.append((t * L, -w))
            pts = [(kw['x'] + px_ * ca - py_ * sa, kw['y'] + px_ * sa + py_ * ca) for px_, py_ in pts]
        else:  # flame: teardrop pointing up
            pts = []
            n = 16
            h, w, lean = kw['h'], kw['w'], kw['lean']
            for i in range(n + 1):
                t = i / n
                ang = math.pi * t
                r = w / 2 * math.sin(ang) ** 0.8
                yy = -h * (1 - t) ** 1.6 if t < 1 else 0
                pts.append((kw['x'] + r + lean * (1 - t) * h * 0.4, kw['y'] - h * (1 - math.cos(ang)) / 2 * 0 + (-(h) * (1 - t))))
            # simpler robust flame polygon
            pts = []
            for i in range(n + 1):
                t = i / n                      # 0 tip → 1 base
                y = kw['y'] - h + h * t
                half = (w / 2) * math.sin(min(1, t * 1.15) * math.pi * 0.62) ** 1.2
                x = kw['x'] + lean * (1 - t) * h * 0.35
                pts.append((x + half, y))
            for i in range(n, -1, -1):
                t = i / n
                y = kw['y'] - h + h * t
                half = (w / 2) * math.sin(min(1, t * 1.15) * math.pi * 0.62) ** 1.2
                x = kw['x'] + lean * (1 - t) * h * 0.35
                pts.append((x - half, y))
            # round bottom
            for i in range(9):
                a = math.pi * i / 8
                pts.insert(n + 1 + i, (kw['x'] + math.cos(a) * w * 0.48, kw['y'] + math.sin(a) * w * 0.3))
        inside = np.zeros(X.shape, dtype=bool)
        n = len(pts)
        j = n - 1
        for i in range(n):
            xi, yi = pts[i]; xj, yj = pts[j]
            cond = ((yi > Y) != (yj > Y)) & (X < (xj - xi) * (Y - yi) / ((yj - yi) + 1e-9) + xi)
            inside ^= cond
            j = i
        # fake normals: from centroid, flattened
        cx = sum(p[0] for p in pts) / n
        cy = sum(p[1] for p in pts) / n
        ext = max(max(abs(p[0] - cx) for p in pts), max(abs(p[1] - cy) for p in pts), 1)
        nx = (X - cx) / ext
        ny = (Y - cy) / ext
        flat = kw.get('flat', False)
        nz = np.sqrt(np.clip(1 - (nx * nx + ny * ny) * (0.5 if not flat else 0.2), 0.15, 1))
        return inside, nx, ny, nz
    raise ValueError(part.kind)


LIGHT = np.array([-0.55, -0.7, 0.65])
LIGHT = LIGHT / np.linalg.norm(LIGHT)

SHINY_ROT = {}
FRONT_ONLY_MATS = ('belly', 'blush', 'nose', 'inner', 'muzzle', 'face')
# seen from behind: the face side of the head (beak, muzzle, belly, inner ears...) is hidden
BACK_HIDE_MATS = FRONT_ONLY_MATS + ('beak',)
# how shiny each material is (specular highlight strength)
GLOSS = {'stone': 0.55, 'bark': 0.25, 'moss': 0.2, 'leaf': 0.7, 'flame': 0.0, 'dark': 0.8, 'fin': 1.1, 'wing': 0.8}
# female forms: accent colours shift hue, body warms slightly (like Pokémon gender differences)
FEMALE_ACCENTS = ('accent', 'crest', 'dot', 'fin', 'horn', 'stem')


def female_mats(mats):
    out = dict(mats)
    for key, col in mats.items():
        c = hx(col)
        if key in FEMALE_ACCENTS:
            out[key] = shift(c, 0.04, 0.06, -42)
        elif key in ('body', 'wing'):
            out[key] = shift(c, 0.025, 0.02, -7)
    return out


def render(parts, mats, S=96, view='front', shiny=False, outline=True, female=False, shadow=None):
    """mats: name -> base colour hex. Returns Spr of size S×S."""
    k = S / 96.0
    if shadow is None:
        shadow = S >= 64
    if female:
        mats = female_mats(mats)
    ramps = {}
    for name, col in mats.items():
        c = hx(col)
        if shiny:
            c = shift(c, 0.02, 0.05, SHINY_ROT.get(name, 150))
        ramps[name] = ramp(c, 7, 0.19, hue=18, sat=0.06)
    NL = 6  # top ramp index
    out = Spr(S, S)
    owner = np.full((S, S), -1, dtype=int)
    zbuf = np.full((S, S), -1e9)
    shade_idx = np.zeros((S, S), dtype=int)
    spec_map = np.zeros((S, S))
    matname = np.full((S, S), '', dtype=object)
    Xs, Ys = np.mgrid[0:S, 0:S][1], np.mgrid[0:S, 0:S][0]
    plist = [p for p in parts if p.view in ('both', view) and p.kind not in ('eye', 'mouth')]
    zs = [p.z for p in plist]
    if view == 'back':
        keep = [i for i, p in enumerate(plist) if p.mat not in BACK_HIDE_MATS]
        plist = [plist[i] for i in keep]
        # what was behind the Morph (tail, far wing, back fins) is now nearest the camera
        zs = [(50 - p.z) if p.z < 0 else p.z for p in plist]
    order = sorted(range(len(plist)), key=lambda i: zs[i])
    L = LIGHT.copy()
    if view == 'back':
        L[0] = -L[0]      # the sprite is mirrored afterwards, so light still comes from the top-left
    for idx in order:
        p = plist[idx]
        m, nx, ny, nz = raster(p, S, k)
        if not m.any():
            continue
        d = (nx * L[0] + ny * L[1] + nz * L[2])
        v = np.clip(d * 0.56 + 0.5, 0, 1)
        # rim light on the side away from the lamp: makes round forms read as 3D
        rim = np.clip(1 - nz, 0, 1) ** 1.6 * np.clip(-(nx * L[0] + ny * L[1]), 0, 1)
        v = np.clip(v + rim * 0.34, 0, 1)
        # specular highlight (view vector = +z)
        rz = 2 * d * nz - L[2]
        spec = np.clip(rz, 0, 1) ** 18 * GLOSS.get(p.mat, 0.85)
        thr = BAYER4[Ys % 4, Xs % 4]
        q = np.clip(np.floor(v * 6.0 + (thr - 0.5) * 0.6), 0, NL).astype(int)
        mm = m & (zs[idx] >= zbuf)
        owner[mm] = idx
        zbuf[mm] = zs[idx]
        shade_idx[mm] = q[mm]
        spec_map[mm] = spec[mm]
        matname[mm] = p.mat
    # cast shadows: a part throws a soft shadow down-and-away from the light onto parts behind it
    off = max(1, int(round(2.4 * k)))
    ox = off if L[0] < 0 else -off
    oy = off
    src_owner = owner.copy()
    for y in range(S):
        yy = y - oy
        if yy < 0:
            continue
        for x in range(S):
            o = src_owner[y, x]
            if o < 0:
                continue
            xx = x - ox
            if not (0 <= xx < S):
                continue
            o2 = src_owner[yy, xx]
            if o2 >= 0 and o2 != o and zs[o2] > zs[o] + 0.2 and plist[o].mat != 'flame':
                shade_idx[y, x] = max(0, shade_idx[y, x] - 2)
                spec_map[y, x] = 0
    # paint
    for y in range(S):
        for x in range(S):
            if owner[y, x] < 0:
                continue
            mn = matname[y, x]
            r = ramps.get(mn) or ramps['body']
            c = r[shade_idx[y, x]]
            if spec_map[y, x] > 0.5:
                c = shift(r[NL], 0.1, -0.05, 0)
            elif spec_map[y, x] > 0.2 and shade_idx[y, x] < NL:
                c = r[min(NL, shade_idx[y, x] + 1)]
            out.a[y, x] = (*c, 255)
    # inner edges: darken pixels of a front part that border a part behind it
    if outline:
        for y in range(S):
            for x in range(S):
                o = owner[y, x]
                if o < 0:
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    xx, yy = x + dx, y + dy
                    if 0 <= xx < S and 0 <= yy < S:
                        o2 = owner[yy, xx]
                        if o2 >= 0 and o2 != o and zs[o2] < zs[o] and matname[yy, xx] != matname[y, x] or \
                           (o2 >= 0 and o2 != o and zs[o2] < zs[o] - 0.5):
                            r = ramps.get(matname[y, x]) or ramps['body']
                            out.a[y, x] = (*r[max(0, shade_idx[y, x] - 2)], 255)
                            break
    # face details (front only)
    if view == 'front':
        eyes = [p for p in parts if p.kind == 'eye']
        mid = sum(e.kw['x'] for e in eyes) / len(eyes) if eyes else 48
        for p in parts:
            if p.kind == 'eye':
                _eye(out, p, k)
                if female:
                    _lashes(out, p, k, -1 if p.kw['x'] <= mid else 1)
            elif p.kind == 'mouth':
                _mouth(out, p, k)
    if outline:
        _outer_outline(out, owner, matname, ramps)
    if shadow:
        _ground_shadow(out, k)
    if view == 'back':
        out = out.flip()
    return out


def _lashes(out, p, k, side):
    """Female form: two little eyelashes at the outer top of each eye."""
    kw = p.kw
    if kw['style'] == 'sleepy':
        return
    cx, cy, r = kw['x'] * k, kw['y'] * k, max(1.2, kw['r'] * k)
    dark = hx(kw['col'])
    pts = [(cx + side * r * 0.55, cy - r * 1.05), (cx + side * r * 1.0, cy - r * 0.75)]
    if r >= 2.5:
        pts += [(cx + side * r * 0.85, cy - r * 1.35), (cx + side * r * 1.35, cy - r * 0.95)]
    for x, y in pts:
        xi, yi = int(round(x)), int(round(y))
        if 0 <= xi < out.w and 0 <= yi < out.h:
            out.px(xi, yi, dark)


def _ground_shadow(out, k):
    """Soft oval shadow on the ground under the Morph (drawn only where the sprite is empty)."""
    S = out.w
    alpha = out.a[:, :, 3] > 0
    cols = np.where(alpha.any(axis=0))[0]
    rows = np.where(alpha.any(axis=1))[0]
    if not len(cols):
        return
    bottom = rows[-1]
    # width of the bottom part of the body
    band = alpha[max(0, bottom - int(10 * k)):bottom + 1]
    bc = np.where(band.any(axis=0))[0]
    x0, x1 = (bc[0], bc[-1]) if len(bc) else (cols[0], cols[-1])
    cx = (x0 + x1) / 2
    rx = max(6 * k, (x1 - x0) / 2 + 3 * k)
    gy = min(S - 2, 90 * k)
    ry = max(2, 3.2 * k)
    for y in range(int(gy - ry - 1), int(gy + ry + 2)):
        for x in range(int(cx - rx - 1), int(cx + rx + 2)):
            if not (0 <= x < S and 0 <= y < S) or alpha[y, x]:
                continue
            dd = ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - gy) / ry) ** 2
            if dd <= 1:
                a = 150 if dd < 0.45 else 95
                out.a[y, x] = (22, 20, 40, a)


def _eye(out, p, k):
    kw = p.kw
    cx, cy, r = kw['x'] * k, kw['y'] * k, max(1.2, kw['r'] * k)
    style = kw['style']
    dark = hx(kw['col'])
    S = out.w
    for y in range(max(0, int(cy - r - 2)), min(S, int(cy + r + 3))):
        for x in range(max(0, int(cx - r - 2)), min(S, int(cx + r + 3))):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            if style == 'sleepy':
                if abs(dy) < max(0.6, r * 0.25) and abs(dx) < r:
                    out.px(x, y, dark)
                continue
            if style == 'fierce':
                # slanted top
                if dx * dx / (r * r) + dy * dy / (r * r * 0.7) <= 1 and dy > -r * 0.35 + dx * 0.35 * (1 if kw.get('look', 0) >= 0 else -1):
                    out.px(x, y, dark)
                continue
            if dx * dx + dy * dy <= r * r:
                out.px(x, y, dark)
                if kw.get('iris') and dx * dx + dy * dy <= (r * 0.62) ** 2:
                    out.px(x, y, hx(kw['iris']))
    # highlight
    if style not in ('sleepy',) and r >= 1.5:
        hx_, hy_ = int(cx - r * 0.35), int(cy - r * 0.4)
        out.px(hx_, hy_, (255, 255, 255))
        if r >= 3:
            out.px(hx_ + 1, hy_, (255, 255, 255)); out.px(hx_, hy_ + 1, (255, 255, 255))
            out.px(int(cx + r * 0.35), int(cy + r * 0.35), (220, 230, 255))


def _mouth(out, p, k):
    kw = p.kw
    x, y, w = kw['x'] * k, kw['y'] * k, max(2, kw['w'] * k)
    col = hx(kw['col'])
    style = kw['style']
    if style == 'smile':
        for i in range(int(w)):
            t = (i / max(1, w - 1)) * 2 - 1
            out.px(int(x - w / 2 + i), int(y + (1 - t * t) * max(1, w * 0.18)), col)
    elif style == 'fang':
        for i in range(int(w)):
            out.px(int(x - w / 2 + i), int(y), col)
        out.px(int(x - w / 2 + 1), int(y + 1), (250, 250, 250)); out.px(int(x + w / 2 - 2), int(y + 1), (250, 250, 250))
    elif style == 'open':
        for yy in range(int(max(2, w * 0.6))):
            for i in range(int(w)):
                t = (i / max(1, w - 1)) * 2 - 1
                if yy <= (1 - t * t) * w * 0.6:
                    out.px(int(x - w / 2 + i), int(y + yy), col if yy < 1 or abs(t) > 0.7 else (200, 70, 90))
    elif style == 'line':
        for i in range(int(w)):
            out.px(int(x - w / 2 + i), int(y), col)
    elif style == 'beak':
        pass


def _outer_outline(out, owner, matname, ramps):
    S = out.w
    a = out.a.copy()
    op = a[:, :, 3] > 0
    for y in range(S):
        for x in range(S):
            if op[y, x]:
                continue
            best = None
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                xx, yy = x + dx, y + dy
                if 0 <= xx < S and 0 <= yy < S and op[yy, xx]:
                    best = (xx, yy)
                    break
            if best:
                mn = matname[best[1], best[0]] or 'body'
                r = ramps.get(mn) or ramps['body']
                c = shift(r[0], -0.12, 0.05, 10)
                out.a[y, x] = (*c, 255)
