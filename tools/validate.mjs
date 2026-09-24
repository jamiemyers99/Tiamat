// World validator: checks every map, warp, connection, NPC, trainer, item and script reference,
// and flood-fills each map to find anything the player can never reach.
//   node tools/validate.mjs
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

globalThis.localStorage = { getItem: () => null, setItem: () => {}, removeItem: () => {} };
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const MAPDIR = path.join(ROOT, 'public/assets/maps');
const META = ['none', 'solid', 'water', 'grass', 'ledge_down', 'ledge_left', 'ledge_right', 'counter', 'door', 'bridge', 'noenc'];

const { SPECIES } = await import('../src/data/species.js');
const { TRAINERS } = await import('../src/data/trainers.js');
const { ITEMS } = await import('../src/data/items.js');
const { ENCOUNTERS } = await import('../src/data/encounters.js');
const { MOVES } = await import('../src/data/moves.js');
const { SCRIPTS } = await import('../src/scripts/index.js');
const { REGION } = await import('../src/data/region.js');
const chars = JSON.parse(fs.readFileSync(path.join(ROOT, 'public/assets/sprites/chars.json'), 'utf8'));
const CHAR_NAMES = new Set(Object.keys(chars.sprites || chars));

const errors = [];
const warns = [];
const err = (m) => errors.push(m);
const warn = (m) => warns.push(m);

const index = JSON.parse(fs.readFileSync(path.join(MAPDIR, 'index.json'), 'utf8'));
const maps = {};
for (const id of Object.keys(index)) {
  const tm = JSON.parse(fs.readFileSync(path.join(MAPDIR, `${id}.tmj`), 'utf8'));
  const props = Object.fromEntries((tm.properties || []).map((p) => [p.name, p.value]));
  const metaL = tm.layers.find((l) => l.name === 'meta');
  const metaTs = tm.tilesets.find((t) => t.name === 'meta');
  const meta = metaL.data.map((g) => (g >= metaTs.firstgid ? META[g - metaTs.firstgid] : 'none'));
  const objs = tm.layers.find((l) => l.type === 'objectgroup').objects.map((o) => ({
    type: o.type, x: Math.floor(o.x / 16), y: Math.floor(o.y / 16), w: Math.max(1, Math.round(o.width / 16)), h: Math.max(1, Math.round(o.height / 16)),
    props: Object.fromEntries((o.properties || []).map((p) => [p.name, p.value])),
  }));
  maps[id] = { id, w: tm.width, h: tm.height, props, meta, objs };
}

const beh = (m, x, y) => (x < 0 || y < 0 || x >= m.w || y >= m.h ? 'oob' : m.meta[y * m.w + x]);
const walkable = (b, water) => ['none', 'grass', 'bridge', 'noenc'].includes(b) || (water && b === 'water');

// ── references ─────────────────────────────────────────────────────────────
const scriptRefs = new Set();
for (const m of Object.values(maps)) {
  for (const side of ['north', 'south', 'east', 'west']) {
    if (!m.props[side]) { continue; }
    const [t, off] = String(m.props[side]).split(/\s+/);
    if (!maps[t]) { err(`${m.id}: ${side} connection to unknown map ${t}`); continue; }
    const tm = maps[t];
    const o = +off || 0;
    // every open edge cell must land on something walkable
    const n = side === 'north' || side === 'south' ? m.w : m.h;
    for (let i = 0; i < n; i++) {
      const [x, y] = side === 'north' ? [i, 0] : side === 'south' ? [i, m.h - 1] : side === 'west' ? [0, i] : [m.w - 1, i];
      const b = beh(m, x, y);
      if (!walkable(b, true)) { continue; }
      const [tx, ty] = side === 'north' ? [x + o, tm.h - 1] : side === 'south' ? [x + o, 0] : side === 'west' ? [tm.w - 1, y + o] : [0, y + o];
      const tb = beh(tm, tx, ty);
      if (!walkable(tb, b === 'water')) { err(`${m.id}: leaving ${side} at ${x},${y} (${b}) lands on ${t}:${tx},${ty} (${tb})`); }
    }
    const back = { north: 'south', south: 'north', east: 'west', west: 'east' }[side];
    if (!tm.props[back] || String(tm.props[back]).split(/\s+/)[0] !== m.id) { err(`${m.id}: ${side} → ${t} but ${t} has no ${back} connection back`); }
  }
  for (const o of m.objs) {
    const p = o.props;
    if (o.type === 'warp') {
      if (!p.to) { err(`${m.id}: warp at ${o.x},${o.y} has no destination`); continue; }
      const [t, xy] = String(p.to).split(':');
      if (!maps[t]) { err(`${m.id}: warp to unknown map ${t}`); continue; }
      const [x, y] = xy.split(',').map(Number);
      const b = beh(maps[t], x, y);
      if (!walkable(b, false)) { err(`${m.id}: warp ${o.x},${o.y} → ${p.to} lands on ${b}`); }
    }
    if (o.type === 'npc') {
      if (!CHAR_NAMES.has(p.sprite)) { err(`${m.id}: npc ${p.id} unknown sprite ${p.sprite}`); }
      if (p.script) { scriptRefs.add(p.script); }
      if (p.trainer && !TRAINERS[p.trainer]) { err(`${m.id}: npc ${p.id} unknown trainer ${p.trainer}`); }
      if (!p.script && !p.text && !p.trainer) { warn(`${m.id}: npc ${p.id} says nothing`); }
    }
    if ((o.type === 'sign' || o.type === 'trigger') && p.script) { scriptRefs.add(p.script); }
    if (o.type === 'item' && !ITEMS[p.item]) { err(`${m.id}: item ${p.item} unknown`); }
  }
  if (m.props.escape) {
    const [t, xy] = m.props.escape.split(':');
    const [x, y] = xy.split(',').map(Number);
    if (!maps[t] || !walkable(beh(maps[t], x, y), false)) { err(`${m.id}: bad escape ${m.props.escape}`); }
  }
  if (m.props.fly) {
    const [x, y] = m.props.fly.split(',').map(Number);
    if (!walkable(beh(m, x, y), false)) { err(`${m.id}: fly point ${m.props.fly} not walkable (${beh(m, x, y)})`); }
  }
}
for (const s of scriptRefs) { if (!SCRIPTS[s]) { err(`missing script ${s}`); } }
for (const k of Object.keys(SCRIPTS)) {
  if (k.startsWith('map:') && !maps[k.slice(4)]) { err(`script ${k} for unknown map`); }
}

for (const [id, tr] of Object.entries(TRAINERS)) {
  if (!CHAR_NAMES.has(tr.sprite)) { err(`trainer ${id}: unknown sprite ${tr.sprite}`); }
  for (const [sp, lv, moves] of tr.party) {
    if (!SPECIES[sp]) { err(`trainer ${id}: unknown species ${sp}`); }
    if (!(lv >= 1 && lv <= 100)) { err(`trainer ${id}: bad level ${lv}`); }
    for (const mv of moves || []) { if (!MOVES[mv]) { err(`trainer ${id}: unknown move ${mv}`); } }
  }
  for (const it of tr.items || []) { if (!ITEMS[it]) { err(`trainer ${id}: unknown item ${it}`); } }
}
const usedTrainers = new Set(Object.values(maps).flatMap((m) => m.objs.filter((o) => o.props.trainer).map((o) => o.props.trainer)));
const scriptSrc = fs.readdirSync(path.join(ROOT, 'src/scripts')).map((f) => fs.readFileSync(path.join(ROOT, 'src/scripts', f), 'utf8')).join('\n');
for (const id of Object.keys(TRAINERS)) {
  if (!usedTrainers.has(id) && !scriptSrc.includes(`'${id}'`) && !/^rival\d_/.test(id)) { warn(`trainer ${id} is never battled`); }
}
for (const [mid, t] of Object.entries(ENCOUNTERS)) {
  if (!maps[mid]) { err(`encounters for unknown map ${mid}`); }
  for (const [k, table] of Object.entries(t)) {
    for (const [sp] of table) { if (!SPECIES[sp]) { err(`encounters ${mid}.${k}: unknown species ${sp}`); } }
  }
}
for (const p of REGION.points) {
  for (const mid of p.maps) { if (!maps[mid]) { err(`region ${p.id}: unknown map ${mid}`); } }
  if (p.fly && !maps[p.fly].props.fly) { err(`region ${p.id}: map ${p.fly} has no fly point`); }
}
for (const id of Object.keys(maps)) { if (!REGION.locate(id)) { warn(`map ${id} is not on the Reach Map`); } }

// ── reachability ───────────────────────────────────────────────────────────
// Entrances: arrival tiles of warps into this map + open edge tiles with connections + spawn.
const entries = {};
for (const m of Object.values(maps)) { entries[m.id] = []; }
for (const m of Object.values(maps)) {
  for (const o of m.objs) {
    if (o.type === 'warp' && o.props.to) {
      const [t, xy] = String(o.props.to).split(':');
      const [x, y] = xy.split(',').map(Number);
      if (entries[t]) { entries[t].push([x, y]); }
    }
    if (o.type === 'spawn') { entries[m.id].push([o.x, o.y]); }
  }
  for (const side of ['north', 'south', 'east', 'west']) {
    if (!m.props[side]) { continue; }
    const n = side === 'north' || side === 'south' ? m.w : m.h;
    for (let i = 0; i < n; i++) {
      const [x, y] = side === 'north' ? [i, 0] : side === 'south' ? [i, m.h - 1] : side === 'west' ? [0, i] : [m.w - 1, i];
      if (walkable(beh(m, x, y), true)) { entries[m.id].push([x, y]); }
    }
  }
}
const DIRS = [[0, -1, 'up'], [0, 1, 'down'], [-1, 0, 'left'], [1, 0, 'right']];
for (const m of Object.values(maps)) {
  const seen = new Set();
  const q = [...entries[m.id]];
  const brambles = new Set(m.objs.filter((o) => o.type === 'bramble').map((o) => `${o.x},${o.y}`));
  const blockers = new Set(m.objs.filter((o) => o.type === 'item' && !o.props.hidden).map((o) => `${o.x},${o.y}`));
  for (const k of q) { seen.add(`${k[0]},${k[1]}`); }
  while (q.length) {
    const [x, y] = q.shift();
    for (const [dx, dy, d] of DIRS) {
      let nx = x + dx, ny = y + dy;
      const b = beh(m, nx, ny);
      if ((b === 'ledge_down' && d === 'down') || (b === 'ledge_left' && d === 'left') || (b === 'ledge_right' && d === 'right')) { nx += dx; ny += dy; }
      else if (!walkable(b, true)) { continue; }
      const key = `${nx},${ny}`;
      if (seen.has(key) || blockers.has(key) || !walkable(beh(m, nx, ny), true)) { continue; }
      seen.add(key);
      q.push([nx, ny]);
    }
  }
  if (!entries[m.id].length) { warn(`${m.id}: no entrances found`); continue; }
  const near = (x, y, w = 1, h = 1) => {
    for (let yy = y - 1; yy <= y + h; yy++) { for (let xx = x - 1; xx <= x + w; xx++) { if (seen.has(`${xx},${yy}`)) { return true; } } }
    return false;
  };
  for (const o of m.objs) {
    const what = o.type === 'npc' ? `npc ${o.props.id}` : o.type === 'item' ? `item ${o.props.item}` : o.type === 'warp' ? `warp → ${o.props.to}` : o.type === 'sign' ? `sign "${String(o.props.text || o.props.script).slice(0, 24)}"` : o.type === 'trigger' ? `trigger ${o.props.script}` : null;
    if (!what || o.props.show === 'never') { continue; }
    let ok;
    if (o.type === 'item' && o.props.in) { ok = near(o.x, o.y) && beh(m, o.x, o.y) === 'solid'; }
    else if (o.type === 'item' && o.props.hidden) { ok = seen.has(`${o.x},${o.y}`); }
    else if (o.type === 'trigger') { ok = [...Array(o.w * o.h).keys()].some((i) => seen.has(`${o.x + (i % o.w)},${o.y + Math.floor(i / o.w)}`)); }
    else if (o.type === 'warp' && (o.props.door === '1' || o.props.door === true)) { ok = near(o.x, o.y); }
    else if (o.type === 'warp') { ok = seen.has(`${o.x},${o.y}`); }
    else if (o.type === 'npc') {
      ok = near(o.x, o.y, o.w, o.h) || DIRS.some(([dx, dy]) => beh(m, o.x + dx, o.y + dy) === 'counter' && seen.has(`${o.x + 2 * dx},${o.y + 2 * dy}`));
    } else { ok = near(o.x, o.y, o.w, o.h); }
    if (!ok) { err(`${m.id}: unreachable ${what} at ${o.x},${o.y}`); }
  }
}

console.log(`${Object.keys(maps).length} maps, ${Object.keys(TRAINERS).length} trainers, ${Object.keys(SCRIPTS).length} scripts`);
for (const w of warns) { console.log('warn:', w); }
for (const e of errors) { console.log('ERROR:', e); }
console.log(errors.length ? `${errors.length} errors` : 'OK — no errors');
process.exit(errors.length ? 1 : 0);
