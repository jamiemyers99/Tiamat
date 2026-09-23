// Balance report: pits a typical player team at each story checkpoint against every boss,
// for all three starters, and prints win rates.  node tools/balance-sim.mjs [runs]
import { createMon } from '../src/battle/mon.js';
import { TRAINERS } from '../src/data/trainers.js';
import { simulate } from './sim.mjs';

const RUNS = +(process.argv[2] || 40);
const LINES = { spriglet: ['spriglet', 'spriggrove', 'mosswarden'], cindlet: ['cindlet', 'cindreaver', 'pyromane'], puddlet: ['puddlet', 'torrentide', 'maelstrand'] };
const stage = (s, lv) => LINES[s][lv >= 36 ? 2 : lv >= 16 ? 1 : 0];

// [boss, player level, the rest of a sensible team]
const CHECKPOINTS = [
  ['rival1', 5, []],
  ['mossa', 13, [['beakling', 11], ['nibbit', 10]]],
  ['rival2', 16, [['beakling', 14], ['burrlet', 13], ['nyxen', 13]]],
  ['brann', 20, [['skyveer', 19], ['voltquill', 18], ['nyxen', 18], ['burrlet', 17]]],
  ['vesk1', 23, [['skyveer', 21], ['voltquill', 21], ['nyxen', 20], ['pebbling', 20]]],
  ['iskra', 27, [['skyveer', 25], ['cragmaul', 25], ['nyxen', 24], ['voltquill', 24]]],
  ['rival3', 28, [['skyveer', 26], ['cragmaul', 26], ['vesperel', 25], ['fulmirex', 26]]],
  ['maren1', 31, [['skyveer', 29], ['cragmaul', 29], ['vesperel', 29], ['fulmirex', 29], ['lambkin', 28]]],
  ['morrow', 33, [['skyveer', 31], ['cragmaul', 31], ['vesperel', 30], ['fulmirex', 31], ['pugilus', 30]]],
  ['hale', 37, [['skyveer', 35], ['cragmaul', 35], ['vesperel', 34], ['fulmirex', 35], ['pugilus', 34]]],
  ['seren', 42, [['tempestral', 40], ['cragmaul', 40], ['vesperel', 39], ['fulmirex', 40], ['glaciursa', 39]]],
  ['maren2', 44, [['tempestral', 42], ['cragmaul', 42], ['noctheart', 42], ['arcfowl', 42], ['glaciursa', 41]]],
  ['oriel', 47, [['tempestral', 45], ['cragmaul', 45], ['noctheart', 45], ['arcfowl', 45], ['glaciursa', 44]]],
  ['rival4', 51, [['tempestral', 49], ['cragmaul', 49], ['noctheart', 49], ['arcfowl', 49], ['glaciursa', 48]]],
];

const pct = (n) => `${String(Math.round(n * 100)).padStart(3)}%`;
console.log(`boss       lv  ${Object.keys(LINES).map((s) => s.padEnd(9)).join(' ')}  (win rate, ${RUNS} runs, no player items)`);
for (const [boss, lv, rest] of CHECKPOINTS) {
  const row = [];
  for (const s of Object.keys(LINES)) {
    const id = boss.startsWith('rival') ? `${boss}_${s}` : boss;
    const tr = TRAINERS[id];
    let wins = 0;
    for (let i = 0; i < RUNS; i++) {
      const p = [createMon(stage(s, lv), lv), ...rest.map(([sp, l]) => createMon(sp, l))];
      const e = tr.party.map(([sp, l, moves]) => createMon(sp, l, { moves }));
      const r = await simulate(p, e, { trainer: tr, skill: tr.skill, items: tr.items, playerSkill: 'greedy' });
      if (r.out === 'win') { wins++; }
    }
    row.push(pct(wins / RUNS).padEnd(9));
  }
  console.log(`${boss.padEnd(10)} ${String(lv).padStart(2)}  ${row.join(' ')}`);
}
