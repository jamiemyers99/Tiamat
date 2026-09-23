"""Battle backdrops (480×270) with baked platforms. public/assets/battle/<id>.png"""
import os, sys, json, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
import numpy as np
from PIL import Image
from pal import hx, ramp, shift, BAYER4, periodic_noise, hash_grid

W, H = 480, 270
EP = (348, 138, 78, 17)     # enemy platform cx, cy, rx, ry
PP = (128, 236, 104, 22)    # player platform

THEMES = {
    'meadow': dict(sky=('#7ec8f0', '#d8f0ff'), far='#8ec6a0', mid='#5aa860', ground='#6cbc54', plat='#4f9a40', rim='#88d06a', deco='hills'),
    'forest': dict(sky=('#5a9ab8', '#b8e0d0'), far='#3a7a5a', mid='#2f6a44', ground='#4a8a3c', plat='#356e2e', rim='#6aaa4a', deco='trees'),
    'coast': dict(sky=('#78c0f0', '#f0f8ff'), far='#4a9ad8', mid='#3a84c8', ground='#e8d49b', plat='#cdb47a', rim='#fff0c0', deco='sea'),
    'cave': dict(sky=('#2a2230', '#4a3a48'), far='#3a3040', mid='#4a3c44', ground='#6d5a4e', plat='#56463c', rim='#8a7462', deco='cave'),
    'moor': dict(sky=('#8a92a8', '#d8d4dc'), far='#7a7a78', mid='#6a7050', ground='#8a9150', plat='#6a7040', rim='#a8b068', deco='stones'),
    'snow': dict(sky=('#a8c0e0', '#f0f6ff'), far='#c8d8f0', mid='#a8bcd8', ground='#e8f0f8', plat='#c8d6ec', rim='#ffffff', deco='peaks'),
    'town': dict(sky=('#88c8f0', '#e8f6ff'), far='#b8a890', mid='#9a8a74', ground='#a9a092', plat='#8a8276', rim='#c8c0b0', deco='roofs'),
    'arena': dict(sky=('#3a3a58', '#5a5a80'), far='#4a4a6a', mid='#5a5470', ground='#b8a88a', plat='#9a8a70', rim='#e8d8b0', deco='arena'),
    'rift': dict(sky=('#1a1238', '#4a2a78'), far='#2a1e50', mid='#3a2a68', ground='#3a2e58', plat='#2a2048', rim='#8a6ae0', deco='rift'),
    'night': dict(sky=('#101838', '#2a3a6a'), far='#1e2a4a', mid='#24344a', ground='#2e4a3a', plat='#223a2c', rim='#4a6a4a', deco='hills'),
    'water': dict(sky=('#78c0f0', '#e8f6ff'), far='#4a9ad8', mid='#3a84c8', ground='#3a7ac8', plat='#2a5aa8', rim='#9fd0f5', deco='sea'),
    'chapel': dict(sky=('#141026', '#2a2044'), far='#241c3a', mid='#2e2448', ground='#4a4660', plat='#3a3650', rim='#6fe0c8', deco='arena'),
}


def grad(img, y0, y1, c0, c1):
    c0, c1 = np.array(hx(c0)), np.array(hx(c1))
    for y in range(y0, y1):
        t = (y - y0) / max(1, y1 - y0 - 1)
        for x in range(W):
            tt = t + (BAYER4[y % 4, x % 4] - 0.5) * 0.12
            tt = min(1, max(0, tt))
            q = round(tt * 6) / 6
            img[y, x] = c0 + (c1 - c0) * q


def ellipse(img, cx, cy, rx, ry, col, alpha=1.0):
    ys, xs = np.mgrid[0:H, 0:W]
    m = ((xs + 0.5 - cx) / rx) ** 2 + ((ys + 0.5 - cy) / ry) ** 2 <= 1
    c = np.array(hx(col) if isinstance(col, str) else col)
    img[m] = img[m] * (1 - alpha) + c * alpha
    return m


def ridge(img, base_y, amp, freq, col, seed, top=None):
    rng = np.random.RandomState(seed)
    ph = rng.rand(3) * 10
    c = np.array(hx(col))
    for x in range(W):
        y = base_y - amp * (0.5 + 0.3 * math.sin(x * freq + ph[0]) + 0.2 * math.sin(x * freq * 2.7 + ph[1]) + 0.1 * math.sin(x * freq * 6.1 + ph[2]))
        yi = int(y)
        img[yi:, x] = c
        if top:
            img[yi:yi + 1, x] = np.array(hx(top))


def platform(img, cx, cy, rx, ry, col, rim):
    base = ramp(col, 5, 0.1)
    ellipse(img, cx, cy + 4, rx, ry, base[0])
    ellipse(img, cx, cy, rx, ry, base[2])
    ellipse(img, cx - rx * 0.12, cy - ry * 0.18, rx * 0.78, ry * 0.62, base[3])
    # rim highlight
    ys, xs = np.mgrid[0:H, 0:W]
    d = ((xs + 0.5 - cx) / rx) ** 2 + ((ys + 0.5 - cy) / ry) ** 2
    m = (d <= 1) & (d > 0.86) & (ys < cy)
    img[m] = np.array(hx(rim))


def build(tid, t):
    img = np.zeros((H, W, 3), dtype=np.float64)
    horizon = 150
    grad(img, 0, horizon, t['sky'][0], t['sky'][1])
    deco = t['deco']
    if deco in ('hills', 'meadow'):
        for i in range(5):
            cx, cy = 40 + i * 110, 40 + (i % 2) * 18
            for dx in (-14, 0, 14):
                ellipse(img, cx + dx, cy + (abs(dx) // 3), 16, 8, '#ffffff', 0.85)
        ridge(img, horizon - 4, 34, 0.012, t['far'], 1)
        ridge(img, horizon + 6, 20, 0.02, t['mid'], 2, top=shift(hx(t['mid']), 0.08))
    elif deco == 'trees':
        ridge(img, horizon - 10, 20, 0.02, t['far'], 3)
        rng = np.random.RandomState(4)
        for i in range(26):
            x = int(rng.rand() * W); h = 40 + int(rng.rand() * 50)
            ellipse(img, x, horizon - h * 0.5, 16, h * 0.5, t['mid'])
            ellipse(img, x - 4, horizon - h * 0.62, 10, h * 0.3, shift(hx(t['mid']), 0.07))
    elif deco == 'sea':
        img[horizon - 30:horizon + 20] = np.array(hx(t['far']))
        for y in range(horizon - 30, horizon + 20, 5):
            for x in range(0, W, 23):
                img[y, (x + y * 7) % W:(x + y * 7) % W + 8] = np.array(hx('#9fd0f5'))
        for i in range(4):
            ellipse(img, 60 + i * 120, 34 + (i % 2) * 12, 18, 7, '#ffffff', 0.9)
    elif deco == 'cave':
        rng = np.random.RandomState(7)
        for i in range(18):
            x = int(rng.rand() * W); h = 20 + int(rng.rand() * 50)
            pts = np.array([[x - 10, 0], [x + 10, 0], [x, h]])
            ys, xs = np.mgrid[0:H, 0:W]
            m = (ys < h) & (np.abs(xs - x) < (10 * (1 - ys / h)))
            img[m] = np.array(hx(t['far']))
        ridge(img, horizon + 10, 30, 0.03, t['mid'], 8)
    elif deco == 'stones':
        ridge(img, horizon - 6, 22, 0.01, t['far'], 9)
        for i, x in enumerate([60, 130, 380, 440]):
            h = 34 + (i % 2) * 10
            ys, xs = np.mgrid[0:H, 0:W]
            m = (ys > horizon - h) & (ys < horizon + 4) & (np.abs(xs - x) < 7 - (ys < horizon - h + 6) * 2)
            img[m] = np.array(hx('#8b8a96'))
        ridge(img, horizon + 8, 12, 0.03, t['mid'], 10)
    elif deco == 'peaks':
        for i, (x, h) in enumerate([(60, 90), (170, 120), (300, 100), (420, 130)]):
            ys, xs = np.mgrid[0:H, 0:W]
            m = (ys > horizon - h) & (ys < horizon) & (np.abs(xs - x) < (ys - (horizon - h)) * 0.9)
            img[m] = np.array(hx(t['mid']))
            m2 = m & (ys < horizon - h + h * 0.3)
            img[m2] = np.array(hx('#ffffff'))
        ridge(img, horizon + 6, 10, 0.03, t['far'], 11)
    elif deco == 'roofs':
        ridge(img, horizon - 6, 20, 0.01, '#9ac8a0', 12)
        for i in range(8):
            x0 = i * 64 + 6
            h = 30 + (i % 3) * 12
            img[horizon - h:horizon, x0:x0 + 50] = np.array(hx(t['far']))
            for y in range(horizon - h - 12, horizon - h):
                k = (y - (horizon - h - 12)) / 12
                img[y, int(x0 + 25 - 30 * k):int(x0 + 25 + 30 * k)] = np.array(hx(['#c8473f', '#3f6fc8', '#4a9a52'][i % 3]))
    elif deco == 'arena':
        img[:horizon] = img[:horizon] * 0.8
        for x in range(20, W, 60):
            img[30:horizon, x:x + 14] = np.array(hx(t['mid']))
            img[30:34, x - 3:x + 17] = np.array(hx(shift(hx(t['mid']), 0.1)))
        img[horizon - 8:horizon, :] = np.array(hx(t['far']))
    elif deco == 'rift':
        rng = np.random.RandomState(13)
        for i in range(60):
            x, y = int(rng.rand() * W), int(rng.rand() * horizon)
            img[y, x] = np.array(hx('#e8d8ff'))
        for i, x in enumerate([50, 150, 330, 430]):
            h = 50 + (i % 2) * 40
            ys, xs = np.mgrid[0:H, 0:W]
            m = (ys > horizon - h) & (ys < horizon) & (np.abs(xs - x) < 5 + (ys - (horizon - h)) * 0.12)
            img[m] = np.array(hx('#7a5ce0'))
        ridge(img, horizon + 4, 20, 0.02, t['mid'], 14, top='#8a6ae0')
    # ground
    g = ramp(t['ground'], 5, 0.07)
    for y in range(horizon, H):
        for x in range(W):
            k = (y - horizon) / (H - horizon)
            idx = 2 if k > 0.3 else 3
            if (x * 7 + y * 13) % 29 == 0:
                idx = 1
            img[y, x] = np.array(g[idx])
    if deco in ('sea',) and tid == 'water':
        for y in range(horizon, H, 6):
            for x in range(0, W, 31):
                img[y, (x + y * 5) % W:(x + y * 5) % W + 10] = np.array(hx('#9fd0f5'))
    platform(img, *EP, t['plat'], t['rim'])
    platform(img, *PP, t['plat'], t['rim'])
    return Image.fromarray(img.clip(0, 255).astype(np.uint8), 'RGB')


def main():
    out = os.path.join(ROOT, 'public', 'assets', 'battle')
    os.makedirs(out, exist_ok=True)
    for tid, t in THEMES.items():
        build(tid, t).save(os.path.join(out, f'{tid}.png'), optimize=True)
    with open(os.path.join(out, 'index.json'), 'w') as f:
        json.dump({'themes': list(THEMES), 'enemy': EP, 'player': PP}, f)
    print('battle backdrops:', len(THEMES))


if __name__ == '__main__':
    main()
