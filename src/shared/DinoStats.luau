-- Works out a dino's numbers from what's stored about it (id, mutation, size), so
-- changing the configs later also applies to dinos players already own.
local Biomes = require(script.Parent.Config.Biomes)
local Catch = require(script.Parent.Config.Catch)
local Chonk = require(script.Parent.Config.Chonk)
local Dinos = require(script.Parent.Config.Dinos)
local Specials = require(script.Parent.Config.Specials)

local DinoStats = {}

local dinosById = {}
local standardScaleById = {}
for _, biome in Biomes do
	for _, dino in Dinos[biome.id] or {} do
		dinosById[dino.id] = dino
		standardScaleById[dino.id] = biome.standardScale
	end
end

-- A monster's place in its own map's list, most common first: its rarity (1 Common ... 8 Secret, UiKit.RARITY_ORDER).
local rarityRankById = {}
for key, list in Dinos do
	if key ~= "DeepPool" then -- a mix of worlds: places in it mean nothing
		for index, dino in list do
			rarityRankById[dino.id] = index
		end
	end
end

-- That place, or nil for a monster from no map (the specials).
function DinoStats.rarityRank(dinoId: string): number?
	return rarityRankById[dinoId]
end

-- How big a dino is with no size mutation: its biome's standard size.
function DinoStats.standardScale(dinoId: string): number
	return standardScaleById[dinoId] or 1
end

function DinoStats.findOption(options, id: string?)
	for _, option in options do
		if option.id == id then
			return option
		end
	end
	return nil
end

-- The Config/Specials entry for this id, or nil for a monster from a map.
function DinoStats.special(id: string?)
	return DinoStats.findOption(Specials, id)
end

-- Whether a monster can be sold (or fed to another): all but the specials, bought with Robux, so they're never lost by
-- mistake [Owner, 2026-11-08]. Their row has RESIZE where SELL was (PlotController, Config/Specials resizes).
function DinoStats.sellable(id: string?): boolean
	return DinoStats.special(id) == nil
end

-- The sizes a special can be set to with RESIZE, smallest first: its normal size, then each size mutation's scale. Only
-- how big it looks: its income stays what it was when bought.
local resizes = { { id = "Normal", name = "NORMAL", scale = 1 } }
for index = #Catch.sizes, 1, -1 do
	table.insert(resizes, Catch.sizes[index])
end
DinoStats.resizes = resizes

-- How much bigger a special shows, from its saved RESIZE choice (entry.resize); 1 for everything else.
function DinoStats.resizeScale(entry): number
	local option = DinoStats.special(entry.id) and DinoStats.findOption(resizes, entry.resize)
	return if option then option.scale else 1
end

-- The "1 in X" players see is the real chance of exactly that catch on a plain throw at its map's start (luck 1, the
-- map's own egg, no boosts), worked out from the rolls themselves (DinoRoll): which monster comes, then the colour, then
-- the size. [Owner, 2026-11-06] wanted no round numbers ("1 in 32,000", "1 in 10,000"): multiplying the configs' round
-- chances gave those; the real chances come out like "1 in 482,947", and they're true.
local monsterChance: { [string]: number } = {} -- the chance its map's roll picks it, at luck 1
for _, biome in Biomes do
	local list = Dinos[biome.id] or {}
	local commonest = list[1] and list[1].chance or 1
	local total = 0
	for _, dino in list do
		total += (commonest / dino.chance) ^ Catch.pick.falloff
	end
	for _, dino in list do
		monsterChance[dino.id] = (commonest / dino.chance) ^ Catch.pick.falloff / total
	end
end

-- The colour and size rolls try the rarest first and stop at the first hit, each at its own chance (DinoRoll).
local function extraChances(options): ({ [string]: number }, number)
	local chances, none = {}, 1
	for _, option in options do
		local chance = math.min(1 / option.chance, Catch.maxChance)
		chances[option.id] = none * chance
		none *= 1 - chance
	end
	return chances, none
end
local mutationChance, noMutation = extraChances(Catch.mutations)
local sizeChance, noSize = extraChances(Catch.sizes)

-- The monster's own "1 in X" whatever its colour and size (the Index shows it).
function DinoStats.monsterOneIn(dinoId: string): number
	local chance = monsterChance[dinoId]
	return if chance then math.max(math.floor(1 / chance + 0.5), 1) else 1
end

-- Returns { name, income, oneIn }, or nil if the dino no longer exists in the configs.
function DinoStats.describe(entry)
	local special = DinoStats.special(entry.id)
	if special then
		return { name = special.name, income = entry.income or 0, oneIn = 1 } -- its income was fixed when bought
	end
	local dino = dinosById[entry.id]
	if not dino then
		return nil
	end
	local chance = monsterChance[dino.id] or 1 / dino.chance
	local income = dino.income
	local mutation = DinoStats.findOption(Catch.mutations, entry.mutation)
	if mutation then
		chance *= mutationChance[mutation.id]
		income *= mutation.incomeMultiplier
	else
		chance *= noMutation
	end
	local size = DinoStats.findOption(Catch.sizes, entry.size)
	if size then
		chance *= sizeChance[size.id]
		income *= size.incomeMultiplier
	else
		chance *= noSize
	end
	income *= Chonk.incomeMultiplier(entry.chonk)
	return { name = dino.name, income = income, oneIn = math.max(math.floor(1 / chance + 0.5), 1) }
end

return DinoStats
