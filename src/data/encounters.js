// Wild encounter tables per map. Each entry: [species, minLv, maxLv, weight]
// grass: tall grass by day · night: tall grass 20:00–05:00 · water: while using the Skiff · cave: any floor tile
import { timeOfDay } from '../core/time.js';

export const ENCOUNTERS = {
  route1: {
    grass: [['nibbit', 2, 3, 35], ['beakling', 2, 3, 30], ['trotter', 3, 4, 15], ['burrlet', 3, 4, 12], ['chittik', 3, 3, 8], ['pawpunch', 3, 4, 8], ['hivling', 3, 4, 10]],
    night: [['nibbit', 2, 3, 35], ['hushling', 3, 4, 20], ['pookit', 3, 4, 20], ['burrlet', 3, 4, 15], ['beakling', 2, 3, 10], ['wispurr', 3, 4, 8]],
  },
  route2: {
    grass: [['chittik', 7, 9, 25], ['fuzzling', 7, 9, 20], ['beakling', 7, 10, 20], ['burrlet', 8, 10, 15], ['nibbit', 7, 9, 15], ['sporra', 9, 10, 5], ['pipfrog', 8, 10, 10], ['scorchling', 8, 10, 8]],
    night: [['fuzzling', 7, 10, 25], ['hushling', 8, 10, 20], ['pookit', 8, 10, 20], ['glowick', 9, 10, 15], ['nibbit', 7, 9, 20], ['stingrix', 8, 10, 8], ['wispurr', 8, 10, 8]],
    water: [['crabbit', 9, 12, 15], ['gullip', 9, 12, 60], ['jellume', 10, 13, 25], ['pipfrog', 9, 11, 10]],
  },
  thornwild: {
    grass: [['chittik', 9, 11, 20], ['fuzzling', 9, 11, 20], ['sporra', 10, 12, 20], ['burrlet', 10, 12, 15], ['mantipule', 12, 13, 5], ['glowick', 10, 12, 10], ['nyxen', 11, 12, 10], ['rivetle', 10, 12, 8], ['hivling', 10, 12, 10]],
    night: [['echirp', 10, 12, 25], ['pookit', 10, 12, 20], ['nyxen', 11, 13, 20], ['mothlume', 12, 13, 5], ['glowick', 10, 12, 15], ['hushling', 10, 12, 15], ['hollowisp', 11, 13, 10]],
  },
  saltreach: {
    water: [['gullip', 13, 16, 45], ['crabbit', 13, 16, 30], ['jellume', 14, 16, 25], ['zaplet', 13, 16, 12]],
  },
  route3: {
    grass: [['gullip', 15, 18, 25], ['trotter', 15, 18, 15], ['pebbling', 15, 18, 20], ['pugnet', 16, 18, 15], ['voltquill', 16, 18, 15], ['crabbit', 15, 18, 10], ['pawpunch', 15, 17, 8], ['scorchling', 15, 17, 8], ['stingrix', 16, 18, 8]],
    night: [['echirp', 15, 18, 25], ['pookit', 16, 18, 20], ['pebbling', 15, 18, 20], ['hushling', 16, 18, 20], ['pugnet', 16, 18, 15]],
    water: [['gullip', 16, 19, 40], ['crabbit', 16, 19, 30], ['jellume', 17, 20, 25], ['stormgull', 21, 22, 5], ['zaplet', 16, 19, 15]],
  },
  coldforge_mines: {
    cave: [['pebbling', 17, 20, 25], ['tunnip', 17, 20, 25], ['ferrite', 18, 21, 15], ['echirp', 17, 20, 20], ['oozelet', 18, 21, 10], ['coilbit', 19, 21, 5], ['rivetle', 17, 20, 12], ['oculith', 20, 21, 3]],
    water: [['crabbit', 18, 21, 70], ['oozelet', 18, 21, 30]],
  },
  route4: {
    grass: [['omenet', 24, 27, 20], ['lambkin', 24, 27, 20], ['sporra', 24, 27, 15], ['trotter', 24, 26, 10], ['voltquill', 25, 27, 15], ['cairnite', 26, 28, 5], ['pugnet', 25, 27, 15], ['knuckroo', 25, 27, 6], ['carapaxe', 25, 27, 6], ['brutusk', 26, 28, 5]],
    night: [['echirp', 24, 27, 20], ['pookit', 25, 28, 20], ['hushling', 25, 28, 20], ['omenet', 25, 27, 15], ['cairnite', 26, 28, 10], ['nyxen', 25, 27, 15], ['mystaline', 25, 27, 6], ['hollowisp', 24, 27, 10]],
    water: [['jellume', 25, 28, 40], ['gullip', 25, 28, 40], ['oozelet', 25, 28, 20], ['croakmire', 25, 28, 15]],
  },
  hollowmere: {
    water: [['jellume', 27, 30, 35], ['gullip', 27, 30, 35], ['crabbit', 27, 30, 20], ['medusheen', 30, 31, 10], ['croakmire', 27, 30, 15], ['thundeel', 30, 31, 5]],
  },
  route5: {
    grass: [['fuzzling', 28, 30, 15], ['mothlume', 29, 31, 10], ['omenet', 28, 31, 20], ['hushling', 28, 31, 20], ['lambkin', 28, 30, 15], ['chillcub', 29, 31, 10], ['flurrit', 30, 32, 10], ['frostkit', 28, 30, 10], ['waspire', 29, 31, 6], ['wyvlet', 28, 30, 2]],
    night: [['mothlume', 29, 31, 20], ['hushling', 28, 31, 25], ['vesperel', 30, 32, 10], ['pookit', 28, 31, 25], ['chillcub', 29, 31, 20], ['rimewraith', 30, 32, 4], ['stingrix', 28, 30, 8]],
    water: [['gullip', 27, 30, 30], ['jellume', 27, 30, 25], ['crabbit', 27, 30, 20], ['stormgull', 29, 31, 15], ['medusheen', 30, 31, 10], ['zaplet', 27, 30, 15]],
  },
  frostspire: {
    water: [['crabbit', 32, 35, 50], ['jellume', 32, 35, 50], ['thundeel', 32, 35, 10]],
  },
  route6: {
    grass: [['chillcub', 33, 36, 20], ['flurrit', 33, 36, 15], ['lambkin', 33, 35, 15], ['rammoth', 35, 37, 5], ['pebbling', 33, 35, 10], ['cragmaul', 35, 37, 10], ['wyrmkin', 34, 36, 10], ['glowick', 33, 36, 15], ['glacivix', 34, 36, 6], ['frostkit', 33, 35, 8], ['alloyena', 34, 37, 6], ['magmaw', 35, 37, 4], ['wyvlet', 33, 35, 3]],
    night: [['chillcub', 33, 36, 20], ['duskwing', 34, 37, 15], ['cairnite', 34, 37, 15], ['vesperel', 35, 37, 15], ['wyrmkin', 34, 36, 15], ['blazewing', 35, 37, 20], ['rimewraith', 34, 37, 8], ['grimshroud', 35, 37, 4]],
  },
  abyssal_rift: {
    cave: [['wyrmkin', 40, 43, 20], ['wyrmguard', 42, 45, 10], ['cairnite', 40, 43, 15], ['borebeast', 40, 43, 15], ['ferroclad', 41, 44, 10], ['vesperel', 40, 43, 15], ['duskwing', 40, 43, 15], ['scorvex', 40, 43, 10], ['grimshroud', 40, 43, 10], ['oculith', 41, 44, 6], ['wyverant', 41, 44, 4], ['alloyena', 40, 43, 8], ['juggernox', 43, 45, 3]],
    water: [['medusheen', 40, 44, 40], ['pincerock', 40, 44, 30], ['stormgull', 40, 44, 30], ['thundeel', 40, 44, 20]],
  },
};

if (typeof window !== 'undefined') { window.__encounters = ENCOUNTERS; }

function pick(table, rng) {
  const total = table.reduce((s, e) => s + e[3], 0);
  let r = rng() * total;
  for (const e of table) { r -= e[3]; if (r <= 0) { return e; } }
  return table[table.length - 1];
}

export function rollEncounter(mapId, kind, minute, rng = Math.random) {
  const t = ENCOUNTERS[mapId];
  if (!t) { return null; }
  let table = t[kind];
  if (kind === 'grass' && timeOfDay(minute) === 'night' && t.night) { table = t.night; }
  if (kind === 'cave' && !table) { table = t.grass; }
  if (!table || !table.length) { return null; }
  const [species, lo, hi] = pick(table, rng);
  return { species, level: lo + Math.floor(rng() * (hi - lo + 1)) };
}
