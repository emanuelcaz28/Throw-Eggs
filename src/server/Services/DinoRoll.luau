-- Picks which dino hatches. Each dino's weight is 1 / chance, and luck multiplies the
-- weight of everything except the biome's most common dino, so more luck shifts
-- catches away from the common one and towards the rarer ones. minRank and maxRank (pity, the new-map
-- gift and lucky throws: Config/Hooks, Config/LuckyOutcomes) leave out the dinos outside those ranks.
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Catch = require(ReplicatedStorage.Shared.Config.Catch)
local DinoStats = require(ReplicatedStorage.Shared.DinoStats)
local Dinos = require(ReplicatedStorage.Shared.Config.Dinos)
local LuckyOutcomes = require(ReplicatedStorage.Shared.Config.LuckyOutcomes)

local DinoRoll = {}

local rng = Random.new()

function DinoRoll.roll(biomeId: string, luck: number, minRank: number?, maxRank: number?)
	local dinos = Dinos[biomeId]
	local lowest = math.min(minRank or 1, #dinos)
	local highest = math.max(math.min(maxRank or #dinos, #dinos), lowest)

	local weights = {}
	local total = 0
	for index, dino in dinos do
		local weight = if index < lowest or index > highest then 0 else 1 / dino.chance
		if index > 1 then
			weight *= luck
		end
		weights[index] = weight
		total += weight
	end

	local pick = rng:NextNumber() * total
	for index, dino in dinos do
		pick -= weights[index]
		if weights[index] > 0 and pick <= 0 then
			return dino, index
		end
	end
	return dinos[#dinos], #dinos
end

-- One of the options with these ids, picked the way they're rolled (weight 1 / chance).
local function pickAmong(options, ids: { string })
	local chosen, total = {}, 0
	for _, option in options do
		if table.find(ids, option.id) then
			table.insert(chosen, option)
			total += 1 / option.chance
		end
	end
	local pick = rng:NextNumber() * total
	for _, option in chosen do
		pick -= 1 / option.chance
		if pick <= 0 then
			return option
		end
	end
	return chosen[#chosen]
end

-- What a lucky throw of this multiplier hatches (Config/LuckyOutcomes), or nil when it isn't lucky this
-- time (the x50's coin flip) or the multiplier has no entry.
function DinoRoll.luckyGuarantee(multiplier: number)
	for _, throw in LuckyOutcomes.throws do
		if throw.multiplier == multiplier then
			if rng:NextNumber() >= throw.chance then
				return nil
			end
			local outcome = LuckyOutcomes.outcomes[throw.outcome]
			local guarantee = { minRank = outcome.minRank, maxRank = outcome.maxRank, mutations = outcome.mutations }
			if outcome.presets then
				local preset = outcome.presets[rng:NextInteger(1, #outcome.presets)]
				guarantee.mutation, guarantee.size = preset.mutation, preset.size
			end
			return guarantee
		end
	end
	return nil
end

-- boost multiplies every option's chance, so 2 turns "1 in 20" into "1 in 10".
local function rollExtra(options, boost: number)
	for _, option in options do
		if rng:NextNumber() < math.min(boost / option.chance, Catch.maxChance) then
			return option
		end
	end
	return nil
end

-- A full catch: the dino plus its mutation and size, and what they add up to. Luck makes the
-- mutation and size likelier too (Catch.luckPower), on top of any event boost.
-- The "1 in X" shown stays the normal odds, even when luck, an event or a guarantee helps.
-- luck here is counted from the biome's start (Luck.inBiome times the boosts), not the shown number.
-- guarantee (optional): minRank / maxRank for the dino, and a fixed mutation or size, or mutations to
-- pick one from; anything it leaves out is rolled as normal.
function DinoRoll.rollCatch(biomeId: string, luck: number, mutationBoost: number, sizeBoost: number, guarantee)
	guarantee = guarantee or {}
	local dino, rank = DinoRoll.roll(biomeId, luck, guarantee.minRank, guarantee.maxRank)
	local luckBoost = math.max(luck, 1) ^ Catch.luckPower
	local mutation = if guarantee.mutation
		then DinoStats.findOption(Catch.mutations, guarantee.mutation)
		elseif guarantee.mutations then pickAmong(Catch.mutations, guarantee.mutations)
		else rollExtra(Catch.mutations, mutationBoost * luckBoost)
	local size = if guarantee.size
		then DinoStats.findOption(Catch.sizes, guarantee.size)
		else rollExtra(Catch.sizes, sizeBoost * luckBoost)

	local entry = { id = dino.id, mutation = mutation and mutation.id, size = size and size.id }
	local stats = DinoStats.describe(entry)

	return {
		id = entry.id,
		rank = rank,
		name = stats.name,
		mutation = entry.mutation,
		size = entry.size,
		oneIn = stats.oneIn,
		income = stats.income,
	}
end

return DinoRoll
