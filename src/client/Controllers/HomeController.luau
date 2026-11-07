-- The Back to Plot button: a wide text button at the bottom middle of the screen, under the thrower
-- [Owner, 2026-11-07]. Only there while the throw meter is up (ThrowController shows and hides it), so a player can
-- always leave the meter. A press asks the server to put them out in front of their plot's gate (HomeService).
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local HudStyle = require(ReplicatedStorage.Shared.HudStyle)
local UiKit = require(ReplicatedStorage.Shared.UiKit)

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
	gui.Enabled = false -- until the meter starts
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

	button.Activated:Connect(function()
		remote:FireServer()
	end)
end

return HomeController
