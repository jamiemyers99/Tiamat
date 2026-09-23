# V16 Audit — apply audio pack v2

## §2 Engine registration
- [x] SFX_FILES extended with 8 v2 entries (ui_move, world_door, battle_super_effective, battle_capture_success, battle_capture_fail, level_up path updated, evolve path updated, heal)
- [x] BGM_FILES extended with 4 v2 entries (route_outdoor, interior_house, interior_centre, battle_trial)
- [x] No v1 entry renamed or removed (menu_move, menu_confirm, menu_back, capture, capture_success, battle_start, level_up key, evolve key all retained)
- [x] ui_move 40ms throttle centralised in audio.js playSfx

## §3 BGM map
- [x] MAP_BGM updated: player_home/house_a-e → interior_house; healing_centre/town_shop/morph_lab → interior_centre; brindlewood_centre/brindlewood_shop → interior_centre
- [x] route_1 and route_2 → route_outdoor
- [x] Trial battle BGM wired via getBattleBgm() helper in App.js, not via MAP_BGM
- [x] trial_arena set to null (silence on entry); battle_trial fires on Mossa's battle start via getBattleBgm()
- [x] brindlewood still using town_brindlewood (flagged for future — no distinct track provided in v2 pack)

## §4 SFX wiring
- [x] ui_move replaces menu_move at every cursor-navigation call site: BattleScreen, PauseScreen (all sub-screens), MoveLearnPrompt, StorageScreen
- [x] world_door fires at start of every map transition via App.js changeMap() and whiteout respawn in endBattle()
- [x] battle_super_effective layers ~100ms after battle_hit, only when enemy took damage and log contains "Super effective!" (damage-only; miss/0× immunity handled by enemy HP check)
- [x] battle_capture_success on capture success — final wobble does not play battle_capture_pulse (pulse skipped when remaining reaches 0)
- [x] battle_capture_fail on capture fail
- [x] level_up plays once per level gained; currently applyExperience returns levelled boolean — single call in App.js endBattle (multi-level spacing not implemented — applyExperience only reports one level per call; flagged below)
- [x] evolve plays at scene start (_advance); BGM fades out on EvolutionScene.start(), resumes in App.js onDone callback
- [x] heal plays once per heal action: App.js healParty() (bed + centre), BattleScreen._healPlayer(), BattleScreen._cureStatus(), PauseScreen bag potion use
- [x] capture_success call site renamed to battle_capture_success; grep returns no stragglers

## §5 OptionsScreen
- [x] BGM slider applies to currently playing track in real time — audio.applySettings() called immediately in PauseScreen.updateOptions() on volume change; _applyVolumes() updates _bgmGain instantly

## §6 v15 gap-fill
- [x] world_step 80ms throttle confirmed in movement.js
- [x] Tab-visibility ducking confirmed in audio.js (visibilitychange listener on _bgmGain)
- [x] Pause-menu BGM ducks to 30% via setBgmDuck(true) in App.js enterPause(), restored in resumeGame()

## Flagged for future passes
- [ ] Brindlewood needs distinct town theme (currently shares town_brindlewood from v15 — no v2 track provided)
- [ ] No rival/trainer-specific battle theme yet (battle_trainer used for all non-trial trainers)
- [ ] No victory jingle (post-battle summary screen plays nothing)
- [ ] level_up: applyExperience returns a single `levelled` boolean — multi-level spacing (250ms apart per level) requires applyExperience to report level count; deferred to v17 when xp.js is refactored
