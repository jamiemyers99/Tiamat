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


def render(parts, mats, S=96, view='front', shiny=False, outline=True):
    """mats: name -> base colour hex. Returns Spr of size S×S."""
    k = S / 96.0
    ramps = {}
    for name, col in mats.items():
        c = hx(col)
        if shiny:
            c = shift(c, 0.02, 0.05, SHINY_ROT.get(name, 150))
        ramps[name] = ramp(c, 6, 0.16, hue=16, sat=0.05)
    out = Spr(S, S)
    owner = np.full((S, S), -1, dtype=int)
    zbuf = np.full((S, S), -1e9)
    shade_idx = np.zeros((S, S), dtype=int)
    matname = np.full((S, S), '', dtype=object)
    Xs, Ys = np.mgrid[0:S, 0:S][1], np.mgrid[0:S, 0:S][0]
    plist = [p for p in parts if p.view in ('both', view) and p.kind not in ('eye', 'mouth')]
    if view == 'back':
        plist = [p for p in plist if p.mat not in FRONT_ONLY_MATS]
    order = sorted(range(len(plist)), key=lambda i: plist[i].z)
    for idx in order:
        p = plist[idx]
        m, nx, ny, nz = raster(p, S, k)
        if not m.any():
            continue
        L = LIGHT.copy()
        if view == 'back':
            L[0] = -L[0]
        d = (nx * L[0] + ny * L[1] + nz * L[2])
        v = np.clip(d * 0.55 + 0.52, 0, 1)
        thr = BAYER4[Ys % 4, Xs % 4]
        q = np.clip(np.floor(v * 5.0 + (thr - 0.5) * 0.55), 0, 5).astype(int)
        mm = m & (p.z >= zbuf)
        owner[mm] = idx
        zbuf[mm] = p.z
        shade_idx[mm] = q[mm]
        matname[mm] = p.mat
    # paint
    for y in range(S):
        for x in range(S):
            if owner[y, x] < 0:
                continue
            mn = matname[y, x]
            r = ramps.get(mn) or ramps['body']
            out.a[y, x] = (*r[shade_idx[y, x]], 255)
    # inner edges: darken pixels of a front part that border a part behind it
    if outline:
        src = out.a.copy()
        for y in range(S):
            for x in range(S):
                o = owner[y, x]
                if o < 0:
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    xx, yy = x + dx, y + dy
                    if 0 <= xx < S and 0 <= yy < S:
                        o2 = owner[yy, xx]
                        if o2 >= 0 and o2 != o and plist[o2].z < plist[o].z and matname[yy, xx] != matname[y, x] or \
                           (o2 >= 0 and o2 != o and plist[o2].z < plist[o].z - 0.5):
                            r = ramps.get(matname[y, x]) or ramps['body']
                            out.a[y, x] = (*r[max(0, shade_idx[y, x] - 2)], 255)
                            break
    # face details (front only)
    if view == 'front':
        for p in parts:
            if p.kind == 'eye':
                _eye(out, p, k)
            elif p.kind == 'mouth':
                _mouth(out, p, k)
    if outline:
        _outer_outline(out, owner, matname, ramps)
    if view == 'back':
        out = out.flip()
    return out


SHINY_ROT = {}
FRONT_ONLY_MATS = ('belly', 'blush', 'nose', 'inner', 'muzzle', 'face')


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
