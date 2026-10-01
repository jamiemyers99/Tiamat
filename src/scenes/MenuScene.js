// Pause menu and every full-screen sub-screen: Team, Summary, Bag, Index,
// Tamer Card, Options, Save, Reach Map, Shop and Storage.
import Phaser from 'phaser';
import { GAME_W, GAME_H, MONEY_CAP } from '../config.js';
import { input, DEFAULT_KEYS, REBINDABLE, ESSENTIAL, keyName } from '../core/input.js';
import { audio } from '../core/audio.js';
import { RESCUES, openRescues } from '../data/rescue.js';
import { G, saveGame, readSlot, loadGame, saveSettings, itemCount, giveItem, takeItem, addMoney, flag, hasCaughtForm, hasSeenForm } from '../core/state.js';
import { NATURES, natureText } from '../data/natures.js';
import { playerStyleKey } from '../data/players.js';
import { SPECIES, SPECIES_LIST } from '../data/species.js';
import { MOVES } from '../data/moves.js';
import { ITEMS, POCKETS, canLearnDisc } from '../data/items.js';
import { TYPE_COLORS } from '../data/types.js';
import { calcStats, maxHp, monName, monFrame, sexSymbol, xpProgress, xpToNext, STAT_KEYS, addXp, learnMove, replaceMove, evolutionTarget, healMon, rememberableMoves } from '../battle/mon.js';
import { pickMove } from '../ui/moveScreen.js';
import { txt, wrap, fmt, fmtKeys, measure } from '../ui/text.js';
import { panel, selBar, sexMark, choose, ListMenu, Bar } from '../ui/widgets.js';
import { UI } from './UIScene.js';
import { REGION } from '../data/region.js';
import { nameEntry } from '../ui/nameEntry.js';
import { timeOfDay } from '../world/Atmosphere.js';

const STAT_LABEL = { hp: 'HP', atk: 'Attack', def: 'Defense', spa: 'Sp. Atk', spd: 'Sp. Def', spe: 'Speed' };

const MENU_EXIT = Symbol('menu-exit');

// PC box wallpapers (pattern drawn in MenuScene._wallpaper). Saved per box as an index into this list.
const WALLPAPERS = [
  { id: 'meadow', name: 'Meadow', base: 0x2f5a3a, accent: 0x3d7049, pattern: 'grass' },
  { id: 'ocean', name: 'Ocean', base: 0x1d4468, accent: 0x2a5a86, pattern: 'waves' },
  { id: 'ember', name: 'Ember', base: 0x5e2820, accent: 0x74352a, pattern: 'diamonds' },
  { id: 'frost', name: 'Frost', base: 0x4a6886, accent: 0x6886a4, pattern: 'snow' },
  { id: 'dusk', name: 'Dusk', base: 0x3f2a58, accent: 0x4d346a, pattern: 'stripes' },
  { id: 'stone', name: 'Stone', base: 0x46433f, accent: 0x58544f, pattern: 'bricks' },
  { id: 'blossom', name: 'Blossom', base: 0x683452, accent: 0x844466, pattern: 'petals' },
  { id: 'night', name: 'Night', base: 0x141838, accent: 0x3a4290, pattern: 'stars' },
];

export class MenuScene extends Phaser.Scene {
  constructor() { super('Menu'); }
  init(data) { this.cfg = data || {}; }

  async create() {
    this.owner = 'pause';
    // Track every per-frame listener this menu session adds, so none can outlive it
    // (fly / escape close the menu from deep inside nested sub-menus).
    const events = this.events;
    const added = [];
    const origOn = events.on;
    events.on = function (ev, fn, ctx) { if (ev === 'update') { added.push([fn, ctx]); } return origOn.call(this, ev, fn, ctx); };
    this._untrack = () => { events.on = origOn; for (const [fn, ctx] of added) { events.off('update', fn, ctx); } };
    input.push(this.owner);
    audio.setDuck(0.55);
    this.root = this.add.container(0, 0);
    let result = null;
    try {
      const mode = this.cfg.mode;
      if (mode === 'shop') { result = await this.shop(this.cfg.stock || [], this.cfg.title); }
      else if (mode === 'storage') { result = await this.storage(); }
      else if (mode === 'options') { result = await this.options(); }
      else if (mode === 'controls') { result = await this.controls(); }
      else if (mode === 'party-pick') { result = await this.party({ pick: true, title: this.cfg.title, filter: this.cfg.filter }); }
      else if (mode === 'map') { result = await this.reachMap(); }
      else if (mode === 'index') { result = await this.index(this.cfg.species); }
      else { result = await this.mainMenu(); }
    } catch (e) {
      if (e !== MENU_EXIT) { console.error('[menu]', e); }
    }
    input.pop(this.owner);
    audio.setDuck(1);
    this.cfg.onClose && this.cfg.onClose(result);
    const after = this._afterClose;
    this._afterClose = null;
    this._untrack();
    this.scene.stop();
    if (after) { after(); }
  }

  // Load a saved journey from the pause menu (the same three slots as the title screen).
  async loadMenu() {
    const slots = [0, 1, 2].map((i) => {
      const s = readSlot(i);
      if (!s) { return { label: `Slot ${i + 1}  — Empty`, value: i, disabled: true }; }
      if (s.corrupt) { return { label: `Slot ${i + 1}  — Damaged`, value: i, disabled: true }; }
      const h = Math.floor((s.playMs || 0) / 3600000), m = Math.floor(((s.playMs || 0) % 3600000) / 60000);
      const cur = i === G.slot ? ' (this one)' : '';
      return { label: `${s.player.name}${cur}`, right: `${(s.sigils || []).length}★  ${h}:${String(m).padStart(2, '0')}`, value: i, name: s.player.name };
    });
    const c = this.add.container(0, 0);
    c.add(this.dim(0.6));
    c.add(txt(this, GAME_W / 2, 70, 'Load which journey?', { align: 'center', color: 'gold' }));
    const pick = await choose(this, slots, { x: GAME_W / 2 - 100, y: 86, depth: 30 });
    c.destroy();
    if (pick === null || pick === undefined) { return; }
    const ok = await this.confirm(`Load ${slots[pick].name}'s journey (Slot ${pick + 1})? Anything since your last save will be lost.`);
    if (!ok) { return; }
    if (!loadGame(pick)) { audio.sfx('cancel'); await this.toast('That save could not be loaded.'); return; }
    audio.sfx('select');
    this.exitThen(() => {
      const w = this.scene.get('World');
      w.cameras.main.fadeOut(350, 0, 0, 0);
      w.cameras.main.once('camerafadeoutcomplete', () => { input.focus = ['world']; w.scene.restart({}); });
    });
  }

  // Close every open sub-menu at once and then run fn (used by fly / escape).
  exitThen(fn) {
    this._afterClose = fn;
    throw MENU_EXIT;
  }

  // helpers
  dim(alpha = 0.72) { return this.add.rectangle(0, 0, GAME_W, GAME_H, 0x0b0c16, alpha).setOrigin(0, 0); }
  waitKey(keys = ['confirm', 'cancel']) {
    return new Promise((resolve) => {
      const tick = () => { for (const k of keys) { if (input.pressed(k, this.owner)) { this.events.off('update', tick); resolve(k); return; } } };
      this.events.on('update', tick);
    });
  }
  loop(handler) {
    // handler(tick) returns undefined to continue, or a value to stop
    return new Promise((resolve) => {
      const tick = () => {
        if (!input.has(this.owner)) { return; }
        const v = handler();
        if (v !== undefined) { this.events.off('update', tick); resolve(v); }
      };
      this.events.on('update', tick);
    });
  }

  // ─── main menu ───────────────────────────────────────────────────────
  async mainMenu() {
    const items = [];
    if (G.state.party.length) { items.push({ label: 'Team', value: 'team', icon: 'menu_party' }); }
    items.push({ label: 'Bag', value: 'bag', icon: 'menu_bag' });
    if (flag('got_index')) { items.push({ label: 'Index', value: 'index', icon: 'menu_index' }); }
    if (itemCount('reach_map')) { items.push({ label: 'Map', value: 'map', icon: 'menu_map' }); }
    items.push({ label: G.state.player.name, value: 'card', icon: 'menu_card' });
    items.push({ label: 'Save', value: 'save', icon: 'menu_save' });
    items.push({ label: 'Load', value: 'load', icon: 'menu_load' });
    items.push({ label: 'Controls', value: 'controls', icon: 'menu_keys' });
    items.push({ label: 'Options', value: 'options', icon: 'menu_options' });
    items.push({ label: 'Close', value: 'close', icon: 'menu_exit' });
    let index = 0;
    for (;;) {
      const c = this.add.container(0, 0);
      const w = 118, h = items.length * 18 + 12;
      const x = GAME_W - w - 8, y = 8;
      c.add(panel(this, x, y, w, h, 'dark'));
      items.forEach((it, i) => c.add(this.add.image(x + 20, y + 13 + i * 18, 'ui', it.icon).setOrigin(0.5)));
      // info panel
      const map = this.scene.get('World').mapView;
      const hh = Math.floor(G.state.clock / 60), mm = Math.floor(G.state.clock % 60);
      c.add(panel(this, 8, 8, 160, 48, 'dark'));
      c.add(txt(this, 16, 14, map ? map.name : '', { color: 'gold' }));
      c.add(txt(this, 16, 28, `${String(hh).padStart(2, '0')}:${String(mm).padStart(2, '0')}  ${timeOfDay(G.state.clock)}`));
      c.add(txt(this, 16, 40, `${G.state.money.toLocaleString()}¢`, { color: 'green' }));
      const menu = new ListMenu(this, { items: items.map((it) => ({ label: `    ${it.label}`, value: it.value })), x, y: y + 3, width: w, rowH: 18, noPanel: true, index, depth: 10 });
      const v = await menu.run();
      index = menu.index;
      menu.destroy(); c.destroy();
      if (v === null || v === 'close') { return null; }
      if (v === 'team') { await this.party({}); }
      if (v === 'bag') { await this.bag({}); }
      if (v === 'index') { await this.index(); }
      if (v === 'map') { await this.reachMap(); }
      if (v === 'card') { await this.card(); }
      if (v === 'options') { await this.options(); }
      if (v === 'controls') { await this.controls(); }
      if (v === 'load') { await this.loadMenu(); }
      if (v === 'save') {
        const yes = await this.confirm('Save your progress?');
        if (yes) {
          const ok = saveGame();
          audio.sfx(ok ? 'heal' : 'cancel');
          await this.toast(ok ? 'Your journey has been saved.' : 'Saving failed — storage may be full or blocked.');
        }
      }
    }
  }

  async confirm(text) {
    const c = this.add.container(0, 0);
    c.add(this.dim(0.5));
    c.add(panel(this, GAME_W / 2 - 110, GAME_H / 2 - 30, 220, 34, 'dark'));
    c.add(txt(this, GAME_W / 2, GAME_H / 2 - 20, text, { align: 'center' }));
    const v = await choose(this, [{ label: 'Yes', value: true }, { label: 'No', value: false }], { x: GAME_W / 2 - 30, y: GAME_H / 2 + 8, width: 60 });
    c.destroy();
    return v === true;
  }

  async toast(text, ms = 0) {
    const c = this.add.container(0, 0);
    const lines = wrap(this, text, 300);
    const h = lines.length * 13 + 14;
    c.add(panel(this, GAME_W / 2 - 160, GAME_H / 2 - h / 2, 320, h, 'gold'));
    lines.forEach((l, i) => c.add(txt(this, GAME_W / 2, GAME_H / 2 - h / 2 + 8 + i * 13, l, { align: 'center' })));
    if (ms) { await new Promise((r) => this.time.delayedCall(ms, r)); } else { await this.waitKey(); }
    c.destroy();
  }

  // ─── team ─────────────────────────────────────────────────────────────
  async party({ pick = false, title = null, filter = null } = {}) {
    let i = 0;
    let swapFrom = null;
    for (;;) {
      const party = G.state.party;
      if (!party.length) { await this.toast("You don't have any Morphs yet."); return null; }
      const c = this.add.container(0, 0);
      c.add(this.dim(0.85));
      c.add(txt(this, 16, 10, title || (swapFrom !== null ? 'Move to where?' : 'Team'), { color: 'gold' }));
      c.add(txt(this, GAME_W - 16, 10, fmtKeys(pick ? '{BTN:confirm}: choose   {BTN:cancel}: back' : '{BTN:confirm}: options   {BTN:cancel}: back'), { face: 'small', color: 'gray', align: 'right' }));
      const rows = party.map((m, k) => {
        const x = 16 + (k % 2) * 228, y = 26 + Math.floor(k / 2) * 76;
        const ok = !filter || filter(m);
        c.add(panel(this, x, y, 220, 70, swapFrom === k ? 'gold' : (k === 0 ? 'teal' : 'dark')));
        c.add(this.add.image(x + 26, y + 30, 'mons', monFrame(m, 'i')).setScale(1.3).setAlpha(ok ? 1 : 0.4));
        c.add(txt(this, x + 52, y + 8, monName(m), { color: ok ? 'white' : 'gray' }));
        c.add(sexMark(this, x + 52, y + 8, m, monName(m)));
        c.add(txt(this, x + 212, y + 8, `Lv${m.level}`, { align: 'right', color: 'gold' }));
        SPECIES[m.species].types.forEach((t, j) => c.add(this.add.image(x + 52 + j * 38, y + 22, 'ui', `type_${t}`).setOrigin(0, 0)));
        const bar = new Bar(this, x + 52, y + 36, 110, 4);
        bar.set(m.hp / maxHp(m)); bar.addTo(c);
        c.add(txt(this, x + 212, y + 34, `${m.hp}/${maxHp(m)}`, { align: 'right', face: 'small' }));
        if (m.hp <= 0 || m.status) { c.add(this.add.image(x + 52, y + 46, 'ui', `st_${m.hp <= 0 ? 'faint' : m.status}`).setOrigin(0, 0)); }
        const xpb = new Bar(this, x + 52, y + 60, 150, 2, { kind: 'xp' }); xpb.set(xpProgress(m)); xpb.addTo(c);
        return { x, y };
      });
      const sel = this.add.rectangle(0, 0, 222, 72).setOrigin(0, 0).setStrokeStyle(2, 0xffd65c);
      c.add(sel);
      const draw = () => sel.setPosition(rows[i].x - 1, rows[i].y - 1);
      i = Math.min(i, party.length - 1);
      draw();
      const n = party.length;
      const action = await this.loop(() => {
        const o = this.owner;
        if (input.nav('left', o) && i % 2 === 1) { i--; audio.sfx('cursor'); draw(); }
        else if (input.nav('right', o) && i % 2 === 0 && i + 1 < n) { i++; audio.sfx('cursor'); draw(); }
        else if (input.nav('up', o) && i >= 2) { i -= 2; audio.sfx('cursor'); draw(); }
        else if (input.nav('down', o) && i + 2 < n) { i += 2; audio.sfx('cursor'); draw(); }
        else if (input.pressed('confirm', o)) { audio.sfx('select'); return 'ok'; }
        else if (input.pressed('cancel', o)) { audio.sfx('cancel'); return 'back'; }
        return undefined;
      });
      if (action === 'back') {
        c.destroy();
        if (swapFrom !== null) { swapFrom = null; continue; }
        return null;
      }
      if (pick) {
        c.destroy();
        if (filter && !filter(party[i])) { await this.toast("That Morph can't be chosen."); continue; }
        return i;
      }
      if (swapFrom !== null) {
        c.destroy();
        const t = party[swapFrom]; party[swapFrom] = party[i]; party[i] = t;
        swapFrom = null;
        continue;
      }
      // the team stays on screen behind the options
      const opt = await choose(this, [{ label: 'Summary', value: 'sum' }, { label: 'Moves', value: 'moves' }, { label: 'Switch', value: 'swap' }, { label: 'Item', value: 'item' }, { label: 'Nickname', value: 'nick' }, { label: 'Cancel', value: null }],
        { x: GAME_W - 12, y: GAME_H - 12, anchor: 'bottom-right', depth: 20 });
      c.destroy();
      if (opt === 'sum') { i = await this.summary(i); }
      if (opt === 'swap') { swapFrom = i; }
      if (opt === 'item') { await this.bag({ target: i }); }
      if (opt === 'nick') { await this.nickname(party[i]); }
      if (opt === 'moves') { await this.moveReminder(party[i]); }
    }
  }

  // Move Reminder (like the newer classics): swap in any move this Morph learned before, or should
  // have learned by its level — including moves from the stages it evolved from.
  async moveReminder(m) {
    const nm = monName(m);
    for (;;) {
      const choices = rememberableMoves(m);
      if (!choices.length) { await this.toast(`${nm} has no other moves to remember yet.`); return; }
      const id = await pickMove(this, m, { title: `Which move should ${nm} remember? (${choices.length} to choose from)`, choices, owner: this.owner });
      if (!id) { return; }
      if (m.moves.length < 4) {
        learnMove(m, id);
        audio.sfx('level_up');
        await this.toast(`${nm} remembered ${MOVES[id].name}!`);
        continue;
      }
      const idx = await pickMove(this, m, { title: `Forget which move to make room for ${MOVES[id].name}?`, newMove: id, owner: this.owner });
      if (idx === null || idx === -1) { continue; }
      const old = MOVES[m.moves[idx].id].name;
      replaceMove(m, idx, id);
      audio.sfx('level_up');
      await this.toast(`${nm} forgot ${old} and remembered ${MOVES[id].name}!`);
    }
  }

  async nickname(m) {
    const cur = monName(m);
    const name = await nameEntry(this, { title: `Nickname for ${SPECIES[m.species].name} (Clear + Done to reset)`, initial: m.nick || '', max: 12, owner: this.owner, allowEmpty: true, depth: 60 });
    if (name === null) { return; }
    const clean = name.replace(/[^A-Za-z0-9 '\-.!?]/g, '').slice(0, 12).trim();
    m.nick = clean || null;
    input.clear();
    await this.toast(`${cur} is now called ${monName(m)}.`);
  }

  // ─── summary ─────────────────────────────────────────────────────────
  async summary(i, list = G.state.party) {
    let page = 0;
    for (;;) {
      const party = list;
      const m = party[i];
      const sp = SPECIES[m.species];
      const st = calcStats(m);
      const c = this.add.container(0, 0);
      c.add(this.dim(0.92));
      c.add(panel(this, 8, 8, 170, 254, 'dark'));
      c.add(txt(this, 18, 16, monName(m), { color: 'gold' }));
      c.add(sexMark(this, 18, 16, m, monName(m)));
      c.add(txt(this, 168, 16, `Lv${m.level}`, { align: 'right' }));
      c.add(this.add.image(93, 132, 'mons', monFrame(m, 'f')).setOrigin(0.5, 1).setScale(1.3));
      if (m.shiny) { c.add(txt(this, 18, 30, '★ Radiant', { color: 'gold', face: 'small' })); }
      sp.types.forEach((t, j) => c.add(this.add.image(18 + j * 40, 142, 'ui', `type_${t}`).setOrigin(0, 0)));
      c.add(txt(this, 18, 156, `No. ${String(sp.num).padStart(3, '0')}  ${sp.name}`, { face: 'small', color: 'gray' }));
      c.add(txt(this, 18, 168, sp.cls, { face: 'small', color: 'gray' }));
      if (m.status) { c.add(this.add.image(18, 180, 'ui', `st_${m.status}`).setOrigin(0, 0)); }
      c.add(txt(this, 18, 196, `Tamer: ${m.ot || '—'}`, { face: 'small' }));
      c.add(txt(this, 18, 206, `Met at Lv${m.metLevel}`, { face: 'small' }));
      const tabs = ['Stats', 'Moves', 'Notes'];
      tabs.forEach((t, k) => {
        c.add(panel(this, 186 + k * 96, 8, 92, 20, k === page ? 'gold' : 'ghost'));
        c.add(txt(this, 232 + k * 96, 12, t, { align: 'center', color: k === page ? 'gold' : 'gray' }));
      });
      c.add(panel(this, 186, 32, 286, 230, 'dark'));
      if (page === 0) {
        STAT_KEYS.forEach((k, j) => {
          const y = 44 + j * 20;
          // nature: the raised stat is shown in red with +, the lowered one in blue with -
          const nat = NATURES[m.nature] || [];
          const up = nat[0] === k, down = nat[1] === k;
          c.add(txt(this, 198, y, `${STAT_LABEL[k]}${up ? ' +' : down ? ' -' : ''}`, { color: up ? 'red' : down ? 'blue' : 'white' }));
          const val = k === 'hp' ? `${m.hp}/${st.hp}` : `${st[k]}`;
          c.add(txt(this, 330, y, val, { align: 'right', color: 'gold' }));
          const bw = Math.min(120, Math.round(st[k] / (m.level * 2.2 + 10) * 60));
          c.add(this.add.rectangle(340, y + 3, 120, 5, 0x262a47).setOrigin(0, 0));
          c.add(this.add.rectangle(340, y + 3, bw, 5, [0x5ee07a, 0xff8a5a, 0xf5c542, 0x78c8ff, 0xb89aff, 0xf06292][j]).setOrigin(0, 0));
        });
        c.add(txt(this, 198, 160, natureText(m.nature), { face: 'small', color: 'gray' }));
        c.add(txt(this, 198, 172, 'Experience'));
        c.add(txt(this, 460, 172, `${m.xp}`, { align: 'right' }));
        c.add(txt(this, 198, 186, 'To next level'));
        c.add(txt(this, 460, 186, `${xpToNext(m)}`, { align: 'right' }));
        const xb = new Bar(this, 198, 202, 262, 3, { kind: 'xp' }); xb.set(xpProgress(m)); xb.addTo(c);
        const into = sp.evo ? SPECIES[sp.evo.into] : null;
        if (into && G.state.index.caught.includes(sp.evo.into)) { c.add(txt(this, 198, 216, `Evolves into ${into.name} at Lv${sp.evo.level}.`, { face: 'small', color: 'gray' })); }
        else if (sp.evo) { c.add(txt(this, 198, 216, 'It seems it could still grow...', { face: 'small', color: 'gray' })); }
      } else if (page === 1) {
        m.moves.forEach((mv, j) => {
          const d = MOVES[mv.id];
          const y = 42 + j * 50;
          c.add(this.add.rectangle(196, y, 266, 44, TYPE_COLORS[d.type], 0.18).setOrigin(0, 0).setStrokeStyle(1, TYPE_COLORS[d.type]));
          c.add(txt(this, 204, y + 5, d.name));
          c.add(this.add.image(204, y + 19, 'ui', `type_${d.type}`).setOrigin(0, 0));
          c.add(this.add.image(242, y + 19, 'ui', `cat_${d.cat}`).setOrigin(0, 0));
          c.add(txt(this, 454, y + 5, `PP ${mv.pp}/${mv.max}`, { align: 'right', face: 'small' }));
          c.add(txt(this, 454, y + 20, `POW ${d.power || '-'}  ACC ${d.acc ?? '-'}`, { align: 'right', face: 'small', color: 'gray' }));
          const dl = wrap(this, d.desc, 250, 'small');
          c.add(txt(this, 204, y + 32, dl[0] || '', { face: 'small', color: 'gray' }));
        });
      } else {
        const lines = wrap(this, sp.dex, 262);
        lines.forEach((l, j) => c.add(txt(this, 198, 44 + j * 13, l)));
        c.add(txt(this, 198, 150, `Friendship: ${m.friendship >= 200 ? 'Adores you' : m.friendship >= 120 ? 'Very close' : m.friendship >= 80 ? 'Friendly' : 'Getting used to you'}`, { face: 'small' }));
        c.add(txt(this, 198, 164, `Caught on: ${m.metMap ? (this.cache.json.get('mapIndex')[m.metMap] || {}).name || m.metMap : 'a gift'}`, { face: 'small' }));
      }
      c.add(txt(this, GAME_W - 12, GAME_H - 10, fmtKeys('left / right: page   up / down: Morph   {BTN:cancel}: back'), { face: 'small', color: 'gray', align: 'right' }));
      const act = await this.loop(() => {
        const o = this.owner;
        if (input.nav('left', o)) { return 'l'; }
        if (input.nav('right', o)) { return 'r'; }
        if (input.nav('up', o)) { return 'u'; }
        if (input.nav('down', o)) { return 'd'; }
        if (input.pressed('cancel', o) || input.pressed('confirm', o)) { return 'x'; }
        return undefined;
      });
      c.destroy();
      if (act === 'x') { audio.sfx('cancel'); return i; }
      audio.sfx('cursor');
      if (act === 'l') { page = (page + 2) % 3; }
      if (act === 'r') { page = (page + 1) % 3; }
      if (act === 'u') { i = (i + party.length - 1) % party.length; }
      if (act === 'd') { i = (i + 1) % party.length; }
    }
  }

  // ─── bag ─────────────────────────────────────────────────────────────
  async bag({ target = null } = {}) {
    let pocket = 0;
    let idx = 0;
    for (;;) {
      const pk = POCKETS[pocket];
      const ids = Object.keys(G.state.bag).filter((k) => ITEMS[k] && ITEMS[k].pocket === pk.id && G.state.bag[k] > 0)
        .sort((a, b) => Object.keys(ITEMS).indexOf(a) - Object.keys(ITEMS).indexOf(b));
      const c = this.add.container(0, 0);
      c.add(this.dim(0.9));
      POCKETS.forEach((p, k) => {
        c.add(panel(this, 8 + k * 118, 8, 114, 20, k === pocket ? 'gold' : 'ghost'));
        c.add(txt(this, 65 + k * 118, 12, p.name, { align: 'center', color: k === pocket ? 'gold' : 'gray' }));
      });
      c.add(panel(this, 8, 32, 250, 230, 'dark'));
      c.add(panel(this, 264, 32, 208, 230, 'dark'));
      const icon = this.add.image(368, 70, 'icons', 'capsule').setScale(3).setVisible(false);
      const nameT = txt(this, 368, 100, '', { align: 'center', color: 'gold' });
      const descLines = [0, 1, 2, 3, 4, 5].map((j) => txt(this, 276, 120 + j * 13, ''));
      c.add([icon, nameT, ...descLines]);
      c.add(txt(this, 464, 248, `${G.state.money.toLocaleString()}¢`, { align: 'right', color: 'green' }));
      c.add(txt(this, 276, 248, '< > pocket', { face: 'small', color: 'gray' }));
      const show = (id) => {
        if (!id) { icon.setVisible(false); nameT.setText(''); descLines.forEach((l) => l.setText('')); return; }
        const it = ITEMS[id];
        icon.setFrame(id).setVisible(this.textures.get('icons').has(id));
        nameT.setText(it.name);
        const dl = wrap(this, fmtKeys(it.desc), 186);
        descLines.forEach((l, j) => l.setText(dl[j] || ''));
      };
      if (!ids.length) {
        c.add(txt(this, 133, 130, 'Nothing here yet.', { align: 'center', color: 'gray' }));
        show(null);
        const k = await this.loop(() => {
          if (input.nav('left', this.owner)) { return 'l'; }
          if (input.nav('right', this.owner)) { return 'r'; }
          if (input.pressed('cancel', this.owner)) { return 'x'; }
          return undefined;
        });
        c.destroy();
        if (k === 'x') { return null; }
        pocket = (pocket + (k === 'l' ? 3 : 1)) % 4; idx = 0; audio.sfx('cursor');
        continue;
      }
      idx = Math.min(idx, ids.length - 1);
      const menu = new ListMenu(this, {
        items: ids.map((k) => ({ label: ITEMS[k].name, right: k === 'xp_share' ? (G.state.xpShareOn ? 'ON' : 'OFF') : ITEMS[k].key || ITEMS[k].disc ? '' : `×${G.state.bag[k]}`, rightColor: k === 'xp_share' ? (G.state.xpShareOn ? 'green' : 'gray') : undefined, value: k })),
        x: 10, y: 36, width: 246, visible: 15, noPanel: true, index: idx, depth: 5, onMove: (it) => show(it.value),
      });
      // allow pocket switching while the list is open
      let switched = null;
      const sw = () => {
        if (!input.has(menu.owner)) { return; }
        if (input.nav('left', menu.owner)) { switched = 'l'; }
        if (input.nav('right', menu.owner)) { switched = 'r'; }
        if (switched) { input.keysDown.add('cancel'); this.time.delayedCall(20, () => input.keysDown.delete('cancel')); }
      };
      this.events.on('update', sw);
      const v = await menu.run();
      this.events.off('update', sw);
      idx = menu.index;
      menu.destroy();
      c.destroy();
      if (switched) { pocket = (pocket + (switched === 'l' ? 3 : 1)) % 4; idx = 0; audio.sfx('cursor'); input.clear(); continue; }
      if (v === null) { return null; }
      await this.useItem(v, target);
    }
  }

  async useItem(id, target) {
    const it = ITEMS[id];
    const u = it.use;
    const party = G.state.party;
    const opts = [];
    const usable = ['heal', 'cure', 'revive', 'revive_all', 'pp', 'level', 'teach', 'repel', 'escape', 'map'].includes(u.kind);
    if (usable) { opts.push({ label: 'Use', value: 'use' }); }
    if (u.kind === 'attach') { opts.push({ label: G.state.xpShareOn ? 'Detach' : 'Attach', value: 'attach' }); }
    if (!it.key && !it.disc) { opts.push({ label: 'Toss', value: 'toss' }); }
    opts.push({ label: 'Cancel', value: null });
    const a = await choose(this, opts, { x: GAME_W - 12, y: GAME_H - 12, anchor: 'bottom-right', depth: 30 });
    if (a === 'toss') {
      if (await this.confirm(`Throw away one ${it.name}?`)) { takeItem(id); }
      return;
    }
    if (a === 'attach') {
      G.state.xpShareOn = !G.state.xpShareOn;
      audio.sfx(G.state.xpShareOn ? 'heal' : 'cancel');
      await this.toast(G.state.xpShareOn
        ? `${G.state.player.name} attached the XP Share. The whole team will share battle XP!`
        : `${G.state.player.name} took off the XP Share.`);
      return;
    }
    if (a !== 'use') { return; }
    if (u.kind === 'repel') {
      G.state.repel = u.steps; takeItem(id);
      await this.toast(`The scent of the ${it.name} spreads around you.`);
      return;
    }
    if (u.kind === 'escape') {
      const w = this.scene.get('World');
      const back = w.mapView.props.escape;
      if (!back) { await this.toast("It can't be used here."); return; }
      takeItem(id);
      const [map, xy] = back.split(':'); const [x, y] = xy.split(',').map(Number);
      await this.toast('You followed the thread back to the entrance!', 900);
      this.exitThen(() => w.transition(map, x, y, 'down'));
    }
    if (u.kind === 'map') { await this.reachMap(); return; }
    if (u.kind === 'revive_all') {
      const down = party.filter((m) => m.hp <= 0);
      if (!down.length) { await this.toast("It won't have any effect."); return; }
      down.forEach((m) => { m.hp = maxHp(m); m.status = null; });
      takeItem(id); audio.sfx('heal');
      await this.toast(down.length === 1 ? `${monName(down[0])} is revived!` : `All ${down.length} fainted Morphs are revived!`);
      return;
    }
    const t = target !== null && target !== undefined ? target : await this.party({ pick: true, title: `Use ${it.name} on which Morph?` });
    if (t === null || t === undefined) { return; }
    const m = party[t];
    const mx = maxHp(m);
    const nm = monName(m);
    if (u.kind === 'heal') {
      if (m.hp <= 0 || (m.hp >= mx && !(u.cure && m.status))) { await this.toast("It won't have any effect."); return; }
      const before = m.hp; m.hp = Math.min(mx, m.hp + u.hp); if (u.cure) { m.status = null; }
      takeItem(id); audio.sfx('heal');
      await this.toast(`${nm} recovered ${m.hp - before} HP.`);
    } else if (u.kind === 'cure') {
      if (m.hp <= 0 || !m.status || (u.status !== 'all' && !u.status.includes(m.status))) { await this.toast("It won't have any effect."); return; }
      m.status = null; takeItem(id); audio.sfx('heal');
      await this.toast(`${nm} is cured!`);
    } else if (u.kind === 'revive') {
      if (m.hp > 0) { await this.toast("It won't have any effect."); return; }
      m.hp = Math.max(1, Math.floor(mx * u.frac)); m.status = null; takeItem(id); audio.sfx('heal');
      if (u.bitter) { m.friendship = Math.max(0, (m.friendship ?? 70) - u.bitter); }
      await this.toast(u.bitter ? `${nm} is revived! It pulled a face at the bitter taste.` : `${nm} is revived!`);
    } else if (u.kind === 'pp') {
      const mi = await choose(this, m.moves.map((mv, k) => ({ label: MOVES[mv.id].name, right: `${mv.pp}/${mv.max}`, value: k })), { x: GAME_W - 12, y: GAME_H - 12, anchor: 'bottom-right', depth: 30 });
      if (mi === null) { return; }
      const mv = m.moves[mi];
      if (mv.pp >= mv.max) { await this.toast("It won't have any effect."); return; }
      mv.pp = Math.min(mv.max, mv.pp + u.pp); takeItem(id);
      await this.toast(`${MOVES[mv.id].name}'s PP was restored.`);
    } else if (u.kind === 'level') {
      if (m.level >= 100) { await this.toast("It won't have any effect."); return; }
      takeItem(id);
      const need = (() => { const s = SPECIES[m.species]; return null; })();
      const before = m.level;
      const target = m.level + 1;
      let steps = [];
      while (m.level < target) { steps = steps.concat(addXp(m, Math.max(1, xpToNext(m)))); }
      audio.sfx('level_up');
      await this.toast(`${nm} grew to Lv. ${m.level}!`);
      for (const s of steps) {
        for (const mv of s.learn) {
          if (learnMove(m, mv)) { await this.toast(`${nm} learned ${MOVES[mv].name}!`); }
          else { await this.teachFlow(m, mv); }
        }
      }
      const into = evolutionTarget(m);
      if (into) {
        await new Promise((r) => { this.scene.launch('Evolution', { mon: m, into, onDone: r }); this.scene.bringToTop('Evolution'); });
        input.clear();
      }
    } else if (u.kind === 'teach') {
      const sp = SPECIES[m.species];
      if (!canLearnDisc(sp, u.move)) { await this.toast(`${nm} can't learn ${MOVES[u.move].name}.`); return; }
      if (m.moves.some((mv) => mv.id === u.move)) { await this.toast(`${nm} already knows ${MOVES[u.move].name}.`); return; }
      if (learnMove(m, u.move)) { audio.sfx('level_up'); await this.toast(`${nm} learned ${MOVES[u.move].name}!`); }
      else { await this.teachFlow(m, u.move); }
    }
  }

  async teachFlow(m, moveId) {
    const nm = monName(m);
    const mv = MOVES[moveId];
    await this.toast(`${nm} wants to learn ${mv.name}, but already knows four moves.`);
    const idx = await pickMove(this, m, { title: `Which move should ${nm} forget to learn ${mv.name}?`, newMove: moveId, owner: this.owner });
    if (idx === null || idx === -1) { await this.toast(`${nm} did not learn ${mv.name}.`); return; }
    const old = MOVES[m.moves[idx].id].name;
    replaceMove(m, idx, moveId);
    audio.sfx('level_up');
    await this.toast(`${nm} forgot ${old} and learned ${mv.name}!`);
  }

  // ─── Index ────────────────────────────────────────────────────────────
  async index(startId) {
    const list = SPECIES_LIST;
    let i = Math.max(0, list.findIndex((sp) => sp.id === startId));
    const seen = new Set(G.state.index.seen), caught = new Set(G.state.index.caught);
    const c = this.add.container(0, 0);
    c.add(this.dim(0.94));
    c.add(panel(this, 8, 8, 200, 254, 'dark'));
    c.add(panel(this, 214, 8, 258, 254, 'dark'));
    c.add(txt(this, 16, 14, `Seen ${seen.size}   Caught ${caught.size}`, { color: 'gold', face: 'main' }));
    const rows = [];
    for (let k = 0; k < 15; k++) { const t = txt(this, 30, 32 + k * 15, ''); const b = this.add.image(18, 36 + k * 15, 'ui', 'party_pip'); c.add([t, b]); rows.push([t, b]); }
    const bar = selBar(this, 11, 194, 14); c.addAt(bar, 3);
    const cur = this.add.image(10, 0, 'cursor').setOrigin(0, 0); c.add(cur);
    const pic = this.add.image(343, 116, 'mons', 'nibbit_f').setOrigin(0.5, 1).setScale(1.1); c.add(pic);
    const nm = txt(this, 343, 122, '', { align: 'center', color: 'gold' });
    const cls = txt(this, 343, 136, '', { align: 'center', face: 'small', color: 'gray' });
    const t1 = this.add.image(300, 146, 'ui', 'type_Plain').setOrigin(0, 0);
    const t2 = this.add.image(342, 146, 'ui', 'type_Plain').setOrigin(0, 0);
    const desc = [0, 1, 2, 3, 4, 5].map((k) => txt(this, 224, 162 + k * 13, ''));
    const hab = txt(this, 224, 244, '', { face: 'small', color: 'blue' });
    // male / female forms: coloured = caught in that form, gray = not caught yet; A switches the picture
    const fm = txt(this, 446, 14, '♂'), ff = txt(this, 458, 14, '♀');
    const formHint = txt(this, 222, 14, 'A: SWITCH FORM', { face: 'small', color: 'gray' });
    c.add([nm, cls, t1, t2, ...desc, hab, fm, ff, formHint]);
    const ix = G.state.index;
    const twoForms = (sp) => (sp.female ?? 0.5) > 0 && (sp.female ?? 0.5) < 1;
    const firstForm = (sp) => {
      if (!twoForms(sp)) { return (sp.female ?? 0.5) >= 1 ? 'f' : 'm'; }
      if (hasCaughtForm(sp.id, 'm', ix)) { return 'm'; }
      if (hasCaughtForm(sp.id, 'f', ix)) { return 'f'; }
      return hasSeenForm(sp.id, 'f', ix) && !hasSeenForm(sp.id, 'm', ix) ? 'f' : 'm';
    };
    let form = firstForm(list[i]);
    let formOf = list[i].id;
    let scroll = 0;
    const habitats = this.habitats();
    const draw = () => {
      if (i < scroll) { scroll = i; }
      if (i >= scroll + 15) { scroll = i - 14; }
      rows.forEach(([t, b], k) => {
        const sp = list[scroll + k];
        if (!sp) { t.setText(''); b.setVisible(false); return; }
        const s = seen.has(sp.id);
        t.setText(`${String(sp.num).padStart(3, '0')} ${s ? sp.name : '-----'}`).setFont(`main_${caught.has(sp.id) ? 'white' : s ? 'gray' : 'gray'}`);
        b.setVisible(caught.has(sp.id));
      });
      cur.setY(33 + (i - scroll) * 15);
      bar.setY(29 + (i - scroll) * 15);
      rows.forEach(([t], k) => { if (k === i - scroll && list[scroll + k] && seen.has(list[scroll + k].id)) { t.setFont('main_gold'); } });
      const sp = list[i];
      const s = seen.has(sp.id), cg = caught.has(sp.id);
      if (formOf !== sp.id) { form = firstForm(sp); formOf = sp.id; }
      pic.setFrame(monFrame({ species: sp.id, sex: form }, 'f')).setVisible(s);
      if (s && !hasCaughtForm(sp.id, form, ix)) { pic.setTintFill(0x2a2d44); } else { pic.clearTint(); }
      const both = twoForms(sp);
      const onlyF = !both && (sp.female ?? 0.5) >= 1;
      fm.setVisible(s && (both || !onlyF)).setFont(`main_${hasCaughtForm(sp.id, 'm', ix) ? 'blue' : 'gray'}`).setAlpha(form === 'm' ? 1 : 0.5);
      ff.setVisible(s && (both || onlyF)).setFont(`main_${hasCaughtForm(sp.id, 'f', ix) ? 'pink' : 'gray'}`).setAlpha(form === 'f' ? 1 : 0.5);
      if (!both) { fm.setX(458); } else { fm.setX(446); }
      formHint.setVisible(s && both);
      nm.setText(s ? sp.name : '???');
      cls.setText(cg ? (sp.mythical ? `${sp.cls}  -  MYTHICAL` : sp.legendary ? `${sp.cls}  -  LEGENDARY` : sp.cls) : '');
      t1.setVisible(cg).setFrame(`type_${sp.types[0]}`);
      t2.setVisible(cg && sp.types.length > 1).setFrame(`type_${sp.types[1] || sp.types[0]}`);
      t1.setX(343 - (sp.types.length > 1 ? 40 : 18));
      t2.setX(343 + 2);
      const dl = cg ? wrap(this, sp.dex, 236) : (s ? ['Catch one to learn more.'] : ['Not yet seen.']);
      desc.forEach((d, k) => d.setText(dl[k] || ''));
      hab.setText(s && habitats[sp.id] ? `Found: ${habitats[sp.id].slice(0, 3).join(', ')}` : '');
    };
    draw();
    await this.loop(() => {
      const o = this.owner;
      if (input.nav('up', o)) { i = (i + list.length - 1) % list.length; audio.sfx('cursor'); draw(); }
      else if (input.nav('down', o)) { i = (i + 1) % list.length; audio.sfx('cursor'); draw(); }
      else if (input.nav('left', o)) { i = Math.max(0, i - 15); audio.sfx('cursor'); draw(); }
      else if (input.nav('right', o)) { i = Math.min(list.length - 1, i + 15); audio.sfx('cursor'); draw(); }
      else if (input.pressed('confirm', o)) {
        if (caught.has(list[i].id) || seen.has(list[i].id)) {
          if (twoForms(list[i])) { form = form === 'm' ? 'f' : 'm'; draw(); }
          audio.cry(list[i].num);
        }
      }
      else if (input.pressed('cancel', o)) { audio.sfx('cancel'); return true; }
      return undefined;
    });
    c.destroy();
  }

  habitats() {
    const out = {};
    const idx = this.cache.json.get('mapIndex') || {};
    // lazy import to avoid cycles
    const E = window.__encounters || {};
    for (const [map, t] of Object.entries(E)) {
      for (const kind of Object.keys(t)) {
        for (const [sp] of t[kind]) {
          out[sp] = out[sp] || [];
          const nm = (idx[map] && idx[map].name) || map;
          if (!out[sp].includes(nm)) { out[sp].push(nm); }
        }
      }
    }
    // starters you can still rescue
    for (const sp of openRescues()) { out[sp] = [`${RESCUES[sp].where} (needs help!)`, ...(out[sp] || [])]; }
    return out;
  }

  // ─── Tamer card ───────────────────────────────────────────────────────
  async card() {
    const s = G.state;
    const c = this.add.container(0, 0);
    c.add(this.dim(0.9));
    c.add(panel(this, 40, 30, 400, 210, 'gold'));
    c.add(txt(this, 56, 42, 'TAMER CARD', { color: 'gold' }));
    c.add(txt(this, 424, 42, `ID ${s.trainerId}`, { align: 'right', color: 'gray' }));
    const idx = this.cache.json.get('charIndex');
    const style = playerStyleKey(s.player.style || 0);
    c.add(this.add.image(380, 140, 'chars', idx[style] * 12).setScale(3).setOrigin(0.5, 1));
    const h = Math.floor(s.playMs / 3600000), m = Math.floor((s.playMs % 3600000) / 60000);
    const lines = [
      ['Name', s.player.name], ['Money', `${s.money.toLocaleString()}¢`], ['Index', flag('got_index') ? `${s.index.caught.length} caught / ${s.index.seen.length} seen` : '—'],
      ['Play time', `${h}:${String(m).padStart(2, '0')}`], ['Adventure began', new Date(s.started).toLocaleDateString()],
    ];
    lines.forEach(([k, v], i) => { c.add(txt(this, 60, 66 + i * 18, k, { color: 'gray' })); c.add(txt(this, 180, 66 + i * 18, v)); });
    c.add(txt(this, 60, 168, 'Sigils', { color: 'gray' }));
    ['moss', 'tide', 'spark', 'veil', 'rime', 'wyrm'].forEach((sg, i) => {
      const got = s.sigils.includes(sg);
      c.add(this.add.image(80 + i * 36, 200, 'ui', got ? `sigil_${sg}` : `sigil_${sg}_empty`).setScale(1.6));
    });
    await this.waitKey();
    audio.sfx('cancel');
    c.destroy();
  }

  // ─── options ──────────────────────────────────────────────────────────
  async options() {
    const S = G.settings;
    const defs = [
      { k: 'textSpeed', label: 'Text speed', vals: ['slow', 'normal', 'fast', 'instant'] },
      { k: 'musicVol', label: 'Music volume', vol: true },
      { k: 'sfxVol', label: 'Sound volume', vol: true },
      { k: 'battleAnims', label: 'Battle animations', vals: [true, false], names: ['On', 'Off'] },
      { k: 'battleStyle', label: 'Battle style', vals: ['shift', 'set'], names: ['Shift', 'Set'] },
      { k: 'expShare', label: 'Bond Charm XP', vals: [true, false], names: ['On', 'Off'] },
      { k: 'autoRun', label: 'Always run', vals: [false, true], names: ['Off', 'On'] },
      { k: 'clock', label: 'Clock', vals: ['game', 'real'], names: ['Game time', 'Real time'] },
      { k: 'scaling', label: 'Screen scaling', vals: ['pixel', 'fill'], names: ['Pixel-perfect', 'Fill window'] },
      { k: 'frame', label: 'Text box colour', vals: [0, 1, 2, 3, 4], names: ['Night', 'Teal', 'Gold', 'Rose', 'Paper'] },
      { k: '_fullscreen', label: 'Fullscreen', action: true },
      { k: '_controls', label: 'Controls...', action: true, open: true },
    ];
    let i = 0;
    const c = this.add.container(0, 0);
    c.add(this.dim(0.9));
    c.add(panel(this, 60, 20, 360, 230, 'dark'));
    c.add(txt(this, 76, 28, 'OPTIONS', { color: 'gold' }));
    c.add(txt(this, 404, 28, fmtKeys('< > change   {BTN:cancel} back'), { align: 'right', face: 'small', color: 'gray' }));
    const rows = defs.map((d, k) => [txt(this, 90, 48 + k * 17, d.label), txt(this, 404, 48 + k * 17, '', { align: 'right', color: 'blue' })]);
    rows.forEach((r) => c.add(r));
    const bar = selBar(this, 72, 338, 15); c.addAt(bar, 2);
    const cur = this.add.image(76, 0, 'cursor').setOrigin(0, 0); c.add(cur);
    const valText = (d) => {
      if (d.open) { return ''; }
      if (d.action) { return this.scale.isFullscreen ? 'On' : 'Off'; }
      if (d.vol) { return `${'■'.replace('■', '|').repeat(Math.round(S[d.k] * 10))}${'.'.repeat(10 - Math.round(S[d.k] * 10))}  ${Math.round(S[d.k] * 100)}%`; }
      const vi = d.vals.indexOf(S[d.k]);
      return d.names ? d.names[vi] : String(S[d.k]).replace(/^./, (x) => x.toUpperCase());
    };
    const draw = () => {
      rows.forEach(([l, v], k) => { v.setText(valText(defs[k])); l.setFont(k === i ? 'main_gold' : 'main_white'); });
      cur.setY(49 + i * 17);
      bar.setY(45 + i * 17);
    };
    draw();
    for (;;) {
    const res = await this.loop(() => {
      const o = this.owner;
      const d = defs[i];
      if (input.nav('up', o)) { i = (i + defs.length - 1) % defs.length; audio.sfx('cursor'); draw(); }
      else if (input.nav('down', o)) { i = (i + 1) % defs.length; audio.sfx('cursor'); draw(); }
      else if (input.nav('left', o) || input.nav('right', o) || (input.pressed('confirm', o) && d.action)) {
        const dir = input.nav('left', o) ? -1 : 1;
        if (d.open) {
          if (input.pressed('confirm', o)) { audio.sfx('select'); return 'controls'; }
          return undefined;
        } else if (d.action) {
          if (this.scale.isFullscreen) { this.scale.stopFullscreen(); } else { this.scale.startFullscreen(); }
        } else if (d.vol) {
          S[d.k] = Math.max(0, Math.min(1, Math.round((S[d.k] + dir * 0.1) * 10) / 10));
          audio.refreshVolumes();
        } else {
          const vi = d.vals.indexOf(S[d.k]);
          S[d.k] = d.vals[(vi + dir + d.vals.length) % d.vals.length];
        }
        if (d.k === 'scaling' && window.__fit) { window.__fit(); }
        audio.sfx('cursor');
        saveSettings(S);
        draw();
      } else if (input.pressed('cancel', o)) { audio.sfx('cancel'); return true; }
      return undefined;
    });
    if (res !== 'controls') { break; }
    c.setVisible(false);
    await this.controls();
    c.setVisible(true);
    draw();
    }
    c.destroy();
  }

  // ─── controls (key rebinding) ─────────────────────────────────────────
  async controls() {
    const LABELS = {
      up: 'Move up', down: 'Move down', left: 'Move left', right: 'Move right', confirm: 'Talk / confirm',
      cancel: 'Back / cancel', menu: 'Pause menu', run: 'Run', info: 'Info (in menus)',
    };
    const bind = {};
    for (const a of REBINDABLE) { bind[a] = [...input.bindings[a]]; }
    const c = this.add.container(0, 0).setDepth(40);
    c.add(this.dim(0.94));
    c.add(panel(this, 40, 8, 400, 254, 'dark'));
    c.add(txt(this, 56, 16, 'CONTROLS', { color: 'gold' }));
    const kn = (a) => input.hint(a);
    c.add(txt(this, 424, 16, `${kn('confirm')} change key   ${kn('cancel')} done`, { align: 'right', face: 'small', color: 'gray' }));
    c.add(txt(this, 262, 32, 'KEY 1', { align: 'center', face: 'small', color: 'gray' }));
    c.add(txt(this, 362, 32, 'KEY 2', { align: 'center', face: 'small', color: 'gray' }));
    const Y = (r) => 44 + r * 16;
    const rows = REBINDABLE.map((a, r) => {
      const lab = txt(this, 72, Y(r), LABELS[a]);
      const k1 = txt(this, 262, Y(r), '', { align: 'center', color: 'blue' });
      const k2 = txt(this, 362, Y(r), '', { align: 'center', color: 'blue' });
      c.add([lab, k1, k2]);
      return [k1, k2];
    });
    const nR = REBINDABLE.length;
    c.add(txt(this, 72, Y(nR) + 4, 'Reset to defaults'));
    c.add(txt(this, 72, Y(nR + 1) + 4, 'Done'));
    c.add(txt(this, 240, 220, 'Always work too: Space / E confirm · Q back · Tab menu', { align: 'center', face: 'small', color: 'gray' }));
    c.add(txt(this, 240, 230, 'Gamepad: stick / D-pad move · A confirm · B back · Start menu · X run', { align: 'center', face: 'small', color: 'gray' }));
    const status = txt(this, 240, 244, '', { align: 'center', color: 'gold' });
    c.add(status);
    const cur = this.add.image(56, 0, 'cursor').setOrigin(0, 0);
    const box = this.add.rectangle(0, 0, 86, 14, 0xffd65c, 0.25).setStrokeStyle(1, 0xffd65c).setOrigin(0.5, 0);
    const bar = selBar(this, 52, 364, 14);
    c.addAt(bar, 2);
    c.add([cur, box]);
    let r = 0, col = 0;
    const say = (t) => status.setText(t);
    const draw = () => {
      rows.forEach(([k1, k2], i) => { k1.setText(keyName(bind[REBINDABLE[i]][0])); k2.setText(keyName(bind[REBINDABLE[i]][1])); });
      const y = r < nR ? Y(r) : Y(r) + 4;
      cur.setY(y + 1);
      bar.setY(y - 3);
      box.setVisible(r < nR);
      if (r < nR) { box.setPosition(col === 0 ? 262 : 362, y - 2); }
    };
    const apply = () => {
      input.setBindings(bind);
      G.settings.keys = JSON.parse(JSON.stringify(bind));
      saveSettings(G.settings);
    };
    const FIXED = { ' ': 'confirm', e: 'confirm', q: 'cancel', tab: 'menu', r: 'info', pageup: null, pagedown: null, f1: null, '`': null };
    const assign = (a, j, k) => {
      const old = bind[a][j];
      if (k === 'delete') {
        if (ESSENTIAL.includes(a) && !bind[a][1 - j]) { return `${LABELS[a]} needs at least one key.`; }
        bind[a][j] = null;
        return `Cleared ${LABELS[a]}, key ${j + 1}.`;
      }
      if (k in FIXED && FIXED[k] !== a) { return `${keyName(k)} is reserved${FIXED[k] ? ` for ${LABELS[FIXED[k]]}` : ''}.`; }
      if (k === old) { return 'No change.'; }
      for (const b of REBINDABLE) {
        for (let jb = 0; jb < 2; jb++) {
          if (bind[b][jb] !== k || (b === a && jb === j)) { continue; }
          if (b === a) { bind[a][jb] = old; bind[a][j] = k; return `${LABELS[a]}: ${keyName(k)}.`; }
          if (!old && ESSENTIAL.includes(b) && !bind[b][1 - jb]) { return `${keyName(k)} is the only key for ${LABELS[b]}.`; }
          bind[b][jb] = old;
          bind[a][j] = k;
          return `${LABELS[a]}: ${keyName(k)}  (swapped with ${LABELS[b]})`;
        }
      }
      bind[a][j] = k;
      return `${LABELS[a]}: ${keyName(k)}.`;
    };
    draw();
    for (;;) {
      const act = await this.loop(() => {
        const o = this.owner;
        if (input.nav('up', o)) { r = (r + nR + 1) % (nR + 2); audio.sfx('cursor'); draw(); }
        else if (input.nav('down', o)) { r = (r + 1) % (nR + 2); audio.sfx('cursor'); draw(); }
        else if ((input.nav('left', o) || input.nav('right', o)) && r < nR) { col = 1 - col; audio.sfx('cursor'); draw(); }
        else if (input.pressed('confirm', o)) { return 'ok'; }
        else if (input.pressed('cancel', o)) { return 'back'; }
        return undefined;
      });
      if (act === 'back' || (act === 'ok' && r === nR + 1)) { audio.sfx('cancel'); break; }
      if (r === nR) {
        for (const a of REBINDABLE) { bind[a] = [...DEFAULT_KEYS[a]]; }
        apply(); audio.sfx('select'); say('Controls reset to defaults.'); draw();
        continue;
      }
      const a = REBINDABLE[r];
      audio.sfx('select');
      say(`Press a key for ${LABELS[a]} (Delete clears)...`);
      box.setStrokeStyle(2, 0x7cea8c);
      await new Promise((res) => this.time.delayedCall(120, res));
      const k = await input.captureKey();
      box.setStrokeStyle(1, 0xffd65c);
      const msg = assign(a, col, k);
      apply();
      input.clear();
      audio.sfx('cursor');
      say(msg);
      draw();
    }
    c.destroy();
    return true;
  }

  // ─── Reach map ────────────────────────────────────────────────────────
  // The Reach Map. Only places you've found can be picked (the rest sit under fog, marked "???"); a pin
  // glides to the place you pick, and for towns you can fly to a dotted flight path is drawn from where you are.
  async reachMap(startId = null) {
    const c = this.add.container(0, 0);
    c.add(this.dim(0.95));
    const ox = (GAME_W - 400) / 2, oy = (GAME_H - 240) / 2 - 8;
    c.add(this.add.image(GAME_W / 2, oy + 120, 'regionmap').setOrigin(0.5));
    const here = G.state.player.map;
    const loc = REGION.locate(here);
    const pts = REGION.points;
    const seen = new Set(G.state.seenMaps || []);
    const found = (p) => p.id === loc || p.maps.some((m) => seen.has(m)) || (p.fly && flag(`visited_${p.fly}`));
    const P = (p) => ({ x: ox + p.x, y: oy + p.y });
    // fog over places not found yet
    for (const p of pts) {
      if (found(p)) { continue; }
      const q = P(p);
      const fog = this.add.image(q.x, q.y, 'glow').setTint(0x0b0c16).setAlpha(0.85).setScale(0.75);
      c.add([fog, txt(this, q.x, q.y - 4, '???', { face: 'small', color: 'white', align: 'center' })]);
    }
    // markers: towns you can fly to (gold), other found places (white)
    const canFly = (p) => this.canFly(p, loc);
    for (const p of pts) {
      if (!found(p)) { continue; }
      const q = P(p);
      const dot = p.town ? this.add.rectangle(q.x, q.y, 6, 6, canFly(p) ? 0xffd65c : 0xe8ecf4).setStrokeStyle(1, 0x1c1a28)
        : this.add.circle(q.x, q.y, 2.5, 0xe8ecf4).setStrokeStyle(1, 0x1c1a28);
      c.add(dot);
    }
    // you are here
    const lp = pts.find((p) => p.id === loc);
    const you = this.add.image(0, 0, 'chars', 0).setOrigin(0.5, 1).setScale(0.75);
    const idx = this.cache.json.get('charIndex');
    you.setFrame((idx[playerStyleKey(G.state.player.style || 0)] ?? 0) * 12);
    if (lp) { const q = P(lp); you.setPosition(q.x, q.y + 2); } else { you.setVisible(false); }
    // flight path, waypoint ring and pin
    const path = this.add.graphics();
    const ring = this.add.image(0, 0, 'p_ring').setTint(0xffd65c).setScale(1.2);
    const pin = this.add.image(0, 0, 'ui', 'map_pin').setOrigin(0.5, 1).setScale(1.4);
    c.add([path, you, ring, pin]);
    this.tweens.add({ targets: ring, scale: 3, alpha: 0, duration: 900, repeat: -1 });
    const bob = this.tweens.add({ targets: pin, y: '-=3', duration: 380, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
    // info panel
    c.add(panel(this, 8, GAME_H - 40, GAME_W - 16, 34, 'dark'));
    const title = txt(this, 16, GAME_H - 36, '', { color: 'gold' });
    const desc = txt(this, 16, GAME_H - 24, '', { face: 'small' });
    const hint = txt(this, GAME_W - 16, GAME_H - 36, '', { face: 'small', align: 'right', color: 'green' });
    c.add([title, desc, hint]);
    const choices = pts.filter(found);
    let i = Math.max(0, choices.findIndex((p) => p.id === (startId || loc)));
    let first = true;
    const draw = () => {
      const p = choices[i];
      const q = P(p);
      bob.pause();
      if (first) { pin.setPosition(q.x, q.y - 3); first = false; } else {
        this.tweens.add({ targets: pin, x: q.x, y: q.y - 3, duration: 160, ease: 'Quad.easeOut', onComplete: () => bob.resume() });
      }
      ring.setPosition(q.x, q.y);
      path.clear();
      const fly = canFly(p);
      if (fly && lp) {
        const a = P(lp);
        const n = Math.max(2, Math.floor(Math.hypot(q.x - a.x, q.y - a.y) / 6));
        path.fillStyle(0xffd65c, 1);
        for (let k = 1; k < n; k++) {
          const t = k / n;
          path.fillRect(a.x + (q.x - a.x) * t - 1, a.y + (q.y - a.y) * t - Math.sin(t * Math.PI) * 14 - 1, 2, 2);
        }
      }
      title.setText(p.name);
      desc.setText(p.desc);
      const status = p.id === loc ? 'YOU ARE HERE'
        : fly ? `${input.hint('confirm') || 'A'}: FLY HERE`
          : p.fly && !itemCount('wing_whistle') ? ''
            : p.fly && flag(`visited_${p.fly}`) ? "CAN'T FLY FROM INDOORS" : '';
      hint.setText(status).setFont(`small_${fly || p.id === loc ? 'green' : 'gray'}`);
    };
    draw();
    // pick the nearest found place in the direction pressed
    const step = (dx, dy) => {
      const a = P(choices[i]);
      let best = -1, bestScore = Infinity;
      choices.forEach((p, k) => {
        if (k === i) { return; }
        const q = P(p);
        const vx = q.x - a.x, vy = q.y - a.y;
        const along = vx * dx + vy * dy;
        if (along <= 0) { return; }
        const side = Math.abs(vx * dy - vy * dx);
        const score = along + side * 2.2;
        if (score < bestScore) { bestScore = score; best = k; }
      });
      if (best >= 0) { i = best; audio.sfx('cursor'); draw(); } else { audio.blip('bump'); }
    };
    const res = await this.loop(() => {
      const o = this.owner;
      if (input.nav('left', o)) { step(-1, 0); }
      else if (input.nav('right', o)) { step(1, 0); }
      else if (input.nav('up', o)) { step(0, -1); }
      else if (input.nav('down', o)) { step(0, 1); }
      else if (input.pressed('confirm', o)) {
        if (canFly(choices[i])) { return 'fly'; }
        audio.blip('bump');
      } else if (input.pressed('cancel', o)) { audio.sfx('cancel'); return true; }
      return undefined;
    });
    if (res === 'fly') {
      const p = choices[i];
      if (await this.confirm(`Blow the Wing Whistle and fly to ${p.name}?`)) {
        c.destroy();
        await this.flyTo(p);
        return true;
      }
      c.destroy();
      return this.reachMap(p.id);
    }
    c.destroy();
    return true;
  }

  canFly(p, loc) {
    if (!p.fly || p.id === loc || !itemCount('wing_whistle')) { return false; }
    if (!flag(`visited_${p.fly}`)) { return false; }
    const w = this.scene.get('World');
    return !!(w && w.mapView && w.mapView.props.kind !== 'interior' && w.mapView.props.kind !== 'cave');
  }

  async flyTo(p) {
    const w = this.scene.get('World');
    const props = {};
    for (const pr of this.cache.tilemap.get(`map_${p.fly}`).data.properties || []) { props[pr.name] = pr.value; }
    const [x, y] = String(props.fly || '5,5').split(',').map(Number);
    audio.sfx('select');
    this.exitThen(() => w.transition(p.fly, x, y, 'down', { fade: 400 }));
  }

  // ─── shop ─────────────────────────────────────────────────────────────
  async shop(stock, title = 'Haven Counter') {
    for (;;) {
      const c = this.add.container(0, 0);
      c.add(panel(this, 8, 8, 170, 24, 'dark'));
      c.add(txt(this, 16, 14, `${G.state.money.toLocaleString()}¢`, { color: 'green' }));
      const v = await choose(this, [{ label: 'Buy', value: 'buy' }, { label: 'Sell', value: 'sell' }, { label: 'Leave', value: null }], { x: 8, y: 36, width: 100 });
      c.destroy();
      if (!v) { return null; }
      if (v === 'buy') { await this.shopList(stock, true, title); } else { await this.shopList(null, false, title); }
    }
  }

  async shopList(stock, buying, title) {
    let idx = 0;
    for (;;) {
      const ids = buying ? stock : Object.keys(G.state.bag).filter((k) => ITEMS[k] && !ITEMS[k].key && !ITEMS[k].disc && G.state.bag[k] > 0);
      const priceOf = (k) => (buying ? ITEMS[k].price : (ITEMS[k].sell ?? Math.floor(ITEMS[k].price / 2)));
      const c = this.add.container(0, 0);
      c.add(this.dim(0.6));
      c.add(panel(this, 8, 8, 280, 200, 'dark'));
      c.add(txt(this, 16, 14, buying ? `${title} — Buy` : 'Sell items', { color: 'gold' }));
      c.add(panel(this, 294, 8, 178, 24, 'dark'));
      const money = txt(this, 302, 14, `${G.state.money.toLocaleString()}¢`, { color: 'green' });
      c.add(money);
      c.add(panel(this, 8, 212, 464, 50, 'dark'));
      const icon = this.add.image(32, 237, 'icons', 'capsule').setScale(2);
      const dl = [txt(this, 56, 222, ''), txt(this, 56, 236, '')];
      const own = txt(this, 464, 222, '', { align: 'right', color: 'gray', face: 'small' });
      c.add([icon, ...dl, own]);
      if (!ids.length) {
        c.add(txt(this, 148, 100, 'Nothing to sell.', { align: 'center', color: 'gray' }));
        await this.waitKey(); c.destroy(); return;
      }
      const show = (k) => {
        icon.setFrame(k).setVisible(this.textures.get('icons').has(k));
        const w = wrap(this, fmtKeys(ITEMS[k].desc), 360);
        dl[0].setText(w[0] || ''); dl[1].setText(w[1] || '');
        own.setText(`In bag: ${itemCount(k)}`);
      };
      const menu = new ListMenu(this, { items: ids.map((k) => ({ label: ITEMS[k].name, right: `${priceOf(k)}¢`, value: k })), x: 10, y: 28, width: 276, visible: 12, noPanel: true, index: Math.min(idx, ids.length - 1), depth: 5, onMove: (it) => show(it.value) });
      const k = await menu.run();
      idx = menu.index;
      menu.destroy();
      if (k === null) { c.destroy(); return; }
      const price = priceOf(k);
      const maxQ = buying ? Math.min(99, Math.floor(G.state.money / Math.max(1, price))) : itemCount(k);
      if (maxQ <= 0) { c.destroy(); await this.toast("You don't have enough money."); continue; }
      const q = await this.quantity(maxQ, price);
      c.destroy();
      if (!q) { continue; }
      if (buying) {
        if (!(await this.confirm(`${q}× ${ITEMS[k].name} for ${q * price}¢?`))) { continue; }
        addMoney(-q * price); giveItem(k, q);
        audio.blip('coin');
        let bonus = '';
        if (k === 'capsule' && q >= 10) { giveItem('prime_capsule', 1); bonus = ' And have a Prime Capsule on the house!'; }
        await this.toast(`Here you go! Thank you!${bonus}`);
      } else {
        if (!(await this.confirm(`Sell ${q}× ${ITEMS[k].name} for ${q * price}¢?`))) { continue; }
        takeItem(k, q); addMoney(q * price);
        audio.blip('coin');
      }
    }
  }

  quantity(max, price) {
    let q = 1;
    const c = this.add.container(0, 0);
    c.add(panel(this, GAME_W - 160, 150, 150, 40, 'gold'));
    const t = txt(this, GAME_W - 150, 158, '');
    const p = txt(this, GAME_W - 20, 172, '', { align: 'right', color: 'green' });
    c.add([t, p]);
    const draw = () => { t.setText(`× ${String(q).padStart(2, '0')}   (max ${max})`); p.setText(`${q * price}¢`); };
    draw();
    return this.loop(() => {
      const o = this.owner;
      if (input.nav('up', o)) { q = q >= max ? 1 : q + 1; draw(); audio.sfx('cursor'); }
      else if (input.nav('down', o)) { q = q <= 1 ? max : q - 1; draw(); audio.sfx('cursor'); }
      else if (input.nav('right', o)) { q = Math.min(max, q + 10); draw(); audio.sfx('cursor'); }
      else if (input.nav('left', o)) { q = Math.max(1, q - 10); draw(); audio.sfx('cursor'); }
      else if (input.pressed('confirm', o)) { c.destroy(); return q; }
      else if (input.pressed('cancel', o)) { c.destroy(); return 0; }
      return undefined;
    });
  }

  // ─── storage (PC) ─────────────────────────────────────────────────────
  // Works like the classics' PC: flip between boxes with the box name at the top (or PgUp/PgDn, L/R,
  // RUN), pick a Morph up and carry it to any slot in any box or the team, and tidy boxes up with
  // names, wallpapers and sorting. A Morph being carried is never lost: backing out always puts it
  // somewhere free (its own slot first).
  async storage() {
    const S = G.state;
    const boxes = S.boxes;
    const nb = boxes.length;
    let box = Math.max(0, Math.min(nb - 1, Number.isInteger(S.pcBox) ? S.pcBox : 0));
    let zone = 'box'; // 'head' (box name), 'box' (the grid) or 'team'
    let cx = 0, cy = 0, pi = 0;
    let held = null, heldFrom = null, hole = null; // hole: the space the first Morph was lifted from
    const party = () => S.party;
    const healthy = (list) => list.some((m) => m && m.hp > 0);
    const boxCount = (b) => b.slots.filter(Boolean).length;
    const slotAt = () => (zone === 'box' ? boxes[box].slots[cy * 6 + cx] : zone === 'team' ? party()[pi] : null);
    const teamRows = () => Math.max(1, Math.min(6, party().length + (held && party().length < 6 ? 1 : 0)));

    // layout (480×270): details on the left, the box in the middle, the team on the right
    const GX = 128, GY = 32, CW = 37, CH = 41;
    const cellX = (k) => GX + (k % 6) * CW, cellY = (k) => GY + Math.floor(k / 6) * CH;
    const TX = 366, TY = 26, TH = 36;

    // every layer is its own top-level object (drawn in this order) so the box can be clipped while it slides
    const c = this.add.container(0, 0);
    c.add(this.dim(0.94));
    c.add(panel(this, 6, 6, 112, 240, 'dark'));
    c.add(panel(this, 122, 6, 236, 240, 'dark'));
    c.add(panel(this, 362, 6, 112, 240, 'dark'));
    c.add(txt(this, 418, 11, 'Team', { align: 'center', color: 'gold' }));
    const boxLayer = this.add.container(0, 0);
    const clip = this.make.graphics({ x: 0, y: 0 }, false);
    clip.fillStyle(0xffffff).fillRect(125, 29, 230, 214);
    boxLayer.setMask(clip.createGeometryMask());
    const head = this.add.container(0, 0);
    const teamLayer = this.add.container(0, 0);
    const detail = this.add.container(0, 0);
    const cursor = this.add.rectangle(0, 0, 10, 10).setOrigin(0, 0);
    const carry = this.add.image(0, 0, 'mons', 'nibbit_i').setVisible(false);
    const bob = { off: 0 };
    let carryY = 0;
    const carryBob = this.tweens.add({ targets: bob, off: 3, duration: 420, yoyo: true, repeat: -1, ease: 'Sine.easeInOut', onUpdate: () => { carry.y = carryY - bob.off; } });
    const hint = txt(this, GAME_W - 8, GAME_H - 15, '', { face: 'small', color: 'gray', align: 'right' });
    const note = txt(this, 10, GAME_H - 15, '', { face: 'small', color: 'gold' });
    const layers = [c, boxLayer, head, teamLayer, detail, cursor, carry, hint, note, clip];
    let noteTimer = null;
    const say = (text, color = 'gold') => {
      note.setText(text); note.setFont(`small_${color}`);
      if (noteTimer) { noteTimer.remove(); }
      noteTimer = this.time.delayedCall(2600, () => { note.setText(''); noteTimer = null; });
    };

    const renderBox = (slide = 0) => {
      boxLayer.removeAll(true);
      const bx = boxes[box];
      boxLayer.add(this.add.image(126, 30, this._wallpaper(bx.wall)).setOrigin(0, 0));
      for (let k = 0; k < 30; k++) {
        boxLayer.add(this.add.rectangle(cellX(k) + 2, cellY(k) + 2, CW - 4, CH - 4, 0x0b0c16, 0.22).setOrigin(0, 0));
        const m = bx.slots[k];
        if (m) { boxLayer.add(this.add.image(cellX(k) + CW / 2, cellY(k) + CH / 2 + 1, 'mons', monFrame(m, 'i'))); }
      }
      if (slide) {
        boxLayer.x = slide * 40; boxLayer.alpha = 0.3;
        this.tweens.add({ targets: boxLayer, x: 0, alpha: 1, duration: 140, ease: 'Cubic.easeOut' });
      } else { boxLayer.x = 0; boxLayer.alpha = 1; }
      renderHead();
    };
    const renderHead = () => {
      head.removeAll(true);
      const bx = boxes[box];
      const on = zone === 'head';
      head.add(panel(this, 128, 9, 224, 19, on ? 'gold' : 'ghost'));
      head.add(txt(this, 136, 13, '<', { color: on ? 'gold' : 'gray' }));
      head.add(txt(this, 344, 13, '>', { color: on ? 'gold' : 'gray' }));
      head.add(txt(this, 240, 13, bx.name, { align: 'center', color: on ? 'gold' : 'white' }));
      head.add(txt(this, 334, 15, `${boxCount(bx)}/30`, { face: 'small', color: 'gray', align: 'right' }));
      head.add(txt(this, 148, 15, `${box + 1}/${nb}`, { face: 'small', color: 'gray' }));
    };
    const renderTeam = () => {
      teamLayer.removeAll(true);
      for (let k = 0; k < 6; k++) {
        const y = TY + k * TH;
        const m = party()[k];
        teamLayer.add(this.add.rectangle(TX, y, 104, TH - 2, m ? 0x262a47 : 0x1b1e33).setOrigin(0, 0).setStrokeStyle(1, 0x2f3558));
        if (!m) { continue; }
        teamLayer.add(this.add.image(TX + 17, y + 16, 'mons', monFrame(m, 'i')));
        teamLayer.add(txt(this, TX + 34, y + 4, monName(m).slice(0, 9), { color: m.hp > 0 ? 'white' : 'gray' }));
        teamLayer.add(txt(this, TX + 34, y + 17, `Lv${m.level}`, { face: 'small', color: 'gray' }));
        const bar = new Bar(this, TX + 60, y + 19, 38, 2);
        bar.set(m.hp / maxHp(m)); bar.addTo(teamLayer);
      }
    };
    const renderDetail = () => {
      detail.removeAll(true);
      const m = held || slotAt();
      if (!m) {
        const bx = boxes[box];
        detail.add(txt(this, 62, 14, bx.name, { align: 'center', color: 'gold' }));
        detail.add(txt(this, 62, 28, `${boxCount(bx)} of 30 spaces used`, { face: 'small', color: 'gray', align: 'center' }));
        const total = boxes.reduce((n, b) => n + boxCount(b), 0);
        detail.add(txt(this, 62, 40, `${total} Morphs in storage`, { face: 'small', color: 'gray', align: 'center' }));
        const lines = zone === 'head'
          ? ['Press', fmtKeys('{BTN:confirm} for box'), 'options:', 'jump, rename,', 'wallpaper, sort.', '', '< > flips boxes.']
          : zone === 'team' ? ['An empty space', 'in your team.'] : ['An empty space.'];
        lines.forEach((l, j) => detail.add(txt(this, 62, 110 + j * 12, l, { align: 'center', color: 'gray' })));
        return;
      }
      const sp = SPECIES[m.species];
      detail.add(txt(this, 12, 11, monName(m), { color: 'gold' }));
      detail.add(sexMark(this, 12, 11, m, monName(m)));
      if (m.shiny) { detail.add(txt(this, 112, 11, '★', { color: 'gold', align: 'right' })); }
      detail.add(this.add.image(62, 120, 'mons', monFrame(m, 'f')).setOrigin(0.5, 1));
      detail.add(txt(this, 12, 123, `Lv${m.level}`));
      detail.add(txt(this, 112, 125, `No.${String(sp.num).padStart(3, '0')}`, { face: 'small', color: 'gray', align: 'right' }));
      sp.types.forEach((t, j) => detail.add(this.add.image(12 + j * 36, 138, 'ui', `type_${t}`).setOrigin(0, 0)));
      detail.add(txt(this, 12, 152, `${m.nature || '—'} nature`, { face: 'small', color: 'gray' }));
      detail.add(txt(this, 12, 163, 'HP', { face: 'small' }));
      const bar = new Bar(this, 26, 164, 50, 3); bar.set(m.hp / maxHp(m)); bar.addTo(detail);
      detail.add(txt(this, 112, 163, `${m.hp}/${maxHp(m)}`, { face: 'small', align: 'right' }));
      if (m.status && m.hp > 0) { detail.add(this.add.image(12, 174, 'ui', `st_${m.status}`).setOrigin(0, 0)); }
      (m.moves || []).forEach((mv, j) => {
        const d = MOVES[mv.id];
        if (!d) { return; }
        detail.add(this.add.rectangle(12, 184 + j * 12, 3, 9, TYPE_COLORS[d.type]).setOrigin(0, 0));
        detail.add(txt(this, 18, 185 + j * 12, d.name, { face: 'small' }));
      });
      if (held) { detail.add(txt(this, 62, 238, 'Carrying', { face: 'small', color: 'green', align: 'center' })); }
    };
    const renderCursor = () => {
      let x, y, w, h;
      if (zone === 'head') { x = 127; y = 8; w = 226; h = 21; }
      else if (zone === 'box') { const k = cy * 6 + cx; x = cellX(k); y = cellY(k); w = CW; h = CH; }
      else { x = TX - 1; y = TY + pi * TH - 1; w = 106; h = TH; }
      cursor.setPosition(x, y).setSize(w, h).setStrokeStyle(2, held ? 0x7cea8c : 0xffd65c);
      cursor.setVisible(zone !== 'head');
      if (held) {
        carry.setFrame(monFrame(held, 'i')).setVisible(true);
        carry.x = zone === 'team' ? x + 17 : x + w / 2;
        carryY = zone === 'head' ? y + h + 8 : y - 4;
        carry.y = carryY - bob.off;
      } else { carry.setVisible(false); }
      const dev = input.lastDevice;
      const flip = dev === 'touch' ? '{BTN:run}: next box' : dev === 'pad' ? 'L / R: box' : 'PgUp / PgDn: box';
      // (the small font has no arrow symbols, so directions are spelled out)
      let h1;
      if (zone === 'head') { h1 = `left / right: switch box   {BTN:confirm}: box options   ${held ? '' : '{BTN:cancel}: close'}`; }
      else if (held) { h1 = `{BTN:confirm}: place here   ${flip}   {BTN:cancel}: put back`; }
      else if (slotAt()) { h1 = `{BTN:confirm}: options   ${flip}   {BTN:cancel}: close`; }
      else { h1 = `${flip}   {BTN:cancel}: close`; }
      hint.setText(fmtKeys(h1.trim()));
    };
    const refresh = ({ box: b = false, team = false, slide = 0 } = {}) => {
      if (b) { renderBox(slide); } else { renderHead(); }
      if (team) { renderTeam(); }
      renderDetail();
      renderCursor();
    };
    const switchBox = (d) => {
      box = (box + d + nb) % nb;
      S.pcBox = box;
      audio.sfx('cursor');
      refresh({ box: true, slide: d });
    };

    // somewhere free for a Morph: its own space first, then this box, then any box, then the team
    const putBack = () => {
      if (!held) { return; }
      const m = held;
      const spots = [heldFrom, hole].filter(Boolean);
      held = null; heldFrom = null; hole = null;
      for (const from of spots) {
        if (from.party && party().length < 6) { party().splice(Math.min(from.i ?? 6, party().length), 0, m); return; }
        if (from.box !== undefined && !boxes[from.box].slots[from.k]) { healMon(m); boxes[from.box].slots[from.k] = m; return; }
      }
      for (const b of [boxes[box], ...boxes]) {
        const k = b.slots.indexOf(null);
        if (k >= 0) { healMon(m); b.slots[k] = m; return; }
      }
      party().push(m); // (can't happen: something was always freed when it was picked up)
    };
    const pickUp = () => {
      if (zone === 'box') {
        const k = cy * 6 + cx;
        held = boxes[box].slots[k]; boxes[box].slots[k] = null; heldFrom = { box, k }; hole = heldFrom;
        return true;
      }
      const m = party()[pi];
      if (!healthy(party().filter((x) => x !== m))) { audio.blip('bump'); say('Your last healthy Morph has to stay with you!', 'red'); return false; }
      party().splice(pi, 1); held = m; heldFrom = { party: true, i: pi }; hole = heldFrom;
      return true;
    };
    const place = () => {
      if (zone === 'box') {
        const k = cy * 6 + cx;
        const here = boxes[box].slots[k];
        healMon(held);                                  // storage heals
        boxes[box].slots[k] = held;
        held = here || null; heldFrom = here ? { box, k } : null;
        if (!held) { hole = null; }
        return true;
      }
      const here = party()[pi];
      if (!here) { party().push(held); held = null; heldFrom = null; hole = null; pi = party().length - 1; return true; }
      const after = party().map((x) => (x === here ? held : x));
      if (!healthy(after)) { audio.blip('bump'); say('Your team needs at least one healthy Morph!', 'red'); return false; }
      party()[pi] = held; held = here; heldFrom = { party: true, i: pi };
      return true;
    };
    const firstFree = (from) => {
      for (let j = 0; j < nb; j++) {
        const b = (from + j) % nb;
        const k = boxes[b].slots.indexOf(null);
        if (k >= 0) { return { b, k }; }
      }
      return null;
    };

    const onKey = () => {
      const o = this.owner;
      if (input.pressed('pageup', o)) { switchBox(-1); return undefined; }
      if (input.pressed('pagedown', o) || input.pressed('run', o)) { switchBox(1); return undefined; }
      let moved = false;
      if (zone === 'head') {
        if (input.nav('left', o)) { switchBox(-1); return undefined; }
        if (input.nav('right', o)) { switchBox(1); return undefined; }
        if (input.nav('down', o)) { zone = 'box'; cy = 0; moved = true; }
        else if (input.nav('up', o)) { zone = 'box'; cy = 4; moved = true; }
      } else if (zone === 'box') {
        if (input.nav('left', o)) { if (cx > 0) { cx--; } else { zone = 'team'; pi = Math.min(Math.floor(cy * 6 / 5), teamRows() - 1); } moved = true; }
        else if (input.nav('right', o)) { if (cx < 5) { cx++; } else { zone = 'team'; pi = Math.min(Math.floor(cy * 6 / 5), teamRows() - 1); } moved = true; }
        else if (input.nav('up', o)) { if (cy > 0) { cy--; } else { zone = 'head'; } moved = true; }
        else if (input.nav('down', o)) { if (cy < 4) { cy++; } else { zone = 'head'; } moved = true; }
      } else {
        const n = teamRows();
        if (input.nav('left', o)) { zone = 'box'; cx = 5; cy = Math.min(4, Math.floor(pi * 5 / 6)); moved = true; }
        else if (input.nav('right', o)) { zone = 'box'; cx = 0; cy = Math.min(4, Math.floor(pi * 5 / 6)); moved = true; }
        else if (input.nav('up', o)) { pi = (pi + n - 1) % n; moved = true; }
        else if (input.nav('down', o)) { pi = (pi + 1) % n; moved = true; }
      }
      if (moved) { audio.sfx('cursor'); refresh(); return undefined; }
      if (input.pressed('confirm', o)) { return 'confirm'; }
      if (input.pressed('info', o) && !held && slotAt()) { return 'summary'; }
      if (input.pressed('cancel', o)) { return 'cancel'; }
      return undefined;
    };

    refresh({ box: true, team: true });
    try {
      for (;;) {
        const act = await this.loop(onKey);
        if (act === 'cancel') {
          if (held) { putBack(); audio.sfx('cancel'); refresh({ box: true, team: true }); continue; }
          audio.sfx('cancel');
          return null;
        }
        if (act === 'summary') { audio.sfx('select'); await this._storageSummary(zone, box, cy * 6 + cx, pi, (k) => { if (zone === 'box') { cx = k % 6; cy = Math.floor(k / 6); } else { pi = k; } }); refresh(); continue; }
        // confirm
        if (zone === 'head') { audio.sfx('select'); await this._boxOptions(box, (b) => { box = b; S.pcBox = b; }, () => refresh({ box: true })); refresh({ box: true }); continue; }
        if (held) {
          if (place()) { audio.sfx('select'); }
          refresh({ box: true, team: true });
          continue;
        }
        const m = slotAt();
        if (!m) { audio.blip('bump'); continue; }
        audio.sfx('select');
        const inTeam = zone === 'team';
        const opts = [{ label: 'Move', value: 'move' }, { label: 'Summary', value: 'sum' }];
        if (inTeam) { opts.push({ label: 'Deposit', value: 'deposit' }); }
        else { opts.push({ label: 'Withdraw', value: 'withdraw', disabled: party().length >= 6, right: party().length >= 6 ? 'full' : undefined }); }
        opts.push({ label: 'Release', value: 'release' }, { label: 'Cancel', value: null });
        const opt = await choose(this, opts, { x: GAME_W - 10, y: GAME_H - 20, anchor: 'bottom-right', depth: 20 });
        if (opt === 'move') { if (pickUp()) { audio.sfx('select'); } refresh({ box: true, team: true }); }
        else if (opt === 'sum') { await this._storageSummary(zone, box, cy * 6 + cx, pi, (k) => { if (zone === 'box') { cx = k % 6; cy = Math.floor(k / 6); } else { pi = k; } }); refresh(); }
        else if (opt === 'withdraw') {
          const k = cy * 6 + cx;
          boxes[box].slots[k] = null; party().push(m);
          audio.sfx('heal'); say(`${monName(m)} joined your team.`);
          refresh({ box: true, team: true });
        } else if (opt === 'deposit') {
          if (!healthy(party().filter((x) => x !== m))) { audio.blip('bump'); say('Your last healthy Morph has to stay with you!', 'red'); }
          else {
            const spot = firstFree(box);
            if (!spot) { audio.blip('bump'); say('Every box is full!', 'red'); }
            else {
              party().splice(pi, 1); healMon(m); boxes[spot.b].slots[spot.k] = m;
              pi = Math.max(0, Math.min(pi, party().length - 1));
              audio.sfx('heal'); say(`${monName(m)} was sent to ${boxes[spot.b].name}.`);
            }
          }
          refresh({ box: true, team: true });
        } else if (opt === 'release') {
          if (inTeam && !healthy(party().filter((x) => x !== m))) { audio.blip('bump'); say('Your last healthy Morph has to stay with you!', 'red'); }
          else if (await this.confirm(`Release ${monName(m)}? It won't come back.`)) {
            if (inTeam) { party().splice(pi, 1); pi = Math.max(0, Math.min(pi, party().length - 1)); }
            else { boxes[box].slots[cy * 6 + cx] = null; }
            audio.sfx('cancel');
            say(`${monName(m)} was released. Bye-bye, ${monName(m)}!`);
          }
          refresh({ box: true, team: true });
        } else { refresh(); }
      }
    } finally {
      putBack();                                        // never lose a carried Morph, whatever closes the PC
      if (noteTimer) { noteTimer.remove(); }
      carryBob.remove();
      boxLayer.clearMask(true);
      layers.forEach((o) => o.destroy());
    }
  }

  // Summary for a Morph in the PC; up/down flips through the others in the same box (or the team).
  // setIndex(k) moves the PC cursor onto whichever Morph the summary ended on.
  async _storageSummary(zone, box, k, pi, setIndex) {
    if (zone === 'team') { setIndex(await this.summary(pi, G.state.party)); return; }
    const slots = G.state.boxes[box].slots;
    const list = slots.filter(Boolean);
    const at = list.indexOf(slots[k]);
    if (at < 0) { return; }
    const j = await this.summary(at, list);
    setIndex(slots.indexOf(list[j]));
  }

  // Box options: jump to any box, rename it, change its wallpaper or sort it.
  async _boxOptions(box, setBox, redraw) {
    const S = G.state;
    const bx = S.boxes[box];
    const opt = await choose(this, [
      { label: 'Jump to box', value: 'jump' }, { label: 'Rename', value: 'name' }, { label: 'Wallpaper', value: 'wall' },
      { label: 'Sort', value: 'sort' }, { label: 'Cancel', value: null },
    ], { x: 10, y: 30, depth: 20 });
    if (opt === 'jump') {
      const items = S.boxes.map((b, i) => ({ label: b.name, right: `${b.slots.filter(Boolean).length}/30`, value: i }));
      const pick = await choose(this, items, { x: 10, y: 30, width: 150, visible: 12, index: box, depth: 20 });
      if (pick !== null && pick !== undefined) { setBox(pick); }
    } else if (opt === 'name') {
      const name = await nameEntry(this, { title: 'Name this box', initial: bx.name, max: 12, owner: this.owner, allowEmpty: true, depth: 60 });
      input.clear();
      if (name !== null) { bx.name = name.replace(/[^A-Za-z0-9 '\-.!?]/g, '').slice(0, 12).trim() || `Box ${box + 1}`; }
    } else if (opt === 'wall') {
      const was = bx.wall;
      const items = WALLPAPERS.map((w, i) => ({ label: w.name, value: i }));
      const pick = await choose(this, items, { x: 10, y: 30, width: 104, index: was, depth: 20, onMove: (_, i) => { bx.wall = i; redraw(); } });
      bx.wall = pick === null || pick === undefined ? was : pick;
    } else if (opt === 'sort') {
      const how = await choose(this, [
        { label: 'By Index No.', value: 'num' }, { label: 'By level', value: 'level' }, { label: 'By name', value: 'name' },
        { label: 'By type', value: 'type' }, { label: 'Close gaps', value: 'gaps' }, { label: 'Cancel', value: null },
      ], { x: 10, y: 30, depth: 21 });
      if (how) {
        const list = bx.slots.filter(Boolean);
        const num = (m) => SPECIES[m.species].num;
        const by = {
          num: (a, b) => num(a) - num(b) || b.level - a.level,
          level: (a, b) => b.level - a.level || num(a) - num(b),
          name: (a, b) => monName(a).localeCompare(monName(b)) || b.level - a.level,
          type: (a, b) => SPECIES[a.species].types[0].localeCompare(SPECIES[b.species].types[0]) || num(a) - num(b),
        }[how];
        if (by) { list.sort(by); }
        bx.slots = Array.from({ length: bx.slots.length }, (_, k) => list[k] || null);
        audio.sfx('select');
      }
    }
  }

  // Box wallpapers: drawn once into a texture each.
  _wallpaper(i) {
    const w = WALLPAPERS[((i % WALLPAPERS.length) + WALLPAPERS.length) % WALLPAPERS.length] || WALLPAPERS[0];
    const key = `pcwall_${w.id}`;
    if (this.textures.exists(key)) { return key; }
    const W = 228, H = 212;
    const g = this.make.graphics({ x: 0, y: 0 }, false);
    g.fillStyle(w.base).fillRect(0, 0, W, H);
    g.fillStyle(w.accent);
    const P = w.pattern;
    if (P === 'grass') { for (let y = 6; y < H; y += 14) { for (let x = (y / 14) % 2 ? 4 : 11; x < W; x += 14) { g.fillRect(x, y + 2, 1, 3); g.fillRect(x + 2, y, 1, 5); g.fillRect(x + 4, y + 2, 1, 3); } } }
    if (P === 'waves') { for (let y = 8; y < H; y += 16) { for (let x = 0; x < W; x += 2) { g.fillRect(x, y + Math.round(2 * Math.sin(x / 5)), 2, 1); } } }
    if (P === 'diamonds') { for (let y = 0; y < H + 12; y += 20) { for (let x = (y / 20) % 2 ? 10 : 0; x < W + 10; x += 20) { g.fillTriangle(x, y - 6, x + 6, y, x, y + 6); g.fillTriangle(x, y - 6, x - 6, y, x, y + 6); } } }
    if (P === 'snow') { for (let y = 5; y < H; y += 17) { for (let x = (y / 17) % 2 ? 3 : 12; x < W; x += 18) { g.fillRect(x - 2, y, 5, 1); g.fillRect(x, y - 2, 1, 5); } } }
    if (P === 'stripes') { for (let x = -H; x < W; x += 12) { g.fillStyle(w.accent).beginPath(); g.moveTo(x, H); g.lineTo(x + H, 0); g.lineTo(x + H + 5, 0); g.lineTo(x + 5, H); g.closePath(); g.fillPath(); } }
    if (P === 'bricks') { for (let y = 0; y < H; y += 12) { g.fillRect(0, y, W, 1); for (let x = (y / 12) % 2 ? 0 : 12; x < W; x += 24) { g.fillRect(x, y, 1, 12); } } }
    if (P === 'petals') { for (let y = 8; y < H; y += 22) { for (let x = (y / 22) % 2 ? 6 : 17; x < W; x += 22) { g.fillCircle(x, y, 2); g.fillCircle(x + 3, y + 2, 2); g.fillCircle(x - 1, y + 3, 2); } } }
    if (P === 'stars') {
      let seed = 7;
      const rnd = () => { seed = (seed * 16807) % 2147483647; return seed / 2147483647; };
      for (let n = 0; n < 90; n++) { g.fillStyle(n % 5 ? w.accent : 0xd8dcff, n % 5 ? 1 : 0.8).fillRect(Math.floor(rnd() * W), Math.floor(rnd() * H), 1, 1); }
    }
    g.generateTexture(key, W, H);
    g.destroy();
    return key;
  }

  _msg(c, text) {
    const t = txt(this, GAME_W / 2, GAME_H - 34, text, { align: 'center', color: 'red' });
    this.time.delayedCall(1300, () => t.destroy());
  }
}
