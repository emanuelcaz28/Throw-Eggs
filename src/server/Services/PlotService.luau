-- Owns the dinos players have caught: keeps them on the plot or in the backpack, pays
-- their $/s, and shows them as statues wherever they were placed. A backpack dino can be
-- equipped (carried on the character's head) and then placed anywhere on the plot. The client
-- can only ask for changes through DinoAction; every request is checked here against the
-- player's saved data.
local CollectionService = game:GetService("CollectionService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local BaseKit = require(ReplicatedStorage.Shared.BaseKit)
local Catch = require(ReplicatedStorage.Shared.Config.Catch)
local Chonk = require(ReplicatedStorage.Shared.Config.Chonk)
local DinoModel = require(ReplicatedStorage.Shared.DinoModel)
local DinoStats = require(ReplicatedStorage.Shared.DinoStats)
local DinoLife = require(ReplicatedStorage.Shared.Config.DinoLife)
local Map = require(ReplicatedStorage.Shared.Config.Map)
local Plot = require(ReplicatedStorage.Shared.Config.Plot)
local Format = require(ReplicatedStorage.Shared.Format)
local Shop = require(ReplicatedStorage.Shared.Config.Shop)
local BaseSigns = require(script.Parent.BaseSigns)
local PlayerData = require(script.Parent.PlayerData)
local TutorialService = require(script.Parent.TutorialService)
local World = require(ReplicatedStorage.Shared.World)

local PlotService = {}

local INCOME_TICK = 1 -- seconds
local OUT = Vector3.new(0, 0, -1) -- out of every base, through its gate
local SPOT_TRIES = 40

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

-- The best monster this player owns from the maps: what a special monster's share is taken from.
local function bestIncome(data): number
	local best = 0
	for _, entry in data.dinos do
		if not DinoStats.special(entry.id) then
			best = math.max(best, incomeOf(entry))
		end
	end
	return best
end

-- The plot's $/s with every lasting bonus, but not the timed event's.
local function baseIncome(player: Player, data): number
	local total = 0
	for _, entry in plotted(data) do
		total += incomeOf(entry)
	end
	local passMultiplier = if player:GetAttribute("HasDoubleCash") then Shop.doubleCash.multiplier else 1
	return total * passMultiplier
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

-- The carried monster sits on top of the character's head at its real size (its map's standard size times its size
-- mutation), facing the way the character faces, welded on so everyone sees it. Its body is centred over the head
-- and its feet stand on the top of the whole character, hats and big avatar heads included, so it's never inside
-- the player (Config/DinoLife carry) [Owner, 2026-11-07]. DinoLifeController makes it walk and idle; its tag
-- (MonsterTagController) shows its name and rarity.
local function attachHeldModel(player: Player, entry)
	dropHeldModel(player)
	local character = player.Character
	local root = character and character:FindFirstChild("HumanoidRootPart") :: BasePart?
	local head = character and character:FindFirstChild("Head") :: BasePart?
	local stats = DinoStats.describe(entry)
	if not root or not head or not stats then
		return
	end
	local model = DinoModel.build(entry.id, entry.mutation, Vector3.zero, DinoModel.entryScale(entry))
	model.Name = "HeldDino"
	local centre = DinoModel.visibleBox(model)
	local sink = math.min((DinoModel.legHeight(model) or 0) * DinoLife.carry.sink, DinoLife.carry.maxSink)
	local facing = if DinoModel.facesBack(model) then CFrame.Angles(0, math.pi, 0) else CFrame.identity
	-- The top of everything the character wears, measured upright from its root: a Head part can be much smaller
	-- than the avatar's head mesh, and hats and hair stick up above it.
	local top = root.CFrame:PointToObjectSpace(head.Position + Vector3.new(0, head.Size.Y / 2, 0)).Y
	for _, part in character:GetDescendants() do
		if part:IsA("BasePart") and part ~= root and part.Transparency < 1 then
			local corner = part.Size / 2
			local reach = math.abs(part.CFrame.RightVector.Y) * corner.X
				+ math.abs(part.CFrame.UpVector.Y) * corner.Y
				+ math.abs(part.CFrame.LookVector.Y) * corner.Z
			top = math.max(top, root.CFrame:PointToObjectSpace(part.Position).Y + reach)
		end
	end
	model:PivotTo(root.CFrame * CFrame.new(0, top - sink, 0) * facing * CFrame.new(-centre.X, 0, -centre.Z))
	for _, part in model:GetDescendants() do
		if part:IsA("BasePart") then
			part.Anchored = false
			part.Massless = true
			part.CanQuery = false
			local weld = Instance.new("WeldConstraint")
			weld.Part0 = root
			weld.Part1 = part
			weld.Parent = part
		end
	end
	model:SetAttribute("Carried", true)
	-- What its floating tag shows, like the monsters on the base (MonsterTagController).
	model:SetAttribute("TagName", stats.name)
	model:SetAttribute("TagIncome", stats.income)
	model:SetAttribute("TagMutation", entry.mutation)
	model:SetAttribute("TagSize", entry.size)
	model:SetAttribute("TagId", entry.id)
	model.ModelStreamingMode = Enum.ModelStreamingMode.Atomic
	CollectionService:AddTag(model, DinoLife.tag)
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

-- Listeners told whenever a player's plot is rebuilt (BestCatchService), and the dinos on a save's plot.
local plotListeners = {}
function PlotService.onPlotChanged(listener: (Player) -> ())
	table.insert(plotListeners, listener)
end
function PlotService.plotted(data): { any }
	return plotted(data)
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
			local statue = DinoModel.build(entry.id, entry.mutation, position, DinoModel.entryScale(entry))
			-- What its floating tag shows (MonsterTagController draws it, on the few monsters nearest each player).
			statue:SetAttribute("TagName", stats.name)
			statue:SetAttribute("TagIncome", stats.income)
			statue:SetAttribute("TagMutation", entry.mutation)
			statue:SetAttribute("TagSize", entry.size)
			statue.ModelStreamingMode = Enum.ModelStreamingMode.Atomic
			statue:SetAttribute("PlotIndex", plotIndex)
			statue:SetAttribute("DinoKey", entry.key) -- tapping or clicking it picks it up (PlotController)
			CollectionService:AddTag(statue, DinoLife.tag)
			statue.Parent = folder
		end
	end
	folder.Parent = plotModels[plotIndex]
	statueFolders[player] = folder
	for _, listener in plotListeners do
		task.spawn(listener, player)
	end
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
				resize = entry.resize, -- a special's RESIZE choice (DinoStats.resizes)
				income = stats.income,
				oneIn = stats.oneIn,
				onPlot = entry.onPlot,
				sellPrice = sellPrice(entry),
				chonk = entry.chonk or 0,
				food = entry.food or 0,
			})
		end
	end
	table.sort(list, function(a, b)
		return a.income > b.income
	end)
	player:SetAttribute("Income", totalIncome(player, data))
	player:SetAttribute("BaseIncome", baseIncome(player, data))
	player:SetAttribute("BestIncome", bestIncome(data))
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

-- Puts the best monsters on the base and says what happened. When they're already there nothing moves, so monsters
-- that earn the same aren't swapped around for nothing.
local function equipBest(player: Player, data)
	local sorted = table.clone(data.dinos)
	table.sort(sorted, function(a, b)
		return incomeOf(a) > incomeOf(b)
	end)
	local now, best = 0, 0
	for rank, entry in sorted do
		now += if entry.onPlot then incomeOf(entry) else 0
		best += if rank <= capacityOf(data) then incomeOf(entry) else 0
	end
	if best <= now * (1 + 1e-9) then -- a hair over, as adding up in another order can differ in the last digits
		remotes.Notice:FireClient(player, "Your best monsters are already on your base")
		return
	end
	for rank, entry in sorted do
		entry.onPlot = rank <= capacityOf(data)
	end
	changed(player, data)
	remotes.Notice:FireClient(player, `Best monsters equipped! +{Format.cash(best - now)}/s`)
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

-- The Sell Stand: sells the backpack monsters with these keys at once. Monsters on the base and the carried one stay.
local function sellMany(player: Player, data, keys: any)
	if typeof(keys) ~= "table" or #keys > Plot.backpackSize then
		return
	end
	local wanted = {}
	for _, key in keys do
		if typeof(key) == "number" and key == key then -- key ~= key is only true for NaN
			wanted[key] = true
		end
	end
	local sold, cash = 0, 0
	for index = #data.dinos, 1, -1 do
		local entry = data.dinos[index]
		if wanted[entry.key] and not entry.onPlot and entry.key ~= held[player] and DinoStats.sellable(entry.id) then
			sold += 1
			cash += sellPrice(entry)
			table.remove(data.dinos, index)
		end
	end
	if sold > 0 then
		earn(player, data, cash)
		changed(player, data)
		remotes.Notice:FireClient(player, `+{Format.cash(cash)} sold!`)
	end
end

-- Feeds backpack monsters with these keys to a monster, for cash (Config/Chonk). Only what it takes to reach the top level
-- is used. The carried monster and ones already fed stay out of it, and passes' monsters can't be fed or eaten.
local function feed(player: Player, data, target, keys: any)
	if typeof(keys) ~= "table" or #keys > Plot.backpackSize or DinoStats.special(target.id) then
		return
	end
	local level, food = target.chonk or 0, target.food or 0
	if level >= Chonk.maxLevel then
		return
	end
	local wanted = {}
	for _, key in keys do
		if typeof(key) == "number" and key == key then -- key ~= key is only true for NaN
			wanted[key] = true
		end
	end
	-- The tutorial's feeding step is free, once (Config/Tutorial freeFeed).
	local free = TutorialService.isFreeFeed(data, target.key)
	local price = if free then 0 else Chonk.priceOf(incomeOf(target))
	local eaten = {}
	for _, entry in data.dinos do
		if level >= Chonk.maxLevel then
			break
		end
		if wanted[entry.key] and entry ~= target and not entry.onPlot and entry.key ~= held[player]
			and DinoStats.sellable(entry.id) and (entry.chonk or 0) == 0 then
			eaten[entry] = true
			level, food = Chonk.grow(level, food, Chonk.foodOf(target.id, entry.id))
		end
	end
	local amount = 0
	for _ in eaten do
		amount += 1
	end
	if amount == 0 then
		return
	end
	if data.cash < price * amount then
		remotes.Notice:FireClient(player, `You need {Format.cash(price * amount)} to feed these`, true)
		return
	end
	data.cash -= price * amount
	player:SetAttribute("Cash", data.cash)
	for index = #data.dinos, 1, -1 do
		if eaten[data.dinos[index]] then
			table.remove(data.dinos, index)
		end
	end
	if free then
		TutorialService.usedFreeFeed(player, data)
	end
	local before = target.chonk or 0
	target.chonk, target.food = level, food
	changed(player, data)
	local name = DinoStats.describe(target).name
	remotes.Notice:FireClient(player, if level > before then `{name} grew to Chonk {level}!` else `{name} ate {amount}!`)
end

local function onAction(player: Player, action: any, key: any, x: any, z: any)
	local data = PlayerData.get(player)
	if not data then
		return
	end

	if action == "equipBest" then
		equipBest(player, data)
		return
	elseif action == "unequip" then
		setHeld(player, data, nil)
		return
	elseif action == "sellMany" then
		sellMany(player, data, key)
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
		-- Picked up off the base, it goes to the backpack and onto the player's head, ready to put down elsewhere.
		if entry.onPlot and backpackCount(data) < Plot.backpackSize then
			entry.onPlot = false
			changed(player, data)
			setHeld(player, data, entry.key)
		end
	elseif action == "feed" then
		feed(player, data, entry, x)
	elseif action == "resize" and DinoStats.special(entry.id) then
		-- RESIZE on a special: how big it looks, from its normal size up to the biggest size mutation's. Its income
		-- stays as it is.
		if typeof(x) ~= "string" or not DinoStats.findOption(DinoStats.resizes, x) or (entry.resize or "Normal") == x then
			return
		end
		entry.resize = if x == "Normal" then nil else x
		changed(player, data)
		if held[player] == entry.key then
			setHeld(player, data, entry.key) -- the one on the player's head, rebuilt at its new size
		end
	elseif action == "sell" and DinoStats.sellable(entry.id) then
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
-- With no room in either, it's sold. Returns where it went: "plot", "backpack", "carried" or "sold", and its key.
-- Carried (every catch with Config/Plot carryNewCatches, and the tutorial's): it waits in the backpack, on the hotbar,
-- for PlotService.carry, even with the base full: the player picks one up to make room (the tutorial's catches come
-- while the base is still empty).
function PlotService.addCatch(player: Player, catch, carry: boolean?): (string?, number?)
	local data = PlayerData.get(player)
	if not data then
		return nil
	end
	local entry = { key = data.nextDinoKey, id = catch.id, mutation = catch.mutation, size = catch.size, income = catch.income, onPlot = false }
	local result
	if carry and backpackCount(data) < Plot.backpackSize then
		result = "carried"
	elseif #plotted(data) < capacityOf(data) then
		entry.onPlot = true
		result = "plot"
	elseif backpackCount(data) < Plot.backpackSize or catch.income then
		result = "backpack" -- a bought monster always fits: it's never sold off for lack of room
	else
		earn(player, data, sellPrice(entry))
		return "sold"
	end
	data.nextDinoKey += 1
	table.insert(data.dinos, entry)
	changed(player, data)
	return result, entry.key
end

-- Puts this backpack monster on the player's head to be placed, like equipping it from the hotbar.
function PlotService.carry(player: Player, key: number)
	local data = PlayerData.get(player)
	local entry = data and findEntry(data, key)
	if entry and not entry.onPlot then
		setHeld(player, data, key)
	end
end

-- Takes the carried monster off the player's head; it stays in the backpack, on the hotbar.
function PlotService.putAway(player: Player)
	local data = PlayerData.get(player)
	if data and held[player] then
		setHeld(player, data, nil)
	end
end

-- Gives a Config/Specials monster, its income fixed now at its share of the player's best, and returns that income.
-- The caller saves the data.
function PlotService.addSpecial(player: Player, data, special): number
	local income = math.max(bestIncome(data), special.minimumIncome) * special.share
	PlotService.addCatch(player, { id = special.id, income = income })
	PlotService.notify(player, `{special.name} joined you! +{Format.cash(income)}/s`)
	return income
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
		character:WaitForChild("Head", 5)
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
			data.peakIncome = math.max(data.peakIncome, income) -- the HIGHEST $/S leaderboard
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
