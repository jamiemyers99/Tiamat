"""Render every Morph (front/back/shiny/icon) into public/assets/sprites/mons.png + atlas json."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
from mongen import render
from mon_designs import D
from mon_designs_a import NEW as NEW_A
from mon_designs_b import NEW as NEW_B
from mon_designs_c import NEW as NEW_C

for _extra in (NEW_A, NEW_B, NEW_C):
    for _k in _extra:
        assert _k not in D, f'duplicate Morph design {_k}'
    D.update(_extra)
from spr import Spr
from PIL import Image

# species that only exist as female (Tiamat, the Draco Queen): their plain frames use the female form too
FEMALE_ONLY = {'tiamat'}


def main(only=None):
    frames = []
    for sid, (mats, parts) in D.items():
        if only and sid not in only:
            continue
        for sex in ('', '_fem'):
            fem = sex == '_fem' or sid in FEMALE_ONLY
            frames.append((f'{sid}_f{sex}', render(parts, mats, 96, 'front', female=fem)))
            frames.append((f'{sid}_b{sex}', render(parts, mats, 96, 'back', female=fem)))
            frames.append((f'{sid}_fs{sex}', render(parts, mats, 96, 'front', shiny=True, female=fem)))
            frames.append((f'{sid}_bs{sex}', render(parts, mats, 96, 'back', shiny=True, female=fem)))
            frames.append((f'{sid}_i{sex}', render(parts, mats, 32, 'front', female=fem)))
            frames.append((f'{sid}_is{sex}', render(parts, mats, 32, 'front', shiny=True, female=fem)))
    big = [f for f in frames if f[1].w == 96]
    small = [f for f in frames if f[1].w == 32]
    cols = 32   # keeps the sheet under 4096 px tall (phone GPU texture limit)
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
    print(f'mons: {len(big)//8} species (male + female), sheet {W}x{H}')


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
