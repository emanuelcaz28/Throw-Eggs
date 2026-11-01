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
		cyclesPerSecond = 0.8, -- full left-right-left sweeps of the cursor
		minTime = 0.25, -- seconds before a tap counts, so a throw can't be instant
		minMultiplier = 0.4, -- tap at the very edge of the bar
		maxMultiplier = 1, -- tap just outside the perfect zone
		perfectAccuracy = 0.9, -- accuracy (0 = edge, 1 = centre) that counts as perfect
		perfectBonus = 1.5, -- extra multiplier on a perfect tap
	},

	flight = {
		launchHeight = 4,
		baseTime = 1.2, -- seconds
		studsPerSecond = 200,
		maxTime = 8,
		arcPerStud = 0.2, -- peak height as a share of the distance
		maxArc = 80,
		landingPause = 1.5, -- seconds to look at the landing before the next throw
	},
}

function Throw.isPerfect(accuracy: number): boolean
	return accuracy >= Throw.meter.perfectAccuracy
end

function Throw.multiplier(accuracy: number): number
	local meter = Throw.meter
	local multiplier = meter.minMultiplier + (meter.maxMultiplier - meter.minMultiplier) * accuracy
	return if Throw.isPerfect(accuracy) then multiplier * meter.perfectBonus else multiplier
end

function Throw.flightTime(distance: number): number
	local flight = Throw.flight
	return math.min(flight.baseTime + distance / flight.studsPerSecond, flight.maxTime)
end

return Throw
