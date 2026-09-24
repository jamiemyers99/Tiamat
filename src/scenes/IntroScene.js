// New-game intro: Dr. Marsh welcomes the player, style + name selection.
import Phaser from 'phaser';
import { GAME_W, GAME_H } from '../config.js';
import { input } from '../core/input.js';
import { audio } from '../core/audio.js';
import { G } from '../core/state.js';
import { txt } from '../ui/text.js';
import { UI } from './UIScene.js';
import { PLAYER_STYLES, STYLES_FOR } from '../data/players.js';
import { nameEntry } from '../ui/nameEntry.js';

const NAMES = ['Rowan', 'Aoife', 'Kai', 'Nia', 'Finn', 'Maeve', 'Ash', 'Robin'];

export class IntroScene extends Phaser.Scene {
  constructor() { super('Intro'); }

  async create() {
    input.focus = ['intro'];
    this.add.rectangle(0, 0, GAME_W, GAME_H, 0x141627).setOrigin(0, 0);
    const g = this.add.graphics();
    g.fillStyle(0x1b1e33, 1).fillCircle(GAME_W / 2, 130, 110);
    g.fillStyle(0x222640, 1).fillCircle(GAME_W / 2, 130, 80);
    const idx = this.cache.json.get('charIndex');
    this.marsh = this.add.image(GAME_W / 2, 150, 'chars', idx.marsh * 12).setScale(3).setOrigin(0.5, 1).setAlpha(0);
    this.cameras.main.fadeIn(600);
    audio.playMusic('bgm_haven', { restart: true });
    await this.tween({ targets: this.marsh, alpha: 1, duration: 600 });
    const M = 'Dr. Marsh';
    await UI.say(M, "Oh! Hello there. Welcome to the Riven Reach!");
    await UI.say(M, "My name is Ione Marsh. The folk around Rootmere call me the Morph Doctor.");
    // show a Morph
    const mon = this.add.image(GAME_W / 2 + 70, 150, 'mons', 'spriglet_f').setOrigin(0.5, 1).setScale(0).setDepth(2);
    await this.tween({ targets: this.marsh, x: GAME_W / 2 - 40, duration: 400 });
    audio.sfx('select');
    await this.tween({ targets: mon, scale: 1, duration: 300, ease: 'Back.easeOut' });
    audio.cry(1);
    await UI.say(M, "This little one is a Morph. The Reach is full of them — in the grass, the rivers, the old mines, even the fog on the moors.");
    await UI.say(M, "People and Morphs have lived side by side here for as long as there are stories. Some folk tame them, train with them, and take on the Trials.");
    await UI.say(M, "And the oldest story of all says the Reach itself was made from a Morph called Tiamat... but that's a tale for another day.");
    await this.tween({ targets: mon, alpha: 0, duration: 300 });
    mon.destroy();
    await UI.say(M, "Now, let me get a proper look at you.");
    // boy or girl, then one of four looks (B goes back to the question)
    let style = null, me = null;
    while (style === null) {
      const girl = await UI.ask(M, 'First things first — are you a boy or a girl?', 'Boy', 'Girl') === false;
      const sex = girl ? 'f' : 'm';
      const opts = STYLES_FOR[sex];
      const previews = opts.map((st, i) => this.add.image(GAME_W / 2 - 90 + i * 60, 150, 'chars', idx[PLAYER_STYLES[st]] * 12).setScale(2).setOrigin(0.5, 1).setAlpha(0));
      if (this.marsh.alpha > 0) { await this.tween({ targets: this.marsh, alpha: 0, duration: 300 }); }
      previews.forEach((p) => this.tweens.add({ targets: p, alpha: 0.5, duration: 300 }));
      const sel = this.add.rectangle(0, 0, 50, 70).setStrokeStyle(2, 0xffd65c).setOrigin(0.5, 1);
      UI.say(M, 'Which one is you?', { keepOpen: true });
      const pick = await this.pickStyle(previews, sel);
      UI.hideBox();
      sel.destroy();
      if (pick === null) { previews.forEach((p) => p.destroy()); continue; }
      style = opts[pick];
      G.state.player.style = style;
      G.state.player.gender = sex;
      previews.forEach((p, i) => { if (i !== pick) { p.destroy(); } });
      me = previews[pick];
    }
    this.tweens.add({ targets: me, x: GAME_W / 2, alpha: 1, duration: 300 });
    await UI.say(M, "And what's your name?");
    const name = await this.nameEntry();
    G.state.player.name = name;
    await UI.say(M, `${name}! What a fine name.`);
    await UI.say(M, `Your neighbour, my grandchild Wren, has been counting down the days until you both turn old enough to tame a Morph.`);
    await UI.say(M, `Well, ${name} — today's that day. Come by the lab once you're up and about. Your very own adventure is about to begin!`);
    await this.tween({ targets: me, scale: 0.5, alpha: 0, duration: 700 });
    this.cameras.main.fadeOut(600, 0, 0, 0);
    this.cameras.main.once('camerafadeoutcomplete', () => {
      G.state.flags.intro_done = true;
      input.focus = ['world'];
      this.scene.start('World');
    });
  }

  tween(cfg) { return new Promise((r) => this.tweens.add({ ...cfg, onComplete: r })); }

  pickStyle(previews, sel) {
    let i = 0;
    const draw = () => {
      previews.forEach((p, k) => p.setAlpha(k === i ? 1 : 0.45));
      sel.setPosition(previews[i].x, previews[i].y + 2);
    };
    draw();
    return new Promise((resolve) => {
      const tick = () => {
        if (input.nav('left')) { i = (i + previews.length - 1) % previews.length; audio.sfx('cursor'); draw(); }
        else if (input.nav('right')) { i = (i + 1) % previews.length; audio.sfx('cursor'); draw(); }
        else if (input.pressed('confirm')) { this.events.off('update', tick); audio.sfx('select'); resolve(i); }
        else if (input.pressed('cancel')) { this.events.off('update', tick); audio.sfx('cancel'); resolve(null); }
      };
      this.events.on('update', tick);
    });
  }

  // On-screen keyboard + physical typing.
  nameEntry(max = 10) {
    return nameEntry(this, { title: 'Your name', max, randomNames: NAMES });
  }
}
