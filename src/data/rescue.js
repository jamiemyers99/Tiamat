// Rescue quests: the two starters you didn't choose can each be found somewhere in the Reach,
// in trouble. Help them and they join you — so every Morph can be collected in one game.
import { G } from '../core/state.js';

export const RESCUES = {
  spriglet: { npc: 'tw_spriglet', level: 12, flag: 'rescued_spriglet', where: 'Thornwild', hint: 'a Spriglet was seen deep in Thornwild, tangled in brambles' },
  puddlet: { npc: 'r3_puddlet', level: 15, flag: 'rescued_puddlet', where: 'Gullcliff Road', hint: 'a Puddlet is stranded on the Gullcliff Road shore, east of Saltreach' },
  cindlet: { npc: 'cf_cindlet', level: 17, flag: 'rescued_cindlet', where: 'Coldforge Mines', hint: 'a Cindlet has been spotted shivering in Coldforge Mines' },
};

// Quests still open for this save (never the starter you chose).
export function openRescues(state = G.state) {
  const mine = state.vars && state.vars.starter;
  return Object.keys(RESCUES).filter((id) => id !== mine && !(state.flags && state.flags[RESCUES[id].flag]));
}

// A stable male/female form for a Morph you meet in the world (the same every time you load).
export function worldMorphSex(species, state = G.state) {
  let h = (Number(state.trainerId) || 0) >>> 0;
  for (const ch of species) { h = Math.imul(h ^ ch.charCodeAt(0), 2654435761) >>> 0; }
  return (h >>> 15) & 1 ? 'f' : 'm';
}
