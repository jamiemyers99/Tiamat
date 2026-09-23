# Tiamat Browser Roadmap

The browser version is the master version of Tiamat.

The Python terminal version is paused unless explicitly requested later.

## Clean-Room Rules

- Use only original Tiamat names, characters, regions, maps, dialogue, creatures, UI, music, and code.
- Do not use Pokemon-owned names, sprites, maps, music, UI assets, dialogue, code, logos, or fonts.
- Use only custom-made or clearly licensed open-source assets.
- Track every external asset in `ASSETS.md`.

## Immediate Build Order

1. Fix doors and NPC interaction.
2. Make compact Rootmere work properly.
3. Add working Morph Lab starter selection.
4. Add Route One transition.
5. Add Route One long grass encounters.
6. Improve battle UI.
7. Add XP and level-up.
8. Add catching.
9. Add party menu.
10. Add save/load.

## Minimum Playable Goal

The next stable browser build should allow the player to:

- start in Rootmere
- walk around the compact starter town
- talk to NPCs
- enter and exit houses
- enter the Morph Lab
- choose Spriglet, Cindlet, or Drizzle
- leave town for Route One
- walk through long grass
- trigger a wild Morph battle
- win or run from battle
- return to Rootmere

## Phase Overview

### Phase 1 - Core Overworld Interaction

- movement
- collision
- facing direction
- door interaction
- building entry and exit
- NPC interaction
- dialogue box
- compact Rootmere town
- Route One transition

### Phase 2 - Map System

Reusable map definitions should support:

- `id`
- `name`
- `width`
- `height`
- `tileset`
- tile layers
- collision
- doors and warps
- NPCs
- signs
- items
- triggers
- encounter table
- music

### Phase 3 - Event and Dialogue System

Support scripted actions such as:

- `SHOW_TEXT`
- `YES_NO_CHOICE`
- `GIVE_ITEM`
- `REMOVE_ITEM`
- `GIVE_MORPH`
- `START_BATTLE`
- `SET_FLAG`
- `CLEAR_FLAG`
- `CHECK_FLAG`
- `MOVE_NPC`
- `WARP_PLAYER`
- `OPEN_SHOP`
- `OPEN_STORAGE`
- `HEAL_PARTY`
- `PLAY_SOUND`
- `PLAY_MUSIC`

### Phase 4 - Morph Species System

Starter species in the browser roadmap:

- Spriglet
- Cindlet
- Drizzle

Each species should eventually define:

- `id`
- `name`
- `type_1`
- `type_2` optional
- base stats
- `catch_rate`
- `base_xp_yield`
- `growth_rate`
- `learnset`
- `evolutions`
- `dex_entry`
- `front_sprite`
- `back_sprite`

### Phase 5 and Beyond

Planned systems:

- individual Morph instances
- move data and PP
- turn-based battle flow
- damage and type chart
- wild encounters
- catching
- party system
- XP and leveling
- bag and inventory
- money and shops
- healing center equivalent
- save and load
- in-game menu
- Morph Index
- Tamer battles
- Trials
- evolution
- storage
- machines and field moves
- audio
- data-driven file layout
- browser-focused source layout

## Data Direction

Recommended long-term structure:

```text
/data
  species.json
  moves.json
  items.json
  tamers.json
  maps/
    rootmere.json
    route_1.json
    thornwild.json
  encounters.json
  shops.json
  scripts.json
  type_chart.json
```

## Code Direction

Recommended long-term browser layout:

```text
/src
  /core
  /world
  /morph
  /battle
  /items
  /ui
  /audio
  /data
```
