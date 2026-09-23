"""Render every Morph (front/back/shiny/icon) into public/assets/sprites/mons.png + atlas json."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
from mongen import render
from mon_designs import D
from spr import Spr
from PIL import Image


def main(only=None):
    frames = []
    for sid, (mats, parts) in D.items():
        if only and sid not in only:
            continue
        frames.append((f'{sid}_f', render(parts, mats, 96, 'front')))
        frames.append((f'{sid}_b', render(parts, mats, 96, 'back')))
        frames.append((f'{sid}_fs', render(parts, mats, 96, 'front', shiny=True)))
        frames.append((f'{sid}_bs', render(parts, mats, 96, 'back', shiny=True)))
        frames.append((f'{sid}_i', render(parts, mats, 32, 'front')))
        frames.append((f'{sid}_is', render(parts, mats, 32, 'front', shiny=True)))
    big = [f for f in frames if f[1].w == 96]
    small = [f for f in frames if f[1].w == 32]
    cols = 16
    rows_big = (len(big) + cols - 1) // cols
    rows_small = (len(small) + cols * 3 - 1) // (cols * 3)
    W = cols * 96
    H = rows_big * 96 + rows_small * 32
    sheet = Spr(W, H)
    meta = {}
    for i, (name, s) in enumerate(big):
        x, y = (i % cols) * 96, (i // cols) * 96
        sheet.blit(s, x, y)
        meta[name] = {'frame': {'x': x, 'y': y, 'w': 96, 'h': 96}, 'rotated': False, 'trimmed': False,
                      'spriteSourceSize': {'x': 0, 'y': 0, 'w': 96, 'h': 96}, 'sourceSize': {'w': 96, 'h': 96}}
    y0 = rows_big * 96
    for i, (name, s) in enumerate(small):
        x, y = (i % (cols * 3)) * 32, y0 + (i // (cols * 3)) * 32
        sheet.blit(s, x, y)
        meta[name] = {'frame': {'x': x, 'y': y, 'w': 32, 'h': 32}, 'rotated': False, 'trimmed': False,
                      'spriteSourceSize': {'x': 0, 'y': 0, 'w': 32, 'h': 32}, 'sourceSize': {'w': 32, 'h': 32}}
    out = os.path.join(ROOT, 'public', 'assets', 'sprites')
    os.makedirs(out, exist_ok=True)
    sheet.image().save(os.path.join(out, 'mons.png'), optimize=True)
    with open(os.path.join(out, 'mons.json'), 'w') as f:
        json.dump({'frames': meta, 'meta': {'image': 'mons.png', 'size': {'w': W, 'h': H}, 'scale': '1'}}, f)
    print(f'mons: {len(big)//4} species, sheet {W}x{H}')


def contact(path='/tmp/contact.png'):
    names = list(D.keys())
    cols = 12
    rows = (len(names) + cols - 1) // cols
    sheet = Spr(cols * 98, rows * 98)
    sheet.rect(0, 0, sheet.w, sheet.h, '#cfd6e8')
    for i, sid in enumerate(names):
        mats, parts = D[sid]
        sheet.blit(render(parts, mats, 96, 'front'), (i % cols) * 98, (i // cols) * 98)
    sheet.save(path)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'contact':
        contact()
    else:
        main()
