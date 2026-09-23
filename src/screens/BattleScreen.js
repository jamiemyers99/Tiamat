// Battle screen — Gen-1 mechanics: damage, catch, run, info panel, wobble.
// Exports: BattleScreen
import { performTurn, attemptCatch, attemptRun } from "../engine/battle.js?v=20260429-19";
import { xpYield } from "../engine/xp.js?v=20260429-19";
import { getEffectiveness, getTypeMatchups } from "../data/typeChart.js?v=20260429-19";
import audio from "../engine/audio.js?v=20260429-19";

const BAG_ITEMS = [
  { id: "capsule",       name: "CAPSULE"       },
  { id: "great_capsule", name: "GREAT CAPSULE" },
  { id: "potion",        name: "POTION"        },
  { id: "super_potion",  name: "SUPER POTION"  },
  { id: "antidote",      name: "ANTIDOTE"      },
  { id: "burnHeal",      name: "BURN HEAL"     },
  { id: "awakening",     name: "AWAKENING"     },
  { id: "paralyzeHeal",  name: "PARALYZ HEAL"  },
  { id: "iceHeal",       name: "ICE HEAL"      },
];

const MOVE_TYPE_BG = {
  Nature: "#3a6010", Ember:  "#943010", Tide:   "#1840a0", Static: "#906800",
  Sprout: "#3a6010", Stone:  "#504810", Mist:   "#404880", Chill:  "#285870",
  Ash:    "#484828", Blaze:  "#802808", Fang:   "#501860", Umbra:  "#302048",
  Gust:   "#286080", Plain:  "#604820", Aqua:   "#1850a0",
};

const STATUS_COLOURS = {
  burn:     "#c83e20",
  poison:   "#8040c0",
  sleep:    "#406080",
  paralyse: "#b8a020",
  freeze:   "#40a0c0",
  confuse:  "#c04080",
};

const STATUS_LABELS = {
  burn:     "BRN",
  poison:   "PSN",
  sleep:    "SLP",
  paralyse: "PAR",
  freeze:   "FRZ",
  confuse:  "CNF",
};

export class BattleScreen {
  constructor(canvas, ctx) {
    this.canvas      = canvas;
    this.ctx         = ctx;
    this._hpAnim     = { enemy: null, player: null };
    this._flashTimer = 0;
    this._flashEnemy = false;
    this._wobble     = null; // { caught, remaining, timer, onResolve }
  }

  // ─── Update ──────────────────────────────────────────────────────────────

  update(state, input, delta, endBattle) {
    const battle = state.battle;
    if (!battle) { return; }

    this._tickHpAnim(battle, delta);

    // Wobble blocks all input during capsule shake animation.
    if (this._wobble) {
      this._tickWobble(delta);
      return;
    }

    if (battle.phase === "message") {
      if (input.wasPressed("e", " ", "enter")) {
        if (battle.enemyCreature.hp <= 0) {
          audio.playSfx("battle_morph_faint");
          const isTrainer = battle.type === "trainer";
          battle.xpEarned += _xpRewardFor(battle.enemyCreature, isTrainer);
          if (isTrainer && battle.enemyPartyIndex < battle.enemyParty.length - 1) {
            battle.enemyPartyIndex += 1;
            battle.enemyCreature = structuredClone(battle.enemyParty[battle.enemyPartyIndex]);
            this._setHpTarget(battle);
            battle.phase = "message";
            battle.log   = `${battle.opponentName} sent out ${battle.enemyCreature.name}!`;
            return;
          }
          endBattle({ outcome: "victory" });
          return;
        }
        if (battle.playerCreature.hp <= 0) {
          audio.playSfx("battle_morph_faint");
          const fIdx = battle.partyIndex ?? 0;
          if (state.party[fIdx]) { state.party[fIdx].hp = 0; }
          const hasLive = state.party.some((c, i) => i !== fIdx && c.hp > 0);
          if (hasLive) {
            battle.phase = "force_switch";
            battle.forceSwitchIndex = 0;
            battle.log = `${battle.playerCreature.name} fainted! Choose a replacement.`;
            return;
          }
          endBattle({ outcome: "defeat" });
          return;
        }
        battle.phase = "menu";
        battle.log   = `What will ${battle.playerCreature.name} do?`;
      }
      return;
    }

    if (battle.phase === "fight") {
      const nMoves = battle.playerCreature.moves.length;
      const fRow   = Math.floor(battle.selectedIndex / 2);
      const fCol   = battle.selectedIndex % 2;
      if (input.wasPressed("arrowleft", "a")) {
        if (fCol > 0) { battle.selectedIndex--; audio.playSfx("ui_move"); }
      } else if (input.wasPressed("arrowright", "d")) {
        if (fCol < 1 && battle.selectedIndex + 1 < nMoves) { battle.selectedIndex++; audio.playSfx("ui_move"); }
      } else if (input.wasPressed("arrowup", "w")) {
        if (fRow > 0) { battle.selectedIndex -= 2; audio.playSfx("ui_move"); }
      } else if (input.wasPressed("arrowdown", "s")) {
        if (battle.selectedIndex + 2 < nMoves) { battle.selectedIndex += 2; audio.playSfx("ui_move"); }
      } else if (input.wasPressed("e", " ", "enter")) {
        battle.showMoveInfo = false;
        audio.playSfx("menu_confirm");
        audio.playSfx("battle_attack");
        const playerMove = battle.playerCreature.moves[battle.selectedIndex];
        const enemyMove  = battle.enemyCreature.moves[
          Math.floor(Math.random() * battle.enemyCreature.moves.length)
        ];
        const prevPlayerHp = battle.playerCreature.hp;
        const prevEnemyHp  = battle.enemyCreature.hp;

        const logs = performTurn(
          battle.playerCreature,
          battle.enemyCreature,
          playerMove,
          enemyMove,
        );
        battle.log = logs.join(" ");

        this._hpAnim.enemy  = { from: prevEnemyHp,  to: battle.enemyCreature.hp,
          max: battle.enemyCreature.maxHp,  current: prevEnemyHp };
        this._hpAnim.player = { from: prevPlayerHp, to: battle.playerCreature.hp,
          max: battle.playerCreature.maxHp, current: prevPlayerHp };

        if (battle.enemyCreature.hp < prevEnemyHp) {
          this._flashTimer = 120; this._flashEnemy = true;
          audio.playSfx("battle_hit");
          if (battle.log.includes("Super effective!")) {
            setTimeout(() => audio.playSfx("battle_super_effective"), 100);
          }
        } else if (battle.playerCreature.hp < prevPlayerHp) {
          this._flashTimer = 120; this._flashEnemy = false;
          audio.playSfx("battle_hit");
        }
        battle.phase = "message";
      } else if (input.wasPressed("escape", "backspace")) {
        audio.playSfx("menu_back");
        battle.showMoveInfo = false;
        battle.phase = "menu";
        battle.selectedIndex = 0;
        battle.log = `What will ${battle.playerCreature.name} do?`;
      }
      return;
    }

    if (battle.phase === "bag") {
      if (input.wasPressed("escape", "backspace")) {
        audio.playSfx("menu_back");
        battle.phase = "menu";
        battle.selectedIndex = 0;
        battle.log = `What will ${battle.playerCreature.name} do?`;
        return;
      }
      if (input.wasPressed("arrowup", "w")) {
        battle.bagIndex = Math.max(0, (battle.bagIndex ?? 0) - 1);
        audio.playSfx("ui_move");
        return;
      }
      if (input.wasPressed("arrowdown", "s")) {
        battle.bagIndex = Math.min(BAG_ITEMS.length - 1, (battle.bagIndex ?? 0) + 1);
        audio.playSfx("ui_move");
        return;
      }
      if (input.wasPressed("e", " ", "enter")) {
        audio.playSfx("menu_confirm");
        const item = BAG_ITEMS[battle.bagIndex ?? 0];
        switch (item.id) {
          case "capsule":       this._startCatch(battle, state, endBattle, "capsule"); break;
          case "great_capsule": this._startCatch(battle, state, endBattle, "great_capsule"); break;
          case "potion":        this._healPlayer(battle, state, "potion",       20); break;
          case "super_potion":  this._healPlayer(battle, state, "super_potion", 50); break;
          case "antidote":      this._cureStatus(battle, state, "antidote",      "poison",   "Antidote"); break;
          case "burnHeal":      this._cureStatus(battle, state, "burnHeal",      "burn",     "Burn Heal"); break;
          case "awakening":     this._cureStatus(battle, state, "awakening",     "sleep",    "Awakening"); break;
          case "paralyzeHeal":  this._cureStatus(battle, state, "paralyzeHeal",  "paralyse", "Paralyz Heal"); break;
          case "iceHeal":       this._cureStatus(battle, state, "iceHeal",       "freeze",   "Ice Heal"); break;
        }
      }
      return;
    }

    if (battle.phase === "party" || battle.phase === "force_switch") {
      const forced = battle.phase === "force_switch";
      const curIdx = battle.partyIndex ?? 0;

      if (!forced && input.wasPressed("escape", "backspace")) {
        audio.playSfx("menu_back");
        battle.phase = "menu";
        battle.selectedIndex = 0;
        battle.log = `What will ${battle.playerCreature.name} do?`;
        return;
      }

      const validIndices = state.party
        .map((c, i) => ({ c, i }))
        .filter(({ c, i }) => i !== curIdx && c.hp > 0)
        .map(({ i }) => i);

      if (validIndices.length === 0) {
        if (forced) { endBattle({ outcome: "defeat" }); }
        else { battle.phase = "menu"; }
        return;
      }

      const maxSel = validIndices.length - 1;
      battle.forceSwitchIndex = Math.min(battle.forceSwitchIndex ?? 0, maxSel);

      if (input.wasPressed("arrowup", "w")) {
        battle.forceSwitchIndex = Math.max(0, battle.forceSwitchIndex - 1);
        audio.playSfx("ui_move");
      } else if (input.wasPressed("arrowdown", "s")) {
        battle.forceSwitchIndex = Math.min(maxSel, battle.forceSwitchIndex + 1);
        audio.playSfx("ui_move");
      } else if (input.wasPressed("e", " ", "enter")) {
        audio.playSfx("menu_confirm");
        const newIdx = validIndices[battle.forceSwitchIndex];
        if (!forced && state.party[curIdx]) {
          state.party[curIdx].hp          = battle.playerCreature.hp;
          state.party[curIdx].status      = battle.playerCreature.status;
          state.party[curIdx].statusTurns = battle.playerCreature.statusTurns ?? 0;
          state.party[curIdx].moves       = structuredClone(battle.playerCreature.moves);
        }
        battle.partyIndex        = newIdx;
        battle.playerCreature    = structuredClone(state.party[newIdx]);
        battle.forceSwitchIndex  = 0;
        this._hpAnim.player = {
          from: battle.playerCreature.maxHp, to: battle.playerCreature.hp,
          max:  battle.playerCreature.maxHp, current: battle.playerCreature.maxHp,
        };
        battle.phase = "message";
        battle.log   = `Go, ${battle.playerCreature.name}!`;
      }
      return;
    }

    // menu phase
    if (input.wasPressed("arrowup", "w", "arrowleft", "a")) {
      battle.selectedIndex =
        (battle.selectedIndex + battle.menu.length - 1) % battle.menu.length;
      audio.playSfx("ui_move");
    } else if (input.wasPressed("arrowdown", "s", "arrowright", "d")) {
      battle.selectedIndex = (battle.selectedIndex + 1) % battle.menu.length;
      audio.playSfx("ui_move");
    } else if (input.wasPressed("e", " ", "enter")) {
      audio.playSfx("menu_confirm");
      const choice = battle.menu[battle.selectedIndex];
      if (choice === "RUN") {
        if (battle.type === "trainer") {
          battle.log   = "You can't run from a trainer battle!";
          battle.phase = "message";
          return;
        }
        battle.runAttempts = (battle.runAttempts ?? 0) + 1;
        const player = battle.playerCreature;
        const enemy  = battle.enemyCreature;
        const result = attemptRun(player.speed ?? player.spd ?? 10, enemy.speed ?? enemy.spd ?? 10, battle.runAttempts);
        if (result.success) {
          audio.playSfx("menu_back");
          endBattle({ outcome: "fled" });
        } else {
          this._enemyCounterAttack(battle, "Can't escape!");
        }
        return;
      }
      if (choice === "BAG")      { battle.phase = "bag";   battle.bagIndex = 0; return; }
      if (choice === "CREATURE") { battle.phase = "party"; return; }
      battle.phase = "fight";
      battle.selectedIndex = 0;
      battle.showMoveInfo  = false;
      battle.log = "Choose a move.";
    }
  }

  // ─── Wobble animation ────────────────────────────────────────────────────

  _tickWobble(delta) {
    const w = this._wobble;
    if (!w) { return; }
    const WOBBLE_MS = 500;
    w.timer += delta;
    if (w.timer >= WOBBLE_MS) {
      w.timer -= WOBBLE_MS;
      w.remaining -= 1;
      if (w.remaining > 0) {
        audio.playSfx("battle_capture_pulse");
      }
      if (w.remaining <= 0) {
        this._wobble = null;
        w.onResolve(w.caught);
      }
    }
  }

  _tickHpAnim(battle, delta) {
    if (this._flashTimer > 0) {
      this._flashTimer = Math.max(0, this._flashTimer - delta);
    }
    const SPEED = 0.06;
    for (const who of ["enemy", "player"]) {
      const a = this._hpAnim[who];
      if (!a) { continue; }
      const diff = a.to - a.current;
      if (Math.abs(diff) < 0.5) {
        a.current = a.to;
        this._hpAnim[who] = null;
      } else {
        a.current += diff * SPEED * delta;
      }
    }
  }

  _setHpTarget(battle) {
    this._hpAnim.enemy = {
      from: battle.enemyCreature.maxHp,
      to:   battle.enemyCreature.hp,
      max:  battle.enemyCreature.maxHp,
      current: battle.enemyCreature.maxHp,
    };
  }

  // ─── Item uses ────────────────────────────────────────────────────────────

  _startCatch(battle, state, endBattle, capsuleType) {
    if (battle.type === "trainer") {
      battle.log   = "Can't catch a trainer's Morph!";
      battle.phase = "message";
      return;
    }
    const qty = state.items?.[capsuleType] ?? 0;
    if (qty <= 0) {
      battle.log   = `You have no ${capsuleType === "great_capsule" ? "Great Capsules" : "Capsules"}!`;
      battle.phase = "message";
      return;
    }
    state.items[capsuleType] -= 1;
    const result = attemptCatch(battle.enemyCreature, capsuleType);
    audio.playSfx("capture");
    this._wobble = {
      caught:    result.caught,
      remaining: Math.max(1, result.wobbles ?? 1),
      timer:     0,
      onResolve: (caught) => {
        if (caught) {
          audio.playSfx("battle_capture_success");
          endBattle({ outcome: "caught", creature: structuredClone(battle.enemyCreature) });
        } else {
          audio.playSfx("battle_capture_fail");
          this._enemyCounterAttack(battle, `${battle.enemyCreature.name} broke free!`);
        }
      },
    };
  }

  _healPlayer(battle, state, itemId, amount) {
    const qty = state.items?.[itemId] ?? 0;
    const label = BAG_ITEMS.find((b) => b.id === itemId)?.name ?? itemId;
    if (qty <= 0) {
      battle.log   = `You have no ${label}s!`;
      battle.phase = "message";
      return;
    }
    const c = battle.playerCreature;
    if (c.hp >= c.maxHp) {
      battle.log   = `${c.name} is already at full HP!`;
      battle.phase = "message";
      return;
    }
    state.items[itemId] -= 1;
    const healed = Math.min(amount, c.maxHp - c.hp);
    c.hp = Math.min(c.maxHp, c.hp + amount);
    this._hpAnim.player = {
      from: c.hp - healed, to: c.hp, max: c.maxHp, current: c.hp - healed,
    };
    audio.playSfx("heal");
    this._enemyCounterAttack(battle, `Used ${label}! ${c.name} recovered ${healed} HP.`);
  }

  _cureStatus(battle, state, itemId, targetStatus, label) {
    const qty = state.items?.[itemId] ?? 0;
    if (qty <= 0) {
      battle.log   = `You have no ${label}s!`;
      battle.phase = "message";
      return;
    }
    const c = battle.playerCreature;
    if (c.status !== targetStatus) {
      battle.log   = `${c.name} isn't ${targetStatus}d!`;
      battle.phase = "message";
      return;
    }
    state.items[itemId] -= 1;
    c.status      = null;
    c.statusTurns = 0;
    audio.playSfx("heal");
    this._enemyCounterAttack(battle, `Used ${label}! ${c.name} was cured.`);
  }

  _enemyCounterAttack(battle, prefix) {
    const atk  = battle.enemyCreature;
    const def  = battle.playerCreature;
    const move = atk.moves[Math.floor(Math.random() * atk.moves.length)];
    let log    = prefix;
    if (atk.hp > 0 && move) {
      const hit = Math.random() * 100;
      if (hit <= (move.accuracy ?? 100)) {
        if ((move.power ?? 0) > 0) {
          const A    = atk.attack;
          const D    = Math.max(1, def.defense);
          const L    = atk.level;
          const atkTypes = atk.types ?? [atk.type];
          const stab = atkTypes.includes(move.type) ? 1.5 : 1.0;
          const defTypes = def.types ?? [def.type];
          const eff  = getEffectiveness(move.type, defTypes);
          const rand = (217 + Math.floor(Math.random() * 39)) / 255;
          const dmg  = Math.max(1, Math.floor(
            ((((2 * L / 5 + 2) * move.power * A / D) / 50) + 2) * stab * eff * rand,
          ));
          def.hp = Math.max(0, def.hp - dmg);
          log   += ` ${atk.name} used ${move.name}! ${dmg} damage.`;
          if (eff > 1)            { log += " Super effective!"; }
          else if (eff < 1 && eff > 0) { log += " Not very effective."; }
        } else {
          log += ` ${atk.name} used ${move.name}!`;
        }
      } else {
        log += ` ${atk.name} missed!`;
      }
    }
    battle.log   = log;
    battle.phase = "message";
  }

  // ─── Render ───────────────────────────────────────────────────────────────

  render(state) {
    const battle = state.battle;
    if (!battle) { return; }

    const { ctx } = this;
    const W = this.canvas.width;
    const H = this.canvas.height;

    // Background — sky + grass bands
    ctx.fillStyle = "#c8d8f0";
    ctx.fillRect(0, 0, W, Math.floor(H * 0.55));
    ctx.fillStyle = "#88b848";
    ctx.fillRect(0, Math.floor(H * 0.55), W, Math.floor(H * 0.15));
    ctx.fillStyle = "#6a9830";
    ctx.fillRect(0, Math.floor(H * 0.60), W, Math.floor(H * 0.12));

    this.drawPlatform(Math.floor(W * 0.73), Math.floor(H * 0.32), 38, 12);
    this.drawPlatform(Math.floor(W * 0.27), Math.floor(H * 0.55), 44, 14);

    const enemyFlash  = this._flashTimer > 0 && this._flashEnemy;
    const playerFlash = this._flashTimer > 0 && !this._flashEnemy;

    this.drawCreature(Math.floor(W * 0.60), Math.floor(H * 0.08),
      battle.enemyCreature.sprite ?? battle.enemyCreature.speciesId ?? battle.enemyCreature.id,
      true, enemyFlash);
    this.drawCreature(Math.floor(W * 0.10), Math.floor(H * 0.37),
      battle.playerCreature.sprite ?? battle.playerCreature.speciesId ?? battle.playerCreature.id,
      false, playerFlash);

    this.drawStatusBox(6, Math.floor(H * 0.03), battle.enemyCreature,   true);
    this.drawStatusBox(Math.floor(W * 0.50), Math.floor(H * 0.50), battle.playerCreature, false);

    this.drawMenu(battle, state);
  }

  drawPlatform(cx, cy, rx, ry) {
    const { ctx } = this;
    ctx.fillStyle = "#7aaa50";
    ctx.beginPath();
    ctx.ellipse(cx, cy, rx, ry, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = "#5a8a38";
    ctx.beginPath();
    ctx.ellipse(cx, cy + 2, rx - 2, ry - 2, 0, 0, Math.PI * 2);
    ctx.fill();
  }

  drawCreature(x, y, sprite, enemy, flash) {
    const { ctx } = this;
    const palettes = {
      // Starters
      spriglet:  ["#306230", "#6d9f31", "#d7efc2"],
      spriglit:  ["#2f5730", "#78b33b", "#d7efc2"],
      sprighorn: ["#1e4220", "#5a9e2a", "#c4e8a8"],
      cindlet:   ["#5e5e2d", "#b0a53a", "#f4e8a3"],
      chardit:   ["#6f321d", "#dc7a32", "#ffd699"],
      cindrak:   ["#8f2810", "#e06020", "#ffe080"],
      drizzle:   ["#4f4f4f", "#8e8e8e", "#d0d0d0"],
      brinlin:   ["#3c5e79", "#79a8c9", "#d6eef4"],
      maretide:  ["#1a3a56", "#4080a8", "#a0d0e8"],
      // Route 1
      trotter:   ["#905830", "#c89060", "#f4d8a8"],
      trotterion:["#6a3c18", "#a87040", "#e8c888"],
      beakling:  ["#404888", "#7888c8", "#c0ccf0"],
      wingale:   ["#303878", "#5868b8", "#a8b4e8"],
      chittik:   ["#485828", "#788848", "#b8c888"],
      mothwing:  ["#584878", "#9878c8", "#e8d8f8"],
      voltquill: ["#807020", "#d8c020", "#fff880"],
      // Route 2
      pebbling:  ["#604830", "#988060", "#d0b898"],
      stoneback: ["#483820", "#706050", "#a89880"],
      oozelet:   ["#304820", "#508040", "#90c870"],
      venomfang: ["#283818", "#406030", "#70a060"],
      // Gift
      nyxen:     ["#301840", "#604880", "#a888c0"],
      spectrox:  ["#200c30", "#4c2870", "#8860a8"],
      umbravast: ["#180820", "#381858", "#704890"],
      // Legacy
      mothbit:   ["#584878", "#9878c8", "#e8d8f8"],
      pebbloid:  ["#604830", "#988060", "#d0b898"],
      sparkit:   ["#604820", "#c89040", "#ffd880"],
    };
    const [dark, mid, light] = palettes[sprite] ?? palettes.spriglit;

    ctx.save();
    if (enemy) {
      ctx.translate(x + 28, y);
      ctx.scale(-1, 1);
      x = 0; y = 0;
    }

    this.drawSpriteShape(x, y, sprite, dark, mid, light, enemy);

    if (flash) {
      ctx.globalCompositeOperation = "source-atop";
      ctx.fillStyle = "rgba(255,255,255,0.85)";
      ctx.fillRect(x, y, 28, 28);
      ctx.globalCompositeOperation = "source-over";
    }

    ctx.restore();
  }

  drawSpriteShape(x, y, sprite, dark, mid, light, enemy) {
    const { ctx } = this;

    if (sprite === "spriglet" || sprite === "spriglit" || sprite === "sprighorn") {
      ctx.fillStyle = dark;
      ctx.fillRect(x + 8, y + 6, 10, 10);
      ctx.fillRect(x + 6, y + 14, 14, 8);
      ctx.fillStyle = mid;
      ctx.fillRect(x + 4, y + 8, 18, 11);
      ctx.fillRect(x + 2, y + 15, 5, 4);
      ctx.fillRect(x + 21, y + 15, 5, 4);
      ctx.fillStyle = light;
      ctx.fillRect(x + 10, y + 11, 2, 2);
      ctx.fillRect(x + 15, y + 11, 2, 2);
      ctx.fillStyle = "#8bac0f";
      ctx.fillRect(x + 3, y + 3, 5, 5);
      ctx.fillRect(x + 18, y + 3, 5, 5);
      ctx.fillRect(x + (enemy ? 20 : 2), y + 18, 4, 4);
    } else if (sprite === "cindlet" || sprite === "chardit" || sprite === "cindrak") {
      ctx.fillStyle = dark;
      ctx.fillRect(x + 8, y + 5, 10, 10);
      ctx.fillRect(x + 6, y + 14, 14, 8);
      ctx.fillStyle = mid;
      ctx.fillRect(x + 4, y + 8, 18, 11);
      ctx.fillRect(x + 2, y + 10, 5, 5);
      ctx.fillRect(x + 21, y + 10, 5, 5);
      ctx.fillStyle = light;
      ctx.fillRect(x + 10, y + 10, 2, 2);
      ctx.fillRect(x + 15, y + 10, 2, 2);
      ctx.fillStyle = "#f4e8a3";
      ctx.fillRect(x + 4,  y + 3, 4, 5);
      ctx.fillRect(x + 20, y + 3, 4, 5);
      ctx.fillRect(x + (enemy ? 1 : 24), y + 8, 4, 7);
    } else if (sprite === "drizzle" || sprite === "brinlin" || sprite === "maretide") {
      ctx.fillStyle = dark;
      ctx.fillRect(x + 6, y + 8, 14, 10);
      ctx.fillRect(x + 4, y + 16, 18, 6);
      ctx.fillStyle = mid;
      ctx.fillRect(x + 4, y + 10, 18, 9);
      ctx.fillRect(x + 2, y + 16, 22, 6);
      ctx.fillStyle = light;
      ctx.fillRect(x + 9, y + 13, 2, 2);
      ctx.fillRect(x + 15, y + 13, 2, 2);
      ctx.fillRect(x + 8, y + 6, 10, 3);
      ctx.fillStyle = "#d7efc2";
      ctx.fillRect(x + (enemy ? 19 : 1), y + 10, 5, 3);
    } else if (sprite === "trotter" || sprite === "trotterion") {
      // Plain runner — stocky quadruped body
      ctx.fillStyle = dark;
      ctx.fillRect(x + 6, y + 10, 16, 10);
      ctx.fillRect(x + 10, y + 6, 8, 6);
      ctx.fillStyle = mid;
      ctx.fillRect(x + 7, y + 11, 13, 7);
      ctx.fillRect(x + 11, y + 7, 6, 5);
      ctx.fillStyle = light;
      ctx.fillRect(x + 12, y + 9, 2, 2);
      ctx.fillRect(x + 16, y + 9, 2, 2);
      // legs
      ctx.fillStyle = dark;
      ctx.fillRect(x + 7, y + 20, 3, 6);
      ctx.fillRect(x + 11, y + 20, 3, 5);
      ctx.fillRect(x + 16, y + 20, 3, 5);
      ctx.fillRect(x + 20, y + 20, 3, 6);
    } else if (sprite === "beakling" || sprite === "wingale") {
      // Wing — bird silhouette
      ctx.fillStyle = dark;
      ctx.fillRect(x + 9, y + 8, 8, 8);
      ctx.fillRect(x + 7, y + 14, 12, 6);
      ctx.fillStyle = mid;
      ctx.fillRect(x + 10, y + 9, 6, 6);
      ctx.fillRect(x + 8, y + 15, 10, 4);
      ctx.fillStyle = light;
      ctx.fillRect(x + 11, y + 11, 2, 2);
      ctx.fillRect(x + 15, y + 11, 2, 2);
      // wings spread
      ctx.fillStyle = mid;
      ctx.fillRect(x + 1, y + 6, 8, 10);
      ctx.fillRect(x + 19, y + 6, 8, 10);
      ctx.fillStyle = dark;
      ctx.fillRect(x + 1, y + 6, 3, 8);
      ctx.fillRect(x + 24, y + 6, 3, 8);
      // beak
      ctx.fillStyle = "#d8a020";
      ctx.fillRect(x + 11, y + 14, 4, 3);
    } else if (sprite === "chittik") {
      // Bug — small rounded body
      ctx.fillStyle = dark;
      ctx.fillRect(x + 9, y + 10, 10, 8);
      ctx.fillRect(x + 8, y + 16, 12, 5);
      ctx.fillStyle = mid;
      ctx.fillRect(x + 10, y + 11, 8, 6);
      ctx.fillStyle = light;
      ctx.fillRect(x + 11, y + 13, 2, 2);
      ctx.fillRect(x + 15, y + 13, 2, 2);
      // antennae
      ctx.fillStyle = dark;
      ctx.fillRect(x + 10, y + 5, 2, 5);
      ctx.fillRect(x + 16, y + 5, 2, 5);
      ctx.fillRect(x + 8,  y + 4, 4, 2);
      ctx.fillRect(x + 16, y + 4, 4, 2);
      // legs
      ctx.fillRect(x + 6, y + 16, 4, 2);
      ctx.fillRect(x + 18, y + 16, 4, 2);
    } else if (sprite === "mothwing" || sprite === "mothbit") {
      ctx.fillStyle = dark;
      ctx.fillRect(x + 9, y + 8, 8, 8);
      ctx.fillRect(x + 7, y + 14, 12, 6);
      ctx.fillStyle = mid;
      ctx.fillRect(x + 6, y + 6, 14, 14);
      ctx.fillStyle = light;
      ctx.fillRect(x + 10, y + 11, 2, 2);
      ctx.fillRect(x + 14, y + 11, 2, 2);
      ctx.fillStyle = mid;
      ctx.fillRect(x + 1, y + 4, 7, 10);
      ctx.fillRect(x + 18, y + 4, 7, 10);
      ctx.fillStyle = light;
      ctx.fillRect(x + 2, y + 5, 4, 6);
      ctx.fillRect(x + 20, y + 5, 4, 6);
    } else if (sprite === "voltquill") {
      // Static hedgehog — spiky back
      ctx.fillStyle = dark;
      ctx.fillRect(x + 8, y + 10, 12, 9);
      ctx.fillRect(x + 10, y + 7, 8, 5);
      ctx.fillStyle = mid;
      ctx.fillRect(x + 9, y + 11, 10, 7);
      ctx.fillRect(x + 11, y + 8, 6, 4);
      ctx.fillStyle = light;
      ctx.fillRect(x + 11, y + 13, 2, 2);
      ctx.fillRect(x + 15, y + 13, 2, 2);
      // spikes
      ctx.fillStyle = "#fff080";
      ctx.fillRect(x + 10, y + 2, 3, 6);
      ctx.fillRect(x + 15, y + 2, 3, 6);
      ctx.fillRect(x + 6, y + 7, 3, 5);
      ctx.fillRect(x + 19, y + 7, 3, 5);
      ctx.fillRect(x + 12, y + 1, 4, 5);
    } else if (sprite === "pebbling" || sprite === "stoneback" || sprite === "pebbloid") {
      ctx.fillStyle = dark;
      ctx.fillRect(x + 5, y + 8, 16, 12);
      ctx.fillRect(x + 8, y + 5, 10, 5);
      ctx.fillStyle = mid;
      ctx.fillRect(x + 6, y + 10, 14, 9);
      ctx.fillRect(x + 9, y + 6, 8, 5);
      ctx.fillStyle = light;
      ctx.fillRect(x + 10, y + 12, 2, 2);
      ctx.fillRect(x + 14, y + 12, 2, 2);
      ctx.fillStyle = "#a09080";
      ctx.fillRect(x + 7, y + 8, 3, 3);
      ctx.fillRect(x + 16, y + 10, 3, 3);
    } else if (sprite === "oozelet" || sprite === "venomfang") {
      // Toxin — amorphous blob
      ctx.fillStyle = dark;
      ctx.fillRect(x + 7, y + 10, 14, 10);
      ctx.fillRect(x + 5, y + 14, 18, 6);
      ctx.fillStyle = mid;
      ctx.fillRect(x + 8, y + 11, 12, 8);
      ctx.fillRect(x + 6, y + 15, 16, 4);
      ctx.fillStyle = light;
      ctx.fillRect(x + 10, y + 13, 2, 2);
      ctx.fillRect(x + 15, y + 13, 2, 2);
      // drips
      ctx.fillStyle = dark;
      ctx.fillRect(x + 8, y + 20, 2, 4);
      ctx.fillRect(x + 14, y + 20, 2, 3);
      ctx.fillRect(x + 20, y + 19, 2, 3);
    } else if (sprite === "nyxen" || sprite === "spectrox" || sprite === "umbravast") {
      // Umbra — ghostly wisp
      ctx.fillStyle = dark;
      ctx.fillRect(x + 8, y + 7, 10, 12);
      ctx.fillRect(x + 6, y + 12, 14, 8);
      ctx.fillStyle = mid;
      ctx.fillRect(x + 9, y + 8, 8, 10);
      ctx.fillRect(x + 7, y + 13, 12, 6);
      ctx.fillStyle = light;
      ctx.fillRect(x + 11, y + 11, 2, 3);
      ctx.fillRect(x + 15, y + 11, 2, 3);
      // wispy tails
      ctx.fillStyle = dark;
      ctx.fillRect(x + 8,  y + 20, 3, 4);
      ctx.fillRect(x + 13, y + 21, 3, 3);
      ctx.fillRect(x + 18, y + 20, 3, 4);
    } else if (sprite === "sparkit") {
      ctx.fillStyle = dark;
      ctx.fillRect(x + 8, y + 8, 10, 10);
      ctx.fillRect(x + 6, y + 14, 14, 7);
      ctx.fillStyle = mid;
      ctx.fillRect(x + 5, y + 9, 16, 10);
      ctx.fillStyle = light;
      ctx.fillRect(x + 10, y + 12, 2, 2);
      ctx.fillRect(x + 14, y + 12, 2, 2);
      ctx.fillStyle = "#fff080";
      ctx.fillRect(x + 12, y + 2, 4, 6);
      ctx.fillRect(x + 10, y + 6, 8, 4);
      ctx.fillRect(x + 13, y + 10, 4, 3);
    } else {
      // Fallback
      ctx.fillStyle = dark;
      ctx.fillRect(x + 6, y + 8, 14, 12);
      ctx.fillStyle = mid;
      ctx.fillRect(x + 5, y + 10, 16, 9);
      ctx.fillStyle = light;
      ctx.fillRect(x + 10, y + 13, 2, 2);
      ctx.fillRect(x + 15, y + 13, 2, 2);
    }
  }

  drawStatusBox(x, y, creature, enemy) {
    const { ctx } = this;
    const W = 80, H = enemy ? 30 : 42;

    ctx.fillStyle = "#0f380f";
    ctx.fillRect(x, y, W, H);
    ctx.fillStyle = "#fff";
    ctx.fillRect(x + 1, y + 1, W - 2, H - 2);
    ctx.fillStyle = "#0f380f";
    ctx.fillRect(x + 2, y + 2, W - 2, H - 2);
    ctx.fillStyle = "#d7efc2";
    ctx.fillRect(x + 2, y + 2, W - 4, H - 4);

    ctx.fillStyle = "#0f380f";
    ctx.font = "bold 7px 'Courier New', monospace";
    ctx.textBaseline = "top";
    ctx.fillText(creature.name, x + 5, y + 4);
    ctx.font = "7px 'Courier New', monospace";
    ctx.fillText(`Lv${creature.level}`, x + W - 22, y + 4);

    if (creature.status) {
      ctx.fillStyle = STATUS_COLOURS[creature.status] ?? "#888";
      ctx.fillRect(x + W - 30, y + 13, 24, 8);
      ctx.fillStyle = "#fff";
      ctx.font = "6px 'Courier New', monospace";
      ctx.fillText(STATUS_LABELS[creature.status] ?? "???", x + W - 28, y + 14);
    }

    const barX = x + 5;
    const barY = y + 20;
    const barW = W - 10;
    const barH = 6;

    let displayHp;
    const who = enemy ? "enemy" : "player";
    if (this._hpAnim[who]) {
      displayHp = this._hpAnim[who].current;
    } else {
      displayHp = creature.hp;
    }
    const hpRatio = Math.max(0, displayHp) / creature.maxHp;

    ctx.fillStyle = "#0f380f";
    ctx.fillRect(barX, barY, barW, barH);
    ctx.fillStyle =
      hpRatio > 0.5 ? "#306230" :
      hpRatio > 0.2 ? "#9c7a3c" : "#7f3326";
    ctx.fillRect(barX + 1, barY + 1, Math.max(1, Math.floor((barW - 2) * hpRatio)), barH - 2);

    if (!enemy) {
      ctx.fillStyle = "#0f380f";
      ctx.font = "7px 'Courier New', monospace";
      ctx.textBaseline = "top";
      ctx.fillText(`${Math.ceil(displayHp)} / ${creature.maxHp}`, Math.round(x + 5), Math.round(y + 30));
    }
  }

  drawMenu(battle, state) {
    if (battle.phase === "bag")                                     { this.drawBag(battle, state); return; }
    if (battle.phase === "party" || battle.phase === "force_switch") { this.drawParty(battle, state); return; }

    const { ctx } = this;
    const W  = this.canvas.width;
    const H  = this.canvas.height;
    const by = Math.floor(H * 0.72);
    const bh = H - by;

    ctx.fillStyle = "#0f380f";
    ctx.fillRect(0, by, W, bh);
    ctx.fillStyle = "#fff";
    ctx.fillRect(1, by + 1, W - 2, bh - 2);
    ctx.fillStyle = "#0f380f";
    ctx.fillRect(2, by + 2, W - 2, bh - 2);
    ctx.fillStyle = "#d7efc2";
    ctx.fillRect(2, by + 2, W - 4, bh - 4);

    ctx.fillStyle = "#0f380f";
    ctx.font = "7px 'Courier New', monospace";

    // Wobble animation display.
    if (this._wobble) {
      const wobbled = (this._wobble.remaining < (this._wobble.totalWobbles ?? this._wobble.remaining + 1));
      ctx.fillText("The Capsule is shaking...", 8, by + 14);
      const dots = ".".repeat(4 - this._wobble.remaining);
      ctx.fillText(dots, 8, by + 26);
      return;
    }

    if (battle.phase === "fight") {
      this.drawFightGrid(battle, by, bh, W);
      return;
    }

    // Message / menu phase.
    const lines = _wrapText(battle.log, Math.floor((W - 84) / 6));
    lines.slice(0, 3).forEach((line, i) => {
      ctx.fillStyle = "#0f380f";
      ctx.fillText(line, 8, by + 12 + i * 11);
    });

    if (battle.phase === "menu") {
      ctx.fillStyle = "#0f380f";
      ctx.fillRect(W - 78, by + 4, 74, bh - 8);
      ctx.fillStyle = "#fff";
      ctx.fillRect(W - 77, by + 5, 72, bh - 10);
      ctx.fillStyle = "#0f380f";
      ctx.fillRect(W - 76, by + 6, 72, bh - 10);
      ctx.fillStyle = "#d7efc2";
      ctx.fillRect(W - 76, by + 6, 70, bh - 12);

      battle.menu.forEach((item, i) => {
        const marker = battle.selectedIndex === i ? "▶" : " ";
        const mx = i < 2 ? W - 72 : W - 36;
        const my = by + 16 + (i % 2) * 14;
        ctx.fillStyle = "#0f380f";
        ctx.font = "7px 'Courier New', monospace";
        ctx.fillText(`${marker}${item}`, mx, my);
      });
    } else {
      ctx.fillStyle = "#0f380f";
      ctx.font = "7px 'Courier New', monospace";
      ctx.fillText("▼", W - 14, by + bh - 8);
    }
  }

  drawFightGrid(battle, by, bh, W) {
    const { ctx } = this;
    const COL_W      = Math.floor(W / 2);
    const GRID_H     = Math.floor(bh * 0.66);
    const ROW_H      = Math.floor(GRID_H / 2);
    const INFO_Y     = by + GRID_H;
    const INFO_H     = bh - GRID_H;
    const enemyTypes = battle.enemyCreature.types ?? [battle.enemyCreature.type];
    const moves      = battle.playerCreature.moves;

    // ── 2×2 move grid ────────────────────────────────────────────────────────
    for (let i = 0; i < 4; i++) {
      const move = moves[i] ?? null;
      const col  = i % 2;
      const row  = Math.floor(i / 2);
      const cx   = col * COL_W;
      const cy   = by + row * ROW_H;
      const sel  = battle.selectedIndex === i;

      if (sel && move) {
        ctx.fillStyle = "rgba(15,56,15,0.18)";
        ctx.fillRect(cx + 2, cy + 2, COL_W - 4, ROW_H - 4);
      }

      if (!move) {
        ctx.fillStyle = "rgba(15,56,15,0.30)";
        ctx.font = "8px 'Courier New', monospace";
        ctx.textBaseline = "top";
        ctx.textAlign = "center";
        ctx.fillText("—", Math.round(cx + COL_W / 2), Math.round(cy + ROW_H / 2) - 4);
        ctx.textAlign = "left";
        continue;
      }

      // Line 1: cursor + move name
      ctx.fillStyle = "#0f380f";
      ctx.font = sel ? "bold 8px 'Courier New', monospace" : "8px 'Courier New', monospace";
      ctx.textBaseline = "top";
      ctx.fillText(`${sel ? "▶" : " "} ${move.name}`, Math.round(cx + 4), Math.round(cy + 4));

      // Effectiveness tag — right-aligned on line 1
      if ((move.power ?? 0) > 0) {
        const eff = getEffectiveness(move.type, enemyTypes);
        let effStr = "", effColor = "";
        if (eff >= 2)       { effStr = "[SE]"; effColor = "#1a7010"; }
        else if (eff === 0) { effStr = "[IM]"; effColor = "#556655"; }
        else if (eff < 1)   { effStr = "[NE]"; effColor = "#b85000"; }
        if (effStr) {
          ctx.font = "7px 'Courier New', monospace";
          ctx.fillStyle = effColor;
          const tw = ctx.measureText(effStr).width;
          ctx.fillText(effStr, Math.round(cx + COL_W - tw - 4), Math.round(cy + 5));
        }
      }

      // Line 2: type as coloured plain text + PP right-aligned
      const typeColor = MOVE_TYPE_BG[move.type] ?? "#3a5050";
      ctx.fillStyle = typeColor;
      ctx.font = "8px 'Courier New', monospace";
      ctx.fillText(move.type, Math.round(cx + 14), Math.round(cy + 14));

      const ppStr = `PP ${move.pp ?? "?"}/${move.maxPp ?? move.pp ?? "?"}`;
      ctx.fillStyle = "rgba(15,56,15,0.70)";
      const ppW = ctx.measureText(ppStr).width;
      ctx.fillText(ppStr, Math.round(cx + COL_W - ppW - 4), Math.round(cy + 14));
    }

    // Grid dividers
    if (moves.length > 2) {
      ctx.fillStyle = "rgba(15,56,15,0.30)";
      ctx.fillRect(2, by + ROW_H, W - 4, 1);
    }
    ctx.fillStyle = "rgba(15,56,15,0.30)";
    ctx.fillRect(COL_W, by + 2, 1, GRID_H - 4);

    // ── Persistent info strip ─────────────────────────────────────────────────
    ctx.fillStyle = "rgba(15,56,15,0.12)";
    ctx.fillRect(2, INFO_Y, W - 4, INFO_H - 1);

    const selMove = moves[battle.selectedIndex];
    if (selMove) {
      ctx.fillStyle = "#0f380f";
      ctx.font = "7px 'Courier New', monospace";
      ctx.textBaseline = "top";
      const infoLine = `${selMove.name}  ·  ${selMove.type}  ·  Pow ${selMove.power ?? "—"}  ·  Acc ${selMove.accuracy ?? "—"}`;
      ctx.fillText(infoLine, Math.round(6), Math.round(INFO_Y + 4));

      let matchups;
      try { matchups = getTypeMatchups(selMove.type); } catch { matchups = { strong: [], weak: [] }; }
      const parts = [];
      if (matchups.strong?.length > 0) { parts.push(`Strong: ${matchups.strong.slice(0, 3).join(", ")}`); }
      if (matchups.weak?.length   > 0) { parts.push(`Weak: ${matchups.weak.slice(0, 3).join(", ")}`); }
      if (parts.length > 0) {
        ctx.fillStyle = "rgba(15,56,15,0.70)";
        ctx.fillText(parts.join("  "), Math.round(6), Math.round(INFO_Y + 13));
      }
    }

    // Footer
    ctx.fillStyle = "rgba(15,56,15,0.55)";
    ctx.font = "7px 'Courier New', monospace";
    ctx.fillText("[E] Attack    [Esc] Back", Math.round(8), Math.round(by + bh - 6));
  }

  drawMoveInfo(battle, by, bh, W) {
    const { ctx } = this;
    const move = battle.playerCreature.moves[battle.selectedIndex];
    if (!move) { return; }

    ctx.fillStyle = "#0f380f";
    ctx.font = "bold 7px 'Courier New', monospace";
    ctx.fillText(`${move.name} [${move.type}]`, 8, by + 12);

    ctx.font = "7px 'Courier New', monospace";
    ctx.fillText(`Pow:${move.power ?? "—"} Acc:${move.accuracy ?? "—"} PP:${move.pp ?? "—"}`, 8, by + 22);

    const descLines = _wrapText(move.description ?? "", Math.floor((W - 20) / 6));
    descLines.slice(0, 2).forEach((ln, i) => {
      ctx.fillText(ln, 8, by + 32 + i * 10);
    });

    let matchups;
    try { matchups = getTypeMatchups(move.type); } catch { matchups = { strong: [], weak: [] }; }
    if (matchups.strong.length > 0) {
      ctx.fillText(`Hits: ${matchups.strong.slice(0, 4).join(",")}`, 8, by + bh - 18);
    }
    if (matchups.weak.length > 0) {
      ctx.fillText(`Weak: ${matchups.weak.slice(0, 4).join(",")}`, 8, by + bh - 8);
    }
    ctx.fillStyle = "rgba(15,56,15,0.6)";
    ctx.fillText("[Shift] back", W - 78, by + 12);
  }

  drawBag(battle, state) {
    const { ctx } = this;
    const W  = this.canvas.width;
    const H  = this.canvas.height;
    const by = Math.floor(H * 0.72);
    const bh = H - by;

    ctx.fillStyle = "#0f380f";
    ctx.fillRect(0, by, W, bh);
    ctx.fillStyle = "#d7efc2";
    ctx.fillRect(2, by + 2, W - 4, bh - 4);

    ctx.fillStyle = "#0f380f";
    ctx.font = "bold 7px 'Courier New', monospace";
    ctx.textBaseline = "top";
    ctx.fillText("BAG", 6, by + 4);
    ctx.font = "7px 'Courier New', monospace";
    ctx.fillText("[Esc] back", W - 70, by + 4);

    const visStart = Math.max(0, (battle.bagIndex ?? 0) - 3);
    const visible  = BAG_ITEMS.slice(visStart, visStart + 5);
    visible.forEach((item, vi) => {
      const realIdx = visStart + vi;
      const qty     = state.items?.[item.id] ?? 0;
      const marker  = (battle.bagIndex ?? 0) === realIdx ? "▶" : " ";
      ctx.fillStyle = "#0f380f";
      ctx.fillText(`${marker} ${item.name}  x${qty}`, 6, by + 16 + vi * 11);
    });
  }

  drawParty(battle, state) {
    const { ctx } = this;
    const W  = this.canvas.width;
    const H  = this.canvas.height;
    const by = Math.floor(H * 0.72);
    const bh = H - by;
    const forced = battle.phase === "force_switch";
    const curIdx = battle.partyIndex ?? 0;

    ctx.fillStyle = "#0f380f";
    ctx.fillRect(0, by, W, bh);
    ctx.fillStyle = "#d7efc2";
    ctx.fillRect(2, by + 2, W - 4, bh - 4);

    ctx.fillStyle = "#0f380f";
    ctx.font = "bold 7px 'Courier New', monospace";
    ctx.textBaseline = "top";
    ctx.fillText(forced ? "CHOOSE REPLACEMENT" : "PARTY", 6, by + 4);
    if (!forced) {
      ctx.font = "7px 'Courier New', monospace";
      ctx.fillText("[Esc] back", W - 70, by + 4);
    }

    // Build valid switch targets (for cursor tracking).
    const validIndices = state.party
      .map((c, i) => ({ c, i }))
      .filter(({ c, i }) => i !== curIdx && c.hp > 0)
      .map(({ i }) => i);
    const selPartyIdx = validIndices[battle.forceSwitchIndex ?? 0] ?? -1;

    state.party.slice(0, 6).forEach((creature, i) => {
      const display   = i === curIdx ? battle.playerCreature : creature;
      if (!display) { return; }
      const fainted   = display.hp <= 0;
      const isCur     = i === curIdx;
      const isSel     = i === selPartyIdx;
      const hpRatio   = fainted ? 0 : display.hp / display.maxHp;
      const statusLbl = display.status ? ` [${STATUS_LABELS[display.status] ?? "?"}]` : "";
      const row       = i < 4 ? i : i; // up to 6 shown 2 per row if needed; keep linear for now

      const ry = by + 16 + i * 12;
      if (ry + 12 > by + bh - 2) { return; }

      // Selection cursor
      if (isSel) {
        ctx.fillStyle = "#306230";
        ctx.fillRect(2, ry - 1, W - 4, 11);
      }
      ctx.fillStyle = fainted ? "#7f3326" : isCur ? "#9c7a3c" : "#0f380f";
      ctx.font = "7px 'Courier New', monospace";
      const prefix = isSel ? "▶ " : isCur ? "· " : "  ";
      ctx.fillText(`${prefix}${display.name} Lv${display.level}${statusLbl}`, 6, ry);
      if (!fainted) {
        ctx.fillStyle = "#0f380f";
        ctx.fillRect(110, ry - 1, 44, 6);
        ctx.fillStyle = hpRatio > 0.5 ? "#306230" : hpRatio > 0.2 ? "#9c7a3c" : "#7f3326";
        ctx.fillRect(111, ry,     Math.max(1, Math.floor(42 * hpRatio)), 4);
        ctx.fillStyle = "#0f380f";
        ctx.fillText(`${Math.ceil(display.hp)}/${display.maxHp}`, W - 38, ry);
      } else {
        ctx.fillStyle = "#7f3326";
        ctx.fillText("FAINTED", W - 48, ry);
      }
    });
  }
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function _xpRewardFor(creature, isTrainer = false) {
  return xpYield({
    baseExp:    creature.baseXpYield ?? creature.baseExp ?? 40,
    foeLevel:   creature.level,
    isTrainer,
    ownerCount: 1,
  });
}

function _wrapText(text, width) {
  if (!text) { return []; }
  const words = text.split(" ");
  const lines = [];
  let current = "";
  for (const word of words) {
    const candidate = current ? `${current} ${word}` : word;
    if (candidate.length > width) {
      if (current) { lines.push(current); }
      current = word;
    } else {
      current = candidate;
    }
  }
  if (current) { lines.push(current); }
  return lines;
}
