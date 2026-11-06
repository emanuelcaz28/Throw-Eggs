-- Builds a squat rack and an XP upgrade pad at every base, and runs training. Stepping on your own
-- rack's pad locks you in under the bar; reps come automatically until you press STOP. Everyone sees
-- every rack, but only the base's owner trains there. The orange button in front of it sells more XP
-- per rep, and while training a bubble now and then offers a double rep. The rack and the button are
-- Blender models (BaseKit), and each base shows the rack its owner's upgrades have earned (Config/Training rackModels). Everything is decided here on the server; the client reads the Player attributes set in
-- publish and can only ask through TrainingRemotes (StopTraining, TapBubble).
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Training = require(ReplicatedStorage.Shared.Config.Training)
local BaseKit = require(ReplicatedStorage.Shared.BaseKit)
local Format = require(ReplicatedStorage.Shared.Format)
local Plot = require(ReplicatedStorage.Shared.Config.Plot)
local Roles = require(ReplicatedStorage.Shared.Roles)
local IndexService = require(script.Parent.IndexService)
local PlayerData = require(script.Parent.PlayerData)
local PlotService = require(script.Parent.PlotService)
local Shop = require(ReplicatedStorage.Shared.Config.Shop)
local World = require(ReplicatedStorage.Shared.World)

local TrainingService = {}

local TICK = 0.25
local PAD_TOP = 0 -- the lifter stands on the ground, inside the rack's dashed circle
local BAR_PARTS = { Bar = true, Plate = true } -- the loaded bar, hidden while it's on someone's shoulders

local remotes: { [string]: RemoteEvent } = {}
local training: { [Player]: number } = {} -- the base whose rack each player is training at
local repProgress: { [Player]: number } = {}
local wasOnXpPad: { [Player]: boolean } = {}
local nextBubbleAt: { [Player]: number } = {}
local activeBubble: { [Player]: { id: number, expires: number } } = {}
local bubbleCount = 0
local rackBarParts: { [number]: { BasePart } } = {} -- per base
local shownRacks: { [number]: Model } = {} -- the rack standing at each base
local FACING = Vector3.new(0, 0, -1) -- out of the base, the way the lifter looks
local rng = Random.new()

local function makeRemotes()
	local folder = Instance.new("Folder")
	folder.Name = "TrainingRemotes"
	for _, name in { "StopTraining", "BubbleShown", "TapBubble", "Boosted" } do
		local remote = Instance.new("RemoteEvent")
		remote.Name = name
		remote.Parent = folder
		remotes[name] = remote
	end
	folder.Parent = ReplicatedStorage
end

-- Stands a rack at a base in place of the one there, and notes its loaded bar. It faces out of the base, like the lifter.
local function placeRack(parent: Instance, plotIndex: number, name: string)
	local rackAt = Training.rackPosition(plotIndex)
	local rack = BaseKit.place(name, CFrame.lookAt(rackAt, rackAt + FACING), parent)
	local barParts = {}
	if rack then
		Roles.lightUp(rack)
		for _, part in rack:GetDescendants() do
			if part:IsA("BasePart") then
				if BAR_PARTS[part.Name] then
					table.insert(barParts, part)
				end
				if part.Name == "Dash" then
					part.CanCollide = false
				end
			end
		end
	end
	if shownRacks[plotIndex] then
		shownRacks[plotIndex]:Destroy()
	end
	shownRacks[plotIndex] = rack
	rackBarParts[plotIndex] = barParts
end

local function buildRack(parent: Instance, plotIndex: number)
	local model = Instance.new("Model")
	model.Name = `Rack{plotIndex}`

	placeRack(model, plotIndex, Training.rackModels[1].model)

	local buttonAt = Training.xpPadPosition(plotIndex)
	BaseKit.place("base_XpButton", CFrame.lookAt(buttonAt, buttonAt + FACING), model)

	model.Parent = parent
end

local function buildRacks()
	local folder = Instance.new("Folder")
	folder.Name = "Racks"
	for plotIndex in Plot.positions do
		buildRack(folder, plotIndex)
	end
	folder.Parent = workspace
end

local function rootOf(player: Player): (BasePart?, Humanoid?)
	local character = player.Character
	local root = character and character:FindFirstChild("HumanoidRootPart") :: BasePart?
	local humanoid = character and character:FindFirstChildOfClass("Humanoid")
	if not root or not humanoid or humanoid.Health <= 0 then
		return nil, nil
	end
	return root, humanoid
end

-- The x2 Training pass, times the x2 XP from completing a world in the Index while it runs.
local function passMultiplier(player: Player): number
	local pass = if player:GetAttribute("HasDoubleTraining") then Shop.doubleTraining.multiplier else 1
	local data = PlayerData.get(player)
	return pass * (if data then IndexService.xpMultiplier(data) else 1)
end

-- Power each full bar gives: the rack's tier, doubled by the x2 Power pass.
local function powerPerBar(player: Player, data): number
	local pass = if player:GetAttribute("HasDoublePower") then Shop.doublePower.multiplier else 1
	return Training.powerPerBar(data.xpUpgrades) * pass
end

local function xpPerRep(player: Player, data): number
	return Training.xpPerRepFor(data.xpUpgrades) * passMultiplier(player)
end

-- The starting power, plus what full bars gave, plus power bought in Shop packs.
local function throwPower(data): number
	return Training.startPower + data.trainedPower + data.bonusPower
end

local function publish(player: Player, data: { [string]: any })
	player:SetAttribute("ThrowPower", throwPower(data))
	player:SetAttribute("TrainingLevel", data.trainingLevel)
	player:SetAttribute("TrainingXp", data.trainingXp)
	player:SetAttribute("TrainingXpNeeded", Training.xpForNextBar(throwPower(data)))
	player:SetAttribute("XpPerRep", xpPerRep(player, data))
	player:SetAttribute("NextXpPerRep", Training.xpPerRepFor(data.xpUpgrades + 1) * passMultiplier(player))
	player:SetAttribute("XpUpgradePrice", Training.xpUpgradePrice(data.xpUpgrades))
	local upgradesLeft, nextPower = Training.nextTier(data.xpUpgrades)
	player:SetAttribute("PowerPerBar", powerPerBar(player, data))
	player:SetAttribute("NextPowerPerBar", nextPower * (powerPerBar(player, data) / Training.powerPerBar(data.xpUpgrades)))
	player:SetAttribute("UpgradesToNextTier", upgradesLeft)
end

-- Each full bar gives the rack's power per bar. The next bar's XP follows the power reached (Training.xpForNextBar).
local function addXp(player: Player, data, amount: number)
	data.trainingXp += amount
	local needed = Training.xpForNextBar(throwPower(data))
	while data.trainingXp >= needed do
		data.trainingXp -= needed
		data.trainingLevel += 1
		data.trainedPower += powerPerBar(player, data)
		needed = Training.xpForNextBar(throwPower(data))
	end
end

local function updateRackBar(plotIndex: number?)
	local parts = plotIndex and rackBarParts[plotIndex]
	if not parts then
		return
	end
	local inUse = false
	for _, rack in training do
		if rack == plotIndex then
			inUse = true
		end
	end
	for _, part in parts do
		part.Transparency = if inUse then 1 else 0
	end
end

-- Shows the rack this many upgrades has earned at a base. A model that hasn't been imported yet is skipped for the
-- best one that has.
local function showRack(plotIndex: number, upgrades: number)
	local earned = Training.rackFor(upgrades)
	for index = table.find(Training.rackModels, earned) :: number, 1, -1 do
		local name = Training.rackModels[index].model
		if BaseKit.has(name) then
			local shown = shownRacks[plotIndex]
			if not shown or shown.Name ~= name then
				placeRack(workspace.Racks[`Rack{plotIndex}`], plotIndex, name)
				updateRackBar(plotIndex)
			end
			return
		end
	end
end

local function scheduleBubble(player: Player)
	local bubble = Training.bubble
	nextBubbleAt[player] = os.clock() + rng:NextNumber(bubble.minDelay, bubble.maxDelay)
end

-- Puts the player under the bar, facing out, and holds them there.
local function startTraining(player: Player, plotIndex: number, root: BasePart, humanoid: Humanoid)
	training[player] = plotIndex
	repProgress[player] = 0
	scheduleBubble(player)
	local spot = Training.rackPosition(plotIndex) + Vector3.new(0, PAD_TOP + humanoid.HipHeight + root.Size.Y / 2, 0)
	player.Character:PivotTo(CFrame.lookAt(spot, spot + FACING))
	root.AssemblyLinearVelocity = Vector3.zero
	root.Anchored = true
	player:SetAttribute("IsTraining", true)
	updateRackBar(plotIndex)
end

-- Lets the player go. With moveOut, they're put down in front of the rack, off the pad, so
-- training doesn't start again straight away.
local function stopTraining(player: Player, moveOut: boolean)
	local plotIndex = training[player]
	if not plotIndex then
		return
	end
	training[player] = nil
	activeBubble[player] = nil
	player:SetAttribute("IsTraining", false)
	local root, humanoid = rootOf(player)
	if root and humanoid then
		root.Anchored = false
		if moveOut then
			local spot = Training.rackPosition(plotIndex) + Training.rack.stopOffset + Vector3.new(0, PAD_TOP + humanoid.HipHeight + root.Size.Y / 2, 0)
			player.Character:PivotTo(CFrame.lookAt(spot, spot + FACING))
		end
	end
	updateRackBar(plotIndex)
end

local function tryBuyXpUpgrade(player: Player, data)
	local price = Training.xpUpgradePrice(data.xpUpgrades)
	if data.cash < price then
		PlotService.notify(player, `You need {Format.cash(price)} for this upgrade`, true)
		return
	end
	local before = powerPerBar(player, data)
	local rackBefore = Training.rackFor(data.xpUpgrades)
	data.cash -= price
	data.xpUpgrades += 1
	player:SetAttribute("Cash", data.cash)
	publish(player, data)
	local now = powerPerBar(player, data)
	-- One notice: a second would replace it on screen.
	local rack = Training.rackFor(data.xpUpgrades)
	local opening = if rack ~= rackBefore then `New rack: {rack.name}!` else "Upgraded!"
	if now > before then
		PlotService.notify(player, `{opening} Every full bar now gives {Format.short(now)} power`)
	else
		local left, nextPower = Training.nextTier(data.xpUpgrades)
		PlotService.notify(player, `{opening} {left} more for {Format.short(nextPower)} power per bar`)
	end
end

local function step(dt: number)
	local rack = Training.rack
	local xpPad = Training.xpUpgrade
	local owned: { [number]: boolean } = {}
	for _, player in Players:GetPlayers() do
		local data = PlayerData.get(player)
		local plotIndex = player:GetAttribute("PlotIndex")
		if data then
			if plotIndex then
				owned[plotIndex] = true
				showRack(plotIndex, data.xpUpgrades)
			end
			local root, humanoid = rootOf(player)
			if training[player] and (not root or training[player] ~= plotIndex) then
				stopTraining(player, false)
			elseif not training[player] and root and humanoid and plotIndex then
				if World.isOnPad(player, Training.rackPosition(plotIndex), rack.padRadius, rack.padHeight) then
					startTraining(player, plotIndex, root, humanoid)
				end
			end

			-- One purchase per step onto the player's own XP pad.
			local onXpPad = plotIndex ~= nil and World.isOnPad(player, Training.xpPadPosition(plotIndex), xpPad.padRadius, xpPad.padHeight)
			if onXpPad and not wasOnXpPad[player] then
				tryBuyXpUpgrade(player, data)
			end
			wasOnXpPad[player] = onXpPad

			if training[player] then
				local progress = (repProgress[player] or 0) + dt
				local reps = math.floor(progress / Training.repInterval)
				repProgress[player] = progress - reps * Training.repInterval
				if reps > 0 then
					addXp(player, data, xpPerRep(player, data) * reps)
					publish(player, data)
				end

				local bubble = activeBubble[player]
				if bubble and os.clock() > bubble.expires then
					activeBubble[player] = nil
					scheduleBubble(player)
				elseif not bubble and os.clock() >= (nextBubbleAt[player] or math.huge) then
					bubbleCount += 1
					activeBubble[player] = { id = bubbleCount, expires = os.clock() + Training.bubble.lifetime }
					remotes.BubbleShown:FireClient(player, bubbleCount)
				end
			end
		end
	end
	-- A base nobody owns goes back to the first rack.
	for plotIndex in shownRacks do
		if not owned[plotIndex] then
			showRack(plotIndex, 0)
		end
	end
end

local function onTapBubble(player: Player, id: any)
	local bubble = activeBubble[player]
	local data = PlayerData.get(player)
	if not bubble or bubble.id ~= id or os.clock() > bubble.expires or not data then
		return
	end
	activeBubble[player] = nil
	scheduleBubble(player)
	addXp(player, data, xpPerRep(player, data) * Training.bubble.multiplier)
	publish(player, data)
	remotes.Boosted:FireAllClients(player)
end

-- The server's copy of a player's Throw Power, for the throw system to use.
function TrainingService.getThrowPower(player: Player): number?
	local data = PlayerData.get(player)
	return data and throwPower(data)
end

-- Adds Throw Power from a Shop pack. The caller saves the data.
function TrainingService.addBonusPower(player: Player, data, amount: number)
	data.bonusPower += amount
	publish(player, data)
end

-- Saves from before bars kept their power as levels: 20 a level.
local function onLoaded(player: Player, data)
	if data.trainedPower < 0 then
		data.trainedPower = 20 * (data.trainingLevel - 1)
	end
	publish(player, data)
end

function TrainingService.start()
	makeRemotes()
	buildRacks()
	PlayerData.onLoaded(onLoaded)
	-- The x2 Power pass can arrive after loading (bought, or checked late): refresh power per bar.
	Players.PlayerAdded:Connect(function(player)
		player:GetAttributeChangedSignal("HasDoublePower"):Connect(function()
			local data = PlayerData.get(player)
			if data then
				publish(player, data)
			end
		end)
	end)
	remotes.StopTraining.OnServerEvent:Connect(function(player)
		stopTraining(player, true)
	end)
	remotes.TapBubble.OnServerEvent:Connect(onTapBubble)
	Players.PlayerRemoving:Connect(function(player)
		local plotIndex = training[player]
		training[player] = nil
		repProgress[player] = nil
		wasOnXpPad[player] = nil
		nextBubbleAt[player] = nil
		activeBubble[player] = nil
		updateRackBar(plotIndex)
	end)
	task.spawn(function()
		while true do
			step(task.wait(TICK))
		end
	end)
end

return TrainingService
