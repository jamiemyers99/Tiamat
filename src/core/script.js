// Event scripting: every story beat, NPC and sign runs through this API.
// Scripts are async functions registered in src/scripts/*.js:
//   'rootmere.mum': async (S, ctx) => { await S.say('Mum', 'Morning!'); }
import { G, flag, setFlag, getVar, setVar, giveItem, takeItem, itemCount, addMoney, receiveMorph, markCaught, markSeen, saveGame } from './state.js';
import { audio } from './audio.js';
import { input } from './input.js';
import { UI } from '../scenes/UIScene.js';
import { DIRS, OPP } from '../world/Actor.js';
import { WALK_MS, TILE } from '../config.js';
import { ITEMS } from '../data/items.js';
import { createMon, healMon } from '../battle/mon.js';
import { SPECIES } from '../data/species.js';
import { SCRIPTS } from '../scripts/index.js';
import { timeOfDay } from '../world/Atmosphere.js';

export function evalCond(expr, dflt = true) {
  if (expr === undefined || expr === null || expr === '') { return dflt; }
  const s = String(expr).trim();
  if (s.includes('|')) { return s.split('|').some((p) => evalCond(p, dflt)); }
  if (s.includes('&')) { return s.split('&').every((p) => evalCond(p, dflt)); }
  if (s.startsWith('!')) { return !evalCond(s.slice(1), dflt); }
  if (s.startsWith('has:')) { return itemCount(s.slice(4)) > 0; }
  if (s.startsWith('sigils>=')) { return G.state.sigils.length >= +s.slice(8); }
  if (s.startsWith('time:')) { return timeOfDay(G.state.clock) === s.slice(5); }
  if (s.startsWith('beat:')) { return !!G.state.defeated[s.slice(5)]; }
  if (s.startsWith('party:')) { return G.state.party.some((m) => m.species === s.slice(6)); }
  if (s.startsWith('var:')) { const [k, v] = s.slice(4).split('='); return String(getVar(k)) === v; }
  if (s === 'party') { return G.state.party.length > 0; }
  return flag(s);
}

export async function runScript(id, S, ctx = {}) {
  const fn = SCRIPTS[id];
  if (!fn) {
    if (!String(id).startsWith('map:')) { console.warn('[script] missing', id); }
    return;
  }
  await fn(S, ctx);
}

export class ScriptAPI {
  constructor(world) { this.w = world; }

  get state() { return G.state; }
  get player() { return this.w.player; }
  get name() { return G.state.player.name; }

  // ── text ──
  say(name, text, opts) { return UI.say(name, text, opts); }
  ask(name, text, yes, no) { return UI.ask(name, text, yes, no); }
  choose(name, text, options) {
    return UI.choose(name, text, options.map((o) => (typeof o === 'string' ? { label: o, value: o } : o)));
  }
  toast(text, color) { UI.toast(text, color); }
  wait(ms) { return new Promise((r) => this.w.time.delayedCall(ms, r)); }

  // ── flags ──
  flag(k) { return flag(k); }
  set(k, v = true) { setFlag(k, v); this.w.refreshNpcs(); }
  clear(k) { setFlag(k, false); this.w.refreshNpcs(); }
  var(k, d) { return getVar(k, d); }
  setVar(k, v) { setVar(k, v); }
  cond(expr) { return evalCond(expr); }

  // ── actors ──
  actor(id) {
    if (id === 'player') { return this.w.player; }
    const n = this.w.npcById(id);
    return n ? n.actor : null;
  }
  npc(id) { return this.w.npcById(id); }

  async move(id, path, ms = WALK_MS) {
    const a = this.actor(id);
    if (!a) { return; }
    const steps = Array.isArray(path) ? path : String(path).split(',').map((s) => s.trim()).filter(Boolean);
    const map = { u: 'up', d: 'down', l: 'left', r: 'right' };
    for (const st of steps) {
      const m = st.match(/^([udlr]|up|down|left|right)(\d*)$/);
      if (!m) { continue; }
      const dir = map[m[1]] || m[1];
      const n = +(m[2] || 1);
      for (let i = 0; i < n; i++) { await a.walk(dir, ms); }
    }
    if (id === 'player') { G.state.player.x = a.tx; G.state.player.y = a.ty; G.state.player.face = a.face; }
  }
  face(id, dir) {
    const a = this.actor(id);
    if (!a) { return; }
    if (dir === 'player') {
      const p = this.w.player;
      const dx = p.tx - a.tx, dy = p.ty - a.ty;
      dir = Math.abs(dx) > Math.abs(dy) ? (dx > 0 ? 'right' : 'left') : (dy > 0 ? 'down' : 'up');
    }
    a.setFace(dir);
  }
  facePlayerTo(id) {
    const a = this.actor(id);
    const p = this.w.player;
    const dx = a.tx - p.tx, dy = a.ty - p.ty;
    p.setFace(Math.abs(dx) > Math.abs(dy) ? (dx > 0 ? 'right' : 'left') : (dy > 0 ? 'down' : 'up'));
  }
  emote(id, kind = '!', ms) { const a = this.actor(id); return a ? a.emote(kind, ms) : Promise.resolve(); }
  show(id, x, y, face) {
    const n = this.w.npcById(id);
    if (!n) { return; }
    n.active = true; n.forced = true;
    n.actor.setVisible(true);
    if (x !== undefined) { n.actor.warp(x, y, face || n.actor.face); }
  }
  hide(id) {
    const n = this.w.npcById(id);
    if (!n) { return; }
    n.active = false; n.forced = false;
    n.actor.setVisible(false);
  }
  // Release a scripted NPC back to its normal show/hide rules.
  release(id) { const n = this.w.npcById(id); if (n) { n.forced = false; this.w.refreshNpcs(); } }
  // Step the player back one tile (used by gatekeepers).
  async stepBack() {
    const p = this.w.player;
    const back = OPP[p.face];
    const [dx, dy] = DIRS[back];
    const face = p.face;
    if (this.w.isWalkable(p.tx + dx, p.ty + dy, back) || G.state.player.surfing) {
      await p.walk(back, WALK_MS);
      p.setFace(face);
      G.state.player.x = p.tx; G.state.player.y = p.ty;
    }
  }
  async block(name, text) {
    await this.say(name, text);
    await this.stepBack();
  }
  // Big sprite for cutscenes (e.g. Tiamat rising over the altar). Tile coords, anchored bottom-centre.
  spriteAt(tex, frame, x, y, opts = {}) {
    const img = this.w.add.image(x * TILE + 8, y * TILE + 16, tex, frame).setOrigin(0.5, 1).setDepth(opts.depth ?? 5000);
    if (opts.scale) { img.setScale(opts.scale); }
    if (opts.alpha !== undefined) { img.setAlpha(opts.alpha); }
    return img;
  }
  tweenP(cfg) { return new Promise((r) => this.w.tweens.add({ ...cfg, onComplete: r })); }
  // Walk an NPC to stand next to the player (Manhattan path, x first).
  async approach(id, ms = WALK_MS) {
    const a = this.actor(id);
    const p = this.w.player;
    let guard = 40;
    while (guard-- > 0 && Math.abs(a.tx - p.tx) + Math.abs(a.ty - p.ty) > 1) {
      const dx = p.tx - a.tx, dy = p.ty - a.ty;
      const dir = Math.abs(dx) > Math.abs(dy) ? (dx > 0 ? 'right' : 'left') : (dy > 0 ? 'down' : 'up');
      await a.walk(dir, ms);
    }
    this.face(id, 'player');
    this.facePlayerTo(id);
  }

  // ── camera & fx ──
  shake(ms = 300, k = 0.01) { this.w.cameras.main.shake(ms, k); return this.wait(ms); }
  flash(ms = 300) { this.w.cameras.main.flash(ms, 255, 255, 255); return this.wait(ms); }
  fadeOut(ms = 400) { return new Promise((r) => { this.w.cameras.main.fadeOut(ms, 8, 7, 14); this.w.cameras.main.once('camerafadeoutcomplete', r); }); }
  fadeIn(ms = 400) { return new Promise((r) => { this.w.cameras.main.fadeIn(ms, 8, 7, 14); this.w.cameras.main.once('camerafadeincomplete', r); }); }
  async pan(x, y, ms = 800) {
    const cam = this.w.cameras.main;
    cam.stopFollow();
    cam.pan(x * TILE + 8, y * TILE + 8, ms, 'Sine.easeInOut');
    await this.wait(ms);
  }
  async panBack(ms = 600) {
    const cam = this.w.cameras.main;
    cam.pan(this.w.player.sprite.x, this.w.player.sprite.y - 4, ms, 'Sine.easeInOut');
    await this.wait(ms);
    cam.startFollow(this.w.player.sprite, true, 1, 1, 0, -4);
  }

  // ── audio ──
  music(key) { audio.playMusic(key ? `bgm_${key}` : null); }
  sfx(key) { audio.sfx(key); }
  jingle(key) { return audio.jingle(key); }

  // ── items / money ──
  has(id, n = 1) { return itemCount(id) >= n; }
  count(id) { return itemCount(id); }
  take(id, n = 1) { return takeItem(id, n); }
  async give(id, qty = 1, { found = false, silent = false } = {}) {
    const it = ITEMS[id];
    giveItem(id, qty);
    if (silent) { return; }
    const nm = it ? it.name : id;
    const what = qty > 1 ? `${qty}× ${nm}` : `${/^[aeiou]/i.test(nm) ? 'an' : 'a'} ${nm}`;
    const verb = found ? 'found' : 'received';
    audio.jingle('jingle_item');
    const pocket = it ? it.pocketName : 'Bag';
    await UI.say(null, `{PLAYER} ${verb} ${it && it.key ? 'the ' + nm : what}!|{PLAYER} put ${qty > 1 ? 'them' : 'it'} in the ${pocket} pocket.`);
  }
  money(n) { addMoney(n); if (n > 0) { audio.blip('coin'); } }

  // ── Morphs ──
  async giveMorph(species, level, opts = {}) {
    const mon = createMon(species, level, { ot: G.state.player.name, ...opts });
    markCaught(species);
    const where = receiveMorph(mon);
    audio.jingle('jingle_item');
    const nm = SPECIES[species].name;
    if (where === 'party') {
      await UI.say(null, opts.text || `{PLAYER} received ${nm}!`);
    } else if (where) {
      await UI.say(null, `{PLAYER} received ${nm}!|Your party is full, so ${nm} was sent to storage.`);
    } else {
      await UI.say(null, `There's no room for ${nm}...`);
    }
    return mon;
  }
  partyHas(species) { return G.state.party.some((m) => m.species === species); }
  seen(species) { markSeen(species); }

  async heal({ silent = false } = {}) {
    G.state.party.forEach(healMon);
    if (!silent) { await audio.jingle('jingle_heal'); }
  }

  // ── battles ──
  battle(trainerId, opts = {}) { return this._battle({ kind: 'trainer', trainerId, ...opts }); }
  wild(species, level, opts = {}) { return this._battle({ kind: 'wild', species, level, ...opts }); }

  // Battles are queued so two scripts can never start overlapping battles.
  _battle(data) {
    const run = () => this._battleNow(data);
    this._battleQueue = (this._battleQueue || Promise.resolve()).then(run, run);
    return this._battleQueue;
  }

  _battleNow(data) {
    const w = this.w;
    return new Promise((resolve) => {
      w.busy++;
      input.push('battle-transition');
      w.scene.launch('Transition', {
        style: data.kind === 'trainer' ? (data.boss ? 'boss' : 'trainer') : 'wild',
        onCovered: () => {
          input.pop('battle-transition');
          w.scene.sleep('World');
          w.scene.launch('Battle', {
            ...data,
            onEnd: async (result) => {
              w.scene.stop('Battle');
              w.scene.wake('World');
              w.cameras.main.fadeIn(300, 8, 7, 14);
              audio.playMusic(w.mapView.props.music ? `bgm_${w.mapView.props.music}` : null, { restart: true });
              if (result.outcome === 'lose' && !data.noWhiteout) {
                await this.whiteout();
              }
              w.refreshNpcs();
              w.busy--;
              input.clear();
              resolve(result.outcome);
            },
          });
          w.scene.bringToTop('Battle');
          w.scene.bringToTop('UI');
        },
      });
      w.scene.bringToTop('Transition');
    });
  }

  // Roll the credits over the world and wait for them to finish.
  credits() {
    const w = this.w;
    return new Promise((resolve) => {
      w.busy++;
      w.scene.launch('Credits', { onDone: () => { w.busy--; input.clear(); resolve(); } });
      w.scene.bringToTop('Credits');
    });
  }

  async whiteout() {
    const lost = Math.floor(G.state.money / 2);
    G.state.money -= lost;
    await UI.say(null, `{PLAYER} is out of usable Morphs!|{PLAYER} dropped ${lost}¢ in the panic...|...and hurried back to safety, shielding the party.`);
    G.state.party.forEach(healMon);
    const h = G.state.lastHeal;
    await this.fadeOut(300);
    this.w.loadMap(h.map, h.x, h.y, 'down');
    await this.fadeIn(400);
    if (h.map.endsWith('_haven')) {
      await UI.say('Haven Keeper', "Oh, you poor things. Your Morphs are all rested now — please be more careful out there.");
    } else {
      await UI.say('Mum', "{PLAYER}! You look exhausted. Rest up — your Morphs are fine now, love.");
    }
  }

  // ── world ──
  async warp(map, x, y, face = 'down', fade = 300) {
    await this.w.transition(map, x, y, face, { fade });
  }
  setHealPoint(map, x, y) { G.state.lastHeal = { map, x, y }; }
  save() { return saveGame(); }
  sigil(id) { if (!G.state.sigils.includes(id)) { G.state.sigils.push(id); } }
  refresh() { this.w.refreshNpcs(); }
  // Run another script inline (shares this script's busy lock).
  run(id, ctx = {}) { return runScript(id, this, ctx); }
  lockSurf(v) { G.state.player.surfing = v; this.w.player.setSkiff(v); }

  // Open a sub-screen (shop, storage, etc.) and wait for it to close.
  openScreen(mode, data = {}) {
    const w = this.w;
    return new Promise((resolve) => {
      w.scene.launch('Menu', { mode, ...data, onClose: (res) => { input.clear(); resolve(res); } });
      w.scene.bringToTop('Menu');
      w.scene.bringToTop('UI');
    });
  }
}
