"""Tiamat map builder.

Reads text map sources from tools/maps/*.map, renders ground / decor / above
layers at pixel level, slices them into 16×16 tiles, de-duplicates everything
into one shared tileset (public/assets/tilesets/world.png) and writes a Tiled
JSON map (.tmj) per map to public/assets/maps/.

The .tmj files open in the Tiled editor (https://www.mapeditor.org). Object
layers (NPCs, warps, signs, items, triggers) are safe to tweak in Tiled, but
re-running this builder regenerates the maps from the .map sources.

Run:  python tools/art/build_maps.py
"""
import os, sys, json, shlex, glob, hashlib
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))

from terrain import render_ground, TID
from spr import Spr
import decor as D
import buildings as B
import interiors as I

T = 16
META = ['none', 'solid', 'water', 'grass', 'ledge_down', 'ledge_left', 'ledge_right', 'counter', 'door', 'bridge', 'noenc']
MI = {n: i for i, n in enumerate(META)}

TERRAIN_CH = {'.': None, ',': 'grass', ':': 'path', ';': 'cobble', '~': 'water', 's': 'sand', 'd': 'forest',
              'm': 'moor', 'n': 'snow', 'c': 'cave', 'k': 'plank', 'a': 'ash'}
TREES = {'T': 'oak', 'A': 'autumn', 'K': 'dark', 'Y': 'pine', 'N': 'snowpine', 'P': 'palm', 'X': 'dead'}


# ────────────────────────────────────────────────────────────────────────────
class MapSrc:
    def __init__(self, path):
        self.path = path
        self.props = {}
        self.layout = []
        self.objects = []
        section = None
        for raw in open(path, encoding='utf-8'):
            line = raw.rstrip('\n')
            if section == 'layout':
                if line.strip() == 'end':
                    section = None
                    continue
                if line.strip() == '':
                    continue
                self.layout.append(line.rstrip())
                continue
            s = line.strip()
            if not s or s.startswith('#'):
                continue
            if s == 'layout:':
                section = 'layout'; continue
            if s == 'objects:':
                section = 'objects'; continue
            if section == 'objects':
                parts = shlex.split(s)
                o = {'type': parts[0], 'x': int(parts[1]), 'y': int(parts[2]), 'args': [], 'kv': {}}
                for p in parts[3:]:
                    if '=' in p:
                        k, v = p.split('=', 1)
                        o['kv'][k] = v
                    else:
                        o['args'].append(p)
                self.objects.append(o)
            else:
                k, v = s.split(':', 1)
                self.props[k.strip()] = v.strip()
        w = max(len(r) for r in self.layout)
        pad = '#' if self.kind == 'interior' else self.props.get('pad', 'T')
        self.layout = [r.ljust(w, pad) for r in self.layout]
        self.id = self.props['id']
        self.w, self.h = w, len(self.layout)

    @property
    def kind(self):
        return self.props.get('kind', 'town')


# ────────────────────────────────────────────────────────────────────────────
class Tileset:
    def __init__(self):
        self.tiles = []          # list of RGBA uint8 arrays
        self.index = {}          # bytes -> id
        self.anims = {}          # first frame id -> [ids]
        self.anim_index = {}

    def add(self, tile):
        if tile[:, :, 3].max() == 0:
            return -1
        key = tile.tobytes()
        if key in self.index:
            return self.index[key]
        self.tiles.append(tile.copy())
        self.index[key] = len(self.tiles) - 1
        return len(self.tiles) - 1

    def add_anim(self, frames):
        key = b''.join(f.tobytes() for f in frames)
        if key in self.anim_index:
            return self.anim_index[key]
        ids = []
        for f in frames:
            self.tiles.append(f.copy())
            ids.append(len(self.tiles) - 1)
        self.anims[ids[0]] = ids
        self.anim_index[key] = ids[0]
        return ids[0]

    def image(self, cols=64):
        n = len(self.tiles)
        rows = (n + cols - 1) // cols
        img = np.zeros((rows * T, cols * T, 4), dtype=np.uint8)
        for i, t in enumerate(self.tiles):
            y, x = divmod(i, cols)
            img[y * T:(y + 1) * T, x * T:(x + 1) * T] = t
        return img, cols, rows


# ────────────────────────────────────────────────────────────────────────────
class Layers:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.decor = Spr(w * T, h * T)
        self.above = Spr(w * T, h * T)
        self.meta = [[0] * w for _ in range(h)]
        self.draws = []   # (sortkey, fn)

    def put_obj(self, spr, ox, oy, cx, cy, split=True):
        """Place sprite so its footprint origin (ox,oy) lands on cell (cx,cy)."""
        X, Y = cx * T - ox, cy * T - oy
        if not split:
            self.decor.blit(spr, X, Y)
            return
        top = Spr(spr.w, spr.h); top.a[:oy] = spr.a[:oy]
        bot = Spr(spr.w, spr.h); bot.a[oy:] = spr.a[oy:]
        self.above.blit(top, X, Y)
        self.decor.blit(bot, X, Y)

    def solid(self, cx, cy, fw, fh, kind='solid'):
        for yy in range(cy, cy + fh):
            for xx in range(cx, cx + fw):
                if 0 <= xx < self.w and 0 <= yy < self.h:
                    self.meta[yy][xx] = MI[kind]


def build_map(src, all_src, tileset, links):
    W, H = src.w, src.h
    L = src.layout
    kind = src.kind
    base = src.props.get('base', 'grass')
    cave = base == 'cave'
    lay = Layers(W, H)
    objects = []
    lights = []

    def ch(x, y):
        if 0 <= x < W and 0 <= y < H:
            return L[y][x]
        return None

    # auto-create exit mats from 'm' cells in interiors
    if kind == 'interior':
        have = {(o['x'], o['y']) for o in src.objects if o['type'] == 'mat'}
        for y in range(H):
            for x in range(W):
                if L[y][x] == 'm' and (x, y) not in have:
                    src.objects.append({'type': 'mat', 'x': x, 'y': y, 'args': [], 'kv': {}})
    # ── ground ──
    if kind == 'interior':
        floor = src.props.get('floor', 'wood')
        wall = src.props.get('wall', 'cream')
        ground = Spr(W * T, H * T)
        ground.rect(0, 0, W * T, H * T, (12, 10, 18))
        windows = []
        for y in range(H):
            for x in range(W):
                c = L[y][x]
                if c in '.m_=':
                    v = (x * 7 + y * 3) % 3
                    ground.blit(I.floor_tile('carpet' if c == '_' else floor, v), x * T, y * T)
                if c in 'Ww':
                    # count wall rows in this column
                    top = y
                    while top - 1 >= 0 and L[top - 1][x] in 'Ww':
                        top -= 1
                    bottom = y
                    while bottom + 1 < H and L[bottom + 1][x] in 'Ww':
                        bottom += 1
                    ground.blit(I.wall_tile(wall, y - top, bottom - top + 1), x * T, y * T)
                    lay.meta[y][x] = MI['solid']
                    if c == 'w' and (y + 1 >= H or L[y + 1][x] not in 'Ww'):
                        windows.append((x, y, top))
                elif c == '#':
                    lay.meta[y][x] = MI['solid']
                elif c == '=':
                    lay.meta[y][x] = MI['counter']
                if c == 'm':
                    lay.decor.blit(I.furniture('mat')[0], x * T, y * T)
        # windows span the lower part of the wall face
        for (wx, wy, top) in windows:
            y0 = max(top * T + 4, wy * T - 10)
            win = I.wall_window()
            ground.blit(win, wx * T, y0)
        # soft shadow along the bottom of walls
        for y in range(1, H):
            for x in range(W):
                if L[y][x] not in 'Ww#' and L[y - 1][x] in 'Ww':
                    for yy in range(3):
                        for xx in range(T):
                            px = ground.a[y * T + yy, x * T + xx]
                            f = (0.72, 0.84, 0.93)[yy]
                            ground.a[y * T + yy, x * T + xx, :3] = (px[:3] * f).astype(np.uint8)
        # counter tops
        for y in range(H):
            x = 0
            while x < W:
                if L[y][x] == '=':
                    x2 = x
                    while x2 + 1 < W and L[y][x2 + 1] == '=':
                        x2 += 1
                    spr, ox, oy, fw, fh = I.furniture('counter', x2 - x + 1)
                    lay.put_obj(spr, ox, oy, x, y)
                    x = x2 + 1
                else:
                    x += 1
        ground_frames = [ground.a]
        water_any = False
    else:
        cells = []
        for y in range(H):
            row = []
            for x in range(W):
                c = L[y][x]
                t = TERRAIN_CH.get(c, None) if c in TERRAIN_CH else None
                if c in ('=', 'H'):
                    t = 'water'
                if t is None:
                    t = base
                row.append(t)
            cells.append(row)
        water_any = any('water' in r for r in cells)
        frames, _ = render_ground(cells, 4 if water_any else 1)
        ground_frames = [np.dstack([f, np.full(f.shape[:2], 255, np.uint8)]) for f in frames]
        # meta for water
        for y in range(H):
            for x in range(W):
                if cells[y][x] == 'water' and L[y][x] not in ('=', 'H'):
                    lay.meta[y][x] = MI['water']

        # ── flat decor ──
        for y in range(H):
            for x in range(W):
                c = L[y][x]
                if c == 'G':
                    lay.decor.blit(D.tall_grass((x * 3 + y) % 2, 0), x * T, y * T)
                    lay.meta[y][x] = MI['grass']
                elif c == 'F':
                    lay.decor.blit(D.flowers((x * 5 + y * 3) % 5), x * T, y * T)
                elif c in ('=', 'H'):
                    lay.decor.blit(D.bridge_tile(c == '='), x * T, y * T)
                    lay.meta[y][x] = MI['bridge']
                elif c == 'v':
                    lay.decor.blit(D.ledge_tile('down', ch(x - 1, y) == 'v', ch(x + 1, y) == 'v', base), x * T, y * T)
                    lay.meta[y][x] = MI['ledge_down']
                elif c in '<>':
                    k = 'left' if c == '<' else 'right'
                    lay.decor.blit(D.ledge_tile(k, ch(x, y - 1) == c, ch(x, y + 1) == c, base), x * T, y * T)
                    lay.meta[y][x] = MI['ledge_' + k]
                elif c == 'R':
                    up, dn, lf, rt = ch(x, y - 1) == 'R', ch(x, y + 1) == 'R', ch(x - 1, y) == 'R', ch(x + 1, y) == 'R'
                    if y == 0: up = True
                    if y == H - 1: dn = True
                    if x == 0: lf = True
                    if x == W - 1: rt = True
                    lay.decor.blit(D.rock_cell(up, dn, lf, rt, cave, snow=(base == 'snow')), x * T, y * T)
                    lay.meta[y][x] = MI['solid']
                elif c == '#':
                    lay.meta[y][x] = MI['solid']

        # ── objects from layout (trees, bushes, fences, props) ──
        done = set()
        for y in range(H):
            for x in range(W):
                c = L[y][x]
                if c in TREES:
                    bx, by = x - x % 2, y - y % 2
                    block = [(bx, by), (bx + 1, by), (bx, by + 1), (bx + 1, by + 1)]
                    if all(ch(px_, py_) == c for px_, py_ in block):
                        if (bx, by) not in done:
                            done.add((bx, by))
                            spr, ox, oy, fw, fh = D.tree(TREES[c], (bx * 3 + by) % 3)
                            lay.draws.append(((by + 2) * T, bx, lambda s=spr, ox=ox, oy=oy, bx=bx, by=by: lay.put_obj(s, ox, oy, bx, by)))
                    else:
                        kind_b = {'N': 'snow', 'K': 'dark', 'X': 'dark'}.get(c, 'green')
                        spr, ox, oy, fw, fh = D.bush(kind_b, (x + y) % 2)
                        lay.draws.append(((y + 1) * T, x, lambda s=spr, ox=ox, oy=oy, x=x, y=y: lay.put_obj(s, ox, oy, x, y)))
                    lay.meta[y][x] = MI['solid']
                elif c in 'bq':
                    spr, ox, oy, fw, fh = D.bush('berry' if c == 'q' else ('snow' if base == 'snow' else 'green'), (x + y) % 2)
                    lay.draws.append(((y + 1) * T, x, lambda s=spr, ox=ox, oy=oy, x=x, y=y: lay.put_obj(s, ox, oy, x, y)))
                    lay.meta[y][x] = MI['solid']
                elif c == 'o':
                    spr, ox, oy, fw, fh = D.boulder('cave' if cave else 'rock')
                    lay.draws.append(((y + 1) * T, x, lambda s=spr, ox=ox, oy=oy, x=x, y=y: lay.put_obj(s, ox, oy, x, y)))
                    lay.meta[y][x] = MI['solid']
                elif c in 'fw':
                    k = 'wood' if c == 'f' else 'stone'
                    spr, ox, oy, fw, fh = D.fence_tile(ch(x - 1, y) == c, ch(x + 1, y) == c, ch(x, y - 1) == c, ch(x, y + 1) == c, k)
                    lay.draws.append(((y + 1) * T, x, lambda s=spr, ox=ox, oy=oy, x=x, y=y: lay.put_obj(s, ox, oy, x, y)))
                    lay.meta[y][x] = MI['solid']
                elif c == 'L':
                    spr, ox, oy, fw, fh = D.prop('lamp')
                    lay.draws.append(((y + 1) * T, x, lambda s=spr, ox=ox, oy=oy, x=x, y=y: lay.put_obj(s, ox, oy, x, y)))
                    lay.meta[y][x] = MI['solid']
                    lights.append({'x': x * T + 8, 'y': y * T - 10, 'r': 44, 'color': '#ffd98a'})

    # ── objects section ──
    for o in src.objects:
        t, x, y, kv, args = o['type'], o['x'], o['y'], o['kv'], o['args']
        if t == 'building':
            bkind = args[0] if args else 'house'
            opts = dict(kind=bkind, w=int(kv.get('w', 4)), h=int(kv.get('h', 4)), roof=kv.get('roof', 'red'),
                        wall=kv.get('wall', 'plaster'), snow=kv.get('snow') == '1', label=kv.get('label'),
                        emblem=kv.get('emblem'), emblem_col=kv.get('type'), variant=int(kv.get('variant', 0)),
                        door=int(kv['door']) if 'door' in kv else None, chimney=kv.get('chimney', '1') == '1')
            b = B.building(**opts)
            lay.draws.append(((y + opts['h']) * T, x, lambda b=b, x=x, y=y: lay.put_obj(b['spr'], b['ox'], b['oy'], x, y)))
            lay.solid(x, y, b['fw'], b['fh'])
            dx, dy = x + b['door'][0], y + b['door'][1]
            lay.meta[dy][dx] = MI['door']
            for (lx_, ly_) in b['lights']:
                lights.append({'x': x * T + lx_, 'y': y * T + ly_ - b['oy'], 'r': 22, 'color': '#ffe7a8', 'window': True})
            if 'to' in kv:
                wkv = {'to': kv['to'], 'door': '1'}
                for k in ('cond', 'locked'):
                    if k in kv:
                        wkv[k] = kv[k]
                objects.append({'type': 'warp', 'x': dx, 'y': dy, 'kv': wkv, 'link_interior': kv['to']})
        elif t == 'lighthouse':
            b = B.lighthouse()
            lay.draws.append(((y + 2) * T, x, lambda b=b, x=x, y=y: lay.put_obj(b['spr'], b['ox'], b['oy'], x, y)))
            lay.solid(x, y, 2, 2)
            dx, dy = x + b['door'][0], y + b['door'][1]
            lay.meta[dy][dx] = MI['door']
            lights.append({'x': x * T + 16, 'y': y * T - 41, 'r': 60, 'color': '#fff3b0'})
            if 'to' in kv:
                objects.append({'type': 'warp', 'x': dx, 'y': dy, 'kv': {'to': kv['to'], 'door': '1'}, 'link_interior': kv['to']})
        elif t == 'cave':
            b = B.cave_mouth('cave' if cave else 'rock')
            lay.draws.append(((y + 2) * T, x, lambda b=b, x=x, y=y: lay.put_obj(b['spr'], b['ox'], b['oy'], x, y)))
            lay.solid(x, y, 3, 2)
            dx, dy = x + 1, y + 1
            lay.meta[dy][dx] = MI['door']
            objects.append({'type': 'warp', 'x': dx, 'y': dy, 'kv': dict(kv, door='1')})
        elif t == 'prop':
            name = args[0]
            spr, ox, oy, fw, fh = D.prop(name)
            lay.draws.append(((y + fh) * T, x, lambda s=spr, ox=ox, oy=oy, x=x, y=y: lay.put_obj(s, ox, oy, x, y)))
            if kv.get('walk') != '1':
                lay.solid(x, y, fw, fh)
            if name == 'sign':
                objects.append({'type': 'sign', 'x': x, 'y': y, 'kv': kv})
            if name in ('lamp', 'lantern_post'):
                lights.append({'x': x * T + 8, 'y': y * T - 10, 'r': 44, 'color': '#ffd98a'})
            if name in ('crystal', 'stone', 'rift_rock'):
                lights.append({'x': x * T + 8, 'y': y * T, 'r': 18, 'color': '#8ae8ff' if name != 'crystal' else '#b89aff'})
            if 'script' in kv or 'text' in kv and name != 'sign':
                objects.append({'type': 'sign', 'x': x, 'y': y, 'kv': kv})
        elif t == 'furn':
            name = args[0]
            v = kv.get('v', 0)
            try:
                v = int(v)
            except ValueError:
                pass
            spr, ox, oy, fw, fh = I.furniture(name, v)
            lay.draws.append(((y + fh) * T, x, lambda s=spr, ox=ox, oy=oy, x=x, y=y: lay.put_obj(s, ox, oy, x, y)))
            if name not in ('rug', 'mat', 'stairs_up', 'stairs_down'):
                lay.solid(x, y, fw, fh, 'counter' if name == 'counter' else 'solid')
            if 'script' in kv or 'text' in kv:
                objects.append({'type': 'sign', 'x': x, 'y': y, 'kv': kv, 'w': fw, 'h': fh})
            if name in ('crystal',):
                lights.append({'x': x * T + 8, 'y': y * T, 'r': 20, 'color': '#b89aff'})
        elif t == 'mat':
            objects.append({'type': 'warp', 'x': x, 'y': y, 'kv': dict(kv, mat='1'), 'is_mat': True})
        elif t in ('warp', 'npc', 'item', 'trigger', 'sign', 'spawn', 'bramble', 'light', 'boulder'):
            if t == 'bramble':
                lay.meta[y][x] = MI['solid']
            if t == 'light':
                lights.append({'x': x * T + 8, 'y': y * T + 8, 'r': int(kv.get('r', 40)), 'color': kv.get('color', '#ffd98a')})
                continue
            objects.append({'type': t, 'x': x, 'y': y, 'kv': kv, 'w': int(kv.get('w', 1)), 'h': int(kv.get('h', 1))})
        else:
            raise ValueError(f'{src.id}: unknown object type {t}')

    for _, _, fn in sorted(lay.draws, key=lambda d: (d[0], d[1])):
        fn()

    # ── slice into tiles ──
    ground_ids = [[0] * W for _ in range(H)]
    decor_ids = [[0] * W for _ in range(H)]
    above_ids = [[0] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            sl = (slice(y * T, (y + 1) * T), slice(x * T, (x + 1) * T))
            frames = [f[sl] for f in ground_frames]
            if len(frames) > 1 and not all(np.array_equal(frames[0], f) for f in frames[1:]):
                gid = tileset.add_anim(frames)
            else:
                gid = tileset.add(frames[0])
            ground_ids[y][x] = gid + 1
            decor_ids[y][x] = tileset.add(lay.decor.a[sl]) + 1
            above_ids[y][x] = tileset.add(lay.above.a[sl]) + 1
    return dict(src=src, W=W, H=H, ground=ground_ids, decor=decor_ids, above=above_ids, meta=lay.meta,
                objects=objects, lights=lights)


def link_warps(built):
    """Resolve building→interior links and interior mats."""
    by_id = {b['src'].id: b for b in built}
    for b in built:
        for o in b['objects']:
            if o['type'] != 'warp':
                continue
            kv = o['kv']
            if 'link_interior' in o:
                target = by_id.get(o['link_interior'])
                if not target:
                    raise ValueError(f"{b['src'].id}: door links to unknown map {o['link_interior']}")
                mats = [m for m in target['objects'] if m.get('is_mat')]
                if not mats:
                    raise ValueError(f"{target['src'].id}: interior has no mat")
                mat = mats[0]
                kv['to'] = f"{target['src'].id}:{mat['x']},{mat['y'] - 1}"
                kv['face'] = 'up'
                for mt in mats:
                    if 'to' not in mt['kv']:
                        mt['kv']['to'] = f"{b['src'].id}:{o['x']},{o['y'] + 1}"
                        mt['kv']['face'] = 'down'
    for b in built:
        for o in b['objects']:
            if o['type'] == 'warp' and 'to' not in o['kv']:
                raise ValueError(f"{b['src'].id}: warp at {o['x']},{o['y']} has no destination")


def _props(d):
    out = []
    for k, v in d.items():
        if isinstance(v, bool):
            out.append({'name': k, 'type': 'bool', 'value': v})
        elif isinstance(v, int):
            out.append({'name': k, 'type': 'int', 'value': v})
        else:
            out.append({'name': k, 'type': 'string', 'value': str(v)})
    return out


def write_all(built, tileset, out_maps, out_tiles):
    os.makedirs(out_maps, exist_ok=True)
    os.makedirs(out_tiles, exist_ok=True)
    img, cols, rows = tileset.image()
    Image.fromarray(img, 'RGBA').save(os.path.join(out_tiles, 'world.png'), optimize=True)
    # meta marker tileset (for Tiled display)
    colors = [(0, 0, 0, 0), (230, 60, 60, 120), (60, 120, 230, 120), (60, 200, 80, 120), (240, 200, 60, 140),
              (240, 160, 60, 140), (240, 120, 60, 140), (200, 60, 200, 120), (255, 255, 255, 140), (160, 110, 60, 120), (120, 120, 120, 120)]
    meta_img = np.zeros((T, T * len(META), 4), dtype=np.uint8)
    for i, c in enumerate(colors):
        meta_img[1:T - 1, i * T + 1:(i + 1) * T - 1] = c
    Image.fromarray(meta_img, 'RGBA').save(os.path.join(out_tiles, 'meta.png'))
    ntiles = len(tileset.tiles)
    tiles_json = [{'id': k, 'animation': [{'tileid': f, 'duration': 220} for f in v]} for k, v in tileset.anims.items()]
    world_ts = {'firstgid': 1, 'name': 'world', 'image': '../tilesets/world.png', 'imagewidth': cols * T,
                'imageheight': rows * T, 'tilewidth': T, 'tileheight': T, 'tilecount': ntiles, 'columns': cols,
                'margin': 0, 'spacing': 0, 'tiles': tiles_json}
    meta_ts = {'firstgid': ntiles + 1, 'name': 'meta', 'image': '../tilesets/meta.png', 'imagewidth': T * len(META),
               'imageheight': T, 'tilewidth': T, 'tileheight': T, 'tilecount': len(META), 'columns': len(META),
               'margin': 0, 'spacing': 0,
               'tiles': [{'id': i, 'properties': [{'name': 'behavior', 'type': 'string', 'value': n}]} for i, n in enumerate(META)]}
    index = {}
    for b in built:
        src = b['src']
        W, H = b['W'], b['H']
        flat = lambda g: [v for row in g for v in row]
        meta_flat = [(ntiles + 1 + v) if v else 0 for row in b['meta'] for v in row]
        objs = []
        oid = 1
        for o in b['objects']:
            kv = dict(o['kv'])
            objs.append({'id': oid, 'name': kv.get('id', ''), 'type': o['type'], 'x': o['x'] * T, 'y': o['y'] * T,
                         'width': o.get('w', 1) * T, 'height': o.get('h', 1) * T, 'rotation': 0, 'visible': True,
                         'properties': _props(kv)})
            oid += 1
        for l in b['lights']:
            objs.append({'id': oid, 'name': '', 'type': 'light', 'x': l['x'], 'y': l['y'], 'width': 0, 'height': 0,
                         'rotation': 0, 'visible': True, 'point': True,
                         'properties': _props({'r': l['r'], 'color': l['color'], 'window': bool(l.get('window'))})})
            oid += 1
        props = {k: v for k, v in src.props.items() if k != 'id'}
        tm = {'type': 'map', 'version': '1.10', 'tiledversion': '1.10.2', 'orientation': 'orthogonal',
              'renderorder': 'right-down', 'width': W, 'height': H, 'tilewidth': T, 'tileheight': T,
              'infinite': False, 'nextlayerid': 6, 'nextobjectid': oid,
              'properties': _props(props),
              'layers': [
                  {'id': 1, 'name': 'ground', 'type': 'tilelayer', 'width': W, 'height': H, 'x': 0, 'y': 0, 'opacity': 1, 'visible': True, 'data': flat(b['ground'])},
                  {'id': 2, 'name': 'decor', 'type': 'tilelayer', 'width': W, 'height': H, 'x': 0, 'y': 0, 'opacity': 1, 'visible': True, 'data': flat(b['decor'])},
                  {'id': 3, 'name': 'above', 'type': 'tilelayer', 'width': W, 'height': H, 'x': 0, 'y': 0, 'opacity': 1, 'visible': True, 'data': flat(b['above'])},
                  {'id': 4, 'name': 'meta', 'type': 'tilelayer', 'width': W, 'height': H, 'x': 0, 'y': 0, 'opacity': 0.6, 'visible': False, 'data': meta_flat},
                  {'id': 5, 'name': 'objects', 'type': 'objectgroup', 'draworder': 'topdown', 'x': 0, 'y': 0, 'opacity': 1, 'visible': True, 'objects': objs},
              ],
              'tilesets': [world_ts, meta_ts]}
        with open(os.path.join(out_maps, src.id + '.tmj'), 'w') as f:
            json.dump(tm, f, separators=(',', ':'))
        index[src.id] = {'name': src.props.get('name', src.id), 'kind': src.kind, 'w': W, 'h': H}
    with open(os.path.join(out_maps, 'index.json'), 'w') as f:
        json.dump(index, f, indent=1)
    return ntiles


def main(only=None):
    srcs = [MapSrc(p) for p in sorted(glob.glob(os.path.join(ROOT, 'tools', 'maps', '*.map')))]
    tileset = Tileset()
    built = []
    for s in srcs:
        built.append(build_map(s, srcs, tileset, None))
    link_warps(built)
    n = write_all(built, tileset, os.path.join(ROOT, 'public', 'assets', 'maps'), os.path.join(ROOT, 'public', 'assets', 'tilesets'))
    print(f'built {len(built)} maps, {n} unique tiles, {len(tileset.anims)} animated')


if __name__ == '__main__':
    main()
