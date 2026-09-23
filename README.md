# Tiamat

Tiamat is an original retro creature-adventure prototype inspired by the broad
feel of late-1990s handheld RPGs while using original names, creatures, tiles,
sprites, UI, and dialogue.

## Browser Prototype

The browser build is now the main version of Tiamat. It uses a `160x144`
internal canvas and currently includes:

- compact Rootmere starter town
- Route One as the first exploration area outside town
- enterable Player Home, Morph Lab, and two small houses
- lab-only starter selection for Spriglet, Cindlet, and Drizzle
- Route One grass encounters that unlock after choosing a starter
- retro dialogue panels, battle screen, and map HUD

Open [index.html](./index.html) in a browser, or serve the folder locally with:

```powershell
python -m http.server 4173
```

Then visit `http://localhost:4173/`.

## Controls

- `W`, `A`, `S`, `D` or arrow keys: move
- `E`, `Space`, or `Enter`: interact, advance dialogue, confirm battle choices

## Current Milestone Features

- Compact Rootmere town with attached building doors and a locked Trial Gate
- Route One expansion area with long grass, bridge, water, trainers, and a blocked Thornwild path
- Enterable Player Home, Morph Lab, and two cottage interiors
- Facing-based interaction for doors, NPCs, the lab console, and room objects
- Collision with trees, water, buildings, the Trial Gate, furniture, and NPCs
- Starter selection from the Morph Lab console only
- Route One encounters only after starter selection
- Original starter creatures: Spriglet, Cindlet, and Drizzle
- Wild Route One Morphs: Spriglit, Chardit, and Brinlin
- Trainer battles, coins, and Morph XP progression
- Retro battle screen with `FIGHT`, `BAG`, `CREATURE`, and `RUN`
- Original placeholder pixel art drawn directly in code

## Project Shape

```text
src/
  data/
  engine/
  screens/
index.html
styles.css
CREDITS.md
```

## Terminal Prototype

The older Python terminal prototype is paused for now and is no longer the
primary development target. It is still included in the repo, but new features
should be built in the browser version first.

You can still run it with:

```powershell
python main.py
```

Tests for the Python prototype:

```powershell
python -m unittest
```

Windows executable for the Python prototype:

```text
dist/Tiamat.exe
```

## IP Note

This project must stay original. Do not add official Pokemon characters,
creatures, sprites, music, sound effects, maps, UI elements, names, or copied
mechanics text.
