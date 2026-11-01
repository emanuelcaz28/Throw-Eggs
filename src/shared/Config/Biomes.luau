-- Biomes in throw order (near -> far). Distances in studs from the throw line.
-- luck = multiplier reached at the END of the biome; interpolate inside it.
return {
	{ id = "FernValley",  name = "Fern Valley",  startDist = 0,    endDist = 400,  luck = 2 },
	{ id = "DryPlains",   name = "Dry Plains",   startDist = 400,  endDist = 900,  luck = 5 },
	{ id = "Swamp",       name = "Swamp",        startDist = 900,  endDist = 1500, luck = 9 },
	-- Post-MVP:
	-- { id = "VolcanoFoothills", name = "Volcano Foothills", ... luck = 14 },
	-- { id = "IceAgeTundra",     name = "Ice Age Tundra",    ... luck = 20 },
	-- { id = "TarPits",          name = "Tar Pits",          ... luck = 27 },
	-- { id = "DeepSeaTrench",    name = "Deep Sea Trench",   ... luck = 35 },
	-- { id = "MeteorCrater",     name = "Meteor Crater",     ... luck = 45 },
}
