-- The shot from the monster's feet after the walk (docs/GAME_SPEC.md section 7). [Owner, 2026-11-07] This is the most
-- important part of the reveal: the camera switches to the feet and one continuous, very slow zoom out runs while the
-- numbers climb, the body coming into view bit by bit but never all of it. Only when the numbers finish does the camera
-- whip back to the whole monster. The monster is simply there, at its real size, right by the egg, facing the way it
-- walked. It doesn't pop out of the egg: it walked up to it. Display only.
-- Numbers live in Config/Reveal closeUp. RevealController plays it.
local ContentProvider = game:GetService("ContentProvider")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local DinoModel = require(ReplicatedStorage.Shared.DinoModel)
local Map = require(ReplicatedStorage.Shared.Config.Map)
local Reveal = require(ReplicatedStorage.Shared.Config.Reveal)
local Roles = require(ReplicatedStorage.Shared.Roles)
local Throw = require(ReplicatedStorage.Shared.Config.Throw)

local RevealCloseUp = {}

local settings = Reveal.closeUp
-- The bones the front feet hang from, best first: a four-legged monster's front legs, a two-legged one's knees, then
-- its hips, a swimmer's front flippers or fins.
local FRONT_FEET = {
	{ "FrontL", "FrontR" },
	{ "ShinL", "ShinR" },
	{ "LegL", "LegR" },
	{ "FlipperFL", "FlipperFR" },
	{ "FinL", "FinR" },
}
local SEARCH_STEPS = 48 -- how finely the egg's spot is looked for along the monster's length...
local REFINE_STEPS = 6 -- ...then narrowed down
local RISE_POWER = 2.5 -- the camera stays low for most of the zoom: it rises at progress ^ this
local PATH_CHECKS = 12 -- how many spots along the camera's way are checked against the monster's body
local EYE_FALLBACK = 0.85 -- share of its height, for a model with no Pupil parts

local function lerp(a: number, b: number, u: number): number
	return a + (b - a) * u
end

-- Where value sits between low (0) and high (1), evenly on a log scale.
local function logShare(value: number, low: number, high: number): number
	return math.clamp(math.log(math.max(value, low) / low) / math.log(high / low), 0, 1)
end

local function flat(direction: Vector3?): Vector3?
	if not direction then
		return nil
	end
	local level = Vector3.new(direction.X, 0, direction.Z)
	return if level.Magnitude > 1e-3 then level.Unit else nil
end

-- Whether the model's head points along its pivot's +Z, from where its head is against its tail (as
-- DinoLifeController works it out). Most imported models do; a few, and the block models, face -Z.
local function facesPlusZ(model: Model): boolean
	local pivot = model:GetPivot()
	local front, back = nil, nil
	for _, bone in model:GetDescendants() do
		if bone:IsA("Bone") then
			if bone.Name == "Jaw" or (bone.Name == "Head" and not front) then
				front = bone
			end
			if bone.Name == "Tail1" or ((bone.Name == "Spine" or bone.Name == "Swim") and not back) then
				back = bone
			end
		end
	end
	return front ~= nil
		and back ~= nil
		and pivot:PointToObjectSpace(front.WorldPosition).Z > pivot:PointToObjectSpace(back.WorldPosition).Z
end

local function frontFeet(model: Model): (Vector3?, Vector3?)
	for _, pair in FRONT_FEET do
		local left = model:FindFirstChild(pair[1], true)
		local right = model:FindFirstChild(pair[2], true)
		if left and right and left:IsA("Bone") and right:IsA("Bone") then
			return left.WorldPosition, right.WorldPosition
		end
	end
	return nil, nil
end

-- How far the box (`boxFrame`, `boxSize`) reaches from `from` along `direction`.
local function reach(boxFrame: CFrame, boxSize: Vector3, from: Vector3, direction: Vector3): number
	local furthest = -math.huge
	for _, x in { -1, 1 } do
		for _, y in { -1, 1 } do
			for _, z in { -1, 1 } do
				local corner = boxFrame * (boxSize / 2 * Vector3.new(x, y, z))
				furthest = math.max(furthest, (corner - from):Dot(direction))
			end
		end
	end
	return furthest
end

-- How far from `from` along `forward` the egg has to lie so it touches nothing of the monster, looking up to `upTo`
-- studs. Uses the monster's real shape (its parts' collision shapes).
local function clearAlong(model: Model, eggSize: Vector3, from: Vector3, forward: Vector3, upTo: number): number
	local gap = settings.eggGap
	local probe = Instance.new("Part")
	probe.Name = "RevealEggProbe"
	probe.Anchored = true
	probe.CanCollide = false
	probe.CanQuery = false
	probe.CanTouch = false
	probe.Transparency = 1
	probe.Size = eggSize + Vector3.new(gap * 2, 0, gap * 2)
	probe.Parent = workspace
	local params = OverlapParams.new()
	params.FilterType = Enum.RaycastFilterType.Include
	params.FilterDescendantsInstances = { model }
	params.MaxParts = 1
	local turn = CFrame.lookAt(Vector3.zero, forward)
	local lift = Vector3.new(0, eggSize.Y / 2 + gap, 0)
	local function blocked(ahead: number): boolean
		probe.CFrame = turn + (from + forward * ahead + lift)
		return #workspace:GetPartsInPart(probe, params) > 0
	end

	local step = math.max(eggSize.Z / 2, upTo / SEARCH_STEPS)
	local lastBlocked, clear = nil, math.max(upTo, 0)
	local ahead = 0
	while ahead < upTo do
		if not blocked(ahead) then
			clear = ahead
			break
		end
		lastBlocked = ahead
		ahead += step
	end
	if lastBlocked then
		local low = lastBlocked
		for _ = 1, REFINE_STEPS do
			local middle = (low + clear) / 2
			if blocked(middle) then
				low = middle
			else
				clear = middle
			end
		end
	end
	probe:Destroy()
	return clear
end

-- Loads the monster's meshes ahead of time (call it as the walk starts): a model whose meshes haven't loaded shows up
-- a moment late, and the close-up would open on an egg with nothing behind it. Yields until loaded.
function RevealCloseUp.preload(dinoId: string)
	local assets = ReplicatedStorage:FindFirstChild("Assets")
	local dinos = assets and assets:FindFirstChild("Dinos")
	local template = dinos and dinos:FindFirstChild(`dino_{dinoId}`)
	if template then
		ContentProvider:PreloadAsync({ template })
	end
end

export type Stage = {
	model: Model, -- the monster, at its real size, in the workspace
	forward: Vector3, -- the way it faces (the way it walked), flat
	box: CFrame, -- the middle of the box round the monster and the egg, turned the monster's way...
	size: Vector3, -- ...and its size: across, up, along
	feet: Vector3, -- on the ground, between its front feet: where the shot starts
	feetLift: number, -- how far above the feet the camera aims, per stud it stands from them, to keep them above the text
	hold: number, -- seconds on the feet before the zoom starts
	whipTime: number, -- seconds the final move takes
	countShare: number, -- how far through the whole move (0 to 1) the slow zoom gets by the last number
	distance: { number }, -- how far the camera is from what it looks at, at the start and the end
	yaw: { number }, -- radians round from straight in front of the monster, at the start and the end
	elevation: { number }, -- radians it looks down from, at the start and the end
	focus: Vector3, -- what the camera looks at in the end: the box's middle...
	aim: number, -- ...and studs above that (below when negative), to frame them above the text
	floor: number, -- the camera never goes below this height
	wallHalf: number, -- how far the walls stand from the corridor's middle in this reveal (RevealOpening)
}

-- Where the monster's eyes are, from its Pupil parts.
local function eyesOf(model: Model): { Vector3 }
	local eyes = {}
	for _, part in model:GetDescendants() do
		if part:IsA("BasePart") and Roles.of(part) == "Pupil" then
			table.insert(eyes, part.Position)
		end
	end
	return eyes
end

-- Whether `point` shows on the screen from `view`.
local function onScreen(view: CFrame, point: Vector3, tanUp: number, tanAcross: number): boolean
	local seen = view:PointToObjectSpace(point)
	return seen.Z < 0 and math.abs(seen.X / seen.Z) <= tanAcross and math.abs(seen.Y / seen.Z) <= tanUp
end

-- Runs `check` with the monster's parts queryable, so it can be tested against.
local function withQuery<T>(model: Model, check: () -> T): T
	local queryable = {}
	for _, part in model:GetDescendants() do
		if part:IsA("BasePart") then
			queryable[part] = part.CanQuery
			part.CanQuery = true
		end
	end
	local ok, result = pcall(check)
	for part, canQuery in queryable do
		part.CanQuery = canQuery
	end
	if not ok then
		error(result, 0)
	end
	return result
end

-- Builds the caught monster right by the egg, at its real size, facing `approach` (the way it walked; the throw's way if
-- unknown), and works out the camera's move. `band` is the part of the screen to frame them in at the end, as shares of
-- its height from the top: {top, bottom for the smallest monsters, bottom for the biggest}. The final text covers the
-- rest. The whole screen when left out. `wallHalf` is where the walls stand for this reveal.
function RevealCloseUp.stage(
	catch,
	egg: BasePart,
	approach: Vector3?,
	random: Random?,
	band: { number }?,
	wallHalf: number?
): Stage
	random = random or Random.new()
	local eggSize = egg.Size
	local ground = egg.Position - Vector3.new(0, eggSize.Y / 2, 0)
	local forward = flat(approach) or flat(Throw.lane.direction) or -Vector3.zAxis
	local right = forward:Cross(Vector3.yAxis)
	local scale = DinoModel.statueScale(catch.id, catch.size)
	local bigness = logShare(scale, 1, Reveal.walk.bigScale)

	local turn = if random:NextNumber() < 0.5 then -1 else 1
	local cameraSide = right * -turn -- the side the camera looks from, a little round from the monster's front

	local model = DinoModel.build(catch.id, catch.mutation, ground, scale)
	model.Name = "RevealDino"
	local turned = facesPlusZ(model)
	model:PivotTo(CFrame.lookAt(ground, ground + (if turned then -forward else forward)))
	model.Parent = workspace

	-- [Owner, 2026-11-07: it must get literally to the egg] The egg goes between the front feet, as near as fits...
	local spot = ground
	local leftFoot, rightFoot = frontFeet(model)
	if leftFoot and rightFoot then
		local middle = (leftFoot + rightFoot) / 2
		spot = Vector3.new(middle.X, ground.Y, middle.Z)
	end
	-- ...further ahead if the monster is too low there to stand over it. A monster hardly taller than the egg
	-- would hide behind it, so then the egg goes beside its front feet instead, on the camera's side.
	local boxFrame, boxSize = model:GetBoundingBox()
	local away = if boxSize.Y < eggSize.Y * settings.besideBelow then cameraSide else forward
	local upTo = reach(boxFrame, boxSize, spot, away) + eggSize.Z
	local ok, shift = pcall(withQuery, model, function()
		return clearAlong(model, eggSize, spot, away, upTo)
	end)
	if ok then
		spot += away * shift
	else
		warn(`[RevealCloseUp] Couldn't fit the egg by the monster: {shift}`)
	end
	-- Then a clear gap further on, so the egg and the monster never look stuck together.
	-- A giant's half length would put the egg hundreds of studs off, so the gap stops at maxAhead egg heights.
	local length = reach(boxFrame, boxSize, spot, forward) + reach(boxFrame, boxSize, spot, -forward)
	-- The gap goes off at an angle, away from the camera's side, so the egg sits beside the monster in the picture
	-- instead of in front of the lens.
	local gapWay = if away == forward then CFrame.Angles(0, math.rad(-turn * settings.aheadAngle), 0):VectorToWorldSpace(forward) else away
	spot += gapWay * math.min(length * settings.aheadShare, eggSize.Y * settings.maxAhead)
	-- The egg stays where it landed, so the monster steps back to put that spot on it.
	model:PivotTo(model:GetPivot() + (ground - spot))

	-- The box round the monster and the egg, in the monster's own directions.
	local frame = CFrame.lookAt(ground, ground + forward)
	boxFrame, boxSize = model:GetBoundingBox()
	local low = Vector3.new(-eggSize.X / 2, 0, -eggSize.Z / 2)
	local high = Vector3.new(eggSize.X / 2, eggSize.Y, eggSize.Z / 2)
	for _, x in { -1, 1 } do
		for _, y in { -1, 1 } do
			for _, z in { -1, 1 } do
				local corner = frame:PointToObjectSpace(boxFrame * (boxSize / 2 * Vector3.new(x, y, z)))
				low = low:Min(corner)
				high = high:Max(corner)
			end
		end
	end
	local size = high - low
	local box = frame * CFrame.new((low + high) / 2)

	-- Where the shot starts: on the ground under the front foot on the camera's side, or under the front of a monster
	-- with no feet.
	boxFrame, boxSize = model:GetBoundingBox()
	leftFoot, rightFoot = frontFeet(model)
	local function feetSeenFrom(side: Vector3): Vector3
		if leftFoot and rightFoot then
			local near = if (leftFoot - rightFoot):Dot(side) > 0 then leftFoot else rightFoot
			return Vector3.new(near.X, ground.Y, near.Z)
		end
		local front = boxFrame.Position + forward * reach(boxFrame, boxSize, boxFrame.Position, forward) * 0.6
		return Vector3.new(front.X, ground.Y, front.Z)
	end
	local height = math.max(boxFrame.Position.Y + boxSize.Y / 2 - ground.Y, 1)
	local eyePoints = eyesOf(model)
	local eyes = height * EYE_FALLBACK
	if #eyePoints > 0 then
		eyes = 0
		for _, point in eyePoints do
			eyes += (point.Y - ground.Y) / #eyePoints
		end
	end

	-- At the end it stands framed in the middle of the screen: far enough back for its height and width to fit, and
	-- for its length to stay in front of the camera.
	local camera = workspace.CurrentCamera
	local tanUp = math.tan(math.rad(camera.FieldOfView) / 2)
	local tanAcross = tanUp * camera.ViewportSize.X / math.max(camera.ViewportSize.Y, 1)
	-- They fit in the band of the screen above the final text, and the camera aims above their middle to put them in it.
	local top = if band then math.clamp(band[1], 0, 0.5) else 0
	local bottom = if band then math.clamp(lerp(band[2], band[3] or band[2], bigness), top + settings.minBand, 1) else 1
	local tanBand = tanUp * (bottom - top)
	local endDistance = math.max(size.Y / 2 / tanBand, size.X / 2 / tanAcross) * settings.margin + size.Z * settings.depthShare
	endDistance = math.max(endDistance, size.Z / 2 * settings.margin)
	-- [Owner, 2026-11-07] Giants should feel enormous: the camera ends closer, so they fill the frame and can overflow it.
	endDistance *= lerp(1, settings.bigFill, bigness)
	local lift = ((top + bottom) / 2 - 0.5) * 2 * tanUp * endDistance

	-- The zoom: how much of the monster above its feet is in view at each distance, with the ground under the feet held
	-- feetAt of the way down the screen. It opens on the feet and, by the last number, still stops short of the eyes.
	local feetLift = (settings.feetAt - 0.5) * 2 * tanUp
	local inView = math.tan(math.rad(camera.FieldOfView) / 2 + math.atan(feetLift))
	local startDistance = math.min(math.max(height * settings.startWindow, settings.minWindow) / inView, endDistance * 0.5)
	local countDistance = math.min(height * settings.countWindow, eyes * settings.belowEyes) / inView
	countDistance = math.clamp(countDistance, startDistance * 1.3, endDistance * 0.8)
	local countShare = math.log(countDistance / startDistance) / math.log(endDistance / startDistance)

	-- It ends as far round as the walls allow.
	wallHalf = wallHalf or Throw.lane.width / 2
	local lane = Throw.lane
	local along = flat(lane.direction) or -Vector3.zAxis
	local side = math.abs((box.Position - lane.origin):Dot(along:Cross(Vector3.yAxis)))
	local room = math.max(wallHalf - settings.wallMargin - side, 0)
	local endYaw = math.min(math.rad(settings.endYaw), math.asin(math.clamp(room / endDistance, 0, 1)))

	local stage: Stage = {
		model = model,
		forward = forward,
		box = box,
		size = size,
		feet = feetSeenFrom(cameraSide),
		feetLift = feetLift,
		hold = settings.hold,
		whipTime = lerp(settings.whipTime, settings.bigWhipTime, bigness),
		countShare = countShare,
		distance = { startDistance, endDistance },
		yaw = { turn * math.rad(settings.startYaw), turn * endYaw },
		-- The camera starts just off the ground, wherever the feet sit on the screen.
		elevation = {
			math.asin(math.clamp((settings.floorGap - feetLift * startDistance) / startDistance, -1, 1)),
			math.rad(lerp(settings.endElevation, settings.bigEndElevation, bigness)),
		},
		focus = box.Position,
		aim = lift,
		floor = ground.Y + settings.floorGap,
		wallHalf = wallHalf,
	}

	-- A head low to the ground could sit right where the camera has to go, or show from the start. So it looks for a way in
	-- that's clear of the monster's body and keeps the eyes off the screen until the last number, trying further and
	-- further round, on both sides, up to from behind the foot. Clear comes first: seeing a face early beats going
	-- through it.
	local probe = Instance.new("Part")
	probe.Name = "RevealCameraProbe"
	probe.Shape = Enum.PartType.Ball
	probe.Anchored = true
	probe.CanCollide = false
	probe.CanQuery = false
	probe.CanTouch = false
	probe.Transparency = 1
	probe.Size = Vector3.one * math.clamp(startDistance * 0.25, 0.8, 16)
	probe.Parent = workspace
	local params = OverlapParams.new()
	params.FilterType = Enum.RaycastFilterType.Include
	params.FilterDescendantsInstances = { model }
	params.MaxParts = 1
	local function tryWay(): (boolean, boolean)
		local hidden = true
		for check = 0, PATH_CHECKS do
			local pulled = check / PATH_CHECKS
			local view = RevealCloseUp.cameraAt(stage, pulled)
			probe.CFrame = CFrame.new(view.Position)
			if #workspace:GetPartsInPart(probe, params) > 0 then
				return false, false
			end
			if pulled <= stage.countShare then
				for _, point in eyePoints do
					hidden = hidden and not onScreen(view, point, tanUp, tanAcross)
				end
			end
		end
		return true, hidden
	end
	pcall(withQuery, model, function()
		local fallback = nil
		for attempt = 0, settings.yawTries do
			for _, way in { turn, -turn } do
				stage.yaw[1] = way * math.rad(settings.startYaw + attempt * settings.yawStep)
				stage.feet = feetSeenFrom(right * -way)
				local clear, hidden = tryWay()
				if clear and hidden then
					return
				end
				if clear and not fallback then
					fallback = { yaw = stage.yaw[1], feet = stage.feet }
				end
			end
		end
		if fallback then
			stage.yaw[1], stage.feet = fallback.yaw, fallback.feet
			return
		end
		-- No way in from anywhere: it's a wide belly over the feet. It starts further back until it's clear.
		stage.yaw[1], stage.feet = turn * math.rad(settings.startYaw), feetSeenFrom(cameraSide)
		for _ = 1, settings.backTries do
			stage.distance[1] = math.min(stage.distance[1] * settings.backStep, countDistance * 0.8)
			stage.countShare = math.log(countDistance / stage.distance[1]) / math.log(endDistance / stage.distance[1])
			if tryWay() then
				return
			end
		end
	end)
	probe:Destroy()

	return stage
end

-- The camera stays between the corridor's walls, wherever they stand in this reveal.
local function insideWalls(position: Vector3, wallHalf: number): Vector3
	local lane = Throw.lane
	local along = flat(lane.direction) or -Vector3.zAxis
	if (position - lane.origin):Dot(along) < 0 then
		return position -- over the arena, behind the throw line
	end
	local across = along:Cross(Vector3.yAxis)
	local side = (position - lane.origin):Dot(across)
	local limit = wallHalf - settings.wallMargin
	return position - across * (side - math.clamp(side, -limit, limit))
end

-- The camera `pulled` of the way through the whole move (0 to 1). The distance grows evenly on a log scale, so the zoom
-- feels steady however big the monster is. Up to stage.countShare it looks at the feet, keeping them in the same place
-- on the screen while more and more of the body comes into view above them; past that, in the final move, it lifts to
-- the whole monster. Once in it holds still: the owner doesn't want it circling.
function RevealCloseUp.cameraAt(stage: Stage, pulled: number): CFrame
	local near, far = stage.distance[1], stage.distance[2]
	local distance = near * (far / near) ^ pulled
	local onFeet = stage.feet + Vector3.new(0, stage.feetLift * distance, 0)
	local whip = math.clamp((pulled - stage.countShare) / math.max(1 - stage.countShare, 1e-3), 0, 1)
	whip = whip * whip * (3 - 2 * whip)
	local focus = onFeet:Lerp(stage.focus, whip)
	local yaw = lerp(stage.yaw[1], stage.yaw[2], pulled)
	local elevation = lerp(stage.elevation[1], stage.elevation[2], pulled ^ RISE_POWER)
	local around = CFrame.Angles(0, yaw, 0):VectorToWorldSpace(stage.forward)
	local position = focus + (around * math.cos(elevation) + Vector3.yAxis * math.sin(elevation)) * distance
	position = Vector3.new(position.X, math.max(position.Y, stage.floor), position.Z)
	-- Only the aim moves to frame them above the text, never the camera itself, so it can't sink into the ground.
	return CFrame.lookAt(insideWalls(position, stage.wallHalf), focus + Vector3.new(0, stage.aim * whip, 0))
end

return RevealCloseUp
