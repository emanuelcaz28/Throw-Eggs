# How to make a new map

The recipe, learned from building maps 1 to 9. Follow it step by step and you don't need to study the older
maps: everything reusable is in `assets/models/map_kit.py`, and `assets/models/build_eclipse_temple.py` (map 9)
is the worked example to copy. `docs/GAME_SPEC.md` still wins over this file.

A "map" (a world, a biome in the code) is one stretch of the corridor with its own colours, light, props and,
later, 6 monsters. The arena and the bases don't change. It's two separate jobs, usually on different days:

1. **The world** (this recipe, steps 1 to 8): props, corridor colours, light, where everything goes, what moves.
2. **Its 6 monsters** (step 9). Until they're in `Config/Dinos`, eggs can't land in the world
   (`Throw.maxDistance`): players see it ahead during long throws, it has no Index card and can't be completed.

## 1. Before you start (minutes, not hours)

- In `docs/GAME_SPEC.md` read only section 8a (the map table and the style per map) and the end of section 9
  (the world list, the luck table and the last world's build notes). Find what the owner said about this map.
- Memory: `later-maps-weirder-monsters` (each map's mood) and `two-accounts-same-checkout`.
- `git status`: another account may be editing the same shared files. Use small exact edits, never rewrite them.
- Don't read the older build scripts. If you need a shape, look in `map_kit.py` first (section 3).

## 2. Design the world

Write the pitch in the build script's docstring first: theme, mood, colours, signature prop, landmarks, what moves.

**Colour identity.** Each world must read in under a second from the flight, so its floor, walls and rims, and its
glow, must differ from its neighbours'. Taken so far:

| # | World | Floor | Walls | Rims | Glow | Light |
|---|---|---|---|---|---|---|
| 1 | Forest | bright green | brown dirt | lime grass | none | bright day |
| 2 | Desert | pale sand | tan | sand | none | golden haze |
| 3 | Swamp | murky blue-green | brown | olive green | yellow lanterns | green murk |
| 4 | Volcano | dark rock | darker rock | scorched red | orange lava | orange haze |
| 5 | Frozen Peaks | packed snow | frozen blue | white snow | warm fire (monsters: ice blue) | pale blue |
| 6 | Shadow Bog | slate violet | dark plum | teal moss | magenta, violet | violet dusk |
| 7 | The Abyss | deep blue sand | abyssal blue | sea green | cyan, pink | dim blue, thick haze |
| 8 | Starfall Crater | midnight blue | navy | pale moon dust | cyan, gold, magenta | night (ClockTime 0) |
| 9 | Eclipse Temple | red laterite | dark plum stone | jungle green | jade green, lantern gold | night before dawn, jade mist |
| 10 | Forbidden Library | deep violet carpet | dark walnut | parchment | violet ink, candle amber | night (ClockTime 2), indigo haze |
| 11 | Midnight Carnival | deep teal | crimson | gold straw | warm bulbs, pink neon, ghost white | midnight (ClockTime 0), plum haze |
| 12 | Clockwork Citadel | bronze plates | soot iron | copper | electric blue, furnace orange | before dawn (ClockTime 4), steel-blue smog |
| 13 | Thorn Kingdom | dark moss | black-violet thorn bark | silver moss | crimson roses, firefly gold | night (ClockTime 3), silver-mauve mist |
| 14 | Spore Hollow | dark umber loam | peat | pale cream mycelium | chartreuse gills, amber windows, lilac bells | night (ClockTime 2), olive-gold spore mist |
| 15 | The Weeping Dark | ash black | black | grey ash | pale tear-light, candles; red only for eyes | night (ClockTime 1), the darkest, dim grey starless sky |
| 16 | Shattered Mirror | polished lilac silver | smoked violet glass | white quartz | white cracks, cyan eyes, rainbow bands; props are holographic chrome and gold (`METAL`) | bright pearl-pink dawn (ClockTime 6) |

The exact colours are in `Config/Map` `biomeColors` and `Config/Lighting` `worlds`.

**The prop list.** About 16 to 18 props, sorted by where they go (these are `Config/Decor`'s lists):

| Kind | How many | Notes |
|---|---|---|
| Signature | 1 | The world's symbol (a guardian head, a crystal cluster). Most common on the floor, big on the rims too. |
| Floor props | 6 to 8 | Off the middle (24 to 34 studs out). One or two are rare treats (weight 3 to 6). |
| Filler | 1 or 2 | Small plants, rocks: used as `extras` round the floor props and on the rims. |
| Flat floor prop | 1 | Under 0.5 studs tall, so it can lie in the middle where eggs land (rune circles, craters). |
| Rim props | 3 to 5 | Trees and the like, scaled 1.8 to 2.6 on the rims. |
| Landmarks | 2 or 3 | Big set pieces at fixed `spots` on the rims (temples, statues, volcanoes). |
| Sky piece | 0 or 1 | Floats beyond the island (planets, comets, eclipses). Its model starts high up. |
| Wall prop | 1 | Hangs down a corridor wall (`walls`): falls of lava, water or stardust. |
| Overhead | 1 | Spans the corridor (`overhead`): arches, gates, fallen trees. |

From map 8 on the owner wants things to **move where it makes sense**: aim for most props having a moving or
pulsing part (step 4).

**Sizes** (1 stud = 1 Blender unit, a player is about 5 tall). The corridor is 88 wide with walls 44 tall; the
rims run from 44 to 116 out. At size 1, floor props are about 6 to 12 tall and placed at 1.2 to 2; rim props are
placed at 1.8 to 2.6; landmarks are 20 to 30 tall at size 1 and placed at 1.4 to 1.8.

**Names** are ours, never the reference game's. Ids are CamelCase without spaces (`EclipseTemple`), used for code,
files and Studio folders alike.

## 3. Build the props in Blender

Copy `assets/models/build_weeping_dark.py` (map 15: the newest, with hands, hooded figures, tears, candles, real light and
preview fog), `build_forbidden_library.py` (map 10, with the plain-colour setting and helpers for
books, candles, turned boxes and magic circles), `build_clockwork_citadel.py` (map 12: gears that mesh, flywheels,
steam and smoke puffs that rise for ever, lightning arcs, gauges, valve wheels) or `build_eclipse_temple.py` to `build_<map>.py` and replace: the docstring, `RENDERS`,
`GLOW_ROLES`, the colours, `CORRIDOR` and `SKY` (preview only), `MOTION`, the prop functions and `ALL`, `DECOR`,
the light function, and the `big` dict in `main` (which props get their own spot in the renders).

**Shapes** (all in `map_kit`, each adds to one colour role of a model `m`):

| Helper | Makes |
|---|---|
| `m.block(role, x, y, z, w, d, h)` | a box round a centre |
| `m.loft_z(role, (z, x, y, w, d), (z, x, y, w, d))` | a box tapering from one rectangle to another (also `loft_x`, `loft_y`) |
| `prism(m, role, x, y, z0, z1, r0, r1, sides, turn, lean)` | an upright n-sided column, tapering and leaning |
| `beam(m, role, a, b, width, height, end_width)` | a stick from point a to b (branches, legs, ribs) |
| `plate(m, role, a, b, side, w0, w1, thick)` | a flat tapering plate whose width lies along `side`: rays, petals, feathers (beam lays them flat) |
| `limb(m, role, points, w0, w1)` | a crooked branch or root through points |
| `ball`, `gem`, `disc`, `hoop`, `flat_ring`, `dome`, `puddle` | balls, double-pointed crystals, round slabs, upright rings, flat rings, blobs, flat pools |
| `hanging_vine`, `moss_beard`, `crystal`, `sparkle`, `star_prism`, `boulder` | vines, moss, crystal columns, twinkles, stars, rocks |
| `stone_face` (in build_eclipse_temple.py) | a carved face on a flat front, looking +Y or -Y |

**Rules that matter in the game:**

- **No stud texture in Blender** (owner, 2026-11-04). Keep `kit.PREVIEW_STUDS = False` near the top of the script
  (map 10's has it): every material is a plain colour, with none of the old round-stud preview image the maps
  before 10 have. The studs come only from Studio's shared "Studs" material (step 8). The UVs are still made.
- **One mesh per colour role.** A role is one colour and becomes one part in Studio. Its name is the part's last
  word (`prop_Orrery_RingA` → `RingA`), so no underscores, CamelCase.
- **Roles are shared by the whole game.** `shared/Roles.luau` `glowing` makes a role Neon on every model, so a new
  glowing role must not be a name another model uses for something dull (and the other way round); `check_map.py`
  warns about that. Don't use bone names (`Head`, `Jaw`, `Wing`) as roles either.
- **Glowing parts:** list the role in the script's `GLOW_ROLES` and in `Roles.glowing`. Keep studs off them.
- **Metal parts** (Shattered Mirror on): list the role in the script's `METAL` with a MaterialVariant name (`HoloChrome`,
  `PolishedGold`, made in MaterialService by `studio_chrome.luau`); studio_tidy makes them Foil with that variant and no
  studs, the part's colour tinting it. Metal needs its world's `EnvironmentSpecularScale` turned up in `Config/Lighting`.
- **Props stand on Z = 0 at their origin and face +Y.** Sky pieces start high above it, wall props hang below it.
- **Front marker:** a prop that has to face a certain way (wall props, overhead props, spots with `face`) gets a
  tiny `Front` part on its +Y side: `m.block("Front", 0, 6, z, 0.2, 0.2, 0.2)`. MapDecor turns the prop by it and
  removes it, so it works whichever way Studio's importer turned the model (it often turns them round).
- **Wall props:** origin on the wall's top inner edge: the rim is Z = 0, the corridor floor Z = -44, +Y out into the
  corridor. Stay more than 1.5 out from the wall (the hanging jungle or grass sticks out that far).
- **Overhead props:** modelled for a 72-wide corridor, feet beyond 36 from the middle (MapDecor stretches them to
  88), and all of it above Z = 0 so the flight camera, which stays in the valley, never hits it.
- **Flat floor props:** under 0.5 tall.
- **Faces:** simple blocks, but the face is where the effort goes. Calm reads as a level brow and level lids;
  angry is slanted brows and teeth. Check the map's mood in memory before choosing.

**Run it and look:**

```
cd assets/models
/Applications/Blender.app/Contents/MacOS/Blender -b -P build_<map>.py -- stills   # about 20 seconds
/Applications/Blender.app/Contents/MacOS/Blender -b -P build_<map>.py             # stills and both videos, a few minutes
```

It saves `<map>_models.blend` and writes renders to `design/world/models_<map>/`: one still per prop, `props`,
`landmarks`, four corridor shots, and the videos `<x>_motion.mp4` and `<x>_flight.mp4`. Look at them yourself;
a contact sheet saves time:

```
ffmpeg -y -i a.png -i b.png -i c.png -i d.png -filter_complex "[0][1][2][3]hstack=4,scale=1600:-1" sheet.png
```

Things to look for: anything floating that shouldn't be, a face that doesn't read, glow that clips to white or
cyan (lower `mk.GLOW_STRENGTH`; it's only the preview), props too small to read from the flight, and whether the
corridor shots look like this world and nothing else.

## 4. Make things move

A moving piece is its own role (several pieces with exactly the same move can share one). List the moves in the
script's `MOTION` and copy them to `src/shared/Config/PropMotion.luau`; `PropMotionController` plays them on each
player's screen, and the Blender videos play the same moves, so what you see in the video is what the game does.

| Move | Means |
|---|---|
| `spin = 20` | turns 20 degrees a second |
| `swing = 12, period = 2.6` | rocks 12 degrees each way and back every 2.6 seconds (lanterns, bells, a head looking round) |
| `axis = "up" / "across" / "ahead"` | what spin and swing turn round: upright (default), the model's X, or its Y |
| `about = "self"` | turn round the part's own middle; without it, round the prop's origin |
| `height = 7.8` | turn round the point 7.8 studs straight above the origin instead (a lantern's hook) |
| `bob = 0.5, period = 3` | rises and sinks 0.5 studs every 3 seconds |
| `pulse = 0.4, period = 3` | the glow dims to 40 % and back |
| `fall = 4, period = 0.8` | drops 4 studs and starts again; space the drops exactly 4 apart and it loops seamlessly. Negative rises (sparks). |
| `"*": drift = 420, period = 36, fade = 0.12, head = "Role"` | the whole prop glides head first and fades out and back (comets) |

**Real light.** Neon lights nothing round it. A map too dark for that can give a prop real light: list it in the
script's `LIGHTS` and `Config/Decor` `propLights` (the role it shines from, colour, range and brightness at size 1;
`check_map.py` compares them). `MapDecor` adds a PointLight, and `PropMotionController` dims it with the role's pulse,
so a flickering lamp really flickers. **See-through glow** (a beam): `Roles.sheer`. `build_weeping_dark.py` (map 15) has
both, with preview fog and lights in its renders.

Getting the centre right: parts that must turn together (a lantern's frame and its light, a head and its mask)
must turn round the **same point**. `about = "self"` uses each part's own middle, so it only suits a part that is
one piece centred on its own axis (a ring round an orb, a spinning star). Otherwise build the moving thing
straight above the prop's origin and use the origin (`height` for a hook or a hinge). For `axis = "across"` any
point along the X line at that height works, so lanterns hung anywhere along a lintel at that height swing right.

## 5. Export the FBX files

Add the map's folder to `MAPS` and its `.blend` to `MAP_OF_FILE` in `assets/models/export_fbx.py`, then:

```
/Applications/Blender.app/Contents/MacOS/Blender -b assets/models/<map>_models.blend -P assets/models/export_fbx.py
```

One FBX per prop lands in `assets/models/fbx/NN_<Map>/Props/`. The owner imports them in Studio themselves
(memory `owner-does-studio-imports`): tell them which folder is ready.

## 6. Wire it into the game

Small exact edits, one per file:

| File | Add |
|---|---|
| `Config/Biomes` | `{ id, name, startDist, endDist, luck, standardScale, color }`. Each map is 100 studs longer than the last (map 9: 6000 to 7200, map 10: 7200 to 8500). Luck at its end from GAME_SPEC section 9 (maps 10 to 15: 5M, 25M, 100M, 500M, 2.5B, 10B). `standardScale` about 1.05x the last (1.56, 1.64, 1.72, 1.81, 1.9, 2). `color` is the world's UI colour. |
| `Config/Map` `biomeColors` | `Floor`, `Dirt` (walls), `Grass` (rims and what hangs over the walls). The game adds the checker and studs. |
| `Config/Lighting` `worlds` | Only what differs from the main look. Keep `ClockTime` at 6 or below: the blend tweens it as a plain number, and coming from Starfall's 0 anything later flashes through daylight. |
| `Config/Decor` `corridor` | The same lists as `DECOR` in the script: `floor` (with `extras`), `rim`, `overhead`, `walls`, `spots`. A spot can have `face = "middle"` (turned towards the corridor) or `face = "along"` (down it). `floor` and `rim` can have `zones` ({ from, to, props, gap?, pairs? }) for acts with props of their own; `pairs` twins every prop across the corridor, mirrored (Shattered Mirror's Garden and Ballroom). |
| `Config/PropMotion` | The same as `MOTION`. |
| `shared/Roles.luau` | New glowing roles in `glowing`. |
| `Config/Index` `mapPictures` | The world's picture on its Index card: an in-game shot cropped to 628x553 (`design/index/cards`), uploaded to Roblox. Its colour there is the biome's `color`. |

Then check that the script and the game agree; it catches every drift we've had:

```
/Applications/Blender.app/Contents/MacOS/Blender -b --python assets/models/check_map.py -- build_<map> <WorldId>
```

And compile-check the Luau you touched with lune (`~/.rokit/tool-storage/lune-org/lune/<version>/lune`): load
each file with `luau.compile` from `@lune/luau`.

## 7. Update the docs

- `docs/GAME_SPEC.md`: the map's row in section 8a's table, the world list and the luck table in section 9, and a
  build-notes entry under "World build tasks" like the ones before it (what's in it, colours, what moves, where
  the renders are). Mark what the owner said as **[Owner]** and what we built as **[Built]**.
- `docs/GDD.md`: the biome table.
- Memory, if the owner gave direction about this map's mood or monsters.

## 8. In Studio, after the owner imports

One command does the tidy, for props and monsters alike (Studio open, the imports still in Workspace):

```
python3 assets/models/studio_tidy.py <WorldId> build_<map> build_<map>_monsters
```

It unwraps each import (the importer wraps it in a Model of the same name), moves its pivot to the world origin
(imports come in with the pivot at the Blender origin and no rotation), names parts by bare role, colours them
from the build scripts, makes them SmoothPlastic and anchored with the shared `Studs` material (MaterialService;
not on glowing or face parts), and puts props in `Assets.Maps.<WorldId>.Props` and monsters in `Assets.Dinos`. Then add the monsters to
`Config/Dinos` (step 9) and play-test: count the world's props in `Map.CorridorDecor`, read the console, and take
screenshots with StudioMCP's `screen_capture` (memory `studio-mcp-connection`).

## 9. Its monsters (a separate job)

Copy `assets/models/build_eclipse_temple_monsters.py` (map 9) to `build_<map>_monsters.py`. It uses
`monster_stage.py` (renders, lineup, Gold lineup, walk-and-roar video, saves the `.blend`) and `face_kit.py`
(`classic_mouth`: jaws on a Jaw bone, teeth, a gold tooth, a tongue).

**Each map's 7th and 8th** (owner, 2026-11-06: 8 a map, two more each, 6 at a time, a prompt each): one script a map,
`build_<map>_monsters_7_8.py`, on `rare_kit.py` instead of this template. See the note at the top of `rare_kit.py`.
In `Config/Dinos` they carry `prize = true`, with chances about 4 and 13 times the 6th's and income 3 and 10 times its.

**Monster numbers for a 12-monster map** (owner, 2026-11-14: the end-game maps have 12, and "the next map and next 12
monsters" use the same economy and luck). Nothing new to design; copy map 15's lines and multiply:
- `Config/Dinos`, commonest first. Chance: 2, 4, 12, 60, 400, 3000, then 12007 and 39989 (`prize = true`), then 149993,
  600011, 2500009, 9999991 (`prize = true, apex = true`). Income: 1, 3, 10, 40, 200, 500, 1500, 5000, 20000, 100000,
  500000, 2500000 times the map's first monster, which is 100x the map before's (map 16 starts at 1e30).
- `Config/RarityLadder`: the first 8 letters one step up from the map before (never lower), then `NDOX` (Nightmare,
  Doomsday, Oblivion, Unknown). Map 16's line is already there.
- Nothing else: x100 (up to the 9th), x500 (all 12, leaning rare), the free end-game streak (a 9th or 10th every 300
  throws without one), the guarantees that skip prizes, the Index (12 cards,
  reward on the first 8) and the Sell stand read these two files. `Config/Eggs` needs the map's egg and
  `tools/pace_sim.luau` `LAST_WORLD` the new last map.
- Check with the roll's own code before saying it works (GAME_SPEC section 8, "End-game rarities" has the numbers to match).

**Design.** Six per map, most common first. Style per map: GAME_SPEC section 8a and memory
`later-maps-weirder-monsters`. From map 2 the common ones are silly (goofy names, derpy faces) and the rarest
fierce, the last one a boss, both a step stronger each map; map 8 was calm on purpose. Give the map **one shared
face idea** (Volcano: ember eyes; Starfall: star irises; Eclipse Temple: the eclipse eye) and vary it: in a white
eye for the silly ones, a black socket under a mask or a heavy slanted brow for the fierce ones. Rarer ones stand
bigger: build them bigger, or `grow(m, 1.3)` at the end. Commons are about 3 to 5 tall, the boss 10 to 14.

**Rig.** The game moves bones by name (`DinoLifeController`); any other bone just doesn't move.

| Bones | Made by |
|---|---|
| `Spine` | `m.joint("Spine", pivot)` first, at the hips |
| `FrontL/R`, `BackL/R` (four legs) | `quad_legs(m, ...)` from build_desert |
| `LegL/R` + `ShinL/R` (two legs) | `biped_legs(m, ...)` from build_forest |
| `ArmL/R` | `m.use("ArmL", shoulder)` |
| `WingL/R`, `WingTipL/R` | wings, or extra arms, heads or crystals that should sway |
| `Tail1` to `Tail3` | `tail(m, start, end, 3)` (only 3 move) |
| `Neck`, `Head` | `m.use("Neck", ...)`, then `m.head_joint(yc, d, zc, h)` |
| `Jaw` | `classic_mouth(...)`, called on the Head bone: it snaps as it walks and opens wide in the roar |
| `Swim` | swimmers only (The Abyss): they hover and swim instead of walking |
| `Key`, `Drill`, `Cog` | parts that turn for ever, whatever the monster does: round the upright, its forward axis, its sideways axis (`DinoLifeController` `SPIN`; `build_clockwork_citadel_monsters.py` has the preview). Build the part centred on its bone, along that axis |
| `Lash<n>a`, `b`, `c` (n up to 8) | whips that never stop thrashing: `lash(m, n, points, ...)` in `build_thorn_kingdom_monsters.py`. A monster with these also twitches all over: head jerks, jaw gnashes, body shudders (`DinoLifeController` `THRASH`, `thrash_of` in the script). For aggressive, chaotic maps |
| `Snap<n>` | a spare head's jaw, on the end of a lash: chatters for ever. It opens round the monster's sideways axis, so keep spare heads looking mostly forwards |
| `Drip`, `DripB` | tears falling for ever: `weeping(m, spots, ground)` in `build_weeping_dark_monsters.py`, spaced 0.6 or 1.6 apart. A monster with either bone also **rages**: it lunges, bites, claws and charges (`DinoLifeController` `RAGE`, `rage_of` in the script). For the most aggressive maps. Built before a `grow(m, k)`, pass `grown=k` so the gap comes out right |
| `PalmL`, `PalmR` | hands held to the face that pull away in the roar and the lunge (Endless Grief): turn on the upright, pivot behind the wrist |
| `Vent<n>` | spore clouds rising for ever out of a vent: `vent(m, n, base, parent, ...)` in `build_spore_hollow_monsters.py`, made by its `finish(m, k)` after the grow so the clouds stay 0.6 apart. A monster with these also **pounces** every 4 seconds: rears back, then lunges, jaw flung open, arms raking (`DinoLifeController` `POUNCE` and `VENT`, `pounce_of` in the script). A step below `RAGE` |
| `MandL`, `MandR` | side jaws (mandibles, pincers, a mouth that opens four ways): `rot_maw(..., mandibles=dict(...))` in `build_spore_hollow_monsters.py`. They gnash, spread when the monster rears and fling open in the roar, turning on the upright |
| `Sway<n>a`, `b`, `c` (n up to 8) | slow waves down a chain: feathers, cloth, sails, moss. `chain(m, "Sway", n, points, ...)` in `rare_kit.py`, or one `Sway<n>a` for a stiff feather. `Wriggle<n>a`, `b`, `c` is the same but fast and wide: a worm lure (`DinoLifeController` `SWAY`, `sway_of` in `rare_kit.py`, for all the bones in the rows below too) |
| `PinchL`, `PinchR` | a pincer's moving outer finger: eases open, snaps shut every 2 seconds, one half a beat after the other, flung open in the roar. Pivot at the finger's root |
| `Sting` | a scorpion's stinger, the last bone of the tail: draws back, then stabs, every 4 seconds |
| `Flick` | a forked tongue, under the Jaw: darts out twice every 2 seconds |
| `Slither1` to `Slither8` | a snake's body, each the child of the one before, from the Spine down to the tail tip: a wave runs down them, gently at rest and wide on the move. No legs needed: with these the reveal's walk glides like a swimmer's |
| `Strike` | between the Spine and the Neck: rears back and lunges every 4 seconds, and the Jaw bites along with it. The most a map-3 monster does |
| `Spit1` to `Spit6` | fire: `fireball(m, n, at, size)` in `build_volcano_monsters_7_8.py`, parked inside the head and thrown out one after the other as the `Strike` lunges (jaw held wide, `MandL`, `MandR` snapping, wings beating). Map 4 |
| `Step<n>` | a centipede's legs, one bone for each `Slither<n>`, its child: a ripple down the sides, wide on the move |
| `Kick1` to `Kick4` | snow off the hooves: `chunk(m, "Kick", ...)` in `build_frozen_peaks_monsters_7_8.py`, parked in the belly on `Root`. With these it **charges**: paws, sinks back, throws its whole body forward head down. Map 5 |
| `Shard1` to `Shard6` | ice off the ground, the same on `Root`. With these it **smashes**: both `ArmL`, `ArmR` up over its head, then down. The arms must reach the ground from the rest pose. Map 5 |
| `Stab`, `BuzzL`, `BuzzR` | a needle that stabs twice every 4 seconds as the body dips and the `FrontL`, `FrontR` reach in; wings that blur. Map 6 |
| `Curl1` to `Curl4`, `Thumb` | a hand's fingers, each `Curl` the middle joint under a `Front` or `Back` bone: drums them one by one, then rears and **grabs**. Map 6 |
| `PunchL`, `PunchR`, `ClubL`, `ClubR`, `Shock1`, `Shock2`, `Bubble1` to `Bubble4` | a folded arm that snaps out, one side then the other, a ring of shock flying off each: `punch_arm` and `shock_ring` in `build_abyss_monsters_7_8.py`. Map 7 |
| `SeizeL1` to `5`, `SeizeR1` to `5` | long arms held up in a curve that unroll straight, strike and drag back: `hunting_arm` in the same script. `SEIZE_TURN` is how far each joint turns, worked out from `SEIZE_PATH`, so change the two together. Map 7 |
| `Spout1` to `Spout6`, `Fall1` to `Fall6` | stars out of a blowhole; meteors down the `METEOR` line (`rare_kit.py`), their tails built pointing back up it. Calm, for map 8: the face doesn't change, only the sky does |
| `Orbit` | turns round the upright, once in 8 seconds, on `DinoLifeController` `SPIN`: a moon built off to one side of a bone in the middle of the monster |
| `ArmL`, `ArmR`, `ScytheL`, `ScytheR`, `Crescent1`, `Crescent2` | scythes up and down, and blades thrown out and back: `to` equals `from` and the arc is a Vector3, so it flies out along it and returns, spinning. Map 9 |
| `Maul` | between the Spine and the Neck, on a piece of the chest: maps 10 to 12's bare monsters. Every 2 seconds the whole front lunges, the Jaw bites three times, Neck and Head shake, arms rake, legs drive. `beast_head` in `rare_kit.py` is the shared head: mostly mouth, small slit eyes, no glow. Check the jaw reaches no lower than the floor: a long head needs a small `gape` |
| `Whirl`, `Gore`, `Gulp`, `Bounce`, `Pummel`, `Reach1` | maps 13 to 15's bare monsters, the most aggressive of all, one attack each (`WHIRLER` and friends, built from `beat`, `wave`, `hop` and `stacked`, line for line in both files). `Whirl`: the waist, top half spins twice; build the top as its own round piece turning in a bowl of hips, never one skin, or it twists shut. `Gore`: the chest, with `Quill1` to `8` (thorns that stand up, negative pitch when they lie back). `Gulp`: the throat; `Head` flings back, so `Jaw` must turn the other way or it goes up with it. `Bounce`: the chest, with `HockL`, `HockR` (the lower hind legs). `Pummel`: the chest, with `ForeL`, `ForeR`; fists must reach the ground at rest. `Reach1` to `12`: a neck with a bone for every ring, each sliding 1.7; fewer bones stretch into stairs |
| `Ring1` to `Ring4` | rings of sound, with `Swim`, `WingL`, `WingR`, `WingTipL`, `WingTipR`: wings beat, it climbs, screams, folds them and drops. `Swim` makes it a flyer: no feet, and the reveal glides. Map 9 |
| `Prowl`, `Frill` + `Rosette`, `Twist`, `Swing` + `Club`, `Reflect`, `Rampant` + `Sliver1` to `20` | Shattered Mirror (map 16), one attack each (`build_shattered_mirror_monsters.py`): circles you, rears and runs on two legs, head turned right round then a jerky lunge (`stepped`), pendulum tail and slam, two necks striking like shears, rampant. A marker table's `"@always"` holds moves that run all the time on top of everything, attack or not: `Rosette` and `Club` turn for ever, the swan's necks sway as mirror images (`mirrored`, `NeckL1` to the R side), and each `Sliver` slides along its own way out of the skin and back in, a stadium wave (`along`; the ways are worked out the same in both files). A sliding shard must be sunk deeper than its wave and burst together slide it (`MANE_SUNK`), or it comes out and floats |
| `Stilt` + `VaneL/R1-5`, `Prism` + `Sail1-7`, `Flutter` + `LoopA/B`, `Train` + `Eye1-13`, `Glass1`-`8` + `LoopA/B`, `Royal` + `PaneL/R1-5` + `Tiara` | Map 16's six rarest (`build_shattered_mirror_rare.py`): shards that float free of the body, each on its own bone, moved all the time by `"@always"` (`bob` along a way, `spun` rings) and thrown out and back in the attack one after another (`thrust` with `volley` keys). Owner, 2026-11-14: no head or mouth shared across a set, no `fierce_head` rows of teeth by default, two-legged bodies that aren't humanoid (`bird_leg`, `raptor_leg`), the rarest the best looking. A floater hidden inside something thin (the face in the mirror) can be no deeper than what hides it |

`Spit1`, `Kick1`, `Shard1`, `Stab`, `Curl1`, `Whirl`, `Gore`, `Gulp`, `Bounce`, `Pummel`, `Reach1` and `Strike` are **markers**: a monster with one has the rest of its body moved by that bone's table (`MARKED` in `DinoLifeController` and `rare_kit.py`, which must stay equal). Thrown bits are in `FLING` / `fling`: parked out of sight, they jump to `from`, fly to `to` and snap back, so `to` should end below the ground. Their numbers are per bone name, not per monster, so a new thrower with different feet or fists needs new bone names.

**Spare eyes** use the role `Slit` for their pupils, not `Pupil`: the reveal aims at the middle of the `Pupil` parts, so an eye on a stalk would drag it away from the face. **Jaw** must sit in front of `Tail1` (or the `Spine` if there's no tail): that's how the game reads which way a monster faces.

Blocks go on whichever bone `m.bone` names when they're added; `m.stretch(role, bone)` right after a neck or tail
piece keeps its back end on the bone before it. Set `m.head_centre` (for the face renders).

**Roles.** Skin is `Body`, `Accent`, `Belly`, `Claw` (the colour mutations recolour these). Face roles `EyeWhite`,
`Pupil`, `Highlight`, `Mouth`, `Tongue`, `Teeth`. Anything that must keep its colour through a mutation (gold,
plumes, jade) gets its own role. Glowing ones follow the same rules as props (step 3).

**Run it:**

```
QUICK=1 QUICK_OUT=<scratch folder> Blender -b -P build_<map>_monsters.py              # stills, about 15 s
ONLY=idol_ollie QUICK=1 QUICK_OUT=<scratch folder> Blender -b -P build_<map>_monsters.py  # just one
Blender -b -P build_<map>_monsters.py                                                # everything, a few minutes
Blender -b --python check_map.py -- build_<map>_monsters <WorldId>                   # roles and glow
```

Look at each one whole, its face, and straight on; check the faces read at a glance and that the rarer ones look
it. Then add `"<map>_monsters": "NN_<Map>"` to `MAP_OF_FILE`, export (step 5) into `fbx/NN_<Map>/Animals/`, and
once they're imported and tidied (step 8), list them in `Config/Dinos` (ids never change; chances
2, 4, 12, 60, 400, 3000; income 100x the map before's, rank by rank). Then eggs can land in the world.

## 10. Pitfalls we've hit

- **The importer turns models round** (most face +Z in Studio). Never rely on a yaw to face something; use a
  Front marker and `face`.
- **The corridor got wider** (72 to 88). Overhead props stay modelled for 72 and are stretched; the preview stage in
  `map_kit` is the real size.
- **ClockTime tweens as a number** (step 6).
- **Glow clips in renders** at high emission, turning green into cyan. It's the preview, not the model.
- **`beam` picks its own width direction**, which lays horizontal rays and feathers on their edge. Use `plate`.
- **Parts that move together but turn round different centres** come apart. See step 4.
- **Floating bits:** something placed on a tier or ledge you didn't check the size of. Look at each still.
- **Flicker (z-fighting):** two faces in exactly the same place shimmer as the camera moves (a brace ending flush
  with a leg's face, a stripe overlapping the next one, a ring of a ball exactly on a cap's top). Run
  `Blender -b --python assets/models/check_flicker.py -- build_<map>` and nudge what it lists. The preview corridor
  in `map_kit.py` had it too (its hanging grass lay flush on the wall; fixed 2026-11-04, map 11).
- **Two accounts, one folder:** shared files change under you. Re-read before editing; commit only your own hunks.
- **Drift wins over every other move.** In the game a prop with `"*": drift` moves all its parts itself, so its
  spins, swings and bobs never show (the Blender video still plays them). A sky piece that has to turn something
  (propellers) bobs in place instead (map 12's airships).
- **Don't tie a turn to a bob** (a beam engine's rocking beam and its piston). Importers can flip X or Y, which
  reverses every turn but never a bob, so the two would come apart. Turns that only depend on each other are fine:
  meshing gears both reverse and stay in mesh.
- **The far end:** the corridor stops at an end wall 36 studs past the last map's end (`Map.corridor.extra`), 8 thick.
  Anything standing against it must clear it: map 15's eye first landed inside the wall, where nobody would ever see it.
- **Something you read one way from the flight** (a face on the floor): a Front marker and `face = "along"`, as yaw alone
  isn't safe, and remember the far end of the prop is the top of the screen.
- **Blender's previews flatter a dark map, so test in play.** Things map 15 only showed in Studio:
  - The sky at night is black with stars, whatever the preview's sky colour says, so a dark shape against it vanishes.
    To get a dim sky: `Haze` carries the fog's colour up the sky (and hides the stars), `Density` is what hides objects,
    so use high Haze and low Density (6 and 0.24).
  - ClockTime 6 still draws a night sky with stars. For a dawn-coloured sky use the same trick: high Haze in a warm
    colour (Shattered Mirror: (255, 176, 150) with Haze 4.5 came out dusty pink; a pink colour came out lavender).
  - Roblox tints the night atmosphere blue, so a grey `Color` gives a blue sky. Warm it to cancel that: (158, 124, 97)
    came out neutral grey; (170, 94, 47) was brown. Don't desaturate the screen instead, it kills the colour you kept.
  - Neon turns any hint of a colour into that colour. For a truly grey glow use a pure grey, R = G = B.
  - PointLights are much stronger on mid-grey parts than a Blender point light: start around brightness 1.
  - Sky pieces look far smaller from the corridor than in a close render: check from the flight camera's height.
  - A world this dark hides its own monsters from the reveal. A world's `reveal` table in `Config/Lighting` lifts its light
    while a reveal is on, for a monster of any size.
  - The Studio pane can be very wide and short. To check a dark map: anchor the player near the spot on the Server, hide
    the GUI, and set a Scriptable camera on the Client (it resets when the script ends, but holds for the capture).
- **Rare monsters that read as the wrong animal** (the first Therizinosaurus, 2026-11-06). White body and orange legs and bill: a
  goose. Upright pink crest and a beak: a rooster. The fix was never more detail. Check the render for "what is this at a
  glance", then change the colours and the part that says the wrong animal: a soft muzzle instead of a bill, feathers swept
  back instead of up. A round ball eye with `cap()` irises and skin `lid()`s sets the mood far better than flat square plates.
- **Check monsters for flicker before exporting:** `Blender -b --python assets/models/check_flicker_monsters.py -- build_<map>_monsters_7_8`. `check_flicker.py` only finds flat faces in the same plane; monsters shimmer on curves too. The usual causes: layers of an eye too close (`slit_eye`'s `layer` keeps them 0.04 apart), teeth grazing a mouth plate (root them in the jaw, keep the plate narrower), a body's end cap showing inside an open mouth, a flat bump lying along a body (make it stand up), a claw running along the end of a limb (start it wider).
- **Build a body as one sweep from rump to skull,** with a bone per ring. Separate blocks for chest and neck leave steps at every joint, and `beast_head`'s skin at the corners of the mouth is what stops the jaw looking bolted on.
- **The reveal meets a monster head on.** Every catch ends looking straight at its face, so judge a render from the front as well as the three-quarter view. Eyes on the sides of a whale's head left a blue ball in the reveal (2026-11-06): set them forward and give it a line of mouth, however unlike the real animal. In a play test, end a reveal with Space and make a new egg and move the player back each time: the reveal eats the egg and sends the player home.
- **Smooth it before you add detail.** `sweep_fine` and `fine` (`rare_kit.py`) put more rings on a smooth curve, `ring_round` makes rims, `sheet` makes real wings and fins. A stack of `sweep`s reads as boxes; flat `poly` fins read as cardboard. Straight legs read as a table: give every leg a bend, a thin wrist and a real foot. Keep the bones and the joints thrown bits aim at where they are and the attacks don't change.
- **A preview that adds to a pose needs a pose to add to.** `sway` adds a marker's move to what the walk and idle set, so a bone they don't set builds up frame by frame. A flyer's wings drifted into a cloak in the video (2026-11-06); the game was never wrong. If a preview looks mad, check it against the numbers before changing the model.
- **Park thrown bits on the bone that carries the body.** Parked on `Root`, a monster that really moves leaves them hanging in mid air: the bat's rings stayed behind when it dived, so theirs are on `Swim`. `Root` is fine when the body only leans. And a meteor's or a star's whole length has to fit inside the body when parked, or it pokes out of the monster's back.
- **Heads from a table, teeth round the front** (maps 13 to 15's pairs, 2026-11-06). All six on `beast_head` came out as one rat head on six bodies, and head on its teeth were two white curtains: rows that stop short of the tip are seen end on. `fierce_head` in `fierce_kit.py` takes a skull table per monster and runs the teeth right round the jaw on a gum. `beast_head` stays for maps 10 to 12. Bigger eyes need their socket to stop short of the iris and a bigger `layer`; a big head's jaw needs its lowest point measured, not just the `gape` guessed. Pale bumps on a dome read as a sesame bun: use bone spikes.
- **A face is a surface.** Features placed by eye on a new head can land inside it (the Constellion's did, twice). Work out the surface from the rings, and for a lion keep the skull short with the mane right round it, or it reads as a capybara.
- **A `sweep` of one short piece picks its own frame.** Plates along a long body twisted at random until each was given `up=` the body's own normal from `frames_along`.
- **An eye sunk in a `Socket` egg vanishes.** The socket must stop short of the eye's front, or you get a black ball. And a ring of fur round a face runs straight through an open mouth: skip the spikes where the mouth opens.
- **Scales or feathers in a ring stripe if they alternate colour** (`scallop`): flaps overlap, so only a sliver of each shows. One
  colour a ring, alternating ring by ring.
- **A squashed `cap` dips under the one below it** between its corners, so a slit pupil comes out jagged: lift it a few percent
  and cut it finer (`slit_eye` does).
- **The importer drops a bone with no mesh on it.** Endless Grief's empty marker bone vanished, and with it the thing that
  turned its rage on. A bone the game looks for must carry something, and check the bones in Studio after an import.
- **`about = "self"` turns round the bounding box's middle.** Give a gear or a wheel an even number of teeth and
  spokes so that middle is its axle, or it wobbles.
- **Monsters meant to be scary that came out as toys** (map 14's first six; the owner rejected them, 2026-11-06). What read
  cute: a flat bar of a pupil across a round glowing eye (sleepy), big round glowing orbs (googly), red caps with spots
  (a game's power-up), a cone or dome cap on a head (a witch's or a bowler hat), a thick flat-topped upper jaw (a box or a
  treasure chest), straight thick legs (a table), small mouths and upright poses. What read scary: small burning eyes with a
  thin upright slit in a black socket under a brow slanting hard to the nose, no white; a mouth that is most of the face,
  hanging open on long needle teeth; dark bodies with bone-pale teeth, claws and spikes; heads low and thrust forward,
  limbs reaching. `build_spore_hollow_monsters.py` (`rot_eye`, `rot_maw`) and `build_weeping_dark_monsters.py` have both.
