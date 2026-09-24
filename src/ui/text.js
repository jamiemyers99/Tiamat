// Bitmap text helpers using the generated Tiamat pixel fonts.
// Faces: 'main' (line height 12) and 'small' (line height 7).
// Colours: white, dark, gold, red, green, blue, gray, ink.

export function txt(scene, x, y, str, opts = {}) {
  const face = opts.face || 'main';
  const color = opts.color || 'white';
  const t = scene.add.bitmapText(Math.round(x), Math.round(y), `${face}_${color}`, String(str ?? ''));
  if (opts.origin !== undefined) {
    const o = Array.isArray(opts.origin) ? opts.origin : [opts.origin, 0];
    t.setOrigin(o[0], o[1]);
  }
  if (opts.align === 'center') { t.setOrigin(0.5, 0); }
  if (opts.align === 'right') { t.setOrigin(1, 0); }
  if (opts.scale) { t.setScale(opts.scale); }
  if (opts.depth !== undefined) { t.setDepth(opts.depth); }
  if (opts.scroll === false) { t.setScrollFactor(0); }
  return t;
}

// Recolour an existing bitmap text by swapping its font.
export function recolor(t, color, face) {
  const f = face || t.font.split('_')[0];
  t.setFont(`${f}_${color}`);
  return t;
}

const widthCache = {};

function charWidths(scene, fontKey) {
  if (widthCache[fontKey]) { return widthCache[fontKey]; }
  const data = scene.cache.bitmapFont.get(fontKey).data;
  const map = {};
  for (const code in data.chars) { map[code] = data.chars[code].xAdvance; }
  widthCache[fontKey] = map;
  return map;
}

export function measure(scene, str, face = 'main') {
  const w = charWidths(scene, `${face}_white`);
  let x = 0;
  for (const ch of String(str)) { x += w[ch.charCodeAt(0)] ?? 4; }
  return x;
}

// Word-wrap into lines that fit maxWidth. '\n' forces a line break.
export function wrap(scene, str, maxWidth, face = 'main') {
  const lines = [];
  for (const para of String(str).split('\n')) {
    const words = para.split(' ');
    let line = '';
    for (const word of words) {
      const test = line ? `${line} ${word}` : word;
      if (measure(scene, test, face) > maxWidth && line) {
        lines.push(line);
        line = word;
      } else {
        line = test;
      }
    }
    lines.push(line);
  }
  return lines;
}

// Control names for the device in use ({BTN:run} → 'RUN' on a phone, 'Shift' on a keyboard).
// main.js plugs in input.hint so this file stays free of browser-only imports.
let hintFn = (a) => a;
let keyboardFn = () => false;
export function setHintProvider(fn, isKeyboard) { hintFn = fn; if (isKeyboard) { keyboardFn = isKeyboard; } }
export function fmtKeys(str) {
  return String(str)
    .replace(/\{BTN:(\w+)\}/g, (_, a) => hintFn(a))
    .replaceAll('{KEYNOTE}', keyboardFn() ? ' You can change any key under Controls in the menu.' : '');
}

// Fill in {PLAYER}, {RIVAL}, {BTN:…} etc.
export function fmt(str, state) {
  return fmtKeys(String(str)
    .replaceAll('{PLAYER}', state.player.name)
    .replaceAll('{RIVAL}', state.rivalName || 'Wren'));
}
