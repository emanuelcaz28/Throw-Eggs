-- Extra rolls on every catch. chance = "1 in X", incomeMultiplier multiplies the dino's $/s.
-- The "1 in X" a player sees is dino chance * mutation chance * size chance.
-- Placeholder numbers; tune during playtesting.
return {
	-- Rarest first: the first one that hits wins, so a dino gets at most one of each.
	-- Colour mutations recolour the skin and leave the face alone. Each needs a colour that's easy to
	-- tell from the others, on the model and in the UI text.
	mutations = {
		{ id = "Ghost", name = "GHOST", chance = 20000, incomeMultiplier = 100, color = Color3.fromRGB(235, 242, 255) },
		{ id = "Shadow", name = "SHADOW", chance = 8000, incomeMultiplier = 50, color = Color3.fromRGB(20, 14, 48) },
		{ id = "Amethyst", name = "AMETHYST", chance = 3000, incomeMultiplier = 30, color = Color3.fromRGB(170, 90, 255) },
		{ id = "Bubblegum", name = "BUBBLEGUM", chance = 1200, incomeMultiplier = 18, color = Color3.fromRGB(255, 120, 200) },
		{ id = "Emerald", name = "EMERALD", chance = 500, incomeMultiplier = 12, color = Color3.fromRGB(60, 210, 110) },
		{ id = "Diamond", name = "DIAMOND", chance = 200, incomeMultiplier = 6, color = Color3.fromRGB(130, 215, 255) },
		{ id = "Ruby", name = "RUBY", chance = 80, incomeMultiplier = 3.5, color = Color3.fromRGB(230, 40, 70) },
		{ id = "Gold", name = "GOLD", chance = 30, incomeMultiplier = 2, color = Color3.fromRGB(255, 205, 70) },
	},
	-- Size mutations are the only way a monster grows past its biome's standard size (Config/Biomes
	-- standardScale); scale multiplies that standard size, with no cap.
	sizes = {
		{ id = "UnitOfDoom", name = "UNIT OF DOOM", chance = 10000, incomeMultiplier = 50, scale = 5 },
		{ id = "PlanetSized", name = "PLANET-SIZED", chance = 2500, incomeMultiplier = 20, scale = 3.5 },
		{ id = "MegaChonk", name = "MEGA CHONK", chance = 600, incomeMultiplier = 8, scale = 2.6 },
		{ id = "Chonker", name = "CHONKER", chance = 150, incomeMultiplier = 4, scale = 2 },
		{ id = "AbsoluteUnit", name = "ABSOLUTE UNIT", chance = 40, incomeMultiplier = 2.5, scale = 1.6 },
		{ id = "Thicc", name = "THICC", chance = 10, incomeMultiplier = 1.5, scale = 1.3 },
	},
	-- Luck also makes mutations and sizes likelier, but much more gently than it shifts which dino
	-- hatches: their chances are multiplied by luck ^ luckPower. At 0.4, 2x luck gives 1.3x,
	-- 45x gives 4.6x and 300x (far biome, best egg, every boost) gives 9.8x.
	luckPower = 0.4,
	-- No single mutation or size is ever likelier than this, however much luck and event boost.
	maxChance = 0.5,

	-- Size ids in saves from before the six sizes, and what they became.
	renamedSizes = { Big = "Thicc", Large = "AbsoluteUnit", Huge = "Chonker", Colossal = "MegaChonk" },
}
