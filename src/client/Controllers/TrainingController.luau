-- Shows Throw Power and training progress. Display only: every value here is
-- read from attributes the server sets on the local player.
local Players = game:GetService("Players")
local TweenService = game:GetService("TweenService")

local player = Players.LocalPlayer

local TrainingController = {}

local ACCENT = Color3.fromRGB(226, 142, 58)
local PANEL = Color3.fromRGB(28, 30, 36)
local TRACK = Color3.fromRGB(58, 62, 72)
local TEXT = Color3.new(1, 1, 1)
local MUTED = Color3.fromRGB(190, 195, 205)

local function corner(parent: Instance, radius: number)
	local uiCorner = Instance.new("UICorner")
	uiCorner.CornerRadius = UDim.new(0, radius)
	uiCorner.Parent = parent
end

local function makeLabel(parent: Instance, font: Enum.Font, color: Color3, align: Enum.TextXAlignment): TextLabel
	local label = Instance.new("TextLabel")
	label.BackgroundTransparency = 1
	label.Font = font
	label.TextColor3 = color
	label.TextXAlignment = align
	label.TextScaled = true
	label.Text = ""
	label.Parent = parent
	return label
end

local function buildHud()
	local gui = Instance.new("ScreenGui")
	gui.Name = "TrainingHud"
	gui.ResetOnSpawn = false
	gui.Parent = player:WaitForChild("PlayerGui")

	local panel = Instance.new("Frame")
	panel.AnchorPoint = Vector2.new(0.5, 1)
	panel.Position = UDim2.new(0.5, 0, 1, -16)
	panel.Size = UDim2.new(0.6, 0, 0, 84)
	panel.BackgroundColor3 = PANEL
	panel.BackgroundTransparency = 0.15
	panel.Parent = gui
	corner(panel, 12)

	local sizeLimit = Instance.new("UISizeConstraint")
	sizeLimit.MaxSize = Vector2.new(380, 84)
	sizeLimit.Parent = panel

	local power = makeLabel(panel, Enum.Font.GothamBlack, TEXT, Enum.TextXAlignment.Left)
	power.Position = UDim2.fromOffset(14, 8)
	power.Size = UDim2.new(0.68, -14, 0, 26)

	local level = makeLabel(panel, Enum.Font.GothamBold, ACCENT, Enum.TextXAlignment.Right)
	level.AnchorPoint = Vector2.new(1, 0)
	level.Position = UDim2.new(1, -14, 0, 11)
	level.Size = UDim2.new(0.32, -14, 0, 20)

	local track = Instance.new("Frame")
	track.Position = UDim2.fromOffset(14, 40)
	track.Size = UDim2.new(1, -28, 0, 12)
	track.BackgroundColor3 = TRACK
	track.BorderSizePixel = 0
	track.Parent = panel
	corner(track, 6)

	local fill = Instance.new("Frame")
	fill.Size = UDim2.fromScale(0, 1)
	fill.BackgroundColor3 = ACCENT
	fill.BorderSizePixel = 0
	fill.Parent = track
	corner(fill, 6)

	local status = makeLabel(panel, Enum.Font.Gotham, MUTED, Enum.TextXAlignment.Left)
	status.Position = UDim2.fromOffset(14, 58)
	status.Size = UDim2.new(1, -28, 0, 16)
	status.Text = "Loading your save..."

	return { panel = panel, power = power, level = level, fill = fill, status = status }
end

local function popText(panel: Frame, text: string, color: Color3)
	local label = makeLabel(panel, Enum.Font.GothamBlack, color, Enum.TextXAlignment.Center)
	label.AnchorPoint = Vector2.new(0.5, 1)
	label.Position = UDim2.new(0.5, 0, 0, -4)
	label.Size = UDim2.new(1, 0, 0, 26)
	label.Text = text
	local tween = TweenService:Create(label, TweenInfo.new(0.9, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {
		Position = UDim2.new(0.5, 0, 0, -36),
		TextTransparency = 1,
	})
	tween.Completed:Once(function()
		label:Destroy()
	end)
	tween:Play()
end

function TrainingController.start()
	local hud = buildHud()
	local lastLevel: number? = nil
	local lastXp: number? = nil

	local function render()
		local power = player:GetAttribute("ThrowPower")
		local level = player:GetAttribute("TrainingLevel")
		local xp = player:GetAttribute("TrainingXp")
		local needed = player:GetAttribute("TrainingXpNeeded")
		if not (power and level and xp and needed) then
			return
		end

		hud.power.Text = `Throw Power {power}`
		hud.level.Text = `Level {level}`
		hud.status.Text = if player:GetAttribute("IsTraining")
			then `Training... {xp} / {needed} XP`
			else `Stand on the orange pad to train · {xp} / {needed} XP`
		hud.fill:TweenSize(UDim2.fromScale(math.clamp(xp / needed, 0, 1), 1), "Out", "Quad", 0.2, true)

		if lastLevel and level > lastLevel then
			popText(hud.panel, "LEVEL UP!", ACCENT)
		elseif lastXp and level == lastLevel and xp > lastXp then
			popText(hud.panel, `+{xp - lastXp} XP`, TEXT)
		end
		lastLevel, lastXp = level, xp
	end

	player.AttributeChanged:Connect(render)
	render()
end

return TrainingController
