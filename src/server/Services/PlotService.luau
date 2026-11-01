-- Owns the dinos players have caught: keeps them on the plot or in the backpack, pays
-- their $/s, and shows them as statues. The client can only ask for changes through
-- DinoAction; every request is checked here against the player's saved data.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Catch = require(ReplicatedStorage.Shared.Config.Catch)
local DinoModel = require(ReplicatedStorage.Shared.DinoModel)
local DinoStats = require(ReplicatedStorage.Shared.DinoStats)
local Plot = require(ReplicatedStorage.Shared.Config.Plot)
local Format = require(ReplicatedStorage.Shared.Format)
local IndexService = require(script.Parent.IndexService)
local PlayerData = require(script.Parent.PlayerData)
local World = require(script.Parent.World)

local PlotService = {}

local INCOME_TICK = 1 -- seconds
local SLOT_THICKNESS = 0.2
local SIGN_HEIGHT = 20
local SIGN_DISTANCE = 400
local STATUE_LABEL_DISTANCE = 90

local remotes: { [string]: RemoteEvent } = {}
local plotModels: { Model } = {}
local plotOwners: { [number]: Player } = {}
local statueFolders: { [Player]: Folder } = {}

local function makeRemotes()
	local folder = Instance.new("Folder")
	folder.Name = "PlotRemotes"
	for _, name in { "DinoAction", "DinosChanged" } do
		local remote = Instance.new("RemoteEvent")
		remote.Name = name
		remote.Parent = folder
		remotes[name] = remote
	end
	folder.Parent = ReplicatedStorage
end

local function slotPosition(plotIndex: number, slot: number): Vector3
	local columns = Plot.columns
	local rows = math.ceil(Plot.slots / columns)
	local column = (slot - 1) % columns
	local row = math.floor((slot - 1) / columns)
	local x = (column - (columns - 1) / 2) * Plot.slotSpacing.X
	local z = (row - (rows - 1) / 2) * Plot.slotSpacing.Y
	return Plot.positions[plotIndex] + Vector3.new(x, Plot.size.Y + SLOT_THICKNESS, z)
end

local function buildPlots()
	local folder = Instance.new("Folder")
	folder.Name = "Plots"
	for plotIndex, position in Plot.positions do
		local model = Instance.new("Model")
		model.Name = `Plot{plotIndex}`
		local ground = World.makePart(
			model,
			"Ground",
			Plot.size,
			CFrame.new(position + Vector3.new(0, Plot.size.Y / 2, 0)),
			Plot.color
		)
		ground.TopSurface = Enum.SurfaceType.Studs
		for slot = 1, Plot.slots do
			local base = World.makePart(
				model,
				"Slot",
				Vector3.new(Plot.slotSpacing.X - 4, SLOT_THICKNESS, Plot.slotSpacing.Y - 4),
				CFrame.new(slotPosition(plotIndex, slot) - Vector3.new(0, SLOT_THICKNESS / 2, 0)),
				Plot.slotColor
			)
			base.TopSurface = Enum.SurfaceType.Studs
		end
		local signAnchor = World.makePart(
			model,
			"SignAnchor",
			Vector3.new(1, 1, 1),
			CFrame.new(position + Vector3.new(0, SIGN_HEIGHT, -Plot.size.Z / 2)),
			Plot.color
		)
		signAnchor.Transparency = 1
		signAnchor.CanCollide = false
		World.makeSign(signAnchor, "Free plot", 0, SIGN_DISTANCE, 420)
		model.Parent = folder
		plotModels[plotIndex] = model
	end
	folder.Parent = workspace
end

local function plotIndexOf(player: Player): number?
	for plotIndex in plotModels do
		if plotOwners[plotIndex] == player then
			return plotIndex
		end
	end
	return nil
end

local function setSign(plotIndex: number, text: string)
	plotModels[plotIndex].SignAnchor.Sign.TextLabel.Text = text
end

local function plotted(data): { any }
	local list = {}
	for _, entry in data.dinos do
		if entry.onPlot then
			table.insert(list, entry)
		end
	end
	return list
end

local function incomeOf(entry): number
	local stats = DinoStats.describe(entry)
	return if stats then stats.income else 0
end

local function totalIncome(data): number
	local total = 0
	for _, entry in plotted(data) do
		total += incomeOf(entry)
	end
	return total * IndexService.cashMultiplier(data)
end

local function sellPrice(entry): number
	return math.floor(incomeOf(entry) * Plot.sellSeconds)
end

local function statueScale(entry): number
	local size = DinoStats.findOption(Catch.sizes, entry.size)
	return math.min(if size then size.scale else 1, Plot.maxStatueScale)
end

local function rebuildStatues(player: Player, data)
	local plotIndex = plotIndexOf(player)
	if not plotIndex then
		return
	end
	local old = statueFolders[player]
	if old then
		old:Destroy()
	end
	local folder = Instance.new("Folder")
	folder.Name = "Statues"
	for slot, entry in plotted(data) do
		local stats = DinoStats.describe(entry)
		if stats then
			local statue = DinoModel.build(stats.name, entry.mutation, slotPosition(plotIndex, slot), statueScale(entry))
			local head = statue.Head
			World.makeSign(head, `{stats.name}\n{Format.cash(stats.income)}/s`, 5, STATUE_LABEL_DISTANCE, 170)
			statue.Parent = folder
		end
	end
	folder.Parent = plotModels[plotIndex]
	statueFolders[player] = folder
end

-- Everything the client's panel shows, best dino first.
local function publish(player: Player, data)
	local list = {}
	for _, entry in data.dinos do
		local stats = DinoStats.describe(entry)
		if stats then
			table.insert(list, {
				key = entry.key,
				name = stats.name,
				mutation = entry.mutation,
				size = entry.size,
				income = stats.income,
				oneIn = stats.oneIn,
				onPlot = entry.onPlot,
				sellPrice = sellPrice(entry),
			})
		end
	end
	table.sort(list, function(a, b)
		return a.income > b.income
	end)
	player:SetAttribute("Income", totalIncome(data))
	remotes.DinosChanged:FireClient(player, list, Plot.slots)
end

local function changed(player: Player, data)
	rebuildStatues(player, data)
	publish(player, data)
end

local function findEntry(data, key: any)
	for index, entry in data.dinos do
		if entry.key == key then
			return entry, index
		end
	end
	return nil, nil
end

local function backpackCount(data): number
	return #data.dinos - #plotted(data)
end

local function equipBest(data)
	local sorted = table.clone(data.dinos)
	table.sort(sorted, function(a, b)
		return incomeOf(a) > incomeOf(b)
	end)
	for rank, entry in sorted do
		entry.onPlot = rank <= Plot.slots
	end
end

local function onAction(player: Player, action: any, key: any)
	local data = PlayerData.get(player)
	if not data then
		return
	end

	if action == "equipBest" then
		equipBest(data)
		changed(player, data)
		return
	end

	local entry, index = findEntry(data, key)
	if not entry then
		return
	end
	if action == "place" then
		if not entry.onPlot and #plotted(data) < Plot.slots then
			entry.onPlot = true
			changed(player, data)
		end
	elseif action == "pickUp" then
		if entry.onPlot and backpackCount(data) < Plot.backpackSize then
			entry.onPlot = false
			changed(player, data)
		end
	elseif action == "sell" then
		data.cash += sellPrice(entry)
		table.remove(data.dinos, index)
		player:SetAttribute("Cash", data.cash)
		changed(player, data)
	end
end

-- Stores a new catch: on the plot if there's room, otherwise in the backpack.
-- With no room in either, it's sold. Returns where it went: "plot", "backpack" or "sold".
function PlotService.addCatch(player: Player, catch): string?
	local data = PlayerData.get(player)
	if not data then
		return nil
	end
	local entry = { key = data.nextDinoKey, id = catch.id, mutation = catch.mutation, size = catch.size, onPlot = false }
	local result
	if #plotted(data) < Plot.slots then
		entry.onPlot = true
		result = "plot"
	elseif backpackCount(data) < Plot.backpackSize then
		result = "backpack"
	else
		data.cash += sellPrice(entry)
		player:SetAttribute("Cash", data.cash)
		return "sold"
	end
	data.nextDinoKey += 1
	table.insert(data.dinos, entry)
	changed(player, data)
	return result
end

local function onLoaded(player: Player, data)
	for plotIndex in plotModels do
		if not plotOwners[plotIndex] then
			plotOwners[plotIndex] = player
			setSign(plotIndex, `{player.DisplayName}'s Plot`)
			player:SetAttribute("PlotIndex", plotIndex)
			break
		end
	end
	player:SetAttribute("Cash", data.cash)
	changed(player, data)
end

local function onLeaving(player: Player)
	local plotIndex = plotIndexOf(player)
	if plotIndex then
		plotOwners[plotIndex] = nil
		setSign(plotIndex, "Free plot")
	end
	local folder = statueFolders[player]
	if folder then
		folder:Destroy()
		statueFolders[player] = nil
	end
end

local function payIncome()
	for _, player in Players:GetPlayers() do
		local data = PlayerData.get(player)
		if data then
			local income = totalIncome(data)
			data.cash += income * INCOME_TICK
			player:SetAttribute("Cash", data.cash)
			player:SetAttribute("Income", income)
		end
	end
end

function PlotService.start()
	makeRemotes()
	buildPlots()
	remotes.DinoAction.OnServerEvent:Connect(onAction)
	PlayerData.onLoaded(onLoaded)
	Players.PlayerRemoving:Connect(onLeaving)
	task.spawn(function()
		while true do
			task.wait(INCOME_TICK)
			payIncome()
		end
	end)
end

return PlotService
