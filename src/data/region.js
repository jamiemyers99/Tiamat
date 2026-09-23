// Region map points (pixel coords on the 400×240 region map image).
// `tier`: how far into the adventure an area is (0 = Rootmere … 7 = the Riven). Drives difficulty.
// `fly`: towns you can Wing Whistle to once visited (arrival read from the map's `fly` property).
export const REGION = {
  points: [
    { id: 'rootmere', tier: 0, name: 'Rootmere', x: 60, y: 204, town: true, fly: 'rootmere', desc: 'A quiet farming village. Home.', maps: ['rootmere', 'home_1f', 'home_2f', 'marsh_lab', 'wren_house', 'rootmere_cottage'] },
    { id: 'route1', tier: 0, name: 'Route 1 · Mossway', x: 60, y: 170, desc: 'Meadows and gentle ledges.', maps: ['route1'] },
    { id: 'brindlewood', tier: 0, name: 'Brindlewood', x: 60, y: 132, town: true, fly: 'brindlewood', desc: 'A woodland town. Moss Trial.', maps: ['brindlewood', 'brindlewood_haven', 'brindlewood_trial', 'brindlewood_house', 'brindlewood_posy'] },
    { id: 'route2', tier: 1, name: 'Route 2 · Bramble Bridge', x: 102, y: 132, desc: 'A river crossing east of Brindlewood.', maps: ['route2'] },
    { id: 'thornwild', tier: 1, name: 'Thornwild', x: 146, y: 130, desc: 'An old, dark forest with a forgotten shrine.', maps: ['thornwild'] },
    { id: 'saltreach', tier: 2, name: 'Saltreach', x: 150, y: 194, town: true, fly: 'saltreach', desc: 'A fishing port. Tide Trial.', maps: ['saltreach', 'saltreach_haven', 'saltreach_trial', 'saltreach_house', 'saltreach_net', 'saltreach_lighthouse'] },
    { id: 'route3', tier: 2, name: 'Route 3 · Gullcliff Road', x: 196, y: 194, desc: 'Sea cliffs. The road east is blocked.', maps: ['route3'] },
    { id: 'coldforge', tier: 3, name: 'Coldforge Mines', x: 226, y: 172, desc: 'Old mines under the hills.', maps: ['coldforge_mines'] },
    { id: 'gearhollow', tier: 3, name: 'Gearhollow', x: 252, y: 150, town: true, fly: 'gearhollow', desc: 'A town of forges and clockwork. Spark Trial.', maps: ['gearhollow', 'gearhollow_haven', 'gearhollow_trial', 'gearhollow_ironworks', 'gearhollow_house', 'gearhollow_store'] },
    { id: 'route4', tier: 4, name: 'Route 4 · Moorwind Way', x: 252, y: 112, desc: 'Foggy moorland and standing stones.', maps: ['route4'] },
    { id: 'hollowmere', tier: 4, name: 'Hollowmere', x: 252, y: 76, town: true, fly: 'hollowmere', desc: 'A lakeside town in the fog. Veil Trial.', maps: ['hollowmere', 'hollowmere_haven', 'hollowmere_trial', 'hollowmere_archive', 'hollowmere_house'] },
    { id: 'route5', tier: 5, name: 'Route 5 · Glasslake Crossing', x: 202, y: 64, desc: 'A wide, clear lake. Boat needed.', maps: ['route5'] },
    { id: 'frostspire', tier: 5, name: 'Frostspire', x: 150, y: 40, town: true, fly: 'frostspire', desc: 'A mountain town in the snow. Rime Trial.', maps: ['frostspire', 'frostspire_haven', 'frostspire_trial', 'frostspire_lodge', 'frostspire_house'] },
    { id: 'route6', tier: 6, name: 'Route 6 · Rimepass', x: 246, y: 30, desc: 'A snowy pass down to the Riven.', maps: ['route6'] },
    { id: 'riftgate', tier: 6, name: 'Riftgate', x: 336, y: 44, town: true, fly: 'riftgate', desc: 'The city on the lip of the Riven. Wyrm Trial.', maps: ['riftgate', 'riftgate_haven', 'riftgate_trial', 'riftgate_house', 'sunken_chapel', 'spire_crown'] },
    { id: 'riven', tier: 7, name: 'The Riven', x: 364, y: 104, desc: 'The wound that never closed.', maps: ['abyssal_rift', 'cradle'] },
  ],
  locate(mapId) {
    for (const p of this.points) { if (p.maps.includes(mapId)) { return p.id; } }
    const base = mapId.split('_')[0];
    const hit = this.points.find((p) => p.id === base);
    return hit ? hit.id : null;
  },
};
