// Loads a Tiled map (.tmj) into Phaser layers and exposes collision/behaviour data.
import { TILE, DEPTH } from '../config.js';

const META = ['none', 'solid', 'water', 'grass', 'ledge_down', 'ledge_left', 'ledge_right', 'counter', 'door', 'bridge', 'noenc'];

function propsToObj(props) {
  const o = {};
  for (const p of props || []) { o[p.name] = p.value; }
  return o;
}

export class MapView {
  constructor(scene, id) {
    this.scene = scene;
    this.id = id;
    const key = `map_${id}`;
    const raw = scene.cache.tilemap.get(key);
    if (!raw) { throw new Error(`Unknown map ${id}`); }
    this.data = raw.data;
    this.props = propsToObj(this.data.properties);
    this.w = this.data.width;
    this.h = this.data.height;
    this.pw = this.w * TILE;
    this.ph = this.h * TILE;
    this.tilemap = scene.make.tilemap({ key });
    const ts = this.tilemap.addTilesetImage('world', 'tiles_world', TILE, TILE, 0, 0);
    this.layers = {};
    const depths = { ground: DEPTH.ground, decor: DEPTH.decor, above: DEPTH.above };
    for (const name of ['ground', 'decor', 'above']) {
      const l = this.tilemap.createLayer(name, ts, 0, 0);
      l.setDepth(depths[name]);
      this.layers[name] = l;
    }
    // behaviours from the meta layer
    const metaLayer = this.data.layers.find((l) => l.name === 'meta');
    const metaTs = this.data.tilesets.find((t) => t.name === 'meta');
    this.meta = new Array(this.w * this.h).fill('none');
    if (metaLayer) {
      metaLayer.data.forEach((gid, i) => {
        if (gid >= metaTs.firstgid) { this.meta[i] = META[gid - metaTs.firstgid] || 'none'; }
      });
    }
    // objects
    const objLayer = this.data.layers.find((l) => l.type === 'objectgroup');
    this.objects = (objLayer ? objLayer.objects : []).map((o) => ({
      id: o.id,
      name: o.name,
      type: o.type || o.class,
      x: Math.floor(o.x / TILE),
      y: Math.floor(o.y / TILE),
      px: o.x, py: o.y,
      w: Math.max(1, Math.round(o.width / TILE)),
      h: Math.max(1, Math.round(o.height / TILE)),
      props: propsToObj(o.properties),
    }));
    this.lights = this.objects.filter((o) => o.type === 'light');
    // animated tiles
    this.anims = [];
    const worldTs = this.data.tilesets.find((t) => t.name === 'world');
    const animDefs = {};
    for (const t of worldTs.tiles || []) {
      if (t.animation) { animDefs[t.id + worldTs.firstgid] = t.animation.map((f) => f.tileid + worldTs.firstgid); }
    }
    const ground = this.layers.ground;
    for (let y = 0; y < this.h; y++) {
      for (let x = 0; x < this.w; x++) {
        const tile = ground.getTileAt(x, y);
        if (tile && animDefs[tile.index]) { this.anims.push({ tile, frames: animDefs[tile.index] }); }
      }
    }
    this.animFrame = 0;
    this.animTimer = 0;
  }

  update(delta) {
    if (!this.anims.length) { return; }
    this.animTimer += delta;
    if (this.animTimer >= 240) {
      this.animTimer -= 240;
      this.animFrame = (this.animFrame + 1) % 4;
      for (const a of this.anims) { a.tile.index = a.frames[this.animFrame % a.frames.length]; }
    }
  }

  inBounds(x, y) { return x >= 0 && y >= 0 && x < this.w && y < this.h; }
  behavior(x, y) { return this.inBounds(x, y) ? this.meta[y * this.w + x] : 'solid'; }
  setBehavior(x, y, b) { if (this.inBounds(x, y)) { this.meta[y * this.w + x] = b; } }

  objectsAt(x, y, type) {
    return this.objects.filter((o) => (!type || o.type === type) && x >= o.x && x < o.x + o.w && y >= o.y && y < o.y + o.h);
  }

  get name() { return this.props.name || this.id; }
  get outdoor() { return this.props.kind !== 'interior' && this.props.light !== 'dark'; }

  destroy() {
    this.tilemap.destroy();
  }
}
