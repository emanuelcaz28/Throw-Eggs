-- The hatch reveal after an egg lands. Times are in seconds.
-- Placeholder numbers; tune during playtesting.
return {
	landingHold = 0.8, -- time to read the distance before the reveal starts
	counterRate = 1.25, -- the "1 in X" counter grows this much per step...
	counterStepTime = 0.125, -- ...every this many seconds, until it hits the real number
	minClimbTime = 1.5, -- shortest time before the final card, even for common catches
	maxClimbTime = 9,
	counterMinOneIn = 10, -- catches more common than this show no counter
	hatchAt = 0.4, -- share of the climb when the egg bursts and the dino appears
	skipDelay = 0.4, -- ignore taps this soon, so the throw tap can't skip the reveal

	-- The server frees the player for the next throw once they finish the reveal,
	-- but never sooner than this.
	minTime = 1,

	caughtBannerMinOneIn = 1000, -- catches this rare keep a "YOU CAUGHT!" banner up afterwards...
	caughtBannerTime = 6, -- ...unless they're rare enough for the lucky catch banner below

	-- After the last letter lands: the rarity colour washes over the screen and a ring grows round the dino.
	washTime = 1,
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

	-- The camera starts close on the egg, then pulls back to the dino view when it hatches.
	camera = {
		eggRadius = 9,
		eggHeight = 3,
		eggFocusHeight = 1.5,
		radius = 30,
		height = 12,
		focusHeight = 6,
		turnSpeed = 0.35,
		pullBackTime = 0.6,
	},

	-- Each label appears when the counter passes minOneIn. Lowest first. glow is how strongly the
	-- tier's colour lights the top and bottom of the screen (0 = none, 1 = solid at the edge).
	-- Catches with a label also get a light beam of that colour, and the final screen shows the
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
