-- The Sell Stand panel (Figma "Throw Eggs - Index & Inventory"): the SELL stall's pad opens it. The backpack as a
-- grid of tiles, cheapest first; tap a rarity button or single monsters to pick them, then SELL and a second tap
-- to confirm. Nothing is picked when it opens, the carried monster can't be picked, and monsters on the base aren't
-- shown. Display only: the server checks every monster and works out the money (PlotService "sellMany").
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Catch = require(ReplicatedStorage.Shared.Config.Catch)
local DinoStats = require(ReplicatedStorage.Shared.DinoStats)
local Format = require(ReplicatedStorage.Shared.Format)
local UiKit = require(ReplicatedStorage.Shared.UiKit)

local player = Players.LocalPlayer

local SellPanel = {}

local PANEL_SIZE = Vector2.new(800, 618)
local TILE_SIZE = Vector2.new(140, 166)
local CHIP_SIZE = Vector2.new(80, 44) -- nine across the panel: ALL and the eight rarities
local CHIP_STEP = 85
local FOOTER_HEIGHT = 100
local CONFIRM_TIME = 3 -- seconds the SURE? button waits for a second tap
local HELD_FADE = 0.55 -- how see-through the carried monster's picture is
local WHITE = Color3.new(1, 1, 1)

local function rarityRank(dinoId: string): number
	return table.find(UiKit.RARITY_ORDER, UiKit.rarityOf(dinoId)) or 1
end

local function borderOf(object: GuiObject): UIStroke?
	for _, child in object:GetChildren() do
		if child:IsA("UIStroke") and child.ApplyStrokeMode == Enum.ApplyStrokeMode.Border then
			return child
		end
	end
	return nil
end

local function makeChip(parent: Instance, text: string, width: number, style: string): Frame
	local chip = Instance.new("Frame")
	chip.AutomaticSize = Enum.AutomaticSize.X
	chip.Size = UDim2.fromOffset(width, 22)
	chip.ZIndex = 3
	chip.Parent = parent
	UiKit.gradient(chip, style)
	UiKit.corner(chip, 8)
	UiKit.stroke(chip, 3)
	local pad = Instance.new("UIPadding")
	pad.PaddingLeft = UDim.new(0, 7)
	pad.PaddingRight = UDim.new(0, 7)
	pad.Parent = chip
	local label = UiKit.text(chip, text, 13)
	label.AutomaticSize = Enum.AutomaticSize.X
	label.Size = UDim2.fromScale(0, 1)
	label.ZIndex = 3
	return chip
end

-- The green tick on a picked tile's corner, drawn from two bars so it needs no image.
local function makeTick(parent: Instance): Frame
	local disc = Instance.new("Frame")
	disc.Name = "Tick"
	disc.Position = UDim2.fromOffset(TILE_SIZE.X - 34, -8)
	disc.Size = UDim2.fromOffset(38, 38)
	disc.ZIndex = 4
	disc.Parent = parent
	UiKit.gradient(disc, "green")
	UiKit.corner(disc, 19)
	UiKit.stroke(disc, 4)
	for _, bar in { { 14, 21, 14, 45 }, { 22, 18, 24, -52 } } do
		local line = Instance.new("Frame")
		line.AnchorPoint = Vector2.new(0.5, 0.5)
		line.BackgroundColor3 = WHITE
		line.BorderSizePixel = 0
		line.Position = UDim2.fromOffset(bar[1], bar[2])
		line.Size = UDim2.fromOffset(bar[3], 5)
		line.Rotation = bar[4]
		line.ZIndex = 5
		line.Parent = disc
		UiKit.corner(line, 2)
	end
	return disc
end

-- send(keys) asks the server to sell those monsters. feeding: the same panel to pick monsters to feed instead, with
-- { accepts(dino), tileText(dino), summary(picked) -> (count line, total line) } (PlotController).
function SellPanel.new(gui: ScreenGui, send: ({ number }) -> (), feeding)
	local verb = if feeding then "FEED" else "SELL"
	local panel = UiKit.panel(gui, {
		name = if feeding then "FeedPanel" else "SellPanel",
		width = PANEL_SIZE.X,
		height = PANEL_SIZE.Y,
		header = if feeding then "purple" else "red",
		title = if feeding then "Feed" else "Sell Stand",
		icon = if feeding then "🍖" else "💵",
		iconKey = if feeding then nil else "cash",
	})
	local body = panel.body

	local grid = Instance.new("ScrollingFrame")
	grid.Name = "Grid"
	grid.BackgroundTransparency = 1
	grid.BorderSizePixel = 0
	grid.Position = UDim2.fromOffset(8, 58)
	grid.Size = UDim2.new(1, -16, 1, -58 - FOOTER_HEIGHT)
	grid.AutomaticCanvasSize = Enum.AutomaticSize.Y
	grid.CanvasSize = UDim2.new()
	grid.ScrollBarThickness = 10
	grid.ScrollBarImageColor3 = Color3.fromRGB(91, 74, 140)
	grid.ScrollingDirection = Enum.ScrollingDirection.Y
	grid.Parent = body
	local layout = Instance.new("UIGridLayout")
	layout.CellSize = UDim2.fromOffset(TILE_SIZE.X, TILE_SIZE.Y)
	layout.CellPadding = UDim2.fromOffset(12, 14)
	layout.HorizontalAlignment = Enum.HorizontalAlignment.Center
	layout.SortOrder = Enum.SortOrder.LayoutOrder
	layout.Parent = grid
	local gridPad = Instance.new("UIPadding")
	gridPad.PaddingTop = UDim.new(0, 12)
	gridPad.PaddingBottom = UDim.new(0, 12)
	gridPad.Parent = grid

	-- The footer sits inside the panel's edge, its bottom corners following the panel's.
	local footer = Instance.new("Frame")
	footer.Name = "Footer"
	footer.AnchorPoint = Vector2.new(0, 1)
	footer.BackgroundColor3 = UiKit.DEEP
	footer.Position = UDim2.new(0, 3, 1, -3)
	footer.Size = UDim2.new(1, -6, 0, FOOTER_HEIGHT - 3)
	footer.Parent = body
	UiKit.corner(footer, 27)
	local squared = Instance.new("Frame")
	squared.BackgroundColor3 = UiKit.DEEP
	squared.BorderSizePixel = 0
	squared.Size = UDim2.new(1, 0, 0, 30)
	squared.Parent = footer
	local count = UiKit.text(footer, "", 22, UiKit.MUTED, Enum.TextXAlignment.Left)
	count.Name = "Count"
	count.Position = UDim2.fromOffset(24, 12)
	count.Size = UDim2.fromOffset(320, 28)
	local total = UiKit.text(footer, "", 38, UiKit.CASH, Enum.TextXAlignment.Left)
	total.Name = "Total"
	total.Position = UDim2.fromOffset(24, 42)
	total.Size = UDim2.fromOffset(320, 46)
	local sell = UiKit.button(footer, verb, "grey", 420, 72, 32)
	sell.Name = "SellButton"
	sell.AnchorPoint = Vector2.new(1, 0.5)
	sell.Position = UDim2.new(1, -22, 0.5, 0)

	local emptyTitle = UiKit.text(body, "Your backpack is empty.", 34)
	emptyTitle.Name = "Empty"
	emptyTitle.Position = UDim2.fromOffset(0, 190)
	local emptyHint = UiKit.muted(body, `Throw more eggs, then come back to {string.lower(verb)}.`, 22)
	emptyHint.Name = "EmptyHint"
	emptyHint.Position = UDim2.fromOffset(0, 244)

	local list = {} -- backpack monsters, cheapest rarity first
	local tiles = {} -- key -> the tile's parts
	local picked = {} -- key -> true
	local chips = {} -- rarity name or "all" -> button
	local confirming = false
	local confirmRound = 0

	local function heldKey()
		return player:GetAttribute("HeldDino")
	end

	-- Monsters a rarity button works on: everything of that rarity (or everything), but never the carried one.
	local function matching(rarity: string)
		local found = {}
		for _, dino in list do
			if dino.key ~= heldKey() and (rarity == "all" or UiKit.rarityOf(dino.id) == rarity) then
				table.insert(found, dino)
			end
		end
		return found
	end

	local function allPicked(dinos): boolean
		for _, dino in dinos do
			if not picked[dino.key] then
				return false
			end
		end
		return #dinos > 0
	end

	local function render()
		local held = heldKey()
		local amount, cash = 0, 0
		local chosen = {}
		for _, dino in list do
			if dino.key == held then
				picked[dino.key] = nil
			end
			if picked[dino.key] then
				table.insert(chosen, dino)
			end
			local tile = tiles[dino.key]
			local isPicked = picked[dino.key] == true
			if isPicked then
				amount += 1
				cash += dino.sellPrice
			end
			tile.border.Color = if isPicked then WHITE else UiKit.INK
			tile.border.Thickness = if isPicked then 5 else 4
			tile.tick.Visible = isPicked
			tile.holding.Visible = dino.key == held
			tile.price.Visible = dino.key ~= held
			if feeding then
				tile.price.Text = feeding.tileText(dino)
			end
			tile.fade = if dino.key == held then HELD_FADE else 0
			local view = tile.art:FindFirstChildOfClass("ViewportFrame")
			if view then
				view.ImageTransparency = tile.fade
			end
		end
		for rarity, chip in chips do
			local on = allPicked(matching(rarity))
			local border = borderOf(chip)
			if border then
				border.Color = if on then WHITE else UiKit.INK
			end
		end
		if amount == 0 then
			confirming = false
		end
		count.Text = if amount == 0 then `TAP MONSTERS TO {verb}` elseif amount == 1 then "1 MONSTER" else `{amount} MONSTERS`
		total.Text = if amount == 0 then "" else `+{Format.cash(cash)}`
		if feeding then
			count.Text, total.Text = feeding.summary(chosen)
		end
		UiKit.restyle(sell, if confirming then "SURE? TAP AGAIN" elseif amount == 0 then verb else `{verb} {amount}`, if confirming then "yellow" elseif amount == 0 then "grey" elseif feeding then "purple" else "red")

		local empty = #list == 0
		emptyTitle.Visible = empty
		emptyHint.Visible = empty
		grid.Visible = not empty
		footer.Visible = not empty
		for _, chip in chips do
			chip.Visible = not empty
		end
	end

	-- Changing what's picked always takes back a waiting SURE?, so the second tap sells what was shown.
	local function changePicks(change: () -> ())
		change()
		confirming = false
		render()
	end

	-- Tiles build their 3D model only once scrolled into view, since a backpack can hold a lot.
	local function showVisibleTiles()
		if not panel.frame.Visible then
			return
		end
		local top = grid.AbsolutePosition.Y
		local bottom = top + grid.AbsoluteWindowSize.Y
		local height = TILE_SIZE.Y * panel.scale.Scale
		for _, dino in list do
			local tile = tiles[dino.key]
			local y = tile.button.AbsolutePosition.Y
			if not tile.art:FindFirstChildOfClass("ViewportFrame") and y < bottom + height and y + height > top - height then
				local view = UiKit.monster(tile.art, dino.id, { mutation = dino.mutation, aspect = 116 / 94, position = UDim2.fromOffset(4, 4), size = UDim2.new(1, -8, 1, -8) })
				view.ImageTransparency = tile.fade
			end
		end
	end

	local function makeTile(dino)
		local button = Instance.new("TextButton")
		button.Name = "Tile"
		button.AutoButtonColor = false
		button.BackgroundColor3 = UiKit.ROW
		button.Text = ""
		button.Parent = grid
		UiKit.corner(button, 20)
		local border = UiKit.stroke(button, 4)

		local art = Instance.new("Frame")
		art.Name = "Art"
		art.Position = UDim2.fromOffset(8, 8)
		art.Size = UDim2.fromOffset(124, 102)
		art.Parent = button
		UiKit.gradient(art, UiKit.rarityOf(dino.id))
		UiKit.corner(art, 14)
		UiKit.stroke(art, 3)

		local mutation = DinoStats.findOption(Catch.mutations, dino.mutation)
		if mutation then
			local chip = makeChip(button, mutation.name, 0, "tagGold")
			chip.Name = "Mutation"
			chip.Position = UDim2.fromOffset(12, 90)
			chip:FindFirstChildOfClass("UIGradient"):Destroy()
			chip.BackgroundColor3 = mutation.color
		end

		local name = UiKit.text(button, dino.name, 16)
		name.Name = "DinoName"
		name.Position = UDim2.fromOffset(6, 113)
		name.Size = UDim2.fromOffset(128, 22)
		name.TextScaled = true
		local limit = Instance.new("UITextSizeConstraint")
		limit.MaxTextSize = 16
		limit.Parent = name
		local price = UiKit.text(button, Format.cash(dino.sellPrice), 18, UiKit.CASH)
		price.Name = "Price"
		price.Position = UDim2.fromOffset(6, 136)
		price.Size = UDim2.fromOffset(128, 24)
		local holding = makeChip(button, "HOLDING", 0, "green")
		holding.Name = "Holding"
		holding.AnchorPoint = Vector2.new(0.5, 0)
		holding.Position = UDim2.fromOffset(TILE_SIZE.X / 2, 137)

		local key = dino.key
		button.Activated:Connect(function()
			if key ~= heldKey() then
				changePicks(function()
					picked[key] = if picked[key] then nil else true
				end)
			end
		end)
		return { button = button, art = art, border = border, tick = makeTick(button), holding = holding, price = price, fade = 0 }
	end

	for index, name in { "all", table.unpack(UiKit.RARITY_ORDER) } do
		local chip = UiKit.button(body, string.upper(name), if name == "all" then "dark" else name, CHIP_SIZE.X, CHIP_SIZE.Y, 13)
		chip.Name = `Chip_{name}`
		if name == "secret" then
			-- A button's gradient tints its text too, and this one is so dark the word vanished: one flat colour instead.
			chip:FindFirstChildOfClass("UIGradient"):Destroy()
			chip.BackgroundColor3 = Color3.fromHex(UiKit.RARITY.secret[1])
		end
		chip.Position = UDim2.fromOffset(18 + (index - 1) * CHIP_STEP, 8)
		chips[name] = chip
		chip.Activated:Connect(function()
			changePicks(function()
				local dinos = matching(name)
				local choose = if allPicked(dinos) then nil else true
				for _, dino in dinos do
					picked[dino.key] = choose
				end
			end)
		end)
	end

	sell.Activated:Connect(function()
		local keys = {}
		for key in picked do
			table.insert(keys, key)
		end
		if #keys == 0 then
			return
		end
		if confirming then
			confirming = false
			table.clear(picked)
			send(keys)
			render()
		else
			confirming = true
			confirmRound += 1
			local round = confirmRound
			render()
			task.delay(CONFIRM_TIME, function()
				if confirming and round == confirmRound then
					confirming = false
					render()
				end
			end)
		end
	end)

	grid:GetPropertyChangedSignal("CanvasPosition"):Connect(showVisibleTiles)
	player:GetAttributeChangedSignal("HeldDino"):Connect(render)

	local sellPanel = { panel = panel }

	-- Takes the whole list of monsters, as the server sends it to My Dinos.
	function sellPanel.setDinos(dinos)
		table.clear(list)
		local present = {}
		for _, dino in dinos do
			if not dino.onPlot and DinoStats.sellable(dino.id) and (not feeding or feeding.accepts(dino)) then
				table.insert(list, dino)
				present[dino.key] = true
			end
		end
		table.sort(list, function(a, b)
			local rankA, rankB = rarityRank(a.id), rarityRank(b.id)
			if rankA ~= rankB then
				return rankA < rankB
			end
			if a.sellPrice ~= b.sellPrice then
				return a.sellPrice < b.sellPrice
			end
			return a.key < b.key
		end)
		for key, tile in tiles do
			if not present[key] then
				tile.button:Destroy()
				tiles[key] = nil
				picked[key] = nil
			end
		end
		for index, dino in list do
			tiles[dino.key] = tiles[dino.key] or makeTile(dino)
			tiles[dino.key].button.LayoutOrder = index
		end
		render()
		task.defer(showVisibleTiles)
	end

	function sellPanel.open()
		table.clear(picked)
		confirming = false
		grid.CanvasPosition = Vector2.zero
		render()
		UiKit.openPanel(panel)
		task.defer(showVisibleTiles)
	end

	-- The header's words, for the monster being fed.
	function sellPanel.setTitle(text: string)
		for _, child in panel.header:GetChildren() do
			if child:IsA("TextLabel") then
				child.Text = text
			end
		end
	end

	function sellPanel.close()
		UiKit.closePanel(panel)
	end

	render()
	return sellPanel
end

return SellPanel
