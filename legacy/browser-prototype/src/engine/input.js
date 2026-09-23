// Keyboard input manager — press (single-frame) and down (held) tracking.
// Exports: Input

const PRESS_KEYS = new Set(["e", " ", "enter", "escape", "backspace"]);
const MOVE_KEYS = {
  arrowup:    "up",
  w:          "up",
  arrowdown:  "down",
  s:          "down",
  arrowleft:  "left",
  a:          "left",
  arrowright: "right",
  d:          "right",
};

export class Input {
  constructor() {
    this.down    = new Set();
    this.pressed = new Set();

    window.addEventListener("keydown", (event) => {
      const key = event.key.toLowerCase();
      this.down.add(key);
      this.pressed.add(key);
      if (MOVE_KEYS[key] || PRESS_KEYS.has(key)) {
        event.preventDefault();
      }
    });

    window.addEventListener("keyup", (event) => {
      this.down.delete(event.key.toLowerCase());
    });
  }

  endFrame() {
    this.pressed.clear();
  }

  wasPressed(...keys) {
    return keys.some((k) => this.pressed.has(k));
  }

  // Returns true while the key is physically held down
  isDown(key) {
    return this.down.has(key);
  }

  getMoveDirection() {
    for (const [key, direction] of Object.entries(MOVE_KEYS)) {
      if (this.down.has(key)) {
        return direction;
      }
    }
    return null;
  }
}
