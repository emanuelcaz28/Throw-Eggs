local Biomes = require(script.Parent.Biomes)
local Plot = require(script.Parent.Plot)
local Throw = require(script.Parent.Throw)

-- Training station: a squat rack at each base. Stepping on its pad locks the player in under the bar and
-- reps come automatically until they press STOP. Placeholder numbers; tune during playtesting.
local Training = {
	repInterval = 1, -- seconds per rep (one squat)
	xpPerRep = 1, -- every rep, before the x2 Training pass and the bubble
	xpPerRepGrowth = 1.25, -- XP per rep is multiplied by this for each upgrade bought at the sign

	-- Power works like the reference: XP fills a bar, and each full bar gives a fixed amount of Throw Power
	-- (powerPerBar, raised by rack upgrades). The XP a bar needs grows with how far your Throw Power reaches, also
	-- like the reference ("XP per level grows with distance down the lane"): baseXp at the throw line, times
	-- xpPerMap for every map a PERFECT throw passes, smoothly in between (xpForNextBar). It depends on where you
	-- are, not on how many bars you've filled, so the x2 Power and x2 Training passes make training exactly 2x
	-- faster and a power pack skips just the bars it replaces. (When it grew with the bar count, x2 Power skipped
	-- the most expensive bars and finished the game in under an hour.) Early bars fill in seconds, late ones in
	-- minutes: that paces the game (docs/GAME_SPEC.md section 12).
	-- [Owner, 2026-11-07] A little easy early to mid game, then harder from map 10, but never a hard grind. So bars grow
	-- gently through the maps before hardFromMap, jump once across that map, then grow steadily again.
	baseXp = 2,
	xpPerMap = 1.8, -- each map before hardFromMap
	hardFromMap = 10, -- the game's turn: late game starts here
	hardMapStep = 3.2, -- across that one map
	xpPerLateMap = 1.85, -- each map after it

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

	-- [Owner] The rack itself gets better as its owner buys upgrades, for everyone to see. upgrades is how many it
	-- takes, lowest first: spread so a new rack comes about every 2 to 3 maps, the last one around map 15. model is
	-- a piece in BaseKit (assets/models/build_racks.py). A base with no owner has the first.
	rackModels = {
		{ upgrades = 0, model = "base_SquatRack", name = "Gym Rack" },
		{ upgrades = 3, model = "base_SquatRack_Iron", name = "Iron Rack" },
		{ upgrades = 7, model = "base_SquatRack_Bone", name = "Bone Rack" },
		{ upgrades = 10, model = "base_SquatRack_Crystal", name = "Crystal Rack" },
		{ upgrades = 13, model = "base_SquatRack_Magma", name = "Magma Rack" },
		{ upgrades = 16, model = "base_SquatRack_Titan", name = "Titan Rack" },
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

	-- [Owner] While training, a bubble pops up every 3 seconds, tapped or not; tapping it gives one rep worth
	-- multiplier reps. Keep lifetime + tapGrace under interval, so one bubble is gone before the next.
	bubble = {
		interval = 3, -- seconds from one bubble appearing to the next
		lifetime = 2, -- seconds it shows on screen
		tapGrace = 0.3, -- extra seconds the server still accepts a tap, for one made at the last moment on a slow connection
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

-- How many maps a throw this far has passed: 0 at the throw line, 1.5 halfway through the second map, and so on.
local function mapsPassed(distance: number): number
	for index, biome in Biomes do
		if distance <= biome.endDist then
			return index - 1 + math.clamp((distance - biome.startDist) / (biome.endDist - biome.startDist), 0, 1)
		end
	end
	return #Biomes
end

-- The XP the next bar needs at this Throw Power (power packs included): see xpPerMap.
function Training.xpForNextBar(power: number): number
	local passed = mapsPassed(power * Throw.meter.perfectMultiplier)
	local turn = Training.hardFromMap - 1 -- maps passed when that map starts
	local early = math.min(passed, turn)
	local step = math.clamp(passed - turn, 0, 1)
	local late = math.max(passed - turn - 1, 0)
	return math.floor(Training.baseXp * Training.xpPerMap ^ early * Training.hardMapStep ^ step * Training.xpPerLateMap ^ late)
end

-- Each upgrade at the sign also multiplies XP per rep by xpPerRepGrowth (the pad shows "+X XP / rep", like the
-- reference's bars). Bars cost about 2x more XP a map against about 1.3x more XP a rep, so later maps take longer.
function Training.xpPerRepFor(upgrades: number): number
	return math.floor(Training.xpPerRep * Training.xpPerRepGrowth ^ upgrades * 10 + 0.5) / 10
end

-- The best entry of rackModels this many upgrades has earned.
function Training.rackFor(upgrades: number)
	local best = Training.rackModels[1]
	for _, rack in Training.rackModels do
		if upgrades >= rack.upgrades then
			best = rack
		end
	end
	return best
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
