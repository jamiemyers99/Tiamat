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

// Integer (pixel-perfect) or fill scaling.
function fit() {
  const w = window.innerWidth, h = window.innerHeight;
  const canvas = game.canvas;
  if (!canvas) { return; }
  let scale = Math.min(w / GAME_W, h / GAME_H);
  if ((G.settings.scaling || 'pixel') === 'pixel' && scale >= 1) { scale = Math.floor(scale); }
  canvas.style.width = `${Math.round(GAME_W * scale)}px`;
  canvas.style.height = `${Math.round(GAME_H * scale)}px`;
  game.scale.refresh();
}
window.addEventListener('resize', fit);
game.events.once(Phaser.Core.Events.READY, () => { fit(); const b = document.getElementById('boot'); if (b) { b.remove(); } });
window.__fit = fit;
