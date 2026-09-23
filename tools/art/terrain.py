"""Ground-terrain rendering for Tiamat maps.

A map's ground layer is rendered at pixel level for the whole map, then sliced
into 16×16 tiles and de-duplicated by the map builder. Textures are tile-periodic
so identical neighbourhoods produce identical tiles.

Terrains carry an elevation: higher terrain overhangs lower terrain with a soft,
rounded lip (grass over paths, land over water) — computed with distance fields
so every corner case (the classic 47-tile blob set) is handled automatically.
"""
import numpy as np
from scipy import ndimage
import zlib
from pal import hx, ramp, periodic_noise, hash_grid, shift


def sh(v):
    return zlib.crc32(repr(v).encode()) & 0xFFFF

T = 16

TERRAINS = {
    # id: (elevation, description)
    'grass':  2,
    'forest': 2,
    'moor':   2,
    'snow':   2,
    'path':   1,
    'sand':   1,
    'cobble': 1,
    'cave':   1,
    'plank':  1,
    'ash':    1,
    'water':  0,
}
TID = {name: i for i, name in enumerate(TERRAINS)}
ELEV = np.array([TERRAINS[n] for n in TERRAINS])
NAMES = list(TERRAINS)

# Overhang margins (px) of a higher terrain into a lower one
MARGIN = {
    (2, 1): 2.2,
    (2, 0): 3.2,
    (1, 0): 3.0,
}

# ── Colour ramps ────────────────────────────────────────────────────────────
R = {
    'grass':  ramp('#5bab47', 5, 0.12),
    'forest': ramp('#3f8a44', 5, 0.11),
    'moor':   ramp('#8a9150', 5, 0.11, hue=18),
    'snow':   [hx('#9fb2d6'), hx('#c3d2ec'), hx('#e2ebf8'), hx('#f4f8ff'), hx('#ffffff')],
    'path':   ramp('#cfa46a', 5, 0.10),
    'sand':   ramp('#e9d49b', 5, 0.08),
    'cobble': ramp('#a9a092', 5, 0.12),
    'cave':   ramp('#7b6758', 5, 0.10),
    'plank':  ramp('#b07a48', 5, 0.12),
    'ash':    ramp('#6f6470', 5, 0.10),
    'water':  [hx('#1d3f7c'), hx('#2757a3'), hx('#3574c4'), hx('#5b9ae0'), hx('#9fd0f5')],
}
FOAM = hx('#e9f7ff')
SHALLOW = hx('#4d93d8')
DEEP = hx('#23498f')
BANK = {'grass': hx('#3d6b33'), 'forest': hx('#2c5a33'), 'moor': hx('#5d6036'), 'snow': hx('#8ea4cc'),
        'path': hx('#8c6a44'), 'sand': hx('#b89a62'), 'cobble': hx('#6f685f'), 'cave': hx('#4d3f36'),
        'plank': hx('#6d4526'), 'ash': hx('#463e49')}

NVAR = 4


def _tex(name, variant, frame=0):
    """Return a 16×16×3 uint8 texture tile for a terrain."""
    rng = hash_grid(T, T, seed=sh((name, variant)))
    n = periodic_noise(T, seed=(sh(name) & 0xFF) + variant * 7)
    r = R[name]
    img = np.zeros((T, T, 3), dtype=np.uint8)

    def put(x, y, c):
        img[y % T, x % T] = c

    if name in ('grass', 'forest', 'moor'):
        base_idx = np.where(n > 0.70, 3, np.where(n < 0.28, 1, 2))
        img[:] = np.array(r)[base_idx]
        # scattered blade tufts
        count = [3, 4, 2, 5][variant]
        for k in range(count):
            x = int(rng[k * 3 % T, k * 5 % T] * T)
            y = int(rng[(k * 7 + 3) % T, (k * 11 + 1) % T] * T)
            put(x, y, r[0]); put(x + 2, y, r[0]); put(x + 1, y + 1, r[1])
            put(x, y - 1, r[3]); put(x + 2, y - 1, r[3])
        if name == 'moor':
            for k in range(3 + variant):
                x = int(rng[(k * 5 + 2) % T, (k * 3) % T] * T)
                y = int(rng[(k * 3) % T, (k * 9 + 4) % T] * T)
                put(x, y, hx('#9a6aa8')); put(x + 1, y, hx('#b98ac4'))
        if variant == 2 and name == 'grass':
            for k in range(3):
                x = int(rng[k + 2, k * 4 % T] * T)
                y = int(rng[k * 4 % T, k + 5] * T)
                put(x, y, hx('#f4f1d8'))
        if variant == 3 and name != 'moor':
            x, y = 5 + int(rng[1, 1] * 6), 5 + int(rng[2, 2] * 6)
            put(x, y, r[4]); put(x + 1, y, r[3])
    elif name == 'snow':
        idx = np.where(n > 0.66, 3, np.where(n < 0.33, 1, 2))
        img[:] = np.array(r)[idx]
        for k in range(2 + variant):
            x = int(rng[k * 5 % T, k * 3 % T] * T)
            y = int(rng[k * 7 % T, (k * 2 + 1) % T] * T)
            put(x, y, r[4])
        for k in range(variant):
            x = int(rng[(k * 3 + 1) % T, k * 5 % T] * T)
            y = int(rng[k * 9 % T, (k * 4 + 2) % T] * T)
            put(x, y, r[1]); put(x + 1, y, r[1])
    elif name in ('path', 'sand', 'ash'):
        idx = np.where(n > 0.72, 3, np.where(n < 0.26, 1, 2))
        img[:] = np.array(r)[idx]
        for k in range(3 + variant):
            x = int(rng[k * 3 % T, k * 7 % T] * T)
            y = int(rng[(k * 5 + 2) % T, k * 3 % T] * T)
            put(x, y, r[0] if k % 2 else r[4])
            if name == 'path' and k % 3 == 0:
                put(x + 1, y, r[1]); put(x, y + 1, r[1]); put(x + 1, y - 1, r[4])
        if name == 'sand' and variant == 3:
            put(4, 10, hx('#f6e7c4')); put(5, 10, hx('#e0a58a')); put(6, 10, hx('#f6e7c4'))
    elif name == 'cobble':
        img[:] = r[1]
        # staggered stones 8×6
        for row in range(3):
            y0 = row * 6 - 1
            off = (row % 2) * 4 + variant % 2 * 2
            for col in range(3):
                x0 = col * 8 + off - 4
                shade = r[2] if (row + col + variant) % 3 else r[3]
                for yy in range(y0 + 1, y0 + 5):
                    for xx in range(x0 + 1, x0 + 7):
                        put(xx, yy, shade)
                for xx in range(x0 + 1, x0 + 7):
                    put(xx, y0 + 1, r[3] if shade == r[2] else r[4])
                    put(xx, y0 + 5, r[0])
    elif name == 'cave':
        idx = np.where(n > 0.6, 3, np.where(n < 0.4, 1, 2))
        img[:] = np.array(r)[idx]
        for k in range(2 + variant):
            x = int(rng[k * 3 % T, k * 7 % T] * T)
            y = int(rng[(k * 5 + 2) % T, k * 3 % T] * T)
            put(x, y, r[0]); put(x + 1, y, r[4])
        if variant == 1:
            for i in range(5):
                put(3 + i, 7 + (i % 2), r[0])
    elif name == 'plank':
        img[:] = r[2]
        for y in range(T):
            if y % 4 == 3:
                img[y, :] = r[0]
            elif y % 4 == 0:
                img[y, :] = r[3]
        for yb in range(4):
            xs = (yb * 5 + variant * 3) % T
            for y in range(yb * 4, yb * 4 + 3):
                put(xs, y, r[1])
    elif name == 'water':
        img[:] = r[2]
        ph = frame * 4
        for k in range(5):
            x = int(rng[k * 3 % T, k * 5 % T] * T)
            y = int(rng[(k * 7) % T, (k * 3 + 1) % T] * T)
            for i in range(3):
                put(x + i + ph // 2, y + (frame % 2), r[3])
            put(x + 1 + ph // 2, y - 1 + (frame % 2), r[4]) if k % 2 == 0 else None
        for k in range(2):
            x = int(rng[(k + 9) % T, (k * 2) % T] * T)
            y = int(rng[(k * 4 + 6) % T, (k + 3) % T] * T)
            put(x - ph // 4, y, r[1]); put(x + 1 - ph // 4, y, r[1])
    return img


_TEX_CACHE = {}


def tex(name, variant, frame=0):
    key = (name, variant, frame if name == 'water' else 0)
    if key not in _TEX_CACHE:
        _TEX_CACHE[key] = _tex(name, variant, key[2])
    return _TEX_CACHE[key]


def _level_mask(cell_level, lx, ly, xs, ys, margin, noise, sigma=1.8):
    """Grow a cell-level boolean mask by `margin` px, round its corners and
    roughen the edge with tile-periodic noise."""
    inside = cell_level[ys // T, xs // T]
    if inside.all() or not inside.any():
        return inside
    d_out = ndimage.distance_transform_edt(~inside)
    grown = (d_out < margin).astype(np.float32)
    soft = ndimage.gaussian_filter(grown, sigma)
    return soft > (0.5 + (noise[ly, lx] - 0.5) * 0.55)


def render_ground(cells, frames=1):
    """cells: 2-D list of terrain names. Returns (frames, water_mask)."""
    h, w = len(cells), len(cells[0])
    ids = np.array([[TID[c] for c in row] for row in cells], dtype=np.int16)
    cell_elev = ELEV[ids]
    ys, xs = np.mgrid[0:h * T, 0:w * T]
    lx, ly = xs % T, ys % T
    n1 = periodic_noise(T, seed=41)
    n2 = periodic_noise(T, seed=77)
    m1 = _level_mask(cell_elev >= 1, lx, ly, xs, ys, MARGIN[(1, 0)], n1)
    m2 = _level_mask(cell_elev >= 2, lx, ly, xs, ys, MARGIN[(2, 1)], n2) & m1
    E = np.where(m2, 2, np.where(m1, 1, 0))
    # terrain per pixel = terrain of the nearest cell of that pixel's level,
    # sampled through a small wobble so same-level borders look organic
    jx = (periodic_noise(T, seed=11) * 6 - 3).round().astype(int)
    jy = (periodic_noise(T, seed=23) * 6 - 3).round().astype(int)
    sx = np.clip(xs + jx[ly, lx], 0, w * T - 1)
    sy = np.clip(ys + jy[ly, lx], 0, h * T - 1)
    P = np.zeros(E.shape, dtype=np.int16)
    jn = periodic_noise(T, seed=97, octaves=((8, 0.5), (16, 0.5)))[ly, lx]
    for lev in (0, 1, 2):
        cell_is = (cell_elev == lev)
        if not cell_is.any():
            continue
        pix_is = cell_is[ys // T, xs // T]
        _, (iy, ix) = ndimage.distance_transform_edt(~pix_is, return_indices=True)
        nearest = ids[iy // T, ix // T]
        present = [t for t in np.unique(ids[cell_is])]
        if len(present) == 1:
            choice = np.full(E.shape, present[0], dtype=np.int16)
        else:
            scores = []
            for t in present:
                ind = (ids == t)[ys // T, xs // T].astype(np.float32)
                sc = ndimage.gaussian_filter(ind, 2.4) + (nearest == t) * 0.02 + (jn - 0.5) * (0.9 if len(scores) % 2 == 0 else -0.9)
                scores.append(sc)
            scores = np.stack(scores)
            # noise tilts the decision near borders → organic, dithered edge
            choice = np.array(present, dtype=np.int16)[np.argmax(scores, axis=0)]
        P = np.where(E == lev, choice, P)
    # distance fields for shading
    d_to_higher = np.full(E.shape, 99.0)
    d_to_lower = np.full(E.shape, 99.0)
    for lev in (0, 1):
        hi = E > lev
        if hi.any() and (E == lev).any():
            d = ndimage.distance_transform_edt(~hi)
            d_to_higher = np.where(E == lev, d, d_to_higher)
    for lev in (1, 2):
        lo = E < lev
        if lo.any() and (E == lev).any():
            d = ndimage.distance_transform_edt(~lo)
            d_to_lower = np.where(E == lev, d, d_to_lower)
    water_px = E == 0
    d_to_water = ndimage.distance_transform_edt(~water_px) if water_px.any() else np.full(E.shape, 99.0)
    var = (hash_grid(w, h, seed=5) * NVAR).astype(int)
    V = var[ys // T, xs // T]
    out = []
    for f in range(frames):
        img = np.zeros((h * T, w * T, 3), dtype=np.uint8)
        for tid, name in enumerate(NAMES):
            mask = P == tid
            if not mask.any():
                continue
            for v in range(NVAR):
                mv = mask & (V == v)
                if mv.any():
                    t = tex(name, v, f)
                    img[mv] = t[ly[mv], lx[mv]]
        # lower land: soft shadow under the grass lip
        sh_ = (E == 1) & (d_to_higher < 1.5)
        for tid, name in enumerate(NAMES):
            m = sh_ & (P == tid)
            if m.any():
                img[m] = BANK[name]
        # higher land: darker 1px edge where it meets lower ground (not water)
        lip = (E == 2) & (d_to_lower < 1.2) & (d_to_water > 1.5)
        for tid, name in enumerate(NAMES):
            m = lip & (P == tid)
            if m.any():
                img[m] = R[name][1]
        if water_px.any():
            phase = (f / max(1, frames)) * 2 * np.pi
            wob = 0.45 * np.sin(phase + (lx * 0.9 + ly * 0.6))
            dist = d_to_higher
            foam = water_px & (dist < 1.3 + wob)
            shallow = water_px & ~foam & (dist < 3.6 + wob * 0.5)
            img[shallow] = np.clip(img[shallow].astype(int) + (np.array(SHALLOW) - np.array(R['water'][2])), 0, 255)
            img[foam] = FOAM
            bank = (~water_px) & (d_to_water < 1.4)
            for tid, name in enumerate(NAMES):
                m = bank & (P == tid)
                if m.any() and name in BANK:
                    img[m] = BANK[name]
        out.append(img)
    return out, water_px
