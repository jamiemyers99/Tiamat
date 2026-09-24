"""Build the character spritesheet (public/assets/sprites/chars.png + chars.json).

Each character occupies one row of 12 frames (32×32, see chars.py for the frame contract):
  down×3, left×3, right×3, up×3   (stand, stepA, stepB)
chars.png is 384 px wide × 32 px per character; chars.json maps id → row index.

    python3 tools/art/build_chars.py
"""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
from chars import frame, make_palette, W, H, FEET_Y
from spr import Spr

P = make_palette
HERO = {'gear': ('pack',)}      # optional extras: the heroes carry a backpack in their accent colour
# id: (head, body, palette[, extras])
ROSTER = {
    # player styles
    'player_a':  ('cap', 'casual', P('light', '#6b4a2e', '#3f6fc8', '#34394f', '#2a2230', '#d8453d'), HERO),
    'player_b':  ('ponytail', 'casual', P('light', '#7a3a2a', '#d8453d', '#34394f', '#2a2230', '#f2c14e'), HERO),
    'player_c':  ('cap', 'casual', P('brown', '#2a1f1a', '#2aa19a', '#3a3040', '#2a2230', '#f2c14e'), HERO),
    'player_d':  ('ponytail', 'casual', P('deep', '#1e1414', '#7a52b0', '#34394f', '#2a2230', '#6fe0c8'), HERO),
    # extra player styles so boys and girls each have four to choose from
    'player_e':  ('spiky', 'casual', P('tan', '#3a2a1a', '#3a8a4a', '#2a2f40', '#2a2230', '#f2c14e'), HERO),
    'player_f':  ('long', 'casual', P('light', '#e8b04a', '#e27a8a', '#34394f', '#2a2230', '#6fe0c8'), HERO),
    'player_g':  ('short', 'casual', P('deep', '#1a1414', '#e07a3a', '#2a2f40', '#2a2230', '#3f6fc8'), HERO),
    'player_h':  ('bun', 'casual', P('brown', '#2a1a14', '#2aa19a', '#34394f', '#2a2230', '#f5c542'), HERO),
    # story cast
    'mum':       ('bun', 'robe', P('light', '#8a5a3a', '#d88a6a', '#6a4a3a', '#3a2a2a', '#d88a6a')),
    'marsh':     ('long', 'robe', P('light', '#d8d8e4', '#f2f2f4', '#5a6a8a', '#3a3a44', '#6fa0d8', '#8aa4c8')),
    'wren':      ('spiky', 'casual', P('light', '#c86a3a', '#4a9a52', '#3a3a50', '#2a2230', '#2a2a2a')),
    'wren_dark': ('spiky', 'robe', P('light', '#c86a3a', '#1f4a4a', '#1a3434', '#1a1a24', '#1f5a5a', '#6fe0c8')),
    'assistant': ('short', 'casual', P('tan', '#2a2a36', '#eef0f2', '#4a5a7a', '#2a2230', '#2a2a2a')),
    'nurse':     ('bun', 'casual', P('light', '#e27a8a', '#f4f4f4', '#e2a0a8', '#8a6a6a', '#e2555f', '#e2555f')),
    'clerk':     ('cap', 'casual', P('tan', '#3a2a24', '#2aa19a', '#3a3f58', '#2a2230', '#2aa19a')),
    'acolyte':   ('hood', 'robe', P('light', '#222', '#1f4f52', '#16383a', '#1a1a24', '#1f4f52', '#6fe0c8')),
    'acolyte_b': ('hood', 'robe', P('tan', '#222', '#1f4f52', '#16383a', '#1a1a24', '#1f4f52', '#6fe0c8')),
    'vesk':      ('hood', 'robe', P('pale', '#222', '#3a2a5a', '#2a1f40', '#1a1a24', '#4a2f78', '#c89aff')),
    'maren':     ('long', 'robe', P('light', '#2a3a6a', '#1c2a4a', '#141e36', '#1a1a24', '#2a3a6a', '#6fe0c8')),
    'oriel':     ('hood', 'robe', P('pale', '#eee', '#e8e4d8', '#b8b0a0', '#3a3a44', '#f2f0e8', '#e2b64a')),
    # wardens (trial leaders)
    'mossa':     ('bun', 'robe', P('tan', '#4a6a2a', '#5a9a4a', '#3a5a2a', '#2a2a1a', '#8ac84a', '#c8a04a')),
    'brann':     ('hat', 'casual', P('light', '#e8e8e8', '#2a3f7a', '#2a2a38', '#1a1a1a', '#1c2440')),
    'iskra':     ('spiky', 'casual', P('light', '#f2c14e', '#e07a3a', '#3a3f58', '#2a2230', '#2a2a2a', '#f5c542')),
    'morrow':    ('long', 'robe', P('pale', '#1e1a2a', '#4a2f78', '#2a1f40', '#1a1a24', '#4a2f78', '#b89aff')),
    'hale':      ('hat', 'casual', P('brown', '#2a1f1a', '#6a8ac8', '#3a3a50', '#2a2230', '#8a5a3a')),
    'seren':     ('long', 'robe', P('light', '#c8453d', '#8a2a2a', '#5a1a1a', '#1a1a24', '#c8453d', '#f2c14e')),
    # townsfolk & trainers
    'kid':       ('spiky', 'casual', P('light', '#6b4a2e', '#e2b64a', '#3a5a8a', '#2a2230', '#2a2a2a')),
    'kid_b':     ('ponytail', 'casual', P('tan', '#2a1a1a', '#e27a8a', '#3a3f58', '#2a2230', '#6fe0c8')),
    'lass':      ('long', 'casual', P('light', '#e8b04a', '#e27a8a', '#4a3a6a', '#2a2230', '#e27a8a')),
    'youth':     ('cap', 'casual', P('light', '#3a2a24', '#4a9a52', '#5a4a3a', '#2a2230', '#e2b64a')),
    'hiker':     ('hat', 'casual', P('tan', '#3a2a1a', '#8a6a3a', '#4a4a3a', '#2a2230', '#6a4a2a')),
    'sailor':    ('cap', 'casual', P('light', '#2a2a2a', '#f4f4f4', '#2a3f7a', '#1a1a1a', '#2a3f7a')),
    'fisher':    ('hat', 'casual', P('brown', '#2a2a2a', '#3a7a8a', '#3a4a4a', '#2a2230', '#c8a04a')),
    'scholar':   ('short', 'robe', P('light', '#6a6a7a', '#6a4a8a', '#4a3a5a', '#2a2230', '#6a4a8a')),
    'miner':     ('hat', 'casual', P('tan', '#2a2a2a', '#e0a03a', '#3a3a44', '#2a2230', '#f2c14e')),
    'engineer':  ('short', 'casual', P('light', '#8a5a3a', '#e07a3a', '#3a3f58', '#2a2230', '#2a2a2a')),
    'mystic':    ('hood', 'robe', P('light', '#222', '#6a4a8a', '#3a2a5a', '#1a1a24', '#6a4a8a', '#c89aff')),
    'skier':     ('cap', 'casual', P('light', '#e8b04a', '#e24a4a', '#2a3f7a', '#2a2230', '#f4f4f4')),
    'ranger':    ('hat', 'casual', P('tan', '#3a2a1a', '#4a6a3a', '#3a3a2a', '#2a2230', '#6a8a3a')),
    'gent':      ('short', 'robe', P('light', '#8a8a9a', '#2a2a3a', '#1a1a24', '#1a1a1a', '#2a2a3a', '#c8a04a')),
    'lady':      ('bun', 'robe', P('light', '#e8c86a', '#8a52b0', '#5a3a7a', '#2a2230', '#8a52b0', '#f2c14e')),
    'elder':     ('bald', 'casual', P('pale', '#d8d8e0', '#8a6a4a', '#4a4a58', '#2a2230', '#2a2a2a')),
    'elder_b':   ('bun', 'robe', P('pale', '#d8d8e0', '#7a8a6a', '#4a5a4a', '#2a2230', '#7a8a6a')),
    'farmer':    ('hat', 'casual', P('light', '#6b4a2e', '#5a7ac8', '#4a4a3a', '#3a2a2a', '#e8c86a')),
    'woman':     ('long', 'casual', P('tan', '#2a1a1a', '#4a9a8a', '#3a3f58', '#2a2230', '#4a9a8a')),
    'man':       ('short', 'casual', P('light', '#3a2a24', '#8a3a3a', '#3a3a44', '#2a2230', '#2a2a2a')),
    'man_b':     ('short', 'casual', P('deep', '#1a1a1a', '#e2b64a', '#3a3a44', '#2a2230', '#2a2a2a')),
    'woman_b':   ('bun', 'casual', P('brown', '#1a1a1a', '#c84a6a', '#3a3f58', '#2a2230', '#c84a6a')),
    'guard':     ('cap', 'casual', P('light', '#2a2a2a', '#3a4a6a', '#2a3040', '#1a1a1a', '#3a4a6a')),
    'twin':      ('ponytail', 'casual', P('light', '#c86a3a', '#f2c14e', '#e27a8a', '#2a2230', '#f4f4f4')),
    'ace':       ('spiky', 'casual', P('tan', '#1a1a2a', '#2a2a3a', '#1a1a24', '#1a1a1a', '#2a2a2a')),
    'ace_b':     ('long', 'casual', P('light', '#f4f4f4', '#2a2a3a', '#1a1a24', '#1a1a1a', '#e2555f')),
}


def check_frame(fr, cid, col):
    """Every frame must honour the contract the game relies on."""
    a = fr.a[:, :, 3]
    ys, xs = np.nonzero(a == 255)
    assert ys.max() == FEET_Y, (cid, col, 'feet must end on row', FEET_Y, ys.max())
    assert ys.min() >= 1, (cid, col, 'figure reaches row', ys.min())
    assert xs.min() >= 5 and xs.max() <= 27, (cid, col, 'figure outside x 5..27', xs.min(), xs.max())


def main():
    rows = list(ROSTER.items())
    sheet = Spr(W * 12, H * len(rows))
    index = {}
    for r, (cid, (head, body, pal, *extras)) in enumerate(rows):
        index[cid] = r
        gear = extras[0].get('gear', ()) if extras else ()
        for d, direction in enumerate(['down', 'left', 'right', 'up']):
            for f in range(3):
                fr = frame(head, body, direction, f, pal, gear)
                check_frame(fr, cid, d * 3 + f)
                sheet.blit(fr, (d * 3 + f) * W, r * H)
    out = os.path.join(ROOT, 'public', 'assets', 'sprites')
    os.makedirs(out, exist_ok=True)
    sheet.save(os.path.join(out, 'chars.png'))
    with open(os.path.join(out, 'chars.json'), 'w') as f:
        json.dump(index, f, indent=1)
    print(f'chars: {len(rows)} characters, {W}×{H} frames, sheet {W * 12}×{H * len(rows)}')


if __name__ == '__main__':
    main()
