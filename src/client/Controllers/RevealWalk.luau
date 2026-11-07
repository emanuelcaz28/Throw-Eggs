-- The monster's walk to the egg, seen through its own eyes (docs/GAME_SPEC.md section 7, "The walk"). After the
-- landing the screen cuts to black and opens on the view from the caught monster's eyes, already walking up the
-- corridor to the egg, each step swaying the view and tilting the horizon; then it cuts to black again for the
-- shot from its feet. No monster shows: it's the camera doing the walking. [Owner, 2026-11-07] It's slow and goes all
-- the way: over the last of the walk the monster lowers its head to the egg, so even the biggest ends with its face at it.
-- How it looks depends on the catch: rarer catches start further from the egg, bigger monsters see from higher up
-- (their real eye height at their real size) and take slower, heavier steps, swimmers glide, and a colour mutation
-- glows round the screen's edges in its colour. It opens and ends with a blink. Display only: the server has already rolled the catch.
-- Numbers live in Config/Reveal walk. RevealController plays it.
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")

local Biomes = require(ReplicatedStorage.Shared.Config.Biomes)
local DinoModel = require(ReplicatedStorage.Shared.DinoModel)
local Map = require(ReplicatedStorage.Shared.Config.Map)
local Reveal = require(ReplicatedStorage.Shared.Config.Reveal)
local Roles = require(ReplicatedStorage.Shared.Roles)
local Throw = require(ReplicatedStorage.Shared.Config.Throw)

local RevealWalk = {}

local settings = Reveal.walk
local EGG_MIDDLE = 1.5 -- studs above the ground the camera aims at, the egg's middle
local EGG_HEIGHT = 3 -- studs, about
local FALLBACK_EYE_SHARE = 0.85 -- of its height, for a model with no Pupil parts
local SWIM_PACE = 0.5 -- swimmers sway at this share of a walker's step rate
local MARKER_LIFT = 0.3 -- share of the way from the egg to the eyes the far-egg dot hangs

local function lerp(a: number, b: number, u: number): number
	return a + (b - a) * u
end

-- Where value sits between low (0) and high (1), evenly on a log scale.
local function logShare(value: number, low: number, high: number): number
	return math.clamp(math.log(math.max(value, low) / low) / math.log(high / low), 0, 1)
end

local function tween(instance: Instance, time: number, goal)
	local created = TweenService:Create(instance, TweenInfo.new(time, Enum.EasingStyle.Sine), goal)
	created:Play()
	return created
end

-- Each monster's eye height at its model's own size (the middle of its Pupil parts, above its feet), how wide it is,
-- and whether it has no feet to step on (a swimmer's Swim bone, a snake's Slither1), so it glides, measured once from
-- its model.
local bodies = {}
local function bodyOf(dinoId: string)
	local body = bodies[dinoId]
	if body then
		return body
	end
	local model = DinoModel.build(dinoId, nil, Vector3.zero, 1)
	local total, count, swims = 0, 0, false
	for _, item in model:GetDescendants() do
		if item:IsA("BasePart") and Roles.of(item) == "Pupil" then
			total += item.Position.Y
			count += 1
		elseif item:IsA("Bone") and (item.Name == "Swim" or item.Name == "Slither1") then
			swims = true
		end
	end
	local eye = total / math.max(count, 1)
	local box, size = model:GetBoundingBox()
	if count == 0 then
		eye = (box.Position.Y + size.Y / 2) * FALLBACK_EYE_SHARE
	end
	model:Destroy()
	body = { eye = math.max(eye, 0.5), swims = swims, width = size.X }
	bodies[dinoId] = body
	return body
end

export type Plan = {
	eye: number, -- studs above the ground
	lowest: number, -- how far above the ground its head ends, lowered to the egg
	width: number, -- studs across, at its real size
	ground: Vector3, -- under the egg
	start: Vector3, -- on the ground, under the eyes at the start
	finish: Vector3, -- on the ground, under the eyes at the end
	approach: Vector3, -- the way it walks, flat
	duration: number,
	bigness: number, -- 0 for the first map's standard size, 1 at Config bigScale
	rarity: number, -- 0 for the commonest catch, 1 for the rarest
	swims: boolean,
	color: Color3?, -- the colour mutation's, for the rings round the screen
}

-- Works out the walk for a catch whose egg lies on the ground at `ground`. `color` is its colour mutation's colour.
function RevealWalk.plan(catch, ground: Vector3, color: Color3?, random: Random?): Plan
	random = random or Random.new()
	local body = bodyOf(catch.id)
	local scale = DinoModel.statueScale(catch.id, catch.size)
	local eye = body.eye * scale
	local rarity = logShare(catch.oneIn, settings.commonOneIn, settings.rarestOneIn)
	local bigness = logShare(scale, 1, settings.bigScale)

	-- How far away it starts and stops, from how far below its eyes it sees the egg.
	local startAngle = math.rad(lerp(settings.nearAngle, settings.farAngle, rarity) + settings.bigAngle * bigness)
	local lowest = math.min(eye, EGG_HEIGHT * settings.bowEggs + eye * settings.bowEye)
	local endDistance = math.max(lowest * settings.endReach, settings.minEndDistance)
	local shortest = endDistance * (1 + settings.minWalkShare)
	local startDistance = math.max(math.min(eye / math.tan(startAngle), settings.maxStartDistance), shortest)

	-- Along the corridor from the thrower's side, or from the far side when there's no room behind the egg. Eyes
	-- above the walls see over everything, so only lower ones have to stay inside the corridor.
	local lane = Throw.lane
	local forward = Vector3.new(lane.direction.X, 0, lane.direction.Z).Unit
	local along = (ground - lane.origin):Dot(forward)
	local roomBehind = along - settings.backMargin
	local roomAhead = Biomes[#Biomes].endDist + Map.corridor.extra - along - settings.backMargin
	local overWalls = ground.Y + eye > Map.walls.rimY
	local fromBehind = startDistance <= roomBehind or roomBehind >= roomAhead
	if not overWalls then
		startDistance = math.max(math.min(startDistance, if fromBehind then roomBehind else roomAhead), shortest)
	end
	local heading = if fromBehind then forward else -forward
	local yaw = math.rad((random:NextNumber() * 2 - 1) * settings.approachAngle)
	local start = ground - CFrame.Angles(0, yaw, 0):VectorToWorldSpace(heading) * startDistance
	if not overWalls then
		local across = forward:Cross(Vector3.yAxis)
		local side = (start - lane.origin):Dot(across)
		local limit = lane.width / 2 - settings.sideMargin
		start -= across * (side - math.clamp(side, -limit, limit))
	end
	local flat = Vector3.new(ground.X - start.X, 0, ground.Z - start.Z)
	local approach = flat.Unit

	return {
		eye = eye,
		lowest = lowest,
		width = body.width * scale,
		ground = ground,
		start = Vector3.new(start.X, ground.Y, start.Z),
		finish = ground - approach * endDistance,
		approach = approach,
		duration = lerp(settings.minTime, settings.maxTime, rarity) + settings.bigExtraTime * bigness,
		bigness = bigness,
		rarity = rarity,
		swims = body.swims,
		color = color,
	}
end

-- The share of the way walked at u (0 to 1 of the walk's time), braking all the way to the egg, and how fast that
-- share grows per unit of u.
local function walked(u: number): (number, number)
	u = math.clamp(u, 0, 1)
	local power = settings.slowPower
	return 1 - (1 - u) ^ power, power * (1 - u) ^ (power - 1)
end

local function smoother(u: number): number
	u = math.clamp(u, 0, 1)
	return u * u * u * (u * (u * 6 - 15) + 10)
end

-- The eyes at a moment of the walk, `u` of the way through its time: `share` of the way walked, `steps` taken so far (a
-- footfall at each whole number) and `sinceFootfall` seconds since the last one. Near the end the head goes down to the
-- egg and the sway dies away.
function RevealWalk.cameraAt(plan: Plan, u: number, share: number, steps: number, sinceFootfall: number): CFrame
	local bowed = smoother((u - settings.bowFrom) / (1 - settings.bowFrom))
	local calm = 1 - smoother((u - settings.calmFrom) / (1 - settings.calmFrom))
	local eye = lerp(plan.eye, plan.lowest, bowed)
	local swing = math.sin(math.pi * steps) * calm -- one way on one step, the other way on the next
	local lift = (if plan.swims then 0.5 * math.sin(2 * math.pi * steps) else math.abs(swing) - 0.5) * calm -- lowest at a footfall
	-- A footfall jolts the view down, then it shakes and settles.
	local jolt = 0
	if not plan.swims and sinceFootfall < settings.thudTime * 2 then
		jolt = math.exp(-4 * sinceFootfall / settings.thudTime) * math.cos(sinceFootfall * 45) * calm
	end

	local across = plan.approach:Cross(Vector3.yAxis)
	local height = eye + lift * settings.bob * eye - math.max(jolt, 0) * settings.thudDrop * plan.bigness * eye
	local position = plan.start:Lerp(plan.finish, share) + across * (swing * settings.sway * eye) + Vector3.new(0, height, 0)

	-- Looks at the egg, keeping it a little below the middle of the screen.
	local toEgg = plan.ground + Vector3.new(0, EGG_MIDDLE, 0) - position
	local flatDistance = Vector3.new(toEgg.X, 0, toEgg.Z).Magnitude
	local heading = math.atan2(-toEgg.X, -toEgg.Z)
	local down = math.atan2(-toEgg.Y, flatDistance)
	local pitch = down - math.min(down * settings.aimBelow, math.rad(settings.maxAimBelow))
	pitch += jolt * math.rad(lerp(settings.thudAngle, settings.bigThudAngle, plan.bigness) + settings.rareThudAngle * plan.rarity)
	heading += math.rad(settings.turn) * math.sin(math.pi * steps - 0.6) * calm
	local roll = math.rad(lerp(settings.tilt, settings.bigTilt, plan.bigness)) * swing
	return CFrame.new(position) * CFrame.Angles(0, heading, 0) * CFrame.Angles(-pitch, 0, 0) * CFrame.Angles(0, 0, roll)
end

-- What the screen looks like through the monster's eyes: eyelids at the top and bottom that blink open at the
-- start and shut at the end, and for a colour mutation a soft round glow in its colour at the edges with sparkles
-- twinkling in it. Hidden until shown.
local sparkleLoop: RBXScriptConnection? = nil

local function sparkle(parent: Instance): Frame
	local holder = Instance.new("Frame")
	holder.Name = "Sparkle"
	holder.AnchorPoint = Vector2.new(0.5, 0.5)
	holder.BackgroundTransparency = 1
	holder.Parent = parent
	Instance.new("UIScale").Parent = holder
	-- Two thin bars crossing, fading out towards their tips: a four-pointed twinkle.
	for _, wide in { true, false } do
		local bar = Instance.new("Frame")
		bar.AnchorPoint = Vector2.new(0.5, 0.5)
		bar.Position = UDim2.fromScale(0.5, 0.5)
		bar.Size = if wide then UDim2.fromScale(1, 0.16) else UDim2.fromScale(0.16, 1)
		bar.BorderSizePixel = 0
		bar.Parent = holder
		local corner = Instance.new("UICorner")
		corner.CornerRadius = UDim.new(0.5, 0)
		corner.Parent = bar
		local fade = Instance.new("UIGradient")
		fade.Transparency = NumberSequence.new({
			NumberSequenceKeypoint.new(0, 1),
			NumberSequenceKeypoint.new(0.5, 0),
			NumberSequenceKeypoint.new(1, 1),
		})
		fade.Rotation = if wide then 0 else 90
		fade.Parent = bar
	end
	return holder
end

function RevealWalk.buildGlow(parent: Instance): Frame
	local glow = settings.glow
	local eyes = settings.eyes
	local holder = Instance.new("Frame")
	holder.Name = "WalkEyes"
	holder.Size = UDim2.fromScale(1, 1)
	holder.BackgroundTransparency = 1
	holder.Visible = false
	holder.ZIndex = 1
	holder.Parent = parent

	-- The colour glow, kept round on any screen: sized against the screen's width only.
	local colour = Instance.new("Frame")
	colour.Name = "Glow"
	colour.Size = UDim2.fromScale(1, 1)
	colour.BackgroundTransparency = 1
	colour.ZIndex = 1
	colour.Parent = holder
	local dark = Instance.new("ImageLabel")
	dark.Name = "Dark"
	dark.AnchorPoint = Vector2.new(0.5, 0.5)
	dark.Position = UDim2.fromScale(0.5, 0.5)
	dark.BackgroundTransparency = 1
	dark.Image = glow.darkImage
	dark.ImageTransparency = 1
	dark.Parent = colour
	for index = 1, glow.bands do
		local u = (index - 1) / glow.bands
		local band = Instance.new("Frame")
		band.Name = `Band{index}`
		band.AnchorPoint = Vector2.new(0.5, 0.5)
		band.Position = UDim2.fromScale(0.5, 0.5)
		band:SetAttribute("Size", lerp(glow.innerSize, glow.outerSize, u))
		band.BackgroundTransparency = 1
		band.Parent = colour
		local corner = Instance.new("UICorner")
		corner.CornerRadius = UDim.new(0.5, 0)
		corner.Parent = band
		local stroke = Instance.new("UIStroke")
		stroke.ApplyStrokeMode = Enum.ApplyStrokeMode.Border
		stroke.Transparency = 1
		stroke:SetAttribute("Shown", lerp(glow.innerTransparency, glow.outerTransparency, u ^ 1.5))
		stroke.Parent = band
	end
	for index = 1, glow.sparkles do
		sparkle(colour).Name = `Sparkle{index}`
	end

	-- The eyelids: the edges of two huge dark circles above and below, shut to start with (sized when shown).
	for _, top in { true, false } do
		local lid = Instance.new("Frame")
		lid.Name = if top then "LidTop" else "LidBottom"
		lid.AnchorPoint = Vector2.new(0.5, if top then 1 else 0)
		lid.BackgroundColor3 = eyes.color
		lid.BorderSizePixel = 0
		lid.ZIndex = 2
		lid.Parent = holder
		local corner = Instance.new("UICorner")
		corner.CornerRadius = UDim.new(0.5, 0)
		corner.Parent = lid
	end
	return holder
end

-- The size of the screen the eyes are drawn on: their own layer's, so they always fit what they have to cover.
local function screenOf(holder: Frame): Vector2
	local size = holder.AbsoluteSize
	return if size.X > 1 and size.Y > 1 then size else workspace.CurrentCamera.ViewportSize
end

-- Where the lids sit to cover `cover` of the screen's height each in the middle; shut, they reach past the middle
-- by as much as their edges curve up at the corners, so no gap shows.
local function lidsAt(holder: Frame, cover: number?): ({ [Instance]: UDim2 })
	local viewport = screenOf(holder)
	local radius = settings.eyes.curve * viewport.X / 2
	local lift = radius - math.sqrt(radius ^ 2 - (viewport.X / 2) ^ 2)
	local reach = if cover then cover * viewport.Y else viewport.Y / 2 + lift + 8
	return {
		[holder.LidTop] = UDim2.new(0.5, 0, 0, reach),
		[holder.LidBottom] = UDim2.new(0.5, 0, 1, -reach),
	}
end

local function moveLids(holder: Frame, cover: number?, time: number): Tween
	local last = nil
	for lid, position in lidsAt(holder, cover) do
		last = TweenService:Create(lid, TweenInfo.new(time, Enum.EasingStyle.Quad, Enum.EasingDirection.InOut), { Position = position })
		last:Play()
	end
	return last
end

-- Shows the eyes shut, and the glow in `color` if the catch has a colour mutation.
function RevealWalk.showGlow(holder: Frame, color: Color3?)
	local glow = settings.glow
	holder.Visible = true
	local viewport = screenOf(holder)
	local diameter = settings.eyes.curve * viewport.X
	for lid, position in lidsAt(holder, nil) do
		lid.Size = UDim2.fromOffset(diameter, diameter)
		lid.Position = position
	end
	local colour = holder.Glow
	colour.Visible = color ~= nil
	if not color then
		return
	end
	-- Sized from the screen's diagonal in pixels, so the glow is round and reaches the corners on any screen.
	local diagonal = viewport.Magnitude
	-- Each band's ring runs out from its edge to the next band's, so together they make one soft glow.
	local thickness = math.max((glow.outerSize - glow.innerSize) * diagonal / (2 * glow.bands), 1)
	colour.Dark.Size = UDim2.fromOffset(glow.darkSize * diagonal, glow.darkSize * diagonal)
	colour.Dark.ImageTransparency = 1
	tween(colour.Dark, glow.fadeTime, { ImageTransparency = glow.darkTransparency })
	local spots = {}
	for _, child in colour:GetChildren() do
		local stroke = child:FindFirstChildOfClass("UIStroke")
		if stroke then
			local size = child:GetAttribute("Size") * diagonal
			child.Size = UDim2.fromOffset(size, size)
			stroke.Color = color
			stroke.Thickness = thickness
			stroke.Transparency = 1
			tween(stroke, glow.fadeTime, { Transparency = stroke:GetAttribute("Shown") })
		elseif child.Name:match("^Sparkle") then
			local size = glow.sparkleSize * math.clamp(viewport.Y / 1000, 0.6, 1.5)
			local angle = math.random() * 2 * math.pi
			local reach = lerp(glow.sparkleFrom, glow.sparkleTo, math.random()) * diagonal
			local x = math.clamp(0.5 * viewport.X + math.cos(angle) * reach, size, viewport.X - size)
			local y = math.clamp(0.5 * viewport.Y + math.sin(angle) * reach, size, viewport.Y - size)
			child.Size = UDim2.fromOffset(size, size)
			child.Position = UDim2.fromOffset(x, y)
			for _, bar in child:GetChildren() do
				if bar:IsA("Frame") then
					bar.BackgroundColor3 = color:Lerp(Color3.new(1, 1, 1), glow.sparkleLift)
				end
			end
			table.insert(spots, { sparkle = child, x = x, y = y, phase = math.random() * 2 * math.pi, turn = math.random() * 2 * math.pi })
		end
	end
	-- Twinkle: each sparkle grows and shrinks to nothing, turning a little and drifting, at its own phase.
	if sparkleLoop then
		sparkleLoop:Disconnect()
	end
	local started = os.clock()
	sparkleLoop = RunService.RenderStepped:Connect(function()
		if not colour.Parent then -- its screen was removed without hiding it first
			RevealWalk.hideGlow(holder)
			return
		end
		local t = os.clock() - started
		local drift = glow.drift * viewport.X
		for _, spot in spots do
			local wave = math.sin(t * glow.twinkle * 2 * math.pi + spot.phase)
			spot.sparkle.UIScale.Scale = math.max(wave, 0) * math.min(t / glow.fadeTime, 1)
			spot.sparkle.Rotation = math.deg(0.3 * math.sin(t + spot.turn))
			spot.sparkle.Position = UDim2.fromOffset(spot.x + drift * math.sin(0.7 * t + spot.turn), spot.y + drift * math.cos(0.5 * t + spot.phase))
		end
	end)
end

-- The blink open, to thin lids resting at the top and bottom (`rest` of the screen's height each, if given).
function RevealWalk.openEyes(holder: Frame, rest: number?): Tween
	return moveLids(holder, rest or settings.eyes.rest, settings.eyes.open)
end

-- The eyes shutting: the cut to black at the end of the walk.
function RevealWalk.closeEyes(holder: Frame): Tween
	return moveLids(holder, nil, settings.eyes.close)
end

function RevealWalk.hideGlow(holder: Frame)
	holder.Visible = false
	if sparkleLoop then
		sparkleLoop:Disconnect()
		sparkleLoop = nil
	end
end

-- The dot that marks a far-off egg: always the same size on screen.
local function buildMarker(egg: BasePart): BillboardGui
	local size = settings.markerSize
	local marker = Instance.new("BillboardGui")
	marker.Name = "WalkMarker"
	marker.Size = UDim2.fromOffset(size * 2, size * 2)
	marker.LightInfluence = 0
	marker.Enabled = false
	marker.Adornee = egg
	marker.Parent = egg
	for _, part in { { 1, 0.75, settings.markerRing }, { 0.5, 0.05, settings.markerImage } } do
		local label = Instance.new("ImageLabel")
		label.AnchorPoint = Vector2.new(0.5, 0.5)
		label.Position = UDim2.fromScale(0.5, 0.5)
		label.Size = UDim2.fromScale(part[1], part[1])
		label.BackgroundTransparency = 1
		label.Image = part[3]
		label.ImageColor3 = settings.markerColor
		label.ImageTransparency = 1
		label:SetAttribute("Shown", part[2])
		label.Parent = marker
	end
	return marker
end

export type Hooks = {
	onBlack: (() -> ())?, -- once the screen is black, before the eyes open: changes the player can't see happen
	onFrame: ((elapsed: number, u: number, footfall: boolean) -> ())?, -- every frame of the walk; `footfall` as a step lands
	lids: number?, -- how far the eyelids stay down
}

-- Plays the walk: a cut to black, the walk, a cut to black. It returns with the screen black, for the shot from the
-- monster's feet to fade in on. Once skipped() says yes, it cuts to black straight away.
function RevealWalk.play(plan: Plan, egg: BasePart, black: Frame, glow: Frame, skipped: () -> boolean, hooks: Hooks?)
	hooks = hooks or {}
	local camera = workspace.CurrentCamera
	task.wait(settings.cutDelay)
	tween(black, settings.cutIn, { BackgroundTransparency = 0 }).Completed:Wait()

	egg.CFrame = CFrame.new(egg.Position) -- upright, whatever way it tumbled in flight
	camera.CameraType = Enum.CameraType.Scriptable
	camera.FieldOfView = settings.fieldOfView
	local steps = 0.5 -- mid-stride, so the first footfall comes soon
	camera.CFrame = RevealWalk.cameraAt(plan, 0, 0, steps, math.huge)
	RevealWalk.showGlow(glow, plan.color)
	if hooks.onBlack then
		hooks.onBlack()
	end
	task.wait(settings.blackHold)
	-- The shut eyelids take over from the black, then blink open.
	black.BackgroundTransparency = 1
	RevealWalk.openEyes(glow, hooks.lids)

	local marker = buildMarker(egg)
	local eggHeight = egg.Size.Y

	local distance = (plan.finish - plan.start).Magnitude
	local stride = plan.eye * settings.strideEyes
	local startedAt = os.clock()
	local last, lastFootfall = startedAt, -math.huge
	while not skipped() do
		local now = os.clock()
		local u = (now - startedAt) / plan.duration
		if u >= 1 then
			break
		end
		-- Steps keep pace with how fast it goes, so a big stride is a slow step.
		local share, pace = walked(u)
		local speed = distance / plan.duration * pace
		local rate = math.clamp(speed / stride, settings.minStepRate, settings.maxStepRate) * (if plan.swims then SWIM_PACE else 1)
		rate *= 1 - smoother((u - settings.calmFrom) / (1 - settings.calmFrom)) -- the last step lands before the egg
		local before = steps
		steps += rate * (now - last)
		last = now
		local footfall = math.floor(steps) > math.floor(before) and not plan.swims
		if footfall then
			lastFootfall = now
		end
		camera.CameraType = Enum.CameraType.Scriptable -- in case anything else took the camera back
		camera.CFrame = RevealWalk.cameraAt(plan, u, share, steps, now - lastFootfall)
		if hooks.onFrame then
			hooks.onFrame(now - startedAt, u, footfall)
		end
		-- How tall the egg looks on screen, in pixels.
		local eggDistance = (egg.Position - camera.CFrame.Position).Magnitude
		local pixels = eggHeight / eggDistance / math.tan(math.rad(camera.FieldOfView) / 2) * camera.ViewportSize.Y / 2
		local hidden = math.clamp((pixels - settings.markerFull) / (settings.markerFrom - settings.markerFull), 0, 1)
		marker.Enabled = hidden < 1
		-- Far off, the dot covers a lot of ground, so it hangs part way towards the eyes where the floor can't
		-- cut through it. It stays the same size and in the same place on screen.
		marker.StudsOffset = Vector3.new(0, 0, eggDistance * MARKER_LIFT)
		for _, label in marker:GetChildren() do
			label.ImageTransparency = lerp(label:GetAttribute("Shown"), 1, hidden)
		end
		RunService.RenderStepped:Wait()
	end

	-- The eyes shut, then the black takes over again.
	RevealWalk.closeEyes(glow).Completed:Wait()
	black.BackgroundTransparency = 0
	marker:Destroy()
	RevealWalk.hideGlow(glow)
	task.wait(settings.blackAfter)
end

return RevealWalk
