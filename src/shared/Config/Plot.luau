-- Player plots: caught dinos stand here as statues and earn $/s.
-- Placeholder numbers; tune during playtesting.
return {
	slots = 8, -- dinos that can earn at once
	backpackSize = 100, -- dinos held off the plot; a catch with no room is sold automatically
	sellSeconds = 60, -- a dino sells for this many seconds of its own income
	maxStatueScale = 1.6, -- so the biggest sizes still fit in their slot

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
	columns = 4,
	slotSpacing = Vector2.new(27, 32), -- studs between statues
	color = Color3.fromRGB(110, 190, 90),
	slotColor = Color3.fromRGB(86, 158, 72),
	ownColor = Color3.fromRGB(226, 142, 58), -- edge of the plot that belongs to you
}
