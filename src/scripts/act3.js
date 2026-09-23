// Act III — Fog and Glass: Moorwind Way, Hollowmere and Glasslake.
import { bossBattle } from './common.js';

export default {
  'route4.circle': async (S) => {
    await S.say(null, 'The centre stone of the circle is carved with six marks around a coiled shape. Beneath them:');
    await S.say(null, '"SIX TO SEAL. SIX TO OPEN.|THE COVENANT HOLDS WHILE THE KEYS ARE KEPT APART."');
    if (S.state.sigils.length >= 3) { await S.say(null, 'The Sigils in your bag grow warm, all at once.'); }
  },

  // ── Hollowmere ─────────────────────────────────────────────────────────
  'hollowmere.seal': async (S) => {
    await S.say(null, 'A Seal-stone stands among older standing stones, half-swallowed by fog. You can hear the lake lapping behind it.');
    if (S.flag('sigil_veil')) { await S.say(null, 'The Veil Sigil answers with a low hum. So do the other three.'); }
  },
  'hollowmere.fisher': async (S) => {
    if (S.flag('maren1_done')) { await S.say('Angler', "Fog's lifting over Glasslake. With a Skiff you can cross west, then follow the north shore up to Frostspire."); return; }
    await S.say('Angler', "Can't see ten feet across Glasslake today. Fog comes and goes with the Warden's moods, folk say.");
  },
  'hollowmere.lakegate': async (S) => {
    await S.say(null, 'The fog over Glasslake is as thick as wool. You could paddle in circles out there for days.');
    await S.stepBack();
  },
  'hollowmere.archivist': async (S) => {
    await S.say('Archivist', 'Welcome to the Archive. Every story the Reach has ever told is on these shelves — the true ones, and the other kind.');
    await S.say('Archivist', 'The oldest record of all is a single line: "The Wardens keep the keys apart, and the Mother keeps her sleep."');
    if (S.flag('sigil_veil')) { await S.say('Archivist', "Keys apart... and here you are, carrying four of them in one bag. Hm."); }
  },
  'hollowmere.ferry': async (S) => {
    await S.say('Ferrywoman', "I used to row folk across Glasslake. Then the Deepcall bought every boat on the shore. Every single one.");
  },
  'hollowmere_trial.warden': async (S) => {
    if (S.flag('sigil_veil')) {
      await S.say('Morrow', 'Go on to Frostspire, {PLAYER}. And keep your Sigils close — closer than you ever have.');
      return;
    }
    await S.say('Morrow', "Every Trial is a story, {PLAYER}. Mine is a ghost story. Let's see how yours ends.");
    const r = await S.battle('morrow');
    if (r !== 'win') { return; }
    S.sigil('veil'); S.set('sigil_veil');
    S.jingle('jingle_sigil');
    await S.say(null, '{PLAYER} received the Veil Sigil from Warden Morrow!');
    await S.give('td09');
    await S.say('Morrow', "And now, the story you've been wondering about. Sit. Listen.");
    await S.say('Morrow', "Long ago the sea-dragon Tiamat was sundered, and the Reach was built from her body. She did not die. She sleeps.");
    await S.say('Morrow', "The first Wardens built six Seals to keep her sleeping, and made six Sigils — the keys to her Cradle.");
    await S.say('Morrow', "Then they did something clever. They gave the keys away, one at a time, to Tamers who would scatter across the Reach. Keys kept apart can never open a door.");
    await S.say('Morrow', "...But you are not scattering, are you, {PLAYER}? You are collecting. Someone has been waiting a very long time for a Tamer like you.");
  },
  'hollowmere.shore': async (S) => {
    S.show('hm_wren', 11, 16, 'right');
    S.show('hm_maren', 10, 17, 'right');
    S.music('deepcall');
    await S.say('???', '{PLAYER}.');
    S.face('player', 'left');
    await S.say(null, 'Two figures stand on the pier. One of them is wearing Deepcall robes — and it is Wren.');
    await S.say('Wren', "Don't look at me like that. Maren told me everything. The things Grandma's notes were too scared to say.");
    await S.say('Wren', "The Wardens aren't protectors, {PLAYER}. They're JAILERS. There's something alive under the Reach and they've kept it chained for a thousand years.");
    await S.say('Maren', "I'm Maren. I'm sorry we had to meet like this. Tiamat is not a monster — she is the sea's mother, and she is in pain.");
    await S.say('Maren', "We only want to wake her. But you carry four of the keys now... I need to know what kind of Tamer you are.");
    await bossBattle(S, 'maren1');
    await S.say('Maren', "You fight for what you believe. So do we. The fog will lift for you now — we'll meet again at the Riven.");
    await S.say('Wren', "...See you, {PLAYER}. I hope you understand, one day.");
    await S.fadeOut(300);
    S.hide('hm_wren'); S.hide('hm_maren');
    S.music('hollowmere');
    await S.fadeIn(300);
    await S.say(null, 'The fog over Glasslake is thinning. You could cross it with the Skiff now.');
  },
};
