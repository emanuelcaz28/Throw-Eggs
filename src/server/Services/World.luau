-- Small helpers shared by the services that build things in the world.
local World = {}

function World.makePart(parent: Instance, name: string, size: Vector3, cframe: CFrame, color: Color3): Part
	local part = Instance.new("Part")
	part.Name = name
	part.Anchored = true
	part.Size = size
	part.CFrame = cframe
	part.Color = color
	part.TopSurface = Enum.SurfaceType.Smooth
	part.BottomSurface = Enum.SurfaceType.Smooth
	part.Parent = parent
	return part
end

-- A flat round pad whose bottom sits at position.
function World.makePad(parent: Instance, position: Vector3, radius: number, color: Color3): Part
	local thickness = 0.5
	local diameter = radius * 2
	local pad = World.makePart(
		parent,
		"Pad",
		Vector3.new(thickness, diameter, diameter),
		CFrame.new(position + Vector3.new(0, thickness / 2, 0)) * CFrame.Angles(0, 0, math.rad(90)),
		color
	)
	pad.Shape = Enum.PartType.Cylinder
	pad.Material = Enum.Material.SmoothPlastic
	return pad
end

-- Floating text above a part.
function World.makeSign(part: BasePart, text: string, heightOffset: number, maxDistance: number, width: number)
	local sign = Instance.new("BillboardGui")
	sign.Name = "Sign"
	sign.Size = UDim2.fromOffset(width, 50)
	sign.StudsOffsetWorldSpace = Vector3.new(0, heightOffset, 0)
	sign.MaxDistance = maxDistance
	sign.Adornee = part
	sign.Parent = part

	local label = Instance.new("TextLabel")
	label.Size = UDim2.fromScale(1, 1)
	label.BackgroundTransparency = 1
	label.Font = Enum.Font.GothamBlack
	label.Text = text
	label.TextColor3 = Color3.new(1, 1, 1)
	label.TextStrokeTransparency = 0.3
	label.TextScaled = true
	label.Parent = sign
end

-- True if the player's living character is within a pad's zone.
function World.isOnPad(player: Player, position: Vector3, radius: number, height: number): boolean
	local character = player.Character
	local root = character and character:FindFirstChild("HumanoidRootPart")
	local humanoid = character and character:FindFirstChildOfClass("Humanoid")
	if not root or not humanoid or humanoid.Health <= 0 then
		return false
	end
	local offset = root.Position - position
	return Vector2.new(offset.X, offset.Z).Magnitude <= radius and offset.Y >= 0 and offset.Y <= height
end

return World
