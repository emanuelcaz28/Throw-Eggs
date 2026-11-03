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
- **[Seen]** Walking onto the platform: a quick fade to dark, then the camera is behind the player for aiming.
- **[Seen]** After the tap: black bars slide in at the top and bottom. The character does a big spinning wind-up
  while the camera whips around them, showing the arena behind, for about 1 second. Then the item is released.

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
- **[Built]** Very rare catches get a light beam and a "YOU CAUGHT!" banner on the base. Tapping skips ahead.

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
| Fern Valley | Compy, Gallimimus, Parasaurolophus, Stegosaurus, Velociraptor |
| Dry Plains | Pachycephalosaurus, Ankylosaurus, Triceratops, Carnotaurus, T-Rex |
| Swamp | Baryonyx, Dilophosaurus, Sarcosuchus, Brachiosaurus, Spinosaurus |

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
| 1 | Fern Valley | 1x | Compy, Gallimimus, Parasaurolophus, Stegosaurus, Velociraptor, Pteranodon |
| 2 | Dry Plains | 1.4x | Dusty Proto, Bonkhead, Grumposaurus, Triceratops, Carnotaurus, T-Rex |
| 3 | Swamp | 1.9x | Soggy Dimetrodon, Burpasaurus, Baryonyx, Sir Chomps-a-Lot, Neckzilla, Spinosaurus |
| 4 | Volcano Foothills | 2.7x | Toasty Raptor, Burnt Ankylo, Hot Sauce Trike, Magma Stego, Obsidian Rex, Volcano King |
| 5 | Ice Age Tundra | 3.7x | Brain Freeze, Woolly Rhino, Chilly Mammoth, Sabertooth, Frost Raptor, Blizzard Rex |
| 6 | Tar Pits | 5.2x | Sticky Steve, Slow Bob, Terror Bird, Pitch Raptor, Tar Titan, Bog Rex |
| 7 | Deep Sea Trench | 7.2x | Spiral Gary, Derpichthys, Dunkleosteus, Plesiosaur, Megalodon, Mosasaurus |
| 8 | Meteor Crater | 10x | Cosmic Chicken, Alien Steve, Comet Trike, Crystal Raptor, Void Rex, Meteor King |

### The style as you advance
**[Owner]** Keep the same chunky stud style, but as the maps go on, add absurd, funny models and names alongside
good-looking, aggressive dinos.

- **Map 1 is cute:** friendly faces and real dino names.
- **From map 2, each map mixes the two:** common animals are the silly ones (goofy names, derpy faces), and the rarest are the
  fierce ones (angry brows, smaller eyes, lots of teeth, horns, dark colours).
- **Both get stronger with each map:** sillier jokes and meaner, more fantastical dinos. The last map's rarest should look like a boss.
- **Names are ours:** none come from the reference game, and they stay readable in the letter-by-letter reveal.

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

| # | World | Luck at its end |
|---|---|---|
| 1 | Fern Valley | 2x |
| 2 | Dry Plains | 5x |
| 3 | Swamp | 9x |
| 4 | Volcano Foothills | 14x |
| 5 | Ice Age Tundra | 20x |
| 6 | Tar Pits | 27x |
| 7 | Deep Sea Trench | 35x |
| 8 | Meteor Crater | 45x |

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
2. **Real models in Blender**: the 6 animals and 9 props are made and waiting for the owner's OK (`assets/models/build_fern_valley.py`).
   Dino animations are in the same file. Floor, walls with hanging grass and rim, and platform are in `build_world_kit.py`. Colour comes from each part's Color, with see-through stud images on top
   (`assets/textures/`, applied in Studio as a SurfaceAppearance with AlphaMode Overlay), so one image suits every world. The arena pieces
   (floor and its four walls) are in the same file, under one model, `kit_Arena`.
3. **Into Roblox Studio**: import, apply the stud texture and two-tone checker, sky and lighting. Replace the current
   ground, and move the lane and arena numbers in `Config`, so throwing still works. *(Done 2026-11-03, sky and lighting
   still to do: the arena is `kit_Arena` from `build_world_kit.py`, placed with the corridor by `MapService`, sizes in
   `Config/Map`.)*
4. **Bases**: 5 small bases in the row, each with its rack, XP pad, sign and owner plate, plus a shop only the owner sees.
   Capacity 10 to 20. *(Done 2026-11-03. The rack, XP button, stall, fence and upgrade sign are Blender models,
   `assets/models/build_base_kit.py`, kept in `Assets.Maps.FernValley.Base` and placed through `BaseKit`. The owner plate
   and the sign's face follow the mock-ups 13b and 14 in `design/ui-mockups/build.py`. All fences are wood and every base
   has a rack until questions 1 to 3 in section 15 are answered.)*
5. **Fern Valley props and decoration**: our own trees, ferns, rocks and rim decoration, in Blender. *(Placed
   2026-11-03: the 9 props from `build_fern_valley.py` stand along the corridor floor (kept off the middle), as big
   trees on its rims, as eggs along the arena's rim and as small things behind the bases. `MapDecor` places them
   from `Config/Decor`, the corridor's with a fixed seed so every server matches. Props are scaled up to suit the
   walls, which makes their studs a little bigger than the walls' studs.)*
6. **Huge animals**: each map's standard size grows (to 10x at the last map), and size mutations scale up from that
   standard, with no cap, until late-game monsters look absurd on those bases (section 8). *(Done 2026-11-03: the six
   size mutations and per-map standard size are in, on the base, in the hand-placement preview and in the reveal. The
   carried copy stays small.)*
7. **Polish**: lighting, sky, small effects, and a check on phone speed.
8. **Then the other worlds**: each one copies the first world's pieces with its own look, and they get joined up.

The walking reveal, the throw wind-up and the flight camera are a separate job, after the world.

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
| After landing, the camera circles the egg right away | White ring and dust, cut to black, then the amber walking view | Owner + Seen |
| The egg wobbles and bursts at 40%, and the dino pops up from nothing and spins | Close-up, then pull back to the dino already standing still over the egg | Owner + Seen |
| Yellow letter tiles at the top | White outlined letters with blanks at the bottom centre | Seen |
| Final result in a panel with chips | Plain text at the bottom, a NEW! sticker, a rarity-coloured wash | Seen |
| Throw starts instantly | Black bars and a spinning wind-up with a whipping camera | Seen |
| Egg flight with one fixed camera offset | Camera low, then high, then low, with a white trail on the floor | Seen |
| Flight can last up to 8 seconds | About 6 seconds at the last map, shorter for nearer maps, always smooth | Owner |
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
9. Does the amber glow in the walking view change colour with rarity? One video isn't enough to tell. A second throw with a different catch would show it.
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
