-- The admin panel (AdminService, Config/Admin): a small ADMIN button, only for admins, that opens a plain panel of
-- test tools. The server checks every request.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local UiKit = require(ReplicatedStorage.Shared.UiKit)

local player = Players.LocalPlayer

local AdminController = {}

local BUTTONS = {
	{ action = "fresh", text = "Play as new player", style = "green" },
	{ action = "real", text = "Back to my save", style = "blue" },
	{ action = "finishTutorial", text = "Finish tutorial", style = "purple" },
	{ action = "cash", text = "+$1M (test save)", style = "yellow" },
}

function AdminController.start()
	while not player:GetAttribute("IsAdmin") do
		player:GetAttributeChangedSignal("IsAdmin"):Wait()
	end
	local remote = ReplicatedStorage:WaitForChild("AdminRemotes"):WaitForChild("Action")

	local gui = Instance.new("ScreenGui")
	gui.Name = "AdminHud"
	gui.ResetOnSpawn = false
	gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	gui.DisplayOrder = 3
	gui.Parent = player:WaitForChild("PlayerGui")

	local scale = UiKit.scale()
	local open = UiKit.button(gui, "ADMIN", "red", 110, 40, 20)
	open.Name = "AdminButton"
	open.AnchorPoint = Vector2.new(0, 0)
	open.Position = UDim2.fromOffset(12 * scale, 12 * scale) -- top left, clear of STOP and the training bar
	local openScale = open:FindFirstChildOfClass("UIScale")
	if openScale then
		openScale.Scale = scale -- its press squash works from this size
	end

	local panel = UiKit.panel(gui, { name = "AdminPanel", width = 420, height = 420, header = "red", title = "Admin" })
	local list = Instance.new("Frame")
	list.BackgroundTransparency = 1
	list.Position = UDim2.fromOffset(30, 16)
	list.Size = UDim2.new(1, -60, 1, -32)
	list.Parent = panel.body
	local layout = Instance.new("UIListLayout")
	layout.Padding = UDim.new(0, 12)
	layout.HorizontalAlignment = Enum.HorizontalAlignment.Center
	layout.SortOrder = Enum.SortOrder.LayoutOrder
	layout.Parent = list

	local status = UiKit.muted(list, "", 18)
	status.LayoutOrder = 0
	local function showStatus(extra: string?)
		local save = if player:GetAttribute("AdminTestSave") then "Throwaway test save: nothing is saved" else "Your real save"
		status.Text = if extra then `{save}\n{extra}` else save
		status.Size = UDim2.new(1, 0, 0, 48)
	end
	showStatus()
	player:GetAttributeChangedSignal("AdminTestSave"):Connect(function()
		showStatus()
	end)

	for order, entry in BUTTONS do
		local button = UiKit.button(list, entry.text, entry.style, 340, 52, 22)
		button.Name = entry.action
		button.LayoutOrder = order
		button.Activated:Connect(function()
			remote:FireServer(entry.action)
		end)
	end

	remote.OnClientEvent:Connect(function(kind: string, text: string)
		if kind == "message" then
			showStatus(text)
		end
	end)
	open.Activated:Connect(function()
		UiKit.togglePanel(panel)
	end)
end

return AdminController
