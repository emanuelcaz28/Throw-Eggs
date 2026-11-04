-- Builds the map from the Blender pieces in ReplicatedStorage.Assets.Maps (Config/Map): the sunken
-- arena (kit_Arena), the orange throw platform in its front wall, and the corridor below it, one
-- 64-stud section after another past the farthest biome, each biome's sections in its own colours.
-- Runs before every other service, so the floor is there before anyone spawns.
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Biomes = require(ReplicatedStorage.Shared.Config.Biomes)
local Map = require(ReplicatedStorage.Shared.Config.Map)
local Roles = require(ReplicatedStorage.Shared.Roles)
local World = require(ReplicatedStorage.Shared.World)
local MapDecor = require(script.Parent.MapDecor)

local MapService = {}

-- The Blender pieces use the corridor floor as their zero; the game uses the arena floor.
local KIT_OFFSET = Vector3.new(0, Map.corridor.floorY, 0)

-- A copy of a Blender piece. A missing one is skipped with a warning, so the rest of the game still runs.
local function kitPiece(folder: Instance?, name: string): Model?
	local piece = folder and folder:FindFirstChild(name)
	if not piece then
		warn(`[MapService] {name} is missing from ReplicatedStorage.Assets.Maps: import it from assets/models/fbx`)
		return nil
	end
	return piece:Clone()
end

local function prepare(model: Model, colors: { [string]: Color3 }?)
	for _, part in model:GetDescendants() do
		if part:IsA("BasePart") then
			part.Anchored = true
			part.CastShadow = false -- huge walls would put whole corridor sections in shade
			local color = colors and colors[Roles.of(part)]
			if color then
				part.Color = color
			end
		end
	end
end

-- Places a kit piece by its position in the Blender file, moved along -Z by `along` studs.
local function place(parent: Instance, folder: Instance?, name: string, along: number, colors: { [string]: Color3 }?)
	local piece = kitPiece(folder, name)
	if not piece then
		return
	end
	prepare(piece, colors)
	piece:PivotTo(piece:GetPivot() + KIT_OFFSET - Vector3.new(0, 0, along))
	piece.Parent = parent
end

local function biomeColorsAt(distance: number)
	for _, biome in Biomes do
		if distance < biome.endDist then
			return Map.biomeColors[biome.id]
		end
	end
	return Map.biomeColors[Biomes[#Biomes].id]
end

local function buildCorridor(parent: Instance, kit: Instance)
	local corridor = Map.corridor
	local model = Instance.new("Model")
	model.Name = "Corridor"
	-- The corridor runs far from the players. Without this, Roblox may not send distant parts to
	-- the client and the egg would fly over nothing.
	model.ModelStreamingMode = Enum.ModelStreamingMode.Persistent

	local length = Biomes[#Biomes].endDist + corridor.extra
	-- Each section takes the colours of the biome at its middle, so the change is never more than
	-- half a section from where the biome starts.
	local half = corridor.section / 2
	for start = 0, length - 1, corridor.section do
		place(model, kit, "kit_Floor", start, biomeColorsAt(start + half))
	end
	-- The kit's walls start at its throw line; these start where the arena's front walls end.
	for start = -corridor.wallStartZ, length - 1, corridor.section do
		local colors = biomeColorsAt(start + half)
		place(model, kit, "kit_WallWest", start, colors)
		place(model, kit, "kit_WallEast", start, colors)
	end

	-- The far end: a dirt wall up to the rim between the corridor walls, in the last biome's colour.
	local walls = Map.walls
	local endZ = -length
	local height = walls.rimY - walls.bottomY
	local lastColors = biomeColorsAt(length)
	local endWall = World.makePart(
		model,
		"EndWall",
		Vector3.new(Map.platform.width, height, 8),
		CFrame.new(0, walls.bottomY + height / 2, endZ - 4),
		lastColors and lastColors.Dirt or Map.colors.dirt
	)
	endWall.CastShadow = false

	model.Parent = parent
end

-- An invisible wall along the throw line, so players can't walk off the platform into the corridor.
local function buildBarrier(parent: Instance)
	local platform = Map.platform
	local height = Map.corridor.barrierHeight
	local barrier = World.makePart(
		parent,
		"ThrowLineBarrier",
		Vector3.new(platform.width, height, 1),
		CFrame.new(0, platform.top + height / 2, -0.5),
		Color3.new(1, 1, 1)
	)
	barrier.Transparency = 1
	barrier.CastShadow = false
end

function MapService.start()
	local assets = ReplicatedStorage:WaitForChild("Assets"):WaitForChild("Maps"):WaitForChild("Forest")
	local kit = assets:WaitForChild("Corridor")

	-- The old flat ground is replaced by the arena.
	local baseplate = workspace:FindFirstChild("Baseplate")
	if baseplate then
		baseplate:Destroy()
	end
	local spawn = workspace:FindFirstChildOfClass("SpawnLocation")
	if spawn then
		spawn.CFrame = CFrame.lookAt(Map.spawn + Vector3.new(0, spawn.Size.Y / 2, 0), Map.spawn + Vector3.new(0, spawn.Size.Y / 2, 1))
	end

	local folder = Instance.new("Folder")
	folder.Name = "Map"
	place(folder, assets:FindFirstChild("Arena"), "kit_Arena", 0)
	place(folder, kit, "kit_Platform", 0)
	buildCorridor(folder, kit)
	buildBarrier(folder)
	MapDecor.build(folder)
	folder.Parent = workspace
end

return MapService
