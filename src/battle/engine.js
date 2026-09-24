// Battle rules engine. Drives a battle through an async `ui` interface so the
// same code runs the animated BattleScene and the headless balance simulator.
import { SPECIES } from '../data/species.js';
import { MOVES } from '../data/moves.js';
import { ITEMS } from '../data/items.js';
import { effectiveness } from '../data/types.js';
import { calcStats, maxHp, monName, addXp, learnMove, STAT_NAMES, isFainted } from './mon.js';
import { chooseEnemyMove } from './ai.js';

const STAGE_KEYS = ['atk', 'def', 'spa', 'spd', 'spe', 'acc', 'eva'];

function stageMult(s) { return s >= 0 ? (2 + s) / 2 : 2 / (2 - s); }
function accMult(s) { return s >= 0 ? (3 + s) / 3 : 3 / (3 - s); }

export class Battler {
  constructor(side, party) {
    this.side = side;          // 0 player, 1 enemy
    this.party = party;
    this.index = party.findIndex((m) => m.hp > 0);
    if (this.index < 0) { this.index = 0; }
    this.reset();
  }
  get mon() { return this.party[this.index]; }
  reset() {
    this.stages = { atk: 0, def: 0, spa: 0, spd: 0, spe: 0, acc: 0, eva: 0 };
    this.confused = 0;
    this.flinch = false;
    this.seeded = false;
    this.protect = false;
    this.protectCount = 0;
    this.charging = null;
    this.toxic = 0;
    this.lastMove = null;
    this.turnsOut = 0;
  }
  stat(k) {
    const base = calcStats(this.mon)[k];
    let v = base * stageMult(this.stages[k] || 0);
    if (k === 'spe' && this.mon.status === 'paralyze') { v *= 0.5; }
    return Math.max(1, Math.floor(v));
  }
  alive() { return this.party.filter((m) => m.hp > 0); }
  types() { return SPECIES[this.mon.species].types; }
}

export class Battle {
  constructor({ playerParty, enemyParty, kind = 'wild', trainer = null, ui, rng = Math.random, opts = {} }) {
    this.kind = kind;
    this.trainer = trainer;
    this.ui = ui;
    this.rng = rng;
    this.opts = opts;
    this.p = new Battler(0, playerParty);
    this.e = new Battler(1, enemyParty);
    this.turn = 0;
    this.runs = 0;
    this.participants = new Set([this.p.mon.uid]);
    this.outcome = null;
    this.enemyItemsLeft = [...(trainer?.items || [])];
    this.caught = null;
    this.levelled = new Set();
  }

  name(b) {
    const n = monName(b.mon);
    if (b.side === 1) { return this.kind === 'wild' ? `The wild ${n}` : `The foe's ${n}`; }
    return n;
  }

  // ─── main loop ───────────────────────────────────────────────────────
  async run() {
    await this.ui.intro(this);
    while (!this.outcome) {
      this.turn++;
      this.p.protect = false; this.e.protect = false;
      this.p.flinch = false; this.e.flinch = false;
      let pAct;
      if (this.p.charging) {
        pAct = { type: 'move', index: this.p.mon.moves.findIndex((m) => m.id === this.p.charging), forced: this.p.charging };
      } else {
        pAct = await this.ui.chooseAction(this);
      }
      if (pAct.type === 'run') {
        const ok = await this.tryRun();
        if (ok) { this.outcome = 'fled'; break; }
        pAct = { type: 'none' };
      }
      const eAct = this.enemyAction();
      // switches and items happen first
      if (pAct.type === 'switch') { await this.doSwitch(this.p, pAct.index); }
      if (pAct.type === 'item') {
        const res = await this.useItem(pAct.item, pAct.target);
        if (res === 'caught') { this.outcome = 'caught'; break; }
      }
      if (eAct.type === 'item') { await this.enemyUseItem(eAct.item); }
      // moves ordered by priority, then speed
      const queue = [];
      if (pAct.type === 'move') { queue.push({ b: this.p, t: this.e, move: this.moveFor(this.p, pAct.index), slot: pAct.index }); }
      if (eAct.type === 'move') { queue.push({ b: this.e, t: this.p, move: this.moveFor(this.e, eAct.index), slot: eAct.index }); }
      queue.sort((a, b) => {
        if (b.move.prio !== a.move.prio) { return b.move.prio - a.move.prio; }
        const sa = a.b.stat('spe'), sb = b.b.stat('spe');
        if (sa !== sb) { return sb - sa; }
        return this.rng() < 0.5 ? -1 : 1;
      });
      for (const q of queue) {
        if (this.outcome) { break; }
        if (q.b.mon.hp <= 0 || q.b !== (q.b.side === 0 ? this.p : this.e)) { continue; }
        if (q.b.mon !== q.b.party[q.b.index]) { continue; }
        await this.useMove(q.b, q.t, q.move, q.slot);
        if (await this.checkFaints()) { break; }
      }
      if (this.outcome) { break; }
      await this.endOfTurn();
      await this.checkFaints();
    }
    await this.ui.end(this, this.outcome);
    return this.outcome;
  }

  moveFor(b, index) {
    const slot = b.mon.moves[index];
    if (!slot || (slot.pp <= 0 && !b.charging)) { return MOVES.flail_out; }
    return MOVES[slot.id];
  }

  enemyAction() {
    if (this.e.charging) {
      return { type: 'move', index: this.e.mon.moves.findIndex((m) => m.id === this.e.charging) };
    }
    // trainers may heal once when low
    if (this.kind !== 'wild' && this.enemyItemsLeft.length && this.e.mon.hp / maxHp(this.e.mon) < 0.25 && this.rng() < 0.8) {
      return { type: 'item', item: this.enemyItemsLeft.shift() };
    }
    const idx = chooseEnemyMove(this, this.e, this.p, this.kind === 'wild' ? (this.opts.wildSkill ?? 0) : (this.trainer?.skill ?? 1));
    return { type: 'move', index: idx };
  }

  // ─── actions ─────────────────────────────────────────────────────────
  async tryRun() {
    if (this.kind !== 'wild' || this.opts.noRun) {
      await this.ui.message(this.kind === 'wild' ? "You can't run from this battle!" : "There's no running from a Tamer battle!");
      return false;
    }
    this.runs++;
    const ps = this.p.stat('spe'), es = this.e.stat('spe');
    const odds = Math.floor((ps * 128) / Math.max(1, es)) + 30 * this.runs;
    if (ps >= es || this.rng() * 256 < odds) {
      await this.ui.message('You got away safely!');
      return true;
    }
    await this.ui.message("Couldn't get away!");
    return false;
  }

  async doSwitch(b, index, forced = false) {
    if (!forced) { await this.ui.withdraw(this, b); }
    b.index = index;
    b.reset();
    if (b.side === 0) { this.participants.add(b.mon.uid); }
    await this.ui.sendOut(this, b);
  }

  async enemyUseItem(itemId) {
    const it = ITEMS[itemId];
    const mon = this.e.mon;
    const mx = maxHp(mon);
    const before = mon.hp;
    mon.hp = Math.min(mx, mon.hp + (it?.use?.hp || 60));
    if (it?.use?.cure) { mon.status = null; }
    await this.ui.message(`${this.trainer.name} used a ${it ? it.name : 'Tonic'}!`);
    await this.ui.hp(this, this.e, before, mon.hp);
  }

  async useItem(itemId, targetIndex) {
    const it = ITEMS[itemId];
    const u = it.use;
    if (u.kind === 'capsule') { return this.throwCapsule(itemId); }
    const mon = this.p.party[targetIndex ?? this.p.index];
    const mx = maxHp(mon);
    await this.ui.message(`You used a ${it.name}.`);
    if (u.kind === 'heal') {
      const before = mon.hp;
      mon.hp = Math.min(mx, mon.hp + u.hp);
      if (u.cure) { mon.status = null; mon.statusTurns = 0; if (mon === this.p.mon) { this.p.confused = 0; } }
      if (mon === this.p.mon) { await this.ui.hp(this, this.p, before, mon.hp); }
      await this.ui.message(`${monName(mon)} recovered ${mon.hp - before} HP!`);
    } else if (u.kind === 'cure') {
      mon.status = null; mon.statusTurns = 0;
      if (u.status === 'all' && mon === this.p.mon) { this.p.confused = 0; }
      await this.ui.message(`${monName(mon)} feels much better!`);
    } else if (u.kind === 'revive') {
      mon.hp = Math.max(1, Math.floor(mx * u.frac));
      mon.status = null;
      await this.ui.message(`${monName(mon)} was revived!`);
    } else if (u.kind === 'pp') {
      mon.moves.forEach((m) => { m.pp = Math.min(m.max, m.pp + u.pp); });
      await this.ui.message(`${monName(mon)}'s PP was restored.`);
    }
    await this.ui.refresh(this);
    return 'used';
  }

  async throwCapsule(itemId) {
    const it = ITEMS[itemId];
    if (this.kind !== 'wild') {
      await this.ui.message("You can't take another Tamer's Morph!");
      return 'blocked';
    }
    const mon = this.e.mon;
    const sp = SPECIES[mon.species];
    const mx = maxHp(mon);
    let ball = it.use.rate;
    if (it.use.dusk && (this.opts.night || this.opts.cave)) { ball = it.use.dusk; }
    if (it.use.firstTurn && this.turn === 1) { ball = it.use.firstTurn; }
    const statusBonus = ['sleep', 'freeze'].includes(mon.status) ? 2.5 : (mon.status ? 1.5 : 1);
    const a = (((3 * mx - 2 * mon.hp) * sp.catch * ball) / (3 * mx)) * statusBonus;
    let shakes = 0;
    let caught = false;
    if (a >= 255 || ball >= 255) { shakes = 3; caught = true; }
    else {
      const b = 1048560 / Math.sqrt(Math.sqrt(16711680 / a));
      let passes = 0;
      for (let i = 0; i < 4; i++) { if (this.rng() * 65536 < b) { passes++; } else { break; } }
      shakes = Math.min(3, passes);
      caught = passes === 4;
    }
    await this.ui.capture(this, itemId, shakes, caught);
    if (caught) {
      this.caught = mon;
      await this.ui.message(`Gotcha! ${sp.name} was caught!`);
      await this.awardXp(true);
      return 'caught';
    }
    const lines = ['Oh no! It broke free!', 'Argh! Almost had it!', 'Aww! It appeared to be caught!', 'Gah! So close!'];
    await this.ui.message(lines[shakes]);
    return 'failed';
  }

  // ─── moves ───────────────────────────────────────────────────────────
  async canAct(b) {
    const mon = b.mon;
    const nm = this.name(b);
    if (mon.status === 'sleep') {
      mon.statusTurns--;
      if (mon.statusTurns <= 0) {
        mon.status = null;
        await this.ui.message(`${nm} woke up!`);
        await this.ui.refresh(this);
      } else {
        await this.ui.statusAnim(this, b, 'sleep');
        await this.ui.message(`${nm} is fast asleep.`);
        b.charging = null;
        return false;
      }
    }
    if (mon.status === 'freeze') {
      if (this.rng() < 0.2) {
        mon.status = null;
        await this.ui.message(`${nm} thawed out!`);
        await this.ui.refresh(this);
      } else {
        await this.ui.statusAnim(this, b, 'freeze');
        await this.ui.message(`${nm} is frozen solid!`);
        return false;
      }
    }
    if (b.flinch) {
      await this.ui.message(`${nm} flinched and couldn't move!`);
      b.charging = null;
      return false;
    }
    if (b.confused > 0) {
      b.confused--;
      if (b.confused <= 0) {
        await this.ui.message(`${nm} snapped out of its confusion!`);
      } else {
        await this.ui.statusAnim(this, b, 'confuse');
        await this.ui.message(`${nm} is confused!`);
        if (this.rng() < 0.33) {
          const dmg = this.rawDamage(b, b, 40, 'phys', null, false, 1).damage;
          const before = mon.hp;
          mon.hp = Math.max(0, mon.hp - dmg);
          await this.ui.hitFlash(this, b);
          await this.ui.hp(this, b, before, mon.hp);
          await this.ui.message('It hurt itself in its confusion!');
          b.charging = null;
          return false;
        }
      }
    }
    if (mon.status === 'paralyze' && this.rng() < 0.25) {
      await this.ui.statusAnim(this, b, 'paralyze');
      await this.ui.message(`${nm} is paralysed! It can't move!`);
      b.charging = null;
      return false;
    }
    return true;
  }

  async useMove(b, t, move, slot) {
    if (!(await this.canAct(b))) { return; }
    const nm = this.name(b);
    // charge turn
    if (move.fx.charge && b.charging !== move.id) {
      b.charging = move.id;
      if (slot >= 0 && b.mon.moves[slot]) { b.mon.moves[slot].pp = Math.max(0, b.mon.moves[slot].pp - 1); }
      await this.ui.message(`${nm} ${move.fx.charge}`);
      await this.ui.charge(this, b);
      return;
    }
    const wasCharging = b.charging === move.id;
    b.charging = null;
    if (!wasCharging && move.id !== 'flail_out' && slot >= 0 && b.mon.moves[slot]) {
      b.mon.moves[slot].pp = Math.max(0, b.mon.moves[slot].pp - 1);
    }
    if (move.id === 'flail_out') { await this.ui.message(`${nm} has no moves left!`); }
    await this.ui.message(`${nm} used ${move.name}!`);
    b.lastMove = move.id;
    // protect
    if (move.fx.protect) {
      const chance = Math.pow(1 / 3, b.protectCount);
      if (this.rng() < chance) {
        b.protect = true; b.protectCount++;
        await this.ui.moveAnim(this, b, t, move);
        await this.ui.message(`${nm} braced itself!`);
      } else {
        b.protectCount = 0;
        await this.ui.message('But it failed!');
      }
      return;
    }
    b.protectCount = 0;
    const targetsFoe = move.cat !== 'status' || move.fx.target === 'foe' || move.fx.status || move.fx.confuse || move.fx.seed;
    if (targetsFoe && t.protect) {
      await this.ui.message(`${this.name(t)} protected itself!`);
      return;
    }
    // accuracy
    if (move.acc !== null && targetsFoe) {
      const acc = move.acc * accMult(b.stages.acc - t.stages.eva);
      if (this.rng() * 100 >= acc) {
        await this.ui.message(`${this.name(t)} avoided the attack!`);
        return;
      }
    }
    if (move.cat === 'status') {
      await this.ui.moveAnim(this, b, t, move);
      await this.applyStatusMove(b, t, move);
      return;
    }
    // damaging move
    const eff = effectiveness(move.type, t.types());
    if (eff === 0) {
      await this.ui.message(`It doesn't affect ${this.name(t)}...`);
      return;
    }
    const hits = move.fx.multi ? this.rollHits(move.fx.multi) : 1;
    let total = 0;
    let crits = 0;
    let n = 0;
    for (let i = 0; i < hits; i++) {
      if (t.mon.hp <= 0) { break; }
      let res;
      if (move.fx.fixed === 'level') {
        res = { damage: b.mon.level, crit: false };
      } else {
        res = this.rawDamage(b, t, move.power, move.cat, move.type, move.fx.highCrit, eff);
      }
      await this.ui.moveAnim(this, b, t, move, eff);
      const before = t.mon.hp;
      t.mon.hp = Math.max(0, t.mon.hp - res.damage);
      total += before - t.mon.hp;
      if (res.crit) { crits++; }
      await this.ui.hitFlash(this, t, eff, res.crit);
      await this.ui.hp(this, t, before, t.mon.hp);
      n++;
      if (res.crit && hits > 1) { await this.ui.message('A critical hit!'); }
    }
    if (crits && hits === 1) { await this.ui.message('A critical hit!'); }
    if (eff > 1) { await this.ui.message("It's super effective!"); }
    else if (eff < 1) { await this.ui.message("It's not very effective..."); }
    if (hits > 1) { await this.ui.message(`Hit ${n} time${n > 1 ? 's' : ''}!`); }
    // thaw frozen target with Ember
    if (move.type === 'Ember' && t.mon.status === 'freeze') { t.mon.status = null; await this.ui.message(`${this.name(t)} thawed out!`); }
    // drain / recoil
    if (move.fx.drain && total > 0 && b.mon.hp > 0) {
      const heal = Math.max(1, Math.floor(total * move.fx.drain));
      const before = b.mon.hp;
      b.mon.hp = Math.min(maxHp(b.mon), b.mon.hp + heal);
      await this.ui.hp(this, b, before, b.mon.hp);
      await this.ui.message(`${this.name(t)} had its energy drained!`);
    }
    if (move.fx.recoil && total > 0) {
      const dmg = Math.max(1, Math.floor(total * move.fx.recoil));
      const before = b.mon.hp;
      b.mon.hp = Math.max(0, b.mon.hp - dmg);
      await this.ui.hp(this, b, before, b.mon.hp);
      await this.ui.message(`${nm} is hurt by recoil!`);
    }
    // secondary effects (only if target still standing)
    if (t.mon.hp > 0) {
      if (move.fx.status && this.rng() < (move.fx.chance ?? 1)) { await this.inflict(t, move.fx.status, false); }
      if (move.fx.confuse && this.rng() < move.fx.confuse && !t.confused) {
        t.confused = 2 + Math.floor(this.rng() * 4);
        await this.ui.statusAnim(this, t, 'confuse');
        await this.ui.message(`${this.name(t)} became confused!`);
      }
      if (move.fx.flinch && this.rng() < move.fx.flinch) { t.flinch = true; }
      if (move.fx.stat && move.fx.target === 'foe' && this.rng() < (move.fx.chance ?? 1)) { await this.changeStats(t, move.fx.stat); }
    }
    if (move.fx.stat && move.fx.target === 'self' && this.rng() < (move.fx.chance ?? 1)) { await this.changeStats(b, move.fx.stat); }
    if (move.fx.selfStat) { await this.changeStats(b, move.fx.selfStat); }
  }

  rollHits([lo, hi]) {
    // 2:35%, 3:35%, 4:15%, 5:15% (for 2-5)
    if (lo === 2 && hi === 5) {
      const r = this.rng();
      return r < 0.35 ? 2 : r < 0.7 ? 3 : r < 0.85 ? 4 : 5;
    }
    return lo + Math.floor(this.rng() * (hi - lo + 1));
  }

  rawDamage(b, t, power, cat, type, highCrit, eff) {
    const L = b.mon.level;
    const phys = cat === 'phys';
    const critChance = highCrit ? 1 / 8 : 1 / 16;
    const crit = type !== null && this.rng() < critChance;
    let aStage = phys ? b.stages.atk : b.stages.spa;
    let dStage = phys ? t.stages.def : t.stages.spd;
    if (crit) { aStage = Math.max(0, aStage); dStage = Math.min(0, dStage); }
    const A = Math.max(1, Math.floor(calcStats(b.mon)[phys ? 'atk' : 'spa'] * stageMult(aStage)));
    const D = Math.max(1, Math.floor(calcStats(t.mon)[phys ? 'def' : 'spd'] * stageMult(dStage)));
    let dmg = Math.floor(Math.floor(Math.floor((2 * L) / 5 + 2) * power * A / D) / 50) + 2;
    if (crit) { dmg = Math.floor(dmg * 1.5); }
    dmg = Math.floor(dmg * (0.85 + this.rng() * 0.15));
    if (type && b.types().includes(type)) { dmg = Math.floor(dmg * 1.5); }
    dmg = Math.floor(dmg * eff);
    if (phys && b.mon.status === 'burn') { dmg = Math.floor(dmg / 2); }
    return { damage: Math.max(1, dmg), crit };
  }

  async applyStatusMove(b, t, move) {
    const fx = move.fx;
    let did = false;
    if (fx.heal) {
      const mx = maxHp(b.mon);
      if (b.mon.hp >= mx) { await this.ui.message(`${this.name(b)}'s HP is already full!`); return; }
      const before = b.mon.hp;
      b.mon.hp = Math.min(mx, b.mon.hp + Math.floor(mx * fx.heal));
      await this.ui.hp(this, b, before, b.mon.hp);
      await this.ui.message(`${this.name(b)} restored its health!`);
      return;
    }
    if (fx.status) { did = (await this.inflict(t, fx.status, true)) || did; }
    if (fx.confuse) {
      if (t.confused) { await this.ui.message(`${this.name(t)} is already confused!`); }
      else {
        t.confused = 2 + Math.floor(this.rng() * 4);
        await this.ui.statusAnim(this, t, 'confuse');
        await this.ui.message(`${this.name(t)} became confused!`);
      }
      did = true;
    }
    if (fx.seed) {
      if (t.seeded || t.types().includes('Nature')) { await this.ui.message('But it failed!'); }
      else { t.seeded = true; await this.ui.message(`${this.name(t)} was snared by roots!`); }
      did = true;
    }
    if (fx.stat) {
      const target = fx.target === 'self' ? b : t;
      await this.changeStats(target, fx.stat);
      did = true;
    }
    if (!did) { await this.ui.message('But nothing happened!'); }
  }

  async inflict(t, status, announceFail) {
    const mon = t.mon;
    const types = t.types();
    const immune = (status === 'burn' && types.includes('Ember')) || (status === 'freeze' && types.includes('Frost'))
      || ((status === 'poison' || status === 'toxic') && (types.includes('Toxin') || types.includes('Iron')))
      || (status === 'paralyze' && types.includes('Static'));
    if (mon.status || immune) {
      if (announceFail) { await this.ui.message(mon.status ? `${this.name(t)} is already ${statusWord(mon.status)}!` : `It doesn't affect ${this.name(t)}...`); }
      return false;
    }
    mon.status = status;
    if (status === 'sleep') { mon.statusTurns = 1 + Math.floor(this.rng() * 3); }
    if (status === 'toxic') { t.toxic = 0; }
    await this.ui.statusAnim(this, t, status);
    await this.ui.message(`${this.name(t)} ${statusVerb(status)}`);
    await this.ui.refresh(this);
    return true;
  }

  async changeStats(b, changes) {
    for (const [k, v] of Object.entries(changes)) {
      const cur = b.stages[k] || 0;
      const nv = Math.max(-6, Math.min(6, cur + v));
      const nm = this.name(b);
      if (nv === cur) {
        await this.ui.message(`${nm}'s ${STAT_NAMES[k]} won't go any ${v > 0 ? 'higher' : 'lower'}!`);
        continue;
      }
      b.stages[k] = nv;
      await this.ui.statAnim(this, b, v > 0);
      const amt = Math.abs(v) >= 2 ? (v > 0 ? 'rose sharply' : 'harshly fell') : (v > 0 ? 'rose' : 'fell');
      await this.ui.message(`${nm}'s ${STAT_NAMES[k]} ${amt}!`);
    }
  }

  async endOfTurn() {
    for (const b of [this.p, this.e]) {
      const mon = b.mon;
      if (mon.hp <= 0) { continue; }
      b.turnsOut++;
      const mx = maxHp(mon);
      let dmg = 0;
      let msg = null;
      if (mon.status === 'burn') { dmg = Math.max(1, Math.floor(mx / 16)); msg = `${this.name(b)} is hurt by its burn!`; }
      if (mon.status === 'poison') { dmg = Math.max(1, Math.floor(mx / 8)); msg = `${this.name(b)} is hurt by poison!`; }
      if (mon.status === 'toxic') { b.toxic++; dmg = Math.max(1, Math.floor((mx * b.toxic) / 16)); msg = `${this.name(b)} is hurt by poison!`; }
      if (dmg) {
        await this.ui.statusAnim(this, b, mon.status);
        const before = mon.hp;
        mon.hp = Math.max(0, mon.hp - dmg);
        await this.ui.hp(this, b, before, mon.hp);
        await this.ui.message(msg);
      }
      if (b.seeded && mon.hp > 0) {
        const other = b === this.p ? this.e : this.p;
        const d = Math.max(1, Math.floor(mx / 8));
        const before = mon.hp;
        mon.hp = Math.max(0, mon.hp - d);
        await this.ui.hp(this, b, before, mon.hp);
        if (other.mon.hp > 0) {
          const ob = other.mon.hp;
          other.mon.hp = Math.min(maxHp(other.mon), other.mon.hp + d);
          await this.ui.hp(this, other, ob, other.mon.hp);
        }
        await this.ui.message(`${this.name(b)}'s health is sapped by the roots!`);
      }
    }
  }

  // Returns true if the battle's turn should stop (someone fainted).
  async checkFaints() {
    let any = false;
    if (this.e.mon.hp <= 0 && !this.e.faintHandled) {
      any = true;
      this.e.faintHandled = true;
      await this.ui.faint(this, this.e);
      await this.ui.message(`${this.name(this.e)} fainted!`);
      await this.awardXp(false);
      const next = this.e.party.findIndex((m) => m.hp > 0);
      if (next < 0) {
        this.outcome = 'win';
        return true;
      }
      // trainer sends out the next Morph
      const shift = this.opts.style !== 'set' && this.p.mon.hp > 0 && this.p.alive().length > 1;
      if (shift) {
        const nextMon = this.e.party[next];
        const sw = await this.ui.askShift(this, nextMon);
        if (sw !== null && sw !== undefined && sw !== this.p.index) { await this.doSwitch(this.p, sw); }
      }
      this.e.index = next; this.e.reset(); this.e.faintHandled = false;
      await this.ui.sendOut(this, this.e);
      this.participants = new Set([this.p.mon.uid]);
    }
    if (this.p.mon.hp <= 0 && !this.outcome) {
      any = true;
      this.p.charging = null;
      await this.ui.faint(this, this.p);
      await this.ui.message(`${monName(this.p.mon)} fainted!`);
      this.participants.delete(this.p.mon.uid);
      if (!this.p.alive().length) {
        this.outcome = 'lose';
        return true;
      }
      const idx = await this.ui.chooseSwitch(this, true);
      await this.doSwitch(this.p, idx, true);
    }
    return any;
  }

  async awardXp(fromCapture) {
    const foe = this.e.mon;
    const sp = SPECIES[foe.species];
    const trainerMult = this.kind === 'trainer' ? 1.5 : 1;
    const parts = this.p.party.filter((m) => m.hp > 0 && this.participants.has(m.uid));
    if (!parts.length) { return; }
    const shareOthers = this.opts.expShare;
    const Le = foe.level;
    const xpFor = (m) => {
      const base = Math.floor((sp.xp * Le) / 5) * trainerMult / parts.length;
      let amt = Math.floor(base * Math.pow((2 * Le + 10) / (Le + m.level + 10), 2.5)) + 1;
      if (this.opts.xpMult) { amt = Math.floor(amt * this.opts.xpMult); }
      return amt;
    };
    // XP Share attached: every healthy Morph gets exactly what the one that fought earned
    if (this.opts.xpShareAll) {
      const amt = xpFor(parts[parts.length - 1]);
      await this.ui.message(`The XP Share glows! Your whole team gains ${amt} XP.`);
      for (const m of this.p.party) {
        if (m.hp <= 0 || m.level >= 100) { continue; }
        await this.giveXp(m, amt, this.participants.has(m.uid), 'share');
      }
      return;
    }
    for (const m of this.p.party) {
      if (m.hp <= 0 || m.level >= 100) { continue; }
      const isPart = this.participants.has(m.uid);
      if (!isPart && !shareOthers) { continue; }
      let amt = xpFor(m);
      if (!isPart) { amt = Math.max(1, Math.floor(amt / 2)); }
      await this.giveXp(m, amt, isPart);
    }
  }

  async giveXp(m, amt, isPart, via) {
    const before = m.level;
    const beforeXp = m.xp;
    const msg = via === 'share' ? `${monName(m)} gained ${amt} XP!` : isPart ? `${monName(m)} gained ${amt} XP!` : `${monName(m)} gained ${amt} XP from the Bond Charm!`;
    await this.ui.message(msg, { quick: via === 'share' || !isPart });
    const steps = addXp(m, amt);
    await this.ui.xp(this, m, beforeXp, steps);
    for (const st of steps) {
      this.levelled.add(m.uid);
      await this.ui.levelUp(this, m, st);
      for (const mv of st.learn) {
        if (learnMove(m, mv)) {
          await this.ui.message(`${monName(m)} learned ${MOVES[mv].name}!`);
        } else {
          await this.ui.learnPrompt(this, m, mv);
        }
      }
    }
    if (m.level !== before && m === this.p.mon) { await this.ui.refresh(this); }
  }
}

export function statusWord(s) {
  return { burn: 'burned', poison: 'poisoned', toxic: 'badly poisoned', paralyze: 'paralysed', sleep: 'asleep', freeze: 'frozen' }[s] || s;
}
function statusVerb(s) {
  return { burn: 'was burned!', poison: 'was poisoned!', toxic: 'was badly poisoned!', paralyze: 'is paralysed! It may be unable to move!', sleep: 'fell asleep!', freeze: 'was frozen solid!' }[s];
}
