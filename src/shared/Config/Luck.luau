-- Luck multiplier by throw distance. Each biome's luck is reached at its far end and climbs from the
-- end of the biome before it, multiplying evenly along the way (so 5x to 7x passes 5.9x halfway).
-- This is the number players see (1x to 50x). The roll doesn't use it: it has its own luck, 1x at each
-- biome's start to rollRange at its far end (Luck.forRoll), so each biome's odds stay the same.
local Biomes = require(script.Parent.Biomes)
local Eggs = require(script.Parent.Eggs)

local Luck = {
	startLuck = 1, -- luck at the throw line
	rollRange = 5, -- the roll's luck at a biome's far end, against 1 at its start (with the egg made for it)
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

-- The roll's luck from distance alone: 1 at the biome's start, rollRange at its far end, multiplying evenly.
function Luck.inBiome(distance: number): number
	local biome = Luck.biomeAt(distance)
	local progress = math.clamp((distance - biome.startDist) / (biome.endDist - biome.startDist), 0, 1)
	return Luck.rollRange ^ progress
end

-- The egg made for this biome: Config/Eggs has one per map, in map order (biomes past the last egg use it).
function Luck.eggFor(biome)
	return Eggs[math.min(table.find(Biomes, biome) or 1, #Eggs)]
end

-- The luck a roll uses (DinoRoll, docs/GAME_SPEC.md section 8b), before Index, Server Luck, events and
-- lucky throws multiply it. It's counted from the biome's par: the luck at its start with the egg made for
-- it. So every biome runs from 1x at its start to 5x at its far end with its own egg; a newer egg gives a
-- bit more, an older one less. That keeps late eggs (x17) from making every catch a rare one.
function Luck.forRoll(distance: number, eggLuck: number): number
	return Luck.inBiome(distance) * Luck.eggFactor(eggLuck, distance)
end

-- What the thrown egg multiplies luck by, for an egg landing at this distance: its luck against the egg made
-- for that biome (1 with that egg, about 1.2 with the next). The number shown uses it too, worked out once for
-- the landing spot so it doesn't jump mid-flight; that keeps the shown luck at 50x or less without boosts.
function Luck.eggFactor(eggLuck: number, landingDistance: number): number
	return eggLuck / Luck.eggFor(Luck.biomeAt(landingDistance)).luckBonus
end

return Luck
