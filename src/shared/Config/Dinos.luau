-- Dinos per biome, most common first. chance = base "1 in X" before luck. income = $/s.
-- Placeholder numbers; tune during playtesting.
return {
	Forest = {
		{ id = "Compy",        name = "Compy",         chance = 2,    income = 1 },
		{ id = "Gallimimus",   name = "Gallimimus",    chance = 5,    income = 3 },
		{ id = "Parasaur",     name = "Parasaurolophus", chance = 20, income = 10 },
		{ id = "Stego",        name = "Stegosaurus",   chance = 100,  income = 40 },
		{ id = "Raptor",       name = "Velociraptor",  chance = 500,  income = 150 },
		{ id = "Ptero",        name = "Pteranodon",    chance = 2000, income = 500 },
	},
	Desert = {
		{ id = "Proto",        name = "Dusty Proto",   chance = 2,    income = 15 },
		{ id = "Pachy",        name = "Bonkhead",      chance = 4,    income = 25 },
		{ id = "Ankylo",       name = "Grumposaurus",  chance = 8,    income = 70 },
		{ id = "Triceratops",  name = "Triceratops",   chance = 30,   income = 250 },
		{ id = "Carno",        name = "Carnotaurus",   chance = 150,  income = 900 },
		{ id = "TRex",         name = "T-Rex",         chance = 1000, income = 4000 },
	},
	-- Models from assets/models/build_swamp_monsters.py. The ids are the old stand-ins', so monsters
	-- players already own keep working and get the new models.
	Swamp = {
		{ id = "Dimetro",      name = "Soggy Dimetrodon", chance = 2,   income = 500 },
		{ id = "Dilo",         name = "Burpasaurus",   chance = 4,    income = 1200 },
		{ id = "Bary",         name = "Baryonyx",      chance = 10,   income = 3000 },
		{ id = "Sarco",        name = "Sir Chomps-a-Lot", chance = 40, income = 7000 },
		{ id = "Brachio",      name = "Neckzilla",     chance = 250,  income = 30000 },
		{ id = "Spino",        name = "Spinosaurus",   chance = 2000, income = 150000 },
	},
	-- Models from assets/models/build_volcano.py (dino_<id>).
	Volcano = {
		{ id = "ToastyRaptor",  name = "Toasty Raptor",   chance = 2,    income = 8000 },
		{ id = "BurntAnkylo",   name = "Burnt Ankylo",    chance = 4,    income = 18000 },
		{ id = "HotSauceTrike", name = "Hot Sauce Trike", chance = 12,   income = 50000 },
		{ id = "MagmaStego",    name = "Magma Stego",     chance = 60,   income = 200000 },
		{ id = "ObsidianRex",   name = "Obsidian Rex",    chance = 400,  income = 900000 },
		{ id = "VolcanoKing",   name = "Volcano King",    chance = 3000, income = 5000000 },
	},
	-- Models from assets/models/build_frozen_peaks_monsters.py (dino_<id>).
	FrozenPeaks = {
		{ id = "BrainFreeze",   name = "Brain Freeze",    chance = 2,    income = 40000 },
		{ id = "WoollyRhino",   name = "Woolly Rhino",    chance = 4,    income = 90000 },
		{ id = "ChillyMammoth", name = "Chilly Mammoth",  chance = 12,   income = 250000 },
		{ id = "Sabertooth",    name = "Sabertooth",      chance = 60,   income = 1000000 },
		{ id = "FrostRaptor",   name = "Frost Raptor",    chance = 400,  income = 4500000 },
		{ id = "BlizzardRex",   name = "Blizzard Rex",    chance = 3000, income = 25000000 },
	},
}
