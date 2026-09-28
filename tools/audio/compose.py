"""Tiamat soundtrack composer: hand-written melodies and chord charts → full arrangements → General MIDI.

Every song in score.py is a small dict: tempo, metre, key, a chord chart per section, hand-written melody lines,
and an arrangement (which instruments play which accompaniment pattern). This module turns that into a
humanised, swung multi-track MIDI file that render.py plays through FluidSynth with the FluidR3 GM soundfont.

Melody syntax (one string per section, bars split by '|', every bar is checked for length):
    'E5:1 G5:.5 A5:.5 B5:1.5 A5:.5 | G5:2 r:1 E5:1 |'
    note = <name><octave>[:<beats>]   rest = r[:<beats>]   the duration carries over to following notes.
    A trailing '~' ties the note into the next one of the same pitch (e.g. 'G5:1~ | G5:2').
Chord charts: one entry per bar, 1–4 chords split by spaces: 'Imaj7 | vi7 | ii7 V7 | I'.
"""
import math, random, re, zlib
import mido

TPB = 480
NOTE_PC = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
MAJOR_DEG = {'I': 0, 'II': 2, 'III': 4, 'IV': 5, 'V': 7, 'VI': 9, 'VII': 11}
MODES = {
    'major': [0, 2, 4, 5, 7, 9, 11], 'minor': [0, 2, 3, 5, 7, 8, 10], 'dorian': [0, 2, 3, 5, 7, 9, 10],
    'mixolydian': [0, 2, 4, 5, 7, 9, 10], 'lydian': [0, 2, 4, 6, 7, 9, 11], 'phrygian': [0, 1, 3, 5, 7, 8, 10],
    'harmonic': [0, 2, 3, 5, 7, 8, 11],
}
# General MIDI programs (0-based) used by the score
GM = dict(piano=0, bright_piano=1, rhodes=4, ep2=5, harpsichord=6, clav=7, celesta=8, glock=9, musicbox=10, vibes=11,
          marimba=12, xylo=13, bells=14, organ=16, church_organ=19, accordion=21, nylon=24, steel=25, jazz_gtr=26,
          clean_gtr=27, muted_gtr=28, ac_bass=32, finger_bass=33, pick_bass=34, fretless=35, slap=36, slap2=37,
          violin=40, viola=41, cello=42, contrabass=43, trem_strings=44, pizz=45, harp=46, timpani=47,
          strings=48, slow_strings=49, synth_strings=50, choir=52, oohs=53, trumpet=56, trombone=57, tuba=58,
          muted_tpt=59, horn=60, brass=61, soprano_sax=64, alto_sax=65, tenor_sax=66, oboe=68, english_horn=69,
          bassoon=70, clarinet=71, piccolo=72, flute=73, recorder=74, pan_flute=75, shakuhachi=77, whistle=78,
          ocarina=79, newage_pad=88, warm_pad=89, choir_pad=91, bowed_pad=92, halo_pad=94, koto=107, kalimba=108,
          fiddle=110, steel_drums=114, taiko=116, melodic_tom=117)
KITS = dict(standard=0, room=8, jazz=32, brush=40, orchestra=48)


# ── pitch helpers ──────────────────────────────────────────────────────────
def note_num(name):
    m = re.fullmatch(r'([A-G])([#b]*)(-?\d)', name)
    if not m:
        raise ValueError(f'bad note {name!r}')
    pc = NOTE_PC[m.group(1)] + m.group(2).count('#') - m.group(2).count('b')
    return 12 * (int(m.group(3)) + 1) + pc


def key_pc(key):
    return (NOTE_PC[key[0]] + key[1:].count('#') - key[1:].count('b')) % 12


CHORD_RE = re.compile(r'^(b|#)?(VII|VI|V|IV|III|II|I|vii|vi|v|iv|iii|ii|i)(.*?)(?:/(b|#)?(VII|VI|V|IV|III|II|I|vii|vi|v|iv|iii|ii|i|[A-G][#b]?))?$')


def parse_chord(sym, key):
    """Roman numeral → (root pitch class, intervals above the root, bass pitch class).
    Upper case = major, lower case = minor. Suffixes: 7 maj7 9 maj9 add9 6 sus2 sus4 dim ø + 7sus."""
    m = CHORD_RE.match(sym)
    if not m:
        raise ValueError(f'bad chord {sym!r}')
    acc, num, suf, bacc, bass = m.groups()
    root = (key_pc(key) + MAJOR_DEG[num.upper()] + (1 if acc == '#' else -1 if acc == 'b' else 0)) % 12
    minor = num.islower()
    third = 3 if minor else 4
    iv = [0, third, 7]
    if suf in ('dim', '°'):
        iv = [0, 3, 6]
    elif suf in ('dim7', '°7'):
        iv = [0, 3, 6, 9]
    elif suf in ('ø', 'ø7', 'm7b5'):
        iv = [0, 3, 6, 10]
    elif suf == '+':
        iv = [0, 4, 8]
    elif suf == '7':
        iv = [0, third, 7, 10]
    elif suf == 'maj7':
        iv = [0, third, 7, 11]
    elif suf == '9':
        iv = [0, third, 7, 10, 14]
    elif suf == 'maj9':
        iv = [0, third, 7, 11, 14]
    elif suf == 'add9':
        iv = [0, third, 7, 14]
    elif suf == '6':
        iv = [0, third, 7, 9]
    elif suf == '69':
        iv = [0, third, 7, 9, 14]
    elif suf == 'sus2':
        iv = [0, 2, 7]
    elif suf == 'sus4':
        iv = [0, 5, 7]
    elif suf == '7sus':
        iv = [0, 5, 7, 10]
    elif suf == '11':
        iv = [0, 7, 10, 14, 17]
    elif suf == '13':
        iv = [0, 4, 10, 14, 21]
    elif suf == '7b9':
        iv = [0, 4, 7, 10, 13]
    elif suf:
        raise ValueError(f'unknown chord suffix {suf!r} in {sym}')
    bass_pc = root
    if bass:
        if bass[0] in NOTE_PC:
            bass_pc = key_pc(bass)
        else:
            bass_pc = (key_pc(key) + MAJOR_DEG[bass.upper()] + (1 if bacc == '#' else -1 if bacc == 'b' else 0)) % 12
    return root, iv, bass_pc


class Chord:
    def __init__(self, sym, key, start, dur):
        self.sym, self.start, self.dur = sym, start, dur
        self.root, self.iv, self.bass = parse_chord(sym, key)
        self.pcs = sorted({(self.root + i) % 12 for i in self.iv})
        self.triad = [(self.root + i) % 12 for i in self.iv[:3]]

    def tones_in(self, lo, hi, pcs=None):
        pcs = pcs or self.pcs
        return [n for n in range(lo, hi + 1) if n % 12 in pcs]


def parse_chart(chart, key, bar_beats, t0=0.0):
    bars = [b.strip() for b in chart.split('|') if b.strip()]
    out = []
    for i, bar in enumerate(bars):
        syms = bar.split()
        d = bar_beats / len(syms)
        for k, s in enumerate(syms):
            out.append(Chord(s, key, t0 + i * bar_beats + k * d, d))
    return out, len(bars)


def parse_melody(text, bar_beats, t0=0.0, name='melody'):
    """→ list of (start, dur, pitch or None). Validates bar lengths."""
    notes = []
    bars = [b.strip() for b in text.split('|')]
    if bars and bars[-1] == '':
        bars = bars[:-1]
    dur = 1.0
    t = t0
    for bi, bar in enumerate(bars):
        used = 0.0
        for tok in bar.split():
            tie = tok.endswith('~')
            tok = tok.rstrip('~')
            if ':' in tok:
                tok, d = tok.split(':')
                dur = float(d)
            pitch = None if tok == 'r' else note_num(tok)
            notes.append([t + used, dur, pitch, tie])
            used += dur
        if abs(used - bar_beats) > 1e-6:
            raise ValueError(f'{name}: bar {bi + 1} has {used} beats, expected {bar_beats}: {bar!r}')
        t += bar_beats
    # merge ties
    merged = []
    for n in notes:
        if merged and merged[-1][3] and merged[-1][2] == n[2]:
            merged[-1][1] += n[1]
            merged[-1][3] = n[3]
        else:
            merged.append(n)
    return [(s, d, p) for s, d, p, _ in merged], len(bars)


def chord_at(chords, t):
    for c in chords:
        if c.start - 1e-6 <= t < c.start + c.dur - 1e-6:
            return c
    return chords[-1]


def check_melody(notes, chords, key, mode, bar_beats, label):
    """Warn about melody notes that clash with the harmony on strong beats."""
    warns = []
    scale = {(key_pc(key) + s) % 12 for s in MODES[mode]}
    for s, d, p in notes:
        if p is None:
            continue
        c = chord_at(chords, s)
        pc = p % 12
        strong = abs(s % 1) < 1e-6 and (int(round(s)) % bar_beats == 0 or (bar_beats == 4 and int(round(s)) % 4 == 2) or d >= 1.5)
        if not strong or pc in c.pcs:
            continue
        rel = (pc - c.root) % 12
        clash = any((pc - t) % 12 == 1 for t in c.pcs)          # a semitone above a chord tone = minor 9th
        clash = clash or (rel == 6 and 10 not in c.iv and 6 not in c.iv)   # #11 held over a plain chord
        if clash or (pc not in scale and rel not in (2, 9)):
            bar = int(s // bar_beats) + 1
            warns.append(f'{label}: bar {bar} beat {s % bar_beats + 1:g}: {p} over {c.sym}')
    return warns


# ── voicing ────────────────────────────────────────────────────────────────
def voice(chord, prev, lo, hi, n=4):
    """Pick an n-note voicing of chord within [lo, hi] closest to prev (smooth voice leading)."""
    pcs = [(chord.root + i) % 12 for i in chord.iv]
    # prefer 3rd and 7th/extensions, drop the fifth first when there are more tones than voices
    order = pcs[:]
    if len(order) > n and len(order) >= 3:
        order.pop(2)
    order = order[:n]
    while len(order) < n:
        order.append(order[len(order) % len(pcs)])
    best, best_cost = None, 1e9
    for base in range(lo, hi - 6):
        v = []
        for pc in order:
            cand = [x for x in range(base, hi + 1) if x % 12 == pc and x not in v]
            if not cand:
                break
            v.append(cand[0])
        if len(v) < n:
            continue
        v.sort()
        if v[-1] - v[0] > 14 or v[-1] > hi:
            continue
        cost = sum(abs(a - b) for a, b in zip(v, prev)) if prev else abs(sum(v) / n - (lo + hi) / 2) * 2
        cost += 20 * sum(1 for a, b in zip(v, v[1:]) if b - a == 1)      # no semitone rubs inside a voicing
        if cost < best_cost:
            best, best_cost = v, cost
    return best or sorted(lo + (pc - lo) % 12 for pc in order)


# ── the arrangement ────────────────────────────────────────────────────────
class Song:
    def __init__(self, spec):
        self.spec = spec
        self.tempo = spec['tempo']
        self.bar = spec.get('bar', 4)
        self.key = spec['key']
        self.mode = spec.get('mode', 'major')
        self.swing = spec.get('swing', 0.5)
        self.swing16 = spec.get('swing16', False)
        self.rng = random.Random(spec.get('seed', zlib.crc32(spec['name'].encode())))
        self.events = []        # (start, dur, part, pitch, vel)
        self.parts = {}         # part name → dict(program, channel, vol, pan, rev, cho, kit)
        self.chords = []
        self.warnings = []
        self.sections = []
        self.roles = {}         # part → mix role override ('double', 'counter'...)

    # parts
    def part(self, name, program, vol=100, pan=64, rev=50, cho=10, drums=False):
        if name not in self.parts:
            self.parts[name] = dict(program=program, vol=vol, pan=pan, rev=rev, cho=cho, drums=drums)
        return name

    def note(self, part, start, dur, pitch, vel):
        if pitch is None or dur <= 0:
            return
        self.events.append((start, dur, part, int(pitch), max(1, min(127, int(vel)))))

    # timing
    def swing_t(self, t):
        s = self.swing
        if s == 0.5:
            return t
        unit = 0.5 if self.swing16 else 1.0
        b = math.floor(t / unit + 1e-9) * unit
        p = (t - b) / unit
        p = p * 2 * s if p <= 0.5 else s + (p - 0.5) * 2 * (1 - s)
        return b + p * unit


def build(spec):
    """spec → Song with every event placed (sections in the order of spec['form'])."""
    S = Song(spec)
    bb = S.bar
    t = 0.0
    for sec_name in spec['form']:
        sec = spec['sections'][sec_name]
        chords, nbars = parse_chart(sec['chords'], S.key, bb, t)
        S.chords += chords
        S.sections.append((sec_name, t, nbars))
        for layer in sec.get('lead', []) + spec.get('lead_all', []):
            inst, text = layer[0], layer[1]
            opts = layer[2] if len(layer) > 2 else {}
            notes, mbars = parse_melody(text, bb, t, f"{spec['name']}.{sec_name}.{inst}")
            if mbars != nbars:
                raise ValueError(f"{spec['name']}.{sec_name}: melody has {mbars} bars, chords {nbars}")
            S.warnings += check_melody(notes, chords, S.key, S.mode, bb, f"{spec['name']}.{sec_name}.{inst}")
            play_lead(S, inst, notes, chords, opts)
        for acc in sec.get('acc', spec.get('acc', [])):
            ACC[acc[0]](S, chords, t, nbars, **(acc[1] if len(acc) > 1 else {}))
        dr = sec.get('drums', spec.get('drums'))
        if dr:
            before = set(S.parts)
            DRUMS[dr[0]](S, t, nbars, **(dr[1] if len(dr) > 1 else {}))
            for p in set(S.parts) - before:
                S.roles.setdefault(p, f'drum_{dr[0]}')
        t += nbars * bb
    S.length = t
    resolve_clashes(S)
    return S


PRIORITY = ['bass', 'lead', 'double', 'counter', 'comp', 'strum', 'pick', 'ost', 'stab', 'skank', 'pizz', 'arp', 'pad', 'bells']


def part_role(S, part):
    if part in S.roles:
        return S.roles[part]
    for pre in ('pad', 'arp', 'pick', 'strum', 'comp', 'skank', 'ost', 'stab', 'bass', 'counter', 'bells'):
        if part.startswith(pre + '_'):
            return pre
    return 'pizz' if part == 'pizz' else ('lead' if part not in ('timpani', 'taiko') else 'drum')


def resolve_clashes(S):
    """Held notes a semitone (or minor ninth) apart in different parts rub unpleasantly: drop the note from the
    less important part. Melody and bass always win; a bass passing note (off the chord, one beat or less) is let be."""
    rank = {r: i for i, r in enumerate(PRIORITY)}
    evs = [e for e in S.events if not S.parts[e[2]]['drums'] and part_role(S, e[2]) != 'drum']
    evs.sort()
    drop = set()
    for i, e1 in enumerate(evs):
        s1, d1, p1, n1, _ = e1
        if e1 in drop:
            continue
        for e2 in evs[i + 1:]:
            s2, d2, p2, n2, _ = e2
            if s2 >= s1 + d1:
                break
            if p1 == p2 or e2 in drop or abs(n1 - n2) not in (1, 13):
                continue
            if min(s1 + d1, s2 + d2) - max(s1, s2) < 0.5 or min(d1, d2) < 0.75:
                continue
            r1, r2 = part_role(S, p1), part_role(S, p2)
            loser = e2 if rank.get(r1, 5) <= rank.get(r2, 5) else e1
            lr = part_role(S, loser[2])
            if lr in ('lead', 'bass'):
                other = e1 if loser is e2 else e2
                if part_role(S, other[2]) in ('lead', 'bass'):
                    continue          # melody against a bass passing note: leave it
                loser = other
            drop.add(loser)
            if loser is e1:
                break
    if drop:
        S.events = [e for e in S.events if e not in drop]
    S.dropped = len(drop)


LEAD_DEF = dict(flute=('flute', 92, 60, 58), piano=('piano', 96, 64, 50), ocarina=('ocarina', 88, 70, 55),
                oboe=('oboe', 92, 58, 55), clarinet=('clarinet', 96, 66, 50), horn=('horn', 98, 62, 60),
                violin=('violin', 92, 58, 58), cello=('cello', 96, 70, 55), whistle=('whistle', 80, 64, 60),
                trumpet=('trumpet', 88, 60, 50), muted_tpt=('muted_tpt', 92, 64, 45), vibes=('vibes', 98, 64, 55),
                rhodes=('rhodes', 98, 64, 45), steel_drums=('steel_drums', 90, 64, 45), marimba=('marimba', 104, 64, 45),
                celesta=('celesta', 96, 64, 60), kalimba=('kalimba', 104, 64, 55), shakuhachi=('shakuhachi', 90, 60, 65),
                pan_flute=('pan_flute', 88, 64, 60), fiddle=('fiddle', 88, 60, 55), recorder=('recorder', 92, 64, 55),
                strings=('strings', 100, 64, 60), choir=('choir', 96, 64, 70), brass=('brass', 94, 64, 50),
                alto_sax=('alto_sax', 90, 70, 45), tenor_sax=('tenor_sax', 92, 58, 45), harp=('harp', 100, 70, 60),
                clav=('clav', 92, 64, 35), musicbox=('musicbox', 90, 64, 60), glock=('glock', 80, 64, 60),
                english_horn=('english_horn', 94, 60, 58), koto=('koto', 100, 60, 55), accordion=('accordion', 86, 64, 45),
                bassoon=('bassoon', 96, 64, 50), piccolo=('piccolo', 78, 64, 55), trombone=('trombone', 92, 64, 50),
                xylo=('xylo', 90, 64, 50), clean_gtr=('clean_gtr', 94, 60, 45), nylon=('nylon', 100, 60, 50),
                jazz_gtr=('jazz_gtr', 96, 60, 45), soprano_sax=('soprano_sax', 88, 64, 50), viola=('viola', 94, 64, 58),
                trem_strings=('trem_strings', 92, 64, 60), bells=('bells', 80, 64, 60), oohs=('oohs', 92, 64, 70),
                harpsichord=('harpsichord', 88, 64, 45), organ=('church_organ', 82, 64, 60), tuba=('tuba', 96, 64, 40),
                timpani=('timpani', 100, 64, 55), taiko=('taiko', 100, 64, 45), slow_strings=('slow_strings', 100, 64, 60))


def play_lead(S, inst, notes, chords, opts):
    prog, vol, pan, rev = LEAD_DEF[inst]
    name = opts.get('as', inst)
    S.part(name, GM[prog], vol=opts.get('vol', vol), pan=opts.get('pan', pan), rev=opts.get('rev', rev), cho=opts.get('cho', 12))
    if opts.get('role'):
        S.roles[name] = opts['role']
    base = opts.get('vel', 88)
    octave = opts.get('octave', 0) * 12
    legato = opts.get('legato', 0.94)
    harm = opts.get('harm')     # 'third' / 'sixth' below, diatonic
    scale = [(key_pc(S.key) + x) % 12 for x in MODES[S.mode]]
    for i, (s, d, p) in enumerate(notes):
        if p is None:
            continue
        beat = s % S.bar
        accent = 8 if abs(beat) < 1e-6 else (4 if abs(beat % 1) < 1e-6 else -2)
        v = base + accent + S.rng.randint(-5, 5) + (6 if d >= 2 else 0)
        S.note(name, s, d * legato, p + octave, v)
        if harm:
            hp = diatonic_below(p + octave, 2 if harm == 'third' else 5, scale)
            c = chord_at(chords, s)
            if (hp % 12) not in c.pcs and d >= 1:
                hp = max([x for x in c.tones_in(hp - 4, p + octave - 3)] or [hp])
            S.note(name, s, d * legato, hp, v - 10)


def diatonic_below(p, steps, scale):
    q = p
    k = 0
    while k < steps:
        q -= 1
        if q % 12 in scale:
            k += 1
    return q


# ── accompaniment patterns ─────────────────────────────────────────────────
ACC = {}


def acc(fn):
    ACC[fn.__name__] = fn
    return fn


def _chords_in(chords, t0, nbars, bb):
    return [c for c in chords if t0 - 1e-6 <= c.start < t0 + nbars * bb - 1e-6]


@acc
def pad(S, chords, t0, nbars, inst='strings', lo=52, hi=72, vel=58, voices=4, vol=84, pan=64, rev=70, swell=False, name=None):
    name = S.part(name or f'pad_{inst}', GM[inst], vol=vol, pan=pan, rev=rev, cho=25)
    prev = None
    for c in _chords_in(chords, t0, nbars, S.bar):
        v = voice(c, prev, lo, hi, voices)
        prev = v
        for p in v:
            S.note(name, c.start, c.dur * 0.98, p, vel + (8 if swell else 0) + S.rng.randint(-3, 3))


@acc
def arp(S, chords, t0, nbars, inst='harp', lo=55, hi=79, step=0.5, vel=62, shape='updown', vol=90, pan=70, rev=65, name=None, accent_first=10):
    """Arpeggio through the chord tones (harp, piano, celesta, marimba, kalimba...)."""
    name = S.part(name or f'arp_{inst}', GM[inst], vol=vol, pan=pan, rev=rev)
    for c in _chords_in(chords, t0, nbars, S.bar):
        tones = c.tones_in(lo, hi)
        if not tones:
            continue
        seq = tones + tones[-2:0:-1] if shape == 'updown' else (tones if shape == 'up' else tones[::-1])
        if shape == 'rolling':   # 1-5-8-10-8-5 style
            b = [x for x in tones if x % 12 == c.bass] or tones
            b0 = b[0]
            up = [x for x in tones if x > b0][:4]
            seq = [b0] + up + up[-2:0:-1]
        n = int(round(c.dur / step))
        for k in range(n):
            p = seq[k % len(seq)]
            t = c.start + k * step
            S.note(name, t, min(step * 1.8, c.start + c.dur - t + 0.05), p, vel + (accent_first if k == 0 else 0) + S.rng.randint(-6, 4))


@acc
def fingerpick(S, chords, t0, nbars, inst='nylon', lo=40, hi=71, vel=64, vol=96, pan=58, rev=45, name=None):
    """Travis-style picking: bass on the beat, chord tones between."""
    name = S.part(name or f'pick_{inst}', GM[inst], vol=vol, pan=pan, rev=rev)
    for c in _chords_in(chords, t0, nbars, S.bar):
        bass = [x for x in range(lo, lo + 12) if x % 12 == c.bass][0]
        fifth = bass + 7 if (bass + 7) % 12 in c.pcs else bass + 12
        top = [x for x in c.tones_in(bass + 10, hi)][:3] or [bass + 12]
        n = int(round(c.dur / 0.5))
        for k in range(n):
            t = c.start + k * 0.5
            if k % 2 == 0:
                S.note(name, t, min(0.9, c.start + c.dur - t + 0.05), bass if (k // 2) % 2 == 0 else fifth, vel + 6 + S.rng.randint(-4, 4))
            else:
                S.note(name, t, min(0.8, c.start + c.dur - t + 0.05), top[(k // 2) % len(top)], vel - 6 + S.rng.randint(-5, 3))


@acc
def strum(S, chords, t0, nbars, inst='steel', lo=48, hi=69, vel=60, pattern='folk', vol=88, pan=46, rev=40, name=None):
    """Strummed guitar with down/up strokes (a few ms between strings)."""
    name = S.part(name or f'strum_{inst}', GM[inst], vol=vol, pan=pan, rev=rev)
    pats = {'folk': [(0, 1, 1), (1, .5, 1), (1.5, .5, -1), (2.5, .5, -1), (3, .5, 1), (3.5, .5, -1)],
            'waltz': [(0, 1, 1), (1, 1, 1), (2, 1, 1)],
            'half': [(0, 2, 1), (2, 2, 1)]}
    prev = None
    for c in _chords_in(chords, t0, nbars, S.bar):
        v = voice(c, prev, lo, hi, 5)
        prev = v
        for (off, d, direction) in pats[pattern]:
            if off >= c.dur - 1e-6:
                continue
            strings = v if direction > 0 else v[::-1]
            acc_v = vel + (8 if off == 0 else 0) - (10 if direction < 0 else 0)
            for i, p in enumerate(strings):
                S.note(name, c.start + off + i * 0.012, d * 0.95, p, acc_v + S.rng.randint(-5, 3))


@acc
def comp(S, chords, t0, nbars, inst='rhodes', lo=55, hi=74, vel=58, pattern='funk', vol=88, pan=40, rev=40, name=None):
    """Syncopated chord comping (Rhodes / clav / jazz guitar)."""
    name = S.part(name or f'comp_{inst}', GM[inst], vol=vol, pan=pan, rev=rev, cho=30)
    pats = {'funk': [(0, .4), (0.75, .2), (1.5, .4), (2.5, .2), (2.75, .5)],
            'charleston': [(0, .9), (1.5, .4)],
            'offbeat': [(0.5, .35), (1.5, .35), (2.5, .35), (3.5, .35)],
            'bossa': [(0, .5), (1.5, .5), (3, .5)],
            'stabs': [(0, .25), (1.5, .25)],
            'long': [(0, 1.8), (2.5, 1.3)],
            'waltz': [(1, .6), (2, .6)]}
    prev = None
    for c in _chords_in(chords, t0, nbars, S.bar):
        v = voice(c, prev, lo, hi, 4)
        prev = v
        for off, d in pats[pattern]:
            if off >= c.dur - 1e-6:
                continue
            for p in v:
                S.note(name, c.start + off, d, p, vel + S.rng.randint(-6, 6))


@acc
def skank(S, chords, t0, nbars, inst='muted_gtr', lo=57, hi=72, vel=62, vol=80, pan=90, rev=25, name=None, density=0.7):
    """Funky muted-guitar 16ths with accents on the 'e' and 'a'."""
    name = S.part(name or f'skank_{inst}', GM[inst], vol=vol, pan=pan, rev=rev)
    prev = None
    for c in _chords_in(chords, t0, nbars, S.bar):
        v = voice(c, prev, lo, hi, 3)
        prev = v
        n = int(round(c.dur / 0.25))
        for k in range(n):
            accent = k % 4 in (1, 3)
            if not accent and S.rng.random() > density * 0.5:
                continue
            for p in v:
                S.note(name, c.start + k * 0.25, 0.12, p, (vel + 10 if accent else vel - 14) + S.rng.randint(-5, 5))


@acc
def pizz(S, chords, t0, nbars, lo=48, hi=67, vel=70, pattern='walk', vol=92, pan=74, rev=55, name=None):
    """Pizzicato strings: bouncing chord tones."""
    name = S.part(name or 'pizz', GM['pizz'], vol=vol, pan=pan, rev=rev)
    for c in _chords_in(chords, t0, nbars, S.bar):
        tones = c.tones_in(lo, hi)
        n = int(round(c.dur / (0.5 if pattern == 'eighths' else 1)))
        step = 0.5 if pattern == 'eighths' else 1
        seq = [tones[0], tones[min(2, len(tones) - 1)], tones[min(1, len(tones) - 1)], tones[min(3, len(tones) - 1)]]
        for k in range(n):
            S.note(name, c.start + k * step, 0.4, seq[k % 4], vel + (10 if k == 0 else 0) + S.rng.randint(-6, 4))


@acc
def ostinato(S, chords, t0, nbars, inst='strings', lo=57, hi=76, vel=66, pattern='16ths', vol=92, pan=64, rev=45, name=None):
    """Driving battle ostinato: repeated 16th/8th chord tones with accents (strings / marimba / pizz)."""
    name = S.part(name or f'ost_{inst}', GM[inst], vol=vol, pan=pan, rev=rev)
    step = 0.25 if pattern == '16ths' else 0.5
    acc_pat = [1, 0, 0, 1, 0, 0, 1, 0] if pattern == '16ths' else [1, 0, 1, 1]
    for c in _chords_in(chords, t0, nbars, S.bar):
        tones = c.tones_in(lo, hi)
        if len(tones) < 3:
            tones = tones * 3
        cell = [tones[0], tones[1], tones[2], tones[1]] if pattern == '16ths' else [tones[0], tones[2], tones[1], tones[2]]
        n = int(round(c.dur / step))
        for k in range(n):
            a = acc_pat[k % len(acc_pat)]
            S.note(name, c.start + k * step, step * 0.8, cell[k % 4], vel + (14 if a else 0) + S.rng.randint(-4, 4))


@acc
def stabs(S, chords, t0, nbars, inst='brass', lo=53, hi=72, vel=80, rhythm=((0, .5), (1.5, .5), (3, .5)), vol=86, pan=58, rev=45, name=None):
    name = S.part(name or f'stab_{inst}', GM[inst], vol=vol, pan=pan, rev=rev)
    prev = None
    for c in _chords_in(chords, t0, nbars, S.bar):
        v = voice(c, prev, lo, hi, 4)
        prev = v
        for off, d in rhythm:
            if off >= c.dur - 1e-6:
                continue
            for p in v:
                S.note(name, c.start + off, d, p, vel + S.rng.randint(-5, 5))


@acc
def bass(S, chords, t0, nbars, inst='ac_bass', style='root5', lo=33, vel=86, vol=100, pan=64, rev=20, name=None):
    """Bass lines: whole, root5, walking, funk, drive (8ths), waltz, bossa, pedal."""
    name = S.part(name or f'bass_{inst}', GM[inst], vol=vol, pan=pan, rev=rev, cho=0)
    cs = _chords_in(chords, t0, nbars, S.bar)
    scale = [(key_pc(S.key) + x) % 12 for x in MODES[S.mode]]
    for i, c in enumerate(cs):
        root = [x for x in range(lo, lo + 12) if x % 12 == c.bass][0]
        fifth = root + 7
        nxt = cs[i + 1] if i + 1 < len(cs) else chords[0]
        nroot = [x for x in range(lo, lo + 12) if x % 12 == nxt.bass][0]
        d = c.dur
        r = S.rng
        if style == 'whole':
            S.note(name, c.start, d * 0.95, root, vel)
        elif style == 'root5':
            S.note(name, c.start, min(d, 2) * 0.9, root, vel)
            if d >= 4:
                S.note(name, c.start + 2, 1.8, fifth if fifth - lo < 19 else fifth - 12, vel - 8)
            elif d >= 2 and r.random() < 0.5:
                S.note(name, c.start + 1.5, 0.45, root, vel - 14)
        elif style == 'waltz':
            S.note(name, c.start, 1.9, root, vel)
            if d >= 3:
                S.note(name, c.start + 2, 0.9, fifth - 12 if fifth - lo > 12 else fifth, vel - 12)
        elif style == 'walking':
            beats = int(round(d))
            line = [root]
            tones = c.tones_in(root, root + 12)
            for k in range(1, beats):
                if k == beats - 1:   # approach the next root by a step
                    line.append(nroot - 1 if r.random() < 0.5 else nroot + (2 if (nroot + 2) % 12 in scale else 1))
                else:
                    step = line[-1] + 2
                    while step % 12 not in scale:
                        step += 1
                    line.append(tones[min(k, len(tones) - 1)] if r.random() < 0.7 else step)
            for k, p in enumerate(line):
                while p > lo + 20:
                    p -= 12
                S.note(name, c.start + k, 0.92, p, vel - (0 if k == 0 else 10) + r.randint(-4, 4))
        elif style == 'funk':
            pat = [(0, .4, root, 0), (0.75, .2, root + 12, -8), (1.5, .3, root, -6), (2, .2, root, -20),
                   (2.5, .3, fifth, -8), (3, .2, root + 10 if (root + 10) % 12 in c.pcs else root + 12, -10), (3.5, .45, nroot - 1 if (nroot - 1) % 12 in scale else root, -4)]
            for off, dd, p, dv in pat:
                if off < d - 1e-6:
                    S.note(name, c.start + off, dd, p, vel + dv + r.randint(-4, 4))
        elif style == 'drive':
            n = int(round(d / 0.5))
            for k in range(n):
                p = root if k % 8 not in (6,) else (fifth if fifth - lo < 19 else root + 12)
                S.note(name, c.start + k * 0.5, 0.42, p, vel + (8 if k % 2 == 0 else -6) + r.randint(-3, 3))
        elif style == 'bossa':
            for off, dd, p in [(0, 1.4, root), (1.5, .5, fifth), (2, 1.4, fifth), (3.5, .5, root)]:
                if off < d - 1e-6:
                    S.note(name, c.start + off, dd, p if p - lo < 19 else p - 12, vel - (0 if off == 0 else 10))
        elif style == 'pedal':
            S.note(name, c.start, d * 0.97, [x for x in range(lo, lo + 12) if x % 12 == key_pc(S.key)][0], vel)
        elif style == 'battle':
            pat = [(0, .45, root), (.5, .2, root), (.75, .2, root), (1, .45, root + 12), (1.5, .45, root),
                   (2, .45, root), (2.5, .2, fifth), (2.75, .2, root), (3, .45, root + 12), (3.5, .45, fifth)]
            for off, dd, p in pat:
                if off < d - 1e-6:
                    S.note(name, c.start + off, dd, p, vel + (6 if off in (0, 2) else -6) + r.randint(-3, 3))


@acc
def counter(S, chords, t0, nbars, inst='flute', lo=67, hi=84, vel=64, rhythm='long', vol=80, pan=80, rev=65, name=None):
    """A gentle counter-line of chord tones moving by the smallest step (long notes or answering phrases)."""
    name = S.part(name or f'counter_{inst}', GM[inst], vol=vol, pan=pan, rev=rev)
    prev = None
    for c in _chords_in(chords, t0, nbars, S.bar):
        tones = [x for x in c.tones_in(lo, hi) if (x - c.root) % 12 != 0] or c.tones_in(lo, hi)
        p = min(tones, key=lambda x: abs(x - prev) if prev else abs(x - (lo + hi) // 2))
        if prev and p == prev and len(tones) > 1:
            p = sorted(tones, key=lambda x: abs(x - prev))[1]
        prev = p
        if rhythm == 'long':
            S.note(name, c.start, c.dur * 0.96, p, vel + S.rng.randint(-4, 4))
        else:   # answer: a little figure in the second half of each chord
            if c.dur >= 2:
                q = min([x for x in c.tones_in(lo, hi) if x != p] or [p], key=lambda x: abs(x - p))
                S.note(name, c.start + c.dur - 1.5, 0.5, q, vel - 6)
                S.note(name, c.start + c.dur - 1, 1, p, vel)


@acc
def bells(S, chords, t0, nbars, inst='celesta', lo=72, hi=91, vel=52, every=2, vol=70, pan=90, rev=80, name=None):
    """Sparse sparkles: a high chord tone every couple of beats."""
    name = S.part(name or f'bells_{inst}', GM[inst], vol=vol, pan=pan, rev=rev)
    for c in _chords_in(chords, t0, nbars, S.bar):
        tones = c.tones_in(lo, hi)
        k = 0
        while k < c.dur - 1e-6:
            t = c.start + k + (0.5 if S.rng.random() < 0.3 else 0)
            S.note(name, t, min(1.5, c.start + c.dur - t + 0.05), S.rng.choice(tones), vel + S.rng.randint(-8, 6))
            k += every


@acc
def timp(S, chords, t0, nbars, vel=80, pattern='downbeat', vol=90, rev=60, name=None):
    name = S.part(name or 'timpani', GM['timpani'], vol=vol, rev=rev)
    for i, c in enumerate(_chords_in(chords, t0, nbars, S.bar)):
        root = [x for x in range(41, 53) if x % 12 == c.bass][0]
        if pattern == 'downbeat':
            S.note(name, c.start, 1.5, root, vel)
        elif pattern == 'roll':
            n = int(c.dur / 0.125)
            for k in range(n):
                S.note(name, c.start + k * 0.125, 0.12, root, int(vel * (0.45 + 0.55 * k / n)))
        elif pattern == 'battle':
            for off, dv in [(0, 0), (1.5, -12), (2, -4), (3.5, -10)]:
                if off < c.dur:
                    S.note(name, c.start + off, 0.6, root if off != 3.5 else root + 7 if root + 7 <= 53 else root - 5, vel + dv)


# ── drums ──────────────────────────────────────────────────────────────────
DRUMS = {}


def drum(fn):
    DRUMS[fn.__name__] = fn
    return fn


def _kit(S, kit, vol=92, rev=35):
    return S.part(f'drums_{kit}', KITS[kit], vol=vol, rev=rev, drums=True)


def _hit(S, name, t, n, v):
    S.note(name, t, 0.2, n, v + S.rng.randint(-6, 5))


@drum
def brush(S, t0, nbars, vel=62, fill=True, kit='brush'):
    """Relaxed brushes: swirl on every beat, tap on 2 & 4, soft kick on 1 (and the 'and' of 3 sometimes)."""
    k = _kit(S, kit, vol=86, rev=40)
    bb = S.bar
    for b in range(nbars):
        t = t0 + b * bb
        for beat in range(bb):
            _hit(S, k, t + beat, 40 if kit == 'brush' else 44, vel - 18)            # swirl
            if beat in (1, 3) or (bb == 3 and beat in (1, 2)):
                _hit(S, k, t + beat, 38, vel - 4)
            _hit(S, k, t + beat + 0.5, 42 if kit != 'brush' else 38, vel - 26)
        _hit(S, k, t, 36, vel)
        if bb == 4 and S.rng.random() < 0.5:
            _hit(S, k, t + 2.5, 36, vel - 16)
        if fill and b % 4 == 3:
            _hit(S, k, t + bb - 0.5, 38, vel)
            _hit(S, k, t + bb - 0.25, 38, vel - 8)


@drum
def softkit(S, t0, nbars, vel=66, fill=True, ride=False, kit='room', rim=True):
    """Soft pop groove: kick 1 & 3, rim click 2 & 4, gentle 8th hats."""
    k = _kit(S, kit, vol=84, rev=30)
    for b in range(nbars):
        t = t0 + b * 4
        _hit(S, k, t, 36, vel + 4)
        _hit(S, k, t + 2, 36, vel - 4)
        if S.rng.random() < 0.4:
            _hit(S, k, t + 2.5, 36, vel - 18)
        for beat in (1, 3):
            _hit(S, k, t + beat, 37 if rim else 38, vel - 2)
        for e in range(8):
            _hit(S, k, t + e * 0.5, 51 if ride else 42, vel - (14 if e % 2 else 6))
        if fill and b % 4 == 3:
            for i, n in enumerate((45, 45, 41, 41)):
                _hit(S, k, t + 3 + i * 0.25, n, vel - 4 + i * 3)
        if b % 8 == 0:
            _hit(S, k, t, 49 if not ride else 51, vel - 10)


@drum
def funk(S, t0, nbars, vel=72, kit='standard', open_hat=True):
    """Funk groove: 16th hats with accents, syncopated kick, backbeat snare with ghost notes."""
    k = _kit(S, kit, vol=90, rev=22)
    kicks = [[0, 0.75, 2.5], [0, 1.75, 2.5, 3.25], [0, 0.75, 2, 2.75], [0, 1.5, 2.5, 3.75]]
    for b in range(nbars):
        t = t0 + b * 4
        for s16 in range(16):
            p = s16 * 0.25
            hv = vel - 24 + (10 if s16 % 4 == 0 else (4 if s16 % 2 == 0 else -8))
            if open_hat and s16 == 14 and b % 2 == 1:
                _hit(S, k, t + p, 46, hv)
            else:
                _hit(S, k, t + p, 42, hv)
        for p in kicks[b % 4]:
            _hit(S, k, t + p, 36, vel + 2)
        for p in (1, 3):
            _hit(S, k, t + p, 38, vel + 4)
        for p in (1.75, 2.25, 3.5) if b % 2 else (0.5, 1.75, 3.75):
            _hit(S, k, t + p, 38, vel - 36)      # ghost notes
        if b % 8 == 7:
            for i, n in enumerate((38, 38, 45, 41)):
                _hit(S, k, t + 3 + i * 0.25, n, vel - 2)
        if b % 8 == 0:
            _hit(S, k, t, 49, vel - 6)


@drum
def bossa(S, t0, nbars, vel=62, kit='jazz'):
    k = _kit(S, kit, vol=82, rev=35)
    clave = [0, 1.5, 3, 5, 6.5]      # 2-bar clave (rim)
    for b in range(nbars):
        t = t0 + b * 4
        for e in range(8):
            _hit(S, k, t + e * 0.5, 42, vel - (8 if e % 2 == 0 else 18))
        for p in (0, 1.5, 2, 3.5):
            _hit(S, k, t + p, 36, vel - (0 if p in (0, 2) else 12))
        for p in clave:
            if b % 2 == int(p // 4):
                _hit(S, k, t + p % 4, 37, vel - 2)


@drum
def march(S, t0, nbars, vel=66, kit='orchestra'):
    """Light snare march for the Trial halls."""
    k = _kit(S, kit, vol=84, rev=45)
    for b in range(nbars):
        t = t0 + b * 4
        _hit(S, k, t, 36, vel + 4)
        _hit(S, k, t + 2, 36, vel - 6)
        for p, dv in [(0, 0), (1, -8), (1.5, -18), (1.75, -18), (2, -4), (3, -8), (3.5, -16)]:
            _hit(S, k, t + p, 38, vel + dv)
        if b % 4 == 3:
            for i in range(8):
                _hit(S, k, t + 2 + i * 0.25, 38, vel - 20 + i * 3)


@drum
def battle(S, t0, nbars, vel=80, kit='standard', toms=True):
    """Driving battle groove: kick on the 8th-note pulse pattern, snare 2 & 4, ride/hats, fills, crashes."""
    k = _kit(S, kit, vol=92, rev=28)
    for b in range(nbars):
        t = t0 + b * 4
        for p in ([0, 0.75, 1.5, 2, 2.75] if b % 2 == 0 else [0, 0.5, 1.5, 2, 3, 3.5]):
            _hit(S, k, t + p, 36, vel)
        for p in (1, 3):
            _hit(S, k, t + p, 38, vel + 6)
        for e in range(8):
            _hit(S, k, t + e * 0.5, 42, vel - (8 if e % 2 == 0 else 22))
        if b % 8 == 0:
            _hit(S, k, t, 49, vel)
        if toms and b % 4 == 3:
            for i, n in enumerate((50, 48, 47, 45, 43, 41, 38, 38)):
                _hit(S, k, t + 2 + i * 0.25, n, vel - 6 + i)


@drum
def taiko(S, t0, nbars, vel=84, busy=False):
    """Orchestral taiko pattern (tuned drum program) with a big hit every other bar."""
    name = S.part('taiko', GM['taiko'], vol=96, rev=55)
    for b in range(nbars):
        t = t0 + b * 4
        pat = [(0, 0), (1.5, -14), (2, -6), (3, -10), (3.5, -16)] if busy else [(0, 0), (2.5, -14), (3, -8)]
        for p, dv in pat:
            S.note(name, t + p, 0.5, 38 if p else 36, vel + dv + S.rng.randint(-5, 4))


@drum
def hand(S, t0, nbars, vel=58, kit='standard'):
    """Hand percussion for the woods: shaker 8ths, conga tumbao, woodblock."""
    k = _kit(S, kit, vol=80, rev=45)
    bb = S.bar
    for b in range(nbars):
        t = t0 + b * bb
        for e in range(bb * 2):
            _hit(S, k, t + e * 0.5, 70, vel - (6 if e % 2 else 16))
        for p, n, dv in ([(0, 64, 0), (1.5, 63, -8), (2, 62, -12), (3, 63, -6), (3.5, 63, -10)] if bb == 4 else [(0, 64, 0), (1, 62, -10), (2, 63, -8)]):
            _hit(S, k, t + p, n, vel + dv)
        if b % 2 == 1:
            _hit(S, k, t + bb - 1, 76, vel - 8)


@drum
def waltz(S, t0, nbars, vel=56, kit='brush'):
    k = _kit(S, kit, vol=80, rev=45)
    for b in range(nbars):
        t = t0 + b * 3
        _hit(S, k, t, 36, vel)
        _hit(S, k, t + 1, 38 if kit == 'brush' else 42, vel - 14)
        _hit(S, k, t + 2, 38 if kit == 'brush' else 42, vel - 14)
        if kit == 'brush':
            for beat in range(3):
                _hit(S, k, t + beat, 40, vel - 20)


@drum
def shaker(S, t0, nbars, vel=50, kit='standard'):
    k = _kit(S, kit, vol=74, rev=40)
    for b in range(nbars):
        t = t0 + b * S.bar
        for e in range(S.bar * 2):
            _hit(S, k, t + e * 0.5, 69, vel - (0 if e % 2 else 12))
        if b % 2 == 0:
            _hit(S, k, t, 81, vel - 14)


# ── MIDI output ────────────────────────────────────────────────────────────
def to_midi(S, path, repeats=2, tail_beats=16, humanize_ms=7):
    """Write the song `repeats` times back to back (render.py keeps the second pass so the loop joins seamlessly)."""
    mid = mido.MidiFile(ticks_per_beat=TPB, type=1)
    meta = mido.MidiTrack()
    mid.tracks.append(meta)
    meta.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(S.tempo), time=0))
    meta.append(mido.MetaMessage('time_signature', numerator=S.bar, denominator=4, time=0))
    chans = {}
    free = [c for c in range(16) if c != 9]
    for name, p in S.parts.items():
        chans[name] = 9 if p['drums'] else free.pop(0)
    beat_ms = 60000.0 / S.tempo
    for name, p in S.parts.items():
        ch = chans[name]
        tr = mido.MidiTrack()
        mid.tracks.append(tr)
        tr.append(mido.MetaMessage('track_name', name=name, time=0))
        msgs = [(0, 0, mido.Message('program_change', program=p['program'], channel=ch))]
        for cc, val in ((7, p['vol']), (10, p['pan']), (91, p['rev']), (93, p['cho'])):
            msgs.append((0, 0, mido.Message('control_change', control=cc, value=int(val), channel=ch)))
        for rep in range(repeats):
            rng = random.Random(zlib.crc32(name.encode()))   # identical humanising on every pass
            off = rep * S.length
            for (s, d, part, pitch, vel) in S.events:
                if part != name:
                    continue
                on = S.swing_t(s) + off
                offt = S.swing_t(s + d) + off
                jitter = rng.gauss(0, humanize_ms) / beat_ms if not p['drums'] else rng.gauss(0, humanize_ms * 0.6) / beat_ms
                on_t = max(0, int(round((on + jitter) * TPB)))
                off_t = max(on_t + 10, int(round((offt + jitter) * TPB)))
                msgs.append((on_t, 1, mido.Message('note_on', note=pitch, velocity=vel, channel=ch)))
                msgs.append((off_t, 0, mido.Message('note_off', note=pitch, velocity=0, channel=ch)))
        end = int(round((repeats * S.length + tail_beats) * TPB))
        # a note that starts again while still sounding is cut just before the new one (otherwise its note-off
        # would arrive late and silence the new note)
        # pair each note-on with its note-off in order and clip overlaps
        stacks = {}
        pairs = []
        for t, f, m in sorted(msgs, key=lambda x: (x[0], x[1])):
            if m.type == 'note_on':
                pairs.append([t, None, m])
                stacks.setdefault(m.note, []).append(pairs[-1])
            elif m.type == 'note_off':
                st = stacks.get(m.note)
                if st:
                    st.pop(0)[1] = t
        msgs = [(t, 0, m) for t, f, m in msgs if m.type not in ('note_on', 'note_off')]
        by_pitch = {}
        for pr in pairs:
            by_pitch.setdefault(pr[2].note, []).append(pr)
        for n, prs in by_pitch.items():
            prs.sort(key=lambda x: x[0])
            for a, b in zip(prs, prs[1:]):
                if a[1] is None or a[1] > b[0]:
                    a[1] = max(a[0] + 5, b[0] - 1)
            for on_t, off_t, m in prs:
                msgs.append((on_t, 1, m))
                msgs.append((off_t if off_t is not None else on_t + TPB, 0, mido.Message('note_off', note=n, velocity=0, channel=m.channel)))
        msgs.sort(key=lambda m: (m[0], m[1]))
        last = 0
        for t, _, m in msgs:
            tr.append(m.copy(time=t - last))
            last = t
        tr.append(mido.MetaMessage('end_of_track', time=max(0, end - last)))
    mid.save(path)
    return S.length * 60.0 / S.tempo


def clash_report(S, min_dur=0.75):
    """Pairs of held notes (≥ min_dur beats, different parts, not drums) sounding a semitone or minor 9th apart
    for at least half a beat. Returns a list of strings."""
    evs = [e for e in S.events if not S.parts[e[2]]['drums'] and e[1] >= min_dur and S.parts[e[2]]['program'] not in (GM['timpani'], GM['taiko'])]
    evs.sort()
    out = []
    for i, (s1, d1, p1, n1, _) in enumerate(evs):
        for s2, d2, p2, n2, _ in evs[i + 1:]:
            if s2 >= s1 + d1:
                break
            if p1 == p2:
                continue
            overlap = min(s1 + d1, s2 + d2) - max(s1, s2)
            iv = abs(n1 - n2)
            if overlap >= 0.5 and iv in (1, 13):
                out.append(f'bar {int(max(s1, s2) // S.bar) + 1} beat {max(s1, s2) % S.bar + 1:g}: {p1} {n1} vs {p2} {n2}')
    return out
