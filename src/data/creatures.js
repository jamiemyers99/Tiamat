// Species definitions, creature factory, XP utilities.
// Exports: SPECIES, CREATURES (alias), createCreature, getLearnsetMoves,
//          getLearnsetMove, applyExperience, xpToNextLevel
import { MOVES } from "./moves.js?v=20260429-15";
import { computeStats, rollIvs, totalXpForLevel, levelForTotalXp, xpYield } from "../engine/xp.js?v=20260429-15";

export const SPECIES = {
  // ── Starter chain: Nature ─────────────────────────────────────────────────
  spriglet: {
    id: "spriglet", name: "Spriglet", types: ["Nature"],
    baseStats: { hp: 45, atk: 49, def: 49, spd: 45 },
    growthRate: "medium_slow", baseExp: 64, catchRate: 45, compatibleTMs: ["tm01_body_slam"],
    evolvesTo: "spriggrove", evolvesAtLevel: 16,
    learnset: [
      { level: 1,  move: "tackle"      },
      { level: 5,  move: "vine_lash"   },
      { level: 10, move: "seed_volley" },
      { level: 16, move: "heal_bud"    },
      { level: 22, move: "pin_volley"  },
      { level: 30, move: "body_slam"   },
    ],
    description: "A timid sapling-Morph that shelters in mossy hollows near streams.",
  },
  spriggrove: {
    id: "spriggrove", name: "Spriggrove", types: ["Nature"],
    baseStats: { hp: 60, atk: 62, def: 63, spd: 60 },
    growthRate: "medium_slow", baseExp: 141, catchRate: 45, compatibleTMs: ["tm01_body_slam"],
    evolvesTo: "mosswarden", evolvesAtLevel: 32,
    learnset: [
      { level: 1,  move: "tackle"      },
      { level: 5,  move: "vine_lash"   },
      { level: 10, move: "seed_volley" },
      { level: 16, move: "heal_bud"    },
      { level: 22, move: "pin_volley"  },
      { level: 30, move: "body_slam"   },
      { level: 35, move: "hydro_burst" },
    ],
    description: "Spriglet's evolved form. Dense foliage shields it from most attacks.",
  },
  mosswarden: {
    id: "mosswarden", name: "Mosswarden", types: ["Nature"],
    baseStats: { hp: 80, atk: 82, def: 83, spd: 80 },
    growthRate: "medium_slow", baseExp: 208, catchRate: 45, compatibleTMs: ["tm01_body_slam"],
    evolvesTo: null, evolvesAtLevel: null,
    learnset: [
      { level: 1,  move: "tackle"      },
      { level: 5,  move: "vine_lash"   },
      { level: 10, move: "seed_volley" },
      { level: 16, move: "heal_bud"    },
      { level: 22, move: "pin_volley"  },
      { level: 30, move: "body_slam"   },
      { level: 35, move: "hydro_burst" },
      { level: 42, move: "hyper_voice" },
    ],
    description: "An ancient guardian draped in living moss. Its presence calms wild Morphs.",
  },

  // ── Starter chain: Ember ──────────────────────────────────────────────────
  cindlet: {
    id: "cindlet", name: "Cindlet", types: ["Ember"],
    baseStats: { hp: 39, atk: 52, def: 43, spd: 65 },
    growthRate: "medium_slow", baseExp: 62, catchRate: 45, compatibleTMs: ["tm01_body_slam"],
    evolvesTo: "cindreaver", evolvesAtLevel: 16,
    learnset: [
      { level: 1,  move: "scratch"     },
      { level: 5,  move: "ember_spark" },
      { level: 10, move: "flare_bite"  },
      { level: 16, move: "quick_jab"   },
      { level: 22, move: "rock_slide"  },
      { level: 30, move: "inferno_lash"},
    ],
    description: "A hot-headed little Morph that always charges in head first.",
  },
  cindreaver: {
    id: "cindreaver", name: "Cindreaver", types: ["Ember"],
    baseStats: { hp: 58, atk: 64, def: 58, spd: 80 },
    growthRate: "medium_slow", baseExp: 142, catchRate: 45, compatibleTMs: ["tm01_body_slam"],
    evolvesTo: "pyromane", evolvesAtLevel: 32,
    learnset: [
      { level: 1,  move: "scratch"     },
      { level: 5,  move: "ember_spark" },
      { level: 10, move: "flare_bite"  },
      { level: 16, move: "quick_jab"   },
      { level: 22, move: "rock_slide"  },
      { level: 30, move: "inferno_lash"},
      { level: 38, move: "body_slam"   },
    ],
    description: "Cindlet's evolved form. Blazing mane marks it as a force to respect.",
  },
  pyromane: {
    id: "pyromane", name: "Pyromane", types: ["Ember"],
    baseStats: { hp: 78, atk: 84, def: 78, spd: 100 },
    growthRate: "medium_slow", baseExp: 209, catchRate: 45, compatibleTMs: ["tm01_body_slam"],
    evolvesTo: null, evolvesAtLevel: null,
    learnset: [
      { level: 1,  move: "scratch"     },
      { level: 5,  move: "ember_spark" },
      { level: 10, move: "flare_bite"  },
      { level: 16, move: "quick_jab"   },
      { level: 22, move: "rock_slide"  },
      { level: 30, move: "inferno_lash"},
      { level: 38, move: "body_slam"   },
      { level: 46, move: "hyper_voice" },
    ],
    description: "Pyromane burns with controlled fury. Rivals say its roar alone scorches grass.",
  },

  // ── Starter chain: Tide ───────────────────────────────────────────────────
  drizzle: {
    id: "drizzle", name: "Drizzle", types: ["Tide"],
    baseStats: { hp: 44, atk: 48, def: 65, spd: 43 },
    growthRate: "medium_slow", baseExp: 63, catchRate: 45, compatibleTMs: ["tm01_body_slam"],
    evolvesTo: "torrentide", evolvesAtLevel: 16,
    learnset: [
      { level: 1,  move: "tackle"      },
      { level: 5,  move: "splash_drop" },
      { level: 10, move: "tide_pulse"  },
      { level: 16, move: "body_slam"   },
      { level: 22, move: "icicle_jab"  },
      { level: 30, move: "hydro_burst" },
    ],
    description: "A gentle water-pup that keeps its fur perpetually damp.",
  },
  torrentide: {
    id: "torrentide", name: "Torrentide", types: ["Tide"],
    baseStats: { hp: 59, atk: 63, def: 80, spd: 58 },
    growthRate: "medium_slow", baseExp: 142, catchRate: 45, compatibleTMs: ["tm01_body_slam"],
    evolvesTo: "maelstrand", evolvesAtLevel: 32,
    learnset: [
      { level: 1,  move: "tackle"      },
      { level: 5,  move: "splash_drop" },
      { level: 10, move: "tide_pulse"  },
      { level: 16, move: "body_slam"   },
      { level: 22, move: "icicle_jab"  },
      { level: 30, move: "hydro_burst" },
      { level: 38, move: "rock_slide"  },
    ],
    description: "Drizzle's evolved form. Its wake floods riverbanks after battle.",
  },
  maelstrand: {
    id: "maelstrand", name: "Maelstrand", types: ["Tide"],
    baseStats: { hp: 79, atk: 83, def: 100, spd: 78 },
    growthRate: "medium_slow", baseExp: 210, catchRate: 45, compatibleTMs: ["tm01_body_slam"],
    evolvesTo: null, evolvesAtLevel: null,
    learnset: [
      { level: 1,  move: "tackle"      },
      { level: 5,  move: "splash_drop" },
      { level: 10, move: "tide_pulse"  },
      { level: 16, move: "body_slam"   },
      { level: 22, move: "icicle_jab"  },
      { level: 30, move: "hydro_burst" },
      { level: 38, move: "rock_slide"  },
      { level: 46, move: "hyper_voice" },
    ],
    description: "Maelstrand controls ocean currents with a sweep of its massive fin.",
  },

  // ── Route 1: Plain chain ──────────────────────────────────────────────────
  trotter: {
    id: "trotter", name: "Trotter", types: ["Plain"],
    baseStats: { hp: 40, atk: 35, def: 35, spd: 50 },
    growthRate: "medium_fast", baseExp: 51, catchRate: 180, compatibleTMs: ["tm01_body_slam"],
    evolvesTo: "trotterion", evolvesAtLevel: 18,
    learnset: [
      { level: 1,  move: "tackle"    },
      { level: 5,  move: "quick_jab"},
      { level: 11, move: "body_slam" },
      { level: 18, move: "hyper_voice"},
    ],
    description: "A compact four-legged Morph that can outrun most foes on open ground.",
  },
  trotterion: {
    id: "trotterion", name: "Trotterion", types: ["Plain"],
    baseStats: { hp: 65, atk: 55, def: 50, spd: 70 },
    growthRate: "medium_fast", baseExp: 128, catchRate: 75, compatibleTMs: ["tm01_body_slam"],
    evolvesTo: null, evolvesAtLevel: null,
    learnset: [
      { level: 1,  move: "tackle"     },
      { level: 5,  move: "quick_jab" },
      { level: 11, move: "body_slam"  },
      { level: 18, move: "hyper_voice"},
      { level: 26, move: "wing_strike"},
    ],
    description: "Trotterion's proud bearing earns it respect on any route.",
  },

  // ── Route 1: Wing chain ───────────────────────────────────────────────────
  beakling: {
    id: "beakling", name: "Beakling", types: ["Wing"],
    baseStats: { hp: 35, atk: 45, def: 40, spd: 56 },
    growthRate: "medium_fast", baseExp: 52, catchRate: 170, compatibleTMs: ["tm01_body_slam"],
    evolvesTo: "skyveer", evolvesAtLevel: 20,
    learnset: [
      { level: 1,  move: "peck"       },
      { level: 5,  move: "gust"       },
      { level: 12, move: "wing_strike"},
      { level: 20, move: "quick_jab"  },
    ],
    description: "A small, sharp-beaked Morph that circles high and dives on prey.",
  },
  skyveer: {
    id: "skyveer", name: "Skyveer", types: ["Wing"],
    baseStats: { hp: 55, atk: 60, def: 55, spd: 80 },
    growthRate: "medium_fast", baseExp: 122, catchRate: 75, compatibleTMs: ["tm01_body_slam"],
    evolvesTo: "tempestral", evolvesAtLevel: 36,
    learnset: [
      { level: 1,  move: "peck"       },
      { level: 5,  move: "gust"       },
      { level: 12, move: "wing_strike"},
      { level: 20, move: "quick_jab"  },
      { level: 28, move: "sky_dive"   },
    ],
    description: "Skyveer's wingspan has doubled. It hunts across mountain ridges.",
  },
  tempestral: {
    id: "tempestral", name: "Tempestral", types: ["Wing"],
    baseStats: { hp: 75, atk: 80, def: 70, spd: 100 },
    growthRate: "medium_fast", baseExp: 196, catchRate: 45, compatibleTMs: ["tm01_body_slam"],
    evolvesTo: null, evolvesAtLevel: null,
    learnset: [
      { level: 1,  move: "peck"       },
      { level: 5,  move: "gust"       },
      { level: 12, move: "wing_strike"},
      { level: 20, move: "quick_jab"  },
      { level: 28, move: "sky_dive"   },
      { level: 40, move: "hyper_voice"},
    ],
    description: "Tempestral commands storms. Its cry triggers sudden downpours.",
  },

  // ── Route 1: Sprout chain ─────────────────────────────────────────────────
  chittik: {
    id: "chittik", name: "Chittik", types: ["Sprout"],
    baseStats: { hp: 30, atk: 35, def: 35, spd: 45 },
    growthRate: "fast", baseExp: 53, catchRate: 190, compatibleTMs: ["tm01_body_slam"],
    evolvesTo: "mantipule", evolvesAtLevel: 10,
    learnset: [
      { level: 1, move: "bug_bite"    },
      { level: 5, move: "pin_volley"  },
      { level: 9, move: "spore_cloud" },
    ],
    description: "A chitinous bug-Morph with clacking mandibles and tireless energy.",
  },
  mantipule: {
    id: "mantipule", name: "Mantipule", types: ["Sprout"],
    baseStats: { hp: 55, atk: 60, def: 55, spd: 65 },
    growthRate: "fast", baseExp: 140, catchRate: 75, compatibleTMs: ["tm01_body_slam"],
    evolvesTo: null, evolvesAtLevel: null,
    learnset: [
      { level: 1,  move: "bug_bite"    },
      { level: 5,  move: "pin_volley"  },
      { level: 9,  move: "spore_cloud" },
      { level: 15, move: "wing_strike" },
      { level: 22, move: "karate_chop" },
    ],
    description: "A razor-armed insect that can slice through bark with a single swipe.",
  },

  // ── Route 1: Static chain (ultra-rare) ────────────────────────────────────
  voltquill: {
    id: "voltquill", name: "Voltquill", types: ["Static"],
    baseStats: { hp: 35, atk: 55, def: 30, spd: 90 },
    growthRate: "medium_fast", baseExp: 82, catchRate: 45, compatibleTMs: ["tm01_body_slam"],
    evolvesTo: "fulmirex", evolvesAtLevel: 25,
    learnset: [
      { level: 1,  move: "quick_jab"   },
      { level: 5,  move: "static_jolt" },
      { level: 14, move: "spark"        },
      { level: 25, move: "thunder_arc"  },
    ],
    description: "Extremely rare. Each quill can discharge 10,000 volts independently.",
  },
  fulmirex: {
    id: "fulmirex", name: "Fulmirex", types: ["Static"],
    baseStats: { hp: 55, atk: 75, def: 50, spd: 105 },
    growthRate: "medium_fast", baseExp: 142, catchRate: 45, compatibleTMs: ["tm01_body_slam"],
    evolvesTo: "arcfowl", evolvesAtLevel: 40,
    learnset: [
      { level: 1,  move: "quick_jab"   },
      { level: 5,  move: "static_jolt" },
      { level: 14, move: "spark"        },
      { level: 25, move: "thunder_arc"  },
      { level: 35, move: "sky_dive"     },
    ],
    description: "Fulmirex generates a perpetual electromagnetic field around itself.",
  },
  arcfowl: {
    id: "arcfowl", name: "Arcfowl", types: ["Static", "Wing"],
    baseStats: { hp: 75, atk: 95, def: 70, spd: 120 },
    growthRate: "medium_fast", baseExp: 218, catchRate: 45, compatibleTMs: ["tm01_body_slam"],
    evolvesTo: null, evolvesAtLevel: null,
    learnset: [
      { level: 1,  move: "quick_jab"   },
      { level: 5,  move: "static_jolt" },
      { level: 14, move: "spark"        },
      { level: 25, move: "thunder_arc"  },
      { level: 35, move: "sky_dive"     },
      { level: 50, move: "hyper_voice"  },
    ],
    description: "Legend says Arcfowl guided sailors through storms by riding lightning bolts.",
  },

  // ── Route 2: Stone chain ──────────────────────────────────────────────────
  pebbling: {
    id: "pebbling", name: "Pebbling", types: ["Stone"],
    baseStats: { hp: 50, atk: 50, def: 70, spd: 30 },
    growthRate: "slow", baseExp: 60, catchRate: 160, compatibleTMs: ["tm01_body_slam"],
    evolvesTo: "cragmaul", evolvesAtLevel: 22,
    learnset: [
      { level: 1,  move: "tackle"     },
      { level: 5,  move: "stone_toss" },
      { level: 14, move: "rock_slide" },
      { level: 22, move: "body_slam"  },
    ],
    description: "A round, slow-moving pebble-Morph with a deceptively tough shell.",
  },
  cragmaul: {
    id: "cragmaul", name: "Cragmaul", types: ["Stone"],
    baseStats: { hp: 70, atk: 80, def: 100, spd: 40 },
    growthRate: "slow", baseExp: 164, catchRate: 75, compatibleTMs: ["tm01_body_slam"],
    evolvesTo: null, evolvesAtLevel: null,
    learnset: [
      { level: 1,  move: "tackle"      },
      { level: 5,  move: "stone_toss"  },
      { level: 14, move: "rock_slide"  },
      { level: 22, move: "body_slam"   },
      { level: 32, move: "iron_tail"   },
    ],
    description: "Cragmaul's granite fists can shatter boulders. It rarely moves unless provoked.",
  },

  // ── Route 2: Toxin chain ──────────────────────────────────────────────────
  oozelet: {
    id: "oozelet", name: "Oozelet", types: ["Toxin"],
    baseStats: { hp: 40, atk: 40, def: 35, spd: 55 },
    growthRate: "medium_fast", baseExp: 55, catchRate: 170, compatibleTMs: ["tm01_body_slam"],
    evolvesTo: "vexgore", evolvesAtLevel: 24,
    learnset: [
      { level: 1,  move: "tackle"    },
      { level: 5,  move: "acid_spit" },
      { level: 15, move: "toxic_fang"},
      { level: 24, move: "body_slam" },
    ],
    description: "A dripping blob of toxin. Its slime trail corrodes stone over time.",
  },
  vexgore: {
    id: "vexgore", name: "Vexgore", types: ["Toxin"],
    baseStats: { hp: 65, atk: 65, def: 60, spd: 70 },
    growthRate: "medium_fast", baseExp: 146, catchRate: 75, compatibleTMs: ["tm01_body_slam"],
    evolvesTo: null, evolvesAtLevel: null,
    learnset: [
      { level: 1,  move: "tackle"     },
      { level: 5,  move: "acid_spit"  },
      { level: 15, move: "toxic_fang" },
      { level: 24, move: "body_slam"  },
      { level: 34, move: "shadow_creep"},
    ],
    description: "Vexgore secretes a fast-acting venom that can put a Morph to sleep in seconds.",
  },

  // ── Route 1 wild (no starter chain) ──────────────────────────────────────
  spriglit: {
    id: "spriglit", name: "Spriglit", types: ["Nature"],
    baseStats: { hp: 38, atk: 42, def: 42, spd: 40 },
    growthRate: "medium_fast", baseExp: 50, catchRate: 190, compatibleTMs: ["tm01_body_slam"],
    evolvesTo: null, evolvesAtLevel: null,
    learnset: [
      { level: 1, move: "tackle"    },
      { level: 5, move: "vine_lash" },
      { level: 9, move: "heal_bud"  },
    ],
    description: "A common weed-sprite found in tall grass. Surprisingly affectionate when tamed.",
  },

  // ── Brindlewood gift: Umbra chain ─────────────────────────────────────────
  nyxen: {
    id: "nyxen", name: "Nyxen", types: ["Umbra"],
    baseStats: { hp: 38, atk: 50, def: 35, spd: 55 },
    growthRate: "medium_fast", baseExp: 58, catchRate: 45, compatibleTMs: ["tm01_body_slam"],
    evolvesTo: "vesperel", evolvesAtLevel: 24,
    learnset: [
      { level: 1,  move: "bite"        },
      { level: 5,  move: "quick_jab"   },
      { level: 13, move: "shadow_creep"},
      { level: 24, move: "confuse_ray" },
    ],
    description: "Nyxen is shy around strangers but fiercely loyal to its Tamer.",
  },
  vesperel: {
    id: "vesperel", name: "Vesperel", types: ["Umbra"],
    baseStats: { hp: 58, atk: 70, def: 55, spd: 75 },
    growthRate: "medium_fast", baseExp: 142, catchRate: 45, compatibleTMs: ["tm01_body_slam"],
    evolvesTo: "noctheart", evolvesAtLevel: 42,
    learnset: [
      { level: 1,  move: "bite"        },
      { level: 5,  move: "quick_jab"   },
      { level: 13, move: "shadow_creep"},
      { level: 24, move: "confuse_ray" },
      { level: 34, move: "psy_blast"   },
    ],
    description: "Vesperel moves in near silence. It prefers moonlit routes and fog-covered valleys.",
  },
  noctheart: {
    id: "noctheart", name: "Noctheart", types: ["Umbra", "Mind"],
    baseStats: { hp: 80, atk: 90, def: 70, spd: 90 },
    growthRate: "medium_fast", baseExp: 218, catchRate: 45, compatibleTMs: ["tm01_body_slam"],
    evolvesTo: null, evolvesAtLevel: null,
    learnset: [
      { level: 1,  move: "bite"        },
      { level: 5,  move: "quick_jab"   },
      { level: 13, move: "shadow_creep"},
      { level: 24, move: "confuse_ray" },
      { level: 34, move: "psy_blast"   },
      { level: 50, move: "hyper_voice" },
    ],
    description: "Noctheart reads the deepest fears of its opponents and weaponises them.",
  },
};

// Keep CREATURES as an alias for backward compatibility.
export const CREATURES = SPECIES;

// ─── Creature factory ─────────────────────────────────────────────────────────

export function createCreature(id, level, providedIvs = null) {
  const species = SPECIES[id];
  if (!species) { return null; }

  const lvl  = Math.max(1, level ?? species.learnset[0]?.level ?? 1);
  const ivs  = providedIvs ?? rollIvs();
  const stats = computeStats(species.baseStats, lvl, ivs);

  // Build moveset: take the last ≤4 moves learned at or below this level
  const learned = species.learnset
    .filter((e) => e.level <= lvl)
    .slice(-4)
    .map((e) => MOVES[e.move])
    .filter(Boolean);

  return {
    speciesId:  id,
    id,                       // legacy field
    name:       species.name,
    types:      [...species.types],
    type:       species.types[0], // legacy field for older code
    level:      lvl,
    maxHp:      stats.maxHp,
    hp:         stats.maxHp,
    attack:     stats.attack,
    defense:    stats.defense,
    speed:      stats.speed,
    moves:      learned,
    ivs,
    xp:         totalXpForLevel(species.growthRate, lvl), // total XP at this level
    status:     null,
    statusTurns: 0,
    friendship: 70,
    heldItem:   null,
    baseXpYield: species.baseExp, // legacy field used by old battle code
    catchRate:   species.catchRate,
  };
}

// Returns all moves the species can learn at exactly `level` (used on level-up).
export function getLearnsetMoves(speciesId, level) {
  return (SPECIES[speciesId]?.learnset ?? [])
    .filter((e) => e.level === level)
    .map((e) => MOVES[e.move])
    .filter(Boolean);
}

// Returns the FIRST move learned at exactly `level`, or null. (Legacy helper.)
export function getLearnsetMove(speciesId, level) {
  return getLearnsetMoves(speciesId, level)[0] ?? null;
}

// ─── XP / level progression ───────────────────────────────────────────────────

export function xpToNextLevel(creature) {
  const species = SPECIES[creature.speciesId ?? creature.id];
  const gr = species?.growthRate ?? "medium_fast";
  return totalXpForLevel(gr, creature.level + 1) - creature.xp;
}

// Applies earned XP to a creature, handling level-ups and stat recalculation.
// Returns an array of log messages.
export function applyExperience(creature, amount) {
  const messages = [`${creature.name} gained ${amount} XP!`];
  creature.xp = (creature.xp ?? 0) + amount;

  const species = SPECIES[creature.speciesId ?? creature.id];
  const gr = species?.growthRate ?? "medium_fast";

  let levelled = false;
  while (creature.level < 100) {
    const needed = totalXpForLevel(gr, creature.level + 1);
    if (creature.xp < needed) { break; }
    creature.level += 1;
    levelled = true;

    const newStats = computeStats(species?.baseStats ?? { hp: 40, atk: 40, def: 40, spd: 40 }, creature.level, creature.ivs);
    const hpGain   = newStats.maxHp - creature.maxHp;
    creature.maxHp   = newStats.maxHp;
    creature.attack  = newStats.attack;
    creature.defense = newStats.defense;
    creature.speed   = newStats.speed;
    creature.hp      = Math.min(creature.hp + hpGain, creature.maxHp);
    creature.friendship = Math.min(255, (creature.friendship ?? 70) + 1);
    messages.push(`${creature.name} grew to Level ${creature.level}!`);
  }

  return { messages, levelled };
}
