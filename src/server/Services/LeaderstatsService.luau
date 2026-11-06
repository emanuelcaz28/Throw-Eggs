-- The stats in Roblox's own player list (the one Tab opens): each player's money per second and Throw Power,
-- shortened the way the HUD shows them ($2.3Qi/s, 10,612). They copy the Income and ThrowPower attributes that
-- PlotService and TrainingService already keep up to date. Text values, because the numbers outgrow whole-number
-- values in the later worlds.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Format = require(ReplicatedStorage.Shared.Format)

local LeaderstatsService = {}

local function onPlayerAdded(player: Player)
	local folder = Instance.new("Folder")
	folder.Name = "leaderstats" -- the name Roblox's player list looks for
	local income = Instance.new("StringValue")
	income.Name = "Money/s"
	income.Parent = folder
	local power = Instance.new("StringValue")
	power.Name = "Power"
	power.Parent = folder
	folder.Parent = player

	local function update()
		income.Value = `{Format.cash(player:GetAttribute("Income") or 0)}/s`
		power.Value = Format.commas(player:GetAttribute("ThrowPower") or 0)
	end
	player:GetAttributeChangedSignal("Income"):Connect(update)
	player:GetAttributeChangedSignal("ThrowPower"):Connect(update)
	update()
end

function LeaderstatsService.start()
	Players.PlayerAdded:Connect(onPlayerAdded)
	for _, player in Players:GetPlayers() do
		task.spawn(onPlayerAdded, player)
	end
end

return LeaderstatsService
