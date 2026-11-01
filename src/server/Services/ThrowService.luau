-- Builds the throw lane and runs each player's throw: aiming -> flying -> aiming again.
-- The client only reports how accurate its tap was. The server checks that the tap
-- is allowed and works out the distance itself.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Biomes = require(ReplicatedStorage.Shared.Config.Biomes)
local Throw = require(ReplicatedStorage.Shared.Config.Throw)
local TrainingService = require(script.Parent.TrainingService)
local World = require(script.Parent.World)

local ThrowService = {}

local TICK = 0.1
local GROUND_THICKNESS = 1
local GROUND_TOP = 0.1 -- just above the baseplate, so the two don't flicker
local PAD_COLOR = Color3.fromRGB(70, 170, 220)
local MARKER_COLOR = Color3.new(1, 1, 1)

type ThrowState = { phase: "idle" | "aiming" | "flying", aimStartedAt: number }

local states: { [Player]: ThrowState } = {}
local remotes: { [string]: RemoteEvent } = {}

local function makeRemotes()
	local folder = Instance.new("Folder")
	folder.Name = "ThrowRemotes"
	for _, name in { "MeterStart", "MeterCancel", "Tap", "Launched" } do
		local remote = Instance.new("RemoteEvent")
		remote.Name = name
		remote.Parent = folder
		remotes[name] = remote
	end
	folder.Parent = ReplicatedStorage
end

local function buildLane()
	local lane = Throw.lane
	local model = Instance.new("Model")
	model.Name = "ThrowLane"
	-- The lane runs far from the player. Without this, Roblox may not send distant
	-- parts to the client and the egg would fly over nothing.
	model.ModelStreamingMode = Enum.ModelStreamingMode.Persistent

	local function groundPoint(distance: number): Vector3
		return lane.origin + lane.direction * distance + Vector3.new(0, GROUND_TOP, 0)
	end

	for _, biome in Biomes do
		local length = biome.endDist - biome.startDist
		local middle = groundPoint((biome.startDist + biome.endDist) / 2)
		local ground = World.makePart(
			model,
			biome.id,
			Vector3.new(lane.width, GROUND_THICKNESS, length),
			CFrame.new(middle - Vector3.new(0, GROUND_THICKNESS / 2, 0)),
			biome.color
		)
		ground.Material = Enum.Material.Grass

		local entrance = World.makePart(
			model,
			"BiomeSign",
			Vector3.new(1, 1, 1),
			CFrame.new(groundPoint(biome.startDist) + Vector3.new(0, 12, 0)),
			biome.color
		)
		entrance.Transparency = 1
		entrance.CanCollide = false
		World.makeSign(entrance, biome.name, 0, 600, 320)
	end

	local maxDistance = Biomes[#Biomes].endDist
	for distance = lane.markerSpacing, maxDistance, lane.markerSpacing do
		local marker = World.makePart(
			model,
			"Marker",
			Vector3.new(lane.width, 0.1, 1),
			CFrame.new(groundPoint(distance) + Vector3.new(0, 0.05, 0)),
			MARKER_COLOR
		)
		marker.CanCollide = false
		marker.Material = Enum.Material.SmoothPlastic
		World.makeSign(marker, `{distance}`, 3, 200, 120)
	end

	local pad = World.makePad(model, lane.padPosition, lane.padRadius, PAD_COLOR)
	World.makeSign(pad, "THROW HERE", 8, 150, 220)

	model.Parent = workspace
end

local function isOnPad(player: Player): boolean
	local lane = Throw.lane
	return World.isOnPad(player, lane.padPosition, lane.padRadius, lane.padHeight)
end

local function onTap(player: Player, accuracy: any)
	local state = states[player]
	if not state or state.phase ~= "aiming" then
		return
	end
	-- accuracy ~= accuracy is only true for NaN.
	if typeof(accuracy) ~= "number" or accuracy ~= accuracy then
		return
	end
	if os.clock() - state.aimStartedAt < Throw.meter.minTime or not isOnPad(player) then
		return
	end
	local power = TrainingService.getThrowPower(player)
	if not power then
		return
	end

	accuracy = math.clamp(accuracy, 0, 1)
	local maxDistance = Biomes[#Biomes].endDist
	local distance = math.min(power * Throw.multiplier(accuracy), maxDistance)

	state.phase = "flying"
	remotes.Launched:FireAllClients(player, distance, Throw.isPerfect(accuracy))

	task.delay(Throw.flightTime(distance) + Throw.flight.landingPause, function()
		-- The roll for what hatches (MVP step 3) happens on landing.
		if states[player] == state then
			state.phase = "idle"
		end
	end)
end

local function step()
	for player, state in states do
		local onPad = isOnPad(player)
		if state.phase == "idle" and onPad and TrainingService.getThrowPower(player) then
			state.phase = "aiming"
			state.aimStartedAt = os.clock()
			remotes.MeterStart:FireClient(player)
		elseif state.phase == "aiming" and not onPad then
			state.phase = "idle"
			remotes.MeterCancel:FireClient(player)
		end
	end
end

local function addPlayer(player: Player)
	states[player] = { phase = "idle", aimStartedAt = 0 }
end

function ThrowService.start()
	makeRemotes()
	buildLane()

	remotes.Tap.OnServerEvent:Connect(onTap)
	Players.PlayerAdded:Connect(addPlayer)
	Players.PlayerRemoving:Connect(function(player)
		states[player] = nil
	end)
	for _, player in Players:GetPlayers() do
		addPlayer(player)
	end

	task.spawn(function()
		while true do
			task.wait(TICK)
			step()
		end
	end)
end

return ThrowService
