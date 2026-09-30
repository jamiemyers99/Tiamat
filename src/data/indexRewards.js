// Dr. Marsh's Index rewards: visit him in Rootmere after catching 25, 50, 75 and 100 Morphs — and all of them.
// Each one gives money and goodies (Capsules, medicine, and Tech Discs with strong moves). A complete Index
// (every Morph except the one hatched as the final reward) earns the Radiant Charm and the Mysterious Egg.
import { SPECIES, SPECIES_LIST } from './species.js';

export const INDEX_TOTAL = SPECIES_LIST.filter((s) => !s.hatchOnly).length;

export const INDEX_REWARDS = [
  { at: 25, money: 2500, items: [['prime_capsule', 5], ['strong_tonic', 3], ['td19', 1]] },
  { at: 50, money: 5000, items: [['apex_capsule', 5], ['full_tonic', 3], ['rekindle_seed', 2], ['td20', 1], ['td21', 1]] },
  { at: 75, money: 7500, items: [['dusk_capsule', 5], ['swift_capsule', 5], ['panacea', 3], ['growth_fruit', 2], ['td22', 1], ['td23', 1]] },
  { at: 100, money: 10000, items: [['apex_capsule', 10], ['bloom_seed', 3], ['growth_fruit', 3], ['focus_drop', 5], ['td24', 1], ['td25', 1], ['td26', 1]] },
  { at: 'all', money: 20000, items: [['radiant_charm', 1], ['mystery_egg', 1]] },
];

export const rewardFlag = (r) => `index_reward_${r.at}`;
export const needFor = (r) => (r.at === 'all' ? INDEX_TOTAL : r.at);

// How many Morphs count towards the Index (the hatched legendary doesn't).
export function indexCount(caughtIds) {
  return caughtIds.filter((id) => SPECIES[id] && !SPECIES[id].hatchOnly).length;
}

// Rewards earned but not yet collected, in order.
export function dueRewards(caughtIds, flags) {
  const n = indexCount(caughtIds);
  return INDEX_REWARDS.filter((r) => n >= needFor(r) && !flags[rewardFlag(r)]);
}

// The next reward still to earn (or null when they're all earned).
export function nextReward(caughtIds) {
  const n = indexCount(caughtIds);
  return INDEX_REWARDS.find((r) => n < needFor(r)) || null;
}
