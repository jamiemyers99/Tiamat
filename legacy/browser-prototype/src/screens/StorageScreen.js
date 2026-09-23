// PC Box storage screen — deposit, withdraw, swap party ↔ box.
// Exports: StorageScreen
import { withdrawMorph, depositMorph, swapPartyWithBox } from "../engine/storage.js?v=20260429-19";
import audio from "../engine/audio.js?v=20260429-19";

// Modes: 'boxes' (select box) | 'grid' (navigate slots in a box) | 'party' (select party slot)
export class StorageScreen {
  constructor(canvas, ctx) {
    this.canvas = canvas;
    this.ctx    = ctx;
  }

  update(state, input, ps) {
    const st = ps.storageState;
    if (!st) { return; }
    const storage = state.storage;

    if (input.wasPressed("escape", "backspace")) {
      audio.playSfx("menu_back");
      if (st.mode === "grid")  { st.mode = "boxes";  return; }
      if (st.mode === "party") { st.mode = "grid";   st.held = null; return; }
      ps.subScreen = null;
      return;
    }

    if (st.mode === "boxes") {
      if (input.wasPressed("arrowup", "w")) {
        st.boxIndex = (st.boxIndex + storage.boxes.length - 1) % storage.boxes.length;
        audio.playSfx("ui_move");
      } else if (input.wasPressed("arrowdown", "s")) {
        st.boxIndex = (st.boxIndex + 1) % storage.boxes.length;
        audio.playSfx("ui_move");
      } else if (input.wasPressed("e", " ", "enter")) {
        audio.playSfx("menu_confirm");
        st.mode      = "grid";
        st.slotIndex = 0;
      }
      return;
    }

    if (st.mode === "grid") {
      const COLS = 6;
      const ROWS = 5; // 30 slots / 6 cols
      if (input.wasPressed("arrowleft", "a")) {
        st.slotIndex = (st.slotIndex % COLS === 0) ? st.slotIndex : st.slotIndex - 1;
        audio.playSfx("ui_move");
      } else if (input.wasPressed("arrowright", "d")) {
        st.slotIndex = (st.slotIndex % COLS === COLS - 1) ? st.slotIndex : st.slotIndex + 1;
        audio.playSfx("ui_move");
      } else if (input.wasPressed("arrowup", "w")) {
        st.slotIndex = Math.max(0, st.slotIndex - COLS);
        audio.playSfx("ui_move");
      } else if (input.wasPressed("arrowdown", "s")) {
        st.slotIndex = Math.min(29, st.slotIndex + COLS);
        audio.playSfx("ui_move");
      } else if (input.wasPressed("e", " ", "enter")) {
        audio.playSfx("menu_confirm");
        const box     = storage.boxes[st.boxIndex];
        const inSlot  = box?.slots[st.slotIndex];
        if (inSlot) {
          // Pick up — switch to party selection mode.
          st.held      = { boxIndex: st.boxIndex, slotIndex: st.slotIndex };
          st.mode      = "party";
          st.partyIdx  = 0;
        }
      }
      return;
    }

    if (st.mode === "party") {
      const partyLen = state.party.length;
      if (input.wasPressed("arrowup", "w")) {
        st.partyIdx = (st.partyIdx + partyLen - 1) % Math.max(1, partyLen);
        audio.playSfx("ui_move");
      } else if (input.wasPressed("arrowdown", "s")) {
        st.partyIdx = (st.partyIdx + 1) % Math.max(1, partyLen);
        audio.playSfx("ui_move");
      } else if (input.wasPressed("e", " ", "enter")) {
        audio.playSfx("menu_confirm");
        if (st.held) {
          // Swap box slot with party slot.
          swapPartyWithBox(state.party, st.partyIdx, storage, st.held.boxIndex, st.held.slotIndex);
          // Remove empty party slots (preserve at least one if possible).
          const filled = state.party.filter(Boolean);
          if (filled.length > 0) { state.party.length = 0; filled.forEach((c) => state.party.push(c)); }
          st.held = null;
        }
        st.mode = "grid";
      }
    }
  }

  render(state, ps) {
    const st = ps.storageState;
    if (!st) { return; }

    const { ctx } = this;
    const W = this.canvas.width;
    const H = this.canvas.height;
    const storage = state.storage;

    _gbPanel(ctx, 4, 4, W - 8, H - 8);

    ctx.fillStyle = "#0f380f";
    ctx.font = "bold 8px 'Courier New', monospace";
    ctx.textBaseline = "top";
    ctx.fillText("PC STORAGE", 12, 12);
    ctx.font = "7px 'Courier New', monospace";
    ctx.fillText("[Esc] back", W - 76, 12);

    // Box list (left panel).
    const BOX_PX = 70;
    storage.boxes.forEach((box, i) => {
      const sel = st.boxIndex === i;
      if (sel) {
        ctx.fillStyle = "#a8cc80";
        ctx.fillRect(8, 26 + i * 14, BOX_PX - 4, 12);
      }
      ctx.fillStyle = "#0f380f";
      ctx.fillText(`${sel ? "▶" : " "} ${box.name}`, 10, 27 + i * 14);
      const count = box.slots.filter(Boolean).length;
      ctx.fillText(`${count}/30`, 50, 27 + i * 14);
    });

    // Grid panel (right side).
    if (st.mode === "grid" || st.mode === "party") {
      const box  = storage.boxes[st.boxIndex];
      const gx   = BOX_PX + 10;
      const gy   = 24;
      const COLS = 6;
      const CW   = 26;
      const CH   = 18;

      ctx.fillStyle = "#0f380f";
      ctx.font = "bold 7px 'Courier New', monospace";
      ctx.fillText(box?.name ?? "", gx, gy - 4);

      box?.slots.forEach((creature, idx) => {
        const col = idx % COLS;
        const row = Math.floor(idx / COLS);
        const sx  = gx + col * CW;
        const sy  = gy + row * CH;
        const sel = st.slotIndex === idx && st.mode === "grid";

        ctx.fillStyle = sel ? "#a8cc80" : (creature ? "#306230" : "#9bbc0f");
        ctx.fillRect(sx, sy, CW - 2, CH - 2);

        if (creature) {
          ctx.fillStyle = "#d7efc2";
          ctx.font = "6px 'Courier New', monospace";
          ctx.fillText(creature.name.slice(0, 4), sx + 1, sy + 2);
          ctx.fillText(`L${creature.level}`, sx + 1, sy + 10);
        }

        if (sel) {
          ctx.strokeStyle = "#c83e20";
          ctx.lineWidth   = 1;
          ctx.strokeRect(sx, sy, CW - 2, CH - 2);
        }
      });

      // Held info.
      if (st.held) {
        const heldBox     = storage.boxes[st.held.boxIndex];
        const heldCreature = heldBox?.slots[st.held.slotIndex];
        ctx.fillStyle = "#0f380f";
        ctx.font = "7px 'Courier New', monospace";
        ctx.fillText(`Held: ${heldCreature?.name ?? "?"}`, gx, H - 30);
        ctx.fillText("Select party slot to swap", gx, H - 20);
      }
    }

    // Party panel (shown in party mode).
    if (st.mode === "party") {
      const px = 4, py = Math.floor(H * 0.55), pw = W - 8, ph = Math.floor(H * 0.40);
      _gbPanel(ctx, px, py, pw, ph);
      ctx.fillStyle = "#0f380f";
      ctx.font = "bold 7px 'Courier New', monospace";
      ctx.fillText("Swap with party slot:", px + 8, py + 10);
      ctx.font = "7px 'Courier New', monospace";
      state.party.forEach((c, i) => {
        const sel = st.partyIdx === i;
        if (sel) {
          ctx.fillStyle = "#a8cc80";
          ctx.fillRect(px + 6, py + 18 + i * 14, pw - 12, 12);
        }
        ctx.fillStyle = "#0f380f";
        ctx.fillText(`${sel ? "▶" : " "} ${c?.name ?? "---"} L${c?.level ?? "?"}`, px + 8, py + 20 + i * 14);
      });
    }
  }
}

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
