// End credits.
import Phaser from 'phaser';
import { GAME_W, GAME_H } from '../config.js';
import { input } from '../core/input.js';
import { audio } from '../core/audio.js';
import { G } from '../core/state.js';
import { txt } from '../ui/text.js';

const LINES = [
  ['TIAMAT', 'gold'], [''], ['Tales of the Riven Reach', 'blue'], [''],
  ['Created by', 'gray'], ['Myro'], [''],
  ['Design, code, art & story', 'gray'], ['Myro with Claude'], [''],
  ['Music & sound', 'gray'], ['Tiamat audio pack + original chiptunes'], [''],
  ['Built with', 'gray'], ['Phaser 3, Vite, Tiled'], [''],
  ['Morphs catalogued', 'gray'], ['{CAUGHT} of 68'], [''],
  ['Special thanks', 'gray'], ['Everyone who played this far.'], [''], [''],
  ['The sea sleeps. The Reach remembers.', 'gold'], [''], ['THE END'],
];

export class CreditsScene extends Phaser.Scene {
  constructor() { super('Credits'); }
  init(data) { this.cfg = data || {}; }
  create() {
    input.push('credits');
    this.cameras.main.setBackgroundColor('#0c0b14');
    audio.playMusic(this.cache.audio.exists('bgm_crown') ? 'bgm_crown' : 'bgm_title', { restart: true });
    const c = this.add.container(0, GAME_H + 10);
    LINES.forEach(([t, col], i) => {
      c.add(txt(this, GAME_W / 2, i * 18, t.replace('{CAUGHT}', G.state.index.caught.length), { align: 'center', color: col || 'white', scale: i === 0 ? 3 : 1 }));
    });
    const pics = ['spriglet', 'cindlet', 'puddlet', 'tiamat'];
    pics.forEach((p, i) => c.add(this.add.image(i % 2 ? GAME_W - 70 : 70, 120 + i * 110, 'mons', `${p}_f`).setOrigin(0.5)));
    this.tweens.add({ targets: c, y: -LINES.length * 18 - 40, duration: LINES.length * 1100, ease: 'Linear', onComplete: () => this.finish() });
    this.c = c;
  }
  update() {
    if (input.pressed('confirm', 'credits') && this.c) { this.tweens.timeScale = 4; }
  }
  finish() {
    input.pop('credits');
    this.tweens.timeScale = 1;
    this.cfg.onDone ? this.cfg.onDone() : this.scene.start('Title');
    this.scene.stop();
  }
}
