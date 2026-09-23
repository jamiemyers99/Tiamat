// audio.js — Web Audio API engine with master/bgm/sfx gain chain, crossfade BGM, deferred init.
// Exports: default audio

const SFX_FILES = {
  // UI (v2)
  ui_move:                "audio/sfx/ui/sfx_ui_move.wav",
  // World (v2)
  world_step:             "audio/sfx/world/sfx_world_step.wav",
  world_encounter:        "audio/sfx/world/sfx_world_encounter.wav",
  world_door:             "audio/sfx/world/sfx_world_door.wav",
  // Battle (v2)
  battle_attack:          "audio/sfx/battle/sfx_battle_attack.wav",
  battle_hit:             "audio/sfx/battle/sfx_battle_hit.wav",
  battle_morph_faint:     "audio/sfx/battle/sfx_battle_morph_faint.wav",
  battle_super_effective: "audio/sfx/battle/sfx_battle_super_effective.wav",
  battle_capture_pulse:   "audio/sfx/battle/sfx_battle_capture_pulse.wav",
  battle_capture_success: "audio/sfx/battle/sfx_battle_capture_success.wav",
  battle_capture_fail:    "audio/sfx/battle/sfx_battle_capture_fail.wav",
  capture:                "audio/sfx/battle/sfx_battle_capture_pulse.wav",
  // System (v2)
  level_up:               "audio/sfx/system/sfx_system_level_up.wav",
  evolve:                 "audio/sfx/system/sfx_system_evolve.wav",
  heal:                   "audio/sfx/system/sfx_system_heal.wav",
};

const BGM_FILES = {
  // Town / overworld
  rootmere_theme:   "audio/bgm/rootmere/bgm_rootmere_theme.wav",
  route_outdoor:    "audio/bgm/route/bgm_route_outdoor.wav",
  // Interiors
  interior_house:   "audio/bgm/interior/bgm_interior_house.wav",
  interior_centre:  "audio/bgm/interior/bgm_interior_centre.wav",
  // Battle
  battle_basic:     "audio/bgm/battle/bgm_battle_basic.wav",
  battle_trial:     "audio/bgm/battle/bgm_battle_trial.wav",
};

// ── State ────────────────────────────────────────────────────────────────────

let _ctx           = null;
let _masterGain    = null;
let _bgmGain       = null;
let _sfxGain       = null;
let _currentBgm    = null;  // { name, source, srcGain }
let _pendingBgm    = null;  // BGM name queued before first gesture
let _bgmDucked     = false;
let _lastUiMoveMs  = 0;     // throttle for ui_move (40ms min gap)

const _vols    = { master: 0.8, bgm: 0.7, sfx: 0.9, muted: false };
const _buffers = new Map();
const _pending = new Map(); // name → Promise<ArrayBuffer|null>
const _missing = new Set();

// ── Fetch / Decode ───────────────────────────────────────────────────────────

function preload() {
  const all = { ...SFX_FILES, ...BGM_FILES };
  for (const [name, path] of Object.entries(all)) {
    _pending.set(name,
      fetch(path)
        .then((r) => (r.ok ? r.arrayBuffer() : null))
        .catch(() => null),
    );
  }
}

async function _ensureCtx() {
  if (_ctx) {
    if (_ctx.state === "suspended") { try { await _ctx.resume(); } catch { /* blocked */ } }
    return;
  }
  _ctx        = new (window.AudioContext || window.webkitAudioContext)();
  _masterGain = _ctx.createGain();
  _bgmGain    = _ctx.createGain();
  _sfxGain    = _ctx.createGain();
  _bgmGain.connect(_masterGain);
  _sfxGain.connect(_masterGain);
  _masterGain.connect(_ctx.destination);
  _applyVolumes();

  if (_ctx.state === "suspended") { try { await _ctx.resume(); } catch { /* blocked */ } }

  // Decode all pending buffers in parallel.
  await Promise.all(
    [..._pending.entries()].map(async ([name, promise]) => {
      const raw = await promise;
      if (!raw) { _logMissing(name); return; }
      try {
        _buffers.set(name, await _ctx.decodeAudioData(raw));
      } catch {
        _logMissing(name);
      }
    }),
  );
  _pending.clear();

  // Mute BGM when tab is hidden; restore when visible.
  document.addEventListener("visibilitychange", () => {
    if (!_bgmGain || !_ctx) { return; }
    _bgmGain.gain.setTargetAtTime(
      document.hidden ? 0 : _bgmTarget(),
      _ctx.currentTime,
      0.05,
    );
  });
}

function _logMissing(name) {
  if (!_missing.has(name)) {
    _missing.add(name);
    console.debug(`[audio] missing: ${name}`);
  }
}

// ── Volume helpers ───────────────────────────────────────────────────────────

function _bgmTarget() {
  return _vols.muted ? 0 : _vols.bgm * (_bgmDucked ? 0.3 : 1);
}

function _applyVolumes() {
  if (!_ctx) { return; }
  const t = _ctx.currentTime;
  _masterGain.gain.setTargetAtTime(_vols.muted ? 0 : _vols.master, t, 0.05);
  _bgmGain.gain.setTargetAtTime(_bgmTarget(), t, 0.05);
  _sfxGain.gain.setTargetAtTime(_vols.muted ? 0 : _vols.sfx, t, 0.05);
}

// ── Public API ───────────────────────────────────────────────────────────────

function init() {
  const handler = async () => {
    await _ensureCtx();
    if (_pendingBgm) {
      const name  = _pendingBgm;
      _pendingBgm = null;
      await _startBgm(name);
    }
  };
  document.addEventListener("keydown",     handler, { once: true });
  document.addEventListener("pointerdown", handler, { once: true });
}

function applySettings(settings) {
  _vols.master = settings?.audioMaster ?? 0.8;
  _vols.bgm    = settings?.audioBgm    ?? 0.7;
  _vols.sfx    = settings?.audioSfx    ?? 0.9;
  _vols.muted  = settings?.audioMuted  ?? false;
  _applyVolumes();
}

function setMasterVolume(v) { _vols.master = Math.max(0, Math.min(1, v)); _applyVolumes(); }
function setBgmVolume(v)    { _vols.bgm    = Math.max(0, Math.min(1, v)); _applyVolumes(); }
function setSfxVolume(v)    { _vols.sfx    = Math.max(0, Math.min(1, v)); _applyVolumes(); }
function setMuted(muted)    { _vols.muted  = !!muted; _applyVolumes(); }
function setBgmDuck(on)     { _bgmDucked = on; _applyVolumes(); }
function getVolumes()       { return { ..._vols }; }

function playSfx(name) {
  if (!_ctx || _ctx.state === "suspended") { return; }
  if (name === "ui_move") {
    const now = Date.now();
    if (now - _lastUiMoveMs < 40) { return; }
    _lastUiMoveMs = now;
  }
  const buf = _buffers.get(name);
  if (!buf) { _logMissing(name); return; }
  const src = _ctx.createBufferSource();
  src.buffer = buf;
  src.connect(_sfxGain);
  src.start();
}

async function playBgm(name, opts = {}) {
  if (!name) { stopBgm(opts); return; }
  if (_currentBgm?.name === name) { return; }
  if (!_ctx || _ctx.state === "suspended") {
    _pendingBgm = name;
    return;
  }
  await _startBgm(name, opts);
}

async function _startBgm(name, { fadeMs = 250 } = {}) {
  // Fade out old source via its srcGain, then disconnect.
  if (_currentBgm?.srcGain) {
    const { source, srcGain } = _currentBgm;
    srcGain.gain.setTargetAtTime(0, _ctx.currentTime, fadeMs / 3000);
    const gn = srcGain, src = source;
    setTimeout(() => { try { src?.stop(); } catch { /* stopped */ } gn?.disconnect(); }, fadeMs * 2 + 100);
  }
  _currentBgm = { name, source: null, srcGain: null };

  const buf = _buffers.get(name);
  if (!buf) { _logMissing(name); return; }

  const srcGain = _ctx.createGain();
  srcGain.gain.setValueAtTime(0, _ctx.currentTime);
  srcGain.gain.setTargetAtTime(1, _ctx.currentTime, fadeMs / 3000);
  srcGain.connect(_bgmGain);

  const source = _ctx.createBufferSource();
  source.buffer = buf;
  source.loop   = true;
  source.connect(srcGain);
  source.start();

  _currentBgm = { name, source, srcGain };
}

function stopBgm({ fadeMs = 250 } = {}) {
  if (!_currentBgm) { return; }
  if (_currentBgm.srcGain && _ctx) {
    const { source, srcGain } = _currentBgm;
    srcGain.gain.setTargetAtTime(0, _ctx.currentTime, fadeMs / 3000);
    const gn = srcGain, src = source;
    setTimeout(() => { try { src?.stop(); } catch { /* stopped */ } gn?.disconnect(); }, fadeMs * 2 + 100);
  }
  _currentBgm = null;
}

export default {
  preload,
  init,
  applySettings,
  playSfx,
  playBgm,
  stopBgm,
  setMasterVolume,
  setBgmVolume,
  setSfxVolume,
  setMuted,
  setBgmDuck,
  getVolumes,
};
