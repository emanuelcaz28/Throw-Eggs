-- The reveal after an egg lands. Times are in seconds.
-- Placeholder numbers; tune during playtesting.
return {
	landingHold = 0.8, -- time to read the distance before the reveal starts
	counterRate = 1.25, -- the "1 in X" counter grows this much per step...
	counterStepTime = 0.125, -- ...every this many seconds, until it hits the real number
	minClimbTime = 2.4, -- shortest time before the final card, even for common catches
	maxClimbTime = 9,
	-- Catches more common than this show nothing about luck: no counter, no luck label, no "1 in X", no tier sticker
	-- (the owner's wish, 2026-11-04: seeing "1 in 160" on every catch made none of them special). [Owner, 2026-11-07] Like
	-- the reference, the counter showing up on the walk is how you know you got something: "1 in 900" is one of the
	-- owner's own examples, so the line came down from 1,000. A plain catch is about 1 in 2 now, so it still shows nothing.
	counterMinOneIn = 100,
	maxTotal = 38, -- [Owner, 2026-11-07] a reveal may take its time, but not past about 40 seconds: walk, climb and hush

	-- The "1 in X" on the walk [Owner, 2026-11-07]. It shows big as the eyes open, already on a random number that depends on
	-- how rare the catch is: a catch that's not that rare starts around 1 in 17, a luckier one higher. It stays locked there
	-- for a while, then creeps up just a little. The numbers only go up for real once the camera has switched to the feet.
	tease = {
		lock = { 2, 3 }, -- seconds locked on the first number, picked at random
		-- The first number is picked at random between these two: `common` at counterMinOneIn, `rarest` at rarestOneIn or
		-- rarer, evenly on a log scale between. It never ends in 0 or 5, so it never looks round.
		common = { 11, 24 },
		rarest = { 58, 89 },
		rarestOneIn = 1000000000,
		rise = { 1.15, 1.5 }, -- on the walk it creeps up to this many times the first number, picked at random...
		most = 97, -- ...never past this, so no luck label lands before the camera switches
		riseEnd = 0.92, -- it reaches its number at this share of the walk
		size = 1.2, -- the counter's size on the walk, with no monster to keep clear of...
		above = 56, -- ...and how many design pixels it sits above the screen's bottom, below the egg
		pop = 1.16, -- each step up pops the number this big
		popTime = 0.16,
	},

	-- Lucky catches (the ones with the counter) take their time (the owner's wish, 2026-11-04): the counter climbs for
	-- minClimb seconds at counterMinOneIn up to maxClimb at rarestOneIn (evenly on a log scale), never stopping: each
	-- luck label slams onto the screen as it's passed while the numbers keep going [Owner, 2026-11-06]. The whole monster is
	-- in view all the while [Owner, 2026-11-06]: the camera pulls back to it early, then creeps slowly in on it to the
	-- last number (closeUp push), while its luck aura builds up round it (aura).
	lucky = {
		minClimb = 6,
		maxClimb = 18,
		rarestOneIn = 100000000000,
		climbPower = 1.5, -- the numbers start slowly and run away at the end: they follow progress ^ this
		grow = 0.3, -- the counter grows by this share over the climb...
		shake = 1.4, -- ...and trembles by up to this many degrees
		holdTime = 0.8, -- how long a slammed label stays where it lands before flying up to the top
		-- Each new label slams in huge in the middle of the screen, then flies up to its place at the top.
		slamScale = 1.6, -- its size where it lands, against its size in its place over the counter...
		slamFrom = 4, -- ...starting this big and see-through, landing in slamIn seconds
		slamIn = 0.28,
		slamFly = 0.3, -- the flight to the top, at the end of the pause
		slamY = 0.44, -- where it lands, as a share of the screen's height: over the counter
		flash = 0.82, -- a flash in the label's colour as it lands: how strong (0 = solid, 1 = none)...
		flashTime = 0.35, -- ...and how fast it fades
		-- The camera jolts as it lands: degrees, by the label (LUCKY! first), dying away over joltTime.
		jolt = { 1.4, 2, 2.8, 3.6, 4.6, 5.8 },
		joltTime = 0.65,
		vignette = { 0.7, 0.35 }, -- the screen's edges darken as the labels go up: see-through (0 = solid), first to rarest
	},
	skipDelay = 0.4, -- ignore taps this soon, so the throw tap can't skip the reveal

	-- The mood of rare and big catches (RevealDrama). [Owner, 2026-11-07] The reveal is the soul of the game. A catch reaches
	-- a level by its "1 in X" or its size mutation's scale, whichever is higher. It starts on the walk, so you feel it
	-- coming. dim: how much of the world's light is left (it multiplies, so the darkest worlds keep their shapes). hush:
	-- seconds of held breath after the last number. minClimb: shortest climb. boom: the unveil's volume. lids: how far the
	-- walk's eyelids stay down (a narrower, meaner look).
	drama = {
		levels = {
			-- [Owner, 2026-11-11: "make sure that monsters are visible"] dim was 0.8, 0.68, 0.56, shadow 0.45 and hushDim
			-- 0.3: together they left under a third of the light on the rarest catches, and the feet could hardly be seen.
			{ oneIn = 1000, scale = 2.2, dim = 0.88, hush = 0.6, minClimb = 9, boom = 0.6, lids = 0.09 },
			{ oneIn = 1000000, scale = 3.2, dim = 0.8, hush = 0.9, minClimb = 13, boom = 0.8, lids = 0.12 },
			{ oneIn = 100000000, scale = 5, dim = 0.72, hush = 1.3, minClimb = 16, boom = 1, lids = 0.15 },
		},
		darkenTime = 2.5, -- slowly, over the first steps of the walk
		shadow = 0.2, -- how far the monster's colours sink towards black until the unveil, on top of the world's dimming
		hushDim = 0.45, -- how much light is left while the world holds its breath
		letterPower = 3, -- the name's letters hold back: they fill in at progress ^ this
		heartSpeed = { 0.8, 1.7 }, -- the heartbeat's speed from the walk to the last number
		heartVolume = 0.7,
		droneVolume = 0.5,
		riseVolume = 0.55, -- strings climbing with the numbers, peaking on the last one...
		riseLength = 19.4, -- ...how long that sound is
		sounds = {
			drone = "rbxassetid://9125485274", -- "Deep Synth Drone Modulating Sub Rumble", Pro Sound Effects
			heart = "rbxassetid://6202853067", -- "Heartbeat (loop)"
			boom = "rbxassetid://9048829865", -- "Doom Maker End Hit", APM
			rise = "rbxassetid://9039693546", -- "Styx Riser", APM
		},
	},

	-- Sounds of every reveal (RevealSound).
	sounds = {
		step = "rbxassetid://9114036511", -- "Deep Impacts 7", Pro Sound Effects: the walk's footfalls
		stepVolume = { 0.06, 0.75 }, -- from the smallest monster to the biggest...
		stepSpeed = { 1.25, 0.55 }, -- ...lower and slower
		tick = "rbxasset://sounds/clickfast.wav", -- built into Roblox: the counter stepping up
		tickVolume = 0.22,
		tickEvery = 0.07, -- never more often than this, while the numbers fly
		tickSpeed = { 0.9, 1.9 }, -- its pitch from the walk to the last number
		roar = "", -- [Owner, 2026-11-08: removed, a weird scream after the reveal] was 9113980319, "Creature Mix Giant Crab Monster Roar"
		roarVolume = { 0.35, 1 }, -- from a first-label catch to the biggest...
		roarSpeed = { 1.15, 0.7 }, -- ...deeper the bigger it is
		-- The egg landing and being cut in half (ElevenLabs). Empty is silent. Only the thrower hears their own throw's sounds;
		-- other players' throws are silent [Owner, 2026-11-08: every sound only for the player it belongs to].
		eggDrop = "rbxassetid://115878085017623", -- sounds/egg_drop_2_loud.mp3 (the first upload was 14 dB too quiet)
		eggSlice = "rbxassetid://105375332927135", -- sounds/egg_slice_1.mp3
		eggVolume = { mine = 0.9 },
		-- [Owner, 2026-11-08] The whoosh when the egg leaves the hand. Same volume as the egg sounds, and only for the thrower.
		throwWhoosh = "rbxassetid://116592483100589",
		throwWhooshSkip = 0.3, -- the file starts with 0.3 s of silence, skipped
		throwWhooshLead = 0.25, -- its loudest part is 0.56 s in, so it starts this much before the release to peak with it
		-- [Owner, 2026-11-08] Plays when the reveal finishes (the whole monster shows) on a big catch: the sizes listed
		-- here. Not too loud, a little louder the bigger the size. Empty is silent.
		bigReveal = "rbxassetid://130323531865053",
		bigRevealSizes = { Chonker = 0.3, MegaChonk = 0.35, PlanetSized = 0.42, UnitOfDoom = 0.5 }, -- size id = volume
		-- [Owner, 2026-11-08] The owner's sound for a plain catch (no luck label: commoner than 1 in 100) when its whole
		-- body shows, and for a tap that skips the reveal, quieter. One play per reveal: a skipped plain catch gets the
		-- skip one only. Empty is silent.
		plainReveal = "rbxassetid://138090834068666",
		plainRevealVolume = 1,
		skipVolume = 0.6,
		-- [Owner, 2026-11-08] every monster slams when its whole body is shown: punchy for the weakest, huge from
		-- hugeFrom up (0 = weakest tier, 1 = rarest), louder the rarer.
		unveilSlam = { hugeFrom = 0.5, volume = { 0.35, 0.6 } },
		-- The tap on the throw meter (ElevenLabs). One soft pop for every level from 1 to 9, and the PERFECT sound on the top
		-- one (it replaces the pop). Empty is silent.
		meterTap = "rbxassetid://72148299314968", -- sounds/meter_tap_pop_b.mp3
		meterPerfect = "rbxassetid://134056799185127", -- [Owner, 2026-11-08] the owner's new PERFECT sound (replaced perfect_voice_dark_unreal, 113022786466445)
		meterTapSkip = 0.2, -- meter_tap_pop_b.mp3 starts with 0.2 s of silence; skipped so the pop lands on the tap
		meterPerfectSkip = 0,
		meterTapVolume = 0.4, -- [Owner, 2026-11-07] low to medium
		meterPerfectVolume = 0.55, -- [Owner] not loud, quieter, but still easy to hear
		-- The slam when a luck label hits the screen with the camera punch (ElevenLabs, uploaded by the owner).
		-- Paste the rbxassetid:// numbers here after uploading; an empty one is simply silent.
		slam = {
			small = "rbxassetid://96964679141367", -- sounds/slam_small_a.mp3: no longer in the reveal, only the 2X XP training hit
			mid = "rbxassetid://86796383601211", -- sounds/slam_punchy_a.mp3
			huge = "rbxassetid://118199520952084", -- sounds/slam_huge_c.mp3
			-- [Owner, 2026-11-08] which one each of the six tiers plays: the weakest is out, the first two get the
			-- second strongest, the rest the strongest. Was small, small, mid, mid, huge, huge.
			weights = { "mid", "mid", "huge", "huge", "huge", "huge" },
			volume = { 1.4, 2.2 }, -- [Owner, 2026-11-08: louder, was 0.6 to 1] from the first tier to the last...
			speed = { 1.1, 0.9 }, -- ...a little deeper each time
			boostVolume = 1.4, -- [Owner, 2026-11-08] the small slam also plays when a training tap hits the 2X XP bubble (BoostMoment)
		},
	},

	-- The server frees the player for the next throw once they finish the reveal,
	-- but never sooner than this.
	minTime = 1,

	caughtBannerMinOneIn = 1000, -- catches this rare keep a "YOU CAUGHT!" banner up afterwards...
	caughtBannerTime = 6, -- ...unless they're rare enough for the lucky catch banner below

	-- After the last letter lands: a white flash, the rarity colour lights the screen's top and bottom edges, and light
	-- rays burst out behind the monster (rays, below). The middle of the screen stays clear, so the monster keeps its
	-- own colours.
	washTime = 1,
	washTransparency = 0.84, -- how strongly the colour covers the top and bottom edges (was 0.72: too strong)
	finalGlow = 0.3, -- the luck tier's edge glow fades down to at most this strength at the end (0 to 1)
	flashTransparency = 0.45, -- how strong the white flash is at its peak...
	flashTime = 0.45, -- ...and how fast it fades
	namePop = 1.35, -- the name lands this big and settles back to normal size

	-- The light rays behind the monster at the final moment (RevealRays). Rays are measured against the monster's size;
	-- each pair of numbers goes from a catch with no luck label to one with the rarest label.
	rays = {
		count = 10, -- rays in the main layer...
		bigCount = 22,
		opacity = 0.45, -- how strong they are at their root (0 to 1)...
		bigOpacity = 0.8,
		turnSpeed = 8, -- degrees a second...
		bigTurnSpeed = 22,
		length = 1.6, -- how far they reach, times the monster's height or width (the bigger)
		shortShare = 0.72, -- every other ray reaches only this share
		width = 0.5, -- how much of the circle a ray's tip covers (1 = rays touching)
		rootWidth = 0.08, -- a ray's width at its root, against its tip
		innerLength = 0.62, -- the thinner rays in between: their reach...
		innerWidth = 0.3, -- ...width...
		innerOpacity = 0.55, -- ...strength...
		innerSpin = 0.6, -- ...and speed, turning the other way
		brightness = 1.6,
		behind = 0.35, -- how far behind the monster's middle, times its size
		downFade = 2.5, -- rays pointing down shrink away: gone 24 degrees below level, so none streak over the ground
		openTime = 0.55, -- they shoot out over this time
		pulse = 0.04, -- they breathe in and out by this share...
		pulseRate = 0.6, -- ...this many times a second
	},

	-- The camera shakes at the final moment on lucky catches: degrees, by the catch's luck label (none for the first
	-- ones), dying away over shakeTime.
	shake = { 0, 1.2, 2, 3, 4, 5.2, 6.8 },
	shakeTime = 1.7,

	-- [Owner, 2026-11-07] A rare catch has to hit hard: the camera shakes more the rarer it is, and instant zooms land on the
	-- big moments. Nothing here touches common catches.
	impact = {
		-- The camera never stops trembling once a label is up: degrees by the label (LUCKY! first), half that at the climb's
		-- start growing to all of it on the last number.
		rumble = { 0.3, 0.5, 0.75, 1.05, 1.4, 1.8 },
		rumbleSpeed = 22, -- how fast it trembles
		-- An instant zoom in as each label lands: the field of view is multiplied by this, by the label...
		zoom = { 0.88, 0.84, 0.8, 0.76, 0.72, 0.68 },
		zoomIn = 0.05, -- ...snapping in this fast...
		zoomHold = 0.12, -- ...holding for this long...
		zoomOut = 0.55, -- ...and easing back in this long
		-- Smaller instant zooms on a beat that speeds up with the numbers, on rare and big catches: by Config drama level...
		beat = { 0.975, 0.96, 0.945 },
		beatEvery = { 2.3, 0.65 }, -- ...seconds between them, from the climb's start to the last number
		beatJolt = 1, -- degrees of camera jolt on each
		arrive = 0.86, -- the switch to the feet lands like a stomp: an instant zoom...
		arriveJolt = 3, -- ...with this many degrees of jolt, dust and a thud
		lastNumber = 0.74, -- the last number snaps in and holds through the held breath...
		-- ...then the unveil snaps wide, showing the whole monster at once, and eases to the final view: the field of view
		-- is multiplied by this, from a catch with no label to the rarest.
		unveilWide = { 1.12, 1.55 },
	},

	-- The dust thrown up when something big lands (RevealDust). Sizes are shares of the monster.
	dust = {
		color = Color3.fromRGB(214, 204, 188),
		size = 0.16, -- a puff's size against the monster's height or width...
		smallest = 1.6, -- ...at least this many studs
		speed = { 0.05, 0.22 }, -- how fast it flies, against the monster's height
		drag = 3,
		life = { 0.7, 1.5 },
		thickest = 0.5, -- how see-through it starts (0 = solid)
		puffs = { 12, 60 }, -- how many, from a small hit to the biggest
	},
	-- [Owner, 2026-11-11] THE SHOWCASE: the cinematic side of the reveal (RevealShowcase, RevealBackdrop; art drawn in Figma
	-- "Throw Eggs - Reveal Showcase", https://www.figma.com/design/i7JF39IAKl4MzhPM4gdFyh). First asked as "multiple angles,
	-- make the monster not move for a better shot, better effects, fill the screen with better visuals", then corrected the
	-- same day: "the cinematic angles should happen while the numbers are going up and the luck still goes up, not after he
	-- gets revealed", and no texts presenting the name, size, rarity and money: "just a better visual for the final reveal".
	-- So: while the numbers climb, each luck label that lands cuts to a close angle on a part of the monster, never its
	-- face. At the unveil the world behind it is swapped for a drawn backdrop in its rarity's colours, so it always stands
	-- out, and the final text lands at once. Angles in degrees, times in seconds.
	showcase = {
		-- Which catches get it. A catch reaches a level by its "1 in X" or its size mutation's scale, whichever is higher; a
		-- monster caught for the first time gets at least the first level (isNew) and a Robux monster the last (special).
		-- timedCuts: how many angles a catch with no luck labels gets (a big or new one; with labels, each label is a cut).
		-- debris: pieces of ground hanging in the air at the unveil. cosmos: the backdrop is outer space with an eclipse.
		-- Commoner catches get none of it.
		levels = {
			{ oneIn = 100, scale = 1.8, isNew = true, timedCuts = 1 },
			{ oneIn = 10000, scale = 2.7, timedCuts = 2, debris = 26 },
			{ oneIn = 1000000, scale = 5, special = true, timedCuts = 3, debris = 44, cosmos = true },
		},
		-- The monster stands still, like a statue, all through the climb (stillClimb), then comes alive at the unveil: it roars
		-- and carries on with its own idle on the final screen [Owner, 2026-11-11: "I don't want him to stand still here",
		-- about the final screen]. freezeAfter: seconds after the unveil it freezes again, or false to never freeze. still: it
		-- doesn't start an attack as it's unveiled, so it roars instead.
		-- [Owner, 2026-11-11] The camera changes angle only as a luck label slams in, with its sound: it holds that angle
		-- until the next label or the unveil, and a catch with no luck labels gets no cuts (timedCuts is then unused).
		labelCutsOnly = true,
		stillClimb = true,
		freezeAfter = false,
		still = true,
		-- The close angles of the climb, played in detailOrder, round again if there are more luck labels than angles. Each
		-- frames a part of the monster: at = where its middle is {up, towards its front} and span = how much of it {across,
		-- up, along}, as shares of the monster (0 is its middle, 0.5 its top or its nose). yaw: how far round from straight
		-- in front the camera stands; elevation: how far above what it looks at; fill: how much of the free screen the part
		-- fills; push: it starts this much further back and creeps in; turn: it starts this many degrees further round.
		-- An angle that would show the monster's eyes, or put the camera inside it, is left out for that monster.
		detailOrder = { "flank", "rear", "claw", "back" },
		details = {
			-- Its side: belly and legs, through a long lens.
			flank = { time = 2.6, fieldOfView = 40, at = { -0.12, -0.14 }, span = { 0.3, 0.6, 0.4 }, yaw = 100, elevation = 1, fill = 0.95, push = 1.12, turn = 7 },
			-- From behind, low, up its back legs and tail.
			rear = { time = 2.6, fieldOfView = 55, at = { -0.2, -0.35 }, span = { 0.7, 0.55, 0.3 }, yaw = 158, elevation = 3, fill = 0.95, push = 1.12, turn = -8 },
			-- Its front feet, from the other side.
			claw = { time = 2.4, fieldOfView = 45, at = { -0.36, 0.3 }, span = { 0.6, 0.26, 0.3 }, yaw = -68, elevation = 2, fill = 0.95, push = 1.14, turn = -6 },
			-- Its back and shoulders, from behind and above.
			back = { time = 2.6, fieldOfView = 50, at = { 0.28, -0.05 }, span = { 0.6, 0.35, 0.6 }, yaw = -150, elevation = 26, fill = 0.95, push = 1.1, turn = 8 },
		},
		-- [Owner, 2026-11-11: "add transitions between the camera angles"] The camera glides to the next angle and back to
		-- the feet, or whip-pans when a glide would pass through the monster: it swings whipAngle degrees away, blurring,
		-- and swings in on the new angle from the other side. Times in seconds. blur: the blur at the peak of a whip
		-- (Roblox BlurEffect size), glideBlur: the share of it a glide gets. checks: points tested along a glide's way.
		-- whipOnly: always whip-pan.
		transition = { glide = 0.5, glideBack = 0.65, whip = 0.38, whipAngle = 40, blur = 18, glideBlur = 0.35, checks = 8, whipOnly = false },
		detailBottom = 0.62, -- they're framed above this share of the screen's height: the counter and the letters are below
		detailLead = 1.4, -- a close angle ends at least this long before the last number: the unveil whips back from the feet
		detailShortest = 1.1, -- ...and one that would be shorter than this isn't started
		-- Each cut lands with a hit: a white flash, speed lines over the screen, an instant zoom and a camera jolt.
		cut = { flash = 0.4, flashTime = 0.22, lines = 0.1, linesTime = 0.28, zoom = 0.9, jolt = 2.2 },
		-- Black cinema bars at the screen's top and bottom while the numbers climb. [Owner, 2026-11-11: "I want those lines
		-- from above to be removed"] Off; true brings them back.
		cinemaBars = false,
		bars = 0.085, -- each bar's share of the screen's height
		barTime = 0.28,
		-- The drawn backdrop behind the monster (RevealBackdrop). Set enabled to false to keep the real world behind it.
		backdrop = {
			enabled = false, -- [Owner, 2026-11-11: the backdrop behind the monster at the end "to be removed as well"]
			pad = 0.12, -- it stands this share of the monster's size behind its furthest point, clear of a lashing tail
			haze = 0.3, -- the world's haze thins to this share while it's up, or it would wash the backdrop out
			darkBelow = 0.38, -- a monster darker than this (0 black to 1 white) gets a brighter backdrop, others a darker one
			keyLight = 1.1, -- ...and a white light of this brightness from the camera, so its shape shows too
			spin = 5, -- degrees a second the sunburst turns
			flicker = 14, -- times a second the speed lines jump
			streakSpeed = 0.9, -- screen heights a second the streaks fly sideways
			starDrift = 0.012, -- screen heights a second the stars drift
			images = { -- uploaded from assets/reveal/, white on see-through, tinted in the game
				sunburst = "rbxassetid://71335050499467",
				speedLines = "rbxassetid://77103256642553",
				halftone = "rbxassetid://73008576912279",
				glow = "rbxassetid://71295354462826",
				corona = "rbxassetid://76741715438887",
				stars = "rbxassetid://117559592495396",
				streaks = "rbxassetid://138216328051858",
			},
		},
		-- Pieces of the ground burst up round the feet at the unveil and hang in the air, hardly moving, while the camera
		-- moves round them. Sizes are shares of the monster's height or width (the bigger).
		debris = {
			size = { 0.012, 0.035 },
			smallest = 0.35, -- studs
			speed = { 0.35, 0.95 }, -- how fast they fly up, in monster heights a second
			fly = 0.28, -- seconds at full speed...
			slowTo = 0.035, -- ...then time slows to this
			slowTime = 0.25,
			color = Color3.fromRGB(120, 112, 100), -- when the ground under the monster can't be found
		},
		dustSlow = 0.25, -- the dust thrown up at the unveil hangs too: its time runs this slow
	},

	-- [Owner, 2026-11-11: "I want the numbers to have more life at the final screen reveal, for bigger numbers, you can do
	-- effects on those numbers and change their colors and doing some crazy stuff"] The "1 in X" on the final screen
	-- (RevealOdds). Lists have one value per luck label, LUCKY! to IMPOSSIBLE!. Sizes in design pixels, times in seconds.
	oddsFx = {
		-- [Owner, 2026-11-11, second look] Only the number moves ("1 in" stays plain) and nothing zooms in and out.
		stagger = 0.05, -- the digits drop in one after the other, this far apart...
		drop = 26, -- ...from this many pixels up...
		dropTurn = { 0, 0 }, -- ...this many degrees slanted at most (LUCKY! to IMPOSSIBLE!; 6 to 30 until 2026-11-11: it looked messy)...
		dropTime = 0.45, -- ...landing with a bounce in this long
		spacing = 2, -- pixels between characters
		-- The digits roll like a slot machine, then lock left to right with a tick, over this long (0 = no roll).
		roll = { 0, 0.7, 0.9, 1.1, 1.3, 1.6 },
		rollStart = 0.2,
		lockKick = 9, -- each digit kicks up this many pixels as it locks...
		lockKickTime = 0.22, -- ...and falls back in this long
		-- How the colour moves: "fixed" in the luck label's colour, "shift" drifting round it by `drift` of the colour
		-- wheel, "rainbow" running through every colour at `rainbowSpeed` turns a second.
		colors = { "fixed", "fixed", "shift", "shift", "rainbow", "rainbow" },
		drift = 0.07,
		rainbowSpeed = 0.35,
		shineEvery = 1.6, -- a white shine sweeps across this often...
		shineTime = 0.55, -- ...taking this long
		-- [Owner, 2026-11-11: the wobbling looked "weird"; he wants it visually better, not busier] Once landed the digits
		-- stay still: no wave, shake or hops, and fewer sparkles.
		wave = { 0, 0, 0, 0, 0, 0 }, -- pixels the digits rise and fall in a wave...
		waveSpeed = 5, -- ...this fast...
		wavePhase = 0.55, -- ...each this far behind the one before
		glow = { 0, 2, 3, 3, 4, 4 }, -- how wide the thin glow round them is (0 = none)...
		glowRate = 1.1, -- ...breaths a second...
		glowFrom = 0.65, -- ...from this see-through...
		glowTo = 0.9, -- ...to this
		jitter = { 0, 0, 0, 0, 0, 0 }, -- degrees each digit shakes...
		hop = { 0, 0, 0, 0, 0, 0 }, -- ...and pixels it hops...
		shakeEvery = 0.07, -- ...a fresh nudge this often
		sparkles = { 0, 0, 0, 0, 2, 2 }, -- sparkles twinkling either side of the number...
		sparkleSize = { 10, 20 }, -- ...pixels across at their biggest
	},


	-- [Owner, 2026-11-11: "I also want a change in these other texts and how they're positioned. I don't feel amazed"] The
	-- final text, laid out like a fighter's entrance (RevealFinalCard): the name on a slash bottom left with the rarity word
	-- above and stickers below, the luck bottom right. Design pixels (a 1280 x 720 screen), measured up from the card's
	-- bottom edge, which sits `bottom` above the screen's; times in seconds.
	finalCard = {
		-- [Owner, 2026-11-11, fourth look: "it's hard to distinguish what's the name of the monster... it looks like I got the
		-- 'secret amethyst monster' instead of 'death knell'. The name should be above him. The rarity tags the same design
		-- the game uses. The 3D space is oriented too much on the sides. The text for what type of luck I got should be more
		-- crazy."] Panels standing in the world in front of the camera: the title over the monster's head, the luck along
		-- the bottom, the money under its feet. Design pixels on a 1280 x 720 screen, measured from the screen's bottom left;
		-- angles in degrees, times in seconds.
		depth = 3, -- studs in front of the camera the panels stand
		margin = 8, -- from the screen's top edge
		titlePitch = 9, -- the title's top leans towards the lens, looming over the monster
		luckPitch = -9, -- the bottom panels' tops lean away, as if lying before its feet
		slamFrom = 0.45, -- the title and the shout fly in from this share of the way nearer the lens...
		slamTime = 0.35, -- ...in this long, landing with a bounce
		sway = 1.5, -- then everything sways this many degrees...
		swayRate = 0.7, -- ...this fast
		titleAt = 0, -- when each appears, after the unveil
		moneyAt = 0.3,
		shoutAt = 0.35,
		-- For framing the monster between the texts: how high the bottom text reaches, how low a giant's feet may go, and
		-- how much of the top the title takes (the name and the row under it).
		frameTop = 215, -- the luck block: number line + shout line (195 when they stood side by side)
		frameFeet = 150,
		frameHead = 166,
		extrudeX = 0.6, -- solid letters step this far sideways for each pixel down
		shineEvery = 2.8, -- a white shine crosses the big words this often...
		shineTime = 0.6, -- ...taking this long
		glintSize = { 12, 26 },
		rowGlintSize = { 7, 13 }, -- smaller round the mutation in the row, so they don't cover its letters
		-- A soft dark band behind the title and one along the bottom behind the luck, so the text reads over any monster.
		shade = 0.5, -- how see-through at its darkest (0 = solid black)
		titleShade = Vector2.new(2600, 300),
		luckShade = Vector2.new(2600, 330),
		pad = 10,
		gap = 4,
		-- TITLE: the NAME, then the row saying what it is (rarity, mutation, size, NEW!).
		titleSize = Vector2.new(940, 210),
		headGap = 4, -- its bottom this far over the monster's head...
		titleLowest = 0.5, -- ...but never lower than this share of the screen's height
		nameSize = 80, -- the headline; a long name shrinks to fit
		nameDepth = 8,
		nameStroke = 6,
		nameAt = 0.05,
		rowHeight = 54,
		rowGap = 16,
		rowAt = 0.3,
		raritySize = 40, -- the game's rarity label (RarityLabel)
		stickerSize = 22,
		mutationSize = 44,
		mutationDepth = 6,
		mutationStroke = 4,
		mutationCaption = 15,
		messageSize = 20,
		messageRow = 28,
		-- The SIZE word: solid letters like the mutation's, with "SIZE" small beside it. By size id (Config/Catch sizes):
		-- colors: its face, top to bottom; side: the solid part; depth: how thick; rumble: degrees it trembles in bursts;
		-- glow: a pulsing aura. Bigger sizes run hotter and thicker.
		sizeWordSize = 36,
		sizeWordStroke = 4,
		sizes = {
			default = { colors = { "#ffffff", "#ffe9b8", "#f2b24a" }, side = "#6b4310", depth = 4 },
			Thicc = { colors = { "#ffffff", "#fff0c4", "#ffcf5c" }, side = "#7a5200", depth = 4 },
			AbsoluteUnit = { colors = { "#fff6dc", "#ffc861", "#ff9a1f" }, side = "#7a3d00", depth = 5 },
			Chonker = { colors = { "#fff0d6", "#ffa64d", "#ff6a1f" }, side = "#7a2a00", depth = 6 },
			MegaChonk = { colors = { "#ffe6d6", "#ff7a4d", "#f0321f" }, side = "#6b0f08", depth = 7, rumble = 1.5 },
			PlanetSized = { colors = { "#f2fbff", "#7fe0ff", "#3a7dff", "#5a3ad6" }, side = "#1a1a66", depth = 8, rumble = 2 },
			UnitOfDoom = { colors = { "#ffd0c2", "#ff3d2e", "#8a0010", "#2a0006" }, side = "#120003", depth = 9, rumble = 3, glow = "#ff2a1a" },
		},
		-- Each mutation's material. colors: its face, top to bottom; side: the solid part; facets: hard bands across it like
		-- a cut gem; shine: a white gleam this often; glints: twinkling stars round it; glow: a dark pulsing aura; flicker:
		-- fading in and out like a ghost; wobble: degrees it wobbles, like jelly.
		mutations = {
			Gold = { colors = { "#fffbe0", "#ffe36b", "#ffc21a", "#c98a0c" }, side = "#7a4d00", shine = 1.6, glints = 6 },
			Ruby = { colors = { "#ffd6de", "#ff5c7c", "#ffd6de", "#e8264c", "#9c0020" }, side = "#5a0012", facets = true, shine = 2.2, glints = 5 },
			Emerald = { colors = { "#d8ffe6", "#3fe07f", "#d8ffe6", "#1fb35c", "#0b6b33" }, side = "#053d1c", facets = true, shine = 2.2, glints = 5 },
			Diamond = { colors = { "#ffffff", "#bfeeff", "#ffffff", "#7fd6ff", "#3aa4e6" }, side = "#1b5f8c", facets = true, shine = 1.4, glints = 8 },
			Amethyst = { colors = { "#f1deff", "#b56bff", "#f1deff", "#8a3be8", "#4e1699" }, side = "#2c0b5c", facets = true, shine = 2.2, glints = 5 },
			Bubblegum = { colors = { "#fff0fa", "#ff9ad6", "#ff5cb8" }, side = "#a3216b", wobble = 4 },
			Shadow = { colors = { "#c9b8ff", "#6a4fd1", "#2a1a66" }, side = "#08031c", glow = "#9d6bff" },
			Ghost = { colors = { "#ffffff", "#eef4ff", "#b8ccff" }, side = "#6f86c4", flicker = true },
		},
		-- LUCK: one centred block along the bottom, the shout over "1 in" and the NUMBER [Owner, 2026-11-11: side by side
		-- they looked like two separate pieces].
		luckBottom = 30, -- above the screen's bottom edge, clear of "tap to continue"
		luckGap = -14, -- the shout's panel overlaps the number's by this much
		shoutSize = Vector2.new(1100, 110),
		-- The shout, one value per luck label from LUCKY! to IMPOSSIBLE LUCK!!!!.
		shout = {
			-- [Owner, 2026-11-11: letters dropping, waving, rocking and shaking one by one looked "weird"] One still line.
			width = 820, -- a line that's wider shrinks to this
			size = { 46, 50, 53, 56, 60, 64 }, -- its letters [Owner, 2026-11-11: a bit smaller, it covered the money]
			depth = { 5, 6, 6, 7, 8, 8 }, -- how thick the solid letters are
			stroke = 5,
			tilt = -2, -- the whole shout leans a touch
			rainbow = { false, false, false, false, false, true }, -- only IMPOSSIBLE's face is a rainbow, drifting along the word...
			rainbowRate = 0.12, -- ...this many times round the colours a second
			rays = { 0, 8, 10, 12, 16, 20 }, -- bars in the burst behind it...
			rayLength = { 0, 120, 135, 150, 170, 190 }, -- ...this long from its middle...
			rayWidth = 12,
			rayStrength = 0.65, -- ...this see-through at the middle (0 = solid)...
			raySpin = 12, -- ...turning this many degrees a second (40 until 2026-11-11)
		},
		numberPanel = Vector2.new(1100, 130),
		numberSize = 84, -- the number's biggest size; a long one shrinks to fit
		numberDepth = 10,
		numberStroke = 6,
		numberAt = 0.55,
		oneInSize = 40, -- "1 in", on the number's line...
		oneInGap = 10, -- ...this far before it
		oneInStroke = 5,
		-- MONEY, under the monster.
		moneySize = Vector2.new(420, 72),
		moneyDepth = 5,
		moneyStroke = 5,
		moneyBelowFeet = 6, -- its top this far under the monster's feet...
		-- ...but its top never lower than this, so its whole height (moneySize.Y) clears the shout's top (luckBottom +
		-- numberPanel.Y + luckGap + shoutSize.Y = 256) [Owner, 2026-11-11: GODLY LUCK covered the $/s; this was 262]...
		moneyLowest = 336,
		moneyLowestPlain = 100, -- ...or than this on a catch with no luck label
		hintSize = 18,
		hintAbove = 4,
	},


	-- After the final tap: fade to white, hold, then fade into the player's base.
	whiteIn = 0.3,
	whiteHold = 0.5,
	whiteOut = 0.4,

	-- The lucky catch banner at the top centre (mock-ups 12 and 12b). Everyone in the server sees it,
	-- even while training. The catcher sees it too, once their own reveal is over.
	luckyBanner = {
		minOneIn = 10000, -- [Guess] tune in playtests; rarer than this is announced to the server
		dropTime = 0.35, -- falls in from above the top edge with a small bounce
		holdTime = 6,
		leaveTime = 0.3,
		gap = 0.4, -- pause between two banners in the queue
		maxQueue = 5, -- a busy server drops the most common waiting catches past this
	},

	-- [Owner, 2026-11-07: the corridor's walls covered big monsters] A monster too wide for the corridor gets more room: on
	-- the catcher's screen only, behind the first cut to black, the walls and everything on them slide apart and the floor
	-- widens with them, until the reveal is over (RevealOpening). Nothing changes for anyone else.
	opening = {
		room = 1.5, -- the walls open until the monster's width times this fits between them
		minGap = 6, -- studs a side: less than this and they stay where they are
		wallBack = 8, -- the new floor reaches this far under the walls
	},

	-- The monster's walk to the egg, seen through its own eyes (RevealWalk, docs/GAME_SPEC.md section 7). It plays
	-- between the landing and the shot from its feet. Angles are in degrees, times in seconds.
	walk = {
		cutDelay = 0.2, -- after the luck panel starts fading out...
		cutIn = 0.1, -- ...a quick cut to black...
		blackHold = 0.15, -- ...held a moment, then the eyes blink open on the walk, already under way (eyes, below).
		blackAfter = 0.12, -- black held before the close-up on the egg fades in
		closeUpFadeIn = 0.2,

		-- How rare the catch is, from its "1 in X": 0 at commonOneIn or commoner, 1 at rarestOneIn or rarer, evenly
		-- on a log scale (1 in 100 is about 0.25, 1 in 10,000 about 0.55, 1 in a million about 0.85).
		commonOneIn = 2,
		rarestOneIn = 10000000,
		-- How big the monster is: its map's standard size times its size mutation (DinoModel.statueScale). 0 at the
		-- first map's standard size, 1 at bigScale (a Unit of Doom on the last map is 16x), evenly on a log scale.
		bigScale = 16,

		-- Where the walk starts, as how far below its eyes the monster sees the egg: a shallow angle is far away.
		-- The commonest catches start at nearAngle and the rarest at farAngle, then bigger monsters look down by up
		-- to bigAngle more, so huge ones start way above the map looking down at a tiny egg. The eyes are the
		-- model's real eye height (its Pupil parts) at its real size, so the distance follows from the angle.
		nearAngle = 8,
		farAngle = 1.8,
		bigAngle = 22,
		maxStartDistance = 1500, -- studs, a cap for the very biggest and rarest
		-- Where it stops [Owner, 2026-11-07: it must get literally to the egg]. Over the last of the walk it lowers its head
		-- to the egg, from bowFrom of the walk's time on: down to bowEggs egg heights plus bowEye of its own eye height
		-- above the ground, so even the biggest ends with its face at the egg. It stops with the egg endReach times that
		-- far ahead, never closer than minEndDistance studs. The cut comes there.
		bowFrom = 0.55,
		bowEggs = 2,
		bowEye = 0.03,
		endReach = 1.1,
		minEndDistance = 4,
		minWalkShare = 0.3, -- it always walks at least this share of where it stops, so a walk never stands still

		-- How long the walk lasts [Owner, 2026-11-07: way slower]: minTime for the commonest, maxTime for the rarest,
		-- plus up to bigExtraTime for the biggest. It slows all the way to the egg, stopping there: slowPower 1 is steady,
		-- higher brakes harder. The steps and the sway die away from calmFrom of the walk on.
		minTime = 4,
		maxTime = 13,
		bigExtraTime = 8,
		slowPower = 1.7,
		calmFrom = 0.8,

		-- It comes along the corridor from the thrower's side, a random few degrees off the middle, and from the
		-- far side when there's no room behind the egg. It stays sideMargin studs inside the corridor's walls.
		approachAngle = 10,
		backMargin = 12, -- studs kept clear of the throw line behind the egg
		sideMargin = 8,

		-- The camera keeps the egg below the middle of the screen: by aimBelow of the angle down to it, but never
		-- more than maxAimBelow degrees. fieldOfView is the camera's while walking.
		aimBelow = 0.35,
		maxAimBelow = 7,
		fieldOfView = 74,
		-- From far away or high up the egg is a speck, so a small glowing dot marks it while it's under markerFrom
		-- pixels tall on screen, fully shown at markerFull pixels and below. markerSize is the dot's own size in
		-- pixels, with a faint ring round it.
		markerFrom = 10,
		markerFull = 4,
		markerSize = 14,
		markerImage = "rbxasset://textures/whiteCircle.png",
		markerColor = Color3.fromRGB(255, 250, 225),

		-- Footsteps. A step covers strideEyes of the monster's eye height, so its pace follows how fast it goes;
		-- steps per second stay between minStepRate and maxStepRate (big monsters hit the slow end).
		strideEyes = 1.1,
		minStepRate = 0.55,
		maxStepRate = 3.2,
		bob = 0.05, -- how far the eyes dip at each footfall, as a share of eye height
		sway = 0.1, -- how far they swing side to side, as a share of eye height
		tilt = 3, -- degrees the horizon tilts each way for the smallest...
		bigTilt = 6, -- ...and for the biggest
		turn = 1.5, -- degrees the head turns each way with the sway
		-- Heavy footfalls: the view jolts down and shakes, more the bigger the monster.
		thudAngle = 0.6, -- degrees for the smallest...
		bigThudAngle = 4, -- ...and the biggest...
		rareThudAngle = 2.5, -- ...plus up to this for the rarest catch
		thudDrop = 0.02, -- share of eye height the view drops on a big footfall (times bigness)
		thudTime = 0.35, -- how quickly a jolt dies away
		-- Swimmers (models with a Swim bone, The Abyss on) glide instead: no footfalls, a slow smooth sway.
		swimRate = 0.7, -- sway cycles per second at the first map's size, slower the bigger

		-- Seen through its eyes [Owner, 2026-11-04: the old rings looked weird and players didn't know what they were]
		-- (Figma "Throw Eggs - Monster Tags & Walk Vision"). The walk opens with a blink: eyelids lift from black and
		-- rest as thin curved lids at the top and bottom, then close for the cut to black at the end. Every catch
		-- blinks. A catch with a colour mutation also gets a soft round glow in its colour at the screen's edges, with
		-- sparkles twinkling in it. No text: the mutation is only named at the end of the reveal.
		eyes = {
			open = 0.35, -- seconds the lids take to open...
			close = 0.18, -- ...and to close at the end
			rest = 0.06, -- share of the screen's height each lid covers in the middle while walking
			curve = 3, -- each lid is the edge of a circle this many screen widths across: bigger is flatter
			color = Color3.fromRGB(10, 6, 2),
		},
		glow = {
			-- Built-in Roblox image, so nothing has to be uploaded.
			darkImage = "rbxasset://textures/loading/loadingvignette.png", -- black, clear in the middle
			darkSize = 1.15, -- the dark edge's size against the screen's diagonal, kept square so it stays round
			darkTransparency = 0.35,
			-- The colour glow: soft bands of colour from a clear middle out to the corners, kept round on any screen.
			-- Sizes are diameters against the screen's diagonal (1 reaches the corners).
			bands = 16,
			innerSize = 0.62, -- the clear middle...
			outerSize = 1.02, -- ...to just past the corners
			innerTransparency = 0.94, -- faint inside...
			outerTransparency = 0.2, -- ...strong at the edges
			fadeTime = 0.3,
			-- Sparkles twinkling in the glow, in its colour lifted towards white.
			sparkles = 10,
			sparkleSize = 26, -- pixels across, before scaling for small screens
			sparkleLift = 0.6,
			sparkleFrom = 0.3, -- how far from the middle they sit, as a share of the screen's diagonal...
			sparkleTo = 0.48,
			twinkle = 1.6, -- twinkles per second
			drift = 0.015, -- how far they drift, as a share of the screen's width
		},
		markerRing = "rbxasset://textures/ui/Input/Ring_padded.png", -- the faint ring round the far-egg dot
	},

	-- [Owner, 2026-11-07] THE shot, the most important part of the reveal. The walk ends, the camera switches to the monster's
	-- feet, and one continuous, very slow zoom out runs while the numbers climb: the body comes into view bit by bit but
	-- never all of it. Only when the numbers finish does the camera whip back to the whole monster (RevealCloseUp, docs/
	-- GAME_SPEC.md section 7). Angles are in degrees, times in seconds.
	closeUp = {
		-- Where the egg lies: between the monster's front feet, as near as fits. A monster under besideBelow egg heights
		-- tall would hide behind the egg, so the egg lies beside its front feet instead (a first-map Compy is about 1.2).
		-- eggGap studs are kept clear round the egg.
		besideBelow = 2.5,
		eggGap = 0.3,
		-- Then the egg lies a little further ahead, this share of the monster's length, so the two never look stuck
		-- together (the owner's wish, 2026-11-04), but never more than maxAhead egg heights.
		aheadShare = 0.15,
		maxAhead = 15,
		aheadAngle = 60, -- degrees off straight ahead, away from the camera's side
		-- The zoom out. The ground under the feet sits feetAt of the way down the screen, above the counter and the letters,
		-- and the camera stays low, looking up (elevation below zero: under what it looks at).
		feetAt = 0.58,
		startWindow = 0.16, -- it opens on this share of the monster's height...
		minWindow = 1.6, -- ...at least this many studs of it...
		countWindow = 0.72, -- ...and when the last number lands this share is in view...
		belowEyes = 0.85, -- ...but never past this share of the height of its eyes, so the face waits for the very end
		startElevation = -8,
		-- Which way it looks from: this far round from straight in front of the monster, starting more from the side, where
		-- a foot stands clear of the head, and turning to the final view as it goes. If the camera would pass through the
		-- monster or show its eyes early, it starts further round, in steps of yawStep, up to yawTries times, either side.
		startYaw = 38,
		endYaw = 16,
		yawStep = 24,
		yawTries = 5,
		backStep = 1.3, -- with no way in from any side, it starts this much further back, up to backTries times
		backTries = 6,
		floorGap = 0.8, -- the camera stays this many studs above the ground
		creep = 1.2, -- the zoom eases into motion: it follows progress ^ this
		hold = 0.25, -- seconds on the feet before it starts moving
		-- The final move: from wherever the count left it to the whole monster, in this long. A tap to skip finishes in skipTime.
		whipTime = 1.1,
		bigWhipTime = 1.6,
		skipTime = 0.5,
		-- Where it ends: the monster and the egg fill the screen with margin to spare, from far enough back that
		-- depthShare of their length is in front of the camera too, looking down from endElevation.
		margin = 1.45, -- room over the head for its roar and its name (1.2 until the name moved over its head, then 1.3; measured 2026-11-11: at 1.3 the head touched the name)
		depthShare = 0.15,
		endElevation = 4, -- low, looking up at the monster a little, so it towers and the egg shows above the text...
		bigEndElevation = 1, -- ...and the biggest from right down on the ground, towering: no walls in the way now
		-- [Owner, 2026-11-11: "the text is covering the face of the monster... zoom out a little bit more on bigger monsters"]
		-- 0.7 until then: a giant overflowed the frame and its head went behind the name.
		bigFill = 1, -- the biggest end this much closer than a perfect fit (0.95 still put a giant's head 3% into the name)
		-- They're framed in the part of the screen the final text leaves free, topGap design pixels under the top bar,
		-- and never in less than minBand of the screen's height.
		topGap = 12,
		textGap = 40, -- design pixels kept clear above the text for small monsters: the egg, nearest the camera, sits lowest
		minBand = 0.4,
		-- The world's haze thins when the camera ends further back than clearDistance studs: scaled by clearDistance
		-- over the distance, down to minHaze (SkyController HazeScale), so a giant seen from far off stays clear.
		clearDistance = 250,
		minHaze = 0.12,
		-- Once it has landed the camera holds still, with no circling (the owner's wish, 2026-11-04). It keeps wallMargin
		-- studs inside the corridor's walls, where they stand for this reveal.
		wallMargin = 4,
	},

	-- The look of the "1 in X" and the luck labels (Figma "Throw Eggs - Reveal Text"): three layers of the same text, a hard
	-- shadow, a rim in the tier's deep colour (rim, below), and the lit text in its dark outline. Sizes in design pixels.
	text = {
		number = { size = 116, ink = 10, rim = 16, drop = 8 },
		lead = { size = 54, ink = 7, rim = 11, drop = 5, raise = 18 }, -- the "1 in", raised to sit on the number's baseline
		label = { size = 46, ink = 6, rim = 10, drop = 4 },
		slam = { size = 84, ink = 9, rim = 14, drop = 7 },
		walkTop = Color3.fromRGB(255, 255, 255), -- the plain number on the walk...
		walkBottom = Color3.fromRGB(217, 223, 242),
	},

	-- Each label appears when the counter passes minOneIn. Lowest first. glow is how strongly the
	-- tier's colour lights the top and bottom of the screen (0 = none, 1 = solid at the edge).
	-- The final screen of a catch with a label shows the
	-- tier's sticker (sticker = its label and {top, bottom} colours). panel colours the lucky catch
	-- banner; more than two colours make a scrolling rainbow.
	tiers = {
		{
			minOneIn = 100,
			label = "LUCKY!",
			rim = Color3.fromRGB(184, 106, 0),
			color = Color3.fromRGB(255, 226, 110),
			glow = 0.1,
			sticker = { label = "LUCKY!", colors = { "#fff1a8", "#ffc21a" } },
			panel = { "#fff1a8", "#ffc21a" },
		},
		{
			minOneIn = 1000,
			label = "SUPER LUCKY!",
			rim = Color3.fromRGB(168, 15, 79),
			color = Color3.fromRGB(255, 110, 150),
			glow = 0.12,
			sticker = { label = "SUPER LUCKY!", colors = { "#ffc2d4", "#ff6e96" } },
			panel = { "#ffc2d4", "#ff6e96" },
		},
		{
			minOneIn = 10000,
			label = "INSANE!",
			rim = Color3.fromRGB(6, 122, 140),
			color = Color3.fromRGB(90, 235, 235),
			glow = 0.14,
			sticker = { label = "INSANE LUCK!", colors = { "#e6ffff", "#5aebeb" } },
			panel = { "#c9fdfd", "#3fd6d6" },
		},
		{
			minOneIn = 100000,
			label = "LEGENDARY!",
			rim = Color3.fromRGB(151, 16, 138),
			color = Color3.fromRGB(255, 120, 220),
			glow = 0.16,
			sticker = { label = "LEGENDARY LUCK!!", colors = { "#ffe8f9", "#ff78dc" } },
			panel = { "#ffd3f3", "#ff6fd2" },
		},
		{
			minOneIn = 1000000,
			label = "GODLY!",
			rim = Color3.fromRGB(47, 138, 20),
			color = Color3.fromRGB(190, 255, 120),
			glow = 0.18,
			sticker = { label = "GODLY LUCK!!!", colors = { "#f4ffe6", "#beff78" } },
			panel = { "#ff8f8f", "#ffd36b", "#b4ff7a", "#6fe3ff", "#c58bff" },
		},
		-- Above a billion: a map's rarest monster with a rare colour and a big size, all at once.
		{
			minOneIn = 1000000000,
			label = "IMPOSSIBLE!",
			rim = Color3.fromRGB(91, 22, 201),
			color = Color3.fromRGB(255, 90, 220),
			glow = 0.2,
			sticker = { label = "IMPOSSIBLE LUCK!!!!", colors = { "#ffe6fb", "#ff5adc" } },
			panel = { "#ff5adc", "#ff8f8f", "#ffd36b", "#b4ff7a", "#6fe3ff", "#c58bff" },
		},
	},
}
