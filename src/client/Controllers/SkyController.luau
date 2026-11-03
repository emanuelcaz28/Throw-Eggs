-- The sky on this player's screen: chunky block clouds drifting slowly around the floating island,
-- and each world's own light while the camera is over it (Config/Lighting clouds and worlds). Both
-- happen on this screen only, so they cost the server and the network nothing.
local Lighting = game:GetService("Lighting")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")

local Biomes = require(ReplicatedStorage.Shared.Config.Biomes)
local LightingConfig = require(ReplicatedStorage.Shared.Config.Lighting)
local Map = require(ReplicatedStorage.Shared.Config.Map)

local SkyController = {}

local FADE_SHARE = 0.1 -- of a cloud's path, at each end

local function between(rng: Random, range: { number }): number
	return rng:NextNumber(range[1], range[2])
end

-- One cloud: a few flat white blocks bunched together, pivoted at its middle.
local function buildCloud(rng: Random, parent: Instance): Model
	local settings = LightingConfig.clouds
	local model = Instance.new("Model")
	model.Name = "Cloud"
	local count = rng:NextInteger(settings.blocks[1], settings.blocks[2])
	for index = 1, count do
		local width = between(rng, settings.blockSize)
		local part = Instance.new("Part")
		part.Name = "Puff"
		part.Anchored = true
		part.CanCollide = false
		part.CanQuery = false
		part.CanTouch = false
		part.CastShadow = false
		part.Material = Enum.Material.SmoothPlastic
		part.Color = settings.color
		part.Transparency = settings.transparency
		part.Size = Vector3.new(width, width * rng:NextNumber(0.3, 0.5), width * rng:NextNumber(0.6, 1))
		-- Puffs spread sideways and the middle ones sit a little higher, like a cumulus.
		local spread = (index - (count + 1) / 2) * width * 0.55
		part.CFrame = CFrame.new(spread, rng:NextNumber(0, 6) + (if math.abs(spread) < width then 6 else 0), rng:NextNumber(-8, 8))
		part.Parent = model
	end
	model.WorldPivot = CFrame.new()
	model.Parent = parent
	return model
end

-- Which world the camera is over. The corridor runs along -Z from the throw line, so anything
-- before it (the arena and the platform) is nil, which uses the main look.
local function worldAt(z: number): string?
	local distance = -z
	if distance <= 0 then
		return nil
	end
	for _, biome in Biomes do
		if distance < biome.endDist then
			return biome.id
		end
	end
	return Biomes[#Biomes].id
end

-- Blends Lighting and the server's atmosphere and colour effects towards the world under the
-- camera. Only properties some world changes are touched; a world without its own look (Fern
-- Valley) gets the main look's values for those.
local function followWorlds()
	local targets = {
		lighting = Lighting,
		atmosphere = Lighting:WaitForChild(LightingConfig.names.atmosphere),
		colorCorrection = Lighting:WaitForChild(LightingConfig.names.colorCorrection),
	}
	local looks = {}
	local function lookFor(worldId: string?)
		local key = worldId or ""
		if not looks[key] then
			local own = LightingConfig.worlds[worldId or ""] or {}
			local look = {}
			for group in targets do
				look[group] = {}
				for _, other in LightingConfig.worlds do
					for property in other[group] or {} do
						local value = own[group] and own[group][property]
						look[group][property] = if value ~= nil then value else LightingConfig[group][property]
					end
				end
			end
			looks[key] = look
		end
		return looks[key]
	end

	local info = TweenInfo.new(LightingConfig.worldBlendSeconds, Enum.EasingStyle.Sine, Enum.EasingDirection.Out)
	local current = false -- nothing applied yet; nil is the main look
	RunService.RenderStepped:Connect(function()
		local world = worldAt(workspace.CurrentCamera.CFrame.Position.Z)
		if LightingConfig.worlds[world or ""] == nil then
			world = nil
		end
		if world == current then
			return
		end
		current = world
		-- A new tween on the same properties replaces the one still running.
		for group, values in lookFor(world) do
			TweenService:Create(targets[group], info, values):Play()
		end
	end)
end

function SkyController.start()
	task.spawn(followWorlds)

	local settings = LightingConfig.clouds
	local rng = Random.new(settings.seed)
	local folder = Instance.new("Folder")
	folder.Name = "Clouds"

	-- Around the middle of the island: halfway between the arena and the far end of the corridor.
	local centre = Vector3.new(0, 0, (Map.arena.backZ - Biomes[#Biomes].endDist) / 2)
	local direction = settings.direction.Unit
	local clouds = {}
	for _ = 1, settings.count do
		local angle = rng:NextNumber(0, 2 * math.pi)
		local radius = between(rng, settings.ringRadius)
		local start = centre + Vector3.new(math.cos(angle) * radius, between(rng, settings.height), math.sin(angle) * radius)
		local cloud = buildCloud(rng, folder)
		table.insert(clouds, {
			model = cloud,
			start = start,
			travelled = rng:NextNumber(0, settings.wrap), -- spread out along their paths from the first frame
			speed = between(rng, settings.speed),
			turn = CFrame.Angles(0, rng:NextNumber(0, 2 * math.pi), 0),
			transparency = settings.transparency,
		})
	end
	folder.Parent = workspace

	RunService.Heartbeat:Connect(function(dt)
		for _, cloud in clouds do
			-- Drift, and when far enough, start over from the other side of the start point.
			cloud.travelled = (cloud.travelled + cloud.speed * dt) % settings.wrap
			local offset = direction * (cloud.travelled - settings.wrap / 2)
			cloud.model:PivotTo(CFrame.new(cloud.start + offset) * cloud.turn)
			-- Fades out at the end of its path and in at the start, so the jump back isn't seen.
			local edge = math.min(cloud.travelled, settings.wrap - cloud.travelled) / (settings.wrap * FADE_SHARE)
			local transparency = 1 - (1 - settings.transparency) * math.clamp(edge, 0, 1)
			if transparency ~= cloud.transparency then
				cloud.transparency = transparency
				for _, puff in cloud.model:GetChildren() do
					(puff :: BasePart).Transparency = transparency
				end
			end
		end
	end)
end

return SkyController
