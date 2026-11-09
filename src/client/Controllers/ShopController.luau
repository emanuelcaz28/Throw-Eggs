-- The Robux shop panel, built from Figma "Throw Eggs - Shop" (2026-11-06). Display and prompts only:
-- Roblox handles the payment, and the server decides what it grants. Sections: Special Monsters (a featured card per
-- pass monster, then the Prism Egg), Boosts (lucky throws, Server Luck), Packs (cash, Throw Power), Passes (x2 Cash,
-- x2 Training, x2 Power) and Free (the starter monster). The GIFT buttons open the Gift panel (GiftController).
-- The monsters are the real models playing their own idle (DinoLifeController.showcase), never spinning. Effects run
-- only while the panel is open: light rays turning, glows breathing, sparkles twinkling, the rainbow edge shimmering.
local MarketplaceService = game:GetService("MarketplaceService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local DinoLifeController = require(script.Parent.DinoLifeController)
local DinoStats = require(ReplicatedStorage.Shared.DinoStats)
local Format = require(ReplicatedStorage.Shared.Format)
local GiftController = require(script.Parent.GiftController)
local HudStyle = require(ReplicatedStorage.Shared.HudStyle)
local LuckyThrows = require(ReplicatedStorage.Shared.LuckyThrows)
local PopText = require(ReplicatedStorage.Shared.PopText)
local Shop = require(ReplicatedStorage.Shared.Config.Shop)
local Specials = require(ReplicatedStorage.Shared.Config.Specials)
local UiKit = require(ReplicatedStorage.Shared.UiKit)

local player = Players.LocalPlayer

local ShopController = {}

local PANEL_SIZE = Vector2.new(1064, 690)
local LIST_WIDTH = 1008
local GAP = 16
local RAINBOW = { "#ff4f6d", "#ffb21a", "#fff15a", "#5aff8a", "#4fc8ff", "#9a6bff", "#ff4fd8" }
-- The Prism Egg's tiers, most common first: card colour, light colour.
local TIERS = { { "#2f8fe6", "#9ad9ff" }, { "#9150e8", "#dcb0ff" }, { "#e8265a", "#ffd23f" } }

-- Things that move while the panel is open, each called with the seconds since the game started.
local effects: { (number) -> () } = {}
local function every(effect: (number) -> ())
	table.insert(effects, effect)
end

local function hex(value: string): Color3
	return Color3.fromHex(value)
end

local function at(object: GuiObject, x: number, y: number, w: number?, h: number?)
	object.Position = UDim2.fromOffset(x, y)
	if w and h then
		object.Size = UDim2.fromOffset(w, h)
	end
	return object
end

local function round(object: GuiObject, radius: UDim)
	local corner = Instance.new("UICorner")
	corner.CornerRadius = radius
	corner.Parent = object
end

local function blank(parent: Instance, name: string): Frame
	local frame = Instance.new("Frame")
	frame.Name = name
	frame.BackgroundTransparency = 1
	frame.Parent = parent
	return frame
end

local function sequence(colours: { string }): ColorSequence
	local keys = {}
	for index, colour in colours do
		table.insert(keys, ColorSequenceKeypoint.new((index - 1) / (#colours - 1), hex(colour)))
	end
	return ColorSequence.new(keys)
end

-- A gradient fill on a label's letters (its ink outline stays).
local function paint(label: TextLabel, colours: { string }, rotation: number?): UIGradient
	local gradient = Instance.new("UIGradient")
	gradient.Color = sequence(colours)
	gradient.Rotation = rotation or 90
	gradient.Parent = label
	return gradient
end

-- A soft round glow: six stacked ellipses, see-through at the edge and strongest in the middle. It breathes.
local function glow(parent: Instance, colour: Color3, cx: number, cy: number, w: number, h: number, strength: number, phase: number?)
	local holder = blank(parent, "Glow")
	holder.AnchorPoint = Vector2.new(0.5, 0.5)
	at(holder, cx, cy, w, h)
	for i = 1, 6 do
		local k = 1 - (i - 1) / 6
		local ring = Instance.new("Frame")
		ring.AnchorPoint = Vector2.new(0.5, 0.5)
		ring.Position = UDim2.fromScale(0.5, 0.5)
		ring.Size = UDim2.fromScale(k, k)
		ring.BackgroundColor3 = colour
		ring.BackgroundTransparency = 1 - strength
		ring.BorderSizePixel = 0
		ring.Parent = holder
		round(ring, UDim.new(0.5, 0))
	end
	local scale = Instance.new("UIScale")
	scale.Parent = holder
	every(function(t)
		scale.Scale = 1 + 0.06 * math.sin(t * 2.4 + (phase or 0))
	end)
	return holder
end

-- Light rays from a point, turning slowly: bars through the middle, fading out towards both ends.
local function rays(parent: Instance, colour: Color3, cx: number, cy: number, length: number, count: number, width: number)
	local hub = blank(parent, "Rays")
	hub.AnchorPoint = Vector2.new(0.5, 0.5)
	at(hub, cx, cy, length * 2, length * 2)
	for i = 1, count do
		local ray = Instance.new("Frame")
		ray.AnchorPoint = Vector2.new(0.5, 0.5)
		ray.Position = UDim2.fromScale(0.5, 0.5)
		ray.Size = UDim2.new(0, width, 1, 0)
		ray.Rotation = (i - 1) * 180 / count
		ray.BackgroundColor3 = colour
		ray.BorderSizePixel = 0
		ray.Parent = hub
		local fade = Instance.new("UIGradient")
		fade.Rotation = 90
		fade.Transparency = NumberSequence.new({
			NumberSequenceKeypoint.new(0, 1),
			NumberSequenceKeypoint.new(0.5, 0.5),
			NumberSequenceKeypoint.new(1, 1),
		})
		fade.Parent = ray
	end
	every(function(t)
		hub.Rotation = (t * 7) % 360
	end)
	return hub
end

-- A four-pointed sparkle that twinkles: grows, turns and shrinks away, then waits.
local function sparkle(parent: Instance, x: number, y: number, size: number, phase: number)
	local star = blank(parent, "Sparkle")
	star.AnchorPoint = Vector2.new(0.5, 0.5)
	at(star, x, y, size, size)
	star.ZIndex = 4
	for _, rotation in { 0, 90 } do
		local bar = Instance.new("Frame")
		bar.AnchorPoint = Vector2.new(0.5, 0.5)
		bar.Position = UDim2.fromScale(0.5, 0.5)
		bar.Size = UDim2.new(1, 0, 0.2, 0)
		bar.Rotation = rotation
		bar.BackgroundColor3 = Color3.new(1, 1, 1)
		bar.BorderSizePixel = 0
		bar.ZIndex = 4
		bar.Parent = star
		round(bar, UDim.new(1, 0))
		local taper = Instance.new("UIGradient")
		taper.Transparency = NumberSequence.new({
			NumberSequenceKeypoint.new(0, 1),
			NumberSequenceKeypoint.new(0.5, 0),
			NumberSequenceKeypoint.new(1, 1),
		})
		taper.Parent = bar
	end
	local scale = Instance.new("UIScale")
	scale.Parent = star
	every(function(t)
		scale.Scale = math.max(0, math.sin(t * 1.7 + phase)) ^ 1.5
		star.Rotation = (t * 50 + phase * 40) % 360
	end)
end

-- A glowing ring on the floor that a monster stands on.
local function pedestal(parent: Instance, cx: number, cy: number, w: number, h: number, light: Color3)
	glow(parent, light, cx, cy, w * 1.3, h * 2.6, 0.12, cx)
	local ring = Instance.new("Frame")
	ring.Name = "Pedestal"
	ring.AnchorPoint = Vector2.new(0.5, 0.5)
	at(ring, cx, cy, w, h)
	ring.BackgroundColor3 = light
	ring.BackgroundTransparency = 0.55
	ring.Parent = parent
	round(ring, UDim.new(0.5, 0))
	local inner = Instance.new("UIGradient") -- brightest at the back rim, as if lit from above
	inner.Rotation = 90
	inner.Transparency = NumberSequence.new(0, 0.6)
	inner.Parent = ring
	local edge = Instance.new("UIStroke")
	edge.Color = light
	edge.Thickness = 5
	edge.Parent = ring
	return ring
end

-- A card: a gradient face, rounded, an ink edge, a gloss across the top. Children may spill outside it.
local function card(parent: Instance, name: string, w: number, h: number, colours, order: number?): Frame
	local frame = Instance.new("Frame")
	frame.Name = name
	frame.Size = UDim2.fromOffset(w, h)
	frame.LayoutOrder = order or 0
	frame.Parent = parent
	UiKit.gradient(frame, colours, 90)
	UiKit.corner(frame, 26)
	UiKit.stroke(frame, 5)
	local gloss = Instance.new("Frame")
	gloss.Name = "Gloss"
	gloss.Position = UDim2.fromOffset(12, 8)
	gloss.Size = UDim2.new(1, -24, 0.38, 0)
	gloss.BackgroundColor3 = Color3.new(1, 1, 1)
	gloss.Parent = frame
	round(gloss, UDim.new(0, 20))
	local fade = Instance.new("UIGradient")
	fade.Rotation = 90
	fade.Transparency = NumberSequence.new(0.72, 1)
	fade.Parent = gloss
	return frame
end

-- A layer inside a card that clips its effects. A plain clipping Frame, set in a little so the rounded corners
-- hide its square ones: a CanvasGroup would clip to the rounded shape, but in Studio any ViewportFrame drawn after
-- one in the panel stopped showing (the monsters vanished).
local INSET = 8
local function decor(frame: Frame): Frame
	local layer = blank(frame, "Decor")
	layer.Position = UDim2.fromOffset(INSET, INSET)
	layer.Size = UDim2.new(1, -2 * INSET, 1, -2 * INSET)
	layer.ClipsDescendants = true
	return layer
end

local function label(parent: Instance, value: string, size: number, colour: Color3?, align: Enum.TextXAlignment?, x: number, y: number, w: number): TextLabel
	return at(UiKit.text(parent, value, size, colour, align or Enum.TextXAlignment.Left), x, y, w, math.ceil(size * 1.25))
end

local function centred(parent: Instance, value: string, size: number, colour: Color3?, y: number, w: number): TextLabel
	return label(parent, value, size, colour, Enum.TextXAlignment.Center, 0, y, w)
end

-- The live monster on a card: the real model playing its idle, seen three-quarters on, its feet at (cx, bottom).
local live: { Model } = {}
local function monster(parent: Instance, id: string, cx: number, bottom: number, w: number, h: number, turn: number?)
	local view, model = UiKit.monster(parent, id, { live = true, aspect = w / h, zoom = 0.92, turn = turn })
	view.Name = "Monster"
	view.AnchorPoint = Vector2.new(0.5, 1)
	view.Position = UDim2.fromOffset(cx, bottom)
	view.Size = UDim2.fromOffset(w, h)
	view.ZIndex = 3
	view.Ambient = Color3.fromRGB(170, 160, 190)
	view.LightColor = Color3.new(1, 1, 1)
	view.LightDirection = Vector3.new(-0.4, -1, -0.8)
	table.insert(live, model)
	return view
end

local function gift(parent: Instance, x: number, y: number, w: number, h: number): TextButton
	local button = UiKit.button(parent, "🎁 GIFT", "berry", w, h, math.floor(h * 0.4))
	button.Position = UDim2.fromOffset(x, y)
	button.ZIndex = 3
	return button
end

local function buyButton(parent: Instance, w: number, h: number): TextButton
	local button = UiKit.button(parent, "SOON", "grey", w, h, math.floor(h * 0.44))
	button.ZIndex = 3
	return button
end

local function sticker(parent: Instance, value: string, style, x: number, y: number, tilt: number?)
	local tag = UiKit.tag(parent, value, style, 20, tilt)
	tag.Position = UDim2.fromOffset(x, y)
	tag.ZIndex = 5
	for _, child in tag:GetDescendants() do
		if child:IsA("GuiObject") then
			child.ZIndex = 5
		end
	end
	return tag
end

-- A pass monster's featured card: its glow, turning rays and pedestal, the monster bursting out over the top edge,
-- its name, share of your best, what it would earn now, the buy and gift buttons.
local function featured(list: Instance, special, order: number)
	local frame = card(list, `Featured {special.id}`, LIST_WIDTH, 400, { "#4a0b17", "#0d0510" }, order)
	frame.ZIndex = 2
	local red = hex("#ff2438")
	local layer = decor(frame)
	rays(layer, red, 740, 190, 560, 7, 70)
	glow(layer, red, 740, 210, 760, 560, 0.13)
	pedestal(layer, 740, 336, 420, 74, red)
	monster(frame, special.id, 700, 404, 780, 640, math.rad(55))
	for index, spot in { { 440, 60, 26 }, { 960, 100, 20 }, { 900, 300, 24 }, { 560, 250, 16 }, { 990, 40, 14 } } do
		sparkle(frame, spot[1], spot[2], spot[3], index * 1.3)
	end
	sticker(frame, "BEST VALUE!", "tagGold", 24, -16, -4)
	label(frame, "GAME PASS · YOURS FOREVER", 19, hex("#ffb0bc"), nil, 36, 40, 420)
	paint(label(frame, string.upper(special.name), 78, nil, nil, 30, 62, 520), { "#ffffff", "#ffc2c9" })
	paint(label(frame, `{special.share * 100}% OF YOUR BEST MONSTER`, 30, nil, nil, 36, 168, 520), { "#fff1a8", "#ffb21a" })
	local income = label(frame, "", 44, UiKit.CASH, nil, 36, 208, 460)
	label(frame, special.description, 19, hex("#e8d8e0"), nil, 38, 268, 460)
	local button = buyButton(frame, 220, 76)
	button.Position = UDim2.fromOffset(36, 302)
	local giftButton = gift(frame, 272, 302, 160, 76)
	-- The monster's view spreads across the card: the words and buttons stay over its tail.
	for _, child in frame:GetChildren() do
		if child:IsA("TextLabel") or child:IsA("TextButton") then
			child.ZIndex = 4
		end
	end
	return { item = special, button = button, income = income, gift = giftButton }
end

-- The Prism Egg's card: a shimmering rainbow edge, rainbow beams, the egg, and its three monsters on glowing
-- pedestals, each with its odds (Roblox wants them shown before buying), its share and what it would earn now.
local function prismCard(list: Instance, order: number)
	local egg = Shop.prismEgg
	local frame = card(list, "Prism Egg", LIST_WIDTH, 556, { "#3b1f7a", "#0f0a26" }, order)
	frame.ZIndex = 2
	local edge = frame:FindFirstChildOfClass("UIStroke")
	edge.Color = Color3.new(1, 1, 1)
	edge.Thickness = 7
	local shimmer = Instance.new("UIGradient")
	shimmer.Color = sequence(RAINBOW)
	shimmer.Parent = edge
	every(function(t)
		shimmer.Rotation = (t * 40) % 360
	end)
	local layer = decor(frame)
	for i, colour in RAINBOW do
		local beam = Instance.new("Frame")
		beam.AnchorPoint = Vector2.new(0.5, 0.5)
		beam.Size = UDim2.fromOffset(110, 900)
		beam.Rotation = -30
		beam.BackgroundColor3 = hex(colour)
		beam.BorderSizePixel = 0
		beam.Parent = layer
		local fade = Instance.new("UIGradient")
		fade.Rotation = 90
		fade.Transparency = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.82), NumberSequenceKeypoint.new(1, 1) })
		fade.Parent = beam
		every(function(t)
			beam.Position = UDim2.fromOffset((i * 150 + t * 30) % 1150 - 70, 260)
		end)
	end
	-- The egg: a rainbow oval turning its colours, with a shine.
	local eggShape = Instance.new("Frame")
	eggShape.Name = "Egg"
	at(eggShape, 30, 22, 72, 92)
	eggShape.BackgroundColor3 = Color3.new(1, 1, 1)
	eggShape.ZIndex = 3
	eggShape.Parent = frame
	round(eggShape, UDim.new(0.5, 0))
	UiKit.stroke(eggShape, 5)
	local eggColours = Instance.new("UIGradient")
	eggColours.Color = sequence(RAINBOW)
	eggColours.Parent = eggShape
	every(function(t)
		eggColours.Rotation = (t * 60) % 360
	end)
	local shine = Instance.new("Frame")
	shine.BackgroundColor3 = Color3.new(1, 1, 1)
	shine.BackgroundTransparency = 0.3
	shine.Rotation = 20
	shine.ZIndex = 3
	at(shine, 16, 12, 16, 28)
	shine.Parent = eggShape
	round(shine, UDim.new(0.5, 0))
	local title = label(frame, string.upper(egg.name), 60, nil, nil, 120, 18, 420)
	local titleColours = paint(title, { "#ff7a8a", "#ffd23f", "#7affa0", "#6fd0ff", "#c49aff" }, 0)
	every(function(t)
		titleColours.Offset = Vector2.new(0.25 * math.sin(t * 1.5), 0)
	end)
	label(frame, egg.description, 22, nil, nil, 124, 88, 440)
	local button = buyButton(frame, 250, 76)
	button.Position = UDim2.fromOffset(LIST_WIDTH - 24 - 160 - 12 - 250, 24)
	local giftButton = gift(frame, LIST_WIDTH - 24 - 160, 24, 160, 76)
	local widths = { 296, 296, 336 }
	local x = 24
	local shares = {}
	for index, option in egg.hatches do
		local special = DinoStats.special(option.id)
		local tier = TIERS[index] or TIERS[#TIERS]
		local colour, light = hex(tier[1]), hex(tier[2])
		local w = widths[index] or widths[#widths]
		local column = card(frame, `Hatch {option.id}`, w, 380, { tier[1], "#120c26" }, index)
		column.Position = UDim2.fromOffset(x, 152)
		column.ZIndex = 2
		column:FindFirstChildOfClass("UIStroke").Color = light
		column:FindFirstChildOfClass("UIGradient").Transparency = NumberSequence.new(0.35, 0.75)
		x += w + GAP
		-- Not a clipped CanvasGroup: one here hides the monster's ViewportFrame after it (seen in Studio). The glow
		-- fits inside the card anyway.
		local inside = blank(column, "Decor")
		inside.Size = UDim2.fromScale(1, 1)
		glow(inside, colour, w / 2, 140, w * 0.95, 290, 0.16, index)
		pedestal(column, w / 2, 222, w * 0.7, 46, light)
		local jackpot = index == #egg.hatches
		local turn = math.rad(if option.id == "Umbray" then 22 else 50) -- the ray's wings read best nearly face on
		monster(column, option.id, w / 2, 250, w + (if jackpot then 90 else 40), if jackpot then 360 else 300, turn)
		centred(column, special.name, 32, nil, 262, w)
		local pill = Instance.new("Frame")
		pill.Name = "Chance"
		pill.AnchorPoint = Vector2.new(0.5, 0)
		pill.Position = UDim2.fromOffset(w / 2, 304)
		pill.Size = UDim2.fromOffset(170, 32)
		pill.BackgroundColor3 = UiKit.INK
		pill.BackgroundTransparency = 0.25
		pill.ZIndex = 3
		pill.Parent = column
		round(pill, UDim.new(0, 16))
		local pillEdge = Instance.new("UIStroke")
		pillEdge.Color = light
		pillEdge.Thickness = 3
		pillEdge.Parent = pill
		local chance = UiKit.text(pill, `{option.chance}% CHANCE`, 20, light)
		chance.Size = UDim2.fromScale(1, 1)
		chance.ZIndex = 3
		shares[index] = centred(column, "", 19, UiKit.GOLD, 344, w)
		if index == #egg.hatches then
			sticker(column, "JACKPOT!", { "#ff9ec4", "#e8265a" }, w - 140, -16, 5)
			sparkle(column, 34, 40, 22, 0.4)
			sparkle(column, w - 40, 170, 18, 2.1)
			sparkle(column, 50, 190, 14, 3.3)
		end
	end
	return { button = button, gift = giftButton, shares = shares }
end

-- A boost card: clover on a white glow, name, what it does, a big gold line, a state line and a buy button.
local function boostCard(row: Instance, name: string, description: string, big: string, colours, order: number)
	local w = (LIST_WIDTH - GAP * 2) / 3
	local frame = card(row, name, w, 360, colours, order)
	glow(frame, Color3.new(1, 1, 1), w / 2, 92, 220, 200, 0.07, order)
	UiKit.art(frame, "clover", "clover", { yaw = math.rad(72), position = UDim2.fromOffset(w / 2 - 75, 16), size = UDim2.fromOffset(150, 150) })
	centred(frame, name, 32, nil, 164, w)
	local about = centred(frame, description, 17, nil, 204, w - 32)
	about.Position = UDim2.fromOffset(16, 204)
	about.TextWrapped = true
	about.Size = UDim2.fromOffset(w - 32, 42)
	centred(frame, big, 28, UiKit.GOLD, 250, w)
	local state = centred(frame, "", 18, nil, 284, w)
	local button = buyButton(frame, 210, 58)
	button.AnchorPoint = Vector2.new(0.5, 1)
	button.Position = UDim2.new(0.5, 0, 1, -14)
	return state, button, frame
end

-- A row of cards across the list.
local function row(list: Instance, name: string, height: number, order: number): Frame
	local frame = blank(list, name)
	frame.Size = UDim2.fromOffset(LIST_WIDTH, height)
	frame.LayoutOrder = order
	local layout = Instance.new("UIListLayout")
	layout.FillDirection = Enum.FillDirection.Horizontal
	layout.Padding = UDim.new(0, GAP)
	layout.SortOrder = Enum.SortOrder.LayoutOrder
	layout.VerticalAlignment = Enum.VerticalAlignment.Bottom
	layout.Parent = frame
	return frame
end

-- A row of pack cards: art spinning on a glow, an amount (the caller fills it in), a buy button, maybe a sticker.
local function packRow(list: Instance, packs, colours, amountColour: Color3?, order: number)
	local frame = row(list, "Packs", 300, order)
	local width = math.floor((LIST_WIDTH - GAP * (#packs - 1)) / #packs)
	local result = { buttons = {}, amounts = {} }
	for index, pack in packs do
		local holder = blank(frame, "Pack")
		holder.LayoutOrder = index
		holder.Size = UDim2.fromOffset(width, 300)
		local face = card(holder, "Card", width, 284, colours, 0)
		face.Position = UDim2.fromOffset(0, 16)
		glow(face, Color3.new(1, 1, 1), width / 2, 84, 200, 170, 0.06, index)
		UiKit.art(face, pack.art, pack.art, { spin = true, position = UDim2.fromOffset(width / 2 - 85, 10), size = UDim2.fromOffset(170, 150) })
		result.amounts[index] = centred(face, "", 34, amountColour, 164, width)
		local button = buyButton(face, width - 50, 56)
		button.AnchorPoint = Vector2.new(0.5, 1)
		button.Position = UDim2.new(0.5, 0, 1, -14)
		result.buttons[index] = button
		if pack.tag then
			local tag = UiKit.tag(holder, pack.tag, pack.tagStyle, 18)
			tag.AnchorPoint = Vector2.new(0.5, 0)
			tag.Position = UDim2.fromScale(0.5, 0)
			tag.ZIndex = 2
		end
	end
	return result
end

local function buildGui()
	local gui = Instance.new("ScreenGui")
	gui.Name = "ShopHud"
	gui.ResetOnSpawn = false
	gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	gui.DisplayOrder = 4 -- above the other panels
	gui.Parent = player:WaitForChild("PlayerGui")

	local open = HudStyle.iconButton(gui, "🛍️", "Shop", "shop")
	open.AnchorPoint = Vector2.new(0, 0.5)
	open.Position = UDim2.new(0, 16, HudStyle.COLUMN_CENTER, (HudStyle.BUTTON_SIZE + HudStyle.BUTTON_GAP) / 2 * HudStyle.scale())
	open.Name = "OpenShop"

	-- [Owner, 2026-11-09] A bit smaller than before on PC, console and phone alike, and it springs up with a dark veil
	-- behind (UiKit openEffect).
	local panel = UiKit.panel(gui, {
		name = "ShopPanel",
		width = PANEL_SIZE.X,
		height = PANEL_SIZE.Y,
		header = "sun",
		title = "Shop",
		icon = "🛍️",
		iconKey = "shop",
		sizeFactor = 0.85,
		openEffect = "rise",
	})
	local list = UiKit.scrollList(panel.body, UDim2.fromOffset(16, 4), UDim2.new(1, -24, 1, -16), 30)
	local pad = list:FindFirstChildOfClass("UIPadding")
	pad.PaddingTop = UDim.new(0, 20) -- room for stickers over the first card

	-- GIFT, beside the close button so it stays in view while the list scrolls.
	local giftButton = UiKit.button(panel.frame, "🎁 GIFT", "berry", 150, 58, 26)
	giftButton.Name = "Gift"
	giftButton.AnchorPoint = Vector2.new(1, 0)
	giftButton.Position = UDim2.new(1, -panel.closeInset - 14, 0, 14)
	giftButton.ZIndex = 4

	local order = 0
	local function nextOrder(): number
		order += 1
		return order
	end

	-- Special monsters: a featured card per Game Pass monster, then the Prism Egg.
	UiKit.divider(list, "Special Monsters", LIST_WIDTH).LayoutOrder = nextOrder()
	local specialCards = {}
	for _, special in Specials do
		if special.passId then
			local spacer = blank(list, "Room above") -- the monster bursts out over the card's top edge
			spacer.Size = UDim2.fromOffset(LIST_WIDTH, 70)
			spacer.LayoutOrder = nextOrder()
			table.insert(specialCards, featured(list, special, nextOrder()))
		end
	end
	local prism = prismCard(list, nextOrder())

	-- Boosts: lucky throws (yours, one throw each), then Server Luck (everyone's, for a while), side by side.
	UiKit.divider(list, "Boosts", LIST_WIDTH).LayoutOrder = nextOrder()
	local boosts = row(list, "Boosts", 380, nextOrder())
	local luckyCards = {}
	for index, item in Shop.luckyThrows do
		local state, button, frame = boostCard(boosts, `Luck x{item.multiplier}`, item.description, `x{item.multiplier} LUCK`, item.colours, index)
		local dealTag = nil
		if item.dealProductId then
			-- The one-time deal's sticker, shown until it's used.
			dealTag = sticker(frame, item.dealTag, "tagGold", 90, -18, 4)
		end
		luckyCards[index] = { item = item, state = state, button = button, dealTag = dealTag }
	end
	local serverLuck = Shop.serverLuck
	local luckState, luckButton =
		boostCard(boosts, serverLuck.name, serverLuck.description, `x1 > x{serverLuck.multiplier}`, { "#9cf28f", "#1fa860" }, #Shop.luckyThrows + 1)

	-- Packs: a row of cash packs, then a row of Throw Power packs.
	UiKit.divider(list, "Packs", LIST_WIDTH).LayoutOrder = nextOrder()
	local cashPacks = packRow(list, Shop.cashPacks, { "#b4ff9a", "#2fae46" }, UiKit.CASH, nextOrder())
	local powerPacks = packRow(list, Shop.powerPacks, { "#ffe066", "#ff7a1a" }, nil, nextOrder())
	for index, pack in Shop.powerPacks do
		powerPacks.amounts[index].Text = `⚡ +{Format.commas(pack.amount)}`
	end

	-- Passes: x2 Cash, x2 Training and x2 Power, side by side.
	UiKit.divider(list, "Passes", LIST_WIDTH).LayoutOrder = nextOrder()
	local passes = row(list, "Passes", 340, nextOrder())
	local function passCard(item, colours, key, art, index)
		local w = (LIST_WIDTH - GAP * 2) / 3
		local frame = card(passes, item.name, w, 324, colours, index)
		glow(frame, Color3.new(1, 1, 1), w / 2, 86, 200, 170, 0.06, index)
		UiKit.art(frame, key, art, { spin = art ~= "bolts_M", yaw = math.rad(72), position = UDim2.fromOffset(w / 2 - 85, 12), size = UDim2.fromOffset(170, 150) })
		sticker(frame, "FOREVER", "tagGold", w - 128, -14, 4)
		centred(frame, item.name, 34, nil, 162, w)
		local about = centred(frame, item.description, 17, nil, 206, w - 32)
		about.Position = UDim2.fromOffset(16, 206)
		about.TextWrapped = true
		about.Size = UDim2.fromOffset(w - 32, 42)
		local button = buyButton(frame, 220, 58)
		button.AnchorPoint = Vector2.new(0.5, 1)
		button.Position = UDim2.new(0.5, 0, 1, -14)
		return button
	end
	local cashButton = passCard(Shop.doubleCash, { "#7fd4ff", "#2f6fe6" }, "pass_cash", "cash_L", 1)
	local trainingButton = passCard(Shop.doubleTraining, { "#d3a3ff", "#6b3dff" }, "pass_training", "bolts_M", 2)
	local powerButton = passCard(Shop.doublePower, { "#ffe066", "#ff7a1a" }, "bolts_XL", "bolts_XL", 3)

	-- Free: the starter monster, idling on its own pedestal.
	UiKit.divider(list, "Free", LIST_WIDTH).LayoutOrder = nextOrder()
	local free = card(list, "Free", LIST_WIDTH, 200, { "#7fe7ff", "#3f6cff" }, nextOrder())
	pedestal(free, 150, 168, 190, 36, Color3.new(1, 1, 1))
	monster(free, Shop.starterDino.id, 150, 184, 260, 190)
	label(free, "Free Monster!", 44, nil, nil, 290, 40, 440)
	label(free, Shop.starterDino.description, 22, nil, nil, 292, 104, 440)
	local starterButton = UiKit.button(free, "CLAIM", "green", 220, 70, 32)
	starterButton.AnchorPoint = Vector2.new(1, 0.5)
	starterButton.Position = UDim2.new(1, -28, 0.5, 0)

	return {
		open = open,
		panel = panel,
		luckButton = luckButton,
		luckState = luckState,
		luckyCards = luckyCards,
		specialCards = specialCards,
		prism = prism,
		giftButton = giftButton,
		cashPacks = cashPacks,
		powerPacks = powerPacks,
		cashButton = cashButton,
		trainingButton = trainingButton,
		powerButton = powerButton,
		starterButton = starterButton,
	}
end

-- A paid random item the policy doesn't allow where this player is (ShopService): grey, and no price.
local function markUnavailable(button: TextButton)
	button:SetAttribute("Unavailable", true)
	UiKit.restyle(button, "UNAVAILABLE", "grey")
end

-- Shows the Robux price once Roblox tells us; items without an id stay "SOON". prefix goes before it ("BUY 1 ").
local function showPrice(button: TextButton, id: number, infoType: Enum.InfoType, prefix: string?)
	if id == 0 then
		return
	end
	task.spawn(function()
		local ok, info = pcall(function()
			return MarketplaceService:GetProductInfo(id, infoType)
		end)
		if ok and info.PriceInRobux and button.Text ~= "OWNED" and not button:GetAttribute("Unavailable") then
			UiKit.restyle(button, `{prefix or ""}R$ {info.PriceInRobux}`, "green")
			UiKit.shake(button) -- no zoom on Robux buttons, only a little shake every 3 seconds [Owner, 2026-11-09]
		end
	end)
end

function ShopController.start()
	local remotes = ReplicatedStorage:WaitForChild("ShopRemotes")
	local hud = buildGui()
	local claimed = false

	local function renderPass(button: TextButton, attribute: string)
		if player:GetAttribute(attribute) then
			UiKit.restyle(button, "OWNED", "grey")
		end
	end

	hud.cashButton.Activated:Connect(function()
		if Shop.doubleCash.passId ~= 0 and not player:GetAttribute("HasDoubleCash") then
			MarketplaceService:PromptGamePassPurchase(player, Shop.doubleCash.passId)
		end
	end)
	hud.powerButton.Activated:Connect(function()
		if Shop.doublePower.passId ~= 0 and not player:GetAttribute("HasDoublePower") then
			MarketplaceService:PromptGamePassPurchase(player, Shop.doublePower.passId)
		end
	end)
	hud.trainingButton.Activated:Connect(function()
		if Shop.doubleTraining.passId ~= 0 and not player:GetAttribute("HasDoubleTraining") then
			MarketplaceService:PromptGamePassPurchase(player, Shop.doubleTraining.passId)
		end
	end)
	for _, special in hud.specialCards do
		local item = special.item
		local ownedAttribute = `Owns{item.id}`
		special.button.Activated:Connect(function()
			if not player:GetAttribute(ownedAttribute) then
				MarketplaceService:PromptGamePassPurchase(player, item.passId)
			end
		end)
		showPrice(special.button, item.passId, Enum.InfoType.GamePass)
		local function renderOwned()
			if player:GetAttribute(ownedAttribute) then
				UiKit.restyle(special.button, "OWNED", "grey")
			end
		end
		player:GetAttributeChangedSignal(ownedAttribute):Connect(renderOwned)
		renderOwned()
		-- What it would earn right now, worked out as the server will.
		local function renderIncome()
			local best = math.max(player:GetAttribute("BestIncome") or 0, item.minimumIncome)
			special.income.Text = `+{Format.cash(best * item.share)}/s`
		end
		player:GetAttributeChangedSignal("BestIncome"):Connect(renderIncome)
		renderIncome()
	end
	-- The Prism Egg can be bought again and again. What each of its monsters would earn follows your best.
	local prismEgg = Shop.prismEgg
	hud.prism.button.Activated:Connect(function()
		if prismEgg.productId ~= 0 then
			remotes.BuyRandom:FireServer(prismEgg.productId) -- the server checks the policy, then prompts
		end
	end)
	showPrice(hud.prism.button, prismEgg.productId, Enum.InfoType.Product, "BUY 1  ")
	local function renderPrismIncomes()
		local best = player:GetAttribute("BestIncome") or 0
		for index, option in prismEgg.hatches do
			local special = DinoStats.special(option.id)
			local income = Format.cash(math.max(best, special.minimumIncome) * special.share)
			hud.prism.shares[index].Text = `{special.share * 100}% OF BEST  ·  +{income}/s`
		end
	end
	player:GetAttributeChangedSignal("BestIncome"):Connect(renderPrismIncomes)
	renderPrismIncomes()
	-- The server's big moments for the shop: a Prism Egg hatching, a gift arriving.
	remotes.Shout.OnClientEvent:Connect(function(title: string, detail: string?)
		PopText.shout(title, detail)
	end)
	hud.giftButton.Activated:Connect(GiftController.open)
	hud.prism.gift.Activated:Connect(GiftController.open)
	for _, special in hud.specialCards do
		special.gift.Activated:Connect(GiftController.open)
	end

	-- The monsters play their own idle while the shop is open, and the effects move.
	local function shown(): boolean
		return hud.panel.frame.Visible
	end
	for _, model in live do
		DinoLifeController.showcase(model, shown)
	end
	RunService.Heartbeat:Connect(function()
		if shown() then
			local t = os.clock()
			for _, effect in effects do
				effect(t)
			end
		end
	end)

	-- Paid random items the policy doesn't allow here say UNAVAILABLE (the server refuses their prompts too).
	local function renderRestriction()
		if player:GetAttribute("PaidRandomBlocked") then
			markUnavailable(hud.prism.button)
			markUnavailable(hud.luckButton)
			for _, card in hud.luckyCards do
				markUnavailable(card.button)
			end
		end
	end
	player:GetAttributeChangedSignal("PaidRandomBlocked"):Connect(renderRestriction)
	renderRestriction()

	-- Lucky throws: a card with a deal sells the deal until it's used, then the regular product.
	-- Each card says how many of that throw you own.
	for _, card in hud.luckyCards do
		local item = card.item
		local function product(): number
			return if item.dealProductId and not player:GetAttribute("LuckDealBought") then item.dealProductId else item.productId
		end
		local function renderDeal()
			if card.dealTag then
				card.dealTag.Visible = not player:GetAttribute("LuckDealBought")
			end
			showPrice(card.button, product(), Enum.InfoType.Product)
		end
		local function renderOwned()
			local owned = LuckyThrows.count(player, item.multiplier)
			card.state.Text = if owned > 0 then `You have {owned}` else "1 throw"
		end
		card.button.Activated:Connect(function()
			if product() ~= 0 then
				remotes.BuyRandom:FireServer(product()) -- the server checks the policy, then prompts
			end
		end)
		player:GetAttributeChangedSignal("LuckDealBought"):Connect(renderDeal)
		player:GetAttributeChangedSignal(LuckyThrows.attribute(item.multiplier)):Connect(renderOwned)
		renderDeal()
		renderOwned()
	end
	hud.luckButton.Activated:Connect(function()
		if Shop.serverLuck.productId ~= 0 then
			remotes.BuyRandom:FireServer(Shop.serverLuck.productId) -- the server checks the policy, then prompts
		end
	end)
	for _, row in { { hud.cashPacks, Shop.cashPacks }, { hud.powerPacks, Shop.powerPacks } } do
		for index, pack in row[2] do
			row[1].buttons[index].Activated:Connect(function()
				if pack.productId ~= 0 then
					MarketplaceService:PromptProductPurchase(player, pack.productId)
				end
			end)
			showPrice(row[1].buttons[index], pack.productId, Enum.InfoType.Product)
		end
	end
	-- Cash packs pay minutes of the plot's $/s, so their amounts follow it.
	local function renderCashPacks()
		local baseIncome = player:GetAttribute("BaseIncome") or 0
		for index, pack in Shop.cashPacks do
			hud.cashPacks.amounts[index].Text = `💵 +{Format.cash(Shop.cashPackAmount(pack, baseIncome))}`
		end
	end
	player:GetAttributeChangedSignal("BaseIncome"):Connect(renderCashPacks)
	renderCashPacks()

	hud.starterButton.Activated:Connect(function()
		if not claimed then
			remotes.ClaimStarter:FireServer()
		end
	end)
	UiKit.pulse(hud.starterButton)
	remotes.StarterClaimed.OnClientEvent:Connect(function(isClaimed: boolean)
		claimed = isClaimed
		if claimed then
			UiKit.restyle(hud.starterButton, "CLAIMED", "grey")
		end
	end)

	showPrice(hud.cashButton, Shop.doubleCash.passId, Enum.InfoType.GamePass)
	showPrice(hud.trainingButton, Shop.doubleTraining.passId, Enum.InfoType.GamePass)
	showPrice(hud.luckButton, Shop.serverLuck.productId, Enum.InfoType.Product)
	player:GetAttributeChangedSignal("HasDoubleCash"):Connect(function()
		renderPass(hud.cashButton, "HasDoubleCash")
	end)
	player:GetAttributeChangedSignal("HasDoubleTraining"):Connect(function()
		renderPass(hud.trainingButton, "HasDoubleTraining")
	end)
	renderPass(hud.cashButton, "HasDoubleCash")
	renderPass(hud.trainingButton, "HasDoubleTraining")
	showPrice(hud.powerButton, Shop.doublePower.passId, Enum.InfoType.GamePass)
	player:GetAttributeChangedSignal("HasDoublePower"):Connect(function()
		renderPass(hud.powerButton, "HasDoublePower")
	end)
	renderPass(hud.powerButton, "HasDoublePower")

	hud.open.Activated:Connect(function()
		UiKit.togglePanel(hud.panel)
	end)

	-- What's active shows in the row at the bottom (BoostRowController); the Shop only says so on the Server Luck card.
	local function clock(seconds: number): string
		return string.format("%d:%02d", seconds // 60, seconds % 60)
	end
	RunService.Heartbeat:Connect(function()
		local now = workspace:GetServerTimeNow()
		local remaining = (ReplicatedStorage:GetAttribute("ServerLuckEndsAt") or 0) - now
		hud.luckState.Text = if remaining > 0 then `Active · {clock(remaining)} left` else `+{Shop.serverLuck.seconds // 60} min`
	end)
end

return ShopController
