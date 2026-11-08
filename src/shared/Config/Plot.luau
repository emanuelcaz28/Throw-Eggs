-- Player plots: caught dinos stand here as statues and earn $/s, wherever the player puts them.
-- Placeholder numbers; tune during playtesting.
local Plot = {
	slots = 10, -- dinos that can earn at once, before any upgrades
	upgradeSlots = 2, -- each upgrade at the plot's sign adds this many
	maxSlots = 20,
	-- The first upgrade; each one after costs upgradePriceGrowth times more: $500K, $500B, $500Qa, $500Sx, $500No.
	-- [Owner, 2026-11-06] the plot was maxed 3 minutes in; it should be late game. A play simulation on the game's code
	-- (2026-11-06) buys them around maps 2, 5, 8, 10 and 13: maxed about 14 hours into a 30-hour game.
	upgradeBasePrice = 500000,
	upgradePriceGrowth = 1000000,
	backpackSize = 100, -- dinos held off the plot; a catch with no room is sold automatically
	-- Every catch goes into the backpack (hotbar) and onto the player's head once the reveal is done, so they place it
	-- themselves, instead of landing straight on the base [Owner, 2026-11-08]. false: catches go on the base by themselves.
	carryNewCatches = true,
	sellSeconds = 60, -- a dino sells for this many seconds of its own income
	offlineRate = 0.5, -- share of the plot's $/s paid for time away (events don't count)
	maxOfflineHours = 8, -- time away beyond this earns nothing more
	minOfflineSeconds = 60, -- shorter breaks (like a quick rejoin) pay nothing
	offlinePayoutDelay = 3, -- seconds after joining, so Game Pass bonuses are known by then
	placeMargin = 4, -- studs between a dino's feet and the plot's edge
	autoSpacing = 10, -- dinos placed automatically keep at least this far apart when there's room

	-- One plot per player, in one row across the back of the arena (Config/Map), gates facing the
	-- throw platform (-Z). Bases are small on purpose: late dinos are meant to spill over the fences.
	-- Set the server size in Game Settings to match this count. Players beyond it still earn, keep
	-- and manage dinos, but have no base, rack or egg shop.
	positions = {
		Vector3.new(-104, 0, 120),
		Vector3.new(-52, 0, 120),
		Vector3.new(0, 0, 120),
		Vector3.new(52, 0, 120),
		Vector3.new(104, 0, 120),
	},
	size = Vector3.new(48, 1, 48),
	color = Color3.fromRGB(110, 190, 90),
	ownColor = Color3.fromRGB(226, 142, 58), -- edge of the plot that belongs to you
	homeInset = 6, -- after a catch you land this far inside the plot's front edge (its exit)
	-- The Back to Plot button (HomeController, HomeService) puts you this far out in front of your gate, facing in.
	-- Straight out from the gate is clear: the squat rack and XP pad stand to one side, the egg stall to the other
	-- (Config/Training, Config/Hub), so you never land on a pad. Your own screen moves you at once; if the server
	-- still sees you on the throw platform backupAfter seconds later, it moves you itself.
	homeButton = { outFromGate = 10, cooldown = 1, backupAfter = 1.5 },
	gateWidth = 12, -- the gap in the fence at the middle of the front edge
	fenceSection = 6, -- studs between fence posts: the Blender rails' length (BaseKit base_FenceRails)

	-- The upgrade sign stands on the front fence beside the gate, on the rack's side, facing out.
	upgradeSign = {
		offset = Vector3.new(-9, 0, -0.9), -- from the middle of the gate (gatePosition), between it and the rack
		clickDistance = 40,
	},

	-- The owner plate floats over the middle of the base (BillboardGui, sized in studs).
	ownerPlate = {
		height = 26,
		size = Vector2.new(18, 15),
		maxDistance = 1000,
	},

	-- Tags floating over the monsters on the bases (MonsterTagController, Figma "Throw Eggs - Monster Tags &
	-- Walk Vision"): its mutations (only when it has some), its name, its $/s. Only the few monsters nearest to you
	-- show one, so a full base doesn't pile its tags into a heap.
	tags = {
		-- Tags show only while you stand on a base or within plotMargin studs of its edge [Owner, 2026-11-04], and
		-- only on that base's monsters: at most `nearest` of them, the ones closest to you.
		plotMargin = 10,
		nearest = 3,
		maxDistance = 60, -- studs at which a tag has shrunk to farScale (measured to the monster's edge)
		ceiling = 18, -- studs over the monster's feet a tag stops at, so a giant's tag stays readable from its base
		headGap = 1.5, -- studs between the top of the head and the tag
		size = Vector2.new(240, 80), -- the tag's box in pixels, the same on screen for every monster size
		farScale = 0.75, -- how big a tag is at maxDistance, against up close
		mutationText = 13, -- pixel heights of the three lines [Owner, 2026-11-04: the first ones were far too big]
		nameText = 20,
		rarityText = 15, -- the carried monster's rarity word, between the mutations and the name
		-- The carried monster's tag [Owner, 2026-11-07: "more close to its head and not that big"]: this much
		-- smaller than a base monster's, and gap studs over the top of its visible body.
		carried = { scale = 0.7, gap = 0.3 },
		incomeText = 17,
		outline = 2.5, -- the dark outline round the letters, in pixels
		sizeWord = { "#FFFFFF", "#AEB8C8" }, -- size mutations are silver, top to bottom
		income = { "#B6FF8A", "#2FD24A" },
		-- A colour mutation's word runs from its colour lifted towards white (by this much) down to its colour.
		colourLift = 0.6,
		-- Mutations too dark to read on the dark outline (Shadow) are lifted towards white instead: the top of the
		-- word by darkTop, the bottom by darkBottom.
		darkBelow = 0.25, -- a colour this dark or darker (0 black, 1 white)
		darkTop = 0.8,
		darkBottom = 0.45,
	},
}

-- How many dinos a plot holds after this many upgrades.
function Plot.capacity(upgrades: number): number
	return math.min(Plot.slots + Plot.upgradeSlots * upgrades, Plot.maxSlots)
end

function Plot.upgradePrice(upgrades: number): number
	return Plot.upgradeBasePrice * Plot.upgradePriceGrowth ^ upgrades
end

-- Where a player lands on their plot after a catch: just inside the front edge (the side
-- facing the throw platform, where the gate and sign are), facing into the plot so the camera shows their dinos.
function Plot.homeCFrame(plotIndex: number): CFrame
	local position = Plot.positions[plotIndex]
	local home = position + Vector3.new(0, Plot.size.Y, -Plot.size.Z / 2 + Plot.homeInset)
	return CFrame.lookAt(home, home + Vector3.new(0, 0, 1))
end

-- Where the Back to Plot button puts you: out in front of your gate, on the ground, facing into the plot.
function Plot.frontCFrame(plotIndex: number): CFrame
	local spot = Plot.gatePosition(plotIndex) - Vector3.new(0, 0, Plot.homeButton.outFromGate)
	return CFrame.lookAt(spot, spot + Vector3.new(0, 0, 1))
end

-- The middle of a plot's gate, on the ground. Its shop, rack and XP pad are placed from here
-- (offsets in Config/Hub and Config/Training): -Z is out of the base, +X is to the left as you
-- walk up to the gate.
function Plot.gatePosition(plotIndex: number): Vector3
	return Plot.positions[plotIndex] - Vector3.new(0, 0, Plot.size.Z / 2)
end

-- Whether a spot (studs from the plot's centre, along X and Z) is far enough inside the plot.
function Plot.inBounds(x: number, z: number): boolean
	return math.abs(x) <= Plot.size.X / 2 - Plot.placeMargin and math.abs(z) <= Plot.size.Z / 2 - Plot.placeMargin
end

return Plot
