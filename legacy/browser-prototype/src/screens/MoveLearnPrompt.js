// Move-learn prompt — "Forget which move?" overlay shown when a Morph wants
// to learn a new move but already knows 4.
// Exports: MoveLearnPrompt
// Usage: prompt.open(creature, newMove, onDone)
//   onDone(forgottenMove | null) — null means "Don't learn".

import audio from "../engine/audio.js?v=20260429-19";

export class MoveLearnPrompt {
  constructor(canvas, ctx) {
    this.canvas   = canvas;
    this.ctx      = ctx;
    this._open    = false;
    this._creature = null;
    this._newMove  = null;
    this._onDone   = null;
    this._index    = 0;      // 0-3 = existing moves, 4 = "Don't learn"
    this._OPTIONS  = 5;
  }

  get active() { return this._open; }

  open(creature, newMove, onDone) {
    this._creature = creature;
    this._newMove  = newMove;
    this._onDone   = onDone;
    this._index    = 0;
    this._open     = true;
  }

  update(input) {
    if (!this._open) { return; }

    if (input.wasPressed("arrowup", "w")) {
      this._index = (this._index + this._OPTIONS - 1) % this._OPTIONS;
      audio.playSfx("ui_move");
    } else if (input.wasPressed("arrowdown", "s")) {
      this._index = (this._index + 1) % this._OPTIONS;
      audio.playSfx("ui_move");
    } else if (input.wasPressed("e", " ", "enter")) {
      audio.playSfx("menu_confirm");
      if (this._index === 4) {
        // Don't learn.
        this._close(null);
      } else {
        const forgotten = this._creature.moves[this._index];
        this._creature.moves[this._index] = this._newMove;
        this._close(forgotten);
      }
    } else if (input.wasPressed("backspace", "escape")) {
      audio.playSfx("menu_back");
      this._close(null);
    }
  }

  _close(result) {
    this._open = false;
    this._onDone?.(result);
  }

  render() {
    if (!this._open) { return; }
    const { ctx } = this;
    const W = this.canvas.width;
    const H = this.canvas.height;
    const x = 10, y = 10, w = W - 20, h = H - 20;

    _gbPanel(ctx, x, y, w, h);

    ctx.fillStyle = "#0f380f";
    ctx.font = "bold 8px 'Courier New', monospace";
    ctx.textBaseline = "top";
    ctx.fillText(`${this._creature?.name} wants to learn`, x + 8, y + 10);
    ctx.fillText(`${this._newMove?.name}!`, x + 8, y + 20);

    ctx.font = "7px 'Courier New', monospace";
    ctx.fillText("Forget which move?", x + 8, y + 34);

    const moves = this._creature?.moves ?? [];
    moves.forEach((m, i) => {
      const sel = this._index === i;
      if (sel) {
        ctx.fillStyle = "#a8cc80";
        ctx.fillRect(x + 6, y + 48 + i * 22 - 2, w - 12, 20);
      }
      ctx.fillStyle = "#0f380f";
      ctx.font = "bold 7px 'Courier New', monospace";
      ctx.fillText(`${sel ? "▶" : " "} ${m.name}`, x + 8, y + 48 + i * 22);
      ctx.font = "7px 'Courier New', monospace";
      ctx.fillText(`Type: ${m.type}  Pow: ${m.power || "—"}  PP: ${m.pp}`, x + 18, y + 58 + i * 22);
    });

    // "Don't learn" option.
    const dontSel = this._index === 4;
    if (dontSel) {
      ctx.fillStyle = "#e8a080";
      ctx.fillRect(x + 6, y + 48 + 4 * 22 - 2, w - 12, 20);
    }
    ctx.fillStyle = "#0f380f";
    ctx.font = "bold 7px 'Courier New', monospace";
    ctx.fillText(`${dontSel ? "▶" : " "} Don't learn ${this._newMove?.name}`, x + 8, y + 48 + 4 * 22);
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
