// Shared scripts: Havens (healing, shops, storage), home, generic helpers.
import { G } from '../core/state.js';
import { ITEMS } from '../data/items.js';

// What the Haven counter sells grows with your Sigils.
export function havenStock() {
  const n = G.state.sigils.length;
  const s = ['capsule', 'tonic', 'purge_herb', 'nerve_balm', 'wake_chime', 'cool_salve', 'ward_incense'];
  if (n >= 1) { s.push('prime_capsule', 'strong_tonic', 'thaw_draught', 'homing_thread'); }
  if (n >= 2) { s.push('rekindle_seed', 'strong_incense'); }
  if (n >= 3) { s.push('grand_tonic', 'dusk_capsule', 'swift_capsule', 'clarity_leaf'); }
  if (n >= 4) { s.push('apex_capsule', 'full_tonic'); }
  if (n >= 5) { s.push('panacea', 'focus_drop'); }
  const order = { capsules: 0, items: 1 };
  return s.filter((id) => ITEMS[id]).sort((a, b) => (order[ITEMS[a].pocket] ?? 2) - (order[ITEMS[b].pocket] ?? 2));
}

// Rival battles never send you home: Wren patches your team up instead.
export async function rivalBattle(S, id) {
  const r = await S.battle(id, { noWhiteout: true });
  if (r === 'lose') {
    await S.heal({ silent: true });
    await S.say('Wren', "Here — I'm not letting you walk around with a fainted team. Grandma would never forgive me.");
  }
  return r;
}

// A story boss: losing sends you back to the last Haven as usual, but only after the scene ends cleanly.
export async function bossBattle(S, id, opts = {}) {
  const r = await S.battle(id, { noWhiteout: true, boss: true, ...opts });
  if (r === 'lose') { await S.whiteout(); }
  return r;
}

export default {
  'home.pc': async (S) => {
    await S.say(null, '{PLAYER} booted up the PC.');
    await S.openScreen('storage');
  },
  'home.mum': async (S) => {
    if (!S.flag('got_starter')) {
      await S.say('Mum', "Happy naming day, love! Dr. Marsh is waiting for you at the lab.|Go on — your first Morph! I'm so proud I could burst.");
      return;
    }
    const lines = S.flag('game_clear')
      ? "My little Tamer, home from saving the whole Reach. Sit down, I'll put the kettle on."
      : S.state.sigils.length >= 3
        ? "Look at you, all those Sigils! You look tired though. Have a rest."
        : "There you are! You look worn out. Come and have a rest.";
    await S.say('Mum', lines);
    await S.heal();
    S.setHealPoint('home_1f', 4, 7);
    await S.say('Mum', "There — you and your Morphs are right as rain. Don't forget to write! Or visit. Visiting is better.");
  },

  'haven.heal': async (S) => {
    const yes = await S.ask('Haven Keeper', 'Welcome to the Haven! Would you like me to rest your Morphs?', 'Yes, please', 'No thanks');
    if (!yes) { await S.say('Haven Keeper', 'Safe travels! We are always open.'); return; }
    if (!S.state.party.length) { await S.say('Haven Keeper', "Oh! You don't have any Morphs with you. Come back when you do!"); return; }
    await S.say('Haven Keeper', "Let's see to your team...");
    await S.heal();
    const p = S.state.player;
    S.setHealPoint(p.map, p.x, p.y);
    await S.say('Haven Keeper', 'All done! Your Morphs are fighting fit. Come back any time!');
  },
  'haven.shop': async (S) => {
    await S.say('Clerk', 'Welcome! What can I get you?');
    await S.openScreen('shop', { stock: havenStock(), title: 'Haven Counter' });
    await S.say('Clerk', 'Thanks for stopping by!');
  },
  'haven.pc': async (S) => {
    await S.say(null, '{PLAYER} booted up the Haven PC.|Morph Storage System: online.');
    await S.openScreen('storage');
  },
};
