-- The leaderboards in the arena: the top players across every server, refreshed every minute.
-- Bump storeVersion only to wipe the boards.
return {
	updateInterval = 60, -- seconds between saving everyone's scores and reading the top lists
	rows = 10,
	storeVersion = 1,
	-- [Owner, 2026-11-08] accounts never shown on the boards (the owner). Their old scores are removed on server start.
	hiddenNames = { "cacaciosu3000" },

	-- Where the boards stand: the middle of each one's foot, in a shallow arc in front of the arena's front
	-- wall, on the right as you face the bases from the platform (-X), clear of the corner and of base 1's
	-- rack. yaw: degrees each is turned from facing the bases (+Z); the outer two turn in towards the middle.
	placements = {
		{ position = Vector3.new(-126, 0, 28), yaw = 12 },
		{ position = Vector3.new(-110, 0, 26), yaw = 0 },
		{ position = Vector3.new(-94, 0, 28), yaw = -12 },
	},
	-- The Blender boards (assets/models/build_leaderboards.py), board_<id> in this folder of Assets.Maps.
	-- Without them, plain boards of this size stand in.
	modelFolder = { "Forest", "Arena" },
	scale = 0.8, -- the boards' size against their Blender models (owner, 2026-11-05: 20% smaller, closer together)
	size = Vector3.new(16, 20, 1),

	-- The list's look (fonts are UiKit's, like the HUD's).
	medals = { -- the rows of the top three
		Color3.fromRGB(255, 201, 60),
		Color3.fromRGB(200, 212, 230),
		Color3.fromRGB(226, 146, 84),
	},
	valueColors = { count = Color3.fromRGB(111, 227, 255), cash = Color3.fromRGB(141, 255, 90), oneIn = Color3.fromRGB(255, 150, 240) },

	-- stat is the save field, "throwPower" for the player's Throw Power (TrainingService), or "income" for their $/s
	-- right now (the Income attribute PlotService sets: the base with passes, no timed event). "count" shows plain
	-- numbers, "cash" and "oneIn" short ones (1.2M); perSecond adds "/s". model: the Blender board to use, if not
	-- board_<id>.
	-- [Owner, 2026-11-08] Most Power replaced Most Dinos; it has its own store and reuses that board's model.
	-- [Owner, 2026-11-08] Top Money shows $/s instead of total money earned: its own store (TopIncome), the same board.
	boards = {
		{ id = "MostPower", title = "MOST POWER", subtitle = "Throw Power", stat = "throwPower", kind = "count", model = "board_MostDinos", color = Color3.fromRGB(70, 150, 230) },
		{ id = "TopIncome", title = "TOP MONEY", subtitle = "Money per second", stat = "income", kind = "cash", perSecond = true, model = "board_TopMoney", color = Color3.fromRGB(90, 190, 80) },
		{ id = "LuckiestCatch", title = "LUCKIEST CATCH", subtitle = "Rarest catch", stat = "rarestOneIn", kind = "oneIn", color = Color3.fromRGB(170, 90, 220) },
	},
}
