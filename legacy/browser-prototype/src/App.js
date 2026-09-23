// Main game class — state, lifecycle, screen routing, save/load.
// Exports: Game
import { migrateSave } from "./engine/saveMigration.js?v=20260429-19";
import { applyExperience, createCreature, getLearnsetMove, SPECIES, CREATURES } from "./data/creatures.js?v=20260429-19";
import { MOVES } from "./data/moves.js?v=20260429-19";
import { buildEvolutionQueue } from "./engine/evolution.js?v=20260429-19";
import { createStorage } from "./engine/storage.js?v=20260429-19";
import { DOORS, MAPS } from "./data/maps.js?v=20260429-19";
import { NPCS } from "./data/npcs.js?v=20260429-19";
import { BattleScreen } from "./screens/BattleScreen.js?v=20260429-19";
import { PauseScreen } from "./screens/PauseScreen.js?v=20260429-19";
import { WorldScreen } from "./screens/WorldScreen.js?v=20260429-19";
import { EvolutionScene } from "./screens/EvolutionScene.js?v=20260429-19";
import { MoveLearnPrompt } from "./screens/MoveLearnPrompt.js?v=20260429-19";
import { createEncounterManager } from "./engine/encounters.js?v=20260429-19";
import { Input } from "./engine/input.js?v=20260429-19";
import { beginDialogue } from "./engine/dialogue.js?v=20260429-19";
import { CANVAS_W, CANVAS_H } from "./data/constants.js?v=20260429-19";
import audio from "./engine/audio.js?v=20260429-19";
import { MAP_BGM } from "./data/audio.js?v=20260429-19";

// Expose data globally so screens can access without circular imports.
window._tiamatCreatures = { SPECIES, CREATURES, MOVES };

function getBattleBgm(battleId) {
  if (battleId === "trial_mossa") { return "battle_trial"; }
  return "battle_basic";
}

const TRAINER_BATTLES = {
  r1_youngster_jay: { party: [createCreature("trotter",    4)]                                      },
  r1_lass_meri:     { party: [createCreature("beakling",   3), createCreature("chittik",     4)]    },
  r1_bug_dale:      { party: [createCreature("chittik",    3), createCreature("chittik",     4)]    },
  br_sailor_tomm:   { party: [createCreature("pebbling",   8), createCreature("oozelet",     7)]    },
  br_camper_quin:   { party: [createCreature("trotterion", 9), createCreature("pebbling",    8)]    },
  br_picnic_rin:    { party: [createCreature("beakling",   8)]                                      },
  tg_veteran_rook:  { party: [createCreature("voltquill", 12), createCreature("beakling",   11)]    },
  trial_mossa:      { party: [createCreature("spriggrove",15), createCreature("mantipule",  14), createCreature("trotterion", 16)] },
};

const SAVE_KEY     = "tiamat_save";
const SAVE_VERSION = 3;
const MONEY_CAP    = 999_999;

export class Game {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx    = canvas.getContext("2d");
    this.ctx.imageSmoothingEnabled = false;
    this.ctx.textBaseline = "top";

    this.canvas.width  = CANVAS_W;
    this.canvas.height = CANVAS_H;

    this.input          = new Input();
    this.state          = this.createInitialState();

    const save = this.loadSave();
    if (save) { this.applySave(save); }

    this.worldScreen    = new WorldScreen(canvas, this.ctx);
    this.battleScreen   = new BattleScreen(canvas, this.ctx);
    this.pauseScreen    = new PauseScreen(canvas, this.ctx);
    this.evolutionScene = new EvolutionScene(canvas, this.ctx);
    this.moveLearnPrompt = new MoveLearnPrompt(canvas, this.ctx);

    this._moveLearnQueue = []; // [{creature, newMove}]
    this.lastTime        = 0;
    this.boundFrame      = (time) => this.frame(time);
  }

  createInitialState() {
    return {
      mode:       "world",
      currentMap: "rootmere",
      map:        MAPS.rootmere.tiles,
      mapName:    MAPS.rootmere.name,
      npcs:       structuredClone(NPCS.rootmere ?? {}),
      player: {
        x:         9,
        y:         10,
        direction: "down",
        stepFrame: 0,
      },
      party:  [],
      money:  0,
      items: {
        capsule:       3,
        great_capsule: 0,
        potion:        0,
        super_potion:  0,
        antidote:      0,
        burnHeal:      0,
        awakening:     0,
        paralyzeHeal:  0,
        iceHeal:       0,
      },
      flags: {
        canRun:        false,
        bridgeCleared: false,
      },
      stats: {
        steps:      0,
        battlesWon: 0,
        captures:   0,
      },
      storage:  createStorage(),
      settings: {
        textSpeed:   "normal",
        battleAnims: true,
        windowFrame: 1,
        confirmSave: false,
        audioMaster: 0.8,
        audioBgm:    0.7,
        audioSfx:    0.9,
        audioMuted:  false,
      },
      starterChosen:    false,
      activeDialogue:   null,
      activeChoice:     null,
      activeShop:       null,
      transitionAlpha:  0,
      battle:           null,
      pauseMenu:        null,
      defeatedTrainers: {},
      dex: {
        seen:   new Set(),
        caught: new Set(),
      },
      encounterManager: createEncounterManager(),
      transitions: { doors: DOORS },
      hudMessage: "Welcome to Rootmere.",
      prompt:     "Visit the Morph Lab and choose your first Morph.",
    };
  }

  // ─── Save / Load ──────────────────────────────────────────────────────────

  saveGame() {
    const s = this.state;
    try {
      localStorage.setItem(
        SAVE_KEY,
        JSON.stringify({
          version:          SAVE_VERSION,
          currentMap:       s.currentMap,
          player:           { x: s.player.x, y: s.player.y, direction: s.player.direction },
          party:            s.party,
          money:            s.money,
          items:            s.items,
          flags:            s.flags,
          stats:            s.stats,
          settings:         s.settings,
          storage:          s.storage,
          starterChosen:    s.starterChosen,
          defeatedTrainers: s.defeatedTrainers,
          dex: {
            seen:   [...s.dex.seen],
            caught: [...s.dex.caught],
          },
        }),
      );
    } catch {
      // localStorage unavailable — ignore
    }
  }

  loadSave() {
    try {
      const raw = localStorage.getItem(SAVE_KEY);
      if (!raw) { return null; }
      return JSON.parse(raw);
    } catch {
      return null;
    }
  }

  loadAndApplySave() {
    const save = this.loadSave();
    if (!save) { return false; }
    this.applySave(save);
    return true;
  }

  applySave(raw) {
    let save;
    try {
      save = migrateSave(raw);
    } catch (err) {
      console.warn("Corrupted save:", err.message);
      this.state.mode = "corrupt_save";
      this.state.corruptSaveConfirm = 1; // 0=YES(delete+new), 1=NO(continue blank)
      return;
    }

    const s   = this.state;
    const map = save.currentMap ?? "rootmere";
    s.currentMap = map;
    s.map        = MAPS[map]?.tiles ?? s.map;
    s.mapName    = MAPS[map]?.name  ?? s.mapName;
    s.npcs       = structuredClone(NPCS[map] ?? {});

    if (save.player) {
      s.player.x         = save.player.x         ?? s.player.x;
      s.player.y         = save.player.y         ?? s.player.y;
      s.player.direction = save.player.direction ?? "down";
    }

    s.party            = save.party            ?? [];
    s.money            = save.money            ?? 0;
    s.items            = { ...this.createInitialState().items, ...save.items };
    s.flags            = { canRun: false, bridgeCleared: false, ...save.flags };
    s.stats            = { steps: 0, battlesWon: 0, captures: 0, ...save.stats };
    s.settings         = {
      textSpeed: "normal", battleAnims: true, windowFrame: 1, confirmSave: false,
      audioMaster: 0.8, audioBgm: 0.7, audioSfx: 0.9, audioMuted: false,
      ...save.settings,
    };
    audio.applySettings(s.settings);
    audio.playBgm(MAP_BGM[map] ?? null);
    s.storage          = save.storage ?? createStorage();
    s.starterChosen    = save.starterChosen    ?? false;
    s.defeatedTrainers = save.defeatedTrainers ?? {};

    if (save.dex) {
      s.dex = {
        seen:   new Set(save.dex.seen   ?? []),
        caught: new Set(save.dex.caught ?? []),
      };
    }

    s.hudMessage = `Welcome back to ${s.mapName}.`;
    s.prompt     = "Your journey continues.";
  }

  // ─── Mode transitions ─────────────────────────────────────────────────────

  enterPause() {
    audio.setBgmDuck(true);
    this.state.mode     = "pause";
    this.state.pauseMenu = {
      selectedIndex:  0,
      confirmNewGame: false,
      confirmIndex:   1,
      flashMessage:   null,
      flashTimer:     0,
      subScreen:      null,
    };
  }

  resumeGame() {
    audio.setBgmDuck(false);
    this.state.mode      = "world";
    this.state.pauseMenu = null;
  }

  newGame() {
    try { localStorage.removeItem(SAVE_KEY); } catch { /* ignore */ }
    this.state = this.createInitialState();
  }

  // ─── World actions ────────────────────────────────────────────────────────

  buildWorldActions() {
    return {
      beginBattle:        this.beginBattle.bind(this),
      beginTrainerBattle: this.beginTrainerBattle.bind(this),
      changeMap:          this.changeMap.bind(this),
      chooseStarter:      this.chooseStarter.bind(this),
      healParty:          this.healParty.bind(this),
      openShop:           this.openShop.bind(this),
      saveGame:           this.saveGame.bind(this),
      handleQuest:        this.handleQuest.bind(this),
      openStorage:        this.openStorage.bind(this),
    };
  }

  healParty(context = "home") {
    const s = this.state;
    s.party.forEach((c) => {
      c.hp          = c.maxHp;
      c.status      = null;
      c.statusTurns = 0;
      c.moves.forEach((m) => { m.pp = m.maxPp ?? m.pp; });
    });
    const isNurse = context === "centre";
    if (isNurse) {
      s.flags.lastHealingCentre = {
        mapId:  s.currentMap,
        x:      s.player.x,
        y:      s.player.y,
        facing: s.player.direction,
      };
    }
    const lines = isNurse
      ? ["Your Morphs have all been fully healed!", "Please come again!"]
      : ["You curl up and sleep soundly.", "Your Morphs wake up fully healed!"];
    audio.playSfx("heal");
    beginDialogue(s, isNurse ? "NURSE" : "HOME", lines);
    this.saveGame();
  }

  openShop(items) {
    this.state.activeShop = {
      items,
      selectedIndex: 0,
      scrollOffset:  0,
      flashMessage:  null,
      flashTimer:    0,
      mode:          "root",
      rootIndex:     0,
    };
  }

  openStorage() {
    // Open the storage screen via the pause menu system.
    this.state.mode      = "pause";
    this.state.pauseMenu = {
      selectedIndex:  0,
      confirmNewGame: false,
      confirmIndex:   1,
      flashMessage:   null,
      flashTimer:     0,
      subScreen:      "storage",
      storageState: {
        mode:      "boxes",
        boxIndex:  0,
        slotIndex: 0,
        partyIdx:  0,
        held:      null,
      },
    };
  }

  changeMap(targetMap, targetPos, message) {
    if (!MAPS[targetMap]) { return; }
    audio.playSfx("world_door");
    this.state.transitionAlpha = 1.0;
    this.state.currentMap = targetMap;
    this.state.map        = MAPS[targetMap].tiles;
    this.state.mapName    = MAPS[targetMap].name;
    this.state.npcs       = structuredClone(NPCS[targetMap] ?? {});
    this.state.player.x   = targetPos.x;
    this.state.player.y   = targetPos.y;
    this.state.hudMessage = message;
    audio.playBgm(MAP_BGM[targetMap] ?? null);
    this.state.prompt =
      targetMap === "route_1" || targetMap === "route_2"
        ? "Watch the grass and keep an eye on trainers."
        : "Face doors, NPCs, or markers, then press E.";
    this.saveGame();
  }

  chooseStarter(creatureId) {
    const s = this.state;
    const starter = createCreature(creatureId, 5);
    if (s.starterChosen || !starter) { return; }

    s.party          = [starter];
    s.starterChosen  = true;
    s.activeChoice   = null;
    s.flags.canRun   = true;

    s.dex.seen.add(starter.speciesId ?? starter.id);
    s.dex.caught.add(starter.speciesId ?? starter.id);

    beginDialogue(s, "RESEARCHER", [
      `${starter.name} joined your party!`,
      "Running Shoes obtained — hold Shift to run.",
    ]);

    s.hudMessage = `${starter.name} joined your party.`;
    s.prompt     = "Your first Morph is ready. Head south to Route One.";
    this.saveGame();
  }

  handleQuest(questId, npc) {
    const s = this.state;

    if (questId === "heal_party") {
      this.healParty("centre");
      return;
    }

    if (questId === "gift_morph") {
      if (s.flags.giftMorphReceived) {
        beginDialogue(s, npc.name, npc.afterDialogue ?? ["Nyxen is in good hands."]);
        return;
      }
      const nyxen = createCreature("nyxen", 15);
      if (nyxen) {
        s.dex.seen.add("nyxen");
        s.dex.caught.add("nyxen");
        if (s.party.length < 6) {
          s.party.push(nyxen);
        } else {
          // Deposit directly into the first open storage slot.
          let placed = false;
          for (const box of s.storage.boxes) {
            const idx = box.slots.findIndex((sl) => sl === null);
            if (idx >= 0) { box.slots[idx] = nyxen; placed = true; break; }
          }
          if (!placed) {
            beginDialogue(s, npc.name, ["No room for Nyxen — storage and party are full!"]);
            return;
          }
        }
        s.flags.giftMorphReceived = true;
        s.flags.bridgeCleared     = true; // reaching house_d implies bridge cleared
        beginDialogue(s, npc.name, npc.afterDialogue ?? [
          "Nyxen is in good hands now.",
          "Umbra-types are rare. Train it well.",
        ]);
        this.saveGame();
      }
      return;
    }

    if (questId === "move_tutor") {
      if (s.flags.moveTutorDone) {
        beginDialogue(s, npc.name, npc.afterDialogue ?? ["Body Slam is yours. Use it wisely."]);
        return;
      }
      s.flags.moveTutorDone = true;
      s.items["tm01_body_slam"] = (s.items["tm01_body_slam"] ?? 0) + 1;
      beginDialogue(s, npc.name, [
        "Take this — TM01 Body Slam.",
        "Use it from your bag to teach it to a Morph.",
        "Power without precision is just noise.",
      ]);
      this.saveGame();
      return;
    }

    if (questId === "lost_pet") {
      if (s.flags.lostPetReturned) {
        beginDialogue(s, npc.name, npc.afterDialogue ?? ["You found Pip! Thank you!"]);
      } else {
        beginDialogue(s, npc.name, npc.dialogue ?? [
          "My little Spriglit wandered off!",
          "If you find it, please bring it back.",
        ]);
      }
      return;
    }

    if (questId === "letter_quest") {
      if (s.flags.letterDelivered) {
        if (!s.flags.letterRewardGiven) {
          s.flags.letterRewardGiven = true;
          s.money = Math.min(MONEY_CAP, (s.money ?? 0) + 500);
          beginDialogue(s, npc.name, [
            "You actually faced Mossa? That's incredible!",
            "Here — 500 coins as thanks. A small reward, but heartfelt.",
          ]);
        } else {
          beginDialogue(s, npc.name, npc.afterDialogue ?? ["Thank you again — travel safely!"]);
        }
      } else {
        s.flags.carryingLetter = true;
        beginDialogue(s, npc.name, npc.dialogue ?? [
          "Could you deliver this letter to Trial Leader Mossa?",
          "The gate to the north leads to the Trial grounds.",
        ]);
      }
      return;
    }
  }

  // ─── Battle lifecycle ─────────────────────────────────────────────────────

  beginBattle(wildCreature) {
    if (!this.state.party.length) { return; }
    audio.playSfx("battle_start");
    audio.playBgm("battle_basic");
    this.state.mode   = "battle";
    this.state.battle = this._createBattleState({
      type:           "wild",
      playerCreature: structuredClone(this.state.party[0]),
      enemyParty:     [structuredClone(wildCreature)],
      opponentName:   `Wild ${wildCreature.name}`,
      openingLog:     `A wild ${wildCreature.name} appeared!`,
      rewardCoins:    0,
    });
  }

  beginTrainerBattle(npc) {
    if (!this.state.party.length || !npc?.battleId) { return; }
    const trainer = TRAINER_BATTLES[npc.battleId];
    if (!trainer) { return; }

    const enemyParty  = trainer.party.map((c) => structuredClone(c));
    const maxLevel    = Math.max(...enemyParty.map((c) => c.level));
    const rewardCoins = (npc.rewardBase ?? 16) * maxLevel;

    enemyParty.forEach((c) => this.state.dex.seen.add(c.speciesId ?? c.id));
    audio.playSfx("battle_start");
    audio.playBgm(getBattleBgm(npc.battleId));

    this.state.mode   = "battle";
    this.state.battle = this._createBattleState({
      type:           "trainer",
      trainerId:      npc.battleId,
      playerCreature: structuredClone(this.state.party[0]),
      enemyParty,
      opponentName:   npc.name,
      openingLog:     npc.openingLog ?? `${npc.name} wants to battle!`,
      rewardCoins,
    });
  }

  _createBattleState({ type, trainerId = null, playerCreature, enemyParty, opponentName, openingLog, rewardCoins }) {
    return {
      type,
      trainerId,
      opponentName,
      playerCreature,
      partyIndex:      0,
      enemyParty,
      enemyPartyIndex: 0,
      enemyCreature:   structuredClone(enemyParty[0]),
      selectedIndex:   0,
      forceSwitchIndex: 0,
      menu:            ["FIGHT", "BAG", "CREATURE", "RUN"],
      log:             openingLog,
      phase:           "message",
      rewardCoins,
      xpEarned:        0,
      runAttempts:     0,
      showMoveInfo:    false,
    };
  }

  endBattle(result) {
    const battle = this.state.battle;
    if (!battle) { return; }

    // Sync active creature stats back to its party slot.
    const partyLeader = this.state.party[battle.partyIndex ?? 0];
    if (partyLeader) {
      const bc        = battle.playerCreature;
      partyLeader.level   = bc.level;
      partyLeader.maxHp   = bc.maxHp;
      partyLeader.hp      = bc.hp;
      partyLeader.attack  = bc.attack;
      partyLeader.defense = bc.defense;
      partyLeader.speed   = bc.speed;
      partyLeader.status  = bc.status;
      partyLeader.statusTurns = bc.statusTurns ?? 0;
      partyLeader.moves   = structuredClone(bc.moves);
      partyLeader.xp      = bc.xp ?? partyLeader.xp;
      partyLeader.ivs     = bc.ivs ?? partyLeader.ivs;
    }

    const summary = [];

    if (result?.outcome === "victory" && partyLeader) {
      const { messages, levelled } = applyExperience(partyLeader, battle.xpEarned);
      summary.push(...messages);

      if (levelled) {
        audio.playSfx("level_up");
        const newMove = getLearnsetMove(partyLeader.speciesId ?? partyLeader.id, partyLeader.level);
        if (newMove) {
          if (partyLeader.moves.length < 4) {
            partyLeader.moves.push(newMove);
            summary.push(`${partyLeader.name} learned ${newMove.name}!`);
          } else {
            this._moveLearnQueue.push({ creature: partyLeader, newMove });
          }
        }
      }

      if (battle.type === "trainer") {
        this.state.money = Math.min(MONEY_CAP, this.state.money + battle.rewardCoins);
        this.state.defeatedTrainers[battle.trainerId] = true;
        this.state.stats.battlesWon += 1;
        summary.push(`You earned $${battle.rewardCoins}!`);
        if (battle.trainerId === "trial_mossa") {
          this.state.flags.trial1Won       = true;
          this.state.flags.letterDelivered = true;
          this.state.flags.badges          = [...(this.state.flags.badges ?? []), "sprout"];
          this.state.money                 = Math.min(MONEY_CAP, this.state.money + 2000);
          summary.push("The Sprout Badge is yours!");
          summary.push("You received 2,000 coins!");
        }
      } else {
        this.state.dex.seen.add(battle.enemyCreature.speciesId ?? battle.enemyCreature.id);
        this.state.stats.battlesWon += 1;
        summary.push(`Wild ${battle.enemyCreature.name} fled.`);
      }

    } else if (result?.outcome === "caught") {
      const caught   = result.creature;
      caught.status  = null;
      caught.statusTurns = 0;

      if (partyLeader) {
        partyLeader.hp = Math.max(1, battle.playerCreature.hp);
        const { messages } = applyExperience(partyLeader, battle.xpEarned);
        summary.push(...messages);
      }

      const catchId = caught.speciesId ?? caught.id;
      this.state.dex.seen.add(catchId);
      this.state.dex.caught.add(catchId);
      this.state.stats.captures += 1;

      if (this.state.party.length < 6) {
        this.state.party.push(caught);
        summary.push(`${caught.name} was caught!`);
      } else {
        // Send to storage.
        let stored = false;
        for (const box of this.state.storage.boxes) {
          const idx = box.slots.findIndex((s) => s === null);
          if (idx >= 0) { box.slots[idx] = caught; stored = true; break; }
        }
        summary.push(stored
          ? `${caught.name} was caught and sent to storage!`
          : `${caught.name} was caught! But party and storage are full.`);
      }

    } else if (result?.outcome === "defeat") {
      // Full party restore — whiteout rules.
      this.state.party.forEach((c) => {
        c.hp          = c.maxHp;
        c.status      = null;
        c.statusTurns = 0;
        c.moves.forEach((m) => { m.pp = m.maxPp ?? m.pp; });
      });
      this.state.money        = Math.floor(this.state.money / 2);
      this.state.whiteoutTimer = 90; // frames (~1.5 s at 60 fps)
      summary.push("All your Morphs fainted...");
      summary.push("You scrambled to the nearest safe point!");
      // Teleport to last healing centre or starting home.
      const hc        = this.state.flags.lastHealingCentre;
      const respawnMap = hc?.mapId ?? "player_home";
      const respawnX   = hc?.x    ?? 3;
      const respawnY   = hc?.y    ?? 4;
      if (MAPS[respawnMap]) {
        audio.playSfx("world_door");
        this.state.currentMap       = respawnMap;
        this.state.map              = MAPS[respawnMap].tiles;
        this.state.mapName          = MAPS[respawnMap].name;
        this.state.npcs             = structuredClone(NPCS[respawnMap] ?? {});
        this.state.player.x         = respawnX;
        this.state.player.y         = respawnY;
        this.state.player.direction = "down";
      }

    } else if (result?.outcome === "fled") {
      if (partyLeader) { partyLeader.hp = Math.max(1, battle.playerCreature.hp); }
      summary.push("Got away safely!");

    } else if (result?.message) {
      summary.push(result.message);
    }

    this.state.mode   = "world";
    this.state.battle = null;
    this.state.hudMessage = summary[0] ?? "Back on the path.";
    audio.playBgm(MAP_BGM[this.state.currentMap] ?? null);

    if (summary.length > 1) {
      beginDialogue(this.state, "BATTLE", summary);
    }

    // Process queued move-learn prompts.
    this._processMoveLearnQueue();

    // Check for pending evolutions.
    const evoQueue = buildEvolutionQueue(this.state.party);
    if (evoQueue.length > 0) {
      this.evolutionScene.start(evoQueue, this.state.party, () => {
        audio.playBgm(MAP_BGM[this.state.currentMap] ?? null);
        this.saveGame();
      });
    } else {
      this.saveGame();
    }
  }

  _processMoveLearnQueue() {
    if (this._moveLearnQueue.length === 0) { return; }
    const next = this._moveLearnQueue.shift();
    this.moveLearnPrompt.open(next.creature, next.newMove, () => {
      this._processMoveLearnQueue(); // chain next prompt
      this.saveGame();
    });
  }

  // ─── Corrupt-save screen ─────────────────────────────────────────────────

  _updateCorruptSave() {
    const s = this.state;
    if (this.input.wasPressed("arrowleft")  || this.input.wasPressed("a")) { s.corruptSaveConfirm = 0; }
    if (this.input.wasPressed("arrowright") || this.input.wasPressed("d")) { s.corruptSaveConfirm = 1; }
    if (this.input.wasPressed("enter")      || this.input.wasPressed("e")) {
      if (s.corruptSaveConfirm === 0) {
        try { localStorage.removeItem(SAVE_KEY); } catch { /* ignore */ }
        this.state = this.createInitialState();
      } else {
        s.mode = "world";
      }
    }
  }

  _renderCorruptSave() {
    const ctx = this.ctx;
    const W = CANVAS_W, H = CANVAS_H;
    ctx.fillStyle = "rgba(0,0,0,0.88)";
    ctx.fillRect(0, 0, W, H);
    const bx = 20, by = 68, bw = W - 40, bh = 80;
    ctx.fillStyle = "#12122a";
    ctx.fillRect(bx, by, bw, bh);
    ctx.strokeStyle = "#c84880";
    ctx.lineWidth = 2;
    ctx.strokeRect(bx + 1, by + 1, bw - 2, bh - 2);
    ctx.lineWidth = 1;
    ctx.font = "bold 8px monospace";
    ctx.fillStyle = "#f080b0";
    ctx.fillText("SAVE FILE CORRUPTED", bx + 8, by + 10);
    ctx.font = "7px monospace";
    ctx.fillStyle = "#e0e0e0";
    ctx.fillText("Your save data could not be loaded.", bx + 8, by + 24);
    ctx.fillText("Start a new game? (saves will be deleted)", bx + 8, by + 36);
    const sel = this.state.corruptSaveConfirm;
    const opts = ["YES", "NO"];
    opts.forEach((label, i) => {
      const ox = bx + 20 + i * 60, oy = by + 52;
      if (sel === i) {
        ctx.fillStyle = "#f0f0f0";
        ctx.fillRect(ox - 2, oy - 1, 36, 12);
        ctx.fillStyle = "#12122a";
      } else {
        ctx.fillStyle = "#888888";
      }
      ctx.font = "bold 7px monospace";
      ctx.fillText(label, ox + 4, oy + 1);
    });
  }

  // ─── Main loop ────────────────────────────────────────────────────────────

  start() {
    // Queue initial BGM — will start playing after first user gesture via audio.init().
    audio.playBgm(MAP_BGM[this.state.currentMap] ?? null);
    requestAnimationFrame(this.boundFrame);
  }

  frame(time) {
    const delta = Math.min(32, time - this.lastTime || 16.67);
    this.lastTime = time;

    if (this.state.mode === "world") {
      if (
        this.input.wasPressed("escape") &&
        !this.state.activeDialogue &&
        !this.state.activeChoice &&
        !this.state.activeShop &&
        !this.evolutionScene.active &&
        !this.moveLearnPrompt.active
      ) {
        this.enterPause();
      } else {
        this.worldScreen.update(this.state, this.input, delta, this.buildWorldActions());
      }
      this.worldScreen.render(this.state);

    } else if (this.state.mode === "pause") {
      this.pauseScreen.update(this.state, this.input, delta, {
        resume:    this.resumeGame.bind(this),
        saveGame:  this.saveGame.bind(this),
        loadSave:  this.loadAndApplySave.bind(this),
        newGame:   this.newGame.bind(this),
        teachMove: (creature, newMove) => {
          this._moveLearnQueue.push({ creature, newMove });
          this.resumeGame();
          this._processMoveLearnQueue();
        },
      });
      this.worldScreen.render(this.state);
      if (this.state.mode === "pause") {
        this.pauseScreen.render(this.state);
      }

    } else if (this.state.mode === "corrupt_save") {
      this._updateCorruptSave();
      this._renderCorruptSave();

    } else {
      // battle
      this.battleScreen.update(this.state, this.input, delta, this.endBattle.bind(this));
      this.battleScreen.render(this.state);
    }

    // Overlay screens — rendered on top regardless of mode.
    if (this.evolutionScene.active) {
      this.evolutionScene.update(this.input, delta);
      this.evolutionScene.render();
    }
    if (this.moveLearnPrompt.active) {
      this.moveLearnPrompt.update(this.input);
      this.moveLearnPrompt.render();
    }

    this.input.endFrame();
    requestAnimationFrame(this.boundFrame);
  }
}
