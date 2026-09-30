import test from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

test('world validator: maps, warps, scripts, trainers and reachability', () => {
  const r = spawnSync(process.execPath, [path.join(ROOT, 'tools/validate.mjs')], { encoding: 'utf8' });
  assert.equal(r.status, 0, r.stdout + r.stderr);
});

test('a won Trial powers down: gates stay open and the Warden\'s pads appear', async () => {
  const fs = await import('node:fs');
  const halls = { brindlewood_trial: 'moss', saltreach_trial: 'tide', gearhollow_trial: 'spark', hollowmere_trial: 'veil', frostspire_trial: 'rime', riftgate_trial: 'wyrm' };
  for (const [id, sigil] of Object.entries(halls)) {
    const tm = JSON.parse(fs.readFileSync(path.join(ROOT, `public/assets/maps/${id}.tmj`), 'utf8'));
    const prop = (o, k) => (o.properties || []).find((p) => p.name === k)?.value;
    const done = `sigil_${sigil}`;
    assert.equal(prop(tm, 'done'), done, `${id}: done condition`);
    const objs = tm.layers.find((l) => l.type === 'objectgroup').objects;
    for (const g of objs.filter((o) => o.type === 'gate')) { assert.ok(String(prop(g, 'open')).split('|').includes(done), `${id}: a gate that stays shut`); }
    const pads = objs.filter((o) => o.type === 'warp' && prop(o, 'quiet') && prop(o, 'cond') === done);
    assert.equal(pads.length, 2, `${id}: two Warden's pads`);
    for (const p of pads) { assert.ok(objs.some((o) => o.type === 'plate' && o.x === p.x && o.y === p.y && prop(o, 'onframe') === 'warden_pad' && !prop(o, 'frame')), `${id}: pad art`); }
  }
});
