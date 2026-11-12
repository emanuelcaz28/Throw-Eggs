-- The Leash: a switch (the button beside Ragdoll) that stays on until it's pressed again. While it's on, a click or
-- tap on any monster, however far off, takes hold of it; it then floats on the end of a line wherever the cursor
-- points, and the next click throws it wherever it was heading [Owner, 2026-11-12].
--
-- The server decides who holds which monster (the "LeashedBy" attribute, LeashService). Monsters live on each
-- player's own screen, so the line and the tumbling are made here: an invisible ball the monster's size is hauled
-- toward the spot the holder points at, Roblox's physics swings, bounces and rolls it, and the monster is drawn
-- wherever the ball is, bones limp (DinoLifeController.hold). Thrown, it flies on, lies crumpled, heaves itself up,
-- sways dizzily and hurries home. Display only: nothing here is saved or earns anything.
--
-- With the Player Leash pass a click on a nearby player leashes them instead (a rope, further down).
local CollectionService = game:GetService("CollectionService")
local GuiService = game:GetService("GuiService")
local MarketplaceService = game:GetService("MarketplaceService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")

local Config = ReplicatedStorage.Shared.Config
local DinoLife = require(Config.DinoLife)
local Shop = require(Config.Shop)
local Troll = require(Config.Troll)
local HudStyle = require(ReplicatedStorage.Shared.HudStyle)
local DinoLifeController = require(script.Parent.DinoLifeController)
local ThrowAreaPrivacy = require(script.Parent.ThrowAreaPrivacy)

local LeashController = {}

local player = Players.LocalPlayer

type Leash = {
	model: Model,
	body: Part,
	offset: CFrame, -- the monster's pivot, seen from the ball
	holder: Player?,
	hand: BasePart?,
	pull: AlignPosition?,
	extras: { Instance },
	letGoAt: number?,
	radius: number,
	lift: number, -- how far its pivot stands above the ground under it
	hold: number, -- how far from the camera this player holds it
	lastVelocity: Vector3,
	lastSlam: number,
	stun: number, -- the hardest slam it took, 0 to 1
	-- Once it lies still (rest): when, the pose it lies in, the pose it stands up to, and how long it stays down.
	restAt: number?,
	from: CFrame?,
	upright: CFrame?,
	downFor: number?,
	shook: boolean?,
}

local leashes: { [Model]: Leash } = {}

-- The line starts at the holder's middle (their root part), a little to the right where the hand is.
local GRIP = Vector3.new(1.3, 0.2, -0.6)

local function handOf(holder: Player): BasePart?
	local character = holder.Character
	return character and character:FindFirstChild("HumanoidRootPart") :: BasePart?
end

-- Where on the screen this player points: the cursor, or on a phone the middle of the screen (they aim by turning
-- the camera).
local function pointer(): Vector2
	if UserInputService.MouseEnabled then
		return UserInputService:GetMouseLocation()
	end
	local size = workspace.CurrentCamera.ViewportSize
	return Vector2.new(size.X / 2, size.Y * 0.42)
end

local mapOnly = RaycastParams.new()
mapOnly.FilterType = Enum.RaycastFilterType.Exclude
mapOnly.CollisionGroup = "Leashed" -- only what the ball itself would hit: the map, not players...
mapOnly.RespectCanCollide = true -- ...or monsters (the held one would block its own line)

-- The spot this player holds a monster at: out along the cursor's line, `leash.hold` studs from the camera, pulled in
-- front of anything in the way and never further than aimRange from the player.
local function aimSpot(leash: Leash): Vector3?
	local hand = leash.hand
	if not hand or not hand.Parent then
		return nil
	end
	local camera = workspace.CurrentCamera
	local point = pointer()
	local ray = camera:ViewportPointToRay(point.X, point.Y)
	local reach = leash.hold
	local hit = workspace:Raycast(ray.Origin, ray.Direction * reach, mapOnly)
	local spot = if hit then hit.Position + hit.Normal * leash.radius else ray.Origin + ray.Direction * reach
	local offset = spot - hand.Position
	if offset.Magnitude > Troll.leash.aimRange then
		spot = hand.Position + offset.Unit * Troll.leash.aimRange
	end
	return spot
end

local function finish(leash: Leash)
	if leashes[leash.model] ~= leash then
		return
	end
	leashes[leash.model] = nil
	for _, object in leash.extras do
		object:Destroy()
	end
	leash.body:Destroy()
	if leash.model.Parent then
		DinoLifeController.release(leash.model, Troll.leash.homeSpeed)
	end
end

-- The line goes. Thrown (the holder clicked), it keeps the speed and direction the cursor gave it, times the boost
-- the server worked out from the holder's Throw Power; otherwise it just drops.
local function letGo(leash: Leash)
	if leash.letGoAt then
		return
	end
	leash.letGoAt = os.clock()
	for _, object in leash.extras do
		object:Destroy()
	end
	table.clear(leash.extras)
	leash.pull = nil
	local boost = leash.model:GetAttribute("LeashFling")
	local body = leash.body
	if typeof(boost) == "number" and boost > 0 and body.Parent then
		local fling = Troll.leash.fling
		local velocity = body.AssemblyLinearVelocity * boost
		if velocity.Magnitude > fling.maxSpeed then
			velocity = velocity.Unit * fling.maxSpeed
		end
		body.AssemblyLinearVelocity = velocity
		if velocity.Magnitude > 1 then
			body.AssemblyAngularVelocity = velocity.Unit:Cross(Vector3.yAxis) * -fling.spin
		end
		leash.lastVelocity = velocity -- the throw itself isn't a slam
		DinoLifeController.jolt(leash.model, 0.6)
	end
end

-- It lies still: the ball goes, and from here it's all for show (place). It stays down crumpled, longer the harder
-- it was slammed, heaves itself up, sways dizzily, and then goes home (step).
local function rest(leash: Leash)
	local settings = Troll.leash
	local body = leash.body
	local from = body.CFrame * leash.offset
	local look = from.LookVector * Vector3.new(1, 0, 1)
	if look.Magnitude < 0.1 then
		look = from.UpVector * Vector3.new(1, 0, 1) -- lying nose up or nose down
	end
	look = if look.Magnitude > 0.01 then look.Unit else Vector3.xAxis
	local feet = Vector3.new(body.Position.X, body.Position.Y - leash.radius + leash.lift, body.Position.Z)
	leash.from = from
	leash.upright = CFrame.lookAt(feet, feet + look)
	leash.downFor = settings.downSeconds + settings.stunSeconds * leash.stun
	leash.restAt = os.clock()
	body:Destroy()
end

-- Where the monster is drawn this frame.
local function place(leash: Leash): CFrame
	local restAt = leash.restAt
	if not restAt then
		return leash.body.CFrame * leash.offset -- on the line or in the air: wherever its tumbling body is
	end
	local settings = Troll.leash
	local from, upright = leash.from :: CFrame, leash.upright :: CFrame
	local t = os.clock() - restAt - (leash.downFor :: number)
	if t < 0 then
		return from
	elseif t < settings.riseSeconds then
		local u = t / settings.riseSeconds
		return from:Lerp(upright, u * u * (3 - 2 * u)) + Vector3.new(0, math.sin(math.pi * u) * leash.radius * 0.5, 0)
	end
	-- On its feet, swaying in a slowing circle.
	t -= settings.riseSeconds
	local lean = settings.dizzyLean * math.max(0, 1 - t / settings.dizzySeconds)
	return upright * CFrame.Angles(math.sin(t * 7) * lean, 0, math.cos(t * 5.3) * lean)
end

local function begin(model: Model, holder: Player)
	local hand = handOf(holder)
	if not hand or leashes[model] then
		return
	end
	local settings = Troll.leash
	local boxAt, boxSize = model:GetBoundingBox()
	local width = math.clamp(math.min(boxSize.X, boxSize.Y, boxSize.Z), settings.bodyMin, settings.bodyMax)
	local radius = width / 2

	local body = Instance.new("Part")
	body.Name = "LeashBody"
	body.Shape = Enum.PartType.Ball
	body.Size = Vector3.one * width
	body.Transparency = 1
	body.CanQuery = false
	body.CanTouch = false
	body.CastShadow = false
	body.CollisionGroup = "Leashed" -- RagdollService: hits the map and the throw area's wall, never a player
	local volume = 4 / 3 * math.pi * radius ^ 3
	body.CustomPhysicalProperties = PhysicalProperties.new(math.clamp(settings.bodyMass / volume, 0.0001, 100), settings.friction, settings.bounce)
	-- The ball sits at the monster's middle, low enough to rest on the ground it stands on.
	local low = boxAt.Position.Y - boxSize.Y / 2 + radius
	body.CFrame = boxAt.Rotation + Vector3.new(boxAt.Position.X, math.max(low, math.min(boxAt.Position.Y, low + radius)), boxAt.Position.Z)
	local offset = body.CFrame:ToObjectSpace(model:GetPivot())

	local leash: Leash = {
		model = model,
		body = body,
		offset = offset,
		holder = holder,
		hand = hand,
		extras = {},
		radius = radius,
		lift = model:GetPivot().Position.Y - (boxAt.Position.Y - boxSize.Y / 2),
		hold = math.clamp((body.Position - workspace.CurrentCamera.CFrame.Position).Magnitude, settings.holdMin, settings.holdMax),
		lastVelocity = Vector3.zero,
		lastSlam = 0,
		stun = 0,
	}
	if not DinoLifeController.hold(model, function()
		return place(leash)
	end) then
		body:Destroy()
		return
	end

	-- It's hauled by its middle (hauled by its edge, the ball only rolled on the spot), and set slowly turning so it
	-- hangs there helpless; bumps and its limp bones do the rest.
	local collar = Instance.new("Attachment")
	collar.Parent = body
	body.AssemblyAngularVelocity = Vector3.new(math.random() - 0.5, math.random() - 0.5, math.random() - 0.5).Unit * settings.holdSpin
	local pull = Instance.new("AlignPosition")
	pull.Mode = Enum.PositionAlignmentMode.OneAttachment
	pull.Attachment0 = collar
	pull.Position = collar.WorldPosition
	pull.MaxForce = settings.bodyMass * settings.pull
	pull.MaxVelocity = settings.maxSpeed
	pull.Responsiveness = 30
	pull.ApplyAtCenterOfMass = true
	pull.Parent = body
	leash.pull = pull
	local grip = Instance.new("Attachment")
	grip.Name = "LeashGrip"
	grip.Position = GRIP
	grip.Parent = hand
	local line = Instance.new("Beam")
	line.Name = "LeashLine"
	line.Attachment0 = grip
	line.Attachment1 = collar
	line.Width0 = settings.ropeThickness
	line.Width1 = settings.ropeThickness
	line.FaceCamera = true
	line.Segments = 12
	line.CurveSize0 = 2 -- a little slack in the line
	line.CurveSize1 = -2
	line.Color = ColorSequence.new(settings.ropeColor)
	line.LightInfluence = 0
	line.Parent = body
	table.insert(leash.extras, grip)
	table.insert(leash.extras, pull)
	table.insert(leash.extras, line)
	body.Parent = workspace
	leashes[model] = leash
end

-- A leashed player (the Player Leash pass). The server makes them go limp and names their holder on their character
-- ("LeashedBy"). Every screen draws the rope; only the victim's own screen ties a real one, because each player's
-- body is moved by their own screen: it drags them behind the holder, and the holder feels no weight.
type PlayerLeash = { extras: { Instance }, rope: RopeConstraint? }
local playerLeashes: { [Model]: PlayerLeash } = {}

local function endPlayerLeash(character: Model)
	local leash = playerLeashes[character]
	if leash then
		playerLeashes[character] = nil
		for _, object in leash.extras do
			object:Destroy()
		end
	end
end

local function beginPlayerLeash(character: Model, holder: Player)
	local hand = handOf(holder)
	local chest = (character:FindFirstChild("UpperTorso") or character:FindFirstChild("Torso") or character:FindFirstChild("HumanoidRootPart")) :: BasePart?
	if not hand or not chest or playerLeashes[character] then
		return
	end
	local settings = Troll.leash
	local grip = Instance.new("Attachment")
	grip.Name = "LeashGrip"
	grip.Position = GRIP
	grip.Parent = hand
	local collar = Instance.new("Attachment")
	collar.Name = "LeashCollar"
	collar.Parent = chest
	local line = Instance.new("Beam")
	line.Name = "LeashLine"
	line.Attachment0 = grip
	line.Attachment1 = collar
	line.Width0 = settings.ropeThickness
	line.Width1 = settings.ropeThickness
	line.FaceCamera = true
	line.Segments = 1
	line.Color = ColorSequence.new(settings.ropeColor)
	line.LightInfluence = 0
	line.Parent = chest
	local leash: PlayerLeash = { extras = { grip, collar, line } }
	if character == player.Character then
		local rope = Instance.new("RopeConstraint")
		rope.Name = "LeashRope"
		rope.Attachment0 = grip
		rope.Attachment1 = collar
		rope.Length = math.max(Troll.playerLeash.rope, (grip.WorldPosition - collar.WorldPosition).Magnitude)
		rope.Restitution = 0.1
		rope.Parent = chest
		leash.rope = rope
		table.insert(leash.extras, rope)
	end
	playerLeashes[character] = leash
end

local function watchCharacter(character: Model)
	local function changed()
		local userId = character:GetAttribute("LeashedBy")
		local holder = userId and Players:GetPlayerByUserId(userId)
		if holder then
			beginPlayerLeash(character, holder)
		else
			endPlayerLeash(character)
		end
	end
	character:GetAttributeChangedSignal("LeashedBy"):Connect(changed)
	character.Destroying:Connect(function()
		endPlayerLeash(character)
	end)
	task.defer(changed)
end

local function watchPlayer(other: Player)
	if other.Character then
		watchCharacter(other.Character)
	end
	other.CharacterAdded:Connect(watchCharacter)
	other.CharacterRemoving:Connect(endPlayerLeash)
end

local function watch(model: Model)
	local function changed()
		local userId = model:GetAttribute("LeashedBy")
		local leash = leashes[model]
		if userId then
			local holder = Players:GetPlayerByUserId(userId)
			if holder and leash and leash.letGoAt then
				finish(leash) -- taken again before it was back on its feet
				leash = nil
			end
			if holder and not leash then
				begin(model, holder)
			end
		elseif leash then
			letGo(leash)
		end
	end
	model:GetAttributeChangedSignal("LeashedBy"):Connect(changed)
	task.defer(changed) -- after DinoLifeController has taken the monster in
end

local aimRemote: UnreliableRemoteEvent? = nil
local lastAimSent = 0

local function step(dt: number)
	local settings = Troll.leash
	local now = os.clock()
	for character, leash in playerLeashes do
		local rope = leash.rope
		if rope and rope.Length > Troll.playerLeash.rope then
			rope.Length = math.max(Troll.playerLeash.rope, rope.Length - 0.6) -- reeled in
		end
		local grip = leash.extras[1]
		if not character.Parent or not grip.Parent then
			endPlayerLeash(character) -- the holder's character went
		end
	end
	for model, leash in leashes do
		local body = leash.body
		if not model.Parent then
			finish(leash) -- sold, picked up, or its plot was rebuilt
		elseif leash.restAt then
			local t = now - leash.restAt - (leash.downFor :: number)
			if t >= settings.riseSeconds + settings.dizzySeconds then
				finish(leash) -- steady again: off home
			elseif t >= 0 and not leash.shook then
				leash.shook = true
				DinoLifeController.jolt(model, 0.5) -- it shakes itself as it heaves up
			end
		elseif not body.Parent then
			finish(leash) -- it fell out of the world
		else
			-- A slam: its body stopped or turned hard in one moment (the haul itself is far gentler than that).
			local velocity = body.AssemblyLinearVelocity
			local change = (velocity - leash.lastVelocity).Magnitude
			leash.lastVelocity = velocity
			if change > settings.slamSpeed and now - leash.lastSlam > 0.2 then
				leash.lastSlam = now
				local strength = math.clamp(change / settings.slamFull, 0.25, 1)
				leash.stun = math.max(leash.stun, strength)
				DinoLifeController.jolt(model, strength)
			end
			if leash.letGoAt then
				-- Flying free: it comes to rest once it lies still, or when the time is up.
				local age = now - leash.letGoAt
				if leash.lastSlam > leash.letGoAt or age > settings.rollAfter then
					-- Down from the throw: it rolls to a stop instead of rolling on across the map.
					local slow = math.exp(-settings.rollDrag * dt)
					body.AssemblyLinearVelocity = Vector3.new(velocity.X * slow, velocity.Y, velocity.Z * slow)
					body.AssemblyAngularVelocity *= slow
				end
				if age >= settings.settleSeconds or (age > 0.4 and velocity.Magnitude < settings.stillSpeed) then
					rest(leash)
				end
			else
				local hand = leash.hand
				local pull = leash.pull
				if not hand or not hand.Parent or not pull then
					letGo(leash) -- the holder's character went
				elseif leash.holder == player then
					-- Mine: hauled to where I point, and the server is told so other screens can follow.
					local spot = aimSpot(leash)
					if spot then
						pull.Position = spot
						if aimRemote and now - lastAimSent >= 0.1 then
							lastAimSent = now
							aimRemote:FireServer(spot)
						end
					end
				else
					-- Someone else's: hauled to where they said they point; until that arrives, above their head.
					local spot = model:GetAttribute("LeashAim")
					pull.Position = if typeof(spot) == "Vector3" then spot else hand.Position + Vector3.new(0, 10 + leash.radius, 0)
				end
			end
		end
	end
end

-- The walking plot monster under a point on the screen, or the other player there.
local function targetAt(point: Vector2): (Model?, Player?)
	local include: { Instance } = {}
	for _, model in CollectionService:GetTagged(DinoLife.tag) do
		if model:GetAttribute("DinoKey") and model:GetAttribute("PlotIndex") and not model:GetAttribute("Stay") and not model:GetAttribute("Carried") then
			table.insert(include, model)
		end
	end
	for _, other in Players:GetPlayers() do
		if other ~= player and other.Character then
			table.insert(include, other.Character)
		end
	end
	local params = RaycastParams.new()
	params.FilterType = Enum.RaycastFilterType.Include
	params.FilterDescendantsInstances = include
	local ray = workspace.CurrentCamera:ViewportPointToRay(point.X, point.Y)
	local hit = workspace:Raycast(ray.Origin, ray.Direction * 2000, params)
	if not hit then
		return nil, nil
	end
	for _, owner in include do
		if hit.Instance:IsDescendantOf(owner) then
			local other = Players:GetPlayerFromCharacter(owner)
			if other then
				return nil, other
			end
			return owner :: Model, nil
		end
	end
	return nil, nil
end

function LeashController.start()
	for _, model in CollectionService:GetTagged(DinoLife.tag) do
		watch(model)
	end
	CollectionService:GetInstanceAddedSignal(DinoLife.tag):Connect(watch)
	CollectionService:GetInstanceRemovedSignal(DinoLife.tag):Connect(function(model)
		local leash = leashes[model]
		if leash then
			finish(leash)
		end
	end)
	RunService.Heartbeat:Connect(step)
	for _, other in Players:GetPlayers() do
		watchPlayer(other)
	end
	Players.PlayerAdded:Connect(watchPlayer)

	local remote = ReplicatedStorage:WaitForChild("LeashToggle") :: RemoteEvent
	local playerRemote = ReplicatedStorage:WaitForChild("LeashPlayer") :: RemoteEvent
	aimRemote = ReplicatedStorage:WaitForChild("LeashAim") :: UnreliableRemoteEvent

	local gui = Instance.new("ScreenGui")
	gui.Name = "LeashHud"
	gui.ResetOnSpawn = false
	gui.Parent = player:WaitForChild("PlayerGui")

	-- Beside Ragdoll: the switch. A green dot in its corner shows it's on. PlotController reads "LeashArmed" and
	-- leaves clicks alone while it is (no picking monsters up by accident).
	local across = (HudStyle.BUTTON_SIZE + HudStyle.BUTTON_GAP) * HudStyle.scale()
	local button = HudStyle.iconButton(gui, "🪢", "Leash")
	button.AnchorPoint = Vector2.new(0, 0.5)
	button.Position = UDim2.new(0, 16 + across, HudStyle.COLUMN_CENTER, across * 1.5)
	local dot = Instance.new("Frame")
	dot.Name = "On"
	dot.AnchorPoint = Vector2.new(1, 0)
	dot.Position = UDim2.new(1, -5, 0, 5)
	dot.Size = UDim2.fromOffset(16, 16)
	dot.BackgroundColor3 = Color3.fromRGB(80, 230, 110)
	dot.Visible = false
	dot.ZIndex = 5
	dot.Parent = button
	local round = Instance.new("UICorner")
	round.CornerRadius = UDim.new(1, 0)
	round.Parent = dot

	local armed = false
	local function holding(): boolean
		for model, leash in leashes do
			if leash.holder == player and not leash.letGoAt and model:GetAttribute("LeashedBy") == player.UserId then
				return true
			end
		end
		for character in playerLeashes do
			if character:GetAttribute("LeashedBy") == player.UserId then
				return true
			end
		end
		return false
	end
	local function setArmed(on: boolean)
		armed = on
		dot.Visible = on
		player:SetAttribute("LeashArmed", on or nil)
		if not on and holding() then
			remote:FireServer() -- switching off throws whatever is held
		end
	end
	button.Activated:Connect(function()
		setArmed(not armed)
	end)

	-- A click or tap while the Leash is on: throw what's held, else take hold of what was clicked.
	local function press(point: Vector2)
		if not armed or ThrowAreaPrivacy.inArea() then
			return
		end
		if holding() then
			remote:FireServer()
			return
		end
		local model, other = targetAt(point)
		if model then
			remote:FireServer(model:GetAttribute("PlotIndex"), model:GetAttribute("DinoKey"))
		elseif other then
			local theirs = other.Character and other.Character:FindFirstChild("HumanoidRootPart") :: BasePart?
			local mine = handOf(player)
			if not theirs or not mine or (theirs.Position - mine.Position).Magnitude > Troll.playerLeash.reach or Shop.playerLeash.passId == 0 then
				return
			end
			if player:GetAttribute("HasPlayerLeash") == true then
				playerRemote:FireServer(other.UserId)
			else
				MarketplaceService:PromptGamePassPurchase(player, Shop.playerLeash.passId)
			end
		end
	end
	UserInputService.InputBegan:Connect(function(input, gameProcessed)
		if not gameProcessed and input.UserInputType == Enum.UserInputType.MouseButton1 then
			press(UserInputService:GetMouseLocation())
		end
	end)
	UserInputService.TouchTap:Connect(function(positions, gameProcessed)
		if not gameProcessed and #positions == 1 then
			press(positions[1] + GuiService:GetGuiInset())
		end
	end)

	task.spawn(function()
		while true do
			task.wait(0.25)
			button.Visible = not ThrowAreaPrivacy.inArea() and player:GetAttribute("IsTraining") ~= true
		end
	end)
end

return LeashController
