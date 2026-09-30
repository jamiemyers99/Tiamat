import './setup.mjs';
import test from 'node:test';
import assert from 'node:assert/strict';
import { SPECIES, validateSpecies } from '../src/data/species.js';
import { MOVES } from '../src/data/moves.js';
import { ITEMS } from '../src/data/items.js';
import { TRAINERS, RIVAL_PICK, CROWN_ORDER } from '../src/data/trainers.js';
import { INDEX_TOTAL, INDEX_REWARDS, dueRewards, nextReward, rewardFlag, indexCount } from '../src/data/indexRewards.js';
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
  assert.equal(Object.keys(SPECIES).length, 106);
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
        assert.ok(!SPECIES[sp].legendary, `${map}.${kind}: legendary ${sp} in the wild`);
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

test("Dr. Marsh's Index rewards: 25, 50, 75, 100 and a complete Index", () => {
  const ids = Object.values(SPECIES).filter((s) => !s.hatchOnly).map((s) => s.id);
  assert.equal(INDEX_TOTAL, 105);
  assert.equal(INDEX_TOTAL, ids.length);
  assert.deepEqual(INDEX_REWARDS.map((r) => r.at), [25, 50, 75, 100, 'all']);
  for (const r of INDEX_REWARDS) {
    assert.ok(r.money > 0, `${r.at}: always some money`);
    assert.ok(r.items.length >= 2, `${r.at}: and some goodies`);
    for (const [id, n] of r.items) { assert.ok(ITEMS[id], `${r.at}: ${id}`); assert.ok(n >= 1); }
  }
  // the milestone rewards include Tech Discs with strong moves
  for (const r of INDEX_REWARDS.slice(0, 4)) { assert.ok(r.items.some(([id]) => ITEMS[id].disc || /^td\d+$/.test(id)), `${r.at}: a Tech Disc`); }
  assert.ok(INDEX_REWARDS.at(-1).items.some(([id]) => id === 'mystery_egg'));
  assert.equal(dueRewards(ids.slice(0, 24), {}).length, 0);
  assert.deepEqual(dueRewards(ids.slice(0, 60), {}).map((r) => r.at), [25, 50]);
  assert.deepEqual(dueRewards(ids.slice(0, 60), { [rewardFlag(INDEX_REWARDS[0])]: true }).map((r) => r.at), [50]);
  assert.equal(nextReward(ids.slice(0, 60)).at, 75);
  assert.deepEqual(dueRewards(ids, {}).map((r) => r.at), [25, 50, 75, 100, 'all']);
  assert.equal(nextReward(ids), null);
  // the hatched legendary doesn't count towards the Index
  assert.equal(indexCount([...ids.slice(0, 10), 'abzurath']), 10);
});

test('Abzurath: the Draco King, a male Iron/Drake legendary that only hatches from the egg', () => {
  const a = SPECIES.abzurath;
  assert.deepEqual(a.types, ['Iron', 'Drake']);
  assert.ok(a.legendary && a.hatchOnly);
  assert.equal(a.female, 0);
  assert.ok(SPECIES.tiamat.legendary);
  assert.ok(a.learn.some(([, m]) => m === 'primordial_anvil'));
  for (const t of Object.values(ENCOUNTERS)) { for (const table of Object.values(t)) { assert.ok(!table.some(([sp]) => sp === 'abzurath')); } }
});

test('the Crown Challenge: six Wardens getting stronger, then Wren', () => {
  assert.equal(CROWN_ORDER.length, 6);
  let prev = 0;
  for (const id of CROWN_ORDER) {
    const tr = TRAINERS[`elite_${id}`];
    assert.ok(tr, id);
    assert.equal(tr.party.length, 6);
    const top = Math.max(...tr.party.map(([, lv]) => lv));
    assert.ok(top > prev, `${id} should be stronger than the Warden before`);
    prev = top;
  }
  for (const starter of Object.keys(RIVAL_PICK)) {
    const w = TRAINERS[`elite_wren_${starter}`];
    assert.ok(w && w.party.length === 6);
    assert.ok(Math.max(...w.party.map(([, lv]) => lv)) > prev);
  }
  assert.ok(ITEMS.crown_gem && ITEMS.mystery_egg && ITEMS.radiant_charm);
});
