// Procedurally drawn UI textures (panels, cursors, bars, emotes).
// Everything is drawn pixel-by-pixel on canvases at boot so the UI stays crisp.

export const PANEL_STYLES = {
  // bg, border, inner highlight, shadow
  dark:   ['#1b1e33', '#5c679e', '#2c3257', '#0b0c16'],
  deep:   ['#141627', '#3d4470', '#1f2340', '#07070e'],
  light:  ['#f4f1e8', '#8a7f6a', '#ffffff', '#3a3444'],
  gold:   ['#2a2438', '#e2b64a', '#3a3250', '#0b0c16'],
  red:    ['#321a26', '#e25a64', '#44202f', '#0b0c16'],
  teal:   ['#15282e', '#4fc7b8', '#1d3a40', '#07070e'],
  sel:    ['#2f3a66', '#ffd65c', '#3d4a80', '#0b0c16'],
  ghost:  ['#1b1e33', '#3d4470', '#22264a', '#0b0c16'],
};

function hexToRgb(h) {
  const n = parseInt(h.slice(1), 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}

function makeCanvas(scene, key, w, h, draw) {
  if (scene.textures.exists(key)) { return; }
  const tex = scene.textures.createCanvas(key, w, h);
  const ctx = tex.getContext();
  const img = ctx.createImageData(w, h);
  const px = (x, y, c, a = 255) => {
    if (x < 0 || y < 0 || x >= w || y >= h) { return; }
    const [r, g, b] = typeof c === 'string' ? hexToRgb(c) : c;
    const i = (y * w + x) * 4;
    img.data[i] = r; img.data[i + 1] = g; img.data[i + 2] = b; img.data[i + 3] = a;
  };
  draw(px, w, h);
  ctx.putImageData(img, 0, 0);
  tex.refresh();
}

// 16×16 nine-slice source with 5px rounded corners.
function panelTex(scene, key, style, alpha = 240) {
  const [bg, border, hi, shadow] = PANEL_STYLES[style];
  makeCanvas(scene, key, 16, 16, (px, w, h) => {
    const R = 4;
    const inside = (x, y, inset) => {
      const x0 = inset, y0 = inset, x1 = w - 1 - inset, y1 = h - 1 - inset;
      if (x < x0 || y < y0 || x > x1 || y > y1) { return false; }
      const r = Math.max(0, R - inset);
      const cx = x < x0 + r ? x0 + r : (x > x1 - r ? x1 - r : x);
      const cy = y < y0 + r ? y0 + r : (y > y1 - r ? y1 - r : y);
      const dx = x - cx, dy = y - cy;
      return dx * dx + dy * dy <= r * r + r * 0.6;
    };
    for (let y = 0; y < h; y++) {
      for (let x = 0; x < w; x++) {
        if (!inside(x, y, 0)) { continue; }
        if (!inside(x, y, 1)) { px(x, y, shadow, 255); continue; }
        if (!inside(x, y, 2)) { px(x, y, border, 255); continue; }
        if (!inside(x, y, 3) && y < h / 2) { px(x, y, hi, alpha); continue; }
        px(x, y, bg, alpha);
      }
    }
  });
}

export function buildSkin(scene) {
  for (const s of Object.keys(PANEL_STYLES)) {
    panelTex(scene, `panel_${s}`, s, 255);
  }
  // cursor arrow ▶ (7×9)
  makeCanvas(scene, 'cursor', 7, 9, (px) => {
    const rows = ['o......', 'oo.....', 'ogo....', 'oggo...', 'ogggo..', 'oggo...', 'ogo....', 'oo.....', 'o......'];
    rows.forEach((r, y) => [...r].forEach((c, x) => { if (c === 'o') { px(x, y, '#2a1a08'); } else if (c === 'g') { px(x, y, '#ffd65c'); } }));
  });
  // advance arrow ▼ (7×5)
  makeCanvas(scene, 'advance', 7, 5, (px) => {
    const rows = ['ggggggg', '.ggggg.', '..ggg..', '...g...', '.......'];
    rows.forEach((r, y) => [...r].forEach((c, x) => { if (c === 'g') { px(x, y, '#ffd65c'); px(x, y + 1, '#2a1a08'); } }));
    rows.forEach((r, y) => [...r].forEach((c, x) => { if (c === 'g') { px(x, y, '#ffd65c'); } }));
  });
  // 1×1 white pixel
  makeCanvas(scene, 'px', 1, 1, (px) => px(0, 0, '#ffffff'));
  // soft radial light (64×64) used by lighting + glows
  makeCanvas(scene, 'glow', 64, 64, (px, w, h) => {
    for (let y = 0; y < h; y++) {
      for (let x = 0; x < w; x++) {
        const d = Math.hypot(x + 0.5 - 32, y + 0.5 - 32) / 32;
        if (d < 1) {
          const a = Math.pow(1 - d, 1.6);
          px(x, y, '#ffffff', Math.round(a * 255));
        }
      }
    }
  });
  // hard-edged, dithered light for a pixel look (64×64)
  makeCanvas(scene, 'glow_px', 64, 64, (px, w, h) => {
    const bayer = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5];
    for (let y = 0; y < h; y++) {
      for (let x = 0; x < w; x++) {
        const d = Math.hypot(x + 0.5 - 32, y + 0.5 - 32) / 32;
        if (d >= 1) { continue; }
        const t = 1 - d;
        const lv = t > 0.66 ? 255 : t > 0.4 ? 190 : t > 0.2 ? 120 : 60;
        const thr = bayer[(y % 4) * 4 + (x % 4)] / 16;
        const a = (t * 3) % 1 > thr ? Math.min(255, lv + 60) : lv;
        px(x, y, '#ffffff', a);
      }
    }
  });
  // emotes 12×12
  const emote = (key, rows, col) => makeCanvas(scene, key, 12, 13, (px) => {
    const bubble = ['..oooooooo..', '.owwwwwwwwo.', 'owwwwwwwwwwo', 'owwwwwwwwwwo', 'owwwwwwwwwwo', 'owwwwwwwwwwo',
      'owwwwwwwwwwo', 'owwwwwwwwwwo', 'owwwwwwwwwwo', '.owwwwwwwwo.', '..ooowwoooo.', '....owo.....', '.....o......'];
    bubble.forEach((r, y) => [...r].forEach((c, x) => { if (c === 'o') { px(x, y, '#1c1a28'); } else if (c === 'w') { px(x, y, '#ffffff'); } }));
    rows.forEach((r, y) => [...r].forEach((c, x) => { if (c === '#') { px(x + 2, y + 2, col); } }));
  });
  emote('emote_!', ['...##...', '...##...', '...##...', '...##...', '........', '...##...', '........'], '#e23a3a');
  emote('emote_?', ['..####..', '.#....#.', '.....##.', '...##...', '........', '...##...', '........'], '#3a6ae2');
  emote('emote_...', ['........', '........', '........', '........', '#..#..#.', '........', '........'], '#3a3848');
  emote('emote_heart', ['.##..##.', '########', '########', '.######.', '..####..', '...##...', '........'], '#e2555f');
  emote('emote_note', ['...####.', '...#..#.', '...#..#.', '...#..#.', '.###.##.', '.##.###.', '........'], '#2aa19a');
  emote('emote_angry', ['.#....#.', '..#..#..', '........', '..#..#..', '.#....#.', '........', '........'], '#e2555f');
  // shadow ellipse 12×4
  makeCanvas(scene, 'shadow', 12, 4, (px) => {
    const rows = ['..######..', '##########', '##########', '..######..'];
    rows.forEach((r, y) => [...r].forEach((c, x) => { if (c === '#') { px(x + 1, y, '#101018', 80); } }));
  });
  // bars: 1px tall gradient strips for HP/XP (drawn with tint in code)
  makeCanvas(scene, 'bar', 4, 4, (px) => {
    for (let y = 0; y < 4; y++) { for (let x = 0; x < 4; x++) { px(x, y, y === 0 ? '#ffffff' : (y === 3 ? '#9a9aa8' : '#e4e4ec')); } }
  });
  // particles
  makeCanvas(scene, 'p_dot', 3, 3, (px) => { px(1, 0, '#fff'); px(0, 1, '#fff'); px(1, 1, '#fff'); px(2, 1, '#fff'); px(1, 2, '#fff'); });
  makeCanvas(scene, 'p_sq', 2, 2, (px) => { px(0, 0, '#fff'); px(1, 0, '#fff'); px(0, 1, '#fff'); px(1, 1, '#fff'); });
  makeCanvas(scene, 'p_star', 5, 5, (px) => { [[2, 0], [2, 1], [0, 2], [1, 2], [2, 2], [3, 2], [4, 2], [2, 3], [2, 4]].forEach(([x, y]) => px(x, y, '#fff')); });
  makeCanvas(scene, 'p_rain', 1, 6, (px) => { for (let y = 0; y < 6; y++) { px(0, y, '#cfe6ff', 90 + y * 25); } });
  makeCanvas(scene, 'p_snow', 2, 2, (px) => { px(0, 0, '#ffffff'); px(1, 0, '#ffffff', 180); px(0, 1, '#ffffff', 180); px(1, 1, '#e8f0ff', 120); });
  makeCanvas(scene, 'p_leaf', 4, 3, (px) => { px(0, 1, '#d8883a'); px(1, 0, '#e8a04a'); px(1, 1, '#c8702a'); px(2, 1, '#e8a04a'); px(3, 2, '#a85a2a'); });
  makeCanvas(scene, 'p_ring', 9, 9, (px) => {
    for (let y = 0; y < 9; y++) { for (let x = 0; x < 9; x++) { const d = Math.hypot(x - 4, y - 4); if (d > 3 && d < 4.4) { px(x, y, '#ffffff'); } } }
  });
  // fog texture 128×128 tileable
  makeCanvas(scene, 'fog', 128, 128, (px, w, h) => {
    const rnd = (x, y) => { const s = Math.sin(x * 12.9898 + y * 78.233) * 43758.5453; return s - Math.floor(s); };
    const val = (x, y) => {
      let v = 0, amp = 0.5, f = 4;
      for (let o = 0; o < 4; o++) {
        const gx = (x / w) * f, gy = (y / h) * f;
        const x0 = Math.floor(gx), y0 = Math.floor(gy);
        const tx = gx - x0, ty = gy - y0;
        const sm = (t) => t * t * (3 - 2 * t);
        const g = (i, j) => rnd(((i % f) + f) % f, ((j % f) + f) % f + o * 17);
        const a = g(x0, y0) * (1 - sm(tx)) + g(x0 + 1, y0) * sm(tx);
        const b = g(x0, y0 + 1) * (1 - sm(tx)) + g(x0 + 1, y0 + 1) * sm(tx);
        v += amp * (a * (1 - sm(ty)) + b * sm(ty));
        amp *= 0.5; f *= 2;
      }
      return v;
    };
    for (let y = 0; y < h; y++) { for (let x = 0; x < w; x++) { const v = val(x, y); px(x, y, '#dfe6f0', Math.max(0, Math.min(255, Math.round((v - 0.35) * 420)))); } }
  });
}
