// Global constants for Tiamat.
export const GAME_W = 480;
export const GAME_H = 270;
export const TILE = 16;

export const WALK_MS = 190;     // ms per tile walking
export const RUN_MS = 105;      // ms per tile running (Trail Boots)
export const SURF_MS = 150;     // ms per tile on the Skiff

export const DEPTH = {
  ground: 0,
  decor: 1,
  items: 5,
  actors: 100,        // + y
  above: 5000,
  weatherLow: 5500,
  light: 6000,
  weather: 6500,
  fx: 7000,
};

// Game clock: one in-game minute every REAL_MS_PER_GAME_MIN real milliseconds.
export const REAL_MS_PER_GAME_MIN = 2000 / 60 * 2; // 1 game hour ≈ 2 real minutes

export const MAX_PARTY = 6;
export const BOX_COUNT = 8;
export const BOX_SIZE = 30;
export const MONEY_CAP = 999999;
export const MAX_LEVEL = 100;

export const SAVE_PREFIX = 'tiamat.save.';
export const SETTINGS_KEY = 'tiamat.settings';
export const SAVE_VERSION = 5;

export const DEBUG = typeof location !== 'undefined' && new URLSearchParams(location.search).has('debug');

export const COLORS = {
  ink: 0x14121f,
  panel: 0x1b1e33,
  panel2: 0x262a47,
  line: 0x3d4470,
  hi: 0x5c679e,
  gold: 0xffd65c,
  red: 0xff6b6b,
  green: 0x7cea8c,
  blue: 0x78c8ff,
  white: 0xf6f6fa,
  gray: 0x969cb4,
};
