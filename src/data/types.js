// The 15 Morph types and the type-effectiveness chart.
// Design notes: Nature/Ember/Tide form the starter triangle. Drake is rare and
// only threatened by Frost and Drake itself. Umbra is immune to Mind; Stone is
// immune to Static; Iron is immune to Toxin.

export const TYPES = ['Plain', 'Nature', 'Ember', 'Tide', 'Static', 'Stone', 'Frost', 'Wing', 'Swarm', 'Toxin', 'Brawl', 'Mind', 'Umbra', 'Iron', 'Drake'];

export const TYPE_COLORS = {
  Plain: 0xa8a29a, Nature: 0x4caf50, Ember: 0xff7a3d, Tide: 0x3d8bfd, Static: 0xf5c542,
  Stone: 0xb38b5d, Frost: 0x7fd6f2, Wing: 0x8fa8ff, Swarm: 0x9bbf3a, Toxin: 0xa560c8,
  Brawl: 0xd0503a, Mind: 0xf06292, Umbra: 0x5e4b8b, Iron: 0x8e9aaf, Drake: 0x6a4cd8,
};

const CHART = {
  Plain:  { Stone: 0.5, Iron: 0.5, Umbra: 0.5 },
  Nature: { Tide: 2, Stone: 2, Ember: 0.5, Nature: 0.5, Wing: 0.5, Swarm: 0.5, Toxin: 0.5, Iron: 0.5, Drake: 0.5 },
  Ember:  { Nature: 2, Swarm: 2, Frost: 2, Iron: 2, Ember: 0.5, Tide: 0.5, Stone: 0.5, Drake: 0.5 },
  Tide:   { Ember: 2, Stone: 2, Tide: 0.5, Nature: 0.5, Drake: 0.5 },
  Static: { Tide: 2, Wing: 2, Static: 0.5, Nature: 0.5, Drake: 0.5, Stone: 0 },
  Stone:  { Ember: 2, Static: 2, Wing: 2, Frost: 2, Toxin: 2, Nature: 0.5, Brawl: 0.5, Iron: 0.5 },
  Frost:  { Nature: 2, Wing: 2, Stone: 2, Drake: 2, Ember: 0.5, Tide: 0.5, Frost: 0.5, Iron: 0.5 },
  Wing:   { Nature: 2, Swarm: 2, Brawl: 2, Static: 0.5, Stone: 0.5, Iron: 0.5 },
  Swarm:  { Nature: 2, Mind: 2, Umbra: 2, Ember: 0.5, Wing: 0.5, Brawl: 0.5, Toxin: 0.5, Iron: 0.5 },
  Toxin:  { Nature: 2, Tide: 2, Toxin: 0.5, Stone: 0.5, Umbra: 0.5, Iron: 0 },
  Brawl:  { Plain: 2, Stone: 2, Frost: 2, Iron: 2, Umbra: 2, Wing: 0.5, Swarm: 0.5, Toxin: 0.5, Mind: 0.5 },
  Mind:   { Brawl: 2, Toxin: 2, Mind: 0.5, Iron: 0.5, Umbra: 0 },
  Umbra:  { Mind: 2, Umbra: 2, Brawl: 0.5, Iron: 0.5 },
  Iron:   { Stone: 2, Frost: 2, Ember: 0.5, Tide: 0.5, Static: 0.5, Iron: 0.5 },
  Drake:  { Drake: 2, Iron: 0.5 },
};

export function effectiveness(atkType, defTypes) {
  let m = 1;
  for (const d of defTypes) { m *= CHART[atkType]?.[d] ?? 1; }
  return m;
}

export function matchups(atkType) {
  const strong = [], weak = [], none = [];
  for (const t of TYPES) {
    const v = CHART[atkType]?.[t] ?? 1;
    if (v >= 2) { strong.push(t); } else if (v === 0) { none.push(t); } else if (v < 1) { weak.push(t); }
  }
  return { strong, weak, none };
}

export function validateChart() {
  for (const a of Object.keys(CHART)) {
    if (!TYPES.includes(a)) { throw new Error(`bad attacker ${a}`); }
    for (const d of Object.keys(CHART[a])) { if (!TYPES.includes(d)) { throw new Error(`bad defender ${d} in ${a}`); } }
  }
  return true;
}
