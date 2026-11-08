-- The 2X XP moment, when the server confirms a tapped x2 bubble: the bubble bursts where it was tapped (a flash,
-- a ring and flying diamonds), a big "2X XP!" slams in over a purple sunburst with the XP gained under it, and
-- orbs fly from the bubble into the level bar, which flashes as they land. Purple edges and a small camera punch
-- sell the hit. It can come every 3 seconds, so it's over in about a second and stays out of the way: nothing
-- here takes taps. Display only: the XP is the server's.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local PopText = require(ReplicatedStorage.Shared.PopText)
local UiKit = require(ReplicatedStorage.Shared.UiKit)
local RevealSound = require(script.Parent.RevealSound)

local BoostMoment = {}

local LENGTH = 1.1 -- seconds; under Training.bubble.interval, so one is over before the next bubble
local CENTRE_Y = 0.3 -- the title's middle, as a share of the screen's height: clear of the bar and STOP
local MIN_SCALE = 0.62 -- the title and burst never go below this, so they read on a phone
local PURPLE = Color3.fromRGB(176, 92, 255)
local RAY = Color3.fromRGB(205, 140, 255)
local FLASH = Color3.fromRGB(255, 245, 255)
local SHARD_COLORS = { Color3.fromRGB(226, 190, 255), Color3.fromRGB(176, 92, 255), Color3.fromRGB(255, 224, 102) }
local TITLE_FILL = { "#ffffff", "#d39bff" }
local SHARDS = 12
local SHARD_SIZE = 26 -- design pixels (1280 x 720), like everything below
local SHARD_REACH = 210
local ORBS = 5
local ORB_SIZE = 34
local ORB_START, ORB_GAP, ORB_FLIGHT = 0.12, 0.05, 0.3 -- seconds
local RING_SIZE = 340
local RAY_PAIRS = 6 -- each beam crosses the middle, so 12 rays
local RAY_LENGTH, RAY_WIDTH = 520, 30
local SPIN = 40 -- degrees a second
local EDGE_DEPTH = 0.16 -- how far the edge flash reaches in, as a share of the screen
local EDGE_STRENGTH = 0.5
local SHAKE, SHAKE_TIME = 5, 0.12 -- pixels, seconds
local FOV_PUNCH = 2.5 -- degrees narrower, then back

local TITLE = { size = 118, outline = 11, shadow = 8 }
local DETAIL = { size = 46, outline = 6, shadow = 4 }

local TRACKS = {
	edge = { { 0, 0 }, { 0.05, 1, "out" }, { 0.3, 0.6 }, { 0.8, 0, "in" } },
	flashScale = { { 0, 0.6 }, { 0.14, 1.5, "out" } },
	flashOpacity = { { 0, 1 }, { 0.16, 0, "in" } },
	ringScale = { { 0, 0.2 }, { 0.42, 1, "out" } },
	ringOpacity = { { 0, 1 }, { 0.2, 1 }, { 0.42, 0, "in" } },
	shardReach = { { 0, 0.12 }, { 0.5, 1, "out" } },
	shardSize = { { 0, 1.2 }, { 0.3, 1 }, { 0.5, 0, "in" } },
	titleScale = { { 0, 2.1 }, { 0.11, 0.9, "in" }, { 0.21, 1, "out" }, { 0.75, 1 }, { 1.05, 1.12, "in" } },
	titleOpacity = { { 0, 0 }, { 0.05, 1 }, { 0.78, 1 }, { 1.05, 0, "in" } },
	titleRise = { { 0.75, 0 }, { 1.05, -30, "in" } },
	burstScale = { { 0, 0.3 }, { 0.22, 1, "out" } },
	burstOpacity = { { 0, 0 }, { 0.07, 1 }, { 0.6, 1 }, { 0.95, 0, "in" } },
	detailRise = { { 0.1, 16 }, { 0.26, 0, "out" } },
	detailOpacity = { { 0.1, 0 }, { 0.26, 1, "out" }, { 0.78, 1 }, { 1.05, 0, "in" } },
	orbScale = { { 0, 0.4 }, { 0.08, 1.2, "out" }, { 0.3, 0.7 } }, -- per orb, from its own start
	barFlash = { { 0, 0 }, { 0.05, 0.85, "out" }, { 0.45, 0, "in" } }, -- from the first orb landing
	barScale = { { 0, 1 }, { 0.06, 1.05, "out" }, { 0.3, 1, "inOut" } },
	fov = { { 0, 0 }, { 0.05, 1, "out" }, { 0.4, 0, "inOut" } },
}

local gui: ScreenGui? = nil
local stopRunning: (() -> ())? = nil

local function getGui(): ScreenGui
	if not gui then
		local layer = Instance.new("ScreenGui")
		layer.Name = "BoostMoment"
		layer.IgnoreGuiInset = true
		layer.ScreenInsets = Enum.ScreenInsets.None -- the edges reach the screen's edges, past a phone's notch too
		layer.ResetOnSpawn = false
		layer.DisplayOrder = 6 -- under the pop-up text (7)
		layer.Parent = Players.LocalPlayer:WaitForChild("PlayerGui")
		gui = layer
	end
	return gui :: ScreenGui
end

-- A strip along one edge, purple at the edge and clear inwards.
local function edgeStrip(parent: Instance, rotation: number, position: UDim2, size: UDim2): UIGradient
	local strip = Instance.new("Frame")
	strip.BorderSizePixel = 0
	strip.BackgroundColor3 = PURPLE
	strip.Position, strip.Size = position, size
	strip.Parent = parent
	local gradient = Instance.new("UIGradient")
	gradient.Rotation = rotation
	gradient.Parent = strip
	return gradient
end

local function setEdge(gradients: { UIGradient }, amount: number)
	local edge = 1 - EDGE_STRENGTH * amount
	local sequence = NumberSequence.new({ NumberSequenceKeypoint.new(0, edge), NumberSequenceKeypoint.new(1, 1) })
	for _, gradient in gradients do
		gradient.Transparency = sequence
	end
end

-- A drawn circle or diamond with an ink edge. Not a character: phones have no font with "✦".
local function blob(parent: Instance, size: number, color: Color3, round: boolean): (Frame, UIStroke)
	local shape = Instance.new("Frame")
	shape.BorderSizePixel = 0
	shape.BackgroundColor3 = color
	shape.AnchorPoint = Vector2.new(0.5, 0.5)
	shape.Size = UDim2.fromOffset(size, size)
	shape.Rotation = if round then 0 else 45
	shape.Parent = parent
	UiKit.corner(shape, if round then size else 4)
	local stroke = Instance.new("UIStroke")
	stroke.Color = UiKit.INK
	stroke.Thickness = 3
	stroke.Parent = shape
	return shape, stroke
end

-- The purple edges, and the sunburst with the words' frame on top of it, in the upper middle.
local function buildScreen(root: Frame, scale: number)
	local edges = {
		edgeStrip(root, 90, UDim2.fromScale(0, 0), UDim2.fromScale(1, EDGE_DEPTH)),
		edgeStrip(root, -90, UDim2.fromScale(0, 1 - EDGE_DEPTH), UDim2.fromScale(1, EDGE_DEPTH)),
		edgeStrip(root, 0, UDim2.fromScale(0, 0), UDim2.fromScale(EDGE_DEPTH * 0.6, 1)),
		edgeStrip(root, 180, UDim2.fromScale(1 - EDGE_DEPTH * 0.6, 0), UDim2.fromScale(EDGE_DEPTH * 0.6, 1)),
	}

	local centre = Instance.new("Frame")
	centre.Name = "Centre"
	centre.BackgroundTransparency = 1
	centre.Position = UDim2.fromScale(0.5, CENTRE_Y)
	centre.Parent = root
	local burst = Instance.new("Frame")
	burst.Name = "Sunburst"
	burst.BackgroundTransparency = 1
	burst.Parent = centre
	local burstScale = Instance.new("UIScale")
	burstScale.Parent = burst
	local rays = {}
	for index = 1, RAY_PAIRS do
		local ray = Instance.new("Frame")
		ray.BorderSizePixel = 0
		ray.BackgroundColor3 = RAY
		ray.AnchorPoint = Vector2.new(0.5, 0.5)
		ray.Size = UDim2.fromOffset(RAY_LENGTH * scale, RAY_WIDTH * scale)
		ray.Rotation = (index - 1) * 180 / RAY_PAIRS
		ray.Parent = burst
		local gradient = Instance.new("UIGradient")
		gradient.Parent = ray
		table.insert(rays, gradient)
	end

	local words = Instance.new("Frame")
	words.Name = "Words"
	words.BackgroundTransparency = 1
	words.Parent = centre
	local wordsScale = Instance.new("UIScale")
	wordsScale.Scale = scale
	wordsScale.Parent = words
	return edges, burst, burstScale, rays, words
end

-- Plays the moment. tapAt is the bubble's middle as AbsolutePosition measures it, bar the level bar the orbs fly
-- to, multiplier and xp what the server gave.
function BoostMoment.play(tapAt: Vector2, bar: GuiObject, multiplier: number, xp: string)
	RevealSound.boostSlam() -- the weakest slam, as the title hits
	if stopRunning then
		stopRunning()
	end
	local root = Instance.new("Frame")
	root.Name = "Boost"
	root.BackgroundTransparency = 1
	root.Size = UDim2.fromScale(1, 1)
	root.Parent = getGui()
	local scale = math.max(UiKit.scale(), MIN_SCALE)

	local edges, burst, burstScale, rays, words = buildScreen(root, scale)
	local title = PopText.word(words, `{multiplier}X XP!`, TITLE, Color3.new(1, 1, 1))
	title.Rotation = -4
	UiKit.gradient(title:FindFirstChild("Text") :: TextLabel, TITLE_FILL)
	local titleScale = Instance.new("UIScale")
	titleScale.Parent = title
	local detail = PopText.word(words, `+{xp} XP`, DETAIL, UiKit.GOLD)
	local detailY = (TITLE.size + DETAIL.size) / 2 + 2

	-- What happens at the bubble and the bar goes in their own ScreenGui, so it lines up with them on any screen
	-- (this layer reaches past a phone's notch and top bar; theirs doesn't).
	local hudGui = bar:FindFirstAncestorWhichIsA("ScreenGui") :: ScreenGui
	local origin = hudGui.AbsolutePosition
	local hudLayer = Instance.new("Frame")
	hudLayer.Name = "BoostHits"
	hudLayer.BackgroundTransparency = 1
	hudLayer.Size = UDim2.fromScale(1, 1)
	hudLayer.ZIndex = 5
	hudLayer.Parent = hudGui

	-- At the tap: a white flash, a ring and the diamonds.
	local tapSpot = tapAt - origin
	local spot = Instance.new("Frame")
	spot.Name = "Tap"
	spot.BackgroundTransparency = 1
	spot.Position = UDim2.fromOffset(tapSpot.X, tapSpot.Y)
	spot.Parent = hudLayer
	local flash, flashEdge = blob(spot, 150 * scale, FLASH, true)
	flashEdge:Destroy()
	local ring = Instance.new("Frame")
	ring.BackgroundTransparency = 1
	ring.AnchorPoint = Vector2.new(0.5, 0.5)
	ring.Size = UDim2.fromOffset(RING_SIZE * scale, RING_SIZE * scale)
	ring.Parent = spot
	UiKit.corner(ring, RING_SIZE)
	local ringStroke = Instance.new("UIStroke")
	ringStroke.Color = FLASH
	ringStroke.Thickness = 10 * scale
	ringStroke.Parent = ring
	local ringScale = Instance.new("UIScale")
	ringScale.Parent = ring

	local shards = {}
	for index = 1, SHARDS do
		local angle = (index - 1) / SHARDS * 2 * math.pi + math.random() * 0.3
		local reach = SHARD_REACH * scale * (0.75 + math.random() * 0.45)
		local shard = blob(spot, SHARD_SIZE * scale, SHARD_COLORS[index % #SHARD_COLORS + 1], false)
		local grow = Instance.new("UIScale")
		grow.Parent = shard
		table.insert(shards, { label = shard, grow = grow, to = Vector2.new(math.cos(angle), math.sin(angle)) * reach })
	end

	-- Into the bar.
	local barAt = bar.AbsolutePosition - origin + bar.AbsoluteSize / 2
	local orbs = {}
	for index = 1, ORBS do
		local orb = blob(hudLayer, ORB_SIZE * scale, SHARD_COLORS[1], true)
		orb.Visible = false
		local grow = Instance.new("UIScale")
		grow.Parent = orb
		local spread = (index - (ORBS + 1) / 2) / ORBS * bar.AbsoluteSize.X * 0.5
		table.insert(orbs, { label = orb, grow = grow, to = barAt + Vector2.new(spread, 0), bend = (index % 2 * 2 - 1) * 90 * scale })
	end

	-- The bar's flash sits on the bar itself, so it moves and scales with it.
	local barFlash = Instance.new("Frame")
	barFlash.Name = "BoostFlash"
	barFlash.BorderSizePixel = 0
	barFlash.BackgroundColor3 = FLASH
	barFlash.BackgroundTransparency = 1
	barFlash.Size = UDim2.fromScale(1, 1)
	barFlash.ZIndex = 1
	barFlash.Parent = bar
	UiKit.corner(barFlash, 22)
	local barGrow = Instance.new("UIScale")
	barGrow.Parent = bar

	local camera = workspace.CurrentCamera
	local baseFov = camera.FieldOfView
	local started = os.clock()
	local barHitAt = ORB_START + ORB_FLIGHT
	local connection: RBXScriptConnection

	local function stop()
		connection:Disconnect()
		root:Destroy()
		hudLayer:Destroy()
		barFlash:Destroy()
		barGrow:Destroy()
		camera.FieldOfView = baseFov
		stopRunning = nil
	end
	stopRunning = stop

	local sample = PopText.sample
	connection = RunService.RenderStepped:Connect(function()
		local t = os.clock() - started
		if t >= LENGTH then
			stop()
			return
		end
		setEdge(edges, sample(TRACKS.edge, t))

		burst.Rotation = t * SPIN
		burstScale.Scale = sample(TRACKS.burstScale, t)
		local rayOpacity = sample(TRACKS.burstOpacity, t)
		local raySequence = NumberSequence.new({
			NumberSequenceKeypoint.new(0, 1),
			NumberSequenceKeypoint.new(0.3, 1 - 0.55 * rayOpacity),
			NumberSequenceKeypoint.new(0.5, 1 - 0.85 * rayOpacity),
			NumberSequenceKeypoint.new(0.7, 1 - 0.55 * rayOpacity),
			NumberSequenceKeypoint.new(1, 1),
		})
		for _, gradient in rays do
			gradient.Transparency = raySequence
		end

		local shake = if t < SHAKE_TIME then SHAKE * (1 - t / SHAKE_TIME) else 0
		words.Position = UDim2.fromOffset(
			(math.random() * 2 - 1) * shake * scale,
			(math.random() * 2 - 1) * shake * scale + sample(TRACKS.titleRise, t) * scale
		)
		titleScale.Scale = sample(TRACKS.titleScale, t)
		PopText.setOpacity(title, sample(TRACKS.titleOpacity, t))
		detail.Position = UDim2.fromOffset(0, detailY + sample(TRACKS.detailRise, t))
		PopText.setOpacity(detail, sample(TRACKS.detailOpacity, t))

		local flashSize = 150 * scale * sample(TRACKS.flashScale, t)
		flash.Size = UDim2.fromOffset(flashSize, flashSize)
		flash.BackgroundTransparency = 1 - sample(TRACKS.flashOpacity, t)
		ringScale.Scale = sample(TRACKS.ringScale, t)
		ringStroke.Transparency = 1 - sample(TRACKS.ringOpacity, t)

		local reach = sample(TRACKS.shardReach, t)
		local shardSize = sample(TRACKS.shardSize, t)
		for _, shard in shards do
			shard.label.Position = UDim2.fromOffset(shard.to.X * reach, shard.to.Y * reach)
			shard.grow.Scale = shardSize
		end

		for index, orb in orbs do
			local own = t - ORB_START - (index - 1) * ORB_GAP
			local share = own / ORB_FLIGHT
			orb.label.Visible = share >= 0 and share < 1
			if orb.label.Visible then
				local eased = share * share -- speeds up into the bar
				local at = tapSpot:Lerp(orb.to, eased) + Vector2.new(orb.bend * math.sin(share * math.pi), 0)
				orb.label.Position = UDim2.fromOffset(at.X, at.Y)
				orb.grow.Scale = sample(TRACKS.orbScale, own)
			end
		end

		local sinceHit = t - barHitAt
		barFlash.BackgroundTransparency = 1 - sample(TRACKS.barFlash, sinceHit)
		barGrow.Scale = sample(TRACKS.barScale, sinceHit)

		camera.FieldOfView = baseFov - FOV_PUNCH * sample(TRACKS.fov, t)
	end)
end

return BoostMoment
