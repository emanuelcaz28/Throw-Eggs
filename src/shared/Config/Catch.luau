-- Extra rolls on every catch. chance = "1 in X", incomeMultiplier multiplies the dino's $/s.
-- The "1 in X" a player sees is dino chance * mutation chance * size chance.
-- Placeholder numbers; tune during playtesting.
return {
	-- Rarest first: the first one that hits wins, so a dino gets at most one of each.
	mutations = {
		{ id = "Emerald", name = "EMERALD", chance = 500, incomeMultiplier = 15, color = Color3.fromRGB(120, 226, 140) },
		{ id = "Diamond", name = "DIAMOND", chance = 100, incomeMultiplier = 5, color = Color3.fromRGB(130, 215, 255) },
		{ id = "Gold", name = "GOLD", chance = 20, incomeMultiplier = 2, color = Color3.fromRGB(255, 205, 70) },
	},
	sizes = {
		{ id = "Colossal", name = "COLOSSAL", chance = 1000, incomeMultiplier = 20, scale = 3 },
		{ id = "Huge", name = "HUGE", chance = 200, incomeMultiplier = 6, scale = 2 },
		{ id = "Large", name = "LARGE", chance = 40, incomeMultiplier = 2.5, scale = 1.5 },
		{ id = "Big", name = "BIG", chance = 10, incomeMultiplier = 1.5, scale = 1.2 },
	},
}
