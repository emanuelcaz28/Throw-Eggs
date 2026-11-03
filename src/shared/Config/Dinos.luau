-- Dinos per biome, most common first. chance = base "1 in X" before luck. income = $/s.
-- Placeholder numbers; tune during playtesting.
return {
	FernValley = {
		{ id = "Compy",        name = "Compy",         chance = 2,    income = 1 },
		{ id = "Gallimimus",   name = "Gallimimus",    chance = 5,    income = 3 },
		{ id = "Parasaur",     name = "Parasaurolophus", chance = 20, income = 10 },
		{ id = "Stego",        name = "Stegosaurus",   chance = 100,  income = 40 },
		{ id = "Raptor",       name = "Velociraptor",  chance = 500,  income = 150 },
		{ id = "Ptero",        name = "Pteranodon",    chance = 2000, income = 500 },
	},
	DryPlains = {
		{ id = "Pachy",        name = "Pachycephalosaurus", chance = 2,  income = 25 },
		{ id = "Ankylo",       name = "Ankylosaurus",  chance = 6,    income = 70 },
		{ id = "Triceratops",  name = "Triceratops",   chance = 30,   income = 250 },
		{ id = "Carno",        name = "Carnotaurus",   chance = 150,  income = 900 },
		{ id = "TRex",         name = "T-Rex",         chance = 1000, income = 4000 },
	},
	Swamp = {
		{ id = "Bary",         name = "Baryonyx",      chance = 2,    income = 600 },
		{ id = "Dilo",         name = "Dilophosaurus", chance = 8,    income = 1800 },
		{ id = "Sarco",        name = "Sarcosuchus",   chance = 40,   income = 7000 },
		{ id = "Brachio",      name = "Brachiosaurus", chance = 250,  income = 30000 },
		{ id = "Spino",        name = "Spinosaurus",   chance = 2000, income = 150000 },
	},
}
