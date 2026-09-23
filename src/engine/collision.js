// Solid-tile check — returns true if the tile at (x,y) blocks movement.
// J (ledge) is handled in movement.js, so it counts as solid here to
// prevent direct northward entry; the ledge logic bypasses this when moving south.
// Exports: isSolidTile
import { TILE_TYPES, getTile } from "../data/maps.js?v=20260429-15";

export function isSolidTile(state, x, y) {
  const tile = getTile(state.currentMap, x, y);
  if (tile === null) {
    return true;
  }

  const def = TILE_TYPES[tile];
  if (!def?.walkable) {
    return true;
  }

  // NPC positions block movement, except for trainers already defeated
  const npcKey = `${x},${y}`;
  if (Object.prototype.hasOwnProperty.call(state.npcs, npcKey)) {
    const npc = state.npcs[npcKey];
    if (npc?.trainer && state.defeatedTrainers?.[npc.battleId]) {
      return false; // defeated trainer — let the player walk past
    }
    return true;
  }

  return false;
}
