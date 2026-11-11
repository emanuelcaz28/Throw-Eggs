-- The Back to Plot button: the player's screen has already put them out in front of their own plot's gate
-- (HomeController, Plot.frontCFrame), at once. Here the server calls their throw meter off straight away, rather than
-- when it next sees them off the platform, and stops training. Should the move not reach the server, it moves them
-- itself a moment later. Nothing happens while their egg is in the air or the catch is showing.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Plot = require(ReplicatedStorage.Shared.Config.Plot)
local Throw = require(ReplicatedStorage.Shared.Config.Throw)
local RemoteGuard = require(script.Parent.RemoteGuard)
local PlotService = require(script.Parent.PlotService)
local ThrowService = require(script.Parent.ThrowService)
local TrainingService = require(script.Parent.TrainingService)

local HomeService = {}

local lastUsed: { [Player]: number } = {}

local function alive(player: Player): (Model?, Humanoid?, BasePart?)
	local character = player.Character
	local humanoid = character and character:FindFirstChildOfClass("Humanoid")
	local root = character and character:FindFirstChild("HumanoidRootPart") :: BasePart?
	if character and humanoid and root and humanoid.Health > 0 then
		return character, humanoid, root
	end
	return nil, nil, nil
end

local function goHome(player: Player)
	local now = os.clock()
	if now - (lastUsed[player] or -math.huge) < Plot.homeButton.cooldown then
		return
	end
	lastUsed[player] = now

	local plotIndex = player:GetAttribute("PlotIndex")
	if not plotIndex then
		PlotService.notify(player, "You don't have a plot in this server", true)
		return
	end
	if not alive(player) or ThrowService.isThrowing(player) then
		return
	end

	TrainingService.stop(player)
	ThrowService.leaveMeter(player)
	task.delay(Plot.homeButton.backupAfter, function()
		local character, humanoid, root = alive(player)
		if character and humanoid and root and Throw.onPlatform(root.Position) and not ThrowService.isThrowing(player) then
			humanoid.Sit = false
			character:PivotTo(Plot.frontCFrame(plotIndex) + Vector3.new(0, humanoid.HipHeight + root.Size.Y / 2, 0))
			root.AssemblyLinearVelocity = Vector3.zero
		end
	end)
end

function HomeService.start()
	local remote = Instance.new("RemoteEvent")
	remote.Name = "GoHome"
	remote.Parent = ReplicatedStorage
	RemoteGuard.connect(remote, goHome)
	Players.PlayerRemoving:Connect(function(player)
		lastUsed[player] = nil
	end)
end

return HomeService
