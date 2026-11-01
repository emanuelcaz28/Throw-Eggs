-- Luck multiplier by throw distance. Each biome's luck is reached at its far end
-- and grows evenly from the end of the biome before it.
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

function Luck.at(distance: number): number
	local previousLuck = Luck.startLuck
	for _, biome in Biomes do
		if distance <= biome.endDist then
			local progress = math.max(distance - biome.startDist, 0) / (biome.endDist - biome.startDist)
			return previousLuck + (biome.luck - previousLuck) * progress
		end
		previousLuck = biome.luck
	end
	return previousLuck
end

return Luck
