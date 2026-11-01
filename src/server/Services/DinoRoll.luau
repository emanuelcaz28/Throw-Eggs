-- Picks which dino hatches. Each dino's weight is 1 / chance, and luck multiplies the
-- weight of everything except the biome's most common dino, so more luck shifts
-- catches away from the common one and towards the rarer ones.
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Catch = require(ReplicatedStorage.Shared.Config.Catch)
local DinoStats = require(ReplicatedStorage.Shared.DinoStats)
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

-- boost multiplies every option's chance, so 2 turns "1 in 20" into "1 in 10".
local function rollExtra(options, boost: number)
	for _, option in options do
		if rng:NextNumber() < boost / option.chance then
			return option
		end
	end
	return nil
end

-- A full catch: the dino plus its mutation and size, and what they add up to.
-- The "1 in X" shown stays the normal odds, even when an event boosts the extras.
function DinoRoll.rollCatch(biomeId: string, luck: number, mutationBoost: number, sizeBoost: number)
	local dino = DinoRoll.roll(biomeId, luck)
	local mutation = rollExtra(Catch.mutations, mutationBoost)
	local size = rollExtra(Catch.sizes, sizeBoost)

	local entry = { id = dino.id, mutation = mutation and mutation.id, size = size and size.id }
	local stats = DinoStats.describe(entry)

	return {
		id = entry.id,
		name = stats.name,
		mutation = entry.mutation,
		size = entry.size,
		oneIn = stats.oneIn,
		income = stats.income,
	}
end

return DinoRoll
