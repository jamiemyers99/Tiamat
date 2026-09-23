import './setup.mjs';
import test from 'node:test';
import assert from 'node:assert/strict';
import { tierOf, WILD_IV_CAP, TAMER_IV, BOSS_IV, wildIvs, trainerIvs, trainerSkill, wildSkill, partnerIvs, settleCaught } from '../src/data/difficulty.js';
import { createMon } from '../src/battle/mon.js';
import { ENCOUNTERS } from '../src/data/encounters.js';
import { TRAINERS } from '../src/data/trainers.js';

const ORDER = ['route1', 'route2', 'thornwild', 'route3', 'coldforge_mines', 'route4', 'route5', 'route6', 'abyssal_rift'];

test('areas get tougher along the journey', () => {
  const tiers = ORDER.map(tierOf);
  for (let i = 1; i < tiers.length; i++) { assert.ok(tiers[i] >= tiers[i - 1], `${ORDER[i]} tier`); }
  assert.equal(tierOf('home_2f'), 0);
  assert.equal(tierOf('brindlewood_trial'), 0);
  assert.equal(tierOf('cradle'), 7);
  // wild levels rise with the route
  // (land encounters: water spots open up later with the Skiff)
  const land = (m) => Object.entries(ENCOUNTERS[m]).filter(([k]) => k !== 'water' || m === 'route5').flatMap(([, t]) => t);
  const top = (m) => Math.max(...land(m).map((e) => e[2]));
  for (let i = 1; i < ORDER.length; i++) { assert.ok(top(ORDER[i]) > top(ORDER[i - 1]), `${ORDER[i]} levels`); }
});

test('genes and tactics ramp up tier by tier', () => {
  for (const arr of [WILD_IV_CAP, TAMER_IV, BOSS_IV]) {
    for (let i = 1; i < arr.length; i++) { assert.ok(arr[i] >= arr[i - 1]); }
  }
  for (let t = 0; t < 8; t++) { assert.ok(BOSS_IV[t] >= TAMER_IV[t]); }
  for (let i = 0; i < 50; i++) {
    const iv = wildIvs(0);
    for (const v of Object.values(iv)) { assert.ok(v >= 0 && v <= WILD_IV_CAP[0]); }
  }
  const youngster = TRAINERS.r1_ollie, warden = TRAINERS.mossa;
  assert.equal(trainerIvs(0, youngster).atk, 0);
  assert.ok(trainerIvs(0, warden).atk > 0);
  assert.equal(trainerSkill(0, youngster), 1);
  assert.equal(trainerSkill(0, warden), 2);
  assert.equal(trainerSkill(6, TRAINERS.seren), 3);
  assert.equal(wildSkill(0), 0);
  assert.equal(wildSkill(7), 1);
});

test('partners are strong and caught Morphs settle in', () => {
  const p = partnerIvs();
  for (const v of Object.values(p)) { assert.ok(v >= 20 && v <= 31); }
  const m = createMon('nibbit', 3, { ivs: wildIvs(0) });
  const before = { ...m.ivs };
  settleCaught(m);
  for (const k of Object.keys(before)) { assert.ok(m.ivs[k] >= before[k] && m.ivs[k] <= 31); }
});
