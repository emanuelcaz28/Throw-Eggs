-- The throw's camera work and effects, as in the owner's recording of the reference game (docs/GAME_SPEC.md
-- section 7): the dip to black onto the throw spot, the camera whipping round the thrower, the flight camera that
-- climbs high behind the egg and drops low at the end, the white streak behind the egg, the luck panel, and the
-- white ring and dust where it lands. Timings and positions live in Config/Throw. ThrowController drives it.
local Debris = game:GetService("Debris")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")

local Biomes = require(ReplicatedStorage.Shared.Config.Biomes)
local FlightFx = require(ReplicatedStorage.Shared.Config.FlightFx)
local Format = require(ReplicatedStorage.Shared.Format)
local Throw = require(ReplicatedStorage.Shared.Config.Throw)
local UiKit = require(ReplicatedStorage.Shared.UiKit)

local ThrowCinematic = {}

local luckHolder: Frame? = nil -- the luck panel, once built (isLuckPanelShown)

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

local function streak(egg: BasePart, width: number): Trail
	local top = Instance.new("Attachment")
	top.Position = Vector3.new(0, width / 2, 0)
	top.Parent = egg
	local bottom = Instance.new("Attachment")
	bottom.Position = Vector3.new(0, -width / 2, 0)
	bottom.Parent = egg
	local trail = Instance.new("Trail")
	trail.Attachment0 = top
	trail.Attachment1 = bottom
	trail.FaceCamera = true
	trail.Enabled = false
	trail.Parent = egg
	return trail
end

-- The streak behind the egg, off until the egg leaves the hand: a white comet tapering to a point (Config/FlightFx
-- trail), with a wide soft glow round it that copies its colour and follows it on and off.
function ThrowCinematic.addTrail(egg: BasePart): Trail
	local settings = Throw.flight.trail
	local look = FlightFx.trail
	local trail = streak(egg, settings.width)
	trail.Color = ColorSequence.new(Color3.new(1, 1, 1))
	trail.Transparency = NumberSequence.new({
		NumberSequenceKeypoint.new(0, settings.transparency),
		NumberSequenceKeypoint.new(0.6, (settings.transparency + 1) / 2),
		NumberSequenceKeypoint.new(1, 1),
	})
	trail.WidthScale = NumberSequence.new(1, look.taper)
	trail.Lifetime = settings.lifetime
	trail.LightEmission = 0.6
	trail.Name = "Streak"

	local glow = streak(egg, look.glow.width)
	glow.Name = "StreakGlow"
	glow.Transparency = NumberSequence.new(look.glow.transparency, 1)
	glow.WidthScale = NumberSequence.new(1, 0.3)
	glow.Lifetime = look.glow.lifetime
	glow.LightEmission = 1
	glow.Color = trail.Color
	trail:GetPropertyChangedSignal("Color"):Connect(function()
		glow.Color = trail.Color
	end)
	trail:GetPropertyChangedSignal("Enabled"):Connect(function()
		glow.Enabled = trail.Enabled
	end)
	return trail
end

-- Leans the streak's tail to the colour of the world the egg is over; the head stays white.
function ThrowCinematic.tintTrail(trail: Trail, color: Color3)
	trail.Color = ColorSequence.new(Color3.new(1, 1, 1), Color3.new(1, 1, 1):Lerp(color, FlightFx.trail.tint))
end

-- The egg has crossed into a new world: a ring in the world's colour bursts out round it and rides along with it, and
-- it leaves a short wake of sparks behind (Config/FlightFx gate).
function ThrowCinematic.worldGate(egg: BasePart, color: Color3)
	local settings = FlightFx.gate
	local direction = Throw.lane.direction
	-- A thin disc facing down the lane (a cylinder's round faces are on its X axis).
	local facing = CFrame.Angles(0, math.atan2(-direction.X, -direction.Z) + math.pi / 2, 0)
	local ring = Instance.new("Part")
	ring.Name = "WorldGate"
	ring.Shape = Enum.PartType.Cylinder
	ring.Anchored = true
	ring.CanCollide = false
	ring.CanQuery = false
	ring.CanTouch = false
	ring.CastShadow = false
	ring.Material = Enum.Material.ForceField -- glows brightest at its edge, like a ring
	ring.Color = color:Lerp(Color3.new(1, 1, 1), 0.2)
	ring.Transparency = settings.startTransparency
	ring.Size = Vector3.new(0.2, 2, 2)

	local sparks = Instance.new("ParticleEmitter")
	sparks.Texture = "rbxasset://textures/particles/sparkles_main.dds"
	sparks.Color = ColorSequence.new(Color3.new(1, 1, 1), color)
	sparks.LightEmission = 1
	sparks.Size = NumberSequence.new({ NumberSequenceKeypoint.new(0, 1.4), NumberSequenceKeypoint.new(1, 0) })
	sparks.Transparency = NumberSequence.new(0, 1)
	sparks.Lifetime = NumberRange.new(0.35, 0.7)
	sparks.Speed = NumberRange.new(8, 22)
	sparks.SpreadAngle = Vector2.new(180, 180)
	sparks.Drag = 4
	sparks.Rate = settings.sparks / settings.sparkTime
	sparks.Parent = ring

	local function place()
		ring.CFrame = CFrame.new(egg.Position - direction * settings.behind) * facing
	end
	place()
	ring.Parent = workspace
	local info = TweenInfo.new(settings.time, Enum.EasingStyle.Quart, Enum.EasingDirection.Out)
	TweenService:Create(ring, info, { Size = Vector3.new(0.2, settings.radius * 2, settings.radius * 2), Transparency = 1 }):Play()
	local follow = RunService.RenderStepped:Connect(function()
		if egg.Parent then
			place()
		end
	end)
	task.delay(settings.sparkTime, function()
		sparks.Enabled = false
	end)
	task.delay(settings.time, function()
		follow:Disconnect()
		ring.Transparency = 1
		Debris:AddItem(ring, 0.8) -- the last sparks fade out
	end)
end

-- The egg bursts through the Last Door into The Deep End: the screen flashes mint-white, which also hides the camera
-- passing through the door, then clears on the world behind it.
function ThrowCinematic.doorBurst()
	local gui = Instance.new("ScreenGui")
	gui.Name = "DoorBurst"
	gui.IgnoreGuiInset = true
	gui.ScreenInsets = Enum.ScreenInsets.None
	gui.DisplayOrder = 5
	local flash = Instance.new("Frame")
	flash.BorderSizePixel = 0
	flash.BackgroundColor3 = Color3.fromRGB(214, 255, 244)
	flash.Size = UDim2.fromScale(1, 1)
	flash.Parent = gui
	gui.Parent = Players.LocalPlayer:WaitForChild("PlayerGui")
	TweenService:Create(flash, TweenInfo.new(0.55, Enum.EasingStyle.Quad, Enum.EasingDirection.In), { BackgroundTransparency = 1 }):Play()
	Debris:AddItem(gui, 0.6)
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
	luckHolder = holder
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
	local shownCount = 0 -- goes up on every show, so a fade-out from an earlier throw can't hide this one
	local fades: { Tween } = {}

	local function clearFade()
		for _, tween in fades do
			tween:Cancel()
		end
		table.clear(fades)
		for _, object in holder:GetDescendants() do
			if object:IsA("TextLabel") then
				object.TextTransparency = 0
			elseif object:IsA("UIStroke") then
				object.Transparency = 0
			end
		end
	end

	function luckPanel.show(shown: boolean)
		shownCount += 1
		clearFade()
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
		clearFade()
		for _, object in holder:GetDescendants() do
			local goal = if object:IsA("TextLabel") then { TextTransparency = 1 }
				elseif object:IsA("UIStroke") then { Transparency = 1 }
				else nil
			if goal then
				local tween = TweenService:Create(object, info, goal)
				tween:Play()
				table.insert(fades, tween)
			end
		end
		local fadingShow = shownCount
		task.delay(seconds, function()
			if shownCount == fadingShow then -- not shown again for a new throw in the meantime
				holder.Visible = false
				clearFade()
			end
		end)
	end

	return luckPanel
end

-- Whether this player's luck panel is on screen (their egg is in the air or just landed). The lucky catch banner waits
-- for it, as it would cover the luck and the world's name (LuckyBannerController).
function ThrowCinematic.isLuckPanelShown(): boolean
	return luckHolder ~= nil and luckHolder.Visible
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
