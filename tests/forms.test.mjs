import './setup.mjs';
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createMon, monFrame, rollSex, sexSymbol, SHINY_ODDS } from '../src/battle/mon.js';
import { SPECIES_LIST } from '../src/data/species.js';
import { migrate } from '../src/core/state.js';

test('every Morph is male or female; Tiamat is always female', () => {
  const seen = new Set();
  for (let i = 0; i < 200; i++) { seen.add(createMon('nibbit', 5).sex); }
  assert.deepEqual([...seen].sort(), ['f', 'm']);
  for (let i = 0; i < 50; i++) { assert.equal(createMon('tiamat', 50).sex, 'f'); }
  assert.equal(rollSex('tiamat'), 'f');
  assert.equal(sexSymbol({ sex: 'f' }), '♀');
  assert.equal(sexSymbol({ sex: 'm' }), '♂');
});

test('shinies are about 1 in 100 and can be forced', () => {
  assert.equal(SHINY_ODDS, 1 / 100);
  let n = 0;
  let seed = 1;
  const rng = () => { seed = (seed * 16807) % 2147483647; return seed / 2147483647; };
  for (let i = 0; i < 20000; i++) { if (createMon('nibbit', 3, { rng }).shiny) { n++; } }
  assert.ok(n > 120 && n < 290, `got ${n} shinies in 20000`);
  assert.equal(createMon('nibbit', 3, { shiny: true }).shiny, true);
});

test('saves from before male/female forms get a stable sex', () => {
  const s = migrate({ party: [{ species: 'nibbit', uid: 7, level: 5 }, { species: 'tiamat', uid: 8, level: 50 }], boxes: [{ name: 'Box 1', slots: [{ species: 'nibbit', uid: 10 }, null] }] });
  assert.equal(s.party[0].sex, 'f');
  assert.equal(s.party[1].sex, 'f');
  assert.equal(s.boxes[0].slots[0].sex, 'm');
  assert.equal(migrate(s).party[0].sex, 'f');
});

test('the sprite atlas has male and female frames for every Morph', () => {
  const atlas = JSON.parse(readFileSync(new URL('../public/assets/sprites/mons.json', import.meta.url))).frames;
  for (const sp of SPECIES_LIST) {
    for (const sex of ['m', 'f']) {
      for (const shiny of [false, true]) {
        for (const view of ['f', 'b', 'i']) {
          const f = monFrame({ species: sp.id, sex, shiny }, view);
          assert.ok(atlas[f], `missing frame ${f}`);
        }
      }
    }
  }
});

test('natures raise one stat and lower another, and lean toward the type', async () => {
  const { NATURES, natureMult, rollNature } = await import('../src/data/natures.js');
  const { calcStats } = await import('../src/battle/mon.js');
  assert.equal(Object.keys(NATURES).length, 25);
  assert.equal(natureMult('Fierce', 'atk'), 1.1);
  assert.equal(natureMult('Fierce', 'spa'), 0.9);
  assert.equal(natureMult('Fierce', 'hp'), 1);
  const a = createMon('nibbit', 50, { nature: 'Fierce', ivs: { hp: 10, atk: 10, def: 10, spa: 10, spd: 10, spe: 10 } });
  const b = createMon('nibbit', 50, { nature: 'Even', ivs: { hp: 10, atk: 10, def: 10, spa: 10, spd: 10, spe: 10 } });
  assert.ok(calcStats(a).atk > calcStats(b).atk && calcStats(a).spa < calcStats(b).spa && calcStats(a).hp === calcStats(b).hp);
  let seed = 7;
  const rng = () => { seed = (seed * 16807) % 2147483647; return seed / 2147483647; };
  let atkUp = 0;
  for (let i = 0; i < 4000; i++) { if (NATURES[rollNature(['Brawl'], rng)][0] === 'atk') { atkUp++; } }
  assert.ok(atkUp / 4000 > 0.35, `Brawl should lean to Attack natures (${atkUp})`);
  assert.ok(createMon('nibbit', 5).nature in NATURES);
});

test('wild Morphs stay close to half male, half female', async () => {
  const { balancedSex } = await import('../src/battle/mon.js');
  const tally = { m: 0, f: 0 };
  for (let i = 0; i < 40; i++) { balancedSex('nibbit', tally); assert.ok(Math.abs(tally.m - tally.f) <= 6, JSON.stringify(tally)); }
  assert.equal(balancedSex('tiamat', tally), 'f');
});

test('starter lines only learn their own signature moves; old saves are updated', async () => {
  const { SPECIES, SPECIES_LIST } = await import('../src/data/species.js');
  const { STARTER_LINES } = await import('../src/battle/mon.js');
  const sig = new Set(STARTER_LINES.flatMap((id) => SPECIES[id].learn.map(([, mv]) => mv)));
  for (const sp of SPECIES_LIST) {
    if (STARTER_LINES.includes(sp.id)) { continue; }
    for (const [, mv] of sp.learn) { assert.ok(!sig.has(mv), `${sp.id} shares starter move ${mv}`); }
  }
  const s = migrate({ party: [{ species: 'cindreaver', uid: 3, level: 30, moves: [{ id: 'flare_bite', pp: 1, max: 15 }, { id: 'rubble_fall', pp: 9, max: 10 }] }] });
  const ids = s.party[0].moves.map((m) => m.id);
  assert.ok(ids.includes('rubble_fall'), 'Tech Disc moves are kept');
  assert.ok(!ids.includes('flare_bite') && ids.includes('umbral_flare'), ids.join());
});

test('evolved Morphs have their own signature moves, stronger than the basic ones', async () => {
  const { SPECIES_LIST } = await import('../src/data/species.js');
  const { MOVES } = await import('../src/data/moves.js');
  const learners = {};
  for (const sp of SPECIES_LIST) { for (const [, mv] of sp.learn) { (learners[mv] = learners[mv] || new Set()).add(sp.id); } }
  const sigs = ['eye_of_the_storm', 'riftbreaker', 'tyrant_skyfall', 'peakfall', 'siren_sting', 'dusk_hunt', 'champions_gauntlet'];
  for (const id of sigs) {
    assert.ok(MOVES[id], id);
    assert.equal(learners[id].size, 1, `${id} should belong to one Morph`);
    assert.ok(MOVES[id].power >= 90, `${id} should hit hard`);
  }
});
