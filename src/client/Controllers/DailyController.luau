-- The Daily Reward panel (Config/Daily): seven day tiles, each a lucky throw, the big one on day 7, CLAIM, and today's three
-- tasks. It opens itself a few seconds after joining when a claim is waiting; a button above Monsters opens it any time,
-- with a red dot while a claim is waiting. Display and requests only: DailyService and DailyTasks decide everything.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local Daily = require(ReplicatedStorage.Shared.Config.Daily)
local HudStyle = require(ReplicatedStorage.Shared.HudStyle)
local Index = require(ReplicatedStorage.Shared.Config.Index)
local LuckyThrows = require(ReplicatedStorage.Shared.LuckyThrows)
local PopText = require(ReplicatedStorage.Shared.PopText)
local WelcomeController = require(script.Parent.WelcomeController)
local UiKit = require(ReplicatedStorage.Shared.UiKit)

local player = Players.LocalPlayer

local DailyController = {}

local TILE = Vector2.new(112, 168)
local BIG_TILE = Vector2.new(150, 196) -- day 7
local TILE_GAP = 10
local DONE = Color3.fromRGB(80, 200, 90)

local function tileFor(parent: Instance, day: number, reward): { [string]: any }
	local big = day == #Daily.days
	local size = if big then BIG_TILE else TILE
	local frame = Instance.new("Frame")
	frame.LayoutOrder = day
	frame.Size = UDim2.fromOffset(size.X, size.Y)
	frame.Parent = parent
	UiKit.gradient(frame, if big then { "#fff1a8", "#ffb21a" } else { "#e0a8ff", "#8a3fd6" }, 90)
	UiKit.corner(frame, 20)
	local stroke = UiKit.stroke(frame, 4)

	local title = UiKit.text(frame, `DAY {day}`, if big then 26 else 22, if big then UiKit.INK else nil)
	title.Position = UDim2.fromOffset(0, 8)
	UiKit.iconImage(frame, "clover", {
		anchor = Vector2.new(0.5, 0),
		position = UDim2.new(0.5, 0, 0, 40),
		size = UDim2.fromOffset(if big then 84 else 64, if big then 84 else 64),
	})
	local amount = UiKit.text(frame, `x{reward.luckyThrow}`, if big then 40 else 32, UiKit.GOLD)
	amount.AnchorPoint = Vector2.new(0, 1)
	amount.Position = UDim2.new(0, 0, 1, -34)
	local kind = UiKit.text(frame, "LUCKY THROW", 15, if big then UiKit.INK else nil)
	kind.AnchorPoint = Vector2.new(0, 1)
	kind.Position = UDim2.new(0, 0, 1, -10)

	-- A drawn tick, not a character: phones have no font with one.
	local check = Instance.new("Frame")
	check.BackgroundTransparency = 1
	check.AnchorPoint = Vector2.new(0.5, 0.5)
	check.Position = UDim2.fromScale(0.5, 0.45)
	check.Size = UDim2.fromOffset(72, 72)
	check.Visible = false
	check.Parent = frame
	for _, bar in { { 24, 44, 30, 45 }, { 44, 34, 52, -52 } } do
		local line = Instance.new("Frame")
		line.AnchorPoint = Vector2.new(0.5, 0.5)
		line.BackgroundColor3 = DONE
		line.BorderSizePixel = 0
		line.Position = UDim2.fromOffset(bar[1], bar[2])
		line.Size = UDim2.fromOffset(bar[3], 11)
		line.Rotation = bar[4]
		line.Parent = check
		UiKit.corner(line, 5)
		UiKit.stroke(line, 3)
	end

	return { frame = frame, stroke = stroke, check = check }
end

local function buildGui()
	local gui = Instance.new("ScreenGui")
	gui.Name = "DailyHud"
	gui.ResetOnSpawn = false
	gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	gui.DisplayOrder = 5
	gui.Parent = player:WaitForChild("PlayerGui")

	local width = TILE.X * (#Daily.days - 1) + BIG_TILE.X + TILE_GAP * (#Daily.days - 1)
	local panel = UiKit.panel(gui, { name = "DailyPanel", width = width + 60, height = 576, header = "gold", title = "Daily Reward", icon = "🎁" })

	local line = UiKit.muted(panel.body, "Come back every day: day 7 is a x500 lucky throw!", 22)
	line.Position = UDim2.fromOffset(0, 14)

	local row = Instance.new("Frame")
	row.BackgroundTransparency = 1
	row.AnchorPoint = Vector2.new(0.5, 0)
	row.Position = UDim2.new(0.5, 0, 0, 56)
	row.Size = UDim2.fromOffset(width, BIG_TILE.Y)
	row.Parent = panel.body
	local layout = Instance.new("UIListLayout")
	layout.FillDirection = Enum.FillDirection.Horizontal
	layout.VerticalAlignment = Enum.VerticalAlignment.Center
	layout.Padding = UDim.new(0, TILE_GAP)
	layout.SortOrder = Enum.SortOrder.LayoutOrder
	layout.Parent = row

	local tiles = {}
	for day, reward in Daily.days do
		tiles[day] = tileFor(row, day, reward)
	end

	local claim = UiKit.button(panel.body, "CLAIM", "green", 380, 80, 42)
	claim.AnchorPoint = Vector2.new(0.5, 0)
	claim.Position = UDim2.new(0.5, 0, 0, 56 + BIG_TILE.Y + 24)

	-- Today's tasks under the button.
	local taskTop = 56 + BIG_TILE.Y + 24 + 80 + 14
	local goal = UiKit.muted(panel.body, `Finish all 3 today: x{Index.xpBoost.multiplier} XP for {Daily.taskBoostSeconds // 60} minutes`, 20)
	goal.Position = UDim2.fromOffset(0, taskTop)
	local taskRow = Instance.new("Frame")
	taskRow.BackgroundTransparency = 1
	taskRow.AnchorPoint = Vector2.new(0.5, 0)
	taskRow.Position = UDim2.new(0.5, 0, 0, taskTop + 32)
	taskRow.Size = UDim2.fromOffset(width, 58)
	taskRow.Parent = panel.body
	local taskLayout = Instance.new("UIListLayout")
	taskLayout.FillDirection = Enum.FillDirection.Horizontal
	taskLayout.Padding = UDim.new(0, TILE_GAP)
	taskLayout.SortOrder = Enum.SortOrder.LayoutOrder
	taskLayout.Parent = taskRow
	local tasks = {}
	for index, task in Daily.tasks do
		local chip = Instance.new("Frame")
		chip.LayoutOrder = index
		chip.BackgroundColor3 = UiKit.ROW
		chip.Size = UDim2.fromOffset((width - TILE_GAP * (#Daily.tasks - 1)) / #Daily.tasks, 58)
		chip.Parent = taskRow
		UiKit.corner(chip, 16)
		local stroke = UiKit.stroke(chip, 4)
		local label = UiKit.text(chip, "", 24)
		label.Size = UDim2.fromScale(1, 1)
		tasks[task.id] = { label = label, stroke = stroke, chip = chip, task = task }
	end

	-- In its own layer under the other panels, so an open panel covers it, as My Monsters does its own button.
	local buttonGui = Instance.new("ScreenGui")
	buttonGui.Name = "DailyButtonHud"
	buttonGui.ResetOnSpawn = false
	buttonGui.DisplayOrder = -1
	buttonGui.Parent = player:WaitForChild("PlayerGui")
	local open = HudStyle.iconButton(buttonGui, "🎁", "Daily")
	open.Name = "OpenDaily"
	open.AnchorPoint = Vector2.new(1, 0.5)
	open.Position = UDim2.new(1, -16, HudStyle.COLUMN_CENTER, -(HudStyle.BUTTON_SIZE + 14) * HudStyle.scale())
	local dot = Instance.new("Frame")
	dot.Name = "Dot"
	dot.AnchorPoint = Vector2.new(0.5, 0.5)
	dot.BackgroundColor3 = Color3.fromRGB(240, 60, 50)
	dot.Position = UDim2.new(1, -6, 0, 6)
	dot.Size = UDim2.fromOffset(20 * HudStyle.scale(), 20 * HudStyle.scale())
	dot.ZIndex = 5
	dot.Parent = open
	UiKit.corner(dot, 12)

	return { panel = panel, tiles = tiles, claim = claim, tasks = tasks, open = open, dot = dot }
end

local function countdown(seconds: number): string
	seconds = math.max(math.floor(seconds), 0)
	return string.format("%d:%02d:%02d", seconds // 3600, (seconds % 3600) // 60, seconds % 60)
end

function DailyController.start()
	local claimRemote = ReplicatedStorage:WaitForChild("ClaimDaily") :: RemoteEvent
	local hud = buildGui()
	local pulsing = false

	-- Days before the current one are ticked; the current one (to claim, or claimed today) is outlined.
	local function render()
		local day = player:GetAttribute("DailyDay") or 1
		local claimable = player:GetAttribute("DailyClaimable") == true
		local doneUpTo = if claimable then day - 1 else day
		for index, tile in hud.tiles do
			tile.check.Visible = index <= doneUpTo
			tile.stroke.Color = if index == day then Color3.new(1, 1, 1) else UiKit.INK
			tile.stroke.Thickness = if index == day then 6 else 4
		end
		hud.dot.Visible = claimable
		hud.claim.TextSize = if claimable then 42 else 30
		if claimable then
			UiKit.restyle(hud.claim, "CLAIM", "green")
			if not pulsing then
				pulsing = true
				UiKit.pulse(hud.claim)
			end
		else
			UiKit.restyle(hud.claim, "COME BACK TOMORROW", "grey")
		end
	end

	local function renderTasks()
		for id, row in hud.tasks do
			local count = math.min(player:GetAttribute(`DailyTask_{id}`) or 0, row.task.goal)
			local done = count >= row.task.goal
			row.label.Text = `{row.task.text}  {count} / {row.task.goal}`
			row.label.TextColor3 = if done then UiKit.CASH else UiKit.TEXT
			row.stroke.Color = if done then DONE else UiKit.INK
		end
	end

	for _, name in { "DailyDay", "DailyClaimable" } do
		player:GetAttributeChangedSignal(name):Connect(render)
	end
	for id in hud.tasks do
		player:GetAttributeChangedSignal(`DailyTask_{id}`):Connect(renderTasks)
	end
	render()
	renderTasks()

	hud.open.Activated:Connect(function()
		UiKit.togglePanel(hud.panel)
	end)

	hud.claim.Activated:Connect(function()
		if player:GetAttribute("DailyClaimable") then
			local reward = Daily.days[player:GetAttribute("DailyDay") or 1]
			claimRemote:FireServer()
			UiKit.closePanel(hud.panel)
			if reward then
				PopText.shout(`LUCKY THROW x{reward.luckyThrow}!`, if LuckyThrows.isPicked(reward.luckyThrow) then "Tap USE on the throw meter when you want it" else "Your next throw has a lucky bonus")
			end
		end
	end)

	-- Grey button counts down to midnight UTC, when the next claim opens.
	RunService.Heartbeat:Connect(function()
		if player:GetAttribute("DailyClaimable") == false then
			local left = (player:GetAttribute("DailyNextAt") or 0) - workspace:GetServerTimeNow()
			hud.claim.Text = `NEXT IN {countdown(left)}`
		end
	end)

	-- The panel also opens by itself when a claim is waiting, once the Welcome back pop-up is out of the way
	-- (after CLAIM, or straight away when there was nothing to collect), and again at midnight UTC for a player
	-- still in the game, when the server makes the next day claimable.
	local function offer()
		if player:GetAttribute("DailyClaimable") then
			UiKit.openPanel(hud.panel)
		end
	end
	task.delay(Daily.openDelay, function()
		WelcomeController.waitUntilDone()
		offer()
		player:GetAttributeChangedSignal("DailyClaimable"):Connect(offer)
	end)
end

return DailyController
