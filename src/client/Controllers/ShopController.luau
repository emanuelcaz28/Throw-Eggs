-- The Robux shop panel and the Server Luck timer. Display and prompts only: Roblox handles
-- the payment, and the server decides what it grants. Sections: Boosts (Server Luck), Passes
-- (x2 Cash, x2 Training) and Free (the starter dino).
local MarketplaceService = game:GetService("MarketplaceService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local HudStyle = require(ReplicatedStorage.Shared.HudStyle)
local Shop = require(ReplicatedStorage.Shared.Config.Shop)
local UiKit = require(ReplicatedStorage.Shared.UiKit)

local player = Players.LocalPlayer

local ShopController = {}

local PANEL_SIZE = Vector2.new(980, 672)
local LIST_WIDTH = 932

local function card(parent: Instance, width: number, height: number, colours, order: number): Frame
	local frame = Instance.new("Frame")
	frame.Size = UDim2.fromOffset(width, height)
	frame.LayoutOrder = order
	frame.Parent = parent
	UiKit.gradient(frame, colours, 20)
	UiKit.corner(frame, 26)
	UiKit.stroke(frame, 5)
	return frame
end

local function at(object: GuiObject, x: number, y: number, w: number?, h: number?)
	object.Position = UDim2.fromOffset(x, y)
	if w and h then
		object.Size = UDim2.fromOffset(w, h)
	end
	return object
end

local function buildGui()
	local gui = Instance.new("ScreenGui")
	gui.Name = "ShopHud"
	gui.ResetOnSpawn = false
	gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	gui.DisplayOrder = 4 -- above the other panels
	gui.Parent = player:WaitForChild("PlayerGui")

	local open = HudStyle.iconButton(gui, "🛍️", "Shop")
	open.AnchorPoint = Vector2.new(0, 0.5)
	open.Position = UDim2.new(0, 16, HudStyle.COLUMN_CENTER, (HudStyle.BUTTON_SIZE + HudStyle.BUTTON_GAP) / 2 * HudStyle.scale())
	open.Name = "OpenShop"

	local timer = UiKit.text(gui, "", 24, UiKit.CASH)
	timer.Name = "ServerLuckTimer"
	timer.AnchorPoint = Vector2.new(1, 0)
	timer.Position = UDim2.new(1, -16, 0, 16)
	timer.Size = UDim2.fromOffset(260, 46)
	timer.BackgroundColor3 = UiKit.PANEL
	timer.BackgroundTransparency = 0.05
	timer.Visible = false
	UiKit.corner(timer, 16)
	UiKit.stroke(timer, 4)

	local panel = UiKit.panel(gui, { name = "ShopPanel", width = PANEL_SIZE.X, height = PANEL_SIZE.Y, header = "sun", title = "Shop", icon = "🛍️" })
	local list = UiKit.scrollList(panel.body, UDim2.fromOffset(16, 4), UDim2.new(1, -24, 1, -16), 14)

	-- Boosts: Server Luck.
	UiKit.divider(list, "Boosts", LIST_WIDTH).LayoutOrder = 1
	local luck = card(list, LIST_WIDTH, 170, { "#9cf28f", "#2fbf5a" }, 2)
	-- Flat art faces the camera instead of spinning, so it never turns edge-on.
	UiKit.viewport(luck, "clover", { yaw = math.rad(72), position = UDim2.fromOffset(30, 6), size = UDim2.fromOffset(170, 160) })
	at(UiKit.text(luck, Shop.serverLuck.name, 36, nil, Enum.TextXAlignment.Left), 230, 18, 440, 44)
	at(UiKit.text(luck, Shop.serverLuck.description, 19, nil, Enum.TextXAlignment.Left), 230, 62, 460, 24)
	local multiplier = UiKit.text(luck, `x1 > x{Shop.serverLuck.multiplier}`, 46, UiKit.GOLD, Enum.TextXAlignment.Left)
	at(multiplier, 230, 96, 300, 56)
	local luckState = UiKit.text(luck, `+{Shop.serverLuck.seconds // 60} min`, 22, nil, Enum.TextXAlignment.Left)
	at(luckState, 450, 112, 220, 30)
	local luckButton = UiKit.button(luck, "SOON", "grey", 170, 64, 30)
	luckButton.AnchorPoint = Vector2.new(1, 0.5)
	luckButton.Position = UDim2.new(1, -24, 0.5, 0)

	-- Passes: x2 Cash and x2 Training, side by side.
	UiKit.divider(list, "Passes", LIST_WIDTH).LayoutOrder = 3
	local passes = Instance.new("Frame")
	passes.BackgroundTransparency = 1
	passes.LayoutOrder = 4
	passes.Size = UDim2.fromOffset(LIST_WIDTH, 210)
	passes.Parent = list
	local row = Instance.new("UIListLayout")
	row.FillDirection = Enum.FillDirection.Horizontal
	row.Padding = UDim.new(0, 16)
	row.SortOrder = Enum.SortOrder.LayoutOrder
	row.Parent = passes
	local function passCard(item, colours, art, order)
		local frame = card(passes, (LIST_WIDTH - 16) / 2, 204, colours, order)
		at(UiKit.text(frame, item.name, 32, nil, Enum.TextXAlignment.Left), 20, 12, 300, 40)
		UiKit.viewport(frame, art, { spin = art ~= "bolts_M", yaw = math.rad(72), position = UDim2.fromOffset(16, 52), size = UDim2.fromOffset(170, 140) })
		local tag = UiKit.tag(frame, `x{item.multiplier}`, "tagGold", 22)
		tag.Position = UDim2.fromOffset(130, 146)
		local desc = UiKit.text(frame, item.description, 22)
		desc.TextWrapped = true
		at(desc, 200, 56, 240, 62)
		local button = UiKit.button(frame, "SOON", "grey", 210, 58, 28)
		button.Position = UDim2.fromOffset(220, 128)
		return button
	end
	local cashButton = passCard(Shop.doubleCash, { "#7fd4ff", "#2f7fe6" }, "cash_L", 1)
	local trainingButton = passCard(Shop.doubleTraining, { "#d3a3ff", "#7b4dff" }, "bolts_M", 2)

	-- Free: the starter dino.
	UiKit.divider(list, "Free", LIST_WIDTH).LayoutOrder = 5
	local free = card(list, 680, 170, { "#7fe7ff", "#3f8cff" }, 6)
	local tile = UiKit.dinoTile(free, Shop.starterDino.id, "", 150, 134, { found = true })
	tile.Position = UDim2.fromOffset(16, 14)
	at(UiKit.text(free, "Free Dino!", 34, nil, Enum.TextXAlignment.Left), 190, 18, 300, 42)
	at(UiKit.text(free, Shop.starterDino.description, 20, nil, Enum.TextXAlignment.Left), 190, 64, 300, 26)
	local starterButton = UiKit.button(free, "CLAIM", "green", 160, 62, 30)
	starterButton.AnchorPoint = Vector2.new(1, 0.5)
	starterButton.Position = UDim2.new(1, -20, 0.5, 0)

	return {
		open = open,
		timer = timer,
		panel = panel,
		luckButton = luckButton,
		luckState = luckState,
		cashButton = cashButton,
		trainingButton = trainingButton,
		starterButton = starterButton,
	}
end

-- Shows the Robux price once Roblox tells us; items without an id stay "SOON".
local function showPrice(button: TextButton, id: number, infoType: Enum.InfoType)
	if id == 0 then
		return
	end
	task.spawn(function()
		local ok, info = pcall(function()
			return MarketplaceService:GetProductInfo(id, infoType)
		end)
		if ok and info.PriceInRobux and button.Text ~= "OWNED" then
			UiKit.restyle(button, `R$ {info.PriceInRobux}`, "green")
			UiKit.pulse(button)
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
	hud.trainingButton.Activated:Connect(function()
		if Shop.doubleTraining.passId ~= 0 and not player:GetAttribute("HasDoubleTraining") then
			MarketplaceService:PromptGamePassPurchase(player, Shop.doubleTraining.passId)
		end
	end)
	hud.luckButton.Activated:Connect(function()
		if Shop.serverLuck.productId ~= 0 then
			MarketplaceService:PromptProductPurchase(player, Shop.serverLuck.productId)
		end
	end)
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

	hud.open.Activated:Connect(function()
		UiKit.togglePanel(hud.panel)
	end)

	RunService.Heartbeat:Connect(function()
		local remaining = (ReplicatedStorage:GetAttribute("ServerLuckEndsAt") or 0) - workspace:GetServerTimeNow()
		local active = remaining > 0
		hud.timer.Visible = active
		if active then
			local clock = string.format("%d:%02d", remaining // 60, remaining % 60)
			hud.timer.Text = `🍀 LUCK x{Shop.serverLuck.multiplier}  {clock}`
			hud.luckState.Text = `Active · {clock} left`
		else
			hud.luckState.Text = `+{Shop.serverLuck.seconds // 60} min`
		end
	end)
end

return ShopController
