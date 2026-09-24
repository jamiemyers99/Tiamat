// Items. pocket: items | capsules | discs | key
// use.kind: heal, revive, cure, pp, capsule, repel, escape, level, teach, key
import { MOVES } from './moves.js';

export const POCKETS = [
  { id: 'items', name: 'Items' },
  { id: 'capsules', name: 'Capsules' },
  { id: 'discs', name: 'Tech Discs' },
  { id: 'key', name: 'Key Items' },
];

export const ITEMS = {};
function it(id, name, pocket, price, use, desc, extra = {}) {
  ITEMS[id] = { id, name, pocket, price, use, desc, pocketName: POCKETS.find((p) => p.id === pocket).name, ...extra };
}

// ── Capsules ────────────────────────────────────────────────────────────────
it('capsule', 'Capsule', 'capsules', 200, { kind: 'capsule', rate: 1 }, 'A standard capsule for taming wild Morphs.');
it('prime_capsule', 'Prime Capsule', 'capsules', 600, { kind: 'capsule', rate: 1.5 }, 'A sturdier capsule with a better chance of success.');
it('apex_capsule', 'Apex Capsule', 'capsules', 1200, { kind: 'capsule', rate: 2 }, 'A high-grade capsule used by veteran Tamers.');
it('dusk_capsule', 'Dusk Capsule', 'capsules', 1000, { kind: 'capsule', rate: 1, dusk: 3 }, 'Works far better at night or deep underground.');
it('swift_capsule', 'Swift Capsule', 'capsules', 1000, { kind: 'capsule', rate: 1, firstTurn: 4 }, 'Works best if thrown at the very start of a battle.');
it('covenant_capsule', 'Covenant Capsule', 'key', 0, { kind: 'capsule', rate: 255 }, 'Forged from the six Sigils. It can hold even something ancient.', { key: true });

// ── Healing ─────────────────────────────────────────────────────────────────
it('tonic', 'Tonic', 'items', 200, { kind: 'heal', hp: 20 }, 'A herbal tonic. Restores 20 HP.');
it('strong_tonic', 'Strong Tonic', 'items', 700, { kind: 'heal', hp: 60 }, 'A potent tonic. Restores 60 HP.');
it('grand_tonic', 'Grand Tonic', 'items', 1500, { kind: 'heal', hp: 150 }, 'A remarkable tonic. Restores 150 HP.');
it('full_tonic', 'Full Tonic', 'items', 2500, { kind: 'heal', hp: 9999 }, 'Fully restores a Morph\'s HP.');
it('panacea', 'Panacea', 'items', 3000, { kind: 'heal', hp: 9999, cure: 'all' }, 'Fully restores HP and cures any status problem.');
it('purge_herb', 'Purge Herb', 'items', 150, { kind: 'cure', status: ['poison', 'toxic'] }, 'A bitter herb that cures poisoning.');
it('cool_salve', 'Cool Salve', 'items', 250, { kind: 'cure', status: ['burn'] }, 'A soothing salve that heals a burn.');
it('wake_chime', 'Wake Chime', 'items', 250, { kind: 'cure', status: ['sleep'] }, 'A bright chime that wakes a sleeping Morph.');
it('thaw_draught', 'Thaw Draught', 'items', 250, { kind: 'cure', status: ['freeze'] }, 'A warming drink that thaws a frozen Morph.');
it('nerve_balm', 'Nerve Balm', 'items', 200, { kind: 'cure', status: ['paralyze'] }, 'Rubbed on stiff limbs, it cures paralysis.');
it('clarity_leaf', 'Clarity Leaf', 'items', 600, { kind: 'cure', status: 'all' }, 'Cures any status problem, including confusion.');
it('rekindle_seed', 'Rekindle Seed', 'items', 1500, { kind: 'revive', frac: 0.5 }, 'Revives a fainted Morph with half its HP.');
it('bloom_seed', 'Bloom Seed', 'items', 0, { kind: 'revive', frac: 1 }, 'Revives a fainted Morph with full HP.');
it('focus_drop', 'Focus Drop', 'items', 1200, { kind: 'pp', pp: 10 }, 'Restores 10 PP to one move.');
it('growth_fruit', 'Growth Fruit', 'items', 0, { kind: 'level' }, 'A rare fruit that raises a Morph\'s level by 1.');
it('ward_incense', 'Ward Incense', 'items', 400, { kind: 'repel', steps: 100 }, 'Keeps weaker wild Morphs away for 100 steps.');
it('strong_incense', 'Strong Incense', 'items', 700, { kind: 'repel', steps: 250 }, 'Keeps weaker wild Morphs away for 250 steps.');
it('homing_thread', 'Homing Thread', 'items', 550, { kind: 'escape' }, 'Follow it back to the entrance of a cave or dungeon.');
it('pearl', 'Tide Pearl', 'items', 0, { kind: 'sell' }, 'A lovely pearl. Shops pay well for it.', { sell: 1400 });
it('star_shard', 'Star Shard', 'items', 0, { kind: 'sell' }, 'A shard that fell from the night sky. Worth a lot.', { sell: 3000 });

// ── Key items ───────────────────────────────────────────────────────────────
it('trail_boots', 'Trail Boots', 'key', 0, { kind: 'key' }, 'Hold {BTN:run} while walking to dash.', { key: true });
it('xp_share', 'XP Share', 'key', 0, { kind: 'attach' }, 'A charm on a cord. While it is attached to you, every Morph in your team gets the full XP from each battle.', { key: true });
it('bond_charm', 'Bond Charm', 'key', 0, { kind: 'key' }, 'Lets Morphs that sit out a battle still gain some XP.', { key: true });
it('reach_map', 'Reach Map', 'key', 0, { kind: 'map' }, 'A map of the Riven Reach. Shows where you are.', { key: true });
it('brush_hook', 'Brush Hook', 'key', 0, { kind: 'key' }, 'A curved blade for clearing brambles. Use it by facing a bramble.', { key: true });
it('skiff', 'Skiff', 'key', 0, { kind: 'key' }, 'A folding boat. Face open water and press {BTN:confirm} to launch it.', { key: true });
it('marsh_parcel', 'Marsh Parcel', 'key', 0, { kind: 'key' }, 'A parcel of research notes for Warden Mossa.', { key: true });
it('forge_ember', 'Forge Ember', 'key', 0, { kind: 'key' }, 'A glowing coal from Gearhollow\'s great forge, kept alight in a little lantern.', { key: true });
it('pips_bell', "Pip's Bell", 'key', 0, { kind: 'key' }, 'A little bell on a ribbon. Pip the Burrlet wore it.', { key: true });
it('forge_pass', 'Forge Pass', 'key', 0, { kind: 'key' }, 'A pass for the Coldforge Ironworks.', { key: true });
it('rift_key', 'Chapel Key', 'key', 0, { kind: 'key' }, 'A heavy key stamped with a wave. Opens the Sunken Chapel.', { key: true });
it('wing_whistle', 'Wing Whistle', 'key', 0, { kind: 'map' }, 'Calls a friendly Skyveer. Open the Reach Map outdoors to fly to any town you have visited.', { key: true });
it('seal_shard', 'Seal Shard', 'key', 0, { kind: 'key' }, 'A glowing chip of Seal-stone, still warm.', { key: true });

// ── Tech Discs (reusable) ─────────────────────────────────────────────────
const TDS = [
  ['td01', 'guard_up', 1500], ['td02', 'mend', 0], ['td03', 'quake_stomp', 0], ['td04', 'thunder_arc', 0],
  ['td05', 'rime_ray', 0], ['td06', 'blaze_ring', 3000], ['td07', 'bloom_blast', 0], ['td08', 'tide_pulse', 3000],
  ['td09', 'shadow_creep', 0], ['td10', 'mind_spike', 0], ['td11', 'power_kick', 3000], ['td12', 'wing_strike', 2500],
  ['td13', 'alloy_lash', 0], ['td14', 'mire_blast', 0], ['td15', 'swarm_strike', 0], ['td16', 'scale_rake', 0],
  ['td17', 'rally_cry', 2000], ['td18', 'numb_pulse', 2500],
];
for (const [id, move, price] of TDS) {
  const mv = MOVES[move];
  it(id, `${id.toUpperCase()} ${mv.name}`, 'discs', price, { kind: 'teach', move }, `Teaches ${mv.name}. ${mv.desc}`, { disc: true });
}

// Can this species learn a Tech Disc move? Same-type moves, Plain utility moves,
// and a few sensible extras.
export function canLearnDisc(species, moveId) {
  const mv = MOVES[moveId];
  if (!mv) { return false; }
  if (['guard_up', 'rally_cry', 'mend'].includes(moveId)) { return species.id !== 'tiamat' || moveId !== 'rally_cry'; }
  if (species.types.includes(mv.type)) { return true; }
  const extras = {
    quake_stomp: ['Brawl', 'Iron', 'Drake', 'Plain'],
    power_kick: ['Plain', 'Stone', 'Umbra', 'Frost'],
    wing_strike: ['Drake', 'Swarm'],
    thunder_arc: ['Wing', 'Tide', 'Iron'],
    rime_ray: ['Tide', 'Drake'],
    shadow_creep: ['Mind', 'Toxin'],
    mind_spike: ['Umbra', 'Frost'],
    numb_pulse: ['Wing', 'Iron', 'Mind'],
    tide_pulse: ['Frost', 'Drake'],
    bloom_blast: ['Toxin', 'Swarm'],
  };
  return (extras[moveId] || []).some((t) => species.types.includes(t));
}
