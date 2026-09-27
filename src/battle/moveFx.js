// Battle move animations. Every move plays a "recipe": a list of steps built from the effects below
// (lunges, slashes, jaws, beams, lightning, waves, falling rocks, rings, swirls, clouds, sparkles...).
// Common moves share recipes by kind (see data/moveAnims.js); signature moves have their own.
//
// A step is { op, ...params }. Steps run one after another; a step with `par: true` starts and the
// next one begins straight away (so effects can overlap). Positions: 'user' | 'foe' (sprite centres),
// 'userGround' | 'foeGround', 'mid' (between them), 'sky' (above the foe).
import Phaser from 'phaser';
import { GAME_W, GAME_H } from '../config.js';
import { audio } from '../core/audio.js';

const D_FX = 34;      // above both Morphs, below the HUD panels (40)
const D_TINT = 30;    // screen tints sit under the effects

// Colours per type: [main, light, dark]
export const TYPE_COL = {
  Plain: [0xf2f0ea, 0xffffff, 0xa8a29a], Nature: [0x5cc15a, 0xb8f07a, 0x2f7a3a], Ember: [0xff7a3d, 0xffd24a, 0xd0302a],
  Tide: [0x3d8bfd, 0x9ad8ff, 0x1f4aa8], Static: [0xf5d442, 0xfffbb0, 0xc89a1a], Stone: [0xb38b5d, 0xdcc49a, 0x6e5234],
  Frost: [0x8fe0ff, 0xf0fbff, 0x4aa6d8], Wing: [0xb8c8ff, 0xffffff, 0x7088d8], Swarm: [0xa8c83a, 0xe0f07a, 0x5a7a1a],
  Toxin: [0xb060d8, 0xe0a8ff, 0x6a2a8a], Brawl: [0xe86040, 0xffc0a0, 0x9a2a1a], Mind: [0xf06292, 0xffc0dc, 0xa02a5a],
  Umbra: [0x6a54a0, 0xb89aff, 0x201830], Iron: [0xb8c4d4, 0xffffff, 0x6a7488], Drake: [0x7a5ae8, 0x6fe0c8, 0x3a2a8a],
  Fae: [0xf7a8dc, 0xfff0fa, 0xd060a8],
};

const rnd = (a, b) => a + Math.random() * (b - a);

export class MoveFx {
  constructor(scene, { move, from, to, aSpr, dSpr, side }) {
    this.s = scene;
    this.move = move;
    this.from = from;          // attacker centre
    this.to = to;              // defender centre
    this.aSpr = aSpr;
    this.dSpr = dSpr;
    this.side = side;          // 0 = player attacking (enemy is up-right), 1 = enemy attacking
    this.col = TYPE_COL[move.type] || TYPE_COL.Plain;
    this.objs = [];
    this.pending = [];
  }

  // ── plumbing ──────────────────────────────────────────────────────────
  async run(steps) {
    for (const st of steps) {
      const fn = this[st.op];
      if (!fn) { continue; }
      const p = Promise.resolve(fn.call(this, st)).catch(() => {});
      if (st.par) { this.pending.push(p); } else { await p; }
    }
    await Promise.all(this.pending);
    this.cleanup();
  }

  cleanup() {
    for (const o of this.objs) { if (o && o.scene) { o.destroy(); } }
    this.objs = [];
    this.aSpr.setAngle(0);
    this.dSpr.setAngle(0);
  }

  at(where = 'foe') {
    if (typeof where === 'object') { return where; }
    const f = this.from, t = this.to;
    switch (where) {
      case 'user': return { x: f.x, y: f.y };
      case 'foe': return { x: t.x, y: t.y };
      case 'userGround': return { x: f.x, y: f.y + (this.side === 0 ? 50 : 40) };
      case 'foeGround': return { x: t.x, y: t.y + (this.side === 0 ? 40 : 50) };
      case 'mid': return { x: (f.x + t.x) / 2, y: (f.y + t.y) / 2 };
      case 'sky': return { x: t.x, y: -20 };
      case 'center': return { x: GAME_W / 2, y: GAME_H / 2 - 30 };
      default: return { x: t.x, y: t.y };
    }
  }

  color(c, i = 0) {
    if (c === undefined || c === null) { return this.col[i]; }
    if (Array.isArray(c)) { return c[i % c.length]; }
    if (typeof c === 'string') { return this.col[{ main: 0, light: 1, dark: 2 }[c] ?? 0]; }
    return c;
  }

  img(key, x, y, opts = {}) {
    const isFrame = key.startsWith('fx_') || key.startsWith('throw_') || key === 'item_ball';
    const o = isFrame ? this.s.add.image(x, y, 'ui', key) : this.s.add.image(x, y, key);
    o.setDepth(opts.depth ?? D_FX);
    if (opts.tint !== undefined && opts.tint !== false) { o.setTint(opts.tint); }
    if (opts.scale) { o.setScale(opts.scale); }
    if (opts.alpha !== undefined) { o.setAlpha(opts.alpha); }
    if (opts.add) { o.setBlendMode(Phaser.BlendModes.ADD); }
    this.objs.push(o);
    return o;
  }

  tw(cfg) { return new Promise((r) => this.s.tweens.add({ ...cfg, onComplete: r })); }
  wait({ ms = 100 }) { return new Promise((r) => this.s.time.delayedCall(ms, r)); }
  sprite(who) { return who === 'foe' ? this.dSpr : this.aSpr; }
  dir() { const dx = this.to.x - this.from.x, dy = this.to.y - this.from.y; const L = Math.hypot(dx, dy) || 1; return { x: dx / L, y: dy / L, ang: Math.atan2(dy, dx), len: L }; }

  sfx({ key, vol = 1, rate = 1 }) { audio.sfx(key, { volume: vol, rate, throttle: 0 }); }

  // ── attacker / target motion ──────────────────────────────────────────
  async lunge({ dist = 26, ms = 110, who = 'user' }) {
    const spr = this.sprite(who);
    const d = this.dir();
    const sx = spr.x, sy = spr.y;
    const k = who === 'user' ? 1 : -1;
    await this.tw({ targets: spr, x: sx + d.x * dist * k, y: sy + d.y * dist * k, duration: ms, yoyo: true, ease: 'Quad.easeOut' });
    spr.setPosition(sx, sy);
  }

  async hop({ h = 18, ms = 150, who = 'user', times = 1 }) {
    const spr = this.sprite(who);
    const sy = spr.y;
    for (let i = 0; i < times; i++) { await this.tw({ targets: spr, y: sy - h, duration: ms, yoyo: true, ease: 'Quad.easeOut' }); }
    spr.y = sy;
  }

  async spin({ who = 'user', turns = 1, ms = 400 }) {
    const spr = this.sprite(who);
    await this.tw({ targets: spr, angle: 360 * turns * (this.side === 0 ? 1 : -1), duration: ms, ease: 'Sine.easeInOut' });
    spr.setAngle(0);
  }

  async wobble({ who = 'foe', ms = 420, amp = 6, times = 4 }) {
    const spr = this.sprite(who);
    const sx = spr.x;
    await this.tw({ targets: spr, x: sx + amp, duration: ms / (times * 2), yoyo: true, repeat: times - 1, ease: 'Sine.easeInOut' });
    spr.x = sx;
  }

  async squash({ who = 'foe', ms = 180, amt = 0.25 }) {
    const spr = this.sprite(who);
    const sx = spr.scaleX, sy = spr.scaleY;
    await this.tw({ targets: spr, scaleY: sy * (1 - amt), scaleX: sx * (1 + amt * 0.6), duration: ms / 2, yoyo: true });
    spr.setScale(sx, sy);
  }

  // Attacker leaps off the top of the screen and plunges onto the foe.
  async dive({ ms = 520, color, trail = true }) {
    const spr = this.aSpr;
    const sx = spr.x, sy = spr.y;
    await this.tw({ targets: spr, y: sy - 160, alpha: 0, duration: ms * 0.35, ease: 'Quad.easeIn' });
    const t = this.at('foe');
    const streak = this.img('px', t.x, -10, { tint: this.color(color, 1), add: true }).setOrigin(0.5, 0).setScale(6, 1);
    if (trail) { await this.tw({ targets: streak, scaleY: t.y + 10, duration: ms * 0.3, ease: 'Quad.easeIn' }); }
    streak.destroy();
    spr.setPosition(sx, sy).setAlpha(1);
  }

  async glow({ who = 'user', color, ms = 380, pulses = 2 }) {
    const spr = this.sprite(who);
    const c = this.color(color);
    for (let i = 0; i < pulses; i++) {
      spr.setTintFill(c);
      await this.wait({ ms: ms / (pulses * 2) });
      spr.clearTint();
      await this.wait({ ms: ms / (pulses * 2) });
    }
  }

  async fade({ who = 'foe', to = 0.3, ms = 300 }) {
    const spr = this.sprite(who);
    await this.tw({ targets: spr, alpha: to, duration: ms / 2, yoyo: true });
    spr.setAlpha(1);
  }

  // ── screen effects ────────────────────────────────────────────────────
  shake({ amp = 0.01, ms = 220 }) { this.s.cameras.main.shake(ms, amp); return this.wait({ ms: Math.min(ms, 120) }); }

  async flash({ color = 0xffffff, alpha = 0.7, ms = 140 }) {
    const r = this.s.add.rectangle(0, 0, GAME_W, GAME_H, this.color(color), alpha).setOrigin(0, 0).setDepth(D_FX + 2);
    this.objs.push(r);
    await this.tw({ targets: r, alpha: 0, duration: ms });
    r.destroy();
  }

  async tint({ color, alpha = 0.35, ms = 600, hold = 200 }) {
    const r = this.s.add.rectangle(0, 0, GAME_W, GAME_H, this.color(color, 2), 0).setOrigin(0, 0).setDepth(D_TINT);
    this.objs.push(r);
    await this.tw({ targets: r, fillAlpha: alpha, duration: (ms - hold) / 2 });
    await this.wait({ ms: hold });
    await this.tw({ targets: r, fillAlpha: 0, duration: (ms - hold) / 2 });
    r.destroy();
  }

  // ── projectiles ───────────────────────────────────────────────────────
  async projectile({ key = 'fx_orb', count = 1, ms = 300, arc = 0, spin = 0, scale = 1.4, color, stagger = 45, spread = 6, from = 'user', to = 'foe', add = true, grow = 0, rotate = true }) {
    const a = this.at(from), b = this.at(to);
    const tint = this.color(color);
    const jobs = [];
    for (let i = 0; i < count; i++) {
      const o = this.img(key, a.x, a.y, { tint, scale, add });
      if (rotate && !spin) { o.setRotation(Math.atan2(b.y - a.y, b.x - a.x)); }
      const tx = b.x + rnd(-spread, spread), ty = b.y + rnd(-spread, spread);
      const p = { t: 0 };
      jobs.push(new Promise((res) => this.s.tweens.add({
        targets: p, t: 1, delay: i * stagger, duration: ms, ease: 'Sine.easeIn',
        onUpdate: () => {
          o.x = a.x + (tx - a.x) * p.t;
          o.y = a.y + (ty - a.y) * p.t - Math.sin(p.t * Math.PI) * arc;
          if (spin) { o.angle = p.t * 360 * spin; }
          if (grow) { o.setScale(scale * (1 + grow * p.t)); }
        },
        onComplete: () => { o.destroy(); res(); },
      })));
    }
    await Promise.all(jobs);
  }

  stream(o) { return this.projectile({ count: 14, stagger: 28, ms: 260, spread: 10, ...o }); }

  async beam({ w = 7, color, color2, ms = 480, from = 'user', to = 'foe', pulse = true }) {
    const a = this.at(from), b = this.at(to);
    const len = Math.hypot(b.x - a.x, b.y - a.y);
    const ang = Math.atan2(b.y - a.y, b.x - a.x);
    const outer = this.img('px', a.x, a.y, { tint: this.color(color), add: true }).setOrigin(0, 0.5).setRotation(ang).setScale(0, w);
    const inner = this.img('px', a.x, a.y, { tint: this.color(color2 ?? 0xffffff) }).setOrigin(0, 0.5).setRotation(ang).setScale(0, Math.max(1, w * 0.35));
    await this.tw({ targets: [outer, inner], scaleX: len, duration: ms * 0.3, ease: 'Quad.easeOut' });
    if (pulse) { this.s.tweens.add({ targets: outer, scaleY: w * 1.5, duration: 60, yoyo: true, repeat: Math.floor(ms * 0.5 / 120) }); }
    await this.wait({ ms: ms * 0.5 });
    await this.tw({ targets: [outer, inner], scaleY: 0, alpha: 0, duration: ms * 0.2 });
  }

  // Zig-zag lightning from the sky (or from the user) onto the target.
  async bolt({ from = 'sky', to = 'foe', count = 1, color, ms = 320, width = 3 }) {
    const b = this.at(to);
    for (let k = 0; k < count; k++) {
      const a = from === 'sky' ? { x: b.x + rnd(-20, 20), y: -10 } : this.at(from);
      const g = this.s.add.graphics().setDepth(D_FX + 1);
      this.objs.push(g);
      const pts = [a];
      const n = 7;
      for (let i = 1; i < n; i++) {
        const t = i / n;
        pts.push({ x: a.x + (b.x - a.x) * t + rnd(-12, 12), y: a.y + (b.y - a.y) * t + rnd(-4, 4) });
      }
      pts.push(b);
      const draw = (w, c, al) => { g.lineStyle(w, c, al); g.beginPath(); g.moveTo(pts[0].x, pts[0].y); for (const p of pts) { g.lineTo(p.x, p.y); } g.strokePath(); };
      draw(width * 3, this.color(color), 0.45);
      draw(width, 0xffffff, 1);
      await this.tw({ targets: g, alpha: 0.2, duration: 50, yoyo: true, repeat: 2 });
      await this.tw({ targets: g, alpha: 0, duration: ms * 0.4 });
      g.destroy();
    }
  }

  // ── at the target ─────────────────────────────────────────────────────
  burst({ key = 'p_star', count = 14, speed = 70, color, at = 'foe', scale = 1.8, life = 460, gravity = 0, frame }) {
    const p = this.at(at);
    const tints = Array.isArray(color) ? color : [this.color(color, 0), this.color(color, 1), this.color(color, 2)];
    const isFrame = key.startsWith('fx_');
    const em = this.s.add.particles(p.x, p.y, isFrame ? 'ui' : key, {
      ...(isFrame ? { frame: key } : {}), speed: { min: speed * 0.35, max: speed }, lifespan: life,
      scale: { start: scale, end: scale * 0.2 }, alpha: { start: 1, end: 0 }, tint: tints, emitting: false, gravityY: gravity,
      rotate: { min: 0, max: 360 },
    }).setDepth(D_FX + 1);
    this.objs.push(em);
    em.explode(count);
    return this.wait({ ms: Math.min(life, 260) });
  }

  async impact({ at = 'foe', scale = 1.3, color, ms = 220, key = 'fx_impact', ox = 0, oy = 0 }) {
    const p = this.at(at);
    const o = this.img(key, p.x + ox, p.y + oy, { tint: this.color(color, 1), scale: scale * 0.4, add: true });
    await this.tw({ targets: o, scale, alpha: 0, duration: ms, ease: 'Quad.easeOut' });
    o.destroy();
  }

  // One or more hits with a sprite (fist, foot, horn...) on the target.
  async hit({ key = 'fx_fist', count = 1, scale = 1.6, gap = 90, jitter = 14, color, at = 'foe' }) {
    const p = this.at(at);
    for (let i = 0; i < count; i++) {
      const x = p.x + rnd(-jitter, jitter), y = p.y + rnd(-jitter, jitter);
      const o = this.img(key, x, y, { tint: color === false ? undefined : this.color(color, 1), scale: scale * 1.6 });
      o.setFlipX(this.side === 1);
      this.impact({ at: { x, y }, scale: 1, color });
      await this.tw({ targets: o, scale, duration: 70, ease: 'Quad.easeIn' });
      await this.tw({ targets: o, alpha: 0, duration: gap });
      o.destroy();
    }
  }

  async slash({ key = 'fx_slash', count = 1, angle = -35, scale = 1.6, color, gap = 80, at = 'foe', cross = false }) {
    const p = this.at(at);
    for (let i = 0; i < count; i++) {
      const ang = cross && i % 2 ? 180 - angle : angle + (i % 2 ? 30 : 0);
      const o = this.img(key, p.x + rnd(-6, 6), p.y + rnd(-6, 6), { tint: this.color(color, 1), scale: scale * 0.6, add: true }).setAngle(ang);
      this.tw({ targets: o, scale, duration: 120, ease: 'Quad.easeOut' }).then(() => this.tw({ targets: o, alpha: 0, duration: 140 }));
      await this.wait({ ms: gap });
    }
    await this.wait({ ms: 160 });
  }

  async jaws({ color, at = 'foe', ms = 200, scale = 1.4, times = 1 }) {
    const p = this.at(at);
    for (let i = 0; i < times; i++) {
      const top = this.img('fx_jaw', p.x, p.y - 26, { tint: this.color(color, 1), scale });
      const bot = this.img('fx_jaw', p.x, p.y + 26, { tint: this.color(color, 1), scale }).setFlipY(true);
      await Promise.all([
        this.tw({ targets: top, y: p.y - 6, duration: ms, ease: 'Quad.easeIn' }),
        this.tw({ targets: bot, y: p.y + 6, duration: ms, ease: 'Quad.easeIn' }),
      ]);
      this.impact({ at: p, scale: 1.1, color });
      await this.tw({ targets: [top, bot], alpha: 0, duration: 160 });
      top.destroy(); bot.destroy();
    }
  }

  // Things dropping from above onto the target (rocks, ice, stars...).
  async fall({ keys = ['fx_rock0', 'fx_rock1', 'fx_rock2'], count = 5, ms = 380, spread = 30, color = false, scale = 1.6, stagger = 70, at = 'foe' }) {
    const p = this.at(at);
    const jobs = [];
    for (let i = 0; i < count; i++) {
      const key = keys[i % keys.length];
      const x = p.x + rnd(-spread, spread);
      const o = this.img(key, x, -20, { tint: color === false ? undefined : this.color(color, 1), scale }).setAngle(rnd(-30, 30));
      jobs.push(this.tw({ targets: o, y: p.y + rnd(-8, 16), angle: o.angle + rnd(-90, 90), delay: i * stagger, duration: ms, ease: 'Quad.easeIn' })
        .then(() => { this.impact({ at: { x: o.x, y: o.y }, scale: 0.9, color: color === false ? undefined : color }); return this.tw({ targets: o, alpha: 0, duration: 160 }); }));
    }
    await Promise.all(jobs);
  }

  // Things bursting up from the ground under the target (spikes, roots, flame pillars).
  async rise({ key = 'fx_icicle', count = 5, h = 34, color, scale = 1.6, stagger = 50, at = 'foeGround', flip = true }) {
    const p = this.at(at);
    const jobs = [];
    for (let i = 0; i < count; i++) {
      const x = p.x + (i - (count - 1) / 2) * 12 + rnd(-3, 3);
      const o = this.img(key, x, p.y + 6, { tint: this.color(color, 1), scale: scale * 0.3 }).setFlipY(flip && key === 'fx_icicle');
      jobs.push(this.tw({ targets: o, y: p.y - h * rnd(0.6, 1), scale, delay: i * stagger, duration: 180, ease: 'Back.easeOut' })
        .then(() => this.tw({ targets: o, alpha: 0, duration: 260, delay: 120 })));
    }
    await Promise.all(jobs);
  }

  async rings({ at = 'foe', count = 3, color, from = 0.5, to = 5, ms = 520, gap = 110, key = 'p_ring', add = true }) {
    const p = this.at(at);
    const jobs = [];
    for (let i = 0; i < count; i++) {
      const o = this.img(key, p.x, p.y, { tint: this.color(color, i % 2 ? 1 : 0), scale: from, add });
      jobs.push(this.tw({ targets: o, scale: to, alpha: 0, delay: i * gap, duration: ms, ease: 'Quad.easeOut' }));
    }
    await Promise.all(jobs);
  }

  // A wall of water / sludge / sand rolling from the user's side across the foe.
  async wave({ color, ms = 700, drops = 'fx_bubble', height = 1 }) {
    const a = this.at('userGround'), b = this.at('foeGround');
    const w = this.img('glow', a.x, a.y - 10, { tint: this.color(color), scale: 0.5, alpha: 0.85, add: true });
    w.setScale(1.4, 0.9 * height);
    const crest = this.img('glow', a.x, a.y - 30, { tint: this.color(color, 1), alpha: 0.9, add: true }).setScale(0.9, 0.35);
    const p = { t: 0 };
    await this.tw({
      targets: p, t: 1, duration: ms, ease: 'Sine.easeInOut',
      onUpdate: () => {
        const x = a.x + (b.x - a.x) * p.t, y = a.y + (b.y - a.y) * p.t;
        w.setPosition(x, y - 20 * height).setScale(1.4 + p.t * 0.8, (0.9 + Math.sin(p.t * Math.PI) * 0.5) * height);
        crest.setPosition(x + 6, y - 44 * height);
      },
    });
    this.burst({ key: drops, count: 16, speed: 90, color, at: 'foe', scale: 1.2, gravity: 160 });
    await this.tw({ targets: [w, crest], alpha: 0, duration: 260 });
  }

  // Sprites orbiting the target and closing in (leaves, whirlpool, fae lights).
  async swirl({ key = 'fx_leaf', count = 10, radius = 38, ms = 720, at = 'foe', color, spin = 1.5, close = true, scale = 1.5, add = false }) {
    const p = this.at(at);
    const items = [];
    for (let i = 0; i < count; i++) { items.push({ o: this.img(key, p.x, p.y, { tint: this.color(color, i % 3), scale, add }), a0: (i / count) * Math.PI * 2 }); }
    const s = { t: 0 };
    await this.tw({
      targets: s, t: 1, duration: ms, ease: 'Sine.easeIn',
      onUpdate: () => {
        const r = radius * (close ? 1 - s.t * 0.85 : 1);
        for (const it of items) {
          const a = it.a0 + s.t * Math.PI * 2 * spin;
          it.o.setPosition(p.x + Math.cos(a) * r, p.y + Math.sin(a) * r * 0.55);
          it.o.setRotation(a);
        }
      },
    });
    for (const it of items) { it.o.destroy(); }
  }

  // Particles falling across the target (or the whole screen).
  async rain({ key = 'p_rain', count = 26, ms = 700, area = 'foe', color, angle = 0.25, scale = 1.5 }) {
    const p = this.at('foe');
    const jobs = [];
    for (let i = 0; i < count; i++) {
      const x0 = area === 'screen' ? rnd(0, GAME_W + 60) : p.x + rnd(-50, 60);
      const o = this.img(key, x0, -10, { tint: this.color(color, i % 3), scale, add: key !== 'p_rain' });
      const y1 = area === 'screen' ? GAME_H * 0.75 : p.y + rnd(-10, 30);
      jobs.push(this.tw({ targets: o, y: y1, x: x0 - (y1 + 10) * angle, delay: rnd(0, ms * 0.6), duration: ms * 0.45, ease: 'Linear' }).then(() => o.destroy()));
    }
    await Promise.all(jobs);
  }

  async cloud({ color, count = 9, at = 'foe', ms = 700, key = 'glow', spread = 26, scale = 0.45, add = false, alpha = 0.55 }) {
    const p = this.at(at);
    const jobs = [];
    for (let i = 0; i < count; i++) {
      const o = this.img(key, p.x + rnd(-spread, spread), p.y + rnd(-spread * 0.6, spread * 0.6), { tint: this.color(color, i % 3), scale: scale * 0.3, alpha: 0, add });
      jobs.push(this.tw({ targets: o, scale: scale * rnd(0.8, 1.3), alpha, delay: i * (ms / count / 2), duration: ms * 0.45 })
        .then(() => this.tw({ targets: o, alpha: 0, y: o.y - 10, duration: ms * 0.4 })));
    }
    await Promise.all(jobs);
  }

  // Energy flowing from the foe back into the user.
  drain({ key = 'fx_orb', count = 9, color, ms = 520, scale = 0.9 }) {
    return this.projectile({ key, count, from: 'foe', to: 'user', ms, stagger: 50, arc: 24, color, scale, spread: 10 });
  }

  // Sprites drifting up from a Morph (notes, z's, hearts, bubbles).
  async float({ key = 'fx_note', count = 4, at = 'foe', color, ms = 700, scale = 1.5, stagger = 120 }) {
    const p = this.at(at);
    const jobs = [];
    for (let i = 0; i < count; i++) {
      const o = this.img(key, p.x + rnd(-18, 18), p.y + rnd(-4, 10), { tint: this.color(color, 1), scale, alpha: 0 });
      jobs.push(this.tw({ targets: o, alpha: 1, duration: 120, delay: i * stagger })
        .then(() => this.tw({ targets: o, y: o.y - 34, x: o.x + rnd(-10, 10), alpha: 0, duration: ms })));
    }
    await Promise.all(jobs);
  }

  async sparkle({ at = 'foe', count = 10, color, ms = 600, radius = 30, key = 'fx_sparkle', scale = 1.4 }) {
    const p = this.at(at);
    const jobs = [];
    for (let i = 0; i < count; i++) {
      const o = this.img(key, p.x + rnd(-radius, radius), p.y + rnd(-radius, radius * 0.7), { tint: this.color(color, i % 2), scale: 0.1, add: true });
      jobs.push(this.tw({ targets: o, scale, angle: 90, duration: ms * 0.35, delay: rnd(0, ms * 0.5), yoyo: true }));
    }
    await Promise.all(jobs);
  }

  async arrows({ who = 'user', dir = 'up', color, count = 7 }) {
    const p = this.at(who);
    const jobs = [];
    for (let i = 0; i < count; i++) {
      const o = this.img('fx_arrow', p.x + rnd(-26, 26), p.y + (dir === 'up' ? 24 : -24), { tint: this.color(color, 1), scale: 1.4 }).setFlipY(dir !== 'up');
      jobs.push(this.tw({ targets: o, y: o.y + (dir === 'up' ? -44 : 44), alpha: 0, delay: i * 45, duration: 460 }));
    }
    await Promise.all(jobs);
  }

  async shield({ who = 'user', color, ms = 520 }) {
    const p = this.at(who);
    const o = this.img('fx_shield', p.x, p.y, { tint: this.color(color, 1), scale: 0.3, alpha: 0.9, add: true });
    await this.tw({ targets: o, scale: 2.2, duration: ms * 0.4, ease: 'Back.easeOut' });
    await this.tw({ targets: o, alpha: 0, duration: ms * 0.6 });
  }

  // A single custom sprite: appears at a spot and animates (moon, halo, anvil, lantern...).
  async show({ key, at = 'foe', dx = 0, dy = 0, scale = 1.5, color, ms = 500, to = {}, add = false, from = {} }) {
    const p = this.at(at);
    const o = this.img(key, p.x + dx, p.y + dy, { tint: color === false ? undefined : this.color(color, 1), scale, add, alpha: from.alpha ?? 1 });
    if (from.scale !== undefined) { o.setScale(from.scale); }
    if (Object.keys(to).length) { await this.tw({ targets: o, ...to, duration: ms, ease: 'Sine.easeInOut' }); } else { await this.wait({ ms }); }
    await this.tw({ targets: o, alpha: 0, duration: 180 });
  }

  // A quick straight streak (dash lines behind a fast attack).
  async streak({ count = 3, color, ms = 180 }) {
    const a = this.at('user'), b = this.at('foe');
    const ang = Math.atan2(b.y - a.y, b.x - a.x);
    const len = Math.hypot(b.x - a.x, b.y - a.y);
    const jobs = [];
    for (let i = 0; i < count; i++) {
      const off = (i - (count - 1) / 2) * 8;
      const o = this.img('px', a.x - Math.sin(ang) * off, a.y + Math.cos(ang) * off, { tint: this.color(color, 1), add: true }).setOrigin(0, 0.5).setRotation(ang).setScale(0, 2);
      jobs.push(this.tw({ targets: o, scaleX: len, duration: ms * 0.6, delay: i * 30 }).then(() => this.tw({ targets: o, alpha: 0, duration: ms * 0.4 })));
    }
    await Promise.all(jobs);
  }

  // Lines of force converging on the user (charging up).
  async gather({ who = 'user', color, count = 12, ms = 420, radius = 60 }) {
    const p = this.at(who);
    const jobs = [];
    for (let i = 0; i < count; i++) {
      const a = (i / count) * Math.PI * 2;
      const o = this.img('fx_orb', p.x + Math.cos(a) * radius, p.y + Math.sin(a) * radius * 0.7, { tint: this.color(color, i % 2), scale: 0.6, add: true });
      jobs.push(this.tw({ targets: o, x: p.x, y: p.y, scale: 0.2, duration: ms, delay: (i % 4) * 30, ease: 'Quad.easeIn' }));
    }
    await Promise.all(jobs);
  }
}
