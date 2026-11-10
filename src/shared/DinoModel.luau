-- Builds a dino: its imported model if it has one (made in Blender, imported into ReplicatedStorage.Assets.Dinos in
-- Studio, saved in the place, not in Rojo), otherwise its block model from ModelBlueprints.
-- A dino with neither gets a plain eight-block stand-in coloured from its name.
-- A mutation tints the skin of an imported model and leaves its face alone. Glowing parts (the Volcano
-- monsters' eyes, mouths and lava) light up, see Roles.
-- Live games load imported models on demand (DinoLibrary): the server keeps them in ServerStorage, and each player gets
-- only the ones their screen needs. On a client, building a monster whose model hasn't arrived asks for it and waits.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local BlockModel = require(script.Parent.BlockModel)
local Catch = require(script.Parent.Config.Catch)
local DinoLife = require(script.Parent.Config.DinoLife)
local DinoStats = require(script.Parent.DinoStats)
local Roles = require(script.Parent.Roles)

local DinoModel = {}

DinoModel.LIBRARY = "DinoLibrary" -- the models' folder in ServerStorage (DinoLibrary)
DinoModel.TEMPLATE_GUI = "DinoTemplates" -- each player's hidden ScreenGui of the models sent to them
DinoModel.ASK_REMOTE = "DinoLibraryAsk" -- RemoteFunction in ReplicatedStorage: ask for models by id

local IS_SERVER = RunService:IsServer()
local ASK_WAIT = 8 -- seconds a client waits for an asked-for model before falling back to its block model

local asked: { [string]: boolean } = {} -- ids this client already asked for, so a missing model isn't asked for again

-- Where a monster's imported model is, or nil if this side doesn't have it (yet).
local function templateOf(dinoId: string): Instance?
	local name = `dino_{dinoId}`
	if IS_SERVER then
		local library = game:GetService("ServerStorage"):FindFirstChild(DinoModel.LIBRARY)
		local template = library and library:FindFirstChild(name)
		if template then
			return template
		end
	else
		local playerGui = Players.LocalPlayer:FindFirstChildOfClass("PlayerGui")
		local folder = playerGui and playerGui:FindFirstChild(DinoModel.TEMPLATE_GUI)
		local template = folder and folder:FindFirstChild(name)
		if template then
			return template
		end
	end
	-- Studio edit mode, and a server that hasn't started DinoLibrary: the models where they're imported.
	local assets = ReplicatedStorage:FindFirstChild("Assets")
	local dinos = assets and assets:FindFirstChild("Dinos")
	return dinos and dinos:FindFirstChild(name)
end

-- Client only: makes sure these monsters' models are here, asking the server for any that aren't, and waits for them
-- (up to ASK_WAIT seconds). Call it before building many at once (the Index), so they come in one request.
function DinoModel.need(dinoIds: { string })
	if IS_SERVER then
		return
	end
	local missing = {}
	for _, dinoId in dinoIds do
		if not asked[dinoId] and not templateOf(dinoId) then
			asked[dinoId] = true
			table.insert(missing, dinoId)
		end
	end
	if #missing == 0 then
		return
	end
	local remote = ReplicatedStorage:FindFirstChild(DinoModel.ASK_REMOTE) :: RemoteFunction?
	if not remote then
		return -- an old server without DinoLibrary: everything is already in ReplicatedStorage
	end
	local ok = pcall(remote.InvokeServer, remote, missing)
	if not ok then
		return
	end
	local folder = Players.LocalPlayer:WaitForChild("PlayerGui"):WaitForChild(DinoModel.TEMPLATE_GUI, ASK_WAIT)
	if not folder then
		return
	end
	-- Replication sends the models before the reply, so this is normally instant. A monster with no imported model
	-- (a block model) never comes, so the wait is short and shared by all of them.
	local deadline = os.clock() + 1
	for _, dinoId in missing do
		while not templateOf(dinoId) and os.clock() < deadline do
			task.wait(0.05)
		end
	end
end

-- The monster's imported model, for preloading its meshes; asks for it on a client if needed. nil if it has none.
function DinoModel.template(dinoId: string): Instance?
	DinoModel.need({ dinoId })
	return templateOf(dinoId)
end

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

-- How big a dino stands on a plot and in the reveal, against a plain first-map monster (every model is first brought
-- to one size, fitScale): its biome's standard size, times its size mutation if it has one, or the size tier feeding has reached when that's bigger (Config/Chonk).
function DinoModel.statueScale(dinoId: string, sizeId: string?, chonk: number?): number
	-- Its caught size, or the size feeding has grown it to when that's bigger (DinoStats.shownSize, Config/Chonk).
	local size = DinoStats.shownSize(sizeId, chonk)
	return DinoStats.standardScale(dinoId) * (if size then size.scale else 1)
end

-- An owned monster's size on the base, on a player's head and as a placement ghost: statueScale, times a special's
-- RESIZE choice (DinoStats.resizeScale).
function DinoModel.entryScale(entry): number
	return DinoModel.statueScale(entry.id, entry.size, entry.chonk) * DinoStats.resizeScale(entry)
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
	local template = DinoModel.template(dinoId)
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

-- Whether a monster's head points along its pivot's +Z rather than -Z, judged from where its head (or jaw) bone is
-- against its tail (or spine) bone. Most imported models face +Z (the importer turns them round); models without
-- those bones face -Z.
function DinoModel.facesBack(model: Model): boolean
	local front, back = nil, nil
	for _, bone in model:GetDescendants() do
		if bone:IsA("Bone") then
			if bone.Name == "Jaw" or (bone.Name == "Head" and not front) then
				front = bone
			end
			if bone.Name == "Tail1" or ((bone.Name == "Spine" or bone.Name == "Swim") and not back) then
				back = bone
			end
		end
	end
	if not front or not back then
		return false
	end
	local pivot = model:GetPivot()
	return pivot:PointToObjectSpace(front.WorldPosition).Z > pivot:PointToObjectSpace(back.WorldPosition).Z
end

local CORNERS = {
	Vector3.new(-1, -1, -1),
	Vector3.new(-1, -1, 1),
	Vector3.new(-1, 1, -1),
	Vector3.new(-1, 1, 1),
	Vector3.new(1, -1, -1),
	Vector3.new(1, -1, 1),
	Vector3.new(1, 1, -1),
	Vector3.new(1, 1, 1),
}

-- The box round the parts you can see (leaving out the invisible bone holder and the Head marker), as its centre
-- and size in the model's pivot space.
function DinoModel.visibleBox(model: Model): (Vector3, Vector3)
	local pivot = model:GetPivot()
	local low, high = Vector3.one * math.huge, -Vector3.one * math.huge
	for _, part in model:GetDescendants() do
		if part:IsA("BasePart") and part.Transparency < 1 then
			local half = part.Size / 2
			for _, corner in CORNERS do
				local point = pivot:PointToObjectSpace(part.CFrame:PointToWorldSpace(half * corner))
				low, high = low:Min(point), high:Max(point)
			end
		end
	end
	if low.X > high.X then
		return Vector3.zero, Vector3.zero
	end
	return (low + high) / 2, high - low
end

-- How high its hips are above its feet (its LegL or FrontL bone), or nil for monsters without legs (swimmers).
function DinoModel.legHeight(model: Model): number?
	local bone = model:FindFirstChild("LegL", true) or model:FindFirstChild("FrontL", true)
	if bone and bone:IsA("Bone") then
		return bone.WorldPosition.Y - model:GetPivot().Y
	end
	return nil
end

-- The model as made, scaled by worldScale, not yet settled.
local function buildRaw(dinoId: string, mutationId: string?, origin: Vector3, worldScale: number): Model
	local mutation = DinoStats.findOption(Catch.mutations, mutationId)
	local imported = buildImported(dinoId, mutation, origin, worldScale)
	if imported then
		return imported
	end
	local blocks = BlockModel.build(`dino_{dinoId}`, origin, mutation and mutation.color, MUTATION_TINT)
	if blocks then
		blocks.Name = "Dino"
		blocks:ScaleTo(worldScale)
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
	model:ScaleTo(worldScale)
	return model
end

-- Every monster's model is made at its own size in Blender (a Compy 4 studs long, Batastrophe 61), so first each is
-- brought to one longest side, Catch.standardLength studs, and only then do its map's standard size and its size
-- mutation multiply it [Owner, 2026-11-09: "a catch with no size mutation is always exactly X", docs/GAME_SPEC.md].
-- Measured once per monster.
local fits: { [string]: number } = {}
function DinoModel.fitScale(dinoId: string): number
	local fit = fits[dinoId]
	if fit then
		return fit
	end
	local probe = buildRaw(dinoId, nil, Vector3.zero, 1)
	local _, size = DinoModel.visibleBox(probe)
	probe:Destroy()
	local longest = math.max(size.X, size.Y, size.Z)
	fit = if longest > 0 then Catch.standardLength / longest else 1
	fits[dinoId] = fit
	return fit
end

-- Builds the dino with its feet at origin. Scaling and spinning happen around the feet. scale is its size against
-- a plain first-map monster (statueScale); 1 means its longest side is Catch.standardLength studs.
-- Not parented: the caller decides where it goes. The "Head" part is the top of the model.
function DinoModel.build(dinoId: string, mutationId: string?, origin: Vector3, scale: number): Model
	local model = settle(buildRaw(dinoId, mutationId, origin, scale * DinoModel.fitScale(dinoId)), scale)
	model:SetAttribute("DinoId", dinoId) -- which monster it is, for DinoLifeController (DinoLife.attackCycle)
	return model
end

return DinoModel
