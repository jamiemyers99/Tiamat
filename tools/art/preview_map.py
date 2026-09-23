"""Render a built .tmj to PNG (for quick visual checks)."""
import json, sys, os
from PIL import Image
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
def render(mid, scale=2, out=None):
    tm = json.load(open(f'{ROOT}/public/assets/maps/{mid}.tmj'))
    ts = Image.open(f'{ROOT}/public/assets/tilesets/world.png').convert('RGBA')
    cols = tm['tilesets'][0]['columns']; n = tm['tilesets'][0]['tilecount']
    W, H = tm['width'], tm['height']
    img = Image.new('RGBA', (W*16, H*16), (10, 8, 16, 255))
    for layer in tm['layers']:
        if layer['type'] != 'tilelayer' or layer['name'] == 'meta': continue
        for i, g in enumerate(layer['data']):
            if g == 0 or g > n: continue
            t = g - 1; tx, ty = (t % cols) * 16, (t // cols) * 16
            tile = ts.crop((tx, ty, tx+16, ty+16))
            img.alpha_composite(tile, ((i % W)*16, (i // W)*16))
    img = img.resize((W*16*scale, H*16*scale), Image.NEAREST)
    img.save(out or f'/tmp/map_{mid}.png')
if __name__ == '__main__':
    for m in sys.argv[1:]: render(m)
