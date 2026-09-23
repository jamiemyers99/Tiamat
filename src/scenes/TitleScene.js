// Title screen with save-slot selection.
import Phaser from 'phaser';
import { GAME_W, GAME_H, SAVE_VERSION } from '../config.js';
import { input } from '../core/input.js';
import { audio } from '../core/audio.js';
import { G, newState, readSlot, loadGame, deleteSlot } from '../core/state.js';
import { txt } from '../ui/text.js';
import { panel, choose } from '../ui/widgets.js';
import { UI } from './UIScene.js';

export class TitleScene extends Phaser.Scene {
  constructor() { super('Title'); }

  create() {
    input.focus = ['title'];
    this.owner = 'title';
    // night sky gradient
    const g = this.add.graphics();
    for (let y = 0; y < GAME_H; y += 2) {
      const k = y / GAME_H;
      const c = Phaser.Display.Color.Interpolate.ColorWithColor({ r: 10, g: 10, b: 30 }, { r: 40, g: 34, b: 90 }, 100, k * 100);
      g.fillStyle(Phaser.Display.Color.GetColor(c.r, c.g, c.b), 1).fillRect(0, y, GAME_W, 2);
    }
    for (let i = 0; i < 90; i++) {
      const s = this.add.image(Math.random() * GAME_W, Math.random() * 150, 'px').setAlpha(0.3 + Math.random() * 0.7);
      this.tweens.add({ targets: s, alpha: 0.1, duration: 800 + Math.random() * 2000, yoyo: true, repeat: -1, delay: Math.random() * 2000 });
    }
    // moon
    this.add.circle(390, 60, 26, 0xf4ecd0).setAlpha(0.95);
    this.add.circle(398, 54, 22, 0x1c1a3a).setAlpha(0.35);
    // Tiamat silhouette rising from the sea
    this.tia = this.add.image(GAME_W / 2 + 70, 230, 'mons', 'tiamat_f').setScale(2.2).setOrigin(0.5, 1).setTint(0x16143a).setAlpha(0.95);
    this.tweens.add({ targets: this.tia, y: 222, duration: 3000, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
    const eyes = this.add.container(0, 0);
    // sea
    const sea = this.add.graphics();
    this.seaT = 0;
    this.events.on('update', (t, d) => {
      this.seaT += d;
      sea.clear();
      for (let row = 0; row < 8; row++) {
        const y = 196 + row * 10;
        sea.fillStyle(Phaser.Display.Color.GetColor(20 + row * 4, 28 + row * 6, 70 + row * 8), 1);
        sea.fillRect(0, y, GAME_W, 10);
        sea.fillStyle(0x6a8ae0, 0.5);
        for (let x = -20; x < GAME_W; x += 26) {
          const off = Math.sin((this.seaT / 600) + row + x * 0.05) * 6;
          sea.fillRect(x + off + (row % 2) * 13, y + 2, 10, 1);
        }
      }
    });
    // logo
    const logoShadow = txt(this, GAME_W / 2 + 2, 44, 'TIAMAT', { align: 'center', color: 'dark', scale: 5 });
    logoShadow.setTint ? logoShadow.setAlpha(0.6) : null;
    this.logo = txt(this, GAME_W / 2, 40, 'TIAMAT', { align: 'center', color: 'gold', scale: 5 });
    this.sub = txt(this, GAME_W / 2, 98, 'Tales of the Riven Reach', { align: 'center', color: 'blue' });
    this.press = txt(this, GAME_W / 2, 150, input.isTouch ? 'Tap  A  to start' : 'Press  Z / Enter / Space', { align: 'center' });
    this.tweens.add({ targets: this.press, alpha: 0.2, duration: 700, yoyo: true, repeat: -1 });
    txt(this, GAME_W - 6, GAME_H - 10, 'v1.0', { face: 'small', color: 'gray', align: 'right' });
    if (input.isTouch) {
      // centred so the on-screen pad and buttons don't cover it
      txt(this, GAME_W / 2, GAME_H - 10, 'Pad to move · A to talk · B to go back', { face: 'small', color: 'gray', align: 'center' });
    } else {
      txt(this, 6, GAME_H - 10, 'An original game. Arrow keys / WASD to move.', { face: 'small', color: 'gray' });
    }
    audio.playMusic(this.cache.audio.exists('bgm_title') ? 'bgm_title' : 'bgm_rootmere', { restart: true });
    this.state = 'press';
    this.cameras.main.fadeIn(600);
  }

  update() {
    if (this.state === 'press' && (input.pressed('confirm') || input.pressed('menu'))) {
      audio.sfx('select');
      this.state = 'menu';
      this.press.destroy();
      this.mainMenu();
    }
  }

  slotInfo(i) {
    const s = readSlot(i);
    if (!s) { return { label: `Slot ${i + 1}  — Empty`, empty: true }; }
    if (s.corrupt) { return { label: `Slot ${i + 1}  — Damaged`, corrupt: true }; }
    const h = Math.floor(s.playMs / 3600000), m = Math.floor((s.playMs % 3600000) / 60000);
    return { label: `${s.player.name}`, right: `${s.sigils.length}★  ${h}:${String(m).padStart(2, '0')}`, s };
  }

  async mainMenu() {
    for (;;) {
      const slots = [0, 1, 2].map((i) => this.slotInfo(i));
      const any = slots.some((s) => s.s);
      const items = [];
      if (any) { items.push({ label: 'Continue', value: 'continue' }); }
      items.push({ label: 'New Game', value: 'new' });
      items.push({ label: 'Options', value: 'options' });
      input.focus = ['title'];
      const v = await choose(this, items, { x: GAME_W / 2 - 50, y: 120, width: 100, cancellable: false });
      if (v === 'continue') {
        const pick = await this.pickSlot(slots, 'Continue which journey?', false);
        if (pick === null) { continue; }
        if (loadGame(pick)) { this.start(false); return; }
      } else if (v === 'new') {
        const pick = await this.pickSlot(slots, 'Start in which slot?', true);
        if (pick === null) { continue; }
        if (slots[pick].s || slots[pick].corrupt) {
          const ok = await choose(this, [{ label: 'Overwrite', value: true }, { label: 'Cancel', value: false }], { x: GAME_W / 2 - 50, y: 150, width: 100 });
          if (!ok) { continue; }
          deleteSlot(pick);
        }
        G.state = newState();
        G.slot = pick;
        this.start(true);
        return;
      } else if (v === 'options') {
        this.scene.launch('Menu', { mode: 'options', onClose: () => {} });
        this.scene.bringToTop('Menu');
        await new Promise((r) => { const ev = () => { if (!this.scene.isActive('Menu')) { this.events.off('update', ev); r(); } }; this.events.on('update', ev); });
        input.focus = ['title'];
      }
    }
  }

  async pickSlot(slots, title, allowEmpty) {
    const t = txt(this, GAME_W / 2, 104, title, { align: 'center', color: 'gold' });
    const items = slots.map((s, i) => ({ label: s.label, right: s.right || '', value: i, disabled: !allowEmpty && !s.s }));
    const v = await choose(this, items, { x: GAME_W / 2 - 100, y: 120, width: 200 });
    t.destroy();
    return v;
  }

  start(isNew) {
    audio.sfx('select');
    this.cameras.main.fadeOut(500, 0, 0, 0);
    this.cameras.main.once('camerafadeoutcomplete', () => {
      if (isNew) { this.scene.start('Intro'); }
      else { input.focus = ['world']; this.scene.start('World'); }
    });
  }
}
