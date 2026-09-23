// Wild encounter tables per map. Each entry: [species, minLv, maxLv, weight]
// grass: tall grass by day · night: tall grass 20:00–05:00 · water: while using the Skiff · cave: any floor tile
import { timeOfDay } from '../core/time.js';

export const ENCOUNTERS = {
  route1: {
    grass: [['nibbit', 2, 4, 35], ['beakling', 2, 4, 30], ['trotter', 3, 4, 20], ['burrlet', 3, 5, 10], ['chittik', 3, 4, 5]],
    night: [['nibbit', 2, 4, 35], ['hushling', 3, 5, 20], ['pookit', 3, 5, 20], ['burrlet', 3, 5, 15], ['beakling', 2, 3, 10]],
  },
  route2: {
    grass: [['chittik', 8, 11, 25], ['fuzzling', 8, 11, 20], ['beakling', 9, 11, 20], ['burrlet', 9, 12, 15], ['nibbit', 9, 11, 15], ['sporra', 10, 12, 5]],
    night: [['fuzzling', 9, 12, 25], ['hushling', 9, 12, 20], ['pookit', 9, 12, 20], ['glowick', 10, 12, 15], ['nibbit', 9, 11, 20]],
    water: [['puddlet', 10, 14, 15], ['gullip', 10, 14, 60], ['jellume', 12, 15, 25]],
  },
  thornwild: {
    grass: [['chittik', 10, 13, 20], ['fuzzling', 10, 13, 20], ['sporra', 11, 14, 20], ['burrlet', 11, 14, 15], ['mantipule', 13, 15, 5], ['glowick', 11, 14, 10], ['nyxen', 12, 14, 10]],
    night: [['echirp', 11, 14, 25], ['pookit', 11, 14, 20], ['nyxen', 12, 15, 20], ['mothlume', 14, 15, 5], ['glowick', 11, 14, 15], ['hushling', 11, 14, 15]],
  },
  saltreach: {
    water: [['gullip', 14, 18, 45], ['crabbit', 14, 18, 30], ['jellume', 15, 18, 25]],
  },
  route3: {
    grass: [['gullip', 16, 19, 25], ['trotter', 16, 19, 15], ['pebbling', 16, 19, 20], ['pugnet', 17, 20, 15], ['voltquill', 17, 20, 15], ['crabbit', 16, 19, 10]],
    night: [['echirp', 16, 19, 25], ['pookit', 17, 20, 20], ['pebbling', 16, 19, 20], ['hushling', 17, 20, 20], ['pugnet', 17, 20, 15]],
    water: [['gullip', 17, 21, 40], ['crabbit', 17, 21, 30], ['jellume', 18, 22, 25], ['stormgull', 22, 24, 5]],
  },
  coldforge_mines: {
    cave: [['pebbling', 18, 21, 25], ['tunnip', 18, 21, 25], ['ferrite', 19, 22, 15], ['echirp', 18, 21, 20], ['oozelet', 19, 22, 10], ['coilbit', 20, 22, 5]],
    water: [['crabbit', 19, 22, 70], ['oozelet', 19, 22, 30]],
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
    water: [['gullip', 28, 32, 30], ['jellume', 28, 32, 25], ['crabbit', 28, 32, 20], ['stormgull', 30, 33, 15], ['medusheen', 31, 33, 10]],
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
