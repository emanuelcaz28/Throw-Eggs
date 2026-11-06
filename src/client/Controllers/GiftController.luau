-- The Gift panel (GIFT [Owner, 2026-11-05]), opened by the GIFT button in the Shop's header: pick a player in this
-- server, then something to buy them (Shared/Gifts). Display and requests only: the server checks the gift, shows the
-- purchase prompt and gives it to them. Built the first time it opens.
local MarketplaceService = game:GetService("MarketplaceService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Gifts = require(ReplicatedStorage.Shared.Gifts)
local UiKit = require(ReplicatedStorage.Shared.UiKit)

local player = Players.LocalPlayer

local GiftController = {}

local PANEL_SIZE = Vector2.new(780, 640)
local LIST_WIDTH = 728
local ROW_HEIGHT = 108

local ui -- { panel, list, hint, change }, once built
local receiver: Player? = nil -- who the items are for; nil while choosing a player
local connections: { RBXScriptConnection } = {} -- the shown rows' own, dropped when the list is redrawn
local prices: { [number]: number } = {} -- Robux price by product id, once Roblox has said

local function at(object: GuiObject, x: number, y: number, w: number, h: number)
	object.Position = UDim2.fromOffset(x, y)
	object.Size = UDim2.fromOffset(w, h)
	return object
end

local function clearList()
	for _, connection in connections do
		connection:Disconnect()
	end
	table.clear(connections)
	for _, child in ui.list:GetChildren() do
		if child:IsA("GuiObject") then
			child:Destroy()
		end
	end
end

local function row(order: number): Frame
	local frame = Instance.new("Frame")
	frame.Size = UDim2.fromOffset(LIST_WIDTH, ROW_HEIGHT)
	frame.BackgroundColor3 = UiKit.ROW
	frame.LayoutOrder = order
	frame.Parent = ui.list
	UiKit.corner(frame, 22)
	UiKit.stroke(frame, 4)
	return frame
end

local function rightButton(frame: Frame, text: string, style: string): TextButton
	local button = UiKit.button(frame, text, style, 176, 62, 28)
	button.AnchorPoint = Vector2.new(1, 0.5)
	button.Position = UDim2.new(1, -18, 0.5, 0)
	return button
end

local showItems

-- Step 1: everyone else in the server.
local function showPlayers()
	receiver = nil
	clearList()
	ui.change.Visible = false
	local others = {}
	for _, other in Players:GetPlayers() do
		if other ~= player then
			table.insert(others, other)
		end
	end
	table.sort(others, function(a, b)
		return a.DisplayName:lower() < b.DisplayName:lower()
	end)
	ui.hint.Text = if #others == 0 then "No one else is in this server yet." else "Who is it for?"
	for index, other in others do
		local frame = row(index)
		local face = Instance.new("ImageLabel")
		face.BackgroundColor3 = UiKit.DEEP
		at(face, 14, 12, 84, 84)
		face.Parent = frame
		UiKit.corner(face, 42)
		task.spawn(function()
			local ok, image = pcall(function()
				return Players:GetUserThumbnailAsync(other.UserId, Enum.ThumbnailType.HeadShot, Enum.ThumbnailSize.Size100x100)
			end)
			if ok then
				face.Image = image
			end
		end)
		at(UiKit.text(frame, other.DisplayName, 32, nil, Enum.TextXAlignment.Left), 116, 14, 400, 40)
		at(UiKit.muted(frame, `@{other.Name}`, 20, Enum.TextXAlignment.Left), 116, 58, 400, 26)
		rightButton(frame, "CHOOSE", "berry").Activated:Connect(function()
			showItems(other)
		end)
	end
end

-- Step 2: what can be bought for them, each with its price, or OWNED when they can only have one and have it.
function showItems(other: Player)
	receiver = other
	clearList()
	ui.change.Visible = true
	ui.hint.Text = `A gift for {other.DisplayName}`
	for index, item in Gifts.items do
		local frame = row(index)
		local picture = { spin = true, position = UDim2.fromOffset(10, 6), size = UDim2.fromOffset(140, 96) }
		if item.monster then
			picture.aspect = 140 / 96
			UiKit.monster(frame, item.monster, picture)
		else
			UiKit.art(frame, item.artKey, item.art, picture)
		end
		at(UiKit.text(frame, item.name, 32, nil, Enum.TextXAlignment.Left), 166, 0, 360, ROW_HEIGHT)
		local button = rightButton(frame, "SOON", "grey")
		local function owned(): boolean
			return item.ownedAttribute ~= nil and other:GetAttribute(item.ownedAttribute) == true
		end
		local function render()
			if owned() then
				UiKit.restyle(button, "OWNED", "grey")
			elseif prices[item.productId] then
				UiKit.restyle(button, `R$ {prices[item.productId]}`, "green")
			end
		end
		if item.productId ~= 0 and not prices[item.productId] then
			task.spawn(function()
				local ok, info = pcall(function()
					return MarketplaceService:GetProductInfo(item.productId, Enum.InfoType.Product)
				end)
				if ok and info.PriceInRobux then
					prices[item.productId] = info.PriceInRobux
					if button.Parent then
						render()
					end
				end
			end)
		end
		render()
		if item.ownedAttribute then
			table.insert(connections, other:GetAttributeChangedSignal(item.ownedAttribute):Connect(render))
		end
		button.Activated:Connect(function()
			if item.productId ~= 0 and not owned() then
				ui.remotes.Gift:FireServer(item.productId, other.UserId)
			end
		end)
	end
end

local function build()
	local gui = Instance.new("ScreenGui")
	gui.Name = "GiftHud"
	gui.ResetOnSpawn = false
	gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	gui.DisplayOrder = 5 -- above the Shop it opens from
	gui.Parent = player:WaitForChild("PlayerGui")

	local panel = UiKit.panel(gui, { name = "GiftPanel", width = PANEL_SIZE.X, height = PANEL_SIZE.Y, header = "berry", title = "Gift", icon = "🎁" })
	local hint = at(UiKit.text(panel.body, "", 28, nil, Enum.TextXAlignment.Left), 28, 10, 520, 44)
	local change = UiKit.button(panel.body, "CHANGE", "blue", 150, 48, 22)
	change.AnchorPoint = Vector2.new(1, 0)
	change.Position = UDim2.new(1, -24, 0, 8)
	change.Activated:Connect(showPlayers)
	local list = UiKit.scrollList(panel.body, UDim2.fromOffset(16, 64), UDim2.new(1, -24, 1, -76), 12)
	ui = { panel = panel, list = list, hint = hint, change = change, remotes = ReplicatedStorage:WaitForChild("ShopRemotes") }

	-- Keep the list true while it's open: a new player to choose, or the chosen one leaving.
	Players.PlayerAdded:Connect(function()
		if panel.frame.Visible and not receiver then
			showPlayers()
		end
	end)
	Players.PlayerRemoving:Connect(function(other)
		if panel.frame.Visible and (not receiver or other == receiver) then
			task.defer(showPlayers) -- after it has left the list
		end
	end)
end

-- Opens on choosing a player (closing the Shop: one panel at a time).
function GiftController.open()
	if not ui then
		build()
	end
	showPlayers()
	UiKit.openPanel(ui.panel)
end

return GiftController
