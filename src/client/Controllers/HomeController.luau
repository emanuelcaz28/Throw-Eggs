-- The Back to Plot button: a wide text button at the bottom middle of the screen, under the thrower
-- [Owner, 2026-11-07]. ThrowController shows it while the throw meter is up and whenever the player stands on the throw
-- platform outside a throw, so there's always a way out of the throwing area. A press works at once on this screen:
-- the meter goes and the character is put out in front of their plot's gate, the way walking moves it, with no wait
-- for the server [player feedback, 2026-11-08: it seemed not to work]. Then the server is told (HomeService).
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local HudStyle = require(ReplicatedStorage.Shared.HudStyle)
local Plot = require(ReplicatedStorage.Shared.Config.Plot)
local UiKit = require(ReplicatedStorage.Shared.UiKit)
local ThrowController = require(script.Parent.ThrowController)

local HomeController = {}

local player = Players.LocalPlayer

local WIDTH = 220
local HEIGHT = 50
local EDGE = 12 -- gap to the screen's bottom

function HomeController.start()
	local remote = ReplicatedStorage:WaitForChild("GoHome") :: RemoteEvent

	local gui = Instance.new("ScreenGui")
	gui.Name = "HomeHud"
	gui.ResetOnSpawn = false
	gui.Enabled = false -- until ThrowController shows it
	gui.Parent = player:WaitForChild("PlayerGui")

	local scale = HudStyle.scale()
	local button = UiKit.button(gui, "BACK TO PLOT", "blue", math.floor(WIDTH * scale), math.floor(HEIGHT * scale))
	button.Name = "BackToPlot"
	button.AnchorPoint = Vector2.new(0.5, 1)
	button.Position = UDim2.new(0.5, 0, 1, -EDGE * scale)

	local function render()
		button.Visible = player:GetAttribute("PlotIndex") ~= nil
	end
	player:GetAttributeChangedSignal("PlotIndex"):Connect(render)
	render()

	local lastPress = -math.huge
	button.Activated:Connect(function()
		local plotIndex = player:GetAttribute("PlotIndex")
		if not plotIndex or os.clock() - lastPress < Plot.homeButton.cooldown then
			return
		end
		-- Not from the tap until the reveal is over; otherwise the meter is called off here.
		if not ThrowController.leaveMeter() then
			return
		end
		lastPress = os.clock()
		local character = player.Character
		local humanoid = character and character:FindFirstChildOfClass("Humanoid")
		local root = character and character:FindFirstChild("HumanoidRootPart") :: BasePart?
		if humanoid and root and humanoid.Health > 0 then
			humanoid.Sit = false
			character:PivotTo(Plot.frontCFrame(plotIndex) + Vector3.new(0, humanoid.HipHeight + root.Size.Y / 2, 0))
			root.AssemblyLinearVelocity = Vector3.zero
		end
		remote:FireServer()
	end)
end

return HomeController
