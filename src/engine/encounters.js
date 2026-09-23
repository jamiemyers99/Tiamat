// Wild encounter system — 10% per grass step, weighted species table from map config.
// Exports: createEncounterManager, maybeStartEncounter
import { createCreature } from "../data/creatures.js?v=20260429-15";
import { MAPS } from "../data/maps.js?v=20260429-15";

const ENCOUNTER_CHANCE = 0.10;

export function createEncounterManager() {
  return {};
}

function pickWeighted(table) {
  const total = table.reduce((s, e) => s + e.weight, 0);
  let roll = Math.random() * total;
  for (const entry of table) {
    roll -= entry.weight;
    if (roll <= 0) { return entry; }
  }
  return table[table.length - 1];
}

export function maybeStartEncounter(state) {
  const mapCfg = MAPS[state.currentMap];
  if (!mapCfg?.encounters || !mapCfg.encounterTable?.length) { return null; }

  if (Math.random() >= ENCOUNTER_CHANCE) { return null; }

  const entry = pickWeighted(mapCfg.encounterTable);
  const level = entry.levelMin + Math.floor(Math.random() * (entry.levelMax - entry.levelMin + 1));

  return createCreature(entry.species, level);
}
