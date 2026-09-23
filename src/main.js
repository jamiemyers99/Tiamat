import { validateTypeChart } from "./data/typeChart.js?v=20260429-19";
import { Game } from "./App.js?v=20260429-19";
import audio from "./engine/audio.js?v=20260429-19";

validateTypeChart();

audio.preload();
audio.init();

const canvas = document.getElementById("game");

if (!(canvas instanceof HTMLCanvasElement)) {
  throw new Error("Game canvas was not found.");
}

const game = new Game(canvas);
game.start();
