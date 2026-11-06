-- The Egg Shop's eggs as made in Blender (assets/models/build_eggs.py), imported into ReplicatedStorage.Assets.Eggs
-- as egg_<id> (studio_tidy.py puts them there; each one's pivot is its foot, Y up). Every part of an egg's top half
-- has a name ending in "Lid"; the rest is its bottom half. Both halves are closed by a disc of white with a yolk.
--
-- The thrown egg stays the plain Part the throw and the reveal move about (ThrowController, RevealWalk,
-- RevealCloseUp): dress() hides it and puts the Blender egg on it, following it every frame and growing with it.
-- split() cuts it in half where it lands (Config/Throw landing.split, the same numbers as build_eggs.py's SPLIT, whose
-- egg_slice.mp4 shows it): a white streak sweeps across its middle, the top half slides off, tips over and lands upside
-- down beside the bottom half, its white and yolk facing up, and rocks to a stop. An egg with no model yet stays the
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

type Dressed = {
	eggId: string,
	holder: Model,
	bottom: Model,
	lid: Model,
	scale: number,
	splitAt: number?,
	streak: BasePart?,
	connection: RBXScriptConnection?,
}

local dressed: { [BasePart]: Dressed } = setmetatable({}, { __mode = "k" }) :: any

-- Puts the halves where they belong on the egg Part this frame.
local function place(egg: BasePart, state: Dressed)
	local scale = egg.Size.Y / settings.height
	if math.abs(scale - state.scale) > 1e-4 then
		state.bottom:ScaleTo(scale)
		state.lid:ScaleTo(scale)
		state.scale = scale
	end
	local foot = egg.CFrame * CFrame.new(0, -egg.Size.Y / 2, 0)
	state.bottom:PivotTo(foot)
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
	end
	state.lid:PivotTo(foot * CFrame.new(across * scale, up * scale, 0) * CFrame.Angles(0, 0, -tip))
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
	local holder = Instance.new("Model")
	holder.Name = "EggLook"
	local bottom = Instance.new("Model")
	bottom.Name = "Bottom"
	bottom.Parent = holder
	local lid = Instance.new("Model")
	lid.Name = "Lid"
	lid.Parent = holder
	for _, part in model:GetDescendants() do
		if part:IsA("BasePart") then
			part.Parent = if string.sub(part.Name, -#LID) == LID then lid else bottom
		end
	end
	model:Destroy()
	bottom.WorldPivot = foot
	lid.WorldPivot = foot * CFrame.new(0, settings.cut * settings.height, 0)
	holder.Parent = egg
	egg.Transparency = 1

	local state: Dressed = { eggId = eggId, holder = holder, bottom = bottom, lid = lid, scale = 1 }
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
