-- Power Limit [player feedback, 2026-11-08]: strong players can set the farthest their eggs fly, so they can still land
-- in earlier maps whose monsters they haven't all caught. A throw goes as far as it would anyway, but never past the
-- limit: with a limit well under your power nearly every tap lands right on it. Saved with the player's settings
-- (Config/Settings powerLimitOn, powerLimit), set in the Power Limit panel (PowerLimitController), applied by the server
-- (ThrowService) and by the luck offer's chances (LuckOfferController).
local Biomes = require(script.Parent.Biomes)
local Dinos = require(script.Parent.Dinos)

local PowerLimit = {
	minimum = 50, -- the lowest limit, in power (studs at a PERFECT throw)
	step = 10, -- the slider moves in steps of this much power
	-- The map buttons put the limit this far short of a map's far end, so the egg lands inside it, not on the line.
	mapMargin = 10,
	-- The HUD's LIMIT button shows once Throw Power can carry an egg past the first map.
	showFrom = Biomes[1].endDist,
}

-- How far a throw goes with the player's limit: `reach` is how far it would go without one.
function PowerLimit.apply(reach: number, on: any, limit: any): number
	if on == true and typeof(limit) == "number" and limit >= PowerLimit.minimum then
		return math.min(reach, limit)
	end
	return reach
end

-- The limits the map buttons jump between, lowest first: the far end of each map with monsters, as far as `power`
-- reaches. The map `power` ends in gets `power` itself. Each: { limit = number, biome = Biomes entry }.
function PowerLimit.stops(power: number)
	local stops = {}
	for _, biome in Biomes do
		local dinos = Dinos[biome.id]
		if not dinos or #dinos == 0 or biome.startDist >= power then
			continue
		end
		table.insert(stops, { limit = math.min(biome.endDist - PowerLimit.mapMargin, math.floor(power)), biome = biome })
	end
	return stops
end

return PowerLimit
