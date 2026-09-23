"""A small chiptune synthesiser for Tiamat's music and jingles.

Songs are written as bars of note tokens and rendered to seamless loops:
  melody:  "E5/2 G5/1 A5/1 | B5/4"   — note/length in steps (default step = 1/8 note)
           "r/2" rest, "~/2" tie (extend previous note)
  chords:  "Am F C G"                — one chord per bar (or "Am:4 F:4" with beats)
  drums:   "k.h.s.h.k.h.s.h."        — k kick, s snare, h hat, o open hat, per 16th

Every effect (echo) wraps around the loop so the seam is inaudible.
"""
import numpy as np

SR = 32000
NOTE = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
CHORD_Q = {
    '': [0, 4, 7], 'm': [0, 3, 7], '7': [0, 4, 7, 10], 'm7': [0, 3, 7, 10], 'maj7': [0, 4, 7, 11], 'sus2': [0, 2, 7],
    'sus4': [0, 5, 7], 'dim': [0, 3, 6], 'aug': [0, 4, 8], '5': [0, 7], 'add9': [0, 4, 7, 14], 'm9': [0, 3, 7, 14],
}


def midi(tok):
    """'C#4' -> 61"""
    n = NOTE[tok[0].upper()]
    i = 1
    while i < len(tok) and tok[i] in '#b':
        n += 1 if tok[i] == '#' else -1
        i += 1
    octv = int(tok[i:])
    return 12 * (octv + 1) + n


def freq(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)


def chord_notes(name, octave=3):
    """'F#m7' -> midi notes rooted in given octave."""
    root = name[0].upper()
    i = 1
    acc = 0
    while i < len(name) and name[i] in '#b':
        acc += 1 if name[i] == '#' else -1
        i += 1
    q = name[i:]
    bass = None
    if '/' in q:
        q, b = q.split('/')
        bass = NOTE[b[0]] + (1 if b[1:2] == '#' else -1 if b[1:2] == 'b' else 0)
    r = 12 * (octave + 1) + NOTE[root] + acc
    notes = [r + iv for iv in CHORD_Q[q]]
    return notes, (12 * (octave + 1) + bass if bass is not None else r)


# ── oscillators ────────────────────────────────────────────────────────────
def osc(kind, f, n, t0=0.0, vib=0.0, vib_rate=5.5, duty=0.5, detune=0.0):
    t = (np.arange(n) / SR) + t0
    if vib:
        # vibrato fades in after 120 ms
        depth = vib * np.clip((t - t0 - 0.12) / 0.25, 0, 1)
        ph = 2 * np.pi * f * t + (f * depth / vib_rate) * np.sin(2 * np.pi * vib_rate * t)
        phase = ph / (2 * np.pi)
    else:
        phase = f * t
    phase = phase % 1.0
    dt = min(0.49, f / SR)
    if kind == 'pulse':
        naive = np.where(phase < duty, 1.0, -1.0)
        return naive + _blep(phase, dt) - _blep((phase - duty) % 1.0, dt)
    if kind == 'tri':
        v = 4 * np.abs(phase - 0.5) - 1
        return np.round(v * 7.5) / 7.5          # 4-bit stepped, NES-like
    if kind == 'saw':
        return 2 * phase - 1 - _blep(phase, dt)
    if kind == 'sine':
        return np.sin(2 * np.pi * phase)
    if kind == 'bell':
        # 2-op FM bell
        mod = np.sin(2 * np.pi * f * 3.5 * t) * 2.2 * np.exp(-t * 6)
        return np.sin(2 * np.pi * f * t + mod)
    if kind == 'pad':
        out = 0
        for mul, off, g in ((1.0, 0.0, 1.0), (1.006, 0.3, 1.0), (0.497, 0.6, 0.6)):
            ph = (f * mul * t + off) % 1.0
            out = out + g * (2 * ph - 1 - _blep(ph, min(0.49, f * mul / SR)))
        return out / 2.6
    if kind == 'organ':
        return (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(4 * np.pi * f * t) + 0.25 * np.sin(6 * np.pi * f * t)) / 1.75
    raise ValueError(kind)


def _blep(t, dt):
    """PolyBLEP residual: removes most of the aliasing from hard waveform edges."""
    y = np.zeros_like(t)
    m = t < dt
    x = t[m] / dt
    y[m] = x + x - x * x - 1
    m = t > 1 - dt
    x = (t[m] - 1) / dt
    y[m] = x * x + x + x + 1
    return y


def env(n, a=0.005, d=0.08, s=0.7, r=0.04, gate=None):
    """ADSR with the release starting at `gate` samples."""
    gate = n if gate is None else min(gate, n)
    e = np.ones(n) * s
    ai = max(1, int(a * SR)); di = max(1, int(d * SR)); ri = max(1, int(r * SR))
    e[:ai] = np.linspace(0, 1, ai)[:min(ai, n)] if n >= ai else np.linspace(0, 1, n)
    if ai < n:
        seg = e[ai:ai + di]
        e[ai:ai + di] = np.linspace(1, s, di)[:len(seg)]
    if gate < n:
        tail = n - gate
        start = e[gate - 1] if gate > 0 else s
        e[gate:] = start * np.linspace(1, 0, tail)
    return e


def lowpass(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    # vectorised one-pole via lfilter when available
    try:
        from scipy.signal import lfilter
        return lfilter([1 - a], [1, -a], x)
    except ImportError:
        for i, v in enumerate(x):
            acc = (1 - a) * v + a * acc
            y[i] = acc
        return y


INSTR = {
    # name: (osc, duty, env(a,d,s,r), vib, gain, lowpass)
    'lead':    ('pulse', 0.25, (0.004, 0.10, 0.65, 0.05), 0.012, 0.22, 7000),
    'lead50':  ('pulse', 0.50, (0.004, 0.10, 0.60, 0.05), 0.010, 0.18, 6000),
    'lead12':  ('pulse', 0.125, (0.003, 0.08, 0.55, 0.04), 0.012, 0.22, 8000),
    'soft':    ('pulse', 0.50, (0.02, 0.2, 0.55, 0.12), 0.008, 0.15, 3000),
    'harm':    ('pulse', 0.50, (0.004, 0.15, 0.40, 0.04), 0.0, 0.10, 4500),
    'arp':     ('pulse', 0.25, (0.002, 0.06, 0.25, 0.02), 0.0, 0.09, 5000),
    'bass':    ('tri', 0.5, (0.002, 0.05, 0.85, 0.02), 0.0, 0.34, 20000),
    'bassp':   ('pulse', 0.5, (0.002, 0.08, 0.6, 0.02), 0.0, 0.12, 1400),
    'pad':     ('pad', 0.5, (0.25, 0.4, 0.75, 0.4), 0.0, 0.10, 1800),
    'bell':    ('bell', 0.5, (0.002, 0.6, 0.15, 0.4), 0.0, 0.20, 9000),
    'flute':   ('sine', 0.5, (0.04, 0.1, 0.8, 0.08), 0.018, 0.22, 9000),
    'organ':   ('organ', 0.5, (0.03, 0.1, 0.8, 0.1), 0.006, 0.16, 5000),
    'strings': ('saw', 0.5, (0.08, 0.3, 0.8, 0.2), 0.010, 0.10, 2400),
}


def render_note(instr, m, dur_s, amp=1.0):
    kind, duty, (a, d, s, r), vib, gain, lp = INSTR[instr]
    n = int((dur_s + r) * SR)
    x = osc(kind, freq(m), n, vib=vib, duty=duty)
    e = env(n, a, d, s, r, gate=int(dur_s * SR))
    y = x * e * gain * amp
    return y, lp


# ── drums ────────────────────────────────────────────────────────────────────
_rng = np.random.default_rng(1234)
NOISE = _rng.uniform(-1, 1, SR * 2)


def drum(kind, amp=1.0):
    if kind == 'k':
        n = int(0.16 * SR); t = np.arange(n) / SR
        f = 120 * np.exp(-t * 28) + 45
        ph = 2 * np.pi * np.cumsum(f) / SR
        return np.sin(ph) * np.exp(-t * 18) * 0.55 * amp
    if kind == 's':
        n = int(0.14 * SR); t = np.arange(n) / SR
        body = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30) * 0.25
        return (lowpass(NOISE[:n], 6000) * np.exp(-t * 22) * 0.32 + body) * amp
    if kind == 'h':
        n = int(0.04 * SR); t = np.arange(n) / SR
        x = NOISE[1000:1000 + n] - lowpass(NOISE[1000:1000 + n], 7000)
        return x * np.exp(-t * 90) * 0.22 * amp
    if kind == 'o':
        n = int(0.18 * SR); t = np.arange(n) / SR
        x = NOISE[3000:3000 + n] - lowpass(NOISE[3000:3000 + n], 6000)
        return x * np.exp(-t * 16) * 0.16 * amp
    if kind == 't':   # low tom
        n = int(0.2 * SR); t = np.arange(n) / SR
        f = 150 * np.exp(-t * 8) + 70
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 12) * 0.4 * amp
    if kind == 'c':   # crash
        n = int(0.9 * SR); t = np.arange(n) / SR
        x = NOISE[:n] - lowpass(NOISE[:n], 4000)
        return x * np.exp(-t * 4) * 0.14 * amp
    raise ValueError(kind)


# ── song rendering ───────────────────────────────────────────────────────────
class Song:
    def __init__(self, bpm, bars, beats_per_bar=4, step=0.5, swing=0.0):
        self.bpm, self.bars, self.bpb, self.step = bpm, bars, beats_per_bar, step
        self.spb = 60.0 / bpm
        self.length = bars * beats_per_bar * self.spb
        self.n = int(round(self.length * SR))
        self.bus = {}
        self.swing = swing

    def _bus(self, name):
        if name not in self.bus:
            self.bus[name] = [np.zeros(self.n + SR * 3), None]
        return self.bus[name]

    def add(self, bus, y, start_s, lp=None):
        b = self._bus(bus)
        i = int(start_s * SR)
        end = min(i + len(y), len(b[0]))
        b[0][i:end] += y[:end - i]
        if lp is not None:
            b[1] = lp

    def note(self, instr, m, beat, beats, amp=1.0, bus=None, legato=0.92, octave=0):
        start = beat * self.spb
        if self.swing and (beat * 2) % 1 == 0 and (beat * 2) % 2 == 1:
            start += self.swing * self.spb * 0.5
        y, lp = render_note(instr, m + 12 * octave, beats * self.spb * legato, amp)
        self.add(bus or instr, y, start, lp)

    def melody(self, instr, text, start_bar=0, step=None, amp=1.0, octave=0, bus=None, legato=0.92, transpose=0):
        """Tokens separated by spaces; '|' bar lines are ignored (for readability)."""
        step = step or self.step
        beat = start_bar * self.bpb
        events = []
        for tok in text.replace('|', ' ').split():
            if '/' in tok:
                name, ln = tok.split('/')
                ln = float(ln)
            else:
                name, ln = tok, 1.0
            if name == 'r':
                beat += ln * step
                continue
            if name == '~' and events:
                events[-1][2] += ln * step
                beat += ln * step
                continue
            vel = 1.0
            if name.endswith('!'):
                vel = 1.25; name = name[:-1]
            if name.endswith('_'):
                vel = 0.7; name = name[:-1]
            events.append([midi(name) + transpose, beat, ln * step, vel])
            beat += ln * step
        for m, b, l, v in events:
            self.note(instr, m, b, l, amp * v, bus=bus, legato=legato, octave=octave)
        return beat

    def chords(self, prog, start_bar=0, beats=None):
        """'Am F C G' or 'Am:2 F:2' → list of (chord, beat, length)."""
        out = []
        beat = start_bar * self.bpb
        for tok in prog.split():
            if ':' in tok:
                c, l = tok.split(':'); l = float(l)
            else:
                c, l = tok, float(beats or self.bpb)
            out.append((c, beat, l))
            beat += l
        return out

    def bassline(self, prog, pattern='r.r.', instr='bass', start_bar=0, octave=2, amp=1.0, bus='bass'):
        """pattern per beat-half: r root, f fifth, o octave, t third, '.' rest, '-' hold."""
        for c, b, l in self.chords(prog, start_bar):
            notes, root = chord_notes(c, octave)
            steps = int(l * 2)
            for i in range(steps):
                p = pattern[i % len(pattern)]
                if p in '.-':
                    continue
                hold = 1
                while i + hold < steps and pattern[(i + hold) % len(pattern)] == '-':
                    hold += 1
                m = {'r': root, 'f': root + 7, 'o': root + 12, 't': notes[1] if len(notes) > 1 else root, 'l': root - 12}[p]
                self.note(instr, m, b + i * 0.5, hold * 0.5, amp, bus=bus, legato=0.85)

    def arpeggio(self, prog, pattern='0121', instr='arp', start_bar=0, octave=4, rate=0.25, amp=1.0, bus='arp'):
        for c, b, l in self.chords(prog, start_bar):
            notes, _ = chord_notes(c, octave)
            ext = notes + [n + 12 for n in notes]
            steps = int(round(l / rate))
            for i in range(steps):
                idx = int(pattern[i % len(pattern)])
                self.note(instr, ext[idx % len(ext)], b + i * rate, rate, amp, bus=bus, legato=0.8)

    def pad(self, prog, instr='pad', start_bar=0, octave=4, amp=1.0, bus='pad'):
        for c, b, l in self.chords(prog, start_bar):
            notes, _ = chord_notes(c, octave)
            for m in notes[:4]:
                self.note(instr, m, b, l, amp / max(1, len(notes) ** 0.5), bus=bus, legato=0.98)

    def stabs(self, prog, rhythm, instr='harm', start_bar=0, octave=4, amp=1.0, bus='stabs'):
        """rhythm: string of 8th steps, 'x' = chord stab."""
        for c, b, l in self.chords(prog, start_bar):
            notes, _ = chord_notes(c, octave)
            for i in range(int(l * 2)):
                if rhythm[i % len(rhythm)] == 'x':
                    for m in notes[:3]:
                        self.note(instr, m, b + i * 0.5, 0.45, amp * 0.7, bus=bus, legato=0.7)

    def drums(self, pattern, bars, start_bar=0, amp=1.0, fill=None):
        """pattern: 16 chars per bar of 4/4 (or bpb*4)."""
        spb16 = self.spb / 4
        per_bar = self.bpb * 4
        for bar in range(start_bar, start_bar + bars):
            pat = fill if (fill and bar == start_bar + bars - 1) else pattern
            for i in range(per_bar):
                ch = pat[i % len(pat)]
                if ch in 'kshotc':
                    y = drum(ch, amp)
                    self.add('drums', y, (bar * self.bpb) * self.spb + i * spb16)

    def mix(self, gains=None, echo=None, target_rms=0.2, peak=0.92, loop=True):
        gains = gains or {}
        out = np.zeros(self.n)
        for name, (buf, lp) in self.bus.items():
            x = buf.copy()
            if lp:
                x = lowpass(x, lp)
            if loop:
                # fold the tail past the loop end back onto the start → seamless loop
                body = x[:self.n].copy()
                tail = x[self.n:]
                k = min(len(tail), self.n)
                body[:k] += tail[:k]
                x = body
            else:
                x = x[:self.n + SR * 2]
            g = gains.get(name, 1.0)
            if len(x) > len(out):
                out = np.pad(out, (0, len(x) - len(out)))
            out[:len(x)] += x * g
        if echo:
            delay_s, fb, wet = echo
            d = int(delay_s * SR)
            e = np.zeros_like(out)
            src = out.copy()
            for k in range(1, 4):
                e += np.roll(src, d * k) * (fb ** (k - 1)) if loop else np.pad(src, (d * k, 0))[:len(src)] * (fb ** (k - 1))
            out = out + e * wet
        rms = np.sqrt(np.mean(out ** 2)) + 1e-9
        out *= target_rms / rms
        # soft-knee limiter: untouched below the knee, smoothly squashed above it
        knee = 0.7 * peak
        mag = np.abs(out)
        over = mag > knee
        out[over] = np.sign(out[over]) * (knee + (peak - knee) * np.tanh((mag[over] - knee) / (peak - knee)))
        return out.astype(np.float32)


def write_ogg(path, x, quality=3):
    import subprocess
    pcm = (np.clip(x, -1, 1) * 32767).astype('<i2').tobytes()
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 's16le', '-ar', str(SR), '-ac', '1', '-i', '-',
                    '-c:a', 'libvorbis', '-q:a', str(quality), path], input=pcm, check=True)
