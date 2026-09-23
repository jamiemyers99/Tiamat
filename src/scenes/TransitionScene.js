// Battle-intro wipe played over the overworld.
import Phaser from 'phaser';
import { GAME_W, GAME_H } from '../config.js';
import { audio } from '../core/audio.js';

export class TransitionScene extends Phaser.Scene {
  constructor() { super('Transition'); }

  init(data) { this.cfg = data; }

  create() {
    const style = this.cfg.style || 'wild';
    const g = this.add.graphics();
    const flash = this.add.rectangle(0, 0, GAME_W, GAME_H, 0xffffff, 0).setOrigin(0, 0);
    audio.sfx(style === 'wild' ? 'encounter' : 'encounter_jingle');
    const flashes = [0, 1];
    let t = 0;
    const total = 760;
    const done = () => {
      this.events.off('update', upd);
      this.cfg.onCovered && this.cfg.onCovered();
      this.time.delayedCall(30, () => this.scene.stop());
    };
    const upd = (time, delta) => {
      t += delta;
      // two quick flashes, then the wipe
      if (t < 240) {
        const k = (t % 120) / 120;
        flash.setAlpha(k < 0.5 ? k * 1.6 : (1 - k) * 1.6);
        return;
      }
      flash.setAlpha(0);
      const p = Math.min(1, (t - 240) / (total - 240));
      g.clear();
      g.fillStyle(0x08070e, 1);
      if (style === 'wild') {
        const bars = 12;
        const h = GAME_H / bars;
        for (let i = 0; i < bars; i++) {
          const w = GAME_W * Math.min(1, Math.max(0, p * 1.6 - (i % 2) * 0.3));
          if (i % 2) { g.fillRect(GAME_W - w, i * h, w, h + 1); } else { g.fillRect(0, i * h, w, h + 1); }
        }
      } else if (style === 'trainer') {
        const s = 30;
        for (let y = 0; y < GAME_H + s; y += s) {
          for (let x = 0; x < GAME_W + s; x += s) {
            const d = (x + y) / (GAME_W + GAME_H);
            const k = Math.min(1, Math.max(0, (p * 1.8 - d)) * 3);
            if (k > 0) {
              const r = (s / 2) * k * 1.45;
              g.fillPoints([{ x: x, y: y - r }, { x: x + r, y }, { x, y: y + r }, { x: x - r, y }], true);
            }
          }
        }
      } else {
        // boss: shutters closing from both sides with a coloured edge
        const w = (GAME_W / 2) * p;
        const cols = 16;
        const cw = GAME_H / cols;
        for (let i = 0; i < cols; i++) {
          const k = Math.min(1, p * 1.3 - (i % 3) * 0.08);
          const ww = Math.max(0, (GAME_W / 2 + 4) * k);
          g.fillStyle(0x6a4cd8, 1);
          g.fillRect(0, i * cw, ww + 3, cw + 1);
          g.fillRect(GAME_W - ww - 3, i * cw, ww + 3, cw + 1);
          g.fillStyle(0x08070e, 1);
          g.fillRect(0, i * cw, ww, cw + 1);
          g.fillRect(GAME_W - ww, i * cw, ww, cw + 1);
        }
        if (w <= 0) { g.clear(); }
      }
      if (p >= 1) { done(); }
    };
    this.events.on('update', upd);
  }
}
