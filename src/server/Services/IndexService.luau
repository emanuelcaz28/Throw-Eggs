-- The Dino Index: which dinos a player has ever caught, and the timed XP boost for completing a world.
local ReplicatedStorage = game:GetService("ReplicatedStorage")

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

-- Whether the player has ever caught anything from this biome (the new-map gift, Config/Hooks).
function IndexService.hasCaughtIn(data, biomeId: string): boolean
	for _, dino in Dinos[biomeId] or {} do
		if data.discovered[dino.id] then
			return true
		end
	end
	return false
end

local function publish(player: Player, data)
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
	if not biomeComplete(data, biome.id) then
		return true, nil
	end
	-- The world's x2 XP (Config/Index xpBoost), added to any that's still running.
	data.xpBoostEndsAt = math.max(data.xpBoostEndsAt, os.time()) + Index.xpBoost.seconds
	IndexService.publishXpBoost(player, data)
	return true, biome.name
end

-- Training XP multiplier from completing a world, while it runs.
function IndexService.xpMultiplier(data): number
	return if os.time() < data.xpBoostEndsAt then Index.xpBoost.multiplier else 1
end

-- XpBoostEndsAt on the player, in server time (workspace:GetServerTimeNow), so the client can count it down.
function IndexService.publishXpBoost(player: Player, data)
	local left = data.xpBoostEndsAt - os.time()
	player:SetAttribute("XpBoostEndsAt", if left > 0 then workspace:GetServerTimeNow() + left else nil)
end

local function onLoaded(player: Player, data)
	-- Saves from before the Index existed: count the dinos they already own.
	for _, entry in data.dinos do
		data.discovered[entry.id] = true
	end
	publish(player, data)
	IndexService.publishXpBoost(player, data)
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
