-- The Dino Index: which dinos a player has ever caught, and the permanent bonuses for
-- completing a biome. Bonuses are worked out from the saved list, so changing the
-- numbers in Config/Index also applies to existing players.
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Biomes = require(ReplicatedStorage.Shared.Config.Biomes)
local Dinos = require(ReplicatedStorage.Shared.Config.Dinos)
local Index = require(ReplicatedStorage.Shared.Config.Index)
local PlayerData = require(script.Parent.PlayerData)

local IndexService = {}

local changedRemote: RemoteEvent

local function biomeComplete(data, biomeId: string): boolean
	local dinos = Dinos[biomeId]
	if not dinos or #dinos == 0 then
		return false -- a world whose monsters aren't made yet can't be completed
	end
	for _, dino in dinos do
		if not data.discovered[dino.id] then
			return false
		end
	end
	return true
end

local function completedCount(data): number
	local count = 0
	for _, biome in Biomes do
		if biomeComplete(data, biome.id) then
			count += 1
		end
	end
	return count
end

function IndexService.cashMultiplier(data): number
	return 1 + completedCount(data) * Index.cashBonusPerBiome
end

function IndexService.luckMultiplier(data): number
	return 1 + completedCount(data) * Index.luckBonusPerBiome
end

local function publish(player: Player, data)
	player:SetAttribute("IndexLuck", IndexService.luckMultiplier(data))
	changedRemote:FireClient(player, data.discovered)
end

-- Records a catch. Returns whether it's new, and the name of the biome it completed, if any.
function IndexService.discover(player: Player, dinoId: string, biome): (boolean, string?)
	local data = PlayerData.get(player)
	if not data or data.discovered[dinoId] then
		return false, nil
	end
	data.discovered[dinoId] = true
	publish(player, data)
	return true, if biomeComplete(data, biome.id) then biome.name else nil
end

local function onLoaded(player: Player, data)
	-- Saves from before the Index existed: count the dinos they already own.
	for _, entry in data.dinos do
		data.discovered[entry.id] = true
	end
	publish(player, data)
end

function IndexService.start()
	local folder = Instance.new("Folder")
	folder.Name = "IndexRemotes"
	changedRemote = Instance.new("RemoteEvent")
	changedRemote.Name = "IndexChanged"
	changedRemote.Parent = folder
	folder.Parent = ReplicatedStorage
	PlayerData.onLoaded(onLoaded)
end

return IndexService
