-- The Egg Shop: which eggs a player owns and which one they throw. The client can only
-- ask to buy or equip; the price, cash and ownership are all checked here.
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local DinoStats = require(ReplicatedStorage.Shared.DinoStats)
local Eggs = require(ReplicatedStorage.Shared.Config.Eggs)
local RemoteGuard = require(script.Parent.RemoteGuard)
local PlayerData = require(script.Parent.PlayerData)

local EggService = {}

local remotes: { [string]: RemoteEvent } = {}

local function makeRemotes()
	local folder = Instance.new("Folder")
	folder.Name = "EggRemotes"
	for _, name in { "EggAction", "EggsChanged" } do
		local remote = Instance.new("RemoteEvent")
		remote.Name = name
		remote.Parent = folder
		remotes[name] = remote
	end
	folder.Parent = ReplicatedStorage
end

local function publish(player: Player, data)
	remotes.EggsChanged:FireClient(player, data.ownedEggs, data.equippedEgg)
end

local function onAction(player: Player, action: any, eggId: any)
	local data = PlayerData.get(player)
	local egg = DinoStats.findOption(Eggs, eggId)
	if not data or not egg then
		return
	end

	if action == "buy" then
		if data.ownedEggs[egg.id] or data.cash < egg.price then
			return
		end
		data.cash -= egg.price
		data.ownedEggs[egg.id] = true
		data.equippedEgg = egg.id
		player:SetAttribute("Cash", data.cash)
		publish(player, data)
	elseif action == "equip" then
		if data.ownedEggs[egg.id] then
			data.equippedEgg = egg.id
			publish(player, data)
		end
	end
end

-- The egg this player is throwing right now.
function EggService.equipped(player: Player)
	local data = PlayerData.get(player)
	return data and DinoStats.findOption(Eggs, data.equippedEgg) or Eggs[1]
end

function EggService.start()
	makeRemotes()
	RemoteGuard.connect(remotes.EggAction, onAction)
	PlayerData.onLoaded(publish)
end

return EggService
