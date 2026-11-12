-- The Ragdoll button (left column, under Shop) and this player's side of a ragdoll. The server decides who is
-- ragdolled and loosens the joints (RagdollService); this screen lets the body fall and stands it up again, because
-- Roblox leaves a character's physics to its own player. Hidden in the throwing area, where ragdolls aren't allowed.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local HudStyle = require(ReplicatedStorage.Shared.HudStyle)
local Troll = require(ReplicatedStorage.Shared.Config.Troll)
local ThrowAreaPrivacy = require(script.Parent.ThrowAreaPrivacy)

local RagdollController = {}

local player = Players.LocalPlayer

local function fall(character: Model, humanoid: Humanoid)
	humanoid:SetStateEnabled(Enum.HumanoidStateType.GettingUp, false) -- else Roblox stands the body straight back up
	humanoid:ChangeState(Enum.HumanoidStateType.Physics)
	local root = character:FindFirstChild("HumanoidRootPart") :: BasePart?
	if root and not character:GetAttribute("LeashedBy") then -- a leashed player just drops; the rope does the rest
		local hop = Troll.ragdoll.hop
		root.AssemblyLinearVelocity = root.CFrame.LookVector * hop.Z + Vector3.new(0, hop.Y, 0)
		root.AssemblyAngularVelocity = root.CFrame.RightVector * Troll.ragdoll.spin
	end
end

local function getUp(humanoid: Humanoid)
	humanoid:SetStateEnabled(Enum.HumanoidStateType.GettingUp, true)
	if humanoid.Health > 0 then
		humanoid:ChangeState(Enum.HumanoidStateType.GettingUp)
	end
end

local function watch(character: Model)
	local humanoid = character:WaitForChild("Humanoid", 10) :: Humanoid?
	if not humanoid then
		return
	end
	character:GetAttributeChangedSignal("Ragdolled"):Connect(function()
		if character:GetAttribute("Ragdolled") then
			fall(character, humanoid)
		else
			getUp(humanoid)
		end
	end)
end

function RagdollController.start()
	local remote = ReplicatedStorage:WaitForChild("RagdollToggle") :: RemoteEvent

	local gui = Instance.new("ScreenGui")
	gui.Name = "RagdollHud"
	gui.ResetOnSpawn = false
	gui.Parent = player:WaitForChild("PlayerGui")

	local button = HudStyle.iconButton(gui, "🤸", "Ragdoll")
	button.AnchorPoint = Vector2.new(0, 0.5)
	button.Position = UDim2.new(0, 16, HudStyle.COLUMN_CENTER, (HudStyle.BUTTON_SIZE + HudStyle.BUTTON_GAP) * 1.5 * HudStyle.scale())
	button.Activated:Connect(function()
		remote:FireServer()
	end)

	local since = 0
	RunService.Heartbeat:Connect(function(dt)
		since += dt
		if since >= 0.2 then
			since = 0
			button.Visible = not ThrowAreaPrivacy.inArea()
		end
	end)

	if player.Character then
		task.spawn(watch, player.Character)
	end
	player.CharacterAdded:Connect(watch)
end

return RagdollController
