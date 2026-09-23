// saveMigration.js — chain v1→v2→v3 save upgrades.
// Each step is a pure function; chain is auditable top-to-bottom.

export const CURRENT_SAVE_VERSION = 4;

export function migrateSave(raw) {
  if (!raw || typeof raw !== "object") { throw new Error("save_invalid"); }
  let state = raw;
  const version = state.version ?? 1;
  if (version < 2) { state = _v1toV2(state); }
  if (version < 3) { state = _v2toV3(state); }
  if (version < 4) { state = _v3toV4(state); }
  state.version = CURRENT_SAVE_VERSION;
  return state;
}

function _migrateCreature(c) {
  if (!c) { return c; }
  return {
    ...c,
    speciesId:   c.speciesId   ?? c.id,
    types:       c.types       ?? [c.type].filter(Boolean),
    ivs:         c.ivs         ?? { hp: 0, atk: 0, def: 0, spd: 0 },
    friendship:  c.friendship  ?? 70,
    heldItem:    c.heldItem    ?? null,
    statusTurns: c.statusTurns ?? 0,
  };
}

function _migrateStorage(st) {
  if (!st) { return { boxes: [] }; }
  return {
    boxes: (st.boxes ?? []).map((box) => ({
      ...box,
      slots: (box.slots ?? []).map((slot) => slot ? _migrateCreature(slot) : null),
    })),
  };
}

function _v1toV2(raw) {
  return _v2toV3({
    version:          2,
    currentMap:       raw.currentMap        ?? "rootmere",
    player:           raw.player            ?? {},
    party:            raw.party             ?? [],
    money:            raw.money             ?? 0,
    items:            raw.items             ?? {},
    flags:            {},
    starterChosen:    raw.starterChosen     ?? false,
    defeatedTrainers: raw.defeatedTrainers  ?? {},
    dex:              { seen: [], caught: [] },
  });
}

function _v2toV3(raw) {
  return {
    version:          3,
    currentMap:       raw.currentMap        ?? "rootmere",
    player:           raw.player            ?? {},
    party:            (raw.party ?? []).map(_migrateCreature),
    money:            raw.money             ?? 0,
    items:            raw.items             ?? {},
    flags:            raw.flags             ?? {},
    stats:            raw.stats             ?? { steps: 0, battlesWon: 0, captures: 0 },
    settings:         raw.settings          ?? {},
    storage:          _migrateStorage(raw.storage),
    starterChosen:    raw.starterChosen     ?? false,
    defeatedTrainers: raw.defeatedTrainers  ?? {},
    dex:              raw.dex               ?? { seen: [], caught: [] },
  };
}

function _v3toV4(raw) {
  return {
    ...raw,
    version:  4,
    settings: {
      audioMaster: 0.8,
      audioBgm:    0.7,
      audioSfx:    0.9,
      audioMuted:  false,
      ...(raw.settings ?? {}),
    },
  };
}
