-- Marks the throw lane on the corridor floor and runs each player's throw: aiming -> flying -> aiming again.
-- The client only reports how high the meter marker was when it tapped. The server checks that the tap
-- is allowed and works out the distance itself.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Biomes = require(ReplicatedStorage.Shared.Config.Biomes)
local Events = require(ReplicatedStorage.Shared.Config.Events)
local Luck = require(ReplicatedStorage.Shared.Config.Luck)
local Reveal = require(ReplicatedStorage.Shared.Config.Reveal)
local Throw = require(ReplicatedStorage.Shared.Config.Throw)
local DinoRoll = require(script.Parent.DinoRoll)
local EggService = require(script.Parent.EggService)
local IndexService = require(script.Parent.IndexService)
local PlayerData = require(script.Parent.PlayerData)
local PlotService = require(script.Parent.PlotService)
local ShopService = require(script.Parent.ShopService)
local TrainingService = require(script.Parent.TrainingService)
local World = require(ReplicatedStorage.Shared.World)

local ThrowService = {}

local TICK = 0.1
local MARKER_COLOR = Color3.new(1, 1, 1)
local MARKER_LIFT = 0.05 -- just above the corridor floor, so the two don't flicker

type ThrowState = { phase: "idle" | "aiming" | "flying" | "revealing", aimStartedAt: number, revealStartedAt: number }

local states: { [Player]: ThrowState } = {}
local remotes: { [string]: RemoteEvent } = {}

local function makeRemotes()
	local folder = Instance.new("Folder")
	folder.Name = "ThrowRemotes"
	for _, name in { "MeterStart", "MeterCancel", "Tap", "Launched", "Landed", "RevealDone" } do
		local remote = Instance.new("RemoteEvent")
		remote.Name = name
		remote.Parent = folder
		remotes[name] = remote
	end
	folder.Parent = ReplicatedStorage
end

-- Thin lines across the corridor floor every markerSpacing studs, a sign at each biome's start
-- and THROW HERE over the platform. The floor itself is MapService's.
local function buildLane()
	local lane = Throw.lane
	local model = Instance.new("Model")
	model.Name = "ThrowLane"
	-- The lane runs far from the player. Without this, Roblox may not send distant
	-- parts to the client.
	model.ModelStreamingMode = Enum.ModelStreamingMode.Persistent

	local function floorPoint(distance: number): Vector3
		local point = lane.origin + lane.direction * distance
		return Vector3.new(point.X, lane.floorY, point.Z)
	end

	for _, biome in Biomes do
		local entrance = World.makePart(
			model,
			"BiomeSign",
			Vector3.new(1, 1, 1),
			CFrame.new(floorPoint(biome.startDist) + Vector3.new(0, 12, 0)),
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
			CFrame.new(floorPoint(distance) + Vector3.new(0, MARKER_LIFT, 0)),
			MARKER_COLOR
		)
		marker.CanCollide = false
		marker.Material = Enum.Material.SmoothPlastic
		marker.Transparency = 0.4
		World.makeSign(marker, `{distance}`, 3, 200, 120)
	end

	local signAnchor = World.makePart(model, "ThrowSign", Vector3.one, CFrame.new(lane.zoneCenter + Vector3.new(0, 10, 0)), MARKER_COLOR)
	signAnchor.Transparency = 1
	signAnchor.CanCollide = false
	World.makeSign(signAnchor, "THROW HERE", 0, 150, 220)

	model.Parent = workspace
end

local function isOnPad(player: Player): boolean
	local character = player.Character
	local root = character and character:FindFirstChild("HumanoidRootPart") :: BasePart?
	local humanoid = character and character:FindFirstChildOfClass("Humanoid")
	return root ~= nil and humanoid ~= nil and humanoid.Health > 0 and Throw.onPlatform(root.Position)
end

local function onTap(player: Player, height: any)
	local state = states[player]
	if not state or state.phase ~= "aiming" then
		return
	end
	-- height ~= height is only true for NaN.
	if typeof(height) ~= "number" or height ~= height then
		return
	end
	if os.clock() - state.aimStartedAt < Throw.meter.minTime or not isOnPad(player) then
		return
	end
	local power = TrainingService.getThrowPower(player)
	if not power then
		return
	end

	height = math.clamp(height, 0, 1)
	local maxDistance = Biomes[#Biomes].endDist
	local distance = math.min(power * Throw.multiplier(height), maxDistance)

	-- The egg in hand when it leaves counts, even if the player swaps mid-flight.
	local egg = EggService.equipped(player)

	state.phase = "flying"
	remotes.Launched:FireAllClients(player, distance, Throw.isPerfect(height), egg.id)

	task.delay(Throw.flightTime(distance), function()
		if states[player] ~= state then
			return
		end
		local data = PlayerData.get(player)
		local indexLuck = if data then IndexService.luckMultiplier(data) else 1
		local luck = Luck.at(distance) * egg.luckBonus * indexLuck * ShopService.serverLuckMultiplier() * Events.multiplier("luck")
		local biome = Luck.biomeAt(distance)
		local catch = DinoRoll.rollCatch(biome.id, luck, Events.multiplier("mutationChance"), Events.multiplier("sizeChance"))
		catch.luck = luck
		catch.newBest = data ~= nil and catch.income > data.bestIncome
		if catch.newBest then
			data.bestIncome = catch.income
		end
		if data then
			data.totalCaught += 1
			data.rarestOneIn = math.max(data.rarestOneIn, catch.oneIn)
		end
		catch.isNew, catch.completedBiome = IndexService.discover(player, catch.id, biome)
		catch.storedIn = PlotService.addCatch(player, catch)

		state.phase = "revealing"
		state.revealStartedAt = os.clock()
		remotes.Landed:FireClient(player, catch)
	end)
end

local function onRevealDone(player: Player)
	local state = states[player]
	if not state or state.phase ~= "revealing" then
		return
	end
	local remaining = Reveal.minTime - (os.clock() - state.revealStartedAt)
	task.delay(math.max(remaining, 0), function()
		if states[player] == state and state.phase == "revealing" then
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
	states[player] = { phase = "idle", aimStartedAt = 0, revealStartedAt = 0 }
end

function ThrowService.start()
	makeRemotes()
	buildLane()

	remotes.Tap.OnServerEvent:Connect(onTap)
	remotes.RevealDone.OnServerEvent:Connect(onRevealDone)
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
