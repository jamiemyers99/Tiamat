// Music + SFX manager on top of Phaser's WebAudio sound manager.
// Also synthesises a unique cry for every Morph species.
import { G } from './state.js';

// per-sound loudness trims so every effect sits at the same level in the mix
const SFX_GAIN = {};

class AudioManager {
  constructor() {
    this.game = null;
    this.music = null;
    this.musicKey = null;
    this.stack = [];
    this.lastSfx = {};
    this.duck = 1;
    this.allMusic = new Set();   // every music instance that exists, current or fading out
    this.jingling = 0;
  }

  init(game) {
    this.game = game;
  }

  // ── streaming ─────────────────────────────────────────────────────────────
  // Music files download in the background, most-needed first, and are kept compressed (≈1 MB each). A track is
  // only decoded when it's about to play, and just the last few decoded tracks are kept, so memory stays low
  // even with the whole soundtrack downloaded. A track asked for before it has arrived jumps the queue.
  startStreaming(index) {
    this.known = new Set((index && index.bgm) || []);
    this.bytes = new Map();       // key → compressed ArrayBuffer
    this.decoded = [];            // keys whose decoded audio is in the cache, oldest first
    if (this.game.cache.audio.exists('bgm_title')) { this.decoded.push('bgm_title'); }
    const first = ['rootmere', 'house', 'haven', 'route', 'battle_wild', 'battle_trainer', 'victory', 'brindlewood', 'trial',
      'battle_trial', 'battle_rival', 'route_b', 'forest', 'saltreach', 'deepcall', 'battle_deepcall', 'cave', 'gearhollow', 'moor',
      'hollowmere', 'lake', 'battle_boss', 'frostspire', 'riftgate', 'rift', 'battle_oriel', 'cradle', 'battle_legend', 'crown'];
    // (the title track was preloaded; its compressed copy is fetched last so it can be let go of later)
    this.queue = [...first, ...[...this.known].filter((k) => !first.includes(k) && k !== 'title'), 'title'].filter((k) => this.known.has(k)).map((k) => `bgm_${k}`);
    this._pump();
  }
  has(key) { return !key || !this.known || this.known.has(key.replace(/^bgm_/, '')); }
  _pump() {
    if (this._fetching || !this.queue || !this.queue.length) { return; }
    const key = this.queue.shift();
    if (this.bytes.has(key)) { this._pump(); return; }
    this._fetching = key;
    fetch(`assets/audio/bgm/${key.slice(4)}.ogg`)
      .then((r) => (r.ok ? r.arrayBuffer() : Promise.reject(new Error(r.status))))
      .then((buf) => { this.bytes.set(key, buf); })
      .catch((e) => console.warn('[audio] could not load', key, e.message))
      .finally(() => {
        this._fetching = null;
        if (this.musicKey === key && !this.music) { this.playMusic(key, { fade: 700 }); }
        setTimeout(() => this._pump(), 60);
      });
  }
  // decode a downloaded track into the sound cache (and forget the oldest decoded ones)
  _decode(key) {
    if (this._decoding === key) { return; }
    this._decoding = key;
    const ctx = this.game.sound.context;
    ctx.decodeAudioData(this.bytes.get(key).slice(0)).then((buffer) => {
      this._decoding = null;
      if (!this.game.cache.audio.exists(key)) { this.game.cache.audio.add(key, buffer); }
      this.decoded = [...this.decoded.filter((k) => k !== key), key];
      this._evict();
      if (this.musicKey === key && !this.music) { this.playMusic(key, { fade: 600 }); }
    }).catch((e) => { this._decoding = null; console.warn('[audio] could not decode', key, e && e.message); });
  }
  _evict() {
    const inUse = new Set([...this.allMusic].map((m) => m.key));
    while (this.decoded.length > 3) {
      const old = this.decoded.find((k) => !inUse.has(k) && k !== this.musicKey);
      if (!old) { break; }
      this.decoded = this.decoded.filter((k) => k !== old);
      if (this.bytes.has(old)) { this.game.cache.audio.remove(old); }
    }
  }

  get sm() { return this.game.sound; }

  musicVolume() { return (G.settings.musicVol ?? 0.7) * this.duck; }
  sfxVolume() { return G.settings.sfxVol ?? 0.85; }

  // One track at a time. Every other music instance is faded out on a timer that belongs to the audio manager
  // itself — never to a scene — so a track can't be left playing when the scene that started its fade is
  // stopped (that is how battle music used to leak into the overworld).
  playMusic(key, { fade = 400, restart = false } = {}) {
    if (!this.game) { return; }
    if (!key) { this.stopMusic(fade); return; }
    if (this.musicKey === key && this.music && (this.music.isPlaying || this.music.isPaused) && !restart) {
      if (this.music.isPaused && !this.jingling) { this.music.resume(); }
      return;
    }
    if (!this.game.cache.audio.exists(key)) {
      // not ready yet: go quiet, then start it the moment it's decoded (downloading it first if need be)
      this.stopMusic(fade);
      this.musicKey = key;
      if (this.bytes && this.bytes.has(key)) { this._decode(key); }
      else if (this.has(key) && this.queue) {
        this.queue = [key, ...this.queue.filter((k) => k !== key)];
        this._pump();
      }
      return;
    }
    if (this.decoded) { this.decoded = [...this.decoded.filter((k) => k !== key), key]; }
    this._retireAll(fade);
    const m = this.sm.add(key, { loop: true, volume: 0 });
    m.key = key;
    this.allMusic.add(m);
    if (this.jingling) { this.music = m; this.musicKey = key; return; }   // starts when the jingle ends
    m.play();
    this._setVol(m, 0);      // start silent and fade in
    this._fade(m, this.musicVolume(), fade);
    this.music = m;
    this.musicKey = key;
  }

  // Temporarily switch music, restoring the previous track afterwards.
  pushMusic(key) {
    this.stack.push(this.musicKey);
    this.playMusic(key, { fade: 150, restart: true });
  }
  popMusic() {
    const prev = this.stack.pop();
    this.playMusic(prev, { fade: 500, restart: true });
  }

  stopMusic(fade = 400) {
    this._retireAll(fade);
    this.music = null;
    this.musicKey = null;
  }

  // fade out and destroy every music instance (the current one included)
  _retireAll(fade) {
    for (const m of this.allMusic) {
      if (m._retiring) { continue; }
      m._retiring = true;
      if (!m.isPlaying || fade <= 0) { this._kill(m); continue; }
      this._fade(m, 0, fade, () => this._kill(m));
    }
  }
  _kill(m) {
    if (m._fader) { clearInterval(m._fader); m._fader = null; }
    try { m.stop(); m.destroy(); } catch { /* already gone */ }
    this.allMusic.delete(m);
    if (this.decoded) { this._evict(); }
  }

  // Play a short jingle over the paused music, then carry on.
  jingle(key) {
    return new Promise((resolve) => {
      if (!this.game || !this.game.cache.audio.exists(key)) { resolve(); return; }
      const paused = this.music && this.music.isPlaying ? this.music : null;
      if (paused) { paused.pause(); }
      this.jingling = (this.jingling || 0) + 1;
      const j = this.sm.add(key, { volume: this.musicVolume() * 1.05 });
      let done = false;
      const finish = () => {
        if (done) { return; }
        done = true;
        try { j.destroy(); } catch { /* gone */ }
        this.jingling--;
        if (!this.jingling && this.music && !this.music._retiring) {
          if (this.music.isPaused) { this.music.resume(); }
          else if (!this.music.isPlaying) { this.music.play(); this._setVol(this.music, 0); this._fade(this.music, this.musicVolume(), 300); }
        }
        resolve();
      };
      j.once('complete', finish);
      setTimeout(finish, Math.max(1000, (j.duration || 6) * 1000 + 800));   // never hang if 'complete' is lost
      j.play();
    });
  }

  setDuck(v) {
    this.duck = v;
    if (this.music && !this.music._retiring) { this._fade(this.music, this.musicVolume(), 180); }
  }

  refreshVolumes() {
    if (this.music && !this.music._retiring) { this._setVol(this.music, this.musicVolume()); }
  }

  sfx(key, { volume = 1, rate = 1, throttle = 40, detune = 0 } = {}) {
    if (!this.game) { return; }
    const now = performance.now();
    if (this.lastSfx[key] && now - this.lastSfx[key] < throttle) { return; }
    this.lastSfx[key] = now;
    if (!this.game.cache.audio.exists(key)) { return; }
    try { this.sm.play(key, { volume: volume * this.sfxVolume() * (SFX_GAIN[key] ?? 1), rate, detune }); } catch { /* locked */ }
  }

  // Volume fades run on the audio manager's own timer, independent of any scene.
  // (we keep our own copy of each track's volume: reading it back from Web Audio lags a frame, which made new
  // tracks start at full volume and fade *down* instead of fading in)
  _setVol(sound, v) { sound._vol = v; try { sound.volume = v; } catch { /* destroyed */ } }
  _fade(sound, vol, ms, onDone) {
    if (sound._fader) { clearInterval(sound._fader); sound._fader = null; }
    if (ms <= 0) { this._setVol(sound, vol); if (onDone) { onDone(); } return; }
    const from = sound._vol ?? sound.volume, t0 = performance.now();
    sound._fader = setInterval(() => {
      let k = Math.min(1, (performance.now() - t0) / ms);
      try { this._setVol(sound, from + (vol - from) * k); } catch { k = 1; }
      if (k >= 1) { clearInterval(sound._fader); sound._fader = null; if (onDone) { onDone(); } }
    }, 25);
  }

  // ── procedural creature cries ──
  // Each species gets its own voice from its number: 1–3 syllables, a pitch contour, and a vowel-like formant.
  // Soft triangle/sine voices through a formant filter and a gentle low-pass — creature-like, never buzzy.
  cry(speciesNum, { pitch = 1, faint = false } = {}) {
    const ctx = this.game && this.game.sound && this.game.sound.context;
    if (!ctx || ctx.state !== 'running') { return; }
    const seed = (n) => { const x = Math.sin(speciesNum * 91.7 + n * 12.9) * 43758.5453; return x - Math.floor(x); };
    const t0 = ctx.currentTime + 0.01;
    const out = ctx.createGain();
    out.gain.value = 0.2 * this.sfxVolume();
    const soft = ctx.createBiquadFilter();
    soft.type = 'lowpass'; soft.frequency.value = 2600; soft.Q.value = 0.5;
    out.connect(soft);
    soft.connect(this.game.sound.masterVolumeNode || ctx.destination);
    const syllables = 1 + Math.floor(seed(11) * 3);
    const base = (190 + seed(1) * 360) * pitch * (faint ? 0.85 : 1);
    const total = (0.34 + seed(2) * 0.36) * (faint ? 1.6 : 1);
    const shape = Math.floor(seed(5) * 4);          // rise-fall, fall, rise, wobble
    let end = t0;
    for (let i = 0; i < syllables; i++) {
      const len = (total / syllables) * (0.75 + seed(20 + i) * 0.3);
      const st = t0 + i * (total / syllables);
      const f0 = base * (1 + (seed(30 + i) - 0.5) * 0.25);
      const peak = f0 * (faint ? 0.95 : [1.3, 1.08, 1.22, 1.12][shape]);
      const f1 = f0 * (faint ? 0.5 : [0.85, 0.72, 1.35, 0.95][shape]);
      const g = ctx.createGain();
      g.gain.setValueAtTime(0.0001, st);
      g.gain.exponentialRampToValueAtTime(1, st + 0.03);
      g.gain.setValueAtTime(0.8, st + len * 0.6);
      g.gain.exponentialRampToValueAtTime(0.0001, st + len);
      // vowel: a band-pass formant that slides (like 'ee' to 'oo')
      const formant = ctx.createBiquadFilter();
      formant.type = 'bandpass'; formant.Q.value = 2.5;
      const fa = 650 + seed(40 + i) * 1300;
      formant.frequency.setValueAtTime(fa, st);
      formant.frequency.linearRampToValueAtTime(fa * (0.6 + seed(50 + i) * 0.9), st + len);
      const body = ctx.createGain(); body.gain.value = 0.55;
      g.connect(formant); formant.connect(out);
      g.connect(body); body.connect(out);
      const voices = [['triangle', 1, 1], ['sine', 2, 0.35], ['sine', 1.5 + seed(9) * 0.02, 0.18]];
      for (const [type, mult, amp] of voices) {
        const osc = ctx.createOscillator();
        osc.type = type;
        osc.frequency.setValueAtTime(f0 * mult, st);
        osc.frequency.exponentialRampToValueAtTime(Math.max(60, peak * mult), st + len * 0.35);
        osc.frequency.exponentialRampToValueAtTime(Math.max(50, f1 * mult), st + len);
        const lfo = ctx.createOscillator(); const lg = ctx.createGain();
        lfo.frequency.value = 5 + seed(7) * 4;
        lg.gain.value = f0 * mult * (0.012 + seed(8) * 0.02);
        lfo.connect(lg); lg.connect(osc.frequency);
        const a = ctx.createGain(); a.gain.value = amp;
        osc.connect(a); a.connect(g);
        osc.start(st); lfo.start(st); osc.stop(st + len + 0.05); lfo.stop(st + len + 0.05);
      }
      end = st + len;
    }
    // a little breath under the voice
    const n = Math.floor(ctx.sampleRate * (end - t0 + 0.1));
    const buf = ctx.createBuffer(1, n, ctx.sampleRate);
    const d = buf.getChannelData(0);
    for (let i = 0; i < n; i++) { d[i] = (Math.random() * 2 - 1) * Math.exp(-i / (ctx.sampleRate * 0.12)); }
    const src = ctx.createBufferSource(); src.buffer = buf;
    const bpf = ctx.createBiquadFilter(); bpf.type = 'bandpass'; bpf.frequency.value = 1200 + seed(60) * 1500; bpf.Q.value = 1.2;
    const bg = ctx.createGain(); bg.gain.value = 0.05;
    src.connect(bpf); bpf.connect(bg); bg.connect(out);
    src.start(t0);
  }

  // Small interface sounds. Recorded versions (tools/audio/ui_sfx.py) are used when they're loaded; the synth
  // fallback is kept soft (sine/triangle, low-passed).
  blip(kind = 'tick') {
    const file = { tick: 'cursor', text: 'ui_text', bump: 'ui_bump', coin: 'ui_coin', jump: 'ui_jump', cut: 'ui_cut', splash: 'ui_splash' }[kind];
    if (file && this.game && this.game.cache.audio.exists(file)) {
      this.sfx(file, { throttle: kind === 'text' ? 35 : 70, detune: kind === 'text' ? Math.random() * 200 - 100 : 0 });
      return;
    }
    const ctx = this.game && this.game.sound && this.game.sound.context;
    if (!ctx || ctx.state !== 'running') { return; }
    const t0 = ctx.currentTime + 0.005;
    const o = ctx.createOscillator();
    const g = ctx.createGain();
    const f = ctx.createBiquadFilter();
    f.type = 'lowpass'; f.frequency.value = 2200;
    const presets = {
      tick: ['triangle', 880, 820, 0.05, 0.05],
      bump: ['sine', 140, 70, 0.09, 0.16],
      text: ['sine', 1200, 1000, 0.018, 0.02],
      coin: ['sine', 988, 1318, 0.14, 0.07],
      jump: ['triangle', 220, 330, 0.12, 0.06],
      cut: ['triangle', 700, 300, 0.12, 0.05],
      splash: ['triangle', 400, 120, 0.2, 0.08],
    };
    const [type, f0, f1, dur, vol] = presets[kind] || presets.tick;
    o.type = type;
    o.frequency.setValueAtTime(f0, t0);
    o.frequency.exponentialRampToValueAtTime(f1, t0 + dur);
    g.gain.setValueAtTime(vol * this.sfxVolume(), t0);
    g.gain.exponentialRampToValueAtTime(0.0001, t0 + dur);
    o.connect(f); f.connect(g); g.connect(this.game.sound.masterVolumeNode || ctx.destination);
    o.start(t0); o.stop(t0 + dur + 0.02);
  }
}

export const audio = new AudioManager();
