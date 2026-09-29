"""Which trainers can be walked straight past?

For every outdoor map: finds the ways in and out (walkable tiles on the map edges and door warps), then for each
trainer checks whether you can still get from one way in to every other one without ever stepping into that
trainer's line of sight. A trainer that can be avoided like that is "optional"; everything else is "blocking".

    python3 tools/trainer_gates.py route6 riftgate      (or no names for every outdoor map)
"""
import json, os, sys
from collections import deque

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
MAPS = os.path.join(ROOT, 'public', 'assets', 'maps')
META = ['none', 'solid', 'water', 'grass', 'ledge_down', 'ledge_left', 'ledge_right', 'counter', 'door', 'bridge', 'noenc']
SIGHT_BLOCK = {'solid', 'counter', 'door', 'water', 'ledge_down', 'ledge_left', 'ledge_right'}
DIRS = {'up': (0, -1), 'down': (0, 1), 'left': (-1, 0), 'right': (1, 0)}
LEDGE = {'ledge_down': (0, 1), 'ledge_left': (-1, 0), 'ledge_right': (1, 0)}
SOLID_PROPS = {'sign', 'npc', 'item', 'prop', 'furn'}


def load(mid):
    tm = json.load(open(os.path.join(MAPS, f'{mid}.tmj')))
    W, H = tm['width'], tm['height']
    mts = next(t for t in tm['tilesets'] if t['name'] == 'meta')
    ml = next(l for l in tm['layers'] if l['name'] == 'meta')
    meta = [META[g - mts['firstgid']] if g >= mts['firstgid'] else 'none' for g in ml['data']]
    objs = []
    for l in tm['layers']:
        if l['type'] == 'objectgroup':
            for o in l['objects']:
                p = {q['name']: q['value'] for q in o.get('properties', [])}
                objs.append((o['type'], int(o['x'] // 16), int(o['y'] // 16), p))
    props = {q['name']: q['value'] for q in tm.get('properties', [])}
    return W, H, meta, objs, props


def analyse(mid):
    W, H, meta, objs, props = load(mid)
    beh = lambda x, y: meta[y * W + x] if 0 <= x < W and 0 <= y < H else 'solid'
    blocked = set()
    trainers = []
    doors = []
    for t, x, y, p in objs:
        if t == 'npc' and p.get('show') == 'never':
            continue
        if t == 'item' and p.get('hidden') == '1':
            continue
        if t == 'warp':
            doors.append((x, y)); continue
        if t == 'trigger' and ('block' in p.get('script', '') or 'gate' in p.get('script', '')) and p.get('cond'):
            # a story gate ("nobody passes until ...") — treat it as closed
            for k in range(int(p.get('w', 1))):
                for j in range(int(p.get('h', 1))):
                    blocked.add((x + k, y + j))
            continue
        if t in SOLID_PROPS and not p.get('walk'):
            blocked.add((x, y))
        if t == 'npc' and p.get('trainer'):
            trainers.append((p['trainer'], x, y, p.get('face', 'down'), int(p.get('sight', 4)), p.get('move', 'still')))

    def sight(tr):
        _, x, y, face, rng, move = tr
        seen = set()
        for f in (DIRS if move == 'look' else [face]):
            dx, dy = DIRS[f]
            for i in range(1, rng + 1):
                cx, cy = x + dx * i, y + dy * i
                if beh(cx, cy) in SIGHT_BLOCK or (cx, cy) in blocked:
                    break
                seen.add((cx, cy))
        return seen

    def free(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in blocked and beh(x, y) in ('none', 'grass', 'bridge', 'noenc', 'door')

    def steps(x, y):
        for dx, dy in DIRS.values():
            nx, ny = x + dx, y + dy
            b = beh(nx, ny)
            if b in LEDGE:
                if LEDGE[b] == (dx, dy) and free(nx + dx, ny + dy):
                    yield nx + dx, ny + dy
            elif free(nx, ny):
                yield nx, ny

    # ways in: walkable edge tiles (grouped per side) and doors
    sides = {'west': [(0, y) for y in range(H)], 'east': [(W - 1, y) for y in range(H)],
             'north': [(x, 0) for x in range(W)], 'south': [(x, H - 1) for x in range(W)]}
    exits = {k: [p for p in v if free(*p)] for k, v in sides.items()}
    exits = {k: v for k, v in exits.items() if v and props.get(k)}
    for i, d in enumerate(doors):
        exits[f'door{d}'] = [d]

    def reach(start, avoid):
        seen = set(p for p in start if p not in avoid)
        q = deque(seen)
        while q:
            x, y = q.popleft()
            for n in steps(x, y):
                if n not in seen and n not in avoid:
                    seen.add(n); q.append(n)
        return seen

    names = list(exits)
    main = [k for k in names if not k.startswith('door')]
    report = []
    for tr in trainers:
        s = sight(tr)
        dodge = []
        for a in main:
            got = reach(exits[a], s)
            for b in main:
                if b != a and any(p in got for p in exits[b]):
                    dodge.append(f'{a}->{b}')
        blocks = [f'{a}->{b}' for a in main for b in main if a != b and f'{a}->{b}' not in dodge]
        report.append((tr[0], tr[1:3], tr[3], tr[5], len(s), dodge, blocks))
    allsight = set().union(*[sight(t) for t in trainers]) if trainers else set()
    clean = []
    for a in main:
        got = reach(exits[a], allsight)
        for b in main:
            if b != a and any(p in got for p in exits[b]):
                clean.append(f'{a}->{b}')
    return report, clean, main


def route(mid, start, goal):
    """Shortest walk (list of 'up'/'down'/'left'/'right' presses) from start to goal, honouring ledges."""
    W, H, meta, objs, props = load(mid)
    beh = lambda x, y: meta[y * W + x] if 0 <= x < W and 0 <= y < H else 'solid'
    blocked = {(x, y) for t, x, y, p in objs if t in SOLID_PROPS and not p.get('walk') and p.get('show') != 'never' and not (t == 'item' and p.get('hidden') == '1')}
    free = lambda x, y: 0 <= x < W and 0 <= y < H and (x, y) not in blocked and beh(x, y) in ('none', 'grass', 'bridge', 'noenc', 'door')
    prev = {tuple(start): None}
    q = deque([tuple(start)])
    while q:
        x, y = q.popleft()
        if (x, y) == tuple(goal):
            break
        for name, (dx, dy) in DIRS.items():
            nx, ny = x + dx, y + dy
            b = beh(nx, ny)
            if b in LEDGE:
                if LEDGE[b] != (dx, dy) or not free(nx + dx, ny + dy):
                    continue
                nx, ny = nx + dx, ny + dy
            elif not free(nx, ny):
                continue
            if (nx, ny) not in prev:
                prev[(nx, ny)] = ((x, y), name); q.append((nx, ny))
    if tuple(goal) not in prev:
        return None
    out, cur = [], tuple(goal)
    while prev[cur]:
        cur, name = prev[cur][0], prev[cur][1]
        out.append(name)
    return out[::-1]


if __name__ == '__main__':
    ids = sys.argv[1:] or sorted(f[:-4] for f in os.listdir(MAPS) if f.endswith('.tmj'))
    for mid in ids:
        W, H, meta, objs, props = load(mid)
        if props.get('kind') == 'interior':
            continue
        report, clean, main = analyse(mid)
        if not report:
            continue
        print(f'== {mid}  (ways in: {", ".join(main)})')
        for tid, pos, face, move, n, dodge, blocks in report:
            if len(main) < 2:
                state = 'n/a (only one way in on foot)'
            else:
                state = ('blocks ' + ', '.join(blocks)) if blocks else 'can be walked around'
            print(f'   {tid:<16} at {pos[0]:>2},{pos[1]:>2} facing {face:<5} {move:<5} sees {n} tiles  {state}')
        print('   walk through without any battle:', ', '.join(clean) if clean else 'impossible')
