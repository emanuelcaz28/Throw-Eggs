-- The hatch reveal: the egg shakes while the name fills in and the "1 in X" counter climbs,
-- the dino bursts out, and a final card shows what was caught. Display only: the server has
-- already rolled the catch, and all of this is suspense leading up to that result.
local ContextActionService = game:GetService("ContextActionService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")
local UserInputService = game:GetService("UserInputService")

local Catch = require(ReplicatedStorage.Shared.Config.Catch)
local Reveal = require(ReplicatedStorage.Shared.Config.Reveal)
local DinoModel = require(ReplicatedStorage.Shared.DinoModel)
local DinoStats = require(ReplicatedStorage.Shared.DinoStats)
local Format = require(ReplicatedStorage.Shared.Format)

local player = Players.LocalPlayer

local RevealController = {}

local SKIP_ACTION = "RevealSkip"
local TEXT = Color3.new(1, 1, 1)
local INK = Color3.fromRGB(20, 22, 28)
local CASH = Color3.fromRGB(120, 235, 120)
local SIZE_COLOR = Color3.fromRGB(255, 214, 70)
local STICKER = Color3.fromRGB(255, 214, 70)
local SPIN_SPEED = 0.6
local WOBBLE_SPEED = 18
local MAX_WOBBLE = math.rad(22)
local POP_TIME = 0.45
local STORED_TEXT = {
	backpack = "plot full: sent to your backpack · tap to continue",
	sold = "plot and backpack full: sold · tap to continue",
}

local function makeLabel(parent: Instance, size: UDim2, position: UDim2, color: Color3): TextLabel
	local label = Instance.new("TextLabel")
	label.AnchorPoint = Vector2.new(0.5, 0)
	label.BackgroundTransparency = 1
	label.Font = Enum.Font.GothamBlack
	label.Position = position
	label.Size = size
	label.Text = ""
	label.TextColor3 = color
	label.TextScaled = true
	label.TextStrokeColor3 = INK
	label.TextStrokeTransparency = 0
	label.Parent = parent
	return label
end

local function buildGui()
	local gui = Instance.new("ScreenGui")
	gui.Name = "RevealHud"
	gui.IgnoreGuiInset = true
	gui.ResetOnSpawn = false
	gui.DisplayOrder = 10
	gui.Parent = player:WaitForChild("PlayerGui")

	local wash = Instance.new("Frame")
	wash.Name = "TierWash"
	wash.Size = UDim2.fromScale(1, 1)
	wash.BackgroundTransparency = 1
	wash.BorderSizePixel = 0
	wash.Parent = gui

	local ring = Instance.new("Frame")
	ring.Name = "Ring"
	ring.AnchorPoint = Vector2.new(0.5, 0.5)
	ring.Position = UDim2.fromScale(0.5, 0.5)
	ring.BackgroundTransparency = 1
	ring.Visible = false
	ring.Parent = gui
	local ringCorner = Instance.new("UICorner")
	ringCorner.CornerRadius = UDim.new(0.5, 0)
	ringCorner.Parent = ring
	local ringStroke = Instance.new("UIStroke")
	ringStroke.Thickness = 6
	ringStroke.Color = TEXT
	ringStroke.Parent = ring

	local tier = makeLabel(gui, UDim2.new(0.8, 0, 0, 56), UDim2.new(0.5, 0, 0, 48), TEXT)
	tier.Name = "Tier"

	local pill = Instance.new("Frame")
	pill.Name = "CounterPill"
	pill.AnchorPoint = Vector2.new(0.5, 0)
	pill.Position = UDim2.new(0.5, 0, 0, 108)
	pill.Size = UDim2.new(0.6, 0, 0, 56)
	pill.BackgroundColor3 = INK
	pill.BackgroundTransparency = 0.4
	pill.Visible = false
	pill.Parent = gui
	local pillLimit = Instance.new("UISizeConstraint")
	pillLimit.MaxSize = Vector2.new(420, 56)
	pillLimit.Parent = pill
	local pillCorner = Instance.new("UICorner")
	pillCorner.CornerRadius = UDim.new(0.5, 0)
	pillCorner.Parent = pill
	local counter = makeLabel(pill, UDim2.new(1, -24, 1, -12), UDim2.new(0.5, 0, 0, 6), TEXT)
	counter.Name = "Counter"

	local letters = makeLabel(gui, UDim2.new(0.9, 0, 0, 56), UDim2.new(0.5, 0, 1, -120), TEXT)
	letters.Name = "Letters"

	local hint = makeLabel(gui, UDim2.new(0.6, 0, 0, 20), UDim2.new(0.5, 0, 1, -44), TEXT)
	hint.Name = "Hint"
	hint.Font = Enum.Font.GothamBold
	hint.TextStrokeTransparency = 0.5

	local card = Instance.new("Frame")
	card.Name = "Card"
	card.AnchorPoint = Vector2.new(0.5, 1)
	card.Position = UDim2.new(0.5, 0, 1, -16)
	card.Size = UDim2.new(0.9, 0, 0, 190)
	card.BackgroundColor3 = INK
	card.BackgroundTransparency = 0.28
	card.Visible = false
	card.Parent = gui
	local cardLimit = Instance.new("UISizeConstraint")
	cardLimit.MaxSize = Vector2.new(620, 190)
	cardLimit.Parent = card
	local cardCorner = Instance.new("UICorner")
	cardCorner.CornerRadius = UDim.new(0, 18)
	cardCorner.Parent = card

	local mutation = makeLabel(card, UDim2.new(0.9, 0, 0, 24), UDim2.new(0.5, 0, 0, 10), TEXT)
	mutation.Name = "Mutation"
	local name = makeLabel(card, UDim2.new(0.94, 0, 0, 56), UDim2.new(0.5, 0, 0, 36), TEXT)
	name.Name = "DinoName"
	local size = makeLabel(card, UDim2.new(0.9, 0, 0, 24), UDim2.new(0.5, 0, 0, 94), SIZE_COLOR)
	size.Name = "SizeName"
	local income = makeLabel(card, UDim2.new(0.9, 0, 0, 28), UDim2.new(0.5, 0, 0, 122), CASH)
	income.Name = "Income"
	local cardHint = makeLabel(card, UDim2.new(0.9, 0, 0, 16), UDim2.new(0.5, 0, 0, 160), TEXT)
	cardHint.Name = "Continue"
	cardHint.Font = Enum.Font.GothamBold
	cardHint.TextStrokeTransparency = 0.5

	local sticker = Instance.new("TextLabel")
	sticker.Name = "NewBest"
	sticker.AnchorPoint = Vector2.new(1, 0)
	sticker.Position = UDim2.new(1, 16, 0, -18)
	sticker.Size = UDim2.fromOffset(150, 44)
	sticker.Rotation = 8
	sticker.BackgroundColor3 = STICKER
	sticker.Font = Enum.Font.GothamBlack
	sticker.Text = "NEW BEST!"
	sticker.TextColor3 = INK
	sticker.TextScaled = true
	sticker.Visible = false
	sticker.ZIndex = 2
	sticker.Parent = card
	local stickerCorner = Instance.new("UICorner")
	stickerCorner.CornerRadius = UDim.new(0, 10)
	stickerCorner.Parent = sticker
	local stickerStroke = Instance.new("UIStroke")
	stickerStroke.Thickness = 3
	stickerStroke.Color = INK
	stickerStroke.ApplyStrokeMode = Enum.ApplyStrokeMode.Border
	stickerStroke.Parent = sticker

	local banner = Instance.new("Frame")
	banner.Name = "CaughtBanner"
	banner.AnchorPoint = Vector2.new(0.5, 0)
	banner.Position = UDim2.new(0.5, 0, 0, 56)
	banner.Size = UDim2.new(0.8, 0, 0, 92)
	banner.BackgroundColor3 = INK
	banner.BackgroundTransparency = 0.2
	banner.Visible = false
	banner.Parent = gui
	local bannerLimit = Instance.new("UISizeConstraint")
	bannerLimit.MaxSize = Vector2.new(560, 92)
	bannerLimit.Parent = banner
	local bannerCorner = Instance.new("UICorner")
	bannerCorner.CornerRadius = UDim.new(0, 16)
	bannerCorner.Parent = banner
	local bannerTitle = makeLabel(banner, UDim2.new(0.9, 0, 0, 18), UDim2.new(0.5, 0, 0, 8), TEXT)
	bannerTitle.Text = "YOU CAUGHT"
	local bannerName = makeLabel(banner, UDim2.new(0.94, 0, 0, 34), UDim2.new(0.5, 0, 0, 28), TEXT)
	bannerName.Name = "Name"
	local bannerOdds = makeLabel(banner, UDim2.new(0.9, 0, 0, 20), UDim2.new(0.5, 0, 0, 64), TEXT)
	bannerOdds.Name = "Odds"

	local flash = Instance.new("Frame")
	flash.Name = "Flash"
	flash.Size = UDim2.fromScale(1, 1)
	flash.BackgroundColor3 = TEXT
	flash.BackgroundTransparency = 1
	flash.BorderSizePixel = 0
	flash.ZIndex = 5
	flash.Parent = gui

	return {
		wash = wash,
		ring = ring,
		ringStroke = ringStroke,
		tier = tier,
		pill = pill,
		counter = counter,
		letters = letters,
		hint = hint,
		card = card,
		mutation = mutation,
		name = name,
		size = size,
		income = income,
		cardHint = cardHint,
		sticker = sticker,
		banner = banner,
		bannerName = bannerName,
		bannerOdds = bannerOdds,
		flash = flash,
	}
end

local hud = nil

local function tween(instance: Instance, time: number, goal, style: Enum.EasingStyle?, direction: Enum.EasingDirection?)
	local info = TweenInfo.new(time, style or Enum.EasingStyle.Quad, direction or Enum.EasingDirection.Out)
	local created = TweenService:Create(instance, info, goal)
	created:Play()
	return created
end

local function makeSparkles(position: Vector3): (Part, ParticleEmitter)
	local anchor = Instance.new("Part")
	anchor.Name = "RevealSparkles"
	anchor.Anchored = true
	anchor.CanCollide = false
	anchor.CanQuery = false
	anchor.CanTouch = false
	anchor.Transparency = 1
	anchor.Size = Vector3.new(4, 4, 4)
	anchor.Position = position
	anchor.Parent = workspace

	local emitter = Instance.new("ParticleEmitter")
	emitter.Rate = 0
	emitter.Lifetime = NumberRange.new(0.8, 1.6)
	emitter.Speed = NumberRange.new(10, 22)
	emitter.SpreadAngle = Vector2.new(180, 180)
	emitter.Size = NumberSequence.new(0.8)
	emitter.Parent = anchor
	return anchor, emitter
end

-- Blanks for every letter, with the revealed ones filled in.
local function lettersText(name: string, shown: { [number]: boolean }): string
	local out = {}
	for index = 1, #name do
		local char = name:sub(index, index)
		if char:match("%w") and not shown[index] then
			char = "_"
		end
		table.insert(out, char)
	end
	return table.concat(out, " ")
end

local function shuffledLetterIndexes(name: string): { number }
	local indexes = {}
	for index = 1, #name do
		if name:sub(index, index):match("%w") then
			table.insert(indexes, index)
		end
	end
	for index = #indexes, 2, -1 do
		local swap = math.random(index)
		indexes[index], indexes[swap] = indexes[swap], indexes[index]
	end
	return indexes
end

-- How long the climb lasts: the counter's natural pace, within the configured limits.
local function climbTime(oneIn: number): number
	local steps = math.log(math.max(oneIn, 1)) / math.log(Reveal.counterRate)
	return math.clamp(steps * Reveal.counterStepTime, Reveal.minClimbTime, Reveal.maxClimbTime)
end

local function tierFor(value: number)
	local current = nil
	for _, tier in Reveal.tiers do
		if value >= tier.minOneIn then
			current = tier
		end
	end
	return current
end

local function pulse(tier)
	hud.wash.BackgroundColor3 = tier.color
	hud.wash.BackgroundTransparency = tier.wash - 0.3
	tween(hud.wash, 0.5, { BackgroundTransparency = tier.wash })

	hud.tier.Text = tier.label
	hud.tier.TextColor3 = tier.color
	hud.tier.Rotation = -6
	tween(hud.tier, 0.3, { Rotation = 0 }, Enum.EasingStyle.Back)

	hud.ring.Size = UDim2.fromOffset(60, 60)
	hud.ringStroke.Color = tier.color
	hud.ringStroke.Transparency = 0
	hud.ring.Visible = true
	tween(hud.ring, 0.7, { Size = UDim2.fromOffset(900, 900) })
	tween(hud.ringStroke, 0.7, { Transparency = 1 })
end

function RevealController.start()
	hud = buildGui()
end

-- Plays the whole reveal and returns once the player has tapped through it.
-- The egg part is taken over and destroyed here.
function RevealController.play(catch, egg: BasePart)
	local camera = workspace.CurrentCamera
	local landing = egg.Position
	local ground = Vector3.new(landing.X, landing.Y - egg.Size.Y / 2, landing.Z)
	local duration = climbTime(catch.oneIn)
	local showCounter = catch.oneIn >= Reveal.counterMinOneIn
	local mutation = DinoStats.findOption(Catch.mutations, catch.mutation)
	local size = DinoStats.findOption(Catch.sizes, catch.size)
	local dinoScale = if size then size.scale else 1
	local upperName = catch.name:upper()
	local letterOrder = shuffledLetterIndexes(upperName)
	local finalTier = tierFor(catch.oneIn)
	local shown = {}
	local revealedCount = 0
	local currentTier = nil
	local dino = nil
	local hatchedAt = nil
	local baseEggCFrame = CFrame.new(landing) -- upright, whatever way it tumbled in flight
	local anchor, sparkles = makeSparkles(landing)
	local startedAt = os.clock()
	local finished = false
	local cardShown = false
	local cardShownAt = 0
	local done = Instance.new("BindableEvent")

	hud.tier.Text = ""
	hud.wash.BackgroundTransparency = 1
	hud.ring.Visible = false
	hud.card.Visible = false
	hud.sticker.Visible = false
	hud.banner.Visible = false
	hud.pill.Visible = showCounter
	hud.counter.Text = "1 in 1"
	hud.letters.Visible = true
	hud.letters.Text = lettersText(upperName, shown)
	hud.hint.Visible = true
	hud.hint.Text = "tap to skip"

	local function hatch()
		egg:Destroy()
		dino = DinoModel.build(catch.name, catch.mutation, ground, 0.01)
		dino.Name = "RevealDino"
		dino.Parent = workspace
		sparkles:Emit(60)
	end

	local function showCard()
		cardShown = true
		cardShownAt = os.clock()
		if not dino then
			hatch()
		end
		dino:ScaleTo(dinoScale)
		for index = 1, #upperName do
			shown[index] = true
		end
		if showCounter then
			hud.counter.Text = `1 in {Format.commas(catch.oneIn)}`
		end
		if finalTier and finalTier ~= currentTier then
			currentTier = finalTier
			pulse(finalTier)
		end
		sparkles.Rate = if finalTier then finalTier.sparkles else 0

		hud.letters.Visible = false
		hud.hint.Visible = false
		hud.mutation.Text = if mutation then mutation.name else ""
		hud.mutation.TextColor3 = if mutation then mutation.color else TEXT
		hud.name.Text = upperName
		hud.name.TextColor3 = if finalTier then finalTier.color else TEXT
		hud.size.Text = if size then size.name else ""
		hud.income.Text = `{Format.cash(catch.income)}/s`
		hud.sticker.Text = if catch.newBest then "NEW BEST!" else "NEW DINO!"
		hud.sticker.Visible = catch.newBest or catch.isNew
		hud.cardHint.Text = if catch.completedBiome
			then `{catch.completedBiome} complete! Permanent bonus earned · tap to continue`
			else STORED_TEXT[catch.storedIn] or "tap to continue"
		hud.card.Visible = true
	end

	local function onTap()
		local now = os.clock()
		if now - startedAt < Reveal.skipDelay then
			return
		end
		if not cardShown then
			showCard()
		elseif now - cardShownAt >= Reveal.skipDelay and not finished then
			finished = true
			done:Fire()
		end
	end

	local inputConnection = UserInputService.InputBegan:Connect(function(input, gameProcessed)
		if
			not gameProcessed
			and (
				input.UserInputType == Enum.UserInputType.MouseButton1
				or input.UserInputType == Enum.UserInputType.Touch
			)
		then
			onTap()
		end
	end)
	ContextActionService:BindAction(SKIP_ACTION, function(_, inputState)
		if inputState == Enum.UserInputState.Begin then
			onTap()
		end
		return Enum.ContextActionResult.Sink
	end, false, Enum.KeyCode.Space, Enum.KeyCode.ButtonA)

	camera.CameraType = Enum.CameraType.Scriptable
	local stepConnection = RunService.RenderStepped:Connect(function()
		local elapsed = os.clock() - startedAt
		local progress = math.min(elapsed / duration, 1)

		local angle = elapsed * Reveal.camera.turnSpeed
		local view = Reveal.camera
		local pullBack = 0
		if dino then
			if not hatchedAt then
				hatchedAt = os.clock()
			end
			pullBack = math.min((os.clock() - hatchedAt) / view.pullBackTime, 1)
			pullBack = TweenService:GetValue(pullBack, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)
		end
		local radius = view.eggRadius + (view.radius * dinoScale - view.eggRadius) * pullBack
		local height = view.eggHeight + (view.height * dinoScale - view.eggHeight) * pullBack
		local focusHeight = view.eggFocusHeight + (view.focusHeight * dinoScale - view.eggFocusHeight) * pullBack
		local focus = ground + Vector3.new(0, focusHeight, 0)
		local cameraOffset = Vector3.new(math.sin(angle) * radius, height, math.cos(angle) * radius)
		camera.CFrame = CFrame.lookAt(focus + cameraOffset, focus)

		if dino then
			local popProgress = math.min((elapsed - duration * Reveal.hatchAt) / POP_TIME, 1)
			local pop = TweenService:GetValue(math.max(popProgress, 0), Enum.EasingStyle.Back, Enum.EasingDirection.Out)
			if cardShown then
				pop = 1
			end
			dino:ScaleTo(math.max(dinoScale * pop, 0.01))
			dino:PivotTo(CFrame.new(ground) * CFrame.Angles(0, elapsed * SPIN_SPEED, 0))
		elseif egg.Parent then
			local wobble = math.sin(elapsed * WOBBLE_SPEED) * MAX_WOBBLE * math.min(progress / Reveal.hatchAt, 1)
			egg.CFrame = baseEggCFrame * CFrame.Angles(0, 0, wobble)
		end

		if cardShown then
			return
		end

		if progress >= Reveal.hatchAt and not dino then
			hatch()
		end

		if showCounter then
			local value = catch.oneIn ^ progress
			hud.counter.Text = `1 in {Format.commas(value)}`
			local tier = tierFor(value)
			if tier and tier ~= currentTier then
				currentTier = tier
				sparkles.Rate = tier.sparkles
				pulse(tier)
			end
		end

		local targetLetters = math.floor(progress * #letterOrder)
		while revealedCount < targetLetters do
			revealedCount += 1
			shown[letterOrder[revealedCount]] = true
			hud.letters.Text = lettersText(upperName, shown)
		end

		if progress >= 1 then
			showCard()
		end
	end)

	done.Event:Wait()
	done:Destroy()
	stepConnection:Disconnect()
	inputConnection:Disconnect()
	ContextActionService:UnbindAction(SKIP_ACTION)

	-- White flash back to the player.
	tween(hud.flash, 0.15, { BackgroundTransparency = 0 }).Completed:Wait()
	hud.card.Visible = false
	hud.pill.Visible = false
	hud.tier.Text = ""
	hud.ring.Visible = false
	hud.wash.BackgroundTransparency = 1
	if dino then
		dino:Destroy()
	end
	if egg.Parent then
		egg:Destroy()
	end
	anchor:Destroy()
	camera.CameraType = Enum.CameraType.Custom
	tween(hud.flash, 0.3, { BackgroundTransparency = 1 })

	if catch.oneIn >= Reveal.caughtBannerMinOneIn then
		local prefix = ""
		if size then
			prefix ..= size.name .. " "
		end
		if mutation then
			prefix ..= mutation.name .. " "
		end
		hud.bannerName.Text = prefix .. upperName
		hud.bannerName.TextColor3 = if finalTier then finalTier.color else TEXT
		hud.bannerOdds.Text = `1 in {Format.commas(catch.oneIn)}`
		hud.banner.Visible = true
		task.delay(Reveal.caughtBannerTime, function()
			hud.banner.Visible = false
		end)
	end
end

return RevealController
