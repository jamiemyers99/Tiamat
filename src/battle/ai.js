// Enemy move selection. skill 0 = wild (mostly random), 1 = ordinary Tamer,
// 2 = veteran, 3 = Warden / rival / boss (plays to win).
import { MOVES } from '../data/moves.js';
import { SPECIES } from '../data/species.js';
import { effectiveness } from '../data/types.js';
import { calcStats, maxHp } from './mon.js';

function estimate(self, foe, move) {
  if (move.cat === 'status' || !move.power) { return 0; }
  const eff = effectiveness(move.type, SPECIES[foe.mon.species].types);
  if (eff === 0) { return -1; }
  const st = calcStats(self.mon);
  const ft = calcStats(foe.mon);
  const phys = move.cat === 'phys';
  const A = phys ? st.atk : st.spa;
  const D = phys ? ft.def : ft.spd;
  const stab = SPECIES[self.mon.species].types.includes(move.type) ? 1.5 : 1;
  let power = move.power;
  if (move.fx.multi) { power *= 3; }
  if (move.fx.fixed === 'level') { return self.mon.level; }
  if (move.fx.charge) { power *= 0.55; }
  const L = self.mon.level;
  const dmg = ((((2 * L) / 5 + 2) * power * A / D) / 50 + 2) * stab * eff * 0.92;
  return dmg * ((move.acc ?? 100) / 100);
}

export function chooseEnemyMove(battle, self, foe, skill = 1) {
  const moves = self.mon.moves;
  const usable = moves.map((m, i) => ({ m, i })).filter(({ m }) => m.pp > 0);
  if (!usable.length) { return 0; }
  const rng = battle.rng;
  if (skill === 0) {
    // wild: random, but prefer attacks slightly
    const weights = usable.map(({ m }) => (MOVES[m.id].cat === 'status' ? 0.6 : 1));
    let r = rng() * weights.reduce((a, b) => a + b, 0);
    for (let k = 0; k < usable.length; k++) { r -= weights[k]; if (r <= 0) { return usable[k].i; } }
    return usable[0].i;
  }
  const foeHp = foe.mon.hp;
  const hpFrac = self.mon.hp / maxHp(self.mon);
  const scored = usable.map(({ m, i }) => {
    const mv = MOVES[m.id];
    let score = 0;
    if (mv.cat !== 'status') {
      const d = estimate(self, foe, mv);
      if (d < 0) { score = -100; }
      else {
        score = d;
        if (d >= foeHp) { score += 60 + (mv.prio > 0 ? 40 : 0); }
      }
    } else {
      const fx = mv.fx;
      if (fx.heal) { score = hpFrac < 0.45 ? 80 : (hpFrac > 0.8 ? -50 : 5); }
      else if (fx.protect) { score = self.protectCount > 0 ? -50 : 8; }
      else if (fx.status) { score = foe.mon.status ? -60 : (fx.status === 'sleep' ? 45 : 30); }
      else if (fx.confuse) { score = foe.confused ? -40 : 22; }
      else if (fx.seed) { score = foe.seeded || SPECIES[foe.mon.species].types.includes('Nature') ? -40 : 28; }
      else if (fx.stat) {
        const target = fx.target === 'self' ? self : foe;
        const vals = Object.entries(fx.stat);
        const room = vals.every(([k, v]) => (v > 0 ? target.stages[k] < 2 : target.stages[k] > -2));
        score = room ? (hpFrac > 0.6 ? 25 : 6) : -40;
        if (battle.turn > 4) { score -= 12; }
      }
    }
    // imperfection for weaker Tamers
    const noise = skill >= 3 ? 8 : skill === 2 ? 18 : 35;
    score += rng() * noise;
    return { i, score };
  });
  scored.sort((a, b) => b.score - a.score);
  return scored[0].i;
}
