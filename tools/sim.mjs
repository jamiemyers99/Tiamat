// Headless battle simulator used by tests and the balance report.
import { Battle } from '../src/battle/engine.js';
import { createMon, healMon, maxHp } from '../src/battle/mon.js';
import { chooseEnemyMove } from '../src/battle/ai.js';
import { MOVES } from '../src/data/moves.js';
import { SPECIES } from '../src/data/species.js';
import { effectiveness } from '../src/data/types.js';

// A human-ish player: always picks the attack that looks like it hits hardest.
function greedyMove(b) {
  let best = 0, bv = -1;
  b.p.mon.moves.forEach((m, i) => {
    const mv = MOVES[m.id];
    if (m.pp <= 0) { return; }
    const stab = SPECIES[b.p.mon.species].types.includes(mv.type) ? 1.5 : 1;
    const v = (mv.power || 0) * stab * effectiveness(mv.type, SPECIES[b.e.mon.species].types) * ((mv.acc ?? 100) / 100);
    if (v > bv) { bv = v; best = i; }
  });
  return best;
}

export function headlessUI({ log = false, playerSkill = 3 } = {}) {
  const say = log ? (t) => console.log('  ' + t) : () => {};
  return {
    async intro() {}, async message(t) { say(t); }, async moveAnim() {}, async hitFlash() {}, async hp() {},
    async faint() {}, async sendOut() {}, async withdraw() {}, async statusAnim() {}, async statAnim() {},
    async xp() {}, async levelUp(b, m, st) { say(`${m.species} -> L${st.level}`); }, async learnPrompt() {},
    async capture() {}, async refresh() {}, async end() {}, async charge() {}, async askShift() { return null; },
    async chooseAction(b) {
      if (playerSkill === 'greedy') { return { type: 'move', index: greedyMove(b) }; }
      return { type: 'move', index: chooseEnemyMove(b, b.p, b.e, playerSkill) };
    },
    async chooseSwitch(b) {
      // pick the healthiest remaining
      let best = -1, bv = -1;
      b.p.party.forEach((m, i) => { if (m.hp > 0 && i !== b.p.index) { const v = m.hp / maxHp(m); if (v > bv) { bv = v; best = i; } } });
      return best;
    },
  };
}

export async function simulate(playerParty, enemyParty, opts = {}) {
  const b = new Battle({ playerParty, enemyParty, kind: opts.kind || 'trainer', trainer: opts.trainer || { name: 'Sim', skill: opts.skill ?? 2, items: opts.items || [] }, ui: headlessUI(opts), opts: { expShare: true, ...(opts.battleOpts || {}) } });
  const out = await b.run();
  return { out, turns: b.turn };
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const p = [createMon('cindlet', 12)];
  const e = [createMon('spriglet', 12), createMon('burrlet', 11)];
  const r = await simulate(p, e, { log: true });
  console.log(r);
}
