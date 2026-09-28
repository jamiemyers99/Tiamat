"""Battle move sound effects for Tiamat — all synthesised here (no samples).

Every move plays one of these (see src/data/moveAnims.js): impacts (tackle, punch, bite, slash...),
elements (fire, water, zap, ice, rock, wind, leaf...), and status sounds (buff, heal, protect...).
Run:  python3 tools/audio/sfx.py            (writes public/assets/audio/sfx/mv_*.ogg + index.json)
"""
import os, sys, json
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from synth import SR, lowpass, write_ogg

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT = os.path.join(ROOT, 'public', 'assets', 'audio', 'sfx')
rng = np.random.default_rng(77)


# ── building blocks ─────────────────────────────────────────────────────────
def T(sec):
    return np.arange(int(sec * SR)) / SR


def noise(sec):
    return rng.uniform(-1, 1, int(sec * SR))


def highpass(x, cutoff):
    return x - lowpass(x, cutoff)


def band(x, lo, hi):
    return lowpass(highpass(x, lo), hi)


def glide(f0, f1, sec, kind='sine', curve=1.0):
    """Oscillator sliding from f0 to f1 (exponential)."""
    t = T(sec)
    k = (t / max(sec, 1e-6)) ** curve
    f = f0 * (f1 / f0) ** k
    ph = 2 * np.pi * np.cumsum(f) / SR
    if kind == 'sine':
        return np.sin(ph)
    if kind == 'square':      # a rounded pulse, not a raw square wave (that was the shrill chiptune edge)
        return lowpass(lowpass(np.sign(np.sin(ph)), 1800), 2600) * 0.8
    if kind == 'saw':
        return lowpass(((ph / (2 * np.pi)) % 1.0) * 2 - 1, 2500)
    if kind == 'tri':
        return 2 * np.abs(((ph / (2 * np.pi)) % 1.0) * 2 - 1) - 1
    raise ValueError(kind)


def tone(f, sec, kind='sine'):
    return glide(f, f, sec, kind)


def decay(sec, rate):
    return np.exp(-T(sec) * rate)


def ad(sec, a=0.01, curve=1.0):
    """Attack then linear-ish fade to zero."""
    t = T(sec)
    e = np.minimum(1.0, t / max(a, 1e-4)) * np.clip(1 - (t - a) / max(sec - a, 1e-4), 0, 1) ** curve
    return e


def swell(sec, peak=0.5):
    t = T(sec) / sec
    return np.where(t < peak, t / peak, (1 - t) / (1 - peak))


def mix(*parts):
    n = max(len(p[1]) + int(p[0] * SR) for p in parts)
    out = np.zeros(n)
    for at, x in parts:
        i = int(at * SR)
        out[i:i + len(x)] += x
    return out


def bell(f, sec, partials=((1, 1), (2.76, 0.5), (5.4, 0.25), (8.9, 0.12)), rate=6):
    t = T(sec)
    return sum(a * np.sin(2 * np.pi * f * m * t) * np.exp(-t * rate * (1 + m * 0.3)) for m, a in partials)


def thump(f0=160, f1=45, sec=0.2, rate=16):
    return glide(f0, f1, sec) * decay(sec, rate)


def crackle(sec, density=60, sharp=5000):
    x = np.zeros(int(sec * SR))
    for _ in range(int(sec * density)):
        i = rng.integers(0, len(x) - 200)
        L = rng.integers(40, 160)
        x[i:i + L] += rng.uniform(-1, 1, L) * np.exp(-np.arange(L) / 25) * rng.uniform(0.4, 1)
    return highpass(x, sharp * 0.3)


def norm(x, peak=0.85):
    m = np.max(np.abs(x)) or 1
    return x / m * peak


def finish(x, level_db=-17.0):
    """Every move sound gets the same treatment so they sit together and with the music: the top rounded off
    (nothing glassy above ~6 kHz), a touch of the same small room, and one loudness (loudest 80 ms window)."""
    from scipy.signal import butter, sosfilt
    x = np.asarray(x, dtype=np.float64)
    x = sosfilt(butter(2, 6200, 'lowpass', fs=SR, output='sos'), x)
    x = sosfilt(butter(1, 45, 'highpass', fs=SR, output='sos'), x)
    tail = int(0.3 * SR)
    ir = rng.uniform(-1, 1, tail) * np.exp(-np.arange(tail) / SR * 10)
    ir = sosfilt(butter(2, 3000, 'lowpass', fs=SR, output='sos'), ir)
    wet = np.convolve(x, ir)
    wet *= (np.abs(x).max() + 1e-9) / (np.abs(wet).max() + 1e-9)
    y = np.zeros(len(wet)); y[:len(x)] = x
    y = y * 0.9 + wet * 0.12
    nz = np.nonzero(np.abs(y) > 1e-4 * np.abs(y).max())[0]
    y = y[: nz[-1] + 1]
    f = min(int(0.02 * SR), len(y) // 4)
    y[-f:] *= np.linspace(1, 0, f)
    w = int(0.08 * SR)
    loud = np.sqrt(np.convolve(y ** 2, np.ones(w) / w, mode='same').max()) if len(y) > w else np.sqrt(np.mean(y ** 2))
    y *= 10 ** (level_db / 20) / (loud + 1e-12)
    pk = np.abs(y).max()
    return y * (0.84 / pk) if pk > 0.84 else y


# ── the sounds ──────────────────────────────────────────────────────────────
S = {}


def sfx(fn):
    S['mv_' + fn.__name__] = fn
    return fn


@sfx
def tackle():
    return mix((0, thump(170, 50, 0.22, 14) * 0.9), (0, band(noise(0.06), 800, 5000) * decay(0.06, 60) * 0.5))


@sfx
def heavy():
    return mix((0, thump(130, 32, 0.5, 7)), (0, lowpass(noise(0.6), 300) * decay(0.6, 6) * 0.8),
               (0, band(noise(0.08), 600, 4000) * decay(0.08, 50) * 0.5))


@sfx
def punch():
    return mix((0, thump(220, 70, 0.14, 26)), (0, band(noise(0.05), 1500, 7000) * decay(0.05, 80) * 0.7))


@sfx
def kick():
    whoosh = band(noise(0.12), 900, 4000) * swell(0.12, 0.8) * 0.35
    return mix((0, whoosh), (0.1, punch()))


@sfx
def slash():
    shing = highpass(noise(0.22), 3000) * ad(0.22, 0.02, 1.5) * 0.7
    return mix((0, shing), (0.05, bell(2600, 0.3, rate=12) * 0.25))


@sfx
def claw():
    one = highpass(noise(0.07), 2500) * ad(0.07, 0.005, 2) * 0.8
    return mix((0, one), (0.07, one * 0.9), (0.14, one * 0.8))


@sfx
def bite():
    snap = band(noise(0.05), 700, 3500) * decay(0.05, 70)
    click = tone(900, 0.03, 'square') * decay(0.03, 120) * 0.4
    return mix((0, snap + np.pad(click, (0, len(snap) - len(click)))), (0.09, snap * 1.1), (0.09, thump(200, 90, 0.08, 40) * 0.5))


@sfx
def sting():
    return mix((0, glide(2400, 1200, 0.07, 'square') * decay(0.07, 40) * 0.5), (0.02, highpass(noise(0.03), 4000) * 0.5))


@sfx
def whip():
    whoosh = band(noise(0.18), 500, 3000) * swell(0.18, 0.85) * 0.4
    crack = highpass(noise(0.03), 2500) * decay(0.03, 90) * 1.0
    return mix((0, whoosh), (0.16, crack))


@sfx
def wing():
    t = T(0.4)
    flap = 0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 14 * t))
    return band(noise(0.4), 400, 2500) * flap * ad(0.4, 0.05) * 0.6


@sfx
def dive():
    return mix((0, glide(1600, 260, 0.45, 'sine', 0.7) * ad(0.45, 0.03) * 0.35), (0.42, thump(180, 40, 0.3, 10)))


@sfx
def quake():
    t = T(0.9)
    rum = lowpass(noise(0.9), 160) * 3 * (0.6 + 0.4 * np.sin(2 * np.pi * 9 * t)) * ad(0.9, 0.05)
    return mix((0, rum), (0, thump(90, 30, 0.6, 5) * 0.8))


@sfx
def rock():
    parts = [(0, thump(140, 50, 0.2, 18))]
    for k in range(5):
        parts.append((0.05 + k * 0.07, lowpass(noise(0.08), 900) * decay(0.08, 40) * rng.uniform(0.4, 0.9)))
    return mix(*parts)


@sfx
def throw():
    return band(noise(0.25), 600, 2500) * swell(0.25, 0.6) * 0.5


@sfx
def orb():
    return mix((0, glide(300, 900, 0.3, 'tri') * ad(0.3, 0.05) * 0.4), (0.28, band(noise(0.1), 500, 3000) * decay(0.1, 40) * 0.6))


@sfx
def beam():
    t = T(0.65)
    f = 520 + 180 * np.sin(2 * np.pi * 11 * t)
    las = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.4 + ((np.cumsum(f * 1.5) / SR) % 1.0 - 0.5) * 0.2
    return lowpass(las, 4000) * ad(0.65, 0.04, 0.8)


@sfx
def fire():
    body = band(noise(0.7), 300, 2500) * swell(0.7, 0.3) * 0.7
    return body + crackle(0.7, 50) * 0.5 * ad(0.7, 0.05)


@sfx
def water():
    splash = lowpass(noise(0.45), 3000) * decay(0.45, 9) * 0.8
    blips = mix(*[(0.05 + k * 0.06, glide(500 + 150 * k, 900 + 150 * k, 0.05) * decay(0.05, 40) * 0.3) for k in range(5)])
    return mix((0, splash), (0, blips))


@sfx
def wave():
    t = T(1.0)
    return lowpass(noise(1.0), 1200) * (0.6 + 0.4 * np.sin(2 * np.pi * 2.2 * t)) * swell(1.0, 0.45) * 1.1


@sfx
def bubble():
    return mix(*[(k * 0.07, glide(350 + 90 * k, 1100 + 120 * k, 0.06) * decay(0.06, 35) * 0.45) for k in range(6)])


@sfx
def bolt():
    crack = highpass(noise(0.12), 1500) * decay(0.12, 30) * 1.0
    zap = mix(*[(k * 0.03, tone(rng.uniform(300, 1200), 0.03, 'square') * 0.25) for k in range(6)])
    rum = lowpass(noise(0.7), 200) * 3 * decay(0.7, 4) * 0.6
    return mix((0, crack), (0, zap), (0.05, rum))


@sfx
def zap():
    x = mix(*[(k * 0.028, tone(rng.uniform(200, 1400), 0.028, 'square') * 0.35) for k in range(11)])
    return x * ad(len(x) / SR, 0.01)


@sfx
def ice():
    chimes = mix(*[(k * 0.05, bell(f, 0.5, rate=7) * 0.25) for k, f in enumerate([2093, 2637, 3136, 2349, 3520])])
    return mix((0, chimes), (0, highpass(noise(0.2), 6000) * decay(0.2, 15) * 0.2))


@sfx
def wind():
    x = noise(0.7)
    t = T(0.7)
    lo = lowpass(x, 700)
    hi = lowpass(x, 2500)
    blend = 0.5 + 0.5 * np.sin(2 * np.pi * 1.4 * t)
    return (lo * (1 - blend) + hi * blend) * swell(0.7, 0.5) * 1.3


@sfx
def leaf():
    parts = []
    for k in range(7):
        parts.append((k * 0.06, band(noise(0.05), 1500, 6000) * decay(0.05, 45) * rng.uniform(0.3, 0.6)))
    return mix(*parts)


@sfx
def psychic():
    t = T(0.8)
    f = 420 + 160 * np.sin(2 * np.pi * 7 * t)
    w = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(2 * np.pi * 31 * t)
    return (w * 0.5 + np.sin(2 * np.pi * np.cumsum(f * 2) / SR) * 0.2) * ad(0.8, 0.08)


@sfx
def shadow():
    a = glide(260, 70, 0.7, 'saw') * 0.3
    b = glide(268, 72, 0.7, 'saw') * 0.3
    return lowpass(a + b, 900) * swell(0.7, 0.35) + lowpass(noise(0.7), 500) * swell(0.7, 0.3) * 0.5


@sfx
def poison():
    parts = [(0, lowpass(noise(0.6), 700) * swell(0.6, 0.3) * 0.6)]
    for k in range(8):
        parts.append((0.03 + k * 0.065, glide(rng.uniform(120, 220), rng.uniform(250, 400), 0.06) * decay(0.06, 30) * 0.4))
    return mix(*parts)


@sfx
def powder():
    return lowpass(noise(0.55), 1800) * swell(0.55, 0.25) * 0.55 + highpass(noise(0.55), 5000) * swell(0.55, 0.5) * 0.12


@sfx
def sound():
    t = T(0.55)
    f = 210 + 30 * np.sin(2 * np.pi * 6 * t)
    saw = ((np.cumsum(f) / SR) % 1.0) * 2 - 1
    return band(saw, 300, 2400) * ad(0.55, 0.03) * 0.9


@sfx
def drain():
    rev = (band(noise(0.5), 800, 5000) * np.linspace(0, 1, int(0.5 * SR)) ** 2) * 0.5
    return mix((0, rev), (0.45, bell(1760, 0.4, rate=9) * 0.3))


@sfx
def breath():
    return band(noise(0.75), 700, 3200) * swell(0.75, 0.3) * 0.9 + lowpass(noise(0.75), 250) * swell(0.75, 0.3) * 0.5


@sfx
def nova():
    boom = mix((0, thump(110, 28, 0.8, 5)), (0, lowpass(noise(0.9), 600) * decay(0.9, 5) * 0.9))
    shimmer = highpass(noise(0.9), 5000) * decay(0.9, 5) * 0.2
    return mix((0, boom), (0.02, shimmer))


@sfx
def fae():
    notes = [1047, 1319, 1568, 2093, 2637]
    return mix(*[(k * 0.055, bell(f, 0.45, ((1, 1), (3, 0.3), (5.1, 0.1)), rate=8) * 0.28) for k, f in enumerate(notes)])


@sfx
def buff():
    return mix(*[(k * 0.06, tone(f, 0.07, 'square') * decay(0.07, 25) * 0.3) for k, f in enumerate([523, 659, 784, 1047, 1319])])


@sfx
def debuff():
    return mix(*[(k * 0.07, tone(f, 0.08, 'square') * decay(0.08, 22) * 0.3) for k, f in enumerate([988, 784, 622, 494, 392])])


@sfx
def heal():
    return mix(*[(k * 0.08, bell(f, 0.6, ((1, 1), (2, 0.3)), rate=5) * 0.3) for k, f in enumerate([784, 988, 1175, 1568])])


@sfx
def protect():
    t = T(0.6)
    trem = 0.7 + 0.3 * np.sin(2 * np.pi * 18 * t)
    return (tone(523, 0.6) + tone(784, 0.6) * 0.7 + tone(1046, 0.6) * 0.4) * trem * ad(0.6, 0.03) * 0.3


@sfx
def sleep():
    return mix(*[(k * 0.22, tone(f, 0.25, 'tri') * ad(0.25, 0.03) * 0.35) for k, f in enumerate([659, 587, 523])])


@sfx
def metal():
    return mix((0, bell(700, 0.6, ((1, 1), (2.41, 0.7), (3.93, 0.5), (5.8, 0.3)), rate=5) * 0.5), (0, highpass(noise(0.04), 3000) * 0.6))


@sfx
def dragon():
    t = T(0.8)
    f = 85 + 25 * np.sin(2 * np.pi * 5 * t)
    growl = (((np.cumsum(f) / SR) % 1.0) * 2 - 1) * (0.7 + 0.3 * np.sin(2 * np.pi * 23 * t))
    return lowpass(growl, 1200) * swell(0.8, 0.25) + band(noise(0.8), 300, 1500) * swell(0.8, 0.3) * 0.5


@sfx
def buzz():
    t = T(0.45)
    return tone(220, 0.45, 'square') * (0.5 + 0.5 * np.sin(2 * np.pi * 40 * t)) * ad(0.45, 0.03) * 0.35


@sfx
def seed():
    pops = mix(*[(k * 0.05, glide(700, 300, 0.04) * decay(0.04, 50) * 0.4) for k in range(5)])
    return mix((0, pops), (0, leaf() * 0.5))


@sfx
def silk():
    return glide(3000, 900, 0.3, 'sine', 0.5) * ad(0.3, 0.01) * 0.25 + highpass(noise(0.3), 4000) * ad(0.3, 0.01) * 0.15


@sfx
def charge():
    return glide(200, 1400, 0.55, 'tri', 1.3) * ad(0.55, 0.05, 0.3) * 0.35


def main(only=None):
    os.makedirs(OUT, exist_ok=True)
    idx_path = os.path.join(ROOT, 'public', 'assets', 'audio', 'index.json')
    idx = json.load(open(idx_path))
    for name, fn in S.items():
        if only and name not in only:
            continue
        x = finish(fn())
        write_ogg(os.path.join(OUT, f'{name}.ogg'), x)
        if name not in idx['sfx']:
            idx['sfx'].append(name)
    idx['sfx'].sort()
    json.dump(idx, open(idx_path, 'w'), indent=1)
    print(f'{len(S)} move sounds written')


if __name__ == '__main__' and (len(sys.argv) < 2 or sys.argv[1] != 'sig'):
    main(sys.argv[1:] or None)
    main_sig_later = True


# ── signature moves: each has its own sound, never shared ───────────────────
# (layers of the base sounds above — name, start s, gain, pitch rate — plus a short motif of its own)
def pitched(x, rate):
    if rate == 1:
        return x
    n = int(len(x) / rate)
    return np.interp(np.arange(n) * rate, np.arange(len(x)), x)


def voice(kind, f, sec):
    t = T(sec)
    if kind == 'pluck':
        return glide(f, f, sec, 'tri') * decay(sec, 9) * 0.6
    if kind == 'bell':
        return bell(f, sec, ((1, 1), (2, 0.4), (3, 0.2)), rate=5) * 0.5
    if kind == 'glass':
        return bell(f, sec, ((1, 1), (2.76, 0.3), (5.4, 0.15)), rate=4) * 0.45
    if kind == 'square':      # soft reed
        return (glide(f, f, sec, 'tri') + 0.25 * glide(2 * f, 2 * f, sec)) * ad(sec, 0.006, 1.5) * 0.4
    if kind == 'horn':
        return lowpass(glide(f, f, sec, 'saw'), 1800) * ad(sec, 0.04, 0.7) * 0.6
    if kind == 'choir':
        v = 1 + 0.006 * np.sin(2 * np.pi * 5 * t)
        ph = 2 * np.pi * f * np.cumsum(v) / SR
        return (np.sin(ph) + 0.4 * np.sin(2 * ph) + 0.2 * np.sin(3 * ph)) * swell(sec, 0.3) * 0.4
    if kind == 'harp':
        return (glide(f, f, sec) + 0.3 * glide(2 * f, 2 * f, sec)) * decay(sec, 6) * 0.5
    if kind == 'deep':
        return (glide(f, f * 0.97, sec) + 0.5 * glide(f * 2, f * 2, sec, 'tri')) * ad(sec, 0.02, 1.2) * 0.8
    raise ValueError(kind)


def motif(notes, kind, step=0.085, sec=0.3):
    from synth import midi, freq
    def f(n):
        hz = freq(midi(n))
        while hz > 1100:          # keep motifs out of the piercing top octave
            hz /= 2
        return hz
    parts = [(k * step, voice(kind, f(n), sec)) for k, n in enumerate(notes.split())]
    return mix(*parts)


SIG = {
    # Twinklit line
    'dream_tap': ([('psychic', 0, .3, 1.4)], 'E6 G6', 'glass'),
    'glimmer_kiss': ([('fae', 0, .6, 1.2)], 'C6 E6 A6', 'bell'),
    'starlight_purr': ([('fae', 0, .5, .8), ('protect', .1, .3, 1.3)], 'G5 E5 C5 G4', 'harp'),
    'mind_ripple': ([('psychic', 0, .7, .9)], 'D5 F5 D5 F5', 'square'),
    'moonbeam_pounce': ([('beam', 0, .4, .7), ('dive', .3, .7, 1.2)], 'A5 E6', 'glass'),
    'psyche_bloom': ([('heal', 0, .6, 1.1), ('leaf', 0, .3, 1.3)], 'C5 G5 C6 E6', 'bell'),
    'fae_ring': ([('fae', 0, .6, .9), ('bubble', .2, .3, 1.6)], 'F5 A5 C6 F6', 'harp'),
    'wishing_star': ([('heal', .1, .6, 1)], 'E5 B5 E6 G#6', 'glass'),
    'astral_purr': ([('psychic', 0, .6, .7), ('wind', 0, .3, .6)], 'C4 G4 D5 A5', 'choir'),
    'dreamshatter': ([('nova', .15, .8, 1.3), ('ice', .15, .4, .8)], 'B5 F5 B4', 'glass'),
    'aurora_benediction': ([('heal', 0, .5, .8), ('beam', .1, .4, 1.1)], 'D5 F#5 A5 D6', 'choir'),
    'cosmic_insight': ([('charge', 0, .5, .8), ('nova', .45, .9, .8), ('beam', .4, .5, .9)], 'C4 E4 G4 B4 D5', 'choir'),
    # Spriglet line
    'sprout_tackle': ([('tackle', .12, 1, 1.1), ('leaf', .12, .4, 1.4)], 'G5 C6', 'pluck'),
    'petal_cloak': ([('leaf', 0, .6, 1), ('protect', .2, .5, 1.2)], 'E5 G5', 'bell'),
    'bramble_whip': ([('whip', 0, 1, .9), ('leaf', .12, .6, 1.2)], 'A4 C5', 'pluck'),
    'pebble_seed': ([('seed', 0, .5, .8), ('rock', .2, .7, 1.2)], 'D5 A4', 'pluck'),
    'verdant_pulse': ([('drain', 0, .6, 1), ('leaf', 0, .4, .9)], 'C5 E5 G5 B5', 'bell'),
    'rootquake': ([('quake', 0, 1, 1), ('leaf', .2, .3, .7)], 'E3 B2', 'deep'),
    'grove_renewal': ([('heal', 0, .6, .9), ('leaf', 0, .5, 1.1)], 'F5 A5 C6', 'harp'),
    'ancient_canopy': ([('wave', 0, .6, .6), ('leaf', .3, .7, .8)], 'D3 A3 D4', 'horn'),
    'monolith_crash': ([('heavy', .35, 1, .8), ('rock', .4, .8, .8)], 'C2 G2', 'deep'),
    # Cindlet line
    'cinder_pounce': ([('tackle', .12, 1, 1.05), ('fire', .12, .5, 1.4)], 'F5 A5', 'pluck'),
    'sulk_smoke': ([('powder', 0, .9, .8)], 'C5 B4 A#4', 'square'),
    'ember_fang': ([('bite', 0, 1, 1), ('fire', .05, .5, 1.2)], 'E5 G#5', 'pluck'),
    'shadow_spark': ([('zap', 0, .6, .7), ('shadow', 0, .5, 1.3)], 'F#5 C5', 'square'),
    'blaze_mane': ([('fire', 0, .9, 1.1)], 'A4 E5', 'horn'),
    'dusk_ignite': ([('fire', 0, .6, .8), ('shadow', 0, .5, 1)], 'D5 A5', 'bell'),
    'umbral_flare': ([('fire', 0, .8, .7), ('shadow', 0, .6, 1.2)], 'C#4 G4', 'horn'),
    'black_pyre': ([('fire', 0, .9, .6), ('nova', .3, .6, 1.1)], 'A2 D#3', 'deep'),
    'nightfire_rend': ([('claw', .1, 1, .9), ('fire', .1, .5, .9)], 'E5 A#4', 'square'),
    # Puddlet line
    'puddle_hop': ([('water', .2, .8, 1.3), ('tackle', .2, .7, 1.2)], 'C6 G5', 'pluck'),
    'drizzle_eyes': ([('water', 0, .6, .9), ('debuff', .3, .4, 1.1)], 'A5 F5 D5', 'bell'),
    'bubble_snap': ([('bubble', 0, 1, 1.2)], 'E6 C6', 'pluck'),
    'rime_splash': ([('water', 0, .7, 1), ('ice', .2, .6, 1)], 'G6 D6', 'glass'),
    'riptide_fang': ([('wave', 0, .6, 1.3), ('bite', .45, 1, .9)], 'D5 F5', 'pluck'),
    'current_coat': ([('bubble', 0, .6, .8), ('protect', .3, .5, .9)], 'G4 B4 D5', 'harp'),
    'glacier_surge': ([('wave', 0, .8, 1), ('ice', .4, .6, .8)], 'E4 B4', 'horn'),
    'maelstrom': ([('wave', 0, .9, .8), ('bubble', .2, .5, .7)], 'F2 C3 F3', 'deep'),
    'permafrost_breath': ([('breath', 0, .8, 1), ('ice', .2, .6, .8)], 'B4 F#5', 'choir'),
    # evolved signatures
    'eye_of_the_storm': ([('wind', 0, .8, .7), ('bolt', .6, .8, 1)], 'G3 D4 G4', 'horn'),
    'thunderwing': ([('dive', 0, .7, 1), ('zap', .35, .6, 1.2)], 'E6 B5', 'square'),
    'heartless_night': ([('shadow', 0, .9, .6)], 'D#4 A4', 'choir'),
    'riftbreaker': ([('quake', 0, .9, 1.1), ('dragon', .1, .7, 1)], 'C2 F#2', 'deep'),
    'plague_tide': ([('wave', 0, .8, .9), ('poison', .2, .6, 1)], 'A#3 E4', 'horn'),
    'champions_gauntlet': ([('charge', 0, .4, 1.2), ('punch', .45, 1, .9), ('metal', .45, .5, 1)], 'C5 E5 G5 C6', 'horn'),
    'prophecy_beam': ([('beam', .2, .8, 1), ('psychic', 0, .4, 1.2)], 'A5 C#6 E6', 'glass'),
    'aurora_lance': ([('ice', 0, .7, 1), ('beam', 0, .4, 1.3)], 'F#6 C#6', 'glass'),
    'siege_ram': ([('heavy', .15, 1, .9), ('metal', .15, .7, .8)], 'G2 D3', 'deep'),
    'tyrant_skyfall': ([('dive', 0, .8, .8), ('dragon', .4, .8, .9)], 'D3 A3 F4', 'horn'),
    'guillotine_scythe': ([('slash', 0, 1, .7)], 'E6 E5', 'glass'),
    'peakfall': ([('heavy', .4, 1, .8), ('wind', 0, .5, .8)], 'B1 F#2', 'deep'),
    'siren_sting': ([('sting', .3, .8, 1), ('wave', 0, .4, 1.5)], 'G#5 D#6', 'choir'),
    'crushing_claw': ([('bite', .1, 1, .7), ('metal', .15, .5, 1.3)], 'C4 C5', 'pluck'),
    'mammoth_stampede': ([('quake', 0, .8, 1.3), ('tackle', .3, .9, .8)], 'F3 F3 C4', 'horn'),
    'tesla_coil': ([('zap', .2, .8, 1), ('bolt', .3, .6, 1.2)], 'C6 G6 C7', 'square'),
    'glacier_maul': ([('claw', 0, 1, .8), ('ice', .1, .6, .9)], 'A3 E4', 'horn'),
    'thunder_jaws': ([('bite', 0, 1, 1), ('zap', .05, .6, 1)], 'B5 F6', 'square'),
    'reapers_lantern': ([('drain', 0, .7, .8), ('shadow', 0, .5, .9)], 'E4 G4 B4', 'choir'),
    'caldera_crush': ([('bite', 0, 1, .8), ('fire', .1, .7, .8)], 'D3 G#3', 'deep'),
    'death_stinger': ([('sting', .1, 1, .7), ('poison', .1, .6, 1)], 'F#5 C6', 'square'),
    'royal_sting': ([('sting', .15, .9, 1), ('buzz', 0, .5, 1.1)], 'C6 E6 G6', 'bell'),
    'moonlit_riddle': ([('psychic', 0, .6, 1.2)], 'D6 A5 F6', 'glass'),
    'haymaker': ([('kick', .25, .8, .8), ('punch', .3, 1, .85)], 'G3 C4', 'horn'),
    'mycelial_surge': ([('powder', 0, .8, 1), ('seed', 0, .5, 1)], 'A3 C4 E4', 'pluck'),
    'bulwark_charge': ([('protect', 0, .5, .8), ('heavy', .3, .9, 1)], 'E3 B3', 'pluck'),
    'tunnel_quake': ([('quake', 0, 1, .9), ('rock', .3, .7, 1)], 'A1 E2', 'deep'),
    'dusk_hunt': ([('shadow', 0, .6, 1.5), ('claw', .25, .9, 1)], 'D#5 G5', 'square'),
    'primordial_tide': ([('wave', 0, 1, .6), ('dragon', .2, .6, .8)], 'D3 A3 D4 F4', 'choir'),
    # other one-line moves
    'clamor': ([('sound', 0, 1, 1.1)], 'G4 G#4', 'square'),
    'pummel': ([('punch', 0, 1, 1.3)], 'C5', 'pluck'),
    'vine_lash': ([('whip', 0, 1, 1.2)], 'E5 A4', 'pluck'),
    'seed_volley': ([('seed', 0, 1, 1.2)], 'G5', 'pluck'),
    'root_snare': ([('seed', 0, .7, .8), ('leaf', .3, .4, .8)], 'D4 F4 A4', 'pluck'),
    'timber_crash': ([('heavy', .3, 1, 1), ('leaf', .3, .5, .8)], 'F2 C3', 'deep'),
    'moss_shield': ([('protect', 0, .7, 1.1), ('leaf', 0, .3, 1)], 'B4 D5', 'bell'),
    'flare_bite': ([('bite', 0, 1, 1.1), ('fire', 0, .6, 1)], 'G5 D5', 'pluck'),
    'cinder_claw': ([('claw', 0, 1, 1), ('fire', 0, .5, 1.3)], 'A5 E5', 'pluck'),
    'inferno_lash': ([('whip', 0, 1, .8), ('fire', .15, .8, 1)], 'B4 G5', 'horn'),
    'smoke_veil': ([('powder', 0, 1, .7)], 'E4 D4', 'square'),
    'kindle': ([('fire', 0, .7, 1.5)], 'C#6 A5', 'glass'),
    'magma_jaws': ([('bite', 0, 1, .8), ('fire', 0, .6, .8)], 'E3 A3', 'deep'),
    'pyre_rush': ([('tackle', .15, 1, 1), ('fire', .15, .7, 1)], 'C4 G4 C5', 'horn'),
    'rip_current': ([('water', 0, 1, 1.4)], 'F6 C6', 'pluck'),
    'volt_fang': ([('bite', 0, 1, 1.1), ('zap', 0, .5, 1.3)], 'D6 A5', 'pluck'),
    'volt_needle': ([('sting', 0, 1, 1.2), ('zap', 0, .4, 1.6)], 'B6', 'pluck'),
    'mud_lob': ([('throw', 0, .8, 1), ('water', .35, .7, .6)], 'C4 E4', 'pluck'),
    'frost_fang': ([('bite', 0, 1, 1), ('ice', 0, .5, 1.1)], 'F#5 B5', 'pluck'),
    'glacial_crush': ([('rock', .3, .9, 1.2), ('ice', .3, .7, .9)], 'G2 D3 G3', 'deep'),
    'frost_armor': ([('ice', 0, .7, 1), ('protect', .2, .5, 1)], 'A5 C#6', 'bell'),
    'psi_wave': ([('psychic', 0, .7, 1.3)], 'F5 G5', 'glass'),
    'soul_siphon': ([('drain', 0, .8, .8), ('shadow', 0, .5, 1.1)], 'F4 C5', 'choir'),
    'gleam_cannon': ([('beam', .2, 1, 1.2), ('metal', .2, .5, 1.1)], 'A5 E6 A6', 'square'),
    'drake_talon': ([('claw', 0, 1, 1), ('dragon', 0, .5, 1.4)], 'C#5 G#5', 'pluck'),
    'wyvern_dive': ([('dive', 0, .8, .8), ('dragon', .35, .7, 1)], 'A#2 F3', 'horn'),
}


def sig_sound(move):
    layers, notes, kind = SIG[move]
    parts = [(at, pitched(np.asarray(S['mv_' + base](), dtype=np.float64), rate) * gain) for base, at, gain, rate in layers]
    parts.append((0.0, motif(notes, kind) * 0.55))
    return mix(*parts)


def main_sig(only=None):
    motifs = [(v[1], v[2]) for v in SIG.values()]
    assert len(set(motifs)) == len(motifs), 'every signature move needs its own motif'
    idx_path = os.path.join(ROOT, 'public', 'assets', 'audio', 'index.json')
    idx = json.load(open(idx_path))
    for move in SIG:
        if only and move not in only:
            continue
        x = finish(sig_sound(move), -16.0)
        write_ogg(os.path.join(OUT, f'sig_{move}.ogg'), x)
        if f'sig_{move}' not in idx['sfx']:
            idx['sfx'].append(f'sig_{move}')
    idx['sfx'].sort()
    json.dump(idx, open(idx_path, 'w'), indent=1)
    print(f'{len(SIG)} signature sounds written')


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'sig':
        main_sig(sys.argv[2:] or None)
    elif len(sys.argv) < 2:
        main_sig()
