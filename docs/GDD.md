# Throw Eggs for Dinosaurs — Game Design Doc

`docs/GAME_SPEC.md` wins where the two differ (base size and count, map, shop and rack placement). This file
still describes the game as built.

Genre reference: "Throw Food for Animals" (train → throw → RNG catch → plot income).
Familiarity hook: eggs + dinos, borrowing recognition from "Steal an Egg"-style games.
Rule: same genre, our own names, models, UI and numbers. Nothing copied 1:1.

## Core loop

1. **Train** — step into the squat rack's dashed circle (every base has one, right of its gate; only its owner trains there): the character is locked in under the bar and squats with it
   on their shoulders; auto-reps give XP until STOP. Level-ups raise **Throw Power** ("LEVEL UP! Throw Power +20").
   The round orange button in front of the rack sells more XP per rep for cash. Now and then an x2 bubble pops up; tapping
   it gives a double rep and a purple glow. The level bar and STOP only show while training (`Config/Training`).
2. **Throw** — step onto the orange platform in the arena's front wall → egg meter: a marker swings up and down a vertical tube with 10 levels
   and slows near the top. Level 10, the top step, is PERFECT and gives the biggest throw.
   The equipped **egg** flies down one long corridor, below the arena, through biomes and lands on its floor. Distance = Throw Power × the level's bonus.
   A **Luck multiplier** grows with distance (shown live, top of screen).
3. **Hatch / reveal** — the egg lands in a biome and hatches. Dino name fills in letter by letter
   (hangman style) while a "1 in X" counter climbs. Labels escalate: LUCKY! → SUPER LUCKY! → INSANE → LEGENDARY → GODLY.
   Final card: mutation (Gold / Diamond / Emerald…), size (Big / Large / Huge / Colossal), $/s, "NEW BEST!".
   The roll is decided on landing; the counter is just suspense animation. Luck aims the roll at a "1 in X" in the
   map's list, chances fall off on both sides, and the last two catches are less likely to come again
   (`DinoRoll`, `Config/Catch` pick; GAME_SPEC section 8b).
   Common catches skip the counter. Tapping skips to the final card. Reveal numbers live in `Config/Reveal`,
   mutation and size odds in `Config/Catch`. Dinos are block stand-ins until the Blender models exist.
   After the reveal the player is teleported back to their own plot, next to its exit (`Config/Plot` homeInset).
4. **Plot** — caught dinos stand on your plot and earn $/s, anywhere on it (no grid). Backpack dinos sit in a
   hotbar (keys 1–0, best first); equipping one, or picking one up off the plot, sits it on the character's
   head at its real size, walking while they move and idling while they stand. While it's
   carried, a see-through dino follows the pointer over your plot (green = can go, red = can't) and a
   click places it there; the server checks the spot. New catches and Equip Best pick a free spot by
   themselves. The plot holds a limited number (start 10); extras go to backpack. Equip Best / Pick Up / Sell.
   Plots (bases) are 48 x 48, five in one row across the back of the arena, fenced, with a gate in the middle
   of the front edge. A blue upgrade sign on the front fence by the gate shows "🐾 10 › 12" and the price
   (green when the owner can afford it, red when not, a gold MAX bar at 20); clicking it buys +2 room (up to
   20), each upgrade 6x pricier. An owner plate floats high over each base: the owner's Roblox headshot, name
   and $/s (`BaseSigns`, `Config/Plot` ownerPlate). Free bases show no plate.
5. **Egg Shop** — buy better egg tiers with cash. Better egg = better roll table / more luck.

Loop: train → farther throws → more luck → rarer dinos → more cash → better eggs → rarer dinos.

## Biomes (throw order, near → far)

| # | Biome | Luck at end (target) |
|---|-------|----------------------|
| 1 | Forest | 2x |
| 2 | Desert | 5x |
| 3 | Swamp | 9x |
| 4 | Volcano | 14x |
| 5 | Frozen Peaks | 20x |
| 6 | Shadow Bog | 27x |
| 7 | The Abyss | 35x |
| 8 | Starfall Crater | 45x |
| 9 | Eclipse Temple | 1M (GAME_SPEC section 9 has the current luck plan) |
| 10 | Forbidden Library | 5M (world built; monsters later) |
| 11 | Midnight Carnival | 25M (world built; monsters later) |
| 12 | Clockwork Citadel | 100M (world and monsters in the game) |
| 13 | Thorn Kingdom | 500M (world and monsters in the game) |
| 14 | Spore Hollow | 2.5B (world and monsters in the game) |
| 15 | The Weeping Dark | 10B |

MVP ships biomes 1–3. Volcano (4) is built too, as the first update. Frozen Peaks (5) is built too, map and monsters, and so is Shadow Bog (6); The Abyss (7) and Starfall Crater (8) have their maps, their monsters come later (Starfall Crater's are in the game: `build_starfall_crater_monsters.py`, imported into `Assets.Dinos`, listed in `Config/Dinos`).

## Differentiators (things the reference doesn't have)

- Steer the egg mid-flight (tap left/right) to hit boost rings / dodge obstacles.
- Biome completion reward: x2 training XP for 15 minutes (no cash or luck from the Index).
- Server-wide announcement for catches rarer than 1 in 1M.
- Timed events (e.g. "Meteor Shower": 2x mutation chance for 10 min).

## Monetization (later, not MVP)

- Dinos priced as "X% of your best dino" (scales with progress).
- Server Luck 2x (15 min), cheap — benefits everyone.
- Gamepasses: x2 Cash, x2 Training.
- Free starter dino to get players into the shop. Gift button.

## MVP build order

1. Training station → Throw Power stat (saved with DataStore).
2. Throw lane + timing meter; distance = power × meter.
3. 3 biomes × 5 dinos, weighted roll × luck multiplier.
4. Reveal sequence (hangman letters + climbing "1 in X"). Spend real time here.
5. Plot holding 8 dinos placed freely + $/s income, fenced, with capacity upgrades at its sign (`Config/Plot`).
6. Egg Shop with one egg per map (15). (Buy any egg you can afford; each multiplies distance luck, counted against the egg made for the map it lands in, `Luck.forRoll`. Numbers live in `Config/Eggs`.)
7. Index: one scrolling list of every map, its picture on a card at the panel's left edge and its monsters beside it in
   rows of four, sorted by rarity, COMMON to MYTHIC (the boss), on real-model tiles (only maps near the screen hold live
   models); it opens at your farthest map; completing a biome gives x2 training XP for 15 minutes (`Config/Index`).
8. Robux shop: x2 Cash, x2 Training, Server Luck x2, four cash packs (10 min to 30 h of the plot's $/s
   without events, each with a minimum), four Throw Power packs (+100 to +10,000 power, saved on top of the
   training level) and a free starter dino (`Config/Shop`).
9. Timed events: one every 15 minutes for 5 minutes, taking turns: Double Luck (2x luck) and Ghost Rush (GHOST 10x
   likelier), from the server clock (`Config/Events`); an icon at the bottom right explains it on hover or tap.
10. Arena leaderboards (along the right-hand wall, seen from the platform): MOST DINOS (dinos caught), TOP MONEY (money earned) and LUCKIEST CATCH (rarest
    "1 in X"), top 10 across all servers, refreshed every minute (`Config/Leaderboards`).
11. Offline earnings: on rejoin, the plot pays 50% of its $/s for the time away (up to 8 hours, events not
    counted), with a "Your dinos earned $X while you were away!" message (`Config/Plot`).
12. Stalls: an EGG SHOP stall (blue/white awning) left of each base's gate, which only its owner sees, and one
    SELL stall (red/white) in the arena's open ground, each with a shopkeeper and a glowing pad that opens the
    Egg Shop / My Dinos while you stand on it (`Config/Hub`).
13. HUD restyle: square icon buttons with outlined labels (Index and Shop on the left, Dinos on the right; the
    Egg Shop opens only from its stall), big outlined ⚡ Throw Power and cash at the bottom left, hotbar along
    the bottom edge. Everything shrinks to fit short screens. While aiming and flying only Throw Power stays
    on screen (`HudStyle`).
14. UI redesign in Figma, "Throw Eggs for Dinosaurs - Game UI"
    (https://www.figma.com/design/PZ3emJUorfZBWQoLe1zCfv). Page "UI design v2" is current: Index with a
    map card per biome and that biome's dinos on rarity tiles, a sectioned Shop (Limited, egg, boosts,
    cash/power packs, passes, dino deals, free dino, GIFT) with a full-scroll frame, My Dinos, Egg Shop,
    Welcome Back, HUD, training and motion/colour notes. Source: `design/ui-mockups/build.py`.
    Dino, egg, map and pack art are Blender renders of blocky blueprint models in `assets/models`
    (`dino_blueprints.blend`; rebuild with `build_blueprints.py`, re-render with `render_thumbnails.py`).
    Shop items not in the game yet: dinos priced by % of best. Prism Egg and GIFT are built (GAME_SPEC).
    Built in-game with `UiKit` (panels, glossy buttons, tags, spinning model tiles, motion): Index, Shop
    (Boosts, Packs, Passes, Free), My Dinos (ON PLOT / BACKPACK tabs), Egg Shop, Welcome Back with CLAIM
    (offline earnings are held until claimed), HUD buttons, hotbar and training HUD. Monster tiles (Index, My
    Dinos, hotbar, the YOU CAUGHT banner, the free dino) show each monster's real imported model live in a
    ViewportFrame (`UiKit.monster`, built with `DinoModel` like the plot statues, mutation colours included);
    eggs, islands and shop art still use the block models (`ModelBlueprints`). Index and inventory design:
    Figma "Throw Eggs - Index & Inventory" (https://www.figma.com/design/dJTVmNiMckziDaSNCniPU5). The hatch reveal has the v2 look too
    (mock-ups 09-10 and 15-16b, reworked 2026-11-04): on catches rarer than 1 in 1,000 the luck label and a plain
    "1 in X" at the top, screen edges lit in the luck tier's colour, the name as white dashes filling in at the
    bottom, then a white flash and turning light rays behind the monster in its rarity's colour (no rings), and the
    final text straight on the screen (no card), and a "YOU CAUGHT!" banner on the plot after very rare ones. Catches of 1 in 10K
    or rarer get the lucky catch banner (mock-up 12) for the whole server (`LuckyBannerController`).
Not built yet: dinos priced by % of best. No rebirth: the reference game has none.

## Reference game notes

Seen in three gameplay recordings of the reference game (2026-11-01). These describe what the
reference does, not what we must build: our design above wins, and nothing here gets copied 1:1.
Exact formulas aren't visible in the recordings, so numbers are readings from the screen.

### Training
- Level 385 → 386 gave Throw Power +5 (1938 → 1943). XP needed grows about 2% per level (18.3M → 18.7M).
- While training: camera behind the bar, a STOP button, and a level/XP bar at the bottom.
- A cash upgrade pad next to the bar sells more XP per rep (shown as "$12Qi, +2.1M XP / rep").
- A tap bubble appears during training; tapping it gives a "x2!" rep and turns the character purple.

### Throw meter
- Vertical bar with 5 segments, red at the bottom and green at the top. A marker climbs it, labelled
  +1 up to +20, taking about 1 second. PERFECT! is at the very top and shows "+20 POWER".
- **Differs from our design:** the meter adds flat power instead of multiplying it, so +20 is about 1%
  at 2,000 power. Our distance = power × meter on purpose, so timing keeps mattering at every level.
  Our meter is vertical too, but has its own look (egg target) and a marker that slows near the top.
- Both throws recorded were perfect, so what a miss does is unknown.
- A full throw animation plays first, with letterbox bars. The camera then follows the item from behind.
- A "100x LUCK" Robux 9 offer sits on the throw screen, with a close button.

### Flight
- Luck climbs about 6x per second and slows just before landing. Throws reached 30.09x at 1,958 power
  and 32.58x at 2,223 power, so luck doesn't grow in proportion to power.
- Biomes are about 3x luck apart, evenly spaced. Ours are deliberately uneven (see Biomes).
- The biome name sits under the luck number. The landing raises a dust puff, then the screen dims.

### Reveal
Our step 4 target. In order:
1. Camera orbits the landed item. "tap to skip" shows on catches without a counter. (Corrected in
   `GAME_SPEC.md`: that "orbit" is the animal's walking view, and the full timing is there. Ours is built:
   `RevealWalk`, numbers in `Config/Reveal` `walk`, described in `GAME_SPEC.md` section 7.)
2. Blank letters appear and fill in out of order, with the model sweeping past in close-up.
3. The "1 in X" counter starts at 1 and rises about 25% every 1/8 second, with a short hold before
   the letters start. It isn't shown on every catch (a Whale and a Gold Winged Imp had none).
4. Each label comes with a color wash, ring pulses and more confetti. Label first seen at:

   | Label | Counter range where it first appears |
   |-------|--------------------------------------|
   | LUCKY! | 395–403 |
   | SUPER LUCKY! | 2,075–2,580 |
   | INSANE LUCK! | 9,608–12,530 |
   | LEGENDARY LUCK!! | 129,777–593,681 |
   | GODLY LUCK!!! | 11.1M–26.3M (clovers and gems rain down) |

5. Final card: mutation, name in its rarity color, size, $/s, "NEW BEST!" sticker, "tap to continue".
   Rare catches also get a glowing beam.
6. White flash back to the plot. Very rare catches keep a "YOU CAUGHT ... 1 in 26.3M" banner on screen
   for a while, and clovers burst around the player.

Mutations seen: Gold, Diamond, Emerald. Sizes seen: Big, Large, Monstrous, Huge. Colossal wasn't seen.

### Plot and backpack
- Recorded at 14 slots. A sign on the plot sells the next upgrade: 14 → 16 for $50Qi, so +2 slots.
- "My Animals" lists On Your Plot and Backpack (87–88 held), with Pick Up, Equip, Sell and Equip Best.
- Messages: "Your plot is full! (14 animals)" and "Your best 14 animals are on your plot!".
- A 10-slot bar at the bottom shows animals with their $/s and keys 1–0. Selecting one makes the
  character hold that animal (seen with slot 1: a bird walks next to the player). It looks like a
  Roblox-style hotbar of carried animals, which fits placing them freely on the plot.
- Animals stand freely on the plot, overlapping, not on slots. Each has a small label overhead with its
  size/mutation, name and $/s (e.g. "BIG $156Qi/s").
- The plot is fenced in with wooden fences. The upgrade sign stands at the plot's entrance:
  paw icon, "18 > 20" and a dark price bar "▲ $5Sp".
- After a catch, the player reappears inside their own plot, next to the exit.
- "My Animals" (the Animals button) slides in on the right side of the screen, not the centre: purple
  header with "18/18" in a paw badge, "ON YOUR PLOT 18/18", one row per animal (icon on a rarity-coloured
  tile, mutation above the name, size under it, $/s in green, blue PICK UP and red SELL), and a big
  orange EQUIP BEST at the bottom.
- "Your animals earn $X offline!" shows on join, so income keeps counting while offline.

### Shops and Index
- Throwable items are food. Tiers run to at least 17, with rarity names and prices shown on each card.
- "NEW FOOD UNLOCKED!" announces the next item. Buying equips it, and older items can be re-equipped.
- Hub stalls: a food shop pad and a SELL pad.
- Index: 38/140 unlocked. Each biome has 8 animals (12 in the last) and a progress bar, and missing ones
  show as "???" silhouettes. 140 implies 17 biomes; 16 names were readable. Any completion reward isn't shown.
- Robux shop, in order: limited Halloween animal (900% of best) and egg, Rainbow Egg, Server Luck 1x → 2x
  (15 min, R$19), cash packs, Throw Power packs (+5 to +500), a third pack type (+5 to +100, purpose
  unclear), x2 Cash (R$99), x2 Training Power (R$149), Giant Squid 300% (R$299), Woolly Mammoth 150% (R$199),
  and a free Hyena ($200/s). A Gift button stays on screen.
- Worth noting for our monetization: Throw Power packs and the 100x Luck offer aren't in our list yet.

### Look and feel
From the owner's screenshots and a live look at the game (2026-11-02). Style to aim for in our own way,
not to copy: chunky, bright and readable from far away.
- Everything is built from big stud-textured blocks: checkered green grass,
  brown dirt walls with grass hanging over the top, wooden fences, pumpkins as seasonal decoration.
- HUD: big square icon buttons with a dark rounded frame and a bold outlined label under the icon:
  Index (book) and Shop (basket) on the left, Animals (paw) on the right. Bottom left: muscle icon with
  Throw Power in big blue outlined numbers (and a gear icon next to it), cash-stack icon with cash in big
  green outlined numbers. Spending shows a red "-$X" floating up from the cash.
- Fonts are heavy, rounded and outlined in black, with gradient fills on titles (yellow names, green $/s).
- Hub: a SELL stall (red/white striped awning, NPC behind the counter, red dashed circle on the ground)
  and the food shop stall (blue/white awning, glowing cyan circle pad).
- Hub leaderboards, three boards side by side: MOST ANIMALS (animals caught), TOP MONEY (total money
  earned), LUCKIEST CATCH (rarest "1 in X"). Top 10 each, top 3 highlighted in orange, "Updates every minute".
- Food Shop panel: purple header, cards scroll sideways, each with the name, rarity word (e.g. "Supreme"),
  a 3D preview on a green gradient, a "Tier 17" bar and a red price button.
- Robux Shop panel: orange header, big featured cards ("BEST VALUE!" tag, "900% OF YOUR BEST ANIMAL",
  green Robux button), an egg row ("Up to 900% of your best animal!", Buy 1) and a GIFT! button.
- Throw screen: every other HUD element hides except Throw Power. The meter sits in the middle of the
  screen with "TAP TO THROW!" under it; the marker's label shows the bonus (+14). The 100x LUCK offer is
  top right. The camera is behind the player, looking down the corridor between tall dirt walls.
- Far biomes get their own colour and props (e.g. a neon purple biome with glowing crystals and towers).
  "tap to skip" sits at the bottom while the camera looks at the landing.
- Reveal text sits at the bottom centre: white outlined letters with blanks ("W__ERN"), then the full name
  with a yellow gradient, $/s in green under it, and "tap to continue". The dino stands on the ground
  with the thrown item lying next to it.
- Training: two white pillars with coloured rings and a bar, a big "LEVEL UP! Throw Power +5" over the
  player, a purple tap bubble "x2", a red STOP button and a long "Level 641 507M/1.81B" bar at the bottom.
