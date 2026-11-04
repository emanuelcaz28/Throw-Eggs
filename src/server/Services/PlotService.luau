-- Owns the dinos players have caught: keeps them on the plot or in the backpack, pays
-- their $/s, and shows them as statues wherever they were placed. A backpack dino can be
-- equipped (carried beside the character) and then placed anywhere on the plot. The client
-- can only ask for changes through DinoAction; every request is checked here against the
-- player's saved data.
local CollectionService = game:GetService("CollectionService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local BaseKit = require(ReplicatedStorage.Shared.BaseKit)
local Catch = require(ReplicatedStorage.Shared.Config.Catch)
local DinoModel = require(ReplicatedStorage.Shared.DinoModel)
local DinoStats = require(ReplicatedStorage.Shared.DinoStats)
local DinoLife = require(ReplicatedStorage.Shared.Config.DinoLife)
local Map = require(ReplicatedStorage.Shared.Config.Map)
local Plot = require(ReplicatedStorage.Shared.Config.Plot)
local Format = require(ReplicatedStorage.Shared.Format)
local Shop = require(ReplicatedStorage.Shared.Config.Shop)
local BaseSigns = require(script.Parent.BaseSigns)
local IndexService = require(script.Parent.IndexService)
local PlayerData = require(script.Parent.PlayerData)
local World = require(ReplicatedStorage.Shared.World)

local PlotService = {}

local INCOME_TICK = 1 -- seconds
local STATUE_LABEL_DISTANCE = 90
local OUT = Vector3.new(0, 0, -1) -- out of every base, through its gate
local SPOT_TRIES = 40
local HELD_SCALE = 0.35
local HELD_SIDE = 3.5 -- studs to the character's right

local remotes: { [string]: RemoteEvent } = {}
local plotModels: { Model } = {}
local plotOwners: { [number]: Player } = {}
local statueFolders: { [Player]: Folder } = {}
local held: { [Player]: number } = {} -- key of the dino each player is carrying
local heldModels: { [Player]: Model } = {}
local rng = Random.new()

local function makeRemotes()
	local folder = Instance.new("Folder")
	folder.Name = "PlotRemotes"
	for _, name in { "DinoAction", "DinosChanged", "Notice", "OfflineEarnings", "ClaimOffline" } do
		local remote = Instance.new("RemoteEvent")
		remote.Name = name
		remote.Parent = folder
		remotes[name] = remote
	end
	folder.Parent = ReplicatedStorage
end

-- A spot on the plot's surface, from its saved offset (studs from the plot's centre).
local function spotPosition(plotIndex: number, x: number, z: number): Vector3
	return Plot.positions[plotIndex] + Vector3.new(x, Plot.size.Y, z)
end

local onUpgradeClicked: (number, Player) -> ()

-- A wooden fence along a base's edge, from a to b (points on the ground): Blender posts every
-- Plot.fenceSection studs with rails between them. Posts are shared with the next run at the corners.
local function buildFence(model: Model, posts: { [string]: boolean }, a: Vector3, b: Vector3)
	local length = (b - a).Magnitude
	local direction = (b - a).Unit
	local sections = math.max(math.round(length / Plot.fenceSection), 1)
	for index = 0, sections do
		local point = a + direction * (length * index / sections)
		local key = `{math.round(point.X)},{math.round(point.Z)}`
		if not posts[key] then
			posts[key] = true
			BaseKit.place("base_FencePost", CFrame.lookAt(point, point + OUT), model)
		end
		if index < sections then
			-- The rails run along the piece's X, so turn X onto the fence's direction.
			local middle = a + direction * (length * (index + 0.5) / sections)
			BaseKit.place("base_FenceRails", CFrame.fromMatrix(middle, direction, Vector3.yAxis), model)
		end
	end
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
		-- The same studs as the arena around it and every model (Config/Map studsMaterial).
		ground.Material = Enum.Material.SmoothPlastic
		ground.MaterialVariant = Map.studsMaterial
		BaseSigns.buildPlate(model, plotIndex)

		-- Fence on all four sides, with a gate in the middle of the front edge (the plot's exit).
		local top = position.Y + Plot.size.Y
		local halfX, halfZ, halfGate = Plot.size.X / 2, Plot.size.Z / 2, Plot.gateWidth / 2
		local function corner(x: number, z: number): Vector3
			return Vector3.new(position.X + x, top, position.Z + z)
		end
		local fence = Instance.new("Model")
		fence.Name = "Fence"
		local posts = {}
		buildFence(fence, posts, corner(-halfX, -halfZ), corner(-halfGate, -halfZ))
		buildFence(fence, posts, corner(halfGate, -halfZ), corner(halfX, -halfZ))
		buildFence(fence, posts, corner(-halfX, halfZ), corner(halfX, halfZ))
		buildFence(fence, posts, corner(-halfX, -halfZ), corner(-halfX, halfZ))
		buildFence(fence, posts, corner(halfX, -halfZ), corner(halfX, halfZ))
		fence.Parent = model

		-- The upgrade sign stands on the front fence by the gate. Clicking it buys more room.
		local signAt = Plot.gatePosition(plotIndex) + Plot.upgradeSign.offset
		local sign = BaseKit.place("base_UpgradeSign", CFrame.lookAt(signAt, signAt + OUT), model)
		local board = sign and sign:FindFirstChild("Board") :: BasePart?
		if board then
			board.Name = "UpgradeSign"
			BaseSigns.buildSignFace(board, BaseKit.faceToward(board, OUT))
			local click = Instance.new("ClickDetector")
			click.MaxActivationDistance = Plot.upgradeSign.clickDistance
			click.Parent = board
			click.MouseClick:Connect(function(player)
				onUpgradeClicked(plotIndex, player)
			end)
		end

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

-- Shows the owner's next upgrade on the sign, and whether they can afford it. A free plot's sign is blank.
local function setUpgradeSign(plotIndex: number, data)
	local board = plotModels[plotIndex]:FindFirstChild("UpgradeSign", true)
	if board then
		BaseSigns.setSignFace(board, data, data and data.cash)
	end
end

local function capacityOf(data): number
	return Plot.capacity(data.plotUpgrades)
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

-- The plot's $/s with every lasting bonus, but not the timed event's.
local function baseIncome(player: Player, data): number
	local total = 0
	for _, entry in plotted(data) do
		total += incomeOf(entry)
	end
	local passMultiplier = if player:GetAttribute("HasDoubleCash") then Shop.doubleCash.multiplier else 1
	return total * IndexService.cashMultiplier(data) * passMultiplier
end

local function totalIncome(player: Player, data): number
	return baseIncome(player, data)
end

local function sellPrice(entry): number
	return math.floor(incomeOf(entry) * Plot.sellSeconds)
end

-- All cash a player earns goes through here, so the Top Money leaderboard counts it.
local function earn(player: Player, data, amount: number)
	data.cash += amount
	data.totalEarned += amount
	player:SetAttribute("Cash", data.cash)
end

-- A random spot that keeps clear of the dinos already placed and of where players land
-- after a catch. When the plot is crowded, the emptiest spot found is used.
local function freeSpot(data): (number, number)
	local taken = { Vector2.new(0, -Plot.size.Z / 2 + Plot.homeInset) }
	for _, entry in data.dinos do
		if entry.onPlot and entry.x and entry.z then
			table.insert(taken, Vector2.new(entry.x, entry.z))
		end
	end
	local halfX = Plot.size.X / 2 - Plot.placeMargin
	local halfZ = Plot.size.Z / 2 - Plot.placeMargin
	local bestSpot, bestGap = Vector2.zero, -1
	for _ = 1, SPOT_TRIES do
		local spot = Vector2.new(rng:NextNumber(-halfX, halfX), rng:NextNumber(-halfZ, halfZ))
		local gap = math.huge
		for _, other in taken do
			gap = math.min(gap, (spot - other).Magnitude)
		end
		if gap >= Plot.autoSpacing then
			return spot.X, spot.Y
		end
		if gap > bestGap then
			bestSpot, bestGap = spot, gap
		end
	end
	return bestSpot.X, bestSpot.Y
end

-- Dinos on the plot always have a spot; dinos in the backpack never do. Gives a spot to new
-- catches, Equip Best picks and saves from before free placement.
local function updateSpots(data)
	for _, entry in data.dinos do
		if not entry.onPlot then
			entry.x, entry.z = nil, nil
		elseif not entry.x or not entry.z then
			entry.x, entry.z = freeSpot(data)
		end
	end
end

local function dropHeldModel(player: Player)
	local model = heldModels[player]
	if model then
		model:Destroy()
		heldModels[player] = nil
	end
end

-- A small copy of the carried dino walks beside the character, welded to it so everyone sees it.
local function attachHeldModel(player: Player, entry)
	dropHeldModel(player)
	local character = player.Character
	local root = character and character:FindFirstChild("HumanoidRootPart") :: BasePart?
	local humanoid = character and character:FindFirstChildOfClass("Humanoid")
	local stats = DinoStats.describe(entry)
	if not root or not humanoid or not stats then
		return
	end
	local feet = root.CFrame * CFrame.new(HELD_SIDE, -(humanoid.HipHeight + root.Size.Y / 2), 0)
	local model = DinoModel.build(entry.id, entry.mutation, Vector3.zero, HELD_SCALE)
	model.Name = "HeldDino"
	model:PivotTo(feet)
	for _, part in model:GetDescendants() do
		if part:IsA("BasePart") then
			part.Anchored = false
			part.Massless = true
			local weld = Instance.new("WeldConstraint")
			weld.Part0 = root
			weld.Part1 = part
			weld.Parent = part
		end
	end
	model.Parent = character
	heldModels[player] = model
end

local function setHeld(player: Player, data, key: number?)
	held[player] = key
	player:SetAttribute("HeldDino", key)
	local entry = nil
	for _, candidate in data.dinos do
		if candidate.key == key then
			entry = candidate
		end
	end
	if entry then
		attachHeldModel(player, entry)
	else
		dropHeldModel(player)
	end
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
	for _, entry in plotted(data) do
		local stats = DinoStats.describe(entry)
		if stats then
			local position = spotPosition(plotIndex, entry.x, entry.z)
			local statue = DinoModel.build(entry.id, entry.mutation, position, DinoModel.statueScale(entry.id, entry.size))
			local head = statue.Head
			World.makeSign(head, `{stats.name}\n{Format.cash(stats.income)}/s`, 5, STATUE_LABEL_DISTANCE, 170)
			statue.ModelStreamingMode = Enum.ModelStreamingMode.Atomic
			statue:SetAttribute("PlotIndex", plotIndex)
			CollectionService:AddTag(statue, DinoLife.tag)
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
				id = entry.id,
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
	player:SetAttribute("Income", totalIncome(player, data))
	player:SetAttribute("BaseIncome", baseIncome(player, data))
	remotes.DinosChanged:FireClient(player, list, capacityOf(data))
end

local function changed(player: Player, data)
	updateSpots(data)
	-- A carried dino that was placed, sold or moved by Equip Best is no longer carried.
	local heldKey = held[player]
	if heldKey then
		local stillInBackpack = false
		for _, entry in data.dinos do
			if entry.key == heldKey and not entry.onPlot then
				stillInBackpack = true
			end
		end
		if not stillInBackpack then
			setHeld(player, data, nil)
		end
	end
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
		entry.onPlot = rank <= capacityOf(data)
	end
end

-- Saves from before the bases shrank can hold more dinos than the base now fits, or spots outside
-- its fence. The best ones stay on the base, the rest go to the backpack, and out-of-bounds dinos
-- get a new spot (updateSpots).
local function fitToPlot(data)
	local placed = plotted(data)
	table.sort(placed, function(a, b)
		return incomeOf(a) > incomeOf(b)
	end)
	for rank, entry in placed do
		if rank > capacityOf(data) then
			entry.onPlot = false
		elseif entry.x and entry.z and not Plot.inBounds(entry.x, entry.z) then
			entry.x, entry.z = nil, nil
		end
	end
end

-- Saves from before the six size mutations keep their dino's size under its new name.
local function renameOldSizes(data)
	for _, entry in data.dinos do
		entry.size = Catch.renamedSizes[entry.size] or entry.size
	end
end

local function onAction(player: Player, action: any, key: any, x: any, z: any)
	local data = PlayerData.get(player)
	if not data then
		return
	end

	if action == "equipBest" then
		equipBest(data)
		changed(player, data)
		return
	elseif action == "unequip" then
		setHeld(player, data, nil)
		return
	end

	local entry, index = findEntry(data, key)
	if not entry then
		return
	end
	if action == "equip" then
		-- Equipping the dino already carried puts it away again.
		if not entry.onPlot then
			setHeld(player, data, if held[player] == entry.key then nil else entry.key)
		end
	elseif action == "placeAt" then
		-- x ~= x is only true for NaN.
		if typeof(x) ~= "number" or typeof(z) ~= "number" or x ~= x or z ~= z or not Plot.inBounds(x, z) then
			return
		end
		if not entry.onPlot and #plotted(data) < capacityOf(data) and plotIndexOf(player) then
			entry.onPlot = true
			entry.x = math.round(x * 10) / 10
			entry.z = math.round(z * 10) / 10
			changed(player, data)
		end
	elseif action == "pickUp" then
		if entry.onPlot and backpackCount(data) < Plot.backpackSize then
			entry.onPlot = false
			changed(player, data)
		end
	elseif action == "sell" then
		earn(player, data, sellPrice(entry))
		table.remove(data.dinos, index)
		changed(player, data)
	end
end

-- Pays a Shop cash pack: minutes of the plot's $/s without events (Config/Shop). The caller saves the data.
function PlotService.payCashPack(player: Player, data, pack)
	earn(player, data, Shop.cashPackAmount(pack, baseIncome(player, data)))
end

-- A short message above the player's hotbar, like "Plot upgraded!". bad shows it in red, for things that
-- didn't work, like "You need $500".
function PlotService.notify(player: Player, text: string, bad: boolean?)
	remotes.Notice:FireClient(player, text, bad)
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
	if #plotted(data) < capacityOf(data) then
		entry.onPlot = true
		result = "plot"
	elseif backpackCount(data) < Plot.backpackSize then
		result = "backpack"
	else
		earn(player, data, sellPrice(entry))
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
			BaseSigns.setPlate(plotModels[plotIndex], player)
			setUpgradeSign(plotIndex, data)
			player:SetAttribute("PlotIndex", plotIndex)
			break
		end
	end
	player:SetAttribute("Cash", data.cash)
	renameOldSizes(data)
	fitToPlot(data)
	changed(player, data)

	-- Offline earnings wait for the player to press CLAIM on the Welcome back pop-up. They're
	-- saved, so leaving before claiming keeps them for next time. Read the last-seen time now,
	-- before the income ticks overwrite it.
	local away = math.min(os.time() - data.lastSeen, Plot.maxOfflineHours * 3600)
	local wasAway = data.lastSeen > 0 and away >= Plot.minOfflineSeconds
	if wasAway or data.offlinePending > 0 then
		task.delay(Plot.offlinePayoutDelay, function()
			if PlayerData.get(player) ~= data then
				return
			end
			if wasAway then
				data.offlinePending += math.floor(baseIncome(player, data) * away * Plot.offlineRate)
			end
			if data.offlinePending > 0 then
				remotes.OfflineEarnings:FireClient(player, data.offlinePending, if wasAway then away else 0)
			end
		end)
	end

	-- A new character drops the carried copy, so give it back.
	player.CharacterAdded:Connect(function(character)
		character:WaitForChild("HumanoidRootPart", 5)
		if held[player] then
			setHeld(player, data, held[player])
		end
	end)
end

local function onLeaving(player: Player)
	held[player] = nil
	heldModels[player] = nil
	local plotIndex = plotIndexOf(player)
	if plotIndex then
		plotOwners[plotIndex] = nil
		BaseSigns.setPlate(plotModels[plotIndex], nil)
		setUpgradeSign(plotIndex, nil)
	end
	local folder = statueFolders[player]
	if folder then
		folder:Destroy()
		statueFolders[player] = nil
	end
end

onUpgradeClicked = function(plotIndex: number, player: Player)
	local data = PlayerData.get(player)
	if not data then
		return
	end
	if plotOwners[plotIndex] ~= player then
		remotes.Notice:FireClient(player, "That's someone else's plot", true)
		return
	end
	if capacityOf(data) >= Plot.maxSlots then
		remotes.Notice:FireClient(player, "Your plot is as big as it gets!", true)
		return
	end
	local price = Plot.upgradePrice(data.plotUpgrades)
	if data.cash < price then
		remotes.Notice:FireClient(player, `You need {Format.cash(price)} for this upgrade`, true)
		return
	end
	data.cash -= price
	data.plotUpgrades += 1
	player:SetAttribute("Cash", data.cash)
	setUpgradeSign(plotIndex, data)
	remotes.Notice:FireClient(player, `Plot upgraded! It now holds {capacityOf(data)} dinos`)
	changed(player, data)
end

local function payIncome()
	for _, player in Players:GetPlayers() do
		local data = PlayerData.get(player)
		if data then
			local income = totalIncome(player, data)
			-- $/s first: the client tells this tick from other cash by comparing the two.
			player:SetAttribute("Income", income)
			earn(player, data, income * INCOME_TICK)
			data.lastSeen = os.time()
			player:SetAttribute("BaseIncome", baseIncome(player, data))
			local plotIndex = plotIndexOf(player)
			if plotIndex then
				BaseSigns.setPlateIncome(plotModels[plotIndex], income)
				setUpgradeSign(plotIndex, data) -- the price turns green once they can afford it
			end
		end
	end
end

function PlotService.start()
	makeRemotes()
	buildPlots()
	remotes.DinoAction.OnServerEvent:Connect(onAction)
	remotes.ClaimOffline.OnServerEvent:Connect(function(player)
		local data = PlayerData.get(player)
		if data and data.offlinePending > 0 then
			local amount = data.offlinePending
			data.offlinePending = 0
			earn(player, data, amount)
			remotes.Notice:FireClient(player, `+{Format.cash(amount)} claimed!`)
		end
	end)
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
