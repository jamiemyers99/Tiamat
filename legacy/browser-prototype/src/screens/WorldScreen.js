// World overworld screen — rendering and update logic.
// Exports: WorldScreen
import {
  DOORS,
  INTERACTION_TEXT,
  MAPS,
  MAP_TRANSITIONS,
  TILE_SIZE,
  VIEWPORT_TILES_X,
  VIEWPORT_TILES_Y,
  getTile,
  positionKey,
} from "../data/maps.js?v=20260429-19";
import { SPECIES, CREATURES } from "../data/creatures.js?v=20260429-19";
import { getNpcAt } from "../data/npcs.js?v=20260429-19";
import { beginDialogue, getDialogueLine, updateDialogue } from "../engine/dialogue.js?v=20260429-19";
import { maybeStartEncounter } from "../engine/encounters.js?v=20260429-19";
import { tileAhead, tryMovePlayer } from "../engine/movement.js?v=20260429-19";
import { checkTrainerVision } from "../engine/trainerVision.js?v=20260429-19";
import { MOVE_SPEED, RUN_SPEED } from "../data/constants.js?v=20260429-19";
import audio from "../engine/audio.js?v=20260429-19";

const STARTER_OPTIONS = ["spriglet", "cindlet", "drizzle"];
const CONFIRM_KEYS    = ["enter", "e", " "];

// ─── Palette ──────────────────────────────────────────────────────────────────
const P = {
  black:       "#0f380f",
  darkGreen:   "#1e4010",
  midGreen:    "#306230",
  green:       "#5aa03e",
  lightGreen:  "#8bbc0f",
  palePaper:   "#d7efc2",
  grassDark:   "#3a6a10",
  grassMid:    "#5a9a18",
  grassLight:  "#9bbc0f",
  water:       "#3860a8",
  waterMid:    "#4878c0",
  waterLight:  "#88b8e8",
  wallCream:   "#f0e8c8",
  wallShadow:  "#c8b888",
  window:      "#88c8e0",
  windowLight: "#d0f0ff",
  roofRedDk:   "#8a2010",
  roofRedMid:  "#c83e20",
  roofRedHi:   "#e06040",
  roofBlueDk:  "#1a3a8a",
  roofBlueMid: "#2e5ec4",
  roofBlueHi:  "#5888e8",
  roofGrDk:    "#2e5030",
  roofGrMid:   "#4a8030",
  roofGrHi:    "#6ab040",
  roofPinkDk:  "#8a2858",
  roofPinkMid: "#c84880",
  roofPinkHi:  "#f080b0",
  awningGrDk:  "#1e5020",
  awningGrMid: "#389838",
  door:        "#5c3018",
  doorLight:   "#8a5030",
  brickDk:     "#8a6040",
  brickMid:    "#b08060",
  bridgeDk:    "#6a4820",
  bridgeMid:   "#9a7040",
  bridgeLight: "#c09060",
  pathDk:      "#8bac0f",
  pathLight:   "#9bbc1f",
  indoorFloor: "#d8c8a0",
  indoorLine:  "#c0a880",
  bedBlue:     "#4860b8",
  bedLight:    "#a0b8e8",
  consoleBlue: "#607898",
  flowerYel:   "#e8d830",
  flowerPink:  "#e868a0",
  treeTrunk:   "#7a5030",
  treeDk:      "#1a4010",
  treeMid:     "#2e6220",
  treeHi:      "#4a9030",
  signBoard:   "#d4b070",
  signPost:    "#8a6030",
};

// ─── Building stamp renderer ──────────────────────────────────────────────────
// Draws a multi-tile building at map-tile position (bx, by) with given roof type.
// screenX/Y = pixel position of top-left corner of the stamp on screen.

function drawBuilding(ctx, screenX, screenY, kind) {
  const T  = TILE_SIZE;
  const is = (k) => kind === k;

  // ── Trial Arena — stone gateway, completely different look ────────────────
  if (is("building_trial")) {
    const pw   = 5 * T;  // 5 tiles wide
    const wallY2 = screenY + T * 2;
    const wallY3 = screenY + T * 3;

    // Rows 0–1 — upper battlement (usually off-screen above map boundary)
    ctx.fillStyle = "#353d3d";
    ctx.fillRect(screenX, screenY, pw, T * 2);
    ctx.fillStyle = "#424e4e";
    ctx.fillRect(screenX + 1, screenY + 1, pw - 2, T * 2 - 2);
    // battlement notches
    for (let i = 0; i < 5; i++) {
      ctx.fillStyle = "#262d2d";
      ctx.fillRect(screenX + i * T + 4, screenY, T - 8, 5);
    }

    // Row 2 — stone wall with narrow arrow-slit windows
    ctx.fillStyle = "#485050";
    ctx.fillRect(screenX, wallY2, pw, T);
    ctx.fillStyle = "#353d3d";
    ctx.fillRect(screenX, wallY2 + 6, pw, 1);
    ctx.fillRect(screenX, wallY2 + 12, pw, 1);
    for (let i = 0; i < 5; i++) {
      if (i === 2) { continue; }  // skip centre column (arch will be there)
      ctx.fillStyle = "#1a2020";
      ctx.fillRect(screenX + i * T + 6, wallY2 + 2, 3, 10);
    }
    ctx.fillStyle = "#1a2020";
    ctx.fillRect(screenX, wallY2, pw, 1);

    // Row 3 — archway gate (centred on tile 2 of the 5-tile stamp = the '>' tile)
    ctx.fillStyle = "#485050";
    ctx.fillRect(screenX, wallY3, pw, T);
    ctx.fillStyle = "#353d3d";
    ctx.fillRect(screenX, wallY3 + T - 4, pw, 4);
    // arch opening (centred at offset 40 from stamp left)
    const archX = screenX + 2 * T + T / 2 - 4;
    ctx.fillStyle = "#080808";
    ctx.fillRect(archX, wallY3, 9, T - 4);
    // arch lintel and columns
    ctx.fillStyle = "#606e6e";
    ctx.fillRect(archX - 2, wallY3, 13, 3);
    ctx.fillRect(archX - 1, wallY3 + 3, 1, T - 7);
    ctx.fillRect(archX + 9, wallY3 + 3, 1, T - 7);
    ctx.fillStyle = "#1a2020";
    ctx.fillRect(screenX, wallY3, pw, 1);
    return;
  }

  // Choose roof colours by building type
  let roofDk, roofMid, roofHi;
  if (is("building_lab")) {
    roofDk = P.roofRedDk; roofMid = P.roofRedMid; roofHi = P.roofRedHi;
  } else if (is("building_reed")) {
    roofDk = P.roofGrDk; roofMid = P.roofGrMid; roofHi = P.roofGrHi;
  } else if (is("building_heal")) {
    roofDk = P.roofPinkDk; roofMid = P.roofPinkMid; roofHi = P.roofPinkHi;
  } else {
    roofDk = P.roofBlueDk; roofMid = P.roofBlueMid; roofHi = P.roofBlueHi;
  }

  const wide = is("building_lab")  ? 5
             : is("building_heal") ? 6
             : is("building_shop") ? 5
             : 4; // tiles
  const pw   = wide * T;
  const ph   = 4 * T;

  // Row 0 — roof top / chimney
  ctx.fillStyle = roofDk;
  ctx.fillRect(screenX, screenY, pw, T);
  ctx.fillStyle = roofMid;
  ctx.fillRect(screenX + 2,      screenY + 2, pw - 4, T - 4);
  ctx.fillStyle = roofHi;
  ctx.fillRect(screenX + 4,      screenY + 4, pw - 8, 4);
  // chimney
  ctx.fillStyle = P.brickMid;
  ctx.fillRect(screenX + pw - 8, screenY,     5, 6);
  ctx.fillStyle = P.brickDk;
  ctx.fillRect(screenX + pw - 8, screenY,     5, 2);

  // Row 1 — roof body
  ctx.fillStyle = roofDk;
  ctx.fillRect(screenX, screenY + T, pw, T);
  ctx.fillStyle = roofMid;
  ctx.fillRect(screenX + 1, screenY + T + 1, pw - 2, T - 2);
  ctx.fillStyle = roofHi;
  // diagonal highlight dashes
  for (let i = 0; i < wide; i++) {
    ctx.fillRect(screenX + 3 + i * T, screenY + T + 2, 6, 2);
  }

  // Row 2 — roof underhang + top of wall + windows
  ctx.fillStyle = roofDk;
  ctx.fillRect(screenX, screenY + T * 2, pw, 4);
  ctx.fillStyle = P.wallCream;
  ctx.fillRect(screenX, screenY + T * 2 + 4, pw, T - 4);
  ctx.fillStyle = P.wallShadow;
  ctx.fillRect(screenX, screenY + T * 2 + 4, pw, 2);
  // windows
  const winY = screenY + T * 2 + 6;
  const winH = T - 10;
  for (let i = 0; i < wide - 1; i++) {
    const wx = screenX + 3 + i * T;
    ctx.fillStyle = P.window;
    ctx.fillRect(wx, winY, 10, winH);
    ctx.fillStyle = P.windowLight;
    ctx.fillRect(wx + 1, winY + 1, 4, 3);
    ctx.fillStyle = P.black;
    ctx.fillRect(wx, winY, 10, 1);
    ctx.fillRect(wx, winY, 1, winH);
  }

  // Row 3 — wall + door + brick base
  const wallY = screenY + T * 3;
  ctx.fillStyle = P.wallCream;
  ctx.fillRect(screenX, wallY, pw, T);
  // brick base
  ctx.fillStyle = P.brickMid;
  ctx.fillRect(screenX, wallY + T - 4, pw, 4);
  ctx.fillStyle = P.brickDk;
  for (let i = 0; i < wide; i++) {
    ctx.fillRect(screenX + i * T, wallY + T - 4, 1, 4);
    ctx.fillRect(screenX + i * T + T / 2, wallY + T - 4, 1, 4);
  }
  // door
  const doorX = screenX + Math.floor(wide / 2) * T - 3;
  ctx.fillStyle = P.door;
  ctx.fillRect(doorX, wallY + 2, 7, T - 2);
  ctx.fillStyle = P.doorLight;
  ctx.fillRect(doorX + 1, wallY + 3, 5, 5);
  ctx.fillStyle = "#d4a040";
  ctx.fillRect(doorX + 5, wallY + 8, 1, 2);
  // wall shadow line
  ctx.fillStyle = P.black;
  ctx.fillRect(screenX, wallY, pw, 1);

  // Healing Centre: plus symbol on roof
  if (is("building_heal")) {
    const cx = screenX + Math.floor(pw / 2) - 2;
    const cy = screenY + 2;
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(cx + 2, cy, 2, 6);
    ctx.fillRect(cx, cy + 2, 6, 2);
  }

  // Town Shop: green awning strip under roofline
  if (is("building_shop")) {
    const ay = screenY + T * 2 + 2;
    ctx.fillStyle = P.awningGrDk;
    ctx.fillRect(screenX, ay, pw, 4);
    ctx.fillStyle = P.awningGrMid;
    for (let i = 0; i < wide; i++) {
      ctx.fillRect(screenX + i * T + 2, ay + 1, T - 4, 2);
    }
  }
}

export class WorldScreen {
  constructor(canvas, ctx) {
    this.canvas      = canvas;
    this.ctx         = ctx;
    this.moveTimer   = MOVE_SPEED;
    this.hudLocation = document.getElementById("hud-location");
    this.hudParty    = document.getElementById("hud-party");
    this.hudCoins    = document.getElementById("hud-coins");
    this.hudPos      = document.getElementById("hud-pos");
    this.hudTip      = document.getElementById("hud-tip");
    // Trainer vision state
    this._visionFlash    = null; // { npc, key, timer }
    this._frameTick      = 0;
  }

  // ─── Update ──────────────────────────────────────────────────────────────

  update(state, input, delta, actions) {
    if (!state.activeDialogue && !state.activeShop && !state.activeChoice && !this._visionFlash) {
      this._tickNpcWalkers(state);
    }

    if (state.activeDialogue) {
      updateDialogue(state, input, delta);
      return;
    }

    if (state.activeShop) {
      this.updateShop(state, input, delta, actions);
      return;
    }

    if (state.activeChoice?.type === "starter") {
      this.updateStarterChoice(state, input, actions.chooseStarter);
      return;
    }

    // Trainer ! emote — lock input while flash shows
    if (this._visionFlash) {
      this._visionFlash.timer -= delta;
      if (this._visionFlash.timer <= 0) {
        const { npc } = this._visionFlash;
        this._visionFlash = null;
        actions.beginTrainerBattle(npc);
      }
      return;
    }

    if (input.wasPressed(...CONFIRM_KEYS)) {
      this.tryInteract(state, actions);
      return;
    }

    // Determine movement speed (running shoes)
    const running  = state.flags?.canRun && input.isDown("shift");
    const interval = running ? RUN_SPEED : MOVE_SPEED;
    this.moveTimer += delta;

    const direction = input.getMoveDirection();
    if (!direction || this.moveTimer < interval) {
      return;
    }

    this.moveTimer = 0;
    const result = tryMovePlayer(state, direction);
    if (!result.moved) {
      return;
    }

    this.afterMove(state, result.tile, actions);

    // Check trainer vision after every step
    const spotted = checkTrainerVision(state);
    if (spotted) {
      this._visionFlash = { npc: spotted.npc, timer: 900 };
      audio.playSfx("world_encounter");
    }
  }

  updateShop(state, input, delta, actions) {
    const shop = state.activeShop;
    if (!shop) { return; }

    if (shop.flashTimer > 0) {
      shop.flashTimer = Math.max(0, shop.flashTimer - delta);
    }

    // ── Root menu ─────────────────────────────────────────────────────────
    if (shop.mode === "root") {
      const ROOT_OPTS = ["BUY", "SELL", "EXIT"];
      if (input.wasPressed("escape", "backspace")) {
        state.activeShop = null;
        return;
      }
      if (input.wasPressed("arrowup", "w")) {
        shop.rootIndex = (shop.rootIndex + ROOT_OPTS.length - 1) % ROOT_OPTS.length;
        audio.playSfx("ui_move");
        return;
      }
      if (input.wasPressed("arrowdown", "s")) {
        shop.rootIndex = (shop.rootIndex + 1) % ROOT_OPTS.length;
        audio.playSfx("ui_move");
        return;
      }
      if (input.wasPressed(...CONFIRM_KEYS)) {
        const choice = ROOT_OPTS[shop.rootIndex];
        if (choice === "BUY") {
          shop.mode          = "buy";
          shop.selectedIndex = 0;
          shop.scrollOffset  = 0;
        } else if (choice === "SELL") {
          const sellables = shop.items.filter((it) => (state.items[it.id] ?? 0) > 0);
          if (sellables.length === 0) {
            shop.flashMessage = "Nothing to sell.";
            shop.flashTimer   = 1800;
          } else {
            shop.mode          = "sell";
            shop.selectedIndex = 0;
            shop.scrollOffset  = 0;
          }
        } else {
          state.activeShop = null;
        }
      }
      return;
    }

    // ── Buy mode ──────────────────────────────────────────────────────────
    if (shop.mode === "buy") {
      if (input.wasPressed("escape", "backspace")) {
        shop.mode      = "root";
        shop.rootIndex = 0;
        return;
      }
      const PAGE = 5;
      if (input.wasPressed("arrowup", "w")) {
        shop.selectedIndex =
          (shop.selectedIndex + shop.items.length - 1) % shop.items.length;
        if (shop.selectedIndex < shop.scrollOffset)
          shop.scrollOffset = shop.selectedIndex;
        if (shop.selectedIndex === shop.items.length - 1)
          shop.scrollOffset = Math.max(0, shop.items.length - PAGE);
        audio.playSfx("ui_move");
        return;
      }
      if (input.wasPressed("arrowdown", "s")) {
        shop.selectedIndex = (shop.selectedIndex + 1) % shop.items.length;
        if (shop.selectedIndex >= shop.scrollOffset + PAGE)
          shop.scrollOffset = shop.selectedIndex - PAGE + 1;
        if (shop.selectedIndex === 0)
          shop.scrollOffset = 0;
        audio.playSfx("ui_move");
        return;
      }
      if (input.wasPressed(...CONFIRM_KEYS)) {
        const item = shop.items[shop.selectedIndex];
        if (state.money < item.price) {
          shop.flashMessage = "Not enough coins.";
          shop.flashTimer   = 1800;
          return;
        }
        state.money -= item.price;
        state.items[item.id] = (state.items[item.id] ?? 0) + 1;
        shop.flashMessage = `Bought ${item.name.toLowerCase()}!`;
        shop.flashTimer   = 1800;
        actions.saveGame();
      }
      return;
    }

    // ── Sell mode ─────────────────────────────────────────────────────────
    if (shop.mode === "sell") {
      if (input.wasPressed("escape", "backspace")) {
        shop.mode          = "root";
        shop.rootIndex     = 0;
        shop.selectedIndex = 0;
        return;
      }
      const sellItems = shop.items.filter((it) => (state.items[it.id] ?? 0) > 0);
      if (sellItems.length === 0) { shop.mode = "root"; return; }
      const PAGE = 5;
      if (input.wasPressed("arrowup", "w")) {
        shop.selectedIndex =
          (shop.selectedIndex + sellItems.length - 1) % sellItems.length;
        if (shop.selectedIndex < shop.scrollOffset)
          shop.scrollOffset = shop.selectedIndex;
        if (shop.selectedIndex === sellItems.length - 1)
          shop.scrollOffset = Math.max(0, sellItems.length - PAGE);
        audio.playSfx("ui_move");
        return;
      }
      if (input.wasPressed("arrowdown", "s")) {
        shop.selectedIndex = (shop.selectedIndex + 1) % sellItems.length;
        if (shop.selectedIndex >= shop.scrollOffset + PAGE)
          shop.scrollOffset = shop.selectedIndex - PAGE + 1;
        if (shop.selectedIndex === 0)
          shop.scrollOffset = 0;
        audio.playSfx("ui_move");
        return;
      }
      if (input.wasPressed(...CONFIRM_KEYS)) {
        const item      = sellItems[shop.selectedIndex];
        const sellPrice = Math.floor(item.price / 2);
        state.items[item.id] = (state.items[item.id] ?? 0) - 1;
        if (state.items[item.id] <= 0) { delete state.items[item.id]; }
        state.money += sellPrice;
        shop.flashMessage = `Sold for ${sellPrice} coins!`;
        shop.flashTimer   = 1800;
        const remaining = shop.items.filter((it) => (state.items[it.id] ?? 0) > 0);
        if (shop.selectedIndex >= remaining.length) {
          shop.selectedIndex = Math.max(0, remaining.length - 1);
        }
        actions.saveGame();
      }
    }
  }

  updateStarterChoice(state, input, chooseStarter) {
    if (input.wasPressed("arrowup", "w")) {
      state.activeChoice.selectedIndex =
        (state.activeChoice.selectedIndex + STARTER_OPTIONS.length - 1) %
        STARTER_OPTIONS.length;
      return;
    }
    if (input.wasPressed("arrowdown", "s")) {
      state.activeChoice.selectedIndex =
        (state.activeChoice.selectedIndex + 1) % STARTER_OPTIONS.length;
      return;
    }
    if (input.wasPressed(...CONFIRM_KEYS)) {
      chooseStarter(STARTER_OPTIONS[state.activeChoice.selectedIndex]);
    }
  }

  afterMove(state, tile, actions) {
    if (tile === "G") {
      if (!state.starterChosen) {
        state.hudMessage = "Visit the Morph Lab before heading into the grass.";
        state.prompt = "Choose your first Morph at the lab.";
        return;
      }
      state.hudMessage = "Tall grass sways around your boots.";
      state.prompt = "Wild Morphs may appear here.";
      const encounter = maybeStartEncounter(state);
      if (encounter) {
        if (state.dex) {
          state.dex.seen.add(encounter.id);
        }
        audio.playSfx("world_encounter");
        actions.beginBattle(encounter);
      }
      return;
    }

    if (tile === ">") {
      const key = positionKey(state.player.x, state.player.y);
      const trans = MAP_TRANSITIONS[state.currentMap]?.[key];
      if (trans) {
        if (trans.locked) {
          state.hudMessage = trans.lockedMessage ?? "The way is blocked.";
          state.prompt = "Find another path.";
          return;
        }
        if (trans.requiresFlag && !state.flags?.[trans.requiresFlag]) {
          state.hudMessage = trans.lockedMessage ?? "The way is blocked.";
          state.prompt = "Find another path.";
          return;
        }
        if (trans.requiresStarter && !state.starterChosen) {
          state.hudMessage = trans.blockedMessage;
          state.prompt = "Choose a Morph first.";
          return;
        }
        actions.changeMap(trans.targetMap, trans.targetPos, trans.message);
      }
      return;
    }

    if (tile === "<") {
      const key = positionKey(state.player.x, state.player.y);
      const transition = DOORS[state.currentMap]?.[key];
      if (transition) {
        actions.changeMap(transition.targetMap, transition.targetPos, transition.message);
      }
      return;
    }

    if (tile === "=") {
      state.hudMessage = "The wooden bridge creaks softly.";
      state.prompt = "Bridges are safe to cross.";
      return;
    }

    const routeMsg = {
      route_1:      "The route stretches ahead.",
      route_2:      "The bridge winds north toward Brindlewood.",
      brindlewood:  "Brindlewood bustles with Tamers and their Morphs.",
    };
    state.hudMessage = routeMsg[state.currentMap] ?? "The village feels calm and close-knit.";
    const routePrompt = {
      rootmere:    "Visit the lab, then head south for Route One.",
      brindlewood: "Explore shops, houses, and the Healing Centre.",
    };
    state.prompt = routePrompt[state.currentMap] ?? "Face doors, NPCs, and markers, then press E.";
  }

  _tickNpcWalkers(state) {
    const npcs = state.npcs;
    const px = state.player.x;
    const py = state.player.y;
    const toMove = [];

    for (const [key, npc] of Object.entries(npcs)) {
      if (!npc.walkPath || npc.trainer) { continue; }
      npc._walkTick = (npc._walkTick ?? 0) + 1;
      if (npc._walkTick < (npc.walkInterval ?? 60)) { continue; }
      const [cx, cy] = key.split(",").map(Number);
      const nextIdx  = ((npc._walkIdx ?? 0) + 1) % npc.walkPath.length;
      const next     = npc.walkPath[nextIdx];
      if ((next.x === px && next.y === py) || npcs[`${next.x},${next.y}`]) { continue; }
      toMove.push({ fromKey: key, cx, cy, npc, nextIdx, next });
    }

    for (const { fromKey, cx, cy, npc, nextIdx, next } of toMove) {
      if (state.npcs[fromKey] !== npc) { continue; }
      npc._walkTick = 0;
      npc._walkIdx  = nextIdx;
      npc.direction = next.x > cx ? "right" : next.x < cx ? "left" : next.y > cy ? "down" : "up";
      delete state.npcs[fromKey];
      state.npcs[`${next.x},${next.y}`] = npc;
    }
  }

  tryInteract(state, actions) {
    const target = this.facingTarget(state);

    if (this.tryTransition(state, target, actions.changeMap)) { return; }

    // Check for NPC at the facing tile regardless of ground tile character.
    // (NPCs can occupy walkable ground tiles in the layered map design.)
    const npc = getNpcAt(state.currentMap, target.x, target.y);
    if (npc) {
      npc.direction = oppositeDirection(state.player.direction);
      if (npc.trainer) {
        if (state.defeatedTrainers[npc.battleId]) {
          beginDialogue(state, npc.name, npc.afterDialogue ?? ["We already battled today."]);
          return;
        }
        actions.beginTrainerBattle(npc);
        return;
      }
      if (npc.shopItems) {
        actions.openShop(npc.shopItems);
        return;
      }
      if (npc.questId) {
        actions.handleQuest(npc.questId, npc);
        return;
      }
      beginDialogue(state, npc.name, npc.dialogue ?? ["..."]);
      return;
    }

    if (state.currentMap === "morph_lab" && target.tile === "C") {
      if (state.starterChosen) {
        state.hudMessage = "You already chose your first Morph.";
        state.prompt = "The console rests in standby.";
      } else {
        state.activeChoice = { type: "starter", selectedIndex: 0 };
        state.hudMessage = "Choose your first Morph.";
        state.prompt = "Use arrows, then press Enter to confirm.";
      }
      return;
    }

    if (target.tile === "B") {
      actions.healParty("home");
      return;
    }

    if (target.tile === "P") {
      actions.openStorage();
      return;
    }

    if (target.tile === "V") {
      const tvLines = INTERACTION_TEXT[`${state.currentMap}:V`]
        ?? INTERACTION_TEXT["player_home:V"]
        ?? ["There's nothing interesting on."];
      beginDialogue(state, "TV", tvLines);
      return;
    }

    if (target.tile === "T") {
      beginDialogue(state, "TRIAL GATE", ["The Rootmere Trial Gate is locked for now."]);
      return;
    }
    if (target.tile === "X") {
      beginDialogue(state, "ROADBLOCK", ["The way to Thornwild is blocked for now."]);
      return;
    }

    // Check object-layer signs at the facing tile.
    const signObj = (MAPS[state.currentMap]?.objects ?? [])
      .find((o) => o.kind === "sign" && o.x === target.x && o.y === target.y);
    if (signObj?.text) {
      beginDialogue(state, "SIGN", Array.isArray(signObj.text) ? signObj.text : [signObj.text]);
      return;
    }

    const lines = INTERACTION_TEXT[`${state.currentMap}:${target.tile}`];
    if (lines) {
      beginDialogue(state, interactionSpeaker(target.tile), lines);
      return;
    }

    state.hudMessage = "Only reeds and porch-light answer back.";
    state.prompt = "Nothing nearby responds.";
  }

  tryTransition(state, target, changeMap) {
    const key = positionKey(target.x, target.y);

    if (target.tile === "D") {
      const transition = DOORS[state.currentMap]?.[key];
      if (!transition) { return false; }
      if (transition.requiresFlag && !state.flags[transition.requiresFlag]) {
        beginDialogue(state, "DOOR", [transition.lockedMessage ?? "The door is locked."]);
        return true;
      }
      changeMap(transition.targetMap, transition.targetPos, transition.message);
      return true;
    }

    if (target.tile === ">") {
      const transition = MAP_TRANSITIONS[state.currentMap]?.[key];
      if (!transition) { return false; }
      if (transition.locked) {
        beginDialogue(state, "GATE", [transition.lockedMessage ?? "The way is blocked."]);
        return true;
      }
      if (transition.requiresFlag && !state.flags?.[transition.requiresFlag]) {
        beginDialogue(state, "GATE", [transition.lockedMessage ?? "The way is blocked."]);
        return true;
      }
      if (transition.requiresStarter && !state.starterChosen) {
        beginDialogue(state, "ROOTMERE", [transition.blockedMessage]);
        return true;
      }
      changeMap(transition.targetMap, transition.targetPos, transition.message);
      return true;
    }

    if (target.tile === "<") {
      const transition = DOORS[state.currentMap]?.[key];
      if (!transition) { return false; }
      changeMap(transition.targetMap, transition.targetPos, transition.message);
      return true;
    }

    return false;
  }

  facingTarget(state) {
    const next = tileAhead(state.player);
    return {
      x: next.x,
      y: next.y,
      tile: getTile(state.currentMap, next.x, next.y),
    };
  }

  // ─── Render ──────────────────────────────────────────────────────────────

  render(state) {
    const { ctx } = this;
    ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    this._frameTick += 1;

    const cam = this.camera(state);

    // Ground layer
    for (let y = cam.startY; y < cam.endY; y++) {
      for (let x = cam.startX; x < cam.endX; x++) {
        const tile = getTile(state.currentMap, x, y);
        const sx   = (x - cam.startX + cam.offsetX) * TILE_SIZE;
        const sy   = (y - cam.startY + cam.offsetY) * TILE_SIZE;
        this.drawTile(state.currentMap, tile, sx, sy, x, y);
      }
    }

    // Object layer — building stamps and decorations
    this.drawObjects(state, cam);

    // NPCs
    for (const [pos, npc] of Object.entries(state.npcs)) {
      const [nx, ny] = pos.split(",").map(Number);
      if (nx < cam.startX || nx >= cam.endX || ny < cam.startY || ny >= cam.endY) {
        continue;
      }
      const sx = (nx - cam.startX + cam.offsetX) * TILE_SIZE;
      const sy = (ny - cam.startY + cam.offsetY) * TILE_SIZE;
      this.drawPerson(sx, sy, npc.direction, npc.palette);

      // ! emote above trainer being triggered
      if (
        this._visionFlash &&
        this._visionFlash.npc === npc &&
        Math.floor(this._visionFlash.timer / 120) % 2 === 0
      ) {
        this.drawEmote(sx, sy);
      }

      // Vision cone debug dots (only if npc is trainer and not defeated)
      // (omitted for production — too noisy)
    }

    // Player
    const psx = (state.player.x - cam.startX + cam.offsetX) * TILE_SIZE;
    const psy = (state.player.y - cam.startY + cam.offsetY) * TILE_SIZE;
    this.drawPerson(psx, psy, state.player.direction, "player", state.player.stepFrame);

    if (!state.activeDialogue && !state.activeShop && !state.activeChoice && !this._visionFlash) {
      if (this._isFacingInteractable(state)) {
        this._drawInteractionPrompt(psx, psy);
      }
    }

    this.updateHudPanel(state);
    this.drawDialogueBox(state);
    this.drawStarterChoiceOverlay(state);
    this.drawShopOverlay(state);
    this._drawWhiteout(state);
    this._drawTransitionFade(state);
  }

  _drawWhiteout(state) {
    if (!state.whiteoutTimer || state.whiteoutTimer <= 0) { return; }
    state.whiteoutTimer -= 1;
    const alpha = Math.min(1, state.whiteoutTimer / 30);
    this.ctx.fillStyle = `rgba(255,255,255,${alpha.toFixed(2)})`;
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
  }

  _drawTransitionFade(state) {
    if (!state.transitionAlpha || state.transitionAlpha <= 0) { return; }
    state.transitionAlpha = Math.max(0, state.transitionAlpha - 0.04);
    this.ctx.fillStyle = `rgba(0,0,0,${state.transitionAlpha.toFixed(2)})`;
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
  }

  _isFacingInteractable(state) {
    const target = this.facingTarget(state);
    if (getNpcAt(state.currentMap, target.x, target.y)) { return true; }
    if (["D", ">", "<", "B", "P", "C", "V", "T", "X"].includes(target.tile)) { return true; }
    if ((MAPS[state.currentMap]?.objects ?? []).some(
      (o) => o.kind === "sign" && o.x === target.x && o.y === target.y
    )) { return true; }
    if (INTERACTION_TEXT[`${state.currentMap}:${target.tile}`]) { return true; }
    return false;
  }

  _drawInteractionPrompt(psx, psy) {
    if (Math.floor(this._frameTick / 30) % 2 === 1) { return; }
    const { ctx } = this;
    ctx.fillStyle = "#fff8c0";
    ctx.fillRect(psx + 3, psy - 12, 10, 8);
    ctx.strokeStyle = P.black;
    ctx.lineWidth = 1;
    ctx.strokeRect(psx + 3, psy - 12, 10, 8);
    ctx.fillStyle = P.black;
    ctx.font = "bold 6px monospace";
    ctx.fillText("E", psx + 6, psy - 6);
  }

  camera(state) {
    const mapW  = state.map[0]?.length ?? VIEWPORT_TILES_X;
    const mapH  = state.map.length ?? VIEWPORT_TILES_Y;

    const startX = clamp(
      state.player.x - Math.floor(VIEWPORT_TILES_X / 2),
      0,
      Math.max(0, mapW - VIEWPORT_TILES_X),
    );
    const startY = clamp(
      state.player.y - Math.floor(VIEWPORT_TILES_Y / 2),
      0,
      Math.max(0, mapH - VIEWPORT_TILES_Y),
    );
    // Offset for maps narrower/shorter than the viewport (centres them)
    const offsetX = mapW < VIEWPORT_TILES_X
      ? Math.floor((VIEWPORT_TILES_X - mapW) / 2) : 0;
    const offsetY = mapH < VIEWPORT_TILES_Y
      ? Math.floor((VIEWPORT_TILES_Y - mapH) / 2) : 0;

    return {
      startX,
      startY,
      endX: Math.min(mapW,  startX + VIEWPORT_TILES_X),
      endY: Math.min(mapH,  startY + VIEWPORT_TILES_Y),
      offsetX,
      offsetY,
    };
  }

  drawObjects(state, cam) {
    const mapCfg = MAPS[state.currentMap];
    if (!mapCfg?.objects?.length) { return; }
    const T = TILE_SIZE;

    for (const obj of mapCfg.objects) {
      const sx = (obj.x - cam.startX + cam.offsetX) * T;
      const sy = (obj.y - cam.startY + cam.offsetY) * T;

      if (obj.kind.startsWith("building_")) {
        const wide = obj.kind === "building_lab" ? 5 : obj.kind === "building_heal" ? 6 : obj.kind === "building_trial" ? 5 : 4;
        const tall = 4;
        if (
          obj.x + wide < cam.startX || obj.x > cam.endX ||
          obj.y + tall < cam.startY || obj.y > cam.endY
        ) {
          continue;
        }
        drawBuilding(this.ctx, sx, sy, obj.kind);

      } else if (obj.kind === "flower") {
        if (sx >= -T && sx <= this.canvas.width && sy >= -T && sy <= this.canvas.height) {
          this.drawFlower(sx, sy);
        }

      } else if (obj.kind === "sign") {
        if (sx >= -T && sx <= this.canvas.width && sy >= -T && sy <= this.canvas.height) {
          this._drawSignPost(sx, sy);
        }

      } else if (obj.kind === "bookshelf") {
        if (sx >= -T && sx <= this.canvas.width && sy >= -T && sy <= this.canvas.height) {
          this.drawIndoorFloor(sx, sy);
          const ctx = this.ctx;
          ctx.fillStyle = P.treeTrunk;
          ctx.fillRect(sx + 1, sy + 2, T - 2, T - 3);
          ctx.fillStyle = P.brickDk;
          ctx.fillRect(sx + 1, sy + 2, T - 2, 1);
          ctx.fillRect(sx + 1, sy + 11, T - 2, 1);
          const bookCols = ["#e04040","#4080e0","#40b060","#e0c040","#b040d0"];
          bookCols.forEach((col, i) => {
            ctx.fillStyle = col;
            ctx.fillRect(sx + 2 + i * 2, sy + 3, 1, 8);
          });
        }

      } else if (obj.kind === "pot_plant") {
        if (sx >= -T && sx <= this.canvas.width && sy >= -T && sy <= this.canvas.height) {
          this.drawIndoorFloor(sx, sy);
          const ctx = this.ctx;
          ctx.fillStyle = "#a06030";
          ctx.fillRect(sx + 4, sy + 10, 8, 4);
          ctx.fillRect(sx + 5, sy + 9, 6, 2);
          ctx.fillStyle = P.treeMid;
          ctx.fillRect(sx + 6, sy + 5, 4, 5);
          ctx.fillStyle = P.treeHi;
          ctx.fillRect(sx + 5, sy + 3, 6, 4);
          ctx.fillRect(sx + 7, sy + 1, 2, 4);
        }

      } else if (obj.kind === "table") {
        if (sx >= -T && sx <= this.canvas.width && sy >= -T && sy <= this.canvas.height) {
          this.drawIndoorFloor(sx, sy);
          const ctx = this.ctx;
          ctx.fillStyle = "#c89060";
          ctx.fillRect(sx + 1, sy + 4, T - 2, 5);
          ctx.fillStyle = "#a07040";
          ctx.fillRect(sx + 1, sy + 4, T - 2, 1);
          ctx.fillStyle = P.treeTrunk;
          ctx.fillRect(sx + 1, sy + 9, 2, 5);
          ctx.fillRect(sx + T - 3, sy + 9, 2, 5);
        }
      }
    }
  }

  _drawSignPost(sx, sy) {
    const { ctx } = this;
    const T = TILE_SIZE;
    this.drawGrassTile(sx, sy);
    ctx.fillStyle = P.signPost;
    ctx.fillRect(sx + 7, sy + 8, 2, 8);
    ctx.fillStyle = P.signBoard;
    ctx.fillRect(sx + 2, sy + 3, 12, 6);
    ctx.fillStyle = P.brickDk;
    ctx.fillRect(sx + 2, sy + 3, 12, 1);
    ctx.fillRect(sx + 2, sy + 8, 12, 1);
  }

  drawEmote(x, y) {
    const { ctx } = this;
    ctx.fillStyle = "#fff8c0";
    ctx.fillRect(x + 5, y - 10, 6, 8);
    ctx.strokeStyle = P.black;
    ctx.lineWidth = 1;
    ctx.strokeRect(x + 5, y - 10, 6, 8);
    ctx.fillStyle = P.black;
    ctx.font = "bold 7px monospace";
    ctx.fillText("!", x + 7, y - 9);
  }

  // ─── Tile drawing ──────────────────────────────────────────────────────

  drawTile(mapId, tile, sx, sy, gx = 0, gy = 0) {
    const { ctx } = this;
    const T = TILE_SIZE;
    const terrain = MAPS[mapId]?.terrain ?? "outdoor";
    const indoor  = terrain === "indoor";

    switch (tile) {
      case ".":
        if (indoor) {
          this.drawIndoorFloor(sx, sy);
        } else {
          this.drawGrassTile(sx, sy);
        }
        break;

      case "F":
        this.drawGrassTile(sx, sy);
        this.drawFlower(sx, sy);
        break;

      case "G": {
        const gPhase = Math.floor((this._frameTick + (gx + gy) % 4 * 8) / 30) % 2;
        const gShift = gPhase === 0 ? 0 : 1;
        ctx.fillStyle = P.grassDark;
        ctx.fillRect(sx, sy, T, T);
        ctx.fillStyle = P.grassMid;
        ctx.fillRect(sx + 1,  sy + 3 - gShift, 2, 9);
        ctx.fillRect(sx + 5,  sy + 1 - gShift, 2, 11);
        ctx.fillRect(sx + 9,  sy + 4 - gShift, 2, 8);
        ctx.fillRect(sx + 13, sy + 2 - gShift, 2, 10);
        ctx.fillStyle = P.grassLight;
        ctx.fillRect(sx + 2,  sy + 2 - gShift, 1, 3);
        ctx.fillRect(sx + 6,  sy     - gShift, 1, 3);
        ctx.fillRect(sx + 10, sy + 3 - gShift, 1, 3);
        ctx.fillRect(sx + 14, sy + 1 - gShift, 1, 3);
        break;
      }

      case "#":
        this.drawTreeTile(sx, sy);
        break;

      case "~": {
        const wPhase = Math.floor(this._frameTick / 24) % 2;
        ctx.fillStyle = P.water;
        ctx.fillRect(sx, sy, T, T);
        ctx.fillStyle = P.waterMid;
        if (wPhase === 0) {
          ctx.fillRect(sx + 1, sy + 3, 6, 2);
          ctx.fillRect(sx + 9, sy + 8, 5, 2);
        } else {
          ctx.fillRect(sx + 3, sy + 5, 6, 2);
          ctx.fillRect(sx + 1, sy + 10, 5, 2);
        }
        ctx.fillStyle = P.waterLight;
        ctx.fillRect(sx + 2 + wPhase * 2, sy + 4, 3, 1);
        ctx.fillRect(sx + 10,             sy + 9 + wPhase, 3, 1);
        break;
      }

      case "=":
        ctx.fillStyle = P.bridgeDk;
        ctx.fillRect(sx, sy, T, T);
        ctx.fillStyle = P.bridgeMid;
        ctx.fillRect(sx,     sy + 3, T, 2);
        ctx.fillRect(sx,     sy + 9, T, 2);
        ctx.fillStyle = P.bridgeLight;
        ctx.fillRect(sx + 3, sy + 1, 2, T - 2);
        ctx.fillRect(sx + 9, sy + 1, 2, T - 2);
        break;

      case "J":
        // Ledge — looks like a low step / cliff edge
        this.drawGrassTile(sx, sy);
        ctx.fillStyle = P.darkGreen;
        ctx.fillRect(sx, sy + 12, T, 4);
        ctx.fillStyle = P.midGreen;
        ctx.fillRect(sx, sy + 12, T, 2);
        ctx.fillStyle = P.black;
        ctx.fillRect(sx, sy + 14, T, 1);
        // small arrow hints
        ctx.fillStyle = P.lightGreen;
        ctx.fillRect(sx + 5,  sy + 13, 2, 2);
        ctx.fillRect(sx + 10, sy + 13, 2, 2);
        break;

      case "W":
        // Raw wall tile (under building stamp) — brick pattern background
        ctx.fillStyle = P.brickMid;
        ctx.fillRect(sx, sy, T, T);
        ctx.fillStyle = P.brickDk;
        ctx.fillRect(sx, sy, T, 1);
        break;

      case "D":
        // Raw door tile (under building stamp) — plain wall with door hint
        ctx.fillStyle = P.wallCream;
        ctx.fillRect(sx, sy, T, T);
        ctx.fillStyle = P.door;
        ctx.fillRect(sx + 5, sy + 2, 6, T - 2);
        ctx.fillStyle = P.doorLight;
        ctx.fillRect(sx + 6, sy + 3, 4, 5);
        break;

      case "S":
        this.drawGrassTile(sx, sy);
        ctx.fillStyle = P.signPost;
        ctx.fillRect(sx + 7, sy + 8, 2, 8);
        ctx.fillStyle = P.signBoard;
        ctx.fillRect(sx + 2, sy + 3, 12, 6);
        ctx.fillStyle = P.brickDk;
        ctx.fillRect(sx + 2, sy + 3, 12, 1);
        ctx.fillRect(sx + 2, sy + 8, 12, 1);
        break;

      case "N":
        if (indoor) { this.drawIndoorFloor(sx, sy); } else { this.drawGrassTile(sx, sy); }
        break;

      case "B":
        this.drawIndoorFloor(sx, sy);
        ctx.fillStyle = P.bedBlue;
        ctx.fillRect(sx + 2, sy + 4, 12, 8);
        ctx.fillStyle = P.bedLight;
        ctx.fillRect(sx + 3, sy + 5, 5, 4);
        ctx.fillStyle = P.palePaper;
        ctx.fillRect(sx + 3, sy + 5, 5, 2);
        break;

      case "V":
        this.drawIndoorFloor(sx, sy);
        ctx.fillStyle = "#202020";
        ctx.fillRect(sx + 2, sy + 4, 12, 8);
        ctx.fillStyle = "#1a3060";
        ctx.fillRect(sx + 3, sy + 5, 10, 5);
        ctx.fillStyle = "#88aacc";
        ctx.fillRect(sx + 4, sy + 6, 7, 3);
        break;

      case "C":
        this.drawIndoorFloor(sx, sy);
        ctx.fillStyle = P.consoleBlue;
        ctx.fillRect(sx + 3, sy + 5, 10, 6);
        ctx.fillStyle = "#d7efc2";
        ctx.fillRect(sx + 5, sy + 6, 6, 2);
        ctx.fillStyle = P.black;
        ctx.fillRect(sx + 5, sy + 9, 2, 1);
        ctx.fillRect(sx + 8, sy + 9, 2, 1);
        break;

      case ">":
        // North-exit tile — upward arrow
        this.drawGrassTile(sx, sy);
        ctx.fillStyle = P.lightGreen;
        ctx.fillRect(sx + 3, sy, 10, T);
        ctx.fillStyle = P.black;
        ctx.fillRect(sx + 7, sy + 7, 2, 6);
        ctx.fillRect(sx + 5, sy + 7, 6, 2);
        ctx.fillRect(sx + 6, sy + 5, 4, 1);
        ctx.fillRect(sx + 7, sy + 4, 2, 1);
        break;

      case "<":
        // South-return tile — downward arrow
        this.drawGrassTile(sx, sy);
        ctx.fillStyle = P.lightGreen;
        ctx.fillRect(sx + 3, sy, 10, T);
        ctx.fillStyle = P.black;
        ctx.fillRect(sx + 7, sy + 3, 2, 6);
        ctx.fillRect(sx + 5, sy + 7, 6, 2);
        ctx.fillRect(sx + 6, sy + 9, 4, 1);
        ctx.fillRect(sx + 7, sy + 10, 2, 1);
        break;

      case "T":
        ctx.fillStyle = "#404848";
        ctx.fillRect(sx, sy, T, T);
        ctx.fillStyle = "#788888";
        ctx.fillRect(sx + 3, sy + 1, 10, 12);
        ctx.fillStyle = P.black;
        ctx.fillRect(sx + 7, sy + 3, 2, 8);
        break;

      case "X":
        this.drawGrassTile(sx, sy);
        ctx.fillStyle = "#8b3322";
        ctx.fillRect(sx + 3, sy + 3, 10, 2);
        ctx.fillRect(sx + 5, sy + 5, 2, 8);
        ctx.fillRect(sx + 9, sy + 5, 2, 8);
        break;

      case "P":
        // PC Storage terminal
        this.drawIndoorFloor(sx, sy);
        ctx.fillStyle = "#304878";
        ctx.fillRect(sx + 2, sy + 3, 12, 8);
        ctx.fillStyle = "#6090c8";
        ctx.fillRect(sx + 3, sy + 4, 10, 5);
        ctx.fillStyle = "#a8d0f0";
        ctx.fillRect(sx + 4, sy + 5, 6, 2);
        ctx.fillStyle = "#4060a0";
        ctx.fillRect(sx + 4, sy + 9, 2, 1);
        ctx.fillRect(sx + 7, sy + 9, 2, 1);
        ctx.fillStyle = "#d7efc2";
        ctx.fillRect(sx + 6, sy + 11, 4, 2);
        break;

      default:
        if (indoor) { this.drawIndoorFloor(sx, sy); } else { this.drawGrassTile(sx, sy); }
        break;
    }
  }

  drawGrassTile(sx, sy) {
    const { ctx } = this;
    const T = TILE_SIZE;
    ctx.fillStyle = P.lightGreen;
    ctx.fillRect(sx, sy, T, T);
    ctx.fillStyle = P.pathDk;
    ctx.fillRect(sx + 2,  sy + 3, 2, 5);
    ctx.fillRect(sx + 11, sy + 7, 2, 4);
    ctx.fillRect(sx + 6,  sy + 11, 2, 3);
  }

  drawIndoorFloor(sx, sy) {
    const { ctx } = this;
    const T = TILE_SIZE;
    ctx.fillStyle = P.indoorFloor;
    ctx.fillRect(sx, sy, T, T);
    ctx.fillStyle = P.indoorLine;
    ctx.fillRect(sx, sy + T - 4, T, 1);
    ctx.fillRect(sx, sy + T - 8, T, 1);
  }

  drawTreeTile(sx, sy) {
    const { ctx } = this;
    const T = TILE_SIZE;
    ctx.fillStyle = P.treeDk;
    ctx.fillRect(sx, sy, T, T);
    ctx.fillStyle = P.treeMid;
    ctx.fillRect(sx + 3, sy + 1, 10, 4);
    ctx.fillStyle = P.treeHi;
    ctx.fillRect(sx + 1, sy + 4, 14, 4);
    ctx.fillStyle = "#60b035";
    ctx.fillRect(sx + 1, sy + 6, 14, 3);
    ctx.fillStyle = P.treeMid;
    ctx.fillRect(sx + 3, sy + 2, 4, 2);
    ctx.fillStyle = P.treeTrunk;
    ctx.fillRect(sx + 6, sy + 9, 4, 7);
    ctx.fillStyle = "#a07848";
    ctx.fillRect(sx + 7, sy + 9, 2, 5);
  }

  drawFlower(sx, sy) {
    const { ctx } = this;
    // Alternate pink/yellow per tile position for variety (cheap noise)
    const col = (sx / TILE_SIZE + sy / TILE_SIZE) % 2 === 0 ? P.flowerYel : P.flowerPink;
    ctx.fillStyle = col;
    ctx.fillRect(sx + 3, sy + 8, 2, 2);
    ctx.fillRect(sx + 5, sy + 6, 2, 2);
    ctx.fillRect(sx + 5, sy + 10, 2, 2);
    ctx.fillRect(sx + 7, sy + 8, 2, 2);
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(sx + 5, sy + 8, 2, 2);
  }

  // ─── Sprite drawing ───────────────────────────────────────────────────────

  drawPerson(x, y, direction, palette, stepFrame = 0) {
    const { ctx } = this;
    const palettes = {
      player:  { dark: "#2f395f", mid: "#4e69a2", light: "#d7efc2", hair: "#6e4e31", cap: "#c83e20" },
      elmwood: { dark: "#37563a", mid: "#82aa6e", light: "#e8ead7", hair: "#ede3a5", cap: "#82aa6e" },
      mira:    { dark: "#5d2b38", mid: "#b55c7b", light: "#f0d9bc", hair: "#7b4325", cap: "#b55c7b" },
      vella:   { dark: "#49385e", mid: "#8f78bc", light: "#f1e3d8", hair: "#d8bb8f", cap: "#8f78bc" },
      keeper:  { dark: "#5b4b2c", mid: "#9a8456", light: "#f0dfc6", hair: "#7a6743", cap: "#9a8456" },
      fen:     { dark: "#304d44", mid: "#5f947f", light: "#e7ead6", hair: "#b1c79a", cap: "#5f947f" },
    };
    const c   = palettes[palette] ?? palettes.player;
    const bob = stepFrame ? 1 : 0;

    // Shadow
    ctx.fillStyle = "rgba(0,0,0,0.18)";
    ctx.fillRect(x + 3, y + 14, 10, 2);

    // Cap
    ctx.fillStyle = c.cap;
    ctx.fillRect(x + 4, y + 1, 8, 3);
    ctx.fillRect(x + 3, y + 4, 10, 1);

    // Head / face
    ctx.fillStyle = c.hair;
    ctx.fillRect(x + 5, y + 2, 6, 2);
    ctx.fillStyle = c.light;
    ctx.fillRect(x + 4, y + 4, 8, 5);
    // eyes
    ctx.fillStyle = P.black;
    if (direction === "down" || direction === "up") {
      ctx.fillRect(x + 6, y + 6, 1, 2);
      ctx.fillRect(x + 9, y + 6, 1, 2);
    }

    // Body
    ctx.fillStyle = c.mid;
    ctx.fillRect(x + 3, y + 9, 10, 4);

    // Arms
    if (direction === "left") {
      ctx.fillStyle = c.mid;
      ctx.fillRect(x + 1, y + 9, 3, 4);
    } else if (direction === "right") {
      ctx.fillStyle = c.mid;
      ctx.fillRect(x + 12, y + 9, 3, 4);
    }

    // Legs
    ctx.fillStyle = c.dark;
    ctx.fillRect(x + 4,  y + 13, 3, 3 - bob);
    ctx.fillRect(x + 9,  y + 13, 3, 3 - (1 - bob));
  }

  // ─── HUD / Overlays ───────────────────────────────────────────────────────

  updateHudPanel(state) {
    if (this.hudLocation) {
      this.hudLocation.textContent = `Location: ${MAPS[state.currentMap]?.name ?? "?"}`;
    }
    const leader = state.party[0];
    if (this.hudParty) {
      this.hudParty.textContent = leader
        ? `Party: ${leader.name} Lv${leader.level}  HP ${leader.hp}/${leader.maxHp}`
        : "Party: None";
    }
    if (this.hudCoins) {
      this.hudCoins.textContent = `Coins: ${state.money}`;
    }
    if (this.hudPos) {
      this.hudPos.textContent = `Pos: ${state.player.x},${state.player.y}`;
    }
    if (this.hudTip) {
      this.hudTip.textContent = `Tip: ${state.prompt}`;
    }
  }

  drawDialogueBox(state) {
    if (!state.activeDialogue) { return; }
    const { ctx } = this;
    const W = this.canvas.width;
    const H = this.canvas.height;
    const bx = 8, by = H - 60, bw = W - 16, bh = 52;

    // GB-style border: outer black → white → black → content
    ctx.fillStyle = P.black;
    ctx.fillRect(bx, by, bw, bh);
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(bx + 1, by + 1, bw - 2, bh - 2);
    ctx.fillStyle = P.black;
    ctx.fillRect(bx + 2, by + 2, bw - 4, bh - 4);
    ctx.fillStyle = P.palePaper;
    ctx.fillRect(bx + 3, by + 3, bw - 6, bh - 6);

    ctx.fillStyle = P.black;
    ctx.font = "bold 8px 'Courier New', monospace";
    ctx.imageSmoothingEnabled = false;
    ctx.fillText(state.activeDialogue.speaker, bx + 8, by + 12);

    ctx.font = "8px 'Courier New', monospace";
    const lines = wrapText(getDialogueLine(state.activeDialogue), Math.floor((bw - 16) / 6));
    lines.slice(0, 3).forEach((line, i) => {
      ctx.fillText(line, bx + 8, by + 24 + i * 10);
    });

    if (state.activeDialogue.finished) {
      ctx.fillText("▼", bx + bw - 14, by + bh - 10);
    }
  }

  drawStarterChoiceOverlay(state) {
    if (state.activeChoice?.type !== "starter") { return; }
    const { ctx } = this;
    const W  = this.canvas.width;
    const px = 8, py = 8, pw = W - 16, ph = 140;

    gbPanel(ctx, px, py, pw, ph);

    ctx.fillStyle = P.black;
    ctx.font = "bold 8px 'Courier New', monospace";
    ctx.fillText("CHOOSE YOUR FIRST MORPH", px + 10, py + 14);

    STARTER_OPTIONS.forEach((key, index) => {
      const creature = SPECIES[key] ?? CREATURES[key];
      const name     = creature?.name ?? key;
      const type     = (creature?.types ?? [creature?.type]).filter(Boolean).join("/");
      const rowY   = py + 28 + index * 32;
      const sel    = state.activeChoice.selectedIndex === index;

      if (sel) {
        ctx.fillStyle = "#a8cc80";
        ctx.fillRect(px + 4, rowY - 2, pw - 8, 28);
        ctx.fillStyle = P.black;
        ctx.fillText("▶", px + 5, rowY + 10);
      }

      this.drawStarterIcon(key, px + 16, rowY + 2);

      ctx.fillStyle = P.black;
      ctx.font = "bold 8px 'Courier New', monospace";
      ctx.fillText(name, px + 38, rowY + 10);
      ctx.font = "7px 'Courier New', monospace";
      ctx.fillText(`[${type}]`, px + 38, rowY + 21);
    });

    ctx.fillStyle = P.black;
    ctx.font = "7px 'Courier New', monospace";
    ctx.fillText("[Enter] / [E] to confirm", px + 10, py + ph - 10);
  }

  drawShopOverlay(state) {
    const shop = state.activeShop;
    if (!shop) { return; }

    const { ctx } = this;
    const W = this.canvas.width;
    const H = this.canvas.height;

    ctx.fillStyle = "rgba(15,56,15,0.50)";
    ctx.fillRect(0, 0, W, H);

    const x = 12, y = 30, w = W - 24, h = 120;
    gbPanel(ctx, x, y, w, h);

    ctx.fillStyle = P.black;
    ctx.font = "bold 8px 'Courier New', monospace";
    ctx.fillText("KEEPER'S SHOP", x + 8, y + 12);
    ctx.font = "7px 'Courier New', monospace";

    // ── Root menu ─────────────────────────────────────────────────────────
    if (shop.mode === "root") {
      ctx.fillText("[Esc] leave", x + w - 72, y + 12);
      ["BUY", "SELL", "EXIT"].forEach((opt, i) => {
        const marker = shop.rootIndex === i ? "▶" : " ";
        ctx.fillStyle = P.black;
        ctx.fillText(`${marker} ${opt}`, x + 8, y + 38 + i * 18);
      });
      if (shop.flashTimer > 0 && shop.flashMessage) {
        ctx.fillText(shop.flashMessage, x + 8, y + h - 8);
      }
      return;
    }

    // ── Buy mode ──────────────────────────────────────────────────────────
    if (shop.mode === "buy") {
      ctx.fillText("[Esc] back", x + w - 68, y + 12);
      const PAGE    = 5;
      const ROW_H   = 14;
      const offset  = shop.scrollOffset ?? 0;
      const visible = shop.items.slice(offset, offset + PAGE);
      if (offset > 0) { ctx.fillText("▲", x + w - 16, y + 22); }
      visible.forEach((item, i) => {
        const qty    = state.items[item.id] ?? 0;
        const marker = shop.selectedIndex === offset + i ? "▶" : " ";
        ctx.fillStyle = P.black;
        ctx.fillText(`${marker} ${item.name}`, x + 8, y + 30 + i * ROW_H);
        ctx.fillText(`x${qty}`, x + 110, y + 30 + i * ROW_H);
        ctx.fillText(`${item.price}c`, x + w - 28, y + 30 + i * ROW_H);
      });
      ctx.fillStyle = P.black;
      ctx.fillText(`You have: ${state.money} coins`, x + 8, y + h - 20);
      if (offset + PAGE < shop.items.length) {
        ctx.fillText("▼ more", x + w - 48, y + h - 20);
      }
      if (shop.flashTimer > 0 && shop.flashMessage) {
        ctx.fillText(shop.flashMessage, x + 8, y + h - 8);
      }
      return;
    }

    // ── Sell mode ─────────────────────────────────────────────────────────
    if (shop.mode === "sell") {
      ctx.fillText("[Esc] back", x + w - 68, y + 12);
      const sellItems = shop.items.filter((it) => (state.items[it.id] ?? 0) > 0);
      const PAGE    = 5;
      const ROW_H   = 14;
      const offset  = shop.scrollOffset ?? 0;
      if (sellItems.length === 0) {
        ctx.fillStyle = P.black;
        ctx.fillText("Nothing to sell.", x + 8, y + 50);
      } else {
        const visible = sellItems.slice(offset, offset + PAGE);
        if (offset > 0) { ctx.fillText("▲", x + w - 16, y + 22); }
        visible.forEach((item, i) => {
          const qty       = state.items[item.id] ?? 0;
          const sellPrice = Math.floor(item.price / 2);
          const marker    = shop.selectedIndex === offset + i ? "▶" : " ";
          ctx.fillStyle = P.black;
          ctx.fillText(`${marker} ${item.name}`, x + 8, y + 30 + i * ROW_H);
          ctx.fillText(`x${qty}`, x + 110, y + 30 + i * ROW_H);
          ctx.fillText(`${sellPrice}c`, x + w - 28, y + 30 + i * ROW_H);
        });
        if (offset + PAGE < sellItems.length) {
          ctx.fillText("▼ more", x + w - 48, y + h - 20);
        }
      }
      ctx.fillStyle = P.black;
      ctx.fillText(`You have: ${state.money} coins`, x + 8, y + h - 20);
      if (shop.flashTimer > 0 && shop.flashMessage) {
        ctx.fillText(shop.flashMessage, x + 8, y + h - 8);
      }
    }
  }

  drawStarterIcon(sprite, x, y) {
    const { ctx } = this;
    ctx.fillStyle = "#c7d2a0";
    ctx.fillRect(x, y, 16, 16);
    ctx.strokeStyle = P.black;
    ctx.lineWidth = 1;
    ctx.strokeRect(x, y, 16, 16);

    if (sprite === "spriglet") {
      ctx.fillStyle = P.midGreen;
      ctx.fillRect(x + 4, y + 5, 8, 7);
      ctx.fillStyle = P.green;
      ctx.fillRect(x + 2, y + 2, 5, 5);
      ctx.fillRect(x + 9, y + 2, 5, 5);
      ctx.fillStyle = P.palePaper;
      ctx.fillRect(x + 6, y + 7, 1, 1);
      ctx.fillRect(x + 9, y + 7, 1, 1);
    } else if (sprite === "cindlet") {
      ctx.fillStyle = "#7a5a20";
      ctx.fillRect(x + 4, y + 5, 8, 7);
      ctx.fillStyle = "#d9be42";
      ctx.fillRect(x + 2, y + 2, 3, 5);
      ctx.fillRect(x + 11, y + 2, 3, 5);
      ctx.fillStyle = "#f4e8a3";
      ctx.fillRect(x + 6, y + 7, 1, 1);
      ctx.fillRect(x + 9, y + 7, 1, 1);
    } else {
      ctx.fillStyle = "#4f6880";
      ctx.fillRect(x + 3, y + 6, 10, 6);
      ctx.fillStyle = "#86b8d7";
      ctx.fillRect(x + 2, y + 4, 12, 7);
      ctx.fillRect(x + 5, y + 2, 6, 3);
      ctx.fillStyle = "#d6eef4";
      ctx.fillRect(x + 6, y + 7, 1, 1);
      ctx.fillRect(x + 9, y + 7, 1, 1);
    }
  }
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function gbPanel(ctx, x, y, w, h) {
  ctx.fillStyle = "#0f380f";
  ctx.fillRect(x, y, w, h);
  ctx.fillStyle = "#ffffff";
  ctx.fillRect(x + 1, y + 1, w - 2, h - 2);
  ctx.fillStyle = "#0f380f";
  ctx.fillRect(x + 2, y + 2, w - 4, h - 4);
  ctx.fillStyle = "#d7efc2";
  ctx.fillRect(x + 3, y + 3, w - 6, h - 6);
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function oppositeDirection(dir) {
  switch (dir) {
    case "up":    return "down";
    case "down":  return "up";
    case "left":  return "right";
    case "right": return "left";
    default:      return "down";
  }
}

function wrapText(text, maxChars) {
  const words = text.split(" ");
  const lines = [];
  let current = "";
  for (const word of words) {
    const next = current ? `${current} ${word}` : word;
    if (next.length > maxChars) {
      if (current) { lines.push(current); }
      current = word;
    } else {
      current = next;
    }
  }
  if (current) { lines.push(current); }
  return lines;
}

function interactionSpeaker(tile) {
  switch (tile) {
    case "S":  return "SIGN";
    case "T":  return "TRIAL GATE";
    case "X":  return "ROADBLOCK";
    case "C":  return "CONSOLE";
    case "V":  return "TV";
    case "B":  return "BED";
    default:   return "NOTICE";
  }
}
