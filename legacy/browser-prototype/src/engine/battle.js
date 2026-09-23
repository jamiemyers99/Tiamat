// Battle engine — Gen-1 damage formula, status conditions, catch, run.
// Exports: computeDamage, performTurn, applyStatusTick, attemptCatch, attemptRun
import { getEffectiveness } from "../data/typeChart.js?v=20260429-15";
import { SPECIES } from "../data/creatures.js?v=20260429-15";

// Gen-1 crit chance: attacker base speed / 512.
function critChance(creature) {
  const baseSpd = SPECIES[creature.speciesId ?? creature.id]?.baseStats?.spd ?? 45;
  return Math.min(baseSpd / 512, 0.5);
}

// Gen-1 damage formula.
export function computeDamage(attacker, move, defender) {
  // Status: sleeping attackers can't act.
  if (attacker.status === "sleep") {
    attacker.statusTurns = (attacker.statusTurns ?? 1) - 1;
    if (attacker.statusTurns <= 0) {
      attacker.status = null;
      attacker.statusTurns = 0;
      return { hit: false, damage: 0, effectiveness: 1, slept: true, woke: true };
    }
    return { hit: false, damage: 0, effectiveness: 1, slept: true, woke: false };
  }

  // Frozen attackers can't act (10% thaw chance per turn).
  if (attacker.status === "freeze") {
    if (Math.random() < 0.10) {
      attacker.status = null;
      return { hit: false, damage: 0, effectiveness: 1, frozenThawed: true };
    }
    return { hit: false, damage: 0, effectiveness: 1, frozen: true };
  }

  // Paralysed attackers have 25% chance to be fully immobilised.
  if (attacker.status === "paralyse") {
    if (Math.random() < 0.25) {
      return { hit: false, damage: 0, effectiveness: 1, paralysed: true };
    }
  }

  // Status moves (power 0, effect handles everything).
  if (move.power === 0 && move.category === "status") {
    return handleStatusMove(attacker, move, defender);
  }

  // Heal Bud — special: heals user.
  if (move.effect?.kind === "heal") {
    const fraction = move.effect.fraction ?? 0.5;
    const healed   = Math.floor(attacker.maxHp * fraction);
    attacker.hp    = Math.min(attacker.maxHp, attacker.hp + healed);
    return { hit: true, damage: 0, effectiveness: 1, healed };
  }

  // Accuracy roll.
  if (move.accuracy && move.accuracy < 100) {
    if (Math.random() * 100 > move.accuracy) {
      return { hit: false, damage: 0, effectiveness: 1 };
    }
  }

  // Type effectiveness — supports dual-type defenders.
  const defTypes     = Array.isArray(defender.types) ? defender.types : [defender.type ?? "Plain"];
  const effectiveness = getEffectiveness(move.type, defTypes);

  // Immune — no damage.
  if (effectiveness === 0) {
    return { hit: true, damage: 0, effectiveness: 0, immune: true };
  }

  // Gen-1 damage formula.
  const isCrit = Math.random() < critChance(attacker);
  const L      = isCrit ? attacker.level * 2 : attacker.level;
  const A      = attacker.status === "burn" ? Math.floor(attacker.attack * 0.5) : attacker.attack;
  const D      = defender.defense;

  const attackTypes = Array.isArray(attacker.types) ? attacker.types : [attacker.type ?? "Plain"];
  const stab        = attackTypes.includes(move.type) ? 1.5 : 1.0;
  const rand        = (217 + Math.floor(Math.random() * 39)) / 255;

  const base   = Math.floor(
    (((2 * L / 5 + 2) * Math.max(1, move.power) * (A / Math.max(1, D))) / 50 + 2) * stab * effectiveness * rand,
  );
  const damage = Math.max(1, base);

  return { hit: true, damage, effectiveness, isCrit };
}

function handleStatusMove(attacker, move, defender) {
  if (!move.effect) { return { hit: true, damage: 0, effectiveness: 1 }; }
  const eff = move.effect;
  if (eff.kind === "confuse") {
    if (!defender.confused) {
      defender.confused = true;
      defender.confuseTurns = 1 + Math.floor(Math.random() * 4);
    }
    return { hit: true, damage: 0, effectiveness: 1, inflicted: "confuse" };
  }
  if (eff.kind === "sleep") {
    if (!defender.status && Math.random() < (eff.chance ?? 1)) {
      defender.status      = "sleep";
      defender.statusTurns = 1 + Math.floor(Math.random() * 3);
    }
    return { hit: true, damage: 0, effectiveness: 1, inflicted: "sleep" };
  }
  return { hit: true, damage: 0, effectiveness: 1 };
}

function tryInflictStatus(attacker, defender, move) {
  if (!move.effect || !move.effect.kind || move.effect.kind === "heal") { return null; }
  const kind = move.effect.kind;
  if (["priority", "multi_hit", "two_turn", "high_crit", "def_down", "atk_up_self"].includes(kind)) { return null; }
  if (kind === "confuse") {
    if (!defender.confused && Math.random() < (move.effect.chance ?? 1)) {
      defender.confused     = true;
      defender.confuseTurns = 1 + Math.floor(Math.random() * 4);
      return "confuse";
    }
    return null;
  }
  if (kind === "flinch") {
    if (Math.random() < (move.effect.chance ?? 0.3)) {
      defender._flinched = true;
    }
    return null;
  }
  if (defender.status) { return null; } // already has a status
  if (Math.random() < (move.effect.chance ?? 0)) {
    defender.status = kind;
    if (kind === "sleep") {
      defender.statusTurns = 1 + Math.floor(Math.random() * 3);
    }
    return kind;
  }
  return null;
}

export function applyStatusTick(creature) {
  const messages = [];
  if (creature.status === "burn" || creature.status === "poison") {
    const dmg = Math.max(1, Math.floor(creature.maxHp / 16));
    creature.hp = Math.max(0, creature.hp - dmg);
    const label = creature.status === "burn" ? "burned" : "poisoned";
    messages.push(`${creature.name} is ${label}! −${dmg} HP.`);
  }
  return messages;
}

export function performTurn(playerCreature, enemyCreature, playerMove, enemyMove) {
  const pSpd = playerCreature.status === "paralyse"
    ? Math.floor(playerCreature.speed * 0.5) : playerCreature.speed;
  const eSpd = enemyCreature.status === "paralyse"
    ? Math.floor(enemyCreature.speed * 0.5)  : enemyCreature.speed;

  // Priority moves go first.
  const pPrio = playerMove.effect?.kind === "priority" ? 1 : 0;
  const ePrio = enemyMove.effect?.kind   === "priority" ? 1 : 0;

  const order = (pPrio > ePrio || (pPrio === ePrio && pSpd >= eSpd))
    ? [
        { attacker: playerCreature, defender: enemyCreature, move: playerMove  },
        { attacker: enemyCreature,  defender: playerCreature, move: enemyMove   },
      ]
    : [
        { attacker: enemyCreature,  defender: playerCreature, move: enemyMove   },
        { attacker: playerCreature, defender: enemyCreature,  move: playerMove  },
      ];

  const log = [];

  for (const step of order) {
    if (step.attacker.hp <= 0 || step.defender.hp <= 0) { continue; }

    // Flinch check.
    if (step.attacker._flinched) {
      step.attacker._flinched = false;
      log.push(`${step.attacker.name} flinched and couldn't move!`);
      continue;
    }

    // Confusion self-hit.
    if (step.attacker.confused) {
      step.attacker.confuseTurns = (step.attacker.confuseTurns ?? 1) - 1;
      if (step.attacker.confuseTurns <= 0) {
        step.attacker.confused = false;
        log.push(`${step.attacker.name} snapped out of confusion!`);
      } else if (Math.random() < 0.33) {
        const selfDmg = Math.max(1, Math.floor(
          (((2 * step.attacker.level / 5 + 2) * 40 * step.attacker.attack) / (50 * Math.max(1, step.attacker.defense))) + 2,
        ));
        step.attacker.hp = Math.max(0, step.attacker.hp - selfDmg);
        log.push(`${step.attacker.name} is confused and hurt itself! −${selfDmg} HP.`);
        continue;
      }
    }

    const outcome = computeDamage(step.attacker, step.move, step.defender);

    if (outcome.frozen)       { log.push(`${step.attacker.name} is frozen solid!`);          continue; }
    if (outcome.frozenThawed) { log.push(`${step.attacker.name} thawed out!`);                continue; }
    if (outcome.paralysed)    { log.push(`${step.attacker.name} is paralysed and can't move!`); continue; }
    if (outcome.slept) {
      log.push(outcome.woke ? `${step.attacker.name} woke up!` : `${step.attacker.name} is fast asleep.`);
      continue;
    }
    if (outcome.healed !== undefined) {
      log.push(`${step.attacker.name} used ${step.move.name} and restored ${outcome.healed} HP!`);
      continue;
    }
    if (outcome.inflicted) {
      const labels = { confuse: "became confused", sleep: "fell asleep" };
      log.push(`${step.attacker.name} used ${step.move.name}! ${step.defender.name} ${labels[outcome.inflicted] ?? "was affected"}!`);
      continue;
    }
    if (!outcome.hit) {
      log.push(`${step.attacker.name} used ${step.move.name}, but missed!`);
      continue;
    }
    if (outcome.immune) {
      log.push(`${step.attacker.name} used ${step.move.name}. It has no effect on ${step.defender.name}!`);
      continue;
    }

    step.defender.hp = Math.max(0, step.defender.hp - outcome.damage);
    let msg = `${step.attacker.name} used ${step.move.name}!`;
    if (outcome.isCrit)           { msg += " Critical hit!"; }
    msg += ` −${outcome.damage} HP.`;
    if (outcome.effectiveness > 1) { msg += " Super effective!"; }
    else if (outcome.effectiveness < 1 && outcome.effectiveness > 0) { msg += " Not very effective."; }

    const inflicted = tryInflictStatus(step.attacker, step.defender, step.move);
    if (inflicted === "burn")     { msg += ` ${step.defender.name} was burned!`;     }
    if (inflicted === "poison")   { msg += ` ${step.defender.name} was poisoned!`;   }
    if (inflicted === "sleep")    { msg += ` ${step.defender.name} fell asleep!`;    }
    if (inflicted === "paralyse") { msg += ` ${step.defender.name} was paralysed!`;  }
    if (inflicted === "freeze")   { msg += ` ${step.defender.name} was frozen!`;     }
    if (inflicted === "confuse")  { msg += ` ${step.defender.name} became confused!`;}

    log.push(msg);
  }

  // End-of-turn status damage.
  [playerCreature, enemyCreature].forEach((c) => { log.push(...applyStatusTick(c)); });

  return log;
}

// Gen-1 catch formula (simplified).
// capsuleType: 'capsule' | 'great_capsule'
export function attemptCatch(target, capsuleType = "capsule") {
  const catchRate = target.catchRate ?? 100;
  const ballMod   = capsuleType === "great_capsule" ? 8 : 12;

  // Sleep/freeze bonus: instant catch roll first.
  if (target.status === "sleep" || target.status === "freeze") {
    if (Math.random() * 256 < 25) { return { caught: true, wobbles: 3 }; }
  }

  // Species catch rate check.
  const r = Math.floor(Math.random() * (capsuleType === "great_capsule" ? 200 : 255));
  if (r > catchRate) {
    return { caught: false, wobbles: 1 };
  }

  // HP-based formula.
  const f = Math.min(255, Math.floor((target.maxHp * 255 * 4) / (target.hp * ballMod)));
  if (Math.random() * 255 < f) {
    return { caught: true, wobbles: 3 };
  }

  // Wobble count based on how close we were.
  const wobbles = f > 170 ? 3 : f > 85 ? 2 : 1;
  return { caught: false, wobbles };
}

// Gen-1 run formula.
// runAttempts: how many times the player has tried to run this battle (incremented by caller).
export function attemptRun(playerSpeed, enemySpeed, runAttempts) {
  const odds = Math.floor((playerSpeed * 32) / Math.max(1, (Math.floor(enemySpeed / 4)) % 256)) + 30 * runAttempts;
  return Math.random() * 256 < odds;
}
