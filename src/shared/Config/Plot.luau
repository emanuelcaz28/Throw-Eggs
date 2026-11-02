-- Player plots: caught dinos stand here as statues and earn $/s, wherever the player puts them.
-- Placeholder numbers; tune during playtesting.
local Plot = {
	slots = 8, -- dinos that can earn at once
	backpackSize = 100, -- dinos held off the plot; a catch with no room is sold automatically
	sellSeconds = 60, -- a dino sells for this many seconds of its own income
	maxStatueScale = 1.6, -- so the biggest sizes don't swallow the plot
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
}

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
