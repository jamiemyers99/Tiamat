"""Generates every map source in tools/maps/ for the Riven Reach.

    python tools/worldgen.py && python tools/art/build_maps.py

Hand-made interiors (home_1f, home_2f, wren_house, rootmere_cottage) live in
tools/maps/ directly; everything else is authored here with the mapkit DSL.
Coordinates are tiles; (0,0) is the top-left.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import trials
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
    m = M('rootmere', 34, 38, name='Rootmere', kind='town', base='grass', music='rootmere', weather='none',
          battle='meadow', north='route1 0', fly='6,7')
    m.border(gaps=[('n', 16, 17)])
    m.path([(16, 0), (16, 17)])
    # ── the south glade and the Old Door (Covenant stonework, older than the village; there all game) ──
    m.rect(2, 24, 31, 25, 'T')
    m.path([(18, 17), (18, 26), (12, 26), (12, 32), (18, 32)])
    m.grove(2, 26, 8, 10); m.grove(24, 26, 8, 10)
    m.rect(8, 26, 9, 27, '.'); m.rect(24, 32, 25, 35, '.'); m.rect(8, 34, 9, 35, '.')
    m.path([(18, 24), (18, 25)])
    m.scatter([(10, 29), (11, 31), (22, 27), (23, 30), (23, 27), (21, 33), (10, 33), (15, 35), (22, 34), (9, 35), (25, 34)], 'F')
    m.obj('ancient_door 16 28 to=ancient_tunnel:15,37 face=up cond=ancient_door_open '
          'locked="An enormous door of carved stone, far older than Rootmere. In the middle of it is an empty hollow, the shape of a gem."')
    m.obj('plate 18 31 on=ancient_door_open frame=ancient_slab onframe=ancient_open')
    m.trigger(18, 32, 'rootmere.ancient_door', cond='has:crown_gem&!ancient_door_open')
    for (x, y) in [(15, 31), (21, 31), (11, 28), (22, 29)]:
        m.obj(f'prop {x} {y} stone')
    m.sign(20, 33, 'THE OLD DOOR|Older than Rootmere itself. Nobody knows who built it, or how it opens.')
    m.npc(14, 29, 'rm_elder', 'elder', face='right', script='rootmere.elder')
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
    m.sign(17, 22, 'ROOTMERE POND|Please do not feed the Puddlets.')
    m.obj('prop 9 6 mailbox')
    m.obj('prop 30 20 hay'); m.obj('prop 30 21 hay'); m.obj('prop 21 19 hay')
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
    # A winding lane north from Rootmere. Every trainer stands where the lane is only a few steps wide and faces
    # across it, so each one has to be battled on the way north. The ledge lane on the east side is the quick
    # (one-way) way back home.
    m = M('route1', 34, 50, fill='T', name='Route 1 · Mossway', kind='route', base='grass', music='route', battle='meadow',
          south='rootmere 0', north='brindlewood 2')
    m.rect(16, 48, 17, 49, '.'); m.rect(16, 0, 17, 1, '.')     # ways in and out
    m.rect(4, 40, 31, 47, '.')                                  # the south meadow
    m.rect(2, 34, 5, 39, '.')                                   # west nook (off the meadow)
    m.rect(14, 34, 17, 39, '.')                                 # the lane north (Ollie)
    m.rect(20, 26, 23, 39, '.')                                 # ledge lane back down to the meadow
    m.rect(6, 30, 17, 33, '.')                                  # the bend (Dana)
    m.rect(6, 18, 9, 29, '.')                                   # the long lane
    m.rect(4, 24, 5, 25, '.')                                   # a little notch with a berry bush
    m.rect(6, 14, 27, 17, '.')                                  # the crossing (Nell)
    m.rect(20, 18, 29, 25, '.')                                 # east meadow
    m.rect(24, 6, 27, 13, '.')                                  # the climb north (Theo)
    m.rect(14, 2, 27, 5, '.'); m.rect(2, 2, 13, 9, '.')         # the top path and the north-west glade
    m.path([(16, 49), (16, 31), (7, 31), (7, 15), (25, 15), (25, 3), (16, 3), (16, 0)], ':')
    m.put(26, 16, ':')
    m.rect(4, 42, 11, 47, 'G'); m.rect(20, 20, 29, 25, 'G'); m.rect(2, 2, 9, 5, 'G')
    m.stamp(22, 40, ['  ssssss  ',
                     ' ss~~~~ss ',
                     ' s~~~~~~s ',
                     ' s~~~~~~s ',
                     ' ss~~~~ss ',
                     '  ssssss  '])
    m.hline(38, 20, 23, 'v')                                    # hop down, never back up
    m.put(4, 24, 'q'); m.put(31, 40, 'b'); m.put(2, 39, 'b')
    m.scatter([(20, 44), (21, 46), (13, 41), (30, 47), (9, 19), (6, 28), (15, 33), (26, 14), (12, 7), (22, 5), (27, 17)], 'F')
    # objects
    m.sign(15, 46, 'ROUTE 1 · MOSSWAY|North: Brindlewood   South: Rootmere')
    m.sign(18, 2, 'BRINDLEWOOD|Home of the Moss Trial.')
    m.trainer(14, 36, 'r1_ollie', 'kid', face='right', sight=4)
    m.trainer(10, 30, 'r1_dana', 'lass', face='down', sight=4)
    m.trainer(18, 17, 'r1_nell', 'kid_b', face='up', sight=4)
    m.trainer(24, 8, 'r1_theo', 'youth', face='right', sight=4)
    m.npc(12, 14, 'r1_aide', 'assistant', face='down', script='route1.aide')
    m.item(3, 37, 'capsule', 2)
    m.item(28, 19, 'tonic')
    m.item(5, 8, 'ward_incense')
    m.item(29, 46, 'capsule', hidden=True)
    m.item(23, 30, 'purge_herb')
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
    return trials.brindlewood_trial()


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
    m.trainer(23, 9, 'r2_fisher', 'fisher', face='down', sight=4)
    m.trainer(33, 12, 'r2_ivy', 'lass', face='left', sight=4)
    m.trainer(40, 9, 'r2_bram', 'hiker', face='down', sight=4)
    m.item(5, 5, 'td15')
    m.item(44, 18, 'capsule', 2)
    m.item(15, 20, 'tonic')
    m.item(29, 3, 'wake_chime', hidden=True)
    return m


@reg
def thornwild():
    # Thornwild: one trail from Route 2 (west) down to Saltreach (south), through the old shrine. The trail
    # narrows wherever a trainer waits, and each one faces across it; the glades off the trail are dead ends.
    # The Deepcall acolytes at the shrine still hold the south road until both are beaten (story).
    m = M('thornwild', 44, 40, name='Thornwild', kind='route', base='forest', music='forest', battle='forest',
          west='route2 0', south='saltreach 0', fill='K')
    def c(x0, y0, x1, y1, ch='.'):
        m.rect(x0, y0, x1, y1, ch)
    c(0, 10, 1, 11)                                         # from Route 2
    c(2, 8, 27, 11)                                         # the entry trail (Rook)
    c(4, 2, 13, 5); c(4, 6, 7, 7)                           # north-west glade
    c(16, 4, 27, 7)                                         # north glade
    c(28, 4, 39, 13)                                        # north-east grove (Pip)
    c(12, 12, 15, 21)                                       # the trail south (Sable)
    c(12, 22, 23, 25)                                       # the bend (Orla)
    c(4, 26, 13, 35)                                        # south-west glade
    c(20, 26, 35, 33)                                       # the shrine clearing
    c(36, 24, 41, 31)                                       # east pocket
    c(30, 34, 31, 39)                                       # south to Saltreach
    m.path([(0, 10), (12, 10), (12, 23), (21, 23), (21, 29), (30, 29), (30, 39)], ':')
    c(18, 4, 25, 5, 'G'); c(30, 6, 37, 11, 'G'); c(14, 12, 15, 21, 'G'); c(6, 28, 11, 33, 'G'); c(38, 26, 41, 31, 'G')
    c(4, 2, 9, 3, 'G')
    m.scatter([(20, 27), (34, 27), (21, 32), (34, 32), (17, 9), (26, 6), (9, 34), (37, 24)], 'F')
    m.obj('prop 23 28 stone'); m.obj('prop 32 28 stone'); m.obj('prop 23 31 stone'); m.obj('prop 32 31 stone')
    m.obj('prop 27 27 statue script=thornwild.shrine')
    m.rect(34, 8, 35, 8, 'q')
    m.put(38, 5, 'q')
    m.obj('sign 38 5 script=thornwild.pip')
    m.sign(3, 9, 'THORNWILD|Stay on the trail. The trees remember.', walk=False)
    m.trainer(8, 8, 'tw_bugs', 'kid', face='down', sight=4)
    m.trainer(15, 16, 'tw_ranger', 'ranger', face='left', sight=4)
    m.trainer(18, 22, 'tw_mystic', 'mystic', face='down', sight=4)
    m.trainer(29, 26, 'tw_acolyte_1', 'acolyte', face='down', sight=7, hide='wren2_done', leave='1')   # watches the whole clearing
    m.trainer(26, 33, 'tw_acolyte_2', 'acolyte_b', face='right', sight=4, hide='wren2_done', leave='1')
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
    m.trainer(20, 27, 'st_acolyte_1', 'acolyte', face='up', sight=4, leave='1')
    m.trainer(21, 27, 'st_acolyte_2', 'acolyte_b', face='up', sight=4, leave='1')
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
    return trials.saltreach_trial()


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
    m.trainer(10, 11, 'r3_hiker', 'hiker', face='down', sight=4)
    m.trainer(24, 18, 'r3_sailor', 'sailor', face='up', sight=4)
    m.trainer(30, 14, 'r3_twin', 'twin', face='left', sight=4)
    m.trainer(41, 18, 'r3_fisher', 'fisher', face='left', sight=4)
    m.trainer(20, 10, 'r3_ace', 'ace', face='down', sight=4)
    # starter rescue: a Puddlet stranded in a rock pool, two Deepcall acolytes trying to take it
    m.npc(8, 20, 'r3_puddlet', 'mon:puddlet', face='up', script='rescue.puddlet',
          show='!var:starter=puddlet', hide='rescued_puddlet')
    # once both are beaten they run off down the beach (rescue.poacher / poachersLeave)
    m.trainer(7, 19, 'r3_poacher_a', 'acolyte', face='up', sight=4, script='rescue.poacher',
              show='!var:starter=puddlet', hide='r3_poachers_fled|rescued_puddlet')
    m.trainer(9, 19, 'r3_poacher_b', 'acolyte_b', face='up', sight=4, script='rescue.poacher',
              show='!var:starter=puddlet', hide='r3_poachers_fled|rescued_puddlet')
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
    return trials.gearhollow_trial()


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
    m.trainer(8, 10, 'iw_acolyte_1', 'acolyte', face='down', sight=4, hide='ironworks_done', leave='1')
    m.trainer(12, 7, 'iw_acolyte_2', 'acolyte_b', face='left', sight=4, hide='ironworks_done', leave='1')
    m.trainer(7, 5, 'iw_acolyte_3', 'acolyte', face='right', sight=4, hide='ironworks_done', leave='1')
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
    # Moorwind Way: a single trail north through the fog, past the old stone circle. Every trainer stands where
    # the trail narrows and faces across it. The west ledge lane is a one-way shortcut back to Gearhollow.
    m = M('route4', 36, 54, fill='Y', name='Route 4 · Moorwind Way', kind='route', base='moor', music='moor', battle='moor',
          weather='fog', south='gearhollow 4', north='hollowmere 4')
    m.rect(16, 52, 17, 53, '.'); m.rect(16, 0, 17, 1, '.')      # ways in and out
    m.rect(4, 46, 33, 51, '.')                                   # the southern moor
    m.rect(14, 38, 17, 45, '.')                                  # the first rise (Tor)
    m.rect(14, 34, 29, 37, '.')                                  # the heath (Cordelia)
    m.rect(26, 28, 29, 33, '.')                                  # up to the circle (Wynne)
    m.rect(12, 16, 31, 27, '.')                                  # the stone circle
    m.rect(10, 20, 11, 23, '.')                                  # a gap west to the heather
    m.rect(2, 12, 9, 27, '.')                                    # the west heather
    m.rect(2, 28, 5, 45, '.')                                    # ledge lane back down (one way)
    m.rect(26, 6, 29, 15, '.')                                   # the northern climb (Pemberton)
    m.rect(12, 2, 29, 5, '.')                                    # the ridge path (Hollis)
    m.rect(2, 2, 11, 9, '.')                                     # the north-west hollow
    m.path([(16, 53), (16, 35), (27, 35), (27, 3), (16, 3), (16, 0)], ':')
    m.put(28, 36, ':')
    # stone circle (centre stone carries the old inscription)
    for (x, y) in [(20, 18), (24, 19), (26, 22), (24, 25), (20, 26), (16, 25), (14, 22), (16, 19)]:
        m.obj(f'prop {x} {y} stone')
    m.obj('prop 20 22 stone script=route4.circle')
    m.rect(18, 20, 22, 24, ',')
    # grass
    m.rect(4, 46, 11, 51, 'G'); m.rect(2, 14, 9, 25, 'G'); m.rect(2, 2, 9, 5, 'G'); m.rect(30, 18, 31, 25, 'G')
    m.hline(44, 2, 5, 'v')
    m.stamp(24, 46, ['  ss  ', ' s~~s ', 's~~~~s', ' s~~s ', '  ss  '])
    for (x, y) in [(3, 12), (13, 46), (32, 51), (7, 9), (29, 37), (12, 27), (31, 16), (14, 2), (2, 33)]:
        m.put(x, y, 'b' if (x, y) in [(3, 12), (13, 46), (7, 9)] else 'o')
    m.scatter([(14, 17), (30, 26), (22, 50), (8, 48), (4, 30), (25, 2), (6, 20)], 'F')
    m.sign(18, 51, 'ROUTE 4 · MOORWIND WAY|South: Gearhollow   North: Hollowmere')
    m.sign(18, 2, 'HOLLOWMERE|Mind the fog.')
    m.trainer(14, 41, 'r4_hiker', 'hiker', face='right', sight=4)
    m.trainer(21, 34, 'r4_lady', 'lady', face='down', sight=4)
    m.trainer(26, 30, 'r4_mystic', 'mystic', face='right', sight=4)
    m.trainer(26, 12, 'r4_scholar', 'scholar', face='right', sight=4)
    m.trainer(21, 5, 'r4_ranger', 'ranger', face='up', sight=4)
    m.item(20, 20, 'td10')
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
    return trials.hollowmere_trial()


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
    m.trainer(16, 16, 'r5_fisher', 'fisher', face='down', sight=4)
    m.trainer(36, 21, 'r5_sailor', 'sailor', face='left', sight=4)
    m.trainer(24, 8, 'r5_skier', 'skier', face='left', sight=4)
    m.trainer(40, 11, 'r5_mystic', 'mystic', face='left', sight=4)
    m.trainer(6, 21, 'r5_ace', 'ace_b', face='right', sight=4)
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
    return trials.frostspire_trial()


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
    # Rimepass, laid out like a classic route: one winding pass between the trees, and every trainer stands
    # where the path is narrow enough that you can't slip past without them seeing you. Ledges only go one
    # way (east is downhill); the way back west hops down the ledge into the entrance hollow.
    m = M('route6', 54, 30, fill='N', name='Route 6 · Rimepass', kind='route', base='snow', music='route_b', battle='snow',
          weather='snow', west='frostspire 0', east='riftgate 4')
    m.rect(28, 0, 53, 29, 'Q')                                   # bare ash-rock where the snow ends...
    m.rect(28, 0, 53, 1, 'X'); m.rect(28, 26, 53, 29, 'X'); m.rect(52, 0, 53, 29, 'X'); m.rect(28, 0, 29, 29, 'X')   # ...ringed by dead trees
    m.rect(12, 8, 21, 13, 'R')                                   # a snowy crag between the ridge and the hollow
    # ── the snowy climb ──
    m.rect(0, 16, 1, 17, '.')                                    # from Frostspire
    m.rect(2, 14, 14, 19, '.')                                   # entrance hollow
    m.rect(2, 20, 7, 25, '.')                                    # side meadow
    m.rect(8, 8, 11, 13, '.')                                    # the climb north
    m.rect(2, 4, 25, 7, '.')                                     # the ridge (with a nook at its west end)
    m.rect(22, 8, 25, 13, '.')                                   # the drop
    m.rect(16, 14, 27, 21, '.')                                  # the basin
    # ── the ash flats ──
    m.rect(28, 18, 39, 21, 'a')                                  # into the ash
    m.rect(36, 8, 39, 21, 'a')                                   # up the gully
    m.rect(36, 8, 47, 11, 'a')                                   # along the rim
    m.rect(42, 12, 47, 17, 'a')                                  # the gate square
    m.rect(48, 12, 49, 13, 'a')                                  # a lookout by the road
    m.rect(48, 14, 53, 15, 'a')                                  # the road to Riftgate
    m.rect(42, 18, 47, 25, 'a')                                  # ash hollow (south) — nothing grows this close to the Riven
    # the path, then grass, ledges and rocks on top
    m.path([(0, 16), (8, 16), (8, 4), (22, 4), (22, 16), (26, 16), (26, 19), (37, 19), (37, 9), (44, 9), (44, 14), (53, 14)], ':')
    m.rect(2, 20, 7, 25, 'G'); m.rect(12, 6, 17, 7, 'G'); m.rect(10, 10, 11, 13, 'G'); m.rect(16, 18, 21, 21, 'G')
    m.hline(10, 22, 25, 'v')                                     # ledge down the drop (one way)
    m.vline(15, 14, 19, '<')                                     # ledge back down to the hollow (one way, west)
    for (x, y) in [(3, 7), (24, 12), (27, 14), (16, 14), (36, 21), (29, 21), (47, 12)]:
        m.put(x, y, 'o')
    m.rect(46, 10, 47, 11, 'Q')
    for (x, y) in [(36, 12), (46, 8), (33, 21), (43, 22), (46, 20)]:
        m.obj(f'prop {x} {y} rift_rock')
    m.sign(3, 15, 'ROUTE 6 · RIMEPASS|West: Frostspire   East: Riftgate')
    m.sign(47, 16, 'RIFTGATE|City on the edge of the world.')
    # trainers: each one faces across the pass, so their line of sight covers its whole width
    m.trainer(8, 10, 'r6_skier_1', 'skier', face='right', sight=4)
    m.trainer(20, 7, 'r6_skier_2', 'skier', face='up', sight=4)
    m.trainer(31, 18, 'r6_hiker', 'hiker', face='down', sight=4)
    m.trainer(39, 14, 'r6_acolyte', 'acolyte', face='left', sight=4, leave='1')
    m.trainer(48, 13, 'r6_ace', 'ace', face='down', sight=4)
    m.item(2, 4, 'full_tonic')
    m.item(47, 25, 'apex_capsule')
    m.item(2, 25, 'strong_incense', hidden=True)
    m.item(27, 21, 'rekindle_seed')
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
    return trials.riftgate_trial()


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
    m.trainer(9, 20, 'sc_acolyte_1', 'acolyte', face='right', sight=4)
    m.trainer(12, 17, 'sc_acolyte_2', 'acolyte_b', face='left', sight=4)
    m.trainer(7, 14, 'sc_acolyte_3', 'acolyte', face='right', sight=4)
    m.trainer(18, 10, 'sc_acolyte_4', 'acolyte_b', face='left', sight=4)
    m.npc(10, 12, 'sc_vesk', 'vesk', face='down', script='chapel.vesk', trainer='vesk2', sight=4, hide='vesk2_done')
    m.npc(11, 7, 'sc_maren', 'maren', face='down', script='chapel.maren', trainer='maren2', sight=4, hide='maren2_done')
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
    m.trainer(20, 9, 'ar_acolyte_1', 'acolyte', face='down', sight=4)
    m.trainer(6, 24, 'ar_acolyte_2', 'acolyte_b', face='down', sight=4)
    m.trainer(34, 24, 'ar_acolyte_3', 'acolyte', face='down', sight=4)
    m.trainer(20, 38, 'ar_ace', 'ace_b', face='down', sight=4)
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


@reg
def ancient_tunnel():
    """Under Rootmere, behind the Old Door (opened with the Crown Gem after the Crown Challenge): a winding
    Covenant-built tunnel down to the Deep Cradle. Keeper Enna waits at the carved door at the far end."""
    m = M('ancient_tunnel', 32, 40, name='Ancient Tunnel', kind='cave', base='cave', music='cave', battle='cave',
          light='dark', enc_floor='1', escape='rootmere:18,32', fill='R')
    def c(x0, y0, x1, y1, ch='.'):
        m.rect(x0, y0, x1, y1, ch)
    c(11, 31, 20, 37); c(15, 38, 16, 38)                      # the stair hall under the Old Door
    m.obj('warp 15 38 to=rootmere:18,32 face=down'); m.obj('warp 16 38 to=rootmere:18,32 face=down')
    c(21, 33, 27, 36)                                          # a side vault
    c(4, 32, 10, 34); c(4, 20, 7, 34)                          # west gallery, climbing north
    c(4, 16, 26, 21); m.rect(9, 18, 13, 20, '~')               # the pillared cavern, with a still pool
    c(23, 6, 26, 21)                                           # east stair
    c(8, 6, 26, 10); c(12, 2, 18, 5)                           # north gallery and the door
    c(28, 12, 30, 16); c(27, 14, 27, 14)                       # a hidden nook off the east stair
    c(8, 25, 9, 29); c(2, 23, 3, 26); c(21, 22, 22, 23)        # alcoves, so it isn't all straight lines
    m.put(9, 29, 'o'); m.put(2, 23, 'o')
    for (x, y) in [(13, 33), (18, 33), (13, 35), (18, 35), (16, 16), (20, 16), (9, 16), (14, 8), (18, 8)]:
        m.obj(f'furn {x} {y} pillar')
    m.obj('ancient_door 13 2 to=deep_cradle cond=keeper_met locked="The carved slab will not move."')
    m.obj('plate 15 5 on=keeper_met frame=ancient_slab onframe=ancient_open')
    for (x, y) in [(12, 31), (19, 31), (12, 36), (19, 36), (4, 16), (26, 16), (8, 6), (20, 6), (11, 6)]:
        m.obj(f'prop {x} {y} stone')
    for (x, y) in [(21, 33), (27, 36), (4, 34), (26, 21), (4, 21), (30, 12), (26, 6)]:
        m.obj(f'prop {x} {y} crystal')
    m.npc(15, 6, 'keeper_enna', 'elder_b', face='down', script='tunnel.keeper', name='Enna', hide='keeper_met')
    m.npc(13, 6, 'keeper_enna_side', 'elder_b', face='right', script='tunnel.keeper', name='Enna', show='keeper_met')
    m.trigger(21, 6, 'tunnel.keeper', h=5, cond='!keeper_met')
    m.trainer(6, 27, 'at_ace', 'ace', face='down', sight=4)
    m.trainer(18, 21, 'at_mystic', 'mystic', face='up', sight=3)
    m.trainer(23, 11, 'at_ace_b', 'ace_b', face='right', sight=3)
    m.item(26, 34, 'apex_capsule', 3)
    m.item(5, 17, 'full_tonic', 2)
    m.item(29, 15, 'growth_fruit')
    m.item(24, 7, 'bloom_seed', hidden=True)
    m.item(6, 33, 'panacea')
    return m


@reg
def deep_cradle():
    m = M('deep_cradle', 16, 14, kind='interior', name='The Deep Cradle', floor='ancient', wall='ancient', music='cradle',
          light='dark', battle='cave')
    m.rect(0, 0, 15, 1, 'W')
    m.rect(0, 2, 1, 13, '#'); m.rect(14, 2, 15, 13, '#')
    m.put(7, 13, 'm'); m.put(8, 13, 'm')
    m.obj('furn 6 3 incubator script=cradle.incubator')
    for (x, y) in [(3, 3), (12, 3), (3, 8), (12, 8)]:
        m.obj(f'furn {x} {y} pillar')
    for (x, y) in [(2, 5), (13, 5), (4, 11), (11, 11)]:
        m.obj(f'furn {x} {y} crystal')
    m.obj('light 7 4 r=70 color=#ffb040')
    return m


# ═══════════════════════════════════════════════════════════════════════════
# Items hidden inside bushes, rocks and trees (Pokémon-style): face it and press A to search.
# route1 (4, 24) is the berry bush in the little notch off the long lane — the early XP Share easter egg.
HIDDEN_IN = {
    'route1': [(4, 24, 'xp_share', 1, 'bush'), (31, 40, 'tonic', 2, 'bush')],
    'rootmere': [(13, 4, 'tonic', 1, 'bush')],
    'route2': [(45, 14, 'capsule', 3, 'rock'), (31, 23, 'purge_herb', 2, 'bush')],
    'brindlewood': [(15, 23, 'wake_chime', 1, 'bush')],
    'thornwild': [(38, 14, 'strong_tonic', 1, 'tree'), (35, 8, 'rekindle_seed', 1, 'bush')],
    'route3': [(12, 10, 'prime_capsule', 2, 'rock')],
    'route4': [(3, 12, 'star_shard', 1, 'bush'), (29, 37, 'focus_drop', 1, 'rock')],
    'hollowmere': [(24, 28, 'pearl', 1, 'rock')],
    'route6': [(15, 21, 'grand_tonic', 1, 'tree'), (29, 21, 'growth_fruit', 1, 'rock')],
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
