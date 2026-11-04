-- Builds a dino: its imported model from ReplicatedStorage.Assets.Dinos if it has one (made in
-- Blender, saved in the place, not in Rojo), otherwise its block model from ModelBlueprints.
-- A dino with neither gets a plain eight-block stand-in coloured from its name.
-- A mutation tints the skin of an imported model and leaves its face alone. Glowing parts (the Volcano
-- monsters' eyes, mouths and lava) light up, see Roles.
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local BlockModel = require(script.Parent.BlockModel)
local Catch = require(script.Parent.Config.Catch)
local DinoLife = require(script.Parent.Config.DinoLife)
local DinoStats = require(script.Parent.DinoStats)
local Roles = require(script.Parent.Roles)

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

-- How big a dino stands on a plot and in the reveal: its biome's standard size, times its size
-- mutation if it has one.
function DinoModel.statueScale(dinoId: string, sizeId: string?): number
	local size = DinoStats.findOption(Catch.sizes, sizeId)
	return DinoStats.standardScale(dinoId) * (if size then size.scale else 1)
end

local SKIN_ROLES = { Body = true, Accent = true, Belly = true, Claw = true }
local SKIN_TINT = 0.75

-- Bones only move the parts joined to the part that holds them, and the importer leaves the colour parts
-- loose. So each part that isn't joined yet gets a Motor6D to the bones' part; models joined in Studio
-- before are left as they are.
local function joinParts(model: Model)
	local holder = nil
	for _, bone in model:GetDescendants() do
		if bone:IsA("Bone") then
			holder = bone:FindFirstAncestorWhichIsA("BasePart")
			break
		end
	end
	if not holder then
		return
	end
	local joined = { [holder] = true }
	for _, joint in model:GetDescendants() do
		if joint:IsA("JointInstance") or joint:IsA("WeldConstraint") then
			if joint.Part0 then
				joined[joint.Part0] = true
			end
			if joint.Part1 then
				joined[joint.Part1] = true
			end
		end
	end
	for _, part in model:GetDescendants() do
		if part:IsA("BasePart") and not joined[part] then
			local motor = Instance.new("Motor6D")
			motor.Part0 = holder
			motor.Part1 = part
			motor.C0 = holder.CFrame:ToObjectSpace(part.CFrame)
			motor.Parent = holder
		end
	end
end

local function buildImported(dinoId: string, mutation, origin: Vector3, scale: number): Model?
	local assets = ReplicatedStorage:FindFirstChild("Assets")
	local dinos = assets and assets:FindFirstChild("Dinos")
	local template = dinos and dinos:FindFirstChild(`dino_{dinoId}`)
	if not template then
		return nil
	end
	local model = template:Clone()
	model.Name = "Dino"
	for _, part in model:GetDescendants() do
		if part:IsA("BasePart") then
			part.Anchored = true
			if mutation and SKIN_ROLES[Roles.of(part)] then
				part.Color = part.Color:Lerp(mutation.color, SKIN_TINT)
			end
		end
	end
	joinParts(model)
	Roles.lightUp(model)
	local _, extents = model:GetBoundingBox()
	local head = Instance.new("Part")
	head.Name = "Head"
	head.Anchored = true
	head.CanCollide = false
	head.CanQuery = false
	head.CanTouch = false
	head.Transparency = 1
	head.Size = Vector3.one * 0.2
	head.CFrame = model:GetPivot() + Vector3.new(0, extents.Y, 0)
	head.Parent = model
	model:PivotTo(CFrame.new(origin))
	model:ScaleTo(scale)
	return model
end

-- Monsters are scenery: players walk straight through them (a giant on your base would otherwise knock you off
-- it), and only ones of normal size cast a shadow (Config/DinoLife shadowMaxScale).
local function settle(model: Model, scale: number): Model
	local shadow = scale <= DinoLife.shadowMaxScale
	for _, part in model:GetDescendants() do
		if part:IsA("BasePart") then
			part.CanCollide = false
			part.CanTouch = false
			part.CastShadow = shadow
		end
	end
	return model
end

-- Builds the dino with its feet at origin. Scaling and spinning happen around the feet.
-- Not parented: the caller decides where it goes. The "Head" part is the top of the model.
function DinoModel.build(dinoId: string, mutationId: string?, origin: Vector3, scale: number): Model
	local mutation = DinoStats.findOption(Catch.mutations, mutationId)
	local imported = buildImported(dinoId, mutation, origin, scale)
	if imported then
		return settle(imported, scale)
	end
	local blocks = BlockModel.build(`dino_{dinoId}`, origin, mutation and mutation.color, MUTATION_TINT)
	if blocks then
		blocks.Name = "Dino"
		blocks:ScaleTo(scale)
		return settle(blocks, scale)
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
	return settle(model, scale)
end

return DinoModel
