-- Biomes in throw order (near -> far). `name` is what players see; `id` never changes (saves, models, configs use it). Distances in studs from the throw line.
-- luck = the luck shown at the END of the biome (Config/Luck climbs to it inside the biome), 50x at the last
-- map's end [Owner, 2026-11-06]. It's only the number players see: the roll has its own 1x-5x in every biome
-- (Luck.rollRange, docs/GAME_SPEC.md section 8b), so changing these doesn't change any odds.
-- standardScale = how big this biome's monsters are with no size mutation, against the first biome's.
-- It grows slowly, to 2x at map 15, so every map has room for size mutations up to 100x.
return {
	{ id = "Forest",  name = "Forest",       startDist = 0,    endDist = 400,  luck = 3, standardScale = 1,   color = Color3.fromRGB(96, 158, 84) },
	{ id = "Desert",   name = "Desert",       startDist = 400,  endDist = 900,  luck = 5, standardScale = 1.05, color = Color3.fromRGB(196, 170, 104) },
	{ id = "Swamp",       name = "Swamp",        startDist = 900,  endDist = 1500, luck = 7, standardScale = 1.1, color = Color3.fromRGB(74, 104, 82) },
	{ id = "Volcano", name = "Volcano", startDist = 1500, endDist = 2200, luck = 9, standardScale = 1.16, color = Color3.fromRGB(214, 84, 44) },
	{ id = "FrozenPeaks", name = "Frozen Peaks", startDist = 2200, endDist = 3000, luck = 11, standardScale = 1.22, color = Color3.fromRGB(120, 196, 236) },
	{ id = "ShadowBog", name = "Shadow Bog", startDist = 3000, endDist = 3900, luck = 14, standardScale = 1.28, color = Color3.fromRGB(150, 98, 220) },
	{ id = "Abyss", name = "The Abyss", startDist = 3900, endDist = 4900, luck = 17, standardScale = 1.35, color = Color3.fromRGB(64, 190, 230) },
	{ id = "StarfallCrater", name = "Starfall Crater", startDist = 4900, endDist = 6000, luck = 20, standardScale = 1.42, color = Color3.fromRGB(255, 200, 80) },
	{ id = "EclipseTemple", name = "Eclipse Temple", startDist = 6000, endDist = 7200, luck = 24, standardScale = 1.49, color = Color3.fromRGB(80, 230, 150) },
	{ id = "ForbiddenLibrary", name = "Forbidden Library", startDist = 7200, endDist = 8500, luck = 28, standardScale = 1.56, color = Color3.fromRGB(170, 130, 255) },
	{ id = "MidnightCarnival", name = "Midnight Carnival", startDist = 8500, endDist = 9900, luck = 32, standardScale = 1.64, color = Color3.fromRGB(255, 120, 150) },
	{ id = "ClockworkCitadel", name = "Clockwork Citadel", startDist = 9900, endDist = 11400, luck = 36, standardScale = 1.72, color = Color3.fromRGB(236, 164, 72) },
	{ id = "ThornKingdom", name = "Thorn Kingdom", startDist = 11400, endDist = 13000, luck = 40, standardScale = 1.81, color = Color3.fromRGB(236, 72, 104) },
	{ id = "SporeHollow", name = "Spore Hollow", startDist = 13000, endDist = 14700, luck = 45, standardScale = 1.9, color = Color3.fromRGB(176, 236, 64) },
	{ id = "WeepingDark", name = "The Weeping Dark", startDist = 14700, endDist = 16500, luck = 50, standardScale = 2, color = Color3.fromRGB(216, 228, 244) },
	-- Not a world of its own monsters: Config/DeepEnd. rollFrom is the list in Config/Dinos its eggs roll.
	{ id = "DeepEnd", name = "The Deep End", startDist = 16500, endDist = 18000, luck = 50, standardScale = 2, rollFrom = "DeepPool", color = Color3.fromRGB(150, 235, 215) },
}
