// Reusable UI widgets: panels, list menus, confirm prompts, bars.
import { input } from '../core/input.js';
import { GAME_W } from '../config.js';
import { audio } from '../core/audio.js';
import { txt, measure } from './text.js';
import { sexSymbol } from '../battle/mon.js';

let menuSeq = 0;

export function panel(scene, x, y, w, h, style = 'dark') {
  const p = scene.add.nineslice(Math.round(x), Math.round(y), `panel_${style}`, null, Math.round(w), Math.round(h), 5, 5, 5, 5);
  p.setOrigin(0, 0);
  return p;
}

// ♂ / ♀ after a name: blue for male, pink for female. x is where the name starts.
export function sexMark(scene, x, y, mon, name) {
  const sym = sexSymbol(mon);
  return txt(scene, x + (name ? measure(scene, name) + 2 : 0), y, sym, { color: sym === '♀' ? 'pink' : 'blue' });
}

// Highlight bar for the selected row of a list (easy to see on small phone screens).
export function selBar(scene, x, w, h = 13) {
  const g = scene.add.graphics();
  g.fillStyle(0xffd65c, 0.2); g.fillRoundedRect(0, 0, w, h, 3);
  g.lineStyle(1, 0xffd65c, 0.9); g.strokeRoundedRect(0.5, 0.5, w - 1, h - 1, 3);
  g.x = x;
  const tw = scene.tweens.add({ targets: g, alpha: 0.6, duration: 650, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
  g.once('destroy', () => tw.remove());
  return g;
}

// A vertical list menu with a cursor. Resolves with the chosen item's value,
// or `null` if cancelled (when cancellable).
export class ListMenu {
  constructor(scene, opts) {
    this.scene = scene;
    this.items = opts.items;
    this.x = opts.x; this.y = opts.y;
    this.width = opts.width || (Math.max(...this.items.map((i) => measure(scene, i.label) + (i.right ? measure(scene, String(i.right)) + 12 : 0))) + 26);
    this.rowH = opts.rowH || 14;
    this.visible = Math.min(opts.visible || this.items.length, this.items.length);
    this.cancellable = opts.cancellable !== false;
    this.index = Math.max(0, Math.min(opts.index || 0, this.items.length - 1));
    this.scroll = 0;
    this.depth = opts.depth ?? 9000;
    this.style = opts.style || 'dark';
    this.onMove = opts.onMove;
    this.owner = `menu${++menuSeq}`;
    this.pad = opts.pad ?? 7;
    this.height = this.visible * this.rowH + this.pad * 2 - 2;
    if (opts.anchor === 'bottom-right') {
      // on phones, keep clear of the A / B / RUN buttons
      const right = Math.min(opts.x, input.touchSafeRight(GAME_W));
      this.x = right - this.width; this.y = opts.y - this.height;
    }
    this.container = scene.add.container(0, 0).setDepth(this.depth).setScrollFactor(0);
    if (!opts.noPanel) { this.container.add(panel(scene, this.x, this.y, this.width, this.height, this.style)); }
    this.barH = Math.min(this.rowH - 1, 17);
    this.bar = selBar(scene, this.x + 3, this.width - 6, this.barH);
    this.container.add(this.bar);
    this.rows = [];
    for (let i = 0; i < this.visible; i++) {
      const t = txt(scene, this.x + 14, this.y + this.pad + i * this.rowH, '');
      const r = txt(scene, this.x + this.width - 8, this.y + this.pad + i * this.rowH, '', { align: 'right' });
      this.container.add([t, r]);
      this.rows.push([t, r]);
    }
    this.cursor = scene.add.image(this.x + 6, 0, 'cursor').setOrigin(0, 0);
    this.upArrow = txt(scene, this.x + this.width - 12, this.y - 1, '^', { color: 'gold' });
    this.downArrow = txt(scene, this.x + this.width - 12, this.y + this.height - 9, 'v', { color: 'gold' });
    this.container.add([this.cursor, this.upArrow, this.downArrow]);
    this.render();
  }

  render() {
    if (this.index < this.scroll) { this.scroll = this.index; }
    if (this.index >= this.scroll + this.visible) { this.scroll = this.index - this.visible + 1; }
    for (let i = 0; i < this.visible; i++) {
      const item = this.items[this.scroll + i];
      const [t, r] = this.rows[i];
      if (!item) { t.setText(''); r.setText(''); continue; }
      t.setText(item.label);
      const sel = this.scroll + i === this.index;
      t.setFont(`main_${item.disabled ? 'gray' : (item.color || (sel ? 'gold' : 'white'))}`);
      r.setText(item.right !== undefined ? String(item.right) : '');
      r.setFont(`main_${item.rightColor || (item.disabled ? 'gray' : 'white')}`);
    }
    this.cursor.y = this.y + this.pad + (this.index - this.scroll) * this.rowH + 1;
    this.bar.y = this.y + this.pad + (this.index - this.scroll) * this.rowH - Math.floor((this.barH - 9) / 2) - 1;
    this.upArrow.setVisible(this.scroll > 0);
    this.downArrow.setVisible(this.scroll + this.visible < this.items.length);
  }

  setItems(items) { this.items = items; this.index = Math.min(this.index, items.length - 1); this.render(); }

  run() {
    input.push(this.owner);
    return new Promise((resolve) => {
      const tick = () => {
        if (!input.has(this.owner)) { return; }
        const n = this.items.length;
        if (input.nav('up', this.owner)) { this.index = (this.index + n - 1) % n; audio.sfx('cursor'); this.render(); this.onMove && this.onMove(this.items[this.index], this.index); }
        else if (input.nav('down', this.owner)) { this.index = (this.index + 1) % n; audio.sfx('cursor'); this.render(); this.onMove && this.onMove(this.items[this.index], this.index); }
        else if (input.pressed('confirm', this.owner)) {
          const item = this.items[this.index];
          if (item.disabled) { audio.blip('bump'); return; }
          audio.sfx('select');
          finish(item.value !== undefined ? item.value : this.index);
        } else if (this.cancellable && input.pressed('cancel', this.owner)) {
          audio.sfx('cancel');
          finish(null);
        }
      };
      const finish = (v) => {
        this.scene.events.off('update', tick);
        input.pop(this.owner);
        resolve(v);
      };
      this.scene.events.on('update', tick);
      this.onMove && this.onMove(this.items[this.index], this.index);
    });
  }

  destroy() { this.container.destroy(); }
}

// Convenience: show a menu, await choice, destroy.
export async function choose(scene, items, opts = {}) {
  const m = new ListMenu(scene, { items, ...opts });
  const v = await m.run();
  if (!opts.keep) { m.destroy(); }
  return v;
}

// Horizontal HP / XP bar made of rectangles.
export class Bar {
  constructor(scene, x, y, w, h, opts = {}) {
    this.scene = scene;
    this.w = w; this.h = h;
    this.kind = opts.kind || 'hp';
    this.bg = scene.add.rectangle(x, y, w + 2, h + 2, 0x0b0c16).setOrigin(0, 0);
    this.back = scene.add.rectangle(x + 1, y + 1, w, h, 0x3a3f5e).setOrigin(0, 0);
    this.fill = scene.add.rectangle(x + 1, y + 1, w, h, 0x5ee07a).setOrigin(0, 0);
    this.shine = scene.add.rectangle(x + 1, y + 1, w, 1, 0xffffff, 0.35).setOrigin(0, 0);
    this.value = 1;
    this.parts = [this.bg, this.back, this.fill, this.shine];
  }
  addTo(container) { container.add(this.parts); return this; }
  setDepth(d) { this.parts.forEach((p) => p.setDepth(d)); return this; }
  set(frac) {
    this.value = Math.max(0, Math.min(1, frac));
    const w = Math.round(this.w * this.value);
    this.fill.width = w; this.shine.width = w;
    this.fill.setVisible(w > 0); this.shine.setVisible(w > 0);
    if (this.kind === 'hp') {
      this.fill.fillColor = this.value > 0.5 ? 0x5ee07a : (this.value > 0.2 ? 0xf5c542 : 0xf05a5a);
    } else {
      this.fill.fillColor = 0x5ab4ff;
    }
    return this;
  }
  tweenTo(frac, ms = 500) {
    return new Promise((resolve) => {
      const o = { v: this.value };
      this.scene.tweens.add({ targets: o, v: frac, duration: ms, ease: 'Sine.easeOut', onUpdate: () => this.set(o.v), onComplete: () => { this.set(frac); resolve(); } });
    });
  }
  setVisible(v) { this.parts.forEach((p) => p.setVisible(v)); return this; }
  destroy() { this.parts.forEach((p) => p.destroy()); }
}
