// Full-screen move picker, used whenever a Morph learns or changes a move: level-ups in battle,
// evolution, Tech Discs and the Move Reminder. Like the classics it shows every move's type,
// category, power, accuracy, PP and what it does, so you can see what you're giving up.
import { GAME_W, GAME_H } from '../config.js';
import { input } from '../core/input.js';
import { audio } from '../core/audio.js';
import { MOVES } from '../data/moves.js';
import { SPECIES } from '../data/species.js';
import { TYPE_COLORS } from '../data/types.js';
import { monName, monFrame } from '../battle/mon.js';
import { txt, wrap, measure } from './text.js';
import { panel } from './widgets.js';

const CAT_NAME = { phys: 'Physical', spec: 'Special', status: 'Status' };
const ROW_H = 24;

/**
 * pickMove(scene, mon, opts) → Promise
 *  opts.title      prompt shown at the top
 *  opts.newMove    learn mode: the move being learned (listed last, marked NEW);
 *                  resolves with the index (0-3) of the move to forget, or -1 to not learn it
 *  opts.choices    list mode: move ids to choose from; resolves with the chosen id, or null
 *  opts.owner      input owner (the calling scene's)
 */
export function pickMove(scene, mon, opts = {}) {
  const owner = opts.owner || scene.owner;
  const learnMode = !!opts.newMove;
  const rows = learnMode
    ? [...mon.moves.map((m, i) => ({ id: m.id, pp: m.pp, max: m.max, value: i })), { id: opts.newMove, pp: MOVES[opts.newMove].pp, max: MOVES[opts.newMove].pp, value: -1, isNew: true }]
    : opts.choices.map((id) => ({ id, pp: MOVES[id].pp, max: MOVES[id].pp, value: id }));
  const myTypes = SPECIES[mon.species].types;
  const c = scene.add.container(0, 0).setDepth(opts.depth || 5000).setScrollFactor(0);   // works over any scene
  c.add(scene.add.rectangle(0, 0, GAME_W, GAME_H, 0x0b0c16, 0.94).setOrigin(0, 0));
  // header: who is learning
  c.add(panel(scene, 8, 6, GAME_W - 16, 34, 'dark'));
  c.add(scene.add.image(28, 23, 'mons', monFrame(mon, 'i')));
  c.add(txt(scene, 48, 10, `${monName(mon)}  Lv${mon.level}`, { color: 'gold' }));
  myTypes.forEach((t, k) => c.add(scene.add.image(48 + k * 37, 24, 'ui', `type_${t}`).setOrigin(0, 0)));
  const titleLines = wrap(scene, opts.title || '', 300, 'small');
  titleLines.slice(0, 2).forEach((l, k) => c.add(txt(scene, GAME_W - 16, 12 + k * 10, l, { face: 'small', align: 'right' })));
  // left: the list
  const listX = 10, listY = 46, listW = 222;
  const visible = Math.min(rows.length, 8);
  c.add(panel(scene, listX - 2, listY - 2, listW + 4, visible * ROW_H + 6, 'dark'));
  const cells = [];
  for (let k = 0; k < visible; k++) {
    const y = listY + k * ROW_H;
    const bg = scene.add.rectangle(listX + 2, y + 1, listW - 4, ROW_H - 2, 0x3a3f58, 0.5).setOrigin(0, 0);
    const badge = scene.add.image(listX + 6, y + 4, 'ui', 'type_Plain').setOrigin(0, 0);
    const cat = scene.add.image(listX + 6, y + 14, 'ui', 'cat_phys').setOrigin(0, 0);
    const nm = txt(scene, listX + 46, y + 3, '');
    const sub = txt(scene, listX + 46, y + 14, '', { face: 'small', color: 'gray' });
    const tag = txt(scene, listX + listW - 6, y + 3, '', { face: 'small', align: 'right', color: 'gold' });
    const pp = txt(scene, listX + listW - 6, y + 14, '', { face: 'small', align: 'right', color: 'gray' });
    c.add([bg, badge, cat, nm, sub, tag, pp]);
    cells.push({ bg, badge, cat, nm, sub, tag, pp, y });
  }
  const sel = scene.add.rectangle(0, 0, listW - 2, ROW_H).setOrigin(0, 0).setStrokeStyle(2, 0xffd65c);
  c.add(sel);
  const up = scene.add.image(listX + listW / 2, listY - 6, 'advance').setFlipY(true);
  const dn = scene.add.image(listX + listW / 2, listY + visible * ROW_H + 7, 'advance');
  c.add([up, dn]);
  // right: details of the highlighted move
  const dX = 244, dY = 46, dW = GAME_W - dX - 10;
  c.add(panel(scene, dX - 2, dY - 2, dW + 4, 190, 'deep'));
  const dName = txt(scene, dX + 6, dY + 4, '', { color: 'gold' });
  const dType = scene.add.image(dX + 6, dY + 18, 'ui', 'type_Plain').setOrigin(0, 0);
  const dCat = scene.add.image(dX + 43, dY + 18, 'ui', 'cat_phys').setOrigin(0, 0);
  const dCatName = txt(scene, dX + 60, dY + 18, '', { face: 'small', color: 'gray' });
  const stats = [0, 1, 2].map((k) => [txt(scene, dX + 6 + k * 72, dY + 32, ['POWER', 'ACCURACY', 'PP'][k], { face: 'small', color: 'blue' }), txt(scene, dX + 6 + k * 72, dY + 41, '')]);
  const stab = txt(scene, dX + 6, dY + 56, '', { face: 'small', color: 'gold' });
  const desc = [0, 1, 2, 3, 4, 5, 6].map((k) => txt(scene, dX + 6, dY + 68 + k * 13, ''));
  c.add([dName, dType, dCat, dCatName, stab, ...desc, ...stats.flat()]);
  const hint = txt(scene, GAME_W / 2, GAME_H - 14, learnMode ? 'A: forget the highlighted move    B: don\'t learn' : 'A: choose    B: back', { face: 'small', align: 'center', color: 'gray' });
  c.add(hint);

  let i = learnMode ? rows.length - 1 : 0;   // start on the new move
  let scroll = 0;
  const draw = () => {
    if (i < scroll) { scroll = i; }
    if (i >= scroll + visible) { scroll = i - visible + 1; }
    cells.forEach((cell, k) => {
      const r = rows[scroll + k];
      const mv = r && MOVES[r.id];
      [cell.bg, cell.badge, cell.cat, cell.nm, cell.sub, cell.tag, cell.pp].forEach((o) => o.setVisible(!!mv));
      if (!mv) { return; }
      cell.bg.setFillStyle(TYPE_COLORS[mv.type], r.isNew ? 0.45 : 0.25);
      cell.badge.setFrame(`type_${mv.type}`);
      cell.cat.setFrame(`cat_${mv.cat}`);
      const long = measure(scene, mv.name) > 118;
      cell.nm.setText(mv.name).setFont(long ? 'small_white' : 'main_white');
      cell.sub.setText(mv.cat === 'status' ? 'STATUS' : `POW ${mv.power || '-'}  ACC ${mv.acc ?? '-'}`);
      cell.tag.setText(r.isNew ? 'NEW' : '');
      cell.pp.setText(`PP ${r.pp}/${r.max}`);
    });
    sel.setPosition(listX + 1, listY + (i - scroll) * ROW_H);
    up.setVisible(scroll > 0);
    dn.setVisible(scroll + visible < rows.length);
    const r = rows[i];
    const mv = MOVES[r.id];
    dName.setText(mv.name + (r.isNew ? '  (new)' : ''));
    dType.setFrame(`type_${mv.type}`);
    dCat.setFrame(`cat_${mv.cat}`);
    dCatName.setText(CAT_NAME[mv.cat] || '');
    stats[0][1].setText(mv.cat === 'status' ? '-' : String(mv.power || '-'));
    stats[1][1].setText(mv.acc == null ? 'Never misses' : `${mv.acc}%`);
    stats[2][1].setText(`${r.pp}/${r.max}`);
    stab.setText(mv.cat !== 'status' && myTypes.includes(mv.type) ? `SAME TYPE BONUS x1.5 (${myTypes.join('/')} Morph)` : '');
    const lines = wrap(scene, mv.desc || '', dW - 12);
    desc.forEach((d, k) => d.setText(lines[k] || ''));
  };
  draw();
  return new Promise((resolve) => {
    const tick = () => {
      if (input.nav('up', owner)) { i = (i + rows.length - 1) % rows.length; audio.sfx('cursor'); draw(); }
      else if (input.nav('down', owner)) { i = (i + 1) % rows.length; audio.sfx('cursor'); draw(); }
      else if (input.pressed('confirm', owner)) { audio.sfx('select'); finish(rows[i].value); }
      else if (input.pressed('cancel', owner)) { audio.sfx('cancel'); finish(learnMode ? -1 : null); }
    };
    const finish = (v) => { scene.events.off('update', tick); c.destroy(); resolve(v); };
    scene.events.on('update', tick);
  });
}
