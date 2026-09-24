"""Generates every map source in tools/maps/ for the Riven Reach.

    python tools/worldgen.py && python tools/art/build_maps.py

Hand-made interiors (home_1f, home_2f, wren_house, rootmere_cottage) live in
tools/maps/ directly; everything else is authored here with the mapkit DSL.
Coordinates are tiles; (0,0) is the top-left.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mapkit import M, haven, house, trial

MAPS = []


def reg(fn):
    MAPS.append(fn)
    return fn


def conn(a, side, b, off):
    """Connect map a's `side` edge to map b. off is added to the crossing coordinate."""
    opp = {'north': 'south', 'south': 'north', 'east': 'west', 'west': 'east'}[side]
    a.props[side] = f'{b} {off}'
    return (b, opp, a.id, -off)


# ═══════════════════════════════════════════════════════════════════════════
# ACT I — ROOTS
# ═══════════════════════════════════════════════════════════════════════════
@reg
def rootmere():
    m = M('rootmere', 34, 26, name='Rootmere', kind='town', base='grass', music='rootmere', weather='none',
          battle='meadow', north='route1 0', fly='6,7')
    m.border(gaps=[('n', 16, 17)])
    m.path([(16, 0), (16, 17)])
    m.rect(4, 7, 29, 7, ':')
    m.rect(6, 17, 27, 17, ':')
    m.rect(12, 3, 13, 4, 'b')
    m.scatter([(4, 9), (9, 9), (24, 9), (29, 9), (26, 5), (27, 5), (5, 11)], 'F')
    m.put(9, 11, 'L'); m.put(24, 11, 'L')
    # pond
    m.stamp(8, 19, [' ss~~~~ss ',
                    's~~~~~~~s',
                    's~~~~~~~s',
                    ' ss~~~ss '])
    # field
    m.stamp(22, 19, ['ffffffff',
                     'fFFFFFFf',
                     'fFFFFFFf',
                     'ffff.fff'])
    m.obj('building 4 3 house w=5 h=4 roof=red variant=0 to=home_1f')
    m.obj('building 21 2 lab w=7 h=5 roof=slate wall=white label=LAB to=marsh_lab')
    m.obj('building 5 13 house w=4 h=4 roof=blue wall=wood variant=1 to=wren_house')
    m.obj('building 24 13 house w=4 h=4 roof=green wall=timber variant=2 to=rootmere_cottage')
    m.sign(15, 5, 'ROOTMERE|Where every journey takes root.')
    m.sign(20, 7, 'MARSH MORPH LAB|Dr. Ione Marsh, Morph Researcher')
    m.sign(10, 6, "{PLAYER}'S HOUSE")
    m.sign(18, 22, 'ROOTMERE POND|Please do not feed the Puddlets.')
    m.obj('prop 9 6 mailbox')
    m.obj('prop 30 20 hay'); m.obj('prop 30 21 hay'); m.obj('prop 19 19 hay')
    m.npc(11, 22, 'rm_kid', 'kid', move='wander', radius=2,
          text="When I'm older I'm going to be a Tamer too! I'll catch a Puddlet from the pond... once they stop splashing me.")
    m.npc(25, 20, 'rm_farmer', 'farmer', face='down',
          text="The Nibbits keep nibbling my carrots. Can't stay cross at them, though. Look at their little faces!")
    m.npc(21, 11, 'rm_woman', 'woman', move='wander', radius=2, script='rootmere.woman')
    m.npc(13, 17, 'rm_man', 'man_b', face='left',
          text="Route 1 is north of the village. Tall grass means wild Morphs — never go in without one of your own!")
    m.npc(22, 9, 'rm_mum', 'mum', face='down', show='got_starter&!mum_boots')
    m.trigger(16, 1, 'rootmere.north', w=2, h=2, cond='!got_starter')
    m.item(31, 3, 'tonic', hidden=True)
    return m


@reg
def marsh_lab():
    m = M('marsh_lab', 14, 10, kind='interior', name='Marsh Morph Lab', floor='lab', wall='white', music='haven')
    m.rect(0, 0, 13, 1, 'W')
    m.put(3, 1, 'w'); m.put(9, 1, 'w')
    m.put(6, 9, 'm')
    for o in ['furn 0 2 machine', 'furn 1 2 machine', 'furn 12 2 machine', 'furn 13 2 bookshelf v=1',
              'furn 4 2 bookshelf v=3', 'furn 5 2 bookshelf v=4', 'furn 10 2 pc text="Dr. Marsh\'s research notes: \'Six Seals. Six Sigils. Why would the old Wardens tie a Tamer\'s badge to a stone?\'"',
              'furn 0 7 plant', 'furn 13 7 plant', 'furn 10 6 table v=2', 'furn 11 5 chair',
              'furn 5 4 capsule_table script=lab.starters']:
        m.obj(o)
    m.npc(8, 3, 'marsh', 'marsh', face='down', script='lab.marsh', name='Dr. Marsh')
    m.npc(3, 4, 'lab_wren', 'wren', face='right', script='lab.wren', hide='got_starter')
    m.npc(11, 7, 'lab_aide', 'assistant', move='wander', radius=1, script='lab.aide')
    return m


@reg
def route1():
    m = M('route1', 34, 50, name='Route 1 · Mossway', kind='route', base='grass', music='route', battle='meadow',
          south='rootmere 0', north='brindlewood 2')
    m.border(gaps=[('n', 16, 17), ('s', 16, 17)])
    # winding path
    m.path([(16, 49), (16, 40), (8, 40), (8, 26), (22, 26), (22, 12), (16, 12), (16, 0)], ':')
    # south meadow
    m.rect(10, 43, 15, 47, 'G')
    m.grove(2, 44, 8, 4)
    m.stamp(22, 40, ['  ssssss  ',
                     ' ss~~~~ss ',
                     ' s~~~~~~s ',
                     ' s~~~~~~s ',
                     ' ss~~~~ss ',
                     '  ssssss  '])
    m.scatter([(20, 44), (21, 45), (20, 46), (31, 42), (30, 46)], 'F')
    m.grove(18, 36, 4, 2)
    m.put(18, 38, 'b'); m.put(21, 38, 'b')
    # west nook with an item, behind trees
    m.grove(2, 28, 6, 6)
    m.rect(2, 34, 7, 39, '.')
    m.put(6, 34, 'b'); m.put(7, 34, 'b')
    m.rect(10, 35, 13, 39, '.')
    # east grass above a ledge you can hop back down
    m.rect(18, 29, 29, 33, 'G')
    m.hline(34, 10, 31, 'v')
    m.rect(10, 29, 15, 33, '.')
    m.grove(12, 28, 4, 4)
    m.grove(30, 28, 2, 6)
    # middle
    m.rect(4, 16, 13, 22, 'G')
    m.grove(14, 16, 6, 6)
    m.grove(2, 14, 2, 10)
    m.grove(26, 14, 6, 10)
    m.scatter([(24, 15), (25, 18), (24, 21), (15, 23), (18, 23)], 'F')
    m.put(4, 24, 'q')
    # north
    m.rect(20, 3, 29, 9, 'G')
    m.grove(2, 2, 12, 8)
    m.rect(4, 4, 9, 7, '.')
    m.rect(4, 8, 9, 9, '.')
    m.rect(10, 8, 11, 9, '.')
    m.grove(30, 2, 2, 10)
    m.rect(19, 10, 21, 11, '.')
    m.scatter([(12, 11), (13, 10), (27, 11)], 'F')
    # objects
    m.sign(15, 46, 'ROUTE 1 · MOSSWAY|North: Brindlewood   South: Rootmere')
    m.sign(18, 2, 'BRINDLEWOOD|Home of the Moss Trial.')
    m.trainer(11, 36, 'r1_ollie', 'kid', face='left', sight=3)
    m.trainer(14, 23, 'r1_dana', 'lass', face='down', sight=3)
    m.trainer(19, 6, 'r1_theo', 'youth', face='left', sight=3)
    m.trainer(27, 31, 'r1_nell', 'kid_b', face='left', sight=4)
    m.npc(12, 24, 'r1_aide', 'assistant', face='down', script='route1.aide')
    m.item(3, 37, 'capsule', 2)
    m.item(24, 19, 'tonic')
    m.item(5, 5, 'ward_incense')
    m.item(29, 46, 'capsule', hidden=True)
    m.item(24, 33, 'purge_herb')
    return m


@reg
def brindlewood():
    m = M('brindlewood', 40, 34, name='Brindlewood', kind='town', base='grass', music='brindlewood', battle='forest',
          south='route1 -2', east='route2 0', fly='12,16')
    m.border(gaps=[('s', 18, 19), ('e', 16, 17)])
    for (x, y) in [(2, 2), (6, 2), (32, 2), (36, 4), (2, 26), (36, 30), (2, 12), (26, 2)]:
        m.rect(x, y, x + 1, y + 1, 'A')
    m.path([(18, 33), (18, 16)])
    m.rect(3, 16, 39, 17, ':')
    m.rect(4, 27, 34, 28, ':')
    m.rect(20, 9, 21, 15, ':')
    m.obj('building 9 12 haven w=6 h=4 roof=red wall=white to=brindlewood_haven')
    m.obj('building 17 4 arena w=7 h=5 roof=green wall=wood emblem=leaf type=Nature label="MOSS TRIAL" to=brindlewood_trial')
    m.obj('building 8 23 house w=4 h=4 roof=orange wall=timber variant=1 to=brindlewood_posy')
    m.obj('building 28 23 house w=5 h=4 roof=brown wall=log variant=2 to=brindlewood_house')
    # the Moss Seal in its little walled garden
    m.rect(25, 9, 31, 9, 'w'); m.rect(25, 10, 25, 12, 'w'); m.rect(31, 10, 31, 12, 'w')
    m.obj('prop 28 11 stone script=brindlewood.seal')
    m.scatter([(26, 10), (30, 10), (26, 12), (30, 12), (27, 13), (29, 13)], 'F')
    m.stamp(2, 18, [' ss~~ss ',
                    's~~~~~~s',
                    's~~~~~~s',
                    ' ss~~ss '])
    m.rect(33, 19, 37, 22, 'f'); m.rect(34, 20, 36, 21, 'F'); m.put(35, 22, '.')
    for (x, y) in [(15, 15), (24, 15), (34, 15), (16, 26), (26, 26)]:
        m.put(x, y, 'L')
    m.scatter([(4, 14), (5, 13), (14, 20), (22, 22), (24, 25), (13, 29), (6, 10), (33, 13), (23, 11)], 'F')
    m.grove(4, 4, 4, 4); m.grove(10, 4, 4, 2); m.grove(34, 6, 4, 4)
    m.grove(4, 30, 12, 2); m.grove(22, 30, 12, 2)
    m.rect(14, 22, 15, 23, 'q')
    m.sign(16, 31, 'BRINDLEWOOD|A town that grew up around a very old tree.')
    m.sign(22, 9, 'MOSS TRIAL · Warden Mossa|"Patience is a kind of strength."')
    m.sign(37, 15, 'EAST: Route 2 · Bramble Bridge')
    m.npc(24, 20, 'bw_gardener', 'farmer', face='down', script='brindlewood.gardener')
    m.npc(12, 26, 'bw_posy', 'lass', face='down', script='brindlewood.posy', hide='pip_returned')
    m.npc(32, 13, 'bw_woman', 'woman_b', move='wander', radius=2,
          text="They say the Seal-stone hums on quiet nights. Warden Mossa says it's just singing to itself.")
    m.npc(6, 25, 'bw_kid', 'kid_b', move='wander', radius=1,
          text="Warden Mossa's plants are super tough. My Cindlet singed one and it just... grew back angrier.")
    m.item(37, 3, 'tonic', hidden=True)
    m.item(28, 29, 'capsule')
    return m


@reg
def brindlewood_haven():
    return haven('brindlewood_haven', 'Brindlewood')


@reg
def brindlewood_trial():
    m = trial('brindlewood_trial', 'Brindlewood', 'Nature', 'mossa', 'mossa',
              [('bw_adept_1', 'lass', 4, 12, 'right'), ('bw_adept_2', 'ranger', 9, 8, 'left')],
              "Hey, challenger! Warden Mossa's Morphs are Nature type. Fire burns them, and birds peck them to bits. Tide Morphs will struggle in here!")
    for (x, y) in [(1, 8), (12, 8), (1, 12), (12, 12)]:
        m.obj(f'furn {x} {y} plant')
    return m


@reg
def brindlewood_house():
    m = house('brindlewood_house', "Old Aldous's House", wall='wood', floor='dark', variant=2)
    m.npc(7, 5, 'aldous', 'elder', face='left', script='brindlewood.aldous')
    return m


@reg
def brindlewood_posy():
    m = house('brindlewood_posy', "Posy's House", wall='pink', variant=1)
    m.npc(6, 3, 'posy_mum', 'woman', face='down', script='brindlewood.posy_mum')
    m.npc(3, 6, 'posy_home', 'lass', face='right', script='brindlewood.posy', show='pip_returned')
    return m


# ═══════════════════════════════════════════════════════════════════════════
# ACT II — SALT AND IRON
# ═══════════════════════════════════════════════════════════════════════════
@reg
def route2():
    m = M('route2', 48, 26, name='Route 2 · Bramble Bridge', kind='route', base='grass', music='route', battle='meadow',
          west='brindlewood 0', east='thornwild 0')
    m.border(gaps=[('w', 16, 17), ('e', 10, 11)])
    # west corridor, sealed by brambles until you have the Brush Hook
    m.grove(2, 12, 10, 4); m.grove(2, 18, 10, 6)
    m.rect(0, 16, 13, 17, ':')
    m.obj('bramble 6 16'); m.obj('bramble 6 17')
    m.rect(12, 10, 13, 17, ':')
    m.rect(12, 10, 47, 11, ':')
    # the river
    for y in range(0, 26):
        m.rect(24, y, 27, y, '~')
        m.put(23, y, 's'); m.put(28, y, 's')
    m.rect(22, 10, 29, 11, '=')
    # grass & groves
    m.rect(14, 3, 21, 7, 'G'); m.rect(14, 14, 21, 21, 'G')
    m.rect(31, 3, 38, 8, 'G'); m.rect(32, 14, 43, 20, 'G')
    m.grove(40, 2, 6, 6); m.grove(14, 22, 8, 2)
    m.grove(2, 2, 10, 8); m.rect(4, 4, 7, 7, '.'); m.rect(4, 8, 7, 8, '.')
    m.rect(8, 8, 11, 9, '.')
    m.hline(9, 14, 21, 'v')
    m.scatter([(15, 12), (19, 13), (30, 13), (34, 12), (41, 12), (44, 21), (30, 21)], 'F')
    m.rect(30, 22, 31, 23, 'q')
    m.put(38, 12, 'o'); m.put(45, 14, 'o')
    m.sign(10, 15, 'ROUTE 2 · BRAMBLE BRIDGE|West: Brindlewood   East: Thornwild')
    m.sign(30, 9, 'Mind the river — the current is stronger than it looks!')
    m.trainer(18, 12, 'r2_pim', 'kid_b', face='down', sight=4)
    m.trainer(20, 9, 'r2_fisher', 'fisher', face='right', sight=3)
    m.trainer(33, 12, 'r2_ivy', 'lass', face='left', sight=3)
    m.trainer(40, 9, 'r2_bram', 'hiker', face='down', sight=2)
    m.item(5, 5, 'td15')
    m.item(44, 18, 'capsule', 2)
    m.item(15, 20, 'tonic')
    m.item(29, 3, 'wake_chime', hidden=True)
    return m


@reg
def thornwild():
    m = M('thornwild', 44, 40, name='Thornwild', kind='route', base='forest', music='forest', battle='forest',
          west='route2 0', south='saltreach 0', fill='K')
    # carve the forest
    def c(x0, y0, x1, y1, ch='.'):
        m.rect(x0, y0, x1, y1, ch)
    c(0, 10, 15, 11, ':')                                   # entry trail
    c(4, 4, 15, 9); c(4, 12, 11, 17, 'G')
    c(14, 10, 15, 25, ':')
    c(16, 4, 27, 7); c(18, 4, 25, 5, 'G')                  # north glade
    c(16, 6, 17, 9, ':')
    c(16, 18, 21, 23, 'G')
    c(14, 24, 31, 25, ':')
    c(28, 4, 39, 13); c(30, 6, 37, 11, 'G')               # north-east grove (Pip)
    c(28, 14, 29, 23, ':')
    # the shrine clearing
    c(20, 26, 35, 33)
    c(30, 26, 31, 39, ':')
    c(4, 26, 13, 35); c(6, 28, 11, 33, 'G')                # south-west glade
    c(12, 30, 19, 31, ':')
    c(36, 16, 41, 27); c(36, 18, 41, 23, 'G')             # east pocket
    c(30, 20, 35, 21, ':')
    m.scatter([(21, 27), (34, 27), (21, 32), (34, 32)], 'F')
    m.obj('prop 23 28 stone'); m.obj('prop 32 28 stone'); m.obj('prop 23 31 stone'); m.obj('prop 32 31 stone')
    m.obj('prop 27 27 statue script=thornwild.shrine')
    m.rect(26, 29, 29, 30, ':')
    m.rect(34, 8, 35, 8, 'q')
    m.put(38, 5, 'q')
    m.obj('sign 38 5 script=thornwild.pip')
    m.sign(2, 12, 'THORNWILD|Stay on the trail. The trees remember.', walk=False)
    m.trainer(8, 11, 'tw_bugs', 'kid', face='right', sight=4)
    m.trainer(20, 22, 'tw_ranger', 'ranger', face='left', sight=4)
    m.trainer(37, 17, 'tw_mystic', 'mystic', face='down', sight=4)
    m.trainer(29, 26, 'tw_acolyte_1', 'acolyte', face='down', sight=3, hide='wren2_done')
    m.trainer(26, 33, 'tw_acolyte_2', 'acolyte_b', face='right', sight=4, hide='wren2_done')
    m.npc(30, 38, 'tw_wren', 'wren', face='up', show='never')
    m.trigger(30, 35, 'thornwild.wren', w=2, once='wren2_done', cond='beat:tw_acolyte_1&beat:tw_acolyte_2')
    m.trigger(30, 34, 'thornwild.acolytes_block', w=2, cond='!beat:tw_acolyte_1|!beat:tw_acolyte_2')
    m.item(5, 5, 'td14')
    m.item(40, 26, 'prime_capsule')
    m.item(24, 4, 'strong_tonic', hidden=True)
    m.item(5, 34, 'capsule', 3)
    m.item(36, 12, 'nerve_balm')
    # starter rescue: a Spriglet boxed in by brambles in the south-west glade (Brush Hook clears them)
    m.npc(4, 26, 'tw_spriglet', 'mon:spriglet', face='right', script='rescue.spriglet',
          show='!var:starter=spriglet', hide='rescued_spriglet')
    m.obj('bramble 5 26 hide=var:starter=spriglet'); m.obj('bramble 4 27 hide=var:starter=spriglet')
    return m


@reg
def saltreach():
    m = M('saltreach', 46, 38, name='Saltreach', kind='town', base='grass', music='saltreach', battle='coast',
          north='thornwild 0', east='route3 0', fly='11,12')
    m.border(gaps=[('n', 30, 31), ('e', 12, 13)])
    # sea & beach
    m.rect(0, 25, 45, 37, '~')
    m.rect(2, 22, 43, 24, 's')
    for x in range(0, 46):
        if (x * 7) % 5 == 0:
            m.put(x, 22, '.')
    m.rect(0, 22, 1, 24, 's'); m.rect(44, 22, 45, 24, 's')
    m.rect(38, 18, 44, 24, 's')
    # pier
    m.rect(20, 25, 21, 31, 'k'); m.rect(14, 31, 27, 32, 'k')
    m.rect(33, 25, 34, 28, 'k')
    # island
    m.stamp(38, 30, [' sss ', 'sssss', ' sss '])
    m.rect(44, 14, 45, 37, 'R')
    # streets
    m.path([(30, 0), (30, 12)], ';')
    m.rect(3, 12, 45, 13, ';')
    m.rect(20, 14, 21, 24, ';')
    m.rect(24, 9, 25, 11, ';')
    # buildings
    m.obj('building 8 8 haven w=6 h=4 roof=red wall=white to=saltreach_haven')
    m.obj('building 21 3 arena w=7 h=5 roof=blue wall=brick emblem=drop type=Tide label="TIDE TRIAL" to=saltreach_trial cond=docks_done locked="The door is locked. A note is nailed to it:|GONE TO THE DOCKS TO SORT OUT SOME BARNACLES. — BRANN"')
    m.obj('building 32 17 house w=5 h=4 roof=teal wall=sand variant=0 to=saltreach_house door=3')
    m.obj('building 4 16 house w=5 h=4 roof=navy wall=plaster variant=1 to=saltreach_net')
    m.obj('lighthouse 41 19 to=saltreach_lighthouse')
    m.obj('prop 14 16 stall'); m.obj('prop 17 16 stall')
    m.obj('prop 24 27 boat walk=0'); m.obj('prop 15 34 boat')
    m.obj('prop 26 24 barrel'); m.obj('prop 27 24 crate'); m.obj('prop 18 24 crate')
    m.obj('prop 35 11 stone script=saltreach.seal')
    m.grove(2, 2, 6, 4); m.grove(10, 2, 8, 4); m.grove(36, 2, 8, 6)
    m.rect(15, 6, 16, 7, 'P'); m.rect(4, 6, 5, 7, 'P'); m.rect(28, 6, 29, 7, 'P'); m.rect(42, 14, 43, 15, 'P')
    for (x, y) in [(7, 11), (19, 11), (29, 14), (39, 11), (22, 20)]:
        m.put(x, y, 'L')
    m.scatter([(3, 14), (16, 10), (33, 9), (38, 14), (26, 15)], 'F')
    m.sign(28, 11, 'SALTREACH|Salt on the wind, fish on the table.')
    m.sign(26, 8, 'TIDE TRIAL · Captain Brann|"The sea tests everyone."')
    m.sign(22, 23, 'SALTREACH DOCKS')
    m.npc(20, 31, 'st_brann', 'brann', face='up', script='saltreach.brann_docks', hide='docks_done')
    m.trainer(20, 27, 'st_acolyte_1', 'acolyte', face='up', sight=2, leave='1')
    m.trainer(21, 27, 'st_acolyte_2', 'acolyte_b', face='up', sight=2, leave='1')
    m.npc(43, 12, 'st_guard', 'sailor', face='left', script='saltreach.eastguard', hide='sigil_tide')
    m.trigger(43, 13, 'saltreach.eastgate', cond='!sigil_tide')
    m.npc(13, 18, 'st_fishwife', 'woman_b', face='down',
          text="Fresh gullfish! ...Oh, you're a Tamer? Then keep those robed folk off my pier, would you?")
    m.npc(30, 20, 'st_sailor', 'sailor', move='wander', radius=2,
          text="Those Deepcall types have been chartering every boat in the harbour. Where are they going? The Riven, they say. Nobody sails to the Riven.")
    m.npc(10, 21, 'st_kid', 'kid', move='wander', radius=2,
          text="If you had a boat, you could reach the little island out in the bay! I saw something shiny there.")
    m.item(39, 31, 'pearl')
    m.item(3, 23, 'tonic', hidden=True)
    return m


@reg
def saltreach_haven():
    return haven('saltreach_haven', 'Saltreach')


@reg
def saltreach_trial():
    m = trial('saltreach_trial', 'Saltreach', 'Tide', 'brann', 'brann',
              [('st_adept_1', 'sailor', 4, 12, 'right'), ('st_adept_2', 'fisher', 9, 8, 'left'), ('st_adept_3', 'sailor', 4, 5, 'right')],
              "Ahoy! Captain Brann's crew are all Tide type. Nature and Static Morphs make short work of them. Try not to get soaked!")
    for (x, y) in [(1, 8), (12, 8), (1, 12), (12, 12)]:
        m.obj(f'furn {x} {y} crate')
    return m


@reg
def saltreach_house():
    m = house('saltreach_house', "Harbourmaster's House", wall='blue', variant=0)
    m.npc(3, 5, 'st_harbourmaster', 'gent', face='right', script='saltreach.harbourmaster')
    return m


@reg
def saltreach_net():
    m = house('saltreach_net', "Net-Mender's Cottage", wall='cream', floor='dark', variant=1)
    m.npc(7, 5, 'st_netmender', 'elder_b', face='left', script='saltreach.netmender')
    return m


@reg
def saltreach_lighthouse():
    m = M('saltreach_lighthouse', 10, 9, kind='interior', name='Saltreach Lighthouse', floor='stone', wall='white', music='house')
    m.rect(0, 0, 9, 1, 'W'); m.put(4, 1, 'w')
    m.put(4, 8, 'm')
    m.obj('furn 0 2 barrel'); m.obj('furn 1 2 crate'); m.obj('furn 8 2 bookshelf v=6'); m.obj('furn 6 4 table v=1')
    m.obj('furn 9 6 plant')
    m.npc(5, 4, 'lh_keeper', 'elder', face='down', script='saltreach.lighthouse')
    return m


@reg
def route3():
    m = M('route3', 52, 28, name='Route 3 · Gullcliff Road', kind='route', base='grass', music='route', battle='coast',
          west='saltreach 0')
    m.border(gaps=[('w', 12, 13)])
    # cliffs along the north
    for x in range(2, 50):
        top = 7 if (8 <= x <= 17 or 26 <= x <= 31) else 6
        m.rect(x, 2, x, top - 1, 'T')
        m.rect(x, top, x, top + 1, 'R')
    m.obj('cave 36 6 to=coldforge_mines:4,31')
    # sea along the south
    m.rect(0, 21, 51, 27, '~')
    m.rect(2, 18, 49, 20, 's')
    m.stamp(40, 22, [' ss ', 'ssss', ' ss '])
    m.put(28, 22, 'o'); m.put(29, 23, 'o')
    m.rect(0, 14, 1, 27, 'R')
    # the road
    m.rect(0, 12, 45, 13, ':')
    m.rect(36, 8, 37, 11, ':')
    # rockfall
    for (x, y) in [(46, 11), (47, 12), (46, 13), (48, 14), (47, 10), (48, 11), (46, 12), (47, 14), (48, 13), (47, 13), (46, 14), (48, 12)]:
        m.put(x, y, 'o')
    m.rect(46, 8, 49, 9, 'R'); m.grove(44, 16, 6, 2)
    # grass
    m.rect(4, 14, 13, 17, 'G'); m.rect(18, 9, 25, 11, 'G'); m.rect(22, 14, 33, 17, 'G'); m.rect(38, 14, 44, 17, 'G')
    m.hline(14, 14, 21, 'v')
    m.scatter([(3, 10), (20, 15), (35, 10), (41, 9), (16, 11)], 'F')
    m.rect(2, 8, 5, 9, 'P')
    m.put(12, 10, 'o'); m.put(33, 9, 'o')
    m.sign(3, 11, 'ROUTE 3 · GULLCLIFF ROAD|West: Saltreach   East: Gearhollow')
    m.sign(43, 11, 'ROCKFALL! Road closed.|Travellers to Gearhollow: go through the Coldforge Mines.')
    m.trainer(10, 11, 'r3_hiker', 'hiker', face='down', sight=2)
    m.trainer(24, 18, 'r3_sailor', 'sailor', face='up', sight=4)
    m.trainer(30, 14, 'r3_twin', 'twin', face='left', sight=4)
    m.trainer(41, 18, 'r3_fisher', 'fisher', face='left', sight=3)
    m.trainer(20, 10, 'r3_ace', 'ace', face='down', sight=2)
    # starter rescue: a Puddlet stranded in a rock pool, two Deepcall acolytes trying to take it
    m.npc(8, 20, 'r3_puddlet', 'mon:puddlet', face='up', script='rescue.puddlet',
          show='!var:starter=puddlet', hide='rescued_puddlet')
    m.trainer(7, 19, 'r3_poacher_a', 'acolyte', face='up', sight=3, show='!var:starter=puddlet', hide='rescued_puddlet')
    m.trainer(9, 19, 'r3_poacher_b', 'acolyte_b', face='up', sight=3, show='!var:starter=puddlet', hide='rescued_puddlet')
    m.item(41, 23, 'star_shard')
    m.item(4, 16, 'strong_tonic')
    m.item(48, 19, 'prime_capsule', hidden=True)
    m.item(22, 9, 'nerve_balm')
    return m


@reg
def coldforge_mines():
    m = M('coldforge_mines', 44, 34, name='Coldforge Mines', kind='cave', base='cave', music='cave', battle='cave',
          light='dark', enc_floor='1', escape='route3:37,8', fill='R')
    def c(x0, y0, x1, y1, ch='.'):
        m.rect(x0, y0, x1, y1, ch)
    # entrance hall (south-west)
    c(2, 26, 12, 31); c(3, 32, 5, 33)
    m.obj('warp 4 33 to=route3:37,8 face=down')
    m.obj('warp 5 33 to=route3:37,8 face=down')
    c(6, 18, 8, 25)                                  # shaft north
    c(2, 12, 16, 17)                                 # first gallery
    c(14, 18, 16, 23); c(14, 22, 26, 25)            # lower tunnel east
    c(24, 14, 26, 21); c(20, 8, 32, 13)            # upper gallery
    c(10, 3, 22, 7); c(10, 8, 12, 11)              # north workings
    c(30, 14, 34, 27); c(28, 26, 40, 31)           # east descent
    c(36, 16, 41, 25)                                 # Vesk's cavern
    c(38, 4, 41, 15); c(34, 2, 41, 5)
    m.obj('warp 40 1 to=gearhollow:3,14 face=down')
    m.obj('warp 41 1 to=gearhollow:3,14 face=down')
    c(40, 0, 41, 1)
    # water seep
    m.rect(3, 13, 6, 15, '~')
    # props
    for (x, y, p) in [(9, 27, 'cart'), (11, 26, 'crate'), (12, 30, 'barrel'), (15, 12, 'lantern_post'), (2, 26, 'lantern_post'),
                      (21, 8, 'crate'), (31, 9, 'crystal'), (20, 12, 'crystal'), (11, 4, 'cart'), (29, 30, 'lantern_post'),
                      (40, 16, 'crystal'), (36, 25, 'crystal'), (34, 2, 'lantern_post'), (22, 4, 'barrel'), (24, 25, 'crate')]:
        m.obj(f'prop {x} {y} {p}')
    m.sign(8, 26, 'COLDFORGE MINES|Ore cart line — keep clear of the rails.')
    m.trainer(8, 14, 'cf_miner_1', 'miner', face='right', sight=4)
    m.trainer(24, 18, 'cf_miner_2', 'miner', face='down', sight=4)
    m.trainer(15, 5, 'cf_engineer', 'engineer', face='right', sight=4)
    m.trainer(32, 20, 'cf_acolyte_1', 'acolyte', face='down', sight=4, hide='vesk1_done')
    m.trainer(35, 29, 'cf_acolyte_2', 'acolyte_b', face='left', sight=4, hide='vesk1_done')
    m.npc(39, 18, 'cf_vesk', 'vesk', face='down', script='mines.vesk', hide='vesk1_done')
    m.npc(38, 23, 'cf_digger', 'acolyte', face='up', hide='vesk1_done', text='The scale-iron sings when you strike it... can you hear it? The Mother is waking.')
    m.trigger(36, 21, 'mines.vesk', w=6, once='vesk1_seen')
    m.npc(4, 28, 'cf_foreman', 'miner', face='right', script='mines.foreman')
    # starter rescue: a freezing Cindlet by the icy seep (needs an ember from Gearhollow's forge)
    m.npc(2, 14, 'cf_cindlet', 'mon:cindlet', face='right', script='rescue.cindlet',
          show='!var:starter=cindlet', hide='rescued_cindlet')
    m.item(21, 4, 'td03')
    m.item(26, 12, 'homing_thread')
    m.item(2, 17, 'prime_capsule')
    m.item(39, 30, 'strong_tonic')
    m.item(12, 15, 'star_shard', hidden=True)
    m.item(41, 6, 'rekindle_seed')
    return m


@reg
def gearhollow():
    m = M('gearhollow', 46, 36, name='Gearhollow', kind='town', base='grass', music='gearhollow', battle='town',
          north='route4 -4', fly='12,14')
    m.border(t=2, ch='Y', gaps=[('n', 20, 21)])
    m.rect(2, 2, 43, 3, 'R')
    m.rect(2, 4, 3, 11, 'R'); m.rect(2, 17, 3, 20, 'R')
    m.obj('cave 2 12 to=coldforge_mines:40,2 face=down')
    # cobbled streets
    m.rect(3, 15, 42, 16, ';')
    m.rect(20, 0, 21, 14, ';')
    m.rect(20, 17, 21, 28, ';')
    m.rect(12, 14, 12, 14, ';')
    m.rect(34, 10, 35, 14, ';')
    m.rect(8, 29, 36, 30, ';')
    m.rect(7, 27, 8, 28, ';'); m.rect(30, 27, 31, 28, ';')
    m.obj('building 9 10 haven w=6 h=4 roof=red wall=white to=gearhollow_haven')
    m.obj('building 29 4 hall w=11 h=6 roof=gray wall=brick label=IRONWORKS door=5 to=gearhollow_ironworks cond=has:forge_pass locked="The Ironworks gate is shut tight.|AUTHORISED STAFF ONLY. FORGE PASS REQUIRED."')
    m.obj('building 24 19 arena w=7 h=5 roof=gold wall=brick emblem=bolt type=Static label="SPARK TRIAL" to=gearhollow_trial cond=ironworks_done locked="A note is taped to the door:|AT THE IRONWORKS. BACK SOON. PROBABLY. — ISKRA"')
    m.obj('building 5 23 house w=5 h=4 roof=slate wall=brick variant=1 to=gearhollow_house')
    m.obj('building 12 19 house w=4 h=4 roof=brown wall=stone variant=0 to=gearhollow_store')
    m.rect(24, 24, 30, 24, ';'); m.rect(27, 25, 27, 28, ';')
    m.rect(14, 23, 14, 28, ';')
    m.obj('prop 16 6 stone script=gearhollow.seal')
    m.rect(14, 5, 18, 5, 'w'); m.put(14, 6, 'w'); m.put(18, 6, 'w')
    for (x, y, p) in [(38, 18, 'cart'), (40, 21, 'crate'), (41, 21, 'crate'), (37, 22, 'barrel'), (6, 18, 'barrel'), (24, 12, 'crate')]:
        m.obj(f'prop {x} {y} {p}')
    for (x, y) in [(8, 14), (18, 14), (26, 14), (40, 14), (19, 27), (33, 28)]:
        m.put(x, y, 'L')
    m.rect(38, 30, 43, 33, 'Y'); m.rect(2, 30, 5, 33, 'Y'); m.rect(4, 4, 9, 7, 'Y')
    m.scatter([(6, 20), (16, 25), (35, 25), (22, 32), (11, 32)], 'F')
    m.sign(22, 12, 'GEARHOLLOW|Where the Reach keeps its clockwork.')
    m.sign(23, 23, 'SPARK TRIAL · Warden Iskra|"If it isn\'t broken, improve it anyway."')
    m.npc(21, 3, 'gh_gate', 'engineer', face='down', script='gearhollow.northgate', hide='sigil_spark')
    m.trigger(20, 4, 'gearhollow.northgate', w=2, cond='!sigil_spark')
    m.npc(34, 11, 'gh_worker', 'engineer', face='down', script='gearhollow.worker')
    m.npc(38, 12, 'gh_smith', 'miner', face='down', script='gearhollow.smith')
    m.npc(16, 16, 'gh_man', 'man', move='wander', radius=2,
          text="Warden Iskra built the Haven's healing machine, the Ironworks crane AND my kettle. My kettle talks now. I wish it didn't.")
    m.npc(35, 20, 'gh_kid', 'kid_b', move='wander', radius=2,
          text="Static Morphs hate the ground! Stone and... um... ground-ish Morphs. Stone ones. That's what my big sister says.")
    m.npc(27, 30, 'gh_wren', 'wren', face='up', show='never')
    m.trigger(24, 24, 'gearhollow.wren', w=7, h=2, once='wren3_done', cond='sigil_spark')
    m.item(36, 32, 'rekindle_seed', hidden=True)
    m.item(24, 33, 'capsule', 3)
    return m


@reg
def gearhollow_haven():
    return haven('gearhollow_haven', 'Gearhollow')


@reg
def gearhollow_trial():
    m = trial('gearhollow_trial', 'Gearhollow', 'Static', 'iskra', 'iskra',
              [('gh_adept_1', 'engineer', 4, 12, 'right'), ('gh_adept_2', 'scholar', 9, 8, 'left'), ('gh_adept_3', 'engineer', 4, 5, 'right')],
              "Hey hey! Iskra's Morphs are Static type — but half of them are armoured in Iron too. Stone Morphs shrug off lightning. Bring one!")
    for (x, y) in [(1, 8), (12, 8), (1, 12), (12, 12), (0, 4), (13, 4)]:
        m.obj(f'furn {x} {y} machine')
    return m


@reg
def gearhollow_ironworks():
    m = M('gearhollow_ironworks', 20, 14, kind='interior', name='Gearhollow Ironworks', floor='stone', wall='stone', music='deepcall')
    m.rect(0, 0, 19, 1, 'W'); m.put(4, 1, 'w'); m.put(15, 1, 'w')
    m.put(9, 13, 'm'); m.put(10, 13, 'm')
    for x in (0, 1, 2, 17, 18, 19):
        m.obj(f'furn {x} 2 machine')
    for (x, y) in [(5, 5), (14, 5), (5, 9), (14, 9)]:
        m.obj(f'furn {x} {y} pillar')
    m.obj('furn 8 2 machine'); m.obj('furn 11 2 machine')
    m.obj('furn 0 8 crate'); m.obj('furn 0 9 crate'); m.obj('furn 19 8 barrel'); m.obj('furn 19 9 barrel')
    m.obj('furn 1 12 crate'); m.obj('furn 18 12 crate')
    m.trainer(8, 10, 'iw_acolyte_1', 'acolyte', face='down', sight=2, hide='ironworks_done')
    m.trainer(12, 7, 'iw_acolyte_2', 'acolyte_b', face='left', sight=4, hide='ironworks_done')
    m.trainer(7, 5, 'iw_acolyte_3', 'acolyte', face='right', sight=4, hide='ironworks_done')
    m.npc(10, 3, 'iw_iskra', 'iskra', face='down', script='ironworks.iskra', hide='ironworks_done')
    m.npc(9, 3, 'iw_boss', 'acolyte', face='right', hide='ironworks_done', text='...')
    m.npc(16, 11, 'iw_worker', 'engineer', face='left', script='ironworks.worker')
    m.item(17, 4, 'td13')
    return m


@reg
def gearhollow_house():
    m = house('gearhollow_house', "Tinker's House", wall='stone', floor='tile', variant=0)
    m.npc(7, 5, 'gh_tinker', 'engineer', face='left', script='gearhollow.tinker')
    return m


@reg
def gearhollow_store():
    m = M('gearhollow_store', 12, 9, kind='interior', name='Gearhollow Disc Shop', floor='tile', wall='white', music='house')
    m.rect(0, 0, 11, 1, 'W'); m.put(3, 1, 'w'); m.put(8, 1, 'w'); m.put(5, 8, 'm')
    m.rect(2, 4, 8, 4, '=')
    m.obj('furn 3 2 shelf v=2'); m.obj('furn 6 2 shelf v=3'); m.obj('furn 11 2 plant'); m.obj('furn 0 2 bookshelf v=2')
    m.obj('furn 10 6 table v=1'); m.obj('furn 0 7 plant')
    m.npc(5, 3, 'gh_discclerk', 'clerk', face='down', script='gearhollow.discshop', noturn='1')
    return m


# ═══════════════════════════════════════════════════════════════════════════
# ACT III — FOG AND GLASS
# ═══════════════════════════════════════════════════════════════════════════
@reg
def route4():
    m = M('route4', 36, 54, name='Route 4 · Moorwind Way', kind='route', base='moor', music='moor', battle='moor',
          weather='fog', south='gearhollow 4', north='hollowmere 4')
    m.border(ch='Y', gaps=[('n', 16, 17), ('s', 16, 17)])
    m.path([(16, 53), (16, 44), (24, 44), (24, 30), (10, 30), (10, 16), (16, 16), (16, 0)], ':')
    # stone circle
    for (x, y) in [(24, 18), (28, 19), (30, 22), (28, 25), (24, 26), (20, 25), (18, 22), (20, 19)]:
        m.obj(f'prop {x} {y} stone')
    m.obj('prop 24 22 stone script=route4.circle')
    m.rect(22, 20, 26, 24, ',')
    # grass
    m.rect(4, 46, 13, 51, 'G'); m.rect(20, 46, 31, 50, 'G'); m.rect(12, 32, 21, 37, 'G')
    m.rect(3, 18, 8, 27, 'G'); m.rect(20, 4, 31, 10, 'G'); m.rect(4, 4, 11, 9, 'G')
    m.hline(40, 2, 21, 'v')
    m.stamp(26, 34, ['  ss  ', ' s~~s ', 's~~~~s', ' s~~s ', '  ss  '])
    for (x, y) in [(3, 12), (13, 12), (30, 14), (6, 36), (27, 40), (32, 30), (4, 42), (30, 5)]:
        m.put(x, y, 'o' if (x + y) % 3 else 'b')
    m.grove(26, 12, 4, 4, 'Y'); m.grove(12, 20, 4, 6, 'Y'); m.grove(2, 30, 6, 4, 'Y')
    m.scatter([(14, 14), (22, 13), (7, 40), (19, 42), (30, 44)], 'F')
    m.put(18, 12, 'o'); m.put(29, 28, 'o'); m.put(5, 14, 'o')
    m.sign(18, 51, 'ROUTE 4 · MOORWIND WAY|South: Gearhollow   North: Hollowmere')
    m.sign(18, 2, 'HOLLOWMERE|Mind the fog.')
    m.trainer(14, 34, 'r4_mystic', 'mystic', face='left', sight=3)
    m.trainer(26, 38, 'r4_ranger', 'ranger', face='left', sight=2)
    m.trainer(12, 22, 'r4_scholar', 'scholar', face='left', sight=2)
    m.trainer(20, 7, 'r4_hiker', 'hiker', face='left', sight=3)
    m.trainer(6, 28, 'r4_lady', 'lady', face='right', sight=4)
    m.item(24, 21, 'td10')
    m.item(5, 5, 'dusk_capsule', 2)
    m.item(31, 48, 'strong_tonic')
    m.item(28, 36, 'star_shard', hidden=True)
    m.item(3, 20, 'clarity_leaf')
    return m


@reg
def hollowmere():
    m = M('hollowmere', 44, 34, name='Hollowmere', kind='town', base='moor', music='hollowmere', battle='moor',
          weather='fog', south='route4 -4', west='route5 0', fly='25,12')
    m.border(ch='Y', gaps=[('s', 20, 21)])
    # the lake
    m.rect(0, 4, 13, 29, '~')
    m.rect(0, 4, 1, 11, 'Y'); m.rect(0, 20, 1, 29, 'Y')
    for y in range(4, 30):
        m.put(14, y, 's')
    m.rect(2, 3, 13, 3, 's'); m.rect(2, 30, 14, 30, 's')
    m.rect(8, 16, 14, 17, 'k')
    # streets
    m.path([(20, 33), (20, 14)])
    m.rect(15, 14, 41, 15, ':')
    m.rect(15, 16, 15, 17, ':')
    m.rect(16, 23, 40, 24, ':')
    m.rect(25, 12, 25, 13, ':'); m.rect(33, 13, 33, 13, ':')
    m.rect(28, 22, 28, 22, ':'); m.rect(36, 22, 36, 22, ':')
    m.obj('building 22 8 haven w=6 h=4 roof=red wall=white to=hollowmere_haven')
    m.obj('building 30 8 arena w=7 h=5 roof=purple wall=dark emblem=moon type=Umbra label="VEIL TRIAL" to=hollowmere_trial')
    m.obj('building 26 18 house w=5 h=4 roof=plum wall=stone variant=2 to=hollowmere_archive')
    m.obj('building 34 18 house w=4 h=4 roof=slate wall=timber variant=0 to=hollowmere_house')
    for (x, y) in [(16, 5), (19, 4), (18, 8)]:
        m.obj(f'prop {x} {y} stone')
    m.obj('prop 17 7 stone script=hollowmere.seal')
    for (x, y) in [(38, 5), (40, 9), (17, 26), (38, 28), (24, 28), (30, 30)]:
        m.put(x, y, 'o')
    m.rect(2, 2, 3, 3, 'Y')
    m.scatter([(22, 17), (19, 20), (31, 27), (40, 26), (35, 12)], 'F')
    for (x, y) in [(19, 13), (29, 13), (40, 13), (24, 22), (33, 25)]:
        m.put(x, y, 'L')
    m.sign(22, 30, 'HOLLOWMERE|The fog lifts for those who listen.')
    m.sign(37, 13, 'VEIL TRIAL · Warden Morrow|"Every story is true somewhere."')
    m.sign(15, 18, 'GLASSLAKE|Boats launch from the pier.')
    m.npc(39, 20, 'hm_elder', 'elder_b', face='left',
          text="The fog comes in off Glasslake every evening. My grandmother said it was Tiamat breathing in her sleep.")
    m.npc(18, 28, 'hm_fisher', 'fisher', face='left', script='hollowmere.fisher')
    m.npc(30, 16, 'hm_kid', 'kid', move='wander', radius=2,
          text="Umbra Morphs come out at night! Mum says if I'm good I can stay up late and watch the Nyxens glow.")
    m.npc(11, 16, 'hm_wren', 'wren_dark', face='right', show='never')
    m.npc(10, 17, 'hm_maren', 'maren', face='right', show='never')
    m.trigger(14, 4, 'hollowmere.shore', h=26, once='maren1_done', cond='sigil_veil')
    m.trigger(2, 30, 'hollowmere.shore', w=12, once='maren1_done', cond='sigil_veil')
    m.trigger(1, 12, 'hollowmere.lakegate', h=8, cond='!maren1_done')
    m.item(40, 31, 'rekindle_seed', hidden=True)
    m.item(3, 31, 'dusk_capsule')
    return m


@reg
def hollowmere_haven():
    return haven('hollowmere_haven', 'Hollowmere')


@reg
def hollowmere_trial():
    m = trial('hollowmere_trial', 'Hollowmere', 'Umbra', 'morrow', 'morrow',
              [('hm_adept_1', 'mystic', 4, 12, 'right'), ('hm_adept_2', 'scholar', 9, 8, 'left'), ('hm_adept_3', 'mystic', 4, 5, 'right')],
              "...Can you see me? Warden Morrow keeps the hall dark. Umbra Morphs fear Brawl fists and bright Swarm wings.",
              light='dark')
    for (x, y) in [(1, 8), (12, 8), (1, 12), (12, 12)]:
        m.obj(f'furn {x} {y} pot')
    return m


@reg
def hollowmere_archive():
    m = house('hollowmere_archive', 'The Hollowmere Archive', wall='dark', floor='dark', variant=0)
    for x in (2, 3, 4):
        m.obj(f'furn {x} 2 bookshelf v={x + 3}')
    m.npc(7, 5, 'hm_archivist', 'scholar', face='left', script='hollowmere.archivist')
    m.obj('furn 9 5 globe')
    return m


@reg
def hollowmere_house():
    m = house('hollowmere_house', 'Lakeside House', wall='green', variant=1)
    m.npc(6, 4, 'hm_ferrywoman', 'woman', face='down', script='hollowmere.ferry')
    return m


@reg
def route5():
    m = M('route5', 50, 34, name='Route 5 · Glasslake Crossing', kind='route', base='grass', music='lake', battle='water',
          weather='fog', east='hollowmere 0', north='frostspire 8')
    m.rect(0, 0, 49, 33, '~')
    # north shore (snow creeping down)
    m.rect(0, 0, 49, 9, 'n')
    m.rect(0, 0, 49, 1, 'N'); m.rect(0, 0, 1, 9, 'N'); m.rect(48, 0, 49, 9, 'N')
    m.rect(10, 0, 11, 1, ':')
    m.rect(2, 8, 47, 9, 's')
    m.rect(10, 2, 11, 9, ':')
    m.grove(2, 2, 6, 4, 'N'); m.grove(14, 2, 8, 4, 'N'); m.grove(32, 2, 8, 2, 'N')
    m.rect(22, 3, 31, 6, 'G'); m.rect(40, 3, 45, 6, 'G')
    m.put(8, 6, 'o'); m.put(36, 6, 'o')
    # border of the lake (south shore trees)
    m.rect(0, 30, 49, 33, 'T')
    m.rect(0, 28, 49, 29, 's')
    # islands
    m.stamp(14, 13, [' ssssss ', 'sGGGGGGs', 'sGGGGGGs', 'sG.TTGGs', 'ss.TTsss', ' ssssss '])
    m.stamp(30, 19, [' ssssss ', 'ssGGGGss', 'sGGGGG.s', ' ssssss '])
    m.stamp(38, 10, [' sss ', 'ss.ss', ' sss '])
    m.stamp(4, 20, [' ssss ', 'ss..ss', ' ssss '])
    m.rect(48, 10, 49, 11, 'o'); m.rect(48, 20, 49, 29, 'o')
    m.sign(12, 7, 'ROUTE 5 · GLASSLAKE CROSSING|North: Frostspire   East: Hollowmere')
    m.trainer(16, 16, 'r5_fisher', 'fisher', face='down', sight=3)
    m.trainer(36, 21, 'r5_sailor', 'sailor', face='left', sight=4)
    m.trainer(24, 8, 'r5_skier', 'skier', face='down', sight=3)
    m.trainer(40, 11, 'r5_mystic', 'mystic', face='left', sight=2)
    m.trainer(6, 21, 'r5_ace', 'ace_b', face='right', sight=3)
    m.item(15, 17, 'prime_capsule', 3)
    m.item(40, 12, 'pearl')
    m.item(5, 21, 'full_tonic')
    m.item(44, 4, 'swift_capsule', 2)
    m.item(34, 20, 'star_shard', hidden=True)
    return m


# ═══════════════════════════════════════════════════════════════════════════
# ACT IV — THE RIVEN
# ═══════════════════════════════════════════════════════════════════════════
@reg
def frostspire():
    m = M('frostspire', 40, 34, name='Frostspire', kind='town', base='snow', music='frostspire', battle='snow',
          weather='snow', south='route5 -8', east='route6 0', fly='11,16')
    m.border(ch='N', gaps=[('s', 18, 19), ('e', 16, 17)])
    m.path([(18, 33), (18, 16)])
    m.rect(3, 16, 39, 17, ':')
    m.rect(23, 11, 24, 15, ':')
    m.rect(4, 25, 34, 26, ':')
    m.rect(10, 24, 10, 24, ':'); m.rect(30, 24, 30, 24, ':')
    m.obj('building 8 12 haven w=6 h=4 roof=red wall=white snow=1 to=frostspire_haven')
    m.obj('building 20 6 arena w=7 h=5 roof=white wall=stone snow=1 emblem=flake type=Frost label="RIME TRIAL" to=frostspire_trial')
    m.obj('building 8 21 house w=5 h=4 roof=navy wall=log snow=1 variant=1 to=frostspire_lodge')
    m.obj('building 28 21 house w=5 h=4 roof=teal wall=stone snow=1 variant=0 to=frostspire_house')
    m.obj('prop 32 11 stone script=frostspire.seal')
    m.rect(29, 9, 35, 9, 'w'); m.rect(29, 10, 29, 12, 'w'); m.rect(35, 10, 35, 12, 'w')
    m.stamp(3, 3, [' ssss ', 's~~~~s', 's~~~~s', ' ssss '])
    for (x, y) in [(14, 20), (24, 20), (36, 28)]:
        m.obj(f'prop {x} {y} snowman')
    for (x, y) in [(15, 15), (27, 15), (35, 15), (16, 24), (24, 27)]:
        m.put(x, y, 'L')
    m.grove(34, 2, 4, 6, 'N'); m.grove(10, 4, 6, 2, 'N'); m.grove(2, 28, 12, 2, 'N'); m.grove(22, 28, 12, 2, 'N')
    m.sign(16, 30, 'FROSTSPIRE|The last warm fire before the Riven.')
    m.sign(26, 11, 'RIME TRIAL · Warden Hale|"Every summit starts at the bottom."')
    m.npc(37, 15, 'fs_guide', 'hiker', face='down', script='frostspire.eastguide', hide='sigil_rime')
    m.trigger(37, 16, 'frostspire.eastgate', h=2, cond='!sigil_rime')
    m.npc(20, 22, 'fs_skier', 'skier', move='wander', radius=2,
          text="Frost Morphs can't stand fire, and Brawl fists crack their ice. Stone? Stone's fine. Stone's always fine.")
    m.npc(6, 18, 'fs_elder', 'elder', face='right',
          text="From the top of the Spire in Riftgate you can see all six Seals at once. Or so the Wardens say. Nobody else is allowed up.")
    m.item(37, 30, 'rekindle_seed')
    m.item(2, 10, 'thaw_draught', 2, hidden=True)
    return m


@reg
def frostspire_haven():
    return haven('frostspire_haven', 'Frostspire')


@reg
def frostspire_trial():
    m = trial('frostspire_trial', 'Frostspire', 'Frost', 'hale', 'hale',
              [('fs_adept_1', 'skier', 4, 12, 'right'), ('fs_adept_2', 'hiker', 9, 8, 'left'), ('fs_adept_3', 'skier', 4, 5, 'right')],
              "Brr! Warden Hale's Frost Morphs will freeze you solid. Ember, Brawl, Stone and Iron all do the job. Stay warm!")
    return m


@reg
def frostspire_lodge():
    m = house('frostspire_lodge', "Climbers' Lodge", wall='wood', floor='dark', variant=1)
    m.npc(3, 5, 'fs_climber', 'hiker', face='right', script='frostspire.climber')
    m.npc(8, 6, 'fs_cook', 'woman_b', face='left', text='Soup? Soup. Everyone who comes down off the mountain gets soup. That\'s the rule.')
    return m


@reg
def frostspire_house():
    m = house('frostspire_house', 'Snowbound House', wall='ice', floor='wood', variant=2)
    m.npc(6, 5, 'fs_girl', 'lass', face='down', script='frostspire.girl')
    return m


@reg
def route6():
    m = M('route6', 54, 30, name='Route 6 · Rimepass', kind='route', base='snow', music='route_b', battle='snow',
          weather='snow', west='frostspire 0', east='riftgate 4')
    m.border(ch='N', gaps=[('w', 16, 17), ('e', 14, 15)])
    # east half: ash and dead trees
    m.rect(28, 0, 53, 29, 'a')
    m.rect(28, 0, 53, 1, 'X'); m.rect(28, 28, 53, 29, 'X'); m.rect(52, 0, 53, 29, 'X')
    m.rect(52, 14, 53, 15, ':')
    m.path([(0, 16), (12, 16), (12, 8), (24, 8), (24, 20), (38, 20), (38, 14), (53, 14)], ':')
    # cliffs & ledges stepping down to the east
    m.rect(2, 2, 9, 5, 'R'); m.rect(30, 2, 45, 5, 'R'); m.rect(30, 24, 49, 25, 'R')
    m.vline(20, 10, 18, '>'); m.vline(34, 8, 18, '>')
    m.rect(14, 22, 21, 26, 'G'); m.rect(26, 10, 31, 16, 'G'); m.rect(4, 20, 9, 25, 'G'); m.rect(40, 16, 47, 21, 'G')
    m.grove(14, 12, 4, 4, 'N'); m.grove(2, 8, 6, 4, 'N')
    for (x, y) in [(36, 10), (44, 8), (48, 22), (30, 20), (41, 25)]:
        m.put(x, y, 'o')
    for (x, y) in [(39, 7), (47, 11), (32, 22)]:
        m.obj(f'prop {x} {y} rift_rock')
    m.sign(3, 15, 'ROUTE 6 · RIMEPASS|West: Frostspire   East: Riftgate')
    m.sign(49, 13, 'RIFTGATE|City on the edge of the world.')
    m.trainer(14, 9, 'r6_skier_1', 'skier', face='down', sight=3)
    m.trainer(22, 18, 'r6_skier_2', 'skier', face='left', sight=2)
    m.trainer(28, 21, 'r6_hiker', 'hiker', face='right', sight=4)
    m.trainer(40, 17, 'r6_acolyte', 'acolyte', face='up', sight=3, leave='1')
    m.trainer(46, 13, 'r6_ace', 'ace', face='left', sight=3)
    m.item(3, 6, 'full_tonic')
    m.item(47, 20, 'apex_capsule')
    m.item(15, 25, 'strong_incense', hidden=True)
    m.item(31, 12, 'rekindle_seed')
    return m


@reg
def riftgate():
    m = M('riftgate', 48, 38, name='Riftgate', kind='town', base='ash', music='riftgate', battle='rift',
          west='route6 -4', fly='11,10')
    m.border(ch='X', gaps=[('w', 18, 19)])
    # the Riven: a sheer drop to the sea
    m.rect(38, 0, 47, 37, '~')
    m.rect(36, 0, 37, 37, 'R')
    m.rect(0, 18, 35, 19, ';')
    m.rect(16, 11, 27, 17, ';')
    m.rect(11, 10, 11, 17, ';')
    m.rect(23, 9, 23, 10, ';')
    m.rect(32, 10, 33, 17, ';')
    m.rect(4, 30, 33, 31, ';')
    m.rect(18, 20, 19, 29, ';')
    m.rect(10, 28, 10, 29, ';')
    m.rect(29, 29, 29, 29, ';')
    m.obj('building 8 6 haven w=6 h=4 roof=red wall=white to=riftgate_haven')
    m.obj('building 20 4 arena w=7 h=5 roof=red wall=stone emblem=claw type=Drake label="WYRM TRIAL" to=riftgate_trial')
    m.obj('building 30 3 hall w=6 h=7 roof=black wall=stone label=SPIRE door=3 to=spire_crown cond=cradle_done locked="The Spire door is barred. Only Wardens may climb to the Crown."')
    m.obj('building 7 24 house w=5 h=4 roof=slate wall=dark variant=2 to=riftgate_house')
    m.obj('building 25 24 chapel w=8 h=5 roof=black wall=dark label=CHAPEL door=4 to=sunken_chapel cond=has:rift_key locked="The chapel doors are locked with a heavy iron lock shaped like a wave."')
    m.obj('prop 21 14 stone script=riftgate.seal')
    for (x, y) in [(18, 12), (25, 12), (18, 16), (25, 16)]:
        m.obj(f'prop {x} {y} crystal')
    for (x, y) in [(14, 22), (4, 12), (34, 21), (22, 34), (3, 34), (15, 3)]:
        m.obj(f'prop {x} {y} rift_rock')
    for (x, y) in [(15, 17), (28, 17), (7, 17), (21, 29), (33, 29)]:
        m.put(x, y, 'L')
    m.sign(5, 17, 'RIFTGATE|City on the lip of the Riven.')
    m.sign(35, 18, 'THE RIVEN|Do not climb the railings.')
    m.sign(26, 9, 'WYRM TRIAL · Warden Seren|"Stand at the edge. Do not flinch."')
    m.npc(33, 11, 'rg_spireguard', 'guard', face='down', script='riftgate.spireguard', hide='cradle_done')
    m.npc(30, 30, 'rg_chapelguard', 'guard', face='up', script='riftgate.chapelguard', hide='oriel_reveal')
    m.npc(27, 20, 'rg_man', 'man', move='wander', radius=2,
          text="On a still night you can hear the sea at the bottom of the Riven, breathing in and out. My kids think it's snoring.")
    m.npc(12, 21, 'rg_woman', 'woman_b', move='wander', radius=2,
          text="The Deepcall used to hold services at the old chapel. Then they started locking the doors.")
    m.npc(21, 10, 'rg_oriel', 'oriel', face='down', show='never')
    m.npc(20, 11, 'rg_acolyte_a', 'acolyte', face='down', show='never')
    m.npc(22, 11, 'rg_acolyte_b', 'acolyte_b', face='down', show='never')
    m.npc(20, 22, 'rg_wren', 'wren_dark', face='up', show='never')
    m.npc(24, 13, 'rg_seren', 'seren', face='down', show='never')
    m.trigger(19, 9, 'riftgate.oriel', w=9, h=2, once='oriel_reveal', cond='sigil_wyrm')
    m.item(3, 3, 'full_tonic', hidden=True)
    m.item(34, 35, 'apex_capsule')
    return m


@reg
def riftgate_haven():
    return haven('riftgate_haven', 'Riftgate')


@reg
def riftgate_trial():
    m = trial('riftgate_trial', 'Riftgate', 'Drake', 'seren', 'seren',
              [('rg_adept_1', 'ace', 4, 12, 'right'), ('rg_adept_2', 'ace_b', 9, 8, 'left'), ('rg_adept_3', 'guard', 4, 5, 'right')],
              "This is it — the Wyrm Trial. Drake Morphs shrug off almost everything. Frost is your best weapon. Drake beats Drake, too, if you dare.")
    return m


@reg
def riftgate_house():
    m = house('riftgate_house', "Seren's Old House", wall='stone', floor='dark', variant=2)
    m.npc(7, 5, 'rg_oldwarden', 'elder_b', face='left', script='riftgate.oldwarden')
    return m


@reg
def sunken_chapel():
    m = M('sunken_chapel', 22, 26, kind='interior', name='Sunken Chapel', floor='chapel', wall='dark', music='deepcall',
          light='dark', battle='chapel')
    m.rect(0, 0, 21, 1, 'W')
    m.rect(10, 4, 11, 25, '_')
    m.put(10, 25, 'm'); m.put(11, 25, 'm')
    m.obj('furn 9 2 altar')
    m.obj('furn 17 3 stairs_down')
    m.obj('warp 17 3 to=abyssal_rift:20,3 face=down cond=wren_freed locked="A cold draught rises from the stairs. The Deepcall are waiting below — free Wren first."')
    for y in (6, 10, 14, 18, 22):
        m.obj(f'furn 6 {y} pillar'); m.obj(f'furn 15 {y} pillar')
    for y in (8, 12, 16, 20):
        for x in (2, 17):
            m.obj(f'furn {x} {y} table v=2')
    m.obj('furn 0 2 banner'); m.obj('furn 21 2 banner'); m.obj('furn 4 2 crystal'); m.obj('furn 13 2 crystal')
    m.rect(0, 12, 1, 12, '#')
    m.trainer(9, 20, 'sc_acolyte_1', 'acolyte', face='right', sight=3)
    m.trainer(12, 17, 'sc_acolyte_2', 'acolyte_b', face='left', sight=3)
    m.trainer(4, 14, 'sc_acolyte_3', 'acolyte', face='down', sight=4)
    m.trainer(18, 10, 'sc_acolyte_4', 'acolyte_b', face='left', sight=4)
    m.npc(10, 12, 'sc_vesk', 'vesk', face='down', script='chapel.vesk', trainer='vesk2', sight=4, hide='vesk2_done')
    m.npc(11, 7, 'sc_maren', 'maren', face='down', script='chapel.maren', trainer='maren2', sight=3, hide='maren2_done')
    m.npc(10, 4, 'sc_wren', 'wren_dark', face='down', script='chapel.wren', hide='wren_freed')
    m.item(1, 23, 'full_tonic')
    m.item(20, 23, 'rekindle_seed')
    return m


@reg
def abyssal_rift():
    m = M('abyssal_rift', 40, 46, name='The Abyssal Rift', kind='cave', base='cave', music='rift', battle='rift',
          light='dark', enc_floor='1', escape='riftgate:29,29', fill='R')
    def c(x0, y0, x1, y1, ch='.'):
        m.rect(x0, y0, x1, y1, ch)
    c(18, 1, 22, 6)
    m.obj('warp 20 1 to=sunken_chapel:17,4 face=down')
    c(8, 6, 32, 11)
    m.hline(12, 10, 30, 'v')
    c(8, 12, 12, 21); c(28, 12, 32, 21)
    c(4, 16, 36, 19); m.rect(14, 16, 26, 19, '~')
    c(4, 20, 8, 31); c(32, 20, 36, 31)
    c(8, 26, 32, 31); m.hline(27, 12, 28, 'v')
    c(14, 32, 26, 36); m.rect(17, 33, 23, 35, '~')
    c(10, 37, 30, 41); c(18, 42, 21, 45)
    m.obj('warp 19 45 to=cradle:9,13 face=up')
    m.obj('warp 20 45 to=cradle:10,13 face=up')
    for (x, y) in [(9, 7), (31, 7), (5, 17), (35, 17), (13, 29), (27, 29), (11, 38), (29, 38), (16, 32), (24, 32), (6, 30), (34, 30)]:
        m.obj(f'prop {x} {y} crystal')
    m.trainer(20, 9, 'ar_acolyte_1', 'acolyte', face='down', sight=2)
    m.trainer(6, 24, 'ar_acolyte_2', 'acolyte_b', face='down', sight=4)
    m.trainer(34, 24, 'ar_acolyte_3', 'acolyte', face='down', sight=4)
    m.trainer(20, 38, 'ar_ace', 'ace_b', face='down', sight=3)
    m.item(9, 20, 'full_tonic')
    m.item(31, 13, 'apex_capsule', 2)
    m.item(5, 31, 'panacea')
    m.item(35, 31, 'bloom_seed')
    m.item(20, 8, 'growth_fruit', hidden=True)
    return m


@reg
def cradle():
    m = M('cradle', 20, 16, kind='interior', name="Tiamat's Cradle", floor='chapel', wall='dark', music='cradle',
          light='dark', battle='rift')
    m.rect(0, 0, 19, 1, 'W')
    m.rect(0, 2, 1, 15, '#'); m.rect(18, 2, 19, 15, '#')
    m.rect(9, 5, 10, 15, '_')
    m.obj('furn 8 2 altar')
    for (x, y) in [(3, 4), (16, 4), (3, 9), (16, 9), (5, 13), (14, 13)]:
        m.obj(f'furn {x} {y} crystal')
    m.obj('warp 9 15 to=abyssal_rift:19,44 face=down')
    m.obj('warp 10 15 to=abyssal_rift:20,44 face=down')
    m.npc(9, 6, 'cr_oriel', 'oriel', face='down', script='cradle.oriel', hide='oriel_beaten')
    m.trigger(2, 10, 'cradle.oriel', w=16, once='cradle_scene1')
    m.obj('sign 9 3 script=cradle.tiamat w=2')
    return m


@reg
def spire_crown():
    m = M('spire_crown', 18, 14, kind='interior', name="The Warden's Crown", floor='arena', wall='stone', music='crown')
    m.rect(0, 0, 17, 1, 'W')
    for x in (3, 6, 11, 14):
        m.put(x, 1, 'w')
    m.rect(8, 3, 9, 13, '_')
    m.put(8, 13, 'm'); m.put(9, 13, 'm')
    m.obj('furn 1 2 banner'); m.obj('furn 16 2 banner'); m.obj('furn 8 2 statue'); m.obj('furn 9 2 statue')
    m.obj('furn 0 12 plant'); m.obj('furn 17 12 plant')
    for (i, (wid, x, y, f)) in enumerate([('mossa', 3, 5, 'right'), ('brann', 3, 8, 'right'), ('iskra', 3, 11, 'right'),
                                           ('morrow', 14, 5, 'left'), ('hale', 14, 8, 'left'), ('seren', 14, 11, 'left')]):
        m.npc(x, y, f'crown_{wid}', wid, face=f, script='crown.warden', show='cradle_done')
    m.npc(8, 4, 'crown_wren', 'wren', face='down', script='crown.wren', show='cradle_done')
    return m


# ═══════════════════════════════════════════════════════════════════════════
# Items hidden inside bushes, rocks and trees (Pokémon-style): face it and press A to search.
# route1 (4, 24) is the berry bush just north of Rootmere's path — the early XP Share easter egg.
HIDDEN_IN = {
    'route1': [(4, 24, 'xp_share', 1, 'bush'), (21, 38, 'tonic', 2, 'bush')],
    'rootmere': [(13, 4, 'tonic', 1, 'bush')],
    'route2': [(45, 14, 'capsule', 3, 'rock'), (31, 23, 'purge_herb', 2, 'bush')],
    'brindlewood': [(15, 23, 'wake_chime', 1, 'bush')],
    'thornwild': [(38, 15, 'strong_tonic', 1, 'tree'), (35, 8, 'rekindle_seed', 1, 'bush')],
    'route3': [(12, 10, 'prime_capsule', 2, 'rock')],
    'route4': [(3, 12, 'star_shard', 1, 'bush'), (27, 40, 'focus_drop', 1, 'rock')],
    'hollowmere': [(24, 28, 'pearl', 1, 'rock')],
    'route6': [(14, 15, 'grand_tonic', 1, 'tree'), (30, 20, 'growth_fruit', 1, 'rock')],
}


def main():
    for fn in MAPS:
        m = fn()
        for (x, y, item, qty, inside) in HIDDEN_IN.get(m.id, []):
            m.item(x, y, item, qty, inside=inside)
        m.save()
    print(f'wrote {len(MAPS)} map sources')


if __name__ == '__main__':
    main()
