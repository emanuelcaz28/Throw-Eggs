# Keeping Players: Build Plan

Written 2026-11-07. **Nothing here is built yet.** `docs/GAME_SPEC.md` still wins over this file. When a step is built, its
details go into the spec and the step gets ticked here. One step per prompt, in this order.

## The goal

**[Owner, 2026-11-07]** A game that finishes in a few hours is not good. If a free player can complete it in half a day, it
will die quickly. The game needs a hook that keeps players for a long time and brings them back every day.

Three things are wrong today:

1. **Nothing comes after world 15.** Distance stops at 16,500 studs, so training has no purpose once you get there.
2. **Most catches stop mattering.** Late on, almost every throw is weaker than what's already on the base.
3. **Nothing lasting to earn.** Finishing a world in the Index gives a 15-minute boost, and the daily reward lasts one throw.

The answer has two halves: a longer climb that still feels quick, and something to do after it that has no end.

## Targets

| What | Today | Target | Where it comes from |
|---|---|---|---|
| Average free player reaches world 15 | 20.6 h of play, 21 days (built) | **About 20 h, 3 weeks** | Simulated, see step 1 |
| Keen player has things to do after world 15 | Nothing | **Months** | To be tuned in step 3 |
| Squats per bar, from about world 8 | 20 to 26 (built) | **15 to 30** | Gemini's idea, judged by feel in step 1 |
| Day 1 / day 7 / day 30 retention | Unknown, not launched | **20% / 8% / 4%** | Near GameAnalytics' top 1% of Roblox games (22% / 9% / 4.7%) |

The retention numbers are something to measure against after launch, not a promise. Gemini's 42 to 50% for day 1 had no
source and is about double what the top 1% of games reach.

## Decisions needed from the owner

These would have broken rules the owner set earlier. All three are settled.

| # | Rule today | Change it to | Recommendation | Needed by |
|---|---|---|---|---|
| 1 | Only size mutations make a monster bigger than its map's standard | Feeding can make it bigger too | **Decided: yes** (owner, 2026-11-07) | Step 4 |
| 2 | Completing a world gives no cash or luck, only a timed XP boost | Permanent rewards for Index stars | **Decided: no** (owner, 2026-11-07) | Step 5, skipped |
| 3 | A base holds 20 monsters at most | More than 20 | **Stays at 20.** Step 5 is skipped | Step 5, skipped |

Already decided, so not up for change: passes stay full x2 on every map, the throw stays long enough to see the worlds
(flight 2 to 8 seconds), the reveal isn't cut, and there's no trading.

## Before launch

### Step 1. Longer climb with quick bars (small)
**Done 2026-11-07.** The owner played it and said it feels right. Simulation and a Studio test match the table.

The owner found 80 squats a bar too hard and 25 too fast. That mixed up two things: how long a **bar** takes and how long a
**world** takes. They can be set apart, so bars stay quick while worlds take longer.

- Slow the climb: `xpPerMap` 1.85, `hardMapStep` 3.5, `xpPerLateMap` 2.1.
- Split bars: from about world 6, divide both a bar's XP and its power by the same number, so a bar stays at 15 to 30 squats. The
  speed of progress doesn't change, and x2 Training and x2 Power still give exactly double. Throw Power may need to allow
  decimals, or a bar's gain would round down to nothing.

Simulated (play time to world 15, days at each player's daily time):

| Player | World 10 | World 15 | Days | Longest late world |
|---|---|---|---|---|
| Casual, 20 min a day | 3 h | 30.7 h | 90 | 11.2 h |
| Average, 1 h a day | 2 h | 20.8 h | 21 | 7.6 h |
| Grinder, 6 h a day | 1.1 h | 10.9 h | 2 | 3.9 h |
| Both x2 passes | 42 min | 6.4 h | 7 | 2.1 h |
| All 3 passes, keen | 27 min | 4.8 h | 2 | 1.7 h |

**Done when:** the owner has played worlds 8 to 12 and says it feels right, and `tools/pace_sim.luau` matches the table.

### Step 2. Test the money rework in the simulation (small, no game changes)
**Done 2026-11-07. Result: skip it for now.** Time saved by x2 Cash for an average player, 5 runs each:

| Economy | Average to world 15 | With x2 Cash |
|---|---|---|
| Today (income x100 a world, rack x50) | 20.7 h | 19.5 h (6%, close to run-to-run noise) |
| Income x100, smaller rack steps at x115 a world | 23.2 h | 22.4 h (3%, noise) |
| Income x3.5, rack x4 a world, $5,000 start | 12.3 h | 11.1 h (10%) |
| Income x3.5, rack x5 a world, $500 start | 13.8 h | 11.1 h (20%) |

So the x100 income jump really is what makes cash weak, and smaller rack steps alone don't fix it. Gemini's x3.5 works, but saves
about 3 hours rather than its 4.5, and needs every monster's income and every price rewritten. It also loses the owner-approved
moment where a new world's first good catch multiplies income at once. Step 4 gives cash a purpose far more cheaply, so skip this
unless x2 Cash needs to be worth more after launch. All the x3.5 runs would also need the XP numbers retuned.

Money barely affects progress. Income jumps x100 each world, which seems to be why x2 Cash saves almost nothing. Gemini
suggests x3.5 a world with rack upgrades costing x4. Its own numbers for that actually came to x11, so they need redoing.

- Simulate income at about x3.5 a world, with five smaller rack steps per world.
- Find out whether money can become a real part of progress, and whether x2 Cash starts to matter.

**Done when:** there's a clear yes or no. If yes, it becomes its own large step, because it touches every monster's income
and every egg, base and cash pack price. If no, skip it.

### Step 3. The Deep End past world 15 (large)
**Built 2026-11-07, imported and play-tested on desktop and at phone size.** The world's 14 models are from Blender (`assets/models/fbx/17_DeepEnd/Props/`), 423 props in play. It's what's behind the Last Door: the egg bursts through it with a flash,
which beats the broken wall first proposed. Simulated play time to Depth 1, 5 and 10: average 36 h, 67 h, 219 h; keen 29 h, 55 h,
176 h; all 3 passes 8 h, 15 h, 48 h. Not tested: a real player earning their way there, and a real phone.

The main hook. Past 16,500 studs the corridor opens into a bottomless Abyss, so distance never ends. Each time your throw
doubles, you reach a new **Depth Tier**, and deeper tiers make rare colours and sizes likelier.

First build the smallest version and test it:
- A real place for the egg to land and the reveal to happen. Gemini said no new art is needed, but the monster still has to walk
  to the egg somewhere.
- Depth tiers on the server, with the flight kept close to 8 seconds, and a new global board for deepest depth.
- Which monsters come from the Abyss, and their odds. Any bought luck must keep showing real odds.

**Correction, 2026-11-07:** the earlier estimate here (tier 6 at about 200 h) is out of date. Since step 1, a bar at world 15 gives
about +2 power, or roughly 150 power an hour of play. Doubling distance from there would take about 70 hours for the first tier
alone. So tiers can't be "each doubling of distance". Instead they need their own power steps, starting about 3 to 5 hours apart
and growing by about a third each time, tuned in the simulation. Six to ten tiers then give a keen player months of goals.

**The design, approved 2026-11-07:**
- **Name: The Deep End.** Gemini's "Titan Abyss" clashes with world 7, The Abyss.
- **Look:** the end wall of The Weeping Dark breaks open onto a huge pit, and the egg drops to a stone floor far below. It's built
  as a 16th world with `docs/MAP_RECIPE.md`, so the landing and the reveal work the way they do everywhere else.
- **Catches:** the 40 monsters of worlds 11 to 15, no new models, with deeper tiers making rare colours and sizes likelier. All
  120 would mostly give worthless catches, because income grows x100 a world.
- The egg always lands in the same real place. Depth is a number the server works out, so nothing flies far from the map.

**Done when:** a throw past world 15 works from start to finish on desktop and at phone size, and the simulation shows the tier times.

### Step 4. Feeding duplicates (medium)
**Built 2026-11-07, play-tested on desktop, panels checked at phone size.** The owner chose yes on decision 1: feeding makes monsters bigger.
Numbers in `Config/Chonk`: level 50 at most, +5% income a level (x3.5), +2% size a level (x2), one food per monster, three for the same
kind, each costing 30 seconds of the fed monster's income, and no training bonus, so step 1's pacing is untouched. Each level needs
one more food than the last: 1,275 in all, roughly 7 to 8 hours of throwing for one monster and far more for a whole base. Not
tested: a real phone with several level 50 giants, or real touch on the buttons.

Extra catches get fed to a favourite monster with some cash, raising its **Chonk Level**. Every throw now matters, money has
somewhere to go late in the game, and your favourite monster grows until it spills over the fence.

Gemini's numbers would break the game, so these need limits:
- Income adds up rather than compounds. Starting point: +5% a level, level 50 at most.
- Any training bonus counts only the best monster, or has a low cap. Gemini's version comes to 21x training.
- Size grows by a capped amount, and stays under Roblox's limit of about 2,000 studs a part.
- Giant monsters mustn't block the rack, the pads or taps.

**Done when:** tested on phone size with the biggest monsters, and the simulation shows the bonus doesn't undo step 1.

### Step 5. Index stars and picking a world: skipped
**[Owner, 2026-11-07]** Not wanted. The Index keeps its timed x2 XP boost, with no stars and no permanent rewards, and there's no way to pick a target world.

### Step 6. A daily reason to return (small)
**Built 2026-11-07, tested on desktop, panel checked at phone size.** The reward for the tasks is the timed x2 XP boost. A 🎁 Daily button was added, as the panel could only open by itself before. Not tested: a real midnight reset, or a real PERFECT counting, though it's the same counter as bubbles and catches.

- **The streak pauses instead of resetting** when a day is missed. Rewards stay as they are: x50 on days 1 to 6, x500 on day 7.
- **Three daily tasks**, about 15 minutes in all, for a 15-minute boost. For example: 5 Perfects, 25 bubbles, 10 catches in your best
  world. Gemini's 15 Perfects would take about 98 throws.
- Not Gemini's three overnight eggs at x500. That gives away what the shop sells.

**Done when:** tasks reset every day, save properly, and read clearly on a phone.

### Step 7. Equip Best notifications (small)
**Built 2026-11-07, tested on desktop.** **[Owner]** Swap Weakest isn't wanted, because Equip Best already does that job. Instead EQUIP BEST always says what happened: "Best monsters equipped! +$X/s", or "Your best monsters are already on your base", when nothing moves.

### Step 8. Launch checks
Checked 2026-11-07:
- **Paid items:** the Prism Egg's odds add up to 100% and lucky throws have DETAILS with live odds, Depth included. Server Luck was missing the regional check and its numbers, both fixed. Roblox's page doesn't say if the check must cover luck boosts, so we treat it as yes. Free daily lucky throws need no odds. Feeding has no randomness.
- **Giants:** no monster part collides, so they can't block walking, the rack or the pads. A tap on a giant still picks it up, and a giant can hide what's behind it.
- **Corridor size:** 31,593 corridor parts are always loaded for every player (`Persistent`). The Deep End is 1,673 of them. This is the biggest phone risk.

Still needs a person:
- [ ] Play on a real phone, ideally an older one: does it load, does it crash, is the flight smooth? If not, the fix is to stop keeping the whole corridor loaded.
- [ ] One real Robux purchase of each kind.
- [ ] A real gift between two accounts.
- [ ] Touch on the Index and on FEED, on a real phone.
- [ ] Open the Creator Dashboard and confirm Retention shows.

**First week after launch, once a day:**
- Day 1 / day 7 retention against 20% / 8%. Below 10% on day 1 means look at the first 10 minutes first.
- Average session length, and the console's error report.
- Crash or low-memory reports, split by phone and desktop.
- Which world most players stop at. A sudden drop means a wall there.
- What people buy. Nobody buying a pass means check its card, not its price, first.

## After launch

Decide these from real numbers, in about this order:

1. **Rotating bounties**: an NPC asks for specific catches every 4 hours, for permanent upgrades.
2. **Weekly leaderboards** that reset, so new players have a chance.
3. **Regular updates**: new events and limited Abyss monsters often, and a new side world about every two weeks. New
   worlds shouldn't go into the main corridor, as that upsets the pacing.
4. **Multi-Throw**: two or three eggs in one throw. More catches without shortening the cinematic part.
5. **Weather Totems and Reroll Serums**: good repeat purchases, but both fall under Roblox's paid random item rules.
6. **Rebirth ("Meteor Extinction")**: rejected on 2026-11-02. Only worth reopening if real players run out of things to do.

## Not doing

- Auto-Throw or a wider Perfect zone for Robux: it sells away the game's one skill.
- Weakening passes, or making them worth less in late worlds.
- Shortening the throw or skipping reveals. The reveal already has tap to continue.
- Changing the meter to 0.85x to 1.35x: timing should keep mattering.
- Moving bases along the corridor, trading, bigger servers, and locking worlds behind rare catches.

## Unknowns

All hours here are simulated players with guessed habits, not real ones. The Abyss times are a rough sum, not a simulation.
Whether any of this keeps people is unknown until real players try it, which is why launch data decides the later steps.
