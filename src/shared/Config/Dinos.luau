-- Dinos per biome, most common first. chance = base "1 in X" before luck. income = $/s.
-- Income by rank is 1, 3, 10, 40, 150, 500 on the Forest, times 100 for each map after it, so a new map's
-- first good catch multiplies income at once (docs/GAME_SPEC.md section 12, worked out with a play
-- simulation). Tune during playtesting.
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
		{ id = "Proto",        name = "Dusty Proto",   chance = 2,    income = 100 },
		{ id = "Pachy",        name = "Bonkhead",      chance = 4,    income = 300 },
		{ id = "Ankylo",       name = "Grumposaurus",  chance = 8,    income = 1000 },
		{ id = "Triceratops",  name = "Triceratops",   chance = 30,   income = 4000 },
		{ id = "Carno",        name = "Carnotaurus",   chance = 150,  income = 15000 },
		{ id = "TRex",         name = "T-Rex",         chance = 1000, income = 50000 },
	},
	-- Models from assets/models/build_swamp_monsters.py. The ids are the old stand-ins', so monsters
	-- players already own keep working and get the new models.
	Swamp = {
		{ id = "Dimetro",      name = "Soggy Dimetrodon", chance = 2,   income = 10000 },
		{ id = "Dilo",         name = "Burpasaurus",   chance = 4,    income = 30000 },
		{ id = "Bary",         name = "Baryonyx",      chance = 10,   income = 100000 },
		{ id = "Sarco",        name = "Sir Chomps-a-Lot", chance = 40, income = 400000 },
		{ id = "Brachio",      name = "Neckzilla",     chance = 250,  income = 1500000 },
		{ id = "Spino",        name = "Spinosaurus",   chance = 2000, income = 5000000 },
	},
	-- Models from assets/models/build_volcano.py (dino_<id>).
	Volcano = {
		{ id = "ToastyRaptor",  name = "Toasty Raptor",   chance = 2,    income = 1000000 },
		{ id = "BurntAnkylo",   name = "Burnt Ankylo",    chance = 4,    income = 3000000 },
		{ id = "HotSauceTrike", name = "Hot Sauce Trike", chance = 12,   income = 10000000 },
		{ id = "MagmaStego",    name = "Magma Stego",     chance = 60,   income = 40000000 },
		{ id = "ObsidianRex",   name = "Obsidian Rex",    chance = 400,  income = 150000000 },
		{ id = "VolcanoKing",   name = "Volcano King",    chance = 3000, income = 500000000 },
	},
	-- Models from assets/models/build_frozen_peaks_monsters.py (dino_<id>).
	FrozenPeaks = {
		{ id = "BrainFreeze",   name = "Brain Freeze",    chance = 2,    income = 100000000 },
		{ id = "WoollyRhino",   name = "Woolly Rhino",    chance = 4,    income = 300000000 },
		{ id = "ChillyMammoth", name = "Chilly Mammoth",  chance = 12,   income = 1000000000 },
		{ id = "Sabertooth",    name = "Sabertooth",      chance = 60,   income = 4000000000 },
		{ id = "FrostRaptor",   name = "Frost Raptor",    chance = 400,  income = 15000000000 },
		{ id = "BlizzardRex",   name = "Blizzard Rex",    chance = 3000, income = 50000000000 },
	},
	-- Models from assets/models/build_shadow_bog_monsters.py (dino_<id>).
	ShadowBog = {
		{ id = "StickySteve",   name = "Sticky Steve",    chance = 2,    income = 10000000000 },
		{ id = "SlowBob",       name = "Slow Bob",        chance = 4,    income = 30000000000 },
		{ id = "TerrorBird",    name = "Terror Bird",     chance = 12,   income = 100000000000 },
		{ id = "PitchRaptor",   name = "Pitch Raptor",    chance = 60,   income = 400000000000 },
		{ id = "TarTitan",      name = "Tar Titan",       chance = 400,  income = 1500000000000 },
		{ id = "BogRex",        name = "Bog Rex",         chance = 3000, income = 5000000000000 },
	},
	-- Models from assets/models/build_abyss_monsters.py (dino_<id>). They swim and hover (DinoLifeController).
	Abyss = {
		{ id = "SpiralGary",    name = "Spiral Gary",     chance = 2,    income = 1000000000000 },
		{ id = "Derpichthys",   name = "Derpichthys",     chance = 4,    income = 3000000000000 },
		{ id = "Dunkleosteus",  name = "Dunkleosteus",    chance = 12,   income = 10000000000000 },
		{ id = "Plesiosaur",    name = "Plesiosaur",      chance = 60,   income = 40000000000000 },
		{ id = "Megalodon",     name = "Megalodon",       chance = 400,  income = 150000000000000 },
		{ id = "Mosasaurus",    name = "Mosasaurus",      chance = 3000, income = 500000000000000 },
	},
	-- Models from assets/models/build_starfall_crater_monsters.py (dino_<id>). Calm faces, by the owner's wish.
	StarfallCrater = {
		{ id = "Craterback",    name = "Craterback",      chance = 2,    income = 100000000000000 },
		{ id = "Stargazer",     name = "Stargazer",       chance = 4,    income = 300000000000000 },
		{ id = "CometTrike",    name = "Comet Trike",     chance = 12,   income = 1e15 },
		{ id = "Ringhorn",      name = "Ringhorn",        chance = 60,   income = 4e15 },
		{ id = "Nebulasaur",    name = "Nebulasaur",      chance = 400,  income = 2e16 },
		{ id = "StarSovereign", name = "Star Sovereign",  chance = 3000, income = 5e16 },
	},
	-- Models from assets/models/build_eclipse_temple_monsters.py (dino_<id>): temple thieves to temple guardians.
	EclipseTemple = {
		{ id = "IdolOllie",       name = "Idol Ollie",       chance = 2,    income = 1e16 },
		{ id = "MossyMo",         name = "Mossy Mo",         chance = 4,    income = 3e16 },
		{ id = "LanternLarry",    name = "Lantern Larry",    chance = 12,   income = 1e17 },
		{ id = "JadeJaguar",      name = "Jade Jaguar",      chance = 60,   income = 4e17 },
		{ id = "PlumedWyrm",      name = "Plumed Wyrm",      chance = 400,  income = 2e18 },
		{ id = "EclipseDevourer", name = "Eclipse Devourer", chance = 3000, income = 5e18 },
	},
	-- Models from assets/models/build_clockwork_citadel_monsters.py (their keys, saw, drill and gear sail turn
	-- on Key, Drill and Cog bones: DinoLifeController SPIN).
	ClockworkCitadel = {
		{ id = "WindUpWally", name = "Wind-Up Wally", chance = 2,    income = 1e22 },
		{ id = "Sprocket",    name = "Sprocket",      chance = 4,    income = 3e22 },
		{ id = "KettleBelly", name = "Kettle Belly",  chance = 12,   income = 1e23 },
		{ id = "Gearjaw",     name = "Gearjaw",       chance = 60,   income = 4e23 },
		{ id = "Drillhorn",   name = "Drillhorn",     chance = 400,  income = 2e24 },
		{ id = "ChronoRex",   name = "Chrono Rex",    chance = 3000, income = 5e24 },
	},
	-- Models from assets/models/build_thorn_kingdom_monsters.py (their briar whips thrash on Lash bones:
	-- DinoLifeController THRASH).
	ThornKingdom = {
		{ id = "BrambleBrat",  name = "Bramble Brat",  chance = 2,    income = 1e24 },
		{ id = "GrandmaGnash", name = "Grandma Gnash", chance = 4,    income = 3e24 },
		{ id = "SirSkewer",    name = "Sir Skewer",    chance = 12,   income = 1e25 },
		{ id = "HartAttack",   name = "Hart Attack",   chance = 60,   income = 4e25 },
		{ id = "Hydrangry",    name = "Hydrangry",     chance = 400,  income = 2e26 },
		{ id = "Wrathorn",     name = "Wrathorn",      chance = 3000, income = 5e26 },
	},
}
