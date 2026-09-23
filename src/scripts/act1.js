// Act I — Roots: Rootmere, the Marsh Lab, Route 1 and Brindlewood.
import { SPECIES } from '../data/species.js';
import { RIVAL_PICK } from '../data/trainers.js';
import { rivalBattle } from './common.js';
import { partnerIvs } from '../data/difficulty.js';

const STARTERS = {
  spriglet: { name: 'Spriglet', type: 'Nature', blurb: 'Spriglet, the Nature Morph. Patient and tough — it drinks sunlight and shrugs off Tide and Stone attacks.' },
  cindlet: { name: 'Cindlet', type: 'Ember', blurb: 'Cindlet, the Ember Morph. A fiery little scrapper that burns through Nature and Frost.' },
  puddlet: { name: 'Puddlet', type: 'Tide', blurb: 'Puddlet, the Tide Morph. Playful and quick — it douses Ember and Stone Morphs.' },
};

export default {
  // ── home ────────────────────────────────────────────────────────────────
  'map:home_2f': async (S) => {
    if (S.flag('woke_up')) { return; }
    S.set('woke_up');
    await S.wait(400);
    await S.say(null, '{PLAYER} woke up to birdsong and the smell of toast.|Today is your naming day — the day every child in Rootmere becomes a Tamer!');
    await S.say(null, 'Tip: arrow keys or WASD to walk, Z / Enter / Space to talk, X to go back, and C, Esc or Tab for the menu. You can change any key in the menu under Controls.');
  },

  // ── Rootmere ────────────────────────────────────────────────────────────
  'map:rootmere': async (S) => {
    if (!S.flag('got_starter') || S.flag('mum_boots')) { return; }
    const p = S.state.player;
    await S.wait(200);
    await S.say('Mum', '{PLAYER}! Yoo-hoo!');
    if (p.x === 24 && p.y === 7) { await S.move('rm_mum', 'u1,r2'); S.face('rm_mum', 'up'); S.face('player', 'down'); }
    else { await S.approach('rm_mum'); }
    await S.say('Mum', "I just saw Wren stomp off in a huff — so you won, did you? Or lost? Either way, you've got your very first Morph!");
    await S.say('Mum', "Oh, I nearly forgot. Your father's old walking boots. He wore them from one end of the Reach to the other.");
    await S.give('trail_boots');
    await S.say('Mum', 'Hold Shift (or B on a pad) to run in them. And come home whenever you need a rest — the kettle is always on.');
    S.set('mum_boots');
    await S.move('rm_mum', 'l3');
    S.hide('rm_mum');
  },
  'rootmere.north': async (S) => {
    await S.say('???', '{PLAYER}! Wait!');
    await S.say(null, "It's Dr. Marsh's assistant, waving from the lab door.");
    await S.say('Aide', "Don't go into the tall grass without a Morph of your own! Dr. Marsh is waiting for you in the lab.");
    await S.stepBack();
  },
  'rootmere.woman': async (S) => {
    if (S.flag('game_clear')) { await S.say(null, "Is it true? You calmed Tiamat herself? Rootmere's own Tamer! I'm telling EVERYONE."); return; }
    if (S.flag('got_starter')) { await S.say(null, "A Tamer at last! Route 1 is north of the village. Wild Morphs hide in the tall grass — weaken them before you throw a Capsule."); return; }
    await S.say(null, "Happy naming day, {PLAYER}! Dr. Marsh has been up since dawn getting the lab ready for you and Wren.");
  },

  // ── Marsh Morph Lab ───────────────────────────────────────────────────
  'map:marsh_lab': async (S) => {
    if (S.flag('lab_intro')) { return; }
    S.set('lab_intro');
    await S.wait(250);
    await S.emote('marsh', '!');
    await S.say('Dr. Marsh', "Ah, {PLAYER}! There you are. Happy naming day!");
    await S.move('player', 'u3');
    await S.say('Wren', "Finally! Grandma wouldn't let me choose until you got here. I've been waiting for AGES.");
    await S.say('Dr. Marsh', "Patience, Wren. Now — every Tamer in Rootmere receives their first Morph on their naming day.");
    await S.say('Dr. Marsh', "On the table are three capsules: Spriglet, the Nature Morph; Cindlet, the Ember Morph; and Puddlet, the Tide Morph.");
    await S.say('Dr. Marsh', 'Go on, {PLAYER}. Take a look and choose the one that speaks to you.');
    await S.say('Wren', "And then I'll pick the one that beats it. Obviously.");
  },
  'lab.starters': async (S) => {
    if (S.flag('got_starter')) { await S.say(null, 'The capsules are empty now. Their Morphs have all found their Tamers.'); return; }
    const pick = await S.choose(null, 'Three capsules sit on the table. Which Morph will you choose?', [
      { label: 'Spriglet  (Nature)', value: 'spriglet' },
      { label: 'Cindlet   (Ember)', value: 'cindlet' },
      { label: 'Puddlet   (Tide)', value: 'puddlet' },
      { label: 'Not yet', value: null },
    ]);
    if (!pick) { return; }
    const info = STARTERS[pick];
    const img = S.spriteAt('mons', `${pick}_f`, 6, 5, { depth: 7600 });
    S.w.tweens.add({ targets: img, y: img.y - 4, duration: 500, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
    const ok = await S.ask(null, `${info.blurb}|Will you choose ${info.name}?`);
    img.destroy();
    if (!ok) { return; }
    S.setVar('starter', pick);
    await S.giveMorph(pick, 5, { text: `{PLAYER} chose ${info.name}!`, ivs: partnerIvs() });
    const wp = RIVAL_PICK[pick];
    await S.emote('lab_wren', '!');
    await S.say('Wren', `Then I'll take ${SPECIES[wp].name}! ${STARTERS[wp].type} beats ${info.type}. Sorry, not sorry.`);
    await S.say(null, `Wren received ${SPECIES[wp].name}!`);
    await S.say('Wren', "Grandma says we're both Tamers now. So let's find out who's better — right here, right now!");
    await S.say('Dr. Marsh', 'Not near the machines, you two— oh, never mind.');
    const r = await rivalBattle(S, `rival1_${pick}`);
    await S.heal({ silent: true });
    if (r === 'win') {
      await S.say('Wren', "What?! I had the type advantage! That's not how it's supposed to go!");
    } else {
      await S.say('Wren', "Ha! Told you. Type advantage, {PLAYER}. Look it up.");
    }
    await S.say('Wren', "I'm going to train until my Morph is the strongest in the Reach. See you out there!");
    await S.move('lab_wren', 'd4,r3,d1');
    S.hide('lab_wren');
    S.sfx('door');
    await S.say('Dr. Marsh', 'That child... Well! I patched up both your teams. Now, a few gifts for a new Tamer.');
    S.set('got_index');
    await S.say(null, "{PLAYER} received the Morph Index!|It records every Morph you see and catch. Open it from the menu.");
    await S.give('reach_map');
    await S.give('capsule', 5);
    await S.say('Dr. Marsh', "And one favour. This parcel is for my old friend Mossa — Warden Mossa, in Brindlewood. It's north along Route 1.");
    await S.give('marsh_parcel');
    await S.say('Dr. Marsh', 'Warden Mossa runs the Moss Trial. Win it, and she\'ll give you a Sigil — the first of six. Off you go, {PLAYER}!');
    S.set('got_starter');
  },
  'lab.marsh': async (S) => {
    if (!S.flag('got_starter')) { await S.say('Dr. Marsh', 'Take your time. A Tamer and their first Morph are partners for life.'); return; }
    const seen = S.state.index.seen.length, caught = S.state.index.caught.length;
    await S.say('Dr. Marsh', `Let me see your Index... ${seen} seen, ${caught} caught.`);
    const verdict = caught >= 60 ? "Extraordinary. You've nearly catalogued the whole Reach!"
      : caught >= 40 ? 'Superb work. The Index has never been this full.'
        : caught >= 20 ? 'A fine start! Every new Morph teaches us something.'
          : caught >= 8 ? "Good! Keep an eye on the tall grass — different Morphs come out at night."
            : 'Everyone starts somewhere. Weaken wild Morphs, then throw a Capsule!';
    await S.say('Dr. Marsh', verdict);
    if (S.state.sigils.length >= 6 && !S.flag('cradle_done')) {
      await S.say('Dr. Marsh', "Six Sigils... Be careful, {PLAYER}. I've read the old records. The Sigils were never meant to be together.");
    }
  },
  'lab.wren': async (S) => {
    await S.say('Wren', "Hurry up and choose! Whatever you pick, I'm taking the one that beats it.");
  },
  'lab.aide': async (S) => {
    if (S.flag('got_starter') && !S.flag('lab_aide_gift')) {
      await S.say('Aide', "Congratulations! Here's something from me — every new Tamer needs a few Tonics.");
      await S.give('tonic', 3);
      S.set('lab_aide_gift');
      return;
    }
    await S.say('Aide', "Tip: a wild Morph is easier to catch when its HP is low — and even easier if it's asleep or paralysed!");
  },

  // ── Route 1 ─────────────────────────────────────────────────────────────
  'route1.aide': async (S) => {
    if (!S.flag('r1_aide_gift')) {
      await S.say('Aide', "Oh, {PLAYER}! Dr. Marsh asked me to check the Route for new Tamers. How's your team?");
      await S.say('Aide', 'Here, take these. Ward Incense keeps weak wild Morphs away for a while.');
      await S.give('ward_incense', 2);
      S.set('r1_aide_gift');
      return;
    }
    await S.say('Aide', 'Ledges only go one way — you can hop down them, but not climb back up. Handy for getting home fast!');
  },

  // ── Brindlewood ─────────────────────────────────────────────────────────
  'brindlewood.seal': async (S) => {
    await S.say(null, 'An ancient standing stone, furred with moss. Faint carvings spiral around it.|It hums, very quietly, like someone singing in their sleep.');
    if (S.flag('sigil_moss')) { await S.say(null, 'The Moss Sigil in your bag hums back.'); }
  },
  'brindlewood.gardener': async (S) => {
    if (!S.flag('sigil_moss')) { await S.say(null, "Warden Mossa's Trial Hall is the big green building up north. She loves a challenger — mind her Thornbur, mind you."); return; }
    await S.say(null, 'Route 2 is east of town, but the brambles have grown right over the road. A Brush Hook would clear them.');
  },
  'brindlewood.posy': async (S) => {
    if (S.flag('pip_found') && !S.flag('pip_returned')) {
      await S.say('Posy', 'Is that... PIP!');
      await S.say(null, 'Pip the Burrlet leaps out of your arms and into Posy\'s, ringing its little bell.');
      await S.say('Posy', "You found him! Thank you, thank you, THANK YOU! Here — Grandad made this charm for Pip, but I think you should have it.");
      await S.take('pips_bell');
      await S.give('bond_charm');
      await S.say('Posy', 'The Bond Charm shares battle experience with the Morphs who sit out. That way the whole team grows together!');
      S.set('pip_returned');
      return;
    }
    if (!S.flag('pip_asked')) {
      await S.say('Posy', "*sniff*... My Burrlet, Pip, chased a Beakling into Thornwild and never came back.");
      await S.say('Posy', "Thornwild's east, past the brambles on Route 2. Pip has a little bell on a ribbon... Please, if you see him...");
      S.set('pip_asked');
      return;
    }
    await S.say('Posy', 'Pip likes berry bushes... and hiding. Please find him!');
  },
  'brindlewood.posy_mum': async (S) => {
    if (S.flag('pip_returned')) { await S.say(null, "Posy hasn't let go of that Burrlet since you brought him home. Thank you, dear."); return; }
    await S.say(null, "Posy's been crying since this morning. Her Burrlet ran off into Thornwild. I'd go myself, but those woods...");
  },
  'brindlewood.aldous': async (S) => {
    if (S.flag('got_nyxen')) { await S.say('Aldous', "How's the little one? Nyxen glow brightest under a new moon. Take it out at night sometime."); return; }
    if (S.state.sigils.length < 1) {
      await S.say('Aldous', "Eh? A new Tamer. I walked the whole Reach once, you know. Six Sigils. Long time ago.|Come back when you've earned your first Sigil. I might have something for you.");
      return;
    }
    await S.say('Aldous', "The Moss Sigil! So Mossa's finally met her match. Good, good.");
    await S.say('Aldous', "My old partner had a clutch before she passed. This one never took to me — too old, too slow. It wants to travel. Will you take it?");
    const mon = await S.giveMorph('nyxen', 12, { ivs: partnerIvs() });
    if (mon) { S.set('got_nyxen'); }
    await S.say('Aldous', 'Nyxen is an Umbra Morph. Sneaky. Loyal. Look after each other.');
  },
  'brindlewood_trial.warden': async (S) => {
    if (S.flag('sigil_moss')) {
      await S.say('Mossa', "You've got the Moss Sigil, dear. Now go and see the rest of the Reach — it's bigger than you think.");
      await S.say('Mossa', "And if you ever wonder why a Warden guards a stone... well. Ask Morrow in Hollowmere. She tells it better than I do.");
      return;
    }
    if (S.has('marsh_parcel')) {
      await S.say('Mossa', "Oh! Is that a parcel from Ione? Let me see... research notes. 'The Seals. Why six? Why Sigils?'");
      S.take('marsh_parcel');
      S.set('parcel_given');
      await S.say('Mossa', "She's asking the same questions I used to. Hm. Thank you for bringing it, {PLAYER}.");
    }
    await S.say('Mossa', "Now then. You've come for my Trial. My garden grows slowly — and hits back hard. Ready?");
    const r = await S.battle('mossa');
    if (r !== 'win') { return; }
    S.sigil('moss'); S.set('sigil_moss');
    S.jingle('jingle_sigil');
    await S.say(null, '{PLAYER} received the Moss Sigil from Warden Mossa!');
    await S.say('Mossa', 'The Moss Sigil. Keep it close. It is more than a badge — though nobody has asked me what more in a very long time.');
    await S.give('td07');
    await S.say('Mossa', 'TD07 is Bloom Blast. A Tech Disc can be used again and again.');
    await S.give('brush_hook');
    await S.say('Mossa', "And my Brush Hook. The brambles on Route 2 have grown wild — face them and you'll clear the way. Thornwild is past the river.");
  },
};
