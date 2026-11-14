# Throw Eggs for Dinosaurs: Full Game Spec

Everything the owner has said about the game and how it should look, in one place.
**When this file disagrees with `docs/GDD.md` or the code, this file wins.** Section 14 lists what has to change.

How to read the tags:

- **[Owner]**: the owner said this. It's a rule.
- **[Seen]**: read from screenshots of the reference game. Very likely right, but not stated by the owner.
- **[Guess]**: an estimate. Check it before relying on it.
- **[Built]**: already in our game. Numbers can be tuned.

Reference game: "Throw Food for Animals" on Roblox. Screenshots are in `docs/reference/` (section 16).

---

## 1. The game in short

You train to get stronger, throw an egg as far as you can down a long corridor through different worlds, and a
dinosaur comes to it where it lands. The farther the egg goes, the more luck you get and the rarer the dino. Dinos
stand on your base and earn money. Money buys better eggs and more training, so you throw farther. Repeat.

**The joke of the game [Owner]:** bases stay tiny while the animals keep growing. Animals start small on the first
map, but each map's are bigger than the last, so a late-game player's dinos look ridiculously too big, spilling over
the fences and onto the neighbours' bases and towering over the whole map. Bases are **not** designed to give dinos
room. This is the look we want on purpose, and it's what makes the game funny and gives players something to show off.

---

## 2. How we work

- **[Owner]** Same structure and mechanics as the reference game, and the map should look very similar to it.
- **[Owner]** Our own names, models, numbers and assets: eggs and monsters (dinos among them) instead of food and animals. Nothing is
  taken directly from the reference game.
- **[Owner]** Don't add systems the reference game doesn't have without asking. Rebirth was rejected for this reason.
- **[Owner]** Models are made plainly in Blender, with no studs modelled in. The stud texture is applied afterwards in
  Roblox Studio. Almost everything in the game has studs, including every model.
- **[Owner, 2026-11-04]** From map 10 on, the Blender models carry no stud texture at all, not even the old
  round-stud preview image the earlier maps' materials had: plain colours only, so the one stud texture is the
  one used now, Studio's shared "Studs" material (`docs/MAP_RECIPE.md`, steps 3 and 8).
- **[Owner]** UI is designed in Figma ([file](https://www.figma.com/design/PZ3emJUorfZBWQoLe1zCfv), page "UI design v2").
- **[Owner]** Big jobs get split into separate tasks so each is done well.
- **[Owner]** The owner is a first-time game developer with no coding background: explain Studio steps plainly.
  Prompts written for Codex must be in English.
- **[Built]** Luau code synced to Studio with Rojo. Tunable numbers live in `src/shared/Config/`.
- **[Owner]** The server decides everything that matters: rolls, cash, power and throw distance. The client only
  sends the timing-meter result, which the server checks. Saves use DataStore with a session lock and retries.

---

## 3. The map

### Overview

**[Owner]** Each server has **5 players**, so the map has **5 bases**.

**[Seen]** The whole map is one sunken, rectangular arena with a raised grass rim, and the corridor leaves from one side:

```
   ┌──────────────── raised grass rim, pumpkins along the edge ───────────────┐
   │   dirt wall with grass hanging over it (all four sides)                  │
   │                                                                          │
   │   back strip: small decorations (dead trees, graves, lamp posts)         │
   │                                                                          │
   │   ┌────────┐┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐                  │
   │   │ base 1 ││ base 2 │ │ base 3 │ │ base 4 │ │ base 5 │  one single row  │
   │   │        ││        │ │        │ │        │ │        │                  │
   │   └──╴ ╶───┘└──╴ ╶───┘ └──╴ ╶───┘ └──╴ ╶───┘ └──╴ ╶───┘  gates face front │
   │    shop, rack and sign are right outside each gate (section 5)           │
   │                                                                          │
   │   big open grass, where players walk                                     │
   │                                                                          │
   │        SELL stall                                                        │
   │                                                                          │
   └───────────────┐  ▓▓▓▓ orange throw platform ▓▓▓▓  ┌──────────────────────┘
       raised grass│        white dashed line          │raised grass, trees
       rim         │  ↓ drop down to the corridor ↓    │
                   │                                   │
                   │    World 1 floor (lower level)    │
                   │    walls on both sides            │
                   ▼             continues...          ▼
```

### What's in it

- **Bases [Seen]:** one single row across the back half, side by side, with small gaps. They fill the arena's width.
- **Open ground [Seen]:** the front half of the arena is empty checkered grass.
- **Walls [Seen]:** brown checkered dirt on all four sides, with chunky grass blocks hanging down over the top.
- **Rim [Seen]:** flat checkered grass above the walls, with pumpkins evenly spaced along the edge. There are big
  blocky trees and bushes on the rim near the corridor.
- **Throw platform [Seen]:** an orange and yellow checkered strip set into the arena's front wall, with a white dashed
  line along the arena side. You walk onto it from the arena, level with the ground.
- **Corridor [Seen]:** starts below the platform, so the platform's front is a dirt face and the corridor floor is
  lower than the arena. In the first world it's **one tall wall on each side** with grass hanging over it, a floor with
  blocky trees, hedge mounds, stumps and rocks kept away from the middle, thin pale lines across the floor, and more
  trees on the rim above. Far worlds look like **a valley with three levels**: the centre floor, a ledge on each side,
  then a second wall up to the rim (`video-flight-corridor-levels.jpg`). Beyond the rim, the outer dirt faces drop away
  into the sky, so the whole map reads as a floating island.
- **Decorations [Seen]:** pumpkins, jack-o'-lanterns, graves and dead trees. Some of this is the reference's Halloween
  event, so the seasonal items aren't permanent.
- **Sky [Seen]:** bright blue in some shots and dark purple in others, a minute apart. It may be a fast day/night
  cycle or an event (see section 15).

### Starting sizes [Guess]

Measured roughly against the player's height (about 5 studs). Check against a straight top-down shot.

| Thing | Estimate |
|---|---|
| One base | 48 wide, 48 deep |
| Gap between bases | 4 |
| Arena | 288 wide, 160 deep (32 behind the bases, 80 in front) |
| Throw platform | 88 wide, 16 deep, and the corridor is the same width. **[Owner]** wider than the 72 measured: the corridor felt too narrow (2026-11-04) |
| Walls | Rim 32 above the arena floor; corridor floor 12 below it, so corridor walls are 44 tall |
| Checker squares | 8 studs |

These are the numbers in `assets/models/build_world_layout.py`, whose renders were compared with the reference shots.

---

## 4. Bases

- **[Owner]** One base per player, 5 in a server.
- **[Owner]** Bases are **small compared to late-game animals**. There's no attempt to give animals enough room.
- **[Owner]** A base starts at **10 animals** and upgrades to a **maximum of 20**, **+2 per upgrade** (5 upgrades:
  10 → 12 → 14 → 16 → 18 → 20).
- **[Owner]** Dinos can go **anywhere** on the base. No grid of slots. **[Built]**
- **[Owner]** After a catch, the player is teleported back to their base, next to its exit. **[Built]**
- **[Owner]** No spawn pad in the arena (2026-11-04). **[Built]** Players still appear at `Config/Map` `spawn`, but its pad is
  hidden; the throw's animation rig, which stood on it, is kept in ServerStorage for republishing the clip.
- **[Seen]** Fenced all round with a gap (the gate) in the middle of the front edge. Wooden fence: posts and two rails,
  all with studs.
- **[Seen]** Some bases have blue fences instead of wood (see section 15).
- **[Seen]** Dinos overlap each other freely and stick out far past the fence, with a small name and $/s label over each.
- **[Owner]** No name over the monsters at all (2026-11-04): a base's labels piled into an unreadable heap.
- **[Owner, 2026-11-04, later] Tags over the monsters after all**, styled like Steal an Egg's but our own (Figma "Throw
  Eggs - Monster Tags & Walk Vision", approved). **[Built]** (`MonsterTagController`, numbers in `Config/Plot` `tags`):
  - Three lines of chunky outlined text: the mutations ("GOLD  MEGA CHONK": the colour word in its colour, the size
    word in silver; no line at all without a mutation), the name in white, the $/s in green.
  - **No heap:** only the 3 monsters nearest to you show a tag, within 120 studs, and where two would overlap on
    screen the further one's is lifted above the nearer one's.
  - Over the head, but never more than 18 studs above the monster's feet, so a giant's tag can be read from its base.
    Every tag is the same size on screen whatever the monster's size, shrinking a little with distance.

---

## 5. What stands at each base

**[Owner]** The egg shop and the squat rack are **always next to your base**.
**[Owner]** Other players **can't see your shop**, only your **squat rack**, which is there to show off.

| Thing | Where | Who sees it |
|---|---|---|
| **Egg shop stall** | Outside the fence, left of the gate **[Seen]** | **Only the owner of the base [Owner]** |
| **Squat rack** (the reference uses a pull-up bar) | Outside the fence, right of the gate **[Seen]** | **Everyone [Owner]** |
| **XP upgrade pad** | In front of the rack **[Seen]** | Everyone **[Seen]** |
| **Upgrade sign** | On the front fence at the gate **[Seen]** | Everyone **[Seen]** |
| **Owner plate** | Floating high above the base | Everyone **[Owner]** |

### Egg shop stall
**[Seen]** Brown studded wooden stall with posts and a counter, a blue and white striped awning, and a round cyan pad on
the ground in front of it. Standing on the pad opens the Egg Shop.

### Squat rack
**[Owner]** Ours is a squat rack where the reference has a pull-up bar.
**[Seen]** Two thick pillars with coloured rings and a bar across them. A dashed circle on the ground marks the training
spot. A round orange button with a grey edge sits in front of it, with floating text above: the price in big red
outlined numbers and "+X XP / rep" under it.
**[Owner, 2026-11-05]** The rack gets better on its own as its owner buys rack upgrades, and everyone sees it, so it's
there to show off: no menu, nothing to choose. Six racks (`Config/Training` `rackModels`, a new one about every 2 to 3 maps):

| Rack | Upgrades | Look |
|---|---|---|
| Gym | 0 | Yellow pillars with coloured rings. Every base with no owner has this one |
| Iron | 3 | Braced steel with bolts, blue bands, chains and kettlebells |
| Bone | 7 | Thigh-bone pillars, ribs, a spine for a crossbar, a horned skull with green eyes |
| Crystal | 10 | Amethyst columns grown from rock, a glowing gem floating overhead |
| Magma | 13 | Basalt split by lava, standing in lava pools, braziers, black horns |
| Titan | 16 | Gold columns on marble, banners, a crowned monster's head with golden wings |

The upgrade that earns one says "New rack: Iron Rack!". Models: `assets/models/build_racks.py` (Gym is in
`build_base_kit.py`); they must keep the bar and pad where the Gym rack has them, as its notes explain.

### Upgrade sign
**[Seen]** A small sign with a paw icon, showing the size, and a darker price bar under it. At the top level it reads "20" and "MAX".

### Owner plate
**[Owner]** Each base shows the player's **profile picture** and **how much money they make per second**.
**[Seen]** A round picture, the username in white outlined text, and $/s in green under it, floating high above the base.
An empty base's owner shows "$0/s".

---

## 6. Things shared by everyone

- **SELL stall [Seen]:** one red and white striped stall in the open ground, with a dashed red circle on the ground.
  **[Built]** Front left of the arena seen from the platform, its counter and pad facing the bases (`Config/Hub`).
  **[Built], [Owner, 2026-11-05] Sell Stand panel** (Figma "Throw Eggs - Index & Inventory", `SellPanel`): the pad opens a
  red panel in the middle of the screen with the backpack as a grid, cheapest rarity first. Rarity buttons (ALL, COMMON
  to MYTHIC) pick or unpick all of a rarity; tapping a tile picks one. The footer shows how many and the total, and
  SELL needs a second tap (SURE? TAP AGAIN, 3 seconds). Nothing is picked on opening, monsters on the base aren't
  shown, and the carried one shows HOLDING and can't be picked. The server re-checks all of this (`sellMany`).
- **Leaderboards:** MOST POWER (Throw Power; replaced MOST DINOS [Owner, 2026-11-08]), TOP MONEY and LUCKIEST CATCH, top 10 across all servers, refreshed every minute,
  standing side by side **[Built]**. In the arena they stand on the ground in front of the wall, on the right as you
  face the bases from the platform **[Seen]**. The exact spot is an estimate. **[Built]** A shallow arc in front of the front
  wall on that side (`Config/Leaderboards`). Each is a Blender board (`build_leaderboards.py`): a screen in a wooden frame
  on a stone plinth, a header plaque with marquee bulbs, and a gold medallion on top with its icon (a paw, cash, a
  clover). The list uses the HUD's Fredoka One with thick outlines, always shows all ten ranks, gold, silver and bronze
  for the top three.
- **Lucky catch announcements [Owner]:** when someone catches something lucky, everyone in the server sees it. See below.

### Lucky catch announcements
**[Owner]** There's an announcement when someone hits something lucky, shown in `training-announcement-leaderboards.webp`.

**[Seen]** A big banner at the top centre of the screen, over whatever the player is doing, even training:
- A big green four-leaf clover overlapping its left side.
- A rounded panel with a thick dark outline, its colour matching the luck tier (pink for LEGENDARY).
- Three centred lines in heavy outlined text: `WOLDEMORD2003 CAUGHT`, then `BIG RUBY THUNDERBIRD`, then `1 in 445K`.
- A tilted sticker over the top right corner with the tier's label: `LEGENDARY LUCK!!`.

The name line includes size and mutation. Our lower limit for showing one is still to be tuned **[Guess]**: start at
1 in 10K within the server. This replaces the "rarer than 1 in 1M" idea in section 13.

**[Built]** From mock-ups 12 and 12b: INSANE (cyan), LEGENDARY (pink) and GODLY (turning rainbow) panels, the clover
landing with a half turn, 6 seconds on screen, one at a time with the rarest first. It never shows during your own
reveal; your own catch appears once you've tapped through it. Limit and timings are in `Config/Reveal` (`luckyBanner`).

---

## 7. How you play

### Train
- **[Built]** Step onto the rack's spot: the character locks in under the bar and squats automatically until STOP.
- **[Built]** Each rep gives XP. Level-ups raise Throw Power with a big "LEVEL UP! Throw Power +20".
- **[Built]** The orange pad buys more XP per rep with cash.
- **[Owner, 2026-11-06]** An x2 bubble pops up every 3 seconds while training, tapped or not (`Config/Training` `bubble`),
  and stays 2 seconds. Tapping it gives a double rep and the 2X XP moment (`BoostMoment`), when the server confirms it: the
  bubble bursts, "2X XP!" slams in over a purple sunburst with the XP gained, and orbs fly into the level bar, which flashes.
  About a second, so it's over before the next bubble. Everyone nearby sees the lifter flash purple, with sparks and a ring on the ground.
- **[Built]** The level bar and STOP only show while training.

### Throw
- **[Built]** Step on the throw pad and a vertical meter appears. A marker swings up and down a tube with 10 levels and
  slows near the top. Level 10 is PERFECT and gives the biggest throw. **[Owner, 2026-11-05]** PERFECT is a little harder
  (the top 6% of the tube, `Throw.meter.perfectZone`, about 1 tap in 6.5) and gets its own moment (`PerfectMoment`, Figma
  "Perfect / Moment"): gold edge flash, sunburst, a big slammed PERFECT! and FULL POWER. No extra reward.
- **[Built]** Distance = Throw Power × the level's share: 0.4 at level 1 up to 0.9 just below the top.
  **[Owner, 2026-11-08]** PERFECT throws exactly your Throw Power, with no 1.5x bonus (`Throw.meter.perfectMultiplier` 1).
- **[Owner, 2026-11-08, from player feedback] [Built] Power Limit:** strong players can set the farthest their eggs fly,
  so they can still reach earlier maps whose monsters they haven't all caught. A throw goes as far as it would anyway but
  never past the limit, so with a limit well under your power nearly every tap lands right on it. A **LIMIT** button sits
  right of the Throw Power number (shown once your power can pass the first map; LIMIT OFF dark, LIMIT 1,450 orange when
  on, still shown while aiming). It opens the Power Limit panel: an ON/OFF switch, the limit as a big number with a
  slider (up to your power), and a map card between < and > buttons that jump the limit to the far end of the map before
  or after, showing "EGGS LAND IN" the map and how many of its monsters you've caught. Moving the slider or the arrows
  turns it on. Saved with your settings; the server applies it to every throw (`Config/PowerLimit`,
  `PowerLimitController`, `ThrowService`), and the luck offer's chances count it. No "SO CLOSE" hint when the limit
  stopped the egg. Screenshots in `design/power-limit/` (Figma not connected when built).
- **[Built]** All HUD except Throw Power hides while aiming and flying.
- **[Seen]** The owner's recording of the throw (`~/Documents/Screen Recording 2026-11-03 at 20.02.26.mov`,
  watched frame by frame for the first 10 seconds). Times in seconds:

  | Time | What happens |
  |---|---|
  | 1.3 to 1.5 | The player walks onto the platform; the whole screen dips to black. |
  | 1.6 to 2.1 | Back from black on a new scene: the player stands still on the throw spot facing down the corridor, the camera low behind their right shoulder. All HUD is gone except Throw Power. |
  | 2.1 | The meter rises in beside the player, "TAP TO THROW!" under it. |
  | 3.0 | Tap: the result (+13, "+13 POWER", GOOD) holds on the meter for about half a second. |
  | 3.1 | Thin black bars slide in at the top and bottom. |
  | 3.45 to 3.7 | The thrower crouches and swings the item low on the right; the camera starts to swing round. |
  | 3.7 to 3.85 | The camera whips round to face the thrower, showing the arena and bases behind them. |
  | 3.85 to 4.2 | They spin upright with the item raised, then drop into a deep lunge, arm swinging through. |
  | 4.3 | Release with a straight arm from the lunge; the camera is behind the thrower again, low, looking down the corridor. The bars slide away. |
  | 4.4 | A thick white streak trails behind the item; the luck panel appears with the world's name. |

- **[Built]** All of that: the dip to black onto the throw spot (`Config/Throw` `aim`), the held egg, the result on
  the meter, the bars, and the camera's keyed path round the thrower (`windup.camera`). The clip is made in Blender on
  the MrXen0 R15 rig and converted straight to a KeyframeSequence (`assets/animations/build_throw.py`, previews in
  `design/animations/throw/`), synced by Rojo to `ReplicatedStorage.Shared.Animations.ThrowWindup`. Studio play tests
  play that clip, so they always show the latest build; live games play the published
  rbxassetid://136948284707759, which has to be republished over the same asset after each change. The egg is
  0.45× its size in the hand and grows back as it flies. The camera work is in `ThrowCinematic`.

### Flight
- **[Built]** The camera follows the egg down the corridor through the worlds. The luck multiplier climbs live at the
  top of the screen, with the current world's name.
- **[Owner]** Flight time depends on how far the throw goes. Throws to the first maps must be over faster than a throw to
  the last map, and always smooth. **[Owner, 2026-11-07]** A little longer than the first 6 seconds, so players get to see
  the worlds: `Config/Throw` `flight`, 2 seconds at the shortest, 8 to the end of the last map (about 3 s to the Forest's end). Past the Last Door the egg slows and takes 3 more seconds (`deepTime`), so players get to see The Deep End.
- **[Seen]** The bars and Throw Power go away as it starts. The camera begins low, climbs high behind the item
  looking down the valley, then drops low again as it comes down.
- **[Seen]** A thin white line trails along the floor behind the item, and white lines cross the floor at intervals.
- **[Built, 2026-11-11] The flight made worth watching** (**[Owner]**: "something clean, actually nice";
  `Config/FlightFx`, `ThrowCinematic`). The streak is a tapering comet with a soft glow, its tail tinted the colour of
  the world below (PERFECT stays gold). Entering a new world, a ring in the world's colour bursts round the egg and
  rides with it, leaving a short wake of sparks. The camera follows 65% of the egg's rise and fall, so the arc shows.
  **[Owner, 2026-11-11]** No flight sounds wanted: a chime-per-world version was built and removed.
- **[Built, 2026-11-12] Throwing alone** (**[Owner]**; `ThrowAreaPrivacy`): while you stand on the throw platform,
  other players on it are hidden on your screen (bodies and names), and their throws aren't shown to you. Players
  outside the throwing area still see everyone, throwers included. Only your screen changes.
- **[Seen]** The luck number sits in a see-through rounded panel whose tint changes per world. Under it, a dark
  strip holds the world's name in that world's colour, with a small icon.
- **[Seen]** Luck climbs fast and then slows right down. Half-second readings from one throw at 6883 power:
  13.54, 22.13, 28.84, 34.41, 38.51, 41.13, 43.20, 44.74, 46.34, 47.99, 49.37, 50.14 (final).
- **[Built]** The flight camera climbs from the thrower to high behind the egg (looking down the valley, the egg low
  in the middle of the screen) and drops low behind it at the end (`Config/Throw` `flight.camera`). The egg slows as
  it goes, and flights run from 1.5 s for short throws to 6 s at the far end of the last world. A white trail
  follows it. The luck panel at the top shows the luck number in a see-through panel tinted for the world, with the
  world's name in a dark strip under it, and pops each time the egg crosses into a new world. The floating distance
  numbers and world names that stood in the corridor are gone, as in the reference.
- **[Built]** Landing: a white ring flashes out on the ground and a puff of dust rises (`Config/Throw` `landing`).
  The walking view after it, then the close-up and pull back, are built (below).
- **[Owner, 2026-11-06] When the egg lands it's cut in half, and the white and the yolk show.** **[Built]**
  (`EggModel.split`, numbers in `Config/Throw` `landing.split`, the same as `SPLIT` in `assets/models/build_eggs.py`,
  preview `design/eggs/egg_slice.mp4`): the egg stands upright where it landed, a white streak sweeps across its middle
  (its widest point), the top half slides off along the cut, tips over and lands upside down beside the bottom half, and
  rocks to a stop, so both halves show a disc of white with a domed yolk. About 1.3 seconds, played on every screen.
  The bottom half stays where the egg landed, so the reveal is unchanged. Only eggs with their Blender model in the
  place are cut; until they're imported the egg stays a ball.

### Landing and arrival: the animal walks to the egg
**[Owner]** Pay special attention to this part. The animal walking towards what you threw is the key moment, then its
name shows up slowly.

**[Owner, 2026-11-07] The reveal is the soul of the game, and this is how it works.** It's why people buy x100 and x500. It
must never feel like wasted time, and a huge catch may take as long as it wants, up to about 40 seconds. Where anything
further down this section disagrees, this wins. **[Built]** (`RevealWalk`, `RevealCloseUp`, `RevealOpening`, `RevealDrama`,
`RevealSound`, `Config/Reveal`; text designed in Figma "Throw Eggs - Reveal Text",
https://www.figma.com/design/GkAQPam3aVAIkfHi8uUWfI):

1. **The walk is slow and goes all the way.** 4 seconds for a common catch up to 13 for the rarest, plus up to 8 for the
   biggest, braking all the way to the egg. Over the last of it the monster lowers its head to the egg, so even a Unit of Doom
   ends with its face at it instead of stopping hundreds of studs short. Each footfall has a sound, heavier the bigger it is.
2. **The "1 in X" shows on the walk**, big, from catches of 1 in 100 up (`counterMinOneIn`, was 1,000: the owner's own example is
   a 1 in 900). Its being there is how you know you got something. **[Owner, 2026-11-07, replacing the lock on "1 in 1"]** It
   starts on a random number that depends on how rare the catch is: 11 to 24 for a catch that's not that rare, rising to 58 to
   89 for the rarest, never ending in 0 or 5 (`tease`). It stays locked there for 2 to 3 seconds, then creeps up just a little,
   never past 97, so no luck label lands before the camera switches.
3. **The camera switches to the feet. This is the most important part.** One continuous, very slow zoom out runs while the
   numbers go up for real, starting on one front foot from ground level, with the ground under the feet held in the same place
   on the screen. More and more of the body comes into view, but never all of it: by the last number it has stopped short of
   the eyes (`closeUp`). The numbers start slowly and run away at the end, growing and trembling, and each luck label slams in
   above them. Rare catches get strings rising to a peak on the last number. **[Owner, 2026-11-07] More shaking and instant
   zooms for rarer monsters** (`impact`, `lucky` `jolt`, `shake`): the switch to the feet lands like a stomp; each luck label
   snaps the view in and jolts the camera, harder the rarer the label; the camera trembles from the first label on, more and
   more as the numbers run away; on rare and big catches smaller snaps land on a beat that speeds up. Common catches get none
   of this.
4. **Only when the numbers finish is the whole monster revealed.** On rare catches the last number snaps the view in and it all
   goes still and quiet for a moment. Then a flash, a boom and a roar: the view snaps wide at once, showing the whole monster,
   and the camera whips back with its biggest shake, its head roaring, as the final text lands. The camera ends low, looking
   up. It holds still there, with no circling.
5. **Monsters stand still while the numbers climb [Owner, 2026-11-11: "make the monster not move for a better shot"]**,
   like a statue, so the close angles stay clean. **At the unveil they come alive:** they roar and keep playing their own
   idle on the final screen [Owner, 2026-11-11, about the final screen: "I don't want him to stand still here"]
   (`DinoLifeController.reveal`, `showcase` `stillClimb`, `freezeAfter` false). They roar rather than start an attack as
   they're unveiled.
6. **Rare and big catches set a mood from the first step of the walk:** the eyelids stay narrower, the world dims, a drone and
   a heartbeat build. The monster's colours sink a little until the unveil, but stay readable: a gold foot is a hint. Common
   catches get the same shape with no numbers, about 7 seconds in all.
7. **No flashy effects round the monster [Owner, 2026-11-07].** The glowing outline, star sparkles, rising lights, shockwave rings,
   lightning and rainbow are gone (`RevealAura` deleted). The only thing round the monster now is plain ground dust when something
   big lands (`RevealDust`, `dust`), and the screen's coloured edges are half as strong. The light rays behind it at the final
   moment stay.
8. **Big monsters get room [Owner: the corridor's walls covered them].** A monster too wide for the corridor opens it: on the
   catcher's screen only, behind the first cut to black, the walls and everything on their rims slide apart, the floor widens
   with them and the props spanning the corridor hide, so the real map stays as it is for everyone else. The walls open to 1.5
   times the monster's width (`opening`). A real wider map wasn't enough: a Unit of Doom on the last map is over 400 studs wide,
   past the island's edge, against an 88-stud corridor.

9. **The showcase [Owner, 2026-11-11]. [Built]** (`RevealShowcase`, `RevealBackdrop`, `Config/Reveal` `showcase`; art drawn
   in Figma "Throw Eggs - Reveal Showcase", https://www.figma.com/design/i7JF39IAKl4MzhPM4gdFyh, exported to
   `assets/reveal/` and uploaded). The owner first asked for a nicer reveal with several camera angles, a monster that
   doesn't move, better effects and visuals. A first version played the angles after the unveil with a fact text on each;
   **the owner corrected it the same day: "the cinematic angles should happen while the numbers are going up and the luck
   still goes up, not after he gets revealed", and no texts presenting the name, size, rarity and money: "just a better
   visual for the final reveal".** So:
   - **Who gets it** (`showcase.levels`): catches from 1 in 100, or Absolute Unit and bigger, or a monster caught for the
     first time, or a Robux monster. Commoner catches are as before.
   - **While the numbers climb, the camera cuts between close angles.** Each luck label that lands (LUCKY! up to
     IMPOSSIBLE!) cuts to a new close angle on a part of the monster, with the label's own slam, flash and jolt plus speed
     lines over the screen: its flank, its back legs from behind, its front feet from the other side, its back from above
     (`details`). Each is a slow creep of about 2.5 seconds, then the camera goes back to the slow zoom out from the feet
     (step 3), which carries on underneath. A rarer catch passes more labels, so it gets more angles (they go round again
     after four). A big or new catch with no labels gets 1 to 3 cuts on the clock. **The face never shows:** an angle that
     would show the monster's eyes, or put the camera inside it, is left out for that monster. The last 1.4 seconds always
     belong to the feet, so the unveil still whips back from there.
   - **Transitions between angles [Owner, 2026-11-11: "add transitions between the camera angles"]:** the camera never
     jumps. It glides to the next angle in half a second, and back to the feet in 0.65, slow at either end with a light
     blur in the middle. When the straight way there would pass through the monster, it whip-pans instead: it swings 40°
     away the way it's heading, blurring hard, and swings in on the new angle from the other side, in 0.38 seconds
     (`showcase` `transition`).
   - **The monster stands still** all through the climb, then roars at the unveil and moves freely on the final screen.
   - **No cinema bars [Owner, 2026-11-11: "I want those lines from above to be removed"]** (built, off: `cinemaBars`).
   - **[Owner, 2026-11-11, after seeing it: the backdrop "to be removed as well"] The backdrop is off**
     (`showcase.backdrop.enabled = false`): the monster ends in its real world with the old light rays behind it, as
     before. What follows describes it when switched on. **The final reveal's visual: a backdrop that makes the monster
     stand out on any world.** At the unveil everything
     behind the monster is swapped for drawn art in its rarity's colours (turning rays, a soft light, dots): a screen-sized
     picture standing in the world just behind it, so the monster, its egg and the ground in front stay real. **A dark
     monster gets a bright backdrop and a white light from the camera; a bright one gets a dark backdrop.** From 1 in
     1,000,000, Mega Chonk, or a Robux monster the backdrop is outer space with stars and an eclipse (a dark monster stands
     in front of a blazing star instead, since a dark moon would swallow it). From 1 in 10,000 or Chonker, pieces of the
     ground burst up round its feet and hang in the air. The dust slows to a quarter speed. The world's haze thins while the
     backdrop is up. These catches don't get the old light rays. `showcase.backdrop.enabled = false` brings the real world
     back.
   - **No new texts.** The final text is the usual one and lands at the unveil, as before. Taps work as before.
   - **Lighter mood:** the rare-catch darkness is weaker (`drama` `dim` 0.88/0.8/0.72, `shadow` 0.2, `hushDim` 0.45; they were
     0.8/0.68/0.56, 0.45 and 0.3), so the feet can be seen.
   - It adds no time to the reveal. Not yet seen on a phone.

10. **The final screen, in 3D [Owner, 2026-11-11, after two earlier versions: "can you do the texts feel like they're in 3D
   space? and make the rarity and the number the most important thing. I also want a new design on the texts. Mutations feel
   like they're not special at all. The money/s should be placed under the monster"; before that: "keep '1 in' simple and
   only change the other number's appearance, I don't want the numbers to zoom in and out"]. [Built]** (`RevealFinalCard`,
   `RevealOdds`, `Config/Reveal` `finalCard`, `oddsFx`.) It replaces the centred stack described further down.
   - **Fourth look [Owner, 2026-11-11: "it's hard to distinguish what's the name of the monster... it looks like I got the
     'secret amethyst monster' instead of 'death knell'. The name of the monster should be above him. I want the rarity tags
     to be the same design the game uses. I love that AMETHYST design. The 3D space is oriented too much on the sides. The
     text for what type of luck I got should be more crazy."] [Built, checked on a flat copy in Studio; not yet seen by the
     owner on a real catch]** The layout below replaces the left and right panels.
   - **Polish [Owner, 2026-11-11, after seeing it on a catch: "make it more clean/polished so everything looks nice"] [Built]:**
     a soft dark band sits behind the title and another along the bottom behind the luck, so the text reads over any
     monster; the shout and the number are centred together; fewer, smaller glints on the mutation.
   - **Camera angles only on a luck label [Owner, 2026-11-11: "only make them switch when the type of luck and that sound
     effect of slamming happens"] [Built, not yet tried on a real throw]:** during the climb the camera changes angle only
     at the moment a luck label slams in with its sound. It holds that angle until the next label or the unveil; it no
     longer goes back to the feet on its own, and a catch with no luck labels gets no angle changes
     (`showcase.labelCutsOnly`).
   - **In 3D space:** the text stands on panels in the world a few studs in front of the camera, drawn over everything and
     seen in real perspective: the title leans over the monster, the luck lies before its feet, facing the camera. They follow the camera, sway a little, and the title and the luck shout fly in
     from near the lens and land with a bounce.
   - **Solid letters:** every big word is a block: copies of it step down and back behind the face in a dark shade of its
     colour, and the face is lit top to bottom; a white shine crosses the big words every few seconds.
   - **Title, over the monster's head:** the monster's **NAME** is the headline, the biggest text there, standing just
     above its head (it follows the head; a long name shrinks to fit). Under the name, one row says what it is: its
     **rarity, drawn as the game's own rarity label** (same colours, glow and movement as on tags and in the Index), its
     **MUTATION** in its own material with "MUTATION" small beside it (Gold gleams with glints; Ruby, Emerald, Diamond and
     Amethyst are cut gems with facets, a gleam and glints; Shadow broods with a dark pulsing aura; Ghost flickers;
     Bubblegum wobbles), then its size and NEW! as stickers. A message (a finished map, NEW BEST!) sits small over the name.
   - **Luck, along the bottom (lucky catches) [Owner, 2026-11-11, after an IMPOSSIBLE catch: the letters' movement
     "looks kind of weird", he wants it "visually better", not more movement or more effects; and the shout, "1 in" and
     the number looked like separate pieces] [Built, checked on a flat copy in Studio; not yet seen by the owner on a real
     catch]:** one centred block. On top **the luck shout** in one line of solid letters ("GODLY LUCK!!!"), standing still,
     in its luck's colours, a white shine crossing it every few seconds and a soft burst of rays turning slowly behind;
     IMPOSSIBLE's face is a rainbow drifting slowly along the whole word. Under it, as one line, **"1 in"** plainly and
     **the number**, huge and solid. The digits drop in and land; from SUPER LUCKY! they roll like a slot machine and lock
     left to right with a tick, and a thin glow breathes round them; from INSANE! the colour drifts; from GODLY! the
     rainbow runs through them. Once landed nothing wobbles, shakes or hops; only the two rarest labels get two sparkles.
   - **Money under the monster:** what it earns, in solid green, on a panel just under the monster's feet (kept clear of the
     luck under it), rising into place.
   - "tap to continue" small, flat, bottom centre. The camera frames the monster between the title and the luck. If the card ever fails,
     the old centred text shows instead.
   - Studio's screen capture doesn't draw panels like these; they were checked by laying a flat copy over the screen.

**[Owner, 2026-11-07, tested on a phone]** The eyes closing, the cuts to black and every other full-screen cover reach the screen's
real edges, past a phone's notch and round corners. They live on their own layers (`RevealBehind`, `RevealInFront`), and the text
stays on `RevealHud` inside the safe area, so it's never cut off.

Checked on all 124 monsters at normal size and at Unit of Doom: the camera never passes through a body, the whole monster
is in the last frame, and the eyes stay hidden until the last number but for two giants (Clockodile, Spiral Gary), whose
heads sit too low to hide.

**[Seen]** From the owner's video. Times are seconds after the item touches the ground; the whole thing takes about 7 seconds.

| Time | What happens |
|---|---|
| 0 | The item lands. A flat white ring flashes on the ground under it. Luck stays on screen, frozen. |
| 0.6 | A puff of dust rises behind it. |
| 0.9 | The luck panel and world name fade out. |
| 1.1 | Quick cut to black. |
| 1.35 to 3.9 | **The walk: the camera becomes the animal's eyes.** Low to the ground, far from the item, moving slowly towards it and swaying side to side with its horizon tilting, like footsteps. A thick amber glow with faint rings darkens the screen's edges, leaving the centre clear. **No animal is visible yet and there's no text.** |
| 4.1 | Quick cut to black. |
| 4.2 | Fades in on a close-up of the item on the ground, with the animal's feet already standing behind it. |
| 4.4 | Blank name appears, bottom centre: `______ _____`. Holds for a moment. |
| 5.0 to 6.4 | **The camera pulls back and up** past the animal's legs, and it's revealed standing over the item. Then the camera keeps circling very slowly (ours doesn't: the owner wants it to hold still, see below). |
| 5.2 to 7.0 | Letters fill in **out of order**, about one every 0.2 seconds: `E`, `RE`, `IRE`, `S_IRE`, then `S`, `SI`… in big white outlined text. |
| 7.2 | **The final moment:** the screen washes in the rarity's colour (purple here) with a big ring around the animal, fading in about a second, with sparkles on the model. |

- **[Seen]** The animal never appears to walk on screen. It's the camera doing the walking, then the animal is simply
  there. So this needs no walking animations on our block dinos. It's one more reason it works so well.
- **[Seen]** The item stays lying on the ground between the animal's feet throughout.
- **[Owner, 2026-11-04]** No circling: once the pull back ends, the camera holds still. And it must not zoom out too
  far: the monster fills a good part of the screen, framed from its own size (said about the old hatch's camera,
  which ended 30 studs × the monster's size away and spun round it).
- **[Seen]** Final text sits directly on the screen at the bottom with **no panel behind it**, stacked as: mutation
  ("GOLD") small and gold, the name big in its rarity colour, a tilted orange "NEW!" sticker beside it, $/s in green,
  then a small "tap to continue".
- **[Seen]** After the tap, the text vanishes straight away, the screen fades to white, stays white for about half a
  second, then fades into the player's base with the HUD back.
- **[Seen]** This catch had no "1 in X" counter; earlier recordings show one on other catches (see the GDD's Reveal notes).
- **[Built]** The roll is decided on landing. The counter is suspense only.
- **[Built]** Labels escalate: LUCKY! → SUPER LUCKY! → INSANE! → LEGENDARY! → GODLY!
- **[Built]** Very rare catches get a light beam and a "YOU CAUGHT!" banner on the base (1 in 1K to 10K; rarer ones
  get the lucky catch banner instead). Tapping skips ahead. [Owner, 2026-11-11] The "YOU CAUGHT" banner looks like a
  smaller lucky catch banner (shared code, `CatchBannerLook`), with the monster where the clover is, not a dark box.
- **[Built]** The text follows mock-ups 15 to 16b: white dashes that fill with letters at the bottom centre, then the
  final moment and the final text with no panel (tier sticker on lucky catches, size and mutation, name in its rarity
  colour, NEW! on a first catch, $/s, the "1 in X" on lucky catches, tap to continue), then white for half a second.
- **[Owner, 2026-11-04] No rings, and luck only when it's really lucky.** The old rings round the monster looked cheap
  and made the animal feel unimportant. The "1 in X" showed on nearly every catch (a common monster with a common size
  is already "1 in 160"), so it meant nothing. And the clover icon and box round the odds looked ugly. **[Built]** now:
  - **Luck only from 1 in 1,000 (1 in 100 since 2026-11-07, see the top of this section):** rarer catches get the counter, the luck labels, the tier sticker, the "1 in X" and
    the tier sticker. Commoner ones show none of that (`Config/Reveal` `counterMinOneIn`).
  - **The final moment:** a quick white flash, then light rays in the rarity's colour burst out from behind the monster
    and turn slowly, two layers turning opposite ways (`RevealRays`, `Config/Reveal` `rays`). Rarer luck labels get
    more rays, brighter and faster, a bigger sparkle burst, and from SUPER LUCKY! up a camera shake that grows to
    GODLY! (`shake`). The name pops in. The rarity colour and the luck glow light only the top and bottom edges,
    softly, so the monster keeps its own colours. The old light pillar is gone: it covered the monster. Sparkles stay
    round the monster, so on a giant they don't fly past the camera.
  - **The "1 in X":** plain big outlined text lit in the luck tier's colour, with no icon and no box, at the top
    during the climb and under $/s at the end.
  - **The tier sticker** sits just above the name instead of at the top of the screen, so it never covers the head.
  - **Framing:** the camera ends low, looking up a little, and frames the monster and the egg in the part of the
    screen the text leaves free, so nothing overlaps. A big monster may stand with its feet behind the sticker and the
    top of its name, so it fills more of the screen (its egg is a speck). The camera never goes below the ground.
  - **Nothing in the way [Owner, 2026-11-04: a Planet-Sized Bog Rex showed only blue]:** a giant's camera ends up to
    thousands of studs back. So during the reveal the light stays the egg's world's, even when the camera is over the
    next world (it had switched to the Abyss's thick blue water). The world's haze thins the further back the camera
    ends (`closeUp` `clearDistance`, `minHaze`). The bases' statues hide, and so do the map's decorations standing
    between the camera and the monster, on the catcher's screen only, until the white flash.
  - Dark mutation names (SHADOW) are lifted towards white so they read on the dark outline.
  - Tested on every map's rarest monster with big sizes, and common catches (screenshots in `design/reveal/final/`).
- **[Owner, 2026-11-04] Lucky catches take their time.** While the numbers climb the reveal must slowly show the
  monster, and the luck labels must be more fascinating. Common catches stay quick. **[Built]** (`Config/Reveal`
  `lucky`, `closeUp` `slowHold`, `slowAcross`, `slowRise`):
  - **Length:** the counter climbs for 4.5 seconds at 1 in 1,000 up to 9 at 1 in 100 billion, plus a 0.8 second
    pause on each luck label it reaches. So 1 in 1,000 takes about 6 seconds and the rarest about 14 (measured:
    1 in 1,200 took 6.2 s, a 1 in 60 billion Bog Rex 13.7 s). Commoner catches are as before (1.5 s for a Compy).
  - **Camera, feet to head:** the close-up on the egg holds 0.8 seconds, then the camera turns from the egg to the
    monster's front feet and slowly pulls back and up its body over the whole climb, so the head comes into view
    last and the final framing lands with the last number. No circling.
  - **Labels slam in:** each new label (LUCKY! up to IMPOSSIBLE!) lands huge in the middle of the screen, see-through
    to solid with a bounce, then a flash in its colour, a camera jolt that grows with the label, and a burst of
    sparkles. The counter pauses on the label's own number ("1 in 10,000" under INSANE!) and the letters wait. At
    the end of the pause the label flies up to its place at the top and the climb goes on. A tap still skips ahead.
- **[Owner, 2026-11-06] A better reveal: the monster in view, bigger lucky effects, numbers that never stop.** The owner
  watched the reveal in Studio: the monster was barely visible (the lucky reveal crept up from its feet, the head
  last; a giant seen from out over a wall was hidden behind the wall's top), the slowed camera moved badly, and the
  "1 in X" stopped on every label. **[Built]** (`RevealAura`, `RevealCloseUp`, `Config/Reveal` `aura`, `closeUp`
  `luckyHold`/`push`; previews in `design/reveal/v2/`):
  - **Always in view (replaced 2026-11-07: the owner now wants the body hidden until the last number, see the top of this section):** after the walk (now 2 to 3.2 seconds, was up to 4.6) a short close-up on the egg, then the
    camera pulls back to the whole monster in about 1.5 to 2.5 seconds on every catch. On lucky ones it pulls back a
    little further, then creeps straight in on the monster over the count, landing with the last number. No
    circling. It stays inside the corridor at any height, so the walls can't hide a giant, and looks down a little
    on the biggest (`bigEndElevation`). The egg lies closer to the monster (`aheadShare` 0.3), so the monster is
    framed bigger.
  - **Nonstop count:** the "1 in X" never pauses. Each luck label slams onto the screen between the monster and the
    counter as it's passed, then settles over the counter, while the numbers keep climbing. The label and counter sit
    at the bottom, just above the name's letters, so the monster has the top of the screen; the final text takes the
    same space, so the monster doesn't move when it comes.
  - **Luck building up round the monster (removed 2026-11-07, see the top of this section)** (from the first label): a glowing outline in the label's colour that
    breathes and flashes as each label lands, lights rising off the ground round its feet, a light on it, a shockwave
    ring racing out along the ground at each label, the screen's edges darkening (vignette) so the monster stands out;
    from GODLY! lightning striking round it, and on IMPOSSIBLE! everything cycling through the rainbow. At the final
    moment one or two big shockwaves, a burst of lights and lightning, then a soft glow stays on.
  - **Softer screen colour:** the luck glows at the screen's top and bottom are smaller and weaker, the flashes
    gentler, so the screen never washes over the monster.
  - **The "1 in X" is the real chance of that exact catch** (monster, colour and size) on a plain throw at its map's
    start, from the rolls themselves (`DinoStats.describe`, `monsterOneIn` for the Index), instead of the configs'
    round chances multiplied together. So it never comes out round: a Gold Thicc Pteranodon is 1 in 483,422, a Shadow
    Planet-Sized Volcano King 1 in 51,177,829,002. The rarest colour and size have odd chances (Ghost 1 in 19,683,
    Unit of Doom 1 in 9,787) for the same reason. None of the 5,311 catches that show a "1 in X" ends in 000.
- **[Replaced 2026-11-07, the same day: the owner said it still wasn't it, see the top of this section]** A first try at the
  mood (`RevealDrama`): catches from 1 in 1,000, or Chonker and up, arrived as a **shadow**: a black shape with only its eyes and glowing parts lit, inside the
  aura's glowing edge, while the world dims and a drone and speeding heartbeat build. The name's letters hold back until late.
  Mega Chonk and up also shake the ground every 1.5 seconds. At the last number all goes black and quiet for 0.7 to 1.4 seconds (the
  hush), then a full flash, a boom, and the monster bursts into colour. Three levels (1 in 1,000, 1 in a million, 1 in 100 million, or the
  sizes Chonker, Mega Chonk, Planet-Sized) go darker, hush longer and boom louder. Giants end seen head on (`bigFill`, 1 since 2026-11-11: any closer and the head went behind the name over it). What the reveal hides for the camera never leaves a hole: sight lines stop at the ground (corridor floor, arena floor, throw platform), a wall section hides whole with what stands on it, and floor is laid under every hidden wall for the length of the reveal (`hideBlockers`).
  Common catches stay as before. These are the game's first sounds, from Roblox's licensed libraries.
- **[Owner]** The walk depends on the catch: a very rare monster starts far from the egg, and a very big one starts way
  above the map. It simulates the POV of each monster. Made in-game, not in Blender: it changes with every catch's
  rarity and size and with where the egg landed, so a camera script works it out on the spot.
- **[Owner]** The golden rings in the reference video are there because that animal had a **Gold** mutation.
- **[Built]** The walk (`RevealWalk`, numbers in `Config/Reveal` `walk`). After the landing: a quick cut to black, then
  the view opens already walking up the corridor towards the egg, from the thrower's side (or from the far side when
  the egg landed too close to the platform), a few random degrees off the middle. Then a quick cut to black and the
  close-up fades in. Tapping cuts the walk short. No monster and no text show. Previews in `design/reveal/walk/`.
  - **Eyes:** the camera sits at the monster's real eye height (the middle of its model's pupils) times its real size
    (its map's standard size × its size mutation). A first-map Compy sees from under 3 studs; a Unit of Doom Star
    Sovereign on Starfall Crater sees from about 400 studs up, with the whole map a strip far below.
  - **Start and end (the end replaced 2026-11-07: it goes right to the egg now):** set by how far below its eyes it sees the egg. The commonest catch starts with the egg 8° down
    (19 studs away for a Compy); the rarest (1 in 10 million and rarer) 1.8° down (about 85 studs for a Compy). Bigger
    monsters look down by up to 22° more, so a giant starts high up looking down at a tiny egg (about 900 studs away for
    that Star Sovereign). It stops with the egg 22° down (52° for the biggest), where the cut to black comes.
  - **Time (replaced 2026-11-07, see the top of this section):** 2.6 seconds for the commonest up to 4.6 for the rarest, plus up to 0.8 for the biggest. It slows a little
    as it nears the egg.
  - **Steps:** each footfall dips the view, swings it side to side, tilts the horizon (3° each way, 6° for the biggest)
    and turns the head a little. A step covers about one eye height, so big monsters take slow steps (down to about one
    every two seconds) and each lands with a jolt that grows with size. Swimmers from The Abyss glide instead, with a
    slow smooth sway and no footfalls.
  - **Eyes [Owner, 2026-11-04: the old rings looked weird and players didn't know what they were]:** the walk opens
    with a blink (eyelids lift from black and rest as thin curved lids at the top and bottom) and ends with the eyes
    shutting. A catch with a colour mutation also glows round the screen's edges in that colour, round on any screen,
    with sparkles twinkling in it. **No text** during the walk: the owner doesn't want the mutation named before the
    reveal. Built from shapes and a built-in Roblox image, so nothing had to be uploaded (`Config/Reveal` `walk.eyes`,
    `walk.glow`).
  - **Far eggs:** when the egg is a speck (under 10 pixels tall), a small glowing dot marks it so it can still be found.
- **[Replaced 2026-11-07 by the shot from the feet, see the top of this section]** The close-up and pull back after the walk (`RevealCloseUp`, numbers in `Config/Reveal` `closeUp`).
  Previews in `design/reveal/closeup/`.
  - **The monster is simply there:** behind the black after the walk, the caught monster stands still where its walk
    ended, at its real size (its map's standard size × its size mutation), facing the way it walked. It never pops out
    of the egg or spins. The egg lies upright on the ground and never moves (cut in half since 2026-11-06: its bottom
    half stands where it landed, the top half lies beside it).
  - **Where the egg lies [Owner, 2026-11-04: too close before]:** a clear gap ahead of the monster's front feet, half
    its length (`closeUp` `aheadShare`) and at most 15 egg heights, turned 60° away from the camera's side so the egg
    sits beside the monster on screen rather than in front of the lens. Worked out from the spot described next. With a giant, the egg lies far enough ahead of its feet
    for both feet to show in the close-up (a Unit of Doom's feet stand on the corridor's rims, either side of it).
    Where the monster's body is too low to stand over the egg, the egg lies just in front of its feet, worked out from
    the model's real shape. A monster under 2.5 egg heights tall (the first map's, like the Compy) would hide behind
    the egg, so the egg lies beside its front feet instead.
  - **Close-up:** fades in on the egg with the feet behind it, the camera low and close, a little to one side, looking
    down at it by 20° (only 4° for the biggest, so their legs tower up behind the egg over the corridor walls). The
    blank name, and on rare catches the counter, show at once. It holds for 30% of the name's time (0.4 to 2.5 s).
  - **Pull back:** the camera pulls back and up past the legs until the monster and the egg fill the screen, in 1.4
    seconds (2.4 for the biggest, whose camera ends hundreds of studs away), ending with the name. Down in the
    corridor the camera keeps between the walls. Then it holds still, with no circling. Tapping during the climb
    brings up the final text and finishes the pull back in half a second.
  - **Loading:** the monster's model loads during the walk, so it stands there from the close-up's first frame.
  - The letters, the counter, the colour wash, the final text and the tap timing are as before. The sparkles spread
    over the whole monster and the light beam rises above it, so both grow with its size.

### Earn
- **[Built]** Dinos on your base earn $/s. Spare ones go in the backpack.
- **[Built]** Hotbar of carried dinos on keys 1 to 0, best first. Holding one shows a see-through preview over your
  base (green = OK, red = not); clicking places it.
- **[Built]** Equip Best, Pick Up and Sell in the My Dinos panel.
- **[Owner, 2026-11-08] Every catch goes into the player's hands, not onto the base.** **[Built]** When the reveal ends
  the new monster is in the backpack, on the hotbar, and carried on the player's head, so they place it themselves
  (`Config/Plot` carryNewCatches). It's carried even with the base full (pick one up to make room). The carried
  monster is always on the hotbar: in the last slot if it isn't among the ten best. Starting a throw puts it back in
  the hotbar so it's not on the head through the reveal. Bought and gifted monsters still go straight to the base.
- **[Owner, 2026-11-07]** EQUIP BEST always says what happened: "Best monsters equipped! +$X/s", or "Your best monsters are already on
  your base", and then nothing moves.
- **[Owner, 2026-11-05] The carried monster sits on your head at its real size and plays its animation.** **[Built]**
  Equipping a monster (hotbar key, slot or EQUIP) or picking one up off the base (PICK UP, which also puts it in the
  backpack) sits it on top of the player's head at the size it has on a base: its map's standard size times its size
  mutation, in its mutation's colours, facing the way the player faces, welded on so everyone sees it. It stands on
  the top of the character, hats and big avatar heads included, never inside the player **[Owner, 2026-11-07]**
  (`Config/DinoLife` `carry`). Its tag floats over it like a base monster's, with its rarity word added: your own
  always, other players' within 60 studs (`MonsterTagController`). It
  walks while the player moves and idles (roar and all) while they stand (`DinoLifeController`). On the carrier's
  own screen it hides while aiming, throwing, in the reveal and while training. A big size mutation blocks some of
  the view ahead: that's the joke of the game, and `carry` is where to change it.
- **[Owner, 2026-11-05]** Players walk a bit faster: walk speed 32 (`Config/Movement`, was 28).
- **[Built], [Owner, 2026-11-05] Inventory with real monster icons** (Figma "Throw Eggs - Index & Inventory",
  https://www.figma.com/design/dJTVmNiMckziDaSNCniPU5): the hotbar and My Dinos show each monster's real model
  (`UiKit.monster`), not the old block stand-ins. Hotbar slots are rarity tiles with the key in a dark disc, $/s
  above, and the carried one raised with a white edge. My Dinos rows: the model on its rarity tile with its colour
  mutation in a chip, its rarity word in the rarity's colour, the name, the size mutation in silver and $/s in green,
  then EQUIP (green HOLDING when carried, PICK UP on the base) and SELL. The hotbar steps aside while My Dinos is open.
- **[Built]** While away, the base earns 50% of its $/s for up to 8 hours, collected with a CLAIM button.

---

## 8. Monsters

- **[Owner]** The creatures are **monsters**, not only dinosaurs, so any kind of creature can be made. The dinos already
  built stay, and later maps can still have dinosaurs alongside other monsters. (Whether the game's name, the "Dinos"
  labels and the code's names change too is still to be decided.)
- **[Owner]** Depending on luck, a monster can get a colour mutation, a size mutation, both or neither: "Diamond Big",
  "Gold Huge", or just "Diamond" at standard size.

### Size: two separate things [Owner]

1. **Standard size comes from progress only.** Each map has a standard size X, and a catch with no size mutation is
   always exactly X. **[Owner, 2026-11-04]** X grows only a little across the 15 maps, from 1x to 2x (about 1.05x
   per map), so every map has room for the full range of sizes.
2. **Abnormal sizes come from size mutations, and they depend on luck.** A size mutation scales the monster up from X,
   to **X × 100 at most**. More luck makes the bigger sizes likelier. 100x of map 15's 2x is about 2,000 studs, the
   most Roblox allows for one part, which is why X grows slowly (the owner chose this over a shared ceiling).

**[Owner, 2026-11-09]** X stops growing at map 7 (The Abyss, 1.35x): maps 8 to 16 all use 1.35x. And "exactly X" means
every monster: the Blender models were made at very different sizes (a Compy 4 studs long, Batastrophe 61), and X used
to multiply each model's own size, so rare late monsters came out far too big. **[Built]** Every model is now first
brought to one longest side, `Config/Catch` `standardLength` (10 studs, a player is about 5 tall), and only then
multiplied by X and its size mutation (`DinoModel.fitScale`). A Unit of Doom is 100 studs long on map 1 and 135 on
maps 7 to 16, whatever the monster.

The size mutation tiers work **the same as the reference game's**, with our own names. The reference has Big, Large,
Monstrous, Huge and Colossal **[Seen/Owner]** (Colossal exists, it just wasn't in our recordings), and a Giant size from
its Rainbow Egg **[Web, unconfirmed]**. Their order, odds and scale aren't published anywhere, so ours stay our own
numbers.

**[Owner]** Our six size mutations, smallest to biggest: **Thicc → Absolute Unit → Chonker → Mega Chonk → Planet-Sized →
Unit of Doom**. **[Built]** (`Config/Catch`), scale is on top of the map's standard size:

| Size | Chance | Income | Scale |
|---|---|---|---|
| Thicc | 1 in 10 | ×1.5 | 1.2× |
| Absolute Unit | 1 in 40 | ×2.5 | 1.8× |
| Chonker | 1 in 150 | ×4 | 2.7× |
| Mega Chonk | 1 in 600 | ×8 | 5× |
| Planet-Sized | 1 in 2,500 | ×20 | 7.5× |
| Unit of Doom | 1 in 9,787 | ×50 | 10× |

**[Owner, 2026-11-07]** The big sizes were way too big: the scales went from 1.25×, 1.6×, 2.2×, 3.2×, 5×, 8× to the
ones above, so the biggest is still clearly huge but no longer too big.

**[Owner, 2026-11-08/09]** Planet-Sized and Unit of Doom went to 13× and 18× on 2026-11-08, and were still too big on the
bases on 2026-11-09, so the list became an even ramp instead of jumping from 2.4× to 13×, and the owner then set the top
three: Mega Chonk 5×, Planet-Sized 7.5×, Unit of Doom 10× (the table above: 1.2, 1.8, 2.7, 5, 7.5, 10). Saves keep only the
size's id, never its scale, so every owner's existing monsters show the new sizes the next time their base is built.

**[Built]** Luck makes mutations and sizes likelier too, gently: their chances are multiplied by luck^0.4 (`Config/Catch`
`luckPower`), and no single one goes above a 1 in 2 chance. It's the same luck as the monster roll, counted from the
map's par, lucky throws included (section 8b). Roughly, worked out from the formula:

| Luck (counted from the map's par) | Thicc | Chonker | Unit of Doom |
|---|---|---|---|
| 1x (start of any map, its own egg) | 1 in 10 | 1 in 150 | 1 in 9,787 |
| 5x (far end of any map) | 1 in 5 | 1 in 80 | 1 in 5,300 |
| 500x (a x100 lucky throw at a far end) | 1 in 2 | 1 in 12 | 1 in 830 |
| 2,500x (a x500 lucky throw at a far end) | 1 in 2 | 1 in 7 | 1 in 440 |

The "1 in X" shown on a catch stays the normal odds.

Old saves keep their sizes under the new names (Big → Thicc, Large → Absolute Unit, Huge → Chonker, Colossal → Mega Chonk).

- **[Owner]** Models are simple, not complex at all, but must have **good faces**. All animals get the stud texture in Studio.
- **[Owner]** More colour mutations, some much rarer than others. Gold is the most common, but not too common.
- **[Built]** Colour mutations (`Config/Catch`), most common first. Each recolours the skin and leaves the face alone:

| Mutation | Chance | Income | At a map's far end (5x) | x500 lucky throw there (2,500x) |
|---|---|---|---|---|
| Gold | 1 in 30 | ×2 | 1 in 16 | 1 in 2 |
| Ruby | 1 in 80 | ×3.5 | 1 in 42 | 1 in 3.5 |
| Diamond | 1 in 200 | ×6 | 1 in 105 | 1 in 9 |
| Emerald | 1 in 500 | ×12 | 1 in 260 | 1 in 22 |
| Bubblegum | 1 in 1,200 | ×18 | 1 in 630 | 1 in 52 |
| Amethyst | 1 in 3,000 | ×30 | 1 in 1,600 | 1 in 130 |
| Shadow | 1 in 8,000 | ×50 | 1 in 4,200 | 1 in 350 |
| Ghost | 1 in 19,683 | ×100 | 1 in 10,300 | 1 in 860 |

- **[Built]** Each map's standard size is `standardScale` in `Config/Biomes`: 1x, 1.05x, 1.1x ... 1.42x for maps 1 to 8.
- **[Seen]** The reference's mutated animals are recoloured all over (gold, rainbow and so on), with the face still readable.
  It also has a Ruby mutation.
- **[Built]** Blocky models from `assets/models/blueprints.json`.

| World | Dinos, most common first |
|---|---|
| Forest | Compy, Gallimimus, Parasaurolophus, Stegosaurus, Velociraptor |
| Desert | Pachycephalosaurus, Ankylosaurus, Triceratops, Carnotaurus, T-Rex |
| Swamp | Soggy Dimetrodon, Burpasaurus, Baryonyx, Sir Chomps-a-Lot, Neckzilla, Spinosaurus |
| Volcano | Toasty Raptor, Burnt Ankylo, Hot Sauce Trike, Magma Stego, Obsidian Rex, Volcano King |
| Frozen Peaks | Brain Freeze, Woolly Rhino, Chilly Mammoth, Sabertooth, Frost Raptor, Blizzard Rex |
| Shadow Bog | Sticky Steve, Slow Bob, Terror Bird, Pitch Raptor, Tar Titan, Bog Rex |
| Starfall Crater | Craterback, Stargazer, Comet Trike, Ringhorn, Nebulasaur, Star Sovereign |
| Eclipse Temple | Idol Ollie, Mossy Mo, Lantern Larry, Jade Jaguar, Plumed Wyrm, Eclipse Devourer |

---

## 8a. The game plan

**[Owner]** Left to us to decide: how many maps and animals per map, and how the plan runs. Decided:

**[Owner, 2026-11-04]** 8 maps was a misunderstanding: the game has **15 maps** for now, with 6 animals each
(90 animals). It's built in order and released in stages, so the game can go live before all 15 are done:

1. **Maps 1 to 3 are the first release.**
2. Then the rest, one at a time, as updates that give players a reason to come back.

Each map's standard size is about 1.05x the previous map's, reaching 2x at map 15; the huge sizes come from luck
(section 8, Size).

| # | Map | Size | Animals, most common first |
|---|---|---|---|
| 1 | Forest | 1x | Compy, Gallimimus, Parasaurolophus, Stegosaurus, Velociraptor, Pteranodon |
| 2 | Desert | 1.05x | Dusty Proto, Bonkhead, Grumposaurus, Triceratops, Carnotaurus, T-Rex |
| 3 | Swamp | 1.1x | Soggy Dimetrodon, Burpasaurus, Baryonyx, Sir Chomps-a-Lot, Neckzilla, Spinosaurus |
| 4 | Volcano | 1.16x | Toasty Raptor, Burnt Ankylo, Hot Sauce Trike, Magma Stego, Obsidian Rex, Volcano King |
| 5 | Frozen Peaks | 1.22x | Brain Freeze, Woolly Rhino, Chilly Mammoth, Sabertooth, Frost Raptor, Blizzard Rex |
| 6 | Shadow Bog | 1.28x | Sticky Steve, Slow Bob, Terror Bird, Pitch Raptor, Tar Titan, Bog Rex |
| 7 | The Abyss | 1.35x | Spiral Gary, Derpichthys, Dunkleosteus, Plesiosaur, Megalodon, Mosasaurus |
| 8 | Starfall Crater | 1.42x | Craterback, Stargazer, Comet Trike, Ringhorn, Nebulasaur, Star Sovereign |
| 9 | Eclipse Temple | 1.49x | Idol Ollie, Mossy Mo, Lantern Larry, Jade Jaguar, Plumed Wyrm, Eclipse Devourer |
| 10 | Forbidden Library | 1.56x | Inkling, Hermit Tome, Wax Hound, Quillback, Hex Owl, Tome Tyrant |
| 11 | Midnight Carnival | 1.64x | Jack Snap, Popcorn Fiend, Twisty, Nightmare Mare, Grinmaster, Big Top Terror |
| 12 | Clockwork Citadel | 1.72x | Wind-Up Wally, Sprocket, Kettle Belly, Gearjaw, Drillhorn, Chrono Rex |
| 13 | Thorn Kingdom | 1.81x | Bramble Brat, Grandma Gnash, Sir Skewer, Hart Attack, Hydrangry, Wrathorn |
| 14 | Spore Hollow | 1.9x | Toad Rage, Morel Panic, Antagonist, Sporantula, Gillotine, Shroomageddon |
| 15 | The Weeping Dark | 2x | Teddy Wrecks, Good Boy, Casket Case, Wailing Widow, Death Knell, Endless Grief |
| 16 | Shattered Mirror | 1.35x (capped) | 12 on this map **[Owner, 2026-11-13]**, all made in Blender, not imported: Paw de Deux, Frill Seeker, Dressed to Kill, Wrecking Ballroom, Swanquish, Mane Event, then the six rarest: Stilt Life, Prism Break, Moth-er of Pearl, Vainglory, Mirror Mirror, Royal Pane (section 9, map 16) |

**[Owner, 2026-11-13] Four more on maps 14 and 15, rarer than their 8:** "even more aggressive than the rarest", each with a
unique animation and an effect or object animated on it from the map's theme, made in Blender, clean geometry and clean
animations "including the idle". Their rarities, chances and money came on 2026-11-14: see "End-game rarities" below.
**[Built, in Blender]** `assets/models/build_spore_hollow_apex.py`, `build_weeping_dark_apex.py` and what they
share, `apex_kit.py`; FBX files ready in `fbx/14_SporeHollow/Animals/` and `fbx/15_WeepingDark/Animals/`, not imported yet. Names are ours.
Spore Hollow: **Rot Weiler** (three heads that strike in turn, a mane of acid), **Acid Reign** (a king cobra under a crown of
thorns turning in the air, which tips over its face as it strikes), **Cap Punishment** (a tyrant with a spinning death-cap saw on
an arm out of its back), **Sporeactor** (a walking reactor: a core of light in two tumbling rings, rods rising from its back).
The Weeping Dark, still no colour and red only for eyes: **Grim Weeper** (scythes for arms, a wheel of red eyes turning behind
it), **Cage Rage** (its ribs are a second mouth round a heart full of eyes), **Mourning Star** (a tail that whirls a spiked star
with eyes in it), **Nevermore** (a giant raven with a bare skull, a ring of feathers circling over it that bursts outward).
Their attacks and the bones that turn all the time (`Halo`, `Wheel`, `Hoop`, `Saw`) are in `DinoLifeController` already, so they
move once imported and tidied. Each .blend has three looping actions, Walk, Idle and Attack. Nothing is thrown or dripped.

**[Owner, 2026-11-06] 8 monsters a map, not 6:** two more each, made in Blender and animated, nicer than the ones before and
more aggressive map by map, 6 at a time, a prompt each. **[Built]** in Blender, `DinoLifeController` (`SWAY`) and `Config/Dinos`. Their
rarities are **ANCIENT** and **SECRET** **[Owner]** (`UiKit.RARITY_ORDER`), after Mythic; special monsters stay Mythic. They're each
map's prizes (`prize = true`): the rarest about 1 in 20,000, luck reaches them (a x500 throw at a far end gives the 7th about
half the time, the 8th about 1 in 7), but the pity rules and the new map gift count from the 6th, so they're never handed out.

**[Owner, 2026-11-08] Rarity words climb with the maps.** "As you make progress in the game the rarities should only be
higher": the first map tops out at Epic, the second has 2 Epics, the third has no Common, 2 Epics and a Legendary, and so on.
**[Built]** (`Config/RarityLadder`, read by `UiKit.rarityOf` everywhere: Index, plot, tags, reveal, Sell, Details). Only
the word changes; each map's odds stay in `Config/Dinos`. Commonest first:

| Map | Words | Map | Words | Map | Words |
|---|---|---|---|---|---|
| 1 | C C C U U R R E | 6 | R R E E L L M M | 11 | E L L M M A A S |
| 2 | C C U U R R E E | 7 | R E E L L L M M | 12 | L L M M A A A S |
| 3 | U U R R R E E L | 8 | R E E L L M M A | 13 | L L M M A A S S |
| 4 | U U R R E E L L | 9 | E E L L M M A A | 14 | M M A A A S S S + N D O X |
| 5 | U R R E E L L M | 10 | E L L M M M A A | 15 | A A A A S S S S + N D O X |

The Deep End's monsters keep their home map's word. Rules that name a rarity follow the words: the surprise gift and
x100/x500 lucky throws (section 13).

**[Owner, 2026-11-14] End-game rarities.** "More rarities just for these worlds", "more nice and crazy than secret", with
"unKnown" as one of them, and "starting from weeping dark there should not be a mythic anymore". The economy and luck must
give no advantage to players who only play for free: "of course they can get it but not easy". And the next map's 12
monsters get the same system. **[Built, not tested in Studio]**
- **Four words above Secret**, one for each of a map's 9th to 12th monster: **NIGHTMARE** (blood red, flickers and beats),
  **DOOMSDAY** (yellow burning to red, embers and sparks), **OBLIVION** (black letters, ice-cyan rim, glitches) and
  **UNKNOWN** (bone white, and its letters scramble into ?#%! as it glitches). Names and looks are ours (`Config/Rarity`,
  `UiKit.RARITY`); no Figma design yet.
- **Words now:** map 14 `M M A A A S S S N D O X`, map 15 `A A A A S S S S N D O X` (no Mythic), map 16 ready as
  `A A A S S S S S N D O X` (`Config/RarityLadder`).
- **The 8 monsters** (`Config/Dinos`, `prize = true, apex = true`), rarest last. Spore Hollow: Rot Weiler, Acid Reign,
  Cap Punishment, Sporeactor. The Weeping Dark: Grim Weeper, Cage Rage, Mourning Star, Nevermore.

  | Place | Word | Chance in Config | Shown as about | Money against the map's 8th |
  |---|---|---|---|---|
  | 9th | Nightmare | 149,993 | 1 in 128,000 | 4x |
  | 10th | Doomsday | 600,011 | 1 in 512,000 | 20x |
  | 11th | Oblivion | 2,500,009 | 1 in 2.1 million | 100x |
  | 12th | Unknown | 9,999,991 | 1 in 8.5 million | 500x |

  So map 14's Unknown earns 5x map 15's 8th, and each map's Unknown sits between the next map's 8th and 9th.
- **Who gets them** (`Config/Catch` `luckyHits`; numbers from the roll's own code):
  - **x100** (R$ 9) stops at the 9th: 72% the 7th, 22% the 8th, **6% a Nightmare**, never anything above.
  - **x500** (R$ 39) reaches all of them and leans to the rare end (its own `falloff` 0.5): 48% the 7th, 26% the 8th,
    **13.6% Nightmare, 6.8% Doomsday, 3.3% Oblivion, 1.7% Unknown** (one Unknown in about 59 throws). On average it pays
    about 1,100x the map's best normal monster, against 50x for a x100. On the 8-monster maps a x500 is now 65% the 7th
    and 35% the 8th (was 77 / 23); x100 is the same there.
  - **Free:** a plain throw gives any of the four about 1 in 97,000 at a map's start and 1 in 18,000 at its far end (the
    Unknown 1 in 1.6 million). No guarantee ever gives one (pity, jackpot, new world, gift: they are prizes), and the
    daily x50 never does. The real free way is the daily reward's day-7 x500 (and the one-time x500 play gift): one in
    four is one of the four, so about one a month for a player who never misses a day.
  - **End-game streak [Owner, 2026-11-14: "let's not make it that unfair for free players", without making them "way too
    powerful"]** (`Config/Hooks` `apexStreak`, save field `throwsSinceApex`): after 300 throws in a row on a 12-monster
    map without one of its four, the next plain throw is its 9th or 10th (Nightmare 80%, Doomsday 20%), colour and size
    rolled as usual, with "NIGHTMARE STREAK!" after the reveal. About two and a half hours of throwing: one or two a
    week at an hour a day. Never Oblivion or Unknown: those stay for luck and x500. Catching one any other way starts
    the count again; a lucky throw or another guarantee keeps its own rules and the streak waits.
  - Shop text changed to stay true: "one of the map's top monsters, 1 in 1M+" and "a top monster, up to the map's very
    rarest, 1 in 100M+". Details shows the exact chances per map, from the same code as the roll.
- **Index:** maps 14 and 15 show 12 cards (three rows of smaller cards). The world's reward still needs only its first 8,
  so worlds completed before keep their +10% cash; the four are extras (`IndexService`, `apex`). The Index total is 128.
- **Sell stand:** the rarity buttons are two rows now (ALL and 12 rarities).
- The play simulation is unchanged (average free player at map 15 in 21.7 h): money barely changes the pace.
- **A new 12-monster map** copies this: `docs/MAP_RECIPE.md` step 9, "Monster numbers".
Income carries on the same steps: 1,500 and 5,000 on the Forest, times 100 a map. So far, rarest last:

| Map | 7th | 8th | What's new in how they move |
|---|---|---|---|
| Forest | Therizinosaurus: a violet fluffball with huge golden scythe claws, carefully holding a daisy | Amargasaurus: a sweet blue long-neck with a rippling sunset sail | Only sways: gentle giants |
| Desert | Scorchion: a truck-sized scorched scorpion | Rexhotep: a mummified T-Rex with a gold death mask, royal headcloth, pharaoh's beard, and a tiny crook and flail in its tiny arms | Pincers snap, the sting stabs |
| Swamp | Mossmaw: a giant snapping turtle with a bog on its back and a worm lure in its open beak | Titanoboa: a hooded giant snake, reared up, fangs out | The neck lunges and the jaw bites; the snake slithers |
| Volcano | Magmapede: a street-long centipede of black glass, lava showing between its plates, its front third reared up on red-hot sickle fangs | Cinderdrake: a black dragon cracked with lava, wings raised, a furnace for a throat | They rear back, lunge and spit fire; Magmapede's legs ripple, Cinderdrake's wings beat |
| Frozen Peaks | Ramvalanche: a mountain ram gone wrong, great curled horns of blue ice, crystals out of its back, fangs no ram should have | Abominator: a huge hunched yeti, a bare dark face that's mostly mouth, ice tusks, crystals growing out of its shoulders | The whole body attacks: Ramvalanche paws the ground and charges, Abominator smashes both fists down and ice flies |
| Shadow Bog | Skeeterror: a mosquito the size of a house, a skull for a head, a bone needle longer than its body, its swollen belly glowing | Manhandler: a giant hand of tar walking on its fingers, a mouth across the palm, its forearm dragging behind | Skeeterror's wings blur and it stabs twice; Manhandler drums its fingers one by one, then rears up and grabs |
| The Abyss | Shrimpact: a neon mantis shrimp, club fists folded under its chin | Kraken: a huge dark squid, a ring of hooked arms round a beak, two long hunting arms held up over its head | They hit from across the base: Shrimpact's punches crack the water and rings of shock fly off them; the Kraken's arms shoot out straight and drag back |
| Starfall Crater | Moonwhale: a whale of night sky with a crater on its back and a little moon going round it | Constellion: a lion of night sky with a constellation on its flanks and a mane like the sun | **[Owner]** faces stay calm here (no teeth, level lids). They don't attack, the sky does: Moonwhale breathes out a fountain of stars, Constellion lifts its head and sings, and meteors fall round it |
| Eclipse Temple | Praying Menace: a temple mantis in a gold mask, obsidian scythes folded as if in prayer | Batastrophe: a giant bat in a gold mask, wings wider than a temple, a mouth that's most of its face | They come through the air: Praying Menace throws two spinning crescents of jade that come back to its hands; Batastrophe climbs, screams rings of sound, folds its wings and drops |
| Forbidden Library | Bookworm: a giant ink-black worm, its front a round hole lined with needles | Papercut: a gaunt thing the colour of old paper, razor claws, a mouth too wide | **[Owner] maps 10 to 12: "simple yet very very aggressive", no accessories, no auras.** Bare bodies, nothing glowing or thrown. Every 2 seconds they throw themselves forward, bite three times and shake what they caught, arms raking (`Maul`) |
| Midnight Carnival | Last Laugh: a hyena with a grin round its head | Unbearable: a huge bear, head as big as a barrel | The same |
| Clockwork Citadel | Tick-Tock: a bloated bronze tick on eight hooked legs, all jaws | Clockodile: a long heavy iron crocodile, a third of it jaw | The same |
| Thorn Kingdom | Thornado: a lean black thing with four thorned arms and a waist that turns right round | Thorn to Bits: a boar-backed brute, a hill of shoulder, a back of thorns, hooked tusks | **[Owner] maps 13 to 15: "very very aggressive", "the most aggressive", unique animations.** Bare again, each its own attack, faster than the Maul. Thornado spins twice on its own hips, arms flung out, and falls forward biting; Thorn to Bits stands every thorn on end, rams and hooks upward three times |
| Spore Hollow | Mouth Breather: a body that's nothing but a mouth, on four short claws | Spore Loser: a gaunt thing on folded hopper's legs that can't keep still | Mouth Breather leaps every second, skull flung right back, and lands jaws first; Spore Loser ricochets twice a second, left, right, ahead and home, biting each time it lands |
| The Weeping Dark | Inconsolable: a hunched colossus, arms like tree trunks, a mouth open in one long scream | Last Breath: the last monster of all, a starved thing on stilts with a neck that shouldn't stretch and does | Black, ash and bone, red only for eyes. Inconsolable hammers the ground with both fists, four blows a second, and never stops; every second Last Breath's neck stretches twice its length, left, ahead, right, and snaps shut |

### The style as you advance
**[Owner]** Keep the same chunky stud style, but as the maps go on, add absurd, funny models and names alongside
good-looking, aggressive dinos.

- **Map 1 is cute:** friendly faces and real dino names.
- **From map 2, each map mixes the two:** common animals are the silly ones (goofy names, derpy faces), and the rarest are the
  fierce ones (angry brows, smaller eyes, lots of teeth, horns, dark colours).
- **Both get stronger with each map:** sillier jokes and meaner, more fantastical dinos. The last map's rarest should look like a boss.
- **Names are ours:** none come from the reference game, and they stay readable in the letter-by-letter reveal.
- **[Owner] Map 4, Volcano:** a bit more aggressive than the maps before, with a different face.
  **[Built]** The Volcano face: eyes that glow like embers with an upright slit pupil, under a heavy brow that slants
  down to the nose, and a snarl that glows inside like a furnace, jagged teeth top and bottom and often tusks. Even
  the silly ones are angry: a raptor still smoking from the lava, an ankylo whose tail club is on fire, a trike that ate
  the hot sauce (chili horns, steam, a burning tongue). The rare ones are lava and obsidian, and Volcano King, the map's
  boss, is a hulking lava monster walking on its knuckles with a crown of burning horns and a volcano on its back.
  They also have a **jaw bone**: they snap it as they walk and roar once per idle (head up, jaw wide, arms out), in
  Blender (`build_volcano.py`) and in the game (`DinoLifeController`).
- **[Owner] Map 8, Starfall Crater (2026-11-04):** the run of ever-angrier faces stops here. Nice-looking,
  interesting monsters that fit the biome: **not cute, but not aggressive, above all in the face.**
  **[Built]** The starfall face (`build_starfall_crater_monsters.py`): long half-closed almond eyes, dark as the night
  sky, with a glowing four-point star for an iris under a level lid of skin (a level lid reads calm; slanted ones read
  angry or sad), and a quiet closed mouth with no teeth. Inside the mouth is the night sky dotted with stars, so the
  roar turns into a song. Calm, old, a little strange: Craterback (a grazer with a crater on its back and a fallen
  star stuck in it), Stargazer (a stilt-legged bird always looking up, star-tipped plumes), Comet Trike (its frill is
  a comet's head, the tail streaming back over its body), Ringhorn (a stag with crystal antlers and a planet's ring
  round them), Nebulasaur (a long-necked giant made of night sky, a pink nebula on its flanks) and Star Sovereign,
  the boss: a robed king of the stars with a crown, a halo, a star-topped staff and a stardust beard. Its boss look
  comes from size and grandeur, not from a snarl.
- **[Built] Map 9, Eclipse Temple (2026-11-04):** after Starfall's calm faces the run picks up again, for the first
  of the mysterious, dark maps: temple thieves and squatters at the common end, the temple's guardians at the rare
  end, then a boss. They share the **eclipse eye** (`build_eclipse_temple_monsters.py`): a black iris ringed with
  glowing jade, like the eclipsed sun over the map. The silly ones have it in a white eye; the fierce ones have no
  white at all, just the black eye and its jade ring under a gold mask, which is what makes them unsettling. Idol
  Ollie (a cross-eyed toad wearing a stolen gold idol as a helmet, the idol's stern face peering over its eyes, its
  tongue hanging out), Mossy Mo (a sleepy sloth with a temple ruin and a little jungle on its back, one eye shut;
  its roar is a yawn), Lantern Larry (a lanky temple monkey with a lantern, a gold mask pushed up on its head and
  a gold tooth in a sneaky grin), Jade Jaguar (an obsidian guardian cat with glowing jade rosettes and a gold mask),
  Plumed Wyrm (a feathered serpent-dragon with a huge crest and ruff of green, gold and red plumes) and Eclipse
  Devourer, the boss: a four-armed obsidian god-beast that swallowed the sun, with a black sun and its corona
  behind a pale skull of a head under a gold mask, the eaten sun glowing in its chest, a black sun in each raised
  hand, great horns, a third eye and jade fire in its throat. The rarer ones stand bigger.

- **[Owner] Map 10, Forbidden Library (2026-11-04):** monsters that suit the biome, aggressive in a good way, animated.
  **[Built]** `build_forbidden_library_monsters.py`: all six glare and bare page-white teeth, sharing the **ink eye** (a
  glowing violet iris with a slit pupil under a brow slanting to the nose; white eyes on the common ones, black sockets
  on the fierce ones) with violet ink glowing in their mouths and dripping off them: Inkling (an ink gremlin, quill
  crest, nib tail), Hermit Tome (a crab under an open book, pincers up), Wax Hound (candles burning on its back),
  Quillback (a raptor bristling with ink-dipped quills, nib claws), Hex Owl (gold spectacles, page feathers, a chest
  of glowing writing) and Tome Tyrant, the boss (its head a grimoire whose covers bite, a crown of candles, broken
  shackles, a ribbon tail). Plain colours in Blender, like the map. Renders and
  `forbidden_library_animation_preview.mp4` in `design/world/monsters_forbidden_library/`, FBX in
  `fbx/10_ForbiddenLibrary/Animals/`; they go in `Config/Dinos` once imported.

- **[Owner] Map 11, Midnight Carnival (2026-11-05):** monsters that suit the biome, scary and aggressive at the same
  time, animated. **[Built]** `build_midnight_carnival_monsters.py`: the fair's attractions come alive, all teeth.
  They share the **carnival face**: chalk-white greasepaint, black harlequin diamonds over glowing neon-pink eyes with
  pinprick pupils, and a crimson painted grin carrying a mouth of needle teeth up the cheeks (white eyes on the
  common ones, black sockets on the fierce ones): Jack Snap (a jack-in-the-box, clown head on a spring neck),
  Popcorn Fiend (a popcorn box whose top half is a jaw), Twisty (a balloon-animal dog with devil-horn ears),
  Nightmare Mare (a carousel horse with the brass pole through its back and a neon mane), Grinmaster (the
  ringmaster, top hat, cracking whip) and Big Top Terror, the boss (the big top on its back, a giant clown head
  with a crown of bulbs, arms reaching from under its ruff). Plain colours in Blender. Renders and
  `midnight_carnival_animation_preview.mp4` in `design/world/monsters_midnight_carnival/`, FBX in
  `fbx/11_MidnightCarnival/Animals/`; they go in `Config/Dinos` once imported.

- **[Owner] Map 12, Clockwork Citadel (2026-11-05):** monsters that suit the biome, animated as well, and nice.
  **[Built]** `build_clockwork_citadel_monsters.py`: the citadel's machines built in the shape of beasts and wound up,
  silly at the common end, fierce at the rare end, then a boss. They share the **lens eye**: a riveted brass bezel
  round a glass lens with a glowing iris (white glass and an electric-blue iris on the silly ones, dark glass and a
  furnace-orange glare under brows slanting to the nose on the fierce ones), and every one has a **wind-up key** in
  its back that never stops turning: Wind-Up Wally (a tin toy rex, mismatched googly lenses, chattering tin teeth),
  Sprocket (a copper clockwork pup, flying goggles pushed up, flapping ears, tongue out, coil-spring tail), Kettle
  Belly (a grumpy walking boiler, glowing furnace belly, chest gauge, chimney hat, wrench claws), Gearjaw (a steel
  raptor with a buzz saw spinning along its skull and a furnace in its throat), Drillhorn (an iron triceratops with
  a gear frill and a drill for a nose horn that never stops boring) and Chrono Rex, the boss (an iron tyrant with a
  giant brass gear turning on its back like a sail, smokestacks, a furnace heart behind a riveted porthole, a crest
  of gear teeth and fire in its throat). The parts that turn for ever ride their own bones (`Key`, `Drill`, `Cog`),
  which `DinoLifeController` turns at a steady speed on top of the walk and idle (its `SPIN` table, the same as the
  script's). Plain colours in Blender. Renders and `clockwork_citadel_animation_preview.mp4` in
  `design/world/monsters_clockwork_citadel/`, FBX in `fbx/12_ClockworkCitadel/Animals/`; imported into `Assets.Dinos`
  and in `Config/Dinos` (2026-11-05).

- **[Owner] Map 13, Thorn Kingdom (2026-11-05):** monsters that fit the biome, animated, aggressive and chaotic looking,
  built in Blender. **[Built]** `build_thorn_kingdom_monsters.py`: the kingdom slept for a thousand years and these are
  the things that tore themselves awake, furious, the briars still growing through them. All six are hostile, the
  common ones too, so the silliness lives in their names and one joke each. Nothing is mirror symmetric or stands
  straight. They share the **sleepless eye** (wide open, a crimson iris and a pinprick slit, never the same size
  twice; white and bloodshot on the feral ones, in a black socket under a slab of brow on the fierce ones) and the
  **rose maw** (a jaw hanging open at rest, crooked teeth of every length, a rose glowing in the throat): Bramble Brat
  (a ball of briars that is nearly all mouth, one huge eye, one tiny, a third on a stalk, a long whipping tongue),
  Grandma Gnash (the wolf that ate her and kept the clothes: nightcap, shawl and bent spectacles), Sir Skewer (armour
  with nobody in it but briars bursting from a hole in its chest round a glowing rose, a hound-snout visor, a giant
  spindle for a lance and a spinning wheel ringed with thorns for a shield), Hart Attack (a stag with a bare skull for a
  face, open ribs with a rose burning inside, vast crooked briar antlers with spare eyes, snapped arrows in its flank),
  Hydrangry (a heap of violet roots and crimson blooms with five snapping heads on writhing necks) and Wrathorn, the
  boss (the sleeping king turned dragon: wings of crimson blades, rose fire veining its hide, a rusted crown jammed on
  crooked horns, five eyes, a mace of thorns on its tail, and in its chest a second mouth, a ring of teeth grinding
  for ever round a burning rose). They thrash: briar whips on `Lash` bones never stop, and `DinoLifeController`'s
  `THRASH` table adds head jerks, gnashing and shudders on top of the walk and idle, the same as the script's. The
  wheel, the chest maw and the crown's ring of petals turn on the `SPIN` bones. Plain colours in Blender. Renders and
  `thorn_kingdom_animation_preview.mp4` in `design/world/monsters_thorn_kingdom/`, FBX in
  `fbx/13_ThornKingdom/Animals/`; imported into `Assets.Dinos` and in `Config/Dinos` (2026-11-05).

- **[Owner] Map 14, Spore Hollow (2026-11-05):** monsters that suit the map, "very aggressive and nice, more aggressive
  than the 13th map", built in Blender and animated nicely. **[Owner, 2026-11-06]** The first six came out toy-like and the
  owner didn't like them at all: they want them **more scary and aggressive**. **[Built]** The same six (same names, ids
  and rig), rebuilt from scratch in `build_spore_hollow_monsters.py`: down here the rot is the predator, eating into
  everything that lives in the hollow and wearing it. All six are dark and rotten with bone-pale teeth, claws and spikes,
  crusts of pale mycelium bursting out of the hide, black caps with gills glowing chartreuse under them, and none of them
  stands up straight: they crouch, hunch and reach, heads low and thrust at you. They share the **rot glare** (no white in
  any eye: a burning chartreuse iris with a thin upright slit in a black socket, under a brow slanting hard to the nose,
  glowing threads creeping out of it, and spare eyes burst up through the hide round it) and the **rot maw** (most of the
  face, hanging wide open on two rows of long needle teeth, gills glowing back to a glowing throat, glowing strings of
  mycelium stretched between the jaws like drool): Toad Rage (a bloated black cave toad crouched to spring, its head
  nearly all mouth, burning eyes on bumps under warty brows, bone spikes down its back, black ink caps and shelf fungi
  growing out of it, splayed hooked claws), Morel Panic (a gaunt ash-pale crawler on four long limbs, knees and elbows
  above its back, ribs and spine showing, long black-clawed fingers reaching, a black morel for a hood with embers in its
  pits, and under it two burning eyes and a jaw hanging open in a scream), Antagonist (a black ant reared up with its front
  legs raised to grab, huge serrated mandibles spread round a mouth of needles, white mycelium bursting from every joint,
  a sting curled over its back, and the fungus that took it arching out of its head to dangle a glowing club in front of
  its face), Sporantula (a black spider, front legs raised high to strike, bone knuckles, two burning eyes and six more,
  huge bone fangs dripping glowing venom, a swollen abdomen with glowing chevrons and black caps bursting out of it),
  Gillotine (a towering ash-pale mantis, two great serrated blades raised wide, slanted burning eyes, bone horns and
  black ink caps bursting from the back of its head, side jaws round a mouth of needles, wings stood up behind it each
  with a huge glaring eye) and Shroomageddon, the boss (a colossal black titan on its knuckles, a ragged black cap pulled
  down over its head like a hood, seven burning eyes under it, a crown of bone horns, a mouth that opens four ways, its
  chest torn open on a glowing heart behind ribs of bone, a forest of black and deathly pale caps round a spore geyser on
  its back, mycelium whips, and a club of bone spikes on its tail). What moves is unchanged, so the game needed no new
  code. **On top of map 13's thrashing (`Lash`, `Snap`) they pounce and pour
  spores (`POUNCE` and `VENT` in `DinoLifeController`, the same as `pounce_of` and `vent_rise` in the script, compared
  number by number):** every 4 seconds they rear back, front legs up and side jaws spread, then lunge, neck down, jaw
  flung open, arms raking and side jaws slamming shut; the side jaws (`MandL`, `MandR`) gnash the rest of the time and
  fling open in the roar; and spore clouds rise for ever out of vents in their hides (`Vent` bones). A step below map
  15's rage on purpose: no charge, and the body doesn't surge. Plain colours in Blender. Renders,
  `spore_hollow_animation_preview.mp4` and close-ups of each one pouncing (`spore_hollow_pounce_preview.mp4`) in
  `design/world/monsters_spore_hollow/`, FBX in `fbx/14_SporeHollow/Animals/`; imported into `Assets.Dinos` and in
  `Config/Dinos` (2026-11-05): chances 2, 4, 12, 60, 400, 3000; income 1e26, 3e26, 1e27, 4e27, 2e28, 5e28 (100x
  Thorn Kingdom's), so throws reach 14,700. In play at their real size every whip, fang, jaw, side jaw, arm, wing and
  vent was measured moving, the spores rising 1.14 studs a cycle (0.6 x 1.9). That also lets map 15's go in. **The
  rebuilt six (2026-11-06) are exported to the same folder; they replace the old ones in `Assets.Dinos` once the owner
  re-imports them and they're tidied (`studio_tidy.py SporeHollow build_spore_hollow build_spore_hollow_monsters`). `Config/Dinos` doesn't
  change, as the ids are the same.**

- **[Owner] Map 15, The Weeping Dark (2026-11-05):** monsters that suit the map, "very aggressive, the most aggressive
  out of all the animals we did", built in Blender and animated nicely. **[Built]** `build_weeping_dark_monsters.py`:
  everybody here walked into the dark to look for the sun, and these are what came back, grief gone bad, each one
  something from the map turned to rage. No silly ones at all, the commons included: the jokes are only in the names. They
  keep the map's rule, no colour, red only ever for eyes, with a lot of pale in them, which also keeps them readable in the
  map's very dark light. They share the **weeping glare** (burning eyes in black sockets under brows slanting hard to the
  nose, crying as they rage, the tears really falling) and the **throat eye** (at the back of every mouth, another red eye
  looks out): Teddy Wrecks (the Lost Bear, its whole face torn open into a mouth of nails, a button dangling by a thread,
  stuffing bursting from its belly), Good Boy (the dog that waited too long: a gaunt hound, ribs showing, hackles up, its
  collar still on and the chain it snapped lashing behind it), Casket Case (a coffin for a head, lid and box a snapping
  jaw of nails, galloping on four long pale arms, two more reaching ahead, its shroud streaming), Wailing Widow (tall,
  black and veiled, a bone mask, a jaw hanging to its chest in one long scream, veil strips lashing, pale arms as long as
  it is tall), Death Knell (a hulking brute on its knuckles with a great black bell for a head: the bell is the mouth, its
  rim a ring of teeth, and the clapper is a tongue on a chain with a red eye on the end) and Endless Grief, the boss and
  what's behind the Last Door: the door's eye in a colossal hood, a mouth too wide for anything, huge pale hands clawing
  at its own face, the door's shackles on its wrists, and the arms of everyone it took thrashing out of its back. **They
  don't just thrash, they attack (`RAGE` in `DinoLifeController`, the same as `rage_of` in the script, compared number
  by number):** every 4 seconds they load up and lunge, the body heaving back and slamming forward, the head driving in,
  the jaw dropping and biting shut, the tail cracking; arms claw one after the other; they snap at the air between
  lunges; and they pant and shake all the time. They charge, a stride taking 2/3 of a second (`Config/DinoLife`
  `rageStrideSeconds`), and their tears fall for ever on `Drip` bones (`DRIP`). Endless Grief's hands pull away from its
  face in the roar and the lunge (`Palm` bones). No gore: nothing bleeds, and stuffing and bones are all the insides
  you see. Plain colours in Blender. Renders, `weeping_dark_animation_preview.mp4` and close-ups of each one attacking
  (`weeping_dark_attacks.mp4`) in `design/world/monsters_weeping_dark/`, FBX in `fbx/15_WeepingDark/Animals/`, imported into `Assets.Dinos` (2026-11-05). Tested
  in play at their real size: all six lunge, cry and walk head first at the charge. In the dark most of them are only eyes and
  tears, so **a reveal lifts this world's light** (`Config/Lighting` `reveal`, applied by `SkyController` while the reveal's
  `WorldFocusZ` is set), which works for a monster of any size. A real catch hasn't been seen yet. **Not in `Config/Dinos`
  yet:** they go in only after map 14 has monsters, as eggs land up to the last world with monsters, so a monster-less map 14
  would be a world eggs could land in with nothing to catch. Their line then: chances 2, 4, 12, 60, 400, 3000; income 1e28,
  3e28, 1e29, 4e29, 2e30, 5e30 (100x map 14's, which is 100x Thorn Kingdom's).

### How animal models are made
- **Simple shapes:** chunky blocks and tapered blocks, no fine detail. The silhouette should read from far away.
- **Good faces:** big eyes with a pupil and a highlight, an expressive brow, clear teeth or mouth. Each animal has its
  own personality. The face is where the effort goes.
- **No studs modelled**, but every model has UV maps laid out so the stud texture repeats evenly in Studio.
- **Parts by colour role** (body, accent, belly, eyes, teeth and so on), so a mutation can recolour the skin and leave
  the eyes and teeth alone, keeping the face readable.

---

## 8b. Luck and keeping players hooked

**[Owner, 2026-11-04]** The main goal: players get hooked, progress is easy, and now and then they get a very nice
monster so they stay. The luck number climbing during the flight should be big and exciting, and a 100x luck boost
should feel huge.

**[Owner, 2026-11-07]** A game that finishes in a few hours of play isn't good: if a free player can complete it in half a
day, it will die quickly. The game needs a hook that keeps players for a long time and brings them back every day. Not
designed yet; the build plan is in `docs/RETENTION_PLAN.md`.

- **[Built] The number on screen climbs from 1x to 50x across the whole game** (**[Owner, 2026-11-06]**: billions
  were useless; 50x is the most without boosts). Each map ends at: Forest 3, Desert 5, Swamp 7, Volcano 9, Frozen
  Peaks 11, Shadow Bog 14, Abyss 17, Starfall 20, Eclipse 24, Forbidden 28, Carnival 32, Clockwork 36, Thorn 40, Spore
  45, Weeping Dark 50 (`Config/Biomes` luck). The egg multiplies it by its luck against the egg made for the map it
  lands in (`Luck.eggFactor`, worked out once so it doesn't jump mid-flight), then Server Luck and lucky
  throws multiply on top (a x500 throw can show thousands). The number is only for show: the roll has its own luck,
  1x at every map's start to 5x at its far end (`Luck.rollRange`), times that egg factor and the boosts
  (`Luck.forRoll`). A newer egg gives a bit more (about 1.2x per egg), an older one less, and a much older one leaves
  only the map's starting odds (like the reference, where older food brings only the commonest animals).
- **[Built, 2026-11-06] The luck sign during the flight is plain text, no panel** (**[Owner]**): the number big
  (92) with a thick outline and a tint of the world's colour, LUCK under it, and the world's name big (58) in its
  colour. It pops when the egg crosses into a new world (`ThrowCinematic.buildLuckPanel`).
- **[Built, 2026-11-06] How luck picks the monster** (`Config/Catch` `pick`, `DinoRoll`). **[Owner, 2026-11-06]**
  After the owner's friends played: "the luck is fucked, the monsters are the same every single time", x100 can give
  "just a 1 in 32k" and x500 always gives the best, never the second best. The whole roll was redone following the
  reference game's catch rules, as game.guide's catch calculator describes them (its food aims at a rank, each
  rank's chance falls off smoothly away from the aim, and your last catch is 200x less likely, the one before 2.5x):
  - **Luck aims at a "1 in X":** the map's commonest monster's odds times the luck. 50x luck on the Forest
    (commonest 1 in 2) aims at 1 in 100, the Stegosaurus.
  - **Monsters near the aim come most,** and each one further away, rarer or more common, is that many times less
    likely: 10x rarer or 10x more common than the aim is 10x less likely (`falloff` 1). So luck really multiplies a
    rare monster's chance (x100 makes a 1 in 2,000 a 1 in 20), and monsters far more common than the aim fade out.
  - **The aim stops halfway between the two rarest** (`topAim` 0.5), so with huge luck the best and the second best
    come about equally and the third now and then. Nothing is ever certain.
  - **No repeats** (`repeatPenalty`): the monster you just caught is 200x less likely on the next throw, the one
    before it 2.5x (kept in the save, `recentCatches`). The same monster twice in a row went from 40-55% of throws to
    under 1%, and 10 throws show about 4 different monsters instead of 2 or 3.
  - What it gives with each map's own egg, % per monster from the commonest to the rarest (the game's own code run
    in a simulation, before the no-repeat rule):

    | Throw | Forest | The Weeping Dark |
    |---|---|---|
    | Normal, map start | 66, 26, 7, 1.3, 0.3, 0.07 (rarest 1 in 1,500) | 59, 29, 10, 2, 0.3, 0.04 (1 in 2,600) |
    | Normal, far end | 15, 38, 38, 8, 1.5, 0.4 (1 in 265) | 16, 32, 42, 8, 1.3, 0.2 (1 in 590) |
    | x100, map start | 1, 2, 9, 44, 35, 9 | 1, 2, 6, 31, 52, 7 |
    | x100, far end | 0.2, 0.4, 2, 9, 44, 44 | 0.3, 0.6, 2, 9, 58, 31 |
    | x500, anywhere | 0.2, 0.4, 2, 9, 44, 44 | 0.2, 0.5, 1.4, 7, 46, 46 |

    With the no-repeat rule, 20 x500 throws in a row give the best about 38% of the time, the second best 38% and
    the third 19%, a colour 70% of the time, and 1 in a million or rarer (GODLY) 36%.
  - The old roll, for the record: luck multiplied every monster but the commonest, so it only moved catches from the
    commonest to the second (70% of every catch on late maps, whatever the luck), and the rarest stayed about 1 in 1,100.
  - **For the 8-monster maps:** with 6 monsters from 1 in 2 to 1 in 3,000, a x100 at a map's far end already reaches
    the aim's stop (on the Desert, 1 in 2 to 1 in 1,000, from its middle), so it gives the same monsters as a x500,
    which only keeps twice the colour and size luck. Spread the odds so the rarest is about 1 in 20,000 or rarer and
    x100 and x500 stay apart everywhere. Pity and the new-map gift count "the map's N rarest", so they need no change.
  - Average income per throw is about 2x what it was (fewer commonest monsters, more rare ones): the economy
    timeline in section 12 was worked out with the old roll.
- **[Built] Lucky throws** (`Config/Shop` `luckyThrows`, `LuckyThrows`). **[Owner, 2026-11-04]**
  A luck boost is for **one throw only**, and the shop sells several sizes: **x100** and **x500**. They're kept until
  used (several can be owned), and the next throw uses the biggest one owned, when the egg lands. The panel at the top
  right shows "NEXT THROW x100" and how many are owned.
  **[Owner, 2026-11-06] The x number is real luck now:** it multiplies that throw's luck in the roll, not just the
  number on screen. (Before, each had a fixed outcome: x100 always the 4th or 5th rarest with Gold, Ruby or Diamond,
  x500 always the map's rarest in a rare colour and size, so the friends' 20 gifted x500s hatched the same monster 20
  times.) Each is rolled like any throw:
  - **x50** (daily reward): 50x luck. **[Owner, 2026-11-13]** Always the map's best normal monster (its 6th), never a
    prize, with a colour or a size: see "Paid luck must beat free luck" below.
  - **x100:** 100x luck. At a map's start mostly its 3rd and 2nd rarest, the rarest about 1 in 10; at its far end the
    two rarest about equally. A colour on a third to a half of them.
  - **x500:** 500x luck. The two rarest about equally, the third now and then, a colour on 70%. About a third land
    GODLY (1 in a million or rarer); IMPOSSIBLE (1 in a billion) only when the rarest gets a rare colour and size at once.
  - **The "1 in X" is never made up:** it's always the catch's normal odds, whatever luck helped. Roblox bans
    misleading purchases and most players are kids, so the shop text says only what's true: "Next throw: 100x luck,
    rare monsters far likelier" and "Next throw: 500x luck, the map's top monsters".
  - **x100:** two Developer Products. "ONE TIME DEAL LUCK x100" (3728190387) at **R$ 3**, so people buy it without a
    thought, offered once per player with a ONE TIME DEAL! sticker; after that "Luck x100" (3728190780) at **R$ 9**.
  - **x500:** "Luck x500" (3728240108) at R$ 39.
  - Prices are set on the Creator Dashboard; the shop reads them from Roblox. Server Luck x2 stays a timed boost for
    the whole server.
- **[Owner, 2026-11-06] Lucky throws are a guaranteed massive hit.** Playing with friends, x500 gave "very weak
  monsters, 1 in 1k+" and x100 was worse: plain luck mostly picked the map's top monsters but with no colour or size,
  and their honest "1 in X" is only about 1 in 2,000. **[Built]** (`Config/Catch` `luckyHits`, `DinoRoll.rollCatch`):
  the monster is still rolled with the throw's luck, then its colour and size are picked among every combination
  that makes the catch at least **1 in 100 million (x500), 1 in a million (x100), 1 in 100,000 (x50)**, each as likely
  as it really is, so results vary (simulated: x500 is IMPOSSIBLE! about 7% of the time). The luck number in flight
  no longer includes the lucky throw's x. Shop text: "Next throw: a guaranteed 1 in 100M+ catch" / "1 in 1M+".
  **[Owner, 2026-11-08] Legendary or better, by the word.** x100 and x500 never give anything below Legendary (the
  words in section 8) and, as before, nothing below a map's 5th place. Maps 1 and 2 top out at Epic, so there the
  throw is a 100% Epic and big sizes are far likelier (`Config/Catch` `shortMapSizeBoost` = 1: every size as likely as
  the others). On map 1: x100 gives each size about 17% (Unit of Doom was 0.1%), x500 gives Mega Chonk or bigger 84%
  of the time. Details shows it per map, because it reads the same `CatchOdds` code.
- **[Owner, 2026-11-13] Paid luck must beat free luck.** The point of the luck system: plain luck is not so lucky
  that nobody buys x100 and x500, and free players don't get too much power. Checked against the roll's own code:
  plain luck is weak as meant (the map's best normal monster comes from the 250-throw guarantee, a prize about once in
  a whole game), but five things worked against the shop. **[Built, not tested in Studio]**
  - **x100 and x500 always give one of the map's two prizes** (its 7th or 8th; `Config/Catch` `luckyHits` `minPlace` 7),
    with a colour and a size as before. From map 6 on a x100 used to pay 5x to 6x the map's best normal monster (160x
    on map 1), less than the next map's free first catch, with a prize 4% of the time. Now, against the map's best
    normal monster: x100 about 16x and x500 about 90x on every map from the 4th on (maps 1 to 3 as before: 160x, 72x,
    50x and 400x, 290x, 180x). Shop text: "one of the map's 2 rarest monsters, 1 in 1M+" / "1 in 100M+".
  - **The daily x50 is always the map's best normal monster** (its 6th: `minPlace` 6, `maxPlace` 6), in a colour or a
    size that makes it 1 in 100,000 or rarer: about 3.5x that monster plain (was about 2x, often a common monster in a
    rare colour). Never a prize: prizes are what Robux buys. Day 7 stays a x500.
  - **Server Luck x2 lasts 20 minutes** (was 3: about 9 throws for R$ 29).
  - **The free x500 comes later, for new players only:** the free x100 stays at 8 minutes of play and the x500 comes
    30 minutes after it, at 38 (was 20: it arrived while a new map was minutes away, on top of the starter run, the big
    shots and the new-world gifts). Saves that had already played keep 8 and 20 (`Config/PlayGifts`
    `luckyThrowsBefore`, save field `playGiftPlan`).
  - The play simulation is unchanged by this: an average free player still reaches map 15 in about 21.7 h.
  - Left as they are, on purpose: Double Luck and Ghost Rush do little, and prizes almost never come from plain throws.
- **[Built] Luck offer, [Owner, 2026-11-06]** (`LuckOfferController`, Figma "Throw Eggs - Shop" Luck offer v2, from the
  owner's recording of the reference): while aiming, and only then, two glowing pills in the top left sell x100 and x500
  (rainbow rim, halo, rays, shine, sparkles, clover bob), with the R$ 3 deal on x100 until it's used. Prices come from
  Roblox. They leave the moment the egg is thrown. Top left is the one corner clear of the meter and Throw Power, and far
  from the throw tap. A player who owns a lucky throw sees a green READY chip instead. Width: 375 HUD pixels, at most 300.
  **DETAILS** shows every chance, normal against lucky, for this player: a perfect throw with their egg and boosts now.
  Lucky chances change with the map and the landing, so they're worked out live by `CatchOdds`, the same code DinoRoll
  rolls with, and never typed in. No throw goes while Details is open. "Next egg", never "this egg": the throw is used at
  landing, but flights can be 1.5 s, shorter than a Robux prompt.
- **[Built] Use x100 and x500 when you want, [Owner, 2026-11-07]** (`LuckyThrows.isPicked`, `LuckOfferController`
  `chosen`, `ThrowService` `lucky`): bought x100s and x500s (and the day 7 x500) are no longer spent on the next throw by
  themselves. On the throw meter an owned pill shows a green **USE n** instead of its price; tapping it picks that luck
  for this throw (gold **ON**, ON THIS THROW! sticker), tapping again un-picks it. Each meter starts with none picked.
  The pick goes to the server with the tap, which checks it's owned; it's used up only when the egg lands, so going
  back to the plot or leaving the game on the platform or mid-flight keeps it (it's in the save). The daily x50 still
  goes on the next throw by itself, unless an x100 or x500 is picked (one per throw); its READY chip sits under the pills.
- **[Built] Pity** (`Config/Hooks`): after 25 throws in a row without one of the map's 3 rarest monsters, the next
  throw is guaranteed one. It says so after the reveal ("LUCKY STREAK!").
- **[Built] Jackpot pity** (`Config/Hooks` jackpotPity, **[Owner, 2026-11-05]**): after 250 throws in a row without the
  map's rarest monster, the next throw is it ("JACKPOT STREAK!"), about 2 hours of play. With the new roll the rarest
  comes on its own about 1 in 250 to 1 in 900 throws on 6-monster maps, so this mostly helps the unlucky.
- **[Built] Starter run** (`Config/Hooks` starterRun, **[Owner, 2026-11-10]** "on their third or fourth throw they
  always get Compy, which makes no sense"; new players need better monsters and that dopamine to stay): a save's first
  10 catches (the tutorial's two included) are never one of the map's 2 commonest monsters, and while a monster above
  them (prizes not counted) is missing from the Index, the catch is one of the missing ones. On the Forest that makes
  throws 3 and 4 the two of Stegosaurus, Velociraptor and Pteranodon the tutorial didn't give, each one NEW; the rest of
  the 10 roll normally from Parasaurolophus up. Hidden like the gift. Tutorial throws, lucky throws and the new-world
  gift keep their own rules.
- **[Built] Big shots** (`Config/Hooks` bigShots, **[Owner, 2026-11-11]**): after the starter boosts, three fixed lucky
  shots so new players feel great. Once a new player reaches map 2 and its new-world gift is caught, their next 3 plain
  throws on map 2 or any later map give, in order, Absolute Unit + Gold, Chonker + Ruby, Mega Chonk + Diamond, each on
  the rarest monster of the map it lands on (never its very rarest) whose $/s with that size and colour stays under 20x
  the map's best normal monster (`incomeCap`, **[Owner, 2026-11-11]**: not always Scorchion, and not so rich it skips a
  map). So the bigger the shot, the commoner the monster: map 2 gives Scorchion, T-Rex, Carnotaurus; map 3 Mossmaw,
  Spinosaurus, Brachiosaurus; from map 3 on mostly Epic or better. Each earns about 14-19x the map's best normal monster,
  about a good catch on the next map. A player
  who throws once on map 2 and moves on keeps the other two for the next maps. A new world's gift or a lucky throw keeps
  its own rules and the shot waits. Only saves started after this was added (`bigShotsLeft`). Hidden, like the gift.
- **[Built] Surprise gift** (`Config/Hooks` surpriseGift, **[Owner, 2026-11-08]**): every 60th throw is a Legendary or a
  Mythic, never Ancient or Secret and nothing below Legendary. A fixed beat, not pity: catching a Legendary on your own
  doesn't move it. No countdown, "they should not see it coming", and nothing tells them it was a gift: no
  pop-up, and the server doesn't even send the reason to the client, so it looks like plain luck. Normal odds pick between the two (about 88% Legendary, 12% Mythic at a world's
  par luck; more Mythic with better eggs and boosts). Works in The Deep End too (its Legendaries and Mythics by their home
  world's rarity). A throw that already has a guarantee (new world, jackpot, a lucky throw, the tutorial) keeps it and
  the gift waits for the next plain throw. The play simulation shows no change to the pace (training gates it).
  **[Owner, 2026-11-08]** The gift goes by the rarity words (section 8) and only counts on maps where Legendary and
  Mythic are high rarities: a Legendary or Mythic in the map's rarer half (5th place or rarer, `minPlace`). That's maps
  3 to 11 and The Deep End. Throws on maps 1-2 (no Legendary) and 12-15 (there Legendary and Mythic are the commonest)
  don't count towards the 60. A lucky throw (x50, x100, x500) on the 60th keeps its own odds and the gift waits for the
  next plain throw. On maps 3 and 4 the only Legendaries are the map's prizes, so there the gift is one of the map's two
  Epics instead (`prizeOnlyRarity`, **[Owner, 2026-11-08]** "for the 3 and 4 only give an epic from those 2"): Swamp
  Spinosaurus 80% / Mossmaw 20%, Volcano Obsidian Rex 88% / Volcano King 12%. From map 6 on it's mostly the 5th
  (1 in 400). The play simulation shows no change to the pace.
- **[Built] New-map gift:** the first egg that lands in a map you've never caught anything in hatches one of its 3
  rarest ("NEW WORLD BONUS!").
- **[Built] So close:** landing within 60 studs of the next map shows "SO CLOSE! 23 studs short of Swamp".
- **[Built] Daily reward with a streak** (`Config/Daily`, `DailyService`, `DailyController`): **[Owner]** days 1 to 6
  give a **x50 lucky throw** and day 7 a **x500 lucky throw** ("seems absurd but trust me"), kept until used like
  the bought ones. One claim per UTC day. **[Owner, 2026-11-07]** A missed day only pauses the streak, and after day 7 it
  goes back to day 1. The panel opens by itself 3 seconds after joining when a claim is waiting, and a 🎁 Daily button above
  Monsters opens it any time, with a red dot while a claim waits.
- **[Built, 2026-11-07] Daily tasks** (`Config/Daily` `tasks`, `DailyTasks`, shown in the Daily panel): hit 5 PERFECTs, tap 25 x2
  bubbles, catch 10 monsters. They start again each UTC day, and finishing all three gives x2 XP for 15 minutes, once a day, the
  same timed boost as completing a world in the Index. **[Owner]** No lasting rewards.
- The "1 in X" shown on a catch stays the normal odds, even when a boost or a guarantee helped.

## 9. Worlds

**[Owner]** The plan for building them:

1. Make the **first world only**, in a layout very similar to the original.
2. Polish it until it's beautiful.
3. Design each other world **from that first layout**, changing its look.
4. **Join them all together**, one after another. That is how all the worlds get made.

**[Owner]** Modelled in Blender, stud texture applied in Roblox Studio.

**[Owner]** World names (chosen 2026-11-04: simple first, more serious further on): Forest, Desert, Swamp, Volcano,
Frozen Peaks, Shadow Bog, The Abyss, Starfall Crater. Code ids, files and Studio folders use the same names (Forest,
Desert, Swamp, Volcano, FrozenPeaks, ShadowBog, Abyss, StarfallCrater); no save stores a world id.
**[Built]** Map 9 is **Eclipse Temple** (`EclipseTemple`), a name we picked for the first of the mysterious, dark
maps; the owner can rename it (only `name` in `Config/Biomes` changes).
**[Built]** Map 10 is **Forbidden Library** (`ForbiddenLibrary`), our name too; the owner can rename it.
**[Built]** Map 11 is **Midnight Carnival** (`MidnightCarnival`), our name too, built before map 10.
**[Built]** Map 12 is **Clockwork Citadel** (`ClockworkCitadel`), our name too; the owner can rename it.
**[Built]** Map 13 is **Thorn Kingdom** (`ThornKingdom`), our name too; the owner can rename it.
**[Built]** Map 14 is **Spore Hollow** (`SporeHollow`), our name too; the owner can rename it.
**[Owner, 2026-11-13]** Map 16 is **Shattered Mirror** (`ShatteredMirror`): the owner picked the theme from three of ours.

**[Owner, 2026-11-04]** Luck reaches the billions, about 4-5x more per map (section 8b). **Replaced 2026-11-06:** the
luck shown now tops out at 50x (section 8b); the table below is the old plan:

| # | World | Luck at its end |
|---|---|---|
| 1 | Forest | 5x |
| 2 | Desert | 25x |
| 3 | Swamp | 100x |
| 4 | Volcano | 500x |
| 5 | Frozen Peaks | 2.5K |
| 6 | Shadow Bog | 10K |
| 7 | The Abyss | 50K |
| 8 | Starfall Crater | 250K |
| 9 | Eclipse Temple | 1M |
| 10 | Forbidden Library | 5M |
| 11 | Midnight Carnival | 25M |
| 12 | Clockwork Citadel | 100M |
| 13 | Thorn Kingdom | 500M |
| 14 | Spore Hollow | 2.5B |
| 15 | The Weeping Dark | 10B |

**[Seen]** Far worlds change colour and props completely: sand with cactus and skulls, dark rock with lava and
black spires, neon purple with crystals. The reference's thumbnail shows worlds stepping **down** one after another (see section 15).

**[Seen]** Worlds keep the same basic corridor with different colours, props and sky, which fits the owner's plan
exactly. Worlds pass in under a second each at high power, so they're read from a distance:
big shapes and strong colours matter more than detail. The sky, fog and light change per world too, from bright blue
to dark green. Props are themed and include things overhead, such as power lines and bridges across the valley.

The reference's worlds, in order, for scale only (ours keep their own names): Forest, Savanna, Desert, Jungle, Ocean,
Mountains, Taiga, Winter, Deep Waters, Ancient Ruins, Mythical Paradise, Shadow Realm, Harvest Fields, Phantom Harbor,
Nuclear Wasteland, which the owner says is the last map. I read these from frames half a second apart, so one or two could be missing.

**The first world's corridor [Seen]:** bright green checkered floor, tall brown checkered walls on both sides, chunky
grass hanging over the wall tops, open blue sky, and raised grass with trees on the rim above.

### World build tasks

Done one at a time, each in its own step:

1. **Layout blockout in Blender**: sizes and positions only, checked against the reference. *(Done, approved by the owner.)*
2. **Real models in Blender**: the 6 animals and 9 props are made and waiting for the owner's OK (`assets/models/build_forest.py`).
   Dino animations are in the same file. Floor, walls with hanging grass and rim, and platform are in `build_world_kit.py`. Colour comes from each part's Color, with see-through stud images on top
   (`assets/textures/`, applied in Studio as a SurfaceAppearance with AlphaMode Overlay), so one image suits every world. The arena pieces
   (floor and its four walls) are in the same file, under one model, `kit_Arena`.
3. **Into Roblox Studio**: import, apply the stud texture and two-tone checker, sky and lighting. Replace the current
   ground, and move the lane and arena numbers in `Config`, so throwing still works. *(Done 2026-11-03, sky and lighting
   still to do: the arena is `kit_Arena` from `build_world_kit.py`, placed with the corridor by `MapService`, sizes in
   `Config/Map`.)*
4. **Bases**: 5 small bases in the row, each with its rack, XP pad, sign and owner plate, plus a shop only the owner sees.
   Capacity 10 to 20. *(Done 2026-11-03. The rack, XP button, stall, fence and upgrade sign are Blender models,
   `assets/models/build_base_kit.py`, kept in `Assets.Maps.Forest.Base` and placed through `BaseKit`. The owner plate
   and the sign's face follow the mock-ups 13b and 14 in `design/ui-mockups/build.py`. All fences are wood and every base
   has a rack until questions 1 to 3 in section 15 are answered.)*
5. **Forest props and decoration**: our own trees, ferns, rocks and rim decoration, in Blender. *(Placed
   2026-11-03: the 9 props from `build_forest.py` stand along the corridor floor (kept off the middle), as big
   trees on its rims, as eggs along the arena's rim and as small things behind the bases. `MapDecor` places them
   from `Config/Decor`, the corridor's with a fixed seed so every server matches. Props are scaled up to suit the
   walls, which makes their studs a little bigger than the walls' studs.)*
6. **Huge animals**: each map's standard size grows a little (to 2x at map 15), and size mutations scale up from that
   standard, up to 100x, until late-game monsters look absurd on those bases (section 8). *(Done 2026-11-03: the six
   size mutations and per-map standard size are in, on the base, in the hand-placement preview and in the reveal. The
   carried copy stays small.)*
7. **Polish**: lighting, sky, small effects, and a check on phone speed. *(Done 2026-11-03: `Config/Lighting`, applied by
   `LightingService` when the server starts: bright, saturated light with soft shadows, matte studs, a thin sky-blue
   atmosphere instead of grey haze, and no depth-of-field blur on the corridor. `SkyController` drifts 18 chunky block
   clouds round the island on each player's screen only. Phone check: about 1,100 parts in play, which is light, and the
   clouds are solid because see-through parts cost phones the most. Per-world sky and light come with step 8.)*
8. **Then the other worlds**: each one copies the first world's pieces with its own look, and they get joined up.
   One world at a time:
   - **Desert** *(done 2026-11-03, in Studio under `Assets.Maps.Desert.Props` and `Assets.Dinos`)*: 9 props in `build_desert.py` (saguaro,
     barrel cactus, tumbleweed, a giant skull, a rib cage, a red mesa, a dead tree, dry grass, a boulder), placed by
     `Config/Decor` like Forest's, sparser, with mesas, giant cacti and bones on the rims. Its animals are now
     built at the first map's size like every map's, since the game makes them 1.4x (they were made 1.4x in Blender
     too, which doubled up). Bonkhead's model is now `dino_Pachy`, the game's id.
   - **Per-world light** *(built)*: `Config/Lighting` `worlds` gives each world its own light, haze and tint, golden
     for Desert and murky green for the Swamp. `SkyController` blends to it in 0.6 s while the camera is over that
     world, so it covers the flight, the landing and the reveal, and back in the arena it returns to Forest's.
   - **Swamp** *(props made 2026-11-03, organised into `Assets.Maps.Swamp.Props` the same evening: they had been left in Workspace)*:
     10 props in `build_swamp.py` (a bald cypress on stilt roots with hanging moss, a weeping willow, lily pads with a
     pink flower, cattails, a mossy log, giant purple and teal toadstools, a bubbling bog pool, a hut on stilts, a
     lantern post, and a fallen giant tree lying across the corridor from rim to rim with vines hanging under it).
     `Config/Decor` places them like Desert' props, plus a new `overhead` list for the fallen tree. The corridor floor is now a
     murky blue-green (`Config/Map`) so it doesn't blend into the rims' grass. Renders, including a stretch of
     corridor, are in `design/world/models_swamp/`. Its 6 monsters (made 2026-11-04, `build_swamp_monsters.py`, renders and
     `swamp_animation_preview.mp4` in `design/world/monsters_swamp/`): Soggy Dimetrodon (a drenched, flopped sail and a
     lily pad on its head), Burpasaurus (mid-burp, frill flared), Baryonyx (with a fish), Sir Chomps-a-Lot (a croc with a
     monocle and a gold tooth), Neckzilla (an angry swamp sauropod with reeds growing on its back) and Spinosaurus (the
     boss, a red sail). The first maps' face, the Volcano's jaw bone and roar. Ids stay the old stand-ins' (Bary, Dilo,
     Sarco, Brachio, Spino) plus Dimetro, so owned monsters get the new models. Imported and play-tested 2026-11-04.
   - **Volcano** *(made 2026-11-03; imported and organised in `Assets.Dinos` and `Assets.Maps.Volcano.Props`; play-tested: props placed, monsters walk, snap and roar on a base)*: the 6 monsters, animated,
     and 11 props in `build_volcano.py`: a smoking volcano with lava running down it (on the rims), obsidian
     spires, lava pools, charred trees with embers, steam vents, basalt columns, glowing lava rocks, fire flowers, flat
     cracks of lava across the floor (they can lie in the middle, where eggs land), lava falls pouring down the corridor
     walls and a rock arch over the corridor with lava running along it. `Config/Decor` places them, with two new lists:
     `walls` (on a wall's top edge, facing the middle) and `spots` (set pieces at fixed places, on the rim or the floor).
     Props that must face a certain way carry a small `Front` part that `MapDecor` uses to turn them, then removes. Dark
     rock floor, scorched red rims (`Config/Map`), orange haze (`Config/Lighting`). Glowing parts (lava, embers, fire,
     the monsters' eyes and mouths) get the Neon material in the game (`shared/Roles.luau`). Renders, a corridor stretch
     and `volcano_animation_preview.mp4` are in `design/world/models_volcano/`. Built before the Swamp's animals, at the
     owner's request; it's the world after the Swamp (1,500 to 2,200 studs, 14x luck, 2.7x size).
   - **Frozen Peaks** *(map made, imported and play-tested 2026-11-03, in `Assets.Maps.FrozenPeaks.Props`; monsters later, at the owner's request)*:
     12 props in `build_frozen_peaks.py`: snowy pines (the signature tree), ice crystal spikes, a glacier and giant
     mammoth tusks arching out of the snow (landmarks on the rims), an igloo with a warm lit doorway, a campfire with log
     benches, frosted bushes with red berries, snowy boulders, snow drifts, flat frozen ponds across the floor, frozen
     waterfalls down the walls and an ice arch over the corridor. Packed-snow floor, frozen blue walls, white rims
     (`Config/Map`), crisp pale blue haze (`Config/Lighting`), placed by `Config/Decor`. Renders in
     `design/world/models_frozen_peaks/`. **Until a world has monsters, eggs can't land in it** (`Throw.maxDistance`): it's
     built and decorated and seen ahead during long throws, has no Index card and can't be completed. Its 6 monsters
     (made 2026-11-04, `build_frozen_peaks_monsters.py`, renders and `frozen_peaks_animation_preview.mp4` in
     `design/world/monsters_frozen_peaks/`): Brain Freeze (ice cream splatted on its head), Woolly Rhino (fur over its eyes),
     Chilly Mammoth (hat, scarf, an icicle off its trunk), then the frost face on the fierce ones, eyes glowing icy blue:
     Sabertooth, Frost Raptor (glowing ice crystals) and Blizzard Rex (the boss: shaggy white, ice armour and crown,
     frost breath). Glowing crystals are the `IceGlow` role (Neon). With them in `Config/Dinos`, throws reach Frozen Peaks. Imported and play-tested 2026-11-04.
   - **Shadow Bog** *(map made, imported into `Assets.Maps.ShadowBog.Props` and play-tested 2026-11-04: 152 props placed; monsters made 2026-11-04, imported and organised in `Assets.Dinos` the same day)*:
     a tar pit at dusk, slate violet and black so it doesn't read as the Swamp's green or the Volcano's orange.
     12 props in `build_shadow_bog.py`: crooked black gloom trees with beards of moss and glowing pods (the
     signature tree), thorn bushes, leaning slate shards, mounds of bubbling tar, dead reeds, a snapping bog plant,
     will-o'-wisps with sleepy faces, a hollow stump with two eyes glaring out of it, the skeleton of a huge
     long-necked monster sinking in the tar (the landmark on the rims), flat tar pits across the floor, tar oozing
     down the walls with a skull stuck in it, and an arch of braided roots over the corridor. Slate violet floor, dark
     plum walls, deep teal moss on the rims (`Config/Map`), violet dusk haze (`Config/Lighting`), placed by
     `Config/Decor`. Glowing parts are `Glow` and `Wisp` (Neon). Renders in `design/world/models_shadow_bog/`.
     It's world 6 (3,000 to 3,900 studs, 27x luck, 5.2x size).
     **[Owner]** Its monsters: a step more aggressive and interesting than the Frozen Peaks', weird in a good way, and
     they don't have to make sense as animals. **[Built]** The 6 (`build_shadow_bog_monsters.py`, renders and
     `shadow_bog_animation_preview.mp4` in `design/world/monsters_shadow_bog/`) all get the bog face: glowing magenta
     eyes with a slit pupil, never just a plain pair (spare eyes crowd round, or one is far too big), and a maw glowing
     violet inside, crammed with crooked bone-white teeth, with tar dripping off the jaw. Even the common ones are
     hostile: Sticky Steve (a dollop of tar with a grin too wide for it, one huge eye and one tiny one, arms up to
     grab, a bone stuck through its head), Slow Bob (a slug wearing a horned skull as its shell, a lamprey mouth and
     three eye stalks), Terror Bird (plucked and black, a hooked beak full of teeth, five eyes, skeleton wings), then
     Pitch Raptor (its face splits four ways, with a pincer each side of its jaws; six spider eyes, mantis scythes, a
     bone tail blade), Tar Titan (no neck, its whole front one mouth of gravestone teeth, seven eyes, ribs bursting
     out of its back round a trapped wisp) and Bog Rex (the boss: three heads, a bare skull with a third eye in the
     middle and a cyclops and a three-eyed head on necks from its shoulders, an open rib cage with a wisp inside,
     a crown of roots hung with glowing pods). Extra parts ride the Wing bones, which roll as they walk: Slow Bob's
     eye stalks, Pitch Raptor's pincers, Terror Bird's wings and Bog Rex's side heads. With them in `Config/Dinos`,
     throws reach Shadow Bog.
   - **The Abyss** *(map made, imported into `Assets.Maps.Abyss.Props` and play-tested 2026-11-04: 232 props placed; monsters imported into `Assets.Dinos` and play-tested the same day: they hover and swim head first on a base)*:
     the bottom of the ocean, and on the owner's request the most decorated world so far (18 props, placed denser than
     the others). Deep blue sand, dark abyssal walls and sea-green reef flats on the rims (`Config/Map`), a dim blue
     underwater haze (`Config/Lighting`). In `build_abyss.py`: branching coral (the signature), brain coral, tube
     sponges, tall golden kelp, anemones with glowing tips, a giant clam with a glowing pearl, tube worms, urchins and
     starfish, sea grass, jellyfish drifting high over the floor, hydrothermal vents with glowing cracks and smoke,
     a rusty anchor, an open treasure chest; set pieces: sunken shipwrecks and giant ammonite shells on the rims, reefs
     tumbling down the walls (`walls`), three coral arches over the corridor (`overhead`) and flat shell patches across
     the floor. Glowing parts are `Glow` (cyan), `Shine` (pink) and `Ember` (Neon). Renders in
     `design/world/models_abyss/`. World 7 (3,900 to 4,900 studs, 35x luck, 7.2x size). Its 6 monsters (made 2026-11-04,
     `build_abyss_monsters.py`, renders and `abyss_animation_preview.mp4` in `design/world/monsters_abyss/`), all very
     aggressive at the owner's request, with the abyss face (glowing cyan eyes under a heavy brow, a crimson mouth gaping
     open, glowing spots down the flanks): Spiral Gary (a spiked ammonite with a hooked beak and eight tentacles),
     Derpichthys (an anglerfish all underbite and needle fangs, with a pink lure), Dunkleosteus (an armoured helmet with
     glowing seams and blade jaws), Plesiosaur (rearing to strike, needle teeth splayed), Megalodon (two rows of teeth,
     claw scars, a harpoon in its back) and Mosasaurus (the boss: croc jaws with two rows of teeth, a horn crown and a
     crest of glowing spines). They **swim**: a Swim bone tells `DinoLifeController` to play the swim and hover moves
     instead of the walk (tail beats, fins and flippers, pulsing tentacles, a bobbing lure), with an attack once per
     idle loop (they rear up and lunge, jaw wide, shaking their head and thrashing their tail); they float just above
     the ground, so they hover over the base (`Config/DinoLife` `swim`). With them in `Config/Dinos`, throws reach The Abyss.
   - **Monsters walk head first** *(fixed 2026-11-04)*: 30 of the 36 imported monsters face their pivot's +Z (the importer
     turns them round), so they walked backwards and their jaws and roars bent the wrong way. `DinoLifeController` now
     tells which way each one faces from its head and tail bones.
   - **Starfall Crater** *(map made, imported into `Assets.Maps.StarfallCrater.Props` and play-tested 2026-11-04: 202 props placed, and the moving parts move; monsters later, at the owner's request)*:
     **[Owner]** the last world, nicer and more decorative than the maps before, with objects that move where it makes
     sense. **[Built]** Where the stars came down: a crater field at night. Midnight-blue crater rock, deep navy walls,
     pale moon dust on the rims (`Config/Map`), and the sky turns to night over it, stars and all (`Config/Lighting`
     sets ClockTime 0 with a thin blue haze, so the glow pops). 16 props in `build_starfall_crater.py`: crystal clusters
     (the signature) with a shard floating and turning over them and motes of light circling, alien star-flowers whose
     gold star turns, moon rocks with craters, a skidded meteorite glowing through its cracks, glowing tufts, a crashed
     probe whose dish still turns and whose light still blinks; floating rocks bobbing over a glowing crater and star
     lamps on the rims; landmarks: a fallen star plunged point first into its crater (its heart pulsing, sparkles
     circling), crystal spires with a gold halo turning round them, little observatories whose domes turn; ringed
     planets (turning, moons going round) and comets (gliding head first across the sky, fading out and back) beyond
     the rims; stardust pouring down the walls with sparkles falling for ever (`walls`), two crystal arches with a
     turning gyroscope (`overhead`), and flat star-scorched craters across the floor. **What moves**: each moving piece
     is its own colour role, and `PropMotionController` moves it on each player's screen only, within 700 studs of the
     camera (spin, bob, pulse, fall and drift, numbers in `Config/PropMotion`, the same as `MOTION` in the Blender
     script). Renders and two videos (`starfall_flight.mp4` down the corridor, `starfall_motion.mp4` close up) in
     `design/world/models_starfall_crater/`. World 8 (4,900 to 6,000 studs, 45x luck, 10x size); eggs can't land in it
     until it has monsters. The wall at the corridor's far end takes the last world's colour.
   - **Eclipse Temple** *(map and monsters made 2026-11-04, imported into `Assets.Maps.EclipseTemple.Props` and `Assets.Dinos` and play-tested the same day: 256 props placed; its own light not yet seen in play)*: **[Owner]** a very nice
     map 9, made in Blender with animated props; maps 9 to 15 mysterious and dark. **[Built]** A lost temple city
     swallowed by the jungle, frozen under a total eclipse: red laterite floor, dark carved plum walls with jungle
     hanging over them, jungle-green rims (`Config/Map`), and the night before dawn behind a thick jade mist
     (`Config/Lighting`, ClockTime 5.6, kept under 6 so the blend from Starfall doesn't flash through daylight). Its
     own light is glowing jade, with gold lantern light. 17 props in `build_eclipse_temple.py`, 16 of them with moving
     parts: guardian heads half sunk in the floor with glowing eyes (the signature), jungle trees and fronds with
     glowing pods, temple ruins, stone posts with a lantern swinging on its hook, spirit braziers burning jade fire
     with sparks rising, flowers with one big eye that looks from side to side, giant stone hands holding up a
     floating orb, a rare bronze orrery with three rings turning round an orb; on the rims floating monoliths
     circling, sky lanterns drifting round a shrine; landmarks: stepped temples with glyph-crystals circling a
     floating orb, guardian statues whose heads slowly turn to watch the eggs go by, black eclipsed suns in the sky
     with their corona turning; carved faces in the walls pouring glowing spirit water into the corridor (`walls`),
     temple gates with four-faced pillars and a bell and lanterns swinging under the lintel (`overhead`), and flat
     rune circles whose rings turn opposite ways across the floor. Placed by `Config/Decor`; statues, temples and
     eclipses turn to the corridor with a new `face` option on spots. It added a **swing** move and turning round
     a sideways axis to `PropMotionController` (`Config/PropMotion`). Renders and two videos (`eclipse_motion.mp4`
     close up, `eclipse_flight.mp4` at the flight camera's height) in `design/world/models_eclipse_temple/`.
     World 9 (6,000 to 7,200 studs, 1M luck, 1.49x size). The recipe it was made with, for every map after it, is
     `docs/MAP_RECIPE.md`. Its 6 monsters (section 8a) are in `build_eclipse_temple_monsters.py`, with renders and
     `eclipse_temple_animation_preview.mp4` in `design/world/monsters_eclipse_temple/` and FBX files in
     `fbx/09_EclipseTemple/Animals/`. They're in `Config/Dinos` (chances 2, 4, 12, 60, 400, 3000; income 100x
     Starfall's: 1e16 to 5e18), so throws reach Eclipse Temple.
   - **Forbidden Library** *(map 10's world made 2026-11-04, in Blender; FBX files ready in `fbx/10_ForbiddenLibrary/Props/`, not imported yet; monsters later)*:
     **[Owner]** a nice map 10, made in Blender, with no stud texture in the Blender files (plain colours, studs only
     from Studio's "Studs" material); maps 10 to 15 mysterious and dark. **[Built]** A library so old it became a world
     of its own, locked up for ever because its books are alive. A deep violet carpet on the floor, dark walnut walls
     like the backs of bookcases, parchment on the rims hanging over the walls like loose pages (`Config/Map`), night
     behind a dusty indigo haze (`Config/Lighting`, ClockTime 2, between its neighbours' 5.6 and 0). Its own light is
     warm candlelight and the violet glow of living ink. 19 props in `build_forbidden_library.py`, all with moving
     parts: open tomes on carved lecterns (the signature) with a page turning back and forth by itself, letters of
     light rising out of them and a sigil floating and turning over them; towers of books with a candle on top;
     double-sided bookcases with a library ladder and two eyes blinking in the dark between the books; candelabras
     and candles floating in the air, bobbing; inkwells whose quill nods as if it writes; hourglasses of glowing sand
     with grains falling through the neck; now and then a mimic book chomping its cover, fangs along its pages and a
     ribbon for a tongue; scroll piles as filler; on the rims page trees (pages for leaves, little books perched like
     birds, glowing moths circling), stacked bookcases dropping pages for ever, and forbidden tomes chained to their
     pedestals, rattling; landmarks: clock towers whose minute hand runs backwards over a pendulum swinging in front of
     a lit window, giant pop-up books with a paper castle, paper bats circling and a paper moon rocking on a stick,
     spiral stairs climbing to a glowing door to nowhere with books circling them, and huge books flapping their covers
     like wings in the sky; giant inkwells tipped over the wall tops pouring glowing ink down into the corridor
     (`walls`), book arches over the corridor with a chandelier swinging under the crown (`overhead`), and flat spell
     pages across the floor. The magic circles use a four-pointed star and plain runes, never a five- or six-pointed
     star or a cross, which read as religious or occult symbols. Renders and two videos (`library_motion.mp4`,
     `library_flight.mp4`) in `design/world/models_forbidden_library/`. World 10 (7,200 to 8,500 studs, 5M luck,
     1.56x size); `Config/Biomes`, `Map`, `Lighting`, `Decor`, `PropMotion`, `Roles` and the Index card colours are in.
   - **Midnight Carnival** *(map 11's world made 2026-11-04, in Blender; FBX files ready in `fbx/11_MidnightCarnival/Props/`, not imported yet; monsters later)*:
     **[Owner]** a very nice map 11, made in Blender; maps 10 to 15 mysterious and dark. **[Built]** A travelling fair
     that set up at midnight and never left: nobody runs it, yet every ride still turns and every bulb still burns.
     Deep teal midway floor, crimson walls like a big top's curtain with gold fringe hanging over them, gold straw on
     the rims (`Config/Map`), midnight with stars behind a thin plum haze (`Config/Lighting`, ClockTime 0). Its own
     light is warm carnival bulbs, a little pink neon, and the pale glow of ghosts riding the rides. 19 props in
     `build_midnight_carnival.py`, 18 with moving parts: striped tents with a waving pennant and a glowing door (the
     signature), jack-in-the-boxes whose clown bobs and wobbles on its spring while the crank turns, popcorn carts
     popping for ever, a fortune teller whose head turns over a glowing crystal ball, strength testers whose puck rings
     the bell, balloon carts whose balloons sway (one grins), lamp posts with a swinging sign and a crow that looks
     round, now and then a carousel with horses rising and falling in turn, crates as filler; on the rims swing rides
     with ghosts in the chairs, purple-and-gold hot-air balloons swaying on their ropes and teal helter-skelters;
     landmarks: Ferris wheels turning, big tops whose searchlights sweep the sky, clown-faced fun houses with spiral
     eyes turning and a pulsing red nose, and sleeping crescent moons hung in the sky on a rope like a stage prop,
     swaying with stars on strings; giant popcorn boxes tipped over the wall tops pouring popcorn down into the
     corridor (`walls`), roller-coaster loops over the corridor with two cars of ghost riders going round (`overhead`),
     and flat circus rings with chasing bulbs across the floor. Renders and two videos (`carnival_motion.mp4`,
     `carnival_flight.mp4`) in `design/world/models_midnight_carnival/`. Planned as world 11 (8,500 to 9,900 studs,
     25M luck, 1.64x size); `Config/Map`, `Lighting`, `Decor`, `PropMotion`, `Roles` and the Index card colours are
     in, and since map 10 exists it's in `Config/Biomes` too (added 2026-11-04 with Forbidden Library).
   - **Clockwork Citadel** *(map 12's world made 2026-11-05, in Blender; imported into `Assets.Maps.ClockworkCitadel.Props` and play-tested the same day: 332 props placed, no console errors; monsters later)*:
     **[Owner]** map 12, nice, made in Blender, with animated objects, no animals yet; maps 12 to 15 mysterious and
     dark. **[Built]** A citadel that is one enormous machine, so old its gears grew as big as houses. Whoever built it
     is long gone, but it never stopped: it winds itself in the dark, every gear turning, pistons pounding, steam
     hissing and blue lightning crackling, as if it's still building something nobody has seen. A floor of bronze
     plates, soot-black iron walls, copper on the rims hanging over the walls like old copper roofing (`Config/Map`),
     and the night before dawn behind a thick steel-blue smog (`Config/Lighting`, ClockTime 4). Its own light is
     electric blue and furnace orange. 19 props in `build_clockwork_citadel.py`, all with moving parts: gear works (the
     signature), a big brass gear meshing with a small iron one that turns the other way twice as fast, steam puffing
     beside them; steam hammers pounding a glowing ingot while a flywheel spins; boilers with a glowing furnace door,
     a smoking chimney and a twitching gauge needle; bundles of copper pipes with turning valve wheels; giant
     metronomes ticking; music boxes whose drum and key turn while a brass bird goes round on top; spark coils with
     lightning flickering out of a blue orb and a ring of sparks racing round it; now and then a giant pocket watch
     lying open, its hands going round; scrap piles as filler; on the rims smokestacks rolling out smoke, brass trees
     crowned with a turning gear, and wind-pump fan towers; landmarks: cog spires ringed with four gears turning
     opposite ways under a crackling orb, lightning towers arcing down to three little coils, and brick engine houses
     with a huge flywheel turning and a governor whirling on the roof; airships hanging in the smog beyond the island,
     bobbing, their propellers turning; crucibles tipped over the wall tops pouring glowing molten brass down into
     the corridor (`walls`), iron arches over the corridor with three gears turning and a lamp swinging (`overhead`),
     and flat floor plates with two gears meshing in them across the middle. Meshing gears have even teeth and turn
     at the inverse ratio of their teeth, so they stay in mesh in the game too (spins have no phase). Plain colours in
     Blender (no stud image), like map 10. Renders and two videos (`clockwork_motion.mp4`, `clockwork_flight.mp4`) in
     `design/world/models_clockwork_citadel/`. World 12 (9,900 to 11,400 studs, 100M luck, 1.72x size);
     `Config/Biomes`, `Map`, `Lighting`, `Decor`, `PropMotion`, `Roles` and the Index card colours are in. Eggs can't
     land in it until it has monsters. Its 6 monsters (section 8a) are made (2026-11-05,
     `build_clockwork_citadel_monsters.py`, FBX in `fbx/12_ClockworkCitadel/Animals/`), imported and in `Config/Dinos`
     (chances 2, 4, 12, 60, 400, 3000; income 100x Midnight Carnival's: 1e22 to 5e24), so throws reach it (11,400).
   - **Thorn Kingdom** *(map 13's world made 2026-11-05, in Blender; imported into `Assets.Maps.ThornKingdom.Props` and play-tested the same day: 339 props placed, no console errors; its monsters built, imported and play-tested the same day)*:
     **[Owner]** map 13, made in Blender like the maps before it, only the world for now; maps 13 to 15 mysterious and
     dark. **[Built]** A fairy-tale kingdom put to sleep by a curse a thousand years ago and swallowed by briars as big
     as trees; only the roses are still alive, glowing crimson in the dark, and the fireflies keep watch. A floor of
     dark moss, black-violet thorn-bark walls, silvery moss on the rims hanging over the walls (`Config/Map`), and night
     under a pale silver-mauve mist (`Config/Lighting`, ClockTime 3). Its own light is crimson rose-glow and the warm
     gold of fireflies and lit windows; its crimson glow is a first. 19 props in `build_thorn_kingdom.py`, all with
     moving parts: briar roses (the signature), a giant rose on a thorny stem, its heart glowing and petals falling off
     it for ever; thorn thickets with fireflies; kneeling stone knights with a glowing visor holding out a swinging
     lantern; spinning wheels still turning, glowing gold thread on the spindle; briar-strangled lamp posts with a
     lantern swinging; fairy rings of glowing toadstools; enchanted fountains dripping glowing water; now and then a
     magic mirror whose eyes open and close or the kingdom's crown floating and turning over its cushion; briar tufts
     as filler; on the rims black thorn trees dropping glowing petals and turrets with a banner waving; landmarks:
     sleeping castles with banners and lit windows, rose towers crowned by a colossal glowing rose with petals circling
     it, and crooked cottages smoking with a weather vane turning; a huge moon wound with briars hangs beyond the
     island, ravens circling it; briars spill over the wall tops dropping glowing petals down into the corridor
     (`walls`), stone bridges span it with banners swinging along it (`overhead`), and fallen rose windows of glowing
     glass lie flat across the floor. No five- or six-pointed stars or crosses (the rose windows are twelve petals).
     Plain colours in Blender (no stud image). Renders and two videos (`thorn_motion.mp4`, `thorn_flight.mp4`) in
     `design/world/models_thorn_kingdom/`. World 13 (11,400 to 13,000 studs, 500M luck, 1.81x size); `Config/Biomes`,
     `Map`, `Lighting`, `Decor`, `PropMotion`, `Roles` and the Index card colours are in. Its 6 monsters (section 8a)
     are made (2026-11-05, `build_thorn_kingdom_monsters.py`, FBX in `fbx/13_ThornKingdom/Animals/`), imported and in
     `Config/Dinos` (chances 2, 4, 12, 60, 400, 3000; income 100x Clockwork Citadel's: 1e24 to 5e26), so throws reach it
     (13,000).
   - **Spore Hollow** *(map 14's world made 2026-11-05, in Blender; imported into `Assets.Maps.SporeHollow.Props` and play-tested the same day: 524 props placed; its monsters built, imported and play-tested the same day)*:
     **[Owner]** map 14, made in Blender like the maps before it, nice, with animated objects, no animals yet; maps 12 to
     15 mysterious and dark. **[Built]** A hollow at the bottom of the world where no sun ever reached, so the fungus grew
     as big as castles instead. It makes its own light: chartreuse from under every cap, spores sifting down from the
     gills and puffing up out of puffballs, moths circling the brightest caps, and a few windows lit warm amber where
     somebody small moved into a mushroom. A floor of dark umber loam, peat walls, pale cream mycelium on the rims hanging
     over the walls like felt (`Config/Map`), and night under a hazy olive-gold spore mist (`Config/Lighting`, ClockTime
     2). Its chartreuse glow is a first; lilac wavecap bells are its one cool light. 18 props in `build_spore_hollow.py`,
     all with moving parts: glowcaps (the signature), a giant rust-red mushroom on a ringed stalk, glowing specks on its
     cap, its gills glowing and spores sifting down from them for ever; puffball clusters puffing spore clouds with
     glowing spores in them; lamp mushrooms, a stalk curling over like a lamp post with a glowing bulb swinging from its
     tip and moths round it; wavecaps, three tall stalks with lilac bells each swaying its own way; rotten stumps stepped
     with glowing shelf fungi; orange coral fungus with glowing tips; now and then a mushroom hut (a door, lit windows, a
     chimney smoking, a lantern swinging, its roof a chocolate cap freckled with glowing specks) or the mycelium heart, a
     ribbed aubergine bulb beating in the ground with glowing veins running out from it; spore tufts as filler; on the
     rims parasol mushrooms with glowing gills, spores falling and moths circling, and morel spires glowing amber through
     their honeycomb with spores rising off their tips; landmarks: elder shrooms (a colossal mushroom with a door, lit
     windows and a stair of shelf fungi winding up its stalk), shroom towers (three caps stacked into a house, lanterns
     swinging under the two lower ones, smoke at the top) and spore geysers (a crater blowing a column of spore clouds
     into the mist); giant spores drift across the sky beyond the island trailing threads of glowing beads (drift);
     mycelium cords twist down the walls with shelf fungi dripping glowing drops into a pool (`walls`); two giant
     mushrooms lean in from both rims until their caps almost touch over the middle, glowing bulbs swinging under them
     (`overhead`); and glowing mycelium webs lie flat across the floor. Plain colours in Blender (no stud image). Renders
     and two videos (`spore_motion.mp4`, `spore_flight.mp4`) in `design/world/models_spore_hollow/`, FBX in
     `fbx/14_SporeHollow/Props/`. World 14 (13,000 to 14,700 studs, 2.5B luck, 1.9x size); `Config/Biomes`, `Map`,
     `Lighting`, `Decor`, `PropMotion`, `Roles` and the Index card colours are in. Its 6 monsters (section 8a) are made
     (2026-11-05, `build_spore_hollow_monsters.py`, FBX in `fbx/14_SporeHollow/Animals/`), imported and in `Config/Dinos`,
     so throws reach it (14,700).
   - **The Weeping Dark** *(map 15's world made 2026-11-05, in Blender; imported into `Assets.Maps.WeepingDark.Props` and play-tested the same day: 447 props placed, 210 real lights; its monsters built and imported the same day, not catchable yet)*:
     **[Owner]** the 15th map, made in Blender with animated objects, "special", "very dark and sad", "the darkest and
     scariest map", nothing from any earlier map's idea, and only the map, not the monsters. Theme and name are ours.
     **[Built]** The end of the corridor. There was a town here and a sun; the sun went out, everybody walked into the
     dark to look for it, and nobody came back. What they left behind is still waiting. **It's the only map with no
     colour:** black, ash and bone, lit by pale tear-light and candles (`Config/Map`: ash-black floor, black walls, grey
     ash on the rims; `Config/Lighting`: ClockTime 1, the least light of any world, a dim neutral grey sky with no stars). **The one
     colour left is red, and red is only ever eyes:** wherever you see red, something is looking at you. 24 props in
     `build_weeping_dark.py`, all with moving parts: mourners (the signature), hooded stone figures kneeling with their
     hands over their faces, shoulders heaving, tears running through their fingers, one red eye opening between them as
     they sob; black willows dripping tears; empty swings, one still swinging high, a small pair of shoes under it;
     rocking chairs rocking by themselves beside a candle; the last wall of a house, a candle in its window, its door
     swinging; plots of plain headstones with souls rising; coffins whose lids lift by themselves, pale fingers round the
     edge and red eyes in the gap; pale hands sliding up out of the ash; dying street lamps with moths; hooded bearers
     with no feet, holding out a lantern; now and then a lost teddy bear on its suitcase, its head turning after you, an
     empty socket glowing; ash reeds and candle stubs as filler; tear pools lying flat across the middle, a drowned face
     under each looking up at the flight, the right way up from it; on the rims claw trees and hollow houses where a
     shape rises in the lit window and sinks away; landmarks: the last lighthouse, its beam still sweeping (see-through,
     `Roles.sheer`), the tolling bell tower, and colossal wailing heads whose stone eyelids lift on red eyes; a funeral
     procession gliding along the top of the wall; heads pushing out of the walls, crying long lines of light, hands
     pressed against the stone beside them (`walls`); and a Long Arm reaching from one rim right over the corridor to
     grip the other (`overhead`). **The Watchers** fill the sky: colossal hooded shapes standing in the void beyond the
     island, high elbows, long pale fingers resting on its edge, heads turning slowly after you, weeping, two red eyes
     opening and closing. They're the size of the world and only just lighter than the fog. **The Last Door** ends the
     corridor, and the game: where every map has only ever had a wall, a colossal black door from the floor to high above
     the rims, chained, two great mourners carved in it crying down its face, and it isn't quite shut. Long fingers
     hold its edge from the other side, an eye moves in the gap, and a sea of candles fills the floor before it. If a
     map is ever added after this one, the door moves to the new end. **[Built, new]** This map is too dark for Neon
     alone, which lights nothing round it, so its candles and lamps cast real light (`Config/Decor` `propLights`, a
     PointLight added by `MapDecor`, flickering with the part's pulse in `PropMotionController`). Sparser than any other
     map on purpose: the emptiness is the point. No pentagrams, hexagrams or crosses: headstones are plain and
     round-topped, windows have upright bars only. Nothing shows how anyone died: the sadness is who's missing, the fear
     is what's watching. Plain colours in Blender (no stud image). Renders and two videos (`weeping_motion.mp4`,
     `weeping_flight.mp4`) in `design/world/models_weeping_dark/`, with the end of the world and a Watcher over the wall.
     FBX in `fbx/15_WeepingDark/Props/`. World 15 (14,700 to 16,500 studs, 10B luck, 2x size); `Config/Biomes`, `Map`,
     `Lighting`, `Decor`, `PropMotion`, `Roles` and the Index card colours are in. Until it has monsters eggs can't land in it.
     Tuned in play (2026-11-05): the Watchers went from size 2 to 3 (266 out, fingers still on the island's edge) as they
     looked small from the corridor; the real lights were halved, as they washed the stone out; and the sky was black with
     stars, hiding the Watchers, so the atmosphere is now high Haze, low Density and a warm Color that comes out grey (see
     `Config/Lighting`). In play, 21 of the 23 prop kinds in range moved (candle stubs and tear pools only glow) and all
     151 lights in range flickered. Shots from the game: `ingame_*.jpg`. Not seen yet: a real throw through it, and how a
     phone draws it. Its monsters must stay readable in the reveal, which keeps this world's light.
   - **Shattered Mirror** *(map 16's world made 2026-11-13, in Blender; FBX files ready in `fbx/18_ShatteredMirror/Props/`, not
     imported yet)*: **[Owner]** a new map after The Weeping Dark, Shattered Mirror picked from our three themes; "only design the world"
     this time, the monsters are a later prompt. **[Built]** `assets/models/build_shattered_mirror.py`, 18 props, all with moving parts.
     The world behind the glass: after the blackest map the light comes back all at once, a pearl-pink dawn, a silver floor,
     white quartz rims and smoked violet glass walls, everything throwing rainbows, and the reflections are wrong. Signature:
     the Standing Mirror, a gilt mirror on claw feet, cracked, with a silhouette in it that isn't yours, breathing, cold
     eyes open. Around it: shard clusters with one piece turning in the air, glass prism obelisks pouring rainbows on the
     floor, porcelain mannequins with cracked mirror faces turning their heads after you, kaleidoscope flowers of mirror
     petals, crashed chandeliers still lit, statues split into floating pieces, and now and then a heap of empty frames
     with eyes in the biggest; glass tufts and broken mirror bits as filler; flat cracked mirror pools with rings of
     rainbow in the middle. Rims: glass trees with mirror leaves, broken halls of mirrors with one panel revolving.
     Landmarks: the Looking Glass (a tower-sized hand mirror with an eye looking round in it, splinters orbiting it) and
     Kaleidoscope Towers (a rose window of rainbow glass turning on top). The Broken Moon hangs in the sky, its pieces
     circling it; splinters pour down the walls from cracks in the glass (`Shardfall`); colossal gilt Great Frames stand
     across the corridor, so the flight goes through one empty mirror after another. **[Owner]** Real chrome, "silver
     but with multiple colours", not something basic. **[Built, new]** Every silver, glass and gold part is metal: two
     MaterialVariants in MaterialService, **HoloChrome** (silver with rainbow flowing through it, almost mirror smooth) and
     **PolishedGold**, from our maps (`assets/textures/make_chrome.py`, uploaded 2026-11-13) made by
     `assets/models/studio_chrome.luau`. The build script's `METAL` says which roles get which; studio_tidy puts them on
     (Foil, no studs) and the part's colour tints them (near white = the whole rainbow, dark = dark chrome). Porcelain,
     marble and velvet keep their studs. This world's lighting turns reflections up (`EnvironmentSpecularScale` 1 against
     the game's 0.15). Roblox has no colour-shift-with-angle effect, so the colours change across a surface, not as you
     turn. World 16 (16,500 to 18,400 studs, luck 55 at its end, our pick past the old 50x top, size 1.35x like every map
     since 7). `Config/Biomes`, `Map`, `Lighting` (ClockTime 6, bright), `Decor`, `PropMotion` and `Roles` are in. The
     Last Door moved to the new end of the corridor (`Decor` WeepingDark, `Throw.lastDoorAt` 18,426), and the hidden Deep
     End moved behind it (18,400 to 19,900). Until its monsters are in `Config/Dinos` eggs can't land in it: far throws
     still land in The Weeping Dark, and luck stops at its 50x (`Throw.farthestLanding` and `luckDistance` now stop at the
     last world eggs can land in, not the last one built). Renders and two videos (`mirror_motion.mp4`,
     `mirror_flight.mp4`) in `design/world/models_shattered_mirror/`. Not seen in play yet, nor its light.
     **[Owner, 2026-11-13]** "More props, organized nicely with animations, I want this map to feel special." **[Built]** 28
     props now, all moving, and the world is three acts. You fly in through **the Threshold**, a colossal gilt arch whose
     broken mirror hangs in the air inside it in two rings turning opposite ways. **The Shattering** (0 to 680): broken
     glass scattered anyhow, as before. **The Glass Garden** (680 to 1,280): fountains pouring light into mirror pools,
     mirror butterflies beating their wings, kaleidoscope flowers, Kaleidoscope Towers either side of its gates, chrome
     islands floating in the sky. **The Ballroom** (1,280 to the end): music boxes with porcelain ballerinas pirouetting
     (their keys turning, notes of light rising), mannequins, statues and standing mirrors on a runway of mirror inlays
     down the middle, chandeliers swinging on bars across the corridor, oval mirrors hung on both walls (one crooked,
     swinging on its nail, a shape standing in another), pendulum mirrors on the rims, twin glass cathedrals with rainbow
     rose windows and prisms turning on their spires, and at the very end two Looking Glasses facing each other across the
     corridor before the Last Door. In the Garden and the Ballroom every prop has its twin across the corridor, mirrored.
     **[Built, new]** `Config/Decor` floor and rim rules can have `zones` ({ from, to, props, gap?, pairs? }): stretches of a
     world with props of their own, and with `pairs` each prop is placed twice, mirrored across the corridor (`MapDecor`,
     `map_kit.decorate_stage`, checked by `check_map.py`). Worlds without zones are laid out exactly as before. Renders of
     each act: `garden_*.png`, `ballroom_*.png`, `the_end.png`.
     **[Built]** Imported by the owner and tidied 2026-11-13 (`Assets.Maps.ShatteredMirror.Props`, 28 props; 95 HoloChrome
     parts, 38 PolishedGold). Play-tested: the game builds 570 props in the world, every act reads as planned, the
     ballerinas spin, chandeliers, wall mirrors and pendulums swing, notes rise, no errors. Tuned in play: at ClockTime 6
     the sky was night with stars, so its atmosphere is now a thick warm haze that comes out a dusty pink dawn
     (`Config/Lighting`). Not seen yet: a real throw through it (eggs can't land there until it has monsters), phones.
     **[Owner, 2026-11-13] Its monsters:** twelve on this map, not 8; "aggressive, but at the same time magnificent", not too
     aggressive, in the map's theme, each with an animation of its own and an aggression that looks like no monster already in
     the game. The owner's example, for one monster and not all: skin covered in shards that "get out of him and then go back in"
     in waves, like a stadium wave, and "not float". Six now and six in another prompt (left to us). **[Built]** the first six in
     `assets/models/build_shattered_mirror_monsters.py` (renders `design/world/monsters_shattered_mirror/`, FBX
     `fbx/18_ShatteredMirror/Animals/`, not imported yet), most common first: **Paw de Deux** (a smoked-glass panther with a
     crest of mirror shards; it sidesteps a whole circle round you, eyes on you, then springs and rakes), **Frill Seeker** (a
     porcelain lizard whose frill is a kaleidoscope, always turning; it rears and runs at you on two legs), **Dressed to Kill** (a
     mannequin whose head is a gilt hand mirror with a face in it; turns its head right round, then lunges in jerks like a broken
     doll), **Wrecking Ballroom** (tiled in mirrors, a mirror ball for a tail club, always turning; pendulum swings, higher each
     time, then a slam), **Swanquish** (a swan and its black reflection on one body, two necks that always move as mirror images;
     wings flare, necks strike together like shears), **Mane Event** (a lion whose mane of mirror shards does the owner's
     stadium wave for ever; it rears rampant, every shard bursts out and rattles, it roars and slams down). Shared face: cold
     cyan slit eyes (the world's Gleam) under chrome brows, glass fangs. Chrome and gilt are metal, as in the world (`METAL`).
     New in `DinoLifeController`: a marker table's `"@always"` moves run all the time, on top of the attack cycle. Names are
     ours.
     **[Owner, 2026-11-14] On those six:** only Swanquish is good; the owner doesn't like the other five (not to be remade now):
     they share one mouth and one set of teeth. For the next six: "something unique", "more complex, something actually wow",
     two feet but "not an actual humanoid body", "I want them shards to be floating and waving and doing stuff" (this replaces
     "not float"), and the rarest "must look the best". **[Built]** the six rarest in
     `assets/models/build_shattered_mirror_rare.py` (renders `design/world/monsters_shattered_mirror_rare/`, FBX in the same
     `Animals` folder, not imported yet). No shared head, no rows of teeth, and on every one shards that float free of the body
     and never stop moving: **Stilt Life** (a porcelain wader on gilt stilts with a dagger bill, two fans of mirror blades
     hanging in the air for wings; coils its neck and stabs three times), **Prism Break** (a midnight raptor with a prism for a
     head and a visor of light, a sail of rainbow glass floating over its back; the sail tips forward and fires blade after
     blade, then it charges), **Moth-er of Pearl** (a pearl moth in the air on four glass wings, no mouth, two rings of shards
     circling it opposite ways; claps its wings shut and dives), **Vainglory** (a sapphire peacock whose train is thirteen
     floating mirror eyes with a wave running through them; fans, shivers, struts, and the eyes stab outward), **Mirror Mirror**
     (the world's standing mirror walking on two bird legs, two cold eyes in the hole in its glass, two rings of shards wheeling
     round it; the glass bursts out and what lives inside leans out to look for you), and the rarest, **Royal Pane** (a white
     and gold wyvern helmed in chrome, a ring of shards turning over its head, wings of stained-glass panes floating between
     gilt fingers; it rears and beats the panes out at you). **Not in `Config/Dinos` yet:** that comes when all twelve are
     imported, with their chances, rarity words and Index card.
   - **Joining**: whether the floor steps down at each world (question 5 in section 15) is still open.

The walking reveal and the flight camera are a separate job, after the world. The throw wind-up is built (section 7).

---

### The Deep End, after the last world [Owner, 2026-11-07]
**[Owner]** The game needs something that doesn't end. **[Built]** (`Config/DeepEnd`, `docs/RETENTION_PLAN.md` step 3) Behind the Last
Door, at 16,500 to 18,000 studs, is The Deep End, the 16th entry in `Config/Biomes`. An egg strong enough bursts through the door
with a flash (`ThrowCinematic.doorBurst`). The door itself is unchanged.
- **Depth:** distance stops being a place and becomes a number. The egg always lands on the same floor (`Throw.farthestLanding`), and the
  real distance (Throw Power x the meter) gives its Depth: Depth 1 at 16,950 studs, each step 1.38x longer than the last. There's no
  last one. Each Depth makes rare colours and sizes x0.5 likelier on that throw, so x2 at Depth 2. The first time you reach a Depth
  it shouts "DEPTH 2!". FARTHEST THROW shows the real distance, and bars stop getting dearer past the last world.
- **Catches:** it has no monsters of its own and no Index card. Its eggs roll `Dinos.DeepPool`, the 40 monsters of worlds 11 to 15, and a
  catch counts for its own world in the Index. The luck offer's Details shows these real odds, Depth included.
- **The world** (`assets/models/build_deep_end.py`, renders in `design/world/models_deep_end/`): a shock of colour after the blackest
  map: teal stone, old bone and mint light at the bottom of a colossal shaft. Something giant fell here: its ribs, teeth and skulls
  lie about, and Depth Gauges, the signature, measure a depth nobody found the bottom of. Chains hang from too high to see. At
  the end the Bottom Face glares back up the corridor, with a working jaw: past Depth 2 every egg lands in front of it.

---

## 10. How it looks

**[Owner]** Studs on everything.

**[Seen]**
- Chunky, bright and readable from far away. Everything is big blocks.
- **Two-tone checker on all ground and walls**: light and dark green grass, light and dark brown dirt, orange and yellow platform.
- **Grass over walls**: a flat band with square blocks of different lengths hanging down. It's a signature of the look.
- Saturated colours, slightly neon greens. Black outlines on UI text.

---

## 11. Screens and HUD

**[Built]**, built with `UiKit` from the Figma designs:

- **Left:** square icon buttons with bold outlined labels: Index (book) and Shop (basket).
- **Right:** Dinos (paw) button.
- **Bottom left:** ⚡ Throw Power in big blue outlined numbers, and cash in big green outlined numbers.
- **Bottom:** 10-slot hotbar with each dino's $/s and key number.
- **Panels:** Index, Robux Shop, My Dinos (ON PLOT / BACKPACK tabs), Egg Shop (opens only from its stall), Welcome Back.
- Everything shrinks to fit short screens.
- **[Owner, 2026-11-06] Phones** (play-tested by the owner's friends on an iPhone): the HUD came out PC-sized, the
  Shop button covered Throw Power, the hotbar covered the cash, the jump button sat on the meter, the PERFECT! tint
  and the throw's bars stopped short of the screen's sides, the sparkles were empty boxes, the NEW! sticker sat on
  the monster's name, the #1 crown was a big yellow blob, and monsters couldn't be picked up off the base. **[Built]**
  fixes:
  - Sizes come from the area our UI really gets (`UiKit.screenSize`: under the top bar, inside the phone's safe
    area), read the landscape way round: the Roblox app is portrait on phones, and a size read while the game was
    still loading made the HUD full size. The hotbar shrinks to fit between the cash/power and the same margin on
    the right; its $/s stays readable.
  - While aiming, throwing and in the reveal the phone's joystick and jump button are hidden, and a tap anywhere
    throws (before, only a tap on the meter did). **[Built] [Owner, 2026-11-07]** The jump button still showed
    on a phone and a jump over the throw platform left the player stuck, so `ThrowController.lockJumping` now also hides
    the jump button and turns Jumping off while the player is over the platform or in a throw. Full-screen layers (the throw's bars, the fades, the PERFECT! edges)
    reach past the notch. The aim camera pulls back for big avatars (`ThrowCinematic.setThrower`).
  - **Tap or click one of your monsters on your base to pick it up** (on a computer it's outlined while the mouse is
    over it), as well as PICK UP in My Dinos. A drag turns the camera without dropping a carried monster.
  - The crown is shiny metal with a soft light, not Neon, and no bigger than a normal head's. The event icon sits just
    above a phone's (smaller, lower) jump button.
  - Text uses no symbols phone fonts lack ("✦", "✓", "▲", "›" showed as empty boxes); sparkles are drawn shapes.

**[Seen]** The reference's gear icon sits next to Throw Power, and spending shows a red "-$X" floating up from cash.

**[Built, 2026-11-13] Low detail, [Owner]** "a switchable option in settings, not automatically". A switch in the gear's
Settings panel, under **Performance** (the old "Bases" heading, with "Hide other players' dinos"), off by default and
saved (`Config/Settings` `lowDetail`, `LowDetail`). On that player's screen only: no glow or sun rays, no shadows from
the map, no clouds, moving props stand still, and monsters further than 50 studs move less smoothly (120 normally).
Turning it off puts everything back. Nothing about the game itself changes. Measured in Studio at the start of the lane:
589 of 1,896 loaded map parts cast a shadow; with the switch on, none. The switch's own logic is tested; the row was
not clicked through by hand, and no frame rate was measured on a real phone.

**[Built]** Pop-up text, designed in Figma ([Throw Eggs - Pop-up Text](https://www.figma.com/design/RPcPJ7Qm7DBI6957rW04cG),
where each motion plays) and built in `PopText` with its looks and timings in `Config/Pop`. No panel behind any of it,
just a thick ink outline and a hard shadow:
- **Float:** a red "-$X" beside the cash when spending, a green "+$X" for other gains (not the income ticking in every
  second), "+$X/s" when income rises, "+XP" over the training bar.
- **Shout:** LEVEL UP!, an event starting (in its colour) and a world completed in the Index (after the reveal), big
  and gold in the upper middle.
- **Notice:** server messages above the hotbar, gold when something worked, red with a shake when it didn't.
- **Punch:** the meter's result word (PERFECT!, GREAT!…) punches in on the tap.

---

## 12. Shops and progress

### The economy [Owner, 2026-11-04]
**[Owner]** Numbers start small, but after a few minutes of play things change. The goal is for players to stay,
feel powerful and compete; how big the numbers get doesn't matter.

**[Owner, 2026-11-07]** A little bit of easy progress early to mid game, then harder. Late game means map 10 and up: it
shouldn't be easy, but it shouldn't be a hard grind or impossible either.

**[Built, re-run 2026-11-08 after fixed power per bar and PERFECT at 1x: every row within about half an hour of this
table; average free player map 10 at 2.0 h, map 15 at 21.6 h]** Worked out with a play simulation (`tools/pace_sim.luau`: each kind of player trains, throws and shops in their
own way, a session a day, with offline earnings and the daily reward) that runs the game's own Config (2026-11-07, median of 9
runs). Run on the numbers of 2026-11-06 it gave map 15 at 30.3 h, against 30 h from the simulation it replaces. Hours are
time played; the Index's x2 XP boost and bought lucky throws aren't counted.

| Player | Map 5 | Map 10 | Map 15 | Days to map 15 | Longest late map |
|---|---|---|---|---|---|
| Free: casual (20 min a day) | 36 min | 3 h | 30.6 h | 90 | 11.3 h |
| Free: average (1 h a day) | 22 min | 2 h | 20.6 h | 21 | 7.7 h |
| Free: keen (3 h a day) | 17 min | 1.5 h | 16.3 h | 6 | 5.8 h |
| Free: grinder (6 h a day) | 15 min | 1.1 h | 10.9 h | 2 | 3.9 h |
| Free: leaves it squatting (2 h a day) | 23 min | 1.7 h | 14.3 h | 7 | 4.6 h |
| Free: loves throwing (1 h a day, 10 s of squats per 8 throws) | 1.2 h | 7.7 h | 90 h | 88 | 33.7 h |
| Free: bad at the meter | 32 min | 2.4 h | 22.7 h | 23 | 7.9 h |
| Free: never taps bubbles | 28 min | 2.7 h | 28.4 h | 28 | 9.9 h |
| Free: never buys rack upgrades | 1.5 h | 67.5 h | never | never | 102 h |
| Free: only buys rack upgrades | 22 min | 1.9 h | 20.6 h | 21 | 7.7 h |
| x2 Cash | 23 min | 1.9 h | 19.9 h | 20 | 7.2 h |
| x2 Training or x2 Power | 16 min | 1.1 h | 11.4 h | 12 | 4.1 h |
| Both of those | 11 min | 41 min | 6.1 h | 7 | 2.2 h |
| All 3 passes, keen | 6 min | 29 min | 4.7 h | 2 | 1.6 h |

The way there: `xpPerMap` 2.03 made power "way too hard" at map 10 (80 squats for +25 power), and 1.8 for every map was "way too
fast" (25 squats). That mixed up how long a bar takes and how long a map takes, so they're now separate (`docs/RETENTION_PLAN.md`
step 1): the maps' numbers set the XP each point of power costs, and `barSquats` cut every bar to about 22 squats, each giving
its share of the power. An average player's bar gave +20 power at map 8, +7 at map 11 and +2 at map 15, down to +1 in The
Deep End.

**[Owner, 2026-11-08]** That was wrong: "I don't want people to be capped at training at all, but harder", and buying rack
upgrades while the power per bar went down "players will not like that at all". Like the reference, every bar now gives the
same +5 power forever (x2 Power: +10), rack upgrades only give more XP per squat so bars fill faster, and the XP a bar needs
grows down the lane. An average player's bar takes 1 to 4 squats up to map 9, 5 at map 10, 17 at map 12 and 44 at map 15;
after a rack upgrade bars feel quick, then slowly get harder again.

**[Owner, 2026-11-07]** The passes stay full x2 on every map, as the shop promises ("forever"), even though both together
reach map 15 in about 3.4 h. Making late rack upgrades dearer doesn't help: it slows free players just as much.

**[Owner, 2026-11-06]** The owner's friends reached far maps far too easily. Two causes, both fixed:
1. Each rack upgrade had started multiplying XP per rep by 1.25 (`xpPerRepGrowth`) while a bar's XP only grew 1.1%
   a bar, so training snowballed: map 15 in about 2 hours instead of 31. The friends' 20 gifted x500 lucky throws
   (each a map's rarest in a rare colour and size, before the luck change in section 8b) made it under an hour.
2. A bar's XP grew with how many bars you'd filled, so anything that gives more power per bar skipped the most
   expensive bars: the x2 Power pass finished the game in 48 minutes.

- **Income** by rank is 1, 3, 10, 40, 150, 500 $/s on the Forest, **×100 for each map after it** (`Config/Dinos`), so a
  new map's first good catch multiplies income at once (map 15's rarest: about $5 × 10^30/s before mutations).
- **Throw Power works like the reference [Owner]:** XP fills a bar, and **every full bar gives +5 Throw Power, always**
  (`powerPerBar`; x2 Power makes it +10). **Rack upgrades** (the pad by the squat rack, bought with money) never change
  that: each gives 25% more XP per squat (`xpPerRepGrowth`; the pad shows "+X XP per squat" and how many more until the
  next rack), so bars fill faster. Upgrades cost $50, ×50 each (`Config/Training`). **The XP a bar needs follows how far
  your Throw Power reaches**, like the reference ("XP per level grows with distance down the lane"): 1 XP at the throw
  line, 1.6x more for every map your power reaches up to map 9, 3.5x across map 10, then 2x a map (`baseXp`, `xpPerMap`,
  `hardFromMap`, `hardMapStep`, `xpPerLateMap`, `Training.xpForNextBar`). Power from packs counts too. So x2 Power and
  x2 Training each make training exactly 2x faster, and a power pack skips just the bars it replaces. Early bars fill
  in a squat or two; later maps take longer because each bar needs more XP; money gates the rack upgrades (each costs
  minutes of income early on, hours later). A full bar floats "+5 ⚡ POWER" above STOP; the bar shows "Level N" (owner, 2026-11-08: no "per bar" text).
- **x2 Power (Game Pass) [Owner]:** every full bar on the squat rack gives double power, forever. Its card sits under
  x2 Cash and x2 Training in the shop; it shows SOON until its pass id is in `Config/Shop` `doublePower`.
- **Base upgrades** (`Config/Plot`): 10 spots, +2 an upgrade, 20 at most. **[Owner, 2026-11-06]** At $1,000 ×10 each
  the base was maxed 3 minutes in; it should be late game. Now $500K ×1,000,000 each ($500K, $500B, $500Qa, $500Sx,
  $500No): the play simulation buys them around maps 2, 5, 8, 10 and 13, maxed about 14 hours into the game.
- **One egg per map** (`Config/Eggs`), each 100x the one before: Dirty (free), Spotted ($500), Golden ($50K), Lava
  ($5M), Frost ($500M), Shadow ($50B), Abyss ($5T), Cosmic ($500T), Eclipse ($50Qa), Forbidden ($5Qi), Carnival
  ($5Sx), Clockwork ($5Sp), Thorn ($5Oc), Spore ($5No), Weeping ($5Dc); luck ×1 to ×17. **[Owner, 2026-11-08]**
  From Carnival on each egg is 1000x the one before, not 100x: late income outgrows 100x a map, so every egg was
  owned by about 7 h of a 22 h game and the shop went quiet. The play simulation shows egg prices don't change how
  fast anyone reaches map 15, so this only spreads the buying over the late game (last egg at about 17 h). **[Built], [Owner,
  2026-11-05]** Each egg's model follows its map (`assets/models/build_egg_blueprints.py`), and its card wears its
  colour and names its map. The Egg Shop row scrolls sideways past five and opens on your best egg.
  **[Owner, 2026-11-06]** The eggs made in Blender, "nothing special but more attractive as they ramp up in price".
  **[Built]** `assets/models/build_eggs.py` (renders in `design/eggs/`, FBX in `assets/models/fbx/00_Eggs/Props/`): all
  15 are the same faceted shell, exactly the thrown egg's size, each painted by its own pattern and following its map.
  The first three are plain patterns (dirt smudges, spots, a gold zigzag); then glow comes in (Lava's cracks, Frost's
  snow cap and icicles, Shadow's glowing eyes); then extra pieces (Abyss's lure, Cosmic's twinkling stars and gold
  planet's ring, Eclipse's glowing corona); then gold, gems and machinery (Forbidden's gilt book binding and gem clasp,
  Carnival's candy stripes and bulbs, Clockwork's gear, gauge and wind-up key); and the last three wear a gold crown with
  glowing roses (Thorn), glowing mushrooms (Spore) and a red weeping eye under a glowing halo (Weeping). From Cosmic on the
  yolk glows too. Each egg is two halves, the top half's parts ending in `Lid`, each closed by white and yolk. In the game
  (`src/shared/EggModel.luau`) the shop's cards and the egg in the hand and in flight use the Blender egg once it's in
  `ReplicatedStorage.Assets.Eggs`, and the block egg until then. The Prism Egg keeps its block model.
- **Number names** go up to 10^63 (K, M, B, T, Qa, Qi, Sx, Sp, Oc, No, Dc ... Vg).
- **Next goal bar** at the top: the Throw Power the next world needs with a PERFECT throw (a bar in that world's
  colour), and the cheapest thing to buy next with "$X to go" or "you can buy it!".
- **Money you can see:** the cash counter rolls up instead of jumping, and "+$X" rises over every base each second
  (one per base, not one per monster: the owner asked for no labels heaped over monsters; the monster tags show
  only on the 3 nearest, see section 4).

### Feeding [Owner, 2026-11-07]
**[Owner]** Feeding makes a monster bigger, beyond what its size mutation gives. It's the game's joke made into a goal.
**[Built]** (`Config/Chonk`, `PlotService` feed, `SellPanel`) My Monsters shows FEED on each monster on the base, in place of SELL (it's sold
from the backpack, or here once it's at the top level). FEED opens the Sell Stand's grid on the backpack: pick monsters, then FEED and a
second tap. Each is 1 food, 3 if it's the same kind, and costs 30 seconds of the fed monster's income. Each level needs one more food
than the last, up to Chonk 50. Passes' special monsters can't be fed, and a monster that's been fed, or the carried
one, can't be eaten. No training bonus, so it doesn't change how fast worlds come.
**[Owner, 2026-11-08] Looks only.** Feeding no longer changes money (it was +5% a level, x3.5 at the top, and Robux
monsters, a share of the best monster, grew with it). It climbs the size tiers instead: Thicc at Chonk 3, Absolute Unit 8,
Chonker 15, Mega Chonk 25, Planet-Sized 38, Unit of Doom 50 (about 1,275 food; 425 monsters of the same kind). A monster
caught bigger keeps its size until feeding passes it. Its tag and its My Monsters row say the size with **FED** after it,
so lucky catches stay special; the tag changes as soon as it grows. The Feed panel says which size a feed reaches, or
the next size and its level.

### Competition [Owner, 2026-11-04]
- **Server ranking** in the top left: the 5 players by $/s, you highlighted, a crown on #1.
- **Crown:** the server's #1 by $/s wears a glowing gold crown. The top three bases glow gold, silver and bronze
  round their fence and show 👑 #1, #2, #3 on the owner plate (`CompetitionService`, `Config/Competition`).
- **Overtaken alerts:** "Alex passed you! You're #3" in red, "You passed Alex! You're #2" in gold.
- **World first:** the first player in the server to land an egg in a world gets a shout on everyone's screen.
- **Two more global leaderboards:** HIGHEST $/S (best income ever) and FARTHEST THROW (studs). Their stats are saved;
  they stand right of the corridor, either side of the SELL stall (not checked in Studio), and show as plain parts
  until `board_HighestIncome` and `board_FarthestThrow` are made in `build_leaderboards.py`.

- **Egg Shop [Built]:** one egg per map, see The economy above.
- **Robux Shop [Built]:** x2 Cash, x2 Training, x2 Power, lucky throws x100 (R$ 3 once, then R$ 9) and x500 (one throw each), Server Luck x2 (20 min since 2026-11-13; was 3, and 15 until 2026-11-09), 4 cash packs, 4 Throw Power packs, free starter dino.
  Product ids still have to be created on the Creator Dashboard.
  **[Owner, 2026-11-05]** Everything bought comes back after leaving. Server Luck runs for the whole server, and the
  buyer also keeps the time they haven't used (it only counts down while they play): it starts again when they next
  join, even if the old server closed. Game Passes are checked on join, with retries if Roblox doesn't answer.
- **Special monsters [Built], [Owner, 2026-11-05]:** Game Passes at the top of the Shop, bought once (a pass bought on
  the Store page counts, given on the next join). They can't be sold. They belong to no map and earn a share of your best monster (`Config/Specials`). ~~The income is fixed when bought~~ **[Owner, 2026-11-12]** The income is saved on the monster and follows your best monster: whenever your monsters change (a catch, a placement, a sale, a feed) it is worked out again as its share of the best you own, so its $/s tag and what it pays go up; it never goes down (`PlotService.refreshSpecials`);
  other special monsters never count as "best", so buying a second can't multiply the first. A bought monster always
  fits: it goes to the backpack if the base is full. First one: **Gloomfin**, 900%, a dark shark floating clear of the
  ground with red glowing eyes (`assets/models/build_special_monsters.py`; our name, the owner may rename it). Its
  pass id is in `Config/Specials`. **[Owner, 2026-11-06]** Remade as "the most aggressive" of the specials: hunched
  and scarred, a mouth that is most of its face hanging open on crooked teeth with a red eye in its throat, slit eyes
  under hard brows and bone horns, a torn bone-edged dorsal fin, bone spikes, burning gills and slashes, and foam
  dripping from its jaws. It swims and hovers like The Abyss's monsters, and its foam's Drip bone gives it The
  Weeping Dark's RAGE on top: every 4 seconds it lunges and bites, snapping between, its tail cracking.
- **The shop four, better looking and with their own attacks [Built, not imported yet], [Owner, 2026-11-12]:** all four specials got
  more to look at (tiger bands over the dark back, a burning crack across the skull; Gloomfin small under-fins, jaw spurs and
  veins in its dorsal fin; Duskeel a cobra hood with a false eye and a burning sail edge; Umbray burning wing edges and a
  harpoon stinger; Dreadlure belly lights and bait threads under its lure) and an attack nothing else has, 4 seconds, once per
  `DinoLife.attackCycle`, nothing leaving the body. A marker bone picks it (`MARKED` in `DinoLifeController`, mirrored in
  `build_special_monsters.py`): **Gloomfin** `Dorsal`, the death roll (draws back, rams, rolls twice biting, last bite and shake;
  this replaces RAGE, its Drip bone is gone); **Duskeel** `HoodL`, the hooded strike (rears like a cobra, hood wide, strikes
  ahead then to the side); **Umbray** `Stinger`, the loop and the sting (loops the loop, tail whips over its back, stabs twice);
  **Dreadlure** `Bait`, the bait (shuts its mouth, dangles its lure, then lunges and takes everything in front). Until the new
  FBX files are imported the old models keep their old moves.
- **Prism Egg [Built], [Owner, 2026-11-05]:** a Robux egg (Developer Product) bought again and again, like the
  reference's Rainbow Egg, on a card under the pass monsters. It hatches at once, rolled on the server, into one of
  three special monsters of Gloomfin's dark family: **Duskeel** 150% (70%), **Umbray** 300% (25%), **Dreadlure** 700%
  (5%) (`Config/Shop` prismEgg, `Config/Specials`). The card shows each one turning with its odds, its share and what
  it would earn now (Roblox wants odds shown before buying). A hatch gets a shout. Like Gloomfin they never count as
  "best". ~~They can be sold, since another egg can always be bought.~~
- **No selling Robux monsters, RESIZE instead [Built], [Owner, 2026-11-08]:** none of the four specials (Gloomfin,
  Duskeel, Umbray, Dreadlure) can be sold, at the Sell Stand or in My Monsters, or fed to another monster, so Robux is
  never lost by mistake. Their row in My Monsters has **RESIZE** where SELL was: a panel with SMALLEST, -, +, BIGGEST
  steps through normal size and each size mutation's scale (x1 up to x10, Unit of Doom). Looks only: the income stays
  what it was when bought. Saved on the monster (`entry.resize`; `DinoStats.resizes`, `PlotService` resize).
- **GIFT [Built], [Owner, 2026-11-05]:** "only dev products and game passes": a GIFT button in the Shop's header opens
  a panel to pick a player in the server, then one of: Prism Egg, Gloomfin, Luck x100/x500, x2 Cash/Training/Power,
  cash packs, Throw Power packs (`Shared/Gifts`). Server Luck is left out (it's for the whole server already), and so
  is the one-time Luck x100 deal. Developer Products are gifted with their own ids: the server remembers who the gift
  is for when it shows the prompt and gives the receipt to them. A Game Pass can't be bought for someone else, so each
  pass has a gift Developer Product priced like it (`giftProductId`, 0 until created); a gifted pass is saved on the
  receiver (`giftedPasses`). The receiver gets a shout "GIFT FROM NAME!"; if they left before it arrived, the buyer
  keeps it. Someone who already has a pass shows OWNED and can't be sent it.
- **Shop size and opening [Built], [Owner, 2026-11-09]:** the Shop panel opens at 85% of its old size on computers (phones keep
  the full size, already scaled to fit, so the text stays readable). It springs up from lower down and tilted 5 degrees,
  growing from 60% with a little overshoot over 0.45 s, while a dark veil fades in behind it over the whole screen; closing is a quick
  0.14 s shrink with the veil fading out. `UiKit.panel` options `sizeFactor` and `openEffect = "rise"` (other panels keep the
  small pop); no fade on the panel itself, as a CanvasGroup would hide its live monsters.
- **Shop redesign [Built], [Owner, 2026-11-06]:** "like the original but more beautiful, more effects". Figma
  "Throw Eggs - Shop" (https://www.figma.com/design/kMvEjKptJBD0q5GRR5SaX4) is the design; `ShopController` builds it.
  Each pass monster gets a big featured card with the real model **playing its own idle, never spinning** (it bursts out
  over the card's top edge), red light rays turning behind it, a breathing glow and a glowing pedestal; the Prism Egg
  card has a shimmering rainbow edge, drifting rainbow beams and its three monsters on tier-coloured pedestals (Dreadlure
  bigger, JACKPOT!). Boosts, packs and passes are card grids; the free starter monster idles on a pedestal. Effects only
  run while the panel is open (`DinoLifeController.showcase`).
- **Not built yet:** more special monsters.
- **Index [Built], [Owner, 2026-11-11]: a total redesign** (Figma "Throw Eggs - Index & Inventory", Index v4, row at
  y=9000; `IndexController`). It replaces the scrolling list below.
  - **One map fills the panel**, its picture as the background. Left: one monster with nothing behind or under it [Owner], the real model
    playing its idle (**only the selected monster moves**; the cards are still), with its name, rarity and "1 in X"
    written straight over the picture (no box, no "caught", no earnings). Right: the map's 8 monsters as cards; tap one
    to put it on the pedestal. An uncaught one is a black shape named "???".
  - **Scrolling changes map:** the mouse wheel, or a swipe up or down on a phone; the next map slides in and the
    picture fades. A thin bar on the right shows where you are. **ALL MAPS** opens a grid of the 15 worlds (picture,
    found bar, lock with "Needs N Power", red dot) to jump to one. It opens on a map with a reward waiting, else on a
    new farthest map, else where you left it.
  - **Throw Power per map:** a green pill under the name, "400 POWER NEEDED" (the map's start distance: a PERFECT throw
    flies as far as your power; Forest says "NO POWER NEEDED"). A map you can't reach is darker with a lock, "TOO FAR
    TO REACH" and a bar of your power against what it needs. No other helper text [Owner].
  - **The reward is collected by hand:** under the cards is a plain **2x TRAINING XP** button. Grey until every monster
    of the map is found; then green with a red dot. Pressing it cracks an egg open (`Config/Index` `rewardEgg`) and
    starts the boost (`IndexRemotes.Claim`, checked on the server, once per map, saved in `indexClaimed`); after that
    it is grey with a tick. Finishing a map only shouts "COMPLETE! Reward waiting in the Index". Maps finished before
    this was built already gave their boost, so they start collected.
  - **Red dot:** on the HUD's Index button with the number of rewards waiting, on ALL MAPS, on that map in the grid
    and on its button.
  - Rejected on the way [Owner]: a strip of map numbers under the header, a found-eggs row, "MAP 2 OF 15", "you have N
    power", a boxed monster card, an egg-shaped reward card, a "COMPLETE!" ribbon on the reward.
  - The background uses the card pictures stretched (`mapPictures`); taller shots can be set per map in
    `Config/Index` `mapBackdrops`.
- **Index, 2026-11-06 (replaced):** the tabs below are replaced. "Scrollable like it was in the very first version",
  with real map pictures, and "the maps to show on the left edge", ready for 8 monsters a map. Figma Index v2: one
  scrolling list; each map's in-game picture on a card flush with the panel's left edge (number, name, found bar, the XP
  reward) and its monsters beside it in rows of four. It opens at your farthest map. Only maps near the screen hold live
  models, and none while it's closed. Pictures in `Config/Index` `mapPictures`.
- **Index, earlier:** every dino by world. **[Owner, 2026-11-05]** Redesigned (Figma "Throw Eggs - Index &
  Inventory"): a tab per map down the left (its colours, number, "4/6 found", a tick when complete; maps whose
  monsters aren't made yet say COMING SOON), and the chosen map's banner and its 6 monsters on the right, **sorted by
  rarity** from COMMON to the map's boss, a new 6th tier **MYTHIC** (pink; it also colours that monster's reveal and
  lucky banner): COMMON, UNCOMMON, RARE, EPIC, LEGENDARY, MYTHIC. Each tile shows the real model turning, its rarity,
  its "1 in X" and its name; unseen ones are black silhouettes named "???" with their rarity and odds still shown.
  The total found sits in the header, the map's reward under its monsters. It opens on the farthest map you've
  found anything in. **[Owner, 2026-11-06]** Completing a world gives only
  x2 training XP for 15 minutes (`Config/Index` xpBoost; shown in the boost row at the bottom): no cash or luck from the Index. **[Owner, 2026-11-13]** Replaced: a
  world needs both its prize monsters, which now come from x100 and x500 throws (section 8b), and 15 minutes of XP was
  too little for that. Every collected world now also gives **+10% cash, forever** (`Config/Index` `cashBonus`,
  `IndexService.cashMultiplier`, applied in `PlotService`): +150% with all 15, on top of x2 Cash. Cash was chosen
  because it barely changes how fast anyone finishes. The button reads "+10% CASH FOREVER"; the XP boost still comes with
  it. Still no luck from the Index. **[Built]** maths tested in Studio; the button was not pressed in a play test. **[Owner, 2026-11-11]** It is
  collected by hand in the Index, not given the moment the world is completed.
- **Gifts for staying [Built, not play-tested], [Owner, 2026-11-12]** (`Config/PlayGifts`; to keep a new player past
  10 minutes): once per save, counted in minutes of play after the tutorial. A free x100 lucky throw at 8 minutes and a
  free x500 at 38 (**[Owner, 2026-11-12]** x500, not x100; **[Owner, 2026-11-13]** 30 minutes after the x100, was 20; players who already played keep 20, section 8b), shown as a gift icon counting down in the boost row, with the gift notification when it arrives. At 5 minutes the
  player's own first event (Double Luck, 5 minutes, only for them) starts, unless a real event is running then.
- **Gift notification [Built], [Owner, 2026-11-12]** (Figma "Throw Eggs - Pop-up Text", `Gift Toast` 20:140;
  `GiftToastController`): a small card at the top right for free play gifts and gifts from other players, not a big
  shout. It slides in from the right with a small overshoot, the gift tile pops, a shine sweeps once, it stays 4 s and
  slides out; tap closes it. Several queue, and it waits while a reveal or the tutorial is on screen.
- **Timed events [Built], [Owner, 2026-11-05]:** every 15 minutes one starts and runs 5 minutes, taking turns:
  Double Luck (2x luck) and Ghost Rush (GHOST 10x likelier) (`Config/Events`, from the server clock, the same on
  every server). A shout when one starts and an icon at the bottom right with the time left; hover (PC) or tap
  (phone) for what it does. The older Meteor Shower / Growth Spurt / Gold Rush were removed before this.
- **Server best catch [Built], [Owner, 2026-11-05]:** the rarest catch of the server's life stands on a pedestal at
  the arena's front-left, against the wall, off every walking path (`Config/BestCatch`, `BestCatchService`). [Owner, 2026-11-07] Every monster on it stands at the same size, its longest side `monsterSize` studs, whatever its map, size mutation or feeding.
  A sign in front, part of the map (not a floating label), shows mutation, size, name, odds, income, world and
  who caught it. Pedestal: `build_best_catch.py` > `fbx/01_Forest/Arena/prop_BestCatchPedestal.fbx`.
- **No rebirth [Owner].** The reference game has none.

---

## 13. Ideas still waiting for a decision

These are in the GDD but the reference doesn't have them, so **ask before building any**: steering the egg mid-flight,
a 
and biome completion rewards (built, in section 12). Announcements are confirmed, so they moved to section 6.

---

## 14. What has to change in the game

| Today | Must become | Source |
|---|---|---|
| No announcements | A server-wide banner for lucky catches (section 6) | Owner |
| Auto-placement keeps dinos apart | Overlap is fine | Seen |
| Plain coloured parts with little or no stud texture | Checker and studs on everything | Owner |
| ~~After landing, the camera circles the egg right away~~ | Cut to black, then the walking view. **Built** (section 7) | Owner + Seen |
| ~~The egg wobbles and bursts at 40%, and the dino pops up from nothing and spins~~ | Close-up, then pull back to the dino already standing still over the egg. **Built** (section 7) | Owner + Seen |
| Yellow letter tiles at the top | White outlined letters with blanks at the bottom centre | Seen |
| Final result in a panel with chips | Plain text at the bottom, a NEW! sticker, a rarity-coloured wash | Seen |
| Luck grows evenly with distance | Fast at first, slowing right down (ours is evenly spaced inside each world) | Seen |

Done on 2026-11-03: the sunken arena, platform and lower corridor, the throw line on the platform, 5 bases of 48 × 48
in one row holding 10 to 20, a rack and XP pad at each base, an Egg Shop only its owner sees, and SELL and the
leaderboards in the arena. Old saves that held more than 20 dinos, or spots outside the smaller fence, are fitted to the
new base when they load (the best dinos stay, the rest go to the backpack).

---

## 15. Open questions for the owner

1. Why are some bases' fences blue instead of wood? (Upgraded? Top level? A paid item?)
2. ~~Do racks change look as you progress?~~ Yes, with rack upgrades (section 5).
3. ~~Do empty or new players have a rack?~~ Every base has one; a base with no owner has the Gym rack (section 5).
4. ~~Where do the leaderboards stand?~~ Answered by a screenshot (section 6).
5. Does the corridor floor step **down** at each new world, as the thumbnail shows?
6. Is the sky changing a normal day/night cycle or part of the Halloween event?
7. How do you get back from a throw if you walk down into the corridor? Can players walk down there at all?
8. ~~Our item is an egg. Should the dino just stand over it like the reference, or should the egg also crack at the end?~~
   Answered 2026-11-06: it's cut in half when it lands, white and yolk showing (section 7, Flight).
9. ~~Does the amber glow in the walking view change colour with rarity?~~ Answered: the glow shows the catch's colour
   mutation (the video's animal was Gold). Still unknown: whether the reference darkens the edges on a catch with no
   colour mutation. Ours walks with a clear view then.
10. Does the "1 in X" counter appear during the walking view or after it on rare catches? A video of a rare catch would show it.

---

## 16. Reference material

In `docs/reference/` (the owner's red circles mark what matters):

| File | Shows |
|---|---|
| `arena-top-view-bases-circled.webp` | The arena from above, 5 bases in one row, tiny compared to animals |
| `arena-from-corridor-side.webp` | Platform, corridor below it, rim, trees, and the whole arena |
| `shop-rack-sign-circled.webp` | Shop stall, squat rack with orange pad, "20 MAX" sign |
| `owner-plate-circled.webp` | Profile picture with name and $/s over a base |
| `training-announcement-leaderboards.webp` | Announcement banner, leaderboards, a rack from inside while training, x2 bubble |
| `video-throw-windup-frames.jpg` | Perfect meter, black bars, spinning wind-up, first worlds of the flight |
| `video-flight-corridor-levels.jpg` | The three-level valley, the luck panel and world name |
| `video-landing-walk-pov-frames.jpg` | Dust, cut to black, the amber walking view |
| `video-closeup-pullback-letters-frames.jpg` | Close-up, pull back, letters filling in, final colour wash |
| `video-final-text-return-frames.jpg` | Final text, fade to white, back at the base |

The frames come from the owner's 23-second recording of one throw: `~/Documents/Screen Recording 2026-11-03 at 01.44.03.mov`
(no sound in the recording).

Also: the reference game's store thumbnails come from Roblox's public thumbnails API (universe id `10766972131`).
`docs/GDD.md` has detailed notes from three earlier gameplay recordings (training numbers, meter, flight, reveal order, shops).
