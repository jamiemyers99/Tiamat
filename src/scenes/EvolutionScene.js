// Evolution sequence overlay.
import Phaser from 'phaser';
import { GAME_W, GAME_H } from '../config.js';
import { input } from '../core/input.js';
import { audio } from '../core/audio.js';
import { G, markCaught } from '../core/state.js';
import { evolve, monName, monFrame, replaceMove } from '../battle/mon.js';
import { SPECIES } from '../data/species.js';
import { MOVES } from '../data/moves.js';
import { txt, wrap, fmt } from '../ui/text.js';
import { panel, choose } from '../ui/widgets.js';

export class EvolutionScene extends Phaser.Scene {
  constructor() { super('Evolution'); }
  init(data) { this.cfg = data; }

  async create() {
    const { mon, into } = this.cfg;
    this.owner = 'evo';
    input.push(this.owner);
    this.add.rectangle(0, 0, GAME_W, GAME_H, 0x0c0b14).setOrigin(0, 0);
    const rays = this.add.graphics();
    this.rays = rays;
    this.bgT = 0;
    this.events.on('update', (t, d) => {
      this.bgT += d;
      rays.clear();
      for (let i = 0; i < 18; i++) {
        const a = (i / 18) * Math.PI * 2 + this.bgT / 3000;
        rays.fillStyle(i % 2 ? 0x1b1e33 : 0x141627, 1);
        rays.fillTriangle(GAME_W / 2, 110, GAME_W / 2 + Math.cos(a) * 400, 110 + Math.sin(a) * 400, GAME_W / 2 + Math.cos(a + 0.18) * 400, 110 + Math.sin(a + 0.18) * 400);
      }
    });
    const oldF = monFrame(mon, 'f');
    const newF = monFrame({ ...mon, species: into }, 'f');
    const spr = this.add.image(GAME_W / 2, 160, 'mons', oldF).setOrigin(0.5, 1).setScale(1.3);
    this.msgBg = panel(this, 8, GAME_H - 62, GAME_W - 16, 56, 'dark');
    this.lines = [0, 1, 2].map((i) => txt(this, 22, GAME_H - 52 + i * 14, ''));
    audio.stopMusic(200);
    const name = monName(mon);
    await this.say(`What? ${name} is evolving!`);
    audio.sfx('evolve');
    audio.jingle('jingle_evolve');
    let cancelled = false;
    let t = 0, period = 600, showNew = false;
    spr.setTintFill(0xffffff);
    const total = 5200;
    await new Promise((resolve) => {
      const tick = (time, d) => {
        t += d;
        if (input.pressed('cancel', this.owner)) { cancelled = true; }
        if (cancelled || t >= total) { this.events.off('update', tick); resolve(); return; }
        period = Math.max(70, 600 - t / 9);
        const phase = Math.floor(t / period) % 2 === 1;
        if (phase !== showNew) {
          showNew = phase;
          spr.setFrame(showNew ? newF : oldF);
          spr.setScale(showNew ? 1.4 : 1.3);
        }
        if (Math.random() < 0.3) {
          const p = this.add.image(spr.x + Phaser.Math.Between(-60, 60), spr.y - Phaser.Math.Between(0, 120), 'p_star').setTint(0xffd65c).setScale(2);
          this.tweens.add({ targets: p, alpha: 0, y: p.y - 20, duration: 500, onComplete: () => p.destroy() });
        }
      };
      this.events.on('update', tick);
    });
    if (cancelled) {
      spr.setFrame(oldF).clearTint().setScale(1.3);
      await this.say(`Huh? ${name} stopped evolving!`);
    } else {
      this.cameras.main.flash(500, 255, 255, 255);
      spr.setFrame(newF).clearTint().setScale(1.4);
      const oldName = SPECIES[mon.species].name;
      const pending = evolve(mon, into);
      markCaught(into);
      audio.cry(SPECIES[into].num);
      await this.say(`Congratulations! Your ${oldName} evolved into ${SPECIES[into].name}!`);
      for (const mv of pending) { await this.learn(mon, mv); }
    }
    input.pop(this.owner);
    this.cfg.onDone && this.cfg.onDone(!cancelled);
    this.scene.stop();
  }

  async learn(mon, moveId) {
    const mv = MOVES[moveId];
    const nm = monName(mon);
    await this.say(`${nm} wants to learn ${mv.name}, but already knows four moves.`);
    const items = mon.moves.map((m, i) => ({ label: MOVES[m.id].name, value: i }));
    items.push({ label: `Don't learn ${mv.name}`, value: -1, color: 'gold' });
    const idx = await choose(this, items, { x: GAME_W - 12, y: GAME_H - 66, anchor: 'bottom-right', width: 200 });
    if (idx === null || idx === -1) { await this.say(`${nm} did not learn ${mv.name}.`); return; }
    const old = MOVES[mon.moves[idx].id].name;
    replaceMove(mon, idx, moveId);
    await this.say(`${nm} forgot ${old} and learned ${mv.name}!`);
  }

  say(text) {
    const lines = wrap(this, fmt(text, G.state), GAME_W - 60);
    return new Promise((resolve) => {
      let shown = 0;
      const full = lines.join('\n');
      const tick = () => {
        shown = Math.min(full.length, shown + 2);
        const parts = full.slice(0, shown).split('\n');
        this.lines.forEach((l, i) => l.setText(parts[i] || ''));
        if (shown >= full.length && (input.pressed('confirm', this.owner) || input.pressed('cancel', this.owner))) {
          this.events.off('update', tick); resolve();
        }
      };
      this.events.on('update', tick);
    });
  }
}
