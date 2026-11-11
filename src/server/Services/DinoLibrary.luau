-- Monster models load on demand, so a new player's phone doesn't download all of them on joining. The imported models
-- (ReplicatedStorage.Assets.Dinos in Studio, about 17,500 instances) move to ServerStorage.DinoLibrary as the server
-- starts, before anyone joins. Each player then gets a copy of only the models their screen needs, in a hidden
-- ScreenGui in their PlayerGui, which replicates to that player alone: their own monsters on load, each new catch
-- before its reveal, and whatever the client asks for (DinoModel.need: the Index, the Shop, gifts).
-- Creator Analytics 2026-11-10: phones had the worst 30-second retention (86%).
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerStorage = game:GetService("ServerStorage")

local RemoteGuard = require(script.Parent.RemoteGuard)
local DinoModel = require(ReplicatedStorage.Shared.DinoModel)
local PlayerData = require(script.Parent.PlayerData)

local DinoLibrary = {}

local MAX_PER_ASK = 200 -- more than every monster in the game; anything bigger is not a real client

local library: Folder? = nil
local given: { [Player]: { [string]: boolean } } = {}

-- The player's hidden folder of models (DinoModel.TEMPLATE_GUI). ResetOnSpawn off, so respawning keeps it.
local function folderOf(player: Player): ScreenGui?
	local playerGui = player:FindFirstChildOfClass("PlayerGui")
	if not playerGui then
		return nil
	end
	local gui = playerGui:FindFirstChild(DinoModel.TEMPLATE_GUI) :: ScreenGui?
	if not gui then
		gui = Instance.new("ScreenGui")
		gui.Name = DinoModel.TEMPLATE_GUI
		gui.Enabled = false
		gui.ResetOnSpawn = false
		gui.Parent = playerGui
	end
	return gui
end

-- Sends these monsters' models to the player, once each. Unknown ids (block-model monsters) are skipped.
-- spread: one model a frame (yields). Copying a whole Index page's eight at once cost the server ~12 ms in one frame.
function DinoLibrary.give(player: Player, dinoIds: { string }, spread: boolean?)
	if not library then
		return
	end
	local folder = folderOf(player)
	if not folder or not player.Parent then
		return
	end
	local sent = given[player] or {}
	given[player] = sent
	local copied = false
	for _, dinoId in dinoIds do
		if not sent[dinoId] then
			local template = library:FindFirstChild(`dino_{dinoId}`)
			if template and spread and copied then
				task.wait()
				if not player.Parent or not folder.Parent then
					return -- left, or the folder went: what wasn't sent can be asked for again
				end
			end
			if sent[dinoId] then
				continue -- another request sent it while this one waited
			end
			sent[dinoId] = true
			if template then
				template:Clone().Parent = folder
				copied = true
			end
		end
	end
end

-- The client asks for models it's about to show. Returns once they are on their way (instances replicate before the
-- reply arrives).
local function onAsk(player: Player, dinoIds: any): boolean
	if not RemoteGuard.allow(player, "DinoLibraryAsk", 20, 40) or typeof(dinoIds) ~= "table" or #dinoIds > MAX_PER_ASK then
		return false
	end
	local ids = {}
	for _, dinoId in dinoIds do
		if typeof(dinoId) == "string" and #dinoId <= 64 then
			table.insert(ids, dinoId)
		end
	end
	DinoLibrary.give(player, ids, true)
	return true
end

-- Runs first in Main, before any player can join, so nobody receives the whole library.
function DinoLibrary.start()
	local assets = ReplicatedStorage:FindFirstChild("Assets")
	local dinos = assets and assets:FindFirstChild("Dinos")
	if dinos then
		dinos.Name = DinoModel.LIBRARY
		dinos.Parent = ServerStorage
	end
	library = ServerStorage:FindFirstChild(DinoModel.LIBRARY) :: Folder?

	local remote = Instance.new("RemoteFunction")
	remote.Name = DinoModel.ASK_REMOTE
	remote.OnServerInvoke = onAsk
	remote.Parent = ReplicatedStorage

	Players.PlayerRemoving:Connect(function(player)
		given[player] = nil
	end)
	-- The player's own monsters: their base, hotbar and My Dinos show them straight away.
	PlayerData.onLoaded(function(player, data)
		local ids = {}
		for _, entry in data.dinos do
			table.insert(ids, entry.id)
		end
		DinoLibrary.give(player, ids)
	end)
end

return DinoLibrary
