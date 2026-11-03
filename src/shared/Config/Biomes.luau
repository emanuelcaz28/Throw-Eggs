-- Biomes in throw order (near -> far). Distances in studs from the throw line.
-- luck = multiplier reached at the END of the biome; interpolate inside it.
-- standardScale = how big this biome's monsters are with no size mutation, against the first biome's.
-- It grows about 1.39x per biome, to 10x at the last one (docs/GAME_SPEC.md section 8a).
return {
	{ id = "FernValley",  name = "Fern Valley",  startDist = 0,    endDist = 400,  luck = 2, standardScale = 1,   color = Color3.fromRGB(96, 158, 84) },
	{ id = "DryPlains",   name = "Dry Plains",   startDist = 400,  endDist = 900,  luck = 5, standardScale = 1.4, color = Color3.fromRGB(196, 170, 104) },
	{ id = "Swamp",       name = "Swamp",        startDist = 900,  endDist = 1500, luck = 9, standardScale = 1.9, color = Color3.fromRGB(74, 104, 82) },
	-- Post-MVP:
	-- { id = "VolcanoFoothills", name = "Volcano Foothills", ... luck = 14, standardScale = 2.7 },
	-- { id = "IceAgeTundra",     name = "Ice Age Tundra",    ... luck = 20, standardScale = 3.7 },
	-- { id = "TarPits",          name = "Tar Pits",          ... luck = 27, standardScale = 5.2 },
	-- { id = "DeepSeaTrench",    name = "Deep Sea Trench",   ... luck = 35, standardScale = 7.2 },
	-- { id = "MeteorCrater",     name = "Meteor Crater",     ... luck = 45, standardScale = 10 },
}
