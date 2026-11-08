-- The animated rarity word (COMMON ... SECRET), from the Figma file "Throw Eggs - Rarity Labels" (numbers in
-- Config/Rarity). Letters in a top-to-bottom gradient with a dark outline; then, rarer and rarer, a gentle bob, a
-- white shine that sweeps across, a breathing glow, a pulse, twinkling sparkles, a wobble, Ancient's rumble and
-- rising embers, and Secret's glitch with pink and cyan ghosts. Every word on screen shares one clock, so two of the
-- same rarity move together. Not started by Main: the first label made starts the loop.
--
-- RarityLabel.create(parent, rarity, textSize, align?, text?) returns a see-through Frame the size of a UiKit.text
-- line; position and size it like one. text replaces the word (My Monsters adds its CHONK level).
local RunService = game:GetService("RunService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Rarity = require(ReplicatedStorage.Shared.Config.Rarity)
local UiKit = require(ReplicatedStorage.Shared.UiKit)

local RarityLabel = {}

local LOOP = Rarity.loop
local WHITE = Color3.new(1, 1, 1)
local labels = {} -- [container] = state
local running = false

local function ease(x: number): number
	x = math.clamp(x, 0, 1)
	return x * x * (3 - 2 * x)
end

-- Between keys { { time, value }, ... }: eased between them, held before the first and after the last.
local function between(keys, t: number): number
	if t <= keys[1][1] then
		return keys[1][2]
	end
	for index = 2, #keys do
		local a, b = keys[index - 1], keys[index]
		if t <= b[1] then
			return a[2] + (b[2] - a[2]) * ease((t - a[1]) / (b[1] - a[1]))
		end
	end
	return keys[#keys][2]
end

-- Jumps from one value to the next at each key, like Figma's HOLD keyframes.
local function step(keys, t: number): number
	local value = keys[1][2]
	for _, key in keys do
		if t >= key[1] then
			value = key[2]
		end
	end
	return value
end

-- 0 at the loop's start and end, 1 in the middle (`times` waves a loop).
local function wave(t: number, times: number?): number
	return 0.5 - 0.5 * math.cos(2 * math.pi * t / LOOP * (times or 1))
end

local SHAKE = { { 0, 0 }, { 0.07, -3 }, { 0.14, 3 }, { 0.21, -2.5 }, { 0.28, 2 }, { 0.35, -1 }, { 0.42, 0 } }
local FLICKER = { { 0, 0.9 }, { 0.15, 0.5 }, { 0.3, 1 }, { 0.9, 0.55 }, { 1.4, 0.95 }, { 2.1, 0.5 }, { 3, 0.9 } }
local JUMPS = { { 0, 0 }, { 1.05, -6 }, { 1.12, 5 }, { 1.18, -3 }, { 1.25, 7 }, { 1.32, 0 }, { 2.44, 4 }, { 2.5, -5 }, { 2.56, 0 } }
local GHOST_SHOW = { { 0, 0 }, { 1.05, 0.85 }, { 1.32, 0 }, { 2.44, 0.7 }, { 2.56, 0 } }
local GHOST_SHIFT = { { 0, 4 }, { 1.18, 8 }, { 1.25, 3 }, { 2.44, 6 } }
local BLINK = { { 0, 1 }, { 2.15, 0.35 }, { 2.2, 1 }, { 2.25, 0.5 }, { 2.3, 1 } }

local function word(parent: Instance, text: string, size: number, align: Enum.TextXAlignment, z: number): TextLabel
	local label = Instance.new("TextLabel")
	label.BackgroundTransparency = 1
	label.FontFace = UiKit.FONT
	label.Text = text
	label.TextSize = size
	label.TextColor3 = WHITE
	label.TextXAlignment = align
	label.Size = UDim2.fromScale(1, 1)
	label.ZIndex = z
	label.Parent = parent
	return label
end

local function stroke(label: TextLabel, color: Color3, thickness: number): UIStroke
	local s = Instance.new("UIStroke")
	s.ApplyStrokeMode = Enum.ApplyStrokeMode.Contextual
	s.Color = color
	s.Thickness = thickness
	s.LineJoinMode = Enum.LineJoinMode.Round
	s.Parent = label
	return s
end

local function round(frame: Frame)
	local corner = Instance.new("UICorner")
	corner.CornerRadius = UDim.new(1, 0)
	corner.Parent = frame
end

-- A four-point sparkle: two thin rounded bars crossed, on a turning holder.
local function sparkle(parent: Instance, color: Color3, z: number): Frame
	local holder = Instance.new("Frame")
	holder.BackgroundTransparency = 1
	holder.AnchorPoint = Vector2.new(0.5, 0.5)
	holder.ZIndex = z
	holder.Parent = parent
	for _, rotation in { 0, 90 } do
		local bar = Instance.new("Frame")
		bar.BackgroundColor3 = WHITE
		bar.BorderSizePixel = 0
		bar.AnchorPoint = Vector2.new(0.5, 0.5)
		bar.Position = UDim2.fromScale(0.5, 0.5)
		bar.Size = UDim2.fromScale(1, 0.26)
		bar.Rotation = rotation
		bar.ZIndex = z
		bar.Parent = holder
		round(bar)
		local glow = Instance.new("UIStroke")
		glow.Color = color
		glow.Thickness = 1.5
		glow.Transparency = 0.3
		glow.Parent = bar
	end
	return holder
end

local function update(state, t: number)
	local style, size = state.style, state.size
	local main = state.main
	local bounds = main.TextBounds
	local box = main.AbsoluteSize
	if box.X <= 0 or bounds.X <= 0 then
		return
	end
	-- Where the letters sit across the label, as shares of its width (the layout's scale cancels out).
	local share = math.min(bounds.X / box.X, 1)
	local left = if main.TextXAlignment == Enum.TextXAlignment.Left
		then 0
		elseif main.TextXAlignment == Enum.TextXAlignment.Right then 1 - share
		else (1 - share) / 2
	local unit = size / 56 -- the Figma design's moves are for 56px letters

	local y = if style.bob then -Rarity.bob * size * wave(t) else 0
	local x = if style.shake then step(SHAKE, t) * unit else 0
	if style.glitch then
		x = step(JUMPS, t) * unit
	end
	state.holder.Position = UDim2.fromOffset(x, y)
	if style.pulse then
		state.scale.Scale = 1 + style.pulse * wave(t, if style.pulseTwice then 2 else 1)
	end
	if style.wobble then
		state.holder.Rotation = style.wobble * math.sin(2 * math.pi * t / LOOP)
	end

	local blink = if style.glitch then step(BLINK, t) else 1
	main.TextTransparency = 1 - blink
	state.inkLabel.TextTransparency = 1 - blink
	state.ink.Transparency = 1 - blink

	if state.glow then
		local amount
		if style.flicker then
			amount = between(FLICKER, t)
		else
			local range = style.glowRange
			amount = range[1] + (range[2] - range[1]) * wave(t, if style.glowTwice then 2 else 1)
		end
		amount *= blink
		for index, layer in state.glow do
			layer.stroke.Transparency = 1 - Rarity.glowLayers[index][2] * amount
		end
	end

	if state.shine then
		local centre = nil
		for _, window in style.shine do
			if t >= window[1] and t <= window[2] then
				local from, to = left - Rarity.shineWidth, left + share + Rarity.shineWidth
				centre = from + (to - from) * ease((t - window[1]) / (window[2] - window[1]))
			end
		end
		state.shine.Visible = centre ~= nil and blink > 0.9
		if centre then
			state.shineGradient.Offset = Vector2.new(centre - 0.5, 0)
		end
	end

	for _, spark in state.sparkles do
		local p = (t - spark.start) / spark.speed
		local grow = if p >= 0 and p <= 1 then math.sin(math.pi * p) else 0
		local s = size * spark.size * (0.15 + 1.1 * grow)
		spark.frame.Size = UDim2.fromOffset(s, s)
		spark.frame.Rotation = -90 * math.clamp(p, 0, 1)
		spark.frame.Position = UDim2.fromScale(left + spark.x * share, spark.y)
	end

	for index, ember in state.embers do
		local start = ((index - 1) * 0.55) % 2.2
		local p = (t - start) / 0.8
		ember.Visible = p >= 0 and p <= 1
		if ember.Visible then
			local rise = 1 - (1 - p) ^ 2
			ember.Position = UDim2.new(left + state.emberAt[index] * share, 0, 0.8, -1.25 * size * rise)
			ember.BackgroundTransparency = if p < 0.125 then 1 - p / 0.125 else (p - 0.125) / 0.875
		end
	end

	for _, ghost in state.ghosts do
		ghost.label.TextTransparency = 1 - step(GHOST_SHOW, t)
		ghost.label.Position = UDim2.fromOffset(ghost.side * step(GHOST_SHIFT, t) * unit, 0)
	end
end

-- Whether a label can be seen at all: it and every frame above it shown, in a switched-on ScreenGui or BillboardGui.
-- The My Monsters rows keep their labels while the panel is shut, so without this they all animated unseen, every frame.
local function onScreen(container: GuiObject): boolean
	local node: Instance? = container
	while node do
		if node:IsA("GuiObject") then
			if not node.Visible then
				return false
			end
		elseif node:IsA("LayerCollector") then
			return node.Enabled
		end
		node = node.Parent
	end
	return false
end

local function start()
	if running then
		return
	end
	running = true
	RunService.RenderStepped:Connect(function()
		local t = os.clock() % LOOP
		for container, state in labels do
			if not container.Parent then
				labels[container] = nil
			elseif onScreen(container) then
				update(state, t)
			end
		end
	end)
end

function RarityLabel.create(parent: Instance, rarity: string, size: number, align: Enum.TextXAlignment?, text: string?, still: boolean?): Frame
	local style = Rarity.styles[rarity] or Rarity.styles.common
	align = align or Enum.TextXAlignment.Center
	text = text or string.upper(rarity)
	local zBase = if parent:IsA("GuiObject") then parent.ZIndex else 1

	local container = Instance.new("Frame")
	container.Name = "RarityLabel"
	container.BackgroundTransparency = 1
	container.Size = UDim2.new(1, 0, 0, math.ceil(size * 1.25))
	container.ZIndex = zBase
	container.Parent = parent

	local holder = Instance.new("Frame")
	holder.Name = "Moves"
	holder.BackgroundTransparency = 1
	holder.Size = UDim2.fromScale(1, 1)
	holder.ZIndex = zBase
	holder.Parent = container
	local scale = Instance.new("UIScale")
	scale.Parent = holder

	local state = { style = style, size = size, holder = holder, scale = scale, sparkles = {}, embers = {}, emberAt = {}, ghosts = {} }

	if style.glow then
		-- Roblox has no blur, so the soft glow is a few outlines, each wider and fainter (Config/Rarity glowLayers),
		-- widest at the back.
		local glowColor = Color3.fromHex(style.glow)
		state.glow = {}
		for index = #Rarity.glowLayers, 1, -1 do
			local layer = word(holder, text, size, align, zBase)
			layer.TextColor3 = glowColor
			layer.TextTransparency = 0.6
			local s = stroke(layer, glowColor, math.max(1.5, size * Rarity.glowLayers[index][1]))
			state.glow[index] = { label = layer, stroke = s }
		end
	end
	if style.glitch then
		for _, ghost in { { "#ff3da8", -1 }, { "#3dfcff", 1 } } do
			local label = word(holder, text, size, align, zBase)
			label.TextColor3 = Color3.fromHex(ghost[1])
			label.TextTransparency = 1
			table.insert(state.ghosts, { label = label, side = ghost[2] })
		end
	end

	-- The outline is its own layer under the letters: a UIGradient tints its label's UIStroke too, which would
	-- turn Secret's light outline dark.
	local inkColor = Color3.fromHex(style.ink)
	local ink = word(holder, text, size, align, zBase)
	ink.Name = "Ink"
	ink.TextColor3 = inkColor
	state.ink = stroke(ink, inkColor, math.max(1.5, size * Rarity.strokeShare))
	state.inkLabel = ink
	local main = word(holder, text, size, align, zBase)
	main.Name = "Word"
	local fill = Instance.new("UIGradient")
	fill.Color = ColorSequence.new(Color3.fromHex(style.top), Color3.fromHex(style.bottom))
	fill.Rotation = 90
	fill.Parent = main
	state.main = main

	if style.shine then
		local shine = word(holder, text, size, align, zBase)
		shine.Name = "Shine"
		shine.Visible = false
		local band = Instance.new("UIGradient")
		local half = Rarity.shineWidth / 2
		band.Transparency = NumberSequence.new({
			NumberSequenceKeypoint.new(0, 1),
			NumberSequenceKeypoint.new(0.5 - half, 1),
			NumberSequenceKeypoint.new(0.5, 0.15),
			NumberSequenceKeypoint.new(0.5 + half, 1),
			NumberSequenceKeypoint.new(1, 1),
		})
		band.Rotation = 15
		band.Parent = shine
		state.shine, state.shineGradient = shine, band
	end

	local sparkColor = Color3.fromHex(style.glow or style.bottom)
	for _, spot in style.sparkles or {} do
		table.insert(state.sparkles, {
			frame = sparkle(holder, sparkColor, zBase),
			x = spot[1],
			y = spot[2],
			size = spot[3],
			start = spot[4],
			speed = style.sparkleSpeed or 1,
		})
	end
	for index, at in style.embers or {} do
		local ember = Instance.new("Frame")
		ember.BorderSizePixel = 0
		ember.AnchorPoint = Vector2.new(0.5, 0.5)
		ember.Size = UDim2.fromOffset(math.max(2, size * (if index % 2 == 0 then 0.09 else 0.13)), math.max(2, size * (if index % 2 == 0 then 0.09 else 0.13)))
		ember.BackgroundColor3 = Color3.fromHex(if index % 2 == 0 then "#ffd27a" else "#ff7a2e")
		ember.Visible = false
		ember.ZIndex = zBase
		ember.Parent = holder
		round(ember)
		table.insert(state.embers, ember)
		state.emberAt[index] = at
	end

	if still then
		-- Drawn once at a pose with the glow up and never updated again, so it costs nothing per frame (the Index, where
		-- the moving ones lagged). The word keeps its gradient, outline and glow, and its sparkles stay as little stars.
		-- Embers, ghosts and the sweeping shine are movement itself, so they stay away.
		update(state, LOOP / 2)
		for _, spark in state.sparkles do
			local s = size * spark.size * 1.25
			spark.frame.Size = UDim2.fromOffset(s, s)
			spark.frame.Rotation = -45
			spark.frame.Visible = true
		end
		for _, ember in state.embers do
			ember.Visible = false
		end
		for _, ghost in state.ghosts do
			ghost.label.Visible = false
		end
		if state.shine then
			state.shine.Visible = false
		end
		return container
	end

	labels[container] = state
	start()
	return container
end

return RarityLabel
