-- Throw lane and timing meter. Distance = Throw Power * meter multiplier.
-- Placeholder numbers; tune during playtesting.
local Throw = {
	lane = {
		origin = Vector3.new(-30, 0, 0), -- the throw line; biome distances are measured from here
		direction = Vector3.new(0, 0, -1), -- eggs fly along this axis
		width = 40,
		markerSpacing = 100, -- studs between distance markers
		padPosition = Vector3.new(-30, 0, 8),
		padRadius = 5,
		padHeight = 8, -- how far above the pad still counts
	},

	meter = {
		cyclesPerSecond = 0.8, -- full up-and-down trips of the marker
		minTime = 0.25, -- seconds before a tap counts, so a throw can't be instant
		levels = 10, -- equal steps up the tube; the top one is PERFECT
		minMultiplier = 0.4, -- distance multiplier at level 1
		maxMultiplier = 1, -- at the level just below the top
		perfectMultiplier = 1.5, -- at the top level
	},

	flight = {
		launchHeight = 4,
		baseTime = 1.2, -- seconds
		studsPerSecond = 200,
		maxTime = 8,
		arcPerStud = 0.2, -- peak height as a share of the distance
		maxArc = 80,
		landingPause = 2.5, -- seconds other players' eggs stay on the ground
	},
}

-- Which level a marker height (0 = bottom, 1 = top) falls in, from 1 up to meter.levels.
function Throw.level(height: number): number
	return math.min(math.floor(height * Throw.meter.levels) + 1, Throw.meter.levels)
end

function Throw.isPerfect(height: number): boolean
	return Throw.level(height) == Throw.meter.levels
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

function Throw.flightTime(distance: number): number
	local flight = Throw.flight
	return math.min(flight.baseTime + distance / flight.studsPerSecond, flight.maxTime)
end

return Throw
