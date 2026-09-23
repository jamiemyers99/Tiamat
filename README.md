# Tiamat — Tales of the Riven Reach

An original creature-taming adventure in the spirit of the classic handheld RPGs.
Choose your first Morph, take on six Warden Trials, stop the Deepcall — and decide
what to do when the sea-dragon Tiamat wakes.

Everything in the game — creatures, names, maps, characters, story, art, music — is
original to Tiamat.

## Play

**Easiest:** double-click **`Play Tiamat.bat`** (Windows). It starts a tiny local
server and opens the game in your browser. It needs Python 3 (already installed if
you've run the old prototype). On macOS/Linux run `./play.sh`.

**For development:**

```bash
npm install
npm run dev        # hot-reloading dev server at http://localhost:5173
npm run build      # production build into dist/
```

Add `?debug` to the URL for developer tools (F1 or ` in game: warp, heal, items, flags).

## Controls

| Action | Keyboard | Gamepad |
|---|---|---|
| Move | Arrow keys / WASD | D-pad / stick |
| Talk, confirm | Z, E, Space, Enter | A |
| Back, cancel | X, Q, Backspace | B |
| Menu | C, Tab, Esc | Start |
| Run (with Trail Boots) | Hold Shift | Hold X / R2 |
| Info in menus | F / R | Y |

Touch controls appear automatically on phones and tablets.

## What's in the game

- **The Riven Reach**: 49 hand-built maps — 7 towns, 6 routes, a forest, mines, a lake crossing,
  a mountain pass, a cult headquarters, the Abyssal Rift and Tiamat's Cradle.
- **68 Morphs** across 15 types, with evolutions, move learning, Tech Discs,
  shinies, day/night encounter tables and water encounters.
- **Six Warden Trials** (Mossa, Brann, Iskra, Morrow, Hale, Seren), a rival who always
  picks the starter that beats yours, the Deepcall admins Vesk and Maren, and the
  Hierophant Oriel.
- **91 trainer battles**, gyms-with-adepts, story bosses and a legendary encounter.
- **Pokémon-style systems**: Havens (heal + shop + storage PC), 8-box storage, Bond Charm
  XP sharing, Ward Incense, Homing Thread, Skiff (surfing), Brush Hook (cutting),
  Wing Whistle fast travel on the Reach Map, nicknames, trainer AI with items.
- **Modern presentation**: 480×270 widescreen pixel art, smooth movement and camera,
  animated battles, day/night lighting with glowing windows and lamps, fog/rain/snow
  weather, screen transitions, and a full soundtrack.
- **Saves**: three save slots in your browser (Continue from the title screen).

The whole story is in [STORY.md](STORY.md).

## Project layout

```text
index.html, src/        the game (Phaser 3 + Vite)
  scenes/               Title, Intro, World, Battle, Menu, Evolution, Credits…
  battle/               battle engine, Morph maths, trainer AI
  data/                 species, moves, items, trainers, encounters, region map
  scripts/              every story event, NPC and cutscene (act1–act4.js)
  world/, ui/, core/    map rendering, lighting & weather, widgets, input, saves, audio
public/assets/          generated art, Tiled maps (.tmj), fonts and audio
tools/
  worldgen.py           authors every map (tools/maps/*.map)
  art/                  pixel-art generators (tiles, buildings, characters, Morphs, UI)
  audio/                chiptune synthesiser + the soundtrack
  validate.mjs          checks every map, warp, script and trainer; flood-fills for unreachable stuff
  balance-sim.mjs       simulates every boss fight for each starter
  playtest.py           headless-browser playthrough of the whole story
tests/                  unit tests (node --test)
legacy/                 the earlier 160×144 browser prototype and the Python prototype
```

## Rebuilding assets

```bash
npm run art        # characters, UI, Morph sprites, battle backgrounds, maps, Reach Map
npm run maps       # just the maps (after editing tools/worldgen.py)
npm run music      # re-render the soundtrack (tools/audio/songs.py)
npm test           # unit tests + world validator
npm run balance    # boss difficulty report
```

The `.tmj` maps open in the [Tiled](https://www.mapeditor.org) editor. Maps are
regenerated from `tools/worldgen.py`, so make lasting layout changes there.
