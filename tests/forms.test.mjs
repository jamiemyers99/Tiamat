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
