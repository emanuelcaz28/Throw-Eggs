-- The Egg Shop panel. Display and requests only: the server checks every purchase.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local Eggs = require(ReplicatedStorage.Shared.Config.Eggs)
local Format = require(ReplicatedStorage.Shared.Format)
local HudStyle = require(ReplicatedStorage.Shared.HudStyle)
local Hub = require(ReplicatedStorage.Shared.Config.Hub)

local player = Players.LocalPlayer

local EggShopController = {}

local INK = Color3.fromRGB(20, 22, 28)
local PANEL = Color3.fromRGB(28, 30, 36)
local CARD = Color3.fromRGB(58, 62, 72)
local ACCENT = Color3.fromRGB(226, 142, 58)
local BUY = Color3.fromRGB(90, 170, 80)
local EQUIP = Color3.fromRGB(70, 130, 210)
local EQUIPPED = Color3.fromRGB(110, 114, 124)
local TOO_POOR = Color3.fromRGB(150, 70, 62)
local CLOSE = Color3.fromRGB(190, 70, 60)
local TEXT = Color3.new(1, 1, 1)
local LUCK = Color3.fromRGB(120, 235, 120)
local CARD_WIDTH, CARD_HEIGHT = 140, 226

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
	gui.Name = "EggShopHud"
	gui.ResetOnSpawn = false
	gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	gui.DisplayOrder = 2 -- above the My Dinos panel
	gui.Parent = player:WaitForChild("PlayerGui")

	-- A shortcut; the Egg Shop stall in the hub opens it too.
	local open = HudStyle.iconButton(gui, "🥚", "Eggs")
	open.AnchorPoint = Vector2.new(0, 0.5)
	open.Position = UDim2.new(0, 16, HudStyle.COLUMN_CENTER, (HudStyle.BUTTON_SIZE + HudStyle.BUTTON_GAP) * HudStyle.scale())
	open.Name = "OpenShop"

	local panel = Instance.new("Frame")
	panel.Name = "ShopPanel"
	panel.AnchorPoint = Vector2.new(0.5, 0.5)
	panel.Position = UDim2.fromScale(0.5, 0.5)
	panel.Size = UDim2.new(0.9, 0, 0, CARD_HEIGHT + 96)
	panel.BackgroundColor3 = PANEL
	panel.BackgroundTransparency = 0.06
	panel.Visible = false
	panel.Parent = gui
	corner(panel, 16)
	local panelLimit = Instance.new("UISizeConstraint")
	panelLimit.MaxSize = Vector2.new(780, CARD_HEIGHT + 96)
	panelLimit.Parent = panel

	local title = makeLabel(panel, Enum.Font.GothamBlack, TEXT, UDim2.fromOffset(16, 14), UDim2.new(0.5, 0, 0, 32))
	title.Text = "Egg Shop"
	title.TextXAlignment = Enum.TextXAlignment.Left

	local close = makeButton(panel, "X", CLOSE, UDim2.new(1, -60, 0, 12), UDim2.fromOffset(46, 46))
	close.Name = "Close"

	local list = Instance.new("ScrollingFrame")
	list.Name = "List"
	list.BackgroundTransparency = 1
	list.BorderSizePixel = 0
	list.Position = UDim2.fromOffset(12, 68)
	list.Size = UDim2.new(1, -24, 0, CARD_HEIGHT + 16)
	list.AutomaticCanvasSize = Enum.AutomaticSize.X
	list.CanvasSize = UDim2.new()
	list.ScrollBarThickness = 6
	list.ScrollingDirection = Enum.ScrollingDirection.X
	list.Parent = panel
	local layout = Instance.new("UIListLayout")
	layout.FillDirection = Enum.FillDirection.Horizontal
	layout.Padding = UDim.new(0, 10)
	layout.SortOrder = Enum.SortOrder.LayoutOrder
	layout.Parent = list

	return { open = open, panel = panel, close = close, list = list }
end

-- Cards are kept and updated, not rebuilt, so cash ticking up can't eat a click.
local function buildCard(list: Instance, egg, order: number, onPressed: () -> ())
	local card = Instance.new("Frame")
	card.Name = egg.id
	card.LayoutOrder = order
	card.BackgroundColor3 = CARD
	card.Size = UDim2.fromOffset(CARD_WIDTH, CARD_HEIGHT)
	card.Parent = list
	corner(card, 12)

	local name = makeLabel(card, Enum.Font.GothamBlack, TEXT, UDim2.fromOffset(8, 8), UDim2.new(1, -16, 0, 22))
	name.Name = "EggName"
	name.Text = egg.name

	local icon = Instance.new("Frame")
	icon.Name = "Icon"
	icon.AnchorPoint = Vector2.new(0.5, 0)
	icon.Position = UDim2.new(0.5, 0, 0, 38)
	icon.Size = UDim2.fromOffset(72, 92)
	icon.BackgroundColor3 = egg.color
	icon.Parent = card
	local iconCorner = Instance.new("UICorner")
	iconCorner.CornerRadius = UDim.new(0.5, 0)
	iconCorner.Parent = icon
	local stroke = Instance.new("UIStroke")
	stroke.Color = INK
	stroke.Thickness = 3
	stroke.Parent = icon

	local luck = makeLabel(card, Enum.Font.GothamBold, LUCK, UDim2.fromOffset(8, 138), UDim2.new(1, -16, 0, 22))
	luck.Name = "Luck"
	luck.Text = `{egg.luckBonus}x luck`

	local button = makeButton(card, "", BUY, UDim2.fromOffset(8, 168), UDim2.new(1, -16, 0, 48))
	button.Name = "Action"
	button.Activated:Connect(onPressed)
	return button
end

function EggShopController.start()
	local remotes = ReplicatedStorage:WaitForChild("EggRemotes")
	local hud = buildGui()
	local owned = {}
	local equipped = nil
	local buttons = {}

	local function render()
		local cash = player:GetAttribute("Cash") or 0
		for _, egg in Eggs do
			local button = buttons[egg.id]
			if equipped == egg.id then
				button.Text = "EQUIPPED"
				button.BackgroundColor3 = EQUIPPED
			elseif owned[egg.id] then
				button.Text = "EQUIP"
				button.BackgroundColor3 = EQUIP
			else
				button.Text = Format.cash(egg.price)
				button.BackgroundColor3 = if cash >= egg.price then BUY else TOO_POOR
			end
		end
	end

	for order, egg in Eggs do
		buttons[egg.id] = buildCard(hud.list, egg, order, function()
			if owned[egg.id] then
				if equipped ~= egg.id then
					remotes.EggAction:FireServer("equip", egg.id)
				end
			elseif (player:GetAttribute("Cash") or 0) >= egg.price then
				remotes.EggAction:FireServer("buy", egg.id)
			end
		end)
	end

	hud.open.Activated:Connect(function()
		hud.panel.Visible = not hud.panel.Visible
	end)
	hud.close.Activated:Connect(function()
		hud.panel.Visible = false
	end)

	-- Stepping onto the Egg Shop stall's pad opens this panel; walking off closes it again.
	local onStallPad = false
	RunService.Heartbeat:Connect(function()
		local character = player.Character
		local root = character and character:FindFirstChild("HumanoidRootPart")
		local nowOnPad = root ~= nil and Hub.isOnPad(Hub.eggStall, root.Position)
		if nowOnPad ~= onStallPad then
			onStallPad = nowOnPad
			hud.panel.Visible = nowOnPad
		end
	end)
	remotes.EggsChanged.OnClientEvent:Connect(function(newOwned, newEquipped)
		owned = newOwned
		equipped = newEquipped
		render()
	end)
	player:GetAttributeChangedSignal("Cash"):Connect(render)
	render()
end

return EggShopController
