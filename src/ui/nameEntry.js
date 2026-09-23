// On-screen keyboard for names and nicknames. Works with arrows/pad and physical typing.
import { GAME_W } from '../config.js';
import { input } from '../core/input.js';
import { audio } from '../core/audio.js';
import { txt } from './text.js';
import { panel } from './widgets.js';

const ROWS = ['ABCDEFGHIJ', 'KLMNOPQRST', "UVWXYZ-'. ", 'abcdefghij', 'klmnopqrst', 'uvwxyz!?  '];

/**
 * @param scene   Phaser scene to draw in
 * @param opts    { title, initial, max, owner, randomNames, allowEmpty, depth }
 * @returns       the entered name; '' when allowEmpty and cleared; null when cancelled on an empty name
 */
export function nameEntry(scene, opts = {}) {
  const { title = '', initial = '', max = 10, owner, randomNames = null, allowEmpty = false, depth = 50 } = opts;
  const c = scene.add.container(0, 0).setDepth(depth);
  c.add(panel(scene, 60, 30, 360, 190, 'dark'));
  if (title) { c.add(txt(scene, GAME_W / 2, 38, title, { align: 'center', color: 'gray', face: 'small' })); }
  const nameTxt = txt(scene, GAME_W / 2, 52, '', { align: 'center', color: 'gold', scale: 2 });
  c.add(nameTxt);
  ROWS.forEach((r, y) => [...r].forEach((ch, x) => {
    c.add(txt(scene, 96 + x * 30, 90 + y * 16, ch === ' ' ? '' : ch, { align: 'center' }));
  }));
  const extra = [
    { label: randomNames ? 'Random' : 'Clear', x: 96, y: 192 },
    { label: 'Delete', x: 196, y: 192 },
    { label: 'Done', x: 300, y: 192 },
  ];
  extra.forEach((e) => { e.t = txt(scene, e.x, e.y, e.label, { color: 'blue' }); c.add(e.t); });
  const cur = scene.add.rectangle(0, 0, 22, 14).setStrokeStyle(1, 0xffd65c).setOrigin(0.5, 0);
  c.add(cur);
  let name = initial;
  let cx = 0, cy = 0;
  const draw = () => {
    nameTxt.setText(name + (name.length < max ? '_' : ''));
    if (cy < ROWS.length) { cur.setSize(22, 14).setPosition(96 + cx * 30, 88 + cy * 16); }
    else { const e = extra[cx]; cur.setSize(e.t.width + 8, 14).setPosition(e.x + e.t.width / 2, e.y - 2); }
  };
  draw();
  const nav = (d) => input.nav(d, owner);
  const pressed = (k) => input.pressed(k, owner);
  return new Promise((resolve) => {
    const done = (value) => {
      input.textListener = null;
      scene.events.off('update', tick);
      c.destroy();
      input.clear();
      resolve(value);
    };
    const finish = () => {
      let v = name.trim();
      if (!v && randomNames) { v = randomNames[Math.floor(Math.random() * randomNames.length)]; }
      if (!v && !allowEmpty) { audio.sfx('cancel'); return; }
      audio.sfx('select');
      done(v);
    };
    input.textListener = (e) => {
      if (e.key.length === 1 && /[A-Za-z0-9'\-.!?]/.test(e.key)) {
        if (name.length < max) { name += e.key; audio.sfx('cursor'); draw(); }
        return true;
      }
      if (e.key === ' ') { if (name.length && name.length < max) { name += ' '; draw(); } return true; }
      if (e.key === 'Backspace') { name = name.slice(0, -1); draw(); return true; }
      if (e.key === 'Enter') { finish(); return true; }
      if (e.key === 'Escape') { if (!name) { done(null); } else { name = ''; draw(); } return true; }
      return false;
    };
    const tick = () => {
      if (nav('left')) { cx = cy < ROWS.length ? (cx + 9) % 10 : (cx + 2) % 3; audio.sfx('cursor'); draw(); }
      else if (nav('right')) { cx = cy < ROWS.length ? (cx + 1) % 10 : (cx + 1) % 3; audio.sfx('cursor'); draw(); }
      else if (nav('up')) { cy = (cy + ROWS.length) % (ROWS.length + 1); if (cy === ROWS.length) { cx = Math.min(2, Math.floor(cx / 4)); } audio.sfx('cursor'); draw(); }
      else if (nav('down')) { cy = (cy + 1) % (ROWS.length + 1); if (cy === ROWS.length) { cx = Math.min(2, Math.floor(cx / 4)); } audio.sfx('cursor'); draw(); }
      else if (pressed('confirm')) {
        if (cy < ROWS.length) {
          const ch = ROWS[cy][cx];
          if (ch !== ' ' && name.length < max) { name += ch; audio.sfx('select'); }
        } else if (cx === 0) { name = randomNames ? randomNames[Math.floor(Math.random() * randomNames.length)] : ''; audio.sfx('select'); }
        else if (cx === 1) { name = name.slice(0, -1); audio.sfx('cancel'); }
        else { finish(); return; }
        draw();
      } else if (pressed('cancel')) {
        if (!name && !randomNames) { audio.sfx('cancel'); done(null); return; }
        name = name.slice(0, -1); draw();
      }
    };
    scene.events.on('update', tick);
  });
}
