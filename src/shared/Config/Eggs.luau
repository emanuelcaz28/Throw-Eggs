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
	{ id = "EclipseEgg", name = "Eclipse Egg", price = 5e16, luckBonus = 5.5, color = Color3.fromRGB(255, 190, 70) },
	{ id = "ForbiddenEgg", name = "Forbidden Egg", price = 5e18, luckBonus = 6.5, color = Color3.fromRGB(150, 60, 50) },
	{ id = "CarnivalEgg", name = "Carnival Egg", price = 5e20, luckBonus = 8, color = Color3.fromRGB(235, 60, 85) },
	{ id = "ClockworkEgg", name = "Clockwork Egg", price = 5e22, luckBonus = 9.5, color = Color3.fromRGB(210, 150, 60) },
	{ id = "ThornEgg",   name = "Thorn Egg",   price = 5e24, luckBonus = 11.5, color = Color3.fromRGB(60, 130, 75) },
	{ id = "SporeEgg",   name = "Spore Egg",   price = 5e26, luckBonus = 14, color = Color3.fromRGB(150, 100, 210) },
	{ id = "WeepingEgg", name = "Weeping Egg", price = 5e28, luckBonus = 17, color = Color3.fromRGB(140, 140, 146) },
}
