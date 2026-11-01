-- The cash display and the My Dinos panel. Display and requests only: the server
-- decides what actually happens to a dino and what it's worth.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Catch = require(ReplicatedStorage.Shared.Config.Catch)
local DinoModel = require(ReplicatedStorage.Shared.DinoModel)
local DinoStats = require(ReplicatedStorage.Shared.DinoStats)
local Format = require(ReplicatedStorage.Shared.Format)

local player = Players.LocalPlayer

local PlotController = {}

local INK = Color3.fromRGB(20, 22, 28)
local PANEL = Color3.fromRGB(28, 30, 36)
local ROW = Color3.fromRGB(58, 62, 72)
local ACCENT = Color3.fromRGB(226, 142, 58)
local PLACE = Color3.fromRGB(90, 170, 80)
local PICK_UP = Color3.fromRGB(70, 130, 210)
local SELL = Color3.fromRGB(190, 70, 60)
local TEXT = Color3.new(1, 1, 1)
local CASH = Color3.fromRGB(120, 235, 120)
local TAG = Color3.fromRGB(255, 214, 70)
local ROW_HEIGHT = 84
local SELL_CONFIRM_TIME = 3 -- seconds the "SURE?" button waits for a second tap

local function corner(parent: Instance, radius: number)
	local uiCorner = Instance.new("UICorner")
	uiCorner.CornerRadius = UDim.new(0, radius)
	uiCorner.Parent = parent
end

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

local function makeButton(parent: Instance, text: string, color: Color3, position: UDim2, size: UDim2): TextButton
	local button = Instance.new("TextButton")
	button.BackgroundColor3 = color
	button.Font = Enum.Font.GothamBlack
	button.Position = position
	button.Size = size
	button.Text = text
	button.TextColor3 = TEXT
	button.TextScaled = true
	button.Parent = parent
	corner(button, 10)
	local padding = Instance.new("UIPadding")
	padding.PaddingTop = UDim.new(0, 8)
	padding.PaddingBottom = UDim.new(0, 8)
	padding.PaddingLeft = UDim.new(0, 6)
	padding.PaddingRight = UDim.new(0, 6)
	padding.Parent = button
	return button
end

local function buildGui()
	local gui = Instance.new("ScreenGui")
	gui.Name = "PlotHud"
	gui.ResetOnSpawn = false
	gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	gui.DisplayOrder = 1 -- so the open panel covers the training display
	gui.Parent = player:WaitForChild("PlayerGui")

	local cashPill = Instance.new("Frame")
	cashPill.Name = "CashPill"
	cashPill.AnchorPoint = Vector2.new(0, 0.5)
	cashPill.Position = UDim2.new(0, 16, 0.5, -90)
	cashPill.Size = UDim2.fromOffset(190, 70)
	cashPill.BackgroundColor3 = PANEL
	cashPill.BackgroundTransparency = 0.12
	cashPill.Parent = gui
	corner(cashPill, 12)

	local cash = makeLabel(cashPill, Enum.Font.GothamBlack, CASH, UDim2.fromOffset(12, 6), UDim2.new(1, -24, 0, 32))
	cash.Name = "Cash"
	local income = makeLabel(cashPill, Enum.Font.GothamBold, TEXT, UDim2.fromOffset(12, 40), UDim2.new(1, -24, 0, 20))
	income.Name = "Income"

	local open = makeButton(gui, "MY DINOS", ACCENT, UDim2.new(0, 16, 0.5, -48), UDim2.fromOffset(190, 46))
	open.Name = "OpenDinos"
	open.AnchorPoint = Vector2.new(0, 0)

	local panel = Instance.new("Frame")
	panel.Name = "DinoPanel"
	panel.AnchorPoint = Vector2.new(0.5, 0.5)
	panel.Position = UDim2.fromScale(0.5, 0.5)
	panel.Size = UDim2.fromScale(0.9, 0.86)
	panel.BackgroundColor3 = PANEL
	panel.BackgroundTransparency = 0.06
	panel.Visible = false
	panel.ZIndex = 2
	panel.Parent = gui
	corner(panel, 16)
	local panelLimit = Instance.new("UISizeConstraint")
	panelLimit.MaxSize = Vector2.new(640, 560)
	panelLimit.Parent = panel

	local title = makeLabel(panel, Enum.Font.GothamBlack, TEXT, UDim2.fromOffset(16, 12), UDim2.new(0.4, 0, 0, 32))
	title.Text = "My Dinos"
	local count = makeLabel(panel, Enum.Font.GothamBold, TAG, UDim2.fromOffset(16, 46), UDim2.new(0.4, 0, 0, 20))
	count.Name = "Count"

	local equip = makeButton(panel, "EQUIP BEST", ACCENT, UDim2.new(1, -212, 0, 14), UDim2.fromOffset(140, 46))
	equip.Name = "EquipBest"
	local close = makeButton(panel, "X", SELL, UDim2.new(1, -60, 0, 14), UDim2.fromOffset(46, 46))
	close.Name = "Close"

	local list = Instance.new("ScrollingFrame")
	list.Name = "List"
	list.BackgroundTransparency = 1
	list.BorderSizePixel = 0
	list.Position = UDim2.fromOffset(12, 76)
	list.Size = UDim2.new(1, -24, 1, -88)
	list.AutomaticCanvasSize = Enum.AutomaticSize.Y
	list.CanvasSize = UDim2.new()
	list.ScrollBarThickness = 8
	list.Parent = panel
	local layout = Instance.new("UIListLayout")
	layout.Padding = UDim.new(0, 8)
	layout.SortOrder = Enum.SortOrder.LayoutOrder
	layout.Parent = list

	local empty = makeLabel(panel, Enum.Font.GothamBold, TEXT, UDim2.new(0, 16, 0, 90), UDim2.new(1, -32, 0, 26))
	empty.Name = "Empty"
	empty.Text = "No dinos yet. Throw an egg to catch one!"

	return {
		cash = cash,
		income = income,
		open = open,
		panel = panel,
		count = count,
		equip = equip,
		close = close,
		list = list,
		empty = empty,
	}
end

local function tagText(dino): string
	local parts = {}
	local mutation = DinoStats.findOption(Catch.mutations, dino.mutation)
	if mutation then
		table.insert(parts, mutation.name)
	end
	local size = DinoStats.findOption(Catch.sizes, dino.size)
	if size then
		table.insert(parts, size.name)
	end
	return table.concat(parts, " ")
end

function PlotController.start()
	local remotes = ReplicatedStorage:WaitForChild("PlotRemotes")
	local hud = buildGui()
	local confirmKey = nil -- the dino whose SELL button is showing "SURE?"
	local dinos = {}
	local slots = 0
	local renderList

	local function send(action: string, key: number?)
		remotes.DinoAction:FireServer(action, key)
	end

	local function makeRow(dino, order: number)
		local row = Instance.new("Frame")
		row.Name = "Row"
		row.LayoutOrder = order
		row.BackgroundColor3 = ROW
		row.Size = UDim2.new(1, -10, 0, ROW_HEIGHT)
		row.Parent = hud.list
		corner(row, 12)

		local swatch = Instance.new("Frame")
		swatch.Position = UDim2.fromOffset(10, 12)
		swatch.Size = UDim2.fromOffset(60, 60)
		swatch.BackgroundColor3 = DinoModel.color(dino.name, dino.mutation)
		swatch.Parent = row
		corner(swatch, 10)
		local stroke = Instance.new("UIStroke")
		stroke.Color = INK
		stroke.Thickness = 2
		stroke.Parent = swatch

		local tag = makeLabel(row, Enum.Font.GothamBlack, TAG, UDim2.fromOffset(80, 6), UDim2.new(1, -310, 0, 16))
		tag.Text = tagText(dino)
		local name = makeLabel(row, Enum.Font.GothamBlack, TEXT, UDim2.fromOffset(80, 24), UDim2.new(1, -310, 0, 26))
		name.Name = "DinoName"
		name.Text = dino.name
		local income = makeLabel(row, Enum.Font.GothamBold, CASH, UDim2.fromOffset(80, 54), UDim2.new(1, -310, 0, 20))
		income.Text = `{Format.cash(dino.income)}/s`

		local move = makeButton(
			row,
			if dino.onPlot then "PICK UP" else "PLACE",
			if dino.onPlot then PICK_UP else PLACE,
			UDim2.new(1, -222, 0, 18),
			UDim2.fromOffset(104, 48)
		)
		move.Name = "Move"
		move.Activated:Connect(function()
			send(if dino.onPlot then "pickUp" else "place", dino.key)
		end)

		local sell = makeButton(
			row,
			if confirmKey == dino.key then "SURE?" else `SELL {Format.cash(dino.sellPrice)}`,
			SELL,
			UDim2.new(1, -110, 0, 18),
			UDim2.fromOffset(100, 48)
		)
		sell.Name = "Sell"
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

	renderList = function()
		for _, child in hud.list:GetChildren() do
			if child:IsA("Frame") then
				child:Destroy()
			end
		end
		local onPlot = 0
		for order, dino in dinos do
			if dino.onPlot then
				onPlot += 1
			end
			makeRow(dino, order)
		end
		hud.count.Text = `On plot {onPlot} / {slots}  ·  Backpack {#dinos - onPlot}`
		hud.empty.Visible = #dinos == 0
	end

	local function renderCash()
		hud.cash.Text = Format.cash(player:GetAttribute("Cash") or 0)
		hud.income.Text = `+{Format.cash(player:GetAttribute("Income") or 0)}/s`
	end

	hud.open.Activated:Connect(function()
		hud.panel.Visible = not hud.panel.Visible
	end)
	hud.close.Activated:Connect(function()
		hud.panel.Visible = false
	end)
	hud.equip.Activated:Connect(function()
		send("equipBest")
	end)
	remotes.DinosChanged.OnClientEvent:Connect(function(newDinos, newSlots)
		dinos = newDinos
		slots = newSlots
		renderList()
	end)
	player:GetAttributeChangedSignal("Cash"):Connect(renderCash)
	player:GetAttributeChangedSignal("Income"):Connect(renderCash)

	renderList()
	renderCash()
end

return PlotController
