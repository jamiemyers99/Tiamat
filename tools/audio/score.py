"""The Tiamat soundtrack: hand-written melodies and chord charts, arranged by compose.py.

Each song: name, tempo, bar (beats per bar), key, mode, swing (0.5 straight … 0.67 full triplet swing),
form (section order; the file loops back to the start), sections {chords, lead [(instrument, melody, opts)],
acc [(pattern, opts)], drums (pattern, opts)}, and cat (loudness target: town / route / calm / battle / jingle).
Melody notes on strong beats are checked against the chords when rendering.

Sound world: warm acoustic and orchestral instruments (flutes, strings, harp, guitars, marimba, Rhodes, brass),
soft brushes and hand percussion; the towns by the sea and the factory town groove; battles drive hard but stay
warm — no shrill leads, nothing buzzy.
"""

SONGS = []


def song(**kw):
    SONGS.append(kw)
    return kw


def lead(inst, mel, **o):
    return (inst, mel, o)


def dbl(inst, mel, name, **o):
    """A doubling of the melody (sits a little under the lead)."""
    return (inst, mel, dict(o, **{'as': name, 'role': 'double'}))


# ════════════════════════════════════ TITLE / CROWN ═══════════════════════════════════════
# The main theme. Horn over harp and strings, then violins, then everyone. The Crown (the last place in the game,
# and the credits) plays the same theme broader and slower.
TITLE_A = 'I | vi | IV | V | I | iii | IV | Vsus4 V'
TITLE_B = 'vi | IV | I | V | vi | IV | ii7 | Vsus4 V'
title_a = ('D5:1 A5:1.5 G5:.5 F#5:1 | F#5:1.5 E5:.5 D5:1 B4:1 | D5:1 E5:.5 F#5:.5 G5:1 B5:1 | A5:3 r:1 |'
           'D5:1 A5:1.5 G5:.5 F#5:1 | E5:1 F#5:.5 A5:.5 C#6:2 | B5:1.5 A5:.5 G5:1 E5:1 | E5:2 C#5:1 A4:1 |')
title_b = ('B5:2 A5:1 F#5:1 | G5:1.5 A5:.5 B5:1 D6:1 | A5:2 F#5:1 D5:1 | E5:1.5 F#5:.5 E5:1 C#5:1 |'
           'D5:1 F#5:1 B5:1.5 A5:.5 | G5:1 B5:1 D6:1.5 E6:.5 | D6:1 B5:1 G5:1 E5:1 | A5:2 E5:1 C#5:1 |')
song(name='title', tempo=80, key='D', cat='town', form=['A', 'B', 'A2'],
     sections={
         'A': dict(chords=TITLE_A, lead=[lead('horn', title_a, octave=-1, vel=92)],
                   acc=[('pad', dict(inst='slow_strings', vel=52, lo=50, hi=69)), ('arp', dict(inst='harp', lo=50, hi=79, step=.5, vel=58)),
                        ('bass', dict(inst='contrabass', style='whole', lo=26, vel=80))]),
         'B': dict(chords=TITLE_B, lead=[lead('violin', title_b, vel=90)],
                   acc=[('pad', dict(inst='slow_strings', vel=56, lo=50, hi=69)), ('arp', dict(inst='harp', lo=50, hi=79, step=.5, vel=56)),
                        ('counter', dict(inst='flute', lo=69, hi=86, vel=60, rhythm='answer')), ('bass', dict(inst='contrabass', style='whole', lo=26, vel=82)),
                        ('timp', dict(vel=58))]),
         'A2': dict(chords=TITLE_A, lead=[lead('flute', title_a, vel=90), dbl('violin', title_a, 'violin_dbl', octave=-1, vel=76)],
                    acc=[('pad', dict(inst='choir', vel=50, lo=52, hi=69, name='pad_choir')), ('pad', dict(inst='slow_strings', vel=54, lo=45, hi=64)),
                         ('arp', dict(inst='harp', lo=50, hi=79, step=.5, vel=58)), ('bells', dict(inst='celesta', every=2, vel=46)),
                         ('bass', dict(inst='contrabass', style='whole', lo=26, vel=84)), ('timp', dict(vel=62))]),
     })
song(name='crown', tempo=74, key='D', cat='town', form=['A', 'B', 'A2'],
     sections={
         'A': dict(chords=TITLE_A, lead=[lead('strings', title_a, vel=92), dbl('horn', title_a, 'horn_dbl', octave=-1, vel=80)],
                   acc=[('pad', dict(inst='choir', vel=54, lo=50, hi=67, name='pad_choir')), ('arp', dict(inst='harp', lo=50, hi=79, step=.5, vel=60)),
                        ('bass', dict(inst='contrabass', style='whole', lo=26, vel=84)), ('timp', dict(vel=60))]),
         'B': dict(chords=TITLE_B, lead=[lead('horn', title_b, octave=-1, vel=94)],
                   acc=[('pad', dict(inst='slow_strings', vel=58, lo=50, hi=69)), ('counter', dict(inst='violin', lo=74, hi=88, vel=62)),
                        ('arp', dict(inst='harp', lo=50, hi=79, step=.5, vel=58)), ('bass', dict(inst='contrabass', style='whole', lo=26, vel=84)),
                        ('bells', dict(inst='celesta', every=4, vel=44))]),
         'A2': dict(chords=TITLE_A, lead=[lead('flute', title_a, vel=90), dbl('strings', title_a, 'strings_dbl', octave=-1, vel=80)],
                    acc=[('pad', dict(inst='choir', vel=56, lo=50, hi=67, name='pad_choir')), ('pad', dict(inst='slow_strings', vel=56, lo=45, hi=62)),
                         ('arp', dict(inst='harp', lo=50, hi=79, step=.5, vel=60)), ('bass', dict(inst='contrabass', style='whole', lo=26, vel=86)),
                         ('timp', dict(vel=66)), ('stabs', dict(inst='brass', vel=64, lo=50, hi=67, rhythm=((0, 2),)))]),
     })

# ════════════════════════════════════ ROOTMERE ════════════════════════════════════════════
# Home. A gentle waltz: fingerpicked nylon guitar, ocarina, clarinet.
ROOT_A = 'I | IV | I | V | vi | IV | ii | V'
ROOT_B = 'IV | V | iii | vi | IV | I | ii7 | V7'
root_a = 'B4:1 D5:1 G5:1 | E5:2 G5:1 | D5:1.5 C5:.5 B4:1 | A4:3 | B4:1 E5:1 G5:1 | G5:1.5 F#5:.5 E5:1 | C5:1 E5:1 A5:1 | F#5:2 D5:1 |'
root_b = 'E5:2 D5:.5 C5:.5 | D5:2 A4:1 | B4:1.5 D5:.5 F#5:1 | E5:3 | E5:1 G5:1 C6:1 | B5:2 G5:1 | A5:1 G5:1 E5:1 | F#5:1.5 E5:.5 D5:1 |'
ROOT_ACC = [('fingerpick', dict(inst='nylon', lo=40, hi=67, vel=58)), ('bass', dict(inst='ac_bass', style='waltz', lo=31, vel=74)),
            ('pad', dict(inst='slow_strings', vel=36, lo=55, hi=71))]
song(name='rootmere', tempo=92, bar=3, key='G', cat='town', form=['A', 'B', 'A2', 'B2'], acc=ROOT_ACC,
     drums=('shaker', dict(vel=40)),
     sections={
         'A': dict(chords=ROOT_A, lead=[lead('ocarina', root_a, vel=88)]),
         'B': dict(chords=ROOT_B, lead=[lead('clarinet', root_b, vel=86)]),
         'A2': dict(chords=ROOT_A, lead=[lead('ocarina', root_a, vel=86), dbl('clarinet', root_a, 'clarinet_dbl', octave=-1, vel=70)]),
         'B2': dict(chords=ROOT_B, lead=[lead('flute', root_b, vel=84)],
                    acc=ROOT_ACC + [('bells', dict(inst='celesta', every=3, vel=40, lo=76, hi=88))]),
     })

# ════════════════════════════════════ BRINDLEWOOD ═════════════════════════════════════════
# The forest town: bouncy and cosy. Clarinet, pizzicato, marimba, hand drums.
BRIN_A = 'I | IV | V | I | vi | ii7 | V7 | I'
BRIN_B = 'IV | V | iii | vi | ii | V | I | V7sus V7'
brin_a = ('C5:.5 D5:.5 F5:1 A5:1 F5:1 | D5:.5 F5:.5 Bb5:1 F5:1 D5:1 | E5:1 G5:.5 C6:.5 Bb5:1 G5:1 | A5:2 r:1 C5:1 |'
          'D5:.5 F5:.5 A5:1 D6:1 C6:1 | Bb5:1.5 A5:.5 G5:1 F5:1 | E5:1 G5:1 Bb5:1 G5:1 | F5:2 r:2 |')
brin_b = ('F5:1 D5:1 F5:1 Bb5:1 | C6:1.5 Bb5:.5 G5:2 | A5:1 E5:1 C5:1 E5:1 | F5:2 D5:2 |'
          'G5:1 Bb5:1 D6:1 Bb5:1 | C6:1 G5:1 E5:1 G5:1 | A5:1.5 G5:.5 F5:1 A5:1 | G5:2 E5:2 |')
BRIN_ACC = [('pizz', dict(vel=60, lo=48, hi=65)), ('bass', dict(inst='ac_bass', style='root5', lo=29, vel=78)),
            ('pad', dict(inst='slow_strings', vel=34, lo=57, hi=72))]
song(name='brindlewood', tempo=100, key='F', swing=0.56, cat='town', form=['A', 'B', 'A2'], acc=BRIN_ACC,
     drums=('hand', dict(vel=52)),
     sections={
         'A': dict(chords=BRIN_A, lead=[lead('clarinet', brin_a, vel=90)]),
         'B': dict(chords=BRIN_B, lead=[lead('flute', brin_b, vel=86)],
                   acc=BRIN_ACC + [('counter', dict(inst='bassoon', lo=46, hi=58, vel=64, rhythm='answer'))]),
         'A2': dict(chords=BRIN_A, lead=[lead('clarinet', brin_a, vel=88)],
                    acc=BRIN_ACC + [('arp', dict(inst='marimba', lo=60, hi=79, step=.5, shape='up', vel=56))]),
     })

# ════════════════════════════════════ SALTREACH ═══════════════════════════════════════════
# The port: a breezy, funky shuffle. Steel drums, Rhodes on the offbeats, muted-guitar chops, alto sax.
SALT_A = 'Imaj7 | iii7 | IVmaj7 | V7sus | Imaj7 | vi7 | ii7 | V7'
SALT_B = 'IVmaj7 | V7 | iii7 | vi7 | ii7 | iii7 | IVmaj7 | V7sus V7'
salt_a = ('D5:.5 G5:.5 B5:.75 A5:.25 B5:1 G5:1 | F#5:.75 E5:.25 D5:1 F#5:.5 A5:1.5 | G5:.5 E5:.5 G5:.5 B5:1 A5:.5 G5:1 | A5:2 r:1 G5:.5 A5:.5 |'
          'B5:.5 D6:.5 B5:.75 A5:.25 G5:1 D5:1 | E5:.75 G5:.25 B5:1 D6:1 B5:1 | C6:1.5 B5:.5 A5:1 E5:1 | F#5:1 A5:1 C6:1.5 r:.5 |')
salt_b = ('E5:1.5 G5:.5 B5:2 | A5:1.5 F#5:.5 D5:2 | F#5:1 A5:1 D6:1 B5:1 | G5:3 r:1 |'
          'E5:.5 G5:.5 A5:1 C6:1 A5:1 | B5:1 A5:1 F#5:1 D5:1 | E5:1.5 D5:.5 E5:1 G5:1 | A5:2 F#5:1 r:1 |')
SALT_ACC = [('comp', dict(inst='rhodes', pattern='offbeat', vel=50, lo=55, hi=71)), ('skank', dict(inst='muted_gtr', vel=56, density=.5)),
            ('bass', dict(inst='finger_bass', style='funk', lo=31, vel=80))]
song(name='saltreach', tempo=98, key='G', swing=0.56, swing16=True, cat='town', form=['A', 'B', 'A2'], acc=SALT_ACC,
     drums=('funk', dict(vel=60, kit='room')),
     sections={
         'A': dict(chords=SALT_A, lead=[lead('steel_drums', salt_a, vel=92)]),
         'B': dict(chords=SALT_B, lead=[lead('alto_sax', salt_b, octave=-1, vel=84)]),
         'A2': dict(chords=SALT_A, lead=[lead('steel_drums', salt_a, vel=90), dbl('vibes', salt_a, 'vibes_dbl', vel=80)],
                    acc=SALT_ACC + [('pad', dict(inst='warm_pad', vel=36, lo=55, hi=71))]),
     })

# ════════════════════════════════════ GEARHOLLOW ══════════════════════════════════════════
# The engineers' town: proper funk. Clavinet, slap bass, a sax-and-trombone horn line, brass stabs, a jazz-guitar bridge.
GEAR_A = 'i7 | IV7 | i7 | IV7 | bVII | bIII | IV7 | IV7'
GEAR_B = 'bIIImaj7 | IV7 | v7 | i7 | bIIImaj7 | IV7 | bVII | v7'
gear_a = ('E5:.5 r:.25 E5:.25 G5:.5 A5:.5 B5:1 r:1 | C#6:.5 B5:.5 A5:.5 G5:.5 E5:1 r:1 | E5:.5 r:.25 E5:.25 G5:.5 A5:.5 B5:.5 D6:.5 B5:1 | A5:1.5 G5:.5 E5:2 |'
          'F#5:.5 A5:.5 D6:1 A5:1 F#5:1 | G5:.5 B5:.5 D6:.5 B5:.5 G5:1 r:1 | E5:.5 G5:.5 A5:.5 C#6:.5 E6:1 C#6:1 | A5:3 r:1 |')
gear_b = ('B4:1 D5:.5 F#5:.5 A5:1 F#5:1 | E5:1 G5:.5 A5:.5 C#6:2 | D5:1.5 F#5:.5 A5:1 F#5:1 | E5:2 G5:1 B5:1 |'
          'D5:1 B4:.5 D5:.5 F#5:1 D5:1 | C#5:1 E5:1 G5:1 E5:1 | F#5:1.5 E5:.5 D5:1 A4:1 | B4:2 D5:1 F#5:1 |')
GEAR_ACC = [('comp', dict(inst='clav', pattern='funk', vel=54, lo=55, hi=70)), ('bass', dict(inst='slap', style='funk', lo=28, vel=82))]
song(name='gearhollow', tempo=104, key='E', mode='dorian', swing=0.55, swing16=True, cat='town', form=['A', 'B', 'A2'], acc=GEAR_ACC,
     drums=('funk', dict(vel=66)),
     sections={
         'A': dict(chords=GEAR_A, lead=[lead('alto_sax', gear_a, octave=-1, vel=92), dbl('trombone', gear_a, 'trombone_dbl', octave=-2, vel=80)]),
         'B': dict(chords=GEAR_B, lead=[lead('jazz_gtr', gear_b, vel=92)],
                   acc=GEAR_ACC + [('pad', dict(inst='warm_pad', vel=36, lo=55, hi=71))]),
         'A2': dict(chords=GEAR_A, lead=[lead('tenor_sax', gear_a, octave=-1, vel=92), dbl('trombone', gear_a, 'trombone_dbl', octave=-2, vel=78)],
                    acc=GEAR_ACC + [('stabs', dict(inst='brass', vel=70, lo=55, hi=70, rhythm=((1.5, .25), (3.5, .25))))]),
     })

# ════════════════════════════════════ HOLLOWMERE ══════════════════════════════════════════
# The misty lakeside town (a ghost story): celesta, English horn, wordless voices. Hushed, never spooky-loud.
HOLL_A = 'i | bVI | bIII | bVII | i | iv | bVI | V'
HOLL_B = 'bVI | bVII | i | i | iv | bVII | bIII | V'
holl_a = ('A4:1.5 D5:.5 F5:1 E5:1 | D5:2 F5:1 D5:1 | C5:1.5 A4:.5 F4:1 A4:1 | G4:3 r:1 |'
          'A4:1 D5:1 F5:1.5 G5:.5 | A5:1 G5:1 Bb5:1.5 A5:.5 | F5:1.5 D5:.5 Bb4:1 D5:1 | E5:2 C#5:1 r:1 |')
holl_b = ('D5:2 F5:1 D5:1 | E5:2 C5:2 | D5:1 F5:1 A5:2 | A5:3 r:1 | G5:1.5 F5:.5 D5:2 | E5:1.5 D5:.5 C5:2 | A4:1 C5:1 F5:2 | E5:3 r:1 |')
HOLL_ACC = [('arp', dict(inst='celesta', lo=62, hi=81, step=.5, shape='up', vel=44)), ('pad', dict(inst='warm_pad', vel=44, lo=50, hi=67)),
            ('bass', dict(inst='fretless', style='whole', lo=26, vel=72))]
song(name='hollowmere', tempo=74, key='D', mode='minor', cat='calm', form=['A', 'B', 'A2'], acc=HOLL_ACC,
     sections={
         'A': dict(chords=HOLL_A, lead=[lead('english_horn', holl_a, vel=88)]),
         'B': dict(chords=HOLL_B, lead=[lead('oohs', holl_b, vel=90)],
                   acc=HOLL_ACC + [('arp', dict(inst='harp', lo=43, hi=62, step=1, shape='up', vel=50))]),
         'A2': dict(chords=HOLL_A, lead=[lead('english_horn', holl_a, vel=86), dbl('oohs', holl_a, 'oohs_dbl', vel=70)]),
     })

# ════════════════════════════════════ FROSTSPIRE ══════════════════════════════════════════
# The snowy mountain town: sparkling celesta, harp, strings and a clear flute. A touch of Lydian.
FROST_A = 'I | II | IV | I | vi | II | IV | V'
FROST_B = 'vi | IV | I | V | ii7 | IV | Vsus4 | V'
frost_a = ('E5:1 A5:1 C#6:1.5 B5:.5 | D#6:1 C#6:.5 B5:.5 F#5:2 | A5:1.5 F#5:.5 D5:1 F#5:1 | E5:3 r:1 |'
           'C#6:1 A5:1 F#5:1.5 A5:.5 | B5:1 A5:.5 B5:.5 D#6:2 | D6:1 C#6:.5 B5:.5 A5:1 F#5:1 | G#5:2 B5:1 E5:1 |')
frost_b = ('A5:2 C#6:1 A5:1 | F#5:2 A5:1 D6:1 | C#6:1.5 B5:.5 A5:2 | B5:2 G#5:1 E5:1 |'
           'D5:1 F#5:1 A5:1 B5:1 | A5:1.5 F#5:.5 D5:2 | E5:2 A5:1 B5:1 | G#5:3 r:1 |')
FROST_ACC = [('arp', dict(inst='harp', lo=52, hi=76, step=.5, vel=54)), ('pad', dict(inst='slow_strings', vel=48, lo=52, hi=69)),
             ('bass', dict(inst='ac_bass', style='root5', lo=33, vel=72)), ('bells', dict(inst='celesta', every=2, vel=40, lo=76, hi=88))]
song(name='frostspire', tempo=84, key='A', cat='town', form=['A', 'B', 'A2'], acc=FROST_ACC,
     drums=('brush', dict(vel=46, fill=False)),
     sections={
         'A': dict(chords=FROST_A, lead=[lead('flute', frost_a, vel=88)]),
         'B': dict(chords=FROST_B, lead=[lead('violin', frost_b, vel=88)]),
         'A2': dict(chords=FROST_A, lead=[lead('flute', frost_a, vel=86), dbl('celesta', frost_a, 'celesta_dbl', vel=70)]),
     })

# ════════════════════════════════════ RIFTGATE ════════════════════════════════════════════
# The last town before the end: solemn and resolute. Cello, rolling piano, horn.
RIFT_A = 'i | bVI | bIII | bVII | iv | bVI | V | V'
RIFT_B = 'bVI | bVII | bIII | bVI | iv | v | bVI | V'
riftg_a = ('G4:1.5 Eb4:.5 C4:1 Eb4:1 | Ab4:1.5 C5:.5 Eb5:1 C5:1 | Bb4:2 G4:1 Eb4:1 | F4:3 r:1 |'
           'F4:1 Ab4:1 C5:1.5 Bb4:.5 | Ab4:1 C5:1 Eb5:1.5 D5:.5 | D5:2 B4:1 G4:1 | G4:3 r:1 |')
riftg_b = ('C5:2 Eb5:1 C5:1 | D5:2 F5:1 D5:1 | Eb5:1.5 D5:.5 Bb4:2 | C5:3 r:1 |'
           'Ab4:1 C5:1 F5:2 | G4:1 Bb4:1 D5:2 | Eb5:1.5 C5:.5 Ab4:2 | B4:2 D5:1 G4:1 |')
RIFTG_ACC = [('arp', dict(inst='piano', lo=43, hi=67, step=.5, shape='rolling', vel=50)), ('pad', dict(inst='slow_strings', vel=46, lo=53, hi=70)),
             ('bass', dict(inst='contrabass', style='whole', lo=24, vel=78))]
song(name='riftgate', tempo=84, key='C', mode='minor', cat='town', form=['A', 'B', 'A2'], acc=RIFTG_ACC,
     sections={
         'A': dict(chords=RIFT_A, lead=[lead('cello', riftg_a, vel=92)]),
         'B': dict(chords=RIFT_B, lead=[lead('horn', riftg_b, octave=-1, vel=90)], acc=RIFTG_ACC + [('timp', dict(vel=50))]),
         'A2': dict(chords=RIFT_A, lead=[lead('cello', riftg_a, vel=90), dbl('violin', riftg_a, 'violin_dbl', octave=1, vel=72)]),
     })

# ════════════════════════════════════ HAVEN ═══════════════════════════════════════════════
# The Haven (healing centre): warm and jazzy with a little swing. Vibes over Rhodes, walking bass, brushes.
HAVEN_A = 'Imaj7 | vi7 | ii7 | V7 | iii7 | VI7 | ii7 | V7sus V7'
HAVEN_B = 'IVmaj7 | iii7 | vi7 | ii7 V7 | IVmaj7 | iii7 VI7 | ii7 | V7sus'
haven_a = ('C5:.5 F5:.5 A5:1 G5:.5 A5:.5 E5:1 | D5:1.5 F5:.5 A5:1 C6:1 | Bb5:.5 A5:.5 G5:1 F5:.5 D5:.5 F5:1 | E5:2 r:1 C5:1 |'
           'E5:.5 A5:.5 C6:1 A5:.5 G5:.5 E5:1 | F#5:1.5 A5:.5 C6:1 A5:1 | Bb5:1 A5:.5 G5:.5 F5:1 D5:1 | G5:2 E5:1 r:1 |')
haven_b = ('D6:1.5 C6:.5 A5:2 | G5:.5 A5:.5 C6:1 E6:2 | D6:1 C6:.5 A5:.5 F5:2 | G5:.5 Bb5:.5 D6:1 C6:1 Bb5:1 |'
           'A5:1.5 F5:.5 D5:1 F5:1 | E5:1 G5:1 F#5:1 A5:1 | Bb5:2 A5:1 G5:1 | F5:3 r:1 |')
HAVEN_ACC = [('comp', dict(inst='rhodes', pattern='charleston', vel=50, lo=53, hi=70)),
             ('bass', dict(inst='ac_bass', style='walking', vel=80, lo=29)),
             ('pad', dict(inst='slow_strings', vel=34, lo=55, hi=72))]
song(name='haven', tempo=92, key='F', swing=0.62, cat='calm', form=['A', 'B', 'A2'], acc=HAVEN_ACC,
     drums=('brush', dict(vel=56)),
     sections={
         'A': dict(chords=HAVEN_A, lead=[lead('vibes', haven_a, vel=90)]),
         'B': dict(chords=HAVEN_B, lead=[lead('flute', haven_b, vel=80)]),
         'A2': dict(chords=HAVEN_A, lead=[lead('vibes', haven_a, vel=88), dbl('flute', haven_a, 'flute_dbl', vel=64)]),
     })

# ════════════════════════════════════ HOUSE ═══════════════════════════════════════════════
# Indoors: a music box and a piano, like a quiet afternoon.
HOUSE_A = 'Imaj7 | vi7 | IVmaj7 | V7sus V7 | Imaj7 | vi7 | IVmaj7 | V7sus V7'
HOUSE_B = 'IVmaj7 | iii7 | ii7 | V7 | IVmaj7 | iii7 vi7 | ii7 | V7sus V7'
house_a = ('E5:1 G5:1 B5:1 G5:1 | C6:1.5 B5:.5 A5:1 E5:1 | F5:1 A5:1 C6:1 A5:1 | G5:2 F5:1 D5:1 |'
           'E5:1 G5:1 C6:1.5 B5:.5 | A5:1 G5:1 E5:2 | A5:1.5 G5:.5 F5:1 E5:1 | D5:2 B4:1 r:1 |')
house_b = ('A5:1.5 C6:.5 E6:2 | D6:1.5 B5:.5 G5:2 | F5:1 A5:1 C6:1.5 A5:.5 | B5:2 G5:1 F5:1 |'
           'E5:1 F5:1 A5:1 C6:1 | B5:1 G5:1 C6:1 A5:1 | A5:1.5 F5:.5 D5:2 | C6:2 B5:2 |')
HOUSE_ACC = [('arp', dict(inst='piano', lo=43, hi=64, step=.5, shape='rolling', vel=44)), ('bass', dict(inst='ac_bass', style='whole', lo=28, vel=66)),
             ('pad', dict(inst='warm_pad', vel=30, lo=55, hi=71))]
song(name='house', tempo=84, key='C', swing=0.58, cat='calm', form=['A', 'B'], acc=HOUSE_ACC,
     sections={
         'A': dict(chords=HOUSE_A, lead=[lead('musicbox', house_a, octave=-1, vel=86)]),
         'B': dict(chords=HOUSE_B, lead=[lead('piano', house_b, vel=78)]),
     })

# ════════════════════════════════════ ROUTE ═══════════════════════════════════════════════
# The early routes: an easy-going walking tune. Strummed guitar, flute then fiddle, soft kit.
ROUTE_A = 'I | IVmaj7 | vi | V | I | IV | ii7 | Vsus4 V'
ROUTE_B = 'IV | V | iii | vi | ii | II | IV | V'
route_a = ('A5:1 F#5:.5 A5:.5 D6:1.5 A5:.5 | B5:1.5 A5:.5 G5:1 F#5:1 | F#5:1 E5:.5 D5:.5 B4:1 D5:1 | E5:3 r:1 |'
           'A5:1 F#5:.5 A5:.5 D6:1 E6:1 | D6:1.5 B5:.5 G5:1 B5:1 | E6:1 D6:.5 B5:.5 G5:1 E5:1 | E5:2 C#5:1 r:1 |')
route_b = ('D5:1 G5:1 B5:1.5 A5:.5 | A5:1 C#6:1 E6:1.5 D6:.5 | C#6:2 A5:1 F#5:1 | B5:1.5 A5:.5 F#5:1 D5:1 |'
           'E5:1 G5:1 B5:1 E6:1 | D6:1 B5:1 G#5:2 | A5:1 B5:1 D6:1 B5:1 | C#6:2 E5:2 |')
ROUTE_ACC = [('strum', dict(inst='steel', vel=54, lo=50, hi=69)), ('bass', dict(inst='finger_bass', style='root5', vel=82, lo=38))]
song(name='route', tempo=104, key='D', swing=0.54, cat='route', form=['A', 'B', 'A2'], acc=ROUTE_ACC,
     drums=('softkit', dict(vel=58)),
     sections={
         'A': dict(chords=ROUTE_A, lead=[lead('flute', route_a, vel=84)], acc=ROUTE_ACC + [('pizz', dict(vel=52))]),
         'B': dict(chords=ROUTE_B, lead=[lead('fiddle', route_b, vel=82)],
                   acc=ROUTE_ACC + [('counter', dict(inst='horn', lo=55, hi=67, vel=58, pan=40))]),
         'A2': dict(chords=ROUTE_A, lead=[lead('flute', route_a, vel=82), dbl('fiddle', route_a, 'fiddle_dbl', octave=-1, vel=66)],
                    acc=ROUTE_ACC + [('pad', dict(inst='slow_strings', vel=40, lo=55, hi=71))]),
     })

# ════════════════════════════════════ ROUTE B ═════════════════════════════════════════════
# The wider world: marimba ostinato, pizzicato, oboe then horn over strings.
RB_A = 'I | iii | IV | V | vi | iii | IV | V7sus V7'
RB_B = 'IV | V | vi | I | IV | V | ii7 | V7'
rb_a = ('B4:1 E5:1 G#5:1.5 F#5:.5 | D#5:1 E5:.5 F#5:.5 G#5:1 B5:1 | A5:1.5 G#5:.5 E5:1 C#5:1 | D#5:2 F#5:2 |'
        'E5:1 G#5:1 C#6:1.5 B5:.5 | B5:1 G#5:1 D#5:2 | C#6:1.5 B5:.5 A5:1 E5:1 | E5:2 D#5:2 |')
rb_b = ('C#5:1.5 E5:.5 A5:2 | B5:1.5 A5:.5 F#5:2 | G#5:1 E5:1 C#5:2 | B4:2 E5:1 G#5:1 |'
        'A5:1 C#6:1 E6:1.5 C#6:.5 | D#6:2 B5:2 | A5:1 F#5:1 E5:1 C#5:1 | D#5:2 F#5:1 A5:1 |')
RB_ACC = [('arp', dict(inst='marimba', lo=64, hi=81, step=.5, shape='up', vel=50)), ('pizz', dict(vel=56, lo=45, hi=64)),
          ('bass', dict(inst='ac_bass', style='root5', lo=28, vel=78)), ('pad', dict(inst='slow_strings', vel=40, lo=52, hi=68))]
song(name='route_b', tempo=100, key='E', swing=0.53, cat='route', form=['A', 'B', 'A2'], acc=RB_ACC,
     drums=('softkit', dict(vel=52, rim=True)),
     sections={
         'A': dict(chords=RB_A, lead=[lead('oboe', rb_a, vel=88)]),
         'B': dict(chords=RB_B, lead=[lead('horn', rb_b, octave=-1, vel=92)]),
         'A2': dict(chords=RB_A, lead=[lead('flute', rb_a, vel=86), dbl('oboe', rb_a, 'oboe_dbl', octave=-1, vel=70)]),
     })

# ════════════════════════════════════ FOREST ══════════════════════════════════════════════
# Thornwild: kalimba, pan flute and shakuhachi over hand drums. Dorian and a little mysterious.
FOR_A = 'i7 | IV | i7 | IV | bVII | bIII | IV | V7sus'
FOR_B = 'bIII | bVII | IV | i7 | bIII | bVII | IV | IV'
for_a = ('E5:1.5 G5:.5 A5:1 E5:1 | F#5:1.5 E5:.5 D5:1 A4:1 | C5:1 D5:.5 E5:.5 G5:1 E5:1 | A5:2 F#5:2 |'
         'G5:1 B5:1 D6:1.5 B5:.5 | C6:1 G5:1 E5:2 | F#5:1 A5:1 D6:1 A5:1 | B5:2 A5:1 E5:1 |')
for_b = 'E5:2 G5:1 E5:1 | D5:2 B4:1 G4:1 | A4:1 D5:1 F#5:2 | E5:3 r:1 | G5:1.5 E5:.5 C5:2 | B4:1.5 D5:.5 G5:2 | F#5:2 E5:1 D5:1 | A4:3 r:1 |'
FOR_ACC = [('arp', dict(inst='kalimba', lo=57, hi=76, step=.5, shape='up', vel=56)), ('bass', dict(inst='fretless', style='root5', lo=33, vel=72)),
           ('pad', dict(inst='bowed_pad', vel=38, lo=52, hi=67))]
song(name='forest', tempo=92, key='A', mode='dorian', cat='route', form=['A', 'B', 'A2'], acc=FOR_ACC,
     drums=('hand', dict(vel=56)),
     sections={
         'A': dict(chords=FOR_A, lead=[lead('pan_flute', for_a, vel=88)]),
         'B': dict(chords=FOR_B, lead=[lead('shakuhachi', for_b, vel=92)]),
         'A2': dict(chords=FOR_A, lead=[lead('pan_flute', for_a, vel=86), dbl('marimba', for_a, 'marimba_dbl', octave=-1, vel=70)]),
     })

# ════════════════════════════════════ CAVE ════════════════════════════════════════════════
# The Coldforge Mines: slow and echoing. Clarinet and bassoon, marimba drips, a low bowed pad.
CAVE_A = 'i | i | bVI | bVI | iv | iv | V | V'
CAVE_B = 'bIII | bVII | i | i | bVI | iv | V | V'
cave_a = 'B4:2 E5:1 G5:1 | F#5:1.5 E5:.5 B4:2 | C5:2 E5:1 G5:1 | G5:1.5 F#5:.5 E5:2 | A4:1 C5:1 E5:1.5 D5:.5 | C5:3 r:1 | D#5:2 F#5:1 B4:1 | B4:3 r:1 |'
cave_b = 'D5:2 B4:1 G4:1 | A4:2 F#4:1 D4:1 | E4:1 G4:1 B4:2 | B4:3 r:1 | C5:1.5 B4:.5 G4:2 | A4:1.5 C5:.5 E5:2 | D#5:2 B4:2 | F#4:3 r:1 |'
CAVE_ACC = [('pad', dict(inst='bowed_pad', vel=46, lo=45, hi=62)), ('arp', dict(inst='marimba', lo=52, hi=71, step=1, shape='up', vel=48)),
            ('bells', dict(inst='celesta', every=4, vel=36, lo=76, hi=91)), ('bass', dict(inst='contrabass', style='whole', lo=28, vel=72))]
song(name='cave', tempo=72, key='E', mode='minor', cat='calm', form=['A', 'B', 'A2'], acc=CAVE_ACC,
     sections={
         'A': dict(chords=CAVE_A, lead=[lead('clarinet', cave_a, vel=86)]),
         'B': dict(chords=CAVE_B, lead=[lead('bassoon', cave_b, vel=92)]),
         'A2': dict(chords=CAVE_A, lead=[lead('clarinet', cave_a, vel=84), dbl('oohs', cave_a, 'oohs_dbl', vel=66)]),
     })

# ════════════════════════════════════ MOOR ════════════════════════════════════════════════
# Moorwind Way: a folk waltz in the fog. Fiddle and recorder over harp and brushes.
MOOR_A = 'i | bVII | bVI | bVII | i | iv | V | V'
MOOR_B = 'bIII | bVII | i | V | bIII | bVII | iv | V'
moor_a = 'B4:1 D5:1 F#5:1 | E5:1.5 D5:.5 C#5:1 | D5:1 B4:1 G4:1 | A4:3 | F#5:1 B5:1 A5:1 | G5:1.5 F#5:.5 E5:1 | C#5:1 F#5:1 A#5:1 | F#5:3 |'
moor_b = 'F#5:1 A5:1 D6:1 | C#6:1.5 B5:.5 A5:1 | B5:1 F#5:1 D5:1 | C#5:3 | D5:1 F#5:1 A5:1 | E5:1 A5:1 C#6:1 | B5:1.5 A5:.5 G5:1 | F#5:2 E5:1 |'
MOOR_ACC = [('arp', dict(inst='harp', lo=50, hi=74, step=.5, shape='up', vel=52)), ('bass', dict(inst='ac_bass', style='waltz', lo=35, vel=76)),
            ('pad', dict(inst='slow_strings', vel=36, lo=50, hi=66))]
song(name='moor', tempo=108, bar=3, key='B', mode='minor', cat='route', form=['A', 'B', 'A2', 'B2'], acc=MOOR_ACC,
     drums=('waltz', dict(vel=50, kit='brush')),
     sections={
         'A': dict(chords=MOOR_A, lead=[lead('fiddle', moor_a, vel=86)]),
         'B': dict(chords=MOOR_B, lead=[lead('recorder', moor_b, vel=84)]),
         'A2': dict(chords=MOOR_A, lead=[lead('fiddle', moor_a, vel=84), dbl('recorder', moor_a, 'recorder_dbl', octave=1, vel=64)]),
         'B2': dict(chords=MOOR_B, lead=[lead('fiddle', moor_b, vel=84)],
                    acc=MOOR_ACC + [('counter', dict(inst='cello', lo=48, hi=60, vel=60))]),
     })

# ════════════════════════════════════ LAKE ════════════════════════════════════════════════
# Glasslake: a slow, shimmering waltz on the water. Harp, strings, flute.
LAKE_A = 'I | IV | vi | V | I | IV | ii | V'
LAKE_B = 'IV | V | iii | vi | ii | V | I | V'
lake_a = 'Bb4:1 Eb5:1 G5:1 | C6:2 Bb5:1 | G5:1.5 F5:.5 Eb5:1 | D5:3 | G5:1 Bb5:1 Eb6:1 | Eb6:1.5 C6:.5 Ab5:1 | Ab5:1 G5:1 F5:1 | F5:3 |'
lake_b = 'C5:1 Eb5:1 Ab5:1 | D5:1 F5:1 Bb5:1 | Bb5:2 G5:1 | Eb5:3 | F5:1 Ab5:1 C6:1 | D6:2 Bb5:1 | G5:1.5 F5:.5 Eb5:1 | D5:2 F5:1 |'
LAKE_ACC = [('arp', dict(inst='harp', lo=51, hi=79, step=.5, vel=54)), ('pad', dict(inst='slow_strings', vel=46, lo=51, hi=68)),
            ('bass', dict(inst='ac_bass', style='waltz', lo=27, vel=70)), ('bells', dict(inst='celesta', every=3, vel=36, lo=79, hi=91))]
song(name='lake', tempo=84, bar=3, key='Eb', cat='calm', form=['A', 'B', 'A2', 'B2'], acc=LAKE_ACC,
     sections={
         'A': dict(chords=LAKE_A, lead=[lead('flute', lake_a, vel=86)]),
         'B': dict(chords=LAKE_B, lead=[lead('violin', lake_b, vel=86)]),
         'A2': dict(chords=LAKE_A, lead=[lead('flute', lake_a, vel=84), dbl('violin', lake_a, 'violin_dbl', octave=-1, vel=68)]),
         'B2': dict(chords=LAKE_B, lead=[lead('clarinet', lake_b, vel=86)]),
     })

# ════════════════════════════════════ DEEPCALL ════════════════════════════════════════════
# The Deepcall cult: sly, sinister funk. Slap bass, clav, trombone and saxes, an organ underneath.
DEEP_A = 'i7 | i7 | bVI7 | V7 | i7 | i7 | iv7 | V7'
DEEP_B = 'iv7 | bVII7 | bIIImaj7 | bVImaj7 | iiø | V7 | i7 | V7'
deep_a = ('G4:.5 r:.25 G4:.25 Bb4:.5 D5:.5 F5:.5 D5:.5 r:1 | Bb4:.5 C5:.5 D5:.5 F5:.5 G5:1 F5:.5 D5:.5 | Eb5:1 Db5:.5 Bb4:.5 G4:1 Bb4:1 | A4:.5 C5:.5 D5:.5 F#5:.5 A5:2 |'
          'G4:.5 r:.25 G4:.25 Bb4:.5 D5:.5 F5:.5 D5:.5 r:1 | D5:.5 F5:.5 G5:.5 Bb5:.5 A5:1 G5:1 | G5:1 Eb5:.5 C5:.5 Bb4:1 G4:1 | F#4:1 A4:1 C5:1 D5:1 |')
deep_b = ('Eb5:1.5 D5:.5 C5:1 G4:1 | A4:1 C5:1 Eb5:1.5 C5:.5 | D5:1 F5:1 A5:2 | G5:1.5 F5:.5 D5:2 |'
          'C5:1 Eb5:1 G5:1.5 Eb5:.5 | F#5:1.5 D5:.5 A4:1 C5:1 | Bb4:1 D5:1 G5:2 | A5:2 F#5:1 D5:1 |')
DEEP_ACC = [('comp', dict(inst='clav', pattern='funk', vel=52, lo=55, hi=70)), ('bass', dict(inst='slap', style='funk', lo=31, vel=82)),
            ('pad', dict(inst='organ', vel=34, lo=50, hi=65, name='pad_organ'))]
song(name='deepcall', tempo=96, key='G', mode='minor', swing=0.56, swing16=True, cat='town', form=['A', 'B', 'A2'], acc=DEEP_ACC,
     drums=('funk', dict(vel=64, open_hat=False)),
     sections={
         'A': dict(chords=DEEP_A, lead=[lead('trombone', deep_a, octave=-1, vel=94), dbl('tenor_sax', deep_a, 'sax_dbl', vel=76)]),
         'B': dict(chords=DEEP_B, lead=[lead('tenor_sax', deep_b, octave=-1, vel=90)]),
         'A2': dict(chords=DEEP_A, lead=[lead('alto_sax', deep_a, vel=90), dbl('trombone', deep_a, 'trombone_dbl', octave=-1, vel=76)],
                    acc=DEEP_ACC + [('stabs', dict(inst='brass', vel=64, lo=55, hi=70, rhythm=((1.5, .25), (3.5, .25))))]),
     })

# ════════════════════════════════════ RIFT ════════════════════════════════════════════════
# The Abyssal Rift: deep and uneasy but never harsh. Shakuhachi and English horn, choir, a Neapolitan shadow.
ABY_A = 'i | i | bVI | bVI | iv | iv | V | V'
ABY_B = 'bVI | bII | i | i | iv | bII | V | V'
aby_a = 'G#4:2 C#5:1 E5:1 | D#5:1.5 C#5:.5 G#4:2 | A4:2 C#5:1 E5:1 | E5:3 r:1 | F#4:1 A4:1 C#5:1.5 B4:.5 | A4:3 r:1 | B#4:2 D#5:1 G#4:1 | G#4:3 r:1 |'
aby_b = 'C#5:2 E5:1 C#5:1 | D5:2 F#5:1 A5:1 | G#5:2 E5:1 C#5:1 | C#5:3 r:1 | A4:1.5 C#5:.5 F#5:2 | F#5:1.5 E5:.5 D5:2 | D#5:2 B#4:2 | G#4:3 r:1 |'
ABY_ACC = [('pad', dict(inst='choir', vel=42, lo=52, hi=68, name='pad_choir')), ('pad', dict(inst='bowed_pad', vel=44, lo=40, hi=58)),
           ('bells', dict(inst='celesta', every=4, vel=34, lo=73, hi=88)), ('bass', dict(inst='contrabass', style='whole', lo=25, vel=76)),
           ('timp', dict(vel=44, pattern='downbeat'))]
song(name='rift', tempo=70, key='C#', mode='harmonic', cat='calm', form=['A', 'B', 'A2'], acc=ABY_ACC,
     sections={
         'A': dict(chords=ABY_A, lead=[lead('shakuhachi', aby_a, vel=92)]),
         'B': dict(chords=ABY_B, lead=[lead('english_horn', aby_b, vel=90)]),
         'A2': dict(chords=ABY_A, lead=[lead('shakuhachi', aby_a, vel=90), dbl('cello', aby_a, 'cello_dbl', octave=-1, vel=70)]),
     })

# ════════════════════════════════════ CRADLE ══════════════════════════════════════════════
# The Cradle, where Tiamat sleeps: solemn strings, choir and harp.
CRAD_A = 'i | bVI | iv | V | i | bVII | bVI | V'
CRAD_B = 'bIII | bVII | iv | i | bVI | bIII | iv | V'
crad_a = 'A4:2 D5:1 F5:1 | F5:1.5 D5:.5 Bb4:2 | G4:1 Bb4:1 D5:1.5 C5:.5 | C#5:3 r:1 | D5:1 F5:1 A5:2 | G5:1.5 E5:.5 C5:2 | D5:1 F5:1 Bb5:1.5 A5:.5 | A5:3 r:1 |'
crad_b = 'A4:2 C5:1 F5:1 | E5:2 G5:1 E5:1 | D5:2 Bb4:2 | A4:3 r:1 | D5:1.5 F5:.5 Bb5:2 | A5:1.5 G5:.5 F5:2 | G5:1 F5:1 D5:1 Bb4:1 | C#5:2 E5:2 |'
CRAD_ACC = [('pad', dict(inst='slow_strings', vel=50, lo=50, hi=67)), ('arp', dict(inst='harp', lo=45, hi=74, step=1, shape='up', vel=50)),
            ('bass', dict(inst='contrabass', style='whole', lo=26, vel=76))]
song(name='cradle', tempo=66, key='D', mode='minor', cat='calm', form=['A', 'B', 'A2'], acc=CRAD_ACC,
     sections={
         'A': dict(chords=CRAD_A, lead=[lead('violin', crad_a, vel=88)]),
         'B': dict(chords=CRAD_B, lead=[lead('choir', crad_b, vel=92)], acc=CRAD_ACC + [('timp', dict(vel=46))]),
         'A2': dict(chords=CRAD_A, lead=[lead('violin', crad_a, vel=86), dbl('oohs', crad_a, 'oohs_dbl', octave=-1, vel=70)],
                    acc=CRAD_ACC + [('pad', dict(inst='choir', vel=42, lo=52, hi=67, name='pad_choir'))]),
     })

# ════════════════════════════════════ TRIAL ═══════════════════════════════════════════════
# The Trial halls: confident and rhythmic. Pizzicato, a light snare march, horn and strings.
TRIAL_A = 'i | bVII | bVI | V | i | bVII | iv | V'
TRIAL_B = 'bIII | bVII | iv | i | bVI | bIII | iv | V'
trial_a = ('A4:.75 A4:.25 C5:.5 E5:.5 A5:1 G5:.5 E5:.5 | D5:1 B4:.5 D5:.5 G5:2 | C5:.75 C5:.25 F5:.5 A5:.5 C6:1 A5:1 | B5:2 G#5:1 E5:1 |'
           'A4:.75 A4:.25 C5:.5 E5:.5 A5:1 G5:.5 E5:.5 | B5:1 A5:.5 G5:.5 D5:2 | F5:.75 F5:.25 A5:.5 D6:.5 C6:1 A5:1 | G#5:2 B5:1 E5:1 |')
trial_b = ('E5:1.5 G5:.5 C6:2 | B5:1.5 A5:.5 G5:2 | A5:1 F5:1 D5:1 F5:1 | E5:3 r:1 |'
           'F5:1 A5:1 C6:1 A5:1 | G5:1.5 E5:.5 C5:2 | D5:1 F5:1 A5:1 D6:1 | E6:2 B5:1 G#5:1 |')
TRIAL_ACC = [('pizz', dict(vel=62, pattern='eighths', lo=45, hi=64)), ('bass', dict(inst='contrabass', style='root5', lo=28, vel=80)),
             ('pad', dict(inst='strings', vel=46, lo=52, hi=69))]
song(name='trial', tempo=112, key='A', mode='minor', cat='town', form=['A', 'B', 'A2'], acc=TRIAL_ACC,
     drums=('march', dict(vel=60)),
     sections={
         'A': dict(chords=TRIAL_A, lead=[lead('horn', trial_a, octave=-1, vel=94)]),
         'B': dict(chords=TRIAL_B, lead=[lead('strings', trial_b, vel=92)], acc=TRIAL_ACC + [('timp', dict(vel=56))]),
         'A2': dict(chords=TRIAL_A, lead=[lead('horn', trial_a, octave=-1, vel=94), dbl('strings', trial_a, 'strings_dbl', vel=78)],
                    acc=TRIAL_ACC + [('stabs', dict(inst='brass', vel=62, lo=52, hi=67, rhythm=((0, .5),)))]),
     })


# ════════════════════════════════════ BATTLES ═════════════════════════════════════════════
def battle_acc(bass='pick_bass', ost='strings', lo=57, hi=76, timp=True, stabs=False, extra=()):
    a = [('ostinato', dict(inst=ost, lo=lo, hi=hi, vel=58, pattern='16ths')), ('bass', dict(inst=bass, style='battle', lo=28, vel=86)),
         ('pad', dict(inst='strings', vel=44, lo=50, hi=66, name='pad_low'))]
    if timp:
        a.append(('timp', dict(vel=66, pattern='battle')))
    if stabs:
        a.append(('stabs', dict(inst='brass', vel=70, lo=52, hi=69, rhythm=((0, .5), (1.5, .5), (3, .5)))))
    return a + list(extra)


# Wild Morphs: bright and driving, Legends-style strings and horns.
BW_A = 'i | bVI | bVII | i | i | bVI | iv | V'
BW_B = 'bVI | bVII | i | i | bVI | bVII | V | V'
bw_a = ('E5:.5 B4:.5 E5:.5 F#5:.5 G5:1 F#5:.5 E5:.5 | E5:1.5 D5:.5 C5:1 G4:1 | F#5:.5 E5:.5 D5:.5 E5:.5 F#5:1 A5:1 | G5:2 B4:2 |'
        'E5:.5 B4:.5 E5:.5 F#5:.5 G5:1 A5:.5 B5:.5 | C6:1.5 B5:.5 G5:1 E5:1 | A5:1 G5:.5 F#5:.5 E5:1 C5:1 | D#5:2 F#5:1 B4:1 |')
bw_b = ('G5:1 E5:.5 G5:.5 C6:1.5 B5:.5 | A5:1 F#5:.5 A5:.5 D6:1.5 C6:.5 | B5:1.5 A5:.5 G5:1 E5:1 | B4:.5 E5:.5 G5:.5 B5:.5 E6:2 |'
        'E6:1 D6:.5 C6:.5 G5:1 E5:1 | F#5:1 A5:.5 D6:.5 F#6:2 | D#6:1.5 B5:.5 F#5:2 | B5:1 A5:1 F#5:1 D#5:1 |')
song(name='battle_wild', tempo=150, key='E', mode='minor', cat='battle', form=['A', 'B', 'A2', 'B2'], shelf=-4.5,
     acc=battle_acc(), drums=('battle', dict(vel=70, kit='room')),
     sections={
         'A': dict(chords=BW_A, lead=[lead('horn', bw_a, octave=-1, vel=100), dbl('strings', bw_a, 'strings_dbl', vel=80)]),
         'B': dict(chords=BW_B, lead=[lead('strings', bw_b, vel=96)], acc=battle_acc(stabs=True)),
         'A2': dict(chords=BW_A, lead=[lead('brass', bw_a, octave=-1, vel=96), dbl('flute', bw_a, 'flute_dbl', vel=76)]),
         'B2': dict(chords=BW_B, lead=[lead('strings', bw_b, vel=96), dbl('horn', bw_b, 'horn_dbl', octave=-1, vel=80)], acc=battle_acc(stabs=True)),
     })

# Trainers: brassier, with a bit of a strut.
BT_A = 'i | i | bVI | bVII | i | i | iv | V'
BT_B = 'bIII | bVII | bVI | bVII | bIII | bVII | iv | V'
bt_a = ('A4:.5 E5:.5 r:.5 E5:.5 E5:.5 D5:.5 C5:1 | B4:.5 C5:.5 D5:.5 E5:.5 A5:1.5 G5:.5 | F5:1 E5:.5 C5:.5 A4:1 C5:1 | D5:1.5 B4:.5 G4:1 B4:1 |'
        'A4:.5 E5:.5 r:.5 E5:.5 E5:.5 D5:.5 C5:1 | C5:.5 D5:.5 E5:.5 G5:.5 A5:1 C6:1 | D6:1 C6:.5 A5:.5 F5:1 D5:1 | E5:1 G#5:1 B5:1 E6:1 |')
bt_b = ('G5:1.5 E5:.5 C5:1 E5:1 | D5:1 G5:1 B5:1.5 A5:.5 | A5:1.5 G5:.5 F5:1 C5:1 | B4:1 D5:1 G5:2 |'
        'E5:1 G5:1 C6:1.5 B5:.5 | B5:1 A5:.5 G5:.5 D5:2 | F5:1 A5:1 D6:1 C6:1 | B5:2 G#5:2 |')
song(name='battle_trainer', tempo=154, key='A', mode='minor', cat='battle', form=['A', 'B', 'A2', 'B2'], shelf=-4.5,
     acc=battle_acc(ost='pizz', lo=52, hi=71), drums=('battle', dict(vel=72, kit='room')),
     sections={
         'A': dict(chords=BT_A, lead=[lead('brass', bt_a, vel=98)]),
         'B': dict(chords=BT_B, lead=[lead('strings', bt_b, vel=96)], acc=battle_acc(ost='strings')),
         'A2': dict(chords=BT_A, lead=[lead('brass', bt_a, vel=98), dbl('strings', bt_a, 'strings_dbl', octave=1, vel=76)],
                    acc=battle_acc(ost='pizz', lo=52, hi=71, stabs=True)),
         'B2': dict(chords=BT_B, lead=[lead('horn', bt_b, octave=-1, vel=98), dbl('flute', bt_b, 'flute_dbl', vel=74)], acc=battle_acc(ost='strings')),
     })

# Trial Wardens: bigger, prouder, timpani and brass.
BTR_A = 'i | bVII | bVI | V | i | bVII | iv | V'
BTR_B = 'bVI | bVII | i | i | bVI | bVII | V | V'
btr_a = ('D5:1 A4:.5 D5:.5 F5:1 E5:.5 D5:.5 | E5:1 C5:.5 E5:.5 G5:1.5 F5:.5 | F5:1 D5:.5 F5:.5 Bb5:1 A5:1 | A5:2 E5:1 C#5:1 |'
         'D5:1 A4:.5 D5:.5 F5:1 E5:.5 D5:.5 | G5:1 E5:.5 G5:.5 C6:1 Bb5:1 | Bb5:1 A5:.5 G5:.5 D5:1 G5:1 | C#5:1 E5:1 A5:2 |')
btr_b = ('D6:1.5 C6:.5 Bb5:1 F5:1 | E5:1 G5:1 C6:1.5 Bb5:.5 | A5:1 F5:1 D5:1 F5:1 | A5:.5 G5:.5 F5:.5 E5:.5 D5:2 |'
         'F5:1 Bb5:1 D6:1.5 C6:.5 | C6:1 G5:1 E5:1.5 G5:.5 | E6:2 C#6:1 A5:1 | A5:.5 G5:.5 F5:.5 E5:.5 C#5:2 |')
song(name='battle_trial', tempo=160, key='D', mode='minor', cat='battle', form=['A', 'B', 'A2', 'B2'], shelf=-4.5,
     acc=battle_acc(stabs=True), drums=('battle', dict(vel=74, kit='room')),
     sections={
         'A': dict(chords=BTR_A, lead=[lead('horn', btr_a, octave=-1, vel=100), dbl('strings', btr_a, 'strings_dbl', vel=80)]),
         'B': dict(chords=BTR_B, lead=[lead('strings', btr_b, vel=96)]),
         'A2': dict(chords=BTR_A, lead=[lead('brass', btr_a, octave=-1, vel=98), dbl('strings', btr_a, 'strings_dbl', vel=80)],
                    acc=battle_acc(stabs=True, )),
         'B2': dict(chords=BTR_B, lead=[lead('strings', btr_b, vel=96), dbl('horn', btr_b, 'horn_dbl', octave=-1, vel=80)]),
     })

# Wren, the rival: cocky and funky — slap bass, sax, brass.
BR_A = 'i | bVII | bVI | bVII | i | bVII | bVI | V'
BR_B = 'iv | bVII | bIII | bVI | iv | bVII | V | V'
br_a = ('B4:.5 D5:.5 F#5:.5 B5:1 A5:.5 F#5:1 | E5:1 C#5:.5 E5:.5 A5:1.5 G5:.5 | D5:1 B4:.5 D5:.5 G5:1 F#5:1 | E5:2 C#5:2 |'
        'B4:.5 D5:.5 F#5:.5 B5:1 A5:.5 F#5:1 | C#6:1 B5:.5 A5:.5 E5:2 | B5:1.5 A5:.5 G5:1 D5:1 | C#5:1 F#5:1 A#5:2 |')
br_b = ('G5:1.5 F#5:.5 E5:1 B4:1 | C#5:1 E5:1 A5:2 | F#5:1 A5:1 D6:1.5 C#6:.5 | B5:2 G5:2 |'
        'E5:1 G5:1 B5:1 E6:1 | C#6:1.5 B5:.5 A5:2 | A#5:2 C#6:2 | F#5:1 A#5:1 C#6:1 F#6:1 |')
BR_ACC = [('ostinato', dict(inst='strings', lo=54, hi=73, vel=56, pattern='16ths')), ('bass', dict(inst='slap', style='battle', lo=30, vel=86)),
          ('comp', dict(inst='clav', pattern='stabs', vel=58, lo=55, hi=70)), ('timp', dict(vel=60, pattern='battle'))]
song(name='battle_rival', tempo=158, key='B', mode='minor', cat='battle', form=['A', 'B', 'A2', 'B2'], shelf=-4.5, acc=BR_ACC,
     drums=('battle', dict(vel=74, kit='standard')),
     sections={
         'A': dict(chords=BR_A, lead=[lead('alto_sax', br_a, vel=96), dbl('brass', br_a, 'brass_dbl', octave=-1, vel=80)]),
         'B': dict(chords=BR_B, lead=[lead('strings', br_b, vel=96)]),
         'A2': dict(chords=BR_A, lead=[lead('brass', br_a, vel=96), dbl('alto_sax', br_a, 'sax_dbl', octave=-1, vel=78)],
                    acc=BR_ACC + [('stabs', dict(inst='brass', vel=66, lo=52, hi=69, rhythm=((1.5, .25), (3.5, .25)), name='stab_hits'))]),
         'B2': dict(chords=BR_B, lead=[lead('strings', br_b, vel=96), dbl('alto_sax', br_b, 'sax_dbl', octave=-1, vel=76)]),
     })

# Deepcall grunts: their theme at battle speed, funk-rock.
song(name='battle_deepcall', tempo=148, key='G', mode='minor', swing=0.5, cat='battle', form=['A', 'B', 'A2', 'B2'], shelf=-4.5,
     acc=[('comp', dict(inst='clav', pattern='funk', vel=58, lo=55, hi=70)), ('bass', dict(inst='slap', style='battle', lo=31, vel=86)),
          ('ostinato', dict(inst='strings', lo=55, hi=74, vel=54, pattern='16ths')), ('pad', dict(inst='organ', vel=36, lo=50, hi=65, name='pad_organ'))],
     drums=('battle', dict(vel=74, kit='standard')),
     sections={
         'A': dict(chords=DEEP_A, lead=[lead('brass', deep_a, vel=96), dbl('trombone', deep_a, 'trombone_dbl', octave=-1, vel=80)]),
         'B': dict(chords=DEEP_B, lead=[lead('tenor_sax', deep_b, octave=-1, vel=94)]),
         'A2': dict(chords=DEEP_A, lead=[lead('brass', deep_a, vel=96)]),
         'B2': dict(chords=DEEP_B, lead=[lead('strings', deep_b, vel=94), dbl('tenor_sax', deep_b, 'sax_dbl', octave=-1, vel=76)]),
     })

# Deepcall leaders (Vesk, Maren): dark orchestra, choir, taiko.
BB_A = 'i | bVI | bIII | bVII | i | bVI | iv | V'
BB_B = 'bVI | bVII | i | i | iv | bVII | bIII | V'
bb_a = ('F4:1 C5:1 Ab4:.5 C5:.5 F5:1 | F5:1.5 Eb5:.5 Db5:1 Ab4:1 | C5:1 Eb5:1 Ab5:1.5 G5:.5 | G5:2 Eb5:2 |'
        'F5:1 G5:.5 Ab5:.5 C6:1 Ab5:1 | Db6:1.5 C6:.5 Ab5:1 F5:1 | F5:1 Db5:1 Bb4:1 Db5:1 | E5:2 G5:1 C5:1 |')
bb_b = ('Ab4:2 Db5:1 F5:1 | G5:2 Eb5:1 Bb4:1 | C5:2 F5:1 Ab5:1 | G5:1 F5:1 Eb5:1 C5:1 |'
        'Db5:2 F5:1 Bb5:1 | Bb5:2 G5:1 Eb5:1 | C6:2 Ab5:1 Eb5:1 | E5:2 G5:2 |')
song(name='battle_boss', tempo=146, key='F', mode='minor', cat='battle', form=['A', 'B', 'A2', 'B2'], shelf=-4.5,
     acc=battle_acc(bass='contrabass', stabs=True, extra=[('pad', dict(inst='choir', vel=46, lo=53, hi=69, name='pad_choir'))]),
     drums=('taiko', dict(vel=80, busy=True)),
     sections={
         'A': dict(chords=BB_A, lead=[lead('horn', bb_a, vel=100), dbl('strings', bb_a, 'strings_dbl', vel=80)]),
         'B': dict(chords=BB_B, lead=[lead('choir', bb_b, vel=98), dbl('strings', bb_b, 'strings_dbl', vel=80)]),
         'A2': dict(chords=BB_A, lead=[lead('brass', bb_a, vel=98), dbl('strings', bb_a, 'strings_dbl', octave=1, vel=78)]),
         'B2': dict(chords=BB_B, lead=[lead('strings', bb_b, octave=1, vel=96), dbl('horn', bb_b, 'horn_dbl', vel=80)]),
     })

# Oriel, the Hierophant: organ, choir, strings, the Neapolitan chord in every phrase.
BO_A = 'i | bII | i | bII | iv | bVI | V | V'
BO_B = 'bVI | bVII | bIII | bVI | iv | bII | V | V'
bo_a = ('C5:1 G4:.5 C5:.5 Eb5:1 D5:.5 C5:.5 | Db5:1 F5:1 Ab5:1.5 G5:.5 | G5:1 Eb5:.5 G5:.5 C6:1 Bb5:1 | Ab5:2 F5:2 |'
        'F5:1 Ab5:1 C6:1.5 Bb5:.5 | C6:1 Ab5:1 Eb5:1 C5:1 | B4:1 D5:1 G5:1 B5:1 | D6:2 B5:2 |')
bo_b = ('C5:2 Eb5:1 Ab5:1 | D5:2 F5:1 Bb5:1 | G5:2 Eb5:1 Bb4:1 | C5:3 r:1 | Ab4:1 C5:1 F5:2 | F5:1 Ab5:1 Db6:2 | D6:2 B5:2 | G5:1 F5:1 D5:1 B4:1 |')
song(name='battle_oriel', tempo=150, key='C', mode='harmonic', cat='battle', form=['A', 'B', 'A2', 'B2'], shelf=-4.5,
     acc=battle_acc(bass='contrabass', extra=[('pad', dict(inst='church_organ', vel=40, lo=48, hi=64, name='pad_organ'))]),
     drums=('battle', dict(vel=72, kit='orchestra', toms=False)),
     sections={
         'A': dict(chords=BO_A, lead=[lead('organ', bo_a, vel=92), dbl('strings', bo_a, 'strings_dbl', vel=82)]),
         'B': dict(chords=BO_B, lead=[lead('choir', bo_b, vel=98), dbl('brass', bo_b, 'brass_dbl', octave=-1, vel=80)],
                   acc=battle_acc(bass='contrabass', stabs=True)),
         'A2': dict(chords=BO_A, lead=[lead('strings', bo_a, vel=96), dbl('organ', bo_a, 'organ_dbl', octave=-1, vel=78)]),
         'B2': dict(chords=BO_B, lead=[lead('brass', bo_b, vel=96), dbl('choir', bo_b, 'choir_dbl', vel=80)],
                    acc=battle_acc(bass='contrabass', stabs=True)),
     })

# Tiamat: the legend. Taiko, choir, horns; Phrygian flat two.
BL_A = 'i | bII | i | bII | bVI | bVII | i | i'
BL_B = 'iv | bVI | bVII | i | iv | bVI | bII | V'
bl_a = ('D5:1.5 A4:.5 D5:1 F5:1 | G5:1.5 F5:.5 Eb5:1 Bb4:1 | A5:1.5 G5:.5 F5:1 D5:1 | Eb5:2 G5:2 |'
        'F5:1 D5:1 Bb4:1 D5:1 | E5:1 G5:1 C6:1.5 Bb5:.5 | A5:2 F5:1 E5:1 | D5:3 r:1 |')
bl_b = ('Bb5:2 A5:1 G5:1 | F5:1.5 G5:.5 F5:1 D5:1 | E5:1 G5:1 C6:2 | A5:3 r:1 | G5:1 Bb5:1 D6:2 | D6:1.5 C6:.5 Bb5:1 F5:1 | G5:2 Bb5:2 | A5:1 C#6:1 E6:2 |')
song(name='battle_legend', tempo=138, key='D', mode='minor', cat='battle', form=['A', 'B', 'A2', 'B2'], shelf=-4.5,
     acc=battle_acc(bass='contrabass', lo=50, hi=69, extra=[('pad', dict(inst='choir', vel=48, lo=50, hi=67, name='pad_choir'))]),
     drums=('taiko', dict(vel=86, busy=True)),
     sections={
         'A': dict(chords=BL_A, lead=[lead('horn', bl_a, vel=100), dbl('choir', bl_a, 'choir_dbl', vel=80)]),
         'B': dict(chords=BL_B, lead=[lead('strings', bl_b, vel=98), dbl('horn', bl_b, 'horn_dbl', octave=-1, vel=80)],
                   acc=battle_acc(bass='contrabass', lo=50, hi=69, stabs=True)),
         'A2': dict(chords=BL_A, lead=[lead('brass', bl_a, vel=98), dbl('strings', bl_a, 'strings_dbl', octave=1, vel=80)]),
         'B2': dict(chords=BL_B, lead=[lead('choir', bl_b, vel=98), dbl('strings', bl_b, 'strings_dbl', vel=82)],
                    acc=battle_acc(bass='contrabass', lo=50, hi=69, stabs=True)),
     })

# Victory: a happy little march that loops until you leave the battle.
VIC_A = 'I | IV | V | I | vi | IV | ii7 | V7'
VIC_B = 'IV | V | iii | vi | IV | V | I | V7'
vic_a = ('C5:.5 E5:.5 G5:.5 C6:.5 G5:1 E5:1 | F5:.5 A5:.5 C6:1 A5:1 F5:1 | D5:.5 G5:.5 B5:1 D6:1 B5:1 | C6:2 G5:2 |'
         'A5:.5 C6:.5 E6:1 C6:1 A5:1 | F5:1 A5:1 C6:1 F5:1 | D5:1 F5:1 A5:1 C6:1 | B5:2 G5:1 F5:1 |')
vic_b = ('A5:1.5 G5:.5 F5:1 C5:1 | B5:1.5 A5:.5 G5:1 D5:1 | E5:1 G5:1 B5:2 | C6:2 A5:2 |'
         'F5:1 A5:1 C6:1 A5:1 | G5:1 B5:1 D6:2 | E6:1.5 D6:.5 C6:2 | B5:1 G5:1 F5:1 D5:1 |')
song(name='victory', tempo=132, key='C', cat='battle', form=['A', 'B'],
     acc=[('pizz', dict(vel=60, pattern='eighths', lo=48, hi=67)), ('bass', dict(inst='pick_bass', style='root5', lo=36, vel=80)),
          ('pad', dict(inst='strings', vel=44, lo=52, hi=69))],
     drums=('softkit', dict(vel=62, kit='room')),
     sections={
         'A': dict(chords=VIC_A, lead=[lead('brass', vic_a, octave=-1, vel=96), dbl('flute', vic_a, 'flute_dbl', vel=70)]),
         'B': dict(chords=VIC_B, lead=[lead('flute', vic_b, vel=90), dbl('strings', vic_b, 'strings_dbl', octave=-1, vel=76)]),
     })


# ════════════════════════════════════ JINGLES ═════════════════════════════════════════════
# Short, non-looping; they play over the paused music.
def jingle(name, tempo, key, chords, melody, lead_inst, acc, tail=1.8, dbl_inst=None, octave=0, end=None):
    """end: cut after this many beats (plus the tail), so a jingle never holds the music up for long."""
    lds = [lead(lead_inst, melody, vel=96, octave=octave)]
    if dbl_inst:
        lds.append(dbl(dbl_inst, melody, f'{dbl_inst}_dbl', vel=78, octave=octave))
    song(name=name, jingle=True, tempo=tempo, key=key, cat='jingle', form=['A'], tail_sec=tail, end_beat=end,
         sections={'A': dict(chords=chords, lead=lds, acc=acc)})


jingle('item', 124, 'C', 'I | I', 'C5:.5 E5:.5 G5:.5 C6:.5 E6:2 | r:4 |', 'celesta',
       [('arp', dict(inst='harp', lo=60, hi=84, step=.25, shape='up', vel=62))], tail=0.45, dbl_inst='vibes', end=4)
jingle('heal', 132, 'F', 'I V7 | I', 'C5:.5 F5:.5 A5:.5 C6:.5 Bb5:.5 A5:.5 G5:.5 E5:.5 | F5:3 r:1 |', 'vibes',
       [('arp', dict(inst='harp', lo=53, hi=81, step=.25, shape='up', vel=60)), ('pad', dict(inst='slow_strings', vel=50, lo=53, hi=69))],
       tail=0.5, dbl_inst='celesta', end=7)
jingle('level', 150, 'C', 'I', 'C5:.25 E5:.25 G5:.25 C6:.25 E6:1 r:2 |', 'marimba',
       [('arp', dict(inst='harp', lo=60, hi=84, step=.25, shape='up', vel=58))], tail=0.2, dbl_inst='celesta')
jingle('catch', 124, 'G', 'I V7 | I | I', 'D5:.5 G5:.5 B5:.5 D6:.5 C6:.5 B5:.5 A5:.5 F#5:.5 | G5:2 D5:1 B4:1 | G5:3 r:1 |', 'brass',
       [('pad', dict(inst='strings', vel=58, lo=55, hi=71)), ('bass', dict(inst='pizz', style='root5', lo=43, vel=72)),
        ('timp', dict(vel=62))], tail=0.5, dbl_inst='flute', octave=-1, end=10)
jingle('evolve', 100, 'Eb', 'I | IV | I | I', 'Bb4:1 Eb5:1 G5:1 Bb5:1 | C6:2 Bb5:1 Ab5:1 | G5:1 Bb5:1 Eb6:2 | Eb6:3 r:1 |', 'strings',
       [('arp', dict(inst='harp', lo=51, hi=82, step=.25, shape='up', vel=56)), ('pad', dict(inst='choir', vel=50, lo=51, hi=67, name='pad_choir')),
        ('bells', dict(inst='celesta', every=1, vel=44))], tail=0.7, dbl_inst='flute', end=13)
jingle('sigil', 112, 'C', 'I | IV V | I', 'G4:.5 C5:.5 E5:.5 G5:.5 C6:1 G5:1 | A5:.5 C6:.5 F6:1 G5:.5 B5:.5 D6:1 | C6:3 r:1 |', 'brass',
       [('pad', dict(inst='strings', vel=60, lo=52, hi=69)), ('timp', dict(vel=70)), ('arp', dict(inst='harp', lo=55, hi=79, step=.25, shape='up', vel=54))],
       tail=0.7, dbl_inst='strings', octave=-1, end=11)
