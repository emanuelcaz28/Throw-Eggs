-- The timing meter, the egg's flight and the landing result. Display and input only:
-- the server decides when the meter runs and how far every egg goes.
local ContextActionService = game:GetService("ContextActionService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")

local Luck = require(ReplicatedStorage.Shared.Config.Luck)
local Throw = require(ReplicatedStorage.Shared.Config.Throw)

local player = Players.LocalPlayer

local ThrowController = {}

local TAP_ACTION = "ThrowEggTap"
local CAMERA_OFFSET = Vector3.new(14, 10, 24)
local EGG_SIZE = Vector3.new(2.4, 3, 2.4)
local EGG_COLOR = Color3.fromRGB(240, 226, 196)

local INK = Color3.fromRGB(20, 22, 28)
local TUBE_LOW = Color3.fromRGB(222, 62, 48)
local TUBE_MID = Color3.fromRGB(242, 150, 50)
local TUBE_HIGH = Color3.fromRGB(255, 214, 70)
local GOOD = Color3.fromRGB(226, 142, 58)
local PERFECT = Color3.fromRGB(110, 220, 110)
local GOLD = Color3.fromRGB(255, 226, 110)
local EGG = Color3.fromRGB(246, 239, 217)
local TEXT = Color3.new(1, 1, 1)

-- Meter layout, in pixels of the Figma design ("Throw Eggs - Timing Meter").
local METER_WIDTH, METER_HEIGHT = 220, 470
local TUBE_LEFT, TUBE_WIDTH = 78, 64
local TUBE_TOP, TUBE_HEIGHT = 70, 330
local ZONE_LEFT, ZONE_TOP, ZONE_WIDTH, ZONE_OVERHANG = 56, 48, 108, 22
local MARKER_LEFT, MARKER_WIDTH, MARKER_HEIGHT = 64, 92, 18
local LABEL_LEFT, LABEL_WIDTH, LABEL_HEIGHT = 166, 54, 34
local PROMPT_TOP, PROMPT_HEIGHT = 414, 42
local METER_SCREEN_SHARE = 0.62 -- share of the screen height the meter fills
local RESULT_HOLD = 0.7 -- seconds the meter stays up after a tap

local function meterBox(left: number, top: number, width: number, height: number)
	return UDim2.fromScale(left / METER_WIDTH, top / METER_HEIGHT), UDim2.fromScale(width / METER_WIDTH, height / METER_HEIGHT)
end

local function outline(parent: Instance, thickness: number)
	local stroke = Instance.new("UIStroke")
	stroke.Color = INK
	stroke.Thickness = thickness
	stroke.ApplyStrokeMode = Enum.ApplyStrokeMode.Border
	stroke.Parent = parent
end

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

	-- The whole meter is a button so it makes a big target on phones.
	local meter = Instance.new("TextButton")
	meter.AnchorPoint = Vector2.new(1, 0.5)
	meter.Position = UDim2.new(1, -24, 0.5, 0)
	meter.Size = UDim2.fromScale(1, METER_SCREEN_SHARE)
	meter.BackgroundTransparency = 1
	meter.AutoButtonColor = false
	meter.Text = ""
	meter.Visible = false
	meter.Parent = gui

	local aspect = Instance.new("UIAspectRatioConstraint")
	aspect.AspectRatio = METER_WIDTH / METER_HEIGHT
	aspect.AspectType = Enum.AspectType.ScaleWithParentSize
	aspect.DominantAxis = Enum.DominantAxis.Height
	aspect.Parent = meter

	local tube = Instance.new("Frame")
	tube.Name = "Tube"
	tube.Position, tube.Size = meterBox(TUBE_LEFT, TUBE_TOP, TUBE_WIDTH, TUBE_HEIGHT)
	tube.BackgroundColor3 = TEXT
	tube.Parent = meter
	corner(tube, 10)
	outline(tube, 3)

	local gradient = Instance.new("UIGradient")
	gradient.Rotation = 90 -- first colour at the top
	gradient.Color = ColorSequence.new({
		ColorSequenceKeypoint.new(0, TUBE_HIGH),
		ColorSequenceKeypoint.new(0.5, TUBE_MID),
		ColorSequenceKeypoint.new(1, TUBE_LOW),
	})
	gradient.Parent = tube

	-- The sweet zone flares wider than the tube so it reads as a big target.
	local levels = Throw.meter.levels
	for level = 1, levels - 2 do
		local tick = Instance.new("Frame")
		tick.Name = "LevelLine"
		tick.Position, tick.Size = meterBox(TUBE_LEFT + 6, TUBE_TOP + TUBE_HEIGHT * (1 - level / levels) - 1, TUBE_WIDTH - 12, 3)
		tick.BackgroundColor3 = INK
		tick.BackgroundTransparency = 0.65
		tick.BorderSizePixel = 0
		tick.Parent = meter
	end

	local zoneBottom = TUBE_TOP + TUBE_HEIGHT / levels
	local zone = Instance.new("Frame")
	zone.Name = "SweetZone"
	zone.Position, zone.Size = meterBox(ZONE_LEFT, ZONE_TOP, ZONE_WIDTH, zoneBottom - TUBE_TOP + ZONE_OVERHANG)
	zone.BackgroundColor3 = PERFECT
	zone.Parent = meter
	corner(zone, 14)
	outline(zone, 3)

	local egg = Instance.new("Frame")
	egg.Name = "Egg"
	egg.AnchorPoint = Vector2.new(0.5, 0.5)
	egg.Position = UDim2.fromScale(0.5, 0.5)
	egg.Size = UDim2.fromScale(0.28, 0.7)
	egg.BackgroundColor3 = EGG
	egg.Parent = zone
	local eggCorner = Instance.new("UICorner")
	eggCorner.CornerRadius = UDim.new(0.5, 0)
	eggCorner.Parent = egg
	outline(egg, 2)

	local marker = Instance.new("Frame")
	marker.Name = "Marker"
	marker.AnchorPoint = Vector2.new(0, 0.5)
	marker.BackgroundColor3 = TEXT
	marker.ZIndex = 2
	marker.Parent = meter
	corner(marker, 6)
	outline(marker, 3)
	local _, markerSize = meterBox(MARKER_LEFT, 0, MARKER_WIDTH, MARKER_HEIGHT)
	marker.Size = markerSize

	local value = makeLabel(meter)
	value.Name = "Level"
	value.AnchorPoint = Vector2.new(0, 0.5)
	value.TextXAlignment = Enum.TextXAlignment.Left
	local _, valueSize = meterBox(LABEL_LEFT, 0, LABEL_WIDTH, LABEL_HEIGHT)
	value.Size = valueSize

	local prompt = makeLabel(meter)
	prompt.Name = "Prompt"
	prompt.Position, prompt.Size = meterBox(0, PROMPT_TOP, METER_WIDTH, PROMPT_HEIGHT)

	local banner = makeLabel(gui)
	banner.AnchorPoint = Vector2.new(0.5, 0)
	banner.Position = UDim2.new(0.5, 0, 0, 90)
	banner.Size = UDim2.new(0.8, 0, 0, 44)
	banner.Visible = false

	local luck = makeLabel(gui)
	luck.AnchorPoint = Vector2.new(0.5, 0)
	luck.Position = UDim2.new(0.5, 0, 0, 16)
	luck.Size = UDim2.new(0.8, 0, 0, 64)
	luck.TextColor3 = PERFECT
	luck.Visible = false

	local catch = makeLabel(gui)
	catch.AnchorPoint = Vector2.new(0.5, 0)
	catch.Position = UDim2.new(0.5, 0, 0, 142)
	catch.Size = UDim2.new(0.8, 0, 0, 56)
	catch.TextColor3 = GOOD
	catch.Visible = false

	return {
		meter = meter,
		zone = zone,
		marker = marker,
		value = value,
		prompt = prompt,
		banner = banner,
		luck = luck,
		catch = catch,
	}
end

local function luckText(distance: number): string
	return string.format("Luck x%.1f", Luck.at(distance))
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
	local markerHeight = 0

	local function placeMarker(height: number)
		local center = (TUBE_TOP + TUBE_HEIGHT * (1 - height)) / METER_HEIGHT
		hud.marker.Position = UDim2.fromScale(MARKER_LEFT / METER_WIDTH, center)
		hud.value.Position = UDim2.fromScale(LABEL_LEFT / METER_WIDTH, center)
		hud.value.Text = `Lv {Throw.level(height)}`
		local inZone = Throw.isPerfect(height)
		hud.prompt.Text = if inZone then "TAP NOW!" else "TAP!"
		hud.prompt.TextColor3 = TEXT
		hud.zone.BackgroundColor3 = PERFECT
	end

	-- Stops taking taps. The meter stays on screen until hideMeter.
	local function stopAiming()
		aiming = false
		ContextActionService:UnbindAction(TAP_ACTION)
	end

	local function hideMeter()
		stopAiming()
		hud.meter.Visible = false
	end

	local function tap()
		if aiming and os.clock() - aimStartedAt >= Throw.meter.minTime then
			stopAiming()
			remotes.Tap:FireServer(markerHeight)
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
			markerHeight = Throw.markerHeight(os.clock() - aimStartedAt)
			placeMarker(markerHeight)
		end
	end)

	remotes.MeterStart.OnClientEvent:Connect(function()
		aiming = true
		aimStartedAt = os.clock()
		placeMarker(0)
		hud.meter.Visible = true
		-- Taken over while aiming so Space throws instead of jumping.
		ContextActionService:BindAction(TAP_ACTION, function(_, inputState)
			if inputState == Enum.UserInputState.Begin then
				tap()
			end
			return Enum.ContextActionResult.Sink
		end, false, Enum.KeyCode.Space, Enum.KeyCode.ButtonA)
	end)

	remotes.MeterCancel.OnClientEvent:Connect(hideMeter)

	remotes.Landed.OnClientEvent:Connect(function(dinoName: string, chance: number)
		hud.catch.Text = `{dinoName} · 1 in {chance}`
		hud.catch.Visible = true
	end)

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
			if perfect then
				hud.zone.BackgroundColor3 = GOLD
				hud.prompt.TextColor3 = GOLD
				hud.prompt.Text = "PERFECT!"
			end
			task.delay(RESULT_HOLD, function()
				if not aiming then
					hud.meter.Visible = false
				end
			end)
			camera.CameraType = Enum.CameraType.Scriptable
			hud.banner.Text = if perfect then "PERFECT!" else ""
			hud.banner.Visible = true
			hud.luck.Visible = true
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
				hud.luck.Text = luckText(travelled)
			end
			if t >= 1 then
				break
			end
			RunService.RenderStepped:Wait()
		end

		if isMine then
			hud.banner.Text = `{math.floor(distance)} studs · {Luck.biomeAt(distance).name}`
		end
		task.wait(flight.landingPause)
		egg:Destroy()
		if isMine then
			hud.banner.Visible = false
			hud.luck.Visible = false
			hud.catch.Visible = false
			camera.CameraType = Enum.CameraType.Custom
		end
	end)
end

return ThrowController
