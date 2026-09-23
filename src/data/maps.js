// Map data — tile strings, object layers, doors, transitions, encounter tables.
// Exports: TILE_SIZE, VIEWPORT_TILES_X, VIEWPORT_TILES_Y, MAPS, DOORS,
//          MAP_TRANSITIONS, INTERACTION_TEXT, getTile, positionKey

export const TILE_SIZE       = 16;
export const VIEWPORT_TILES_X = 15;
export const VIEWPORT_TILES_Y = 13;

// ─── Tile legend ──────────────────────────────────────────────────────────────
// # boundary/tree   W wall   D door   J ledge (south-hop)   F flower
// G tall grass      ~ water  = bridge  > exit (walk-on)     < return (walk-on)
// S sign   N NPC   C console  T trial gate  B bed  V TV
// P PC (storage terminal)   K counter (cosmetic)   X blocked road
// ─────────────────────────────────────────────────────────────────────────────

// ─── Rootmere (20×18) ────────────────────────────────────────────────────────
export const ROOTMERE_MAP = [
  "####################", // 0
  "#~~~~..............#", // 1  pond
  "#~~~~..............#", // 2
  "#..................#", // 3
  "#WWWW.......WWWWW..#", // 4  home (x=1-4)  lab (x=12-16)
  "#WWWW.......WWWWW..#", // 5
  "#WWWW.......WWWWW..#", // 6
  "#..D........WWDWW..#", // 7  home door x=3  lab door x=14
  "#....F.....F.......#", // 8
  "#.S................#", // 9  sign x=2
  "#..F...............#", // 10
  "#WWWW.......WWWW...#", // 11 willow (x=1-4)  reed (x=12-15)
  "#WWWW.......WWWW...#", // 12
  "#WWWW.......WWWW...#", // 13
  "#..D........WDWW...#", // 14 willow door x=3  reed door x=13
  "#.......F...F......#", // 15
  "#########>##########", // 16 south exit x=9
  "####################", // 17
];

// ─── Route 1 (10×36) — Plain/Wing/Sprout + rare Static ───────────────────────
export const ROUTE_1_MAP = [
  "#####>####", //  0  north exit to Route 2
  "#........#", //  1
  "#..GGGG..#", //  2  tall grass
  "#..GGGG..#", //  3
  "#........#", //  4
  "#........#", //  5  Youngster Jay
  "#........#", //  6
  "#..GGGG..#", //  7
  "#..GGGG..#", //  8
  "#........#", //  9
  "#........#", // 10
  "#JJJJ.JJJ#", // 11 ledge 1 (gap at x=5 channels player through Jay's vision)
  "#........#", // 12
  "#........#", // 13
  "#........#", // 14  Lass Meri
  "#........#", // 15
  "#..GGGG..#", // 16
  "#..GGGG..#", // 17
  "#........#", // 18
  "#........#", // 19
  "#.....~~.#", // 20 pond
  "#.....~~.#", // 21
  "#JJJ.JJJJ#", // 22 ledge 2 (gap at x=4 channels player through Meri's vision)
  "#........#", // 23
  "#........#", // 24
  "#..GGGG..#", // 25  Bug Dale
  "#..GGGG..#", // 26
  "#........#", // 27
  "#.S......#", // 28 south sign
  "#........#", // 29
  "#========#", // 30 bridge
  "#........#", // 31
  "#..GGGG..#", // 32
  "#..GGGG..#", // 33
  "#........#", // 34
  "#####<####", // 35 return tile x=5
];

// ─── Route 2 (10×24) — Stone/Toxin/Wing + bridge gauntlet ───────────────────
export const ROUTE_2_MAP = [
  "#####>####", //  0  north exit to Brindlewood
  "#.S......#", //  1  sign x=2
  "#........#", //  2
  "#........#", //  3  guard NPC area
  "#........#", //  4
  "#........#", //  5
  "#..GGGG..#", //  6
  "#..GGGG..#", //  7
  "#........#", //  8
  "#........#", //  9
  "#..GGGG..#", // 10
  "#..GGGG..#", // 11
  "#........#", // 12
  "#........#", // 13  bridge approach
  "#~~~===~~#", // 14  river + bridge (trainer A)
  "#~~~===~~#", // 15  bridge (trainer B)
  "#~~~===~~#", // 16  bridge (trainer C)
  "#........#", // 17  south bridge approach
  "#........#", // 18
  "#..GGGG..#", // 19
  "#..GGGG..#", // 20
  "#........#", // 21
  "#........#", // 22
  "#####<####", // 23  return to Route 1
];

// ─── Brindlewood (20×22) ────────────────────────────────────────────────────
export const BRINDLEWOOD_MAP = [
  "####################", //  0 tree wall
  "#########>##########", //  1 north exit (locked) x=9
  "#WWWWWW.....WWWWW..#", //  2 Healing Centre (x=1-6), Shop (x=12-16)
  "#WWWWWW.....WWWWW..#", //  3
  "#WWWWWW.....WWWWW..#", //  4
  "#...D...F.F...D....#", //  5 HC door x=4, Shop door x=14, flowers x=8,10
  "#.........~........#", //  6 fountain at x=10
  "#....F.....F.......#", //  7 flowers
  "#...................#", //  8
  "#...................#", //  9
  "#WWWW.WWWW.WWWW....#", // 10 Houses A(1-4) B(6-9) C(11-14)
  "#WWWW.WWWW.WWWW....#", // 11
  "#WWWW.WWWW.WWWW....#", // 12
  "#..D...D....D......#", // 13 doors: A(x=3) B(x=7) C(x=12)
  "#...................#", // 14 street between house rows
  "#WWWW.....WWWW.....#", // 15 Houses D(1-4) E(10-13)
  "#WWWW.....WWWW.....#", // 16
  "#WWWW.....WWWW.....#", // 17
  "#..D......D........#", // 18 doors: D(x=3) E(x=10)
  "#....F.....F.......#", // 19
  "#...................#", // 20
  "#.........F........#", // 21
  "#########<##########", // 22 south exit to Route 2 x=9
];

// ─── Interior maps ────────────────────────────────────────────────────────────

export const PLAYER_HOME_MAP = [
  "##########",
  "#........#",
  "#.B.....V#",  // bed x=2, TV x=8
  "#........#",
  "#...N....#",  // family NPC x=4
  "#...P....#",  // PC terminal x=4
  "#....D...#",  // door x=5
  "##########",
];

export const MORPH_LAB_MAP = [
  "############",
  "#..........#",
  "#.N.....N..#",  // researchers
  "#..........#",
  "#....C.....#",  // starter console
  "#..........#",
  "#.....D....#",  // door
  "############",
];

export const WILLOW_HOUSE_MAP = [
  "##########",
  "#........#",
  "#.N......#",
  "#........#",
  "#....D...#",
  "##########",
];

export const REED_HOUSE_MAP = [
  "##########",
  "#........#",
  "#.N......#",
  "#........#",
  "#....D...#",
  "##########",
];

export const HEALING_CENTRE_MAP = [
  "############",
  "#..........#",
  "#....N.....#",  // nurse NPC x=5
  "#..........#",
  "#...P......#",  // PC terminal x=4
  "#.....D....#",  // door x=6
  "############",
];

export const TOWN_SHOP_MAP = [
  "##########",
  "#........#",
  "#.N......#",  // shopkeeper x=2
  "#........#",
  "#....D...#",
  "##########",
];

export const HOUSE_A_MAP = [
  "##########",
  "#........#",
  "#.N......#",  // pet-owner NPC
  "#........#",
  "#....D...#",
  "##########",
];

export const HOUSE_B_MAP = [
  "##########",
  "#........#",
  "#.N......#",  // move tutor
  "#........#",
  "#....D...#",
  "##########",
];

export const HOUSE_C_MAP = [
  "##########",
  "#........#",
  "#.N...N..#",  // two lore NPCs
  "#........#",
  "#....D...#",
  "##########",
];

export const HOUSE_D_MAP = [
  "##########",
  "#........#",
  "#.N......#",  // gift giver
  "#........#",
  "#....D...#",
  "##########",
];

export const HOUSE_E_MAP = [
  "##########",
  "#........#",
  "#.N......#",  // letter-quest NPC
  "#........#",
  "#....D...#",
  "##########",
];

// ─── Trial Grounds (10×14) — Wild Static/Flying encounters + Rook trainer ────
export const TRIAL_GROUNDS_MAP = [
  "##########", //  0 top boundary
  "#WWWWDWWW#", //  1 arena wall (D at x=5 = arena entrance)
  "#........#", //  2
  "#........#", //  3
  "#..GGGG..#", //  4 tall grass
  "#..GGGG..#", //  5
  "#........#", //  6 Rook trainer (via npcs) at x=1
  "#........#", //  7
  "#..GGGG..#", //  8 tall grass
  "#..GGGG..#", //  9
  "#........#", // 10
  "#.S......#", // 11 sign at x=2
  "#........#", // 12
  "#####<####", // 13 return to Brindlewood at x=5
];

// ─── Trial Arena (12×10) — Indoor arena, Trial Leader Mossa ──────────────────
export const TRIAL_ARENA_MAP = [
  "############", //  0 back wall
  "#..........#", //  1
  "#..........#", //  2 Mossa NPC position (x=5, via npcs)
  "#..........#", //  3
  "#..........#", //  4
  "#..........#", //  5
  "#..........#", //  6
  "#..........#", //  7 player arrives here
  "#####D######", //  8 exit door at x=5
  "############", //  9
];

// ─── Tile type registry ───────────────────────────────────────────────────────

export const TILE_TYPES = {
  ".": { walkable: true,  label: "Path" },
  "F": { walkable: true,  label: "Flower" },
  "G": { walkable: true,  label: "Tall Grass", encounter: true },
  ">": { walkable: true,  label: "Exit",   interactable: true },
  "<": { walkable: true,  label: "Return", interactable: true },
  "=": { walkable: true,  label: "Bridge" },
  "J": { walkable: true,  label: "Ledge",  ledge: true },
  "#": { walkable: false, label: "Boundary" },
  "W": { walkable: false, label: "Wall" },
  "~": { walkable: false, label: "Water" },
  "X": { walkable: false, label: "Blocked Road" },
  "D": { walkable: false, label: "Door",    interactable: true },
  "N": { walkable: false, label: "NPC",     interactable: true },
  "C": { walkable: false, label: "Console", interactable: true },
  "T": { walkable: false, label: "Trial Gate", interactable: true },
  "S": { walkable: false, label: "Sign",    interactable: true },
  "B": { walkable: false, label: "Bed",     interactable: true },
  "V": { walkable: false, label: "TV",      interactable: true },
  "P": { walkable: false, label: "PC",      interactable: true },
  "K": { walkable: false, label: "Counter" },
};

// ─── Map configs ──────────────────────────────────────────────────────────────

export const MAPS = {
  rootmere: {
    name: "Rootmere",
    tiles: ROOTMERE_MAP,
    encounters: false,
    encounterTable: null,
    terrain: "town",
    objects: [
      { kind: "building_home",   x: 1,  y: 4 },
      { kind: "building_lab",    x: 12, y: 4 },
      { kind: "building_willow", x: 1,  y: 11 },
      { kind: "building_reed",   x: 12, y: 11 },
      { kind: "sign", x: 2, y: 9, text: "Rootmere — A quiet starting place." },
      { kind: "flower", x: 5,  y: 8  },
      { kind: "flower", x: 11, y: 8  },
      { kind: "flower", x: 2,  y: 10 },
      { kind: "flower", x: 7,  y: 15 },
      { kind: "flower", x: 11, y: 15 },
    ],
  },

  route_1: {
    name: "Route One",
    tiles: ROUTE_1_MAP,
    encounters: true,
    terrain: "tall_grass",
    encounterTable: [
      { species: "trotter",   weight: 35, levelMin: 2, levelMax: 4 },
      { species: "beakling",  weight: 30, levelMin: 2, levelMax: 4 },
      { species: "chittik",   weight: 33, levelMin: 2, levelMax: 3 },
      { species: "voltquill", weight:  2, levelMin: 3, levelMax: 5 },
    ],
    objects: [],
  },

  route_2: {
    name: "Route Two",
    tiles: ROUTE_2_MAP,
    encounters: true,
    terrain: "tall_grass",
    encounterTable: [
      { species: "trotter",   weight: 20, levelMin: 5, levelMax: 8 },
      { species: "beakling",  weight: 15, levelMin: 5, levelMax: 8 },
      { species: "chittik",   weight: 15, levelMin: 5, levelMax: 7 },
      { species: "pebbling",  weight: 20, levelMin: 5, levelMax: 8 },
      { species: "oozelet",   weight: 20, levelMin: 5, levelMax: 8 },
      { species: "voltquill", weight:  5, levelMin: 5, levelMax: 8 },
      { species: "spriglit",  weight:  5, levelMin: 5, levelMax: 7 },
    ],
    objects: [
      { kind: "sign", x: 2, y: 1, text: "Route Two — Cross the bridge and prove your worth." },
    ],
  },

  brindlewood: {
    name: "Brindlewood",
    tiles: BRINDLEWOOD_MAP,
    encounters: false,
    encounterTable: null,
    terrain: "town",
    objects: [
      // Trial Arena building — 5 tiles wide, positioned so its arch row aligns with the '>' at (9,1)
      { kind: "building_trial", x: 7, y: -2 },
      { kind: "building_heal",  x: 1,  y: 2 },
      { kind: "building_shop",  x: 12, y: 2 },
      { kind: "building_house", x: 1,  y: 10 },
      { kind: "building_house", x: 6,  y: 10 },
      { kind: "building_house", x: 11, y: 10 },
      { kind: "building_house", x: 1,  y: 15 },
      { kind: "building_house", x: 10, y: 15 },
      { kind: "sign", x: 2,  y: 7,  text: ["Brindlewood Healing Centre", "Free healing for Tamers and Morphs."] },
      { kind: "sign", x: 14, y: 7,  text: ["Brindlewood Shop", "Items for every adventuring need."] },
      { kind: "sign", x: 9,  y: 3,  text: ["Trial Gate — Ahead lies the path to the first Trial.", "Seek a reason to pass before heading north."] },
      { kind: "flower", x: 8,  y: 5  },
      { kind: "flower", x: 10, y: 5  },
      { kind: "flower", x: 4,  y: 7  },
      { kind: "flower", x: 11, y: 7  },
      { kind: "flower", x: 4,  y: 19 },
      { kind: "flower", x: 11, y: 19 },
      { kind: "flower", x: 9,  y: 21 },
    ],
  },

  player_home: {
    name: "Player Home",
    tiles: PLAYER_HOME_MAP,
    encounters: false,
    encounterTable: null,
    terrain: "indoor",
    objects: [
      { kind: "bookshelf", x: 5, y: 1 },
      { kind: "bookshelf", x: 6, y: 1 },
      { kind: "pot_plant", x: 7, y: 3 },
    ],
  },

  morph_lab: {
    name: "Morph Lab",
    tiles: MORPH_LAB_MAP,
    encounters: false,
    encounterTable: null,
    terrain: "indoor",
    objects: [
      { kind: "table", x: 3, y: 1 },
      { kind: "table", x: 4, y: 1 },
      { kind: "table", x: 7, y: 1 },
      { kind: "table", x: 8, y: 1 },
      { kind: "pot_plant", x: 10, y: 1 },
    ],
  },

  small_house_1: {
    name: "Willow House",
    tiles: WILLOW_HOUSE_MAP,
    encounters: false,
    encounterTable: null,
    terrain: "indoor",
    objects: [
      { kind: "bookshelf", x: 7, y: 1 },
      { kind: "pot_plant", x: 8, y: 1 },
    ],
  },

  small_house_2: {
    name: "Reed House",
    tiles: REED_HOUSE_MAP,
    encounters: false,
    encounterTable: null,
    terrain: "indoor",
    objects: [
      { kind: "table", x: 6, y: 1 },
      { kind: "pot_plant", x: 8, y: 1 },
    ],
  },

  healing_centre: {
    name: "Healing Centre",
    tiles: HEALING_CENTRE_MAP,
    encounters: false,
    encounterTable: null,
    terrain: "indoor",
    objects: [
      { kind: "pot_plant", x: 1,  y: 1 },
      { kind: "pot_plant", x: 10, y: 1 },
    ],
  },

  town_shop: {
    name: "Brindlewood Shop",
    tiles: TOWN_SHOP_MAP,
    encounters: false,
    encounterTable: null,
    terrain: "indoor",
    objects: [
      { kind: "table", x: 5, y: 1 },
      { kind: "table", x: 6, y: 1 },
      { kind: "pot_plant", x: 8, y: 1 },
    ],
  },

  house_a: {
    name: "House A",
    tiles: HOUSE_A_MAP,
    encounters: false,
    encounterTable: null,
    terrain: "indoor",
    objects: [
      { kind: "bookshelf", x: 6, y: 1 },
      { kind: "pot_plant", x: 8, y: 1 },
    ],
  },

  house_b: {
    name: "House B",
    tiles: HOUSE_B_MAP,
    encounters: false,
    encounterTable: null,
    terrain: "indoor",
    objects: [
      { kind: "bookshelf", x: 6, y: 1 },
      { kind: "bookshelf", x: 7, y: 1 },
    ],
  },

  house_c: {
    name: "House C",
    tiles: HOUSE_C_MAP,
    encounters: false,
    encounterTable: null,
    terrain: "indoor",
    objects: [
      { kind: "bookshelf", x: 4, y: 1 },
      { kind: "bookshelf", x: 5, y: 1 },
      { kind: "pot_plant", x: 8, y: 1 },
    ],
  },

  house_d: {
    name: "Gift House",
    tiles: HOUSE_D_MAP,
    encounters: false,
    encounterTable: null,
    terrain: "indoor",
    objects: [
      { kind: "bookshelf", x: 5, y: 1 },
      { kind: "pot_plant", x: 7, y: 1 },
    ],
  },

  house_e: {
    name: "House E",
    tiles: HOUSE_E_MAP,
    encounters: false,
    encounterTable: null,
    terrain: "indoor",
    objects: [
      { kind: "table", x: 5, y: 1 },
      { kind: "pot_plant", x: 8, y: 1 },
    ],
  },

  trial_grounds: {
    name: "Trial Grounds",
    tiles: TRIAL_GROUNDS_MAP,
    encounters: true,
    terrain: "tall_grass",
    encounterTable: [
      { species: "voltquill", weight: 35, levelMin: 10, levelMax: 14 },
      { species: "beakling",  weight: 30, levelMin: 10, levelMax: 13 },
      { species: "chittik",   weight: 25, levelMin:  8, levelMax: 11 },
      { species: "fulmirex",  weight: 10, levelMin: 13, levelMax: 16 },
    ],
    objects: [],
  },

  trial_arena: {
    name: "Trial Arena",
    tiles: TRIAL_ARENA_MAP,
    encounters: false,
    encounterTable: null,
    terrain: "indoor",
    objects: [],
  },
};

// ─── Door transitions ─────────────────────────────────────────────────────────

export const DOORS = {
  rootmere: {
    "3,7":  { targetMap: "player_home",  targetPos: { x: 5, y: 5 }, name: "Player Home",  message: "You entered your home." },
    "14,7": { targetMap: "morph_lab",    targetPos: { x: 5, y: 5 }, name: "Morph Lab",    message: "You entered the Morph Lab." },
    "3,14": { targetMap: "small_house_1",targetPos: { x: 4, y: 3 }, name: "Willow House", message: "You entered Willow's house." },
    "13,14":{ targetMap: "small_house_2",targetPos: { x: 4, y: 3 }, name: "Reed House",   message: "You entered Reed's house." },
  },
  player_home: {
    "5,6":  { targetMap: "rootmere", targetPos: { x: 3, y: 8 }, name: "Exit", message: "You stepped outside." },
  },
  morph_lab: {
    "6,6":  { targetMap: "rootmere", targetPos: { x: 14, y: 8 }, name: "Exit", message: "You returned to Rootmere." },
  },
  small_house_1: {
    "5,4":  { targetMap: "rootmere", targetPos: { x: 3, y: 15 }, name: "Exit", message: "You returned to Rootmere." },
  },
  small_house_2: {
    "5,4":  { targetMap: "rootmere", targetPos: { x: 13, y: 15 }, name: "Exit", message: "You returned to Rootmere." },
  },
  route_1: {
    "5,35": { targetMap: "rootmere", targetPos: { x: 9, y: 15 }, name: "Return", message: "You returned to Rootmere." },
  },
  route_2: {
    "5,23": { targetMap: "route_1", targetPos: { x: 5, y: 1 }, name: "Return to Route One", message: "You returned to Route One." },
  },
  brindlewood: {
    "9,22": { targetMap: "route_2", targetPos: { x: 5, y: 1 }, name: "South Exit", message: "You returned to Route Two." },
    "4,5":  { targetMap: "healing_centre", targetPos: { x: 5, y: 4 }, name: "Healing Centre", message: "You entered the Healing Centre." },
    "14,5": { targetMap: "town_shop",      targetPos: { x: 4, y: 3 }, name: "Shop",           message: "You entered the shop." },
    "3,13": { targetMap: "house_a",        targetPos: { x: 4, y: 3 }, name: "House A",        message: "You entered." },
    "7,13": { targetMap: "house_b",        targetPos: { x: 4, y: 3 }, name: "House B",        message: "You entered." },
    "12,13":{ targetMap: "house_c",        targetPos: { x: 4, y: 3 }, name: "House C",        message: "You entered." },
    "3,18": { targetMap: "house_d",        targetPos: { x: 4, y: 3 }, name: "Gift House",     message: "You entered.",
      requiresFlag: "bridgeCleared", lockedMessage: "The door is shut. Someone inside calls out — 'Come back once you've crossed the bridge!'" },
    "10,18":{ targetMap: "house_e",        targetPos: { x: 4, y: 3 }, name: "House E",        message: "You entered." },
  },
  healing_centre: {
    "6,5":  { targetMap: "brindlewood", targetPos: { x: 4, y: 6 }, name: "Exit", message: "You left the Healing Centre." },
  },
  town_shop: {
    "5,4":  { targetMap: "brindlewood", targetPos: { x: 14, y: 6 }, name: "Exit", message: "You left the shop." },
  },
  house_a: {
    "5,4":  { targetMap: "brindlewood", targetPos: { x: 3, y: 14 }, name: "Exit", message: "You left." },
  },
  house_b: {
    "5,4":  { targetMap: "brindlewood", targetPos: { x: 7, y: 14 }, name: "Exit", message: "You left." },
  },
  house_c: {
    "5,4":  { targetMap: "brindlewood", targetPos: { x: 12, y: 14 }, name: "Exit", message: "You left." },
  },
  house_d: {
    "5,4":  { targetMap: "brindlewood", targetPos: { x: 3, y: 19 }, name: "Exit", message: "You left." },
  },
  house_e: {
    "5,4":  { targetMap: "brindlewood", targetPos: { x: 10, y: 19 }, name: "Exit", message: "You left." },
  },
  trial_grounds: {
    "5,1":  { targetMap: "trial_arena",  targetPos: { x: 5, y: 7  }, name: "Trial Arena", message: "You entered the Trial Arena."      },
    "5,13": { targetMap: "brindlewood",  targetPos: { x: 9, y: 3  }, name: "Return",      message: "You returned to Brindlewood."      },
  },
  trial_arena: {
    "5,8":  { targetMap: "trial_grounds", targetPos: { x: 5, y: 2 }, name: "Exit",        message: "You returned to the Trial Grounds." },
  },
};

// ─── Walk-on transitions ──────────────────────────────────────────────────────

export const MAP_TRANSITIONS = {
  rootmere: {
    "9,16": {
      targetMap: "route_1", targetPos: { x: 5, y: 34 },
      requiresStarter: true,
      blockedMessage: "Choose your first Morph at the lab before heading out.",
      message: "You stepped onto Route One.",
    },
  },
  route_1: {
    "5,0": {
      targetMap: "route_2", targetPos: { x: 5, y: 22 },
      requiresStarter: false,
      blockedMessage: "",
      message: "You pressed on toward Route Two.",
    },
    "5,35": {
      targetMap: "rootmere", targetPos: { x: 9, y: 15 },
      requiresStarter: false,
      blockedMessage: "",
      message: "You returned to Rootmere.",
    },
  },
  route_2: {
    "5,0": {
      targetMap: "brindlewood", targetPos: { x: 9, y: 20 },
      requiresStarter: false,
      blockedMessage: "",
      message: "You arrived in Brindlewood.",
    },
    "5,23": {
      targetMap: "route_1", targetPos: { x: 5, y: 1 },
      requiresStarter: false,
      blockedMessage: "",
      message: "You returned to Route One.",
    },
  },
  brindlewood: {
    "9,1": {
      targetMap: "trial_grounds", targetPos: { x: 5, y: 12 },
      requiresFlag: "carryingLetter",
      lockedMessage: "The Trial Gate is sealed. Speak with the villagers — someone in town may have a reason for you.",
      message: "You entered the Trial Grounds.",
    },
  },
};

// ─── Static interaction text ──────────────────────────────────────────────────

export const INTERACTION_TEXT = {
  "rootmere:S":        ["Rootmere — A quiet starting place."],
  "rootmere:T":        ["The Rootmere Trial Gate is locked for now."],
  "route_1:X":         ["The way to Thornwild is blocked."],
  "route_2:S":         ["Route Two — Cross the bridge and prove your worth."],
  "trial_grounds:S":   ["Trial Grounds — the proving path of Brindlewood's first Trial.", "Trial Leader Mossa awaits at the arena ahead."],
  "player_home:B":     ["You settle onto your bed.", "Your Morphs wake up fully healed!"],
  "player_home:V":     [
    "There's a documentary on wild Morphs.",
    "\"Spriglit populations thrive near mossy streams.\"",
    "\"Stone-types are rarer past the bridge.\"",
  ],
  "player_home:P":     ["The PC terminal hums. Access your stored Morphs here."],
  "morph_lab:C":       [
    "The research console hums quietly.",
    "Data on all known Morph species is stored here.",
  ],
  "healing_centre:P":  ["A PC terminal. Access your stored Morphs here."],
};

// ─── Helpers ──────────────────────────────────────────────────────────────────

export function getTile(mapId, x, y) {
  const map = MAPS[mapId];
  const row = map?.tiles[y];
  if (!row) { return null; }
  return row[x] ?? null;
}

export function positionKey(x, y) {
  return `${x},${y}`;
}
