-- Shows Throw Power at all times, and while training the level/XP bar, the STOP button, the
-- x2 bubble and the pop-ups (+XP, LEVEL UP!, the 2X XP moment). Also writes the price on the XP upgrade pad. Display and
-- requests only: every value is read from attributes the server sets on the local player.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")

local BoostMoment = require(script.Parent.BoostMoment)
local Format = require(ReplicatedStorage.Shared.Format)
local HudStyle = require(ReplicatedStorage.Shared.HudStyle)
local Plot = require(ReplicatedStorage.Shared.Config.Plot)
local Pop = require(ReplicatedStorage.Shared.Config.Pop)
local Sfx = require(script.Parent.Sfx)
local PopText = require(ReplicatedStorage.Shared.PopText)
local Training = require(ReplicatedStorage.Shared.Config.Training)
local UiKit = require(ReplicatedStorage.Shared.UiKit)

local player = Players.LocalPlayer

local TrainingController = {}

local POWER = Color3.fromRGB(90, 190, 255)
local TEXT = Color3.new(1, 1, 1)
local TAU = 2 * math.pi
local BUBBLE_SIZE = 112
local POWER_HEIGHT = 52 -- before scaling for small screens
local POWER_ABOVE_BOTTOM = 98 -- clears the cash and $/s beneath it

local function buildHud()
	local gui = Instance.new("ScreenGui")
	gui.Name = "TrainingHud"
	gui.ResetOnSpawn = false
	gui.Parent = player:WaitForChild("PlayerGui")

	-- Always on screen, bottom left, just above the cash (PlotController draws that).
	local powerStat, power = HudStyle.stat(gui, "⚡", POWER, POWER_HEIGHT, "bolt")
	powerStat.Name = "PowerStat"
	powerStat.AnchorPoint = Vector2.new(0, 1)
	powerStat.Position = UDim2.new(0, 16, 1, -POWER_ABOVE_BOTTOM * HudStyle.scale())

	-- Only while training: the level bar with STOP above it, bottom centre.
	local training = Instance.new("Frame")
	training.Name = "TrainingGroup"
	training.BackgroundTransparency = 1
	training.AnchorPoint = Vector2.new(0.5, 1)
	training.Position = UDim2.new(0.5, 0, 1, -16)
	training.Size = UDim2.fromOffset(640, 150)
	training.Parent = gui
	local trainingScale = Instance.new("UIScale")
	trainingScale.Scale = UiKit.scale()
	trainingScale.Parent = training

	local bar = Instance.new("Frame")
	bar.Name = "LevelBar"
	bar.AnchorPoint = Vector2.new(0.5, 1)
	bar.Position = UDim2.new(0.5, 0, 1, 0)
	bar.Size = UDim2.fromOffset(640, 60)
	bar.BackgroundColor3 = UiKit.DEEP
	bar.Visible = false
	bar.Parent = training
	UiKit.corner(bar, 22)
	UiKit.stroke(bar, 5)
	local fill = Instance.new("Frame")
	fill.Name = "Fill"
	fill.Size = UDim2.fromScale(0, 1)
	fill.Parent = bar
	UiKit.gradient(fill, { "#8ff0ff", "#2fb6e6" })
	UiKit.corner(fill, 18)
	local level = UiKit.text(bar, "", 32, nil, Enum.TextXAlignment.Left)
	level.Position = UDim2.fromOffset(20, 0)
	level.Size = UDim2.new(0.5, -20, 1, 0)
	level.ZIndex = 2
	local xp = UiKit.text(bar, "", 32, nil, Enum.TextXAlignment.Right)
	xp.AnchorPoint = Vector2.new(1, 0)
	xp.Position = UDim2.new(1, -20, 0, 0)
	xp.Size = UDim2.new(0.5, -20, 1, 0)
	xp.ZIndex = 2

	local stop = UiKit.button(training, "STOP", "red", 200, 70, 36)
	stop.Name = "Stop"
	stop.AnchorPoint = Vector2.new(0.5, 0)
	stop.Position = UDim2.new(0.5, 0, 0, 0)
	stop.Visible = false

	local bubble = Instance.new("TextButton")
	bubble.Name = "Bubble"
	bubble:SetAttribute("NoClickSound", true) -- the 2X XP moment has its own
	bubble.AnchorPoint = Vector2.new(0.5, 0.5)
	bubble.Size = UDim2.fromOffset(BUBBLE_SIZE, BUBBLE_SIZE)
	bubble.AutoButtonColor = false
	bubble.FontFace = UiKit.FONT
	bubble.Text = `x{Training.bubble.multiplier}`
	bubble.TextSize = 50
	bubble.TextColor3 = TEXT
	bubble.Visible = false
	bubble.ZIndex = 3
	bubble.Parent = gui
	UiKit.gradient(bubble, { "#e3b8ff", "#9a4ff0" })
	UiKit.corner(bubble, BUBBLE_SIZE)
	UiKit.stroke(bubble, 6, TEXT)
	local bubbleText = Instance.new("UIStroke")
	bubbleText.ApplyStrokeMode = Enum.ApplyStrokeMode.Contextual
	bubbleText.Color = UiKit.INK
	bubbleText.Thickness = 5
	bubbleText.Parent = bubble

	return {
		power = power,
		bar = bar,
		fill = fill,
		level = level,
		xp = xp,
		stop = stop,
		bubble = bubble,
	}
end

-- Price and reward floating over the XP upgrade pad at the player's own base, so only they see
-- their numbers (Config/Training xpUpgrade.sign). It hangs on its own point in the world, not on the pad: the pad
-- unloads when the player goes far (map streaming, every throw) and the words used to vanish with it [Owner,
-- 2026-11-08: "I don't usually see the text above the pad"].
local function padLine(parent: Instance, size: number, order: number): (TextLabel, UIGradient)
	local look = Training.xpUpgrade.sign
	local label = Instance.new("TextLabel")
	label.BackgroundTransparency = 1
	label.FontFace = UiKit.FONT
	label.TextSize = size
	label.TextColor3 = TEXT
	label.Text = ""
	label.Size = UDim2.new(1, 0, 0, size + look.outline * 2)
	label.LayoutOrder = order
	label.Parent = parent
	HudStyle.outline(label, look.outline)
	local gradient = Instance.new("UIGradient")
	gradient.Rotation = 90
	gradient.Parent = label
	return label, gradient
end

local function colours(gradient: UIGradient, pair)
	gradient.Color = ColorSequence.new(Color3.fromHex(pair[1]), Color3.fromHex(pair[2]))
end

local function buildPadSign()
	local look = Training.xpUpgrade.sign
	local point = Instance.new("Attachment")
	point.Name = "XpUpgradeSignPoint"
	point.Parent = workspace.Terrain -- never streamed out

	local sign = Instance.new("BillboardGui")
	sign.Name = "XpUpgradeSign"
	sign.Size = UDim2.fromOffset(look.size.X, look.size.Y)
	sign.MaxDistance = look.maxDistance
	sign.LightInfluence = 0
	sign.ResetOnSpawn = false
	sign.Enabled = false
	sign.Adornee = point
	sign.Parent = player:WaitForChild("PlayerGui")

	local root = Instance.new("Frame")
	root.BackgroundTransparency = 1
	root.AnchorPoint = Vector2.new(0.5, 1) -- springs from its bottom middle, over the pad
	root.Position = UDim2.fromScale(0.5, 1)
	root.Size = UDim2.fromScale(1, 1)
	root.Parent = sign
	local punch = Instance.new("UIScale")
	punch.Parent = root
	local list = Instance.new("UIListLayout")
	list.HorizontalAlignment = Enum.HorizontalAlignment.Center
	list.VerticalAlignment = Enum.VerticalAlignment.Bottom
	list.SortOrder = Enum.SortOrder.LayoutOrder
	list.Parent = root

	local price, priceColour = padLine(root, look.priceText, 1)
	local pulse = Instance.new("UIScale")
	pulse.Parent = price
	-- Each upgrade raises XP per squat (Training.xpPerRepGrowth): what it will be after this one.
	local xp, xpColour = padLine(root, look.xpText, 2)
	colours(xpColour, look.xp)
	local rack, rackColour = padLine(root, look.rackText, 3)
	colours(rackColour, look.rack)

	-- A short hold of E buys one, the same request as the ready pop-up's UPGRADE (the server checks the price).
	local settings = Training.xpUpgrade.prompt
	local promptPoint = Instance.new("Attachment")
	promptPoint.Name = "XpUpgradePromptPoint"
	promptPoint.Parent = workspace.Terrain
	local prompt = Instance.new("ProximityPrompt")
	prompt.Name = "XpUpgradePrompt"
	prompt.ActionText = "Upgrade"
	prompt.ObjectText = "XP per squat"
	prompt.KeyboardKeyCode = Enum.KeyCode.E
	prompt.HoldDuration = settings.holdSeconds
	prompt.MaxActivationDistance = settings.reach
	prompt.RequiresLineOfSight = false
	prompt.Enabled = false
	prompt.Parent = promptPoint

	return {
		point = point,
		promptPoint = promptPoint,
		prompt = prompt,
		sign = sign,
		punch = punch,
		price = price,
		priceColour = priceColour,
		pulse = pulse,
		xp = xp,
		rack = rack,
	}
end

function TrainingController.start()
	local remotes = ReplicatedStorage:WaitForChild("TrainingRemotes")
	local hud = buildHud()
	local lastLevel: number? = nil
	local lastXp: number? = nil
	local lastPower: number? = nil
	local bubbleId: number? = nil
	local tappedAt = Vector2.zero -- the middle of the bubble last tapped, for the moment when the server confirms it

	local function render()
		local power = player:GetAttribute("ThrowPower")
		local level = player:GetAttribute("TrainingLevel")
		local xp = player:GetAttribute("TrainingXp")
		local needed = player:GetAttribute("TrainingXpNeeded")
		if not (power and level and xp and needed) then
			return
		end
		local isTraining = player:GetAttribute("IsTraining") == true

		hud.power.Text = Format.commas(power)
		hud.bar.Visible = isTraining
		hud.stop.Visible = isTraining
		hud.level.Text = `Level {Format.short(level)}`
		hud.xp.Text = `{Format.short(xp)} / {Format.short(needed)}`
		hud.fill:TweenSize(UDim2.fromScale(math.clamp(xp / needed, 0, 1), 1), "Out", "Quad", 0.2, true)

		-- Each squat's XP floats from above STOP, which sits on the bar, so phones don't get the words over the button.
		-- A full bar's +POWER slams in over Throw Power instead (GameFeelJuice).
		if isTraining and lastXp and lastLevel and level == lastLevel and xp > lastXp then
			PopText.float(`+{Format.short(xp - lastXp)} XP`, Pop.colors.xp, PopText.above(hud.stop))
		end
		if not isTraining then
			hud.bubble.Visible = false
			bubbleId = nil
		end
		lastLevel, lastXp, lastPower = level, xp, power
	end

	hud.stop.Activated:Connect(function()
		remotes.StopTraining:FireServer()
	end)

	remotes.BubbleShown.OnClientEvent:Connect(function(id: number)
		bubbleId = id
		hud.bubble.Position = UDim2.fromScale(0.3 + math.random() * 0.4, 0.3 + math.random() * 0.25)
		hud.bubble.Size = UDim2.fromOffset(BUBBLE_SIZE * 0.4, BUBBLE_SIZE * 0.4)
		hud.bubble.Visible = true
		TweenService:Create(hud.bubble, TweenInfo.new(0.25, Enum.EasingStyle.Back), { Size = UDim2.fromOffset(BUBBLE_SIZE, BUBBLE_SIZE) }):Play()
		task.delay(Training.bubble.lifetime, function()
			if bubbleId == id then
				bubbleId = nil
				hud.bubble.Visible = false
			end
		end)
	end)
	hud.bubble.Activated:Connect(function()
		if bubbleId then
			remotes.TapBubble:FireServer(bubbleId)
			bubbleId = nil
			tappedAt = hud.bubble.AbsolutePosition + hud.bubble.AbsoluteSize / 2
			hud.bubble.Visible = false
		end
	end)
	-- The server has the last word on a tap: the moment plays when it says the double rep landed.
	remotes.Boosted.OnClientEvent:Connect(function(booster: Player, gained: number)
		if booster == player then
			BoostMoment.play(tappedAt, hud.bar, Training.bubble.multiplier, Format.short(gained))
		end
	end)

	player.AttributeChanged:Connect(render)
	render()

	task.spawn(function()
		local pad = buildPadSign()
		local look = Training.xpUpgrade.sign
		local ready = false -- a plot and a price to show
		local affordable = false
		local lastUpgrades: number? = nil

		local function renderPad()
			local plotIndex = player:GetAttribute("PlotIndex")
			local cost = player:GetAttribute("XpUpgradePrice")
			local upgrades = player:GetAttribute("XpUpgrades")
			ready = plotIndex ~= nil and Plot.positions[plotIndex] ~= nil and cost ~= nil and upgrades ~= nil
			pad.sign.Enabled = ready
			pad.prompt.Enabled = ready and player:GetAttribute("IsTraining") ~= true
			if not ready then
				return
			end
			pad.point.WorldPosition = Training.xpPadPosition(plotIndex)
			pad.promptPoint.WorldPosition = pad.point.WorldPosition + Vector3.new(0, Training.xpUpgrade.prompt.height, 0)
			pad.price.Text = Format.cash(cost)
			affordable = (player:GetAttribute("Cash") or 0) >= cost
			colours(pad.priceColour, if affordable then look.afford else look.tooPricey)
			local nextXp = player:GetAttribute("NextXpPerRep") or 0
			pad.xp.Text = `+{if nextXp % 1 == 0 then nextXp else string.format("%.1f", nextXp)} XP per squat`
			-- Upgrades only fill bars faster (Config/Training); every few, the rack itself changes.
			local nextRack, left = Training.nextRack(upgrades)
			pad.rack.Text = if not nextRack then "Faster bars"
				elseif left == 1 then `Next: {nextRack.name}!`
				else `{left} more to {nextRack.name}`
			-- Just bought one: the sign jumps and springs back.
			if lastUpgrades and upgrades > lastUpgrades then
				pad.punch.Scale = look.punch
				TweenService:Create(pad.punch, TweenInfo.new(0.45, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Scale = 1 }):Play()
			end
			lastUpgrades = upgrades
		end
		player.AttributeChanged:Connect(renderPad)
		renderPad()
		pad.prompt.Triggered:Connect(function()
			if not affordable then
				Sfx.play("error") -- can't afford it yet; the server would refuse it anyway
				return
			end
			remotes.BuyUpgrade:FireServer()
		end)

		-- It floats gently, and the price breathes while you can afford it.
		RunService.RenderStepped:Connect(function()
			if not ready then
				return
			end
			local now = os.clock()
			pad.sign.StudsOffsetWorldSpace = Vector3.new(0, look.height + math.sin(now * TAU / look.bobSeconds) * look.bob, 0)
			pad.pulse.Scale = if affordable
				then 1 + (look.pulse - 1) * (0.5 + 0.5 * math.sin(now * TAU / look.pulseSeconds))
				else 1
		end)
	end)
end

return TrainingController
