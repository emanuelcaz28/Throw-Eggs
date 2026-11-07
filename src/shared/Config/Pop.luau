-- Pop-up text: outlined words with no panel behind them, from the Figma file "Throw Eggs - Pop-up Text"
-- (https://www.figma.com/design/RPcPJ7Qm7DBI6957rW04cG, where each motion also plays). Sizes are design
-- pixels on the 1280 x 720 screen, scaled like the rest of the UI. Motion is keyframes, { seconds, value,
-- easing }: the easing shapes the move from the keyframe before ("in", "out", "inOut" or "outBack";
-- straight if left out), and the value holds before the first keyframe and after the last.
return {
	colors = {
		cash = Color3.fromRGB(141, 255, 90), -- cash and $/s coming in
		spent = Color3.fromRGB(255, 91, 79),
		xp = Color3.new(1, 1, 1),
		good = Color3.fromRGB(255, 224, 102), -- a notice when something worked
		bad = Color3.fromRGB(255, 107, 94), -- and when it didn't
	},

	-- Small gains and costs, floating up from where they happen: pops in, settles, rises and fades.
	float = {
		size = 30,
		outline = 3,
		shadow = 3, -- the hard ink shadow, straight down
		tilt = 6, -- degrees either way, at random
		spread = 14, -- sideways, at random, so several at once don't stack up
		scale = { { 0, 0.3 }, { 0.12, 1.15, "out" }, { 0.22, 1, "inOut" } },
		rise = { { 0, 0 }, { 0.9, 56, "out" } },
		opacity = { { 0, 0 }, { 0.06, 1 }, { 0.6, 1 }, { 0.9, 0, "in" } },
	},

	-- Big moments in the upper middle of the screen (LEVEL UP!, an event starting, a world completed): the
	-- title slams in, the detail line rises in under it, then the whole thing swells and fades.
	shout = {
		height = 0.24, -- where its middle sits, as a share of the screen's height
		title = { size = 76, outline = 8, shadow = 6 },
		detail = { size = 32, outline = 4, shadow = 3 },
		tilt = 3, -- degrees, the title's right end up
		overlap = 8, -- how far the detail line tucks up under the title
		scale = { { 0, 1.8 }, { 0.16, 0.94, "in" }, { 0.3, 1, "out" }, { 1.6, 1 }, { 1.8, 1.12, "in" } },
		opacity = { { 0, 0 }, { 0.08, 1 }, { 1.6, 1 }, { 1.8, 0, "in" } },
		detailRise = { { 0.12, 12 }, { 0.3, 0, "out" } }, -- below its spot, coming up into it
		detailOpacity = { { 0.12, 0 }, { 0.3, 1, "out" } },
	},

	-- Messages from the server, above the hotbar. Good ones pop with a small overshoot; bad ones pop and shake.
	notice = {
		size = 28,
		outline = 3,
		shadow = 3,
		bottom = 148, -- from the screen's bottom edge, like the hotbar
		scale = { { 0, 0.6 }, { 0.12, 1.08, "out" }, { 0.22, 1, "inOut" } },
		badScale = { { 0, 0.6 }, { 0.1, 1, "out" } },
		shake = { { 0.1, 0 }, { 0.16, 10, "inOut" }, { 0.22, -9, "inOut" }, { 0.28, 7, "inOut" }, { 0.34, -5, "inOut" }, { 0.4, 3, "inOut" }, { 0.46, 0, "inOut" } },
		lift = { { 2.5, 0 }, { 2.75, 12, "in" } },
		opacity = { { 0, 0 }, { 0.08, 1 }, { 2.5, 1 }, { 2.75, 0, "in" } },
	},

	-- A label already on screen punching in, like the meter's PERFECT!: from big with a twist, springing back.
	punch = {
		scale = { { 0, 1.7 }, { 0.25, 1, "outBack" } },
		twist = { { 0, 8 }, { 0.25, 0, "outBack" } }, -- degrees, clockwise
	},
}
