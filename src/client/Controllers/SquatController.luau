-- Makes everyone who is training squat: a barbell on their shoulders and their joints bent in
-- time with the reps. Runs on every client for every training player, so all of it is local
-- and nothing needs replicating. Only R15 characters bend; R6 characters just hold the bar.
-- Also gives a player who tapped the x2 bubble a burst everyone can see: a flash of purple that fades, sparks and
-- a ring along the ground.
local Debris = game:GetService("Debris")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")

local Training = require(ReplicatedStorage.Shared.Config.Training)

local SquatController = {}

local SQUAT_ANGLE = math.rad(72) -- how far the thighs swing forward at the bottom
local LEAN = 0.35 -- share of SQUAT_ANGLE the torso tips forward
local ARM_OUT = math.rad(70) -- upper arms out to the sides, to reach the bar
local ARM_BACK = math.rad(25)
local ELBOW_BEND = math.rad(105)
local BAR_LENGTH = 12
local BAR_BACK = 0.45 -- studs behind the shoulders
local PLATE_OFFSETS = { 4.9, 5.4 }
local BAR_COLOR = Color3.fromRGB(200, 205, 212)
local PLATE_COLOR = Color3.fromRGB(40, 42, 48)
local GLOW = Color3.fromRGB(180, 100, 255)
local GLOW_TIME = 0.9
local SPARKS = 36
local SPARK_COLORS = ColorSequence.new(Color3.fromRGB(235, 205, 255), Color3.fromRGB(170, 80, 255))
local RING_START, RING_END, RING_TIME = 4, 26, 0.5 -- studs across, seconds

local function motor(character: Model, partName: string, motorName: string): Motor6D?
	local part = character:FindFirstChild(partName)
	return part and part:FindFirstChild(motorName) :: Motor6D?
end

local function makeBarPart(parent: Instance, size: Vector3, color: Color3): Part
	local part = Instance.new("Part")
	part.Shape = Enum.PartType.Cylinder -- along X
	part.Material = Enum.Material.Metal
	part.Size = size
	part.Color = color
	part.CanCollide = false
	part.CanQuery = false
	part.CanTouch = false
	part.Massless = true
	part.Parent = parent
	return part
end

-- A loaded barbell welded across the back of the shoulders.
local function addBar(character: Model)
	local torso = character:FindFirstChild("UpperTorso") or character:FindFirstChild("Torso")
	if not torso or character:FindFirstChild("SquatBar") then
		return
	end
	local model = Instance.new("Model")
	model.Name = "SquatBar"
	local onShoulders = CFrame.new(0, torso.Size.Y / 2 - 0.05, BAR_BACK)
	local pieces = { { makeBarPart(model, Vector3.new(BAR_LENGTH, 0.35, 0.35), BAR_COLOR), 0 } }
	for _, offset in PLATE_OFFSETS do
		for _, side in { -1, 1 } do
			table.insert(pieces, { makeBarPart(model, Vector3.new(0.4, 2.8, 2.8), PLATE_COLOR), side * offset })
		end
	end
	for _, piece in pieces do
		local weld = Instance.new("Weld")
		weld.Part0 = torso
		weld.Part1 = piece[1]
		weld.C0 = onShoulders * CFrame.new(piece[2], 0, 0)
		weld.Parent = piece[1]
	end
	model.Parent = character
end

-- Bends an R15 character to a squat depth from 0 (standing) to 1 (bottom).
local function pose(character: Model, depth: number)
	local root = motor(character, "LowerTorso", "Root")
	if not root then
		return
	end
	local angle = SQUAT_ANGLE * depth
	local lean = angle * LEAN
	local upperLeg = character:FindFirstChild("LeftUpperLeg") :: BasePart?
	local lowerLeg = character:FindFirstChild("LeftLowerLeg") :: BasePart?
	local legLength = (if upperLeg then upperLeg.Size.Y else 1.2) + (if lowerLeg then lowerLeg.Size.Y else 1.2)
	local drop = legLength * (1 - math.cos(angle))

	root.Transform = CFrame.new(0, -drop, 0) * CFrame.Angles(-lean, 0, 0)
	for _, side in { "Left", "Right" } do
		local hip = motor(character, `{side}UpperLeg`, `{side}Hip`)
		local knee = motor(character, `{side}LowerLeg`, `{side}Knee`)
		local ankle = motor(character, `{side}Foot`, `{side}Ankle`)
		-- Thighs forward, shins back by the same amount, feet flat on the floor.
		if hip then
			hip.Transform = CFrame.Angles(angle + lean, 0, 0)
		end
		if knee then
			knee.Transform = CFrame.Angles(-2 * angle, 0, 0)
		end
		if ankle then
			ankle.Transform = CFrame.Angles(angle, 0, 0)
		end

		-- Hands up on the bar behind the neck.
		local out = if side == "Right" then 1 else -1
		local shoulder = motor(character, `{side}UpperArm`, `{side}Shoulder`)
		local elbow = motor(character, `{side}LowerArm`, `{side}Elbow`)
		if shoulder then
			shoulder.Transform = CFrame.Angles(-ARM_BACK, 0, out * ARM_OUT)
		end
		if elbow then
			elbow.Transform = CFrame.Angles(0, 0, out * ELBOW_BEND)
		end
	end
end

local function onBoosted(booster: Player)
	local character = booster.Character
	local root = character and character:FindFirstChild("HumanoidRootPart") :: BasePart?
	local humanoid = character and character:FindFirstChildOfClass("Humanoid")
	if not root or not humanoid then
		return
	end
	local fade = TweenInfo.new(GLOW_TIME, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)
	local highlight = Instance.new("Highlight")
	highlight.FillColor = GLOW
	highlight.OutlineColor = Color3.new(1, 1, 1)
	highlight.FillTransparency = 0.1
	highlight.Parent = character
	TweenService:Create(highlight, fade, { FillTransparency = 1, OutlineTransparency = 1 }):Play()
	Debris:AddItem(highlight, GLOW_TIME)

	local spot = Instance.new("Attachment")
	spot.Parent = root
	local sparks = Instance.new("ParticleEmitter")
	sparks.Rate = 0
	sparks.Color = SPARK_COLORS
	sparks.LightEmission = 0.6
	sparks.Lifetime = NumberRange.new(0.4, 0.8)
	sparks.Speed = NumberRange.new(14, 30)
	sparks.SpreadAngle = Vector2.new(180, 180)
	sparks.Size = NumberSequence.new(1.1, 0)
	sparks.Parent = spot
	sparks:Emit(SPARKS)
	Debris:AddItem(spot, 1)

	-- Flat on the ground under the lifter. A cylinder's round faces look along X.
	local feet = root.Position - Vector3.new(0, humanoid.HipHeight + root.Size.Y / 2 - 0.15, 0)
	local ring = Instance.new("Part")
	ring.Name = "BoostRing"
	ring.Shape = Enum.PartType.Cylinder
	ring.Material = Enum.Material.Neon
	ring.Color = GLOW
	ring.Anchored = true
	ring.CanCollide = false
	ring.CanQuery = false
	ring.CanTouch = false
	ring.CastShadow = false
	ring.Transparency = 0.2
	ring.Size = Vector3.new(0.2, RING_START, RING_START)
	ring.CFrame = CFrame.new(feet) * CFrame.Angles(0, 0, math.rad(90))
	ring.Parent = workspace
	TweenService:Create(ring, TweenInfo.new(RING_TIME, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {
		Size = Vector3.new(0.2, RING_END, RING_END),
		Transparency = 1,
	}):Play()
	Debris:AddItem(ring, RING_TIME)
end

function SquatController.start()
	local remotes = ReplicatedStorage:WaitForChild("TrainingRemotes")
	remotes.Boosted.OnClientEvent:Connect(onBoosted)

	-- Stepped runs after the animations each frame, so these poses win over the idle animation.
	RunService.Stepped:Connect(function()
		-- One full squat per rep, starting from standing.
		local depth = (1 - math.cos(2 * math.pi * os.clock() / Training.repInterval)) / 2
		for _, other in Players:GetPlayers() do
			local character = other.Character
			if character then
				local bar = character:FindFirstChild("SquatBar")
				if other:GetAttribute("IsTraining") then
					addBar(character)
					pose(character, depth)
				elseif bar then
					bar:Destroy()
				end
			end
		end
	end)
end

return SquatController
