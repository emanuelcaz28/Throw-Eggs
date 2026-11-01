# Throw Eggs for Dinosaurs — Game Design Doc

Genre reference: "Throw Food for Animals" (train → throw → RNG catch → plot income).
Familiarity hook: eggs + dinos, borrowing recognition from "Steal an Egg"-style games.
Rule: same genre, our own names, models, UI and numbers. Nothing copied 1:1.

## Core loop

1. **Train** — stand at a training station (pull-up bar). Auto-reps give XP; level-ups raise **Throw Power**.
2. **Throw** — step on the throw lane → timing meter ("TAP TO THROW!"), perfect tap = bonus power.
   The equipped **egg** flies down one long corridor through biomes. Distance = Throw Power × meter result.
   A **Luck multiplier** grows with distance (shown live, top of screen).
3. **Hatch / reveal** — the egg lands in a biome and hatches. Dino name fills in letter by letter
   (hangman style) while a "1 in X" counter climbs. Labels escalate: LUCKY! → INSANE → LEGENDARY → GODLY.
   Final card: mutation (Gold / Diamond / Emerald…), size (Big / Large / Huge / Colossal), $/s, "NEW BEST!".
   The roll is decided on landing; the counter is just suspense animation.
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
