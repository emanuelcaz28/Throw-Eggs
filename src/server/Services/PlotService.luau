-- Owns the dinos players have caught: keeps them on the plot or in the backpack, pays
-- their $/s, and shows them as statues wherever they were placed. A backpack dino can be
-- equipped (carried beside the character) and then placed anywhere on the plot. The client
-- can only ask for changes through DinoAction; every request is checked here against the
-- player's saved data.
local CollectionService = game:GetService("CollectionService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local DinoModel = require(ReplicatedStorage.Shared.DinoModel)
local DinoStats = require(ReplicatedStorage.Shared.DinoStats)
local DinoLife = require(ReplicatedStorage.Shared.Config.DinoLife)
local Events = require(ReplicatedStorage.Shared.Config.Events)
local Plot = require(ReplicatedStorage.Shared.Config.Plot)
local Format = require(ReplicatedStorage.Shared.Format)
local Shop = require(ReplicatedStorage.Shared.Config.Shop)
local IndexService = require(script.Parent.IndexService)
local PlayerData = require(script.Parent.PlayerData)
local World = require(script.Parent.World)

local PlotService = {}

local INCOME_TICK = 1 -- seconds
local SIGN_HEIGHT = 20
local SIGN_DISTANCE = 400
local STATUE_LABEL_DISTANCE = 90
local FENCE_POST_SPACING = 8
local UPGRADE_SIGN_SIZE = Vector3.new(10, 5, 1)
local UPGRADE_SIGN_INSET = 4 -- studs inside the front edge, beside the gate
local UPGRADE_CLICK_DISTANCE = 40
local SIGN_INK = Color3.fromRGB(20, 22, 28)
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

-- A wooden fence from a to b (points on the plot's surface): posts with two rails.
local function buildFence(model: Model, a: Vector3, b: Vector3)
	local length = (b - a).Magnitude
	local direction = (b - a).Unit
	local posts = math.max(math.ceil(length / FENCE_POST_SPACING), 1)
	for post = 0, posts do
		local point = a + direction * (length * post / posts)
		local part = World.makePart(
			model,
			"FencePost",
			Vector3.new(1.2, Plot.fenceHeight, 1.2),
			CFrame.new(point + Vector3.new(0, Plot.fenceHeight / 2, 0)),
			Plot.fenceColor
		)
		part.TopSurface = Enum.SurfaceType.Studs
	end
	for _, height in { Plot.fenceHeight * 0.4, Plot.fenceHeight * 0.8 } do
		local middle = (a + b) / 2 + Vector3.new(0, height, 0)
		World.makePart(model, "FenceRail", Vector3.new(0.6, 0.6, length), CFrame.lookAt(middle, middle + direction), Plot.fenceColor)
	end
end

-- Text on one face of the upgrade sign: "8 > 10" over a dark price bar.
local function makeSignFace(board: BasePart, face: Enum.NormalId)
	local gui = Instance.new("SurfaceGui")
	gui.Name = face.Name
	gui.Face = face
	gui.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
	gui.PixelsPerStud = 50
	gui.Parent = board

	local count = Instance.new("TextLabel")
	count.Name = "Count"
	count.BackgroundTransparency = 1
	count.Position = UDim2.fromScale(0.05, 0.06)
	count.Size = UDim2.fromScale(0.9, 0.5)
	count.Font = Enum.Font.GothamBlack
	count.TextColor3 = Color3.new(1, 1, 1)
	count.TextStrokeTransparency = 0
	count.TextScaled = true
	count.Parent = gui

	local bar = Instance.new("TextLabel")
	bar.Name = "Price"
	bar.BackgroundColor3 = SIGN_INK
	bar.Position = UDim2.fromScale(0.08, 0.62)
	bar.Size = UDim2.fromScale(0.84, 0.3)
	bar.Font = Enum.Font.GothamBlack
	bar.TextColor3 = Color3.new(1, 1, 1)
	bar.TextScaled = true
	bar.Parent = gui
	local barCorner = Instance.new("UICorner")
	barCorner.CornerRadius = UDim.new(0.25, 0)
	barCorner.Parent = bar
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

		-- Fence on all four sides, with a gate in the middle of the front edge (the plot's exit).
		local top = position.Y + Plot.size.Y
		local halfX, halfZ, halfGate = Plot.size.X / 2, Plot.size.Z / 2, Plot.gateWidth / 2
		local function corner(x: number, z: number): Vector3
			return Vector3.new(position.X + x, top, position.Z + z)
		end
		buildFence(model, corner(-halfX, -halfZ), corner(-halfGate, -halfZ))
		buildFence(model, corner(halfGate, -halfZ), corner(halfX, -halfZ))
		buildFence(model, corner(-halfX, halfZ), corner(halfX, halfZ))
		buildFence(model, corner(-halfX, -halfZ), corner(-halfX, halfZ))
		buildFence(model, corner(halfX, -halfZ), corner(halfX, halfZ))

		-- The upgrade sign stands on two legs just inside the gate, above the fence so it can be
		-- clicked from outside too. Clicking it buys more room.
		local signBase = corner(halfGate + UPGRADE_SIGN_SIZE.X / 2 + 2, -halfZ + UPGRADE_SIGN_INSET)
		local legHeight = Plot.fenceHeight + 1
		for _, side in { -1, 1 } do
			World.makePart(
				model,
				"SignLeg",
				Vector3.new(1, legHeight, 1),
				CFrame.new(signBase + Vector3.new(side * (UPGRADE_SIGN_SIZE.X / 2 - 1), legHeight / 2, 0)),
				Plot.fenceColor
			)
		end
		local board = World.makePart(
			model,
			"UpgradeSign",
			UPGRADE_SIGN_SIZE,
			CFrame.new(signBase + Vector3.new(0, legHeight + UPGRADE_SIGN_SIZE.Y / 2, 0)),
			Plot.fenceColor
		)
		board.TopSurface = Enum.SurfaceType.Studs
		makeSignFace(board, Enum.NormalId.Front)
		makeSignFace(board, Enum.NormalId.Back)
		local click = Instance.new("ClickDetector")
		click.MaxActivationDistance = UPGRADE_CLICK_DISTANCE
		click.Parent = board
		click.MouseClick:Connect(function(player)
			onUpgradeClicked(plotIndex, player)
		end)

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

-- Shows the owner's next upgrade on both faces of the sign. A free plot's sign is blank.
local function setUpgradeSign(plotIndex: number, data)
	local board = plotModels[plotIndex].UpgradeSign
	for _, face in { board.Front, board.Back } do
		face.Enabled = data ~= nil
		if data then
			local capacity = Plot.capacity(data.plotUpgrades)
			local maxed = capacity >= Plot.maxSlots
			face.Count.Text = if maxed then `{capacity} MAX` else `{capacity} > {Plot.capacity(data.plotUpgrades + 1)}`
			face.Price.Text = if maxed then "MAXED" else `▲ {Format.cash(Plot.upgradePrice(data.plotUpgrades))}`
		end
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
	return baseIncome(player, data) * Events.multiplier("income")
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
			local statue = DinoModel.build(entry.id, entry.mutation, position, DinoModel.statueScale(entry.size))
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

-- A short message above the player's hotbar, like "Plot upgraded!". seconds is optional.
-- Pays a Shop cash pack: minutes of the plot's $/s without events (Config/Shop). The caller saves the data.
function PlotService.payCashPack(player: Player, data, pack)
	earn(player, data, Shop.cashPackAmount(pack, baseIncome(player, data)))
end

function PlotService.notify(player: Player, text: string, seconds: number?)
	remotes.Notice:FireClient(player, text, seconds)
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
			setSign(plotIndex, `{player.DisplayName}'s Plot`)
			setUpgradeSign(plotIndex, data)
			player:SetAttribute("PlotIndex", plotIndex)
			break
		end
	end
	player:SetAttribute("Cash", data.cash)
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
		setSign(plotIndex, "Free plot")
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
		remotes.Notice:FireClient(player, "That's someone else's plot")
		return
	end
	if capacityOf(data) >= Plot.maxSlots then
		remotes.Notice:FireClient(player, "Your plot is as big as it gets!")
		return
	end
	local price = Plot.upgradePrice(data.plotUpgrades)
	if data.cash < price then
		remotes.Notice:FireClient(player, `You need {Format.cash(price)} for this upgrade`)
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
			earn(player, data, income * INCOME_TICK)
			data.lastSeen = os.time()
			player:SetAttribute("Income", income)
			player:SetAttribute("BaseIncome", baseIncome(player, data))
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
