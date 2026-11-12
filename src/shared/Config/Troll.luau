-- Trolling: ragdolls and (later) leashes. Pure fun: nothing here earns or costs anyone anything [Owner, 2026-11-12].
return {
	-- The one switch for all of it: the Ragdoll and Leash buttons, the leash itself, the Player Leash pass and the
	-- "Let players leash me" setting. false: none of it is in the game (hidden until the owner wants it in an
	-- update) [Owner, 2026-11-12]. true: it's all there.
	enabled = false,
	ragdoll = {
		maxSeconds = 6, -- the player gets up by themselves after this long
		minSeconds = 0.8, -- a second press sooner than this is ignored, so a double tap doesn't cancel the fall
		cooldown = 2, -- seconds after getting up before the next ragdoll
		hop = Vector3.new(0, 34, 22), -- the little jump into the fall: up, and forwards the way they face (studs/second)
		spin = 6, -- how hard the body tumbles as it leaves the ground
		limbSwing = 50, -- how far limbs bend at each joint, degrees
		limbTwist = 35,
	},
	-- Leashing a monster. With the Leash switched on, a click on any monster, however far, takes hold of it: it floats
	-- on the end of a line wherever the cursor points, tumbling for real, and a second click throws it wherever it
	-- was heading [Owner, 2026-11-12, after a grab-and-throw reference video]. Then it gets up and walks home.
	leash = {
		maxSeconds = 15, -- then the monster shakes itself off
		minSeconds = 0.25, -- a second click sooner than this is ignored
		cooldown = 2, -- seconds before your own monster can be leashed again
		cooldownOthers = 20, -- the same, after someone who isn't its owner leashed it: it gets a rest from trolls
		holderCooldown = 1, -- seconds after letting go before the same player can leash anything
		range = 220, -- studs from the middle of a plot the holder may stand and still leash its monsters
		-- Where it's held: along the line from the camera through the cursor, as far off as it was when taken (between
		-- holdMin and holdMax studs), never more than aimRange from the holder, and never inside the map.
		holdMin = 16,
		holdMax = 70,
		aimRange = 95,
		pull = 420, -- how hard it's hauled toward that spot (studs a second, each second); gravity is about 196
		maxSpeed = 115, -- the fastest it's hauled, so a flick of the cursor whips it round
		holdSpin = 2.5, -- how fast it turns over as it hangs (radians a second)
		ropeThickness = 0.3,
		ropeColor = Color3.fromRGB(255, 190, 60),
		bodyMin = 2.5, -- the tumbling body is a ball this wide at least...
		bodyMax = 14, -- ...and this wide at most, however huge the monster
		bodyMass = 3,
		bounce = 0.45,
		friction = 0.5,
		settleSeconds = 5, -- after the throw it flies and rolls this long at most; it stops sooner once it lies still
		rollAfter = 1.2, -- seconds after the throw (or at its first slam) it starts slowing down...
		rollDrag = 1.8, -- ...this hard, so it rolls to a stop instead of across the whole map
		stillSpeed = 5, -- slower than this (studs a second) counts as lying still
		homeSpeed = 4, -- it hurries home this many times its walking speed
		-- The throw: it keeps the speed and direction the cursor gave it, times a boost that grows with the holder's
		-- Throw Power. Power numbers get enormous, so the boost climbs by the number of digits and tops out, and
		-- the speed is capped: the monster always stays on the map. The server works the boost out (LeashService).
		fling = {
			boost = 0.6, -- at `fullPower` it leaves this much faster again (1.6 times)
			fullPower = 1e9,
			maxSpeed = 160, -- studs a second, whatever the boost
			spin = 9, -- how hard it tumbles as it leaves
		},
		-- A slam: its body stops or turns this hard in one moment (studs a second). Its bones are knocked out of
		-- place and it's stunned, more the harder the hit, up to `slamFull`.
		slamSpeed = 38,
		slamFull = 120,
		-- Once it lies still it stays down, crumpled, for downSeconds (plus stunSeconds for the hardest slam it
		-- took), heaves itself up in riseSeconds with a little hop, sways dizzily for dizzySeconds, then goes home.
		downSeconds = 0.5,
		stunSeconds = 1.4,
		riseSeconds = 0.45,
		dizzySeconds = 1.1,
		dizzyLean = 0.2, -- radians it sways as it finds its feet
		lostDistance = 250, -- further than this from the holder (fell off the map): put back beside them
	},
	-- Leashing another player (the Player Leash game pass, Config/Shop playerLeash): they go limp and are dragged on a
	-- rope. The protection is the victim's, so several trolls can't keep one player down.
	playerLeash = {
		maxSeconds = 6, -- then the victim gets up, whatever the holder does
		reach = 14, -- studs between holder and victim to start
		immunity = 20, -- seconds after getting up that nobody can leash the victim again
		cooldown = 15, -- seconds before the same pass owner can leash another player
		rope = 8, -- studs
	},
	-- A leashed monster's loose bones (DinoLifeController flop): every bone hangs on a spring.
	limp = {
		rate = 9, -- how fast a bone swings (radians a second); each bone varies around this
		damping = 0.22, -- 0 swings for ever, 1 doesn't swing at all
		maxAngle = 1.25, -- radians a bone hangs away from its own pose at most
		innerReach = 0.3, -- a bone that carries other bones (spine, neck, thigh) gives only this share
		maxPush = 900, -- the hardest yank the bones feel (studs a second, each second); gravity is about 196
		joltAngle = 1.6, -- radians a full slam throws a bone
		fadeIn = 0.25, -- seconds to go limp
		fadeOut = 0.5, -- seconds to pull itself together once it's let go
	},
	-- The invisible wall around the throw platform. Only ragdolled bodies hit it (later: leashed monsters too), so
	-- nothing flung can land in the throwing area. Everyone else walks through as if it isn't there.
	throwWall = {
		margin = 4, -- studs the wall stands out from the platform's edge
		height = 120,
		thickness = 6,
	},
}
