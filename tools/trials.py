"""The six Trial halls, each with its own puzzle, getting harder as you go:

  1 Moss  (Brindlewood)  a hedge maze
  2 Tide  (Saltreach)    tide currents that carry you across a pool
  3 Spark (Gearhollow)   floor switches that flip which electric gates are open
  4 Veil  (Hollowmere)   warp pads between islands in the dark
  5 Rime  (Frostspire)   sliding across ice rinks
  6 Wyrm  (Riftgate)     rift-glass slides, with crystal gates switched from the ice

Adepts stand where the solution has to pass, so each one is battled (the Warden checks too).
Every layout is checked by tools/puzzle_check.py.

Layout characters (interiors): W wall, . floor, _ carpet, m exit mat, h hedge, x barrier block, p deep pool,
# a drop into the dark, i ice, j rift glass, r ice rock, 8 2 4 6 currents (up down left right).
"""
import random
from mapkit import M, TRIAL_STYLE


# Once a Trial is won the hall powers down, like a finished gym in the classics: ice and rift glass stop sliding,
# currents go still, every gate stays open, and a pair of Warden's pads lights up: one by the entrance that takes you
# straight to the Warden, one by the Warden that takes you straight back out. (hall: sigil, pad in, pad out)
DONE = {
    'brindlewood_trial': ('moss', (10, 15), (5, 3)),
    'saltreach_trial': ('tide', (5, 18), (11, 3)),
    'gearhollow_trial': ('spark', (6, 18), (5, 3)),
    'hollowmere_trial': ('veil', (7, 17), (12, 3)),
    'frostspire_trial': ('rime', (10, 21), (6, 3)),
    'riftgate_trial': ('wyrm', (7, 17), (6, 3)),
}


def room(id, town, type_, rows, warden, adepts, guide, objs=(), light=None):
    st = TRIAL_STYLE[type_]
    H, W = len(rows), len(rows[0])
    assert all(len(r) == W for r in rows), f'{id}: ragged rows ' + str([len(r) for r in rows])
    sigil, pad_in, pad_out = DONE[id]
    done = f'sigil_{sigil}'
    props = dict(name=f'{town} Trial Hall', floor=st['floor'], wall=st['wall'], music='trial', battle='arena', done=done)
    if light:
        props['light'] = light
    m = M(id, W, H, kind='interior', **props)
    for y, row in enumerate(rows):
        for x, c in enumerate(row):
            m.g[y][x] = c
    wid, wspr, wx, wy = warden
    m.npc(wx, wy, wid, wspr, script=f'{id}.warden')
    for (tid, spr, x, y, face, sight) in adepts:
        m.trainer(x, y, tid, spr, face=face, sight=sight, post='1')   # back to their post after the battle
    gx, gy, text = guide
    m.npc(gx, gy, f'{id}_guide', 'ace', text=text)
    for o in objs:
        if o.startswith('gate ') and ' open=' in o:          # gates stay open once the Trial is won
            head, rest = o.split(' open=', 1)
            cond, _, tail = rest.partition(' ')
            o = f'{head} open={cond}|{done} {tail}'.rstrip()
        m.obj(o)
    # the Warden's pads (hidden and inactive until the Trial is won)
    mx, my = next((x, y) for y, r in enumerate(rows) for x, c in enumerate(r) if c == 'm')
    taken = {(int(o.split()[1]), int(o.split()[2])) for o in objs if o.startswith('furn ')}
    taken |= {(a[2], a[3]) for a in adepts} | {(wx, wy), (guide[0], guide[1])}
    for (px, py), (tx, ty, face) in ((pad_in, (wx, wy + 1, 'up')), (pad_out, (mx, my - 1, 'down'))):
        assert rows[py][px] in '._' and (px, py) not in taken, f'{id}: Warden pad at {px},{py} is not on free floor'
        assert (tx, ty) not in taken, f'{id}: Warden pad arrival {tx},{ty} is taken'
        assert rows[ty][tx] in '._', f'{id}: Warden pad arrival {tx},{ty} is not on the floor'
        m.obj(f'warp {px} {py} to={id}:{tx},{ty} face={face} cond={done} quiet=1')
        m.obj(f'plate {px} {py} on={done} onframe=warden_pad')
    return m


# ── 1. Moss: a hedge maze ────────────────────────────────────────────────────
def perfect_maze(cw, ch, seed):
    """A maze with exactly one route between any two cells (recursive backtracker). Cells sit at odd tiles."""
    rnd = random.Random(seed)
    g = [['h'] * (2 * cw + 1) for _ in range(2 * ch + 1)]
    stack, seen = [(0, 0)], {(0, 0)}
    g[1][1] = '.'
    while stack:
        cx, cy = stack[-1]
        nb = [(cx + dx, cy + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
              if 0 <= cx + dx < cw and 0 <= cy + dy < ch and (cx + dx, cy + dy) not in seen]
        if not nb:
            stack.pop()
            continue
        nx, ny = rnd.choice(nb)
        g[cy + ny + 1][cx + nx + 1] = '.'
        g[2 * ny + 1][2 * nx + 1] = '.'
        seen.add((nx, ny))
        stack.append((nx, ny))
    return g


def maze_route(g, a, b):
    """Tile route between two cells of a perfect maze."""
    from collections import deque
    H, W = len(g), len(g[0])
    prev = {a: None}
    q = deque([a])
    while q:
        p = q.popleft()
        if p == b:
            break
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (p[0] + dx, p[1] + dy)
            if 0 <= n[0] < W and 0 <= n[1] < H and g[n[1]][n[0]] == '.' and n not in prev:
                prev[n] = p
                q.append(n)
    out, p = [], b
    while p:
        out.append(p)
        p = prev[p]
    return out[::-1]


def brindlewood_trial():
    cw, ch = 8, 5                                   # 17×11 tiles of maze
    entry, exit_ = (3, ch - 1), (4, 0)              # cells: bottom middle-left, top middle
    best = None
    for seed in range(400):                         # the longest-winding maze whose route has room for adepts
        g = perfect_maze(cw, ch, seed)
        route = maze_route(g, (2 * entry[0] + 1, 2 * entry[1] + 1), (2 * exit_[0] + 1, 2 * exit_[1] + 1))
        if best is None or len(route) > len(best[1]):
            best = (g, route, seed)
    g, route, seed = best
    rows = ['W' * 17, 'W' * 17,
            '........_........',
            '.......___.......']
    maze = [''.join(r) for r in g]
    maze[0] = maze[0][:9] + '.' + maze[0][10:]               # out to the Warden's court
    maze[-1] = maze[-1][:7] + '.' + maze[-1][8:]             # in from the entrance hall
    rows += maze
    rows += ['h......._.......h', '.......mm........'[:17]]
    # adepts stand in gaps cut into the hedge right beside the route, facing it; the route is the only way
    # through, so nobody gets past them unseen (the gap stays blocked by the adept, so no shortcut opens)
    adepts = []
    for frac, (tid, spr) in zip((0.3, 0.72), [('bw_adept_1', 'lass'), ('bw_adept_2', 'ranger')]):
        k = int(len(route) * frac)
        for j in list(range(k, len(route))) + list(range(k, 0, -1)):
            px, py = route[j]
            if px % 2 == 0 or py % 2 == 0:
                continue                             # route cells only
            spot = None
            for dx, dy, face in ((1, 0, 'left'), (-1, 0, 'right'), (0, 1, 'up'), (0, -1, 'down')):
                wx, wy = px + dx, py + dy
                if 0 < wx < 16 and 0 < wy < 10 and g[wy][wx] == 'h' and (wx, wy) not in route:
                    spot = (wx, wy, face)
                    break
            if spot and all(abs(spot[0] - a[2]) + abs(spot[1] + 4 - a[3]) > 4 for a in adepts):
                rows[spot[1] + 4] = rows[spot[1] + 4][:spot[0]] + '.' + rows[spot[1] + 4][spot[0] + 1:]
                adepts.append((tid, spr, spot[0], spot[1] + 4, spot[2], 3))
                break
    objs = ['furn 0 2 plant', 'furn 16 2 plant', 'furn 6 2 statue', 'furn 10 2 statue', 'furn 0 15 plant', 'furn 16 15 plant']
    return room('brindlewood_trial', 'Brindlewood', 'Nature', rows, ('mossa', 'mossa', 8, 2), adepts,
                (6, 15, "Hey, challenger! Warden Mossa grew this hedge maze herself. Find your way to her! Her Morphs are Nature type — Fire burns them, and birds peck them to bits."),
                objs)


def grid(W, H, fill):
    return [[fill] * W for _ in range(H)]


def put(g, x, y, c):
    g[y][x] = c


def fill(g, x0, y0, x1, y1, c):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            g[y][x] = c


def lane(g, *steps):
    """A current: steps are (x, y, arrow) where arrow is 8 2 4 6."""
    for (x, y, a) in steps:
        g[y][x] = a


# ── 2. Tide: currents across a pool ─────────────────────────────────────────
def saltreach_trial():
    W, H = 18, 20
    g = grid(W, H, 'p')
    fill(g, 0, 0, W - 1, 1, 'W')
    fill(g, 6, 2, 11, 3, '.')                     # the Captain's deck
    fill(g, 4, 17, 13, 18, '.')                   # the landing
    put(g, 8, 19, 'm'); put(g, 9, 19, 'm')
    fill(g, 1, 13, 3, 15, '.')                    # A  (south-west rock)
    fill(g, 14, 13, 16, 15, '.')                  # B  (south-east rock)
    fill(g, 7, 9, 10, 11, '.')                    # C  (the middle)
    fill(g, 1, 5, 3, 7, '.')                      # D  (north-west rock)
    fill(g, 14, 5, 16, 7, '.')                    # E  (north-east rock)
    lane(g, (3, 17, '8'), (3, 16, '8'))                                                   # landing → A
    lane(g, (14, 17, '8'), (14, 16, '8'))                                                 # landing → B
    lane(g, (4, 14, '6'), (5, 14, '6'), (6, 14, '6'), (7, 14, '8'), (7, 13, '8'), (7, 12, '8'))   # A → C
    lane(g, (13, 14, '4'), (12, 14, '4'), (11, 14, '2'), (11, 15, '2'), (11, 16, '2'))    # B → back to the landing
    lane(g, (8, 8, '8'), (8, 7, '4'), (7, 7, '4'), (6, 7, '4'), (5, 7, '4'), (4, 7, '4'))  # C → D
    lane(g, (6, 10, '2'), (6, 11, '2'), (6, 12, '2'), (6, 13, '2'))                     # C → round and back to C
    lane(g, (11, 10, '6'), (12, 10, '6'), (13, 10, '2'), (13, 11, '2'), (13, 12, '2'), (13, 13, '6'))   # C → B
    lane(g, (2, 8, '2'), (2, 9, '2'), (2, 10, '2'), (2, 11, '2'), (2, 12, '2'))         # D → A
    lane(g, *[(x, 6, '6') for x in range(4, 14)])                                       # D → E
    lane(g, (13, 5, '8'), (13, 4, '4'), (12, 4, '4'), (11, 4, '8'))                     # E → the Captain's deck
    lane(g, (15, 8, '2'), (15, 9, '2'), (15, 10, '2'), (15, 11, '2'), (15, 12, '2'))    # E → B
    rows = [''.join(r) for r in g]
    adepts = [('st_adept_1', 'sailor', 1, 14, 'right', 3), ('st_adept_2', 'fisher', 10, 9, 'left', 3),
              ('st_adept_3', 'sailor', 16, 5, 'left', 3)]
    fill(g, 4, 19, 13, 19, '.'); put(g, 8, 19, 'm'); put(g, 9, 19, 'm')
    rows = [''.join(r) for r in g]
    objs = ['furn 6 2 barrel', 'furn 11 2 barrel', 'furn 4 18 crate', 'furn 13 18 crate']
    return room('saltreach_trial', 'Saltreach', 'Tide', rows, ('brann', 'brann', 8, 2), adepts,
                (12, 17, "Ahoy! The Captain's pool runs on tides — step onto a current and it carries you. Pick your currents well! His crew are Tide type: Nature and Static Morphs make short work of them."),
                objs)


# ── 3. Spark: switches flip which gates carry current ────────────────────────
def spark_gate(x, y, colour):
    """A yellow gate is open while the switch is yellow (flag off); a blue one while it's blue (flag on)."""
    cond = '!gh_flip' if colour == 'y' else 'gh_flip'
    return f'gate {x} {y} open={cond} frame=gate_{colour} openframe=gate_open'


def spark_plate(x, y):
    return [f'trigger {x} {y} script=trial.flip flag=gh_flip', f'plate {x} {y} on=gh_flip frame=plate_y onframe=plate_b']


def gearhollow_trial():
    W, H = 18, 20
    g = grid(W, H, '.')
    fill(g, 0, 0, W - 1, 1, 'W')
    for y in (5, 10, 14):
        fill(g, 0, y, W - 1, y, 'x')                   # the three walls
    fill(g, 0, 6, 0, 18, 'x'); fill(g, W - 1, 6, W - 1, 18, 'x')
    fill(g, 8, 6, 9, 9, 'x'); fill(g, 8, 11, 9, 13, 'x')   # the middle walls splitting west from east
    fill(g, 0, 19, W - 1, 19, 'x'); put(g, 8, 19, 'm'); put(g, 9, 19, 'm')
    for (x, y) in [(4, 14), (13, 14), (4, 10), (13, 10), (8, 7), (9, 7), (13, 5)]:
        put(g, x, y, '.')                                 # the gates stand in gaps in the walls
    rows = [''.join(r) for r in g]
    objs = []
    objs += [spark_gate(4, 14, 'y'), spark_gate(13, 14, 'b')]          # hall → west / east
    objs += [spark_gate(4, 10, 'b'), spark_gate(13, 10, 'y')]          # west → upper west / east → upper east
    objs += [spark_gate(8, 7, 'y'), spark_gate(9, 7, 'y')]             # upper west ↔ upper east
    objs += [spark_gate(13, 5, 'b')]                                   # upper east → Iskra
    for (x, y) in [(2, 12), (15, 12), (2, 7), (15, 7)]:
        objs += spark_plate(x, y)
    objs += ['furn 1 2 machine', 'furn 16 2 machine', 'furn 5 2 statue', 'furn 11 2 statue', 'furn 1 17 machine', 'furn 16 17 machine']
    adepts = [('gh_adept_1', 'engineer', 6, 12, 'left', 4), ('gh_adept_2', 'scholar', 6, 7, 'left', 4),
              ('gh_adept_3', 'engineer', 11, 7, 'right', 4)]
    return room('gearhollow_trial', 'Gearhollow', 'Static', rows, ('iskra', 'iskra', 8, 2), adepts,
                (11, 17, "Hey hey! Iskra wired the whole hall. Step on a switch and every yellow gate swaps with every blue one! Her Morphs are Static — and half are Iron too. Stone Morphs shrug off lightning."),
                objs)


# ── 4. Veil: warp pads between islands in the dark ──────────────────────────
def hollowmere_trial():
    W, H = 20, 20
    g = grid(W, H, '#')
    fill(g, 0, 0, W - 1, 1, 'W')
    fill(g, 7, 2, 12, 4, '.')                       # Morrow's island
    fill(g, 7, 16, 12, 18, '.')                     # the landing
    put(g, 9, 19, 'm'); put(g, 10, 19, 'm')
    islands = {
        'I1': [(4, 14), (3, 14), (2, 14), (2, 13)],
        'I4': [(9, 11), (10, 11), (11, 11)],
        'I5': [(15, 9), (16, 9), (17, 9)],
        'I2': [(15, 14), (16, 14), (17, 14), (17, 13), (16, 15)],
        'I3': [(3, 9), (4, 9), (5, 9), (5, 8), (2, 9), (4, 10)],
        'I6': [(3, 4), (4, 4), (5, 4), (5, 3)],
        'I7': [(15, 4), (16, 4), (17, 4), (17, 5), (16, 3)],
    }
    for tiles in islands.values():
        for (x, y) in tiles:
            put(g, x, y, '.')
    rows = [''.join(r) for r in g]
    objs = []
    def pads(a, b, colour, one_way=False):
        (ax, ay), (bx, by) = a, b
        objs.append(f'furn {ax} {ay} pad v={colour}')
        objs.append(f'warp {ax} {ay} to=hollowmere_trial:{bx},{by} face=down')
        if not one_way:
            objs.append(f'furn {bx} {by} pad v={colour}')
            objs.append(f'warp {bx} {by} to=hollowmere_trial:{ax},{ay} face=down')
    pads((8, 16), (4, 14), 0)          # landing ↔ I1
    pads((11, 16), (15, 14), 1)        # landing ↔ I2
    pads((2, 13), (9, 11), 2)          # I1 ↔ I4
    pads((11, 11), (15, 9), 3)         # I4 ↔ I5
    pads((17, 9), (10, 17), 0, True)   # I5 → back to the landing
    pads((17, 13), (3, 9), 2)          # I2 ↔ I3
    pads((2, 9), (10, 11), 1, True)    # I3 → I4 (a detour)
    pads((5, 8), (3, 4), 3)            # I3 ↔ I6
    pads((5, 3), (15, 4), 1)           # I6 ↔ I7
    pads((17, 5), (8, 4), 2)           # I7 ↔ Morrow's island
    objs += ['furn 7 2 crystal', 'furn 12 2 crystal', 'furn 7 18 pot', 'furn 12 18 pot']
    adepts = [('hm_adept_1', 'mystic', 16, 15, 'up', 3), ('hm_adept_2', 'scholar', 4, 10, 'up', 3),
              ('hm_adept_3', 'mystic', 16, 3, 'down', 3)]
    return room('hollowmere_trial', 'Hollowmere', 'Umbra', rows, ('morrow', 'morrow', 10, 2), adepts,
                (12, 17, "...Can you see me? Morrow keeps the hall dark. Only the warp pads glow — each one sends you to another island. Remember where they go! Umbra Morphs fear Brawl fists and bright Swarm wings."),
                objs, light='dark')


# ── shared: a tiny ice solver for the generators below (same rules as puzzle_check) ──
DIRS4 = {'u': (0, -1), 'd': (0, 1), 'l': (-1, 0), 'r': (1, 0)}


def ice_solve(g, start, goal_fn, solid='x#rWp', slide='ij', switches=None, gates=None):
    """BFS over (x, y, flags). g: list of lists. switches {(x,y): flag}; gates {(x,y): cond(flags)->open}.
    Returns (presses, route) or None."""
    from collections import deque
    switches, gates = switches or {}, gates or {}
    H, W = len(g), len(g[0])

    def blocked(x, y, fl):
        if not (0 <= x < W and 0 <= y < H) or g[y][x] in solid:
            return True
        return (x, y) in gates and not gates[(x, y)](fl)

    def settle(x, y, d, fl):
        for _ in range(200):
            if (x, y) in switches:
                f = switches[(x, y)]
                fl = fl ^ {f}
            if g[y][x] not in slide:
                return x, y, fl
            dx, dy = DIRS4[d]
            if blocked(x + dx, y + dy, fl):
                return x, y, fl
            x, y = x + dx, y + dy
        return x, y, fl

    s0 = (start[0], start[1], frozenset())
    prev = {s0: None}
    q = deque([s0])
    while q:
        st = q.popleft()
        x, y, fl = st
        if goal_fn(x, y):
            route, cur = [], st
            while prev[cur]:
                cur, d = prev[cur]
                route.append(d)
            return len(route), route[::-1], len(prev)
        for d, (dx, dy) in DIRS4.items():
            if blocked(x + dx, y + dy, fl):
                continue
            nx, ny, nf = settle(x + dx, y + dy, d, fl)
            ns = (nx, ny, frozenset(nf))
            if ns not in prev:
                prev[ns] = (st, d)
                q.append(ns)
    return None


def ice_rink(W, rows, entry_cols, exit_col, seed_base, want=(7, 11), density=0.16, avoid=()):
    """Search seeds for a rock layout on a W-wide, `rows`-tall ice rink: you step in from below at one of
    entry_cols and must come out of the top at exit_col. Returns (grid rows, presses)."""
    best = None
    for seed in range(seed_base, seed_base + 1500):
        rnd = random.Random(seed)
        g = [['x'] + ['i'] * (W - 2) + ['x'] for _ in range(rows)]
        for y in range(rows):
            for x in range(1, W - 1):
                if rnd.random() < density and (x, y) not in avoid:
                    g[y][x] = 'r'
        full = [['x'] * W] + g + [['x'] * W]                 # wall above (with the exit) and below (with the entries)
        full[0][exit_col] = '.'
        for c in entry_cols:
            full[-1][c] = '.'
        if any(full[-2][c] == 'r' for c in entry_cols) or full[1][exit_col] == 'r':
            continue
        res = [ice_solve(full, (c, rows + 1), lambda x, y: (x, y) == (exit_col, 0)) for c in entry_cols]
        res = [r for r in res if r]
        if not res:
            continue
        n = min(r[0] for r in res)
        if want[0] <= n <= want[1]:
            score = n * 10 + min(r[2] for r in res) / 10     # longer, and more places to get lost in
            if best is None or score > best[0]:
                best = (score, [row[:] for row in g], n)
    assert best, 'no rink found'
    return best[1], best[2]


# ── 5. Rime: two ice rinks ───────────────────────────────────────────────────
def frostspire_trial():
    W = 19
    lower, n1 = ice_rink(W, 6, [8, 9, 10], 3, 100, want=(6, 10))
    upper, n2 = ice_rink(W, 6, [4, 14], 15, 5000, want=(7, 12))
    gaps = lambda cols: ''.join('.' if x in cols else 'x' for x in range(W))
    rows = ['W' * W, 'W' * W, '.' * W, '.' * W,        # rows 2–3: Hale's ledge
            gaps([15])]                                 # row 4: the only way off the upper rink
    rows += [''.join(r) for r in upper]                # rows 5–10
    rows += [gaps([4, 14])]                            # row 11: two ways onto the upper rink
    rows += ['x' + '.' * (W - 2) + 'x'] * 2            # rows 12–13: the rest ledge in the middle
    rows += [gaps([3])]                                # row 14: the only way off the lower rink
    rows += [''.join(r) for r in lower]                # rows 15–20
    rows += [gaps([8, 9, 10]), gaps([8, 9, 10]), gaps([]).replace('x', 'm', 0)]
    rows[-1] = 'xxxxxxxxmmxxxxxxxxx'
    adepts = [('fs_adept_1', 'skier', 7, 12, 'down', 3), ('fs_adept_2', 'hiker', 11, 12, 'down', 3),
              ('fs_adept_3', 'skier', 16, 3, 'left', 3)]
    objs = ['furn 1 2 statue', 'furn 17 2 statue', 'furn 5 2 statue', 'furn 13 2 statue']
    m = room('frostspire_trial', 'Frostspire', 'Frost', rows, ('hale', 'hale', 9, 2), adepts,
             (10, 22, "Brr! Hale's hall is solid ice. Once you start sliding, you don't stop till you hit something! Her Frost Morphs hate Ember, Brawl, Stone and Iron."),
             objs)
    return m


# ── 6. Wyrm: rift-glass slides with crystal gates you switch from the ice ────
def riftgate_trial():
    W, R = 21, 11                                    # rink rows 5–15
    exit_col, entries = 10, [16]
    best = None
    for seed in range(20000, 23000):
        rnd = random.Random(seed)
        g = [['x'] + ['j'] * (W - 2) + ['x'] for _ in range(R)]
        for y in range(R):
            for x in range(1, W - 1):
                if rnd.random() < 0.13:
                    g[y][x] = 'x'
        full = [['x'] * W] + g + [['x'] * W]
        full[0][exit_col] = '.'
        for c in entries:
            full[-1][c] = '.'
        if full[1][exit_col] != 'j' or any(full[-2][c] != 'j' for c in entries):
            continue
        free = [(x, y + 1) for y in range(R) for x in range(1, W - 1) if g[y][x] == 'j']
        pa, pb = rnd.sample(free, 2)
        gb = rnd.sample([t for t in free if t not in (pa, pb)], 3)
        switches = {pa: 'rg_a', pb: 'rg_b'}
        gates = {(exit_col, 0): (lambda fl: 'rg_a' in fl)}
        for t in gb:
            gates[t] = (lambda fl: 'rg_b' in fl)
        goal = lambda x, y: (x, y) == (exit_col, 0)
        sols = [ice_solve(full, (c, R + 1), goal, switches=switches, gates=gates) for c in entries]
        sols = [s_ for s_ in sols if s_]
        if not sols:
            continue
        n = min(s_[0] for s_ in sols)
        # without the switches it must be impossible, and both switches must matter
        no_b = [ice_solve(full, (c, R + 1), goal, switches={pa: 'rg_a'}, gates=gates) for c in entries]
        if any(no_b):
            continue
        if 12 <= n <= 20:
            score = n * 10 + min(s_[2] for s_ in sols) / 20
            if best is None or score > best[0]:
                best = (score, [r[:] for r in g], pa, pb, gb, n)
    assert best, 'no Wyrm rink found'
    _, g, pa, pb, gb, n = best
    gaps = lambda cols: ''.join('.' if x in cols else 'x' for x in range(W))
    rows = ['W' * W, 'W' * W, '#' + '.' * (W - 2) + '#', '#' + '.' * (W - 2) + '#', gaps([exit_col])]
    rows += [''.join(r) for r in g]
    rows += [gaps(entries)]
    rows += ['#' + '.' * (W - 2) + '#', '#' + '.' * (W - 2) + '#', '#########..##########'[:W]]
    rows[-1] = '#' * 9 + 'mm' + '#' * (W - 11)
    gate = lambda x, y, flag: f'gate {x} {y} open={flag} frame=gate_crystal openframe=gate_crystal_open'
    objs = [gate(exit_col, 4, 'rg_a')] + [gate(x, y + 4, 'rg_b') for (x, y) in gb]
    for (x, y), flag, col in [(pa, 'rg_a', 'a'), (pb, 'rg_b', 'b')]:
        objs += [f'trigger {x} {y + 4} script=trial.flip flag={flag}', f'plate {x} {y + 4} on={flag} frame=plate_rift_off onframe=plate_rift_{col}']
    objs += ['furn 1 2 pillar', 'furn 19 2 pillar', 'furn 7 2 banner', 'furn 13 2 banner']
    adepts = [('rg_adept_1', 'ace', 12, 17, 'down', 3), ('rg_adept_2', 'ace_b', 14, 18, 'up', 3),
              ('rg_adept_3', 'guard', 12, 3, 'left', 3)]
    m = room('riftgate_trial', 'Riftgate', 'Drake', rows, ('seren', 'seren', 10, 2), adepts,
             (7, 18, "This is it — the Wyrm Trial. The floor is rift-glass: you slide on it. Glide over a glowing seal to switch the crystal gates — the violet seal works Seren's door, the gold one the gates on the glass. Frost is your best weapon against Drake Morphs."),
             objs)
    return m
