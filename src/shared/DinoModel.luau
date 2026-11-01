-- Stand-in dino until the real models exist: blocks, with a colour picked from the
-- name, or the mutation's colour if it has one.
local Catch = require(script.Parent.Config.Catch)
local DinoStats = require(script.Parent.DinoStats)

local DinoModel = {}

local BASE_SATURATION, BASE_VALUE = 0.55, 0.85

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

-- Builds the dino with its feet at origin. Scaling and spinning happen around the feet.
-- Not parented: the caller decides where it goes.
function DinoModel.build(name: string, mutationId: string?, origin: Vector3, scale: number): Model
	local color = DinoModel.color(name, mutationId)
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
