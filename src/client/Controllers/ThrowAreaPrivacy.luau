-- While you stand in the throwing area (the throw platform, Throw.onPlatform), the other players standing there with you
-- are hidden on your screen, with their names: you throw alone. Anyone outside the area sees everyone as normal, and
-- you see the throwers again as soon as you step off [Owner, 2026-11-12]. Only this player's screen changes
-- (LocalTransparencyModifier): the server and other players never see it. Their throws are skipped on your screen
-- too while you're in the area (ThrowController), so no egg flies out of an empty spot. Display only.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local Throw = require(ReplicatedStorage.Shared.Config.Throw)

local ThrowAreaPrivacy = {}

local CHECK_EVERY = 0.15 -- seconds between checks

local player = Players.LocalPlayer
local hidden: { [Model]: { humanoid: Humanoid?, display: Enum.HumanoidDisplayDistanceType? } } = {}

local function inArea(character: Model?): boolean
	local root = character and character:FindFirstChild("HumanoidRootPart") :: BasePart?
	return root ~= nil and Throw.onPlatform(root.Position)
end

-- Whether this player is in the throwing area now.
function ThrowAreaPrivacy.inArea(): boolean
	return inArea(player.Character)
end

local function setVisible(character: Model, visible: boolean)
	local modifier = if visible then 0 else 1
	for _, object in character:GetDescendants() do
		if object:IsA("BasePart") or object:IsA("Decal") then
			object.LocalTransparencyModifier = modifier
		end
	end
end

local function hide(character: Model)
	local record = hidden[character]
	if not record then
		local humanoid = character:FindFirstChildOfClass("Humanoid")
		record = { humanoid = humanoid, display = humanoid and humanoid.DisplayDistanceType }
		hidden[character] = record
		if humanoid then
			humanoid.DisplayDistanceType = Enum.HumanoidDisplayDistanceType.None -- their name and health bar too
		end
	end
	setVisible(character, false) -- every check, so a hat or tool added since is hidden too
end

local function show(character: Model)
	local record = hidden[character]
	if not record then
		return
	end
	hidden[character] = nil
	if character.Parent then
		setVisible(character, true)
		if record.humanoid and record.display then
			record.humanoid.DisplayDistanceType = record.display
		end
	end
end

local function update()
	local mine = ThrowAreaPrivacy.inArea()
	local wanted: { [Model]: boolean } = {}
	if mine then
		for _, other in Players:GetPlayers() do
			local character = other.Character
			if other ~= player and character and inArea(character) then
				wanted[character] = true
				hide(character)
			end
		end
	end
	for character in hidden do
		if not wanted[character] then
			show(character)
		end
	end
end

function ThrowAreaPrivacy.start()
	local since = 0
	RunService.Heartbeat:Connect(function(dt)
		since += dt
		if since >= CHECK_EVERY then
			since = 0
			update()
		end
	end)
end

return ThrowAreaPrivacy
