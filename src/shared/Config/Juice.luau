-- Visual juice: the quick flashes, bursts and puffs on the game's small moments [Owner, 2026-11-10;
-- docs/GROWTH_PLAYBOOK.md "action and response": every action gets instant feedback]. Drawn by the client's
-- GameFeelJuice next to the sounds in GameFeelSounds. Sizes are design pixels on the 1280 x 720 screen (scaled like
-- the rest of the UI), times in seconds, colours as hex. Everything ends in under a second and never blocks a tap.
-- Keyframe tracks work like Config/Pop: { seconds, value, easing }.
return {
	-- A burst: a ring growing out of a point plus small diamonds flying out of it and fading.
	bursts = {
		-- A power bar filled, at the Throw Power number.
		power = { ring = 110, ringWidth = 6, sparks = 10, sparkSize = 14, distance = 90, time = 0.55, colors = { "#6fe3ff", "#ffffff", "#ffe066" } },
		-- Cash spent, at the cash number.
		cash = { ring = 70, ringWidth = 4, sparks = 0, sparkSize = 0, distance = 0, time = 0.35, colors = { "#8dff5a" } },
		-- On the button that bought it (eggs, feeding, upgrades in a panel).
		button = { ring = 90, ringWidth = 5, sparks = 8, sparkSize = 10, distance = 70, time = 0.4, colors = { "#ffe066", "#ffffff" } },
		-- A tutorial step done, in the upper middle of the screen. No text, ever (the tutorial is "instinctual").
		tutorial = { ring = 220, ringWidth = 8, sparks = 18, sparkSize = 16, distance = 200, time = 0.8, colors = { "#ffe066", "#8dff5a", "#6fe3ff", "#ff7ad9", "#ffffff" } },
	},
	tutorialAt = Vector2.new(0.5, 0.36), -- share of the screen's width and height

	-- A PERFECT tap [Owner, 2026-11-11: "a better visual for when players hit perfect, not too much"]. On the meter,
	-- where the player is looking: a gold ring and sparks out of the PERFECT zone, the zone flashing white back to
	-- gold, and the meter giving a small bump. Then the egg flies with a gold trail instead of the white one, seen by
	-- everyone. The big "PERFECT!" in the middle of the screen is PerfectMoment's.
	perfectHit = {
		burst = { ring = 150, ringWidth = 7, sparks = 12, sparkSize = 14, distance = 120, time = 0.5, colors = { "#ffd23c", "#ffffff", "#fff3b0" } },
		bump = { scale = 1.08, time = 0.3 },
		flash = { color = "#ffffff", time = 0.35 }, -- the zone starts this colour and fades back to gold
		trail = { from = "#ffd23c", to = "#fff3b0", lightEmission = 1, widthScale = 1.4, lifetime = 1.4 },
	},

	-- The big "+5 POWER" over Throw Power when a bar fills: slams in, holds, rises and fades.
	powerPop = {
		look = { size = 48, outline = 5, shadow = 4 },
		fill = "#6fe3ff",
		above = 34, -- its middle, above the top of the Throw Power number
		scale = { { 0, 2 }, { 0.14, 0.92, "in" }, { 0.26, 1, "out" } },
		rise = { { 0.45, 0 }, { 0.9, 40, "in" } },
		opacity = { { 0, 0 }, { 0.06, 1 }, { 0.6, 1 }, { 0.9, 0, "in" } },
	},

	-- A number on the HUD bumping up and flashing (Throw Power on a full bar, cash on a purchase).
	statBump = { scale = 1.22, time = 0.3, flash = "#ffffff" },
	-- What was bought gets the same bump, a little smaller (only buttons without their own scale motion).
	buttonBump = { scale = 1.12, time = 0.25 },
	buyWindow = 1, -- a purchase this soon after a button tap counts as that button's

	-- Each squat: the XP bar bumps and its fill shines. Cheap enough for every rep.
	squat = { scale = 1.04, time = 0.22, shine = 0.45 }, -- shine: how see-through the white shine starts (1 = none)

	-- A monster put down on the base: a dust ring and a few dust puffs on the ground at its feet, then the $/s it
	-- adds floats up from there. Studs; the size follows the monster's footprint between min and max.
	placePuff = {
		color = "#efe4cf",
		footprint = 0.6, -- the ring's final width, as a share of the monster's widest side
		min = 6,
		max = 70,
		puffs = 7,
		puffSize = 0.22, -- each puff, as a share of the ring
		time = 0.5,
		startTransparency = 0.25,
		findFor = 2, -- how long to wait for the statue to show up (the plot rebuilds and streams it in)
		textAbove = 3, -- studs above its feet where the $/s starts
	},
}
