-- The Deep End (docs/RETENTION_PLAN.md step 3): what comes after the last world. Throw distance never stops here. The egg
-- always lands on the same floor at the bottom of the pit, and how far the throw would have gone gives its Depth, which
-- makes rare colours and sizes likelier on that throw. The studs are real distance (Throw Power x the meter). Each Depth
-- is a longer step than the last, so there's always one more to reach. Tune during playtesting.
local DeepEnd = {
	startsAt = 18400, -- the far end of the last world with its own monsters (Shattered Mirror since 2026-11-13; hidden for now)
	firstStep = 450, -- studs past startsAt to reach Depth 1
	stepGrowth = 1.38, -- each step this much longer than the one before
	boostPerDepth = 0.5, -- rare colours and sizes: x1.5 likelier at Depth 1, x2 at Depth 2, and so on
}

-- The real distance a Depth starts at. Depth 0 is the pit's top.
function DeepEnd.distanceOf(depth: number): number
	if depth <= 0 then
		return DeepEnd.startsAt
	end
	return DeepEnd.startsAt + DeepEnd.firstStep * (DeepEnd.stepGrowth ^ depth - 1) / (DeepEnd.stepGrowth - 1)
end

-- The Depth a throw of this real distance reaches.
function DeepEnd.depthAt(distance: number): number
	local depth = 0
	while distance >= DeepEnd.distanceOf(depth + 1) do
		depth += 1
	end
	return depth
end

-- How much likelier rare colours and sizes are on a throw of this real distance.
function DeepEnd.boostAt(distance: number): number
	return 1 + DeepEnd.boostPerDepth * DeepEnd.depthAt(distance)
end

return DeepEnd
