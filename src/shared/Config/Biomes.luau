-- Biomes in throw order (near -> far). `name` is what players see; `id` never changes (saves, models, configs use it). Distances in studs from the throw line.
-- luck = multiplier reached at the END of the biome; interpolate inside it.
-- standardScale = how big this biome's monsters are with no size mutation, against the first biome's.
-- It grows about 1.39x per biome, to 10x at the last one (docs/GAME_SPEC.md section 8a).
return {
	{ id = "Forest",  name = "Forest",       startDist = 0,    endDist = 400,  luck = 2, standardScale = 1,   color = Color3.fromRGB(96, 158, 84) },
	{ id = "Desert",   name = "Desert",       startDist = 400,  endDist = 900,  luck = 5, standardScale = 1.4, color = Color3.fromRGB(196, 170, 104) },
	{ id = "Swamp",       name = "Swamp",        startDist = 900,  endDist = 1500, luck = 9, standardScale = 1.9, color = Color3.fromRGB(74, 104, 82) },
	{ id = "Volcano", name = "Volcano", startDist = 1500, endDist = 2200, luck = 14, standardScale = 2.7, color = Color3.fromRGB(214, 84, 44) },
	{ id = "FrozenPeaks", name = "Frozen Peaks", startDist = 2200, endDist = 3000, luck = 20, standardScale = 3.7, color = Color3.fromRGB(120, 196, 236) },
	{ id = "ShadowBog", name = "Shadow Bog", startDist = 3000, endDist = 3900, luck = 27, standardScale = 5.2, color = Color3.fromRGB(150, 98, 220) },
	{ id = "Abyss", name = "The Abyss", startDist = 3900, endDist = 4900, luck = 35, standardScale = 7.2, color = Color3.fromRGB(64, 190, 230) },
	{ id = "StarfallCrater", name = "Starfall Crater", startDist = 4900, endDist = 6000, luck = 45, standardScale = 10, color = Color3.fromRGB(255, 200, 80) },
}
