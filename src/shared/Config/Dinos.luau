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
	-- Models from assets/models/build_shadow_bog_monsters.py (dino_<id>).
	ShadowBog = {
		{ id = "StickySteve",   name = "Sticky Steve",    chance = 2,    income = 200000 },
		{ id = "SlowBob",       name = "Slow Bob",        chance = 4,    income = 450000 },
		{ id = "TerrorBird",    name = "Terror Bird",     chance = 12,   income = 1250000 },
		{ id = "PitchRaptor",   name = "Pitch Raptor",    chance = 60,   income = 5000000 },
		{ id = "TarTitan",      name = "Tar Titan",       chance = 400,  income = 22000000 },
		{ id = "BogRex",        name = "Bog Rex",         chance = 3000, income = 125000000 },
	},
	-- Models from assets/models/build_abyss_monsters.py (dino_<id>). They swim and hover (DinoLifeController).
	Abyss = {
		{ id = "SpiralGary",    name = "Spiral Gary",     chance = 2,    income = 1000000 },
		{ id = "Derpichthys",   name = "Derpichthys",     chance = 4,    income = 2250000 },
		{ id = "Dunkleosteus",  name = "Dunkleosteus",    chance = 12,   income = 6250000 },
		{ id = "Plesiosaur",    name = "Plesiosaur",      chance = 60,   income = 25000000 },
		{ id = "Megalodon",     name = "Megalodon",       chance = 400,  income = 110000000 },
		{ id = "Mosasaurus",    name = "Mosasaurus",      chance = 3000, income = 625000000 },
	},
	-- Models from assets/models/build_starfall_crater_monsters.py (dino_<id>). Calm faces, by the owner's wish.
	StarfallCrater = {
		{ id = "Craterback",    name = "Craterback",      chance = 2,    income = 5000000 },
		{ id = "Stargazer",     name = "Stargazer",       chance = 4,    income = 11000000 },
		{ id = "CometTrike",    name = "Comet Trike",     chance = 12,   income = 31000000 },
		{ id = "Ringhorn",      name = "Ringhorn",        chance = 60,   income = 125000000 },
		{ id = "Nebulasaur",    name = "Nebulasaur",      chance = 400,  income = 550000000 },
		{ id = "StarSovereign", name = "Star Sovereign",  chance = 3000, income = 3100000000 },
	},
}
