// Evolution system — check, scene queue, and application.
// Exports: checkEvolution, buildEvolutionQueue, applyEvolution
import { SPECIES, createCreature, getLearnsetMoves } from "../data/creatures.js?v=20260429-15";
import { computeStats } from "./xp.js?v=20260429-15";
import { MOVES } from "../data/moves.js?v=20260429-15";

// Returns the target species ID if the given creature is ready to evolve, else null.
export function checkEvolution(creature) {
  const species = SPECIES[creature.speciesId ?? creature.id];
  if (!species?.evolvesTo)            { return null; }
  if (creature.level < species.evolvesAtLevel) { return null; }
  if (creature.flags?.evolutionCancelled)       { return null; }
  return species.evolvesTo;
}

// After a battle, iterate party and collect any pending evolutions into a queue.
// Returns an array of { partyIndex, targetSpeciesId }.
export function buildEvolutionQueue(party) {
  const queue = [];
  party.forEach((creature, i) => {
    const target = checkEvolution(creature);
    if (target) { queue.push({ partyIndex: i, targetSpeciesId: target }); }
  });
  return queue;
}

// Apply an evolution to a party member in-place.
// Returns log messages.
export function applyEvolution(creature, targetSpeciesId) {
  const prevName  = creature.name;
  const newSpecies = SPECIES[targetSpeciesId];
  if (!newSpecies) { return []; }

  creature.speciesId = targetSpeciesId;
  creature.id        = targetSpeciesId;
  creature.name      = newSpecies.name;
  creature.types     = [...newSpecies.types];
  creature.type      = newSpecies.types[0];
  creature.catchRate = newSpecies.catchRate;

  // Recompute stats with new base stats, keeping IVs and level.
  const newStats = computeStats(newSpecies.baseStats, creature.level, creature.ivs ?? { hp: 8, atk: 8, def: 8, spd: 8 });
  const hpGain   = newStats.maxHp - creature.maxHp;
  creature.maxHp   = newStats.maxHp;
  creature.attack  = newStats.attack;
  creature.defense = newStats.defense;
  creature.speed   = newStats.speed;
  creature.hp      = Math.min(creature.hp + hpGain, creature.maxHp);

  // Learn any moves the new species has at the current level.
  const newMoves = getLearnsetMoves(targetSpeciesId, creature.level);
  newMoves.forEach((move) => {
    if (!creature.moves.some((m) => m.id === move.id)) {
      if (creature.moves.length < 4) {
        creature.moves.push(move);
      }
      // If full, auto-replace slot 3 — the MoveLearnPrompt handles the proper UI.
    }
  });

  // Reset evolution flag so the new form can evolve again later.
  if (creature.flags) { creature.flags.evolutionCancelled = false; }

  return [`${prevName} evolved into ${newSpecies.name}!`];
}
