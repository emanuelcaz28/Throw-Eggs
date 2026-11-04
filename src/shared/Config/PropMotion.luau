-- Props whose parts move, on each player's screen only (PropMotionController). The same numbers as MOTION in
-- assets/models/build_starfall_crater.py, whose preview videos show them; keep the two in step.
--
-- Each prop lists the colour roles that move (a moving piece is its own role in Blender, so it's its own part
-- in Studio). A role can:
--   spin   degrees a second round the upright axis, through the prop's pivot ("pivot") or the part's own
--          middle ("self")
--   bob    studs up and down (at the prop's size 1; bigger props move further) over `period` seconds
--   pulse  its glow dims to this share of its colour and back, over `period` seconds
--   fall   drops this many studs (at size 1) over `period` seconds, then starts again
-- "*" moves the whole prop: drift glides it this many studs (in the world, whatever its size) head first,
-- the head being the middle of its `head` parts, over `period` seconds, fading out and in over `fade` of the
-- way at each end, then it starts over.
return {
	range = 700, -- only props this close to the camera move; the rest hold still where they are

	props = {
		prop_StarCrystals = {
			Shard = { bob = 0.5, period = 3.2, spin = 50, about = "self" },
			Motes = { spin = 30, about = "pivot", bob = 0.3, period = 4.5 },
		},
		prop_Meteorite = {
			Core = { pulse = 0.4, period = 2.2 },
		},
		prop_StarBloom = {
			Bloom = { spin = 35, about = "self", bob = 0.15, period = 3 },
		},
		prop_CrashedProbe = {
			Dish = { spin = 60, about = "self" },
			Beacon = { pulse = 0.1, period = 1.1 },
		},
		prop_FloatingRocks = {
			RockA = { bob = 0.6, period = 4.2, spin = 6, about = "self" },
			RockB = { bob = 0.8, period = 5.3, spin = -9, about = "self" },
			RockC = { bob = 0.5, period = 3.7, spin = 12, about = "self" },
		},
		prop_CrystalSpire = {
			Halo = { spin = 18, about = "pivot", bob = 0.6, period = 5 },
		},
		prop_Observatory = {
			Dome = { spin = 8, about = "pivot" },
			Slit = { spin = 8, about = "pivot" },
			Scope = { spin = 8, about = "pivot" },
		},
		prop_StarLamp = {
			LampStar = { spin = 45, about = "self" },
		},
		prop_FallenStar = {
			Motes = { spin = 22, about = "pivot", bob = 0.8, period = 4 },
			StarGlow = { pulse = 0.55, period = 3 },
		},
		prop_RingedPlanet = {
			PlanetA = { spin = 10, about = "pivot" },
			PlanetB = { spin = 10, about = "pivot" },
			Moons = { spin = -16, about = "pivot" },
		},
		prop_Comet = {
			["*"] = { drift = 420, period = 36, fade = 0.12, head = "CometHead" },
		},
		prop_StardustFall = {
			Falling = { fall = 4, period = 0.9 },
		},
		prop_CrystalArch = {
			Gyro = { spin = 40, about = "self" },
		},
	},
}
