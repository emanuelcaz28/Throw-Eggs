-- Brings plot dinos to life: each walks to a random spot on its plot, idles, and repeats, moving its
-- skeleton as it goes. Runs on each client only; the server just places the dino. The poses copy the
-- Walk and Idle loops in assets/models/build_forest.py, and the jaw and roar of the monsters that
-- have a Jaw bone copy build_volcano.py. Dinos without bones still walk, stiffly.
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

local function zero()
	return 0, 0, 0, 0
end

local function plus(a, b)
	return function(x)
		local ax, ay, az, ab = a(x)
		local bx, by, bz, bb = b(x)
		return ax + bx, ay + by, az + bz, ab + bb
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
	for _, bone in model:GetDescendants() do
		if bone:IsA("Bone") and bone.Name == "Jaw" then
			roars = true
		end
	end
	for _, bone in model:GetDescendants() do
		if bone:IsA("Bone") then
			-- The pose axes, in the bone's own space, measured while the dino stands at rest.
			local function axis(direction: Vector3): Vector3
				return bone.WorldCFrame:VectorToObjectSpace(pivot:VectorToWorldSpace(direction))
			end
			local idle = IDLE[bone.Name] or zero
			if roars and ROAR[bone.Name] then
				idle = plus(idle, ROAR[bone.Name])
			end
			table.insert(bones, {
				bone = bone,
				walk = WALK[bone.Name] or zero,
				idle = idle,
				pitch = axis(Vector3.xAxis),
				roll = axis(-Vector3.zAxis),
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
		facing = pivot.LookVector,
		speed = strideLength / DinoLife.strideSeconds,
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
	state.model:PivotTo(CFrame.lookAt(state.position, state.position + state.facing))
end

local function pose(state, dt: number)
	local goal = if state.target then 1 else 0
	local step = dt / DinoLife.blendTime
	state.blend += math.clamp(goal - state.blend, -step, step)
	local w = state.blend
	local eased = w * w * (3 - 2 * w)
	state.stride = (state.stride + dt / DinoLife.strideSeconds * TAU) % TAU
	state.idleClock = (state.idleClock + dt / DinoLife.idleLoopSeconds * TAU) % TAU
	local p, t = state.stride, state.idleClock
	for _, entry in state.bones do
		local wx, wy, wz, wb = entry.walk(p)
		local ix, iy, iz, ib = entry.idle(t)
		local rise = (ib + (wb - ib) * eased) * state.scale
		entry.bone.Transform = CFrame.new(entry.yaw * rise)
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
