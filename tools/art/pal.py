"""Palette + noise helpers shared by the Tiamat art generators."""
import colorsys
import numpy as np


def hx(h):
    if not isinstance(h, str):
        return tuple(int(v) for v in h[:3])
    h = h.lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def to_hex(c):
    return '#%02x%02x%02x' % tuple(int(v) for v in c[:3])


def clamp(v, a=0, b=255):
    return max(a, min(b, v))


def shift(rgb, dl=0.0, ds=0.0, dh=0.0):
    """Shift an rgb colour in HLS space. dh in degrees."""
    r, g, b = [c / 255 for c in rgb[:3]]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    h = (h + dh / 360.0) % 1.0
    l = min(1, max(0, l + dl))
    s = min(1, max(0, s + ds))
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return (round(r * 255), round(g * 255), round(b * 255))


def ramp(base, n=5, spread=0.13, hue=14, sat=0.04):
    """Hue-shifted ramp dark→light around a base colour.

    Shadows drift toward blue/purple, highlights toward yellow — the classic
    pixel-art lighting trick that keeps colours lively.
    """
    base = hx(base) if isinstance(base, str) else base
    mid = (n - 1) / 2
    out = []
    for i in range(n):
        k = (i - mid) / max(1, mid)            # -1 .. 1
        # hue: shadows rotate toward 230° (blue), lights toward 55° (yellow)
        r, g, b = [c / 255 for c in base]
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        hdeg = h * 360
        target = 55 if k > 0 else 235
        diff = ((target - hdeg + 540) % 360) - 180
        hdeg += max(-abs(hue * k), min(abs(hue * k), diff * abs(k)))
        l2 = min(0.97, max(0.04, l + spread * k * 1.6 if k < 0 else l + spread * k * 1.3))
        s2 = min(1, max(0, s + sat * (-k if k > 0 else abs(k) * 0.5)))
        r, g, b = colorsys.hls_to_rgb((hdeg % 360) / 360, l2, s2)
        out.append((round(r * 255), round(g * 255), round(b * 255)))
    return out


def h2(x, y, seed=0):
    """Deterministic integer hash → float in [0,1)."""
    n = (x * 374761393 + y * 668265263 + seed * 2147483647) & 0xFFFFFFFF
    n = (n ^ (n >> 13)) * 1274126177 & 0xFFFFFFFF
    n = n ^ (n >> 16)
    return (n & 0xFFFFFF) / float(0x1000000)


def hash_grid(w, h, seed=0):
    ys, xs = np.mgrid[0:h, 0:w]
    n = (xs.astype(np.uint64) * 374761393 + ys.astype(np.uint64) * 668265263 + np.uint64(seed * 2654435761 & 0xFFFFFFFF)) & np.uint64(0xFFFFFFFF)
    n = (n ^ (n >> np.uint64(13))) * np.uint64(1274126177) & np.uint64(0xFFFFFFFF)
    n = n ^ (n >> np.uint64(16))
    return (n & np.uint64(0xFFFFFF)).astype(np.float64) / float(0x1000000)


def periodic_noise(size=16, seed=0, octaves=((4, 0.6), (8, 0.3), (16, 0.1))):
    """Smooth value noise that tiles seamlessly on a size×size square."""
    out = np.zeros((size, size))
    for cells, amp in octaves:
        g = hash_grid(cells, cells, seed + cells * 31)
        ys, xs = np.mgrid[0:size, 0:size]
        fx = xs * cells / size
        fy = ys * cells / size
        x0 = np.floor(fx).astype(int) % cells
        y0 = np.floor(fy).astype(int) % cells
        x1 = (x0 + 1) % cells
        y1 = (y0 + 1) % cells
        tx = fx - np.floor(fx)
        ty = fy - np.floor(fy)
        tx = tx * tx * (3 - 2 * tx)
        ty = ty * ty * (3 - 2 * ty)
        a = g[y0, x0] * (1 - tx) + g[y0, x1] * tx
        b = g[y1, x0] * (1 - tx) + g[y1, x1] * tx
        out += amp * (a * (1 - ty) + b * ty)
    return out / sum(a for _, a in octaves)


BAYER4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0


def dither_pick(value, levels, x, y):
    """Map value in [0,1] to an index in range(levels) using 4×4 ordered dither."""
    v = value * (levels - 1)
    base = int(np.floor(v))
    frac = v - base
    if frac > BAYER4[y % 4, x % 4]:
        base += 1
    return max(0, min(levels - 1, base))
