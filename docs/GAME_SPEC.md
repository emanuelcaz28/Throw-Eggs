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
outlined numbers and "+X XP / rep" under it. Other players' racks can look different from yours (see section 15).

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
- **Leaderboards:** MOST DINOS, TOP MONEY and LUCKIEST CATCH, top 10 across all servers, refreshed every minute,
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
- **[Built]** An x2 bubble pops up now and then. Tapping it gives a double rep and a purple glow.
- **[Built]** The level bar and STOP only show while training.

### Throw
- **[Built]** Step on the throw pad and a vertical meter appears. A marker swings up and down a tube with 10 levels and
  slows near the top. Level 10 is PERFECT and gives the biggest throw.
- **[Built]** Distance = Throw Power × the level's bonus. Our meter multiplies on purpose, unlike the reference's flat bonus.
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
- **[Owner]** Flight time depends on how far the throw goes. About 6 seconds is what a throw to the **last map** takes,
  so throws to the first maps must be over faster than that, and always smooth.
- **[Seen]** The bars and Throw Power go away as it starts. The camera begins low, climbs high behind the item
  looking down the valley, then drops low again as it comes down.
- **[Seen]** A thin white line trails along the floor behind the item, and white lines cross the floor at intervals.
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

### Landing and arrival: the animal walks to the egg
**[Owner]** Pay special attention to this part. The animal walking towards what you threw is the key moment, then its
name shows up slowly.

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
  get the lucky catch banner instead). Tapping skips ahead.
- **[Built]** The text follows mock-ups 15 to 16b: white dashes that fill with letters at the bottom centre, then the
  final moment and the final text with no panel (tier sticker on lucky catches, size and mutation, name in its rarity
  colour, NEW! on a first catch, $/s, the "1 in X" on lucky catches, tap to continue), then white for half a second.
- **[Owner, 2026-11-04] No rings, and luck only when it's really lucky.** The old rings round the monster looked cheap
  and made the animal feel unimportant. The "1 in X" showed on nearly every catch (a common monster with a common size
  is already "1 in 160"), so it meant nothing. And the clover icon and box round the odds looked ugly. **[Built]** now:
  - **Luck only from 1 in 1,000:** rarer catches get the counter, the luck labels, the tier sticker, the "1 in X" and
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
  - **Start and end:** set by how far below its eyes it sees the egg. The commonest catch starts with the egg 8° down
    (19 studs away for a Compy); the rarest (1 in 10 million and rarer) 1.8° down (about 85 studs for a Compy). Bigger
    monsters look down by up to 22° more, so a giant starts high up looking down at a tiny egg (about 900 studs away for
    that Star Sovereign). It stops with the egg 22° down (52° for the biggest), where the cut to black comes.
  - **Time:** 2.6 seconds for the commonest up to 4.6 for the rarest, plus up to 0.8 for the biggest. It slows a little
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
- **[Built]** The close-up and pull back after the walk (`RevealCloseUp`, numbers in `Config/Reveal` `closeUp`).
  Previews in `design/reveal/closeup/`.
  - **The monster is simply there:** behind the black after the walk, the caught monster stands still where its walk
    ended, at its real size (its map's standard size × its size mutation), facing the way it walked. It never pops out
    of the egg or spins. The egg lies upright on the ground and never moves.
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

The size mutation tiers work **the same as the reference game's**, with our own names. The reference has Big, Large,
Monstrous, Huge and Colossal **[Seen/Owner]** (Colossal exists, it just wasn't in our recordings), and a Giant size from
its Rainbow Egg **[Web, unconfirmed]**. Their order, odds and scale aren't published anywhere, so ours stay our own
numbers.

**[Owner]** Our six size mutations, smallest to biggest: **Thicc → Absolute Unit → Chonker → Mega Chonk → Planet-Sized →
Unit of Doom**. **[Built]** (`Config/Catch`), scale is on top of the map's standard size:

| Size | Chance | Income | Scale |
|---|---|---|---|
| Thicc | 1 in 10 | ×1.5 | 1.5× |
| Absolute Unit | 1 in 40 | ×2.5 | 2.5× |
| Chonker | 1 in 150 | ×4 | 5× |
| Mega Chonk | 1 in 600 | ×8 | 12× |
| Planet-Sized | 1 in 2,500 | ×20 | 35× |
| Unit of Doom | 1 in 10,000 | ×50 | 100× |

**[Built]** Luck makes mutations and sizes likelier too, gently: their chances are multiplied by luck^0.4 (`Config/Catch`
`luckPower`), and no single one goes above a 1 in 2 chance. The luck here is counted from the map's start, like the
monster roll (section 8b). Roughly, worked out from the formula:

| Luck (counted from the map's start) | Thicc | Chonker | Unit of Doom |
|---|---|---|---|
| 1x (start of any map) | 1 in 10 | 1 in 150 | 1 in 10,000 |
| 5x (end of any map) | 1 in 5 | 1 in 80 | 1 in 5,300 |
| 15x (end of a map, best egg) | 1 in 3 | 1 in 50 | 1 in 3,400 |
| 1,500x (and Luck x100) | 1 in 2 | 1 in 8 | 1 in 540 |

The "1 in X" shown on a catch stays the normal odds.

Old saves keep their sizes under the new names (Big → Thicc, Large → Absolute Unit, Huge → Chonker, Colossal → Mega Chonk).

- **[Owner]** Models are simple, not complex at all, but must have **good faces**. All animals get the stud texture in Studio.
- **[Owner]** More colour mutations, some much rarer than others. Gold is the most common, but not too common.
- **[Built]** Colour mutations (`Config/Catch`), most common first. Each recolours the skin and leaves the face alone:

| Mutation | Chance | Income | At 15x luck (end of a map, best egg) |
|---|---|---|---|
| Gold | 1 in 30 | ×2 | 1 in 10 |
| Ruby | 1 in 80 | ×3.5 | 1 in 27 |
| Diamond | 1 in 200 | ×6 | 1 in 68 |
| Emerald | 1 in 500 | ×12 | 1 in 170 |
| Bubblegum | 1 in 1,200 | ×18 | 1 in 410 |
| Amethyst | 1 in 3,000 | ×30 | 1 in 1,000 |
| Shadow | 1 in 8,000 | ×50 | 1 in 2,700 |
| Ghost | 1 in 20,000 | ×100 | 1 in 6,800 |

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
| 10 | Forbidden Library | 1.56x | Not made yet (its world is built) |
| 11 | Midnight Carnival | 1.64x | Not made yet (its world is built) |
| 12 to 15 | Not chosen yet | 1.72x to 2x | Mysterious, dark maps |

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

- **[Built] The number on screen is real, but each map counts it from its own start.** Luck climbs from one map's end
  to the next, multiplying evenly along the way (`Config/Luck`). The roll divides it by the map's starting luck, so
  every map runs from 1x at its start to about 5x at its end, then the egg, the Index, Server Luck, Luck x100 and
  events multiply on top. That's how a 10B number doesn't break a map's odds.
- **[Built] How luck changes a roll:** it multiplies every monster except the map's most common one, so extra luck is
  shared by five monsters. Forest, at the end of the map: the common Compy drops from 28% of catches to under 1% with
  Luck x100, and the rarest goes from 1 in 725 to 1 in 527. Every catch gets visibly better, and the rarest stay rare.
- **[Built] Lucky throws** (`Config/Shop` `luckyThrows`, `Config/LuckyOutcomes`, `LuckyThrows`). **[Owner, 2026-11-04]**
  A luck boost is for **one throw only**, and the shop sells several sizes: **x100** and **x500**. They're kept until
  used (several can be owned), and the next throw uses the biggest one owned, when the egg lands. The panel at the top
  right shows "NEXT THROW x100" and how many are owned.
  **[Owner] The x number is for show:** it multiplies the luck number during the flight, not the roll. What each one
  really does:
  - **x50** (daily reward): a 50/50. If it hits, the same as x100; if not, an ordinary throw.
  - **x100:** always something nice, never the nicest: the map's 4th or 5th rarest monster with a Gold, Ruby or
    Diamond colour (Gold most often), size rolled as normal. Forest: 1 in 3,000 to 1 in 100,000.
  - **x500:** the show. The map's rarest monster in one of four presets: Amethyst + Planet-Sized, Shadow +
    Planet-Sized, Shadow + Unit of Doom, Ghost + Unit of Doom. The reveal's counter climbs for 9 seconds through every
    label to a new top one, **IMPOSSIBLE!** (1 in a billion and up, pink, 400 sparkles), and the whole server gets the
    lucky catch banner.
  - **The "1 in X" is never made up** (the owner offered presets of numbers; we chose presets of catches instead).
    It's always the catch's real odds in normal play, and a banger's really are huge: Forest 1 in 15,000,000,000 to
    1 in 400,000,000,000. Roblox bans misleading purchases and most players are kids, so the shop text says what each
    throw really gives ("Next throw: the map's rarest, rare colour, GIANT").
  - A banger earns 600x to 5,000x its monster's $/s: a Forest banger makes 300K to 2.5M $/s, Volcano money.
  - **x100:** two Developer Products. "ONE TIME DEAL LUCK x100" (3728190387) at **R$ 3**, so people buy it without a
    thought, offered once per player with a ONE TIME DEAL! sticker; after that "Luck x100" (3728190780) at **R$ 9**.
  - **x500:** its Developer Product isn't created yet; the card shows SOON until its id is in `Config/Shop`.
  - Prices are set on the Creator Dashboard; the shop reads them from Roblox. Server Luck x2 stays a timed boost for
    the whole server.
- **[Built] Pity** (`Config/Hooks`): after 25 throws in a row without a monster of the map's 3 rarest, the next throw
  is guaranteed one. It says so after the reveal ("LUCKY STREAK!").
- **[Built] New-map gift:** the first egg that lands in a map you've never caught anything in hatches one of its 3
  rarest ("NEW WORLD BONUS!").
- **[Built] So close:** landing within 60 studs of the next map shows "SO CLOSE! 23 studs short of Swamp".
- **[Built] Daily reward with a streak** (`Config/Daily`, `DailyService`, `DailyController`): **[Owner]** days 1 to 6
  give a **x50 lucky throw** and day 7 a **x500 lucky throw** ("seems absurd but trust me"), kept until used like
  the bought ones. One claim per UTC day; the next day continues the
  streak, a missed day starts again at day 1, and after day 7 it goes back to day 1. The panel opens by itself 3
  seconds after joining when a claim is waiting, and a 🎁 button under Shop opens it any time, with a red dot while a
  claim waits.
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

**[Owner, 2026-11-04]** Luck reaches the billions, about 4-5x more per map (section 8b):

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
| 12 to 15 | Not built yet | 100M, 500M, 2.5B, 10B |

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
   - **Joining**: whether the floor steps down at each world (question 5 in section 15) is still open.

The walking reveal and the flight camera are a separate job, after the world. The throw wind-up is built (section 7).

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

**[Seen]** The reference's gear icon sits next to Throw Power, and spending shows a red "-$X" floating up from cash.

**[Built]** Pop-up text, designed in Figma ([Throw Eggs - Pop-up Text](https://www.figma.com/design/RPcPJ7Qm7DBI6957rW04cG),
where each motion plays) and built in `PopText` with its looks and timings in `Config/Pop`. No panel behind any of it,
just a thick ink outline and a hard shadow:
- **Float:** a red "-$X" beside the cash when spending, a green "+$X" for other gains (not the income ticking in every
  second), "+$X/s" when income rises, "+XP" over the training bar and "x2!" from the bubble.
- **Shout:** LEVEL UP!, an event starting (in its colour) and a world completed in the Index (after the reveal), big
  and gold in the upper middle.
- **Notice:** server messages above the hotbar, gold when something worked, red with a shake when it didn't.
- **Punch:** the meter's result word (PERFECT!, GREAT!…) punches in on the tap.

---

## 12. Shops and progress

### The economy [Owner, 2026-11-04]
**[Owner]** Numbers start small, but after a few minutes of play things change. The goal is for players to stay,
feel powerful and compete; how big the numbers get doesn't matter.

**[Built]** Worked out with a play simulation (a player who trains 40 s, throws 4 times, then buys the cheapest
thing they can, no Robux) that uses the game's real formulas, over all 15 maps (maps 9 to 15 continue the
pattern: each 100 studs longer than the last, incomes ×100, one egg each):

| Map | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Reached after | 2 min | 9 min | 18 min | 34 min | 54 min | 75 min | 1.9 h | 2.8 h | 4 h | 6 h | 9 h | 14 h | 21 h | 31 h |

- **Income** by rank is 1, 3, 10, 40, 150, 500 $/s on the Forest, **×100 for each map after it** (`Config/Dinos`), so a
  new map's first good catch multiplies income at once (map 15's rarest: about $5 × 10^30/s before mutations).
- **Throw Power works like the reference [Owner]:** XP fills a bar, and each full bar gives a fixed amount of power.
  **Rack upgrades** (the pad by the squat rack, bought with money) raise the power per bar in tiers: **5**, then
  **10** after 3 upgrades, **20** after 4 more, then each tier is one upgrade longer and gives 25% more (25, 31, 39...).
  Upgrades cost $50, ×50 each (`Config/Training`). Each bar needs 1.1% more XP than the one before: early bars
  fill in 2 seconds, by map 13 a bar takes about 2½ minutes (the x2 Training pass halves that). That growth, not
  money, is what makes the later maps take hours. (With fixed-size bars every map took about 20 minutes and the
  game was over in 5 hours.) A full bar floats "+5 ⚡ POWER"; the bar shows the power per bar.
- **Throw Power packs (Robux) [Owner]:** power put straight into your stats, small amounts at small prices so
  everything looks cheap: +100, +500, +1,000 (`Config/Shop` `powerPacks`).
- **x2 Power (Game Pass) [Owner]:** every full bar on the squat rack gives double power, forever. Its card sits under
  x2 Cash and x2 Training in the shop; it shows SOON until its pass id is in `Config/Shop` `doublePower`.
- **Base upgrades** $1,000, ×10 each (`Config/Plot`).
- **One egg per map** (`Config/Eggs`), each 100x the one before: Dirty (free), Spotted ($500), Golden ($50K), Lava
  ($5M), Frost ($500M), Shadow ($50B), Abyss ($5T), Cosmic ($500T); luck ×1 to ×4.5. The Egg Shop row scrolls
  sideways past five.
- **Number names** go up to 10^63 (K, M, B, T, Qa, Qi, Sx, Sp, Oc, No, Dc ... Vg).
- **Next goal bar** at the top: the Throw Power the next world needs with a PERFECT throw (a bar in that world's
  colour), and the cheapest thing to buy next with "$X to go" or "you can buy it!".
- **Money you can see:** the cash counter rolls up instead of jumping, and "+$X" rises over every base each second
  (one per base, not one per monster: the owner asked for no labels heaped over monsters; the monster tags show
  only on the 3 nearest, see section 4).

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
- **Robux Shop [Built]:** x2 Cash, x2 Training, x2 Power, lucky throws x100 (R$ 3 once, then R$ 9) and x500 (one throw each), Server Luck x2 (15 min), 4 cash packs, 4 Throw Power packs, free starter dino.
  Product ids still have to be created on the Creator Dashboard.
- **Not built yet:** dinos priced as a % of your best dino, Prism Egg, GIFT button.
- **Index [Built]:** every dino by world. Completing a world gives +10% $/s and +5% luck for good.
- **Timed events [Built], accepted by the owner:** Meteor Shower (2x mutations), Growth Spurt (2x sizes), Gold Rush
  (2x cash). 10 minutes each with a 20 minute break.
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
2. Do racks change look as you progress, since they're for showing off? One rack in the screenshots is gold and another blue.
3. Do empty or new players have a rack? Only two bases in the screenshots seem to have one.
4. ~~Where do the leaderboards stand?~~ Answered by a screenshot (section 6).
5. Does the corridor floor step **down** at each new world, as the thumbnail shows?
6. Is the sky changing a normal day/night cycle or part of the Halloween event?
7. How do you get back from a throw if you walk down into the corridor? Can players walk down there at all?
8. Our item is an egg. Should the dino just stand over it like the reference, or should the egg also crack at the end?
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
