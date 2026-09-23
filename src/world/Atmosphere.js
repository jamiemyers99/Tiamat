// Day/night lighting and weather effects for the overworld.
import Phaser from 'phaser';
import { GAME_W, GAME_H, DEPTH } from '../config.js';
import { timeOfDay } from '../core/time.js';

// ambient multiply colour by minute of day
const KEYS = [
  [0, [58, 66, 128]],
  [300, [58, 66, 128]],
  [360, [255, 196, 170]],
  [420, [255, 255, 255]],
  [1050, [255, 255, 255]],
  [1110, [255, 184, 140]],
  [1170, [150, 120, 170]],
  [1230, [72, 78, 140]],
  [1440, [58, 66, 128]],
];

export function ambientAt(minute) {
  const m = ((minute % 1440) + 1440) % 1440;
  for (let i = 0; i < KEYS.length - 1; i++) {
    const [a, ca] = KEYS[i], [b, cb] = KEYS[i + 1];
    if (m >= a && m <= b) {
      const t = (m - a) / Math.max(1, b - a);
      return ca.map((v, k) => Math.round(v + (cb[k] - v) * t));
    }
  }
  return [255, 255, 255];
}

export { timeOfDay };

export class Lighting {
  constructor(scene) {
    this.scene = scene;
    this.rt = scene.add.renderTexture(0, 0, GAME_W, GAME_H).setOrigin(0, 0).setScrollFactor(0).setDepth(DEPTH.light);
    this.rt.setBlendMode(Phaser.BlendModes.MULTIPLY);
    this.brush = scene.make.image({ key: 'glow', add: false });
    this.glows = scene.add.container(0, 0).setDepth(DEPTH.light + 1);
    this.glowPool = [];
    this.mode = 'outdoor';
    this.darkness = null;
  }

  // mode: 'outdoor' | 'indoor' | 'dark'
  setMode(mode) { this.mode = mode; }

  update(minute, lights, cam, player, weatherDim = 0) {
    let amb;
    if (this.mode === 'indoor') {
      amb = [255, 255, 255];
    } else if (this.mode === 'dark') {
      amb = [26, 24, 48];
    } else {
      amb = ambientAt(minute);
    }
    if (weatherDim && this.mode === 'outdoor') {
      amb = amb.map((v) => Math.round(v * (1 - weatherDim)));
    }
    const isPlain = amb[0] > 250 && amb[1] > 250 && amb[2] > 250;
    this.rt.setVisible(!isPlain);
    const night = this.mode === 'dark' || (this.mode === 'outdoor' && (amb[0] + amb[1] + amb[2]) < 560);
    let gi = 0;
    if (!isPlain) {
      this.rt.clear();
      this.rt.fill(Phaser.Display.Color.GetColor(amb[0], amb[1], amb[2]), 1);
      const lit = [];
      if (night) {
        for (const l of lights) { lit.push(l); }
      }
      if (this.mode === 'dark' && player) {
        lit.push({ px: player.sprite.x, py: player.sprite.y - 8, props: { r: 64 } });
      }
      for (const l of lit) {
        const x = (l.px ?? l.x) - cam.scrollX, y = (l.py ?? l.y) - cam.scrollY;
        const r = (l.props && l.props.r) || 40;
        if (x < -r || y < -r || x > GAME_W + r || y > GAME_H + r) { continue; }
        this.brush.setScale((r * 2) / 64);
        this.brush.setAlpha(l.props && l.props.window ? 0.8 : 1);
        this.rt.erase(this.brush, x, y);
        if (night && this.mode === 'outdoor') {
          let g = this.glowPool[gi];
          if (!g) { g = this.scene.add.image(0, 0, 'glow').setBlendMode(Phaser.BlendModes.ADD); this.glows.add(g); this.glowPool.push(g); }
          const col = Phaser.Display.Color.HexStringToColor((l.props && l.props.color) || '#ffd98a');
          g.setTint(col.color).setAlpha(l.props && l.props.window ? 0.28 : 0.42).setScale((r * 1.1) / 64).setPosition(l.px ?? l.x, l.py ?? l.y).setVisible(true);
          gi++;
        }
      }
    }
    for (let i = gi; i < this.glowPool.length; i++) { this.glowPool[i].setVisible(false); }
  }

  destroy() { this.rt.destroy(); this.glows.destroy(); }
}

export class Weather {
  constructor(scene) {
    this.scene = scene;
    this.kind = 'none';
    this.objs = [];
    this.dim = 0;
  }

  set(kind) {
    if (kind === this.kind) { return; }
    this.clear();
    this.kind = kind || 'none';
    const s = this.scene;
    const zone = { source: new Phaser.Geom.Rectangle(-40, -20, GAME_W + 80, 10) };
    if (this.kind === 'rain') {
      this.dim = 0.25;
      const e = s.add.particles(0, 0, 'p_rain', {
        emitZone: zone, lifespan: 700, speedY: { min: 330, max: 420 }, speedX: { min: -70, max: -50 },
        quantity: 3, frequency: 16, alpha: { start: 0.8, end: 0.5 }, rotate: 10,
      }).setScrollFactor(0).setDepth(DEPTH.weather);
      const sp = s.add.particles(0, 0, 'p_ring', {
        emitZone: { source: new Phaser.Geom.Rectangle(0, 0, GAME_W, GAME_H) }, lifespan: 300, scale: { start: 0.2, end: 0.8 },
        alpha: { start: 0.5, end: 0 }, quantity: 1, frequency: 40,
      }).setScrollFactor(0).setDepth(DEPTH.weatherLow);
      this.objs.push(e, sp);
    } else if (this.kind === 'snow') {
      this.dim = 0.08;
      const e = s.add.particles(0, 0, 'p_snow', {
        emitZone: zone, lifespan: 6000, speedY: { min: 18, max: 40 }, speedX: { min: -18, max: 12 },
        quantity: 1, frequency: 70, alpha: { start: 1, end: 0.6 }, scale: { min: 0.8, max: 1.5 },
      }).setScrollFactor(0).setDepth(DEPTH.weather);
      this.objs.push(e);
    } else if (this.kind === 'fog') {
      this.dim = 0.12;
      const f = s.add.tileSprite(0, 0, GAME_W, GAME_H, 'fog').setOrigin(0, 0).setScrollFactor(0).setDepth(DEPTH.weather).setAlpha(0.55);
      const f2 = s.add.tileSprite(0, 0, GAME_W, GAME_H, 'fog').setOrigin(0, 0).setScrollFactor(0).setDepth(DEPTH.weather).setAlpha(0.35).setTileScale(2);
      this.fog = [f, f2];
      this.objs.push(f, f2);
    } else if (this.kind === 'leaves') {
      const e = s.add.particles(0, 0, 'p_leaf', {
        emitZone: { source: new Phaser.Geom.Rectangle(GAME_W, -20, 20, GAME_H * 0.7) }, lifespan: 7000,
        speedX: { min: -60, max: -30 }, speedY: { min: 10, max: 30 }, rotate: { start: 0, end: 360 }, quantity: 1, frequency: 700,
      }).setScrollFactor(0).setDepth(DEPTH.weather);
      this.objs.push(e);
    } else if (this.kind === 'ash') {
      this.dim = 0.15;
      const e = s.add.particles(0, 0, 'p_sq', {
        emitZone: zone, lifespan: 7000, speedY: { min: 10, max: 25 }, speedX: { min: -10, max: 10 },
        quantity: 1, frequency: 90, tint: [0x9a9aa8, 0x6a6a78], alpha: { start: 0.8, end: 0.2 },
      }).setScrollFactor(0).setDepth(DEPTH.weather);
      this.objs.push(e);
    } else if (this.kind === 'sparkle') {
      this.dim = 0.1;
      const e = s.add.particles(0, 0, 'p_star', {
        emitZone: { source: new Phaser.Geom.Rectangle(0, 0, GAME_W, GAME_H) }, lifespan: 1800, speedY: { min: -12, max: -4 },
        quantity: 1, frequency: 160, tint: [0xb89aff, 0x6fe0c8, 0xffffff], alpha: { start: 0, end: 0, ease: 'Sine.easeInOut', steps: 0 },
        scale: { start: 0.6, end: 1 },
      }).setScrollFactor(0).setDepth(DEPTH.weather);
      e.setParticleAlpha({ onEmit: () => 0, onUpdate: (p, k, t) => Math.sin(t * Math.PI) * 0.9 });
      this.objs.push(e);
    } else {
      this.dim = 0;
    }
  }

  update(delta, cam) {
    if (this.fog) {
      this.fog[0].tilePositionX = cam.scrollX * 0.6 + this.scene.time.now * 0.006;
      this.fog[0].tilePositionY = cam.scrollY * 0.6;
      this.fog[1].tilePositionX = cam.scrollX * 0.3 - this.scene.time.now * 0.004;
      this.fog[1].tilePositionY = cam.scrollY * 0.3 + this.scene.time.now * 0.002;
    }
  }

  clear() {
    this.objs.forEach((o) => o.destroy());
    this.objs = [];
    this.fog = null;
    this.kind = 'none';
    this.dim = 0;
  }
}
