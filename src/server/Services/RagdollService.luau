-- Ragdolls. A player presses the Ragdoll button and their character goes limp and tumbles; a second press, or
-- Config/Troll's maxSeconds, stands them up again. Pure fun: nothing is earned or lost [Owner, 2026-11-12].
--
-- The server decides who is ragdolled (the "Ragdolled" attribute on the character) and swaps the stiff joints for
-- loose ones. The player's own screen then lets the body fall (RagdollController), because Roblox leaves a
-- character's physics to its player.
--
-- Throw area safety: nobody can ragdoll on the throw platform, a ragdolled player can't start a throw
-- (ThrowService.isOnPad asks isRagdolled), and an invisible wall around the platform stops ragdolled bodies only.
local PhysicsService = game:GetService("PhysicsService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Throw = require(ReplicatedStorage.Shared.Config.Throw)
local Troll = require(ReplicatedStorage.Shared.Config.Troll)
local RemoteGuard = require(script.Parent.RemoteGuard)

local RagdollService = {}

local GROUP_BODY = "Ragdoll" -- a ragdolled character's parts
local GROUP_WALL = "ThrowWall" -- stops ragdolled bodies and leashed monsters, and nothing else
local GROUP_PLAYERS = "Players" -- every character's parts while they're up and about
local GROUP_LEASHED = "Leashed" -- a leashed monster's body (LeashController): hits the map and the wall, never a player
local ROOT_JOINTS = { Root = true, RootJoint = true } -- kept stiff, so the root part follows the body

type Record = {
	character: Model,
	startedAt: number,
	forced: boolean?, -- leashed by another player (LeashService): the Ragdoll button can't end it
	added: { Instance }, -- loose joints and limb colliders, removed on getting up
	motors: { Motor6D | AnimationConstraint }, -- the stiff joints switched off
	groups: { [BasePart]: string },
	rootCollide: boolean?,
	requiresNeck: boolean?,
}

local records: { [Player]: Record } = {}
local readyAt: { [Player]: number } = {}
local blockers: { (Player) -> boolean } = {}

-- Other services say when a player may not ragdoll (ThrowService: from the tap until the reveal is done).
function RagdollService.addBlocker(blocker: (Player) -> boolean)
	table.insert(blockers, blocker)
end

function RagdollService.isRagdolled(player: Player): boolean
	return records[player] ~= nil
end

-- Whether a point is inside the wall around the throw platform (the platform plus the wall's margin).
function RagdollService.inThrowArea(position: Vector3): boolean
	local lane = Throw.lane
	local reach = Troll.throwWall.margin + Troll.throwWall.thickness
	local offset = position - lane.zoneCenter
	return math.abs(offset.X) <= lane.zoneSize.X / 2 + reach and math.abs(offset.Z) <= lane.zoneSize.Y / 2 + reach
end

-- Whether a player is at the throw: standing in the throwing area (aiming), or from the tap until the reveal is done.
-- Their monsters can't be leashed meanwhile (LeashService).
function RagdollService.isAtThrow(player: Player): boolean
	local character = player.Character
	local root = character and character:FindFirstChild("HumanoidRootPart") :: BasePart?
	if root and RagdollService.inThrowArea(root.Position) then
		return true
	end
	for _, blocker in blockers do
		if blocker(player) then
			return true
		end
	end
	return false
end

-- Whether a player can't troll right now: not alive, held still (training at the rack), sitting, in the throwing
-- area, or busy with something another service named (addBlocker). Ragdolls and leashes both ask.
function RagdollService.isBusy(player: Player): boolean
	local character = player.Character
	local humanoid = character and character:FindFirstChildOfClass("Humanoid")
	local root = character and character:FindFirstChild("HumanoidRootPart") :: BasePart?
	if not humanoid or not root or humanoid.Health <= 0 then
		return true
	end
	if root.Anchored or humanoid.SeatPart or RagdollService.inThrowArea(root.Position) then
		return true
	end
	for _, blocker in blockers do
		if blocker(player) then
			return true
		end
	end
	return false
end

-- Lets one stiff joint go loose. Older characters are held together by Motor6Ds; newer ones by AnimationConstraints,
-- and those come with their own loose joint (a BallSocketConstraint beside each) that takes over once the stiff one
-- is switched off. A joint with no loose partner gets one made here.
local function loosen(record: Record, joint: Motor6D | AnimationConstraint)
	local part0: BasePart?, part1: BasePart?
	local a0: Attachment?, a1: Attachment?
	if joint:IsA("Motor6D") then
		part0, part1 = joint.Part0, joint.Part1
	else
		a0, a1 = joint.Attachment0, joint.Attachment1
		part0 = a0 and a0.Parent :: any
		part1 = a1 and a1.Parent :: any
	end
	if not part0 or not part1 or not part0:IsA("BasePart") or not part1:IsA("BasePart") then
		return
	end
	local function add<T>(object: T): T
		table.insert(record.added, object :: any)
		return object
	end
	local limb = if joint.Parent == part0 then part0 else part1 -- the joint sits in the limb it moves
	if not limb:FindFirstChildWhichIsA("BallSocketConstraint") then
		if joint:IsA("Motor6D") then
			a0 = add(Instance.new("Attachment"))
			a0.CFrame = joint.C0
			a0.Parent = part0
			a1 = add(Instance.new("Attachment"))
			a1.CFrame = joint.C1
			a1.Parent = part1
		end
		local socket = add(Instance.new("BallSocketConstraint"))
		socket.Name = "RagdollSocket"
		socket.Attachment0 = a0
		socket.Attachment1 = a1
		socket.LimitsEnabled = true
		socket.UpperAngle = Troll.ragdoll.limbSwing
		socket.TwistLimitsEnabled = true
		socket.TwistLowerAngle = -Troll.ragdoll.limbTwist
		socket.TwistUpperAngle = Troll.ragdoll.limbTwist
		socket.Parent = limb
	end
	-- Joined parts mustn't push each other apart.
	local quiet = add(Instance.new("NoCollisionConstraint"))
	quiet.Name = "RagdollQuiet"
	quiet.Part0 = part0
	quiet.Part1 = part1
	quiet.Parent = limb
	-- Roblox keeps a character's arms and legs from colliding, so each limb carries a small solid ball instead.
	local ball = add(Instance.new("Part"))
	ball.Name = "RagdollCollider"
	ball.Shape = Enum.PartType.Ball
	ball.Size = Vector3.one * math.max(0.6, math.min(limb.Size.X, limb.Size.Y, limb.Size.Z))
	ball.Transparency = 1
	ball.Massless = true
	ball.CanQuery = false
	ball.CanTouch = false
	ball.CollisionGroup = GROUP_BODY
	ball.CFrame = limb.CFrame
	local weld = Instance.new("WeldConstraint")
	weld.Part0 = limb
	weld.Part1 = ball
	weld.Parent = ball
	ball.Parent = limb
	table.insert(record.motors, joint)
	joint.Enabled = false
end

local function stop(player: Player)
	local record = records[player]
	if not record then
		return
	end
	records[player] = nil
	readyAt[player] = os.clock() + Troll.ragdoll.cooldown
	local character = record.character
	for _, motor in record.motors do
		if motor.Parent then
			motor.Enabled = true
		end
	end
	for _, object in record.added do
		object:Destroy()
	end
	for part, group in record.groups do
		if part.Parent then
			part.CollisionGroup = group
		end
	end
	if not character.Parent then
		return
	end
	local root = character:FindFirstChild("HumanoidRootPart") :: BasePart?
	if root and record.rootCollide ~= nil then
		root.CanCollide = record.rootCollide
	end
	local humanoid = character:FindFirstChildOfClass("Humanoid")
	if humanoid and record.requiresNeck ~= nil then
		humanoid.RequiresNeck = record.requiresNeck
	end
	character:SetAttribute("Ragdolled", false) -- last: the player's screen stands the body up on this
end

local function start(player: Player, forced: boolean?): boolean
	local character = player.Character
	local humanoid = character and character:FindFirstChildOfClass("Humanoid")
	local root = character and character:FindFirstChild("HumanoidRootPart") :: BasePart?
	if not character or not humanoid or not root or records[player] or RagdollService.isBusy(player) then
		return false
	end
	if not forced and os.clock() < (readyAt[player] or 0) then
		return false
	end

	local record: Record = { character = character, startedAt = os.clock(), added = {}, motors = {}, groups = {}, forced = forced }
	records[player] = record
	record.requiresNeck = humanoid.RequiresNeck
	humanoid.RequiresNeck = false -- a loose neck must not count as a lost head
	record.rootCollide = root.CanCollide
	root.CanCollide = false -- else the body is propped up on the root's box
	for _, object in character:GetDescendants() do
		if object:IsA("BasePart") then
			record.groups[object] = object.CollisionGroup
			object.CollisionGroup = GROUP_BODY
		end
	end
	for _, object in character:GetDescendants() do
		if (object:IsA("Motor6D") or object:IsA("AnimationConstraint")) and not ROOT_JOINTS[object.Name] then
			loosen(record, object)
		end
	end
	character:SetAttribute("Ragdolled", true)

	task.delay(Troll.ragdoll.maxSeconds, function()
		if records[player] == record then
			stop(player)
		end
	end)
	return true
end

-- Another player's leash makes this one go limp (LeashService decides who may). True if they did. It lasts until
-- stop, or the usual longest ragdoll, whichever comes first; their own Ragdoll button can't end it.
function RagdollService.force(player: Player): boolean
	return start(player, true)
end

RagdollService.stop = stop

local function onToggle(player: Player)
	local record = records[player]
	if not record then
		start(player)
	elseif not record.forced and os.clock() - record.startedAt >= Troll.ragdoll.minSeconds then
		stop(player)
	end
end

-- Four walls and a lid around the throw platform that only ragdolled bodies hit.
local function buildThrowWall()
	PhysicsService:RegisterCollisionGroup(GROUP_BODY)
	PhysicsService:RegisterCollisionGroup(GROUP_WALL)
	PhysicsService:CollisionGroupSetCollidable(GROUP_WALL, "Default", false)
	PhysicsService:CollisionGroupSetCollidable(GROUP_WALL, GROUP_WALL, false)
	PhysicsService:CollisionGroupSetCollidable(GROUP_WALL, GROUP_BODY, true)
	PhysicsService:RegisterCollisionGroup(GROUP_PLAYERS)
	PhysicsService:RegisterCollisionGroup(GROUP_LEASHED)
	PhysicsService:CollisionGroupSetCollidable(GROUP_WALL, GROUP_PLAYERS, false)
	PhysicsService:CollisionGroupSetCollidable(GROUP_LEASHED, GROUP_PLAYERS, false)
	PhysicsService:CollisionGroupSetCollidable(GROUP_LEASHED, GROUP_BODY, false)

	local lane = Throw.lane
	local wall = Troll.throwWall
	local halfX = lane.zoneSize.X / 2 + wall.margin
	local halfZ = lane.zoneSize.Y / 2 + wall.margin
	local thick = wall.thickness
	local centre = lane.zoneCenter + Vector3.new(0, wall.height / 2 - 10, 0) -- starts a little under the platform

	local model = Instance.new("Model")
	model.Name = "ThrowAreaWall"
	local function piece(size: Vector3, offset: Vector3)
		local part = Instance.new("Part")
		part.Name = "Wall"
		part.Anchored = true
		part.Transparency = 1
		part.CanQuery = false
		part.CanTouch = false
		part.CastShadow = false
		part.CollisionGroup = GROUP_WALL
		part.Size = size
		part.CFrame = CFrame.new(centre + offset)
		part.Parent = model
	end
	local across = (halfX + thick) * 2
	local along = (halfZ + thick) * 2
	piece(Vector3.new(thick, wall.height, along), Vector3.new(halfX + thick / 2, 0, 0))
	piece(Vector3.new(thick, wall.height, along), Vector3.new(-halfX - thick / 2, 0, 0))
	piece(Vector3.new(across, wall.height, thick), Vector3.new(0, 0, halfZ + thick / 2))
	piece(Vector3.new(across, wall.height, thick), Vector3.new(0, 0, -halfZ - thick / 2))
	piece(Vector3.new(across, thick, along), Vector3.new(0, wall.height / 2 + thick / 2, 0))
	model.Parent = workspace
end

-- Every character's parts go in the Players group, so a leashed monster's body can pass through people.
local function group(character: Model)
	local function take(object: Instance)
		if object:IsA("BasePart") and object.CollisionGroup == "Default" then
			object.CollisionGroup = GROUP_PLAYERS
		end
	end
	for _, object in character:GetDescendants() do
		take(object)
	end
	character.DescendantAdded:Connect(take)
end

local function watch(player: Player)
	player.CharacterRemoving:Connect(function()
		stop(player)
	end)
	player.CharacterAdded:Connect(group)
	if player.Character then
		group(player.Character)
	end
end

function RagdollService.start()
	buildThrowWall()

	local remote = Instance.new("RemoteEvent")
	remote.Name = "RagdollToggle"
	remote.Parent = ReplicatedStorage
	RemoteGuard.connect(remote, onToggle, 4, 6)

	Players.PlayerAdded:Connect(watch)
	for _, player in Players:GetPlayers() do
		watch(player)
	end
	Players.PlayerRemoving:Connect(function(player)
		stop(player)
		readyAt[player] = nil
	end)
end

return RagdollService
