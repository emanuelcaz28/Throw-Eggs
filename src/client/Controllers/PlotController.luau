-- The cash display, the My Dinos panel, the hotbar of backpack dinos and placing an equipped
-- dino on the plot. Display and requests only: the server decides what actually happens to a
-- dino, checks every spot and works out what it's worth. The panel and hotbar follow Figma
-- "Throw Eggs - Index & Inventory" and show each monster's real model, in its mutation's colours.
local GuiService = game:GetService("GuiService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local StarterGui = game:GetService("StarterGui")
local UserInputService = game:GetService("UserInputService")

local Catch = require(ReplicatedStorage.Shared.Config.Catch)
local Chonk = require(ReplicatedStorage.Shared.Config.Chonk)
local DinoModel = require(ReplicatedStorage.Shared.DinoModel)
local DinoStats = require(ReplicatedStorage.Shared.DinoStats)
local Format = require(ReplicatedStorage.Shared.Format)
local HudStyle = require(ReplicatedStorage.Shared.HudStyle)
local Hub = require(ReplicatedStorage.Shared.Config.Hub)
local Plot = require(ReplicatedStorage.Shared.Config.Plot)
local Pop = require(ReplicatedStorage.Shared.Config.Pop)
local PopText = require(ReplicatedStorage.Shared.PopText)
local SellPanel = require(script.Parent.SellPanel)
local RarityLabel = require(script.Parent.RarityLabel)
local UiKit = require(ReplicatedStorage.Shared.UiKit)

local player = Players.LocalPlayer

local PlotController = {}

local TEXT = Color3.new(1, 1, 1)
local CASH = Color3.fromRGB(120, 235, 120)
local PANEL_SIZE = Vector2.new(470, 692)
local ROW_WIDTH, ROW_HEIGHT = 428, 100
local SLOT_SIZE = Vector2.new(72, 72)
local SLOT_GAP = 8
local HELD_RAISE = 1.14 -- the carried monster's hotbar slot stands this much bigger
local SIZE_WORD = Color3.fromRGB(217, 222, 232) -- size mutations are silver
local CASH_HEIGHT = 56 -- height of the cash number, before scaling for small screens
local POWER_HEIGHT = 52 -- Throw Power's, just above it (TrainingController)
local INCOME_HEIGHT = 22
local SELL_CONFIRM_TIME = 3 -- seconds the "SURE?" button waits for a second tap
local GOOD_SPOT = Color3.fromRGB(90, 220, 110)
local BAD_SPOT = Color3.fromRGB(230, 70, 60)
local GHOST_TRANSPARENCY = 0.45
local HOTBAR_KEYS = {
	Enum.KeyCode.One,
	Enum.KeyCode.Two,
	Enum.KeyCode.Three,
	Enum.KeyCode.Four,
	Enum.KeyCode.Five,
	Enum.KeyCode.Six,
	Enum.KeyCode.Seven,
	Enum.KeyCode.Eight,
	Enum.KeyCode.Nine,
	Enum.KeyCode.Zero,
}

local function makeLabel(parent: Instance, font: Enum.Font, color: Color3, position: UDim2, size: UDim2): TextLabel
	local label = Instance.new("TextLabel")
	label.BackgroundTransparency = 1
	label.Font = font
	label.Position = position
	label.Size = size
	label.Text = ""
	label.TextColor3 = color
	label.TextScaled = true
	label.TextXAlignment = Enum.TextXAlignment.Left
	label.Parent = parent
	return label
end

local function buildGui()
	local gui = Instance.new("ScreenGui")
	gui.Name = "PlotHud"
	gui.ResetOnSpawn = false
	gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	gui.DisplayOrder = 1 -- so the open panel covers the training display
	gui.Parent = player:WaitForChild("PlayerGui")

	-- Bottom left, under Throw Power: big outlined cash with the $/s small beneath it.
	local scale = HudStyle.scale()
	local cashStat, cash = HudStyle.stat(gui, "💵", CASH, CASH_HEIGHT, "cash")
	cashStat.Name = "CashStat"
	cashStat.AnchorPoint = Vector2.new(0, 1)
	cashStat.Position = UDim2.new(0, 16, 1, -INCOME_HEIGHT * scale - 12)
	local income = makeLabel(gui, HudStyle.FONT, TEXT, UDim2.new(0, 16 + CASH_HEIGHT * scale * 1.1, 1, -8), UDim2.fromOffset(200 * scale, INCOME_HEIGHT * scale))
	income.Name = "Income"
	income.AnchorPoint = Vector2.new(0, 1)
	HudStyle.outline(income, 2 * scale)

	local open = HudStyle.iconButton(gui, "🐾", "Monsters", "paw")
	open.Name = "OpenDinos"
	open.AnchorPoint = Vector2.new(1, 0.5)
	open.Position = UDim2.new(1, -16, HudStyle.COLUMN_CENTER, 0)

	-- My Monsters docks on the right, like a side drawer.
	local panel = UiKit.panel(gui, {
		name = "DinoPanel",
		width = PANEL_SIZE.X,
		height = PANEL_SIZE.Y,
		header = "jungle",
		title = "My Monsters",
		titleSize = 44,
		icon = "🐾",
		iconKey = "paw",
		anchor = Vector2.new(1, 0.5),
		position = UDim2.new(1, -16, 0.5, 0),
	})
	local tabs = {}
	for index, name in { "plot", "backpack" } do
		local tab = UiKit.button(panel.body, "", "green", (PANEL_SIZE.X - 42) / 2, 46, 23)
		tab.Name = `Tab_{name}`
		tab.Position = UDim2.fromOffset(16 + (index - 1) * ((PANEL_SIZE.X - 42) / 2 + 10), 6)
		tabs[name] = tab
	end
	local list = UiKit.scrollList(panel.body, UDim2.fromOffset(12, 62), UDim2.new(1, -20, 1, -150), 8)
	list.Name = "List"
	local empty = UiKit.muted(panel.body, "", 20)
	empty.Name = "Empty"
	empty.Position = UDim2.fromOffset(20, 90)
	empty.Size = UDim2.new(1, -40, 0, 60)
	-- EQUIP BEST and UNEQUIP ALL side by side along the bottom.
	local bottomWidth = (PANEL_SIZE.X - 42) / 2
	local equip = UiKit.button(panel.body, "EQUIP BEST", "yellow", bottomWidth, 66, 28)
	equip.Name = "EquipBest"
	equip.AnchorPoint = Vector2.new(0, 1)
	equip.Position = UDim2.new(0, 16, 1, -16)
	local unequipAll = UiKit.button(panel.body, "UNEQUIP ALL", "red", bottomWidth, 66, 28)
	unequipAll.Name = "UnequipAll"
	unequipAll.AnchorPoint = Vector2.new(0, 1)
	unequipAll.Position = UDim2.new(0, 26 + bottomWidth, 1, -16)

	-- Backpack dinos, best first, on keys 1-0. Along the bottom edge; training hides it, so the
	-- training bar can have that spot.
	local hotbar = Instance.new("Frame")
	hotbar.Name = "Hotbar"
	hotbar.AnchorPoint = Vector2.new(0.5, 1)
	hotbar.Position = UDim2.new(0.5, 0, 1, -10)
	hotbar.Size = UDim2.fromOffset(#HOTBAR_KEYS * (SLOT_SIZE.X + SLOT_GAP), SLOT_SIZE.Y * HELD_RAISE + 24)
	hotbar.BackgroundTransparency = 1
	hotbar.Parent = gui
	-- On narrow screens (phones) it shrinks to fit between the cash and power at the bottom left and the same
	-- margin on the right, rather than running under them.
	local statsWidth = 16 + math.max(CASH_HEIGHT, POWER_HEIGHT) * 5 * scale + 12
	local roomForHotbar = UiKit.screenSize().X - 2 * statsWidth
	local hotbarScale = Instance.new("UIScale")
	hotbarScale.Scale = math.clamp(roomForHotbar / hotbar.Size.X.Offset, 0.3, scale)
	hotbarScale.Parent = hotbar
	local hotbarLayout = Instance.new("UIListLayout")
	hotbarLayout.FillDirection = Enum.FillDirection.Horizontal
	hotbarLayout.HorizontalAlignment = Enum.HorizontalAlignment.Center
	hotbarLayout.VerticalAlignment = Enum.VerticalAlignment.Bottom
	hotbarLayout.SortOrder = Enum.SortOrder.LayoutOrder
	hotbarLayout.Padding = UDim.new(0, SLOT_GAP)
	hotbarLayout.Parent = hotbar

	local slots = {}
	for index = 1, #HOTBAR_KEYS do
		local slot = Instance.new("TextButton")
		slot.Name = `Slot{index}`
		slot.LayoutOrder = index
		slot.Size = UDim2.fromOffset(SLOT_SIZE.X, SLOT_SIZE.Y)
		slot.AutoButtonColor = false
		slot.Text = ""
		slot.Parent = hotbar
		local gradient = UiKit.gradient(slot, "common")
		UiKit.corner(slot, 16)
		local edge = UiKit.stroke(slot, 4)
		local raise = Instance.new("UIScale")
		raise.Parent = slot
		-- Larger when the hotbar is shrunk for a phone, so the $/s stays readable (14 at full size).
		local income = UiKit.text(slot, "", math.floor(14 / math.max(hotbarScale.Scale, 0.75)), UiKit.CASH)
		income.Position = UDim2.fromOffset(-12, -20)
		income.Size = UDim2.new(1, 24, 0, 18)
		income.ZIndex = 3
		-- The key that equips it, in a dark disc on its bottom-left corner.
		local key = Instance.new("Frame")
		key.Name = "Key"
		key.Position = UDim2.fromOffset(-4, SLOT_SIZE.Y - 18)
		key.Size = UDim2.fromOffset(22, 22)
		key.BackgroundColor3 = UiKit.INK
		key.BackgroundTransparency = 0.2
		key.ZIndex = 3
		key.Parent = slot
		UiKit.corner(key, 11)
		local number = UiKit.text(key, tostring(index % 10), 13)
		number.Size = UDim2.fromScale(1, 1)
		number.ZIndex = 3
		slots[index] = { button = slot, gradient = gradient, edge = edge, raise = raise, income = income, key = nil, view = nil }
	end

	local hint = UiKit.text(gui, "", 26)
	hint.Name = "PlaceHint"
	hint.AnchorPoint = Vector2.new(0.5, 1)
	hint.Position = UDim2.new(0.5, 0, 1, -110 * HudStyle.scale())
	hint.Size = UDim2.new(0.8, 0, 0, 34)
	hint.Visible = false

	return {
		gui = gui,
		hotbar = hotbar,
		slots = slots,
		hint = hint,
		cash = cash,
		income = income,
		open = open,
		panel = panel,
		tabs = tabs,
		equip = equip,
		unequipAll = unequipAll,
		list = list,
		empty = empty,
	}
end

function PlotController.start()
	local remotes = ReplicatedStorage:WaitForChild("PlotRemotes")
	local hud = buildGui()
	local confirmKey = nil -- the dino whose SELL button is showing "SURE?"
	local tab = "plot" -- which list the panel shows: "plot" or "backpack"
	local dinos = {}
	local slots = 0
	local renderList

	local function send(action: string, key: (number | { number })?, x: (number | string)?, z: number?)
		remotes.DinoAction:FireServer(action, key, x, z)
	end
	local sellPanel = SellPanel.new(hud.gui, function(keys)
		send("sellMany", keys)
	end)

	-- The Feed panel: the Sell Stand's grid, picking food for one monster on the base (Config/Chonk). The server checks it all.
	local feedKey: number? = nil
	local function feedTarget()
		for _, dino in dinos do
			if dino.key == feedKey then
				return dino
			end
		end
		return nil
	end
	local feedPanel = SellPanel.new(hud.gui, function(keys)
		send("feed", feedKey, keys)
	end, {
		accepts = function(dino)
			return dino.chonk == 0
		end,
		tileText = function(dino)
			local target = feedTarget()
			return `+{if target then Chonk.foodOf(target.id, dino.id) else Chonk.food} food`
		end,
		summary = function(picked)
			local target = feedTarget()
			if not target then
				return "", ""
			end
			if #picked == 0 then
				local nextSize, nextLevel = Chonk.nextSize(target.chonk)
				local toward = if nextSize then ` ({DinoStats.findOption(Catch.sizes, nextSize).name} at {nextLevel})` else ""
				return `CHONK {target.chonk}: {target.food} / {Chonk.foodFor(target.chonk)} FOOD{toward}`, ""
			end
			local level, food = target.chonk, target.food
			local used = 0
			for _, dino in picked do
				if level < Chonk.maxLevel then
					level, food = Chonk.grow(level, food, Chonk.foodOf(target.id, dino.id))
					used += 1
				end
			end
			-- The tutorial's feeding step is free, once (TutorialService).
			local free = player:GetAttribute("TutorialFreeFeed") == target.key
			-- Feeding only changes the size (Config/Chonk): say which size this reaches, or how far the next one is.
			local reached = Chonk.sizeAt(level)
			local before = Chonk.sizeAt(target.chonk)
			local nextSize, nextLevel = Chonk.nextSize(level)
			local growth = if reached and reached ~= before
				then ` = {DinoStats.findOption(Catch.sizes, reached).name}!`
				elseif nextSize then `, {DinoStats.findOption(Catch.sizes, nextSize).name} at {nextLevel}`
				else ""
			return `CHONK {target.chonk} TO {level}{growth}`, if free then "FREE" else `-{Format.cash(Chonk.priceOf(target.income) * used)}`
		end,
	})
	local function openFeed(dino)
		feedKey = dino.key
		feedPanel.setTitle(`Feed {dino.name}`)
		UiKit.closePanel(hud.panel)
		feedPanel.open()
	end

	-- The Resize panel: a special (bought with Robux) can't be sold, so its row has RESIZE instead [Owner, 2026-11-08].
	-- It steps through DinoStats.resizes, from its normal size to the biggest size mutation's. Looks only: its income
	-- stays the same. The server checks it all.
	local resizeKey: number? = nil
	local resizePanel = UiKit.panel(hud.gui, { name = "ResizePanel", title = "Resize", header = "purple", width = 500, height = 360 })
	local resizeName = UiKit.text(resizePanel.body, "", 40)
	resizeName.Position = UDim2.fromOffset(0, 18)
	local resizeTimes = UiKit.text(resizePanel.body, "", 24, SIZE_WORD)
	resizeTimes.Position = UDim2.fromOffset(0, 70)
	local pips = Instance.new("Frame")
	pips.BackgroundTransparency = 1
	pips.AnchorPoint = Vector2.new(0.5, 0)
	pips.Position = UDim2.new(0.5, 0, 0, 112)
	pips.Size = UDim2.fromOffset(#DinoStats.resizes * 52, 22)
	pips.Parent = resizePanel.body
	local pipsLayout = Instance.new("UIListLayout")
	pipsLayout.FillDirection = Enum.FillDirection.Horizontal
	pipsLayout.HorizontalAlignment = Enum.HorizontalAlignment.Center
	pipsLayout.Padding = UDim.new(0, 8)
	pipsLayout.SortOrder = Enum.SortOrder.LayoutOrder
	pipsLayout.Parent = pips
	for index in DinoStats.resizes do
		local pip = Instance.new("Frame")
		pip.Name = `Pip{index}`
		pip.LayoutOrder = index
		pip.Size = UDim2.fromOffset(44, 22)
		pip.Parent = pips
		UiKit.corner(pip, 8)
		UiKit.stroke(pip, 3)
	end
	local resizeButtons = Instance.new("Frame")
	resizeButtons.BackgroundTransparency = 1
	resizeButtons.Position = UDim2.fromOffset(0, 160)
	resizeButtons.Size = UDim2.new(1, 0, 0, 64)
	resizeButtons.Parent = resizePanel.body
	local buttonsLayout = Instance.new("UIListLayout")
	buttonsLayout.FillDirection = Enum.FillDirection.Horizontal
	buttonsLayout.HorizontalAlignment = Enum.HorizontalAlignment.Center
	buttonsLayout.Padding = UDim.new(0, 10)
	buttonsLayout.SortOrder = Enum.SortOrder.LayoutOrder
	buttonsLayout.Parent = resizeButtons
	local resizeNote = UiKit.muted(resizePanel.body, "Only changes how big it looks. It earns the same.", 18)
	resizeNote.Position = UDim2.fromOffset(0, 236)

	local function resizeTarget()
		for _, dino in dinos do
			if dino.key == resizeKey then
				return dino
			end
		end
		return nil
	end
	local function resizeIndex(dino): number
		for index, option in DinoStats.resizes do
			if option.id == (dino.resize or "Normal") then
				return index
			end
		end
		return 1
	end
	local function renderResize()
		local dino = resizeTarget()
		if not dino then
			UiKit.closePanel(resizePanel)
			return
		end
		local index = resizeIndex(dino)
		local option = DinoStats.resizes[index]
		resizeName.Text = option.name
		resizeTimes.Text = `x{option.scale} SIZE`
		for pipIndex in DinoStats.resizes do
			pips[`Pip{pipIndex}`].BackgroundColor3 = if pipIndex <= index then Color3.fromRGB(190, 120, 255) else Color3.fromRGB(45, 40, 70)
		end
	end
	local function resizeTo(index: number)
		local dino = resizeTarget()
		local option = DinoStats.resizes[math.clamp(index, 1, #DinoStats.resizes)]
		if dino and option.id ~= (dino.resize or "Normal") then
			send("resize", dino.key, option.id)
		end
	end
	for order, spec in { { "SMALLEST", "blue", 128, 20, 1 }, { "-", "blue", 64, 34, -1 }, { "+", "green", 64, 34, 1 }, { "BIGGEST", "green", 128, 20, math.huge } } do
		local label, style, width, textSize, step = spec[1], spec[2], spec[3], spec[4], spec[5]
		local button = UiKit.button(resizeButtons, label, style, width, 56, textSize)
		button.LayoutOrder = order
		button.Activated:Connect(function()
			local dino = resizeTarget()
			if not dino then
				return
			end
			if label == "SMALLEST" then
				resizeTo(1)
			elseif label == "BIGGEST" then
				resizeTo(#DinoStats.resizes)
			else
				resizeTo(resizeIndex(dino) + step)
			end
		end)
	end
	local function openResize(dino)
		resizeKey = dino.key
		resizePanel.header:FindFirstChildWhichIsA("TextLabel").Text = `Resize {dino.name}`
		renderResize()
		UiKit.openPanel(resizePanel)
	end

	-- Backpack dinos in hotbar order (the list arrives best first). The carried one is always on the hotbar: past the
	-- last key it takes the last slot, so a new catch carried off the reveal shows even when it's not among the best.
	local function backpack()
		local list = {}
		local heldKey = player:GetAttribute("HeldDino")
		for _, dino in dinos do
			if not dino.onPlot then
				table.insert(list, dino)
			end
		end
		for index = #HOTBAR_KEYS + 1, #list do
			if list[index].key == heldKey then
				table.insert(list, #HOTBAR_KEYS, table.remove(list, index))
				break
			end
		end
		return list
	end

	local function heldDino()
		local key = player:GetAttribute("HeldDino")
		for _, dino in dinos do
			if dino.key == key and not dino.onPlot then
				return dino
			end
		end
		return nil
	end

	local function renderHotbar()
		local list = backpack()
		local heldKey = player:GetAttribute("HeldDino")
		for index, slot in hud.slots do
			local dino = list[index]
			if (dino and dino.key) ~= slot.key then
				slot.key = dino and dino.key
				if slot.view then
					slot.view:Destroy()
					slot.view = nil
				end
				local pair = UiKit.RARITY[if dino then UiKit.rarityOf(dino.id) else "common"]
				slot.gradient.Color = ColorSequence.new(UiKit.color(pair[1]), UiKit.color(pair[2]))
				if dino then
					slot.view = UiKit.monster(slot.button, dino.id, { mutation = dino.mutation, position = UDim2.fromOffset(4, 5), size = UDim2.new(1, -8, 1, -10) })
				end
			end
			slot.income.Text = if dino then `{Format.cash(dino.income)}/s` else ""
			slot.button.BackgroundTransparency = if dino then 0 else 0.55
			slot.gradient.Enabled = dino ~= nil
			slot.button.BackgroundColor3 = if dino then Color3.new(1, 1, 1) else UiKit.DEEP
			local held = dino ~= nil and dino.key == heldKey
			slot.edge.Color = if held then Color3.new(1, 1, 1) else UiKit.INK
			slot.raise.Scale = if held then HELD_RAISE else 1
		end
	end

	local function equipSlot(index: number)
		local dino = backpack()[index]
		if dino then
			send("equip", dino.key)
		end
	end

	-- Rows build their 3D tile only once scrolled into view, since a backpack can hold a lot.
	local function showVisibleTiles()
		local top = hud.list.AbsolutePosition.Y
		local bottom = top + hud.list.AbsoluteWindowSize.Y
		for _, row in hud.list:GetChildren() do
			local tile = row:FindFirstChild("Tile")
			if tile and not tile:FindFirstChildOfClass("ViewportFrame") then
				local y = row.AbsolutePosition.Y
				if y < bottom + ROW_HEIGHT and y + ROW_HEIGHT > top - ROW_HEIGHT then
					UiKit.monster(tile, row:GetAttribute("DinoId"), { mutation = row:GetAttribute("Mutation"), position = UDim2.fromOffset(3, 3), size = UDim2.new(1, -6, 1, -10) })
				end
			end
		end
	end

	-- One monster's row: its real model on a rarity tile with its colour mutation in a chip under it, its rarity, its
	-- name, its size mutation in silver and its $/s, then EQUIP (or HOLDING, or PICK UP) and SELL.
	local function makeRow(dino, order: number)
		local holding = dino.key == player:GetAttribute("HeldDino")
		local rarity = UiKit.rarityOf(dino.id)
		local row = Instance.new("Frame")
		row.Name = "Row"
		row.LayoutOrder = order
		row.BackgroundColor3 = UiKit.ROW
		row.Size = UDim2.fromOffset(ROW_WIDTH, ROW_HEIGHT)
		row:SetAttribute("DinoId", dino.id)
		row:SetAttribute("Mutation", dino.mutation)
		row.Parent = hud.list
		UiKit.corner(row, 20)
		UiKit.stroke(row, 4, if holding then Color3.new(1, 1, 1) else nil)

		local tile = Instance.new("Frame")
		tile.Name = "Tile"
		tile.Position = UDim2.fromOffset(8, 8)
		tile.Size = UDim2.fromOffset(84, 84)
		tile.Parent = row
		UiKit.gradient(tile, rarity)
		UiKit.corner(tile, 16)
		UiKit.stroke(tile, 4)

		local mutation = DinoStats.findOption(Catch.mutations, dino.mutation)
		if mutation then
			local chip = Instance.new("Frame")
			chip.Name = "Mutation"
			chip.Position = UDim2.fromOffset(14, 78)
			chip.AutomaticSize = Enum.AutomaticSize.X
			chip.Size = UDim2.fromOffset(0, 20)
			chip.BackgroundColor3 = mutation.color
			chip.ZIndex = 3
			chip.Parent = row
			UiKit.corner(chip, 8)
			UiKit.stroke(chip, 3)
			local chipPad = Instance.new("UIPadding")
			chipPad.PaddingLeft = UDim.new(0, 7)
			chipPad.PaddingRight = UDim.new(0, 7)
			chipPad.Parent = chip
			local chipLabel = UiKit.text(chip, mutation.name, 13)
			chipLabel.AutomaticSize = Enum.AutomaticSize.X
			chipLabel.Size = UDim2.fromScale(0, 1)
			chipLabel.ZIndex = 3
		end

		-- The size it shows: caught, or grown to by feeding (then marked FED, Config/Chonk).
		local size = DinoStats.findOption(Catch.sizes, dino.shownSize)
		local chonkWord = if dino.chonk > 0 then `  CHONK {dino.chonk}` else ""
		local tier = RarityLabel.create(row, UiKit.rarityLook(dino.id), 14, Enum.TextXAlignment.Left, UiKit.rarityWord(dino.id) .. chonkWord)
		tier.Position = UDim2.fromOffset(104, 8)
		tier.Size = UDim2.fromOffset(176, 18)
		local name = UiKit.text(row, dino.name, 24, nil, Enum.TextXAlignment.Left)
		name.Name = "DinoName"
		name.Position = UDim2.fromOffset(104, 28)
		name.Size = UDim2.fromOffset(176, 30)
		name.TextScaled = true
		local limit = Instance.new("UITextSizeConstraint")
		limit.MaxTextSize = 24
		limit.Parent = name
		local stats = Instance.new("Frame")
		stats.BackgroundTransparency = 1
		stats.Position = UDim2.fromOffset(104, 64)
		stats.Size = UDim2.fromOffset(184, 24)
		stats.Parent = row
		local statsLayout = Instance.new("UIListLayout")
		statsLayout.FillDirection = Enum.FillDirection.Horizontal
		statsLayout.VerticalAlignment = Enum.VerticalAlignment.Center
		statsLayout.Padding = UDim.new(0, 8)
		statsLayout.SortOrder = Enum.SortOrder.LayoutOrder
		statsLayout.Parent = stats
		if size then
			local sizeWord = UiKit.text(stats, if dino.fed then `{size.name} FED` else size.name, 15, SIZE_WORD)
			sizeWord.AutomaticSize = Enum.AutomaticSize.X
			sizeWord.Size = UDim2.fromScale(0, 1)
		end
		local income = UiKit.text(stats, `{Format.cash(dino.income)}/s`, 18, UiKit.CASH)
		income.LayoutOrder = 2
		income.AutomaticSize = Enum.AutomaticSize.X
		income.Size = UDim2.fromScale(0, 1)

		local move = UiKit.button(row, if dino.onPlot then "PICK UP" elseif holding then "HOLDING" else "EQUIP", if holding then "green" else "blue", 124, 38, 19)
		move.Name = "Move"
		move.AnchorPoint = Vector2.new(1, 0)
		move.Position = UDim2.new(1, -12, 0, 10)
		move.Activated:Connect(function()
			if dino.onPlot then
				send("pickUp", dino.key)
			else
				-- Equipped: close the panel so the player can pick a spot on the plot.
				send("equip", dino.key)
				UiKit.closePanel(hud.panel)
			end
		end)

		local sell = UiKit.button(row, if confirmKey == dino.key then "SURE?" else `SELL {Format.cash(dino.sellPrice)}`, "red", 124, 38, 17)
		sell.Name = "Sell"
		-- On the base the second button feeds it; it's sold from the backpack, or here once it can't grow.
		local feedable = dino.onPlot and not DinoStats.special(dino.id) and dino.chonk < Chonk.maxLevel
		sell.Visible = DinoStats.sellable(dino.id) and not feedable
		if DinoStats.special(dino.id) then -- bought with Robux: never sold, resized instead
			local resize = UiKit.button(row, "RESIZE", "purple", 124, 38, 18)
			resize.Name = "Resize"
			resize.AnchorPoint = Vector2.new(1, 0)
			resize.Position = UDim2.new(1, -12, 0, 52)
			resize.Activated:Connect(function()
				openResize(dino)
			end)
		end
		if feedable then
			local feed = UiKit.button(row, "FEED", "purple", 124, 38, 18)
			feed.Name = "Feed"
			feed.AnchorPoint = Vector2.new(1, 0)
			feed.Position = UDim2.new(1, -12, 0, 52)
			feed.Activated:Connect(function()
				openFeed(dino)
			end)
		end
		sell.AnchorPoint = Vector2.new(1, 0)
		sell.Position = UDim2.new(1, -12, 0, 52)
		sell.Activated:Connect(function()
			if confirmKey == dino.key then
				confirmKey = nil
				send("sell", dino.key)
			else
				confirmKey = dino.key
				renderList()
				task.delay(SELL_CONFIRM_TIME, function()
					if confirmKey == dino.key then
						confirmKey = nil
						renderList()
					end
				end)
			end
		end)
	end

	-- The list is rebuilt only while the panel is open: picking up or placing a monster changes it twice (HeldDino,
	-- then DinosChanged), and rebuilding every row each time, panel shut, was a hitch on every pick-up. Opening the
	-- panel catches up.
	local listStale = true
	renderList = function()
		if not hud.panel.frame.Visible then
			listStale = true
			return
		end
		listStale = false
		for _, child in hud.list:GetChildren() do
			if child:IsA("Frame") then
				child:Destroy()
			end
		end
		local onPlot = 0
		local order = 0
		for _, dino in dinos do
			if dino.onPlot then
				onPlot += 1
			end
			if dino.onPlot == (tab == "plot") then
				order += 1
				makeRow(dino, order)
			end
		end
		local inBackpack = #dinos - onPlot
		hud.tabs.plot.Text = `ON PLOT {onPlot}/{slots}`
		hud.tabs.backpack.Text = `BACKPACK {inBackpack}`
		for name, button in hud.tabs do
			UiKit.restyle(button, button.Text, if name == tab then "green" else "dark")
		end
		hud.empty.Text = if #dinos == 0 then "No monsters yet. Throw an egg to catch one!"
			elseif order == 0 then (if tab == "plot" then "Nothing on your plot. Equip a monster and click your plot." else "Your backpack is empty.")
			else ""
		hud.empty.Visible = order == 0
		task.defer(showVisibleTiles)
	end

	for name, button in hud.tabs do
		button.Activated:Connect(function()
			tab = name
			renderList()
		end)
	end
	hud.list:GetPropertyChangedSignal("CanvasPosition"):Connect(showVisibleTiles)

	-- The cash counter rolls up to its new value instead of jumping, so money visibly pours in.
	local shownCash = player:GetAttribute("Cash") or 0
	local function renderCash()
		hud.income.Text = `+{Format.cash(player:GetAttribute("Income") or 0)}/s`
	end
	RunService.Heartbeat:Connect(function(dt)
		local target = player:GetAttribute("Cash") or 0
		local gap = target - shownCash
		shownCash = if math.abs(gap) <= math.max(1, math.abs(target) * 1e-4) then target else shownCash + gap * math.min(dt * 6, 1)
		hud.cash.Text = Format.cash(shownCash)
	end)

	hud.open.Activated:Connect(function()
		UiKit.togglePanel(hud.panel)
		task.defer(showVisibleTiles)
	end)

	-- Stepping onto the SELL stall's pad opens the Sell Stand; walking off closes it again.
	local onStallPad = false
	RunService.Heartbeat:Connect(function()
		local character = player.Character
		local root = character and character:FindFirstChild("HumanoidRootPart")
		local nowOnPad = root ~= nil and Hub.isOnPad(Hub.stallCFrame(Hub.sellStall), root.Position)
		if nowOnPad ~= onStallPad then
			onStallPad = nowOnPad
			if nowOnPad then
				sellPanel.open()
			else
				sellPanel.close()
			end
		end
	end)
	hud.equip.Activated:Connect(function()
		send("equipBest")
	end)
	hud.unequipAll.Activated:Connect(function()
		send("unequipAll")
	end)
	remotes.DinosChanged.OnClientEvent:Connect(function(newDinos, newSlots)
		dinos = newDinos
		slots = newSlots
		renderList()
		renderHotbar()
		sellPanel.setDinos(newDinos)
		feedPanel.setDinos(newDinos)
		if resizePanel.frame.Visible then
			renderResize()
		end
	end)
	remotes.Notice.OnClientEvent:Connect(function(text: string, bad: boolean?)
		PopText.notice(text, not bad)
	end)
	-- Training fills the bottom of the screen, so the hotbar steps aside.
	-- The open My Dinos panel stands where the hotbar's right end is, and lists the same monsters, so the hotbar
	-- steps aside for it too, and for the Sell Stand.
	local function renderHotbarVisible()
		hud.hotbar.Visible = player:GetAttribute("IsTraining") ~= true and not feedPanel.panel.frame.Visible and not hud.panel.frame.Visible and not sellPanel.panel.frame.Visible
	end
	player:GetAttributeChangedSignal("IsTraining"):Connect(renderHotbarVisible)
	hud.panel.frame:GetPropertyChangedSignal("Visible"):Connect(function()
		renderHotbarVisible()
		if hud.panel.frame.Visible and listStale then
			renderList()
		end
	end)
	sellPanel.panel.frame:GetPropertyChangedSignal("Visible"):Connect(renderHotbarVisible)
	feedPanel.panel.frame:GetPropertyChangedSignal("Visible"):Connect(renderHotbarVisible)
	renderHotbarVisible()
	player:GetAttributeChangedSignal("HeldDino"):Connect(function()
		renderList()
		renderHotbar()
	end)

	-- Our own hotbar takes the number keys, so Roblox's tool bar stays out of the way.
	pcall(function()
		StarterGui:SetCoreGuiEnabled(Enum.CoreGuiType.Backpack, false)
	end)
	for index, slot in hud.slots do
		slot.button.Activated:Connect(function()
			equipSlot(index)
		end)
	end

	-- Placing: a see-through copy of the equipped dino follows the pointer over the plot,
	-- green where it can stand and red where it can't. A click (or tap) asks the server.
	local ghost: Model? = nil
	local ghostKey: number? = nil
	local aim = nil -- { x, z, valid } for the spot under the mouse this frame

	local function clearGhost()
		if ghost then
			ghost:Destroy()
		end
		ghost, ghostKey = nil, nil
	end

	local function ghostFor(dino): Model
		if ghost and ghostKey == dino.key then
			return ghost
		end
		clearGhost()
		local model = DinoModel.build(dino.id, dino.mutation, Vector3.zero, DinoModel.entryScale(dino))
		model.Name = "PlacementGhost"
		for _, part in model:GetDescendants() do
			if part:IsA("BasePart") and part.Transparency < 1 then
				part.Transparency = GHOST_TRANSPARENCY
			end
		end
		local highlight = Instance.new("Highlight")
		highlight.Name = "GhostTint" -- not "Highlight": some monsters have a part by that name (Parasaurolophus)
		highlight.FillTransparency = 0.6
		highlight.Parent = model
		ghost, ghostKey = model, dino.key
		return model
	end

	local function plotHasRoom(): boolean
		local onPlot = 0
		for _, dino in dinos do
			if dino.onPlot then
				onPlot += 1
			end
		end
		return onPlot < slots
	end

	-- The spot on the player's own plot under a point on the screen, or nil.
	local function spotAt(viewportPoint: Vector2)
		local plotIndex = player:GetAttribute("PlotIndex")
		local plots = workspace:FindFirstChild("Plots")
		local plotModel = plotIndex and plots and plots:FindFirstChild(`Plot{plotIndex}`)
		local ground = plotModel and plotModel:FindFirstChild("Ground")
		if not ground then
			return nil
		end
		local ray = workspace.CurrentCamera:ViewportPointToRay(viewportPoint.X, viewportPoint.Y)
		local params = RaycastParams.new()
		params.FilterType = Enum.RaycastFilterType.Include
		params.FilterDescendantsInstances = { plotModel }
		-- The fence or the upgrade sign in the way means no spot, so clicking the sign never drops a dino.
		local result = workspace:Raycast(ray.Origin, ray.Direction * 1000, params)
		if not result or result.Instance ~= ground then
			return nil
		end
		local offset = result.Position - Plot.positions[plotIndex]
		return { x = offset.X, z = offset.Z, inBounds = Plot.inBounds(offset.X, offset.Z), plotIndex = plotIndex }
	end

	-- One of the player's own monsters standing on their plot under a point on the screen, or nil. Tapping or
	-- clicking it picks it up (onto the head, ready to put down elsewhere), the same as PICK UP in My Dinos.
	local function statueAt(viewportPoint: Vector2): Model?
		local plotIndex = player:GetAttribute("PlotIndex")
		local plots = workspace:FindFirstChild("Plots")
		local plotModel = plotIndex and plots and plots:FindFirstChild(`Plot{plotIndex}`)
		local statues = plotModel and plotModel:FindFirstChild("Statues")
		if not statues then
			return nil
		end
		local ray = workspace.CurrentCamera:ViewportPointToRay(viewportPoint.X, viewportPoint.Y)
		local params = RaycastParams.new()
		params.FilterType = Enum.RaycastFilterType.Include
		params.FilterDescendantsInstances = { plotModel } -- so the fence in front of a monster still blocks it
		local result = workspace:Raycast(ray.Origin, ray.Direction * 1000, params)
		local hit: Instance? = result and result.Instance
		while hit and hit.Parent ~= statues do
			hit = hit.Parent
		end
		return if hit and hit:GetAttribute("DinoKey") then hit :: Model else nil
	end

	-- On a computer, the monster a click would pick up gets a white outline while the mouse is over it. Each monster
	-- keeps its own outline, made the first time it's hovered and only switched on and off after that: moving one
	-- Highlight from monster to monster froze the game for up to a tenth of a second each time (measured in Studio
	-- 2026-11-07), which was the lag on walking onto the base and on sweeping the mouse over it.
	local hovered: Model? = nil
	local function outlineOf(statue: Model): Highlight
		local outline = statue:FindFirstChild("PickUpHover") :: Highlight?
		if not outline then
			outline = Instance.new("Highlight")
			outline.Name = "PickUpHover"
			outline.FillTransparency = 1
			outline.OutlineColor = Color3.new(1, 1, 1)
			outline.DepthMode = Enum.HighlightDepthMode.Occluded
			outline.Enabled = false
			outline.Adornee = statue
			outline.Parent = statue
		end
		return outline :: Highlight
	end
	local function setHovered(statue: Model?)
		if statue == hovered then
			return
		end
		if hovered and hovered.Parent then
			outlineOf(hovered).Enabled = false
		end
		hovered = statue
		if statue then
			outlineOf(statue).Enabled = true
		end
	end

	local function isTraining(): boolean
		return player:GetAttribute("IsTraining") == true
	end

	-- Consoles have no mouse or touch: with a controller, the spot (or monster) aimed at is the ground a few studs in
	-- front of the player, and X or R2 places or picks up. Without this, console players were stuck holding their
	-- first catch (Creator Analytics 2026-11-10: 9% of console players still playing at 5 minutes).
	local GAMEPAD_BUTTONS = { Enum.KeyCode.ButtonX, Enum.KeyCode.ButtonR2 }
	local GAMEPAD_REACH = 8 -- studs in front of the player
	local function usingGamepad(): boolean
		local last = UserInputService:GetLastInputType()
		return last.Name:sub(1, 7) == "Gamepad"
	end
	-- The screen point to aim with: the mouse, or with a controller, the ground in front of the character.
	local function aimPoint(): Vector2
		if usingGamepad() then
			local character = player.Character
			local root = character and character:FindFirstChild("HumanoidRootPart") :: BasePart?
			if root then
				local ahead = root.CFrame.LookVector * Vector3.new(1, 0, 1)
				local ground = root.Position + ahead.Unit * GAMEPAD_REACH - Vector3.new(0, root.Size.Y * 1.5, 0)
				local point = workspace.CurrentCamera:WorldToViewportPoint(ground)
				return Vector2.new(point.X, point.Y)
			end
		end
		return UserInputService:GetMouseLocation()
	end

	RunService.RenderStepped:Connect(function()
		local dino = heldDino()
		-- Training pauses placing: the hint would sit right on the STOP button, and it comes back on stopping.
		if not dino or isTraining() then
			clearGhost()
			aim = nil
			hud.hint.Visible = false
			setHovered(if not dino and not isTraining() and not player:GetAttribute("LeashArmed") and UserInputService.MouseEnabled then statueAt(UserInputService:GetMouseLocation()) else nil)
			return
		end
		setHovered(nil)
		local touch = UserInputService.TouchEnabled and not UserInputService.MouseEnabled
		local spot = spotAt(aimPoint())
		local model = ghostFor(dino)
		local room = plotHasRoom()
		hud.hint.Visible = true
		if not player:GetAttribute("PlotIndex") then
			hud.hint.Text = "You don't have a plot in this server"
		elseif not room then
			hud.hint.Text = `Plot full ({slots}/{slots}): pick a monster up first`
		elseif not spot then
			hud.hint.Text = `Go to your plot to place {dino.name}`
		elseif not spot.inBounds then
			hud.hint.Text = "Too close to the edge"
		else
			hud.hint.Text = `{if usingGamepad() then "Press X" elseif touch then "Tap" else "Click"} to place {dino.name}`
		end
		if spot then
			local valid = spot.inBounds and room
			aim = { x = spot.x, z = spot.z, valid = valid }
			model:PivotTo(CFrame.new(Plot.positions[spot.plotIndex] + Vector3.new(spot.x, Plot.size.Y, spot.z)))
			local tint = model:FindFirstChild("GhostTint") :: Highlight
			tint.FillColor = if valid then GOOD_SPOT else BAD_SPOT
			tint.OutlineColor = if valid then GOOD_SPOT else BAD_SPOT
			model.Parent = workspace
		else
			aim = nil
			model.Parent = nil
		end
	end)

	UserInputService.InputBegan:Connect(function(input, gameProcessed)
		if gameProcessed or isTraining() then -- training: no stray equips or pick-ups (PlotService refuses them too)
			return
		end
		if player:GetAttribute("LeashArmed") and input.UserInputType == Enum.UserInputType.MouseButton1 then
			return -- the Leash is on: clicks take hold of monsters and throw them (LeashController)
		end
		for index, keyCode in HOTBAR_KEYS do
			if input.KeyCode == keyCode then
				equipSlot(index)
				return
			end
		end
		if input.UserInputType ~= Enum.UserInputType.MouseButton1 and not table.find(GAMEPAD_BUTTONS, input.KeyCode) then
			return
		end
		local dino = heldDino()
		if not dino then
			local statue = statueAt(aimPoint())
			if statue then
				send("pickUp", statue:GetAttribute("DinoKey"))
			end
		elseif aim and aim.valid then
			send("placeAt", dino.key, aim.x, aim.z)
		end
	end)
	-- Phones: a tap (not a drag, which turns the camera) puts the carried monster down where it lands, or with
	-- nothing carried picks up the monster tapped. Phones have no hover, so the tap itself picks the spot. Touch
	-- positions leave out the top bar, while the camera's ray needs the whole screen.
	UserInputService.TouchTap:Connect(function(positions, gameProcessed)
		if gameProcessed or #positions ~= 1 or isTraining() or player:GetAttribute("LeashArmed") then
			return
		end
		local point = positions[1] + GuiService:GetGuiInset()
		local dino = heldDino()
		if not dino then
			local statue = statueAt(point)
			if statue then
				send("pickUp", statue:GetAttribute("DinoKey"))
			end
			return
		end
		local spot = spotAt(point)
		if spot and spot.inBounds and plotHasRoom() and not isTraining() then
			send("placeAt", dino.key, spot.x, spot.z)
		end
	end)
	-- Spending floats a red "-$X" up beside the cash and other gains a green "+$X", but not the plot's $/s
	-- ticking in every second (PlotService pays exactly the Income attribute each second). A rise in $/s floats
	-- up beside the $/s line. Both start past the end of the longer number.
	local lastCash: number? = nil
	local lastIncome: number? = nil
	local function moneyPop(text: string, color: Color3, row: TextLabel)
		local x = math.max(PopText.after(hud.cash).X, PopText.after(hud.income).X)
		PopText.float(text, color, Vector2.new(x, PopText.after(row).Y), Vector2.new(0, 0.5))
	end
	player:GetAttributeChangedSignal("Cash"):Connect(function()
		local cash = player:GetAttribute("Cash") or 0
		if lastCash then
			local change = cash - lastCash
			local tick = player:GetAttribute("Income") or 0
			if change < 0 then
				moneyPop(`-{Format.cash(-change)}`, Pop.colors.spent, hud.cash)
			elseif change > 0 and math.abs(change - tick) > math.max(1, tick * 0.001) then
				moneyPop(`+{Format.cash(change)}`, Pop.colors.cash, hud.cash)
			end
		end
		lastCash = cash
		renderCash()
	end)
	player:GetAttributeChangedSignal("Income"):Connect(function()
		local income = player:GetAttribute("Income") or 0
		if lastIncome and income > lastIncome then
			moneyPop(`+{Format.cash(income - lastIncome)}/s`, Pop.colors.cash, hud.income)
		end
		lastIncome = income
		renderCash()
	end)

	renderList()
	renderHotbar()
	renderCash()
	lastCash = player:GetAttribute("Cash")
	lastIncome = player:GetAttribute("Income")
end

return PlotController
