// Unified input: keyboard, gamepad and touch mapped to logical actions.
// Scenes read input through a focus stack so only the top-most UI reacts.

// Default keyboard bindings: action → up to two keys (KeyboardEvent.key, lower-cased).
export const DEFAULT_KEYS = {
  up: ['arrowup', 'w'],
  down: ['arrowdown', 's'],
  left: ['arrowleft', 'a'],
  right: ['arrowright', 'd'],
  confirm: ['z', 'enter'],
  cancel: ['x', 'backspace'],
  menu: ['c', 'escape'],
  run: ['shift', null],
  info: ['f', null],
};
// Keys that always work, whatever the player binds (so nobody can lock themselves out).
const FIXED_KEYS = {
  ' ': 'confirm', e: 'confirm', q: 'cancel', tab: 'menu', r: 'info',
  pageup: 'pageup', pagedown: 'pagedown', f1: 'debug', '`': 'debug',
};
export const REBINDABLE = ['up', 'down', 'left', 'right', 'confirm', 'cancel', 'menu', 'run', 'info'];
export const ESSENTIAL = ['up', 'down', 'left', 'right', 'confirm', 'cancel', 'menu'];
// The menu key doubles as cancel inside menus.
const ALSO = { menu: ['cancel'] };

const ACTIONS = ['up', 'down', 'left', 'right', 'confirm', 'cancel', 'menu', 'run', 'info', 'pageup', 'pagedown', 'debug'];
const DIRS = ['up', 'down', 'left', 'right'];

// Human-readable key names for the controls screen.
export function keyName(k) {
  if (!k) { return '—'; }
  const names = {
    arrowup: 'Up', arrowdown: 'Down', arrowleft: 'Left', arrowright: 'Right', ' ': 'Space', enter: 'Enter',
    escape: 'Esc', backspace: 'Bksp', shift: 'Shift', control: 'Ctrl', alt: 'Alt', tab: 'Tab', meta: 'Meta',
    delete: 'Del', insert: 'Ins', home: 'Home', end: 'End', capslock: 'Caps',
  };
  if (names[k]) { return names[k]; }
  return k.length === 1 ? k.toUpperCase() : k.charAt(0).toUpperCase() + k.slice(1);
}

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
    // presses that started since the last frame — so a quick tap or key flick is never missed
    this.latched = new Set();
    this.lastDirOrder = [];
    this.textListener = null;
    this.captureListener = null;
    this.rotated = 0;   // 0, 90 or -90: how far main.js has turned the game on an upright screen
    this.setBindings(DEFAULT_KEYS);
    window.addEventListener('keydown', (e) => {
      const k = e.key.toLowerCase();
      if (this.captureListener) { e.preventDefault(); const cb = this.captureListener; this.captureListener = null; cb(k); return; }
      if (this.textListener && this.textListener(e)) { e.preventDefault(); return; }
      const act = this.keymap[k];
      if (act) {
        e.preventDefault();
        this.keysDown.add(act);
        (ALSO[act] || []).forEach((a) => this.keysDown.add(a));
        if (!e.repeat) { this.latched.add(act); (ALSO[act] || []).forEach((a) => this.latched.add(a)); }
        if (DIRS.includes(act)) { this.lastDirOrder = this.lastDirOrder.filter((d) => d !== act); this.lastDirOrder.push(act); }
      }
    });
    window.addEventListener('keyup', (e) => {
      const act = this.keymap[e.key.toLowerCase()];
      if (act) {
        this.keysDown.delete(act);
        (ALSO[act] || []).forEach((a) => this.keysDown.delete(a));
      }
    });
    window.addEventListener('blur', () => { this.keysDown.clear(); this.touchDown.clear(); });
    this._setupTouch();
  }

  // Apply keyboard bindings ({ action: [key, key] }); missing actions fall back to the defaults.
  setBindings(bind) {
    const b = {};
    for (const a of REBINDABLE) { b[a] = (bind && Array.isArray(bind[a]) ? bind[a] : DEFAULT_KEYS[a]).slice(0, 2); }
    this.bindings = b;
    this.keymap = { ...FIXED_KEYS };
    for (const a of REBINDABLE) { for (const k of b[a]) { if (k) { this.keymap[k] = a; } } }
    this.keysDown.clear();
  }

  // Grab the very next key press (for the controls screen).
  captureKey() { return new Promise((resolve) => { this.captureListener = resolve; }); }

  _setupTouch() {
    const root = document.getElementById('touch');
    if (!root) { return; }
    const isTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
    this.isTouch = isTouch;
    if (isTouch) { root.classList.add('on'); document.documentElement.classList.add('touch'); }
    const buzz = () => { try { if (navigator.vibrate) { navigator.vibrate(8); } } catch { /* not supported */ } };
    // D-pad: one finger steers; slide between arrows without lifting.
    const pad = root.querySelector('.pad');
    if (pad) {
      const arrows = { up: pad.querySelector('.u'), down: pad.querySelector('.d'), left: pad.querySelector('.l'), right: pad.querySelector('.r') };
      let pointer = null, cur = null;
      const setDir = (d) => {
        if (d === cur) { return; }
        if (cur) { this.touchDown.delete(cur); arrows[cur]?.classList.remove('down'); }
        cur = d;
        if (d) {
          this.touchDown.add(d);
          this.latched.add(d);
          this.lastDirOrder = this.lastDirOrder.filter((x) => x !== d);
          this.lastDirOrder.push(d);
          arrows[d]?.classList.add('down');
          buzz();
        }
      };
      const dirAt = (e) => {
        const r = pad.getBoundingClientRect();
        let dx = e.clientX - (r.left + r.width / 2), dy = e.clientY - (r.top + r.height / 2);
        // game turned sideways on an upright screen (see main.js): screen → game directions
        if (this.rotated === 90) { [dx, dy] = [dy, -dx]; } else if (this.rotated === -90) { [dx, dy] = [-dy, dx]; }
        if (Math.hypot(dx, dy) < r.width * 0.1) { return cur; }
        return Math.abs(dx) > Math.abs(dy) ? (dx > 0 ? 'right' : 'left') : (dy > 0 ? 'down' : 'up');
      };
      pad.addEventListener('pointerdown', (e) => {
        e.preventDefault();
        pointer = e.pointerId;
        try { pad.setPointerCapture(e.pointerId); } catch { /* ignore */ }
        setDir(dirAt(e));
      });
      pad.addEventListener('pointermove', (e) => { if (e.pointerId === pointer) { e.preventDefault(); setDir(dirAt(e)); } });
      const end = (e) => { if (e.pointerId === pointer) { pointer = null; setDir(null); } };
      pad.addEventListener('pointerup', end);
      pad.addEventListener('pointercancel', end);
      pad.addEventListener('lostpointercapture', end);
    }
    root.querySelectorAll('.btn[data-k]').forEach((el) => {
      const k = el.dataset.k;
      const on = (ev) => { ev.preventDefault(); this.touchDown.add(k); this.latched.add(k); el.classList.add('down'); buzz(); };
      const off = (ev) => { ev.preventDefault(); this.touchDown.delete(k); el.classList.remove('down'); };
      el.addEventListener('pointerdown', on);
      el.addEventListener('pointerup', off);
      el.addEventListener('pointercancel', off);
      el.addEventListener('pointerleave', off);
    });
    // Stop long-press menus and pinch-zoom on the game.
    window.addEventListener('contextmenu', (e) => { if (isTouch) { e.preventDefault(); } });
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
    this.down = new Set([...this.keysDown, ...this.touchDown, ...this.padDown, ...this.latched]);
    this.latched.clear();
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
