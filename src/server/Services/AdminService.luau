-- Admin tools for testing (Config/Admin): play as a brand-new player on a throwaway save, go back to the real save,
-- finish the tutorial, and add cash to a throwaway save. Only admins can ask (AdminRemotes.Action); everything is
-- checked here. A throwaway save is never written (PlayerData.wantsFreshSave, set here), so the real save is safe.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local TeleportService = game:GetService("TeleportService")

local Admin = require(ReplicatedStorage.Shared.Config.Admin)
local Tutorial = require(ReplicatedStorage.Shared.Config.Tutorial)
local PlayerData = require(script.Parent.PlayerData)

local AdminService = {}

local FRESH_KEY = "adminFreshSave" -- in the teleport data that brings an admin back on a throwaway save

function AdminService.isAdmin(player: Player): boolean
	if game.CreatorType == Enum.CreatorType.User and player.UserId == game.CreatorId then
		return true
	end
	return table.find(Admin.userIds, player.UserId) ~= nil
end

-- True when an admin joined through "Play as new player": PlayerData then gives a throwaway save.
function AdminService.joinedFresh(player: Player): boolean
	local ok, joinData = pcall(player.GetJoinData, player)
	local teleportData = ok and joinData and joinData.TeleportData
	return AdminService.isAdmin(player) and typeof(teleportData) == "table" and teleportData[FRESH_KEY] == true
end

local remote: RemoteEvent

local function tell(player: Player, text: string)
	remote:FireClient(player, "message", text)
end

-- Rejoins this game, on a throwaway save or back on the real one.
local function rejoin(player: Player, fresh: boolean)
	if RunService:IsStudio() then
		tell(player, if fresh
			then "In Studio: stop, tick StudioFreshSave on Workspace, then Play"
			else "In Studio: stop, untick StudioFreshSave on Workspace, then Play")
		return
	end
	tell(player, "Rejoining...")
	local options = Instance.new("TeleportOptions")
	options:SetTeleportData({ [FRESH_KEY] = fresh })
	local ok, err = pcall(TeleportService.TeleportAsync, TeleportService, game.PlaceId, { player }, options)
	if not ok then
		tell(player, `Rejoin failed: {err}`)
	end
end

local function onAction(player: Player, action: any)
	if not AdminService.isAdmin(player) then
		return
	end
	local data = PlayerData.get(player)
	if not data then
		return
	end
	if action == "fresh" then
		rejoin(player, true)
	elseif action == "real" then
		rejoin(player, false)
	elseif action == "finishTutorial" then
		if typeof(data.tutorial) == "table" then
			data.tutorial.step = Tutorial.doneStep
			data.tutorial.throws = 2
			player:SetAttribute("TutorialStep", Tutorial.doneStep)
		end
		tell(player, "Tutorial finished")
	elseif action == "cash" then
		if not PlayerData.isTestSave(player) then
			tell(player, "Cash only works on a throwaway save")
			return
		end
		data.cash += Admin.testCash
		player:SetAttribute("Cash", data.cash)
		tell(player, "Added cash")
	end
end

function AdminService.start()
	local folder = Instance.new("Folder")
	folder.Name = "AdminRemotes"
	remote = Instance.new("RemoteEvent")
	remote.Name = "Action"
	remote.Parent = folder
	folder.Parent = ReplicatedStorage
	remote.OnServerEvent:Connect(onAction)
	PlayerData.wantsFreshSave = AdminService.joinedFresh
	PlayerData.onLoaded(function(player: Player)
		if AdminService.isAdmin(player) then
			player:SetAttribute("IsAdmin", true)
			player:SetAttribute("AdminTestSave", PlayerData.isTestSave(player))
		end
	end)
end

return AdminService
