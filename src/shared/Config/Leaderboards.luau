-- The leaderboards in the hub: the top players across every server, refreshed every minute.
-- Bump storeVersion only to wipe the boards.
return {
	updateInterval = 60, -- seconds between saving everyone's scores and reading the top lists
	rows = 10,
	storeVersion = 1,

	-- Where the boards stand: centre of the bottom edge, facing +Z (towards the plots).
	positions = {
		Vector3.new(52, 0, -24),
		Vector3.new(72, 0, -24),
		Vector3.new(92, 0, -24),
	},
	size = Vector3.new(16, 20, 1),

	-- stat is the save field. "count" shows plain numbers, "cash" and "oneIn" short ones (1.2M).
	boards = {
		{ id = "MostDinos", title = "MOST DINOS", subtitle = "Dinos caught", stat = "totalCaught", kind = "count", color = Color3.fromRGB(70, 150, 230) },
		{ id = "TopMoney", title = "TOP MONEY", subtitle = "Total money earned", stat = "totalEarned", kind = "cash", color = Color3.fromRGB(90, 190, 80) },
		{ id = "LuckiestCatch", title = "LUCKIEST CATCH", subtitle = "Rarest catch", stat = "rarestOneIn", kind = "oneIn", color = Color3.fromRGB(170, 90, 220) },
	},
}
