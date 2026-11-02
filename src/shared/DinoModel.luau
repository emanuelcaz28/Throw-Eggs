-- Builds a dino: its block model from ModelBlueprints, tinted towards its mutation's colour.
-- A dino without a blueprint gets a plain eight-block stand-in coloured from its name.
local BlockModel = require(script.Parent.BlockModel)
local Catch = require(script.Parent.Config.Catch)
local DinoStats = require(script.Parent.DinoStats)
local Plot = require(script.Parent.Config.Plot)

local DinoModel = {}

local BASE_SATURATION, BASE_VALUE = 0.55, 0.85
local MUTATION_TINT = 0.55 -- how far a mutation pulls the dino's colours towards its own

local BLOCKS = {
	{ Vector3.new(4, 4, 7), Vector3.new(0, 5, 0), "Body" },
	{ Vector3.new(2, 4, 2), Vector3.new(0, 8, -3), "Neck" },
	{ Vector3.new(3, 3, 5), Vector3.new(0, 10, -4.5), "Head" },
	{ Vector3.new(2, 2, 6), Vector3.new(0, 5, 6), "Tail" },
	{ Vector3.new(1.5, 3, 1.5), Vector3.new(-1.5, 1.5, 1.5), "Leg" },
	{ Vector3.new(1.5, 3, 1.5), Vector3.new(1.5, 1.5, 1.5), "Leg" },
	{ Vector3.new(1.5, 3, 1.5), Vector3.new(-1.5, 1.5, -1.5), "Leg" },
	{ Vector3.new(1.5, 3, 1.5), Vector3.new(1.5, 1.5, -1.5), "Leg" },
}

function DinoModel.color(name: string, mutationId: string?): Color3
	local mutation = DinoStats.findOption(Catch.mutations, mutationId)
	if mutation then
		return mutation.color
	end
	local hue = 0
	for index = 1, #name do
		hue = (hue + name:byte(index) * index) % 360
	end
	return Color3.fromHSV(hue / 360, BASE_SATURATION, BASE_VALUE)
end

-- How big a dino of this size stands on a plot.
function DinoModel.statueScale(sizeId: string?): number
	local size = DinoStats.findOption(Catch.sizes, sizeId)
	return math.min(if size then size.scale else 1, Plot.maxStatueScale)
end

-- Builds the dino with its feet at origin. Scaling and spinning happen around the feet.
-- Not parented: the caller decides where it goes. The "Head" part is the top of the model.
function DinoModel.build(dinoId: string, mutationId: string?, origin: Vector3, scale: number): Model
	local mutation = DinoStats.findOption(Catch.mutations, mutationId)
	local blocks = BlockModel.build(`dino_{dinoId}`, origin, mutation and mutation.color, MUTATION_TINT)
	if blocks then
		blocks.Name = "Dino"
		blocks:ScaleTo(scale)
		return blocks
	end
	local color = DinoModel.color(dinoId, mutationId)
	local model = Instance.new("Model")
	model.Name = "Dino"
	for _, block in BLOCKS do
		local part = Instance.new("Part")
		part.Name = block[3]
		part.Anchored = true
		part.CanCollide = false
		part.CanQuery = false
		part.CanTouch = false
		part.Size = block[1]
		part.Color = color
		part.CFrame = CFrame.new(origin + block[2])
		part.Parent = model
	end
	model.WorldPivot = CFrame.new(origin)
	model:ScaleTo(scale)
	return model
end

return DinoModel
