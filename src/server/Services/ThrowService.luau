-- Marks the throw lane on the corridor floor and runs each player's throw: aiming -> flying -> aiming again.
-- The client only reports how high the meter marker was when it tapped. The server checks that the tap
-- is allowed and works out the distance itself.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Biomes = require(ReplicatedStorage.Shared.Config.Biomes)
local Hooks = require(ReplicatedStorage.Shared.Config.Hooks)
local Luck = require(ReplicatedStorage.Shared.Config.Luck)
local Reveal = require(ReplicatedStorage.Shared.Config.Reveal)
local Throw = require(ReplicatedStorage.Shared.Config.Throw)
local DinoRoll = require(script.Parent.DinoRoll)
local CompetitionService = require(script.Parent.CompetitionService)
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
	for _, name in { "MeterStart", "MeterCancel", "Tap", "Launched", "Landed", "RevealDone", "LuckyCatch" } do
		local remote = Instance.new("RemoteEvent")
		remote.Name = name
		remote.Parent = folder
		remotes[name] = remote
	end
	folder.Parent = ReplicatedStorage
end

-- Thin lines across the corridor floor every markerSpacing studs and THROW HERE over the platform. The floor
-- itself is MapService's. There are no floating labels down the corridor, as in the reference: the world's name
-- shows in the flight's luck panel instead.
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

	local maxDistance = Throw.maxDistance()
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
	local maxDistance = Throw.maxDistance()
	local distance = math.min(power * Throw.multiplier(height), maxDistance)

	-- The egg in hand when it leaves counts, even if the player swaps mid-flight.
	local egg = EggService.equipped(player)

	state.phase = "flying"
	remotes.Launched:FireAllClients(player, distance, Throw.isPerfect(height), egg.id)

	task.delay(Throw.releaseDelay() + Throw.flightTime(distance), function()
		if states[player] ~= state then
			return
		end
		local data = PlayerData.get(player)
		local indexLuck = if data then IndexService.luckMultiplier(data) else 1
		local boosts = egg.luckBonus * indexLuck * ShopService.luckMultiplier(player)
		local biome = Luck.biomeAt(distance)

		-- Guarantees (Config/Hooks): the first catch in a new biome, or too many throws without a rare one.
		local guarantee, reason = nil, nil
		if data and not IndexService.hasCaughtIn(data, biome.id) then
			guarantee, reason = { minRank = Hooks.newMapGift.minRank }, "newMap"
		elseif data and data.throwsSinceRare + 1 >= Hooks.pity.throws then
			guarantee, reason = { minRank = Hooks.pity.minRank }, "pity"
		end
		-- A lucky throw (bought or from the daily reward) is used up here, when the egg lands. Its x number
		-- only multiplies the luck shown; what it hatches is Config/LuckyOutcomes, and it wins over the above.
		local luckyThrow = if data then ShopService.takeLuckyThrow(player, data) else 1
		local lucky = if luckyThrow > 1 then DinoRoll.luckyGuarantee(luckyThrow) else nil
		if lucky then
			guarantee, reason = lucky, "luckyThrow"
		end

		-- The big number is what players see; the roll counts luck from the biome's start.
		local catch = DinoRoll.rollCatch(biome.id, Luck.inBiome(distance) * boosts, 1, 1, guarantee)
		catch.luck = Luck.at(distance) * boosts * luckyThrow
		catch.guarantee = reason
		if data then
			data.throwsSinceRare = if catch.rank >= Hooks.pity.minRank then 0 else data.throwsSinceRare + 1
			data.farthestThrow = math.max(data.farthestThrow, math.floor(distance))
		end
		CompetitionService.landedIn(player, biome)

		-- Just short of the next biome: the client shows how close it was.
		local nextBiome = Biomes[table.find(Biomes, biome) + 1]
		if nextBiome and nextBiome.startDist - distance <= Hooks.almostThere.studs and distance < Throw.maxDistance() then
			catch.almostThere = { name = nextBiome.name, studs = math.max(math.ceil(nextBiome.startDist - distance), 1) }
		end
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

		-- Lucky catch banner for everyone else in the server. The catcher's own client shows it
		-- after their reveal, from the catch it already has.
		if catch.oneIn >= Reveal.luckyBanner.minOneIn then
			local announcement = {
				player = player.Name,
				id = catch.id,
				name = catch.name,
				size = catch.size,
				mutation = catch.mutation,
				oneIn = catch.oneIn,
			}
			for _, other in Players:GetPlayers() do
				if other ~= player then
					remotes.LuckyCatch:FireClient(other, announcement)
				end
			end
		end
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
