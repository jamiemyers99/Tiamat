"""Tiamat's soundtrack. Renders every new track and jingle to public/assets/audio.

    python tools/audio/songs.py            # all
    python tools/audio/songs.py title cave  # just these
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from synth import Song, write_ogg, SR
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
BGM = os.path.join(ROOT, 'public', 'assets', 'audio', 'bgm')
SFX = os.path.join(ROOT, 'public', 'assets', 'audio', 'sfx')
SONGS = {}
JINGLES = {}


def song(fn):
    SONGS[fn.__name__] = fn
    return fn


def jingle(fn):
    JINGLES['jingle_' + fn.__name__] = fn
    return fn


# ═══ World ════════════════════════════════════════════════════════════════
@song
def title():
    s = Song(112, 16)
    A = "Dm Bb F C Dm Bb C A"
    B = "Bb C Dm Dm Gm Bb A A"
    s.melody('lead', """
      D5/3 A4/1 D5/2 E5/2 | F5/4 E5/2 D5/2 | C5/3 A4/1 C5/2 F5/2 | E5/6 r/2 |
      D5/3 A4/1 D5/2 E5/2 | F5/2 G5/2 A5/2 F5/2 | G5/3 E5/1 C5/2 E5/2 | C#5/4 E5/2 A5/2 |
      Bb5/4 A5/2 G5/2 | A5/4 G5/2 E5/2 | F5/3 E5/1 D5/2 A5/2 | D6/6 r/2 |
      Bb5/3 A5/1 G5/2 D5/2 | F5/3 E5/1 D5/2 F5/2 | E5/4 C#5/2 E5/2 | A5/6 r/2""")
    s.melody('strings', """
      D4/8 | D4/8 | C4/8 | C4/8 | D4/8 | D4/8 | E4/8 | E4/8 |
      F4/8 | G4/8 | A4/8 | A4/8 | G4/8 | F4/8 | E4/8 | C#4/8""")
    s.bassline(A, 'r.r.o.r.'); s.bassline(B, 'r.r.o.r.', start_bar=8)
    s.arpeggio(A, '0120', rate=0.5, octave=4, amp=0.8); s.arpeggio(B, '0121', rate=0.5, octave=4, start_bar=8, amp=0.8)
    s.drums('k...s...k.k.s...', 15); s.drums('k...s...k.k.s.ss', 1, start_bar=15)
    return s.mix(echo=(0.27, 0.35, 0.18), target_rms=0.2)


@song
def brindlewood():
    s = Song(138, 24, beats_per_bar=3)
    A = "G C G D G C D G"
    B = "Em C G D Em C D D"
    mel = """
      B4/2 D5/2 G5/2 | E5/3 D5/1 C5/2 | B4/2 G4/2 B4/2 | A4/4 r/2 |
      B4/2 D5/2 G5/2 | A5/3 G5/1 E5/2 | D5/2 F#5/2 A5/2 | G5/4 r/2 |"""
    s.melody('flute', mel)
    s.melody('flute', mel.replace('A4/4 r/2', 'A4/2 B4/2 C5/2'), start_bar=8)
    s.melody('flute', """
      G5/2 F#5/2 E5/2 | E5/3 D5/1 C5/2 | D5/2 B4/2 G4/2 | A4/4 D5/2 |
      G5/2 A5/2 B5/2 | C6/3 B5/1 A5/2 | F#5/2 E5/2 D5/2 | D5/4 r/2""", start_bar=16)
    for i, prog in enumerate([A, A, B]):
        s.bassline(prog, 'r.....', start_bar=i * 8)
        s.stabs(prog, '..x.x.', instr='harm', start_bar=i * 8, octave=4, amp=0.8)
    s.drums('k...h...h...', 24, amp=0.6)
    return s.mix(echo=(0.22, 0.3, 0.15), target_rms=0.19)


@song
def saltreach():
    s = Song(276, 16, beats_per_bar=6, step=1)
    A = "Dm C Dm A Dm C A Dm"
    B = "F C Dm A F C A Dm"
    s.melody('organ', """
      A4/2 D5/1 D5/2 E5/1 | F5/2 E5/1 D5/2 C5/1 | A4/2 D5/1 F5/2 A5/1 | G5/3 E5/3 |
      A4/2 D5/1 D5/2 E5/1 | F5/2 G5/1 A5/2 G5/1 | E5/3 C#5/3 | D5/6 |
      C5/2 F5/1 F5/2 G5/1 | A5/2 G5/1 E5/2 C5/1 | D5/2 F5/1 A5/2 D6/1 | C#6/3 A5/3 |
      C6/2 A5/1 F5/2 A5/1 | G5/2 E5/1 C5/2 E5/1 | E5/3 C#5/3 | D5/6""")
    s.bassline(A, 'r-----f-----'); s.bassline(B, 'r-----f-----', start_bar=8)
    s.stabs(A, '...x.....x..', instr='harm', amp=0.9); s.stabs(B, '...x.....x..', instr='harm', start_bar=8, amp=0.9)
    s.drums('k.......h.......s.......', 16, amp=0.8)
    return s.mix(echo=(0.33, 0.25, 0.12), target_rms=0.2)


@song
def gearhollow():
    s = Song(126, 16)
    A = "Em Em C D Em Em Am B7"
    B = "C D Em Em C D B7 B7"
    s.melody('lead12', """
      E5/1 r/1 E5/1 G5/1 r/1 B5/2 A5/1 | G5/2 F#5/1 E5/1 r/2 B4/2 | C5/1 r/1 E5/1 G5/1 r/1 C6/2 B5/1 | A5/3 F#5/1 D5/4 |
      E5/1 r/1 E5/1 G5/1 r/1 B5/2 A5/1 | G5/2 A5/1 B5/1 r/2 E6/2 | C6/2 B5/1 A5/1 E5/2 C5/2 | D#5/4 F#5/2 B5/2 |
      G5/2 E5/2 C5/2 E5/2 | F#5/2 D5/2 A4/2 D5/2 | E5/1 F#5/1 G5/1 A5/1 B5/2 E6/2 | D6/2 B5/2 G5/2 E5/2 |
      E6/3 D6/1 C6/2 G5/2 | F#5/3 G5/1 A5/2 D6/2 | B5/2 A5/2 F#5/2 D#5/2 | B4/6 r/2""")
    s.bassline(A, 'r.rr.r.o'); s.bassline(B, 'r.rr.r.o', start_bar=8)
    s.stabs(A, '.x..x.x.', amp=0.8); s.stabs(B, '.x..x.x.', start_bar=8, amp=0.8)
    s.drums('k..hk.s.k.k.s.hh', 16, amp=0.9)
    return s.mix(echo=(0.24, 0.25, 0.12), target_rms=0.2)


@song
def hollowmere():
    s = Song(76, 12)
    P = "Am F C G Am F E E Dm Am F E"
    s.melody('soft', """
      E5/4 A4/2 B4/2 | C5/4 A4/4 | G4/2 C5/2 E5/2 G5/2 | D5/8 |
      E5/4 A5/2 G5/2 | F5/4 E5/2 C5/2 | B4/4 G#4/2 B4/2 | E5/8 |
      F5/4 E5/2 D5/2 | C5/4 A4/4 | A4/2 C5/2 F5/2 A5/2 | G#5/8""")
    s.pad(P, octave=3, amp=1.2)
    s.bassline(P, 'r-------', octave=2, amp=0.8)
    s.arpeggio(P, '0121', instr='bell', rate=1.0, octave=5, amp=0.35)
    return s.mix(echo=(0.47, 0.45, 0.35), target_rms=0.17)


@song
def frostspire():
    s = Song(100, 16)
    A = "E B C#m A E B A B"
    B = "C#m A E B C#m A B B"
    s.melody('bell', """
      G#5/2 B5/2 E6/2 D#6/2 | D#6/3 C#6/1 B5/4 | E5/2 G#5/2 C#6/2 B5/2 | A5/6 r/2 |
      G#5/2 B5/2 E6/2 F#6/2 | D#6/3 E6/1 F#6/4 | E6/2 C#6/2 A5/2 C#6/2 | B5/6 r/2 |
      C#6/3 B5/1 G#5/4 | A5/3 B5/1 C#6/4 | B5/2 G#5/2 E5/2 G#5/2 | F#5/6 r/2 |
      E6/3 D#6/1 C#6/2 G#5/2 | A5/2 B5/2 C#6/2 E6/2 | D#6/4 F#6/4 | D#6/6 r/2""", amp=1.2)
    s.melody('flute', """
      r/8 | r/8 | r/8 | r/8 | r/8 | r/8 | r/8 | r/8 |
      C#5/8 | C#5/8 | B4/8 | A#4/8 | C#5/8 | C#5/8 | D#5/8 | D#5/8""", amp=0.6)
    s.pad(A, instr='strings', octave=3, amp=0.9); s.pad(B, instr='strings', octave=3, start_bar=8, amp=0.9)
    s.bassline(A, 'r...f...'); s.bassline(B, 'r...f...', start_bar=8)
    s.drums('k.....h.k.s...h.', 16, amp=0.55)
    return s.mix(echo=(0.3, 0.4, 0.3), target_rms=0.18)


@song
def riftgate():
    s = Song(96, 16)
    A = "Cm Ab Bb G Cm Ab Fm G"
    B = "Ab Bb Cm Cm Ab Bb G G"
    s.melody('strings', """
      C5/3 D5/1 Eb5/4 | Eb5/2 D5/2 C5/4 | D5/3 Eb5/1 F5/4 | D5/6 r/2 |
      G5/3 F5/1 Eb5/4 | Ab5/2 G5/2 F5/2 Eb5/2 | F5/3 Eb5/1 D5/2 C5/2 | B4/6 r/2 |
      C6/4 Bb5/2 Ab5/2 | Bb5/4 Ab5/2 G5/2 | G5/2 Eb5/2 C5/2 Eb5/2 | G5/6 r/2 |
      Ab5/3 G5/1 F5/2 Eb5/2 | D5/3 Eb5/1 F5/2 D5/2 | B4/4 D5/4 | G5/6 r/2""", amp=1.6)
    s.melody('lead50', """
      r/8 | r/8 | r/8 | r/8 | G5/3 F5/1 Eb5/4 | Ab5/2 G5/2 F5/2 Eb5/2 | F5/3 Eb5/1 D5/2 C5/2 | B4/6 r/2 |
      C6/4 Bb5/2 Ab5/2 | Bb5/4 Ab5/2 G5/2 | G5/2 Eb5/2 C5/2 Eb5/2 | G5/6 r/2 |
      Ab5/3 G5/1 F5/2 Eb5/2 | D5/3 Eb5/1 F5/2 D5/2 | B4/4 D5/4 | G5/6 r/2""", amp=0.7)
    s.bassline(A, 'r.r.r.rf'); s.bassline(B, 'r.r.r.rf', start_bar=8)
    s.drums('t...s...t.t.s...', 16, amp=0.8)
    return s.mix(echo=(0.31, 0.3, 0.2), target_rms=0.2)


@song
def forest():
    s = Song(92, 16)
    A = "Em D Em D C D Em Em"
    B = "Am Em Am B7 C D B7 B7"
    s.melody('flute', """
      B4/2 E5/2 G5/3 F#5/1 | F#5/2 E5/2 D5/4 | B4/2 E5/2 G5/2 B5/2 | A5/6 r/2 |
      G5/3 F#5/1 E5/2 C5/2 | D5/3 E5/1 F#5/4 | E5/8 | r/8 |
      A5/3 G5/1 E5/4 | G5/2 F#5/2 E5/4 | C6/3 B5/1 A5/2 E5/2 | F#5/6 r/2 |
      E5/2 G5/2 C6/2 B5/2 | A5/2 F#5/2 D5/2 F#5/2 | D#5/4 F#5/4 | B4/6 r/2""")
    s.bassline(A, 'r...r...'); s.bassline(B, 'r...r...', start_bar=8)
    s.arpeggio(A, '0121', instr='arp', rate=0.5, octave=4, amp=0.7); s.arpeggio(B, '0121', instr='arp', rate=0.5, octave=4, start_bar=8, amp=0.7)
    s.drums('..h...h...h...h.', 16, amp=0.6)
    return s.mix(echo=(0.49, 0.4, 0.3), target_rms=0.18)


@song
def cave():
    s = Song(70, 8)
    P = "Dm Bb Gm A Dm Bb Gm A"
    s.melody('bell', """
      r/4 A4/2 D5/2 | F5/6 r/2 | r/4 G4/2 Bb4/2 | C#5/6 r/2 |
      r/2 D5/2 F5/2 A5/2 | G5/6 F5/2 | E5/4 D5/4 | C#5/8""", amp=1.1)
    s.pad(P, octave=3, amp=1.3)
    s.bassline(P, 'r...r...', octave=2, amp=0.9)
    s.drums('t...............', 8, amp=0.7)
    return s.mix(echo=(0.64, 0.5, 0.4), target_rms=0.16)


@song
def moor():
    s = Song(108, 16)
    A = "G F C G G F C D"
    B = "Em C G D Em C D D"
    s.melody('lead50', """
      D5/2 G5/2 A5/2 B5/2 | C6/3 A5/1 F5/4 | E5/2 G5/2 C6/2 E5/2 | D5/6 r/2 |
      B4/2 D5/2 G5/2 A5/2 | A5/3 G5/1 F5/2 C5/2 | E5/3 D5/1 C5/2 E5/2 | D5/6 r/2 |
      E5/2 G5/2 B5/3 A5/1 | G5/2 E5/2 C5/4 | D5/2 G5/2 B5/2 D6/2 | C6/3 B5/1 A5/4 |
      B5/3 A5/1 G5/2 E5/2 | E5/3 F#5/1 G5/4 | A5/3 G5/1 F#5/2 A5/2 | D6/6 r/2""")
    s.bassline(A, 'r.f.r.f.'); s.bassline(B, 'r.f.r.f.', start_bar=8)
    s.stabs(A, 'x...x...', instr='soft', amp=0.9); s.stabs(B, 'x...x...', instr='soft', start_bar=8, amp=0.9)
    s.drums('k...s.h.k.k.s...', 16, amp=0.75)
    return s.mix(echo=(0.28, 0.3, 0.18), target_rms=0.19)


@song
def lake():
    s = Song(96, 16)
    A = "F C Dm Bb F C Bb C"
    B = "Dm Am Bb F Gm C F F"
    s.melody('flute', """
      A5/4 C6/4 | G5/4 E5/4 | F5/3 E5/1 D5/4 | D5/8 |
      A5/3 Bb5/1 C6/4 | G5/3 A5/1 Bb5/4 | A5/2 G5/2 F5/2 D5/2 | E5/8 |
      F5/4 A5/4 | E5/4 C5/4 | D5/2 F5/2 Bb5/2 A5/2 | A5/8 |
      Bb5/3 A5/1 G5/4 | G5/2 A5/2 Bb5/2 G5/2 | F5/8 | r/8""")
    s.arpeggio(A, '01232101', instr='arp', rate=0.25, octave=4, amp=0.8)
    s.arpeggio(B, '01232101', instr='arp', rate=0.25, octave=4, start_bar=8, amp=0.8)
    s.bassline(A, 'r...f...'); s.bassline(B, 'r...f...', start_bar=8)
    s.drums('....h.......h...', 16, amp=0.5)
    return s.mix(echo=(0.31, 0.35, 0.25), target_rms=0.18)


@song
def route_b():
    s = Song(132, 16)
    A = "Bm G D A Bm G A F#"
    B = "G A Bm Bm G A F# F#"
    s.melody('lead', """
      B4/2 D5/2 F#5/3 E5/1 | D5/2 B4/2 G4/4 | A4/2 D5/2 F#5/2 A5/2 | G5/3 F#5/1 E5/4 |
      F#5/2 B5/2 A5/2 F#5/2 | G5/2 F#5/2 E5/2 D5/2 | C#5/2 E5/2 A5/2 G5/2 | F#5/6 r/2 |
      D6/4 B5/2 G5/2 | C#6/4 A5/2 E5/2 | D6/3 C#6/1 B5/2 F#5/2 | B5/6 r/2 |
      G5/3 A5/1 B5/2 D6/2 | C#6/3 B5/1 A5/2 E5/2 | A#5/4 C#6/4 | F#6/6 r/2""")
    s.bassline(A, 'r.rro.r.'); s.bassline(B, 'r.rro.r.', start_bar=8)
    s.stabs(A, 'x..x..x.', amp=0.7); s.stabs(B, 'x..x..x.', start_bar=8, amp=0.7)
    s.drums('k.h.s.h.k.k.s.h.', 16, amp=0.85)
    return s.mix(echo=(0.23, 0.25, 0.12), target_rms=0.2)


@song
def deepcall():
    s = Song(120, 8)
    P = "Em F Em F Em C B B"
    s.melody('lead12', """
      E5/1 r/1 E5/1 F5/1 E5/2 B4/2 | C5/2 B4/1 A4/1 B4/4 | E5/1 r/1 E5/1 F5/1 G5/2 A5/2 | Bb5/2 A5/2 G5/2 F5/2 |
      E5/1 r/1 G5/1 B5/1 E6/2 D6/2 | C6/2 B5/1 A5/1 G5/2 E5/2 | D#5/2 F#5/2 A5/2 F#5/2 | D#5/6 r/2""")
    s.pad(P, instr='organ', octave=3, amp=1.0)
    s.bassline(P, 'rrrrrrrr', amp=0.9)
    s.drums('k..sk..sk..sk.ss', 8, amp=0.8)
    return s.mix(echo=(0.25, 0.3, 0.15), target_rms=0.19)


@song
def rift():
    s = Song(84, 8)
    P = "Dm Eb Dm Eb Bb A Dm Dm"
    s.melody('strings', """
      A4/6 G4/2 | G4/4 Bb4/4 | A4/2 D5/2 F5/2 E5/2 | Eb5/8 |
      D5/3 C5/1 Bb4/4 | C#5/4 E5/4 | D5/8 | r/8""", amp=1.5)
    s.melody('bell', "r/8 | r/8 | r/8 | r/4 G5/2 Bb5/2 | r/8 | r/4 A5/2 C#6/2 | r/8 | D6/2 A5/2 F5/2 D5/2", amp=0.8)
    s.pad(P, octave=3, amp=1.3)
    s.bassline(P, 'r-------', octave=1, instr='bassp', amp=1.4)
    s.drums('k..k............', 8, amp=0.9)
    return s.mix(echo=(0.54, 0.45, 0.35), target_rms=0.16)


@song
def cradle():
    s = Song(64, 8)
    P = "Cm Abmaj7 Fm G Cm Ab Bb G"
    s.melody('organ', """
      G4/8 | Ab4/4 C5/4 | C5/4 Ab4/4 | B4/8 | C5/4 Eb5/4 | Eb5/4 C5/4 | D5/4 F5/4 | G5/8""", amp=1.2)
    s.pad(P, instr='strings', octave=3, amp=1.2)
    s.pad(P, instr='pad', octave=4, amp=0.8)
    s.bassline(P, 'r-------', octave=1, instr='bassp', amp=1.4)
    s.drums('t.......t.......', 8, amp=0.6)
    return s.mix(echo=(0.47, 0.5, 0.4), target_rms=0.16)


@song
def crown():
    s = Song(100, 16)
    A = "C G Am F C G F G"
    B = "F G Em Am F G C C"
    s.melody('lead', """
      E5/2 G5/2 C6/3 B5/1 | B5/2 A5/2 G5/4 | A5/2 C6/2 E6/2 D6/2 | C6/6 r/2 |
      E5/2 G5/2 C6/2 E6/2 | D6/3 C6/1 B5/2 G5/2 | A5/2 C6/2 F6/2 E6/2 | D6/6 r/2 |
      C6/3 A5/1 F5/4 | B5/3 G5/1 D5/4 | E5/2 G5/2 B5/2 E6/2 | C6/6 r/2 |
      A5/2 C6/2 F6/2 A6/2 | G6/3 F6/1 D6/2 B5/2 | C6/8 | r/8""")
    s.pad(A, instr='strings', octave=3); s.pad(B, instr='strings', octave=3, start_bar=8)
    s.bassline(A, 'r.f.o.f.'); s.bassline(B, 'r.f.o.f.', start_bar=8)
    s.arpeggio(A, '0120', rate=0.5, amp=0.6); s.arpeggio(B, '0120', rate=0.5, start_bar=8, amp=0.6)
    s.drums('k...s...k...s.h.', 16, amp=0.7)
    return s.mix(echo=(0.3, 0.3, 0.2), target_rms=0.19)


@song
def trial():
    s = Song(120, 8)
    P = "Am Am F G Am Am F E"
    s.melody('lead', """
      A4/1 C5/1 E5/1 A5/1 G5/2 E5/2 | A5/1 G5/1 E5/1 C5/1 D5/2 E5/2 | F5/2 A5/2 C6/2 A5/2 | G5/3 F5/1 D5/4 |
      A4/1 C5/1 E5/1 A5/1 B5/2 C6/2 | B5/1 A5/1 G5/1 E5/1 A5/4 | F5/2 E5/2 D5/2 C5/2 | B4/4 E5/4""")
    s.bassline(P, 'r.o.r.o.')
    s.stabs(P, 'x...x.x.', amp=0.7)
    s.drums('k.h.s.h.k.h.s.hh', 8, amp=0.8)
    return s.mix(echo=(0.25, 0.25, 0.12), target_rms=0.19)


# ═══ Battles ═══════════════════════════════════════════════════════════════
@song
def battle_trainer():
    s = Song(152, 16)
    A = "Em C D B Em C D D"
    B = "C D Em Em C D B B"
    s.melody('lead', """
      E5/1 F#5/1 G5/2 B5/2 A5/1 G5/1 | E5/2 G5/2 C6/4 | D6/1 C6/1 B5/1 A5/1 F#5/2 D5/2 | D#5/4 F#5/2 B5/2 |
      E5/1 F#5/1 G5/2 B5/2 E6/2 | D6/2 C6/2 G5/2 E5/2 | F#5/2 A5/2 D6/2 F#6/2 | E6/1 D6/1 C6/1 A5/1 D6/4 |
      E6/3 D6/1 C6/2 G5/2 | D6/3 C6/1 B5/2 A5/2 | B5/2 G5/2 E5/2 G5/2 | B5/1 C6/1 B5/1 A5/1 G5/2 F#5/2 |
      G5/2 C6/2 E6/2 G6/2 | F#6/3 E6/1 D6/2 A5/2 | B5/2 D#6/2 F#6/2 B6/2 | A6/1 F#6/1 D#6/1 B5/1 F#5/4""")
    s.bassline(A, 'rorororo'); s.bassline(B, 'rorororo', start_bar=8)
    s.arpeggio(A, '0120', instr='harm', rate=0.25, octave=4, amp=0.6); s.arpeggio(B, '0120', instr='harm', rate=0.25, octave=4, start_bar=8, amp=0.6)
    s.drums('k.h.s.h.k.k.s.h.', 15); s.drums('k.h.s.h.k.k.ssss', 1, start_bar=15)
    return s.mix(echo=(0.2, 0.2, 0.1), target_rms=0.21)


@song
def battle_rival():
    s = Song(160, 16)
    A = "Gm Eb F D Gm Eb Cm D"
    B = "Eb F Gm Gm Eb F D D"
    s.melody('lead', """
      G5/2 D5/1 G5/1 Bb5/2 A5/2 | G5/2 Eb5/2 Bb4/4 | C5/2 F5/1 A5/1 C6/2 Bb5/2 | A5/4 F#5/4 |
      G5/2 D5/1 G5/1 Bb5/2 D6/2 | C6/1 Bb5/1 G5/2 Eb6/4 | D6/2 C6/2 Bb5/2 G5/2 | F#5/4 A5/2 D6/2 |
      Eb6/3 D6/1 C6/2 Bb5/2 | C6/3 Bb5/1 A5/2 F5/2 | G5/2 Bb5/2 D6/2 G6/2 | F6/2 D6/2 Bb5/2 G5/2 |
      Bb5/2 Eb6/2 G6/2 Eb6/2 | A5/2 C6/2 F6/2 C6/2 | D6/2 F#6/2 A6/2 F#6/2 | D6/4 D5/4""")
    s.melody('harm', """
      D5/4 D5/4 | Bb4/4 G4/4 | A4/4 C5/4 | F#4/8 | D5/4 D5/4 | G4/4 Bb4/4 | G4/4 Eb4/4 | D4/8 |
      G5/4 Eb5/4 | A4/4 C5/4 | Bb4/4 D5/4 | D5/8 | G5/4 Eb5/4 | F5/4 A4/4 | A4/4 D5/4 | F#4/8""", amp=0.8)
    s.bassline(A, 'rrorrorr'); s.bassline(B, 'rrorrorr', start_bar=8)
    s.drums('k.hsk.s.k.hsk.sh', 15); s.drums('k.s.k.s.ssssssss', 1, start_bar=15)
    return s.mix(echo=(0.19, 0.2, 0.1), target_rms=0.21)


@song
def battle_deepcall():
    s = Song(144, 8)
    P = "Em F Em F Em F G F"
    s.melody('lead12', """
      E5/1 E5/1 r/1 E5/1 F5/2 E5/2 | A5/2 G5/2 F5/2 E5/2 | E5/1 E5/1 r/1 B5/1 C6/2 B5/2 | A5/2 C6/2 F5/4 |
      E6/2 D6/2 B5/2 G5/2 | F5/2 A5/2 C6/2 A5/2 | B5/2 D6/2 G5/2 B5/2 | A5/4 F5/4""")
    s.pad(P, instr='organ', octave=3, amp=0.9)
    s.bassline(P, 'rrrrrrro')
    s.drums('k.hsk.s.k.hsk.s.', 7); s.drums('k.s.k.s.k.ssssss', 1, start_bar=7)
    return s.mix(echo=(0.21, 0.2, 0.1), target_rms=0.21)


@song
def battle_boss():
    s = Song(150, 16)
    A = "Dm Bb Gm A Dm Bb C A"
    B = "Bb C Dm Dm Gm A Dm A"
    s.melody('lead', """
      D5/1 r/1 D5/1 F5/1 A5/2 D6/2 | C6/2 Bb5/2 F5/4 | G5/1 r/1 G5/1 Bb5/1 D6/2 G6/2 | E6/2 C#6/2 A5/4 |
      D6/1 C6/1 A5/1 F5/1 D5/2 F5/2 | Bb5/2 A5/2 F5/2 D5/2 | E5/2 G5/2 C6/2 E6/2 | C#6/4 A5/4 |
      D6/3 C6/1 Bb5/2 F5/2 | E6/3 D6/1 C6/2 G5/2 | F6/2 E6/2 D6/2 A5/2 | D6/6 r/2 |
      Bb5/2 D6/2 G6/2 D6/2 | C#6/2 E6/2 A6/2 E6/2 | F6/2 D6/2 A5/2 F5/2 | E5/4 C#6/4""")
    s.pad(A, instr='organ', octave=3, amp=0.8); s.pad(B, instr='organ', octave=3, start_bar=8, amp=0.8)
    s.bassline(A, 'rrorrorr'); s.bassline(B, 'rrorrorr', start_bar=8)
    s.drums('k.hsk.s.kkhsk.s.', 15); s.drums('k.s.k.s.ttttssss', 1, start_bar=15)
    return s.mix(echo=(0.2, 0.2, 0.1), target_rms=0.21)


@song
def battle_oriel():
    s = Song(156, 16)
    A = "Bm G Em F# Bm G A F#"
    B = "G A Bm D Em F# Bm F#"
    s.melody('lead', """
      B5/2 F#5/2 D5/2 B4/2 | G5/3 F#5/1 E5/2 D5/2 | E5/2 G5/2 B5/2 E6/2 | D6/2 C#6/2 A#5/4 |
      B5/1 C#6/1 D6/2 F#6/3 E6/1 | D6/2 B5/2 G5/4 | A5/2 C#6/2 E6/2 A6/2 | F#6/4 A#5/4 |
      B5/3 A5/1 G5/2 B5/2 | C#6/3 B5/1 A5/2 C#6/2 | D6/2 F#6/2 B6/4 | A6/2 F#6/2 D6/4 |
      G6/3 F#6/1 E6/2 B5/2 | A#5/2 C#6/2 F#6/2 E6/2 | D6/2 C#6/2 B5/4 | F#5/4 A#5/4""")
    s.pad(A, instr='organ', octave=3); s.pad(B, instr='organ', octave=3, start_bar=8)
    s.melody('strings', "B3/8 | G3/8 | E3/8 | F#3/8 | B3/8 | G3/8 | A3/8 | F#3/8 | G3/8 | A3/8 | B3/8 | D4/8 | E4/8 | F#4/8 | B3/8 | F#3/8", amp=1.2)
    s.bassline(A, 'rorrorro'); s.bassline(B, 'rorrorro', start_bar=8)
    s.drums('k.hsk.s.k.hsksss', 15); s.drums('c...k.s.k.ssssss', 1, start_bar=15)
    return s.mix(echo=(0.19, 0.25, 0.12), target_rms=0.21)


@song
def battle_legend():
    s = Song(138, 16)
    A = "Cm Ab Eb Bb Cm Ab Fm G"
    B = "Ab Bb Cm Cm Ab Bb G G"
    s.melody('strings', """
      G5/4 C6/4 | Eb6/3 D6/1 C6/4 | Bb5/4 G5/4 | F5/3 G5/1 Bb5/4 |
      C6/2 D6/2 Eb6/2 G6/2 | F6/3 Eb6/1 C6/4 | Ab5/2 C6/2 F6/2 Eb6/2 | D6/4 B5/4 |
      C6/3 Bb5/1 Ab5/4 | D6/3 C6/1 Bb5/4 | Eb6/2 G6/2 C7/4 | Bb6/2 G6/2 Eb6/4 |
      C6/3 D6/1 Eb6/4 | F6/3 Eb6/1 D6/4 | B5/4 D6/4 | G6/8""", amp=1.4, octave=-1)
    s.melody('lead', """
      G5/4 C6/4 | Eb6/3 D6/1 C6/4 | Bb5/4 G5/4 | F5/3 G5/1 Bb5/4 |
      C6/2 D6/2 Eb6/2 G6/2 | F6/3 Eb6/1 C6/4 | Ab5/2 C6/2 F6/2 Eb6/2 | D6/4 B5/4 |
      C6/3 Bb5/1 Ab5/4 | D6/3 C6/1 Bb5/4 | Eb6/2 G6/2 C7/4 | Bb6/2 G6/2 Eb6/4 |
      C6/3 D6/1 Eb6/4 | F6/3 Eb6/1 D6/4 | B5/4 D6/4 | G6/8""", amp=0.7)
    s.arpeggio(A, '01210121', instr='harm', rate=0.25, octave=4, amp=0.7)
    s.arpeggio(B, '01210121', instr='harm', rate=0.25, octave=4, start_bar=8, amp=0.7)
    s.bassline(A, 'r.r.r.ro'); s.bassline(B, 'r.r.r.ro', start_bar=8)
    s.drums('k.h.s.hkk.h.s.hs', 15); s.drums('c...t.t.t.t.ssss', 1, start_bar=15)
    return s.mix(echo=(0.22, 0.3, 0.15), target_rms=0.21)


@song
def victory():
    s = Song(132, 8)
    P = "C F G C Am F G C"
    s.melody('lead', """
      C5/1 E5/1 G5/1 C6/1 E6/4 | C6/2 A5/2 F5/4 | D6/1 B5/1 G5/1 D6/1 B5/4 | C6/4 G5/4 |
      A5/2 C6/2 E6/4 | F6/2 E6/2 C6/4 | D6/2 B5/2 G5/2 B5/2 | C6/6 r/2""")
    s.bassline(P, 'r.f.o.f.')
    s.arpeggio(P, '0120', rate=0.5, octave=4, amp=0.7)
    s.drums('k...s...k.k.s...', 8, amp=0.7)
    return s.mix(echo=(0.23, 0.25, 0.12), target_rms=0.19)


# ═══ Jingles (one-shots) ═════════════════════════════════════════════════
def _j(bpm, bars, bpb=4):
    return Song(bpm, bars, beats_per_bar=bpb)


@jingle
def item():
    s = _j(150, 1, 3)
    s.melody('lead', 'C5/0.5 E5/0.5 G5/0.5 C6/0.5 E6/3', step=0.5)
    s.melody('harm', 'r/2 G4/3', step=0.5)
    s.melody('bass', 'C3/1 C3/4', step=0.5)
    return s.mix(target_rms=0.2, loop=False)


@jingle
def heal():
    s = _j(110, 2, 3)
    s.melody('bell', 'E5/1 G5/1 C6/2 | D6/1 B5/1 G5/2 | C6/6', step=0.5)
    s.pad('C:3 G:3', octave=4, amp=0.8)
    return s.mix(target_rms=0.17, loop=False)


@jingle
def level():
    s = _j(160, 1, 3)
    s.melody('lead', 'G5/0.5 A5/0.5 B5/0.5 D6/0.5 G6/4', step=0.5)
    s.melody('bass', 'G3/2 G3/4', step=0.5)
    return s.mix(target_rms=0.18, loop=False)


@jingle
def catch():
    s = _j(150, 2, 4)
    s.melody('lead', 'C5/1 C5/1 C5/1 E5/1 G5/2 E5/2 | F5/1 A5/1 C6/2 D6/1 B5/1 C6/2', step=0.5)
    s.melody('harm', 'E4/4 G4/4 | A4/4 G4/4', step=0.5)
    s.bassline('C:4 F:2 C:2', 'r.o.')
    s.drums('k...s...k.k.s...', 2, amp=0.7)
    return s.mix(target_rms=0.2, loop=False)


@jingle
def evolve():
    s = _j(120, 3, 4)
    s.arpeggio('C:4 F:4 G:4', '012345', instr='arp', rate=0.25, octave=4, amp=1.0)
    s.melody('lead', 'r/4 E5/4 | F5/4 A5/4 | B5/4 D6/2 G6/2', step=0.5)
    s.pad('C:4 F:4 G:4', instr='strings', octave=3)
    return s.mix(target_rms=0.2, loop=False)


@jingle
def sigil():
    s = _j(120, 2, 4)
    s.melody('lead', 'G4/1 C5/1 E5/1 G5/1 C6/3 G5/1 | A5/1 B5/1 C6/1 D6/1 E6/4', step=0.5)
    s.melody('strings', 'C4/8 | G4/8', step=0.5, amp=1.2)
    s.bassline('C:4 G:2 C:2', 'r.o.')
    s.drums('k...s...k.k.ssss', 1, amp=0.8); s.drums('c...............', 1, start_bar=1, amp=0.8)
    return s.mix(target_rms=0.2, loop=False)


def main(names=None):
    os.makedirs(BGM, exist_ok=True)
    idx_path = os.path.join(ROOT, 'public', 'assets', 'audio', 'index.json')
    idx = json.load(open(idx_path))
    for name, fn in SONGS.items():
        if names and name not in names:
            continue
        x = fn()
        write_ogg(os.path.join(BGM, f'{name}.ogg'), x)
        if name not in idx['bgm']:
            idx['bgm'].append(name)
        print(f'bgm {name}: {len(x) / SR:.1f}s')
    for name, fn in JINGLES.items():
        if names and name not in names:
            continue
        x = fn()
        # trim trailing silence
        nz = np.nonzero(np.abs(x) > 1e-3)[0]
        x = x[:nz[-1] + 1] if len(nz) else x
        write_ogg(os.path.join(SFX, f'{name}.ogg'), x)
        if name not in idx['sfx']:
            idx['sfx'].append(name)
        print(f'jingle {name}: {len(x) / SR:.1f}s')
    idx['bgm'].sort(); idx['sfx'].sort()
    json.dump(idx, open(idx_path, 'w'), indent=1)


if __name__ == '__main__':
    main(sys.argv[1:] or None)
