-- The showcase: the cinematic side of the reveal, for catches that deserve it (docs/GAME_SPEC.md section 7, Config/Reveal
-- showcase). [Owner, 2026-11-11: "the cinematic angles should happen while the numbers are going up and the luck still
-- goes up, not after he gets revealed... I don't like the texts that present the name, size, rarity and money, I just
-- want a better visual for the final reveal"]
-- WHILE THE NUMBERS CLIMB: each luck label that lands cuts the camera to a new close angle on a part of the monster (its
-- flank, its back legs from behind, its other front foot, its back from above), a slow creep that never shows its face,
-- then back to the slow zoom out from its feet (RevealCloseUp), which carries on underneath. Rarer catches pass more
-- labels, so they get more angles. Black cinema bars frame it. The monster stands still, like a statue.
-- AT THE UNVEIL: the world behind the monster is swapped for a drawn backdrop in its rarity's colours (RevealBackdrop),
-- pieces of the ground hang in the air, and the final text lands at once, as it always did. No extra texts.
-- Common catches get none of it (RevealShowcase.level). RevealController plays it. Display only.
local Lighting = game:GetService("Lighting")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")

local Catch = require(ReplicatedStorage.Shared.Config.Catch)
local DinoStats = require(ReplicatedStorage.Shared.DinoStats)
local Reveal = require(ReplicatedStorage.Shared.Config.Reveal)
local RevealBackdrop = require(script.Parent.RevealBackdrop)
local RevealCloseUp = require(script.Parent.RevealCloseUp)
local Roles = require(ReplicatedStorage.Shared.Roles)
local UiKit = require(ReplicatedStorage.Shared.UiKit)

local RevealShowcase = {}

local settings = Reveal.showcase
local WHITE = Color3.new(1, 1, 1)
local BLACK = Color3.new(0, 0, 0)
local FIT_STEPS = 24 -- how finely a camera's distance is searched
local GRAVITY = 0.9 -- the debris falls by this many monster heights a second, each second

local function lerp(a: number, b: number, u: number): number
	return a + (b - a) * u
end

local function rotated(direction: Vector3, degrees: number): Vector3
	return CFrame.Angles(0, math.rad(degrees), 0):VectorToWorldSpace(direction)
end

-- `level` lifted off the ground by `degrees` (sunk below it when negative).
local function raised(level: Vector3, degrees: number): Vector3
	local angle = math.rad(degrees)
	return level * math.cos(angle) + Vector3.yAxis * math.sin(angle)
end

local function cornersOf(box: CFrame, size: Vector3): { Vector3 }
	local corners = {}
	for _, x in { -1, 1 } do
		for _, y in { -1, 1 } do
			for _, z in { -1, 1 } do
				table.insert(corners, box * (size / 2 * Vector3.new(x, y, z)))
			end
		end
	end
	return corners
end

-- How much of a showcase a catch deserves: 0 for none, up to #settings.levels.
function RevealShowcase.level(catch): number
	local size = DinoStats.findOption(Catch.sizes, catch.size)
	local level = 0
	for index, step in settings.levels do
		if
			(catch.oneIn or 0) >= step.oneIn
			or (size and size.scale >= step.scale)
			or (step.isNew and catch.isNew == true)
			or (step.special and DinoStats.special(catch.id) ~= nil)
		then
			level = index
		end
	end
	return level
end

-- The view from `position` towards `target`, tilted so that `target` sits `share` of the way down the screen.
local function viewOf(position: Vector3, target: Vector3, share: number, tanUp: number): CFrame
	local tilt = math.atan((0.5 - share) * 2 * tanUp)
	return CFrame.lookAt(position, target) * CFrame.Angles(-tilt, 0, 0)
end

-- The nearest view along `positionAt` (a distance to a camera position) from which all of `points` show inside `fill`
-- of the screen's band (`band`: shares of its height from the top). Returns the view and its distance.
local function fit(
	positionAt: (number) -> Vector3,
	target: Vector3,
	points: { Vector3 },
	fieldOfView: number,
	aspect: number,
	band: { number },
	fill: number,
	near: number,
	far: number
): (CFrame, number)
	local tanUp = math.tan(math.rad(fieldOfView) / 2)
	local tanAcross = tanUp * aspect
	local middle = (band[1] + band[2]) / 2
	local half = (band[2] - band[1]) / 2 * fill
	local function view(distance: number): CFrame
		return viewOf(positionAt(distance), target, middle, tanUp)
	end
	local function fits(distance: number): boolean
		local from = view(distance)
		for _, point in points do
			local seen = from:PointToObjectSpace(point)
			if seen.Z > -0.05 then
				return false
			end
			local across = seen.X / -seen.Z / tanAcross
			local down = 0.5 - seen.Y / -seen.Z / (2 * tanUp)
			if math.abs(across) > fill or math.abs(down - middle) > half then
				return false
			end
		end
		return true
	end
	if not fits(far) then
		return view(far), far
	end
	local low, high = near, far
	for _ = 1, FIT_STEPS do
		local between = math.sqrt(low * high)
		if fits(between) then
			high = between
		else
			low = between
		end
	end
	return view(high), high
end

export type Shot = {
	name: string,
	from: CFrame,
	to: CFrame,
	time: number,
	fieldOfView: number,
}

-- Where the monster's eyes are (its Pupil parts).
local function eyesOf(model: Model): { Vector3 }
	local eyes = {}
	for _, part in model:GetDescendants() do
		if part:IsA("BasePart") and Roles.of(part) == "Pupil" then
			table.insert(eyes, part.Position)
		end
	end
	return eyes
end

-- Works out one close angle on a part of the monster for the climb, or nil when it has no good one: the camera would
-- stand inside its body, or its eyes would show (the face waits for the unveil). `band` is the part of the screen above
-- the counter and the letters.
local function planDetail(name: string, stage, band: { number }): Shot?
	local detail = settings.details[name]
	if not detail then
		return nil
	end
	local camera = workspace.CurrentCamera
	local aspect = camera.ViewportSize.X / math.max(camera.ViewportSize.Y, 1)
	local tanUp = math.tan(math.rad(detail.fieldOfView) / 2)
	local tanAcross = tanUp * aspect
	local middle = (band[1] + band[2]) / 2
	local forward: Vector3 = stage.forward
	local side = if (if stage.yaw[2] ~= 0 then stage.yaw[2] else stage.yaw[1]) < 0 then -1 else 1
	-- The part of it this angle frames: a share of the box round the monster itself (not its egg), turned to look along
	-- `forward` (its front is at -Z).
	local frame, size = stage.model:GetBoundingBox()
	local body = CFrame.lookAt(frame.Position, frame.Position + forward)
	local extent = Vector3.new(
		math.abs(body.RightVector:Dot(frame.RightVector)) * size.X + math.abs(body.RightVector:Dot(frame.LookVector)) * size.Z,
		size.Y,
		math.abs(body.LookVector:Dot(frame.RightVector)) * size.X + math.abs(body.LookVector:Dot(frame.LookVector)) * size.Z
	)
	local centre = body * (extent * Vector3.new(0, detail.at[1], -detail.at[2]))
	local region = extent * Vector3.new(detail.span[1], detail.span[2], detail.span[3])
	local points = cornersOf(CFrame.new(centre) * body.Rotation, region)
	local function aboveFloor(position: Vector3): Vector3
		return Vector3.new(position.X, math.max(position.Y, stage.floor), position.Z)
	end
	local way = raised(rotated(forward, side * detail.yaw), detail.elevation)
	local to, distance = fit(function(d: number)
		return aboveFloor(centre + way * d)
	end, centre, points, detail.fieldOfView, aspect, band, detail.fill, region.Magnitude * 0.3, region.Magnitude * 14)
	local startWay = raised(rotated(forward, side * (detail.yaw + detail.turn)), detail.elevation)
	local from = viewOf(aboveFloor(centre + startWay * distance * detail.push), centre, middle, tanUp)
	if not RevealCloseUp.clear(stage.model, { to.Position, from.Position }, math.max(region.Magnitude * 0.06, 0.5)) then
		return nil
	end
	-- Its eyes stay off the screen, unless the camera is well behind them (from the side an eye still shows).
	for _, eye in eyesOf(stage.model) do
		for _, view in { from, to } do
			local seen = view:PointToObjectSpace(eye)
			local inFront = (view.Position - eye).Unit:Dot(forward) > -0.5
			if inFront and seen.Z < 0 and math.abs(seen.X / seen.Z) <= tanAcross and math.abs(seen.Y / seen.Z) <= tanUp then
				return nil
			end
		end
	end
	return { name = name, from = from, to = to, time = detail.time, fieldOfView = detail.fieldOfView }
end

-- Pieces of the ground that burst up round the monster's feet and hang in the air. `update` moves them on.
local function newDebris(count: number, stage)
	local look = settings.debris
	local box: CFrame, size: Vector3 = stage.box, stage.size
	local ground = stage.floor - Reveal.closeUp.floorGap
	local reach = math.max(size.X, size.Y)
	local folder = Instance.new("Folder")
	folder.Name = "RevealDebris"
	folder.Parent = workspace

	-- They're made of the ground they come from.
	local color, material = look.color, Enum.Material.Slate
	local map = workspace:FindFirstChild("Map")
	if map then
		local params = RaycastParams.new()
		params.FilterType = Enum.RaycastFilterType.Include
		params.FilterDescendantsInstances = { map }
		local under = workspace:Raycast(Vector3.new(stage.feet.X, ground + 6, stage.feet.Z), Vector3.new(0, -14, 0), params)
		if under then
			color, material = under.Instance.Color, under.Material
		end
	end

	local random = Random.new()
	local pieces = {}
	for _ = 1, count do
		local big = random:NextNumber() ^ 2
		local across = math.max(lerp(look.size[1], look.size[2], big) * reach, look.smallest)
		local part = Instance.new("Part")
		part.Anchored = true
		part.CanCollide = false
		part.CanQuery = false
		part.CanTouch = false
		part.CastShadow = false
		part.Material = material
		part.Color = color:Lerp(BLACK, random:NextNumber() * 0.3)
		part.Size = Vector3.new(across, across * random:NextNumber(0.45, 1), across * random:NextNumber(0.6, 1.3))
		-- From the ground round its footprint, flying up and a little outwards.
		local angle = random:NextNumber() * 2 * math.pi
		local out = random:NextNumber(0.5, 1.15)
		local offset = box.RightVector * math.cos(angle) * size.X / 2 * out + box.LookVector * math.sin(angle) * size.Z / 2 * out
		local position = Vector3.new(box.Position.X + offset.X, ground, box.Position.Z + offset.Z)
		local outward = if offset.Magnitude > 1e-3 then offset.Unit else Vector3.xAxis
		local speed = lerp(look.speed[1], look.speed[2], random:NextNumber()) * size.Y
		part.CFrame = CFrame.new(position)
		part.Parent = folder
		table.insert(pieces, {
			part = part,
			position = position,
			velocity = (Vector3.yAxis + outward * random:NextNumber(0.1, 0.45)) * speed,
			turn = CFrame.Angles(random:NextNumber() * 6, random:NextNumber() * 6, random:NextNumber() * 6),
			axis = random:NextUnitVector(),
			spin = random:NextNumber(2, 7),
			angle = 0,
			landed = false,
		})
	end

	local age = 0
	return {
		update = function(dt: number)
			-- Full speed for a moment, then time all but stops.
			age += dt
			local slowing = math.clamp((age - look.fly) / look.slowTime, 0, 1)
			local pace = dt * lerp(1, look.slowTo, slowing)
			for _, piece in pieces do
				if piece.landed then
					continue
				end
				piece.velocity -= Vector3.new(0, GRAVITY * size.Y * pace, 0)
				piece.position += piece.velocity * pace
				piece.angle += piece.spin * pace
				if piece.position.Y < ground and piece.velocity.Y < 0 then -- back down: it lies where it fell
					piece.position = Vector3.new(piece.position.X, ground + piece.part.Size.Y / 2, piece.position.Z)
					piece.landed = true
				end
				piece.part.CFrame = CFrame.new(piece.position) * CFrame.fromAxisAngle(piece.axis, piece.angle) * piece.turn
			end
		end,
		destroy = function()
			folder:Destroy()
		end,
	}
end

-- Sets up the showcase for `catch`, standing on `stage` (RevealCloseUp), or returns nil for a catch that gets none.
-- Call it before anything darkens the monster's colours. options: rarity (its tier id), tier (its luck label's
-- Config/Reveal tier, or nil), scale (the HUD's), onCut (called when a cut lands that no luck label marks: the flash, the
-- zoom and the sound are RevealController's).
function RevealShowcase.new(catch, stage, options)
	local level = RevealShowcase.level(catch)
	local plan = settings.levels[level]
	if not plan then
		return nil
	end
	local playerGui = Players.LocalPlayer:WaitForChild("PlayerGui")
	local scale: number = options.scale
	local pair = UiKit.RARITY[options.rarity] or UiKit.RARITY.common
	local light, deep = Color3.fromHex(pair[1]), Color3.fromHex(pair[2])
	local accent: Color3 = if options.tier then options.tier.color else Color3.fromHex(UiKit.RARITY_TEXT[options.rarity] or "#ffffff")
	local tone = RevealBackdrop.tone(stage.model)

	-- The close angles for the climb, in the order they'll play; the ones this monster has no good view for drop out.
	local band = { (if settings.cinemaBars then settings.bars else 0) + 0.03, settings.detailBottom }
	local shots: { Shot } = {}
	for _, name in settings.detailOrder do
		local ok, shot = pcall(planDetail, name, stage, band)
		if ok and shot then
			table.insert(shots, shot)
		elseif not ok then
			warn(`[RevealShowcase] Couldn't plan the {name} angle: {shot}`)
		end
	end
	local spots, farthest = {}, 0
	for _, shot in shots do
		for _, view in { shot.from, shot.to } do
			table.insert(spots, view.Position)
			farthest = math.max(farthest, (view.Position - stage.box.Position).Magnitude)
		end
	end

	-- The cinema bars and the speed lines of a cut cover the whole screen, past a phone's notch.
	local cover = Instance.new("ScreenGui")
	cover.Name = "RevealShowBars"
	cover.IgnoreGuiInset = true
	cover.ScreenInsets = Enum.ScreenInsets.None
	cover.ResetOnSpawn = false
	cover.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	cover.DisplayOrder = 10
	cover.Parent = playerGui
	local lines = Instance.new("ImageLabel")
	lines.Name = "CutLines"
	lines.AnchorPoint = Vector2.new(0.5, 0.5)
	lines.Position = UDim2.fromScale(0.5, 0.5)
	lines.BackgroundTransparency = 1
	lines.Image = settings.backdrop.images.speedLines
	lines.ImageColor3 = WHITE
	lines.ImageTransparency = 1
	lines.ZIndex = 1
	lines.Parent = cover
	local bars = {}
	for _, top in { true, false } do
		local bar = Instance.new("Frame")
		bar.Name = if top then "BarTop" else "BarBottom"
		bar.AnchorPoint = Vector2.new(0, if top then 0 else 1)
		bar.Size = UDim2.fromScale(1, settings.bars)
		bar.Position = UDim2.fromScale(0, if top then -settings.bars - 0.01 else 1 + settings.bars + 0.01)
		bar.BackgroundColor3 = BLACK
		bar.BorderSizePixel = 0
		bar.ZIndex = 2
		bar.Parent = cover
		local trim = Instance.new("Frame") -- a thin line in the catch's colour along its inner edge
		trim.AnchorPoint = Vector2.new(0, if top then 0 else 1)
		trim.Position = UDim2.fromScale(0, if top then 1 else 0)
		trim.Size = UDim2.new(1, 0, 0, math.max(2, math.round(4 * scale)))
		trim.BackgroundColor3 = accent
		trim.BorderSizePixel = 0
		trim.ZIndex = 2
		trim.Parent = bar
		bars[top] = bar
	end
	for _, bar in bars do
		bar.Visible = settings.cinemaBars == true
	end
	local function slideBars(shown: boolean)
		local info = TweenInfo.new(settings.barTime, Enum.EasingStyle.Quart, Enum.EasingDirection.Out)
		TweenService:Create(bars[true], info, { Position = UDim2.fromScale(0, if shown then 0 else -settings.bars - 0.01) }):Play()
		TweenService:Create(bars[false], info, { Position = UDim2.fromScale(0, if shown then 1 else 1 + settings.bars + 0.01) }):Play()
	end

	-- The speed lines of a cut flash over the picture and fly outwards.
	local function hit()
		local cut = settings.cut
		local diagonal = workspace.CurrentCamera.ViewportSize.Magnitude
		lines.Size = UDim2.fromOffset(diagonal * 1.15, diagonal * 1.15)
		lines.ImageTransparency = cut.lines
		lines.Rotation = math.random(0, 359)
		local info = TweenInfo.new(cut.linesTime, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)
		TweenService:Create(lines, info, { ImageTransparency = 1, Size = UDim2.fromOffset(diagonal * 1.6, diagonal * 1.6) }):Play()
	end

	local backdrop = nil
	local keyLight: Part? = nil
	local function raiseBackdrop()
		if backdrop or not settings.backdrop.enabled then
			return
		end
		-- A dark monster also gets a white light from near the camera, like a photographer's flash, so its shape shows
		-- as well as its outline. A light reaches 60 studs at most, so the biggest keep to their outline.
		if tone < settings.backdrop.darkBelow then
			local holder = Instance.new("Part")
			holder.Name = "RevealKeyLight"
			holder.Anchored = true
			holder.CanCollide = false
			holder.CanQuery = false
			holder.CanTouch = false
			holder.Transparency = 1
			holder.Size = Vector3.one
			holder.Parent = workspace
			local lamp = Instance.new("PointLight")
			lamp.Brightness = settings.backdrop.keyLight
			lamp.Shadows = false
			lamp.Parent = holder
			keyLight = holder
		end
		backdrop = RevealBackdrop.new({
			box = stage.box,
			size = stage.size,
			light = light,
			deep = deep,
			accent = accent,
			tone = tone,
			name = nil, -- no giant name behind it [Owner, 2026-11-11: no texts presenting the catch]
			cosmos = plan.cosmos == true,
		})
		backdrop.update(os.clock(), workspace.CurrentCamera) -- in place from its first frame
		-- The world's haze would wash the backdrop out (it stands in the world, behind the monster), so it thins until the
		-- reveal ends (SkyController HazeScale; RevealController puts it back).
		local camera = workspace.CurrentCamera
		camera:SetAttribute("HazeScale", math.min(camera:GetAttribute("HazeScale") or 1, settings.backdrop.haze))
	end

	local show = {
		level = level,
		spots = spots, -- where its cameras stand, for hiding what's in their way
		farthest = farthest, -- how far the furthest of them is from the monster, for thinning the haze
		hasBackdrop = settings.backdrop.enabled,
	}
	local unveiled = false
	local nextShot = 1 -- which close angle the next cut goes to
	local current: Shot? = nil
	local currentFrom, currentUntil = 0, 0
	-- [Owner, 2026-11-11: "add transitions between the camera angles"] The camera never jumps: it glides from where it is
	-- to the next angle (and back to the feet), or, when a glide would pass through the monster, whip-pans: it swings
	-- away fast, blurring, and swings in on the new angle from the other side. `move` is the transition running now.
	local look = settings.transition
	local lastView: CFrame? = nil
	local lastFov = 70
	local move = nil -- { from, fov, at, time, kind = "glide" | "whip", turn = 1 | -1, back = true when it's to the feet }
	local blur = Instance.new("BlurEffect")
	blur.Name = "RevealWhipBlur"
	blur.Size = 0
	blur.Parent = Lighting
	local timedDone = 0 -- cuts made on the clock, for a catch with no luck labels
	local startMove, blend

	-- A transition starting now from `from` towards a camera that will stand at `to`: a glide when the straight way there
	-- is clear of the monster's body, a whip-pan when it isn't. `back` when it returns to the feet.
	startMove = function(from: CFrame, fov: number, to: Vector3, now: number, back: boolean)
		local points = {}
		for step = 1, look.checks do
			table.insert(points, from.Position:Lerp(to, step / (look.checks + 1)))
		end
		local room = math.max(stage.size.Magnitude * 0.015, 0.4)
		local kind = if not look.whipOnly and RevealCloseUp.clear(stage.model, points, room) then "glide" else "whip"
		-- A whip turns the way the camera is heading, so the swing reads as one movement.
		local heading = from:VectorToObjectSpace(to - from.Position)
		return {
			from = from,
			fov = fov,
			at = now,
			time = if kind == "glide" then (if back then look.glideBack else look.glide) else look.whip,
			kind = kind,
			turn = if heading.X > 0 then -1 else 1,
		}
	end

	-- Where the camera is `u` (0 to 1) through `m`, on its way to `toView`/`toFov` (which may be moving). Also returns the blur.
	blend = function(m, toView: CFrame, toFov: number, u: number): (CFrame, number, number)
		if m.kind == "glide" then
			local e = u * u * u * (u * (u * 6 - 15) + 10) -- slow out, fast through the middle, slow in
			local view = m.from:Lerp(toView, e)
			return view, m.fov + (toFov - m.fov) * e, look.blur * look.glideBlur * math.sin(math.pi * u)
		end
		local swing = math.rad(look.whipAngle)
		local peak = (1 - math.abs(u * 2 - 1)) ^ 0.6
		if u < 0.5 then
			local k = (u * 2) ^ 2.2 -- speeding up as it swings away
			return m.from * CFrame.Angles(0, m.turn * swing * k, 0), m.fov, look.blur * peak
		end
		local k = (1 - (u - 0.5) * 2) ^ 2.2 -- slowing down as it lands
		return toView * CFrame.Angles(0, -m.turn * swing * k, 0), toFov, look.blur * peak
	end
	local debris = nil
	local lastRender = os.clock()

	-- The numbers start climbing: the cinema bars slide in.
	function show.arrive()
		slideBars(true)
	end

	-- A cut to the next close angle, with `remaining` seconds of climb left. `marked` when a luck label lands with it (its
	-- slam is the hit); otherwise the cut brings its own. Does nothing when there's no angle left to show or no time for one.
	function show.cut(now: number, remaining: number, marked: boolean?)
		if unveiled or #shots == 0 then
			return
		end
		local time = math.min(shots[nextShot].time, remaining - settings.detailLead)
		if time < settings.detailShortest then
			return -- the last stretch belongs to the zoom out from its feet, which the unveil whips back from
		end
		current = shots[nextShot]
		-- [Owner, 2026-11-11: "only make them switch when the type of luck and that sound effect of slamming happens"] It
		-- holds this angle until the next luck label slams in (or the unveil), instead of going back to the feet on its own.
		currentFrom, currentUntil = now, if settings.labelCutsOnly then math.huge else now + time
		nextShot = nextShot % #shots + 1
		move = if lastView then startMove(lastView, lastFov, current.from.Position, now, false) else nil
		hit()
		if not marked and options.onCut then
			options.onCut()
		end
	end

	-- Each frame of the climb, `progress` 0 to 1: a catch with no luck labels (a big or a new one) gets its cuts on the
	-- clock instead, evenly spread.
	function show.climb(now: number, progress: number, remaining: number)
		local cuts = plan.timedCuts or 0
		if settings.labelCutsOnly or options.tier or timedDone >= cuts then
			return
		end
		if progress >= (timedDone + 1) / (cuts + 1) then
			timedDone += 1
			show.cut(now, remaining, false)
		end
	end

	-- The camera for now and its field of view during the climb, given where the zoom out from the feet (`base`, `baseFov`)
	-- is: on a close angle, on the feet, or on its way between them. Nil after the unveil.
	function show.camera(now: number, base: CFrame, baseFov: number): (CFrame?, number?)
		if unveiled then
			blur.Size = 0
			return nil, nil
		end
		local shot = current
		if shot and now >= currentUntil then
			current = nil -- back to the feet
			shot = nil
			move = if lastView then startMove(lastView, lastFov, base.Position, now, true) else nil
		end
		local view, fov = base, baseFov
		if shot then
			local along = math.clamp((now - currentFrom) / shot.time, 0, 1)
			local eased = TweenService:GetValue(along, Enum.EasingStyle.Sine, Enum.EasingDirection.Out)
			view, fov = shot.from:Lerp(shot.to, eased), shot.fieldOfView
		end
		local blurNow = 0
		if move then
			local u = (now - move.at) / move.time
			if u >= 1 then
				move = nil
			else
				view, fov, blurNow = blend(move, view, fov, math.max(u, 0))
			end
		end
		blur.Size = blurNow
		lastView, lastFov = view, fov
		return view, fov
	end

	-- The unveil: the backdrop is up behind the flash, the bars leave and the ground bursts. Also on a tap that skips.
	function show.unveil(now: number)
		if unveiled then
			return
		end
		unveiled = true
		current = nil
		move = nil
		blur.Size = 0
		lastRender = now
		raiseBackdrop()
		slideBars(false)
		if plan.debris then
			local ok, made = pcall(newDebris, plan.debris, stage)
			debris = if ok then made else nil
		end
	end

	-- Each frame, once the camera is where it will be drawn from.
	function show.render(now: number, camera: Camera)
		local dt = math.clamp(now - lastRender, 0, 0.1)
		lastRender = now
		if backdrop then
			backdrop.update(now, camera)
		end
		if keyLight then
			-- A third of the way from the camera to the monster and a little above, so it lights the monster more than
			-- the ground right by the lens.
			local eye = camera.CFrame.Position
			local toMonster = stage.box.Position - eye
			keyLight.CFrame = CFrame.new(eye + toMonster * 0.33 + Vector3.new(0, stage.size.Y * 0.3, 0))
			local lamp = keyLight:FindFirstChildOfClass("PointLight")
			if lamp then
				lamp.Range = math.clamp(toMonster.Magnitude * 0.75 + stage.size.Magnitude * 0.6, 12, 60)
			end
		end
		if debris then
			debris.update(dt)
		end
	end

	function show.destroy()
		if backdrop then
			backdrop.destroy()
			backdrop = nil
		end
		if debris then
			debris.destroy()
			debris = nil
		end
		if keyLight then
			keyLight:Destroy()
			keyLight = nil
		end
		blur:Destroy()
		cover:Destroy()
	end

	return show
end

-- Removes anything a reveal that broke half-way left behind.
function RevealShowcase.cleanUp()
	local playerGui = Players.LocalPlayer:FindFirstChild("PlayerGui")
	for _, name in { "RevealShowBars", "RevealBackdrop" } do
		local left = playerGui and playerGui:FindFirstChild(name)
		if left then
			left:Destroy()
		end
	end
	local whipBlur = Lighting:FindFirstChild("RevealWhipBlur")
	if whipBlur then
		whipBlur:Destroy()
	end
	for _, name in { "RevealBackdrop", "RevealDebris", "RevealKeyLight" } do
		local left = workspace:FindFirstChild(name)
		if left then
			left:Destroy()
		end
	end
end

return RevealShowcase
