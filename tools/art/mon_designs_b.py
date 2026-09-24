"""Group B Morph designs (same format as mon_designs.D): species id -> (materials, parts).
Coordinates are in a 96x96 box; ground is y~90; Morphs face left (3/4 view).
"""
from mongen import E, Cap, Tri, Leaf, Flame, Eye, Mouth, Spot
from mon_designs import T

NEW = {}


def batwing(shoulder, wrist, tips, back, mem, bone, z, r=2.0, pull=0.35):
    """Bat/wyvern wing: arm bone shoulder→wrist, finger bones wrist→tips, scalloped membrane."""
    sx, sy = shoulder
    wx, wy = wrist
    pts = [(sx, sy), (wx, wy)]
    for i, (tx, ty) in enumerate(tips):
        if i:
            px, py = tips[i - 1]
            mx, my = (px + tx) / 2, (py + ty) / 2
            pts.append((mx + (wx - mx) * pull, my + (wy - my) * pull))
        pts.append((tx, ty))
    lx, ly = tips[-1]
    bx, by = back
    mx, my = (lx + bx) / 2, (ly + by) / 2
    pts.append((mx + (sx - mx) * pull * 0.6, my + (sy - my) * pull * 0.6))
    pts.append((bx, by))
    out = [Tri(pts, mem, z=z)]
    out.append(Cap(sx, sy, wx, wy, r, r * 0.75, bone, z=z + 0.02))
    for tx, ty in tips:
        out.append(Cap(wx, wy, tx, ty, r * 0.6, 0.5, bone, z=z + 0.01))
    return out


def glow_eye(x, y, w, h, side, mat='glow', z=5, core=None):
    """Angular glowing eye drawn as a polygon (for dark faces where a painted Eye would vanish).
    side=-1: eye on the left of the face (brow slopes down to the right); side=+1: mirrored."""
    drop = h * 0.55
    tl = y - h * 0.5 + (drop if side > 0 else 0)
    tr = y - h * 0.5 + (drop if side < 0 else 0)
    pts = [(x - w, tl), (x + w, tr), (x + w * 0.8, y + h * 0.45), (x, y + h * 0.55), (x - w * 0.8, y + h * 0.45)]
    out = [Tri(pts, mat, z=z, view='front')]
    if core:
        out.append(Spot(x - side * w * 0.2, y + h * 0.1, max(0.8, h * 0.22), core, z=z + 0.01, view='front'))
    return out


# ── Iron/Swarm beetle line: rivetle → carapaxe → juggernox ───────────────────
NEW['rivetle'] = (dict(body='#6a8ab8', accent='#f0a03a', dark='#2a3448', face='#f4f8ff', blush='#ff9aa8'), T([
    # far legs
    Cap(62, 82, 65, 89, 2.6, 2.4, 'dark', z=-1), Cap(72, 80, 76, 88, 2.6, 2.4, 'dark', z=-1),
    # shell dome
    E(57, 66, 24, 19, 'body', z=1),
    # stubby orange horn
    Cap(46, 54, 40, 46, 5.6, 4.2, 'accent', z=1.1), Cap(40, 46, 34, 43, 4.2, 2.8, 'accent', z=1.1),
    # rivets
    Spot(53, 51, 1.6, 'accent', z=1.5), Spot(63, 49, 1.6, 'accent', z=1.5), Spot(72, 53, 1.6, 'accent', z=1.5),
    Spot(78, 62, 1.6, 'accent', z=1.5), Spot(77, 72, 1.6, 'accent', z=1.5),
    # head peeking out from under the shell
    E(34, 77, 13, 9.5, 'dark', z=1.2),
    # near legs
    Cap(36, 84, 33, 89, 2.8, 2.6, 'dark', z=2.5), Cap(49, 84, 49, 89.5, 2.8, 2.6, 'dark', z=2.5), Cap(62, 84, 63, 89.5, 2.8, 2.6, 'dark', z=0.5),
    # the shell's front lip (same material, merges with the dome) shading the eyes
    E(38, 66, 17, 6, 'body', z=1.4, rot=-0.12),
    Spot(27, 67, 1.3, 'accent', z=1.5), Spot(36, 65.5, 1.3, 'accent', z=1.5), Spot(45, 64, 1.3, 'accent', z=1.5),
    # big eyes
    Spot(29, 76, 5.2, 'face', z=3.5), Spot(40, 76, 5.2, 'face', z=3.5),
    Eye(29, 76.5, 4.2, iris='#5ac8ff'), Eye(40, 76.5, 4.2, iris='#5ac8ff'),
    Spot(24, 83, 1.8, 'blush', z=99), Spot(45, 83, 1.8, 'blush', z=99),
    Mouth(34.5, 83, 3, 'smile')], s=0.9))


NEW['carapaxe'] = (dict(body='#5a78a8', accent='#ff9a2a', dark='#232c3e', blade='#7890b4', edge='#e4eeff', glow='#ffc040'), T([
    # far legs (with glowing knees)
    Cap(64, 74, 71, 79, 3.2, 2.8, 'dark', z=-1), Spot(71, 79, 2.6, 'accent', z=-0.9), Cap(71, 79, 74, 89, 2.8, 2.2, 'dark', z=-1),
    Cap(76, 72, 84, 77, 3.2, 2.8, 'dark', z=-1), Spot(84, 77, 2.6, 'accent', z=-0.9), Cap(84, 77, 88, 88, 2.8, 2.2, 'dark', z=-1),
    # underside
    E(60, 73, 23, 10, 'dark', z=0),
    # overlapping armour bands, back to front, with glowing seams
    E(76, 64, 12, 14, 'body', z=1.0),
    E(69, 63, 13, 16, 'accent', z=1.05), E(68, 63, 13, 16, 'body', z=1.1),
    E(61, 62, 13, 17, 'accent', z=1.15), E(60, 62, 13, 17, 'body', z=1.2),
    # pronotum shield
    E(50, 61, 12, 15, 'accent', z=1.25), E(49, 61, 12, 15, 'body', z=1.3),
    Tri([(58, 48), (62, 40), (65, 50)], 'blade', z=1.19), Tri([(67, 50), (72, 43), (74, 52)], 'blade', z=1.09),
    # the axe horn: sweeps up off the shield into a crescent blade
    Cap(48, 52, 33, 33, 6.2, 3.8, 'body', z=1.35),
    Tri([(37, 14), (27, 14), (18, 18), (12, 26), (11, 36), (14, 45), (21, 52), (31, 56), (28, 47), (28, 39), (29, 29), (31, 21)], 'blade', z=1.4),
    Tri([(27, 14), (18, 18), (12, 26), (11, 36), (14, 45), (21, 52), (31, 56), (21, 47), (16, 38), (16, 29), (20, 21)], 'edge', z=1.42),
    Tri([(33, 24), (41, 19), (36, 30)], 'blade', z=1.38),
    # head
    E(34, 69, 9.5, 8.5, 'dark', z=1.6),
    Tri([(27, 73), (20, 76), (28, 76)], 'blade', z=1.7, view='front'),
    # near legs
    Cap(42, 72, 35, 78, 3.2, 2.8, 'dark', z=2), Spot(35, 78, 2.8, 'accent', z=2.1), Cap(35, 78, 31, 89, 2.8, 2.2, 'dark', z=2),
    Cap(54, 76, 50, 81, 3.2, 2.8, 'dark', z=2), Spot(50, 81, 2.8, 'accent', z=2.1), Cap(50, 81, 52, 89, 2.8, 2.2, 'dark', z=2),
    Cap(66, 76, 72, 81, 3.2, 2.8, 'dark', z=0.5), Spot(72, 81, 2.8, 'accent', z=0.6), Cap(72, 81, 76, 89, 2.8, 2.2, 'dark', z=0.5),
    *glow_eye(29, 67, 3, 2.6, -1), *glow_eye(37.5, 67, 2.6, 2.4, 1)], s=0.9))


NEW['juggernox'] = (dict(body='#4a6494', accent='#ff8a1a', dark='#1c2232', horn='#8a9cbc', steam='#c4ccd8', glow='#ffb030'), T([
    # exhaust stacks venting steam
    Cap(80, 42, 82, 32, 3.2, 3.2, 'dark', z=0.8), E(82, 31, 4, 2, 'dark', z=0.82), Spot(82, 31, 1.8, 'accent', z=0.83),
    Cap(88, 50, 90, 42, 2.6, 2.6, 'dark', z=0.8), E(90, 41, 3.2, 1.6, 'dark', z=0.82), Spot(90, 41, 1.4, 'accent', z=0.83),
    E(83, 25, 3.6, 3.2, 'steam', z=0.85), E(85, 20, 4.6, 4, 'steam', z=0.85), E(89, 17, 4.2, 3.8, 'steam', z=0.85),
    E(86, 13, 3.8, 3.4, 'steam', z=0.85), E(90, 10, 3, 2.8, 'steam', z=0.85), E(91, 35, 2.2, 2, 'steam', z=0.85), E(92, 31, 1.6, 1.5, 'steam', z=0.85),
    # far legs
    Cap(66, 74, 76, 80, 5, 4.2, 'dark', z=-1), Spot(76, 80, 3.4, 'accent', z=-0.9), Cap(76, 80, 80, 89, 4.2, 3.2, 'dark', z=-1),
    Cap(78, 72, 87, 77, 5, 4.2, 'dark', z=-1), Spot(87, 77, 3.4, 'accent', z=-0.9), Cap(87, 77, 90, 88, 4.2, 3, 'dark', z=-1),
    # underside
    E(58, 72, 30, 12, 'dark', z=0),
    # spikes behind each band's crest
    Tri([(53, 36), (57, 16), (65, 34)], 'horn', z=1.19), Tri([(65, 40), (72, 22), (76, 38)], 'horn', z=1.09),
    Tri([(75, 45), (85, 32), (85, 48)], 'horn', z=0.99),
    # armour bands with glowing seams
    E(79, 60, 12, 19, 'body', z=1.0),
    E(71, 58, 14, 22, 'accent', z=1.05), E(70, 58, 14, 22, 'body', z=1.1),
    E(61, 56, 15, 24, 'accent', z=1.15), E(60, 56, 15, 24, 'body', z=1.2),
    E(48, 57, 14, 20, 'accent', z=1.25), E(47, 57, 14, 20, 'body', z=1.3),
    Spot(52, 74, 1.6, 'horn', z=1.31), Spot(62, 77, 1.6, 'horn', z=1.21), Spot(72, 76, 1.6, 'horn', z=1.11), Spot(81, 73, 1.6, 'horn', z=1.01),
    # the battering ram: a massive iron-banded upper horn hooking down over a lower horn
    Tri([(36, 34), (40, 25), (44, 36)], 'horn', z=1.33), Tri([(26, 30), (29, 22), (33, 31)], 'horn', z=1.33),
    Cap(47, 45, 28, 33, 8, 6.6, 'body', z=1.35), Cap(28, 33, 14, 31, 6.6, 5.2, 'body', z=1.35),
    Cap(15, 31, 6, 41, 5.2, 2.4, 'horn', z=1.36),
    Cap(36, 31, 33, 44, 1.6, 1.6, 'dark', z=1.37), Cap(22, 25, 21, 38, 1.5, 1.5, 'dark', z=1.37),
    Spot(35, 33, 1.1, 'horn', z=1.38), Spot(34, 41, 1.1, 'horn', z=1.38), Spot(22, 28, 1, 'horn', z=1.38), Spot(21, 35, 1, 'horn', z=1.38),
    E(26, 64, 11.5, 10.5, 'dark', z=1.6),
    Tri([(18, 72), (10, 78), (20, 76)], 'horn', z=1.65, view='front'), Tri([(26, 74), (22, 80), (29, 76)], 'horn', z=1.65, view='front'),
    Cap(25, 67, 12, 61, 5.4, 4.2, 'body', z=1.8), Cap(12, 61, 6, 51, 4.2, 2, 'horn', z=1.81),
    Cap(18, 60, 17, 69, 1.3, 1.3, 'dark', z=1.82),
    # near legs
    Cap(40, 72, 30, 79, 5.4, 4.6, 'dark', z=2), Spot(30, 79, 3.6, 'accent', z=2.1), Cap(30, 79, 27, 89, 4.6, 3.4, 'dark', z=2),
    Tri([(20, 90), (27, 84), (33, 90)], 'horn', z=2.2), Tri([(34, 78), (40, 71), (39, 80)], 'horn', z=2.15),
    Cap(56, 76, 51, 82, 5.4, 4.6, 'dark', z=2), Spot(51, 82, 3.6, 'accent', z=2.1), Cap(51, 82, 53, 89, 4.6, 3.4, 'dark', z=2),
    Tri([(46, 90), (53, 84), (59, 90)], 'horn', z=2.2), Tri([(55, 81), (61, 75), (59, 83)], 'horn', z=2.15),
    Cap(68, 76, 74, 82, 5.4, 4.6, 'dark', z=0.5), Spot(74, 82, 3.6, 'accent', z=0.6), Cap(74, 82, 77, 89, 4.6, 3.4, 'dark', z=0.5),
    *glow_eye(20, 61, 3.4, 3, -1, core='steam'), *glow_eye(30, 61, 3, 2.8, 1, core='steam'),
    Spot(16, 67, 1, 'glow', z=5, view='front'), Spot(33, 67, 1, 'glow', z=5, view='front')], dx=-1))


# ── Drake line: wyvlet → wyverant → skyrannox ──────────────────────────────
NEW['wyvlet'] = (dict(body='#3aa8a0', belly='#f8ecd0', accent='#ff7a5a', horn='#f8ecd0', blush='#ff9aa8', nose='#1e4a48'), T([
    # stubby tail with a little coral spade
    Cap(60, 82, 76, 78, 6, 2.6, 'body', z=-2), Tri([(74, 74), (84, 72), (80, 81)], 'accent', z=-1.9),
    # far wing (tiny)
    *batwing((60, 66), (66, 52), [(80, 50), (82, 60)], (68, 68), 'accent', 'body', z=-1.5, r=1.8),
    E(58, 88, 5, 3, 'body', z=-1),
    # body
    E(52, 76, 15, 13, 'body', z=0), E(48, 79, 9, 9, 'belly', z=0.5),
    Tri([(58, 62), (63, 58), (63, 65)], 'accent', z=-0.2), Tri([(63, 67), (69, 64), (67, 71)], 'accent', z=-0.2),
    # near wing (tiny)
    *batwing((56, 68), (62, 56), [(76, 54), (78, 64)], (64, 72), 'accent', 'body', z=0.8, r=1.8),
    E(42, 88, 5.5, 3, 'body', z=1),
    # head
    Cap(40, 43, 36, 35, 2.6, 1.6, 'horn', z=2.9), Cap(52, 43, 56, 36, 2.6, 1.6, 'horn', z=2.9),
    E(42, 55, 17, 15, 'body', z=3), E(29, 62, 7, 5, 'belly', z=3.2),
    Spot(24.5, 60, 0.8, 'nose', z=3.3),
    Eye(35, 53, 4.4, iris='#ffcf4a'), Eye(48, 53, 4.4, iris='#ffcf4a'),
    Spot(35, 61, 2, 'blush', z=99), Spot(53, 60, 2.2, 'blush', z=99),
    Mouth(30, 64, 4, 'smile')], s=0.9))


NEW['wyverant'] = (dict(body='#2f968f', belly='#f4e4c4', accent='#ff6a4a', horn='#f4e8d0', nose='#123a38'), T([
    # far wing
    *batwing((60, 50), (74, 24), [(92, 22), (93, 38), (86, 50)], (68, 60), 'accent', 'body', z=-3, r=2.4),
    # tail with a spiked tip
    Cap(62, 76, 80, 84, 6, 4, 'body', z=-1), Cap(80, 84, 89, 72, 4, 2, 'body', z=-1.1),
    Tri([(86, 68), (93, 60), (92, 74)], 'accent', z=-1.05), Tri([(84, 70), (82, 62), (89, 67)], 'accent', z=-1.15),
    Tri([(70, 76), (74, 70), (77, 79)], 'accent', z=-1.2), Tri([(78, 78), (83, 73), (84, 82)], 'accent', z=-1.2),
    # far leg
    E(60, 76, 7, 10, 'body', z=-0.5), E(62, 88, 6, 2.6, 'body', z=-0.4),
    # near wing
    *batwing((54, 48), (56, 20), [(72, 14), (80, 26), (76, 40)], (62, 56), 'accent', 'body', z=-2.5, r=2.4),
    # torso
    E(52, 64, 12, 15, 'body', z=0.5, rot=0.35), E(46, 67, 6, 11, 'belly', z=0.8, rot=0.3),
    # near leg
    E(47, 77, 8, 10, 'body', z=1.2), E(43, 88, 7, 2.6, 'body', z=1.3),
    Tri([(36, 89), (38, 86), (40, 89)], 'horn', z=1.4), Tri([(40, 90), (42, 86), (44, 90)], 'horn', z=1.4),
    # neck and dorsal spikes
    Tri([(46, 42), (52, 38), (50, 46)], 'accent', z=1.4), Tri([(54, 48), (60, 45), (58, 53)], 'accent', z=0.4),
    Cap(48, 54, 38, 40, 6, 5, 'body', z=1.5), Cap(44, 55, 35, 42, 3, 2.4, 'belly', z=1.7),
    # head with growing horns
    Cap(36, 30, 47, 21, 2.4, 1, 'horn', z=1.8),
    E(32, 34, 9.5, 8, 'body', z=2, rot=-0.1), E(22, 38, 7, 4.5, 'body', z=2.2), E(24, 41.5, 6, 2.2, 'belly', z=2.3),
    Tri([(27, 29), (34, 26), (33, 31)], 'accent', z=2.35),
    Cap(32, 28, 40, 19, 2.2, 1, 'horn', z=2.5),
    Spot(17, 36, 0.9, 'nose', z=2.4),
    Eye(29, 33, 3, 'fierce'), Mouth(21, 41, 4, 'fang')], s=0.9, dx=-2))


NEW['skyrannox'] = (dict(body='#1a5c62', belly='#f0dcb8', accent='#ff5a36', horn='#f4e8d0', inner='#5a1420', face='#fff8ec',
                         nose='#0a2a2a', glow='#ffd24a', muzzle='#c8a882'), T([
    # wings spread wide
    *batwing((62, 44), (80, 10), [(93, 5), (94, 26), (92, 44)], (72, 58), 'accent', 'body', z=-3, r=3),
    *batwing((52, 42), (48, 5), [(64, 3), (74, 14), (70, 32)], (58, 52), 'accent', 'body', z=-2.5, r=3),
    # tail sweeping back with a blade tip
    Cap(64, 76, 82, 86, 8, 5, 'body', z=-1), Cap(82, 86, 90, 74, 5, 2.6, 'body', z=-1.1),
    Tri([(87, 70), (94, 61), (94, 78)], 'accent', z=-1.05), Tri([(86, 72), (81, 62), (90, 68)], 'accent', z=-1.15),
    Tri([(70, 78), (75, 70), (78, 81)], 'accent', z=-1.2), Tri([(79, 82), (85, 75), (86, 85)], 'accent', z=-1.2),
    # far leg
    E(64, 74, 8, 11, 'body', z=-0.5), E(67, 88, 7, 2.8, 'body', z=-0.4),
    Tri([(60, 90), (62, 85), (64, 90)], 'horn', z=-0.3),
    # torso
    E(54, 60, 16, 18, 'body', z=0.5, rot=0.35), E(46, 64, 8.5, 13, 'belly', z=0.8, rot=0.3),
    Cap(40, 57, 50, 54, 0.6, 0.6, 'muzzle', z=0.85), Cap(39, 63, 51, 61, 0.6, 0.6, 'muzzle', z=0.85), Cap(41, 69, 52, 68, 0.6, 0.6, 'muzzle', z=0.85),
    # near leg
    E(50, 73, 11, 13, 'body', z=1.2), Cap(47, 80, 43, 87, 5.4, 4, 'body', z=1.25), E(41, 88, 8, 3, 'body', z=1.3),
    Tri([(31, 90), (33, 83), (37, 90)], 'accent', z=1.4), Tri([(37, 90), (39, 83), (43, 90)], 'accent', z=1.4),
    # neck and dorsal spikes
    Tri([(40, 30), (47, 20), (47, 35)], 'accent', z=1.4), Tri([(48, 38), (57, 31), (54, 44)], 'accent', z=1.4),
    Tri([(56, 45), (65, 41), (60, 50)], 'accent', z=0.4),
    Cap(48, 50, 32, 34, 8.5, 6.8, 'body', z=1.5), Cap(43, 53, 28, 37, 4, 3, 'belly', z=1.7),
    # roaring head: horns swept straight back
    Cap(30, 24, 52, 16, 3.2, 1.2, 'horn', z=1.8),
    E(28, 28, 11, 8.5, 'body', z=2, rot=-0.2),
    Tri([(30, 29), (10, 25), (8, 39), (26, 35)], 'inner', z=2.05),
    Tri([(36, 21), (14, 19), (4, 21), (4, 26), (12, 28), (34, 31)], 'body', z=2.2),
    Tri([(32, 33), (14, 39), (5, 43), (7, 38), (26, 30)], 'body', z=2.1),
    Tri([(9, 27), (11, 32.5), (13, 27.5)], 'face', z=2.25), Tri([(16, 28), (18, 33.5), (20, 28.5)], 'face', z=2.25),
    Tri([(11, 38), (13, 32), (15, 37)], 'face', z=2.15), Tri([(18, 36), (20, 30.5), (22, 34.5)], 'face', z=2.15),
    Tri([(18, 21), (30, 14), (33, 22)], 'accent', z=2.3),
    Cap(27, 20, 48, 9, 2.8, 1, 'horn', z=2.4), Spot(47, 9.5, 1.3, 'accent', z=2.41),
    Spot(6, 22, 0.9, 'nose', z=2.3),
    *glow_eye(24.5, 24.5, 4, 3.4, 1)], dx=-1))


# ── Swarm bee line: hivling → waspire ──────────────────────────────────────
NEW['hivling'] = (dict(body='#f5c542', dark='#3a2a1a', wing='#e8f4ff', accent='#f09a20', blush='#ff8a9a'), T([
    # tiny wings
    Leaf(56, 54, 16, 10, -1.25, 'wing', z=-1), Leaf(60, 56, 14, 8, -0.7, 'wing', z=-1.2),
    # honey-drop tail
    Flame(79, 84, 12, 9, 'accent', z=-0.5, lean=0.4),
    # legs
    Cap(46, 82, 44, 89, 1.6, 1.4, 'dark', z=-0.5), Cap(58, 82, 58, 89, 1.6, 1.4, 'dark', z=-0.5), Cap(66, 80, 70, 88, 1.6, 1.4, 'dark', z=-0.5),
    # striped fuzzy abdomen
    E(64, 72, 14, 13, 'dark', z=0), E(61, 72, 13, 13.4, 'body', z=0.1), E(57, 72, 12, 13.6, 'dark', z=0.2), E(53, 72, 11, 13.8, 'body', z=0.3),
    # antennae
    Cap(36, 50, 30, 38, 1.2, 1, 'dark', z=1.5), E(29, 37, 2.6, 2.6, 'accent', z=1.6),
    Cap(46, 50, 51, 37, 1.2, 1, 'dark', z=1.5), E(52, 36, 2.6, 2.6, 'accent', z=1.6),
    # big round fuzzy head with a cowlick
    Leaf(41, 50, 9, 5, -2.1, 'body', z=1.9), Leaf(42, 50, 10, 5, -1.45, 'body', z=1.9), Leaf(43, 50, 8, 4.5, -0.9, 'body', z=1.9),
    E(40, 63, 16, 15, 'body', z=2),
    Spot(25, 60, 2.4, 'body', z=1.95), Spot(26, 69, 2.2, 'body', z=1.95), Spot(33, 76, 2.2, 'body', z=1.95), Spot(45, 77, 2.2, 'body', z=1.95),
    Eye(34, 62, 4.2, iris='#9a6a2a'), Eye(46, 62, 4.2, iris='#9a6a2a'),
    Spot(29, 69, 2.2, 'blush', z=99), Spot(51, 69, 2.2, 'blush', z=99),
    Mouth(40, 70, 3, 'smile')], s=0.9))


NEW['waspire'] = (dict(body='#f0a820', dark='#241c22', wing='#dff0ff', accent='#ffd040', muzzle='#f5c542', dot='#ff3a4a', glow='#ff4a2a'), [
    # sharp wings
    Leaf(54, 50, 38, 11, -0.72, 'wing', z=-2), Leaf(54, 52, 32, 9, -0.3, 'wing', z=-2.2), Leaf(52, 48, 32, 9, -1.1, 'wing', z=-1.8),
    # stinger and banded abdomen
    Cap(77, 81, 91, 89, 2.6, 0.3, 'dark', z=-0.1),
    E(78, 82, 6, 5.5, 'dark', z=0, rot=0.8), E(74, 78, 8, 7, 'body', z=0.1, rot=0.8),
    E(69, 73, 9, 8, 'dark', z=0.2, rot=0.8), E(64, 68, 9, 8.5, 'body', z=0.3, rot=0.8),
    Cap(56, 58, 60, 63, 2.2, 2.2, 'dark', z=0.35),
    # dangling legs
    Cap(50, 60, 48, 70, 1.4, 1.2, 'body', z=0.9), Cap(48, 70, 50, 78, 1.2, 0.9, 'dark', z=0.9),
    Cap(56, 60, 58, 70, 1.4, 1.2, 'body', z=0.4), Cap(58, 70, 56, 78, 1.2, 0.9, 'dark', z=0.4),
    # thorax
    E(52, 54, 9, 9, 'dark', z=1), Spot(52, 50, 2.4, 'body', z=1.1),
    Tri([(56, 47), (62, 42), (60, 50)], 'dark', z=0.95),
    # raised forelegs with hooks
    Cap(46, 58, 36, 58, 1.6, 1.3, 'body', z=2.5), Cap(36, 58, 30, 52, 1.3, 1, 'dark', z=2.5),
    # head
    Cap(34, 38, 26, 28, 1, 0.8, 'dark', z=1.5), Cap(26, 28, 20, 30, 0.8, 0.7, 'dark', z=1.5),
    E(36, 44, 10, 9, 'dark', z=2), E(31, 48.5, 6, 4.5, 'muzzle', z=2.1),
    Tri([(27, 50), (22, 56), (29, 53)], 'dark', z=2.2, view='front'), Tri([(32, 51), (29, 57), (34, 53)], 'dark', z=2.2, view='front'),
    # crown
    Cap(30, 37, 44, 36, 1.8, 1.8, 'accent', z=2.3),
    Tri([(29, 37), (29, 28), (34, 35)], 'accent', z=2.3), Tri([(34, 36), (37, 24), (41, 35)], 'accent', z=2.3), Tri([(41, 36), (46, 28), (45, 38)], 'accent', z=2.3),
    Spot(37, 35.5, 1.4, 'dot', z=2.4),
    *glow_eye(31, 43, 3.2, 3, -1), *glow_eye(40, 43, 2.8, 2.8, 1)])


# ── Ember salamander line: scorchling → magmaw ─────────────────────────────
NEW['scorchling'] = (dict(body='#ff6a3a', belly='#ffe0a0', flame='#ffc83a', core='#fff6c0', accent='#ffa84a', blush='#ff3a5a'), T([
    # tail curling up to a flame tip
    Cap(62, 80, 76, 77, 5, 3.8, 'body', z=-2), Cap(76, 77, 83, 66, 3.8, 2.6, 'body', z=-2.1),
    Flame(84, 67, 22, 14, 'flame', z=-1.9, lean=0.2), Flame(84, 67, 12, 7, 'core', z=-1.85, lean=0.2),
    # far legs
    Cap(58, 80, 62, 88, 3, 2.8, 'body', z=-1), Cap(44, 81, 46, 88, 3, 2.8, 'body', z=-1),
    # body
    E(53, 77, 15, 10, 'body', z=0), E(49, 83, 11, 4.5, 'belly', z=0.3),
    Spot(58, 71, 2, 'accent', z=0.4), Spot(65, 75, 1.6, 'accent', z=0.4), Spot(51, 70, 1.5, 'accent', z=0.4),
    # near legs
    Cap(39, 80, 36, 88, 3.4, 3, 'body', z=1.5), Cap(61, 81, 64, 88.5, 3.4, 3, 'body', z=1.5),
    # head with a little flame tuft flickering back
    Flame(38, 52, 16, 10, 'flame', z=2.02, lean=0.9), Flame(46, 54, 11, 7, 'flame', z=2.01, lean=1.0),
    Flame(38, 52, 8, 5, 'core', z=2.03, lean=0.9),
    E(34, 62, 16, 13, 'body', z=2), E(30, 69, 10, 4.5, 'belly', z=2.1),
    Eye(28, 60, 4.4, iris='#ffcf4a'), Eye(41, 60, 4.4, iris='#ffcf4a'),
    Spot(23, 67, 2, 'blush', z=99), Spot(46, 67, 2, 'blush', z=99),
    Mouth(32, 67.5, 7, 'smile')], s=0.9))


NEW['magmaw'] = (dict(body='#cc3a1c', belly='#f4cc90', flame='#ffac2a', core='#fff2a8', stone='#2c2430', accent='#ff8a1a',
                      face='#fff4e0', inner='#5a1418', claw='#2c2430', glow='#ffe04a'), [
    # tail with obsidian spikes and a flame tip
    Cap(72, 74, 85, 80, 9, 6, 'body', z=-2), Cap(85, 80, 87, 66, 6, 3.4, 'body', z=-2.1),
    Tri([(75, 67), (80, 59), (84, 70)], 'stone', z=-2.2), Tri([(85, 73), (91, 68), (89, 77)], 'stone', z=-2.2),
    Flame(87, 66, 20, 11.5, 'flame', z=-1.9, lean=0.2), Flame(87, 66, 10, 6, 'core', z=-1.85, lean=0.2),
    # far legs
    Cap(70, 76, 74, 86, 5, 4.5, 'body', z=-1), E(75, 88, 6, 2.6, 'body', z=-0.9),
    Cap(46, 76, 48, 86, 5, 4.5, 'body', z=-1), E(47, 88, 6, 2.6, 'body', z=-0.9),
    # back flames licking up from between the plates
    Flame(55, 52, 20, 11, 'flame', z=0.55, lean=0.5), Flame(55, 52, 10, 5, 'core', z=0.56, lean=0.5),
    Flame(70, 50, 27, 13, 'flame', z=0.55, lean=0.6), Flame(70, 50, 14, 6.5, 'core', z=0.56, lean=0.6),
    Flame(83, 56, 16, 9, 'flame', z=0.55, lean=0.6),
    # body; magma glows through the cracks between obsidian plates
    E(58, 69, 26, 15, 'body', z=0), E(54, 80, 20, 5, 'belly', z=0.3),
    E(61, 61, 25, 11, 'accent', z=0.5),
    Tri([(37, 63), (39, 55), (47, 50), (55, 51), (56, 60), (45, 65)], 'stone', z=0.6, flat=True),
    Tri([(58, 59), (57, 50), (66, 47), (74, 49), (72, 58), (64, 62)], 'stone', z=0.6, flat=True),
    Tri([(74, 59), (76, 51), (82, 53), (86, 60), (83, 66), (77, 65)], 'stone', z=0.6, flat=True),
    Tri([(46, 67), (57, 62), (63, 65), (60, 72), (48, 72)], 'stone', z=0.6, flat=True),
    Tri([(65, 64), (73, 61), (81, 67), (77, 72), (67, 72)], 'stone', z=0.6, flat=True),
    # near legs
    Cap(40, 72, 34, 86, 6, 5, 'body', z=1.5), E(31, 88, 8, 3, 'body', z=1.6),
    Tri([(22, 90), (24, 86), (27, 90)], 'claw', z=1.7), Tri([(26, 90), (28, 86), (31, 90)], 'claw', z=1.7),
    Cap(66, 74, 64, 86, 6, 5, 'body', z=1.5), E(61, 88, 8, 3, 'body', z=1.6),
    Tri([(52, 90), (54, 86), (57, 90)], 'claw', z=1.7), Tri([(56, 90), (58, 86), (61, 90)], 'claw', z=1.7),
    # huge crocodile head, jaws wide open
    E(38, 57, 13, 11, 'body', z=2),
    Tri([(40, 57), (10, 57), (8, 71), (38, 67)], 'inner', z=2.05),
    Tri([(40, 46), (18, 47), (8, 49), (4, 53), (5, 58), (11, 59), (40, 60)], 'body', z=2.2),
    Tri([(38, 67), (24, 71), (10, 75), (5, 75), (5, 70), (12, 66), (38, 60)], 'body', z=2.1),
    Tri([(10, 58), (12, 63.5), (14, 58.5)], 'face', z=2.25), Tri([(16, 59), (18, 64.5), (20, 59)], 'face', z=2.25),
    Tri([(22, 59), (24, 64), (26, 59)], 'face', z=2.25), Tri([(29, 59.5), (30.5, 63), (32, 59.5)], 'face', z=2.25),
    Tri([(12, 66), (14, 61), (16, 65.5)], 'face', z=2.15), Tri([(19, 64.5), (21, 59.5), (23, 64)], 'face', z=2.15),
    Tri([(26, 63), (28, 58.5), (30, 62.5)], 'face', z=2.15),
    E(8, 50, 3.4, 2.6, 'body', z=2.25), Spot(7, 49, 1.1, 'stone', z=2.3),
    # obsidian brow and snout plates with a magma crack
    Tri([(13, 49), (22, 46.5), (31, 47.5), (23, 50.5)], 'stone', z=2.3, flat=True),
    Tri([(31, 47.5), (39, 42), (49, 46), (42, 49)], 'stone', z=2.3, flat=True),
    Cap(44, 51, 47, 58, 0.7, 0.7, 'accent', z=2.25), Cap(47, 58, 45, 62, 0.7, 0.7, 'accent', z=2.25),
    *glow_eye(38, 51.5, 4.4, 3.6, 1)])


# ── Swarm/Brawl: mantipule → mantiscythe ───────────────────────────────────
def _scythe(sx, sy, ex, ey, side, z):
    """Mantis fore-limb: upper arm out to the elbow, then a huge sickle blade hanging down (pale edge, green spine)."""
    f = lambda pts: [(ex + side * x * 1.15, ey + y * 1.2) for x, y in pts]
    blade = f([(1, -3), (-7, -1), (-13, 7), (-16, 17), (-15, 27), (-11, 35), (-9, 27), (-9, 17), (-6, 9), (0, 4)])
    spine = f([(1, -3), (-7, -1), (-13, 7), (-16, 17), (-15, 27), (-11, 35), (-12.5, 27), (-13, 17), (-10, 8), (-4, 3)])
    return [Cap(sx, sy, ex, ey, 4.4, 3.6, 'body', z=z),
            Tri(blade, 'accent', z=z + 0.1), Tri(spine, 'body', z=z + 0.12),
            Tri(f([(-4, -1), (-2, -8), (1, -2)]), 'dark', z=z + 0.13)]


NEW['mantiscythe'] = (dict(body='#5a9a3a', belly='#c8e8a0', accent='#e8f0d0', dark='#2a3a1a', wing='#3f7a30', scar='#f0e0c8'), [
    # folded wings worn like a tattered cape
    Tri([(36, 42), (50, 40), (46, 64), (38, 80), (34, 88), (31, 84), (27, 88), (25, 82), (26, 64)], 'wing', z=-2),
    Tri([(46, 40), (60, 42), (70, 64), (71, 82), (69, 88), (66, 84), (62, 88), (58, 82), (50, 64)], 'wing', z=-2.1),
    Cap(38, 46, 30, 82, 0.7, 0.7, 'dark', z=-1.95), Cap(58, 46, 66, 82, 0.7, 0.7, 'dark', z=-2.05),
    # thin tail
    Cap(58, 76, 76, 70, 3.6, 1.6, 'body', z=-2.5),
    # legs
    Cap(42, 72, 39, 88, 5.2, 4.6, 'body', z=0), Cap(55, 72, 58, 88, 5.2, 4.6, 'body', z=0),
    E(37, 88, 7, 3.2, 'body', z=0.1), E(60, 88, 7, 3.2, 'body', z=0.1),
    Tri([(44, 78), (48, 74), (46, 81)], 'dark', z=0.2), Tri([(53, 78), (49, 74), (51, 81)], 'dark', z=0.2),
    # far scythe arm
    *_scythe(60, 50, 74, 44, -1, 0.5),
    # body: broad chest tapering to the waist
    E(48, 58, 16, 14, 'body', z=1), E(48, 70, 10, 8, 'body', z=1.05), E(47, 62, 8, 10, 'belly', z=1.5),
    Cap(41, 56, 51, 68, 0.8, 0.8, 'scar', z=1.6, view='front'), Cap(45, 54, 55, 64, 0.8, 0.8, 'scar', z=1.6, view='front'),
    # spiked shoulders
    Tri([(33, 49), (27, 38), (41, 45)], 'dark', z=1.7), Tri([(56, 45), (68, 38), (64, 50)], 'dark', z=0.9),
    # near scythe arm
    *_scythe(36, 50, 22, 44, 1, 2),
    # antennae swept back
    Cap(44, 24, 38, 8, 1.3, 1, 'accent', z=2.4), E(37, 7, 3, 3, 'accent', z=2.5),
    Cap(52, 24, 60, 8, 1.3, 1, 'accent', z=2.4), E(61, 7, 3, 3, 'accent', z=2.5),
    # head with angry brows and mandibles
    E(48, 34, 14, 12.5, 'body', z=3),
    Tri([(41, 42), (43, 49), (46, 43)], 'dark', z=3.1, view='front'), Tri([(51, 43), (54, 49), (56, 42)], 'dark', z=3.1, view='front'),
    Cap(37, 28, 46, 31, 1.3, 1.3, 'dark', z=3.2, view='front'), Cap(60, 28, 51, 31, 1.3, 1.3, 'dark', z=3.2, view='front'),
    Cap(37, 25, 46, 40, 0.8, 0.8, 'scar', z=3.25, view='front'),
    Eye(42, 34, 3.4, 'fierce'), Eye(55, 34, 3.4, 'fierce')])
