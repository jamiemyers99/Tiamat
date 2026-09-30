"""Solve a Trial hall puzzle from its map source, using the game's movement rules.

    python3 tools/puzzle_check.py brindlewood_trial saltreach_trial ...

Rules modelled (same as WorldScene): walls/void/hedges/ice rocks/furniture/people are solid; on ice you keep
sliding the way you were going until blocked; a current carries you along the arrows until it can't; stepping
onto a warp pad teleports you (no slide on arrival); stepping onto a switch (trigger script=trial.flip flag=F)
toggles flag F; gates are solid unless their `open` condition holds.

Reports: whether the Warden can be reached, the fewest button presses to get there, and for each adept whether
you can reach the Warden without ever stepping into their line of sight (they should all be unavoidable).
"""
import os, sys, shlex
from collections import deque

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DIRS = {'up': (0, -1), 'down': (0, 1), 'left': (-1, 0), 'right': (1, 0)}
PUSH = {'8': 'up', '2': 'down', '4': 'left', '6': 'right'}
FLAT_FURN = {'rug', 'mat', 'stairs_up', 'stairs_down', 'pad'}
SOLID = set('Ww#hr=px')
FURN_SIZE = {'healer': (2, 1), 'shelf': (2, 1), 'capsule_table': (3, 1), 'banner': (1, 1), 'statue': (1, 1)}


def load(mid):
    lines = open(os.path.join(ROOT, 'tools', 'maps', f'{mid}.map'), encoding='utf-8').read().split('\n')
    layout, objs, sec, props = [], [], None, {}
    for raw in lines:
        s = raw.strip()
        if sec is None and ': ' in s and not s.endswith(':'):
            k, v = s.split(': ', 1)
            props[k] = v
        if sec == 'layout':
            if s == 'end':
                sec = None
            elif s:
                layout.append(raw.rstrip())
            continue
        if s == 'layout:':
            sec = 'layout'; continue
        if s == 'objects:':
            sec = 'objects'; continue
        if sec == 'objects' and s:
            p = shlex.split(s)
            kv = dict(a.split('=', 1) for a in p[3:] if '=' in a)
            args = [a for a in p[3:] if '=' not in a]
            objs.append((p[0], int(p[1]), int(p[2]), args, kv))
    return layout, objs, props


def cond(expr, flags):
    if not expr:
        return False
    if '|' in expr:
        return any(cond(e, flags) for e in expr.split('|'))
    if '&' in expr:
        return all(cond(e, flags) for e in expr.split('&'))
    if expr.startswith('!'):
        return not cond(expr[1:], flags)
    return expr in flags


def analyse(mid, verbose=False, plan=None):
    """plan=((x, y), flags): just return the button presses from there to the Warden (for playtests)."""
    L, objs, props = load(mid)
    done_flag = props.get('done')
    H, W = len(L), len(L[0])
    solid = set()
    people = {}
    gates = []
    pads = {}
    switches = {}
    warden = None
    for t, x, y, args, kv in objs:
        if t == 'furn':
            name = args[0] if args else ''
            if name not in FLAT_FURN:
                fw, fh = FURN_SIZE.get(name, (1, 1))
                for i in range(fw):
                    for j in range(fh):
                        solid.add((x + i, y + j))
        elif t == 'npc':
            people[(x, y)] = kv
            if kv.get('script', '').endswith('.warden'):
                warden = (x, y)
        elif t == 'gate':
            gates.append(((x, y), kv.get('open', '')))
        elif t == 'warp' and ':' in kv.get('to', '') and kv['to'].split(':')[0] == mid:
            tx, ty = map(int, kv['to'].split(':')[1].split(','))
            pads[(x, y)] = ((tx, ty), kv.get('cond', ''))
        elif t == 'trigger' and kv.get('script') == 'trial.flip':
            switches[(x, y)] = kv['flag']
    start = None
    for y in range(H):
        for x in range(W):
            if L[y][x] == 'm':
                start = (x, y - 1)
                break
        if start:
            break

    def blocked(x, y, flags):
        if not (0 <= x < W and 0 <= y < H):
            return True
        c = L[y][x]
        if c in SOLID or (x, y) in solid or (x, y) in people:
            return True
        for (g, oc) in gates:
            if g == (x, y) and not cond(oc, flags):
                return True
        return False

    def settle(x, y, d, flags, path):
        """After arriving on (x,y) moving d: apply pads, switches, ice and currents. Returns final state."""
        for _ in range(400):
            path.append((x, y))
            if (x, y) in pads and (not pads[(x, y)][1] or cond(pads[(x, y)][1], flags)):
                x, y = pads[(x, y)][0]
                path.append((x, y))
                return x, y, flags
            if (x, y) in switches:
                f = switches[(x, y)]
                flags = flags - {f} if f in flags else flags | {f}
            c = L[y][x]
            if done_flag and done_flag in flags:      # a won hall is powered down: nothing slides
                return x, y, flags
            nd = d if c in 'ij' else PUSH.get(c)
            if not nd:
                return x, y, flags
            dx, dy = DIRS[nd]
            if blocked(x + dx, y + dy, flags):
                return x, y, flags
            x, y, d = x + dx, y + dy, nd
        raise RuntimeError('endless slide')

    def solve(avoid=frozenset(), frm=None, flags0=frozenset(), goal=None):
        s0 = ((frm or start)[0], (frm or start)[1], frozenset(flags0))
        prev = {s0: None}
        q = deque([s0])
        goal = goal or (warden[0], warden[1] + 1)
        while q:
            x, y, flags = q.popleft()
            if (x, y) == goal:
                out, st = [], (x, y, flags)
                while prev[st]:
                    st, move = prev[st]
                    out.append(move)
                return out[::-1]
            for d, (dx, dy) in DIRS.items():
                nx, ny = x + dx, y + dy
                if blocked(nx, ny, flags):
                    continue
                trail = []
                fx, fy, ff = settle(nx, ny, d, flags, trail)
                if trail[-1] in avoid or (len(trail) == 1 and trail[0] in avoid):   # trainers only spot you where you stop
                    continue
                st = (fx, fy, frozenset(ff))
                if st not in prev:
                    prev[st] = ((x, y, flags), d)
                    q.append(st)
        return None

    if plan is not None:     # ((x, y), flags[, goal])
        return solve(frm=plan[0], flags0=plan[1], goal=plan[2] if len(plan) > 2 else None)
    sol = solve()
    print(f'== {mid} ({W}x{H}) start {start} warden {warden}')
    print(f'   solution: {len(sol) if sol else "NONE"} presses')
    if verbose and sol:
        print('   ', ' '.join(d[0] for d in sol))
    for (x, y), kv in people.items():
        if not kv.get('trainer'):
            continue
        dx, dy = DIRS[kv.get('face', 'down')]
        sight = set()
        for i in range(1, int(kv.get('sight', 4)) + 1):
            tx, ty = x + dx * i, y + dy * i
            if not (0 <= tx < W and 0 <= ty < H) or L[ty][tx] in SOLID or (tx, ty) in solid or (tx, ty) in people:
                break
            sight.add((tx, ty))
        ok = solve(frozenset(sight))
        print(f"   {kv['trainer']:<14} at {x},{y} facing {kv.get('face')}: {'can be avoided' if ok else 'unavoidable'}")
    if done_flag:
        # once won, the hall must be easy both ways: walk (or pad) in to the Warden and back out again
        fl = frozenset({done_flag})
        front = (warden[0], warden[1] + 1)
        inn, out = solve(flags0=fl), solve(frm=front, flags0=fl, goal=start)
        print(f'   after the Trial is won: in {len(inn) if inn is not None else "BLOCKED"} presses, '
              f'out {len(out) if out is not None else "BLOCKED"} presses')
        if inn is None or out is None or len(inn) > 4 or len(out) > 4:
            print('   !! a won Trial should have Warden\'s pads right by the entrance and the Warden')
    return sol


if __name__ == '__main__':
    v = '-v' in sys.argv
    for mid in [a for a in sys.argv[1:] if a != '-v']:
        analyse(mid, v)
