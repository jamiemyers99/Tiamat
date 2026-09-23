"""Overworld character sprites (16×24 frames, 4 directions × 3 walk frames).

Characters are composited from a head template (per hair style) and a body
template (per outfit style), then recoloured from a per-character palette.
Sheet layout per character: rows = down, left, right, up; cols = stand, stepA, stepB.
"""
from spr import Spr, C
from pal import hx, shift

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


def _rows_to_spr(rows, pal, y0=0, spr=None):
    s = spr or Spr(W, H)
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch != '.' and ch in pal:
                s.px(x, y + y0, pal[ch])
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
    # soft shadow
    for x in range(4, 12):
        s.px(x, 23, (20, 24, 34), 70)
    for x in range(3, 13):
        s.px(x, 22, (20, 24, 34), 50) if x in (3, 12) else None
    _rows_to_spr(brows, pal, 12, s)
    _rows_to_spr(hrows, pal, bob, s)
    if direction == 'right':
        s = s.flip()
    return s


def sheet(head, body, pal):
    """3 columns × 4 rows (down, left, right, up)."""
    out = Spr(W * 3, H * 4)
    for r, d in enumerate(['down', 'left', 'right', 'up']):
        for c in range(3):
            out.blit(frame(head, body, d, c, pal), c * W, r * H)
    return out


_check()
