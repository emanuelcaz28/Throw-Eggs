-- The Egg Shop panel, opened by the Egg Shop stall at the player's own base. The stall is built
-- here on the client, so only the base's owner sees it (Config/Hub). One card per egg tier with the
-- egg spinning on a glow, its luck bonus and a buy / equip button. Display and requests only: the
-- server checks every purchase.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local Eggs = require(ReplicatedStorage.Shared.Config.Eggs)
local Format = require(ReplicatedStorage.Shared.Format)
local Hub = require(ReplicatedStorage.Shared.Config.Hub)
local Stall = require(ReplicatedStorage.Shared.Stall)
local UiKit = require(ReplicatedStorage.Shared.UiKit)

local player = Players.LocalPlayer

local EggShopController = {}

local CARD_SIZE = Vector2.new(176, 380)
local CARD_GAP = 16
local VISIBLE_CARDS = 5
-- Card colours and rarity words by tier; later tiers reuse the last one.
local TIERS = {
	{ "Common", { "#f6ead2", "#d9bf91" } },
	{ "Uncommon", { "#d8f8e4", "#5cc98a" } },
	{ "Rare", { "#fff3b8", "#ffb81f" } },
	{ "Epic", { "#ffd3c2", "#ff6a3d" } },
	{ "Legendary", { "#e4d2ff", "#8a5cff" } },
}

local function buildGui()
	local gui = Instance.new("ScreenGui")
	gui.Name = "EggShopHud"
	gui.ResetOnSpawn = false
	gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	gui.DisplayOrder = 2 -- above the My Dinos panel
	gui.Parent = player:WaitForChild("PlayerGui")

	-- Five cards show at once; with more eggs (one per map) the row scrolls sideways.
	local shown = math.min(#Eggs, VISIBLE_CARDS)
	local width = shown * CARD_SIZE.X + (shown - 1) * CARD_GAP + 60
	local panel = UiKit.panel(gui, { name = "ShopPanel", width = math.max(width, 600), height = 560, header = "sky", title = "Egg Shop", icon = "🥚", iconKey = "egg" })
	local row = Instance.new("ScrollingFrame")
	row.BackgroundTransparency = 1
	row.BorderSizePixel = 0
	row.Position = UDim2.fromOffset(30, 20)
	row.Size = UDim2.new(1, -60, 0, CARD_SIZE.Y + 16)
	row.CanvasSize = UDim2.new()
	row.AutomaticCanvasSize = Enum.AutomaticSize.X
	row.ScrollingDirection = Enum.ScrollingDirection.X
	row.ScrollBarThickness = 8
	row.Parent = panel.body
	local layout = Instance.new("UIListLayout")
	layout.FillDirection = Enum.FillDirection.Horizontal
	layout.Padding = UDim.new(0, CARD_GAP)
	layout.SortOrder = Enum.SortOrder.LayoutOrder
	layout.Parent = row
	local hint = UiKit.muted(panel.body, "Better eggs multiply the luck of every throw", 18)
	hint.AnchorPoint = Vector2.new(0, 1)
	hint.Position = UDim2.new(0, 0, 1, -10)
	return { panel = panel, row = row }
end

-- Cards are kept and updated, not rebuilt, so cash ticking up can't eat a click.
local function buildCard(row: Instance, egg, order: number, onPressed: () -> ())
	local tier = TIERS[math.min(order, #TIERS)]
	local card = Instance.new("Frame")
	card.Name = egg.id
	card.LayoutOrder = order
	card.Size = UDim2.fromOffset(CARD_SIZE.X, CARD_SIZE.Y)
	card.Parent = row
	UiKit.gradient(card, tier[2])
	UiKit.corner(card, 24)
	UiKit.stroke(card, 5)

	local name = UiKit.text(card, egg.name, 25)
	name.Position = UDim2.fromOffset(0, 12)
	local rarity = UiKit.text(card, tier[1], 18, UiKit.GOLD)
	rarity.Position = UDim2.fromOffset(0, 44)

	local glow = Instance.new("Frame")
	glow.AnchorPoint = Vector2.new(0.5, 0.5)
	glow.Position = UDim2.fromOffset(CARD_SIZE.X / 2, 160)
	glow.Size = UDim2.fromOffset(140, 140)
	glow.BackgroundColor3 = Color3.new(1, 1, 1)
	glow.BackgroundTransparency = 0.55
	glow.Parent = card
	UiKit.corner(glow, 70)
	UiKit.viewport(card, `egg_{egg.id}`, { spin = true, position = UDim2.fromOffset(8, 76), size = UDim2.fromOffset(CARD_SIZE.X - 16, 170), zoom = 1.0 })

	local pill = Instance.new("Frame")
	pill.AnchorPoint = Vector2.new(0.5, 0)
	pill.Position = UDim2.fromOffset(CARD_SIZE.X / 2, 254)
	pill.Size = UDim2.fromOffset(140, 32)
	pill.BackgroundColor3 = UiKit.INK
	pill.Parent = card
	UiKit.corner(pill, 12)
	local luck = UiKit.text(pill, `LUCK x{egg.luckBonus}`, 19, UiKit.CASH)
	luck.Size = UDim2.fromScale(1, 1)

	local button = UiKit.button(card, "", "green", 150, 54, 26)
	button.Name = "Action"
	button.AnchorPoint = Vector2.new(0.5, 1)
	button.Position = UDim2.new(0.5, 0, 1, -16)
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
				UiKit.restyle(button, "✓ EQUIPPED", "grey")
				button.TextSize = 20
			elseif owned[egg.id] then
				UiKit.restyle(button, "EQUIP", "blue")
				button.TextSize = 26
			else
				UiKit.restyle(button, Format.cash(egg.price), if cash >= egg.price then "green" else "red")
				button.TextSize = 26
			end
		end
	end

	for order, egg in Eggs do
		buttons[egg.id] = buildCard(hud.row, egg, order, function()
			if owned[egg.id] then
				if equipped ~= egg.id then
					remotes.EggAction:FireServer("equip", egg.id)
				end
			elseif (player:GetAttribute("Cash") or 0) >= egg.price then
				remotes.EggAction:FireServer("buy", egg.id)
			end
		end)
	end

	-- The stall stands at the player's own base, and moves with it if the base changes.
	local stall: Model? = nil
	local stallCFrame: CFrame? = nil
	local function placeStall()
		if stall then
			stall:Destroy()
			stall, stallCFrame = nil, nil
		end
		local plotIndex = player:GetAttribute("PlotIndex")
		if plotIndex then
			stallCFrame = Hub.stallCFrame(Hub.eggStall, plotIndex)
			stall = Stall.build("MyEggStall", Hub.eggStall, stallCFrame)
			stall.Parent = workspace
		end
	end
	player:GetAttributeChangedSignal("PlotIndex"):Connect(placeStall)
	placeStall()

	-- Stepping onto the Egg Shop stall's pad opens this panel; walking off closes it again.
	local onStallPad = false
	RunService.Heartbeat:Connect(function()
		local character = player.Character
		local root = character and character:FindFirstChild("HumanoidRootPart")
		local nowOnPad = root ~= nil and stallCFrame ~= nil and Hub.isOnPad(stallCFrame, root.Position)
		if nowOnPad ~= onStallPad then
			onStallPad = nowOnPad
			if nowOnPad then
				UiKit.openPanel(hud.panel)
			else
				UiKit.closePanel(hud.panel)
			end
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
