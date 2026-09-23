// Player movement — tryMovePlayer, tileAhead, ledge detection, step counter.
// Exports: tryMovePlayer, tileAhead, isLedge
import { isSolidTile } from "./collision.js?v=20260429-19";
import { getTile } from "../data/maps.js?v=20260429-19";
import audio from "./audio.js?v=20260429-19";

const OFFSETS = {
  up:    { x:  0, y: -1 },
  down:  { x:  0, y:  1 },
  left:  { x: -1, y:  0 },
  right: { x:  1, y:  0 },
};

// Steps-per-friendship tick: one friendship point every 100 steps.
const FRIENDSHIP_STEP_INTERVAL = 100;

let _lastStepMs = 0;

export function tryMovePlayer(state, direction) {
  const offset = OFFSETS[direction];
  if (!offset) { return { moved: false, tile: null }; }

  state.player.direction = direction;
  const nextX = state.player.x + offset.x;
  const nextY = state.player.y + offset.y;
  const nextTile = getTile(state.currentMap, nextX, nextY);

  // Ledge (J) — only passable when moving south; hops 2 tiles.
  if (nextTile === "J") {
    if (direction !== "down") { return { moved: false, tile: null }; }
    const landX = nextX;
    const landY = nextY + 1;
    if (isSolidTile(state, landX, landY)) { return { moved: false, tile: null }; }
    state.player.x = landX;
    state.player.y = landY;
    state.player.stepFrame = (state.player.stepFrame + 1) % 2;
    _tickStats(state);
    return { moved: true, tile: getTile(state.currentMap, landX, landY), ledgeHop: true };
  }

  if (isSolidTile(state, nextX, nextY)) { return { moved: false, tile: null }; }

  state.player.x = nextX;
  state.player.y = nextY;
  state.player.stepFrame = (state.player.stepFrame + 1) % 2;
  _tickStats(state);
  return { moved: true, tile: state.map[nextY]?.[nextX] };
}

function _tickStats(state) {
  // Step counter.
  if (state.stats) {
    state.stats.steps = (state.stats.steps ?? 0) + 1;
    // Friendship tick for lead Morph.
    const leader = state.party?.[0];
    if (leader && state.stats.steps % FRIENDSHIP_STEP_INTERVAL === 0) {
      leader.friendship = Math.min(255, (leader.friendship ?? 70) + 1);
    }
  }
  // Step SFX — throttled to 80ms so running doesn't fire on every frame.
  const now = Date.now();
  if (now - _lastStepMs >= 80) {
    _lastStepMs = now;
    audio.playSfx("world_step");
  }
}

export function tileAhead(player) {
  const offset = OFFSETS[player.direction];
  return { x: player.x + offset.x, y: player.y + offset.y };
}

export function isLedge(tile) {
  return tile === "J";
}
