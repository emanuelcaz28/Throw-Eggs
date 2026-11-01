-- The Robux shop panel and the Server Luck timer. Display and prompts only: Roblox handles
-- the payment, and the server decides what it grants.
local MarketplaceService = game:GetService("MarketplaceService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local Shop = require(ReplicatedStorage.Shared.Config.Shop)

local player = Players.LocalPlayer

local ShopController = {}

local PANEL = Color3.fromRGB(28, 30, 36)
local ROW = Color3.fromRGB(58, 62, 72)
local GOLD = Color3.fromRGB(245, 180, 40)
local BUY = Color3.fromRGB(90, 170, 80)
local OFF = Color3.fromRGB(110, 114, 124)
local CLOSE = Color3.fromRGB(190, 70, 60)
local LUCK = Color3.fromRGB(120, 235, 120)
local TEXT = Color3.new(1, 1, 1)
local MUTED = Color3.fromRGB(190, 195, 205)
local ROW_HEIGHT = 76

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
	gui.Name = "ShopHud"
	gui.ResetOnSpawn = false
	gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	gui.DisplayOrder = 4 -- above the other panels
	gui.Parent = player:WaitForChild("PlayerGui")

	local open = makeButton(gui, "SHOP", GOLD, UDim2.new(0, 16, 0.5, 114), UDim2.fromOffset(190, 46))
	open.Name = "OpenShop"

	local timer = makeLabel(gui, Enum.Font.GothamBlack, LUCK, UDim2.new(1, -16, 0, 16), UDim2.fromOffset(240, 34))
	timer.Name = "ServerLuckTimer"
	timer.AnchorPoint = Vector2.new(1, 0)
	timer.BackgroundColor3 = PANEL
	timer.BackgroundTransparency = 0.12
	timer.TextXAlignment = Enum.TextXAlignment.Center
	timer.Visible = false
	corner(timer, 10)

	local panel = Instance.new("Frame")
	panel.Name = "ShopPanel"
	panel.AnchorPoint = Vector2.new(0.5, 0.5)
	panel.Position = UDim2.fromScale(0.5, 0.5)
	panel.Size = UDim2.fromScale(0.9, 0.86)
	panel.BackgroundColor3 = PANEL
	panel.BackgroundTransparency = 0.06
	panel.Visible = false
	panel.Parent = gui
	corner(panel, 16)
	local panelLimit = Instance.new("UISizeConstraint")
	panelLimit.MaxSize = Vector2.new(600, 430)
	panelLimit.Parent = panel

	local title = makeLabel(panel, Enum.Font.GothamBlack, TEXT, UDim2.fromOffset(16, 14), UDim2.new(0.6, 0, 0, 32))
	title.Text = "Shop"
	local close = makeButton(panel, "X", CLOSE, UDim2.new(1, -60, 0, 12), UDim2.fromOffset(46, 46))
	close.Name = "Close"

	local list = Instance.new("ScrollingFrame")
	list.Name = "List"
	list.BackgroundTransparency = 1
	list.BorderSizePixel = 0
	list.Position = UDim2.fromOffset(12, 68)
	list.Size = UDim2.new(1, -24, 1, -80)
	list.AutomaticCanvasSize = Enum.AutomaticSize.Y
	list.CanvasSize = UDim2.new()
	list.ScrollBarThickness = 8
	list.ScrollingDirection = Enum.ScrollingDirection.Y
	list.Parent = panel
	local layout = Instance.new("UIListLayout")
	layout.Padding = UDim.new(0, 8)
	layout.SortOrder = Enum.SortOrder.LayoutOrder
	layout.Parent = list

	return { open = open, timer = timer, panel = panel, close = close, list = list }
end

local function makeRow(list: Instance, name: string, item, order: number): TextButton
	local row = Instance.new("Frame")
	row.Name = name
	row.LayoutOrder = order
	row.BackgroundColor3 = ROW
	row.Size = UDim2.new(1, -10, 0, ROW_HEIGHT)
	row.Parent = list
	corner(row, 12)

	local title = makeLabel(row, Enum.Font.GothamBlack, TEXT, UDim2.fromOffset(12, 10), UDim2.new(1, -150, 0, 26))
	title.Text = item.name
	local description = makeLabel(row, Enum.Font.GothamBold, MUTED, UDim2.fromOffset(12, 42), UDim2.new(1, -150, 0, 18))
	description.Text = item.description

	local button = makeButton(row, "SOON", OFF, UDim2.new(1, -128, 0, 14), UDim2.fromOffset(116, 48))
	button.Name = "Action"
	return button
end

local function showPrice(button: TextButton, id: number, infoType: Enum.InfoType)
	if id == 0 then
		return
	end
	task.spawn(function()
		local ok, info = pcall(function()
			return MarketplaceService:GetProductInfo(id, infoType)
		end)
		if ok and info.PriceInRobux and button.Text ~= "OWNED" then
			button.Text = `R$ {info.PriceInRobux}`
			button.BackgroundColor3 = BUY
		end
	end)
end

function ShopController.start()
	local remotes = ReplicatedStorage:WaitForChild("ShopRemotes")
	local hud = buildGui()

	local cashButton = makeRow(hud.list, "DoubleCash", Shop.doubleCash, 2)
	local trainingButton = makeRow(hud.list, "DoubleTraining", Shop.doubleTraining, 3)
	local luckButton = makeRow(hud.list, "ServerLuck", Shop.serverLuck, 4)
	local starterButton = makeRow(hud.list, "Starter", Shop.starterDino, 1)
	starterButton.Text = "FREE"
	starterButton.BackgroundColor3 = BUY

	local claimed = false

	local function renderPass(button: TextButton, attribute: string)
		if player:GetAttribute(attribute) then
			button.Text = "OWNED"
			button.BackgroundColor3 = OFF
		end
	end

	cashButton.Activated:Connect(function()
		if Shop.doubleCash.passId ~= 0 and not player:GetAttribute("HasDoubleCash") then
			MarketplaceService:PromptGamePassPurchase(player, Shop.doubleCash.passId)
		end
	end)
	trainingButton.Activated:Connect(function()
		if Shop.doubleTraining.passId ~= 0 and not player:GetAttribute("HasDoubleTraining") then
			MarketplaceService:PromptGamePassPurchase(player, Shop.doubleTraining.passId)
		end
	end)
	luckButton.Activated:Connect(function()
		if Shop.serverLuck.productId ~= 0 then
			MarketplaceService:PromptProductPurchase(player, Shop.serverLuck.productId)
		end
	end)
	starterButton.Activated:Connect(function()
		if not claimed then
			remotes.ClaimStarter:FireServer()
		end
	end)
	remotes.StarterClaimed.OnClientEvent:Connect(function(isClaimed: boolean)
		claimed = isClaimed
		if claimed then
			starterButton.Text = "CLAIMED"
			starterButton.BackgroundColor3 = OFF
		end
	end)

	showPrice(cashButton, Shop.doubleCash.passId, Enum.InfoType.GamePass)
	showPrice(trainingButton, Shop.doubleTraining.passId, Enum.InfoType.GamePass)
	showPrice(luckButton, Shop.serverLuck.productId, Enum.InfoType.Product)
	player:GetAttributeChangedSignal("HasDoubleCash"):Connect(function()
		renderPass(cashButton, "HasDoubleCash")
	end)
	player:GetAttributeChangedSignal("HasDoubleTraining"):Connect(function()
		renderPass(trainingButton, "HasDoubleTraining")
	end)
	renderPass(cashButton, "HasDoubleCash")
	renderPass(trainingButton, "HasDoubleTraining")

	hud.open.Activated:Connect(function()
		hud.panel.Visible = not hud.panel.Visible
	end)
	hud.close.Activated:Connect(function()
		hud.panel.Visible = false
	end)

	RunService.Heartbeat:Connect(function()
		local remaining = (ReplicatedStorage:GetAttribute("ServerLuckEndsAt") or 0) - workspace:GetServerTimeNow()
		hud.timer.Visible = remaining > 0
		if remaining > 0 then
			hud.timer.Text = string.format("LUCK x%d  %d:%02d", Shop.serverLuck.multiplier, remaining // 60, remaining % 60)
		end
	end)
end

return ShopController
