-- The admin panel (AdminService, AdminBoostService, Config/Admin): a small ADMIN button, only for admins, that opens a
-- scrolling panel of tools: test-save tools, boosts for the whole server you are in (luck, power, training XP: any
-- multiplier, any minutes) and gifts to one player here (x100 / x500 lucky throws, Throw Power). The server checks
-- every request.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Admin = require(ReplicatedStorage.Shared.Config.Admin)
local AdminBoosts = require(ReplicatedStorage.Shared.AdminBoosts)
local UiKit = require(ReplicatedStorage.Shared.UiKit)

local player = Players.LocalPlayer

local AdminController = {}

local WIDTH = 520
local ROW = 440 -- the width of everything in the list

local BUTTONS = {
	{ action = "fresh", text = "Play as new player", style = "green" },
	{ action = "real", text = "Back to my save", style = "blue" },
	{ action = "finishTutorial", text = "Finish tutorial", style = "purple" },
	{ action = "cash", text = "+$1M (test save)", style = "yellow" },
}

local BOOSTS = {
	{ kind = "luck", label = "Luck", style = "green", multiplier = 10, minutes = 15 },
	{ kind = "power", label = "Power", style = "yellow", multiplier = 2, minutes = 15 },
	{ kind = "xp", label = "XP", style = "blue", multiplier = 2, minutes = 15 },
}

local GIFTS = {
	{ what = 100, label = "Luck x100", style = "purple", amount = 1 },
	{ what = 500, label = "Luck x500", style = "yellow", amount = 1 },
	{ what = "power", label = "Power", style = "green", amount = 1000 },
}

local function clock(seconds: number): string
	seconds = math.max(0, math.floor(seconds))
	return string.format("%d:%02d", seconds // 60, seconds % 60)
end

local function row(parent: Instance, order: number, height: number): Frame
	local frame = Instance.new("Frame")
	frame.BackgroundTransparency = 1
	frame.Size = UDim2.fromOffset(ROW, height)
	frame.LayoutOrder = order
	frame.Parent = parent
	return frame
end

-- A number box: white, rounded, digits only.
local function numberBox(parent: Instance, value: number, x: number, width: number): TextBox
	local box = Instance.new("TextBox")
	box.Position = UDim2.fromOffset(x, 4)
	box.Size = UDim2.fromOffset(width, 44)
	box.BackgroundColor3 = Color3.new(1, 1, 1)
	box.FontFace = UiKit.FONT
	box.TextColor3 = UiKit.INK
	box.TextSize = 22
	box.Text = tostring(value)
	box.ClearTextOnFocus = false
	box.Parent = parent
	UiKit.corner(box, 12)
	UiKit.stroke(box, 3)
	box:GetPropertyChangedSignal("Text"):Connect(function()
		local digits = string.gsub(box.Text, "%D", "")
		if digits ~= box.Text then
			box.Text = digits
		end
	end)
	return box
end

local function small(parent: Instance, text: string, x: number, width: number): TextLabel
	local label = UiKit.text(parent, text, 20, nil, Enum.TextXAlignment.Left)
	label.Position = UDim2.fromOffset(x, 4)
	label.Size = UDim2.fromOffset(width, 44)
	return label
end

local function placed(button: TextButton, x: number): TextButton
	button.Position = UDim2.fromOffset(x, 2)
	return button
end

function AdminController.start()
	while not player:GetAttribute("IsAdmin") do
		player:GetAttributeChangedSignal("IsAdmin"):Wait()
	end
	local remotes = ReplicatedStorage:WaitForChild("AdminRemotes")
	local remote = remotes:WaitForChild("Action")
	local boostRemote = remotes:WaitForChild("Boost")

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

	local panel = UiKit.panel(gui, { name = "AdminPanel", width = WIDTH, height = 640, header = "red", title = "Admin" })
	local list = UiKit.scrollList(panel.body, UDim2.fromOffset(16, 8), UDim2.new(1, -32, 1, -20), 10)
	local order = 0
	local function nextOrder(): number
		order += 1
		return order
	end

	-- What the server last said, at the top.
	local status = UiKit.muted(list, "", 18)
	status.LayoutOrder = nextOrder()
	status.Size = UDim2.fromOffset(ROW, 48)
	local lastMessage: string? = nil
	local function showStatus()
		local save = if player:GetAttribute("AdminTestSave") then "Throwaway test save: nothing is saved" else "Your real save"
		status.Text = if lastMessage then `{save}\n{lastMessage}` else save
	end
	showStatus()
	player:GetAttributeChangedSignal("AdminTestSave"):Connect(showStatus)
	local function said(text: string)
		lastMessage = text
		showStatus()
	end
	remote.OnClientEvent:Connect(function(kind: string, text: string)
		if kind == "message" then
			said(text)
		end
	end)
	boostRemote.OnClientEvent:Connect(said)

	-- Test-save tools, two a row.
	for index = 1, #BUTTONS, 2 do
		local line = row(list, nextOrder(), 52)
		for offset = 0, 1 do
			local entry = BUTTONS[index + offset]
			if entry then
				local button = UiKit.button(line, entry.text, entry.style, ROW / 2 - 6, 48, 18)
				button.Name = entry.action
				placed(button, offset * (ROW / 2 + 6))
				button.Activated:Connect(function()
					remote:FireServer(entry.action)
				end)
			end
		end
	end

	-- Server boosts: everyone in this server.
	UiKit.divider(list, "Server boosts", ROW).LayoutOrder = nextOrder()
	local hint = UiKit.muted(list, "For everyone in this server, until the minutes run out or the server closes.", 16)
	hint.LayoutOrder = nextOrder()
	hint.Size = UDim2.fromOffset(ROW, 40)
	local running: { [string]: TextLabel } = {}
	for _, entry in BOOSTS do
		local look = Admin.boosts[entry.kind]
		local line = row(list, nextOrder(), 52)
		small(line, entry.label, 0, 70)
		small(line, "x", 72, 16)
		local times = numberBox(line, entry.multiplier, 88, 70)
		local minutes = numberBox(line, entry.minutes, 166, 60)
		small(line, "min", 230, 44)
		local go = placed(UiKit.button(line, "Start", entry.style, 80, 48, 20), 276)
		local stop = placed(UiKit.button(line, "Stop", "red", 76, 48, 20), 364)
		go.Activated:Connect(function()
			boostRemote:FireServer("start", entry.kind, tonumber(times.Text), tonumber(minutes.Text))
		end)
		stop.Activated:Connect(function()
			boostRemote:FireServer("stop", entry.kind)
		end)
		local now = UiKit.muted(list, "", 16)
		now.LayoutOrder = nextOrder()
		now.Size = UDim2.fromOffset(ROW, 22)
		running[entry.kind] = now
		times.PlaceholderText = `2-{look.most}`
	end
	local function showRunning()
		local now = workspace:GetServerTimeNow()
		for kind, label in running do
			local multiplier, endsAt = AdminBoosts.get(kind, now)
			label.Text = if multiplier and endsAt then `On: x{multiplier}, {clock(endsAt - now)} left` else "Off"
		end
	end

	-- Gifts to one player here (or everyone), saved on them at once.
	UiKit.divider(list, "Give a player", ROW).LayoutOrder = nextOrder()
	local pickLine = row(list, nextOrder(), 52)
	local back = placed(UiKit.button(pickLine, "<", "blue", 56, 48, 24), 0)
	local forward = placed(UiKit.button(pickLine, ">", "blue", 56, 48, 24), ROW - 56)
	local who = UiKit.text(pickLine, "", 22)
	who.Position = UDim2.fromOffset(62, 4)
	who.Size = UDim2.fromOffset(ROW - 124, 44)
	who.TextScaled = true
	local picked = player.UserId -- 0 means everyone here
	local function choices(): { number }
		local ids = { player.UserId }
		for _, other in Players:GetPlayers() do
			if other ~= player then
				table.insert(ids, other.UserId)
			end
		end
		table.insert(ids, 0)
		return ids
	end
	local function showPicked()
		if picked == 0 then
			who.Text = "Everyone here"
			return
		end
		local target = Players:GetPlayerByUserId(picked)
		if not target then
			picked = player.UserId
			target = player
		end
		who.Text = if target == player then `{target.DisplayName} (you)` else `{target.DisplayName} (@{target.Name})`
	end
	local function step(by: number)
		local ids = choices()
		local index = table.find(ids, picked) or 1
		picked = ids[(index - 1 + by) % #ids + 1]
		showPicked()
	end
	back.Activated:Connect(function()
		step(-1)
	end)
	forward.Activated:Connect(function()
		step(1)
	end)
	Players.PlayerRemoving:Connect(function(leaving)
		if leaving.UserId == picked then
			task.defer(showPicked)
		end
	end)
	showPicked()

	for _, entry in GIFTS do
		local line = row(list, nextOrder(), 52)
		small(line, entry.label, 0, 130)
		local amount = numberBox(line, entry.amount, 134, 186)
		local give = placed(UiKit.button(line, "Give", entry.style, 110, 48, 20), ROW - 110)
		give.Activated:Connect(function()
			boostRemote:FireServer("give", picked, entry.what, tonumber(amount.Text))
		end)
	end
	local note = UiKit.muted(list, "Gifts are saved on the player at once, like a purchase.", 16)
	note.LayoutOrder = nextOrder()
	note.Size = UDim2.fromOffset(ROW, 24)

	open.Activated:Connect(function()
		UiKit.togglePanel(panel)
	end)
	task.spawn(function()
		while gui.Parent do
			if panel.frame.Visible then
				showRunning()
			end
			task.wait(0.5)
		end
	end)
	showRunning()
end

return AdminController
