// Pause screen — main menu + sub-screens: Party, Bag, Dex, Trainer Card, Options, PC Storage.
// Exports: PauseScreen
import audio from "../engine/audio.js?v=20260429-19";
import { StorageScreen } from "./StorageScreen.js?v=20260429-19";

const MENU_ITEMS = [
  "RESUME",
  "PARTY",
  "BAG",
  "DEX",
  "TRAINER CARD",
  "OPTIONS",
  "PC STORAGE",
  "SAVE GAME",
  "LOAD SAVE",
  "NEW GAME",
];

const OPTIONS_DEFS = [
  { key: "textSpeed",    label: "Text Speed",   values: ["Slow", "Normal", "Fast"] },
  { key: "battleAnims",  label: "Battle Anims", values: ["Off", "On"] },
  { key: "windowFrame",  label: "Window Frame", values: ["1", "2", "3"] },
  { key: "confirmSave",  label: "Confirm Save", values: ["Off", "On"] },
  // Audio section
  { key: "audioMuted",   label: "Mute All",     values: ["Off", "On"],   audio: true },
  { key: "audioMaster",  label: "Master Vol",   volume: true,            audio: true },
  { key: "audioBgm",     label: "Music Vol",    volume: true,            audio: true },
  { key: "audioSfx",     label: "SFX Vol",      volume: true,            audio: true },
];

export class PauseScreen {
  constructor(canvas, ctx) {
    this.canvas   = canvas;
    this.ctx      = ctx;
    this._storage = new StorageScreen(canvas, ctx);
  }

  // ─── Update ──────────────────────────────────────────────────────────────

  update(state, input, delta, actions) {
    const ps = state.pauseMenu;
    if (!ps) { return; }

    if (ps.flashTimer > 0) { ps.flashTimer -= delta; }

    if (ps.subScreen === "party")   { this.updateParty(state, input, ps); return; }
    if (ps.subScreen === "bag")     { this.updateBag(state, input, ps, actions); return; }
    if (ps.subScreen === "dex")     { this.updateDex(state, input, ps); return; }
    if (ps.subScreen === "card")    { this.updateCard(input, ps); return; }
    if (ps.subScreen === "options") { this.updateOptions(state, input, ps); return; }
    if (ps.subScreen === "storage") { this._storage.update(state, input, ps); return; }

    if (ps.confirmNewGame) {
      if (input.wasPressed("arrowleft", "a"))      { ps.confirmIndex = 0; }
      else if (input.wasPressed("arrowright", "d")) { ps.confirmIndex = 1; }
      else if (input.wasPressed("escape", "backspace")) { ps.confirmNewGame = false; }
      else if (input.wasPressed("e", " ", "enter")) {
        if (ps.confirmIndex === 0) { actions.newGame(); }
        else                        { ps.confirmNewGame = false; }
      }
      return;
    }

    if (input.wasPressed("arrowup", "w")) {
      ps.selectedIndex = (ps.selectedIndex + MENU_ITEMS.length - 1) % MENU_ITEMS.length;
      audio.playSfx("ui_move");
    } else if (input.wasPressed("arrowdown", "s")) {
      ps.selectedIndex = (ps.selectedIndex + 1) % MENU_ITEMS.length;
      audio.playSfx("ui_move");
    } else if (input.wasPressed("escape", "backspace")) {
      audio.playSfx("menu_back");
      actions.resume();
    } else if (input.wasPressed("e", " ", "enter")) {
      audio.playSfx("menu_confirm");
      const choice = MENU_ITEMS[ps.selectedIndex];
      if (choice === "RESUME") {
        actions.resume();
      } else if (choice === "PARTY") {
        ps.subScreen  = "party";
        ps.partyIndex = 0;
        ps.partyMode  = "browse";
        ps.swapFrom   = null;
      } else if (choice === "BAG") {
        ps.subScreen = "bag";
        ps.bagTab    = 0;
        ps.bagIndex  = 0;
      } else if (choice === "DEX") {
        ps.subScreen = "dex";
        ps.dexIndex  = 0;
      } else if (choice === "TRAINER CARD") {
        ps.subScreen = "card";
      } else if (choice === "OPTIONS") {
        ps.subScreen = "options";
        ps.optIndex  = 0;
      } else if (choice === "PC STORAGE") {
        ps.subScreen    = "storage";
        ps.storageState = {
          mode:       "boxes",
          boxIndex:   0,
          slotIndex:  0,
          partyIdx:   0,
          held:       null,
        };
      } else if (choice === "SAVE GAME") {
        actions.saveGame();
        ps.flashMessage = "Game saved!";
        ps.flashTimer   = 1800;
      } else if (choice === "LOAD SAVE") {
        const loaded = actions.loadSave();
        if (loaded) { actions.resume(); }
        else        { ps.flashMessage = "No save found."; ps.flashTimer = 1800; }
      } else if (choice === "NEW GAME") {
        ps.confirmNewGame = true;
        ps.confirmIndex   = 1;
      }
    }
  }

  updateParty(state, input, ps) {
    if (input.wasPressed("escape", "backspace")) {
      audio.playSfx("menu_back");
      if (ps.partyMode === "swap") { ps.partyMode = "browse"; ps.swapFrom = null; }
      else                          { ps.subScreen = null; }
      return;
    }
    const partyLen = state.party.length;
    if (partyLen === 0) { return; }
    if (input.wasPressed("arrowup", "w")) {
      ps.partyIndex = (ps.partyIndex + partyLen - 1) % partyLen;
      audio.playSfx("ui_move");
    } else if (input.wasPressed("arrowdown", "s")) {
      ps.partyIndex = (ps.partyIndex + 1) % partyLen;
      audio.playSfx("ui_move");
    } else if (input.wasPressed("e", " ", "enter")) {
      audio.playSfx("menu_confirm");
      if (ps.partyMode === "browse") {
        ps.partyMode = "swap";
        ps.swapFrom  = ps.partyIndex;
      } else if (ps.partyMode === "swap") {
        const a = ps.swapFrom, b = ps.partyIndex;
        if (a !== b) {
          const temp = state.party[a];
          state.party[a] = state.party[b];
          state.party[b] = temp;
        }
        ps.partyMode = "browse";
        ps.swapFrom  = null;
      }
    }
  }

  updateBag(state, input, ps, actions) {
    if (input.wasPressed("escape", "backspace")) {
      if (ps.bagMode === "tm_target") {
        ps.bagMode = null; audio.playSfx("menu_back"); return;
      }
      audio.playSfx("menu_back"); ps.subScreen = null; return;
    }

    // TM target selection sub-mode
    if (ps.bagMode === "tm_target") {
      const partyLen = state.party.length;
      if (partyLen === 0) { ps.bagMode = null; return; }
      if (input.wasPressed("arrowup", "w")) {
        ps.tmTargetIndex = Math.max(0, (ps.tmTargetIndex ?? 0) - 1);
        audio.playSfx("ui_move");
      } else if (input.wasPressed("arrowdown", "s")) {
        ps.tmTargetIndex = Math.min(partyLen - 1, (ps.tmTargetIndex ?? 0) + 1);
        audio.playSfx("ui_move");
      } else if (input.wasPressed("e", " ", "enter")) {
        audio.playSfx("menu_confirm");
        const tmItem  = _getBagItems(state, 3)[ps.bagIndex];
        const morph   = state.party[ps.tmTargetIndex ?? 0];
        const moveId  = TM_MOVES[tmItem?.id];
        const move    = (window._tiamatCreatures?.MOVES)?.[moveId];
        if (!morph || !move || !tmItem) { ps.bagMode = null; return; }
        // Compatibility check against species catalogue.
        const species = window._tiamatCreatures?.SPECIES?.[morph.speciesId ?? morph.id];
        if (species?.compatibleTMs && !species.compatibleTMs.includes(tmItem.id)) {
          ps.flashMessage = `${morph.name} can't learn this TM.`;
          ps.flashTimer   = 2000; ps.bagMode = null; return;
        }
        if (morph.moves.find((m) => m.id === moveId || m.name === move.name)) {
          ps.flashMessage = `${morph.name} already knows it!`;
          ps.flashTimer   = 1800; ps.bagMode = null; return;
        }
        if (morph.moves.length < 4) {
          morph.moves.push({ ...move });
          state.items[tmItem.id] = Math.max(0, (state.items[tmItem.id] ?? 1) - 1);
          ps.flashMessage = `${morph.name} learned ${move.name}!`;
          ps.flashTimer   = 1800; ps.bagMode = null;
          actions.saveGame();
        } else if (actions.teachMove) {
          // Consume TM and open move-replace prompt (closes pause menu).
          state.items[tmItem.id] = Math.max(0, (state.items[tmItem.id] ?? 1) - 1);
          ps.bagMode = null;
          actions.teachMove(morph, { ...move });
        } else {
          ps.flashMessage = "Move slots full — use PC to manage.";
          ps.flashTimer   = 2200; ps.bagMode = null;
        }
      }
      return;
    }

    const TAB_COUNT = 4;
    if (input.wasPressed("arrowleft", "a")) {
      ps.bagTab   = (ps.bagTab + TAB_COUNT - 1) % TAB_COUNT;
      ps.bagIndex = 0;
      audio.playSfx("ui_move");
    } else if (input.wasPressed("arrowright", "d")) {
      ps.bagTab   = (ps.bagTab + 1) % TAB_COUNT;
      ps.bagIndex = 0;
      audio.playSfx("ui_move");
    }
    const bagItems = _getBagItems(state, ps.bagTab);
    if (input.wasPressed("arrowup", "w")) {
      ps.bagIndex = Math.max(0, ps.bagIndex - 1);
      audio.playSfx("ui_move");
    } else if (input.wasPressed("arrowdown", "s")) {
      ps.bagIndex = Math.min(bagItems.length - 1, (ps.bagIndex ?? 0) + 1);
      audio.playSfx("ui_move");
    } else if (input.wasPressed("e", " ", "enter")) {
      audio.playSfx("menu_confirm");
      const item = bagItems[ps.bagIndex];
      if (!item) { return; }
      // TM tab — open party target picker
      if (ps.bagTab === 3) {
        if ((state.items[item.id] ?? 0) <= 0) {
          ps.flashMessage = "No TMs left."; ps.flashTimer = 1800; return;
        }
        ps.bagMode = "tm_target"; ps.tmTargetIndex = 0; return;
      }
      const healItems = { potion: 20, super_potion: 50, hyper_potion: 200 };
      if (healItems[item.id] !== undefined) {
        const leader = state.party[0];
        if (leader && (state.items[item.id] ?? 0) > 0 && leader.hp < leader.maxHp) {
          const healed = Math.min(healItems[item.id], leader.maxHp - leader.hp);
          leader.hp = Math.min(leader.maxHp, leader.hp + healItems[item.id]);
          state.items[item.id] -= 1;
          audio.playSfx("heal");
          ps.flashMessage = `${leader.name} recovered ${healed} HP!`;
          ps.flashTimer   = 1800;
          actions.saveGame();
        } else {
          ps.flashMessage = "Can't use that here.";
          ps.flashTimer   = 1800;
        }
      } else {
        ps.flashMessage = "Can't use that here.";
        ps.flashTimer   = 1800;
      }
    }
  }

  updateDex(state, input, ps) {
    if (input.wasPressed("escape", "backspace")) { audio.playSfx("menu_back"); ps.subScreen = null; return; }
    const entries = _getDexEntries(state);
    if (input.wasPressed("arrowup", "w")) {
      ps.dexIndex = Math.max(0, ps.dexIndex - 1);
      audio.playSfx("ui_move");
    } else if (input.wasPressed("arrowdown", "s")) {
      ps.dexIndex = Math.min(entries.length - 1, ps.dexIndex + 1);
      audio.playSfx("ui_move");
    }
  }

  updateCard(input, ps) {
    if (input.wasPressed("escape", "backspace", "e", " ", "enter")) {
      audio.playSfx("menu_back");
      ps.subScreen = null;
    }
  }

  updateOptions(state, input, ps) {
    if (input.wasPressed("escape", "backspace")) {
      audio.playSfx("menu_back");
      ps.subScreen = null;
      return;
    }
    if (input.wasPressed("arrowup", "w")) {
      ps.optIndex = (ps.optIndex + OPTIONS_DEFS.length - 1) % OPTIONS_DEFS.length;
      audio.playSfx("ui_move");
    } else if (input.wasPressed("arrowdown", "s")) {
      ps.optIndex = (ps.optIndex + 1) % OPTIONS_DEFS.length;
      audio.playSfx("ui_move");
    } else if (input.wasPressed("arrowleft", "a") || input.wasPressed("arrowright", "d")) {
      audio.playSfx("ui_move");
      const opt = OPTIONS_DEFS[ps.optIndex];
      if (!state.settings) { state.settings = {}; }
      if (opt.volume) {
        const cur = typeof state.settings[opt.key] === "number" ? state.settings[opt.key] : 0.8;
        const dir = input.wasPressed("arrowleft", "a") ? -1 : 1;
        state.settings[opt.key] = Math.max(0, Math.min(1, Math.round((cur + dir * 0.1) * 10) / 10));
        audio.applySettings(state.settings);
      } else {
        const settings = state.settings ?? {};
        let curVal = settings[opt.key];
        let curIdx = opt.values.indexOf(String(curVal));
        if (curIdx < 0) { curIdx = opt.values.length - 1; }
        const dir = input.wasPressed("arrowleft", "a") ? -1 : 1;
        const nextIdx = (curIdx + dir + opt.values.length) % opt.values.length;
        const raw = opt.values[nextIdx];
        if (raw === "On" || raw === "Off") {
          state.settings[opt.key] = raw === "On";
        } else if (!isNaN(Number(raw))) {
          state.settings[opt.key] = Number(raw);
        } else {
          state.settings[opt.key] = raw.toLowerCase();
        }
        if (opt.audio) { audio.applySettings(state.settings); }
      }
    }
  }

  // ─── Render ───────────────────────────────────────────────────────────────

  render(state) {
    const ps = state.pauseMenu;
    if (!ps) { return; }

    const { ctx } = this;
    const W = this.canvas.width;
    const H = this.canvas.height;

    ctx.fillStyle = "rgba(15,56,15,0.55)";
    ctx.fillRect(0, 0, W, H);

    if (ps.subScreen === "party")   { this.renderParty(state, ps); return; }
    if (ps.subScreen === "bag")     { this.renderBag(state, ps); return; }
    if (ps.subScreen === "dex")     { this.renderDex(state, ps); return; }
    if (ps.subScreen === "card")    { this.renderCard(state, ps); return; }
    if (ps.subScreen === "options") { this.renderOptions(state, ps); return; }
    if (ps.subScreen === "storage") { this._storage.render(state, ps); return; }

    if (ps.confirmNewGame) { this.renderConfirm(ps); }
    else                    { this.renderMenu(state, ps); }
  }

  renderMenu(state, ps) {
    const { ctx } = this;
    const W = this.canvas.width;
    const H = this.canvas.height;
    const x = 6;
    const w = 126;
    const h = H - 12;
    const y = 6;

    _gbPanel(ctx, x, y, w, h);

    ctx.fillStyle = "#0f380f";
    ctx.font = "bold 8px 'Courier New', monospace";
    ctx.textBaseline = "top";
    ctx.fillText("MENU", x + 8, y + 6);

    ctx.font = "7px 'Courier New', monospace";
    MENU_ITEMS.forEach((item, i) => {
      const marker = ps.selectedIndex === i ? "▶" : " ";
      ctx.fillStyle = "#0f380f";
      ctx.fillText(`${marker} ${item}`, x + 8, y + 22 + i * 17);
    });

    if (ps.flashTimer > 0 && ps.flashMessage) {
      ctx.fillStyle = "#c83e20";
      ctx.font = "6px 'Courier New', monospace";
      ctx.fillText(ps.flashMessage, x + 8, y + h - 10);
    }

    // Quick party summary on right side.
    if (state.party.length > 0) {
      const px = x + w + 6;
      const pw = W - px - 6;
      if (pw > 30) {
        _gbPanel(ctx, px, y, pw, h);
        ctx.fillStyle = "#0f380f";
        ctx.font = "bold 7px 'Courier New', monospace";
        ctx.fillText("TEAM", px + 6, y + 6);
        ctx.font = "7px 'Courier New', monospace";
        state.party.slice(0, 6).forEach((c, i) => {
          const hpRatio = c.hp / c.maxHp;
          ctx.fillStyle = "#0f380f";
          ctx.fillText(`${c.name.slice(0, 6)} L${c.level}`, px + 4, y + 20 + i * 28);
          ctx.fillRect(px + 4, y + 26 + i * 28, pw - 8, 5);
          ctx.fillStyle = hpRatio > 0.5 ? "#306230" : hpRatio > 0.2 ? "#9c7a3c" : "#7f3326";
          ctx.fillRect(px + 5, y + 27 + i * 28, Math.max(1, Math.floor((pw - 10) * hpRatio)), 3);
          ctx.fillStyle = "#0f380f";
          ctx.font = "6px 'Courier New', monospace";
          ctx.fillText(`${c.hp}/${c.maxHp}`, px + 4, y + 34 + i * 28);
          ctx.font = "7px 'Courier New', monospace";
        });
      }
    }
  }

  renderParty(state, ps) {
    const { ctx } = this;
    const W = this.canvas.width;
    const H = this.canvas.height;
    const x = 8, y = 8, w = W - 16, h = H - 16;

    _gbPanel(ctx, x, y, w, h);

    ctx.fillStyle = "#0f380f";
    ctx.font = "bold 8px 'Courier New', monospace";
    ctx.textBaseline = "top";
    ctx.fillText("PARTY", x + 8, y + 6);
    ctx.font = "7px 'Courier New', monospace";
    ctx.fillText("[Esc] back", x + w - 76, y + 6);

    if (ps.partyMode === "swap") {
      ctx.fillStyle = "#c83e20";
      ctx.fillText("Swap with... (Esc=cancel)", x + 8, y + 18);
    }

    if (state.party.length === 0) {
      ctx.fillStyle = "#0f380f";
      ctx.fillText("No Morphs in party.", x + 8, y + 34);
      return;
    }

    state.party.forEach((c, i) => {
      const rowY      = y + 24 + i * 26;
      const selected  = ps.partyIndex === i;
      const isSwapFrom = ps.swapFrom === i;

      if (selected) {
        ctx.fillStyle = isSwapFrom ? "#e8d060" : "#a8cc80";
        ctx.fillRect(x + 4, rowY - 1, w - 8, 22);
      }

      ctx.fillStyle = "#0f380f";
      ctx.font = "bold 7px 'Courier New', monospace";
      ctx.fillText(`${selected ? "▶" : " "} ${c.name}`, x + 5, rowY + 2);
      ctx.font = "7px 'Courier New', monospace";
      ctx.fillText(`Lv${c.level}`, x + 78, rowY + 2);

      if (c.status) {
        ctx.fillStyle = "#8040c0";
        ctx.fillText(`[${c.status.slice(0, 3).toUpperCase()}]`, x + 98, rowY + 2);
      }

      const hpRatio = c.hp / c.maxHp;
      ctx.fillStyle = "#0f380f";
      ctx.fillRect(x + 5, rowY + 12, 100, 6);
      ctx.fillStyle = hpRatio > 0.5 ? "#306230" : hpRatio > 0.2 ? "#9c7a3c" : "#7f3326";
      ctx.fillRect(x + 6, rowY + 13, Math.max(1, Math.floor(98 * hpRatio)), 4);
      ctx.fillStyle = "#0f380f";
      ctx.font = "6px 'Courier New', monospace";
      ctx.fillText(`${c.hp}/${c.maxHp}`, x + 108, rowY + 14);

      c.moves.forEach((mv, mi) => {
        ctx.fillText(mv.name, x + 160 + (mi % 2) * 68, rowY + 2 + Math.floor(mi / 2) * 9);
      });
      ctx.font = "7px 'Courier New', monospace";
    });
  }

  renderBag(state, ps) {
    const { ctx } = this;
    const W = this.canvas.width;
    const H = this.canvas.height;
    const x = 8, y = 8, w = W - 16, h = H - 16;

    _gbPanel(ctx, x, y, w, h);

    // TM target-pick sub-screen
    if (ps.bagMode === "tm_target") {
      ctx.fillStyle = "#0f380f";
      ctx.font = "bold 8px 'Courier New', monospace";
      ctx.textBaseline = "top";
      ctx.fillText("TEACH TO...", x + 8, y + 6);
      ctx.font = "7px 'Courier New', monospace";
      ctx.fillText("[Esc] cancel", x + w - 82, y + 6);
      state.party.forEach((c, i) => {
        const sel = (ps.tmTargetIndex ?? 0) === i;
        if (sel) { ctx.fillStyle = "#a8cc80"; ctx.fillRect(x + 4, y + 22 + i * 20, w - 8, 16); }
        ctx.fillStyle = "#0f380f";
        ctx.font = "7px 'Courier New', monospace";
        ctx.fillText(`${sel ? "▶" : " "} ${c.name}  Lv${c.level}`, x + 6, y + 25 + i * 20);
        ctx.font = "6px 'Courier New', monospace";
        ctx.fillText(c.moves.map((m) => m.name).join(", "), x + 14, y + 33 + i * 20);
      });
      return;
    }

    const TAB_LABELS = ["ITEMS", "CAPS", "KEY", "TMs"];
    ctx.textBaseline = "top";
    TAB_LABELS.forEach((lbl, i) => {
      ctx.fillStyle = ps.bagTab === i ? "#c83e20" : "#0f380f";
      ctx.font = "bold 7px 'Courier New', monospace";
      ctx.fillText(lbl, x + 8 + i * 48, y + 6);
    });
    ctx.fillStyle = "#0f380f";
    ctx.font = "7px 'Courier New', monospace";
    ctx.fillText("[Esc] back  [A/D] tab", x + w - 134, y + 6);

    const items = _getBagItems(state, ps.bagTab);
    if (items.length === 0) {
      ctx.fillStyle = "#0f380f";
      ctx.fillText("(empty)", x + 8, y + 24);
    } else {
      items.forEach((item, i) => {
        const marker = ps.bagIndex === i ? "▶" : " ";
        ctx.fillStyle = "#0f380f";
        ctx.fillText(`${marker} ${item.label}  x${item.qty}`, x + 8, y + 22 + i * 13);
      });
    }

    if (ps.bagTab === 3 && items.length > 0) {
      ctx.fillStyle = "rgba(15,56,15,0.55)";
      ctx.font = "6px 'Courier New', monospace";
      ctx.fillText("[E] to use on a Morph", x + 8, y + h - 20);
    }

    if (ps.flashTimer > 0 && ps.flashMessage) {
      ctx.fillStyle = "#c83e20";
      ctx.font = "6px 'Courier New', monospace";
      ctx.fillText(ps.flashMessage, x + 8, y + h - 10);
    }
  }

  renderDex(state, ps) {
    const { ctx } = this;
    const W = this.canvas.width;
    const H = this.canvas.height;
    const x = 8, y = 8, w = W - 16, h = H - 16;

    _gbPanel(ctx, x, y, w, h);

    const dex     = state.dex ?? { seen: new Set(), caught: new Set() };
    const entries = _getDexEntries(state);

    ctx.fillStyle = "#0f380f";
    ctx.font = "bold 8px 'Courier New', monospace";
    ctx.textBaseline = "top";
    ctx.fillText("MORPH DEX", x + 8, y + 6);
    ctx.font = "7px 'Courier New', monospace";
    ctx.fillText(`Seen:${dex.seen?.size ?? 0} Caught:${dex.caught?.size ?? 0}`, x + 100, y + 6);
    ctx.fillText("[Esc] back", x + w - 76, y + 6);

    const visible = entries.slice(Math.max(0, ps.dexIndex - 4), ps.dexIndex + 9);
    visible.forEach((entry, i) => {
      const globalIdx = Math.max(0, ps.dexIndex - 4) + i;
      const marker    = globalIdx === ps.dexIndex ? "▶" : " ";
      const seen      = dex.seen?.has(entry.id);
      const caught    = dex.caught?.has(entry.id);

      ctx.fillStyle = "#0f380f";
      const label = seen ? entry.name : "???";
      ctx.font = caught ? "bold 7px 'Courier New', monospace" : "7px 'Courier New', monospace";
      ctx.fillText(`${marker} #${String(globalIdx + 1).padStart(3, "0")} ${label}`, x + 6, y + 22 + i * 13);
      if (seen) {
        const typeStr = (entry.types ?? [entry.type]).join("/");
        ctx.font = "7px 'Courier New', monospace";
        ctx.fillText(typeStr, x + w - 56, y + 22 + i * 13);
        ctx.fillText(caught ? "★" : "·", x + w - 12, y + 22 + i * 13);
      }
    });
  }

  renderCard(state, ps) {
    const { ctx } = this;
    const W = this.canvas.width;
    const H = this.canvas.height;
    const x = 20, y = 16, w = W - 40, h = H - 32;

    _gbPanel(ctx, x, y, w, h);

    ctx.fillStyle = "#0f380f";
    ctx.font = "bold 8px 'Courier New', monospace";
    ctx.textBaseline = "top";
    ctx.fillText("TRAINER CARD", x + 8, y + 6);
    ctx.font = "7px 'Courier New', monospace";
    ctx.fillText("[Any] back", x + w - 72, y + 6);

    const stats = state.stats ?? {};
    const money = state.money ?? 0;

    const rows = [
      ["Name",         "Tamer"],
      ["Money",        `$${money.toLocaleString()}`],
      ["Steps",        String(stats.steps ?? 0)],
      ["Battles Won",  String(stats.battlesWon ?? 0)],
      ["Captures",     String(stats.captures ?? 0)],
      ["Party Size",   String(state.party?.length ?? 0)],
    ];

    rows.forEach(([label, value], i) => {
      ctx.fillStyle = "#0f380f";
      ctx.fillText(label, x + 8, y + 24 + i * 18);
      ctx.fillText(value, x + w - 8 - value.length * 6, y + 24 + i * 18);
      // divider
      ctx.fillStyle = "rgba(15,56,15,0.25)";
      ctx.fillRect(x + 6, y + 34 + i * 18, w - 12, 1);
    });

    // Decorative badge area
    ctx.fillStyle = "#0f380f";
    ctx.font = "bold 7px 'Courier New', monospace";
    ctx.fillText("BADGES", x + 8, y + h - 24);
    ctx.font = "7px 'Courier New', monospace";
    const badges = state.flags?.badges ?? [];
    if (badges.length === 0) {
      ctx.fillText("— none yet —", x + 60, y + h - 24);
    } else {
      badges.slice(0, 8).forEach((b, i) => {
        ctx.fillText("★", x + 60 + i * 12, y + h - 24);
      });
    }
  }

  renderOptions(state, ps) {
    const { ctx } = this;
    const W = this.canvas.width;
    const H = this.canvas.height;
    const x = 20, y = 20, w = W - 40, h = H - 40;
    const ROW_H = 16;

    _gbPanel(ctx, x, y, w, h);

    ctx.fillStyle = "#0f380f";
    ctx.font = "bold 8px 'Courier New', monospace";
    ctx.textBaseline = "top";
    ctx.fillText("OPTIONS", x + 8, y + 6);
    ctx.font = "7px 'Courier New', monospace";
    ctx.fillText("[Esc] back", x + w - 72, y + 6);

    const settings = state.settings ?? {};

    OPTIONS_DEFS.forEach((opt, i) => {
      const sel = ps.optIndex === i;
      const raw = settings[opt.key];

      // Divider line before first audio section entry.
      if (opt.audio && !OPTIONS_DEFS[i - 1]?.audio) {
        ctx.fillStyle = "rgba(15,56,15,0.3)";
        ctx.fillRect(x + 6, y + 20 + i * ROW_H - 4, w - 12, 1);
      }

      if (sel) {
        ctx.fillStyle = "#a8cc80";
        ctx.fillRect(x + 4, y + 20 + i * ROW_H - 1, w - 8, ROW_H - 1);
      }
      ctx.fillStyle = "#0f380f";
      ctx.font = sel ? "bold 7px 'Courier New', monospace" : "7px 'Courier New', monospace";
      ctx.fillText(`${sel ? "▶" : " "} ${opt.label}`, x + 8, y + 20 + i * ROW_H);

      if (opt.volume) {
        const val    = typeof raw === "number" ? raw : 0.8;
        const pct    = `${Math.round(val * 100)}%`;
        ctx.font = "7px 'Courier New', monospace";
        ctx.fillText(`◀ ${pct} ▶`, x + w - 8 - (pct.length + 5) * 6, y + 20 + i * ROW_H);
      } else {
        const curStr = _optToDisplay(opt, raw);
        ctx.font = "7px 'Courier New', monospace";
        ctx.fillText(`◀ ${curStr} ▶`, x + w - 8 - (curStr.length + 5) * 6, y + 20 + i * ROW_H);
      }
    });

    ctx.fillStyle = "rgba(15,56,15,0.5)";
    ctx.font = "6px 'Courier New', monospace";
    ctx.fillText("[A/D] or [←/→] to change value", x + 8, y + h - 10);
  }

  renderConfirm(ps) {
    const { ctx } = this;
    const W = this.canvas.width;
    const H = this.canvas.height;
    const x = 20, y = Math.floor(H / 2) - 44, w = W - 40, h = 88;

    _gbPanel(ctx, x, y, w, h);

    ctx.fillStyle = "#0f380f";
    ctx.font = "bold 8px 'Courier New', monospace";
    ctx.textBaseline = "top";
    ctx.fillText("Start a new game?", x + 12, y + 8);
    ctx.font = "7px 'Courier New', monospace";
    ctx.fillText("This will erase your current save.", x + 8, y + 26);
    ctx.fillText("All progress will be lost.", x + 8, y + 38);

    ctx.font = "8px 'Courier New', monospace";
    const yM = ps.confirmIndex === 0 ? "▶" : " ";
    const nM = ps.confirmIndex === 1 ? "▶" : " ";
    ctx.fillText(`${yM} YES`, x + 28, y + 60);
    ctx.fillText(`${nM} NO`,  x + w - 52, y + 60);
  }
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function _gbPanel(ctx, x, y, w, h) {
  ctx.fillStyle = "#0f380f";
  ctx.fillRect(x, y, w, h);
  ctx.fillStyle = "#ffffff";
  ctx.fillRect(x + 1, y + 1, w - 2, h - 2);
  ctx.fillStyle = "#0f380f";
  ctx.fillRect(x + 2, y + 2, w - 4, h - 4);
  ctx.fillStyle = "#d7efc2";
  ctx.fillRect(x + 3, y + 3, w - 6, h - 6);
}

function _getBagItems(state, tab) {
  const items = state.items ?? {};
  if (tab === 0) {
    return [
      { id: "potion",       label: "POTION",       qty: items.potion       ?? 0 },
      { id: "super_potion", label: "SUPER POTION",  qty: items.super_potion ?? 0 },
      { id: "antidote",     label: "ANTIDOTE",      qty: items.antidote     ?? 0 },
      { id: "burnHeal",     label: "BURN HEAL",     qty: items.burnHeal     ?? 0 },
      { id: "awakening",    label: "AWAKENING",     qty: items.awakening    ?? 0 },
      { id: "paralyzeHeal", label: "PARALYZ HEAL",  qty: items.paralyzeHeal ?? 0 },
      { id: "iceHeal",      label: "ICE HEAL",      qty: items.iceHeal      ?? 0 },
    ];
  }
  if (tab === 1) {
    return [
      { id: "capsule",       label: "CAPSULE",       qty: items.capsule       ?? 0 },
      { id: "great_capsule", label: "GREAT CAPSULE", qty: items.great_capsule ?? 0 },
    ];
  }
  const keyItems = [];
  if (state.flags?.canRun)     { keyItems.push({ id: "runningShoes",  label: "RUNNING SHOES", qty: 1 }); }
  if (state.flags?.amuletCoin) { keyItems.push({ id: "amuletCoin",    label: "AMULET COIN",   qty: 1 }); }
  if (tab === 2) { return keyItems; }
  // tab 3 — TMs
  const tmItems = [];
  for (const [id, label] of Object.entries(TM_LABELS)) {
    const qty = state.items?.[id] ?? 0;
    if (qty > 0) { tmItems.push({ id, label, qty }); }
  }
  return tmItems;
}

const TM_LABELS = {
  tm01_body_slam: "TM01 BODY SLAM",
};

const TM_MOVES = {
  tm01_body_slam: "body_slam",
};

function _getDexEntries(state) {
  const src = window._tiamatCreatures ?? {};
  const SPECIES = src.SPECIES ?? src.CREATURES ?? {};
  return Object.values(SPECIES).map((s) => ({
    id:    s.id,
    name:  s.name,
    types: s.types,
    type:  s.type,
  }));
}

function _optToDisplay(opt, raw) {
  if (raw === undefined || raw === null) { return opt.values[opt.values.length - 1]; }
  if (typeof raw === "boolean") { return raw ? "On" : "Off"; }
  if (typeof raw === "number")  { return String(raw); }
  // capitalise first letter
  const s = String(raw);
  return s.charAt(0).toUpperCase() + s.slice(1);
}
