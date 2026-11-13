-- The Dino Index: which dinos a player has ever caught, and the timed XP boost for completing a world, which the
-- player collects by hand in the Index [Owner, 2026-11-11] (the 2x TRAINING XP button, IndexController).
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Biomes = require(ReplicatedStorage.Shared.Config.Biomes)
local Dinos = require(ReplicatedStorage.Shared.Config.Dinos)
local Index = require(ReplicatedStorage.Shared.Config.Index)
local PlayerData = require(script.Parent.PlayerData)
local RemoteGuard = require(script.Parent.RemoteGuard)

local IndexService = {}

local changedRemote: RemoteEvent
local claimRemote: RemoteEvent

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

-- The client gets what's been found and which worlds' rewards have been collected.
local function publish(player: Player, data)
	changedRemote:FireClient(player, data.discovered, data.indexClaimed)
end

-- Records a catch. Returns whether it's new, and the name of the biome it completed, if any.
function IndexService.discover(player: Player, dinoId: string, biome): (boolean, string?)
	local data = PlayerData.get(player)
	if not data or data.discovered[dinoId] then
		return false, nil
	end
	data.discovered[dinoId] = true
	publish(player, data)
	-- A completed world's x2 XP isn't given here: it waits in the Index until the player collects it (claim below).
	if not biomeComplete(data, biome.id) or data.indexClaimed[biome.id] then
		return true, nil
	end
	return true, biome.name
end

-- The player pressed a completed world's reward button: its cash bonus counts from now on (cashMultiplier; the base's
-- $/s follows within a second, PlotService), and its XP boost (Config/Index xpBoost) starts, added to any that's
-- still running. Once per world.
local function claim(player: Player, biomeId: unknown)
	local data = PlayerData.get(player)
	if not data or typeof(biomeId) ~= "string" or data.indexClaimed[biomeId] or not biomeComplete(data, biomeId) then
		return
	end
	local isWorld = false -- Dinos has lists that aren't a world's own (The Deep End's pool): only real worlds pay
	for _, biome in Biomes do
		isWorld = isWorld or biome.id == biomeId
	end
	if not isWorld then
		return
	end
	data.indexClaimed[biomeId] = true
	data.xpBoostEndsAt = math.max(data.xpBoostEndsAt, os.time()) + Index.xpBoost.seconds
	IndexService.publishXpBoost(player, data)
	publish(player, data)
end

-- What collected worlds multiply the base's $/s by, for good (Config/Index cashBonus): 1 with none, 1.1 with one...
-- A world counts while its reward is collected and every one of its monsters is still in the Index.
function IndexService.cashMultiplier(data): number
	local worlds = 0
	for _, biome in Biomes do
		if data.indexClaimed[biome.id] and biomeComplete(data, biome.id) then
			worlds += 1
		end
	end
	return 1 + Index.cashBonus.perWorld * worlds
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
	-- Saves from before rewards were collected by hand: the worlds they had already completed gave their boost then.
	if not data.indexClaimsStarted then
		data.indexClaimsStarted = true
		for _, biome in Biomes do
			if biomeComplete(data, biome.id) then
				data.indexClaimed[biome.id] = true
			end
		end
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
	claimRemote = Instance.new("RemoteEvent")
	claimRemote.Name = "Claim"
	claimRemote.Parent = folder
	RemoteGuard.connect(claimRemote, claim, 3, 6)
	folder.Parent = ReplicatedStorage
	PlayerData.onLoaded(onLoaded)
end

return IndexService
