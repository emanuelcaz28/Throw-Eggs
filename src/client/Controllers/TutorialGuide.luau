-- The tutorial's guides in the world: a flat Beam of scrolling arrows on the ground from the player to where the step
-- happens (owner's texture), and a yolk-yellow chevron bobbing over the spot (TutorialController puts any word over it).
-- Only on this player's screen; numbers in Config/Tutorial guide.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local Plot = require(ReplicatedStorage.Shared.Config.Plot)
local Tutorial = require(ReplicatedStorage.Shared.Config.Tutorial)
local UiKit = require(ReplicatedStorage.Shared.UiKit)

local player = Players.LocalPlayer
local guide = Tutorial.guide

local TutorialGuide = {}

local MAX_LEGS = 3 -- straight beams in the path: player to gate, through the gate, gate to target
local GATE_STEP = 4 -- studs inside and outside the gate the path passes through
local LIFT = 0.15 -- studs over the ground the beam lies, so it never flickers into it

local folder: Folder? = nil
local anchor: BasePart? = nil -- holds the beam's attachments, at the world origin so their Position is world space
local points: { Attachment } = {}
local legs: { Beam } = {}
local corners: { Vector3 } = {} -- the path's corners on the ground after the player, ending at the target
local arrow: Model? = nil
local target: Vector3? = nil
local withTrail = false
local builtFrom: Vector3? = nil
local builtTo: Vector3? = nil
local hidden = true
local outlined: Model? = nil
local outline: Highlight? = nil

local function newPart(parent: Instance, size: Vector3, color: Color3): Part
	local part = Instance.new("Part")
	part.Anchored = true
	part.CanCollide = false
	part.CanQuery = false
	part.CanTouch = false
	part.CastShadow = false
	part.Material = Enum.Material.SmoothPlastic -- Neon glows these yellows to white
	part.Color = color
	part.Size = size
	part.Parent = parent
	return part
end

-- The guide on the ground: flat Beams with the owner's arrow texture (Config/Tutorial guide.beam) scrolling toward
-- the target, from an attachment at the player's feet through the path's corners to one at the target.
local function makeBeams(parent: Instance)
	local config = guide.beam
	local holder = newPart(parent, Vector3.new(0.1, 0.1, 0.1), guide.colours.yolk)
	holder.Name = "BeamAnchor"
	holder.Transparency = 1
	holder.CFrame = CFrame.new()
	anchor = holder
	for index = 1, MAX_LEGS + 1 do
		local point = Instance.new("Attachment")
		point.Name = `Point{index}`
		point.Parent = holder
		points[index] = point
	end
	for index = 1, MAX_LEGS do
		local beam = Instance.new("Beam")
		beam.Name = `Leg{index}`
		beam.Attachment0 = points[index]
		beam.Attachment1 = points[index + 1]
		beam.Texture = config.texture
		beam.TextureMode = Enum.TextureMode.Static
		beam.TextureLength = config.textureLength
		beam.TextureSpeed = config.speed
		beam.Width0 = config.width
		beam.Width1 = config.width
		beam.Color = ColorSequence.new(config.colour)
		beam.LightEmission = config.glow
		beam.LightInfluence = 0
		beam.Transparency = NumberSequence.new(0)
		beam.FaceCamera = false
		beam.Segments = 1
		beam.Enabled = false
		beam.Parent = holder
		legs[index] = beam
	end
end

-- The floating chevron: two bars in a V, outlined in ink so it reads against bright ground and sky.
local function makeArrow(parent: Instance): Model
	local model = Instance.new("Model")
	model.Name = "TutorialArrow"
	local width = guide.arrowWidth
	local bar = Vector3.new(width * 0.24, width * 0.78, width * 0.24)
	for side = -1, 1, 2 do
		local part = newPart(model, bar, guide.colours.yolk)
		part.Name = if side < 0 then "Left" else "Right"
		part:SetAttribute("Offset", CFrame.new(side * width * 0.24, width * 0.3, 0) * CFrame.Angles(0, 0, -side * math.rad(42)))
	end
	local outline = Instance.new("Highlight")
	outline.FillTransparency = 1
	outline.OutlineColor = UiKit.INK
	outline.DepthMode = Enum.HighlightDepthMode.AlwaysOnTop -- seen from across the arena, through walls
	outline.Parent = model

	model.Parent = parent
	return model
end

local function ensureFolder(): Folder
	if folder and folder.Parent then
		return folder
	end
	local made = Instance.new("Folder")
	made.Name = "TutorialGuide"
	makeBeams(made)
	arrow = makeArrow(made)
	folder = made
	return made
end

local function rootPosition(): Vector3?
	local character = player.Character
	local root = character and character:FindFirstChild("HumanoidRootPart") :: BasePart?
	return root and root.Position
end

-- The ground under a point: the first thing a ray down hits that isn't a character or the guide itself.
local rayParams = RaycastParams.new()
rayParams.FilterType = Enum.RaycastFilterType.Exclude
local function groundAt(point: Vector3): Vector3?
	local exclude = { folder :: Instance }
	for _, other in Players:GetPlayers() do
		if other.Character then
			table.insert(exclude, other.Character)
		end
	end
	rayParams.FilterDescendantsInstances = exclude
	local hit = workspace:Raycast(point + Vector3.new(0, 30, 0), Vector3.new(0, -80, 0), rayParams)
	return hit and hit.Position
end

-- Corners of the walk from the player to the target: through the gate when only one of the two is inside the base.
local function waypoints(from: Vector3, to: Vector3): { Vector3 }
	local points = { from }
	local plotIndex = player:GetAttribute("PlotIndex")
	if plotIndex and Plot.positions[plotIndex] then
		local centre = Plot.positions[plotIndex]
		local function inside(point: Vector3): boolean
			return math.abs(point.X - centre.X) < Plot.size.X / 2 and math.abs(point.Z - centre.Z) < Plot.size.Z / 2
		end
		if inside(from) ~= inside(to) then
			local gate = Plot.gatePosition(plotIndex)
			local inner, outer = gate + Vector3.new(0, 0, GATE_STEP), gate - Vector3.new(0, 0, GATE_STEP)
			if inside(from) then
				table.insert(points, inner)
				table.insert(points, outer)
			else
				table.insert(points, outer)
				table.insert(points, inner)
			end
		end
	end
	table.insert(points, to)
	return points
end

-- Works out the path's corners on the ground from the player to the target (through the gate when needed).
local function buildTrail(from: Vector3, to: Vector3)
	local walk = waypoints(Vector3.new(from.X, 0, from.Z), Vector3.new(to.X, 0, to.Z))
	local high = math.max(from.Y, to.Y)
	corners = {}
	for index = 2, #walk do
		local corner = walk[index]
		local ground = groundAt(Vector3.new(corner.X, high, corner.Z))
		table.insert(corners, Vector3.new(corner.X, (if ground then ground.Y else to.Y - 0.5) + LIFT, corner.Z))
	end
end

-- Lays the beams: the first point follows the player's feet every frame, the rest are the path's corners. Flat on the
-- ground (each attachment's width axis sideways), and turned along its leg so the arrows point the way to go.
local function layBeams(feet: Vector3?)
	local path = { feet }
	for _, corner in corners do
		table.insert(path, corner)
	end
	for index, point in points do
		local here = path[index]
		if here then
			local nextPoint = path[index + 1] or path[index - 1]
			local along = if nextPoint then Vector3.new(nextPoint.X - here.X, 0, nextPoint.Z - here.Z) else Vector3.zero
			if index > 1 and not path[index + 1] and path[index - 1] then
				along = Vector3.new(here.X - path[index - 1].X, 0, here.Z - path[index - 1].Z)
			end
			-- An attachment's X axis runs along the beam and its Y axis is the beam's width: sideways, so it lies flat.
			local flat = along.Magnitude > 0.01
			point.CFrame = if flat
				then CFrame.fromMatrix(here, along.Unit, along.Unit:Cross(Vector3.yAxis))
				else CFrame.new(here)
		end
	end
	for index, beam in legs do
		beam.Enabled = feet ~= nil and path[index + 1] ~= nil
	end
end

-- Shows the guides for a step: the arrow over `point` and, with trail, sparks running there from the player. nil
-- point hides them.
function TutorialGuide.set(point: Vector3?, trail: boolean?)
	if point ~= target or (trail == true) ~= withTrail then
		builtFrom, builtTo = nil, nil
	end
	target = point
	withTrail = trail == true
end

-- A pulsing yolk outline around one model (the monster to pick up), or nil for none. The Highlight is only moved
-- when the model changes (moving one is slow, memory highlight-adornee-pitfall).
function TutorialGuide.setOutline(model: Model?)
	if model == outlined then
		return
	end
	outlined = model
	if not outline then
		local made = Instance.new("Highlight")
		made.Name = "TutorialOutline"
		made.FillColor = guide.colours.yolk
		made.OutlineColor = guide.colours.yolk
		made.DepthMode = Enum.HighlightDepthMode.Occluded
		made.Parent = workspace -- not inside the statue: statues are rebuilt (destroyed) on every change to the base
		outline = made
	end
	local highlight = outline :: Highlight
	highlight.Adornee = model
	highlight.Enabled = model ~= nil
end

-- Hides everything for now (throwing, training, a panel) without forgetting the target.
function TutorialGuide.setHidden(value: boolean)
	hidden = value
end

local function update()
	if outline and outlined then
		local pulse = (math.sin(os.clock() * 5) + 1) / 2
		outline.FillTransparency = 0.55 + 0.35 * pulse
		outline.Enabled = not hidden and outlined.Parent ~= nil
	end
	local root = rootPosition()
	if hidden or not target or not root then
		if folder then
			folder.Parent = nil
		end
		return
	end
	local parent = ensureFolder()
	parent.Parent = workspace
	local clock = os.clock()

	-- The arrow over the target, facing the camera.
	local camera = workspace.CurrentCamera
	local height = guide.arrowHeight + math.sin(clock * 3) * guide.arrowBob
	local at = target + Vector3.new(0, height, 0)
	local look = camera and Vector3.new(camera.CFrame.Position.X, at.Y, camera.CFrame.Position.Z) or at + Vector3.zAxis
	local frame = if (look - at).Magnitude > 0.01 then CFrame.lookAt(at, look) else CFrame.new(at)
	for _, part in (arrow :: Model):GetChildren() do
		if part:IsA("BasePart") then
			part.CFrame = frame * (part:GetAttribute("Offset") :: CFrame)
		end
	end

	-- The beam, its corners worked out again when the player has walked a few studs.
	if withTrail then
		if not builtFrom or (root - builtFrom).Magnitude > guide.rebuildDistance or builtTo ~= target then
			buildTrail(root, target)
			builtFrom, builtTo = root, target
		end
		local character = player.Character
		local humanoid = character and character:FindFirstChildOfClass("Humanoid")
		local rootPart = character and character:FindFirstChild("HumanoidRootPart") :: BasePart?
		local feet = if humanoid and rootPart
			then root - Vector3.new(0, humanoid.HipHeight + rootPart.Size.Y / 2 - LIFT, 0)
			else nil
		layBeams(feet)
	else
		layBeams(nil)
	end
end

function TutorialGuide.start()
	RunService.RenderStepped:Connect(update)
end


-- Where the arrow's top is right now, for a word over it on screen; nil while hidden.
function TutorialGuide.arrowTop(): Vector3?
	if hidden or not target or not folder or not folder.Parent then
		return nil
	end
	return target + Vector3.new(0, guide.arrowHeight + guide.arrowWidth * 1.4 + guide.arrowBob, 0)
end

return TutorialGuide
