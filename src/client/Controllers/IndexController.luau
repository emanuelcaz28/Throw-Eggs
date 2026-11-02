-- The Dino Index panel: every dino by biome, with unseen ones hidden as "???".
-- Display only: the server decides what's been discovered.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Biomes = require(ReplicatedStorage.Shared.Config.Biomes)
local DinoModel = require(ReplicatedStorage.Shared.DinoModel)
local Dinos = require(ReplicatedStorage.Shared.Config.Dinos)
local Format = require(ReplicatedStorage.Shared.Format)
local HudStyle = require(ReplicatedStorage.Shared.HudStyle)
local Index = require(ReplicatedStorage.Shared.Config.Index)

local player = Players.LocalPlayer

local IndexController = {}

local PANEL = Color3.fromRGB(28, 30, 36)
local SECTION = Color3.fromRGB(58, 62, 72)
local TRACK = Color3.fromRGB(36, 38, 46)
local UNSEEN = Color3.fromRGB(36, 38, 46)
local INK = Color3.fromRGB(20, 22, 28)
local ACCENT = Color3.fromRGB(226, 142, 58)
local CLOSE = Color3.fromRGB(190, 70, 60)
local TEXT = Color3.new(1, 1, 1)
local MUTED = Color3.fromRGB(190, 195, 205)
local DONE = Color3.fromRGB(120, 235, 120)
local TAG = Color3.fromRGB(255, 214, 70)
local SECTION_HEIGHT = 186

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
	gui.Name = "IndexHud"
	gui.ResetOnSpawn = false
	gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	gui.DisplayOrder = 3 -- above the other panels
	gui.Parent = player:WaitForChild("PlayerGui")

	-- Left column, top of three: Index, Shop, Eggs.
	local open = HudStyle.iconButton(gui, "📖", "Index")
	open.AnchorPoint = Vector2.new(0, 0.5)
	open.Position = UDim2.new(0, 16, HudStyle.COLUMN_CENTER, -(HudStyle.BUTTON_SIZE + HudStyle.BUTTON_GAP) * HudStyle.scale())
	open.Name = "OpenIndex"

	local panel = Instance.new("Frame")
	panel.Name = "IndexPanel"
	panel.AnchorPoint = Vector2.new(0.5, 0.5)
	panel.Position = UDim2.fromScale(0.5, 0.5)
	panel.Size = UDim2.fromScale(0.9, 0.86)
	panel.BackgroundColor3 = PANEL
	panel.BackgroundTransparency = 0.06
	panel.Visible = false
	panel.Parent = gui
	corner(panel, 16)
	local panelLimit = Instance.new("UISizeConstraint")
	panelLimit.MaxSize = Vector2.new(640, 560)
	panelLimit.Parent = panel

	local title = makeLabel(panel, Enum.Font.GothamBlack, TEXT, UDim2.fromOffset(16, 12), UDim2.new(0.6, 0, 0, 32))
	title.Text = "Dino Index"
	title.TextXAlignment = Enum.TextXAlignment.Left
	local total = makeLabel(panel, Enum.Font.GothamBold, TAG, UDim2.fromOffset(16, 46), UDim2.new(0.6, 0, 0, 20))
	total.Name = "Total"
	total.TextXAlignment = Enum.TextXAlignment.Left

	local close = makeButton(panel, "X", CLOSE, UDim2.new(1, -60, 0, 14), UDim2.fromOffset(46, 46))
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
	list.ScrollingDirection = Enum.ScrollingDirection.Y
	list.Parent = panel
	local layout = Instance.new("UIListLayout")
	layout.Padding = UDim.new(0, 10)
	layout.SortOrder = Enum.SortOrder.LayoutOrder
	layout.Parent = list

	return { open = open, panel = panel, total = total, close = close, list = list }
end

local function rewardText(): string
	return `Complete: +{Index.cashBonusPerBiome * 100}% $/s, +{Index.luckBonusPerBiome * 100}% luck`
end

local function makeCell(parent: Instance, dino, seen: boolean, order: number)
	local cell = Instance.new("Frame")
	cell.Name = dino.id
	cell.LayoutOrder = order
	cell.BackgroundTransparency = 1
	cell.Size = UDim2.new(0.19, 0, 1, 0)
	cell.Parent = parent

	local swatch = Instance.new("Frame")
	swatch.Name = "Swatch"
	swatch.AnchorPoint = Vector2.new(0.5, 0)
	swatch.Position = UDim2.fromScale(0.5, 0)
	swatch.Size = UDim2.fromOffset(56, 56)
	swatch.BackgroundColor3 = if seen then DinoModel.color(dino.name, nil) else UNSEEN
	swatch.Parent = cell
	corner(swatch, 10)
	local stroke = Instance.new("UIStroke")
	stroke.Color = INK
	stroke.Thickness = 2
	stroke.Parent = swatch

	if not seen then
		local mark = makeLabel(swatch, Enum.Font.GothamBlack, MUTED, UDim2.fromScale(0.2, 0.2), UDim2.fromScale(0.6, 0.6))
		mark.Text = "?"
	end

	local name = makeLabel(cell, Enum.Font.GothamBold, TEXT, UDim2.fromOffset(0, 60), UDim2.new(1, 0, 0, 18))
	name.Name = "DinoName"
	name.Text = if seen then dino.name else "???"
	local odds = makeLabel(cell, Enum.Font.Gotham, MUTED, UDim2.fromOffset(0, 80), UDim2.new(1, 0, 0, 14))
	odds.Text = `1 in {Format.commas(dino.chance)}`
end

local function makeSection(list: Instance, biome, discovered, order: number): number
	local biomeDinos = Dinos[biome.id]
	local seenCount = 0
	for _, dino in biomeDinos do
		if discovered[dino.id] then
			seenCount += 1
		end
	end
	local complete = seenCount == #biomeDinos

	local section = Instance.new("Frame")
	section.Name = biome.id
	section.LayoutOrder = order
	section.BackgroundColor3 = SECTION
	section.Size = UDim2.new(1, -12, 0, SECTION_HEIGHT)
	section.Parent = list
	corner(section, 12)

	local name = makeLabel(section, Enum.Font.GothamBlack, biome.color:Lerp(TEXT, 0.45), UDim2.fromOffset(12, 8), UDim2.new(0.6, 0, 0, 24))
	name.Name = "BiomeName"
	name.Text = biome.name
	name.TextXAlignment = Enum.TextXAlignment.Left
	local count = makeLabel(section, Enum.Font.GothamBold, if complete then DONE else TEXT, UDim2.new(1, -92, 0, 10), UDim2.fromOffset(80, 20))
	count.Name = "Count"
	count.Text = `{seenCount} / {#biomeDinos}`
	count.TextXAlignment = Enum.TextXAlignment.Right

	local track = Instance.new("Frame")
	track.Position = UDim2.fromOffset(12, 36)
	track.Size = UDim2.new(1, -24, 0, 8)
	track.BackgroundColor3 = TRACK
	track.BorderSizePixel = 0
	track.Parent = section
	corner(track, 4)
	local fill = Instance.new("Frame")
	fill.Size = UDim2.fromScale(seenCount / #biomeDinos, 1)
	fill.BackgroundColor3 = if complete then DONE else biome.color:Lerp(TEXT, 0.2)
	fill.BorderSizePixel = 0
	fill.Parent = track
	corner(fill, 4)

	local reward = makeLabel(section, Enum.Font.GothamBold, if complete then DONE else MUTED, UDim2.fromOffset(12, 48), UDim2.new(1, -24, 0, 16))
	reward.Name = "Reward"
	reward.Text = rewardText()
	reward.TextXAlignment = Enum.TextXAlignment.Left

	local row = Instance.new("Frame")
	row.Name = "Dinos"
	row.BackgroundTransparency = 1
	row.Position = UDim2.fromOffset(8, 72)
	row.Size = UDim2.new(1, -16, 0, 104)
	row.Parent = section
	local layout = Instance.new("UIListLayout")
	layout.FillDirection = Enum.FillDirection.Horizontal
	layout.HorizontalAlignment = Enum.HorizontalAlignment.Center
	layout.Padding = UDim.new(0.01, 0)
	layout.SortOrder = Enum.SortOrder.LayoutOrder
	layout.Parent = row

	for dinoOrder, dino in biomeDinos do
		makeCell(row, dino, discovered[dino.id] == true, dinoOrder)
	end
	return seenCount
end

function IndexController.start()
	local remote = ReplicatedStorage:WaitForChild("IndexRemotes"):WaitForChild("IndexChanged")
	local hud = buildGui()

	local function render(discovered)
		for _, child in hud.list:GetChildren() do
			if child:IsA("Frame") then
				child:Destroy()
			end
		end
		local seen, total = 0, 0
		for order, biome in Biomes do
			seen += makeSection(hud.list, biome, discovered, order)
			total += #Dinos[biome.id]
		end
		hud.total.Text = `{seen} / {total} discovered`
	end

	hud.open.Activated:Connect(function()
		hud.panel.Visible = not hud.panel.Visible
	end)
	hud.close.Activated:Connect(function()
		hud.panel.Visible = false
	end)
	remote.OnClientEvent:Connect(render)
	render({})
end

return IndexController
