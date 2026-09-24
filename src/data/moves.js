// Every move in Tiamat. All names are original to this game.
// m(id, name, type, category, power, accuracy, pp, fx, desc)
//   category: phys | spec | status      accuracy: null = never misses
//   fx: status/chance, confuse, flinch, stat (+target), multi, charge, recoil,
//       drain, heal, highCrit, fixed, seed, protect, selfStat, prio

export const MOVES = {};
function m(id, name, type, cat, power, acc, pp, fx = {}, desc = '') {
  MOVES[id] = { id, name, type, cat, power, acc, pp, fx, prio: fx.prio || 0, desc };
}

// ── Plain ───────────────────────────────────────────────────────────────────
m('bump', 'Bump', 'Plain', 'phys', 40, 100, 35, {}, 'A clumsy but honest shove.');
m('nip', 'Nip', 'Plain', 'phys', 35, 100, 35, { flinch: 0.1 }, 'A quick nip. May make the foe flinch.');
m('flit_strike', 'Flit Strike', 'Plain', 'phys', 40, 100, 30, { prio: 1 }, 'Darts in before the foe can react. Always strikes first.');
m('gruff_bark', 'Gruff Bark', 'Plain', 'status', 0, 100, 40, { stat: { atk: -1 }, target: 'foe' }, 'A rough bark that lowers the foe\'s Attack.');
m('stern_look', 'Stern Look', 'Plain', 'status', 0, 100, 30, { stat: { def: -1 }, target: 'foe' }, 'An unnerving stare that lowers the foe\'s Defense.');
m('ram_charge', 'Ram Charge', 'Plain', 'phys', 85, 100, 15, { recoil: 0.25 }, 'A headlong charge. The user takes some recoil.');
m('clamor', 'Clamor', 'Plain', 'spec', 90, 100, 10, {}, 'A deafening shout that rattles the foe.');
m('pummel', 'Pummel', 'Plain', 'phys', 18, 95, 20, { multi: [2, 5] }, 'A flurry of blows that hits 2-5 times.');
m('rally_cry', 'Rally Cry', 'Plain', 'status', 0, null, 30, { stat: { atk: 1, spe: 1 }, target: 'self' }, 'A rousing cry that raises Attack and Speed.');
m('mend', 'Mend', 'Plain', 'status', 0, null, 10, { heal: 0.5 }, 'Rests a moment to recover half its max HP.');
m('brace', 'Brace', 'Plain', 'status', 0, null, 20, { stat: { def: 2 }, target: 'self' }, 'Tenses every muscle, sharply raising Defense.');
m('lullaby', 'Lullaby', 'Plain', 'status', 0, 60, 15, { status: 'sleep', chance: 1 }, 'A soft song that lulls the foe to sleep.');
m('grand_slam', 'Grand Slam', 'Plain', 'phys', 110, 85, 5, {}, 'A full-body smash with enormous force.');
m('guard_up', 'Guard Up', 'Plain', 'status', 0, null, 10, { protect: true, prio: 4 }, 'Blocks every attack this turn. Fails if used twice in a row.');

// ── Nature ─────────────────────────────────────────────────────────────────
m('leaf_nick', 'Leaf Nick', 'Nature', 'phys', 40, 100, 25, {}, 'Slices with a sharp-edged leaf.');
m('vine_lash', 'Vine Lash', 'Nature', 'phys', 50, 100, 25, {}, 'Whips the foe with a springy vine.');
m('seed_volley', 'Seed Volley', 'Nature', 'phys', 25, 100, 30, { multi: [2, 5] }, 'Fires hard seeds 2-5 times in a row.');
m('heal_bud', 'Heal Bud', 'Nature', 'status', 0, null, 10, { heal: 0.5 }, 'A restorative bloom that recovers half its max HP.');
m('root_snare', 'Root Snare', 'Nature', 'status', 0, 90, 10, { seed: true }, 'Roots burrow into the foe, draining HP every turn.');
m('drowse_pollen', 'Drowse Pollen', 'Nature', 'status', 0, 75, 15, { status: 'sleep', chance: 1 }, 'Heavy golden pollen that makes the foe doze off.');
m('sap_drain', 'Sap Drain', 'Nature', 'spec', 60, 100, 15, { drain: 0.5 }, 'Siphons the foe\'s vigour, healing half the damage dealt.');
m('bloom_blast', 'Bloom Blast', 'Nature', 'spec', 90, 100, 10, { stat: { spd: -1 }, target: 'foe', chance: 0.1 }, 'A burst of living energy. May lower Sp. Def.');
m('timber_crash', 'Timber Crash', 'Nature', 'phys', 110, 95, 5, { recoil: 0.33 }, 'Slams like a falling tree. Heavy recoil.');
m('moss_shield', 'Moss Shield', 'Nature', 'status', 0, null, 20, { stat: { def: 1, spd: 1 }, target: 'self' }, 'Grows a coat of moss that raises Defense and Sp. Def.');

// ── Ember ──────────────────────────────────────────────────────────────────
m('ember_spark', 'Ember Spark', 'Ember', 'spec', 40, 100, 25, { status: 'burn', chance: 0.1 }, 'A jet of sparks. May burn.');
m('flare_bite', 'Flare Bite', 'Ember', 'phys', 65, 95, 15, { status: 'burn', chance: 0.1, flinch: 0.1 }, 'A blazing chomp. May burn or cause flinching.');
m('cinder_claw', 'Cinder Claw', 'Ember', 'phys', 55, 100, 25, { highCrit: true }, 'Glowing claws. High critical-hit ratio.');
m('blaze_ring', 'Blaze Ring', 'Ember', 'spec', 75, 100, 15, { status: 'burn', chance: 0.1 }, 'A ring of fire that closes on the foe. May burn.');
m('inferno_lash', 'Inferno Lash', 'Ember', 'spec', 100, 85, 5, { status: 'burn', chance: 0.2 }, 'A whip of white-hot flame. May burn.');
m('smoke_veil', 'Smoke Veil', 'Ember', 'status', 0, 100, 20, { stat: { acc: -1 }, target: 'foe' }, 'Billowing smoke that lowers the foe\'s accuracy.');
m('kindle', 'Kindle', 'Ember', 'status', 0, 85, 15, { status: 'burn', chance: 1 }, 'Ghostly embers that burn the foe.');
m('magma_jaws', 'Magma Jaws', 'Ember', 'phys', 90, 95, 10, { status: 'burn', chance: 0.2 }, 'Clamps down with molten jaws. May burn.');
m('pyre_rush', 'Pyre Rush', 'Ember', 'phys', 115, 100, 10, { recoil: 0.33, status: 'burn', chance: 0.1 }, 'A blazing tackle. Heavy recoil.');

// ── Tide ───────────────────────────────────────────────────────────────────
m('splash_drop', 'Splash Drop', 'Tide', 'spec', 40, 100, 25, {}, 'A pressurised droplet fired at the foe.');
m('rip_current', 'Rip Current', 'Tide', 'phys', 40, 100, 20, { prio: 1 }, 'Rides a current into the foe. Always strikes first.');
m('tide_pulse', 'Tide Pulse', 'Tide', 'spec', 60, 100, 20, { confuse: 0.2 }, 'A throbbing wave. May confuse.');
m('brine_fang', 'Brine Fang', 'Tide', 'phys', 65, 95, 15, { flinch: 0.2 }, 'Salt-slick fangs. May cause flinching.');
m('undertow', 'Undertow', 'Tide', 'phys', 85, 90, 10, { stat: { spe: -1 }, target: 'foe', chance: 1 }, 'Drags the foe under, lowering its Speed.');
m('hydro_burst', 'Hydro Burst', 'Tide', 'spec', 100, 85, 5, {}, 'A thunderous blast of water.');
m('tidal_guard', 'Tidal Guard', 'Tide', 'status', 0, null, 20, { stat: { def: 1, spd: 1 }, target: 'self' }, 'Wraps itself in water, raising Defense and Sp. Def.');
m('primordial_tide', 'Primordial Tide', 'Tide', 'spec', 120, 90, 5, { stat: { spd: -1 }, target: 'foe', chance: 0.3 }, 'The first sea rises at its call. Tiamat\'s signature move.');

// ── Static ─────────────────────────────────────────────────────────────────
m('volt_fang', 'Volt Fang', 'Static', 'phys', 65, 100, 15, { status: 'paralyze', chance: 0.2 }, 'A bite crackling with current. May paralyse.');
m('static_jolt', 'Static Jolt', 'Static', 'spec', 40, 100, 30, { status: 'paralyze', chance: 0.1 }, 'A crackling jolt. May paralyse.');
m('charge_ram', 'Charge Ram', 'Static', 'phys', 65, 100, 20, { status: 'paralyze', chance: 0.3 }, 'A charged body-check. May paralyse.');
m('volt_needle', 'Volt Needle', 'Static', 'phys', 20, 95, 20, { multi: [2, 5] }, 'Fires charged quills 2-5 times.');
m('numb_pulse', 'Numb Pulse', 'Static', 'status', 0, 90, 20, { status: 'paralyze', chance: 1 }, 'A weak current that paralyses the foe.');
m('thunder_arc', 'Thunder Arc', 'Static', 'spec', 90, 100, 15, { status: 'paralyze', chance: 0.1 }, 'An arc of lightning. May paralyse.');
m('skybolt', 'Skybolt', 'Static', 'spec', 115, 75, 5, { status: 'paralyze', chance: 0.3 }, 'Calls a bolt down from the sky. May paralyse.');
m('overcharge', 'Overcharge', 'Static', 'status', 0, null, 20, { stat: { spa: 2 }, target: 'self' }, 'Builds up current, sharply raising Sp. Atk.');

// ── Stone ──────────────────────────────────────────────────────────────────
m('stone_toss', 'Stone Toss', 'Stone', 'phys', 50, 90, 15, {}, 'Hurls a jagged stone.');
m('grit_spray', 'Grit Spray', 'Stone', 'status', 0, 100, 15, { stat: { acc: -1 }, target: 'foe' }, 'Kicks up grit, lowering the foe\'s accuracy.');
m('mud_lob', 'Mud Lob', 'Stone', 'spec', 55, 95, 15, { stat: { acc: -1 }, target: 'foe', chance: 0.3 }, 'A clod of mud. May lower accuracy.');
m('rubble_fall', 'Rubble Fall', 'Stone', 'phys', 75, 90, 10, { flinch: 0.3 }, 'Brings down rubble. May cause flinching.');
m('quake_stomp', 'Quake Stomp', 'Stone', 'phys', 90, 100, 10, {}, 'A stomp that shakes the ground itself.');
m('mountain_crash', 'Mountain Crash', 'Stone', 'phys', 120, 85, 5, { recoil: 0.25 }, 'Hurls its whole mountainous bulk at the foe. The user takes some recoil.');
m('boulder_drop', 'Boulder Drop', 'Stone', 'phys', 110, 80, 5, {}, 'Drops a boulder on the foe.');
m('stoneskin', 'Stoneskin', 'Stone', 'status', 0, null, 15, { stat: { def: 2 }, target: 'self' }, 'Hardens its hide like stone, sharply raising Defense.');

// ── Frost ──────────────────────────────────────────────────────────────────
m('chill_nip', 'Chill Nip', 'Frost', 'spec', 40, 100, 25, { status: 'freeze', chance: 0.1 }, 'A biting cold. May freeze.');
m('icicle_jab', 'Icicle Jab', 'Frost', 'phys', 65, 100, 20, { status: 'freeze', chance: 0.1 }, 'Stabs with an icicle. May freeze.');
m('hail_volley', 'Hail Volley', 'Frost', 'phys', 25, 100, 30, { multi: [2, 5] }, 'Pelts the foe with hailstones 2-5 times.');
m('rime_ray', 'Rime Ray', 'Frost', 'spec', 90, 100, 10, { status: 'freeze', chance: 0.1 }, 'A freezing ray. May freeze.');
m('whiteout_gale', 'Whiteout Gale', 'Frost', 'spec', 110, 70, 5, { status: 'freeze', chance: 0.1 }, 'A howling storm of snow. May freeze.');
m('frost_fang', 'Frost Fang', 'Frost', 'phys', 60, 100, 20, { status: 'freeze', chance: 0.15 }, 'A bite with frozen fangs. May freeze.');
m('glacial_crush', 'Glacial Crush', 'Frost', 'phys', 100, 90, 5, {}, 'Brings down a slab of glacier ice.');
m('frost_armor', 'Frost Armor', 'Frost', 'status', 0, null, 20, { stat: { def: 1, spd: 1 }, target: 'self' }, 'Coats itself in ice, raising Defense and Sp. Def.');

// ── Wing ───────────────────────────────────────────────────────────────────
m('beak_jab', 'Beak Jab', 'Wing', 'phys', 35, 100, 35, {}, 'A sharp jab of the beak.');
m('breeze_cut', 'Breeze Cut', 'Wing', 'spec', 40, 100, 35, {}, 'A cutting gust of wind.');
m('wing_strike', 'Wing Strike', 'Wing', 'phys', 60, 100, 25, {}, 'Strikes with outstretched wings.');
m('gale_slice', 'Gale Slice', 'Wing', 'spec', 75, 95, 15, { highCrit: true }, 'A blade of wind. High critical-hit ratio.');
m('sky_dive', 'Sky Dive', 'Wing', 'phys', 90, 95, 15, { charge: 'soared high into the sky!' }, 'Flies up on turn one, dives on turn two.');
m('updraft', 'Updraft', 'Wing', 'status', 0, null, 20, { stat: { spe: 2 }, target: 'self' }, 'Catches a rising wind, sharply raising Speed.');
m('tempest_wing', 'Tempest Wing', 'Wing', 'spec', 110, 80, 5, {}, 'A wingbeat that whips up a tempest.');

// ── Swarm ──────────────────────────────────────────────────────────────────
m('mandible_nip', 'Mandible Nip', 'Swarm', 'phys', 40, 100, 30, {}, 'Pinches with clacking mandibles.');
m('pin_volley', 'Pin Volley', 'Swarm', 'phys', 25, 95, 20, { multi: [2, 5] }, 'Fires sharp pins 2-5 times.');
m('silk_snare', 'Silk Snare', 'Swarm', 'status', 0, 95, 40, { stat: { spe: -2 }, target: 'foe' }, 'Sticky silk that sharply lowers the foe\'s Speed.');
m('sap_sting', 'Sap Sting', 'Swarm', 'phys', 60, 100, 15, { drain: 0.5 }, 'A draining sting that heals half the damage dealt.');
m('scythe_rend', 'Scythe Rend', 'Swarm', 'phys', 90, 95, 10, { highCrit: true }, 'Two scythes cross in a flash. High critical-hit ratio.');
m('swarm_strike', 'Swarm Strike', 'Swarm', 'phys', 80, 100, 15, {}, 'Attacks as if backed by a whole swarm.');
m('drone_hum', 'Drone Hum', 'Swarm', 'spec', 90, 100, 10, { stat: { spd: -1 }, target: 'foe', chance: 0.1 }, 'A droning buzz. May lower Sp. Def.');
m('chitin_guard', 'Chitin Guard', 'Swarm', 'status', 0, null, 20, { stat: { def: 1, atk: 1 }, target: 'self' }, 'Hardens its shell, raising Attack and Defense.');

// ── Toxin ──────────────────────────────────────────────────────────────────
m('acid_spit', 'Acid Spit', 'Toxin', 'spec', 40, 100, 30, { status: 'poison', chance: 0.3 }, 'Spits acid. May poison.');
m('toxic_fang', 'Toxic Fang', 'Toxin', 'phys', 55, 100, 15, { status: 'poison', chance: 0.4 }, 'A venom-laced bite. May poison.');
m('corrode', 'Corrode', 'Toxin', 'status', 0, 100, 20, { stat: { def: -2 }, target: 'foe' }, 'Eats at the foe\'s armour, sharply lowering Defense.');
m('blight_cloud', 'Blight Cloud', 'Toxin', 'status', 0, 90, 10, { status: 'toxic', chance: 1 }, 'A foul cloud that badly poisons the foe.');
m('noxious_jab', 'Noxious Jab', 'Toxin', 'phys', 80, 100, 15, { status: 'poison', chance: 0.3 }, 'A dripping stab. May poison.');
m('venom_lash', 'Venom Lash', 'Toxin', 'phys', 70, 100, 15, { status: 'poison', chance: 0.2 }, 'Whips the foe with a venom-soaked limb. May poison.');
m('toxic_torrent', 'Toxic Torrent', 'Toxin', 'spec', 105, 85, 5, { status: 'poison', chance: 0.3 }, 'Floods the field with poison. May poison.');
m('mire_blast', 'Mire Blast', 'Toxin', 'spec', 90, 100, 10, { status: 'poison', chance: 0.3 }, 'A wave of toxic sludge. May poison.');

// ── Brawl ──────────────────────────────────────────────────────────────────
m('palm_strike', 'Palm Strike', 'Brawl', 'phys', 50, 100, 25, { highCrit: true }, 'A precise open-palm strike. High critical-hit ratio.');
m('counterblow', 'Counterblow', 'Brawl', 'phys', 40, 100, 30, { prio: 1 }, 'A lightning-fast jab. Always strikes first.');
m('knuckle_barrage', 'Knuckle Barrage', 'Brawl', 'phys', 18, 100, 20, { multi: [2, 5] }, 'Rapid punches that hit 2-5 times.');
m('power_kick', 'Power Kick', 'Brawl', 'phys', 75, 90, 15, {}, 'A heavy roundhouse kick.');
m('all_out_slam', 'All-Out Slam', 'Brawl', 'phys', 120, 100, 5, { selfStat: { def: -1, spd: -1 } }, 'Holds nothing back. Lowers the user\'s defences.');
m('rising_uppercut', 'Rising Uppercut', 'Brawl', 'phys', 90, 90, 10, { flinch: 0.2 }, 'A leaping uppercut. May cause flinching.');
m('battle_stance', 'Battle Stance', 'Brawl', 'status', 0, null, 20, { stat: { atk: 2 }, target: 'self' }, 'Takes a fighting stance, sharply raising Attack.');

// ── Mind ───────────────────────────────────────────────────────────────────
m('psy_blast', 'Psy Blast', 'Mind', 'spec', 65, 100, 20, { confuse: 0.1 }, 'A burst of psychic force. May confuse.');
m('daze_beam', 'Daze Beam', 'Mind', 'status', 0, 100, 10, { confuse: 1 }, 'A shimmering beam that confuses the foe.');
m('trance', 'Trance', 'Mind', 'status', 0, 60, 20, { status: 'sleep', chance: 1 }, 'A swaying pattern that sends the foe to sleep.');
m('mind_spike', 'Mind Spike', 'Mind', 'spec', 90, 100, 10, { stat: { spd: -1 }, target: 'foe', chance: 0.1 }, 'Drives a spike of thought into the foe.');
m('psi_horn', 'Psi Horn', 'Mind', 'phys', 80, 90, 15, { flinch: 0.2 }, 'A horn charged with psychic power.');
m('psi_wave', 'Psi Wave', 'Mind', 'spec', 45, 100, 30, {}, 'A gentle ripple of psychic force.');
m('astral_ray', 'Astral Ray', 'Mind', 'spec', 110, 85, 5, { confuse: 0.2 }, 'A beam of starlight from beyond. May confuse.');
m('clear_thought', 'Clear Thought', 'Mind', 'status', 0, null, 20, { stat: { spa: 1, spd: 1 }, target: 'self' }, 'Stills the mind, raising Sp. Atk and Sp. Def.');

// ── Umbra ──────────────────────────────────────────────────────────────────
m('shade_fang', 'Shade Fang', 'Umbra', 'phys', 60, 100, 25, { flinch: 0.3 }, 'A bite from the shadows. May cause flinching.');
m('night_tremor', 'Night Tremor', 'Umbra', 'spec', 1, 100, 15, { fixed: 'level' }, 'Deals damage equal to the user\'s level.');
m('ambush', 'Ambush', 'Umbra', 'phys', 70, 100, 10, { prio: 1 }, 'Strikes from hiding. Always goes first.');
m('shadow_creep', 'Shadow Creep', 'Umbra', 'spec', 80, 100, 15, {}, 'Tendrils of shadow engulf the foe.');
m('hex_mist', 'Hex Mist', 'Umbra', 'spec', 65, 100, 15, { confuse: 0.2 }, 'A cursed mist. May confuse.');
m('dread_gaze', 'Dread Gaze', 'Umbra', 'status', 0, 100, 15, { stat: { spa: -2 }, target: 'foe' }, 'A terrifying gaze that sharply lowers Sp. Atk.');
m('soul_siphon', 'Soul Siphon', 'Umbra', 'spec', 70, 100, 10, { drain: 0.5 }, 'Draws out the foe\'s spirit, healing half the damage dealt.');
m('nightrend', 'Nightrend', 'Umbra', 'phys', 90, 100, 10, { highCrit: true }, 'Tears through the dark. High critical-hit ratio.');

// ── Iron ───────────────────────────────────────────────────────────────────
m('chrome_claw', 'Chrome Claw', 'Iron', 'phys', 50, 95, 35, { stat: { atk: 1 }, target: 'self', chance: 0.1 }, 'Metal claws. May raise the user\'s Attack.');
m('cog_strike', 'Cog Strike', 'Iron', 'phys', 20, 95, 20, { multi: [2, 5] }, 'Spinning cogs strike 2-5 times.');
m('alloy_lash', 'Alloy Lash', 'Iron', 'phys', 80, 90, 15, { stat: { def: -1 }, target: 'foe', chance: 0.3 }, 'A whip of hard metal. May lower Defense.');
m('gleam_cannon', 'Gleam Cannon', 'Iron', 'spec', 80, 100, 10, { stat: { spd: -1 }, target: 'foe', chance: 0.1 }, 'A beam of reflected light. May lower Sp. Def.');
m('plate_up', 'Plate Up', 'Iron', 'status', 0, null, 15, { stat: { def: 2 }, target: 'self' }, 'Locks metal plates into place, sharply raising Defense.');
m('steel_ram', 'Steel Ram', 'Iron', 'phys', 95, 95, 10, { recoil: 0.25 }, 'Charges horn-first in heavy armour. The user takes some recoil.');
m('anvil_drop', 'Anvil Drop', 'Iron', 'phys', 100, 90, 5, {}, 'Crashes down like an anvil.');

// ── Drake ──────────────────────────────────────────────────────────────────
m('wyrm_breath', 'Wyrm Breath', 'Drake', 'spec', 60, 100, 20, { status: 'paralyze', chance: 0.3 }, 'Ancient breath. May paralyse.');
m('scale_rake', 'Scale Rake', 'Drake', 'phys', 80, 100, 15, {}, 'Rakes with razor-edged scales.');
m('coil_whip', 'Coil Whip', 'Drake', 'phys', 60, 100, 20, { stat: { atk: -1 }, target: 'foe', chance: 0.3 }, 'Lashes with a long tail. May lower Attack.');
m('draconic_surge', 'Draconic Surge', 'Drake', 'status', 0, null, 20, { stat: { atk: 1, spe: 1 }, target: 'self' }, 'Old blood surges, raising Attack and Speed.');
m('drake_talon', 'Drake Talon', 'Drake', 'phys', 75, 100, 15, { highCrit: true }, 'Rakes with dragon talons. High critical-hit ratio.');
m('wyvern_dive', 'Wyvern Dive', 'Drake', 'phys', 115, 90, 5, { recoil: 0.25 }, 'Folds its wings and plummets onto the foe. The user takes some recoil.');
m('rift_nova', 'Rift Nova', 'Drake', 'spec', 120, 90, 5, { selfStat: { spa: -2 } }, 'A burst of rift-light. Sharply lowers the user\'s Sp. Atk.');

// Used automatically when a Morph has no PP left.
m('flail_out', 'Flail Out', 'Plain', 'phys', 50, null, 1, { recoil: 0.25 }, 'Thrashes about desperately.');
