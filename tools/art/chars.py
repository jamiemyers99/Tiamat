"""Overworld character sprites (16×24 frames, 4 directions × 3 walk frames).

Characters are composited from a head template (per hair style) and a body
template (per outfit style), then recoloured from a per-character palette.
Sheet layout per character: rows = down, left, right, up; cols = stand, stepA, stepB.
"""
from spr import Spr, C
from pal import hx, shift, ramp

W, H = 16, 24

# ── Heads (12 rows) ──────────────────────────────────────────────────────────
# letters: o outline, s skin, S skin shade, e eye, h hair, H hair shade, i hair hi,
#          a accent(hat), A accent shade, j accent hi, w white
HEADS = {}

HEADS['short'] = {
    'down': [
        "................",
        "....oooooooo....",
        "...ohhhhhhhho...",
        "..ohhiihhhhhHo..",
        "..ohhhhhhhhhHo..",
        "..ohhshhhhshHo..",
        "..ohsssssssshHo.",
        "..ossesssseSso..",
        "..ossesssseSso..",
        "..oSssssssssSo..",
        "...oSssssssSo...",
        "....oooooooo....",
    ],
    'up': [
        "................",
        "....oooooooo....",
        "...ohhhhhhhho...",
        "..ohhiihhhhhHo..",
        "..ohhhhhhhhhHo..",
        "..ohhhhhhhhhHo..",
        "..ohhhhhhhhhHo..",
        "..oHhhhhhhhhHo..",
        "..oHHhhhhhhHHo..",
        "..oSHHHHHHHHSo..",
        "...oSSssssSSo...",
        "....oooooooo....",
    ],
    'left': [
        "................",
        ".....ooooooo....",
        "....ohhhhhhho...",
        "...ohiihhhhhHo..",
        "...ohhhhhhhhHo..",
        "..ohhhhhhhhhHo..",
        "..ossshhhhhhHo..",
        "..osesshhhhHHo..",
        "..osessShhhHo...",
        ".ossssSSShHHo...",
        "..oSssssSSo.....",
        "...ooooooo......",
    ],
}

HEADS['long'] = {
    'down': [
        "................",
        "....oooooooo....",
        "...ohhhhhhhho...",
        "..ohhiihhhhhHo..",
        "..ohhhhhhhhhHo..",
        "..ohhshhhhshHo..",
        ".ohhsssssssshHo.",
        ".ohssesssseSsHo.",
        ".ohssesssseSsHo.",
        ".ohSssssssssSHo.",
        ".ohhoSssssSoHHo.",
        ".oHHooooooooHHo.",
    ],
    'up': [
        "................",
        "....oooooooo....",
        "...ohhhhhhhho...",
        "..ohhiihhhhhHo..",
        "..ohhhhhhhhhHo..",
        ".ohhhhhhhhhhHHo.",
        ".ohhhhhhhhhhHHo.",
        ".ohhhhhhhhhhHHo.",
        ".oHhhhhhhhhhHHo.",
        ".oHHhhhhhhhHHHo.",
        ".oHHHhhhhhHHHHo.",
        "..ooooooooooooo.",
    ],
    'left': [
        "................",
        ".....ooooooo....",
        "....ohhhhhhho...",
        "...ohiihhhhhHo..",
        "...ohhhhhhhhHo..",
        "..ohhhhhhhhhHHo.",
        "..ossshhhhhhHHo.",
        "..osesshhhhHHHo.",
        "..osessShhhHHHo.",
        ".ossssSSShHHHHo.",
        "..oSssssSSoHHHo.",
        "...oooooooooooo.",
    ],
}

HEADS['cap'] = {
    'down': [
        "....oooooooo....",
        "...oaaaaaaaao...",
        "..oajjaaaaaaAo..",
        "..oaaaawwaaaAo..",
        "..oaaaaaaaaaAo..",
        ".oAAAAAAAAAAAAo.",
        "..ohsssssssshHo.",
        "..ossesssseSso..",
        "..ossesssseSso..",
        "..oSssssssssSo..",
        "...oSssssssSo...",
        "....oooooooo....",
    ],
    'up': [
        "....oooooooo....",
        "...oaaaaaaaao...",
        "..oajjaaaaaaAo..",
        "..oaaaaaaaaaAo..",
        "..oaaaaaaaaaAo..",
        "..oAAaaaaaaAAo..",
        "..ohhhhhhhhhHo..",
        "..oHhhhhhhhhHo..",
        "..oHHhhhhhhHHo..",
        "..oSHHHHHHHHSo..",
        "...oSSssssSSo...",
        "....oooooooo....",
    ],
    'left': [
        ".....ooooooo....",
        "....oaaaaaaao...",
        "...oajjaaaaaAo..",
        "...oaaaaaaaaAo..",
        "..oaaaaaaaaaAo..",
        "oAAAAAAAAhhhHo..",
        "..ossshhhhhhHo..",
        "..osesshhhhHHo..",
        "..osessShhhHo...",
        ".ossssSSShHHo...",
        "..oSssssSSo.....",
        "...ooooooo......",
    ],
}

HEADS['ponytail'] = {
    'down': [
        "................",
        "....oooooooo....",
        "...ohhhhhhhho...",
        "..ohhiihhhhhHo..",
        "..oaaaaaaaaaAo..",
        "..ohhshhhhshHo..",
        "..ohsssssssshHo.",
        "..ossesssseSso..",
        "..ossesssseSso..",
        "..oSssssssssSo..",
        "...oSssssssSo...",
        "....oooooooo....",
    ],
    'up': [
        "................",
        "....oooooooo....",
        "...ohhhhhhhho...",
        "..ohhiihhhhhHo..",
        "..oaaaaaaaaaAo..",
        "..ohhhhhhhhhHo..",
        "..ohhhhohhhhHo..",
        "..oHhhohhohhHo..",
        "..oHHhohhohHHo..",
        "..oSHHohhoHHSo..",
        "...oSSohhoSSo...",
        "....ooohhooo....",
    ],
    'left': [
        "................",
        ".....ooooooo....",
        "....ohhhhhhho...",
        "...ohiihhhhhHo..",
        "...oaaaaaaaaAoo.",
        "..ohhhhhhhhhHhho",
        "..ossshhhhhhHhho",
        "..osesshhhhHHoho",
        "..osessShhhHo.o.",
        ".ossssSSShHHo...",
        "..oSssssSSo.....",
        "...ooooooo......",
    ],
}

HEADS['hood'] = {
    'down': [
        "....oooooooo....",
        "...oaaaaaaaao...",
        "..oajjaaaaaaAo..",
        "..oaaaaaaaaaAo..",
        ".oaaaAAAAAAaaAo.",
        ".oaaAssssssAaAo.",
        ".oaAssssssssAAo.",
        ".oaAsesssseSAAo.",
        ".oaAsesssseSAAo.",
        ".oaASssssssSAAo.",
        ".oaaAoSsssSoAAo.",
        "..oooooooooooo..",
    ],
    'up': [
        "....oooooooo....",
        "...oaaaaaaaao...",
        "..oajjaaaaaaAo..",
        "..oaaaaaaaaaAo..",
        ".oaaaaaaaaaaAAo.",
        ".oaaaaaaaaaaAAo.",
        ".oaaaaaaaaaaAAo.",
        ".oAaaaaaaaaaAAo.",
        ".oAAaaaaaaaAAAo.",
        ".oAAAaaaaaAAAAo.",
        ".oAAAAAAAAAAAAo.",
        "..oooooooooooo..",
    ],
    'left': [
        ".....ooooooo....",
        "....oaaaaaaao...",
        "...oajjaaaaaAo..",
        "...oaaaaaaaaAo..",
        "..oaAaaaaaaaAAo.",
        "..oAssaaaaaaAAo.",
        "..ossAaaaaaaAAo.",
        "..oseAaaaaaAAAo.",
        "..osesAaaaaAAAo.",
        ".osssSAaaaAAAAo.",
        "..oSssoAAAAAAAo.",
        "...oooooooooooo.",
    ],
}

HEADS['bald'] = {  # elderly: little tuft of grey hair + beard option via hair colour
    'down': [
        "................",
        "................",
        "....oooooooo....",
        "...ossssssssS...",
        "..ohssssssssHo..",
        "..ohsssssssshHo.",
        "..ohsssssssshHo.",
        "..ossesssseSso..",
        "..osshhsshhSso..",
        "..oShhhhhhhhSo..",
        "...ohhhhhhhho...",
        "....oooooooo....",
    ],
    'up': [
        "................",
        "................",
        "....oooooooo....",
        "...ossssssssSo..",
        "..ossssssssssSo.",
        "..ohsssssssshHo.",
        "..ohhsssssshhHo.",
        "..oHhhhhhhhhHHo.",
        "..oHHhhhhhhHHo..",
        "..oSHHHHHHHHSo..",
        "...oSSssssSSo...",
        "....oooooooo....",
    ],
    'left': [
        "................",
        "................",
        ".....ooooooo....",
        "....ossssssSo...",
        "...ossssssssSo..",
        "..ossssssshhHo..",
        "..ossssshhhhHo..",
        "..osesshhhhHHo..",
        "..ohhhSShhhHo...",
        ".ohhhhhSShHHo...",
        "..ohhhhhSSo.....",
        "...ooooooo......",
    ],
}

HEADS['hat'] = {  # wide-brim hat (captain / hiker)
    'down': [
        "....oooooooo....",
        "...oaajjaaaAo...",
        "...oaaaaaaaAo...",
        "...oAAAAAAAAo...",
        ".oooaaaaaaaaooo.",
        "oaaaaaaaaaaaaaAo",
        ".oooAAAAAAAAooo.",
        "..ossesssseSso..",
        "..ossesssseSso..",
        "..oSssssssssSo..",
        "...oShhhhhhSo...",
        "....oooooooo....",
    ],
    'up': [
        "....oooooooo....",
        "...oaajjaaaAo...",
        "...oaaaaaaaAo...",
        "...oAAAAAAAAo...",
        ".oooaaaaaaaaooo.",
        "oaaaaaaaaaaaaaAo",
        ".oooAAAAAAAAooo.",
        "..ohhhhhhhhhHo..",
        "..oHHhhhhhhHHo..",
        "..oSHHHHHHHHSo..",
        "...oSSssssSSo...",
        "....oooooooo....",
    ],
    'left': [
        "....oooooooo....",
        "...oaajjaaaAo...",
        "...oaaaaaaaAo...",
        "...oAAAAAAAAo...",
        ".oooaaaaaaaaooo.",
        "oaaaaaaaaaaaaaAo",
        ".oooAAAAAAAAooo.",
        "..osesshhhhHHo..",
        "..osessShhhHo...",
        ".ossssSSShHHo...",
        "..oSssssSSo.....",
        "...ooooooo......",
    ],
}

HEADS['bun'] = {
    'down': [
        ".....oooooo.....",
        "....ohhhhiho....",
        "....oohhhhoo....",
        "...ohhhhhhhho...",
        "..ohhiihhhhhHo..",
        "..ohhshhhhshHo..",
        "..ohsssssssshHo.",
        "..ossesssseSso..",
        "..ossesssseSso..",
        "..oSssssssssSo..",
        "...oSssssssSo...",
        "....oooooooo....",
    ],
    'up': [
        ".....oooooo.....",
        "....ohhhhiho....",
        "....oohhhhoo....",
        "...ohhhhhhhho...",
        "..ohhiihhhhhHo..",
        "..ohhhhhhhhhHo..",
        "..ohhhhhhhhhHo..",
        "..oHhhhhhhhhHo..",
        "..oHHhhhhhhHHo..",
        "..oSHHHHHHHHSo..",
        "...oSSssssSSo...",
        "....oooooooo....",
    ],
    'left': [
        "........oooo....",
        ".......ohhiho...",
        ".....oooohhoo...",
        "....ohhhhhhho...",
        "...ohiihhhhhHo..",
        "..ohhhhhhhhhHo..",
        "..ossshhhhhhHo..",
        "..osesshhhhHHo..",
        "..osessShhhHo...",
        ".ossssSSShHHo...",
        "..oSssssSSo.....",
        "...ooooooo......",
    ],
}

HEADS['spiky'] = {
    'down': [
        "..o..o..o..o....",
        "..oho.ohoohoo...",
        "..ohhohhhohhho..",
        "..ohhiihhhhhHo..",
        "..ohhhhhhhhhHo..",
        "..ohhshhhhshHo..",
        "..ohsssssssshHo.",
        "..ossesssseSso..",
        "..ossesssseSso..",
        "..oSssssssssSo..",
        "...oSssssssSo...",
        "....oooooooo....",
    ],
    'up': [
        "..o..o..o..o....",
        "..oho.ohoohoo...",
        "..ohhohhhohhho..",
        "..ohhiihhhhhHo..",
        "..ohhhhhhhhhHo..",
        "..ohhhhhhhhhHo..",
        "..ohhhhhhhhhHo..",
        "..oHhhhhhhhhHo..",
        "..oHHhhhhhhHHo..",
        "..oSHHHHHHHHSo..",
        "...oSSssssSSo...",
        "....oooooooo....",
    ],
    'left': [
        "....o..o..o.....",
        "...ohoohoohoo...",
        "...ohhhhhhhhHo..",
        "..ohhiihhhhhHo..",
        "..ohhhhhhhhhHo..",
        "..ohhhhhhhhhHo..",
        "..ossshhhhhhHo..",
        "..osesshhhhHHo..",
        "..osessShhhHo...",
        ".ossssSSShHHo...",
        "..oSssssSSo.....",
        "...ooooooo......",
    ],
}

# ── Bodies (12 rows) ─────────────────────────────────────────────────────────
# c top, C top shade, x top hi, p legs, P legs shade, b shoes, k belt/strap, s/S hands
BODIES = {}
BODIES['casual'] = {
    'down': [
        [   # stand
            "....oCccccCo....",
            "...occxcckcco...",
            "..occcccckcCco..",
            "..osoccckcccCso.",
            "..osocckcccCoso.",
            "..oSooccccccoSo.",
            "...o.okkkkko.o..",
            ".....opppPpo....",
            ".....oppoPPo....",
            ".....oppoPPo....",
            ".....obboBBo....",
            "......oo.oo.....",
        ],
        [   # step A (left foot forward)
            "....oCccccCo....",
            "...occxcckcco...",
            "..occcccckcCco..",
            "..osoccckcccCso.",
            "..osocckcccCoso.",
            "..oSooccccccoSo.",
            "...o.okkkkko.o..",
            ".....opppPpo....",
            ".....oppoPPo....",
            ".....obboPPo....",
            "......oo.BBo....",
            ".........oo.....",
        ],
    ],
    'up': [
        [
            "....oCccccCo....",
            "...occcccccco...",
            "..occcccccccCo..",
            "..osocccccccCso.",
            "..osoccccccCoso.",
            "..oSooccccccoSo.",
            "...o.okkkkko.o..",
            ".....opppPpo....",
            ".....oppoPPo....",
            ".....oppoPPo....",
            ".....obboBBo....",
            "......oo.oo.....",
        ],
        [
            "....oCccccCo....",
            "...occcccccco...",
            "..occcccccccCo..",
            "..osocccccccCso.",
            "..osoccccccCoso.",
            "..oSooccccccoSo.",
            "...o.okkkkko.o..",
            ".....opppPpo....",
            ".....oppoPPo....",
            ".....obboPPo....",
            "......oo.BBo....",
            ".........oo.....",
        ],
    ],
    'left': [
        [
            ".....oCcccCo....",
            "....occxcccCo...",
            "....occcccCCo...",
            "....ocsscccCo...",
            "....ocsScccCo...",
            "....ooSSccCCo...",
            ".....okkkkko....",
            ".....opppPPo....",
            ".....opppPPo....",
            ".....oppPPPo....",
            "....obbbBBo.....",
            ".....ooooo......",
        ],
        [
            ".....oCcccCo....",
            "....occxcccCo...",
            "....occcccCCo...",
            "...osscccccCo...",
            "...oSScccCCo....",
            "....ooccccCo....",
            ".....okkkkko....",
            "....oppppPPPo...",
            "...opppoopPPo...",
            "..obbpo..oPPo...",
            "..oobo...oBBo...",
            "...oo.....oo....",
        ],
        [
            ".....oCcccCo....",
            "....occxcccCo...",
            "....occcccCCSo..",
            "....occcccCCSo..",
            "....occcccCCo...",
            "....ooccccCo....",
            ".....okkkkko....",
            ".....opppPPPo...",
            ".....oppPooPPo..",
            ".....obbo..oPPo.",
            ".....obbo...oBo.",
            "......oo.....o..",
        ],
    ],
}

BODIES['robe'] = {
    'down': [
        [
            "....oCccccCo....",
            "...occxcccccco..",
            "..occccckccccCo.",
            "..osccccckcccso.",
            "..osccccckcccso.",
            "..oSccccckcccSo.",
            "...occccckcccCo.",
            "...occccccccCCo.",
            "...occccccccCCo.",
            "..occccccccCCCCo",
            "..oCCCCCCCCCCCo.",
            "...obbo...obbo..",
        ],
        [
            "....oCccccCo....",
            "...occxcccccco..",
            "..occccckccccCo.",
            "..osccccckcccso.",
            "..osccccckcccso.",
            "..oSccccckcccSo.",
            "...occccckcccCo.",
            "...occccccccCCo.",
            "...occccccccCCo.",
            "..occccccccCCCCo",
            "..oCCCCCCCCCCCo.",
            "...obbo.........",
        ],
    ],
    'up': [
        [
            "....oCccccCo....",
            "...occccccccco..",
            "..occcccccccccCo",
            "..osccccccccccso",
            "..osccccccccccso",
            "..oSccccccccccSo",
            "...occccccccccCo",
            "...occccccccCCo.",
            "...occccccccCCo.",
            "..occccccccCCCCo",
            "..oCCCCCCCCCCCo.",
            "...obbo...obbo..",
        ],
        [
            "....oCccccCo....",
            "...occccccccco..",
            "..occcccccccccCo",
            "..osccccccccccso",
            "..osccccccccccso",
            "..oSccccccccccSo",
            "...occccccccccCo",
            "...occccccccCCo.",
            "...occccccccCCo.",
            "..occccccccCCCCo",
            "..oCCCCCCCCCCCo.",
            "...obbo.........",
        ],
    ],
    'left': [
        [
            ".....oCcccCo....",
            "....occxcccCo...",
            "....occcccCCo...",
            "....ocsscccCo...",
            "....ocsScccCo...",
            "....occSccCCo...",
            "....okkkkkkko...",
            "....occcccCCo...",
            "...occcccCCCCo..",
            "...occccCCCCCo..",
            "...oCCCCCCCCo...",
            "....obbo.obo....",
        ],
        [
            ".....oCcccCo....",
            "....occxcccCo...",
            "....occcccCCo...",
            "...osscccccCo...",
            "...oSScccCCo....",
            "....occcccCCo...",
            "....okkkkkkko...",
            "....occcccCCo...",
            "...occcccCCCCo..",
            "..occccCCCCCCo..",
            "..oCCCCCCCCCo...",
            "..obbo....obo...",
        ],
        [
            ".....oCcccCo....",
            "....occxcccCo...",
            "....occcccCCSo..",
            "....occcccCCSo..",
            "....occcccCCo...",
            "....occcccCCo...",
            "....okkkkkkko...",
            "....occcccCCo...",
            "...occcccCCCCo..",
            "...occccCCCCCCo.",
            "...oCCCCCCCCCCo.",
            "....obo....obbo.",
        ],
    ],
}


def _check():
    for name, dirs in HEADS.items():
        for d, rows in dirs.items():
            assert len(rows) == 12, (name, d, len(rows))
            for r in rows:
                assert len(r) == 16, (name, d, r, len(r))
    for name, dirs in BODIES.items():
        for d, frames in dirs.items():
            for f in frames:
                assert len(f) == 12, (name, d)
                for r in f:
                    assert len(r) == 16, (name, d, r, len(r))


# ── Palettes ────────────────────────────────────────────────────────────────
SKIN = {'light': '#f3cfae', 'tan': '#d9a577', 'brown': '#a8704a', 'deep': '#6e4632', 'pale': '#f6ddc8'}


def make_palette(skin='light', hair='#6b4a2e', top='#3f6fc8', legs='#3a3f58', shoes='#2a2230', accent='#c8473f', belt=None):
    sk = hx(SKIN.get(skin, skin))
    hr = hx(hair); tp = hx(top); lg = hx(legs); sh = hx(shoes); ac = hx(accent)
    return {
        'o': (34, 30, 44), 's': sk, 'S': shift(sk, -0.1, 0.05, 10), 'e': (34, 30, 44), 'w': (250, 250, 250),
        'h': hr, 'H': shift(hr, -0.12, 0, 10), 'i': shift(hr, 0.14, 0, -8),
        'a': ac, 'A': shift(ac, -0.13, 0, 10), 'j': shift(ac, 0.16, 0, -6),
        'c': tp, 'C': shift(tp, -0.12, 0, 10), 'x': shift(tp, 0.14, 0, -6),
        'p': lg, 'P': shift(lg, -0.1, 0, 10), 'b': sh, 'B': shift(sh, -0.08),
        'k': hx(belt) if belt else shift(tp, -0.22, 0, 10), 'r': (240, 140, 140),
    }


def _rows_to_spr(rows, pal, y0=0, spr=None, mat=None):
    s = spr or Spr(W, H)
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch != '.' and ch in pal:
                s.px(x, y + y0, pal[ch])
                if mat is not None and 0 <= y + y0 < H:
                    mat[y + y0][x] = ch
    return s


# ── 3D shading pass ─────────────────────────────────────────────────────────
# Palette letters grouped into materials; each material is shaded as its own rounded volume.
GROUPS = {'s': 'skin', 'S': 'skin', 'h': 'hair', 'H': 'hair', 'i': 'hair', 'a': 'hat', 'A': 'hat', 'j': 'hat',
          'c': 'top', 'C': 'top', 'x': 'top', 'k': 'belt', 'p': 'legs', 'P': 'legs', 'b': 'shoes', 'B': 'shoes'}
BASE_KEY = {'skin': 's', 'hair': 'h', 'hat': 'a', 'top': 'c', 'belt': 'k', 'legs': 'p', 'shoes': 'b'}
# authored shade letters keep their meaning: darker / lighter than the base tone
LETTER_LEVEL = {'S': -1, 'H': -1, 'A': -1, 'C': -1, 'P': -1, 'B': -1, 'i': 1, 'j': 1, 'x': 1}
GLOSSY = {'hair': 1, 'hat': 1, 'shoes': 1}
LX, LY = -0.62, -0.78          # light from the top-left


def _dist(mask):
    """City-block distance from each masked pixel to the nearest unmasked pixel (BFS)."""
    Hh, Ww = len(mask), len(mask[0])
    INF = 99
    d = [[INF if mask[y][x] else 0 for x in range(Ww)] for y in range(Hh)]
    q = [(x, y) for y in range(Hh) for x in range(Ww) if not mask[y][x]]
    # pixels on the canvas edge count as next to the outside
    for y in range(Hh):
        for x in range(Ww):
            if mask[y][x] and (x in (0, Ww - 1) or y in (0, Hh - 1)):
                d[y][x] = 1
                q.append((x, y))
    head = 0
    while head < len(q):
        x, y = q[head]; head += 1
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            xx, yy = x + dx, y + dy
            if 0 <= xx < Ww and 0 <= yy < Hh and d[yy][xx] > d[y][x] + 1:
                d[yy][xx] = d[y][x] + 1
                q.append((xx, yy))
    return d


def shade3d(s, mat, pal):
    """Re-light a composed 16×24 frame so every part reads as a rounded 3D form:
    lit top-left, shadowed bottom-right, rim-lit edge, glossy highlights on hair and shoes,
    a contact shadow under the head and colour-matched (sel-out) outlines."""
    ramps = {}
    for g, key in BASE_KEY.items():
        ramps[g] = ramp(pal[key], 7, 0.15, hue=16, sat=0.05)
    out = s.a.copy()
    for g in ramps:
        mask = [[GROUPS.get(mat[y][x]) == g for x in range(W)] for y in range(H)]
        if not any(any(r) for r in mask):
            continue
        d = _dist(mask)
        for y in range(H):
            for x in range(W):
                if not mask[y][x]:
                    continue
                hgt = min(d[y][x], 4)
                # slope of the pseudo height field → surface normal
                def hv(xx, yy):
                    return min(d[yy][xx], 4) if 0 <= xx < W and 0 <= yy < H and mask[yy][xx] else 0
                gx = (hv(x + 1, y) - hv(x - 1, y)) / 2
                gy = (hv(x, y + 1) - hv(x, y - 1)) / 2
                nx, ny, nz = -gx, -gy, 1.1
                ln = (nx * nx + ny * ny + nz * nz) ** 0.5
                nx, ny, nz = nx / ln, ny / ln, nz / ln
                lam = nx * LX + ny * LY + nz * 0.55
                lvl = 3 + LETTER_LEVEL.get(mat[y][x], 0)
                if lam > 0.62:
                    lvl += 1
                elif lam < 0.2:
                    lvl -= 1
                if lam < -0.05:
                    lvl -= 1
                # the very top-left rim catches extra light; glossy materials get a highlight
                if GLOSSY.get(g) and lam > 0.8 and hgt <= 2:
                    lvl += 1
                # soft falloff toward the bottom of clothes (ambient occlusion)
                if hv(x, y + 1) == 0 and hv(x, y - 1) > 0 and g in ('top', 'legs'):
                    lvl -= 1
                lvl = max(0, min(6, lvl))
                if g == 'skin':   # faces stay clean and bright
                    lvl = max(2, min(4, lvl))
                out[y, x] = (*ramps[g][lvl], 255)
    # the head throws a little shadow onto the shoulders / top of the body
    head_bottom = {}
    for x in range(W):
        for y in range(H):
            if GROUPS.get(mat[y][x]) in ('skin', 'hair', 'hat') and y < 13:
                head_bottom[x] = y
    for x, yb in head_bottom.items():
        for yy in (yb + 2, yb + 3):
            if 0 <= yy < H and GROUPS.get(mat[yy][x]) in ('top', 'belt') and x >= 5:
                r = ramps[GROUPS[mat[yy][x]]]
                cur = tuple(int(v) for v in out[yy, x][:3])
                idx = min(range(7), key=lambda i: sum((a - b) ** 2 for a, b in zip(r[i], cur)))
                out[yy, x] = (*r[max(0, idx - 1)], 255)
    # sel-out: outlines take a dark tint of the colour they wrap
    for y in range(H):
        for x in range(W):
            if mat[y][x] != 'o':
                continue
            best = None
            for dx, dy in ((0, -1), (-1, 0), (1, 0), (0, 1)):
                xx, yy = x + dx, y + dy
                if 0 <= xx < W and 0 <= yy < H and GROUPS.get(mat[yy][xx]):
                    best = GROUPS[mat[yy][xx]]
                    break
            if best:
                o = pal['o']
                t = 0.22 if best == 'skin' else 0.42
                c = tuple(int(o[i] * (1 - t) + ramps[best][0][i] * t) for i in range(3))
                out[y, x] = (*c, 255)
    s.a = out
    return s


def frame(head, body, direction, idx, pal):
    """idx: 0 stand, 1 stepA, 2 stepB."""
    d = 'left' if direction in ('left', 'right') else direction
    hrows = HEADS[head][d]
    brows_set = BODIES[body][d]
    flip = False
    if d in ('down', 'up'):
        brows = brows_set[0] if idx == 0 else brows_set[1]
        if idx == 2:
            brows = [r[::-1] for r in brows]
    else:
        brows = brows_set[idx]
    bob = 1 if idx in (1, 2) else 0
    s = Spr(W, H)
    mat = [['.'] * W for _ in range(H)]
    _rows_to_spr(brows, pal, 12, s, mat)
    _rows_to_spr(hrows, pal, bob, s, mat)
    if direction == 'right':
        s = s.flip()
        mat = [row[::-1] for row in mat]
    shade3d(s, mat, pal)
    # soft oval ground shadow (behind the feet)
    for x in range(3, 13):
        for y, a in ((22, 60 if 4 <= x <= 11 else 0), (23, 95 if 4 <= x <= 11 else 45)):
            if a and s.a[y, x, 3] == 0:
                s.px(x, y, (18, 20, 34), a)
    return s


def sheet(head, body, pal):
    """3 columns × 4 rows (down, left, right, up)."""
    out = Spr(W * 3, H * 4)
    for r, d in enumerate(['down', 'left', 'right', 'up']):
        for c in range(3):
            out.blit(frame(head, body, d, c, pal), c * W, r * H)
    return out


_check()
