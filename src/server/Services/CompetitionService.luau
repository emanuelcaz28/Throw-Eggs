-- Competition inside a server (Config/Competition): every few seconds players are ranked by $/s (the
-- Income attribute PlotService keeps). #1 wears a crown, and the top three bases glow in their medal's
-- colour with the medal on the owner plate. Clients draw the ranking list themselves from the same
-- attribute. Also announces the first player in this server to land an egg in each world.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Biomes = require(ReplicatedStorage.Shared.Config.Biomes)
local Competition = require(ReplicatedStorage.Shared.Config.Competition)

local CompetitionService = {}

local worldFirstRemote: RemoteEvent
local farthestWorld = 1 -- the farthest world anyone in this server has landed in

local function plotModel(player: Player): Model?
	local index = player:GetAttribute("PlotIndex")
	local plots = workspace:FindFirstChild("Plots")
	return index and plots and plots:FindFirstChild(`Plot{index}`) :: Model?
end

local function buildCrown(head: BasePart): Model
	local settings = Competition.crown
	local crown = Instance.new("Model")
	crown.Name = "RankCrown"
	local function piece(size: Vector3, offset: CFrame, color: Color3, shape: Enum.PartType?)
		local part = Instance.new("Part")
		part.Size = size
		part.Color = color
		-- Shiny metal, not Neon: with the game's bloom a Neon crown glowed into a big yellow blob, worst on a phone.
		part.Material = Enum.Material.Foil
		part.Reflectance = 0.15
		part.CanCollide = false
		part.CanQuery = false
		part.CanTouch = false
		part.Massless = true
		if shape then
			part.Shape = shape
		end
		part.CFrame = head.CFrame * CFrame.new(0, head.Size.Y / 2 + settings.lift, 0) * offset
		local weld = Instance.new("WeldConstraint")
		weld.Part0 = head
		weld.Part1 = part
		weld.Parent = part
		part.Parent = crown
		return part
	end
	-- A band of four sides with a spike on each corner and a gem at the front. Sized to the head, but never past
	-- a big avatar's head size, which made a giant crown.
	local width = math.clamp(head.Size.X * 1.05, 1, 2.4)
	for side = 0, 3 do
		local turn = CFrame.Angles(0, side * math.pi / 2, 0)
		piece(Vector3.new(width, 0.45, 0.15), turn * CFrame.new(0, 0, -width / 2), settings.color)
		piece(Vector3.new(0.3, 0.6, 0.3), turn * CFrame.new(width / 2, 0.5, -width / 2) * CFrame.Angles(0, math.pi / 4, 0), settings.color)
	end
	local gem = piece(Vector3.new(0.35, 0.35, 0.35), CFrame.new(0, 0, -width / 2 - 0.12), settings.gem, Enum.PartType.Ball)
	-- A soft gold light round it does the glowing instead.
	local light = Instance.new("PointLight")
	light.Color = settings.color
	light.Brightness = 1.2
	light.Range = 6
	light.Parent = gem
	crown.Parent = head.Parent
	return crown
end

local function setCrown(player: Player, wear: boolean)
	local character = player.Character
	local head = character and character:FindFirstChild("Head") :: BasePart?
	if not head then
		return
	end
	local current = character:FindFirstChild("RankCrown")
	if wear and not current then
		buildCrown(head)
	elseif not wear and current then
		current:Destroy()
	end
end

-- The medal glow round the base's fence and the medal on the owner plate (nil clears both).
local function setBaseMedal(player: Player, medal)
	local model = plotModel(player)
	if not model then
		return
	end
	local fence = model:FindFirstChild("Fence")
	local glow = fence and fence:FindFirstChild("RankGlow") :: Highlight?
	if medal and fence then
		if not glow then
			glow = Instance.new("Highlight")
			glow.Name = "RankGlow"
			glow.FillTransparency = 0.75
			glow.OutlineTransparency = 0
			glow.DepthMode = Enum.HighlightDepthMode.Occluded
			glow.Parent = fence
		end
		glow.FillColor = medal.color
		glow.OutlineColor = medal.color
	elseif glow then
		glow:Destroy()
	end
	local anchor = model:FindFirstChild("OwnerPlateAnchor")
	local plate = anchor and anchor:FindFirstChild("OwnerPlate")
	local rank = plate and plate:FindFirstChild("Rank") :: TextLabel?
	if rank then
		rank.Visible = medal ~= nil
		if medal then
			rank.Text = medal.label
			rank.TextColor3 = medal.color
		end
	end
end

local function rankPlayers()
	local ranked = {}
	for _, player in Players:GetPlayers() do
		if (player:GetAttribute("Income") or 0) > 0 then
			table.insert(ranked, player)
		end
	end
	table.sort(ranked, function(a, b)
		return a:GetAttribute("Income") > b:GetAttribute("Income")
	end)
	local placeOf = {}
	for place, player in ranked do
		placeOf[player] = place
	end
	for _, player in Players:GetPlayers() do
		local place = placeOf[player]
		player:SetAttribute("ServerRank", place)
		setCrown(player, place == 1)
		setBaseMedal(player, place and Competition.medals[place])
	end
end

-- Called by ThrowService when an egg lands: the first player in this server to reach a world gets a
-- shout on everyone's screen.
function CompetitionService.landedIn(player: Player, biome)
	local index = table.find(Biomes, biome)
	if index and index > farthestWorld then
		farthestWorld = index
		worldFirstRemote:FireAllClients(player.Name, biome.name, biome.color)
	end
end

function CompetitionService.start()
	worldFirstRemote = Instance.new("RemoteEvent")
	worldFirstRemote.Name = "WorldFirst"
	worldFirstRemote.Parent = ReplicatedStorage

	task.spawn(function()
		while true do
			task.wait(Competition.rankEvery)
			rankPlayers()
		end
	end)
end

return CompetitionService
