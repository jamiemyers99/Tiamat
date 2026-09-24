// Every Morph species in the Riven Reach.
// base: [HP, Atk, Def, SpA, SpD, Spe]   growth: fast | medium | slow | erratic-free
// evo: { level, into }    learn: [[level, moveId], ...]   (level 1 = starting moves)
import { MOVES } from './moves.js';

export const SPECIES = {};
const LIST = [];

function s(num, id, name, types, base, growth, xp, cat, evo, learn, cls, dex) {
  const sp = { num, id, name, types, base, growth, xp, catch: cat, evo, learn, cls, dex };
  SPECIES[id] = sp;
  LIST.push(sp);
}

// ── Starters ────────────────────────────────────────────────────────────────
s(1, 'spriglet', 'Spriglet', ['Nature'], [50, 52, 52, 55, 55, 46], 'medium', 64, 45, { level: 16, into: 'spriggrove' },
  [[1, 'sprout_tackle'], [1, 'petal_cloak'], [6, 'bramble_whip'], [10, 'pebble_seed'], [14, 'verdant_pulse'], [19, 'grove_renewal'], [24, 'rootquake']],
  'Sapling Morph', 'A shy sapling-Morph that shelters in mossy hollows. The leaves on its head turn toward kind voices.');
s(2, 'spriggrove', 'Spriggrove', ['Nature'], [60, 64, 66, 72, 70, 58], 'medium', 142, 45, { level: 34, into: 'mosswarden' },
  [[1, 'sprout_tackle'], [1, 'bramble_whip'], [1, 'pebble_seed'], [16, 'verdant_pulse'], [20, 'petal_cloak'], [24, 'grove_renewal'], [28, 'rootquake'], [33, 'ancient_canopy']],
  'Grove Morph', 'Dense foliage shields its body. Small birds nest in its branches without fear.');
s(3, 'mosswarden', 'Mosswarden', ['Nature', 'Stone'], [85, 90, 100, 90, 90, 70], 'medium', 236, 45, null,
  [[1, 'verdant_pulse'], [1, 'rootquake'], [1, 'petal_cloak'], [34, 'grove_renewal'], [40, 'ancient_canopy'], [46, 'monolith_crash']],
  'Guardian Morph', 'An ancient guardian cloaked in living moss and boulder-plate. Wild Morphs grow calm in its shade.');

s(4, 'cindlet', 'Cindlet', ['Ember'], [39, 55, 40, 58, 45, 66], 'medium', 62, 45, { level: 16, into: 'cindreaver' },
  [[1, 'cinder_pounce'], [1, 'sulk_smoke'], [6, 'ember_fang'], [10, 'shadow_spark'], [14, 'blaze_mane'], [19, 'dusk_ignite'], [24, 'umbral_flare']],
  'Cinder Morph', 'A hot-headed little Morph that always charges in head first. Its tail-flame flickers when it sulks.');
s(5, 'cindreaver', 'Cindreaver', ['Ember'], [58, 72, 55, 78, 58, 82], 'medium', 142, 45, { level: 36, into: 'pyromane' },
  [[1, 'cinder_pounce'], [1, 'ember_fang'], [1, 'shadow_spark'], [16, 'blaze_mane'], [20, 'sulk_smoke'], [24, 'dusk_ignite'], [29, 'umbral_flare'], [35, 'black_pyre']],
  'Blaze Morph', 'Its blazing mane marks it as a force to respect. It hunts at dusk, when its fire is hardest to see.');
s(6, 'pyromane', 'Pyromane', ['Ember', 'Umbra'], [76, 100, 74, 104, 74, 100], 'medium', 240, 45, null,
  [[1, 'ember_fang'], [1, 'blaze_mane'], [1, 'umbral_flare'], [36, 'dusk_ignite'], [40, 'nightfire_rend'], [46, 'black_pyre']],
  'Pyre Morph', 'Pyromane burns with a black-cored flame. Rivals say its roar alone can scorch a hillside.');

s(7, 'puddlet', 'Puddlet', ['Tide'], [48, 50, 58, 52, 55, 44], 'medium', 63, 45, { level: 16, into: 'torrentide' },
  [[1, 'puddle_hop'], [1, 'drizzle_eyes'], [6, 'bubble_snap'], [10, 'rime_splash'], [14, 'riptide_fang'], [19, 'current_coat'], [24, 'glacier_surge']],
  'Pup Morph', 'A gentle water-pup whose fur is always damp. It shakes itself dry on anyone it likes.');
s(8, 'torrentide', 'Torrentide', ['Tide'], [66, 68, 76, 68, 70, 58], 'medium', 142, 45, { level: 36, into: 'maelstrand' },
  [[1, 'puddle_hop'], [1, 'bubble_snap'], [1, 'rime_splash'], [16, 'riptide_fang'], [20, 'drizzle_eyes'], [24, 'current_coat'], [29, 'glacier_surge'], [35, 'maelstrom']],
  'Current Morph', 'Its wake floods riverbanks after battle. It can hold its breath for an entire afternoon.');
s(9, 'maelstrand', 'Maelstrand', ['Tide', 'Frost'], [92, 95, 95, 88, 90, 68], 'medium', 240, 45, null,
  [[1, 'riptide_fang'], [1, 'glacier_surge'], [1, 'current_coat'], [36, 'rime_splash'], [42, 'maelstrom'], [48, 'permafrost_breath']],
  'Maelstrom Morph', 'It turns the sea to slush with a sweep of its tail. Northern fishers leave it the first of every catch.');

// ── Common early Morphs ─────────────────────────────────────────────────────
s(10, 'nibbit', 'Nibbit', ['Plain'], [35, 50, 35, 25, 35, 70], 'fast', 51, 255, { level: 18, into: 'gnawbit' },
  [[1, 'bump'], [1, 'gruff_bark'], [5, 'flit_strike'], [9, 'nip'], [14, 'rally_cry'], [20, 'pummel'], [26, 'shade_fang'], [32, 'ram_charge']],
  'Nibble Morph', 'Its front teeth never stop growing, so it gnaws on everything — fence posts included.');
s(11, 'gnawbit', 'Gnawbit', ['Plain'], [60, 80, 60, 45, 62, 95], 'fast', 140, 127, null,
  [[1, 'nip'], [1, 'flit_strike'], [14, 'rally_cry'], [22, 'pummel'], [28, 'shade_fang'], [34, 'ram_charge'], [40, 'grand_slam']],
  'Nibble Morph', 'Gnawbit colonies dig warrens so deep that whole hillsides slowly sink.');
s(12, 'trotter', 'Trotter', ['Plain'], [45, 52, 45, 30, 40, 60], 'medium', 58, 200, { level: 22, into: 'trotterion' },
  [[1, 'bump'], [1, 'stern_look'], [6, 'flit_strike'], [10, 'nip'], [15, 'ram_charge'], [21, 'rally_cry'], [27, 'power_kick'], [33, 'grand_slam']],
  'Pony Morph', 'A compact runner that can outpace most foes on open ground. It sleeps standing up.');
s(13, 'trotterion', 'Trotterion', ['Plain'], [75, 88, 70, 45, 62, 85], 'medium', 150, 90, null,
  [[1, 'ram_charge'], [1, 'flit_strike'], [21, 'rally_cry'], [28, 'power_kick'], [34, 'grand_slam'], [40, 'quake_stomp']],
  'Stallion Morph', 'Its proud bearing earns it respect on any road. It remembers every rider who treated it well.');
s(14, 'beakling', 'Beakling', ['Wing'], [40, 45, 40, 35, 35, 56], 'medium', 55, 255, { level: 18, into: 'skyveer' },
  [[1, 'bump'], [1, 'gruff_bark'], [5, 'nip'], [9, 'breeze_cut'], [13, 'beak_jab'], [17, 'updraft'], [23, 'wing_strike'], [30, 'gale_slice']],
  'Chick Morph', 'A plucky chick that circles high and dives on anything shiny.');
s(15, 'skyveer', 'Skyveer', ['Wing'], [63, 65, 58, 50, 52, 80], 'medium', 122, 120, { level: 36, into: 'tempestral' },
  [[1, 'beak_jab'], [1, 'breeze_cut'], [17, 'updraft'], [24, 'wing_strike'], [30, 'gale_slice'], [34, 'sky_dive']],
  'Glider Morph', 'Its wingspan has doubled. It rides thermals over the ridges for hours without a flap.');
s(16, 'tempestral', 'Tempestral', ['Wing'], [80, 95, 75, 85, 70, 105], 'medium', 216, 45, null,
  [[1, 'wing_strike'], [1, 'sky_dive'], [36, 'tempest_wing'], [40, 'eye_of_the_storm'], [42, 'gale_slice'], [48, 'skybolt']],
  'Storm Morph', 'Tempestral commands the weather it flies through. Its cry triggers sudden downpours.');
s(17, 'chittik', 'Chittik', ['Swarm'], [40, 45, 45, 25, 30, 45], 'fast', 53, 255, { level: 14, into: 'mantipule' },
  [[1, 'mandible_nip'], [1, 'silk_snare'], [7, 'pin_volley'], [11, 'bump'], [16, 'sap_sting'], [21, 'swarm_strike'], [27, 'palm_strike']],
  'Beetle Morph', 'A chitinous little Morph with clacking mandibles. It never, ever stops moving.');
s(18, 'mantipule', 'Mantipule', ['Swarm', 'Brawl'], [60, 85, 60, 40, 55, 80], 'fast', 145, 90, { level: 36, into: 'mantiscythe' },
  [[1, 'pin_volley'], [1, 'palm_strike'], [16, 'sap_sting'], [20, 'counterblow'], [24, 'swarm_strike'], [30, 'battle_stance'], [36, 'power_kick'], [42, 'all_out_slam']],
  'Mantis Morph', 'Razor forearms can slice through bark in one swipe. It bows before every fight.');
s(19, 'fuzzling', 'Fuzzling', ['Swarm'], [45, 30, 40, 45, 50, 40], 'fast', 55, 255, { level: 20, into: 'mothlume' },
  [[1, 'bump'], [1, 'silk_snare'], [6, 'mandible_nip'], [10, 'drowse_pollen'], [15, 'psy_blast'], [21, 'drone_hum'], [26, 'daze_beam']],
  'Larva Morph', 'A fluffy caterpillar that curls into a ball when startled. Its fuzz makes Morphs sneeze.');
s(20, 'mothlume', 'Mothlume', ['Swarm', 'Mind'], [65, 45, 60, 85, 80, 80], 'fast', 160, 90, null,
  [[1, 'psy_blast'], [1, 'drowse_pollen'], [21, 'drone_hum'], [26, 'daze_beam'], [31, 'clear_thought'], [36, 'mind_spike'], [42, 'trance']],
  'Lantern Morph', 'The eyespots on its wings glow softly at night. Lost travellers follow them home.');
s(21, 'burrlet', 'Burrlet', ['Nature'], [50, 45, 55, 40, 45, 35], 'medium', 60, 190, { level: 20, into: 'thornbur' },
  [[1, 'bump'], [1, 'leaf_nick'], [6, 'root_snare'], [10, 'vine_lash'], [15, 'brace'], [20, 'seed_volley'], [26, 'sap_drain']],
  'Burr Morph', 'A round, prickly Morph that clings to fur and clothing. Surprisingly affectionate once tamed.');
s(22, 'thornbur', 'Thornbur', ['Nature'], [75, 80, 90, 55, 65, 45], 'medium', 150, 90, null,
  [[1, 'vine_lash'], [1, 'brace'], [20, 'seed_volley'], [27, 'sap_drain'], [33, 'timber_crash'], [39, 'moss_shield']],
  'Bramble Morph', 'Thornbur roll downhill in autumn, collecting seeds they plant in spring.');
s(23, 'sporra', 'Sporra', ['Nature', 'Toxin'], [45, 40, 50, 55, 55, 30], 'medium', 60, 190, { level: 24, into: 'mycelord' },
  [[1, 'bump'], [1, 'acid_spit'], [7, 'drowse_pollen'], [11, 'leaf_nick'], [16, 'sap_drain'], [22, 'blight_cloud'], [28, 'mire_blast']],
  'Mushroom Morph', 'It grows in the damp dark under fallen logs. Its cap puffs out a sleepy haze.');
s(24, 'mycelord', 'Mycelord', ['Nature', 'Toxin'], [75, 60, 75, 90, 85, 45], 'medium', 158, 75, null,
  [[1, 'sap_drain'], [1, 'acid_spit'], [22, 'blight_cloud'], [28, 'mire_blast'], [28, 'mycelial_surge'], [34, 'bloom_blast'], [40, 'heal_bud']],
  'Fungus Morph', 'An entire forest floor can be one Mycelord, connected underground by threads of mycelium.');
s(25, 'voltquill', 'Voltquill', ['Static'], [40, 55, 35, 50, 40, 85], 'medium', 82, 45, { level: 25, into: 'fulmirex' },
  [[1, 'bump'], [1, 'static_jolt'], [7, 'flit_strike'], [11, 'volt_needle'], [16, 'numb_pulse'], [21, 'charge_ram'], [28, 'thunder_arc']],
  'Quill Morph', 'Extremely rare. Each of its quills can discharge a spark on its own.');
s(26, 'fulmirex', 'Fulmirex', ['Static'], [58, 75, 55, 75, 60, 100], 'medium', 150, 45, { level: 40, into: 'arcfowl' },
  [[1, 'volt_needle'], [1, 'charge_ram'], [26, 'thunder_arc'], [32, 'overcharge'], [38, 'skybolt']],
  'Storm Quill Morph', 'Fulmirex carries a permanent static field. Compasses spin wildly near its den.');
s(27, 'arcfowl', 'Arcfowl', ['Static', 'Wing'], [75, 95, 70, 100, 75, 115], 'medium', 230, 20, null,
  [[1, 'thunder_arc'], [1, 'wing_strike'], [40, 'skybolt'], [44, 'sky_dive'], [44, 'thunderwing'], [48, 'tempest_wing']],
  'Lightning Morph', 'Legend says Arcfowl guided sailors home through storms by riding the lightning.');
s(28, 'pebbling', 'Pebbling', ['Stone'], [50, 60, 75, 25, 35, 25], 'slow', 60, 190, { level: 25, into: 'cragmaul' },
  [[1, 'bump'], [1, 'brace'], [6, 'stone_toss'], [11, 'grit_spray'], [16, 'rubble_fall'], [22, 'stoneskin'], [28, 'quake_stomp']],
  'Pebble Morph', 'A round, slow Morph with a deceptively tough shell. Hikers trip over sleeping Pebbling constantly.');
s(29, 'cragmaul', 'Cragmaul', ['Stone', 'Brawl'], [75, 105, 110, 40, 60, 35], 'slow', 170, 75, { level: 44, into: 'montolith' },
  [[1, 'rubble_fall'], [1, 'palm_strike'], [26, 'stoneskin'], [30, 'quake_stomp'], [36, 'power_kick'], [42, 'boulder_drop'], [48, 'all_out_slam']],
  'Boulder Morph', 'Its granite fists can shatter boulders. It rarely moves unless provoked.');
s(30, 'oozelet', 'Oozelet', ['Toxin'], [55, 45, 45, 45, 50, 40], 'medium', 60, 190, { level: 26, into: 'vexgore' },
  [[1, 'bump'], [1, 'acid_spit'], [8, 'corrode'], [13, 'toxic_fang'], [19, 'blight_cloud'], [25, 'mire_blast']],
  'Ooze Morph', 'A dripping blob of toxins. Its slime trail slowly eats through stone.');
s(31, 'vexgore', 'Vexgore', ['Toxin', 'Umbra'], [80, 85, 70, 70, 70, 65], 'medium', 160, 75, null,
  [[1, 'toxic_fang'], [1, 'shade_fang'], [26, 'blight_cloud'], [30, 'noxious_jab'], [35, 'mire_blast'], [40, 'nightrend']],
  'Venom Morph', 'It secretes a venom that makes foes drowsy and sluggish. Even Deepcall acolytes handle it with gloves.');
s(32, 'nyxen', 'Nyxen', ['Umbra'], [45, 55, 40, 55, 45, 65], 'medium', 60, 45, { level: 24, into: 'vesperel' },
  [[1, 'shade_fang'], [1, 'flit_strike'], [10, 'night_tremor'], [14, 'hex_mist'], [19, 'dread_gaze'], [25, 'ambush'], [30, 'shadow_creep']],
  'Dusk Morph', 'Nyxen is shy around strangers but fiercely loyal to its Tamer. Its eyes shine in any dark.');
s(33, 'vesperel', 'Vesperel', ['Umbra'], [62, 72, 58, 75, 62, 82], 'medium', 150, 45, { level: 42, into: 'noctheart' },
  [[1, 'shade_fang'], [1, 'hex_mist'], [25, 'ambush'], [28, 'dusk_hunt'], [30, 'shadow_creep'], [36, 'psy_blast'], [40, 'nightrend']],
  'Twilight Morph', 'Vesperel moves in near silence along moonlit roads and fog-filled valleys.');
s(34, 'noctheart', 'Noctheart', ['Umbra', 'Mind'], [80, 90, 72, 105, 85, 98], 'medium', 240, 45, null,
  [[1, 'shadow_creep'], [1, 'mind_spike'], [42, 'nightrend'], [46, 'clear_thought'], [46, 'heartless_night'], [50, 'dread_gaze']],
  'Nightmind Morph', 'Noctheart reads the deepest fears of its opponents — and sings them softly back.');

// ── Coast ──────────────────────────────────────────────────────────────────
s(35, 'gullip', 'Gullip', ['Tide', 'Wing'], [42, 40, 35, 50, 35, 70], 'medium', 64, 190, { level: 25, into: 'stormgull' },
  [[1, 'splash_drop'], [1, 'gruff_bark'], [8, 'breeze_cut'], [13, 'rip_current'], [19, 'wing_strike'], [26, 'tide_pulse'], [32, 'gale_slice']],
  'Gull Morph', 'Gullip steal chips from fishermen, then drop them for the fishermen\'s children.');
s(36, 'stormgull', 'Stormgull', ['Tide', 'Wing'], [65, 60, 60, 90, 70, 90], 'medium', 158, 75, null,
  [[1, 'wing_strike'], [1, 'tide_pulse'], [26, 'gale_slice'], [32, 'hydro_burst'], [38, 'tempest_wing']],
  'Squall Morph', 'It skims wave-tops in storms that keep every boat in harbour.');
s(37, 'crabbit', 'Crabbit', ['Tide'], [45, 65, 80, 30, 40, 35], 'medium', 62, 190, { level: 28, into: 'pincerock' },
  [[1, 'bump'], [1, 'brace'], [7, 'splash_drop'], [12, 'nip'], [18, 'brine_fang'], [24, 'stone_toss'], [30, 'undertow']],
  'Crab Morph', 'Crabbit walk sideways into battle so they can keep one claw ready.');
s(38, 'pincerock', 'Pincerock', ['Tide', 'Stone'], [70, 100, 115, 45, 60, 45], 'medium', 165, 75, null,
  [[1, 'brine_fang'], [1, 'stone_toss'], [28, 'rubble_fall'], [32, 'undertow'], [32, 'crushing_claw'], [38, 'stoneskin'], [44, 'boulder_drop']],
  'Reef Morph', 'Barnacles grow thick on its shell. Old Pincerock are mistaken for reefs.');
s(39, 'jellume', 'Jellume', ['Tide', 'Toxin'], [50, 35, 40, 60, 70, 60], 'medium', 64, 190, { level: 30, into: 'medusheen' },
  [[1, 'splash_drop'], [1, 'acid_spit'], [9, 'numb_pulse'], [15, 'tide_pulse'], [21, 'blight_cloud'], [28, 'mire_blast']],
  'Jelly Morph', 'It drifts with the tide, glowing faintly. Swimmers keep a wary distance.');
s(40, 'medusheen', 'Medusheen', ['Tide', 'Toxin'], [80, 55, 65, 90, 115, 75], 'medium', 170, 60, null,
  [[1, 'tide_pulse'], [1, 'mire_blast'], [30, 'hydro_burst'], [34, 'siren_sting'], [36, 'clear_thought'], [42, 'mind_spike']],
  'Glass Bell Morph', 'Its trailing veils are beautiful and agonising in equal measure.');

// ── Mines & mountains ──────────────────────────────────────────────────────
s(41, 'ferrite', 'Ferrite', ['Iron'], [45, 55, 75, 35, 45, 40], 'medium', 64, 150, { level: 30, into: 'ferroclad' },
  [[1, 'bump'], [1, 'brace'], [7, 'chrome_claw'], [12, 'stone_toss'], [18, 'cog_strike'], [24, 'plate_up'], [30, 'alloy_lash']],
  'Ore Morph', 'Ferrite feed on iron ore and leave tidy tunnels behind them. Miners consider them lucky.');
s(42, 'ferroclad', 'Ferroclad', ['Iron', 'Stone'], [80, 95, 125, 55, 70, 45], 'medium', 180, 60, null,
  [[1, 'alloy_lash'], [1, 'rubble_fall'], [30, 'plate_up'], [34, 'quake_stomp'], [34, 'bulwark_charge'], [40, 'anvil_drop'], [46, 'boulder_drop']],
  'Bastion Morph', 'Its plated body rings like a bell when struck.');
s(43, 'echirp', 'Echirp', ['Umbra', 'Wing'], [40, 45, 35, 40, 40, 65], 'medium', 58, 255, { level: 24, into: 'duskwing' },
  [[1, 'nip'], [1, 'breeze_cut'], [6, 'shade_fang'], [11, 'daze_beam'], [16, 'wing_strike'], [21, 'hex_mist'], [27, 'ambush']],
  'Echo Morph', 'It maps caves with tiny clicks and never bumps into anything — except Tamers.');
s(44, 'duskwing', 'Duskwing', ['Umbra', 'Wing'], [70, 75, 65, 65, 70, 100], 'medium', 160, 90, null,
  [[1, 'wing_strike'], [1, 'shade_fang'], [24, 'hex_mist'], [29, 'ambush'], [34, 'sky_dive'], [40, 'nightrend']],
  'Night Glider Morph', 'Colonies of Duskwing blot out the moon when they leave the mines at dusk.');
s(45, 'tunnip', 'Tunnip', ['Stone'], [40, 60, 50, 25, 40, 55], 'medium', 60, 190, { level: 28, into: 'borebeast' },
  [[1, 'bump'], [1, 'grit_spray'], [8, 'mud_lob'], [13, 'nip'], [19, 'rubble_fall'], [25, 'quake_stomp']],
  'Mole Morph', 'Tunnip surface only to sneeze. The rest of their lives are spent underground.');
s(46, 'borebeast', 'Borebeast', ['Stone', 'Iron'], [75, 105, 80, 40, 60, 75], 'medium', 170, 75, null,
  [[1, 'rubble_fall'], [1, 'chrome_claw'], [28, 'quake_stomp'], [32, 'tunnel_quake'], [33, 'cog_strike'], [39, 'anvil_drop'], [45, 'boulder_drop']],
  'Drill Morph', 'Its spiralled iron claws can bore through bedrock faster than any machine in Gearhollow.');
s(47, 'coilbit', 'Coilbit', ['Static', 'Iron'], [40, 35, 65, 70, 55, 45], 'medium', 65, 190, { level: 30, into: 'coilossus' },
  [[1, 'static_jolt'], [1, 'brace'], [8, 'numb_pulse'], [13, 'chrome_claw'], [19, 'charge_ram'], [25, 'gleam_cannon'], [31, 'thunder_arc']],
  'Magnet Morph', 'Coilbit cling to machinery and hum happily. Engineers find them in every generator.');
s(48, 'coilossus', 'Coilossus', ['Static', 'Iron'], [70, 60, 95, 115, 80, 60], 'medium', 175, 60, null,
  [[1, 'thunder_arc'], [1, 'gleam_cannon'], [30, 'overcharge'], [34, 'tesla_coil'], [36, 'plate_up'], [42, 'skybolt']],
  'Dynamo Morph', 'Several Coilbit fused into a humming colossus. It can power a whole town for a night.');
s(49, 'pugnet', 'Pugnet', ['Brawl'], [55, 70, 45, 30, 40, 55], 'medium', 62, 180, { level: 28, into: 'pugilus' },
  [[1, 'bump'], [1, 'stern_look'], [6, 'counterblow'], [11, 'palm_strike'], [17, 'knuckle_barrage'], [23, 'battle_stance'], [29, 'power_kick']],
  'Scrapper Morph', 'Pugnet challenge anything bigger than themselves, which is nearly everything.');
s(50, 'pugilus', 'Pugilus', ['Brawl'], [85, 115, 75, 40, 70, 80], 'medium', 172, 75, null,
  [[1, 'power_kick'], [1, 'counterblow'], [28, 'battle_stance'], [32, 'haymaker'], [34, 'knuckle_barrage'], [40, 'all_out_slam'], [46, 'quake_stomp']],
  'Champion Morph', 'Pugilus bow to their opponents before and after every fight — win or lose.');

// ── Moor ───────────────────────────────────────────────────────────────────
s(51, 'omenet', 'Omenet', ['Mind'], [45, 30, 45, 65, 60, 50], 'medium', 64, 190, { level: 32, into: 'augurine' },
  [[1, 'bump'], [1, 'daze_beam'], [8, 'psy_blast'], [14, 'trance'], [20, 'clear_thought'], [27, 'mind_spike']],
  'Omen Morph', 'Omenet stare at the horizon before storms. Moor folk read the weather from where they face.');
s(52, 'augurine', 'Augurine', ['Mind'], [70, 50, 70, 110, 95, 85], 'medium', 172, 60, null,
  [[1, 'psy_blast'], [1, 'trance'], [32, 'mind_spike'], [38, 'clear_thought'], [44, 'hex_mist']],
  'Seer Morph', 'It is said Augurine can see one day into the future — but only on foggy mornings.');
s(53, 'pookit', 'Pookit', ['Umbra'], [45, 60, 40, 40, 40, 65], 'medium', 62, 190, { level: 32, into: 'pookavar' },
  [[1, 'nip'], [1, 'gruff_bark'], [7, 'shade_fang'], [12, 'flit_strike'], [18, 'ambush'], [24, 'hex_mist'], [30, 'nightrend']],
  'Trickster Morph', 'A shape-shifting moor Morph. It likes to appear as a lost foal and lead walkers in circles.');
s(54, 'pookavar', 'Pookavar', ['Umbra', 'Brawl'], [80, 110, 70, 60, 65, 95], 'medium', 175, 60, null,
  [[1, 'nightrend'], [1, 'power_kick'], [32, 'ambush'], [37, 'battle_stance'], [43, 'all_out_slam']],
  'Night Steed Morph', 'On moonless nights it gallops across the bog, and no fence can hold it.');
s(55, 'cairnite', 'Cairnite', ['Stone', 'Umbra'], [70, 75, 110, 60, 90, 20], 'slow', 150, 45, null,
  [[1, 'stone_toss'], [1, 'night_tremor'], [15, 'stoneskin'], [25, 'hex_mist'], [35, 'rubble_fall'], [45, 'shadow_creep']],
  'Menhir Morph', 'A standing stone that wandered off. Moor folk count their stones every morning.');

// ── Frost ──────────────────────────────────────────────────────────────────
s(56, 'chillcub', 'Chillcub', ['Frost'], [55, 60, 50, 40, 45, 40], 'medium', 64, 150, { level: 33, into: 'glaciursa' },
  [[1, 'bump'], [1, 'gruff_bark'], [7, 'chill_nip'], [12, 'nip'], [18, 'icicle_jab'], [24, 'brace'], [30, 'hail_volley']],
  'Frost Cub Morph', 'Chillcub lick icicles for fun and sulk when spring arrives.');
s(57, 'glaciursa', 'Glaciursa', ['Frost', 'Brawl'], [100, 115, 85, 55, 70, 50], 'medium', 180, 60, null,
  [[1, 'icicle_jab'], [1, 'palm_strike'], [33, 'hail_volley'], [37, 'glacier_maul'], [38, 'power_kick'], [44, 'all_out_slam'], [50, 'whiteout_gale']],
  'Glacier Bear Morph', 'It carves dens into glaciers with its bare paws and sleeps through blizzards.');
s(58, 'flurrit', 'Flurrit', ['Frost', 'Wing'], [60, 55, 55, 80, 65, 95], 'medium', 150, 60, null,
  [[1, 'breeze_cut'], [1, 'chill_nip'], [20, 'wing_strike'], [26, 'rime_ray'], [32, 'updraft'], [40, 'whiteout_gale']],
  'Snowflake Morph', 'No two Flurrit have the same wing pattern. They dance in the first snowfall of the year.');

// ── Drake ──────────────────────────────────────────────────────────────────
s(59, 'wyrmkin', 'Wyrmkin', ['Drake'], [45, 64, 45, 50, 45, 50], 'slow', 67, 45, { level: 30, into: 'wyrmguard' },
  [[1, 'nip'], [1, 'stern_look'], [8, 'wyrm_breath'], [14, 'coil_whip'], [20, 'scale_rake'], [26, 'draconic_surge']],
  'Hatchling Morph', 'Wyrmkin hatch in the warm stone near the Riven. They are believed to be Tiamat\'s distant kin.');
s(60, 'wyrmguard', 'Wyrmguard', ['Drake'], [65, 84, 70, 70, 65, 70], 'slow', 150, 45, { level: 45, into: 'riftwyrm' },
  [[1, 'wyrm_breath'], [1, 'coil_whip'], [30, 'scale_rake'], [35, 'draconic_surge'], [40, 'quake_stomp']],
  'Sentinel Morph', 'It coils around nests of eggs that are not its own and guards them fiercely.');
s(61, 'riftwyrm', 'Riftwyrm', ['Drake', 'Stone'], [95, 130, 95, 90, 85, 90], 'slow', 270, 45, null,
  [[1, 'scale_rake'], [1, 'quake_stomp'], [45, 'rift_nova'], [49, 'riftbreaker'], [50, 'boulder_drop'], [55, 'draconic_surge']],
  'Rift Dragon Morph', 'When Riftwyrm roar, the walls of the Riven answer with an echo that lasts a full minute.');

// ── More ───────────────────────────────────────────────────────────────────
s(62, 'glowick', 'Glowick', ['Ember', 'Swarm'], [40, 40, 40, 60, 45, 60], 'medium', 60, 190, { level: 26, into: 'blazewing' },
  [[1, 'ember_spark'], [1, 'silk_snare'], [6, 'mandible_nip'], [11, 'smoke_veil'], [16, 'blaze_ring'], [22, 'drone_hum']],
  'Wick Morph', 'A firefly whose tail is a tiny candle. Forest children catch them in jars and let them go at dawn.');
s(63, 'blazewing', 'Blazewing', ['Ember', 'Swarm'], [70, 60, 60, 100, 70, 95], 'medium', 165, 75, null,
  [[1, 'blaze_ring'], [1, 'drone_hum'], [26, 'updraft'], [31, 'inferno_lash'], [37, 'swarm_strike']],
  'Beacon Morph', 'A swarm of Blazewing can light up a whole valley. Sailors once mistook them for a lighthouse.');
s(64, 'lambkin', 'Lambkin', ['Plain'], [55, 40, 50, 40, 50, 35], 'fast', 58, 190, { level: 28, into: 'rammoth' },
  [[1, 'bump'], [1, 'lullaby'], [7, 'stern_look'], [12, 'ram_charge'], [18, 'brace'], [24, 'clamor']],
  'Fleece Morph', 'Its wool is warm and endlessly regrowing. Farms in the Reach keep a few for luck.');
s(65, 'rammoth', 'Rammoth', ['Plain', 'Frost'], [95, 95, 90, 55, 75, 50], 'fast', 170, 75, null,
  [[1, 'ram_charge'], [1, 'icicle_jab'], [28, 'brace'], [32, 'mammoth_stampede'], [33, 'clamor'], [38, 'grand_slam'], [44, 'whiteout_gale']],
  'Mammoth Ram Morph', 'Herds of Rammoth break trails through the snow of the Rimepass every winter.');
s(66, 'hushling', 'Hushling', ['Wing', 'Mind'], [50, 35, 45, 55, 55, 50], 'medium', 62, 190, { level: 30, into: 'strixage' },
  [[1, 'beak_jab'], [1, 'trance'], [8, 'breeze_cut'], [13, 'daze_beam'], [19, 'psy_blast'], [25, 'wing_strike']],
  'Owlet Morph', 'Hushling are only seen at night. They turn their heads almost all the way around.');
s(67, 'strixage', 'Strixage', ['Wing', 'Mind'], [80, 55, 70, 95, 90, 70], 'medium', 170, 75, null,
  [[1, 'psy_blast'], [1, 'wing_strike'], [30, 'mind_spike'], [34, 'moonlit_riddle'], [35, 'gale_slice'], [40, 'clear_thought'], [46, 'tempest_wing']],
  'Sage Owl Morph', 'Strixage roost in libraries and ruins. Scholars leave candles burning for them.');

// ── Legendary ──────────────────────────────────────────────────────────────
s(68, 'tiamat', 'Tiamat', ['Drake', 'Tide'], [105, 95, 100, 135, 110, 90], 'slow', 306, 3, null,
  [[1, 'primordial_tide'], [1, 'scale_rake'], [1, 'rift_nova'], [1, 'mend'], [60, 'hydro_burst'], [70, 'draconic_surge']],
  'Draco Queen Morph', 'The first sea, given a shape. The old songs say the whole Reach was made from her sundered body — and that she only sleeps.');

// ── New Morphs (69–102) ─────────────────────────────────────────────────────
// Toxin frog line
s(69, 'pipfrog', 'Pipfrog', ['Toxin'], [45, 40, 40, 50, 45, 55], 'medium', 58, 200, { level: 18, into: 'croakmire' },
  [[1, 'bump'], [1, 'acid_spit'], [5, 'splash_drop'], [9, 'corrode'], [13, 'toxic_fang'], [17, 'tide_pulse'], [22, 'blight_cloud']],
  'Poison Frog Morph', 'Its huge eyes never blink. The lime spots on its back taste terrible — which is exactly the point.');
s(70, 'croakmire', 'Croakmire', ['Toxin', 'Tide'], [70, 62, 65, 75, 65, 60], 'medium', 142, 100, { level: 34, into: 'blightoad' },
  [[1, 'acid_spit'], [1, 'toxic_fang'], [18, 'tide_pulse'], [22, 'venom_lash'], [27, 'blight_cloud'], [31, 'mire_blast'], [36, 'undertow']],
  'Bog Toad Morph', 'It puffs its throat sac to boom across the marsh. The louder the croak, the more it thinks it owns the place.');
s(71, 'blightoad', 'Blightoad', ['Toxin', 'Tide'], [100, 85, 90, 105, 90, 60], 'medium', 236, 45, null,
  [[1, 'mire_blast'], [1, 'venom_lash'], [34, 'noxious_jab'], [38, 'hydro_burst'], [38, 'plague_tide'], [42, 'corrode'], [47, 'toxic_torrent']],
  'Plague King Morph', 'Whole swamps turn sickly green where Blightoad squats. Its glowing drool can melt a rowing boat.');
// Brawl kangaroo line
s(72, 'pawpunch', 'Pawpunch', ['Brawl'], [50, 60, 40, 25, 35, 55], 'medium', 58, 190, { level: 20, into: 'knuckroo' },
  [[1, 'bump'], [1, 'counterblow'], [5, 'gruff_bark'], [9, 'palm_strike'], [14, 'knuckle_barrage'], [19, 'battle_stance'], [24, 'power_kick']],
  'Sparring Morph', 'Pawpunch practise jabs on anything that moves — butterflies, leaves, their own tails. They always shake hands after.');
s(73, 'knuckroo', 'Knuckroo', ['Brawl'], [75, 90, 60, 40, 55, 85], 'medium', 145, 90, { level: 38, into: 'gauntlord' },
  [[1, 'palm_strike'], [1, 'knuckle_barrage'], [20, 'counterblow'], [24, 'power_kick'], [29, 'battle_stance'], [33, 'rising_uppercut'], [40, 'all_out_slam']],
  'Boxer Morph', 'It bounces on its tail between punches. A Knuckroo never throws the first blow — but it always throws the last.');
s(74, 'gauntlord', 'Gauntlord', ['Brawl', 'Iron'], [100, 130, 95, 50, 80, 75], 'medium', 240, 45, null,
  [[1, 'rising_uppercut'], [1, 'chrome_claw'], [38, 'plate_up'], [42, 'steel_ram'], [42, 'champions_gauntlet'], [46, 'all_out_slam'], [52, 'anvil_drop']],
  'Champion Morph', 'Gauntlord forges its own steel gauntlets from fallen armour. The scar across its brow is from the only fight it lost.');
// Mind cat line
s(75, 'wispurr', 'Wispurr', ['Mind'], [45, 35, 40, 60, 55, 60], 'medium', 60, 190, { level: 22, into: 'mystaline' },
  [[1, 'bump'], [1, 'psi_wave'], [6, 'lullaby'], [10, 'daze_beam'], [15, 'psy_blast'], [20, 'clear_thought']],
  'Dream Kitten Morph', 'The little orb above its head glows brighter when it purrs. Children who sleep beside one never have nightmares.');
s(76, 'mystaline', 'Mystaline', ['Mind'], [65, 50, 60, 90, 80, 90], 'medium', 150, 90, { level: 40, into: 'oraclynx' },
  [[1, 'psy_blast'], [1, 'daze_beam'], [22, 'trance'], [27, 'clear_thought'], [32, 'mind_spike'], [38, 'shade_fang']],
  'Seer Cat Morph', 'Two orbs circle it like tiny moons. It stares at empty corners, and sometimes the empty corners stare back.');
s(77, 'oraclynx', 'Oraclynx', ['Mind', 'Umbra'], [85, 70, 75, 125, 100, 105], 'medium', 245, 45, null,
  [[1, 'mind_spike'], [1, 'shadow_creep'], [40, 'dread_gaze'], [44, 'astral_ray'], [44, 'prophecy_beam'], [49, 'hex_mist'], [54, 'clear_thought']],
  'Oracle Morph', 'Its third eye opens only when it sees the future. Those who meet its gaze remember things that have not happened yet.');
// Frost fox line
s(78, 'frostkit', 'Frostkit', ['Frost'], [45, 45, 40, 50, 50, 60], 'medium', 60, 190, { level: 24, into: 'glacivix' },
  [[1, 'bump'], [1, 'chill_nip'], [6, 'nip'], [10, 'frost_fang'], [15, 'hail_volley'], [20, 'frost_armor']],
  'Snow Kit Morph', 'It naps curled inside its own snowball tail. Wake it gently — a startled Frostkit sneezes ice.');
s(79, 'glacivix', 'Glacivix', ['Frost'], [65, 75, 60, 80, 70, 95], 'medium', 150, 90, { level: 42, into: 'aurovulpa' },
  [[1, 'frost_fang'], [1, 'hail_volley'], [24, 'icicle_jab'], [29, 'frost_armor'], [34, 'rime_ray'], [39, 'psy_blast']],
  'Crystal Fox Morph', 'Its three crystal tails chime in the wind. Travellers lost in blizzards follow the sound to safety.');
s(80, 'aurovulpa', 'Aurovulpa', ['Frost', 'Mind'], [85, 80, 80, 120, 105, 115], 'medium', 250, 45, null,
  [[1, 'rime_ray'], [1, 'psy_blast'], [42, 'glacial_crush'], [46, 'mind_spike'], [46, 'aurora_lance'], [50, 'whiteout_gale'], [55, 'astral_ray']],
  'Aurora Morph', 'On clear winter nights its five tails paint the aurora across the sky. It is said to crown only one in a generation.');
// Iron beetle line
s(81, 'rivetle', 'Rivetle', ['Iron', 'Swarm'], [45, 55, 65, 25, 40, 30], 'medium', 60, 190, { level: 24, into: 'carapaxe' },
  [[1, 'bump'], [1, 'mandible_nip'], [5, 'plate_up'], [9, 'cog_strike'], [14, 'chrome_claw'], [19, 'sap_sting']],
  'Rivet Bug Morph', 'It peeks out from under its shell with enormous eyes. Rivetle love nesting in old machinery and humming along with engines.');
s(82, 'carapaxe', 'Carapaxe', ['Iron', 'Swarm'], [65, 90, 95, 35, 60, 45], 'medium', 150, 90, { level: 42, into: 'juggernox' },
  [[1, 'chrome_claw'], [1, 'sap_sting'], [24, 'alloy_lash'], [29, 'swarm_strike'], [34, 'plate_up'], [39, 'steel_ram']],
  'Axe Beetle Morph', 'Its horn has grown into a gleaming blade. Lumberjacks in the Reach swear a Carapaxe can fell a pine in three swings.');
s(83, 'juggernox', 'Juggernox', ['Iron', 'Swarm'], [95, 125, 130, 45, 80, 45], 'slow', 250, 45, null,
  [[1, 'steel_ram'], [1, 'swarm_strike'], [42, 'anvil_drop'], [46, 'scythe_rend'], [46, 'siege_ram'], [50, 'plate_up'], [55, 'all_out_slam']],
  'Siege Beetle Morph', 'Steam hisses from its armour when it charges. Nothing — not walls, not gates, not mountains — slows a Juggernox down.');
// Drake wyvern line (rare, very strong)
s(84, 'wyvlet', 'Wyvlet', ['Drake'], [50, 60, 45, 45, 45, 55], 'slow', 67, 45, { level: 30, into: 'wyverant' },
  [[1, 'bump'], [1, 'wyrm_breath'], [6, 'nip'], [11, 'coil_whip'], [16, 'drake_talon'], [22, 'draconic_surge'], [28, 'scale_rake']],
  'Hatchling Morph', 'Its wings are far too small to fly, but it flaps them anyway. Wyvlet hoard shiny pebbles in a nest of their own shed scales.');
s(85, 'wyverant', 'Wyverant', ['Drake', 'Wing'], [70, 90, 65, 65, 65, 80], 'slow', 150, 45, { level: 48, into: 'skyrannox' },
  [[1, 'drake_talon'], [1, 'wing_strike'], [30, 'scale_rake'], [35, 'draconic_surge'], [40, 'gale_slice'], [45, 'sky_dive']],
  'Young Wyvern Morph', 'It practises dives from clifftops and crashes more often than it lands. It never, ever gives up.');
s(86, 'skyrannox', 'Skyrannox', ['Drake', 'Wing'], [95, 130, 90, 100, 90, 105], 'slow', 280, 45, null,
  [[1, 'scale_rake'], [1, 'sky_dive'], [48, 'wyvern_dive'], [52, 'tempest_wing'], [52, 'tyrant_skyfall'], [56, 'draconic_surge'], [60, 'rift_nova']],
  'Sky Tyrant Morph', 'When its roar rolls over the mountains, every other Morph goes quiet. Only the bravest Tamers have ever ridden one.');
// Swarm bee line
s(87, 'hivling', 'Hivling', ['Swarm'], [45, 40, 45, 40, 45, 55], 'fast', 55, 220, { level: 22, into: 'waspire' },
  [[1, 'bump'], [1, 'mandible_nip'], [5, 'drowse_pollen'], [9, 'pin_volley'], [14, 'sap_sting'], [19, 'heal_bud']],
  'Honeybee Morph', 'It carries a drop of honey on its tail and shares it with anyone who looks sad.');
s(88, 'waspire', 'Waspire', ['Swarm', 'Wing'], [70, 95, 65, 50, 65, 110], 'fast', 155, 75, null,
  [[1, 'sap_sting'], [1, 'wing_strike'], [22, 'swarm_strike'], [27, 'venom_lash'], [28, 'royal_sting'], [32, 'gale_slice'], [38, 'scythe_rend'], [44, 'sky_dive']],
  'Queen Wasp Morph', 'A Waspire wears its crest like a crown and rules its hive with a single glare. Its sting leaves a mark for a week.');
// Ember salamander line
s(89, 'scorchling', 'Scorchling', ['Ember'], [45, 50, 40, 55, 45, 55], 'medium', 60, 190, { level: 32, into: 'magmaw' },
  [[1, 'bump'], [1, 'ember_spark'], [6, 'nip'], [10, 'kindle'], [15, 'flare_bite'], [21, 'cinder_claw'], [27, 'blaze_ring']],
  'Salamander Morph', 'The flame on its tail tip flickers when it is happy. If it goes out, the Scorchling sulks until someone relights it.');
s(90, 'magmaw', 'Magmaw', ['Ember', 'Stone'], [95, 115, 100, 75, 70, 50], 'medium', 225, 60, null,
  [[1, 'flare_bite'], [1, 'rubble_fall'], [32, 'magma_jaws'], [36, 'caldera_crush'], [37, 'quake_stomp'], [42, 'pyre_rush'], [48, 'boulder_drop']],
  'Lava Croc Morph', 'It lurks in lava pools with only its glowing eyes showing. Its jaws are hot enough to melt iron.');
// Swarm/Brawl — evolves from Mantipule
s(91, 'mantiscythe', 'Mantiscythe', ['Swarm', 'Brawl'], [80, 125, 80, 50, 70, 105], 'fast', 230, 45, null,
  [[1, 'swarm_strike'], [1, 'power_kick'], [36, 'scythe_rend'], [40, 'battle_stance'], [40, 'guillotine_scythe'], [45, 'rising_uppercut'], [50, 'all_out_slam']],
  'Blade Master Morph', 'Every scar on its body is from a duel it won. It salutes its opponent with crossed scythes before striking.');
// Toxin scorpion line
s(92, 'stingrix', 'Stingrix', ['Toxin', 'Swarm'], [45, 60, 50, 35, 40, 55], 'medium', 60, 190, { level: 30, into: 'scorvex' },
  [[1, 'mandible_nip'], [1, 'acid_spit'], [6, 'pin_volley'], [11, 'toxic_fang'], [16, 'corrode'], [22, 'sap_sting']],
  'Sting Morph', 'It waves its venom bulb around like a toy. Most of the time the sting is only a tickle — most of the time.');
s(93, 'scorvex', 'Scorvex', ['Toxin', 'Swarm'], [80, 115, 100, 60, 75, 80], 'medium', 225, 60, null,
  [[1, 'toxic_fang'], [1, 'swarm_strike'], [30, 'noxious_jab'], [34, 'death_stinger'], [35, 'venom_lash'], [40, 'scythe_rend'], [46, 'toxic_torrent']],
  'Venom Lord Morph', 'Its eyes glow in the dark of the Rift like a cluster of coals. One drop from its stinger can fell a Rammoth.');
// Static eel line
s(94, 'zaplet', 'Zaplet', ['Static', 'Tide'], [45, 45, 40, 60, 45, 60], 'medium', 60, 190, { level: 30, into: 'thundeel' },
  [[1, 'splash_drop'], [1, 'static_jolt'], [6, 'numb_pulse'], [11, 'volt_fang'], [16, 'tide_pulse'], [22, 'charge_ram']],
  'Spark Eel Morph', 'It sparkles when it swims. Fishermen say a Zaplet in the net means good luck — and a tingly afternoon.');
s(95, 'thundeel', 'Thundeel', ['Static', 'Tide'], [90, 105, 75, 105, 75, 75], 'medium', 230, 60, null,
  [[1, 'volt_fang'], [1, 'brine_fang'], [30, 'thunder_arc'], [34, 'thunder_jaws'], [35, 'undertow'], [40, 'hydro_burst'], [46, 'skybolt']],
  'Storm Moray Morph', 'It rears out of the waves with lightning crawling down its body. Sailors in the Reach paint its jaws on their hulls for luck.');
// Umbra wisp line
s(96, 'hollowisp', 'Hollowisp', ['Umbra'], [40, 35, 40, 60, 55, 60], 'medium', 60, 190, { level: 32, into: 'grimshroud' },
  [[1, 'night_tremor'], [1, 'lullaby'], [6, 'hex_mist'], [11, 'shade_fang'], [16, 'dread_gaze'], [22, 'soul_siphon']],
  'Lantern Wisp Morph', 'It lights the way for lost travellers on the moor. Nobody knows whether it wants to help them, or keep them.');
s(97, 'grimshroud', 'Grimshroud', ['Umbra', 'Mind'], [80, 75, 80, 120, 105, 80], 'medium', 235, 45, null,
  [[1, 'soul_siphon'], [1, 'psy_blast'], [32, 'shadow_creep'], [36, 'reapers_lantern'], [37, 'trance'], [42, 'mind_spike'], [48, 'nightrend']],
  'Reaper Morph', 'It carries the lantern of every soul it has guided home. On stormy nights, the lanterns flicker all at once.');
// Singles
s(98, 'oculith', 'Oculith', ['Mind', 'Stone'], [75, 60, 110, 105, 110, 40], 'slow', 180, 45, null,
  [[1, 'psy_blast'], [1, 'stone_toss'], [20, 'dread_gaze'], [26, 'rubble_fall'], [32, 'mind_spike'], [38, 'stoneskin'], [44, 'astral_ray']],
  'Watcher Morph', 'An ancient eye set in a ring of standing stones. It has watched the Riven since before the Wardens, and it never looks away.');
s(99, 'alloyena', 'Alloyena', ['Iron', 'Umbra'], [70, 110, 80, 55, 60, 100], 'medium', 175, 60, null,
  [[1, 'shade_fang'], [1, 'chrome_claw'], [26, 'ambush'], [31, 'alloy_lash'], [36, 'nightrend'], [42, 'steel_ram']],
  'Blade Hyena Morph', 'Its laugh echoes through the scrapyards at night. A pack of Alloyena can strip an abandoned cart to the axles by dawn.');
s(100, 'brutusk', 'Brutusk', ['Brawl', 'Stone'], [100, 120, 100, 35, 60, 60], 'medium', 175, 60, null,
  [[1, 'ram_charge'], [1, 'rubble_fall'], [24, 'battle_stance'], [29, 'power_kick'], [34, 'quake_stomp'], [40, 'rising_uppercut'], [46, 'mountain_crash']],
  'Tusk Boar Morph', 'It charges first and never asks questions. Farmers build their fences of stone where Brutusk roam.');
s(101, 'rimewraith', 'Rimewraith', ['Frost', 'Umbra'], [75, 70, 70, 115, 95, 95], 'medium', 180, 45, null,
  [[1, 'chill_nip'], [1, 'hex_mist'], [30, 'rime_ray'], [35, 'dread_gaze'], [40, 'shadow_creep'], [46, 'whiteout_gale']],
  'Frost Phantom Morph', 'It drifts over the Frostspire passes on moonless nights. Where it screams, the snow freezes solid.');
s(102, 'montolith', 'Montolith', ['Stone', 'Brawl'], [105, 135, 135, 50, 80, 30], 'slow', 250, 45, null,
  [[1, 'quake_stomp'], [1, 'power_kick'], [44, 'mountain_crash'], [48, 'stoneskin'], [48, 'peakfall'], [52, 'rising_uppercut'], [58, 'boulder_drop']],
  'Mountain Morph', 'Snow never melts on its shoulders. Some say the peaks of the Reach are old Montolith that fell asleep standing up.');


export const SPECIES_LIST = LIST;

// Chance a Morph is female (0–1). Every Morph has male and female forms; Tiamat, the Draco Queen, is always female.
for (const sp of LIST) { sp.female = 0.5; }
SPECIES.tiamat.female = 1;

export function validateSpecies() {
  const problems = [];
  for (const sp of LIST) {
    for (const [, mv] of sp.learn) { if (!MOVES[mv]) { problems.push(`${sp.id}: unknown move ${mv}`); } }
    if (sp.evo && !SPECIES[sp.evo.into]) { problems.push(`${sp.id}: evolves into unknown ${sp.evo.into}`); }
  }
  return problems;
}
