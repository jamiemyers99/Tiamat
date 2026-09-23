// Balance report, using the same difficulty curve as the game (src/data/difficulty.js).
//   node tools/balance-sim.mjs [runs]
// 1. Early game: how many wild battles a fresh level-5 starter wins in a row with no healing.
// 2. Wild battles along the route: HP a typical team loses per wild fight in each area.
// 3. Bosses: win rate of a sensible team at each story checkpoint, per starter.
import { createMon, maxHp } from '../src/battle/mon.js';
import { TRAINERS } from '../src/data/trainers.js';
import { ENCOUNTERS, rollEncounter } from '../src/data/encounters.js';
import { Battle } from '../src/battle/engine.js';
import { tierOf, wildIvs, trainerIvs, trainerSkill, wildSkill, partnerIvs } from '../src/data/difficulty.js';
import { simulate, headlessUI } from './sim.mjs';

const RUNS = +(process.argv[2] || 40);
const LINES = { spriglet: ['spriglet', 'spriggrove', 'mosswarden'], cindlet: ['cindlet', 'cindreaver', 'pyromane'], puddlet: ['puddlet', 'torrentide', 'maelstrand'] };
const stage = (s, lv) => LINES[s][lv >= 36 ? 2 : lv >= 16 ? 1 : 0];
const pct = (n) => `${String(Math.round(n * 100)).padStart(3)}%`;
const partner = (sp, lv) => createMon(sp, lv, { ivs: partnerIvs() });
const caught = (sp, lv) => createMon(sp, lv); // settled genes: 0–31

async function wildFight(party, map, kind = 'grass') {
  const tier = tierOf(map);
  const enc = rollEncounter(map, kind, 12 * 60);
  const foe = createMon(enc.species, enc.level, { ivs: wildIvs(tier) });
  const b = new Battle({ playerParty: party, enemyParty: [foe], kind: 'wild', ui: headlessUI({ playerSkill: 'greedy' }), opts: { wildSkill: wildSkill(tier) } });
  return b.run();
}

// ── 1. first steps on Route 1 ───────────────────────────────────────────────
console.log('\nRoute 1 with a fresh level-5 starter: wild wins in a row before fainting (no healing)');
for (const s of Object.keys(LINES)) {
  let total = 0;
  for (let i = 0; i < RUNS * 3; i++) {
    const me = partner(s, 5);
    let n = 0;
    while (me.hp > 0 && n < 40) { if ((await wildFight([me], 'route1')) === 'win') { n++; } else { break; } }
    total += n;
  }
  console.log(`  ${s.padEnd(9)} ${(total / (RUNS * 3)).toFixed(1)}`);
}

// ── 2. wild fights along the journey ───────────────────────────────────────
const AREAS = [
  ['route1', 6, []], ['route2', 14, [['beakling', 12]]], ['thornwild', 15, [['beakling', 13], ['nyxen', 13]]],
  ['route3', 21, [['skyveer', 19], ['nyxen', 19]]], ['coldforge_mines', 23, [['skyveer', 21], ['voltquill', 21]], 'cave'],
  ['route4', 29, [['skyveer', 27], ['cragmaul', 27]]], ['route5', 33, [['skyveer', 31], ['vesperel', 30]], 'water'],
  ['route6', 38, [['skyveer', 36], ['cragmaul', 36]]], ['abyssal_rift', 46, [['tempestral', 44], ['cragmaul', 44]], 'cave'],
];
console.log('\nWild battles by area: tier, wild levels, avg HP% the lead (your starter line) loses per fight');
const STARTERS = Object.keys(LINES);
for (const [map, lv, rest, kind = 'grass'] of AREAS) {
  let lost = 0;
  for (let i = 0; i < RUNS * 3; i++) {
    const lead = partner(stage(STARTERS[i % 3], lv), lv);
    const before = lead.hp / maxHp(lead);
    await wildFight([lead, ...rest.map(([sp, l]) => caught(sp, l))], map, kind);
    lost += before - Math.max(0, lead.hp) / maxHp(lead);
  }
  const table = ENCOUNTERS[map][kind];
  const lo = Math.min(...table.map((e) => e[1])), hi = Math.max(...table.map((e) => e[2]));
  console.log(`  ${map.padEnd(16)} tier ${tierOf(map)}  wild L${lo}-${hi}  player L${lv}  HP lost ${pct(lost / (RUNS * 3))}`);
}

// ── 3. bosses ───────────────────────────────────────────────────────────────
// [boss, where the fight happens, player level, the rest of a sensible team]
const CHECKPOINTS = [
  ['rival1', 'marsh_lab', 5, []],
  ['mossa', 'brindlewood_trial', 13, [['beakling', 11], ['nibbit', 10]]],
  ['rival2', 'thornwild', 16, [['beakling', 14], ['burrlet', 13], ['nyxen', 13]]],
  ['brann', 'saltreach_trial', 20, [['skyveer', 19], ['voltquill', 18], ['nyxen', 18], ['burrlet', 17]]],
  ['vesk1', 'coldforge_mines', 23, [['skyveer', 21], ['voltquill', 21], ['nyxen', 20], ['pebbling', 20]]],
  ['iskra', 'gearhollow_trial', 27, [['skyveer', 25], ['cragmaul', 25], ['nyxen', 24], ['voltquill', 24]]],
  ['rival3', 'gearhollow', 28, [['skyveer', 26], ['cragmaul', 26], ['vesperel', 25], ['fulmirex', 26]]],
  ['maren1', 'hollowmere', 31, [['skyveer', 29], ['cragmaul', 29], ['vesperel', 29], ['fulmirex', 29], ['lambkin', 28]]],
  ['morrow', 'hollowmere_trial', 33, [['skyveer', 31], ['cragmaul', 31], ['vesperel', 30], ['fulmirex', 31], ['pugilus', 30]]],
  ['hale', 'frostspire_trial', 37, [['skyveer', 35], ['cragmaul', 35], ['vesperel', 34], ['fulmirex', 35], ['pugilus', 34]]],
  ['seren', 'riftgate_trial', 42, [['tempestral', 40], ['cragmaul', 40], ['vesperel', 39], ['fulmirex', 40], ['glaciursa', 39]]],
  ['maren2', 'sunken_chapel', 44, [['tempestral', 42], ['cragmaul', 42], ['noctheart', 42], ['arcfowl', 42], ['glaciursa', 41]]],
  ['oriel', 'cradle', 47, [['tempestral', 45], ['cragmaul', 45], ['noctheart', 45], ['arcfowl', 45], ['glaciursa', 44]]],
  ['rival4', 'spire_crown', 51, [['tempestral', 49], ['cragmaul', 49], ['noctheart', 49], ['arcfowl', 49], ['glaciursa', 48]]],
];
console.log(`\nboss       tier  lv  ${Object.keys(LINES).map((s) => s.padEnd(9)).join(' ')}  (win rate, ${RUNS} runs, no player items)`);
for (const [boss, map, lv, rest] of CHECKPOINTS) {
  const tier = tierOf(map);
  const row = [];
  for (const s of Object.keys(LINES)) {
    const id = boss.startsWith('rival') ? `${boss}_${s}` : boss;
    const base = TRAINERS[id];
    const tr = { ...base, skill: trainerSkill(tier, base) };
    const ivs = trainerIvs(tier, base);
    let wins = 0;
    for (let i = 0; i < RUNS; i++) {
      const p = [partner(stage(s, lv), lv), ...rest.map(([sp, l]) => caught(sp, l))];
      const e = tr.party.map(([sp, l, moves]) => createMon(sp, l, { moves, ivs }));
      const r = await simulate(p, e, { trainer: tr, skill: tr.skill, items: tr.items, playerSkill: 'greedy' });
      if (r.out === 'win') { wins++; }
    }
    row.push(pct(wins / RUNS).padEnd(9));
  }
  console.log(`${boss.padEnd(10)}  ${tier}   ${String(lv).padStart(2)}  ${row.join(' ')}`);
}
