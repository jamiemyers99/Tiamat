// The overworld: map rendering, player control, NPCs, events, encounters.
import Phaser from 'phaser';
import { GAME_W, GAME_H, TILE, DEPTH, WALK_MS, RUN_MS, SURF_MS, REAL_MS_PER_GAME_MIN, DEBUG } from '../config.js';
import { input } from '../core/input.js';
import { audio } from '../core/audio.js';
import { G, flag, setFlag, itemCount, saveGame } from '../core/state.js';
import { MapView } from '../world/MapView.js';
import { Actor, DIRS, OPP } from '../world/Actor.js';
import { Lighting, Weather, timeOfDay } from '../world/Atmosphere.js';
import { UI } from './UIScene.js';
import { ScriptAPI, runScript, evalCond } from '../core/script.js';
import { rollEncounter } from '../data/encounters.js';
import { TRAINERS } from '../data/trainers.js';
import { ITEMS } from '../data/items.js';
import { txt } from '../ui/text.js';

export class WorldScene extends Phaser.Scene {
  constructor() { super('World'); }

  init(data) {
    this.initData = data || {};
  }

  create() {
    this.busy = 0;            // >0 while a script/transition controls the game
    this.npcs = [];
    this.itemsOnMap = [];
    this.mapView = null;
    this.player = null;
    this.stepCount = 0;
    this.lastEnc = 0;
    this.S = new ScriptAPI(this);
    this.lighting = new Lighting(this);
    this.weather = new Weather(this);
    this.grassFront = this.add.image(0, 0, 'ui', 'grass_front').setOrigin(0.5, 1).setVisible(false);
    this.cameras.main.setRoundPixels(true);
    this.debugText = DEBUG ? txt(this, 4, 4, '', { face: 'small', scroll: false, depth: DEPTH.fx + 10 }) : null;

    const d = this.initData;
    const p = G.state.player;
    if (d.debugMap) {
      p.map = d.debugMap;
      if (d.x !== null && d.x !== undefined) { p.x = d.x; p.y = d.y; }
      else { const sp = this._spawnPoint(d.debugMap); p.x = sp[0]; p.y = sp[1]; }
    }
    this.loadMap(p.map, p.x, p.y, p.face, { first: true });
    input.focus = ['world'];

    this.events.on('wake', () => { input.clear(); });
    this.events.on('resume', () => { input.clear(); });
  }

  _spawnPoint(mapId) {
    const raw = this.cache.tilemap.get(`map_${mapId}`).data;
    const objs = (raw.layers.find((l) => l.type === 'objectgroup') || { objects: [] }).objects;
    const s = objs.find((o) => (o.type || o.class) === 'spawn') || objs.find((o) => (o.type || o.class) === 'warp');
    return s ? [Math.floor(s.x / TILE), Math.floor(s.y / TILE) - ((s.type || s.class) === 'warp' ? 1 : 0)] : [Math.floor(raw.width / 2), Math.floor(raw.height / 2)];
  }

  // ─── map loading ────────────────────────────────────────────────────────
  loadMap(id, x, y, face = 'down', opts = {}) {
    if (this.mapView) {
      this.mapView.destroy();
      this.npcs.forEach((n) => n.actor.destroy());
      this.itemsOnMap.forEach((i) => i.sprite && i.sprite.destroy());
    }
    const prevMap = G.state.player.map;
    this.mapView = new MapView(this, id);
    const mv = this.mapView;
    G.state.player.map = id;
    G.state.player.x = x; G.state.player.y = y; G.state.player.face = face;
    if (!this.player) {
      this.player = new Actor(this, this.playerSprite(), x, y, face);
    } else {
      this.player.setSprite(this.playerSprite());
      this.player.warp(x, y, face);
    }
    this.player.setSkiff(!!G.state.player.surfing && mv.behavior(x, y) === 'water');
    if (!this.player.skiff) { G.state.player.surfing = false; }
    // camera
    const cam = this.cameras.main;
    if (mv.pw < GAME_W || mv.ph < GAME_H) {
      const bx = mv.pw < GAME_W ? -(GAME_W - mv.pw) / 2 : 0;
      const by = mv.ph < GAME_H ? -(GAME_H - mv.ph) / 2 : 0;
      cam.setBounds(Math.floor(bx), Math.floor(by), Math.max(GAME_W, mv.pw), Math.max(GAME_H, mv.ph));
    } else {
      cam.setBounds(0, 0, mv.pw, mv.ph);
    }
    cam.startFollow(this.player.sprite, true, 1, 1, 0, -4);
    // NPCs, items, brambles
    this.npcs = [];
    this.itemsOnMap = [];
    for (const o of mv.objects) {
      if (o.type === 'npc') { this._spawnNpc(o); }
      if (o.type === 'item') { this._spawnItem(o); }
      if (o.type === 'bramble') { this._spawnBramble(o); }
    }
    // atmosphere
    const light = mv.props.light || (mv.props.kind === 'interior' ? 'indoor' : 'outdoor');
    this.lighting.setMode(light === 'dark' ? 'dark' : (light === 'indoor' ? 'indoor' : 'outdoor'));
    this.weather.set(mv.props.weather || 'none');
    audio.playMusic(mv.props.music ? `bgm_${mv.props.music}` : null);
    if (!opts.first && mv.props.kind !== 'interior' && prevMap !== id && this._regionName(prevMap) !== mv.name) {
      UI.banner(mv.name);
    } else if (opts.first && mv.props.kind !== 'interior') {
      UI.banner(mv.name);
    }
    if (mv.props.kind !== 'interior' && mv.props.fly) { setFlag(`visited_${id}`); }
    this.justWarped = true;
    this._updateGrass();
    // on-enter map script
    this.time.delayedCall(10, () => this._mapEnter(id, opts));
  }

  _regionName(mapId) {
    const idx = this.cache.json.get('mapIndex');
    return idx && idx[mapId] ? idx[mapId].name : '';
  }

  async _mapEnter(id, opts) {
    const key = `map:${id}`;
    await this.run(key, { first: opts.first });
    this.checkTrainers();
  }

  playerSprite() {
    return ['player_a', 'player_b', 'player_c', 'player_d'][G.state.player.style || 0];
  }

  _npcVisible(pr, id) {
    if (flag(`left_${id}`)) { return false; }
    return evalCond(pr.show, true) && !(pr.hide && evalCond(pr.hide, false));
  }

  _spawnNpc(o) {
    const pr = o.props;
    const visible = this._npcVisible(pr, pr.id || `npc${o.id}`);
    const actor = new Actor(this, pr.sprite || 'man', o.x, o.y, pr.face || 'down');
    const npc = { id: pr.id || `npc${o.id}`, def: pr, actor, home: [o.x, o.y], timer: 1000 + Math.random() * 2000, pathIdx: 0, obj: o };
    actor.setVisible(visible);
    npc.active = visible;
    this.npcs.push(npc);
  }

  refreshNpcs() {
    for (const n of this.npcs) {
      if (n.forced) { continue; }
      const vis = this._npcVisible(n.def, n.id);
      if (vis !== n.active) {
        n.active = vis;
        n.actor.setVisible(vis);
        if (vis) { n.actor.warp(n.home[0], n.home[1], n.def.face || 'down'); }
      }
    }
  }

  _spawnItem(o) {
    const f = o.props.flag || `item_${this.mapView.id}_${o.x}_${o.y}`;
    if (flag(f)) { return; }
    const hidden = o.props.hidden === '1' || o.props.hidden === true;
    const sprite = hidden ? null : this.add.image(o.x * TILE + 8, o.y * TILE + 16, 'ui', 'item_ball').setOrigin(0.5, 1).setDepth(DEPTH.actors + (o.y * TILE + 16) / 100);
    this.itemsOnMap.push({ o, flag: f, hidden, sprite });
  }

  _spawnBramble(o) {
    const f = o.props.flag || `bramble_${this.mapView.id}_${o.x}_${o.y}`;
    if (flag(f)) { this.mapView.setBehavior(o.x, o.y, 'none'); return; }
    const sprite = this.add.image(o.x * TILE + 8, o.y * TILE + 16, 'ui', 'bramble').setOrigin(0.5, 1).setDepth(DEPTH.actors + (o.y * TILE + 16) / 100);
    this.mapView.setBehavior(o.x, o.y, 'solid');
    this.itemsOnMap.push({ o, flag: f, bramble: true, sprite });
  }

  npcAt(x, y) {
    return this.npcs.find((n) => n.active && n.actor.tx === x && n.actor.ty === y);
  }
  npcById(id) { return this.npcs.find((n) => n.id === id); }

  itemAt(x, y) { return this.itemsOnMap.find((i) => i.o.x === x && i.o.y === y); }

  // ─── update loop ────────────────────────────────────────────────────────
  update(time, delta) {
    const mv = this.mapView;
    if (!mv) { return; }
    mv.update(delta);
    // clock
    if (!this.busy && input.has('world')) {
      G.state.playMs += delta;
      if (G.settings.clock === 'real') {
        const d = new Date();
        G.state.clock = d.getHours() * 60 + d.getMinutes();
      } else {
        G.state.clock += delta / REAL_MS_PER_GAME_MIN;
        if (G.state.clock >= 1440) { G.state.clock -= 1440; G.state.day += 1; }
      }
    }
    this.lighting.update(G.state.clock, mv.lights, this.cameras.main, this.player, this.weather.dim);
    this.weather.update(delta, this.cameras.main);
    this._updateGrass();
    if (this.debugText) { this.debugText.setText(`${mv.id} ${this.player.tx},${this.player.ty} ${Math.floor(G.state.clock / 60)}:${String(Math.floor(G.state.clock % 60)).padStart(2, '0')} ${timeOfDay(G.state.clock)} ${input.top()}`); }
    this._updateNpcs(delta);
    if (this.busy || !input.has('world') || this.player.moving) { return; }

    if (DEBUG && input.pressed('debug', 'world')) { this.openDebug(); return; }
    if (input.pressed('menu', 'world')) { this.openMenu(); return; }
    if (input.pressed('confirm', 'world')) { this.interact(); return; }
    const dir = input.heldDir('world');
    if (dir) { this.tryMove(dir); } else { this._heldSince = null; this._turnDir = null; }
  }

  _updateGrass() {
    const p = this.player;
    if (!p || !this.mapView) { return; }
    const onGrass = !p.moving && this.mapView.behavior(p.tx, p.ty) === 'grass';
    this.grassFront.setVisible(onGrass && !p.hidden);
    if (onGrass) {
      this.grassFront.setPosition(p.tx * TILE + 8, p.ty * TILE + 16).setDepth(p.sprite.depth + 0.01);
    }
  }

  _updateNpcs(delta) {
    if (this.busy) { return; }
    for (const n of this.npcs) {
      if (!n.active || n.actor.moving || n.frozen) { continue; }
      const mv = n.def.move || 'still';
      if (mv === 'still') { continue; }
      n.timer -= delta;
      if (n.timer > 0) { continue; }
      n.timer = 1400 + Math.random() * 2600;
      if (mv === 'look' || mv === 'spin') {
        const dirs = ['down', 'left', 'right', 'up'];
        n.actor.setFace(dirs[Math.floor(Math.random() * 4)]);
        if (n.def.trainer) { this.checkTrainers(); }
        continue;
      }
      if (mv === 'wander') {
        const dirs = ['down', 'left', 'right', 'up'];
        const d = dirs[Math.floor(Math.random() * 4)];
        const [dx, dy] = DIRS[d];
        const nx = n.actor.tx + dx, ny = n.actor.ty + dy;
        const r = +(n.def.radius || 2);
        if (Math.abs(nx - n.home[0]) > r || Math.abs(ny - n.home[1]) > r || !this.walkableForNpc(nx, ny)) {
          n.actor.setFace(d);
          continue;
        }
        n.actor.walk(d, WALK_MS * 1.3);
      }
    }
  }

  walkableForNpc(x, y) {
    const b = this.mapView.behavior(x, y);
    if (!['none', 'bridge', 'grass', 'noenc'].includes(b)) { return false; }
    if (this.player.tx === x && this.player.ty === y) { return false; }
    if (this.npcAt(x, y)) { return false; }
    if (this.itemAt(x, y) && !this.itemAt(x, y).hidden) { return false; }
    return true;
  }

  // ─── movement ──────────────────────────────────────────────────────────
  async tryMove(dir) {
    const p = this.player;
    const mv = this.mapView;
    // turn on the spot first (tap to turn)
    if (p.face !== dir && !this._heldSince) {
      p.setFace(dir);
      this._heldSince = this.time.now;
      this._turnDir = dir;
      return;
    }
    if (this._turnDir === dir && this._heldSince && this.time.now - this._heldSince < 90) { return; }
    this._heldSince = null; this._turnDir = null;
    p.setFace(dir);
    const [dx, dy] = DIRS[dir];
    const nx = p.tx + dx, ny = p.ty + dy;
    // leaving the map through a connection
    if (!mv.inBounds(nx, ny)) {
      const side = dx < 0 ? 'west' : dx > 0 ? 'east' : dy < 0 ? 'north' : 'south';
      const conn = mv.props[side];
      if (conn) { await this.followConnection(side, conn, nx, ny, dir); }
      else { this.bump(); }
      return;
    }
    const b = mv.behavior(nx, ny);
    // doors & warps entered by walking into them
    const warp = mv.objectsAt(nx, ny, 'warp')[0];
    if (b === 'door' || (warp && (warp.props.door === '1' || warp.props.door === true))) {
      if (warp) { await this.doWarp(warp, dir); return; }
    }
    // ledges
    if ((b === 'ledge_down' && dir === 'down') || (b === 'ledge_left' && dir === 'left') || (b === 'ledge_right' && dir === 'right')) {
      const lx = nx + dx, ly = ny + dy;
      if (this.isWalkable(lx, ly, dir)) {
        this.busy++;
        audio.blip('jump');
        await p.hop(dir, 2);
        this.busy--;
        await this.afterStep();
        return;
      }
    }
    if (!this.isWalkable(nx, ny, dir)) { this.bump(); return; }
    // surfing transitions
    if (G.state.player.surfing && b !== 'water') {
      G.state.player.surfing = false;
      p.setSkiff(false);
    }
    const running = !G.state.player.surfing && itemCount('trail_boots') > 0 && (G.settings.autoRun ? !input.isDown('run') : input.isDown('run'));
    const ms = G.state.player.surfing ? SURF_MS : (running ? RUN_MS : WALK_MS);
    this._stepSfx();
    await p.walk(dir, ms);
    await this.afterStep();
  }

  _stepSfx() {
    if (G.state.player.surfing) { return; }
    audio.sfx('step', { volume: 0.35, throttle: 90 });
  }

  bump() {
    const now = this.time.now;
    if (!this._lastBump || now - this._lastBump > 380) { audio.blip('bump'); this._lastBump = now; }
  }

  isWalkable(x, y, dir) {
    const mv = this.mapView;
    if (!mv.inBounds(x, y)) { return false; }
    const b = mv.behavior(x, y);
    if (this.npcAt(x, y)) { return false; }
    const it = this.itemAt(x, y);
    if (it && !it.hidden) { return false; }
    if (b === 'water') { return !!G.state.player.surfing; }
    if (['solid', 'counter', 'door', 'ledge_down', 'ledge_left', 'ledge_right'].includes(b)) { return false; }
    return true;
  }

  async afterStep() {
    const p = this.player;
    const mv = this.mapView;
    G.state.player.x = p.tx; G.state.player.y = p.ty; G.state.player.face = p.face;
    G.state.steps++;
    this.justWarped = false;
    if (G.state.repel > 0) {
      G.state.repel--;
      if (G.state.repel === 0) { this.busy++; await UI.say(null, 'The Ward Incense wore off.'); this.busy--; }
    }
    // step warps (stairs, mats, holes)
    const w = mv.objectsAt(p.tx, p.ty, 'warp')[0];
    if (w && !(w.props.door === '1' || w.props.door === true)) { await this.doWarp(w, p.face); return; }
    // triggers
    for (const t of mv.objectsAt(p.tx, p.ty, 'trigger')) {
      const pr = t.props;
      if (pr.once && flag(pr.once)) { continue; }
      if (pr.cond && !evalCond(pr.cond, true)) { continue; }
      await this.run(pr.script, { trigger: t });
      if (pr.once) { setFlag(pr.once); }
      return;
    }
    // trainers
    if (this.checkTrainers()) { return; }
    // encounters
    await this.checkEncounter();
  }

  async followConnection(side, conn, nx, ny, dir) {
    const [target, offStr] = String(conn).split(/\s+/);
    const off = parseInt(offStr || '0', 10);
    const idx = this.cache.json.get('mapIndex');
    const t = idx[target];
    if (!t) { this.bump(); return; }
    let x, y;
    if (side === 'north') { x = nx + off; y = t.h - 1; }
    if (side === 'south') { x = nx + off; y = 0; }
    if (side === 'west') { x = t.w - 1; y = ny + off; }
    if (side === 'east') { x = 0; y = ny + off; }
    await this.transition(target, x, y, dir, { fade: 180 });
  }

  async doWarp(w, dir) {
    const [map, xy] = String(w.props.to).split(':');
    const [x, y] = xy.split(',').map((v) => parseInt(v, 10));
    const isDoor = w.props.door === '1' || w.props.door === true;
    if (w.props.cond && !evalCond(w.props.cond, true)) {
      this.busy++;
      await UI.say(null, w.props.locked || "It's locked.");
      this.busy--;
      return;
    }
    audio.sfx(isDoor || w.props.mat ? 'door' : 'step');
    await this.transition(map, x, y, w.props.face || (isDoor ? 'up' : dir), { fade: 220 });
  }

  transition(map, x, y, face, { fade = 250 } = {}) {
    this.busy++;
    const cam = this.cameras.main;
    return new Promise((resolve) => {
      cam.fadeOut(fade, 8, 7, 14);
      cam.once('camerafadeoutcomplete', () => {
        this.loadMap(map, x, y, face);
        cam.fadeIn(fade, 8, 7, 14);
        this.busy--;
        input.clear();
        resolve();
      });
    });
  }

  // ─── interaction ──────────────────────────────────────────────────────
  async interact() {
    const p = this.player;
    const mv = this.mapView;
    let [fx, fy] = p.facingTile();
    let n = this.npcAt(fx, fy);
    if (!n && mv.behavior(fx, fy) === 'counter') {
      const [dx, dy] = DIRS[p.face];
      n = this.npcAt(fx + dx, fy + dy);
    }
    if (n) { await this.talkTo(n); return; }
    const it = this.itemAt(fx, fy) || (this.itemAt(p.tx, p.ty) && this.itemAt(p.tx, p.ty).hidden ? this.itemAt(p.tx, p.ty) : null);
    if (it && it.bramble) { await this.cutBramble(it); return; }
    if (it) { await this.pickUp(it); return; }
    const sign = mv.objectsAt(fx, fy, 'sign')[0];
    if (sign) {
      this.busy++;
      if (sign.props.script) { await this.run(sign.props.script, { sign }); }
      else if (sign.props.text) { await UI.say(null, sign.props.text); }
      this.busy--;
      return;
    }
    // water: launch the skiff
    if (mv.behavior(fx, fy) === 'water' && !G.state.player.surfing) {
      this.busy++;
      if (itemCount('skiff') > 0) {
        if (await UI.ask(null, 'The water is calm. Launch the Skiff?')) {
          G.state.player.surfing = true;
          p.setSkiff(true);
          audio.blip('splash');
          await p.walk(p.face, SURF_MS);
          await this.afterStep();
        }
      } else {
        await UI.say(null, 'The water is deep and blue. A boat would help here.');
      }
      this.busy--;
      return;
    }
    // map-specific tile scripts (e.g. bookshelves) are signs; nothing else here.
  }

  async talkTo(n) {
    const p = this.player;
    this.busy++;
    n.frozen = true;
    if (!n.def.noturn) { n.actor.setFace(OPP[p.face]); }
    try {
      if (n.def.trainer && !G.state.defeated[n.def.trainer]) {
        await this.trainerEncounter(n, false);
      } else if (n.def.script) {
        await this.run(n.def.script, { npc: n });
      } else if (n.def.trainer) {
        const tr = TRAINERS[n.def.trainer];
        await UI.say(tr ? tr.name : n.def.name, (tr && tr.after) || n.def.text || '...');
      } else {
        await UI.say(n.def.name || null, n.def.text || '...');
      }
    } finally {
      n.frozen = false;
      this.busy--;
    }
  }

  async cutBramble(it) {
    this.busy++;
    try {
      if (itemCount('brush_hook') <= 0) {
        await UI.say(null, 'A thick tangle of thorny bramble blocks the way.|A sharp blade could clear it...');
        return;
      }
      if (!(await UI.ask(null, 'A thorny bramble blocks the way. Clear it with the Brush Hook?'))) { return; }
      audio.blip('cut');
      setFlag(it.flag);
      this.mapView.setBehavior(it.o.x, it.o.y, 'none');
      this.itemsOnMap = this.itemsOnMap.filter((x) => x !== it);
      await new Promise((r) => this.tweens.add({ targets: it.sprite, alpha: 0, scaleX: 1.4, scaleY: 0.2, duration: 260, onComplete: r }));
      it.sprite.destroy();
    } finally {
      this.busy--;
    }
  }

  async pickUp(it) {
    this.busy++;
    const id = it.o.props.item;
    const qty = +(it.o.props.qty || 1);
    setFlag(it.flag);
    if (it.sprite) { it.sprite.destroy(); }
    this.itemsOnMap = this.itemsOnMap.filter((x) => x !== it);
    await this.S.give(id, qty, { found: true });
    this.busy--;
  }

  // ─── trainers ──────────────────────────────────────────────────────────
  checkTrainers() {
    if (this.busy) { return false; }
    const p = this.player;
    for (const n of this.npcs) {
      if (!n.active || !n.def.trainer || G.state.defeated[n.def.trainer]) { continue; }
      const range = +(n.def.sight || 4);
      const [dx, dy] = DIRS[n.actor.face];
      for (let i = 1; i <= range; i++) {
        const x = n.actor.tx + dx * i, y = n.actor.ty + dy * i;
        if (x === p.tx && y === p.ty) {
          this.trainerEncounter(n, true);
          return true;
        }
        const b = this.mapView.behavior(x, y);
        if (['solid', 'counter', 'door'].includes(b) || this.npcAt(x, y)) { break; }
      }
    }
    return false;
  }

  async trainerEncounter(n, spotted) {
    this.busy++;
    const p = this.player;
    try {
      if (spotted) {
        audio.sfx('encounter');
        await n.actor.emote('!', 650);
        // walk up to the player
        const dir = n.actor.face;
        const [dx, dy] = DIRS[dir];
        while (n.actor.tx + dx !== p.tx || n.actor.ty + dy !== p.ty) {
          await n.actor.walk(dir, WALK_MS);
        }
        p.setFace(OPP[dir]);
      }
      const tr = TRAINERS[n.def.trainer];
      if (n.def.script) {
        await this.run(n.def.script, { npc: n, trainer: tr });
      } else {
        await UI.say(tr.name, tr.intro || 'Let\'s battle!');
        const result = await this.S.battle(n.def.trainer);
        if (result === 'win' && (n.def.leave === '1' || n.def.leave === true)) { await this.npcLeave(n); }
      }
    } finally {
      this.busy--;
    }
  }

  // A beaten Deepcall grunt flees: hop, fade out, never return.
  async npcLeave(n) {
    await n.actor.emote('...', 500);
    setFlag(`left_${n.id}`);
    await new Promise((r) => this.tweens.add({ targets: n.actor.sprite, alpha: 0, y: n.actor.sprite.y - 6, duration: 350, onComplete: r }));
    n.active = false;
    n.actor.setVisible(false);
    n.actor.sprite.setAlpha(1);
  }

  // ─── encounters ──────────────────────────────────────────────────────
  async checkEncounter() {
    const mv = this.mapView;
    const p = this.player;
    const b = mv.behavior(p.tx, p.ty);
    let kind = null;
    if (b === 'grass') { kind = 'grass'; }
    else if (b === 'water' && G.state.player.surfing) { kind = 'water'; }
    else if ((mv.props.enc_floor === '1' || mv.props.enc_floor === true) && b === 'none') { kind = 'cave'; }
    if (!kind) { return; }
    this.lastEnc++;
    const rate = kind === 'grass' ? 0.1 : kind === 'water' ? 0.075 : 0.07;
    if (this.lastEnc < 3 || Math.random() > rate) { return; }
    const mon = rollEncounter(mv.id, kind, G.state.clock);
    if (!mon) { return; }
    const lead = G.state.party.find((m) => m.hp > 0);
    if (G.state.repel > 0 && lead && mon.level < lead.level) { return; }
    this.lastEnc = 0;
    await this.S.wild(mon.species, mon.level, { kindEnc: kind });
  }

  // ─── scripts ─────────────────────────────────────────────────────────
  async run(id, ctx = {}) {
    if (!id) { return; }
    this.busy++;
    try {
      await runScript(id, this.S, ctx);
    } catch (e) {
      console.error('[script]', id, e);
    } finally {
      this.busy--;
      input.clear();
    }
  }

  openMenu() {
    audio.sfx('select');
    this.busy++;
    this.scene.launch('Menu', { onClose: () => { this.busy--; input.clear(); } });
    this.scene.bringToTop('Menu');
    this.scene.bringToTop('UI');
  }

  async openDebug() {
    const { debugMenu } = await import('../core/debug.js');
    this.busy++;
    await debugMenu(this);
    this.busy--;
  }

  // Called by scripts / battles after the party is healed etc.
  autosave() { saveGame(); }
}
