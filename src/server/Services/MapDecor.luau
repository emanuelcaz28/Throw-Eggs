-- Puts the Blender props around the map (Config/Decor): trees, hedges, rocks and the rest along each
-- biome's stretch of the corridor and up on its rims, eggs along the arena's rim, and small things
-- behind the bases. Called by MapService once the arena and corridor are built.
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Biomes = require(ReplicatedStorage.Shared.Config.Biomes)
local Decor = require(ReplicatedStorage.Shared.Config.Decor)
local Map = require(ReplicatedStorage.Shared.Config.Map)

local MapDecor = {}

type PropChoice = { name: string, weight: number, scale: { number } }

local maps = ReplicatedStorage:WaitForChild("Assets"):WaitForChild("Maps")

local function propsOf(biomeId: string): Instance?
	local biome = maps:FindFirstChild(biomeId)
	return biome and biome:FindFirstChild("Props")
end

-- A copy of a prop standing on `position`, turned `yaw` degrees and scaled. Props nobody can reach
-- aren't solid, which also keeps them out of the physics. A missing prop is skipped with a warning.
local function place(parent: Instance, folder: Instance, name: string, position: Vector3, yaw: number, scale: number, solid: boolean)
	local original = folder:FindFirstChild(name)
	if not original then
		warn(`[MapDecor] {name} is missing from {folder:GetFullName()}: import it from assets/models/fbx`)
		return
	end
	local model = original:Clone() :: Model
	for _, part in model:GetDescendants() do
		if part:IsA("BasePart") then
			part.Anchored = true
			part.CanCollide = solid
			part.CanTouch = false
		end
	end
	if scale ~= 1 then
		model:ScaleTo(scale)
	end
	model:PivotTo(CFrame.new(position) * CFrame.Angles(0, math.rad(yaw), 0))
	model.Parent = parent
end

local function pick(rng: Random, choices: { PropChoice }): PropChoice
	local total = 0
	for _, choice in choices do
		total += choice.weight
	end
	local roll = rng:NextNumber() * total
	for _, choice in choices do
		roll -= choice.weight
		if roll <= 0 then
			return choice
		end
	end
	return choices[#choices]
end

local function between(rng: Random, range: { number }): number
	return rng:NextNumber(range[1], range[2])
end

-- One random prop from `choices` at `x`, distance `distance` down the corridor, height `y`.
local function placeRandom(parent: Instance, folder: Instance, rng: Random, choices: { PropChoice }, x: number, y: number, distance: number)
	local choice = pick(rng, choices)
	place(parent, folder, choice.name, Vector3.new(x, y, -distance), rng:NextNumber(0, 360), between(rng, choice.scale), false)
end

local function decorateBiome(parent: Instance, biome, rules)
	local folder = propsOf(biome.id)
	if not folder then
		return
	end
	local rng = Random.new(rules.seed)
	local wallInside = Map.platform.width / 2

	local floor = rules.floor
	local distance = biome.startDist + floor.firstDistance
	while distance < biome.endDist - floor.gap[1] do
		local side = if rng:NextNumber() < 0.5 then -1 else 1
		local x = side * between(rng, floor.side)
		placeRandom(parent, folder, rng, floor.props, x, Map.corridor.floorY, distance)
		local extras = floor.extras
		if rng:NextNumber() < extras.chance then
			-- Kept between the middle and the wall, whichever way it falls.
			local extraX = side * math.clamp(math.abs(x) + rng:NextNumber(-extras.spread, extras.spread), floor.side[1] - 4, wallInside - 3)
			local extraDistance = distance + rng:NextNumber(-extras.spread, extras.spread)
			placeRandom(parent, folder, rng, extras.props, extraX, Map.corridor.floorY, extraDistance)
		end
		distance += between(rng, floor.gap)
	end

	local rim = rules.rim
	distance = biome.startDist + rim.firstDistance
	while distance < biome.endDist do
		for _, side in { -1, 1 } do
			if rng:NextNumber() < rim.chance then
				placeRandom(parent, folder, rng, rim.props, side * between(rng, rim.side), Map.walls.rimY, distance)
			end
		end
		distance += between(rng, rim.gap)
	end
end

local function decorateArena(parent: Instance)
	local arena = Decor.arena
	local folder = propsOf(arena.biome)
	if not folder then
		return
	end

	local eggs = arena.rimEggs
	local half = Map.arena.halfWidth
	local y = Map.walls.rimY
	local function egg(x: number, z: number, yaw: number)
		place(parent, folder, eggs.name, Vector3.new(x, y, z), yaw, 1, false)
	end
	-- Back and front rims, the front one split by the corridor's mouth.
	local x = -half + eggs.spacing / 2
	while x < half do
		egg(x, Map.arena.backZ + eggs.inset, 180)
		if math.abs(x) > Map.platform.width / 2 + eggs.clearOfCorridor then
			egg(x, Map.arena.frontZ - eggs.inset, 0)
		end
		x += eggs.spacing
	end
	-- The two side rims.
	local z = Map.arena.frontZ + eggs.spacing / 2
	while z < Map.arena.backZ do
		egg(-half - eggs.inset, z, 90)
		egg(half + eggs.inset, z, -90)
		z += eggs.spacing
	end

	for _, spot in arena.backStrip do
		place(parent, folder, spot.name, spot.position, spot.yaw, spot.scale, true)
	end
	for _, spot in arena.rimTrees do
		place(parent, folder, spot.name, spot.position, spot.yaw, spot.scale, false)
	end
end

function MapDecor.build(parent: Instance)
	local arena = Instance.new("Folder")
	arena.Name = "ArenaDecor"
	decorateArena(arena)
	arena.Parent = parent

	-- Streamed to everyone like the corridor itself, so the egg never flies past bare ground.
	local corridor = Instance.new("Model")
	corridor.Name = "CorridorDecor"
	corridor.ModelStreamingMode = Enum.ModelStreamingMode.Persistent
	for _, biome in Biomes do
		local rules = Decor.corridor[biome.id]
		if rules then
			decorateBiome(corridor, biome, rules)
		end
	end
	corridor.Parent = parent
end

return MapDecor
