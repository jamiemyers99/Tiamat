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

test('the Index tracks male and female forms separately; old saves are rebuilt from owned Morphs', async () => {
  const { G, newState, markCaught, hasCaughtForm } = await import('../src/core/state.js');
  const { SPECIES_LIST } = await import('../src/data/species.js');
  const base = SPECIES_LIST.find((sp) => sp.evo && sp.evo.into);
  const evolved = base.evo.into;
  // an older save: caught the first stage, evolved it (male), also caught a lone female Nibbit-style Morph
  const into = new Set(SPECIES_LIST.map((sp) => sp.evo && sp.evo.into).filter(Boolean));
  const other = SPECIES_LIST.find((sp) => !sp.evo && !into.has(sp.id) && sp.id !== 'tiamat');  // a Morph that doesn't evolve
  const old = {
    index: { seen: [base.id, evolved, other.id, 'tiamat'], caught: [base.id, evolved, other.id, 'tiamat'] },
    party: [{ species: evolved, uid: 4, level: 20, sex: 'm' }],
    boxes: [{ name: 'Box 1', slots: [{ species: other.id, uid: 9, level: 5, sex: 'f' }, null] }],
  };
  const s = migrate(old);
  assert.ok(hasCaughtForm(evolved, 'm', s.index) && !hasCaughtForm(evolved, 'f', s.index));
  assert.ok(hasCaughtForm(base.id, 'm', s.index) && !hasCaughtForm(base.id, 'f', s.index), 'the stage it evolved from counts too');
  assert.ok(hasCaughtForm(other.id, 'f', s.index) && !hasCaughtForm(other.id, 'm', s.index));
  assert.ok(hasCaughtForm('tiamat', 'f', s.index));
  assert.deepEqual(s.index.caught, old.index.caught, 'species counts are unchanged');
  assert.deepEqual(migrate(s).index.caughtSex, s.index.caughtSex, 'loading again changes nothing');
  // catching the other form later
  G.state = s;
  assert.equal(markCaught(other.id, 'f'), false);
  assert.equal(markCaught(other.id, 'm'), true, 'a new form of a known species');
  assert.ok(hasCaughtForm(other.id, 'm'));
});

test('the two starters you did not choose can be rescued', async () => {
  const { RESCUES, openRescues, worldMorphSex } = await import('../src/data/rescue.js');
  const { SCRIPTS } = await import('../src/scripts/index.js');
  const { TRAINERS } = await import('../src/data/trainers.js');
  assert.deepEqual(Object.keys(RESCUES).sort(), ['cindlet', 'puddlet', 'spriglet']);
  const s = { vars: { starter: 'cindlet' }, flags: {}, trainerId: 12345 };
  assert.deepEqual(openRescues(s).sort(), ['puddlet', 'spriglet']);
  s.flags.rescued_puddlet = true;
  assert.deepEqual(openRescues(s), ['spriglet']);
  for (const id of ['rescue.spriglet', 'rescue.puddlet', 'rescue.cindlet', 'gearhollow.smith', 'rescue.hint']) { assert.ok(SCRIPTS[id], id); }
  assert.ok(TRAINERS.r3_poacher_a && TRAINERS.r3_poacher_b);
  assert.equal(worldMorphSex('spriglet', s), worldMorphSex('spriglet', s), 'same form every load');
  const forms = new Set();
  for (let id = 10000; id < 10040; id++) { forms.add(worldMorphSex('puddlet', { trainerId: id })); }
  assert.equal(forms.size, 2, 'both forms turn up across saves');
});

test('the mythical Twinklit line: Mind/Fae, its own moves, every Tech Disc', async () => {
  const { SPECIES, SPECIES_LIST } = await import('../src/data/species.js');
  const { MOVES } = await import('../src/data/moves.js');
  const { ITEMS, canLearnDisc } = await import('../src/data/items.js');
  const { effectiveness } = await import('../src/data/types.js');
  const line = ['twinklit', 'lumelynx', 'seraphelis'];
  for (const id of line) { assert.deepEqual(SPECIES[id].types, ['Mind', 'Fae']); assert.ok(SPECIES[id].mythical); }
  assert.equal(SPECIES.twinklit.evo.into, 'lumelynx');
  assert.equal(SPECIES.lumelynx.evo.into, 'seraphelis');
  const mine = new Set(line.flatMap((id) => SPECIES[id].learn.map(([, mv]) => mv)));
  for (const sp of SPECIES_LIST) {
    if (line.includes(sp.id)) { continue; }
    for (const [, mv] of sp.learn) { assert.ok(!mine.has(mv), `${sp.id} shares ${mv}`); }
  }
  assert.ok([...mine].some((mv) => MOVES[mv].type === 'Mind' && MOVES[mv].power >= 120), 'strong Mind moves');
  for (const [id, it] of Object.entries(ITEMS)) { if (it.use && it.use.kind === 'teach') { assert.ok(canLearnDisc(SPECIES.twinklit, it.use.move), id); } }
  assert.equal(createMon('twinklit', 5).moves.length, 3);
  assert.equal(effectiveness('Fae', ['Drake']), 2);
  assert.equal(effectiveness('Drake', ['Mind', 'Fae']), 0);
  assert.equal(effectiveness('Iron', ['Fae']), 2);
});

test('old saves: Aldous\'s Nyxen becomes Twinklit, storage is healed, moves are remembered', () => {
  const nyx = { species: 'nyxen', uid: 40, level: 12, sex: 'f', nature: 'Pensive', ot: 'Jamie', metMap: null, hp: 3, xp: 1700, ivs: { hp: 25, atk: 22, def: 30, spa: 28, spd: 21, spe: 27 }, moves: [{ id: 'shade_fang', pp: 3, max: 25 }] };
  const wild = { species: 'nyxen', uid: 41, level: 9, sex: 'm', ot: 'Jamie', metMap: 'thornwild', hp: 0, ivs: { hp: 5, atk: 5, def: 5, spa: 5, spd: 5, spe: 5 }, moves: [{ id: 'shade_fang', pp: 25, max: 25 }] };
  const s = migrate({ rev: 2, starterMoves2: true, flags: { got_nyxen: true }, index: { seen: ['nyxen'], caught: ['nyxen'], caughtSex: { nyxen: ['f', 'm'] } },
    party: [{ species: 'cindlet', uid: 2, level: 14, sex: 'm', moves: [{ id: 'ember_fang', pp: 5, max: 25 }] }],
    boxes: [{ name: 'Box 1', slots: [nyx, wild] }] });
  const [a, b] = s.boxes[0].slots;
  assert.equal(a.species, 'twinklit');
  assert.equal(a.level, 12); assert.equal(a.sex, 'f'); assert.equal(a.ivs.def, 30);
  assert.ok(a.moves.every((m) => ['dream_tap', 'glimmer_kiss', 'starlight_purr', 'mind_ripple'].includes(m.id)));
  assert.equal(b.species, 'nyxen', 'a Nyxen you caught stays a Nyxen');
  assert.ok(b.hp > 0, 'storage heals');
  assert.ok(s.index.caught.includes('twinklit') && s.index.caught.includes('nyxen'));
  assert.deepEqual(s.party[0].learned, ['ember_fang']);
  assert.equal(s.flags.got_twinklit, true);
  const again = migrate(s);
  assert.equal(again.boxes[0].slots[1].species, 'nyxen', 'runs only once');
});

test('every move has an animation and sounds; signature moves have their own', async () => {
  const { readFileSync } = await import('node:fs');
  const { MOVES } = await import('../src/data/moves.js');
  const { SPECIES_LIST } = await import('../src/data/species.js');
  const { ITEMS } = await import('../src/data/items.js');
  const { recipeFor, soundsOf, SIGNATURE, KINDS, MOVE_KIND, OPS } = await import('../src/data/moveAnims.js');
  const sfx = new Set(JSON.parse(readFileSync(new URL('../public/assets/audio/index.json', import.meta.url))).sfx);
  for (const mv of Object.values(MOVES)) {
    const r = recipeFor(mv);
    assert.ok(r.length >= 2, `${mv.id} has an animation`);
    for (const st of r) { assert.ok(OPS.includes(st.op), `${mv.id}: unknown effect ${st.op}`); }
    const snd = soundsOf(r);
    assert.ok(snd.length, `${mv.id} has a sound`);
    for (const k of snd) { assert.ok(sfx.has(k), `${mv.id}: missing sound ${k}`); }
  }
  // moves only one Morph line learns (and no Tech Disc teaches) all have their own recipe and sound
  const prev = {}; for (const sp of SPECIES_LIST) { if (sp.evo) { prev[sp.evo.into] = sp.id; } }
  const root = (id) => { while (prev[id]) { id = prev[id]; } return id; };
  const lines = {}; for (const sp of SPECIES_LIST) { for (const [, mv] of sp.learn) { (lines[mv] = lines[mv] || new Set()).add(root(sp.id)); } }
  const discs = new Set(Object.values(ITEMS).filter((i) => i.use && i.use.kind === 'teach').map((i) => i.use.move));
  const exclusive = Object.keys(MOVES).filter((m) => lines[m] && lines[m].size === 1 && !discs.has(m));
  const common = new Set(Object.keys(KINDS).map((k) => JSON.stringify(KINDS[k]('Plain'))));
  const seen = new Set();
  for (const id of exclusive) {
    assert.ok(SIGNATURE[id], `${id} needs its own animation`);
    assert.ok(!MOVE_KIND[id], `${id} shouldn't also use a shared kind`);
    const r = SIGNATURE[id];
    assert.ok(soundsOf(r).includes(`sig_${id}`), `${id} needs its own sound`);
    const key = JSON.stringify(r.filter((s) => s.op !== 'sfx'));
    assert.ok(!seen.has(key), `${id} animation is a copy of another signature move`);
    seen.add(key);
    assert.ok(!common.has(JSON.stringify(r)), `${id} animation is a shared one`);
  }
  // no signature sound is used by any other move
  for (const mv of Object.values(MOVES)) {
    for (const k of soundsOf(recipeFor(mv))) { if (k.startsWith('sig_')) { assert.equal(k, `sig_${mv.id}`, `${mv.id} borrows ${k}`); } }
  }
});
