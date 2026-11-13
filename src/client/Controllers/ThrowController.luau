-- The timing meter, the throw's wind-up, the egg's flight and the landing result. Display and input only:
-- the server decides when the meter runs and how far every egg goes.
local ContextActionService = game:GetService("ContextActionService")
local GuiService = game:GetService("GuiService")
local KeyframeSequenceProvider = game:GetService("KeyframeSequenceProvider")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")
local UserInputService = game:GetService("UserInputService")

local DinoStats = require(ReplicatedStorage.Shared.DinoStats)
local EggModel = require(ReplicatedStorage.Shared.EggModel)
local Eggs = require(ReplicatedStorage.Shared.Config.Eggs)
local HudStyle = require(ReplicatedStorage.Shared.HudStyle)
local Luck = require(ReplicatedStorage.Shared.Config.Luck)
local PopText = require(ReplicatedStorage.Shared.PopText)
local LuckBoosts = require(ReplicatedStorage.Shared.LuckBoosts)
local LuckOfferController = require(script.Parent.LuckOfferController)
local Reveal = require(ReplicatedStorage.Shared.Config.Reveal)
local Throw = require(ReplicatedStorage.Shared.Config.Throw)
local UiKit = require(ReplicatedStorage.Shared.UiKit)
local RevealController = require(script.Parent.RevealController)
local PerfectMoment = require(script.Parent.PerfectMoment)
local GameFeelJuice = require(script.Parent.GameFeelJuice)
local MusicController = require(script.Parent.MusicController)
local RevealSound = require(script.Parent.RevealSound)
local ThrowCinematic = require(script.Parent.ThrowCinematic)
local ThrowAreaPrivacy = require(script.Parent.ThrowAreaPrivacy)
local FlightFx = require(ReplicatedStorage.Shared.Config.FlightFx)

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
	meter:SetAttribute("NoClickSound", true) -- the throw has its own sounds
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

	local zoneBottom = TUBE_TOP + TUBE_HEIGHT * Throw.meter.perfectZone
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
	barsGui.ScreenInsets = Enum.ScreenInsets.None -- edge to edge, past a phone's notch too
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

-- The thrown egg: a ball in its egg's colour, dressed in the egg's Blender model when the place has one (EggModel).
local function makeEgg(eggConfig): Part
	local egg = Instance.new("Part")
	egg.Name = "ThrownEgg"
	egg.Anchored = true
	egg.CanCollide = false
	egg.CanQuery = false
	egg.CanTouch = false
	egg.Size = EGG_SIZE
	egg.Color = eggConfig.color
	egg.CastShadow = true
	local mesh = Instance.new("SpecialMesh")
	mesh.MeshType = Enum.MeshType.Sphere
	mesh.Parent = egg
	egg.Parent = workspace
	EggModel.dress(egg, eggConfig.id)
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
	local whooshed = false
	local whooshAt = Throw.releaseDelay() - Reveal.sounds.throwWhooshLead
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
		if not whooshed and elapsed >= whooshAt then
			whooshed = true
			RevealSound.throwWhoosh(isMine) -- peaks with the release
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

-- Server Luck, as the server works it out.
local function boughtLuck(): number
	return LuckBoosts.multiplier(player, workspace:GetServerTimeNow())
end

-- True while a throw is aiming, flying or revealing: no jump button then.
local throwBusy = false
-- This screen took the player into the meter (the dip to black, frozen on the throw spot) and the egg hasn't gone.
local meterTaken = false
-- The tap has gone to the server: from then on Back to Plot can't take the player away from their throw.
local tapSent = false
-- Calls the meter off on this screen (built in start()).
local cancelMeter: () -> () = function() end

-- Back to Plot (HomeController) shows while the meter is up, and whenever the player stands on the throw platform
-- outside a throw, so there's always a way out of the throwing area [player feedback, 2026-11-08]. Never from the
-- tap until the reveal is over.
-- In the throwing area, Throw Power (with LIMIT) sits at the very bottom of the screen [owner, 2026-11-12], and the
-- cash goes up into the spot it leaves; the $/s line is hidden there. Back to the usual spots everywhere else.
local powerLow: boolean? = nil
local function placePowerStat(low: boolean)
	if powerLow == low then
		return
	end
	local gui = player.PlayerGui
	local power = gui:FindFirstChild("TrainingHud") and gui.TrainingHud:FindFirstChild("PowerStat")
	local plotHud = gui:FindFirstChild("PlotHud")
	local cash = plotHud and plotHud:FindFirstChild("CashStat")
	local income = plotHud and plotHud:FindFirstChild("Income")
	if not (power and cash and income) then
		return -- not built yet; tried again next frame
	end
	powerLow = low
	local scale = HudStyle.scale()
	if low then
		power.Position = UDim2.new(0, 16, 1, -12 * scale)
		cash.Position = UDim2.new(0, 16, 1, -(12 + 52 + 8) * scale)
		income.Visible = false
	else
		power.Position = UDim2.new(0, 16, 1, -98 * scale)
		cash.Position = UDim2.new(0, 16, 1, -income.Size.Y.Offset - 12)
		income.Visible = true
	end
end

local function updateHomeButton(onPlatform: boolean)
	placePowerStat(onPlatform or meterTaken)
	local home = player.PlayerGui:FindFirstChild("HomeHud")
	local shown = if meterTaken then not tapSent else onPlatform and not throwBusy
	if home and home.Enabled ~= shown then
		home.Enabled = shown
	end
end

-- Phones: the jump button is hidden and jumping is switched off while the player is over the throw platform or
-- in a throw. GuiService.TouchControlsEnabled alone wasn't enough: the button still showed up there, and a jump
-- in the throw area left the player stuck. The platform check is the same one the server uses.
local function lockJumping()
	local character = Players.LocalPlayer.Character
	local root = character and character:FindFirstChild("HumanoidRootPart") :: BasePart?
	local humanoid = character and character:FindFirstChildOfClass("Humanoid")
	local onPlatform = root ~= nil and Throw.onPlatform(root.Position)
	updateHomeButton(onPlatform)
	local locked = throwBusy or onPlatform
	if humanoid then
		if locked then
			humanoid.Jump = false
		end
		if humanoid:GetStateEnabled(Enum.HumanoidStateType.Jumping) == locked then
			humanoid:SetStateEnabled(Enum.HumanoidStateType.Jumping, not locked)
		end
	end
	local touchGui = Players.LocalPlayer.PlayerGui:FindFirstChild("TouchGui")
	local jumpButton = touchGui and touchGui:FindFirstChild("JumpButton", true)
	if jumpButton and jumpButton:IsA("GuiObject") and jumpButton.Visible == locked then
		jumpButton.Visible = not locked
	end
end

-- The reveal has the screen to itself. While aiming and flying, only Throw Power stays
-- (keepPower), so the meter and the luck number aren't crowded.
local function setHudsEnabled(enabled: boolean, keepPower: boolean?)
	-- A phone's thumbstick and jump button go too: the thrower can't move, and the jump button sat on the meter.
	GuiService.TouchControlsEnabled = enabled
	throwBusy = not enabled
	for _, name in { "TrainingHud", "PlotHud", "DailyButtonHud", "EggShopHud", "IndexHud", "ShopHud", "BoostHud", "BoostCardHud", "DailyHud", "GoalHud", "SettingsHud", "SettingsButtonHud", "TutorialHud", "TutorialPointerHud", "ReadyPopupHud", "PowerLimitHud" } do
		if keepPower and name == "TrainingHud" then
			continue
		end
		local hud = player.PlayerGui:FindFirstChild(name)
		if hud then
			hud.Enabled = enabled
		end
	end
end

-- Back to Plot (HomeController) leaves the meter on this screen at once, without waiting for the server. False from
-- the tap until the reveal is over, when nothing may move the thrower.
function ThrowController.leaveMeter(): boolean
	if tapSent or (throwBusy and not meterTaken) then
		return false
	end
	cancelMeter()
	return true
end

function ThrowController.start()
	LuckOfferController.start()
	RunService.Heartbeat:Connect(lockJumping)
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
		RevealSound.meterTap(perfect) -- the soft pop, or the PERFECT sound on the top level
		if perfect then
			hud.zone.BackgroundColor3 = GOLD
			PerfectMoment.play()
			GameFeelJuice.perfectHit(hud.meter, hud.zone) -- the burst on the meter itself
		end
		PopText.punch(hud.prompt)
	end

	-- Stops taking taps. The meter stays on screen until hideMeter.
	local function stopAiming()
		aiming = false
		LuckOfferController.hide()
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
		if aiming and os.clock() - aimStartedAt >= Throw.meter.minTime and not LuckOfferController.blocksThrow() then
			local lucky = LuckOfferController.chosen() -- read before stopAiming hides the offer
			if lucky then
				markerHeight = 1 -- a picked luck boost is always a PERFECT throw (the server makes it one too)
			end
			stopAiming()
			showResult(markerHeight)
			tapSent = true
			remotes.Tap:FireServer(markerHeight, lucky)
		end
	end

	hud.meter.Activated:Connect(tap)
	-- A click or a touch anywhere throws, not just on the meter (phones had to hit the meter itself).
	UserInputService.InputBegan:Connect(function(input, gameProcessed)
		local kind = input.UserInputType
		if not gameProcessed and (kind == Enum.UserInputType.MouseButton1 or kind == Enum.UserInputType.Touch) then
			tap()
		end
	end)

	RunService.RenderStepped:Connect(function()
		if aiming then
			-- With a luck boost ON the marker waits at the top, in PERFECT: any tap is a perfect throw [Owner, 2026-11-09].
			markerHeight = if LuckOfferController.chosen() then 1 else Throw.markerHeight(os.clock() - aimStartedAt)
			placeMarker(markerHeight)
		end
		-- Held in the right hand while aiming; the wind-up moves it itself.
		local character = player.Character
		local hand = character and character:FindFirstChild("RightHand") :: BasePart?
		if heldEgg and spot and hand then
			heldEgg.CFrame = hand.CFrame * CFrame.new(Throw.windup.eggGrip)
		end
	end)

	-- Goes up on every meter start and every call-off, so a call-off during the dip to black stops the start.
	local meterRun = 0

	-- Calls the meter off on this screen: the server's MeterCancel, Back to Plot, or the player off the platform
	-- during the dip. Nothing to undo when this screen never took the meter (it turned it down).
	cancelMeter = function()
		meterRun += 1
		if not meterTaken then
			return
		end
		meterTaken = false
		tapSent = false
		MusicController.setThrowing(false)
		hideMeter()
		releaseCharacter()
		if heldEgg then
			heldEgg:Destroy()
			heldEgg = nil
		end
		workspace.CurrentCamera.CameraType = Enum.CameraType.Custom
		setHudsEnabled(true)
		task.spawn(ThrowCinematic.fade, hud.fade, false, Throw.aim.fadeIn) -- in case it came during the dip to black
	end

	local function standingOnPlatform(): boolean
		local character = player.Character
		local root = character and character:FindFirstChild("HumanoidRootPart") :: BasePart?
		return root ~= nil and Throw.onPlatform(root.Position)
	end

	-- Stepping onto the platform: a dip to black, and back on the thrower standing on the throw spot with the egg
	-- in hand, the camera low behind their right shoulder, and only Throw Power and the meter left on screen.
	remotes.MeterStart.OnClientEvent:Connect(function()
		-- The server saw the player on the platform a moment ago. With lag they may have walked off since, and they
		-- were pulled back onto it from far away and frozen [player feedback, 2026-11-08]. Now this screen turns the
		-- meter down instead, and the server calls it off.
		if not standingOnPlatform() then
			remotes.MeterDeclined:FireServer()
			return
		end
		meterRun += 1
		local run = meterRun
		meterTaken = true
		tapSent = false
		local aim = Throw.aim
		ThrowCinematic.fade(hud.fade, true, aim.fadeOut)
		if run ~= meterRun then
			return -- called off during the dip (cancelMeter fades back in)
		end
		local character = player.Character
		local root = character and character:FindFirstChild("HumanoidRootPart") :: BasePart?
		local humanoid = character and character:FindFirstChildOfClass("Humanoid")
		if not (root and humanoid and Throw.onPlatform(root.Position)) then
			-- Walked off during the dip.
			cancelMeter()
			remotes.MeterDeclined:FireServer()
			return
		end
		spot = ThrowCinematic.throwSpot(root, humanoid)
		ThrowCinematic.setThrower(character)
		root.CFrame = spot
		root.AssemblyLinearVelocity = Vector3.zero
		root.Anchored = true
		local equipped = DinoStats.findOption(Eggs, equippedEggId) or Eggs[1]
		heldEgg = heldEgg or makeEgg(equipped)
		heldEgg.Size = EGG_SIZE * Throw.windup.heldScale
		local camera = workspace.CurrentCamera
		camera.CameraType = Enum.CameraType.Scriptable
		camera.CFrame = ThrowCinematic.windupCamera(spot, 0)
		setHudsEnabled(false, true)
		MusicController.setThrowing(true) -- the throwing area's music, until the egg lands (Config/Music)
		placeMarker(0)
		hud.meter.Visible = true
		task.wait(aim.black)
		if run ~= meterRun then
			return -- called off while black
		end
		aiming = true
		aimStartedAt = os.clock()
		LuckOfferController.show(equipped.id)
		-- Taken over while aiming so Space throws instead of jumping.
		ContextActionService:BindAction(TAP_ACTION, function(_, inputState)
			if inputState == Enum.UserInputState.Begin then
				tap()
			end
			return Enum.ContextActionResult.Sink
		end, false, Enum.KeyCode.Space, Enum.KeyCode.ButtonA)
		ThrowCinematic.fade(hud.fade, false, aim.fadeIn)
	end)

	remotes.MeterCancel.OnClientEvent:Connect(cancelMeter)

	local pendingCatch = nil
	remotes.Landed.OnClientEvent:Connect(function(catch)
		pendingCatch = catch
		-- The server's own number, in case this screen's differs a little.
		hud.luckPanel.set(catch.luck)
	end)

	-- A throw from the tap to the end of its reveal, on the thrower's screen and everyone else's.
	local function playThrow(thrower: Player, distance: number, perfect: boolean, eggId: string, luckDistance: number?)
		local isMine = thrower == player
		if not isMine and ThrowAreaPrivacy.inArea() then
			return -- I'm in the throwing area, where the other throwers are hidden: their egg isn't shown either
		end
		local lane = Throw.lane
		local flight = Throw.flight
		local duration = Throw.flightTime(distance)
		local arc = math.min(distance * flight.arcPerStud, flight.maxArc)
		local eggConfig = DinoStats.findOption(Eggs, eggId) or Eggs[1]
		-- The egg's share of the luck shown, against the egg made for the world it lands in (Luck.eggFactor).
		-- Luck counts the real reach, which can be a little past where the egg stops (Throw.luckDistance).
		local luckStretch = (luckDistance or distance) / math.max(distance, 1)
		local eggLuck = Luck.eggFactor(eggConfig.luckBonus, luckDistance or distance)
		local egg = if isMine and heldEgg then heldEgg else makeEgg(eggConfig)
		egg.Color = eggConfig.color
		EggModel.dress(egg, eggConfig.id) -- the server's egg, should it differ from the one in the hand
		if isMine then
			heldEgg = nil
			meterTaken = false -- the egg has gone: the meter is over, and Back to Plot waits for the reveal's end
			tapSent = false
			pendingCatch = nil -- an earlier throw's catch that came too late isn't this one's
		end
		local trail = ThrowCinematic.addTrail(egg)
		if perfect then
			GameFeelJuice.goldTrail(trail) -- a PERFECT throw flies gold, on every screen
		end
		-- The egg lands on the corridor floor, which is lower than the platform, on the lane's middle line.
		local landY = lane.floorY + EGG_SIZE.Y / 2
		local landing = lane.origin + lane.direction * distance
		-- It touches down a little short and bounces on to there (Config/Throw landing.bounce).
		local run = math.min(Throw.landing.bounce.run, distance * 0.3)
		local touchdown = landing - lane.direction * run
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
		if isMine then
			MusicController.setThrown() -- the throwing music drops lower while the egg flies
		end
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
		local burstThrough = false
		local world = Luck.biomeAt(0) -- the world the egg is over; each new one tints the streak, and on my screen rings and chimes
		local streakTinted = not perfect -- a PERFECT throw's streak stays gold
		if streakTinted then
			ThrowCinematic.tintTrail(trail, world.color)
		end
		while true do
			local elapsed = os.clock() - startedAt
			local t = math.min(elapsed / duration, 1)
			local share = Throw.flightShare(elapsed, distance)
			local travelled = distance * share
			-- Drops from the hand to the corridor floor, plus a hill that peaks at arc halfway.
			local height = releasedAt.Y + (landY - releasedAt.Y) * t + arc * 4 * t * (1 - t)
			local along = releasedAt:Lerp(touchdown, share)
			local position = Vector3.new(along.X, height, along.Z)
			-- The camera follows only part of the rise and fall, so the arc shows on screen (Config/FlightFx arcFollow).
			local followed = Vector3.new(along.X, height - arc * 4 * t * (1 - t) * (1 - FlightFx.arcFollow), along.Z)
			local grow = math.clamp(t / Throw.windup.eggBlend, 0, 1)
			local eased = grow * grow * (3 - 2 * grow)
			egg.Size = EGG_SIZE * (Throw.windup.heldScale + (1 - Throw.windup.heldScale) * eased)
			-- Spins with the distance covered, so it turns fastest out of the hand and slows as the egg does.
			local tumble = CFrame.fromAxisAngle(tumbleAxis, -flight.spin * duration * share)
			egg.CFrame = CFrame.new(position) * tumble * heldTurn
			local over = Luck.biomeAt(travelled)
			if over ~= world then
				world = over
				if streakTinted then
					ThrowCinematic.tintTrail(trail, over.color)
				end
				if isMine and not over.hidden then -- The Deep End gets the door's burst instead
					ThrowCinematic.worldGate(egg, over.color)
				end
			end
			if isMine and cameraFrom then
				camera.CFrame = ThrowCinematic.flightCamera(cameraFrom, followed, elapsed, duration)
				local luck = Luck.at(travelled * luckStretch) * eggLuck * boughtLuck() -- a lucky throw's x isn't shown [Owner, 2026-11-06]
				hud.luckPanel.set(luck, Luck.biomeAt(travelled))
				if travelled >= Throw.lastDoorAt and not burstThrough then
					burstThrough = true
					ThrowCinematic.doorBurst()
				end
			end
			if t >= 1 then
				break
			end
			RunService.RenderStepped:Wait()
		end

		trail.Enabled = false
		ThrowCinematic.landingEffects(Vector3.new(egg.Position.X, lane.floorY, egg.Position.Z))
		RevealSound.eggDrop(isMine)
		if isMine then
			MusicController.setThrowing(false) -- the egg has landed: the throwing music is cut off
		end
		-- Bounces on, squashing, comes upright, rocks and trembles; my camera follows it down the lane, jolting on
		-- each touch-down.
		local rest = Vector3.new(landing.X, landY, landing.Z)
		EggModel.bounce(egg, rest, if isMine and cameraFrom
			then function(_t, track, jolt)
				local shake = Vector3.new(math.random() - 0.5, math.random() - 0.5, math.random() - 0.5) * jolt * 0.5
				camera.CFrame = ThrowCinematic.flightCamera(cameraFrom, track, duration, duration) + shake
			end
			else nil)
		EggModel.split(egg) -- cut in half where it lands, white and yolk showing (Config/Throw landing.split)
		if EggModel.has(eggConfig.id) then
			task.delay(Throw.landing.split.delay, RevealSound.eggSlice, isMine) -- with the streak's sweep
		end
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
		-- Still over the platform means the walk home didn't happen (the reveal failed, or there is no plot): put the
		-- player back on their plot, so they can walk away instead of being sent to the meter again.
		local character = player.Character
		local root = character and character:FindFirstChild("HumanoidRootPart") :: BasePart?
		if root and Throw.onPlatform(root.Position) then
			RevealController.returnHome()
		end
		remotes.RevealDone:FireServer()
	end

	remotes.Launched.OnClientEvent:Connect(function(thrower: Player, ...: any)
		local ok, err = pcall(playThrow, thrower, ...)
		if not ok and thrower == player then
			-- Whatever broke, the thrower gets their character, camera and HUD back and goes home, and the server hears
			-- the throw is over, so they're never left frozen in the throwing area.
			warn(`[ThrowController] Throw failed: {err}`)
			stopAiming()
			hud.meter.Visible = false
			hud.luckPanel.show(false)
			showBars(hud, false)
			releaseCharacter()
			MusicController.setThrowing(false)
			workspace.CurrentCamera.CameraType = Enum.CameraType.Custom
			setHudsEnabled(true)
			task.spawn(ThrowCinematic.fade, hud.fade, false, Throw.aim.fadeIn)
			if standingOnPlatform() then
				RevealController.returnHome()
			end
			remotes.RevealDone:FireServer()
		end
	end)
end

return ThrowController
