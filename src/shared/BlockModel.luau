-- Builds the block models in ModelBlueprints (dinos, eggs, biome islands, shop art) as Parts.
-- They match the Blender blueprints in assets/models. A model's pivot sits at the centre of its
-- feet and it faces -Z, so scaling and spinning happen around the feet.
local Blueprints = require(script.Parent.ModelBlueprints)

local BlockModel = {}

BlockModel.BLOCK = 0.6 -- studs per block at scale 1

local palette = {}
for index, hex in Blueprints.palette do
	palette[index] = Color3.fromHex(hex)
end

local boundsCache = {}

local function boundsOf(name: string)
	if boundsCache[name] then
		return boundsCache[name]
	end
	local minX, maxX, minY, maxY, minZ, maxZ = math.huge, -math.huge, math.huge, -math.huge, math.huge, -math.huge
	for _, box in Blueprints.models[name] do
		local x, y, z, sx, sy, sz = box[1], box[2], box[3], box[4], box[5], box[6]
		minX, maxX = math.min(minX, x), math.max(maxX, x + sx)
		minY, maxY = math.min(minY, y), math.max(maxY, y + sy)
		minZ, maxZ = math.min(minZ, z), math.max(maxZ, z + sz)
	end
	local bounds = { midX = (minX + maxX) / 2, midY = (minY + maxY) / 2, minZ = minZ, length = maxX - minX, width = maxY - minY, height = maxZ - minZ }
	boundsCache[name] = bounds
	return bounds
end

function BlockModel.has(name: string): boolean
	return Blueprints.models[name] ~= nil
end

-- Size in studs at scale 1: X across, Y up, Z along the body.
function BlockModel.extents(name: string): Vector3
	local b = boundsOf(name)
	return Vector3.new(b.width, b.height, b.length) * BlockModel.BLOCK
end

-- Not parented: the caller decides where it goes. tint pulls every colour towards it (mutations).
-- The invisible "Head" part marks the top centre, for name signs.
function BlockModel.build(name: string, origin: Vector3, tint: Color3?, tintAmount: number?): Model?
	local boxes = Blueprints.models[name]
	if not boxes then
		return nil
	end
	local b = boundsOf(name)
	local s = BlockModel.BLOCK
	local model = Instance.new("Model")
	model.Name = name
	for _, box in boxes do
		local x, y, z, sx, sy, sz, colourIndex = box[1], box[2], box[3], box[4], box[5], box[6], box[7]
		local part = Instance.new("Part")
		part.Anchored = true
		part.CanCollide = false
		part.CanQuery = false
		part.CanTouch = false
		part.Material = Enum.Material.SmoothPlastic
		part.TopSurface = Enum.SurfaceType.Smooth
		part.BottomSurface = Enum.SurfaceType.Smooth
		local colour = palette[colourIndex]
		part.Color = if tint then colour:Lerp(tint, tintAmount or 0.55) else colour
		part.Size = Vector3.new(sy, sz, sx) * s
		local centre = Vector3.new(y + sy / 2 - b.midY, z + sz / 2 - b.minZ, -(x + sx / 2 - b.midX))
		part.CFrame = CFrame.new(origin + centre * s)
		part.Parent = model
	end
	local head = Instance.new("Part")
	head.Name = "Head"
	head.Anchored = true
	head.CanCollide = false
	head.CanQuery = false
	head.CanTouch = false
	head.Transparency = 1
	head.Size = Vector3.one * 0.2
	head.CFrame = CFrame.new(origin + Vector3.new(0, b.height * s, 0))
	head.Parent = model
	model.WorldPivot = CFrame.new(origin)
	return model
end

return BlockModel
