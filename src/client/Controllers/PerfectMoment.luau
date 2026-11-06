-- The PERFECT moment, on a PERFECT tap (Figma "Throw Eggs - Pop-up Text", frame "Perfect / Moment"): gold
-- flashes in from the screen's edges, a sunburst opens and turns behind a big "PERFECT!" that slams in with a
-- small shake and camera punch, "x1.5 THROW" rises under it and sparkles twinkle round it. About a second, and
-- it never holds up the throw. Display only: the distance bonus is the meter's, as before.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local PopText = require(ReplicatedStorage.Shared.PopText)
local Throw = require(ReplicatedStorage.Shared.Config.Throw)
local UiKit = require(ReplicatedStorage.Shared.UiKit)

local PerfectMoment = {}

local CENTRE_Y = 0.35 -- the word's middle, as a share of the screen's height
local LENGTH = 1.1 -- seconds
local GOLD = Color3.fromRGB(255, 200, 60)
local RAY = Color3.fromRGB(255, 210, 70) -- saturated, so the rays show against a bright sky
local SPARKLE = Color3.fromRGB(255, 247, 194)
local RAY_PAIRS = 8 -- each beam crosses the middle, so 16 rays
local RAY_LENGTH, RAY_WIDTH = 660, 34 -- design pixels (1280 x 720)
local SPIN = 25 -- degrees a second
local EDGE_DEPTH = 0.22 -- how far the edge flash reaches in, as a share of the screen
local EDGE_STRENGTH = 0.55
local SHAKE, SHAKE_TIME = 6, 0.15 -- pixels, seconds
local FOV_PUNCH = 4 -- degrees narrower, then back
-- Where the sparkles sit from the word's middle (design pixels) and how big they are.
local SPARKLES = { { -280, -100, 44 }, { 265, -122, 34 }, { 320, 80, 48 }, { -340, 80, 30 }, { -170, -158, 26 }, { 180, 135, 24 } }

local TITLE = { size = 140, outline = 12, shadow = 9 }
local DETAIL = { size = 40, outline = 5, shadow = 4 }

local TRACKS = {
	edge = { { 0, 0 }, { 0.06, 1, "out" }, { 0.5, 1 }, { 1, 0, "in" } },
	titleScale = { { 0, 2.2 }, { 0.12, 0.92, "in" }, { 0.22, 1, "out" }, { 0.7, 1 }, { 1, 1.15, "in" } },
	titleOpacity = { { 0, 0 }, { 0.05, 1 }, { 0.75, 1 }, { 1.05, 0, "in" } },
	titleRise = { { 0.7, 0 }, { 1.05, -40, "in" } },
	burstScale = { { 0, 0.3 }, { 0.25, 1, "out" } },
	burstOpacity = { { 0, 0 }, { 0.08, 1 }, { 0.7, 1 }, { 1, 0, "in" } },
	detailRise = { { 0.12, 14 }, { 0.3, 0, "out" } },
	detailOpacity = { { 0.12, 0 }, { 0.3, 1, "out" }, { 0.75, 1 }, { 1, 0, "in" } },
	sparkle = { { 0, 0 }, { 0.12, 1.25, "out" }, { 0.2, 1 } }, -- per sparkle, from its own start
	sparkleFade = { { 0.75, 1 }, { 1, 0, "in" } },
	fov = { { 0, 0 }, { 0.05, 1, "out" }, { 0.5, 0, "inOut" } },
}

local gui: ScreenGui? = nil
local stopRunning: (() -> ())? = nil

local function getGui(): ScreenGui
	if not gui then
		local layer = Instance.new("ScreenGui")
		layer.Name = "PerfectMoment"
		layer.IgnoreGuiInset = true
		layer.ScreenInsets = Enum.ScreenInsets.None -- the gold edges reach the screen's edges, past a phone's notch too
		layer.ResetOnSpawn = false
		layer.DisplayOrder = 6 -- under the pop-up text (7)
		layer.Parent = Players.LocalPlayer:WaitForChild("PlayerGui")
		gui = layer
	end
	return gui :: ScreenGui
end

-- A strip along one edge, gold at the edge and clear inwards.
local function edgeStrip(parent: Instance, rotation: number, position: UDim2, size: UDim2): UIGradient
	local strip = Instance.new("Frame")
	strip.BorderSizePixel = 0
	strip.BackgroundColor3 = GOLD
	strip.Position, strip.Size = position, size
	strip.Parent = parent
	local gradient = Instance.new("UIGradient")
	gradient.Rotation = rotation -- the gradient's start (the edge) is where it's solid
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

local function build(root: Frame, scale: number)
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
	wordsScale.Parent = words
	local title = PopText.word(words, "PERFECT!", TITLE, "gold")
	title.Rotation = -4
	local titleScale = Instance.new("UIScale")
	titleScale.Parent = title
	local detail = PopText.word(words, `x{Throw.meter.perfectMultiplier} THROW`, DETAIL, Color3.new(1, 1, 1))
	local detailY = (TITLE.size + DETAIL.size) / 2 + 8

	local sparkles = {}
	for _, spot in SPARKLES do
		-- A drawn diamond, not a "✦" character: phones have no font with that one and showed an empty box.
		local star = Instance.new("Frame")
		star.BorderSizePixel = 0
		star.BackgroundColor3 = SPARKLE
		star.AnchorPoint = Vector2.new(0.5, 0.5)
		star.Position = UDim2.fromOffset(spot[1], spot[2])
		star.Size = UDim2.fromOffset(spot[3] * 0.62, spot[3] * 0.62)
		star.Rotation = 45
		star.Parent = words
		UiKit.corner(star, 3)
		local stroke = Instance.new("UIStroke")
		stroke.Color = UiKit.INK
		stroke.Thickness = 2
		stroke.Parent = star
		local starScale = Instance.new("UIScale")
		starScale.Scale = 0
		starScale.Parent = star
		table.insert(sparkles, { label = star, stroke = stroke, scale = starScale })
	end

	return {
		edges = edges,
		burst = burst,
		burstScale = burstScale,
		rays = rays,
		words = words,
		wordsScale = wordsScale,
		title = title,
		titleScale = titleScale,
		detail = detail,
		detailY = detailY,
		sparkles = sparkles,
	}
end

function PerfectMoment.play()
	if stopRunning then
		stopRunning()
	end
	local root = Instance.new("Frame")
	root.Name = "Perfect"
	root.BackgroundTransparency = 1
	root.Size = UDim2.fromScale(1, 1)
	root.Parent = getGui()
	local scale = UiKit.scale()
	local parts = build(root, scale)
	parts.wordsScale.Scale = scale

	local camera = workspace.CurrentCamera
	local baseFov = camera.FieldOfView
	local started = os.clock()
	local connection: RBXScriptConnection

	local function stop()
		connection:Disconnect()
		root:Destroy()
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
		setEdge(parts.edges, sample(TRACKS.edge, t))

		parts.burst.Rotation = t * SPIN
		parts.burstScale.Scale = sample(TRACKS.burstScale, t)
		local rayOpacity = sample(TRACKS.burstOpacity, t)
		local strong = 1 - 0.9 * rayOpacity
		local raySequence = NumberSequence.new({
			NumberSequenceKeypoint.new(0, 1),
			NumberSequenceKeypoint.new(0.3, 1 - 0.6 * rayOpacity),
			NumberSequenceKeypoint.new(0.5, strong),
			NumberSequenceKeypoint.new(0.7, 1 - 0.6 * rayOpacity),
			NumberSequenceKeypoint.new(1, 1),
		})
		for _, gradient in parts.rays do
			gradient.Transparency = raySequence
		end

		local shake = if t < SHAKE_TIME then SHAKE * (1 - t / SHAKE_TIME) else 0
		parts.words.Position = UDim2.fromOffset(
			(math.random() * 2 - 1) * shake * scale,
			(math.random() * 2 - 1) * shake * scale + sample(TRACKS.titleRise, t) * scale
		)
		parts.titleScale.Scale = sample(TRACKS.titleScale, t)
		PopText.setOpacity(parts.title, sample(TRACKS.titleOpacity, t))
		parts.detail.Position = UDim2.fromOffset(0, parts.detailY + sample(TRACKS.detailRise, t))
		PopText.setOpacity(parts.detail, sample(TRACKS.detailOpacity, t))

		local fade = sample(TRACKS.sparkleFade, t)
		for index, sparkle in parts.sparkles do
			local own = t - 0.05 * index
			sparkle.scale.Scale = if own > 0 then sample(TRACKS.sparkle, own) else 0
			sparkle.label.Rotation = 45 + t * 90 * (if index % 2 == 0 then 1 else -1)
			sparkle.label.BackgroundTransparency = 1 - fade
			sparkle.stroke.Transparency = 1 - fade
		end

		camera.FieldOfView = baseFov - FOV_PUNCH * sample(TRACKS.fov, t)
	end)
end

return PerfectMoment
