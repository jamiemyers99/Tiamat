// Unified input: keyboard, gamepad and touch mapped to logical actions.
// Scenes read input through a focus stack so only the top-most UI reacts.

const KEYMAP = {
  arrowup: 'up', w: 'up',
  arrowdown: 'down', s: 'down',
  arrowleft: 'left', a: 'left',
  arrowright: 'right', d: 'right',
  z: 'confirm', e: 'confirm', ' ': 'confirm', enter: 'confirm',
  x: 'cancel', backspace: 'cancel', q: 'cancel',
  escape: 'menu', tab: 'menu', c: 'menu',
  shift: 'run',
  f: 'info', r: 'info',
  pageup: 'pageup', pagedown: 'pagedown',
  f1: 'debug', '`': 'debug',
};
// Escape doubles as cancel inside menus.
const ALSO = { menu: ['cancel'] };

const ACTIONS = ['up', 'down', 'left', 'right', 'confirm', 'cancel', 'menu', 'run', 'info', 'pageup', 'pagedown', 'debug'];
const DIRS = ['up', 'down', 'left', 'right'];

class InputManager {
  constructor() {
    this.down = new Set();
    this.prev = new Set();
    this.pressedSet = new Set();
    this.repeatAt = {};
    this.focus = ['world'];
    this.keysDown = new Set();
    this.touchDown = new Set();
    this.padDown = new Set();
    this.lastDirOrder = [];
    this.textListener = null;
    window.addEventListener('keydown', (e) => {
      const k = e.key.toLowerCase();
      if (this.textListener && this.textListener(e)) { e.preventDefault(); return; }
      const act = KEYMAP[k];
      if (act) {
        e.preventDefault();
        this.keysDown.add(act);
        (ALSO[act] || []).forEach((a) => this.keysDown.add(a));
        if (DIRS.includes(act)) { this.lastDirOrder = this.lastDirOrder.filter((d) => d !== act); this.lastDirOrder.push(act); }
      }
    });
    window.addEventListener('keyup', (e) => {
      const act = KEYMAP[e.key.toLowerCase()];
      if (act) {
        this.keysDown.delete(act);
        (ALSO[act] || []).forEach((a) => this.keysDown.delete(a));
      }
    });
    window.addEventListener('blur', () => { this.keysDown.clear(); this.touchDown.clear(); });
    this._setupTouch();
  }

  _setupTouch() {
    const root = document.getElementById('touch');
    if (!root) { return; }
    const isTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
    if (isTouch) { root.classList.add('on'); }
    root.querySelectorAll('[data-k]').forEach((el) => {
      const k = el.dataset.k;
      const on = (ev) => { ev.preventDefault(); this.touchDown.add(k); if (DIRS.includes(k)) { this.lastDirOrder = this.lastDirOrder.filter((d) => d !== k); this.lastDirOrder.push(k); } };
      const off = (ev) => { ev.preventDefault(); this.touchDown.delete(k); };
      el.addEventListener('pointerdown', on);
      el.addEventListener('pointerup', off);
      el.addEventListener('pointercancel', off);
      el.addEventListener('pointerleave', off);
    });
  }

  _pollPad() {
    this.padDown.clear();
    const pads = navigator.getGamepads ? navigator.getGamepads() : [];
    for (const p of pads) {
      if (!p) { continue; }
      const b = (i) => p.buttons[i] && p.buttons[i].pressed;
      const ax = p.axes[0] || 0, ay = p.axes[1] || 0;
      if (b(12) || ay < -0.5) { this.padDown.add('up'); }
      if (b(13) || ay > 0.5) { this.padDown.add('down'); }
      if (b(14) || ax < -0.5) { this.padDown.add('left'); }
      if (b(15) || ax > 0.5) { this.padDown.add('right'); }
      if (b(0)) { this.padDown.add('confirm'); }
      if (b(1)) { this.padDown.add('cancel'); }
      if (b(9)) { this.padDown.add('menu'); }
      if (b(2) || b(7)) { this.padDown.add('run'); }
      if (b(3)) { this.padDown.add('info'); }
      if (b(4)) { this.padDown.add('pageup'); }
      if (b(5)) { this.padDown.add('pagedown'); }
    }
  }

  // Called once per frame before scenes update.
  update(time) {
    this._pollPad();
    this.prev = this.down;
    this.down = new Set([...this.keysDown, ...this.touchDown, ...this.padDown]);
    this.pressedSet.clear();
    for (const a of ACTIONS) {
      if (this.down.has(a) && !this.prev.has(a)) {
        this.pressedSet.add(a);
        this.repeatAt[a] = time + 380;
      } else if (this.down.has(a) && DIRS.includes(a) && time >= (this.repeatAt[a] || Infinity)) {
        this.pressedSet.add(a + ':repeat');
        this.repeatAt[a] = time + 90;
      }
    }
  }

  // ── focus stack ──
  push(name) { this.focus.push(name); this.pressedSet.clear(); }
  pop(name) {
    const i = this.focus.lastIndexOf(name);
    if (i >= 0) { this.focus.splice(i, 1); }
    this.pressedSet.clear();
  }
  top() { return this.focus[this.focus.length - 1]; }
  has(name) { return this.top() === name; }

  // Was action pressed this frame (for the given focus owner)?
  pressed(action, owner) {
    if (owner && this.top() !== owner) { return false; }
    return this.pressedSet.has(action);
  }
  // Pressed or auto-repeating (for menu cursor movement).
  nav(action, owner) {
    if (owner && this.top() !== owner) { return false; }
    return this.pressedSet.has(action) || this.pressedSet.has(action + ':repeat');
  }
  isDown(action, owner) {
    if (owner && this.top() !== owner) { return false; }
    return this.down.has(action);
  }
  heldDir(owner) {
    if (owner && this.top() !== owner) { return null; }
    for (let i = this.lastDirOrder.length - 1; i >= 0; i--) {
      if (this.down.has(this.lastDirOrder[i])) { return this.lastDirOrder[i]; }
    }
    for (const d of DIRS) { if (this.down.has(d)) { return d; } }
    return null;
  }
  // Swallow everything currently held (after closing a menu, etc.)
  clear() { this.prev = new Set(this.down); this.pressedSet.clear(); }
}

export const input = new InputManager();
