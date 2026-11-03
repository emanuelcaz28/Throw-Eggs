-- Works out a dino's numbers from what's stored about it (id, mutation, size), so
-- changing the configs later also applies to dinos players already own.
local Biomes = require(script.Parent.Config.Biomes)
local Catch = require(script.Parent.Config.Catch)
local Dinos = require(script.Parent.Config.Dinos)

local DinoStats = {}

local dinosById = {}
local standardScaleById = {}
for _, biome in Biomes do
	for _, dino in Dinos[biome.id] or {} do
		dinosById[dino.id] = dino
		standardScaleById[dino.id] = biome.standardScale
	end
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

-- Returns { name, income, oneIn }, or nil if the dino no longer exists in the configs.
function DinoStats.describe(entry)
	local dino = dinosById[entry.id]
	if not dino then
		return nil
	end
	local oneIn = dino.chance
	local income = dino.income
	for _, extra in { DinoStats.findOption(Catch.mutations, entry.mutation), DinoStats.findOption(Catch.sizes, entry.size) } do
		oneIn *= extra.chance
		income *= extra.incomeMultiplier
	end
	return { name = dino.name, income = income, oneIn = oneIn }
end

return DinoStats
