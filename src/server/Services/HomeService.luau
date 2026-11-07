-- The Back to Plot button: puts a player out in front of their own plot's gate (Plot.frontCFrame), from anywhere,
-- so nobody can get stuck (on the throw platform, in a corner of a world, under a giant). The server moves them.
-- Not while their egg is in the air or the catch is showing. Training is stopped first; a meter in progress is
-- called off by ThrowService as soon as they're off the platform.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Plot = require(ReplicatedStorage.Shared.Config.Plot)
local PlotService = require(script.Parent.PlotService)
local ThrowService = require(script.Parent.ThrowService)
local TrainingService = require(script.Parent.TrainingService)

local HomeService = {}

local lastUsed: { [Player]: number } = {}

local function goHome(player: Player)
	local now = os.clock()
	if now - (lastUsed[player] or -math.huge) < Plot.homeButton.cooldown then
		return
	end
	lastUsed[player] = now

	local plotIndex = player:GetAttribute("PlotIndex")
	local character = player.Character
	local humanoid = character and character:FindFirstChildOfClass("Humanoid")
	local root = character and character:FindFirstChild("HumanoidRootPart") :: BasePart?
	if not plotIndex then
		PlotService.notify(player, "You don't have a plot in this server", true)
		return
	end
	if not (humanoid and root) or humanoid.Health <= 0 then
		return
	end
	if ThrowService.isThrowing(player) then
		PlotService.notify(player, "Wait for your egg to land", true)
		return
	end

	TrainingService.stop(player)
	humanoid.Sit = false
	local home = Plot.frontCFrame(plotIndex) + Vector3.new(0, humanoid.HipHeight + root.Size.Y / 2, 0)
	character:PivotTo(home)
	root.AssemblyLinearVelocity = Vector3.zero
end

function HomeService.start()
	local remote = Instance.new("RemoteEvent")
	remote.Name = "GoHome"
	remote.Parent = ReplicatedStorage
	remote.OnServerEvent:Connect(goHome)
	Players.PlayerRemoving:Connect(function(player)
		lastUsed[player] = nil
	end)
end

return HomeService
