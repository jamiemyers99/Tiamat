import './setup.mjs';
import test from 'node:test';
import assert from 'node:assert/strict';
import { G, newState, saveGame, loadGame, readSlot, migrate, giveItem, takeItem, itemCount, receiveMorph } from '../src/core/state.js';
import { createMon } from '../src/battle/mon.js';
import { rollEncounter } from '../src/data/encounters.js';
import { timeOfDay } from '../src/core/time.js';

test('save → load round trip', () => {
  G.state = newState();
  G.state.player.name = 'Myro';
  G.state.party.push(createMon('cindlet', 7));
  giveItem('capsule', 3);
  assert.ok(saveGame(1));
  G.state = newState();
  assert.ok(loadGame(1));
  assert.equal(G.state.player.name, 'Myro');
  assert.equal(G.state.party[0].species, 'cindlet');
  assert.equal(itemCount('capsule'), 3);
});

test('old or partial saves are migrated safely', () => {
  const s = migrate({ player: { name: 'Old' }, party: [] });
  assert.equal(s.player.name, 'Old');
  assert.ok(Array.isArray(s.boxes) && s.boxes.length > 0);
  assert.deepEqual(s.index, { seen: [], caught: [] });
  assert.equal(readSlot(7), null);
});

test('bag and storage overflow', () => {
  G.state = newState();
  giveItem('tonic', 2);
  assert.ok(takeItem('tonic'));
  assert.ok(takeItem('tonic'));
  assert.ok(!takeItem('tonic'));
  for (let i = 0; i < 6; i++) { assert.equal(receiveMorph(createMon('nibbit', 3)), 'party'); }
  assert.equal(receiveMorph(createMon('nibbit', 3)), 'box:0');
});

test('encounters respect the time of day', () => {
  let rng = 0;
  const r = () => { rng = (rng + 0.137) % 1; return rng; };
  for (let i = 0; i < 50; i++) {
    const day = rollEncounter('route1', 'grass', 12 * 60, r);
    assert.ok(['nibbit', 'beakling', 'trotter', 'burrlet', 'chittik', 'pawpunch', 'hivling'].includes(day.species));
    const night = rollEncounter('route1', 'grass', 23 * 60, r);
    assert.ok(['nibbit', 'hushling', 'pookit', 'burrlet', 'beakling', 'wispurr'].includes(night.species));
  }
  assert.equal(timeOfDay(6 * 60), 'dawn');
  assert.equal(timeOfDay(19 * 60), 'dusk');
  assert.equal(rollEncounter('rootmere', 'grass', 600), null);
});

test('blacking out costs little at the start and more later', async () => {
  const { blackoutLoss } = await import('../src/core/state.js');
  const early = blackoutLoss({ money: 3000, sigils: [], party: [{ level: 12 }, { level: 9 }] });
  assert.ok(early <= 100, `early loss ${early}`);
  const late = blackoutLoss({ money: 30000, sigils: ['a', 'b', 'c', 'd', 'e', 'f'], party: [{ level: 50 }] });
  assert.equal(late, 4000);
  assert.equal(blackoutLoss({ money: 50, sigils: ['a'], party: [{ level: 30 }] }), 50);
});

test('the money shown as lost always matches what you had', async () => {
  const { blackoutLoss } = await import('../src/core/state.js');
  assert.equal(blackoutLoss({ money: 50, sigils: ['a', 'b'], party: [{ level: 20 }] }), 50);
  assert.equal(blackoutLoss({ money: 0, sigils: [], party: [{ level: 5 }] }), 0);
});
