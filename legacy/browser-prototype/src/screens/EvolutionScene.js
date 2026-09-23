// Evolution scene — animated evolution sequence with cancel support.
// Exports: EvolutionScene
// Triggered by App after a battle when buildEvolutionQueue returns entries.
// The scene renders over the world. Player presses B/Backspace to cancel.

import { applyEvolution } from "../engine/evolution.js?v=20260429-19";
import audio from "../engine/audio.js?v=20260429-19";

const PHASE_FLASH_IN  = 0;   // white overlay fades in (800ms)
const PHASE_GLOW      = 1;   // silhouette pulses (1200ms)
const PHASE_FLASH_OUT = 2;   // white overlay fades out (600ms)
const PHASE_DONE      = 3;

export class EvolutionScene {
  constructor(canvas, ctx) {
    this.canvas = canvas;
    this.ctx    = ctx;
    this._phase   = PHASE_DONE;
    this._timer   = 0;
    this._alpha   = 0;
    this._queue   = [];  // [{ partyIndex, targetSpeciesId }]
    this._current = null;
    this._msg     = "";
    this._cancelled = false;
  }

  // Call this after a battle to start queued evolutions.
  // `party` is state.party (mutable). `onDone` called when all complete.
  start(queue, party, onDone) {
    this._queue   = [...queue];
    this._party   = party;
    this._onDone  = onDone;
    audio.stopBgm({ fadeMs: 200 });
    this._advance();
  }

  get active() { return this._phase !== PHASE_DONE || this._queue.length > 0; }

  _advance() {
    if (this._queue.length === 0) {
      this._phase = PHASE_DONE;
      this._onDone?.();
      return;
    }
    this._current   = this._queue.shift();
    this._cancelled = false;
    this._phase     = PHASE_FLASH_IN;
    this._timer     = 0;
    this._alpha     = 0;
    this._msg       = "";
    audio.playSfx("evolve");
  }

  update(input, delta) {
    if (this._phase === PHASE_DONE) { return; }

    // Player can cancel during flash-in / glow.
    if (input.wasPressed("backspace", "b") && this._phase !== PHASE_FLASH_OUT) {
      this._cancelled = true;
      const creature = this._party?.[this._current?.partyIndex];
      if (creature) {
        creature.flags = creature.flags ?? {};
        creature.flags.evolutionCancelled = true;
      }
      this._msg = `${creature?.name ?? "It"} did not evolve.`;
      this._phase = PHASE_FLASH_OUT;
      this._timer = 0;
      this._alpha = 0.9;
      return;
    }

    this._timer += delta;

    if (this._phase === PHASE_FLASH_IN) {
      this._alpha = Math.min(0.95, this._timer / 800);
      if (this._timer >= 800) {
        // Apply evolution.
        if (!this._cancelled) {
          const creature = this._party?.[this._current?.partyIndex];
          if (creature) {
            const msgs = applyEvolution(creature, this._current.targetSpeciesId);
            this._msg = msgs[0] ?? "";
            audio.playSfx("evolve");
          }
        }
        this._phase = PHASE_GLOW;
        this._timer = 0;
      }
      return;
    }

    if (this._phase === PHASE_GLOW) {
      this._alpha = 0.9 + Math.sin(this._timer / 200) * 0.05;
      if (this._timer >= 1200) {
        this._phase = PHASE_FLASH_OUT;
        this._timer = 0;
        this._alpha = 0.95;
      }
      return;
    }

    if (this._phase === PHASE_FLASH_OUT) {
      this._alpha = Math.max(0, 0.95 - this._timer / 600);
      if (this._timer >= 600) {
        this._phase = PHASE_DONE;
        this._advance();
      }
    }
  }

  render() {
    if (this._phase === PHASE_DONE) { return; }
    const { ctx } = this;
    const W = this.canvas.width;
    const H = this.canvas.height;

    // White flash overlay.
    ctx.fillStyle = `rgba(255,255,255,${this._alpha})`;
    ctx.fillRect(0, 0, W, H);

    // Message.
    if (this._msg && this._phase === PHASE_GLOW) {
      ctx.fillStyle = "#0f380f";
      ctx.font = "bold 8px 'Courier New', monospace";
      ctx.textBaseline = "top";
      ctx.fillText(this._msg, 12, H - 30);
    }

    // Cancel hint.
    if (this._phase === PHASE_FLASH_IN || this._phase === PHASE_GLOW) {
      ctx.fillStyle = "rgba(15,56,15,0.6)";
      ctx.font = "7px 'Courier New', monospace";
      ctx.fillText("[B] Cancel evolution", 12, H - 14);
    }
  }
}
