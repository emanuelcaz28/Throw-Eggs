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
		-- Forbidden Library (assets/models/build_forbidden_library.py): pages turn by themselves, letters of light
		-- rise, candles flicker and float, quills nod, sand falls, mimics chomp, chained tomes rattle, the clock runs
		-- backwards, books circle the stairs and beat their covers in the sky, and the chandeliers swing.
		prop_OpenTome = {
			FlipPage = { swing = 75, period = 3.2, axis = "ahead", height = 6.24 },
			FlipGlow = { swing = 75, period = 3.2, axis = "ahead", height = 6.24 },
			Spell = { spin = 30, bob = 0.3, period = 3, about = "self" },
			Letters = { fall = -1.5, period = 1.6 },
			InkGlow = { pulse = 0.5, period = 3.5 },
		},
		prop_BookStack = {
			Flame = { bob = 0.06, pulse = 0.55, period = 0.8 },
			FlameCore = { pulse = 0.6, period = 0.5 },
		},
		prop_Bookcase = {
			Flame = { bob = 0.06, pulse = 0.55, period = 0.8 },
			FlameCore = { pulse = 0.6, period = 0.5 },
			Peeper = { pulse = 0.1, period = 4.5 },
		},
		prop_Candelabra = {
			Flame = { bob = 0.06, pulse = 0.55, period = 0.8 },
			FlameCore = { pulse = 0.6, period = 0.5 },
		},
		prop_FloatingCandles = {
			CandleA = { bob = 0.5, period = 3.4 },
			FlameA = { bob = 0.5, pulse = 0.6, period = 3.4 },
			CandleB = { bob = 0.7, period = 4.4 },
			FlameB = { bob = 0.7, pulse = 0.6, period = 4.4 },
		},
		prop_InkWell = {
			Quill = { swing = 9, period = 2.2, axis = "across", height = 4.65 },
			QuillBarb = { swing = 9, period = 2.2, axis = "across", height = 4.65 },
			QuillBand = { swing = 9, period = 2.2, axis = "across", height = 4.65 },
			InkGlow = { pulse = 0.5, period = 3 },
		},
		prop_Hourglass = {
			Grain = { fall = 0.45, period = 0.3 },
			TimeSand = { pulse = 0.7, period = 4 },
		},
		prop_MimicBook = {
			MimicLid = { swing = 14, period = 1.5, axis = "across", height = 1.6 },
			MimicPages = { swing = 14, period = 1.5, axis = "across", height = 1.6 },
			Fangs = { swing = 14, period = 1.5, axis = "across", height = 1.6 },
			MimicBrow = { swing = 14, period = 1.5, axis = "across", height = 1.6 },
			Pupil = { swing = 14, period = 1.5, axis = "across", height = 1.6 },
			Gaze = { swing = 14, pulse = 0.5, period = 1.5, axis = "across", height = 1.6 },
			InkGlow = { pulse = 0.4, period = 1.5 },
		},
		prop_ScrollPile = {
			Flame = { bob = 0.06, pulse = 0.55, period = 0.8 },
			FlameCore = { pulse = 0.6, period = 0.5 },
		},
		prop_SpellPage = {
			SpellRing = { spin = -10 },
			InkGlow = { pulse = 0.4, period = 3.2 },
		},
		prop_PageTree = {
			Moths = { spin = 22, bob = 0.5, period = 3 },
		},
		prop_LeaningShelves = {
			Flutter = { fall = 3, period = 2.6 },
			Lamp = { pulse = 0.7, period = 2.4 },
		},
		prop_ChainedTome = {
			Tome = { swing = 4, period = 0.5, axis = "ahead", height = 4.25 },
			TomePage = { swing = 4, period = 0.5, axis = "ahead", height = 4.25 },
			TomeGilt = { swing = 4, period = 0.5, axis = "ahead", height = 4.25 },
			Lock = { swing = 4, period = 0.5, axis = "ahead", height = 4.25 },
			TomeGlow = { swing = 4, pulse = 0.3, period = 0.5, axis = "ahead", height = 4.25 },
			InkGlow = { pulse = 0.5, period = 3 },
		},
		prop_ClockTower = {
			MinuteHand = { spin = -36, axis = "ahead", height = 18.8 },
			HourHand = { spin = 3, axis = "ahead", height = 18.8 },
			Pendulum = { swing = 16, period = 2, axis = "ahead", height = 16.1 },
			ClockGlow = { pulse = 0.75, period = 4 },
			Orb = { pulse = 0.5, period = 3 },
			InkGlow = { pulse = 0.5, period = 3.6 },
		},
		prop_PopupBook = {
			MoonStick = { swing = 12, period = 3.2, axis = "ahead", height = 1.8 },
			Crescent = { swing = 12, period = 3.2, axis = "ahead", height = 1.8 },
			Bats = { spin = 18, bob = 0.6, period = 3.6 },
			Window = { pulse = 0.6, period = 2.8 },
		},
		prop_SpiralStair = {
			OrbitA = { spin = 12, bob = 0.8, period = 5 },
			OrbitB = { spin = 12, bob = 0.8, period = 5 },
			OrbitPage = { spin = 12, bob = 0.8, period = 5 },
			DoorGlow = { pulse = 0.5, period = 3 },
			InkGlow = { pulse = 0.4, period = 4 },
		},
		prop_SkyTome = {
			CoverL = { swing = 14, bob = 1.2, period = 3, axis = "ahead", height = 46 },
			PageL = { swing = 14, bob = 1.2, period = 3, axis = "ahead", height = 46 },
			InkL = { swing = 14, bob = 1.2, period = 3, axis = "ahead", height = 46 },
			CoverR = { swing = -14, bob = 1.2, period = 3, axis = "ahead", height = 46 },
			PageR = { swing = -14, bob = 1.2, period = 3, axis = "ahead", height = 46 },
			InkR = { swing = -14, bob = 1.2, period = 3, axis = "ahead", height = 46 },
			SkySpine = { bob = 1.2, period = 3 },
			Headband = { bob = 1.2, period = 3 },
			Ribbon = { bob = 1.2, period = 3 },
		},
		prop_InkFall = {
			Falling = { fall = 4, period = 0.8 },
			InkGlow = { pulse = 0.5, period = 3 },
		},
		prop_BookArch = {
			Chain = { swing = 7, period = 3.6, axis = "across", height = 34.5 },
			Chandelier = { swing = 7, period = 3.6, axis = "across", height = 34.5 },
			Taper = { swing = 7, period = 3.6, axis = "across", height = 34.5 },
			Flame = { swing = 7, pulse = 0.6, period = 3.6, axis = "across", height = 34.5 },
		},
		-- Midnight Carnival (assets/models/build_midnight_carnival.py): rides turn, bulbs twinkle, popcorn pops and
		-- pours, clowns bob, the moon sways on its rope. Moving groups share one move so they stay together.
		prop_StripedTent = {
			Flag = { swing = 25, period = 3.2 },
			Bulb = { pulse = 0.4, period = 1.6 },
			Lamp = { pulse = 0.7, period = 2.3 },
		},
		prop_JackBox = {
			Spring = { swing = 10, period = 2.4, axis = "ahead", height = 4.6, bob = 0.4 },
			ClownFace = { swing = 10, period = 2.4, axis = "ahead", height = 4.6, bob = 0.4 },
			Hair = { swing = 10, period = 2.4, axis = "ahead", height = 4.6, bob = 0.4 },
			Nose = { swing = 10, period = 2.4, axis = "ahead", height = 4.6, bob = 0.4 },
			Grin = { swing = 10, period = 2.4, axis = "ahead", height = 4.6, bob = 0.4 },
			Teeth = { swing = 10, period = 2.4, axis = "ahead", height = 4.6, bob = 0.4 },
			EyeWhite = { swing = 10, period = 2.4, axis = "ahead", height = 4.6, bob = 0.4 },
			Pupil = { swing = 10, period = 2.4, axis = "ahead", height = 4.6, bob = 0.4 },
			Ruffle = { swing = 10, period = 2.4, axis = "ahead", height = 4.6, bob = 0.4 },
			RuffleB = { swing = 10, period = 2.4, axis = "ahead", height = 4.6, bob = 0.4 },
			Crank = { spin = 90, axis = "across", about = "self" },
		},
		prop_PopcornCart = {
			Kernels = { fall = -1.2, period = 0.6 },
			Bulb = { pulse = 0.5, period = 1.3 },
		},
		prop_FortuneBooth = {
			TellerFace = { swing = 18, period = 6 },
			Turban = { swing = 18, period = 6 },
			Jewel = { swing = 18, period = 6 },
			Moustache = { swing = 18, period = 6 },
			Trance = { swing = 18, period = 6, pulse = 0.5 },
			Seer = { pulse = 0.35, period = 2.6 },
			Bulb = { pulse = 0.4, period = 1.1 },
		},
		prop_HighStriker = {
			Puck = { bob = 4.4, period = 1.8 },
			Bell = { swing = 10, period = 1.8, axis = "ahead", height = 13.6 },
			Bulb = { pulse = 0.3, period = 0.9 },
		},
		prop_BalloonCart = {
			BalloonA = { swing = 8, period = 3.4, axis = "across", height = 4.2 },
			SmileA = { swing = 8, period = 3.4, axis = "across", height = 4.2 },
			StringA = { swing = 8, period = 3.4, axis = "across", height = 4.2 },
			BalloonB = { swing = 7, period = 4.2, axis = "ahead", height = 4.2 },
			StringB = { swing = 7, period = 4.2, axis = "ahead", height = 4.2 },
			BalloonC = { swing = 9, period = 2.9, axis = "across", height = 4.2 },
			StringC = { swing = 9, period = 2.9, axis = "across", height = 4.2 },
			BalloonD = { swing = 8, period = 3.7, axis = "ahead", height = 4.2 },
			StringD = { swing = 8, period = 3.7, axis = "ahead", height = 4.2 },
		},
		prop_Carousel = {
			Deck = { spin = 25 },
			Column = { spin = 25 },
			Mirror = { spin = 25 },
			Poles = { spin = 25 },
			Canopy = { spin = 25 },
			CanopyLight = { spin = 25 },
			Valance = { spin = 25 },
			Finial = { spin = 25 },
			Bulb = { spin = 25, pulse = 0.45, period = 1.2 },
			SteedA = { spin = 25, bob = 0.5, period = 2 },
			SaddleA = { spin = 25, bob = 0.5, period = 2 },
			SteedB = { spin = 25, bob = -0.5, period = 2 },
			SaddleB = { spin = 25, bob = -0.5, period = 2 },
		},
		prop_BulbPost = {
			Placard = { swing = 14, period = 2.8, axis = "across", height = 7.9 },
			PlacardTrim = { swing = 14, period = 2.8, axis = "across", height = 7.9 },
			Neon = { swing = 14, period = 2.8, axis = "across", height = 7.9, pulse = 0.5 },
			CrowHead = { swing = 40, period = 7 },
			Beak = { swing = 40, period = 7 },
			Gaze = { swing = 40, period = 7 },
			Lamp = { pulse = 0.75, period = 3 },
		},
		prop_CircusRing = {
			Bulb = { spin = 14, pulse = 0.5, period = 1.2 },
			StarRing = { spin = -10 },
			Star = { spin = 6 },
		},
		prop_SwingRide = {
			Canopy = { spin = 45 },
			CanopyLight = { spin = 45 },
			Valance = { spin = 45 },
			Finial = { spin = 45 },
			Chains = { spin = 45 },
			Seats = { spin = 45 },
			SeatBack = { spin = 45 },
			Ghost = { spin = 45 },
			GhostEye = { spin = 45 },
			Bulb = { spin = 45, pulse = 0.5, period = 1 },
		},
		prop_HotAirBalloon = {
			Envelope = { swing = 3, period = 6, axis = "across" },
			EnvelopeB = { swing = 3, period = 6, axis = "across" },
			Band = { swing = 3, period = 6, axis = "across" },
			Rope = { swing = 3, period = 6, axis = "across" },
			Burner = { swing = 3, period = 6, axis = "across" },
			Basket = { swing = 3, period = 6, axis = "across" },
			BasketRim = { swing = 3, period = 6, axis = "across" },
			Sandbag = { swing = 3, period = 6, axis = "across" },
			Flame = { swing = 3, period = 6, axis = "across", pulse = 0.4 },
			Bulb = { swing = 3, period = 6, axis = "across", pulse = 0.5 },
		},
		prop_HelterSkelter = {
			Flag = { swing = 25, period = 3 },
			Bulb = { pulse = 0.4, period = 1.4 },
		},
		prop_FerrisWheel = {
			Wheel = { spin = 8, axis = "ahead", height = 17 },
			Spokes = { spin = 8, axis = "ahead", height = 17 },
			Hub = { spin = 8, axis = "ahead", height = 17 },
			CabinA = { spin = 8, axis = "ahead", height = 17 },
			CabinB = { spin = 8, axis = "ahead", height = 17 },
			CabinTrim = { spin = 8, axis = "ahead", height = 17 },
			Window = { spin = 8, axis = "ahead", height = 17 },
			LampStar = { spin = 8, axis = "ahead", height = 17 },
			Bulb = { spin = 8, axis = "ahead", height = 17, pulse = 0.5, period = 1.5 },
		},
		prop_BigTop = {
			Flag = { swing = 25, period = 3.4 },
			Searchbeam = { spin = 18 },
			Bulb = { pulse = 0.4, period = 1.5 },
			Neon = { pulse = 0.5, period = 2 },
			Lamp = { pulse = 0.75, period = 2.6 },
		},
		prop_FunHouse = {
			SpiralL = { spin = 90, axis = "ahead", about = "self" },
			SpiralR = { spin = -90, axis = "ahead", about = "self" },
			Neon = { pulse = 0.4, period = 1.8 },
			Bulb = { pulse = 0.4, period = 1.1 },
		},
		prop_StageMoon = {
			MoonFace = { swing = 4, period = 7, axis = "ahead", height = 110 },
			Blush = { swing = 4, period = 7, axis = "ahead", height = 110 },
			Rope = { swing = 4, period = 7, axis = "ahead", height = 110 },
			Crescent = { swing = 4, period = 7, axis = "ahead", height = 110, pulse = 0.8 },
			LampStar = { swing = 4, period = 7, axis = "ahead", height = 110, pulse = 0.4 },
		},
		prop_PopcornFall = {
			Kernels = { fall = 4, period = 0.9 },
			Bulb = { pulse = 0.4, period = 1.2 },
		},
		prop_CoasterLoop = {
			Cart = { spin = 60, axis = "ahead", height = 23.4 },
			CartTrim = { spin = 60, axis = "ahead", height = 23.4 },
			Ghost = { spin = 60, axis = "ahead", height = 23.4 },
			GhostEye = { spin = 60, axis = "ahead", height = 23.4 },
			Bulb = { pulse = 0.4, period = 1 },
		},
		-- Clockwork Citadel (assets/models/build_clockwork_citadel.py).
		prop_GearWorks = {
			GearA = { spin = 20, axis = "ahead", about = "self" },
			GearB = { spin = -40, axis = "ahead", about = "self" },
			Steam = { fall = -1.2, period = 0.7 },
			Volt = { pulse = 0.5, period = 1.4 },
		},
		prop_SteamHammer = {
			Hammer = { bob = 0.6, period = 1.1 },
			HammerFace = { bob = 0.6, period = 1.1 },
			Flywheel = { spin = 120, axis = "across", about = "self" },
			Ember = { pulse = 0.6, period = 1.1 },
			Steam = { fall = -1, period = 0.55 },
		},
		prop_SparkCoil = {
			Arc = { pulse = 0.05, period = 0.3 },
			Volt = { pulse = 0.55, period = 1.6 },
			Charge = { spin = 140 },
		},
		prop_Boiler = {
			Needle = { swing = 22, period = 0.9, axis = "ahead", height = 7.6 },
			Furnace = { pulse = 0.55, period = 1.3 },
			Steam = { fall = -1.2, period = 0.7 },
			Smoke = { fall = -1.5, period = 1.4 },
			SmokeLight = { fall = -1.5, period = 1.4 },
		},
		prop_SteamPipes = {
			ValveA = { spin = 50, axis = "ahead", about = "self" },
			ValveB = { spin = -35, axis = "ahead", about = "self" },
			Needle = { swing = 18, period = 1.3, axis = "ahead", height = 1.35 },
			Steam = { fall = -1.2, period = 0.7 },
		},
		prop_Metronome = {
			Arm = { swing = 24, period = 1.6, axis = "ahead", height = 1.8 },
			ArmWeight = { swing = 24, period = 1.6, axis = "ahead", height = 1.8 },
			Key = { spin = 40, axis = "across", about = "self" },
		},
		prop_MusicBox = {
			Drum = { spin = 30, axis = "across", about = "self" },
			Key = { spin = -30, axis = "across", about = "self" },
			Turntable = { spin = 36 },
			Bird = { spin = 36 },
			BirdEye = { spin = 36 },
		},
		prop_PocketWatch = {
			MinuteHand = { spin = -30 },
			HourHand = { spin = -2.5 },
			GearA = { spin = 60, about = "self" },
		},
		prop_ScrapPile = {
			GearA = { spin = 25, axis = "ahead", about = "self" },
			Spark = { pulse = 0.05, period = 0.4 },
		},
		prop_FloorGears = {
			GearA = { spin = 12, about = "self" },
			GearB = { spin = -20, about = "self" },
			Volt = { pulse = 0.4, period = 3 },
		},
		prop_Smokestack = {
			Smoke = { fall = -2.2, period = 1.6 },
			SmokeLight = { fall = -2.2, period = 1.6 },
			Ember = { pulse = 0.6, period = 2.2 },
			Furnace = { pulse = 0.6, period = 1.7 },
		},
		prop_BrassTree = {
			Crown = { spin = 14 },
			Volt = { pulse = 0.45, period = 2.6 },
		},
		prop_FanTower = {
			Fan = { spin = 60, axis = "ahead", height = 15.2 },
			Vane = { swing = 30, period = 6 },
			Lamp = { pulse = 0.7, period = 2.4 },
		},
		prop_CogSpire = {
			GearA = { spin = 12 },
			GearB = { spin = -16 },
			GearC = { spin = 20 },
			GearD = { spin = -26 },
			Volt = { pulse = 0.5, period = 1.8 },
			Arc = { pulse = 0.05, period = 0.35 },
		},
		prop_LightningTower = {
			Arc = { pulse = 0.05, period = 0.4 },
			Volt = { pulse = 0.55, period = 2 },
			Charge = { spin = 90 },
		},
		prop_EngineHouse = {
			Flywheel = { spin = 30, axis = "across", height = 6 },
			Governor = { spin = 150 },
			Smoke = { fall = -1.8, period = 1.4 },
			SmokeLight = { fall = -1.8, period = 1.4 },
			Window = { pulse = 0.8, period = 3 },
		},
		prop_Airship = {
			Envelope = { bob = 1.2, period = 6 },
			EnvelopeDark = { bob = 1.2, period = 6 },
			Band = { bob = 1.2, period = 6 },
			BrassDark = { bob = 1.2, period = 6 },
			Gondola = { bob = 1.2, period = 6 },
			Wood = { bob = 1.2, period = 6 },
			Window = { bob = 1.2, period = 6 },
			Fin = { bob = 1.2, period = 6 },
			IronDark = { bob = 1.2, period = 6 },
			Lamp = { bob = 1.2, period = 6 },
			PropL = { spin = 300, axis = "ahead", about = "self", bob = 1.2, period = 6 },
			PropR = { spin = -300, axis = "ahead", about = "self", bob = 1.2, period = 6 },
		},
		prop_BrassFall = {
			Falling = { fall = 4, period = 0.8 },
			Molten = { pulse = 0.7, period = 2.2 },
			Ember = { fall = -1.5, period = 0.5 },
		},
		prop_GearArch = {
			GearL = { spin = 14, axis = "ahead", about = "self" },
			GearR = { spin = 14, axis = "ahead", about = "self" },
			GearTop = { spin = -11, axis = "ahead", about = "self" },
			Chain = { swing = 8, period = 3.2, axis = "across", height = 29.7 },
			LampCage = { swing = 8, period = 3.2, axis = "across", height = 29.7 },
			Lamp = { swing = 8, period = 3.2, axis = "across", height = 29.7, pulse = 0.7 },
		},
		-- Thorn Kingdom (assets/models/build_thorn_kingdom.py).
		prop_BriarRose = {
			PetalGlow = { fall = 3, period = 2.6 },
			RoseGlow = { pulse = 0.6, period = 3.2 },
			Bud = { pulse = 0.4, period = 2.2 },
		},
		prop_ThornThicket = {
			Motes = { spin = 18, bob = 0.4, period = 3.5 },
			RoseGlow = { pulse = 0.55, period = 2.8 },
		},
		prop_StoneKnight = {
			Chain = { swing = 12, period = 2.4, axis = "across", height = 5.25 },
			Lantern = { swing = 12, period = 2.4, axis = "across", height = 5.25 },
			Lamp = { swing = 12, period = 2.4, axis = "across", height = 5.25, pulse = 0.7 },
			Gaze = { pulse = 0.3, period = 4 },
			RoseGlow = { pulse = 0.6, period = 3.2 },
		},
		prop_SpinningWheel = {
			Wheel = { spin = 40, axis = "ahead", about = "self" },
			Thread = { pulse = 0.6, period = 2.6 },
		},
		prop_BriarLantern = {
			Chain = { swing = 10, period = 2.8, axis = "across", height = 8.1 },
			Lantern = { swing = 10, period = 2.8, axis = "across", height = 8.1 },
			Lamp = { swing = 10, period = 2.8, axis = "across", height = 8.1, pulse = 0.7 },
			Motes = { spin = 20, bob = 0.5, period = 4 },
			RoseGlow = { pulse = 0.6, period = 3.2 },
		},
		prop_Toadstools = {
			Glow = { pulse = 0.5, period = 3 },
			Motes = { spin = 24, bob = 0.4, period = 3 },
			Window = { pulse = 0.8, period = 2.5 },
		},
		prop_RoseFountain = {
			Falling = { fall = 1.2, period = 0.5 },
			Stream = { pulse = 0.75, period = 3 },
		},
		prop_MagicMirror = {
			MirrorGlow = { pulse = 0.55, period = 3.6 },
			Gaze = { pulse = 0.05, period = 5 },
			Motes = { spin = 30, bob = 0.3, period = 3 },
			CrownGem = { pulse = 0.5, period = 2 },
		},
		prop_FloatingCrown = {
			Crown = { spin = 20, bob = 0.3, period = 3 },
			CrownGem = { spin = 20, bob = 0.3, period = 3 },
			Motes = { spin = -20, bob = 0.3, period = 3 },
		},
		prop_BriarTuft = {
			Bud = { pulse = 0.4, period = 2.4 },
		},
		prop_RoseWindow = {
			Pane = { pulse = 0.55, period = 3.4 },
			PaneB = { pulse = 0.6, period = 4.4 },
		},
		prop_ThornTree = {
			PetalGlow = { fall = 3, period = 2.8 },
			RoseGlow = { pulse = 0.6, period = 3.2 },
			Motes = { spin = 14, bob = 0.5, period = 4 },
		},
		prop_Turret = {
			Banner = { swing = 25, period = 3 },
			Window = { pulse = 0.8, period = 3.2 },
			RoseGlow = { pulse = 0.6, period = 3.2 },
		},
		prop_SleepingCastle = {
			BannerA = { swing = 10, period = 3, about = "self" },
			BannerB = { swing = 10, period = 3.4, about = "self" },
			BannerC = { swing = 10, period = 2.7, about = "self" },
			Window = { pulse = 0.8, period = 3.5 },
			RoseGlow = { pulse = 0.6, period = 3.2 },
		},
		prop_RoseTower = {
			PetalOrbit = { spin = 10, bob = 0.6, period = 5 },
			RoseGlow = { pulse = 0.65, period = 3.6 },
			Bud = { pulse = 0.4, period = 2.4 },
			Window = { pulse = 0.8, period = 3 },
		},
		prop_CrookedCottage = {
			Smoke = { fall = -1.6, period = 1.6 },
			SmokeLight = { fall = -1.6, period = 1.6 },
			Vane = { swing = 35, period = 7 },
			Window = { pulse = 0.8, period = 2.6 },
			RoseGlow = { pulse = 0.6, period = 3.2 },
		},
		prop_ThornMoon = {
			Lunar = { bob = 1, period = 9 },
			Crater = { bob = 1, period = 9 },
			Bark = { bob = 1, period = 9 },
			Leaf = { bob = 1, period = 9 },
			Petal = { bob = 1, period = 9 },
			PetalDark = { bob = 1, period = 9 },
			RoseGlow = { bob = 1, period = 9 },
			Raven = { spin = 12, bob = 1, period = 9 },
		},
		prop_BriarCurtain = {
			PetalGlow = { fall = 4, period = 1.4 },
			RoseGlow = { pulse = 0.6, period = 3 },
		},
		prop_StoneBridge = {
			Banner = { swing = 7, period = 3.2, axis = "across", height = 17 },
			Lamp = { pulse = 0.7, period = 2.6 },
			Window = { pulse = 0.8, period = 3.4 },
		},
	},
}
