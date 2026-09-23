// Wild encounter tables per map. Each entry: [species, minLv, maxLv, weight]
// grass: tall grass by day · night: tall grass 20:00–05:00 · water: while using the Skiff · cave: any floor tile
import { timeOfDay } from '../core/time.js';

export const ENCOUNTERS = {
  route1: {
    grass: [['nibbit', 2, 3, 35], ['beakling', 2, 3, 30], ['trotter', 3, 4, 15], ['burrlet', 3, 4, 12], ['chittik', 3, 3, 8]],
    night: [['nibbit', 2, 3, 35], ['hushling', 3, 4, 20], ['pookit', 3, 4, 20], ['burrlet', 3, 4, 15], ['beakling', 2, 3, 10]],
  },
  route2: {
    grass: [['chittik', 7, 9, 25], ['fuzzling', 7, 9, 20], ['beakling', 7, 10, 20], ['burrlet', 8, 10, 15], ['nibbit', 7, 9, 15], ['sporra', 9, 10, 5]],
    night: [['fuzzling', 7, 10, 25], ['hushling', 8, 10, 20], ['pookit', 8, 10, 20], ['glowick', 9, 10, 15], ['nibbit', 7, 9, 20]],
    water: [['crabbit', 9, 12, 15], ['gullip', 9, 12, 60], ['jellume', 10, 13, 25]],
  },
  thornwild: {
    grass: [['chittik', 9, 11, 20], ['fuzzling', 9, 11, 20], ['sporra', 10, 12, 20], ['burrlet', 10, 12, 15], ['mantipule', 12, 13, 5], ['glowick', 10, 12, 10], ['nyxen', 11, 12, 10]],
    night: [['echirp', 10, 12, 25], ['pookit', 10, 12, 20], ['nyxen', 11, 13, 20], ['mothlume', 12, 13, 5], ['glowick', 10, 12, 15], ['hushling', 10, 12, 15]],
  },
  saltreach: {
    water: [['gullip', 13, 16, 45], ['crabbit', 13, 16, 30], ['jellume', 14, 16, 25]],
  },
  route3: {
    grass: [['gullip', 15, 18, 25], ['trotter', 15, 18, 15], ['pebbling', 15, 18, 20], ['pugnet', 16, 18, 15], ['voltquill', 16, 18, 15], ['crabbit', 15, 18, 10]],
    night: [['echirp', 15, 18, 25], ['pookit', 16, 18, 20], ['pebbling', 15, 18, 20], ['hushling', 16, 18, 20], ['pugnet', 16, 18, 15]],
    water: [['gullip', 16, 19, 40], ['crabbit', 16, 19, 30], ['jellume', 17, 20, 25], ['stormgull', 21, 22, 5]],
  },
  coldforge_mines: {
    cave: [['pebbling', 17, 20, 25], ['tunnip', 17, 20, 25], ['ferrite', 18, 21, 15], ['echirp', 17, 20, 20], ['oozelet', 18, 21, 10], ['coilbit', 19, 21, 5]],
    water: [['crabbit', 18, 21, 70], ['oozelet', 18, 21, 30]],
  },
  route4: {
    grass: [['omenet', 24, 27, 20], ['lambkin', 24, 27, 20], ['sporra', 24, 27, 15], ['trotter', 24, 26, 10], ['voltquill', 25, 27, 15], ['cairnite', 26, 28, 5], ['pugnet', 25, 27, 15]],
    night: [['echirp', 24, 27, 20], ['pookit', 25, 28, 20], ['hushling', 25, 28, 20], ['omenet', 25, 27, 15], ['cairnite', 26, 28, 10], ['nyxen', 25, 27, 15]],
    water: [['jellume', 25, 28, 40], ['gullip', 25, 28, 40], ['oozelet', 25, 28, 20]],
  },
  hollowmere: {
    water: [['jellume', 27, 30, 35], ['gullip', 27, 30, 35], ['crabbit', 27, 30, 20], ['medusheen', 30, 31, 10]],
  },
  route5: {
    grass: [['fuzzling', 28, 30, 15], ['mothlume', 29, 31, 10], ['omenet', 28, 31, 20], ['hushling', 28, 31, 20], ['lambkin', 28, 30, 15], ['chillcub', 29, 31, 10], ['flurrit', 30, 32, 10]],
    night: [['mothlume', 29, 31, 20], ['hushling', 28, 31, 25], ['vesperel', 30, 32, 10], ['pookit', 28, 31, 25], ['chillcub', 29, 31, 20]],
    water: [['gullip', 27, 30, 30], ['jellume', 27, 30, 25], ['crabbit', 27, 30, 20], ['stormgull', 29, 31, 15], ['medusheen', 30, 31, 10]],
  },
  frostspire: {
    water: [['crabbit', 32, 35, 50], ['jellume', 32, 35, 50]],
  },
  route6: {
    grass: [['chillcub', 33, 36, 20], ['flurrit', 33, 36, 15], ['lambkin', 33, 35, 15], ['rammoth', 35, 37, 5], ['pebbling', 33, 35, 10], ['cragmaul', 35, 37, 10], ['wyrmkin', 34, 36, 10], ['glowick', 33, 36, 15]],
    night: [['chillcub', 33, 36, 20], ['duskwing', 34, 37, 15], ['cairnite', 34, 37, 15], ['vesperel', 35, 37, 15], ['wyrmkin', 34, 36, 15], ['blazewing', 35, 37, 20]],
  },
  abyssal_rift: {
    cave: [['wyrmkin', 40, 43, 20], ['wyrmguard', 42, 45, 10], ['cairnite', 40, 43, 15], ['borebeast', 40, 43, 15], ['ferroclad', 41, 44, 10], ['vesperel', 40, 43, 15], ['duskwing', 40, 43, 15]],
    water: [['medusheen', 40, 44, 40], ['pincerock', 40, 44, 30], ['stormgull', 40, 44, 30]],
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
