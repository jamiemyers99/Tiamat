"""Interface and world sound effects, made to sit with the soundtrack: the same soft instruments (marimba,
kalimba, harp, vibes, pizzicato, woodblock) and gentle synthesised foley (steps, doors, whooshes, thuds).

    python3 tools/audio/ui_sfx.py            all of them
    python3 tools/audio/ui_sfx.py cursor     just these

Every sound is short, rounded off at the top (nothing above ~7 kHz is left bright), and levelled so the most
frequent ones (cursor, text, steps) are the quietest.
"""
import os, sys, subprocess, tempfile
import numpy as np
import mido
from scipy.signal import butter, sosfilt

sys.path.insert(0, os.path.dirname(__file__))
from compose import GM, note_num

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT = os.path.join(ROOT, 'public/assets/audio/sfx')
SF2 = '/usr/share/sounds/sf2/FluidR3_GM.sf2'
SR = 44100
WORK = os.path.join(tempfile.gettempdir(), 'tiamat_sfx')
os.makedirs(WORK, exist_ok=True)
rng = np.random.default_rng(5)


# ── rendering helpers ──────────────────────────────────────────────────────
def gm(notes, length, reverb=0.35, name='x'):
    """notes: (start s, dur s, program or 'drum', pitch (name or number), velocity). → mono float array."""
    mid = mido.MidiFile(ticks_per_beat=1000)
    tr = mido.MidiTrack(); mid.tracks.append(tr)
    tr.append(mido.MetaMessage('set_tempo', tempo=1000000, time=0))     # 1 beat = 1 s, 1 tick = 1 ms
    progs = {}
    msgs = []
    for (s, d, prog, p, v) in notes:
        drum = prog == 'drum'
        if drum:
            ch = 9
        else:
            if prog not in progs:
                progs[prog] = len(progs) + (1 if len(progs) >= 9 else 0)
                msgs.append((0, 0, mido.Message('program_change', program=GM[prog] if isinstance(prog, str) else prog, channel=progs[prog])))
                msgs.append((0, 0, mido.Message('control_change', control=91, value=60, channel=progs[prog])))
            ch = progs[prog]
        n = note_num(p) if isinstance(p, str) else p
        msgs.append((int(s * 1000), 2, mido.Message('note_on', note=n, velocity=v, channel=ch)))
        msgs.append((int((s + d) * 1000), 1, mido.Message('note_off', note=n, velocity=0, channel=ch)))
    msgs.sort(key=lambda m: (m[0], m[1]))
    last = 0
    for t, _, m in msgs:
        tr.append(m.copy(time=t - last)); last = t
    tr.append(mido.MetaMessage('end_of_track', time=int(length * 1000) - last + 200))
    mp = os.path.join(WORK, f'{name}.mid'); wp = mp[:-4] + '.wav'
    mid.save(mp)
    subprocess.run(['fluidsynth', '-ni', '-q', '-g', '0.6', '-r', str(SR), '-o', f'synth.reverb.room-size={reverb}',
                    '-o', 'synth.reverb.level=0.6', '-o', 'synth.chorus.active=0', '-F', wp, SF2, mp],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    import wave
    with wave.open(wp) as w:
        a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float).reshape(-1, 2) / 32768
    return a.mean(axis=1)[: int(length * SR)]


def T(sec):
    return np.arange(int(sec * SR)) / SR


def noise(sec):
    return rng.uniform(-1, 1, int(sec * SR))


def lp(x, f, order=2):
    return sosfilt(butter(order, f, 'lowpass', fs=SR, output='sos'), x)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, 'highpass', fs=SR, output='sos'), x)


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], 'bandpass', fs=SR, output='sos'), x)


def env(sec, a=0.005, d=None, curve=2.0):
    t = T(sec)
    d = d or sec
    return np.minimum(1, t / max(a, 1e-4)) * np.clip(1 - t / d, 0, 1) ** curve


def glide(f0, f1, sec, kind='sine'):
    t = T(sec)
    f = f0 * (f1 / f0) ** (t / sec)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) if kind == 'sine' else (2 / np.pi) * np.arcsin(np.sin(ph))


def mix(*parts):
    n = max(int(at * SR) + len(x) for at, x in parts)
    out = np.zeros(n)
    for at, x in parts:
        i = int(at * SR); out[i:i + len(x)] += x
    return out


def room(x, sec=0.35, wet=0.14):
    """A small, soft room so the foley shares a space with the music."""
    ir = noise(sec) * np.exp(-T(sec) * 9)
    ir = lp(ir, 3500)
    n = len(x) + len(ir)
    y = np.zeros(n); y[: len(x) + len(ir) - 1] = np.convolve(x, ir)
    y = y / (np.abs(y).max() + 1e-9) * (np.abs(x).max() + 1e-9)
    return np.concatenate([x, np.zeros(len(ir))]) * (1 - wet) + y * wet


def finish(x, level_db, fade=0.03):
    """Round off the top, trim silence, fade the tail, set the level (loudest 60 ms window)."""
    x = lp(x, 7500, 2)
    nz = np.nonzero(np.abs(x) > 1e-4)[0]
    x = x[: nz[-1] + 1] if len(nz) else x
    f = min(int(fade * SR), len(x) // 3)
    if f > 0:
        x[-f:] *= np.linspace(1, 0, f)
    w = int(0.06 * SR)
    pw = np.convolve(x ** 2, np.ones(w) / w, mode='same').max() ** 0.5 if len(x) > w else np.sqrt(np.mean(x ** 2))
    x = x * (10 ** (level_db / 20) / (pw + 1e-12))
    pk = np.abs(x).max()
    if pk > 0.89:
        x *= 0.89 / pk
    return x


def write(name, x):
    pcm = (np.clip(x, -1, 1) * 32767).astype('<i2').tobytes()
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 's16le', '-ar', str(SR), '-ac', '1', '-i', '-',
                    '-c:a', 'libvorbis', '-q:a', '4', os.path.join(OUT, f'{name}.ogg')], input=pcm, check=True)


# ── the sounds (name → (function, level dBFS of the loudest 60 ms)) ─────────
SOUNDS = {}


def sound(level):
    def deco(fn):
        SOUNDS[fn.__name__] = (fn, level)
        return fn
    return deco


# menus
@sound(-27)
def cursor():       # a soft wooden tock
    return gm([(0, 0.08, 'marimba', 'A5', 58)], 0.18, reverb=0.2, name='cursor')


@sound(-23)
def select():       # two kalimba notes, up a fourth
    return gm([(0, 0.1, 'kalimba', 'E5', 72), (0.06, 0.2, 'kalimba', 'A5', 78)], 0.4, name='select')


@sound(-25)
def cancel():       # the same, falling and quieter
    return gm([(0, 0.1, 'kalimba', 'A5', 62), (0.06, 0.2, 'kalimba', 'E5', 58)], 0.4, name='cancel')


@sound(-32)
def ui_text():      # the faint tick while dialogue types out
    return glide(1200, 1000, 0.018) * env(0.018, 0.001, curve=3) * 0.6


@sound(-24)
def ui_bump():      # walking into a wall
    return lp(glide(140, 70, 0.09) * env(0.09, 0.002, curve=2), 900)


@sound(-21)
def ui_coin():      # money
    return gm([(0, 0.12, 'vibes', 'B5', 80), (0.07, 0.4, 'vibes', 'E6', 84)], 0.6, name='coin')


@sound(-24)
def ui_jump():      # hopping down a ledge
    return bp(noise(0.16), 400, 2200) * env(0.16, 0.06, curve=1.5) * 0.7 + glide(220, 330, 0.16) * env(0.16, 0.02) * 0.3


@sound(-22)
def ui_cut():       # clearing a bramble
    swish = bp(noise(0.22), 1200, 5000) * env(0.22, 0.03, curve=2)
    snip = bp(noise(0.03), 2000, 6000) * env(0.03, 0.001, curve=3)
    return mix((0, swish), (0.08, snip * 0.8), (0.14, snip * 0.6))


@sound(-21)
def ui_splash():
    parts = [(0, lp(noise(0.5), 1800) * env(0.5, 0.01, curve=3))]
    for k in range(6):
        f = rng.uniform(500, 1200)
        parts.append((0.05 + k * 0.05, glide(f, f * 1.8, 0.06) * env(0.06, 0.003) * 0.25))
    return mix(*parts)


# world
@sound(-34)
def step():         # soft footfall (played every step, so very quiet)
    return mix((0, lp(noise(0.05), 900) * env(0.05, 0.004, curve=3)), (0, lp(glide(110, 70, 0.04), 400) * env(0.04, 0.002) * 0.4))


@sound(-21)
def door():         # a wooden door and the room behind it
    knock = lp(glide(120, 65, 0.22) * env(0.22, 0.003, curve=2), 700)
    wood = bp(noise(0.12), 250, 1500) * env(0.12, 0.002, curve=3) * 0.6
    air = bp(noise(0.35), 300, 1200) * env(0.35, 0.12, curve=1.5) * 0.15
    return room(mix((0, air), (0.02, knock), (0.02, wood)), 0.4, 0.2)


@sound(-18)
def spotted():      # a trainer's eyes meet yours: a quick pizzicato-and-horn sting
    return gm([(0, 0.15, 'pizz', 'E3', 100), (0, 0.15, 'pizz', 'B3', 96), (0.09, 0.35, 'horn', 'E4', 92), (0.09, 0.35, 'horn', 'G4', 88),
               (0.09, 0.35, 'strings', 'B4', 84), (0.09, 0.35, 'strings', 'E5', 80), (0, 0.4, 'timpani', 'E2', 90)], 0.75, name='spotted')


@sound(-19)
def encounter():    # the wild-battle swoop: a harp sweep over a rising whoosh
    notes = [(k * 0.028, 0.5, 'harp', n, 70 + k * 2) for k, n in enumerate(['E4', 'G4', 'B4', 'D5', 'E5', 'G5', 'B5', 'D6', 'E6'])]
    harp = gm(notes + [(0.25, 0.6, 'strings', 'B4', 70), (0.25, 0.6, 'strings', 'E5', 70)], 1.1, name='encounter')
    whoosh = bp(noise(0.9), 300, 2500) * env(0.9, 0.55, curve=1.2) * 0.35
    return mix((0, harp), (0, whoosh))


@sound(-18)
def encounter_jingle():     # a trainer battle begins: brass and strings rush in
    notes = [(k * 0.045, 0.2, 'strings', n, 80 + k * 3) for k, n in enumerate(['A4', 'B4', 'C5', 'D5', 'E5'])]
    notes += [(0.25, 0.5, 'brass', n, 96) for n in ('A3', 'E4', 'A4', 'C5')] + [(0.25, 0.6, 'timpani', 'A2', 100)]
    return gm(notes, 1.0, name='enc_trainer')


# battle
@sound(-19)
def attack():       # a move being thrown: soft whoosh
    return bp(noise(0.24), 350, 2400) * env(0.24, 0.1, curve=1.3)


@sound(-17)
def hit():
    body = lp(glide(170, 55, 0.22) * env(0.22, 0.002, curve=2.2), 900)
    slap = bp(noise(0.06), 400, 2600) * env(0.06, 0.001, curve=3) * 0.55
    return room(mix((0, body), (0, slap)), 0.25, 0.12)


@sound(-15)
def hit_super():    # a super-effective hit: deeper, with a bright crack on top
    body = lp(glide(150, 42, 0.38) * env(0.38, 0.002, curve=2), 800)
    sub = lp(noise(0.4), 180) * env(0.4, 0.004, curve=2) * 1.5
    crack = bp(noise(0.07), 900, 4200) * env(0.07, 0.001, curve=3) * 0.7
    return room(mix((0, body), (0, sub), (0, crack), (0.07, crack * 0.4)), 0.35, 0.15)


@sound(-20)
def faint():        # a Morph faints: a soft falling tone and a bump
    fall = lp(glide(420, 110, 0.6, 'tri') * env(0.6, 0.02, curve=1.2), 1500) * 0.6
    thud = lp(glide(120, 50, 0.25) * env(0.25, 0.003, curve=2), 600)
    return room(mix((0, fall), (0.5, thud)), 0.3, 0.15)


@sound(-20)
def level_up():
    return gm([(k * 0.06, 0.3, 'marimba', n, 80 + k * 4) for k, n in enumerate(['C5', 'E5', 'G5', 'C6'])], 0.7, name='lvl')


@sound(-19)
def heal():
    return gm([(k * 0.07, 0.6, 'vibes', n, 76) for k, n in enumerate(['F5', 'A5', 'C6', 'F6'])] + [(0, 0.8, 'harp', 'F4', 64)], 1.0, name='heal')


@sound(-19)
def evolve():       # shimmering glissando
    notes = [(k * 0.035, 0.8, 'harp', n, 66 + k) for k, n in enumerate(['Eb4', 'G4', 'Bb4', 'D5', 'Eb5', 'G5', 'Bb5', 'D6', 'Eb6'])]
    notes += [(0.3 + k * 0.08, 0.6, 'celesta', n, 60) for k, n in enumerate(['Bb5', 'Eb6', 'G6'])]
    return gm(notes, 1.4, name='evolve')


@sound(-20)
def capture_shake():    # the capsule wobbles
    return gm([(0, 0.1, 'drum', 76, 90), (0.14, 0.1, 'drum', 77, 70)], 0.35, reverb=0.25, name='shake')


@sound(-19)
def capture_fail():     # it breaks free: a pop and a puff
    pop = glide(260, 900, 0.07) * env(0.07, 0.002, curve=2) * 0.8
    puff = bp(noise(0.3), 500, 3000) * env(0.3, 0.02, curve=2) * 0.5
    return mix((0, pop), (0.02, puff))


@sound(-18)
def capture_success():  # click, then a little chime
    return gm([(0, 0.1, 'drum', 76, 100), (0.12, 0.5, 'vibes', 'G5', 84), (0.2, 0.7, 'vibes', 'D6', 84), (0.2, 0.7, 'harp', 'G4', 70)],
              1.0, name='caught')


def main(only):
    for name, (fn, level) in SOUNDS.items():
        if only and name not in only:
            continue
        x = finish(np.asarray(fn(), dtype=float), level)
        write(name, x)
        print(f'  {name:18s} {len(x) / SR:5.2f}s')


if __name__ == '__main__':
    main(sys.argv[1:])
