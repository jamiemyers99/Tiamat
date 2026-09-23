# V17 Audit — Battle Menu Readability & Outdoor BGM Fix

## §1 BGM diagnosis

- [x] Checked MAP_BGM keys against actual map IDs (cause A) — keys match
- [x] Checked map-enter call sites and boot path (cause B) — boot fires correctly from start() and applySave()
- [x] Checked MAP_BGM values for inversion (cause C) — values not inverted
- [x] Identified actual cause: **BGM_FILES registration points to OGG files that do not exist on disk.** The v1 BGM entries (town_rootmere.ogg, route_1.ogg, battle_wild.ogg, etc.) were never packaged. Actual files are WAVs in subdirectories. The rootmere theme lives at `audio/bgm/rootmere/bgm_rootmere_theme.wav` — not registered in BGM_FILES at all. Only the four v2 entries (interior_house, interior_centre, route_outdoor, battle_trial) had correct paths, which is why only those maps produced audible BGM.
- [x] Fix applied — BGM_FILES updated to actual WAV paths; MAP_BGM keys updated to match; battle track calls updated to battle_basic
- [ ] Verified outdoor BGM plays in Rootmere
- [ ] Verified house BGM plays in Player Home
- [ ] Verified route BGM plays on Route 1
- [ ] Verified BGM persists correctly across save/reload

## §2 Smoothing & font setup

- [x] ctx.imageSmoothingEnabled = false on main canvas (App.js:49)
- [x] image-rendering: pixelated AND crisp-edges in styles.css (lines 86–87)
- [x] All text drawn at integer pixel positions via Math.round() in BattleScreen drawFightGrid/drawStatusBox
- [x] Font sizes raised to 8px minimum (was 5–7px in cells and badges)

## §3 Move grid layout

- [x] Each cell uses the 2-line layout (name+eff tag / type+PP)
- [x] Type rendered as coloured plain text, no rectangular badge background
- [x] Power removed from cells, visible in persistent info strip below grid
- [x] Empty cell shows centred "—" in dim colour
- [x] Cursor navigation unchanged — constrained to nMoves, cannot land on empty cell

## §3.2 Info strip

- [x] Persistent strip always shows highlighted move's name · type · Pow · Acc below the grid
- [x] Strong vs / Weak vs line added below when matchups exist

## §3.3 HUD strip

- [x] Player status box height +2 px (40 → 42)
- [x] Type badges absent from HUD strip (already not present; confirmed)
- [x] HP numeric uses spaced format ("2 / 13" not "2/13")

## §3.5 Footer

- [x] Shift toggle and "[Shift] info" hint removed from fight phase
- [x] Footer reads "[E] Attack    [Esc] Back"

## Files changed

- src/engine/audio.js — BGM_FILES & SFX_FILES paths corrected to actual WAV files
- src/data/audio.js — MAP_BGM keys updated (rootmere, brindlewood, trial_grounds)
- src/App.js — battle BGM calls changed to battle_basic
- src/screens/BattleScreen.js — drawFightGrid rewrite; drawStatusBox HP spacing; Shift toggle removed
- styles.css — no changes needed (pixelated already set)
