-- The Dino Index panel: one block per biome, with the biome's card (name and spinning island) on
-- the left and the dinos that live there on rarity tiles on the right. Unseen dinos show as black
-- silhouettes. Display only: the server decides what's been discovered.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Biomes = require(ReplicatedStorage.Shared.Config.Biomes)
local Dinos = require(ReplicatedStorage.Shared.Config.Dinos)
local Format = require(ReplicatedStorage.Shared.Format)
local HudStyle = require(ReplicatedStorage.Shared.HudStyle)
local Index = require(ReplicatedStorage.Shared.Config.Index)
local PopText = require(ReplicatedStorage.Shared.PopText)
local UiKit = require(ReplicatedStorage.Shared.UiKit)
local RevealController = require(script.Parent.RevealController)

local player = Players.LocalPlayer

local IndexController = {}

local PANEL_SIZE = Vector2.new(1060, 672)
local LIST_WIDTH = 1012
local CARD_SIZE = Vector2.new(250, 368)
local TILE_SIZE = Vector2.new(234, 150)
local TILE_GAP = 12
local TILES_PER_ROW = 3
-- Biome card colours; a biome missing here uses the sky gradient.
local CARD_COLOURS = {
	Forest = { "#4fe0ff", "#1aa6e0" },
	Desert = { "#ffc14d", "#ff7a2f" },
	Swamp = { "#8fe05a", "#2f9e6a" },
	Volcano = { "#ffb347", "#e8481c" },
	FrozenPeaks = { "#c8f2ff", "#4aa8e0" },
	ShadowBog = { "#c9a2ff", "#7a3fd6" },
	Abyss = { "#7ff0ff", "#1f6fb8" },
	StarfallCrater = { "#ffe27a", "#2e3a8c" },
	EclipseTemple = { "#7dffb8", "#7a3a3a" },
}

local function buildGui()
	local gui = Instance.new("ScreenGui")
	gui.Name = "IndexHud"
	gui.ResetOnSpawn = false
	gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	gui.DisplayOrder = 3 -- above the other panels
	gui.Parent = player:WaitForChild("PlayerGui")

	-- Left column, above Shop.
	local open = HudStyle.iconButton(gui, "📖", "Index", "book")
	open.AnchorPoint = Vector2.new(0, 0.5)
	open.Position = UDim2.new(0, 16, HudStyle.COLUMN_CENTER, -(HudStyle.BUTTON_SIZE + HudStyle.BUTTON_GAP) / 2 * HudStyle.scale())
	open.Name = "OpenIndex"

	local panel = UiKit.panel(gui, { name = "IndexPanel", width = PANEL_SIZE.X, height = PANEL_SIZE.Y, header = "berry", title = "Dino Index" })
	local list = UiKit.scrollList(panel.body, UDim2.fromOffset(24, 10), UDim2.new(1, -36, 1, -122), 18)

	-- Overall progress along the bottom, with the book poking out on the left.
	local bar = Instance.new("Frame")
	bar.AnchorPoint = Vector2.new(0, 1)
	bar.Position = UDim2.new(0, 92, 1, -20)
	bar.Size = UDim2.new(1, -122, 0, 72)
	bar.BackgroundColor3 = UiKit.DEEP
	bar.Parent = panel.body
	UiKit.corner(bar, 24)
	UiKit.stroke(bar, 4)
	local fill = Instance.new("Frame")
	fill.Size = UDim2.fromScale(0, 1)
	fill.Parent = bar
	UiKit.gradient(fill, "green")
	UiKit.corner(fill, 20)
	local total = UiKit.text(bar, "", 40)
	total.Size = UDim2.fromScale(1, 1)
	total.ZIndex = 2
	local book = UiKit.iconImage(panel.body, "book") or UiKit.text(panel.body, "📖", 84)
	book.AnchorPoint = Vector2.new(0, 1)
	book.Position = UDim2.new(0, 12, 1, -6)
	book.Size = UDim2.fromOffset(110, 100)
	book.Rotation = -12
	book.ZIndex = 3

	return { open = open, panel = panel, list = list, fill = fill, total = total }
end

local function progressBar(parent: Instance, done: number, count: number, width: number)
	local bar = Instance.new("Frame")
	bar.Size = UDim2.fromOffset(width, 44)
	bar.BackgroundColor3 = UiKit.DEEP
	bar.Parent = parent
	UiKit.corner(bar, 16)
	UiKit.stroke(bar, 4)
	local fill = Instance.new("Frame")
	fill.Size = UDim2.fromScale(done / count, 1)
	fill.Visible = done > 0
	fill.Parent = bar
	UiKit.gradient(fill, "green")
	UiKit.corner(fill, 12)
	local label = UiKit.text(bar, `{done}/{count}`, 28)
	label.Size = UDim2.fromScale(1, 1)
	label.ZIndex = 2
end

local function rewardTile(parent: Instance, complete: boolean)
	local tile = Instance.new("Frame")
	tile.LayoutOrder = math.huge -- after the dinos
	tile.Size = UDim2.fromOffset(TILE_SIZE.X, TILE_SIZE.Y)
	tile.Parent = parent
	UiKit.gradient(tile, { "#3a3060", "#2a2348" })
	UiKit.corner(tile, 20)
	UiKit.stroke(tile, 4)
	local title = UiKit.text(tile, if complete then "✓ COMPLETE!" else "COMPLETE REWARD", 19, UiKit.GOLD)
	title.Position = UDim2.fromOffset(0, 22)
	local cash = UiKit.text(tile, `+{math.round(Index.cashBonusPerBiome * 100)}% cash`, 24, UiKit.CASH)
	cash.Position = UDim2.fromOffset(0, 56)
	local luck = UiKit.text(tile, `+{math.round(Index.luckBonusPerBiome * 100)}% luck`, 24, UiKit.POWER)
	luck.Position = UDim2.fromOffset(0, 90)
end

local function biomeBlock(list: Instance, biome, discovered, order: number): (number, number)
	local dinos = Dinos[biome.id] or {}
	local block = Instance.new("Frame")
	block.BackgroundTransparency = 1
	block.LayoutOrder = order
	block.Size = UDim2.fromOffset(LIST_WIDTH - 20, CARD_SIZE.Y)
	block.Parent = list

	local card = Instance.new("Frame")
	card.Size = UDim2.fromOffset(CARD_SIZE.X, CARD_SIZE.Y)
	card.Parent = block
	UiKit.gradient(card, CARD_COLOURS[biome.id] or "sky")
	UiKit.corner(card, 26)
	UiKit.stroke(card, 5)
	local name = UiKit.text(card, biome.name, 42)
	name.Position = UDim2.fromOffset(0, 14)
	name.TextWrapped = true
	UiKit.viewport(card, `biome_{biome.id}`, { spin = true, position = UDim2.fromOffset(10, 90), size = UDim2.fromOffset(CARD_SIZE.X - 20, 250), zoom = 1.0 })

	local grid = Instance.new("Frame")
	grid.BackgroundTransparency = 1
	grid.Position = UDim2.fromOffset(CARD_SIZE.X + 16, 0)
	grid.Size = UDim2.new(1, -CARD_SIZE.X - 16, 1, 0)
	grid.Parent = block
	local layout = Instance.new("UIGridLayout")
	layout.CellSize = UDim2.fromOffset(TILE_SIZE.X, TILE_SIZE.Y)
	layout.CellPadding = UDim2.fromOffset(TILE_GAP, TILE_GAP)
	layout.SortOrder = Enum.SortOrder.LayoutOrder
	layout.Parent = grid

	local found = 0
	for index, dino in dinos do
		local seen = discovered[dino.id] == true
		if seen then
			found += 1
		end
		local tile = UiKit.dinoTile(grid, dino.id, dino.name, TILE_SIZE.X, TILE_SIZE.Y, {
			found = seen,
			nameSize = 21,
			bottom = if seen then `1 in {Format.commas(dino.chance)}` else nil,
		})
		tile.LayoutOrder = index
	end
	rewardTile(grid, found == #dinos and #dinos > 0)

	local barHolder = Instance.new("Frame")
	barHolder.BackgroundTransparency = 1
	local rows = math.ceil((#dinos + 1) / TILES_PER_ROW)
	barHolder.Position = UDim2.fromOffset(CARD_SIZE.X + 16, rows * (TILE_SIZE.Y + TILE_GAP))
	barHolder.Size = UDim2.fromOffset(TILES_PER_ROW * TILE_SIZE.X + (TILES_PER_ROW - 1) * TILE_GAP, 44)
	barHolder.Parent = block
	progressBar(barHolder, found, math.max(#dinos, 1), barHolder.Size.X.Offset)
	block.Size = UDim2.fromOffset(LIST_WIDTH - 20, math.max(CARD_SIZE.Y, rows * (TILE_SIZE.Y + TILE_GAP) + 48))
	card.Size = UDim2.fromOffset(CARD_SIZE.X, block.Size.Y.Offset)
	return found, #dinos
end

function IndexController.start()
	local remote = ReplicatedStorage:WaitForChild("IndexRemotes"):WaitForChild("IndexChanged")
	local hud = buildGui()
	local completed = {} -- biome ids with every dino caught
	local heardFromServer = false -- the first list is what they already had, so it shouts nothing

	-- Catching a biome's last dino shouts its reward, once the reveal of that dino is over.
	local function shoutCompleted(biome)
		task.spawn(function()
			while RevealController.isPlaying() do
				task.wait(0.25)
			end
			task.wait(1)
			PopText.shout(`{string.upper(biome.name)} COMPLETE!`, `+{math.round(Index.cashBonusPerBiome * 100)}% $/s and +{math.round(Index.luckBonusPerBiome * 100)}% luck, for good`)
		end)
	end

	local function render(discovered)
		for _, child in hud.list:GetChildren() do
			if child:IsA("Frame") then
				child:Destroy()
			end
		end
		local seen, total = 0, 0
		for order, biome in Biomes do
			if #(Dinos[biome.id] or {}) == 0 then
				continue -- no card for a world whose monsters aren't made yet
			end
			local found, count = biomeBlock(hud.list, biome, discovered, order)
			seen += found
			total += count
			if count > 0 and found == count and not completed[biome.id] then
				completed[biome.id] = true
				if heardFromServer then
					shoutCompleted(biome)
				end
			end
		end
		hud.total.Text = `Unlocked: {seen}/{total}`
		hud.fill.Size = UDim2.fromScale(if total > 0 then seen / total else 0, 1)
		hud.fill.Visible = seen > 0
	end

	hud.open.Activated:Connect(function()
		UiKit.togglePanel(hud.panel)
	end)
	remote.OnClientEvent:Connect(function(discovered)
		render(discovered)
		heardFromServer = true
	end)
	render({})
end

return IndexController
