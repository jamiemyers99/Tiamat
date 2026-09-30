// Act IV — The Riven: Frostspire, Rimepass, Riftgate, the Sunken Chapel, the Cradle and the Crown.
import { rivalBattle, bossBattle, adeptsCleared, trialWon } from './common.js';
import { audio } from '../core/audio.js';
import { SPECIES } from '../data/species.js';
import { CROWN_ORDER } from '../data/trainers.js';

function starter(S) { return S.var('starter', 'spriglet'); }

async function tiamatBattle(S) {
  const r = await S.wild('tiamat', 50, { noRun: true, noWhiteout: true, legend: true, music: 'battle_legend', bg: 'rift' });
  if (r === 'caught') {
    S.set('tiamat_caught');
    await S.say(null, 'The Covenant Capsule glows, warm as a hearth. Inside, Tiamat is finally, peacefully still.');
    return true;
  }
  if (r === 'win') {
    S.set('tiamat_calmed');
    await S.say(null, 'Tiamat sinks back beneath the black water. The rage has gone out of her.|She is sleeping again — truly sleeping, for the first time in a thousand years.');
    return true;
  }
  await S.say(null, "Tiamat's fury is too much! A wave hurls you back up the Rift...");
  await S.whiteout();
  return false;
}

export default {
  // ── Frostspire ─────────────────────────────────────────────────────────
  'frostspire.seal': async (S) => {
    await S.say(null, 'The Rime Seal is rimed with frost that never melts. Somebody has tied a woolly scarf around it.');
  },
  'frostspire.eastguide': async (S) => {
    await S.say('Guide', "Rimepass is deadly without a guide's blessing. Warden Hale gives hers with the Rime Sigil — not before.");
  },
  'frostspire.eastgate': async (S) => {
    await S.block('Guide', "Hold it! Nobody crosses Rimepass without the Rime Sigil. Warden Hale's orders — and the mountain's.");
  },
  'frostspire.climber': async (S) => {
    if (!S.flag('climber_gift')) {
      await S.say('Climber', "You made it across Glasslake? Tough kid. Here — I found this growing on a ledge near the summit.");
      await S.give('growth_fruit');
      await S.say('Climber', 'A Growth Fruit. Feed it to a Morph and it grows a whole level. Rare as anything.');
      S.set('climber_gift');
      return;
    }
    await S.say('Climber', 'From the top of the pass you can see the Riven. Like the world got split with an axe.');
  },
  'frostspire.girl': async (S) => {
    await S.say('Girl', "Did you know? If you stand very still at night, you can feel the ground breathe. Mum says it's my imagination.");
  },
  'frostspire_trial.warden': async (S) => {
    if (S.flag('sigil_rime')) {
      await S.say('Hale', "Riftgate's down the pass. Seren's the last Warden — and the best. Don't let her rattle you.");
      return;
    }
    if (!(await adeptsCleared(S, 'Hale'))) { return; }
    await S.say('Hale', "You crossed Glasslake to get here? Good. The mountain respects effort. So do I. Now — climb!");
    const r = await S.battle('hale');
    if (r !== 'win') { return; }
    S.sigil('rime'); S.set('sigil_rime');
    S.jingle('jingle_sigil');
    await S.say(null, '{PLAYER} received the Rime Sigil from Warden Hale!');
    await trialWon(S);
    await S.give('td05');
    await S.say('Hale', "TD05, Rime Ray. You've got five Sigils now. Five! Most Tamers stop at three and settle down.");
    await S.say('Hale', "...Morrow sent a bird. She thinks you're being used. I think you should go to Riftgate anyway — but go carefully.");
  },

  // ── Riftgate ───────────────────────────────────────────────────────────
  'riftgate.seal': async (S) => {
    await S.say(null, 'The Wyrm Seal stands at the centre of the plaza, ringed by glowing crystals. It is cracked down the middle.');
    if (S.flag('cradle_done')) { await S.say(null, 'The crack has closed. The stone is warm, and quiet.'); }
  },
  'riftgate.spireguard': async (S) => {
    await S.say('Spire Guard', 'Only Wardens may climb to the Crown of the Spire. Those are the rules.');
  },
  'riftgate.chapelguard': async (S) => {
    await S.say('Guard', "The old chapel's been locked since the Deepcall moved in. They say it goes all the way down into the Riven.");
  },
  'riftgate.oldwarden': async (S) => {
    await S.say('Old Warden', "I kept the Wyrm Seal before Seren. Forty years. Every one of them I wondered what would happen if one Tamer earned all six.");
    if (S.state.sigils.length >= 6) { await S.say('Old Warden', "...And now I suppose we'll find out."); }
  },
  'riftgate_trial.warden': async (S) => {
    if (S.flag('sigil_wyrm')) {
      await S.say('Seren', S.flag('cradle_done') ? 'The Reach owes you everything, {PLAYER}.' : 'Go. The chapel. I will hold the Seal.');
      return;
    }
    if (!(await adeptsCleared(S, 'Seren'))) { return; }
    await S.say('Seren', "Five Sigils. You have walked the whole Reach to stand here. I will not go easy on you, {PLAYER}.");
    const r = await S.battle('seren');
    if (r !== 'win') { return; }
    S.sigil('wyrm'); S.set('sigil_wyrm');
    S.jingle('jingle_sigil');
    await S.say(null, '{PLAYER} received the Wyrm Sigil from Warden Seren!');
    await trialWon(S);
    await S.give('td16');
    await S.say('Seren', 'Six Sigils. The first Tamer in a hundred years to hold them all.|...I should be proud. Why do I feel afraid?');
  },
  // Safety net: if the player somehow leaves the Trial without seeing Oriel, the scene plays on return.
  'map:riftgate': async (S, ctx) => {
    if (!S.flag('sigil_wyrm') || S.flag('oriel_reveal') || ctx.first) { return; }
    const p = S.state.player;
    if (p.map !== 'riftgate') { return; }
    S.w.player.warp(23, 10, 'down');
    p.x = 23; p.y = 10;
    await S.run('riftgate.oriel');
    S.set('oriel_reveal');
  },
  'riftgate.oriel': async (S) => {
    S.face('player', 'down');
    await S.shake(500, 0.006);
    await S.say(null, 'The ground lurches. In the plaza below, the Wyrm Seal splits with a sound like thunder.');
    S.show('rg_oriel', 21, 12, 'up');
    S.show('rg_acolyte_a', 20, 13, 'up');
    S.show('rg_acolyte_b', 22, 13, 'up');
    S.music('deepcall');
    await S.say('???', 'Six Sigils. Six Seals. And one Tamer carrying all of them.');
    await S.move('player', 'd1');
    await S.say('Oriel', "I am Oriel, Hierophant of the Deepcall. And you, {PLAYER}, are the answer to a thousand years of prayer.");
    await S.say('Oriel', "The Seals open only for one who holds all six keys. The Wardens knew it. That is why they scattered the Sigils.");
    await S.say('Oriel', "Then they forgot why. They made it a GAME. Earn a Sigil, win a prize. And you played so very well.");
    await S.say('Oriel', "The moment you set foot in the Cradle, the last door opens — and the Mother wakes. Come when you are ready. We will be waiting.");
    S.show('rg_wren', 20, 22, 'up');
    await S.say('Wren', '{PLAYER}! DON\'T LISTEN TO THEM!');
    await S.move('rg_wren', 'u5', 120);
    await S.say('Wren', "Maren lied — no, Maren believed it, but ORIEL lied! They don't want to free Tiamat. They want to control her. Drown the Reach and rule what's left!");
    await S.say('Oriel', 'Such a bright child. Take them to the Chapel.');
    // the acolytes march Wren off after Oriel
    await Promise.all(['rg_oriel', 'rg_acolyte_a', 'rg_acolyte_b', 'rg_wren'].map((id) => S.leave(id, { ms: 140 })));
    await S.fadeOut(300);
    S.show('rg_seren', 22, 12, 'up');
    await S.fadeIn(300);
    await S.say(null, "They're gone — and they've taken Wren.");
    await S.move('rg_seren', 'u1');
    S.face('rg_seren', 'player');
    S.face('player', 'left');
    await S.say('Seren', "{PLAYER}! I saw everything. They've gone down into the Sunken Chapel — it opens onto the Rift itself.");
    await S.say('Seren', 'I confiscated this key from the Deepcall years ago. Take it.');
    await S.give('rift_key');
    await S.say('Seren', 'And this. The six Seal-stones share one heart — the Wardens forged a single capsule from it, long ago, in case the worst ever happened.');
    await S.give('covenant_capsule');
    await S.say('Seren', "The Covenant Capsule. If Tiamat wakes, it is the only thing that can hold her. Go. Bring Wren home. I'll gather the Wardens.");
    await S.leave('rg_seren');
    S.music('riftgate');
  },

  // ── Sunken Chapel ─────────────────────────────────────────────────────
  'chapel.vesk': async (S) => {
    await S.say('Vesk', "YOU. The brat from the mines. The Hierophant says I'm not to hurt you. The Hierophant isn't here.");
    const r = await bossBattle(S, 'vesk2');
    if (r !== 'win') { return; }
    await S.say('Vesk', "...Go on, then. Go see the Mother. You'll wish you hadn't.");
    await S.leave('sc_vesk');
    S.set('vesk2_done');
  },
  'chapel.maren': async (S) => {
    await S.say('Maren', "Wren trusted me. I told them the truth — as I understood it. Maybe I was wrong. Show me.");
    const r = await bossBattle(S, 'maren2');
    if (r !== 'win') { return; }
    await S.say('Maren', "...I was wrong. Oriel never wanted to free her. I see that now.|Wren is by the altar. Take them and go. I'll... find my own way out.");
    await S.leave('sc_maren', { ms: 170 });
    S.set('maren2_done');
  },
  'chapel.wren': async (S) => {
    if (!S.flag('maren2_done')) {
      await S.say('Wren', "{PLAYER}! You came! Watch out — Maren's guarding me, and she's stronger than she looks!");
      return;
    }
    await S.say('Wren', "{PLAYER}! You actually came for me. Even after... everything.");
    await S.say('Wren', "Here — let me patch up your team. It's the least I can do.");
    await S.havenHeal();
    await S.say('Wren', "Oriel went down the stairs behind the altar. Down into the Rift. They're going to wake Tiamat right now.");
    await S.say('Wren', "I'm going to get Grandma and the Wardens. You go. And {PLAYER}... be careful. Please.");
    await S.leave('sc_wren', { ms: 125 });
    S.set('wren_freed');
  },

  // ── The Cradle ─────────────────────────────────────────────────────────
  'cradle.oriel': async (S) => {
    if (S.flag('oriel_beaten')) { return; }
    S.face('player', 'up');
    await S.say('Oriel', 'You came. Of course you came. You are the key, {PLAYER}, and a key always finds its lock.');
    await S.shake(600, 0.008);
    await S.say('Oriel', 'Feel that? The last Seal fell the moment you stepped through the door. She is waking.');
    await S.say('Oriel', "All that is left is to make sure no one interferes. Thank you for everything — and goodbye.");
    const r = await bossBattle(S, 'oriel');
    if (r !== 'win') { return; }
    S.set('oriel_beaten');
    await S.say('Oriel', "It... does not matter. Listen. LISTEN!");
    await S.shake(900, 0.012);
    await S.flash(300);
    await S.say(null, 'The black water behind the altar begins to churn.');
    const img = S.spriteAt('mons', 'tiamat_f', 9.5, 6, { depth: 6100, alpha: 0 });
    audio.cry(SPECIES.tiamat.num);
    await S.tweenP({ targets: img, alpha: 1, y: img.y - 10, duration: 1400, ease: 'Sine.easeOut' });
    await S.say('Oriel', 'Mother! I have freed you! Now — the Reach is yours, and I am your voice—');
    await S.shake(500, 0.015);
    await S.say(null, "Tiamat roars. The sound shakes dust from the Cradle's roof — and Oriel is thrown across the chamber.");
    await S.leave('cr_oriel', { ms: 320 });
    await S.say(null, "Oriel crawls away into the dark. Tiamat's eyes turn to you.|In your bag, the Covenant Capsule is glowing.");
    img.destroy();
    const done = await tiamatBattle(S);
    if (done) { await finale(S); }
  },
  'cradle.tiamat': async (S) => {
    if (!S.flag('oriel_beaten')) { await S.say(null, 'An ancient altar of black stone, carved with waves. The water behind it is utterly still.'); return; }
    if (!S.flag('cradle_done')) {
      await S.say(null, 'The black water heaves. Tiamat rises again, roaring!');
      const done = await tiamatBattle(S);
      if (done) { await finale(S); }
      return;
    }
    if (S.flag('tiamat_calmed') && !S.flag('tiamat_caught')) {
      await S.say(null, 'Deep beneath the water, the Draco Queen turns in her sleep. Tiamat stirs as you draw near...');
      if (await S.ask(null, 'Wake Tiamat?')) { await tiamatBattle(S); }
      return;
    }
    await S.say(null, 'The Cradle is quiet now. The water is clear enough to see stars reflected in it — though there is no sky down here.');
  },

  // ── The Warden's Crown ─────────────────────────────────────────────────
  'map:spire_crown': async (S) => {
    // like a Pokémon League: walk out of the Crown and the Challenge starts again from the first Warden
    if (S.flag('game_clear')) { S.setVar('crown_round', 0); }
    if (!S.flag('cradle_done') || S.flag('crown_scene')) { return; }
    S.set('crown_scene');
    await S.wait(300);
    S.face('player', 'up');
    await S.say('Seren', '{PLAYER}. Come in. Everyone is here.');
    await S.say('Mossa', "Look at you, dear. You've grown roots and branches both.");
    await S.say('Brann', 'Ha! Salt in your blood, I said it from the start!');
    await S.say('Iskra', "I've already started drafting new Seals. Better ones. With alarms.");
    await S.say('Morrow', 'And so the story ends differently than anyone wrote it.');
    await S.say('Hale', 'Summited. The biggest mountain in the Reach, and you summited it.');
    await S.say('Seren', "The old Covenant is broken, {PLAYER}. The Wardens agreed — the Reach needs a new one. Not a jailer. A friend.|We'd like it to be you.");
    await S.say('Wren', "...Before the speeches get any longer.");
    await S.move('crown_wren', 'd6');
    await S.say('Wren', "No cults. No Seals. No grandmas watching. Just you and me — as equals. One last battle, {PLAYER}?");
    await rivalBattle(S, `rival4_${starter(S)}`);
    await S.say('Wren', "...Yeah. That was the best battle of my life. Thanks, {PLAYER}. For all of it.");
    await S.say('Wren', "Race you home?");
    S.set('game_clear');
    await S.fadeOut(700);
    await S.credits();
    S.setHealPoint('home_1f', 4, 7);
    await S.heal({ silent: true });
    S.lockSurf(false);
    await S.warp('home_2f', 5, 4, 'down', 50);
    await S.say(null, 'Some time later...|{PLAYER} woke up in their own bed, to birdsong and the smell of toast.');
    await S.say(null, "The Reach is still out there — Morphs to catch, Tamers to battle, and a very large sea-dragon who might like a visitor. Your journey continues!");
  },
  'crown.warden': async (S, ctx) => {
    const id = ctx.npc ? ctx.npc.id.replace('crown_', '') : '';
    const name = cap(id);
    const lines = {
      mossa: "Come and visit my garden, dear. It's quieter now. The stone still sings, but it's a happier song.",
      brann: "Fancy a sail? The Riven's safe to sail now. Imagine that!",
      iskra: 'Version two of the Seals will have an off switch. Obviously.',
      morrow: "I'll write your story down in the Archive. The true version. Mostly.",
      hale: "When you want a real climb, come find me. I know a peak nobody's named yet.",
      seren: 'The Spire is open to you whenever you want it, Covenant.',
    };
    if (!S.flag('game_clear')) { await S.say(name, lines[id] || '...'); return; }
    const round = S.var('crown_round', 0);
    if (round >= CROWN_ORDER.length) { await S.say(name, 'Six Wardens down. Only Wren is left, {PLAYER} — go on!'); return; }
    const next = CROWN_ORDER[round];
    if (id !== next) {
      if (round === 0) {
        await S.say(name, lines[id] || '...');
        await S.say(name, S.flag('crown_champion')
          ? "Back for another Crown Challenge, Champion? Mossa goes first, as always."
          : "If you want a real test, {PLAYER}, speak to Mossa. The Crown Challenge starts with her.");
      } else {
        await S.say(name, `Patience! It's ${cap(next)}'s turn. Round ${round + 1} of the Crown Challenge.`);
      }
      return;
    }
    if (round === 0) {
      if (!S.flag('crown_explained')) {
        await S.say('Mossa', "Now then, dear. The Wardens have been talking. You beat each of us once, one at a time, with weeks to train in between.|The Crown Challenge is different. All six Wardens at full strength, one after another. Then Wren, who has been training every single day.");
        await S.say('Mossa', "There's no Haven up here, so bring plenty of medicine. If you lose, or walk out of the Crown, you start again with me.|Win all seven, and you're the Champion of the Warden's Crown. Seren has something for whoever manages it.");
        S.set('crown_explained');
      }
      if (!(await S.ask('Mossa', 'Take the Crown Challenge?', 'Bring it on', 'Not yet'))) { await S.say('Mossa', "Take your time. We're not going anywhere."); return; }
    }
    await crownRun(S);
  },
  'crown.wren': async (S) => {
    if (!S.flag('game_clear')) { await S.say('Wren', "Grandma cried. Don't tell her I told you. Want a rematch sometime? I'll be training."); return; }
    const round = S.var('crown_round', 0);
    if (round < CROWN_ORDER.length) {
      await S.say('Wren', round === 0
        ? (S.flag('crown_champion')
          ? "Champion! I've been training. Beat all six Wardens again and I'll be right here for the last round."
          : "I'm the last round of the Crown Challenge. Beat all six Wardens first — start with Mossa. I'll be right here.")
        : `${6 - round} Warden${6 - round === 1 ? '' : 's'} to go. Don't keep me waiting!`);
      return;
    }
    await crownFinal(S);
  },
};

const cap = (id) => id.charAt(0).toUpperCase() + id.slice(1);

// Face the Wardens in order. After each win you can carry straight on, or stop to use items and talk to the next
// Warden when you're ready. A loss (or leaving the Crown) sends you back to round one.
async function crownRun(S) {
  for (;;) {
    const round = S.var('crown_round', 0);
    const id = CROWN_ORDER[round];
    S.face(`crown_${id}`, 'player');
    const r = await S.battle(`elite_${id}`, { noWhiteout: true, boss: true });
    if (r !== 'win') { await crownLost(S); return; }
    S.setVar('crown_round', round + 1);
    if (round + 1 >= CROWN_ORDER.length) {
      await S.say('Seren', 'All six Wardens. Only one challenger remains, {PLAYER}.');
      if (await S.ask(null, 'Face Wren for the final round?', 'Yes', 'Not yet')) { await crownFinal(S); }
      else { await S.say(null, 'Talk to Wren when you are ready. (Leaving the Crown restarts the Challenge.)'); }
      return;
    }
    const next = cap(CROWN_ORDER[round + 1]);
    if (!(await S.ask(null, `Round ${round + 2} of 7: face ${next} now?`, 'Yes', 'Not yet'))) {
      await S.say(null, `Talk to ${next} when you are ready. (Leaving the Crown restarts the Challenge.)`);
      return;
    }
  }
}

async function crownLost(S) {
  S.setVar('crown_round', 0);
  await S.whiteout();
}

async function crownFinal(S) {
  S.face('crown_wren', 'player');
  await S.say('Wren', S.flag('crown_champion')
    ? "The Champion, back again! This time I've got you. I can feel it!"
    : "Seven rounds. Six Wardens. And me. I've waited a long time for this, {PLAYER}.");
  const r = await S.battle(`elite_wren_${starter(S)}`, { noWhiteout: true, boss: true });
  if (r !== 'win') { await crownLost(S); return; }
  S.setVar('crown_round', 0);
  S.setVar('crown_wins', S.var('crown_wins', 0) + 1);
  await S.heal();
  if (S.flag('crown_champion')) {
    await S.say('Seren', 'Champion of the Warden\'s Crown, again. The Reach is in good hands, {PLAYER}.');
    return;
  }
  S.set('crown_champion');
  await S.say('Seren', "Seven battles without a Haven. It has not been done since the first Covenant.|{PLAYER}, you are the Champion of the Warden's Crown.");
  await S.say('Seren', 'When the first Covenant built the Spire, they left a gem on this crown for the Tamer who could stand where you stand now. Take it.');
  await S.give('crown_gem');
  await S.say('Seren', "The old records say it is a key. Under your own village, Rootmere, there is a door of carved stone that nobody has opened in a thousand years.|It was sealed by the same hands that sealed Tiamat. I think it is time someone found out why.");
  await S.say('Wren', "The weird old door behind the village? We used to dare each other to knock on it! ...Go on then, Champion. Tell me what's inside.");
}

async function finale(S) {
  S.set('cradle_done');
  await S.fadeOut(600);
  await S.say(null, 'Footsteps echo down the Rift — Wren, Dr. Marsh, and all six Wardens.|Together, they lead you up out of the dark...');
  await S.warp('spire_crown', 8, 11, 'up', 400);
}
