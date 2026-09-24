// Game state, save slots and settings.
import { natureFromId } from '../data/natures.js';
import { refreshStarterMoves } from '../battle/mon.js';
import { SPECIES } from '../data/species.js';
import { SAVE_PREFIX, SETTINGS_KEY, SAVE_VERSION, MONEY_CAP, BOX_COUNT, BOX_SIZE } from '../config.js';

export const DEFAULT_SETTINGS = {
  textSpeed: 'normal',     // slow | normal | fast | instant
  musicVol: 0.7,
  sfxVol: 0.85,
  battleAnims: true,
  battleStyle: 'shift',    // shift | set
  expShare: true,          // benched party members get a share of XP
  autoRun: false,          // run without holding the run key
  clock: 'game',           // game | real
  scaling: 'pixel',        // pixel | fill
  frame: 0,                // dialogue window colour
  keys: null,              // custom keyboard bindings ({ action: [key, key] }); null = defaults
};

export function loadSettings() {
  try {
    const raw = localStorage.getItem(SETTINGS_KEY);
    return { ...DEFAULT_SETTINGS, ...(raw ? JSON.parse(raw) : {}) };
  } catch {
    return { ...DEFAULT_SETTINGS };
  }
}

export function saveSettings(s) {
  try { localStorage.setItem(SETTINGS_KEY, JSON.stringify(s)); } catch { /* storage unavailable */ }
}

export function newState() {
  return {
    version: SAVE_VERSION,
    player: { name: 'Rowan', style: 0, gender: 'm', map: 'home_2f', x: 5, y: 4, face: 'down', surfing: false },
    rivalName: 'Wren',
    party: [],
    boxes: Array.from({ length: BOX_COUNT }, (_, i) => ({ name: `Box ${i + 1}`, slots: Array(BOX_SIZE).fill(null) })),
    bag: {},
    money: 3000,
    flags: {},
    vars: {},
    defeated: {},
    index: { seen: [], caught: [], seenSex: {}, caughtSex: {} },
    sexTally: { m: 0, f: 0 },
    starterMoves2: true,
    xpShareOn: false,
    sigils: [],
    playMs: 0,
    clock: 8 * 60,              // minutes since midnight (game clock)
    day: 1,
    lastHeal: { map: 'home_1f', x: 4, y: 7 },
    repel: 0,
    steps: 0,
    uid: 1,
    started: Date.now(),
    trainerId: Math.floor(10000 + Math.random() * 89999),
  };
}

export const G = {
  state: newState(),
  settings: loadSettings(),
  slot: 0,
};

// ── helpers ──
export const flag = (k) => !!G.state.flags[k];
export const setFlag = (k, v = true) => { if (v) { G.state.flags[k] = true; } else { delete G.state.flags[k]; } };
export const getVar = (k, d = 0) => (G.state.vars[k] ?? d);
export const setVar = (k, v) => { G.state.vars[k] = v; };

export function addMoney(n) {
  G.state.money = Math.max(0, Math.min(MONEY_CAP, G.state.money + n));
}

export function itemCount(id) { return G.state.bag[id] || 0; }
export function giveItem(id, n = 1) { G.state.bag[id] = Math.min(999, (G.state.bag[id] || 0) + n); }
export function takeItem(id, n = 1) {
  if ((G.state.bag[id] || 0) < n) { return false; }
  G.state.bag[id] -= n;
  if (G.state.bag[id] <= 0) { delete G.state.bag[id]; }
  return true;
}

// The Index tracks each species, and (like Pokémon) which male/female forms you've seen and caught.
function addForm(map, speciesId, sex) {
  if (sex !== 'm' && sex !== 'f') { return false; }
  const list = map[speciesId] || (map[speciesId] = []);
  if (list.includes(sex)) { return false; }
  list.push(sex);
  return true;
}
export function markSeen(speciesId, sex) {
  const ix = G.state.index;
  if (!ix.seen.includes(speciesId)) { ix.seen.push(speciesId); }
  addForm(ix.seenSex || (ix.seenSex = {}), speciesId, sex);
}
// Returns true when this is a new form of a species already in the Index.
export function markCaught(speciesId, sex) {
  markSeen(speciesId, sex);
  const ix = G.state.index;
  const firstSpecies = !ix.caught.includes(speciesId);
  if (firstSpecies) { ix.caught.push(speciesId); }
  const newForm = addForm(ix.caughtSex || (ix.caughtSex = {}), speciesId, sex);
  return newForm && !firstSpecies;
}
// Have you caught this species in this form (♂/♀)?
export function hasCaughtForm(speciesId, sex, index = G.state.index) {
  return !!(index && index.caughtSex && (index.caughtSex[speciesId] || []).includes(sex));
}
export function hasSeenForm(speciesId, sex, index = G.state.index) {
  return !!(index && index.seenSex && (index.seenSex[speciesId] || []).includes(sex)) || hasCaughtForm(speciesId, sex, index);
}

// Older saves only knew "caught this species". Work out which forms from the Morphs you own:
// an owned Morph counts for its species and for the earlier stages it evolved from (if you caught those).
export function rebuildForms(state) {
  const prev = {};
  for (const sp of Object.values(SPECIES)) { if (sp.evo && sp.evo.into) { prev[sp.evo.into] = sp.id; } }
  const ix = state.index;
  const caught = new Set(ix.caught || []);
  const caughtSex = {};
  const add = (id, sex) => {
    const l = caughtSex[id] || (caughtSex[id] = []);
    if (!l.includes(sex)) { l.push(sex); }
  };
  const owned = [...(state.party || []), ...(state.boxes || []).flatMap((b) => b.slots || [])].filter(Boolean);
  for (const m of owned) {
    if (m.sex !== 'm' && m.sex !== 'f') { continue; }
    add(m.species, m.sex);
    for (let id = prev[m.species], n = 0; id && n < 5; id = prev[id], n++) { if (caught.has(id)) { add(id, m.sex); } }
  }
  // single-sex species (Tiamat): catching one means you have its only form
  for (const id of caught) { const f = SPECIES[id]?.female; if (f === 1) { add(id, 'f'); } else if (f === 0) { add(id, 'm'); } }
  const seenSex = {};
  for (const [id, l] of Object.entries(caughtSex)) { seenSex[id] = [...l]; }
  return { caughtSex, seenSex };
}

export function nextUid() { G.state.uid = (G.state.uid || 1) + 1; return G.state.uid; }

// Place a Morph in the party, or the first free box slot. Returns 'party' | 'box:N' | null.
export function receiveMorph(mon) {
  if (G.state.party.length < 6) { G.state.party.push(mon); return 'party'; }
  for (let b = 0; b < G.state.boxes.length; b++) {
    const i = G.state.boxes[b].slots.indexOf(null);
    if (i >= 0) { G.state.boxes[b].slots[i] = mon; return `box:${b}`; }
  }
  return null;
}

// ── save slots ──
export function slotKey(i) { return `${SAVE_PREFIX}${i}`; }

export function saveGame(slot = G.slot) {
  try {
    const data = JSON.stringify({ ...G.state, version: SAVE_VERSION, savedAt: Date.now() });
    localStorage.setItem(slotKey(slot), data);
    G.slot = slot;
    return true;
  } catch {
    return false;
  }
}

export function readSlot(i) {
  try {
    const raw = localStorage.getItem(slotKey(i));
    if (!raw) { return null; }
    return migrate(JSON.parse(raw));
  } catch {
    return { corrupt: true };
  }
}

export function loadGame(i) {
  const s = readSlot(i);
  if (!s || s.corrupt) { return false; }
  G.state = s;
  G.slot = i;
  return true;
}

export function deleteSlot(i) {
  try { localStorage.removeItem(slotKey(i)); } catch { /* ignore */ }
}

// Upgrade older saves in place. v5 is the first save format of the rebuilt game.
export function migrate(s) {
  if (!s || typeof s !== 'object') { throw new Error('bad save'); }
  const base = newState();
  const out = { ...base, ...s };
  out.player = { ...base.player, ...(s.player || {}) };
  if (!s.player || !s.player.gender) { out.player.gender = (out.player.style || 0) % 2 ? 'f' : 'm'; }
  const ix = s.index || {};
  out.index = { seen: [...(ix.seen || [])], caught: [...(ix.caught || [])], seenSex: { ...(ix.seenSex || {}) }, caughtSex: { ...(ix.caughtSex || {}) } };
  out.flags = s.flags || {};
  out.vars = s.vars || {};
  out.bag = s.bag || {};
  out.boxes = Array.isArray(s.boxes) && s.boxes.length ? s.boxes : base.boxes;
  // Morphs from saves made before male/female forms: pick a sex that stays the same every load
  const giveSex = (m) => {
    if (!m) { return; }
    if (!m.sex) { m.sex = m.species === 'tiamat' ? 'f' : ((m.uid || 0) % 2 ? 'f' : 'm'); }
    // Morphs from before natures existed get a stable one
    if (!m.nature) { m.nature = natureFromId(m.uid, SPECIES[m.species]?.types || []); }
  };
  (out.party || []).forEach(giveSex);
  out.boxes.forEach((b) => (b.slots || []).forEach(giveSex));
  // starter lines got their own signature moves: swap them into older saves once
  if (!s.starterMoves2) {
    (out.party || []).forEach(refreshStarterMoves);
    out.boxes.forEach((b) => (b.slots || []).forEach(refreshStarterMoves));
    out.starterMoves2 = true;
  }
  // the Index learned about male/female forms: rebuild it once from the Morphs you own
  if (!ix.caughtSex) {
    const forms = rebuildForms(out);
    out.index.caughtSex = forms.caughtSex;
    out.index.seenSex = { ...forms.seenSex, ...(ix.seenSex || {}) };
  }
  for (const id of out.index.caught) { if (!out.index.seen.includes(id)) { out.index.seen.push(id); } }
  out.version = SAVE_VERSION;
  return out;
}

// Money dropped when the whole team faints — like Pokémon it scales with progress, so a new Tamer
// loses pocket change and a veteran loses a lot: (per-level rate by Sigils) × strongest Morph's level.
export const BLACKOUT_RATE = [8, 16, 24, 36, 48, 64, 80];
export function blackoutLoss(state) {
  const sigils = Math.min(BLACKOUT_RATE.length - 1, (state.sigils || []).length);
  const top = Math.max(1, ...(state.party || []).map((m) => m.level || 1));
  return Math.max(0, Math.min(state.money || 0, BLACKOUT_RATE[sigils] * top));
}

export function hasLegacySave() {
  try { return !!localStorage.getItem('tiamat_save'); } catch { return false; }
}
