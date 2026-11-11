-- The look of the catch banners, in one place so they stay in step: the lucky catch banner everyone sees for a
-- very rare catch (LuckyBannerController, full size, a clover on the left) and the smaller "YOU CAUGHT" banner
-- after your own rare catch (RevealController, your monster on the left). A panel in the luck tier's colours
-- with glossy stripes, three centred lines (who caught / the catch in its rarity colour / the odds) and the tier's
-- sticker on the top right. Mock-ups 12 and 12b in design/ui-mockups/build.py.
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local Reveal = require(ReplicatedStorage.Shared.Config.Reveal)
local UiKit = require(ReplicatedStorage.Shared.UiKit)

local CatchBannerLook = {}

-- Design pixels, from the mock-up.
CatchBannerLook.WIDTH, CatchBannerLook.HEIGHT = 880, 196
CatchBannerLook.ART_SIZE = 176 -- the clover or monster overlapping the panel's left side
local WIDTH, HEIGHT = CatchBannerLook.WIDTH, CatchBannerLook.HEIGHT
local PANEL_LEFT, PANEL_TOP, PANEL_HEIGHT = 78, 30, 150
local RAINBOW_SECONDS = 4 -- one full turn of the GODLY panel's rainbow

function CatchBannerLook.tierFor(oneIn: number)
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

-- The banner, hidden, in `gui`, drawn `scale` times its design size. Put the clover or monster at
-- `parts.artPosition` (ART_SIZE square) with ZIndex 3.
function CatchBannerLook.build(gui: Instance, name: string, scale: number)
	local banner = Instance.new("Frame")
	banner.Name = name
	banner.AnchorPoint = Vector2.new(0.5, 0)
	banner.Size = UDim2.fromOffset(WIDTH, HEIGHT)
	banner.BackgroundTransparency = 1
	banner.Visible = false
	banner.Parent = gui
	local uiScale = Instance.new("UIScale")
	uiScale.Scale = scale
	uiScale.Parent = banner

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

	return {
		banner = banner,
		scale = uiScale,
		panelGradient = panelGradient,
		who = line(lines, 28, 1),
		what = line(lines, 37, 2, 6),
		odds = line(lines, 40, 3),
		artPosition = UDim2.fromOffset(0, 4),
		sticker = nil,
	}
end

-- Fills the banner in for a catch: its lines, the tier's panel colours and sticker. Returns a stop function for
-- the GODLY rainbow's turning (does nothing for other tiers); call it once the banner is gone.
function CatchBannerLook.paint(parts, who: string, what: string, dinoId: string, odds: string, oneIn: number): () -> ()
	local tier = CatchBannerLook.tierFor(oneIn) or Reveal.tiers[#Reveal.tiers]
	parts.who.Text = who
	parts.what.Text = what
	parts.what.TextColor3 = Color3.fromHex(UiKit.RARITY_TEXT[UiKit.rarityOf(dinoId)])
	parts.odds.Text = odds

	local rainbow = #tier.panel > 2
	parts.panelGradient.Color = sequence(tier.panel)
	parts.panelGradient.Rotation = if rainbow then 10 else 90

	if parts.sticker then
		parts.sticker:Destroy()
	end
	local sticker = UiKit.tag(parts.banner, tier.sticker.label, tier.sticker.colors, 26, 7)
	sticker.AnchorPoint = Vector2.new(1, 0)
	sticker.Position = UDim2.new(1, 10, 0, 0)
	sticker.ZIndex = 4
	parts.sticker = sticker

	if not rainbow then
		return function() end
	end
	local spin = RunService.RenderStepped:Connect(function()
		parts.panelGradient.Rotation = 10 + (os.clock() % RAINBOW_SECONDS) / RAINBOW_SECONDS * 360
	end)
	return function()
		spin:Disconnect()
	end
end

return CatchBannerLook
