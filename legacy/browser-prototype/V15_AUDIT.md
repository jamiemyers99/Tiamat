# V15 Audit — Audio Integration

Generated: 2026-04-30

---

## §1 Engine: src/engine/audio.js

- ✅ Web Audio API engine with master/bgm/sfx GainNode chain
- ✅ SFX_FILES map (menu_move/confirm/back, battle_start, capture, capture_success, evolve, world_step, world_encounter, level_up, battle_capture_pulse, battle_attack, battle_hit, battle_morph_faint)
- ✅ BGM_FILES map (town_rootmere, route_1, route_2_bridge, town_brindlewood, battle_wild, battle_trainer, battle_mossa, trial_grounds)
- ✅ preload() — kick off fetch for all clips at startup
- ✅ init() — one-shot gesture listener that creates+resumes AudioContext then decodes buffers
- ✅ playSfx(name) — synchronous; silently skips if ctx suspended or clip missing
- ✅ playBgm(name, {fadeMs}) — defers to _pendingBgm if context not ready; per-source srcGain crossfade
- ✅ stopBgm({fadeMs}) — fades out current BGM source
- ✅ applySettings(settings) — reads audioMaster/audioBgm/audioSfx/audioMuted flat keys
- ✅ setMasterVolume/setBgmVolume/setSfxVolume/setMuted — live volume control
- ✅ setBgmDuck(on) — 30% BGM volume when paused, restore on resume
- ✅ Missing clip: silent + console.debug once per name (Set-based)
- ✅ Tab visibility: visibilitychange listener mutes/restores BGM

## §2 Data: src/data/audio.js

- ✅ MAP_BGM table mapping all map IDs to BGM track names
  - rootmere/interiors/healing_centre/town_shop → town_rootmere
  - route_1 → route_1
  - route_2 → route_2_bridge
  - brindlewood/interiors → town_brindlewood
  - trial_grounds/trial_arena → trial_grounds

## §3 Save migration: src/engine/saveMigration.js

- ✅ CURRENT_SAVE_VERSION bumped 3 → 4
- ✅ _v3toV4 adds audioMaster/audioBgm/audioSfx/audioMuted defaults to settings

## §4 Boot: src/main.js

- ✅ audio.preload() called at startup
- ✅ audio.init() registers first-gesture listener

## §5 Movement: src/engine/movement.js

- ✅ world_step SFX with 80ms throttle in _tickStats

## §6 Encounter + trainer SFX: src/screens/WorldScreen.js

- ✅ world_encounter SFX in afterMove when encounter starts
- ✅ world_encounter SFX when trainer spots player (_visionFlash)
- ✅ MAP_BGM BGM lookup on changeMap not applicable (BGM on map change wired in App.js)

## §7 Battle SFX: src/screens/BattleScreen.js

- ✅ sfx import replaced with audio import
- ✅ battle_attack SFX when player confirms a move
- ✅ battle_hit SFX when damage flash triggers
- ✅ battle_morph_faint SFX when hp reaches 0 in message phase
- ✅ battle_capture_pulse SFX per wobble tick in _tickWobble
- ✅ All sfx.play → audio.playSfx

## §8 Evolution SFX: src/screens/EvolutionScene.js

- ✅ sfx import replaced with audio import
- ✅ sfx.play("evolve") → audio.playSfx("evolve")

## §9 MoveLearnPrompt SFX: src/screens/MoveLearnPrompt.js

- ✅ sfx import replaced with audio import
- ✅ sfx.play → audio.playSfx

## §10 StorageScreen SFX: src/screens/StorageScreen.js

- ✅ sfx import replaced with audio import
- ✅ sfx.play → audio.playSfx

## §11 Options + pause duck: src/screens/PauseScreen.js

- ✅ sfx import replaced with audio import
- ✅ sfx.play → audio.playSfx throughout
- ✅ OPTIONS_DEFS extended with audioMuted, audioMaster, audioBgm, audioSfx
- ✅ updateOptions handles volume options (step ±0.1, clamp 0–1)
- ✅ updateOptions live-applies audio settings on change
- ✅ renderOptions renders volume options as percentage display

## §12 BGM wiring: src/App.js

- ✅ sfx import replaced with audio import
- ✅ MAP_BGM imported from data/audio.js
- ✅ changeMap → audio.playBgm(MAP_BGM[targetMap])
- ✅ beginBattle → audio.playBgm("battle_wild")
- ✅ beginTrainerBattle → audio.playBgm("battle_trainer") or "battle_mossa" for Mossa
- ✅ endBattle → audio.playBgm(MAP_BGM[state.currentMap])
- ✅ applySave → audio.applySettings(s.settings) + audio.playBgm(MAP_BGM[map])
- ✅ enterPause → audio.setBgmDuck(true)
- ✅ resumeGame → audio.setBgmDuck(false)
- ✅ endBattle(victory) with levelled → audio.playSfx("level_up")
- ✅ Initial state settings include audioMaster/audioBgm/audioSfx/audioMuted defaults

## §13 Cache bust

- ✅ All imports updated to ?v=20260429-15
- ✅ index.html script/link tags updated to ?v=20260429-15
- ✅ src/engine/sfx.js retained as no-op stub (not deleted; backward-safe)

---

## Summary

| Section | Done | Partial | Skipped |
|---------|------|---------|---------|
| §1 audio.js engine | 14 | 0 | 0 |
| §2 MAP_BGM table | 1 | 0 | 0 |
| §3 Save migration v4 | 3 | 0 | 0 |
| §4 main.js boot | 2 | 0 | 0 |
| §5 movement step SFX | 1 | 0 | 0 |
| §6 encounter SFX | 2 | 0 | 0 |
| §7 battle SFX | 6 | 0 | 0 |
| §8 evolution SFX | 2 | 0 | 0 |
| §9 MoveLearnPrompt | 2 | 0 | 0 |
| §10 StorageScreen | 2 | 0 | 0 |
| §11 Options+duck | 7 | 0 | 0 |
| §12 BGM wiring | 11 | 0 | 0 |
| §13 Cache bust | 3 | 0 | 0 |
