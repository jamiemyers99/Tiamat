"""Render the soundtrack: score.py → MIDI (compose.py) → FluidSynth + FluidR3_GM → mastered, seamless OGG loops.

    python3 tools/audio/render.py              every song and jingle
    python3 tools/audio/render.py haven route  just these
    python3 tools/audio/render.py --report     loudness / brightness table of the rendered files

Mastering: 30 Hz high-pass, a gentle high-shelf cut (nothing shrill), slow glue compression, loudness matched
to a per-category target, soft peak limiting. Loops: the song is rendered twice and the second pass is kept,
so the reverb tail from the end of the loop is already sounding at its start — no click, no gap.
"""
import os, sys, json, subprocess, tempfile, wave
import numpy as np
from scipy.signal import butter, sosfilt, lfilter

sys.path.insert(0, os.path.dirname(__file__))
import compose
import score

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
BGM = os.path.join(ROOT, 'public/assets/audio/bgm')
SFX = os.path.join(ROOT, 'public/assets/audio/sfx')
SF2 = '/usr/share/sounds/sf2/FluidR3_GM.sf2'
SR = 44100
WORK = os.path.join(tempfile.gettempdir(), 'tiamat_music')
os.makedirs(WORK, exist_ok=True)

TARGET_DB = {'town': -20.5, 'route': -20.0, 'calm': -21.5, 'battle': -18.5, 'jingle': -19.0}


def fluid_fast(mid, wav, gain=0.45):
    """Quick dry render for level measurements (no effects, half rate)."""
    subprocess.run(['fluidsynth', '-ni', '-q', '-g', str(gain), '-r', '22050', '-R', '0', '-C', '0', '-F', wav, SF2, mid],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def fluid(mid, wav, reverb=0.62, gain=0.45):
    subprocess.run(['fluidsynth', '-ni', '-q', '-g', str(gain), '-r', str(SR),
                    '-o', f'synth.reverb.room-size={reverb}', '-o', 'synth.reverb.damp=0.35',
                    '-o', 'synth.reverb.width=0.9', '-o', 'synth.reverb.level=0.75',
                    '-o', 'synth.chorus.active=0',
                    '-o', 'synth.polyphony=512', '-F', wav, SF2, mid], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def read_wav(path):
    with wave.open(path) as w:
        n, ch = w.getnframes(), w.getnchannels()
        a = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float64) / 32768.0
    return a.reshape(-1, ch)


def write_wav(path, a):
    a = np.clip(a, -1, 1)
    with wave.open(path, 'wb') as w:
        w.setnchannels(a.shape[1]); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((a * 32767).astype(np.int16).tobytes())


def high_shelf(a, f0=6500, gain_db=-3.5, q=0.7):
    A = 10 ** (gain_db / 40)
    w0 = 2 * np.pi * f0 / SR
    alpha = np.sin(w0) / (2 * q)
    cw = np.cos(w0)
    b0 = A * ((A + 1) + (A - 1) * cw + 2 * np.sqrt(A) * alpha)
    b1 = -2 * A * ((A - 1) + (A + 1) * cw)
    b2 = A * ((A + 1) + (A - 1) * cw - 2 * np.sqrt(A) * alpha)
    a0 = (A + 1) - (A - 1) * cw + 2 * np.sqrt(A) * alpha
    a1 = 2 * ((A - 1) - (A + 1) * cw)
    a2 = (A + 1) - (A - 1) * cw - 2 * np.sqrt(A) * alpha
    return lfilter([b0 / a0, b1 / a0, b2 / a0], [1, a1 / a0, a2 / a0], a, axis=0)


def rms_db(a):
    return 20 * np.log10(np.sqrt(np.mean(a ** 2)) + 1e-12)


def movavg(x, n):
    """Centred moving average in O(N) (running sums)."""
    c = np.cumsum(np.concatenate([np.zeros(1), x]))
    h = n // 2
    i = np.arange(len(x))
    lo = np.clip(i - h, 0, len(x)); hi = np.clip(i + h + 1, 0, len(x))
    return (c[hi] - c[lo]) / (hi - lo)


def glue(a, thresh_db=-22, ratio=1.8, win=0.08):
    """Slow RMS compressor (same gain on both channels)."""
    mono = np.mean(a ** 2, axis=1)
    env = np.sqrt(movavg(mono, int(win * SR)) + 1e-12)
    db = 20 * np.log10(env)
    over = np.maximum(0, db - thresh_db)
    gr = -over * (1 - 1 / ratio)
    gr = movavg(gr, int(0.12 * SR))      # smooth the gain (attack/release ~ 120 ms)
    return a * (10 ** (gr / 20))[:, None]


def soft_limit(a, ceiling=0.93):
    x = a / ceiling
    y = np.where(np.abs(x) < 0.75, x, np.sign(x) * (0.75 + 0.25 * np.tanh((np.abs(x) - 0.75) / 0.25)))
    return y * ceiling


def master(a, target_db, shelf_db=-3.5):
    a = sosfilt(butter(2, 30, 'highpass', fs=SR, output='sos'), a, axis=0)
    a = high_shelf(a, 6500, shelf_db)
    a = glue(a)
    a = a * 10 ** ((target_db - rms_db(a)) / 20)
    return soft_limit(a)


def encode(wav, out, quality=3):
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', wav, '-c:a', 'libvorbis', '-q:a', str(quality), '-ar', str(SR), out], check=True)


def centroid(a):
    m = a.mean(axis=1)
    seg = m[: SR * 20]
    spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
    f = np.fft.rfftfreq(len(seg), 1 / SR)
    return float((spec * f).sum() / (spec.sum() + 1e-12))


# Mix roles: how loud each kind of part sits (while it is playing) relative to the melody.
ROLE_DB = {'lead': 0, 'double': -5, 'counter': -8, 'comp': -8, 'strum': -8, 'pick': -7, 'arp': -8, 'skank': -10,
           'pizz': -9, 'ost': -7, 'stab': -7, 'bass': -6, 'pad': -11, 'bells': -16, 'timpani': -9, 'taiko': -8,
           'drums': -9, 'drum_shaker': -19, 'drum_hand': -15, 'drum_brush': -13, 'drum_waltz': -14, 'drum_softkit': -12,
           'drum_bossa': -12, 'drum_march': -11, 'drum_funk': -9, 'drum_battle': -8, 'drum_taiko': -8}


def role_of(S, part):
    if part in S.roles:
        return S.roles[part]
    for pre in ('pad', 'arp', 'pick', 'strum', 'comp', 'skank', 'ost', 'stab', 'bass', 'counter', 'bells', 'drums'):
        if part.startswith(pre + '_'):
            return pre
    if part in ('pizz', 'timpani', 'taiko'):
        return part
    return 'lead'


def k_weight(a, sr):
    """Roughly how loud it sounds: lows count for less, highs for more (like the K-weighting in loudness meters)."""
    a = sosfilt(butter(2, 60, 'highpass', fs=sr, output='sos'), a, axis=0)
    A = 10 ** (4 / 40); w0 = 2 * np.pi * 1600 / sr; alpha = np.sin(w0) / (2 * 0.7); cw = np.cos(w0)
    b0 = A * ((A + 1) + (A - 1) * cw + 2 * np.sqrt(A) * alpha); b1 = -2 * A * ((A - 1) + (A + 1) * cw)
    b2 = A * ((A + 1) + (A - 1) * cw - 2 * np.sqrt(A) * alpha); a0 = (A + 1) - (A - 1) * cw + 2 * np.sqrt(A) * alpha
    a1 = 2 * ((A - 1) - (A + 1) * cw); a2 = (A + 1) - (A - 1) * cw - 2 * np.sqrt(A) * alpha
    return lfilter([b0 / a0, b1 / a0, b2 / a0], [1, a1 / a0, a2 / a0], a, axis=0)


def active_db(a, floor_db=-52, sr=SR):
    """How loud a stem sounds while it is actually playing (50 ms windows above the floor, K-weighted)."""
    a = k_weight(a, sr)
    m = np.mean(a ** 2, axis=1)
    n = int(0.05 * sr)
    k = len(m) // n
    win = m[: k * n].reshape(k, n).mean(axis=1)
    db = 10 * np.log10(win + 1e-12)
    on = win[db > floor_db]
    return 10 * np.log10(on.mean() + 1e-12) if len(on) else -99.0


def balance(S, spec):
    """Render each part alone, measure it, and set its channel volume (and, past the top, its velocities) so
    every part lands at its role's level. Melody first, accompaniment underneath, drums gently behind."""
    import copy
    from concurrent.futures import ThreadPoolExecutor
    trims = spec.get('trim', {})

    def one(part):
        solo = copy.copy(S)
        solo.events = [e for e in S.events if e[2] == part]
        solo.parts = {part: S.parts[part]}
        mid = os.path.join(WORK, f"stem_{spec['name']}_{part}.mid")
        wav = mid[:-4] + '.wav'
        compose.to_midi(solo, mid, repeats=1, tail_beats=0)
        fluid_fast(mid, wav)
        return part, active_db(read_wav(wav), sr=22050)

    lead_ref = None
    todo = list(S.parts)
    for it in range(3):
        with ThreadPoolExecutor(2) as ex:
            levels = dict(ex.map(one, todo))
        if lead_ref is None:   # the loudest melody sets the reference, so parts are mostly turned down, not pushed
            lead_ref = max([lvl - trims.get(pt, 0) for pt, lvl in levels.items() if role_of(S, pt) == 'lead'] or [-30]) - 1
        todo = [pt for pt, lvl in levels.items() if abs(lead_ref + ROLE_DB[role_of(S, pt)] + trims.get(pt, 0) - lvl) > 1.5]
        _adjust(S, levels, lead_ref, trims, it)
        if not todo:
            break
    # a lead that can't get loud enough (quiet samples, velocity already at the top): bring everything else down
    short = max([lead_ref + trims.get(pt, 0) - lvl for pt, lvl in levels.items() if role_of(S, pt) == 'lead'] + [0])
    if short > 1:
        print(f'    lead is {short:.1f} dB short: lowering the accompaniment to match')
        for pt, p in S.parts.items():
            if role_of(S, pt) != 'lead':
                p['vol'] = int(max(12, round(p['vol'] * 10 ** (-short / 40))))


def _adjust(S, levels, lead_ref, trims, it):
    for part, lvl in levels.items():
        want = lead_ref + ROLE_DB[role_of(S, part)] + trims.get(part, 0)
        corr = want - lvl
        p = S.parts[part]
        vol = p['vol'] * 10 ** (corr / 40)
        extra = 0
        if vol > 120:     # past the channel volume's top: a little more velocity (not too much — it brightens the tone)
            extra = min(4.0, 40 * np.log10(vol / 120))
            vol = 120
        p['vol'] = int(max(20, round(vol)))
        if extra:
            f = 10 ** (extra / 40)
            S.events = [(s, d, pt, pi, min(127, int(v * f))) if pt == part else (s, d, pt, pi, v) for (s, d, pt, pi, v) in S.events]
        if abs(corr) > 1.5 or it == 0:
            print(f'    {"  " * it}{part:20s} {role_of(S, part):8s} {lvl:6.1f} → {want:6.1f} dB   vol {p["vol"]}{f"  +{extra:.1f} dB vel" if extra else ""}')


def render_song(spec, rebalance=True):
    S = compose.build(spec)
    if rebalance:
        balance(S, spec)
    for w in S.warnings:
        print('  warn', w)
    mid = os.path.join(WORK, f"{spec['name']}.mid")
    wav = os.path.join(WORK, f"{spec['name']}.wav")
    if spec.get('jingle'):
        secs = compose.to_midi(S, mid, repeats=1, tail_beats=spec.get('tail', 6))
        fluid(mid, wav, reverb=spec.get('reverb', 0.6))
        a = read_wav(wav)
        if spec.get('end_beat'):
            secs = spec['end_beat'] * 60.0 / spec['tempo']
        end = int((secs + spec.get('tail_sec', 1.6)) * SR)
        a = a[:end]
        fade = int(0.35 * SR)
        a[-fade:] *= np.linspace(1, 0, fade)[:, None]
        # jingles are masked against their own peak, not RMS (short sounds)
        a = sosfilt(butter(2, 30, 'highpass', fs=SR, output='sos'), a, axis=0)
        a = high_shelf(a, 6500, -3)
        a = a * (10 ** (-5.5 / 20) / (np.abs(a).max() + 1e-9))
        a = soft_limit(a, 0.8)
        out_dir = SFX
    else:
        secs = compose.to_midi(S, mid, repeats=2, tail_beats=0)
        fluid(mid, wav, reverb=spec.get('reverb', 0.62))
        a = read_wav(wav)
        L = int(round(secs * SR))
        pre = int(0.05 * SR)          # start a hair early so notes nudged ahead of the beat keep their attack
        if len(a) < 2 * L + pre:   # fluidsynth stopped early (shouldn't happen): pad
            a = np.vstack([a, np.zeros((2 * L + pre - len(a), 2))])
        seg = a[L - pre:2 * L - pre].copy()
        # FluidSynth places events on a 64-sample grid, so the second pass can sit a fraction of a millisecond
        # off the first; blend the loop's first 50 ms from what follows its last sample so the join is seamless
        w = np.linspace(0, 1, pre)[:, None]
        seg[:pre] = a[L - pre:L] * w + a[2 * L - pre:2 * L] * (1 - w)
        # master three copies end to end and keep the middle one, so filters and the compressor see the loop
        # as the endless cycle it is (processing it alone would put a click at the join)
        n = len(seg)
        a = master(np.vstack([seg, seg, seg]), TARGET_DB[spec.get('cat', 'town')], spec.get('shelf', -3.5))[n:2 * n]
        out_dir = BGM
    tmp = os.path.join(WORK, f"{spec['name']}_m.wav")
    write_wav(tmp, a)
    out = os.path.join(out_dir, f"{spec['out']}.ogg")
    encode(tmp, out, spec.get('q', 3))
    print(f"  {spec['name']:18s} {len(a) / SR:6.1f}s  rms {rms_db(a):6.1f} dB  peak {20 * np.log10(np.abs(a).max()):5.1f} dB  centroid {centroid(a):6.0f} Hz  {os.path.getsize(out) // 1024} KB")
    return out


def main(args):
    names = [a for a in args if not a.startswith('--')]
    songs = [s for s in score.SONGS if not names or s['name'] in names]
    for spec in songs:
        spec.setdefault('out', spec['name'] if not spec.get('jingle') else f"jingle_{spec['name']}")
        print(spec['name'])
        render_song(spec)
    # audio index: everything present on disk
    idx_path = os.path.join(ROOT, 'public/assets/audio/index.json')
    idx = json.load(open(idx_path))
    idx['bgm'] = sorted(f[:-4] for f in os.listdir(BGM) if f.endswith('.ogg'))
    idx['sfx'] = sorted(f[:-4] for f in os.listdir(SFX) if f.endswith('.ogg'))
    json.dump(idx, open(idx_path, 'w'), indent=None)


if __name__ == '__main__':
    main(sys.argv[1:])
