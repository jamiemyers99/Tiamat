// XP / level system — Gen-1 growth rate formulas, stat computation, XP yield.
// Exports: GROWTH_RATES, totalXpForLevel, levelForTotalXp, xpProgressInLevel,
//          xpYield, computeStats, rollIvs

// Gen-1 growth rate formulas — total XP required to reach level n.
export const GROWTH_RATES = {
  fast:        (n) => Math.floor(0.8 * n ** 3),
  medium_fast: (n) => n ** 3,
  medium_slow: (n) => Math.max(0, Math.floor((6 / 5) * n ** 3 - 15 * n ** 2 + 100 * n - 140)),
  slow:        (n) => Math.floor(1.25 * n ** 3),
};

export function totalXpForLevel(growthRate, level) {
  if (level <= 1) { return 0; }
  return (GROWTH_RATES[growthRate] ?? GROWTH_RATES.medium_fast)(level);
}

export function levelForTotalXp(growthRate, totalXp) {
  const fn = GROWTH_RATES[growthRate] ?? GROWTH_RATES.medium_fast;
  for (let lvl = 1; lvl <= 99; lvl++) {
    if (totalXp < fn(lvl + 1)) { return lvl; }
  }
  return 100;
}

export function xpProgressInLevel(growthRate, totalXp) {
  const lvl    = levelForTotalXp(growthRate, totalXp);
  const baseXp = totalXpForLevel(growthRate, lvl);
  const nextXp = totalXpForLevel(growthRate, lvl + 1);
  return { level: lvl, into: totalXp - baseXp, span: Math.max(1, nextXp - baseXp) };
}

// Gen-1 XP yield formula.
// baseExp: species base experience value
// foeLevel: level of the defeated foe
// isTrainer: trainer battles grant 1.5× XP
// ownerCount: participating party members (defaults to 1)
export function xpYield({ baseExp, foeLevel, isTrainer = false, ownerCount = 1 }) {
  const trainerBonus = isTrainer ? 1.5 : 1.0;
  return Math.max(1, Math.floor((baseExp * foeLevel * trainerBonus) / (7 * ownerCount)));
}

// Roll random IVs (0–15) for each stat.
export function rollIvs() {
  return {
    hp:  Math.floor(Math.random() * 16),
    atk: Math.floor(Math.random() * 16),
    def: Math.floor(Math.random() * 16),
    spd: Math.floor(Math.random() * 16),
  };
}

// Gen-1 stat formula — derives all combat stats from base stats, level, and IVs.
export function computeStats(baseStats, level, ivs) {
  const iv = ivs ?? { hp: 8, atk: 8, def: 8, spd: 8 };
  return {
    maxHp:   Math.floor(((baseStats.hp  + iv.hp)  * 2 * level) / 100) + level + 10,
    attack:  Math.floor(((baseStats.atk + iv.atk) * 2 * level) / 100) + 5,
    defense: Math.floor(((baseStats.def + iv.def) * 2 * level) / 100) + 5,
    speed:   Math.floor(((baseStats.spd + iv.spd) * 2 * level) / 100) + 5,
  };
}
