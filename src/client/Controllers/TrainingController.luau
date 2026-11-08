-- Shows Throw Power at all times, and while training the level/XP bar, the STOP button, the
-- x2 bubble and the pop-ups (+XP, LEVEL UP!, the 2X XP moment). Also writes the price on the XP upgrade pad. Display and
-- requests only: every value is read from attributes the server sets on the local player.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")

local BoostMoment = require(script.Parent.BoostMoment)
local Format = require(ReplicatedStorage.Shared.Format)
local HudStyle = require(ReplicatedStorage.Shared.HudStyle)
local Pop = require(ReplicatedStorage.Shared.Config.Pop)
local PopText = require(ReplicatedStorage.Shared.PopText)
local Training = require(ReplicatedStorage.Shared.Config.Training)
local UiKit = require(ReplicatedStorage.Shared.UiKit)

local player = Players.LocalPlayer

local TrainingController = {}

local POWER = Color3.fromRGB(90, 190, 255)
local AFFORD = Color3.fromRGB(120, 235, 120)
local TOO_PRICEY = Color3.fromRGB(240, 70, 60)
local TEXT = Color3.new(1, 1, 1)
local BUBBLE_SIZE = 112
local POWER_HEIGHT = 52 -- before scaling for small screens
local POWER_ABOVE_BOTTOM = 98 -- clears the cash and $/s beneath it

local function makeLabel(parent: Instance, font: Enum.Font, color: Color3, align: Enum.TextXAlignment): TextLabel
	local label = Instance.new("TextLabel")
	label.BackgroundTransparency = 1
	label.Font = font
	label.TextColor3 = color
	label.TextXAlignment = align
	label.TextScaled = true
	label.Text = ""
	label.Parent = parent
	return label
end

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
-- their numbers. Returns the sign too, so it can move to a new base.
local function buildPadSign(): (BillboardGui, TextLabel, TextLabel, TextLabel)
	local sign = Instance.new("BillboardGui")
	sign.Name = "XpUpgradeSign"
	sign.Size = UDim2.fromOffset(220, 116)
	sign.StudsOffsetWorldSpace = Vector3.new(0, 5, 0)
	sign.MaxDistance = 120
	sign.Parent = player:WaitForChild("PlayerGui")
	local price = makeLabel(sign, Enum.Font.GothamBlack, TOO_PRICEY, Enum.TextXAlignment.Center)
	price.Size = UDim2.fromScale(1, 0.46)
	price.TextStrokeTransparency = 0
	local reward = makeLabel(sign, Enum.Font.GothamBlack, TEXT, Enum.TextXAlignment.Center)
	reward.Position = UDim2.fromScale(0, 0.46)
	reward.Size = UDim2.fromScale(1, 0.27)
	reward.TextStrokeTransparency = 0
	-- Each upgrade raises XP per squat (Training.xpPerRepGrowth): what it will be after this one.
	local xp = makeLabel(sign, Enum.Font.GothamBlack, UiKit.POWER, Enum.TextXAlignment.Center)
	xp.Position = UDim2.fromScale(0, 0.73)
	xp.Size = UDim2.fromScale(1, 0.27)
	xp.TextStrokeTransparency = 0
	return sign, price, reward, xp
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
		hud.level.Text = `+{Format.short(player:GetAttribute("PowerPerBar") or 0)} ⚡ per bar`
		hud.xp.Text = `{Format.short(xp)} / {Format.short(needed)}`
		hud.fill:TweenSize(UDim2.fromScale(math.clamp(xp / needed, 0, 1), 1), "Out", "Quad", 0.2, true)

		-- A full bar happens every few seconds early on, so it floats instead of shouting.
		if lastLevel and level > lastLevel and lastPower then
			PopText.float(`+{Format.short(power - lastPower)} ⚡ POWER`, Pop.colors.good, PopText.above(hud.bar))
		elseif isTraining and lastXp and level == lastLevel and xp > lastXp then
			PopText.float(`+{Format.short(xp - lastXp)} XP`, Pop.colors.xp, PopText.above(hud.bar))
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
		local sign, price, reward, xpLine = buildPadSign()
		local function placeSign()
			local plotIndex = player:GetAttribute("PlotIndex")
			local rack = plotIndex and workspace:WaitForChild("Racks"):WaitForChild(`Rack{plotIndex}`)
			local button = rack and rack:WaitForChild("base_XpButton", 10)
			sign.Adornee = button and button:FindFirstChild("Button")
			sign.Enabled = sign.Adornee ~= nil
		end
		player:GetAttributeChangedSignal("PlotIndex"):Connect(placeSign)
		placeSign()
		local function renderPad()
			local cost = player:GetAttribute("XpUpgradePrice")
			local upgrades = player:GetAttribute("XpUpgrades")
			if not cost or not upgrades then
				return
			end
			price.Text = Format.cash(cost)
			price.TextColor3 = if (player:GetAttribute("Cash") or 0) >= cost then AFFORD else TOO_PRICEY
			-- Upgrades only fill bars faster (Config/Training); every few, the rack itself changes.
			local nextRack, left = Training.nextRack(upgrades)
			reward.Text = if not nextRack then "Faster bars" elseif left == 1 then `{nextRack.name}!` else `{left} more: {nextRack.name}`
			local nextXp = player:GetAttribute("NextXpPerRep") or 0
			xpLine.Text = `+{if nextXp % 1 == 0 then nextXp else string.format("%.1f", nextXp)} XP per squat`
		end
		player.AttributeChanged:Connect(renderPad)
		renderPad()
	end)
end

return TrainingController
