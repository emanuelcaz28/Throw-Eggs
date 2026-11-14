-- Player save settings. Bump storeName only to wipe everyone's progress.
local Settings = require(script.Parent.Settings)

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

	-- Saves the owner wiped back to a new player's, on that player's next join, once per id. What was bought stays:
	-- receipts (so nothing is given twice), giftedPasses and luckDealBought. Keep old ids: reusing one resets nobody.
	resets = {
		{ id = "RESET_2026-11-06", userIds = { 234533860, 1404164940, 11729966071, 159677990 } },
	},

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
		deepestDepth = 0, -- the deepest Depth reached in The Deep End (Config/DeepEnd)
		statsStarted = false, -- set once the stats above have been filled in for this save
		receipts = {}, -- Robux purchases already granted, by purchase id
		throwsSinceRare = 0, -- throws in a row without a rare monster, for pity (Config/Hooks)
		throwsSinceRarest = 0, -- throws in a row without a map's rarest monster, for the jackpot pity (Config/Hooks)
		throwsSinceApex = 0, -- throws in a row on end-game maps without one of their 9th to 12th, for the end-game streak (Config/Hooks apexStreak)
		throwsSinceGift = 0, -- throws since the last surprise gift, every 60th is a Legendary or Mythic (Config/Hooks)
		bigShotsLeft = -1, -- big shots not used yet (Config/Hooks bigShots); -1 = not decided: a save with nothing caught gets them all, an older one none
		recentCatches = {}, -- ids of the last 2 monsters caught by throwing, newest first; less likely to come again (Config/Catch pick)
		xpBoostEndsAt = 0, -- os.time() when the x2 XP from completing a world in the Index runs out (Config/Index)
		indexClaimed = {}, -- worlds whose x2 XP has been collected in the Index, by biome id
		indexClaimsStarted = false, -- set once a save from before hand-collected rewards has had its finished worlds marked collected
		luckyThrows = {}, -- lucky throws owned, count by multiplier as text ("100" = 2); LuckyThrows
		luckDealBought = false, -- the one-time R$ 3 Luck x100 deal has been used
		specialsGiven = {}, -- special monsters already given for their Game Pass, by id (Config/Specials)
		giftedPasses = {}, -- Game Passes another player gifted, by Config/Shop key ("doubleCash" = true)
		serverLuckLeft = 0, -- seconds of bought Server Luck not used yet; they come back on the next join
		dailyTaskDay = -1, -- the UTC day number the daily tasks below belong to (DailyTasks)
		dailyTaskCounts = {}, -- how far each is today, by task id
		dailyTasksDone = false, -- whether today's x2 XP has been given
		playGiftSeconds = 0, -- seconds played since the tutorial ended, while a gift for staying is still owed (Config/PlayGifts)
		playGiftsGiven = 0, -- how many of its free lucky throws have been given
		playGiftPlan = -1, -- which times its free lucky throws follow (Config/PlayGifts): 2 = luckyThrows, 1 = luckyThrowsBefore (a save that had already played before 2026-11-13); -1 = not decided
		firstEventDone = false, -- the player's own first event has started (or a real one was running then)
		dailyStreak = 0, -- the last daily reward day claimed, 1 to 7 (Config/Daily)
		dailyLastDay = -1, -- the UTC day number (os.time() // 86400) of the last daily claim
		settings = Settings.defaults, -- music and sound effect volume, hide other players' dinos (Config/Settings)
		tutorial = false, -- the new-player tutorial's progress; TutorialService makes it (a save that has played starts it finished)
	},

	-- Studio only: with this attribute ticked on Workspace (in Edit mode, before Play), every player in the play test
	-- gets a brand-new save that is never read or written, and the leaderboards ignore them. For testing the tutorial
	-- and anything else without touching a real save (memory studio-test-save-pitfall).
	studioFreshSaveAttribute = "StudioFreshSave",
}
