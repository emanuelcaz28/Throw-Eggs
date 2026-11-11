-- The number of the "1 in X" on the final screen of a lucky catch, alive [Owner, 2026-11-11: "more life at the final
-- screen reveal, for bigger numbers... effects on those numbers and change their colors and doing some crazy stuff"; then
-- "keep '1 in' simple and only change the other number's appearance, I don't want the numbers to zoom in and out"]. Only
-- the number moves (RevealFinalCard writes "1 in" plainly beside it), and nothing in it ever grows or shrinks: the
-- characters drop in, roll, wave, shake and change colour. Each character is its own label, so each can move on its own.
-- The rarer the luck label, the more it does (Config/Reveal oddsFx, one value per label from LUCKY! to IMPOSSIBLE!):
--   every lucky catch: the digits drop in one by one from a slant, a white shine sweeps across, a gentle wave runs through;
--   from SUPER LUCKY!: they roll like a slot machine and lock left to right with a tick and a kick, a thin glow breathes
--     behind them, sparkles twinkle either side;
--   from INSANE!: the colour drifts round the luck's colour;
--   from GODLY!: every digit runs through the rainbow and they shake and hop.
-- Display only.
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local Reveal = require(ReplicatedStorage.Shared.Config.Reveal)
local UiKit = require(ReplicatedStorage.Shared.UiKit)

local RevealOdds = {}

local settings = Reveal.oddsFx
local WHITE = Color3.new(1, 1, 1)

-- The value for luck label `level` (1 = LUCKY!) from a list with one per label.
local function pick(list, level: number)
	return list[math.clamp(level, 1, #list)]
end

local function hueShift(color: Color3, by: number): Color3
	local h, s, v = color:ToHSV()
	return Color3.fromHSV((h + by) % 1, s, v)
end

local function bounceOut(x: number): number
	x = math.clamp(x, 0, 1)
	if x < 1 / 2.75 then
		return 7.5625 * x * x
	elseif x < 2 / 2.75 then
		x -= 1.5 / 2.75
		return 7.5625 * x * x + 0.75
	elseif x < 2.5 / 2.75 then
		x -= 2.25 / 2.75
		return 7.5625 * x * x + 0.9375
	end
	x -= 2.625 / 2.75
	return 7.5625 * x * x + 0.984375
end

-- A four-point sparkle: two thin rounded bars crossed (glyphs like ✦ show as boxes on phones).
local function sparkle(parent: Instance, color: Color3): Frame
	local holder = Instance.new("Frame")
	holder.BackgroundTransparency = 1
	holder.AnchorPoint = Vector2.new(0.5, 0.5)
	holder.ZIndex = 5
	holder.Parent = parent
	for _, rotation in { 0, 90 } do
		local bar = Instance.new("Frame")
		bar.BackgroundColor3 = WHITE
		bar.BorderSizePixel = 0
		bar.AnchorPoint = Vector2.new(0.5, 0.5)
		bar.Position = UDim2.fromScale(0.5, 0.5)
		bar.Size = UDim2.fromScale(1, 0.24)
		bar.Rotation = rotation
		bar.ZIndex = 5
		bar.Parent = holder
		local corner = Instance.new("UICorner")
		corner.CornerRadius = UDim.new(0.5, 0)
		corner.Parent = bar
		local glow = Instance.new("UIStroke")
		glow.Color = color
		glow.Thickness = 1.5
		glow.Transparency = 0.25
		glow.Parent = bar
	end
	return holder
end

-- Plays `text` (the number, "123,916,608") in `holder`, a Frame in design pixels whose height is the line's. `tier` is the
-- catch's Config/Reveal tier and `level` its place (1 = LUCKY!). options: textSize, stroke (outline thickness), align
-- ("left", "right" or "center": where in the holder it sits), lead ({ text, size, stroke, gap }: plain words before
-- the number, like "1 in"), depth (solid letters: this many copies stepping down behind each
-- digit, darker), onTick(pitch 0 to 1) as each rolling digit locks. Returns stop().
function RevealOdds.play(holder: Frame, text: string, tier, level: number, options): () -> ()
	local random = Random.new()
	local textSize = options.textSize
	local strokeWidth = options.stroke
	local height = holder.Size.Y.Offset
	local right = options.align == "right"
	local base: Color3 = tier.color
	local mode = pick(settings.colors, level)
	local wave = pick(settings.wave, level)
	local glowWidth = pick(settings.glow, level)
	local jitter = pick(settings.jitter, level)
	local hop = pick(settings.hop, level)
	local rollTime = pick(settings.roll, level)
	local share = (level - 1) / math.max(#Reveal.tiers - 1, 1)
	local dropTurn = settings.dropTurn[1] + (settings.dropTurn[2] - settings.dropTurn[1]) * share
	local depth = options.depth or 0
	local extrudeX = Reveal.finalCard.extrudeX

	local centre = options.align == "center"
	local line = Instance.new("Frame")
	line.Name = "OddsFx"
	line.AnchorPoint = Vector2.new(if centre then 0.5 elseif right then 1 else 0, 0.5)
	line.Position = UDim2.fromScale(if centre then 0.5 elseif right then 1 else 0, 0.5)
	line.AutomaticSize = Enum.AutomaticSize.X
	line.Size = UDim2.fromOffset(0, height)
	line.BackgroundTransparency = 1
	line.Parent = holder
	local layout = Instance.new("UIListLayout")
	layout.FillDirection = Enum.FillDirection.Horizontal
	layout.HorizontalAlignment = if right then Enum.HorizontalAlignment.Right else Enum.HorizontalAlignment.Left
	layout.VerticalAlignment = Enum.VerticalAlignment.Center
	layout.SortOrder = Enum.SortOrder.LayoutOrder
	layout.Padding = UDim.new(0, settings.spacing)
	layout.Parent = line

	-- "1 in", plain, in the same line as the number so the two read as one [Owner, 2026-11-11: they looked apart]. Its
	-- letters sit on the number's baseline.
	if options.lead then
		local lead = options.lead
		local cell = Instance.new("Frame")
		cell.Name = "Lead"
		cell.BackgroundTransparency = 1
		cell.AutomaticSize = Enum.AutomaticSize.X
		cell.Size = UDim2.fromOffset(0, height)
		cell.LayoutOrder = 0
		cell.Parent = line
		local pad = Instance.new("UIPadding")
		pad.PaddingRight = UDim.new(0, lead.gap)
		pad.Parent = cell
		local label = UiKit.text(cell, lead.text, lead.size, WHITE, Enum.TextXAlignment.Left)
		label.AutomaticSize = Enum.AutomaticSize.X
		label.Size = UDim2.fromOffset(0, height)
		label.Position = UDim2.fromOffset(0, (textSize - lead.size) * 0.36)
		label:FindFirstChildOfClass("UIStroke").Thickness = lead.stroke
	end

	local chars = {}
	local digitOrder = 0
	local digitCount = #string.gsub(text, "%D", "")
	for index = 1, #text do
		local char = string.sub(text, index, index)
		local cell = Instance.new("Frame")
		cell.BackgroundTransparency = 1
		cell.AutomaticSize = Enum.AutomaticSize.X
		cell.Size = UDim2.fromOffset(0, height)
		cell.LayoutOrder = index
		cell.Parent = line
		local function layer(name: string, z: number): TextLabel
			local label = UiKit.text(cell, char, textSize)
			label.Name = name
			label.AutomaticSize = Enum.AutomaticSize.X
			label.Size = UDim2.fromOffset(0, height)
			label.ZIndex = z
			label.TextTransparency = 1
			label:FindFirstChildOfClass("UIStroke").Thickness = strokeWidth
			label:FindFirstChildOfClass("UIStroke").Transparency = 1
			return label
		end
		local glow = nil
		if glowWidth > 0 then
			-- Its text stays solid (a stroke fades with its text): the digit in front hides it, so only the outline shows.
			glow = layer("Glow", 1)
			glow:FindFirstChildOfClass("UIStroke").Thickness = strokeWidth + glowWidth
		end
		-- The solid part behind it: copies stepping down and sideways, darker the further back.
		local sides = {}
		for step = depth, 1, -1 do
			local side = layer("Side", 0)
			table.insert(sides, { label = side, step = step })
		end
		local label = layer("Char", 2)
		local gradient = Instance.new("UIGradient")
		gradient.Rotation = 90
		gradient.Parent = label
		local isDigit = string.match(char, "%d") ~= nil
		if isDigit then
			digitOrder += 1
		end
		table.insert(chars, {
			char = char,
			label = label,
			glow = glow,
			sides = sides,
			gradient = gradient,
			index = #chars + 1,
			turn0 = random:NextNumber(-dropTurn, dropTurn),
			-- A rolling digit locks on its real value at this time, left to right.
			lockAt = if isDigit and rollTime > 0 then settings.rollStart + rollTime * digitOrder / math.max(digitCount, 1) else nil,
			locked = not (isDigit and rollTime > 0),
			lockedAt = -math.huge,
			jumpY = 0,
			turn = 0,
		})
	end

	-- Sparkles twinkling either side of the number, on a layer the number's size (not part of its layout).
	local sparkLayer = Instance.new("Frame")
	sparkLayer.Name = "OddsSparkles"
	sparkLayer.AnchorPoint = line.AnchorPoint
	sparkLayer.Position = line.Position
	sparkLayer.BackgroundTransparency = 1
	sparkLayer.Parent = holder
	local sparks = {}
	for index = 1, pick(settings.sparkles, level) do
		local left = index % 2 == 1
		table.insert(sparks, {
			frame = sparkle(sparkLayer, base),
			x = if left then random:NextNumber(-0.12, -0.03) else random:NextNumber(1.03, 1.12),
			y = random:NextNumber(0.1, 0.9),
			size = random:NextNumber(settings.sparkleSize[1], settings.sparkleSize[2]),
			phase = random:NextNumber() * 10,
			speed = random:NextNumber(0.7, 1.3),
		})
	end

	local started = os.clock()
	local lastShake = 0
	local count = #chars

	local connection = RunService.RenderStepped:Connect(function()
		local now = os.clock()
		local t = now - started
		local shown = holder.AbsoluteSize.Y / math.max(height, 1) -- screen pixels per design pixel
		if shown > 0 then
			sparkLayer.Size = UDim2.fromOffset(line.AbsoluteSize.X / shown, height)
		end

		-- The shine: a band of white light sweeping across, then a rest.
		local band = (t % settings.shineEvery) / settings.shineTime * (count + 4) - 2

		-- Shaking and hopping on the rarest, a fresh nudge a few times a second.
		local shakeNow = (jitter > 0 or hop > 0) and now - lastShake >= settings.shakeEvery
		if shakeNow then
			lastShake = now
		end

		for _, entry in chars do
			local i = entry.index
			-- Dropping in: from above, slanted and see-through, landing with a bounce. Nothing grows or shrinks.
			local drop = math.clamp((t - settings.stagger * (i - 1)) / settings.dropTime, 0, 1)
			local fall = settings.drop * (1 - bounceOut(drop))
			local seeThrough = 1 - math.min(drop * 3, 1)

			-- Rolling digits show random ones until their turn, then lock with a tick and a kick upwards.
			if not entry.locked then
				if t >= entry.lockAt then
					entry.locked = true
					entry.lockedAt = t
					entry.label.Text = entry.char
					if entry.glow then
						entry.glow.Text = entry.char
					end
					for _, side in entry.sides do
						side.label.Text = entry.char
					end
					if options.onTick then
						options.onTick(math.clamp(t / (settings.rollStart + rollTime), 0, 1))
					end
				elseif drop > 0 then
					local digit = tostring(random:NextInteger(0, 9))
					entry.label.Text = digit
					if entry.glow then
						entry.glow.Text = digit
					end
					for _, side in entry.sides do
						side.label.Text = digit
					end
				end
			end
			local kick = math.max(0, 1 - (t - entry.lockedAt) / settings.lockKickTime)
			kick = settings.lockKick * kick * kick

			-- Its colour: fixed in the luck's colour, drifting round it, or the whole rainbow running through.
			local color = base
			if mode == "shift" then
				color = hueShift(base, settings.drift * math.sin(t * 2.2 + i * 0.45))
			elseif mode == "rainbow" then
				color = Color3.fromHSV((t * settings.rainbowSpeed - i * 0.07) % 1, 0.7, 1)
			end
			local shine = math.max(0, 1 - math.abs(i - band) / 1.6)
			entry.gradient.Color = ColorSequence.new({
				ColorSequenceKeypoint.new(0, color:Lerp(WHITE, 0.6 + 0.4 * shine)),
				ColorSequenceKeypoint.new(0.18, color:Lerp(WHITE, 0.6 + 0.4 * shine)),
				ColorSequenceKeypoint.new(0.85, color:Lerp(WHITE, 0.6 * shine)),
				ColorSequenceKeypoint.new(1, color:Lerp(WHITE, 0.6 * shine)),
			})
			entry.label.TextTransparency = seeThrough
			entry.label:FindFirstChildOfClass("UIStroke").Transparency = seeThrough

			-- The thin glow behind it breathes, in the same colour.
			if entry.glow then
				local breath = 0.5 + 0.5 * math.sin(t * settings.glowRate * 2 * math.pi - i * 0.3)
				local outline = entry.glow:FindFirstChildOfClass("UIStroke")
				outline.Color = color
				entry.glow.TextColor3 = color
				entry.glow.TextTransparency = seeThrough
				outline.Transparency = math.max(seeThrough, settings.glowFrom + (settings.glowTo - settings.glowFrom) * breath)
			end

			-- The wave, plus the shake and the hops, once it has landed.
			local landed = drop >= 1
			if shakeNow and landed then
				entry.turn = random:NextNumber(-jitter, jitter)
				entry.jumpY = if random:NextNumber() < 0.35 then -random:NextNumber(0, hop) else 0
			end
			local y = -fall - kick
			if landed then
				y += -wave * math.sin(t * settings.waveSpeed - i * settings.wavePhase) + entry.jumpY
			end
			entry.label.Position = UDim2.fromOffset(0, y)
			entry.label.Rotation = if landed then entry.turn else entry.turn0 * (1 - drop)
			if entry.glow then
				entry.glow.Position = entry.label.Position
				entry.glow.Rotation = entry.label.Rotation
			end
			-- The solid part follows, in a dark shade of the digit's colour.
			for _, side in entry.sides do
				local shade = color:Lerp(Color3.new(0, 0, 0), 0.55 + 0.25 * side.step / math.max(depth, 1))
				side.label.TextColor3 = shade
				local outline = side.label:FindFirstChildOfClass("UIStroke")
				outline.Color = shade:Lerp(Color3.new(0, 0, 0), 0.3)
				outline.Transparency = seeThrough
				side.label.TextTransparency = seeThrough
				side.label.Position = UDim2.fromOffset(side.step * extrudeX, y + side.step)
				side.label.Rotation = entry.label.Rotation
			end
		end

		-- The sparkles twinkle, turn and drift up a little.
		for _, spark in sparks do
			local life = (t * spark.speed + spark.phase) % 1.6 / 1.6
			local size = spark.size * math.sin(life * math.pi) ^ 2
			spark.frame.Size = UDim2.fromOffset(size, size)
			spark.frame.Position = UDim2.fromScale(spark.x, spark.y - life * 0.25)
			spark.frame.Rotation = (t * 90 * spark.speed) % 360
			local color = if mode == "rainbow" then Color3.fromHSV((t * settings.rainbowSpeed + spark.phase) % 1, 0.6, 1) else base
			for _, bar in spark.frame:GetChildren() do
				local outline = bar:FindFirstChildOfClass("UIStroke")
				if outline then
					outline.Color = color
				end
			end
		end
	end)

	return function()
		connection:Disconnect()
		line:Destroy()
		sparkLayer:Destroy()
	end
end

return RevealOdds
