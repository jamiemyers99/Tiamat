// After the story: the Old Door under Rootmere, the Ancient Tunnel, Keeper Enna and the Deep Cradle, where
// Dr. Marsh's Mysterious Egg (the prize for a complete Index) hatches into Abzurath, the Draco King.
import { audio } from '../core/audio.js';
import { SPECIES } from '../data/species.js';
import { partnerIvs } from '../data/difficulty.js';

export default {
  // ── Rootmere: the Old Door ─────────────────────────────────────────────
  'rootmere.ancient_door': async (S) => {
    if (!S.has('crown_gem') || S.flag('ancient_door_open')) { return; }
    S.face('player', 'up');
    await S.say(null, 'The Crown Gem in your bag is glowing, brighter with every step towards the Old Door.');
    if (!(await S.ask(null, 'Set the Crown Gem into the hollow in the door?', 'Yes', 'Not yet'))) { return; }
    S.take('crown_gem');
    S.sfx('mv_orb');
    const lit = S.spriteAt('ui', 'ancient_slab_lit', 18, 31, { depth: 1.6, alpha: 0 });
    await S.tweenP({ targets: lit, alpha: 1, duration: 900 });
    await S.say(null, 'The gem clicks into place. Light races through the carvings: a wave on one side, a chain of iron on the other, circling the gem.');
    await S.shake(1000, 0.01);
    S.set('ancient_door_open');
    await S.tweenP({ targets: lit, alpha: 0, duration: 500 });
    lit.destroy();
    await S.say(null, 'With a groan like the earth turning over, the two halves of the Old Door slide apart.|Stone steps lead down into the dark beneath Rootmere.');
  },
  'rootmere.elder': async (S) => {
    let line;
    if (S.flag('abzurath_hatched')) {
      line = "A dragon made of iron, sleeping under our village all this time! I don't know whether to be frightened or proud. Proud, I think.";
    } else if (S.flag('ancient_door_open')) {
      line = 'You opened it! In all my years... My gran would never believe it. What is down there? No — don\'t tell me. Tell me when you come back up.';
    } else if (S.has('crown_gem')) {
      line = "That gem in your bag... it's glowing! The same colour as the carvings on the door. Go on, try it!";
    } else {
      line = "That door's been shut since before my great-gran's day. They say a king sleeps under Rootmere, waiting for someone worthy. Rubbish, probably.|Still. I come and sit with it most mornings.";
    }
    await S.say('Elder', line);
  },

  // ── The Ancient Tunnel: Keeper Enna ────────────────────────────────────
  'tunnel.keeper': async (S, ctx) => {
    if (S.flag('keeper_met')) {
      if (S.flag('abzurath_hatched')) {
        await S.say('Enna', 'The Draco King walks again, and he chose you. Treat him kindly, Champion. He waited a thousand years for you.');
      } else if (S.has('mystery_egg')) {
        await S.say('Enna', 'Take the egg to the incubator. It will know what to do. So will he.');
      } else {
        await S.say('Enna', 'The incubator is waiting for its egg. Builders carried it off long ago. Perhaps somebody in Rootmere who studies Morphs has seen it?');
      }
      return;
    }
    await S.emote('keeper_enna', '!');
    if (ctx.trigger) {
      await S.say('???', 'Footsteps? After all these years... Come here, Tamer. Let me see you.');
      await S.walkTo('player', 15, 7, 'up');
    }
    S.face('keeper_enna', 'player');
    await S.say('Enna', 'I am Enna, the last Keeper of the Deep Cradle. My family has watched this door since the first Covenant closed it.');
    await S.say('Enna', 'You know of Tiamat, the Draco Queen: the restless tide. But the first Covenant sang of TWO dragons.|Where she was the sea, he was the stone beneath it. Abzurath, the Draco King. The anchor that holds the world still.');
    await S.say('Enna', 'When the first Tamers put Tiamat to sleep in the Riven, Abzurath gave himself up to hold the Reach steady while she slept.|He folded himself into an egg of iron and sank beneath the place that became Rootmere. Beneath your home.');
    if (S.has('mystery_egg')) {
      await S.say('Enna', '...And you are carrying it. I can hear him. He knows the one who calmed his other half.');
    } else {
      await S.say('Enna', 'The egg was dug up and carried off by builders who never knew what it was. If it ever finds its way to you, bring it here.');
    }
    await S.say('Enna', 'Beyond this door is the incubator the first Covenant built for him. The door is yours, Champion.');
    await S.move('keeper_enna', 'l2');
    S.face('keeper_enna', 'right');
    S.set('keeper_met');
    S.sfx('mv_orb');
    await S.shake(600, 0.006);
    await S.say(null, 'Enna touches the carved slab. It slides aside without a sound.');
  },

  // ── The Deep Cradle: the incubator ─────────────────────────────────────
  'cradle.incubator': async (S) => {
    if (S.flag('abzurath_hatched')) {
      await S.say(null, "The incubator is still warm. Carved around its base: 'The tide and the stone. Neither sleeps alone.'");
      return;
    }
    if (!S.has('mystery_egg')) {
      await S.say(null, 'An incubator of stone and bronze under a dome of amber glass. It hums softly, as if it is waiting for something.|The cradle inside is shaped for an egg — a very large one.');
      return;
    }
    await S.say(null, 'The Mysterious Egg is shaking in your bag. The incubator hums louder.');
    if (!(await S.ask(null, 'Place the Mysterious Egg in the incubator?', 'Yes', 'Not yet'))) { return; }
    S.take('mystery_egg');
    const egg = S.spriteAt('ui', 'drake_egg', 7, 2.25, { depth: 6100, alpha: 0 });
    await S.tweenP({ targets: egg, alpha: 1, duration: 600 });
    await S.say(null, 'The egg settles into the cradle. The amber glass begins to glow...');
    S.sfx('mv_orb');
    for (let i = 0; i < 3; i++) {
      egg.setFrame(i % 2 ? 'drake_egg' : 'drake_egg_glow');
      await S.tweenP({ targets: egg, x: egg.x + 2, duration: 60, yoyo: true, repeat: 2 });
      await S.wait(260);
    }
    await S.shake(900, 0.012);
    egg.setFrame('drake_egg_glow');
    await S.say(null, 'Cracks of golden light split the iron shell!');
    await S.flash(500);
    egg.destroy();
    const mon = S.spriteAt('mons', 'abzurath_f', 7, 3.25, { depth: 6100, alpha: 0 });
    audio.cry(SPECIES.abzurath.num);
    await S.tweenP({ targets: mon, alpha: 1, y: mon.y - 8, duration: 1200, ease: 'Sine.easeOut' });
    await S.shake(500, 0.01);
    await S.say(null, 'The Draco King stretches, and the whole Reach seems to settle, like a ship finding its anchor.|Abzurath looks at you for a long moment... then lowers his great iron head.');
    S.set('abzurath_hatched');
    await S.giveMorph('abzurath', 60, {
      sex: 'm', ivs: partnerIvs(),
      moves: ['primordial_anvil', 'anvil_drop', 'scale_rake', 'rift_nova'],
      text: '{PLAYER} received Abzurath, the Draco King!',
    });
    mon.destroy();
    await S.say(null, "Abzurath's signature move is Primordial Anvil: a blow from the bottom of the world that can shatter a foe's defences.");
  },
};
