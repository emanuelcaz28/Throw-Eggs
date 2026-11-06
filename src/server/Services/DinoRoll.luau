-- Picks which monster hatches, then its mutation and size (docs/GAME_SPEC.md section 8b, Config/Catch).
-- Luck aims at a "1 in X" in the map's list: monsters near the aim come most and the rest fall off on both
-- sides, and the last catches are less likely to come again (Config/Catch pick). minRank (pity and the
-- new-map gift, Config/Hooks) leaves out the monsters more common than that rank.
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Catch = require(ReplicatedStorage.Shared.Config.Catch)
local DinoStats = require(ReplicatedStorage.Shared.DinoStats)
local Dinos = require(ReplicatedStorage.Shared.Config.Dinos)
local Events = require(ReplicatedStorage.Shared.Config.Events)

local DinoRoll = {}

local rng = Random.new()

-- Each monster's chance of hatching, most common first; they add up to 1. luck is counted from the map's par
-- (Config/Luck forRoll) with every boost multiplied in. recent: the ids of the last catches, newest first.
function DinoRoll.odds(biomeId: string, luck: number, minRank: number?, recent: { string }?): { number }
	local dinos = Dinos[biomeId]
	local pick = Catch.pick
	local count = #dinos
	local lowest = math.clamp(minRank or 1, 1, count)

	-- The aim: the commonest monster's odds times the luck, stopped part of the way to the rarest.
	local commonest = dinos[1].chance
	local top = if count > 1 then dinos[count - 1].chance ^ (1 - pick.topAim) * dinos[count].chance ^ pick.topAim else commonest
	local aim = math.clamp(commonest * luck, commonest, math.max(top, commonest))

	local weights, total = {}, 0
	for rank, dino in dinos do
		local weight = 0
		if rank >= lowest then
			weight = math.min(dino.chance / aim, aim / dino.chance) ^ pick.falloff
			for index, id in recent or {} do
				if id == dino.id then
					weight /= pick.repeatPenalty[index] or 1
					break
				end
			end
		end
		weights[rank] = weight
		total += weight
	end
	for rank, weight in weights do
		weights[rank] = weight / total
	end
	return weights
end

function DinoRoll.roll(biomeId: string, luck: number, minRank: number?, recent: { string }?)
	local dinos = Dinos[biomeId]
	local odds = DinoRoll.odds(biomeId, luck, minRank, recent)
	local pick = rng:NextNumber()
	for rank, dino in dinos do
		pick -= odds[rank]
		if odds[rank] > 0 and pick <= 0 then
			return dino, rank
		end
	end
	return dinos[#dinos], #dinos
end

-- boost multiplies every option's chance, so 2 turns "1 in 20" into "1 in 10".
-- perOption (optional) multiplies single options on top, by id ({ Ghost = 10 } during a Ghost Rush).
local function rollExtra(options, boost: number, perOption: { [string]: number }?)
	for _, option in options do
		local optionBoost = boost * (if perOption and perOption[option.id] then perOption[option.id] else 1)
		if rng:NextNumber() < math.min(optionBoost / option.chance, Catch.maxChance) then
			return option
		end
	end
	return nil
end

-- A full catch: the monster plus its mutation and size, and what they add up to. The same luck makes the
-- mutation and size likelier too, more gently (Catch.luckPower), on top of any event boost.
-- The "1 in X" shown is always the normal odds, even when luck or a guarantee helped.
function DinoRoll.rollCatch(biomeId: string, luck: number, minRank: number?, recent: { string }?)
	local dino, rank = DinoRoll.roll(biomeId, luck, minRank, recent)
	local luckBoost = math.max(luck, 1) ^ Catch.luckPower
	local mutation = rollExtra(Catch.mutations, luckBoost, Events.mutationBoosts())
	local size = rollExtra(Catch.sizes, luckBoost)

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
