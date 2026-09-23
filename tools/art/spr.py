"""Tiny RGBA sprite canvas with pixel-art helpers (numpy backed)."""
import numpy as np
from PIL import Image
from pal import hx, shift, BAYER4


def C(c, a=255):
    if isinstance(c, str):
        c = hx(c)
    return (int(c[0]), int(c[1]), int(c[2]), int(c[3]) if len(c) > 3 else a)


class Spr:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.a = np.zeros((h, w, 4), dtype=np.uint8)

    # ── primitives ──
    def px(self, x, y, c, a=255):
        x, y = int(x), int(y)
        if 0 <= x < self.w and 0 <= y < self.h:
            self.a[y, x] = C(c, a)

    def get(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            return self.a[y, x]
        return np.array([0, 0, 0, 0], dtype=np.uint8)

    def opaque(self, x, y):
        return 0 <= x < self.w and 0 <= y < self.h and self.a[y, x, 3] > 0

    def rect(self, x, y, w, h, c, a=255):
        x0, y0 = max(0, int(x)), max(0, int(y))
        x1, y1 = min(self.w, int(x + w)), min(self.h, int(y + h))
        if x1 > x0 and y1 > y0:
            self.a[y0:y1, x0:x1] = C(c, a)

    def hline(self, x0, x1, y, c):
        for x in range(int(x0), int(x1) + 1):
            self.px(x, y, c)

    def vline(self, x, y0, y1, c):
        for y in range(int(y0), int(y1) + 1):
            self.px(x, y, c)

    def line(self, x0, y0, x1, y1, c):
        x0, y0, x1, y1 = int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1))
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx + dy
        while True:
            self.px(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy; x0 += sx
            if e2 <= dx:
                err += dx; y0 += sy

    def ellipse(self, cx, cy, rx, ry, c, a=255):
        ys, xs = np.mgrid[0:self.h, 0:self.w]
        m = ((xs + 0.5 - cx) / max(rx, 0.1)) ** 2 + ((ys + 0.5 - cy) / max(ry, 0.1)) ** 2 <= 1.0
        self.a[m] = C(c, a)
        return m

    def shaded_ellipse(self, cx, cy, rx, ry, ramp, light=(-0.55, -0.7), bias=0.0, dither=True, mask_only=None):
        """Fill an ellipse with sphere-like shading quantised onto `ramp` (dark→light)."""
        ys, xs = np.mgrid[0:self.h, 0:self.w]
        nx = (xs + 0.5 - cx) / max(rx, 0.1)
        ny = (ys + 0.5 - cy) / max(ry, 0.1)
        r2 = nx * nx + ny * ny
        m = r2 <= 1.0
        if mask_only is not None:
            m &= mask_only
        nz = np.sqrt(np.clip(1 - r2, 0, 1))
        lx, ly = light
        lz = 0.6
        ln = np.sqrt(lx * lx + ly * ly + lz * lz)
        d = (nx * lx + ny * ly + nz * lz) / ln
        v = np.clip(d * 0.5 + 0.5 + bias, 0, 1)
        n = len(ramp)
        if dither:
            thr = BAYER4[ys % 4, xs % 4]
            idx = np.clip(np.floor(v * (n - 1) + thr * 0.9), 0, n - 1).astype(int)
        else:
            idx = np.clip(np.round(v * (n - 1)), 0, n - 1).astype(int)
        cols = np.array([C(c) for c in ramp], dtype=np.uint8)
        self.a[m] = cols[idx[m]]
        return m

    def poly(self, pts, c):
        """Fill polygon (list of (x,y))."""
        ys, xs = np.mgrid[0:self.h, 0:self.w]
        X, Y = xs + 0.5, ys + 0.5
        inside = np.zeros((self.h, self.w), dtype=bool)
        n = len(pts)
        j = n - 1
        for i in range(n):
            xi, yi = pts[i]
            xj, yj = pts[j]
            cond = ((yi > Y) != (yj > Y)) & (X < (xj - xi) * (Y - yi) / ((yj - yi) + 1e-9) + xi)
            inside ^= cond
            j = i
        self.a[inside] = C(c)
        return inside

    def outline(self, color=None, darken=0.28, diag=False, only_outside=True):
        """Add a 1px outline around opaque pixels. If color is None use a darker
        version of the neighbouring pixel (selective outlining)."""
        a = self.a
        op = a[:, :, 3] == 255
        new = a.copy()
        offs = [(1, 0), (-1, 0), (0, 1), (0, -1)] + ([(1, 1), (-1, -1), (1, -1), (-1, 1)] if diag else [])
        for y in range(self.h):
            for x in range(self.w):
                if op[y, x]:
                    continue
                for dx, dy in offs:
                    xx, yy = x + dx, y + dy
                    if 0 <= xx < self.w and 0 <= yy < self.h and op[yy, xx]:
                        if color is None:
                            src = a[yy, xx]
                            c = shift(tuple(src[:3]), -darken, 0.05, 8)
                            new[y, x] = (*c, 255)
                        else:
                            new[y, x] = C(color)
                        break
        self.a = new

    def blit(self, other, x, y):
        """Alpha-composite `other` (Spr or ndarray) at x,y."""
        src = other.a if isinstance(other, Spr) else other
        h, w = src.shape[:2]
        x0, y0 = int(x), int(y)
        sx0, sy0 = max(0, -x0), max(0, -y0)
        dx0, dy0 = max(0, x0), max(0, y0)
        dx1, dy1 = min(self.w, x0 + w), min(self.h, y0 + h)
        if dx1 <= dx0 or dy1 <= dy0:
            return
        s = src[sy0:sy0 + (dy1 - dy0), sx0:sx0 + (dx1 - dx0)].astype(np.float32)
        d = self.a[dy0:dy1, dx0:dx1].astype(np.float32)
        sa = s[:, :, 3:4] / 255.0
        da = d[:, :, 3:4] / 255.0
        oa = sa + da * (1 - sa)
        rgb = np.where(oa > 0, (s[:, :, :3] * sa + d[:, :, :3] * da * (1 - sa)) / np.maximum(oa, 1e-6), 0)
        self.a[dy0:dy1, dx0:dx1, :3] = rgb.round().astype(np.uint8)
        self.a[dy0:dy1, dx0:dx1, 3] = (oa[:, :, 0] * 255).round().astype(np.uint8)

    def flip(self):
        s = Spr(self.w, self.h)
        s.a = self.a[:, ::-1].copy()
        return s

    def recolor(self, mapping):
        """mapping: {(r,g,b): (r,g,b)}"""
        out = Spr(self.w, self.h)
        out.a = self.a.copy()
        for src, dst in mapping.items():
            src = C(src); dst = C(dst)
            m = (self.a[:, :, 0] == src[0]) & (self.a[:, :, 1] == src[1]) & (self.a[:, :, 2] == src[2]) & (self.a[:, :, 3] > 0)
            out.a[m, :3] = dst[:3]
        return out

    def image(self):
        return Image.fromarray(self.a, 'RGBA')

    def save(self, path, scale=1):
        im = self.image()
        if scale != 1:
            im = im.resize((self.w * scale, self.h * scale), Image.NEAREST)
        im.save(path)


def from_ascii(rows, palette):
    """Build a sprite from ASCII art rows; palette maps chars→colour ('.' = clear)."""
    h = len(rows)
    w = max(len(r) for r in rows)
    s = Spr(w, h)
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in palette and palette[ch] is not None:
                s.px(x, y, palette[ch])
    return s
