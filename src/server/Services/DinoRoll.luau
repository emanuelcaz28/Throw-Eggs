-- Picks which dino hatches. Each dino's weight is 1 / chance, and luck multiplies the
-- weight of everything except the biome's most common dino, so more luck shifts
-- catches away from the common one and towards the rarer ones.
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Dinos = require(ReplicatedStorage.Shared.Config.Dinos)

local DinoRoll = {}

local rng = Random.new()

function DinoRoll.roll(biomeId: string, luck: number)
	local dinos = Dinos[biomeId]

	local weights = {}
	local total = 0
	for index, dino in dinos do
		local weight = 1 / dino.chance
		if index > 1 then
			weight *= luck
		end
		weights[index] = weight
		total += weight
	end

	local pick = rng:NextNumber() * total
	for index, dino in dinos do
		pick -= weights[index]
		if pick <= 0 then
			return dino
		end
	end
	return dinos[#dinos]
end

return DinoRoll
