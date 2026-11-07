-- Picks which monster hatches, then its mutation and size (docs/GAME_SPEC.md section 8b, Config/Catch).
-- Luck aims at a "1 in X" in the map's list: monsters near the aim come most and the rest fall off on both
-- sides, and the last catches are less likely to come again (Config/Catch pick). minRank (pity and the
-- new-map gift, Config/Hooks) leaves out the monsters more common than that rank.
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Catch = require(ReplicatedStorage.Shared.Config.Catch)
local CatchOdds = require(ReplicatedStorage.Shared.CatchOdds)
local DinoStats = require(ReplicatedStorage.Shared.DinoStats)
local Dinos = require(ReplicatedStorage.Shared.Config.Dinos)
local Events = require(ReplicatedStorage.Shared.Config.Events)

local DinoRoll = {}

local rng = Random.new()

-- Each monster's chance of hatching, most common first (CatchOdds, which the luck offer's Details panel reads too).
DinoRoll.odds = CatchOdds.monsters

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

-- A colour and size for this monster that make the whole catch at least 1 in `minOneIn`, each combination as likely
-- as it really is (1 / its "1 in X"), or nil when none does.
local function hitExtras(dinoId: string, minOneIn: number): (string?, string?, boolean)
	local options, total = CatchOdds.hitOptions(dinoId, minOneIn)
	local pick = rng:NextNumber() * total
	for _, option in options do
		pick -= option.weight
		if pick <= 0 then
			return option.entry.mutation, option.entry.size, true
		end
	end
	local last = options[#options]
	return if last then last.entry.mutation else nil, if last then last.entry.size else nil, last ~= nil
end

-- The "1 in X" a lucky throw of this multiplier guarantees (Config/Catch luckyHits), or nil.
DinoRoll.hitFor = CatchOdds.hitFor

-- A full catch: the monster plus its mutation and size, and what they add up to. The same luck makes the
-- mutation and size likelier too, more gently (Catch.luckPower), on top of any event boost. `minOneIn` (lucky
-- throws): the colour and size are instead picked so the catch is at least that rare (Config/Catch luckyHits).
-- The "1 in X" shown is always the catch's real odds (DinoStats.describe). extraBoost: The Deep End's Depth (Config/DeepEnd).
function DinoRoll.rollCatch(biomeId: string, luck: number, minRank: number?, recent: { string }?, minOneIn: number?, extraBoost: number?)
	local dino, rank = DinoRoll.roll(biomeId, luck, minRank, recent)
	local entry
	if minOneIn then
		local mutationId, sizeId, found = hitExtras(dino.id, minOneIn)
		if not found then
			-- No colour and size get this monster there: the map's rarest always can.
			local dinos = Dinos[biomeId]
			dino, rank = dinos[#dinos], #dinos
			mutationId, sizeId = hitExtras(dino.id, minOneIn)
		end
		entry = { id = dino.id, mutation = mutationId, size = sizeId }
	else
		local luckBoost = math.max(luck, 1) ^ Catch.luckPower * (extraBoost or 1)
		local mutation = rollExtra(Catch.mutations, luckBoost, Events.mutationBoosts())
		local size = rollExtra(Catch.sizes, luckBoost)
		entry = { id = dino.id, mutation = mutation and mutation.id, size = size and size.id }
	end
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
