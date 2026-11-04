-- Props whose parts move, on each player's screen only (PropMotionController). The same numbers as MOTION in
-- each map's Blender script (assets/models/build_starfall_crater.py, build_eclipse_temple.py), whose preview
-- videos show them; keep the two in step.
--
-- Each prop lists the colour roles that move (a moving piece is its own role in Blender, so it's its own part
-- in Studio). A role can:
--   spin   degrees a second round its axis, through the part's own middle (about = "self") or the prop's pivot
--   swing  degrees each way, back and forth over `period` seconds, round its axis like spin: a lantern on its
--          hook, a bell, a head looking from side to side
--          axis   for spin and swing: "up" (the default), "across" (the model's X in Blender) or "ahead" (its Y)
--          height turn round the point this many studs (at size 1) straight above the pivot, instead of the
--                 pivot itself: where a lantern's hook is. Ignored with about = "self".
--   bob    studs up and down (at the prop's size 1; bigger props move further) over `period` seconds
--   pulse  its glow dims to this share of its colour and back, over `period` seconds
--   fall   drops this many studs (at size 1) over `period` seconds, then starts again (negative rises)
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

		-- Eclipse Temple (assets/models/build_eclipse_temple.py, videos in design/world/models_eclipse_temple/).
		prop_GuardianHead = {
			Gaze = { pulse = 0.35, period = 3.4 },
		},
		prop_JungleFronds = {
			Pod = { pulse = 0.45, period = 2.6 },
		},
		prop_JungleTree = {
			Pod = { pulse = 0.45, period = 2.9 },
		},
		prop_HangingLantern = { -- swings on its hook, 7.8 studs up
			Lantern = { swing = 12, period = 2.6, axis = "across", height = 7.8 },
			Lamp = { swing = 12, period = 2.6, axis = "across", height = 7.8 },
		},
		prop_SpiritBrazier = {
			Flame = { pulse = 0.55, period = 0.7, bob = 0.12 },
			FlameCore = { pulse = 0.6, period = 0.45 },
			Ember = { fall = -2, period = 1.3 }, -- sparks rising
		},
		prop_WatcherBloom = { -- the eye looks from side to side
			EyeBall = { swing = 50, period = 7 },
			Iris = { swing = 50, period = 7 },
			Pupil = { swing = 50, period = 7 },
			Lid = { swing = 50, period = 7 },
		},
		prop_Orrery = { -- rings round an orb 8.3 studs up, all floating together
			Orb = { pulse = 0.6, period = 4, bob = 0.3 },
			RingA = { spin = 35, height = 8.3, bob = 0.3, period = 4 },
			Planets = { spin = 35, height = 8.3, bob = 0.3, period = 4 },
			RingB = { spin = -50, height = 8.3, bob = 0.3, period = 4 },
			RingC = { spin = 22, axis = "across", height = 8.3, bob = 0.3, period = 4 },
		},
		prop_StoneHand = {
			Orb = { pulse = 0.5, bob = 0.35, period = 3.6 },
		},
		prop_RuneCircle = {
			RuneOuter = { spin = -8 },
			RuneInner = { spin = 14 },
			Sigil = { pulse = 0.4, period = 3 },
		},
		prop_StepTemple = {
			Orb = { pulse = 0.5, bob = 0.8, period = 5 },
			Glyph = { spin = 20, bob = 0.8, period = 5 },
			Jade = { pulse = 0.6, period = 4 },
		},
		prop_GuardianStatue = { -- its head turns to watch
			StatueHead = { swing = 40, period = 9 },
			Mask = { swing = 40, period = 9 },
			Gaze = { swing = 40, period = 9, pulse = 0.4 },
		},
		prop_FloatingMonoliths = {
			MonolithA = { spin = 10, bob = 0.7, period = 4.4 },
			RuneA = { spin = 10, bob = 0.7, period = 4.4 },
			MonolithB = { spin = 10, bob = 0.9, period = 5.2 },
			RuneB = { spin = 10, bob = 0.9, period = 5.2 },
			MonolithC = { spin = 10, bob = 0.6, period = 3.8 },
			RuneC = { spin = 10, bob = 0.6, period = 3.8 },
			Jade = { pulse = 0.5, period = 3 },
		},
		prop_SkyLanterns = {
			LampA = { spin = 6, bob = 1, period = 5 },
			CapA = { spin = 6, bob = 1, period = 5 },
			LampB = { spin = 6, bob = 1.3, period = 6.2 },
			CapB = { spin = 6, bob = 1.3, period = 6.2 },
			LampC = { spin = 6, bob = 0.8, period = 4.4 },
			CapC = { spin = 6, bob = 0.8, period = 4.4 },
		},
		prop_Eclipse = { -- the corona turns round the black sun
			Corona = { spin = 5, axis = "ahead", about = "self" },
			EclipseRing = { pulse = 0.6, period = 5 },
		},
		prop_FaceFall = {
			Gaze = { pulse = 0.4, period = 3.5 },
			Falling = { fall = 4, period = 0.8 },
		},
		prop_TempleGate = { -- the bell and lanterns swing along the corridor, from under the lintel
			Bell = { swing = 6, period = 4.2, axis = "across", height = 30.6 },
			BellRim = { swing = 6, period = 4.2, axis = "across", height = 30.6 },
			BellGlow = { swing = 6, period = 4.2, axis = "across", height = 30.6, pulse = 0.6 },
			Lantern = { swing = 12, period = 2.8, axis = "across", height = 30.6 },
			Lamp = { swing = 12, period = 2.8, axis = "across", height = 30.6 },
			Jade = { pulse = 0.6, period = 4 },
		},
	},
}
