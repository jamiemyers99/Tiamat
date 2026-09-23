// Move definitions — all learnable moves.
// Exports: MOVES
// Schema: { id, name, type, power, accuracy, pp, category, description, effect? }
// category: 'physical' | 'special' | 'status'
// effect: { kind, chance }  kinds: burn|poison|paralyse|sleep|freeze|confuse|flinch|heal

export const MOVES = {
  // ── Plain (Normal-analogue) ───────────────────────────────────────────────
  tackle: {
    id: "tackle", name: "Tackle", type: "Plain", power: 35, accuracy: 100, pp: 35,
    category: "physical",
    description: "A straightforward body-check. Reliable and always available.",
  },
  scratch: {
    id: "scratch", name: "Scratch", type: "Plain", power: 40, accuracy: 100, pp: 35,
    category: "physical",
    description: "Sharp claws rake across the foe. Slightly stronger than a tackle.",
  },
  quick_jab: {
    id: "quick_jab", name: "Quick Jab", type: "Plain", power: 40, accuracy: 100, pp: 30,
    category: "physical",
    description: "A lightning-fast strike that always goes first.",
    effect: { kind: "priority", value: 1 },
  },
  body_slam: {
    id: "body_slam", name: "Body Slam", type: "Plain", power: 75, accuracy: 100, pp: 15,
    category: "physical",
    description: "A full-body crash into the foe. 30% chance to paralyse.",
    effect: { kind: "paralyse", chance: 0.30 },
  },
  hyper_voice: {
    id: "hyper_voice", name: "Hyper Voice", type: "Plain", power: 90, accuracy: 100, pp: 5,
    category: "special",
    description: "A piercing sonic blast. High power but limited uses.",
  },

  // ── Ember (Fire-analogue) ─────────────────────────────────────────────────
  ember_spark: {
    id: "ember_spark", name: "Ember Spark", type: "Ember", power: 40, accuracy: 100, pp: 25,
    category: "special",
    description: "A small jet of flame. 10% chance to burn the target.",
    effect: { kind: "burn", chance: 0.10 },
  },
  flare_bite: {
    id: "flare_bite", name: "Flare Bite", type: "Ember", power: 65, accuracy: 100, pp: 15,
    category: "physical",
    description: "A blazing chomp that can leave a lingering burn. 10% chance.",
    effect: { kind: "burn", chance: 0.10 },
  },
  inferno_lash: {
    id: "inferno_lash", name: "Inferno Lash", type: "Ember", power: 90, accuracy: 85, pp: 5,
    category: "special",
    description: "A massive wave of flame. High power but lower accuracy. 10% burn.",
    effect: { kind: "burn", chance: 0.10 },
  },

  // ── Tide (Water-analogue) ─────────────────────────────────────────────────
  splash_drop: {
    id: "splash_drop", name: "Splash Drop", type: "Tide", power: 40, accuracy: 100, pp: 25,
    category: "special",
    description: "A focused drop of pressurised water. Fast and accurate.",
  },
  tide_pulse: {
    id: "tide_pulse", name: "Tide Pulse", type: "Tide", power: 60, accuracy: 100, pp: 20,
    category: "special",
    description: "A surging pulse of water that hits with steady force.",
  },
  hydro_burst: {
    id: "hydro_burst", name: "Hydro Burst", type: "Tide", power: 90, accuracy: 85, pp: 5,
    category: "special",
    description: "A torrent of water released at full pressure. Devastatingly powerful.",
  },

  // ── Nature (Grass-analogue) ───────────────────────────────────────────────
  vine_lash: {
    id: "vine_lash", name: "Vine Lash", type: "Nature", power: 45, accuracy: 100, pp: 25,
    category: "physical",
    description: "A whip-like vine strike. Reliable with no side effects.",
  },
  seed_volley: {
    id: "seed_volley", name: "Seed Volley", type: "Nature", power: 25, accuracy: 100, pp: 30,
    category: "physical",
    description: "Launches 2–5 seeds in rapid succession. Each hit counts separately.",
    effect: { kind: "multi_hit", minHits: 2, maxHits: 5 },
  },
  heal_bud: {
    id: "heal_bud", name: "Heal Bud", type: "Nature", power: 0, accuracy: 100, pp: 10,
    category: "status",
    description: "A restorative bloom restores 50% of the user's max HP.",
    effect: { kind: "heal", fraction: 0.5 },
  },

  // ── Umbra (Dark-analogue) ─────────────────────────────────────────────────
  bite: {
    id: "bite", name: "Bite", type: "Umbra", power: 60, accuracy: 100, pp: 25,
    category: "physical",
    description: "A fearsome bite that may make the foe flinch. 30% flinch chance.",
    effect: { kind: "flinch", chance: 0.30 },
  },
  shadow_creep: {
    id: "shadow_creep", name: "Shadow Creep", type: "Umbra", power: 80, accuracy: 100, pp: 15,
    category: "special",
    description: "Tendrils of shadow engulf the foe. No secondary effect.",
  },

  // ── Wing (Flying-analogue) ────────────────────────────────────────────────
  peck: {
    id: "peck", name: "Peck", type: "Wing", power: 35, accuracy: 100, pp: 35,
    category: "physical",
    description: "A sharp beak jab. Simple and consistent.",
  },
  gust: {
    id: "gust", name: "Gust", type: "Wing", power: 40, accuracy: 100, pp: 35,
    category: "special",
    description: "A burst of wind that buffets the target.",
  },
  wing_strike: {
    id: "wing_strike", name: "Wing Strike", type: "Wing", power: 60, accuracy: 100, pp: 25,
    category: "physical",
    description: "A diving wing-buffet that hits hard and fast.",
  },
  sky_dive: {
    id: "sky_dive", name: "Sky Dive", type: "Wing", power: 90, accuracy: 90, pp: 5,
    category: "physical",
    description: "Soars high then crashes down on the second turn. Huge damage.",
    effect: { kind: "two_turn", chargeMsg: "soared into the sky!" },
  },

  // ── Sprout (Bug-analogue) ─────────────────────────────────────────────────
  bug_bite: {
    id: "bug_bite", name: "Bug Bite", type: "Sprout", power: 40, accuracy: 100, pp: 30,
    category: "physical",
    description: "A mandible-driven chomp. Steady damage with no frills.",
  },
  spore_cloud: {
    id: "spore_cloud", name: "Spore Cloud", type: "Sprout", power: 0, accuracy: 75, pp: 15,
    category: "status",
    description: "Releases sleep-inducing spores. Unreliable but devastating when it hits.",
    effect: { kind: "sleep", chance: 1.0 },
  },
  pin_volley: {
    id: "pin_volley", name: "Pin Volley", type: "Sprout", power: 25, accuracy: 100, pp: 30,
    category: "physical",
    description: "Fires 2–5 sharp pins. Each hit counts.",
    effect: { kind: "multi_hit", minHits: 2, maxHits: 5 },
  },

  // ── Static (Electric-analogue) ────────────────────────────────────────────
  static_jolt: {
    id: "static_jolt", name: "Static Jolt", type: "Static", power: 40, accuracy: 100, pp: 30,
    category: "special",
    description: "A crackling jolt of electricity. 10% chance to paralyse.",
    effect: { kind: "paralyse", chance: 0.10 },
  },
  spark: {
    id: "spark", name: "Spark", type: "Static", power: 65, accuracy: 100, pp: 20,
    category: "physical",
    description: "A charged body tackle that can paralyse on contact. 30% chance.",
    effect: { kind: "paralyse", chance: 0.30 },
  },
  thunder_arc: {
    id: "thunder_arc", name: "Thunder Arc", type: "Static", power: 95, accuracy: 100, pp: 10,
    category: "special",
    description: "A wide arc of lightning that never misses. 10% paralyse.",
    effect: { kind: "paralyse", chance: 0.10 },
  },

  // ── Stone (Rock-analogue) ─────────────────────────────────────────────────
  stone_toss: {
    id: "stone_toss", name: "Stone Toss", type: "Stone", power: 50, accuracy: 90, pp: 15,
    category: "physical",
    description: "Hurls a jagged rock at the target. Decent power but slightly inaccurate.",
  },
  rock_slide: {
    id: "rock_slide", name: "Rock Slide", type: "Stone", power: 75, accuracy: 90, pp: 10,
    category: "physical",
    description: "A cascade of boulders. 30% chance to make the target flinch.",
    effect: { kind: "flinch", chance: 0.30 },
  },

  // ── Mist (Ice-analogue) ───────────────────────────────────────────────────
  frost_bite: {
    id: "frost_bite", name: "Frost Bite", type: "Mist", power: 40, accuracy: 100, pp: 25,
    category: "special",
    description: "A chilling blast of frozen mist. 10% chance to freeze.",
    effect: { kind: "freeze", chance: 0.10 },
  },
  icicle_jab: {
    id: "icicle_jab", name: "Icicle Jab", type: "Mist", power: 65, accuracy: 100, pp: 20,
    category: "physical",
    description: "Strikes with a sharpened spike of ice. 10% chance to freeze.",
    effect: { kind: "freeze", chance: 0.10 },
  },

  // ── Toxin (Poison-analogue) ───────────────────────────────────────────────
  acid_spit: {
    id: "acid_spit", name: "Acid Spit", type: "Toxin", power: 40, accuracy: 100, pp: 30,
    category: "special",
    description: "Spews corrosive acid. 30% chance to poison the target.",
    effect: { kind: "poison", chance: 0.30 },
  },
  toxic_fang: {
    id: "toxic_fang", name: "Toxic Fang", type: "Toxin", power: 50, accuracy: 100, pp: 15,
    category: "physical",
    description: "A venom-laced bite. 50% chance to badly poison the target.",
    effect: { kind: "poison", chance: 0.50 },
  },

  // ── Mind (Psychic-analogue) ───────────────────────────────────────────────
  confuse_ray: {
    id: "confuse_ray", name: "Confuse Ray", type: "Mind", power: 0, accuracy: 100, pp: 10,
    category: "status",
    description: "Bewilders the target with a dazzling ray. Always confuses.",
    effect: { kind: "confuse", chance: 1.0 },
  },
  psy_blast: {
    id: "psy_blast", name: "Psy Blast", type: "Mind", power: 65, accuracy: 100, pp: 20,
    category: "special",
    description: "A focused burst of psychic energy. No secondary effects.",
  },

  // ── Brawl (Fighting-analogue) ─────────────────────────────────────────────
  karate_chop: {
    id: "karate_chop", name: "Karate Chop", type: "Brawl", power: 50, accuracy: 100, pp: 25,
    category: "physical",
    description: "A precise hand-strike with a boosted critical hit rate.",
    effect: { kind: "high_crit" },
  },
  power_kick: {
    id: "power_kick", name: "Power Kick", type: "Brawl", power: 75, accuracy: 90, pp: 15,
    category: "physical",
    description: "A heavy roundhouse kick. Powerful but slightly inaccurate.",
  },

  // ── Iron (Steel-analogue) ─────────────────────────────────────────────────
  iron_tail: {
    id: "iron_tail", name: "Iron Tail", type: "Iron", power: 80, accuracy: 85, pp: 15,
    category: "physical",
    description: "Slams the foe with a metal-hard tail. 30% chance to lower defence.",
    effect: { kind: "def_down", chance: 0.30 },
  },
  metal_claw: {
    id: "metal_claw", name: "Metal Claw", type: "Iron", power: 50, accuracy: 95, pp: 35,
    category: "physical",
    description: "Rakes with hardened claws. 10% chance to raise the user's attack.",
    effect: { kind: "atk_up_self", chance: 0.10 },
  },

  // ── Drake (Dragon-analogue) ───────────────────────────────────────────────
  dragon_breath: {
    id: "dragon_breath", name: "Dragon Breath", type: "Drake", power: 60, accuracy: 100, pp: 20,
    category: "special",
    description: "A gale of draconic energy. 30% chance to paralyse the target.",
    effect: { kind: "paralyse", chance: 0.30 },
  },
};
