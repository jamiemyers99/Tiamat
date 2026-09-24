// Overlay scene: dialogue box, choices, toasts and the location banner.
// Other scenes talk to it through the exported `UI` helper.
import Phaser from 'phaser';
import { GAME_W, GAME_H } from '../config.js';
import { input } from '../core/input.js';
import { audio } from '../core/audio.js';
import { G } from '../core/state.js';
import { txt, wrap, fmt } from '../ui/text.js';
import { panel, choose, Bar } from '../ui/widgets.js';
import { maxHp, monName, monFrame } from '../battle/mon.js';

const SPEEDS = { slow: 45, normal: 24, fast: 10, instant: 0 };
const FRAMES = ['dark', 'teal', 'gold', 'red', 'light'];

export const UI = {
  scene: null,
  say(...a) { return this.scene.say(...a); },
  ask(...a) { return this.scene.ask(...a); },
  choose(...a) { return this.scene.chooseList(...a); },
  banner(...a) { return this.scene.banner(...a); },
  toast(...a) { return this.scene.toast(...a); },
  hideBox() { this.scene.hideBox(); },
  sleep(...a) { return this.scene.sleep(...a); },
  healPanel(...a) { return this.scene.healPanel(...a); },
};

export class UIScene extends Phaser.Scene {
  constructor() { super({ key: 'UI', active: false }); }

  create() {
    UI.scene = this;
    this.box = this.add.container(0, 0).setDepth(100).setVisible(false);
    this.boxBg = panel(this, 8, GAME_H - 64, GAME_W - 16, 58, 'dark');
    this.nameBg = panel(this, 14, GAME_H - 78, 60, 17, 'gold');
    this.nameTxt = txt(this, 22, GAME_H - 74, '', { color: 'gold' });
    this.lines = [0, 1, 2].map((i) => txt(this, 22, GAME_H - 56 + i * 14, ''));
    this.adv = this.add.image(GAME_W - 26, GAME_H - 16, 'advance').setOrigin(0.5);
    this.box.add([this.boxBg, this.nameBg, this.nameTxt, ...this.lines, this.adv]);
    this.tweens.add({ targets: this.adv, y: '+=2', duration: 320, yoyo: true, repeat: -1 });
    this.bannerC = this.add.container(0, 0).setDepth(90);
    this.toasts = [];
  }

  applyFrame() {
    const style = FRAMES[G.settings.frame || 0] || 'dark';
    this.boxBg.setTexture(`panel_${style}`);
    const light = style === 'light';
    this.lines.forEach((l) => l.setFont(light ? 'main_ink' : 'main_white'));
  }

  hideBox() { this.box.setVisible(false); }

  // Show text, page by page. Resolves when the player dismisses the last page.
  // opts: { keepOpen: bool (leave box visible after), auto: ms (auto advance) }
  async say(name, text, opts = {}) {
    this.applyFrame();
    const str = fmt(text, G.state);
    const maxW = GAME_W - 56;
    const pages = [];
    for (const chunk of str.split('|')) {
      const lines = wrap(this, chunk.trim(), maxW);
      for (let i = 0; i < lines.length; i += 3) { pages.push(lines.slice(i, i + 3)); }
    }
    this.box.setVisible(true);
    if (name) {
      this.nameTxt.setText(fmt(name, G.state));
      this.nameBg.width = this.nameTxt.width + 18;
      this.nameBg.setVisible(true); this.nameTxt.setVisible(true);
    } else {
      this.nameBg.setVisible(false); this.nameTxt.setVisible(false);
    }
    const owner = 'dialog';
    input.push(owner);
    try {
      for (let p = 0; p < pages.length; p++) {
        const last = p === pages.length - 1;
        await this._typePage(pages[p], owner, opts);
        this.adv.setVisible(!(last && opts.keepOpen));
        if (opts.auto) {
          await new Promise((r) => this.time.delayedCall(opts.auto, r));
        } else if (!(last && opts.keepOpen)) {
          await this._waitConfirm(owner);
          audio.sfx('cursor', { volume: 0.6 });
        }
      }
    } finally {
      input.pop(owner);
    }
    if (!opts.keepOpen) { this.box.setVisible(false); }
  }

  _typePage(lines, owner, opts) {
    return new Promise((resolve) => {
      this.lines.forEach((l) => l.setText(''));
      this.adv.setVisible(false);
      const ms = opts.speed ?? SPEEDS[G.settings.textSpeed] ?? 24;
      const full = lines.join('\n');
      if (ms === 0) { lines.forEach((l, i) => this.lines[i].setText(l)); resolve(); return; }
      let shown = 0;
      let acc = 0;
      const tick = (time, delta) => {
        if (input.pressed('confirm', owner) || input.pressed('cancel', owner)) { shown = full.length; }
        acc += delta;
        while (acc >= ms && shown < full.length) { acc -= ms; shown++; if (shown % 3 === 0) { audio.blip('text'); } }
        const part = full.slice(0, shown).split('\n');
        lines.forEach((_, i) => this.lines[i].setText(part[i] || ''));
        if (shown >= full.length) { this.events.off('update', tick); input.clear(); resolve(); }
      };
      this.events.on('update', tick);
    });
  }

  _waitConfirm(owner) {
    return new Promise((resolve) => {
      const tick = () => {
        if (input.pressed('confirm', owner) || input.pressed('cancel', owner)) { this.events.off('update', tick); resolve(); }
      };
      this.events.on('update', tick);
    });
  }

  // Yes/No prompt after a line of text. Resolves true/false.
  async ask(name, text, yes = 'Yes', no = 'No') {
    await this.say(name, text, { keepOpen: true });
    const v = await choose(this, [{ label: yes, value: true }, { label: no, value: false }],
      { x: GAME_W - 12, y: GAME_H - 70, anchor: 'bottom-right', depth: 120 });
    this.box.setVisible(false);
    return v === true;
  }

  // Text + list of options. Returns value or null.
  async chooseList(name, text, items, opts = {}) {
    if (text) { await this.say(name, text, { keepOpen: true }); }
    const v = await choose(this, items, { x: GAME_W - 12, y: GAME_H - (text ? 70 : 12), anchor: 'bottom-right', depth: 120, visible: 7, ...opts });
    this.box.setVisible(false);
    return v;
  }

  banner(name) {
    this.bannerC.removeAll(true);
    const w = Math.max(90, name.length * 6 + 26);
    const p = panel(this, 0, 0, w, 20, 'dark');
    const t = txt(this, w / 2, 5, name, { align: 'center', color: 'gold' });
    this.bannerC.add([p, t]);
    this.bannerC.setPosition(8, -26);
    this.tweens.killTweensOf(this.bannerC);
    this.tweens.chain({
      targets: this.bannerC,
      tweens: [
        { y: 8, duration: 280, ease: 'Back.easeOut' },
        { y: 8, duration: 1800 },
        { y: -26, duration: 260, ease: 'Sine.easeIn' },
      ],
    });
  }

  // Resting: the screen closes like eyelids (a drowsy blink, then shut), stays dark while
  // `during()` runs (e.g. the heal jingle), then the eyes open again with a couple of blinks.
  async sleep(during) {
    const tw = (cfg) => new Promise((r) => this.tweens.add({ ...cfg, onComplete: r }));
    const half = GAME_H / 2 + 2;
    const top = this.add.rectangle(0, -half, GAME_W, half, 0x050409).setOrigin(0, 0).setDepth(200);
    const bot = this.add.rectangle(0, GAME_H, GAME_W, half, 0x050409).setOrigin(0, 0).setDepth(200);
    const lids = (k, duration, ease = 'Sine.easeInOut') => Promise.all([
      tw({ targets: top, y: -half + half * k, duration, ease }),
      tw({ targets: bot, y: GAME_H - half * k, duration, ease }),
    ]);
    await lids(0.55, 420);           // eyes getting heavy...
    await lids(0.3, 260);
    await lids(1, 520, 'Quad.easeIn'); // ...and shut
    const z = txt(this, GAME_W / 2, GAME_H / 2 - 4, 'z z z', { align: 'center', color: 'gray' }).setDepth(201).setAlpha(0);
    this.tweens.add({ targets: z, alpha: 0.8, y: GAME_H / 2 - 10, duration: 700, yoyo: true, repeat: 1 });
    await Promise.all([during ? during() : null, new Promise((r) => this.time.delayedCall(1600, r))]);
    z.destroy();
    await lids(0.35, 380, 'Quad.easeOut');  // blink awake
    await lids(0.8, 160);
    await lids(0, 420, 'Quad.easeOut');
    top.destroy(); bot.destroy();
  }

  // Healing at a Haven: the team's capsules appear, their health bars refill with a chime.
  async healPanel(party, doHeal) {
    const n = party.length;
    const w = Math.max(200, 20 + n * 70), h = 92;
    const x0 = (GAME_W - w) / 2, y0 = 34;
    const c = this.add.container(0, 0).setDepth(150).setAlpha(0);
    c.add(panel(this, x0, y0, w, h, 'dark'));
    c.add(txt(this, GAME_W / 2, y0 + 7, 'Healing your team...', { align: 'center', color: 'gold' }));
    const bars = party.map((m, i) => {
      const cx = x0 + 10 + 35 + i * ((w - 20) / n);
      c.add(this.add.image(cx, y0 + 44, 'mons', monFrame(m, 'i')).setScale(1.1));
      c.add(txt(this, cx, y0 + 64, monName(m).slice(0, 9), { align: 'center', face: 'small' }));
      const bar = new Bar(this, cx - 24, y0 + 76, 48, 4);
      bar.set(m.hp / maxHp(m)); bar.addTo(c);
      return { bar, cx };
    });
    await new Promise((r) => this.tweens.add({ targets: c, alpha: 1, duration: 200, onComplete: r }));
    const jingle = doHeal();
    await Promise.all(bars.map(({ bar, cx }, i) => new Promise((r) => this.time.delayedCall(i * 160, async () => {
      for (let k = 0; k < 6; k++) {
        const sp = this.add.image(cx + (Math.random() - 0.5) * 30, y0 + 50 + (Math.random() - 0.5) * 20, 'p_star').setDepth(151).setTint(0x8af0c8);
        c.add(sp);
        this.tweens.add({ targets: sp, y: sp.y - 16, alpha: 0, duration: 600, delay: k * 70, onComplete: () => sp.destroy() });
      }
      await bar.tweenTo(1, 700);
      r();
    }))));
    await jingle;
    c.list[1].setText('Your team is fully healed!');
    await new Promise((r) => this.time.delayedCall(700, r));
    await new Promise((r) => this.tweens.add({ targets: c, alpha: 0, duration: 250, onComplete: r }));
    c.destroy();
  }

  toast(text, color = 'white') {
    const w = text.length * 6 + 22;
    const c = this.add.container(GAME_W - w - 8, GAME_H + 4).setDepth(95);
    c.add([panel(this, 0, 0, w, 20, 'dark'), txt(this, 11, 5, text, { color })]);
    this.tweens.chain({ targets: c, tweens: [{ y: GAME_H - 28 - this.toasts.length * 22, duration: 220, ease: 'Back.easeOut' }, { alpha: 1, duration: 1600 }, { alpha: 0, duration: 250 }], onComplete: () => { c.destroy(); this.toasts = this.toasts.filter((x) => x !== c); } });
    this.toasts.push(c);
  }
}
