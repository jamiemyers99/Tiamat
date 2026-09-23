"""App icons for the installable web app (home-screen icon, favicon, maskable icon)."""
import os, json
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.join(ROOT, 'public', 'icons')


def tiamat():
    atlas = json.load(open(os.path.join(ROOT, 'public/assets/sprites/mons.json')))['frames']['tiamat_f']['frame']
    sheet = Image.open(os.path.join(ROOT, 'public/assets/sprites/mons.png')).convert('RGBA')
    im = sheet.crop((atlas['x'], atlas['y'], atlas['x'] + atlas['w'], atlas['y'] + atlas['h']))
    return im.crop(im.getbbox())


def icon(size, safe=1.0):
    S = 128                                   # draw at pixel-art scale, then upscale crisply
    img = Image.new('RGBA', (S, S))
    d = ImageDraw.Draw(img)
    for y in range(S):                        # night-sky gradient
        t = y / (S - 1)
        c = tuple(int(a + (b - a) * t) for a, b in zip((20, 18, 44), (44, 36, 96)))
        d.line([(0, y), (S, y)], fill=c + (255,))
    for (x, y) in [(14, 12), (30, 26), (96, 18), (110, 40), (20, 44), (70, 10), (52, 30)]:
        img.putpixel((x, y), (230, 230, 255, 255))
    d.ellipse([84, 12, 112, 40], fill=(244, 236, 208, 255))
    d.ellipse([90, 8, 116, 34], fill=(40, 34, 84, 150))
    for y in range(96, S):                    # sea
        t = (y - 96) / 32
        d.line([(0, y), (S, y)], fill=(int(28 + 20 * t), int(44 + 30 * t), int(110 + 30 * t), 255))
    for i, y in enumerate(range(100, S, 6)):
        for x in range((i * 7) % 13, S, 13):
            d.line([(x, y), (x + 5, y)], fill=(110, 150, 230, 255))
    t = tiamat()
    k = safe * 104 / max(t.size)
    t = t.resize((max(1, int(t.width * k)), max(1, int(t.height * k))), Image.NEAREST)
    img.alpha_composite(t, ((S - t.width) // 2, 112 - t.height))
    return img.resize((size, size), Image.NEAREST)


def main():
    os.makedirs(OUT, exist_ok=True)
    for s in (192, 512):
        icon(s).save(os.path.join(OUT, f'icon-{s}.png'))
    icon(512, safe=0.72).save(os.path.join(OUT, 'maskable-512.png'))
    icon(180).convert('RGB').save(os.path.join(OUT, 'apple-touch-icon.png'))
    icon(64).save(os.path.join(ROOT, 'public', 'icon.png'))
    print('app icons written')


if __name__ == '__main__':
    main()
