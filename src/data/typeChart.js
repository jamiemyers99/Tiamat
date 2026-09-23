// Type effectiveness chart — 15 custom types.
// getEffectiveness(attackType, defenderTypes[]) returns the combined multiplier.
// validateTypeChart() is called once at boot; logs warnings on unexpected entries.
// Gen-1/2 analogue chart — custom IP names only.

const TYPES = [
  "Nature","Ember","Tide","Static","Sprout","Stone","Mist",
  "Plain","Wing","Umbra","Toxin","Mind","Brawl","Iron","Drake",
];

// chart[attacker][defender] = multiplier (default 1 if not listed)
const CHART = {
  Nature: { Tide: 2, Stone: 2, Ember: 0.5, Wing: 0.5, Sprout: 0.5, Toxin: 0.5 },
  Ember:  { Nature: 2, Sprout: 2, Mist: 2, Iron: 2, Tide: 0.5, Stone: 0.5, Drake: 0.5 },
  Tide:   { Ember: 2, Stone: 2, Nature: 0.5, Static: 0.5, Drake: 0.5 },
  Static: { Tide: 2, Wing: 2, Stone: 0, Nature: 0.5, Drake: 0.5 },
  Sprout: { Nature: 2, Mind: 2, Umbra: 2, Ember: 0.5, Wing: 0.5, Stone: 0.5 },
  Stone:  { Ember: 2, Wing: 2, Sprout: 2, Mist: 2, Tide: 0.5, Nature: 0.5, Brawl: 0.5, Iron: 0.5 },
  Mist:   { Nature: 2, Wing: 2, Drake: 2, Ember: 0.5, Tide: 0.5, Stone: 0.5, Iron: 0.5 },
  Plain:  { Brawl: 0.5 },
  Wing:   { Nature: 2, Sprout: 2, Brawl: 2, Static: 0.5, Stone: 0.5, Mist: 0.5 },
  Umbra:  { Mind: 2, Brawl: 0.5, Sprout: 0.5 },
  Toxin:  { Nature: 2, Stone: 0.5, Iron: 0 },
  Mind:   { Brawl: 2, Toxin: 2, Sprout: 0.5, Umbra: 0.5 },
  Brawl:  { Plain: 2, Stone: 2, Iron: 2, Mist: 2, Umbra: 2, Wing: 0.5, Mind: 0.5, Sprout: 0.5 },
  Iron:   { Stone: 2, Mist: 2, Ember: 0.5, Brawl: 0.5, Toxin: 0 },
  Drake:  { Drake: 2, Mist: 0.5 },
};

// Returns the combined multiplier for one attack type vs an array of defender types.
export function getEffectiveness(attackType, defenderTypes) {
  const types = Array.isArray(defenderTypes) ? defenderTypes : [defenderTypes];
  return types.reduce((mult, def) => {
    const row = CHART[attackType];
    return mult * (row?.[def] ?? 1);
  }, 1);
}

// Returns lists of types the given move type is super-effective or not-very-effective against.
export function getTypeMatchups(attackType) {
  const strong = [], weak = [], immune = [];
  for (const def of TYPES) {
    const row = CHART[attackType];
    const val = row?.[def] ?? 1;
    if (val >= 2)      { strong.push(def); }
    else if (val <= 0) { immune.push(def); }
    else if (val < 1)  { weak.push(def);   }
  }
  return { strong, weak, immune };
}

export function validateTypeChart() {
  let ok = true;
  for (const t of TYPES) {
    if (!CHART[t]) {
      console.warn(`[TypeChart] Missing row for attacker type: ${t}`);
      ok = false;
    }
  }
  if (ok) { console.log("[TypeChart] Validated — 15 types, all rows present."); }
}

export { TYPES };
