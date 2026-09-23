import Phaser from 'phaser';
import { GAME_W, GAME_H } from './config.js';
import { input } from './core/input.js';
import { audio } from './core/audio.js';
import { G } from './core/state.js';
import { BootScene } from './scenes/BootScene.js';
import { PreloadScene } from './scenes/PreloadScene.js';
import { TitleScene } from './scenes/TitleScene.js';
import { IntroScene } from './scenes/IntroScene.js';
import { WorldScene } from './scenes/WorldScene.js';
import { UIScene } from './scenes/UIScene.js';
import { MenuScene } from './scenes/MenuScene.js';
import { BattleScene } from './scenes/BattleScene.js';
import { EvolutionScene } from './scenes/EvolutionScene.js';
import { TransitionScene } from './scenes/TransitionScene.js';
import { CreditsScene } from './scenes/CreditsScene.js';
import { createMon, healMon } from './battle/mon.js';
import * as stateMod from './core/state.js';

const config = {
  type: Phaser.AUTO,
  parent: 'game',
  width: GAME_W,
  height: GAME_H,
  backgroundColor: '#0c0b14',
  pixelArt: true,
  roundPixels: true,
  antialias: false,
  scale: { mode: Phaser.Scale.NONE, zoom: 1 },
  audio: { disableWebAudio: false },
  input: { gamepad: false },
  fps: { target: 60, smoothStep: true },
  scene: [BootScene, PreloadScene, TitleScene, IntroScene, WorldScene, BattleScene, EvolutionScene, MenuScene, TransitionScene, CreditsScene, UIScene],
};

input.setBindings(G.settings.keys);
const game = new Phaser.Game(config);
window.__tiamat = { game, G, input, createMon, healMon, state: stateMod };
audio.init(game);

// Global per-frame input sampling (before any scene updates).
game.events.on(Phaser.Core.Events.PRE_STEP, (time) => input.update(time));

// Phones: if the screen is upright (the phone is held upright, or auto-rotate is off so the screen
// never turns), turn the whole game sideways so it fills the screen when the phone is held landscape.
// Which way the phone is tipped (from the motion sensor), so the sideways game is never upside down.
let tilt = 90;
function layout() {
  const vw = window.innerWidth, vh = window.innerHeight;
  const rot = !!input.isTouch && vh > vw;
  document.documentElement.classList.toggle('rot', rot);
  input.rotated = rot ? tilt : 0;
  const app = document.getElementById('app');
  if (app) {
    app.style.width = rot ? `${vh}px` : '';
    app.style.height = rot ? `${vw}px` : '';
    app.style.transform = !rot ? '' : tilt > 0 ? `translateX(${vw}px) rotate(90deg)` : `translateY(${vh}px) rotate(-90deg)`;
  }
  return rot ? [vh, vw] : [vw, vh];
}
if (input.isTouch && 'DeviceMotionEvent' in window) {
  window.addEventListener('devicemotion', (e) => {
    const g = e.accelerationIncludingGravity;
    if (!g || g.x == null || Math.abs(g.x) < 6 || Math.abs(g.x) < Math.abs(g.y || 0)) { return; }
    const t = g.x > 0 ? 90 : -90;   // right edge up → turn the game clockwise; left edge up → anticlockwise
    if (t !== tilt) { tilt = t; if (input.rotated) { fit(); } }
  });
}

// Integer (pixel-perfect) or fill scaling.
function fit() {
  const [w, h] = layout();
  const canvas = game.canvas;
  if (!canvas) { return; }
  let scale = Math.min(w / GAME_W, h / GAME_H);
  // Whole-number scaling keeps pixels perfectly square on big screens; on phones (where it would
  // leave the game tiny) fill the screen instead — their high pixel density keeps it crisp.
  if ((G.settings.scaling || 'pixel') === 'pixel' && scale >= 2 && !input.isTouch) { scale = Math.floor(scale); }
  canvas.style.width = `${Math.round(GAME_W * scale)}px`;
  canvas.style.height = `${Math.round(GAME_H * scale)}px`;
  game.scale.refresh();
}
window.addEventListener('resize', fit);
window.addEventListener('orientationchange', () => { fit(); setTimeout(fit, 300); });
if (window.visualViewport) { window.visualViewport.addEventListener('resize', fit); }
layout();

// On the first tap, ask for full screen + landscape (Android turns the screen even with auto-rotate
// off). Browsers that refuse just keep the sideways layout above.
if (input.isTouch) {
  let asked = false;
  const goLandscape = () => {
    if (asked) { return; }
    asked = true;
    const lock = () => { try { const p = screen.orientation && screen.orientation.lock && screen.orientation.lock('landscape'); if (p && p.catch) { p.catch(() => {}); } } catch { /* unsupported */ } };
    const el = document.documentElement;
    const installed = window.matchMedia('(display-mode: fullscreen), (display-mode: standalone)').matches;
    if (!installed && !document.fullscreenElement && el.requestFullscreen) {
      el.requestFullscreen({ navigationUI: 'hide' }).then(lock, () => {}).finally(() => setTimeout(fit, 300));
    } else { lock(); }
  };
  // pointerup/touchend count as a user gesture for touch (pointerdown does not)
  window.addEventListener('pointerup', goLandscape, true);
  window.addEventListener('touchend', goLandscape, true);
}
game.events.once(Phaser.Core.Events.READY, () => { fit(); const b = document.getElementById('boot'); if (b) { b.remove(); } });
window.__fit = fit;

// Installable web app: cache the whole game for offline play (production builds only).
if (import.meta.env.PROD && 'serviceWorker' in navigator && (location.protocol === 'https:' || location.hostname === 'localhost' || location.hostname === '127.0.0.1')) {
  window.addEventListener('load', () => { navigator.serviceWorker.register('./sw.js').catch((e) => console.warn('[sw]', e)); });
  // A new version was just downloaded: if we're still on the title screen, switch to it straight away
  // (otherwise it's used next time the game is opened, so no unsaved progress is lost).
  const hadController = !!navigator.serviceWorker.controller;
  let reloading = false;
  navigator.serviceWorker.addEventListener('controllerchange', () => {
    if (!hadController || reloading) { return; }
    if (game.scene.isActive('Title')) { reloading = true; location.reload(); }
  });
}
