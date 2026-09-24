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

## Play on your phone (GitHub Pages)

The game is an installable web app: once it's online you can add it to your home screen,
it opens full-screen in landscape with touch controls, and it keeps working offline.

1. Put this folder on GitHub (e.g. GitHub Desktop → *Add existing repository* → *Publish repository*).
2. On github.com open the repo → **Settings → Pages** → under *Build and deployment* set
   **Source: GitHub Actions**.
3. Every push to `main` now runs the tests, builds the game and publishes it
   (`.github/workflows/pages.yml`). The address appears on the Pages settings page —
   usually `https://<your-username>.github.io/<repo-name>/`.
4. On the phone, open that address in Chrome or Samsung Internet and choose
   **Install app** / **Add to Home screen**.

Saves live on the phone (in the app's browser storage), separate from your computer's saves.
Browsers that wipe site data (e.g. DuckDuckGo's Fire button) wipe the saves too — Chrome is the
best choice for installing it.

The game always plays sideways. If the phone's auto-rotate is off, it turns itself round (using the
motion sensor to pick the right way up) — just hold the phone landscape. New versions download in
the background and switch over on the title screen.
A free GitHub account needs the repository to be public for Pages to work; with a paid plan the
repo can be private, but the game's web address is still reachable by anyone who has the link.

Touch controls: the pad moves (slide your thumb between arrows), **A** talks/confirms,
**B** goes back, **RUN** runs (with Trail Boots), **MENU** opens the pause menu.

## Controls

| Action | Keyboard | Gamepad |
|---|---|---|
| Move | Arrow keys / WASD | D-pad / stick |
| Talk, confirm | Z, E, Space, Enter | A |
| Back, cancel | X, Q, Backspace | B |
| Menu | C, Tab, Esc | Start |
| Run (with Trail Boots) | Hold Shift | Hold X / R2 |
| Change controls | Pause menu → Controls | |
| Info in menus | F / R | Y |

Every keyboard control can be changed in-game: open the pause menu and choose **Controls**
(also under Options). Changes are saved in your browser. Space / E (confirm), Q (back) and
Tab (menu) always work as a fallback. Touch controls appear automatically on phones and tablets.

## Difficulty curve

Every area has a tier from 0 (Rootmere) to 7 (the Riven), set in `src/data/region.js`.
`src/data/difficulty.js` uses it to ramp things up as you travel: wild Morphs near home have
soft genes and fight at random, Tamers start with no genes to speak of and make mistakes, and
both get sharper tier by tier. Wardens and rivals always sit a step above the Tamers around
them. Morphs you catch get a second roll on their genes, so early catches stay useful, and
your starter and gift Morphs are always strong. `npm run balance` prints the whole curve.

## What's in the game

- **The Riven Reach**: 49 hand-built maps — 7 towns, 6 routes, a forest, mines, a lake crossing,
  a mountain pass, a cult headquarters, the Abyssal Rift and Tiamat's Cradle.
- **68 Morphs** across 15 types, each with a male and a female form (Tiamat, the Draco Queen,
  is always female), evolutions, move learning, Tech Discs, Radiant (shiny) Morphs —
  1 wild Morph in 100 — and day/night and water encounter tables.
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
public/manifest.webmanifest, public/icons/   phone app manifest + icons (tools/art/build_icons.py)
.github/workflows/      GitHub Pages deployment
tools/
  worldgen.py           authors every map (tools/maps/*.map)
  art/                  pixel-art generators (tiles, buildings, characters, Morphs, UI)
  audio/                chiptune synthesiser + the soundtrack
  validate.mjs          checks every map, warp, script and trainer; flood-fills for unreachable stuff
  balance-sim.mjs       simulates every boss fight for each starter
  playtest.py           headless-browser playthrough of the whole story
  pwa/sw-template.js    offline cache; vite.config.js fills in the file list at build time
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
