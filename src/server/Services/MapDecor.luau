-- Puts the Blender props around the map (Config/Decor): trees, hedges, rocks and the rest along each
-- biome's stretch of the corridor and up on its rims, set pieces across it and down its walls, eggs
-- along the arena's rim, and small things behind the bases. Called by MapService once the arena and
-- corridor are built.
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Biomes = require(ReplicatedStorage.Shared.Config.Biomes)
local Decor = require(ReplicatedStorage.Shared.Config.Decor)
local Map = require(ReplicatedStorage.Shared.Config.Map)
local Roles = require(ReplicatedStorage.Shared.Roles)

local MapDecor = {}

type PropChoice = { name: string, weight: number, scale: { number } }

local maps = ReplicatedStorage:WaitForChild("Assets"):WaitForChild("Maps")

local function propsOf(biomeId: string): Instance?
	local biome = maps:FindFirstChild(biomeId)
	return biome and biome:FindFirstChild("Props")
end

local ALONG = Vector3.new(0, 0, -1) -- down the corridor

-- Props that have to point a certain way (a lava fall down a wall, an arch across the corridor) carry a
-- tiny "Front" part on their front side in Blender. Where it lies from the pivot shows which way the
-- import left the prop facing, so it can be turned the right way whatever the importer did. The marker
-- itself is removed.
local function frontOf(model: Model): Vector3?
	for _, part in model:GetDescendants() do
		if part:IsA("BasePart") and Roles.of(part) == "Front" then
			local offset = model:GetPivot():PointToObjectSpace(part.Position)
			part:Destroy()
			if Vector2.new(offset.X, offset.Z).Magnitude > 0.01 then
				return Vector3.new(offset.X, 0, offset.Z)
			end
			return nil
		end
	end
	return nil
end

-- A prop in Decor.propLights really lights what's round it, from the parts of its role. Neon alone lights nothing.
local function addLight(model: Model, scale: number)
	local light = Decor.propLights[model.Name]
	if not light then
		return
	end
	for _, part in model:GetDescendants() do
		if part:IsA("BasePart") and Roles.of(part) == light.role then
			local point = Instance.new("PointLight")
			point.Color = light.color
			point.Range = math.min(light.range * scale, 60)
			point.Brightness = light.brightness
			point.Shadows = false
			point.Parent = part
		end
	end
end

-- A copy of a prop standing on `position`, turned `yaw` degrees and scaled. Props nobody can reach
-- aren't solid, which also keeps them out of the physics. A missing prop is skipped with a warning.
-- With `face`, a prop that has a Front marker is first turned so its front points that way.
local function place(parent: Instance, folder: Instance, name: string, position: Vector3, yaw: number, scale: number, solid: boolean, face: Vector3?)
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
	Roles.lightUp(model)
	if scale ~= 1 then
		model:ScaleTo(scale)
	end
	addLight(model, scale)
	local turn = math.rad(yaw)
	local front = frontOf(model)
	if face and front then
		turn += math.atan2(face.X, face.Z) - math.atan2(front.X, front.Z)
	end
	model:PivotTo(CFrame.new(position) * CFrame.Angles(0, turn, 0))
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

	-- Things spanning the corridor overhead, resting on both rims (turned across it, if they say which way is front).
	-- They were modelled for a narrower corridor, so they grow with it to keep their feet on the rims.
	local overheadStretch = Map.platform.width / Map.corridor.overheadBuiltFor
	for _, spot in rules.overhead or {} do
		place(parent, folder, spot.name, Vector3.new(0, Map.walls.rimY, -(biome.startDist + spot.distance)), spot.yaw, spot.scale * overheadStretch, false, ALONG)
	end

	-- Things on a corridor wall's top edge, facing the middle: lava pouring down into the corridor.
	for _, spot in rules.walls or {} do
		local position = Vector3.new(spot.side * wallInside, Map.walls.rimY, -(biome.startDist + spot.distance))
		place(parent, folder, spot.name, position, spot.yaw or 0, spot.scale or 1, false, Vector3.new(-spot.side, 0, 0))
	end

	-- Set pieces at fixed spots: volcanoes on the rims, cracks of lava across the floor. With `face`, a set
	-- piece with a Front marker turns it towards the corridor's middle ("middle") or down it ("along").
	for _, spot in rules.spots or {} do
		local y = if spot.on == "floor" then Map.corridor.floorY else Map.walls.rimY
		local face = if spot.face == "middle" then Vector3.new(-math.sign(spot.x), 0, 0) elseif spot.face == "along" then ALONG else nil
		place(parent, folder, spot.name, Vector3.new(spot.x, y, -(biome.startDist + spot.distance)), spot.yaw, spot.scale, false, face)
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
