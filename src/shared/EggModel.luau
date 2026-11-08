-- The Egg Shop's eggs as made in Blender (assets/models/build_eggs.py), imported into ReplicatedStorage.Assets.Eggs
-- as egg_<id> (studio_tidy.py puts them there; each one's pivot is its foot, Y up). Every part of an egg's top half
-- has a name ending in "Lid"; the rest is its bottom half. Both halves are closed by a disc of white with a yolk.
--
-- The thrown egg stays the plain Part the throw and the reveal move about (ThrowController, RevealWalk,
-- RevealCloseUp): dress() hides it and puts the Blender egg on it, following it every frame and growing with it.
-- bounce() plays its touch-down: it squashes, hops on twice, comes upright, rocks on its foot and trembles
-- (Config/Throw landing.bounce). Then split() cuts it in half where it lands (Config/Throw landing.split, the same numbers as build_eggs.py's SPLIT, whose
-- egg_slice.mp4 shows it): a white streak sweeps across its middle, the top half slides off, tips over and lands upside
-- down beside the bottom half, its white and yolk facing up, and rocks to a stop, while white, yolk and bits of shell
-- splash out round it (landing.splash). An egg with no model yet stays the
-- coloured ball and isn't cut, so the game works before the import.
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local Roles = require(script.Parent.Roles)
local Throw = require(script.Parent.Config.Throw)

local EggModel = {}

local settings = Throw.landing.split
local LID = "Lid"
local STREAK_THICK = 0.16 -- the slice's streak, studs at size 1 (build_eggs.py slice_video)

local function template(eggId: string): Model?
	local assets = ReplicatedStorage:FindFirstChild("Assets")
	local eggs = assets and assets:FindFirstChild("Eggs")
	local found = eggs and eggs:FindFirstChild(`egg_{eggId}`)
	return if found and found:IsA("Model") then found else nil
end

-- Whether this egg has its Blender model in the place.
function EggModel.has(eggId: string): boolean
	return template(eggId) ~= nil
end

-- A copy of an egg's Blender model, whole, its pivot at its foot, glowing parts Neon. nil if it has none yet.
function EggModel.clone(eggId: string): Model?
	local source = template(eggId)
	if not source then
		return nil
	end
	local model = source:Clone()
	for _, part in model:GetDescendants() do
		if part:IsA("BasePart") then
			part.Anchored = true
			part.CanCollide = false
			part.CanQuery = false
			part.CanTouch = false
			if Roles.glowing[part.Name] then
				part.Material = Enum.Material.Neon
				part.MaterialVariant = ""
			end
		end
	end
	return model
end

local function smooth(u: number): number
	return u * u * (3 - 2 * u)
end

-- Where the top half is s seconds after the egg touches down: how far across from the egg's foot its cut's middle is,
-- how far up, and how far it has tipped over (radians, towards +across), in studs at size 1. The same as split_pose in
-- build_eggs.py.
function EggModel.lidPose(s: number): (number, number, number)
	local c = settings.cut * settings.height
	local flipped = settings.height - c - settings.sink -- upside down, its tip on the ground, its cut this high
	local beside = 2 * settings.radius + settings.gap
	local push = settings.push * settings.radius
	local t = s - settings.delay - settings.slice
	if t <= 0 then
		return 0, c, 0
	end
	local lifted = c + settings.lift -- lifted clear of the bottom half's yolk as it slides
	if t < settings.slide then -- slides off along the cut
		local u = smooth(t / settings.slide)
		return push * u, c + settings.lift * u, 0
	end
	t -= settings.slide
	if t < settings.fall then -- tips over and drops beside it, upside down
		local v = t / settings.fall
		return push + (beside - push) * v, lifted + (flipped - lifted) * v + settings.hop * 4 * v * (1 - v), math.pi * smooth(v)
	end
	t -= settings.fall
	local rock = settings.rock * math.sin(t / settings.rockTime * 3 * math.pi) * math.max(0, 1 - t / settings.rockTime) ^ 2
	return beside, flipped, math.pi + rock
end

-- The white streak across the egg's middle s seconds after touching down: how far across it is (-1 to 1) and how
-- faded (0 to 1), or nil when it isn't showing. The same as slice_streak in build_eggs.py.
function EggModel.streak(s: number): (number?, number?)
	local t = s - settings.delay
	if t < 0 or t > settings.slice * 1.6 then
		return nil, nil
	end
	local u = math.min(t / settings.slice, 1)
	return -1 + 2 * smooth(u), math.max(0, (t - settings.slice) / (settings.slice * 0.6))
end

type Piece = { part: BasePart, offset: CFrame, size: Vector3 } -- offset from its half's pivot, size at size 1

type Dressed = {
	eggId: string,
	holder: Model,
	bottom: { Piece },
	lid: { Piece },
	colors: { white: Color3, yolk: Color3, shell: Color3 },
	scale: number,
	squash: Vector3, -- how much wider, taller and deeper than it should be (EggModel.bounce), from its foot
	sized: Vector3?, -- scale * squash the parts were last sized for
	splitAt: number?,
	splashed: boolean?,
	streak: BasePart?,
	connection: RBXScriptConnection?,
}

local dressed: { [BasePart]: Dressed } = setmetatable({}, { __mode = "k" }) :: any

local function scaled(v: Vector3, by: Vector3): Vector3
	return Vector3.new(v.X * by.X, v.Y * by.Y, v.Z * by.Z)
end

-- Puts one half's parts round its pivot, stretched by `by` (every egg part is lined up with its pivot, so stretching
-- them along its axes squashes the egg without skewing it).
local function placeHalf(pieces: { Piece }, pivot: CFrame, by: Vector3, resize: boolean)
	for _, piece in pieces do
		piece.part.CFrame = pivot * CFrame.new(scaled(piece.offset.Position, by)) * piece.offset.Rotation
		if resize then
			piece.part.Size = scaled(piece.size, by)
		end
	end
end

local function lerp(range: { number }): number
	return range[1] + (range[2] - range[1]) * math.random()
end

local function bare(part: BasePart)
	part.Anchored = true
	part.CanCollide = false
	part.CanQuery = false
	part.CanTouch = false
	part.CastShadow = false
end

-- Egg white and yolk splash out of the cut and land flat round the egg; bits of shell fly off and lie where they
-- fall (Config/Throw landing.splash). They fade a while later, and go with the egg if it goes first.
local function splash(state: Dressed, foot: CFrame, scale: number)
	local cfg = Throw.landing.splash
	local folder = Instance.new("Folder")
	folder.Name = "Splash"
	folder.Parent = state.holder
	local groundY = foot.Position.Y
	local cutY = settings.cut * settings.height * scale
	local bits = {}
	local function add(kind: string, color: Color3, size: Vector3)
		local part = Instance.new("Part")
		bare(part)
		part.Name = kind
		part.Shape = if kind == "Chip" then Enum.PartType.Block else Enum.PartType.Ball
		part.Material = Enum.Material.SmoothPlastic
		part.Color = color
		part.Size = size * scale
		local angle = math.random() * 2 * math.pi
		local out = Vector3.new(math.cos(angle), 0, math.sin(angle))
		local position = foot.Position + out * settings.radius * 0.7 * scale + Vector3.new(0, cutY, 0)
		part.CFrame = CFrame.new(position)
		part.Parent = folder
		table.insert(bits, {
			part = part,
			kind = kind,
			position = position,
			velocity = out * lerp(cfg.speed) * scale + Vector3.new(0, lerp(cfg.rise) * scale, 0),
			turn = CFrame.Angles(math.random() * 6, math.random() * 6, math.random() * 6),
			spin = Vector3.new(math.random() - 0.5, math.random() - 0.5, math.random() - 0.5) * 30,
			landed = false,
		})
	end
	for _ = 1, cfg.whites do
		local d = 0.22 + math.random() * 0.2
		add("White", state.colors.white, Vector3.one * d)
	end
	for _ = 1, cfg.yolks do
		local d = 0.24 + math.random() * 0.12
		add("Yolk", state.colors.yolk, Vector3.one * d)
	end
	for _ = 1, cfg.chips do
		add("Chip", state.colors.shell, Vector3.new(0.25 + math.random() * 0.2, 0.07, 0.2 + math.random() * 0.15))
	end

	local startedAt = os.clock()
	local connection
	connection = RunService.RenderStepped:Connect(function(dt)
		if not folder.Parent then
			connection:Disconnect()
			return
		end
		local age = os.clock() - startedAt
		if age > cfg.fadeAfter then
			local fade = math.min((age - cfg.fadeAfter) / 0.6, 1)
			for _, bit in bits do
				bit.part.Transparency = fade
			end
			if fade >= 1 then
				connection:Disconnect()
				folder:Destroy()
			end
			return
		end
		for _, bit in bits do
			if not bit.landed then
				bit.velocity -= Vector3.new(0, cfg.gravity * scale * dt, 0)
				bit.position += bit.velocity * dt
				local part = bit.part
				if bit.kind == "Chip" then
					bit.turn *= CFrame.Angles(bit.spin.X * dt, bit.spin.Y * dt, bit.spin.Z * dt)
					local rest = groundY + part.Size.Y / 2
					if bit.position.Y <= rest and bit.velocity.Y < 0 then
						bit.landed = true
						local _, yaw = bit.turn:ToEulerAnglesYXZ()
						part.CFrame = CFrame.new(bit.position.X, rest, bit.position.Z) * CFrame.Angles(0, yaw, 0)
					else
						part.CFrame = CFrame.new(bit.position) * bit.turn
					end
				else
					-- A drop stretches along the way it flies, and lands as a flat round splat.
					if bit.position.Y <= groundY + part.Size.X / 2 and bit.velocity.Y < 0 then
						bit.landed = true
						local width = part.Size.X * (2.4 + math.random() * 1)
						local lift = if bit.kind == "Yolk" then 0.04 else 0.025
						part.Shape = Enum.PartType.Cylinder
						part.Size = Vector3.new(0.04 * scale, width, width)
						part.CFrame = CFrame.new(bit.position.X, groundY + lift * scale, bit.position.Z) * CFrame.Angles(0, 0, math.pi / 2)
					else
						part.CFrame = CFrame.new(bit.position)
					end
				end
			end
		end
	end)
end

-- Puts the halves where they belong on the egg Part this frame.
local function place(egg: BasePart, state: Dressed)
	local scale = egg.Size.Y / settings.height
	state.scale = scale
	local by = state.squash * scale
	local resize = state.sized == nil or (state.sized :: Vector3 - by).Magnitude > 1e-4
	state.sized = by
	local foot = egg.CFrame * CFrame.new(0, -egg.Size.Y / 2, 0)
	placeHalf(state.bottom, foot, by, resize)
	local across, up, tip = 0, settings.cut * settings.height, 0
	if state.splitAt then
		local s = os.clock() - state.splitAt
		across, up, tip = EggModel.lidPose(s)
		local streak = state.streak
		if streak then
			local sweep, fade = EggModel.streak(s)
			if sweep and fade then
				local length = settings.radius * 1.4 * (1 - fade) * scale
				streak.Size = Vector3.new(math.max(length, 0.05), STREAK_THICK * scale, STREAK_THICK * scale)
				streak.CFrame = foot * CFrame.new(sweep * settings.radius * 1.6 * scale, settings.cut * settings.height * scale, 0)
				streak.Transparency = 0
			else
				streak.Transparency = 1
			end
		end
		if not state.splashed and s >= settings.delay + settings.slice then
			state.splashed = true
			splash(state, foot, scale)
		end
	end
	placeHalf(state.lid, foot * CFrame.new(across * scale, up * by.Y, 0) * CFrame.Angles(0, 0, -tip), by, resize)
end

-- Dresses the egg Part in its egg's Blender model: the Part goes see-through and the model follows it everywhere,
-- growing and shrinking with it. Dressing it again in another egg swaps the model. Returns false, leaving the Part
-- as it is, for an egg with no model yet. Client only (it follows the Part every frame).
function EggModel.dress(egg: BasePart, eggId: string): boolean
	local existing = dressed[egg]
	if existing then
		if existing.eggId == eggId then
			return true
		end
		if existing.connection then
			existing.connection:Disconnect()
		end
		existing.holder:Destroy()
		dressed[egg] = nil
		egg.Transparency = 0
	end
	local model = EggModel.clone(eggId)
	if not model then
		return false
	end
	local foot = model:GetPivot()
	local lidPivot = foot * CFrame.new(0, settings.cut * settings.height, 0)
	local holder = Instance.new("Model")
	holder.Name = "EggLook"
	local bottom: { Piece }, lid: { Piece } = {}, {}
	local colors = { white = Color3.new(1, 1, 1), yolk = Color3.fromRGB(255, 190, 30), shell = egg.Color }
	for _, part in model:GetDescendants() do
		if part:IsA("BasePart") then
			local isLid = string.sub(part.Name, -#LID) == LID
			local pivot = if isLid then lidPivot else foot
			table.insert(if isLid then lid else bottom, { part = part, offset = pivot:ToObjectSpace(part.CFrame), size = part.Size })
			if part.Name == "White" or part.Name == "Yolk" or part.Name == "Shell" then
				colors[string.lower(part.Name)] = part.Color
			end
			part.Parent = holder
		end
	end
	model:Destroy()
	holder.Parent = egg
	egg.Transparency = 1

	local state: Dressed = {
		eggId = eggId,
		holder = holder,
		bottom = bottom,
		lid = lid,
		colors = colors,
		scale = 1,
		squash = Vector3.one,
	}
	dressed[egg] = state
	place(egg, state)
	state.connection = RunService.RenderStepped:Connect(function()
		if egg.Parent then
			place(egg, state)
		end
	end)
	egg.Destroying:Connect(function()
		if state.connection then
			state.connection:Disconnect()
		end
	end)
	return true
end

-- How squashed the egg is t seconds after it touched down: above 0 flatter, below 0 stretched taller. It squashes
-- hard on each touch-down and springs back, overshooting a little.
local function squashAt(t: number): number
	local bounce = Throw.landing.bounce
	local hop1, hop2 = bounce.hops[1], bounce.hops[2]
	local contacts = { 0, hop1.time, hop1.time + hop2.time }
	local amounts = { 1, 0.5, 0.3 }
	local total = 0
	for i, at in contacts do
		local u = (t - at) / bounce.contact
		if u >= 0 and u < 1 then -- squashed flat on the ground
			total += bounce.squash * amounts[i] * math.sin(math.pi * u)
		elseif u >= 1 and i < 3 then -- stretched as it springs off
			local v = (t - at - bounce.contact) / bounce.squashTime
			if v < 1 then
				total -= bounce.squash * amounts[i] * 0.4 * math.sin(math.pi * v)
			end
		end
	end
	return total
end

-- The egg's touch-down (Config/Throw landing.bounce). Call it the moment the egg Part reaches the ground, short of
-- `rest` (where its middle ends, on the ground); it hops on to there, squashing on each touch-down, comes upright,
-- rocks on its foot and trembles, and returns when it stands still at `rest`, upright. Yields. `onFrame` is told the
-- time, where the egg is along its way (without the hops and shakes, for a camera to follow) and how hard it just hit
-- (0 to 1). Works on an egg with no Blender model too, without the squash.
function EggModel.bounce(egg: BasePart, rest: Vector3, onFrame: ((number, Vector3, number) -> ())?)
	local bounce = Throw.landing.bounce
	local state = dressed[egg]
	local start = Vector3.new(egg.Position.X, rest.Y, egg.Position.Z)
	local startTurn = egg.CFrame.Rotation
	local run = rest - start
	local axis = if run.Magnitude > 1e-3 then run.Unit:Cross(Vector3.yAxis) else Vector3.xAxis
	local scale = egg.Size.Y / settings.height
	local half = egg.Size.Y / 2
	local hop1, hop2 = bounce.hops[1], bounce.hops[2]
	local hopsTime = hop1.time + hop2.time
	local total = hopsTime + bounce.wobbleTime + bounce.trembleTime
	local startedAt = os.clock()
	while true do
		local t = math.min(os.clock() - startedAt, total)
		local along, lift = 1, 0
		-- Each hop starts squashed on the ground for `contact`, then flies.
		local function hop(h, from: number, at: number)
			local u = at / h.time
			local air = math.max(0, (at - bounce.contact) / (h.time - bounce.contact))
			return from + h.share * u, h.height * 4 * air * (1 - air)
		end
		if t < hop1.time then
			along, lift = hop(hop1, 0, t)
		elseif t < hopsTime then
			along, lift = hop(hop2, hop1.share, t - hop1.time)
		end
		along = 1 - (1 - along) ^ 1.4 -- skids fast, then slows
		local track = start + run * along
		local turn = startTurn:Lerp(CFrame.identity, smooth(math.min(t / hopsTime, 1)))
		local cframe = CFrame.new(track + Vector3.new(0, lift * scale, 0)) * turn
		local swell = 0
		if t >= hopsTime then
			local w = t - hopsTime
			local rock = 0
			if w < bounce.wobbleTime then
				local u = w / bounce.wobbleTime
				rock = bounce.wobble * math.sin(u * 3 * math.pi) * (1 - u) ^ 2
			end
			local shake = Vector3.zero
			local r = w - bounce.wobbleTime
			if r > 0 and t < total then
				local u = r / bounce.trembleTime
				local amp = bounce.tremble * scale * u
				shake = Vector3.new((math.random() * 2 - 1) * amp, 0, (math.random() * 2 - 1) * amp)
				swell = -0.06 * u -- swells a little, about to burst
			end
			-- Rocks on its foot, not round its middle.
			cframe = CFrame.new(rest - Vector3.new(0, half, 0) + shake) * CFrame.fromAxisAngle(axis, rock) * CFrame.new(0, half, 0)
		end
		egg.CFrame = cframe
		local squash = squashAt(t) + swell
		if state then
			local tall = 1 - squash
			local wide = 1 / math.sqrt(tall)
			state.squash = Vector3.new(wide, tall, wide)
		end
		if onFrame then
			onFrame(t, track, math.clamp(squash / bounce.squash, 0, 1))
		end
		if t >= total then
			break
		end
		RunService.RenderStepped:Wait()
	end
	if state then
		state.squash = Vector3.one
	end
	egg.CFrame = CFrame.new(rest)
end

-- Cuts a dressed egg in half where it lies: stands it upright, then plays the slice. Does nothing to an egg that isn't
-- dressed (no Blender model yet) or is already cut.
function EggModel.split(egg: BasePart)
	local state = dressed[egg]
	if not state or state.splitAt then
		return
	end
	egg.CFrame = CFrame.new(egg.Position) -- upright, whatever way it tumbled in flight
	local streak = Instance.new("Part")
	streak.Name = "SliceStreak"
	streak.Anchored = true
	streak.CanCollide = false
	streak.CanQuery = false
	streak.CanTouch = false
	streak.CastShadow = false
	streak.Material = Enum.Material.Neon
	streak.Color = Color3.new(1, 1, 1)
	streak.Transparency = 1
	streak.Size = Vector3.new(0.05, STREAK_THICK, STREAK_THICK)
	streak.Parent = state.holder
	state.streak = streak
	state.splitAt = os.clock()
end

return EggModel
