-- Throw lane and timing meter, and the throw's cinematic timing. Distance = Throw Power * meter multiplier.
-- Placeholder numbers; tune during playtesting.
local Biomes = require(script.Parent.Biomes)
local Dinos = require(script.Parent.Dinos)

local Throw = {
	-- The throw platform sits in the arena's front wall (Config/Map). Standing anywhere on it starts the
	-- meter. The egg leaves from the throw line, its corridor-side edge, and lands on the corridor floor below.
	lane = {
		origin = Vector3.new(0, 0, 0), -- the throw line at arena level; biome distances are measured from here
		direction = Vector3.new(0, 0, -1), -- eggs fly along this axis
		floorY = -12, -- the corridor floor, where eggs land (Config/Map corridor.floorY)
		width = 88, -- the corridor's width (Config/Map platform.width)
		markerSpacing = 100, -- studs between distance markers
		zoneCenter = Vector3.new(0, 0.5, 8), -- the platform's top, middle
		zoneSize = Vector2.new(88, 16), -- across, along the lane
		zoneHeight = 8, -- how far above the platform still counts
	},

	meter = {
		cyclesPerSecond = 0.8, -- full up-and-down trips of the marker
		minTime = 0.25, -- seconds before a tap counts, so a throw can't be instant
		levels = 10, -- equal steps up the tube; the top one is PERFECT
		-- [Owner, 2026-11-08] A PERFECT throw goes exactly as far as your Throw Power, no 1.5x bonus; the other levels
		-- go less far.
		minMultiplier = 0.4, -- distance multiplier at level 1
		maxMultiplier = 0.9, -- at the level just below the top
		perfectMultiplier = 1, -- at the top level
		-- The PERFECT band: this share of the tube at its top (the other levels split the rest evenly). The
		-- marker slows near the top, so a band of 0.1 was hit about 1 tap in 5; 0.06 is about 1 in 6.5.
		perfectZone = 0.06,
	},

	-- Stepping onto the platform: the screen dips to black, and comes back on the thrower standing still on the throw
	-- spot, facing the corridor with the egg in their right hand, the camera low behind their right shoulder. Only
	-- Throw Power and the meter stay on screen. Times in seconds.
	aim = {
		fadeOut = 0.15,
		black = 0.12,
		fadeIn = 0.2,
		spotZ = 4, -- the throw spot's distance in from the throw line; across, the thrower stays where they stepped on
		spotMargin = 10, -- kept this far in from the platform's sides
		cameraOffset = Vector3.new(3.2, 2, 7.5), -- from the thrower's root: right, up, behind
		cameraPitch = -6, -- degrees, looking slightly down the corridor
	},

	-- After the tap (docs/GAME_SPEC.md section 7, "Throw"): the result shows for a moment, black bars slide in, then
	-- the thrower crouches, swings the egg low, spins upright and lunges into a straight-arm release (ThrowWindup,
	-- made in Blender by assets/animations/build_throw.py). Their camera whips round to face them with the arena
	-- behind, then whips back to look down the corridor as the egg leaves the hand. The flight, and the server's
	-- landing, start releaseDelay() after the tap.
	windup = {
		holdAfterTap = 0.45, -- the result on the meter before anything moves
		releaseInClip = 1.1, -- seconds into the clip (build_throw.py RELEASE)
		-- The published clip. Studio play tests use the clip Rojo syncs to ReplicatedStorage.Shared.Animations,
		-- so they show the latest build_throw.py; live servers can only play the published one, so republish
		-- (overwriting this asset) after changing the clip.
		animationId = "rbxassetid://136948284707759",
		barHeight = 0.11, -- each black bar, as a share of the screen's height
		barsAt = 0.2, -- seconds after the tap the bars slide in
		barSlide = 0.12, -- seconds for the bars to slide in or out
		barsOutAfterRelease = 0.15,
		eggGrip = Vector3.new(0, -1, 0), -- the egg's centre from the right hand
		heldScale = 0.45, -- the egg's size in the hand, against its size in flight and on the ground
		eggBlend = 0.15, -- share of the flight over which the egg grows from its size in the hand to full size
		-- The camera round the thrower, keyed in seconds after the tap. yaw: degrees round them, clockwise seen from
		-- above, 0 = behind; distance and height in studs from their root; side: studs to their right (the aim
		-- framing); look: 0 = at the thrower's chest, 1 = straight down the corridor.
		camera = {
			{ time = 0, yaw = 0, distance = 7.5, height = 2, side = 3.2, look = 1 },
			{ time = 0.45, yaw = 0, distance = 7.5, height = 2, side = 3.2, look = 1 },
			{ time = 0.62, yaw = 35, distance = 7.5, height = 2.5, side = 1.5, look = 0.4 },
			{ time = 0.85, yaw = 172, distance = 9, height = 3.5, side = 0, look = 0 },
			{ time = 1.25, yaw = 192, distance = 8.5, height = 3, side = 0, look = 0 },
			{ time = 1.45, yaw = 40, distance = 6.5, height = 1.6, side = 0, look = 0.6 },
			{ time = 1.55, yaw = -25, distance = 6, height = 1.2, side = 0, look = 1 },
		},
	},

	-- The egg's flight down the corridor. It slows as it goes (speed falls to slowDown of its starting speed), and a
	-- throw to the far end of the last world takes maxTime, nearer ones less. The camera starts low beside the
	-- thrower, climbs high behind the egg looking down the valley, then drops low again as it comes down.
	flight = {
		spin = 8, -- the egg's tumble, in radians a second on average (fastest out of the hand)
		-- [Owner, 2026-11-07] A little longer than 1.5 and 6, so players get to see the worlds go by.
		minTime = 2, -- seconds, for the shortest throws
		maxTime = 8, -- to the end of the last world
		deepTime = 3, -- [Owner, 2026-11-07] seconds past the Last Door, so players get to see The Deep End
		slowDown = 0.4,
		arcPerStud = 0.05, -- peak height as a share of the distance
		maxArc = 18, -- stays inside the valley, under the rim
		landingPause = 2.5, -- seconds other players' eggs stay on the ground
		camera = {
			riseTime = 0.5, -- seconds to climb from the thrower to high behind the egg
			fallTime = 0.7, -- seconds before landing it starts coming down
			-- Studs from the egg: how far behind it, how high above it, and how far ahead of it the camera looks.
			-- High is most of the flight, looking down the valley; low is the landing.
			high = { behind = 26, above = 14, ahead = 40 },
			low = { behind = 13, above = 5, ahead = 4 },
		},
		trail = { lifetime = 1.1, width = 1.6, transparency = 0.15 }, -- the white streak behind the egg
		throwPowerHideAt = 0.3, -- seconds into the flight Throw Power leaves the screen
	},

	-- Where it lands: a flat white ring flashes out on the ground, then a puff of dust rises.
	landing = {
		ringRadius = 7,
		ringTime = 0.3,
		dustDelay = 0.1,
		dustColor = Color3.fromRGB(226, 208, 170),
		-- First it bounces (EggModel.bounce): it touches down `run` studs short of where it lands, squashes flat,
		-- hops on twice, smaller each time, coming upright as it goes, rocks on its foot like a toy that won't fall
		-- over, then trembles: the cut is coming. Studs and seconds; studs at the egg's own size where it says so.
		bounce = {
			run = 3.5, -- studs it skids on along the lane after touching down
			hops = { -- each hop: how high (studs at size 1), how long, and its share of the run
				{ height = 1.7, time = 0.4, share = 0.7 },
				{ height = 0.5, time = 0.24, share = 0.3 },
			},
			squash = 0.35, -- how much flatter it goes on touching down (a share of its height); half that on the 2nd
			contact = 0.08, -- seconds it stays squashed on the ground before it hops on
			squashTime = 0.14, -- seconds it's stretched taller as it springs off
			wobble = 0.24, -- radians it rocks on its foot once it stands
			wobbleTime = 0.45, -- seconds the rocking dies away over
			tremble = 0.06, -- studs at size 1 it shakes just before the cut
			trembleTime = 0.18,
		},
		-- When the cut is through, egg white and yolk splash out and land as flat splats, and bits of shell fly off.
		splash = {
			whites = 9, -- drops of egg white
			yolks = 4, -- drops of yolk
			chips = 7, -- bits of shell
			speed = { 5, 10 }, -- studs a second outwards, at size 1
			rise = { 7, 12 }, -- and upwards
			gravity = 55,
			fadeAfter = 2.5, -- seconds the splats stay before fading
		},
		-- Then the egg is cut in half (EggModel.split): a white streak sweeps across its middle, the top half slides
		-- off along the cut, tips over and lands upside down beside the bottom half, and rocks to a stop, so both show
		-- their white and yolk. Seconds, and studs at the egg's own size; the same as SPLIT in
		-- assets/models/build_eggs.py, whose egg_slice.mp4 plays them. Only eggs with a Blender model in
		-- ReplicatedStorage.Assets.Eggs are cut; the others stay whole.
		split = {
			height = 3, -- the Blender egg's shell is this tall at scale 1 (ThrowController EGG_SIZE.Y)
			radius = 1.2, -- and this wide at its waist
			cut = 0.42, -- where it's cut: its widest point, as a share of its height up from its foot
			delay = 0.05, -- after touching down
			slice = 0.14, -- the streak's sweep
			slide = 0.12, -- the top half sliding off along the cut
			fall = 0.42, -- tipping over and dropping beside the bottom half
			push = 0.42, -- how far it slides, in radii
			lift = 0.15, -- and how far it rises as it slides, clear of the bottom half's yolk
			gap = 0.3, -- between the two halves once it's down
			hop = 0.6, -- how high it hops on the way over
			rock = 0.16, -- radians it rocks once down
			rockTime = 0.7, -- seconds the rocking dies away over
			sink = 0.04, -- how far its tip sinks into the ground
		},
	},
}

-- Which level a marker height (0 = bottom, 1 = top) falls in, from 1 up to meter.levels.
function Throw.isPerfect(height: number): boolean
	return height >= 1 - Throw.meter.perfectZone
end

function Throw.level(height: number): number
	local levels = Throw.meter.levels
	if Throw.isPerfect(height) then
		return levels
	end
	return math.min(math.floor(height * levels) + 1, levels - 1)
end

function Throw.multiplier(height: number): number
	local meter = Throw.meter
	if Throw.isPerfect(height) then
		return meter.perfectMultiplier
	end
	local progress = (Throw.level(height) - 1) / (meter.levels - 2)
	return meter.minMultiplier + (meter.maxMultiplier - meter.minMultiplier) * progress
end

-- Marker height at a time since the meter started. It moves like a swing, slowing
-- down near the top, so the sweet zone stays under the marker for a long moment.
function Throw.markerHeight(elapsed: number): number
	return (1 - math.cos(2 * math.pi * Throw.meter.cyclesPerSecond * elapsed)) / 2
end

-- Whether a point (a character's root) is above the throw platform.
function Throw.onPlatform(position: Vector3): boolean
	local lane = Throw.lane
	local offset = position - lane.zoneCenter
	return math.abs(offset.X) <= lane.zoneSize.X / 2
		and math.abs(offset.Z) <= lane.zoneSize.Y / 2
		and offset.Y >= 0
		and offset.Y <= lane.zoneHeight
end

-- The far end of the last world an egg can land in: one with monsters, or one that rolls another list (The Deep End's
-- rollFrom). A world built after it whose monsters aren't made yet (Shattered Mirror, 2026-11-13) is only seen ahead.
local function landableEnd(): number
	local farthest = 0
	for _, biome in Biomes do
		local dinos = Dinos[biome.rollFrom or biome.id]
		if dinos and #dinos > 0 then
			farthest = biome.endDist
		end
	end
	return farthest
end

-- The farthest place an egg really lands: the far end of the last world it can land in, 100 short of it (of the end wall
-- when that world is the last one built). Past the last world's monsters, how far a throw would have gone is only a
-- number (Config/DeepEnd).
function Throw.farthestLanding(): number
	return landableEnd() - 100
end

-- Where luck is counted for a throw that would go `reach` studs. The egg itself stops at farthestLanding, but luck counts
-- the real reach up to that world's far end, so the strongest throw gets its full luck [Owner, 2026-11-11: max power
-- showed 49.7x].
function Throw.luckDistance(reach: number): number
	return math.min(reach, landableEnd())
end

-- Seconds from the tap until the egg leaves the hand.
function Throw.releaseDelay(): number
	return Throw.windup.holdAfterTap + Throw.windup.releaseInClip
end

-- The farthest an egg can land: the end of the last world that has monsters. A world whose monsters
-- aren't made yet is built and decorated, and seen ahead during long throws, but nothing lands in it.
function Throw.maxDistance(): number
	local farthest = 0
	for _, biome in Biomes do
		local dinos = Dinos[biome.id]
		if dinos and #dinos > 0 then
			farthest = biome.endDist
		end
	end
	return farthest
end

-- Where the Last Door stands, from the throw line: the end of the corridor, past Shattered Mirror since 2026-11-13. Eggs
-- going on to The Deep End burst through it (ThrowCinematic.doorBurst).
Throw.lastDoorAt = 18426

-- The flight's length: grows with the square root of the distance, so short throws are still a moment to watch and
-- the far end of the last world you can reach takes maxTime. Past the Last Door it takes deepTime more.
function Throw.flightTime(distance: number): number
	local flight = Throw.flight
	local share = math.clamp(distance / Throw.maxDistance(), 0, 1)
	local time = flight.minTime + (flight.maxTime - flight.minTime) * math.sqrt(share)
	return if distance > Throw.lastDoorAt then time + flight.deepTime else time
end

-- Share of the distance travelled at a share of the flight's time (both 0 to 1): fast at first, slowing down.
function Throw.travelled(t: number): number
	local slow = 1 - Throw.flight.slowDown
	return (t - slow / 2 * t * t) / (1 - slow / 2)
end

-- Share of a throw's distance covered this many seconds into its flight. A throw into The Deep End flies to the Last Door
-- as a throw that ends there would, then slows through the world behind it for flight.deepTime (the door's flash hides the change).
function Throw.flightShare(elapsed: number, distance: number): number
	if distance <= Throw.lastDoorAt then
		return Throw.travelled(math.min(elapsed / Throw.flightTime(distance), 1))
	end
	local toDoor = Throw.flightTime(distance) - Throw.flight.deepTime
	if elapsed < toDoor then
		return Throw.travelled(elapsed / toDoor) * Throw.lastDoorAt / distance
	end
	local past = Throw.travelled(math.min((elapsed - toDoor) / Throw.flight.deepTime, 1))
	return (Throw.lastDoorAt + (distance - Throw.lastDoorAt) * past) / distance
end

return Throw
