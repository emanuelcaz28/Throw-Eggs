-- Builds the shared SELL stall in the arena. Stalls only open panels on the client; selling still
-- goes through PlotService. Each base's Egg Shop stall is built by its owner's client
-- (EggShopController), so only they see it.
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Hub = require(ReplicatedStorage.Shared.Config.Hub)
local Stall = require(ReplicatedStorage.Shared.Stall)

local HubService = {}

function HubService.start()
	local folder = Instance.new("Folder")
	folder.Name = "Hub"
	Stall.build("SellStall", Hub.sellStall, Hub.stallCFrame(Hub.sellStall)).Parent = folder
	folder.Parent = workspace
end

return HubService
