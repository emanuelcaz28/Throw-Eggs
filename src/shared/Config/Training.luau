local Biomes = require(script.Parent.Biomes)
local Plot = require(script.Parent.Plot)
local Throw = require(script.Parent.Throw)

-- Training station: a squat rack at each base. Stepping on its pad locks the player in under the bar and
-- reps come automatically until they press STOP. Placeholder numbers; tune during playtesting.
local Training = {
	repInterval = 1, -- seconds per rep (one squat)
	xpPerRep = 1, -- every rep, before the x2 Training pass and the bubble
	xpPerRepGrowth = 1.25, -- XP per rep is multiplied by this for each upgrade bought at the sign

	-- [Owner, 2026-11-08] Like the reference: every full bar gives the same Throw Power, always (powerPerBar; the x2
	-- Power pass doubles it). Rack upgrades never change it: they only give more XP per squat, so bars fill faster.
	-- What gets harder is the XP a bar needs, which grows with how far your Throw Power reaches ("XP per level grows
	-- with distance down the lane"): baseXp at the throw line, times xpPerMap for every map your power reaches,
	-- smoothly in between (xpForNextBar). It depends on where you are, not on how many bars you've filled, so the x2
	-- Power and x2 Training passes make training exactly 2x faster and a power pack skips just the bars it replaces.
	-- So after an upgrade bars feel fast, then slowly get harder again as you move down the lane.
	-- [Owner, 2026-11-07] A little easy early to mid game, then harder from map 10, but never a hard grind. So bars grow
	-- gently through the maps before hardFromMap, jump once across that map, then grow steadily again.
	-- These set how long a map takes (docs/RETENTION_PLAN.md step 1: about 20 h to map 15 for an average free player).
	powerPerBar = 5,
	baseXp = 1,
	xpPerMap = 1.6, -- each map before hardFromMap
	hardFromMap = 10, -- the game's turn: late game starts here
	hardMapStep = 3.5, -- across that one map
	xpPerLateMap = 2, -- each map after it

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

	-- The lifter's own camera as training starts (TrainingCamera): one glide to a wide view, then the normal camera
	-- is theirs again [Owner, 2026-11-08: a view of them training from behind; 2026-11-09: no black bars, no swaying,
	-- and players mustn't feel shut off]. Offsets are from the lifter's root, in the way they face: +X their right,
	-- +Y up, +Z behind them.
	camera = {
		-- In front, to their left and above: the lifter, the rack, the other bases and the arena in view. From behind,
		-- the base's fence and the rack's posts hid the lifter.
		offset = Vector3.new(-10, 8, -12),
		glideSeconds = 0.7, -- the glide from wherever the camera was
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
		basePrice = 50, -- the first upgrade; each one after costs priceGrowth times more
		priceGrowth = 50,
		-- The words floating over the owner's own pad (TrainingController): the price, the XP per squat it gives,
		-- and how far the next rack is [Owner, 2026-11-08: "smaller and better, more satisfying"].
		sign = {
			height = 4, -- studs over the pad
			size = Vector2.new(190, 90), -- its box in pixels
			maxDistance = 90, -- studs; further away it's gone
			priceText = 30, -- pixel heights of the three lines
			xpText = 17,
			rackText = 13,
			outline = 3,
			bob = 0.2, -- it floats this many studs up and down...
			bobSeconds = 2.6, -- ...once every this many seconds
			pulse = 1.07, -- while you can afford it, the price breathes up to this size
			pulseSeconds = 1.1,
			punch = 1.35, -- buying one makes the sign jump to this size and spring back
			afford = { "#E2FFC4", "#38D24A" }, -- the price's colours, top to bottom
			tooPricey = { "#FFC2B8", "#EE3B2B" },
			xp = { "#E0F8FF", "#46C3F2" },
			rack = { "#FFFFFF", "#FFD15C" },
		},
		-- Holding E (or the prompt's button on phones and pads) near the pad buys one too [Owner, 2026-11-08].
		prompt = {
			holdSeconds = 0.4,
			reach = 2, -- studs from the prompt's point it shows [Owner, 2026-11-08]
			height = 3, -- studs over the pad it hangs at: a character's middle, so reach is measured across the ground
		},
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
	distance = math.min(distance, Throw.maxDistance()) -- past the last world bars stop growing: Config/DeepEnd paces that
	for index, biome in Biomes do
		if distance <= biome.endDist then
			return index - 1 + math.clamp((distance - biome.startDist) / (biome.endDist - biome.startDist), 0, 1)
		end
	end
	return #Biomes
end

-- The XP a bar needs at this Throw Power (power packs included): see xpPerMap. A PERFECT throw goes as far as the power.
function Training.xpForNextBar(power: number): number
	local passed = mapsPassed(power * Throw.meter.perfectMultiplier)
	local turn = Training.hardFromMap - 1 -- maps passed when that map starts
	local early = math.min(passed, turn)
	local step = math.clamp(passed - turn, 0, 1)
	local late = math.max(passed - turn - 1, 0)
	return math.max(math.floor(Training.baseXp * Training.xpPerMap ^ early * Training.hardMapStep ^ step * Training.xpPerLateMap ^ late), 1)
end

-- Each upgrade at the sign multiplies XP per rep by xpPerRepGrowth (the pad shows "+X XP per squat", like the
-- reference's bars). That's all an upgrade does: the power a bar gives never changes.
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

-- The next rack this many upgrades is working towards, and how many more upgrades it takes; nil after the last one.
function Training.nextRack(upgrades: number)
	for _, rack in Training.rackModels do
		if rack.upgrades > upgrades then
			return rack, rack.upgrades - upgrades
		end
	end
	return nil, 0
end

-- The bar a player fills at this power, before passes: the power it gives (always powerPerBar) and the XP it needs.
function Training.barFor(power: number): (number, number)
	return Training.powerPerBar, Training.xpForNextBar(power)
end

function Training.xpUpgradePrice(upgrades: number): number
	return math.floor(Training.xpUpgrade.basePrice * Training.xpUpgrade.priceGrowth ^ upgrades)
end

return Training
