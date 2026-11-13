-- The Robux shop panel, built from Figma "Shop" page "Shop v2" (2026-11-12). Display and prompts only: Roblox
-- handles the payment, and the server decides what it grants. A rail on the left stays put while the list scrolls:
-- a tap scrolls to that section, and the section in view is lit. Sections: Special Monsters (a featured card per pass
-- monster, then the Prism Egg), Boosts (lucky throws, Server Luck), Cash packs, Throw Power packs, Passes (x2 Cash,
-- x2 Training, x2 Power) and Free (the starter monster). The GIFT buttons open the Gift panel (GiftController).
-- One look for every card: a darker stage with the art in a pool of light, one big number, the price. Only the top
-- items get rays, a gold edge or sparkles. The monsters are the real models playing their own idle
-- (DinoLifeController.showcase). Effects run only while the panel is open.
-- What plays after a purchase is PurchaseMoments (started from here).
local ContentProvider = game:GetService("ContentProvider")
local MarketplaceService = game:GetService("MarketplaceService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")

local DinoLifeController = require(script.Parent.DinoLifeController)
local DinoStats = require(ReplicatedStorage.Shared.DinoStats)
local Format = require(ReplicatedStorage.Shared.Format)
local GiftController = require(script.Parent.GiftController)
local Gifts = require(ReplicatedStorage.Shared.Gifts)
local HudStyle = require(ReplicatedStorage.Shared.HudStyle)
local LuckyThrows = require(ReplicatedStorage.Shared.LuckyThrows)
local PopText = require(ReplicatedStorage.Shared.PopText)
local PrismEgg = require(script.Parent.PrismEgg)
local PurchaseMoments = require(script.Parent.PurchaseMoments)
local Shop = require(ReplicatedStorage.Shared.Config.Shop)
local ShopLook = require(script.Parent.ShopLook)
local ShopMoments = require(ReplicatedStorage.Shared.Config.ShopMoments)
local Specials = require(ReplicatedStorage.Shared.Config.Specials)
local UiKit = require(ReplicatedStorage.Shared.UiKit)

local player = Players.LocalPlayer

local ShopController = {}

local PANEL_SIZE = Vector2.new(1064, 690)
local LIST_WIDTH = 916
local VIEW_HEIGHT = 590 -- how much of the list shows at once
local WHITE = Color3.new(1, 1, 1)
local GOLD = { "#fff1a8", "#ffb21a" }
local RAINBOW = { "#ff4f6d", "#ffb21a", "#fff15a", "#5aff8a", "#4fc8ff", "#9a6bff", "#ff4fd8" }
-- The Prism Egg's tiers, most common first: card colour, light colour.
local TIERS = { { "#2f8fe6", "#9ad9ff" }, { "#9150e8", "#dcb0ff" }, { "#e8265a", "#ffd23f" } }
local CASH_CARDS = { { "#b4ff9a", "#3aa648" }, { "#98f584", "#2d9c4a" }, { "#7ae890", "#208b52" }, { "#5fe0a0", "#0f6f58" } }
local POWER_CARDS = { { "#ffe680", "#ff9a2e" }, { "#ffdb5c", "#ff7f1f" }, { "#ffcf4a", "#f25a16" } }
local RAIL_ON, RAIL_OFF = { "#ffd23f", "#ff8a1f" }, { "#43377a", "#2f2558" }

local hex = ShopLook.hex
local at = ShopLook.at
local blank = ShopLook.blank
local block = ShopLook.block

-- Everything that moves while the panel is open.
local fx = ShopLook.effects()

-- A card's face: a gradient from top to bottom, with a darker lip along its bottom edge.
local function face(frame: GuiObject, colours: { string }, height: number)
	local lipAt = 1 - 9 / height
	local keys = {}
	for index, colour in colours do
		keys[index] = ColorSequenceKeypoint.new((index - 1) / (#colours - 1) * (lipAt - 0.002), hex(colour))
	end
	local lip = hex(colours[#colours]):Lerp(Color3.new(0, 0, 0), 0.28)
	table.insert(keys, ColorSequenceKeypoint.new(lipAt, lip))
	table.insert(keys, ColorSequenceKeypoint.new(1, lip))
	frame.BackgroundColor3 = WHITE
	local gradient = Instance.new("UIGradient")
	gradient.Color = ColorSequence.new(keys)
	gradient.Rotation = 90
	gradient.Parent = frame
end

-- A card: its face, rounded, an ink edge, a thin highlight along the top. Children may spill outside it.
local function card(parent: Instance, name: string, x: number, y: number, w: number, h: number, colours: { string }, radius: number?): Frame
	local frame = Instance.new("Frame")
	frame.Name = name
	frame.BorderSizePixel = 0
	at(frame, x, y, w, h)
	frame.Parent = parent
	face(frame, colours, h)
	UiKit.corner(frame, radius or 24)
	UiKit.stroke(frame, 5)
	block(frame, "Highlight", WHITE, 16, 4, w - 32, 3, 0.3, 2)
	return frame
end

-- A layer inside a rounded shape that clips its effects. A plain clipping Frame, set in far enough that the rounded
-- corners hide its square ones: a CanvasGroup would clip to the rounded shape, but in Studio any ViewportFrame drawn
-- after one in the panel stopped showing (the monsters vanished).
local function decor(frame: GuiObject, w: number, h: number, radius: number): Frame
	local inset = math.ceil(radius * 0.3)
	local holder = blank(frame, "Decor")
	holder.Position = UDim2.fromOffset(inset, inset)
	holder.Size = UDim2.fromOffset(w - 2 * inset, h - 2 * inset)
	holder.ClipsDescendants = true
	-- What's drawn inside uses the card's own coordinates.
	local layer = blank(holder, "Layer")
	layer.Position = UDim2.fromOffset(-inset, -inset)
	layer.Size = UDim2.fromOffset(w, h)
	return layer
end

-- A card with a darker stage across its top for the art, in a pool of light. options: rays (light rays turning in
-- the stage), gold (a gold edge): only for the top item of a row.
local function stageCard(parent: Instance, name: string, x: number, w: number, h: number, colours: { string }, stageHeight: number, options): Frame
	local frame = card(parent, name, x, 0, w, h, colours)
	local well = block(frame, "Stage", UiKit.INK, 10, 10, w - 20, stageHeight, 0.34, 16)
	local layer = decor(well, w - 20, stageHeight, 16)
	if options.rays then
		fx.rays(layer, WHITE, (w - 20) / 2, stageHeight / 2, w * 0.7, 0.22)
	end
	fx.glow(layer, WHITE, (w - 20) / 2, stageHeight / 2 + 6, (w - 20) * 0.95, stageHeight * 1.5, 0.62, x)
	if options.gold then
		ShopLook.innerEdge(frame, 24, 4, GOLD)
	end
	return frame
end

local function label(parent: Instance, value: string, size: number, colour: Color3?, align: Enum.TextXAlignment?, x: number, y: number, w: number): TextLabel
	return at(UiKit.text(parent, value, size, colour, align or Enum.TextXAlignment.Left), x, y, w, math.ceil(size * 1.25))
end

local function centred(parent: Instance, value: string, size: number, colour: Color3?, y: number, w: number): TextLabel
	return label(parent, value, size, colour, Enum.TextXAlignment.Center, 0, y, w)
end

-- Text whose right end sits at x.
local function rightText(parent: Instance, value: string, size: number, colour: Color3?, x: number, y: number): TextLabel
	return label(parent, value, size, colour, Enum.TextXAlignment.Right, x - 400, y, 400)
end

-- Small plain text with no outline, for the quiet lines.
local function quiet(parent: Instance, value: string, size: number, colour: Color3, align: Enum.TextXAlignment, x: number, y: number, w: number): TextLabel
	local text = label(parent, value, size, colour, align, x, y, w)
	text.FontFace = UiKit.BODY
	text:FindFirstChildOfClass("UIStroke").Enabled = false
	return text
end

-- Things side by side, each as wide as its words: a row starting at (x, y).
local function side(parent: Instance, name: string, x: number, y: number, h: number, gap: number): Frame
	local row = blank(parent, name)
	at(row, x, y, 0, h)
	row.AutomaticSize = Enum.AutomaticSize.X
	local layout = Instance.new("UIListLayout")
	layout.FillDirection = Enum.FillDirection.Horizontal
	layout.VerticalAlignment = Enum.VerticalAlignment.Center
	layout.Padding = UDim.new(0, gap)
	layout.SortOrder = Enum.SortOrder.LayoutOrder
	layout.Parent = row
	return row
end

local function fitted(parent: Instance, value: string, size: number, colour: Color3?, order: number): TextLabel
	local text = UiKit.text(parent, value, size, colour, Enum.TextXAlignment.Left)
	text.AutomaticSize = Enum.AutomaticSize.X
	text.Size = UDim2.fromScale(0, 1)
	text.LayoutOrder = order
	return text
end

-- A small dark pill with a coloured edge and quiet words in it. Returns its label.
local function chip(parent: Instance, value: string, colour: Color3, x: number, y: number, h: number, textSize: number): (Frame, TextLabel)
	local pill = block(parent, "Chip", UiKit.INK, x, y, 0, h, 0.7, h / 2)
	pill.AutomaticSize = Enum.AutomaticSize.X
	local edge = UiKit.stroke(pill, 2, colour)
	edge.Transparency = 0.1
	local pad = Instance.new("UIPadding")
	pad.PaddingLeft = UDim.new(0, 10)
	pad.PaddingRight = UDim.new(0, 10)
	pad.Parent = pill
	local text = UiKit.text(pill, value, textSize, colour)
	text.FontFace = UiKit.BODY
	text.AutomaticSize = Enum.AutomaticSize.X
	text.Size = UDim2.fromScale(0, 1)
	text:FindFirstChildOfClass("UIStroke").Enabled = false
	return pill, text
end

-- The live monster on a card: the real model playing its idle, seen three-quarters on, its feet at (cx, bottom).
local live: { Model } = {}
local function monster(parent: Instance, id: string, cx: number, bottom: number, w: number, h: number, turn: number?, zoom: number?)
	local view, model = UiKit.monster(parent, id, { live = true, aspect = w / h, zoom = zoom or 0.92, turn = turn })
	view.Name = "Monster"
	view.AnchorPoint = Vector2.new(0.5, 1)
	view.Position = UDim2.fromOffset(cx, bottom)
	view.Size = UDim2.fromOffset(w, h)
	view.ZIndex = 3
	view.Ambient = Color3.fromRGB(170, 160, 190)
	view.LightColor = WHITE
	view.LightDirection = Vector3.new(-0.4, -1, -0.8)
	table.insert(live, model)
	return view
end

local function buyButton(parent: Instance, x: number, y: number, w: number, h: number, textSize: number): TextButton
	local button = UiKit.button(parent, "SOON", "grey", w, h, textSize)
	button.Position = UDim2.fromOffset(x, y)
	button.ZIndex = 4
	return button
end

local function giftButton(parent: Instance, value: string, x: number, y: number, w: number, h: number, textSize: number): TextButton
	local button = UiKit.button(parent, value, "berry", w, h, textSize)
	button.Position = UDim2.fromOffset(x, y)
	button.ZIndex = 4
	return button
end

-- A tilted sticker over a card's top edge. right: x is where its right end sits.
local function sticker(parent: Instance, value: string, style, x: number, y: number, tilt: number, textSize: number?, right: boolean?)
	local tag = UiKit.tag(parent, value, style, textSize or 19, tilt)
	if right then
		tag.AnchorPoint = Vector2.new(1, 0)
	end
	tag.Position = UDim2.fromOffset(x, y)
	tag.ZIndex = 5
	for _, child in tag:GetDescendants() do
		if child:IsA("GuiObject") then
			child.ZIndex = 5
		end
	end
	return tag
end

local function sparkles(parent: Instance, spots: { { number } })
	for index, spot in spots do
		fx.sparkle(parent, spot[1], spot[2], spot[3], index * 1.3 + spot[1])
	end
end

-- A section's heading: a coloured bar, its name, a faint line to the right edge.
local function head(list: Instance, value: string, colour: string, order: number): Frame
	local frame = blank(list, `Section {value}`)
	frame.Size = UDim2.fromOffset(LIST_WIDTH, 40)
	frame.LayoutOrder = order
	UiKit.stroke(block(frame, "Bar", hex(colour), 2, 6, 10, 28, 1, 5), 3)
	local row = side(frame, "Row", 26, 0, 40, 16)
	row.AutomaticSize = Enum.AutomaticSize.None
	row.Size = UDim2.fromOffset(LIST_WIDTH - 26, 40)
	fitted(row, value, 27, nil, 1)
	local line = block(row, "Line", WHITE, 0, 0, 0, 4, 0.1, 2)
	line.LayoutOrder = 2
	local fill = Instance.new("UIFlexItem")
	fill.FlexMode = Enum.UIFlexMode.Fill
	fill.Parent = line
	return frame
end

-- A pass monster's featured card: red rays, a glow and rising embers, the monster bursting out over the top edge,
-- its name, its share of your best, what it would earn now, the buy and gift buttons.
local function featured(list: Instance, special, order: number)
	local w, h = LIST_WIDTH, 372
	local frame = card(list, `Featured {special.id}`, 0, 0, w, h, { "#6a0f22", "#2a0711", "#0c0308" }, 26)
	frame.LayoutOrder = order
	frame.ZIndex = 2
	local layer = decor(frame, w, h, 26)
	fx.rays(layer, hex("#ff3b4f"), 660, 180, 560, 0.32)
	fx.glow(layer, hex("#ff2438"), 660, 190, 800, 600, 0.62)
	ShopLook.fade(block(layer, "Fog", hex("#0c0308"), 0, 230, w, 142), 1, 0.05)
	ShopLook.fade(block(layer, "Text shade", hex("#16040a"), 0, 0, 480, h), 0.15, 1, 0)
	fx.embers(layer, { { 520, 160, 7 }, { 860, 330, 6 }, { 470, 320, 5 }, { 890, 190, 9 }, { 560, 350, 8 }, { 790, 130, 5 }, { 430, 250, 4 }, { 700, 360, 5 } }, 150)
	monster(frame, special.id, 664, 372, 600, 470, math.rad(55), 0.74)
	sparkles(frame, { { 430, 70, 24 }, { 902, 150, 18 }, { 880, 330, 22 }, { 560, 268, 14 } })
	sticker(frame, "BEST VALUE!", "tagGold", 22, -18, -4)
	local pill = chip(frame, "GAME PASS · YOURS FOREVER", hex("#ffb0bc"), 34, 36, 28, 14)
	pill.BackgroundColor3 = hex("#0c0308")
	pill.ZIndex = 4
	local name = label(frame, string.upper(special.name), 84, nil, nil, 30, 58, 600)
	ShopLook.paint(name, { "#ffffff", "#ffc2c9" })
	local shareRow = side(frame, "Share", 32, 160, 76, 14)
	ShopLook.paint(fitted(shareRow, `{special.share * 100}%`, 62, nil, 1), GOLD)
	local of = fitted(shareRow, "OF YOUR BEST\nMONSTER", 21, nil, 2)
	of.LineHeight = 1.05
	local incomeRow = side(frame, "Income", 34, 236, 50, 14)
	local income = fitted(incomeRow, "", 40, UiKit.CASH, 1)
	local best = fitted(incomeRow, "", 17, hex("#b9aeb4"), 2)
	best.FontFace = UiKit.BODY
	best:FindFirstChildOfClass("UIStroke").Enabled = false
	local button = buyButton(frame, 34, 296, 230, 62, 30)
	local gift = giftButton(frame, "🎁 GIFT", 276, 296, 140, 62, 24)
	-- The monster's view spreads across the card: the words stay over its tail.
	for _, child in { name, shareRow, incomeRow } do
		child.ZIndex = 4
	end
	return { item = special, button = button, income = income, best = best, gift = gift }
end

-- One of the Prism Egg's monsters on its own small card inside the egg's card.
local function hatchCard(parent: Instance, option, index: number, x: number, y: number, w: number, h: number, jackpot: boolean)
	local special = DinoStats.special(option.id)
	local tier = TIERS[index] or TIERS[#TIERS]
	local colour, light = hex(tier[1]), hex(tier[2])
	local frame = card(parent, `Hatch {option.id}`, x, y, w, h, if jackpot then { tier[1], "#3a0a1f", "#140c2c" } else { tier[1], "#140c2c" }, if jackpot then 22 else 20)
	frame:FindFirstChildOfClass("UIStroke").Thickness = 4
	frame.ZIndex = 2
	local layer = decor(frame, w, h, 20)
	local turn = math.rad(if option.id == "Umbray" then 22 else 50) -- the ray's wings read best nearly face on
	local share, income
	if jackpot then
		fx.rays(layer, hex("#ffd23f"), w / 2, 128, 230, 0.28)
		fx.glow(layer, hex("#ff6a8a"), w / 2, 128, 300, 280, 0.7, index)
		ShopLook.innerEdge(frame, 22, 4, GOLD)
		ShopLook.shadow(frame, w / 2, 232, 150, 16, 0.4)
		monster(frame, option.id, w / 2, 240, w + 10, 230, turn)
		sparkles(frame, { { 30, 44, 22 }, { w - 28, 196, 18 }, { 38, 206, 14 } })
		centred(frame, special.name, 30, nil, 242, w).ZIndex = 4
		local pill, text = chip(frame, `{option.chance}% CHANCE`, hex("#ffd23f"), w / 2, 284, 34, 19)
		pill.AnchorPoint = Vector2.new(0.5, 0)
		pill.BackgroundColor3 = hex("#0d0822")
		pill.ZIndex = 4
		text.FontFace = UiKit.FONT
		share = label(frame, "", 15, hex("#ffe066"), nil, 18, 330, 160)
		income = rightText(frame, "", 20, UiKit.CASH, w - 18, 326)
		sticker(frame, "JACKPOT!", { "#ff9ec4", "#e8265a" }, w + 8, -16, 5, 19, true)
	else
		fx.glow(layer, light, 124, 70, 300, 210, 0.6, index)
		ShopLook.innerEdge(frame, 20, 3, light, 0.9)
		ShopLook.shadow(frame, 124, 112, 150, 14, 0.35)
		monster(frame, option.id, 124, 118, 250, 124, turn)
		rightText(frame, `{option.chance}%`, 40, light, w - 18, 18).ZIndex = 4
		quiet(frame, "CHANCE", 14, WHITE, Enum.TextXAlignment.Right, w - 18 - 100, 68, 100).ZIndex = 4
		label(frame, special.name, 25, nil, nil, 18, 112, 200).ZIndex = 4
		share = label(frame, "", 15, hex("#ffe066"), nil, 18, 144, 160)
		income = rightText(frame, "", 20, UiKit.CASH, w - 18, 139)
	end
	share.ZIndex = 4
	income.ZIndex = 4
	return share, income, colour
end

-- The Prism Egg's card: a shimmering rainbow edge, the crystal egg turning on its pedestal, and its three monsters,
-- each with its odds (Roblox wants them shown before buying), its share and what it would earn now.
local function prismCard(list: Instance, order: number)
	local egg = Shop.prismEgg
	local w, h = LIST_WIDTH, 444
	local frame = card(list, "Prism Egg", 0, 0, w, h, { "#3d2190", "#1a0f42", "#0d0822" }, 26)
	frame.LayoutOrder = order
	frame.ZIndex = 2
	local layer = decor(frame, w, h, 26)
	ShopLook.image(layer, "glow", hex("#ff5fb0"), 30, 110, 380, 320, 0.4)
	ShopLook.image(layer, "glow", hex("#4fd8ff"), 290, 340, 380, 320, 0.32)
	ShopLook.image(layer, "glow", hex("#ffd23f"), 300, 90, 260, 220, 0.22)
	fx.rays(layer, WHITE, 154, 222, 290, 0.2)
	fx.glow(layer, hex("#e6d6ff"), 154, 222, 360, 360, 0.5)
	local edge = ShopLook.innerEdge(frame, 26, 6, RAINBOW)
	local shimmer = edge:FindFirstChildOfClass("UIGradient")
	fx.every(function(t)
		shimmer.Rotation = (t * 40) % 360
	end)
	local title = label(frame, string.upper(egg.name), 50, nil, nil, 24, 14, 280)
	local titleColours = ShopLook.paint(title, { "#ff7a8a", "#ffd23f", "#7affa0", "#6fd0ff", "#c49aff" }, 0)
	fx.every(function(t)
		titleColours.Offset = Vector2.new(0.2 * math.sin(t * 1.5), 0)
	end)
	-- The egg bobs and turns slowly on a glowing pedestal.
	ShopLook.image(frame, "glow", hex("#c9a8ff"), 154, 330, 280, 80, 0.55)
	ShopLook.pedestal(frame, 154, 330, 200, 40, hex("#e6d6ff"), 4)
	local view, lookAt = PrismEgg.view(frame, PrismEgg.build(), PrismEgg.HEIGHT * 220 / 176)
	view.AnchorPoint = Vector2.new(0.5, 0.5)
	view.Size = UDim2.fromOffset(190, 220)
	view.ZIndex = 3
	fx.every(function(t)
		lookAt(t * 0.5)
		view.Position = UDim2.fromOffset(154, 226 + 5 * math.sin(t * 1.6))
	end)
	sparkles(frame, { { 52, 150, 22 }, { 262, 128, 16 }, { 250, 270, 20 }, { 48, 280, 14 } })
	local button = buyButton(frame, 24, 366, 198, 60, 24)
	local gift = giftButton(frame, "🎁", 230, 366, 60, 60, 26)
	quiet(frame, "ONE OF THESE HATCHES", 16, hex("#c9b8ff"), Enum.TextXAlignment.Left, 314, 22, 320)
	local shares, incomes = {}, {}
	local count = #egg.hatches
	for index, option in egg.hatches do
		if index == count then
			shares[index], incomes[index] = hatchCard(frame, option, index, 656, 46, 254, 366, true)
		else
			-- The common ones stack on the left of the jackpot.
			local tall = math.floor((366 - 12 - 8 * (count - 2)) / (count - 1))
			shares[index], incomes[index] = hatchCard(frame, option, index, 312, 58 + (index - 1) * (tall + 8), 336, tall, false)
		end
	end
	return { button = button, gift = gift, shares = shares, incomes = incomes }
end

-- A boost card: the clover on its stage, a big multiplier, what it does, its state as a chip, the price.
local function boostCard(row: Instance, x: number, w: number, big: string, sub: string, description: string, colours, options)
	local frame = stageCard(row, `{big} {sub}`, x, w, 318, colours, 150, options)
	UiKit.art(frame, "clover", "clover", { yaw = math.rad(72), position = UDim2.fromOffset(92 - 76, 84 - 76), size = UDim2.fromOffset(152, 152) })
	if options.rays then
		sparkles(frame, { { 36, 34, 18 }, { 170, 36, 14 }, { 160, 138, 16 } })
	end
	rightText(frame, big, if options.rays then 64 else 58, nil, w - 22, 52)
	ShopLook.paint(rightText(frame, sub, if #sub > 6 then 19 else 22, nil, w - 22, 122), GOLD)
	local about = label(frame, description, 15, nil, Enum.TextXAlignment.Center, 16, 166, w - 32)
	about.TextWrapped = true
	about.Size = UDim2.fromOffset(w - 32, 76)
	local _, state = chip(frame, "", hex("#ffe066"), 18, 18, 22, 13)
	local button = buyButton(frame, 18, 250, w - 36, 52, 26)
	-- The regular price, crossed out beside a deal's price.
	local was = Instance.new("TextLabel")
	was.Name = "Was"
	was.BackgroundTransparency = 1
	was.FontFace = UiKit.BODY
	was.RichText = true
	was.TextSize = 17
	was.TextColor3 = WHITE
	was.TextTransparency = 0.2
	was.TextXAlignment = Enum.TextXAlignment.Left
	was.Position = UDim2.fromOffset(22, 0)
	was.Size = UDim2.new(0, 80, 1, -4)
	was.Visible = false
	was.Parent = button
	return { frame = frame, state = state, button = button, was = was }
end

-- A row of cards across the list.
local function row(list: Instance, name: string, height: number, order: number): Frame
	local frame = blank(list, name)
	frame.Size = UDim2.fromOffset(LIST_WIDTH, height)
	frame.LayoutOrder = order
	return frame
end

-- A row of pack cards: the art on its stage, the amount (the caller fills it in), the price, maybe a sticker. The
-- biggest pack gets the rays, the gold edge and the sparkles.
local function packRow(list: Instance, name: string, packs, colours: { { string } }, amountColour: Color3?, amountSize: number, gap: number, order: number)
	local frame = row(list, name, 262, order)
	local width = math.floor((LIST_WIDTH - gap * (#packs - 1)) / #packs)
	local result = { buttons = {}, amounts = {} }
	for index, pack in packs do
		local top = index == #packs
		local face = stageCard(frame, `Pack {index}`, (index - 1) * (width + gap), width, 262, colours[index] or colours[#colours], 126, { rays = top, gold = top })
		local size = if top then 166 else 150
		UiKit.art(face, pack.art, pack.art, { spin = true, position = UDim2.fromOffset(width / 2 - size / 2, 72 - size / 2), size = UDim2.fromOffset(size, size) })
		if top then
			sparkles(face, { { 30, 30, 16 }, { width - 30, 120, 14 } })
		end
		result.amounts[index] = centred(face, "", amountSize, amountColour, 140, width)
		result.buttons[index] = buyButton(face, 14, 194, width - 28, 52, 25)
		if pack.tag then
			sticker(face, pack.tag, pack.tagStyle, width + 8, -16, 3, 16, true)
		end
	end
	return result
end

-- A button on the rail: its picture and its section's name. Lit while its section is in view.
local function railButton(rail: Instance, index: number, value: string): (TextButton, UIGradient, Frame)
	local button = Instance.new("TextButton")
	button.Name = `Rail {value}`
	button.Text = ""
	button.AutoButtonColor = false
	at(button, 0, (index - 1) * 94, 92, 86)
	button.Parent = rail
	local colours = UiKit.gradient(button, RAIL_OFF)
	UiKit.corner(button, 20)
	UiKit.stroke(button, 4)
	local gloss = block(button, "Gloss", WHITE, 6, 4, 80, 26, 0.1, 14)
	centred(button, value, 13, nil, 60, 92)
	return button, colours, gloss
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
	UiKit.gradient(panel.frame, { "#281e4a", "#141026" })
	local list = UiKit.scrollList(panel.body, UDim2.fromOffset(116, 4), UDim2.new(0, 940, 0, VIEW_HEIGHT), 0)
	list.ScrollBarThickness = 8
	local pad = list:FindFirstChildOfClass("UIPadding")
	pad.PaddingTop = UDim.new(0, 14)
	pad.PaddingBottom = UDim.new(0, 22)

	-- GIFT, beside the close button so it stays in view while the list scrolls.
	local gift = UiKit.button(panel.frame, "🎁 GIFT", "berry", 150, 58, 26)
	gift.Name = "Gift"
	gift.AnchorPoint = Vector2.new(1, 0)
	gift.Position = UDim2.new(1, -panel.closeInset - 14, 0, 14)
	gift.ZIndex = 4

	-- The list is laid out top to bottom. cursor is how far down the next thing starts, so the rail knows where each
	-- section is.
	local order = 0
	local cursor = 14
	local sections: { { name: string, y: number } } = {}
	local function place(item: GuiObject, height: number)
		order += 1
		item.LayoutOrder = order
		cursor += height
	end
	local function space(height: number)
		local gap = blank(list, "Space")
		gap.Size = UDim2.fromOffset(LIST_WIDTH, height)
		place(gap, height)
	end
	local function section(railName: string, title: string, colour: string)
		table.insert(sections, { name = railName, y = cursor })
		place(head(list, title, colour, 0), 40)
	end

	-- Special monsters: a featured card per Game Pass monster, then the Prism Egg.
	section("MONSTERS", "SPECIAL MONSTERS", "#ff2438")
	local specialCards = {}
	for _, special in Specials do
		if special.passId then
			space(52) -- the monster bursts out over the card's top edge
			local made = featured(list, special, 0)
			place(list:FindFirstChild(`Featured {special.id}`) :: GuiObject, 372)
			table.insert(specialCards, made)
		end
	end
	space(22)
	local prism = prismCard(list, 0)
	place(list:FindFirstChild("Prism Egg") :: GuiObject, 444)
	space(28)

	-- Boosts: lucky throws (yours, one throw each), then Server Luck (everyone's, for a while), side by side.
	section("BOOSTS", "BOOSTS", "#b06bff")
	space(22)
	local boosts = row(list, "Boosts", 318, 0)
	place(boosts, 318)
	local boostCount = #Shop.luckyThrows + 1
	local boostGap = 17
	local boostWidth = math.floor((LIST_WIDTH - boostGap * (boostCount - 1)) / boostCount)
	local luckyCards = {}
	for index, item in Shop.luckyThrows do
		local top = index == #Shop.luckyThrows
		local made = boostCard(boosts, (index - 1) * (boostWidth + boostGap), boostWidth, `x{item.multiplier}`, "LUCK", item.description, item.colours, { rays = top })
		made.item = item
		if item.dealProductId then
			-- The one-time deal's sticker, shown until it's used.
			made.dealTag = sticker(made.frame, item.dealTag, "tagGold", 78, -18, -3)
		end
		luckyCards[index] = made
	end
	local serverLuck = Shop.serverLuck
	local luck = boostCard(boosts, (boostCount - 1) * (boostWidth + boostGap), boostWidth, `x{serverLuck.multiplier}`, "SERVER LUCK", serverLuck.description, { "#8af2a0", "#1a9a5c" }, {})
	space(28)

	-- Packs: a row of cash packs, then a row of Throw Power packs.
	section("CASH", "CASH PACKS", "#3fbf22")
	space(24)
	local cashPacks = packRow(list, "Cash packs", Shop.cashPacks, CASH_CARDS, hex("#b8ff8a"), 34, 16, 0)
	place(list:FindFirstChild("Cash packs") :: GuiObject, 262)
	space(28)
	section("POWER", "THROW POWER", "#ff8a1f")
	space(24)
	local powerPacks = packRow(list, "Power packs", Shop.powerPacks, POWER_CARDS, nil, 30, 17, 0)
	place(list:FindFirstChild("Power packs") :: GuiObject, 262)
	for index, pack in Shop.powerPacks do
		powerPacks.amounts[index].Text = `+{Format.commas(pack.amount)} POWER`
	end
	space(28)

	-- Passes: x2 Cash, x2 Training and x2 Power, side by side.
	section("PASSES", "PASSES", "#4fc8ff")
	space(22)
	local passes = row(list, "Passes", 304, 0)
	place(passes, 304)
	local passButtons = {}
	local passWidth = math.floor((LIST_WIDTH - 17 * (#Gifts.passes - 1)) / #Gifts.passes)
	for index, pass in Gifts.passes do
		local item = Shop[pass.key]
		local style = ShopMoments.pass.looks[pass.key]
		local frame = stageCard(passes, item.name, (index - 1) * (passWidth + 17), passWidth, 304, style.colours, 140, { rays = true })
		UiKit.art(frame, pass.artKey, pass.art, { yaw = math.rad(72), position = UDim2.fromOffset(98 - 75, 80 - 75), size = UDim2.fromOffset(150, 150) })
		rightText(frame, `x{item.multiplier}`, 80, nil, passWidth - 24, 32)
		ShopLook.paint(centred(frame, style.label, 27, nil, 160, passWidth), GOLD)
		local about = centred(frame, item.description, 15, nil, 196, passWidth)
		about.TextWrapped = true
		about.Position = UDim2.fromOffset(16, 196)
		about.Size = UDim2.fromOffset(passWidth - 32, 38)
		sticker(frame, "FOREVER", "tagGold", passWidth + 8, -16, 4, 16, true)
		passButtons[pass.key] = buyButton(frame, 18, 236, passWidth - 36, 52, 26)
	end
	space(28)

	-- Free: the starter monster, idling in its own light.
	section("FREE", "FREE", "#4fc8ff")
	space(26)
	local free = card(list, "Free", 0, 0, LIST_WIDTH, 132, { "#7fe7ff", "#3f6cff" })
	place(free, 132)
	local freeLayer = decor(free, LIST_WIDTH, 132, 24)
	fx.rays(freeLayer, WHITE, 104, 70, 220, 0.3)
	fx.glow(freeLayer, WHITE, 104, 70, 300, 260, 0.6)
	ShopLook.shadow(free, 104, 118, 110, 14, 0.3)
	monster(free, Shop.starterDino.id, 104, 122, 150, 132)
	label(free, "FREE MONSTER!", 40, nil, nil, 196, 22, 460)
	label(free, Shop.starterDino.description, 19, nil, nil, 198, 78, 460)
	local starterButton = UiKit.button(free, "CLAIM", "green", 200, 64, 30)
	starterButton.Position = UDim2.fromOffset(LIST_WIDTH - 228, 34)
	local bottom = cursor + 22

	-- The rail: one button per section. A tap scrolls there; the section in view is lit.
	local rail = blank(panel.body, "Rail")
	at(rail, 14, 14, 92, 556)
	local railButtons = {}
	local firstSpecial = specialCards[1] and specialCards[1].item.id
	for index, entry in sections do
		local button, colours, gloss = railButton(rail, index, entry.name)
		if entry.name == "MONSTERS" and firstSpecial then
			UiKit.monster(button, firstSpecial, { aspect = 66 / 52, position = UDim2.fromOffset(13, 5), size = UDim2.fromOffset(66, 52) })
		elseif entry.name == "BOOSTS" then
			UiKit.art(button, "clover", "clover", { yaw = math.rad(72), position = UDim2.fromOffset(19, 5), size = UDim2.fromOffset(54, 54) })
		elseif entry.name == "CASH" then
			UiKit.art(button, "cash_M", "cash_M", { position = UDim2.fromOffset(19, 5), size = UDim2.fromOffset(54, 54) })
		elseif entry.name == "POWER" then
			UiKit.art(button, "bolts_L", "bolts_L", { position = UDim2.fromOffset(19, 5), size = UDim2.fromOffset(54, 54) })
		elseif entry.name == "PASSES" then
			UiKit.art(button, "pass_cash", "cash_L", { position = UDim2.fromOffset(19, 5), size = UDim2.fromOffset(54, 54) })
		else
			local emoji = UiKit.text(button, "🎁", 34)
			emoji.Position = UDim2.fromOffset(0, 8)
			emoji:FindFirstChildOfClass("UIStroke").Enabled = false
		end
		railButtons[index] = { colours = colours, gloss = gloss }
		button.Activated:Connect(function()
			-- CanvasPosition is in screen pixels: the list's design pixels times the panel's scale.
			local goal = math.clamp(entry.y - 8, 0, math.max(bottom - VIEW_HEIGHT, 0)) * list.AbsoluteSize.Y / VIEW_HEIGHT
			TweenService:Create(list, TweenInfo.new(0.35, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), { CanvasPosition = Vector2.new(0, goal) }):Play()
		end)
	end
	local litNow = 0
	local function light()
		local y = list.CanvasPosition.Y * VIEW_HEIGHT / math.max(list.AbsoluteSize.Y, 1)
		local lit = 1
		for index, entry in sections do
			if entry.y <= y + VIEW_HEIGHT * 0.45 then
				lit = index
			end
		end
		if y >= bottom - VIEW_HEIGHT - 4 then
			lit = #sections -- the last section is short: at the very bottom it's the one in view
		end
		if lit ~= litNow then
			litNow = lit
			for index, made in railButtons do
				made.colours.Color = ShopLook.sequence(if index == lit then RAIL_ON else RAIL_OFF)
				made.gloss.BackgroundTransparency = if index == lit then 0.7 else 0.9
			end
		end
	end
	list:GetPropertyChangedSignal("CanvasPosition"):Connect(light)
	light()

	-- The list's pictures load before it's opened, so none pops in while it scrolls.
	local pictures = {}
	for _, item in panel.frame:GetDescendants() do
		if item:IsA("ImageLabel") then
			table.insert(pictures, item)
		end
	end
	task.spawn(function()
		pcall(function()
			ContentProvider:PreloadAsync(pictures)
		end)
	end)

	return {
		open = open,
		panel = panel,
		luck = luck,
		luckyCards = luckyCards,
		specialCards = specialCards,
		prism = prism,
		giftButton = gift,
		cashPacks = cashPacks,
		powerPacks = powerPacks,
		passButtons = passButtons,
		starterButton = starterButton,
	}
end

-- A paid random item the policy doesn't allow where this player is (ShopService): grey, and no price.
local function markUnavailable(button: TextButton)
	button:SetAttribute("Unavailable", true)
	UiKit.restyle(button, "UNAVAILABLE", "grey")
end

-- Asks Roblox for a price in Robux, once per item, and hands it to `use` when it comes.
local prices: { [string]: number } = {}
local function withPrice(id: number, infoType: Enum.InfoType, use: (number) -> ())
	if id == 0 then
		return
	end
	local key = `{infoType.Name}{id}`
	if prices[key] then
		use(prices[key])
		return
	end
	task.spawn(function()
		local ok, info = pcall(function()
			return MarketplaceService:GetProductInfo(id, infoType)
		end)
		if ok and info.PriceInRobux then
			prices[key] = info.PriceInRobux
			use(info.PriceInRobux)
		end
	end)
end

-- Shows the Robux price once Roblox tells us; items without an id stay "SOON". prefix goes before it ("BUY 1 ").
local function showPrice(button: TextButton, id: number, infoType: Enum.InfoType, prefix: string?)
	withPrice(id, infoType, function(price)
		if button.Text ~= "OWNED" and not button:GetAttribute("Unavailable") then
			UiKit.restyle(button, `{prefix or ""}R$ {price}`, "green")
			UiKit.shake(button) -- no zoom on Robux buttons, only a little shake every 3 seconds [Owner, 2026-11-09]
		end
	end)
end

function ShopController.start()
	local remotes = ReplicatedStorage:WaitForChild("ShopRemotes")
	local hud = buildGui()
	local claimed = false

	-- The x2 passes.
	for _, pass in Gifts.passes do
		local item = Shop[pass.key]
		local button = hud.passButtons[pass.key]
		local function renderOwned()
			if player:GetAttribute(pass.attribute) then
				UiKit.restyle(button, "OWNED", "grey")
			end
		end
		button.Activated:Connect(function()
			if item.passId ~= 0 and not player:GetAttribute(pass.attribute) then
				MarketplaceService:PromptGamePassPurchase(player, item.passId)
			end
		end)
		showPrice(button, item.passId, Enum.InfoType.GamePass)
		player:GetAttributeChangedSignal(pass.attribute):Connect(renderOwned)
		renderOwned()
	end

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
			special.best.Text = `your best now: {Format.cash(best)}/s`
		end
		player:GetAttributeChangedSignal("BestIncome"):Connect(renderIncome)
		renderIncome()
	end
	-- The Prism Egg can be bought again and again. What each of its monsters would earn follows your best.
	local prismEgg = Shop.prismEgg
	local function buyPrism()
		if prismEgg.productId ~= 0 then
			remotes.BuyRandom:FireServer(prismEgg.productId) -- the server checks the policy, then prompts
		end
	end
	hud.prism.button.Activated:Connect(buyPrism)
	showPrice(hud.prism.button, prismEgg.productId, Enum.InfoType.Product, "BUY 1   ")
	local function renderPrismIncomes()
		local best = player:GetAttribute("BestIncome") or 0
		for index, option in prismEgg.hatches do
			local special = DinoStats.special(option.id)
			hud.prism.shares[index].Text = `{special.share * 100}% OF BEST`
			hud.prism.incomes[index].Text = `+{Format.cash(math.max(best, special.minimumIncome) * special.share)}/s`
		end
	end
	player:GetAttributeChangedSignal("BestIncome"):Connect(renderPrismIncomes)
	renderPrismIncomes()
	-- A plain big message from the server for the shop, kept for anything that has no moment of its own.
	remotes.Shout.OnClientEvent:Connect(function(title: string, detail: string?)
		PopText.shout(title, detail)
	end)
	-- What plays after a purchase goes through: the egg's opening, Gloomfin's bite, a pass unlocking, a quick pop.
	PurchaseMoments.start(remotes:WaitForChild("Moment"), {
		closeShop = function()
			if hud.panel.frame.Visible then
				UiKit.closePanel(hud.panel)
			end
		end,
		buyPrism = buyPrism,
	})
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
			fx.step(os.clock())
		end
	end)

	-- Paid random items the policy doesn't allow here say UNAVAILABLE (the server refuses their prompts too).
	local function renderRestriction()
		if player:GetAttribute("PaidRandomBlocked") then
			markUnavailable(hud.prism.button)
			markUnavailable(hud.luck.button)
			for _, card in hud.luckyCards do
				markUnavailable(card.button)
				card.was.Visible = false
			end
		end
	end
	player:GetAttributeChangedSignal("PaidRandomBlocked"):Connect(renderRestriction)
	renderRestriction()

	-- Lucky throws: a card with a deal sells the deal until it's used, then the regular product. While the deal is on,
	-- the regular price shows crossed out beside it. Each card says how many of that throw you own.
	for _, card in hud.luckyCards do
		local item = card.item
		local function dealOn(): boolean
			return item.dealProductId ~= nil and not player:GetAttribute("LuckDealBought")
		end
		local function product(): number
			return if dealOn() then item.dealProductId else item.productId
		end
		local function renderDeal()
			if card.dealTag then
				card.dealTag.Visible = dealOn()
			end
			card.was.Visible = false
			showPrice(card.button, product(), Enum.InfoType.Product)
			if dealOn() then
				withPrice(item.productId, Enum.InfoType.Product, function(price)
					card.was.Text = `<s>R$ {price}</s>`
					card.was.Visible = dealOn() and not card.button:GetAttribute("Unavailable")
				end)
			end
		end
		local function renderOwned()
			local owned = LuckyThrows.count(player, item.multiplier)
			card.state.Text = if owned > 0 then `YOU HAVE {owned}` else "1 THROW"
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
	hud.luck.button.Activated:Connect(function()
		if Shop.serverLuck.productId ~= 0 then
			remotes.BuyRandom:FireServer(Shop.serverLuck.productId) -- the server checks the policy, then prompts
		end
	end)
	showPrice(hud.luck.button, Shop.serverLuck.productId, Enum.InfoType.Product)
	for _, packs in { { hud.cashPacks, Shop.cashPacks }, { hud.powerPacks, Shop.powerPacks } } do
		for index, pack in packs[2] do
			packs[1].buttons[index].Activated:Connect(function()
				if pack.productId ~= 0 then
					MarketplaceService:PromptProductPurchase(player, pack.productId)
				end
			end)
			showPrice(packs[1].buttons[index], pack.productId, Enum.InfoType.Product)
		end
	end
	-- Cash packs pay minutes of the plot's $/s, so their amounts follow it.
	local function renderCashPacks()
		local baseIncome = player:GetAttribute("BaseIncome") or 0
		for index, pack in Shop.cashPacks do
			hud.cashPacks.amounts[index].Text = `+{Format.cash(Shop.cashPackAmount(pack, baseIncome))}`
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

	hud.open.Activated:Connect(function()
		UiKit.togglePanel(hud.panel)
	end)

	-- What's active shows in the row at the bottom (BoostRowController); the Shop only says so on the Server Luck card.
	local function clock(seconds: number): string
		return string.format("%d:%02d", seconds // 60, seconds % 60)
	end
	local lastLuck = ""
	RunService.Heartbeat:Connect(function()
		local remaining = (ReplicatedStorage:GetAttribute("ServerLuckEndsAt") or 0) - workspace:GetServerTimeNow()
		local text = if remaining > 0 then `ACTIVE · {clock(remaining)}` else `+{Shop.serverLuck.seconds // 60} MIN`
		if text ~= lastLuck then
			lastLuck = text
			hud.luck.state.Text = text
		end
	end)
end

return ShopController
