-- Makes the map's props move on this player's screen (Config/PropMotion): crystal shards bobbing and
-- turning, moons going round their planets, observatory domes turning, stardust pouring down the walls,
-- comets gliding across the sky. The server places the props once and they hold still there; the movement
-- is drawn here only, so it costs the server and the network nothing. Only props near the camera move.
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local PropMotion = require(ReplicatedStorage.Shared.Config.PropMotion)
local Roles = require(ReplicatedStorage.Shared.Roles)

local PropMotionController = {}

local TAU = 2 * math.pi

type Motion = { [string]: any }
type Mover = { part: BasePart, base: CFrame, motion: Motion, color: Color3 }
type Drift = { parts: { BasePart }, bases: { CFrame }, ahead: Vector3, motion: Motion, transparency: number }
type Prop = { pivot: CFrame, scale: number, phase: number, movers: { Mover }, drift: Drift? }

local props: { Prop } = {}
local seen: { [Instance]: boolean } = {}

-- The same prop doesn't move in step with its copies: each starts at a different point in its cycle.
local function phaseOf(position: Vector3): number
	return math.abs(position.X * 0.137 + position.Z * 0.071) % 1
end

local function add(model: Instance)
	if seen[model] or not model:IsA("Model") then
		return
	end
	local rules = PropMotion.props[model.Name]
	if not rules then
		return
	end
	seen[model] = true
	local pivot = model:GetPivot()
	local prop: Prop = { pivot = pivot, scale = model:GetScale(), phase = phaseOf(pivot.Position), movers = {}, drift = nil }
	local parts = {}
	for _, part in model:GetDescendants() do
		if part:IsA("BasePart") then
			table.insert(parts, part)
			local motion = rules[Roles.of(part)]
			if motion then
				table.insert(prop.movers, { part = part, base = part.CFrame, motion = motion, color = part.Color })
			end
		end
	end
	local drift = rules["*"]
	if drift then
		local head, rest, heads, others = Vector3.zero, Vector3.zero, 0, 0
		local bases = {}
		for index, part in parts do
			bases[index] = part.CFrame
			if Roles.of(part) == drift.head then
				head += part.Position
				heads += 1
			else
				rest += part.Position
				others += 1
			end
		end
		local ahead = if heads > 0 and others > 0 then (head / heads - rest / others) else Vector3.xAxis
		prop.drift = { parts = parts, bases = bases, ahead = ahead.Unit, motion = drift, transparency = 0 }
	end
	table.insert(props, prop)
end

local function watch(folder: Instance)
	for _, child in folder:GetChildren() do
		add(child)
	end
	folder.ChildAdded:Connect(add)
end

-- Where a moving part is at time t.
local function placeOf(prop: Prop, mover: Mover, t: number): CFrame
	local motion = mover.motion
	local cf = mover.base
	local cycle = if motion.period then t / motion.period + prop.phase else 0
	if motion.spin then
		local centre = if motion.about == "self" then cf.Position else prop.pivot.Position
		local turn = CFrame.Angles(0, math.rad(motion.spin) * t, 0)
		cf = CFrame.new(centre) * turn * CFrame.new(-centre) * cf
	end
	if motion.bob then
		cf += Vector3.new(0, motion.bob * prop.scale * math.sin(TAU * cycle), 0)
	end
	if motion.fall then
		cf -= Vector3.new(0, motion.fall * prop.scale * (cycle % 1), 0)
	end
	return cf
end

function PropMotionController.start()
	task.spawn(function()
		local map = workspace:WaitForChild("Map")
		watch(map:WaitForChild("CorridorDecor"))
		local arena = map:FindFirstChild("ArenaDecor")
		if arena then
			watch(arena)
		end
	end)

	local start = os.clock()
	local parts: { BasePart } = {}
	local cframes: { CFrame } = {}
	RunService.RenderStepped:Connect(function()
		local t = os.clock() - start
		local camera = workspace.CurrentCamera.CFrame.Position
		local count = 0
		table.clear(parts)
		table.clear(cframes)
		for _, prop in props do
			if (prop.pivot.Position - camera).Magnitude > PropMotion.range then
				continue
			end
			for _, mover in prop.movers do
				local motion = mover.motion
				if motion.spin or motion.bob or motion.fall then
					count += 1
					parts[count] = mover.part
					cframes[count] = placeOf(prop, mover, t)
				end
				if motion.pulse then
					local wave = 0.5 + 0.5 * math.sin(TAU * (t / motion.period + prop.phase))
					local share = motion.pulse + (1 - motion.pulse) * wave
					local c = mover.color
					mover.part.Color = Color3.new(c.R * share, c.G * share, c.B * share)
				end
			end
			local drift = prop.drift
			if drift then
				local motion = drift.motion
				local cycle = (t / motion.period + prop.phase) % 1
				local offset = drift.ahead * motion.drift * (cycle - 0.5)
				for index, part in drift.parts do
					count += 1
					parts[count] = part
					cframes[count] = drift.bases[index] + offset
				end
				-- Fades out at the end of its path and in at the start, so the jump back isn't seen.
				local edge = math.min(cycle, 1 - cycle) / motion.fade
				local transparency = 1 - math.clamp(edge, 0, 1)
				if math.abs(transparency - drift.transparency) > 0.02 then
					drift.transparency = transparency
					for _, part in drift.parts do
						part.Transparency = transparency
					end
				end
			end
		end
		if count > 0 then
			workspace:BulkMoveTo(parts, cframes, Enum.BulkMoveMode.FireCFrameChanged)
		end
	end)
end

return PropMotionController
