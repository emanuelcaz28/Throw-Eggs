-- The timing meter, the throw's wind-up, the egg's flight and the landing result. Display and input only:
-- the server decides when the meter runs and how far every egg goes.
local ContextActionService = game:GetService("ContextActionService")
local KeyframeSequenceProvider = game:GetService("KeyframeSequenceProvider")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")
local UserInputService = game:GetService("UserInputService")

local DinoStats = require(ReplicatedStorage.Shared.DinoStats)
local Eggs = require(ReplicatedStorage.Shared.Config.Eggs)
local Events = require(ReplicatedStorage.Shared.Config.Events)
local Luck = require(ReplicatedStorage.Shared.Config.Luck)
local PopText = require(ReplicatedStorage.Shared.PopText)
local Shop = require(ReplicatedStorage.Shared.Config.Shop)
local Reveal = require(ReplicatedStorage.Shared.Config.Reveal)
local Throw = require(ReplicatedStorage.Shared.Config.Throw)
local UiKit = require(ReplicatedStorage.Shared.UiKit)
local RevealController = require(script.Parent.RevealController)
local ThrowCinematic = require(script.Parent.ThrowCinematic)

local player = Players.LocalPlayer

local ThrowController = {}

local TAP_ACTION = "ThrowEggTap"
local EGG_SIZE = Vector3.new(2.4, 3, 2.4)
local CATCH_TIMEOUT = 5 -- seconds to wait for the server's catch after landing

local INK = Color3.fromRGB(20, 22, 28)
local TUBE_LOW = Color3.fromRGB(222, 62, 48)
local TUBE_MID = Color3.fromRGB(242, 150, 50)
local TUBE_HIGH = Color3.fromRGB(255, 214, 70)
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

	-- In the pop-up text's look (Config/Pop), since the result word punches in here.
	local prompt = makeLabel(meter)
	prompt.Name = "Prompt"
	prompt.Position, prompt.Size = meterBox(0, PROMPT_TOP, METER_WIDTH, PROMPT_HEIGHT)
	prompt.FontFace = UiKit.FONT
	prompt.TextStrokeTransparency = 1
	local promptOutline = Instance.new("UIStroke")
	promptOutline.Color = UiKit.INK
	promptOutline.Thickness = 3
	promptOutline.LineJoinMode = Enum.LineJoinMode.Round
	promptOutline.Parent = prompt

	local luckPanel = ThrowCinematic.buildLuckPanel(gui)
	local fade = ThrowCinematic.buildFade(gui.Parent)

	-- The wind-up's black bars, in their own layer under the meter that reaches the screen's very top.
	local barsGui = Instance.new("ScreenGui")
	barsGui.Name = "ThrowBars"
	barsGui.IgnoreGuiInset = true
	barsGui.ResetOnSpawn = false
	barsGui.DisplayOrder = -1
	barsGui.Parent = gui.Parent
	local bars = {}
	for _, top in { true, false } do
		local bar = Instance.new("Frame")
		bar.Name = if top then "TopBar" else "BottomBar"
		bar.AnchorPoint = Vector2.new(0, if top then 1 else 0)
		bar.Position = UDim2.fromScale(0, if top then 0 else 1)
		bar.Size = UDim2.fromScale(1, Throw.windup.barHeight)
		bar.BackgroundColor3 = Color3.new(0, 0, 0)
		bar.BorderSizePixel = 0
		bar.Parent = barsGui
		table.insert(bars, { frame = bar, top = top })
	end

	return {
		bars = bars,
		meter = meter,
		zone = zone,
		marker = marker,
		value = value,
		prompt = prompt,
		luckPanel = luckPanel,
		fade = fade,
	}
end

local function makeEgg(color: Color3): Part
	local egg = Instance.new("Part")
	egg.Name = "ThrownEgg"
	egg.Anchored = true
	egg.CanCollide = false
	egg.CanQuery = false
	egg.CanTouch = false
	egg.Size = EGG_SIZE
	egg.Color = color
	egg.CastShadow = true
	local mesh = Instance.new("SpecialMesh")
	mesh.MeshType = Enum.MeshType.Sphere
	mesh.Parent = egg
	egg.Parent = workspace
	return egg
end

-- Slides the wind-up's bars onto the screen, or off it.
local function showBars(hud, shown: boolean)
	local info = TweenInfo.new(Throw.windup.barSlide, Enum.EasingStyle.Quad, if shown then Enum.EasingDirection.Out else Enum.EasingDirection.In)
	for _, bar in hud.bars do
		local y = if bar.top then (if shown then Throw.windup.barHeight else 0) else (if shown then 1 - Throw.windup.barHeight else 1)
		TweenService:Create(bar.frame, info, { Position = UDim2.fromScale(0, y) }):Play()
	end
end

-- The wind-up clip to play: in Studio the clip that Rojo syncs (the latest build_throw.py), registered for
-- testing; live, the published one.
local windupAnimation: Animation? = nil
local function getWindupAnimation(): Animation?
	if windupAnimation then
		return windupAnimation
	end
	local id = Throw.windup.animationId
	if RunService:IsStudio() then
		local clips = ReplicatedStorage.Shared:FindFirstChild("Animations")
		local clip = clips and clips:FindFirstChild("ThrowWindup")
		if clip then
			id = KeyframeSequenceProvider:RegisterKeyframeSequence(clip)
		end
	end
	if id == "" then
		return nil
	end
	local animation = Instance.new("Animation")
	animation.Name = "ThrowWindup"
	animation.AnimationId = id
	windupAnimation = animation
	return animation
end

-- After the tap: the result holds, the bars slide in, then the thrower crouches, spins and lunges, holding the egg
-- in their right hand until the release. Their own camera whips round to face them and back (Config/Throw
-- windup.camera). Returns once the egg leaves the hand (where it then is) and the camera's pose at that moment,
-- after the same wait on every screen so they all stay in step.
local function windUp(thrower: Player, egg: BasePart, isMine: boolean, hud, spot: CFrame?): (Vector3, CFrame?)
	local settings = Throw.windup
	local character = thrower.Character
	local humanoid = character and character:FindFirstChildOfClass("Humanoid")
	local hand = character and character:FindFirstChild("RightHand") :: BasePart?
	local camera = workspace.CurrentCamera
	local startedAt = os.clock()
	local track = nil
	local barsShown = false
	egg.Size = EGG_SIZE * settings.heldScale
	while true do
		local elapsed = os.clock() - startedAt
		if hand and hand.Parent then
			egg.CFrame = hand.CFrame * CFrame.new(settings.eggGrip)
		end
		if isMine then
			if not barsShown and elapsed >= settings.barsAt then
				barsShown = true
				showBars(hud, true)
			end
			-- The thrower's own screen plays the clip; everyone else sees it through replication.
			if not track and elapsed >= settings.holdAfterTap and humanoid then
				local animator = humanoid:FindFirstChildOfClass("Animator")
				local animation = getWindupAnimation()
				if animator and animation then
					track = animator:LoadAnimation(animation)
					track:Play(0.05)
					track.Stopped:Once(function()
						track:Destroy()
					end)
				end
			end
			if spot then
				camera.CFrame = ThrowCinematic.windupCamera(spot, elapsed)
			end
		end
		if elapsed >= Throw.releaseDelay() then
			break
		end
		RunService.RenderStepped:Wait()
	end
	if isMine then
		task.delay(settings.barsOutAfterRelease, showBars, hud, false)
	end
	return egg.Position, if isMine then camera.CFrame else nil
end

local function serverLuck(): number
	local active = (ReplicatedStorage:GetAttribute("ServerLuckEndsAt") or 0) > workspace:GetServerTimeNow()
	return if active then Shop.serverLuck.multiplier else 1
end

-- The reveal has the screen to itself. While aiming and flying, only Throw Power stays
-- (keepPower), so the meter and the luck number aren't crowded.
local function setHudsEnabled(enabled: boolean, keepPower: boolean?)
	for _, name in { "TrainingHud", "PlotHud", "EggShopHud", "IndexHud", "ShopHud", "EventHud" } do
		if keepPower and name == "TrainingHud" then
			continue
		end
		local hud = player.PlayerGui:FindFirstChild(name)
		if hud then
			hud.Enabled = enabled
		end
	end
end

function ThrowController.start()
	local remotes = ReplicatedStorage:WaitForChild("ThrowRemotes")
	local hud = buildGui()

	-- Downloaded now, so even the first throw spins: a clip still loading plays nothing.
	task.spawn(function()
		local animation = getWindupAnimation()
		if animation then
			game:GetService("ContentProvider"):PreloadAsync({ animation })
		end
	end)

	local aiming = false
	local aimStartedAt = 0
	local markerHeight = 0
	local heldEgg: BasePart? = nil -- in the thrower's hand from the dip to black until the release
	local spot: CFrame? = nil -- where this player stands to throw, while they're on the platform
	local equippedEggId: string? = nil
	ReplicatedStorage:WaitForChild("EggRemotes"):WaitForChild("EggsChanged").OnClientEvent:Connect(function(_owned, equipped)
		equippedEggId = equipped
	end)

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

	-- What the meter says the moment the player taps, before anything moves.
	local function showResult(height: number)
		local level = Throw.level(height)
		local perfect = Throw.isPerfect(height)
		hud.prompt.Text = if perfect then "PERFECT!" elseif level >= 8 then "GREAT!" elseif level >= 5 then "GOOD" else "OK"
		hud.prompt.TextColor3 = if perfect then GOLD else TEXT
		if perfect then
			hud.zone.BackgroundColor3 = GOLD
		end
		PopText.punch(hud.prompt)
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

	-- Lets the character go again: after the landing, or when the throw is called off.
	local function releaseCharacter()
		local character = player.Character
		local root = character and character:FindFirstChild("HumanoidRootPart") :: BasePart?
		if root then
			root.Anchored = false
		end
		spot = nil
	end

	local function tap()
		if aiming and os.clock() - aimStartedAt >= Throw.meter.minTime then
			stopAiming()
			showResult(markerHeight)
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
		-- Held in the right hand while aiming; the wind-up moves it itself.
		local character = player.Character
		local hand = character and character:FindFirstChild("RightHand") :: BasePart?
		if heldEgg and spot and hand then
			heldEgg.CFrame = hand.CFrame * CFrame.new(Throw.windup.eggGrip)
		end
	end)

	-- Stepping onto the platform: a dip to black, and back on the thrower standing on the throw spot with the egg
	-- in hand, the camera low behind their right shoulder, and only Throw Power and the meter left on screen.
	remotes.MeterStart.OnClientEvent:Connect(function()
		local character = player.Character
		local root = character and character:FindFirstChild("HumanoidRootPart") :: BasePart?
		local humanoid = character and character:FindFirstChildOfClass("Humanoid")
		if not (root and humanoid) then
			return
		end
		local aim = Throw.aim
		ThrowCinematic.fade(hud.fade, true, aim.fadeOut)
		spot = ThrowCinematic.throwSpot(root, humanoid)
		root.CFrame = spot
		root.AssemblyLinearVelocity = Vector3.zero
		root.Anchored = true
		local equipped = DinoStats.findOption(Eggs, equippedEggId) or Eggs[1]
		heldEgg = heldEgg or makeEgg(equipped.color)
		heldEgg.Size = EGG_SIZE * Throw.windup.heldScale
		local camera = workspace.CurrentCamera
		camera.CameraType = Enum.CameraType.Scriptable
		camera.CFrame = ThrowCinematic.windupCamera(spot, 0)
		setHudsEnabled(false, true)
		placeMarker(0)
		hud.meter.Visible = true
		task.wait(aim.black)
		aiming = true
		aimStartedAt = os.clock()
		-- Taken over while aiming so Space throws instead of jumping.
		ContextActionService:BindAction(TAP_ACTION, function(_, inputState)
			if inputState == Enum.UserInputState.Begin then
				tap()
			end
			return Enum.ContextActionResult.Sink
		end, false, Enum.KeyCode.Space, Enum.KeyCode.ButtonA)
		ThrowCinematic.fade(hud.fade, false, aim.fadeIn)
	end)

	remotes.MeterCancel.OnClientEvent:Connect(function()
		hideMeter()
		releaseCharacter()
		if heldEgg then
			heldEgg:Destroy()
			heldEgg = nil
		end
		workspace.CurrentCamera.CameraType = Enum.CameraType.Custom
		setHudsEnabled(true)
	end)

	local pendingCatch = nil
	remotes.Landed.OnClientEvent:Connect(function(catch)
		pendingCatch = catch
		-- The server's own number, in case this screen's differs a little.
		hud.luckPanel.set(catch.luck)
	end)

	remotes.Launched.OnClientEvent:Connect(function(thrower: Player, distance: number, _perfect: boolean, eggId: string)
		local isMine = thrower == player
		local lane = Throw.lane
		local flight = Throw.flight
		local duration = Throw.flightTime(distance)
		local arc = math.min(distance * flight.arcPerStud, flight.maxArc)
		local eggConfig = DinoStats.findOption(Eggs, eggId) or Eggs[1]
		local egg = if isMine and heldEgg then heldEgg else makeEgg(eggConfig.color)
		egg.Color = eggConfig.color
		if isMine then
			heldEgg = nil
		end
		local trail = ThrowCinematic.addTrail(egg)
		-- The egg lands on the corridor floor, which is lower than the platform, on the lane's middle line.
		local landY = lane.floorY + EGG_SIZE.Y / 2
		local landing = lane.origin + lane.direction * distance
		local camera = workspace.CurrentCamera

		if isMine then
			stopAiming()
			task.delay(RESULT_HOLD, function()
				if not aiming then
					hud.meter.Visible = false
				end
			end)
			camera.CameraType = Enum.CameraType.Scriptable
		end

		-- The egg is in the thrower's hand until the release, then flies from exactly there in a straight line (seen
		-- from above) to where it lands, tumbling end over end from the way the hand held it. No jump or swerve.
		local releasedAt, cameraFrom = windUp(thrower, egg, isMine, hud, if isMine then spot else nil)
		local heldTurn = egg.CFrame.Rotation
		local tumbleAxis = lane.direction:Cross(Vector3.yAxis).Unit
		trail.Enabled = true
		if isMine then
			hud.luckPanel.show(true)
			task.delay(flight.throwPowerHideAt, function()
				local training = player.PlayerGui:FindFirstChild("TrainingHud")
				if training and not aiming then
					training.Enabled = false
				end
			end)
		end

		local startedAt = os.clock()
		while true do
			local elapsed = os.clock() - startedAt
			local t = math.min(elapsed / duration, 1)
			local share = Throw.travelled(t)
			local travelled = distance * share
			-- Drops from the hand to the corridor floor, plus a hill that peaks at arc halfway.
			local height = releasedAt.Y + (landY - releasedAt.Y) * t + arc * 4 * t * (1 - t)
			local along = releasedAt:Lerp(landing, share)
			local position = Vector3.new(along.X, height, along.Z)
			local grow = math.clamp(t / Throw.windup.eggBlend, 0, 1)
			local eased = grow * grow * (3 - 2 * grow)
			egg.Size = EGG_SIZE * (Throw.windup.heldScale + (1 - Throw.windup.heldScale) * eased)
			-- Spins with the distance covered, so it turns fastest out of the hand and slows as the egg does.
			local tumble = CFrame.fromAxisAngle(tumbleAxis, -flight.spin * duration * share)
			egg.CFrame = CFrame.new(position) * tumble * heldTurn
			if isMine and cameraFrom then
				camera.CFrame = ThrowCinematic.flightCamera(cameraFrom, position, elapsed, duration)
				local luck = Luck.at(travelled) * eggConfig.luckBonus * (player:GetAttribute("IndexLuck") or 1) * serverLuck() * Events.multiplier("luck")
				hud.luckPanel.set(luck, Luck.biomeAt(travelled))
			end
			if t >= 1 then
				break
			end
			RunService.RenderStepped:Wait()
		end

		trail.Enabled = false
		ThrowCinematic.landingEffects(Vector3.new(egg.Position.X, lane.floorY, egg.Position.Z))
		if not isMine then
			task.wait(flight.landingPause)
			egg:Destroy()
			return
		end

		task.wait(Reveal.landingHold)
		local waitedFor = 0
		while not pendingCatch and waitedFor < CATCH_TIMEOUT do
			waitedFor += task.wait()
		end
		hud.luckPanel.fadeOut(0.25)
		releaseCharacter()

		local catch = pendingCatch
		pendingCatch = nil
		if catch then
			setHudsEnabled(false)
			-- Whatever goes wrong in the reveal, the player must get their camera and next throw back.
			local ok, err = pcall(RevealController.play, catch, egg)
			if not ok then
				warn(`[ThrowController] Reveal failed: {err}`)
				camera.CameraType = Enum.CameraType.Custom
			end
			setHudsEnabled(true)
		else
			egg:Destroy()
			camera.CameraType = Enum.CameraType.Custom
			setHudsEnabled(true)
		end
		remotes.RevealDone:FireServer()
	end)
end

return ThrowController
