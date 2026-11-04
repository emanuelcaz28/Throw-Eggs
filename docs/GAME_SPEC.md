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
| Throw platform | 72 wide, 16 deep, and the corridor is the same width |
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
- **[Seen]** Fenced all round with a gap (the gate) in the middle of the front edge. Wooden fence: posts and two rails,
  all with studs.
- **[Seen]** Some bases have blue fences instead of wood (see section 15).
- **[Seen]** Dinos overlap each other freely and stick out far past the fence, with a small name and $/s label over each.

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
- **Leaderboards:** MOST DINOS, TOP MONEY and LUCKIEST CATCH, top 10 across all servers, refreshed every minute,
  standing side by side **[Built]**. In the arena they stand on the ground in front of the wall, on the right as you
  face the bases from the platform **[Seen]**. The exact spot is an estimate.
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
| 5.0 to 6.4 | **The camera pulls back and up** past the animal's legs, and it's revealed standing over the item. Then the camera keeps circling very slowly. |
| 5.2 to 7.0 | Letters fill in **out of order**, about one every 0.2 seconds: `E`, `RE`, `IRE`, `S_IRE`, then `S`, `SI`… in big white outlined text. |
| 7.2 | **The final moment:** the screen washes in the rarity's colour (purple here) with a big ring around the animal, fading in about a second, with sparkles on the model. |

- **[Seen]** The animal never appears to walk on screen. It's the camera doing the walking, then the animal is simply
  there. So this needs no walking animations on our block dinos. It's one more reason it works so well.
- **[Seen]** The item stays lying on the ground between the animal's feet throughout.
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
  rarity colour wash with two rings and sparkles, and the final text with no panel (size and mutation, name in its
  rarity colour, NEW! on a first catch, $/s, the "1 in X" and the tier sticker on lucky catches, tap to continue),
  then white for half a second.
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
  - **Rings:** a catch with a colour mutation walks with rings round the screen in that colour (gold on a Gold catch,
    red on Ruby...), dark on the inside, strongest at the edges, clear in the middle. A catch with no colour mutation
    walks with a clear view. The rings use two images built into Roblox, so nothing had to be uploaded.
  - **Far eggs:** when the egg is a speck (under 10 pixels tall), a small glowing dot marks it so it can still be found.
- **[Built]** The close-up and pull back after the walk (`RevealCloseUp`, numbers in `Config/Reveal` `closeUp`).
  Previews in `design/reveal/closeup/`.
  - **The monster is simply there:** behind the black after the walk, the caught monster stands still where its walk
    ended, at its real size (its map's standard size × its size mutation), facing the way it walked. It never pops out
    of the egg or spins. The egg lies upright on the ground and never moves.
  - **Where the egg lies:** between the monster's front feet. With a giant, the egg lies far enough ahead of its feet
    for both feet to show in the close-up (a Unit of Doom's feet stand on the corridor's rims, either side of it).
    Where the monster's body is too low to stand over the egg, the egg lies just in front of its feet, worked out from
    the model's real shape. A monster under 2.5 egg heights tall (the first map's, like the Compy) would hide behind
    the egg, so the egg lies beside its front feet instead.
  - **Close-up:** fades in on the egg with the feet behind it, the camera low and close, a little to one side, looking
    down at it by 20° (only 4° for the biggest, so their legs tower up behind the egg over the corridor walls). The
    blank name, and on rare catches the counter, show at once. It holds for 30% of the name's time (0.4 to 2.5 s).
  - **Pull back:** the camera pulls back and up past the legs until the monster and the egg fill the screen, in 1.4
    seconds (2.4 for the biggest, whose camera ends hundreds of studs away), ending with the name. Down in the
    corridor the camera keeps between the walls. Then it circles very slowly, 5° a second. Tapping during the climb
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

1. **Standard size comes from progress only.** Monsters get bigger as you advance: the first map's are small, and the
   last map's **standard** size is about **10x** the first map's. A catch with no size mutation is always exactly its
   map's standard size.
2. **Abnormal sizes come from size mutations only.** Nothing else makes a monster bigger (or different) than its map's
   standard. A size mutation scales the monster up from its map's standard size.

The size mutation tiers work **the same as the reference game's**, with our own names. The reference has Big, Large,
Monstrous, Huge and Colossal **[Seen/Owner]** (Colossal exists, it just wasn't in our recordings), and a Giant size from
its Rainbow Egg **[Web, unconfirmed]**. Their order, odds and scale aren't published anywhere, so ours stay our own
numbers.

**[Owner]** Our six size mutations, smallest to biggest: **Thicc → Absolute Unit → Chonker → Mega Chonk → Planet-Sized →
Unit of Doom**. **[Built]** (`Config/Catch`), scale is on top of the map's standard size:

| Size | Chance | Income | Scale |
|---|---|---|---|
| Thicc | 1 in 10 | ×1.5 | 1.3× |
| Absolute Unit | 1 in 40 | ×2.5 | 1.6× |
| Chonker | 1 in 150 | ×4 | 2× |
| Mega Chonk | 1 in 600 | ×8 | 2.6× |
| Planet-Sized | 1 in 2,500 | ×20 | 3.5× |
| Unit of Doom | 1 in 10,000 | ×50 | 5× |

**[Built]** Luck makes mutations and sizes likelier too, gently: their chances are multiplied by luck^0.4 (`Config/Catch`
`luckPower`), and no single one goes above a 1 in 2 chance. Roughly, checked with 200,000 test rolls each:

| Luck | Thicc | Chonker | Unit of Doom |
|---|---|---|---|
| 1x | 1 in 10 | 1 in 150 | 1 in 10,000 |
| 2x (end of map 1) | 1 in 7 | 1 in 110 | 1 in 7,600 |
| 45x (end of map 8) | 1 in 2 | 1 in 33 | 1 in 2,200 |
| 300x (map 8, best egg, every boost) | 1 in 2 | 1 in 15 | 1 in 1,000 |

The "1 in X" shown on a catch stays the normal odds.

Old saves keep their sizes under the new names (Big → Thicc, Large → Absolute Unit, Huge → Chonker, Colossal → Mega Chonk).

- **[Owner]** Models are simple, not complex at all, but must have **good faces**. All animals get the stud texture in Studio.
- **[Owner]** More colour mutations, some much rarer than others. Gold is the most common, but not too common.
- **[Built]** Colour mutations (`Config/Catch`), most common first. Each recolours the skin and leaves the face alone:

| Mutation | Chance | Income | At 45x luck |
|---|---|---|---|
| Gold | 1 in 30 | ×2 | 1 in 7 |
| Ruby | 1 in 80 | ×3.5 | 1 in 18 |
| Diamond | 1 in 200 | ×6 | 1 in 43 |
| Emerald | 1 in 500 | ×12 | 1 in 110 |
| Bubblegum | 1 in 1,200 | ×18 | 1 in 260 |
| Amethyst | 1 in 3,000 | ×30 | 1 in 650 |
| Shadow | 1 in 8,000 | ×50 | 1 in 1,700 |
| Ghost | 1 in 20,000 | ×100 | 1 in 3,500 |

- **[Built]** Each map's standard size is `standardScale` in `Config/Biomes`: 1x, 1.4x, 1.9x for maps 1 to 3.
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

---

## 8a. The game plan

**[Owner]** Left to us to decide: how many maps and animals per map, and how the plan runs. Decided:

**8 maps with 6 animals each: 48 animals.** The reference has more, but we'd rather have fewer that are all good.
It's built in order and released in stages, so the game can go live before all 8 are done:

1. **Maps 1 to 3 are the first release.**
2. Then maps 4 to 8, one at a time, as updates that give players a reason to come back.

Each map's animals are about 1.39x the size of the previous map's, which reaches 10x at map 8.

| # | Map | Size | Animals, most common first |
|---|---|---|---|
| 1 | Forest | 1x | Compy, Gallimimus, Parasaurolophus, Stegosaurus, Velociraptor, Pteranodon |
| 2 | Desert | 1.4x | Dusty Proto, Bonkhead, Grumposaurus, Triceratops, Carnotaurus, T-Rex |
| 3 | Swamp | 1.9x | Soggy Dimetrodon, Burpasaurus, Baryonyx, Sir Chomps-a-Lot, Neckzilla, Spinosaurus |
| 4 | Volcano | 2.7x | Toasty Raptor, Burnt Ankylo, Hot Sauce Trike, Magma Stego, Obsidian Rex, Volcano King |
| 5 | Frozen Peaks | 3.7x | Brain Freeze, Woolly Rhino, Chilly Mammoth, Sabertooth, Frost Raptor, Blizzard Rex |
| 6 | Shadow Bog | 5.2x | Sticky Steve, Slow Bob, Terror Bird, Pitch Raptor, Tar Titan, Bog Rex |
| 7 | The Abyss | 7.2x | Spiral Gary, Derpichthys, Dunkleosteus, Plesiosaur, Megalodon, Mosasaurus |
| 8 | Starfall Crater | 10x | Craterback, Stargazer, Comet Trike, Ringhorn, Nebulasaur, Star Sovereign |

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

### How animal models are made
- **Simple shapes:** chunky blocks and tapered blocks, no fine detail. The silhouette should read from far away.
- **Good faces:** big eyes with a pupil and a highlight, an expressive brow, clear teeth or mouth. Each animal has its
  own personality. The face is where the effort goes.
- **No studs modelled**, but every model has UV maps laid out so the stud texture repeats evenly in Studio.
- **Parts by colour role** (body, accent, belly, eyes, teeth and so on), so a mutation can recolour the skin and leave
  the eyes and teeth alone, keeping the face readable.

---

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

| # | World | Luck at its end |
|---|---|---|
| 1 | Forest | 2x |
| 2 | Desert | 5x |
| 3 | Swamp | 9x |
| 4 | Volcano | 14x |
| 5 | Frozen Peaks | 20x |
| 6 | Shadow Bog | 27x |
| 7 | The Abyss | 35x |
| 8 | Starfall Crater | 45x |

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
6. **Huge animals**: each map's standard size grows (to 10x at the last map), and size mutations scale up from that
   standard, with no cap, until late-game monsters look absurd on those bases (section 8). *(Done 2026-11-03: the six
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

- **Egg Shop [Built]:** Dirty (free), Spotted ($500), Golden ($10K), Lava ($250K), Cosmic ($8M). Each multiplies distance luck (×1 to ×3).
- **Robux Shop [Built]:** x2 Cash, x2 Training, Server Luck x2 (15 min), 4 cash packs, 4 Throw Power packs, free starter dino.
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
9. ~~Does the amber glow in the walking view change colour with rarity?~~ Answered: the rings show the catch's colour
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
