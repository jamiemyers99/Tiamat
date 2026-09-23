// Animated battle scene. Implements the `ui` interface used by battle/engine.js.
import Phaser from 'phaser';
import { GAME_W, GAME_H } from '../config.js';
import { input } from '../core/input.js';
import { audio } from '../core/audio.js';
import { G, itemCount, takeItem, addMoney, markSeen, markCaught, receiveMorph, flag } from '../core/state.js';
import { Battle } from '../battle/engine.js';
import { createMon, calcStats, maxHp, monName, xpProgress, replaceMove, evolutionTarget, STAT_KEYS } from '../battle/mon.js';
import { SPECIES } from '../data/species.js';
import { MOVES } from '../data/moves.js';
import { ITEMS } from '../data/items.js';
import { TRAINERS } from '../data/trainers.js';
import { nameEntry } from '../ui/nameEntry.js';
import { tierOf, wildIvs, trainerIvs, trainerSkill, wildSkill, settleCaught } from '../data/difficulty.js';
import { TYPE_COLORS, effectiveness } from '../data/types.js';
import { txt, wrap, fmt } from '../ui/text.js';
import { panel, Bar, choose } from '../ui/widgets.js';
import { timeOfDay } from '../world/Atmosphere.js';

const EP = { x: 348, y: 142 };
const PP = { x: 130, y: 238 };
const MSG_Y = GAME_H - 62;
const SPEED = { slow: 38, normal: 20, fast: 8, instant: 0 };

const TYPE_FX = {
  Plain: { tint: [0xffffff, 0xe8e8f0], tex: 'p_star' }, Nature: { tint: [0x6aba4a, 0x3f9a45, 0xb8f07a], tex: 'p_leaf' },
  Ember: { tint: [0xffcf3a, 0xff7a3d, 0xe2403a], tex: 'p_dot' }, Tide: { tint: [0x8ad8ff, 0x3d8bfd, 0xffffff], tex: 'p_dot' },
  Static: { tint: [0xfff27a, 0xf5c542, 0xffffff], tex: 'p_star' }, Stone: { tint: [0xb38b5d, 0x8a6a44, 0xd8c09a], tex: 'p_sq' },
  Frost: { tint: [0xdff6ff, 0x7fd6f2, 0xffffff], tex: 'p_star' }, Wing: { tint: [0xffffff, 0xc8d8ff], tex: 'p_ring' },
  Swarm: { tint: [0x9bbf3a, 0xd8f07a], tex: 'p_sq' }, Toxin: { tint: [0xa560c8, 0xd8a0f0, 0x6a2a8a], tex: 'p_ring' },
  Brawl: { tint: [0xff8a5a, 0xffffff], tex: 'p_star' }, Mind: { tint: [0xf06292, 0xffc0d8], tex: 'p_ring' },
  Umbra: { tint: [0x5e4b8b, 0x2a1e40, 0xb89aff], tex: 'p_dot' }, Iron: { tint: [0xc8d0de, 0x8e9aaf, 0xffffff], tex: 'p_sq' },
  Drake: { tint: [0x8a6ae0, 0x6fe0c8, 0xe0d0ff], tex: 'p_star' },
};

export class BattleScene extends Phaser.Scene {
  constructor() { super('Battle'); }

  init(data) { this.cfg = data; }

  create() {
    const cfg = this.cfg;
    this.cameras.main.setBackgroundColor('#000000');
    this.owner = 'battle';
    input.push(this.owner);
    this.animOn = G.settings.battleAnims !== false;
    // ── build parties ──
    let enemyParty, trainer = null;
    // difficulty ramps with how far into the Reach this battle is (see data/difficulty.js)
    const tier = tierOf(G.state.player.map);
    this.tier = tier;
    if (cfg.kind === 'trainer') {
      const base = TRAINERS[cfg.trainerId];
      trainer = { ...base, skill: trainerSkill(tier, base) };
      const ivs = trainerIvs(tier, base);
      enemyParty = trainer.party.map(([sp, lv, moves]) => createMon(sp, lv, { moves, shiny: false, ivs }));
    } else {
      enemyParty = [createMon(cfg.species, cfg.level, { metMap: G.state.player.map, ivs: wildIvs(tier) })];
    }
    enemyParty.forEach((m) => markSeen(m.species));
    this.trainer = trainer;
    const night = timeOfDay(G.state.clock) === 'night';
    const world = this.scene.get('World');
    const mapProps = world && world.mapView ? world.mapView.props : {};
    let theme = cfg.bg || (trainer && trainer.bg) || mapProps.battle || 'meadow';
    if (cfg.kind === 'wild' && cfg.kindEnc === 'water') { theme = 'water'; }
    if (night && ['meadow', 'forest', 'moor'].includes(theme)) { theme = 'night'; }
    this.theme = theme;
    // ── scene graph ──
    this.add.image(0, 0, `bg_${theme}`).setOrigin(0, 0);
    this.enemyShadow = this.add.image(EP.x, EP.y - 4, 'ui', 'battle_shadow').setAlpha(0.6);
    this.playerShadow = this.add.image(PP.x, PP.y - 16, 'ui', 'battle_shadow').setScale(1.4, 1.3).setAlpha(0.6);
    this.enemySpr = this.add.image(EP.x, EP.y, 'mons', 'nibbit_f').setOrigin(0.5, 1).setVisible(false);
    this.playerSpr = this.add.image(PP.x, PP.y, 'mons', 'nibbit_b').setOrigin(0.5, 1).setScale(1.25).setVisible(false);
    this.fxLayer = this.add.container(0, 0).setDepth(50);
    this._buildPanels();
    this._buildMessageBox();
    // ── music ──
    const music = cfg.music || (trainer && trainer.music) || (cfg.kind === 'trainer' ? 'battle_trainer' : 'battle_wild');
    const key = this.cache.audio.exists(`bgm_${music}`) ? `bgm_${music}` : (cfg.kind === 'trainer' ? 'bgm_battle_trial' : 'bgm_battle_wild');
    audio.playMusic(key, { fade: 100, restart: true });
    // ── engine ──
    this.battle = new Battle({
      playerParty: G.state.party,
      enemyParty,
      kind: cfg.kind,
      trainer,
      ui: this,
      opts: {
        expShare: G.settings.expShare !== false && itemCount('bond_charm') > 0,
        style: G.settings.battleStyle || 'shift',
        night,
        cave: mapProps.light === 'dark' || mapProps.enc_floor === '1',
        noRun: cfg.noRun,
        wildSkill: wildSkill(tier),
      },
    });
    this.cameras.main.fadeIn(250, 0, 0, 0);
    this.time.delayedCall(260, () => this._run());
  }

  async _run() {
    let outcome = 'lose';
    try {
      outcome = await this.battle.run();
    } catch (e) {
      console.error('[battle]', e);
    }
    // caught Morph goes to the party / storage
    if (outcome === 'caught' && this.battle.caught) {
      const m = this.battle.caught;
      m.ot = G.state.player.name;
      m.metMap = G.state.player.map;
      m.status = null;
      const ratio = m.hp / maxHp(m);
      settleCaught(m);
      m.hp = Math.max(1, Math.round(maxHp(m) * ratio));
      const firstTime = !G.state.index.caught.includes(m.species);
      markCaught(m.species);
      if (firstTime) { await this.message(`${SPECIES[m.species].name}'s data was added to the Index!`); }
      this.setPrompt(`Give a nickname to the caught ${SPECIES[m.species].name}?`);
      const nick = await choose(this, [{ label: 'Yes', value: true }, { label: 'No', value: false }], { x: GAME_W - 12, y: MSG_Y - 4, anchor: 'bottom-right', depth: 80 });
      if (nick) {
        const n = await nameEntry(this, { title: `Nickname for ${SPECIES[m.species].name}`, max: 12, owner: this.owner, allowEmpty: true, depth: 120 });
        if (n) { m.nick = n; }
      }
      const where = receiveMorph(m);
      if (where && where.startsWith('box')) {
        await this.message(`${SPECIES[m.species].name} was sent to storage (Box ${+where.split(':')[1] + 1}).`);
      }
    }
    if (outcome !== 'lose') {
      G.state.party.forEach((m) => { if (m.status === 'confuse') { m.status = null; } });
    }
    // evolutions (not after losing)
    if (outcome === 'win' || outcome === 'caught' || outcome === 'fled') {
      for (const m of G.state.party) {
        if (m.hp > 0 && this.battle.levelled.has(m.uid)) {
          const into = evolutionTarget(m);
          if (into) { await this._evolve(m, into); }
        }
      }
    }
    input.pop(this.owner);
    const done = () => this.cfg.onEnd({ outcome, caught: this.battle.caught });
    this.cameras.main.fadeOut(300, 0, 0, 0);
    this.cameras.main.once('camerafadeoutcomplete', done);
  }

  _evolve(mon, into) {
    return new Promise((resolve) => {
      this.scene.launch('Evolution', { mon, into, onDone: resolve });
      this.scene.bringToTop('Evolution');
    });
  }

  // ─── panels ──────────────────────────────────────────────────────────
  _buildPanels() {
    // enemy
    const e = this.add.container(-200, 16).setDepth(40);
    e.add(panel(this, 0, 0, 178, 38, 'dark'));
    this.eName = txt(this, 10, 6, '');
    this.eLv = txt(this, 170, 6, '', { align: 'right', color: 'gold' });
    this.eTypes = this.add.container(10, 21);
    this.eHp = new Bar(this, 52, 22, 116, 5);
    this.eHp.addTo(e);
    this.eStatus = this.add.image(10, 20, 'ui', 'st_burn').setOrigin(0, 0).setVisible(false);
    this.eCaught = this.add.image(160, 7, 'ui', 'menu_party').setOrigin(0, 0).setScale(0.5).setVisible(false);
    e.add([this.eName, this.eLv, this.eStatus, this.eCaught, txt(this, 36, 21, 'HP', { face: 'small', color: 'gold' })]);
    this.ePanel = e;
    // player
    const p = this.add.container(GAME_W + 10, 146).setDepth(40);
    p.add(panel(this, 0, 0, 196, 50, 'dark'));
    this.pName = txt(this, 10, 6, '');
    this.pLv = txt(this, 188, 6, '', { align: 'right', color: 'gold' });
    this.pHp = new Bar(this, 58, 22, 128, 5);
    this.pHp.addTo(p);
    this.pHpTxt = txt(this, 188, 30, '', { align: 'right' });
    this.pXp = new Bar(this, 10, 44, 176, 2, { kind: 'xp' });
    this.pXp.addTo(p);
    this.pStatus = this.add.image(10, 20, 'ui', 'st_burn').setOrigin(0, 0).setVisible(false);
    p.add([this.pName, this.pLv, this.pHpTxt, this.pStatus, txt(this, 42, 21, 'HP', { face: 'small', color: 'gold' })]);
    this.pPanel = p;
  }

  _refreshPanel(side) {
    const b = side === 0 ? this.battle.p : this.battle.e;
    const m = b.mon;
    const mx = maxHp(m);
    if (side === 1) {
      this.eName.setText(monName(m));
      this.eLv.setText(`Lv${m.level}`);
      this.eHp.set(m.hp / mx);
      this._status(this.eStatus, m.status);
      this.eCaught.setVisible(this.battle.kind === 'wild' && G.state.index.caught.includes(m.species));
    } else {
      this.pName.setText(monName(m));
      this.pLv.setText(`Lv${m.level}`);
      this.pHp.set(m.hp / mx);
      this.pHpTxt.setText(`${m.hp} / ${mx}`);
      this.pXp.set(xpProgress(m));
      this._status(this.pStatus, m.status);
    }
  }

  _status(img, st) {
    if (!st) { img.setVisible(false); return; }
    img.setFrame(`st_${st}`).setVisible(true);
  }

  // ─── message box ─────────────────────────────────────────────────────
  _buildMessageBox() {
    this.msgBg = panel(this, 8, MSG_Y, GAME_W - 16, 56, 'dark').setDepth(60);
    this.msgLines = [0, 1, 2].map((i) => txt(this, 22, MSG_Y + 10 + i * 14, '').setDepth(61));
    this.msgAdv = this.add.image(GAME_W - 26, MSG_Y + 44, 'advance').setDepth(61).setVisible(false);
    this.tweens.add({ targets: this.msgAdv, y: '+=2', duration: 300, yoyo: true, repeat: -1 });
  }

  message(text, opts = {}) {
    const str = fmt(text, G.state);
    const lines = wrap(this, str, GAME_W - 60);
    const ms = SPEED[G.settings.textSpeed] ?? 20;
    return new Promise((resolve) => {
      this.msgLines.forEach((l) => l.setText(''));
      this.msgAdv.setVisible(false);
      const full = lines.slice(0, 3).join('\n');
      let shown = ms === 0 ? full.length : 0;
      let acc = 0;
      let phase = 'type';
      let waitT = 0;
      const auto = opts.quick ? 350 : (opts.auto ?? null);
      const tick = (t, d) => {
        if (phase === 'type') {
          if (input.pressed('confirm', this.owner) || input.pressed('cancel', this.owner)) { shown = full.length; }
          acc += d;
          while (acc >= ms && shown < full.length && ms > 0) { acc -= ms; shown++; }
          const parts = full.slice(0, shown).split('\n');
          this.msgLines.forEach((l, i) => l.setText(parts[i] || ''));
          if (shown >= full.length) { phase = 'wait'; waitT = 0; this.msgAdv.setVisible(auto === null); input.clear(); }
        } else {
          waitT += d;
          if ((auto !== null && waitT >= auto) || (auto === null && (input.pressed('confirm', this.owner) || input.pressed('cancel', this.owner)))) {
            this.events.off('update', tick);
            this.msgAdv.setVisible(false);
            resolve();
          }
        }
      };
      this.events.on('update', tick);
    });
  }

  setPrompt(text) {
    const lines = wrap(this, fmt(text, G.state), 250);
    this.msgLines.forEach((l, i) => l.setText(lines[i] || ''));
    this.msgAdv.setVisible(false);
  }

  wait(ms) { return new Promise((r) => this.time.delayedCall(ms, r)); }
  tween(cfg) { return new Promise((r) => this.tweens.add({ ...cfg, onComplete: r })); }

  // ─── engine UI interface ─────────────────────────────────────────────
  async intro(b) {
    const e = b.e.mon;
    this.enemySpr.setFrame(`${e.species}_${e.shiny ? 'fs' : 'f'}`).setVisible(true);
    if (this.trainer) {
      const idx = this.cache.json.get('charIndex');
      const row = idx[this.trainer.sprite] ?? 0;
      this.trainerSpr = this.add.image(GAME_W + 40, EP.y - 4, 'chars', row * 12).setOrigin(0.5, 1).setScale(3);
      this.enemySpr.setVisible(false);
      await this.tween({ targets: this.trainerSpr, x: EP.x + 4, duration: 600, ease: 'Cubic.easeOut' });
      await this.message(`${this.trainer.title ? this.trainer.title + ' ' : ''}${this.trainer.name} wants to battle!`);
      await this.tween({ targets: this.trainerSpr, x: GAME_W + 60, duration: 400, ease: 'Cubic.easeIn' });
      await this.sendOut(b, b.e, true);
    } else {
      this.enemySpr.x = GAME_W + 60;
      this.enemySpr.setTint(0x202030);
      await this.tween({ targets: this.enemySpr, x: EP.x, duration: 700, ease: 'Cubic.easeOut' });
      this.enemySpr.clearTint();
      audio.cry(SPECIES[e.species].num);
      if (e.shiny) { this._sparkle(EP.x, EP.y - 50); }
      this._refreshPanel(1);
      this.tweens.add({ targets: this.ePanel, x: 10, duration: 350, ease: 'Back.easeOut' });
      await this.message(`A wild ${SPECIES[e.species].name} appeared!${e.shiny ? ' It\'s shimmering with an odd light!' : ''}`);
    }
    await this.sendOut(b, b.p, true);
    this._idle();
  }

  _idle() {
    if (this.idleTw) { this.idleTw.forEach((t) => t.stop()); }
    this.idleTw = [
      this.tweens.add({ targets: this.enemySpr, scaleY: 1.03, duration: 900, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' }),
      this.tweens.add({ targets: this.playerSpr, scaleY: 1.28, duration: 1000, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' }),
    ];
  }

  async sendOut(b, battler, first = false) {
    const m = battler.mon;
    markSeen(m.species);
    if (battler.side === 1) {
      if (!first) { await this.message(`${this.trainer ? this.trainer.name : 'The foe'} sent out ${monName(m)}!`); }
      this.enemySpr.setFrame(`${m.species}_${m.shiny ? 'fs' : 'f'}`).setPosition(EP.x, EP.y).setAlpha(1).setScale(0.1).setVisible(true);
      this._burst(EP.x, EP.y - 40, 'Plain', 14);
      await this.tween({ targets: this.enemySpr, scale: 1, duration: 260, ease: 'Back.easeOut' });
      audio.cry(SPECIES[m.species].num);
      this._refreshPanel(1);
      if (this.ePanel.x < 0) { this.tweens.add({ targets: this.ePanel, x: 10, duration: 350, ease: 'Back.easeOut' }); }
    } else {
      await this.message(first ? `Go, ${monName(m)}!` : `Your turn, ${monName(m)}!`, { quick: true });
      this.playerSpr.setFrame(`${m.species}_${m.shiny ? 'bs' : 'b'}`).setPosition(PP.x, PP.y).setAlpha(1).setScale(0.1).setVisible(true);
      const cap = this.add.image(20, PP.y - 120, 'ui', 'throw_capsule').setDepth(45);
      await this.tween({ targets: cap, x: PP.x, y: PP.y - 50, angle: 540, duration: 380, ease: 'Sine.easeOut' });
      cap.destroy();
      this._burst(PP.x, PP.y - 50, 'Plain', 16);
      audio.sfx('select');
      await this.tween({ targets: this.playerSpr, scale: 1.25, duration: 260, ease: 'Back.easeOut' });
      audio.cry(SPECIES[m.species].num);
      this._refreshPanel(0);
      if (this.pPanel.x > GAME_W) { this.tweens.add({ targets: this.pPanel, x: GAME_W - 206, duration: 350, ease: 'Back.easeOut' }); }
    }
    this._idle();
  }

  async withdraw(b, battler) {
    if (battler.side === 0) {
      await this.message(`${monName(battler.mon)}, come back!`, { quick: true });
      this.playerSpr.setTint(0xff6a6a);
      await this.tween({ targets: this.playerSpr, scale: 0.05, duration: 240 });
      this.playerSpr.clearTint().setVisible(false);
    }
  }

  async refresh() { this._refreshPanel(0); this._refreshPanel(1); }

  async hp(b, battler, from, to) {
    const m = battler.mon;
    const mx = maxHp(m);
    const bar = battler.side === 0 ? this.pHp : this.eHp;
    const ms = Math.min(900, 200 + Math.abs(from - to) * 12);
    if (battler.side === 0) {
      const o = { v: from };
      this.tweens.add({ targets: o, v: to, duration: ms, onUpdate: () => this.pHpTxt.setText(`${Math.round(o.v)} / ${mx}`) });
    }
    await bar.tweenTo(to / mx, ms);
    if (battler.side === 0) { this.pHpTxt.setText(`${to} / ${mx}`); }
  }

  _sprite(battler) { return battler.side === 0 ? this.playerSpr : this.enemySpr; }
  _pos(battler) { return battler.side === 0 ? { x: PP.x, y: PP.y - 55 } : { x: EP.x, y: EP.y - 45 }; }

  async moveAnim(b, att, def, move, eff = 1) {
    if (!this.animOn) { audio.sfx('attack'); return; }
    const aSpr = this._sprite(att);
    const from = this._pos(att);
    const to = this._pos(def);
    audio.sfx('attack');
    if (move.cat === 'status') {
      const target = move.fx.target === 'self' || move.fx.heal || move.fx.protect ? att : def;
      const p = this._pos(target);
      if (move.fx.protect) {
        const ring = this.add.image(p.x, p.y, 'p_ring').setScale(4).setTint(0x8ad8ff).setAlpha(0.8).setDepth(50);
        await this.tween({ targets: ring, scale: 9, alpha: 0, duration: 400 });
        ring.destroy();
        return;
      }
      this._burst(p.x, p.y, move.type, 18, 60);
      await this.wait(350);
      return;
    }
    if (move.cat === 'phys') {
      const dx = att.side === 0 ? 26 : -26;
      const dy = att.side === 0 ? -14 : 8;
      await this.tween({ targets: aSpr, x: aSpr.x + dx, y: aSpr.y + dy, duration: 110, yoyo: true, ease: 'Quad.easeOut' });
      this._burst(to.x, to.y, move.type, 12, 70);
    } else {
      await this._projectile(from, to, move.type);
      this._burst(to.x, to.y, move.type, 16, 80);
    }
  }

  _projectile(from, to, type) {
    const fx = TYPE_FX[type] || TYPE_FX.Plain;
    return new Promise((resolve) => {
      const n = 8;
      let done = 0;
      for (let i = 0; i < n; i++) {
        const p = this.add.image(from.x, from.y, fx.tex).setTint(Phaser.Utils.Array.GetRandom(fx.tint)).setScale(2).setDepth(52);
        this.tweens.add({
          targets: p, x: to.x + Phaser.Math.Between(-8, 8), y: to.y + Phaser.Math.Between(-8, 8), delay: i * 28, duration: 260,
          ease: 'Sine.easeIn', onComplete: () => { p.destroy(); if (++done === n) { resolve(); } },
        });
      }
    });
  }

  _burst(x, y, type, count = 12, speed = 60) {
    const fx = TYPE_FX[type] || TYPE_FX.Plain;
    const em = this.add.particles(x, y, fx.tex, {
      speed: { min: speed * 0.4, max: speed }, lifespan: 420, scale: { start: 1.8, end: 0.4 }, alpha: { start: 1, end: 0 },
      tint: fx.tint, quantity: count, emitting: false, gravityY: type === 'Stone' ? 200 : 0,
    }).setDepth(53);
    em.explode(count);
    this.time.delayedCall(600, () => em.destroy());
  }

  _sparkle(x, y) {
    const em = this.add.particles(x, y, 'p_star', { speed: { min: 20, max: 60 }, lifespan: 700, scale: { start: 1.5, end: 0 }, tint: [0xffffff, 0xffd65c, 0x8ad8ff], emitting: false }).setDepth(53);
    em.explode(16);
    audio.blip('coin');
    this.time.delayedCall(900, () => em.destroy());
  }

  async hitFlash(b, battler, eff = 1, crit = false) {
    const spr = this._sprite(battler);
    audio.sfx(eff > 1 ? 'hit_super' : 'hit');
    if (crit || eff > 1) { this.cameras.main.shake(180, crit ? 0.012 : 0.008); }
    if (!this.animOn) { return; }
    for (let i = 0; i < 3; i++) {
      spr.setAlpha(0.15); await this.wait(55);
      spr.setAlpha(1); await this.wait(55);
    }
  }

  async faint(b, battler) {
    const spr = this._sprite(battler);
    audio.cry(SPECIES[battler.mon.species].num, { faint: true });
    audio.sfx('faint');
    await this.tween({ targets: spr, y: spr.y + 40, alpha: 0, duration: 420, ease: 'Quad.easeIn' });
    spr.setVisible(false).setAlpha(1);
    spr.y = battler.side === 0 ? PP.y : EP.y;
    this._refreshPanel(battler.side);
  }

  async statusAnim(b, battler, status) {
    if (!this.animOn) { return; }
    const p = this._pos(battler);
    const map = { burn: 'Ember', poison: 'Toxin', toxic: 'Toxin', paralyze: 'Static', sleep: 'Mind', freeze: 'Frost', confuse: 'Mind' };
    this._burst(p.x, p.y, map[status] || 'Plain', 10, 40);
    await this.wait(260);
  }

  async statAnim(b, battler, up) {
    audio.blip(up ? 'coin' : 'bump');
    if (!this.animOn) { return; }
    const spr = this._sprite(battler);
    spr.setTint(up ? 0xff8a6a : 0x6a8aff);
    const p = this._pos(battler);
    for (let i = 0; i < 6; i++) {
      const a = this.add.image(p.x + Phaser.Math.Between(-24, 24), p.y + (up ? 20 : -20), 'p_sq').setScale(2, 5).setTint(up ? 0xffd65c : 0x8ab8ff).setDepth(52);
      this.tweens.add({ targets: a, y: a.y + (up ? -40 : 40), alpha: 0, duration: 420, delay: i * 40, onComplete: () => a.destroy() });
    }
    await this.wait(420);
    spr.clearTint();
  }

  async charge(b, battler) {
    const spr = this._sprite(battler);
    await this.tween({ targets: spr, y: spr.y - 120, alpha: 0, duration: 300 });
    spr.y += 120; spr.setAlpha(1);
  }

  async xp(b, mon, beforeXp, steps) {
    if (mon !== b.p.mon) { return; }
    const target = steps.length ? 1 : xpProgress(mon);
    await this.pXp.tweenTo(target, 500);
    if (steps.length) { this.pXp.set(0); await this.pXp.tweenTo(xpProgress(mon), 300); }
  }

  async levelUp(b, mon, st) {
    audio.jingle('jingle_level');
    audio.sfx('level_up');
    if (mon === b.p.mon) { this._refreshPanel(0); }
    await this.message(`${monName(mon)} grew to Lv. ${st.level}!`);
    // stat popup
    const c = this.add.container(GAME_W - 150, 20).setDepth(70);
    c.add(panel(this, 0, 0, 140, 100, 'gold'));
    const names = { hp: 'HP', atk: 'Attack', def: 'Defense', spa: 'Sp. Atk', spd: 'Sp. Def', spe: 'Speed' };
    STAT_KEYS.forEach((k, i) => {
      c.add(txt(this, 10, 8 + i * 14, names[k]));
      c.add(txt(this, 130, 8 + i * 14, `+${st.after[k] - st.before[k]}`, { align: 'right', color: 'green' }));
    });
    await this._waitKey();
    STAT_KEYS.forEach((k, i) => { c.list[2 + i * 2].setText(`${st.after[k]}`).setFont('main_white'); });
    await this._waitKey();
    c.destroy();
  }

  _waitKey() {
    return new Promise((resolve) => {
      const tick = () => { if (input.pressed('confirm', this.owner) || input.pressed('cancel', this.owner)) { this.events.off('update', tick); resolve(); } };
      this.events.on('update', tick);
    });
  }

  async learnPrompt(b, mon, moveId) {
    const mv = MOVES[moveId];
    const nm = monName(mon);
    await this.message(`${nm} wants to learn ${mv.name}. But ${nm} already knows four moves.`);
    for (;;) {
      this.setPrompt(`Forget a move to learn ${mv.name}?`);
      const yes = await choose(this, [{ label: 'Forget a move', value: true }, { label: 'Keep old moves', value: false }], { x: GAME_W - 12, y: MSG_Y - 4, anchor: 'bottom-right', depth: 80 });
      if (!yes) {
        await this.message(`${nm} did not learn ${mv.name}.`);
        return;
      }
      const items = mon.moves.map((m, i) => ({ label: MOVES[m.id].name, right: `${m.pp}/${m.max}`, value: i }));
      items.push({ label: `(new) ${mv.name}`, right: `${mv.pp}/${mv.pp}`, value: -1, color: 'gold' });
      this.setPrompt('Which move should be forgotten?');
      const idx = await choose(this, items, { x: GAME_W - 12, y: MSG_Y - 4, anchor: 'bottom-right', depth: 80, width: 190 });
      if (idx === null || idx === -1) { continue; }
      const old = MOVES[mon.moves[idx].id].name;
      replaceMove(mon, idx, moveId);
      await this.message(`1, 2 and... Poof! ${nm} forgot ${old}... and learned ${mv.name}!`);
      return;
    }
  }

  async capture(b, itemId, shakes, caught) {
    const frame = this.textures.get('ui').has(`throw_${itemId}`) ? `throw_${itemId}` : 'throw_capsule';
    await this.message(`{PLAYER} threw a ${ITEMS[itemId].name}!`, { quick: true });
    const cap = this.add.image(PP.x, PP.y - 60, 'ui', frame).setDepth(55).setScale(1.5);
    const tx = EP.x, ty = EP.y - 50;
    // arc
    await new Promise((res) => {
      const o = { t: 0 };
      this.tweens.add({ targets: o, t: 1, duration: 520, onUpdate: () => {
        cap.x = PP.x + (tx - PP.x) * o.t;
        cap.y = PP.y - 60 + (ty - (PP.y - 60)) * o.t - Math.sin(o.t * Math.PI) * 70;
        cap.angle = o.t * 720;
      }, onComplete: res });
    });
    cap.angle = 0;
    this.enemySpr.setTint(0xff4a6a);
    this._burst(tx, ty, 'Plain', 10);
    await this.tween({ targets: this.enemySpr, scale: 0.05, alpha: 0.3, duration: 260 });
    this.enemySpr.setVisible(false);
    await this.tween({ targets: cap, y: EP.y - 10, duration: 320, ease: 'Bounce.easeOut' });
    for (let i = 0; i < shakes; i++) {
      await this.wait(380);
      audio.sfx('capture_shake');
      await this.tween({ targets: cap, angle: i % 2 ? 22 : -22, duration: 110, yoyo: true });
    }
    await this.wait(380);
    if (caught) {
      audio.sfx('capture_success');
      cap.setTint(0x9a9aaa);
      this._sparkle(cap.x, cap.y);
      await audio.jingle('jingle_catch');
      await this.wait(200);
      cap.destroy();
    } else {
      audio.sfx('capture_fail');
      this._burst(cap.x, cap.y, 'Plain', 16);
      cap.destroy();
      this.enemySpr.setVisible(true).clearTint().setAlpha(1);
      await this.tween({ targets: this.enemySpr, scale: 1, duration: 220, ease: 'Back.easeOut' });
    }
  }

  async askShift(b, nextMon) {
    const who = this.trainer ? this.trainer.name : 'The foe';
    this.setPrompt(`${who} is about to send out ${monName(nextMon)}. Switch Morphs?`);
    const yes = await choose(this, [{ label: 'Keep going', value: false }, { label: 'Switch', value: true }], { x: GAME_W - 12, y: MSG_Y - 4, anchor: 'bottom-right', depth: 80 });
    if (!yes) { return null; }
    const idx = await this.partyPicker(false, true);
    return idx === b.p.index ? null : idx;
  }

  async chooseSwitch(b, forced) {
    await this.message(forced ? 'Choose a Morph to send out.' : 'Choose a Morph.', { quick: true });
    return this.partyPicker(forced, true);
  }

  async end(b, outcome) {
    if (outcome === 'win' && this.trainer) {
      const tr = this.trainer;
      const reward = Math.floor((tr.reward || 30) * Math.max(...b.e.party.map((m) => m.level)));
      this.trainerSpr.setPosition(GAME_W + 40, EP.y - 4).setVisible(true);
      this.enemySpr.setVisible(false);
      this.tweens.add({ targets: this.ePanel, x: -200, duration: 300 });
      audio.playMusic(this.cache.audio.exists('bgm_victory') ? 'bgm_victory' : null, { fade: 100, restart: true });
      await this.tween({ targets: this.trainerSpr, x: EP.x + 4, duration: 500, ease: 'Cubic.easeOut' });
      await this.message(`You defeated ${tr.title ? tr.title + ' ' : ''}${tr.name}!`);
      if (tr.lose) { await this.message(`${tr.name}: ${fmt(tr.lose, G.state)}`); }
      addMoney(reward);
      audio.blip('coin');
      await this.message(`{PLAYER} got ${reward}¢ for winning!`);
      G.state.defeated[this.cfg.trainerId] = true;
    } else if (outcome === 'win') {
      // wild win — nothing extra
    } else if (outcome === 'lose') {
      if (this.trainer && this.trainer.win) { await this.message(`${this.trainer.name}: ${fmt(this.trainer.win, G.state)}`); }
    }
  }

  // ─── player action selection ─────────────────────────────────────────
  async chooseAction(b) {
    for (;;) {
      this._refreshPanel(0); this._refreshPanel(1);
      this.setPrompt(`What will ${monName(b.p.mon)} do?`);
      const cmd = await this.commandMenu();
      if (cmd === 'fight') {
        const m = b.p.mon;
        if (m.moves.every((mv) => mv.pp <= 0)) { return { type: 'move', index: 0 }; }
        const idx = await this.moveMenu(b);
        if (idx !== null) { return { type: 'move', index: idx }; }
      } else if (cmd === 'bag') {
        const act = await this.bagMenu(b);
        if (act) { return act; }
      } else if (cmd === 'team') {
        const idx = await this.partyPicker(false, false);
        if (idx !== null && idx !== b.p.index) { return { type: 'switch', index: idx }; }
      } else if (cmd === 'run') {
        return { type: 'run' };
      }
    }
  }

  commandMenu() {
    const opts = [
      { id: 'fight', label: 'FIGHT', col: 0xe2555f }, { id: 'bag', label: 'BAG', col: 0xe2b64a },
      { id: 'team', label: 'TEAM', col: 0x4caf50 }, { id: 'run', label: 'RUN', col: 0x3d8bfd },
    ];
    const c = this.add.container(0, 0).setDepth(70);
    const x0 = GAME_W - 186, y0 = MSG_Y + 4;
    const btns = opts.map((o, i) => {
      const x = x0 + (i % 2) * 88, y = y0 + Math.floor(i / 2) * 24;
      const bg = this.add.rectangle(x, y, 84, 21, o.col, 0.85).setOrigin(0, 0).setStrokeStyle(1, 0x0b0c16);
      const t = txt(this, x + 42, y + 5, o.label, { align: 'center' });
      c.add([bg, t]);
      return { bg, t, o };
    });
    const sel = this.add.rectangle(0, 0, 86, 23).setOrigin(0, 0).setStrokeStyle(2, 0xffd65c);
    c.add(sel);
    let i = this._lastCmd || 0;
    const draw = () => {
      const bb = btns[i].bg;
      sel.setPosition(bb.x - 1, bb.y - 1);
      btns.forEach((x, k) => x.bg.setAlpha(k === i ? 1 : 0.6));
    };
    draw();
    return new Promise((resolve) => {
      const tick = () => {
        const o = this.owner;
        if (input.nav('left', o) && i % 2 === 1) { i--; audio.sfx('cursor'); draw(); }
        else if (input.nav('right', o) && i % 2 === 0) { i++; audio.sfx('cursor'); draw(); }
        else if (input.nav('up', o) && i >= 2) { i -= 2; audio.sfx('cursor'); draw(); }
        else if (input.nav('down', o) && i < 2) { i += 2; audio.sfx('cursor'); draw(); }
        else if (input.pressed('confirm', o)) { audio.sfx('select'); finish(opts[i].id); }
        else if (input.pressed('cancel', o) && i !== 3) { i = 3; audio.sfx('cursor'); draw(); }
      };
      const finish = (v) => { this._lastCmd = i; this.events.off('update', tick); c.destroy(); resolve(v); };
      this.events.on('update', tick);
    });
  }

  moveMenu(b) {
    const mon = b.p.mon;
    const foeTypes = SPECIES[b.e.mon.species].types;
    const c = this.add.container(0, 0).setDepth(70);
    c.add(panel(this, 8, MSG_Y, GAME_W - 16, 56, 'deep'));
    const cells = [];
    for (let i = 0; i < 4; i++) {
      const x = 14 + (i % 2) * 150, y = MSG_Y + 5 + Math.floor(i / 2) * 24;
      const m = mon.moves[i];
      if (!m) {
        c.add(txt(this, x + 70, y + 6, '—', { align: 'center', color: 'gray' }));
        cells.push(null);
        continue;
      }
      const mv = MOVES[m.id];
      const bg = this.add.rectangle(x, y, 146, 21, TYPE_COLORS[mv.type], 0.35).setOrigin(0, 0).setStrokeStyle(1, TYPE_COLORS[mv.type]);
      const t = txt(this, x + 6, y + 5, mv.name, { color: m.pp > 0 ? 'white' : 'gray' });
      const pp = txt(this, x + 140, y + 7, `${m.pp}/${m.max}`, { face: 'small', align: 'right', color: m.pp === 0 ? 'red' : m.pp <= m.max / 4 ? 'gold' : 'gray' });
      c.add([bg, t, pp]);
      cells.push({ bg, x, y });
    }
    const sel = this.add.rectangle(0, 0, 148, 23).setOrigin(0, 0).setStrokeStyle(2, 0xffd65c);
    c.add(sel);
    // info
    const ix = 318;
    const typeImg = this.add.image(ix, MSG_Y + 7, 'ui', 'type_Plain').setOrigin(0, 0);
    const catImg = this.add.image(ix + 40, MSG_Y + 7, 'ui', 'cat_phys').setOrigin(0, 0);
    const pw = txt(this, ix, MSG_Y + 20, '', { face: 'small' });
    const eff = txt(this, ix, MSG_Y + 32, '', { face: 'main' });
    c.add([typeImg, catImg, pw, eff]);
    let i = Math.min(this._lastMove || 0, mon.moves.length - 1);
    const draw = () => {
      const cell = cells[i];
      sel.setPosition(cell.x - 1, cell.y - 1);
      const mv = MOVES[mon.moves[i].id];
      typeImg.setFrame(`type_${mv.type}`);
      catImg.setFrame(`cat_${mv.cat}`).setX(ix + typeImg.width + 3);
      pw.setText(`POW ${mv.power || '-'}   ACC ${mv.acc ?? '-'}`);
      if (mv.cat === 'status') { eff.setText('Status move').setFont('main_gray'); }
      else {
        const e = effectiveness(mv.type, foeTypes);
        const [label, col] = e === 0 ? ['No effect', 'gray'] : e > 1 ? ['Super effective', 'green'] : e < 1 ? ['Not very effective', 'red'] : ['Effective', 'white'];
        eff.setText(label).setFont(`main_${col}`);
      }
    };
    draw();
    return new Promise((resolve) => {
      const n = mon.moves.length;
      const tick = () => {
        const o = this.owner;
        const tryGo = (j) => { if (j >= 0 && j < n && cells[j]) { i = j; audio.sfx('cursor'); draw(); } };
        if (input.nav('left', o) && i % 2 === 1) { tryGo(i - 1); }
        else if (input.nav('right', o) && i % 2 === 0) { tryGo(i + 1); }
        else if (input.nav('up', o) && i >= 2) { tryGo(i - 2); }
        else if (input.nav('down', o) && i < 2) { tryGo(i + 2); }
        else if (input.pressed('confirm', o)) {
          if (mon.moves[i].pp <= 0) { audio.blip('bump'); return; }
          audio.sfx('select'); finish(i);
        } else if (input.pressed('cancel', o)) { audio.sfx('cancel'); finish(null); }
      };
      const finish = (v) => { if (v !== null) { this._lastMove = v; } this.events.off('update', tick); c.destroy(); resolve(v); };
      this.events.on('update', tick);
    });
  }

  async bagMenu(b) {
    const pockets = [
      { name: 'Capsules', ids: Object.keys(G.state.bag).filter((k) => ITEMS[k] && ITEMS[k].use.kind === 'capsule' && itemCount(k) > 0) },
      { name: 'Healing', ids: Object.keys(G.state.bag).filter((k) => ITEMS[k] && ['heal', 'cure', 'revive', 'pp'].includes(ITEMS[k].use.kind) && itemCount(k) > 0) },
    ];
    for (;;) {
      this.setPrompt('Use which pocket?');
      const pk = await choose(this, pockets.map((p, i) => ({ label: p.name, value: i, right: p.ids.reduce((a, k) => a + itemCount(k), 0) })), { x: GAME_W - 12, y: MSG_Y - 4, anchor: 'bottom-right', depth: 80 });
      if (pk === null) { return null; }
      const ids = pockets[pk].ids.filter((k) => itemCount(k) > 0);
      if (!ids.length) { await this.message('Nothing in that pocket.', { quick: true }); continue; }
      this.setPrompt(ITEMS[ids[0]].desc);
      const id = await choose(this, ids.map((k) => ({ label: ITEMS[k].name, right: `×${itemCount(k)}`, value: k })),
        { x: GAME_W - 12, y: MSG_Y - 4, anchor: 'bottom-right', depth: 80, visible: 6, width: 200, onMove: (it) => this.setPrompt(ITEMS[it.value].desc) });
      if (id === null) { continue; }
      const it = ITEMS[id];
      if (it.use.kind === 'capsule') {
        if (this.battle.kind !== 'wild') { await this.message("You can't use that in a Tamer battle!"); continue; }
        takeItem(id);
        return { type: 'item', item: id };
      }
      const target = await this.partyPicker(false, false, it);
      if (target === null) { continue; }
      const m = G.state.party[target];
      const u = it.use;
      const ok = (u.kind === 'heal' && m.hp > 0 && (m.hp < maxHp(m) || (u.cure && m.status)))
        || (u.kind === 'cure' && m.hp > 0 && (m.status && (u.status === 'all' || u.status.includes(m.status))))
        || (u.kind === 'revive' && m.hp <= 0)
        || (u.kind === 'pp' && m.moves.some((mv) => mv.pp < mv.max));
      if (!ok) { await this.message("It won't have any effect."); continue; }
      takeItem(id);
      return { type: 'item', item: id, target };
    }
  }

  // Party list overlay. Returns index or null.
  partyPicker(forced, forSwitch, item = null) {
    const party = G.state.party;
    const c = this.add.container(0, 0).setDepth(90);
    c.add(this.add.rectangle(0, 0, GAME_W, GAME_H, 0x0b0c16, 0.82).setOrigin(0, 0));
    c.add(txt(this, 16, 10, item ? `Use ${item.name} on which Morph?` : (forced ? 'Choose a Morph to send out.' : 'Choose a Morph.'), { color: 'gold' }));
    const rows = party.map((m, i) => {
      const x = 16 + (i % 2) * 228, y = 30 + Math.floor(i / 2) * 58;
      const bg = panel(this, x, y, 220, 52, i === this.battle.p.index ? 'teal' : 'dark');
      const ic = this.add.image(x + 20, y + 22, 'mons', `${m.species}_${m.shiny ? 'is' : 'i'}`);
      const nm = txt(this, x + 40, y + 8, monName(m));
      const lv = txt(this, x + 210, y + 8, `Lv${m.level}`, { align: 'right', color: 'gold' });
      const bar = new Bar(this, x + 40, y + 24, 120, 4);
      bar.set(m.hp / maxHp(m));
      const hpt = txt(this, x + 210, y + 22, `${m.hp}/${maxHp(m)}`, { align: 'right', face: 'small' });
      const st = this.add.image(x + 40, y + 34, 'ui', `st_${m.hp <= 0 ? 'faint' : (m.status || 'burn')}`).setOrigin(0, 0).setVisible(m.hp <= 0 || !!m.status);
      c.add([bg, ic, nm, lv, hpt, st]);
      bar.addTo(c);
      return { x, y };
    });
    const sel = this.add.rectangle(0, 0, 222, 54).setOrigin(0, 0).setStrokeStyle(2, 0xffd65c);
    c.add(sel);
    let i = 0;
    if (forSwitch) {
      // start on the first Morph that can actually be sent out
      const ok = party.findIndex((m, k) => m.hp > 0 && k !== this.battle.p.index);
      if (ok >= 0) { i = ok; }
    }
    const draw = () => sel.setPosition(rows[i].x - 1, rows[i].y - 1);
    draw();
    return new Promise((resolve) => {
      const n = party.length;
      const tick = async () => {
        const o = this.owner;
        if (this._pickerBusy) { return; }
        if (input.nav('left', o) && i % 2 === 1) { i--; audio.sfx('cursor'); draw(); }
        else if (input.nav('right', o) && i % 2 === 0 && i + 1 < n) { i++; audio.sfx('cursor'); draw(); }
        else if (input.nav('up', o) && i >= 2) { i -= 2; audio.sfx('cursor'); draw(); }
        else if (input.nav('down', o) && i + 2 < n) { i += 2; audio.sfx('cursor'); draw(); }
        else if (input.pressed('confirm', o)) {
          const m = party[i];
          if (forSwitch) {
            if (m.hp <= 0) { audio.blip('bump'); this._flash(c, `${monName(m)} has no energy left to battle!`); return; }
            if (i === this.battle.p.index && this.battle.p.mon.hp > 0) { audio.blip('bump'); this._flash(c, `${monName(m)} is already out!`); return; }
          }
          audio.sfx('select');
          finish(i);
        } else if (!forced && input.pressed('cancel', o)) { audio.sfx('cancel'); finish(null); }
      };
      const finish = (v) => { this.events.off('update', tick); c.destroy(); resolve(v); };
      this.events.on('update', tick);
    });
  }

  _flash(c, text) {
    const t = txt(this, GAME_W / 2, GAME_H - 20, text, { align: 'center', color: 'red' }).setDepth(95);
    this.time.delayedCall(1200, () => t.destroy());
  }
}
