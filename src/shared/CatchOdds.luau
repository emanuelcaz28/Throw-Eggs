-- The chances behind a catch, worked out exactly. DinoRoll rolls with these and the Details panel of the luck offer
-- shows them (LuckOfferController), so what players read is what the game does. Roblox wants the odds of paid random
-- items shown before buying; lucky chances change with the map and the landing, so they're never typed in anywhere.
local Catch = require(script.Parent.Config.Catch)
local DinoStats = require(script.Parent.DinoStats)
local Dinos = require(script.Parent.Config.Dinos)

local CatchOdds = {}

-- Each monster's chance of hatching, most common first; they add up to 1. luck is counted from the map's par
-- (Config/Luck forRoll) with every boost multiplied in. recent: the ids of the last catches, newest first.
-- filter (lucky throws and the surprise gift), all optional: minRarity / maxRarity leave out monsters of a lower /
-- higher rarity level (1 Common ... 8 Secret, the words in Config/RarityLadder); minPlace leaves out monsters more common
-- than that place in their home map's list (DinoStats.rarityRank), maxPlace those rarer than it. All go by the monster's home map, so they also work
-- in The Deep End's mixed list. only: just these monster ids (the starter run's missing monsters, Config/Hooks).
-- falloff: used in place of Config/Catch pick.falloff (the x500's, which leans towards the rare end).
export type Filter = { minRarity: number?, maxRarity: number?, minPlace: number?, maxPlace: number?, only: { [string]: boolean }?, falloff: number? }
local function passes(dinoId: string, filter: Filter?): boolean
	if not filter then
		return true
	end
	if filter.only and not filter.only[dinoId] then
		return false
	end
	local level = DinoStats.rarityLevel(dinoId) or 1
	local place = DinoStats.rarityRank(dinoId) or 1
	return not ((filter.minRarity and level < filter.minRarity) or (filter.maxRarity and level > filter.maxRarity)
		or (filter.minPlace and place < filter.minPlace) or (filter.maxPlace and place > filter.maxPlace))
end

function CatchOdds.monsters(biomeId: string, luck: number, minRank: number?, recent: { string }?, filter: Filter?): { number }
	local dinos = Dinos[biomeId]
	local pick = Catch.pick
	local count = #dinos
	local lowest = math.clamp(minRank or 1, 1, count)

	-- The aim: the commonest monster's odds times the luck, stopped part of the way to the rarest.
	local commonest = dinos[1].chance
	local top = if count > 1 then dinos[count - 1].chance ^ (1 - pick.topAim) * dinos[count].chance ^ pick.topAim else commonest
	local aim = math.clamp(commonest * luck, commonest, math.max(top, commonest))

	local falloff = if filter and filter.falloff then filter.falloff else pick.falloff
	local weights, total = {}, 0
	for rank, dino in dinos do
		local weight = 0
		if rank >= lowest and not (minRank and dino.prize) and passes(dino.id, filter) then -- a guarantee never gives a map's prizes (Config/Dinos)
			weight = math.min(dino.chance / aim, aim / dino.chance) ^ falloff
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

-- The rarest monster of this list the filter lets through (its place in the list), or the list's last with none. A
-- lucky throw falls back on it when the rolled monster has no colour and size rare enough (DinoRoll.rollCatch).
function CatchOdds.rarestAllowed(biomeId: string, filter: Filter?): number
	local dinos = Dinos[biomeId]
	for rank = #dinos, 1, -1 do
		if passes(dinos[rank].id, filter) then
			return rank
		end
	end
	return #dinos
end

-- Whether any monster in this list gets through the filter; nonPrize: and isn't one of its map's prizes.
function CatchOdds.hasAny(biomeId: string, filter: Filter, nonPrize: boolean?): boolean
	for _, dino in Dinos[biomeId] or {} do
		if passes(dino.id, filter) and not (nonPrize and dino.prize) then
			return true
		end
	end
	return false
end

-- Which monsters the surprise gift (Config/Hooks surpriseGift) may be on this map, as a filter, or nil when the gift
-- doesn't count here. Where the only Legendaries and Mythics are the map's prizes (maps 3 and 4), its Epics instead.
function CatchOdds.giftFilter(biomeId: string, gift): Filter?
	local filter = { minRarity = gift.minRarity, maxRarity = gift.maxRarity, minPlace = gift.minPlace }
	if not CatchOdds.hasAny(biomeId, filter) then
		return nil
	end
	if not CatchOdds.hasAny(biomeId, filter, true) then
		return { minRarity = gift.prizeOnlyRarity, maxRarity = gift.prizeOnlyRarity }
	end
	return filter
end

-- What a lucky throw on this map may give (a CatchOdds.monsters filter), and whether the map falls short of the
-- line's rarity. A map with no monster that rare (maps 1 and 2 have no Legendary, Config/RarityLadder) gives its
-- rarest word instead, with big sizes made far likelier (Config/Catch shortMapSizeBoost) [Owner, 2026-11-08].
function CatchOdds.luckyFilter(biomeId: string, hit): (Filter?, boolean)
	if not hit.minRarity then
		-- No rarity word asked (the daily x50): only its places in the map's list, if it names any.
		if hit.minPlace or hit.maxPlace then
			return { minPlace = hit.minPlace, maxPlace = hit.maxPlace, falloff = hit.falloff }, false
		end
		return nil, false
	end
	local top = DinoStats.topRarityLevel(biomeId)
	return { minRarity = math.min(hit.minRarity, top), minPlace = hit.minPlace, maxPlace = hit.maxPlace, falloff = hit.falloff }, top < hit.minRarity
end

-- Every colour and size that make this monster's catch at least 1 in `minOneIn`, each weighted by how likely it
-- really is (1 / its "1 in X"), and the weights' total. Empty when none does. colourAndSize: leaves out no colour
-- and normal size (Config/Catch luckyHits). sizeBoost: each size's weight is also multiplied by its own "1 in X" to
-- this power, so 1 makes every size as likely as the others (Config/Catch shortMapSizeBoost).
function CatchOdds.hitOptions(dinoId: string, minOneIn: number, colourAndSize: boolean?, sizeBoost: number?)
	local options, total = {}, 0
	local mutations = if colourAndSize then Catch.mutations else { false, table.unpack(Catch.mutations) }
	local sizes = if colourAndSize then Catch.sizes else { false, table.unpack(Catch.sizes) }
	for _, mutation in mutations do
		for _, size in sizes do
			local entry = { id = dinoId, mutation = mutation and mutation.id or nil, size = size and size.id or nil }
			local stats = DinoStats.describe(entry)
			if stats and stats.oneIn >= minOneIn then
				local weight = 1 / stats.oneIn
				if sizeBoost and size then
					weight *= size.chance ^ sizeBoost
				end
				table.insert(options, { entry = entry, weight = weight })
				total += weight
			end
		end
	end
	return options, total
end

-- The Config/Catch luckyHits line a lucky throw of this multiplier uses, or nil.
function CatchOdds.luckyHit(multiplier: number)
	for _, hit in Catch.luckyHits do
		if multiplier >= hit.multiplier then
			return hit
		end
	end
	return nil
end

-- The "1 in X" a lucky throw of this multiplier guarantees (Config/Catch luckyHits), or nil.
function CatchOdds.hitFor(multiplier: number): number?
	local hit = CatchOdds.luckyHit(multiplier)
	return hit and hit.minOneIn
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
-- all of it, then its colour and size come from CatchOdds.hitOptions; a monster with none gives way to the rarest one
-- the throw may give (CatchOdds.rarestAllowed).
function CatchOdds.lucky(biomeId: string, luck: number, multiplier: number)
	local dinos = Dinos[biomeId]
	local hit = CatchOdds.luckyHit(multiplier) or { minOneIn = 0 }
	local minOneIn, colourAndSize = hit.minOneIn, hit.colourAndSize
	local filter, short = CatchOdds.luckyFilter(biomeId, hit)
	local sizeBoost = if short then Catch.shortMapSizeBoost else nil
	local odds = CatchOdds.monsters(biomeId, luck * multiplier, nil, nil, filter)
	local monsters, mutations, sizes = {}, {}, {}
	for rank = 1, #dinos do
		monsters[rank] = 0
	end
	for rank, dino in dinos do
		local landed = rank
		local options, total = CatchOdds.hitOptions(dino.id, minOneIn, colourAndSize, sizeBoost)
		if #options == 0 then
			landed = CatchOdds.rarestAllowed(biomeId, filter)
			options, total = CatchOdds.hitOptions(dinos[landed].id, minOneIn, colourAndSize, sizeBoost)
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
