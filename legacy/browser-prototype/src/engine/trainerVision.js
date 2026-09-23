// Trainer line-of-sight cone detection.
// Exports: checkTrainerVision
// Returns the first undefeated trainer NPC whose vision cone contains the player,
// or null if none. Vision is blocked by solid tiles (walls, water, other NPCs).

import { getTile, TILE_TYPES } from "../data/maps.js?v=20260429-15";

const DIR_OFFSETS = {
  up:    { dx: 0,  dy: -1 },
  down:  { dx: 0,  dy:  1 },
  left:  { dx: -1, dy:  0 },
  right: { dx:  1, dy:  0 },
};

function tileIsTransparent(mapId, x, y) {
  const t = getTile(mapId, x, y);
  if (t === null) {
    return false;
  }
  const def = TILE_TYPES[t];
  return def ? def.walkable : false;
}

export function checkTrainerVision(state) {
  const { currentMap, npcs, player, defeatedTrainers } = state;

  for (const [key, npc] of Object.entries(npcs)) {
    if (!npc.trainer || !npc.visionRange) {
      continue;
    }
    if (defeatedTrainers[npc.battleId]) {
      continue;
    }

    const [nx, ny] = key.split(",").map(Number);
    const off = DIR_OFFSETS[npc.direction];
    if (!off) {
      continue;
    }

    for (let i = 1; i <= npc.visionRange; i++) {
      const cx = nx + off.dx * i;
      const cy = ny + off.dy * i;

      // Stop if non-transparent tile blocks the sightline
      if (!tileIsTransparent(currentMap, cx, cy)) {
        break;
      }

      if (cx === player.x && cy === player.y) {
        return { npc, key };
      }
    }
  }

  return null;
}
