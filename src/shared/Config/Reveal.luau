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

	caughtBannerMinOneIn = 1000, -- catches this rare keep a banner up afterwards
	caughtBannerTime = 6,

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

	-- Each label appears when the counter passes minOneIn. Lowest first.
	tiers = {
		{ minOneIn = 100, label = "LUCKY!", color = Color3.fromRGB(255, 226, 110), wash = 0.92, sparkles = 15 },
		{ minOneIn = 1000, label = "SUPER LUCKY!", color = Color3.fromRGB(255, 110, 150), wash = 0.9, sparkles = 40 },
		{ minOneIn = 10000, label = "INSANE!", color = Color3.fromRGB(90, 235, 235), wash = 0.88, sparkles = 80 },
		{ minOneIn = 100000, label = "LEGENDARY!", color = Color3.fromRGB(255, 120, 220), wash = 0.86, sparkles = 140 },
		{ minOneIn = 1000000, label = "GODLY!", color = Color3.fromRGB(190, 255, 120), wash = 0.84, sparkles = 240 },
	},
}
