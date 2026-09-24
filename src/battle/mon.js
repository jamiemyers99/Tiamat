// Morph instances: creation, stats, experience, moves, evolution.
import { SPECIES } from '../data/species.js';
import { MOVES } from '../data/moves.js';
import { MAX_LEVEL } from '../config.js';
import { natureMult, rollNature } from '../data/natures.js';

export const STAT_KEYS = ['hp', 'atk', 'def', 'spa', 'spd', 'spe'];
export const STAT_NAMES = { hp: 'HP', atk: 'Attack', def: 'Defense', spa: 'Sp. Atk', spd: 'Sp. Def', spe: 'Speed', acc: 'accuracy', eva: 'evasion' };

let uidCounter = Date.now() % 100000;

// 1 wild Morph in 100 is Radiant (shiny). They're caught like any other Morph.
export const SHINY_ODDS = 1 / 100;

export function rollSex(speciesId, rnd = Math.random) {
  const f = SPECIES[speciesId]?.female ?? 0.5;
  return f >= 1 ? 'f' : (f <= 0 ? 'm' : (rnd() < f ? 'f' : 'm'));
}

// Atlas frame for a Morph: view 'f' (front), 'b' (back) or 'i' (icon).
export function monFrame(mon, view = 'f') {
  return `${mon.species}_${view}${mon.shiny ? 's' : ''}${mon.sex === 'f' ? '_fem' : ''}`;
}

// Wild Morphs: keep the running count of males and females close to even, so a run of one sex
// can't happen for long (the plain coin flip could give long streaks early on).
export function balancedSex(speciesId, tally, rnd = Math.random) {
  const f = SPECIES[speciesId]?.female ?? 0.5;
  if (f >= 1 || f <= 0 || !tally) { return rollSex(speciesId, rnd); }
  const diff = (tally.m || 0) - (tally.f || 0);
  const p = Math.min(0.85, Math.max(0.15, f + diff * 0.12));
  const s = rnd() < p ? 'f' : 'm';
  tally[s] = (tally[s] || 0) + 1;
  return s;
}

export function sexSymbol(mon) { return mon.sex === 'f' ? '♀' : (mon.sex === 'm' ? '♂' : ''); }

export function xpForLevel(growth, L) {
  if (L <= 1) { return 0; }
  const c = L * L * L;
  if (growth === 'fast') { return Math.floor(c * 0.8); }
  if (growth === 'slow') { return Math.floor(c * 1.25); }
  return c;
}

export function calcStats(mon) {
  const sp = SPECIES[mon.species];
  const L = mon.level;
  const out = {};
  STAT_KEYS.forEach((k, i) => {
    const b = sp.base[i];
    const iv = mon.ivs[k] ?? 15;
    const v = Math.floor(((2 * b + iv) * L) / 100);
    out[k] = k === 'hp' ? v + L + 10 : Math.floor((v + 5) * natureMult(mon.nature, k));
  });
  return out;
}

export function maxHp(mon) { return calcStats(mon).hp; }

export function monName(mon) { return mon.nick || SPECIES[mon.species].name; }

export function movesForLevel(speciesId, level) {
  const sp = SPECIES[speciesId];
  const learned = [];
  for (const [lv, id] of sp.learn) {
    if (lv <= level && !learned.includes(id)) { learned.push(id); }
  }
  return learned.slice(-4);
}

export function makeMove(id) {
  const m = MOVES[id];
  return { id, pp: m.pp, max: m.pp };
}

export function createMon(speciesId, level, opts = {}) {
  const sp = SPECIES[speciesId];
  if (!sp) { throw new Error(`Unknown species ${speciesId}`); }
  const rnd = opts.rng || Math.random;
  const ivs = {};
  for (const k of STAT_KEYS) { ivs[k] = opts.ivs?.[k] ?? Math.floor(rnd() * 32); }
  const mon = {
    uid: ++uidCounter,
    species: speciesId,
    nick: opts.nick || null,
    level,
    xp: xpForLevel(sp.growth, level),
    ivs,
    hp: 0,
    moves: (opts.moves || movesForLevel(speciesId, level)).map(makeMove),
    status: null,
    statusTurns: 0,
    ot: opts.ot || null,
    metLevel: level,
    metMap: opts.metMap || null,
    shiny: opts.shiny ?? (rnd() < SHINY_ODDS),
    sex: opts.sex || rollSex(speciesId, rnd),
    nature: opts.nature || rollNature(sp.types, rnd),
    friendship: 70,
  };
  mon.hp = maxHp(mon);
  return mon;
}

// The three starter lines now learn their own signature moves. Morphs from older saves swap the
// moves they learned from the old shared learnsets for the new ones (moves taught by Tech Discs stay).
export const STARTER_LINES = ['spriglet', 'spriggrove', 'mosswarden', 'cindlet', 'cindreaver', 'pyromane', 'puddlet', 'torrentide', 'maelstrand'];
const OLD_STARTER_MOVES = new Set(['bump', 'gruff_bark', 'stern_look', 'nip', 'leaf_nick', 'root_snare', 'stone_toss', 'vine_lash', 'drowse_pollen',
  'sap_drain', 'seed_volley', 'moss_shield', 'bloom_blast', 'heal_bud', 'quake_stomp', 'timber_crash', 'stoneskin', 'ember_spark', 'smoke_veil',
  'cinder_claw', 'flare_bite', 'blaze_ring', 'kindle', 'inferno_lash', 'pyre_rush', 'shade_fang', 'nightrend', 'shadow_creep', 'dread_gaze',
  'splash_drop', 'chill_nip', 'rip_current', 'tidal_guard', 'brine_fang', 'tide_pulse', 'undertow', 'hydro_burst', 'icicle_jab', 'rime_ray',
  'frost_armor', 'whiteout_gale']);

export function refreshStarterMoves(mon) {
  if (!mon || !STARTER_LINES.includes(mon.species)) { return false; }
  const fresh = movesForLevel(mon.species, mon.level);
  const keep = mon.moves.filter((m) => !OLD_STARTER_MOVES.has(m.id) && !fresh.includes(m.id));
  const room = 4 - Math.min(4, keep.length);
  const ids = [...(room ? fresh.slice(-room) : []), ...keep.map((m) => m.id)].slice(0, 4);
  const before = mon.moves.map((m) => m.id).join();
  mon.moves = ids.map((id) => mon.moves.find((m) => m.id === id) || makeMove(id));
  return before !== ids.join();
}

export function healMon(mon) {
  mon.hp = maxHp(mon);
  mon.status = null;
  mon.statusTurns = 0;
  mon.moves.forEach((m) => { m.pp = m.max; });
}

// Adds XP; returns a list of level-up steps [{level, before, after, learn:[moveIds]}]
export function addXp(mon, amount) {
  const sp = SPECIES[mon.species];
  const steps = [];
  if (mon.level >= MAX_LEVEL) { return steps; }
  mon.xp += amount;
  while (mon.level < MAX_LEVEL && mon.xp >= xpForLevel(sp.growth, mon.level + 1)) {
    const before = calcStats(mon);
    mon.level += 1;
    const after = calcStats(mon);
    mon.hp = Math.min(after.hp, mon.hp + (after.hp - before.hp));
    mon.friendship = Math.min(255, mon.friendship + 2);
    const learn = SPECIES[mon.species].learn.filter(([lv]) => lv === mon.level).map(([, id]) => id)
      .filter((id) => !mon.moves.some((m) => m.id === id));
    steps.push({ level: mon.level, before, after, learn });
  }
  if (mon.level >= MAX_LEVEL) { mon.xp = xpForLevel(sp.growth, MAX_LEVEL); }
  return steps;
}

export function xpProgress(mon) {
  const sp = SPECIES[mon.species];
  const a = xpForLevel(sp.growth, mon.level);
  const b = xpForLevel(sp.growth, mon.level + 1);
  return mon.level >= MAX_LEVEL ? 1 : Math.max(0, Math.min(1, (mon.xp - a) / Math.max(1, b - a)));
}

export function xpToNext(mon) {
  const sp = SPECIES[mon.species];
  return mon.level >= MAX_LEVEL ? 0 : xpForLevel(sp.growth, mon.level + 1) - mon.xp;
}

// Try to learn a move automatically. Returns true if learned, false if 4 moves already.
export function learnMove(mon, moveId) {
  if (mon.moves.some((m) => m.id === moveId)) { return true; }
  if (mon.moves.length < 4) { mon.moves.push(makeMove(moveId)); return true; }
  return false;
}

export function replaceMove(mon, index, moveId) {
  mon.moves[index] = makeMove(moveId);
}

export function evolutionTarget(mon) {
  const sp = SPECIES[mon.species];
  if (!sp.evo || mon.noEvolve) { return null; }
  if (sp.evo.level && mon.level >= sp.evo.level) { return sp.evo.into; }
  return null;
}

// Evolve in place; returns list of new moves that could not be auto-learned.
export function evolve(mon, into) {
  const before = maxHp(mon);
  const wasNick = mon.nick;
  mon.species = into;
  const after = maxHp(mon);
  mon.hp = Math.min(after, mon.hp + (after - before));
  mon.nick = wasNick;
  const pending = [];
  for (const [lv, id] of SPECIES[into].learn) {
    if ((lv === mon.level || lv === 1) && !mon.moves.some((m) => m.id === id)) {
      if (lv === 1) { continue; }
      if (!learnMove(mon, id)) { pending.push(id); }
    }
  }
  return pending;
}

export function isFainted(mon) { return mon.hp <= 0; }
