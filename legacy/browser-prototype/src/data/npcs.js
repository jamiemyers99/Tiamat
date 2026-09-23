// NPC definitions per map.
// Exports: NPCS, getNpcAt
// Trainer NPCs include: battleId, visionRange, visionDir, rewardBase
// Shop NPCs include: shopItems
// Special NPCs include: questId for scripted interactions handled in WorldScreen

export const NPCS = {
  rootmere: {
    "9,8": {
      name: "Rootmere Local",
      palette: "fen",
      direction: "down",
      walkPath:     [{ x:8, y:8 }, { x:9, y:8 }, { x:10, y:8 }, { x:9, y:8 }],
      walkInterval: 100,
      dialogue: [
        "Welcome to Rootmere.",
        "The Morph Lab is to the north-east — can't miss the red roof.",
      ],
    },
  },

  player_home: {
    "4,4": {
      name: "Family",
      palette: "mira",
      direction: "down",
      dialogue: [
        "Take care out there.",
        "Visit the Morph Lab before leaving town.",
        "You can always sleep here to recover.",
      ],
    },
  },

  morph_lab: {
    "2,2": {
      name: "Researcher",
      palette: "elmwood",
      direction: "down",
      dialogue: [
        "Morphs are mysterious companions found in the wild.",
        "Choose your first Morph from the research console.",
        "Once you have one, head south to Route One.",
      ],
    },
    "8,2": {
      name: "Assistant",
      palette: "vella",
      direction: "left",
      dialogue: [
        "Spriglet, Cindlet, and Drizzle are all fine starters.",
        "Each has a different type and strategy.",
        "Good luck, Tamer!",
      ],
    },
  },

  small_house_1: {
    "2,2": {
      name: "Willow",
      palette: "mira",
      direction: "down",
      dialogue: [
        "Route One gets lively once the long grass starts moving.",
        "Bring Potions — the trainers there hit hard.",
      ],
    },
  },

  small_house_2: {
    "2,2": {
      name: "Keeper",
      palette: "keeper",
      direction: "down",
      shopItems: [
        { id: "capsule",  name: "CAPSULE",   price: 10  },
        { id: "potion",   name: "POTION",    price: 20  },
        { id: "antidote", name: "ANTIDOTE",  price: 15  },
        { id: "burnHeal", name: "BURN HEAL", price: 15  },
      ],
    },
  },

  // ── Route One trainers ────────────────────────────────────────────────────
  route_1: {
    "5,5": {
      name: "Youngster Jay",
      palette: "fen",
      direction: "down",
      trainer: true,
      battleId: "r1_youngster_jay",
      rewardBase: 12,
      visionRange: 4,
      dialogue: [
        "Hey! I've been training Trotter all week!",
        "You won't get past me that easily!",
      ],
      afterDialogue: [
        "Ugh. Your Morph is something else.",
        "The tall grass up ahead has trickier types — watch out.",
      ],
    },

    "4,14": {
      name: "Lass Meri",
      palette: "mira",
      direction: "down",
      trainer: true,
      battleId: "r1_lass_meri",
      rewardBase: 14,
      visionRange: 4,
      dialogue: [
        "Oh! You startled me.",
        "My Beakling and Chittik won't go down without a fight!",
      ],
      afterDialogue: [
        "You're pretty good for a new Tamer.",
        "The ledge below leads to the south section — mind the bridge.",
      ],
    },

    "2,25": {
      name: "Bug Catcher Dale",
      palette: "keeper",
      direction: "right",
      trainer: true,
      battleId: "r1_bug_dale",
      rewardBase: 16,
      visionRange: 3,
      dialogue: [
        "I've been waiting for a challenger!",
        "My Chittiks are the toughest bugs on Route One!",
      ],
      afterDialogue: [
        "Your Morphs are something else.",
        "The bridge north of here leads to Brindlewood. Keep your guard up.",
      ],
    },
  },

  // ── Route Two trainers (bridge gauntlet) ──────────────────────────────────
  // Positioned off the central column (x=5) so defeated trainers don't block.
  // All face inward to catch the player walking north along x=5.
  route_2: {
    // First challenge: south of bridge on the left bank
    "2,21": {
      name: "Sailor Tomm",
      palette: "keeper",
      direction: "right",
      trainer: true,
      battleId: "br_sailor_tomm",
      rewardBase: 18,
      visionRange: 3,
      dialogue: [
        "I guard this bridge, friend.",
        "Prove you can handle the deep-water Morphs!",
      ],
      afterDialogue: [
        "Ha! Impressive. Press on, Tamer.",
        "Brindlewood is straight ahead. You've earned it.",
      ],
    },

    // Second challenge: south of bridge in the tall grass section
    "7,19": {
      name: "Picnicker Rin",
      palette: "vella",
      direction: "left",
      trainer: true,
      battleId: "br_picnic_rin",
      rewardBase: 20,
      visionRange: 2,
      dialogue: [
        "I was just enjoying the view when you showed up!",
        "Hope you're ready — my Beakling is no pushover.",
      ],
      afterDialogue: [
        "Well, that was exciting.",
        "Cross the bridge — Brindlewood is waiting.",
      ],
    },

    // Third challenge: north of bridge, final gate before town
    "7,13": {
      name: "Camper Quin",
      palette: "elmwood",
      direction: "left",
      trainer: true,
      battleId: "br_camper_quin",
      rewardBase: 20,
      visionRange: 2,
      dialogue: [
        "I camped out here to challenge passing Tamers!",
        "Trotterion and Pebbling — go!",
      ],
      afterDialogue: [
        "A fine team you've got there.",
        "The town has a Healing Centre. You'll need it.",
      ],
    },

    "4,3": {
      name: "Guard",
      palette: "fen",
      direction: "down",
      dialogue: [
        "Brindlewood is just north of here.",
        "The Healing Centre's pink roof is hard to miss.",
      ],
    },
  },

  // ── Brindlewood town NPCs ─────────────────────────────────────────────────
  brindlewood: {
    "5,8": {
      name: "Townsfolk",
      palette: "elmwood",
      direction: "down",
      walkPath:     [{ x:4, y:8 }, { x:5, y:8 }, { x:6, y:8 }, { x:7, y:8 }, { x:6, y:8 }, { x:5, y:8 }],
      walkInterval: 90,
      dialogue: [
        "Brindlewood — gateway to the Trials!",
        "The Trial Gate to the north has been quiet lately.",
      ],
    },
    "12,9": {
      name: "Kid",
      palette: "fen",
      direction: "down",
      walkPath:     [{ x:11, y:9 }, { x:12, y:9 }, { x:13, y:9 }, { x:12, y:9 }],
      walkInterval: 75,
      dialogue: [
        "I heard there's an ultra-rare Morph on Route One!",
        "Something yellow with quills... really hard to find.",
      ],
    },
  },

  // ── Healing Centre ────────────────────────────────────────────────────────
  healing_centre: {
    "5,2": {
      name: "Nurse",
      palette: "mira",
      direction: "down",
      questId: "heal_party",
      dialogue: [
        "Welcome to the Brindlewood Healing Centre!",
        "Shall I restore your party to full health?",
      ],
    },
  },

  // ── Town Shop ─────────────────────────────────────────────────────────────
  town_shop: {
    "2,2": {
      name: "Shopkeeper",
      palette: "keeper",
      direction: "down",
      shopItems: [
        { id: "capsule",      name: "CAPSULE",       price: 200 },
        { id: "great_capsule",name: "GREAT CAPSULE", price: 600 },
        { id: "potion",       name: "POTION",        price: 300 },
        { id: "super_potion", name: "SUPER POTION",  price: 700 },
        { id: "antidote",     name: "ANTIDOTE",      price: 100 },
        { id: "burnHeal",     name: "BURN HEAL",     price: 250 },
        { id: "awakening",    name: "AWAKENING",     price: 250 },
        { id: "paralyzeHeal", name: "PARALYZ HEAL",  price: 200 },
        { id: "iceHeal",      name: "ICE HEAL",      price: 250 },
      ],
    },
  },

  // ── Brindlewood Houses ────────────────────────────────────────────────────
  house_a: {
    "2,2": {
      name: "Worried Owner",
      palette: "mira",
      direction: "down",
      questId: "lost_pet",
      dialogue: [
        "Oh dear — my little Spriglit wandered into the Route Two grass!",
        "If you find it, please bring it back. It answers to 'Pip'.",
      ],
      afterDialogue: [
        "You found Pip! Oh, thank you!",
        "Please, take these Potions as thanks.",
      ],
    },
  },

  house_b: {
    "2,2": {
      name: "Retired Tamer",
      palette: "elmwood",
      direction: "down",
      questId: "move_tutor",
      dialogue: [
        "Ah, a young Tamer! I know a powerful move — Body Slam.",
        "I'll teach it to one of your Morphs, free of charge.",
        "Just pick the one you want to learn it.",
      ],
      afterDialogue: [
        "Body Slam is yours. Use it wisely.",
        "Power without precision is just noise.",
      ],
    },
  },

  house_c: {
    "2,2": {
      name: "Scholar",
      palette: "elmwood",
      direction: "right",
      dialogue: [
        "Ah yes — 'A Brief History of Morphs.'",
        "The first Tamers formed bonds with wild Morphs centuries ago.",
        "The Trial system grew from those early partnerships.",
      ],
    },
    "7,2": {
      name: "Child",
      palette: "fen",
      direction: "down",
      dialogue: [
        "My Trotter can run really fast!",
        "When it grows up I think it'll be huge.",
      ],
    },
  },

  house_d: {
    "2,2": {
      name: "Old Tamer",
      palette: "keeper",
      direction: "down",
      questId: "gift_morph",
      dialogue: [
        "Ah. A Tamer who cleared the bridge — impressive.",
        "I've been looking after this little one for too long.",
        "Nyxen deserves a proper Tamer. Take good care of it.",
      ],
      afterDialogue: [
        "Nyxen is in good hands now.",
        "Umbra-types are rare. Train it well.",
      ],
    },
  },

  house_e: {
    "2,2": {
      name: "Messenger",
      palette: "vella",
      direction: "down",
      questId: "letter_quest",
      dialogue: [
        "Excuse me — could you deliver this letter to Trial Leader Mossa?",
        "The gate to the north leads to the Trial grounds.",
        "I'd go myself, but my Morphs are exhausted.",
      ],
      afterDialogue: [
        "You've delivered it? Wonderful!",
        "Here — take this Amulet Coin. May your coin purse always be full.",
      ],
    },
  },
  // ── Trial Grounds ─────────────────────────────────────────────────────────
  trial_grounds: {
    "1,6": {
      name: "Veteran Rook",
      palette: "keeper",
      direction: "right",
      trainer: true,
      battleId: "tg_veteran_rook",
      rewardBase: 24,
      visionRange: 6,
      dialogue: [
        "Only seasoned Tamers make it this far!",
        "Show me you're ready before you face Mossa!",
      ],
      afterDialogue: [
        "Not bad. Mossa's a different challenge entirely.",
        "The arena is through the door to the north.",
      ],
    },
  },

  // ── Trial Arena ───────────────────────────────────────────────────────────
  trial_arena: {
    "5,2": {
      name: "Trial Leader Mossa",
      palette: "elmwood",
      direction: "down",
      trainer: true,
      battleId: "trial_mossa",
      rewardBase: 30,
      visionRange: 6,
      openingLog: "Trial Leader Mossa steps forward! The first Trial begins!",
      dialogue: [
        "So you made it through the Grounds. Impressive.",
        "But the Trial itself is another matter.",
      ],
      afterDialogue: [
        "You've proven yourself, Tamer.",
        "The first Trial Badge is yours — you've earned it.",
        "The road ahead will test you further. Travel well.",
      ],
    },
  },
};

export function getNpcAt(mapId, x, y) {
  return NPCS[mapId]?.[`${x},${y}`] ?? null;
}
