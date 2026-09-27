// Game state, save slots and settings.
import { natureFromId } from '../data/natures.js';
import { refreshStarterMoves, healMon, movesForLevel, makeMove, preEvolutions } from '../battle/mon.js';
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
    mythicSwap: true,
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
    if (i >= 0) { healMon(mon); G.state.boxes[b].slots[i] = mon; return `box:${b}`; }   // storage heals, like the PC
  }
  return null;
}

// ── save slots ──
export function slotKey(i) { return `${SAVE_PREFIX}${i}`; }

export function saveGame(slot = G.slot) {
  try {
    const data = JSON.stringify({ ...G.state, version: SAVE_VERSION, rev: SAVE_REV, savedAt: Date.now() });
    localStorage.setItem(slotKey(slot), data);
    G.slot = slot;
    return true;
  } catch {
    return false;
  }
}

// Loading never throws a save away: before an older save is upgraded, its original text is kept as
// "<slot>.bak", and if the main copy can't be read the backup is loaded instead.
export function readSlot(i) {
  let raw = null;
  try { raw = localStorage.getItem(slotKey(i)); } catch { return null; }
  if (!raw) { return null; }
  try {
    const parsed = JSON.parse(raw);
    if ((parsed.rev || 0) < SAVE_REV) { try { localStorage.setItem(`${slotKey(i)}.bak`, raw); } catch { /* storage full */ } }
    return migrate(parsed);
  } catch {
    try {
      const bak = localStorage.getItem(`${slotKey(i)}.bak`);
      if (bak) { return migrate(JSON.parse(bak)); }
    } catch { /* fall through */ }
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
  try { localStorage.removeItem(slotKey(i)); localStorage.removeItem(`${slotKey(i)}.bak`); } catch { /* ignore */ }
}

// Upgrade older saves in place. v5 is the first save format of the rebuilt game; SAVE_REV goes up
// every time an upgrade step is added. Each step runs on its own: if one ever fails, the rest still
// run and the save still loads (it is never deleted).
export const SAVE_REV = 4;

function upgrade(name, fn) {
  try { fn(); } catch (e) { console.warn(`[save] upgrade step "${name}" was skipped:`, e); }
}

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
  out.defeated = s.defeated || {};
  out.party = (Array.isArray(s.party) ? s.party : []).filter((m) => m && SPECIES[m.species]);
  out.boxes = Array.isArray(s.boxes) && s.boxes.length ? s.boxes : base.boxes;
  out.boxes.forEach((b) => { b.slots = Array.from({ length: BOX_SIZE }, (_, k) => { const m = (b.slots || [])[k]; return m && SPECIES[m.species] ? m : null; }); });
  const all = () => [...out.party, ...out.boxes.flatMap((b) => b.slots)].filter(Boolean);
  // Morphs from saves made before male/female forms and natures: a sex and nature that stay the same every load
  upgrade('sex+nature', () => all().forEach((m) => {
    if (!m.sex) { m.sex = m.species === 'tiamat' ? 'f' : ((m.uid || 0) % 2 ? 'f' : 'm'); }
    if (!m.nature) { m.nature = natureFromId(m.uid, SPECIES[m.species]?.types || []); }
  }));
  // starter lines got their own signature moves: swap them into older saves once
  if (!s.starterMoves2) {
    upgrade('starter moves', () => all().forEach(refreshStarterMoves));
    out.starterMoves2 = true;
  }
  // the Index learned about male/female forms: rebuild it once from the Morphs you own
  if (!ix.caughtSex) {
    upgrade('index forms', () => {
      const forms = rebuildForms(out);
      out.index.caughtSex = forms.caughtSex;
      out.index.seenSex = { ...forms.seenSex, ...(ix.seenSex || {}) };
    });
  }
  for (const id of out.index.caught) { if (!out.index.seen.includes(id)) { out.index.seen.push(id); } }
  // rev 3: Morphs in storage are always fully healed
  if ((s.rev || 0) < 3) { upgrade('heal storage', () => out.boxes.forEach((b) => b.slots.forEach((m) => { if (m) { healMon(m); } }))); }
  // rev 4: every Morph remembers the moves it knows (for the Move Reminder)
  upgrade('learned moves', () => all().forEach((m) => { if (!Array.isArray(m.learned)) { m.learned = (m.moves || []).map((x) => x.id); } }));
  // rev 4: Aldous's gift is now the mythical Twinklit line — the Nyxen he gave in older saves becomes one
  if (out.flags.got_nyxen && !s.mythicSwap) {
    upgrade('aldous gift', () => swapAldousGift(out, all));
  }
  out.mythicSwap = true;
  out.version = SAVE_VERSION;
  out.rev = SAVE_REV;
  return out;
}

// Older saves got a Nyxen from Aldous; turn that Morph into the Twinklit line (same level, sex, nature,
// genes, nickname and XP; stage picked by level; moves re-learned for its new species). The gift is the
// Nyxen-line Morph with no capture spot recorded (gifts never have one), looking in storage first.
const NYX_LINE = ['nyxen', 'vesperel', 'noctheart'];
function swapAldousGift(out, all) {
  const boxed = out.boxes.flatMap((b) => b.slots).filter(Boolean);
  if ([...boxed, ...out.party].some((m) => SPECIES[m.species]?.mythical)) { return; }   // already has it
  const mine = [...boxed, ...out.party].filter((m) => NYX_LINE.includes(m.species));
  const strong = (m) => Object.values(m.ivs || {}).every((v) => v >= 20);
  const gift = mine.find((m) => !m.metMap) || mine.find(strong);
  if (!gift) { return; }
  const species = gift.level >= 38 ? 'seraphelis' : gift.level >= 18 ? 'lumelynx' : 'twinklit';
  gift.species = species;
  gift.moves = movesForLevel(species, gift.level).map(makeMove);
  gift.learned = gift.moves.map((x) => x.id);
  gift.metMap = 'brindlewood';
  gift.status = null;
  healMon(gift);
  const ix = out.index;
  for (const id of [species, ...preEvolutions(species)]) {
    if (!ix.caught.includes(id)) { ix.caught.push(id); }
    if (!ix.seen.includes(id)) { ix.seen.push(id); }
    ix.caughtSex[id] = [...new Set([...(ix.caughtSex[id] || []), gift.sex])];
    ix.seenSex[id] = [...new Set([...(ix.seenSex[id] || []), gift.sex])];
  }
  // the Nyxen line stays "caught" only if you still own one of that line (there is no releasing Morphs)
  const owned = all();
  for (const id of NYX_LINE) {
    const later = NYX_LINE.slice(NYX_LINE.indexOf(id));
    const stillHave = owned.some((m) => later.includes(m.species));
    if (!stillHave) {
      ix.caught = ix.caught.filter((x) => x !== id);
      delete ix.caughtSex[id];
    }
  }
  out.flags.got_twinklit = true;
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
