// Difficulty curve. Every area of the Reach has a "tier" (0 = Rootmere … 7 = the Riven, see
// region.js). Wild Morphs and Tamers get tougher tier by tier — softer genes and sloppier tactics
// near home, sharp genes and clever tactics out by the Riven — the way the classic games ramp up.
import { REGION } from './region.js';
import { STAT_KEYS } from '../battle/mon.js';

export const MAX_TIER = 7;

export function tierOf(mapId) {
  const id = REGION.locate(mapId || '');
  const p = REGION.points.find((q) => q.id === id);
  return p ? p.tier : 3;
}

const clampTier = (t) => Math.max(0, Math.min(MAX_TIER, t | 0));

// Wild Morphs: random genes (IVs 0–31), capped low in the early areas.
export const WILD_IV_CAP = [5, 9, 13, 17, 21, 25, 29, 31];
// Tamers use fixed genes that rise with the area; Wardens, rivals and bosses a little higher.
export const TAMER_IV = [0, 3, 6, 9, 12, 15, 18, 21];
export const BOSS_IV = [10, 12, 14, 16, 18, 20, 21, 22];

function fill(fn) {
  const o = {};
  for (const k of STAT_KEYS) { o[k] = fn(k); }
  return o;
}

export function wildIvs(tier, rng = Math.random) {
  const cap = WILD_IV_CAP[clampTier(tier)];
  return fill(() => Math.floor(rng() * (cap + 1)));
}

export function isBoss(trainer) {
  return !!trainer && (trainer.skill ?? 1) >= 3;
}

export function trainerIvs(tier, trainer) {
  const t = clampTier(tier);
  const v = isBoss(trainer) ? BOSS_IV[t] : TAMER_IV[t];
  return fill(() => v);
}

// How well a Tamer plays (see battle/ai.js): early Tamers make mistakes, bosses sharpen up after Brindlewood.
export function trainerSkill(tier, trainer) {
  const t = clampTier(tier);
  const s = trainer?.skill ?? 1;
  if (isBoss(trainer)) { return t <= 1 ? 2 : 3; }
  return Math.min(s, t <= 1 ? 1 : 2);
}

// Wild Morphs pick moves at random for most of the journey; past Rimepass they start to fight back properly.
export function wildSkill(tier) {
  return clampTier(tier) >= 6 ? 1 : 0;
}

// Your partner Morphs (the starter, gifts) are healthy specimens.
export function partnerIvs(rng = Math.random) {
  return fill(() => 20 + Math.floor(rng() * 12));
}

// Once caught, a Morph settles in: each gene gets a second roll and keeps the better one,
// so Morphs caught near home aren't stuck with their soft wild genes forever.
export function settleCaught(mon, rng = Math.random) {
  for (const k of STAT_KEYS) { mon.ivs[k] = Math.max(mon.ivs[k] ?? 0, Math.floor(rng() * 32)); }
}
