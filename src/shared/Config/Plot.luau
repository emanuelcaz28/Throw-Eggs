-- Player plots: caught dinos stand here as statues and earn $/s, wherever the player puts them.
-- Placeholder numbers; tune during playtesting.
local Plot = {
	slots = 8, -- dinos that can earn at once, before any upgrades
	upgradeSlots = 2, -- each upgrade at the plot's sign adds this many
	maxSlots = 30,
	upgradeBasePrice = 1000, -- the first upgrade; each one after costs upgradePriceGrowth times more
	upgradePriceGrowth = 6,
	backpackSize = 100, -- dinos held off the plot; a catch with no room is sold automatically
	sellSeconds = 60, -- a dino sells for this many seconds of its own income
	offlineRate = 0.5, -- share of the plot's $/s paid for time away (events don't count)
	maxOfflineHours = 8, -- time away beyond this earns nothing more
	minOfflineSeconds = 60, -- shorter breaks (like a quick rejoin) pay nothing
	offlinePayoutDelay = 3, -- seconds after joining, so Game Pass bonuses are known by then
	placeMargin = 5, -- studs between a dino's feet and the plot's edge
	autoSpacing = 16, -- dinos placed automatically keep at least this far apart when there's room

	-- One plot per player. Set the server size in Game Settings to match this count.
	-- Players beyond it still earn, keep and manage dinos, but have no statues to walk to.
	positions = {
		Vector3.new(-130, 0, 80),
		Vector3.new(0, 0, 80),
		Vector3.new(130, 0, 80),
		Vector3.new(-130, 0, 170),
		Vector3.new(0, 0, 170),
		Vector3.new(130, 0, 170),
	},
	size = Vector3.new(120, 1, 80),
	color = Color3.fromRGB(110, 190, 90),
	ownColor = Color3.fromRGB(226, 142, 58), -- edge of the plot that belongs to you
	homeInset = 6, -- after a catch you land this far inside the plot's front edge (its exit)
	gateWidth = 16, -- the gap in the fence at the middle of the front edge
	fenceHeight = 4,
	fenceColor = Color3.fromRGB(176, 120, 64),
}

-- How many dinos a plot holds after this many upgrades.
function Plot.capacity(upgrades: number): number
	return math.min(Plot.slots + Plot.upgradeSlots * upgrades, Plot.maxSlots)
end

function Plot.upgradePrice(upgrades: number): number
	return Plot.upgradeBasePrice * Plot.upgradePriceGrowth ^ upgrades
end

-- Where a player lands on their plot after a catch: just inside the front edge (the side
-- facing the hub, where the sign is), facing into the plot so the camera shows their dinos.
function Plot.homeCFrame(plotIndex: number): CFrame
	local position = Plot.positions[plotIndex]
	local home = position + Vector3.new(0, Plot.size.Y, -Plot.size.Z / 2 + Plot.homeInset)
	return CFrame.lookAt(home, home + Vector3.new(0, 0, 1))
end

-- Whether a spot (studs from the plot's centre, along X and Z) is far enough inside the plot.
function Plot.inBounds(x: number, z: number): boolean
	return math.abs(x) <= Plot.size.X / 2 - Plot.placeMargin and math.abs(z) <= Plot.size.Z / 2 - Plot.placeMargin
end

return Plot
