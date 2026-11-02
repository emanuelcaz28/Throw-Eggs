-- The hatch reveal: the egg shakes while the name fills in letter tiles and the "1 in X" counter
-- climbs, the dino bursts out, and a card shows what was caught. Display only: the server has
-- already rolled the catch, and all of this is suspense leading up to that result.
-- The look is UI design v2 (mock-ups 09-11 in design/ui-mockups/build.py), built with UiKit.
local ContextActionService = game:GetService("ContextActionService")
local GuiService = game:GetService("GuiService")
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
local Plot = require(ReplicatedStorage.Shared.Config.Plot)
local UiKit = require(ReplicatedStorage.Shared.UiKit)

local player = Players.LocalPlayer

local RevealController = {}

local SKIP_ACTION = "RevealSkip"
local WHITE = Color3.new(1, 1, 1)
local SPIN_SPEED = 0.6
local WOBBLE_SPEED = 18
local MAX_WOBBLE = math.rad(22)
local POP_TIME = 0.45
local LETTER_POP = 1.4 -- a letter tile lands this big and settles back to normal size
local LABEL_WIGGLE = 3 -- degrees the luck label rocks either way
local CARD_WIDTH = 640
local BEAM_HEIGHT = 90
local BANNER_HEIGHT = 132
local STORED_TEXT = {
	backpack = "Plot full: sent to your backpack",
	sold = "Plot and backpack full: sold",
}

local hud = nil

local function tween(instance: Instance, time: number, goal, style: Enum.EasingStyle?, direction: Enum.EasingDirection?)
	local info = TweenInfo.new(time, style or Enum.EasingStyle.Quad, direction or Enum.EasingDirection.Out)
	local created = TweenService:Create(instance, info, goal)
	created:Play()
	return created
end

-- Puts the character back on its own plot, by the exit. Players without a plot stay put.
-- The client moves its own character, the same way walking does.
local function returnHome()
	local plotIndex = player:GetAttribute("PlotIndex")
	local character = player.Character
	local humanoid = character and character:FindFirstChildOfClass("Humanoid")
	local root = character and character:FindFirstChild("HumanoidRootPart")
	if not plotIndex or not humanoid or not root or humanoid.Health <= 0 then
		return
	end
	local home = Plot.homeCFrame(plotIndex) + Vector3.new(0, humanoid.HipHeight + root.Size.Y / 2, 0)
	character:PivotTo(home)
	root.AssemblyLinearVelocity = Vector3.zero
	-- Behind and above the character, so the view opens on the plot.
	workspace.CurrentCamera.CFrame = CFrame.lookAt((home * CFrame.new(0, 8, 16)).Position, home.Position)
end

local function addScale(object: GuiObject, scale: number)
	local uiScale = Instance.new("UIScale")
	uiScale.Scale = scale
	uiScale.Parent = object
	return uiScale
end

local function row(parent: Instance, padding: number): UIListLayout
	local layout = Instance.new("UIListLayout")
	layout.FillDirection = Enum.FillDirection.Horizontal
	layout.HorizontalAlignment = Enum.HorizontalAlignment.Center
	layout.VerticalAlignment = Enum.VerticalAlignment.Center
	layout.SortOrder = Enum.SortOrder.LayoutOrder
	layout.Padding = UDim.new(0, padding)
	layout.Parent = parent
	return layout
end

local function padSides(parent: Instance, left: number, right: number)
	local pad = Instance.new("UIPadding")
	pad.PaddingLeft = UDim.new(0, left)
	pad.PaddingRight = UDim.new(0, right)
	pad.Parent = parent
end

-- Outlined text that grows sideways to fit, for use inside a row.
local function rowText(parent: Instance, value: string, size: number, color: Color3?, height: number): TextLabel
	local label = UiKit.text(parent, value, size, color)
	label.AutomaticSize = Enum.AutomaticSize.X
	label.Size = UDim2.fromOffset(0, height)
	return label
end

-- A dark rounded chip that grows to fit what's in it (mutation, size, $/s, odds).
local function chip(parent: Instance, height: number, order: number): Frame
	local frame = Instance.new("Frame")
	frame.AutomaticSize = Enum.AutomaticSize.X
	frame.Size = UDim2.fromOffset(0, height)
	frame.BackgroundColor3 = UiKit.DEEP
	frame.LayoutOrder = order
	frame.Parent = parent
	UiKit.corner(frame, height * 0.3)
	UiKit.stroke(frame, 4)
	row(frame, 8)
	return frame
end

-- The top or bottom edge of the screen, lit in the luck tier's colour and fading towards the middle.
local function edgeGlow(parent: Instance, top: boolean): Frame
	local glow = Instance.new("Frame")
	glow.Name = if top then "GlowTop" else "GlowBottom"
	glow.AnchorPoint = Vector2.new(0, if top then 0 else 1)
	glow.Position = UDim2.fromScale(0, if top then 0 else 1)
	glow.Size = UDim2.fromScale(1, 0.36)
	glow.BackgroundTransparency = 1
	glow.BorderSizePixel = 0
	glow.Parent = parent
	local fade = Instance.new("UIGradient")
	fade.Rotation = if top then 90 else -90
	fade.Transparency = NumberSequence.new(0, 1)
	fade.Parent = glow
	return glow
end

local function buildGui()
	local gui = Instance.new("ScreenGui")
	gui.Name = "RevealHud"
	gui.IgnoreGuiInset = true
	gui.ResetOnSpawn = false
	gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	gui.DisplayOrder = 10
	gui.Parent = player:WaitForChild("PlayerGui")
	local scale = UiKit.scale()
	local inset = GuiService:GetGuiInset().Y

	local glows = { edgeGlow(gui, true), edgeGlow(gui, false) }

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
	ringStroke.Thickness = 10
	ringStroke.Parent = ring

	-- Top: the luck label (LUCKY! ... GODLY!) and the "1 in X" counter.
	local top = Instance.new("Frame")
	top.Name = "Top"
	top.AnchorPoint = Vector2.new(0.5, 0)
	top.Position = UDim2.new(0.5, 0, 0, inset + 4)
	top.Size = UDim2.fromOffset(1000, 210)
	top.BackgroundTransparency = 1
	top.Visible = false
	top.Parent = gui
	addScale(top, scale)

	local luck = UiKit.text(top, "", 84)
	luck.Name = "Luck"
	luck.Size = UDim2.new(1, 0, 0, 104)
	local luckGradient = Instance.new("UIGradient")
	luckGradient.Rotation = 90
	luckGradient.Parent = luck
	local luckPop = addScale(luck, 1)

	-- The counter pill: ink outline, then an inner edge in the tier's colour around the content.
	local pill = Instance.new("Frame")
	pill.Name = "Counter"
	pill.AnchorPoint = Vector2.new(0.5, 0)
	pill.Position = UDim2.fromOffset(500, 112)
	pill.AutomaticSize = Enum.AutomaticSize.X
	pill.Size = UDim2.fromOffset(0, 86)
	pill.BackgroundColor3 = UiKit.PANEL
	pill.Parent = top
	UiKit.corner(pill, 28)
	UiKit.stroke(pill, 5)
	padSides(pill, 4, 4)
	row(pill, 0)
	local pillInner = Instance.new("Frame")
	pillInner.AutomaticSize = Enum.AutomaticSize.X
	pillInner.Size = UDim2.fromOffset(0, 78)
	pillInner.BackgroundTransparency = 1
	pillInner.Parent = pill
	UiKit.corner(pillInner, 24)
	local pillEdge = UiKit.stroke(pillInner, 4, UiKit.PANEL_EDGE)
	padSides(pillInner, 8, 26)
	row(pillInner, 8)
	local clover = UiKit.viewport(pillInner, "clover", { spin = true, size = UDim2.fromOffset(66, 66) })
	clover.LayoutOrder = 1
	rowText(pillInner, "1 in", 34, UiKit.MUTED, 78).LayoutOrder = 2
	local counter = rowText(pillInner, "1", 58, nil, 78)
	counter.LayoutOrder = 3

	-- Bottom: the name as letter tiles, filled in out of order.
	local letters = Instance.new("Frame")
	letters.Name = "Letters"
	letters.AnchorPoint = Vector2.new(0.5, 1)
	letters.Position = UDim2.new(0.5, 0, 1, -14)
	letters.Size = UDim2.fromOffset(1200, 112)
	letters.BackgroundTransparency = 1
	letters.Visible = false
	letters.Parent = gui
	addScale(letters, scale)
	local tileRow = Instance.new("Frame")
	tileRow.BackgroundTransparency = 1
	tileRow.Size = UDim2.new(1, 0, 0, 72)
	tileRow.Parent = letters
	row(tileRow, 6)
	local hint = UiKit.text(letters, "tap to skip", 24)
	hint.Position = UDim2.fromOffset(0, 80)

	-- The final card: header in the dino's rarity colours with its name, then mutation, size and $/s.
	local card = UiKit.panel(gui, {
		name = "RevealCard",
		width = CARD_WIDTH,
		height = 220,
		title = "",
		anchor = Vector2.new(0.5, 1),
		position = UDim2.new(0.5, 0, 1, -16),
	})
	card.close.Visible = false
	local name = UiKit.text(card.header, "", 56)
	name.Position = UDim2.fromOffset(70, 8) -- clear of the NEW BEST! tag on the right
	name.Size = UDim2.new(1, -140, 0, 70)
	name.TextScaled = true
	name.ZIndex = 2
	local nameLimit = Instance.new("UITextSizeConstraint")
	nameLimit.MaxTextSize = 56
	nameLimit.Parent = name

	local chips = Instance.new("Frame")
	chips.BackgroundTransparency = 1
	chips.Position = UDim2.fromOffset(0, 14)
	chips.Size = UDim2.new(1, 0, 0, 58)
	chips.Parent = card.body
	row(chips, 12)
	local mutationChip = chip(chips, 58, 1)
	padSides(mutationChip, 18, 18)
	local mutation = rowText(mutationChip, "", 28, nil, 58)
	local sizeChip = chip(chips, 58, 2)
	padSides(sizeChip, 18, 18)
	local sizeName = rowText(sizeChip, "", 28, UiKit.GOLD, 58)
	local incomeChip = chip(chips, 58, 3)
	padSides(incomeChip, 10, 18)
	UiKit.viewport(incomeChip, "cash_S", { spin = true, size = UDim2.fromOffset(52, 50) }).LayoutOrder = 1
	local income = rowText(incomeChip, "", 34, UiKit.CASH, 58)
	income.LayoutOrder = 2

	local message = UiKit.text(card.body, "", 22, UiKit.GOLD)
	message.Position = UDim2.fromOffset(0, 84)
	local continueHint = UiKit.text(card.body, "tap to continue", 22, UiKit.MUTED)
	continueHint.AnchorPoint = Vector2.new(0.5, 0) -- it pulses around its middle
	addScale(continueHint, 1)
	UiKit.pulse(continueHint)

	local newBest = UiKit.tag(card.frame, "NEW BEST!", "tagGold", 28)
	local newDino = UiKit.tag(card.frame, "NEW DINO!", "green", 28)
	for _, tag in { newBest, newDino } do
		tag.AnchorPoint = Vector2.new(1, 0.5)
		tag.Position = UDim2.new(1, 26, 0, 0)
		tag.ZIndex = 5
		tag.Visible = false
	end

	-- Back on the plot, very rare catches keep a "YOU CAUGHT!" banner up for a while.
	local banner = Instance.new("Frame")
	banner.Name = "CaughtBanner"
	banner.AnchorPoint = Vector2.new(0.5, 0)
	banner.Size = UDim2.fromOffset(660, BANNER_HEIGHT)
	banner.BackgroundColor3 = UiKit.PANEL
	banner.Visible = false
	banner.Parent = gui
	UiKit.corner(banner, 28)
	UiKit.stroke(banner, 5)
	addScale(banner, scale)
	local bannerEdge = Instance.new("Frame")
	bannerEdge.BackgroundTransparency = 1
	bannerEdge.Position = UDim2.fromOffset(4, 4)
	bannerEdge.Size = UDim2.new(1, -8, 1, -8)
	bannerEdge.Parent = banner
	UiKit.corner(bannerEdge, 24)
	UiKit.stroke(bannerEdge, 4, UiKit.PANEL_EDGE)
	local bannerTile = Instance.new("Frame")
	bannerTile.BackgroundTransparency = 1
	bannerTile.Position = UDim2.fromOffset(16, 16)
	bannerTile.Size = UDim2.fromOffset(100, 100)
	bannerTile.Parent = banner
	local caught = UiKit.text(banner, "YOU CAUGHT!", 22, UiKit.GOLD, Enum.TextXAlignment.Left)
	caught.Position = UDim2.fromOffset(132, 12)
	caught.Size = UDim2.new(1, -148, 0, 28)
	local bannerName = UiKit.text(banner, "", 30, nil, Enum.TextXAlignment.Left)
	bannerName.Position = UDim2.fromOffset(132, 40)
	bannerName.Size = UDim2.new(1, -148, 0, 38)
	bannerName.TextScaled = true
	local bannerNameLimit = Instance.new("UITextSizeConstraint")
	bannerNameLimit.MaxTextSize = 30
	bannerNameLimit.Parent = bannerName
	local odds = chip(banner, 38, 0)
	odds.Position = UDim2.fromOffset(132, 82)
	padSides(odds, 6, 14)
	UiKit.viewport(odds, "clover", { size = UDim2.fromOffset(32, 32) }).LayoutOrder = 1
	local bannerOdds = rowText(odds, "", 22, nil, 38)
	bannerOdds.LayoutOrder = 2

	local flash = Instance.new("Frame")
	flash.Name = "Flash"
	flash.Size = UDim2.fromScale(1, 1)
	flash.BackgroundColor3 = WHITE
	flash.BackgroundTransparency = 1
	flash.BorderSizePixel = 0
	flash.ZIndex = 10
	flash.Parent = gui

	return {
		scale = scale,
		inset = inset,
		glows = glows,
		ring = ring,
		ringStroke = ringStroke,
		top = top,
		luck = luck,
		luckGradient = luckGradient,
		luckPop = luckPop,
		pill = pill,
		pillEdge = pillEdge,
		counter = counter,
		letters = letters,
		tileRow = tileRow,
		card = card,
		name = name,
		mutationChip = mutationChip,
		mutation = mutation,
		sizeChip = sizeChip,
		sizeName = sizeName,
		income = income,
		message = message,
		continueHint = continueHint,
		newBest = newBest,
		newDino = newDino,
		banner = banner,
		bannerTile = bannerTile,
		bannerName = bannerName,
		bannerOdds = bannerOdds,
		flash = flash,
	}
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

-- A glowing pillar of light rising from the dino's feet. It lives on the sparkles anchor and goes with it.
local function addBeam(anchor: BasePart, ground: Vector3, width: number, color: Color3)
	local bottom = Instance.new("Attachment")
	bottom.Position = ground - anchor.Position
	bottom.Parent = anchor
	local topEnd = Instance.new("Attachment")
	topEnd.Position = bottom.Position + Vector3.new(0, BEAM_HEIGHT, 0)
	topEnd.Parent = anchor
	-- A faint wide beam around a brighter narrow one, so the edges look soft.
	for _, layer in { { width = 1, transparency = 0.75 }, { width = 0.45, transparency = 0.35 } } do
		local beam = Instance.new("Beam")
		beam.Attachment0 = bottom
		beam.Attachment1 = topEnd
		beam.Color = ColorSequence.new(color)
		beam.FaceCamera = true
		beam.LightEmission = 1
		beam.LightInfluence = 0
		beam.Segments = 1
		beam.Width0 = width * layer.width
		beam.Width1 = width * layer.width
		beam.Transparency = NumberSequence.new({ NumberSequenceKeypoint.new(0, layer.transparency), NumberSequenceKeypoint.new(1, 1) })
		beam.Parent = anchor
	end
end

-- One tile per letter or digit; other characters (the "-" in T-Rex) sit between them as plain text.
-- Returns the tiles by their position in the name.
local function buildLetterTiles(name: string)
	for _, child in hud.tileRow:GetChildren() do
		if child:IsA("GuiObject") then
			child:Destroy()
		end
	end
	local tiles = {}
	for index = 1, #name do
		local char = name:sub(index, index)
		if char:match("%w") then
			local tile = Instance.new("Frame")
			tile.LayoutOrder = index
			tile.Size = UDim2.fromOffset(52, 64)
			tile.BackgroundColor3 = UiKit.DEEP
			tile.Parent = hud.tileRow
			UiKit.corner(tile, 14)
			UiKit.stroke(tile, 4)
			local label = UiKit.text(tile, "", 40)
			label.Size = UDim2.fromScale(1, 1)
			tiles[index] = { tile = tile, label = label, pop = addScale(tile, 1), char = char }
		else
			local label = UiKit.text(hud.tileRow, char, 40)
			label.LayoutOrder = index
			label.Size = UDim2.fromOffset(22, 64)
		end
	end
	return tiles
end

local function showLetter(entry)
	UiKit.gradient(entry.tile, "yellow")
	entry.label.Text = entry.char
	entry.pop.Scale = LETTER_POP
	tween(entry.pop, 0.3, { Scale = 1 }, Enum.EasingStyle.Back)
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

-- A new luck tier: its label pops in, the screen edges light up and a ring bursts out.
local function pulse(tier)
	for _, glow in hud.glows do
		glow.BackgroundColor3 = tier.color
		glow.BackgroundTransparency = 1 - math.min(tier.glow + 0.3, 1)
		tween(glow, 0.5, { BackgroundTransparency = 1 - tier.glow })
	end

	hud.luck.Text = tier.label
	hud.luckGradient.Color = ColorSequence.new(tier.color:Lerp(WHITE, 0.55), tier.color)
	hud.luckPop.Scale = 0.3
	tween(hud.luckPop, 0.35, { Scale = 1 }, Enum.EasingStyle.Back)
	hud.pillEdge.Color = tier.color

	hud.ring.Size = UDim2.fromOffset(60, 60)
	hud.ringStroke.Color = tier.color
	hud.ringStroke.Transparency = 0
	hud.ring.Visible = true
	tween(hud.ring, 0.7, { Size = UDim2.fromOffset(900, 900) })
	tween(hud.ringStroke, 0.7, { Transparency = 1 })
end

local bannerShows = 0

-- Slides the "YOU CAUGHT!" banner down from the top, and back up after a while.
local function showCaughtBanner(catch, fullName: string)
	bannerShows += 1
	local show = bannerShows
	for _, child in hud.bannerTile:GetChildren() do
		child:Destroy()
	end
	local mutation = DinoStats.findOption(Catch.mutations, catch.mutation)
	UiKit.dinoTile(hud.bannerTile, catch.id, catch.name, 100, 100, { tint = mutation and mutation.color })
	hud.bannerName.Text = fullName
	hud.bannerOdds.Text = `1 in {Format.commas(catch.oneIn)}`

	local hidden = UDim2.new(0.5, 0, 0, -(BANNER_HEIGHT + 20) * hud.scale)
	hud.banner.Position = hidden
	hud.banner.Visible = true
	tween(hud.banner, 0.45, { Position = UDim2.new(0.5, 0, 0, hud.inset + 12) }, Enum.EasingStyle.Back)
	task.delay(Reveal.caughtBannerTime, function()
		if show ~= bannerShows then
			return
		end
		tween(hud.banner, 0.3, { Position = hidden }, Enum.EasingStyle.Quad, Enum.EasingDirection.In).Completed:Wait()
		if show == bannerShows then
			hud.banner.Visible = false
		end
	end)
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
	local tiles = buildLetterTiles(upperName)
	local finalTier = tierFor(catch.oneIn)
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

	for _, glow in hud.glows do
		glow.BackgroundTransparency = 1
	end
	hud.ring.Visible = false
	hud.luck.Text = ""
	hud.pillEdge.Color = UiKit.PANEL_EDGE
	hud.pill.Visible = showCounter
	hud.counter.Text = "1"
	hud.top.Visible = true
	hud.letters.Visible = true
	UiKit.closePanel(hud.card)

	local function setTier(tier)
		currentTier = tier
		sparkles.Rate = tier.sparkles
		sparkles.Color = ColorSequence.new(tier.color, WHITE)
		pulse(tier)
	end

	local function hatch()
		egg:Destroy()
		dino = DinoModel.build(catch.id, catch.mutation, ground, 0.01)
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
		if showCounter then
			hud.counter.Text = Format.commas(catch.oneIn)
		end
		if finalTier and finalTier ~= currentTier then
			setTier(finalTier)
		end
		if finalTier then
			local extents = dino:GetExtentsSize()
			addBeam(anchor, ground, math.max(extents.X, extents.Z) * 0.8, finalTier.color)
		end

		hud.letters.Visible = false
		UiKit.setHeader(hud.card, UiKit.rarityOf(catch.id))
		hud.name.Text = upperName
		hud.mutationChip.Visible = mutation ~= nil
		hud.mutation.Text = if mutation then mutation.name else ""
		hud.mutation.TextColor3 = if mutation then mutation.color else WHITE
		hud.sizeChip.Visible = size ~= nil
		hud.sizeName.Text = if size then size.name else ""
		hud.income.Text = `{Format.cash(catch.income)}/s`
		hud.newBest.Visible = catch.newBest == true
		hud.newDino.Visible = catch.isNew == true and not catch.newBest

		local message = if catch.completedBiome
			then `{catch.completedBiome} complete! Permanent bonus earned`
			else STORED_TEXT[catch.storedIn]
		hud.message.Text = message or ""
		hud.continueHint.Position = UDim2.new(0.5, 0, 0, if message then 114 else 84)
		hud.card.frame.Size = UDim2.fromOffset(CARD_WIDTH, if message then 250 else 220)
		UiKit.openPanel(hud.card)
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

		hud.luck.Rotation = LABEL_WIGGLE * math.sin(elapsed * 4)

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
			hud.counter.Text = Format.commas(value)
			local tier = tierFor(value)
			if tier and tier ~= currentTier then
				setTier(tier)
			end
		end

		local targetLetters = math.floor(progress * #letterOrder)
		while revealedCount < targetLetters do
			revealedCount += 1
			showLetter(tiles[letterOrder[revealedCount]])
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

	-- White flash back to the player, who is moved home while the screen is white.
	tween(hud.flash, 0.15, { BackgroundTransparency = 0 }).Completed:Wait()
	returnHome()
	UiKit.closePanel(hud.card)
	hud.top.Visible = false
	hud.letters.Visible = false
	hud.ring.Visible = false
	for _, glow in hud.glows do
		glow.BackgroundTransparency = 1
	end
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
		showCaughtBanner(catch, prefix .. upperName)
	end
end

return RevealController
