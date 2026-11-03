-- The map: a sunken arena with the bases in it, the orange throw platform in its front wall, and
-- the corridor below the platform that the eggs fly down. Sizes come from the approved blockout
-- (assets/models/build_world_layout.py) and the corridor pieces from build_world_kit.py.
--
-- World coordinates: the arena floor is Y = 0, the throw line (where biome distances start) is Z = 0
-- and the corridor runs along -Z. The arena is +Z of the platform. 1 stud = 1 Blender unit.
local Map = {
	arena = {
		halfWidth = 144, -- the arena floor runs from -halfWidth to +halfWidth along X
		frontZ = 16, -- the platform's arena-side edge
		backZ = 176,
		floorThickness = 12, -- down to the corridor floor, so nothing shows under it
	},

	walls = {
		rimY = 32, -- top of every wall, the grass you see above the arena and the corridor
		bottomY = -60, -- the island's outer dirt faces drop this far
		rimWidth = 56, -- the arena walls, from their inner face to the island's edge
		grassThickness = 2,
		dripBand = 4, -- the grass along the top of the inner face
		dripDepth = 1.5, -- how far the hanging grass sticks out of the wall
		dripWidth = 8,
		dripLengths = { 0, 4, 4, 8, 8, 12, 16 }, -- picked at random under the band, per drip
		dripSeed = 7, -- the same hanging grass in every server
	},

	platform = {
		width = 72, -- the corridor is this wide too
		depth = 16, -- from the throw line (Z = 0) to the arena (Z = depth)
		top = 0.5, -- a step up from the arena floor
	},

	corridor = {
		floorY = -12, -- below the arena, so the platform's front is a dirt face
		section = 64, -- length of one corridor piece (Assets.Maps.FernValley.Corridor)
		wallStartZ = -40, -- the arena's front wall ends here; the corridor walls carry on from it
		extra = 36, -- corridor beyond the farthest biome, so the last eggs land well inside it
		barrierHeight = 40, -- invisible wall at the throw line, so nobody walks off the platform
	},

	-- The kit's corridor pieces are Fern Valley's colours. Other biomes recolour them; a role
	-- that isn't listed keeps the kit's colour.
	biomeColors = {
		DryPlains = {
			Floor = Color3.fromRGB(246, 226, 162),
			Dirt = Color3.fromRGB(194, 150, 92),
			Grass = Color3.fromRGB(217, 189, 119),
		},
		Swamp = {
			Floor = Color3.fromRGB(96, 140, 78),
			Dirt = Color3.fromRGB(92, 74, 52),
			Grass = Color3.fromRGB(110, 150, 70),
		},
	},

	-- The arena, built from plain parts with the same see-through checker and studs as the kit.
	colors = {
		arenaFloor = Color3.fromRGB(76, 196, 37),
		dirt = Color3.fromRGB(173, 106, 62),
		grass = Color3.fromRGB(164, 234, 62),
	},
	checkerTexture = "rbxassetid://126276110612056", -- assets/textures/checker_studs_overlay.png
	checkerStuds = 16, -- one image is 2 x 2 squares of 8 studs

	spawn = Vector3.new(0, 0, 40), -- in the open ground, between the platform and the bases
}

return Map
