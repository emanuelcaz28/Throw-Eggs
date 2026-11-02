-- Training station: a squat rack. Stepping on its pad locks the player in under the bar and
-- reps come automatically until they press STOP. Placeholder numbers; tune during playtesting.
local Training = {
	repInterval = 1, -- seconds per rep (one squat)
	xpPerRep = 1, -- before any XP upgrades

	-- XP needed for the next level = baseXp * xpGrowth ^ (level - 1)
	baseXp = 5,
	xpGrowth = 1.25,

	startPower = 100, -- Throw Power at level 1
	powerPerLevel = 20,

	-- Station placement, in world studs. position is the centre of the pad, on the ground.
	station = {
		position = Vector3.new(30, 0, 0),
		padRadius = 7, -- stepping inside this starts training
		padHeight = 8, -- how far above the pad still counts
		stopDistance = 10, -- after STOP the player is put down this far in front of the rack
	},

	-- The orange pad beside the rack: each step onto it buys more XP per rep.
	xpUpgrade = {
		position = Vector3.new(42, 0, 6),
		padRadius = 3,
		padHeight = 8,
		xpPerUpgrade = 1, -- added to every rep, per upgrade
		basePrice = 50, -- the first upgrade; each one after costs priceGrowth times more
		priceGrowth = 1.5,
	},

	-- While training, a bubble pops up now and then; tapping it gives one rep worth multiplier reps.
	bubble = {
		minDelay = 6, -- seconds between bubbles
		maxDelay = 12,
		lifetime = 3, -- seconds it stays tappable
		multiplier = 2,
	},
}

function Training.xpToNextLevel(level: number): number
	return math.floor(Training.baseXp * Training.xpGrowth ^ (level - 1))
end

function Training.powerForLevel(level: number): number
	return Training.startPower + Training.powerPerLevel * (level - 1)
end

function Training.xpPerRepFor(upgrades: number): number
	return Training.xpPerRep + Training.xpUpgrade.xpPerUpgrade * upgrades
end

function Training.xpUpgradePrice(upgrades: number): number
	return math.floor(Training.xpUpgrade.basePrice * Training.xpUpgrade.priceGrowth ^ upgrades)
end

return Training
