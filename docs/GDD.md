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
4. **Plot** — caught dinos stand on your plot as big statues and earn $/s. Limited slots (start 8, upgradeable).
   Extras go to backpack. Equip Best / Pick Up / Sell.
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
- Rebirth: reset Throw Power for a permanent multiplier.

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
5. Plot with 8 slots + $/s income.
6. Egg Shop with 5 tiers.
Then: Index, Robux shop, events, rebirth.

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
- A 10-slot bar at the bottom shows animals with their $/s. Its purpose isn't clear from the recordings.

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
