-- Dinos on a plot: they walk to a random spot, stand idle, and repeat. Purely visual, so each
-- player's client runs it and nothing is saved. Placeholder numbers; tune during playtesting.
return {
	tag = "WanderingDino",
	idleSeconds = 10,
	idleJitter = 2, -- idle lasts idleSeconds plus or minus this, so dinos don't move in step
	strideSeconds = 1, -- one full walk cycle
	-- Monsters with a Swim bone (The Abyss) swim instead: one tail beat takes strideSeconds, and they cruise at
	-- speed studs a second at the first map's size.
	swim = { strideSeconds = 1.2, speed = 2.2 },
	idleLoopSeconds = 8,
	-- An equipped monster rides on its player's head at its real size (PlotService), sitting: its feet sink below
	-- the top of the head by this share of its hip height, but never more than maxSink studs, so a small one's legs
	-- hang round the head and a big one perches on top instead of standing over the player. It walks while its
	-- player moves faster than walkSpeed (studs a second) and idles, roar and all, while they stand.
	carry = { sink = 0.7, maxSink = 1, walkSpeed = 2 },
	turnSpeed = 2.5, -- radians per second
	blendTime = 0.35, -- seconds to ease between idle and walk
	arriveDistance = 1, -- studs, at the first map's size
	-- Dinos further than this from the camera update less often, to save phones some work.
	nearDistance = 120,
	farDistance = 350,
	farFrameSkip = 6,
	-- Monsters bigger than this (their size against the first map's) cast no shadow, so a size-mutated giant
	-- doesn't put half the map in the dark. Normal-sized ones keep theirs.
	shadowMaxScale = 4,
	midFrameSkip = 2,
}
