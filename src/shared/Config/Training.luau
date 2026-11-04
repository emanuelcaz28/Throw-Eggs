local Plot = require(script.Parent.Plot)

-- Training station: a squat rack at each base. Stepping on its pad locks the player in under the bar and
-- reps come automatically until they press STOP. Placeholder numbers; tune during playtesting.
local Training = {
	repInterval = 1, -- seconds per rep (one squat)
	xpPerRep = 1, -- every rep, before the x2 Training pass and the bubble

	-- Power works like the reference: XP fills a bar, and each full bar gives a fixed amount of Throw Power
	-- (powerPerBar, raised by rack upgrades). Each bar needs xpGrowth times the XP of the one before, so
	-- early bars fill in seconds and late ones in minutes: that, not money, paces the later maps
	-- (docs/GAME_SPEC.md section 12, from a play simulation: map 2 at ~2 min, map 8 at ~3 h, map 15 at ~31 h).
	-- XP needed for the next bar = baseXp * xpGrowth ^ (level - 1)
	baseXp = 2,
	xpGrowth = 1.011,

	startPower = 100, -- Throw Power before any bar

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
		-- Rack upgrades raise the power each full bar gives, in tiers [Owner]: 5 power per bar, 10 after 3
		-- upgrades, 20 after 4 more, then each tier is one upgrade longer and gives 25% more.
		powerTiers = { 5, 10, 20 },
		tierGrowth = 1.25,
		firstTierLength = 3,
		basePrice = 50, -- the first upgrade; each one after costs priceGrowth times more
		priceGrowth = 50,
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

function Training.xpPerRepFor(_upgrades: number): number
	return Training.xpPerRep
end

-- After this many rack upgrades: the tier (0 = first), upgrades already into it, and the tier's length.
function Training.tierOf(upgrades: number): (number, number, number)
	local tier, length = 0, Training.xpUpgrade.firstTierLength
	while upgrades >= length do
		upgrades -= length
		tier += 1
		length += 1
	end
	return tier, upgrades, length
end

local function tierPower(tier: number): number
	local tiers = Training.xpUpgrade.powerTiers
	if tier < #tiers then
		return tiers[tier + 1]
	end
	return math.floor(tiers[#tiers] * Training.xpUpgrade.tierGrowth ^ (tier - #tiers + 1))
end

-- Throw Power each full bar gives after this many rack upgrades.
function Training.powerPerBar(upgrades: number): number
	return tierPower((Training.tierOf(upgrades)))
end

-- How many more upgrades until the next tier, and what that tier gives per bar.
function Training.nextTier(upgrades: number): (number, number)
	local tier, into, length = Training.tierOf(upgrades)
	return length - into, tierPower(tier + 1)
end

function Training.xpUpgradePrice(upgrades: number): number
	return math.floor(Training.xpUpgrade.basePrice * Training.xpUpgrade.priceGrowth ^ upgrades)
end

return Training
