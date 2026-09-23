// MAP_BGM — maps every map ID to a BGM track name from BGM_FILES in audio.js.
// null = silence (no BGM for that map).

export const MAP_BGM = {
  // Town square.
  rootmere:       "rootmere_theme",

  // Home interiors.
  player_home:    "interior_house",
  house_a:        "interior_house",
  house_b:        "interior_house",
  house_c:        "interior_house",
  house_d:        "interior_house",
  house_e:        "interior_house",

  // Service interiors.
  morph_lab:      "interior_centre",
  healing_centre: "interior_centre",
  town_shop:      "interior_centre",

  // Routes — both share the outdoor track; engine won't restart identical track.
  route_1:        "route_outdoor",
  route_2:        "route_outdoor",

  // Brindlewood — uses rootmere_theme as placeholder until a distinct file is available.
  brindlewood:         "rootmere_theme",
  brindlewood_centre:  "interior_centre",
  brindlewood_shop:    "interior_centre",

  // Trial grounds — no dedicated file yet; uses route_outdoor as placeholder.
  trial_grounds: "route_outdoor",
  // Trial arena is silent on entry; battle_trial fires only at Mossa's battle start.
  trial_arena:   null,
};
