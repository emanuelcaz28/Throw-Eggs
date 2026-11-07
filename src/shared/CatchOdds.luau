-- The chances behind a catch, worked out exactly. DinoRoll rolls with these and the Details panel of the luck offer
-- shows them (LuckOfferController), so what players read is what the game does. Roblox wants the odds of paid random
-- items shown before buying; lucky chances change with the map and the landing, so they're never typed in anywhere.
local Catch = require(script.Parent.Config.Catch)
local DinoStats = require(script.Parent.DinoStats)
local Dinos = require(script.Parent.Config.Dinos)

local CatchOdds = {}

-- Each monster's chance of hatching, most common first; they add up to 1. luck is counted from the map's par
-- (Config/Luck forRoll) with every boost multiplied in. recent: the ids of the last catches, newest first.
function CatchOdds.monsters(biomeId: string, luck: number, minRank: number?, recent: { string }?): { number }
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
		if rank >= lowest and not (minRank and dino.prize) then -- a guarantee never gives a map's prizes (Config/Dinos)
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

-- Every colour and size that make this monster's catch at least 1 in `minOneIn`, each weighted by how likely it
-- really is (1 / its "1 in X"), and the weights' total. Empty when none does.
function CatchOdds.hitOptions(dinoId: string, minOneIn: number)
	local options, total = {}, 0
	for _, mutation in { false, table.unpack(Catch.mutations) } do
		for _, size in { false, table.unpack(Catch.sizes) } do
			local entry = { id = dinoId, mutation = mutation and mutation.id or nil, size = size and size.id or nil }
			local stats = DinoStats.describe(entry)
			if stats and stats.oneIn >= minOneIn then
				table.insert(options, { entry = entry, weight = 1 / stats.oneIn })
				total += 1 / stats.oneIn
			end
		end
	end
	return options, total
end

-- The "1 in X" a lucky throw of this multiplier guarantees (Config/Catch luckyHits), or nil.
function CatchOdds.hitFor(multiplier: number): number?
	for _, hit in Catch.luckyHits do
		if multiplier >= hit.multiplier then
			return hit.minOneIn
		end
	end
	return nil
end

-- The chance of each colour or size on a plain throw: tried rarest first, the first hit wins (DinoRoll rollExtra).
-- Returns chances by id, with `none` for no colour or size. perOption multiplies single options, by id.
local function plainExtras(options, boost: number, perOption: { [string]: number }?)
	local chances, left = {}, 1
	for _, option in options do
		local optionBoost = boost * (if perOption and perOption[option.id] then perOption[option.id] else 1)
		local chance = math.min(optionBoost / option.chance, Catch.maxChance)
		chances[option.id] = left * chance
		left *= 1 - chance
	end
	chances.none = left
	return chances
end

-- A plain throw's chances: { monsters = by rank, mutations = by id, sizes = by id }.
-- extraBoost: rare colours and sizes likelier on top, from The Deep End's Depth (Config/DeepEnd).
function CatchOdds.plain(biomeId: string, luck: number, perOption: { [string]: number }?, extraBoost: number?)
	local boost = math.max(luck, 1) ^ Catch.luckPower * (extraBoost or 1)
	return {
		monsters = CatchOdds.monsters(biomeId, luck),
		mutations = plainExtras(Catch.mutations, boost, perOption),
		sizes = plainExtras(Catch.sizes, boost),
	}
end

-- A lucky throw's chances, the same shape. luck is the throw's luck before the multiplier. The monster is rolled with
-- all of it, then its colour and size come from CatchOdds.hitOptions; a monster with none gives way to the map's rarest.
function CatchOdds.lucky(biomeId: string, luck: number, multiplier: number)
	local dinos = Dinos[biomeId]
	local minOneIn = CatchOdds.hitFor(multiplier) or 0
	local odds = CatchOdds.monsters(biomeId, luck * multiplier)
	local monsters, mutations, sizes = {}, {}, {}
	for rank = 1, #dinos do
		monsters[rank] = 0
	end
	for rank, dino in dinos do
		local landed = rank
		local options, total = CatchOdds.hitOptions(dino.id, minOneIn)
		if #options == 0 then
			landed = #dinos
			options, total = CatchOdds.hitOptions(dinos[landed].id, minOneIn)
		end
		monsters[landed] += odds[rank]
		for _, option in options do
			local chance = odds[rank] * option.weight / total
			local mutation = option.entry.mutation or "none"
			local size = option.entry.size or "none"
			mutations[mutation] = (mutations[mutation] or 0) + chance
			sizes[size] = (sizes[size] or 0) + chance
		end
	end
	return { monsters = monsters, mutations = mutations, sizes = sizes }
end

return CatchOdds
