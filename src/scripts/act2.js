// Act II — Salt and Iron: Thornwild, Saltreach, the Coldforge Mines and Gearhollow.
import { rivalBattle, bossBattle } from './common.js';

function starter(S) { return S.var('starter', 'spriglet'); }

export default {
  // ── Thornwild ───────────────────────────────────────────────────────────
  'thornwild.shrine': async (S) => {
    await S.say(null, 'A weathered statue of a coiled sea-serpent, green with age. An old inscription reads:|"SHE SLEEPS SO THAT WE MAY WAKE."');
    if (S.flag('wren2_done')) { await S.say(null, 'The earth around its base has been dug up recently. Someone was looking for something underneath.'); }
  },
  'thornwild.pip': async (S) => {
    if (S.flag('pip_found')) { await S.say(null, "It's a berry bush. Pip seems to have eaten most of the berries."); return; }
    if (!S.flag('pip_asked')) { await S.say(null, 'Something small rustles in the berry bush... then goes very still. Whatever it is, it is shy.'); return; }
    await S.say(null, 'Something rustles in the berry bush... *jingle jingle*');
    await S.say(null, 'A Burrlet with a little bell on a ribbon peeks out! It must be Pip!|Pip hops straight into your arms, trembling.');
    await S.give('pips_bell');
    S.set('pip_found');
    await S.say(null, "Better get Pip home to Posy in Brindlewood.");
  },
  'thornwild.acolytes_block': async (S) => {
    await S.say('Deepcall Acolyte', 'Oi! Nobody leaves the forest while the dig is on. Turn around!');
    await S.stepBack();
  },
  'thornwild.wren': async (S) => {
    const p = S.state.player;
    S.show('tw_wren', p.x, 38, 'up');
    await S.say('???', '{PLAYER}! Hey, {PLAYER}!');
    await S.move('tw_wren', `u${Math.max(0, 38 - p.y - 1)}`, 150);
    S.face('player', 'down');
    await S.say('Wren', "Did you see those robed weirdos? They ran right past me, muttering about 'the Mother' and 'the song under the stone'.");
    await S.say('Wren', "Grandma's notes talk about the Seals, too. Something's going on and I'm going to figure it out before you do.");
    await S.say('Wren', "But first — I've been training. Rematch!");
    await rivalBattle(S, `rival2_${starter(S)}`);
    await S.say('Wren', "Okay. Okay! You're good. I'm heading to Saltreach — Grandma's got an old friend there. Don't follow me!");
    await S.say('Wren', "...Actually the road only goes one way, so I guess you have to. Whatever. See you!");
    await S.move('tw_wren', 'd3', 120);
    S.hide('tw_wren');
  },

  // ── Saltreach ───────────────────────────────────────────────────────────
  'saltreach.seal': async (S) => {
    await S.say(null, 'A barnacled Seal-stone stands at the edge of the square, wet with sea-spray even on dry days.');
    if (S.flag('sigil_tide')) { await S.say(null, 'The Tide Sigil in your bag thrums, like a heartbeat.'); }
  },
  'saltreach.brann_docks': async (S) => {
    if (!S.cond('beat:st_acolyte_1&beat:st_acolyte_2')) {
      await S.say('Old Sailor', "Get those robed barnacles off my pier, would you? I'd do it myself but my knees creak louder than the boards.");
      return;
    }
    await S.say('Old Sailor', "Ha! Look at 'em run! They've been trying to charter my boats all week. For the Riven, they said. Nobody sails to the Riven.");
    await S.say('Brann', "Name's Brann. Captain of Saltreach, keeper of the Tide Seal — and Warden of the Tide Trial.");
    await S.say('Brann', "You've got guts, {PLAYER}. Come find me at the Trial Hall. Let's see if you've got sea-legs to match.");
    S.set('docks_done');
    await S.fadeOut(250); S.hide('st_brann'); await S.fadeIn(250);
  },
  'saltreach.eastguard': async (S) => {
    await S.say('Sailor', "Captain's orders — nobody takes the Gullcliff Road without a Tide Sigil. Rockfalls, robed folk... it's no place for beginners.");
  },
  'saltreach.eastgate': async (S) => {
    await S.block('Sailor', "Whoa there! Captain's orders: the Gullcliff Road is closed to anyone without a Tide Sigil.");
  },
  'saltreach.harbourmaster': async (S) => {
    await S.say('Harbourmaster', "Tide Morphs are the heart of this town. Gullips on every roof, Crabbits under every pier.");
    if (S.flag('sigil_tide')) { await S.say('Harbourmaster', "With the Captain's Skiff you can reach the islet in the bay. I've seen something glinting out there."); }
  },
  'saltreach.netmender': async (S) => {
    await S.say('Net-mender', "My grandmother told me the sea was here first. That the land is just the sea, sleeping.");
    await S.say('Net-mender', "The robed ones say the same thing. Only they say it like it's a promise.");
  },
  'saltreach.lighthouse': async (S) => {
    if (!S.flag('lh_gift')) {
      await S.say('Keeper', "Visitors! I don't get many. The stairs put people off. Here, a little something for climbing them anyway.");
      await S.give('td02');
      await S.say('Keeper', 'TD02 teaches Mend — heals the user. Any Morph can learn it. Handy on a long voyage.');
      S.set('lh_gift');
      return;
    }
    await S.say('Keeper', "On clear nights you can see a glow far to the north-east. The Riven. Sailors say it's the sea breathing.");
  },
  'saltreach_trial.warden': async (S) => {
    if (S.flag('sigil_tide')) {
      await S.say('Brann', "You want to know about the Seals? Six stones, six Wardens, six Sigils. We guard 'em, we test Tamers, we hand out Sigils. Tradition.");
      await S.say('Brann', "Why? Nobody's asked me that in forty years. Iskra in Gearhollow might know — she reads everything.");
      return;
    }
    await S.say('Brann', "Ha! The kid who cleared my pier! The sea tests everyone, {PLAYER}. Let's see if you float!");
    const r = await S.battle('brann');
    if (r !== 'win') { return; }
    S.sigil('tide'); S.set('sigil_tide');
    S.jingle('jingle_sigil');
    await S.say(null, '{PLAYER} received the Tide Sigil from Captain Brann!');
    await S.give('td08');
    await S.say('Brann', "TD08's Tide Pulse. And take this — my old Skiff. Folds up small enough for a pocket.");
    await S.give('skiff');
    await S.say('Brann', "Face open water and press Confirm to launch it. The Gullcliff Road east is open to you now, too. Mind the rockfall.");
  },

  // ── Coldforge Mines ────────────────────────────────────────────────────
  'mines.foreman': async (S) => {
    if (S.flag('vesk1_done')) { await S.say('Foreman', "The robed lot cleared out after you sent their boss packing. Mining's back to normal. Thanks, kid."); return; }
    await S.say('Foreman', "Rockfall's closed the Gullcliff Road, so the only way to Gearhollow is through here. The tunnels go north-east.");
    await S.say('Foreman', "Watch yourself deeper in. Some robed fellows are digging where we never dig. Their boss has a nasty temper.");
  },
  'mines.vesk': async (S) => {
    if (S.flag('vesk1_done')) { return; }
    await S.emote('cf_vesk', '!');
    await S.say('Vesk', "Who let a child down here? DURN! LISSA! ...Useless.");
    await S.say('Vesk', "Do you know what this is, child? Scale-iron. The bones of the Mother. The whole Reach is built on her, and you people MINE her.");
    await S.say('Vesk', "We're taking her home. Now get out of my dig — or I'll bury you with the rest of the rock!");
    const r = await bossBattle(S, 'vesk1');
    if (r !== 'win') { return; }
    await S.say('Vesk', "Tch. Fine! Keep your precious rocks. We've got what we came for anyway.");
    await S.fadeOut(300);
    S.set('vesk1_done');
    S.refresh();
    await S.fadeIn(300);
    await S.say(null, 'Vesk fled — and dropped something in the dust.');
    await S.give('forge_pass');
    await S.say(null, 'A pass for the Gearhollow Ironworks, stamped with a wave. What would the Deepcall want in the Ironworks?');
  },

  // ── Gearhollow ─────────────────────────────────────────────────────────
  'gearhollow.seal': async (S) => {
    await S.say(null, 'The Spark Seal stands in a little fenced yard. Someone has wired a small brass plaque to it:|"DO NOT TOUCH. I MEAN IT. — ISKRA"');
  },
  'gearhollow.northgate': async (S) => {
    await S.block('Engineer', "Sorry! The Moorwind gate is locked down on Warden Iskra's orders. Deepcall trouble. Earn her Sigil and she'll open it for you.");
  },
  'gearhollow.worker': async (S) => {
    if (S.flag('ironworks_done')) { await S.say('Worker', "You ran the Deepcall out of the Ironworks! Drinks are on me. Well — tea. It's the middle of the day."); return; }
    if (S.has('forge_pass')) { await S.say('Worker', "Is that a Forge Pass? Then you can get through the Ironworks gate! Warden Iskra's in there alone with those robed thugs — hurry!"); return; }
    await S.say('Worker', "The Deepcall broke into the Ironworks and locked the gate behind them! Warden Iskra's trapped in there. Only folk with a Forge Pass can get the gate open.");
  },
  'gearhollow.tinker': async (S) => {
    if (!S.flag('tinker_gift')) {
      await S.say('Tinker', "A Tamer! Here, test this for me — I built a capsule that latches on faster. Swift Capsules, I call them.");
      await S.give('swift_capsule', 3);
      S.set('tinker_gift');
      return;
    }
    await S.say('Tinker', "Swift Capsules work best on the very first turn of a battle. After that? Meh. Needs work.");
  },
  'gearhollow.discshop': async (S) => {
    await S.say('Clerk', 'Welcome to the Disc Shop! Every Tech Disc can be used as many times as you like.');
    await S.openScreen('shop', { stock: ['td01', 'td17', 'td12', 'td18', 'td06', 'td08', 'td11'], title: 'Disc Shop' });
  },
  'ironworks.iskra': async (S) => {
    if (!S.cond('beat:iw_acolyte_1&beat:iw_acolyte_2&beat:iw_acolyte_3')) {
      await S.say('Iskra', "Careful! They're after the crane — they want to haul scale-iron all the way to the Riven! Clear them out and I'll do the rest!");
      return;
    }
    await S.say('Iskra', "You cleared them ALL out? On your own? Brilliant. Absolutely brilliant.");
    await S.say('Iskra', "I'm Iskra — chief engineer, Warden of the Spark Seal, and owner of a very dented crane. Thank you, {PLAYER}.");
    await S.say('Iskra', "They were after the scale-iron Vesk dug out of Coldforge. Something about building a 'cradle-song'. I don't like it.");
    await S.say('Iskra', "Right! Come to the Spark Trial. I've been dying for a proper challenger all week.");
    S.set('ironworks_done');
    await S.fadeOut(250); S.refresh(); await S.fadeIn(250);
  },
  'ironworks.worker': async (S) => {
    if (S.flag('ironworks_done')) { await S.say('Engineer', "Look at this mess. It'll take a month to fix the crane. Still — better than it being at the bottom of the Riven."); return; }
    await S.say('Engineer', "I hid behind the boilers when they burst in. Please — help the Warden!");
  },
  'gearhollow_trial.warden': async (S) => {
    if (S.flag('sigil_spark')) {
      await S.say('Iskra', "Why six Seals? I've read every record in the Reach. They all say the same thing: the Sigils are to be earned, never gathered.");
      await S.say('Iskra', "Which is funny, because that's exactly what the Trials make you do. Gather them. Hm. Morrow in Hollowmere knows the old stories.");
      return;
    }
    await S.say('Iskra', "You saved my Ironworks. Now let's see if you can survive my Trial. I tuned everyone up this morning!");
    const r = await S.battle('iskra');
    if (r !== 'win') { return; }
    S.sigil('spark'); S.set('sigil_spark');
    S.jingle('jingle_sigil');
    await S.say(null, '{PLAYER} received the Spark Sigil from Warden Iskra!');
    await S.give('td04');
    await S.say('Iskra', 'TD04 is Thunder Arc. And — oh! — take one of these. I built it for couriers.');
    await S.give('wing_whistle');
    await S.say('Iskra', "The Wing Whistle calls a Skyveer I trained. Open your Reach Map outdoors and it'll fly you to any town you've visited.");
    await S.say('Iskra', "The Moorwind gate north is open for you now. Hollowmere's on the other side of the moor.");
  },
  'gearhollow.wren': async (S) => {
    S.show('gh_wren', 27, 30, 'up');
    await S.say('???', '{PLAYER}.');
    await S.move('gh_wren', 'u4');
    S.face('player', 'down');
    await S.say('Wren', "Three Sigils. You've got three Sigils and I've got... questions.");
    await S.say('Wren', "I read Grandma's notes. The Seals weren't built to protect the towns. They were built to hold something DOWN. Something alive.");
    await S.say('Wren', "Why does nobody talk about that? Why do the Wardens just... hand out Sigils like sweets?|...Battle me. I need to think.");
    await rivalBattle(S, `rival3_${starter(S)}`);
    await S.say('Wren', "...Fine. You win. You always win.");
    await S.say('Wren', "There's someone I want to talk to. Someone who might actually give me answers. Don't wait up.");
    await S.move('gh_wren', 'd4');
    S.hide('gh_wren');
  },
};
