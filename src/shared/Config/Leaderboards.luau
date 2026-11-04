-- The leaderboards in the arena: the top players across every server, refreshed every minute.
-- Bump storeVersion only to wipe the boards.
return {
	updateInterval = 60, -- seconds between saving everyone's scores and reading the top lists
	rows = 10,
	storeVersion = 1,

	-- Where the boards stand: the middle of each one's foot, in a shallow arc in front of the arena's front
	-- wall, on the right as you face the bases from the platform (-X), clear of the corner and of base 1's
	-- rack. yaw: degrees each is turned from facing the bases (+Z); the outer two turn in towards the middle.
	placements = {
		{ position = Vector3.new(-126, 0, 28), yaw = 12 },
		{ position = Vector3.new(-102, 0, 26), yaw = 0 },
		{ position = Vector3.new(-78, 0, 28), yaw = -12 },
		-- The two added boards stand on the other side of the corridor, either side of the SELL stall.
		-- Not checked in Studio yet.
		{ position = Vector3.new(66, 0, 28), yaw = 6 },
		{ position = Vector3.new(126, 0, 28), yaw = -6 },
	},
	-- The Blender boards (assets/models/build_leaderboards.py), board_<id> in this folder of Assets.Maps.
	-- Without them, plain boards of this size stand in.
	modelFolder = { "Forest", "Arena" },
	size = Vector3.new(16, 20, 1),

	-- The list's look (fonts are UiKit's, like the HUD's).
	medals = { -- the rows of the top three
		Color3.fromRGB(255, 201, 60),
		Color3.fromRGB(200, 212, 230),
		Color3.fromRGB(226, 146, 84),
	},
	valueColors = { count = Color3.fromRGB(111, 227, 255), cash = Color3.fromRGB(141, 255, 90), oneIn = Color3.fromRGB(255, 150, 240) },

	-- stat is the save field. "count" shows plain numbers, "cash" and "oneIn" short ones (1.2M).
	boards = {
		{ id = "MostDinos", title = "MOST DINOS", subtitle = "Dinos caught", stat = "totalCaught", kind = "count", color = Color3.fromRGB(70, 150, 230) },
		{ id = "TopMoney", title = "TOP MONEY", subtitle = "Total money earned", stat = "totalEarned", kind = "cash", color = Color3.fromRGB(90, 190, 80) },
		{ id = "LuckiestCatch", title = "LUCKIEST CATCH", subtitle = "Rarest catch", stat = "rarestOneIn", kind = "oneIn", color = Color3.fromRGB(170, 90, 220) },
		-- Added 2026-11-04 for competition. No Blender boards yet: they show as two plain parts until
		-- board_HighestIncome and board_FarthestThrow are made in build_leaderboards.py.
		{ id = "HighestIncome", title = "HIGHEST $/S", subtitle = "Best income ever", stat = "peakIncome", kind = "cash", color = Color3.fromRGB(230, 170, 40) },
		{ id = "FarthestThrow", title = "FARTHEST THROW", subtitle = "Longest throw, in studs", stat = "farthestThrow", kind = "count", color = Color3.fromRGB(230, 90, 60) },
	},
}
