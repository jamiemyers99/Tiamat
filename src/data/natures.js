// Natures: like Pokémon, every Morph has one. It raises one stat by 10% and lowers another by 10%
// (five natures are neutral). Names are original to Tiamat.
export const NATURES = {
  // name: [raised, lowered]
  Reckless: ['atk', 'def'], Fierce: ['atk', 'spa'], Brash: ['atk', 'spd'], Burly: ['atk', 'spe'],
  Placid: ['def', 'atk'], Stout: ['def', 'spa'], Stubborn: ['def', 'spd'], Steadfast: ['def', 'spe'],
  Scholarly: ['spa', 'atk'], Daring: ['spa', 'def'], Brooding: ['spa', 'spd'], Pensive: ['spa', 'spe'],
  Kindly: ['spd', 'atk'], Sensitive: ['spd', 'def'], Wary: ['spd', 'spa'], Serene: ['spd', 'spe'],
  Skittish: ['spe', 'atk'], Restless: ['spe', 'def'], Lively: ['spe', 'spa'], Impulsive: ['spe', 'spd'],
  Even: [null, null], Mellow: [null, null], Curious: [null, null], Dreamy: [null, null], Plucky: [null, null],
};
export const NATURE_NAMES = Object.keys(NATURES);

// Each type leans toward natures that suit it, so e.g. Brawl Morphs are more often strong,
// Mind Morphs clever and Wing Morphs quick. (Any nature can still turn up on any Morph.)
export const TYPE_LEAN = {
  Plain: 'spe', Nature: 'spd', Ember: 'spa', Tide: 'spa', Static: 'spe', Stone: 'def', Frost: 'spa', Wing: 'spe',
  Swarm: 'atk', Toxin: 'def', Brawl: 'atk', Mind: 'spa', Umbra: 'atk', Iron: 'def', Drake: 'atk',
};

export function natureMult(nature, stat) {
  const n = NATURES[nature];
  if (!n || stat === 'hp') { return 1; }
  if (n[0] === stat) { return 1.1; }
  if (n[1] === stat) { return 0.9; }
  return 1;
}

// Roll a nature for a Morph of the given types: natures raising the type's favourite stat are 3× as likely.
export function rollNature(types = [], rnd = Math.random) {
  const lean = new Set(types.map((t) => TYPE_LEAN[t]).filter(Boolean));
  const weights = NATURE_NAMES.map((n) => (lean.has(NATURES[n][0]) ? 3 : 1));
  const total = weights.reduce((a, b) => a + b, 0);
  let r = rnd() * total;
  for (let i = 0; i < NATURE_NAMES.length; i++) {
    r -= weights[i];
    if (r < 0) { return NATURE_NAMES[i]; }
  }
  return NATURE_NAMES[NATURE_NAMES.length - 1];
}

// A stable nature for Morphs from older saves (derived from their id, so it never changes between loads).
export function natureFromId(uid, types = []) {
  let x = (Number(uid) || 1) >>> 0;
  const rnd = () => { x = (x * 1103515245 + 12345) >>> 0; return (x >>> 8) / 16777216; };
  rnd(); rnd();
  return rollNature(types, rnd);
}

export const STAT_LABEL = { atk: 'Attack', def: 'Defense', spa: 'Sp. Atk', spd: 'Sp. Def', spe: 'Speed' };

export function natureText(nature) {
  const n = NATURES[nature];
  if (!n) { return ''; }
  if (!n[0]) { return `${nature} nature`; }
  return `${nature} nature · +${STAT_LABEL[n[0]]} -${STAT_LABEL[n[1]]}`;
}
