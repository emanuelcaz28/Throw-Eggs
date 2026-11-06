-- The Dino Index panel, from Figma "Throw Eggs - Index & Inventory" (Index v2): one long scrolling list of every map,
-- its picture on a card against the panel's left edge and its monsters beside it in rows of four, sorted by rarity
-- from COMMON up, each on a rarity tile with its real model turning. Unseen monsters are black silhouettes named "???",
-- their rarity and odds still showing. Only the maps near the screen hold live models, so phones aren't drawing all
-- of them at once. Display only: the server decides what's been found.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Biomes = require(ReplicatedStorage.Shared.Config.Biomes)
local Dinos = require(ReplicatedStorage.Shared.Config.Dinos)
local DinoStats = require(ReplicatedStorage.Shared.DinoStats)
local Format = require(ReplicatedStorage.Shared.Format)
local HudStyle = require(ReplicatedStorage.Shared.HudStyle)
local Index = require(ReplicatedStorage.Shared.Config.Index)
local PopText = require(ReplicatedStorage.Shared.PopText)
local UiKit = require(ReplicatedStorage.Shared.UiKit)
local RevealController = require(script.Parent.RevealController)

local player = Players.LocalPlayer

local IndexController = {}

local PANEL_SIZE = Vector2.new(1060, 672)
local LIST = { x = 4, y = 10, width = 1040, height = 556 } -- the scrolling list, in the panel's body
local CARD_SIZE = Vector2.new(310, 272) -- a map's card, as much of it as shows
local CARD_TUCK = 26 -- the card starts this far off the list's left edge, which hides its rounded left corners
local TILE_SIZE = Vector2.new(168, 131)
local TILE_GAP = 10
local TILE_COLUMNS = 4
local TILES_X = CARD_SIZE.X + 12
local MAP_PITCH = CARD_SIZE.Y + 20 -- from one map's top to the next
local LIVE_MARGIN = 120 -- how far off the list's edges a map still gets its live models

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
local function progressBar(parent: Instance, x: number, y: number, width: number, height: number, textSize: number, colours)
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
	UiKit.gradient(fill, colours or "green")
	UiKit.corner(fill, 12)
	local label = UiKit.text(bar, "", textSize)
	label.Size = UDim2.fromScale(1, 1)
	label.ZIndex = 2
	return function(done: number, count: number, text: string)
		fill.Size = UDim2.fromScale(if count > 0 then done / count else 0, 1)
		fill.Visible = done > 0
		label.Text = text
	end
end

-- A rounded tag round a line of text, as wide as its text. colours is left out for a caller that colours it itself.
local function chip(parent: Instance, text: string, textSize: number, height: number, colours, textColor: Color3?): Frame
	local tag = Instance.new("Frame")
	tag.AutomaticSize = Enum.AutomaticSize.X
	tag.Size = UDim2.fromOffset(0, height)
	tag.Parent = parent
	if colours then
		UiKit.gradient(tag, colours)
	end
	UiKit.corner(tag, 10)
	UiKit.stroke(tag, 3)
	local pad = Instance.new("UIPadding")
	pad.PaddingLeft = UDim.new(0, 10)
	pad.PaddingRight = UDim.new(0, 10)
	pad.Parent = tag
	local label = UiKit.text(tag, text, textSize, textColor)
	label.AutomaticSize = Enum.AutomaticSize.X
	label.Size = UDim2.fromScale(0, 1)
	return tag
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
	local totalHolder = frame(panel.frame, "TotalFound", PANEL_SIZE.X - panel.closeInset - 18 - 250, 19, 250, 50)
	totalHolder.ZIndex = 4
	local total = progressBar(totalHolder, 0, 0, 250, 50, 24)

	local list = Instance.new("ScrollingFrame")
	list.Name = "Maps"
	list.BackgroundTransparency = 1
	list.BorderSizePixel = 0
	list.Position = UDim2.fromOffset(LIST.x, LIST.y)
	list.Size = UDim2.fromOffset(LIST.width, LIST.height)
	list.CanvasSize = UDim2.fromOffset(0, #Biomes * MAP_PITCH - (MAP_PITCH - CARD_SIZE.Y))
	list.ScrollBarThickness = 8
	list.ScrollBarImageColor3 = Color3.fromRGB(91, 74, 140)
	list.ScrollingDirection = Enum.ScrollingDirection.Y
	list.Parent = panel.body

	return { open = open, panel = panel, total = total, list = list }
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

-- A map's card: its picture, its number, name and how many of its monsters you've found, and what completing it gives.
local function mapCard(parent: Instance, biome, number: number, found: number, count: number)
	local done = count > 0 and found == count
	local card = Instance.new("ImageLabel")
	card.Name = "MapCard"
	card.BackgroundColor3 = UiKit.DEEP
	card.Image = Index.mapPictures[biome.id] or ""
	card.ScaleType = Enum.ScaleType.Crop
	card.Position = UDim2.fromOffset(-CARD_TUCK, 0)
	card.Size = UDim2.fromOffset(CARD_SIZE.X + CARD_TUCK, CARD_SIZE.Y)
	card.Parent = parent
	UiKit.corner(card, 22)
	UiKit.stroke(card, 4)

	-- Darkens the top a little for the map's number and the bottom a lot for its name.
	local shade = frame(card, "Shade", 0, 0, 0, 0)
	shade.Size = UDim2.fromScale(1, 1)
	shade.BackgroundTransparency = 0
	shade.BackgroundColor3 = UiKit.INK
	UiKit.corner(shade, 22)
	local fade = Instance.new("UIGradient")
	fade.Rotation = 90
	fade.Transparency = NumberSequence.new({
		NumberSequenceKeypoint.new(0, 0.7),
		NumberSequenceKeypoint.new(0.3, 1),
		NumberSequenceKeypoint.new(0.5, 0.75),
		NumberSequenceKeypoint.new(0.72, 0.12),
		NumberSequenceKeypoint.new(1, 0.04),
	})
	fade.Parent = shade

	local edge = frame(card, "MapColourEdge", 4, 4, 0, 0)
	edge.Size = UDim2.new(1, -8, 1, -8)
	UiKit.corner(edge, 18)
	UiKit.stroke(edge, 3, biome.color)

	local left = CARD_TUCK + 18
	local mapChip = chip(card, `MAP {number}`, 18, 30, nil)
	mapChip.BackgroundColor3 = biome.color
	mapChip.Position = UDim2.fromOffset(CARD_TUCK + 16, 16)

	local name = UiKit.text(card, biome.name, 30, nil, Enum.TextXAlignment.Left)
	name.Position = UDim2.fromOffset(left, 140)
	name.Size = UDim2.fromOffset(CARD_SIZE.X - 26, 36)
	fitText(name, 30)

	local bar = progressBar(card, left, 184, 270, 32, 18, if done then { "#ffe666", "#faa81a" } else nil)
	bar(found, count, if done then "COMPLETE!" elseif count == 0 then "COMING SOON" else `{found} / {count} found`)

	local reward = frame(card, "Reward", left, 225, 270, 30)
	local row = Instance.new("UIListLayout")
	row.FillDirection = Enum.FillDirection.Horizontal
	row.VerticalAlignment = Enum.VerticalAlignment.Center
	row.Padding = UDim.new(0, 8)
	row.SortOrder = Enum.SortOrder.LayoutOrder
	row.Parent = reward
	local title = UiKit.text(reward, if done then "EARNED ✓" else "REWARD", 15, if done then Color3.fromRGB(140, 242, 92) else UiKit.GOLD)
	title.AutomaticSize = Enum.AutomaticSize.X
	title.Size = UDim2.fromScale(0, 1)
	title.LayoutOrder = 1
	local xp = `x{Index.xpBoost.multiplier} XP for {math.round(Index.xpBoost.seconds / 60)} min`
	local tag = chip(reward, xp, 14, 28, if done then { "#5a4a8c", "#463a70" } else "purple", if done then UiKit.MUTED else nil)
	tag.LayoutOrder = 2
end

-- One monster's tile: rarity colour, its rarity in a pill, its odds and its name. Its model comes and goes with
-- showModels, while it's near the screen.
local function monsterTile(parent: Instance, dino, rarity: string, seen: boolean, order: number)
	local tile = Instance.new("Frame")
	tile.Name = dino.id
	tile.ClipsDescendants = true
	tile.Position = UDim2.fromOffset(
		TILES_X + ((order - 1) % TILE_COLUMNS) * (TILE_SIZE.X + TILE_GAP),
		((order - 1) // TILE_COLUMNS) * (TILE_SIZE.Y + TILE_GAP)
	)
	tile.Size = UDim2.fromOffset(TILE_SIZE.X, TILE_SIZE.Y)
	tile.Parent = parent
	UiKit.gradient(tile, if seen then rarity else "unseen")
	UiKit.corner(tile, 14)
	UiKit.stroke(tile, 3)
	local glow = Instance.new("Frame")
	glow.AnchorPoint = Vector2.new(0.5, 0.5)
	glow.Position = UDim2.fromScale(0.5, 0.5)
	glow.Size = UDim2.fromOffset(104, 76)
	glow.BackgroundColor3 = Color3.new(1, 1, 1)
	glow.BackgroundTransparency = if seen then 0.72 else 0.85
	glow.Parent = tile
	UiKit.corner(glow, 38)
	-- The rarity pill: see-through dark on a found monster, in the rarity's colours on an unseen one.
	local pill = Instance.new("Frame")
	pill.Position = UDim2.fromOffset(7, 7)
	pill.AutomaticSize = Enum.AutomaticSize.X
	pill.Size = UDim2.fromOffset(0, 20)
	pill.BackgroundColor3 = UiKit.INK
	pill.BackgroundTransparency = if seen then 0.45 else 0
	pill.ZIndex = 3
	pill.Parent = tile
	UiKit.corner(pill, 8)
	if not seen then
		local pair = UiKit.RARITY[rarity]
		pill.BackgroundColor3 = Color3.fromHex(pair[2]):Lerp(Color3.new(0, 0, 0), 0.12)
	end
	local pillPad = Instance.new("UIPadding")
	pillPad.PaddingLeft = UDim.new(0, 7)
	pillPad.PaddingRight = UDim.new(0, 7)
	pillPad.Parent = pill
	local rarityLabel = UiKit.text(pill, string.upper(rarity), 12)
	rarityLabel.AutomaticSize = Enum.AutomaticSize.X
	rarityLabel.Size = UDim2.fromScale(0, 1)
	rarityLabel.ZIndex = 3
	local odds = UiKit.text(tile, `1 in {Format.commas(DinoStats.monsterOneIn(dino.id))}`, 12, nil, Enum.TextXAlignment.Right)
	odds.Position = UDim2.fromOffset(70, 8)
	odds.Size = UDim2.fromOffset(TILE_SIZE.X - 78, 18)
	odds.ZIndex = 3
	local name = UiKit.text(tile, if seen then dino.name else "???", 16)
	name.Position = UDim2.fromOffset(5, TILE_SIZE.Y - 27)
	name.Size = UDim2.fromOffset(TILE_SIZE.X - 10, 22)
	fitText(name, 16)
	name.ZIndex = 3
	return tile
end

-- Builds one map's row of the list. Returns what showModels needs.
local function mapRow(parent: Instance, biome, number: number, discovered)
	local found, count = countFound(biome, discovered)
	local row = frame(parent, biome.id, 0, (number - 1) * MAP_PITCH, LIST.width - 14, CARD_SIZE.Y)
	mapCard(row, biome, number, found, count)
	local tiles = {}
	for order, dino in monstersOf(biome) do
		local seen = discovered[dino.id] == true
		local rarity = UiKit.RARITY_ORDER[math.min(order, #UiKit.RARITY_ORDER)]
		table.insert(tiles, { frame = monsterTile(row, dino, rarity, seen, order), dino = dino, seen = seen })
	end
	return { top = (number - 1) * MAP_PITCH, tiles = tiles, shown = false }
end

-- Puts a map's models on its tiles, or takes them off again.
local function showModels(row, show: boolean)
	if row.shown == show then
		return
	end
	row.shown = show
	for _, tile in row.tiles do
		if show then
			tile.view = UiKit.monster(tile.frame, tile.dino.id, {
				spin = tile.seen,
				silhouette = not tile.seen,
				position = UDim2.fromOffset(10, 17),
				size = UDim2.fromOffset(TILE_SIZE.X - 20, 90),
				aspect = (TILE_SIZE.X - 20) / 90,
			})
			tile.view.ZIndex = 2
		elseif tile.view then
			tile.view:Destroy()
			tile.view = nil
		end
	end
end

function IndexController.start()
	local remote = ReplicatedStorage:WaitForChild("IndexRemotes"):WaitForChild("IndexChanged")
	local hud = buildGui()
	local completed = {} -- biome ids with every dino caught
	local heardFromServer = false -- the first list is what they already had, so it shouts nothing
	local discovered = {}
	local rows = {}
	local stale = true -- the list needs rebuilding next time it's seen
	local openedAt: string? = nil -- the farthest map last time it opened, to jump to a new one but not move you otherwise
	local scrolledTo = 0 -- where the list was left, in design pixels
	local holding: number? = nil -- where to keep the list while the panel pops open and its size changes

	-- Catching a biome's last dino shouts its reward, once the reveal of that dino is over.
	local function shoutCompleted(biome)
		task.spawn(function()
			while RevealController.isPlaying() do
				task.wait(0.25)
			end
			task.wait(1)
			PopText.shout(`{string.upper(biome.name)} COMPLETE!`, `x{Index.xpBoost.multiplier} XP for {math.round(Index.xpBoost.seconds / 60)} min`)
		end)
	end

	-- The farthest map you've found anything in, so you see what you're hunting. Its number too.
	local function farthestMap(): (string, number)
		local pick, number = Biomes[1].id, 1
		for index, biome in Biomes do
			if countFound(biome, discovered) > 0 then
				pick, number = biome.id, index
			end
		end
		return pick, number
	end

	-- CanvasPosition is in screen pixels and the panel is scaled to the screen, so this turns design pixels into them.
	local function screenPixels(): number
		return hud.list.AbsoluteCanvasSize.Y / hud.list.CanvasSize.Y.Offset
	end

	local function updateModels()
		local top = hud.list.CanvasPosition.Y / screenPixels()
		for _, row in rows do
			local near = row.top + CARD_SIZE.Y > top - LIVE_MARGIN and row.top < top + LIST.height + LIVE_MARGIN
			showModels(row, near and hud.panel.frame.Visible)
		end
	end

	local function render()
		for _, child in hud.list:GetChildren() do
			if child:IsA("Frame") then
				child:Destroy()
			end
		end
		table.clear(rows)
		local seen, total = 0, 0
		for number, biome in Biomes do
			local found, count = countFound(biome, discovered)
			seen += found
			total += count
			table.insert(rows, mapRow(hud.list, biome, number, discovered))
		end
		hud.total(seen, total, `{seen} / {total} found`)
		stale = false
	end

	hud.open.Activated:Connect(function()
		UiKit.togglePanel(hud.panel)
	end)
	hud.panel.frame:GetPropertyChangedSignal("Visible"):Connect(function()
		if hud.panel.frame.Visible then
			if stale then
				render()
			end
			local farthest, number = farthestMap()
			if farthest ~= openedAt then
				openedAt = farthest
				scrolledTo = (number - 1) * MAP_PITCH
			end
			holding = scrolledTo
			hud.list.CanvasPosition = Vector2.new(0, scrolledTo * screenPixels())
			task.delay(0.3, function()
				holding = nil
			end)
		else
			scrolledTo = hud.list.CanvasPosition.Y / screenPixels()
		end
		updateModels()
	end)
	hud.list:GetPropertyChangedSignal("AbsoluteCanvasSize"):Connect(function()
		if holding then
			hud.list.CanvasPosition = Vector2.new(0, holding * screenPixels())
		end
	end)
	hud.list:GetPropertyChangedSignal("CanvasPosition"):Connect(updateModels)
	remote.OnClientEvent:Connect(function(newDiscovered)
		discovered = newDiscovered
		for _, biome in Biomes do
			local found, count = countFound(biome, discovered)
			if count > 0 and found == count and not completed[biome.id] then
				completed[biome.id] = true
				if heardFromServer then
					shoutCompleted(biome)
				end
			end
		end
		heardFromServer = true
		if hud.panel.frame.Visible then
			render()
			updateModels()
		else
			stale = true
		end
	end)
end

return IndexController
