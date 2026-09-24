// Starter rescue quests (see data/rescue.js). Only the two starters you didn't choose appear.
import { partnerIvs } from '../data/difficulty.js';
import { RESCUES, worldMorphSex, openRescues } from '../data/rescue.js';
import { ITEMS } from '../data/items.js';
import { SPECIES } from '../data/species.js';

const HEALS = ['tonic', 'strong_tonic', 'grand_tonic', 'full_tonic', 'panacea'];

async function join(S, species) {
  const r = RESCUES[species];
  const nm = SPECIES[species].name;
  const ok = await S.ask(null, `${nm} looks up at {PLAYER} hopefully.|Will you take ${nm} with you?`);
  if (!ok) { await S.say(null, `${nm} sits down and waits, watching {PLAYER}.`); return false; }
  await S.giveMorph(species, r.level, { ivs: partnerIvs(), sex: worldMorphSex(species), text: `${nm} joined {PLAYER}'s team!` });
  S.set(r.flag);
  S.hide(r.npc);
  return true;
}

export default {
  // ── Spriglet: cornered in the Thornwild brambles by a hungry Mantipule ──
  'rescue.spriglet': async (S) => {
    const id = RESCUES.spriglet.npc;
    if (!S.flag('spriglet_defended')) {
      await S.say(null, 'A wild Spriglet! Its leaves are chewed ragged, and it is trembling...');
      await S.emote(id, '!');
      await S.say(null, 'Something clicks in the brambles behind it — a Mantipule has been snacking on its leaves!');
      const r = await S.wild('mantipule', 13);
      if (r !== 'win' && r !== 'caught') {
        if (r === 'fled') { await S.say(null, 'The Mantipule is still lurking. The Spriglet is still cornered...'); }
        return;
      }
      S.set('spriglet_defended');
      await S.say(null, 'The Mantipule is gone! The Spriglet tries to stand... and wobbles. It is too weak to walk.');
    }
    const heal = HEALS.find((h) => S.has(h));
    if (!heal) {
      await S.say(null, "The Spriglet's leaves are wilting. Something healing would help — a Tonic from a Haven shop, perhaps.");
      return;
    }
    if (!(await S.ask(null, `Give the Spriglet a ${ITEMS[heal].name}?`))) { return; }
    S.take(heal);
    await S.say(null, `The Spriglet sips the ${ITEMS[heal].name}... its leaves lift and turn bright green again!`);
    await S.emote(id, 'heart');
    await S.say(null, 'Spriglet hops around {PLAYER} in a happy little circle.');
    await join(S, 'spriglet');
  },

  // ── Puddlet: stranded in a drying rock pool, with two Deepcall acolytes trying to take it ──
  'rescue.puddlet': async (S) => {
    const id = RESCUES.puddlet.npc;
    if (!S.state.defeated.r3_poacher_a || !S.state.defeated.r3_poacher_b) {
      await S.say(null, 'A Puddlet, stuck in a rock pool that has almost dried out. The Deepcall acolytes have it cornered!');
      return;
    }
    await S.say(null, "The acolytes are gone. The Puddlet is huddled in the last puddle of its rock pool — its skin is dry and dull.");
    await S.emote(id, '...');
    await S.say(null, "It needs the sea, but it's too frightened to move.");
    if (!(await S.ask(null, 'Carry the Puddlet down to the water?'))) { return; }
    await S.fadeOut(300);
    await S.say(null, '{PLAYER} scooped up the Puddlet and waded out into the surf...');
    await S.fadeIn(300);
    await S.say(null, 'Splash! The Puddlet dives, spins and pops up again, shining and bouncy.');
    await S.emote(id, 'heart');
    await S.say(null, 'It swims straight back to {PLAYER} and will not leave your side.');
    await join(S, 'puddlet');
  },

  // ── Cindlet: freezing in Coldforge Mines; its flame needs real forge fire ──
  'rescue.cindlet': async (S) => {
    const id = RESCUES.cindlet.npc;
    if (!S.has('forge_ember')) {
      if (!S.flag('cindlet_found')) {
        await S.say(null, 'A Cindlet is curled up beside the icy seep. Its tail-flame has shrunk to a tiny blue spark...');
        await S.emote(id, '...');
        await S.say(null, 'It is freezing. A spark that small needs real fire to catch again — a fire that never goes out.');
        S.set('cindlet_found');
        await S.say(null, 'The forges of Gearhollow burn day and night, and the town is just through the mines. Someone there might help.');
      } else {
        await S.say(null, "The Cindlet's spark flickers weakly. Gearhollow's forges burn day and night — someone there might spare some fire.");
      }
      return;
    }
    await S.say(null, '{PLAYER} opened the lantern and held out the Forge Ember...');
    S.take('forge_ember');
    await S.say(null, 'The Cindlet gulps it down — and its tail roars up bright orange! It shakes the frost off its fur.');
    await S.emote(id, 'heart');
    await join(S, 'cindlet');
  },
  'gearhollow.smith': async (S) => {
    if (S.flag(RESCUES.cindlet.flag)) { await S.say('Smith', "That Cindlet of yours looks toasty. Forge fire'll do that. Look after it!"); return; }
    if (S.has('forge_ember')) { await S.say('Smith', 'Get that ember down to the mines, quick. The lantern keeps it lit, but that little one is cold.'); return; }
    if (S.flag('cindlet_found')) {
      await S.say('Smith', "A Cindlet? Down by the seep in the mines? Poor scrap — they can't relight on their own once they get that cold.");
      await S.say('Smith', 'Here. A coal from the great forge, in a lantern. This fire has not gone out in two hundred years.');
      await S.give('forge_ember');
      return;
    }
    await S.say('Smith', 'This forge has burned for two hundred years. Never once gone out. Gearhollow runs on it — and on stubbornness.');
  },
  // Dr. Marsh's tip, added to her Index check
  'rescue.hint': async (S) => {
    const open = openRescues(S.state);
    if (!open.length) { return; }
    await S.say('Dr. Marsh', 'Oh — and field reports keep coming in. Wild starter Morphs are terribly rare, but...');
    for (const sp of open) { await S.say('Dr. Marsh', `...${RESCUES[sp].hint}.`); }
    await S.say('Dr. Marsh', 'If they need help, I can think of no one better than you, {PLAYER}.');
  },
};
