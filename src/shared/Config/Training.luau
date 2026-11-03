local Plot = require(script.Parent.Plot)

-- Training station: a squat rack at each base. Stepping on its pad locks the player in under the bar and
-- reps come automatically until they press STOP. Placeholder numbers; tune during playtesting.
local Training = {
	repInterval = 1, -- seconds per rep (one squat)
	xpPerRep = 1, -- before any XP upgrades

	-- XP needed for the next level = baseXp * xpGrowth ^ (level - 1)
	baseXp = 5,
	xpGrowth = 1.25,

	startPower = 100, -- Throw Power at level 1
	powerPerLevel = 20,

	-- Every base has its own rack, right outside the fence on the right of its gate, and only its
	-- owner trains there; everyone can see it. Offsets are from the middle of the base's gate
	-- (Plot.gatePosition): -Z is out of the base. The lifter faces out of the base.
	rack = {
		offset = Vector3.new(-18, 0, -6), -- centre of the rack's pad, on the ground (clear of the upgrade sign)
		padRadius = 5, -- stepping inside this starts training
		padHeight = 8, -- how far above the pad still counts
		stopOffset = Vector3.new(7, 0, -6), -- after STOP the player is put down here, from the pad's centre
	},

	-- The orange pad in front of the rack: each step onto it buys more XP per rep. Only the owner buys.
	xpUpgrade = {
		offset = Vector3.new(-18, 0, -16), -- from the middle of the gate, like the rack
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

-- Where a base's rack pad and XP pad sit on the ground.
function Training.rackPosition(plotIndex: number): Vector3
	return Plot.gatePosition(plotIndex) + Training.rack.offset
end

function Training.xpPadPosition(plotIndex: number): Vector3
	return Plot.gatePosition(plotIndex) + Training.xpUpgrade.offset
end

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
