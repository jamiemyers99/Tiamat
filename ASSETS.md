# Tiamat — Asset Sources

| Asset | Where it comes from | Rebuild with |
|---|---|---|
| World tileset, all maps (`public/assets/tilesets`, `public/assets/maps`) | `tools/worldgen.py` + `tools/art/build_maps.py` (terrain, decor, buildings, interiors) | `npm run maps` |
| Characters (`sprites/chars.*`) | `tools/art/chars.py` / `build_chars.py` | `npm run art` |
| Morph sprites & icons (`sprites/mons.*`, `sprites/icons.*`) | `tools/art/mon_designs.py`, `mongen.py`, `build_mons.py` | `npm run art` |
| UI atlas, window skins, fonts (`ui/`, `fonts/`) | `tools/art/build_ui.py`, `font.py` | `npm run art` |
| Battle backgrounds (`battle/`) | `tools/art/build_battlebg.py` | `npm run art` |
| Reach Map (`ui/regionmap.png`) | `tools/art/build_regionmap.py` | `npm run art` |
| All music and jingles (`audio/bgm`, `audio/sfx/jingle_*`) | Hand-written melodies and chord charts in `tools/audio/score.py`, arranged by `tools/audio/compose.py`, played through FluidSynth with the FluidR3_GM soundfont and mastered by `tools/audio/render.py` | `npm run music` |
| Menu, world and battle sounds (`cursor`, `select`, `door`, `spotted`, `hit`, `ui_*`…) | `tools/audio/ui_sfx.py` (FluidR3_GM instruments + synthesised foley) | `npm run sfx` |
| Move sounds (`mv_*`, `sig_*`) | Synthesised in `tools/audio/sfx.py` | `npm run sfx` |

The music, melodies and sound design are original to the project. The instrument samples come from the
**FluidR3_GM** General MIDI soundfont by Frank Wen (MIT licence) — see CREDITS.md.
