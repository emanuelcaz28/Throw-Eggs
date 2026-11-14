-- Extra rolls on every catch. chance = "1 in X", incomeMultiplier multiplies the dino's $/s.
-- The "1 in X" a player sees is the real chance of that monster, colour and size together (DinoStats.describe).
-- The rarest of each have odd chances (19,683, 9,787) so no "1 in X" comes out round [Owner, 2026-11-06].
-- Placeholder numbers; tune during playtesting.
return {
	-- Rarest first: the first one that hits wins, so a dino gets at most one of each.
	-- Colour mutations recolour the skin and leave the face alone. Each needs a colour that's easy to
	-- tell from the others, on the model and in the UI text.
	mutations = {
		{ id = "Ghost", name = "GHOST", chance = 19683, incomeMultiplier = 100, color = Color3.fromRGB(235, 242, 255) },
		{ id = "Shadow", name = "SHADOW", chance = 8000, incomeMultiplier = 50, color = Color3.fromRGB(20, 14, 48) },
		{ id = "Amethyst", name = "AMETHYST", chance = 3000, incomeMultiplier = 30, color = Color3.fromRGB(170, 90, 255) },
		{ id = "Bubblegum", name = "BUBBLEGUM", chance = 1200, incomeMultiplier = 18, color = Color3.fromRGB(255, 120, 200) },
		{ id = "Emerald", name = "EMERALD", chance = 500, incomeMultiplier = 12, color = Color3.fromRGB(60, 210, 110) },
		{ id = "Diamond", name = "DIAMOND", chance = 200, incomeMultiplier = 6, color = Color3.fromRGB(130, 215, 255) },
		{ id = "Ruby", name = "RUBY", chance = 80, incomeMultiplier = 3.5, color = Color3.fromRGB(230, 40, 70) },
		{ id = "Gold", name = "GOLD", chance = 30, incomeMultiplier = 2, color = Color3.fromRGB(255, 205, 70) },
	},
	-- Size mutations are the only way a monster grows past its biome's standard size (Config/Biomes
	-- standardScale); scale multiplies that standard size, up to 10x. Luck makes them likelier (luckPower).
	-- Specials' RESIZE offers the same scales (DinoStats.resizes).
	-- [Owner, 2026-11-07: the big sizes were way too big; was 1.25, 1.6, 2.2, 3.2, 5, 8.]
	-- [Owner, 2026-11-08: Planet-Sized x13 and Unit of Doom x18; were 3.3 and 4.5.]
	-- [Owner, 2026-11-09: still too big on the bases, and the list jumped unevenly; now an even ramp, then the top
	-- three set by the owner: 1.2, 1.8, 2.7, 5, 7.5, 10.]
	-- How long a plain first-map monster is, in studs: its longest side, whichever way that runs (a player is about 5
	-- tall). Every model is brought to this before its map's standard size and its size mutation [Owner, 2026-11-09].
	standardLength = 10,
	sizes = {
		{ id = "UnitOfDoom", name = "UNIT OF DOOM", chance = 9787, incomeMultiplier = 50, scale = 10 },
		{ id = "PlanetSized", name = "PLANET-SIZED", chance = 2500, incomeMultiplier = 20, scale = 7.5 },
		{ id = "MegaChonk", name = "MEGA CHONK", chance = 600, incomeMultiplier = 8, scale = 5 },
		{ id = "Chonker", name = "CHONKER", chance = 150, incomeMultiplier = 4, scale = 2.7 },
		{ id = "AbsoluteUnit", name = "ABSOLUTE UNIT", chance = 40, incomeMultiplier = 2.5, scale = 1.8 },
		{ id = "Thicc", name = "THICC", chance = 10, incomeMultiplier = 1.5, scale = 1.2 },
	},
	-- Luck also makes mutations and sizes likelier, but much more gently than it changes which monster
	-- hatches: their chances are multiplied by luck ^ luckPower, the same luck as the monster roll
	-- (Config/Luck forRoll). At 0.4, 5x luck (a map's far end) gives 1.9x, 500x (a x100 lucky throw
	-- there) gives 12x and 2,500x (a x500 one) gives 23x.
	luckPower = 0.4,
	-- No single mutation or size is ever likelier than this, however much luck and event boost.
	maxChance = 0.5,

	-- Lucky throws are a guaranteed hit [Owner, 2026-11-06: "500x must be a guaranteed massive HIT", plain luck gave
	-- 1 in 1k catches]. The monster is rolled with the throw's luck as usual, then its colour and size are picked from
	-- every combination that makes the whole catch at least this rare ("1 in X", DinoStats.describe), each as likely as
	-- it really is, so the result varies: usually just past the line, now and then far past it. Biggest first; a
	-- throw uses the first line its multiplier reaches.
	-- minRarity: no monster below this rarity word (1 Common, 2 Uncommon, 3 Rare, 4 Epic, 5 Legendary, Config/RarityLadder).
	-- A map with no monster that rare (maps 1 and 2 top out at Epic) gives its rarest word instead, with
	-- shortMapSizeBoost below [Owner, 2026-11-08: "100% chance for an epic for the first maps and waaay higher chances
	-- of a big size monster"]. minPlace: and no monster more common than this place in its map's list; maxPlace: and none
	-- rarer than this place.
	-- [Owner, 2026-11-13] Plain luck stays weak so the paid throws are worth buying, and a paid throw must be worth the
	-- same on every map. From map 6 on a x100 paid only 5x to 6x the map's best normal monster (160x on map 1), less than
	-- the next map's free first catch, and gave a prize monster 4% of the time. So x100 and x500 now always give one of
	-- the map's two prizes (minPlace 7: its 7th or 8th, Config/Dinos): about 16x and 90x the best normal monster on
	-- every map from the 4th on. The daily x50 paid about 2x and was often a common monster in a rare colour; it is
	-- now always the map's best normal monster (its 6th) with a colour or a size, about 3x, and never a prize: prizes
	-- are what Robux buys.
	-- [Owner, 2026-11-14] The end-game maps' 9th to 12th (Config/Dinos apex; Nightmare, Doomsday, Oblivion, Unknown) are
	-- what the paid throws chase, "of course free players can get it but not easy":
	--   x100 stops at the 9th (maxPlace 9): about 73% the 7th, 22% the 8th, 6% a Nightmare, never anything above it.
	--   x500 reaches all of them, and its own `falloff` (0.5 against the roll's 1, Config/Catch pick) leans it to the
	--   rare end: about 48% the 7th, 26% the 8th, 13.6% Nightmare, 6.8% Doomsday, 3.3% Oblivion, 1.7% Unknown (1 in 59).
	--   On 8-monster maps that makes a x500 65% the 7th and 35% the 8th (was 77 / 23); x100 is unchanged there.
	--   Free: a plain throw gives one about 1 in 18,000 at a map's far end (1 in 97,000 at its start; the Unknown 1 in
	--   1.6 million). The guarantees never give one, but the end-game streak does: every 300 throws on such a map
	--   without one, a Nightmare or a Doomsday (Config/Hooks apexStreak). The real free
	--   way is the daily reward's day-7 x500: one in four is an apex monster, about one a month.
	--   [Owner, 2026-11-14] The x500's falloff = 0.5 is held back with the apex monsters (hidden in Config/Dinos) for
	--   the next update: until then a x500 stays 77% the 7th, 23% the 8th. Add it back to the x500 line on release.
	-- colourAndSize: always a colour and a size, never "No colour" or "Normal size" [Owner, 2026-11-07: x100 and
	-- x500 must give 0% Common to Epic, no colour and normal size].
	luckyHits = {
		{ multiplier = 500, minOneIn = 100000000, minRarity = 5, minPlace = 7, colourAndSize = true }, -- 1 in 100 million or rarer: GODLY!, sometimes IMPOSSIBLE!
		{ multiplier = 100, minOneIn = 1000000, minRarity = 5, minPlace = 7, maxPlace = 9, colourAndSize = true }, -- 1 in a million or rarer: GODLY!
		{ multiplier = 50, minOneIn = 100000, minPlace = 6, maxPlace = 6 }, -- the daily reward's: the map's 6th, 1 in 100,000 or rarer, LEGENDARY!
	},
	-- On a map that falls short of a lucky throw's minRarity, each size's chance is also multiplied by its own
	-- "1 in X" to this power. At 1 every size is as likely as the others: on map 1 a x100 gives Unit of Doom about
	-- 1 in 6 (0.1% without), and a x500 gives Mega Chonk or bigger about 2 times in 3.
	shortMapSizeBoost = 1,

	-- Which monster comes (DinoRoll, docs/GAME_SPEC.md section 8b). Luck aims at a "1 in X": the map's
	-- commonest monster's odds times the roll's luck (Config/Luck forRoll), so 50x luck on the Forest
	-- (commonest 1 in 2) aims at 1 in 100. A monster at the aim comes most; each one further away, rarer or
	-- more common, is that many times less likely (to the power falloff). So 10x luck makes a monster rarer
	-- than the aim 10x likelier, and monsters far more common than the aim fade out: you've outgrown them.
	-- The aim never goes past topAim of the way from the second rarest monster (0) to the rarest (1): at 0.5,
	-- the two rarest come about as often as each other with huge luck (x500), so even that is never a sure thing.
	-- Like the reference game, the last monster caught is much less likely to come again and the one before
	-- it a bit less, so a run of throws doesn't keep hatching the same monster.
	pick = {
		falloff = 1,
		topAim = 0.5,
		repeatPenalty = { 200, 2.5 }, -- the last catch is 200x less likely, the one before it 2.5x
	},

	-- Size ids in saves from before the six sizes, and what they became.
	renamedSizes = { Big = "Thicc", Large = "AbsoluteUnit", Huge = "Chonker", Colossal = "MegaChonk" },
}
