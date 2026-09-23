# Tiamat — Asset Sources

| Asset | Where it comes from | Rebuild with |
|---|---|---|
| World tileset, all maps (`public/assets/tilesets`, `public/assets/maps`) | `tools/worldgen.py` + `tools/art/build_maps.py` (terrain, decor, buildings, interiors) | `npm run maps` |
| Characters (`sprites/chars.*`) | `tools/art/chars.py` / `build_chars.py` | `npm run art` |
| Morph sprites & icons (`sprites/mons.*`, `sprites/icons.*`) | `tools/art/mon_designs.py`, `mongen.py`, `build_mons.py` | `npm run art` |
| UI atlas, window skins, fonts (`ui/`, `fonts/`) | `tools/art/build_ui.py`, `font.py` | `npm run art` |
| Battle backgrounds (`battle/`) | `tools/art/build_battlebg.py` | `npm run art` |
| Reach Map (`ui/regionmap.png`) | `tools/art/build_regionmap.py` | `npm run art` |
| Music: rootmere, route, haven, house, battle_wild, battle_trial; all SFX | Original project audio pack (converted from WAV to OGG) | — |
| All other music and jingles | `tools/audio/songs.py` (chiptune synth in `tools/audio/synth.py`) | `npm run music` |

Everything is original and owned by the project. No attribution to third parties is required.
