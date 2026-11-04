-- Throwable egg tiers (Egg Shop): one per map, each costing about what that map's income makes in a few
-- minutes (100x the one before, like incomes). luckBonus multiplies the distance luck. The first egg is free
-- and every player starts with it. Ids are saved, so never rename one. Tune during playtesting.
return {
	{ id = "DirtyEgg",   name = "Dirty Egg",   price = 0,    luckBonus = 1.0, color = Color3.fromRGB(190, 170, 135) },
	{ id = "SpottedEgg", name = "Spotted Egg", price = 500,  luckBonus = 1.3, color = Color3.fromRGB(150, 205, 170) },
	{ id = "GoldenEgg",  name = "Golden Egg",  price = 5e4,  luckBonus = 1.6, color = Color3.fromRGB(255, 205, 70) },
	{ id = "LavaEgg",    name = "Lava Egg",    price = 5e6,  luckBonus = 2,   color = Color3.fromRGB(235, 85, 45) },
	{ id = "FrostEgg",   name = "Frost Egg",   price = 5e8,  luckBonus = 2.5, color = Color3.fromRGB(150, 220, 255) },
	{ id = "ShadowEgg",  name = "Shadow Egg",  price = 5e10, luckBonus = 3,   color = Color3.fromRGB(110, 60, 170) },
	{ id = "AbyssEgg",   name = "Abyss Egg",   price = 5e12, luckBonus = 3.7, color = Color3.fromRGB(30, 120, 170) },
	{ id = "CosmicEgg",  name = "Cosmic Egg",  price = 5e14, luckBonus = 4.5, color = Color3.fromRGB(125, 85, 225) },
}
