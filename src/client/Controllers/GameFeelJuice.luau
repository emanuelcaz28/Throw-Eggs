-- Visual juice for the game's small moments, beside the sounds in GameFeelSounds [Owner, 2026-11-10;
-- docs/GROWTH_PLAYBOOK.md "action and response"]: a power bar filling (burst and a big +POWER over Throw Power), each
-- squat (the XP bar bumps and shines), a monster put down (a dust puff at its feet and the $/s it adds), spending cash
-- (the cash bumps and flashes, and so does the button that bought it) and a tutorial step done (a burst, no text).
-- It only listens and draws: the systems it decorates stay untouched. Looks and numbers in Config/Juice.
local GuiService = game:GetService("GuiService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")

local Format = require(ReplicatedStorage.Shared.Format)
local Juice = require(ReplicatedStorage.Shared.Config.Juice)
local Pop = require(ReplicatedStorage.Shared.Config.Pop)
local PopText = require(ReplicatedStorage.Shared.PopText)
local Training = require(ReplicatedStorage.Shared.Config.Training)
local UiKit = require(ReplicatedStorage.Shared.UiKit)

local GameFeelJuice = {}

local player = Players.LocalPlayer
local playerGui = player:WaitForChild("PlayerGui")
local random = Random.new()

local function number(name: string): number
	local value = player:GetAttribute(name)
	return if typeof(value) == "number" then value else 0
end

local layer: ScreenGui? = nil
local function getLayer(): ScreenGui
	if not layer then
		local gui = Instance.new("ScreenGui")
		gui.Name = "Juice"
		gui.IgnoreGuiInset = true
		gui.ScreenInsets = Enum.ScreenInsets.None
		gui.ResetOnSpawn = false
		gui.DisplayOrder = 6 -- under the pop-up text (7)
		gui.Parent = playerGui
		layer = gui
	end
	return layer :: ScreenGui
end

-- The top bar's height when an element's screen leaves room for it: the juice layer measures from the very top.
local function insetOf(element: GuiObject): Vector2
	local gui = element:FindFirstAncestorWhichIsA("ScreenGui")
	return if gui and gui.IgnoreGuiInset then Vector2.zero else GuiService:GetGuiInset()
end

local function centreOf(element: GuiObject): Vector2
	return element.AbsolutePosition + element.AbsoluteSize / 2 + insetOf(element)
end

-- The middle of a left-aligned number's text (the HUD's Throw Power and cash).
local function textMiddle(label: TextLabel): Vector2
	local width = math.min(label.TextBounds.X, label.AbsoluteSize.X)
	return label.AbsolutePosition + Vector2.new(width / 2, label.AbsoluteSize.Y / 2) + insetOf(label)
end

local function shown(element: GuiObject): boolean
	local node: Instance? = element
	while node and node:IsA("GuiObject") do
		if not node.Visible then
			return false
		end
		node = node.Parent
	end
	local gui = element:FindFirstAncestorWhichIsA("ScreenGui")
	return gui ~= nil and gui.Enabled and element.AbsoluteSize.X > 0
end

-- A ring growing out of a point on the screen, with small diamonds flying out of it and fading.
local function burst(at: Vector2, look)
	local scale = UiKit.scale()
	local colors = {}
	for _, color in look.colors do
		table.insert(colors, Color3.fromHex(color))
	end
	local holder = Instance.new("Frame")
	holder.Name = "Burst"
	holder.BackgroundTransparency = 1
	holder.Size = UDim2.fromScale(1, 1)
	holder.Parent = getLayer()
	local info = TweenInfo.new(look.time, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)

	local ring = Instance.new("Frame")
	ring.Name = "Ring"
	ring.AnchorPoint = Vector2.new(0.5, 0.5)
	ring.BackgroundTransparency = 1
	ring.Position = UDim2.fromOffset(at.X, at.Y)
	ring.Size = UDim2.fromOffset(0, 0)
	ring.Parent = holder
	local round = Instance.new("UICorner")
	round.CornerRadius = UDim.new(0.5, 0)
	round.Parent = ring
	local edge = Instance.new("UIStroke")
	edge.Color = colors[1]
	edge.Thickness = look.ringWidth * scale
	edge.Parent = ring
	local width = look.ring * scale
	TweenService:Create(ring, info, { Size = UDim2.fromOffset(width, width) }):Play()
	TweenService:Create(edge, info, { Transparency = 1, Thickness = 1 }):Play()

	for index = 1, look.sparks do
		local angle = (index + random:NextNumber(-0.35, 0.35)) / look.sparks * 2 * math.pi
		local distance = look.distance * scale * random:NextNumber(0.7, 1.1)
		local size = look.sparkSize * scale * random:NextNumber(0.75, 1.2)
		local spark = Instance.new("Frame")
		spark.Name = "Spark"
		spark.AnchorPoint = Vector2.new(0.5, 0.5)
		spark.BorderSizePixel = 0
		spark.BackgroundColor3 = colors[(index - 1) % #colors + 1]
		spark.Position = UDim2.fromOffset(at.X, at.Y)
		spark.Size = UDim2.fromOffset(size, size)
		spark.Rotation = 45
		spark.Parent = holder
		local outline = Instance.new("UIStroke")
		outline.Color = UiKit.INK
		outline.Thickness = math.max(1, 2 * scale)
		outline.Parent = spark
		local to = at + Vector2.new(math.cos(angle), math.sin(angle)) * distance
		TweenService:Create(spark, info, {
			Position = UDim2.fromOffset(to.X, to.Y),
			Size = UDim2.fromOffset(0, 0),
			Rotation = 45 + random:NextNumber(-120, 120),
		}):Play()
		TweenService:Create(outline, info, { Transparency = 1 }):Play()
	end
	task.delay(look.time + 0.05, function()
		holder:Destroy()
	end)
end

-- Makes an element jump to scaleTo and spring back. Elements with their own scale motion (UiKit.pulse) are left alone:
-- false then.
local function bump(element: GuiObject, scaleTo: number, time: number): boolean
	local size = element:FindFirstChildOfClass("UIScale")
	if size and size.Name ~= "JuiceBump" then
		return false
	end
	if not size then
		local made = Instance.new("UIScale")
		made.Name = "JuiceBump"
		made.Parent = element
		size = made
	end
	local bumpScale = size :: UIScale
	bumpScale.Scale = scaleTo
	TweenService:Create(bumpScale, TweenInfo.new(time, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Scale = 1 }):Play()
	return true
end

-- A label's text flashing a colour and fading back to its own.
local function flash(label: TextLabel, color: Color3, time: number)
	local own = label:GetAttribute("JuiceColor")
	if typeof(own) ~= "Color3" then
		own = label.TextColor3
		label:SetAttribute("JuiceColor", own)
	end
	label.TextColor3 = color
	TweenService:Create(label, TweenInfo.new(time, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), { TextColor3 = own }):Play()
end

local function hudPart(guiName: string, ...: string): Instance?
	local node: Instance? = playerGui:FindFirstChild(guiName)
	for _, name in { ... } do
		node = node and node:FindFirstChild(name)
	end
	return node
end

-- 1. A power bar filled: a burst on Throw Power, the number bumps, and a big +POWER slams in over it.
local stopPowerPop: (() -> ())? = nil
local function powerMoment(gain: number)
	local stat = hudPart("TrainingHud", "PowerStat") :: Frame?
	local value = stat and stat:FindFirstChild("Value") :: TextLabel?
	if not (stat and value) then
		return
	end
	local middle = textMiddle(value)
	burst(middle, Juice.bursts.power)
	bump(stat, Juice.statBump.scale, Juice.statBump.time)
	flash(value, Color3.fromHex(Juice.statBump.flash), Juice.statBump.time)

	if stopPowerPop then
		stopPowerPop()
	end
	local look = Juice.powerPop
	local scale = UiKit.scale()
	local holder = PopText.word(getLayer(), `+{Format.short(gain)} POWER`, look.look, Color3.fromHex(look.fill))
	local size = Instance.new("UIScale")
	size.Parent = holder
	-- Over the number, but never past the screen's left edge (Throw Power sits right against it).
	local x = math.max(middle.X, holder.Size.X.Offset * scale / 2 + 12)
	local y = value.AbsolutePosition.Y + insetOf(value).Y - look.above * scale
	local length = math.max(look.scale[#look.scale][1], look.rise[#look.rise][1], look.opacity[#look.opacity][1])
	local startedAt = os.clock()
	local connection: RBXScriptConnection
	local function step(t: number)
		size.Scale = scale * PopText.sample(look.scale, t)
		holder.Position = UDim2.fromOffset(x, y - PopText.sample(look.rise, t) * scale)
		PopText.setOpacity(holder, PopText.sample(look.opacity, t))
	end
	local function stop()
		if connection.Connected then
			connection:Disconnect()
			holder:Destroy()
		end
	end
	step(0)
	connection = RunService.RenderStepped:Connect(function()
		local t = os.clock() - startedAt
		step(math.min(t, length))
		if t >= length then
			stop()
		end
	end)
	stopPowerPop = stop
end

-- 2. Each squat: the XP bar bumps a little and its fill shines white for a moment.
local function squatMoment()
	local bar = hudPart("TrainingHud", "TrainingGroup", "LevelBar") :: Frame?
	local fill = bar and bar:FindFirstChild("Fill") :: Frame?
	if not (bar and fill) then
		return
	end
	local look = Juice.squat
	bump(bar, look.scale, look.time)
	local shine = fill:FindFirstChild("JuiceShine") :: Frame?
	if not shine then
		local made = Instance.new("Frame")
		made.Name = "JuiceShine"
		made.BorderSizePixel = 0
		made.BackgroundColor3 = Color3.new(1, 1, 1)
		made.BackgroundTransparency = 1
		made.Size = UDim2.fromScale(1, 1)
		made.Parent = fill
		UiKit.corner(made, 18)
		shine = made
	end
	local white = shine :: Frame
	white.BackgroundTransparency = look.shine
	TweenService:Create(white, TweenInfo.new(look.time, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), { BackgroundTransparency = 1 }):Play()
end

-- 3. A monster put down: dust on the ground at its feet, then the $/s it adds floating up from there.
local function puff(feet: Vector3, width: number)
	local look = Juice.placePuff
	local ringWidth = math.clamp(width * look.footprint, look.min, look.max)
	local color = Color3.fromHex(look.color)
	local folder = Instance.new("Folder")
	folder.Name = "JuicePuff"
	local function part(shape: Enum.PartType): Part
		local made = Instance.new("Part")
		made.Shape = shape
		made.Anchored = true
		made.CanCollide = false
		made.CanQuery = false
		made.CanTouch = false
		made.CastShadow = false
		made.Material = Enum.Material.SmoothPlastic
		made.Color = color
		made.Transparency = look.startTransparency
		made.Parent = folder
		return made
	end
	local info = TweenInfo.new(look.time, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)
	local ring = part(Enum.PartType.Cylinder)
	ring.Size = Vector3.new(0.2, ringWidth * 0.3, ringWidth * 0.3)
	ring.CFrame = CFrame.new(feet + Vector3.new(0, 0.15, 0)) * CFrame.Angles(0, 0, math.pi / 2) -- lying flat
	TweenService:Create(ring, info, { Size = Vector3.new(0.2, ringWidth, ringWidth), Transparency = 1 }):Play()
	for index = 1, look.puffs do
		local angle = (index + random:NextNumber(-0.3, 0.3)) / look.puffs * 2 * math.pi
		local out = Vector3.new(math.cos(angle), 0, math.sin(angle))
		local size = ringWidth * look.puffSize * random:NextNumber(0.8, 1.2)
		local ball = part(Enum.PartType.Ball)
		ball.Size = Vector3.one * size * 0.4
		ball.Position = feet + out * ringWidth * 0.15 + Vector3.new(0, size * 0.2, 0)
		TweenService:Create(ball, info, {
			Position = feet + out * ringWidth * random:NextNumber(0.4, 0.55) + Vector3.new(0, size * 0.5, 0),
			Size = Vector3.one * size,
			Transparency = 1,
		}):Play()
	end
	folder.Parent = workspace
	task.delay(look.time + 0.1, function()
		folder:Destroy()
	end)
end

local function findStatue(key: any): Model?
	local plots = workspace:FindFirstChild("Plots")
	local plot = plots and plots:FindFirstChild(`Plot{player:GetAttribute("PlotIndex")}`)
	local statues = plot and plot:FindFirstChild("Statues")
	if not statues then
		return nil
	end
	for _, statue in statues:GetChildren() do
		if statue:IsA("Model") and statue:GetAttribute("DinoKey") == key and statue:FindFirstChildWhichIsA("BasePart", true) then
			return statue
		end
	end
	return nil
end

local function placeMoment(key: any, incomeGain: number?)
	local look = Juice.placePuff
	local statue: Model? = nil
	local giveUpAt = os.clock() + look.findFor
	repeat
		statue = findStatue(key)
		if not statue then
			task.wait()
		end
	until statue or os.clock() > giveUpAt
	if not statue then
		return
	end
	local box, size = statue:GetBoundingBox()
	local feet = Vector3.new(box.Position.X, box.Position.Y - size.Y / 2, box.Position.Z)
	puff(feet, math.max(size.X, size.Z))

	local gain = incomeGain
	if not gain or gain <= 0 then
		local tagIncome = statue:GetAttribute("TagIncome")
		gain = if typeof(tagIncome) == "number" then tagIncome else 0
	end
	local camera = workspace.CurrentCamera
	if gain and gain > 0 and camera then
		local point, onScreen = camera:WorldToViewportPoint(feet + Vector3.new(0, look.textAbove, 0))
		if onScreen then
			PopText.float(`+{Format.cash(gain)}/s`, Pop.colors.cash, Vector2.new(point.X, point.Y))
		end
	end
end

-- 4. Cash spent: the cash bumps and flashes, and the button just tapped to buy it (an egg, feeding, an upgrade) too.
local lastButton: GuiButton? = nil
local lastButtonAt = 0
local hooked = setmetatable({}, { __mode = "k" })
local function hookButton(object: Instance)
	if not object:IsA("GuiButton") or hooked[object] then
		return
	end
	hooked[object] = true
	local button = object :: GuiButton
	button.Activated:Connect(function()
		lastButton, lastButtonAt = button, os.clock()
	end)
end

local function buyMoment()
	local stat = hudPart("PlotHud", "CashStat") :: Frame?
	local value = stat and stat:FindFirstChild("Value") :: TextLabel?
	if stat and value then
		bump(stat, Juice.statBump.scale, Juice.statBump.time)
		flash(value, Color3.fromHex(Juice.statBump.flash), Juice.statBump.time)
		burst(textMiddle(value), Juice.bursts.cash)
	end
	local button = lastButton
	if button and os.clock() - lastButtonAt <= Juice.buyWindow and button.Parent and shown(button) then
		lastButton = nil
		bump(button, Juice.buttonBump.scale, Juice.buttonBump.time)
		burst(centreOf(button), Juice.bursts.button)
	end
end

-- 5. A tutorial step done: a burst in the upper middle of the screen. No words: the tutorial teaches by doing.
local function tutorialMoment()
	local screen = getLayer().AbsoluteSize
	burst(Vector2.new(screen.X * Juice.tutorialAt.X, screen.Y * Juice.tutorialAt.Y), Juice.bursts.tutorial)
end

local function watchTraining()
	local lastLevel = number("TrainingLevel")
	local lastXp = number("TrainingXp")
	local lastPower = number("ThrowPower")
	local powerRise, powerRiseAt = 0, -math.huge
	player:GetAttributeChangedSignal("ThrowPower"):Connect(function()
		local power = number("ThrowPower")
		powerRise, powerRiseAt = power - lastPower, os.clock()
		lastPower = power
	end)
	player:GetAttributeChangedSignal("TrainingLevel"):Connect(function()
		local level = number("TrainingLevel")
		local bars = level - lastLevel
		lastLevel = level
		if bars <= 0 then
			return
		end
		-- Throw Power can arrive just before or just after the level: read the rise once both are in.
		task.delay(0.1, function()
			local gain = if os.clock() - powerRiseAt < 0.5 and powerRise > 0 then powerRise else bars * Training.powerPerBar
			powerMoment(gain)
		end)
	end)
	player:GetAttributeChangedSignal("TrainingXp"):Connect(function()
		local xp = number("TrainingXp")
		if xp > lastXp and player:GetAttribute("IsTraining") == true then
			squatMoment()
		end
		lastXp = xp
	end)
end

local function watchPlot()
	-- Which monster went down: the server sets PlacedKey just before it counts the put-down (PlacedTick). Its $/s is
	-- the rise in Income that came with it.
	local lastIncome = number("Income")
	local incomeRise, incomeRiseAt = 0, -math.huge
	player:GetAttributeChangedSignal("Income"):Connect(function()
		local income = number("Income")
		incomeRise, incomeRiseAt = income - lastIncome, os.clock()
		lastIncome = income
	end)
	local lastTick = number("PlacedTick")
	player:GetAttributeChangedSignal("PlacedTick"):Connect(function()
		local placed = number("PlacedTick")
		local rose = placed > lastTick
		lastTick = placed
		local key = player:GetAttribute("PlacedKey")
		if not rose or key == nil then
			return
		end
		local gain = if os.clock() - incomeRiseAt < 1 and incomeRise > 0 then incomeRise else nil
		task.spawn(placeMoment, key, gain)
	end)
end

local function watchCash()
	local last = number("Cash")
	player:GetAttributeChangedSignal("Cash"):Connect(function()
		local cash = number("Cash")
		if cash < last then
			buyMoment()
		end
		last = cash
	end)
	for _, object in playerGui:GetDescendants() do
		hookButton(object)
	end
	playerGui.DescendantAdded:Connect(hookButton)
end

local function watchTutorial()
	local lastStep = number("TutorialStep")
	player:GetAttributeChangedSignal("TutorialStep"):Connect(function()
		local step = number("TutorialStep")
		if lastStep > 0 and step > lastStep then
			tutorialMoment()
		end
		lastStep = step
	end)
end

-- 6. A PERFECT tap, on the meter (Config/Juice perfectHit): a gold burst out of the PERFECT zone, the zone flashing
-- white back to its own colour, and a small bump of the whole meter. ThrowController calls it on the tap.
function GameFeelJuice.perfectHit(meter: GuiObject, zone: GuiObject)
	local look = Juice.perfectHit
	burst(centreOf(zone), look.burst)
	bump(meter, look.bump.scale, look.bump.time)
	local own = zone.BackgroundColor3
	zone.BackgroundColor3 = Color3.fromHex(look.flash.color)
	TweenService:Create(zone, TweenInfo.new(look.flash.time, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), { BackgroundColor3 = own }):Play()
end

-- A PERFECT throw's egg trail turns gold (Config/Juice perfectHit.trail), on every screen that sees the throw.
function GameFeelJuice.goldTrail(trail: Trail)
	local look = Juice.perfectHit.trail
	trail.Color = ColorSequence.new(Color3.fromHex(look.from), Color3.fromHex(look.to))
	trail.LightEmission = look.lightEmission
	trail.Lifetime = look.lifetime
	for _, attachment in { trail.Attachment0, trail.Attachment1 } do
		if attachment then
			attachment.Position *= look.widthScale
		end
	end
end

function GameFeelJuice.start()
	watchTraining()
	watchCash()
	watchTutorial()
	watchPlot()
end

return GameFeelJuice
