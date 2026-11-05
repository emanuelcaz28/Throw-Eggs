-- The Dino Index panel, from Figma "Throw Eggs - Index & Inventory": every map as a tab down the left (its colours,
-- its number, how many of its monsters you've found, a tick when they all are; maps whose monsters aren't made yet
-- say COMING SOON), and the chosen map's monsters on the right, sorted by rarity from COMMON to its MYTHIC boss, each
-- on a rarity tile with its real model turning. Unseen monsters are black silhouettes named "???", their rarity and
-- odds still showing. Under them, what completing the map gives. Display only: the server decides what's been found.
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
local LIST = { x = 18, y = 10, width = 262, height = 556 } -- the map tabs, in the panel's body
local TAB_SIZE = Vector2.new(236, 62)
local RIGHT_X, RIGHT_WIDTH = 290, 752 -- the chosen map's banner, monsters and reward
local TILE_SIZE = Vector2.new(244, 190)
local TILE_GAP = Vector2.new(10, 12)
-- Map colours, top to bottom on its tab and left to right on its banner; a map missing here uses the sky gradient.
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
	ForbiddenLibrary = { "#c3a8ff", "#56392a" },
	MidnightCarnival = { "#ffd36b", "#b3263a" },
	ClockworkCitadel = { "#f0b85a", "#343844" },
	ThornKingdom = { "#ff6b88", "#344e3c" },
}

-- Text that shrinks to fit its box but never grows past its own size.
local function fitText(label: TextLabel, size: number)
	label.TextScaled = true
	local limit = Instance.new("UITextSizeConstraint")
	limit.MaxTextSize = size
	limit.Parent = label
end

local function frame(parent: Instance, name: string, x: number, y: number, width: number, height: number): Frame
	local f = Instance.new("Frame")
	f.Name = name
	f.Position = UDim2.fromOffset(x, y)
	f.Size = UDim2.fromOffset(width, height)
	f.BackgroundTransparency = 1
	f.Parent = parent
	return f
end

-- A dark bar with a green fill and "done / count" over it.
local function progressBar(parent: Instance, x: number, y: number, width: number, height: number, textSize: number)
	local bar = frame(parent, "Progress", x, y, width, height)
	bar.BackgroundTransparency = 0
	bar.BackgroundColor3 = UiKit.DEEP
	bar.ClipsDescendants = true
	UiKit.corner(bar, 16)
	UiKit.stroke(bar, 4)
	local fill = Instance.new("Frame")
	fill.Name = "Fill"
	fill.Size = UDim2.fromScale(0, 1)
	fill.Parent = bar
	UiKit.gradient(fill, "green")
	UiKit.corner(fill, 12)
	local label = UiKit.text(bar, "", textSize)
	label.Size = UDim2.fromScale(1, 1)
	label.ZIndex = 2
	return function(done: number, count: number, suffix: string?)
		fill.Size = UDim2.fromScale(if count > 0 then done / count else 0, 1)
		fill.Visible = done > 0
		label.Text = `{done} / {count}{suffix or ""}`
	end
end

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

	local panel = UiKit.panel(gui, { name = "IndexPanel", width = PANEL_SIZE.X, height = PANEL_SIZE.Y, header = "berry", title = "Dino Index", icon = "📖", iconKey = "book" })

	-- How many of every map's monsters you've found, in the header beside the close button.
	local totalHolder = frame(panel.frame, "TotalFound", 718, 19, 250, 50)
	totalHolder.ZIndex = 4
	local total = progressBar(totalHolder, 0, 0, 250, 50, 24)

	local tabs = Instance.new("ScrollingFrame")
	tabs.Name = "MapTabs"
	tabs.BackgroundTransparency = 1
	tabs.BorderSizePixel = 0
	tabs.Position = UDim2.fromOffset(LIST.x, LIST.y)
	tabs.Size = UDim2.fromOffset(LIST.width, LIST.height)
	tabs.AutomaticCanvasSize = Enum.AutomaticSize.Y
	tabs.CanvasSize = UDim2.new()
	tabs.ScrollBarThickness = 8
	tabs.ScrollBarImageColor3 = Color3.fromRGB(91, 74, 140)
	tabs.ScrollingDirection = Enum.ScrollingDirection.Y
	tabs.Parent = panel.body
	local layout = Instance.new("UIListLayout")
	layout.Padding = UDim.new(0, 10)
	layout.SortOrder = Enum.SortOrder.LayoutOrder
	layout.Parent = tabs
	local pad = Instance.new("UIPadding")
	pad.PaddingTop = UDim.new(0, 4)
	pad.PaddingLeft = UDim.new(0, 4)
	pad.PaddingBottom = UDim.new(0, 4)
	pad.Parent = tabs

	-- The chosen map's banner: its number and name, and how many of its monsters you've found.
	local banner = frame(panel.body, "MapBanner", RIGHT_X, LIST.y, RIGHT_WIDTH, 72)
	banner.BackgroundTransparency = 0
	banner.ClipsDescendants = true
	local bannerGradient = UiKit.gradient(banner, "sky", 0)
	UiKit.corner(banner, 22)
	UiKit.stroke(banner, 4)
	local mapNumber = UiKit.text(banner, "", 16, nil, Enum.TextXAlignment.Left)
	mapNumber.Position = UDim2.fromOffset(20, 4)
	local mapName = UiKit.text(banner, "", 36, nil, Enum.TextXAlignment.Left)
	mapName.Position = UDim2.fromOffset(20, 22)
	mapName.Size = UDim2.fromOffset(470, 44)
	local mapProgress = progressBar(banner, 506, 16, 230, 40, 24)

	local grid = frame(panel.body, "Monsters", RIGHT_X, LIST.y + 84, RIGHT_WIDTH, 2 * TILE_SIZE.Y + TILE_GAP.Y)
	local gridLayout = Instance.new("UIGridLayout")
	gridLayout.CellSize = UDim2.fromOffset(TILE_SIZE.X, TILE_SIZE.Y)
	gridLayout.CellPadding = UDim2.fromOffset(TILE_GAP.X, TILE_GAP.Y)
	gridLayout.SortOrder = Enum.SortOrder.LayoutOrder
	gridLayout.Parent = grid

	-- What completing the map gives, in coloured chips.
	local reward = frame(panel.body, "Reward", RIGHT_X, LIST.y + 84 + grid.Size.Y.Offset + 14, RIGHT_WIDTH, 62)
	reward.BackgroundTransparency = 0
	UiKit.gradient(reward, { "#3a3060", "#2a2348" })
	UiKit.corner(reward, 18)
	UiKit.stroke(reward, 4)
	local rewardTitle = UiKit.text(reward, "", 20, UiKit.GOLD, Enum.TextXAlignment.Left)
	rewardTitle.Position = UDim2.fromOffset(18, 0)
	rewardTitle.Size = UDim2.new(0, 220, 1, 0)
	local chips = frame(reward, "Chips", 0, 0, RIGHT_WIDTH - 14, 62)
	local chipLayout = Instance.new("UIListLayout")
	chipLayout.FillDirection = Enum.FillDirection.Horizontal
	chipLayout.HorizontalAlignment = Enum.HorizontalAlignment.Right
	chipLayout.VerticalAlignment = Enum.VerticalAlignment.Center
	chipLayout.Padding = UDim.new(0, 10)
	chipLayout.SortOrder = Enum.SortOrder.LayoutOrder
	chipLayout.Parent = chips
	for order, chip in {
		{ `+{math.round(Index.cashBonusPerBiome * 100)}% $/s`, "green" },
		{ `+{math.round(Index.luckBonusPerBiome * 100)}% luck`, "blue" },
		{ `x{Index.xpBoost.multiplier} XP for {math.round(Index.xpBoost.seconds / 60)} min`, "purple" },
	} do
		local tag = Instance.new("Frame")
		tag.LayoutOrder = order
		tag.AutomaticSize = Enum.AutomaticSize.X
		tag.Size = UDim2.fromOffset(0, 36)
		tag.Parent = chips
		UiKit.gradient(tag, chip[2])
		UiKit.corner(tag, 14)
		UiKit.stroke(tag, 3)
		local chipPad = Instance.new("UIPadding")
		chipPad.PaddingLeft = UDim.new(0, 12)
		chipPad.PaddingRight = UDim.new(0, 12)
		chipPad.Parent = tag
		local label = UiKit.text(tag, chip[1], 18)
		label.AutomaticSize = Enum.AutomaticSize.X
		label.Size = UDim2.fromScale(0, 1)
	end

	return {
		open = open,
		panel = panel,
		total = total,
		tabs = tabs,
		bannerGradient = bannerGradient,
		mapNumber = mapNumber,
		mapName = mapName,
		mapProgress = mapProgress,
		grid = grid,
		rewardTitle = rewardTitle,
	}
end

-- A map's monsters from most common to rarest, each with its rarity tier.
local function monstersOf(biome)
	local list = table.clone(Dinos[biome.id] or {})
	table.sort(list, function(a, b)
		return a.chance < b.chance
	end)
	return list
end

local function countFound(biome, discovered): (number, number)
	local found, count = 0, 0
	for _, dino in Dinos[biome.id] or {} do
		count += 1
		if discovered[dino.id] then
			found += 1
		end
	end
	return found, count
end

-- One map's tab: its colours, its number in a dark disc, its name, "4/6 found" and a tick once complete.
local function mapTab(parent: Instance, biome, number: number, found: number, count: number, selected: boolean): TextButton
	local soon = count == 0
	local tab = Instance.new("TextButton")
	tab.Name = biome.id
	tab.LayoutOrder = number
	tab.AutoButtonColor = false
	tab.Text = ""
	tab.Size = UDim2.fromOffset(TAB_SIZE.X, TAB_SIZE.Y)
	tab.Active = not soon
	tab.Parent = parent
	UiKit.gradient(tab, if soon then "dark" else (CARD_COLOURS[biome.id] or "sky"))
	UiKit.corner(tab, 18)
	UiKit.stroke(tab, 4, if selected then Color3.new(1, 1, 1) else nil)
	local disc = Instance.new("Frame")
	disc.Position = UDim2.fromOffset(10, 12)
	disc.Size = UDim2.fromOffset(38, 38)
	disc.BackgroundColor3 = UiKit.INK
	disc.BackgroundTransparency = 0.45
	disc.Parent = tab
	UiKit.corner(disc, 19)
	local digits = UiKit.text(disc, tostring(number), 18)
	digits.Size = UDim2.fromScale(1, 1)
	local name = UiKit.text(tab, biome.name, 17, nil, Enum.TextXAlignment.Left)
	name.Position = UDim2.fromOffset(58, 9)
	name.Size = UDim2.fromOffset(if found == count and not soon then 136 else 166, 22)
	fitText(name, 17)
	local progress = UiKit.text(tab, if soon then "COMING SOON" else `{found}/{count} found`, 14, if soon then UiKit.MUTED else nil, Enum.TextXAlignment.Left)
	progress.Position = UDim2.fromOffset(58, 32)
	progress.Size = UDim2.fromOffset(166, 18)
	if found == count and not soon then
		local tick = Instance.new("Frame")
		tick.Name = "Complete"
		tick.AnchorPoint = Vector2.new(1, 0.5)
		tick.Position = UDim2.new(1, -10, 0.5, 0)
		tick.Size = UDim2.fromOffset(26, 26)
		tick.Parent = tab
		UiKit.gradient(tick, "green")
		UiKit.corner(tick, 13)
		UiKit.stroke(tick, 2)
		local mark = UiKit.text(tick, "✓", 16)
		mark.Size = UDim2.fromScale(1, 1)
	end
	return tab
end

-- One monster's tile: rarity colour, its rarity in a pill, its odds, its real model turning, its name.
local function monsterTile(parent: Instance, dino, rarity: string, seen: boolean, order: number)
	local tile = Instance.new("Frame")
	tile.Name = dino.id
	tile.LayoutOrder = order
	tile.ClipsDescendants = true
	tile.Parent = parent
	UiKit.gradient(tile, if seen then rarity else "unseen")
	UiKit.corner(tile, 20)
	UiKit.stroke(tile, 4)
	local glow = Instance.new("Frame")
	glow.AnchorPoint = Vector2.new(0.5, 0.5)
	glow.Position = UDim2.fromScale(0.5, 0.48)
	glow.Size = UDim2.fromOffset(150, 110)
	glow.BackgroundColor3 = Color3.new(1, 1, 1)
	glow.BackgroundTransparency = if seen then 0.72 else 0.85
	glow.Parent = tile
	UiKit.corner(glow, 55)
	local view = UiKit.monster(tile, dino.id, {
		spin = seen,
		silhouette = not seen,
		position = UDim2.fromOffset(14, 26),
		size = UDim2.fromOffset(TILE_SIZE.X - 28, 136),
		aspect = (TILE_SIZE.X - 28) / 136,
	})
	view.ZIndex = 2
	-- The rarity pill: see-through dark on a found monster, in the rarity's colours on an unseen one.
	local pill = Instance.new("Frame")
	pill.Position = UDim2.fromOffset(10, 10)
	pill.AutomaticSize = Enum.AutomaticSize.X
	pill.Size = UDim2.fromOffset(0, 24)
	pill.BackgroundColor3 = UiKit.INK
	pill.BackgroundTransparency = if seen then 0.45 else 0
	pill.ZIndex = 3
	pill.Parent = tile
	UiKit.corner(pill, 10)
	if not seen then
		UiKit.gradient(pill, rarity)
		UiKit.stroke(pill, 3)
	end
	local pillPad = Instance.new("UIPadding")
	pillPad.PaddingLeft = UDim.new(0, 9)
	pillPad.PaddingRight = UDim.new(0, 9)
	pillPad.Parent = pill
	local rarityLabel = UiKit.text(pill, string.upper(rarity), 14)
	rarityLabel.AutomaticSize = Enum.AutomaticSize.X
	rarityLabel.Size = UDim2.fromScale(0, 1)
	rarityLabel.ZIndex = 3
	local odds = UiKit.text(tile, `1 in {Format.commas(dino.chance)}`, 15, nil, Enum.TextXAlignment.Right)
	odds.Position = UDim2.fromOffset(110, 11)
	odds.Size = UDim2.fromOffset(TILE_SIZE.X - 122, 20)
	odds.ZIndex = 3
	local name = UiKit.text(tile, if seen then dino.name else "???", 22)
	name.Position = UDim2.fromOffset(6, TILE_SIZE.Y - 38)
	name.Size = UDim2.fromOffset(TILE_SIZE.X - 12, 28)
	fitText(name, 22)
	name.ZIndex = 3
end

function IndexController.start()
	local remote = ReplicatedStorage:WaitForChild("IndexRemotes"):WaitForChild("IndexChanged")
	local hud = buildGui()
	local completed = {} -- biome ids with every dino caught
	local heardFromServer = false -- the first list is what they already had, so it shouts nothing
	local discovered = {}
	local chosen: string? = nil -- the map whose monsters show; nil until the first render picks one
	local picked = false -- whether the player chose a map themselves, so new catches don't move them off it
	local render

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

	-- The map whose monsters show first: the farthest one you've found anything in, so you see what you're hunting.
	local function defaultMap(): string
		local pick = Biomes[1].id
		for _, biome in Biomes do
			if countFound(biome, discovered) > 0 then
				pick = biome.id
			end
		end
		return pick
	end

	local function showMap(biome, number: number)
		for _, child in hud.grid:GetChildren() do
			if child:IsA("Frame") then
				child:Destroy()
			end
		end
		local pair = CARD_COLOURS[biome.id] or UiKit.GRADIENTS.sky
		hud.bannerGradient.Color = ColorSequence.new(Color3.fromHex(pair[1]), Color3.fromHex(pair[2]))
		hud.mapNumber.Text = `MAP {number}`
		hud.mapName.Text = biome.name
		local found, count = countFound(biome, discovered)
		hud.mapProgress(found, count)
		for order, dino in monstersOf(biome) do
			monsterTile(hud.grid, dino, UiKit.RARITY_ORDER[math.min(order, #UiKit.RARITY_ORDER)], discovered[dino.id] == true, order)
		end
		hud.rewardTitle.Text = if count > 0 and found == count then "✓ COMPLETE!" else "COMPLETE TO GET"
	end

	render = function()
		chosen = chosen or defaultMap()
		for _, child in hud.tabs:GetChildren() do
			if child:IsA("GuiButton") then
				child:Destroy()
			end
		end
		local seen, total = 0, 0
		for number, biome in Biomes do
			local found, count = countFound(biome, discovered)
			seen += found
			total += count
			local tab = mapTab(hud.tabs, biome, number, found, count, biome.id == chosen)
			if count > 0 then
				tab.Activated:Connect(function()
					picked = true
					if chosen ~= biome.id then
						chosen = biome.id
						render()
					end
				end)
				if biome.id == chosen then
					showMap(biome, number)
				end
				if found == count and not completed[biome.id] then
					completed[biome.id] = true
					if heardFromServer then
						shoutCompleted(biome)
					end
				end
			end
		end
		hud.total(seen, total, " found")
	end

	hud.open.Activated:Connect(function()
		UiKit.togglePanel(hud.panel)
	end)
	remote.OnClientEvent:Connect(function(newDiscovered)
		discovered = newDiscovered
		if not picked then
			chosen = defaultMap()
		end
		render()
		heardFromServer = true
	end)
	render()
end

return IndexController
