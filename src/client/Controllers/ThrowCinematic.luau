-- The throw's camera work and effects, as in the owner's recording of the reference game (docs/GAME_SPEC.md
-- section 7): the dip to black onto the throw spot, the camera whipping round the thrower, the flight camera that
-- climbs high behind the egg and drops low at the end, the white streak behind the egg, the luck panel, and the
-- white ring and dust where it lands. Timings and positions live in Config/Throw. ThrowController drives it.
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")

local Biomes = require(ReplicatedStorage.Shared.Config.Biomes)
local Format = require(ReplicatedStorage.Shared.Format)
local Throw = require(ReplicatedStorage.Shared.Config.Throw)
local UiKit = require(ReplicatedStorage.Shared.UiKit)

local ThrowCinematic = {}

local CORRIDOR_LOOK = 30 -- studs ahead the camera aims when it looks down the corridor
local CHEST = Vector3.new(0, 1.5, 0) -- from the root, where the camera looks when it faces the thrower
local STANDARD_BODY = 4 -- a standard avatar's hip height plus its root's height, in studs

-- The thrower's size against a standard avatar (1). The aim and wind-up camera keep this much further out, so a
-- big avatar doesn't fill the screen; smaller ones keep the standard framing.
local body = 1

local function smooth(u: number): number
	u = math.clamp(u, 0, 1)
	return u * u * (3 - 2 * u)
end

local function lerp(a: number, b: number, u: number): number
	return a + (b - a) * u
end

-- The shortest way round from angle a to angle b, in radians.
local function angleTowards(a: number, b: number): number
	return (b - a + math.pi) % (2 * math.pi) - math.pi
end

local function headingOf(direction: Vector3): (number, number)
	return math.atan2(-direction.X, -direction.Z), math.asin(math.clamp(direction.Unit.Y, -1, 1))
end

local function directionOf(heading: number, pitch: number): Vector3
	return Vector3.new(-math.sin(heading) * math.cos(pitch), math.sin(pitch), -math.cos(heading) * math.cos(pitch))
end

-- Where the thrower stands: in from the throw line, across where they stepped on (kept off the sides), facing
-- down the corridor, standing on the platform.
function ThrowCinematic.throwSpot(root: BasePart, humanoid: Humanoid): CFrame
	local lane, aim = Throw.lane, Throw.aim
	local half = lane.zoneSize.X / 2 - aim.spotMargin
	local x = math.clamp(root.Position.X, lane.zoneCenter.X - half, lane.zoneCenter.X + half)
	local y = lane.zoneCenter.Y + humanoid.HipHeight + root.Size.Y / 2
	local position = Vector3.new(x, y, lane.origin.Z + aim.spotZ)
	return CFrame.lookAt(position, position + lane.direction)
end

function ThrowCinematic.setThrower(character: Model)
	local humanoid = character:FindFirstChildOfClass("Humanoid")
	local root = character:FindFirstChild("HumanoidRootPart") :: BasePart?
	body = if humanoid and root then math.clamp((humanoid.HipHeight + root.Size.Y) / STANDARD_BODY, 1, 3) else 1
end

-- The camera round the thrower at a time after the tap (Config/Throw windup.camera). Before the tap it holds the
-- first key, the aim framing.
function ThrowCinematic.windupCamera(spot: CFrame, elapsed: number): CFrame
	local keys = Throw.windup.camera
	local a, b = keys[1], keys[1]
	for index = 1, #keys - 1 do
		if elapsed >= keys[index].time then
			a, b = keys[index], keys[index + 1]
		end
	end
	local u = if b.time > a.time then smooth((elapsed - a.time) / (b.time - a.time)) else 1
	local yaw = math.rad(lerp(a.yaw, b.yaw, u))
	local orbit = spot * CFrame.Angles(0, -yaw, 0) -- clockwise seen from above
	local eye = orbit:PointToWorldSpace(Vector3.new(lerp(a.side, b.side, u), lerp(a.height, b.height, u), lerp(a.distance, b.distance, u)) * body)

	-- Turns between looking at the thrower and looking down the corridor, the short way round.
	local chestHeading, chestPitch = headingOf(spot.Position + CHEST * body - eye)
	local laneHeading, lanePitch = headingOf(spot.LookVector)
	lanePitch += math.rad(Throw.aim.cameraPitch)
	local look = lerp(a.look, b.look, u)
	local heading = chestHeading + angleTowards(chestHeading, laneHeading) * look
	local pitch = lerp(chestPitch, lanePitch, look)
	return CFrame.lookAt(eye, eye + directionOf(heading, pitch) * CORRIDOR_LOOK)
end

-- The flight camera. It starts where the wind-up left it (from), climbs high behind the egg over riseTime, looking
-- down the valley with the egg low in the middle of the screen, and comes down low behind it over the last fallTime
-- of the flight (Config/Throw flight.camera).
function ThrowCinematic.flightCamera(from: CFrame, egg: Vector3, elapsed: number, duration: number): CFrame
	local settings = Throw.flight.camera
	local high, low = settings.high, settings.low
	local fall = smooth((elapsed - (duration - settings.fallTime)) / settings.fallTime)
	local direction = Throw.lane.direction
	local eye = egg - direction * lerp(high.behind, low.behind, fall) + Vector3.new(0, lerp(high.above, low.above, fall), 0)
	local target = egg + direction * lerp(high.ahead, low.ahead, fall)
	-- Never below the corridor floor, however low the egg comes in.
	eye = Vector3.new(eye.X, math.max(eye.Y, Throw.lane.floorY + 2), eye.Z)
	return from:Lerp(CFrame.lookAt(eye, target), smooth(elapsed / settings.riseTime))
end

-- The white streak behind the egg, off until the egg leaves the hand.
function ThrowCinematic.addTrail(egg: BasePart): Trail
	local settings = Throw.flight.trail
	local top = Instance.new("Attachment")
	top.Position = Vector3.new(0, settings.width / 2, 0)
	top.Parent = egg
	local bottom = Instance.new("Attachment")
	bottom.Position = Vector3.new(0, -settings.width / 2, 0)
	bottom.Parent = egg
	local trail = Instance.new("Trail")
	trail.Attachment0 = top
	trail.Attachment1 = bottom
	trail.Color = ColorSequence.new(Color3.new(1, 1, 1))
	trail.Transparency = NumberSequence.new(settings.transparency, 1)
	trail.Lifetime = settings.lifetime
	trail.FaceCamera = true
	trail.LightEmission = 0.4
	trail.Enabled = false
	trail.Parent = egg
	return trail
end

-- A flat white ring flashing out on the ground, then a puff of dust.
function ThrowCinematic.landingEffects(ground: Vector3)
	local settings = Throw.landing
	local ring = Instance.new("Part")
	ring.Name = "LandingRing"
	ring.Shape = Enum.PartType.Cylinder
	ring.Anchored = true
	ring.CanCollide = false
	ring.CanQuery = false
	ring.CanTouch = false
	ring.CastShadow = false
	ring.Material = Enum.Material.Neon
	ring.Color = Color3.new(1, 1, 1)
	ring.Transparency = 0.2
	ring.Size = Vector3.new(0.1, 1, 1)
	ring.CFrame = CFrame.new(ground + Vector3.new(0, 0.08, 0)) * CFrame.Angles(0, 0, math.pi / 2)
	ring.Parent = workspace
	local grow = TweenInfo.new(settings.ringTime, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)
	TweenService:Create(ring, grow, { Size = Vector3.new(0.1, settings.ringRadius * 2, settings.ringRadius * 2), Transparency = 1 }):Play()

	local dust = Instance.new("Part")
	dust.Name = "LandingDust"
	dust.Anchored = true
	dust.CanCollide = false
	dust.CanQuery = false
	dust.CanTouch = false
	dust.Transparency = 1
	dust.Size = Vector3.one
	dust.CFrame = CFrame.new(ground + Vector3.new(0, 1, 0))
	dust.Parent = workspace
	local puff = Instance.new("ParticleEmitter")
	puff.Texture = "rbxasset://textures/particles/smoke_main.dds"
	puff.Color = ColorSequence.new(settings.dustColor)
	puff.Transparency = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.35), NumberSequenceKeypoint.new(1, 1) })
	puff.Size = NumberSequence.new({ NumberSequenceKeypoint.new(0, 3), NumberSequenceKeypoint.new(1, 8) })
	puff.Lifetime = NumberRange.new(0.8, 1.3)
	puff.Speed = NumberRange.new(3, 7)
	puff.SpreadAngle = Vector2.new(70, 70)
	puff.Rotation = NumberRange.new(0, 360)
	puff.RotSpeed = NumberRange.new(-40, 40)
	puff.Acceleration = Vector3.new(0, 2, 0)
	puff.Drag = 3
	puff.EmissionDirection = Enum.NormalId.Top
	puff.Enabled = false
	puff.Parent = dust
	task.delay(settings.dustDelay, function()
		puff:Emit(16)
	end)
	task.delay(2, function()
		ring:Destroy()
		dust:Destroy()
	end)
end

-- The luck panel at the top of the screen in flight: the luck number in a see-through rounded panel tinted for the
-- world the egg is over, and under it a dark strip with that world's name in its colour.
function ThrowCinematic.buildLuckPanel(gui: ScreenGui)
	-- Plain text, no panel [Owner, 2026-11-06]: the luck number big, LUCK under it, then the world's name
	-- in its colour. Thick dark outlines keep it readable over any world.
	local holder = Instance.new("Frame")
	holder.Name = "LuckPanel"
	holder.AnchorPoint = Vector2.new(0.5, 0)
	holder.Position = UDim2.new(0.5, 0, 0, 10)
	holder.Size = UDim2.fromOffset(640, 210)
	holder.BackgroundTransparency = 1
	holder.Visible = false
	holder.Parent = gui
	local scale = Instance.new("UIScale")
	scale.Scale = UiKit.scale()
	scale.Parent = holder

	local panel = Instance.new("Frame")
	panel.Name = "Texts"
	panel.Size = UDim2.fromScale(1, 1)
	panel.BackgroundTransparency = 1
	panel.Parent = holder
	local pop = Instance.new("UIScale")
	pop.Parent = panel

	local number = UiKit.text(panel, "1.00X", 92, UiKit.TEXT)
	number.Size = UDim2.new(1, 0, 0, 100)
	number:FindFirstChildOfClass("UIStroke").Thickness = 8
	local tint = Instance.new("UIGradient")
	tint.Rotation = 90
	tint.Parent = number

	local word = UiKit.text(panel, "LUCK", 32, UiKit.TEXT)
	word.Position = UDim2.fromOffset(0, 92)
	word.Size = UDim2.new(1, 0, 0, 38)
	word:FindFirstChildOfClass("UIStroke").Thickness = 5

	local world = UiKit.text(panel, "", 58, Biomes[1].color)
	world.Position = UDim2.fromOffset(0, 136)
	world.Size = UDim2.new(1, 0, 0, 66)
	world:FindFirstChildOfClass("UIStroke").Thickness = 7

	local current = nil
	local luckPanel = {}

	function luckPanel.show(shown: boolean)
		holder.Visible = shown
		current = nil
	end

	-- Without a biome only the number changes.
	function luckPanel.set(luck: number, biome)
		-- Two decimals while it's small, then 1.5K once a lucky throw takes it past a thousand.
		number.Text = if luck < 1000 then string.format("%.2fX", luck) else `{Format.short(luck)}X`
		if biome == nil or biome == current then
			return
		end
		current = biome
		local color = biome.color
		world.Text = biome.name
		world.TextColor3 = color:Lerp(Color3.new(1, 1, 1), 0.3)
		tint.Color = ColorSequence.new(Color3.new(1, 1, 1), color:Lerp(Color3.new(1, 1, 1), 0.6))
		-- A quick pop each time the egg crosses into a new world.
		pop.Scale = 1.2
		TweenService:Create(pop, TweenInfo.new(0.35, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Scale = 1 }):Play()
	end

	-- Fades it away (the landing's cut to black) and hides it.
	function luckPanel.fadeOut(seconds: number)
		local info = TweenInfo.new(seconds)
		for _, object in holder:GetDescendants() do
			if object:IsA("TextLabel") then
				TweenService:Create(object, info, { TextTransparency = 1 }):Play()
			elseif object:IsA("UIStroke") then
				TweenService:Create(object, info, { Transparency = 1 }):Play()
			end
		end
		task.delay(seconds, function()
			holder.Visible = false
			for _, object in holder:GetDescendants() do
				if object:IsA("TextLabel") then
					object.TextTransparency = 0
				elseif object:IsA("UIStroke") then
					object.Transparency = 0
				end
			end
		end)
	end

	return luckPanel
end

-- A full-screen black layer over everything, for the dips to black.
function ThrowCinematic.buildFade(parent: Instance): Frame
	local gui = Instance.new("ScreenGui")
	gui.Name = "ThrowFade"
	gui.IgnoreGuiInset = true
	gui.ScreenInsets = Enum.ScreenInsets.None -- black edge to edge, past a phone's notch too
	gui.ResetOnSpawn = false
	gui.DisplayOrder = 50
	gui.Parent = parent
	local black = Instance.new("Frame")
	black.Size = UDim2.fromScale(1, 1)
	black.BackgroundColor3 = Color3.new(0, 0, 0)
	black.BackgroundTransparency = 1
	black.BorderSizePixel = 0
	black.Parent = gui
	return black
end

-- Fades the black layer in (opaque) or out, and waits for it.
function ThrowCinematic.fade(black: Frame, opaque: boolean, seconds: number)
	local tween = TweenService:Create(black, TweenInfo.new(seconds, Enum.EasingStyle.Sine), { BackgroundTransparency = if opaque then 0 else 1 })
	tween:Play()
	task.wait(seconds)
end

return ThrowCinematic
