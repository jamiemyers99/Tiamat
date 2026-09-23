import './setup.mjs';
import test from 'node:test';
import assert from 'node:assert/strict';
import { createMon, calcStats, maxHp, addXp, evolutionTarget, healMon } from '../src/battle/mon.js';
import { Battle } from '../src/battle/engine.js';
import { simulate, headlessUI } from '../tools/sim.mjs';

test('createMon builds a healthy Morph with up to four moves', () => {
  const m = createMon('cindlet', 12);
  assert.equal(m.level, 12);
  assert.equal(m.hp, maxHp(m));
  assert.ok(m.moves.length >= 1 && m.moves.length <= 4);
  const st = calcStats(m);
  for (const k of ['hp', 'atk', 'def', 'spa', 'spd', 'spe']) { assert.ok(st[k] > 0, k); }
});

test('levelling up and evolution thresholds', () => {
  const m = createMon('spriglet', 15);
  assert.equal(evolutionTarget(m), null);
  addXp(m, 1e6);
  assert.ok(m.level > 15);
  assert.equal(evolutionTarget(m), 'spriggrove');
});

test('a much stronger team always wins; a much weaker one always loses', async () => {
  for (let i = 0; i < 5; i++) {
    const w = await simulate([createMon('pyromane', 60)], [createMon('nibbit', 5)]);
    assert.equal(w.out, 'win');
    const l = await simulate([createMon('nibbit', 3)], [createMon('riftwyrm', 70)]);
    assert.equal(l.out, 'lose');
  }
});

test('the Covenant Capsule always catches', async () => {
  const party = [createMon('mosswarden', 50)];
  const ui = { ...headlessUI(), chooseAction: async () => ({ type: 'item', item: 'covenant_capsule' }) };
  const b = new Battle({ playerParty: party, enemyParty: [createMon('tiamat', 50)], kind: 'wild', ui, opts: { noRun: true } });
  const out = await b.run();
  assert.equal(out, 'caught');
  assert.equal(b.caught.species, 'tiamat');
});

test('healMon restores HP, PP and status', () => {
  const m = createMon('puddlet', 10);
  m.hp = 1; m.status = 'poison'; m.moves[0].pp = 0;
  healMon(m);
  assert.equal(m.hp, maxHp(m));
  assert.equal(m.status, null);
  assert.equal(m.moves[0].pp, m.moves[0].max);
});
