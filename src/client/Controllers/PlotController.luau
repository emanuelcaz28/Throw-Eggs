-- The cash display, the My Dinos panel, the hotbar of backpack dinos and placing an equipped
-- dino on the plot. Display and requests only: the server decides what actually happens to a
-- dino, checks every spot and works out what it's worth.
local GuiService = game:GetService("GuiService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local StarterGui = game:GetService("StarterGui")
local UserInputService = game:GetService("UserInputService")

local Catch = require(ReplicatedStorage.Shared.Config.Catch)
local DinoModel = require(ReplicatedStorage.Shared.DinoModel)
local DinoStats = require(ReplicatedStorage.Shared.DinoStats)
local Format = require(ReplicatedStorage.Shared.Format)
local Plot = require(ReplicatedStorage.Shared.Config.Plot)

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
local GOOD_SPOT = Color3.fromRGB(90, 220, 110)
local BAD_SPOT = Color3.fromRGB(230, 70, 60)
local GHOST_TRANSPARENCY = 0.45
local NOTICE_TIME = 3 -- seconds a message from the server stays up
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

	-- Backpack dinos, best first, on keys 1-0. Sits just above the training display.
	local hotbar = Instance.new("Frame")
	hotbar.Name = "Hotbar"
	hotbar.AnchorPoint = Vector2.new(0.5, 1)
	hotbar.Position = UDim2.new(0.5, 0, 1, -110)
	hotbar.Size = UDim2.new(0.9, 0, 0, 74)
	hotbar.BackgroundTransparency = 1
	hotbar.Parent = gui
	local hotbarLimit = Instance.new("UISizeConstraint")
	hotbarLimit.MaxSize = Vector2.new(680, 74)
	hotbarLimit.Parent = hotbar
	local hotbarLayout = Instance.new("UIListLayout")
	hotbarLayout.FillDirection = Enum.FillDirection.Horizontal
	hotbarLayout.HorizontalAlignment = Enum.HorizontalAlignment.Center
	hotbarLayout.SortOrder = Enum.SortOrder.LayoutOrder
	hotbarLayout.Padding = UDim.new(0, 6)
	hotbarLayout.Parent = hotbar

	local slots = {}
	for index = 1, #HOTBAR_KEYS do
		local slot = Instance.new("TextButton")
		slot.Name = `Slot{index}`
		slot.LayoutOrder = index
		slot.Size = UDim2.new(0.1, -6, 1, 0)
		slot.BackgroundColor3 = PANEL
		slot.BackgroundTransparency = 0.15
		slot.AutoButtonColor = false
		slot.Text = ""
		slot.Parent = hotbar
		corner(slot, 10)
		local stroke = Instance.new("UIStroke")
		stroke.ApplyStrokeMode = Enum.ApplyStrokeMode.Border
		stroke.Color = TEXT
		stroke.Thickness = 3
		stroke.Enabled = false
		stroke.Parent = slot

		local income = makeLabel(slot, Enum.Font.GothamBlack, CASH, UDim2.fromOffset(4, 3), UDim2.new(1, -8, 0, 16))
		income.TextXAlignment = Enum.TextXAlignment.Center
		local swatch = Instance.new("Frame")
		swatch.AnchorPoint = Vector2.new(0.5, 0)
		swatch.Position = UDim2.new(0.5, 0, 0, 22)
		swatch.Size = UDim2.fromOffset(36, 36)
		swatch.Parent = slot
		corner(swatch, 8)
		local number = makeLabel(slot, Enum.Font.GothamBlack, TEXT, UDim2.new(0, 5, 1, -20), UDim2.fromOffset(16, 16))
		number.Text = tostring(index % 10)

		slots[index] = { button = slot, stroke = stroke, income = income, swatch = swatch }
	end

	local hint = makeLabel(gui, Enum.Font.GothamBlack, TEXT, UDim2.new(0.5, 0, 1, -190), UDim2.new(0.8, 0, 0, 28))
	hint.Name = "PlaceHint"
	hint.AnchorPoint = Vector2.new(0.5, 1)
	hint.TextXAlignment = Enum.TextXAlignment.Center
	hint.TextStrokeTransparency = 0.3
	hint.Visible = false

	-- Messages from the server, like "Plot upgraded!".
	local notice = makeLabel(gui, Enum.Font.GothamBlack, TAG, UDim2.new(0.5, 0, 1, -224), UDim2.new(0.8, 0, 0, 30))
	notice.Name = "Notice"
	notice.AnchorPoint = Vector2.new(0.5, 1)
	notice.TextXAlignment = Enum.TextXAlignment.Center
	notice.TextStrokeTransparency = 0.3
	notice.Visible = false

	return {
		hotbar = hotbar,
		slots = slots,
		hint = hint,
		notice = notice,
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

	local function send(action: string, key: number?, x: number?, z: number?)
		remotes.DinoAction:FireServer(action, key, x, z)
	end

	-- Backpack dinos in hotbar order (the list arrives best first).
	local function backpack()
		local list = {}
		for _, dino in dinos do
			if not dino.onPlot then
				table.insert(list, dino)
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
			slot.income.Text = if dino then `{Format.cash(dino.income)}/s` else ""
			slot.swatch.Visible = dino ~= nil
			if dino then
				slot.swatch.BackgroundColor3 = DinoModel.color(dino.name, dino.mutation)
			end
			slot.stroke.Enabled = dino ~= nil and dino.key == heldKey
			slot.button.BackgroundTransparency = if dino then 0.15 else 0.5
		end
	end

	local function equipSlot(index: number)
		local dino = backpack()[index]
		if dino then
			send("equip", dino.key)
		end
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

		local holding = dino.key == player:GetAttribute("HeldDino")
		local move = makeButton(
			row,
			if dino.onPlot then "PICK UP" elseif holding then "HOLDING" else "EQUIP",
			if dino.onPlot then PICK_UP else PLACE,
			UDim2.new(1, -222, 0, 18),
			UDim2.fromOffset(104, 48)
		)
		move.Name = "Move"
		move.Activated:Connect(function()
			if dino.onPlot then
				send("pickUp", dino.key)
			else
				-- Equipped: close the panel so the player can pick a spot on the plot.
				send("equip", dino.key)
				hud.panel.Visible = false
			end
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
		renderHotbar()
	end)
	local noticeToken = 0
	remotes.Notice.OnClientEvent:Connect(function(text: string, seconds: number?)
		noticeToken += 1
		local token = noticeToken
		hud.notice.Text = text
		hud.notice.Visible = true
		task.delay(seconds or NOTICE_TIME, function()
			if noticeToken == token then
				hud.notice.Visible = false
			end
		end)
	end)
	-- Training fills the bottom of the screen, so the hotbar steps aside.
	local function renderHotbarVisible()
		hud.hotbar.Visible = player:GetAttribute("IsTraining") ~= true
	end
	player:GetAttributeChangedSignal("IsTraining"):Connect(renderHotbarVisible)
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
		local model = DinoModel.build(dino.name, dino.mutation, Vector3.zero, DinoModel.statueScale(dino.size))
		model.Name = "PlacementGhost"
		for _, part in model:GetDescendants() do
			if part:IsA("BasePart") then
				part.Transparency = GHOST_TRANSPARENCY
			end
		end
		local highlight = Instance.new("Highlight")
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

	RunService.RenderStepped:Connect(function()
		local dino = heldDino()
		if not dino then
			clearGhost()
			aim = nil
			hud.hint.Visible = false
			return
		end
		local touch = UserInputService.TouchEnabled and not UserInputService.MouseEnabled
		local spot = spotAt(UserInputService:GetMouseLocation())
		local model = ghostFor(dino)
		local room = plotHasRoom()
		hud.hint.Visible = true
		if not player:GetAttribute("PlotIndex") then
			hud.hint.Text = "You don't have a plot in this server"
		elseif not room then
			hud.hint.Text = `Plot full ({slots}/{slots}): pick a dino up first`
		elseif not spot then
			hud.hint.Text = `Go to your plot to place {dino.name}`
		elseif not spot.inBounds then
			hud.hint.Text = "Too close to the edge"
		else
			hud.hint.Text = `{if touch then "Tap" else "Click"} to place {dino.name}`
		end
		if spot then
			local valid = spot.inBounds and room
			aim = { x = spot.x, z = spot.z, valid = valid }
			model:PivotTo(CFrame.new(Plot.positions[spot.plotIndex] + Vector3.new(spot.x, Plot.size.Y, spot.z)))
			model.Highlight.FillColor = if valid then GOOD_SPOT else BAD_SPOT
			model.Highlight.OutlineColor = if valid then GOOD_SPOT else BAD_SPOT
			model.Parent = workspace
		else
			aim = nil
			model.Parent = nil
		end
	end)

	UserInputService.InputBegan:Connect(function(input, gameProcessed)
		if gameProcessed then
			return
		end
		for index, keyCode in HOTBAR_KEYS do
			if input.KeyCode == keyCode then
				equipSlot(index)
				return
			end
		end
		local dino = heldDino()
		if not dino then
			return
		end
		local target = aim
		if input.UserInputType == Enum.UserInputType.Touch then
			-- Phones have no hover, so a tap both picks and places. Touch positions leave out
			-- the top bar, while the camera's ray needs the whole screen.
			local point = Vector2.new(input.Position.X, input.Position.Y) + GuiService:GetGuiInset()
			local spot = spotAt(point)
			target = spot and { x = spot.x, z = spot.z, valid = spot.inBounds and plotHasRoom() }
		elseif input.UserInputType ~= Enum.UserInputType.MouseButton1 then
			return
		end
		if target and target.valid then
			send("placeAt", dino.key, target.x, target.z)
		end
	end)
	player:GetAttributeChangedSignal("Cash"):Connect(renderCash)
	player:GetAttributeChangedSignal("Income"):Connect(renderCash)

	renderList()
	renderHotbar()
	renderCash()
end

return PlotController
