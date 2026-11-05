# How the maps and monsters are built

How the models and their animations were made for **map 12, Clockwork Citadel** (its world and its 6 monsters) and
**map 13, Thorn Kingdom** (its world). It explains what was done and why. The step-by-step checklist for the next map
is `docs/MAP_RECIPE.md`; what the owner wants is `docs/GAME_SPEC.md`, which wins over both.

## 1. The idea in one paragraph

Nothing is modelled by hand. Each map is a Python script that runs inside Blender and **builds every model out of code**:
boxes, tapered boxes, columns, balls, plates and beams, placed by numbers. The same script renders pictures and videos
to check the result, and saves a `.blend` file. A second script exports one FBX file per model. The owner imports those
into Roblox Studio, and a tidy script finishes them there. Animation works the same way: the moves are **numbers in a
table** (spin this part 20° a second, swing that one 12° each way), which Blender plays in its preview videos and the
game plays on each player's screen. Because both read the same numbers, what the video shows is what the game does.

## 2. The pipeline at a glance

| Step | What happens | Tool |
|---|---|---|
| 1. Design | Theme, colours, ~19 props, what moves; written as the script's opening text | `build_<map>.py` docstring |
| 2. Build | The script makes every model from shapes, one mesh per colour | Blender, background mode |
| 3. Look | Stills per prop, line-ups, corridor shots, two videos; fix and run again | `-- stills` takes ~20 s |
| 4. Check | Script vs. game configs; flickering faces | `check_map.py`, `check_flicker.py` |
| 5. Wire in | The world's colours, light, placement, motion, glow in the game's configs | `src/shared/Config/*.luau` |
| 6. Export | One FBX per model, into `assets/models/fbx/NN_<Map>/Props` (or `Animals`) | `export_fbx.py` |
| 7. Import | The owner imports the FBX files into Studio (File > Import 3D) | Studio |
| 8. Tidy | Names, colours, studs, pivots, folders, all done for you | `studio_tidy.py` |
| 9. Play-test | Count what's placed, read the console, take screenshots | Studio MCP |

The commands are in `docs/MAP_RECIPE.md`.

## 3. How a prop model is built

**Shapes from a shared kit.** `assets/models/map_kit.py` gathers the shape helpers every map uses (block, loft,
prism, ball, beam, plate, limb, disc, ring, hoop, gem). Each map script adds the shapes its theme needs:

| Script | Shapes it added |
|---|---|
| `build_clockwork_citadel.py` | `gear` (toothed rim, spokes, hub), `wheel` (flywheels), `puffs` (steam and smoke columns), `bolt` (zigzag lightning), `gauge`, `handwheel` (valve wheels), `tube`, a turned `Frame` to build in |
| `build_thorn_kingdom.py` | `rose` (three rings of petals round a glowing heart), `thorn_vine` (a twisting briar with thorns), `leaf`, `petal_column` (falling petals), `fireflies`, `banner`, `crenels` (battlements), `cone_roof` |

Map 13 imports map 12's helpers instead of copying them, so each script stays about its own world.

**One mesh per colour role.** Every shape is added to a named *role*, such as `Brass`, `Iron` or `RoseGlow`. Each
role becomes one mesh with one colour, and in Studio one part named after it. That matters because:
- **colour**: the tidy script colours each part from the role's colour in the script;
- **glow**: a role listed in `shared/Roles.luau` `glowing` becomes Neon in the game (roses, lamps, furnaces, sparks).
  These names are shared by the whole game, so a new glowing name must not be used for something dull anywhere else.
  Before naming them, I dumped every role used by every model to check;
- **motion**: a part that moves is its own role, so the game can move it without moving the rest.

**Plain colours, no studs in Blender.** Since map 10 the Blender materials are plain colours. The classic Roblox studs
come only from Studio's shared "Studs" material, which the tidy script puts on every part except the glowing ones.

**Conventions every prop follows.**
- **Orientation:** 1 Blender unit = 1 stud. Props stand on Z = 0 and face +Y.
- **Front marker:** props that must face a certain way (landmarks turned towards the corridor, wall props, overhead
  bridges, sky pieces) carry a tiny `Front` part. The game turns the prop by it and deletes it, because Studio's
  importer often turns models round.
- **Wall props:** these (map 12's molten brass falls, map 13's briar curtains) hang from the wall's top edge, at least
  1.5 studs out from the wall.
- **Overhead props:** these (gear arches, stone bridges) stay entirely above the rims, so the flight camera never
  hits them.
- **Flat floor props:** these (floor gears, rose windows) are under half a stud tall, so eggs can land on them.

## 4. How props move

The moves live in the script's `MOTION` table and in the game's `Config/PropMotion.luau`, with identical numbers.
`PropMotionController` plays them on each player's screen only, for props near the camera, so they cost the server
nothing.

| Move | What it does | Examples |
|---|---|---|
| `spin` | turns at a steady speed | gears, valve wheels, the music box's bird, ravens round the moon |
| `swing` | rocks back and forth | lanterns, banners, the metronome arm, weather vanes, gauge needles |
| `bob` | rises and sinks | the floating crown, airships, the moon |
| `pulse` | the glow dims and brightens | furnace doors, roses, stained glass, the mirror's eyes |
| `fall` | drops and starts again (negative rises) | steam, smoke, falling petals, water drops, molten brass |

Each move also says **what it turns round**: the part's own middle (`about = "self"`), the prop's upright axis, or
a sideways line at a set height (`axis = "across"` / `"ahead"` with `height`).

### Techniques that make the moves look right

- **Meshing gears.** Two gears stay in mesh when they turn at the inverse ratio of their teeth: 16 teeth against 8 means
  the small one turns twice as fast, the other way. Their teeth must be the same size, and the small one starts with a
  gap where the big one's tooth comes in. Spins in the game have no random offset, so they stay locked together.
- **Turning on its own middle.** `about = "self"` turns a part round the middle of its bounding box. A gear or
  wheel with an odd number of teeth or spokes has its box off-centre and wobbles, so every one has an even number.
- **Never-ending columns** (steam, petals, drops, sparks). Pieces are placed exactly one step apart, and each one
  falls (or rises) exactly one step and starts over, so each only travels as far as where the next began. The loop is
  invisible. Map 12's brass falls use 4-stud steps, map 13's petals 3 or 4.
- **Lanterns on hooks.** A lantern, its chain and its glow are three roles with the same swing round the same point:
  the hook. The hook is built either straight above the prop's origin, or on the sideways line at the hook's height,
  which the game turns round (the knight's held-out lantern, the lamp post's arm, the bridge's banners).
- **Banners.** Swinging banners carry no separate trim part, since a part with no move would stay behind.

### Three things the game does that Blender's preview doesn't show

I found these by reading `PropMotionController.luau` before designing the moves; they're now in the recipe's pitfalls.

1. **Drift wins over everything.** A prop that drifts across the sky has all its parts moved by the drift, so its
   spins and swings never show. So the airships and the moon bob in place instead of drifting, and their propellers
   and ravens keep turning.
2. **A turn tied to a bob can come apart.** Studio's importer can mirror a model, which reverses every turn but never a
   bob. A rocking beam engine whose piston bobs could end up moving the wrong way, so I didn't build one. Turns that
   only depend on each other (meshing gears) both reverse and stay in mesh.
3. **Parts that move together must turn round one point**, or they drift apart as they move.

## 5. How the monsters are built (map 12)

The monster script is `build_clockwork_citadel_monsters.py`. It uses the shared `monster_stage.py` (renders, line-ups,
the Gold line-up, the walk-and-roar video) and `face_kit.py` (the jaw).

**Design.** Six per map, most common first. The common ones are silly and the rare ones fierce, then a boss. All six
share one face idea, varied by rarity:
- **The shared face, the "lens eye":** a riveted brass bezel round a glass lens with a glowing iris. The silly ones
  have white glass and an electric-blue iris; the fierce ones have dark glass, a furnace-orange glare and an iron lid
  and brow slanting down to the nose, which is what reads as angry. A level lid reads grumpy (Kettle Belly).
- **The shared clockwork mark:** a wind-up key in every back.

**Rig (bones).** The game moves bones by name, so each body part goes on the right bone:

| Bones | Who has them |
|---|---|
| `Spine` | everyone, at the hips |
| `LegL/R` + `ShinL/R` | two-legged: Wind-Up Wally, Kettle Belly, Gearjaw, Chrono Rex |
| `FrontL/R`, `BackL/R` | four-legged: Sprocket, Drillhorn |
| `ArmL/R` | stubby arms and Kettle Belly's wrench claws |
| `Tail1`-`Tail3` | tails, and Sprocket's coil spring |
| `Neck`, `Head` | heads |
| `Jaw` | everyone: snaps as they walk, opens wide in the roar. It must sit in front of the Spine, because the game reads which way a monster faces from it |
| `WingL/R` | Sprocket's floppy ears, which flap as it trots |
| **`Key`, `Drill`, `Cog`** | **new on map 12**, see section 6 |

**Colours and mutations.** The skin roles `Body`, `Accent`, `Belly` and `Claw` are what the Gold and Diamond
mutations recolour. Brass trim, keys, rivets, steel, glass and the face keep their colour, so a Gold monster still has
readable eyes and teeth. Rarer monsters stand bigger, either built bigger or scaled with `grow()`: from about 3.5 studs
(Wind-Up Wally) to about 12.5 (Chrono Rex, with its gear sail).

## 6. How the monsters move

The game's `DinoLifeController` plays a walk loop (one stride a second), an idle loop (8 seconds) and once per idle a
roar: head up, jaw wide, arms out. The Blender preview plays the same poses, using the same formulas.

**New for map 12: parts that spin for ever.** A clockwork monster needed its key, saw, drill and gear to keep turning.
The walk and idle are blended into each other whenever a monster starts or stops walking, and a spin blended like
that would whirl oddly. So I added a separate `SPIN` table to `DinoLifeController`. It turns three bone names at a
steady speed on top of whatever pose the monster is in:

| Bone | Turns round | Speed | Used for |
|---|---|---|---|
| `Key` | the upright | half a turn a second | the wind-up key in every back |
| `Drill` | its forward axis | two turns a second | Drillhorn's nose drill |
| `Cog` | the sideways axis | half a turn a second | Gearjaw's buzz saw, Chrono Rex's gear sail |

- **Building rule:** a spinning part must be built centred on its bone and along that axis, or it wobbles.
- **Speeds:** chosen as whole half-turns per stride, so the 1-second walk and the 8-second idle loop seamlessly in
  the Blender preview, because a key or gear turned half way round looks the same.
- **Safe for older maps:** no earlier monster has bones with these names. I checked before adding them.

## 7. How everything is checked

- **Looking:** every prop and monster gets its own still, plus contact sheets (several stills in one picture), corridor
  shots from the flight camera's height, and two videos. I looked at each and fixed what read wrong. For example:
  - map 12's dotted watch lid looked like a biscuit;
  - its brass trees looked like straw, until their crowns were rebuilt from little gears;
  - map 13's thicket vines planted on the ground like spider legs;
  - the rose tower's bloom lay flat;
  - the fierce monsters' brows flared up like owl ear-tufts.
- **Motion:** checked frame by frame in the videos (gear teeth staying in mesh, lanterns swinging round their hooks)
  and, for the monsters, by reading bone positions out of the saved `.blend`.
- **`check_map.py`:** proves the script and the game agree: `MOTION` = `Config/PropMotion`, `DECOR` = `Config/Decor`.
  It also checks that every glowing role is in `Roles`, that moving roles exist, that props which must face a way have
  a Front marker, that flat props are flat and overhead props stay above the rims, and that the world is in every
  config. Decor and PropMotion entries are generated from the script, so there are no typos to drift.
- **`check_flicker.py`:** finds two faces lying in the same place, which shimmer in Studio. Visible ones are fixed by
  moving a shape a fraction of a stud; hidden ones (inside another shape) don't matter.
- **In Studio:** after the import and tidy, a play-test counts the props the game placed (map 12: 332, map 13: 339,
  every kind present, all Front markers removed), reads the console (no errors) and takes screenshots. For map 12's
  monsters it also confirmed the game's throw range now reaches the end of the world, and that the spinning bones turn
  while the game runs.

## 8. Where everything is

| What | Map 12, Clockwork Citadel | Map 13, Thorn Kingdom |
|---|---|---|
| World script | `assets/models/build_clockwork_citadel.py` | `assets/models/build_thorn_kingdom.py` |
| Monster script | `assets/models/build_clockwork_citadel_monsters.py` | not made yet |
| Blender files | `clockwork_citadel_models.blend`, `clockwork_citadel_monsters.blend` | `thorn_kingdom_models.blend` |
| FBX files | `assets/models/fbx/12_ClockworkCitadel/Props`, `Animals` | `assets/models/fbx/13_ThornKingdom/Props` |
| Renders and videos | `design/world/models_clockwork_citadel/`, `monsters_clockwork_citadel/` | `design/world/models_thorn_kingdom/` |
| Game configs | `Config/Biomes`, `Map`, `Lighting`, `Decor`, `PropMotion`, `Dinos`; `shared/Roles.luau`; `IndexController` card colours | the same, without `Dinos` |
| Monster motion | `DinoLifeController` `SPIN` | |

## 9. What the next map should keep

- **Read first:** `docs/MAP_RECIPE.md`, then copy the newest script and only replace the theme, colours, props and
  tables.
- **Design the moves around what the game does** (section 4), not just around what looks good in Blender.
- **Look before checking.** Contact sheets catch what no checker can: a face that doesn't read, a shape that looks
  like something else.
- **Two accounts share this folder.** Edit shared files in small exact edits, and commit only your own lines.
