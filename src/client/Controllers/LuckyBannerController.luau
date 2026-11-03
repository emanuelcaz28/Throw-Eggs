-- The lucky catch banner (mock-ups 12 and 12b in design/ui-mockups/build.py): when anyone in the
-- server catches something rare, a big banner drops in at the top centre for everyone, even while
-- training. A clover overlaps its left side, a sticker with the luck tier sits on the top right,
-- and the panel takes the tier's colour.
--
-- One banner at a time; a rarer catch waiting in line goes first. Banners wait while your own
-- reveal plays, and your own catch is queued once its reveal is over.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")

local Catch = require(ReplicatedStorage.Shared.Config.Catch)
local Reveal = require(ReplicatedStorage.Shared.Config.Reveal)
local DinoStats = require(ReplicatedStorage.Shared.DinoStats)
local Format = require(ReplicatedStorage.Shared.Format)
local UiKit = require(ReplicatedStorage.Shared.UiKit)
local RevealController = require(script.Parent.RevealController)

local player = Players.LocalPlayer
local settings = Reveal.luckyBanner

local LuckyBannerController = {}

-- Design pixels, from the mock-up.
local WIDTH, HEIGHT = 880, 196
local PANEL_LEFT, PANEL_TOP, PANEL_HEIGHT = 78, 30, 150
local CLOVER_SIZE = 176
local RAINBOW_SECONDS = 4 -- one full turn of the GODLY panel's rainbow

local hud = nil
local queue = {}
local showing = false

local function tween(instance: Instance, time: number, goal, style: Enum.EasingStyle?, direction: Enum.EasingDirection?)
	local created = TweenService:Create(
		instance,
		TweenInfo.new(time, style or Enum.EasingStyle.Quad, direction or Enum.EasingDirection.Out),
		goal
	)
	created:Play()
	return created
end

local function tierFor(oneIn: number)
	local current = nil
	for _, tier in Reveal.tiers do
		if oneIn >= tier.minOneIn then
			current = tier
		end
	end
	return current
end

-- A ColorSequence through any number of hex colours, evenly spaced.
local function sequence(colors: { string }): ColorSequence
	local points = {}
	for index, hex in colors do
		table.insert(points, ColorSequenceKeypoint.new((index - 1) / (#colors - 1), Color3.fromHex(hex)))
	end
	return ColorSequence.new(points)
end

-- One centred line of outlined text that shrinks if a long name wouldn't fit.
local function line(parent: Instance, size: number, order: number, stroke: number?): TextLabel
	local label = UiKit.text(parent, "", size)
	label.LayoutOrder = order
	label.TextScaled = true
	local limit = Instance.new("UITextSizeConstraint")
	limit.MaxTextSize = size
	limit.Parent = label
	if stroke then
		label:FindFirstChildOfClass("UIStroke").Thickness = stroke
	end
	return label
end

local function buildGui()
	local gui = Instance.new("ScreenGui")
	gui.Name = "LuckyBannerHud"
	gui.IgnoreGuiInset = true
	gui.ResetOnSpawn = false
	gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	gui.DisplayOrder = 9 -- over the HUD and panels, under the reveal
	gui.Parent = player:WaitForChild("PlayerGui")

	local banner = Instance.new("Frame")
	banner.Name = "LuckyBanner"
	banner.AnchorPoint = Vector2.new(0.5, 0)
	banner.Size = UDim2.fromOffset(WIDTH, HEIGHT)
	banner.BackgroundTransparency = 1
	banner.Visible = false
	banner.Parent = gui
	local scale = Instance.new("UIScale")
	scale.Scale = UiKit.scale()
	scale.Parent = banner

	local panel = Instance.new("Frame")
	panel.Name = "Panel"
	panel.Position = UDim2.fromOffset(PANEL_LEFT, PANEL_TOP)
	panel.Size = UDim2.fromOffset(WIDTH - 96, PANEL_HEIGHT)
	panel.ClipsDescendants = true
	panel.Parent = banner
	local panelGradient = UiKit.gradient(panel, { "#ffffff", "#ffffff" })
	UiKit.corner(panel, 32)
	UiKit.stroke(panel, 6)
	-- The glossy diagonal stripes on the right, as on the panel headers.
	for i = 0, 4 do
		local stripe = Instance.new("Frame")
		stripe.BackgroundColor3 = Color3.new(1, 1, 1)
		stripe.BackgroundTransparency = 0.78
		stripe.BorderSizePixel = 0
		stripe.Rotation = 25
		stripe.Position = UDim2.new(0.66, i * 52, 0, -50)
		stripe.Size = UDim2.fromOffset(26, PANEL_HEIGHT + 100)
		stripe.Parent = panel
	end

	-- Three centred lines, nudged right of the clover.
	local lines = Instance.new("Frame")
	lines.BackgroundTransparency = 1
	lines.Position = UDim2.fromOffset(64 + 24, 0)
	lines.Size = UDim2.new(1, -64 - 48, 1, 0)
	lines.ZIndex = 2
	lines.Parent = panel
	local layout = Instance.new("UIListLayout")
	layout.HorizontalAlignment = Enum.HorizontalAlignment.Center
	layout.VerticalAlignment = Enum.VerticalAlignment.Center
	layout.SortOrder = Enum.SortOrder.LayoutOrder
	layout.Padding = UDim.new(0, 0)
	layout.Parent = lines
	local who = line(lines, 28, 1)
	local what = line(lines, 37, 2, 6)
	local odds = line(lines, 40, 3)

	local clover = UiKit.art(banner, "clover", "clover", {
		position = UDim2.fromOffset(0, 4),
		size = UDim2.fromOffset(CLOVER_SIZE, CLOVER_SIZE),
	})
	clover.ZIndex = 3

	return {
		banner = banner,
		scale = scale,
		panelGradient = panelGradient,
		who = who,
		what = what,
		odds = odds,
		clover = clover,
		cloverModel = clover:FindFirstChildOfClass("Model"),
		sticker = nil,
	}
end

-- The catch line: size, mutation, then the dino, e.g. "HUGE DIAMOND SPINOSAURUS".
local function catchName(announcement): string
	local parts = {}
	local size = DinoStats.findOption(Catch.sizes, announcement.size)
	local mutation = DinoStats.findOption(Catch.mutations, announcement.mutation)
	if size then
		table.insert(parts, size.name)
	end
	if mutation then
		table.insert(parts, mutation.name)
	end
	table.insert(parts, string.upper(announcement.name))
	return table.concat(parts, " ")
end

-- The clover lands with a half turn.
local function spinClover()
	local model = hud.cloverModel
	if not model then
		return
	end
	local start = model:GetPivot()
	local began = os.clock()
	local connection
	connection = RunService.RenderStepped:Connect(function()
		local t = math.min((os.clock() - began) / settings.dropTime, 1)
		local eased = TweenService:GetValue(t, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)
		model:PivotTo(start * CFrame.Angles(0, math.pi * (eased - 1), 0))
		if t >= 1 then
			connection:Disconnect()
		end
	end)
end

local function show(announcement)
	local tier = tierFor(announcement.oneIn) or Reveal.tiers[#Reveal.tiers]

	hud.who.Text = `{announcement.player} CAUGHT`
	hud.what.Text = catchName(announcement)
	hud.what.TextColor3 = Color3.fromHex(UiKit.RARITY_TEXT[UiKit.rarityOf(announcement.id)])
	hud.odds.Text = `1 in {Format.short(announcement.oneIn)}`

	local rainbow = #tier.panel > 2
	hud.panelGradient.Color = sequence(tier.panel)
	hud.panelGradient.Rotation = if rainbow then 10 else 90

	if hud.sticker then
		hud.sticker:Destroy()
	end
	local sticker = UiKit.tag(hud.banner, tier.sticker.label, tier.sticker.colors, 26, 7)
	sticker.AnchorPoint = Vector2.new(1, 0)
	sticker.Position = UDim2.new(1, 10, 0, 0)
	sticker.ZIndex = 4
	hud.sticker = sticker

	local rainbowSpin = nil
	if rainbow then
		rainbowSpin = RunService.RenderStepped:Connect(function()
			hud.panelGradient.Rotation = 10 + (os.clock() % RAINBOW_SECONDS) / RAINBOW_SECONDS * 360
		end)
	end

	local hidden = UDim2.new(0.5, 0, 0, -(HEIGHT + 20) * hud.scale.Scale)
	hud.banner.Position = hidden
	hud.banner.Visible = true
	spinClover()
	tween(hud.banner, settings.dropTime, { Position = UDim2.new(0.5, 0, 0, 6) }, Enum.EasingStyle.Back)
	task.wait(settings.dropTime + settings.holdTime)
	tween(hud.banner, settings.leaveTime, { Position = hidden }, Enum.EasingStyle.Quad, Enum.EasingDirection.In).Completed:Wait()
	hud.banner.Visible = false
	if rainbowSpin then
		rainbowSpin:Disconnect()
	end
end

-- Shows queued banners one after another, rarest first, never during your own reveal.
local function runQueue()
	if showing then
		return
	end
	showing = true
	task.spawn(function()
		while #queue > 0 do
			while RevealController.isPlaying() do
				task.wait(0.2)
			end
			show(table.remove(queue, 1))
			task.wait(settings.gap)
		end
		showing = false
	end)
end

function LuckyBannerController.announce(announcement)
	table.insert(queue, announcement)
	table.sort(queue, function(a, b)
		return a.oneIn > b.oneIn
	end)
	while #queue > settings.maxQueue do
		table.remove(queue)
	end
	runQueue()
end

function LuckyBannerController.start()
	hud = buildGui()

	local remotes = ReplicatedStorage:WaitForChild("ThrowRemotes")
	remotes:WaitForChild("LuckyCatch").OnClientEvent:Connect(LuckyBannerController.announce)

	-- Your own lucky catch, once you've tapped through its reveal.
	RevealController.finished:Connect(function(catch)
		if catch.oneIn >= settings.minOneIn then
			LuckyBannerController.announce({
				player = player.Name,
				id = catch.id,
				name = catch.name,
				size = catch.size,
				mutation = catch.mutation,
				oneIn = catch.oneIn,
			})
		end
	end)
end

return LuckyBannerController
