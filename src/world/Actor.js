// A character on the overworld: player or NPC.
import { TILE, DEPTH } from '../config.js';

export const DIRS = { down: [0, 1], up: [0, -1], left: [-1, 0], right: [1, 0] };
const DIR_ROW = { down: 0, left: 1, right: 2, up: 3 };
export const OPP = { up: 'down', down: 'up', left: 'right', right: 'left' };

export class Actor {
  constructor(scene, sprite, x, y, face = 'down') {
    this.scene = scene;
    const idx = scene.cache.json.get('charIndex');
    this.row = idx[sprite] ?? 0;
    this.spriteKey = sprite;
    this.tx = x; this.ty = y;
    this.face = face;
    this.moving = false;
    this.step = 0;
    this.sprite = scene.add.sprite(0, 0, 'chars', 0).setOrigin(0.5, 1);
    this.skiff = null;
    this.hidden = false;
    this._place();
    this._frame(0);
  }

  setSprite(key) {
    const idx = this.scene.cache.json.get('charIndex');
    this.row = idx[key] ?? this.row;
    this.spriteKey = key;
    this._frame(0);
  }

  _frame(f) {
    this.sprite.setFrame(this.row * 12 + DIR_ROW[this.face] * 3 + f);
  }

  _place() {
    this.sprite.x = this.tx * TILE + 8;
    this.sprite.y = this.ty * TILE + TILE;
    this._depth();
  }

  _depth() {
    this.sprite.setDepth(DEPTH.actors + this.sprite.y / 100);
    if (this.skiff) {
      this.skiff.setPosition(this.sprite.x, this.sprite.y + 1).setDepth(this.sprite.depth - 0.01);
    }
  }

  setFace(dir) { this.face = dir; this._frame(0); }

  warp(x, y, face) {
    this.tx = x; this.ty = y;
    if (face) { this.face = face; }
    this.moving = false;
    this._place();
    this._frame(0);
  }

  // Walk one tile in `dir` over `ms`. Resolves when finished.
  walk(dir, ms) {
    const [dx, dy] = DIRS[dir];
    this.face = dir;
    this.moving = true;
    this.step = (this.step + 1) % 2;
    const sx = this.sprite.x, sy = this.sprite.y;
    this.tx += dx; this.ty += dy;
    return new Promise((resolve) => {
      let t = 0;
      const upd = (time, delta) => {
        t += delta;
        const k = Math.min(1, t / ms);
        this.sprite.x = sx + dx * TILE * k;
        this.sprite.y = sy + dy * TILE * k;
        this._frame(k < 0.5 ? 1 + this.step : 0);
        this._depth();
        if (k >= 1) {
          this.scene.events.off('update', upd);
          this.moving = false;
          this._place();
          resolve();
        }
      };
      this.scene.events.on('update', upd);
    });
  }

  // Hop over a ledge: move `tiles` in dir with an arc.
  hop(dir, tiles = 2, ms = 420) {
    const [dx, dy] = DIRS[dir];
    this.face = dir;
    this.moving = true;
    const sx = this.sprite.x, sy = this.sprite.y;
    this.tx += dx * tiles; this.ty += dy * tiles;
    const shadow = this.scene.add.image(sx, sy - 1, 'shadow').setDepth(this.sprite.depth - 0.02);
    return new Promise((resolve) => {
      let t = 0;
      const upd = (time, delta) => {
        t += delta;
        const k = Math.min(1, t / ms);
        const bx = sx + dx * TILE * tiles * k;
        const by = sy + dy * TILE * tiles * k;
        const arc = Math.sin(k * Math.PI) * 10;
        this.sprite.x = bx; this.sprite.y = by - arc;
        shadow.setPosition(bx, by - 1);
        this._frame(k < 0.5 ? 1 : 2);
        this._depth();
        if (k >= 1) {
          this.scene.events.off('update', upd);
          shadow.destroy();
          this.moving = false;
          this._place();
          this._frame(0);
          resolve();
        }
      };
      this.scene.events.on('update', upd);
    });
  }

  emote(kind = '!', ms = 700) {
    const e = this.scene.add.image(this.sprite.x, this.sprite.y - 26, `emote_${kind}`).setOrigin(0.5, 1).setDepth(DEPTH.fx);
    e.setScale(0.2);
    this.scene.tweens.add({ targets: e, scale: 1, duration: 140, ease: 'Back.easeOut' });
    return new Promise((resolve) => {
      this.scene.time.delayedCall(ms, () => { e.destroy(); resolve(); });
    });
  }

  setSkiff(on) {
    if (on && !this.skiff) {
      this.skiff = this.scene.add.image(this.sprite.x, this.sprite.y, 'ui', 'skiff').setOrigin(0.5, 1);
      this.sprite.setCrop(0, 0, 16, 17);
    } else if (!on && this.skiff) {
      this.skiff.destroy(); this.skiff = null;
      this.sprite.setCrop();
    }
    this._depth();
  }

  setVisible(v) { this.hidden = !v; this.sprite.setVisible(v); if (this.skiff) { this.skiff.setVisible(v); } }

  facingTile() {
    const [dx, dy] = DIRS[this.face];
    return [this.tx + dx, this.ty + dy];
  }

  destroy() { this.sprite.destroy(); if (this.skiff) { this.skiff.destroy(); } }
}
