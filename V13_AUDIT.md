# V13 Audit — what shipped vs. what didn't

Generated: 2026-04-29 by coding agent before the v13 completion pass.

---

## §1 Battle move grid (2×2)

- ✅ 2×2 cell layout with empty-slot placeholders — grid renders via `drawFightGrid()`; empty slots simply don't draw
- ✅ Effectiveness tag in brackets per move — `getEffectiveness()` called per move; 2×/½×/0× badge rendered
- ❌ Type badges next to Morph names in HUD — status box shows name+level+HP only; no type badge on the HUD portrait
- ❌ Persistent info strip below grid — the `[Shift] info / [Esc] back` hint only shows at the bottom of the full-height panel, not as a dedicated strip
- ✅ HP-text inside panel — player box H increased to 40px; text at y+29 is inside the box
- ❌ Battle log box (2 lines) — log is a single string rendered in the main panel; no dedicated 2-line box
- ❌ Action queue ordering by speed — `performTurn()` resolves player first always; no speed-based ordering

## §2 Shop screen

- ✅ Scrolling with ▲/▼ arrows — 5-item viewport with scrollOffset; ▲ and "▼ more" indicators shown
- ❌ Three-panel layout (header / list / coins+desc) — single flat panel; no description column
- ❌ BUY / SELL / EXIT root menu — no sell flow exists; shop opens directly to buy list
- ❌ Quantity selector with live total — no quantity picker; each press buys exactly 1
- ❌ Sellable filter respected (key items can't be sold) — sell flow doesn't exist
- ✅ No overflow past panel borders — viewport fix prevents overflow

## §3 Trial Gate building

- ❌ Orange roof + flag + stone walls — no `building_trial` kind; trial gate is just map tiles
- ❌ Double iron-grate door — not rendered
- ❌ Sign in front of gate — no sign object in trial_grounds objects array
- ✅ Mossa's arena interior — trial_arena map exists (12×10) with correct tile layout
- ✅ Veteran Rook trainer with vision — `tg_veteran_rook` NPC in trial_grounds with battleId + vision
- ✅ Mossa fight trainer — `trial_mossa` NPC in trial_arena with battleId + vision
- ⚡ Mossa victory rewards — sets `trial1Won` flag and `letterDelivered`; does NOT grant Sprout Badge, TM Vine Lash, or 2,000 coins — only the Messenger's 500-coin reward is wired
- ❌ flags.mossaDefeated not set — flag used is `trial1Won`; plan name was `mossaDefeated`

## §4 Roof colour coding

- ✅ Healing Centre pink with cross — pink palette + white plus symbol implemented
- ✅ Shop blue with green awning — awning strip added
- ✅ Lab red with chimney — was already red
- ❌ Trial orange with flag — no building_trial kind exists
- ✅ Player Home blue — uses default blue palette
- ❌ Signposts in front of each special building — no sign objects in brindlewood.objects or rootmere.objects for buildings

## §5 Furniture — full catalogue

- ✅ Bed (interactable: heal) — B tile heals in all interiors; map restriction removed
- ✅ Bookshelf — object kind "bookshelf" rendered in drawObjects; placed in all houses + player_home
- ✅ Table — object kind "table" rendered; placed in morph_lab, shops, house_e
- ❌ Chair — not implemented
- ✅ TV_crt (flavour text) — V tile dispatches per-map INTERACTION_TEXT; player_home:V defined
- ✅ PC_terminal — P tile opens StorageScreen globally; healing_centre:P INTERACTION_TEXT wired
- ❌ Lab_apparatus — not implemented
- ✅ Incubator — C tile opens starter selection in morph_lab
- ❌ Healing_machine, Shop_counter — handled via NPC; no separate object
- ✅ Pot_plant — object kind "pot_plant" rendered; placed in all interiors
- ❌ Rug, Door_mat, Arena_pillar, Pew_bench, Podium, Desk_office, Cardboard_box — not implemented
- ✅ Per-interior placements — all interior objects arrays populated

## §6 TM/HM system

- ✅ TM tab in bag (tab 3 of 4)
- ✅ TM usage flow — party picker sub-screen; teaches move if slots free
- ✅ House B tutor gives TM01 item (not direct teach)
- ❌ tms.js catalogue file — TMs defined inline in PauseScreen.js constants
- ✅ compatibleTMs on every species — all 27 species have `compatibleTMs: ["tm01_body_slam"]`; check enforced in PauseScreen
- ✅ Known-move check — `m.id === moveId || m.name === move.name` fallback handles both cases
- ✅ Replace prompt when slots full — opens MoveLearnPrompt via `actions.teachMove`; TM consumed before prompt
- ✅ TM consumed only on actual learn (or when replace-prompt is confirmed)
- ❌ HM system — not started

## §7 Battle polish

- ✅ HP overflow fix — player status box height fixed
- ❌ Battle log box visible — log text shares space with the action menu; no dedicated bordered log box
- ❌ Catch wobble caption in log — wobble shows "The Capsule is shaking..." as static text; does not use the scrolling log format
- ❌ Action sequence rendered in order — player always acts first; no speed-based priority queue

## §8 PC storage wiring

- ✅ Player Home PC interactable — 'P' tile in player_home opens StorageScreen via App.js
- ❌ Healing Centre PCs interactable — healing_centre map has 'P' tile but no INTERACTION_TEXT entry and no handler for that map's P tile in App.js
- ✅ Shared box data across all access points — single `state.storage` object
- ❌ StorageScreen three-panel layout — current layout is single panel with box/slot grid

## §8 PC storage

- ✅ Player Home PC interactable — 'P' tile opens StorageScreen
- ✅ Healing Centre PC interactable — 'P' tile handled globally; INTERACTION_TEXT entry exists
- ✅ Shared box data — single `state.storage` object
- ❌ StorageScreen three-panel layout — single panel with box/slot grid

## §9 Save schema migration

- ✅ Migrator function in saveMigration.js — `migrateSave()` chains v1→v2→v3; `applySave()` uses it
- ✅ Old inline `_migrateV1`/`_migrateV2` removed from App.js
- ✅ Corrupted-save fallback UI — `state.mode = "corrupt_save"` with YES/NO dialog
- ⚡ bag split (items/capsules/keyItems/tms) — still flat `state.items`; save schema stays at v3
- ⚡ TMs tab preserved through migration — `migrateSave` preserves `items` blob which includes TMs

## §10 While-we're-at-it features

- ⚡ Battle reward summary — defeat shows multi-line dialogue; no dedicated screen
- ✅ Faint handling + whiteout — full party heal, halve coins, respawn at lastHealingCentre/home, white fade (90-frame timer)
- ✅ lastHealingCentre tracked — `healParty("centre")` records map+position in `flags.lastHealingCentre`
- ✅ Mossa victory rewards — Sprout Badge flag + 2000 coins granted on trial_mossa defeat
- ✅ force_switch phase — when active creature faints mid-battle, mandatory party switch before next turn (no defeat if other members alive)
- ✅ Voluntary party switch — CREATURE menu shows HP+status, cursor selection, syncs back active creature on switch
- ❌ Map transition fade-through-black — instant cut; no fade
- ✅ NPC walk paths — walkPath+walkInterval on Townsfolk+Kid (brindlewood), Rootmere Local (rootmere); `_tickNpcWalkers` in WorldScreen
- ✅ Tile animations — water `~` (2-frame 24-tick) and tall grass `G` (2-frame 30-tick, staggered)
- ✅ Sign objects rendered — drawObjects handles `sign` and `flower` kinds; tryInteract checks object-layer signs
- ✅ Signposts in brindlewood — HC sign, Shop sign, Trial Gate sign added to objects array
- ✅ TV text per map — tryInteract uses `${currentMap}:V` key before fallback
- ✅ Bed heal in all interiors — map restriction removed; any B tile heals
- ✅ TM replace prompt — full-slots case opens MoveLearnPrompt via `actions.teachMove`
- ❌ Signpost interaction prompt indicator — no visual prompt when adjacent to sign
- ❌ First-time vs repeat NPC dialogue — afterDialogue only fires after trainer defeat
- ❌ Text-speed setting — textSpeed stored but ignored by dialogue.js
- ❌ Palette toggle in Options — not present

---

## Summary (updated 2026-04-29 pass 2)

| Section | Done | Partial | Skipped |
|---------|------|---------|---------|
| §1 Battle 2×2 grid | 3 | 0 | 4 |
| §2 Shop screen | 2 | 0 | 4 |
| §3 Trial Gate | 3 | 1 | 3 |
| §4 Roof colours | 3 | 0 | 2 |
| §5 Furniture catalogue | 2 | 3 | 15 |
| §6 TM system | 4 | 1 | 4 |
| §7 Battle polish | 1 | 0 | 3 |
| §8 PC storage | 3 | 0 | 1 |
| §9 Save migration | 3 | 2 | 0 |
| §10 While-we're-at-it | 8 | 0 | 4 |
3. §5 Furniture catalogue — minimal correct version for each kind
4. §5/§10 NPC walk paths — 2 in Brindlewood, 1 in Rootmere
5. §6 Tile animations — water + tall grass
6. Re-verify all v13 §12 checklist items
