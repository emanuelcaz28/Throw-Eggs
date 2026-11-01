-- Picks which dino hatches. Each dino's weight is 1 / chance, and luck multiplies the
-- weight of everything except the biome's most common dino, so more luck shifts
-- catches away from the common one and towards the rarer ones.
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Catch = require(ReplicatedStorage.Shared.Config.Catch)
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

local function rollExtra(options)
	for _, option in options do
		if rng:NextNumber() < 1 / option.chance then
			return option
		end
	end
	return nil
end

-- A full catch: the dino plus its mutation and size, and what they add up to.
function DinoRoll.rollCatch(biomeId: string, luck: number)
	local dino = DinoRoll.roll(biomeId, luck)
	local mutation = rollExtra(Catch.mutations)
	local size = rollExtra(Catch.sizes)

	local oneIn = dino.chance
	local income = dino.income
	for _, extra in { mutation, size } do
		oneIn *= extra.chance
		income *= extra.incomeMultiplier
	end

	return {
		name = dino.name,
		mutation = mutation and mutation.id,
		size = size and size.id,
		oneIn = oneIn,
		income = income,
	}
end

return DinoRoll
