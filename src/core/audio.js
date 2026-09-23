// Music + SFX manager on top of Phaser's WebAudio sound manager.
// Also synthesises a unique cry for every Morph species.
import { G } from './state.js';

class AudioManager {
  constructor() {
    this.game = null;
    this.music = null;
    this.musicKey = null;
    this.stack = [];
    this.lastSfx = {};
    this.duck = 1;
  }

  init(game) {
    this.game = game;
  }

  get sm() { return this.game.sound; }

  musicVolume() { return (G.settings.musicVol ?? 0.7) * this.duck; }
  sfxVolume() { return G.settings.sfxVol ?? 0.85; }

  playMusic(key, { fade = 400, restart = false } = {}) {
    if (!this.game) { return; }
    if (!key) { this.stopMusic(fade); return; }
    if (this.musicKey === key && this.music && this.music.isPlaying && !restart) { return; }
    if (!this.game.cache.audio.exists(key)) { console.debug('[audio] missing music', key); this.stopMusic(fade); this.musicKey = key; return; }
    const old = this.music;
    if (old) { this._fadeOut(old, fade); }
    const m = this.sm.add(key, { loop: true, volume: 0 });
    m.play();
    this._fadeTo(m, this.musicVolume(), fade);
    this.music = m;
    this.musicKey = key;
  }

  // Temporarily switch music (battles), restoring the previous track afterwards.
  pushMusic(key) {
    this.stack.push(this.musicKey);
    this.playMusic(key, { fade: 150, restart: true });
  }
  popMusic() {
    const prev = this.stack.pop();
    this.playMusic(prev, { fade: 500, restart: true });
  }

  stopMusic(fade = 400) {
    if (this.music) { this._fadeOut(this.music, fade); }
    this.music = null;
    this.musicKey = null;
  }

  // Play a short jingle over paused music, then resume.
  jingle(key) {
    return new Promise((resolve) => {
      if (!this.game || !this.game.cache.audio.exists(key)) { resolve(); return; }
      const m = this.music;
      if (m) { m.pause(); }
      const j = this.sm.add(key, { volume: this.musicVolume() });
      j.once('complete', () => { j.destroy(); if (m && this.music === m) { m.resume(); } resolve(); });
      j.play();
    });
  }

  setDuck(v) {
    this.duck = v;
    if (this.music) { this.music.setVolume(this.musicVolume()); }
  }

  refreshVolumes() {
    if (this.music) { this.music.setVolume(this.musicVolume()); }
  }

  sfx(key, { volume = 1, rate = 1, throttle = 40 } = {}) {
    if (!this.game) { return; }
    const now = performance.now();
    if (this.lastSfx[key] && now - this.lastSfx[key] < throttle) { return; }
    this.lastSfx[key] = now;
    if (!this.game.cache.audio.exists(key)) { return; }
    try { this.sm.play(key, { volume: volume * this.sfxVolume(), rate }); } catch { /* locked */ }
  }

  _fadeTo(sound, vol, ms) {
    const scene = this.game.scene.getScenes(true)[0];
    if (!scene || ms <= 0) { sound.setVolume(vol); return; }
    scene.tweens.add({ targets: sound, volume: vol, duration: ms });
  }

  _fadeOut(sound, ms) {
    const scene = this.game.scene.getScenes(true)[0];
    if (!scene || ms <= 0) { sound.stop(); sound.destroy(); return; }
    scene.tweens.add({ targets: sound, volume: 0, duration: ms, onComplete: () => { sound.stop(); sound.destroy(); } });
  }

  // ── procedural creature cries ──
  cry(speciesNum, { pitch = 1, faint = false } = {}) {
    const ctx = this.game && this.game.sound && this.game.sound.context;
    if (!ctx || ctx.state !== 'running') { return; }
    const seed = (n) => { const x = Math.sin(speciesNum * 91.7 + n * 12.9) * 43758.5453; return x - Math.floor(x); };
    const t0 = ctx.currentTime + 0.01;
    const base = 180 + seed(1) * 520;
    const dur = (0.35 + seed(2) * 0.45) * (faint ? 1.6 : 1);
    const out = ctx.createGain();
    out.gain.value = 0.0001;
    out.connect(this.game.sound.masterVolumeNode || ctx.destination);
    const vol = 0.22 * this.sfxVolume();
    out.gain.exponentialRampToValueAtTime(vol, t0 + 0.02);
    out.gain.exponentialRampToValueAtTime(vol * 0.6, t0 + dur * 0.5);
    out.gain.exponentialRampToValueAtTime(0.0001, t0 + dur);
    const types = ['square', 'sawtooth', 'triangle', 'square'];
    const voices = 1 + Math.floor(seed(3) * 2);
    for (let v = 0; v < voices; v++) {
      const osc = ctx.createOscillator();
      osc.type = types[Math.floor(seed(4 + v) * types.length)];
      const f0 = base * pitch * (v ? 1.5 + seed(9) * 0.5 : 1);
      osc.frequency.setValueAtTime(f0, t0);
      const shape = Math.floor(seed(5) * 4);
      const f1 = f0 * (faint ? 0.45 : [1.6, 0.6, 1.25, 0.8][shape]);
      osc.frequency.exponentialRampToValueAtTime(Math.max(40, f1), t0 + dur * 0.55);
      osc.frequency.exponentialRampToValueAtTime(Math.max(40, f0 * (faint ? 0.3 : 0.9 + seed(6) * 0.4)), t0 + dur);
      // vibrato
      const lfo = ctx.createOscillator();
      const lg = ctx.createGain();
      lfo.frequency.value = 6 + seed(7) * 18;
      lg.gain.value = f0 * (0.02 + seed(8) * 0.08);
      lfo.connect(lg); lg.connect(osc.frequency);
      const g = ctx.createGain();
      g.gain.value = v ? 0.35 : 1;
      const filt = ctx.createBiquadFilter();
      filt.type = 'lowpass';
      filt.frequency.value = 1800 + seed(10) * 2500;
      osc.connect(g); g.connect(filt); filt.connect(out);
      osc.start(t0); lfo.start(t0);
      osc.stop(t0 + dur + 0.05); lfo.stop(t0 + dur + 0.05);
    }
  }

  // Short synthesized UI blips for sounds we don't ship as files.
  blip(kind = 'tick') {
    const ctx = this.game && this.game.sound && this.game.sound.context;
    if (!ctx || ctx.state !== 'running') { return; }
    const t0 = ctx.currentTime + 0.005;
    const o = ctx.createOscillator();
    const g = ctx.createGain();
    const presets = {
      tick: ['square', 880, 880, 0.04, 0.06],
      bump: ['triangle', 110, 70, 0.08, 0.2],
      text: ['square', 620, 620, 0.018, 0.035],
      coin: ['square', 988, 1318, 0.12, 0.08],
      jump: ['square', 300, 700, 0.12, 0.08],
      cut: ['sawtooth', 900, 200, 0.12, 0.08],
      splash: ['triangle', 400, 90, 0.2, 0.12],
    };
    const [type, f0, f1, dur, vol] = presets[kind] || presets.tick;
    o.type = type;
    o.frequency.setValueAtTime(f0, t0);
    o.frequency.exponentialRampToValueAtTime(f1, t0 + dur);
    g.gain.setValueAtTime(vol * this.sfxVolume(), t0);
    g.gain.exponentialRampToValueAtTime(0.0001, t0 + dur);
    o.connect(g); g.connect(this.game.sound.masterVolumeNode || ctx.destination);
    o.start(t0); o.stop(t0 + dur + 0.02);
  }
}

export const audio = new AudioManager();
