"""Tiny DSL for authoring Tiamat map sources (.map files) from Python.

    m = M('rootmere', 34, 26, name='Rootmere', music='rootmere', battle='meadow')
    m.border()                     # 2-thick tree border
    m.rect(16, 0, 17, 25, ':')     # path
    m.obj('npc 5 6 id=mum sprite=mum text="Hello!"')
    m.save()
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'maps')


class M:
    def __init__(self, id, w, h, fill='.', kind='route', **props):
        self.id, self.w, self.h = id, w, h
        self.kind = kind
        self.g = [[fill] * w for _ in range(h)]
        self.props = {'id': id, 'kind': kind, **props}
        self.objs = []

    # ── painting ──
    def put(self, x, y, ch):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.g[y][x] = ch

    def get(self, x, y):
        return self.g[y][x] if 0 <= x < self.w and 0 <= y < self.h else None

    def rect(self, x0, y0, x1, y1, ch):
        for y in range(min(y0, y1), max(y0, y1) + 1):
            for x in range(min(x0, x1), max(x0, x1) + 1):
                self.put(x, y, ch)
        return self

    def frame(self, x0, y0, x1, y1, ch):
        for x in range(x0, x1 + 1):
            self.put(x, y0, ch); self.put(x, y1, ch)
        for y in range(y0, y1 + 1):
            self.put(x0, y, ch); self.put(x1, y, ch)
        return self

    def hline(self, y, x0, x1, ch):
        return self.rect(x0, y, x1, y, ch)

    def vline(self, x, y0, y1, ch):
        return self.rect(x, y0, x, y1, ch)

    def path(self, pts, ch=':', width=2):
        """Orthogonal polyline path through points, `width` tiles wide (extends right/down)."""
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            if x0 == x1:
                self.rect(x0, y0, x0 + width - 1, y1, ch)
            else:
                self.rect(x0, y0, x1, y0 + width - 1, ch)
        return self

    def stamp(self, x, y, rows):
        for dy, row in enumerate(rows):
            for dx, ch in enumerate(row):
                if ch != ' ':
                    self.put(x + dx, y + dy, ch)
        return self

    def border(self, t=2, ch='T', gaps=()):
        """Tree border t cells thick. gaps: list of (side, a, b) openings, e.g. ('n', 16, 17)."""
        for y in range(self.h):
            for x in range(self.w):
                if x < t or y < t or x >= self.w - t or y >= self.h - t:
                    self.g[y][x] = ch
        for side, a, b in gaps:
            for i in range(a, b + 1):
                for k in range(t):
                    if side == 'n': self.put(i, k, ':')
                    if side == 's': self.put(i, self.h - 1 - k, ':')
                    if side == 'w': self.put(k, i, ':')
                    if side == 'e': self.put(self.w - 1 - k, i, ':')
        return self

    def grove(self, x, y, w, h, ch='T'):
        """Block of trees (keeps 2×2 alignment by snapping to even coords)."""
        x0 = x - x % 2; y0 = y - y % 2
        return self.rect(x0, y0, x0 + w - 1, y0 + h - 1, ch)

    def scatter(self, pts, ch):
        for (x, y) in pts:
            self.put(x, y, ch)
        return self

    # ── objects ──
    def obj(self, line):
        self.objs.append(line)
        return self

    def npc(self, x, y, id, sprite, text=None, face='down', move='still', **kw):
        parts = [f'npc {x} {y} id={id} sprite={sprite} face={face} move={move}']
        if text is not None:
            parts.append('text=' + _q(text))
        for k, v in kw.items():
            parts.append(f'{k}={_q(v)}')
        return self.obj(' '.join(parts))

    def trainer(self, x, y, tid, sprite, face='down', sight=4, **kw):
        return self.npc(x, y, tid, sprite, face=face, trainer=tid, sight=sight, **kw)

    def sign(self, x, y, text, walk=False):
        return self.obj(f'prop {x} {y} sign text={_q(text)}' + (' walk=1' if walk else ''))

    def item(self, x, y, item, qty=1, hidden=False):
        return self.obj(f'item {x} {y} item={item} qty={qty} flag=item_{self.id}_{x}_{y}' + (' hidden=1' if hidden else ''))

    def trigger(self, x, y, script, w=1, h=1, once=None, cond=None):
        s = f'trigger {x} {y} script={script} w={w} h={h}'
        if once: s += f' once={once}'
        if cond: s += f' cond={_q(cond)}'
        return self.obj(s)

    def save(self):
        os.makedirs(OUT, exist_ok=True)
        lines = []
        for k, v in self.props.items():
            lines.append(f'{k}: {v}')
        lines.append('')
        lines.append('layout:')
        lines.extend(''.join(r) for r in self.g)
        lines.append('end')
        lines.append('')
        lines.append('objects:')
        lines.extend(self.objs)
        with open(os.path.join(OUT, f'{self.id}.map'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines) + '\n')
        return self


def _q(v):
    s = str(v)
    if any(c in s for c in ' "\'|=') or s == '':
        return '"' + s.replace('"', '\\"') + '"'
    return s


# Common interior templates ---------------------------------------------------
def haven(id, town, music='haven'):
    """Haven: healing counter, shop counter and storage PC corner."""
    m = M(id, 16, 11, kind='interior', name=f'{town} Haven', floor='mint', wall='teal', music=music)
    m.rect(0, 0, 15, 1, 'W')
    m.put(2, 1, 'w'); m.put(13, 1, 'w')
    m.rect(4, 4, 9, 4, '=')
    m.rect(11, 4, 14, 4, '=')
    m.put(7, 10, 'm'); m.put(8, 10, 'm')
    m.obj('furn 6 2 healer')
    m.obj('furn 12 2 shelf v=1')
    m.obj('furn 1 2 pc script=haven.pc')
    m.obj('furn 3 2 bookshelf v=3')
    m.obj('furn 3 3 plant'); m.obj('furn 10 4 plant'); m.obj('furn 15 4 plant')
    m.obj('furn 0 9 plant'); m.obj('furn 15 9 plant')
    m.obj('furn 1 7 table v=0'); m.obj('furn 1 6 chair'); m.obj('furn 3 7 chair')
    m.obj('furn 11 7 table v=0'); m.obj('furn 13 7 chair')
    m.obj('furn 6 6 rug')
    m.npc(7, 3, f'{id}_keeper', 'nurse', script='haven.heal', noturn='1', name='Haven Keeper')
    m.npc(12, 3, f'{id}_clerk', 'clerk', script='haven.shop', noturn='1', name='Clerk')
    return m


def house(id, name, wall='cream', floor='wood', variant=0, music='house'):
    m = M(id, 12, 9, kind='interior', name=name, floor=floor, wall=wall, music=music)
    m.rect(0, 0, 11, 1, 'W')
    m.put(3, 1, 'w'); m.put(8, 1, 'w')
    m.put(5, 8, 'm')
    if variant == 0:
        m.obj('furn 0 2 bookshelf v=1'); m.obj('furn 1 2 bookshelf v=2')
        m.obj('furn 6 4 table v=0'); m.obj('furn 5 4 chair'); m.obj('furn 8 4 chair')
        m.obj('furn 11 2 plant'); m.obj('furn 10 2 tv')
    elif variant == 1:
        m.obj('furn 0 2 fridge'); m.obj('furn 1 2 stove')
        m.obj('furn 4 5 table v=2'); m.obj('furn 9 2 bookshelf v=4'); m.obj('furn 11 6 plant')
        m.obj('furn 10 2 bed v=2')
    else:
        m.obj('furn 1 2 bed v=1'); m.obj('furn 3 2 bookshelf v=5'); m.obj('furn 7 4 table v=1')
        m.obj('furn 11 2 plant'); m.obj('furn 0 6 plant'); m.obj('furn 9 2 globe')
    return m


TRIAL_STYLE = {
    'Nature': dict(floor='wood', wall='green', deco='plant'),
    'Tide':   dict(floor='tile', wall='blue', deco='barrel'),
    'Static': dict(floor='lab', wall='white', deco='machine'),
    'Umbra':  dict(floor='chapel', wall='dark', deco='crystal'),
    'Frost':  dict(floor='ice', wall='ice', deco='statue'),
    'Drake':  dict(floor='arena', wall='stone', deco='pillar'),
}


def trial(id, town, type_, warden_id, warden_sprite, adepts, guide_text, light=None):
    """A Trial hall: carpet aisle, pillars, adepts beside the aisle, the Warden at the top.
    adepts: list of (trainer_id, sprite, x, y, face)."""
    st = TRIAL_STYLE[type_]
    W, H = 14, 18
    props = dict(name=f'{town} Trial Hall', floor=st['floor'], wall=st['wall'], music='trial', battle='arena')
    if light:
        props['light'] = light
    m = M(id, W, H, kind='interior', **props)
    m.rect(0, 0, W - 1, 1, 'W')
    m.put(3, 1, 'w'); m.put(10, 1, 'w')
    m.rect(6, 4, 7, H - 1, '_')
    m.put(6, H - 1, 'm'); m.put(7, H - 1, 'm')
    m.obj('furn 1 2 banner'); m.obj('furn 12 2 banner')
    m.obj('furn 5 2 statue'); m.obj('furn 8 2 statue')
    for y in (6, 10, 14):
        m.obj(f"furn 3 {y} {st['deco']}"); m.obj(f"furn 10 {y} {st['deco']}")
    m.obj('furn 0 16 plant'); m.obj('furn 13 16 plant')
    for (tid, spr, x, y, face) in adepts:
        m.trainer(x, y, tid, spr, face=face, sight=3)
    m.npc(6, 3, warden_id, warden_sprite, script=f'{id}.warden')
    m.npc(9, 15, f'{id}_guide', 'ace', text=guide_text)
    return m
