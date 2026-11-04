-- Player save settings. Bump storeName only to wipe everyone's progress.
return {
	storeName = "PlayerData_v1",
	autosaveInterval = 60, -- seconds between autosaves; each one also refreshes the session lock

	-- A lock older than this belongs to a crashed server and may be taken over.
	-- Keep it well above autosaveInterval so a live server never loses its lock.
	lockExpiry = 180,

	loadAttempts = 12,
	loadRetryDelay = 5, -- seconds; also covers waiting for another server to release its lock
	saveAttempts = 4,
	saveRetryDelay = 2, -- seconds; doubles after each failed attempt

	-- A new player's save. New fields added here are filled in for existing players on load.
	defaults = {
		trainingLevel = 1, -- the bar being filled (Config/Training)
		trainingXp = 0,
		trainedPower = -1, -- Throw Power from full bars; -1 = a save from before bars, worked out on load
		xpUpgrades = 0, -- bought at the orange pad beside the squat rack
		bonusPower = 0, -- Throw Power bought in Shop packs, on top of what the training level gives
		bestIncome = 0, -- $/s of the best dino ever caught
		cash = 0,
		lastSeen = 0, -- os.time() of the last income tick, for offline earnings
		offlinePending = 0, -- offline earnings waiting for the player to press CLAIM
		dinos = {}, -- every dino owned: { key, id, mutation, size, onPlot }
		nextDinoKey = 1,
		ownedEggs = { DirtyEgg = true },
		equippedEgg = "DirtyEgg",
		discovered = {}, -- every dino id ever caught, for the Index
		starterClaimed = false,
		plotUpgrades = 0, -- bought at the sign by the plot's gate
		-- Leaderboard stats. Saves from before these existed get them estimated on load.
		totalCaught = 0, -- dinos caught by throwing, ever
		totalEarned = 0, -- cash earned from income and sales, ever
		rarestOneIn = 0, -- the "1 in X" of the rarest catch ever
		peakIncome = 0, -- the highest $/s ever (events counted)
		farthestThrow = 0, -- studs, the farthest egg ever
		statsStarted = false, -- set once the stats above have been filled in for this save
		receipts = {}, -- Robux purchases already granted, by purchase id
		throwsSinceRare = 0, -- throws in a row without a rare monster, for pity (Config/Hooks)
		luckyThrows = {}, -- lucky throws owned, count by multiplier as text ("100" = 2); LuckyThrows
		luckDealBought = false, -- the one-time R$ 3 Luck x100 deal has been used
		dailyStreak = 0, -- the last daily reward day claimed, 1 to 7 (Config/Daily)
		dailyLastDay = -1, -- the UTC day number (os.time() // 86400) of the last daily claim
	},
}
