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
		trainingLevel = 1,
		trainingXp = 0,
		bestIncome = 0, -- $/s of the best dino ever caught
		cash = 0,
		dinos = {}, -- every dino owned: { key, id, mutation, size, onPlot }
		nextDinoKey = 1,
		ownedEggs = { DirtyEgg = true },
		equippedEgg = "DirtyEgg",
		discovered = {}, -- every dino id ever caught, for the Index
	},
}
