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
	-- standardScale); scale multiplies that standard size, up to 8x. Each tier is about 1.5x the one below, them likelier (luckPower).
	-- so even the rarest towers over its base without filling the screen. Luck makes them likelier (luckPower).
	sizes = {
		{ id = "UnitOfDoom", name = "UNIT OF DOOM", chance = 9787, incomeMultiplier = 50, scale = 8 },
		{ id = "PlanetSized", name = "PLANET-SIZED", chance = 2500, incomeMultiplier = 20, scale = 5 },
		{ id = "MegaChonk", name = "MEGA CHONK", chance = 600, incomeMultiplier = 8, scale = 3.2 },
		{ id = "Chonker", name = "CHONKER", chance = 150, incomeMultiplier = 4, scale = 2.2 },
		{ id = "AbsoluteUnit", name = "ABSOLUTE UNIT", chance = 40, incomeMultiplier = 2.5, scale = 1.6 },
		{ id = "Thicc", name = "THICC", chance = 10, incomeMultiplier = 1.5, scale = 1.25 },
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
	luckyHits = {
		{ multiplier = 500, minOneIn = 100000000 }, -- 1 in 100 million or rarer: GODLY!, sometimes IMPOSSIBLE!
		{ multiplier = 100, minOneIn = 1000000 }, -- 1 in a million or rarer: GODLY!
		{ multiplier = 50, minOneIn = 100000 }, -- the daily reward's: 1 in 100,000 or rarer, LEGENDARY!
	},

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
