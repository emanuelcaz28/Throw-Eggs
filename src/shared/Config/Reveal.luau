-- The reveal after an egg lands. Times are in seconds.
-- Placeholder numbers; tune during playtesting.
return {
	landingHold = 0.8, -- time to read the distance before the reveal starts
	counterRate = 1.25, -- the "1 in X" counter grows this much per step...
	counterStepTime = 0.125, -- ...every this many seconds, until it hits the real number
	minClimbTime = 1.5, -- shortest time before the final card, even for common catches
	maxClimbTime = 9,
	-- Catches more common than this show nothing about luck: no counter, no luck label, no "1 in X", no tier sticker
	-- (the owner's wish, 2026-11-04: seeing "1 in 160" on every catch made none of them special).
	counterMinOneIn = 1000,

	-- Lucky catches (the ones with the counter) take their time (the owner's wish, 2026-11-04): the counter climbs for
	-- minClimb seconds at counterMinOneIn up to maxClimb at rarestOneIn (evenly on a log scale), and pauses holdTime
	-- on each luck label it reaches, so 1 in 1,000 takes about 6 seconds and the rarest about 14. Meanwhile the camera
	-- rises slowly from the egg and the feet to the whole monster, ending with the last number (closeUp slowHold).
	lucky = {
		minClimb = 4.5,
		maxClimb = 9,
		rarestOneIn = 100000000000,
		holdTime = 0.8,
		-- Each new label slams in huge in the middle of the screen, then flies up to its place at the top.
		slamScale = 2.3, -- its size in the middle, against its size at the top...
		slamFrom = 4, -- ...starting this big and see-through, landing in slamIn seconds
		slamIn = 0.28,
		slamFly = 0.3, -- the flight to the top, at the end of the pause
		slamY = 0.5, -- where it lands, as a share of the screen's height
		flash = 0.55, -- a flash in the label's colour as it lands: how strong (0 = solid, 1 = none)...
		flashTime = 0.35, -- ...and how fast it fades
		-- The camera jolts as it lands: degrees, by the label (LUCKY! first), dying away over joltTime.
		jolt = { 0.4, 0.6, 0.9, 1.2, 1.6, 2 },
		joltTime = 0.45,
	},
	skipDelay = 0.4, -- ignore taps this soon, so the throw tap can't skip the reveal

	-- The server frees the player for the next throw once they finish the reveal,
	-- but never sooner than this.
	minTime = 1,

	caughtBannerMinOneIn = 1000, -- catches this rare keep a "YOU CAUGHT!" banner up afterwards...
	caughtBannerTime = 6, -- ...unless they're rare enough for the lucky catch banner below

	-- After the last letter lands: a white flash, the rarity colour lights the screen's top and bottom edges, and light
	-- rays burst out behind the monster (rays, below). The middle of the screen stays clear, so the monster keeps its
	-- own colours.
	washTime = 1,
	washTransparency = 0.72, -- how strongly the colour covers the top and bottom edges
	finalGlow = 0.3, -- the luck tier's edge glow fades down to at most this strength at the end (0 to 1)
	flashTransparency = 0.3, -- how strong the white flash is at its peak...
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
	shake = { 0, 0, 0.35, 0.7, 1.1, 1.6, 2.2 },
	shakeTime = 0.9,
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

	-- The monster's walk to the egg, seen through its own eyes (RevealWalk, docs/GAME_SPEC.md section 7). It plays
	-- between the landing and the close-up on the egg. Angles are in degrees, times in seconds.
	walk = {
		cutDelay = 0.2, -- after the luck panel starts fading out...
		cutIn = 0.1, -- ...a quick cut to black...
		blackHold = 0.15, -- ...held a moment...
		fadeIn = 0.15, -- ...then it opens on the walk, already under way.
		cutOut = 0.12, -- the quick cut to black at the end
		blackAfter = 0.12, -- black held before the close-up on the egg fades in
		closeUpFadeIn = 0.2,

		-- How rare the catch is, from its "1 in X": 0 at commonOneIn or commoner, 1 at rarestOneIn or rarer, evenly
		-- on a log scale (1 in 100 is about 0.25, 1 in 10,000 about 0.55, 1 in a million about 0.85).
		commonOneIn = 2,
		rarestOneIn = 10000000,
		-- How big the monster is: its map's standard size times its size mutation (DinoModel.statueScale). 0 at the
		-- first map's standard size, 1 at bigScale (a Unit of Doom on the last map is 50x), evenly on a log scale.
		bigScale = 50,

		-- Where the walk starts, as how far below its eyes the monster sees the egg: a shallow angle is far away.
		-- The commonest catches start at nearAngle and the rarest at farAngle, then bigger monsters look down by up
		-- to bigAngle more, so huge ones start way above the map looking down at a tiny egg. The eyes are the
		-- model's real eye height (its Pupil parts) at its real size, so the distance follows from the angle.
		nearAngle = 8,
		farAngle = 1.8,
		bigAngle = 22,
		maxStartDistance = 1500, -- studs, a cap for the very biggest and rarest
		-- Where it stops: the egg this far below its eyes, from endAngle for the smallest to bigEndAngle for the
		-- biggest, never closer than minEndDistance studs. The cut to black comes there.
		endAngle = 22,
		bigEndAngle = 52,
		minEndDistance = 4,
		minWalkShare = 0.3, -- it always walks at least this share of where it stops, so a walk never stands still

		-- How long the walk lasts: minTime for the commonest, maxTime for the rarest, plus up to bigExtraTime for
		-- the biggest (their steps are slow). The pace eases off as it nears the egg, by slowDown (0 = steady).
		minTime = 2.6,
		maxTime = 4.6,
		bigExtraTime = 0.8,
		slowDown = 0.5,

		-- It comes along the corridor from the thrower's side, a random few degrees off the middle, and from the
		-- far side when there's no room behind the egg. It stays sideMargin studs inside the corridor's walls.
		approachAngle = 10,
		backMargin = 12, -- studs kept clear of the throw line behind the egg
		sideMargin = 8,

		-- The camera keeps the egg below the middle of the screen: by aimBelow of the angle down to it, but never
		-- more than maxAimBelow degrees. fieldOfView is the camera's while walking.
		aimBelow = 0.35,
		maxAimBelow = 14,
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
		bigThudAngle = 4, -- ...and the biggest
		thudDrop = 0.02, -- share of eye height the view drops on a big footfall (times bigness)
		thudTime = 0.35, -- how quickly a jolt dies away
		-- Swimmers (models with a Swim bone, The Abyss on) glide instead: no footfalls, a slow smooth sway.
		swimRate = 0.7, -- sway cycles per second at the first map's size, slower the bigger

		-- The rings round the screen show the catch's colour mutation, in its colour (gold rings on a Gold catch,
		-- as in the reference video). A catch with no colour mutation walks with a clear view.
		glow = {
			-- Built-in Roblox images, so nothing has to be uploaded. Either can be swapped for an uploaded image id.
			ringImage = "rbxasset://textures/ui/Input/Ring_padded.png", -- a thin white ring, tinted
			darkImage = "rbxasset://textures/loading/loadingvignette.png", -- black, clear in the middle
			rings = 9,
			innerSize = 0.78, -- the innermost ring's size against the screen; the clear middle is inside it...
			outerSize = 1.58, -- ...and the outermost's
			innerTransparency = 0.85, -- faint inside...
			outerTransparency = 0.4, -- ...strong at the edges
			darkTransparency = 0.1, -- how strongly the edges darken behind the rings
			fadeTime = 0.3,
		},
	},

	-- After the walk: a close-up of the egg on the ground with the monster's feet already standing behind it, then the
	-- camera pulls back and up until the whole monster stands over the egg (RevealCloseUp, docs/GAME_SPEC.md
	-- section 7). Angles are in degrees, times in seconds.
	closeUp = {
		-- The close-up: the camera this many egg heights from the egg's middle (as close as nearest for a monster
		-- hardly bigger than the egg), looking down at it from elevation for the smallest monsters and bigElevation
		-- for the biggest (low, so their legs tower up behind the egg, over the corridor's walls), this far round
		-- from straight in front of the monster (to one side or the other, at random).
		distance = 2.4,
		nearest = 1.2,
		elevation = 20,
		bigElevation = 4,
		yaw = 12,
		-- Where the egg lies: between the monster's front feet, far enough ahead of them for both feet to stand in
		-- the close-up (at least feetBehind times their distance to the side, behind the camera), and further ahead
		-- when the monster is too low there to stand over it. A monster under besideBelow egg heights tall would
		-- hide behind the egg, so the egg lies beside its front feet instead (a first-map Compy is about 1.2).
		-- eggGap studs are kept clear round the egg.
		feetBehind = 1.5,
		besideBelow = 2.5,
		eggGap = 0.3,
		-- Then the egg lies a clear gap further ahead, this share of the monster's length, so the two never look stuck
		-- together (the owner's wish, 2026-11-04).
		aheadShare = 0.5,
		maxAhead = 15, -- but never more than this many egg heights
		aheadAngle = 60, -- degrees off straight ahead, away from the camera's side
		-- On lucky catches the close-up holds only slowHold seconds, then the camera rises and pulls back over the whole
		-- rest of the climb, ending with the last number.
		slowHold = 0.8,
		slowAcross = 0.3, -- share of the pull back spent turning from the egg to the monster's feet
		slowRise = 1.6, -- how late the view climbs up the body (1 = evenly; higher = the head comes later)
		-- How long the close-up holds: holdShare of the climb (the name filling in and the counter climbing), but
		-- between minHold and maxHold.
		holdShare = 0.3,
		minHold = 0.4,
		maxHold = 2.5,
		-- The pull back takes pullTime for the first map's standard size, up to bigPullTime for the biggest (at
		-- walk.bigScale), which have much further to go. It's cut short to end with the climb, but never to under
		-- minPullShare of its time. A tap to skip finishes it in skipTime.
		pullTime = 1.4,
		bigPullTime = 2.4,
		minPullShare = 0.6,
		skipTime = 0.5,
		-- Where it ends: the monster and the egg fill the screen with margin to spare, from far enough back that
		-- depthShare of their length is in front of the camera too, looking down from endElevation. It always ends
		-- at least minPullBack times further back than the close-up, so tiny monsters still pull back.
		margin = 1.15,
		depthShare = 0.15,
		endElevation = 4, -- low, looking up at the monster a little, so it towers and the egg shows above the text
		-- They're framed in the part of the screen the final text leaves free, topGap design pixels under the top bar,
		-- and never in less than minBand of the screen's height.
		topGap = 12,
		textGap = 40, -- design pixels kept clear above the text for small monsters: the egg, nearest the camera, sits lowest
		minBand = 0.4,
		-- The world's haze thins when the camera ends further back than clearDistance studs: scaled by clearDistance
		-- over the distance, down to minHaze (SkyController HazeScale), so a giant seen from far off stays clear.
		clearDistance = 250,
		minHaze = 0.12,
		minPullBack = 1.5,
		-- Once the pull back is over the camera holds still, with no circling (the owner's wish, 2026-11-04).
		-- Below the corridor's rim the camera keeps wallMargin studs inside its walls; each stud above the rim lets it
		-- go overWalls studs further out, so it rises clear of them smoothly.
		wallMargin = 4,
		overWalls = 2,
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
			color = Color3.fromRGB(255, 226, 110),
			glow = 0.35,
			sparkles = 15,
			sticker = { label = "LUCKY!", colors = { "#fff1a8", "#ffc21a" } },
			panel = { "#fff1a8", "#ffc21a" },
		},
		{
			minOneIn = 1000,
			label = "SUPER LUCKY!",
			color = Color3.fromRGB(255, 110, 150),
			glow = 0.42,
			sparkles = 40,
			sticker = { label = "SUPER LUCKY!", colors = { "#ffc2d4", "#ff6e96" } },
			panel = { "#ffc2d4", "#ff6e96" },
		},
		{
			minOneIn = 10000,
			label = "INSANE!",
			color = Color3.fromRGB(90, 235, 235),
			glow = 0.5,
			sparkles = 80,
			sticker = { label = "INSANE LUCK!", colors = { "#e6ffff", "#5aebeb" } },
			panel = { "#c9fdfd", "#3fd6d6" },
		},
		{
			minOneIn = 100000,
			label = "LEGENDARY!",
			color = Color3.fromRGB(255, 120, 220),
			glow = 0.58,
			sparkles = 140,
			sticker = { label = "LEGENDARY LUCK!!", colors = { "#ffe8f9", "#ff78dc" } },
			panel = { "#ffd3f3", "#ff6fd2" },
		},
		{
			minOneIn = 1000000,
			label = "GODLY!",
			color = Color3.fromRGB(190, 255, 120),
			glow = 0.66,
			sparkles = 240,
			sticker = { label = "GODLY LUCK!!!", colors = { "#f4ffe6", "#beff78" } },
			panel = { "#ff8f8f", "#ffd36b", "#b4ff7a", "#6fe3ff", "#c58bff" },
		},
	},
}
