"""Draws the Reach Map (public/assets/ui/regionmap.png, 400×240).

Town/route coordinates match src/data/region.js.
"""
import os, re, json
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
W, H = 400, 240


def hx(c):
    c = c.lstrip('#')
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def noise(seed, scale):
    rng = np.random.default_rng(seed)
    n = rng.random((H // scale + 3, W // scale + 3))
    n = ndimage.zoom(n, scale, order=3)[:H, :W]
    return (n - n.min()) / (n.max() - n.min() + 1e-9)


def points():
    src = open(os.path.join(ROOT, 'src', 'data', 'region.js'), encoding='utf-8').read()
    pts = {}
    for m in re.finditer(r"id: '(\w+)', (?:tier: \d+, )?name: '([^']+)', x: (\d+), y: (\d+)(, town: true)?", src):
        pts[m.group(1)] = (int(m.group(3)), int(m.group(4)), bool(m.group(5)))
    return pts


def main():
    yy, xx = np.mgrid[0:H, 0:W]
    n1 = noise(3, 24)
    n2 = noise(7, 8)
    # ── land mask: a blob covering the Reach, cut by the sea in the south and the Riven in the east
    land = np.zeros((H, W), bool)
    cx, cy = 200, 118
    d = ((xx - cx) / 196.0) ** 2 + ((yy - cy) / 120.0) ** 2
    land = d + (n1 - 0.5) * 0.35 + (n2 - 0.5) * 0.08 < 0.93
    # southern sea bay south of Saltreach / Route 3
    bay = (((xx - 175) / 120.0) ** 2 + ((yy - 250) / 40.0) ** 2) + (n2 - 0.5) * 0.25 < 1.0
    land &= ~bay
    # the Riven: a jagged chasm down the east
    riven_x = 366 + 6 * np.sin(yy / 13.0) + 4 * (n2 - 0.5) * 3
    riven = np.abs(xx - riven_x) < 3.5 + 1.5 * np.sin(yy / 7.0 + 1)
    img = np.zeros((H, W, 3), np.float32)
    # ocean
    deep, shallow = np.array(hx('#1d3f7c'), np.float32), np.array(hx('#3574c4'), np.float32)
    dist_land = ndimage.distance_transform_edt(~land)
    t = np.clip(dist_land / 22.0, 0, 1)[..., None]
    img[:] = shallow * (1 - t) + deep * t
    waves = ((xx + yy * 2) % 9 == 0) & (n2 > 0.55) & (dist_land > 4)
    img[waves] = img[waves] * 0.8 + np.array(hx('#9fd0f5')) * 0.2
    # biomes
    grass = np.array(hx('#6cb85a'), np.float32)
    img[land] = grass
    shade = (n1 - 0.5)[..., None] * 18
    img = np.where(land[..., None], img + shade, img)

    def blob(cx_, cy_, rx, ry, col, seed, thr=1.0):
        nn = noise(seed, 10)
        m = (((xx - cx_) / rx) ** 2 + ((yy - cy_) / ry) ** 2 + (nn - 0.5) * 0.6 < thr) & land
        img[m] = np.array(hx(col), np.float32) + (nn[m][:, None] - 0.5) * 20
        return m

    blob(150, 128, 32, 22, '#2f7a3c', 11)                    # Thornwild
    blob(50, 128, 26, 20, '#4a9a48', 12)                     # Brindlewood woods
    blob(256, 96, 40, 44, '#8f9454', 13)                     # moor
    blob(230, 170, 26, 16, '#9a7a5a', 14)                    # Coldforge hills
    snow = blob(200, 22, 170, 34, '#e6eef8', 15)             # northern snow
    blob(330, 60, 34, 34, '#6f6470', 16)                     # ash around Riftgate
    lake = (((xx - 204) / 30.0) ** 2 + ((yy - 66) / 14.0) ** 2 + (n2 - 0.5) * 0.4 < 1.0)
    img[lake] = np.array(hx('#4a8ad4'), np.float32)
    # mountains: little peaks on the snow
    rng = np.random.default_rng(5)
    for _ in range(60):
        px, py = int(rng.integers(40, 340)), int(rng.integers(6, 34))
        if not snow[py, px] or abs(px - 150) < 16 and abs(py - 40) < 10:
            continue
        for k in range(5):
            img[py + k, px - k:px + k + 1] = np.array(hx('#8a9ab8')) if k < 2 else np.array(hx('#b8c4dc'))
        img[py, px] = hx('#ffffff')
    # forest dots
    for _ in range(260):
        px, py = int(rng.integers(0, W)), int(rng.integers(0, H))
        if land[py, px] and (abs(px - 150) < 34 and abs(py - 128) < 22 or abs(px - 50) < 24 and abs(py - 128) < 18):
            img[py:py + 2, px:px + 2] = hx('#1f5a2c')
    # coast outline
    edge = land & ~ndimage.binary_erosion(land)
    img[edge] = hx('#e9d49b')
    edge2 = ~land & ndimage.binary_dilation(land) & ~lake
    img[edge2] = img[edge2] * 0.6 + np.array(hx('#9fd0f5')) * 0.4
    # the Riven
    img[riven & land] = hx('#0e0c14')
    rim = ndimage.binary_dilation(riven, iterations=1) & ~riven & land
    img[rim] = hx('#4a4460')
    glow = riven & ((yy % 11) < 2)
    img[glow & land] = hx('#6fe0c8')
    out = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), 'RGB').convert('RGBA')
    dr = ImageDraw.Draw(out)
    pts = points()
    order = ['rootmere', 'route1', 'brindlewood', 'route2', 'thornwild', 'saltreach', 'route3', 'coldforge', 'gearhollow',
             'route4', 'hollowmere', 'route5', 'frostspire', 'route6', 'riftgate', 'riven']
    path_col = (230, 200, 140, 255)
    for a, b in zip(order, order[1:]):
        if a not in pts or b not in pts:
            continue
        (x0, y0, _), (x1, y1, _) = pts[a], pts[b]
        # draw an L-shaped road
        dr.line([(x0, y0), (x0, y1), (x1, y1)], fill=(60, 40, 30, 255), width=4)
        dr.line([(x0, y0), (x0, y1), (x1, y1)], fill=path_col, width=2)
    for k, (x, y, town) in pts.items():
        if town:
            dr.rectangle([x - 4, y - 4, x + 4, y + 4], fill=(40, 34, 52, 255))
            dr.rectangle([x - 3, y - 3, x + 3, y + 3], fill=(250, 246, 236, 255))
            dr.rectangle([x - 1, y - 1, x + 1, y + 1], fill=(226, 85, 95, 255))
        else:
            dr.rectangle([x - 2, y - 2, x + 2, y + 2], fill=(40, 34, 52, 255))
            dr.rectangle([x - 1, y - 1, x + 1, y + 1], fill=(255, 214, 92, 255))
    # frame
    dr.rectangle([0, 0, W - 1, H - 1], outline=(40, 34, 52, 255), width=2)
    dr.rectangle([2, 2, W - 3, H - 3], outline=(233, 212, 155, 255), width=1)
    # compass
    cx, cy = 26, 26
    dr.polygon([(cx, cy - 12), (cx + 4, cy), (cx, cy + 12), (cx - 4, cy)], fill=(250, 246, 236, 255), outline=(40, 34, 52, 255))
    dr.polygon([(cx, cy - 12), (cx + 4, cy), (cx - 4, cy)], fill=(226, 85, 95, 255))
    os.makedirs(os.path.join(ROOT, 'public', 'assets', 'ui'), exist_ok=True)
    out.save(os.path.join(ROOT, 'public', 'assets', 'ui', 'regionmap.png'))
    print('regionmap.png written')


if __name__ == '__main__':
    main()
