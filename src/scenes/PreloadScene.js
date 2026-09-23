import Phaser from 'phaser';
import { GAME_W, GAME_H } from '../config.js';
import { txt } from '../ui/text.js';

export class PreloadScene extends Phaser.Scene {
  constructor() { super('Preload'); }

  preload() {
    const bar = this.add.rectangle(GAME_W / 2 - 100, GAME_H / 2 + 10, 0, 4, 0xffd65c).setOrigin(0, 0.5);
    this.add.rectangle(GAME_W / 2, GAME_H / 2 + 10, 204, 8, 0x262a47).setDepth(-1);
    txt(this, GAME_W / 2, GAME_H / 2 - 12, 'TIAMAT', { align: 'center', color: 'gold' });
    const pct = txt(this, GAME_W / 2, GAME_H / 2 + 20, '0%', { align: 'center', color: 'gray', face: 'small' });
    this.load.on('progress', (v) => { bar.width = 200 * v; pct.setText(`${Math.round(v * 100)}%`); });

    this.load.image('tiles_world', 'assets/tilesets/world.png');
    this.load.image('tiles_meta', 'assets/tilesets/meta.png');
    const maps = this.cache.json.get('mapIndex') || {};
    for (const id of Object.keys(maps)) {
      this.load.tilemapTiledJSON(`map_${id}`, `assets/maps/${id}.tmj`);
    }
    this.load.spritesheet('chars', 'assets/sprites/chars.png', { frameWidth: 16, frameHeight: 24 });
    this.load.atlas('ui', 'assets/ui/ui.png', 'assets/ui/ui.json');
    this.load.atlas('mons', 'assets/sprites/mons.png', 'assets/sprites/mons.json');
    this.load.atlas('icons', 'assets/sprites/icons.png', 'assets/sprites/icons.json');
    for (const b of ['meadow', 'forest', 'coast', 'cave', 'moor', 'snow', 'town', 'arena', 'rift', 'night', 'water', 'chapel']) {
      this.load.image(`bg_${b}`, `assets/battle/${b}.png`);
    }
    this.load.image('regionmap', 'assets/ui/regionmap.png');
    const audioIdx = this.cache.json.get('audioIndex') || { bgm: [], sfx: [] };
    for (const k of audioIdx.bgm) { this.load.audio(`bgm_${k}`, `assets/audio/bgm/${k}.ogg`); }
    for (const k of audioIdx.sfx) { this.load.audio(k, `assets/audio/sfx/${k}.ogg`); }
    this.load.on('loaderror', (f) => console.warn('[preload] failed', f.key));
  }

  create() {
    this.scene.launch('UI');
    const params = new URLSearchParams(location.search);
    if (params.has('map')) {
      this.scene.start('World', { debugMap: params.get('map'), x: +params.get('x') || null, y: +params.get('y') || null });
    } else {
      this.scene.start('Title');
    }
  }
}
