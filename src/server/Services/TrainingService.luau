-- Builds the training station and gives reps to anyone standing on its pad.
-- Everything is decided here on the server; the client only reads the Player
-- attributes set below (ThrowPower, TrainingLevel, TrainingXp, TrainingXpNeeded, IsTraining).
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Training = require(ReplicatedStorage.Shared.Config.Training)
local PlayerData = require(script.Parent.PlayerData)
local World = require(script.Parent.World)

local TrainingService = {}

local TICK = 0.25
local BAR_HEIGHT = 9
local BAR_WIDTH = 8

local PAD_COLOR = Color3.fromRGB(226, 142, 58)
local FRAME_COLOR = Color3.fromRGB(70, 74, 82)

local repProgress: { [Player]: number } = {}

local function buildStation()
	local station = Training.station
	local origin = station.position

	local model = Instance.new("Model")
	model.Name = "TrainingStation"

	local pad = World.makePad(model, origin, station.padRadius, PAD_COLOR)

	for _, side in { -1, 1 } do
		World.makePart(
			model,
			"Post",
			Vector3.new(1, BAR_HEIGHT, 1),
			CFrame.new(origin + Vector3.new(side * BAR_WIDTH / 2, BAR_HEIGHT / 2, 0)),
			FRAME_COLOR
		)
	end
	local bar = World.makePart(
		model,
		"Bar",
		Vector3.new(BAR_WIDTH, 0.5, 0.5),
		CFrame.new(origin + Vector3.new(0, BAR_HEIGHT, 0)),
		FRAME_COLOR
	)
	bar.Material = Enum.Material.Metal
	World.makeSign(bar, "TRAIN HERE", 3, 150, 220)

	model.PrimaryPart = pad
	model.Parent = workspace
end

local function isOnPad(player: Player): boolean
	local station = Training.station
	return World.isOnPad(player, station.position, station.padRadius, station.padHeight)
end

local function publish(player: Player, data: { [string]: any })
	player:SetAttribute("ThrowPower", Training.powerForLevel(data.trainingLevel))
	player:SetAttribute("TrainingLevel", data.trainingLevel)
	player:SetAttribute("TrainingXp", data.trainingXp)
	player:SetAttribute("TrainingXpNeeded", Training.xpToNextLevel(data.trainingLevel))
end

local function addRep(data: { [string]: any })
	data.trainingXp += Training.xpPerRep
	while data.trainingXp >= Training.xpToNextLevel(data.trainingLevel) do
		data.trainingXp -= Training.xpToNextLevel(data.trainingLevel)
		data.trainingLevel += 1
	end
end

local function step(dt: number)
	for _, player in Players:GetPlayers() do
		local data = PlayerData.get(player)
		if data then
			local training = isOnPad(player)
			player:SetAttribute("IsTraining", training)
			if training then
				local progress = (repProgress[player] or 0) + dt
				local reps = math.floor(progress / Training.repInterval)
				repProgress[player] = progress - reps * Training.repInterval
				if reps > 0 then
					for _ = 1, reps do
						addRep(data)
					end
					publish(player, data)
				end
			end
		end
	end
end

-- The server's copy of a player's Throw Power, for the throw system to use.
function TrainingService.getThrowPower(player: Player): number?
	local data = PlayerData.get(player)
	return data and Training.powerForLevel(data.trainingLevel)
end

function TrainingService.start()
	buildStation()
	PlayerData.onLoaded(publish)
	Players.PlayerRemoving:Connect(function(player)
		repProgress[player] = nil
	end)
	task.spawn(function()
		while true do
			step(task.wait(TICK))
		end
	end)
end

return TrainingService
