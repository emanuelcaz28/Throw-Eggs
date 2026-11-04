-- The close-up and pull back after the walk (docs/GAME_SPEC.md section 7). The caught monster is simply there,
-- standing still at its real size where its walk ended, facing the way it walked, with the egg on the ground a clear
-- gap ahead of its front feet (half its length, Config/Reveal closeUp aheadShare). The camera opens on a close-up of the
-- egg with the feet behind it, then pulls back and up until the whole monster stands framed over the egg, and holds
-- still there. The monster doesn't pop out of the egg: it walked up to it. Display only.
-- Numbers live in Config/Reveal closeUp. RevealController plays it.
local ContentProvider = game:GetService("ContentProvider")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local DinoModel = require(ReplicatedStorage.Shared.DinoModel)
local Map = require(ReplicatedStorage.Shared.Config.Map)
local Reveal = require(ReplicatedStorage.Shared.Config.Reveal)
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
	hold: number, -- seconds the close-up holds
	pullTime: number, -- seconds the pull back takes
	turn: number, -- 1 or -1: which side of the monster's front the camera looks from
	focus: { Vector3 }, -- what the camera looks at: the egg's middle in the close-up, the box's middle at the end
	distance: { number }, -- how far the camera is from it, at the start and the end
	elevation: { number }, -- radians it looks down from, at the start and the end
	aim: number, -- studs the camera aims above the end's focus (below when negative), to frame them above the text
	floor: number, -- the camera never goes below this height
	slow: boolean?, -- the slow reveal of lucky catches: across to the monster early, then up its body, feet to head
	feet: Vector3, -- the middle of the monster's feet, on the ground
}

-- Builds the caught monster standing over the egg, at its real size, facing `approach` (the way it walked; the
-- throw's way if unknown), and works out the camera's moves. `climb` is how long the name and counter take. `band` is
-- the part of the screen to frame them in at the end, as shares of its height from the top: {top, bottom for the
-- smallest monsters, bottom for the biggest}. The final text covers the rest. The whole screen when left out. `slow`
-- (lucky catches): the close-up holds only a moment, and the pull back takes the whole rest of the climb.
function RevealCloseUp.stage(
	catch,
	egg: BasePart,
	approach: Vector3?,
	climb: number,
	random: Random?,
	band: { number }?,
	slow: boolean?
): Stage
	random = random or Random.new()
	local eggSize = egg.Size
	local ground = egg.Position - Vector3.new(0, eggSize.Y / 2, 0)
	local forward = flat(approach) or flat(Throw.lane.direction) or -Vector3.zAxis
	local right = forward:Cross(Vector3.yAxis)
	local scale = DinoModel.statueScale(catch.id, catch.size)
	local bigness = logShare(scale, 1, Reveal.walk.bigScale)
	local closeElevation = math.rad(lerp(settings.elevation, settings.bigElevation, bigness))

	local turn = if random:NextNumber() < 0.5 then -1 else 1
	local cameraSide = right * -turn -- the side the camera looks from, a little round from the monster's front

	local model = DinoModel.build(catch.id, catch.mutation, ground, scale)
	model.Name = "RevealDino"
	local turned = facesPlusZ(model)
	model:PivotTo(CFrame.lookAt(ground, ground + (if turned then -forward else forward)))
	model.Parent = workspace

	-- The egg goes between the front feet, far enough ahead of them for both feet to stand in the close-up...
	local spot = ground
	local halfGap = 0
	local leftFoot, rightFoot = frontFeet(model)
	if leftFoot and rightFoot then
		local middle = (leftFoot + rightFoot) / 2
		spot = Vector3.new(middle.X, ground.Y, middle.Z)
		halfGap = math.abs((leftFoot - rightFoot):Dot(right)) / 2
	end
	local closeDistance = eggSize.Y * settings.distance * math.cos(closeElevation)
	spot += forward * math.max(halfGap * settings.feetBehind - closeDistance, 0)
	-- ...and further ahead if the monster is too low there to stand over it. A monster hardly taller than the egg
	-- would hide behind it, so then the egg goes beside its front feet instead, on the camera's side.
	local boxFrame, boxSize = model:GetBoundingBox()
	local away = if boxSize.Y < eggSize.Y * settings.besideBelow then cameraSide else forward
	local queryable = {}
	for _, part in model:GetDescendants() do
		if part:IsA("BasePart") then
			queryable[part] = part.CanQuery
			part.CanQuery = true
		end
	end
	local upTo = reach(boxFrame, boxSize, spot, away) + eggSize.Z
	local ok, shift = pcall(clearAlong, model, eggSize, spot, away, upTo)
	for part, canQuery in queryable do
		part.CanQuery = canQuery
	end
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
	-- Where its front feet now stand: the slow reveal's view starts there and climbs the body.
	local frontLeft, frontRight = frontFeet(model)
	local feet = if frontLeft and frontRight then (frontLeft + frontRight) / 2 else model:GetBoundingBox().Position

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
	-- A monster hardly bigger than the egg is already in the close-up, so that comes in closer to leave room to
	-- pull back.
	local startDistance = math.clamp(endDistance / settings.minPullBack, eggSize.Y * settings.nearest, eggSize.Y * settings.distance)
	endDistance = math.max(endDistance, startDistance * settings.minPullBack)
	local lift = ((top + bottom) / 2 - 0.5) * 2 * tanUp * endDistance

	local hold = math.clamp(climb * settings.holdShare, settings.minHold, settings.maxHold)
	local pullTime = lerp(settings.pullTime, settings.bigPullTime, bigness)
	pullTime = math.max(math.min(pullTime, climb - hold), pullTime * settings.minPullShare)
	if slow then
		hold = settings.slowHold
		pullTime = math.max(climb - hold, pullTime)
	end

	return {
		model = model,
		forward = forward,
		box = box,
		size = size,
		hold = hold,
		pullTime = pullTime,
		turn = turn,
		focus = { ground + Vector3.new(0, eggSize.Y / 2, 0), box.Position },
		aim = lift,
		floor = ground.Y + eggSize.Y,
		slow = slow,
		feet = Vector3.new(feet.X, ground.Y + eggSize.Y / 2, feet.Z),
		distance = { startDistance, endDistance },
		elevation = { closeElevation, math.rad(settings.endElevation) },
	}
end

-- Down in the corridor the camera stays between its walls; the higher it is above their rim, the further out it may
-- go, so it never cuts through a wall on its way up.
local function insideWalls(position: Vector3): Vector3
	local lane = Throw.lane
	local along = flat(lane.direction) or -Vector3.zAxis
	if (position - lane.origin):Dot(along) < 0 then
		return position -- over the arena, behind the throw line
	end
	local across = along:Cross(Vector3.yAxis)
	local side = (position - lane.origin):Dot(across)
	local limit = lane.width / 2 - settings.wallMargin + math.max(position.Y - Map.walls.rimY, 0) * settings.overWalls
	return position - across * (side - math.clamp(side, -limit, limit))
end

-- The camera `pulled` of the way through the pull back (0 to 1, eased). The distance grows evenly on a log scale, so
-- a giant's long pull back feels as steady as a small one's, and the camera lifts its eyes from the egg to the
-- monster as it goes. Once pulled back it holds still: the owner doesn't want it circling.
function RevealCloseUp.cameraAt(stage: Stage, pulled: number): CFrame
	local near, far = stage.distance[1], stage.distance[2]
	local distance = near * (far / near) ^ pulled
	local focus = stage.focus[1]:Lerp(stage.focus[2], (distance - near) / (far - near))
	if stage.slow then
		-- Across from the egg to the monster's feet over the first part, then up its body as the camera pulls back,
		-- slowly at first, so the head comes into view last.
		local across = math.clamp(pulled / settings.slowAcross, 0, 1)
		across = across * across * (3 - 2 * across)
		local ground = stage.focus[1]:Lerp(stage.feet, across)
		local up = pulled ^ settings.slowRise
		focus = Vector3.new(
			lerp(ground.X, stage.focus[2].X, up),
			lerp(ground.Y, stage.focus[2].Y, up),
			lerp(ground.Z, stage.focus[2].Z, up)
		)
	end
	local elevation = lerp(stage.elevation[1], stage.elevation[2], pulled)
	local yaw = stage.turn * math.rad(settings.yaw)
	local around = CFrame.Angles(0, yaw, 0):VectorToWorldSpace(stage.forward)
	local position = focus + (around * math.cos(elevation) + Vector3.yAxis * math.sin(elevation)) * distance
	position = Vector3.new(position.X, math.max(position.Y, stage.floor), position.Z)
	-- Only the aim moves to frame them above the text, never the camera itself, so it can't sink into the ground.
	local share = (distance - near) / (far - near)
	return CFrame.lookAt(insideWalls(position), focus + Vector3.new(0, stage.aim * share, 0))
end

return RevealCloseUp
