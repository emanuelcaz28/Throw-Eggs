-- Dinos on a plot: they walk to a roomy spot, stand idle, and repeat (or circle their owner, see ring). Purely visual, so each
-- player's client runs it and nothing is saved. Placeholder numbers; tune during playtesting.
return {
	tag = "WanderingDino",
	idleSeconds = 10,
	idleJitter = 2, -- idle lasts idleSeconds plus or minus this, so dinos don't move in step
	strideSeconds = 1, -- one full walk cycle
	rageStrideSeconds = 2 / 3, -- the Weeping Dark's monsters charge: a third faster (DinoLifeController RAGE). Keep 4 a whole number of these
	-- Monsters with a Swim bone (The Abyss) swim instead: one tail beat takes strideSeconds, and they cruise at
	-- speed studs a second at the first map's size.
	swim = { strideSeconds = 1.2, speed = 2.2 },
	idleLoopSeconds = 8,
	-- An equipped monster rides on its player's head at its real size (PlotService), standing on the top of the
	-- character (hats included). Its feet sink below that by this share of its hip height, but never more than
	-- maxSink studs. [Owner, 2026-11-07: it was "literally in me" with sink 0.7 and maxSink 1.] It walks while its
	-- player moves faster than walkSpeed (studs a second) and idles, roar and all, while they stand.
	carry = { sink = 0, maxSink = 0, walkSpeed = 2 },
	turnSpeed = 2.5, -- radians per second
	blendTime = 0.35, -- seconds to ease between idle and walk
	arriveDistance = 1, -- studs, at the first map's size
	-- When a plot's owner stands on their plot, its monsters gather in a circle round them, facing in, with room between
	-- each one's sides. The circle follows the owner while they stay on the plot and breaks up when they leave
	-- [Owner, 2026-11-08]. Big monsters take a wider share of the circle, so it widens to fit them.
	ring = {
		gap = 3, -- studs of empty ground between two neighbours' sides
		ownerGap = 4, -- studs between the owner and the nearest monster's front
		leaveMargin = 4, -- studs past the plot's edge before the circle breaks up (so it doesn't flicker at the gate)
		followDistance = 3, -- a monster walks back to its place once it's this far off (plus a quarter of its width)
		reactJitter = 0.6, -- seconds: each monster reacts up to this late, so they don't all set off together
		scatterIdle = { 0.5, 3 }, -- seconds of standing still after the circle breaks, before they wander again
	},
	-- How a walking monster finds its way.
	steer = {
		avoidWeight = 1.6, -- how hard it swerves round other monsters and the owner
		ownerRadius = 2, -- studs: a player's body, to swerve round
		slowSeconds = 0.8, -- it starts slowing this many seconds of walking before its spot
		minPace = 0.35, -- the slowest it walks while slowing down
		spotTries = 8, -- wander spots it looks at; it picks the one with the most room
		giveUpSeconds = 3, -- no closer to its spot in this long: it stops and thinks again
		turnInPlace = 0.6, -- radians: it steps round on the spot while facing more than this far off
	},
	-- Dinos further than this from the camera update less often, to save phones some work.
	nearDistance = 120,
	farDistance = 350,
	farFrameSkip = 6,
	-- Dinos outside the camera's view (behind it or off to a side) update only every this many frames, wherever they
	-- are: nobody sees them move, and they catch up the moment they come back on screen.
	offScreenFrameSkip = 6,
	-- Monsters bigger than this (their size against the first map's) cast no shadow, so a size-mutated giant
	-- doesn't put half the map in the dark. Normal-sized ones keep theirs.
	shadowMaxScale = 4,
	midFrameSkip = 2,
}
