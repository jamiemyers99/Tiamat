"""Mix check: render every part of a song on its own and print its level, so the melody sits on top.
    python3 tools/audio/stems.py haven"""
import os, sys, copy
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import compose, score
from render import fluid, read_wav, rms_db, WORK, SR

for name in sys.argv[1:]:
    spec = [s for s in score.SONGS if s['name'] == name][0]
    S = compose.build(spec)
    total = []
    for part in S.parts:
        solo = copy.copy(S)
        solo.events = [e for e in S.events if e[2] == part]
        solo.parts = {part: S.parts[part]}
        mid = os.path.join(WORK, f'stem_{part}.mid'); wav = mid[:-4] + '.wav'
        compose.to_midi(solo, mid, repeats=1, tail_beats=0)
        fluid(mid, wav)
        a = read_wav(wav)[: int(S.length * 60 / S.tempo * SR)]
        active = a[np.abs(a).max(axis=1) > 1e-3]
        total.append((part, rms_db(a), rms_db(active) if len(active) else -99, len(active) / max(1, len(a))))
    print(name)
    for part, r, ra, frac in sorted(total, key=lambda x: -x[1]):
        print(f'  {part:22s} overall {r:6.1f} dB   while playing {ra:6.1f} dB   plays {frac * 100:3.0f}%')
