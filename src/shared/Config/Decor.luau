-- Props placed around the map: trees, hedges, rocks and the rest, modelled in Blender
-- (assets/models/build_fern_valley.py) and kept in ReplicatedStorage.Assets.Maps.<biome>.Props.
-- Spots follow the approved blockout (assets/models/build_world_layout.py). The corridor's are picked
-- with a fixed seed, so every server gets the same ones; change `seed` for a different arrangement.
--
-- Coordinates are the game's (Config/Map): arena floor Y = 0, throw line Z = 0, corridor along -Z.
-- `distance` is studs from the throw line, `side` is studs out from the corridor's middle.
-- A prop list is { name, weight, scale = { min, max } }: heavier ones turn up more often.
return {
	-- Along each biome's stretch of the corridor. Biomes without props imported are skipped.
	corridor = {
		FernValley = {
			seed = 7,

			-- On the corridor floor, off the middle where the eggs land.
			floor = {
				firstDistance = 24,
				gap = { 12, 24 }, -- studs to the next one
				side = { 20, 27 },
				props = {
					{ name = "prop_BlockTree", weight = 22, scale = { 1.2, 1.6 } },
					{ name = "prop_CycadTree", weight = 18, scale = { 1.4, 1.8 } },
					{ name = "prop_Hedge", weight = 20, scale = { 0.9, 1.1 } },
					{ name = "prop_Fern", weight = 12, scale = { 1.2, 1.6 } },
					{ name = "prop_Stump", weight = 10, scale = { 1.2, 1.5 } },
					{ name = "prop_Rock", weight = 10, scale = { 1.2, 1.8 } },
					{ name = "prop_Mushrooms", weight = 5, scale = { 1.3, 1.7 } },
					{ name = "prop_Nest", weight = 3, scale = { 1, 1.2 } },
				},
				-- Small things tucked in around the bigger ones.
				extras = {
					chance = 0.6,
					spread = 8, -- studs from the prop they go with
					props = {
						{ name = "prop_Fern", weight = 3, scale = { 0.6, 0.9 } },
						{ name = "prop_Mushrooms", weight = 2, scale = { 0.8, 1.1 } },
						{ name = "prop_Rock", weight = 2, scale = { 0.5, 0.8 } },
					},
				},
			},

			-- Big trees up on the rim, above the corridor walls. They start on the arena's front rim,
			-- so the corridor's mouth is framed by trees.
			rim = {
				firstDistance = 4,
				gap = { 18, 30 },
				chance = 0.85, -- per side, per step
				side = { 56, 94 }, -- the wall's inner edge is 36, the island's edge 108
				props = {
					{ name = "prop_BlockTree", weight = 5, scale = { 1.8, 2.4 } },
					{ name = "prop_CycadTree", weight = 3, scale = { 2, 2.6 } },
					{ name = "prop_Hedge", weight = 2, scale = { 1.3, 1.6 } },
				},
			},
		},
	},

	-- The arena's props, from the first biome's folder.
	arena = {
		biome = "FernValley",

		-- Eggs evenly spaced along the rim's inner edge, where the reference has pumpkins.
		rimEggs = {
			name = "prop_RimEgg",
			spacing = 36,
			inset = 8, -- from the rim's inner edge
			clearOfCorridor = 8, -- none this close to the corridor's mouth
		},

		-- The strip of grass behind the bases. These are solid, so players walk round them.
		backStrip = {
			{ name = "prop_Rock", position = Vector3.new(-120, 0, 160), yaw = 20, scale = 1 },
			{ name = "prop_Fern", position = Vector3.new(-104, 0, 168), yaw = 70, scale = 1.1 },
			{ name = "prop_Stump", position = Vector3.new(-80, 0, 158), yaw = 0, scale = 1 },
			{ name = "prop_Mushrooms", position = Vector3.new(-58, 0, 166), yaw = 140, scale = 1.2 },
			{ name = "prop_Nest", position = Vector3.new(-30, 0, 162), yaw = 30, scale = 0.9 },
			{ name = "prop_Rock", position = Vector3.new(10, 0, 158), yaw = 200, scale = 1.2 },
			{ name = "prop_Fern", position = Vector3.new(24, 0, 168), yaw = 10, scale = 1 },
			{ name = "prop_Stump", position = Vector3.new(48, 0, 164), yaw = 110, scale = 1.1 },
			{ name = "prop_Mushrooms", position = Vector3.new(70, 0, 166), yaw = 60, scale = 1 },
			{ name = "prop_Fern", position = Vector3.new(96, 0, 160), yaw = 160, scale = 1.2 },
			{ name = "prop_Rock", position = Vector3.new(126, 0, 160), yaw = 300, scale = 0.9 },
		},

		-- A few trees on the back and side rims, so the arena isn't ringed by bare grass.
		rimTrees = {
			{ name = "prop_BlockTree", position = Vector3.new(-176, 32, 204), yaw = 0, scale = 2.1 },
			{ name = "prop_CycadTree", position = Vector3.new(-90, 32, 212), yaw = 40, scale = 2.2 },
			{ name = "prop_BlockTree", position = Vector3.new(-20, 32, 206), yaw = 90, scale = 2.0 },
			{ name = "prop_CycadTree", position = Vector3.new(56, 32, 214), yaw = 200, scale = 2.4 },
			{ name = "prop_BlockTree", position = Vector3.new(130, 32, 204), yaw = 180, scale = 2.1 },
			{ name = "prop_Hedge", position = Vector3.new(176, 32, 150), yaw = 0, scale = 1.2 },
			{ name = "prop_BlockTree", position = Vector3.new(178, 32, 90), yaw = 270, scale = 2.0 },
			{ name = "prop_Hedge", position = Vector3.new(-176, 32, 120), yaw = 90, scale = 1.2 },
			{ name = "prop_CycadTree", position = Vector3.new(-178, 32, 60), yaw = 120, scale = 2.1 },
		},
	},
}
