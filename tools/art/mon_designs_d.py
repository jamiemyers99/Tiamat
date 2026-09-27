"""Group D: the mythical Twinklit line (Mind/Fae) — Aldous's late partner's little one.
A tiny floating kitten with fairy wings and a star-wisp tail that grows into a haloed, winged lynx.
Same format as mon_designs.D: (materials, parts); 96x96 box, ground y~90, facing left.
"""
import math
from mongen import E, Cap, Tri, Leaf, Eye, Mouth, Spot
from mon_designs import T, quad
from mon_designs_c import star, band

NEW = {}

# 103. twinklit -- round, big-headed kitten that floats on fairy wings; a star glows at its tail tip
NEW['twinklit'] = (dict(body='#f6ecff', belly='#ffffff', inner='#ffb0dc', accent='#ff8fcf', wing='#c6ecff',
                       star='#ffe27a', gem='#b47cff', nose='#e0609a'), T([
    # fairy wings (behind)
    Leaf(60, 60, 24, 12, -1.25, 'wing', z=-3.2), Leaf(62, 64, 19, 10, -0.55, 'wing', z=-3.3),
    # curly tail with a star wisp
    band([(64, 80), (72, 76), (76, 68), (75, 60), (71, 55)], 5.5, 'body', z=-2, w1=3),
    Spot(71, 54, 2.2, 'accent', z=-1.95), star(71, 49, 6.5, 'star', z=-1.9),
    # chubby floating body and little paws
    E(53, 74, 17, 13.5, 'body', z=0), E(46, 78, 10, 8.5, 'belly', z=0.3),
    E(40, 86, 5, 3.2, 'body', z=1), E(53, 87, 5, 3.2, 'body', z=1),
    # ears
    Tri([(25, 42), (27, 19), (40, 33)], 'body', z=2.5), Tri([(28.5, 38), (29.5, 24), (36.5, 33.5)], 'inner', z=2.6),
    Tri([(47, 31), (59, 17), (61, 40)], 'body', z=2.5), Tri([(50, 32), (57.5, 22), (58, 36)], 'inner', z=2.6),
    # big round head
    E(42, 51, 20.5, 17.5, 'body', z=3),
    Tri([(21, 53), (15, 57), (22, 60)], 'body', z=2.9), Tri([(62, 53), (68, 56), (62, 60)], 'body', z=2.9),
    # forehead gem, blush, face
    Spot(41.5, 38.5, 2.7, 'gem', z=4, view='front'), Spot(40.7, 37.6, 0.9, 'belly', z=4.1, view='front'),
    Spot(29.5, 57, 2.8, 'inner', z=4, view='front'), Spot(53.5, 57, 2.8, 'inner', z=4, view='front'),
    Eye(35, 50, 4.4, 'round', iris='#b47cff'), Eye(48.5, 50, 4.4, 'round', iris='#b47cff'),
    Spot(41.8, 56, 1.2, 'nose', z=102), Mouth(41.8, 59, 3, 'smile')], s=0.92, dy=-2))

# 104. lumelynx -- a slender lynx with ear tufts, taller wings and a ribbon tail of two star wisps
NEW['lumelynx'] = (dict(body='#efe2ff', belly='#ffffff', accent='#ff8fcf', inner='#ffb0dc', nose='#e0609a',
                        wing='#bfe6ff', star='#ffe27a', gem='#a86cff'), T([
    Leaf(58, 55, 30, 13, -1.15, 'wing', z=-3.2), Leaf(61, 59, 25, 11, -0.45, 'wing', z=-3.3), Leaf(55, 54, 21, 9, -1.7, 'wing', z=-3.1),
    star(89, 52, 7, 'star', z=-1.8), star(80, 44, 4.5, 'star', z=-1.85),
    Cap(84, 58, 86, 55, 2, 1.6, 'accent', z=-1.9),
] + quad('pointy', 'long', eye='round', mouth='smile', leg=1.25, neck=3) + [
    # ear tufts
    Tri([(28, 29), (26.5, 20), (31.5, 27)], 'accent', z=2.55), Tri([(52.5, 26), (56, 17), (55.5, 27)], 'accent', z=2.55),
    # crescent gem, blush
    Spot(41, 42, 2.5, 'gem', z=3.6, view='front'), Spot(40.3, 41.2, 0.8, 'belly', z=3.7, view='front'),
    Spot(30.5, 53, 2.4, 'inner', z=3.5, view='front'), Spot(50.5, 52.5, 2.4, 'inner', z=3.5, view='front'),
    # a sparkle on the chest
    star(40, 70, 3.2, 'star', z=1.2)], s=1.05))

# 105. seraphelis -- a haloed, many-winged celestial lynx with a starlight mane and a comet tail
_wings = []
for k, (ang, ln, wd) in enumerate([(-1.95, 30, 10), (-1.55, 38, 12), (-1.15, 40, 13), (-0.75, 34, 12), (-0.4, 26, 10)]):
    _wings.append(Leaf(58, 54, ln, wd, ang, 'wing', z=-3 - k * 0.05))
    _wings.append(Leaf(58, 54, ln * 0.62, wd * 0.6, ang, 'wing2', z=-2.95 - k * 0.05, vein=False))
_halo = [Spot(41 + 11 * math.cos(a / 10 * math.tau), 18 + 3.4 * math.sin(a / 10 * math.tau), 1.5, 'star', z=2.45) for a in range(10)]
NEW['seraphelis'] = (dict(body='#fff6ff', belly='#ffffff', accent='#ffc2ea', inner='#ff9fd6', nose='#d0508a', flame='#ffe27a',
                          wing='#c4e6ff', wing2='#8cc6ff', gem='#9a5cff', star='#ffe27a'), T(_wings + _halo + [
    star(84, 38, 5.5, 'star', z=-1.5),
] + quad('pointy', 'flame', eye='round', mouth='smile', leg=1.45, neck=6, mane=True) + [
    Tri([(27, 26), (25, 16), (30.5, 24)], 'accent', z=2.55), Tri([(51.5, 23), (55.5, 13), (55, 24)], 'accent', z=2.55),
    Spot(41, 39, 3, 'gem', z=3.6, view='front'), Spot(40.2, 38, 1, 'belly', z=3.7, view='front'),
    Spot(30.5, 50, 2.4, 'inner', z=3.5, view='front'), Spot(50.5, 49.5, 2.4, 'inner', z=3.5, view='front'),
    star(40, 67, 4.2, 'star', z=1.2)], s=1.12, dy=0))
