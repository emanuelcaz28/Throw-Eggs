-- Props placed around the map: trees, hedges, rocks and the rest, modelled in Blender (each map's
-- assets/models/build_<map>.py) and kept in ReplicatedStorage.Assets.Maps.<biome>.Props.
-- Spots follow the approved blockout (assets/models/build_world_layout.py). The corridor's are picked
-- with a fixed seed, so every server gets the same ones; change `seed` for a different arrangement.
--
-- Coordinates are the game's (Config/Map): arena floor Y = 0, throw line Z = 0, corridor along -Z.
-- `distance` is studs from the throw line, `side` is studs out from the corridor's middle.
-- A prop list is { name, weight, scale = { min, max } }: heavier ones turn up more often.
-- A biome's `overhead` list puts props across the corridor at fixed spots, resting on both rims; `walls`
-- puts them on a wall's top edge facing the middle; `spots` puts set pieces anywhere, on the rim or the floor.
return {
	-- Along each biome's stretch of the corridor. Biomes without props imported are skipped.
	corridor = {
		Forest = {
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

		-- Sparser than Forest: open sand with cacti, dry grass and old bones, red rock up top.
		-- Props from assets/models/build_desert.py.
		Desert = {
			seed = 12,

			floor = {
				firstDistance = 12,
				gap = { 16, 30 },
				side = { 20, 27 },
				props = {
					{ name = "prop_Saguaro", weight = 22, scale = { 1.2, 1.6 } },
					{ name = "prop_BarrelCactus", weight = 14, scale = { 1.2, 1.6 } },
					{ name = "prop_Skull", weight = 12, scale = { 1.3, 1.8 } },
					{ name = "prop_Boulder", weight = 14, scale = { 1.2, 1.7 } },
					{ name = "prop_DeadTree", weight = 12, scale = { 1.2, 1.5 } },
					{ name = "prop_Tumbleweed", weight = 10, scale = { 1.1, 1.5 } },
					{ name = "prop_DryGrass", weight = 10, scale = { 1.3, 1.8 } },
					{ name = "prop_RibCage", weight = 4, scale = { 1.3, 1.6 } },
				},
				extras = {
					chance = 0.55,
					spread = 8,
					props = {
						{ name = "prop_DryGrass", weight = 4, scale = { 0.9, 1.3 } },
						{ name = "prop_Tumbleweed", weight = 2, scale = { 0.7, 1 } },
						{ name = "prop_Boulder", weight = 2, scale = { 0.5, 0.8 } },
					},
				},
			},

			-- Mesas, giant cacti and the bones of something enormous along the rims.
			rim = {
				firstDistance = 8,
				gap = { 20, 34 },
				chance = 0.8,
				side = { 56, 94 },
				props = {
					{ name = "prop_Mesa", weight = 5, scale = { 1.8, 2.6 } },
					{ name = "prop_Saguaro", weight = 4, scale = { 2, 2.6 } },
					{ name = "prop_RibCage", weight = 2, scale = { 2.2, 3 } },
					{ name = "prop_Skull", weight = 2, scale = { 2.5, 3.2 } },
					{ name = "prop_DeadTree", weight = 2, scale = { 2, 2.6 } },
				},
			},
		},

		-- Murky and overgrown: mossy cypresses and willows, reeds, lily pads and bubbling bog, with
		-- lanterns and giant glowing toadstools for colour. Props from assets/models/build_swamp.py.
		Swamp = {
			seed = 21,

			floor = {
				firstDistance = 10,
				gap = { 12, 24 },
				side = { 20, 27 },
				props = {
					{ name = "prop_SwampTree", weight = 18, scale = { 1.4, 1.8 } },
					{ name = "prop_Cattails", weight = 16, scale = { 1.3, 1.8 } },
					{ name = "prop_Lilypads", weight = 14, scale = { 1.2, 1.6 } },
					{ name = "prop_MossyLog", weight = 12, scale = { 1.3, 1.7 } },
					{ name = "prop_GlowShrooms", weight = 10, scale = { 1.2, 1.6 } },
					{ name = "prop_BogPool", weight = 10, scale = { 1.2, 1.5 } },
					{ name = "prop_Willow", weight = 10, scale = { 1.3, 1.6 } },
					{ name = "prop_SwampLantern", weight = 8, scale = { 1.4, 1.7 } },
				},
				extras = {
					chance = 0.6,
					spread = 8,
					props = {
						{ name = "prop_Cattails", weight = 4, scale = { 0.8, 1.2 } },
						{ name = "prop_Lilypads", weight = 3, scale = { 0.7, 1 } },
						{ name = "prop_GlowShrooms", weight = 2, scale = { 0.6, 0.9 } },
					},
				},
			},

			-- Big mossy trees, a hut on stilts and huge toadstools up on the rims.
			rim = {
				firstDistance = 6,
				gap = { 18, 30 },
				chance = 0.85,
				side = { 56, 94 },
				props = {
					{ name = "prop_SwampTree", weight = 5, scale = { 2, 2.6 } },
					{ name = "prop_Willow", weight = 4, scale = { 2, 2.5 } },
					{ name = "prop_StiltHut", weight = 2, scale = { 1.6, 2 } },
					{ name = "prop_GlowShrooms", weight = 2, scale = { 2.2, 2.8 } },
					{ name = "prop_Cattails", weight = 2, scale = { 2.2, 2.8 } },
					{ name = "prop_BogPool", weight = 1, scale = { 2, 2.6 } },
				},
			},

			-- Across the corridor from rim to rim, studs from the world's start. The log is modelled
			-- lying along X, so yaw stays small or it won't reach both rims.
			overhead = {
				{ name = "prop_LogBridge", distance = 150, yaw = 6, scale = 1 },
				{ name = "prop_LogBridge", distance = 430, yaw = -8, scale = 1.1 },
			},
		},

		-- Dark rock, black glass and lava: lava pools, obsidian spires, charred trees, basalt and steam vents
		-- on the floor and the rims, smoking volcanoes up top, lava pouring down the walls, cracks of lava
		-- across the floor and arches of rock over it. Props from assets/models/build_volcano.py.
		Volcano = {
			seed = 31,

			floor = {
				firstDistance = 12,
				gap = { 14, 26 },
				side = { 20, 27 },
				props = {
					{ name = "prop_LavaPool", weight = 16, scale = { 1.2, 1.6 } },
					{ name = "prop_ObsidianSpire", weight = 14, scale = { 1.2, 1.6 } },
					{ name = "prop_CharredTree", weight = 14, scale = { 1.3, 1.7 } },
					{ name = "prop_BasaltColumns", weight = 12, scale = { 1.2, 1.6 } },
					{ name = "prop_LavaRock", weight = 12, scale = { 1.2, 1.7 } },
					{ name = "prop_SteamVent", weight = 10, scale = { 1.2, 1.5 } },
					{ name = "prop_FireFlower", weight = 8, scale = { 1.3, 1.8 } },
				},
				extras = {
					chance = 0.55,
					spread = 8,
					props = {
						{ name = "prop_FireFlower", weight = 4, scale = { 0.8, 1.2 } },
						{ name = "prop_LavaRock", weight = 3, scale = { 0.5, 0.8 } },
						{ name = "prop_BasaltColumns", weight = 2, scale = { 0.5, 0.7 } },
					},
				},
			},

			rim = {
				firstDistance = 10,
				gap = { 22, 34 },
				chance = 0.8,
				side = { 56, 94 },
				props = {
					{ name = "prop_ObsidianSpire", weight = 4, scale = { 2, 2.8 } },
					{ name = "prop_CharredTree", weight = 4, scale = { 2, 2.6 } },
					{ name = "prop_BasaltColumns", weight = 3, scale = { 2, 2.6 } },
					{ name = "prop_SteamVent", weight = 2, scale = { 2, 2.4 } },
					{ name = "prop_LavaPool", weight = 2, scale = { 2, 2.6 } },
				},
			},

			-- Arches of rock across the corridor, lava running over them.
			overhead = {
				{ name = "prop_RockArch", distance = 230, yaw = 0, scale = 1 },
				{ name = "prop_RockArch", distance = 560, yaw = 5, scale = 1.1 },
			},

			-- Lava falls pouring off a wall's top edge into the corridor. side: 1 for the +X wall, -1 the other.
			walls = {
				{ name = "prop_LavaFall", distance = 70, side = 1 },
				{ name = "prop_LavaFall", distance = 190, side = -1 },
				{ name = "prop_LavaFall", distance = 330, side = 1 },
				{ name = "prop_LavaFall", distance = 450, side = -1 },
				{ name = "prop_LavaFall", distance = 620, side = 1 },
			},

			-- Set pieces at fixed spots. x: studs from the corridor's middle; on: "rim" (up top) or "floor".
			-- The cracks are flat, so they can lie in the middle where the eggs land.
			spots = {
				{ name = "prop_Volcano", distance = 60, x = 74, on = "rim", yaw = 20, scale = 1.7 },
				{ name = "prop_Volcano", distance = 290, x = -76, on = "rim", yaw = 200, scale = 1.9 },
				{ name = "prop_Volcano", distance = 470, x = 72, on = "rim", yaw = 110, scale = 1.6 },
				{ name = "prop_LavaCracks", distance = 40, x = -4, on = "floor", yaw = 15, scale = 1.3 },
				{ name = "prop_LavaCracks", distance = 140, x = 6, on = "floor", yaw = 160, scale = 1.2 },
				{ name = "prop_LavaCracks", distance = 260, x = -2, on = "floor", yaw = 80, scale = 1.4 },
				{ name = "prop_LavaCracks", distance = 380, x = 3, on = "floor", yaw = 220, scale = 1.3 },
				{ name = "prop_LavaCracks", distance = 500, x = -5, on = "floor", yaw = 300, scale = 1.2 },
				{ name = "prop_LavaCracks", distance = 610, x = 4, on = "floor", yaw = 40, scale = 1.4 },
			},
		},

		-- Snow and ice: snowy pines, ice crystals, boulders, drifts and frosted bushes, with an igloo or a
		-- campfire for a warm spot; a glacier and giant mammoth tusks on the rims, frozen waterfalls down the
		-- walls, frozen ponds across the floor and an ice arch over it. Props from
		-- assets/models/build_frozen_peaks.py; its monsters are in build_frozen_peaks_monsters.py.
		FrozenPeaks = {
			seed = 41,

			floor = {
				firstDistance = 12,
				gap = { 14, 26 },
				side = { 20, 27 },
				props = {
					{ name = "prop_SnowPine", weight = 20, scale = { 1.3, 1.7 } },
					{ name = "prop_IceSpikes", weight = 14, scale = { 1.2, 1.6 } },
					{ name = "prop_IceBoulder", weight = 12, scale = { 1.2, 1.6 } },
					{ name = "prop_SnowDrift", weight = 12, scale = { 1.2, 1.6 } },
					{ name = "prop_FrostBush", weight = 10, scale = { 1.3, 1.7 } },
					{ name = "prop_Igloo", weight = 6, scale = { 1.2, 1.4 } },
					{ name = "prop_Campfire", weight = 5, scale = { 1.3, 1.6 } },
				},
				extras = {
					chance = 0.55,
					spread = 8,
					props = {
						{ name = "prop_SnowDrift", weight = 4, scale = { 0.6, 0.9 } },
						{ name = "prop_FrostBush", weight = 3, scale = { 0.7, 1 } },
						{ name = "prop_IceSpikes", weight = 2, scale = { 0.5, 0.7 } },
					},
				},
			},

			rim = {
				firstDistance = 8,
				gap = { 18, 30 },
				chance = 0.85,
				side = { 56, 94 },
				props = {
					{ name = "prop_SnowPine", weight = 6, scale = { 2, 2.6 } },
					{ name = "prop_IceSpikes", weight = 3, scale = { 2, 2.6 } },
					{ name = "prop_IceBoulder", weight = 2, scale = { 2, 2.6 } },
					{ name = "prop_Igloo", weight = 1, scale = { 1.8, 2.2 } },
				},
			},

			overhead = {
				{ name = "prop_IceArch", distance = 250, yaw = 0, scale = 1 },
				{ name = "prop_IceArch", distance = 620, yaw = -4, scale = 1.1 },
			},

			walls = {
				{ name = "prop_Icefall", distance = 60, side = -1 },
				{ name = "prop_Icefall", distance = 200, side = 1 },
				{ name = "prop_Icefall", distance = 360, side = -1 },
				{ name = "prop_Icefall", distance = 500, side = 1 },
				{ name = "prop_Icefall", distance = 700, side = -1 },
			},

			spots = {
				{ name = "prop_Glacier", distance = 90, x = 72, on = "rim", yaw = 10, scale = 1.3 },
				{ name = "prop_GiantTusks", distance = 300, x = -70, on = "rim", yaw = 80, scale = 1.6 },
				{ name = "prop_Glacier", distance = 450, x = -73, on = "rim", yaw = 190, scale = 1.4 },
				{ name = "prop_GiantTusks", distance = 680, x = 70, on = "rim", yaw = 100, scale = 1.7 },
				{ name = "prop_FrozenPond", distance = 40, x = -3, on = "floor", yaw = 20, scale = 1.2 },
				{ name = "prop_FrozenPond", distance = 160, x = 5, on = "floor", yaw = 140, scale = 1.3 },
				{ name = "prop_FrozenPond", distance = 300, x = -4, on = "floor", yaw = 70, scale = 1.2 },
				{ name = "prop_FrozenPond", distance = 420, x = 2, on = "floor", yaw = 200, scale = 1.4 },
				{ name = "prop_FrozenPond", distance = 560, x = -2, on = "floor", yaw = 300, scale = 1.2 },
				{ name = "prop_FrozenPond", distance = 740, x = 4, on = "floor", yaw = 40, scale = 1.3 },
			},
		},

		-- A tar pit at dusk: crooked black trees with hanging moss, thorny brambles, slate shards, bubbling tar,
		-- dead reeds, snapping plants, will-o'-wisps and a hollow stump with eyes in it; the skeletons of huge
		-- long-necked things sinking in the tar on the rims, tar oozing down the walls, flat tar pits across the
		-- floor and arches of braided roots over it. Props from assets/models/build_shadow_bog.py.
		ShadowBog = {
			seed = 51,

			floor = {
				firstDistance = 12,
				gap = { 14, 26 },
				side = { 20, 27 },
				props = {
					{ name = "prop_GloomTree", weight = 18, scale = { 1.3, 1.7 } },
					{ name = "prop_ThornBush", weight = 14, scale = { 1.3, 1.7 } },
					{ name = "prop_GloomRock", weight = 12, scale = { 1.2, 1.6 } },
					{ name = "prop_TarBubbles", weight = 12, scale = { 1.2, 1.6 } },
					{ name = "prop_ShadowReeds", weight = 12, scale = { 1.2, 1.6 } },
					{ name = "prop_BogSnapper", weight = 10, scale = { 1.2, 1.5 } },
					{ name = "prop_Wisps", weight = 8, scale = { 1.2, 1.5 } },
					{ name = "prop_HollowStump", weight = 6, scale = { 1, 1.2 } },
				},
				extras = {
					chance = 0.6,
					spread = 8,
					props = {
						{ name = "prop_ShadowReeds", weight = 4, scale = { 0.7, 1 } },
						{ name = "prop_ThornBush", weight = 3, scale = { 0.6, 0.9 } },
						{ name = "prop_GloomRock", weight = 2, scale = { 0.5, 0.7 } },
					},
				},
			},

			rim = {
				firstDistance = 8,
				gap = { 18, 30 },
				chance = 0.85,
				side = { 56, 94 },
				props = {
					{ name = "prop_GloomTree", weight = 6, scale = { 2, 2.6 } },
					{ name = "prop_HollowStump", weight = 2, scale = { 1.6, 2 } },
					{ name = "prop_BogSnapper", weight = 2, scale = { 2, 2.4 } },
					{ name = "prop_ThornBush", weight = 2, scale = { 2, 2.6 } },
					{ name = "prop_Wisps", weight = 2, scale = { 2, 2.4 } },
				},
			},

			overhead = {
				{ name = "prop_RootArch", distance = 260, yaw = 0, scale = 1 },
				{ name = "prop_RootArch", distance = 640, yaw = 5, scale = 1.1 },
			},

			walls = {
				{ name = "prop_TarFall", distance = 80, side = 1 },
				{ name = "prop_TarFall", distance = 220, side = -1 },
				{ name = "prop_TarFall", distance = 400, side = 1 },
				{ name = "prop_TarFall", distance = 560, side = -1 },
				{ name = "prop_TarFall", distance = 780, side = 1 },
			},

			-- The tar pits are flat, so they can lie in the middle where the eggs land.
			spots = {
				{ name = "prop_SunkenSkeleton", distance = 110, x = 74, on = "rim", yaw = 200, scale = 1.5 },
				{ name = "prop_SunkenSkeleton", distance = 380, x = -72, on = "rim", yaw = 20, scale = 1.4 },
				{ name = "prop_SunkenSkeleton", distance = 700, x = 73, on = "rim", yaw = 160, scale = 1.6 },
				{ name = "prop_TarPit", distance = 50, x = -3, on = "floor", yaw = 20, scale = 1.2 },
				{ name = "prop_TarPit", distance = 170, x = 5, on = "floor", yaw = 140, scale = 1.3 },
				{ name = "prop_TarPit", distance = 300, x = -4, on = "floor", yaw = 70, scale = 1.2 },
				{ name = "prop_TarPit", distance = 450, x = 2, on = "floor", yaw = 200, scale = 1.4 },
				{ name = "prop_TarPit", distance = 590, x = -2, on = "floor", yaw = 300, scale = 1.2 },
				{ name = "prop_TarPit", distance = 730, x = 4, on = "floor", yaw = 40, scale = 1.3 },
				{ name = "prop_TarPit", distance = 850, x = -3, on = "floor", yaw = 110, scale = 1.2 },
			},
		},

		-- The bottom of the ocean, the most decorated world: a reef in warm colours (branching and brain coral,
		-- tube sponges, anemones, giant clams, tube worms, urchins and starfish, kelp and sea grass) with glowing
		-- jellyfish drifting over it, hydrothermal vents, an anchor or a treasure chest now and then; shipwrecks and
		-- giant ammonite shells on the rims, reefs down the walls, coral arches over the corridor and shell patches
		-- across the floor. Denser than the other worlds. Props from assets/models/build_abyss.py.
		Abyss = {
			seed = 61,

			floor = {
				firstDistance = 10,
				gap = { 10, 20 },
				side = { 19, 27 },
				props = {
					{ name = "prop_BranchCoral", weight = 16, scale = { 1.3, 1.7 } },
					{ name = "prop_Kelp", weight = 14, scale = { 1.2, 1.6 } },
					{ name = "prop_BrainCoral", weight = 10, scale = { 1.2, 1.6 } },
					{ name = "prop_TubeSponges", weight = 10, scale = { 1.2, 1.6 } },
					{ name = "prop_Anemones", weight = 10, scale = { 1.2, 1.6 } },
					{ name = "prop_SeaUrchins", weight = 8, scale = { 1.2, 1.6 } },
					{ name = "prop_Jellyfish", weight = 8, scale = { 1.1, 1.4 } },
					{ name = "prop_TubeWorms", weight = 7, scale = { 1.2, 1.6 } },
					{ name = "prop_GiantClam", weight = 6, scale = { 1.1, 1.4 } },
					{ name = "prop_ThermalVent", weight = 4, scale = { 1.1, 1.4 } },
					{ name = "prop_Anchor", weight = 3, scale = { 1.1, 1.3 } },
					{ name = "prop_TreasureChest", weight = 2, scale = { 1.2, 1.4 } },
				},
				extras = {
					chance = 0.75,
					spread = 8,
					props = {
						{ name = "prop_SeaGrass", weight = 5, scale = { 0.8, 1.2 } },
						{ name = "prop_BrainCoral", weight = 2, scale = { 0.5, 0.7 } },
						{ name = "prop_SeaUrchins", weight = 2, scale = { 0.5, 0.8 } },
						{ name = "prop_Anemones", weight = 2, scale = { 0.5, 0.8 } },
					},
				},
			},

			rim = {
				firstDistance = 6,
				gap = { 14, 24 },
				chance = 0.9,
				side = { 54, 96 },
				props = {
					{ name = "prop_Kelp", weight = 5, scale = { 2, 2.6 } },
					{ name = "prop_BranchCoral", weight = 5, scale = { 2, 2.6 } },
					{ name = "prop_BrainCoral", weight = 2, scale = { 2, 2.6 } },
					{ name = "prop_TubeSponges", weight = 2, scale = { 2, 2.4 } },
					{ name = "prop_Jellyfish", weight = 3, scale = { 1.8, 2.2 } },
					{ name = "prop_SeaGrass", weight = 2, scale = { 2.2, 2.8 } },
				},
			},

			overhead = {
				{ name = "prop_CoralArch", distance = 200, yaw = 0, scale = 1 },
				{ name = "prop_CoralArch", distance = 520, yaw = -5, scale = 1.1 },
				{ name = "prop_CoralArch", distance = 850, yaw = 4, scale = 1 },
			},

			walls = {
				{ name = "prop_WallReef", distance = 60, side = 1 },
				{ name = "prop_WallReef", distance = 190, side = -1 },
				{ name = "prop_WallReef", distance = 330, side = 1 },
				{ name = "prop_WallReef", distance = 470, side = -1 },
				{ name = "prop_WallReef", distance = 610, side = 1 },
				{ name = "prop_WallReef", distance = 760, side = -1 },
				{ name = "prop_WallReef", distance = 900, side = 1 },
			},

			-- The shell patches are flat, so they can lie in the middle where the eggs land.
			spots = {
				{ name = "prop_Shipwreck", distance = 140, x = -74, on = "rim", yaw = 20, scale = 1.3 },
				{ name = "prop_Ammonite", distance = 400, x = 72, on = "rim", yaw = 90, scale = 1.6 },
				{ name = "prop_Shipwreck", distance = 640, x = 75, on = "rim", yaw = 200, scale = 1.3 },
				{ name = "prop_Ammonite", distance = 820, x = -72, on = "rim", yaw = 250, scale = 1.7 },
				{ name = "prop_ShellPatch", distance = 40, x = -3, on = "floor", yaw = 20, scale = 1.2 },
				{ name = "prop_ShellPatch", distance = 160, x = 5, on = "floor", yaw = 140, scale = 1.3 },
				{ name = "prop_ShellPatch", distance = 280, x = -4, on = "floor", yaw = 70, scale = 1.2 },
				{ name = "prop_ShellPatch", distance = 410, x = 2, on = "floor", yaw = 200, scale = 1.4 },
				{ name = "prop_ShellPatch", distance = 540, x = -2, on = "floor", yaw = 300, scale = 1.2 },
				{ name = "prop_ShellPatch", distance = 680, x = 4, on = "floor", yaw = 40, scale = 1.3 },
				{ name = "prop_ShellPatch", distance = 800, x = -3, on = "floor", yaw = 110, scale = 1.2 },
				{ name = "prop_ShellPatch", distance = 930, x = 3, on = "floor", yaw = 250, scale = 1.3 },
			},
		},

		-- The last world, where the stars came down, at night: crystal clusters with a shard floating over them,
		-- alien star-flowers, moon rocks, glowing meteorites, glowing tufts and now and then a crashed probe on
		-- the floor; floating rocks, crystals and star lamps on the rims, with landmarks among them (a fallen
		-- star in its crater, crystal spires with a turning halo, observatories), ringed planets and comets in the
		-- sky beyond them, stardust pouring down the walls, crystal arches over the corridor and star-scorched
		-- craters across the floor. Props from assets/models/build_starfall_crater.py; what moves is in
		-- Config/PropMotion.
		StarfallCrater = {
			seed = 71,

			floor = {
				firstDistance = 12,
				gap = { 13, 24 },
				side = { 20, 27 },
				props = {
					{ name = "prop_StarCrystals", weight = 16, scale = { 1.2, 1.6 } },
					{ name = "prop_StarBloom", weight = 14, scale = { 1.2, 1.6 } },
					{ name = "prop_MoonRock", weight = 12, scale = { 1.2, 1.6 } },
					{ name = "prop_Meteorite", weight = 10, scale = { 1.1, 1.4 } },
					{ name = "prop_GlowTufts", weight = 10, scale = { 1.3, 1.7 } },
					{ name = "prop_CrashedProbe", weight = 5, scale = { 1.1, 1.3 } },
				},
				extras = {
					chance = 0.65,
					spread = 8,
					props = {
						{ name = "prop_GlowTufts", weight = 5, scale = { 0.8, 1.1 } },
						{ name = "prop_MoonRock", weight = 3, scale = { 0.5, 0.7 } },
						{ name = "prop_StarBloom", weight = 2, scale = { 0.6, 0.8 } },
					},
				},
			},

			rim = {
				firstDistance = 8,
				gap = { 16, 28 },
				chance = 0.85,
				side = { 56, 94 },
				props = {
					{ name = "prop_StarCrystals", weight = 6, scale = { 2, 2.6 } },
					{ name = "prop_FloatingRocks", weight = 4, scale = { 2, 2.6 } },
					{ name = "prop_StarLamp", weight = 4, scale = { 1.8, 2.2 } },
					{ name = "prop_MoonRock", weight = 3, scale = { 2, 2.6 } },
					{ name = "prop_StarBloom", weight = 3, scale = { 2, 2.4 } },
				},
			},

			overhead = {
				{ name = "prop_CrystalArch", distance = 300, yaw = 0, scale = 1 },
				{ name = "prop_CrystalArch", distance = 760, yaw = 4, scale = 1.1 },
			},

			walls = {
				{ name = "prop_StardustFall", distance = 70, side = 1 },
				{ name = "prop_StardustFall", distance = 210, side = -1 },
				{ name = "prop_StardustFall", distance = 380, side = 1 },
				{ name = "prop_StardustFall", distance = 540, side = -1 },
				{ name = "prop_StardustFall", distance = 700, side = 1 },
				{ name = "prop_StardustFall", distance = 880, side = -1 },
				{ name = "prop_StardustFall", distance = 1020, side = 1 },
			},

			-- Planets and comets hang high in the sky beyond the rims (their models start well above the ground).
			-- The craters are flat, so they can lie in the middle where the eggs land.
			spots = {
				{ name = "prop_FallenStar", distance = 140, x = 78, on = "rim", yaw = 200, scale = 1.6 },
				{ name = "prop_FallenStar", distance = 620, x = -76, on = "rim", yaw = 30, scale = 1.5 },
				{ name = "prop_FallenStar", distance = 1040, x = 80, on = "rim", yaw = 160, scale = 1.8 },
				{ name = "prop_CrystalSpire", distance = 60, x = -72, on = "rim", yaw = 20, scale = 1.6 },
				{ name = "prop_CrystalSpire", distance = 420, x = 74, on = "rim", yaw = 140, scale = 1.5 },
				{ name = "prop_CrystalSpire", distance = 860, x = -74, on = "rim", yaw = 260, scale = 1.7 },
				{ name = "prop_Observatory", distance = 260, x = -82, on = "rim", yaw = 300, scale = 1.5 },
				{ name = "prop_Observatory", distance = 960, x = 84, on = "rim", yaw = 120, scale = 1.4 },
				{ name = "prop_RingedPlanet", distance = 200, x = -130, on = "rim", yaw = 15, scale = 2.4 },
				{ name = "prop_RingedPlanet", distance = 700, x = 140, on = "rim", yaw = 200, scale = 2.8 },
				{ name = "prop_Comet", distance = 100, x = 120, on = "rim", yaw = 120, scale = 2 },
				{ name = "prop_Comet", distance = 480, x = -140, on = "rim", yaw = 300, scale = 2.2 },
				{ name = "prop_Comet", distance = 900, x = 130, on = "rim", yaw = 60, scale = 2 },
				{ name = "prop_StarCrater", distance = 40, x = -3, on = "floor", yaw = 20, scale = 1.2 },
				{ name = "prop_StarCrater", distance = 120, x = 4, on = "floor", yaw = 140, scale = 1.3 },
				{ name = "prop_StarCrater", distance = 230, x = -4, on = "floor", yaw = 70, scale = 1.2 },
				{ name = "prop_StarCrater", distance = 330, x = 3, on = "floor", yaw = 200, scale = 1.4 },
				{ name = "prop_StarCrater", distance = 450, x = -2, on = "floor", yaw = 300, scale = 1.2 },
				{ name = "prop_StarCrater", distance = 560, x = 4, on = "floor", yaw = 40, scale = 1.3 },
				{ name = "prop_StarCrater", distance = 680, x = -3, on = "floor", yaw = 110, scale = 1.2 },
				{ name = "prop_StarCrater", distance = 790, x = 2, on = "floor", yaw = 250, scale = 1.4 },
				{ name = "prop_StarCrater", distance = 900, x = -4, on = "floor", yaw = 330, scale = 1.2 },
				{ name = "prop_StarCrater", distance = 1010, x = 3, on = "floor", yaw = 80, scale = 1.3 },
			},
		},
	},

	-- The arena's props, from the first biome's folder.
	arena = {
		biome = "Forest",

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
