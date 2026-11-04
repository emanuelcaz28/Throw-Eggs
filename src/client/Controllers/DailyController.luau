-- The Daily Reward panel (Config/Daily): seven day tiles, each a lucky throw, the big one on day 7, and CLAIM. It opens by
-- itself a few seconds after joining when a claim is waiting; a button in the left column (under Shop)
-- opens it any time, with a red dot while a claim is waiting. Display and requests only: DailyService
-- decides the day and gives the boost.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local Daily = require(ReplicatedStorage.Shared.Config.Daily)
local HudStyle = require(ReplicatedStorage.Shared.HudStyle)
local PopText = require(ReplicatedStorage.Shared.PopText)
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

	local check = UiKit.text(frame, "✓", 72, DONE)
	check.AnchorPoint = Vector2.new(0.5, 0.5)
	check.Position = UDim2.fromScale(0.5, 0.45)
	check.Visible = false

	return { frame = frame, stroke = stroke, check = check }
end

local function buildGui()
	local gui = Instance.new("ScreenGui")
	gui.Name = "DailyHud"
	gui.ResetOnSpawn = false
	gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	gui.DisplayOrder = 5
	gui.Parent = player:WaitForChild("PlayerGui")

	-- Left column, under Shop.
	local open = HudStyle.iconButton(gui, "🎁", "Daily", nil)
	open.Name = "OpenDaily"
	open.AnchorPoint = Vector2.new(0, 0.5)
	open.Position = UDim2.new(0, 16, HudStyle.COLUMN_CENTER, (HudStyle.BUTTON_SIZE + HudStyle.BUTTON_GAP) * 1.5 * HudStyle.scale())
	local dot = Instance.new("Frame")
	dot.Name = "Waiting"
	dot.AnchorPoint = Vector2.new(0.5, 0.5)
	dot.Position = UDim2.fromScale(0.92, 0.08)
	dot.Size = UDim2.fromScale(0.26, 0.26)
	dot.BackgroundColor3 = Color3.fromRGB(255, 60, 70)
	dot.Visible = false
	dot.Parent = open
	UiKit.corner(dot, 999)
	UiKit.stroke(dot, 3)

	local width = TILE.X * (#Daily.days - 1) + BIG_TILE.X + TILE_GAP * (#Daily.days - 1)
	local panel = UiKit.panel(gui, { name = "DailyPanel", width = width + 60, height = 470, header = "gold", title = "Daily Reward", icon = "🎁" })

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

	return { open = open, dot = dot, panel = panel, tiles = tiles, claim = claim }
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

	for _, name in { "DailyDay", "DailyClaimable" } do
		player:GetAttributeChangedSignal(name):Connect(render)
	end
	render()

	hud.open.Activated:Connect(function()
		UiKit.togglePanel(hud.panel)
	end)
	hud.claim.Activated:Connect(function()
		if player:GetAttribute("DailyClaimable") then
			local reward = Daily.days[player:GetAttribute("DailyDay") or 1]
			claimRemote:FireServer()
			UiKit.closePanel(hud.panel)
			if reward then
				PopText.shout(`LUCKY THROW x{reward.luckyThrow}!`, "Your next throw has a lucky bonus")
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

	-- Opens by itself once, a moment after joining, when a claim is waiting.
	task.delay(Daily.openDelay, function()
		if player:GetAttribute("DailyClaimable") then
			UiKit.openPanel(hud.panel)
		end
	end)
end

return DailyController
