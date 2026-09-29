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

test('Lullaby Siphon: the Twinklit line learns it at 42; it puts the foe to sleep and drains HP', async () => {
  const { SPECIES } = await import('../src/data/species.js');
  const { MOVES } = await import('../src/data/moves.js');
  for (const id of ['twinklit', 'lumelynx', 'seraphelis']) {
    assert.ok(SPECIES[id].learn.some(([lv, mv]) => mv === 'lullaby_siphon' && lv >= 40 && lv <= 50), `${id} learns it between 40 and 50`);
  }
  const lvls = SPECIES.seraphelis.learn.map(([lv]) => lv).filter((lv) => lv >= 40 && lv <= 50);
  assert.equal(new Set(lvls).size, lvls.length, 'it has a level of its own');
  const user = createMon('seraphelis', 45);
  user.hp = Math.floor(maxHp(user) / 2);
  const foe = createMon('cragmaul', 40);
  const b = new Battle({ playerParty: [user], enemyParty: [foe], kind: 'wild', ui: headlessUI(), rng: () => 0.5 });
  const hpBefore = user.hp, foeBefore = foe.hp;
  await b.useMove(b.p, b.e, MOVES.lullaby_siphon, 0);
  assert.ok(foe.hp < foeBefore, 'it deals damage');
  assert.ok(foe.hp > 0);
  assert.equal(foe.status, 'sleep', 'the foe falls asleep');
  assert.ok(user.hp > hpBefore, 'the user recovers HP');
  // it never knocks the foe out, so it's safe to use before throwing a capsule
  const weak = createMon('nibbit', 5);
  weak.hp = 3;
  const b2 = new Battle({ playerParty: [createMon('seraphelis', 60)], enemyParty: [weak], kind: 'wild', ui: headlessUI(), rng: () => 0.5 });
  await b2.useMove(b2.p, b2.e, MOVES.lullaby_siphon, 0);
  assert.equal(weak.hp, 1);
  assert.equal(weak.status, 'sleep');
});

test('sleeping (or frozen) wild Morphs are much easier to catch, like the classics', async () => {
  const rate = async (status) => {
    let got = 0;
    for (let i = 0; i < 1500; i++) {
      const wild = createMon('cragmaul', 30);
      wild.hp = Math.ceil(maxHp(wild) / 2);
      wild.status = status;
      const b = new Battle({ playerParty: [createMon('seraphelis', 45)], enemyParty: [wild], kind: 'wild', ui: headlessUI() });
      if ((await b.throwCapsule('capsule')) === 'caught') { got++; }
    }
    return got / 1500;
  };
  const awake = await rate(null), asleep = await rate('sleep'), poisoned = await rate('poison');
  assert.ok(asleep > awake * 1.8, `asleep ${asleep} vs awake ${awake}`);
  assert.ok(poisoned > awake * 1.15 && poisoned < asleep, `poisoned ${poisoned}`);
});

test('healMon restores HP, PP and status', () => {
  const m = createMon('puddlet', 10);
  m.hp = 1; m.status = 'poison'; m.moves[0].pp = 0;
  healMon(m);
  assert.equal(m.hp, maxHp(m));
  assert.equal(m.status, null);
  assert.equal(m.moves[0].pp, m.moves[0].max);
});
