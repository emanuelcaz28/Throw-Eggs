-- Dinos per biome, most common first. chance = base "1 in X" before luck. income = $/s.
-- Income by rank is 1, 3, 10, 40, 150, 500, 1500, 5000 on the Forest, times 100 for each map after it, so a new map's
-- first good catch multiplies income at once (docs/GAME_SPEC.md section 12, worked out with a play
-- simulation). Tune during playtesting.
-- prize = true: a map's 7th and 8th, its top prizes (assets/models/build_<map>_monsters_7_8.py). Only luck reaches them: the
-- pity rules and the new map gift count from the rarest monster before them (ThrowService) and never give one (CatchOdds).
-- apex = true [Owner, 2026-11-14]: an end-game map's 9th to 12th, above its 8 (assets/models/build_<map>_apex.py), in the
-- four end-game rarities (Config/RarityLadder: Nightmare, Doomsday, Oblivion, Unknown). They are prizes too, so no
-- guarantee ever gives one, and they are not needed for the world's Index reward (IndexService). What reaches them is
-- in Config/Catch luckyHits. Every 12-monster map uses the same ladder, so the next map only needs its numbers
-- multiplied (docs/MAP_RECIPE.md "Monster numbers"):
-- hidden = true [Owner, 2026-11-14]: kept in Studio but out of the game (never rolled, not in the Index), for a later
-- update. Delete the hidden = true to release a monster. Maps 14 and 15's 9th to 12th wait for the next update.
--   chance: 2, 4, 12, 60, 400, 3000 | prizes 12007, 39989 | apex 149993, 600011, 2500009, 9999991
--   income: 1, 3, 10, 40, 200, 500 | prizes 1500, 5000 | apex 20000, 100000, 500000, 2500000,
--           times the map's first monster, which is 100x the map before's.
local Dinos = {
	Forest = {
		{ id = "Compy",        name = "Compy",         chance = 2,    income = 1 },
		{ id = "Gallimimus",   name = "Gallimimus",    chance = 5,    income = 3 },
		{ id = "Parasaur",     name = "Parasaurolophus", chance = 20, income = 10 },
		{ id = "Stego",        name = "Stegosaurus",   chance = 100,  income = 40 },
		{ id = "Raptor",       name = "Velociraptor",  chance = 500,  income = 150 },
		{ id = "Ptero",        name = "Pteranodon",    chance = 2000, income = 500 },
		{ id = "Therizino",    name = "Therizinosaurus", chance = 7500, income = 1500, prize = true },
		{ id = "Amarga",       name = "Amargasaurus",  chance = 25000, income = 5000, prize = true },
	},
	Desert = {
		{ id = "Proto",        name = "Dusty Proto",   chance = 2,    income = 100 },
		{ id = "Pachy",        name = "Bonkhead",      chance = 4,    income = 300 },
		{ id = "Ankylo",       name = "Grumposaurus",  chance = 8,    income = 1000 },
		{ id = "Triceratops",  name = "Triceratops",   chance = 30,   income = 4000 },
		{ id = "Carno",        name = "Carnotaurus",   chance = 150,  income = 15000 },
		{ id = "TRex",         name = "T-Rex",         chance = 1000, income = 50000 },
		{ id = "Scorchion",    name = "Scorchion",     chance = 5000, income = 150000, prize = true },
		{ id = "Rexhotep",     name = "Rexhotep",      chance = 20000, income = 500000, prize = true },
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
		{ id = "Mossmaw",      name = "Mossmaw",       chance = 8000, income = 15000000, prize = true },
		{ id = "Titanoboa",    name = "Titanoboa",     chance = 30000, income = 50000000, prize = true },
	},
	-- Models from assets/models/build_volcano.py (dino_<id>).
	Volcano = {
		{ id = "ToastyRaptor",  name = "Toasty Raptor",   chance = 2,    income = 1000000 },
		{ id = "BurntAnkylo",   name = "Burnt Ankylo",    chance = 4,    income = 3000000 },
		{ id = "HotSauceTrike", name = "Hot Sauce Trike", chance = 12,   income = 10000000 },
		{ id = "MagmaStego",    name = "Magma Stego",     chance = 60,   income = 40000000 },
		{ id = "ObsidianRex",   name = "Obsidian Rex",    chance = 400,  income = 150000000 },
		{ id = "VolcanoKing",   name = "Volcano King",    chance = 3000, income = 500000000 },
		{ id = "Magmapede",     name = "Magmapede",       chance = 12007, income = 1500000000, prize = true },
		{ id = "Cinderdrake",   name = "Cinderdrake",     chance = 39989, income = 5000000000, prize = true },
	},
	-- Models from assets/models/build_frozen_peaks_monsters.py (dino_<id>).
	FrozenPeaks = {
		{ id = "BrainFreeze",   name = "Brain Freeze",    chance = 2,    income = 100000000 },
		{ id = "WoollyRhino",   name = "Woolly Rhino",    chance = 4,    income = 300000000 },
		{ id = "ChillyMammoth", name = "Chilly Mammoth",  chance = 12,   income = 1000000000 },
		{ id = "Sabertooth",    name = "Sabertooth",      chance = 60,   income = 4000000000 },
		{ id = "FrostRaptor",   name = "Frost Raptor",    chance = 400,  income = 15000000000 },
		{ id = "BlizzardRex",   name = "Blizzard Rex",    chance = 3000, income = 50000000000 },
		{ id = "Ramvalanche",   name = "Ramvalanche",     chance = 12007, income = 150000000000, prize = true },
		{ id = "Abominator",    name = "Abominator",      chance = 39989, income = 500000000000, prize = true },
	},
	-- Models from assets/models/build_shadow_bog_monsters.py (dino_<id>).
	ShadowBog = {
		{ id = "StickySteve",   name = "Sticky Steve",    chance = 2,    income = 10000000000 },
		{ id = "SlowBob",       name = "Slow Bob",        chance = 4,    income = 30000000000 },
		{ id = "TerrorBird",    name = "Terror Bird",     chance = 12,   income = 100000000000 },
		{ id = "PitchRaptor",   name = "Pitch Raptor",    chance = 60,   income = 400000000000 },
		{ id = "TarTitan",      name = "Tar Titan",       chance = 400,  income = 1500000000000 },
		{ id = "BogRex",        name = "Bog Rex",         chance = 3000, income = 5000000000000 },
		{ id = "Skeeterror",    name = "Skeeterror",      chance = 12007, income = 15000000000000, prize = true },
		{ id = "Manhandler",    name = "Manhandler",      chance = 39989, income = 50000000000000, prize = true },
	},
	-- Models from assets/models/build_abyss_monsters.py (dino_<id>). They swim and hover (DinoLifeController).
	Abyss = {
		{ id = "SpiralGary",    name = "Spiral Gary",     chance = 2,    income = 1000000000000 },
		{ id = "Derpichthys",   name = "Derpichthys",     chance = 4,    income = 3000000000000 },
		{ id = "Dunkleosteus",  name = "Dunkleosteus",    chance = 12,   income = 10000000000000 },
		{ id = "Plesiosaur",    name = "Plesiosaur",      chance = 60,   income = 40000000000000 },
		{ id = "Megalodon",     name = "Megalodon",       chance = 400,  income = 150000000000000 },
		{ id = "Mosasaurus",    name = "Mosasaurus",      chance = 3000, income = 500000000000000 },
		{ id = "Shrimpact",     name = "Shrimpact",       chance = 12007, income = 1.5e15, prize = true },
		{ id = "Kraken",        name = "Kraken",          chance = 39989, income = 5e15, prize = true },
	},
	-- Models from assets/models/build_starfall_crater_monsters.py (dino_<id>). Calm faces, by the owner's wish.
	StarfallCrater = {
		{ id = "Craterback",    name = "Craterback",      chance = 2,    income = 100000000000000 },
		{ id = "Stargazer",     name = "Stargazer",       chance = 4,    income = 300000000000000 },
		{ id = "CometTrike",    name = "Comet Trike",     chance = 12,   income = 1e15 },
		{ id = "Ringhorn",      name = "Ringhorn",        chance = 60,   income = 4e15 },
		{ id = "Nebulasaur",    name = "Nebulasaur",      chance = 400,  income = 2e16 },
		{ id = "StarSovereign", name = "Star Sovereign",  chance = 3000, income = 5e16 },
		{ id = "Moonwhale",     name = "Moonwhale",       chance = 12007, income = 1.5e17, prize = true },
		{ id = "Constellion",   name = "Constellion",     chance = 39989, income = 5e17, prize = true },
	},
	-- Models from assets/models/build_eclipse_temple_monsters.py (dino_<id>): temple thieves to temple guardians.
	EclipseTemple = {
		{ id = "IdolOllie",       name = "Idol Ollie",       chance = 2,    income = 1e16 },
		{ id = "MossyMo",         name = "Mossy Mo",         chance = 4,    income = 3e16 },
		{ id = "LanternLarry",    name = "Lantern Larry",    chance = 12,   income = 1e17 },
		{ id = "JadeJaguar",      name = "Jade Jaguar",      chance = 60,   income = 4e17 },
		{ id = "PlumedWyrm",      name = "Plumed Wyrm",      chance = 400,  income = 2e18 },
		{ id = "EclipseDevourer", name = "Eclipse Devourer", chance = 3000, income = 5e18 },
		{ id = "PrayingMenace",   name = "Praying Menace",   chance = 12007, income = 1.5e19, prize = true },
		{ id = "Batastrophe",     name = "Batastrophe",      chance = 39989, income = 5e19, prize = true },
	},
	-- Models from assets/models/build_forbidden_library_monsters.py (dino_<id>): ink blots to the tome tyrant.
	ForbiddenLibrary = {
		{ id = "Inkling",    name = "Inkling",     chance = 2,    income = 1e18 },
		{ id = "HermitTome", name = "Hermit Tome", chance = 4,    income = 3e18 },
		{ id = "WaxHound",   name = "Wax Hound",   chance = 12,   income = 1e19 },
		{ id = "Quillback",  name = "Quillback",   chance = 60,   income = 4e19 },
		{ id = "HexOwl",     name = "Hex Owl",     chance = 400,  income = 2e20 },
		{ id = "TomeTyrant", name = "Tome Tyrant", chance = 3000, income = 5e20 },
		{ id = "Bookworm",   name = "Bookworm",    chance = 12007, income = 1.5e21, prize = true },
		{ id = "Papercut",   name = "Papercut",    chance = 39989, income = 5e21, prize = true },
	},
	-- Models from assets/models/build_midnight_carnival_monsters.py (dino_<id>): the fair's attractions, all teeth.
	MidnightCarnival = {
		{ id = "JackSnap",      name = "Jack Snap",      chance = 2,    income = 1e20 },
		{ id = "PopcornFiend",  name = "Popcorn Fiend",  chance = 4,    income = 3e20 },
		{ id = "Twisty",        name = "Twisty",         chance = 12,   income = 1e21 },
		{ id = "NightmareMare", name = "Nightmare Mare", chance = 60,   income = 4e21 },
		{ id = "Grinmaster",    name = "Grinmaster",     chance = 400,  income = 2e22 },
		{ id = "BigTopTerror",  name = "Big Top Terror", chance = 3000, income = 5e22 },
		{ id = "LastLaugh",     name = "Last Laugh",     chance = 12007, income = 1.5e23, prize = true },
		{ id = "Unbearable",    name = "Unbearable",     chance = 39989, income = 5e23, prize = true },
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
		{ id = "TickTock",    name = "Tick-Tock",     chance = 12007, income = 1.5e25, prize = true },
		{ id = "Clockodile",  name = "Clockodile",    chance = 39989, income = 5e25, prize = true },
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
		{ id = "Thornado",     name = "Thornado",      chance = 12007, income = 1.5e27, prize = true },
		{ id = "ThornToBits",  name = "Thorn to Bits", chance = 39989, income = 5e27, prize = true },
	},
	-- Models from assets/models/build_spore_hollow_monsters.py (spores rise from Vent bones and they pounce:
	-- DinoLifeController VENT and POUNCE, on top of THRASH).
	SporeHollow = {
		{ id = "ToadRage",      name = "Toad Rage",     chance = 2,    income = 1e26 },
		{ id = "MorelPanic",    name = "Morel Panic",   chance = 4,    income = 3e26 },
		{ id = "Antagonist",    name = "Antagonist",    chance = 12,   income = 1e27 },
		{ id = "Sporantula",    name = "Sporantula",    chance = 60,   income = 4e27 },
		{ id = "Gillotine",     name = "Gillotine",     chance = 400,  income = 2e28 },
		{ id = "Shroomageddon", name = "Shroomageddon", chance = 3000, income = 5e28 },
		{ id = "MouthBreather", name = "Mouth Breather", chance = 12007, income = 1.5e29, prize = true },
		{ id = "SporeLoser",    name = "Spore Loser",   chance = 39989, income = 5e29, prize = true },
		-- Models from assets/models/build_spore_hollow_apex.py.
		{ id = "RotWeiler",     name = "Rot Weiler",    chance = 149993, income = 2e30, prize = true, apex = true, hidden = true },
		{ id = "AcidReign",     name = "Acid Reign",    chance = 600011, income = 1e31, prize = true, apex = true, hidden = true },
		{ id = "CapPunishment", name = "Cap Punishment", chance = 2500009, income = 5e31, prize = true, apex = true, hidden = true },
		{ id = "Sporeactor",    name = "Sporeactor",    chance = 9999991, income = 2.5e32, prize = true, apex = true, hidden = true },
	},
	-- Models from assets/models/build_weeping_dark_monsters.py (they lunge and weep: a Drip bone turns on
	-- DinoLifeController RAGE and DRIP). Endless Grief is the thing behind the Last Door.
	WeepingDark = {
		{ id = "TeddyWrecks",  name = "Teddy Wrecks",  chance = 2,    income = 1e28 },
		{ id = "GoodBoy",      name = "Good Boy",      chance = 4,    income = 3e28 },
		{ id = "CasketCase",   name = "Casket Case",   chance = 12,   income = 1e29 },
		{ id = "WailingWidow", name = "Wailing Widow", chance = 60,   income = 4e29 },
		{ id = "DeathKnell",   name = "Death Knell",   chance = 400,  income = 2e30 },
		{ id = "EndlessGrief", name = "Endless Grief", chance = 3000, income = 5e30 },
		{ id = "Inconsolable", name = "Inconsolable",  chance = 12007, income = 1.5e31, prize = true },
		{ id = "LastBreath",   name = "Last Breath",   chance = 39989, income = 5e31, prize = true },
		-- Models from assets/models/build_weeping_dark_apex.py.
		{ id = "GrimWeeper",   name = "Grim Weeper",   chance = 149993, income = 2e32, prize = true, apex = true, hidden = true },
		{ id = "CageRage",     name = "Cage Rage",     chance = 600011, income = 1e33, prize = true, apex = true, hidden = true },
		{ id = "MourningStar", name = "Mourning Star", chance = 2500009, income = 5e33, prize = true, apex = true, hidden = true },
		{ id = "Nevermore",    name = "Nevermore",     chance = 9999991, income = 2.5e34, prize = true, apex = true, hidden = true },
	},
}

for _, list in Dinos do
	for index = #list, 1, -1 do
		if list[index].hidden then
			table.remove(list, index)
		end
	end
end

-- What The Deep End's eggs roll (Config/Biomes rollFrom, Config/DeepEnd): every monster of the last five worlds, most common
-- first and prizes last, like a world's own list. No world has this id, so the Index and the rest don't see it twice.
local deepPool = {}
for _, id in { "MidnightCarnival", "ClockworkCitadel", "ThornKingdom", "SporeHollow", "WeepingDark" } do
	for _, dino in Dinos[id] do
		table.insert(deepPool, dino)
	end
end
table.sort(deepPool, function(a, b)
	if (a.prize == true) ~= (b.prize == true) then
		return b.prize == true
	end
	return if a.chance ~= b.chance then a.chance < b.chance else a.income < b.income
end)
Dinos.DeepPool = deepPool

return Dinos
