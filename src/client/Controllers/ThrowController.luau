-- The timing meter, the egg's flight and the landing result. Display and input only:
-- the server decides when the meter runs and how far every egg goes.
local ContextActionService = game:GetService("ContextActionService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")

local Biomes = require(ReplicatedStorage.Shared.Config.Biomes)
local Throw = require(ReplicatedStorage.Shared.Config.Throw)

local player = Players.LocalPlayer

local ThrowController = {}

local TAP_ACTION = "ThrowEggTap"
local CAMERA_OFFSET = Vector3.new(14, 10, 24)
local EGG_SIZE = Vector3.new(2.4, 3, 2.4)
local EGG_COLOR = Color3.fromRGB(240, 226, 196)

local PANEL = Color3.fromRGB(28, 30, 36)
local TRACK = Color3.fromRGB(190, 70, 60)
local GOOD = Color3.fromRGB(226, 142, 58)
local PERFECT = Color3.fromRGB(110, 220, 110)
local TEXT = Color3.new(1, 1, 1)

local function corner(parent: Instance, radius: number)
	local uiCorner = Instance.new("UICorner")
	uiCorner.CornerRadius = UDim.new(0, radius)
	uiCorner.Parent = parent
end

local function makeLabel(parent: Instance): TextLabel
	local label = Instance.new("TextLabel")
	label.BackgroundTransparency = 1
	label.Font = Enum.Font.GothamBlack
	label.TextColor3 = TEXT
	label.TextStrokeTransparency = 0.5
	label.TextScaled = true
	label.Text = ""
	label.Parent = parent
	return label
end

local function buildGui()
	local gui = Instance.new("ScreenGui")
	gui.Name = "ThrowHud"
	gui.ResetOnSpawn = false
	gui.Parent = player:WaitForChild("PlayerGui")

	-- The whole panel is a button so it makes a big target on phones.
	local meter = Instance.new("TextButton")
	meter.AnchorPoint = Vector2.new(0.5, 1)
	meter.Position = UDim2.new(0.5, 0, 1, -112)
	meter.Size = UDim2.new(0.6, 0, 0, 84)
	meter.BackgroundColor3 = PANEL
	meter.BackgroundTransparency = 0.15
	meter.AutoButtonColor = false
	meter.Text = ""
	meter.Visible = false
	meter.Parent = gui
	corner(meter, 12)

	local sizeLimit = Instance.new("UISizeConstraint")
	sizeLimit.MaxSize = Vector2.new(380, 84)
	sizeLimit.Parent = meter

	local prompt = makeLabel(meter)
	prompt.Position = UDim2.fromOffset(14, 8)
	prompt.Size = UDim2.new(1, -28, 0, 28)
	prompt.Text = "TAP TO THROW!"

	local track = Instance.new("Frame")
	track.Position = UDim2.fromOffset(14, 44)
	track.Size = UDim2.new(1, -28, 0, 26)
	track.BackgroundColor3 = TRACK
	track.BorderSizePixel = 0
	track.ClipsDescendants = true
	track.Parent = meter

	-- The closer to the centre the better; green is the perfect zone.
	local good = Instance.new("Frame")
	good.AnchorPoint = Vector2.new(0.5, 0)
	good.Position = UDim2.fromScale(0.5, 0)
	good.Size = UDim2.fromScale(0.5, 1)
	good.BackgroundColor3 = GOOD
	good.BorderSizePixel = 0
	good.Parent = track

	local perfect = Instance.new("Frame")
	perfect.AnchorPoint = Vector2.new(0.5, 0)
	perfect.Position = UDim2.fromScale(0.5, 0)
	perfect.Size = UDim2.fromScale(1 - Throw.meter.perfectAccuracy, 1)
	perfect.BackgroundColor3 = PERFECT
	perfect.BorderSizePixel = 0
	perfect.Parent = track

	local cursor = Instance.new("Frame")
	cursor.AnchorPoint = Vector2.new(0.5, 0)
	cursor.Size = UDim2.new(0, 5, 1, 0)
	cursor.BackgroundColor3 = TEXT
	cursor.BorderSizePixel = 0
	cursor.Parent = track

	local banner = makeLabel(gui)
	banner.AnchorPoint = Vector2.new(0.5, 0)
	banner.Position = UDim2.new(0.5, 0, 0, 90)
	banner.Size = UDim2.new(0.8, 0, 0, 44)
	banner.Visible = false

	return { meter = meter, cursor = cursor, banner = banner }
end

local function biomeNameAt(distance: number): string
	for _, biome in Biomes do
		if distance <= biome.endDist then
			return biome.name
		end
	end
	return Biomes[#Biomes].name
end

local function makeEgg(): Part
	local egg = Instance.new("Part")
	egg.Name = "ThrownEgg"
	egg.Anchored = true
	egg.CanCollide = false
	egg.CanQuery = false
	egg.CanTouch = false
	egg.Size = EGG_SIZE
	egg.Color = EGG_COLOR
	egg.CastShadow = true
	local mesh = Instance.new("SpecialMesh")
	mesh.MeshType = Enum.MeshType.Sphere
	mesh.Parent = egg
	egg.Parent = workspace
	return egg
end

function ThrowController.start()
	local remotes = ReplicatedStorage:WaitForChild("ThrowRemotes")
	local hud = buildGui()

	local aiming = false
	local aimStartedAt = 0
	local cursorPosition = 0.5

	local function stopAiming()
		aiming = false
		hud.meter.Visible = false
		ContextActionService:UnbindAction(TAP_ACTION)
	end

	local function tap()
		if aiming and os.clock() - aimStartedAt >= Throw.meter.minTime then
			stopAiming()
			remotes.Tap:FireServer(1 - math.abs(cursorPosition - 0.5) * 2)
		end
	end

	hud.meter.Activated:Connect(tap)
	UserInputService.InputBegan:Connect(function(input, gameProcessed)
		if not gameProcessed and input.UserInputType == Enum.UserInputType.MouseButton1 then
			tap()
		end
	end)

	RunService.RenderStepped:Connect(function()
		if aiming then
			-- Sweeps 0 -> 1 -> 0, starting at the edge.
			local cycle = ((os.clock() - aimStartedAt) * Throw.meter.cyclesPerSecond) % 1
			cursorPosition = 1 - math.abs(cycle * 2 - 1)
			hud.cursor.Position = UDim2.fromScale(cursorPosition, 0)
		end
	end)

	remotes.MeterStart.OnClientEvent:Connect(function()
		aiming = true
		aimStartedAt = os.clock()
		hud.meter.Visible = true
		-- Taken over while aiming so Space throws instead of jumping.
		ContextActionService:BindAction(TAP_ACTION, function(_, inputState)
			if inputState == Enum.UserInputState.Begin then
				tap()
			end
			return Enum.ContextActionResult.Sink
		end, false, Enum.KeyCode.Space, Enum.KeyCode.ButtonA)
	end)

	remotes.MeterCancel.OnClientEvent:Connect(stopAiming)

	remotes.Launched.OnClientEvent:Connect(function(thrower: Player, distance: number, perfect: boolean)
		local isMine = thrower == player
		local lane = Throw.lane
		local flight = Throw.flight
		local duration = Throw.flightTime(distance)
		local arc = math.min(distance * flight.arcPerStud, flight.maxArc)
		local egg = makeEgg()
		local camera = workspace.CurrentCamera

		if isMine then
			stopAiming()
			camera.CameraType = Enum.CameraType.Scriptable
			hud.banner.Text = if perfect then "PERFECT!" else ""
			hud.banner.Visible = true
		end

		local startedAt = os.clock()
		while true do
			local t = math.min((os.clock() - startedAt) / duration, 1)
			local travelled = distance * t
			-- Drops from launch height to the ground, plus a hill that peaks at arc halfway.
			local height = flight.launchHeight * (1 - t) + arc * 4 * t * (1 - t)
			local position = lane.origin + lane.direction * travelled + Vector3.new(0, height, 0)
			egg.CFrame = CFrame.new(position) * CFrame.Angles(t * 20, 0, 0)
			if isMine then
				camera.CFrame = CFrame.lookAt(position + CAMERA_OFFSET, position)
				hud.banner.Text = if perfect then `PERFECT! {math.floor(travelled)} studs` else `{math.floor(travelled)} studs`
			end
			if t >= 1 then
				break
			end
			RunService.RenderStepped:Wait()
		end

		if isMine then
			hud.banner.Text = `{math.floor(distance)} studs · {biomeNameAt(distance)}`
		end
		task.wait(flight.landingPause)
		egg:Destroy()
		if isMine then
			hud.banner.Visible = false
			camera.CameraType = Enum.CameraType.Custom
		end
	end)
end

return ThrowController
