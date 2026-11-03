-- The leaderboards in the arena: the top players across every server, refreshed every minute.
-- Bump storeVersion only to wipe the boards.
return {
	updateInterval = 60, -- seconds between saving everyone's scores and reading the top lists
	rows = 10,
	storeVersion = 1,

	-- Where the boards stand: centre of the bottom edge. They line the arena's right-hand wall as you
	-- face the bases from the platform (-X), in front of the bases, facing into the arena.
	positions = {
		Vector3.new(-138, 0, 28),
		Vector3.new(-138, 0, 46),
		Vector3.new(-138, 0, 64),
	},
	facing = Vector3.new(1, 0, 0),
	size = Vector3.new(16, 20, 1),

	-- stat is the save field. "count" shows plain numbers, "cash" and "oneIn" short ones (1.2M).
	boards = {
		{ id = "MostDinos", title = "MOST DINOS", subtitle = "Dinos caught", stat = "totalCaught", kind = "count", color = Color3.fromRGB(70, 150, 230) },
		{ id = "TopMoney", title = "TOP MONEY", subtitle = "Total money earned", stat = "totalEarned", kind = "cash", color = Color3.fromRGB(90, 190, 80) },
		{ id = "LuckiestCatch", title = "LUCKIEST CATCH", subtitle = "Rarest catch", stat = "rarestOneIn", kind = "oneIn", color = Color3.fromRGB(170, 90, 220) },
	},
}
