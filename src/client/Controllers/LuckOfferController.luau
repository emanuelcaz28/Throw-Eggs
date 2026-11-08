-- The luck offer, from Figma "Throw Eggs - Shop" (Luck offer v2): while aiming, two glowing pills in the top left corner
-- sell the x100 and x500 lucky throws, with the one-time R$ 3 deal on the first. It's gone the moment the egg is thrown,
-- the one corner clear of the meter and Throw Power, and far from the throw tap. A pill the player already owns shows
-- USE and how many instead of the price: tapping it picks that luck for this throw (ON), tapping again un-picks it
-- [Owner, 2026-11-07]. Nothing is used up until the egg lands (ThrowService). A daily x50, which goes by itself, shows
-- as a small READY chip under the pills. DETAILS shows the real chances for this player (CatchOdds), as Roblox wants for paid
-- random items, and no throw goes while it's open (ThrowController asks blocksThrow).
local MarketplaceService = game:GetService("MarketplaceService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")

local Catch = require(ReplicatedStorage.Shared.Config.Catch)
local DeepEnd = require(ReplicatedStorage.Shared.Config.DeepEnd)
local CatchOdds = require(ReplicatedStorage.Shared.CatchOdds)
local DinoStats = require(ReplicatedStorage.Shared.DinoStats)
local Dinos = require(ReplicatedStorage.Shared.Config.Dinos)
local Eggs = require(ReplicatedStorage.Shared.Config.Eggs)
local Events = require(ReplicatedStorage.Shared.Config.Events)
local Format = require(ReplicatedStorage.Shared.Format)
local HudStyle = require(ReplicatedStorage.Shared.HudStyle)
local Icons = require(ReplicatedStorage.Shared.Config.Icons)
local Luck = require(ReplicatedStorage.Shared.Config.Luck)
local PowerLimit = require(ReplicatedStorage.Shared.Config.PowerLimit)
local LuckBoosts = require(ReplicatedStorage.Shared.LuckBoosts)
local LuckyThrows = require(ReplicatedStorage.Shared.LuckyThrows)
local Shop = require(ReplicatedStorage.Shared.Config.Shop)
local Throw = require(ReplicatedStorage.Shared.Config.Throw)
local UiKit = require(ReplicatedStorage.Shared.UiKit)
local SettingsState = require(script.Parent.SettingsState)

local player = Players.LocalPlayer

local LuckOfferController = {}

local WIDTH = 214 -- an offer's width in Figma, where everything below is measured
local PILL_X, PILL_Y, PILL_HEIGHT = 14, 4, 48
local OFFER_HEIGHT, OFFER_GAP = 86, 14
local SCREEN_WIDTH, MOST_WIDTH = 375, 300 -- its width in HUD pixels, so every phone gets the same share, and its limit
local TOP_MARGIN = 26 -- under Roblox's menu, with room for the sticker
local ROBUX = utf8.char(0xE002)
local RAINBOW = ColorSequence.new({
	ColorSequenceKeypoint.new(0, Color3.fromHex("#ff3b5c")),
	ColorSequenceKeypoint.new(0.17, Color3.fromHex("#ffb21a")),
	ColorSequenceKeypoint.new(0.33, Color3.fromHex("#fff14d")),
	ColorSequenceKeypoint.new(0.5, Color3.fromHex("#3df08a")),
	ColorSequenceKeypoint.new(0.67, Color3.fromHex("#35c8ff")),
	ColorSequenceKeypoint.new(0.83, Color3.fromHex("#b45cff")),
	ColorSequenceKeypoint.new(1, Color3.fromHex("#ff3b5c")),
})
local STYLES = {
	[100] = { colours = { "#d27bff", "#5a14c4" }, halo = "#ffd23f", header = "purple", text = { "#fff8c4", "#ffb21a" } },
	[500] = { colours = { "#ffd23f", "#ff5a1f" }, halo = "#ff4f9a", header = "sun", tag = "BIGGEST LUCK!" },
}
local RIM_TURN = 70 -- degrees a second the rainbow travels round the rim
local SHINE_EVERY = 3.5 -- seconds between shines

local prices: { [number]: number } = {}

-- The product's price from Roblox, or nil until it has answered; `done` runs once it's there.
local function priceOf(productId: number, done: () -> ()): number?
	if prices[productId] then
		return prices[productId]
	end
	task.spawn(function()
		local ok, info = pcall(function()
			return MarketplaceService:GetProductInfo(productId, Enum.InfoType.Product)
		end)
		if ok and info.PriceInRobux then
			prices[productId] = info.PriceInRobux
			done()
		end
	end)
	return nil
end

local function box(parent: Instance, name: string, x: number, y: number, width: number, height: number): Frame
	local frame = Instance.new("Frame")
	frame.Name = name
	frame.BackgroundTransparency = 1
	frame.BorderSizePixel = 0
	frame.Position = UDim2.fromOffset(x, y)
	frame.Size = UDim2.fromOffset(width, height)
	frame.Parent = parent
	return frame
end

local function tapArea(parent: Instance, name: string, x: number, y: number, width: number, height: number): TextButton
	local button = Instance.new("TextButton")
	button.Name = name
	button.Text = ""
	button.AutoButtonColor = false
	button.BorderSizePixel = 0
	button.Position = UDim2.fromOffset(x, y)
	button.Size = UDim2.fromOffset(width, height)
	button.Parent = parent
	return button
end

-- A white layer over the pill, see-through except for bands: its rounded corners match the pill's, which a clipping
-- frame's wouldn't. Returns the gradient, whose Offset moves the bands.
local function bands(parent: Instance, name: string, sequence: NumberSequence): UIGradient
	local layer = box(parent, name, 0, 0, 0, 0)
	layer.Size = UDim2.fromScale(1, 1)
	layer.BackgroundTransparency = 0
	layer.BackgroundColor3 = Color3.new(1, 1, 1)
	UiKit.corner(layer, 15)
	local gradient = Instance.new("UIGradient")
	gradient.Rotation = 20
	gradient.Transparency = sequence
	gradient.Parent = layer
	return gradient
end

local function sparkle(parent: Instance, x: number, y: number, size: number)
	local star = UiKit.text(parent, "✦", size)
	star.Position = UDim2.fromOffset(x, y)
	star.Size = UDim2.fromOffset(size, size)
	star:FindFirstChildOfClass("UIStroke").Enabled = false
	star.ZIndex = 5
	return star
end

local function priceLabel(parent: Instance, text: string, x: number, width: number, size: number, color: Color3): TextLabel
	local label = UiKit.text(parent, text, size, color)
	label.Position = UDim2.fromOffset(x, 0)
	label.Size = UDim2.new(0, width, 1, 0)
	return label
end

-- One offer. Returns its parts for the effects, and connects buy and details.
local function buildOffer(parent: Instance, item, y: number, onBuy: (number) -> (), onDetails: (any) -> (), redraw: () -> (), onUse: (number) -> (), picked: boolean)
	local style = STYLES[item.multiplier]
	local owned = LuckyThrows.count(player, item.multiplier)
	local deal = owned == 0 and item.dealProductId ~= nil and not player:GetAttribute("LuckDealBought")
	local productId = if deal then item.dealProductId else item.productId
	local offer = box(parent, `Offer{item.multiplier}`, 0, y, WIDTH, OFFER_HEIGHT)

	-- The soft glow: two rounded layers, as Roblox has no blur.
	local halos = {}
	for index, grow in { 10, 5 } do
		local halo = box(offer, "Halo", PILL_X - grow, PILL_Y - grow, WIDTH - PILL_X - 2 + grow * 2, PILL_HEIGHT + grow * 2)
		halo.BackgroundTransparency = 0.7
		halo.BackgroundColor3 = Color3.fromHex(style.halo)
		UiKit.corner(halo, 15 + grow)
		halos[index] = halo
	end

	local shadow = box(offer, "Shadow", PILL_X, PILL_Y + 3, WIDTH - PILL_X - 2, PILL_HEIGHT)
	shadow.BackgroundTransparency = 0
	shadow.BackgroundColor3 = UiKit.INK
	UiKit.corner(shadow, 15)

	local pill = tapArea(offer, "Pill", PILL_X, PILL_Y, WIDTH - PILL_X - 2, PILL_HEIGHT)
	UiKit.gradient(pill, style.colours)
	UiKit.corner(pill, 15)
	local rimStroke = Instance.new("UIStroke")
	rimStroke.ApplyStrokeMode = Enum.ApplyStrokeMode.Border
	rimStroke.Color = Color3.new(1, 1, 1)
	rimStroke.Thickness = 4
	rimStroke.Parent = pill
	local rim = Instance.new("UIGradient")
	rim.Color = RAINBOW
	rim.Parent = rimStroke

	-- Rays behind the clover, in a frame that clips them to the pill.
	local rayClip = box(pill, "Rays", 3, 3, WIDTH - PILL_X - 8, PILL_HEIGHT - 6)
	rayClip.ClipsDescendants = true
	local rays = box(rayClip, "Turning", 16, 20, 0, 0)
	for index = 0, 6 do
		local ray = box(rays, "Ray", -5, -90, 10, 180)
		ray.BackgroundTransparency = 0.72
		ray.BackgroundColor3 = Color3.fromHex("#ffe680")
		ray.Rotation = index * 180 / 7
	end

	bands(pill, "Gloss", NumberSequence.new({
		NumberSequenceKeypoint.new(0, 1),
		NumberSequenceKeypoint.new(0.45, 1),
		NumberSequenceKeypoint.new(0.46, 0.88),
		NumberSequenceKeypoint.new(0.54, 0.88),
		NumberSequenceKeypoint.new(0.55, 1),
		NumberSequenceKeypoint.new(0.65, 1),
		NumberSequenceKeypoint.new(0.66, 0.88),
		NumberSequenceKeypoint.new(0.74, 0.88),
		NumberSequenceKeypoint.new(0.75, 1),
		NumberSequenceKeypoint.new(0.85, 1),
		NumberSequenceKeypoint.new(0.86, 0.88),
		NumberSequenceKeypoint.new(0.94, 0.88),
		NumberSequenceKeypoint.new(0.95, 1),
		NumberSequenceKeypoint.new(1, 1),
	}))
	local shine = bands(pill, "Shine", NumberSequence.new({
		NumberSequenceKeypoint.new(0, 1),
		NumberSequenceKeypoint.new(0.42, 1),
		NumberSequenceKeypoint.new(0.5, 0.4),
		NumberSequenceKeypoint.new(0.58, 1),
		NumberSequenceKeypoint.new(1, 1),
	}))

	local clover = Instance.new("ImageLabel")
	clover.Name = "Clover"
	clover.BackgroundTransparency = 1
	clover.Image = Icons.clover
	clover.ScaleType = Enum.ScaleType.Fit
	clover.AnchorPoint = Vector2.new(0.5, 0.5)
	clover.Position = UDim2.fromOffset(29, 25)
	clover.Size = UDim2.fromOffset(64, 64)
	clover.ZIndex = 3
	clover.Parent = offer

	local label = UiKit.text(offer, `x{item.multiplier} LUCK`, 23, nil, Enum.TextXAlignment.Left)
	label.Position = UDim2.fromOffset(64, 14)
	label.Size = UDim2.fromOffset(146, 28)
	label.ZIndex = 3
	if style.text then
		UiKit.gradient(label, style.text)
		label.TextColor3 = Color3.new(1, 1, 1)
		label.BackgroundTransparency = 1
	end

	local sparkles = { sparkle(offer, 176, 2, 15), sparkle(offer, 58, 40, 11), sparkle(offer, 6, 2, 12) }

	-- The price, in a dark pill; the deal also shows what it costs after, crossed out. Owned: USE and how many, green,
	-- or ON in gold once picked for this throw.
	local priceWidth = if deal then 88 else 66
	local buy = tapArea(offer, "Price", if deal then 40 else 46, 56, priceWidth, 28)
	UiKit.gradient(buy, if owned > 0 then (if picked then { "#ffe066", "#ff9a1f" } else { "#3df08a", "#0fa85a" }) else { "#3a3560", "#1f1a33" })
	UiKit.corner(buy, 14)
	UiKit.stroke(buy, 3)
	local pale = Color3.fromHex("#d6ffc4")
	local price = if owned > 0 then nil else priceOf(productId, redraw)
	if owned > 0 then
		local useLabel = UiKit.text(buy, if picked then "ON" else `USE {owned}`, 14)
		useLabel.Size = UDim2.fromScale(1, 1)
	else
		priceLabel(buy, ROBUX, 2, 26, 16, Color3.new(1, 1, 1))
	end
	if owned > 0 then
		-- No price to show.
	elseif deal then
		local regular = priceOf(item.productId, redraw)
		priceLabel(buy, if regular then tostring(regular) else "", 26, 24, 15, Color3.new(1, 1, 1))
		local slash = box(buy, "Slash", 28, 13, 20, 1.5)
		slash.BackgroundTransparency = 0
		slash.BackgroundColor3 = Color3.fromHex("#ff2d4d")
		slash.Rotation = -18
		slash.ZIndex = 2
		priceLabel(buy, if price then tostring(price) else "", 54, 28, 17, pale)
		if price and regular and regular > price then
			local burst = box(offer, "Burst", -6, 46, 40, 40)
			-- A twelve-pointed star from turned squares: dark ones for its outline, red ones on top.
			for _, layer in { { 5, 30, UiKit.INK }, { 7, 26, Color3.fromHex("#f0243f") } } do
				for _, turn in { 0, 30, 60 } do
					local point = box(burst, "Point", layer[1], layer[1], layer[2], layer[2])
					point.BackgroundTransparency = 0
					point.BackgroundColor3 = layer[3]
					point.Rotation = turn
				end
			end
			local off = UiKit.text(burst, `-{math.floor((1 - price / regular) * 100)}%`, 12)
			off.Size = UDim2.fromScale(1, 1)
			off.ZIndex = 3
		end
	else
		priceLabel(buy, if price then tostring(price) else "", 26, priceWidth - 30, 17, pale)
	end

	local details = tapArea(offer, "Details", if deal then 134 else 118, 56, if deal then 76 else 80, 28)
	UiKit.gradient(details, { "#74d3ff", "#1f7fe0" })
	UiKit.corner(details, 12)
	UiKit.stroke(details, 3)
	local detailsLabel = UiKit.text(details, "DETAILS", 13)
	detailsLabel.Size = UDim2.fromScale(1, 1)
	-- It's only 28 tall, so an unseen margin makes it easy to hit with a thumb.
	local detailsPad = tapArea(details, "BiggerTap", -4, -6, details.Size.X.Offset + 8, 42)
	detailsPad.BackgroundTransparency = 1
	detailsPad.ZIndex = 4

	local tagText = if picked then "ON THIS THROW!" elseif deal then item.dealTag else style.tag
	if tagText then
		local tag = UiKit.tag(offer, tagText, if deal then "tagGold" else { "#ff7aa8", "#e8265a" }, 12, -2)
		tag.AnchorPoint = Vector2.new(1, 0)
		tag.Position = UDim2.new(1, 6, 0, -12)
		tag.Size = UDim2.fromOffset(0, 22)
		tag.ZIndex = 6
		tag:FindFirstChildOfClass("UIStroke").Thickness = 2.5
		tag:FindFirstChildOfClass("UICorner").CornerRadius = UDim.new(0, 8)
		local tagPad = tag:FindFirstChildOfClass("UIPadding")
		tagPad.PaddingLeft = UDim.new(0, 8)
		tagPad.PaddingRight = UDim.new(0, 8)
		for _, child in tag:GetDescendants() do
			if child:IsA("GuiObject") then
				child.ZIndex = 6
			end
		end
	end

	local function press()
		if owned > 0 then
			onUse(item.multiplier)
		else
			onBuy(productId)
		end
	end
	pill.Activated:Connect(press)
	buy.Activated:Connect(press)
	details.Activated:Connect(function()
		onDetails(item)
	end)
	detailsPad.Activated:Connect(function()
		onDetails(item)
	end)

	return { halos = halos, rim = rim, rays = rays, shine = shine, clover = clover, sparkles = sparkles }
end

-- The green chip for a player who already has a lucky throw ready.
local function buildReady(parent: Instance, multiplier: number, y: number)
	local chip = box(parent, "Ready", PILL_X, y, WIDTH - PILL_X - 2, 46)
	chip.BackgroundTransparency = 0
	UiKit.gradient(chip, { "#3df08a", "#0fa85a" })
	UiKit.corner(chip, 14)
	UiKit.stroke(chip, 3)
	local clover = Instance.new("ImageLabel")
	clover.BackgroundTransparency = 1
	clover.Image = Icons.clover
	clover.ScaleType = Enum.ScaleType.Fit
	clover.Position = UDim2.fromOffset(5, 5)
	clover.Size = UDim2.fromOffset(36, 36)
	clover.Parent = chip
	local ready = UiKit.text(chip, `x{multiplier} READY!`, 16, UiKit.GOLD, Enum.TextXAlignment.Left)
	ready.Position = UDim2.fromOffset(46, 3)
	ready.Size = UDim2.fromOffset(150, 22)
	local hint = UiKit.text(chip, "on your next egg", 12, nil, Enum.TextXAlignment.Left)
	hint.Position = UDim2.fromOffset(46, 24)
	hint.Size = UDim2.fromOffset(150, 16)
end

local function percent(chance: number): string
	local value = chance * 100
	if value <= 0 then
		return "0%"
	elseif value < 0.001 then
		return "under 0.001%"
	end
	return string.format("%.3f%%", value)
end

local function readable(color: Color3): Color3
	local _, _, brightness = color:ToHSV()
	return if brightness < 0.5 then color:Lerp(Color3.new(1, 1, 1), 0.55) else color
end

local function multiplierText(value: number): string
	return string.format("%g", value)
end

-- How far this player can throw right now, a perfect throw, and where that lands (Config/DeepEnd). The Power Limit
-- stops it short, the same as on the server (Config/PowerLimit).
local function bestLanding(): (number, number)
	local full = (player:GetAttribute("ThrowPower") or 0) * Throw.meter.perfectMultiplier
	local reach = PowerLimit.apply(full, SettingsState.get("powerLimitOn"), SettingsState.get("powerLimit"))
	return math.min(reach, Throw.farthestLanding()), reach
end

-- Fills a Details list with the real chances for this player: a perfect throw with their egg and boosts right now.
local function fillChances(list: ScrollingFrame, width: number, multiplier: number, eggId: string?)
	for _, child in list:GetChildren() do
		if child:IsA("GuiObject") then
			child:Destroy()
		end
	end
	local distance, reach = bestLanding()
	local biome = Luck.biomeAt(distance)
	local pool = biome.rollFrom or biome.id
	local egg = DinoStats.findOption(Eggs, eggId) or Eggs[1]
	local luck = Luck.forRoll(distance, egg.luckBonus) * LuckBoosts.multiplier(player, workspace:GetServerTimeNow())
	local plain = CatchOdds.plain(pool, luck, Events.mutationBoosts(), DeepEnd.boostAt(reach))
	local lucky = CatchOdds.lucky(pool, luck, multiplier)
	local minOneIn = CatchOdds.hitFor(multiplier) or 0
	local order = 0

	local function paragraph(text: string, size: number, color: Color3?)
		order += 1
		local label = UiKit.text(list, text, size, color, Enum.TextXAlignment.Left)
		label.LayoutOrder = order
		label.TextWrapped = true
		label.AutomaticSize = Enum.AutomaticSize.Y
		label.Size = UDim2.fromOffset(width, 0)
		label:FindFirstChildOfClass("UIStroke").Enabled = false
	end
	local function row(name: string, nameColor: Color3?, left: string, right: string, size: number, rightColor: Color3?)
		order += 1
		local line = box(list, "Row", 0, 0, width, size + 12)
		line.LayoutOrder = order
		local title = UiKit.text(line, name, size, nameColor, Enum.TextXAlignment.Left)
		title.Size = UDim2.new(0, width - 340, 1, 0)
		title:FindFirstChildOfClass("UIStroke").Enabled = false
		local normal = UiKit.text(line, left, size, nil, Enum.TextXAlignment.Right)
		normal.Position = UDim2.fromOffset(width - 340, 0)
		normal.Size = UDim2.new(0, 170, 1, 0)
		normal:FindFirstChildOfClass("UIStroke").Enabled = false
		local boosted = UiKit.text(line, right, size, rightColor or UiKit.GOLD, Enum.TextXAlignment.Right)
		boosted.Position = UDim2.fromOffset(width - 170, 0)
		boosted.Size = UDim2.new(0, 170, 1, 0)
		boosted:FindFirstChildOfClass("UIStroke").Enabled = false
	end
	local function section(name: string)
		order += 1
		local label = UiKit.text(list, name, 36, UiKit.GOLD, Enum.TextXAlignment.Left)
		label.LayoutOrder = order
		label.Size = UDim2.fromOffset(width, 48)
		label:FindFirstChildOfClass("UIStroke").Enabled = false
	end

	paragraph(
		`One lucky throw: the egg you use it on rolls with {multiplier}x luck, and its colour and size are picked so the catch is at least 1 in {Format.commas(minOneIn)}.`,
		28
	)
	paragraph(
		`Shown for {biome.name}: a perfect throw with your egg and your boosts right now. Chances change with your map, how far the egg lands, your egg and your boosts.`,
		25,
		UiKit.MUTED
	)
	paragraph(
		"The two monsters you caught last are less likely to come, and a normal throw can also get a streak or new world bonus. This table does not count those.",
		25,
		UiKit.MUTED
	)
	row("", nil, "Normal throw", `Lucky x{multiplier}`, 24)

	-- Monsters by rarity tier, rarest last.
	section("MONSTER")
	local dinos = Dinos[pool]
	local tiers, tierOrder = {}, {}
	for rank, dino in dinos do
		local tier = UiKit.rarityOf(dino.id)
		if not tiers[tier] then
			tiers[tier] = { plain = 0, lucky = 0 }
			table.insert(tierOrder, tier)
		end
		tiers[tier].plain += plain.monsters[rank]
		tiers[tier].lucky += lucky.monsters[rank]
	end
	for _, tier in tierOrder do
		local pair = UiKit.RARITY[tier]
		local name = string.upper(string.sub(tier, 1, 1)) .. string.sub(tier, 2)
		row(name, Color3.fromHex(pair[2]):Lerp(Color3.new(1, 1, 1), 0.25), percent(tiers[tier].plain), percent(tiers[tier].lucky), 28)
	end

	section("COLOUR")
	row("No colour", nil, percent(plain.mutations.none), percent(lucky.mutations.none or 0), 28)
	for index = #Catch.mutations, 1, -1 do
		local option = Catch.mutations[index]
		row(`{option.name} (x{multiplierText(option.incomeMultiplier)} money)`, readable(option.color), percent(plain.mutations[option.id]), percent(lucky.mutations[option.id] or 0), 28)
	end

	section("SIZE")
	row("Normal size (x1)", nil, percent(plain.sizes.none), percent(lucky.sizes.none or 0), 28)
	for index = #Catch.sizes, 1, -1 do
		local option = Catch.sizes[index]
		row(`{option.name} (x{multiplierText(option.incomeMultiplier)})`, nil, percent(plain.sizes[option.id]), percent(lucky.sizes[option.id] or 0), 28)
	end
end

-- A Details panel, made the first time it's asked for.
local function buildDetails(gui: ScreenGui, item)
	local style = STYLES[item.multiplier]
	local panel = UiKit.panel(gui, {
		name = `LuckDetails{item.multiplier}`,
		width = 880,
		height = 660,
		header = style.header,
		title = `Lucky Throw x{item.multiplier}`,
		icon = "🍀",
		iconKey = "clover",
	})
	panel.frame.Position = UDim2.fromScale(0.62, 0.5)
	local list = UiKit.scrollList(panel.body, UDim2.fromOffset(28, 8), UDim2.fromOffset(832, 452), 6)
	list.Name = "Chances"
	local note = UiKit.text(panel.body, "Chances are rounded, so they may not add up to exactly 100%.", 22, UiKit.MUTED)
	note.Position = UDim2.fromOffset(20, 464)
	note.Size = UDim2.fromOffset(840, 28)
	note:FindFirstChildOfClass("UIStroke").Enabled = false
	local gotIt = UiKit.button(panel.body, "GOT IT!", "green", 220, 64, 30)
	gotIt.AnchorPoint = Vector2.new(0.5, 0)
	gotIt.Position = UDim2.new(0.5, 0, 0, 496)
	gotIt.Activated:Connect(function()
		UiKit.closePanel(panel)
	end)
	return { panel = panel, list = list }
end

local gui: ScreenGui
local root: Frame
local details = {}
local parts = {}
local effects: RBXScriptConnection? = nil
local shown = false
local eggId: string? = nil
local chosen: number? = nil -- the owned lucky throw picked with USE for this throw

-- Empties the corner, keeping its UIScale.
local function clearOffers()
	for _, child in root:GetChildren() do
		if child:IsA("GuiObject") then
			child:Destroy()
		end
	end
	table.clear(parts)
end

local function closeDetails()
	for _, entry in details do
		UiKit.closePanel(entry.panel)
	end
end

local function openDetails(item)
	local entry = details[item.multiplier]
	if not entry then
		entry = buildDetails(gui, item)
		details[item.multiplier] = entry
	end
	closeDetails()
	fillChances(entry.list, 800, item.multiplier, eggId)
	entry.list.CanvasPosition = Vector2.zero
	UiKit.openPanel(entry.panel)
end

local function buy(productId: number)
	if productId ~= 0 then
		-- Paid random item: the server checks the policy, then prompts.
		ReplicatedStorage:WaitForChild("ShopRemotes").BuyRandom:FireServer(productId)
	end
end

local redraw: () -> ()

-- Picks this owned lucky throw for the throw being aimed, or un-picks it.
local function use(multiplier: number)
	chosen = if chosen == multiplier then nil else multiplier
	redraw()
end

function redraw()
	if not shown then
		return
	end
	clearOffers()
	if chosen and LuckyThrows.count(player, chosen) == 0 then
		chosen = nil
	end
	for index, item in Shop.luckyThrows do
		table.insert(parts, buildOffer(root, item, (index - 1) * (OFFER_HEIGHT + OFFER_GAP), buy, openDetails, redraw, use, chosen == item.multiplier))
	end
	-- A lucky throw that goes by itself (the daily x50), unless one is picked: only one per throw.
	local auto = LuckyThrows.nextOf(player)
	if auto and not chosen then
		buildReady(root, auto, #Shop.luckyThrows * (OFFER_HEIGHT + OFFER_GAP))
	end
end

local function animate()
	local t = os.clock()
	for index, offer in parts do
		local phase = t + index * 0.7
		offer.rim.Rotation = (t * RIM_TURN + index * 90) % 360
		offer.rays.Rotation = t * 14
		offer.clover.Rotation = math.sin(phase * 2) * 6
		offer.clover.Position = UDim2.fromOffset(29, 25 + math.sin(phase * 2.6) * 1.5)
		for ring, halo in offer.halos do
			halo.BackgroundTransparency = 0.72 + ring * 0.04 + 0.12 * math.sin(phase * 3)
		end
		local sweep = (phase % SHINE_EVERY) / 0.8 -- the shine crosses in 0.8 s, then waits
		offer.shine.Offset = Vector2.new(if sweep < 1 then sweep * 2 - 1 else 2, 0)
		for star, label in offer.sparkles do
			local twinkle = math.sin(phase * 2.2 + star * 2.1)
			label.TextTransparency = if twinkle > 0 then 1 - twinkle else 1
			label.Rotation = t * 60
		end
	end
end

-- While aiming. eggInHand is the id of the egg about to be thrown.
function LuckOfferController.show(eggInHand: string?)
	-- The policy doesn't allow paid random items here (ShopService): no offer to show.
	if shown or player:GetAttribute("PaidRandomBlocked") then
		return
	end
	shown = true
	chosen = nil -- every throw starts with none picked
	eggId = eggInHand
	gui.Enabled = true
	redraw()
	local size = root:FindFirstChildOfClass("UIScale").Scale
	local top = TOP_MARGIN * size
	root.Position = UDim2.fromOffset(-WIDTH * size - 20, top)
	TweenService:Create(root, TweenInfo.new(0.3, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Position = UDim2.fromOffset(10 * size, top) }):Play()
	effects = RunService.Heartbeat:Connect(animate)
end

-- The moment the egg is thrown, or the throw is called off.
function LuckOfferController.hide()
	if not shown then
		return
	end
	shown = false
	closeDetails()
	gui.Enabled = false
	if effects then
		effects:Disconnect()
		effects = nil
	end
	clearOffers()
end

-- The lucky throw picked for this throw, if the player still owns it. ThrowController sends it with the tap.
function LuckOfferController.chosen(): number?
	if chosen and LuckyThrows.count(player, chosen) > 0 then
		return chosen
	end
	return nil
end

-- No throw goes while the player is reading the chances.
function LuckOfferController.blocksThrow(): boolean
	for _, entry in details do
		if entry.panel.frame.Visible then
			return true
		end
	end
	return false
end

function LuckOfferController.start()
	gui = Instance.new("ScreenGui")
	gui.Name = "LuckOffer"
	gui.ResetOnSpawn = false
	gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	gui.DisplayOrder = 2
	gui.Enabled = false
	gui.Parent = player:WaitForChild("PlayerGui")

	root = Instance.new("Frame")
	root.Name = "Offers"
	root.BackgroundTransparency = 1
	root.Size = UDim2.fromOffset(WIDTH, OFFER_HEIGHT * 2 + OFFER_GAP)
	root.Parent = gui
	local scale = Instance.new("UIScale")
	scale.Scale = math.min(SCREEN_WIDTH * HudStyle.scale(), MOST_WIDTH) / WIDTH
	scale.Parent = root

	player:GetAttributeChangedSignal("LuckDealBought"):Connect(redraw)
	for _, multiplier in LuckyThrows.tiers do
		player:GetAttributeChangedSignal(LuckyThrows.attribute(multiplier)):Connect(redraw)
	end
end

return LuckOfferController
