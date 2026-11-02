# Throw Eggs for Dinosaurs — Game Design Doc

Genre reference: "Throw Food for Animals" (train → throw → RNG catch → plot income).
Familiarity hook: eggs + dinos, borrowing recognition from "Steal an Egg"-style games.
Rule: same genre, our own names, models, UI and numbers. Nothing copied 1:1.

## Core loop

1. **Train** — stand at a training station (pull-up bar). Auto-reps give XP; level-ups raise **Throw Power**.
2. **Throw** — step on the throw lane → egg meter: a marker swings up and down a vertical tube with 10 levels
   and slows near the top. Level 10, the top step, is PERFECT and gives the biggest throw.
   The equipped **egg** flies down one long corridor through biomes. Distance = Throw Power × the level's bonus.
   A **Luck multiplier** grows with distance (shown live, top of screen).
3. **Hatch / reveal** — the egg lands in a biome and hatches. Dino name fills in letter by letter
   (hangman style) while a "1 in X" counter climbs. Labels escalate: LUCKY! → SUPER LUCKY! → INSANE → LEGENDARY → GODLY.
   Final card: mutation (Gold / Diamond / Emerald…), size (Big / Large / Huge / Colossal), $/s, "NEW BEST!".
   The roll is decided on landing; the counter is just suspense animation.
   Common catches skip the counter. Tapping skips to the final card. Reveal numbers live in `Config/Reveal`,
   mutation and size odds in `Config/Catch`. Dinos are block stand-ins until the Blender models exist.
   After the reveal the player is teleported back to their own plot, next to its exit (`Config/Plot` homeInset).
4. **Plot** — caught dinos stand on your plot and earn $/s, anywhere on it (no grid). Backpack dinos sit in a
   hotbar (keys 1–0, best first); equipping one makes the character carry a small copy of it. While it's
   carried, a see-through dino follows the pointer over your plot (green = can go, red = can't) and a
   click places it there; the server checks the spot. New catches and Equip Best pick a free spot by
   themselves. The plot holds a limited number (start 8); extras go to backpack. Equip Best / Pick Up / Sell.
   Plots are fenced, with a gate in the middle of the front edge. An upgrade sign on legs just inside the
   gate shows "8 > 10" and the price; clicking it buys +2 room (up to 30), each upgrade 6x pricier.
5. **Egg Shop** — buy better egg tiers with cash. Better egg = better roll table / more luck.

Loop: train → farther throws → more luck → rarer dinos → more cash → better eggs → rarer dinos.

## Biomes (throw order, near → far)

| # | Biome | Luck at end (target) |
|---|-------|----------------------|
| 1 | Fern Valley | 2x |
| 2 | Dry Plains | 5x |
| 3 | Swamp | 9x |
| 4 | Volcano Foothills | 14x |
| 5 | Ice Age Tundra | 20x |
| 6 | Tar Pits | 27x |
| 7 | Deep Sea Trench | 35x |
| 8 | Meteor Crater | 45x |

MVP ships biomes 1–3 only.

## Differentiators (things the reference doesn't have)

- Steer the egg mid-flight (tap left/right) to hit boost rings / dodge obstacles.
- Biome completion rewards (permanent luck/cash boost per completed biome in the Index).
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
6. Egg Shop with 5 tiers. (Buy any egg you can afford; each multiplies distance luck. Numbers live in `Config/Eggs`.)
7. Index: every dino by biome; completing a biome gives a permanent bonus (`Config/Index`).
8. Robux shop: x2 Cash, x2 Training, Server Luck x2 and a free starter dino (`Config/Shop`).
9. Timed events: every server runs one at a time (Meteor Shower 2x mutations, Growth Spurt 2x sizes,
   Gold Rush 2x cash), 10 min each with a 20 min break, shown with a top-right timer (`Config/Events`).
Not built yet: dinos priced by % of best, Throw Power packs and the Gift button. No rebirth: the reference game has none.

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
1. Camera orbits the landed item. "tap to skip" shows on catches without a counter.
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
