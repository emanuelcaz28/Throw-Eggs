-- Brings plot dinos to life: each walks to a random spot on its plot, idles, and repeats, moving its
-- skeleton as it goes. Runs on each client only; the server just places the dino. The poses copy the
-- Walk and Idle loops in assets/models/build_forest.py, and the jaw and roar of the monsters that
-- have a Jaw bone copy build_volcano.py. Monsters with a Swim bone swim and hover instead (SWIM and HOVER,
-- copying build_abyss_monsters.py). Dinos without bones still walk, stiffly.
local CollectionService = game:GetService("CollectionService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local Config = ReplicatedStorage.Shared.Config
local DinoLife = require(Config.DinoLife)
local Plot = require(Config.Plot)

local DinoLifeController = {}

local TAU = 2 * math.pi
local sin, cos = math.sin, math.cos

-- Each pose returns pitch, roll, yaw and how far the bone rises.
-- p runs through one stride; t runs through one idle loop.
local WALK = {}
local IDLE = {}

WALK.Spine = function(p)
	return 0.02 * sin(2 * p), 0.05 * sin(p), 0.05 * sin(p), 0.07 * cos(2 * p)
end
IDLE.Spine = function(t)
	return 0.025 * sin(4 * t), 0, 0, 0.03 * sin(4 * t)
end

for letter, phase in { L = 0, R = math.pi } do
	local side = if letter == "L" then -1 else 1
	WALK["Leg" .. letter] = function(p)
		return 0.45 * sin(p + phase), 0, 0, 0
	end
	WALK["Shin" .. letter] = function(p)
		return -0.6 * (0.5 + 0.5 * cos(p + phase)) ^ 2, 0, 0, 0
	end
	WALK["Arm" .. letter] = function(p)
		return -0.3 * sin(p + phase), 0, 0, 0
	end
	WALK["Wing" .. letter] = function(p)
		return 0, side * 0.14 * sin(2 * p), 0, 0
	end
	WALK["WingTip" .. letter] = function(p)
		return 0, side * 0.1 * sin(2 * p - 0.8), 0, 0
	end
	IDLE["Arm" .. letter] = function(t)
		return 0.08 * sin(4 * t + 0.5), 0, 0, 0
	end
	IDLE["Wing" .. letter] = function(t)
		return 0, side * 0.07 * sin(4 * t), 0, 0
	end
	IDLE["WingTip" .. letter] = function(t)
		return 0, side * 0.06 * sin(4 * t - 0.8), 0, 0
	end
end

-- Four-legged walkers move opposite corners together.
for name, phase in { FrontL = 0, BackR = 0, FrontR = math.pi, BackL = math.pi } do
	WALK[name] = function(p)
		return 0.32 * sin(p + phase), 0, 0, 0
	end
end

for i = 1, 3 do
	WALK["Tail" .. i] = function(p)
		return 0.03 * sin(2 * p - i * 0.6), 0, 0.16 * sin(p - i * 0.7), 0
	end
	IDLE["Tail" .. i] = function(t)
		return 0.02 * sin(4 * t - i * 0.5), 0, 0.14 * sin(2 * t - i * 0.6), 0
	end
end

WALK.Neck = function(p)
	return 0.05 * sin(2 * p + 0.5), 0, 0.05 * sin(p + 0.6), 0
end
IDLE.Neck = function(t)
	return 0.05 * sin(2 * t + 1), 0, 0.14 * sin(t), 0
end
WALK.Head = function(p)
	return -0.06 * sin(2 * p + 0.5), 0, 0.08 * sin(p + 1.2), 0
end
IDLE.Head = function(t)
	return 0.09 * sin(3 * t), 0, 0.36 * sin(t) + 0.08 * sin(3 * t), 0
end

-- Monsters with a Jaw bone (from Volcano on) snap it in time with their steps, and roar once
-- per idle loop: head thrown up, jaw dropped wide, arms out and a shake of the head. ROAR is added on
-- top of the idle above, for those monsters only.
local function roar(t: number): number
	return ((1 - cos(t)) / 2) ^ 10 -- 0 most of the loop, up to 1 halfway through it
end

WALK.Jaw = function(p)
	return -0.08 * (0.5 + 0.5 * sin(2 * p)), 0, 0, 0
end
IDLE.Jaw = function(t)
	return -0.03 * (0.5 + 0.5 * sin(4 * t)) - 0.55 * roar(t), 0, 0, 0
end

local ROAR = {}
ROAR.Spine = function(t)
	return 0.03 * roar(t), 0, 0, 0
end
ROAR.ArmL = function(t)
	return 0.45 * roar(t), 0, 0, 0
end
ROAR.ArmR = ROAR.ArmL
ROAR.Tail1 = function(t)
	return 0.08 * roar(t), 0, 0, 0
end
ROAR.Neck = function(t)
	return 0.12 * roar(t), 0, 0, 0
end
ROAR.Head = function(t)
	local r = roar(t)
	return 0.3 * r, 0, 0.08 * sin(14 * t) * r, 0
end

-- Monsters with a Swim bone (from The Abyss on) swim instead of walking: SWIM while they move and HOVER while
-- they wait, which ends each loop with an attack (they rear up and lunge, jaw wide, shaking their head and
-- thrashing their tail). The poses copy assets/models/build_abyss_monsters.py. Each also returns surge: how far
-- the bone moves forward, for the lunge. Their models float just above the ground, so they hover over the base.
local SWIM = {}
local HOVER = {}

-- Spiral Gary's eight tentacles ring its beak; tentacle n sits at this angle round the front (0 = its right).
local function tentacleTurn(n: number, spread: number, wriggle: number): (number, number)
	local angle = (n - 1) * TAU / 8 + math.pi / 8
	return spread * sin(angle) + wriggle * cos(angle), -spread * cos(angle) + wriggle * sin(angle)
end

SWIM.Swim = function(p)
	return 0.03 * sin(2 * p), 0.05 * sin(p), -0.05 * sin(p), 0.06 * sin(2 * p), 0
end
HOVER.Swim = function(t)
	local r = roar(t)
	return 0.02 * sin(2 * t) + 0.12 * r, 0.03 * sin(t) + 0.05 * sin(14 * t) * r, 0, 0.12 * sin(2 * t), 0.6 * r
end
SWIM.Head = function(p)
	return 0.02 * sin(2 * p), 0, -0.06 * sin(p), 0, 0
end
HOVER.Head = function(t)
	local r = roar(t)
	return 0.06 * sin(3 * t) + 0.22 * r, 0, 0.15 * sin(t) + 0.05 * sin(3 * t) + 0.12 * sin(14 * t) * r, 0, 0
end
for i = 1, 3 do
	SWIM["Neck" .. i] = function(p)
		return 0.03 * sin(2 * p - 0.4 * i), 0, -0.05 * sin(p - 0.4 * i), 0, 0
	end
	HOVER["Neck" .. i] = function(t)
		return 0.05 * sin(2 * t + i) + 0.1 * roar(t), 0, 0.12 * sin(t - 0.3 * i), 0, 0
	end
end
for i = 1, 4 do
	SWIM["Tail" .. i] = function(p)
		return 0.02 * sin(2 * p - i), 0, (0.14 + 0.05 * i) * sin(p - 0.75 * i), 0, 0
	end
	HOVER["Tail" .. i] = function(t)
		return 0, 0, (0.06 + 0.03 * i) * sin(4 * t - 0.75 * i) + 0.22 * sin(10 * t - i) * roar(t), 0, 0
	end
end
for letter, side in { L = -1, R = 1 } do
	SWIM["Fin" .. letter] = function(p)
		return 0.08 * sin(p + 1), side * 0.18 * sin(p), 0, 0, 0
	end
	HOVER["Fin" .. letter] = function(t)
		return 0, side * (0.1 * sin(4 * t) + 0.4 * roar(t)), 0, 0, 0
	end
	-- Front and back flippers beat in turn.
	for pair, phase in { F = 0, B = math.pi } do
		SWIM["Flipper" .. pair .. letter] = function(p)
			return 0.25 * cos(p + phase), side * 0.45 * sin(p + phase), 0, 0, 0
		end
		HOVER["Flipper" .. pair .. letter] = function(t)
			return 0.1 * cos(4 * t + phase), side * (0.18 * sin(4 * t + phase) - 0.45 * roar(t)), 0, 0, 0
		end
	end
end
SWIM.Jaw = function(p)
	return -0.1 * (0.5 + 0.5 * sin(2 * p)), 0, 0, 0, 0
end
HOVER.Jaw = function(t)
	return -0.04 * (0.5 + 0.5 * sin(4 * t)) - 0.7 * roar(t), 0, 0, 0, 0
end
SWIM.Lure = function(p)
	return 0.15 * sin(2 * p), 0, 0.1 * sin(p), 0, 0
end
HOVER.Lure = function(t)
	return 0.1 * sin(3 * t) - 0.3 * roar(t), 0, 0.25 * sin(t), 0, 0
end
SWIM.LureTip = function(p)
	return 0.2 * sin(2 * p - 1), 0, 0, 0, 0
end
HOVER.LureTip = function(t)
	return 0.15 * sin(3 * t - 1) - 0.25 * roar(t), 0, 0, 0, 0
end
for n = 1, 8 do
	-- Each tentacle on two bones: they pulse open and shut as it swims, and flare wide in the attack.
	SWIM["Tentacle" .. n] = function(p)
		local pitch, yaw = tentacleTurn(n, 0.08 + 0.16 * (0.5 + 0.5 * sin(p)), 0.12 * sin(2 * p - 0.8 * n))
		return pitch, 0, yaw, 0, 0
	end
	SWIM["Tentacle" .. n .. "b"] = function(p)
		local pitch, yaw = tentacleTurn(n, 0.18 * sin(p - 1.2), 0.18 * sin(2 * p - 0.8 * n - 1))
		return pitch, 0, yaw, 0, 0
	end
	HOVER["Tentacle" .. n] = function(t)
		local pitch, yaw = tentacleTurn(n, 0.1 + 0.06 * sin(2 * t) + 0.5 * roar(t), 0.14 * sin(4 * t - 0.8 * n))
		return pitch, 0, yaw, 0, 0
	end
	HOVER["Tentacle" .. n .. "b"] = function(t)
		local r = roar(t)
		local pitch, yaw =
			tentacleTurn(n, 0.1 * sin(2 * t - 1) + 0.35 * r, 0.16 * sin(4 * t - 0.8 * n - 1) + 0.1 * sin(14 * t) * r)
		return pitch, 0, yaw, 0, 0
	end
end

local function zero()
	return 0, 0, 0, 0, 0
end

local function plus(a, b)
	return function(x)
		local ax, ay, az, ab, asurge = a(x)
		local bx, by, bz, bb, bsurge = b(x)
		return ax + bx, ay + by, az + bz, ab + bb, (asurge or 0) + (bsurge or 0)
	end
end

local dinos: { [Model]: any } = {}

local function randomSpot(state): Vector3
	local half = Plot.size / 2
	local x = (math.random() * 2 - 1) * (half.X - Plot.placeMargin)
	local z = (math.random() * 2 - 1) * (half.Z - Plot.placeMargin)
	return state.centre + Vector3.new(x, 0, z)
end

local function idleTime(): number
	return DinoLife.idleSeconds + (math.random() * 2 - 1) * DinoLife.idleJitter
end

local function add(model: Model)
	local plotIndex = model:GetAttribute("PlotIndex")
	local position = plotIndex and Plot.positions[plotIndex]
	if not position then
		return
	end
	local pivot = model:GetPivot()
	local scale = model:GetScale()
	local bones = {}
	local legHeight = nil
	local roars = false
	local swims = false
	local front, back = nil, nil
	for _, bone in model:GetDescendants() do
		if bone:IsA("Bone") then
			roars = roars or bone.Name == "Jaw"
			swims = swims or bone.Name == "Swim"
			if bone.Name == "Jaw" or (bone.Name == "Head" and not front) then
				front = bone
			end
			if bone.Name == "Tail1" or ((bone.Name == "Spine" or bone.Name == "Swim") and not back) then
				back = bone
			end
		end
	end
	-- Which way the model faces from its pivot, from where its head is against its tail. Most imported models
	-- face the pivot's +Z (the importer turns them round) and a few its -Z, so the poses take the model's own
	-- right and forward, and it moves head first whichever it is.
	local turned = front ~= nil
		and back ~= nil
		and pivot:PointToObjectSpace(front.WorldPosition).Z > pivot:PointToObjectSpace(back.WorldPosition).Z
	local right = if turned then -Vector3.xAxis else Vector3.xAxis
	local ahead = if turned then Vector3.zAxis else -Vector3.zAxis
	for _, bone in model:GetDescendants() do
		if bone:IsA("Bone") then
			-- The pose axes, in the bone's own space, measured while the dino stands at rest.
			local function axis(direction: Vector3): Vector3
				return bone.WorldCFrame:VectorToObjectSpace(pivot:VectorToWorldSpace(direction))
			end
			local walk = (if swims then SWIM else WALK)[bone.Name] or zero
			local idle = (if swims then HOVER else IDLE)[bone.Name] or zero
			if roars and not swims and ROAR[bone.Name] then
				idle = plus(idle, ROAR[bone.Name])
			end
			table.insert(bones, {
				bone = bone,
				walk = walk,
				idle = idle,
				pitch = axis(right),
				roll = axis(ahead),
				yaw = axis(Vector3.yAxis),
			})
			if bone.Name == "LegL" or bone.Name == "FrontL" then
				legHeight = bone.WorldPosition.Y - pivot.Y
			end
		end
	end
	-- Fast enough that the feet don't look like they slide: a stride covers about this much ground.
	local isBiped = model:FindFirstChild("LegL", true) ~= nil
	local strideLength = (legHeight or 1.5 * scale) * (if isBiped then 1.74 else 1.26)
	dinos[model] = {
		model = model,
		bones = bones,
		scale = scale,
		centre = Vector3.new(position.X, pivot.Y, position.Z),
		position = pivot.Position,
		facing = pivot:VectorToWorldSpace(ahead), -- where its head points
		turned = turned,
		speed = if swims then DinoLife.swim.speed * scale else strideLength / DinoLife.strideSeconds,
		strideSeconds = if swims then DinoLife.swim.strideSeconds else DinoLife.strideSeconds,
		target = nil,
		idleLeft = math.random() * DinoLife.idleSeconds, -- so a plot's dinos don't all set off together
		blend = 0,
		stride = math.random() * TAU,
		idleClock = math.random() * TAU,
		frame = math.random(0, DinoLife.farFrameSkip),
		pending = 0,
	}
end

local function moveAlong(state, dt: number)
	if not state.target then
		state.idleLeft -= dt
		if state.idleLeft <= 0 then
			state.target = randomSpot(state)
		end
		return
	end
	local offset = state.target - state.position
	if offset.Magnitude < DinoLife.arriveDistance * state.scale then
		state.target = nil
		state.idleLeft = idleTime()
		return
	end
	local wanted = offset.Unit
	local angle = math.acos(math.clamp(state.facing:Dot(wanted), -1, 1))
	local turn = DinoLife.turnSpeed * dt
	if angle > 0.001 then
		local sign = if state.facing:Cross(wanted).Y >= 0 then 1 else -1
		state.facing = CFrame.Angles(0, sign * math.min(turn, angle), 0):VectorToWorldSpace(state.facing)
	end
	-- It slows while turning, so it doesn't drift sideways.
	local pace = math.max(state.facing:Dot(wanted), 0)
	state.position += state.facing * state.speed * pace * dt
	local look = if state.turned then -state.facing else state.facing
	state.model:PivotTo(CFrame.lookAt(state.position, state.position + look))
end

local function pose(state, dt: number)
	local goal = if state.target then 1 else 0
	local step = dt / DinoLife.blendTime
	state.blend += math.clamp(goal - state.blend, -step, step)
	local w = state.blend
	local eased = w * w * (3 - 2 * w)
	state.stride = (state.stride + dt / state.strideSeconds * TAU) % TAU
	state.idleClock = (state.idleClock + dt / DinoLife.idleLoopSeconds * TAU) % TAU
	local p, t = state.stride, state.idleClock
	for _, entry in state.bones do
		local wx, wy, wz, wb, ws = entry.walk(p)
		local ix, iy, iz, ib, is = entry.idle(t)
		local rise = (ib + (wb - ib) * eased) * state.scale
		local surge = ((is or 0) + ((ws or 0) - (is or 0)) * eased) * state.scale
		entry.bone.Transform = CFrame.new(entry.yaw * rise + entry.roll * surge)
			* CFrame.fromAxisAngle(entry.pitch, ix + (wx - ix) * eased)
			* CFrame.fromAxisAngle(entry.roll, iy + (wy - iy) * eased)
			* CFrame.fromAxisAngle(entry.yaw, iz + (wz - iz) * eased)
	end
end

local function step(dt: number)
	local cameraPosition = workspace.CurrentCamera.CFrame.Position
	for _, state in dinos do
		state.pending += dt
		state.frame += 1
		local distance = (state.position - cameraPosition).Magnitude
		local skip = if distance > DinoLife.farDistance
			then DinoLife.farFrameSkip
			elseif distance > DinoLife.nearDistance then DinoLife.midFrameSkip
			else 1
		if state.frame % skip == 0 then
			local elapsed = state.pending
			state.pending = 0
			moveAlong(state, elapsed)
			pose(state, elapsed)
		end
	end
end

function DinoLifeController.start()
	for _, model in CollectionService:GetTagged(DinoLife.tag) do
		add(model)
	end
	CollectionService:GetInstanceAddedSignal(DinoLife.tag):Connect(function(model)
		-- Waits a frame so a model that's still arriving has its parts.
		task.defer(add, model)
	end)
	CollectionService:GetInstanceRemovedSignal(DinoLife.tag):Connect(function(model)
		dinos[model] = nil
	end)
	RunService.Heartbeat:Connect(step)
end

return DinoLifeController
