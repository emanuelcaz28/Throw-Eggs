-- Luck multiplier by throw distance. Each biome's luck is reached at its far end and climbs from the
-- end of the biome before it, multiplying evenly along the way (so 5x to 25x passes 11x halfway).
-- This is the number players see. The roll counts it from the biome's starting luck (Luck.inBiome),
-- so each biome's odds stay the same however big the number gets.
local Biomes = require(script.Parent.Biomes)

local Luck = {
	startLuck = 1, -- luck at the throw line
}

-- The biome an egg landing at this distance ends up in.
function Luck.biomeAt(distance: number)
	for _, biome in Biomes do
		if distance <= biome.endDist then
			return biome
		end
	end
	return Biomes[#Biomes]
end

-- Luck at the start of a biome: the end of the one before it.
function Luck.startOf(biome): number
	local previous = Luck.startLuck
	for _, other in Biomes do
		if other == biome then
			return previous
		end
		previous = other.luck
	end
	return previous
end

function Luck.at(distance: number): number
	local biome = Luck.biomeAt(distance)
	local from = Luck.startOf(biome)
	local progress = math.clamp((distance - biome.startDist) / (biome.endDist - biome.startDist), 0, 1)
	return from * (biome.luck / from) ^ progress
end

-- The luck the roll uses: 1 at the biome's start, its luck / start luck at its far end (5x).
function Luck.inBiome(distance: number): number
	return Luck.at(distance) / Luck.startOf(Luck.biomeAt(distance))
end

return Luck
