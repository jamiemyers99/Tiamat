import Phaser from 'phaser';
import { buildSkin } from '../ui/skin.js';

const COLORS = ['white', 'dark', 'gold', 'red', 'green', 'blue', 'gray', 'ink'];

export class BootScene extends Phaser.Scene {
  constructor() { super('Boot'); }

  preload() {
    for (const face of ['main', 'small']) {
      for (const c of COLORS) {
        this.load.bitmapFont(`${face}_${c}`, `assets/fonts/${face}_${c}.png`, `assets/fonts/${face}_${c}.xml`);
      }
    }
    this.load.json('mapIndex', 'assets/maps/index.json');
    this.load.json('charIndex', 'assets/sprites/chars.json');
    this.load.json('audioIndex', 'assets/audio/index.json');
  }

  create() {
    buildSkin(this);
    this.scene.start('Preload');
  }
}
