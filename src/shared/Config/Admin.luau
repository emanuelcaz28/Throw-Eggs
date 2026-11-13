-- Admins: who sees the ADMIN button (AdminService, AdminController). The game's owner always counts; add more
-- Roblox user ids here. The Robux store is untouched: admin tools only change a throwaway test save or the tutorial.
return {
	userIds = {
		234533860, -- cacaciosu3000
	},
	testCash = 1e6, -- what "+$1M" gives, only in a throwaway test save
	-- Server boosts from the admin panel (AdminBoostService, AdminBoosts): the whole server you are in, for the minutes
	-- you choose. They live on the server only and end when it closes. The most each one can be:
	boosts = {
		luck = { name = "Server Luck", most = 1000 }, -- multiplies everyone's luck, on top of bought Server Luck and events
		power = { name = "Power", most = 100 }, -- multiplies how far everyone throws (the Power Limit still applies)
		xp = { name = "Training XP", most = 100 }, -- multiplies the XP every squat gives
	},
	mostMinutes = 24 * 60,
	mostLuckyThrows = 1000, -- x100 / x500 lucky throws given to one player at once
	mostPower = 1e9, -- Throw Power given to one player at once (it's saved, like a Power pack)
}
