-- The egg's flight, made worth watching (ThrowCinematic, FlightSound, ThrowController) [Owner, 2026-11-11: "something
-- clean, actually nice and worthy of watching the egg go", with a sound for passing through each map]. Display only.
return {
	-- The streak behind the egg: a comet that tapers to a point, with a soft wide glow round it. Its tail takes the
	-- colour of the world the egg is flying over (a PERFECT throw stays gold).
	trail = {
		taper = 0.15, -- the tail's width against the head's
		tint = 0.6, -- how far the tail leans to the world's colour: 0 stays white, 1 is the world's full colour
		glow = { width = 4.5, transparency = 0.8, lifetime = 0.35 },
	},

	-- Crossing into a new world: a ring in the world's colour bursts out round the egg and rides with it, and a short
	-- wake of sparks is left behind. Only on the thrower's screen.
	gate = {
		radius = 14, -- studs the ring grows to
		time = 0.5, -- seconds it takes to grow and fade
		behind = 2.5, -- studs behind the egg, so the egg punches out of it
		startTransparency = 0.15,
		sparks = 22, -- how many sparks in the wake
		sparkTime = 0.22, -- seconds the wake keeps sparking
	},

	-- The camera follows this share of the egg's rise and fall (1 = locked to the egg, as before), so the egg climbs
	-- and drops on screen and the arc shows.
	arcFollow = 0.65,
}
