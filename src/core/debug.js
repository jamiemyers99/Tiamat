// Developer tools (enabled with ?debug in the URL, F1 in-game).
import { G, giveItem, setFlag, markCaught, receiveMorph } from './state.js';
import { createMon, healMon } from '../battle/mon.js';
import { ITEMS } from '../data/items.js';
import { UI } from '../scenes/UIScene.js';

export async function debugMenu(world) {
  const maps = Object.keys(world.cache.json.get('mapIndex'));
  const v = await UI.choose(null, 'Debug', [
    { label: 'Warp to map', value: 'warp' }, { label: 'Heal team', value: 'heal' }, { label: 'Give items', value: 'items' },
    { label: 'Team +5 levels', value: 'lv' }, { label: 'Add test team', value: 'team' }, { label: 'Night / day', value: 'time' },
    { label: 'Set flag', value: 'flag' }, { label: 'Close', value: null },
  ]);
  if (v === 'warp') {
    const m = await UI.choose(null, null, maps.map((id) => ({ label: id, value: id })), { visible: 10 });
    if (m) { const sp = world._spawnPoint(m); world.transition(m, sp[0], sp[1], 'down'); }
  }
  if (v === 'heal') { G.state.party.forEach(healMon); }
  if (v === 'items') { Object.keys(ITEMS).forEach((k) => giveItem(k, ITEMS[k].key || ITEMS[k].disc ? 1 : 10)); G.state.money += 50000; setFlag('trail_boots'); setFlag('got_index'); }
  if (v === 'lv') { G.state.party.forEach((m) => { m.level = Math.min(100, m.level + 5); healMon(m); }); }
  if (v === 'team') { ['pyromane', 'maelstrand', 'mosswarden'].forEach((s) => { const m = createMon(s, 40); markCaught(s, m.sex); receiveMorph(m); }); }
  if (v === 'time') { G.state.clock = (G.state.clock + 720) % 1440; }
  if (v === 'flag') { const f = window.prompt('flag name'); if (f) { setFlag(f); world.refreshNpcs(); } }
}
