-- Builds the squat rack and the XP upgrade pad, and runs training. Stepping on the rack's pad
-- locks the player in under the bar; reps come automatically until they press STOP. The orange
-- pad beside it sells more XP per rep, and while training a bubble now and then offers a double
-- rep. Everything is decided here on the server; the client reads the Player attributes set in
-- publish and can only ask through TrainingRemotes (StopTraining, TapBubble).
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Training = require(ReplicatedStorage.Shared.Config.Training)
local Format = require(ReplicatedStorage.Shared.Format)
local PlayerData = require(script.Parent.PlayerData)
local PlotService = require(script.Parent.PlotService)
local Shop = require(ReplicatedStorage.Shared.Config.Shop)
local World = require(script.Parent.World)

local TrainingService = {}

local TICK = 0.25
local PAD_COLOR = Color3.fromRGB(226, 142, 58)
local XP_PAD_COLOR = Color3.fromRGB(245, 170, 40)
local FRAME_COLOR = Color3.fromRGB(70, 74, 82)
local BAR_COLOR = Color3.fromRGB(200, 205, 212)
local PLATE_COLOR = Color3.fromRGB(40, 42, 48)

-- Rack shape, in studs from the pad's centre. The lifter stands at the centre facing +Z.
local UPRIGHT_GAP = 4.2 -- from the centre to each upright
local UPRIGHT_HEIGHT = 8
local RACK_BAR_HEIGHT = 5.3
local RACK_BAR_LENGTH = 12
local PLATE_OFFSETS = { 4.9, 5.4 } -- from the centre, on both sides
local PAD_TOP = 0.5

local remotes: { [string]: RemoteEvent } = {}
local training: { [Player]: boolean } = {}
local repProgress: { [Player]: number } = {}
local wasOnXpPad: { [Player]: boolean } = {}
local nextBubbleAt: { [Player]: number } = {}
local activeBubble: { [Player]: { id: number, expires: number } } = {}
local bubbleCount = 0
local rackBarParts: { BasePart } = {}
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

local function makeCylinder(parent: Instance, name: string, size: Vector3, position: Vector3, color: Color3): Part
	local part = World.makePart(parent, name, size, CFrame.new(position), color)
	part.Shape = Enum.PartType.Cylinder -- along X
	part.Material = Enum.Material.Metal
	return part
end

local function buildStation()
	local station = Training.station
	local origin = station.position

	local model = Instance.new("Model")
	model.Name = "TrainingStation"
	local pad = World.makePad(model, origin, station.padRadius, PAD_COLOR)

	for _, side in { -1, 1 } do
		local x = side * UPRIGHT_GAP
		World.makePart(model, "RackFoot", Vector3.new(1.6, 0.4, 3), CFrame.new(origin + Vector3.new(x, PAD_TOP + 0.2, 0)), FRAME_COLOR)
		World.makePart(
			model,
			"Upright",
			Vector3.new(0.8, UPRIGHT_HEIGHT, 0.8),
			CFrame.new(origin + Vector3.new(x, PAD_TOP + UPRIGHT_HEIGHT / 2, 0)),
			FRAME_COLOR
		)
		World.makePart(
			model,
			"Hook",
			Vector3.new(0.6, 0.3, 0.9),
			CFrame.new(origin + Vector3.new(x - side * 0.6, RACK_BAR_HEIGHT - 0.3, 0)),
			FRAME_COLOR
		)
	end

	-- The loaded bar rests on the hooks; it disappears while someone has it on their shoulders.
	local bar = makeCylinder(
		model,
		"RackBar",
		Vector3.new(RACK_BAR_LENGTH, 0.35, 0.35),
		origin + Vector3.new(0, RACK_BAR_HEIGHT, 0),
		BAR_COLOR
	)
	table.insert(rackBarParts, bar)
	for _, offset in PLATE_OFFSETS do
		for _, side in { -1, 1 } do
			local plate = makeCylinder(
				model,
				"RackPlate",
				Vector3.new(0.4, 2.8, 2.8),
				origin + Vector3.new(side * offset, RACK_BAR_HEIGHT, 0),
				PLATE_COLOR
			)
			table.insert(rackBarParts, plate)
		end
	end

	local signAnchor = World.makePart(model, "SignAnchor", Vector3.one, CFrame.new(origin + Vector3.new(0, UPRIGHT_HEIGHT + 2, 0)), FRAME_COLOR)
	signAnchor.Transparency = 1
	signAnchor.CanCollide = false
	World.makeSign(signAnchor, "TRAIN HERE", 0, 150, 220)

	local xpPad = World.makePad(model, Training.xpUpgrade.position, Training.xpUpgrade.padRadius, XP_PAD_COLOR)
	xpPad.Name = "XpUpgradePad"

	model.PrimaryPart = pad
	model.Parent = workspace
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

local function passMultiplier(player: Player): number
	return if player:GetAttribute("HasDoubleTraining") then Shop.doubleTraining.multiplier else 1
end

local function xpPerRep(player: Player, data): number
	return Training.xpPerRepFor(data.xpUpgrades) * passMultiplier(player)
end

local function publish(player: Player, data: { [string]: any })
	player:SetAttribute("ThrowPower", Training.powerForLevel(data.trainingLevel))
	player:SetAttribute("TrainingLevel", data.trainingLevel)
	player:SetAttribute("TrainingXp", data.trainingXp)
	player:SetAttribute("TrainingXpNeeded", Training.xpToNextLevel(data.trainingLevel))
	player:SetAttribute("XpPerRep", xpPerRep(player, data))
	player:SetAttribute("NextXpPerRep", Training.xpPerRepFor(data.xpUpgrades + 1) * passMultiplier(player))
	player:SetAttribute("XpUpgradePrice", Training.xpUpgradePrice(data.xpUpgrades))
end

local function addXp(data, amount: number)
	data.trainingXp += amount
	while data.trainingXp >= Training.xpToNextLevel(data.trainingLevel) do
		data.trainingXp -= Training.xpToNextLevel(data.trainingLevel)
		data.trainingLevel += 1
	end
end

local function updateRackBar()
	local anyone = next(training) ~= nil
	for _, part in rackBarParts do
		part.Transparency = if anyone then 1 else 0
	end
end

local function scheduleBubble(player: Player)
	local bubble = Training.bubble
	nextBubbleAt[player] = os.clock() + rng:NextNumber(bubble.minDelay, bubble.maxDelay)
end

-- Puts the player under the bar, facing out, and holds them there.
local function startTraining(player: Player, root: BasePart, humanoid: Humanoid)
	training[player] = true
	repProgress[player] = 0
	scheduleBubble(player)
	local spot = Training.station.position + Vector3.new(0, PAD_TOP + humanoid.HipHeight + root.Size.Y / 2, 0)
	player.Character:PivotTo(CFrame.lookAt(spot, spot + Vector3.new(0, 0, 1)))
	root.AssemblyLinearVelocity = Vector3.zero
	root.Anchored = true
	player:SetAttribute("IsTraining", true)
	updateRackBar()
end

-- Lets the player go. With moveOut, they're put down in front of the rack, off the pad, so
-- training doesn't start again straight away.
local function stopTraining(player: Player, moveOut: boolean)
	if not training[player] then
		return
	end
	training[player] = nil
	activeBubble[player] = nil
	player:SetAttribute("IsTraining", false)
	local root, humanoid = rootOf(player)
	if root and humanoid then
		root.Anchored = false
		if moveOut then
			local station = Training.station
			local spot = station.position + Vector3.new(0, PAD_TOP + humanoid.HipHeight + root.Size.Y / 2, station.stopDistance)
			player.Character:PivotTo(CFrame.lookAt(spot, spot + Vector3.new(0, 0, 1)))
		end
	end
	updateRackBar()
end

local function tryBuyXpUpgrade(player: Player, data)
	local price = Training.xpUpgradePrice(data.xpUpgrades)
	if data.cash < price then
		PlotService.notify(player, `You need {Format.cash(price)} for more XP per rep`)
		return
	end
	data.cash -= price
	data.xpUpgrades += 1
	player:SetAttribute("Cash", data.cash)
	publish(player, data)
	PlotService.notify(player, `Upgraded! Every rep now gives {Format.short(xpPerRep(player, data))} XP`)
end

local function step(dt: number)
	local station = Training.station
	local xpPad = Training.xpUpgrade
	for _, player in Players:GetPlayers() do
		local data = PlayerData.get(player)
		if data then
			local root, humanoid = rootOf(player)
			if training[player] and not root then
				stopTraining(player, false)
			elseif not training[player] and root and humanoid then
				if World.isOnPad(player, station.position, station.padRadius, station.padHeight) then
					startTraining(player, root, humanoid)
				end
			end

			-- One purchase per step onto the XP pad.
			local onXpPad = World.isOnPad(player, xpPad.position, xpPad.padRadius, xpPad.padHeight)
			if onXpPad and not wasOnXpPad[player] then
				tryBuyXpUpgrade(player, data)
			end
			wasOnXpPad[player] = onXpPad

			if training[player] then
				local progress = (repProgress[player] or 0) + dt
				local reps = math.floor(progress / Training.repInterval)
				repProgress[player] = progress - reps * Training.repInterval
				if reps > 0 then
					addXp(data, xpPerRep(player, data) * reps)
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
end

local function onTapBubble(player: Player, id: any)
	local bubble = activeBubble[player]
	local data = PlayerData.get(player)
	if not bubble or bubble.id ~= id or os.clock() > bubble.expires or not data then
		return
	end
	activeBubble[player] = nil
	scheduleBubble(player)
	addXp(data, xpPerRep(player, data) * Training.bubble.multiplier)
	publish(player, data)
	remotes.Boosted:FireAllClients(player)
end

-- The server's copy of a player's Throw Power, for the throw system to use.
function TrainingService.getThrowPower(player: Player): number?
	local data = PlayerData.get(player)
	return data and Training.powerForLevel(data.trainingLevel)
end

function TrainingService.start()
	makeRemotes()
	buildStation()
	PlayerData.onLoaded(publish)
	remotes.StopTraining.OnServerEvent:Connect(function(player)
		stopTraining(player, true)
	end)
	remotes.TapBubble.OnServerEvent:Connect(onTapBubble)
	Players.PlayerRemoving:Connect(function(player)
		training[player] = nil
		repProgress[player] = nil
		wasOnXpPad[player] = nil
		nextBubbleAt[player] = nil
		activeBubble[player] = nil
		updateRackBar()
	end)
	task.spawn(function()
		while true do
			step(task.wait(TICK))
		end
	end)
end

return TrainingService
