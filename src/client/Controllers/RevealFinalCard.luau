-- The final text of the reveal, standing in 3D space [Owner, 2026-11-11: "can you do the texts feel like they're in 3D
-- space? and make the rarity and the number the most important thing. I also want a new design on the texts. Mutations
-- feel like they're not special at all. The money/s should be placed under the monster."]
-- The text sits on three see-through panels in the world just in front of the camera (SurfaceGuis, drawn over everything),
-- each turned away from the lens, so it's seen in real perspective; they follow the camera, so they stay put on the
-- screen while the camera shakes and settles, and they sway a little. The letters are solid: each word is stacked from
-- copies of itself stepping down and back, like a block cut out of the colour, lit on top.
--   TITLE panel, over the monster's head, its top leaning towards the lens [Owner, 2026-11-11: "the name of the monster
--     should be above him", it read as "secret amethyst monster"]: the monster's NAME, the biggest thing there; under it
--     one row saying what it is: its RARITY drawn as the game's own rarity label (RarityLabel), its MUTATION in its own
--     material (gold that gleams, gems with facets and glints, Shadow with a dark pulse, Ghost flickering, Bubblegum
--     wobbling), its size and NEW! as stickers.
--   SHOUT and NUMBER panels, one centred block along the bottom (lucky catches only): the luck in one still line of
--     solid letters with a shine and a slow burst of rays behind, IMPOSSIBLE in a drifting rainbow; under it "1 in" and
--     the NUMBER as one line, the number rolling in (RevealOdds).
--   MONEY panel, under the monster's feet: what it earns, in solid green.
-- The title and the shout fly in from nearer the camera and the money rises up. "tap to continue" stays flat at the bottom.
-- RevealController shows it; numbers live in Config/Reveal finalCard. Display only.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")

local Format = require(ReplicatedStorage.Shared.Format)
local Reveal = require(ReplicatedStorage.Shared.Config.Reveal)
local RarityLabel = require(script.Parent.RarityLabel)
local RevealOdds = require(script.Parent.RevealOdds)
local UiKit = require(ReplicatedStorage.Shared.UiKit)

local RevealFinalCard = {}

local look = Reveal.finalCard
local WHITE = Color3.new(1, 1, 1)
local BLACK = Color3.new(0, 0, 0)
local NEW_COLORS = { "#ffc14d", "#ff7a2f" }
local GLYPH_WIDTH = 0.62 -- a Fredoka One letter is about this wide against its size, for fitting words

-- For framing the monster between the texts, in design pixels: how high the bottom text reaches, how low a giant's feet
-- may go, and how much of the top the title over its head takes.
function RevealFinalCard.height(hasMessage: boolean): (number, number, number)
	return look.frameTop, look.frameFeet, look.frameHead + (if hasMessage then look.messageRow else 0)
end

local function ease(u: number): number
	u = math.clamp(u, 0, 1)
	return 1 - (1 - u) ^ 3
end

local function backOut(u: number): number
	u = math.clamp(u, 0, 1)
	local c = 1.70158
	return 1 + (c + 1) * (u - 1) ^ 3 + c * (u - 1) ^ 2
end

-- The biggest text size up to `size` at which `text` fits in `width` design pixels.
local function fit(text: string, size: number, width: number): number
	return math.min(size, width / math.max(#text * GLYPH_WIDTH, 1))
end

local function colors(list: { string }): ColorSequence
	local keys = {}
	for index, value in list do
		table.insert(keys, ColorSequenceKeypoint.new((index - 1) / math.max(#list - 1, 1), Color3.fromHex(value)))
	end
	return ColorSequence.new(keys)
end

-- Solid letters: `depth` copies of the text stepping down and right in `side`, then the face in `face` (a ColorSequence,
-- top to bottom) with an outline. Returns the holder (AutomaticSize X, `height` tall) and its layers.
local function solid(parent: Instance, text: string, size: number, face: ColorSequence, side: Color3, depth: number, stroke: number)
	local height = math.ceil(size * 1.2)
	local holder = Instance.new("Frame")
	holder.BackgroundTransparency = 1
	holder.AutomaticSize = Enum.AutomaticSize.X
	holder.Size = UDim2.fromOffset(0, height + depth)
	local function layer(z: number, offset: number): TextLabel
		local label = UiKit.text(holder, text, size, WHITE, Enum.TextXAlignment.Left)
		label.AutomaticSize = Enum.AutomaticSize.X
		label.Size = UDim2.fromOffset(0, height)
		label.Position = UDim2.fromOffset(offset * look.extrudeX, offset)
		label.ZIndex = z
		label:FindFirstChildOfClass("UIStroke").Thickness = stroke
		return label
	end
	local sides = {}
	for step = depth, 1, -1 do
		local label = layer(1, step)
		-- The far side darker, the near side lighter: it reads as a lit block.
		local shade = side:Lerp(BLACK, 0.35 * step / math.max(depth, 1))
		label.TextColor3 = shade
		label:FindFirstChildOfClass("UIStroke").Color = shade:Lerp(BLACK, 0.3)
		table.insert(sides, label)
	end
	local front = layer(2, 0)
	front:FindFirstChildOfClass("UIStroke").Color = side:Lerp(BLACK, 0.55)
	local gradient = Instance.new("UIGradient")
	gradient.Rotation = 90
	gradient.Color = face
	gradient.Parent = front
	-- A band of white light that can sweep across the face (`shine`).
	local shine = layer(3, 0)
	shine:FindFirstChildOfClass("UIStroke").Enabled = false
	local band = Instance.new("UIGradient")
	band.Rotation = 20
	band.Transparency = NumberSequence.new({
		NumberSequenceKeypoint.new(0, 1),
		NumberSequenceKeypoint.new(0.4, 1),
		NumberSequenceKeypoint.new(0.5, 0.1),
		NumberSequenceKeypoint.new(0.6, 1),
		NumberSequenceKeypoint.new(1, 1),
	})
	band.Offset = Vector2.new(-1, 0)
	band.Parent = shine
	holder.Parent = parent
	return { holder = holder, front = front, gradient = gradient, sides = sides, shine = band, shineLabel = shine, height = height + depth }
end

-- A four-point glint: two thin rounded bars crossed (glyphs like ✦ show as boxes on phones).
local function glint(parent: Instance, color: Color3): Frame
	local holder = Instance.new("Frame")
	holder.BackgroundTransparency = 1
	holder.AnchorPoint = Vector2.new(0.5, 0.5)
	holder.ZIndex = 6
	holder.Parent = parent
	for _, rotation in { 0, 90 } do
		local bar = Instance.new("Frame")
		bar.BackgroundColor3 = WHITE
		bar.BorderSizePixel = 0
		bar.AnchorPoint = Vector2.new(0.5, 0.5)
		bar.Position = UDim2.fromScale(0.5, 0.5)
		bar.Size = UDim2.fromScale(1, 0.22)
		bar.Rotation = rotation
		bar.ZIndex = 6
		bar.Parent = holder
		local corner = Instance.new("UICorner")
		corner.CornerRadius = UDim.new(0.5, 0)
		corner.Parent = bar
		local glow = Instance.new("UIStroke")
		glow.Color = color
		glow.Thickness = 2
		glow.Transparency = 0.2
		glow.Parent = bar
	end
	return holder
end

-- A panel in the world: a SurfaceGui `size` design pixels big, drawn over everything. `place(now)` gives where it stands
-- on the screen in design pixels from the screen's bottom left (its anchor point at that spot), its yaw and pitch in
-- degrees (turned away from the lens) and how far through its entrance it is.
local function newPanel(name: string, size: Vector2, anchor: Vector2, playerGui: Instance, order: number)
	local part = Instance.new("Part")
	part.Name = "RevealCardPanel"
	part.Anchored = true
	part.CanCollide = false
	part.CanQuery = false
	part.CanTouch = false
	part.CastShadow = false
	part.Transparency = 1
	part.Size = Vector3.new(1, 1, 0.05)
	part.Parent = workspace
	local surface = Instance.new("SurfaceGui")
	surface.Name = "RevealCard" .. name
	surface.Adornee = part
	surface.Face = Enum.NormalId.Back -- the face looking back at the camera
	surface.SizingMode = Enum.SurfaceGuiSizingMode.FixedSize
	surface.CanvasSize = size
	surface.AlwaysOnTop = true
	surface.LightInfluence = 0
	surface.Brightness = 1
	surface.ZOffset = order
	surface.MaxDistance = 1000
	pcall(function()
		surface.ClipsDescendants = false -- the solid letters' sides and the glints may reach past its edge
	end)
	surface.ResetOnSpawn = false
	surface.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	surface.Parent = playerGui
	local canvas = Instance.new("Frame")
	canvas.Name = "Canvas"
	canvas.Size = UDim2.fromScale(1, 1)
	canvas.BackgroundTransparency = 1
	canvas.Parent = surface
	return {
		part = part,
		surface = surface,
		canvas = canvas,
		size = size,
		anchor = anchor,
	}
end

-- Puts `panel` where `spot` (design pixels from the screen's bottom left) is on the screen, `look.depth` studs in front of
-- the camera, turned by yaw and pitch (degrees) round its own middle. `near` (0 to 1) brings it that share of the way to
-- the lens along its line of sight: same spot on the screen, bigger.
local function placePanel(panel, camera: Camera, scale: number, spot: Vector2, yaw: number, pitch: number, near: number)
	local viewport = camera.ViewportSize
	local depth = look.depth
	local studsPerPixel = 2 * depth * math.tan(math.rad(camera.FieldOfView) / 2) / math.max(viewport.Y, 1)
	local size = panel.size * scale * studsPerPixel
	-- Its middle on the screen, in pixels from the screen's middle (y up).
	local middle = Vector2.new(
		spot.X * scale + (0.5 - panel.anchor.X) * panel.size.X * scale - viewport.X / 2,
		spot.Y * scale + (0.5 - panel.anchor.Y) * panel.size.Y * scale - viewport.Y / 2
	)
	panel.part.Size = Vector3.new(size.X, size.Y, 0.05)
	panel.part.CFrame = camera.CFrame
		* CFrame.new(middle.X * studsPerPixel * (1 - near), middle.Y * studsPerPixel * (1 - near), -depth * (1 - near))
		* CFrame.Angles(math.rad(pitch), math.rad(yaw), 0)
end

-- The value for luck label `level` (1 = LUCKY!) from a list with one per label.
local function pick(list, level: number)
	return list[math.clamp(level, 1, #list)]
end

-- The luck shout ("GODLY LUCK!!!") [Owner, 2026-11-11, after seeing IMPOSSIBLE: the letters dropping, waving, rocking
-- and shaking one by one "looks kind of weird... not more movement or more text effects, just visually better"]: one
-- line of solid letters, still, in its luck's colours, with a white shine crossing it now and then; behind it a soft
-- burst of rays turns slowly. IMPOSSIBLE's face is a rainbow drifting slowly along the word, all letters together.
-- Numbers in Config/Reveal finalCard.shout, one value per luck label. Returns the block, its word (for the shine) and
-- step(t), run each frame with the time since the shout appeared.
local function buildShout(parent: Instance, tier, level: number)
	local shout = look.shout
	local top, bottom = Color3.fromHex(tier.sticker.colors[1]), Color3.fromHex(tier.sticker.colors[2])
	local face = ColorSequence.new({
		ColorSequenceKeypoint.new(0, WHITE),
		ColorSequenceKeypoint.new(0.45, top),
		ColorSequenceKeypoint.new(1, bottom),
	})
	local side = bottom:Lerp(BLACK, 0.55)
	local rainbow = pick(shout.rainbow, level)

	local block = Instance.new("Frame")
	block.Name = "Shout"
	block.BackgroundTransparency = 1
	block.AutomaticSize = Enum.AutomaticSize.XY
	block.Rotation = shout.tilt
	block.Parent = parent

	-- The burst: bars through its middle, see-through at their ends, long and short in turn.
	local burst = Instance.new("Frame")
	burst.Name = "Burst"
	burst.BackgroundTransparency = 1
	burst.AnchorPoint = Vector2.new(0.5, 0.5)
	burst.Position = UDim2.fromScale(0.5, 0.5)
	burst.Size = UDim2.fromOffset(2, 2) -- not 0: a frame with no size draws nothing inside it
	burst.ZIndex = 0
	burst.Parent = block
	local rays = pick(shout.rays, level)
	for index = 1, rays do
		local long = index % 2 == 1
		local bar = Instance.new("Frame")
		bar.BorderSizePixel = 0
		bar.BackgroundColor3 = if long then top else WHITE
		bar.AnchorPoint = Vector2.new(0.5, 0.5)
		bar.Size = UDim2.fromOffset(pick(shout.rayLength, level) * (if long then 2 else 1.5), if long then shout.rayWidth else shout.rayWidth * 0.6)
		bar.Rotation = (index - 1) * 180 / rays
		bar.ZIndex = 0
		bar.Parent = burst
		local corner = Instance.new("UICorner")
		corner.CornerRadius = UDim.new(0.5, 0)
		corner.Parent = bar
		local fade = Instance.new("UIGradient")
		fade.Transparency = NumberSequence.new({
			NumberSequenceKeypoint.new(0, 1),
			NumberSequenceKeypoint.new(0.5, shout.rayStrength),
			NumberSequenceKeypoint.new(1, 1),
		})
		fade.Parent = bar
	end

	local label: string = tier.sticker.label
	local word = solid(block, label, fit(label, pick(shout.size, level), shout.width), face, side, pick(shout.depth, level), shout.stroke)
	word.holder.Name = "Word"
	if rainbow then
		word.gradient.Rotation = 0 -- the rainbow runs along the word
	end

	local function step(t: number)
		burst.Rotation = (t * shout.raySpin) % 360
		if rainbow then
			local keys = {}
			for index = 0, 6 do
				local hue = (index / 6 * 0.75 - t * shout.rainbowRate) % 1
				table.insert(keys, ColorSequenceKeypoint.new(index / 6, Color3.fromHSV(hue, 0.5, 1)))
			end
			word.gradient.Color = ColorSequence.new(keys)
		end
	end
	return block, word, step
end

-- Shows the card. `gui` is RevealHud (for "tap to continue"), `scale` the HUD's. info: name (capitals), rarity (tier id),
-- rarityLook (Config/Rarity style), rarityWord (UiKit), size and mutation (Config/Catch options or nil), isNew, income
-- (text), tier (Config/Reveal luck tier or nil), level (its place, 1 = LUCKY!), oneIn, message (or nil), feet and head
-- (the bottom and top of the monster, in the world), onTick (each rolling digit). Returns destroy().
function RevealFinalCard.show(gui: ScreenGui, scale: number, info): () -> ()
	local camera = workspace.CurrentCamera
	local playerGui = Players.LocalPlayer:WaitForChild("PlayerGui")
	local pair = UiKit.RARITY[info.rarity] or UiKit.RARITY.common
	local deep = Color3.fromHex(pair[2])
	local textColor = Color3.fromHex(UiKit.RARITY_TEXT[info.rarity] or "#ffffff")
	local random = Random.new()
	local stops = {}
	local alive = true
	local started = os.clock()
	local glints = {}
	local effects = {} -- functions run each frame with the time since the card appeared

	-- The panels.
	local title = newPanel("Title", look.titleSize, Vector2.new(0.5, 0), playerGui, 3)
	local shoutPanel = if info.tier then newPanel("Shout", look.shoutSize, Vector2.new(0.5, 0), playerGui, 4) else nil
	local numberPanel = if info.tier then newPanel("Number", look.numberPanel, Vector2.new(0.5, 0), playerGui, 3) else nil
	local money = newPanel("Money", look.moneySize, Vector2.new(0.5, 1), playerGui, 2)
	-- A soft band of dark, see-through at `fades` (pairs of { place 0 to 1 down it, how see-through }).
	local function shade(parent: Instance, size: Vector2, fades): Frame
		local band = Instance.new("Frame")
		band.Name = "Shade"
		band.BackgroundColor3 = BLACK
		band.BorderSizePixel = 0
		band.Size = UDim2.fromOffset(size.X, size.Y)
		band.ZIndex = 0
		band.Parent = parent
		local keys = {}
		for _, fade in fades do
			table.insert(keys, NumberSequenceKeypoint.new(fade[1], fade[2]))
		end
		local gradient = Instance.new("UIGradient")
		gradient.Rotation = 90
		gradient.Transparency = NumberSequence.new(keys)
		gradient.Parent = band
		return band
	end
	local under = if info.tier then newPanel("Shade", look.luckShade, Vector2.new(0.5, 0), playerGui, 1) else nil
	if under then
		shade(under.canvas, look.luckShade, { { 0, 1 }, { 0.55, look.shade }, { 1, look.shade * 0.8 } })
	end

	-- Something that slides into its place on a panel after `delay`: from `from` pixels away, with a bounce.
	local function enter(object: GuiObject, delay: number, from: Vector2)
		local home = object.Position
		object.Position = home + UDim2.fromOffset(from.X, from.Y)
		object.Visible = false
		task.delay(delay, function()
			if not alive then
				return
			end
			object.Visible = true
			TweenService:Create(object, TweenInfo.new(0.45, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Position = home }):Play()
		end)
	end

	-- Glints twinkling round `holder` (a word), in `color`.
	local function addGlints(panel, holder: GuiObject, count: number, color: Color3, sizes: { number }?)
		local range = sizes or look.glintSize
		for _ = 1, count do
			table.insert(glints, {
				frame = glint(panel.canvas, color),
				holder = holder,
				x = random:NextNumber(-0.05, 1.05),
				y = random:NextNumber(0.05, 0.85),
				size = random:NextNumber(range[1], range[2]),
				phase = random:NextNumber() * 10,
				speed = random:NextNumber(0.8, 1.4),
			})
		end
	end

	-- A white shine sweeping across a word every `every` seconds, the first after `first`.
	local function addShine(word, first: number, every: number)
		table.insert(effects, function(t: number)
			local u = ((t - first) % every) / look.shineTime
			word.shine.Offset = Vector2.new(if t < first then -1 else -1 + 2 * math.clamp(u, 0, 1), 0)
		end)
	end

	---------------------------------------------------------------- TITLE, over the monster's head: NAME, then what it is
	local titleWidth = look.titleSize.X - look.pad * 2
	local y = look.titleSize.Y - look.pad -- building up from the bottom

	-- The row under the name: rarity (the game's own rarity label), mutation in its material, size and NEW! as stickers.
	-- Everything in it shrinks together when it would be wider than the panel.
	local mutation = info.mutation
	local rarityText: string = info.rarityWord
	local wide = #rarityText * GLYPH_WIDTH * look.raritySize + 24
	local cells = 1
	if mutation then
		wide += #mutation.name * GLYPH_WIDTH * look.mutationSize + 8 * GLYPH_WIDTH * look.mutationCaption + 12
		cells += 1
	end
	if info.size then
		wide += #info.size.name * GLYPH_WIDTH * look.sizeWordSize + 4 * GLYPH_WIDTH * look.mutationCaption + 12
		cells += 1
	end
	if info.isNew then
		wide += 4 * GLYPH_WIDTH * look.stickerSize + 32
		cells += 1
	end
	wide += (cells - 1) * look.rowGap
	local shrink = math.min(1, titleWidth / wide)

	local row = Instance.new("Frame")
	row.Name = "Row"
	row.BackgroundTransparency = 1
	row.AnchorPoint = Vector2.new(0.5, 1)
	row.Position = UDim2.new(0.5, 0, 0, y)
	row.Size = UDim2.fromOffset(titleWidth, look.rowHeight)
	row.Parent = title.canvas
	local rowList = Instance.new("UIListLayout")
	rowList.FillDirection = Enum.FillDirection.Horizontal
	rowList.HorizontalAlignment = Enum.HorizontalAlignment.Center
	rowList.VerticalAlignment = Enum.VerticalAlignment.Center
	rowList.SortOrder = Enum.SortOrder.LayoutOrder
	rowList.Padding = UDim.new(0, look.rowGap * shrink)
	rowList.Parent = row
	local function cell(order: number, width: number?): Frame
		local frame = Instance.new("Frame")
		frame.BackgroundTransparency = 1
		frame.LayoutOrder = order
		if width then
			frame.Size = UDim2.fromOffset(width, look.rowHeight)
		else
			frame.AutomaticSize = Enum.AutomaticSize.X
			frame.Size = UDim2.fromOffset(0, look.rowHeight)
		end
		frame.Parent = row
		return frame
	end

	-- The rarity, drawn exactly as the game draws it everywhere else (RarityLabel: its colours, glow and movement).
	local raritySize = look.raritySize * shrink
	local rarityCell = cell(1, #rarityText * GLYPH_WIDTH * raritySize + 24)
	local rarity = RarityLabel.create(rarityCell, info.rarityLook or info.rarity, raritySize, Enum.TextXAlignment.Center, rarityText)
	rarity.AnchorPoint = Vector2.new(0, 0.5)
	rarity.Position = UDim2.fromScale(0, 0.5)

	-- The MUTATION, in its own material.
	if mutation then
		local style = look.mutations[mutation.id] or {}
		local mutationColor: Color3 = mutation.color
		local mutationSize = look.mutationSize * shrink
		local face = if style.colors then colors(style.colors) else ColorSequence.new(mutationColor:Lerp(WHITE, 0.6), mutationColor)
		local side = if style.side then Color3.fromHex(style.side) else mutationColor:Lerp(BLACK, 0.5)
		local holder = cell(2)
		holder.Name = "Mutation"
		local list = Instance.new("UIListLayout")
		list.FillDirection = Enum.FillDirection.Horizontal
		list.VerticalAlignment = Enum.VerticalAlignment.Center
		list.SortOrder = Enum.SortOrder.LayoutOrder
		list.Padding = UDim.new(0, 6)
		list.Parent = holder
		local word = solid(holder, mutation.name, mutationSize, face, side, look.mutationDepth, look.mutationStroke)
		word.holder.LayoutOrder = 1
		if style.facets then
			word.gradient.Rotation = 70 -- a gem's facets: hard bands of light and dark across it
		end
		local captionSize = look.mutationCaption * shrink
		local caption = UiKit.text(holder, "MUTATION", captionSize, Color3.fromHex((style.colors or { "#ffffff" })[1]), Enum.TextXAlignment.Left)
		caption.AutomaticSize = Enum.AutomaticSize.X
		caption.Size = UDim2.fromOffset(0, word.height)
		caption.TextYAlignment = Enum.TextYAlignment.Top
		caption.LayoutOrder = 2
		caption:FindFirstChildOfClass("UIStroke").Color = side:Lerp(BLACK, 0.4)
		if style.shine then
			addShine(word, look.rowAt + 0.4, style.shine)
		end
		if style.glints then
			addGlints(title, word.holder, math.ceil(style.glints / 2), Color3.fromHex((style.colors or { "#ffffff", "#ffffff" })[2]), look.rowGlintSize)
		end
		if style.glow then
			-- A dark pulse: a wide outline in its colour breathing behind the word.
			local glowColor = Color3.fromHex(style.glow)
			local aura = UiKit.text(word.holder, mutation.name, mutationSize, glowColor, Enum.TextXAlignment.Left)
			aura.AutomaticSize = Enum.AutomaticSize.X
			aura.Size = UDim2.fromOffset(0, math.ceil(mutationSize * 1.2))
			aura.ZIndex = 0
			local outline = aura:FindFirstChildOfClass("UIStroke")
			outline.Color = glowColor
			outline.Thickness = look.mutationStroke + 8
			table.insert(effects, function(t: number)
				outline.Transparency = 0.45 + 0.4 * (0.5 + 0.5 * math.sin(t * 3))
			end)
		end
		if style.flicker then
			-- A ghost fades in and out, unevenly.
			table.insert(effects, function(t: number)
				local fade = 0.15 + 0.35 * math.max(0, math.sin(t * 7) * math.sin(t * 2.3))
				word.front.TextTransparency = fade
				for _, layer in word.sides do
					layer.TextTransparency = fade + 0.25
				end
			end)
		end
		if style.wobble then
			table.insert(effects, function(t: number)
				word.holder.Rotation = style.wobble * math.sin(t * 5.5)
			end)
		end
	end
	-- The SIZE, as a heavy solid word in its own colours with "SIZE" small beside it, like the mutation [Owner,
	-- 2026-11-11: the gold sticker "is not quite nice... remake it"]. The bigger the size, the hotter and thicker; the
	-- biggest ones rumble, and the very biggest broods in a red glow (Config/Reveal finalCard.sizes).
	if info.size then
		local style = look.sizes[info.size.id] or look.sizes.default
		local wordSize = look.sizeWordSize * shrink
		local side = Color3.fromHex(style.side)
		local holder = cell(3)
		holder.Name = "Size"
		local list = Instance.new("UIListLayout")
		list.FillDirection = Enum.FillDirection.Horizontal
		list.VerticalAlignment = Enum.VerticalAlignment.Center
		list.SortOrder = Enum.SortOrder.LayoutOrder
		list.Padding = UDim.new(0, 6)
		list.Parent = holder
		local word = solid(holder, info.size.name, wordSize, colors(style.colors), side, style.depth, look.sizeWordStroke)
		word.holder.LayoutOrder = 1
		local caption = UiKit.text(holder, "SIZE", look.mutationCaption * shrink, Color3.fromHex(style.colors[1]), Enum.TextXAlignment.Left)
		caption.AutomaticSize = Enum.AutomaticSize.X
		caption.Size = UDim2.fromOffset(0, word.height)
		caption.TextYAlignment = Enum.TextYAlignment.Top
		caption.LayoutOrder = 2
		caption:FindFirstChildOfClass("UIStroke").Color = side:Lerp(BLACK, 0.4)
		addShine(word, look.rowAt + 0.7, look.shineEvery + 0.4)
		if style.glow then
			local glowColor = Color3.fromHex(style.glow)
			local aura = UiKit.text(word.holder, info.size.name, wordSize, glowColor, Enum.TextXAlignment.Left)
			aura.AutomaticSize = Enum.AutomaticSize.X
			aura.Size = UDim2.fromOffset(0, math.ceil(wordSize * 1.2))
			aura.ZIndex = 0
			local outline = aura:FindFirstChildOfClass("UIStroke")
			outline.Color = glowColor
			outline.Thickness = look.sizeWordStroke + 7
			table.insert(effects, function(t: number)
				outline.Transparency = 0.4 + 0.4 * (0.5 + 0.5 * math.sin(t * 2.4))
			end)
		end
		if style.rumble then
			-- Heavy: it trembles in short bursts, as if the ground shook under it.
			table.insert(effects, function(t: number)
				local burst = math.max(0, math.sin(t * 2.2)) ^ 4
				word.holder.Rotation = style.rumble * burst * math.sin(t * 46)
			end)
		end
	end
	if info.isNew then
		local holder = cell(4)
		local tag = UiKit.tag(holder, "NEW!", NEW_COLORS, look.stickerSize * shrink, 5)
		tag.AnchorPoint = Vector2.new(0, 0.5)
		tag.Position = UDim2.fromScale(0, 0.5)
	end
	enter(row, look.rowAt, Vector2.new(0, 40))
	y -= look.rowHeight + look.gap

	-- The NAME: the headline, the biggest thing above the monster.
	local nameWord = solid(title.canvas, info.name, fit(info.name, look.nameSize, titleWidth - look.nameDepth), colors({ "#ffffff", "#ffffff", "#" .. textColor:Lerp(WHITE, 0.45):ToHex() }), deep:Lerp(BLACK, 0.2), look.nameDepth, look.nameStroke)
	nameWord.holder.AnchorPoint = Vector2.new(0.5, 1)
	nameWord.holder.Position = UDim2.new(0.5, 0, 0, y)
	enter(nameWord.holder, look.nameAt, Vector2.new(0, -70))
	addShine(nameWord, look.nameAt + 0.5, look.shineEvery)
	y -= nameWord.height + look.gap

	-- A message (a finished map, a new best, sent to the backpack) over the name.
	if info.message then
		local message = UiKit.text(title.canvas, info.message, look.messageSize, UiKit.GOLD)
		message.AnchorPoint = Vector2.new(0.5, 1)
		message.Position = UDim2.new(0.5, 0, 0, y)
		message.Size = UDim2.fromOffset(titleWidth, look.messageRow)
		enter(message, look.rowAt + 0.1, Vector2.new(0, -30))
		y -= look.messageRow
	end
	local titleHeight = look.titleSize.Y - y -- how much of the panel, from its bottom, is written on
	local titleBand = shade(title.canvas, look.titleShade, { { 0, 1 }, { 0.5, look.shade }, { 1, 1 } })
	titleBand.AnchorPoint = Vector2.new(0.5, 0.5)
	titleBand.Position = UDim2.new(0.5, 0, 0, look.titleSize.Y - titleHeight / 2)

	---------------------------------------------------------------- LUCK, along the bottom: the shout over "1 in NUMBER"
	-- [Owner, 2026-11-11: shout and number side by side, and "1 in" apart from its number, looked like separate pieces]
	-- One block, centred: the shout on top, and under it "1 in" and the number as one line.
	local shoutStep = nil
	if shoutPanel and numberPanel then
		local block, word, step = buildShout(shoutPanel.canvas, info.tier, info.level)
		block.AnchorPoint = Vector2.new(0.5, 1)
		block.Position = UDim2.fromOffset(look.shoutSize.X / 2, look.shoutSize.Y - look.pad)
		shoutStep = step
		addShine(word, look.shoutAt + 0.6, look.shineEvery)

		local text = Format.commas(info.oneIn)
		local leadSize = look.oneInSize
		local leadWidth = math.ceil(4 * GLYPH_WIDTH * leadSize) + look.oneInGap
		local numberSize = fit(text, look.numberSize, (look.numberPanel.X - look.pad * 2 - leadWidth - look.numberDepth) / 0.92)
		local number = Instance.new("Frame")
		number.Name = "Number"
		number.AnchorPoint = Vector2.new(0.5, 1)
		number.Position = UDim2.fromOffset(look.numberPanel.X / 2, look.numberPanel.Y - look.pad)
		number.Size = UDim2.fromOffset(look.numberPanel.X - look.pad * 2, math.ceil(numberSize * 1.2) + look.numberDepth + 10)
		number.BackgroundTransparency = 1
		number.Parent = numberPanel.canvas
		task.delay(look.numberAt, function()
			if not alive then
				return
			end
			local ok, stop = pcall(RevealOdds.play, number, text, info.tier, info.level, {
				textSize = numberSize,
				stroke = look.numberStroke,
				align = "center",
				depth = look.numberDepth,
				onTick = info.onTick,
				lead = { text = "1 in", size = leadSize, stroke = look.oneInStroke, gap = look.oneInGap },
			})
			if ok then
				table.insert(stops, stop)
			else
				warn(`[RevealFinalCard] Number effects failed: {stop}`)
			end
		end)
	end

	---------------------------------------------------------------- MONEY, under the monster
	local cash = solid(money.canvas, info.income, fit(info.income, look.moneySize.Y * 0.62, look.moneySize.X - 40), colors({ "#f2ffe0", "#9dff6a", "#3fc42a" }), Color3.fromRGB(22, 110, 30), look.moneyDepth, look.moneyStroke)
	cash.holder.AnchorPoint = Vector2.new(0.5, 0.5)
	cash.holder.Position = UDim2.fromScale(0.5, 0.5)
	addShine(cash, look.moneyAt + 0.5, look.shineEvery + 0.7)

	-- "tap to continue", flat, bottom centre.
	local hint = UiKit.text(gui, "tap to continue", look.hintSize)
	hint.Name = "FinalHint"
	hint.AnchorPoint = Vector2.new(0.5, 1)
	hint.Position = UDim2.new(0.5, 0, 1, -look.hintAbove * scale)
	hint.Size = UDim2.fromOffset(400 * scale, math.ceil(look.hintSize * 1.3) * scale)
	hint.TextScaled = true
	hint.ZIndex = 3
	Instance.new("UIScale").Parent = hint -- UiKit.pulse breathes it through this
	UiKit.pulse(hint)

	-- Where a point in the world is on the screen, in design pixels from the screen's bottom left.
	local function onScreen(point: Vector3?): Vector2?
		if not point then
			return nil
		end
		local seen = camera:WorldToViewportPoint(point)
		if seen.Z <= 0 then
			return nil
		end
		return Vector2.new(seen.X / scale, (camera.ViewportSize.Y - seen.Y) / scale)
	end
	-- How far through its fly-in a panel is: it comes from nearer the camera (bigger) and lands with a bounce.
	local function slam(t: number, at: number): number
		return look.slamFrom * (1 - backOut((t - at) / look.slamTime))
	end
	-- Each frame: the panels follow the camera, fly in, sway; the effects run.
	local function step()
		local t = os.clock() - started
		local viewport = camera.ViewportSize
		local width, height = viewport.X / scale, viewport.Y / scale
		local sway = look.sway * math.sin(t * look.swayRate)

		-- The title stands just over the monster's head, never off the top of the screen and never below its middle.
		local head = onScreen(info.head) or Vector2.new(width / 2, height * 0.75)
		local titleY = math.clamp(head.Y + look.headGap, height * look.titleLowest, height - look.margin - titleHeight)
		placePanel(title, camera, scale, Vector2.new(math.clamp(head.X, width * 0.4, width * 0.6), titleY), sway, look.titlePitch, slam(t, look.titleAt))
		title.surface.Enabled = t >= look.titleAt

		-- The luck: the number along the bottom, the shout just over it, both in the middle.
		if shoutPanel and numberPanel then
			if under then
				placePanel(under, camera, scale, Vector2.new(width / 2, 0), 0, 0, 0)
			end
			placePanel(numberPanel, camera, scale, Vector2.new(width / 2, look.luckBottom), sway * 0.5, look.luckPitch, 0)
			numberPanel.surface.Enabled = t >= look.numberAt - 0.15
			placePanel(shoutPanel, camera, scale, Vector2.new(width / 2, look.luckBottom + look.numberPanel.Y + look.luckGap), sway * 0.5, look.luckPitch, slam(t, look.shoutAt))
			shoutPanel.surface.Enabled = t >= look.shoutAt
			if shoutStep and t >= look.shoutAt then
				shoutStep(t - look.shoutAt)
			end
		end

		-- The money stands just under the monster's feet, kept clear of the luck below it.
		local lowest = if shoutPanel then look.moneyLowest else look.moneyLowestPlain
		local feet = onScreen(info.feet) or Vector2.new(width / 2, lowest)
		local rise = ease((t - look.moneyAt) / 0.5)
		local spotY = math.clamp(feet.Y - look.moneyBelowFeet, lowest, math.max(height * 0.55, lowest)) - (1 - rise) * 60
		placePanel(money, camera, scale, Vector2.new(math.clamp(feet.X, width * 0.35, width * 0.65), spotY), sway * 0.5, look.luckPitch * 0.6, 0)
		money.surface.Enabled = t >= look.moneyAt
		for _, effect in effects do
			effect(t)
		end
		-- Glints twinkle round their word and turn.
		for _, spark in glints do
			local holder = spark.holder
			local life = (t * spark.speed + spark.phase) % 1.4 / 1.4
			local size = spark.size * math.sin(life * math.pi) ^ 3
			local box = holder.AbsoluteSize
			local corner = holder.AbsolutePosition - spark.frame.Parent.AbsolutePosition
			spark.frame.Visible = holder.Visible and box.X > 0
			spark.frame.Size = UDim2.fromOffset(size, size)
			spark.frame.Position = UDim2.fromOffset(corner.X + box.X * spark.x, corner.Y + box.Y * spark.y)
			spark.frame.Rotation = (t * 120 * spark.speed) % 360
		end
	end
	step()
	local connection = RunService.RenderStepped:Connect(step)

	return function()
		alive = false
		connection:Disconnect()
		for _, stop in stops do
			pcall(stop)
		end
		for _, panel in { title, shoutPanel, numberPanel, money, under } do
			if panel then
				panel.surface:Destroy()
				panel.part:Destroy()
			end
		end
		hint:Destroy()
	end
end

-- Removes what a reveal that broke half-way left behind.
function RevealFinalCard.cleanUp()
	local playerGui = Players.LocalPlayer:FindFirstChild("PlayerGui")
	for _, name in { "RevealCardTitle", "RevealCardShout", "RevealCardNumber", "RevealCardMoney", "RevealCardShade" } do
		local left = playerGui and playerGui:FindFirstChild(name)
		if left then
			left:Destroy()
		end
	end
	for _, part in workspace:GetChildren() do
		if part.Name == "RevealCardPanel" then
			part:Destroy()
		end
	end
end

return RevealFinalCard
