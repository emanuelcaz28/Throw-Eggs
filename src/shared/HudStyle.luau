-- The look shared by the always-on HUD: big square icon buttons with an outlined label, and
-- large outlined numbers with an icon (⚡ Throw Power, cash). Client only. Icons are emoji until
-- real icon images exist. Sizes shrink on short screens (phones) so everything still fits.
local GuiService = game:GetService("GuiService")

local HudStyle = {}

HudStyle.FONT = Enum.Font.FredokaOne
HudStyle.INK = Color3.fromRGB(20, 22, 28)
HudStyle.BUTTON_SIZE = 84
HudStyle.BUTTON_GAP = 20
HudStyle.COLUMN_CENTER = 0.45 -- height of the side button columns, as a share of the screen

local FRAME = Color3.fromRGB(42, 32, 69)
local FRAME_TOP = Color3.fromRGB(74, 58, 117)
local EDGE = Color3.fromRGB(91, 74, 140)
local TEXT = Color3.new(1, 1, 1)
local DESIGN_HEIGHT = 620 -- usable heights at least this tall get full size
local MIN_SCALE = 0.5

local cachedScale: number? = nil

-- 1 on normal screens, smaller on short ones. Worked out once, when the HUD is built, from
-- the height left under Roblox's top bar.
function HudStyle.scale(): number
	if cachedScale then
		return cachedScale
	end
	local camera = workspace.CurrentCamera
	while camera.ViewportSize.Y <= 1 do
		task.wait()
	end
	local usable = camera.ViewportSize.Y - GuiService:GetGuiInset().Y
	cachedScale = math.clamp(usable / DESIGN_HEIGHT, MIN_SCALE, 1)
	return cachedScale
end

-- Thick black outline around text, like a sticker.
function HudStyle.outline(label: TextLabel | TextButton, thickness: number)
	local stroke = Instance.new("UIStroke")
	stroke.ApplyStrokeMode = Enum.ApplyStrokeMode.Contextual
	stroke.Color = HudStyle.INK
	stroke.Thickness = thickness
	stroke.LineJoinMode = Enum.LineJoinMode.Round
	stroke.Parent = label
end

local function text(parent: Instance, value: string, color: Color3): TextLabel
	local label = Instance.new("TextLabel")
	label.BackgroundTransparency = 1
	label.Font = HudStyle.FONT
	label.Text = value
	label.TextColor3 = color
	label.TextScaled = true
	label.Parent = parent
	return label
end

-- A square button: dark rounded frame, big icon, label overlapping the bottom edge.
-- The caller sets Position and AnchorPoint; the size is already scaled.
function HudStyle.iconButton(parent: Instance, icon: string, label: string): TextButton
	local size = HudStyle.BUTTON_SIZE * HudStyle.scale()
	local button = Instance.new("TextButton")
	button.Size = UDim2.fromOffset(size, size)
	button.BackgroundColor3 = Color3.new(1, 1, 1)
	button.AutoButtonColor = false
	button.Text = ""
	button.Parent = parent
	local gradient = Instance.new("UIGradient")
	gradient.Color = ColorSequence.new(FRAME_TOP, FRAME)
	gradient.Rotation = 90
	gradient.Parent = button
	local corner = Instance.new("UICorner")
	corner.CornerRadius = UDim.new(0.26, 0)
	corner.Parent = button
	local stroke = Instance.new("UIStroke")
	stroke.ApplyStrokeMode = Enum.ApplyStrokeMode.Border
	stroke.Color = HudStyle.INK
	stroke.Thickness = 4
	stroke.Parent = button
	-- A lighter inner edge, like a bevel.
	local edge = Instance.new("Frame")
	edge.BackgroundTransparency = 1
	edge.Position = UDim2.fromOffset(4, 4)
	edge.Size = UDim2.new(1, -8, 1, -8)
	edge.Parent = button
	local edgeCorner = Instance.new("UICorner")
	edgeCorner.CornerRadius = UDim.new(0.24, 0)
	edgeCorner.Parent = edge
	local edgeStroke = Instance.new("UIStroke")
	edgeStroke.Color = EDGE
	edgeStroke.Thickness = 3
	edgeStroke.Parent = edge
	local press = Instance.new("UIScale")
	press.Parent = button
	button.MouseButton1Down:Connect(function()
		press.Scale = 0.92
	end)
	button.MouseButton1Up:Connect(function()
		press.Scale = 1
	end)
	button.MouseLeave:Connect(function()
		press.Scale = 1
	end)

	local iconLabel = text(button, icon, TEXT)
	iconLabel.Name = "Icon"
	iconLabel.AnchorPoint = Vector2.new(0.5, 0)
	iconLabel.Position = UDim2.fromScale(0.5, 0.08)
	iconLabel.Size = UDim2.fromScale(0.72, 0.66)

	local name = text(button, label, TEXT)
	name.Name = "Label"
	name.AnchorPoint = Vector2.new(0.5, 0.5)
	name.Position = UDim2.fromScale(0.5, 0.9)
	name.Size = UDim2.fromScale(1.25, 0.34)
	name.ZIndex = 2
	HudStyle.outline(name, 2.5 * HudStyle.scale())
	return button
end

-- A big outlined number with an icon to its left. Returns the frame and the number's label;
-- the caller sets the frame's Position and AnchorPoint.
function HudStyle.stat(parent: Instance, icon: string, color: Color3, height: number): (Frame, TextLabel)
	local scaled = height * HudStyle.scale()
	local frame = Instance.new("Frame")
	frame.BackgroundTransparency = 1
	frame.Size = UDim2.fromOffset(scaled * 5, scaled)
	frame.Parent = parent

	local iconLabel = text(frame, icon, TEXT)
	iconLabel.Name = "Icon"
	iconLabel.Size = UDim2.fromOffset(scaled, scaled)

	local number = text(frame, "", color)
	number.Name = "Value"
	number.Position = UDim2.fromOffset(scaled * 1.1, 0)
	number.Size = UDim2.new(1, -scaled * 1.1, 1, 0)
	number.TextXAlignment = Enum.TextXAlignment.Left
	HudStyle.outline(number, 3 * HudStyle.scale())
	return frame, number
end

return HudStyle
