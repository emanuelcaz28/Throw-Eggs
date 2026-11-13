-- Filming mode for TikTok clips, Studio only (Config/Filming). The FILM panel (FilmingController) picks a monster, size
-- and colour; every throw then lands in that monster's map and catches exactly it, through the real reveal, until the
-- pick is cleared. The save is a copy that is never written (PlayerData), so nothing caught here is kept.
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local Biomes = require(ReplicatedStorage.Shared.Config.Biomes)
local Catch = require(ReplicatedStorage.Shared.Config.Catch)
local Dinos = require(ReplicatedStorage.Shared.Config.Dinos)
local Filming = require(ReplicatedStorage.Shared.Config.Filming)
local Tutorial = require(ReplicatedStorage.Shared.Config.Tutorial)
local DinoStats = require(ReplicatedStorage.Shared.DinoStats)
local RemoteGuard = require(script.Parent.RemoteGuard)
local PlayerData = require(script.Parent.PlayerData)

local FilmingService = {}

export type Pick = { biome: string, rank: number, size: string?, mutation: string?, distance: number }

local picks: { [Player]: Pick } = {}

function FilmingService.active(): boolean
	return RunService:IsStudio() and workspace:GetAttribute(Filming.attribute) == true
end

-- The player's pick, or nil for a normal throw.
function FilmingService.pick(player: Player): Pick?
	if not FilmingService.active() then
		return nil
	end
	return picks[player]
end

local function biomeById(id: any)
	for _, biome in Biomes do
		if biome.id == id and not biome.hidden and not biome.rollFrom then
			return biome
		end
	end
	return nil
end

local function onPick(player: Player, request: any)
	if typeof(request) ~= "table" then
		picks[player] = nil
		player:SetAttribute("FilmingPick", nil)
		return
	end
	local biome = biomeById(request.biome)
	local dinos = biome and Dinos[biome.id]
	local rank = request.rank
	if not dinos or typeof(rank) ~= "number" or rank % 1 ~= 0 or not dinos[rank] then
		return
	end
	local size = if typeof(request.size) == "string" and DinoStats.findOption(Catch.sizes, request.size) then request.size else nil
	local mutation = if typeof(request.mutation) == "string" and DinoStats.findOption(Catch.mutations, request.mutation)
		then request.mutation
		else nil
	picks[player] = {
		biome = biome.id,
		rank = rank,
		size = size,
		mutation = mutation,
		distance = biome.startDist + (biome.endDist - biome.startDist) * Filming.landAt,
	}
	player:SetAttribute("FilmingPick", dinos[rank].name)
end

function FilmingService.start()
	if not FilmingService.active() then
		return
	end
	warn("[FilmingService] Filming mode is ON (Workspace StudioFilming): nothing is saved, throws catch the FILM pick")
	local folder = Instance.new("Folder")
	folder.Name = "FilmingRemotes"
	local remote = Instance.new("RemoteEvent")
	remote.Name = "Pick"
	remote.Parent = folder
	folder.Parent = ReplicatedStorage
	RemoteGuard.connect(remote, onPick)
	game:GetService("Players").PlayerRemoving:Connect(function(player)
		picks[player] = nil
	end)
	-- No tutorial while filming: its arrow and hidden HUD would get in the shot.
	PlayerData.onLoaded(function(player: Player, data)
		if typeof(data.tutorial) == "table" and (data.tutorial.step or 0) < Tutorial.doneStep then
			data.tutorial.step = Tutorial.doneStep
			data.tutorial.throws = 2
			player:SetAttribute("TutorialStep", Tutorial.doneStep)
		end
	end)
end

return FilmingService
