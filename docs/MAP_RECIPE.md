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

Copy `assets/models/build_forbidden_library.py` (map 10, the newest, with the plain-colour setting and helpers for
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
| `Config/Decor` `corridor` | The same lists as `DECOR` in the script: `floor` (with `extras`), `rim`, `overhead`, `walls`, `spots`. A spot can have `face = "middle"` (turned towards the corridor) or `face = "along"` (down it). |
| `Config/PropMotion` | The same as `MOTION`. |
| `shared/Roles.luau` | New glowing roles in `glowing`. |
| `IndexController` `CARD_COLOURS` | The world's two card colours (used once it has monsters). |

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
- **`about = "self"` turns round the bounding box's middle.** Give a gear or a wheel an even number of teeth and
  spokes so that middle is its axle, or it wobbles.
