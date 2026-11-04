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
	turnSpeed = 2.5, -- radians per second
	blendTime = 0.35, -- seconds to ease between idle and walk
	arriveDistance = 1, -- studs, at the first map's size
	-- Dinos further than this from the camera update less often, to save phones some work.
	nearDistance = 120,
	farDistance = 350,
	farFrameSkip = 6,
	midFrameSkip = 2,
}
