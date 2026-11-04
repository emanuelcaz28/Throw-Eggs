-- Sets every player's walk speed from Config/Movement: new characters through StarterPlayer, and anyone
-- already in the game when it changes.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local StarterPlayer = game:GetService("StarterPlayer")

local Movement = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("Config"):WaitForChild("Movement"))

StarterPlayer.CharacterWalkSpeed = Movement.walkSpeed

local function apply(character: Model)
	local humanoid = character:WaitForChild("Humanoid", 10) :: Humanoid?
	if humanoid then
		humanoid.WalkSpeed = Movement.walkSpeed
	end
end

local function watch(player: Player)
	if player.Character then
		task.spawn(apply, player.Character)
	end
	player.CharacterAdded:Connect(apply)
end

for _, player in Players:GetPlayers() do
	watch(player)
end
Players.PlayerAdded:Connect(watch)
