import './setup.mjs';
import test from 'node:test';
import assert from 'node:assert/strict';
import { SPECIES, validateSpecies } from '../src/data/species.js';
import { MOVES } from '../src/data/moves.js';
import { ITEMS } from '../src/data/items.js';
import { TRAINERS, RIVAL_PICK } from '../src/data/trainers.js';
import { ENCOUNTERS } from '../src/data/encounters.js';
import { TYPES, effectiveness, validateChart } from '../src/data/types.js';

test('type chart is well-formed and the starter triangle holds', () => {
  assert.ok(validateChart());
  assert.equal(effectiveness('Ember', ['Nature']), 2);
  assert.equal(effectiveness('Tide', ['Ember']), 2);
  assert.equal(effectiveness('Nature', ['Tide']), 2);
  assert.equal(effectiveness('Static', ['Stone']), 0);
  assert.equal(effectiveness('Frost', ['Drake', 'Stone']), 4);
});

test('every species is valid: types, learnsets, evolutions', () => {
  validateSpecies();
  assert.equal(Object.keys(SPECIES).length, 102);
  for (const s of Object.values(SPECIES)) {
    for (const t of s.types) { assert.ok(TYPES.includes(t), `${s.id} type ${t}`); }
    for (const [lv, mv] of s.learn) { assert.ok(MOVES[mv], `${s.id} learns unknown ${mv}`); assert.ok(lv >= 1); }
    if (s.evo) { assert.ok(SPECIES[s.evo.into], `${s.id} evolves into unknown ${s.evo.into}`); assert.ok(s.evo.level > 1); }
  }
});

test('names are unique and original', () => {
  const names = Object.values(SPECIES).map((s) => s.name.toLowerCase());
  assert.equal(new Set(names).size, names.length);
  // no clashes with well-known creature names from other series
  for (const bad of ['pikachu', 'eevee', 'charmander', 'squirtle', 'bulbasaur', 'sprigatito', 'ponyta', 'rapidash', 'tentacool']) {
    assert.ok(!names.includes(bad), bad);
  }
});

test('items, discs and trainer parties reference real data', () => {
  for (const it of Object.values(ITEMS)) {
    if (it.use.kind === 'teach') { assert.ok(MOVES[it.use.move], it.id); }
  }
  for (const tr of Object.values(TRAINERS)) {
    assert.ok(tr.party.length >= 1 && tr.party.length <= 6, tr.id);
    for (const [sp, lv, moves] of tr.party) {
      assert.ok(SPECIES[sp], `${tr.id}: ${sp}`);
      assert.ok(lv >= 2 && lv <= 100);
      for (const m of moves || []) { assert.ok(MOVES[m], `${tr.id}: move ${m}`); }
    }
    for (const it of tr.items) { assert.ok(ITEMS[it], `${tr.id}: item ${it}`); }
  }
  for (const [yours, theirs] of Object.entries(RIVAL_PICK)) {
    assert.equal(effectiveness(SPECIES[theirs].types[0], SPECIES[yours].types), 2, `rival counter for ${yours}`);
  }
});

test('encounter tables are sane', () => {
  for (const [map, t] of Object.entries(ENCOUNTERS)) {
    for (const [kind, table] of Object.entries(t)) {
      for (const [sp, lo, hi, w] of table) {
        assert.ok(SPECIES[sp], `${map}.${kind}: ${sp}`);
        assert.ok(lo <= hi && w > 0);
        assert.notEqual(sp, 'tiamat');
      }
    }
  }
});

test('three-stage lines and new Morphs can be found', () => {
  const stages = (id) => { let n = 1; let cur = SPECIES[id]; while (cur.evo) { cur = SPECIES[cur.evo.into]; n++; } return n; };
  const roots = Object.values(SPECIES).filter((s) => !Object.values(SPECIES).some((o) => o.evo && o.evo.into === s.id));
  const threeStage = roots.filter((r) => stages(r.id) === 3).map((r) => r.id);
  assert.ok(threeStage.length >= 14, `only ${threeStage.length} three-stage lines`);
});
