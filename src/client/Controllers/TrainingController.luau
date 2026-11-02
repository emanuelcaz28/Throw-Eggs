-- Shows Throw Power at all times, and while training the level/XP bar, the STOP button, the
-- level-up pop-up and the x2 bubble. Also writes the price on the XP upgrade pad. Display and
-- requests only: every value is read from attributes the server sets on the local player.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")

local Format = require(ReplicatedStorage.Shared.Format)
local Training = require(ReplicatedStorage.Shared.Config.Training)

local player = Players.LocalPlayer

local TrainingController = {}

local ACCENT = Color3.fromRGB(226, 142, 58)
local PANEL = Color3.fromRGB(28, 30, 36)
local TRACK = Color3.fromRGB(58, 62, 72)
local POWER = Color3.fromRGB(90, 190, 255)
local STOP = Color3.fromRGB(205, 55, 50)
local BUBBLE = Color3.fromRGB(160, 90, 230)
local AFFORD = Color3.fromRGB(120, 235, 120)
local TOO_PRICEY = Color3.fromRGB(240, 70, 60)
local TEXT = Color3.new(1, 1, 1)
local LEVEL_UP_TIME = 1.4

local function corner(parent: Instance, radius: UDim)
	local uiCorner = Instance.new("UICorner")
	uiCorner.CornerRadius = radius
	uiCorner.Parent = parent
end

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

	-- Always on screen, just above the cash.
	local powerPill = Instance.new("Frame")
	powerPill.Name = "PowerPill"
	powerPill.AnchorPoint = Vector2.new(0, 0.5)
	powerPill.Position = UDim2.new(0, 16, 0.5, -150)
	powerPill.Size = UDim2.fromOffset(190, 40)
	powerPill.BackgroundColor3 = PANEL
	powerPill.BackgroundTransparency = 0.12
	powerPill.Parent = gui
	corner(powerPill, UDim.new(0, 12))
	local power = makeLabel(powerPill, Enum.Font.GothamBlack, POWER, Enum.TextXAlignment.Left)
	power.Name = "Power"
	power.Position = UDim2.fromOffset(12, 6)
	power.Size = UDim2.new(1, -24, 1, -12)
	power.TextStrokeTransparency = 0.4

	-- Only while training.
	local bar = Instance.new("Frame")
	bar.Name = "LevelBar"
	bar.AnchorPoint = Vector2.new(0.5, 1)
	bar.Position = UDim2.new(0.5, 0, 1, -16)
	bar.Size = UDim2.new(0.7, 0, 0, 46)
	bar.BackgroundColor3 = TRACK
	bar.Visible = false
	bar.Parent = gui
	corner(bar, UDim.new(0, 14))
	local barLimit = Instance.new("UISizeConstraint")
	barLimit.MaxSize = Vector2.new(560, 46)
	barLimit.Parent = bar
	local stroke = Instance.new("UIStroke")
	stroke.Color = PANEL
	stroke.Thickness = 3
	stroke.Parent = bar

	local fill = Instance.new("Frame")
	fill.Name = "Fill"
	fill.Size = UDim2.fromScale(0, 1)
	fill.BackgroundColor3 = POWER
	fill.BorderSizePixel = 0
	fill.Parent = bar
	corner(fill, UDim.new(0, 14))

	local level = makeLabel(bar, Enum.Font.GothamBlack, TEXT, Enum.TextXAlignment.Left)
	level.Position = UDim2.fromOffset(14, 8)
	level.Size = UDim2.new(0.5, -14, 1, -16)
	level.TextStrokeTransparency = 0.3
	level.ZIndex = 2
	local xp = makeLabel(bar, Enum.Font.GothamBlack, TEXT, Enum.TextXAlignment.Right)
	xp.AnchorPoint = Vector2.new(1, 0)
	xp.Position = UDim2.new(1, -14, 0, 8)
	xp.Size = UDim2.new(0.5, -14, 1, -16)
	xp.TextStrokeTransparency = 0.3
	xp.ZIndex = 2

	local stop = Instance.new("TextButton")
	stop.Name = "Stop"
	stop.AnchorPoint = Vector2.new(0.5, 1)
	stop.Position = UDim2.new(0.5, 0, 1, -74)
	stop.Size = UDim2.fromOffset(150, 50)
	stop.BackgroundColor3 = STOP
	stop.Font = Enum.Font.GothamBlack
	stop.Text = "STOP"
	stop.TextColor3 = TEXT
	stop.TextScaled = true
	stop.Visible = false
	stop.Parent = gui
	corner(stop, UDim.new(0, 12))
	local stopPadding = Instance.new("UIPadding")
	stopPadding.PaddingTop = UDim.new(0, 8)
	stopPadding.PaddingBottom = UDim.new(0, 8)
	stopPadding.Parent = stop

	local levelUp = makeLabel(gui, Enum.Font.GothamBlack, ACCENT, Enum.TextXAlignment.Center)
	levelUp.Name = "LevelUp"
	levelUp.AnchorPoint = Vector2.new(0.5, 0.5)
	levelUp.Position = UDim2.fromScale(0.5, 0.22)
	levelUp.Size = UDim2.new(0.6, 0, 0, 64)
	levelUp.TextStrokeTransparency = 0
	levelUp.Visible = false
	local levelUpPower = makeLabel(levelUp, Enum.Font.GothamBlack, POWER, Enum.TextXAlignment.Center)
	levelUpPower.Name = "Power"
	levelUpPower.Position = UDim2.new(0, 0, 1, 0)
	levelUpPower.Size = UDim2.new(1, 0, 0, 30)
	levelUpPower.TextStrokeTransparency = 0.2

	local bubble = Instance.new("TextButton")
	bubble.Name = "Bubble"
	bubble.AnchorPoint = Vector2.new(0.5, 0.5)
	bubble.Size = UDim2.fromOffset(96, 96)
	bubble.BackgroundColor3 = BUBBLE
	bubble.Font = Enum.Font.GothamBlack
	bubble.Text = `x{Training.bubble.multiplier}`
	bubble.TextColor3 = TEXT
	bubble.TextScaled = true
	bubble.Visible = false
	bubble.ZIndex = 3
	bubble.Parent = gui
	corner(bubble, UDim.new(0.5, 0))
	local bubbleStroke = Instance.new("UIStroke")
	bubbleStroke.ApplyStrokeMode = Enum.ApplyStrokeMode.Border
	bubbleStroke.Color = TEXT
	bubbleStroke.Thickness = 4
	bubbleStroke.Parent = bubble
	local bubblePadding = Instance.new("UIPadding")
	bubblePadding.PaddingTop = UDim.new(0, 22)
	bubblePadding.PaddingBottom = UDim.new(0, 22)
	bubblePadding.Parent = bubble

	return {
		power = power,
		bar = bar,
		fill = fill,
		level = level,
		xp = xp,
		stop = stop,
		levelUp = levelUp,
		levelUpPower = levelUpPower,
		bubble = bubble,
	}
end

-- Price and reward floating over the XP upgrade pad. Each player sees their own numbers.
local function buildPadSign(): (TextLabel, TextLabel)
	local station = workspace:WaitForChild("TrainingStation")
	local pad = station:WaitForChild("XpUpgradePad")
	local sign = Instance.new("BillboardGui")
	sign.Name = "XpUpgradeSign"
	sign.Adornee = pad
	sign.Size = UDim2.fromOffset(220, 90)
	sign.StudsOffsetWorldSpace = Vector3.new(0, 5, 0)
	sign.MaxDistance = 120
	sign.Parent = player:WaitForChild("PlayerGui")
	local price = makeLabel(sign, Enum.Font.GothamBlack, TOO_PRICEY, Enum.TextXAlignment.Center)
	price.Size = UDim2.fromScale(1, 0.6)
	price.TextStrokeTransparency = 0
	local reward = makeLabel(sign, Enum.Font.GothamBlack, TEXT, Enum.TextXAlignment.Center)
	reward.Position = UDim2.fromScale(0, 0.6)
	reward.Size = UDim2.fromScale(1, 0.4)
	reward.TextStrokeTransparency = 0
	return price, reward
end

local function popText(parent: GuiObject, text: string, color: Color3)
	local label = makeLabel(parent, Enum.Font.GothamBlack, color, Enum.TextXAlignment.Center)
	label.AnchorPoint = Vector2.new(0.5, 1)
	label.Position = UDim2.new(0.5, 0, 0, -4)
	label.Size = UDim2.new(1, 0, 0, 26)
	label.Text = text
	label.TextStrokeTransparency = 0.3
	local tween = TweenService:Create(label, TweenInfo.new(0.9, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {
		Position = UDim2.new(0.5, 0, 0, -36),
		TextTransparency = 1,
		TextStrokeTransparency = 1,
	})
	tween.Completed:Once(function()
		label:Destroy()
	end)
	tween:Play()
end

function TrainingController.start()
	local remotes = ReplicatedStorage:WaitForChild("TrainingRemotes")
	local hud = buildHud()
	local lastLevel: number? = nil
	local lastXp: number? = nil
	local lastPower: number? = nil
	local levelUpToken = 0
	local bubbleId: number? = nil

	local function showLevelUp(gained: number)
		levelUpToken += 1
		local token = levelUpToken
		hud.levelUp.Text = "LEVEL UP!"
		hud.levelUpPower.Text = `Throw Power +{gained}`
		hud.levelUp.Visible = true
		hud.levelUp.Size = UDim2.new(0.4, 0, 0, 40)
		TweenService:Create(hud.levelUp, TweenInfo.new(0.25, Enum.EasingStyle.Back), { Size = UDim2.new(0.6, 0, 0, 64) }):Play()
		task.delay(LEVEL_UP_TIME, function()
			if levelUpToken == token then
				hud.levelUp.Visible = false
			end
		end)
	end

	local function render()
		local power = player:GetAttribute("ThrowPower")
		local level = player:GetAttribute("TrainingLevel")
		local xp = player:GetAttribute("TrainingXp")
		local needed = player:GetAttribute("TrainingXpNeeded")
		if not (power and level and xp and needed) then
			return
		end
		local isTraining = player:GetAttribute("IsTraining") == true

		hud.power.Text = `💪 {Format.commas(power)}`
		hud.bar.Visible = isTraining
		hud.stop.Visible = isTraining
		hud.level.Text = `Level {level}`
		hud.xp.Text = `{Format.short(xp)} / {Format.short(needed)}`
		hud.fill:TweenSize(UDim2.fromScale(math.clamp(xp / needed, 0, 1), 1), "Out", "Quad", 0.2, true)

		if lastLevel and level > lastLevel and lastPower then
			showLevelUp(power - lastPower)
		elseif isTraining and lastXp and level == lastLevel and xp > lastXp then
			popText(hud.bar, `+{Format.short(xp - lastXp)} XP`, TEXT)
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
		hud.bubble.Size = UDim2.fromOffset(40, 40)
		hud.bubble.Visible = true
		TweenService:Create(hud.bubble, TweenInfo.new(0.25, Enum.EasingStyle.Back), { Size = UDim2.fromOffset(96, 96) }):Play()
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
			hud.bubble.Visible = false
			popText(hud.bar, `x{Training.bubble.multiplier}!`, Color3.fromRGB(200, 150, 255))
		end
	end)

	player.AttributeChanged:Connect(render)
	render()

	task.spawn(function()
		local price, reward = buildPadSign()
		local function renderPad()
			local cost = player:GetAttribute("XpUpgradePrice")
			local nextXp = player:GetAttribute("NextXpPerRep")
			if not cost or not nextXp then
				return
			end
			price.Text = Format.cash(cost)
			price.TextColor3 = if (player:GetAttribute("Cash") or 0) >= cost then AFFORD else TOO_PRICEY
			reward.Text = `+{Format.short(nextXp)} XP / rep`
		end
		player.AttributeChanged:Connect(renderPad)
		renderPad()
	end)
end

return TrainingController
