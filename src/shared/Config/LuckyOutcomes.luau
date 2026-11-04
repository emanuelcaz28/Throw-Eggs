-- What a lucky throw really does (docs/GAME_SPEC.md section 8b). Its x number is for show: it multiplies
-- the luck number on screen during the flight, not the roll. Instead, by multiplier, chance is how likely
-- the throw is lucky, and a lucky throw hatches its outcome instead of an ordinary roll.
-- The "1 in X" the reveal shows is always the catch's real odds in normal play (DinoStats), so a banger's
-- huge number is true: that monster, colour and size together really are that rare.
-- Ranks are places in a biome's list in Config/Dinos: 1 is the most common, 6 the rarest.
return {
	throws = {
		{ multiplier = 50, chance = 0.5, outcome = "nice" }, -- the daily reward's: a coin flip
		{ multiplier = 100, chance = 1, outcome = "nice" },
		{ multiplier = 500, chance = 1, outcome = "banger" },
	},
	outcomes = {
		-- Something nice, not the nicest: the 4th or 5th rarest monster, with a common colour mutation
		-- (picked the way they're rolled: Gold most often). Its size is rolled as normal.
		nice = { minRank = 4, maxRank = 5, mutations = { "Gold", "Ruby", "Diamond" } },
		-- The show: the map's rarest monster in one of these rare colour and size presets, picked evenly.
		-- On the Forest that's 1 in 15 billion to 1 in 400 billion.
		banger = {
			minRank = 6,
			maxRank = 6,
			presets = {
				{ mutation = "Amethyst", size = "PlanetSized" },
				{ mutation = "Shadow", size = "PlanetSized" },
				{ mutation = "Shadow", size = "UnitOfDoom" },
				{ mutation = "Ghost", size = "UnitOfDoom" },
			},
		},
	},
}
